---
type: Example
title: x.py 构建流程剖析
description: 沿一次 ./x 调用逐层走读：入口脚本选择解释器、bootstrap.py 编译 bootstrap 二进制、Kind 分发到 build_steps、三阶段产物落盘 build/ 目录
tags: [rust, bootstrap, build, walkthrough]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-28T10:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T10:00:00+08:00" }
status: stable
stale_after: 2027-08-28
sources:
  - id: rustc-source
    resource: /references/rustc-source-map.md
---

# x.py 构建流程剖析

本篇是 [bootstrap 构建系统](/concepts/01-bootstrap-build-system.md) 的实操走读：沿用户敲下的一条命令，逐层观察它触发的每个环节。前置阅读：[简介与仓库导航](/concepts/00-intro-repo-navigation.md)。

## 第 0 步：你敲的是哪个入口

仓库提供三个入口，先分清：

- **`./x`**（推荐）：POSIX shell 脚本，按 `OSTYPE` 选择解释器搜索顺序——cygwin/msys 下按 `py python3 python python2 uv`，其余按 `python3 python py python2 uv`——找到后以该解释器执行同目录的 `x.py`；
- **`x.py`**：跨平台 Python 入口。它自述只是 bootstrap.py 的"symlink"（第 5 行注释："This file is only a 'symlink' to bootstrap.py, all logic should go there."），末尾把 `src/bootstrap` 插入 `sys.path` 后 `import bootstrap` 并调用 `bootstrap.main()`；
- **`src/tools/x`**：独立 Rust crate（`name = "x"`、version = "0.1.1"、description = "Run x.py slightly more conveniently"），纯粹是便利包装。

结论：**一切逻辑都在 bootstrap.py 与 src/bootstrap**，三个入口只是不同的引信。

## 第 1 步：bootstrap 的自我编译

`src/bootstrap` 本身是一个 Rust crate：Cargo.toml 声明 `name = "bootstrap"`、`version = "0.0.0"`、`edition = "2024"`，定义三个 bin target：`bootstrap`（src/bin/main.rs）、`rustc`（src/bin/rustdoc.rs 之外还有 rustc.rs）、`rustdoc`（src/bin/rustdoc.rs）。bootstrap.py 的职责就是：用系统上可用的 Rust（或下载的）把 bootstrap crate 编译成可执行文件，然后交接控制权。

两个 feature 开关值得知道：`build-metrics`（依赖 sysinfo，构建指标）与 `tracing`（依赖 tracing/tracing-chrome/tracing-subscriber/chrono，性能追踪）。依赖锁版有讲究：`cc = "=1.2.62"`、`cmake = "=0.1.54"` 精确锁定，注释说明升级它们通常需要改 bootstrap 代码。

## 第 2 步：sanity 检查与配置装配

bootstrap 二进制启动后读取配置并做 sanity 检查（src/bootstrap/src/core/ 模块之一即 sanity）。配置来源有：仓库根的 config.toml（可选）、环境变量，以及 `src/bootstrap/defaults/` 下的四个默认配置文件——bootstrap.compiler.toml、bootstrap.dist.toml、bootstrap.library.toml、bootstrap.tools.toml。`./x setup`（Kind::Setup）可以交互式生成 config.toml。

## 第 3 步：Kind 分发

命令的第一个词映射到 `pub enum Kind`（src/bootstrap/src/core/builder/mod.rs:626，derive ValueEnum）：Build、Check、Clippy、Fix、Format、Test、Miri、MiriSetup、MiriTest、Bench、Doc、Clean、Dist、Install、Run、Setup、Vendor、Perf。五个高频命令带单字母别名：`x b`=Build、`x c`=Check、`x t`=Test、`x d`=Doc、`x r`=Run。

`Builder<'a>`（builder/mod.rs:44）是编排中枢，字段含 `sess: &'a Session`、`top_stage: u32`、`kind: Kind`、`cache: Cache`、`stack: RefCell<Vec<Box<dyn AnyDebug>>>`、`time_spent_on_dependencies: Cell<Duration>`、`paths: Vec<PathBuf>`、`submodule_paths_cache: OnceLock<Vec<String>>`、`log_cli_step_for_tests`。随后的路径参数由 cli_paths 解析——`src/bootstrap/src/core/builder/cli_paths/snapshots/` 下 68 个 `.snap` 快照文件守护着这些解析的回归测试（覆盖 `x build/check/test/doc/dist/clean/miri/run/setup/vendor/fix/fmt/clippy/install/bench` 等命令的路径形态）。

## 第 4 步：build_steps 的 Step 执行

以 `x build` 为例，控制流进入 `core/build_steps/mod.rs` 声明的 18 个步骤模块之一（check、clean、clippy、compile、dist、doc、format、gcc、install、llvm、perf、run、setup、synthetic_targets、test、tool、toolstate、vendor）。编译类步骤全部住在 compile.rs，Step 结构体按行号排布：`Std`(L47)、`StdLink`(L724)、`StartupObjects`(L896)、`BuiltRustc`(L981)、`Rustc`(L995)、`GccDylibSet`(L1575)、`GccCodegenBackend`(L1663)、`CraneliftCodegenBackend`(L1740)、`Sysroot`(L1912)。

步骤执行时，"用哪个编译器"的问题由 `pub struct Compiler`（core/compiler.rs:11）回答：字段 `stage: u32`、`host: TargetSelection`、`forced_compiler: bool`，其 Hash/PartialEq 只用 stage 与 host——在 bootstrap 眼里编译器身份就是 (stage, host) 二元组。

## 第 5 步：三阶段自举展开

README「Build phases」的三步在此落地：

1. 入口脚本下载 stage0 编译器/Cargo 二进制——下载源锁定在 `src/stage0`：`dist_server=https://static.rust-lang.org` 等；当前 bootstrap 编译器为 2026-08-18 的 beta（commit `f47d5bb1…`，manifest hash `7c8035ec…`），rustfmt 同日 nightly（`8fa1c96c…`）；下载清单节由 `./x.py run src/tools/bump-stage0` 生成，列有各目标三元组压缩包的 sha256 校验；
2. bootstrap 做完 sanity 检查后用预编译 stage0 编译器准备构建 stage 1；
3. stage0 编译器+标准库构建 stage1 编译器（链接 stage0 标准库），stage1 编译器构建 stage1 标准库，最后 stage1 编译器产出 stage2 编译器（链接 stage1 标准库）。

## 第 6 步：观察产物

构建输出全部落在 `build/`：cache/（按日期缓存 stage0 下载的 tarball）、bootstrap/（debug、release 两种构建）、misc-tools/、node_modules/、dist/、tmp/ 以及按 host triple 命名的目录。排查构建问题的动作序列：先查 `src/stage0` 的日期与哈希（起点是否变了），再看 `build/` 目录结构（走到了哪一步），最后才进源码。

## 常见诊断场景速查

| 症状 | 先查 |
|------|------|
| 构建行为突然变化 | `src/stage0`：beta 日期/哈希是否被 bump |
| 想知道某命令支持哪些路径 | cli_paths/snapshots/ 对应 .snap 文件 |
| cc/cmake 相关失败 | bootstrap Cargo.toml 的精确锁版注释（升级需改代码） |
| dist 产物异常 | library/Cargo.toml 的 `[profile.dist]`（bootstrap 预构建 libstd 的专用 profile） |

## 相关概念

- [bootstrap 构建系统](/concepts/01-bootstrap-build-system.md) — 本篇的概念基础
- [简介与仓库导航](/concepts/00-intro-repo-navigation.md) — 构建域的三个世界划分
- [rustdoc 与工具链](/concepts/10-rustdoc-toolchain.md) — `x test` 背后的 compiletest 与 22 套件
