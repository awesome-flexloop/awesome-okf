---
type: example
title: 基础 C 扩展
description: 使用 scikit-build-core 构建最简单的 C 扩展 Python 模块的完整示例
tags:
  - scikit-build
  - build
  - c-extension
  - example
  - basic
generated: true
verified: false
status: stable
stale_after: "2026-12-01"
sources:
  - "external/libs/tools/scikit-build/scikit-build-core/src/scikit_build_core/resources/templates/c/"
---

# 示例：基础 C 扩展

本示例展示如何使用 scikit-build-core 构建一个最简单的 C 扩展 Python 模块——一个包含 `add(a, b)` 和 `greet(name)` 函数的 `_math` 模块。

## 项目结构

```
c_ext_demo/
├── pyproject.toml
├── CMakeLists.txt
└── src/
    └── c_ext_demo/
        ├── __init__.py
        └── _math.c
```

## pyproject.toml

```toml
[build-system]
requires = ["scikit-build-core>=0.10", "ninja"]
build-backend = "scikit_build_core.build"

[project]
name = "c-ext-demo"
version = "0.1.0"
description = "A minimal C extension built with scikit-build-core"
requires-python = ">=3.9"
license = "MIT"

[tool.scikit-build]
minimum-version = "build-system.requires"
```

## CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.15)
project(c_ext_demo LANGUAGES C)

# 查找 Python 解释器和开发模块
# Development.Module 比 Development 更精确（不需要嵌入库）
find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)

# 编译 C 扩展模块
# python_add_library 是 FindPython 提供的宏
# MODULE = Python 扩展模块（不是共享库）
# WITH_SOABI = 自动添加 ABI 后缀（.cpython-312-x86_64-linux-gnu.so）
python_add_library(_math MODULE src/c_ext_demo/_math.c WITH_SOABI)

# 安装到 Python 包目录
# DESTINATION 必须与 Python 包名一致
install(TARGETS _math DESTINATION c_ext_demo)
```

## C 源码（src/c_ext_demo/_math.c）

```c
#define PY_SSIZE_T_CLEAN
#include <Python.h>

// add(a, b) -> a + b
static PyObject* math_add(PyObject* self, PyObject* args) {
    long a, b;
    if (!PyArg_ParseTuple(args, "ll", &a, &b)) {
        return NULL;  // 参数解析失败时返回 NULL，Python 自动抛出异常
    }
    return PyLong_FromLong(a + b);
}

// greet(name) -> "Hello, {name}!"
static PyObject* math_greet(PyObject* self, PyObject* args) {
    const char* name;
    if (!PyArg_ParseTuple(args, "s", &name)) {
        return NULL;
    }
    char buf[256];
    snprintf(buf, sizeof(buf), "Hello, %s!", name);
    return PyUnicode_FromString(buf);
}

// 方法表
static PyMethodDef MathMethods[] = {
    {"add",   math_add,   METH_VARARGS, "Add two integers."},
    {"greet", math_greet, METH_VARARGS, "Greet someone by name."},
    {NULL, NULL, 0, NULL}  // 哨兵
};

// 模块定义
static struct PyModuleDef _mathmodule = {
    PyModuleDef_HEAD_INIT,
    "_math",        // 模块名（必须与 .so 文件名一致）
    NULL,           // 模块文档字符串
    -1,             // 模块状态大小（-1 = 全局状态）
    MathMethods     // 方法表
};

// 模块初始化函数
// PyInit__<module_name> 命名规则
PyMODINIT_FUNC PyInit__math(void) {
    return PyModule_Create(&_mathmodule);
}
```

## Python 包初始化（src/c_ext_demo/__init__.py）

```python
"""A minimal C extension demo package."""
from ._math import add, greet

__version__ = "0.1.0"
__all__ = ["add", "greet", "__version__"]
```

## 构建和测试

```bash
# 开发模式安装（自动编译 C 扩展）
pip install -e .

# 测试
python -c "
import c_ext_demo
print(c_ext_demo.add(1, 2))       # 3
print(c_ext_demo.greet('World')) # Hello, World!
print(c_ext_demo.__version__)    # 0.1.0
"

# 构建 wheel
pip install build
python -m build

# 构建 sdist
python -m build --sdist
```

## 关键点说明

### 为什么用 Development.Module

`find_package(Python COMPONENTS Interpreter Development.Module)`：

- `Interpreter`：Python 解释器路径
- `Development.Module`：Python 头文件 + 扩展模块编译所需库
- 不用 `Development`（包含嵌入库 `libpython`），因为扩展模块不需要链接 libpython（Linux/macOS）

### WITH_SOABI 的作用

`WITH_SOABI` 让 CMake 自动为输出文件名添加正确的 ABI 后缀：

```
# 不带 WITH_SOABI
_math.so → 错误！Python 找不到

# 带 WITH_SOABI（Python 3.12, Linux x86_64）
_math.cpython-312-x86_64-linux-gnu.so → 正确
```

### install DESTINATION

`install(TARGETS _math DESTINATION c_ext_demo)` 将编译后的 .so 文件安装到 wheel 中的 `c_ext_demo/` 目录下，与 Python 源码包在一起。这是 Python 导入扩展模块的必要条件。

### 多源文件

如果 C 模块有多个源文件：

```cmake
python_add_library(_math MODULE
    src/c_ext_demo/_math.c
    src/c_ext_demo/utils.c
    WITH_SOABI
)
```

### 添加头文件路径

如果需要额外的 include 目录：

```cmake
target_include_directories(_math PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src/c_ext_demo/include
)
```

### 链接库

```cmake
target_link_libraries(_math PRIVATE m)  # 链接数学库
```

## 延伸阅读

- [pybind11 C++ 模块](pybind11-module.md)——使用 pybind11 简化 C++ 绑定
- [CMake 集成机制](../concepts/04-cmake-integration.md)——理解 CMake 类和 CMaker
- [构建流程](../concepts/05-build-flow.md)——理解从源码到 wheel 的完整流程
