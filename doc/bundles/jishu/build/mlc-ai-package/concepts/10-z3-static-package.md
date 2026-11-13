---
type: concept
title: mlc-z3-static 包
description: 静态 Z3 的构建裁剪、CMake/pkg-config 相对化与许可证强制
tags:
  - mlc-ai
  - z3
  - cmake
  - pkg-config
generated: true
verified: false
status: stable
stale_after: "2027-05-01"
sources:
  - "external/dev/libs/mlc-ai/package/packages/mlc-z3-static/README.md"
  - "external/dev/libs/mlc-ai/package/packages/mlc-z3-static/scripts/prepare_z3.py"
  - "external/dev/libs/mlc-ai/package/packages/mlc-z3-static/pyproject.toml"
  - "external/dev/libs/mlc-ai/package/packages/mlc-z3-static/python/mlc_z3_static/__init__.py"
---

# mlc-z3-static 包

## 定位

这是一个**只提供原生开发产物**的 Z3 包：

- Z3 的 C 与 C++ 头文件；
- 位置无关的静态 `libz3`（Unix 上 `libz3.a`，Windows 上 `.lib`）；
- 可重定位的 CMake 与 pkg-config 元数据。

它**不提供 Z3 的 Python 绑定**（该包 README 首段明确）。需要 `z3-solver` 那种 API 的读者应另装官方包——这是一个刻意的范围收缩。

钉扎版本：`Z3_VERSION = "5.3.1"`，commit `ac9156f9...`，归档 SHA-256 `33558971...`（F-020）。

## 内层构建：把 Z3 裁剪成"只有静态库"

`prepare_z3.py` 的 `cmake_configure_command()` 显式关闭了几乎所有可选产物（F-109）：

```python
"-DCMAKE_POSITION_INDEPENDENT_CODE=ON",
"-DCMAKE_CXX_STANDARD=20",
"-DCMAKE_CXX_STANDARD_REQUIRED=ON",
"-DZ3_BUILD_LIBZ3_SHARED=OFF",
...
"-DZ3_BUILD_PYTHON_BINDINGS=OFF", "-DZ3_INSTALL_PYTHON_BINDINGS=OFF",
"-DZ3_BUILD_DOTNET_BINDINGS=OFF", "-DZ3_INSTALL_DOTNET_BINDINGS=OFF",
"-DZ3_BUILD_JAVA_BINDINGS=OFF", "-DZ3_INSTALL_JAVA_BINDINGS=OFF",
"-DZ3_BUILD_GO_BINDINGS=OFF",
"-DZ3_BUILD_OCAML_BINDINGS=OFF",
"-DZ3_BUILD_JULIA_BINDINGS=OFF",
"-DZ3_ENABLE_EXAMPLE_TARGETS=OFF",
"-DZ3_BUILD_EXECUTABLE=OFF",
"-DZ3_BUILD_TEST_EXECUTABLES=OFF",
"-DZ3_USE_LIB_GMP=OFF",
"-DZ3_INCLUDE_GIT_DESCRIBE=OFF", "-DZ3_INCLUDE_GIT_HASH=OFF",
```

逐项理由：

| 设置 | 理由 |
|---|---|
| `Z3_BUILD_LIBZ3_SHARED=OFF` | 只发静态库；避免 `auditwheel` 修复需求 |
| 各语言绑定全关 | 本包不承担"Z3 语言绑定发行版"的角色 |
| `Z3_BUILD_EXECUTABLE=OFF` | 不要 `z3` 命令行工具 |
| `Z3_USE_LIB_GMP=OFF` | 避免引入 GMP 依赖，保持自包含 |
| `Z3_INCLUDE_GIT_*` | 不在产物里写入 git 描述/哈希，保证可复现 |

C++20 是硬要求（Z3 5.x 使用 `<format>`），因此 `CMAKE_CXX_STANDARD_REQUIRED=ON`。该包 README 提示需要 GCC ≥ 13 / Clang ≥ 17 / VS 2022。

## Windows 的架构传递

这是本包最容易踩坑的一处（F-110）：

```python
def cmake_generator_platform(generator: str | None) -> str | None:
    if platform.system() != "Windows":
        return None
    if generator and not generator.startswith("Visual Studio"):
        return None
    explicit = os.environ.get("MLC_Z3_STATIC_CMAKE_GENERATOR_PLATFORM")
    if explicit:
        return explicit
    return _WINDOWS_GENERATOR_PLATFORMS.get(platform.machine().upper())
```

映射表：

| `platform.machine()` | `-A` 值 |
|---|---|
| `AMD64` / `X86_64` | `x64` |
| `ARM64` / `AARCH64` | `ARM64` |
| `X86` | `Win32` |

注释解释了必要性的两个层次：

1. **外层 scikit-build-core 会把 `CMAKE_GENERATOR_PLATFORM` 传进来**，它派生自目标 wheel 平台（例如 `win_arm64` → `ARM64`）；
2. **若没有传入，则回落到构建解释器架构**，避免"在 ARM64 上构建却静默产出 x64 库"。

注意 `if generator and not generator.startswith("Visual Studio")` 这一行：Ninja 不认 `-A`，只有 Visual Studio 生成器需要平台参数。

## 相对化：CMake 导出与 pkg-config

### CMake 导出

上游 Z3 生成的 `Z3Targets.cmake` 会写入配置时的绝对前缀：

```cmake
set(_IMPORT_PREFIX "/abs/path/to/staging")
```

`relativize_cmake_export()` 把它替换为四层相对推导（F-111）：

```cmake
get_filename_component(_IMPORT_PREFIX "${CMAKE_CURRENT_LIST_FILE}" PATH)
get_filename_component(_IMPORT_PREFIX "${_IMPORT_PREFIX}" PATH)
get_filename_component(_IMPORT_PREFIX "${_IMPORT_PREFIX}" PATH)
get_filename_component(_IMPORT_PREFIX "${_IMPORT_PREFIX}" PATH)
if(_IMPORT_PREFIX STREQUAL "/")
  set(_IMPORT_PREFIX "")
endif()
```

为什么是四层：`Z3Targets.cmake` 位于 `<prefix>/lib/cmake/z3/`，向上四层正好回到 `<prefix>`。

然后 `validate_relocatable_cmake_exports()` 反向检查（F-112）：

```python
for path in exported_files:
    text = path.read_text(encoding="utf-8")
    if absolute_stage in text:
        raise RuntimeError(f"Z3 {kind} CMake export is not relocatable: {path...} contains {absolute_stage!r}")
```

"替换 + 校验"必须成对出现：只替换不校验，无法发现某些导出文件用了别的写法；只校验不替换，则会一直红。

### 两代导出文件名

Z3 4.x 用 `Z3Targets.cmake`，Z3 5.x 用 `Z3-<kind>-targets.cmake`。代码同时识别（F-113）：

```python
paths = {*cmake_dir.glob("Z3Targets*.cmake"), *cmake_dir.glob("Z3-*-targets*.cmake"),
         *cmake_dir.glob("Z3-*-dependencies.cmake")}
```

这是一处"兼容两代上游"的显式适配，比硬编码单一文件名更稳。

### pkg-config

```python
replacements = {
    "prefix": "${pcfiledir}/../..",
    "exec_prefix": "${prefix}",
    "libdir": "${exec_prefix}/lib",
    "sharedlibdir": "${exec_prefix}/lib",
    "includedir": "${prefix}/include",
}
```

与 LLVM 侧的做法一致，但 Z3 多处理了 `exec_prefix` / `libdir` / `sharedlibdir` / `includedir` 四个派生键，因为上游 `.pc` 里这些通常也是绝对路径。

## 许可证：必须来自校验过的归档

```python
def write_license(package_dir: Path, source_dir: Path) -> str:
    source_license = source_dir / "LICENSE.txt"
    if not source_license.is_file():
        raise RuntimeError(f"Z3 source archive has no LICENSE.txt at {source_license}")
    shutil.copy2(source_license, dest)
```

目标名 `LICENSE-Z3.txt`，与仓库根的 `LICENSE`（Z3 上游许可证的逐字副本）区分开。该包 README 说明：

- 仓库里的 `LICENSE` 让目录与 sdist 自包含；
- wheel 里的 `licenses/LICENSE-Z3.txt` 来自 SHA-256 校验过的上游归档；
- 构建失败如果该文件缺失。

## 元数据与运行期 API

`staticlib.json` 记录（F-114 相关）：

```python
{
    "name": "z3", "z3_version": ..., "z3_tag": ..., "z3_commit": ...,
    "source_repository": "https://github.com/Z3Prover/z3",
    "source_archive_url": ..., "source_archive_sha256": ...,
    "package_version": ..., "artifacts": {...}, "license": ...,
    "platform": platform.platform(), "python": sys.version.split()[0],
}
```

`artifacts` 是按 kind 组织的路径表（`prefix`、`include_dir`、`library_dir`、`library`、`cmake_prefix_path`、`cmake_dir`、`pkgconfig_dir`），全部**相对于包目录**。

Python 侧（`mlc_z3_static/__init__.py`）提供：

| 函数 | 返回 |
|---|---|
| `artifact_kinds()` | 实际存在的 kind（当前只有 `static`） |
| `get_include_dir()` / `get_library_dir()` / `get_pkgconfig_dir()` | 对应目录 |
| `get_library_path()` / `get_static_library_path()` | 静态库文件路径 |
| `get_cmake_prefix_path()` / `get_cmake_dir()` | CMake 用 |
| `metadata()` | `staticlib.json` 内容 |

`_VALID_KINDS = {"static"}` 是唯一合法 kind，其他值抛 `ValueError`。这保留了未来扩展 `shared` 的位置，但当前明确只支持 static。

库文件名在四个候选里找（F-114 相关）：`libz3.a`、`z3.lib`、`libz3.lib`、`libz3-static.lib`——覆盖 MSVC 与 MinGW 的不同命名。

## 消费方式

该包 README 给出两条 CMake 路线：

**路线一：命令行传 `Z3_DIR`**

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release \
  -DZ3_DIR="$(python -m mlc_z3_static.config --cmake-dir)"
```

```cmake
cmake_minimum_required(VERSION 3.20)
project(my_z3_consumer LANGUAGES C CXX)
find_package(Z3 CONFIG REQUIRED)
add_executable(my_z3_consumer main.cpp)
target_link_libraries(my_z3_consumer PRIVATE z3::libz3)
target_compile_features(my_z3_consumer PRIVATE cxx_std_20)
```

**路线二：在 CMake 内部调 Python**

```cmake
find_package(Python3 COMPONENTS Interpreter REQUIRED)
execute_process(
  COMMAND "${Python3_EXECUTABLE}" -m mlc_z3_static.config --cmake-dir
  OUTPUT_STRIP_TRAILING_WHITESPACE
  OUTPUT_VARIABLE Z3_DIR
)
find_package(Z3 CONFIG REQUIRED)
```

一个容易忽略的约束：**Z3 是 C++ 实现，C-only 消费者也要 `LANGUAGES C CXX`**，让 CMake 用 C++ 链接器处理静态归档（该包 README 明确说明）。

`example_project/` 提供了一个 uv 管理的完整消费示例。

## 测试

`tests/python/test_cmake_consumer.py`（F-155）做的是端到端验证：构建并链接一个小程序，并断言它**没有链接动态 `libz3`**。`test_config.py` 覆盖版本元数据、路径与 CLI。

cibuildwheel 的 `test-command` 在干净 venv 里对这些测试跑一遍（F-037），因此每个 wheel 都被实测过。

## 自检方式

```bash
# 1) 只构建静态库
grep -n "Z3_BUILD_LIBZ3_SHARED" packages/mlc-z3-static/scripts/prepare_z3.py

# 2) 导出文件无绝对路径
python - <<'PY'
from pathlib import Path
import mlc_z3_static as z
for p in Path(z.get_cmake_dir()).rglob("*.cmake"):
    t = p.read_text(encoding="utf-8")
    if str(Path(z.get_cmake_dir()).parent.parent.parent) in t:
        print("LEAK:", p)
print("checked")
PY

# 3) pkg-config 前缀相对
grep -rn "prefix=" packages/mlc-z3-static/python/mlc_z3_static/static/lib/pkgconfig/*.pc

# 4) 消费者不链动态库
pytest packages/mlc-z3-static/tests/python -q
```

## 陷阱

- **Windows ARM64 必须显式传 `-A ARM64`**：否则可能静默产出 x64 库，且直到链接时才暴露。
- **不要期待 `z3` 命令行或 Python 绑定**：两者都被关闭。
- **`Z3-<kind>-dependencies.cmake` 也要纳入相对化**：`exported_cmake_files()` 已包含它，自定义脚本别漏。
- **`wheel.exclude = ["mlc_z3_static/shared/**"]` 是清理残留**：旧版就地构建可能留下 `shared/`，不加排除会被打进 wheel。
- **C++20 编译器是硬门槛**：GCC 12 及以下会在 `<format>` 上失败。

## 延伸阅读

- 与 LLVM 包的共同结构：[scikit-build-core 与内层 CMake 流水线](03-scikit-build-inner-cmake-pipeline.md)
- 消费示例：[消费 Z3 与 Doxygen](../examples/02-consume-z3-and-doxygen.md)
- 同仓库的另一个 CLI 包：[mlc-doxygen-bin 包](11-doxygen-bin-package.md)
