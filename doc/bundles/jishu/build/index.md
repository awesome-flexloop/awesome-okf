---
okf_version: "0.2"
type: group
title: "🔨 构建系统与包管理生态"
description: "构建、打包与开发工具链生态——环境与包管理、跨平台构建生成器、通用开发工具"
---

# 🔨 构建系统与包管理生态

本域存放构建与开发工具链相关的基础设施知识包——从 Conda 环境与包管理、CMake/scikit-build 跨平台构建，到 Copier/Ninja/PyInvoke 等通用开发工具，构成"环境管理 → 构建生成 → 任务自动化"的完整工具链。其中 **scikit-build** 与 **mlc-ai-package** 为本域锚点组：前者讲构建后端的内部机制，后者讲把原生工具链打成可分发 wheel 的完整工程。

## 域内分组导航

| 分组 | 一句话简介 |
|------|-----------|
| [📦 Conda 包管理生态](conda/index.md) | Conda 跨平台包与环境管理器及其工具链生态 |
| [📦 scikit-build 构建后端](scikit-build/index.md) | scikit-build-core——基于 CMake 的 PEP 517 独立构建后端，CMake 作为一等公民（锚点组） |
| [🏗️ CMake 构建系统生态](cmake/index.md) | CMake 跨平台构建系统生成器及其测试/打包工具链 |
| [🔧 通用开发工具](tooling/index.md) | 不绑定特定生态、可独立服务任意项目的通用开发工具 |
| [🧰 MLC AI 原生工具链 wheel 打包](mlc-ai-package/index.md) | mlc-ai/package——把 LLVM/Z3/Doxygen 原生 SDK 打包成可重定位、可验证的 Python wheel；SDK 分片、profile 派发、COFF 裁剪、nightly 流水线与四态验证（锚点组） |

```{toctree}
:hidden:
:maxdepth: 7

conda/index
scikit-build/index
cmake/index
tooling/index
mlc-ai-package/index
```
