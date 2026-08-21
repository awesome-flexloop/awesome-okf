---
okf_version: "0.2"
type: "concept"
title: "conda 简介"
sources:
  - "conda/__init__.py"
  - "pyproject.toml"
  - "README.md"
---

# conda 简介

## 什么是 conda

conda 是一个**跨平台、语言无关的二进制包管理器和环境管理器** [F-001]。它完全使用 Python 编写，采用 BSD-3-Clause 开源许可证发布 [F-001][F-011]，当前版本为 **26.7.1**（遵循 CalVer 版本命名规范 YY.MM.MICRO）。

conda 的核心定位可以用三个关键词概括：

1. **包管理器（Package Manager）**：conda 能够安装、更新、移除预编译的二进制包，支持 Python、R、C/C++、Fortran 等多种语言生态中的软件包。与从源码编译不同，conda 分发的是预编译二进制文件，安装速度快且无需编译工具链。

2. **环境管理器（Environment Manager）**：conda 将环境提升为"一等公民"，允许用户创建完全隔离的独立环境，每个环境拥有独立的包集合和 Python 版本。环境之间通过硬链接（hard link）共享包文件，空间高效，创建秒级完成。

3. **跨平台运行（Cross-platform）**：conda 原生支持 Linux（x86_64/aarch64/ppc64le）、macOS（x86_64/arm64）、Windows 等平台，同一套命令在不同操作系统上行为一致 [F-025]。默认环境名为 `base`（即 root 环境）[F-029]，conda 自身安装在该环境中。

## 开源许可证与项目信息

conda 由 Anaconda, Inc. 主导开发，采用 **BSD-3-Clause** 许可证 [F-001]，项目托管于 GitHub（https://github.com/conda/conda）。核心元数据定义如下：

```python
# conda/__init__.py
__author__ = "Anaconda, Inc."
__license__ = "BSD-3-Clause"
__url__ = "https://github.com/conda/conda"
```

构建系统使用 hatchling + hatch-vcs，版本号通过 VCS（Git）自动生成 [F-011][F-014]，要求 Python ≥ 3.10，支持 Python 3.10–3.14 和 PyPy [F-011]。

## 核心能力

### 环境隔离

conda 的环境隔离是其最核心的能力。每个环境是一个独立的目录前缀（prefix），拥有独立的 `conda-meta/` 目录记录已安装包信息 [F-028][F-055]。环境之间互不干扰，可以在不同环境中安装同一包的不同版本。

### 包安装与链接

conda 安装包时使用三种链接类型：hardlink（硬链接，默认）、softlink（软链接）、copy（复制）[F-052]。系统会按 hardlink→softlink→copy 的顺序自动选择最优链接方式，在保证隔离性的同时最大化磁盘空间利用率。

### 依赖求解（SAT Solver）

conda 内置经典 SAT 求解器，基于布尔可满足性问题算法解决依赖冲突。默认使用 `pycosat` 作为 SAT 后端 [F-013][F-058]，同时支持 PyCryptoSat 和 PySat 作为备选后端 [F-058]。求解器通过 `Clauses` 类管理子句，使用 Tseitin 转换避免逻辑表达式的指数膨胀 [F-060][F-061]。

### 跨平台支持

conda 通过平台映射机制统一不同系统的平台标识 [F-025]：

| 系统 | conda 平台标识 |
|------|---------------|
| Linux | `linux-64`, `linux-aarch64`, `linux-ppc64le` |
| macOS | `osx-64`, `osx-arm64` |
| Windows | `win-64` |

`KNOWN_SUBDIRS` 常量枚举了所有已知平台子目录 [F-029]，`Channel` 模型将 URL 分解为 scheme、auth、location、token、channel、subchannel、platform、package_filename 八个组件 [F-030][F-032]。

### 插件扩展

conda 基于 pluggy 框架（pytest 的同款插件框架）构建了完整的插件体系，支持19种扩展钩子类型，包括自定义求解器、子命令、虚拟包、报告后端、认证处理器等 [F-068][F-069][F-070]。

## conda vs pip vs mamba

| 特性 | conda | pip | mamba |
|------|-------|-----|-------|
| **定位** | 通用二进制包管理器 + 环境管理器 | Python 包安装器 | conda 的 C++ 高性能重实现 |
| **包格式** | conda 包（.conda/.tar.bz2，预编译二进制） | wheel / sdist（源码或二进制） | 兼容 conda 包格式 |
| **环境管理** | 原生一等公民支持 | 通过 venv/virtualenv（外部工具） | 与 conda 相同 |
| **依赖求解** | 经典 SAT 求解器（pycosat） | Resolver（较简单，不处理非Python依赖） | libsolv（C++实现，速度更快） |
| **非Python依赖** | ✅ 原生支持（C库、编译器、CUDA等） | ❌ 不支持 | ✅ 兼容 conda |
| **跨语言** | ✅ Python/R/C++/Julia等 | ❌ 仅Python | ✅ 同 conda |
| **跨平台** | ✅ Linux/macOS/Windows | ✅ 但需编译C扩展 | ✅ 同 conda |
| **二进制兼容性** | ✅ 预编译保证ABI兼容 | ⚠️ wheel可能有兼容问题 | ✅ 同 conda |
| **安装来源** | conda channels（defaults/conda-forge等） | PyPI | 同 conda channels |

**关键区别说明**：

- **pip** 专注于 Python 生态，安装 wheel 或从源码编译（sdist），不管理非 Python 依赖（如 CUDA、MKL 等 C 库）。pip 和 conda 可以在同一环境中共存，conda 环境中可以使用 pip 安装 PyPI 上的包。
- **mamba** 是 conda 的 drop-in 替代实现，使用 C++ 的 libsolv 库进行依赖求解，在大型环境中求解速度比 conda 经典求解器快数倍至数十倍。mamba 通过 conda 插件机制（`conda_solvers` 钩子）集成，可以通过 `conda install conda-libmamba-solver` 启用 [F-070]。
- **conda** 的独特优势在于"全栈管理"——不仅管理 Python 包，还管理 Python 解释器本身、C/C++ 编译器、CUDA 工具包、底层数学库等，这使得它成为数据科学和机器学习领域的事实标准。

## 相关概念

- [5分钟快速上手](01-getting-started.md)
- [七层架构总览](02-architecture-overview.md)
