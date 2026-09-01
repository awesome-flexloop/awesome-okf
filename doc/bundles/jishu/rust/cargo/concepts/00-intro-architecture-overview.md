---
type: Concept
title: 简介与架构总览：src/ 重组基线与组件地图
description: cargo 是什么、仓库双重身份的根 Cargo.toml、版本双轨制、src/ 重组后的组件地图与 lib.rs 八大模块职责
tags: [rust, cargo, architecture, overview]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-28T10:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T10:00:00+08:00" }
status: stable
stale_after: 2027-08-28
sources:
  - id: cargo-source
    resource: /references/cargo-source-map.md
---

# 简介与架构总览：src/ 重组基线与组件地图

## 什么是 cargo

cargo 是 Rust 语言的包管理器与构建工具。README.md 的首句原文定义了它的两大职责：

> "Cargo downloads your Rust project's dependencies and compiles your project."（Cargo 下载你 Rust 项目的依赖并编译你的项目。）（F-cargo-009）

对使用者而言，cargo 是 `cargo build`、`cargo test` 这样的命令行工具；对源码阅读者而言，它同时是一个**workspace 仓库**（编组主 crate 与 19+5 个子 crate）、一个**库 crate**（`cargo` 包，可被作为库嵌入，但 API 永久不稳定）与一个**CLI 二进制**（`src/bin/cargo/`）。README 同时声明："This crate may make major changes to its APIs."（F-cargo-009）

阅读本 bundle 之前必须先建立一张地图：仓库如何编组、主 crate 源码在哪里、八个模块各管什么。本篇即这张地图。

## ⚠️ 结构基线：一次静默的重组

本知识包基于 **master @ 75d17360** 基线（2026-08-26 采集）。此基线已完成结构大重组，与网络上绝大多数旧版 cargo 源码导读的坐标**不一致**：

| 旧文档通行说法 | 本基线实际坐标 | 依据 |
|----------------|----------------|------|
| 主源码位于 `src/cargo/` | 主 crate 源码位于 `src/` | F-cargo-010 |
| 配置类型为 `Config` | 已更名 `GlobalContext`（`src/context/mod.rs`） | F-cargo-043 |
| `SourceId`/`PackageId` 在独立 id 模块 | 位于 `src/workspace/`（`package_id.rs`/`source_id.rs`） | F-cargo-083/085 |
| 根 Cargo.toml 仅为 workspace | 同时声明 `[workspace]` 与 `[package]`（双职合一） | F-cargo-001/003 |

按旧资料导航会直接迷路：配置子系统已独立为 `context/` 模块，"包身份"类型已移驻 `workspace/` 子系统。使用旧版 cargo 源码资料时，只取架构思想，不取路径坐标。

## 仓库解剖：一文件双职的根 Cargo.toml

仓库根的 `Cargo.toml` 同时是 **workspace 清单**与**主 crate 的 package 清单**：

### [workspace] 段（F-cargo-001）

```toml
resolver = "2"
members = ["crates/*", "credential/*", "benches/benchsuite", "benches/capture"]
exclude = ["target/"]  # exclude bench testing
```

- workspace 成员以 glob 收纳 `crates/*`（19 个子 crate）与 `credential/*`（5 个 credential crate），另含两个 bench 成员
- `[workspace.package]` 继承字段（F-cargo-002）：`rust-version = "1.95"`（注释 `# MSRV:3`）、`edition = "2024"`、`license = "MIT OR Apache-2.0"`、`repository = "https://github.com/rust-lang/cargo"`

### [package] 段（F-cargo-003）

```toml
[package]
name = "cargo"
version = "0.101.0"
rust-version = "1.98"  # MSRV:1
documentation = "https://docs.rs/cargo"
description = "Cargo, a package manager for Rust."
```

注意两处细节：主 crate 的 MSRV（`1.98`）**高于** workspace 的 MSRV（`1.95`）；主 crate 的版本是 `0.101.0`——这引出下面的版本双轨制。

另有 `[[bin]]` 声明：`name = "cargo"`、`test = false`、`doc = false`（F-cargo-004），即 CLI 二进制不参与测试与文档构建目标。

### features 与平台特定依赖（F-cargo-005/006）

`[features]` 段定义了 HTTP 传输层的选择：

- `default = ["http-transport-curl"]`
- `http-transport-curl` = `["gix/blocking-http-transport-curl"]`、`http-transport-reqwest` = `["gix/blocking-http-transport-reqwest"]`
- 注释原文："Exactly one of 'http-transport-curl' or 'http-transport-reqwest' must be enabled when using Cargo as a library."（把 Cargo 当库使用时必须恰好启用二者之一）
- `all-static` 聚合 `vendored-openssl`、`curl/static-curl`、`curl/force-system-lib-on-osx`、`vendored-libgit2`

平台特定依赖展示了 credential 的平台矩阵：Linux 含 `cargo-credential-libsecret`，macOS 含 `cargo-credential-macos-keychain`，Windows 含 `cargo-credential-wincred` 与 `windows-sys`（features 列表含 `Win32_System_JobObjects` 等），非 Windows 平台含 optional 的 `openssl`/`openssl-src`（F-cargo-006）。

### workspace 依赖与 lints 治理（F-cargo-007/008）

`[workspace.dependencies]` 集中锁版，关键版本号：`clap = "4.6.0"`、`git2 = { version = "0.21.0", features = ["https", "ssh"] }`、`gix = "0.85.0"`、`curl = "0.4.49"`、`semver = { version = "1.0.27", features = ["serde"] }`、`toml = "1.1.2"`、`toml_edit = "0.25.10"`、`home = "0.5.12"`、`im-rc = "15.1.0"`、`rusqlite = { version = "0.40.0", features = ["bundled"] }`、`pasetors = "0.7.8"`、`rustc-stable-hash = "0.1.2"`、`varisat = "0.2.2"`。这份清单实际上勾勒出了 cargo 的技术选型轮廓：CLI 解析用 clap、git 操作双轨 git2/gix、HTTP 用 curl、SAT 求解用 varisat。

`[workspace.lints.clippy]` 的治理策略值得注意：`all = { level = "allow", priority = -2 }`、`correctness = { level = "warn", priority = -1 }`——整体放行 clippy，但把 correctness 与一组特定 lint（`dbg_macro`、`disallowed_methods`、`disallowed_types`、`print_stderr`、`print_stdout`、`self_named_module_files`）拉回 warn 级别。

## 版本双轨制：0.101.0 的包自称 1.100.0

cargo 存在两条版本链，**刻意脱钩**：

- **包版本**：Cargo.toml 中的 `0.101.0`（F-cargo-003）
- **CLI 显示版本**：`cargo --version` 输出 `1.100.0`

版本说明注释原文（`src/version.rs`）：

> "The library is permanently unstable, so it always has a 0 major version. However, the CLI now reports a stable 1.x version (starting in 1.26) which stays in sync with rustc's version."（库永久不稳定，因此主版本恒为 0；但 CLI 从 1.26 起报告稳定的 1.x 版本，与 rustc 保持同步。）（F-cargo-040）

推导链（F-cargo-144）：非 bootstrap 构建时，`version()` 由 `CARGO_PKG_VERSION_MINOR - 1` 推导出 `1.{minor}.{patch}`（当前 `0.101.0` → `1.100.0`），或使用 bootstrap 注入的 `CFG_RELEASE`；commit 信息来自 build.rs 注入的 `CARGO_COMMIT_HASH`/`CARGO_COMMIT_SHORT_HASH`/`CARGO_COMMIT_DATE`。

讨论 cargo 版本时必须始终区分两个语境：0.x 警示库用户"API 可发生重大变更"（F-cargo-009），1.x 服务工具链视角的版本同步。`cargo -vV` 的完整诊断输出（含 host、libgit2、libcurl、ssl、os 各行）见 [Crate 组织与 CLI 分发](/concepts/01-crate-organization-cli-dispatch.md)。

## 仓库目录地图

```
cargo/                     # 仓库根 = workspace 根 = 主 crate 根
├── Cargo.toml             # [workspace] + [package] 双职合一（F-cargo-001/003）
├── build.rs               # commit_info / compress_man / windows_manifest（F-cargo-135）
├── src/                   # 主 crate 源码（重组后布局，非 src/cargo/）
│   ├── bin/cargo/         # CLI 入口：main.rs、cli.rs、commands/
│   ├── lib.rs             # 库入口：模块声明与组件文档
│   ├── macros.rs
│   ├── version.rs         # 版本双轨推导（F-cargo-040/144）
│   ├── compiler/          # 编译调度子系统
│   ├── context/           # GlobalContext 配置子系统
│   ├── diagnostics/
│   ├── ops/               # 命令业务核心
│   ├── resolver/          # 依赖解析核心算法
│   ├── sources/           # 五种包源
│   ├── util/              # 42 个基础设施工具模块
│   └── workspace/         # Manifest/Package/PackageId/SourceId
├── crates/                # 19 个子 crate（F-cargo-011）
├── credential/            # 5 个 credential crate（F-cargo-123）
├── tests/testsuite/       # 120+ 集成测试模块（F-cargo-140）
├── benches/               # 三类基准（F-cargo-141/142）
└── doc/                   # man 37 手册 / book 四大部分 / contrib 指南
```

crates/ 的 19 个子 crate：build-rs、build-rs-test-lib、cargo-platform、cargo-test-macro、cargo-test-support、cargo-util、cargo-util-schemas、cargo-util-terminal、crates-io、home、mdman、resolver-tests、rustfix、semver-check、xtask-build-man、xtask-bump-check、xtask-lint-docs、xtask-spellcheck、xtask-stale-label（F-cargo-011）。CHANGELOG.md 全文仅一行，指向 Cargo Book（F-cargo-012）；仓库根另有 publish.py、clippy.toml、deny.toml、rustfmt.toml、三份 LICENSE、`.git-blame-ignore-revs`、CODE_OF_CONDUCT.md、CONTRIBUTING.md（F-cargo-013）。

## lib.rs 骨架：八大模块与组件职责

`src/lib.rs` 是主 crate 的入口，它声明了全部模块（F-cargo-033）：

```rust
#[macro_use] mod macros;
pub mod compiler;
pub mod context;
pub mod diagnostics;
pub mod ops;
pub mod resolver;
pub mod sources;
pub mod util;
mod version;
pub mod workspace;
```

re-exports 层（F-cargo-034）：`pub use crate::util::errors::{AlreadyPrintedError, InternalError, VerboseError}`、`pub use crate::util::{CargoResult, CliError, CliResult, GlobalContext, indented_lines}`、`pub use crate::version::version`。注意 `GlobalContext` 经 util 通道 re-export 保持可用。另有常量 `pub const CARGO_ENV: &str = "CARGO";`（F-cargo-035），以及三个公共错误输出函数：`exit_with_error`、`display_error`（遇 `InternalError` 链时输出 "this is an unexpected cargo internal error"）、`display_warning_with_error`（F-cargo-036）。

lib.rs 的模块文档给出了官方自述的组件职责表（F-cargo-037），这是理解 cargo 架构最权威的一句话索引：

| 组件 | 官方自述（原文摘录） |
|------|----------------------|
| `ops` | "Every major operation is implemented here. Each command is a thin wrapper around ops." |
| `ops::cargo_compile` | "the entry point for all the compilation commands" |
| `ops::resolve` | "Top-level API for dependency and feature resolver (e.g. ops::resolve_ws)" |
| `resolver` | "The core algorithm" |
| `compiler` | "the code responsible for running rustc and rustdoc" |
| `sources::source` | "The Source trait is an abstraction over different sources of packages" |
| `context` | "the global application context" |
| `workspace::parser` | "the code for parsing Cargo.toml files" |
| `ops::lockfile` | "where Cargo.lock files are loaded and saved" |

### File Overview：仓库理解的钥匙文件（F-cargo-038）

lib.rs 的 "File Overview" 文档描述了 cargo 世界中的关键文件与目录如何被处理：

- **`Cargo.toml`** — "loaded with workspace::parser::read_manifest and then translated to workspace::manifest::Manifest"
- **`Cargo.lock`** — "loaded with ops::resolve_ws or a variant of it into a resolver::Resolve"
- **`target/`** — "abstracted with compiler::layout"
- **`$CARGO_HOME/registry/`** — 下有 `index/`、`cache/*/*.crate`、`src/*/*`
- **`**/.cargo/config.toml`** — 见 `context` 模块

这份文件清单是追踪任何命令数据流的坐标系：每个概念文档都会回到这五个坐标上。

### 相关 crate 一览（F-cargo-039）

lib.rs 文档还声明了周边 crate 的分工：cargo-platform（"handles parsing cfg expressions"）、cargo-util、cargo-util-schemas（"contains the serde schemas for cargo"）、crates-io（"code for accessing the crates.io API"）、home（"shared between cargo and rustup and is used for finding their home directories"，非 path 依赖）、rustfix（"defines structures that represent fix suggestions from rustc"）、cargo-test-support、cargo-test-macro（"`#[cargo_test]` proc-macro"）、credential（"several packages for implementing the credential providers"）、mdman、resolver-tests。

## 学习路径

本 bundle 的概念文档沿一条命令的数据流推进：

1. **进入与分发**（00→01）：CLI 入口链与三级命令决策树
2. **数据模型与语境**（02→03）：Workspace/Package 模型 → GlobalContext 配置
3. **解析与下载**（04→05）：resolver 依赖解析 → sources 包源
4. **操作与编译调度**（06→07）：ops 业务核心 → compiler 的 BuildRunner
5. **横切纵队**（08→09）：认证与 credential → util 基础设施

## 相关概念

- [Crate 组织与 CLI 分发](/concepts/01-crate-organization-cli-dispatch.md) — `cargo` 命令如何从进程入口走到子命令执行
- [Workspace 与 Package 模型](/concepts/02-workspace-package-model.md) — Cargo.toml 解析后的数据模型
- [ops 命令实现](/concepts/06-ops-command-implementation.md) — "thin wrapper" 宣言的另一端
- [cargo 源码信源登记](/references/cargo-source-map.md) — 基线坐标与文档资产索引
