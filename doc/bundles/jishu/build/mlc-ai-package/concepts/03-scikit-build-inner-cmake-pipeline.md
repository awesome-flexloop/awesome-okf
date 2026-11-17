---
type: concept
title: scikit-build-core 与内层 CMake 流水线
description: 外层 PEP 517 后端如何只做 staging 与 install，内层脚本如何接管真正的原生构建
tags:
  - mlc-ai
  - scikit-build-core
  - cmake
  - build-pipeline
generated: true
verified: false
status: stable
stale_after: "2027-05-01"
sources:
  - "external/dev/libs/mlc-ai/package/packages/mlc-llvm-static/pyproject.toml"
  - "external/dev/libs/mlc-ai/package/packages/mlc-llvm-static/CMakeLists.txt"
  - "external/dev/libs/mlc-ai/package/packages/mlc-z3-static/CMakeLists.txt"
  - "external/dev/libs/mlc-ai/package/packages/mlc-doxygen-bin/CMakeLists.txt"
---

# scikit-build-core 与内层 CMake 流水线

## 两层结构，职责分离

这三个包都采用同一套"外层 + 内层"结构：

```text
pip / build
   └─ scikit-build-core（PEP 517 后端，外层）
        └─ cmake 配置 + 构建（内层，LANGUAGES NONE）
             └─ add_custom_target → python scripts/prepare_<upstream>.py
                  └─ 下载 / 校验 / 编译上游 / staging
             └─ install(...) → wheel 内的 python/<module>/
```

关键点：**内层 CMake 工程不编译任何 C/C++ 代码**。它声明 `project(... LANGUAGES NONE)`（F-031、F-035），本身只做两件事——执行 Python 脚本、把 staging 目录声明为安装产物。

### 为什么让 CMake 当"外壳"

三个理由，都能从代码推出：

1. **scikit-build-core 的安装语义是 CMake install**。`install(DIRECTORY ... DESTINATION mlc_llvm_static)` 直接决定 wheel 里的路径与权限（`USE_SOURCE_PERMISSIONS` 保住可执行位，F-034）。
2. **通用性**。原生 SDK 可能是静态库、可执行文件、CMake 导出或 pkg-config 文件，CMake 的 `install()` 能统一表达。
3. **可观测性**。CMake 构建日志天然分节，`COMMENT "Preparing the LLVM static development SDK"` 让 CI 日志可读。

代价是多一跳：真正的构建逻辑不在 `CMakeLists.txt` 里，而在 `scripts/*.py`。所以读这个仓库时**不要只看 CMake 文件就以为懂了构建**。

## mlc-llvm-static：默认拒绝源码构建

这是全仓库最重要的一个设计决策，写在 `CMakeLists.txt` 开头（F-032）：

```cmake
if(NOT "$ENV{MLC_LLVM_STATIC_ALLOW_SOURCE_BUILD}" STREQUAL "1"
   AND "$ENV{MLC_LLVM_STATIC_PREFIX}" STREQUAL "")
  message(FATAL_ERROR
    "Install an mlc-llvm-static wheel. To build LLVM explicitly, set "
    "MLC_LLVM_STATIC_ALLOW_SOURCE_BUILD=1; to package an existing SDK produced "
    "by this project, set MLC_LLVM_STATIC_PREFIX.")
endif()
```

含义：如果有人 `pip install mlc-llvm-static` 而 PyPI 上没有对应平台的 wheel，pip 会退回 sdist 构建。默认情况下这一步**立刻失败**，而不是默默开始几小时的 LLVM 编译。要构建必须显式选择两条路之一：

| 环境变量 | 含义 |
|---|---|
| `MLC_LLVM_STATIC_ALLOW_SOURCE_BUILD=1` | 真的从源码编译 |
| `MLC_LLVM_STATIC_PREFIX=<path>` | 重新打包一份已存在的 SDK（不编译） |

这是一个"失败快"的防御：错误信息本身就给出了两条出路。

### staging 与 install 的对应关系

```cmake
set(stage "${CMAKE_BINARY_DIR}/staged/mlc_llvm_static")
add_custom_target(stage_mlc_llvm_static ALL
  COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/scripts/build_wheels.py"
    --stage-native "${stage}" --work-root "${CMAKE_BINARY_DIR}/llvm-build"
  ...)
install(DIRECTORY "${stage}/static" "${stage}/licenses" DESTINATION mlc_llvm_static
  USE_SOURCE_PERMISSIONS)
install(FILES "${stage}/staticlib.json" "${stage}/_version.py" DESTINATION mlc_llvm_static)
```

由此可以读出 wheel 内的最终布局：

```text
mlc_llvm_static/
├── __init__.py
├── _llvm_config.py
├── config.py
├── _version.py            ← 生成
├── staticlib.json         ← 生成（native 概况）
├── static/                ← 生成（SDK 全部内容）
│   ├── bin/llvm-config[.py]
│   ├── include/llvm/...
│   ├── lib/*.a + lib/cmake/llvm/...
│   └── share/mlc-llvm-static/base.json
└── licenses/
```

注意 `DESTINATION mlc_llvm_static` 没有前导 `python/`：`wheel.packages = ["python/mlc_llvm_static"]`（F-028）决定源码包根，而 `install()` 的 DESTINATION 是**wheel 内的相对路径**。所以 staging 目录里的 `static/` 会变成 `site-packages/mlc_llvm_static/static/`。

## mlc-z3-static / mlc-doxygen-bin：把外层 CMake 信息传进内层

这两者的 `CMakeLists.txt` 几乎是同构的模板（F-035）：

```cmake
set(MLC_Z3_STATIC_STAGE_DIR "${CMAKE_BINARY_DIR}/staged/mlc_z3_static")
set(MLC_Z3_STATIC_BUILD_ROOT "${CMAKE_BINARY_DIR}/z3-build")

add_custom_target(stage_mlc_z3_static ALL
  COMMAND "${CMAKE_COMMAND}" -E env
    "MLC_Z3_STATIC_PACKAGE_DIR=${MLC_Z3_STATIC_STAGE_DIR}"
    "MLC_Z3_STATIC_BUILD_ROOT=${MLC_Z3_STATIC_BUILD_ROOT}"
    "MLC_Z3_STATIC_CMAKE_COMMAND=${CMAKE_COMMAND}"
    "MLC_Z3_STATIC_CMAKE_GENERATOR=${CMAKE_GENERATOR}"
    "MLC_Z3_STATIC_CMAKE_GENERATOR_PLATFORM=${CMAKE_GENERATOR_PLATFORM}"
    "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/scripts/prepare_z3.py"
  ...)
```

五个环境变量各有用处：

| 变量 | 为什么必须传 |
|---|---|
| `*_PACKAGE_DIR` | 决定 staging 落到哪个目录，供后续 `install()` 取用 |
| `*_BUILD_ROOT` | 把内层构建目录固定在 CMake 的 build tree 内，便于清理 |
| `*_CMAKE_COMMAND` | 使用**外层已解析到的那一个** cmake，避免 PATH 上是旧版本（F-036） |
| `*_CMAKE_GENERATOR` | 内层沿用同一生成器（Ninja / Visual Studio），否则多配置与单配置语义会打架 |
| `*_CMAKE_GENERATOR_PLATFORM` | Windows 上把 `-A x64` / `-A ARM64` 传给内层，保证 ARM64 wheel 不会混进 x64 库（F-110） |

最后一项是最容易忽略的：cibuildwheel 为 `win_arm64` 构建时，外层 CMake 已经知道目标是 ARM64，但内层是重新 configure 的独立工程。如果不显式传递，`platform.machine()` 只反映**构建解释器**的架构，可能产出错误的库。

## 外层 pyproject 的三处关键配置

### 1. 版本必须动态

```toml
[project]
dynamic = ["version"]

[tool.scikit-build.metadata.version]
provider = "scikit_build_core.metadata.regex"
input = "version.py"
```

正则 provider 直接在 `version.py` 文本里找 `__version__ = "..."`，因此源码树导入失败也不影响打包。

### 2. wheel 标签必须是 py3-none

```toml
[tool.scikit-build]
wheel.py-api = "py3"
```

原生 wheel 不含 CPython 扩展模块，所以 `py3`（而非 `cp311`）才是正确的 API 标签。cibuildwheel 的 `build = "cp311-*"`（F-037）只是"用 3.11 解释器跑构建"，不改变产物标签。

### 3. sdist 必须排除全部生成物

```toml
sdist.exclude = [
  "build", "dist", "wheelhouse", ".sdk-cache",
  "extra-targets",
  "python/mlc_llvm_static/static",
  "python/mlc_llvm_static/licenses",
  "python/mlc_llvm_static/staticlib.json",
  "python/mlc_llvm_static/_version.py",
]
```

`extra-targets` 被排除是因为它是**独立的、只发 wheel 的分发**（`wheel.packages = []`，F-023 所在的 pyproject）。把 add-on 打进基础包 sdist 会让 `pip install --no-binary` 走进一个不该存在的路径。

## 一次 `python -m build --wheel` 发生了什么

以 z3 为例，按时间顺序：

1. PEP 517 前端（`build` 或 `pip`）创建隔离环境，安装 `scikit-build-core>=0.11`、`cmake>=3.26`、`ninja`。
2. scikit-build-core 读取 `pyproject.toml`，从 `version.py` 取版本。
3. 配置 CMake：生成 `build/{wheel_tag}/`，执行 `CMakeLists.txt` —— 只有 `add_custom_target` 与 `install()`，无编译。
4. 构建 `stage_mlc_z3_static` 目标：调 `prepare_z3.py`，下载并校验 Z3 归档（或复用 `MLC_Z3_STATIC_SOURCE_DIR`），用内层 CMake 编译静态库，`install` 到 staging，做路径相对化并校验。
5. `install()` 规则把 staging 内容放进 wheel 布局。
6. scikit-build-core 收集 `wheel.packages` 指向的 Python 包，组装 wheel（`py3-none-<platform>`）。
7. cibuildwheel 的 `repair-wheel-command` 执行 `copy_wheel.py`——原样复制，不做 auditwheel 修复（因为不含共享库）。
8. cibuildwheel 的 `test-command` 在一个干净 venv 里装 wheel 并跑 `pytest`。

第 7 步值得强调：多数项目的 repair 命令是 `auditwheel repair`，这里却是 `shutil.copy2`。因为产物没有任何需要"打包进 wheel"的共享库——恰恰是这个包的设计目标。

## 自检方式

```bash
# 1) 内层不编译源码
grep -n "LANGUAGES NONE" packages/*/CMakeLists.txt

# 2) LLVM 默认拒绝隐式源码构建
grep -n "ALLOW_SOURCE_BUILD" packages/mlc-llvm-static/CMakeLists.txt

# 3) z3/doxygen 的五个 env 传递齐全
grep -n "CMAKE_GENERATOR_PLATFORM" packages/mlc-z3-static/CMakeLists.txt \
  packages/mlc-doxygen-bin/CMakeLists.txt

# 4) wheel 标签是 py3
grep -n 'py-api' packages/*/pyproject.toml
```

## 陷阱

- **`install(DESTINATION ...)` 与 `wheel.packages` 是两套路径**：前者是 wheel 内相对路径，后者是源码树路径。写错会得到"文件在 wheel 里但不在包目录下"的奇怪布局。
- **不要在 `CMakeLists.txt` 里加 `project(... LANGUAGES C CXX)`**：一旦声明语言，CMake 会要求编译器并可能触发不必要的探测；这里的工程本来就不编译。
- **`MLC_LLVM_STATIC_PREFIX` 重打包路径不做编辑**：它只复制并重新校验（`prepare_llvm.py` 的 `validate_prefix()`），所以传入的 SDK 必须已包含 `licenses/` 与 `staticlib.json`。
- **`build/{wheel_tag}` 会按 wheel 标签分目录**：同一 checkout 里为不同平台构建不会互相覆盖，但也意味着磁盘占用会累积。

## 延伸阅读

- 上游钉扎：[上游源码钉扎与供应链校验](04-source-pinning-and-provenance.md)
- 真正编译 LLVM 的那一层：[LLVM SDK 构建配方](05-llvm-sdk-build-recipe.md)
- 可复用的 scikit-build-core 基础：[scikit-build-core 知识库](../../scikit-build/index.md)
