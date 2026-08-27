---
type: Example
title: 字节码剖析
description: 使用dis模块分析Python字节码——理解LOAD_FAST/STORE_FAST/CALL/RETURN_VALUE等指令如何执行Python代码
tags: [cpython, bytecode, dis, example, LOAD_FAST, CALL, stack, opcode]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-21T17:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T17:30:00+08:00" }
status: stable
stale_after: 2027-08-21
sources:
  - id: cpython-source
    resource: /references/cpython-source.md
---

# 字节码剖析

Python 源代码在执行前会被编译器编译为**字节码（bytecode）**——一种基于栈的低级指令集，由 CPython 虚拟机（CPython VM，又称 ceval 评估循环）逐条解释执行。Python 标准库提供了 `dis` 模块（disassembler，反汇编器），可以将函数、方法、类或代码对象反汇编为可读的字节码指令列表，帮助我们理解 Python 代码在虚拟机层面的实际执行方式。[^cpython-source]

本示例使用 `dis` 模块分析几个典型 Python 结构的字节码，涵盖栈操作模型、常见指令含义、CodeObject 属性访问，以及源代码与字节码的对应关系。

## 1. 最简函数：add(a, b)

从最简单的二元加法函数开始：

```python
import dis

def add(a, b):
    return a + b

dis.dis(add)
```

输出（CPython 3.12+，格式为「行号 → 字节偏移 → 指令名 → 参数 → 参数说明」）：

```
  4           0 RESUME                   0

  5           2 LOAD_FAST                0 (a)
              4 LOAD_FAST                1 (b)
              6 BINARY_OP                0 (+)
             10 RETURN_VALUE
```

### 1.1 输出列含义

| 列 | 含义 |
|----|------|
| 第一列（如 `4`、`5`） | 对应源代码的行号 |
| 第二列（如 `0`、`2`、`4`） | 字节偏移（byte offset），每条指令占 2 字节（wordcode 格式） |
| 第三列（如 `RESUME`、`LOAD_FAST`） | 指令名（opcode name） |
| 第四列（如 `0`、`1`） | 指令参数（oparg），整数编码 |
| 第五列（如 `(a)`、`(b)`、`(+)`） | 参数的人类可读解释（由 dis 模块解析） |

> **说明**：Python 3.11 之前字节偏移是递增的数字（每条指令 2 字节），3.11+ 部分指令带有内联缓存（cache entries），可能导致偏移跳跃。`RESUME` 是 3.11+ 引入的帧状态检查指令，无实际运算语义。

### 1.2 逐条指令解读

| 指令 | 栈效果 | 含义 |
|------|--------|------|
| `RESUME 0` | — | 帧状态检查点，调试/追踪用；无栈操作 |
| `LOAD_FAST 0 (a)` | push `a` | 将局部变量槽 0（即参数 `a`）压入求值栈（value stack） |
| `LOAD_FAST 1 (b)` | push `b` | 将局部变量槽 1（即参数 `b`）压入栈 |
| `BINARY_OP 0 (+)` | pop `b`, pop `a`; push `a+b` | 弹出栈顶两个值执行二元加法，将结果压回栈 |
| `RETURN_VALUE` | pop `result` | 将栈顶值作为函数返回值返回给调用者 |

### 1.3 栈状态追踪

`add(3, 4)` 执行时的栈变化过程（栈底在左，栈顶在右）：

```
RESUME:            []
LOAD_FAST a:       [3]
LOAD_FAST b:       [3, 4]
BINARY_OP +:       [7]       ← 弹出 4 和 3，计算 3+4=7，压入
RETURN_VALUE:      → 返回 7
```

CPython 虚拟机是**栈式虚拟机（stack machine）**：所有运算操作数来自栈顶，结果也写回栈顶，不使用通用寄存器。

## 2. 列表推导式：make_list(n)

分析一个列表推导式（list comprehension）的字节码：

```python
def make_list(n):
    return [i * 2 for i in range(n)]

dis.dis(make_list)
```

输出（简化展示，省略部分缓存偏移）：

```
  8           0 RESUME                   0

  9           2 LOAD_GLOBAL              1 (NULL + range)
             12 LOAD_FAST                0 (n)
             14 CALL                     1
             22 GET_ITER
        >>   24 FOR_ITER                 7 (to 42)
             28 STORE_FAST               1 (i)
             30 LOAD_FAST                1 (i)
             32 LOAD_CONST               1 (2)
             34 BINARY_OP                5 (*)
             38 LIST_APPEND              2
             40 JUMP_BACKWARD            9 (to 24)
        >>   42 RETURN_VALUE
```

### 2.1 新增指令解读

| 指令 | 含义 |
|------|------|
| `LOAD_GLOBAL 1 (NULL + range)` | 将 `NULL` 和全局名 `range` 压入栈。3.12+ 版本中，`LOAD_GLOBAL` 会自动压入一个 `NULL` 作为方法调用的 self 占位 |
| `CALL 1` | 调用栈顶函数，1 表示有 1 个位置参数。栈上是 `[NULL, range, n]` → 弹出 `n`、`range`、`NULL`，调用 `range(n)`，结果压栈 |
| `GET_ITER` | 弹出栈顶的可迭代对象，调用 `iter()` 获取迭代器，压回栈 |
| `FOR_ITER 7 (to 42)` | 调用迭代器的 `__next__()`；若有值则压入栈顶并继续；若耗尽（StopIteration）则跳转到偏移 42 |
| `STORE_FAST 1 (i)` | 弹出栈顶值（当前迭代元素），存入局部变量槽 1（`i`） |
| `LOAD_CONST 1 (2)` | 从常量表（`co_consts`）加载常量 `2` 压入栈 |
| `LIST_APPEND 2` | 将栈顶元素追加到列表（栈上第二个元素）；参数 2 表示从栈顶向下数，列表在 TOS1 位置 |
| `JUMP_BACKWARD 9 (to 24)` | 向后跳转到偏移 24（即 FOR_ITER 处），继续循环 |

### 2.2 列表推导式的栈追踪

以 `make_list(3)` 为例，推导 `[0, 2, 4]`：

```
初始（LOAD_GLOBAL + LOAD_FAST + CALL后）：
  栈: [range_iterator]   ← range(3) 的迭代器
  GET_ITER: [range_iterator]  (迭代器本身)

第1轮 (i=0):
  FOR_ITER: [range_iterator, 0]
  STORE_FAST i: [range_iterator]           （i=0 存入局部变量）
  LOAD_FAST i: [range_iterator, 0]
  LOAD_CONST 2: [range_iterator, 0, 2]
  BINARY_OP *: [range_iterator, 0]         （0*2=0）
  LIST_APPEND: [range_iterator]            （0 追加到隐式列表）
  JUMP_BACKWARD → FOR_ITER

第2轮 (i=1):
  ... 类似，追加 2 ...

第3轮 (i=2):
  ... 追加 4 ...

第4次 FOR_ITER (迭代器耗尽):
  跳转到 42，栈顶是完成的列表 [0,2,4]
  RETURN_VALUE → 返回 [0,2,4]
```

> 注意：列表推导式中的「隐式列表」由虚拟机在进入推导式前隐式创建（通过 `BUILD_LIST`，在优化版字节码中可能以特殊方式处理），`LIST_APPEND` 直接操作它。

## 3. 类定义：简单类的字节码

类定义也会产生字节码，因为类体在 `class` 语句处执行：

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def origin(cls):
        return cls(0, 0)

dis.dis(Point)
```

输出显示类定义本身不产生函数内字节码，类内方法是独立的代码对象。查看类的创建代码需要反汇编包含 `class` 语句的外层作用域：

```python
def make_point_class():
    class Point:
        def __init__(self, x, y):
            self.x = x
            self.y = y
    return Point

dis.dis(make_point_class)
```

输出中可以看到 `MAKE_FUNCTION`、`LOAD_BUILD_CLASS`、`CALL` 等指令用于构建类对象。

### 3.1 方法的字节码

直接反汇编 `__init__` 方法：

```python
dis.dis(Point.__init__)
```

```
 11           0 RESUME                   0

 12           2 LOAD_FAST                1 (x)
              4 LOAD_FAST                0 (self)
              6 STORE_ATTR               0 (x)

 13           8 LOAD_FAST                2 (y)
             10 LOAD_FAST                0 (self)
             12 STORE_ATTR               1 (y)
             14 LOAD_CONST               0 (None)
             16 RETURN_VALUE
```

| 指令 | 含义 |
|------|------|
| `STORE_ATTR 0 (x)` | 弹出值 `x` 和对象 `self`，执行 `self.x = x`（调用 `__setattr__`） |
| 末尾 `LOAD_CONST None + RETURN_VALUE` | `__init__` 没有显式 return，默认返回 `None` |

## 4. 核心指令速查

| 类别 | 指令 | 栈效果 | 说明 |
|------|------|--------|------|
| **局部变量** | `LOAD_FAST i` | push `locals[i]` | 加载局部变量（参数或函数内变量） |
| | `STORE_FAST i` | pop `v` | 弹出值存入局部变量槽 `i` |
| **常量/全局** | `LOAD_CONST i` | push `consts[i]` | 从 `co_consts` 加载常量（数字、字符串、None 等） |
| | `LOAD_GLOBAL i` | push `NULL, globals[name]` | 加载全局变量（3.12+ 压入 NULL 用于调用） |
| | `STORE_GLOBAL i` | pop `v` | 存储到全局变量 |
| **二元运算** | `BINARY_OP op` | pop `b`, pop `a`; push `a op b` | 二元操作（+、-、*、/、//、%、&、\| 等），op 参数编码操作类型 |
| **比较** | `COMPARE_OP op` | pop `b`, pop `a`; push `a op b` | 比较操作（==、!=、<、<=、>、>=、is、in 等） |
| **栈操作** | `POP_TOP` | pop | 丢弃栈顶 |
| | `PUSH_NULL` | push `NULL` | 压入 NULL（用于方法调用约定） |
| | `DUP_TOP` | push TOS | 复制栈顶 |
| | `SWAP n` | 交换 TOS 与 TOSn | 交换栈中位置（3.12+） |
| **属性/子脚本** | `LOAD_ATTR i` | pop `obj`; push `obj.attr` | 加载属性 |
| | `STORE_ATTR i` | pop `v`, pop `obj` | 设置属性 `obj.attr = v` |
| | `BINARY_SUBSCR` | pop `k`, pop `obj`; push `obj[k]` | 下标读取 `obj[k]` |
| | `STORE_SUBSCR` | pop `v`, pop `k`, pop `obj` | 下标设置 `obj[k] = v` |
| **调用** | `CALL n` | pop args..., pop callable; push result | 函数调用，n 个位置参数 |
| | `CALL_FUNCTION_EX flags` | 高级调用（带 *args/**kwargs） |
| **控制流** | `JUMP_FORWARD/JUMP_BACKWARD off` | — | 无条件跳转 |
| | `POP_JUMP_IF_TRUE/JUMP_IF_FALSE off` | pop `v` | 弹出值，根据真假跳转 |
| | `FOR_ITER off` | push next 或 jump | 迭代器步进 |
| | `RETURN_VALUE` | pop `v` → return | 函数返回 |
| **数据结构** | `BUILD_LIST n` | pop n items; push list | 从 n 个栈元素构建列表 |
| | `LIST_APPEND i` | append TOS to TOSi | 列表追加（推导式专用） |
| | `BUILD_TUPLE n` | pop n items; push tuple | 构建元组 |
| | `BUILD_MAP n` | pop 2n items; push dict | 构建字典 |
| | `DICT_MERGE` / `DICT_UPDATE` | 字典合并 |
| **其他** | `NOP` | — | 空操作（占位用） |
| | `RESUME` | — | 帧检查点（3.11+） |

## 5. CodeObject 深度访问

`dis.dis()` 只是反汇编的高层接口。底层可以直接访问**代码对象（code object）**的属性，它是 CPython 编译后的不可变数据结构，包含字节码和所有相关元数据。

```python
import dis

def add(a, b):
    return a + b

# 获取函数的 __code__ 属性（即 PyCodeObject）
code = add.__code__

print(f"co_name:       {code.co_name}")       # 函数名 'add'
print(f"co_argcount:   {code.co_argcount}")    # 位置参数个数 2
print(f"co_varnames:   {code.co_varnames}")    # 局部变量名元组 ('a', 'b')
print(f"co_consts:     {code.co_consts}")      # 常量元组 (None,) （简单加法无额外常量）
print(f"co_names:      {code.co_names}")       # 使用的名字元组 ()
print(f"co_filename:   {code.co_filename}")    # 源文件路径
print(f"co_firstlineno:{code.co_firstlineno}") # 第一行行号

# co_code 是原始字节码（bytes 对象）
print(f"co_code:       {code.co_code.hex()}")  # 原始字节的十六进制表示

# co_lnotab（3.10-）/ co_linetable（3.10+）编码行号到字节偏移的映射
print(f"co_linetable:  {code.co_linetable.hex()}")

# dis.Bytecode 提供迭代器接口，逐条返回 Instruction 对象
print("\n--- Bytecode 指令迭代 ---")
for instr in dis.Bytecode(add):
    print(f"  offset={instr.offset:3d}  opname={instr.opname:<20} arg={instr.arg!r:<6} argrepr={instr.argrepr}")
```

### 5.1 常用 CodeObject 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `co_name` | `str` | 代码对象的名称（函数名、类名、`<module>`） |
| `co_argcount` | `int` | 位置参数个数（不含 *args/**kwargs） |
| `co_varnames` | `tuple[str]` | 局部变量名（含参数，按槽位顺序排列） |
| `co_consts` | `tuple` | 字面量常量表（数字、字符串、None、嵌套代码对象等） |
| `co_names` | `tuple[str]` | 全局/属性名字表（LOAD_GLOBAL、LOAD_ATTR 等通过索引引用） |
| `co_cellvars` | `tuple[str]` | 闭包中被内层引用的变量名 |
| `co_freevars` | `tuple[str]` | 闭包中来自外层作用域的变量名 |
| `co_code` | `bytes` | 原始字节码指令序列 |
| `co_flags` | `int` | 标志位（CO_OPTIMIZED、CO_VARARGS 等） |
| `co_stacksize` | `int` | 编译器计算的最大栈深度 |
| `co_filename` | `str` | 源文件名 |
| `co_firstlineno` | `int` | 代码起始行号 |

## 6. 完整可运行脚本

将上述分析整合为一个可直接运行的脚本：

```python
#!/usr/bin/env python3
"""字节码剖析示例：使用 dis 模块分析 Python 字节码"""
import dis

# ========== 示例1：简单加法函数 ==========
def add(a, b):
    return a + b

print("=" * 60)
print("1. add(a, b) -> a + b")
print("=" * 60)
dis.dis(add)

# ========== 示例2：列表推导式 ==========
def make_list(n):
    return [i * 2 for i in range(n)]

print("\n" + "=" * 60)
print("2. make_list(n) -> [i*2 for i in range(n)]")
print("=" * 60)
dis.dis(make_list)

# ========== 示例3：简单类的 __init__ ==========
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

print("\n" + "=" * 60)
print("3. Point.__init__")
print("=" * 60)
dis.dis(Point.__init__)

# ========== 示例4：条件分支 ==========
def abs_value(x):
    if x < 0:
        return -x
    return x

print("\n" + "=" * 60)
print("4. abs_value(x) —— 条件分支")
print("=" * 60)
dis.dis(abs_value)

# ========== 示例5：CodeObject 属性 ==========
print("\n" + "=" * 60)
print("5. add() 的 CodeObject 属性")
print("=" * 60)
code = add.__code__
print(f"co_name:       {code.co_name}")
print(f"co_argcount:   {code.co_argcount}")
print(f"co_varnames:   {code.co_varnames}")
print(f"co_consts:     {code.co_consts}")
print(f"co_stacksize:  {code.co_stacksize}")
print(f"co_flags:      {code.co_flags:#x}")

# ========== 示例6：Instruction 对象迭代 ==========
print("\n" + "=" * 60)
print("6. 逐条指令遍历 make_list")
print("=" * 60)
for instr in dis.Bytecode(make_list):
    print(f"  L{instr.starts_line or '':>3}  {instr.offset:3d}  {instr.opname:<20} {instr.arg!r:<5} {instr.argrepr}")
```

运行此脚本：

```bash
python bytecode_dissection.py
```

## 7. 实用提示

- **`dis.dis(func)`**：反汇编函数、方法、生成器、协程、类、模块、代码对象或源码字符串
- **`dis.code_info(obj)`**：以字符串形式返回代码对象的详细信息（标志位、参数、栈大小、常量等）
- **`dis.Bytecode(func)`**：返回可迭代的 `Instruction` 对象序列，适合编程式分析
- **`dis.opmap`**：字典，将指令名映射为操作码数字 ID（如 `dis.opmap['LOAD_FAST'] == 124`）
- **`dis.opname`**：列表，将操作码数字 ID 映射为指令名（如 `dis.opname[124] == 'LOAD_FAST'`）
- 不同 Python 版本的字节码不兼容：`.pyc` 文件头包含魔术数字（magic number）用于版本校验
- 字节码是 CPython 的实现细节：其他 Python 实现（PyPy、Jython）可能使用完全不同的执行模型

## 相关概念

* [字节码执行（§7）](../concepts/07-bytecode-execution.md)
* [编译器流水线（§8）](../concepts/08-compiler-pipeline.md)
* [解释器与栈帧（§6）](../concepts/06-interpreter-frame.md)
* [对象模型（§2）](../concepts/02-object-model.md)
* [CPython 源码信源登记](../references/cpython-source.md)

[^cpython-source]: CPython 3.16.0a0 源码，字节码定义于 `Include/opcode.h`、`Include/opcode_ids.h`，解释主循环位于 `Python/ceval.c`（`_PyEval_EvalFrameDefault`），指令语义定义于 `Python/bytecodes.c`，反汇编器为标准库 `Lib/dis.py`，见本 bundle 信源登记 [references/cpython-source.md](../references/cpython-source.md)。
