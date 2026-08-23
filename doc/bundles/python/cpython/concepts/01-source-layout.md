---
type: Concept
title: "源码目录结构导航"
description: "CPython源码仓库的目录布局——Include/Objects/Python/Modules/Lib等核心目录的用途和关键文件"
tags: [cpython, source, layout, structure, navigation]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-21T18:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T18:30:00+08:00" }
status: stable
stale_after: 2027-08-21
sources:
  - id: cpython-source
    resource: /references/cpython-source.md
---

阅读 CPython 源码的第一步是知道去哪里找代码。CPython 仓库采用经典的 C 项目布局，不同层级的功能——公共 API、内部实现、解释器核心、标准库——分别位于不同的顶层目录中。

## 顶层目录概览

CPython 仓库根目录包含以下核心子目录：

| 目录 | 语言 | 用途 |
|------|------|------|
| `Include/` | C 头文件 | 公共 C API 头文件（含 `cpython/` 和 `internal/` 子目录） |
| `Objects/` | C | 内置对象类型实现 |
| `Python/` | C | 解释器核心（字节码执行、编译器、GC、生命周期、导入系统） |
| `Modules/` | C | C 实现的内置/扩展模块 |
| `Lib/` | Python | Python 实现的标准库 |
| `Grammar/` | PEG 语法 | Python 语法定义（`python.gram`）和词法标记（`Tokens`） |
| `Parser/` | C | PEG 解析器实现 |
| `Doc/` | reStructuredText | 官方文档 |
| `Misc/` | 杂项 | 稳定 ABI 列表、致谢、历史记录等 |
| `Mac/` | C/配置 | macOS 平台特定代码 |

此外还有构建系统文件：`configure.ac`（autoconf 配置）、`Makefile.pre.in`（Makefile 模板）、`pyproject.toml`（Python 包配置），以及 Windows 平台构建目录 `PC/` 和 `PCbuild/`。

## Include/：头文件分层

`Include/` 目录采用**三层头文件**设计，这是理解 CPython API 可见性边界的关键：

### 根目录头文件——公共 C API

`Include/` 根目录下的 `.h` 文件构成了**公共 C API**（稳定 ABI 的基础），是 C 扩展模块唯一应该直接包含的头文件。C 扩展只需 `#include <Python.h>`，该元头文件会自动引入所有必要的公共头。

核心公共头文件：

| 文件 | 内容 |
|------|------|
| `Python.h` | C API 总入口，按序引入所有公共头 |
| `object.h` | [PyObject](/concepts/02-object-model.md)、[PyVarObject](/concepts/02-object-model.md) 结构体与对象宏 |
| `objimpl.h` | 对象内存分配 API（`PyObject_New`、`PyObject_Free` 等） |
| `refcount.h` | 引用计数宏（`Py_INCREF`、`Py_DECREF`、`Py_CLEAR`） |
| `pymem.h` | 底层内存分配 API（`PyMem_Malloc`、`PyMem_Free`） |
| `ceval.h` | 字节码评估器公共 API |
| `pylifecycle.h` | 解释器生命周期（`Py_Initialize`、`Py_Finalize`） |
| `import.h` | 模块导入公共 API |
| `pystate.h` | 解释器/线程状态公共定义 |
| `pytypedefs.h` | 核心类型前向声明（`PyObject`、`PyTypeObject` 等） |
| `abstract.h` | 抽象对象层 API（通用协议调用） |

各内置类型也有对应的公共头文件：`longobject.h`（整数）、`unicodeobject.h`（字符串）、`listobject.h`（列表）、`dictobject.h`（字典）、`tupleobject.h`（元组）、`setobject.h`（集合）、`funcobject.h`（函数）、`codeobject.h`（代码对象）、`frameobject.h`（帧）、`moduleobject.h`（模块）等。

### Include/cpython/——实现细节头文件

`Include/cpython/` 子目录包含 **CPython 实现细节**头文件，不属于稳定 ABI，在次要版本之间可能发生不兼容变更。这些头文件提供了比公共 API 更深入的结构体访问能力，但 C 扩展开发者应意识到使用这些头文件意味着版本绑定。

关键文件包括 `Include/cpython/object.h`（[PyTypeObject](/concepts/03-type-system.md) 完整结构体定义、`PyHeapTypeObject`）、`Include/cpython/ceval.h`（评估器内部接口）、`Include/cpython/pystate.h`（解释器/线程状态内部接口）等。

`Include/object.h` 文件末尾通过以下机制引入实现细节头：

```c
#ifndef Py_LIMITED_API
#  define Py_CPYTHON_OBJECT_H
#  include "cpython/object.h"
#  undef Py_CPYTHON_OBJECT_H
#endif
```

### Include/internal/——私有内部头文件

`Include/internal/` 目录下的 `pycore_*.h` 头文件是**内部私有 API**，仅供 CPython 自身使用。扩展模块**不应**包含这些头文件。它们暴露了解释器最核心的内部结构：

| 文件 | 内容 |
|------|------|
| `pycore_object.h` | 对象内部操作 |
| `pycore_ceval.h` | 评估器内部细节 |
| `pycore_pystate.h` | 解释器状态内部细节 |
| `pycore_frame.h` | 帧结构体内部定义 |
| `pycore_interp.h` | 解释器状态完整结构 |
| `pycore_runtime.h` | 运行时全局状态 |

## Objects/：内置类型实现

`Objects/` 目录是 CPython **对象系统**的核心，每个 `.c` 文件通常对应一个内置类型的完整实现。文件命名遵循 `*object.c` 约定：

| 文件 | 类型 | 对应 Python 类型 |
|------|------|-----------------|
| `object.c` | 通用对象操作 | （None、True、False 等单例与通用函数） |
| `typeobject.c` | 类型对象 | `type`、类型创建、MRO、描述符协议 |
| `longobject.c` | 任意精度整数 | `int` |
| `floatobject.c` | 浮点数 | `float` |
| `unicodeobject.c` | Unicode 字符串 | `str` |
| `bytesobject.c` | 字节串 | `bytes` |
| `boolobject.c` | 布尔值 | `bool` |
| `tupleobject.c` | 元组 | `tuple` |
| `listobject.c` | 列表 | `list` |
| `dictobject.c` | 字典 | `dict` |
| `setobject.c` | 集合/冻结集合 | `set`、`frozenset` |
| `funcobject.c` | 函数对象 | `function` |
| `codeobject.c` | 代码对象 | `code` |
| `frameobject.c` | 帧对象 | `frame` |
| `moduleobject.c` | 模块对象 | `module` |
| `genobject.c` | 生成器/协程 | `generator`、`coroutine` |
| `iterobject.c` | 迭代器 | `iterator` |
| `fileobject.c` | 文件对象 | （C 层面的文件 I/O） |
| `exceptions.c` | 内置异常类型 | `Exception` 及其子类 |
| `call.c` | 调用协议 | `PyObject_Call` 系列函数 |
| `abstract.c` | 抽象对象协议 | 数值/序列/映射抽象层调用 |
| `obmalloc.c` | pymalloc 分配器 | 小对象内存分配器（arena/pool/block） |
| `structseq.c` | 结构体序列 | 用于 `sys.version_info` 等 C 结构体到 Python 元组的桥接 |
| `capsule.c` | Capsule 对象 | `PyCapsule`（C 指针封装） |
| `cellobject.c` | Cell 对象 | 闭包变量单元 |
| `enumobject.c` | 枚举对象 | `enumerate`、`reversed` 等迭代器 |

`Objects/` 目录下还有一个 `README` 文件，对各文件的作用有简要说明。

## Python/：解释器核心

`Python/` 目录是 CPython 解释器的**心脏**，包含编译器、字节码执行引擎、垃圾回收、生命周期管理、导入系统等核心机制：

| 文件 | 功能 |
|------|------|
| `ceval.c` | 字节码解释主循环（`_PyEval_EvalFrameDefault`）——**CPython 最重要的文件** |
| `ceval_gil.c` | GIL（全局解释器锁）实现、待处理信号/调用处理 |
| `bytecodes.c` | 字节码指令语义定义（DSL 形式） |
| `generated_cases.c.h` | 自动生成的字节码 case 分支（由 `bytecodes.c` 生成） |
| `compile.c` | 编译器主文件（AST → 字节码） |
| `ast.c` | AST 节点创建与操作 |
| `ast_unparse.c` | AST 反向生成源码 |
| `symtable.c` | 符号表构建 |
| `flowgraph.c` | 控制流图构建与基本块管理 |
| `assemble.c` | 代码对象汇编 |
| `codegen.c` | 代码生成器 |
| `gc.c` | 分代垃圾回收器实现 |
| `pylifecycle.c` | 解释器初始化与终结（`Py_Initialize`、`Py_Finalize`） |
| `pystate.c` | 线程状态和解释器状态管理 |
| `pythonrun.c` | Python 运行时接口（交互式、脚本执行） |
| `import.c` | 模块导入系统核心实现 |
| `bltinmodule.c` | 内置模块（`__builtins__`）定义 |
| `marshal.c` | 字节码序列化/反序列化（`.pyc` 文件格式） |
| `dtoa.c` | 浮点数与字符串转换（David M. Gay 的 dtoa 库） |
| `pystrtod.c` | 字符串到浮点数转换 |
| `sysmodule.c` | `sys` 模块 |

## Modules/：C 内置模块

`Modules/` 目录包含用 C 实现的**内置模块和可选扩展模块**。与 `Objects/` 中的"核心类型"不同，这里的模块提供标准库功能但不必在核心启动路径上。

关键文件和子目录：

| 文件/目录 | 功能 |
|----------|------|
| `main.c` | CPython 程序入口点（`main()` 函数） |
| `gcmodule.c` | `gc` 模块（Python 层面的 GC 控制接口） |
| `_json.c` | `_json` 模块（JSON 编码/解码器的 C 加速实现） |
| `_pickle.c` | `_pickle` 模块（pickle 序列化的 C 加速） |
| `_io/` | I/O 系统（`fileio.c`、`iobase.c`、`textio.c`、`bytesio.c` 等） |
| `_sre/` | 正则表达式引擎（`sre.c`、`sre.h`） |
| `_ssl.c` | `_ssl` 模块（SSL/TLS 支持） |
| `_lsprof.c` | 性能分析器 |
| `_operator.c` | `operator` 模块的 C 实现 |
| `_weakref.c` | `_weakref` 模块（弱引用） |
| `_abc.c` | `_abc` 模块（抽象基类支持） |
| `_struct.c` | `struct` 模块（C 结构体打包/解包） |
| `_stat.c` | `stat` 模块（文件状态常量） |
| `mathmodule.c` | `math` 模块 |
| `cmathmodule.c` | `cmath` 模块（复数数学） |
| `zlibmodule.c` | `zlib` 压缩模块 |
| `sha2module.c`、`sha3module.c`、`md5module.c` | 哈希算法模块 |
| `binascii.c` | `binascii` 模块（二进制/ASCII 转换） |
| `timemodule.c` | `time` 模块 |
| `mmapmodule.c` | `mmap` 模块（内存映射文件） |
| `pyexpat.c` | Expat XML 解析器绑定 |
| `getpath.c`/`getpath.py` | 解释器路径探测 |
| `Setup` | 静态链接模块的编译配置文件 |

部分复杂模块拥有独立子目录，如 `_io/`、`_sre/`、`_ssl/`、`_tkinter.c`（Tkinter GUI 绑定）等。

## Lib/：Python 标准库

`Lib/` 目录包含用 Python 自身实现的**标准库**。这是 CPython 中最大的目录，涵盖了 Python 日常编程所用的大部分模块。

核心模块示例：

| 文件/目录 | 功能 |
|----------|------|
| `abc.py` | 抽象基类框架 |
| `os.py` | 操作系统接口 |
| `sys.py` | （启动时由 C 层创建，但 Lib/sys.py 提供补充） |
| `typing.py` | 类型注解支持 |
| `asyncio/` | 异步 I/O 框架 |
| `json/` | JSON 编码/解码（纯 Python 实现，C 加速在 `_json`） |
| `re/` | 正则表达式（纯 Python 实现，C 引擎在 `_sre`） |
| `collections/` | 容器数据类型 |
| `importlib/` | 导入系统（Python 层面的实现） |
| `unittest/` | 单元测试框架 |
| `test/` | CPython 自身的测试套件 |
| `pathlib/` | 面向对象的文件系统路径 |
| `concurrent/` | 并发执行（futures、多进程、多线程） |
| `multiprocessing/` | 多进程支持 |
| `xml/` | XML 处理 |
| `email/` | 邮件处理 |
| `http/` | HTTP 客户端/服务器 |
| `urllib/` | URL 处理 |
| `logging/` | 日志模块（如果存在的话；实际位于 logging 包） |
| `site.py` | 站点包初始化 |
| `pickle.py` | pickle 纯 Python 实现 |
| `dis.py` | 字节码反汇编 |
| `ast.py` | AST 辅助工具 |
| `inspect.py` | 内省工具 |
| `functools.py` | 高阶函数和可调用对象工具 |
| `itertools.py` | 迭代器工具 |
| `threading.py` | 线程模块 |

`Lib/test/` 目录尤其值得关注——它包含了 CPython 自身庞大的回归测试套件，是理解各种语言特性预期行为的绝佳参考。

## Grammar/ 和 Parser/：语法与解析器

### Grammar/

`Grammar/` 目录包含 Python 语言的**语法定义**：

- `python.gram`：Python 3 的 PEG（Parsing Expression Grammar）语法定义文件。CPython 从 3.9 开始使用 PEG 解析器替代了旧的 LL(1) 解析器。
- `Tokens`：词法分析器的 token 定义。

### Parser/

`Parser/` 目录包含 PEG 解析器的 C 实现，负责将源代码文本解析为抽象语法树（AST）。解析器的驱动代码、tokenizer、AST 节点构建等均在此目录。

## Doc/：官方文档

`Doc/` 目录包含 CPython 的**官方文档**源码，使用 reStructuredText 格式编写，通过 Sphinx 构建系统生成 HTML/PDF 等输出。主要子目录：

| 目录 | 内容 |
|------|------|
| `c-api/` | C API 参考手册（扩展模块开发者必读） |
| `library/` | 标准库参考 |
| `reference/` | 语言参考手册 |
| `tutorial/` | Python 教程 |
| `howto/` | 专题 HOWTO 指南 |
| `faq/` | 常见问题解答 |
| `whatsnew/` | 各版本新特性说明 |
| `using/` | 平台特定使用说明（Unix/macOS/Windows） |

## 快速找代码指南

当你想研究某个特定功能时，以下是"去哪里找"的快速索引：

| 想了解什么 | 去哪里找 |
|-----------|---------|
| 整数 `int` 的实现 | `Objects/longobject.c` |
| 浮点数 `float` 的实现 | `Objects/floatobject.c` |
| 字符串 `str` 的实现 | `Objects/unicodeobject.c` |
| 列表 `list` 的实现 | `Objects/listobject.c` |
| 字典 `dict` 的实现 | `Objects/dictobject.c` |
| 元组 `tuple` 的实现 | `Objects/tupleobject.c` |
| 集合 `set` 的实现 | `Objects/setobject.c` |
| 对象基础结构 | `Include/object.h`、`Include/cpython/object.h` |
| 字节码如何执行 | `Python/ceval.c` |
| 字节码指令语义 | `Python/bytecodes.c` |
| 源代码如何编译为字节码 | `Python/compile.c`、`Python/ast.c`、`Python/symtable.c`、`Python/flowgraph.c` |
| 垃圾回收器 | `Python/gc.c`、`Modules/gcmodule.c` |
| 引用计数和对象分配 | `Include/refcount.h`、`Objects/obmalloc.c` |
| 模块导入系统 | `Python/import.c`、`Lib/importlib/` |
| 解释器启动/关闭 | `Python/pylifecycle.c`、`Modules/main.c` |
| GIL 实现 | `Python/ceval_gil.c` |
| Python 语法定义 | `Grammar/python.gram` |
| 类型系统和描述符协议 | `Objects/typeobject.c` |
| 函数调用机制 | `Objects/call.c`、`Python/ceval.c` |
| C API 文档 | `Doc/c-api/` |
| 标准库模块 X | `Lib/X.py`（Python 实现）或 `Modules/X.c`/`Modules/_X.c`（C 实现） |

## 构建产物与生成文件

CPython 仓库中有些文件是**自动生成**的，不应手动编辑：

- `Python/generated_cases.c.h`：从 `Python/bytecodes.c` 生成的字节码分派代码
- `Include/opcode_ids.h`：从 `Include/opcode.h` 生成的操作码 ID
- `Lib/opcode.py`：从操作码定义生成的 Python 模块
- `Python/Python-ast.c` 和 `Include/Python-ast.h`：从 ASDL 语法定义生成的 AST C 代码

## 相关概念

- [CPython 简介](/concepts/00-introduction.md) — 项目概览与学习路径
- [对象模型：PyObject 与 PyVarObject](/concepts/02-object-model.md) — 一切 Python 值的底层结构
- [类型系统与 PyTypeObject](/concepts/03-type-system.md) — 类型对象的结构与方法套件
- [CPython 源码信源登记](/references/cpython-source.md) — 源码路径、版本信息、关键文件完整清单

[^cpython-source]: CPython 源码信源，见 [cpython-source.md](/references/cpython-source.md)。
