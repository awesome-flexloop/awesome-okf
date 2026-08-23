---
type: Concept
title: "解释器帧与执行栈"
description: "_PyInterpreterFrame栈帧结构——局部变量、操作数栈、帧链、帧所有者类型、栈操作内联函数"
tags: [cpython, frame, stack, interpreter, _PyInterpreterFrame, locals, operand-stack]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-21T16:55:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T17:30:00+08:00" }
status: stable
stale_after: 2027-08-21
sources:
  - id: cpython-source
    resource: /references/cpython-source.md
---

# 解释器帧与执行栈

每次 Python 函数调用都会创建一个**栈帧**（stack frame），用于保存该次调用的执行状态：局部变量、操作数栈、当前执行到哪条字节码指令、指向前一个调用者帧的指针等。CPython 3.11+ 引入了新的 `_PyInterpreterFrame` 结构（区别于旧的 `PyFrameObject`），它是解释器内部使用的轻量级帧，存储在线程的数据栈（datastack）上，极大地提升了函数调用性能。

## 什么是栈帧

栈帧是函数调用的执行上下文。当解释器执行一个函数时：

1. 在当前线程的数据栈上为新帧分配空间
2. 初始化帧的字段（代码对象、全局/内置命名空间、指令指针等）
3. 将新帧链接到当前帧链的顶端
4. 开始执行新帧的字节码

当函数返回时，弹出当前帧，恢复调用者帧的执行状态。这个帧链就是 Python 的**调用栈**（call stack）。

## _PyInterpreterFrame 结构体

`_PyInterpreterFrame` 定义在 `Include/internal/pycore_interpframe_structs.h`：

```c
struct _PyInterpreterFrame {
    _PyStackRef f_executable;          // 代码对象（强/延迟引用，_PyStackRef）
    struct _PyInterpreterFrame *previous;  // 指向前一帧（帧链）
    _PyStackRef f_funcobj;             // 函数对象（非C栈帧时有效）
    PyObject *f_globals;               // 全局命名空间（借用引用）
    PyObject *f_builtins;              // 内置命名空间（借用引用）
    PyObject *f_locals;                // locals字典（强引用，可为NULL）
    PyFrameObject *frame_obj;          // 对应的PyFrameObject（懒创建）
    _Py_CODEUNIT *instr_ptr;           // 当前执行指令指针
    _PyStackRef *stackpointer;         // 栈顶指针
    uint16_t return_offset;            // 调用返回偏移
    char owner;                        // 帧所有者类型（_frameowner枚举）
    uint8_t visited;                   // GC遍历标记
    _PyStackRef localsplus[1];         // 柔性数组：局部变量 + 操作数栈
};
```

### 各字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `f_executable` | `_PyStackRef` | 代码对象（`PyCodeObject`）或 `None`，包含字节码、常量、变量名等 |
| `previous` | `_PyInterpreterFrame*` | 指向调用者帧，形成帧链；最底层为 `NULL`（或哨兵帧） |
| `f_funcobj` | `_PyStackRef` | 对应的函数对象（`PyFunctionObject`） |
| `f_globals` | `PyObject*` | 全局命名空间字典（`globals()`），借用引用不增减引用计数 |
| `f_builtins` | `PyObject*` | 内置命名空间字典（`__builtins__`），借用引用 |
| `f_locals` | `PyObject*` | locals 字典，通常在需要时才创建（如调用 `locals()`），强引用 |
| `frame_obj` | `PyFrameObject*` | 对应的 Python 层面的帧对象，**懒创建**——仅在需要时（如 `sys._getframe()`）才会分配 `PyFrameObject` |
| `instr_ptr` | `_Py_CODEUNIT*` | 当前正在执行（或即将执行）的字节码指令指针 |
| `stackpointer` | `_PyStackRef*` | 操作数栈栈顶指针，指向第一个空闲槽位 |
| `return_offset` | `uint16_t` | 函数调用返回后，在调用者帧中恢复执行的指令偏移 |
| `owner` | `char` | 帧所有者类型，决定帧的生命周期管理方式 |
| `visited` | `uint8_t` | GC 遍历帧栈时使用的标记位 |
| `localsplus[1]` | `_PyStackRef[]` | 柔性数组（flexible array member），存储局部变量和操作数栈 |

注意：在自由线程构建（`Py_GIL_DISABLED`）中，还有一个额外的 `tlbc_index` 字段（线程局部字节码索引）。

## 帧所有者类型

帧的 `owner` 字段是一个 `_frameowner` 枚举值，定义在 `Include/internal/pycore_interpframe_structs.h`：

```c
enum _frameowner {
    FRAME_OWNED_BY_THREAD = 0,         // 线程持有（C栈上的普通帧）
    FRAME_OWNED_BY_GENERATOR = 1,      // 生成器持有
    FRAME_OWNED_BY_FRAME_OBJECT = 2,   // PyFrameObject 持有（堆上的帧）
    FRAME_OWNED_BY_INTERPRETER = 3,    // 解释器持有（哨兵帧）
};
```

### FRAME_OWNED_BY_THREAD（0）

普通函数调用的帧，分配在**线程的数据栈**（datastack）上。这类帧的生命周期与 C 调用栈同步：函数返回后，帧占用的栈空间立即被回收。这是最常见的帧类型，性能最高。

### FRAME_OWNED_BY_GENERATOR（1）

**生成器**（generator）、**协程**（coroutine）持有的帧。生成器的帧不在 C 栈上，而是内嵌在生成器对象中（`_PyGenObject_HEAD` 宏中的 `prefix##_iframe` 字段）。当生成器被 `yield` 挂起时，帧的完整状态（局部变量、栈顶位置、指令指针）被保存在堆上，下次 `next()` 或 `send()` 时恢复执行。

```c
// 生成器对象头部包含一个完整的 _PyInterpreterFrame
#define _PyGenObject_HEAD(prefix)                                           \
    PyObject_HEAD                                                           \
    PyObject *prefix##_weakreflist;                                         \
    PyObject *prefix##_name;                                                \
    /* ... 其他字段 ... */                                                   \
    _PyInterpreterFrame prefix##_iframe;   /* ← 内嵌的帧 */
```

### FRAME_OWNED_BY_FRAME_OBJECT（2）

由 `PyFrameObject`（Python 层面的帧对象）持有的帧。当用户代码访问帧对象（如通过 `sys._getframe()` 或 `inspect.currentframe()`）时，一个堆上的 `PyFrameObject` 被创建，它持有底层 `_PyInterpreterFrame` 的引用。这类帧在帧对象存活期间一直有效。

### FRAME_OWNED_BY_INTERPRETER（3）

解释器的**哨兵帧**（sentinel frame），位于帧链的最底端。它标记调用栈的底部——当帧遍历到 `FRAME_OWNED_BY_INTERPRETER` 时，表示已到达解释器入口（如模块顶层执行、`exec()` 调用等），不再有更早的调用者帧。

## 栈操作内联函数

帧的操作数栈操作函数定义在 `Include/internal/pycore_interpframe.h` 中，全部为 `static inline` 函数，无函数调用开销。

### _PyFrame_GetCode：获取代码对象

```c
static inline PyCodeObject *_PyFrame_GetCode(_PyInterpreterFrame *f) {
    assert(!PyStackRef_IsNull(f->f_executable));
    PyObject *executable = PyStackRef_AsPyObjectBorrow(f->f_executable);
    assert(PyCode_Check(executable));
    return (PyCodeObject *)executable;
}
```

从帧的 `f_executable` 字段获取 `PyCodeObject`，该对象包含字节码、常量池、变量名等编译产物。

### _PyFrame_Stackbase：获取栈基址

```c
static inline _PyStackRef *_PyFrame_Stackbase(_PyInterpreterFrame *f) {
    return (f->localsplus + _PyFrame_GetCode(f)->co_nlocalsplus);
}
```

返回操作数栈的起始地址。`localsplus` 数组的前 `co_nlocalsplus` 个槽位用于存储局部变量（含参数和 cell 变量），之后的空间才是操作数栈。

### _PyFrame_StackPeek：查看栈中元素

```c
static inline _PyStackRef _PyFrame_StackPeek(_PyInterpreterFrame *f, int depth) {
    assert(f->stackpointer > _PyFrame_Stackbase(f));
    assert(!PyStackRef_IsNull(f->stackpointer[-depth]));
    return f->stackpointer[-depth];
}
```

查看栈中深度为 `depth` 的元素但不弹出：
- `depth = 1` 返回栈顶元素
- `depth = 2` 返回栈顶下第二个元素
- 使用负索引 `stackpointer[-depth]` 访问（`stackpointer` 指向第一个空闲槽位）

### _PyFrame_StackPop：弹出栈顶

```c
static inline _PyStackRef _PyFrame_StackPop(_PyInterpreterFrame *f) {
    assert(f->stackpointer > _PyFrame_Stackbase(f));
    f->stackpointer--;
    return *f->stackpointer;
}
```

弹出栈顶元素，将 `stackpointer` 减 1，并返回弹出的值。

### _PyFrame_StackPush：压入栈

```c
static inline void _PyFrame_StackPush(_PyInterpreterFrame *f, _PyStackRef value) {
    *f->stackpointer = value;
    f->stackpointer++;
}
```

将一个值压入操作数栈，将值写入 `stackpointer` 指向的位置，然后 `stackpointer` 加 1。

### 栈操作示例

字节码指令的实现大量使用这些栈操作函数。例如二元加法指令（简化版）：

```c
// TARGET(BINARY_OP_ADD)：a + b
_PyStackRef b = _PyFrame_StackPop(frame);   // 弹出右操作数
_PyStackRef a = _PyFrame_StackPop(frame);   // 弹出左操作数
_PyStackRef result = PyStackRef_FromPyObjectNew(
    PyNumber_Add(PyStackRef_AsPyObjectBorrow(a),
                 PyStackRef_AsPyObjectBorrow(b)));
_PyFrame_StackPush(frame, result);          // 压入结果
```

## 帧链结构

线程的所有活跃帧通过 `previous` 指针形成一条**单向链表**，即调用栈：

```
线程状态 (PyThreadState)
    │
    ▼
┌──────────────────────┐
│ 当前帧 (current_frame)│ ← 正在执行的帧（栈顶）
│ f_executable: 代码C  │
│ previous ───────────┐│
└─────────────────────│┘
                      ▼
              ┌──────────────────────┐
              │ 调用者帧             │
              │ f_executable: 代码B  │
              │ previous ───────────┐│
              └─────────────────────│┘
                                    ▼
                            ┌──────────────────────┐
                            │ 调用者的调用者帧      │
                            │ f_executable: 代码A  │
                            │ previous ───────────┐│
                            └─────────────────────│┘
                                                  ▼
                                          ┌──────────────────────┐
                                          │ 解释器哨兵帧          │
                                          │ owner: INTERPRETER(3)│
                                          │ previous = NULL      │
                                          └──────────────────────┘
```

通过 `_PyThreadState_GetFrame(tstate)` 获取当前最顶层的完整帧（跳过不完整帧）：

```c
static inline _PyInterpreterFrame *
_PyThreadState_GetFrame(PyThreadState *tstate) {
    return _PyFrame_GetFirstComplete(tstate->current_frame);
}
```

`_PyFrame_GetFirstComplete` 会跳过 `instr_ptr` 尚未到达第一个 `RESUME` 指令的"不完整帧"（这些帧处于函数调用的建立过程中，还未开始执行函数体）。

### 帧的推入与弹出

函数调用时通过 `_PyFrame_PushUnchecked` 在数据栈上分配新帧并链接到帧链：

```c
static inline _PyInterpreterFrame *
_PyFrame_PushUnchecked(PyThreadState *tstate, _PyStackRef func,
                       int null_locals_from, _PyInterpreterFrame *previous)
{
    PyFunctionObject *func_obj = (PyFunctionObject *)PyStackRef_AsPyObjectBorrow(func);
    PyCodeObject *code = (PyCodeObject *)func_obj->func_code;
    // 在数据栈顶分配帧空间
    _PyInterpreterFrame *new_frame = (_PyInterpreterFrame *)tstate->datastack_top;
    tstate->datastack_top += code->co_framesize;
    // 初始化帧
    _PyFrame_Initialize(tstate, new_frame, func, NULL, code,
                        null_locals_from, previous);
    return new_frame;
}
```

函数返回时通过 `_PyThreadState_PopFrame` 弹出帧，恢复调用者的执行状态。

## localsplus 布局

`localsplus` 是一个柔性数组，其内存布局将局部变量区和操作数栈合并为一块连续的内存：

```
低地址 ──────────────────────────────────────────────────────► 高地址
┌─────────────────────────────────┬──────────────────────────────────────┐
│        局部变量区                │          操作数栈                     │
│  (co_nlocalsplus 个槽位)         │  (最多 co_stacksize 个槽位)           │
├────────┬────────┬───────┬────────┼────────┬────────┬────────┬───────────┤
│ 参数0  │ 参数1  │ ...   │ cell变量│ 栈槽0  │ 栈槽1  │ ...    │ 空闲槽    │
│        │        │       │        │ (基址) │        │        │           │
└────────┴────────┴───────┴────────┴────────┴────────┴────────┴───────────┘
▲                                            ▲                          ▲
│                                            │                          │
localsplus                            Stackbase                 stackpointer
(= localsplus[0])                 (= localsplus + co_nlocalsplus)
```

- **局部变量区**：前 `co_nlocalsplus` 个槽位存储函数参数、局部变量、cell/free 变量（闭包变量）。这部分空间的大小由代码对象固定。
- **操作数栈**：从 `localsplus + co_nlocalsplus`（即 `_PyFrame_Stackbase` 返回值）开始，最多使用 `co_stacksize` 个槽位。
- **`stackpointer`**：始终指向操作数栈中下一个空闲槽位。栈为空时 `stackpointer == Stackbase`；栈满时 `stackpointer == Stackbase + co_stacksize`。

这种合并布局的优势是：
1. **缓存友好**：局部变量和操作数在同一块连续内存中，提高 CPU 缓存命中率
2. **分配高效**：帧只需要一次指针加法即可在数据栈上分配，无需多次 malloc
3. **零拷贝**：参数从调用者帧的栈顶直接到达被调用帧的局部变量区

帧的总大小由代码对象的 `co_framesize` 字段决定，包含 `_PyInterpreterFrame` 结构体头部和 `localsplus` 数组空间。

## 相关概念

- [垃圾回收器](05-garbage-collector.md) — GC 需要遍历帧栈以标记栈上引用的对象
- [字节码执行引擎](07-bytecode-execution.md) — 解释主循环如何操作帧和操作数栈
- [对象模型：PyObject 与 PyVarObject](02-object-model.md) — `_PyStackRef` 和 `PyObject` 的关系
- [CPython 源码信源登记](/references/cpython-source.md) — 帧相关关键文件索引
