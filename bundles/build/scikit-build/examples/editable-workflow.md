---
type: example
title: Editable 开发工作流
description: 使用 scikit-build-core 的 editable 模式进行 C++ 扩展开发，rebuild-on-import 实现快速迭代
tags:
  - scikit-build
  - build
  - editable
  - development
  - workflow
  - example
generated: true
verified: false
status: stable
stale_after: "2026-12-01"
sources:
  - "external/libs/tools/scikit-build/scikit-build-core/src/scikit_build_core/build/_editable.py"
---

# 示例：Editable 开发工作流

Editable 模式（`pip install -e .`）让开发者可以修改源码后无需重新 pip install 即可测试变更。对于 C/C++ 扩展，scikit-build-core 提供了独特的 rebuild-on-import 功能，实现真正的"修改→保存→运行"循环。

## 场景：开发一个 C++ 矩阵运算库

### 项目结构

```
matrixlib/
├── pyproject.toml
├── CMakeLists.txt
├── src/
│   └── matrixlib/
│       ├── __init__.py
│       ├── py.typed
│       └── matrix.cpp
└── tests/
    └── test_matrix.py
```

### pyproject.toml（推荐开发配置）

```toml
[build-system]
requires = ["scikit-build-core>=0.10", "ninja", "pybind11>=2.11"]
build-backend = "scikit_build_core.build"

[project]
name = "matrixlib"
version = "0.1.0"
requires-python = ">=3.9"

[tool.scikit-build]
minimum-version = "build-system.requires"
cmake.build-type = "Debug"    # 开发时用 Debug（带调试符号）
build.verbose = true          # 显示编译命令

[tool.scikit-build.editable]
mode = "redirect"             # redirect 模式（支持 rebuild-on-import）
rebuild = true                # 导入时自动检测并重编译
verbose = true                # 显示重定向日志
```

### CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.15)
project(matrixlib LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)
find_package(pybind11 CONFIG REQUIRED)

pybind11_add_module(_matrix MODULE src/matrixlib/matrix.cpp)

# Debug 模式下启用 ASAN（可选）
# target_compile_options(_matrix PRIVATE -fsanitize=address)
# target_link_options(_matrix PRIVATE -fsanitize=address)

install(TARGETS _matrix DESTINATION matrixlib)
```

## 开发流程

### 1. 初始安装

```bash
# editable 模式安装（首次会完整编译）
pip install -e . -v

# 验证
python -c "import matrixlib; print('OK')"
```

安装成功后，site-packages 中生成重定向文件，Python 从源码目录加载 .py 文件，从构建目录加载 .so 文件。

### 2. 修改 C++ 源码

编辑 `src/matrixlib/matrix.cpp`，修改矩阵乘法实现：

```cpp
// 修改前
m.def("multiply", [](const py::array_t<double>& a, ...) {
    // 简单实现...
});

// 修改后——添加循环展开优化
m.def("multiply", [](const py::array_t<double>& a, ...) {
    // 优化实现...
});
```

### 3. 直接测试（无需手动 build！）

```bash
# 直接运行测试——rebuild-on-import 自动检测到 .cpp 变更，重编译
python -c "
import matrixlib
import numpy as np
a = np.array([[1,2],[3,4]])
b = np.array([[5,6],[7,8]])
print(matrixlib.multiply(a, b))
"
```

输出类似：
```
[scikit-build-core editable] Rebuilding _matrix because matrix.cpp changed
[1/1] Building CXX object CMakeFiles/_matrix.dir/src/matrixlib/matrix.cpp.o
[1/1] Linking CXX shared module _matrix.cpython-312-x86_64-linux-gnu.so
[[19 22]
 [43 50]]
```

### 4. 修改 Python 源码（即时生效）

编辑 `src/matrixlib/__init__.py`，添加新函数：

```python
from ._matrix import multiply, add

def version_info():
    return {"matrixlib": "0.1.0", "backend": "pybind11"}
```

直接运行，无需任何重编译（.py 文件的变更由 Python 自身的导入系统处理）：

```bash
python -c "import matrixlib; print(matrixlib.version_info())"
```

### 5. 运行测试

```bash
pip install pytest
pytest tests/ -v
```

每次导入 `matrixlib` 时，editable finder 检查 C++ 源文件时间戳，如果 CMakeLists.txt 或 .cpp 文件有变更则自动重编译。

## rebuild-dir 模式（推荐）

为了避免编译产物污染源码树，使用 `rebuild-dir`：

```toml
[tool.scikit-build.editable]
mode = "redirect"
rebuild = true
rebuild-dir = "build/editable"
verbose = true
```

```bash
# .gitignore 添加
echo "build/" >> .gitignore
```

此时：
- 编译产物输出到 `build/editable/` 独立目录
- 源码树干净（无 .so 文件）
- 重编译自动安装到 `build/editable/`
- editable finder 从重编译目录加载 .so 文件

## 关闭 rebuild（手动构建）

如果不想每次导入都检查（大型项目可能有性能开销）：

```toml
[tool.scikit-build.editable]
mode = "redirect"
rebuild = false
verbose = false
```

修改 C++ 后手动重构建：

```bash
# 方式1：重新安装（最快）
pip install -e . --no-deps

# 方式2：直接调用 cmake 构建
cd build/editable  # 或临时构建目录
cmake --build .
```

## Inplace 模式（简单项目）

对于纯 Python + 简单 C 扩展，可以用 inplace 模式：

```toml
[tool.scikit-build.editable]
mode = "inplace"
```

```bash
pip install -e .
```

此时 CMake 将 .so 文件直接输出到源码目录中（`src/matrixlib/`）。修改 C++ 后需要手动重新运行 `pip install -e .` 或 `cmake --build`。

## 多包开发工作流

同时开发多个相互依赖的 scikit-build-core 包：

```bash
# 包 A（基础库）
cd /path/to/liba
pip install -e .

# 包 B（依赖 A）
cd /path/to/libb
pip install -e .

# 在 B 中修改 A 的 C++ 代码后
# A 的 rebuild-on-import 自动重编译 A
python -c "import libb; libb.use_a_function()"
```

## CI 中禁用 Editable

在 CI/CD 环境中，始终使用普通安装（非 editable）：

```bash
pip install .
# 或构建 wheel
python -m build
pip install dist/matrixlib-*.whl
```

## 常见问题

**Q: rebuild-on-import 太慢怎么办？**
A: 设置 `rebuild = false`，修改 C++ 后手动运行 `pip install -e . --no-deps`。

**Q: 编辑器（VS Code）找不到 .so 文件？**
A: 使用 inplace 模式或将 `build/editable/` 添加到 Python 分析路径。

**Q: 编译出错但错误信息被吞了？**
A: 设置 `verbose = true` 和 `build.verbose = true`，完整显示编译命令和错误。

**Q: 切换 Python 版本后 editable 不工作？**
A: 每个 Python 环境需要单独 `pip install -e .`，因为 .so 文件是 Python 版本特定的。
