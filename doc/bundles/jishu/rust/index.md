---
okf_version: "0.2"
type: group
title: "🦀 Rust 语言核心"
description: "Rust 编译器、Cargo 构建系统与 RFC 设计决策——所有 Rust 生态知识的底层基础"
---

# 🦀 Rust 语言核心

本组存放 Rust 语言官方三大核心仓库的知识：rustc 编译器与标准库（rust 仓库）、Cargo 包管理与构建系统（cargo 仓库）、以及语言设计决策档案（rfcs 仓库）。理解编译器流水线、自举构建机制与 RFC 治理流程，是深入理解所有 Rust 生态项目的基础。

## 学习路径

| 顺序 | 知识包 | 一句话简介 |
|------|--------|-----------|
| 1 | [rust](rust/index.md) | rustc 编译器与标准库——bootstrap 三阶段自举、解析→HIR→类型检查→MIR→代码生成流水线、core/alloc/std 三层标准库、query 懒求值基础设施 |
| 2 | [cargo](cargo/index.md) | Cargo 包管理与构建系统——39 个子命令薄壳分发、GlobalContext 配置系统、依赖解析 resolver、Workspace/Package 模型、编译调度 unit 图 |
| 3 | [rfcs](rfcs/index.md) | Rust RFC 语言设计决策档案——RFC 流程与 FCP 机制、语言/类型系统/异步/编译器架构演进、lang/compiler/libs 三团队治理分流 |

```{toctree}
:hidden:
:maxdepth: 7

rust/index
cargo/index
rfcs/index
```
