---
type: Concept
title: 编译调度与 unit 图：BuildRunner 的世界
description: compiler 模块的 25 个子模块、BuildContext/BuildRunner 双层语境、Unit 构建语义节点与 Lto/links 协调机制
tags: [rust, cargo, compiler, build, unit-graph]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-28T10:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T10:00:00+08:00" }
status: stable
stale_after: 2027-08-28
sources:
  - id: cargo-source
    resource: /references/cargo-source-map.md
---

# 编译调度与 unit 图：BuildRunner 的世界

`src/compiler/` 是"运行 rustc 与 rustdoc"的子系统（lib.rs 官方自述，F-cargo-037）。它的模块文档给出了一张分层地图（原文摘录，F-cargo-107）：

> "`BuildContext` is a static context containing all information you need before a build gets started."（BuildContext 是构建开始前所需全部信息的静态语境。）
> "`BuildRunner` is the center of the world, coordinating a running build"（BuildRunner 是世界的中心，协调一次运行中的构建。）
> "If you consider `ops::cargo_compile::compile` as a `rustc` driver but on Cargo side, this module is kinda the `rustc_interface`"（如果把 ops::cargo_compile::compile 看作 Cargo 侧的 rustc driver，那么本模块大致相当于 rustc_interface。）

最后一句是 cargo 与 rustc 的**官方明认结构类比**：`ops::cargo_compile::compile` ↔ rustc driver，`compiler` 模块 ↔ `rustc_interface`。rustc 的分层叙事可以直接迁移到 cargo 阅读。

## 25 个子模块清单（F-cargo-106/108）

compiler/mod.rs 声明的模块（F-cargo-106）：`artifact`、`build_config`、`build_context`、`build_runner`、`compilation`、`compile_kind`、`crate_type`、`custom_build`、`fingerprint`、`future_incompat`、`job_queue`、`layout`、`links`、`locking`、`lto`、`output_depinfo`、`output_sbom`、`rustdoc`、`standard_lib`、`timings`、`trim_paths`、`unit`、`unit_dependencies`、`unit_graph`、`unused_deps`。

re-exports 层（F-cargo-108）按职责分组：

| 分组 | 类型 |
|------|------|
| 构建配置 | `{BuildConfig, CompileMode, MessageFormat, UserIntent}` |
| 双层语境 | `BuildContext`、`{BuildRunner, Metadata, UnitHash}` |
| 目标数据 | `{DepKindSet, FileFlavor, FileType, RustcTargetData, TargetInfo}` |
| 编译产物 | `{Compilation, Doctest, UnitOutput}` |
| 编译种类 | `{CompileKind, CompileKindFallback, CompileTarget}` |
| 自定义构建 | `CrateType`、`{BuildOutput, BuildScriptOutputs, BuildScripts, LibraryPath, LinkArgTarget}` |
| 指纹与新鲜度 | `Freshness` |
| LTO | `Lto` |
| Unit 体系 | `Unit`/`UnitIndex`/`UnitInterner`、`UnitDep` |

`fingerprint`（脏检查）+ `job_queue`（并发执行）+ `unit_dependencies`/`unit_graph`（依赖图）+ `custom_build`（build.rs 协调）构成本模块的四大支柱。

## Unit：构建调度的原子节点（F-cargo-109/110）

编译调度图的节点不是"包"而是 `Unit`——**包 × 目标 × 档位 × 种类 × 模式 × 特征**的组合：

```rust
pub struct Unit {
    inner: Rc<UnitInner>,
}
pub struct UnitInner {
    pkg: Package,
    target: Target,
    profile: Profile,
    kind: CompileKind,
    mode: CompileMode,
    features: Vec<InternedString>,
    rustflags: Rc<[String]>,
    rustdocflags: Rc<[String]>,
    links_overrides: Rc<BTreeMap<String, BuildOutput>>,
    artifact: IsArtifact,
    is_std: bool,
    dep_hash: u64,
    artifact_target_for_features: Option<CompileTarget>,
    skip_non_compile_time_dep: bool,
}
```

（F-cargo-109。）设计要点：

- **`Rc<UnitInner>` + interning**：`pub struct UnitIndex(pub u64)`（serde transparent，F-cargo-110）给每个 unit 一个稳定整数编号；`pub struct UnitInterner`（:228）保证同语义 unit 唯一——与 `PackageId` 的 `&'static` 模式（F-cargo-083）同属"规范化即缓存"家族
- **语义完整性**：`Unit` 携带 `features`/`rustflags`/`rustdocflags`/`dep_hash`——两个同名同版本的目标可以因特征或标志不同而成为**不同的 unit**，这是 feature 统一（F-cargo-047 的 `FeatureUnification`）在编译端的体现
- **`is_std`**：标准库参与编译（`-Z build-std`）时的标记；`artifact`/`artifact_target_for_features` 服务 artifact 依赖

`build`/`check`/`test`/`doc` 的差异在 Unit 层表示为 `mode: CompileMode` 与 `profile: Profile` 的不同组合——39 个薄壳命令最终都坍缩为"构造不同的 Unit 图"。

## Lto：链接期优化的 Rust 侧视图（F-cargo-111）

```rust
pub enum Lto {
    Run(Option<InternedString>),   // -C lto=foo
    Off,                           // -C lto=off
    OnlyBitcode,                   // -C linker-plugin-lto
    ObjectAndBitcode,
    OnlyObject,                    // -C embed-bitcode=no
}
```

（F-cargo-111，文档表格标注各 variant 对应的 rustc flag。）`pub fn generate(bcx: &BuildContext<'_, '_>) -> CargoResult<HashMap<Unit, Lto>>` 逐 unit 决定 Lto 策略——Lto 状态由**依赖闭包**而非单包决定，因此必须在整个 unit 图上统一计算。

## links 验证：包名声明的全局唯一性（F-cargo-112）

`pub fn validate_links(resolve: &Resolve, unit_graph: &UnitGraph) -> CargoResult<()>`（links.rs:21，文件内唯一 pub 项，F-cargo-112）。`[links]` 声明（native 库链接键）要求解析闭包内全局唯一重复，此函数在编译前对 Resolve 图与 unit 图做交叉验证——这是"一个规则横跨 resolver 与 compiler 两个子系统"的实例。

## 数据流：从 ops 到 rustc 进程

```
CompileOptions（F-cargo-060）
    │ ops::cargo_compile::compile / create_bcx
    ▼
BuildContext（静态语境：RustcTargetData、TargetInfo 等）
    │ BuildRunner::new（build_runner，"世界的中心"）
    ▼
BuildRunner（运行语境：协调执行）
    │ unit_dependencies / unit_graph 构造 Unit 图
    │ fingerprint 脏检查（Freshness）
    │ lto::generate（F-cargo-111）+ links::validate_links（F-cargo-112）
    │ job_queue 调度并发
    ▼
rustc / rustdoc 进程（经 Rustc 封装，F-cargo-105）
    ▼
Compilation（产物汇总：Doctest、UnitOutput 等）
```

`Rustc` 封装（src/util/rustc.rs，F-cargo-105）通过执行 `rustc -vV` 探测版本信息——工具链探测本身也在 util 基础设施内完成。

## 相关概念

- [ops 命令实现](/concepts/06-ops-command-implementation.md) — create_bcx 的调用方与 CompileOptions 的构造
- [依赖解析 resolver](/concepts/04-dependency-resolver.md) — Resolve 图是 unit 图的输入
- [Workspace 与 Package 模型](/concepts/02-workspace-package-model.md) — Unit.pkg 的类型来源
- [util 基础设施](/concepts/09-util-infrastructure.md) — Rustc 探测、Graph 与 Queue 的定义地
