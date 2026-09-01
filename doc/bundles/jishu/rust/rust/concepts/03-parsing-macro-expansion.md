---
type: Concept
title: 解析与宏展开：从字节流到 AST
description: rustc_lexer 的纯手工 tokenize、rustc_parse 的递归下降解析器、rustc_expand 与 rustc_builtin_macros 的声明宏与内建宏展开体系
tags: [rust, rustc, parser, macro]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-28T10:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T10:00:00+08:00" }
status: stable
stale_after: 2027-08-28
sources:
  - id: rustc-source
    resource: /references/rustc-source-map.md
---

# 解析与宏展开：从字节流到 AST

## 两层分界：lexer 与 parser

编译器前端的字符→token→AST 转换分属两个 crate：

- **rustc_lexer**：把字节流转成 token 流，不依赖任何语法知识；
- **rustc_parse**：把 token 流组装成 AST，是递归下降解析器的大本营。

### rustc_lexer：无依赖的 tokenize 层

rustc_lexer/src/lib.rs 的顶层项勾勒出这一层的全部职责：`pub struct Token`(L59)、`pub enum TokenKind`(L72)、`pub enum DocStyle`(L209)、`pub enum LiteralKind`(L221)、`pub struct GuardedStr`(L251)、`pub enum RawStrError`(L258)、`pub enum Base`(L271)、`pub fn strip_shebang`(L284)、`pub fn validate_raw_str`(L311)、`pub fn tokenize`(L327)、`pub fn is_whitespace`(L341)、`pub fn is_id_start`(L387)、`pub fn is_id_continue`(L395)、`pub fn is_ident`(L400)、`pub enum FrontmatterAllowed`(L409)、`pub struct Cursor<'a>`(L418)。

几个细节值得驻足：`strip_shebang` 说明源文件开头的 `#!` 由 lexer 显式剥除；`LiteralKind` 与 `Base` 把整数字面量的进制识别前置到 token 层；`RawStrError` 与 `validate_raw_str`、`GuardedStr` 表明原始字符串字面量（`r"..."`、`r#"..."`）的哈希围栏配对检查在词法层完成；`FrontmatterAllowed` 则是 frontmatter（YAML 头）这类新语法的解析开关。

### rustc_parse：解析器家族

rustc_parse/src/lib.rs 暴露统一的入口族：`pub mod parser`(L30)、`pub mod lexer`(L35)、`pub fn new_parser_from_source_str`(L94)、`pub fn new_parser_from_file`(L111)、`pub fn source_str_to_stream`(L243)、`pub fn parse_in`(L277)、`pub fn fake_token_stream_for_item`(L291)、`pub fn fake_token_stream_for_crate`(L371)。

解析器按语法类别拆成九个子模块：asm、attr、expr、item、pat、path、stmt、ty、tests——分别对应内联汇编、属性、表达式、项、模式、路径、语句、类型的解析以及测试。`fake_token_stream_for_item`/`fake_token_stream_for_crate` 这对入口的名字暗示了一个事实：解析器还会为已经抽象语法化的项**反向伪造** token 流，供宏展开重新消费。

## AST：语法世界的四种 Kind

rustc_ast/src/lib.rs 声明模块 util、ast、ast_traits、attr、entry、expand、format、mut_visit、node_id、token、tokenstream、visit，并通过 `pub use self::ast::*` 将 ast 模块整体再导出。核心枚举全部在 ast.rs：

| 枚举 | 行号 | 覆盖 |
|------|------|------|
| `Crate` | L550 | 整个 crate 的根结构 |
| `PatKind` | L871 | 模式 |
| `ExprKind` | L1742 | 表达式 |
| `TyKind` | L2518 | 类型（四个同名 TyKind 中偏语法的那一个） |
| `ItemKind` | L4126 | 项 |

注意这里的 `TyKind` 只是**语法层**的类型表示——写在源码里的类型长什么样。它与其他三处同名定义的关系见 [HIR 与 AST Lowering](/concepts/04-hir-ast-lowering.md) 与 [类型系统](/concepts/05-type-system-trait-solving.md)。

## 宏展开：一个 query provider

宏展开住在 rustc_expand。其 src/lib.rs 的模块分为两组：pub 的 base、config、expand、module、proc_macro；私有的 build、diagnostics、mbe、placeholders、proc_macro_server、stats。与编译器其余部分一致，它通过

```rust
pub fn provide(providers: &mut rustc_middle::query::Providers)  // rustc_expand/src/lib.rs:27
```

把自己的 query 实现挂进系统（这正是 [流水线总览](/concepts/02-compiler-pipeline-overview.md) 所述 query 心智模型的实例）。

**ExtCtxt**（`pub struct ExtCtxt<'a>`，rustc_expand/src/base.rs:1189）是宏展开上下文——声明宏与过程宏在展开期间看到的"世界"。macro-by-example（`macro_rules!`）的规则解析位于 `rustc_expand/src/mbe/quoted.rs`。

## 内建宏：编译器自带的宏家族

rustc_builtin_macros 实现编译器自带的宏。其 src/lib.rs 的私有模块清单（前 20 个）展示了这个家族的规模与疆域：alloc_error_handler、assert、autodiff、cfg、cfg_accessible、cfg_eval、cfg_select、compile_error、concat、concat_bytes、define_opaque、derive、deriving、diagnostics、direct_const_arg、edition_panic、eii、env、format、format_foreign。

几个例子帮助定位：`cfg`/`cfg_eval`/`cfg_accessible`/`cfg_select` 处理条件编译的求值；`derive`/`deriving` 是 derive 宏的编译器侧入口；`format`/`format_foreign` 支撑 `format!` 家族；`edition_panic` 说明连 `panic!` 的语义都随 edition（版本）切换；`env` 对应 `env!`/`option_env!`；`assert`、`compile_error!`、`concat!`、`concat_bytes!` 皆是日常宏。procedural macro 的运行时支持则由 rustc_proc_macro crate 承接。

## 与流水线的衔接

在 [rustc_interface 的 passes.rs 骨架](/concepts/02-compiler-pipeline-overview.md) 中，`parse`(L54) 与 `configure_and_expand`(L134) 对应本篇的两个世界：前者把源码交给 rustc_parse 得到初始 Crate，后者在配置（crate 级 cfg、feature）就绪后驱动 rustc_expand 反复展开直到定点——因为宏可以产生新的宏调用，展开是一个迭代收敛过程。展开完成的 AST 随后交给 AST lowering 进入 HIR。

## 相关概念

- [编译器流水线总览](/concepts/02-compiler-pipeline-overview.md) — parse 与 configure_and_expand 在驱动骨架中的位置
- [HIR 与 AST Lowering](/concepts/04-hir-ast-lowering.md) — 展开后的 AST 如何降级为 HIR
- [rustc 基础设施](/concepts/09-rustc-infrastructure.md) — rustc_expand 的 provide() 所挂入的 query 系统
- [rustc 编译器信源登记](/references/rustc-source-map.md) — 本篇各 crate 的关键坐标速查
