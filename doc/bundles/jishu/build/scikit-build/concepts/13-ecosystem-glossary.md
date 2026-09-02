---
type: Concept
title: 生态对比、工具链与术语表
description: scikit-build-core 的生态全景：八种 Python 二进制构建后端完整对比与选型建议、协同生态工具表（语言绑定/CI 集成/wheel 修复/构建前端）、核心术语表（ABI3/auditwheel/cibuildwheel/File API/FindPython/manylinux 等 20+ 术语）、近期版本变更要点。
tags: [scikit-build-core, ecosystem, comparison, glossary, wheel, cibuildwheel]
generated: { by: agent:learning-bundles-merge, at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: 2027-09-02
sources:
  - id: learning-skbuild-wiki
    resource: SpecWeave docs/knowledge/learning/04-docs-markup-tooling/scikit-build-core-wiki/（00-overview.md、06-resources.md）
    title: scikit-build-core 全面教程（learning 侧合并来源，基于 v0.12.2）
---

# 生态对比、工具链与术语表

本篇补充 scikit-build-core 的生态全景与选型参考。项目定位与四方简对比见[简介](00-introduction.md)，PEP 517 钩子见 [PEP 517 构建后端接口](01-pep517-build-backend.md)，wheel 打包细节见 [Wheel 与 SDist 打包](06-wheel-and-sdist.md)。

## 为什么需要 scikit-build-core

Python 扩展模块（C/C++/Fortran/Cython/SWIG/pybind11/nanobind 等绑定）的构建与分发长期受困于三大难题：

1. **CMake 集成复杂**：CMake 是跨平台 C/C++ 构建系统的事实标准，但 Python 打包工具（setuptools/distutils）原生不懂 CMake，开发者只能手写 `setup.py` 调用 CMake，跨平台行为难以预测
2. **跨平台 wheel 困难**：manylinux/musllinux/macOS/Windows 各有 wheel 标签与 ABI 约束（如 manylinux 缺 `libpython`、macOS universal2、Windows free-threaded），手工维护 CMake 工程与 wheel 标签的对应关系极易出错
3. **setup.py 时代终结**：PEP 517/518/621/660 等标准确立「构建后端隔离」模型后，`setup.py` 不再是必经之路，但 setuptools 的 CMake 集成仍是临时拼装，缺乏一等公民支持

**一句话定位**：基于 CMake 的 Python 包构建后端，支持 C/C++/Fortran/Cython/SWIG/pybind11/nanobind 等多语言绑定，原生实现 PEP 517/660/621 钩子，无需 setuptools 即可产出 sdist 与 wheel。它是 classic scikit-build（基于 setuptools + distutils 的旧方案）的全面重写。

## 八种构建后端完整对比

| 后端 | 构建系统 | PEP 517 | CMake 集成 | 跨平台 wheel | 可编辑安装 | 学习曲线 | 社区活跃度 |
|---|---|---|---|---|---|---|---|
| **scikit-build-core** | CMake | 原生完整 | 一等公民 | 支持 | redirect/inplace | 中 | 高 |
| classic scikit-build | CMake | 经 setuptools | 一等公民 | 支持 | 不支持 | 中 | 维护模式 |
| setuptools/distutils | 自带 | 原生完整 | 拼装 | 支持 | 支持 | 低 | 高 |
| meson-python | Meson | 原生完整 | 无 | 支持 | 支持 | 中高 | 高 |
| maturin | Cargo（Rust） | 原生完整 | 无 | 支持 | 支持 | 低（Rust 友好） | 高 |
| py-build-cmake | CMake | 经 setuptools | 一等公民 | 部分 | 不支持 | 低 | 中 |
| cmeel | CMake | 原生完整 | 一等公民 | 部分 | 不支持 | 中 | 低 |
| enscons | SCons | 原生完整 | 无 | 支持 | 不支持 | 中高 | 低 |

**关键差异点**：scikit-build-core 是目前唯一同时具备「原生 CMake 集成 + 完整 PEP 517/660/621 支持 + 多语言绑定（C/C++/Fortran/Cython/SWIG/pybind11/nanobind）」三重特性的后端。

**选型建议**：

- 项目已用 CMake 或需多语言绑定（C/C++/Fortran/Cython/SWIG/pybind11/nanobind）→ **scikit-build-core**
- 项目使用 Meson 构建系统 → meson-python
- Rust 扩展或 PyO3 绑定 → maturin
- 纯 Python 项目 → hatchling / flit / setuptools
- 需要轻量 CMake 集成且无 PEP 660 需求 → py-build-cmake

### 与 classic scikit-build 的迁移要点

scikit-build-core 是同一作者团队的全面重写：配置从 `setup.py`/`setup.cfg` 迁移到 `pyproject.toml` 的 `[tool.scikit-build]` 表；CMake 端移除 `PythonExtensions` 模块，改用标准 `find_package(Python ... COMPONENTS Interpreter Development.Module)`；环境变量 `SKBUILD_CONFIGURE_OPTIONS` 改名为 `SKBUILD_CMAKE_ARGS`。

## 生态工具表

scikit-build-core 与以下生态工具协同工作，构成完整的 Python 扩展模块构建与分发工具链：

| 工具 | 类别 | 用途 |
|---|---|---|
| **pybind11** | 语言绑定 | C++ 与 Python 桥接库，scikit-build-core 内置脚手架模板 |
| **nanobind** | 语言绑定 | pybind11 的轻量继任者，推荐配置 `minimum-version="0.4"`、`wheel.py-api="cp312"` |
| **Cython** | 语言绑定 | Python 超集编译器，需配合 `cython-cmake` CMake 包 |
| **SWIG** | 语言绑定 | 多语言绑定生成器 |
| **f2py-cmake** | 语言绑定 | Fortran 扩展（f2py）的 CMake 包装 |
| **hatchling** | 构建后端 | scikit-build-core 提供 `hatch.scikit-build` 插件入口点（实验性） |
| **setuptools-scm** | 版本管理 | 从 git tag 读版本，内置 `metadata.setuptools_scm` provider |
| **hatch-fancy-pypi-readme** | README 渲染 | 复杂 README 渲染，内置 `metadata.fancy_pypi_readme` provider |
| **cibuildwheel** | CI 集成 | 跨平台 wheel 一站式构建（Linux/macOS/Windows） |
| **auditwheel** | wheel 修复 | Linux：将 `linux_*` 标签转为 manylinux/musllinux，使 wheel 可上传 PyPI |
| **delocate** | wheel 修复 | macOS：处理动态库依赖与跨架构（universal2） |
| **delvewheel** | wheel 修复 | Windows：处理 DLL 依赖 |
| **uv** | 包管理 | 推荐通过 `uv init --lib --build-backend=scikit` 与 `uv build` 快速启动 |
| **build** | 构建前端 | PEP 517 构建前端，`python -m build` 是标准构建方式 |
| **validate-pyproject** | 配置校验 | 校验 `pyproject.toml`，scikit-build-core 注册了 `tool_schema.scikit-build` 入口点 |

## 核心术语表

| 术语 | 释义 |
|---|---|
| **ABI3（Stable ABI）** | Python 稳定 ABI（PEP 384），一个 wheel 可支持多 Python 版本。通过 `wheel.py-api = "cp38"` 与 CMake `Development.SABIModule` 启用 |
| **ABI3t（free-threaded Stable ABI）** | 自由线程 Python 3.13+ 的 Stable ABI（PEP 703/793），通过 `wheel.py-api = "cp315.cp315t"` 启用 |
| **auditwheel** | Linux wheel 修复工具，将 `linux_*` 标签转为 manylinux/musllinux |
| **cibuildwheel** | 跨平台 wheel 构建自动化工具，在 CI 中一站式产出多平台 wheel |
| **config-settings** | PEP 517 配置传递机制，扁平点号键（如 `-Cskbuild.logging.level=INFO`），优先级介于环境变量与 TOML 之间 |
| **delocate** | macOS wheel 修复工具，处理动态库依赖与跨架构 |
| **delvewheel** | Windows wheel 修复工具，处理 DLL 依赖 |
| **dynamic metadata** | PEP 621 中标记为 `dynamic` 的字段，由 provider 在构建时填充。内置 `regex`/`template`/`setuptools_scm`/`fancy_pypi_readme` 四个 provider |
| **editable install** | PEP 660 可编辑安装（`pip install -e .`）。支持 `redirect`（默认，含 rebuild-on-import）与 `inplace` 两种模式 |
| **File API** | CMake 文件 API（CMake 3.14+），scikit-build-core 写 stateless query、解析 JSON reply，用于 wheel 文件结构推断与 stale cache 检测 |
| **FindPython** | CMake 内置模块（`find_package(Python ...)`），推荐仅请求 `Interpreter Development.Module`；manylinux 缺 libpython 故禁止请求 `Development.Embed` |
| **manylinux / musllinux** | Linux wheel 兼容性规范（PEP 513/571/599/656），定义 glibc/musl 最低版本与允许的符号集 |
| **minimum-version** | scikit-build-core 向后兼容门，建议设为 `"build-system.requires"` 自动同步 |
| **Ninja** | 高性能构建系统，scikit-build-core 默认 generator（优先级 Ninja > Make > MSVC） |
| **PEP 517** | Python 构建后端标准，定义 `build_wheel`/`build_sdist`/`get_requires_for_build_*`/`prepare_metadata_for_build_*` 等钩子 |
| **PEP 660** | 可编辑安装支持，新增 `build_editable` 等三个钩子 |
| **PEP 621** | 项目元数据标准，定义 `pyproject.toml` 的 `[project]` 表 |
| **PEP 817** | wheel 变体（实验性），通过 `variant`/`variant-label`/`null-variant` 支持，需 `experimental=true` |
| **pyproject.toml** | Python 项目配置文件标准（PEP 518），scikit-build-core 配置位于 `[tool.scikit-build]` 表 |
| **SDist** | 源码分发（Source Distribution），`tar.gz` 格式，由 `build_sdist` 钩子产出 |
| **SOABI** | 共享对象 ABI 标签，标识 Python 扩展模块的二进制兼容性。交叉编译时应使用 `${SKBUILD_SOABI}` 而非 `Python_SOABI` |
| **Wheel** | 二进制分发格式（PEP 427），文件名五段：`name-version-pythontag-abitag-platformtag` |

## 近期版本变更要点

| 版本 | 重要变更 |
|---|---|
| 0.12.x | 新增 `sdist.inclusion-mode`（`default`/`classic`/`manual`）；改进交叉编译；支持 fancy-pypi-readme 25.1；强制规范化 SDist 名 |
| 0.11.x | 新增 `build.requires` 动态注入；新增 `metadata.template` provider；改进 fancy-pypi-readme 版本号支持 |
| 0.10.x | `cmake.minimum-version`/`ninja.minimum-version` 重命名为 `cmake.version`/`ninja.version`（完整 specifier set）；`cmake.verbose`/`cmake.targets` 重命名为 `build.verbose`/`build.targets`；`wheel.packages` 支持 table 形式；新增 `from-sdist`/`system-cmake`/`cmake-wheel`/`failed` override 条件；`minimum-version` 支持 `"build-system.requires"` |

字段迁移机制详见[版本门控与向后兼容](12-version-gating.md)。

## 延伸阅读方向

- **Python 打包生态**：PEP 517/518/621/660 标准、Python Packaging User Guide（packaging.python.org）
- **CMake 深入**：CMake 官方文档、《Professional CMake: A Practical Guide》（Craig Scott）、CMake File API 手册
- **跨平台 wheel 构建**：cibuildwheel 文档、manylinux 规范（PEP 513/571/599）、musllinux 规范（PEP 656）
- **扩展模块开发**：pybind11/nanobind/Cython 文档、Python C API 与 Stable ABI 文档
- **设计原理**：SciPy 2024 论文（Henry Schreiner 等，doi.org/10.25080/FMKR8387）——涵盖 Python 打包历史、scikit-build-core 设计动机与内部实现

## 相关概念

- [scikit-build-core 简介](00-introduction.md)
- [PEP 517 构建后端接口](01-pep517-build-backend.md)
- [Wheel 与 SDist 打包](06-wheel-and-sdist.md)
- [动态元数据](10-dynamic-metadata.md)
- [版本门控与向后兼容](12-version-gating.md)
