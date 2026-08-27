---
type: Concept
title: "编译器流水线"
description: "CPython编译器的五阶段流水线——源码→Tokenizer→Parser→AST→符号表→CFG→字节码→PyCodeObject"
tags: [cpython, compiler, ast, bytecode, code-object, marshal, pyc]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-21T16:58:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T17:30:00+08:00" }
status: stable
stale_after: 2027-08-21
sources:
  - id: cpython-source
    resource: /references/cpython-source.md
---

# 编译器流水线

CPython 并不是一个"纯解释器"。在执行 Python 源代码之前，它会先经过一个多阶段的编译流程，将源代码转换为字节码（bytecode），再由字节码执行引擎解释执行。理解编译流水线有助于理解 Python 的执行模型、作用域规则和性能特征。

## 编译 vs 解释

一个常见的误解是"Python 是解释型语言所以不编译"。实际上 CPython 的执行模型是**先编译后解释**：

1. 源代码（`.py` 文件）被编译为字节码
2. 字节码由虚拟机逐条解释执行

与 C/C++ 等静态编译语言的区别在于：
- Python 的编译发生在**运行时**（导入模块时），而非构建时
- 编译产物（字节码）是平台无关的中间表示，而非机器码
- 编译过程不做类型检查（类型错误在运行时暴露）

编译后的字节码可以缓存到 `.pyc` 文件中（位于 `__pycache__/` 目录），避免重复编译。

## 五阶段编译流程

CPython 编译器可以划分为五个主要阶段：

```
源代码（字符串）
    │
    ▼
[阶段1] Tokenizer（词法分析）── Python/tokenizer.c
    │  输出：token 流
    ▼
[阶段2] Parser（语法分析）── Parser/pegen.c, Grammar/python.gram
    │  输出：AST（抽象语法树）
    ▼
[阶段3] Symbol Table（符号表）── Python/symtable.c
    │  输出：符号表（作用域、变量绑定信息）
    ▼
[阶段4] Flow Graph（控制流图）── Python/flowgraph.c, Python/codegen.c
    │  输出：基本块 + 跳转关系（CFG）
    ▼
[阶段5] Code Generation（代码生成）── Python/assemble.c
    │  输出：PyCodeObject（字节码 + 常量/名称/行号表等元数据）
    ▼
字节码执行引擎（Python/ceval.c）
```

### 阶段1：Tokenizer（词法分析）

词法分析器（Tokenizer，也叫 Lexer）将源代码字符串拆分为一系列 **token**（词法单元）。每个 token 包含类型和值：

| 源码 | Token 类型 | Token 值 |
|------|-----------|---------|
| `def` | NAME/KEYWORD | `def` |
| `foo` | NAME | `foo` |
| `(` | LPAR | `(` |
| `42` | NUMBER | `42` |
| `+` | PLUS | `+` |
| `"hello"` | STRING | `"hello"` |
| `:` | COLON | `:` |
| 换行 | NEWLINE | — |
| 缩进 | INDENT/DEDENT | 缩进层级变化 |

Tokenizer 的核心实现在 `Python/tokenizer.c` 中。它还负责处理：
- **编码声明**（PEP 263：`# -*- coding: utf-8 -*-`）
- **续行符**（`\` 和隐式续行括号）
- **注释**（`#` 开头到行尾）
- **缩进/退格**（INDENT/DEDENT token，Python 用缩进表示块结构）
- **f-string** 解析（Python 3.12+ 的新 f-string 解析器）

### 阶段2：Parser（语法分析）

语法分析器使用 **PEG（Parsing Expression Grammar）** 解析器（从 CPython 3.9 开始替换了旧的 LL(1) 解析器），将 token 流构建为 **AST**（Abstract Syntax Tree，抽象语法树）。

PEG 语法定义在 `Grammar/python.gram` 文件中，例如函数定义的规则：

```
// Grammar/python.gram（简化示例）
function_def[stmt_ty]:
    | decorators function_def_raw[funcdef] { ... }
    | function_def_raw[funcdef]

function_def_raw[stmt_ty]:
    | 'def' n=NAME '(' params=[params_type_kwargs] ')' a=['->' expression] ':' b=block {
        _PyAST_FunctionDef(n, params, b, ...)
    }
```

解析器根据语法规则匹配 token 流，调用 AST 节点构造函数（如 `_PyAST_FunctionDef`）构建树结构。AST 节点类型定义在 `Include/Python-ast.h` 和 `Python/Python.asdl`（ASDL 语法描述语言）中。

AST 节点示例——`def foo(x, y=1): return x + y` 的 AST 大致结构：

```
FunctionDef(
    name='foo',
    args=arguments(
        args=[arg(arg='x'), arg(arg='y')],
        defaults=[Constant(value=1)]
    ),
    body=[Return(
        value=BinOp(
            left=Name(id='x', ctx=Load()),
            op=Add(),
            right=Name(id='y', ctx=Load())
        )
    )]
)
```

AST 相关操作在 `Python/ast.c` 中实现，包括节点创建、遍历、复制、压缩（AST 优化）等。

### 阶段3：Symbol Table（符号表）

符号表阶段分析 AST 中所有变量的**作用域**和**绑定关系**，确定每个名称是局部变量、闭包变量（free variable）、全局变量还是内置名称。

符号表的入口函数是 `_PySymtable_BuildObject`（在 `Python/symtable.c` 中）：

```c
// Python/symtable.c
struct symtable *
_PySymtable_BuildObject(mod_ty mod, PyObject *filename, PyFutureFeatures *future)
```

符号表构建过程解决以下问题：

1. **作用域确定**：每个函数/类/生成器/推导式创建新的作用域
2. **global/nonlocal 声明处理**：`global x` 将 x 绑定到模块作用域，`nonlocal x` 绑定到外层闭包作用域
3. **变量分类**：
   - **LOCAL**：当前作用域赋值的变量
   - **GLOBAL_IMPLICIT**：引用但未赋值的变量（最终在全局/内置作用域查找）
   - **GLOBAL_EXPLICIT**：`global` 声明的变量
   - **FREE**：闭包中外层函数的局部变量
   - **CELL**：被内层闭包引用的局部变量
4. **参数与局部变量计数**：确定 `co_nlocals`（局部变量数量）、`co_argcount`（参数数量）

符号表的结果是一棵 `PySTEntryObject` 树，每个作用域对应一个条目，包含该作用域内所有标识符及其 `_Py_ScopeType` 和 `_Py_IdentifierFlag`。

### 阶段4：Flow Graph（控制流图）

代码生成阶段首先将 AST 转换为**控制流图**（Control Flow Graph, CFG）。CFG 由**基本块**（basic block）组成，每个基本块是一段顺序执行的指令序列，块内没有分支（分支只发生在块的末尾）。

控制流图的构建和优化在 `Python/flowgraph.c` 和 `Python/codegen.c` 中实现。入口函数是 `_PyAST_Compile`（在 `Python/compile.c` 中）：

```c
// Python/compile.c
PyCodeObject *
_PyAST_Compile(mod_ty mod, PyObject *filename, PyCompilerFlags *flags,
               int optimize, PyArena *arena)
```

CFG 构建过程包括：
- 遍历 AST，为每个节点生成对应的字节码指令，追加到当前基本块
- 遇到分支（if/for/while/break/continue/return/异常处理）时，创建新基本块并添加跳转边
- 计算每个基本块的栈深度（用于确定 `co_stacksize`）

CFG 优化包括：
- **死代码消除**（unreachable code elimination）：移除不可达的基本块
- **跳转线程化**（jump threading）：将跳转到跳转的指令直接跳转到最终目标
- **常量折叠**（constant folding）：在编译期计算常量表达式（如 `2 + 3` → `5`）
- **冗余 NOP 移除**

### 阶段5：Code Generation（代码生成）

代码生成阶段（由 `Python/assemble.c` 中的 `assemble` 函数实现）将 CFG 的基本块线性化，生成最终的字节码指令序列，并组装为 `PyCodeObject`：

1. **基本块线性化**：按照深度优先遍历顺序排列基本块，在适当位置插入跳转指令
2. **偏移计算**：为每条指令计算其在最终字节码序列中的偏移
3. **跳转目标回填**：将基本块引用替换为具体的字节码偏移
4. **异常表构建**：将 try-except 块信息编码为异常表（`co_exceptiontable`）
5. **行号表构建**：构建字节码偏移到源码行号的映射（`co_linetable`/`co_lnotab`）

## 关键文件索引

| 文件 | 职责 |
|------|------|
| `Python/ast.c` | AST 节点创建、遍历、复制、压缩优化 |
| `Python/symtable.c` | 符号表构建、作用域分析、变量分类 |
| `Python/flowgraph.c` | CFG 基本块管理、跳转图操作 |
| `Python/compile.c` | 编译器主体，`_PyAST_Compile` 入口，编译器选项处理 |
| `Python/assemble.c` | 代码对象汇编：基本块线性化、偏移回填、异常表生成 |
| `Python/codegen.c` | 代码生成器：AST → CFG 的指令发射 |
| `Python/marshal.c` | 字节码序列化/反序列化（.pyc 文件读写） |
| `Parser/pegen.c` | PEG 解析器实现 |
| `Grammar/python.gram` | PEG 语法定义 |
| `Python/tokenizer.c` | 词法分析器实现 |

## PyCodeObject：编译产物

编译的最终产物是 `PyCodeObject`（代码对象），定义在 `Include/cpython/code.h`。它包含了执行一段代码所需的全部信息：

```c
// Include/cpython/code.h（简化版）
typedef struct {
    PyObject_HEAD
    int co_argcount;            // 位置参数数量
    int co_posonlyargcount;     // 仅限位置参数数量
    int co_kwonlyargcount;      // 仅限关键字参数数量
    int co_nlocals;             // 局部变量数量（含参数）
    int co_stacksize;           // 需要的最大操作数栈深度
    int co_flags;               // 标志位（CO_OPTIMIZED, CO_GENERATOR 等）
    PyObject *co_code;          // 字节码指令序列（bytes 对象）
    PyObject *co_consts;        // 常量元组（字面量、嵌套代码对象等）
    PyObject *co_names;         // 名称元组（全局/属性名等）
    PyObject *co_varnames;      // 局部变量名元组（参数名在前）
    PyObject *co_freevars;      // 自由变量名元组（闭包引用的外层变量）
    PyObject *co_cellvars;      // 单元变量名元组（被内层引用的变量）
    PyObject *co_exceptiontable;// 异常处理表（bytes 对象）
    // ... 行号表、文件名、代码块名等
} PyCodeObject;
```

### co_flags 标志位

`co_flags` 是位掩码，描述代码对象的特性：

| 标志 | 含义 |
|------|------|
| `CO_OPTIMIZED` | 使用快速局部变量（函数/生成器/协程） |
| `CO_NEWLOCALS` | 执行时创建新的 locals 字典 |
| `CO_VARARGS` | 有 `*args` 参数 |
| `CO_VARKEYWORDS` | 有 `**kwargs` 参数 |
| `CO_GENERATOR` | 生成器函数（含 yield） |
| `CO_COROUTINE` | 协程函数（async def） |
| `CO_ITERABLE_COROUTINE` | 可迭代协程（@types.coroutine 装饰的生成器） |
| `CO_ASYNC_GENERATOR` | 异步生成器（async def + yield） |
| `CO_NESTED` | 嵌套函数/类 |
| `CO_FUTURE_*` | `from __future__ import` 启用的特性 |

### 常量池与名称表

- **co_consts**：代码中使用的所有常量，按索引访问。包括整数、浮点数、字符串字面量、`None`/`True`/`False`、以及嵌套函数/类/推导式的 `PyCodeObject`。
- **co_names**：通过名称访问的全局变量和属性名（如 `LOAD_GLOBAL`、`LOAD_ATTR` 使用）。
- **co_varnames**：局部变量名，按槽位索引对应 `fastlocals` 数组。参数在前，其余局部变量按出现顺序排列。

## marshal 序列化与 .pyc 文件

`PyCodeObject` 通过 `marshal` 模块序列化为字节流，写入 `.pyc` 文件（Python Compiled），实现编译缓存：

```c
// Python/marshal.c 中的序列化
void PyMarshal_WriteObjectToFile(PyObject *ob, FILE *fp, int version);
PyObject *PyMarshal_ReadObjectFromFile(FILE *fp);
```

`.pyc` 文件结构：

| 偏移 | 内容 |
|------|------|
| 0~3 | 魔法数（magic number）：标识字节码版本，不匹配则重新编译 |
| 4~7 | 标志位（PEP 552 哈希校验/时间戳模式） |
| 8~11 | 源文件时间戳或源码哈希 |
| 12~ | marshal 序列化的 PyCodeObject 字节流 |

`marshal` 使用类型标记（type tag）编码对象类型：

```c
// 类型标记示例（Python/marshal.c）
#define TYPE_NULL       '0'
#define TYPE_NONE       'N'
#define TYPE_FALSE      'F'
#define TYPE_TRUE       'T'
#define TYPE_INT        'i'
#define TYPE_STRING     's'
#define TYPE_CODE       'c'   // PyCodeObject
#define TYPE_TUPLE      '('
#define TYPE_LIST       '['
#define TYPE_DICT       '{'
```

序列化 `TYPE_CODE` 时，依次写入 `co_argcount`、`co_nlocals`、`co_stacksize`、`co_flags`、`co_code`、`co_consts`、`co_names`、`co_varnames`、`co_freevars`、`co_cellvars`、`co_filename`、`co_name` 等所有字段。

## PyCodeObject 与 _PyInterpreterFrame 的关系

理解编译产物和运行时实例的区分至关重要：

| 概念 | 类比 | 特性 |
|------|------|------|
| **PyCodeObject** | 程序的"蓝图"或"菜谱" | 编译时创建、只读、可共享、无执行状态 |
| **_PyInterpreterFrame** | 蓝图的"一次执行实例" | 运行时创建、可变、每次调用独立、包含 PC/栈/局部变量 |

同一段代码（同一个 `PyCodeObject`）可以被多次调用，每次调用创建一个新的帧。例如递归函数每次递归都创建新帧，但它们共享同一个代码对象。

编译入口的公共 C API 是 `Py_CompileString` 和 `PyAST_Compile`，前者直接从源代码字符串编译，后者从已构建的 AST 编译。

## 相关概念

- [字节码执行引擎](07-bytecode-execution.md) — 编译器输出字节码，执行引擎消费字节码，二者是生产者-消费者关系
- [解释器帧与执行栈](06-interpreter-frame.md) — _PyInterpreterFrame 是 PyCodeObject 的运行时实例
- [模块与导入系统](09-module-import.md) — 导入模块时触发编译流程，.pyc 文件缓存由导入系统管理
- [CPython 源码信源登记](../references/cpython-source.md) — `Python/compile.c`、`Python/ast.c`、`Python/marshal.c` 等关键文件的路径索引
