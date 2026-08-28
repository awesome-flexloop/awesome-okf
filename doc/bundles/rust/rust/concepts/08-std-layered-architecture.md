---
type: Concept
title: 标准库分层架构：core→alloc→std 洋葱与平台分发
description: library/ 独立 workspace 的洋葱分层：零依赖的 core、堆分配的 alloc、面向用户的 std 门面，以及 sys/pal/os 的平台分发与 panic 运行时
tags: [rust, std, core, alloc, platform]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-28T10:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T10:00:00+08:00" }
status: stable
stale_after: 2027-08-28
sources:
  - id: std-source
    resource: /references/std-source-map.md
---

# 标准库分层架构：core→alloc→std 洋葱与平台分发

## 一个独立的 workspace

标准库不住在根 workspace 里。`library/Cargo.toml` 是独立 workspace：`resolver = "1"`（注意与根 workspace 的 "2" 不同），members = `["std", "sysroot", "coretests", "alloctests"]`，exclude = `["stdarch", "windows_link"]`（两者各自拥有独立 workspace）。

`library/` 顶层共 23 个目录：alloc、alloctests、backtrace、compiler-builtins、core、coretests、panic_abort、panic_unwind、portable-simd、proc_macro、profiler_builtins、rtstartup、rustc-std-workspace-alloc、rustc-std-workspace-core、rustc-std-workspace-std、std、std_detect、stdarch、sysroot、test、unwind、windows_link、windows-sys。

## 洋葱的第一层：core 的零依赖宣言

core 是整个洋葱的最内层，crate 文档（library/core/src/lib.rs L1-14）给出双重宣言：

> "The Rust Core Library is the dependency-free foundation of The Rust Standard Library… It links to no upstream libraries, no system libraries, and no libc."
>
> "The core library is *minimal*: it isn't even aware of heap allocation, nor does it provide concurrency or I/O."

零依赖不等于零依赖外部符号。core 的文档（L21-44）诚实列出了它**依赖已存在**的符号：`memcpy`、`memmove`、`memset`、`memcmp`、`bcmp`、`strlen`（由代码生成后端或 compiler-builtins 提供）、panic handler（`#[panic_handler]`）、`rust_eh_personality`。这是理解"零依赖"的精确含义：不链接任何库，但约定一组必须由外界提供的 C ABI 符号。

core 的特殊身份由内部属性（L46-66）声明：`#![stable(feature = "core", since = "1.6.0")]`、`#![no_core]`（core 自己不能依赖 core）、`#![rustc_coherence_is_core]`（告诉编译器一致性检查以 core 为根）、`#![rustc_preserve_ub_checks]`（保留 UB 检查语义）。

core 的顶层 pub 模块清单（L199-389）近 60 个：prelude、f128、f16、f32、f64、num、hint、intrinsics、mem、profiling、ptr、ub_checks、borrow、clone、cmp、convert、default、error、field、index、marker、ops、any、array、ascii、asserting、async_iter、bstr、cell、char、ffi、io、iter、net、os、panic、panicking、pat、pin、process、random、range、result、sync、unsafe_binder、fmt、hash、slice、str、time、wtf8、unicode、future、task、alloc、view、primitive、arch、simd、from、autodiff、offload、contracts——从原始类型到 future/task 异步原语，一应俱全（但没有堆、没有线程、没有系统调用）。

## 洋葱的第二层：alloc

alloc 在 core 之上引入堆分配。其 src/ 顶层源文件：alloc.rs、borrow.rs、boxed.rs、bstr.rs、fmt.rs、intrinsics.rs、lib.rs、lib.miri.rs、macros.rs、panicking.rs、rc.rs、slice.rs、str.rs、string.rs、sync.rs、task.rs；子目录：boxed/、ffi/、io/、raw_vec/、vec/、wtf8/。

文件名即 API 地图：`boxed.rs`（`Box`）、`rc.rs`（`Rc`）、`sync.rs`（`Arc`）、`string.rs`/`str.rs`（`String`/`str`）、`vec/`（`Vec` 与 raw_vec 分层）、`fmt.rs`（格式化）、`task.rs`（Waker 等异步堆类型）。`bstr.rs` 与 `wtf8/` 是字符串家族的平台特化成员。

## 洋葱的最外层：std 门面

std 的 crate 文档（library/std/src/lib.rs L1-12）自我定位："The Rust Standard Library is the foundation of portable Rust software, a set of minimal and battle-tested shared abstractions for the broader Rust ecosystem."，以及一句使用事实："std is available to all Rust crates by default."

std 的顶层 pub 模块（L459-782）：prelude、rt、f128、f16、f32、f64、thread、ascii、backtrace、bstr、collections、env、error、ffi、fs、hash、io、net、num、os、panic、pat、path、process、random、sync、time、view、simd、autodiff、offload、task、arch、sys、alloc、from；另有私有模块 macros、std_float、panicking、backtrace_rs。与 core 的模块表对照可见继承关系：core 有的抽象在 std 全部可用，std 再叠加 thread/fs/net/process/env 这些"操作系统级"模块——正是 core 宣言中"不提供并发与 I/O"的反面。

std 的 Cargo.toml（`name = "std"`、`version = "0.0.0"`、`edition = "2024"`）还声明了三个 `[[test]]` target：pipe-subprocess、sync、thread_local。

## 平台分发的三层结构

std 内部对平台的处理呈三层：

**第一层 sys**：`library/std/src/sys/mod.rs` 的私有模块 configure_builtins、helpers、pal、personality 与 pub 模块 alloc、args、backtrace、cmath、env、env_consts、exit、fd、fs、io、net 等——这是 std 内部使用的平台抽象词汇表，按功能域（而非按平台）切分。

**第二层 os**：`library/std/src/os/` 下 40 个平台子目录：aix、android、cygwin、darwin、dragonfly、emscripten、espidf、fd、fortanix_sgx、freebsd、fuchsia、haiku、hermit、horizon、hurd、illumos、ios、l4re、linux、macos、motor、net、netbsd、nto、nuttx、openbsd、raw、redox、rtems、solaris、solid、trusty、uefi、unix、vita、vxworks、wasi、wasip2、windows、xous——这是**面向用户的**平台扩展模块（`std::os::unix::*`、`std::os::windows::*` 的家）。unix 目录作为 POSIX 家族的公共层，其上有各 Unix 变体的独立目录。

**第三层是 panic 运行时与启动对象**：`library/panic_unwind/src/` 含 dummy.rs、gcc.rs、lib.rs、miri.rs、seh.rs（GCC 与 SEH 两套展开机制，加 Miri 与 dummy 两个特殊实现）；`library/panic_abort/src/` 含 lib.rs 与 zkvm.rs。`library/rtstartup/` 的 rsbegin.rs 与 rsend.rs 提供运行时启动对象；std 自带 build.rs 完成构建期平台适配。

## 门面下的代表模块：env 与 fs

两个代表模块展示"门面 + sys 分发"的实际形状：

- **env.rs**：`current_dir`(L53)、`set_current_dir`(L80)、`vars`(L135)、`vars_os`(L160)、`var`(L228)、`var_os`(L264)、`split_paths`(L483)、`join_paths`(L578)、`home_dir`(L646)、`temp_dir`(L706)、`current_exe`(L757)；结构体 `Vars`(L90)、`VarsOs`(L100)、`SplitPaths`(L447)、`JoinPathsError`(L511)。
- **fs.rs**：`File`(L135)、`Dir`(L189)、`Metadata`(L202)、`ReadDir`(L220)、`DirEntry`(L239)、`OpenOptions`(L279)、`FileTimes`(L285)、`Permissions`(L298)、`FileType`(L305)、`DirBuilder`(L313)；函数 `read`(L346)、`read_to_string`(L389)、`write`(L427)、`set_times`(L470)、`set_times_nofollow`(L511)。

门面层的 `_os` 后缀变体（`var_os`/`vars_os`）是 Rust 平台抽象的经典设计：同一 API 提供"String 版"（非法 UTF-8 时 panic）与"OsString 版"（不失败）两种语义。

## rt.rs：程序入口

`library/std/src/rt.rs` 是每个 Rust 程序真正的起点：再导出 `crate::panicking::{begin_panic, panic_count}` 与 `core::panicking::{panic_display, panic_fmt}`；定义宏 `rtprintpanic!`(L40)、`rtabort!`(L53)、`rtassert!`(L62)、`rtunwrap!`(L70)；`unsafe fn init(argc: isize, argv: *const *const u8, sigpipe: u8)`(L111) 做运行时初始化；`lang_start`(L199) 与 `lang_start_internal`(L152) 是编译器生成的 main 所跳转的语言项入口。而 pat.rs 是最小门面的标本——全文两行，只做 `pub use core::pattern_type;` 的转发。

## sysroot：聚合 dummy crate

`library/sysroot/Cargo.toml` 自述："this is a dummy crate to ensure that all required crates appear in the sysroot"。它 `name = "sysroot"`、`version = "0.0.0"`、`edition = "2024"`，依赖 proc_macro（public）、profiler_builtins（optional）、std（public）、test（public）；feature `default = ["panic-unwind"]`，其余 feature 均转发给 std。它存在的意义是让构建系统在装配 sysroot 时有单一目标可依赖。

## 构建侧的特殊配置

四个构建配置揭示标准库与普通 crate 的不同：

1. `[profile.release.package.compiler_builtins] codegen-units = 10000`——"place every single intrinsic into its own object file to avoid symbol clashes with the system libgcc"（每个 intrinsic 一个目标文件，避免与系统 libgcc 符号冲突）；
2. `[profile.dist]`（`inherits = "release"`、`codegen-units = 1`、`debug = 1`、rustflags 含 `-Cembed-bitcode=yes`、`-Zunstable-options`、`-Cforce-frame-pointers=non-leaf`）——bootstrap 预构建发行版 libstd 的专用 profile；
3. `[patch.crates-io]` 把 rustc-std-workspace-core/alloc/std 与 windows-sys 指向本地路径——构建 sysroot 时劫持同名 crates.io 依赖；
4. panic_abort 在 dev 与 release 两个 profile 下都强制 `rustflags = ["-Cpanic=abort"]`——"panic_abort must always be compiled with panic=abort, even when the rest of the sysroot is panic=unwind"。

另外，core/alloc/std 三库的 src/ 各含一个 `lib.miri.rs`——供 Miri 解释器直接解释执行标准库的版本。

## 相关概念

- [简介与仓库导航](/concepts/00-intro-repo-navigation.md) — library workspace 在仓库三层地图中的位置
- [rustdoc 与工具链](/concepts/10-rustdoc-toolchain.md) — std 文档由 rustdoc-js-std 等套件守护
- [std 模块结构剖析](/examples/std-module-anatomy.md) — 沿本篇架构做逐模块走读
- [标准库信源登记](/references/std-source-map.md) — 全部 23 目录与关键文件坐标
