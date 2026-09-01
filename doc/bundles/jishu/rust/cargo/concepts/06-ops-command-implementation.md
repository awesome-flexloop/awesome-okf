---
type: Concept
title: ops 命令实现：39 个薄壳下的业务核心
description: ops 模块的命令业务实现、cargo_compile 编译族单一入口、resolve_ws 解析编排族与 lockfile 读写函数
tags: [rust, cargo, ops, commands, compile]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-28T10:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T10:00:00+08:00" }
status: stable
stale_after: 2027-08-28
sources:
  - id: cargo-source
    resource: /references/cargo-source-map.md
---

# ops 命令实现：39 个薄壳下的业务核心

lib.rs 的官方自述为整个 CLI 层定了调（F-cargo-037）：

> `ops` — "Every major operation is implemented here. **Each command is a thin wrapper around ops**."
> `ops::cargo_compile` — "the entry point for all the compilation commands"

直觉认为 `cargo build`/`test`/`doc`/`run` 各自独立实现；实际它们共用 `ops::cargo_compile` 单一入口，命令差异被吸收进 `CompileOptions`/`CompileMode`/`Unit`。阅读任何命令的第一问因此变成："它的 ops 函数是什么？"

## 模块清单（F-cargo-051/052）

ops/mod.rs 的 mod 声明（F-cargo-051）：`cargo_add`、`cargo_clean`、`cargo_config`、`cargo_doc`、`cargo_fetch`、`cargo_fix`、`cargo_install`、`cargo_metadata`、`cargo_new`、`cargo_package`、`cargo_pkgid`、`cargo_read_manifest`、`cargo_remove`、`cargo_run`、`cargo_test`、`cargo_tree`、`cargo_uninstall`、`cargo_update`、`cargo_vendor`、`common_for_install_and_uninstall`；另有目录形式：`cargo_add/`、`cargo_compile/`、`cargo_fix/`、`cargo_package/`、`cargo_report/`、`cargo_tree/`、`registry/`——`cargo_compile` 等复杂模块升级为目录（mod.rs + 协作文件）。

re-exports 层（F-cargo-052）按命令族分组：

| 命令族 | re-export 项 |
|--------|--------------|
| 编译族 | `{CompileOptions, compile, compile_with_exec, create_bcx, print, resolve_all_features}` |
| 清理 | `{CleanContext, CleanOptions, clean}` |
| 文档 | `{DocOptions, OutputFormat, doc}` |
| 拉取 | `{FetchOptions, fetch}` |
| 新建 | `{NewOptions, NewProjectKind, VersionControl, init, new}` |
| 运行 | `run` |
| 测试 | `{TestOptions, run_benches, run_tests}` |
| 锁文件 | `{load_pkg_lockfile, resolve_to_string, write_pkg_lockfile}` |
| 注册表 | `{publish, search, yank, info, registry_login, registry_logout, modify_owners, PublishOpts, OwnersOptions, RegistryCredentialConfig, RegistryOrIndex}` |
| 解析编排 | `{WorkspaceResolve, add_overrides, get_resolved_packages, resolve_with_previous, resolve_ws, resolve_ws_with_opts}` |
| vendor | `{VendorOptions, vendor}` |
| 安装 | `{install, install_list}` |
| 元数据 | `{OutputMetadataOptions, ExportInfo, output_metadata}` |
| 过滤器 | `UnitGenerator`、`{CompileFilter, FilterRule, LibRule, Packages}` |

## 编译族：cargo_compile 的入口族（F-cargo-060）

ops/cargo_compile/mod.rs 的公开入口（F-cargo-060）：

- `pub struct CompileOptions` — 编译族命令的全部差异所在（模式、特征、过滤）
- `pub fn compile<'a>(ws: &Workspace<'a>, options: &CompileOptions) -> CargoResult<Compilation<'a>>` — build/check/rustc 的共同终点
- `pub fn compile_with_exec<'a>(...)` — run/test 等"编译后执行"命令的变体
- `pub fn print<'a>(...)` — 输出编译信息
- `pub fn create_bcx<'a, 'gctx>(...)` — 构造 BuildContext（进入 compiler 子系统的交界，见[编译调度与 unit 图](/concepts/07-build-scheduling-unit-graph.md)）
- `pub fn resolve_all_features(...)` — 全特征解析

compiler/mod.rs 文档把 `ops::cargo_compile::compile` 类比为 rustc 侧的 driver（F-cargo-107）——这是 cargo 与 rustc 的官方结构类比，rustc 架构知识可以直接迁移到 cargo 阅读。

## 解析编排族：resolve_ws 家族（F-cargo-053~055）

ops/resolve.rs 是 resolver 算法的编排层：

```rust
pub struct WorkspaceResolve<'gctx> {
    pkg_set: PackageSet<'gctx>,
    workspace_resolve: Option<Resolve>,   // cargo install 与 -Zavoid-dev-deps 时可为 None
    targeted_resolve: Resolve,
    specs_and_features: Vec<SpecsAndResolvedFeatures>,
}
```

（F-cargo-053，字段注释原文："`cargo install` and `-Zavoid-dev-deps` 时可为 None"。）

主入口 `pub fn resolve_ws<'a>(ws: &Workspace<'a>, dry_run: bool) -> CargoResult<(PackageSet<'a>, Resolve)>` 的调用序（F-cargo-054）：`ws.package_registry()` → `resolve_with_registry` → `get_resolved_packages`——构造源注册表、跑解析、收集包集合三步。

家族其余成员（F-cargo-055）：`resolve_ws_with_opts`（:152，带选项变体）、`resolve_with_previous`（:425，以既有锁文件为起点的增量解析——`--locked` 的实现基础）、`add_overrides`（:559，`[patch]`/路径覆盖注入）、`get_resolved_packages`（:591，解析结果转 PackageSet）。

## lockfile：Cargo.lock 的读写（F-cargo-056）

ops/lockfile.rs 的三个公开函数（F-cargo-056）：

- `pub fn load_pkg_lockfile(ws: &Workspace<'_>) -> CargoResult<Option<Resolve>>` — 读（不存在则 None）
- `pub fn resolve_to_string(ws, resolve) -> CargoResult<String>` — Resolve 图序列化为 TOML 文本
- `pub fn write_pkg_lockfile(ws, resolve: &mut Resolve) -> CargoResult<bool>` — 写（返回是否实际变更）

lib.rs 官方自述：`ops::lockfile` 是 "where Cargo.lock files are loaded and saved"（F-cargo-037）。

## 单命令纵队（F-cargo-057~059、061）

- **cargo_new**（F-cargo-057）：`pub enum VersionControl`（vcs 选择）、`pub struct NewOptions`、`pub enum NewProjectKind`（bin/lib）、`pub fn new(opts: &NewOptions, gctx: &GlobalContext) -> CargoResult<()>`、`pub fn init(opts: &NewOptions, gctx: &GlobalContext) -> CargoResult<NewProjectKind>`
- **cargo_test**（F-cargo-058）：`pub struct TestOptions`、`pub fn run_tests(ws: &Workspace<'_>, options: &TestOptions, test_args: &[&str]) -> CliResult`、`pub fn run_benches(ws, options, args) -> CliResult`
- **cargo_doc**（F-cargo-059）：`pub enum OutputFormat`、`pub struct DocOptions`、`pub fn doc(ws: &Workspace<'_>, options: &DocOptions) -> CargoResult<()>`
- **cargo_run**（F-cargo-061）：`pub fn run(...)`（cargo_run.rs:12，实现体委托编译族的 `compile_with_exec`）

## 命令→ops 函数对照表

| CLI 命令（builtin） | ops 入口 | 模式差异 |
|---------------------|----------|----------|
| build / check / rustc | `compile` | `CompileMode`/`CompileOptions` |
| run | `cargo_run::run` → `compile_with_exec` | 编译后带执行 |
| test / bench | `run_tests` / `run_benches` | 测试目标过滤 |
| doc | `doc` | `OutputFormat` |
| new / init | `new` / `init` | `NewProjectKind`/`VersionControl` |
| fetch / generate-lockfile | `fetch` / `resolve_ws` 家族 | 只解析不编译 |
| install | `install`（`Workspace::ephemeral` 场景） | 临时 workspace |

本表是追踪任何命令行为的索引入口：从 `src/bin/cargo/commands/<cmd>.rs` 的薄壳出发，一步跳到上表的 ops 函数。

## 相关概念

- [简介与架构总览](/concepts/00-intro-architecture-overview.md) — thin-wrapper 宣言的出处
- [依赖解析 resolver](/concepts/04-dependency-resolver.md) — resolve_ws 家族调用的算法本体
- [编译调度与 unit 图](/concepts/07-build-scheduling-unit-graph.md) — create_bcx 之后的编译世界
- [cargo new 源码路径追踪](/examples/cargo-new-source-trace.md) — 从薄壳到 ops::new 的完整实走
