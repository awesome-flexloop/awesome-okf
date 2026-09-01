---
type: Example
title: Cargo.toml 解析流程
description: 从磁盘上的 Cargo.toml 到 Workspace 内数据模型的解析数据流：parser、Manifest、EitherManifest 与继承字段逐站拆解
tags: [rust, cargo, example, parsing, manifest, toml]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-28T10:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T10:00:00+08:00" }
status: stable
stale_after: 2027-08-28
sources:
  - id: cargo-source
    resource: /references/cargo-source-map.md
---

# Cargo.toml 解析流程

本篇追踪 `Cargo.toml` 从磁盘文件到内存数据模型的完整数据流。lib.rs 的 File Overview 给出了官方两句话定义（F-cargo-038）：

> `Cargo.toml` — "loaded with workspace::parser::read_manifest and then translated to workspace::manifest::Manifest"

配合组件自述（F-cargo-037）：`workspace::parser` 是 "the code for parsing Cargo.toml files"。

**先区分两种 TOML**：`Cargo.toml`（清单，走 workspace::parser）与 `.cargo/config.toml`（配置，走 context 的两层反序列化，F-cargo-041）。二者的解析管线完全不同——前者产出 Manifest 数据模型，后者产出 ConfigValue + schema 类型。

## 第 0 站：磁盘上的文件（F-cargo-038）

File Overview 的坐标定义：

- `Cargo.toml` — 每个包的清单；workspace 根或成员均有一份
- `Cargo.lock` — 解析产物（走 `ops::resolve_ws` 变体载入 `resolver::Resolve`，不在本篇管线内）
- `target/` — 由 `compiler::layout` 抽象（构建输出）
- `$CARGO_HOME/registry/` — `index/`、`cache/*/*.crate`、`src/*/*`（下载侧，见[Sources 与 registry](/concepts/05-sources-registry.md)）

## 第 1 站：解析入口（src/workspace/parser.rs，F-cargo-077/078）

`workspace::parser` 模块（F-cargo-078 的子模块清单）承载 `read_manifest`（F-cargo-038 的官方入口）。解析层的类型底座来自两个方向：

- workspace/mod.rs re-export 的 `{EitherManifest, VirtualManifest}`、`{Manifest, Target, TargetKind}`（F-cargo-077）
- `pub use cargo_util_schemas::core::{GitReference, PackageIdSpec, SourceKind};`（F-cargo-077）——清单字段的 serde schema 已下沉到 cargo-util-schemas 子 crate（"contains the serde schemas for cargo"，F-cargo-039）；workspace 依赖的 `toml = "1.1.2"` 与 `toml_edit = "0.25.10"`（F-cargo-007）在此生效——**toml_edit 保留原始格式信息**，这正是 `cargo add`/`cargo remove` 能"外科手术式"修改清单而不重排格式的机制基础

## 第 2 站：Manifest 与虚拟根（F-cargo-081）

解析产物的第一形态由 `MaybePackage` 区分（workspace/workspace.rs:149）：

```rust
pub enum MaybePackage {
    Package(Package),          // 根有 [package]
    Virtual(VirtualManifest),   // 根只有 [workspace]
}
```

翻译步骤（F-cargo-038）："translated to workspace::manifest::Manifest"——parser 的原始产物经规整化为 `workspace::manifest` 模块的 `Manifest`（re-export 清单含 `{Manifest, Target, TargetKind}`，F-cargo-077）。`Target`/`TargetKind` 承载 `[[bin]]`/`[[test]]`/`[lib]` 段的目标定义。

workspace 成员判定在此发生（F-cargo-081）：根清单的 `WorkspaceConfig::Root(WorkspaceRootConfig)` 携带 `members`/`default_members`/`exclude`/`inheritable_fields`；成员清单的 `WorkspaceConfig::Member { root: Option<String> }` 反向指根。`inheritable_fields: InheritableFields` 正是 `[workspace.package]` 继承（如本 bundle 的根 Cargo.toml：主 crate 从 workspace 继承 edition/license/repository，见 F-cargo-002/003）的数据载体。

## 第 3 站：Workspace 编组（F-cargo-079/080）

`Workspace::new(manifest_path, gctx)`（workspace.rs:224）从任一清单出发：向上找根（`find_workspace_root`，F-cargo-082）→ 枚举 members → 逐成员走第 1-2 站（`loaded_packages: RefCell<HashMap<PathBuf, Package>>` 按需缓存，F-cargo-079）→ 编组为 `Workspace<'gctx>`。

关键前置：`gctx: &'gctx GlobalContext`（F-cargo-079）——解析继承字段（如 `workspace.package.edition`）与 `[patch]`/`[profile]` 读取时需要配置语境；`resolve_behavior`/`resolve_feature_unification` 等 resolver 配置字段也在此刻从清单/配置固化到 Workspace 上。

`Workspace::ephemeral`（:286，F-cargo-080）构造临时 workspace——`cargo install` 与 `cargo new`（在已有 workspace 内）场景的入口。

## 第 4 站：Package 与 Summary（F-cargo-084）

```rust
pub fn new(manifest: Manifest, manifest_path: &Path) -> Package  // package.rs:103
```

`Package`（package.rs:43）把 Manifest 与磁盘路径绑定，方法族（`dependencies`/`targets`/`summary`/`version`/`rust_version`/`map_source` 等）即清单字段的运行时视图。`map_source` 服务源替换场景的身份重映射（`Resolve.replacements`，F-cargo-064）。

`Summary`（workspace/summary.rs，re-export `{FeatureMap, FeatureValue, Summary}`，F-cargo-077）提取依赖与特征声明——这是 resolver 激活（F-cargo-062 的 `ActivateError`/`dep_cache`）的输入面。

## 对照站：.cargo/config.toml 的另一条管线（F-cargo-041/048）

配置文件走完全不同的两层反序列化（详见[GlobalContext 配置系统](/concepts/03-global-context-config.md)）：

| 维度 | Cargo.toml | .cargo/config.toml |
|------|-----------|---------------------|
| 解析模块 | workspace::parser | context（de.rs 的 Deserializer） |
| 中间形态 | Manifest（经 toml/toml_edit） | ConfigValue（`ConfigValue::from_toml`） |
| 目标类型 | Manifest/Target/Package | CargoBuildConfig 等 23 个 schema 类型（F-cargo-047） |
| 多来源合并 | 单文件权威（根+继承字段） | 多来源叠层（`Value<T>` + `Definition` 优先级，F-cargo-048） |
| 产物去向 | Workspace/PackageSet | GlobalContext 的 OnceLock 缓存群（F-cargo-043） |

## 全路径总览

```
Cargo.toml（磁盘）
    │ workspace::parser::read_manifest（F-cargo-037/038）
    │   [toml/toml_edit + cargo-util-schemas schema（F-cargo-007/039）]
    ▼
原始解析产物 ──翻译──► Manifest（workspace::manifest，F-cargo-077）
    │ MaybePackage: Package | Virtual(VirtualManifest)（F-cargo-081）
    │ WorkspaceConfig: Root(WorkspaceRootConfig{inheritable_fields,...}) | Member
    ▼
Workspace::new 编组（F-cargo-079/080）
    │ gctx: &GlobalContext（配置语境前置）
    │ loaded_packages: RefCell<HashMap<PathBuf, Package>> 按需缓存
    ▼
Package（package.rs:103，F-cargo-084）
    │ Summary / FeatureMap / Dependency（F-cargo-077）
    ▼
resolver 激活输入（F-cargo-062）──► Resolve 图 ──► Cargo.lock（F-cargo-056）
```

## 走读要点

1. **两句话入口**：File Overview（F-cargo-038）的"read_manifest + translate to Manifest"是官方管线定义，本篇全部展开都锚定于此
2. **schema 下沉**：清单字段的 serde 定义在 cargo-util-schemas 子 crate——修改清单格式需要同时动两个 crate
3. **继承字段的双文件协作**：`[workspace.package]` 继承要求根与成员清单都进模型（WorkspaceRootConfig.inheritable_fields）
4. **格式保留**：toml_edit 通道使清单编辑类命令（cargo add/remove）得以保格式修改

## 相关概念

- [Workspace 与 Package 模型](/concepts/02-workspace-package-model.md) — 本篇产物类型的完整定义
- [GlobalContext 配置系统](/concepts/03-global-context-config.md) — 对照站的配置管线
- [依赖解析 resolver](/concepts/04-dependency-resolver.md) — Summary 的下游
- [cargo new 源码路径追踪](/examples/cargo-new-source-trace.md) — 产出清单文件的命令侧走读
