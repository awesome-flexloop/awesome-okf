---
type: Concept
title: "对象模型：PyObject 与 PyVarObject"
description: "CPython对象模型的基础——PyObject结构体、引用计数字段、类型指针、变长对象PyVarObject、对象宏"
tags: [cpython, object, PyObject, PyVarObject, object-model, reference-count]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-21T18:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T18:30:00+08:00" }
status: stable
stale_after: 2027-08-21
sources:
  - id: cpython-source
    resource: /references/cpython-source.md
---

CPython 的核心设计原则是**"一切皆对象"（Everything is an object）**。在 C 层面，所有 Python 值都表示为指向 `PyObject` 结构体的指针。理解 `PyObject` 和 `PyVarObject` 的内存布局是理解整个 CPython 对象系统的基石。

## 什么是对象模型

对象模型（Object Model）定义了 Python 中所有值的**统一表示方式**。无论你操作的是整数、字符串、列表、字典还是函数——在 C 层面，它们都通过 `PyObject*` 指针访问。每个对象在堆上分配，具有固定的头部（包含引用计数和类型指针），以及紧随其后的类型特定数据。

对象具有三个基本特性：

1. **堆分配（Heap-allocated）**：对象不在栈上静态分配（类型对象是例外，标准类型使用静态分配），必须通过专用宏和函数在堆上创建。
2. **固定大小（Fixed-size after allocation）**：对象一旦分配，其内存大小和地址就不再改变。需要存储可变长度数据的对象通过指针指向额外内存，但基础结构体大小不变。
3. **指针访问（Pointer-based access）**：对象始终通过 `PyObject*` 指针引用，这使得引用传递、多态和引用计数成为可能。

## PyObject 结构体

`PyObject`（在源码中定义为 `struct _object`）是所有 Python 对象的**公共基础头部**。它的定义位于 `Include/object.h`，根据编译模式（传统 GIL 模式 vs Free-threading 模式）有两种不同的内存布局。

### 传统 GIL 模式

在默认构建（带 GIL，即非 `Py_GIL_DISABLED`）下，`PyObject` 的 64 位布局如下：

```c
// 64 位系统，SIZEOF_VOID_P > 4
struct _object {
    _Py_ANONYMOUS union {
        int64_t ob_refcnt_full;      // 用于 Clang/ARM 高效初始化
        struct {
#  if PY_BIG_ENDIAN
            uint16_t ob_flags;       // 标志位（永生、静态分配等）
            uint16_t ob_overflow;    // 溢出计数
            uint32_t ob_refcnt;      // 引用计数
#  else
            uint32_t ob_refcnt;      // 引用计数（小端序在前）
            uint16_t ob_overflow;    // 溢出计数
            uint16_t ob_flags;       // 标志位
#  endif
        };
        _Py_ALIGNED_DEF(_PyObject_MIN_ALIGNMENT, char) _aligner;  // 对齐保证
    };
    PyTypeObject *ob_type;           // 指向类型对象的指针
};
```

在 32 位系统上，布局更简单：

```c
// 32 位系统
struct _object {
    Py_ssize_t ob_refcnt;            // 引用计数
    PyTypeObject *ob_type;           // 类型指针
};
```

两个核心字段：

- **ob_refcnt**（引用计数）：32 位无符号整数，记录当前有多少引用指向该对象。当引用计数降为 0 时，对象被释放。64 位系统下引用计数被拆分为 `ob_refcnt`（低 32 位）+ `ob_overflow`（高 16 位）+ `ob_flags`（标志位）。
- **ob_type**（类型指针）：指向该对象的**类型对象**（`PyTypeObject*`）。类型对象决定了对象的行为——它支持哪些操作、占用多大内存、如何销毁等。这是 CPython 实现多态的核心机制。

### Free-threading（nogil）模式

CPython 3.13+ 引入了实验性的**自由线程模式**（Free-threading，即无 GIL 构建，编译时定义 `Py_GIL_DISABLED`）。在此模式下，`PyObject` 需要额外字段支持细粒度同步和分布式引用计数：

```c
// Py_GIL_DISABLED 构建
struct _object {
    _Py_ALIGNED_DEF(_PyObject_MIN_ALIGNMENT, uintptr_t) ob_tid;
    uint16_t ob_flags;          // 对象标志
    PyMutex ob_mutex;           // 每对象锁（per-object lock）
    uint8_t ob_gc_bits;         // GC 相关状态位
    uint32_t ob_ref_local;      // 本地（线程私有）引用计数
    Py_ssize_t ob_ref_shared;   // 共享（原子）引用计数
    PyTypeObject *ob_type;      // 类型指针
};
```

自由线程模式下的字段说明：

| 字段 | 作用 |
|------|------|
| `ob_tid` | 所属线程 ID（0 表示无所有者，包括永生对象和引用计数已合并的对象）；也被 GC 和 trashcan 机制复用为链表指针 |
| `ob_flags` | 标志位（永生标记、静态分配标记等） |
| `ob_mutex` | 每对象互斥锁，用于在无 GIL 环境下保护对象修改 |
| `ob_gc_bits` | GC 状态位（跟踪对象是否在 GC 链表中等） |
| `ob_ref_local` | 当前线程的本地引用计数（非原子操作，快速路径） |
| `ob_ref_shared` | 跨线程共享的引用计数（原子操作，慢路径） |
| `ob_type` | 类型指针（与传统模式一致） |

本地/共享引用计数分离是自由线程模式的关键优化：**同一线程内**的引用增减只操作 `ob_ref_local`（无需原子操作，性能与 GIL 模式相当），只有跨线程传递时才操作 `ob_ref_shared`（需要原子指令）。

### 对象最小对齐

```c
#define _PyObject_MIN_ALIGNMENT 4
```

所有 `PyObject` 保证至少 **4 字节对齐**。这使得对象指针的最低 2 位可用于标记（tagged pointer）用途——CPython 利用这一点在内部实现了一些优化（如 GC 链表指针复用）。

## PyVarObject：变长对象

并非所有对象都是固定大小的。对于长度可变的容器对象（如元组、列表、字节串），CPython 定义了 `PyVarObject`：

```c
struct PyVarObject {
    PyObject ob_base;        // 基础头部（引用计数 + 类型指针）
    Py_ssize_t ob_size;      // 变长部分的元素个数（不是字节数！）
};
```

`ob_size` 字段记录变长部分包含的**元素个数**（而非字节数）。例如，一个包含 5 个元素的元组，其 `ob_size` 为 5。具体元素数据紧跟在 `PyVarObject` 结构体之后，通常通过**柔性数组**（flexible array member）或指针偏移访问。

以下是一些使用 `PyVarObject` 的内置类型：

| 类型 | 结构体 | 变长部分 |
|------|--------|---------|
| `tuple` | `PyTupleObject` | `PyObject *ob_item[1]`（元素指针数组） |
| `bytes` | `PyBytesObject` | `char ob_sval[1]`（字符数据） |
| `list` | `PyListObject` | `PyObject **ob_item`（指向元素指针数组的指针，注意不是柔性数组） |
| `str` | `PyASCIIObject`/`PyCompactUnicodeObject` | 紧凑字符串数据 |
| `int` | `PyLongObject` | `digit ob_digit[1]`（数位数组，用于任意精度整数） |

注意 `PyListObject` 的 `ob_item` 是指针而非柔性数组——列表元素存储在单独分配的数组中，列表对象只持有指向该数组的指针。这使得列表可以动态扩容而无需重新分配列表对象本身。

## 对象头部宏

CPython 定义了两个核心宏，**所有**具体对象类型的结构体都必须以此宏开头，以确保内存布局兼容：

```c
#define PyObject_HEAD     PyObject ob_base;
#define PyObject_VAR_HEAD PyVarObject ob_base;
```

使用示例——以 `PyLongObject`（整数）和 `PyTupleObject`（元组）为例：

```c
// 定长对象示例：浮点数
typedef struct {
    PyObject_HEAD          // 展开为 PyObject ob_base;
    double ob_fval;        // 浮点数的值
} PyFloatObject;

// 变长对象示例：元组
typedef struct {
    PyObject_VAR_HEAD      // 展开为 PyVarObject ob_base; 包含 ob_base.ob_size
    PyObject *ob_item[1];  // 元素指针数组（柔性数组，实际分配更多空间）
} PyTupleObject;
```

这种"手动继承"模式（通过在结构体开头嵌入基类作为第一个成员）是 C 语言中实现面向对象继承的经典手法。由于 C 语言保证结构体第一个成员的偏移量为 0，因此 `PyFloatObject*` 和 `PyTupleObject*` 都可以安全地强制转换为 `PyObject*`，实现多态。

## 静态初始化宏

静态分配的类型对象（如内置类型 `PyLong_Type`、`PyList_Type` 等）使用特殊的初始化宏：

```c
// 传统 GIL 模式
#define PyObject_HEAD_INIT(type)    \
    {                               \
        { _Py_STATIC_IMMORTAL_INITIAL_REFCNT },  \
        (type)                      \
    },

// 自由线程模式
#define PyObject_HEAD_INIT(type)    \
    {                               \
        0,                          \
        _Py_STATICALLY_ALLOCATED_FLAG, \
        { 0 },                      \
        0,                          \
        _Py_IMMORTAL_REFCNT_LOCAL,  \
        0,                          \
        (type),                     \
    },
```

变长对象使用：

```c
#define PyVarObject_HEAD_INIT(type, size) \
    {                                     \
        PyObject_HEAD_INIT(type)          \
        (size)                            \
    },
```

注意 `PyObject_HEAD_INIT` 将静态对象标记为**永生对象**（immortal）——这是必要的，因为静态分配的对象可能在多个解释器之间共享，不能被引用计数机制回收。

## 关键宏与函数

CPython 提供了一系列访问器宏来操作对象头部字段，使用宏而非直接访问字段是为了在不同编译模式（GIL/nogil、32/64 位、Limited API）之间保持兼容性：

### Py_TYPE：获取对象类型

```c
// 获取对象的类型指针
static inline PyTypeObject* _Py_TYPE_impl(PyObject *ob) {
    return ob->ob_type;
}
#define Py_TYPE(ob) _Py_TYPE_impl(_PyObject_CAST(ob))
```

`Py_TYPE(ob)` 返回对象的 `PyTypeObject*` 类型指针。在 Python 层面，这对应于 `type(obj)`。

### Py_SIZE：获取变长对象大小

```c
static inline Py_ssize_t _Py_SIZE_impl(PyObject *ob) {
    assert(Py_TYPE(ob) != &PyLong_Type);
    assert(Py_TYPE(ob) != &PyBool_Type);
    return _PyVarObject_CAST(ob)->ob_size;
}
#define Py_SIZE(ob) _Py_SIZE_impl(_PyObject_CAST(ob))
```

`Py_SIZE(ob)` 返回变长对象的 `ob_size` 字段。注意它不能用于整数和布尔值——这些类型虽然内部也有"长度"概念（如整数的位数组长度），但语义不同，有专门的访问方式。对应的设置函数是 `Py_SET_SIZE(ob, size)`。

### Py_IS_TYPE：类型检查

```c
static inline int _Py_IS_TYPE_impl(PyObject *ob, PyTypeObject *type) {
    return Py_TYPE(ob) == type;
}
#define Py_IS_TYPE(ob, type) _Py_IS_TYPE_impl(_PyObject_CAST(ob), (type))
```

`Py_IS_TYPE(ob, type)` 检查对象的类型是否**精确匹配**指定类型（不检查子类）。这对应 Python 中的 `type(obj) is SomeType`，而非 `isinstance(obj, SomeType)`。对于包含子类的类型检查，应使用 `PyObject_TypeCheck(ob, type)` 或 `PyType_IsSubtype()`。

### Py_Is：同一性检查

```c
#define Py_Is(x, y) ((x) == (y))
```

`Py_Is(x, y)` 检查两个指针是否指向同一个对象，对应 Python 中的 `x is y`。还有便捷宏：
- `Py_IsNone(x)` → `x is None`
- `Py_IsTrue(x)` → `x is True`
- `Py_IsFalse(x)` → `x is False`

## 永生对象（Immortal Objects）

CPython 3.12+ 引入了**永生对象**机制。永生对象的引用计数被设置为一个特殊的高值，使得 `Py_INCREF` 和 `Py_DECREF` 操作实际上不会改变其引用计数，对象永远不会被释放。

永生对象的引用计数判定阈值：

| 平台/模式 | 永生条件 | 初始值 |
|----------|---------|--------|
| 64 位 GIL 模式 | `ob_refcnt >= (1 << 31)`（低 32 位符号位为 1） | `_Py_IMMORTAL_INITIAL_REFCNT = 3 << 30` |
| 32 位 GIL 模式 | `ob_refcnt >= (1 << 30)` | `_Py_IMMORTAL_INITIAL_REFCNT = 5 << 28` |
| 自由线程模式 | `ob_ref_local == UINT32_MAX` | `_Py_IMMORTAL_REFCNT_LOCAL = UINT32_MAX` |

永生对象分为两类：

1. **静态永生对象（Statically allocated immortals）**：在编译时静态分配的对象，通过 `PyObject_HEAD_INIT` 宏初始化时自动标记为永生。所有内置类型对象（`PyLong_Type`、`PyList_Type` 等）、小整数缓存、`Py_None`、`Py_True`、`Py_False`、`Py_Ellipsis`、`Py_NotImplemented` 等单例都属于此类。它们带有 `_Py_STATICALLY_ALLOCATED_FLAG` 标志。

2. **运行时永生对象（Runtime-promoted immortals）**：在运行过程中被提升为永生的堆分配对象。这些对象在解释器关闭时需要清理。

永生对象的设计目的包括：
- 避免跨解释器共享对象的引用计数竞争
- 简化静态对象的生命周期管理
- 为自由线程模式提供安全的共享对象

## 内置单例对象

CPython 预定义了若干全局永生单例，可以直接通过宏访问：

```c
#define Py_None           (&_Py_NoneStruct)       // None
// Py_True 和 Py_False 是 PyLongObject 的实例，不是独立结构
PyAPI_DATA(PyObject) _Py_NotImplementedStruct;
#define Py_NotImplemented (&_Py_NotImplementedStruct)  // NotImplemented
```

`None`、`True`、`False`、`NotImplemented`、`Ellipsis` 都是永生对象。其中 `True` 和 `False` 实际上是整数（`PyLongObject`）的单例实例，这解释了为什么 `isinstance(True, int)` 返回 `True`。

## 相关概念

- [源码目录结构导航](01-source-layout.md) — 了解 Include/object.h 和 Objects/ 目录
- [类型系统与 PyTypeObject](03-type-system.md) — ob_type 指针指向的类型对象结构详解
- [CPython 简介](00-introduction.md) — 对象模型在整体架构中的位置
- [CPython 源码信源登记](../references/cpython-source.md) — Include/object.h 路径与版本信息

[^cpython-source]: CPython 源码信源，见 [cpython-source.md](../references/cpython-source.md)。结构体定义来自 `Include/object.h`（CPython 3.16.0a0）。
