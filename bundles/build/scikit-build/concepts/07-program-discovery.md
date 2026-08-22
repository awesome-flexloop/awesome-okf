---
type: concept
title: 程序搜索与依赖管理
description: scikit-build-core 如何搜索和选择 CMake、Ninja、Make 等构建工具，版本约束与超时处理
tags:
  - scikit-build
  - build
  - cmake
  - ninja
  - dependency
generated: true
verified: false
status: stable
stale_after: "2026-12-01"
sources:
  - "external/libs/tools/scikit-build/scikit-build-core/src/scikit_build_core/program_search.py"
  - "external/libs/tools/scikit-build/scikit-build-core/src/scikit_build_core/builder/get_requires.py"
---

# 程序搜索与依赖管理

scikit-build-core 需要在构建时找到 CMake 和构建工具（Ninja/Make）。`program_search.py` 实现了一个分层搜索和版本匹配机制。

## Program 数据结构

```python
class Program(NamedTuple):
    path: Path           # 可执行文件路径
    version: Version | None  # 解析出的版本号
```

每个搜索到的程序都返回 `Program` 实例，包含可执行文件路径和版本信息。

## CMake 搜索

`get_cmake_programs(*, module=True)` 是一个生成器，按优先级顺序产出候选 CMake：

### 搜索顺序

1. **pip 安装的 cmake 模块**（如果 `module=True`）：
   - 通过 `import cmake; cmake.CMAKE_BIN_DIR` 获取 bin 目录
   - 查找目录下的 `cmake` 可执行文件
   - 优点：版本可控，与项目隔离
   - 需要 `[build-system.requires]` 中包含 `cmake`

2. **系统 PATH 中的 cmake**：
   - 依次查找 `cmake`、`cmake3`
   - 适合系统已安装 CMake 的环境（如 Linux 发行版、macOS Homebrew）

3. **环境变量指定**：
   - `SKBUILD_CMAKE_EXECUTABLE` 环境变量可直接指定 CMake 路径
   - 优先级最高（在 `CMake.default_search()` 中最先检查）

### 版本检测

CMake 版本通过两种方式获取（优先级从高到低）：

1. `cmake -E capabilities`：输出 JSON 格式信息，包含 `version.string` 字段
   - 这是最可靠的方式（CMake 3.7+ 支持）
   - 返回信息还包含生成器列表、平台信息
2. `cmake --version`：正则解析输出文本
   - 回退方案，解析 `cmake version X.Y.Z`

## Ninja 搜索

`get_ninja_programs(*, module=True)` 搜索 Ninja 构建工具：

### 搜索顺序

1. **pip 安装的 ninja 模块**（`module=True`）：
   - 通过 `import ninja; ninja.BIN_DIR` 获取路径
2. **系统 PATH 中的 ninja**：
   - 依次查找 `ninja-build`（Debian/Ubuntu 包名）、`ninja`、`samu`（samurai 实现）

### 版本检测

通过 `ninja --version` 输出版本号。

### Make 回退

如果 Ninja 未找到且 `ninja.make-fallback = true`（默认）：

- `get_make_programs()` 搜索 `gmake`（BSD 系统）、`make`
- 生成器切换到 "Unix Makefiles"
- 注意：Make 并行构建效率低于 Ninja

## 版本匹配

`best_program(programs, *, version)` 函数选择满足版本约束的第一个程序：

```python
def best_program(
    programs: Iterable[Program],
    *,
    version: SpecifierSet | None = None,
) -> Program:
```

1. 遍历候选程序
2. 如果指定了 `version`（SpecifierSet），检查版本是否满足约束
3. 返回第一个满足条件的程序
4. 如果都不满足，抛出 `CMakeNotFoundError`（包含所有候选版本信息）

```python
# 示例：需要 CMake >= 3.21
cmake = best_program(get_cmake_programs(), version=SpecifierSet(">=3.21"))
```

## 超时处理

`compute_timeout(executable)` 根据环境调整版本检测超时时间：

| 环境 | 超时 |
|------|------|
| 默认 | 5 秒 |
| CI 环境（CI=true） | 5 秒 |
| Windows | 30 秒（进程创建较慢） |
| Apple Silicon + Rosetta | 10 秒（x86_64 模拟） |

超时后跳过该候选程序，继续搜索下一个。

## 构建依赖声明

`builder/get_requires.py` 中的 `GetRequires` 类在 `get_requires_for_build_wheel()` 阶段计算需要 pip 安装的构建依赖：

| 条件 | 添加的依赖 |
|------|-----------|
| 系统未找到满足版本的 CMake | `cmake>=X.Y`（到 pip 中获取） |
| 系统未找到 Ninja 且 make-fallback 关闭 | `ninja>=1.5` |
| 配置了 dynamic metadata provider | 对应 provider 包 |
| 配置了 variants | variants 相关依赖 |

`GetRequires.from_config_settings()` 分析 config_settings 和 TOML 配置，判断哪些工具需要通过 pip 安装。

## known_wheels.toml

`resources/known_wheels.toml` 记录了已知提供 CMake/Ninja 的 pip 包信息（按平台、版本），避免在已有系统工具时不必要地下载 pip 包。

## 手动指定工具路径

以下环境变量可覆盖自动搜索：

| 环境变量 | 用途 |
|---------|------|
| `SKBUILD_CMAKE_EXECUTABLE` | 指定 CMake 可执行文件路径 |
| `SKBUILD_NINJA_EXECUTABLE` | 指定 Ninja 可执行文件路径 |
| `SKBUILD_MAKE_EXECUTABLE` | 指定 Make 可执行文件路径 |
| `CMAKE_EXECUTABLE` | 替代 `SKBUILD_CMAKE_EXECUTABLE`（兼容） |
