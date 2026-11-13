---
type: concept
title: mlc-ai/package 简介
description: 这个仓库解决什么问题、四个发行物分别是什么、与 conda/系统包管理的取舍
tags:
  - mlc-ai
  - packaging
  - native-sdk
  - introduction
generated: true
verified: false
status: stable
stale_after: "2027-05-01"
sources:
  - "external/dev/libs/mlc-ai/package/README.md"
  - "external/dev/libs/mlc-ai/package/packages/mlc-llvm-static/README.md"
  - "external/dev/libs/mlc-ai/package/packages/mlc-z3-static/README.md"
  - "external/dev/libs/mlc-ai/package/packages/mlc-doxygen-bin/README.md"
  - "external/dev/libs/mlc-ai/package/packages/mlc-ai/README.md"
---

# mlc-ai/package 简介

## 这是什么

`mlc-ai/package` 不是一个 Python 应用，而是一组**把原生 C/C++ 工具链打包成 Python wheel** 的基建仓库。根 README 把它定义为「a set of packaging utils to build packages in the community」，每个包放在 `packages/<package>/` 下，各自带独立 README 与独立 CI workflow（F-001 ~ F-003）。

目前已发布四个发行物，两类分发目标：

| 包 | 内容 | 分发目标 |
|---|---|---|
| `mlc-llvm-static` | LLVM 静态开发 SDK（静态库 + 头文件 + CMake 导出 + `llvm-config` 兼容前端） | PyPI |
| `mlc-llvm-static-extra-targets` | 同一份 SDK 的全部后端分片 | PyPI |
| `mlc-z3-static` | Z3 静态库 + 头文件 + CMake/pkg-config 元数据 | PyPI |
| `mlc-doxygen-bin` | Doxygen CLI 可执行文件 | PyPI |
| `mlc-ai` / `mlc-llm`（nightly 与稳定版） | TVM / MLC-LLM 的完整运行时 wheel | GitHub Release + `mlc.ai/wheels` 索引 |

前三者（含未在包表中单列的 `extra-targets`）走同一套标准包布局；`mlc-ai` 是例外，它只放构建脚本，上游项目在构建时才克隆（F-010、F-120）。

## 它解决的真实痛点

传统上要在一台机器上构建依赖 LLVM 的 Python 扩展，有三种做法，各有代价：

| 做法 | 代价 |
|---|---|
| 用系统包管理器装 `llvm-dev` | 版本不可控；不同发行版 ABI 不同；Windows 基本没有等价体验 |
| 用 conda 装 `llvmdev` | 引入 conda 生态；与 pip 混用时容易出现两套工具链 |
| 每次从源码编译 LLVM | 小时级耗时；需要额外磁盘与内存；CI 上难以复用 |

这个仓库选择了第四条路：**把"编译好的原生 SDK"做成 pip 可安装的 wheel**。用户执行 `pip install mlc-llvm-static`，得到的是一个已在远端构建机编译完成、经过可重定位处理与静态链接验证的 LLVM SDK。

代价也很明确：wheel 里没有 Python 业务代码，Python 包体只是"定位器"——它告诉构建系统静态库、头文件、CMake 导出在磁盘上的位置（F-099）。所以这类包的**真正 API 是文件布局**，而不是函数签名。

## 四个发行物的定位差异

### 1. `mlc-llvm-static`：LLVM 静态开发 SDK

wheel 内含（见该包 README）：

- PIC 的 LLVM 静态库（原生目标文件，不含 LTO bitcode）；
- LLVM 头文件与生成好的配置头；
- 可重定位的 CMake 导出与 Python 版 `llvm-config` 兼容前端；
- 静态 zlib 1.3.1、zstd 1.5.7 及其头文件与许可；
- Linux 上额外的 ORC 运行时归档。

基础 wheel 只带本机后端（x86_64 主机带 X86，arm64 主机带 AArch64），其余标准后端由 `mlc-llvm-static-extra-targets` 提供。两者来自同一次 All-target 构建，文件所有权互斥（F-087、F-091）。

其使用定位是**构建依赖**：静态链接的下游 wheel 在运行期不需要它。

### 2. `mlc-z3-static`：Z3 静态库

只提供 SMT 求解器的原生开发产物，**不含 Z3 的 Python 绑定**（该包 README 首段明确说明）。原因是定位：它服务的是"要在 C/C++ 项目里链接 Z3"的构建系统。

### 3. `mlc-doxygen-bin`：Doxygen CLI

只构建 `doxygen` 可执行文件，不捆绑 `doxywizard`、`doxyindexer`、`doxysearch.cgi`、libclang、Graphviz、LaTeX、Ghostscript、PlantUML（该包 README「Runtime scope」段）。wheel 装完后 `doxygen --version` 可用。

### 4. `mlc-ai`：TVM / MLC-LLM 的 nightly 与稳定版 wheel

与前三个完全不同：它不是"原生 SDK 打包"，而是"上游项目的整包构建"。构建时才克隆 `mlc-ai/relax`（作为 `tvm/`）与 `mlc-ai/mlc-llm`，按 GPU 变体（CPU / CUDA / ROCm）产出多份 wheel，上传到 GitHub Release 的 `v0.9.dev0` prerelease，并由每日任务把最新版本汇总到 `mlc.ai/wheels` 页面（F-124 ~ F-132）。

## 与同类方案的关键差异

| 维度 | 本仓库 | conda-forge `llvmdev` | 系统包 |
|---|---|---|---|
| 分发通道 | pip / PyPI | conda | apt/dnf/brew |
| 版本钉扎粒度 | 精确到上游 release + 源码归档 SHA-256 | 配方级 | 发行版级 |
| 可重定位 | 显式构造并强制校验 | 依赖 conda 前缀机制 | 否（绑定系统路径） |
| 后端分片 | 基础 + add-on 两 wheel，安装态决定 profile | 单一整包 | 单一整包 |
| Python 版本耦合 | 无（`py3-none-<platform>`） | 无 | 无 |
| 适用场景 | 构建期依赖、CI 可复现 | 数据科学环境 | 系统级开发 |

最后一行值得展开：本仓库所有原生 wheel 都标 `py3-none-<platform>`（F-028、F-028 与 z3/doxygen 的 `wheel.py-api = "py3"`）。这不是笔误——wheel 里没有 CPython ABI 扩展，只有原生开发产物，因此不应随 Python 版本产生矩阵。cibuildwheel 里 `build = "cp311-*"` 只是选择"用哪个 Python 跑构建"（F-037）。

## 读这个包的正确姿势

1. **先分清两层**：外层是 scikit-build-core（PEP 517 后端），内层是一个 `LANGUAGES NONE` 的 CMake 工程，它真正的职责是调用 `prepare_*.py` 并把 staging 目录搬进 wheel（F-031 ~ F-035）。
2. **把 `version.py` 当入口**：所有版本、上游钉扎、SHA-256 都在这里，其余文件都是它的消费者（F-013）。
3. **把验证当规格**：`verify/` 与 `scripts/verify_*.py` 才是"这个 SDK 承诺了什么"的精确定义（F-143 ~ F-156）。
4. **不要用"Python 库"的直觉读它**：这里没有值得关注的 API 设计，值得关注的是文件所有权、profile 派发与链接顺序。

## 什么时候不该用它

- 你只需要 Z3 的 Python API：应该装 `z3-solver`，本仓库的 Z3 包不含绑定。
- 你只需要 Doxygen 的 GUI：本仓库只发 CLI。
- 你的项目愿意用 conda 统一管理工具链：conda 的前缀机制更省事。
- 你需要 LLVM 的共享库、Clang、LLD、MLIR 或其他 LLVM 工具：这些被明确排除在 SDK 之外（该包 README「The SDK contains」段）。

## 延伸阅读

- 仓库目录与发布模型：[仓库布局与发布模型](01-repo-layout-and-release-model.md)
- 版本单一源：[单一版本源与版本戳记](02-single-version-source.md)
- LLVM 分片机制：[SDK 分片：一次构建、两个 wheel](06-split-sdk-partitioning.md)
- 上游依赖审计：[依赖审计要点](../references/02-dependency-audit.md)
