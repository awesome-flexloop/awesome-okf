---
type: Reference
title: rustc 编译器信源登记
description: rust-lang/rust 编译器域的基线版本、构建域划分、79 个 crate 清单、流水线各 crate 关键文件与行号坐标、tests 测试套件索引
tags: [rust, rustc, source, reference, compiler]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-28T10:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T10:00:00+08:00" }
status: stable
stale_after: 2027-08-28
sources:
  - id: rust-repo
    resource: external/libs/rust-lang/rust
    title: rust-lang/rust 源码仓库（main @ e457a7b0）
---

# rustc 编译器信源登记

## 基本信息

| 属性 | 值 |
|------|-----|
| 项目名 | rust-lang/rust |
| 基线 | main @ e457a7b0d326d67b4322ef0d11bd715cfaeda48f（2026-08-27 采集） |
| 版本 | **1.100.0**（记录于 `src/version` 单行文件，而非任何 Cargo.toml） |
| 定位 | Rust 语言主源码仓库：包含编译器、标准库与文档 |
| 许可证 | MIT 与 Apache License 2.0 双许可为主体，部分内容由多种 BSD 类许可覆盖 |
| 商标 | Rust 与 Cargo 商标及徽标归 Rust Foundation 所有并受保护 |
| 源码仓库 | <https://github.com/rust-lang/rust> |

## 源码位置

本知识包所有编译器域坐标均相对以下根路径：

```
external/libs/rust-lang/rust/
```

> 仓库根存在 `AGENTS.md`，内容为 LLM 使用政策与编辑门槛规则（外部仓库路由、禁止文本、reviewer 门槛、soundness 分类等），并声明 `x.py` 是本仓库的构建工具（调用方式为 `./x`）。

## 构建域划分

编译器域隶属仓库根 Cargo workspace（`resolver = "2"`）。该 workspace 的成员包括 `compiler/rustc`（rustc 二进制壳）、`src/build_helper`、三个 `src/rustc-std-workspace/*` crate、`src/rustdoc-json-types`、`src/shim_utils` 以及 38 个 `src/tools/*` 成员条目（含 clippy、compiletest、miri、rustfmt、tidy、x 等）。

根 workspace 显式 **exclude** 了以下 6 个路径，它们不属于任何根 workspace 构建域：

- `build`
- `compiler/rustc_codegen_cranelift`
- `compiler/rustc_codegen_gcc`
- `src/bootstrap`
- `tests/rustdoc-gui`
- `obj`

另有根 Cargo.toml 中的特殊 profile 约定：`lld-wrapper` 与 `wasm-component-ld-wrapper` 两个包在 release profile 下均设 `debug = 0`、`strip = true`（注释称二者是"围绕执行 lld 的极薄包装"）；测试专用 crate `test-float-parse` 在 dev 与 release 两个 profile 下均设 `opt-level = 3`（注释"Bigint libraries are slow without optimization"）。

## compiler/ 目录：79 个子目录清单

`compiler/` 含 79 个子目录 = `rustc` 二进制壳 + 78 个 `rustc_*` crate。以下按流水线职能分组（分组仅为导航便利，清单本身与目录一一对应）：

### 入口与驱动（4）

| crate | 职能 |
|------|------|
| rustc | 二进制壳（Cargo.toml 中 name = "rustc-main"，src/main.rs 为 rustc 二进制入口） |
| rustc_driver | 稳定 dylib 壳（crate-type = ["dylib"]，唯一依赖 rustc_driver_impl） |
| rustc_driver_impl | 编译器驱动实现（crate 文档首行 "The Rust compiler."） |
| rustc_interface | 编译器接口层（Config、run_compiler、passes、queries） |

### 解析、词法与宏（11）

rustc_parse、rustc_parse_format、rustc_lexer、rustc_ast、rustc_ast_ir、rustc_ast_passes、rustc_ast_pretty、rustc_ast_lowering、rustc_expand、rustc_builtin_macros、rustc_proc_macro

### HIR 域（5）

rustc_hir、rustc_hir_id、rustc_hir_pretty、rustc_hir_analysis、rustc_hir_typeck

### 类型系统（10）

rustc_middle、rustc_type_ir、rustc_type_ir_macros、rustc_infer、rustc_trait_selection、rustc_traits、rustc_next_trait_solver、rustc_ty_utils、rustc_ty_walk、rustc_transmute

### MIR 与借用检查（5）

rustc_mir_build、rustc_mir_transform、rustc_mir_dataflow、rustc_borrowck、rustc_pattern_analysis

### 代码生成（7）

rustc_codegen_ssa、rustc_codegen_llvm、rustc_codegen_cranelift、rustc_codegen_gcc、rustc_monomorphize、rustc_symbol_mangling、rustc_llvm

### 基础设施与支撑（37）

rustc_span、rustc_errors、rustc_error_codes、rustc_error_messages、rustc_query_impl、rustc_metadata、rustc_crate_store、rustc_resolve、rustc_data_structures、rustc_arena、rustc_index、rustc_index_macros、rustc_macros、rustc_serialize、rustc_session、rustc_hashes、rustc_graphviz、rustc_log、rustc_fs_util、rustc_structures、rustc_feature、rustc_attr_ir、rustc_attr_parsing、rustc_target、rustc_abi、rustc_lint、rustc_lint_defs、rustc_passes、rustc_privacy、rustc_const_eval、rustc_incremental、rustc_public、rustc_public_bridge、rustc_sanitizers、rustc_thread_pool、rustc_baked_icu_data、rustc_windows_rc

> 其中 `rustc` 壳的 Cargo.toml 依赖 rustc_driver、rustc_driver_impl、rustc_public、rustc_public_bridge、rustc_codegen_ssa；后两者的注释说明它们需要进入 sysroot，供稳定 MIR 消费者与代码生成后端使用。

## 关键坐标速查

### 入口链

| 坐标 | 符号 |
|------|------|
| rustc_driver_impl/src/lib.rs:173 | `pub fn run_compiler(at_args: &[String], callbacks: &mut (dyn Callbacks + Send))`（文档注释"This is the primary entry point for rustc."） |
| rustc_interface/src/interface.rs:318 | `pub struct Config`（字段含 opts、crate_cfg、input、output_dir、lint_caps、register_lints、make_codegen_backend 等） |
| rustc_interface/src/interface.rs:378 | `pub fn run_compiler<R: Send>(config: Config, f: impl FnOnce(&Compiler) -> R + Send) -> R` |
| rustc_interface/src/passes.rs | `parse`(L54)、`configure_and_expand`(L134)、`write_dep_info`(L828)、`write_interface`(L878)、`create_and_enter_global_ctxt`(L936)、`emit_delayed_lints`(L1077)、`run_required_analyses`(L1094)、`analysis`(L1201)、`get_crate_name`(L1357) |
| rustc_interface/src/queries.rs | `pub struct Linker`(L18)、`codegen_and_build_linker`(L29)、`link`(L49) |
| rustc_session/src/session.rs:328 | `pub struct Session`（字段含 target、host、opts、target_tlib_path） |
| rustc_session/src/config.rs:2686 | `build_session_options`；session.rs:1257 `build_session` |

### 解析与宏展开

| 坐标 | 符号 |
|------|------|
| rustc_parse/src/lib.rs | `new_parser_from_source_str`(L94)、`new_parser_from_file`(L111)、`source_str_to_stream`(L243)、`parse_in`(L277)、`fake_token_stream_for_item`(L291)、`fake_token_stream_for_crate`(L371)；parser/ 子模块：asm、attr、expr、item、pat、path、stmt、ty、tests |
| rustc_lexer/src/lib.rs | `Token`(L59)、`TokenKind`(L72)、`DocStyle`(L209)、`LiteralKind`(L221)、`GuardedStr`(L251)、`RawStrError`(L258)、`Base`(L271)、`strip_shebang`(L284)、`validate_raw_str`(L311)、`tokenize`(L327)、`Cursor`(L418) |
| rustc_expand/src/lib.rs | `pub fn provide(providers: &mut rustc_middle::query::Providers)`(L27)；模块：base、config、expand、module、proc_macro、mbe/quoted.rs |
| rustc_expand/src/base.rs:1189 | `pub struct ExtCtxt<'a>`（宏展开上下文） |
| rustc_ast/src/ast.rs | `Crate`(L550)、`PatKind`(L871)、`ExprKind`(L1742)、`TyKind`(L2518)、`ItemKind`(L4126) |
| rustc_builtin_macros/src/lib.rs | 前 20 个私有模块：alloc_error_handler、assert、autodiff、cfg、cfg_accessible、cfg_eval、cfg_select、compile_error、concat、concat_bytes、define_opaque、derive、deriving、diagnostics、direct_const_arg、edition_panic、eii、env、format、format_foreign |

### HIR 域

| 坐标 | 符号 |
|------|------|
| rustc_hir/src/hir.rs:3562 | `pub enum TyKind<'hir, Unambig = ()>` |
| rustc_ast_lowering/src/lib.rs | `provide`(L99)、`LoweringContext`(L147)、`SpanLowerer`(L307)、`index_ast`(L498)、`lower_to_hir`(L659) |
| rustc_hir_analysis/src/lib.rs | `provide`(L129)、`check_crate`(L148)、`lower_ty`(L242)、`lower_const_arg_for_rustdoc`(L254)；rustc_hir_analysis/README.md 仅两行，指向 rustc-dev-guide 的 hir typeck 章节 |
| rustc_hir_typeck/src/lib.rs | 子模块（前 20）：_match、autoderef、callee、cast、check、closure、coercion、demand、diagnostics、diverges、expectation、expr、inline_asm、expr_use_visitor、fallback、fn_ctxt、gather_locals、intrinsicck、loops、method |

### 类型系统

| 坐标 | 符号 |
|------|------|
| rustc_middle/src/ty/context.rs | `CtxtInterners`(L134)、`CommonTypes`(L304)、`CommonLifetimes`(L379)、`CommonConsts`(L400)、`TyCtxtFeed`(L571)、`GlobalCaches`(L663)、`TyCtxt`(L710)、`GlobalCtxt`(L733)、`CurrentGcx`(L815) |
| rustc_type_ir/src/ty_kind.rs:147 | `pub enum TyKind<I: Interner>`（编译器中共 4 处同名 TyKind 之一） |
| rustc_infer/src/infer/mod.rs | `InferCtxtInner`(L97)、`InferCtxt`(L246)、`InferCtxtBuilder`(L588) |
| rustc_trait_selection/src/lib.rs | pub 模块：diagnostics、error_reporting、infer、opaque_types、regions、solve、traits |
| rustc_next_trait_solver/src/lib.rs | pub 模块：canonical、coherence、delegate、normalize、placeholder、solve |

### MIR 与借用检查

| 坐标 | 符号 |
|------|------|
| rustc_middle/src/mir/mod.rs | `Body`(L206)、`Local`(L866)、`LocalKind`(L889)、`LocalDecl`(L967)、`LocalInfo`(L1074)、`BasicBlock`(L1300)、`BasicBlockData`(L1319) |
| rustc_middle/src/thir.rs:63 | `pub struct Thir<'tcx>`（THIR 数据结构在 rustc_middle 而非 rustc_mir_build） |
| rustc_borrowck/src/lib.rs | `provide`(L110)、`mir_borrowck`(L117)；模块含 nll、polonius、region_infer、universal_regions、type_check 等 |
| rustc_mir_build/src/lib.rs | `provide`(L19)；模块：builder、check_tail_calls、check_unsafety、diagnostics、thir |
| rustc_mir_transform/src/lib.rs | `provide`(L214)、`mir_keys`(L327)、`mir_const_qualif`(L360)、`mir_built`(L391)、`mir_promoted`(L432)、`mir_for_ctfe`(L492)、`mir_drops_elaborated_and_const_checked`(L537)、`run_analysis_to_runtime_passes`(L597)、`run_analysis_cleanup_passes`(L631)、`run_runtime_lowering_passes`(L644)、`run_runtime_cleanup_passes`(L671) |
| rustc_mir_dataflow/src/lib.rs | `MoveDataTypingEnv`(L36)；pub 模块：debuginfo、impls、move_paths、points、rustc_peek、value_analysis |

### 代码生成

| 坐标 | 符号 |
|------|------|
| rustc_codegen_ssa/src/traits/backend.rs | `CodegenBackend`(L37)、`BackendTypes`(L21)、`ExtraBackendMethods`(L164) |
| rustc_codegen_ssa/src/lib.rs | `ModuleCodegen<M>`(L58)、`CompiledModule`(L123)、`NativeLib`(L215)、`SymbolExport`(L237) |
| rustc_codegen_cranelift/Cargo.toml | name = "rustc_codegen_cranelift"、version = "0.1.0"、edition = "2024"、crate-type = ["dylib"]；依赖 cranelift-codegen/frontend/module/native/jit/object 均 0.134.0 |
| rustc_codegen_gcc/Cargo.toml | name = "rustc_codegen_gcc"、version = "0.1.0"、crate-type = ["dylib"]；依赖 gccjit 3.3.0（features = ["dlopen"]） |
| rustc_monomorphize/src/lib.rs | `provide`(L54)、`custom_coerce_unsize_info`(L27)；模块：collector、partitioning、graph_checks、mono_checks、offload、util |

### 基础设施

| 坐标 | 符号 |
|------|------|
| rustc_span/src/span_encoding.rs:82 | `pub struct Span` |
| rustc_span/src/symbol.rs:2674 | `pub struct Symbol(SymbolIndex)`；文件引用 `PREDEFINED_SYMBOLS_COUNT`(L3054) |
| rustc_errors/src/lib.rs | `CodeSuggestion`(L157)、`Substitution`(L193)、`ExplicitBug`(L263)、`DelayedBugPanic`(L267)、`DiagCtxt`(L272)、`DiagCtxtHandle`(L277)、`DiagCtxtFlags`(L415) |
| rustc_middle/src/queries.rs:141 | `rustc_queries! {` 宏调用（全仓库唯一一处） |
| rustc_query_impl/src/lib.rs | `query_system`(L29)、`provide`(L50)；私有模块：dep_kind_vtables、diagnostics、execution、handle_cycle_error、incremental、job、query_vtables、self_profile |
| rustc_metadata/src/rmeta/mod.rs | `METADATA_VERSION: u8 = 10`(L63)、`METADATA_HEADER`(L70) |
| rustc_resolve/src/lib.rs | `ModuleData`(L678)、`Module`(L718)、`LocalModule`(L723)、`ExternModule`(L728) |

## 测试套件索引

`tests/` 顶层含 22 个子目录：

| 套件 | 关注点 |
|------|--------|
| ui / ui-fulldeps | 编译器行为与错误信息测试（后者含依赖编译器的测试） |
| rustdoc-ui、rustdoc-html、rustdoc-json、rustdoc-js、rustdoc-js-std、rustdoc-gui | rustdoc 六套件（界面、HTML 输出、JSON 输出、JS 断言、std 文档 JS、GUI） |
| run-make / run-make-cargo | 端到端构建场景测试 |
| mir-opt | MIR 优化 pass 效果测试 |
| incremental | 增量编译测试 |
| debuginfo | 调试信息测试 |
| assembly-llvm、codegen-llvm、codegen-units | 汇编与 LLVM 代码生成测试 |
| coverage、coverage-run-rustdoc | 覆盖率测试 |
| crashes | 崩溃回归测试 |
| pretty、build-std、auxiliary | pretty-printing、标准库构建、辅助目录 |

测试执行器为 `src/tools/compiletest`（含 src/runtest/、directives.rs、executor.rs 等），它是根 workspace members 之一。

## 与标准库域的分界

编译器域（`compiler/` + 根 workspace）与标准库域（`library/` 独立 workspace）的分界、标准库信源坐标见 [标准库信源登记](/references/std-source-map.md)。仓库整体导航见 [简介与仓库导航](/concepts/00-intro-repo-navigation.md)。
