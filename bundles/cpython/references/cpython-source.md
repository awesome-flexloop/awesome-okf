---
type: Reference
title: CPython 源码信源登记
description: CPython 3.16.0a0 源码路径、版本信息、核心目录与关键文件清单
tags: [cpython, source, reference, v3.16, interpreter]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-21T16:51:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T17:30:00+08:00" }
status: stable
stale_after: 2027-08-21
sources:
  - id: cpython-github
    resource: https://github.com/python/cpython
    title: CPython GitHub 仓库
  - id: cpython-docs
    resource: https://docs.python.org/3/
    title: Python 官方文档
---

# CPython 源码信源登记

## 基本信息

| 属性 | 值 |
|------|-----|
| 项目名 | CPython |
| 版本 | **3.16.0a0**（开发版，alpha 0） |
| 描述 | Python 编程语言的官方 C 语言参考实现 |
| 维护者 | Python Software Foundation |
| 许可证 | PSF License v2（Python Software Foundation License） |
| 官方文档 | <https://docs.python.org/3/> |
| 源码仓库 | <https://github.com/python/cpython> |

## 版本标识

版本号定义于 `Include/patchlevel.h`：

```c
#define PY_MAJOR_VERSION        3
#define PY_MINOR_VERSION        16
#define PY_MICRO_VERSION        0
#define PY_RELEASE_LEVEL        PY_RELEASE_LEVEL_ALPHA  // 0xA
#define PY_RELEASE_SERIAL       0
#define PY_VERSION              "3.16.0a0"
```

发布级别常量：

| 常量 | 值 | 含义 |
|------|-----|------|
| `PY_RELEASE_LEVEL_ALPHA` | 0xA | Alpha 开发版 |
| `PY_RELEASE_LEVEL_BETA` | 0xB | Beta 测试版 |
| `PY_RELEASE_LEVEL_GAMMA` | 0xC | Release Candidate |
| `PY_RELEASE_LEVEL_FINAL` | 0xF | 正式发布版 |

## 源码位置

CPython 源码位于 SpecWeave 仓库的外部依赖目录：

```
external/libs/python/cpython/
```

## 核心目录结构

| 目录 | 用途 | 关键文件 |
|------|------|---------|
| `Include/` | 公共 C API 头文件 | `Python.h`（主入口）、`object.h`、`ceval.h`、`pylifecycle.h` |
| `Include/cpython/` | CPython 实现细节头文件 | `object.h`、`ceval.h`、`pylifecycle.h`、`funcobject.h` |
| `Include/internal/` | 内部私有头文件（`pycore_*.h`） | `pycore_object.h`、`pycore_ceval.h`、`pycore_pystate.h`、`pycore_frame.h` |
| `Objects/` | 内置对象类型实现 | `object.c`、`typeobject.c`、`dictobject.c`、`listobject.c`、`obmalloc.c` |
| `Python/` | 解释器核心 | `ceval.c`、`compile.c`、`pylifecycle.c`、`gc.c`、`import.c`、`pythonrun.c` |
| `Modules/` | C 实现的内置模块 | `main.c`、`gcmodule.c`、`_io/`、`_json.c`、`_pickle.c` |
| `Lib/` | Python 实现的标准库 | `abc.py`、`asyncio/`、`json/`、`os.py`、`typing.py` 等 |
| `Grammar/` | 语法定义 | `python.gram`、`Tokens` |
| `Parser/` | 解析器 | （PEG 解析器实现） |
| `Doc/` | 官方文档（reStructuredText） | `c-api/`、`library/`、`reference/`、`tutorial/` |
| `Misc/` | 杂项 | `stable_abi.toml`、`ACKS`、`HISTORY` |

## 关键文件清单

### 对象模型

| 文件 | 内容 |
|------|------|
| `Include/object.h` | PyObject、PyVarObject 结构体定义、对象宏 |
| `Include/cpython/object.h` | PyTypeObject 结构体完整定义、PyHeapTypeObject |
| `Include/pytypedefs.h` | 核心类型前向声明（PyObject、PyTypeObject、PyThreadState 等） |
| `Include/objimpl.h` | 对象内存分配 API（PyObject_New/Free 等） |
| `Include/refcount.h` | 引用计数宏（Py_INCREF、Py_DECREF、Py_CLEAR） |
| `Objects/object.c` | 对象通用操作实现（None/True/False 等通用对象） |
| `Objects/typeobject.c` | 类型对象实现、类型创建、MRO、描述符协议 |

### 内存管理

| 文件 | 内容 |
|------|------|
| `Include/pymem.h` | 底层内存分配 API（PyMem_Malloc/Free） |
| `Objects/obmalloc.c` | pymalloc 小对象分配器实现（arena/pool/block） |
| `Python/gc.c` | 分代垃圾回收器实现 |
| `Include/cpython/pymem.h` | pymem 内部接口 |

### 执行引擎

| 文件 | 内容 |
|------|------|
| `Include/ceval.h` | 评估器公共 API |
| `Include/cpython/ceval.h` | 评估器内部接口 |
| `Include/opcode.h` | 字节码指令操作码 ID 定义 |
| `Include/opcode_ids.h` | 操作码数字 ID |
| `Python/ceval.c` | 字节码解释主循环（_PyEval_EvalFrameDefault） |
| `Python/ceval_gil.c` | GIL 实现、待处理信号/调用处理 |
| `Python/bytecodes.c` | 字节码指令语义定义（DSL 形式） |
| `Python/generated_cases.c.h` | 自动生成的字节码 case 分支 |
| `Include/internal/pycore_interpframe_structs.h` | _PyInterpreterFrame 结构体定义 |

### 编译器

| 文件 | 内容 |
|------|------|
| `Include/cpython/code.h` | PyCodeObject 结构体定义 |
| `Python/compile.c` | 编译器主文件（AST → 字节码） |
| `Python/ast.c` | AST 节点创建与操作 |
| `Python/ast_unparse.c` | AST 反向生成源码 |
| `Python/symtable.c` | 符号表构建 |
| `Python/flowgraph.c` | 控制流图构建与基本块管理 |
| `Python/marshal.c` | 字节码序列化/反序列化（.pyc 文件格式） |
| `Python/assemble.c` | 代码对象汇编 |
| `Python/codegen.c` | 代码生成器 |

### 模块与导入

| 文件 | 内容 |
|------|------|
| `Include/moduleobject.h` | PyModuleObject 定义 |
| `Python/import.c` | 导入系统核心实现 |
| `Python/bltinmodule.c` | 内置模块（__builtins__）定义 |
| `Include/import.h` | 导入系统公共 API |

### 解释器状态与生命周期

| 文件 | 内容 |
|------|------|
| `Include/pystate.h` | PyInterpreterState、PyThreadState 公共定义 |
| `Include/cpython/pystate.h` | 解释器/线程状态内部接口 |
| `Include/internal/pycore_pystate.h` | 解释器状态内部细节 |
| `Include/pylifecycle.h` | 生命周期 API（Py_Initialize/Py_Finalize） |
| `Python/pylifecycle.c` | 解释器初始化与终结实现 |
| `Python/pystate.c` | 线程状态和解释器状态管理 |
| `Python/pythonrun.c` | Python 运行时接口（交互式、脚本执行） |

### 内置对象类型实现

| 文件 | 类型 |
|------|------|
| `Objects/longobject.c` | 整数（PyLongObject） |
| `Objects/floatobject.c` | 浮点数（PyFloatObject） |
| `Objects/unicodeobject.c` | 字符串（PyUnicodeObject） |
| `Objects/bytesobject.c` | 字节串（PyBytesObject） |
| `Objects/tupleobject.c` | 元组（PyTupleObject） |
| `Objects/listobject.c` | 列表（PyListObject） |
| `Objects/dictobject.c` | 字典（PyDictObject） |
| `Objects/setobject.c` | 集合（PySetObject） |
| `Objects/funcobject.c` | 函数（PyFunctionObject） |
| `Objects/frameobject.c` | 帧对象（PyFrameObject） |
| `Objects/codeobject.c` | 代码对象（PyCodeObject） |
| `Objects/moduleobject.c` | 模块对象（PyModuleObject） |
| `Objects/exceptions.c` | 内置异常类型 |
| `Objects/genobject.c` | 生成器/协程对象 |

## C API 入口点

C 扩展模块只需 `#include <Python.h>`，该元头文件按顺序引入所有公共头文件（定义于 `Include/Python.h`）：

1. 配置头：`patchlevel.h`、`pyconfig.h`、`pyabi.h`
2. 标准 C 库头：`assert.h`、`inttypes.h`、`limits.h`、`math.h` 等
3. Python 核心头：`pyport.h`、`pymem.h`、`pytypedefs.h`、`object.h`、`objimpl.h`、`refcount.h` 等
4. 对象类型头：`bytesobject.h`、`unicodeobject.h`、`longobject.h`、`listobject.h`、`dictobject.c` 等
5. 执行相关头：`ceval.h`、`compile.h`、`pythonrun.h`、`pylifecycle.h` 等
6. 其他：`import.h`、`abstract.h`、`bltinmodule.h` 等

## 构建系统

CPython 使用 autotools（`configure.ac` + `Makefile.pre.in`）在 Unix 平台构建，Windows 平台使用 `PCbuild/` 目录下的 MSBuild 项目。关键构建文件：

- `configure.ac` — autoconf 配置
- `Makefile.pre.in` — Makefile 模板
- `Modules/Setup` — 内置模块编译配置
- `pyproject.toml` — Python 包构建配置
