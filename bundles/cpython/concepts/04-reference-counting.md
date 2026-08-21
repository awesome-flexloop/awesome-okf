---
type: Concept
title: "引用计数与内存分配"
description: "CPython引用计数机制——Py_INCREF/Py_DECREF宏、对象创建与销毁流程、pymalloc小对象分配器"
tags: [cpython, reference-counting, memory, pymalloc, allocation, Py_INCREF, Py_DECREF]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-21T16:55:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T17:30:00+08:00" }
status: stable
stale_after: 2027-08-21
sources:
  - id: cpython-source
    resource: /references/cpython-source.md
---

# 引用计数与内存分配

CPython 使用**引用计数**（reference counting）作为主要的内存管理机制，辅以分代垃圾回收器（garbage collector）处理循环引用。每个 Python 对象在底层都维护一个引用计数字段 `ob_refcnt`，记录当前有多少个引用指向该对象。当引用计数归零时，对象立即被销毁并释放内存。

## 引用计数基本原理

每个 `PyObject` 的头部包含一个 `ob_refcnt` 字段（类型为 `Py_ssize_t`，在 64 位系统上其低 32 位用于存储引用计数值）：

- 当一个新的引用指向对象时，`ob_refcnt` 加 1
- 当一个引用被销毁（变量离开作用域、被重新赋值等）时，`ob_refcnt` 减 1
- 当 `ob_refcnt` 降到 0 时，调用对象的析构函数（`tp_dealloc`），释放内存

引用计数的优势是**确定性**——对象在最后一个引用消失时立即被回收，不需要像追踪式 GC 那样等待回收周期；劣势是无法处理循环引用，且每次引用变动都有原子操作开销。

## 引用计数关键宏

引用计数操作的核心宏定义在 `Include/refcount.h` 中。

### Py_INCREF 与 Py_DECREF

```c
// 增加引用计数（op 不能为 NULL）
static inline Py_ALWAYS_INLINE void Py_INCREF(PyObject *op) {
    // 64位系统上的简化逻辑：
    uint32_t cur_refcnt = op->ob_refcnt;
    if (cur_refcnt >= _Py_IMMORTAL_INITIAL_REFCNT) {
        return;  // 永生对象，不修改引用计数
    }
    op->ob_refcnt = cur_refcnt + 1;
}

// 减少引用计数，归零则调用 _Py_Dealloc
static inline Py_ALWAYS_INLINE void Py_DECREF(PyObject *op) {
    if (_Py_IsImmortal(op)) {
        return;  // 永生对象，不做修改
    }
    if (--op->ob_refcnt == 0) {
        _Py_Dealloc(op);
    }
}
```

- **`Py_INCREF(op)`**：增加对象的引用计数。参数 `op` 必须是非 NULL 的有效对象指针。
- **`Py_DECREF(op)`**：减少对象的引用计数。当引用计数归零时，调用 `_Py_Dealloc(op)` 触发析构流程。参数 `op` 必须是非 NULL 的有效对象指针。

### Py_XINCREF 与 Py_XDECREF（NULL 安全版本）

```c
static inline void Py_XINCREF(PyObject *op) {
    if (op != NULL) {
        Py_INCREF(op);
    }
}

static inline void Py_XDECREF(PyObject *op) {
    if (op != NULL) {
        Py_DECREF(op);
    }
}
```

`Py_XINCREF` 和 `Py_XDECREF` 是 `Py_INCREF`/`Py_DECREF` 的**安全版本**，接受可能为 NULL 的指针。当指针为 NULL 时，它们什么也不做，避免了空指针解引用。

### Py_CLEAR：安全清除引用

```c
#define Py_CLEAR(op) \
    do { \
        _Py_TYPEOF(op)* _tmp_op_ptr = &(op); \
        _Py_TYPEOF(op) _tmp_old_op = (*_tmp_op_ptr); \
        if (_tmp_old_op != NULL) { \
            *_tmp_op_ptr = NULL; \        // 先置 NULL
            Py_DECREF(_tmp_old_op); \     // 再减少引用计数
        } \
    } while (0)
```

`Py_CLEAR(op)` 是 `tp_clear` 和 `tp_dealloc` 实现中的关键宏。它**先将指针置为 NULL，再调用 Py_DECREF**，避免了经典的悬空指针问题：如果 DECREF 触发了任意 Python 代码（如 `__del__` 方法、weakref 回调），这些代码可能重新访问正在被销毁的对象，而此时指针已被置 NULL，不会访问到处于不一致状态的对象。

### 永生对象检测

CPython 3.12+ 引入了**永生对象**（immortal objects）机制。在 64 位系统上：

- `_Py_IMMORTAL_INITIAL_REFCNT` = `3ULL << 30`（约 32 亿）：永生对象初始引用计数
- `_Py_IMMORTAL_MINIMUM_REFCNT` = `1ULL << 31`（约 21 亿）：永生判定阈值
- 当 `ob_refcnt` 的低 32 位符号位为负（即 `>= 2^31`）时，对象被视为永生
- 永生对象的 `Py_INCREF`/`Py_DECREF` 直接返回，不修改引用计数，也不会被释放

内置对象如 `None`、`True`、`False`、小整数、内置类型对象等都是永生的。在自由线程（`Py_GIL_DISABLED`）构建中，`_Py_IMMORTAL_REFCNT_LOCAL` = `UINT32_MAX` 用于标记永生对象。

## 对象创建流程

对象的通用创建逻辑在 `Objects/object.c` 中实现。

### _PyObject_New：定长对象分配

```c
// 等价于 PyObject_New(type, typeobj)
PyAPI_FUNC(PyObject *) _PyObject_New(PyTypeObject *tp) {
    PyObject *op = (PyObject *) PyObject_Malloc(_PyObject_SIZE(tp));
    if (op == NULL) {
        return PyErr_NoMemory();
    }
    PyObject_Init(op, tp);
    return op;
}
```

`_PyObject_New(typeobj)` 的执行步骤：

1. 调用 `PyObject_Malloc` 分配 `tp->tp_basicsize` 字节的内存
2. 调用 `PyObject_Init` 初始化对象头：设置 `ob_type` 为 `typeobj`，初始化 `ob_refcnt` 为 1
3. 返回新对象指针

### _PyObject_NewVar：变长对象分配

```c
PyAPI_FUNC(PyVarObject *) _PyObject_NewVar(PyTypeObject *tp, Py_ssize_t nitems) {
    PyVarObject *op = (PyVarObject *) PyObject_Malloc(_PyObject_VAR_SIZE(tp, nitems));
    if (op == NULL) {
        return (PyVarObject *) PyErr_NoMemory();
    }
    PyObject_InitVar(op, tp, nitems);
    return op;
}
```

`_PyObject_NewVar(typeobj, size)` 用于创建**变长对象**（如 tuple、list、bytes），额外分配 `nitems` 个元素的空间，并初始化 `ob_size` 字段。

### PyObject_Init 与 PyObject_InitVar

这两个函数用于初始化**已分配内存**的对象头：

```c
PyAPI_FUNC(PyObject *) PyObject_Init(PyObject *op, PyTypeObject *tp) {
    _Py_NewReference(op);  // ob_refcnt = 1
    Py_SET_TYPE(op, tp);
    return op;
}
```

当使用自定义分配器分配内存后（如使用 mmap、共享内存、C++ 的 `operator new`），需要手动调用 `PyObject_Init` 或 `PyObject_InitVar` 来初始化 Python 对象头。

## 对象销毁流程

### _Py_Dealloc：对象析构入口

```c
// 在 Include/refcount.h 中声明
PyAPI_FUNC(void) _Py_Dealloc(PyObject *op);
```

`_Py_Dealloc(op)` 在引用计数归零时被调用，其核心逻辑：

1. 如果对象被 GC 追踪（设置了 `Py_TPFLAGS_HAVE_GC`），调用 `PyObject_GC_UnTrack` 将其从 GC 链表中移除
2. 调用类型对象的 `tp_dealloc` 析构函数
3. `tp_dealloc` 负责清理对象持有的引用（调用 `Py_CLEAR` 清除成员引用），最终调用 `PyObject_Free`（或 `PyObject_GC_Del`）释放内存

对于简单的不可变对象（如小整数），`tp_dealloc` 通常直接调用 `PyObject_Free`；对于容器对象（如 list、dict），`tp_dealloc` 需要先递减所有元素的引用计数。

## 内存分配 API

内存分配接口定义在 `Include/objimpl.h` 和 `Include/pymem.h` 中。

### 对象层 API（PyObject_ 前缀）

| API | 用途 |
|-----|------|
| `PyObject_Malloc(size)` | 分配对象内存，走 pymalloc 小对象分配器 |
| `PyObject_Calloc(nelem, elsize)` | 分配并清零内存 |
| `PyObject_Realloc(ptr, size)` | 重新分配内存 |
| `PyObject_Free(ptr)` | 释放内存 |
| `PyObject_New(type, typeobj)` | 分配并初始化定长对象 |
| `PyObject_NewVar(type, typeobj, n)` | 分配并初始化变长对象 |
| `PyObject_GC_New(type, typeobj)` | 分配 GC 追踪的定长对象 |
| `PyObject_GC_NewVar(type, typeobj, n)` | 分配 GC 追踪的变长对象 |
| `PyObject_GC_Track(op)` | 将对象加入 GC 追踪链表 |
| `PyObject_GC_Del(op)` | 释放 GC 追踪对象的内存 |

### 内存 API 层级

```
┌─────────────────────────────────────────────┐
│  PyObject_{Malloc,Free,New,NewVar,...}      │  ← 对象层（对象感知）
├─────────────────────────────────────────────┤
│  PyMem_{Malloc,Free,...}                    │  ← 原始内存层（Python 运行时）
├─────────────────────────────────────────────┤
│  pymalloc 分配器 (obmalloc.c)               │  ← 小对象（≤512B）优化
├─────────────────────────────────────────────┤
│  系统 malloc/free/mmap                      │  ← 大对象直接走系统分配
└─────────────────────────────────────────────┘
```

- **`PyObject_` 层**：面向 Python 对象的分配，知道 GC 头、对象头等信息
- **`PyMem_` 层**：底层原始内存接口，被 pymalloc 和系统分配器包装
- **pymalloc**：针对小对象优化的分配器，大于 `SMALL_REQUEST_THRESHOLD`（512 字节）的请求直接转发给系统 malloc

**重要**：不要混用不同层级的分配/释放函数——用 `PyObject_Malloc` 分配的内存必须用 `PyObject_Free` 释放，不能用 `free()`。

## pymalloc 小对象分配器

pymalloc 是 CPython 专为小对象（≤ 512 字节）设计的内存分配器，实现在 `Objects/obmalloc.c` 中，核心常量定义在 `Include/internal/pycore_obmalloc.h`。

### 三级结构

pymalloc 使用 arena → pool → block 的三级内存结构：

```
Arena (ARENA_SIZE = 1 MiB, 64位系统默认)
├── Pool 0 (POOL_SIZE = 16 KiB)
│   ├── Block (16 B)  ──┐
│   ├── Block (16 B)    │  同一 pool 内所有 block 大小相同
│   ├── Block (16 B)    │  （属于同一 size class）
│   └── ...             ┘
├── Pool 1 (POOL_SIZE = 16 KiB)
│   ├── Block (32 B)
│   ├── Block (32 B)
│   └── ...
└── ...
```

| 层级 | 大小（64位系统默认） | 说明 |
|------|---------------------|------|
| **arena** | 1 MiB（`ARENA_BITS = 20`） | 从操作系统申请的大块内存，通过 mmap/malloc 获取 |
| **pool** | 16 KiB（`POOL_BITS = 14`） | arena 内的子区域，同一 pool 的所有 block 属于同一 size class |
| **block** | 按 16 字节对齐（`ALIGNMENT = 16`） | 最小分配单元，大小从 16B 到 512B 共 32 个 size class |

关键常量（64 位系统，启用 `USE_LARGE_POOLS` 和 `USE_LARGE_ARENAS`）：

- `ALIGNMENT = 16`：内存对齐到 16 字节
- `SMALL_REQUEST_THRESHOLD = 512`：超过 512 字节的请求直接交给系统 malloc
- `NB_SMALL_SIZE_CLASSES = 32`：共 32 个大小等级（16, 32, 48, ..., 512）
- `MAX_POOLS_IN_ARENA = ARENA_SIZE / POOL_SIZE = 64`：每个 arena 最多 64 个 pool

### Pool 的三种状态

每个 pool 在运行时处于以下三种状态之一：

| 状态 | 说明 |
|------|------|
| **full**（已满） | 所有 block 都已分配，无空闲 block |
| **used**（部分使用） | 有已分配的 block，也有空闲 block |
| **empty**（空闲） | 所有 block 都空闲，可以被重新分配给任意 size class |

pymalloc 为每个 size class 维护一个 `usedpools` 数组，指向该等级当前可用的 used pool，确保分配时快速找到有空闲 block 的 pool。

### 内存布局概览

```c
// Pool 头部结构（简化）
struct pool_header {
    uint count;              // 已分配的 block 数
    pymem_block *freeblock;  // 空闲 block 链表头
    struct pool_header *nextpool;
    struct pool_header *prevpool;
    uint szidx;              // size class 索引（0~31）
    uint nextoffset;         // 下一个未使用 block 的偏移
    uint maxnextoffset;      // pool 内最大有效偏移
};
```

当一个 pool 被初始化为某个 size class 时，所有 block 通过内嵌的 free-list 指针串联成空闲链表。分配时从 `freeblock` 取一个 block；释放时将 block 重新挂回空闲链表。

## 相关概念

- [对象模型：PyObject 与 PyVarObject](02-object-model.md) — Python 对象的底层结构基础
- [类型系统与 PyTypeObject](03-type-system.md) — 类型对象中的 `tp_alloc`/`tp_dealloc` 方法套件
- [垃圾回收器](05-garbage-collector.md) — 引用计数的补充，处理循环引用
- [CPython 源码信源登记](/references/cpython-source.md) — 关键文件路径索引
