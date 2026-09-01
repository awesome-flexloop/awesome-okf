---
type: Concept
title: 错误处理与安全演进
description: 从 panic 术语重命名、? 操作符与 Try trait、try 关键字到 I/O 安全与 debug_assert，串联 Rust 错误处理与安全边界的演进
tags: [rust, rfcs, error-handling, panic, try-trait, io-safety, assert]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-28T10:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T10:00:00+08:00" }
status: stable
stale_after: 2027-08-28
sources:
  - id: rfcs-source
    resource: /references/rfcs-source-map.md
---

# 错误处理与安全演进

Rust 错误处理的演进是一条「术语先行、机制随后、边界收尾」的路线：2014 年先厘清 panic/failure/abort 的词汇（RFC 221），随后 `?` 操作符从宏惯例升级为 trait 驱动的语言机制（RFC 243 → 1859 → 2388），2021 年再把同样的安全思维延伸到 I/O 资源句柄（RFC 3128）。本篇精读五篇 RFC 并附一篇抽样，覆盖从宏到类型系统的完整光谱。

## 0221-panic：术语三分

RFC 221（Start Date 2014-09-23，Rust Issue rust#17489）做的是纯术语工作：将 "task failure" 重命名为 "task panic"，`fail!` 重命名为 `panic!`（F-rfcs-080、F-rfcs-081）。

Detailed design 的术语三分（F-rfcs-082）：

| 术语 | 语义 |
|------|------|
| **failure** | 产生 `Err` 或 `None` 的操作（普通错误路径） |
| **panic** | 任务级 unwinding（栈展开） |
| **abort** | 中止整个进程 |

"panic" 的选择参考了 discuss 线程与 workweek 讨论（均附链接），语言先例为 Go，词源可溯至 Kernel panics。Alternatives 节列出的落选关键字各有明确否决理由（F-rfcs-083）：`throw!`/`unwind!`（暗示通用异常处理、强调机制而非策略）、`abort!`（与进程 abort 歧义）、`die!`（不明显什么被杀死）。Drawbacks 承认 "panic" 一词略不正式且改名工作量大。

这是一篇仅 5 个二级章节的短文档（F-rfcs-084）——术语 RFC 可以很小，但它定下的词汇表被后续所有错误处理讨论沿用至今。

## 0243 与 1859：? 操作符的两次接力

### 起源：0243-trait-based-exception-handling

抽样 RFC 243（Start Date 2014-09-16，头部字段为 Feature-gates: `question_mark`、`try_catch`）提议添加 `?` 操作符与 `catch { ... }` 表达式；`?` 操作符想法源自 RFC PR 204（@aturon）（F-rfcs-172）。注意它的 Rust Issue 是 rust#31436——**与 RFC 1859 共享同一 tracking issue**：提案间的取代与继承关系比编号所示更纠缠。

### 成型：1859-try-trait

RFC 1859（Feature Name `try_trait`，Start Date 2017-01-19，Rust Issue rust#31436）引入 trait `Try`，定制 `?` 操作符应用于 `Result` 以外类型时的行为（F-rfcs-085、F-rfcs-086）。

Motivation 的证据链（F-rfcs-087）：

- `try_opt!` 宏的存在与流行印证 `Option` 等类型上的类似模式——RFC 的总体目标是让 rustfmt 中的 `try_opt!(width.checked_sub(...))` 写成 `width.checked_sub(...)?`
- futures 的三态（成功结果/"not ready yet"/错误）以 `enum Poll<T, E> { Ready(T), NotReady, Error(E) }` 表达后，可将 `try_ready!(self.stream.poll())` 替换为 `self.stream.poll()?`

文档还记载了既有行为（F-rfcs-088）：`try!` 宏与 `?` 操作符已允许错误侧经 `From` trait 的类型转换（`F: From<E>`，错误时返回 `F::from(err)`），如把多种错误上转到公共错误类型 `Box<Error>`。**? 不是一个新机制，而是对既有转换惯例的 trait 化**——这是理解 Try 设计的关键。

## 2388-try-expr：try 关键字与 try 表达式

RFC 2388（Feature Name `try_expr`，Start Date 2018-04-04，Rust Issue rust#50412）解决 RFC 243 遗留的关键字选择问题（F-rfcs-090、F-rfcs-091）。三项决定：

1. 在 edition 2018 保留 `try` 为关键字
2. 将 `do catch { .. }` 替换为 `try { .. }`
3. 不保留 `catch` 为关键字

Motivation 的技术论证（F-rfcs-092）：所选关键字**不能是 contextual（上下文相关）的**——语法形式 `<word> { .. }` 与名为 `<word>` 的 struct 冲突。文档给出 Rust 2015 中合法的 `struct try; fn main() { try {}; }` 代码示例，并引 `warning: type 'try' should have a camel case name` 警告——该警告降低了生态中存在名为 try 的类型的概率。

Drawbacks 三个小节（F-rfcs-093）：与异常处理的联想（利弊兼有，引 Niko Matsakis 关于利用其他语言直觉的引文）、对 `try!` 宏的破坏、`?` 的反向语义（问号成功继续、失败返回，与直觉相反）。Rationale and alternatives 竟含 8 个备选方案小节（F-rfcs-094）：reserving `catch`、keeping `do catch { .. }`、`do try { .. }`、using `do { .. }`、reserving `trap`、reserving `wrap`、reserving `result`、a smattering of other possible keywords——**单个关键字的选词成本可以高达一整个 RFC**。

## 3128-io-safety：I/O 安全

RFC 3128（Feature Name `io_safety`，Start Date 2021-05-24，Rust Issue rust#87074）把内存安全的思维迁移到资源句柄（F-rfcs-139、F-rfcs-140）：通过引入 I/O 安全概念与一组新类型和 trait，为 `AsRawFd` 及相关 trait 的用户提供关于原始资源句柄的保证，以此关闭 Rust 封装边界（encapsulation boundaries）的漏洞。

漏洞描述（F-rfcs-141）：`FromRawFd::from_raw_fd` 是 unsafe 的（阻止 `File::from_raw_fd(7)`），但 `AsRawFd` **不限制** `as_raw_fd` 的返回值——`pub fn do_some_io<FD: AsRawFd>(input: &FD)` 可对任意 `RawFd` 做 I/O，`do_some_io(&7)` 甚至合法（`RawFd` 自身实现了 `AsRawFd`）。特殊情况下违反 I/O 安全可导致违反内存安全（文档给出 `memfd_create` + `mmap` 安全包装例）。

概念的核心类比（F-rfcs-142）：

> "Protection from raw pointer hazards is called memory safety, so protection from raw handle hazards is called *I/O safety*"

raw handle（原始句柄）类比 raw pointer——**获取（obtain）安全、使用（用于 I/O）可能出危险**。引入的 API（F-rfcs-143）：`OwnedFd` 与 `BorrowedFd<'fd>` 类型；`AsFd`、`Into<OwnedFd>`、`From<OwnedFd>` trait；另有 Gradual adoption（渐进采纳）小节。

## 0050-assert：debug_assert 宏

家族的起点是 2014 年的 RFC 50（Start Date 2014-04-18，Rust Issue rust#13789）：断言对 release 构建太昂贵且妨碍内联（mess up inlining），必须有办法关闭；提议宏 `debug_assert!` 与 `assert!`，测试用例应使用 `assert!`（F-rfcs-158、F-rfcs-159）。

设计极简（F-rfcs-160）：debug 构建（无 `--cfg ndebug`）中 `debug_assert!()` 与 `assert!()` 相同；release 构建（`--cfg ndebug`）中 `debug_assert!()` 编译为空；`assert!()` 的定义为 `if (!EXPR) { fail!("assertion failed ({}, {}): {}", file!(), line!(), stringify!(expr) }`——注意其中的 `fail!` 正是 RFC 221 改名前的旧术语。全文 25 行、5 个二级章节、Unresolved questions 内容 "None."（F-rfcs-161）。

## 家族视角：安全边界的三次迁移

1. **词汇迁移**（221）：先用术语三分把 failure/panic/abort 的语义钉死
2. **机制迁移**（243→1859→2388）：? 从宏惯例到 Try trait 到 edition 关键字——错误处理逐步「类型系统化」
3. **边界迁移**（3128）：从内存安全（raw pointer）到 I/O 安全（raw handle），安全论证的模式可复用

I/O 安全一篇中「不限制 as_raw_fd 返回值」的漏洞模式与 [类型系统演进](/concepts/02-type-system-evolution.md) 中 0401-coercions 的 receiver 强制漏洞模式互为镜像——类型系统每一次「隐式转换放行」都可能是下一个安全 RFC 的动机。

## 相关概念

- [语言演进：表达式与模式](/concepts/01-lang-evolution-expr-pattern.md) — let-else 与 ? 同为「错误路径语法」，常在同一函数中配合使用
- [类型系统演进](/concepts/02-type-system-evolution.md) — Try trait 与 From 转换是类型系统在错误路径上的应用
- [异步与借用](/concepts/04-async-and-borrowing.md) — Try 的 Motivation 直接引用 futures 的 Poll 三态设计
- [RFC 生命周期与团队治理](/concepts/07-rfc-lifecycle-governance.md) — 0243 与 1859 共享 tracking issue 的继承关系
