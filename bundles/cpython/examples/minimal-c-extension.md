---
type: Example
title: 最简 C 扩展模块
description: 从零编写一个CPython C扩展模块——模块定义、方法表、PyInit函数、setup.py构建
tags: [cpython, c-extension, example, module, PyModuleDef, PyInit]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-21T17:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T17:30:00+08:00" }
status: stable
stale_after: 2027-08-21
sources:
  - id: cpython-source
    resource: /references/cpython-source.md
---

# 最简 C 扩展模块

C 扩展模块（C extension module）是编译为共享库（Unix 上为 `.so`，Windows 上为 `.pyd`）的二进制模块，可以像普通 Python 模块一样被 `import` 语句加载。C 扩展直接调用 CPython 的 C API（Application Programming Interface），适合性能关键路径、封装已有 C 库或操作底层系统资源。[^cpython-source]

本示例从零构建一个名为 `spam` 的最简 C 扩展模块，包含系统命令调用和整数加法两个函数，涵盖模块定义、方法表、初始化函数、参数解析和 setuptools 构建的完整流程。

## 1. C 扩展模块的四层结构

一个最简化的 C 扩展模块由四个核心部分组成：

| 层次 | C 结构/函数 | 作用 |
|------|------------|------|
| 方法函数 | 静态 C 函数 | 实现具体的 Python 可调用功能，返回 `PyObject*` |
| 方法表 | `PyMethodDef[]` | 声明模块导出的所有方法名、函数指针、参数类型和文档字符串 |
| 模块定义 | `PyModuleDef` | 描述模块本身的名称、文档、大小和方法表 |
| 入口函数 | `PyInit_<modulename>` | 模块加载时由解释器调用的初始化入口 |

## 2. 完整 C 源码：spammodule.c

创建 `spammodule.c` 文件，内容如下：

```c
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdlib.h>

/* ========== 方法函数层 ========== */

/*
 * spam.system(command) -> int
 *
 * 调用 C 标准库 system() 执行 shell 命令，返回退出状态码。
 * 参数解析使用 PyArg_ParseTuple，格式字符串 "s" 表示一个 str 参数。
 */
static PyObject*
spam_system(PyObject* self, PyObject* args)
{
    const char* command;
    int sts;

    /* PyArg_ParseTuple 解析位置参数："s" = const char*（Python str → C 字符串） */
    if (!PyArg_ParseTuple(args, "s", &command)) {
        return NULL;  /* 解析失败时返回 NULL，解释器自动抛出异常 */
    }

    sts = system(command);

    /* PyLong_FromLong 将 C long 转为 Python int 对象 */
    return PyLong_FromLong(sts);
}

/*
 * spam.add(a, b) -> int
 *
 * 接受两个整数参数并返回它们的和。演示多参数解析与值返回。
 */
static PyObject*
spam_add(PyObject* self, PyObject* args)
{
    long a, b, result;

    /* "ll" 表示两个 long 参数 */
    if (!PyArg_ParseTuple(args, "ll", &a, &b)) {
        return NULL;
    }

    result = a + b;
    return PyLong_FromLong(result);
}

/*
 * spam.greet(name) -> str
 *
 * 返回拼接后的问候语字符串，演示 PyUnicode_FromFormat 的用法。
 */
static PyObject*
spam_greet(PyObject* self, PyObject* args)
{
    const char* name;

    if (!PyArg_ParseTuple(args, "s", &name)) {
        return NULL;
    }

    /* PyUnicode_FromFormat 类似于 printf，安全地构建 Python str 对象 */
    return PyUnicode_FromFormat("Hello, %s! (from C extension)", name);
}

/*
 * spam.nop() -> None
 *
 * 不接受参数、不返回有意义值的函数，演示 Py_RETURN_NONE 宏。
 */
static PyObject*
spam_nop(PyObject* self, PyObject* args)
{
    /* 无参数时仍需检查 args，传 "" 表示无参数 */
    if (!PyArg_ParseTuple(args, "")) {
        return NULL;
    }

    /* Py_RETURN_NONE 宏：Py_INCREF(Py_None) 并 return Py_None */
    Py_RETURN_NONE;
}

/* ========== 方法表层 ========== */

/*
 * PyMethodDef 数组：每个条目定义一个可从 Python 调用的方法。
 * 字段顺序：{ ml_name, ml_meth, ml_flags, ml_doc }
 *
 * ml_flags 常用值：
 *   METH_VARARGS — 接受位置参数 (self, args)
 *   METH_KEYWORDS — 接受关键字参数 (self, args, kwargs)，需配合 METH_VARARGS 使用
 *   METH_NOARGS — 不接受参数 (self, NULL)
 *   METH_O — 接受单个对象参数 (self, arg)
 *
 * 数组必须以 {NULL, NULL, 0, NULL} 哨兵结束。
 */
static PyMethodDef SpamMethods[] = {
    {"system",  spam_system, METH_VARARGS,
     "Execute a shell command. Return the exit status code."},
    {"add",     spam_add,    METH_VARARGS,
     "Add two integers: add(a, b) -> a + b"},
    {"greet",   spam_greet,  METH_VARARGS,
     "Return a greeting string: greet(name) -> str"},
    {"nop",     spam_nop,    METH_NOARGS,
     "Do nothing and return None."},
    {NULL, NULL, 0, NULL}  /* 哨兵（sentinel），标志数组结束 */
};

/* ========== 模块定义层 ========== */

/*
 * PyModuleDef 结构体：描述模块的元信息。
 *
 * 字段顺序：m_base, m_name, m_doc, m_size, m_methods, m_slots, m_traverse, m_clear, m_free
 *
 * - PyModuleDef_HEAD_INIT 是 m_base 的标准初始化宏，不可省略
 * - m_name 为模块全限定名（点分形式），单模块时即模块名
 * - m_size 对于不支持子解释器状态的模块传 -1
 * - m_methods 指向上面的 PyMethodDef 数组
 */
static struct PyModuleDef spammodule = {
    PyModuleDef_HEAD_INIT,
    "spam",                                     /* m_name：模块名 */
    "A minimal C extension module example.\n"
    "Provides system(), add(), greet(), nop().", /* m_doc：模块文档字符串 */
    -1,                                         /* m_size：per-interpreter 状态大小，-1 表示全局 */
    SpamMethods,                                /* m_methods：方法表 */
    NULL,                                       /* m_slots：槽位函数表（多阶段初始化用） */
    NULL,                                       /* m_traverse：GC 遍历函数 */
    NULL,                                       /* m_clear：GC 清除函数 */
    NULL                                        /* m_free：模块释放函数 */
};

/* ========== 入口函数层 ========== */

/*
 * PyInit_spam：模块初始化入口函数。
 *
 * 命名规则：PyInit_<module_name>，其中 <module_name> 必须与 .so/.pyd 文件名一致。
 * 该函数在 import spam 时由解释器自动调用，必须返回 PyObject*（模块对象）。
 *
 * 返回 NULL 表示初始化失败，解释器将抛出 ImportError。
 */
PyMODINIT_FUNC
PyInit_spam(void)
{
    PyObject* m;

    /* PyModule_Create 根据 PyModuleDef 创建模块对象 */
    m = PyModule_Create(&spammodule);
    if (m == NULL) {
        return NULL;
    }

    /* 可在此处添加模块级常量，例如定义 spam.error 异常类 */
    /* PyModule_AddStringConstant(m, "__version__", "1.0.0"); */

    return m;
}
```

## 3. 关键 API 详解

### 3.1 参数解析：`PyArg_ParseTuple`

`PyArg_ParseTuple(PyObject* args, const char* format, ...)` 从位置参数元组中提取 C 类型值，返回 `1` 表示成功、`0` 表示失败（此时已设置异常）。

| 格式字符 | C 类型 | Python 类型 | 说明 |
|---------|--------|------------|------|
| `"s"` | `const char*` | `str` | UTF-8 编码的 C 字符串（不可修改） |
| `"l"` | `long` | `int` | 长整数 |
| `"i"` | `int` | `int` | 普通整数 |
| `"d"` | `double` | `float` | 双精度浮点数 |
| `"O"` | `PyObject*` | 任意 | 获取对象引用（不转换） |
| `"|l"` | `long`（可选） | `int` | `|` 之后的参数为可选 |

对于关键字参数，使用 `PyArg_ParseTupleAndKeywords(args, kwargs, format, kwlist, ...)`，其中 `kwlist` 是 `const char*[]` 关键字名数组。

### 3.2 值返回宏与函数

| API | 用途 |
|-----|------|
| `PyLong_FromLong(long v)` | C `long` → Python `int` |
| `PyUnicode_FromString(const char* s)` | C 字符串 → Python `str`（UTF-8） |
| `PyUnicode_FromFormat(const char* fmt, ...)` | 格式化构建 Python `str`（类似 printf） |
| `PyFloat_FromDouble(double v)` | C `double` → Python `float` |
| `PyBool_FromLong(long v)` | C 布尔 → Python `bool` |
| `Py_RETURN_NONE` | 返回 `None`（自动 INCREF） |
| `Py_RETURN_TRUE` / `Py_RETURN_FALSE` | 返回 `True` / `False` |
| `return NULL` | 表示错误，解释器检查异常状态 |

### 3.3 模块创建：`PyModule_Create`

`PyModule_Create(PyModuleDef* def)` 根据 `PyModuleDef` 创建新的模块对象。它在内部完成：

1. 分配 `PyModuleObject` 内存
2. 设置模块的 `__name__`、`__doc__`、`__file__` 属性
3. 将方法表中的方法注册为模块函数
4. 返回新引用（new reference），调用者持有引用

## 4. 构建：setup.py

创建 `setup.py` 使用 setuptools 编译 C 扩展：

```python
# setup.py
from setuptools import setup, Extension

# 定义一个 Extension 对象：模块名 + 源文件列表
spam_module = Extension(
    "spam",                       # 模块名（必须与 PyInit_xxx 中的 xxx 一致）
    sources=["spammodule.c"],     # C 源文件列表
    # extra_compile_args=["-O2"],  # 可选：额外编译参数
)

setup(
    name="spam",
    version="1.0.0",
    description="A minimal C extension module example",
    ext_modules=[spam_module],    # ext_modules 列表告知 setuptools 编译 C 扩展
)
```

## 5. 编译与测试

### 编译（开发模式）

使用 `pip` 以可编辑模式安装，或直接通过 `build_ext` 命令编译：

```bash
# 方式一：开发模式安装（推荐，修改 C 代码后只需重新运行此命令）
pip install -e .

# 方式二：仅编译，输出 .so/.pyd 到 build/ 目录
python setup.py build_ext --inplace
```

编译成功后，项目目录下会生成 `spam.cpython-316-<platform>.so`（Linux/macOS）或 `spam.pyd`（Windows）文件。

### 测试

```python
# test_spam.py
import spam

# 测试 add()
result = spam.add(3, 4)
print(f"spam.add(3, 4) = {result}")  # 输出: spam.add(3, 4) = 7
assert result == 7

# 测试 greet()
msg = spam.greet("World")
print(f"spam.greet('World') = {msg}")  # 输出: Hello, World! (from C extension)

# 测试 nop() 返回 None
assert spam.nop() is None

# 测试 system()
exit_code = spam.system("echo Hello from C extension")
print(f"system() exit code: {exit_code}")

# 查看模块文档
print(f"Module doc: {spam.__doc__}")
print(f"system doc: {spam.system.__doc__}")
```

运行：

```bash
python test_spam.py
```

### 常见问题排查

- **`ImportError: dynamic module does not define module export function (PyInit_spam)`**：检查 `PyInit_` 后缀是否与 `Extension("spam", ...)` 的模块名完全一致。
- **编译时找不到 `Python.h`**：确认已安装 Python 开发包（Linux 上为 `python3-dev` 或 `python3-devel`），或使用虚拟环境中的 Python。
- **Windows 上链接错误**：需要安装 Visual Studio Build Tools 并使用正确的 Python 版本（32/64 位匹配）。

## 6. 关键字参数示例（进阶）

如需支持关键字参数，将方法标志设为 `METH_VARARGS | METH_KEYWORDS`，并使用 `PyArg_ParseTupleAndKeywords`：

```c
static PyObject*
spam_divide(PyObject* self, PyObject* args, PyObject* kwargs)
{
    long a, b;
    static char* kwlist[] = {"numerator", "denominator", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "ll", kwlist, &a, &b)) {
        return NULL;
    }
    if (b == 0) {
        PyErr_SetString(PyExc_ZeroDivisionError, "division by zero");
        return NULL;
    }
    return PyLong_FromLong(a / b);
}

/* 在 SpamMethods 中添加： */
/* {"divide", spam_divide, METH_VARARGS | METH_KEYWORDS, "Divide two numbers: divide(numerator, denominator)"} */
```

其中 `PyErr_SetString(PyExc_ZeroDivisionError, "message")` 设置了一个 Python 异常，返回 `NULL` 后解释器会抛出该异常。

## 相关概念

* [对象模型（§2）](/concepts/02-object-model.md)
* [类型系统（§3）](/concepts/03-type-system.md)
* [引用计数（§4）](/concepts/04-reference-counting.md)
* [模块导入（§9）](/concepts/09-module-import.md)
* [CPython 源码信源登记](/references/cpython-source.md)

[^cpython-source]: CPython 3.16.0a0 源码，核心头文件为 `Include/Python.h`、`Include/moduleobject.h`、`Include/modsupport.h`（PyArg_ParseTuple 等），见本 bundle 信源登记 [references/cpython-source.md](/references/cpython-source.md)。
