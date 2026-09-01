---
type: concept
title: 快速开始
description: 从零开始创建一个使用 scikit-build-core 的 C 扩展 Python 包
tags:
  - scikit-build
  - build
  - quickstart
  - getting-started
generated: true
verified: false
status: stable
stale_after: "2026-12-01"
sources:
  - "external/libs/tools/scikit-build/scikit-build-core/pyproject.toml"
  - "external/libs/tools/scikit-build/scikit-build-core/src/scikit_build_core/resources/templates/"
---

# 快速开始

## 前置要求

- Python 3.9+
- CMake 3.15+（`pip install cmake` 或系统安装）
- Ninja（可选，推荐；`pip install ninja` 或系统安装）
- C/C++ 编译器（GCC、Clang、MSVC 均可）

## 最简项目结构

创建一个包含 C 扩展的 Python 包，只需要两个配置文件和源码：

```
my_package/
├── pyproject.toml       # 构建配置
├── CMakeLists.txt       # CMake 构建脚本
├── src/
│   └── my_package/
│       ├── __init__.py
│       └── _core.c     # C 扩展源码
```

## pyproject.toml 配置

```toml
[build-system]
requires = ["scikit-build-core>=0.10", "ninja"]
build-backend = "scikit_build_core.build"

[project]
name = "my-package"
version = "0.1.0"
description = "A minimal scikit-build-core example"
requires-python = ">=3.9"
license = "MIT"

[tool.scikit-build]
minimum-version = "build-system.requires"
```

要点说明：
- `build-backend` 必须设为 `"scikit_build_core.build"`
- `requires` 列出构建时依赖（scikit-build-core、ninja、可选 cmake）
- `minimum-version = "build-system.requires"` 自动从 requires 中提取版本约束

## CMakeLists.txt 配置

```cmake
cmake_minimum_required(VERSION 3.15)
project(my_package LANGUAGES C)

# 查找 Python 解释器和开发文件
find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)

# 编译 C 扩展模块
python_add_library(_core MODULE src/my_package/_core.c WITH_SOABI)

# 安装到 Python 包目录
install(TARGETS _core DESTINATION my_package)
```

关键点：
- `find_package(Python COMPONENTS Interpreter Development.Module)` 查找 Python
- `python_add_library` 创建 Python 扩展模块目标
- `WITH_SOABI` 自动添加 ABI 后缀（如 `.cpython-312-x86_64-linux-gnu.so`）
- `install(TARGETS ... DESTINATION my_package)` 安装到包目录

## C 扩展示例（src/my_package/_core.c）

```c
#define PY_SSIZE_T_CLEAN
#include <Python.h>

static PyObject* add(PyObject* self, PyObject* args) {
    long a, b;
    if (!PyArg_ParseTuple(args, "ll", &a, &b))
        return NULL;
    return PyLong_FromLong(a + b);
}

static PyMethodDef Methods[] = {
    {"add", add, METH_VARARGS, "Add two integers"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef _coremodule = {
    PyModuleDef_HEAD_INIT, "_core", NULL, -1, Methods
};

PyMODINIT_FUNC PyInit__core(void) {
    return PyModule_Create(&_coremodule);
}
```

## 包初始化（src/my_package/__init__.py）

```python
from ._core import add

__all__ = ["add"]
```

## 构建和安装

```bash
# 构建 wheel
pip install build
python -m build

# 开发模式安装（editable）
pip install -e .

# 测试
python -c "import my_package; print(my_package.add(1, 2))"
```

## 使用 scikit-build-core init 初始化项目

scikit-build-core 内置项目初始化命令：

```bash
pip install scikit-build-core
scikit-build-core init
```

交互式向导支持：c（纯 C）、abi3（稳定 ABI）、cython、fortran、nanobind、pybind11、swig 等模板。

## 常见配置速查

### 使用 pybind11

`pyproject.toml` 额外添加依赖：
```toml
[build-system]
requires = ["scikit-build-core>=0.10", "ninja", "pybind11>=2.11"]
```

`CMakeLists.txt` 中：
```cmake
find_package(pybind11 CONFIG REQUIRED)
pybind11_add_module(_core src/my_package/bindings.cpp)
install(TARGETS _core DESTINATION my_package)
```

### Debug 构建

```bash
pip install --no-build-isolation -ve . -Ccmake.build-type=Debug
```

### 详细构建输出

```bash
python -m build -Cbuild.verbose=true
```

## 下一步

- [配置系统详解](03-settings-system.md)——掌握三源配置和优先级
- [CMake 集成机制](04-cmake-integration.md)——理解 CMaker 工作原理
- [构建流程](05-build-flow.md)——深入 wheel 构建全链路
