---
type: example
title: pybind11 C++ 模块
description: 使用 scikit-build-core 与 pybind11 构建 C++ Python 绑定模块的完整示例
tags:
  - scikit-build
  - build
  - pybind11
  - cpp
  - example
generated: true
verified: false
status: stable
stale_after: "2026-12-01"
sources:
  - "external/libs/tools/scikit-build/scikit-build-core/src/scikit_build_core/resources/templates/pybind11/"
---

# 示例：pybind11 C++ 模块

本示例展示如何使用 scikit-build-core 与 [pybind11](https://pybind11.readthedocs.io/) 构建 C++ Python 绑定。pybind11 是一个轻量级的 header-only C++ 库，极大简化了 C++ 代码的 Python 绑定。

## 项目结构

```
pybind_demo/
├── pyproject.toml
├── CMakeLists.txt
└── src/
    └── pybind_demo/
        ├── __init__.py
        └── bindings.cpp
```

## pyproject.toml

```toml
[build-system]
requires = [
    "scikit-build-core>=0.10",
    "ninja",
    "pybind11>=2.11",
]
build-backend = "scikit_build_core.build"

[project]
name = "pybind-demo"
version = "0.1.0"
description = "A pybind11 module built with scikit-build-core"
requires-python = ">=3.9"
license = "MIT"

[tool.scikit-build]
minimum-version = "build-system.requires"

# pybind11 通过 CMake config 文件查找
# pip 安装 pybind11 时会提供 pybind11Config.cmake
wheel.py-api = "cp39"
```

## CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.15)
project(pybind_demo LANGUAGES CXX)

# 查找 Python
find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)

# 查找 pybind11（pip 安装或系统安装均可）
find_package(pybind11 CONFIG REQUIRED)

# pybind11_add_module 替代 python_add_library
# 它自动配置 C++ 标准、include 路径、编译标志
pybind11_add_module(_core MODULE src/pybind_demo/bindings.cpp)

# 可选：设置 C++ 标准
target_compile_features(_core PRIVATE cxx_std_17)

# 安装到 Python 包目录
install(TARGETS _core DESTINATION pybind_demo)
```

## C++ 绑定源码（src/pybind_demo/bindings.cpp）

```cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>      // STL 容器自动转换
#include <string>
#include <vector>
#include <cmath>

namespace py = pybind11;

// 简单函数
int add(int a, int b) {
    return a + b;
}

// 带默认参数的函数
std::string greet(const std::string& name = "World") {
    return "Hello, " + name + "!";
}

// C++ 类
class Calculator {
public:
    Calculator() : value_(0) {}

    void reset() { value_ = 0; }
    void add(double x) { value_ += x; }
    double get() const { return value_; }
    double sqrt() const { return std::sqrt(value_); }

private:
    double value_;
};

// 接受 STL 容器
std::vector<int> double_list(const std::vector<int>& v) {
    std::vector<int> result;
    result.reserve(v.size());
    for (int x : v) result.push_back(x * 2);
    return result;
}

// 绑定定义
PYBIND11_MODULE(_core, m) {
    m.doc() = "pybind11 demo module built with scikit-build-core";

    // 绑定函数
    m.def("add", &add, "Add two integers", py::arg("a"), py::arg("b"));
    m.def("greet", &greet, "Greet someone",
          py::arg("name") = "World");
    m.def("double_list", &double_list, "Double all elements in a list",
          py::arg("values"));

    // 绑定类
    py::class_<Calculator>(m, "Calculator")
        .def(py::init<>())           // 默认构造函数
        .def("reset", &Calculator::reset)
        .def("add", &Calculator::add, py::arg("x"))
        .def("get", &Calculator::get)
        .def("sqrt", &Calculator::sqrt)
        .def("__repr__", [](const Calculator& c) {
            return "<Calculator value=" + std::to_string(c.get()) + ">";
        });

    // 绑定版本常量
    m.attr("__version__") = "0.1.0";
}
```

## Python 包初始化（src/pybind_demo/__init__.py）

```python
from ._core import Calculator, add, greet, double_list, __version__

__all__ = ["Calculator", "add", "greet", "double_list", "__version__"]
```

## 构建和测试

```bash
pip install -e .

python -c "
import pybind_demo

# 简单函数
print(pybind_demo.add(1, 2))          # 3
print(pybind_demo.greet())            # Hello, World!
print(pybind_demo.greet('scikit-build'))  # Hello, scikit-build!

# STL 容器转换
print(pybind_demo.double_list([1,2,3]))  # [2, 4, 6]

# C++ 类
calc = pybind_demo.Calculator()
calc.add(10)
calc.add(5)
print(calc.get())   # 15.0
print(calc.sqrt())  # 3.872...
print(calc)         # <Calculator value=15.000000>
"
```

## 常见配置

### 多源文件

```cmake
pybind11_add_module(_core MODULE
    src/pybind_demo/bindings.cpp
    src/pybind_demo/math_utils.cpp
    src/pybind_demo/string_utils.cpp
)
```

### 链接外部 C++ 库

```cmake
find_package(OpenCV REQUIRED)
target_link_libraries(_core PRIVATE ${OpenCV_LIBS})
```

### C++ 标准设置

```cmake
target_compile_features(_core PRIVATE cxx_std_20)
# 或
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
```

### 编译选项

```cmake
if(MSVC)
    target_compile_options(_core PRIVATE /W4 /O2)
else()
    target_compile_options(_core PRIVATE -Wall -Wextra -O3)
endif()
```

### 稳定 ABI（abi3）

```toml
[tool.scikit-build.wheel]
py-api = "abi3"
```

```cmake
pybind11_add_module(_core MODULE src/pybind_demo/bindings.cpp)
# pybind11 自动处理 abi3 宏定义
# 要求 CPython 3.9+
```

使用 abi3 后，一个 wheel 可以兼容多个 Python 版本（3.9+），但需要确保不使用版本特定的 C API。

### nanobind 替代

如果需要更小的二进制体积和更快的编译速度，可以用 [nanobind](https://nanobind.readthedocs.io/) 替代 pybind11：

```toml
[build-system]
requires = ["scikit-build-core>=0.10", "nanobind>=0.2", "ninja"]
```

```cmake
find_package(nanobind CONFIG REQUIRED)
nanobind_add_module(_core src/pybind_demo/bindings.cpp)
install(TARGETS _core DESTINATION pybind_demo LIBRARY DESTINATION pybind_demo)
```

绑定代码几乎相同（`#include <nanobind/nanobind.h>`，`NB_MODULE` 替代 `PYBIND11_MODULE`）。

## 调试构建

```bash
# Debug 模式（带调试符号，无优化）
pip install -ve . --no-build-isolation -Ccmake.build-type=Debug

# 使用 ASAN（地址消毒器，Linux/macOS）
CFLAGS="-fsanitize=address" LDFLAGS="-fsanitize=address" \
    pip install -ve . --no-build-isolation -Ccmake.build-type=Debug
```
