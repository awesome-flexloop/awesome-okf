---
type: Example
title: cargo new 源码路径追踪
description: 从敲下 cargo new 到目录落盘的完整源码实走：CLI 分发决策树、Workspace 构造与 ops::new 的逐站坐标
tags: [rust, cargo, example, trace, cargo-new]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-28T10:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T10:00:00+08:00" }
status: stable
stale_after: 2027-08-28
sources:
  - id: cargo-source
    resource: /references/cargo-source-map.md
---

# cargo new 源码路径追踪

本篇实走 `cargo new hello` 的完整源码路径：从进程入口的命令分发，到 workspace 数据模型构造，最终落在 `ops::cargo_new` 的目录生成。这是一次覆盖 CLI 层 → 数据模型层 → ops 层的纵贯走读，读者可以把本篇当作[架构总览](/concepts/00-intro-architecture-overview.md)各组件的串联练习。

## 第 0 站：进程入口（src/bin/cargo/main.rs）

`main()` 的前置流程（F-cargo-014）：`setup_logger()`（`CARGO_LOG` 过滤，F-cargo-015）→ `GlobalContext::default()`（配置语境，见[GlobalContext 配置系统](/concepts/03-global-context-config.md)）→ channel 判定（`features::channel()`，F-cargo-087：读 `RUSTC_BOOTSTRAP` 或 `version().release_channel`）→ 非 fix 代理路径走 `cargo::util::job::setup()`（Windows Job Objects，F-cargo-097）→ `cli::main(&mut gctx)`。

## 第 1 站：cli::main() 分发序（src/bin/cargo/cli.rs）

`cli::main()`（F-cargo-021）依次：clap 解析（`cli(gctx).try_get_matches()`）→ `-C` 处理 → `expand_aliases`（F-cargo-031；`cargo new` 无别名命中——但注意 `n` 不在内置别名表 F-cargo-016，内置别名只有 b/c/d/r/t/rm）→ `-Z help`/`--version`/`--explain`/`--list` 分支不命中 → `Exec::infer("new")`。

## 第 2 站：Exec 三级推断（F-cargo-022）

对 `"new"` 的判定：

1. `commands::builtin_exec("new")` ——命中！`new` 在 39 个 builtin 清单中（F-cargo-026），返回 `Exec::Builtin`
2. （无需继续）`is_manifest_command` 判定对 builtin 是短路的前置（F-cargo-028：`new` 无路径分量且非 `.rs` 扩展——事实上测试 `avoid_ambiguity_between_builtins_and_manifest_commands` 断言所有 builtin 名都不满足 `is_manifest_command`，F-cargo-030）
3. External 分支不涉及

分发的类型机制（F-cargo-027）：`pub type Exec = fn(&mut GlobalContext, &ArgMatches) -> CliResult;`，`builtin_exec` 以字符串 match 把 `"new"` 路由到 `commands::new` 模块的 `exec` 函数。

## 第 3 站：命令薄壳（src/bin/cargo/commands/new.rs）

commands 模块是薄壳（F-cargo-037 的官方宣言："Each command is a thin wrapper around ops"）：解析 `NewOptions`，然后转发到 `ops::cargo_new`（F-cargo-057）：

```rust
// options 结构（F-cargo-057）
pub enum VersionControl { /* vcs 选择：git / none / ... */ }
pub struct NewOptions { /* ... */ }
pub enum NewProjectKind { /* bin / lib */ }

pub fn new(opts: &NewOptions, gctx: &GlobalContext) -> CargoResult<()>        // cargo new
pub fn init(opts: &NewOptions, gctx: &GlobalContext) -> CargoResult<NewProjectKind>  // cargo init
```

注意签名特征：`new`/`init` 只需要 `&GlobalContext`——`cargo new` 是**少数不需要 Workspace 的命令**（目录还不存在，无清单可编组）。这与编译族命令需要先 `Workspace::new` 形成对照。

## 第 4 站：ops::cargo_new 的职责面（F-cargo-057）

`ops::cargo_new.rs`（:22-493）承担目录脚手架的全部业务：创建目录、生成 `Cargo.toml`（含 `[package]` 段与 `edition` 字段——Edition 枚举的 `LATEST_STABLE: Edition2024`，F-cargo-086，决定新项目的默认 edition）、生成 `src/main.rs` 或 `src/lib.rs`（由 `NewProjectKind` 决定）、按 `VersionControl` 初始化 VCS（`git init` 等——util 的 `{FossilRepo, GitRepo, HgRepo, PijulRepo, existing_vcs_repo}` 封装在此消费，F-cargo-089）。

`cargo-new` 配置段（F-cargo-042 的 20 个顶层键之一：`cargo-new`）允许配置默认 VCS 等偏好。

## 对照站：如果命令需要 Workspace（F-cargo-077~080）

作为对比，设想 `cargo build` 的路径会多一站数据模型构造（详见[Cargo.toml 解析流程](/examples/cargo-toml-parsing-flow.md)）：

```rust
// workspace.rs 的构造入口（F-cargo-079/080）
pub fn new(manifest_path: &Path, gctx: &'gctx GlobalContext)
    -> CargoResult<Workspace<'gctx>>   // :224
pub fn ephemeral(...)                    // :286 临时 workspace
```

`Workspace<'gctx>` 的 `gctx: &'gctx GlobalContext` 字段（F-cargo-079）印证了配置语境先于数据模型的生命周期序。`cargo new` 不走这一站，`cargo init` 在已有目录上操作时则会与已有 workspace 结构交互（`find_workspace_root`，F-cargo-082，避免在成员目录内嵌套创建）。

## 全路径总览

```
$ cargo new hello
    │
    ├─ main()（F-cargo-014）
    │   ├─ setup_logger（F-cargo-015）
    │   ├─ GlobalContext::default()
    │   └─ job::setup（F-cargo-097）
    │
    ├─ cli::main()（F-cargo-021）
    │   ├─ clap 解析（cli() 构造，F-cargo-024）
    │   ├─ expand_aliases（F-cargo-031，无命中）
    │   └─ Exec::infer("new")（F-cargo-022）
    │       ├─ builtin_exec("new") 命中（F-cargo-026/027）
    │       └─ Exec::Builtin(commands::Exec)
    │
    ├─ commands::new::exec（薄壳，F-cargo-037）
    │   └─ 构造 NewOptions（F-cargo-057）
    │
    └─ ops::cargo_new::new（F-cargo-057）
        ├─ 生成 Cargo.toml（Edition 默认 Edition2024，F-cargo-086）
        ├─ 生成 src/main.rs / src/lib.rs（NewProjectKind）
        └─ VCS 初始化（VersionControl → GitRepo 等，F-cargo-089）
```

## 走读要点

1. **薄壳模式的验证**：CLI 层（commands/）不含业务，三站即达 ops——`cargo new` 总路径只有两层跳转
2. **Workspace 不是必需品**：`cargo new` 只需 GlobalContext；需要清单信息的命令才构造 Workspace——区分"语境依赖"与"模型依赖"
3. **决策树的最小路径**：builtin 命中即短路，manifest/external 分支不参与；若换成 `cargo run main.rs` 则走 Manifest 分支并撞上 `-Zscript` 报错（F-cargo-028/029）

## 相关概念

- [Crate 组织与 CLI 分发](/concepts/01-crate-organization-cli-dispatch.md) — 本篇决策树的完整定义
- [Workspace 与 Package 模型](/concepts/02-workspace-package-model.md) — 对照站的数据模型
- [ops 命令实现](/concepts/06-ops-command-implementation.md) — 第 4 站的模块全景
- [Cargo.toml 解析流程](/examples/cargo-toml-parsing-flow.md) — `cargo new` 产出的文件如何被读回
