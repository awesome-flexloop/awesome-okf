---
type: Concept
title: "垃圾回收器"
description: "CPython分代垃圾回收器——GC头布局、三代回收策略、循环引用检测、tp_traverse/tp_clear"
tags: [cpython, gc, garbage-collection, cyclic-gc, generation, tp_traverse]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-21T16:55:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T17:30:00+08:00" }
status: stable
stale_after: 2027-08-21
sources:
  - id: cpython-source
    resource: /references/cpython-source.md
---

# 垃圾回收器

CPython 的**垃圾回收器**（garbage collector，简称 GC）是一个可选的分代追踪回收器，它的唯一目的是检测并回收**引用计数无法处理的循环引用**（reference cycles）。GC 不是内存管理的主力——绝大多数对象的生命周期由引用计数管理——GC 仅作为补充机制周期性运行。

## 为什么需要 GC

引用计数有一个根本缺陷：无法处理**循环引用**（cyclic references）。考虑以下代码：

```python
a = []
b = []
a.append(b)
b.append(a)
del a
del b
```

执行 `del a` 和 `del b` 后，两个列表对象的引用计数都降为 1（因为它们互相引用），不会被引用计数机制回收，造成**内存泄漏**。CPython 的 GC 正是为了解决这个问题而存在的。

只有**容器类型**（可能持有其他对象引用的类型）才需要 GC 参与——list、dict、set、tuple、自定义类实例等。像 int、float、str 这样的不可变原子类型不持有其他对象引用，不可能形成循环，因此不需要 GC 追踪。

## GC 头布局

所有需要 GC 追踪的对象在内存中都带有一个额外的头部 `PyGC_Head`，位于 `PyObject` 结构体**之前**。定义在 `Include/internal/pycore_interp_structs.h`：

```c
/* GC information is stored BEFORE the object structure. */
typedef struct {
    // Tagged pointer to next object in the list.
    // 0 means the object is not tracked
    _Py_ALIGNED_DEF(_PyObject_MIN_ALIGNMENT, uintptr_t) _gc_next;

    // Tagged pointer to previous object in the list.
    // Lowest two bits are used for flags:
    //   bit 0: _PyGC_PREV_MASK_FINALIZED (tp_finalize 已被调用)
    //   bit 1: _PyGC_PREV_MASK_COLLECTING (对象正在被收集中)
    uintptr_t _gc_prev;
} PyGC_Head;
```

内存布局如下：

```
低地址 ───────────────────────────────► 高地址
┌─────────────┬──────────────────────┐
│  PyGC_Head  │  PyObject / PyVar... │
│  (_gc_next) │  (ob_refcnt, ob_type,│
│  (_gc_prev) │   ob_..., 数据...)   │
└─────────────┴──────────────────────┘
              ▲
              │
              PyObject* 指向这里
```

通过 `Include/internal/pycore_gc.h` 中的内联函数在 GC 头和对象指针之间转换：

```c
// 从 PyObject* 获取 GC 头
static inline PyGC_Head* _Py_AS_GC(PyObject *op) {
    char *gc = ((char*)op) - sizeof(PyGC_Head);
    return (PyGC_Head*)gc;
}

// 从 GC 头获取 PyObject*
static inline PyObject* _Py_FROM_GC(PyGC_Head *gc) {
    char *op = ((char *)gc) + sizeof(PyGC_Head);
    return (PyObject *)op;
}
```

- `_gc_next == 0` 表示对象当前未被 GC 追踪
- `_gc_prev` 的最低两位用于标志位，实际指针通过掩码 `_PyGC_PREV_MASK`（`~(uintptr_t)3`）获取

## 三代回收策略

CPython 的 GC 采用**分代回收**（generational collection）策略，基于"大多数对象生命周期很短"的弱分代假说（weak generational hypothesis）。新创建的对象放入年轻代，存活过多次回收的对象晋升到老年代。

定义于 `Include/internal/pycore_interp_structs.h`：

```c
#define NUM_GENERATIONS 3

struct gc_generation {
    PyGC_Head head;       // 双向链表头（环装链表）
    int threshold;        // 回收阈值
    int count;            // 自上次回收以来的分配计数
};
```

三代的默认阈值（见 `GC_GENERATION_INIT`）：

| 代 | 阈值 | 说明 |
|----|------|------|
| **第 0 代** | 700（旧版为 2000） | 新创建的容器对象最先进入第 0 代，回收最频繁 |
| **第 1 代** | 10 | 在第 0 代回收中存活的对象晋升到第 1 代 |
| **第 2 代** | 10 | 在第 1 代回收中存活的对象晋升到第 2 代，回收最不频繁 |

### 触发条件

每分配一定数量的容器对象（通过 `_PyObject_GC_Alloc` 追踪），对应代的 `count` 加 1。当第 0 代的 `count` 超过其 `threshold` 时触发 GC：

1. 如果第 2 代的 `count` 超过阈值，回收所有三代（full collection）
2. 否则如果第 1 代的 `count` 超过阈值，回收第 0 代和第 1 代
3. 否则只回收第 0 代

回收某一代时，比它年轻的代也会同时被回收。每回收完年轻代，会将老年代的 `count` 加 1（除了 full collection 会重置）。

## 容器类型的要求

一个自定义容器类型要参与 GC 追踪，必须满足三个条件：

### 1. 设置 Py_TPFLAGS_HAVE_GC 标志

```c
PyTypeObject MyContainer_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "my_module.MyContainer",
    .tp_basicsize = sizeof(MyContainerObject),
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,  // 必须设置
    // ...
};
```

设置此标志后，对象必须通过 `PyObject_GC_New` 或 `PyObject_GC_NewVar` 分配内存（这会在对象前预留 `PyGC_Head` 空间）。

### 2. 实现 tp_traverse

`tp_traverse` 是访问函数，GC 用它来遍历对象持有的所有子对象引用：

```c
static int
mycontainer_traverse(MyContainerObject *self, visitproc visit, void *arg)
{
    // Py_VISIT 宏会对每个非 NULL 的子对象调用 visit 回调
    Py_VISIT(self->item);
    // 如果有多个成员，依次访问：
    // Py_VISIT(self->other_item);
    return 0;
}
```

`Py_VISIT` 宏定义在 `Include/objimpl.h`：

```c
#define Py_VISIT(op)                                                    \
    do {                                                                \
        if (op) {                                                       \
            int vret = visit(_PyObject_CAST(op), arg);                  \
            if (vret)                                                   \
                return vret;                                            \
        }                                                               \
    } while (0)
```

`tp_traverse` 的作用是让 GC 知道对象引用了哪些其他对象，从而构建对象引用图。

### 3. 实现 tp_clear

`tp_clear` 负责清除对象持有的所有引用，以打破循环引用：

```c
static int
mycontainer_clear(MyContainerObject *self)
{
    // 使用 Py_CLEAR 安全地清除引用（先置 NULL 再 DECREF）
    Py_CLEAR(self->item);
    // Py_CLEAR(self->other_item);
    return 0;
}
```

`tp_clear` 在 GC 检测到对象不可达时被调用。它必须能够安全地在对象处于"半销毁"状态时被调用（使用 `Py_CLEAR` 而非 `Py_DECREF` 来避免悬空指针问题）。

## GC 工作流程

GC 的核心实现在 `Python/gc.c` 中。一次回收周期分为以下阶段：

### 阶段一：更新追踪状态

新分配的容器对象通过 `PyObject_GC_Track()` → 内部宏 `_PyObject_GC_TRACK` 加入第 0 代的双向链表：

```c
// 简化版（非 Py_GIL_DISABLED 构建）
static inline void _PyObject_GC_TRACK(PyObject *op) {
    PyGC_Head *gc = _Py_AS_GC(op);
    struct _gc_runtime_state *gcstate = &_PyInterpreterState_GET()->gc;
    PyGC_Head *generation0 = gcstate->generation0;
    PyGC_Head *last = (PyGC_Head*)(generation0->_gc_prev);
    _PyGCHead_SET_NEXT(last, gc);
    _PyGCHead_SET_PREV(gc, last);
    _PyGCHead_SET_NEXT(gc, generation0);
    generation0->_gc_prev = (uintptr_t)gc;
    gcstate->heap_size++;
}
```

对象被插入到第 0 代链表的末尾（头插法形成双向循环链表）。

某些容器（如空元组、不含可变对象的字典）会在 GC 运行时被"去追踪"（untrack），因为它们不可能参与循环引用。

### 阶段二：标记可达对象

GC 将目标代及更年轻代的所有对象合并到一个集合中，然后执行以下步骤：

1. **初始化副本引用计数**：将每个对象的 `ob_refcnt` 复制到 GC 头的 `gc_refs` 字段（实际使用 `_gc_prev` 指针的空间或更新 `ob_refcnt` 副本）
2. **扫描根对象**：从"外部根"（全局变量、栈上的引用等）出发，通过 `tp_traverse` 遍历可达对象，对每个可达对象递减其副本引用计数
3. **识别不可达对象**：副本引用计数仍大于 0 的对象是从循环内部引用的——它们就是不可达的垃圾对象

这个算法称为"暂停-复制"引用计数减法，本质上是一个简化的标记-清除（mark-sweep）算法：副本计数 > 0 表示该对象**仅被环内对象引用**，从外部根无法到达。

### 阶段三：处理终结器与复活

在清除之前，GC 会检查不可达对象是否有 `tp_finalize`（即 Python 层面的 `__del__` 方法）：

- 有 `__del__` 的对象被移入 `gc.garbage` 列表（Python 3.4+ 中 PEP 442 改进了这一点，大多数有 `__del__` 的对象也能被安全回收）
- 被终结器"复活"的对象（在 `__del__` 中被重新引用）从不可达集合中移除

### 阶段四：清除不可达对象

对所有确认不可达的对象调用 `tp_clear` 清除引用，打破循环。一旦循环被打破，引用计数机制就能正常工作——每个对象的引用计数归零后会被正常的 `Py_DECREF → _Py_Dealloc` 流程回收。

## GC 的 C API

公共 GC API 定义在 `Include/objimpl.h`：

```c
/* C equivalent of gc.collect() */
PyAPI_FUNC(Py_ssize_t) PyGC_Collect(void);

/* C API for controlling the state of the garbage collector */
PyAPI_FUNC(int) PyGC_Enable(void);
PyAPI_FUNC(int) PyGC_Disable(void);
PyAPI_FUNC(int) PyGC_IsEnabled(void);

/* Tell the GC to track/untrack this object */
PyAPI_FUNC(void) PyObject_GC_Track(void *);
PyAPI_FUNC(void) PyObject_GC_UnTrack(void *);

/* Test if a type/object has GC tracking */
#define PyType_IS_GC(t) PyType_HasFeature((t), Py_TPFLAGS_HAVE_GC)
PyAPI_FUNC(int) PyObject_GC_IsTracked(PyObject *);
PyAPI_FUNC(int) PyObject_GC_IsFinalized(PyObject *);
```

| API | 用途 |
|-----|------|
| `PyGC_Collect()` | 立即执行一次完整 GC（回收所有代），返回回收的对象数 |
| `PyGC_Enable()` | 启用自动 GC（默认开启） |
| `PyGC_Disable()` | 禁用自动 GC（不影响手动调用 `PyGC_Collect`） |
| `PyGC_IsEnabled()` | 查询 GC 是否启用 |
| `PyObject_GC_Track(op)` | 将对象加入 GC 追踪链表（通常在对象构造完成后调用） |
| `PyObject_GC_UnTrack(op)` | 将对象从 GC 追踪链表移除 |

## Python 层面的 gc 模块

C 层的 GC 能力通过 `Modules/gcmodule.c` 暴露为 Python 的 `gc` 模块：

```python
import gc

gc.collect()           # 立即执行 GC，返回回收对象数
gc.collect(generation=2)  # 回收指定代（0/1/2）
gc.disable()           # 禁用自动 GC
gc.enable()            # 启用自动 GC
gc.isenabled()         # 查询 GC 状态
gc.get_count()         # 返回各代当前计数 (count0, count1, count2)
gc.get_threshold()     # 返回各代阈值 (threshold0, threshold1, threshold2)
gc.set_threshold(700, 10, 10)  # 设置阈值
gc.get_objects()       # 返回所有被 GC 追踪的对象列表
gc.get_referrers(obj)  # 返回引用了 obj 的对象
gc.get_referents(obj)  # 返回 obj 引用的对象
gc.garbage             # 无法回收的对象列表（有 __del__ 的旧对象）
```

在性能敏感的代码段中，可以临时禁用 GC 以避免回收停顿，但要注意在禁用期间循环引用不会被回收：

```python
gc.disable()
try:
    # 性能关键路径
    ...
finally:
    gc.enable()
    gc.collect()  # 重新启用后可选择手动回收
```

## 相关概念

- [引用计数与内存分配](04-reference-counting.md) — 主要的内存管理机制，GC 是其补充
- [类型系统与 PyTypeObject](03-type-system.md) — 类型标志 `Py_TPFLAGS_HAVE_GC` 和方法套件
- [解释器帧与执行栈](06-interpreter-frame.md) — 栈帧也可能持有对象引用，需要 GC 遍历
- [CPython 源码信源登记](/references/cpython-source.md) — GC 相关关键文件索引
