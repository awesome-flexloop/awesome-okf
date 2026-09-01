---
type: Concept
title: CPython 简介
description: 什么是 CPython、它与 Python 语言的关系、为什么阅读源码、本教程的学习路径
tags: [cpython, introduction, python, interpreter]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-21T16:52:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T17:30:00+08:00" }
status: stable
stale_after: 2027-08-21
sources:
  - id: cpython-source
    resource: /references/cpython-source.md
---

# CPython 简介

## 什么是 CPython

CPython 是 Python 编程语言的**官方参考实现**（reference implementation），用 C 语言编写，也是最广泛使用的 Python 解释器。当人们说"安装 Python"时，通常指的就是安装 CPython。

Python 是一门编程语言，而 CPython 是这门语言的具体实现之一。除了 CPython 之外，还有其他实现：

| 实现 | 语言 | 特点 |
|------|------|------|
| **CPython** | C | 官方实现、最成熟、C 扩展生态最丰富 |
| PyPy | Python | JIT 编译、执行速度快 |
| Jython | Java | 运行在 JVM 上、可调用 Java 类库 |
| IronPython | C# | 运行在 .NET 平台上 |
| GraalPython | Java/Truffle | GraalVM 上的高性能实现 |

CPython 既是解释器（interpreter）也是编译器（compiler）——它将 Python 源代码编译为字节码（bytecode），然后在栈式虚拟机（stack-based VM）上解释执行这些字节码。

## CPython 的核心组件

CPython 解释器可以划分为几个核心子系统：

1. **对象模型（Object Model）**：所有 Python 值的底层表示，包括 PyObject 基础结构、类型系统、引用计数
2. **内存管理（Memory Management）**：pymalloc 小对象分配器 + 分代垃圾回收器
3. **编译器（Compiler）**：源代码 → AST → 符号表 → 控制流图 → 字节码的多阶段流水线
4. **执行引擎（Execution Engine）**：基于栈的字节码解释器，使用 computed goto 进行指令调度
5. **模块系统（Module System）**：模块导入、缓存、包管理
6. **运行时状态（Runtime State）**：解释器状态（PyInterpreterState）、线程状态（PyThreadState）、GIL

## 为什么阅读 CPython 源码

阅读 CPython 源码可以带来以下收获：

- **深入理解 Python 语义**：某些 Python 行为（如可变默认参数、描述符协议、MRO）只看文档难以完全理解，读源码能看到精确的实现逻辑
- **性能优化**：了解底层实现后，可以写出更高效的 Python 代码（如知道列表和字典的内部结构，选择更合适的数据结构）
- **调试能力提升**：遇到诡异的 Bug 时，能够从 C 层面追踪问题根源
- **编写 C 扩展**：理解对象模型和 C API 后，可以编写高性能的 C 扩展模块
- **技术鉴赏力**：CPython 是一个经过30多年演进的成熟项目，其设计决策和工程实践本身就值得学习

## 版本说明

本教程基于 **CPython 3.16.0a0**（main 分支开发版）。3.16 版本包含了一些重要的新特性：

- **自由线程模式（Free-threading / nogil）**：可选的无 GIL 构建，`PyObject` 结构在自由线程模式下有不同的内存布局（增加了 `ob_tid`、`ob_mutex`、`ob_ref_local`、`ob_ref_shared` 等字段）
- **特化自适应解释器（Specializing Adaptive Interpreter）**：从 3.11 开始引入的字节码特化机制在 3.16 中持续优化
- **Tier 2 优化器（Tier 2 Optimizer）**：超级块（superblock）级别的优化执行

## 本教程的学习路径

本教程的概念文档按以下路径组织，建议按顺序阅读：

### 入门基础

1. [源码目录结构导航](01-source-layout.md) — 了解 CPython 仓库的目录布局，知道去哪里找代码
2. [对象模型：PyObject 与 PyVarObject](02-object-model.md) — 理解"一切皆对象"的底层结构
3. [类型系统与 PyTypeObject](03-type-system.md) — 类型对象的结构、方法套件、类型标志
4. [引用计数与内存分配](04-reference-counting.md) — 引用计数宏、对象创建/销毁、pymalloc 分配器

### 核心机制

5. [垃圾回收器](05-garbage-collector.md) — 分代 GC、循环引用检测、GC 头布局
6. [解释器帧与执行栈](06-interpreter-frame.md) — 栈帧结构、局部变量、操作数栈
7. [字节码执行引擎](07-bytecode-execution.md) — 解释主循环、字节码调度、关键指令实现

### 高级主题

8. [编译器流水线](08-compiler-pipeline.md) — 从源码到字节码的五阶段编译过程
9. [模块与导入系统](09-module-import.md) — 导入机制、模块缓存、内置模块

### 实战示例

- [编写最简 C 扩展](../examples/minimal-c-extension.md)
- [用 C 定义自定义类型](../examples/custom-type-c.md)
- [字节码剖析](../examples/bytecode-dissection.md)

## 前置知识

阅读本教程需要以下基础：

- **C 语言**：能够阅读结构体、宏、指针、函数指针等 C 语言特性
- **Python 语言**：熟练使用 Python，理解基本的数据类型、函数、类、模块
- **基本的计算机概念**：栈、堆、指针、内存布局、编译与解释

不需要的知识：

- 编译器设计的专业知识（教程中会解释相关概念）
- x86 汇编（CPython 是纯 C 实现，不包含平台相关汇编，只有少量 JIT trampoline）
- 复杂的构建系统知识

## 相关概念

- [源码目录结构导航](01-source-layout.md) — 第一步：找到你要读的代码在哪里
- [对象模型：PyObject 与 PyVarObject](02-object-model.md) — 理解一切 Python 值的基础
- [CPython 源码信源登记](../references/cpython-source.md) — 源码路径、版本信息、关键文件索引
