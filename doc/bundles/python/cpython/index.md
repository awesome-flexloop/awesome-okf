---
okf_version: "0.2"
---

# CPython 解释器核心架构知识库

本知识包是 [CPython](https://github.com/python/cpython)（Python 编程语言的官方 C 语言参考实现）的系统化中文教程，基于 CPython 3.16.0a0（main 分支开发版）源码深度阅读生成，覆盖从源码导航到核心架构的完整知识体系。所有内容均溯源至 CPython C 源码（`Include/`、`Objects/`、`Python/`、`Modules/` 等核心目录），遵循 [OKF v0.2 规范](https://github.com/awesome-flexloop/awesome-okf)。

## 入门基础（concepts/）

* [CPython 简介](concepts/00-introduction.md) — 什么是 CPython、核心组件概览、为什么阅读源码、学习路径。
* [源码目录结构导航](concepts/01-source-layout.md) — 仓库目录布局详解，Include/Objects/Python/Modules/Lib 等核心目录用途与关键文件。
* [对象模型：PyObject 与 PyVarObject](concepts/02-object-model.md) — "一切皆对象"的底层结构，PyObject/PyVarObject 双模式布局（GIL vs free-threading）、对象宏、永生对象。
* [类型系统与 PyTypeObject](concepts/03-type-system.md) — PyTypeObject 完整字段布局、数值/序列/映射/异步四大方法套件、tp_flags 类型标志、元类型递归。
* [引用计数与内存分配](concepts/04-reference-counting.md) — Py_INCREF/Py_DECREF/Py_CLEAR 宏、对象创建销毁流程、pymalloc arena/pool/block 三级分配器。

## 核心机制（concepts/）

* [垃圾回收器](concepts/05-garbage-collector.md) — 引用计数无法处理循环引用、分代 GC（三代）、GC 头布局、tp_traverse/tp_clear 协议、GC 工作流程。
* [解释器帧与执行栈](concepts/06-interpreter-frame.md) — _PyInterpreterFrame 结构体、四种帧所有者类型、localsplus 内存布局、栈操作内联函数。
* [字节码执行引擎](concepts/07-bytecode-execution.md) — _PyEval_EvalFrameDefault 主循环、computed goto 指令调度、_Py_CODEUNIT 2字节指令单元、关键指令实现、异常展开流程、GIL 与待处理事件。

## 高级主题（concepts/）

* [编译器流水线](concepts/08-compiler-pipeline.md) — 源码→Tokenizer→AST→符号表→CFG→字节码五阶段、PyCodeObject 字段详解、marshal 序列化与 .pyc 文件。
* [模块与导入系统](concepts/09-module-import.md) — _inittab 内置模块注册表、__builtins__ 模块内容、导入四步流程、导入锁、sys.modules 缓存、C 扩展模块定义。

## 实战示例（examples/）

* [最简 C 扩展模块](examples/minimal-c-extension.md) — 从零编写 spam 模块：方法函数→方法表→模块定义→PyInit 入口，含参数解析、setuptools 构建与测试。
* [用 C 定义自定义类型](examples/custom-type-c.md) — 定义 CustomStack 类型：tp_new/tp_init/tp_dealloc 生命周期、tp_members/tp_getset 属性、PyType_Ready 注册。
* [字节码剖析](examples/bytecode-dissection.md) — 使用 dis 模块反汇编 Python 函数，逐条解读 LOAD_FAST/CALL/RETURN_VALUE 等指令、栈状态追踪、CodeObject 属性访问。

## 信源登记簿（references/）

* [CPython 源码信源登记](references/cpython-source.md) — CPython 3.16.0a0 版本信息、源码路径、核心目录结构、关键文件清单、C API 入口点。

## 信任与生命周期说明

* **status 判定依据**：全部 14 个内容文档（10 个概念 + 3 个示例 + 1 个信源登记）均 `status: stable`。内容基于对 CPython 3.16.0a0 源码（`external/libs/python/cpython/` 目录）核心子系统的逐模块阅读与事实提取（233+ 源码事实），经 source-code-to-okf-wiki 五阶段流程（R→I→E→V→C）生成。
* **stale_after 解释**：统一设置为 `2027-08-21`。CPython C API 核心结构（PyObject、PyTypeObject、字节码引擎）自 Python 3 以来保持相对稳定；该日期作为对未来大版本（如 3.17+ 自由线程稳定化、JIT 合入）的保守重新评估节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻（2026-08-21）；`verified.at` 记录 V 阶段对抗审查核验事件（2026-08-21），两者分离、可追溯。

本知识包共收录 14 个内容文档（10 个概念 + 3 个示例 + 1 个信源登记），另含 3 个子目录 index.md 与根 index.md、log.md。

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
