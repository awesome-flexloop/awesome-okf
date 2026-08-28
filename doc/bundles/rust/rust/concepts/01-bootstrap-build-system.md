---
type: Concept
title: bootstrap 构建系统：Python 壳、Rust 芯与三阶段自举
description: x.py 如何用固定的 stage0 beta 编译器自举出 stage1/stage2 工具链；bootstrap crate 的模块结构、Builder 与 Kind、step 体系与构建输出布局
tags: [rust, rustc, bootstrap, build-system]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-28T10:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T10:00:00+08:00" }
status: stable
stale_after: 2027-08-28
sources:
  - id: rustc-source
    resource: /references/rustc-source-map.md
---

# bootstrap 构建系统：Python 壳、Rust 芯与三阶段自举

## 核心反常识：构建从不信任本机工具链

多数编译器项目的构建直觉是"先装好编译器，再 make"。rust-lang/rust 的构建系统 **bootstrap** 打破这一直觉：本机已安装的 rustc 完全不参与构建，起点是从 CI 下载的、带 sha256 哈希校验的固定 **beta** 编译器。当前 `src/stage0` 记录的 bootstrap 编译器为：

- `compiler_date=2026-08-18`
- `compiler_version=beta`
- `compiler_git_commit_hash=f47d5bb13648d5c859f5b438eb7dc834b9729961`
- `compiler_channel_manifest_hash=7c8035eccd259661acc845afb33fb40892f4722327f7d8d8c49feda172d1a159`

同一文件还记录了 bootstrap 用的 rustfmt：`rustfmt_date=2026-08-18`、`rustfmt_version=nightly`、`rustfmt_git_commit_hash=8fa1c96c…`。`src/stage0` 头部还携带服务器与分支信息：`dist_server=https://static.rust-lang.org`、`artifacts_server=https://ci-artifacts.rust-lang.org/rustc-builds`、`artifacts_with_llvm_assertions_server=https://ci-artifacts.rust-lang.org/rustc-builds-alt`、`git_merge_commit_email=bors@rust-lang.org`、`nightly_branch=main`。该文件的下载清单节由 `./x.py run src/tools/bump-stage0` 工具生成，列出 `dist/2026-08-18/` 下各目标三元组的 rustc-beta/rust-std-beta 压缩包的 sha256 哈希。

诊断构建问题的第一步永远是查 `src/stage0` 的日期与哈希，再谈源码。

## Python 壳与 Rust 芯

`x.py` 自述只是 bootstrap.py 的"symlink"（第 5 行注释："This file is only a 'symlink' to bootstrap.py, all logic should go there."），其末尾将 `src/bootstrap` 插入 `sys.path` 后 `import bootstrap` 并调用 `bootstrap.main()`。

但 bootstrap 的主体并不是 Python——`src/bootstrap` 本身是一个 Rust crate：Cargo.toml 声明 `name = "bootstrap"`、`version = "0.0.0"`、`edition = "2024"`，并定义三个 bin target：`bootstrap`（src/bin/main.rs）、`rustc`（src/bin/rustc.rs）、`rustdoc`（src/bin/rustdoc.rs）。它的 features 有两个：`build-metrics`（依赖 sysinfo）与 `tracing`（依赖 tracing/tracing-chrome/tracing-subscriber/chrono）。

对关键依赖的锁版也值得注意：bootstrap 的 Cargo.toml 中 `cc = "=1.2.62"`、`cmake = "=0.1.54"` 以**精确版本**锁定，注释说明更新这些依赖通常需要修改 bootstrap 代码。

`src/bootstrap/src/lib.rs` 模块级文档第一行是 "Implementation of bootstrap, the Rust build system."，其顶层模块为 `cli_main`、`core`、`utils`。`core/mod.rs` 声明 11 个模块：android、backend、build_steps、builder、compiler、config、debuggers、download、metadata、sanity、session；`core/build_steps/mod.rs` 再声明 18 个步骤模块：check、clean、clippy、compile、dist、doc、format、gcc、install、llvm、perf、run、setup、synthetic_targets、test、tool、toolstate、vendor。

## 三阶段自举：蛇吞尾

`src/bootstrap/README.md` 的「Build phases」一节描述了完整链条：

1. **入口脚本**（unix 用 `x`、windows 用 `x.ps1`、跨平台 `x.py`）下载 stage0 编译器/Cargo 二进制并编译构建系统自身，再调用 bootstrap 二进制。
2. **bootstrap 二进制**读取配置并做 sanity 检查后，用预编译 stage0 编译器准备构建 stage 1。
3. **stage 0 编译器与标准库构建 stage 1 编译器**（链接 stage 0 标准库），stage 1 编译器构建 stage 1 标准库，随后 stage 1 编译器产出 stage 2 编译器（链接 stage 1 标准库）。

这就是"蛇吞尾"：新编译器由上一代编译器产出。在 bootstrap 语义里，"哪个编译器"只是 `(stage, host)` 二元组——`pub struct Compiler`（src/bootstrap/src/core/compiler.rs:11）的字段是 `stage: u32`、`host: TargetSelection`、`forced_compiler: bool`，而其 Hash/PartialEq 实现只使用 stage 与 host 两个字段。

## Builder：Kind 与 Step

`Builder<'a>`（src/bootstrap/src/core/builder/mod.rs:44）是构建编排中枢，字段包括 `sess: &'a Session`、`top_stage: u32`、`kind: Kind`、`cache: Cache`、`stack: RefCell<Vec<Box<dyn AnyDebug>>>`、`time_spent_on_dependencies: Cell<Duration>`、`paths: Vec<PathBuf>`、`submodule_paths_cache: OnceLock<Vec<String>>`、`log_cli_step_for_tests`。

`pub enum Kind`（builder/mod.rs:626）枚举所有顶层命令：Build、Check、Clippy、Fix、Format、Test、Miri、MiriSetup、MiriTest、Bench、Doc、Clean、Dist、Install、Run、Setup、Vendor、Perf；其中 Build/Check/Test/Doc/Run 五个高频命令带单字母别名（b/c/t/d/r）。

编译类步骤定义在 `core/build_steps/compile.rs`，Step 结构体包括：`Std`(L47)、`StdLink`(L724)、`StartupObjects`(L896)、`BuiltRustc`(L981)、`Rustc`(L995)、`GccDylibSet`(L1575)、`GccCodegenBackend`(L1663)、`CraneliftCodegenBackend`(L1740)、`Sysroot`(L1912)。配置侧，`core/config/mod.rs` 定义了一组枚举：CompilerBuiltins、Allocator、DebuginfoLevel、StringOrBool、StringOrInt、LlvmLibunwind、SplitDebuginfo、CompressDebuginfo、ReplaceOpt、DryRun、RustcLto、GccCiMode、LlvmCiMode、DebuggerPath。

## 配置与输出布局

`src/bootstrap/defaults/` 提供 4 个默认配置文件：bootstrap.compiler.toml、bootstrap.dist.toml、bootstrap.library.toml、bootstrap.tools.toml。bootstrap 目录还同时存在 `bootstrap.py`、`bootstrap_test.py`、`configure.py`、`build.rs`、`download-ci-llvm-stamp`、`download-ci-gcc-stamp`、`stdlib-semver-check-stamp`。

构建输出位于 `build/` 目录，其子目录包括：cache/（按日期缓存 stage0 下载的 tarball）、bootstrap/（debug、release）、misc-tools/、node_modules/、dist/、tmp/ 以及按 host triple 命名的目录。第一次跑 `x check` 后观察 `build/` 结构，是建立构建直觉的最快方式。

命令行路径解析的回归防护也很特别：`src/bootstrap/src/core/builder/cli_paths/snapshots/` 下有 68 个 `.snap` 快照文件，对应 `x build`/`x check`/`x test`/`x doc`/`x dist`/`x clean`/`x miri`/`x run`/`x setup`/`x vendor`/`x fix`/`x fmt`/`x clippy`/`x install`/`x bench` 等命令的路径解析测试。

## 三个入口的差异

- `x.py`：跨平台 Python 入口，逻辑全部委托 bootstrap.py。
- `x`：POSIX shell 脚本，按 `OSTYPE` 选择解释器搜索顺序（cygwin/msys 下 `py python3 python python2 uv`，其余 `python3 python py python2 uv`），找到后以该解释器执行同目录 `x.py`。
- `src/tools/x`：独立 Rust crate（`name = "x"`、version = "0.1.1"、description = "Run x.py slightly more conveniently"），只是让运行 x.py 更方便的包装。

## 相关概念

- [简介与仓库导航](/concepts/00-intro-repo-navigation.md) — bootstrap 在仓库三层地图中的位置（src/bootstrap 被根 workspace exclude）
- [编译器流水线总览](/concepts/02-compiler-pipeline-overview.md) — bootstrap 产出的 rustc 内部如何组织
- [x.py 构建流程剖析](/examples/x-py-build-walkthrough.md) — 沿一次构建调用链的逐步走读
- [rustdoc 与工具链](/concepts/10-rustdoc-toolchain.md) — 45 个工具目录如何被 bootstrap 编排
