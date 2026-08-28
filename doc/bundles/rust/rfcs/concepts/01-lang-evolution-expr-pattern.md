---
type: Concept
title: 语言演进：表达式与模式
description: 以闭包统一、if let、while let、let-else 四篇精读 RFC 串联 Rust 表达式与模式匹配能力的演进谱系
tags: [rust, rfcs, closures, if-let, while-let, let-else, pattern-matching]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-28T10:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T10:00:00+08:00" }
status: stable
stale_after: 2027-08-28
sources:
  - id: rfcs-source
    resource: /references/rfcs-source-map.md
---

# 语言演进：表达式与模式

本篇精读四篇 RFC，串联 Rust 表达式与模式匹配（pattern matching）能力的演进谱系：RFC 114 把闭包统一进 trait 系统，RFC 160 引入 if let，RFC 214 引入 while let，RFC 3137 引入 let-else。四者跨越 2014 到 2021 七年，却共享同一设计语法——「模式作为条件」与「脱糖（desugaring，语言构造到更基础构造的翻译）到 match」。另附抽样 RFC 2497（if-let 链式写法）作为家族展望。

## 0114-closures：闭包与 Fn trait 统一

RFC 114（Start Date 2014-07-29，Rust Issue rust#16095，早期格式无 Feature Name 字段）是本家族中最早也最激进的一篇（F-rfcs-034）。

Summary 列出的核心变更（F-rfcs-035）：

- 函数调用 `a(b, ..., z)` 经 `Fn<A,R>`、`FnShare<A,R>`、`FnOnce<A,R>` 三个 trait 变为**可重载操作符**——A 为参数类型元组、R 为返回类型，三个 trait 的区别在 self 参数：`&mut self`、`&self`、`self`
- 移除 `proc` 表达式形式与类型
- 移除闭包类型（闭包形式保留为语法糖）

Motivation 的核心小节标题即点题："The core idea: unifying closures and traits"（统一闭包与 trait，F-rfcs-037）。调用 `a(b, c, d)` 脱糖为 `Fn::call(&mut a, (b, c, d))`、`FnShare::call_share(&a, ...)`、`FnOnce::call_once(a, ...)` 三者之一；闭包表达式翻译为实现三个 trait 之一的新鲜 struct。文档给出虚分派与静态分派的对照：`&mut Fn<(int,),int>`（trait 对象，运行时分派）与 `<F:Fn<(int,),int>>`（泛型 bound，静态分派）。

闭包表达式当时的新语法（F-rfcs-036）：`ref |...| expr` 按引用捕获 upvar（被捕获变量），`|...| expr` 按值捕获（Copy 或 move）；receiver（接收者）模式前缀 `|&mut: ...|` 对应 Fn、`|&: ...|` 对应 FnShare、`|: ...|` 对应 FnOnce；类型位置的语法糖 `|T1,...,Tn| -> R` 翻译为 `Fn<(T1,...,Tn),R>` 等对应形式。

> 历史注释：`FnShare` 后更名为 `FnMut`，`Fn` 的语义也有调整——今天的三件套是 `Fn`/`FnMut`/`FnOnce`。读 2014 年 RFC 时要意识到这是设计快照而非最终形态；但「闭包 = 实现 call 系 trait 的匿名 struct」这一核心模型延续至今。

## 0160-if-let：if let 表达式

RFC 160（Start Date 2014-08-26，Rust Issue rust#16779）引入 `if let PAT = EXPR { BODY }` 构造，允许 refutable（可反驳）模式匹配而无完整 `match` 的语法与语义开销及额外右移漂移（rightward drift，嵌套导致的代码右移）；非正式名称 "if-let statement"（F-rfcs-045）。

Motivation 对比两类既有写法的痛点（F-rfcs-046）：

```rust
// 写法一：match 必须写 None 臂、引入两级缩进
match optVal {
    Some(x) => { ... }
    None => {}
}
// 写法二：值被测试两次、unwrap 是可能失败的方法调用、需要预先存在的 let 绑定
if optVal.is_some() {
    let x = optVal.unwrap();
    ...
}
```

Detailed design 基于 Swift 的 if let 先例（Swift 中直接绑定 optional，本提案等价形式为 `if let Some(var) = expr`）；语法产出 `if-cond = 'let' pattern '=' expression`；条件表达式与普通 if 一样禁止尾随 braced block（大括号块）；编译器应对 irrefutable（不可反驳）模式的 if let 发出警告并建议改为普通 let（F-rfcs-047）。

**该构造可在语法 lowering（下降）pass 变换为等价 match——else 块成为 `_ => {}` 臂的 body**（F-rfcs-047）。这条「if let 脱糖为 match」的设计决定是整个家族的技术底座。

## 0214-while-let：while let 循环

RFC 214（Start Date 2014-08-27，即 if let RFC 的第二天）引入 `while let PAT = EXPR { BODY }`，允许将 refutable 模式匹配（含可选变量绑定）作为循环条件（F-rfcs-050）。

Motivation 有一段坦白的历史注记：Swift 也支持 while let，但这是在 if let RFC 完成后才发现的，太迟未纳入（F-rfcs-051）。文档给出 for 循环的脱糖示意：`for` 可映射为 `match &mut EXPR { i => { while let Some(PAT) = i.next() { BODY } } }`——也就是说 **for 循环在概念上就是 while let + 迭代器**。支持 while let 恢复了 if 与 while 两构造间的条件等价性。

脱糖规则（F-rfcs-052）：

```rust
// ['ident:] while let PAT = EXPR { BODY }
// 脱糖为
['ident:] loop {
    match EXPR {
        PAT => BODY,
        _ => break,
    }
}
```

irrefutable 模式给 while let 是错误（源于脱糖后 match 出现不可达模式）；以 feature gate（特性门，名为 `while_let`）引入。

这是一篇 84 行的短文档，Unresolved questions 一节内容为 "None."（F-rfcs-053）——与 [RFC 流程与模板](/concepts/00-rfc-process-and-template.md)所述「诚实条款」一致：没有未决问题也要如实写明。

## 3137-let-else：let-else 语句

时间快进到 2021：RFC 3137（Feature Name `let-else`，Start Date 2021-05-31，Rust Issue rust#87335）引入 `let PATTERN: TYPE = EXPRESSION else DIVERGING_BLOCK;`（非正式名称 let-else 语句），是 if-let 的对应物（F-rfcs-039、F-rfcs-040）。

语义关键点：

- 匹配**成功**时绑定引入外围作用域（而非 else 块）
- 匹配**失败**时必须发散（diverge，返回 `!` 类型，如 return 或 break）
- 表达式有限制——不得以 `}` 结尾或仅为 LazyBooleanExpression（惰性布尔表达式）

文档声明本 RFC 是 2015 年 RFC（PR 1303）中几乎相同特性的「现代化」（F-rfcs-041）——一个特性从提案到现代化落地可以相隔六年，这本身就是 RFC 生态时间尺度的实例。

Motivation 精确刻画了 if-let 的痛点（F-rfcs-042）：if-let 只能在其 body 内创建绑定，导致右移漂移、过度嵌套、条件与错误路径分离。let-else 反转结构——「失败」情形移入 else 块而「成功」情形在外围上下文继续；对非 Option/Result 枚举（没有 `ok_or()` 可用）尤其有价值。

## 抽样：2497-if-let-chains

抽样 RFC 2497（Feature Name `let_chains_2`，Start Date 2018-07-13，头部含 rust#53667、rust#53668 两个 issue 链接）提议扩展 if let 与 while let 表达式的链式写法，示例以 `&&` 连接多个 `let` 与 bool 条件（F-rfcs-176）。它是本家族的自然延伸：从「单个模式作为条件」到「模式与布尔条件混合的合取链」。

## 家族共性：模式匹配的脱糖谱系

四篇精读 + 一篇抽样共享三条设计法则：

1. **模式可以作为条件**：refutable 模式出现在 if/while/let 位置，匹配失败走另一条路径
2. **一切脱糖到 match**：if let 的 else 块是 `_ => {}` 臂、while let 是 `loop + match + break`、for 是 `while let + next()`
3. **irrefutable 模式触发警告或错误**：if let 警告建议改普通 let、while let 直接报错

从 RFC 视角看，这组演进还有治理含义：let-else 与 if-let-chains 都在 Drawbacks/Unresolved questions 中记录了与既有构造的语法冲突权衡（如 F-rfcs-043 的 3137 特有章节 "Conflicts with if-let-chains"）——语言表层语法的每次扩张都要付出歧义审查的成本。

## 相关概念

- [RFC 流程与模板](/concepts/00-rfc-process-and-template.md) — 本家族 RFC 的文体与流程背景
- [类型系统演进](/concepts/02-type-system-evolution.md) — 闭包的 Fn trait 统一是 trait 系统演进的组成部分
- [错误处理与安全演进](/concepts/03-error-safety-evolution.md) — let-else 的主要动机是错误处理模式简化
- [异步与借用](/concepts/04-async-and-borrowing.md) — ? 操作符与 let-else 同为错误路径语法
