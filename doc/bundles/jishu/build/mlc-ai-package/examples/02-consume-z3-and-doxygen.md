---
type: example
title: 消费 Z3 与 Doxygen
description: 用 pip 装的 Z3 静态库与 Doxygen CLI 搭建一个可复现的文档+求解构建
tags:
  - mlc-ai
  - z3
  - doxygen
  - example
generated: true
verified: false
status: stable
stale_after: "2027-05-01"
sources:
  - "external/dev/libs/mlc-ai/package/packages/mlc-z3-static/README.md"
  - "external/dev/libs/mlc-ai/package/packages/mlc-z3-static/example_project/"
  - "external/dev/libs/mlc-ai/package/packages/mlc-doxygen-bin/README.md"
---

# 消费 Z3 与 Doxygen

## 场景

一个 C++ 项目需要：①链接 Z3 做约束求解；②生成 API 文档。两者都不走系统包管理器，全部由 pip 固定版本。

## 安装

```bash
python -m pip install mlc-z3-static mlc-doxygen-bin
```

验证：

```bash
python -m mlc_z3_static.config --cmake-dir
python -m mlc_z3_static.config --prefix
doxygen --version
```

## 第一部分：链接静态 Z3

### 最小 CMake 项目

```cmake
cmake_minimum_required(VERSION 3.20)
project(smt_demo LANGUAGES C CXX)   # 必须含 CXX，即使只用 C API

find_package(Z3 CONFIG REQUIRED)

add_executable(smt_demo main.cpp)
target_link_libraries(smt_demo PRIVATE z3::libz3)
target_compile_features(smt_demo PRIVATE cxx_std_20)
```

注意 `LANGUAGES C CXX`：Z3 是 C++ 实现，静态归档需要 C++ 运行时与 C++ 链接器，即使你的源码只用 `z3.h` 的 C 接口（该包 README 明确说明）。

### 配置命令

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release \
  -DZ3_DIR="$(python -m mlc_z3_static.config --cmake-dir)"
cmake --build build --parallel
```

### 在 CMake 内部自我定位（不传 -D）

```cmake
find_package(Python3 COMPONENTS Interpreter REQUIRED)
execute_process(
  COMMAND "${Python3_EXECUTABLE}" -m mlc_z3_static.config --cmake-dir
  OUTPUT_STRIP_TRAILING_WHITESPACE
  OUTPUT_VARIABLE Z3_DIR
)
find_package(Z3 CONFIG REQUIRED)
```

适合"CI 里只有一个 python，不想额外传参"的场景。代价是 CMake 配置期强依赖 Python。

### 最小 main.cpp

```cpp
#include <z3++.h>
#include <iostream>

int main() {
  z3::context ctx;
  z3::solver solver(ctx);
  z3::expr x = ctx.int_const("x");
  solver.add(x > 10);
  solver.add(x < 20);
  solver.add(x % 2 == 0);
  std::cout << solver.check() << "\n";          // sat
  z3::model m = solver.get_model();
  std::cout << "x = " << m.eval(x) << "\n";     // 12 / 14 / 16 / 18 之一
  return 0;
}
```

### 验证链接的是静态库

```bash
ldd ./build/smt_demo | grep -i z3 && echo "FAIL: 动态 libz3" || echo "OK: 无动态 libz3"
```

仓库自带的 `tests/python/test_cmake_consumer.py` 做的就是这件事（F-155）。

### 通过 Python 拿到路径

```python
import mlc_z3_static as z3

print(z3.Z3_VERSION, z3.Z3_TAG, z3.Z3_COMMIT)
print(z3.get_cmake_dir())
print(z3.get_cmake_prefix_path())
print(z3.get_static_library_path())
print(z3.get_pkgconfig_dir())
print(z3.metadata()["artifacts"])
```

若要手工链接：

```bash
g++ -std=c++20 main.cpp \
  -I"$(python -c 'import mlc_z3_static as z; print(z.get_include_dir())')" \
  "$(python -c 'import mlc_z3_static as z; print(z.get_static_library_path())')" \
  -o smt_demo
```

Z3 静态库的依赖较少，但仍需 C++ 运行时（`-lstdc++` 由 g++ 自动带上）。

## 第二部分：用 pip 装的 Doxygen 生成文档

### 最小项目

```text
demo/
├── Doxyfile
└── include/
    └── demo.h
```

`include/demo.h`：

```cpp
/** @file demo.h
 *  @brief 演示用头文件。
 */

/** @brief 返回常量 42。
 *  @return 恒为 42。
 */
int answer(void);
```

`Doxyfile` 最小配置：

```text
PROJECT_NAME           = "SMT Demo"
OUTPUT_DIRECTORY       = docs
INPUT                  = include
RECURSIVE              = YES
GENERATE_HTML          = YES
GENERATE_LATEX         = NO
QUIET                  = YES
```

生成：

```bash
doxygen Doxyfile
ls docs/html/index.html
```

### 三条调用通路都可以

```bash
doxygen --version
python -m mlc_doxygen_bin --version
python -c "import mlc_doxygen_bin as d; print(d.get_executable_path())"
```

在 CMake 里插入文档目标：

```cmake
find_package(Python3 COMPONENTS Interpreter REQUIRED)
execute_process(
  COMMAND "${Python3_EXECUTABLE}" -m mlc_doxygen_bin.config  # 若存在
  OUTPUT_VARIABLE _ignored
  ERROR_QUIET
)
find_program(DOXYGEN_EXECUTABLE NAMES doxygen)
add_custom_target(docs
  COMMAND "${DOXYGEN_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/Doxyfile"
  WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
  COMMENT "Generating API docs with pip-installed Doxygen")
```

更省事的写法是直接用 console script 名 `doxygen`——安装后它就在当前环境的 `Scripts`/`bin` 目录里，`find_program` 在激活的 venv 中能找到。

### 检查能力边界

```python
import mlc_doxygen_bin as d
print(d.metadata()["features"])
# {'cli': True, 'doxywizard': False, 'search_tools': False, 'libclang': False}
```

如果你的 Doxyfile 依赖以下能力，需要自己提供：

| 需求 | 本包是否提供 | 替代方案 |
|---|---|---|
| `doxywizard` GUI | ❌ | 系统包或官方发行版 |
| 搜索工具（`doxysearch.cgi`） | ❌ | 系统包 |
| `use_libclang` 解析 | ❌（构建时关闭） | 自行构建或换工具 |
| Graphviz 图形 | ❌ | `apt install graphviz` / `brew install graphviz` |
| LaTeX/PDF 输出 | ❌ | 装 TeX 发行版 |

## 组合场景：一个 CI 脚本

```bash
#!/usr/bin/env bash
set -euo pipefail

python -m pip install mlc-z3-static mlc-doxygen-bin

# 编译并测试
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release \
  -DZ3_DIR="$(python -m mlc_z3_static.config --cmake-dir)"
cmake --build build --parallel
./build/smt_demo

# 断言没有动态 Z3
if ldd ./build/smt_demo | grep -qi z3; then
  echo "unexpected dynamic libz3" >&2
  exit 1
fi

# 生成文档
doxygen Doxyfile
test -f docs/html/index.html
```

这个脚本的价值在于：**版本完全由 pip 决定**，不依赖 apt/brew 的 Z3 与 Doxygen 版本。

## 平台注意事项

| 平台 | Z3 | Doxygen |
|---|---|---|
| Linux x86_64/aarch64 | manylinux_2_28 wheel | manylinux_2_28 wheel |
| macOS arm64 / x86_64 | `macosx_14_0_*` wheel | `macosx_14_0_*` wheel |
| Windows AMD64 | `win_amd64` | `win_amd64` |
| Windows ARM64 | `win_arm64` | **不发布**（iconv 限制） |

Windows ARM64 上需要 Doxygen 时，只能自行构建，且要提供 ARM64 iconv：

```powershell
$env:MLC_DOXYGEN_BIN_EXTRA_CMAKE_ARGS = "-DICONV_DIR=C:/path/to/iconv"
python -m build --wheel
```

## 常见错误

| 症状 | 原因 | 处理 |
|---|---|---|
| `find_package(Z3)` 找不到 | 未传 `Z3_DIR` 或 Python 环境不对 | 显式传 `--cmake-dir` 的结果 |
| 链接期 `undefined reference to __cxa_*` | 用了 `LANGUAGES C` 只有 C 编译器 | 加上 `CXX` |
| `doxygen: Permission denied` | 可执行位丢失（手工解压 wheel） | 用 `pip install` |
| `doxygen` 退出码非零但文档已生成 | 存在文档警告 | 检查输出；`cli.py` 原样透传退出码 |
| `mlc_doxygen_bin.metadata()` 返回 `{}` | 只装了包体，没有 `doxygen.json` | 重新安装 wheel |

## 自检方式

```bash
# Z3
pytest "$(python -c 'import mlc_z3_static, pathlib; print(pathlib.Path(mlc_z3_static.__file__).parent.parent.parent)')/tests/python" -q 2>/dev/null || true
python -c "import mlc_z3_static as z; print(z.metadata()['z3_version'], z.get_static_library_path())"

# Doxygen
doxygen --version
python -c "import mlc_doxygen_bin as d; print(d.metadata()['features'])"
```

## 延伸阅读

- Z3 包的构建裁剪与相对化：[mlc-z3-static 包](../concepts/10-z3-static-package.md)
- Doxygen 包的能力边界：[mlc-doxygen-bin 包](../concepts/11-doxygen-bin-package.md)
- 平台矩阵差异：[CI 工作流与 SDK 缓存](../concepts/13-ci-workflows-and-caching.md)
