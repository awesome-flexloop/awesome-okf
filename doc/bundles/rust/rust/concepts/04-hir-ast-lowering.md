---
type: Concept
title: HIR 与 AST Lowering：面向编译器的第二个 AST
description: rustc_ast_lowering 如何把语法 AST 降级为面向编译器的 HIR，rustc_hir_analysis 与 rustc_hir_typeck 如何在其上完成类型检查
tags: [rust, rustc, hir, lowering]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-28T10:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T10:00:00+08:00" }
status: stable
stale_after: 2027-08-28
sources:
  - id: rustc-source
    resource: /references/rustc-source-map.md
---

# HIR 与 AST Lowering：面向编译器的第二个 AST

## 为什么要有第二个 AST

AST（抽象语法树）服务两个主人：**人写下的语法**与**编译器要分析的语义**。rustc 用两份表示分别伺候：rustc_ast 保留语法原貌（供宏、pretty-print、工具消费），HIR（High-level IR，高层中间表示）则是"降级"（lowering）后面向编译器分析的版本——去掉纯语法噪音、带上 DefId 与稳定身份。理解这条传送带，是从"会读解析器"到"会读编译器"的分水岭。

## rustc_hir：HIR 的家

rustc_hir/src/lib.rs 声明模块：arena、def（pub）、hir、intravisit（pub）、lints（pub）、pat_util（pub）、stable_hash_impls、target_impls，并再导出 `pub use hir::*`、`pub use rustc_hir_id::*`、`pub use crate::arena::Arena`。

其中 hir.rs:3562 定义了 `pub enum TyKind<'hir, Unambig = ()>`——这是编译器中四处同名 TyKind 之一（另三处在 rustc_ast、rustc_type_ir、rustc_public）。直接 grep `TyKind` 会在这四个 crate 间迷路，正确做法是记住各自坐标：ast.rs:2518 是语法、hir.rs:3562 是编译器 IR、ty_kind.rs:147 是类型内核、tys.rs:319 是稳定外部接口（详见[类型系统](/concepts/05-type-system-trait-solving.md)）。`intravisit` 是 HIR 的遍访器（visitor）框架，写任何 HIR 分析的第一件工具。

## rustc_ast_lowering：降级机器

rustc_ast_lowering/src/lib.rs 的顶层函数与结构勾勒出降级流程：

- `pub fn provide`(L99) —— 老朋友：向 query 系统注册 provider；
- `struct LoweringContext<'a, 'hir>`(L147) —— 降级状态；
- `struct SpanLowerer`(L307) —— span 层面的处理；
- `fn index_ast`(L498) —— 为 AST 建索引（DefId 分配的前置）；
- `fn lower_to_hir(tcx: TyCtxt<'_>, def_id: LocalDefId) -> hir::MaybeOwner<'_>`(L659) —— 降级主函数。

降级按语法类别分派到子模块：asm、block、contract、delegation、diagnostics、expr、format、index、item、pat、path、stability(pub)。注意 stability 是 pub 的——稳定性（stable/nightly）标注在降级期间就要处理。

## rustc_hir_analysis：HIR 上的第一个分析层

AST lowering 之后，rustc_hir_analysis 承接 HIR 上的收集与检查。其 src/lib.rs 的模块：check(pub)、autoderef(pub)、check_unused、coherence、collect、constrained_generic_params、delegation(pub)、diagnostics(pub)、hir_ty_lowering(pub)、hir_wf_check(pub)、impl_wf_check、outlives、variance；关键函数：`pub fn provide`(L129)、`pub fn check_crate`(L148)、`pub fn lower_ty`(L242)、`pub fn lower_const_arg_for_rustdoc`(L254)。

模块名即职责清单：`collect` 收集项与类型定义，`coherence` 保证 trait 实现的唯一性，`variance` 推导生命周期与类型参数的型变，`hir_ty_lowering` 把 HIR 的类型降级到 ty 层，`outlives` 处理生命周期约束。crate 的 README.md 只有短短两行：指向 rustc-dev-guide 的 hir typeck 章节链接——官方阅读指南也把这里当作类型检查的入口。

## rustc_hir_typeck：表达式层面的类型检查

真正给每个表达式定类型的引擎在 rustc_hir_typeck。其 src/lib.rs 的子模块（前 20 个）像一张检查器地图：_match、autoderef、callee、cast(pub)、check、closure、coercion、demand、diagnostics、diverges、expectation、expr、inline_asm、expr_use_visitor(pub)、fallback、fn_ctxt、gather_locals、intrinsicck、loops、method。

几个关键词：`coercion`（强制转换，Rust 类型系统最微妙的机制之一）、`method`（方法解析）、`callee` 与 `closure`（函数/闭包调用的双向检查）、`diverges`（发散性控制流 `!` 的追踪）、`expectation`（期望类型的双向传播）、`expr_use_visitor`（pub，供外部消费的使用分析）、`autoderef`（自动解引用链）。

## 在流水线中的位置

```text
AST（rustc_ast）
   │  rustc_ast_lowering::lower_to_hir
   ▼
HIR（rustc_hir）
   │  rustc_hir_analysis（collect / coherence / variance / hir_ty_lowering）
   │  rustc_hir_typeck（表达式类型检查）
   ▼
ty 层类型（rustc_middle::ty，见下一概念文档）
```

HIR 上的每个阶段都以 provider 形式接入 query 系统（三个 crate 各有 `provide()`），再次印证[流水线总览](/concepts/02-compiler-pipeline-overview.md)的判断：passes.rs 是骨架，query 图才是执行模型。

## 相关概念

- [解析与宏展开](/concepts/03-parsing-macro-expansion.md) — HIR 的输入：展开完成的 AST
- [类型系统与 trait 求解](/concepts/05-type-system-trait-solving.md) — hir_ty_lowering 的输出目的地：TyCtxt 与 ty 层
- [MIR 与借用检查](/concepts/06-mir-borrow-checking.md) — 类型检查之后的 THIR/MIR 域
- [rustc 编译器信源登记](/references/rustc-source-map.md) — 本篇各 crate 的关键文件与行号坐标
