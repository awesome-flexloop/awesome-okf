---
type: Example
title: 用 C 定义自定义类型
description: 在C扩展中定义新的Python类型——PyTypeObject定义、tp_init/tp_new、方法表、属性访问
tags: [cpython, custom-type, PyTypeObject, tp_init, tp_new, c-extension, example]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-21T17:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T17:30:00+08:00" }
status: stable
stale_after: 2027-08-21
sources:
  - id: cpython-source
    resource: /references/cpython-source.md
---

# 用 C 定义自定义类型

C 扩展不仅可以导出模块级函数，还可以定义全新的 Python 类型（type）。自定义类型在 C 层以 `PyTypeObject` 结构体描述，通过设置各种**槽位（slot）**来定义类型的行为——分配内存、初始化实例、定义方法、访问属性、资源回收等。[^cpython-source]

本示例实现一个 `CustomStack` 类型（栈数据结构），演示完整的类型定义流程：C 结构体布局、`tp_new`/`tp_init`/`tp_dealloc` 三个生命周期槽位、`tp_methods` 方法表、`tp_members` 成员定义表，以及将类型添加到模块的方法。

## 1. 自定义类型的生命周期

Python 对象在 C 层的生命周期由 `PyTypeObject` 中的三个关键槽位控制：

| 槽位 | 对应 Python 特殊方法 | 职责 | 类比 |
|------|---------------------|------|------|
| `tp_new` | `__new__` | 分配内存，创建空实例 | 构造函数（分配） |
| `tp_init` | `__init__` | 初始化实例，接受构造参数 | 构造函数（初始化） |
| `tp_dealloc` | `__del__`（语义类似） | 释放资源，回收内存 | 析构函数 |

调用顺序为：`tp_new` → `tp_init` → 使用对象 → `tp_dealloc`（引用计数归零时）。

## 2. 完整 C 源码：customstack.c

```c
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stddef.h>  /* for offsetof */

/* ========== 实例结构体 ========== */

/*
 * CustomStackObject —— CustomStack 类型的实例结构体。
 *
 * 所有 Python 对象在 C 层的第一个成员必须是 PyObject_HEAD 宏，
 * 它展开为 PyObject ob_base; 包含引用计数 (ob_refcnt) 和类型指针 (ob_type)。
 *
 * 其余成员为类型特有的数据字段。这里使用一个 Python list 作为内部存储。
 */
typedef struct {
    PyObject_HEAD
    /* 类型特有字段 */
    PyObject* data;      /* 内部存储，一个 Python list 对象 */
    Py_ssize_t max_size; /* 栈容量上限，0 表示无限制 */
} CustomStackObject;

/* ========== tp_dealloc：析构函数 ========== */

/*
 * 当对象的引用计数降为 0 时，tp_dealloc 被调用。
 * 职责：1) 递减所持有的其他 Python 对象的引用；2) 释放自身内存。
 */
static void
CustomStack_dealloc(CustomStackObject* self)
{
    /* Py_XDECREF：安全递减引用（NULL 指针安全），等价于 if (x) Py_DECREF(x) */
    Py_XDECREF(self->data);

    /* 调用类型的 tp_free 槽位释放实例内存。
       Py_TYPE(self) 获取对象的类型对象，tp_free 默认由 PyType_Ready 设置。*/
    Py_TYPE(self)->tp_free((PyObject*)self);
}

/* ========== tp_new：构造函数（分配内存） ========== */

/*
 * tp_new 负责分配并返回一个新的空实例。
 * 签名：(PyTypeObject* type, PyObject* args, PyObject* kwargs) -> PyObject*
 *
 * 对于不需要定制分配逻辑的类型，可以直接调用 tp_new 的基类实现
 * （即 PyBaseObject_Type.tp_new），它根据 tp_basicsize 分配内存并清零。
 */
static PyObject*
CustomStack_new(PyTypeObject* type, PyObject* args, PyObject* kwargs)
{
    CustomStackObject* self;

    /* tp_alloc 是通用分配函数，分配 tp_basicsize 字节并将 ob_type 设置为 type */
    self = (CustomStackObject*)type->tp_alloc(type, 0);
    if (self != NULL) {
        /* 初始化 C 层字段为安全默认值 */
        self->data = NULL;
        self->max_size = 0;
    }
    return (PyObject*)self;
}

/* ========== tp_init：初始化函数 ========== */

/*
 * tp_init 负责初始化已分配的实例，对应 Python 的 __init__ 方法。
 * 签名：(PyObject* self, PyObject* args, PyObject* kwargs) -> int
 * 返回 0 表示成功，返回 -1 表示失败（已设置异常）。
 *
 * CustomStack(iterable=None, max_size=0)
 */
static int
CustomStack_init(CustomStackObject* self, PyObject* args, PyObject* kwargs)
{
    PyObject* iterable = NULL;
    Py_ssize_t max_size = 0;
    static char* kwlist[] = {"iterable", "max_size", NULL};

    /* "|On" 表示：| 之后为可选参数；O = PyObject*；n = Py_ssize_t */
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "|On", kwlist,
                                     &iterable, &max_size)) {
        return -1;
    }

    /* 释放之前可能已有的 data（如果 __init__ 被多次调用） */
    Py_XDECREF(self->data);

    /* 创建内部存储列表 */
    if (iterable != NULL) {
        /* PySequence_List 将任意可迭代对象转为新的 list */
        self->data = PySequence_List(iterable);
        if (self->data == NULL) {
            return -1;
        }
    } else {
        /* PyList_New(0) 创建空列表，返回新引用 */
        self->data = PyList_New(0);
        if (self->data == NULL) {
            return -1;
        }
    }

    self->max_size = max_size;
    return 0;
}

/* ========== 方法函数 ========== */

/* push(item) -> None：将元素压入栈顶 */
static PyObject*
CustomStack_push(CustomStackObject* self, PyObject* args)
{
    PyObject* item;

    if (!PyArg_ParseTuple(args, "O", &item)) {
        return NULL;
    }

    /* 检查容量限制 */
    if (self->max_size > 0 && PyList_GET_SIZE(self->data) >= self->max_size) {
        PyErr_SetString(PyExc_OverflowError, "stack is full");
        return NULL;
    }

    /* PyList_Append(list, item) 等价于 list.append(item)，返回 0 成功、-1 失败。
       PyList_Append 内部会 Py_INCREF(item)，调用者无需手动管理。*/
    if (PyList_Append(self->data, item) < 0) {
        return NULL;
    }

    Py_RETURN_NONE;
}

/* pop() -> item：弹出栈顶元素；空栈抛出 IndexError */
static PyObject*
CustomStack_pop(CustomStackObject* self, PyObject* Py_UNUSED(args))
{
    Py_ssize_t len;

    len = PyList_GET_SIZE(self->data);
    if (len == 0) {
        PyErr_SetString(PyExc_IndexError, "pop from empty stack");
        return NULL;
    }

    /* PyList_GetItem 返回借用引用（borrowed reference），不增加引用计数。
       我们需要返回一个新引用给调用者，所以手动 INCREF。*/
    PyObject* item = PyList_GetItem(self->data, len - 1);
    if (item == NULL) {
        return NULL;
    }

    /* PySequence_DelItem 删除列表中指定位置的元素 */
    if (PySequence_DelItem(self->data, len - 1) < 0) {
        return NULL;
    }

    Py_INCREF(item);
    return item;
}

/* peek() -> item：查看栈顶元素但不弹出；空栈抛出 IndexError */
static PyObject*
CustomStack_peek(CustomStackObject* self, PyObject* Py_UNUSED(args))
{
    Py_ssize_t len = PyList_GET_SIZE(self->data);
    if (len == 0) {
        PyErr_SetString(PyExc_IndexError, "peek from empty stack");
        return NULL;
    }

    PyObject* item = PyList_GetItem(self->data, len - 1);
    Py_XINCREF(item);  /* 返回新引用 */
    return item;
}

/* ========== tp_methods：方法表 ========== */

static PyMethodDef CustomStack_methods[] = {
    {"push", (PyCFunction)CustomStack_push, METH_VARARGS,
     "Push an item onto the stack. Raises OverflowError if full."},
    {"pop",  (PyCFunction)CustomStack_pop,  METH_NOARGS,
     "Pop and return the top item. Raises IndexError if empty."},
    {"peek", (PyCFunction)CustomStack_peek, METH_NOARGS,
     "Return the top item without removing it. Raises IndexError if empty."},
    {NULL, NULL, 0, NULL}
};

/* ========== tp_members：成员变量定义表 ========== */

/*
 * PyMemberDef 数组定义可直接从 Python 访问的 C 结构体成员。
 * 解释器根据 offsetof() 自动计算成员偏移并进行读写。
 *
 * 字段顺序：{ name, type, offset, flags, doc }
 *
 * type 常用值（定义在 structmember.h）：
 *   T_INT     — int
 *   T_LONG    — long
 *   T_DOUBLE  — double
 *   T_STRING  — const char*（只读，C 字符串）
 *   T_OBJECT  — PyObject*（自动 INCREF/DECREF 管理）
 *   T_OBJECT_EX — 同 T_OBJECT，但属性为 NULL 时抛出 AttributeError
 *   T_PYSSIZET — Py_ssize_t
 *
 * flags：0 表示可读写，READONLY 表示只读。
 */
static PyMemberDef CustomStack_members[] = {
    {"max_size", T_PYSSIZET, offsetof(CustomStackObject, max_size), READONLY,
     "Maximum stack capacity (0 means unlimited)."},
    {NULL}  /* 哨兵 */
};

/* ========== Getter：size 属性 ========== */

/*
 * 通过 tp_getset 定义属性的 getter/setter 函数，实现计算属性或只读属性。
 * 这里定义 size 属性，返回当前栈中元素个数。
 */
static PyObject*
CustomStack_size_getter(CustomStackObject* self, void* closure)
{
    return PyLong_FromSsize_t(PyList_GET_SIZE(self->data));
}

static PyGetSetDef CustomStack_getseters[] = {
    {"size", (getter)CustomStack_size_getter, NULL,
     "Current number of items in the stack.", NULL},
    {NULL}  /* 哨兵 */
};

/* ========== tp_repr：字符串表示 ========== */

static PyObject*
CustomStack_repr(CustomStackObject* self)
{
    return PyUnicode_FromFormat("<CustomStack size=%zd max=%zd>",
                                PyList_GET_SIZE(self->data),
                                self->max_size);
}

/* ========== PyTypeObject：类型对象定义 ========== */

static PyTypeObject CustomStackType = {
    PyVarObject_HEAD_INIT(NULL, 0)  /* 宏初始化 ob_refcnt 和 ob_type，运行时由 PyType_Ready 填充 */
    .tp_name = "customstack.CustomStack",       /* 类型全名：模块名.类名 */
    .tp_basicsize = sizeof(CustomStackObject),  /* 实例大小（字节） */
    .tp_itemsize = 0,                           /* 可变大小对象才需要（如 list），固定大小为 0 */
    .tp_dealloc = (destructor)CustomStack_dealloc,
    .tp_repr = (reprfunc)CustomStack_repr,
    .tp_flags = Py_TPFLAGS_DEFAULT,             /* 必须包含 Py_TPFLAGS_DEFAULT */
    .tp_doc = PyDoc_STR("A simple stack (LIFO) implemented in C.\n\n"
                        "CustomStack(iterable=None, max_size=0)"),
    .tp_methods = CustomStack_methods,
    .tp_members = CustomStack_members,
    .tp_getset = CustomStack_getseters,
    .tp_init = (initproc)CustomStack_init,
    .tp_new = CustomStack_new,
};

/* ========== 模块定义 ========== */

static PyModuleDef customstackmodule = {
    PyModuleDef_HEAD_INIT,
    "customstack",
    "A module providing CustomStack type implemented in C.",
    -1,
    NULL, NULL, NULL, NULL, NULL
};

PyMODINIT_FUNC
PyInit_customstack(void)
{
    PyObject* m;

    /* PyType_Ready：在创建模块前必须调用，完成类型对象的最终初始化
       （填充继承的槽位、设置 tp_dict、解析 MRO 等）。*/
    if (PyType_Ready(&CustomStackType) < 0) {
        return NULL;
    }

    m = PyModule_Create(&customstackmodule);
    if (m == NULL) {
        return NULL;
    }

    /* Py_INCREF：在将类型对象添加到模块前增加引用计数。
       PyModule_AddObject 会"偷取"一个引用（窃取传递给它的引用），
       所以我们先 INCREF，确保类型对象的引用计数正确。*/
    Py_INCREF(&CustomStackType);
    if (PyModule_AddObject(m, "CustomStack", (PyObject*)&CustomStackType) < 0) {
        Py_DECREF(&CustomStackType);
        Py_DECREF(m);
        return NULL;
    }

    return m;
}
```

## 3. 关键槽位详解

### 3.1 `tp_flags`：类型标志位

`tp_flags` 必须包含 `Py_TPFLAGS_DEFAULT`（值为 `0x00000001` 以外的默认位组合），它启用所有默认的 Python 类型行为。其他常用标志：

| 标志 | 含义 |
|------|------|
| `Py_TPFLAGS_DEFAULT` | 默认标志位集合，**所有新类型必须包含** |
| `Py_TPFLAGS_HAVE_GC` | 类型实例包含对其他对象的循环引用，需要垃圾回收支持 |
| `Py_TPFLAGS_BASETYPE` | 该类型可以被继承（默认已启用） |

### 3.2 `tp_basicsize` 与 `tp_itemsize`

- **`tp_basicsize`**：实例的基本大小，设为 `sizeof(CustomStackObject)`。`tp_alloc` 根据此值分配内存。
- **`tp_itemsize`**：可变长度部分每个元素的大小。对于固定大小的类型（如本例），设为 `0`；对于可变长度类型（如 `list`、`tuple` 继承），设为单个元素的大小。

### 3.3 `tp_new` 与 `tp_init` 的分工

- **`tp_new`** 是静态方法（不接受 `self`，接受 `type`），它**只负责分配内存**，不应接受除类型参数外的业务逻辑参数。`tp_new` 在 `__init__` 之前调用。
- **`tp_init`** 是实例方法（接受 `self`），它**负责初始化**已分配的实例，接受 `__init__` 的参数。`tp_init` 可能被多次调用（例如在 `__init__` 中显式调用），所以必须能安全地重新初始化。

### 3.4 引用计数：借用引用 vs 新引用

CPython C API 中引用管理的核心概念：

- **新引用（new reference）**：API 返回的引用，调用者拥有它，必须在适当时候 `Py_DECREF`。
- **借用引用（borrowed reference）**：API 返回的引用，调用者不拥有，不保证引用在对象被其他操作后仍有效。需要长期持有时必须手动 `Py_INCREF`。
- **偷取引用（stealing reference）**：API 接管调用者传入的引用，调用者不再需要 `Py_DECREF`。`PyModule_AddObject` 会偷取引用。

常见 API 的引用行为：

| API | 返回引用类型 |
|-----|-------------|
| `PyList_New`、`PyLong_FromLong`、`PyUnicode_FromFormat` | 新引用 |
| `PyList_GetItem`、`PyTuple_GetItem` | 借用引用 |
| `PyModule_AddObject` | 偷取传入对象的引用 |
| `PyArg_ParseTuple` 的 `"O"` 格式 | 借用引用（不需要 DECREF） |
| `tp_alloc` | 新引用 |

## 4. 构建与测试

### setup.py

```python
from setuptools import setup, Extension

customstack_module = Extension(
    "customstack",
    sources=["customstack.c"],
)

setup(
    name="customstack",
    version="1.0.0",
    description="CustomStack type implemented in C",
    ext_modules=[customstack_module],
)
```

### 编译与测试

```bash
pip install -e .
```

```python
# test_customstack.py
import customstack

# 创建空栈
s = customstack.CustomStack()
print(s)  # <CustomStack size=0 max=0>
assert s.size == 0
assert s.max_size == 0

# push / pop
s.push("a")
s.push("b")
s.push(42)
assert s.size == 3
assert s.peek() == 42
assert s.pop() == 42
assert s.size == 2
assert s.pop() == "b"

# 从可迭代对象创建
s2 = customstack.CustomStack([1, 2, 3], max_size=5)
assert s2.size == 3
assert s2.max_size == 5
assert s2.peek() == 3

# 容量限制
try:
    s2.push(4)
    s2.push(5)
    s2.push(6)  # 超出 max_size=5，应抛出 OverflowError
    assert False, "Should have raised OverflowError"
except OverflowError:
    print("OverflowError correctly raised when stack is full")

# 空栈 pop/peek
empty = customstack.CustomStack()
try:
    empty.pop()
    assert False
except IndexError:
    pass

try:
    empty.peek()
    assert False
except IndexError:
    pass

print("All tests passed!")
```

运行：

```bash
python test_customstack.py
```

## 5. 常见陷阱

1. **忘记调用 `PyType_Ready`**：在创建模块前必须对每个自定义类型调用 `PyType_Ready`，否则类型对象未完全初始化，使用时会崩溃。
2. **`PyModule_AddObject` 前忘记 `Py_INCREF`**：该函数会偷取引用，所以需要先 `Py_INCREF(type)` 增加一个引用；失败时还需 `Py_DECREF(type)` 和 `Py_DECREF(module)` 回滚。
3. **`tp_init` 中不重新初始化**：`tp_init` 可能被多次调用（如子类调用 `super().__init__()`），必须先 `Py_XDECREF` 旧对象再创建新对象。
4. **`tp_flags` 缺少 `Py_TPFLAGS_DEFAULT`**：不设置此标志会导致类型行为异常，解释器可能崩溃。

## 相关概念

* [对象模型（§2）](../concepts/02-object-model.md)
* [类型系统（§3）](../concepts/03-type-system.md)
* [引用计数（§4）](../concepts/04-reference-counting.md)
* [垃圾回收（§5）](../concepts/05-garbage-collector.md)
* [最简 C 扩展模块](minimal-c-extension.md)
* [CPython 源码信源登记](../references/cpython-source.md)

[^cpython-source]: CPython 3.16.0a0 源码，类型对象定义于 `Include/cpython/object.h`、`Objects/typeobject.c`，成员定义于 `Include/structmember.h`，见本 bundle 信源登记 [references/cpython-source.md](../references/cpython-source.md)。
