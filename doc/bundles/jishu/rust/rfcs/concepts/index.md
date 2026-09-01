# 概念文档

本目录包含 rust-lang/rfcs 知识包的 8 个概念文档，组织原则为**流程治理先行，精读 RFC 按语言特性主题家族分组**：00 是全部精读篇的「文体透镜」，01~06 按主题家族精读，07 以生命周期与治理收束。

## 流程与治理

* [00-RFC 流程与模板](/concepts/00-rfc-process-and-template.md) — 提交流程、RFC 编号即 PR 编号、FCP 机制、0000 模板的 9 章双解释文体、目录统计。
* [07-RFC 生命周期与团队治理](/concepts/07-rfc-lifecycle-governance.md) — active/postponed 生命周期语义、lang/compiler/libs 三团队分流准则、关键字保留、库团队重组。

## 语言演进主题家族

* [01-语言演进：表达式与模式](/concepts/01-lang-evolution-expr-pattern.md) — 闭包与 Fn trait 统一、if let、while let、let-else 的演进谱系。
* [02-类型系统演进](/concepts/02-type-system-evolution.md) — trait 系统清理、UFCS、where 子句、coercions、const fn、union、ADT 种类、复合赋值。
* [03-错误处理与安全演进](/concepts/03-error-safety-evolution.md) — panic 术语三分、? 操作符与 Try trait、try 关键字、I/O 安全、debug_assert。
* [04-异步与借用：NLL、Pin 与 futures](/concepts/04-async-and-borrowing.md) — 非词法生命周期、Pin/Unpin、futures API 稳定化、async/await。

## 架构与生态

* [05-编译器架构演进：HIR、MIR 与 dyno](/concepts/05-compiler-arch-evolution.md) — HIR 引入、MIR 中层表示、基于类型的数据访问与「先批准后部分拒绝」案例。
* [06-标准库与生态演进](/concepts/06-std-ecosystem-evolution.md) — Edition 机制、std::fs 扩展与 std::os 平台层级愿景。

```{toctree}
:hidden:
:maxdepth: 7

00-rfc-process-and-template
01-lang-evolution-expr-pattern
02-type-system-evolution
03-error-safety-evolution
04-async-and-borrowing
05-compiler-arch-evolution
06-std-ecosystem-evolution
07-rfc-lifecycle-governance
```
