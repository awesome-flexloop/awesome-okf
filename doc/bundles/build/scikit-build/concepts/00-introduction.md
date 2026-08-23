---
type: concept
title: scikit-build-core 简介
description: scikit-build-core 是什么、解决什么问题、与同类工具的区别
tags:
  - scikit-build
  - build
  - introduction
generated: true
verified: false
status: stable
stale_after: "2026-12-01"
sources:
  - "external/libs/tools/scikit-build/scikit-build-core/pyproject.toml"
  - "external/libs/tools/scikit-build/scikit-build-core/src/scikit_build_core/__init__.py"
---

# scikit-build-core 简介

## 什么是 scikit-build-core

scikit-build-core 是一个基于 CMake 的 Python 包 PEP 517 构建后端。它替代 setuptools/distutils，负责从源码构建包含 C/C++/Fortran 扩展的 Python wheel 和 sdist 包。

scikit-build-core 不是 setuptools 的插件——它本身是一个完整的、独立的构建后端。它将 CMake 作为一等公民，直接调用 CMake/Ninja 完成编译，再将产物组装为标准 Python wheel。

## 解决的问题

传统 Python C 扩展构建面临以下痛点：

1. **setuptools 的 distutils 层**对 CMake 项目不友好，需要手动处理 include 路径、库路径、编译标志
2. **跨平台差异**：Windows/MSVC、Linux/GCC、macOS/Clang 的编译选项各不相同
3. **已有 CMake 项目**无法无缝接入 Python 打包流程
4. **可编辑安装**（pip install -e）对编译型扩展支持差

scikit-build-core 通过直接集成 CMake 构建系统解决了这些问题：CMake 负责编译配置和跨平台构建，scikit-build-core 负责 PEP 517 接口、配置解析、wheel/sdist 组装。

## 与同类工具对比

| 特性 | scikit-build-core | setuptools | meson-python | cmake-build-extension |
|------|-------------------|------------|--------------|----------------------|
| 构建系统 | CMake | distutils/MSVC | Meson | CMake |
| PEP 517 独立后端 | ✅ | ✅ | ✅ | ❌（setuptools 插件） |
| CMake 原生支持 | ✅（File API） | ❌（手动 subprocess） | ❌ | ✅ |
| Editable 安装 | redirect/inplace 双模式 | 基础 .pth | 基础 .pth | ❌ |
| 动态元数据 | ✅（entry-point 插件） | 有限 | 有限 | ❌ |
| Hatch 插件 | ✅ | ✅ | ❌ | ❌ |
| 配置验证 | ✅（JSON Schema） | ❌ | 有限 | ❌ |

## 项目基本信息

- **许可证**：Apache-2.0
- **作者**：Henry Schreiner
- **Python 版本**：3.9 ~ 3.15（含 Free Threading Python）
- **运行时依赖**：`packaging >=23.2`、`pathspec >=0.12.0`
- **仓库**：<https://github.com/scikit-build/scikit-build-core>

## 何时使用 scikit-build-core

**推荐场景**：

- 项目使用 CMake 作为构建系统（如 pybind11、nanobind 项目）
- 需要跨平台 C/C++/Fortran 编译
- 需要精细控制编译选项、链接库、安装路径
- 已有 CMake C++ 项目需要打包为 Python 包

**不适用场景**：

- 纯 Python 项目（用 hatchling/flit/poetry 更轻量）
- 项目使用 Meson 构建（用 meson-python）
- 项目完全依赖 setuptools 生态（entry-points 注册等可通过 Hatch 插件弥补）

## 延伸阅读

- [PEP 517 构建后端接口](01-pep517-build-backend.md)——了解 scikit-build-core 如何与 pip/build 交互
- [快速开始](02-quickstart.md)——从零创建一个 scikit-build-core 项目
- [配置系统详解](03-settings-system.md)——深入理解三源配置合并
