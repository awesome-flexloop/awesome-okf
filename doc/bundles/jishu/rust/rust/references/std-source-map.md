---
type: Reference
title: 标准库信源登记
description: rust-lang/rust 标准库域（library/）的 workspace 配置、23 个目录清单、core/alloc/std 关键文件坐标、sysroot 与 panic 运行时坐标
tags: [rust, std, source, reference, library]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-28T10:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T10:00:00+08:00" }
status: stable
stale_after: 2027-08-28
sources:
  - id: rust-repo
    resource: external/libs/rust-lang/rust
    title: rust-lang/rust 源码仓库（main @ e457a7b0）
---

# 标准库信源登记

## 基本信息

| 属性 | 值 |
|------|-----|
| 所属仓库 | rust-lang/rust（main @ e457a7b0d326d67b4322ef0d11bd715cfaeda48f，2026-08-27 采集） |
| 版本 | 1.100.0（`src/version`，与编译器共用同一版本真源） |
| 源码根 | `external/libs/rust-lang/rust/library/` |
| workspace | 独立 Cargo workspace，`resolver = "1"` |

## workspace 配置

`library/Cargo.toml` 与根 workspace 完全独立：

- members = `["std", "sysroot", "coretests", "alloctests"]`
- exclude = `["stdarch", "windows_link"]`（两者各自拥有独立 workspace，配置中有注释说明）

### 特殊构建配置

| 配置 | 内容 | 动机 |
|------|------|------|
| `[profile.release.package.compiler_builtins]` | `codegen-units = 10000` | 将每个 intrinsic 放入独立目标文件，避免与系统 libgcc 的符号冲突 |
| `[profile.dist]` | `inherits = "release"`、`codegen-units = 1`、`debug = 1`、rustflags 含 `-Cembed-bitcode=yes`、`-Zunstable-options`、`-Cforce-frame-pointers=non-leaf` | 由 bootstrap 用于预构建 libstd 发行产物 |
| `[patch.crates-io]` | rustc-std-workspace-core/alloc/std 与 windows-sys 指向 library/ 下本地路径 | 构建 sysroot 时劫持同名 crates.io 依赖 |
| panic_abort profile | dev 与 release 两个 profile 均设 `rustflags = ["-Cpanic=abort"]` | "panic_abort must always be compiled with panic=abort, even when the rest of the sysroot is panic=unwind" |

## library/ 目录清单（23 个）

| 目录 | 角色 |
|------|------|
| core | 依赖无关的核心库（零上游、零系统库、零 libc） |
| alloc | 堆分配层（智能指针、集合、format） |
| std | 面向用户的标准库门面（facade） |
| sysroot | 虚拟 crate：确保所有必需 crate 出现在 sysroot |
| coretests / alloctests | core 与 alloc 的测试 harness |
| panic_abort / panic_unwind | 两种 panic 策略运行时 |
| unwind | 栈展开支持 |
| rtstartup | Windows 运行时启动对象（rsbegin.rs、rsend.rs） |
| backtrace | 回溯支持 |
| compiler-builtins | 内建函数（intrinsic）实现 |
| proc_macro | 过程宏运行时支持 |
| profiler_builtins | 性能分析支持 |
| portable-simd / std_detect | 便携 SIMD 与 CPU 特性检测 |
| rustc-std-workspace-core / -alloc / -std | 三个转发 crate（供 `-Zbuild-std` 依赖图使用） |
| stdarch | 独立 workspace（exclude 之一） |
| windows_link / windows-sys | Windows 平台链接支持（windows_link 为独立 workspace） |
| test | libtest 测试 harness |

## core 坐标

| 坐标 | 内容 |
|------|------|
| library/core/src/lib.rs L1-14 | crate 文档：core 是标准库"依赖无关的基础"，"links to no upstream libraries, no system libraries, and no libc"；且"core library is *minimal*: it isn't even aware of heap allocation, nor does it provide concurrency or I/O" |
| library/core/src/lib.rs L46-66 | 内部属性：`#![stable(feature = "core", since = "1.6.0")]`、`#![no_core]`、`#![rustc_coherence_is_core]`、`#![rustc_preserve_ub_checks]` |
| library/core/src/lib.rs L21-44 | 依赖的外部符号诚实清单：`memcpy`、`memmove`、`memset`、`memcmp`、`bcmp`、`strlen`（由 codegen 后端或 compiler-builtins 提供）、panic handler（`#[panic_handler]`）、`rust_eh_personality` |
| library/core/src/lib.rs L199-389 | 顶层 pub 模块：prelude、f128、f16、f32、f64、num、hint、intrinsics、mem、profiling、ptr、ub_checks、borrow、clone、cmp、convert、default、error、field、index、marker、ops、any、array、ascii、asserting、async_iter、bstr、cell、char、ffi、io、iter、net、os、panic、panicking、pat、pin、process、random、range、result、sync、unsafe_binder、fmt、hash、slice、str、time、wtf8、unicode、future、task、alloc、view、primitive、arch、simd、from、autodiff、offload、contracts |
| library/core/src/ | 含 `lib.miri.rs`（core/alloc/std 三库各有同名文件，供 Miri 解释执行） |

## alloc 坐标

`library/alloc/src/` 顶层源文件：alloc.rs、borrow.rs、boxed.rs、bstr.rs、fmt.rs、intrinsics.rs、lib.rs、lib.miri.rs、macros.rs、panicking.rs、rc.rs、slice.rs、str.rs、string.rs、sync.rs、task.rs；子目录：boxed/、ffi/、io/、raw_vec/、vec/、wtf8/。

## std 坐标

| 坐标 | 内容 |
|------|------|
| library/std/src/lib.rs L1-12 | crate 文档："The Rust Standard Library is the foundation of portable Rust software, a set of minimal and battle-tested shared abstractions for the broader Rust ecosystem."；"std is available to all Rust crates by default." |
| library/std/src/lib.rs L459-782 | 顶层 pub 模块：prelude、rt、f128、f16、f32、f64、thread、ascii、backtrace、bstr、collections、env、error、ffi、fs、hash、io、net、num、os、panic、pat、path、process、random、sync、time、view、simd、autodiff、offload、task、arch、sys、alloc、from（另有私有模块 macros、std_float、panicking、backtrace_rs） |
| library/std/src/sys/mod.rs | 私有模块：configure_builtins、helpers、pal、personality；pub 模块：alloc、args、backtrace、cmath、env、env_consts、exit、fd、fs、io、net 等 |
| library/std/src/os/ | 40 个平台子目录：aix、android、cygwin、darwin、dragonfly、emscripten、espidf、fd、fortanix_sgx、freebsd、fuchsia、haiku、hermit、horizon、hurd、illumos、ios、l4re、linux、macos、motor、net、netbsd、nto、nuttx、openbsd、raw、redox、rtems、solaris、solid、trusty、uefi、unix、vita、vxworks、wasi、wasip2、windows、xous |
| library/std/src/env.rs | `current_dir`(L53)、`set_current_dir`(L80)、`vars`(L135)、`vars_os`(L160)、`var`(L228)、`var_os`(L264)、`split_paths`(L483)、`join_paths`(L578)、`home_dir`(L646)、`temp_dir`(L706)、`current_exe`(L757)；结构体 `Vars`(L90)、`VarsOs`(L100)、`SplitPaths`(L447)、`JoinPathsError`(L511) |
| library/std/src/fs.rs | `File`(L135)、`Dir`(L189)、`Metadata`(L202)、`ReadDir`(L220)、`DirEntry`(L239)、`OpenOptions`(L279)、`FileTimes`(L285)、`Permissions`(L298)、`FileType`(L305)、`DirBuilder`(L313)；函数 `read`(L346)、`read_to_string`(L389)、`write`(L427)、`set_times`(L470)、`set_times_nofollow`(L511) |
| library/std/src/rt.rs | 再导出 `crate::panicking::{begin_panic, panic_count}` 与 `core::panicking::{panic_display, panic_fmt}`；宏 `rtprintpanic!`(L40)、`rtabort!`(L53)、`rtassert!`(L62)、`rtunwrap!`(L70)；`unsafe fn init(argc: isize, argv: *const *const u8, sigpipe: u8)`(L111)、`lang_start`(L199)、`lang_start_internal`(L152) |
| library/std/src/pat.rs | 全文两行："Helper module for exporting the 'pattern_type' macro" 与 `pub use core::pattern_type;` |
| library/std/ | 存在 build.rs |

## sysroot 与 panic 运行时坐标

| 坐标 | 内容 |
|------|------|
| library/sysroot/Cargo.toml | `name = "sysroot"`、`version = "0.0.0"`、`edition = "2024"`；注释"this is a dummy crate to ensure that all required crates appear in the sysroot"；依赖 proc_macro（public）、profiler_builtins（optional）、std（public）、test（public）；`default = ["panic-unwind"]`，其余 feature 均转发给 std |
| library/rtstartup/ | rsbegin.rs 与 rsend.rs（运行时启动对象） |
| library/panic_unwind/src/ | 平台实现：dummy.rs、gcc.rs、lib.rs、miri.rs、seh.rs |
| library/panic_abort/src/ | lib.rs 与 zkvm.rs |

## 相关导航

- 标准库分层架构的完整讲解见 [标准库分层架构](/concepts/08-std-layered-architecture.md)
- 逐模块剖析示例见 [std 模块结构剖析](/examples/std-module-anatomy.md)
- 编译器域信源登记见 [rustc 编译器信源登记](/references/rustc-source-map.md)
