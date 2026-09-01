---
type: Concept
title: "模块与导入系统"
description: "CPython模块导入机制——__builtins__内置模块、导入锁、模块缓存、importlib、_inittab扩展模块注册表"
tags: [cpython, module, import, builtins, importlib, _inittab, module-caching]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-21T16:58:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T17:30:00+08:00" }
status: stable
stale_after: 2027-08-21
sources:
  - id: cpython-source
    resource: /references/cpython-source.md
---

# 模块与导入系统

模块（module）是 Python 代码组织的基本单位。每个 `.py` 文件就是一个模块，包（package）是包含 `__init__.py` 的模块目录。CPython 的导入系统负责查找、加载、编译、缓存模块，是运行时基础设施的核心组成部分。

## PyModuleObject：模块对象

在 C 层面，模块由 `PyModuleObject` 结构体表示，定义在 `Include/moduleobject.h`：

```c
// Include/moduleobject.h（简化）
typedef struct {
    PyObject_HEAD
    PyObject *md_dict;   // 模块的 __dict__，存储所有模块级属性
} PyModuleObject;
```

模块本质上是一个带有字典的对象。模块顶层的赋值（函数定义、类定义、变量赋值）本质上都是在向这个字典中插入键值对。

模块对象具有以下特殊属性：

| 属性 | 含义 |
|------|------|
| `__name__` | 模块的全限定名（如 `os.path`、`__main__`） |
| `__dict__` | 模块的命名空间字典（即 `md_dict`） |
| `__file__` | 模块对应的源文件路径（内置模块无此属性） |
| `__path__` | 包的搜索路径列表（仅包有此属性） |
| `__package__` | 模块所属的包名 |
| `__doc__` | 模块的文档字符串 |
| `__spec__` | 模块规格对象（importlib 使用） |
| `__builtins__` | 内置命名空间（通常指向 builtins 模块的字典或模块本身） |

创建模块对象的 C API：

```c
// 创建新模块对象
PyObject *PyModule_NewObject(PyObject *name);
PyObject *PyModule_New(const char *name);

// 获取/设置模块属性
PyObject *PyModule_GetDict(PyObject *module);
PyObject *PyModule_GetName(PyObject *module);
PyObject *PyModule_GetFilenameObject(PyObject *module);
int PyModule_SetDocString(PyObject *module, const char *docstring);
int PyModule_AddObjectRef(PyObject *module, const char *name, PyObject *value);
```

## 内置模块与 _inittab

CPython 将一组核心模块编译为 C 静态链接模块，这些模块不需要从文件系统加载，启动时即可用。它们通过 **_inittab 表**注册。

```c
// Python/pylifecycle.c 或 Python/import.c（简化示例）
struct _inittab _PyImport_Inittab[] = {
    {"builtins", PyInit_builtins},
    {"__main__", NULL},          // __main__ 特殊处理
    {"sys",      PyInit_sys},
    {"_imp",     PyInit__imp},
    {"_io",      PyInit__io},
    {"_thread",  PyInit__thread},
    {"_warnings", PyInit__warnings},
    {"_weakref", PyInit__weakref},
    // ... 约30~50个核心内置模块
    {NULL, NULL}                 // 哨兵
};
```

`_inittab` 数组的每个条目包含模块名和初始化函数指针。当导入内置模块时，解释器查表找到对应的 `PyInit_<modulename>` 函数并调用它。

外部可以通过 `PyImport_ExtendInittab()` 向表中追加静态链接的 C 扩展模块。

### __builtins__ 模块

`builtins` 模块（在 Python 代码中作为 `__builtins__` 访问）是最核心的内置模块，实现在 `Python/bltinmodule.c` 中。它提供了所有 Python 程序默认可用的内置函数、类型和常量。

```c
// Python/bltinmodule.c 中的模块定义
static struct PyModuleDef builtinsmodule = {
    PyModuleDef_HEAD_INIT,
    "builtins",
    builtins_doc,
    -1,  // m_size = -1 表示单初始化模块
    builtin_methods,  // 模块级方法表
    NULL, NULL, NULL, NULL
};
```

builtins 模块包含：

**内置函数**（在 `builtin_methods` 表中注册）：

| 函数 | 用途 |
|------|------|
| `print()` | 输出到标准流 |
| `len()` | 获取容器长度 |
| `type()` | 获取对象类型 |
| `isinstance()` | 类型检查 |
| `range()` | 创建 range 序列 |
| `getattr()`/`setattr()`/`hasattr()` | 属性访问 |
| `globals()`/`locals()` | 命名空间访问 |
| `__import__()` | 导入函数（import 语句的底层实现） |
| `iter()`/`next()` | 迭代器协议 |
| `open()` | 打开文件 |
| `id()` | 获取对象标识 |
| `repr()`/`str()`/`ascii()`/`format()` | 字符串转换 |
| `sorted()`/`reversed()`/`enumerate()`/`zip()`/`map()`/`filter()` | 迭代工具 |
| `sum()`/`min()`/`max()`/`abs()`/`pow()`/`round()` | 数学运算 |
| `super()`/`property()`/`staticmethod()`/`classmethod()` | 面向对象工具 |

**内置类型**：这些类型本身在 `Objects/` 目录的对应文件中定义，在 `PyInit_builtins()` 中添加到 builtins 模块：

| 类型 | C 结构 |
|------|--------|
| `int` | `PyLongObject`（`Objects/longobject.c`） |
| `float` | `PyFloatObject`（`Objects/floatobject.c`） |
| `str` | `PyUnicodeObject`（`Objects/unicodeobject.c`） |
| `bytes` | `PyBytesObject`（`Objects/bytesobject.c`） |
| `bool` | `PyBoolObject`（`Objects/boolobject.c`） |
| `list` | `PyListObject`（`Objects/listobject.c`） |
| `tuple` | `PyTupleObject`（`Objects/tupleobject.c`） |
| `dict` | `PyDictObject`（`Objects/dictobject.c`） |
| `set`/`frozenset` | `PySetObject`（`Objects/setobject.c`） |
| `object` | `PyBaseObject_Type` |
| `type` | `PyType_Type`（元类） |
| `NoneType` | `_Py_NoneStruct` |
| `NotImplementedType` | `_Py_NotImplementedStruct` |
| `ellipsis` | `_Py_EllipsisObject`（`...`） |

**内置常量**：`None`、`True`、`False`、`NotImplemented`、`Ellipsis`。

**内置异常类型**：定义在 `Objects/exceptions.c` 中，包括 `BaseException`、`Exception`、`TypeError`、`ValueError`、`KeyError`、`AttributeError`、`ImportError`、`SyntaxError` 等完整异常层级。

## 导入流程

当 Python 执行 `import foo` 语句时，触发以下流程：

### 第一步：调用 __import__()

`import` 语句被编译为对 `__import__()` 内置函数的调用，该函数最终进入 `Python/import.c` 中的 `PyImport_ImportModule()` C API：

```c
// Python/import.c
PyObject *PyImport_ImportModule(const char *name)
{
    return PyImport_ImportModuleLevelObject(name, ...);
}
```

### 第二步：查找 sys.modules 缓存

CPython 首先检查 `sys.modules` 字典——这是模块缓存（module cache），键是模块全限定名，值是已加载的模块对象。

```c
// Python/import.c 中的缓存查找
PyObject *modules = PyImport_GetModuleDict();  // 获取 sys.modules
PyObject *m = PyDict_GetItemWithError(modules, name);
if (m != NULL) {
    // 缓存命中：检查是否正在初始化中（处理循环导入）
    // 如果模块状态为 "initializing"，返回未完全初始化的模块对象
    return m;
}
```

如果模块在缓存中存在，直接返回，这就是为什么重复 `import` 不会重新加载模块（除非使用 `importlib.reload()`）。

### 第三步：Finder/Loader 机制

如果缓存未命中，导入系统使用 **Finder** 和 **Loader** 抽象（由 `importlib` 实现）来定位和加载模块：

1. **Finder（查找器）**：知道如何在特定位置查找模块。CPython 内置几种 finder：
   - **BuiltinImporter**：查找 `_inittab` 中的内置模块
   - **FrozenImporter**：查找冻结模块（frozen module，嵌入到解释器二进制中的模块）
   - **PathFinder**：在 `sys.path` 列出的路径中查找文件系统模块（.py/.pyc/.so/.pyd）

2. **Loader（加载器）**：知道如何将找到的模块加载到内存中：
   - 对于 `.py` 文件：编译源代码为字节码（通过[编译器流水线](08-compiler-pipeline.md)），然后执行模块顶层代码
   - 对于 `.pyc` 文件：通过 marshal 反序列化加载 `PyCodeObject`，然后执行
   - 对于 C 扩展（`.so`/`.pyd`）：调用动态链接库的 `PyInit_<modulename>` 函数
   - 对于内置模块：调用 `_inittab` 中注册的初始化函数

Finder 返回一个 **ModuleSpec**（模块规格）对象，包含模块名、加载器、来源位置等信息，然后由 Loader 完成实际加载。

### 第四步：执行模块代码

找到模块源（源码或字节码）后，CPython 执行模块的顶层代码：

1. 创建模块对象，插入 `sys.modules`（标记为"initializing"状态）
2. 为模块创建新的执行帧，执行模块代码对象
3. 模块顶层的 `def`、`class`、赋值语句填充模块的 `__dict__`
4. 执行完毕后，将模块状态更新为"ready"

这就是为什么导入一个模块会执行该模块顶层代码的原因。

## 导入锁

导入不是线程安全的操作——如果两个线程同时尝试导入同一个模块，可能导致重复初始化、部分初始化等问题。CPython 使用**导入锁**（import lock）来防止这种竞态条件。

```c
// Python/import.c 中的导入锁
static PyThread_type_lock import_lock = NULL;  // 全局互斥锁

void _PyImport_AcquireLock(PyThreadState *tstate) {
    PyThread_acquire_lock(import_lock, WAIT_LOCK);
}

int _PyImport_ReleaseLock(PyThreadState *tstate) {
    PyThread_release_lock(import_lock);
    return 0;
}
```

导入锁是一个全局互斥锁（mutex），在模块查找和加载期间持有。在多线程程序中，第一个执行导入的线程获取锁，其他线程阻塞等待。这保证了每个模块只被初始化一次。

**循环导入**（circular import）的处理依赖于缓存的"initializing"状态：当模块 A 在初始化过程中导入模块 B，而 B 又导入 A 时，A 已经在 `sys.modules` 中（尽管尚未完全初始化），B 获得的是 A 的部分初始化状态。这就是为什么循环导入有时能工作（如果 B 只引用 A 中在 B 导入之前已定义的属性），有时会失败。

## sys.modules：模块缓存字典

`sys.modules` 是一个普通的 Python 字典（底层是 `PyDictObject`），映射模块全限定名到模块对象：

```python
import sys
# sys.modules 示例内容
{
    'sys': <module 'sys' (built-in)>,
    'builtins': <module 'builtins' (built-in)>,
    'os': <module 'os' from '/usr/lib/python3.16/os.py'>,
    'os.path': <module 'posixpath' from '/usr/lib/python3.16/posixpath.py'>,
    ...
}
```

特性：
- 内置模块的值是 `<module 'name' (built-in)>`，没有 `__file__` 属性
- `__main__` 始终在其中，表示当前主模块
- 可以手动向 `sys.modules` 注入条目来覆盖或添加模块
- 删除条目后下次 import 会重新加载模块

## C 扩展模块

除了 Python 源码模块和内置模块外，CPython 还支持通过动态链接库形式加载 C 扩展模块。

### PyModuleDef：扩展模块定义

C 扩展通过 `PyModuleDef` 结构体定义模块：

```c
// Include/moduleobject.h
typedef struct PyModuleDef {
    PyModuleDef_Base m_base;       // 基类头（含 ob_base, m_init, m_index, m_copy）
    const char *m_name;            // 模块名
    const char *m_doc;             // 模块文档字符串
    Py_ssize_t m_size;             // 每解释器状态大小（-1=单初始化，>=0=多阶段）
    PyMethodDef *m_methods;        // 模块级函数表
    struct PyModuleDef_Slot *m_slots; // 多阶段初始化槽（PEP 489）
    traverseproc m_traverse;       // GC 遍历函数
    inquiry m_clear;               // GC 清除函数
    freefunc m_free;               // 模块析构函数
} PyModuleDef;
```

模块函数表（`PyMethodDef`）定义模块级函数：

```c
static PyMethodDef mymodule_methods[] = {
    {"add",  my_add,  METH_VARARGS, "Add two numbers"},
    {"greet", my_greet, METH_O,      "Greet a person"},
    {NULL, NULL, 0, NULL}  // 哨兵
};
```

### 单初始化 vs 多阶段初始化

**单初始化**（`m_size = -1`）：传统模式，模块全局状态存储在 C 静态变量中，所有解释器共享同一份状态。不支持子解释器隔离。

```c
// 单初始化入口
PyMODINIT_FUNC PyInit_mymodule(void) {
    PyObject *m = PyModule_Create(&mymoduledef);
    // 添加类型、常量等
    return m;
}
```

**多阶段初始化**（PEP 489，`m_size >= 0`）：每个解释器拥有独立的模块状态，支持子解释器隔离。通过 `Py_mod_create` 和 `Py_mod_exec` 两个槽函数完成初始化。

```c
// 多阶段初始化槽
static struct PyModuleDef_Slot mymodule_slots[] = {
    {Py_mod_create,  mymodule_create},
    {Py_mod_exec,    mymodule_exec},
    {0, NULL}
};

static int mymodule_exec(PyObject *module) {
    // 执行模块初始化（添加函数、类型等）
    return 0;
}
```

## 多解释器隔离

CPython 3.12+ 对**子解释器**（sub-interpreter）提供了更好的支持。子解释器拥有独立的模块命名空间和 `sys.modules` 字典，可以在同一进程中隔离执行 Python 代码。

扩展模块需要通过 `m_size >= 0` 和 `PyModuleDef_Slot` 声明支持多解释器。`m_size = -1` 的旧风格模块在多解释器场景下会导致状态共享问题（因为全局 C 变量在所有解释器间可见）。

与多解释器相关的 API：

```c
// 创建子解释器
PyThreadState *Py_NewInterpreter(void);
// 切换线程状态到指定解释器
PyThreadState *PyThreadState_Swap(PyThreadState *tstate);
// 结束子解释器
void Py_EndInterpreter(PyThreadState *tstate);
```

在自由线程（free-threading/nogil）构建中，导入锁的实现有所不同——模块级别的锁替代了全局导入锁，以减少线程间的阻塞。

## importlib：Python 级导入实现

从 Python 3.3 开始，导入系统的大部分逻辑从 C 层迁移到了 Python 层，由 `importlib` 标准库实现（`Lib/importlib/`）。C 层的 `Python/import.c` 主要负责：

- 启动时的引导（bootstrap）：导入 `_imp` 内置模块后，通过它加载 `importlib._bootstrap`，将导入控制权转交给 Python 代码
- 内置模块和冻结模块的查找
- 导入锁管理
- `sys.modules` 字典操作

`importlib` 提供了完整的抽象基类：

- `importlib.abc.MetaPathFinder`：meta-path finder 的抽象基类
- `importlib.abc.PathEntryFinder`：path entry finder 的抽象基类
- `importlib.abc.Loader`：loader 的抽象基类
- `importlib.abc.SourceLoader`：源码加载器的基类
- `importlib.machinery.ModuleSpec`：模块规格类

用户可以通过向 `sys.meta_path` 添加自定义 finder 来扩展导入机制，实现从 ZIP 文件、远程 URL、数据库等非标准位置加载模块。

## 相关概念

- [编译器流水线](08-compiler-pipeline.md) — 导入模块时触发源代码到字节码的编译，理解编译流程有助于理解导入延迟
- [CPython 简介](00-introduction.md) — 了解模块系统在 CPython 整体架构中的位置
- [解释器帧与执行栈](06-interpreter-frame.md) — 模块执行时创建模块级帧，模块顶层代码在帧中执行
- [CPython 源码信源登记](../references/cpython-source.md) — `Python/import.c`、`Python/bltinmodule.c`、`Include/moduleobject.h` 的路径索引
