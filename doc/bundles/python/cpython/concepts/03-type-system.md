---
type: Concept
title: "类型系统与 PyTypeObject"
description: "PyTypeObject结构体详解——类型对象的字段布局、方法套件（as_number/as_sequence/as_mapping）、tp_flags类型标志"
tags: [cpython, type, PyTypeObject, type-system, tp_flags, method-table]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-21T18:20:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T18:30:00+08:00" }
status: stable
stale_after: 2027-08-21
sources:
  - id: cpython-source
    resource: /references/cpython-source.md
---

在 CPython 中，**类型本身也是对象**。每个 Python 值的 `ob_type` 指针都指向一个 `PyTypeObject` 实例，该实例描述了该类型的名称、内存布局、支持的操作、以及各种行为钩子。`PyTypeObject` 是 CPython 类型系统的核心结构体，定义于 `Include/cpython/object.h`。

## 类型也是对象

`PyTypeObject` 自身以 `PyObject_VAR_HEAD` 开头，这意味着它也是一个 `PyObject`（准确地说是 `PyVarObject`）。这形成了类型系统的"鸡生蛋"递归关系：

```text
PyTypeObject 实例（如 PyLong_Type）的 ob_type → PyType_Type（即 type 类型本身）
PyType_Type 的 ob_type → PyType_Type（指向自己，形成闭环）
PyBaseObject_Type（即 object 类型）的 ob_type → PyType_Type
```

这种设计意味着类型可以像普通对象一样被传递、赋值、作为函数参数、甚至在运行时动态创建（这正是 Python 中 `class` 语句和 `type()` 构造函数的基础）。

用 C 代码展示这个元类层次：

```c
// PyType_Type 是 "type" 类型本身，它的 ob_type 指向自己
PyAPI_DATA(PyTypeObject) PyType_Type;      /* built-in 'type' */
PyAPI_DATA(PyTypeObject) PyBaseObject_Type; /* built-in 'object' */
PyAPI_DATA(PyTypeObject) PySuper_Type;     /* built-in 'super' */
```

在 Python 层面，这对应：

```python
>>> type(int)           # <class 'type'>
>>> type(type)          # <class 'type'>
>>> type(object)        # <class 'type'>
>>> isinstance(42, int) # True
>>> isinstance(int, type) # True
```

## PyTypeObject 结构体

`PyTypeObject`（即 `struct _typeobject`）是一个包含数十个字段的大型结构体。以下按功能分组介绍各字段，定义位于 `Include/cpython/object.h`。

### 基础字段

```c
struct _typeobject {
    PyObject_VAR_HEAD                    // 标准对象头部（ob_refcnt, ob_type, ob_size）
    const char *tp_name;                 // 类型名称，格式为 "<module>.<name>"
    Py_ssize_t tp_basicsize;             // 实例基本内存大小（字节）
    Py_ssize_t tp_itemsize;              // 变长元素大小（变长类型使用）
```

- **tp_name**：类型的显示名称，用于调试信息、错误消息和 `repr()` 输出。格式为 `"module.Name"`（如 `"builtins.int"`）。对于内置类型，模块名为 `"builtins"`。
- **tp_basicsize**：该类型实例的基础内存分配大小。`PyObject_New()` 等分配函数使用此值确定分配多少字节。
- **tp_itemsize**：对于变长类型（如元组、字节串），这是每个变长元素的大小（字节）。定长类型设为 0。例如元组的 `tp_itemsize = sizeof(PyObject*)`。

### 析构与属性访问

```c
    destructor tp_dealloc;               // 析构函数（引用计数归零时调用）
    Py_ssize_t tp_vectorcall_offset;     // vectorcall 协议偏移（PEP 590）
    getattrfunc tp_getattr;              // 旧式属性访问（已废弃，保留兼容）
    setattrfunc tp_setattr;              // 旧式属性设置（已废弃）
    PyAsyncMethods *tp_as_async;         // 异步方法套件（await/aiter/anext）
    reprfunc tp_repr;                    // __repr__ 实现
```

- **tp_dealloc**：析构函数，当对象引用计数降为 0 时被调用来释放资源和内存。对于静态分配的类型对象，此指针为 `NULL`（因为它们永生不灭）。
- **tp_repr**：实现 `repr(obj)` 和交互式回显。

### 方法套件（Method Suites）

方法套件是一组函数指针的集合，按操作类别组织。类型通过设置相应的套件指针来声明自己支持哪些协议（protocol）：

```c
    PyNumberMethods *tp_as_number;       // 数值操作（加减乘除等）
    PySequenceMethods *tp_as_sequence;   // 序列操作（索引、切片、长度等）
    PyMappingMethods *tp_as_mapping;     // 映射操作（键值查找等）
```

一个类型可以同时实现多个套件。例如，字符串既支持序列协议（`s[0]`、`len(s)`），也通过映射套件支持某些操作。当序列和映射套件同时定义了相同操作时，映射套件优先（见 `PyHeapTypeObject` 中 `as_sequence` 在 `as_mapping` 之后的布局）。

### 标准操作方法

```c
    hashfunc tp_hash;                    // __hash__ 实现
    ternaryfunc tp_call;                 // 调用操作（obj(*args, **kwargs)）
    reprfunc tp_str;                     // __str__ 实现
    getattrofunc tp_getattro;            // 属性获取（obj.attr）
    setattrofunc tp_setattro;            // 属性设置（obj.attr = val）
```

- **tp_hash**：返回对象的哈希值，用于字典键和集合成员。设为 `NULL` 表示不可哈希。
- **tp_call**：使对象可调用。函数对象、类对象、实现了 `__call__` 的对象都设置此字段。
- **tp_getattro** / **tp_setattro**：实现完整的属性访问协议（包括特殊方法查找），替代旧式的 `tp_getattr`/`tp_setattr`。

### 缓冲区协议

```c
    PyBufferProcs *tp_as_buffer;         // 缓冲区协议（PEP 3118）
```

缓冲区协议允许对象暴露其底层内存缓冲区（如 `bytes`、`bytearray`、`array.array`、`memoryview`），用于零拷贝数据访问。

### 类型标志

```c
    unsigned long tp_flags;              // 类型标志位集合
```

`tp_flags` 是一个位掩码，描述类型的各种属性（GC 参与、可子类化、内置类型子类标识等）。详见下文"tp_flags 常量"一节。

### 文档字符串

```c
    const char *tp_doc;                  // 类型文档字符串
```

### GC 相关

```c
    traverseproc tp_traverse;            // GC 遍历：访问所有包含的引用
    inquiry tp_clear;                    // GC 清除：打破循环引用
```

- **tp_traverse**：对于参与循环垃圾回收的容器类型，此函数遍历对象持有的所有 `PyObject*` 引用，供 GC 追踪引用关系。
- **tp_clear**：在 GC 检测到循环引用时调用，清空容器中的引用以打破循环。

只有设置了 `Py_TPFLAGS_HAVE_GC` 标志的类型才需要实现这两个方法。

### 富比较

```c
    richcmpfunc tp_richcompare;          // 富比较（<, <=, ==, !=, >, >=）
```

`tp_richcompare` 实现六个比较运算符，操作类型通过 `op` 参数指定（`Py_LT`、`Py_LE`、`Py_EQ`、`Py_NE`、`Py_GT`、`Py_GE`）。

### 弱引用与迭代器

```c
    Py_ssize_t tp_weaklistoffset;        // 弱引用链表偏移
    getiterfunc tp_iter;                 // __iter__：返回迭代器
    iternextfunc tp_iternext;            // __next__：返回下一个元素
```

### 方法与成员定义

```c
    PyMethodDef *tp_methods;             // 方法定义表
    PyMemberDef *tp_members;             // 成员变量定义表（C 结构体字段暴露）
    PyGetSetDef *tp_getset;              // 属性访问器（getter/setter 对）
```

这些表定义了类型在 Python 层面可见的方法和属性。

### 继承关系

```c
    PyTypeObject *tp_base;               // 基类类型
    PyObject *tp_dict;                   // 类型字典（__dict__）
```

- **tp_base**：指向基类的 `PyTypeObject`。所有 Python 类型最终都继承自 `object`（`PyBaseObject_Type`）。
- **tp_dict**：类型的属性字典，存储方法、类变量、特殊方法等。

### 描述符协议

```c
    descrgetfunc tp_descr_get;           // 描述符 __get__
    descrsetfunc tp_descr_set;           // 描述符 __set__/__delete__
```

描述符协议是 Python 属性访问机制的核心。函数、属性（`property`）、类方法（`classmethod`）、静态方法（`staticmethod`）等都通过描述符协议实现。

### 实例字典偏移

```c
    Py_ssize_t tp_dictoffset;            // 实例 __dict__ 在结构体中的偏移
```

对于支持实例字典的类型，此字段表示 `__dict__` 指针在实例结构体中的字节偏移。具有 `Py_TPFLAGS_MANAGED_DICT` 标志的类型由 VM 自动管理字典位置。

### 构造与初始化

```c
    initproc tp_init;                    // __init__ 初始化
    allocfunc tp_alloc;                  // 实例分配函数
    newfunc tp_new;                      // __new__ 创建实例
```

- **tp_new**：负责创建并返回新实例（类似其他语言中的构造函数）。
- **tp_init**：负责初始化已创建的实例（对应 `__init__`）。
- **tp_alloc**：底层内存分配函数，通常使用 `PyType_GenericAlloc`。

### 内存释放

```c
    freefunc tp_free;                    // 低层内存释放函数
    inquiry tp_is_gc;                    // 判断实例是否参与 GC
```

### MRO 与子类

```c
    PyObject *tp_bases;                  // 基类元组（所有直接基类）
    PyObject *tp_mro;                    // 方法解析顺序（Method Resolution Order）
    PyObject *tp_cache;                  // （已废弃）
    void *tp_subclasses;                 // 子类列表（静态内置类型为索引）
    PyObject *tp_weaklist;               // 弱引用链表（静态类型不使用）
```

- **tp_mro**：方法解析顺序元组，定义多继承时属性查找的顺序。由 C3 线性化算法计算。
- **tp_bases**：直接基类组成的元组。对于单继承类型，只包含一个元素。

### 终结器与向量调用

```c
    destructor tp_del;                   // __del__ 终结器
    unsigned int tp_version_tag;         // 类型属性缓存版本标签
    destructor tp_finalize;              // PEP 442 终结器
    vectorcallfunc tp_vectorcall;        // PEP 590 快速调用协议
```

### VM 内部字段

```c
    /* 以下字段仅供 VM 内部使用 */
    unsigned char tp_watched;            // 类型观察者位集
    uint16_t tp_versions_used;           // 属性缓存版本计数
    _Py_iteritemfunc _tp_iteritem;       // 虚拟迭代器 next 函数
    void *_tp_cache;                     // 特化缓存
};
```

## 方法套件结构详解

### PyNumberMethods：数值操作

定义于 `Include/cpython/object.h`，包含 39 个函数指针，覆盖所有数值运算：

```c
typedef struct {
    binaryfunc nb_add;            // + （加法）
    binaryfunc nb_subtract;       // - （减法）
    binaryfunc nb_multiply;       // * （乘法）
    binaryfunc nb_remainder;      // % （取模）
    binaryfunc nb_divmod;         // divmod()
    ternaryfunc nb_power;         // ** （幂运算）
    unaryfunc nb_negative;        // -x （负号）
    unaryfunc nb_positive;        // +x （正号）
    unaryfunc nb_absolute;        // abs()
    inquiry nb_bool;              // bool() （真值测试）
    unaryfunc nb_invert;          // ~ （按位取反）
    binaryfunc nb_lshift;         // <<
    binaryfunc nb_rshift;         // >>
    binaryfunc nb_and;            // &
    binaryfunc nb_xor;            // ^
    binaryfunc nb_or;             // |
    unaryfunc nb_int;             // int() 转换
    void *nb_reserved;            // （原 nb_long，保留占位）
    unaryfunc nb_float;           // float() 转换

    binaryfunc nb_inplace_add;      // +=
    binaryfunc nb_inplace_subtract; // -=
    binaryfunc nb_inplace_multiply; // *=
    binaryfunc nb_inplace_remainder;// %=
    ternaryfunc nb_inplace_power;   // **=
    binaryfunc nb_inplace_lshift;   // <<=
    binaryfunc nb_inplace_rshift;   // >>=
    binaryfunc nb_inplace_and;      // &=
    binaryfunc nb_inplace_xor;      // ^=
    binaryfunc nb_inplace_or;       // |=

    binaryfunc nb_floor_divide;         // //
    binaryfunc nb_true_divide;          // /
    binaryfunc nb_inplace_floor_divide; // //=
    binaryfunc nb_inplace_true_divide;  // /=

    unaryfunc nb_index;             // __index__（整数上下文转换）

    binaryfunc nb_matrix_multiply;       // @ （矩阵乘法，PEP 465）
    binaryfunc nb_inplace_matrix_multiply;// @=
} PyNumberMethods;
```

关键函数指针类型：
- `binaryfunc`：`PyObject* (*)(PyObject*, PyObject*)` — 二元操作
- `ternaryfunc`：`PyObject* (*)(PyObject*, PyObject*, PyObject*)` — 三元操作（如幂运算含第三个模数参数）
- `unaryfunc`：`PyObject* (*)(PyObject*)` — 一元操作
- `inquiry`：`int (*)(PyObject*)` — 返回 int 的查询（如真值测试返回 0/1/-1）

### PySequenceMethods：序列操作

```c
typedef struct {
    lenfunc sq_length;            // len()
    binaryfunc sq_concat;         // + （序列连接）
    ssizeargfunc sq_repeat;       // * （序列重复）
    ssizeargfunc sq_item;         // s[i] （索引访问）
    void *was_sq_slice;           // （旧切片支持，已废弃）
    ssizeobjargproc sq_ass_item;  // s[i] = x
    void *was_sq_ass_slice;       // （旧切片赋值，已废弃）
    objobjproc sq_contains;       // x in s
    binaryfunc sq_inplace_concat; // +=
    ssizeargfunc sq_inplace_repeat;// *=
} PySequenceMethods;
```

### PyMappingMethods：映射操作

```c
typedef struct {
    lenfunc mp_length;            // len()
    binaryfunc mp_subscript;      // d[key]
    objobjargproc mp_ass_subscript;// d[key] = val / del d[key]
} PyMappingMethods;
```

映射套件只有三个操作，但足以实现字典式键值访问。

### PyAsyncMethods：异步操作

```c
typedef struct {
    unaryfunc am_await;           // __await__
    unaryfunc am_aiter;           // __aiter__
    unaryfunc am_anext;           // __anext__
    sendfunc am_send;             // asend()
} PyAsyncMethods;
```

## tp_flags 常量

`tp_flags` 是位掩码字段，每一位表示类型的一个属性。常用标志如下：

| 常量 | 值 | 含义 |
|------|-----|------|
| `Py_TPFLAGS_HAVE_GC` | `(1UL << 14)` | 实例参与循环垃圾回收（必须实现 `tp_traverse`/`tp_clear`） |
| `Py_TPFLAGS_BASETYPE` | `(1UL << 10)` | 类型可被子类化（不可继承的类型如 `bool` 不设此标志） |
| `Py_TPFLAGS_IMMUTABLETYPE` | `(1UL << 8)` | 类型对象不可变（不能设置/删除类型属性） |
| `Py_TPFLAGS_HEAPTYPE` | `(1UL << 9)` | 类型对象在堆上动态分配（用户定义的 class 属此类） |
| `Py_TPFLAGS_READY` | `(1UL << 12)` | 类型已完成初始化（`PyType_Ready()` 设置） |
| `Py_TPFLAGS_READYING` | `(1UL << 13)` | 类型正在初始化中（防止递归） |
| `Py_TPFLAGS_IS_ABSTRACT` | `(1UL << 20)` | 抽象类型（含抽象方法），不能实例化 |
| `Py_TPFLAGS_HAVE_VECTORCALL` | `(1UL << 11)` | 支持 PEP 590 vectorcall 快速调用协议 |
| `Py_TPFLAGS_DISALLOW_INSTANTIATION` | `(1UL << 7)` | 禁止创建实例（如抽象类型） |
| `Py_TPFLAGS_METHOD_DESCRIPTOR` | `(1UL << 17)` | 行为类似非绑定方法（用于内置方法描述符） |
| `Py_TPFLAGS_LONG_SUBCLASS` | `(1UL << 24)` | 是 `int` 的子类 |
| `Py_TPFLAGS_LIST_SUBCLASS` | `(1UL << 25)` | 是 `list` 的子类 |
| `Py_TPFLAGS_TUPLE_SUBCLASS` | `(1UL << 26)` | 是 `tuple` 的子类 |
| `Py_TPFLAGS_BYTES_SUBCLASS` | `(1UL << 27)` | 是 `bytes` 的子类 |
| `Py_TPFLAGS_UNICODE_SUBCLASS` | `(1UL << 28)` | 是 `str` 的子类 |
| `Py_TPFLAGS_DICT_SUBCLASS` | `(1UL << 29)` | 是 `dict` 的子类 |
| `Py_TPFLAGS_BASE_EXC_SUBCLASS` | `(1UL << 30)` | 是 `BaseException` 的子类 |
| `Py_TPFLAGS_TYPE_SUBCLASS` | `(1UL << 31)` | 是 `type` 的子类 |
| `Py_TPFLAGS_MANAGED_DICT` | `(1UL << 4)` | VM 自动管理实例字典位置 |
| `Py_TPFLAGS_MANAGED_WEAKREF` | `(1UL << 3)` | VM 自动管理弱引用位置 |
| `Py_TPFLAGS_SEQUENCE` | `(1UL << 5)` | 模式匹配中视为序列 |
| `Py_TPFLAGS_MAPPING` | `(1UL << 6)` | 模式匹配中视为映射 |
| `Py_TPFLAGS_ITEMS_AT_END` | `(1UL << 23)` | 变长元素位于实例内存末尾 |

内置子类标志（`Py_TPFLAGS_LONG_SUBCLASS` 等）用于快速类型检查——`PyLong_Check()`、`PyList_Check()` 等宏直接检查这些位，无需遍历 MRO，性能极高：

```c
#define PyLong_Check(op) PyObject_TypeCheck(op, &PyLong_Type)
// 内部实现：Py_IS_TYPE(op, &PyLong_Type) || PyType_FastSubclass(Py_TYPE(op), Py_TPFLAGS_LONG_SUBCLASS)
```

`Py_TPFLAGS_DEFAULT` 被定义为新类型的默认标志值（目前仅包含 `Py_TPFLAGS_HAVE_STACKLESS_EXTENSION`，实际值为 0）。

## 内置类型对象

CPython 为所有内置类型提供了静态分配的 `PyTypeObject` 实例，声明于各类型的头文件中：

| 类型对象 | Python 类型 | 定义文件 |
|---------|-----------|---------|
| `PyLong_Type` | `int` | `Objects/longobject.c` |
| `PyBool_Type` | `bool` | `Objects/boolobject.c` |
| `PyFloat_Type` | `float` | `Objects/floatobject.c` |
| `PyUnicode_Type` | `str` | `Objects/unicodeobject.c` |
| `PyBytes_Type` | `bytes` | `Objects/bytesobject.c` |
| `PyTuple_Type` | `tuple` | `Objects/tupleobject.c` |
| `PyList_Type` | `list` | `Objects/listobject.c` |
| `PyDict_Type` | `dict` | `Objects/dictobject.c` |
| `PySet_Type` | `set` | `Objects/setobject.c` |
| `PyFrozenSet_Type` | `frozenset` | `Objects/setobject.c` |
| `PyFunction_Type` | `function` | `Objects/funcobject.c` |
| `PyCode_Type` | `code` | `Objects/codeobject.c` |
| `PyModule_Type` | `module` | `Objects/moduleobject.c` |
| `PyType_Type` | `type` | `Objects/typeobject.c` |
| `PyBaseObject_Type` | `object` | `Objects/typeobject.c` |

## 静态类型初始化

标准内置类型使用 `PyObject_HEAD_INIT`（或 `PyVarObject_HEAD_INIT`）进行静态初始化，确保类型对象是永生的。以 `PyFloat_Type` 为例（简化示意）：

```c
PyTypeObject PyFloat_Type = {
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
    .tp_name = "float",
    .tp_basicsize = sizeof(PyFloatObject),
    .tp_dealloc = float_dealloc,
    .tp_repr = float_repr,
    .tp_as_number = &float_as_number,
    .tp_hash = float_hash,
    .tp_str = float_str,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_doc = "float(x) -> floating point number\n...",
    .tp_richcompare = float_richcompare,
    .tp_new = float_new,
    // ... 其他字段
};
```

静态类型在 CPython 启动时通过 `_PyStaticType_InitBuiltin()` 完成最终初始化（设置 MRO、字典等），此过程设置 `_Py_TPFLAGS_STATIC_BUILTIN` 和 `Py_TPFLAGS_READY` 标志。

## PyHeapTypeObject：堆类型的内存布局

当用户使用 `class` 语句创建新类型时，类型对象在堆上分配，使用 `PyHeapTypeObject` 结构体，它在 `PyTypeObject` 基础上内联了方法套件实例：

```c
typedef struct _heaptypeobject {
    PyTypeObject ht_type;
    PyAsyncMethods as_async;
    PyNumberMethods as_number;
    PyMappingMethods as_mapping;
    PySequenceMethods as_sequence;   // 注意：as_sequence 在 as_mapping 之后
    PyBufferProcs as_buffer;
    PyObject *ht_name, *ht_slots, *ht_qualname;
    struct _dictkeysobject *ht_cached_keys;
    PyObject *ht_module;
    char *_ht_tpname;
    void *ht_token;
    struct _specialization_cache _spec_cache;
    /* 可选用户槽位，随后是成员 */
} PyHeapTypeObject;
```

注意方法套件的顺序——`as_sequence` 在 `as_mapping` 之后，这确保当两者都定义了相同操作时（如 `__getitem__`），映射套件优先。这是 CPython 源码注释中明确说明的设计决策（见 `add_operators()` in `typeobject.c`）。

## 相关概念

- [对象模型：PyObject 与 PyVarObject](/concepts/02-object-model.md) — 所有对象的基础结构，PyTypeObject 的 ob_base
- [源码目录结构导航](/concepts/01-source-layout.md) — Include/cpython/object.h 和 Objects/typeobject.c 的位置
- [CPython 简介](/concepts/00-introduction.md) — 类型系统在整体架构中的位置
- [CPython 源码信源登记](/references/cpython-source.md) — PyTypeObject 定义路径与完整文件清单

[^cpython-source]: CPython 源码信源，见 [cpython-source.md](/references/cpython-source.md)。结构体定义来自 `Include/cpython/object.h`（CPython 3.16.0a0）。
