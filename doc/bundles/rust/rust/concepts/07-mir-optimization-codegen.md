---
type: Concept
title: MIR 优化与代码生成：pass 流与三大后端
description: rustc_mir_transform 的四组 pass 编排与代表 pass，rustc_codegen_ssa 的后端 trait 契约，以及 LLVM/Cranelift/GCC 三大代码生成后端
tags: [rust, rustc, mir, codegen]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-28T10:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T10:00:00+08:00" }
status: stable
stale_after: 2027-08-28
sources:
  - id: rustc-source
    resource: /references/rustc-source-map.md
---

# MIR 优化与代码生成：pass 流与三大后端

## rustc_mir_transform：query provider 与 pass 编排

rustc_mir_transform/src/lib.rs 继续遵循 `pub fn provide`(L214) 模式，其注册的 query provider 函数一览：

| 函数 | 行号 | 产出 |
|------|------|------|
| `mir_keys` | L327 | 需要 MIR 的定义集合 |
| `mir_const_qualif` | L360 | 常量限定符（const 求值前置） |
| `mir_built` | L391 | 刚构建的 MIR |
| `mir_promoted` | L432 | 提升（promote）后的 MIR |
| `mir_for_ctfe` | L492 | CTFE（编译期函数求值）专用 MIR |
| `mir_drops_elaborated_and_const_checked` | L537 | drop 展开 + 常量检查后的 MIR |

**pass 编排**由四组函数承接，构成一条从分析态到运行态的流水带：

- `pub fn run_analysis_to_runtime_passes`(L597) —— 从分析态 MIR 走向运行态；
- `run_analysis_cleanup_passes`(L631) —— 分析态清理；
- `run_runtime_lowering_passes`(L644) —— 运行态下降（如展开 drop）；
- `run_runtime_cleanup_passes`(L671) —— 运行态清理。

pass 模块的目录清单里有几个名字直接对应经典优化：`gvn.rs`（全局值编号）、`inline.rs`（内联）、`sroa.rs`（标量替换聚合体）——这三个正是 MIR 层最重要的优化代表。清单还包括：pass_manager、check_pointers、cost_checker、cross_crate_inline、deduce_param_attrs、elaborate_drop、ffi_unwind_calls、lint、lint_tail_expr_drop_order、liveness、patch、shim、ssa、trivial_const。`pass_manager` 是 pass 调度的中枢；`elaborate_drop` 与 `ffi_unwind_calls` 表明展开（lowering）类 pass 与优化类 pass 混居在同一条流水带里。

## rustc_monomorphize：单态化

泛型代码要变成机器码，先要单态化（为每个具体类型实例化一份代码）。rustc_monomorphize/src/lib.rs 的模块：collector、diagnostics、graph_checks、mono_checks、offload、partitioning、util；关键函数 `pub fn provide`(L54) 与 `fn custom_coerce_unsize_info`(L27)。`collector` 收集需要代码生成的 monomorphized item，`partitioning` 决定代码分到哪些编译单元——这直接影响链接时间与优化效果。

## rustc_codegen_ssa：后端无关的代码生成骨架

代码生成的架构核心是一个 trait 契约族。rustc_codegen_ssa/src/traits/backend.rs 定义：

- `pub trait BackendTypes`(L21) —— 后端类型词汇表；
- `pub trait CodegenBackend`(L37) —— 后端总入口契约；
- `pub trait ExtraBackendMethods`(L164) —— 后端扩展方法。

traits/ 目录共定义约 20 个后端需实现的 trait，含 AbiBuilderMethods、AsmBuilderMethods、AsmCodegenMethods、BuilderMethods、ConstCodegenMethods、CoverageInfoBuilderMethods、DebugInfoCodegenMethods、DebugInfoBuilderMethods、IntrinsicCallBuilderMethods、MiscCodegenMethods、ModuleBufferMethods、PreDefineCodegenMethods、StaticCodegenMethods、StaticBuilderMethods、WriteBackendMethods。**任何想成为 rustc 后端的实现，都要填满这张契约表。**

rustc_codegen_ssa/src/lib.rs 同时定义了骨架层的数据结构：`ModuleCodegen<M>`(L58)、`CompiledModule`(L123)、`NativeLib`(L215)、`SymbolExport`(L237)；其 pub 模块覆盖 assert_module_sources、back、base、codegen_attrs、common、debuginfo、diagnostics、meth、mir、mono_item、size_of_val、target_features、traits。

## 三大后端

| 后端 | crate | 形态 | 说明 |
|------|-------|------|------|
| LLVM（默认） | rustc_codegen_llvm | — | 模块清单含 abi、allocator、asm、attributes、back、base、builder、callee、common、consts、context、coverageinfo、debuginfo、declare、diagnostics、intrinsic、llvm、llvm_util、macros、mono_item 等 |
| Cranelift | rustc_codegen_cranelift | `crate-type = ["dylib"]`，version = "0.1.0"，edition = "2024"；依赖 cranelift-codegen/frontend/module/native/jit/object 均 0.134.0 | 快速编译的备选后端；**被根 workspace exclude**（自带独立构建域） |
| GCC | rustc_codegen_gcc | `crate-type = ["dylib"]`，version = "0.1.0"；依赖 `gccjit = { version = "3.3.0", features = ["dlopen"] }`；features `master = ["gccjit/master"]`、`default = ["master"]` | 借助 libgccjit 的后端；同样被根 workspace exclude |

两个备选后端都被根 workspace 显式 exclude（见[仓库导航](/concepts/00-intro-repo-navigation.md)），以独立方式构建——这是"79 crate 联邦"之外的两块飞地。

## 端到端链条

```text
MIR（借用检查通过后）
   │  rustc_mir_transform（四组 pass：优化与展开）
   │  rustc_monomorphize（单态化收集与分区）
   ▼
rustc_codegen_ssa（后端无关骨架）
   │  CodegenBackend trait
   ├── rustc_codegen_llvm（默认后端）
   ├── rustc_codegen_cranelift（备选，独立构建域）
   └── rustc_codegen_gcc（备选，独立构建域）
   ▼
目标代码 + 链接（rustc_interface/src/queries.rs 的 Linker/codegen_and_build_linker/link）
```

回看[流水线总览](/concepts/02-compiler-pipeline-overview.md)中 queries.rs 的 `codegen_and_build_linker` 与 `link`：代码生成与链接正是从 MIR 优化结束后接管的最后两棒。

## 相关概念

- [MIR 与借用检查](/concepts/06-mir-borrow-checking.md) — 优化 pass 的输入：MIR 数据结构与借用检查
- [编译器流水线总览](/concepts/02-compiler-pipeline-overview.md) — 代码生成在驱动骨架中的终点位置
- [rustdoc 与工具链](/concepts/10-rustdoc-toolchain.md) — Miri：直接解释执行 MIR 的另一条路
- [rustc 编译器信源登记](/references/rustc-source-map.md) — 后端与 monomorphize 的关键坐标速查
