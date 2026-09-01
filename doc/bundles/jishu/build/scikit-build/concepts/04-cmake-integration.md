---
type: concept
title: CMake 集成机制
description: scikit-build-core 如何通过 CMake 类和 CMaker 类驱动 CMake 配置、构建和安装
tags:
  - scikit-build
  - build
  - cmake
  - integration
generated: true
verified: false
status: stable
stale_after: "2026-12-01"
sources:
  - "external/libs/tools/scikit-build/scikit-build-core/src/scikit_build_core/cmake.py"
---

# CMake 集成机制

scikit-build-core 的 CMake 集成由两个核心类承担：`CMake`（定位 CMake 可执行文件）和 `CMaker`（执行 configure/build/install 生命周期）。

## CMake 类：可执行文件定位

`CMake` 是一个 frozen dataclass，代表一个 CMake 可执行文件实例：

```python
@dataclass(frozen=True)
class CMake:
    version: Version       # CMake 版本号
    cmake_path: Path       # CMake 可执行文件路径
```

### 默认搜索路径

`CMake.default_search()` 按以下顺序搜索 CMake：

1. `SKBUILD_CMAKE_EXECUTABLE` 环境变量指定的路径
2. pip 安装的 `cmake` 包（通过 `import cmake; cmake.CMAKE_BIN_DIR`）
3. 系统 PATH 中的 `cmake`/`cmake3`

找到后通过 `cmake -E capabilities` 获取版本信息（JSON 格式，比 `--version` 更可靠）。

## CMaker 类：构建生命周期管理

`CMaker` 是一个 dataclass，管理单次 CMake 构建的完整生命周期：

```python
@dataclass
class CMaker:
    cmake: CMake                    # CMake 实例
    source_dir: Path                # 源码目录
    build_dir: Path                 # 构建目录
    build_type: str                 # 构建类型（Release/Debug）
    module_dirs: list[Path]         # CMAKE_MODULE_PATH
    prefix_dirs: list[Path]         # CMAKE_PREFIX_PATH
    prefix_roots: dict[str, list[Path]]  # 分配置前缀路径
    fresh: bool                     # 是否清空重建
    init_cache_file: Path           # 初始缓存文件路径
    env: dict[str, str]             # 环境变量
    single_config: bool             # 是否单配置生成器
    file_api: Index | None          # CMake File API 结果
```

### 初始化（__post_init__）

1. 创建构建目录（`build_dir.mkdir(parents=True, exist_ok=True)`）
2. 检测 stale 缓存（源目录变更时警告或清空）
3. 写入 `.skbuild-info.json` 信息文件

### 初始缓存文件（init_cache）

`init_cache(cache_settings)` 方法生成 `CMakeInit.txt`，使用 CMake `-C` 参数加载：

```cmake
# CMakeInit.txt
set(CMAKE_MODULE_PATH "/path/to/modules" CACHE PATH "..." FORCE)
set(CMAKE_PREFIX_PATH "/path/to/prefix" CACHE PATH "..." FORCE)
set(SKBUILD_PROJECT_NAME "my_package" CACHE STRING "..." FORCE)
set(SKBUILD "1" CACHE STRING "..." FORCE)
```

使用 CMake bracketed argument `[===[...]===]` 避免路径中的转义问题。

scikit-build-core 会自动设置以下 SKBUILD_* 缓存变量：

| 变量 | 值 |
|------|-----|
| `SKBUILD` | `"1"` |
| `SKBUILD_PROJECT_NAME` | 项目名称 |
| `SKBUILD_PROJECT_VERSION` | 项目版本 |
| `SKBUILD_STATE` | `"wheel"` / `"editable"` / `"sdist"` |
| `Python_EXECUTABLE` | 当前 Python 解释器路径 |
| `Python_VERSION` | Python 版本 |

### Configure 阶段

`configure(defines, cmake_args, toolchain)` 执行 `cmake -S source -B build`：

1. 计算命令行参数：`-S`、`-B`、`-G`（生成器）、`--toolchain`、`-C`（init cache）
2. 添加用户 `-D` 定义
3. 设置 `-DCMAKE_BUILD_TYPE`（单配置生成器）
4. 执行 cmake configure 命令
5. 读取 CMake File API 响应（`load_reply_dir`）
6. 将结果存入 `self.file_api`

### Build 阶段

`build(build_args, targets, verbose, build_type)` 执行 `cmake --build`：

```bash
cmake --build build_dir --config Release --target _core --verbose -- -j8
```

- 支持多目标并行构建
- 多配置生成器（Visual Studio、Xcode）需要 `--config` 参数
- verbose 模式传递 `-v` 给底层构建工具
- 额外参数通过 `build_args` 传递（如 `-j8`）

### Install 阶段

`install(prefix, strip, components, targets, build_type)` 执行 `cmake --install`：

```bash
cmake --install build_dir --prefix wheel_temp --component Runtime --strip
```

- `--prefix` 指定安装目标目录（通常是 wheel 临时目录）
- `--component` 按 CMake component 选择性安装
- `--strip` 剥离调试符号
- `--config` 仅多配置生成器需要

## 单配置 vs 多配置生成器

| 特性 | 单配置（Ninja/Makefiles） | 多配置（VS/Xcode） |
|------|--------------------------|-------------------|
| 构建类型 | configure 时设置 `-DCMAKE_BUILD_TYPE` | build 时设置 `--config` |
| 构建目录 | 每个类型一个目录 | 同一目录包含所有类型 |
| 默认平台 | Linux/macOS | Windows |
| single_config 值 | `True` | `False` |

CMaker 在 `__post_init__` 中根据平台和生成器自动设置 `single_config`。

## 构建信息文件

configure 阶段在构建目录写入 `.skbuild-info.json`，记录：

```json
{
  "source_dir": "/path/to/source",
  "build_dir": "/path/to/build",
  "build_type": "Release",
  "cmake_executable": "/usr/bin/cmake",
  "cmake_version": "3.27.0",
  "generator": "Ninja"
}
```

## 跨平台编译器配置

scikit-build-core 不直接设置编译器，而是通过以下机制确保 CMake 找到正确的 Python：

1. `Python_EXECUTABLE` 缓存变量指向当前 Python
2. `python_hints` 选项添加 `-DPython_ROOT_DIR` 等提示
3. macOS 上 `ARCHFLAGS` 环境变量转换为 `-DCMAKE_OSX_ARCHITECTURES`
4. 交叉编译时通过 `cmake.toolchain-file` 指定工具链文件

## 延伸阅读

- [构建流程](05-build-flow.md)——CMaker 在 wheel 构建中的完整调用链
- [CMake File API](09-cmake-file-api.md)——configure 后如何读取构建信息
- [程序搜索与依赖管理](07-program-discovery.md)——CMake/Ninja 搜索算法
