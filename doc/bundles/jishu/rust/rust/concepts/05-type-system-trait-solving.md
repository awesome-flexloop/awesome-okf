---
type: Concept
title: 类型系统与 trait 求解：TyCtxt、InferCtxt 与下一代求解器
description: rustc_middle 的中央数据仓库与 TyCtxt 语境、rustc_infer 的推断上下文、以及 type_ir 与 next_trait_solver 刻画的求解器架构演进
tags: [rust, rustc, type-system, trait-solver]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-28T10:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T10:00:00+08:00" }
status: stable
stale_after: 2027-08-28
sources:
  - id: rustc-source
    resource: /references/rustc-source-map.md
---

# 类型系统与 trait 求解：TyCtxt、InferCtxt 与下一代求解器

## rustc_middle：中央数据仓库

一个反直觉事实先立于门前：**类型系统的大多数"所有权"其实不在某个 type crate，而在 rustc_middle**。它的 src/lib.rs 声明的 pub 模块覆盖了编译器全部中央数据：arena、dep_graph、diagnostics、hir、hooks、ich、infer、lint、metadata、middle、mir、mono、ptrauth、queries、query、thir、traits、ty、util、verify_ich。

thir 与 mir 也在其中（详见 [MIR 与借用检查](/concepts/06-mir-borrow-checking.md)）——rustc_middle 是"类型 + MIR + query"三合一的宿主 crate。

## TyCtxt 与上下文家族

rustc_middle/src/ty/context.rs 定义了类型语境的完整家族：

| 结构 | 行号 | 角色 |
|------|------|------|
| `CtxtInterners<'tcx>` | L134 | 类型驻留（interning）表：每个类型实例只存一份 |
| `CommonTypes<'tcx>` | L304 | 常用类型缓存 |
| `CommonLifetimes<'tcx>` | L379 | 常用生命周期缓存 |
| `CommonConsts<'tcx>` | L400 | 常用常量缓存 |
| `TyCtxtFeed<'tcx, K>` | L571 | 单 query 的"喂食器"（带类型的状态化写入口） |
| `GlobalCaches<'tcx>` | L663 | 全局缓存 |
| `TyCtxt<'tcx>` | L710 | 类型上下文：query 系统的句柄，编译器的心脏 |
| `GlobalCtxt<'tcx>` | L733 | 全局上下文 |
| `CurrentGcx` | L815 | 当前全局上下文的访问凭据 |

`TyCtxt` 既是 query 调用入口（`tcx` 上的每个方法对应一个 query），又通过 `CtxtInterners` 保证类型的廉价比较——两个 `Ty<'tcx>` 相等只需比指针。

类型本体的定义链：rustc_middle/src/ty/mod.rs 通过 `pub use self::sty::{...}` 再导出 TyKind、Binder、EarlyBinder、FnSig、PolyFnSig、TypingMode、ParamTy、ParamConst、Alias、AliasTy、AliasTyKind 等（L102-109）；ty/ 目录的 pub 子模块覆盖 abstract_const、adjustment、cast、codec、error、fast_reject、inhabitedness、layout、normalize_erasing_regions、offload_meta、pattern、print、relate、significant_drop_order、sty、trait_def、typetree、util、vtable。

## 四个 TyKind

`pub enum TyKind<I: Interner>` 定义于 rustc_type_ir/src/ty_kind.rs:147，是四处同名定义中的"类型内核"：

1. rustc_ast/src/ast.rs:2518 —— 语法表示；
2. rustc_hir/src/hir.rs:3562 —— 编译器 IR（[HIR](/concepts/04-hir-ast-lowering.md)）；
3. **rustc_type_ir/src/ty_kind.rs:147 —— 泛型于 Interner 的类型内核**；
4. rustc_public/src/ty/tys.rs:319 —— 稳定外部接口。

四层之间靠 lowering 逐层传递。讲类型系统时先画 rustc_type_ir（内核）到 rustc_middle::ty（编译器实例化）的映射，是官方源码的隐含阅读顺序。

## rustc_type_ir：可复用的类型内核

rustc_type_ir/src/lib.rs 的 pub 模块清单暴露了它的野心：data_structures、elaborate、error、fast_reject、inherent、intern、ir_print、lang_items、lift、outlives、region_constraint、relate、search_graph、solve、sty、walk。

关键信号有两个：`intern`（Interner trait 抽象，让同一套类型定义可以接不同后端）与 `solve` + `search_graph`（下一节的主角）。

## rustc_infer：推断上下文

rustc_infer/src/lib.rs 模块：diagnostics（私有）、infer（pub）、traits（pub）。infer/mod.rs 定义三件套：`InferCtxtInner<'tcx>`(L97)、`InferCtxt<'tcx>`(L246)、`InferCtxtBuilder<'tcx>`(L588)。

InferCtxt 是类型推断的临时语境：推理变量（推理过程中的未知类型）、区域约束、以及 trait 求解期间的快照回滚都住在里面。它从 `InferCtxtBuilder` 构造，围绕 `InferCtxtInner` 包装。

## trait 求解：两代架构并存

trait 求解（把 `impl` 与约束匹配起来的过程）在当前代码库呈现两代并存：

- **rustc_trait_selection**：src/lib.rs 的 pub 模块为 diagnostics、error_reporting、infer、opaque_types、regions、solve、traits——这是现在的主求解栈，`error_reporting` 模块提示 trait 错误信息是诊断体系的重点客户。
- **rustc_next_trait_solver**：pub 模块为 canonical、coherence、delegate、normalize、placeholder、solve。crate 名里的 "next" 是官方命名：它基于 rustc_type_ir 的 search_graph/solve 实现，通过 `delegate` 抽象与宿主编译器解耦——这是把求解器从 rustc_middle 中抽出来、使其可被 Miri 等其他工具复用的架构演进。

配套的 rustc_traits、rustc_ty_utils、rustc_ty_walk、rustc_transmute 分别承载 trait 相关 query 的实现与类型工具。

## 阅读路线图

1. 先读 rustc_type_ir/src/ty_kind.rs:147 的 `TyKind<I: Interner>`——所有类型讨论的公分母；
2. 再读 rustc_middle/src/ty/context.rs 的 TyCtxt 家族——编译器如何实例化内核；
3. 然后 rustc_infer 的 InferCtxt——推断变量如何诞生与消亡；
4. 最后对照 rustc_trait_selection 与 rustc_next_trait_solver 的模块表——同一问题域的两代答案。

类型检查完成的程序随后进入 THIR/MIR 域（[MIR 与借用检查](/concepts/06-mir-borrow-checking.md)）。

## 相关概念

- [HIR 与 AST Lowering](/concepts/04-hir-ast-lowering.md) — hir_ty_lowering 把 HIR 类型送进本篇的 ty 层
- [MIR 与借用检查](/concepts/06-mir-borrow-checking.md) — 类型化之后的中间表示与安全检查
- [rustc 基础设施](/concepts/09-rustc-infrastructure.md) — TyCtxt 背后的 query 系统完整机制
- [rustc 编译器信源登记](/references/rustc-source-map.md) — 类型系统各 crate 的关键坐标
