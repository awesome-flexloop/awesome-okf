# 概念文档

本目录包含 CPython 解释器核心架构的 10 个概念文档，按学习路径排列：从入门到高级主题逐步深入。

## 入门基础

* [00-CPython 简介](00-introduction.md) — 什么是 CPython、核心组件、为什么读源码、学习路径。
* [01-源码目录结构导航](01-source-layout.md) — CPython 仓库的目录布局，Include/Objects/Python/Modules/Lib 等核心目录的用途与关键文件。
* [02-对象模型：PyObject 与 PyVarObject](02-object-model.md) — "一切皆对象"的底层结构，PyObject/PyVarObject 结构体、对象宏、永生对象。
* [03-类型系统与 PyTypeObject](03-type-system.md) — PyTypeObject 字段布局、方法套件（as_number/as_sequence/as_mapping）、tp_flags 类型标志。
* [04-引用计数与内存分配](04-reference-counting.md) — Py_INCREF/Py_DECREF 宏、对象创建销毁流程、pymalloc 三级分配器。

## 核心机制

* [05-垃圾回收器](05-garbage-collector.md) — 分代 GC、GC 头布局、三代回收策略、tp_traverse/tp_clear、循环引用检测。
* [06-解释器帧与执行栈](06-interpreter-frame.md) — _PyInterpreterFrame 栈帧结构、局部变量、操作数栈、帧链、栈操作内联函数。
* [07-字节码执行引擎](07-bytecode-execution.md) — _PyEval_EvalFrameDefault 主循环、computed goto 调度、_Py_CODEUNIT、关键指令实现、异常处理。

## 高级主题

* [08-编译器流水线](08-compiler-pipeline.md) — 源码→Tokenizer→AST→符号表→CFG→字节码五阶段、PyCodeObject、marshal 序列化。
* [09-模块与导入系统](09-module-import.md) — _inittab 内置模块注册表、__builtins__、导入锁、sys.modules 缓存、C 扩展模块。

```{toctree}
:hidden:
:maxdepth: 7

00-introduction
01-source-layout
02-object-model
03-type-system
04-reference-counting
05-garbage-collector
06-interpreter-frame
07-bytecode-execution
08-compiler-pipeline
09-module-import
```
