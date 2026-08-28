---
type: Concept
title: 编译器流水线总览：入口链与 query 心智模型
description: 从 rustc 二进制壳到 rustc_driver_impl 的入口链、rustc_interface 的 passes.rs 函数骨架，以及为什么 rustc 本质是 query 驱动的按需求值系统
tags: [rust, rustc, pipeline, query]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-28T10:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T10:00:00+08:00" }
status: stable
stale_after: 2027-08-28
sources:
  - id: rustc-source
    resource: /references/rustc-source-map.md
---

# 编译器流水线总览：入口链与 query 心智模型

## 入口链：从二进制壳到驱动实现

`compiler/rustc` 是一个极薄的二进制壳：其 Cargo.toml 中 `name = "rustc-main"`，src/main.rs 是 rustc 二进制入口。真正的逻辑在链条下游：

```
rustc（壳，rustc-main）
  └─ rustc_driver（crate-type = ["dylib"]，唯一依赖 rustc_driver_impl）
       └─ rustc_driver_impl（crate 文档首行："The Rust compiler."）
            └─ rustc_interface / rustc_session / …
```

分层动机写在依赖里：rustc_driver 以 dylib 形式暴露稳定壳，同时通过 build-dependencies 引入 rustc_windows_rc；rustc 壳的 Cargo.toml 还依赖 rustc_public、rustc_public_bridge、rustc_codegen_ssa——后两者的注释说明它们需要进入 sysroot，供稳定 MIR 消费者与代码生成后端使用。rustc_driver_impl 的 crate 文档直言 "This API is completely unstable and subject to change."

编译器驱动的总入口是：

```rust
pub fn run_compiler(at_args: &[String], callbacks: &mut (dyn Callbacks + Send))
```

位于 rustc_driver_impl/src/lib.rs:173，文档注释为 "This is the primary entry point for rustc."。rustc_driver_impl 的 feature 开关也透露了驱动的可选能力：check_only、jemalloc、llvm、llvm_offload、max_level_info、rustc_randomized_layouts。

## rustc_interface：编译会话的组装层

rustc_interface 是驱动与编译器内部世界之间的接口层。其 src/lib.rs 声明模块 callbacks、diagnostics、interface、limits、passes、queries、util，并再导出 `interface::{Config, run_compiler}`、`passes::{DEFAULT_QUERY_PROVIDERS, create_and_enter_global_ctxt, parse}`、`queries::Linker`。

`pub struct Config`（interface.rs:318）承载一次编译的全部输入，字段包括：opts（config::Options）、crate_cfg、crate_check_cfg、input、output_dir、output_file、ice_file、file_loader、lint_caps、psess_created、track_state、register_lints、override_queries、extra_symbols、make_codegen_backend、using_internal_features。

驱动主循环则由 `pub fn run_compiler<R: Send>(config: Config, f: impl FnOnce(&Compiler) -> R + Send) -> R`（interface.rs:378）承接，函数体先调用 `rustc_data_structures::sync::set_dyn_thread_safe_mode` 与 `jobserver::initialize`——线程安全模式与 jobserver 参与是每个编译会话的起点动作。

会话状态本身是 `pub struct Session`（rustc_session/src/session.rs:328），字段含 `target: Target`、`host: Target`、`opts: config::Options`、`target_tlib_path: SearchPath`。构造入口有两个：`build_session_options`（config.rs:2686，从 getopts::Matches 解析 Options）与 `build_session`（session.rs:1257）。

## passes.rs：看似流水线的函数骨架

rustc_interface/src/passes.rs 的顶层函数像一张流水线地图：

| 函数 | 行号 | 职能（按名称） |
|------|------|------|
| `parse` | L54 | 解析源码 |
| `configure_and_expand` | L134 | 配置与宏展开 |
| `write_dep_info` | L828 | 写依赖信息 |
| `write_interface` | L878 | 写接口（增量缓存相关） |
| `create_and_enter_global_ctxt` | L936 | 创建并进入全局上下文 |
| `emit_delayed_lints` | L1077 | 发射延迟 lint |
| `run_required_analyses` | L1094 | 运行必需分析 |
| `analysis` | L1201 | 分析主阶段 |
| `get_crate_name` | L1357 | 取 crate 名 |

链接侧的对应物在 rustc_interface/src/queries.rs：`pub struct Linker`(L18)、`pub fn codegen_and_build_linker`(L29)、`pub fn link`(L49)。

**但这只是驱动 query 图的骨架，不是顺序执行的真相。** 来自 gcc 的"前端→优化→后端"直觉在这里会系统性失效：真正的执行模型是 `TyCtxt` 按需触发 query（查询），函数序列只是确保依赖发生的编排点。

## query 心智模型（总览）

rustc 是 query 驱动的**懒求值**（lazy evaluation）系统：

- 所有 query 集中定义于 `rustc_middle/src/queries.rs:141` 的**全仓库唯一一处** `rustc_queries!` 宏调用；其上方注释说明每个 query 对应 `Providers` 结构的一个函数指针字段与 `tcx: TyCtxt` 上的方法。
- 各阶段 crate（rustc_expand、rustc_hir_analysis、rustc_mir_transform、rustc_borrowck 等）通过 `pub fn provide(providers: &mut Providers)` 把实现挂进系统。
- 缓存策略逐 query 声明，如 `derive_macro_expansion` 用 cache_on_disk、`env_var_os` 用 eval_always（每次求值，"get the value of an environment variable"）、`resolver_for_lowering_raw` 用 eval_always + no_hash。
- 系统内建循环检测、增量缓存与自我剖析：rustc_query_impl crate 含 job、cycle、incremental、self_profile 等模块；rustc_middle/src/query/ 的 job.rs 定义 `QueryJobId`、`QueryJob`、`QueryState`、`QueryStackFrame`、`QueryCycle`。

query 体系的完整剖析（宏体结构、缓存实现、循环检测细节）见 [rustc 基础设施](/concepts/09-rustc-infrastructure.md)。本篇只需立住一个观念：**阅读任何流水线阶段 crate，都先问"它注册了哪些 query"**——把 `rustc_middle/src/queries.rs` 的宏体当作编译器能力总清单来读。这一模式也解释了为什么后续每一篇阶段文档（解析、HIR、类型检查、MIR、代码生成）都会出现同构的 `provide()` 函数。

## 三层数据表示预告

流水线各阶段之间的数据表示切换是 rustc 源码阅读的第二张地图：

1. **AST**（rustc_ast）——语法表示，来自解析与宏展开（[解析与宏展开](/concepts/03-parsing-macro-expansion.md)）；
2. **HIR**（rustc_hir）——面向编译器的 IR，由 AST lowering 产出（[HIR 与 AST Lowering](/concepts/04-hir-ast-lowering.md)）；
3. **THIR/MIR**（rustc_middle）——类型检查后的求值与优化域（[类型系统](/concepts/05-type-system-trait-solving.md)、[MIR 与借用检查](/concepts/06-mir-borrow-checking.md)）。

代码生成则由三大后端承接（[MIR 优化与代码生成](/concepts/07-mir-optimization-codegen.md)）。

## 相关概念

- [简介与仓库导航](/concepts/00-intro-repo-navigation.md) — 入口链各 crate 在 70-crate 联邦中的位置
- [解析与宏展开](/concepts/03-parsing-macro-expansion.md) — passes.rs 中 parse 与 configure_and_expand 的内部世界
- [rustc 基础设施](/concepts/09-rustc-infrastructure.md) — query 系统、增量缓存与循环检测的完整机制
- [rustc 编译器信源登记](/references/rustc-source-map.md) — 入口链各 crate 的关键文件与行号坐标
