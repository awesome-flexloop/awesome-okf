---
type: Concept
title: 异步与借用：NLL、Pin 与 futures
description: 以非词法生命周期、Pin/Unpin、futures API 稳定化三篇精读 RFC 串联 Rust 借用检查器与异步生态的协同演进
tags: [rust, rfcs, borrow-checker, nll, pin, futures, async-await]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-28T10:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T10:00:00+08:00" }
status: stable
stale_after: 2027-08-28
sources:
  - id: rfcs-source
    resource: /references/rfcs-source-map.md
---

# 异步与借用：NLL、Pin 与 futures

异步 Rust 的落地史是三条 RFC 线索的交织：借用检查器先学会看控制流（2094-nll），库层再提供「不可移动」的安全抽象（2349-pin），最后 futures API 进入标准库（2592-futures）。本篇精读这三篇 RFC 并附抽样 2394（async/await 语法），展示「借用系统的演进」与「异步的诞生」如何互为前提。

## 2094-nll：非词法生命周期

RFC 2094（Feature Name `nll`，Start Date 2017-08-02，Rust Issue rust#43234）扩展 Rust 借用系统以支持**非词法生命周期**（non-lexical lifetimes）——基于控制流图（CFG）而非词法作用域的生命周期（F-rfcs-096、F-rfcs-097）。总体效果是消除许多「小型、函数局部的代码修改才能通过借用检查」的常见情形。

Motivation 先做术语区分（F-rfcs-098）：**lifetime**（引用被使用的代码跨度）与 **scope**（值被释放/析构函数运行前的跨度）是两回事——引用的 lifetime 不能超过所指值的 scope；文档以 `data` 向量被可变借用传给 `capitalize` 的代码示例区分两者。NLL 改变的是 lifetime 的判定方式：不再随词法块走，而是随实际最后一次使用走。

Motivation 列出四个问题案例（F-rfcs-099）：

1. references assigned into a variable（引用赋给变量后再用）
2. conditional control flow（条件控制流下的借用可用性）
3. conditional control flow across functions（跨函数的条件控制流）
4. mutating `&mut` references（可变引用的重借用）

Detailed design 采用六层分层结构（F-rfcs-100）：Layer 0: Definitions → Layer 1: Control-flow within a function → Layer 2: Avoiding infinite loops → Layer 3: Accommodating dropck → Layer 4: Named lifetimes → Layer 5: How the borrow check works。文档还含附录 "Appendix: What this proposal will not fix"（列举本提案不修复的借用检查器局限），How We Teach This 含 Terminology、framing errors in terms of points 等小节，全文 29 个标题（F-rfcs-101）——**明确写出「不修复什么」是这篇 RFC 最值得学习的诚实设计**。

## 2349-pin：Pin 与 Unpin

RFC 2349（Feature Name `pin`，Start Date 2018-02-19，Rust Issue rust#49150）向 libcore/libstd 引入新 API，作为**不能安全移动的数据的安全抽象**（F-rfcs-102、F-rfcs-103）。

Motivation：长期存在的问题是处理不应被移动的类型——struct 含指向自身表示的指针（自引用类型，self-referential）；generators（生成器）工作使该用例变得重要——generator 将栈帧具象化为对象，而栈帧中天然含自引用。

Guide-level explanation 的核心目标原文（F-rfcs-104）：

> "provide a reference type where the referent is guaranteed to never move before being dropped"（提供一种引用类型，保证其指涉物在被丢弃前永不移动），且 "without *any* type system changes"（**不改动任何类型系统**）

关键设计：`Pin<'a, T>` 同时涵盖可移动与不可移动 referent（被指物），配对 auto trait（自动 trait）`Unpin`：

- `T: Unpin`（默认）时，`Pin<'a, T>` 完全等价于 `&'a mut T`
- `T: !Unpin` 时，安全地只提供 `&'a T` 访问且保证 referent 永不被移动；获得 `&'a mut T` 访问是 unsafe 的（`mem::replace` 等可经 `&mut` 移出数据）

类型定义（F-rfcs-105）：`pub unsafe auto trait Unpin { }` 加入 `core::marker` 与 `std::marker`——是 lang item（语言项），仅为某些 generators 生成 negative impls（否定实现），语义完全经库 API 实施；`#[fundamental] pub struct Pin<'a, T: ?Sized + 'a> { data: &'a mut T }` 加入 `core::mem` 与 `std::mem`；`Pin` 实现 `Deref`，**仅当 `T: Unpin` 时实现 `DerefMut`**（使得 `mem::swap`/`mem::replace` 对非 Unpin 类型不可安全调用）；另有 `PinBox<T>` 作为 `Box` 的 pinned 类比。

Rationale and alternatives 覆盖六个方向的对照（F-rfcs-107）：Comparison to `?Move`、Comparison to using `unsafe` APIs、Anchor as a wrapper type and `StableDeref`、Stack pinning API、Making `Pin` a built-in type、Having both `Pin` and `PinMut`——每个被否决的设计都留下了否决理由。

## 2592-futures：futures API 稳定化

RFC 2592（Feature Name `futures_api`，Start Date 2018-11-09，Rust Issue rust#59113）提议稳定一等 async/await 语法的**库组件**：`std` 级任务系统全部 API（`std::task::*`）与核心 `Future` API（`core::future::Future` 与 `std::future::Future`）（F-rfcs-108、F-rfcs-109）。三个范围声明同样重要：不提议稳定 async/await **语法本身**（另行单独步骤）；不覆盖 `Pin` API 的稳定化（已另行提议）；文档自述为更早 futures RFC（PR 2418）的修订精简版（后者被推迟至 nightly 获得更多经验）。

Historical context 节给出完整时间线（F-rfcs-110）：

| 时间 | 事件 |
|------|------|
| 2016-08 | `Future` trait 起源于 futures crate，0.1 发布——确立 task/polling 模型核心思想 |
| 2018 年初 | futures-rfcs 修订核心 API（产出 0.2） |
| 2018-02 | pinning API（PR 2349）是 "game-changer"——使跨 yield 借用无需使核心 future API 不安全 |
| 2018-05 | 语法 RFC（PR 2394）合并而 API RFC 关闭——约定在 nightly 迭代后以稳定化 RFC 跟进（即本 RFC）；API 于 2018 年 5 月底落地 `std`（rust PR 51263） |
| — | Google Fuchsia 项目在操作系统场景大规模使用这些特性 |

Guide-level explanation（F-rfcs-111）：`Future` trait 表示异步惰性计算（最终产出值而不阻塞当前线程）；`async fn read_frame(socket: &TcpStream) -> Result<Frame, io::Error>` 的签名**等价于** `fn read_frame<'sock>(socket: &'sock TcpStream) -> impl Future<Output = Result<Frame, io::Error>> + 'sock`——async fn 只是返回 future 的函数的语法糖；task 比作轻量级线程，executor（执行器）从 `()`-producing `Future` 创建任务并 pin 之。

## 抽样：2394-async_await

抽样 RFC 2394（Feature Name `async_await`，Start Date 2018-03-30，头部含 rust#50547 与 rust#62290 `#![feature(async_closure)]` 两个 issue 链接）提议添加 async 与 await 语法，文档内嵌指向 companion RFC（姊妹 RFC）的相对链接 `2592-futures.md`（F-rfcs-173）——语法（2394）与 API（2592）作为一对 RFC 分轨推进，是「语法与库组件分离决策」的治理范例。

## 家族视角：三篇 RFC 的因果链

1. **NLL 是前提**：borrow check 基于控制流图后，async fn 跨 await 点的借用分析才有语义地基
2. **Pin 是钥匙**：自引用类型的「不能安全移动」问题被库抽象（而非类型系统改动）解决，futures 的跨 yield 借用因此无需 unsafe
3. **futures 是收口**：API 先于语法稳定，语法（2394）与库（2592）分轨、pinning（2349）独立成篇——异步三件套的解耦设计使每部分可独立演进与评审

Pin 的 `Deref`/`DerefMut` 拆分与 [错误处理与安全演进](/concepts/03-error-safety-evolution.md) 中 I/O 安全的 Owned/Borrowed 拆分同构：**把「能做什么」编码进类型，把不安全操作赶到 unsafe 边界外**。

## 相关概念

- [错误处理与安全演进](/concepts/03-error-safety-evolution.md) — Try trait 的 Motivation 直接引用 futures 的 Poll 三态
- [类型系统演进](/concepts/02-type-system-evolution.md) — Unpin 是 auto trait，其语义框架源自 0048-traits 的 trait 系统清理
- [编译器架构演进](/concepts/05-compiler-arch-evolution.md) — NLL 的控制流图分析以 MIR 为载体落地
- [RFC 生命周期与团队治理](/concepts/07-rfc-lifecycle-governance.md) — 2592 对 2418 的「推迟-重提」关系是 postponed 机制实例
