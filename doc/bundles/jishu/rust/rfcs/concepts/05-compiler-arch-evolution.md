---
type: Concept
title: 编译器架构演进：HIR、MIR 与 dyno
description: 以 HIR 引入、MIR 中层表示、dyno 数据访问三篇 RFC 串联 rustc 编译器内部架构的设计决策与「先批准后部分拒绝」的警示
tags: [rust, rfcs, compiler, hir, mir, type-erasure, dyno]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-28T10:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T10:00:00+08:00" }
status: stable
stale_after: 2027-08-28
sources:
  - id: rfcs-source
    resource: /references/rfcs-source-map.md
---

# 编译器架构演进：HIR、MIR 与 dyno

RFC 仓库不只承载语言特性——编译器内部架构的演进同样在此留档。本篇精读三篇：RFC 1191 引入 HIR（高层中间表示），RFC 1211 引入 MIR（中层中间表示），RFC 3192 扩展 `any` 模块（dyno）。前两篇定义了今天 rustc 的骨架，第三篇则提供了一个罕见的「先批准、后部分拒绝」的活标本。

## 1191-hir：高层中间表示

RFC 1191（Start Date 2015-07-06，Feature Name 与 Rust Issue 均为 N/A）向编译器添加 HIR——文档自述 "basically a new (and additional) AST more suited for use by the compiler"（本质上是一个新的、附加的、更适合编译器使用的 AST）（F-rfcs-113、F-rfcs-114）。文档同时声明：这是**纯编译器实现细节、对语言无影响**，且添加 HIR 不排除未来添加 MIR 或 LIR。

Motivation（F-rfcs-115）：当时的 AST 同时服务于三个主人——libsyntax（语法库）、编译器、语法扩展（syntactic extensions）。RFC 的拆分方案：

- **libsyntax 版本 AST**：语法操作，最终稳定供语法扩展与工具使用
- **HIR**：完全编译器内部

语言构造的语法扩展（如 `for` 循环、`if let`）从 AST 操作移到 AST→HIR lowering（下降）步骤；lifetime elision（生命周期省略）也拟移入 lowering。

Detailed design 坦白得近乎激进（F-rfcs-116）：**初始 HIR 将是（几乎）与 AST 相同的副本，lowering 步骤仅为复制操作**；macros、`for` 循环等已在 libsyntax 中展开的构造不属于 HIR。Alternatives 列出：维持现状，或跳过 HIR 直接 lower 到 MIR——后者是更复杂的重构，且错失稳定 AST 供工具与语法扩展使用的好处。这是一个「先分家、再改造」的两步走策略：第一步只做复制，把编译器内部表示与稳定表面解耦。

## 1211-mir：中层中间表示

RFC 1211（Start Date 2015-07-14，Rust Issue rust#27840）是三篇中最重的一篇（F-rfcs-118）。Summary：向编译器引入「中层 IR」；MIR 脱糖（desugars）大部分 Rust 表面表示，留下适合类型检查与翻译的更简单形式；文档描述 MIR "radically simpler"（激进地更简单）——**不含 "match" 语句**，将 `ref` 绑定与 `&` 表达式转换为单一形式（F-rfcs-119）。

Motivation 六点（原文编号，F-rfcs-120）：

1. **编译器复杂度增加**：所有 pass（遍）须针对完整 Rust 语言编写——闭包/for 循环/if let/while let/box 表达式/重载操作符/方法调用等都需在各阶段脱糖；box patterns 与非词法生命周期在当前表示下几乎不可实现
2. **AST 上推理细粒度控制流困难**：MIR 基于 CFG（控制流图）
3. **安全分析可靠性降低**：分析对象 AST 与执行对象 bitcode 差距大
4. **安全证明可靠性**：MIR 足够简单，最终可基于 MIR 本身做证明
5. **Rust 特定优化有挑战**：可在翻译到 bitcode 前于 MIR 上优化
6. **脱离 LLVM 迁移几乎不可能**：Rust 语义嵌入在 trans（翻译）步骤；MIR 设计下语义改由 AST→MIR 翻译描述

Motivation 还盘点编译器中已有三种模拟 MIR 效果的结构（F-rfcs-121）：Adjustments（类型检查器计算、后续分析读取）、CFG（建于 AST 之上，仅是控制流近似）、`ExprUseVisitor`（向安全分析回调 borrow/move 等动作——文档评价 "effectively a kind of MIR, but it is not complete enough to do translation"，即一种 MIR 但不完整到可做翻译）。Detailed design 展开为 14 个小节（F-rfcs-122）：从 Overview of the MIR、Assignments/values/rvalues，经 Bounds checking、Overflow Checking、Matches、Drops，到 Phasing、Monomorphization（单态化）、Unchecked assertions。

> MIR 的第 1 点动机中「非词法生命周期在当前表示下几乎不可实现」与 [异步与借用](/concepts/04-async-and-borrowing.md) 的 2094-nll 形成 RFC 间因果链：MIR（2015 提案）是 NLL（2017 提案）的实现前提。rustc 的现状可在 rust/rust 知识包的 MIR 与 HIR 篇中找到对应实现坐标（rustc_middle 的 Thir/Body/BasicBlockData 定义、rustc_hir 的 HIR 定义）。

## 3192-dyno：基于类型的数据访问与「先批准后部分拒绝」

RFC 3192（Feature Name `provide_any`，Start Date 2021-11-04，Rust Issue rust#96024）扩展核心库 `any` 模块，提供对象按类型访问数据的通用 API——与既有类型驱动 downcast（向下转型）API 相对，本扩展将 downcast 集成进数据访问；示例：`let s: String = object.request();`、`let s = object.request_field::<str>();`（F-rfcs-124、F-rfcs-126）。

**本篇最重要的内容在文档头部**（F-rfcs-125）：

> "This RFC was previously approved, but part of it later **rejected**"

`Provider` 接口被 libs team 会议拒绝；剩余部分为 `Demand` 类型（在 rust PR 113464 中重命名为 `Request`）；由于 `error_generic_member_access` 是当时唯一已知使用 `Demand`/`Request` 的特性，决定由该特性跟踪并将本 RFC 标记为 rejected for now。这是「接受 ≠ 定案」的活标本——见 [RFC 生命周期与团队治理](/concepts/07-rfc-lifecycle-governance.md)。

Notes 节补充谱系（F-rfcs-127）：主要动机是 `Error` trait 的 'generic member access'（此前由 RFC 2895 提议，本 RFC 以 Error 为驱动示例但明确不提议修改 Error）；概念验证实现在 nrc/provide-any；本工作改编自 mystor/dyno；早期迭代暴露的 type tags（类型标签）概念仍用于实现但**不再暴露于 API**——实现细节从 API 表面退隐的又一实例。

## 家族视角：表示层的经济学

三篇 RFC 共享一个设计经济学：**每个表示层只为自己的消费者负责**。

| 表示层 | 消费者 | 稳定性承诺 |
|--------|--------|-----------|
| AST（libsyntax） | 语法扩展、工具 | 长期稳定 |
| HIR | 编译器各分析阶段 | 编译器内部，无语言承诺 |
| MIR | 类型检查、借用检查、优化、翻译 | 编译器内部，「足够简单以至于可以做证明」 |

HIR RFC 的「初始仅为复制」与 MIR RFC 的「不含 match、ref 与 & 归一」，都是把「脱糖」作为表示层之间的转换语义。而 dyno 一篇补充了另一面：当提案的实现细节（type tags）不再必要时，就应从 API 表面移除——**表示的简化与接口的简化是同一场战争的两条战线**。

## 相关概念

- [RFC 流程与模板](/concepts/00-rfc-process-and-template.md) — 1191/1211 的「纯实现细节 RFC」展示了模板在编译器导向变体下的使用
- [异步与借用](/concepts/04-async-and-borrowing.md) — NLL 以 MIR 为载体，两篇 RFC 构成因果链
- [类型系统演进](/concepts/02-type-system-evolution.md) — MIR 的类型检查职责承接 where 子句与关联类型的求解
- [RFC 生命周期与团队治理](/concepts/07-rfc-lifecycle-governance.md) — 3192 的「先批准后部分拒绝」是生命周期语义的活标本
- [rust-lang/rfcs 信源登记](/references/rfcs-source-map.md) — 三篇 RFC 的文件路径与元数据
