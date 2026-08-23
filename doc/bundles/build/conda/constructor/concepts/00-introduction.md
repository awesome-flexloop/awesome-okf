---
type: concept
title: "constructor 简介"
description: "constructor 是一个用于从 conda 包创建跨平台自包含安装程序的工具，支持 Linux(.sh)、macOS(.pkg/.sh)、Windows(.exe/.msi) 和 Docker 镜像。"
tags: [介绍, 概述, 安装程序, conda]
status: stable
stale_after: 2027-12-31
level: beginner
prerequisites: []
reading_time: 5
generated: { by: "concept_agent/trae-cn", at: "2026-08-21T00:00:00Z" }
sources:
  - id: constructor-pyproject
    resource: "pyproject.toml"
  - id: constructor-main
    resource: "constructor/main.py"
---

# constructor 简介

**constructor** 是一个 Python 工具，用于从 conda 包创建**跨平台、自包含的二进制安装程序**。它是 Miniconda、Anaconda 和 Miniforge 等 conda 发行版安装程序的底层构建工具。

## 什么是 constructor？

简单来说，constructor 将一组 conda 包（从 conda 通道求解依赖、下载）打包成一个用户可以双击或命令行运行的安装程序文件。这个安装程序内置了 conda-standalone 或 micromamba 二进制，在目标机器上执行安装时**不需要预装 conda，也不需要网络连接**。

```
┌─────────────────────┐      constructor        ┌──────────────────────┐
│ construct.yaml      │ ──────────────────────▶ │  MyInstaller-1.0.exe │
│ (配置文件：包、通道、│     (构建机器上运行)     │  MyInstaller-1.0.sh  │
│  安装选项等)         │                          │  MyInstaller-1.0.pkg │
└─────────────────────┘                          └──────────────────────┘
                                                       │
                                                       ▼ 用户双击运行
                                              ┌──────────────────────┐
                                              │ 目标机器上自动安装    │
                                              │ conda环境 + 所有包   │
                                              └──────────────────────┘
```

## 支持的安装程序类型

constructor 为不同操作系统生成不同格式的安装程序：

| 操作系统 | 默认格式 | 可选格式 | 安装程序类型标识符 |
|---------|---------|---------|-----------------|
| Linux   | `.sh`（Shell 自解压脚本） | Dockerfile + Docker 镜像 | `sh`, `docker` |
| macOS   | `.sh` + `.pkg` | — | `sh`, `pkg` |
| Windows | `.exe`（NSIS GUI） | `.msi`（WiX/Briefcase，实验性） | `exe`, `msi` |
| 跨平台 | 可通过 `--platform` 交叉构建 | — | 见 [04-安装程序类型](./04-installer-types.md) |

## 核心特性

- **零依赖安装**：生成的安装程序完全自包含，目标机器无需预装 Python 或 conda。
- **多环境支持**：一个安装程序可同时创建 base 环境和多个额外 conda 环境（`extra_envs`）。
- **通道重映射**：构建时使用内部通道（如内网镜像），安装后用户看到的是公共通道 URL（`channels_remap`）。
- **离线安装**：所有包在构建时下载并打包到安装程序中，安装时无需网络。
- **Frozen 环境保护**：基于 CEP-22 规范，标记 `freeze_base=True` 的环境在安装后不允许用户手动安装/更新/删除包。
- **可定制安装向导**：支持自定义许可证文件、欢迎图片、安装前后脚本、NSIS 自定义页面等。
- **代码签名**：Windows（signtool/AzureSignTool）和 macOS（codesign）签名支持。
- **多构建产物**：可同时输出哈希校验、info.json、license 文件、lockfile、pkgs_list 等附属产物。

## 技术栈

| 依赖 | 最低版本 | 用途 |
|------|---------|------|
| Python | >=3.10 | 运行时环境 |
| conda | >=24.1.0 | 依赖求解与包下载（通过 conda-standalone） |
| ruamel.yaml | >=0.19.0 | YAML 解析与序列化 |
| Jinja2 | >=3.1.0 | construct.yaml 和安装脚本模板渲染 |
| jsonschema | >=4.23 | construct.yaml 的 JSON Schema 校验 |
| Pillow | >=9.5 (Windows/macOS) | 安装程序图片处理 |
| platformdirs | >=4.3.2 | 跨平台配置目录定位 |
| briefcase (Windows MSI) | >=0.3.20 | Windows MSI 安装程序构建（可选） |
| setuptools + setuptools_scm | 构建时 | Python 包构建与版本管理 |

## 适用场景

1. **企业内部分发**：创建包含特定 Python 版本和公司内部包的定制 Python 环境安装程序。
2. **教育/培训**：为学员提供一键安装的完整数据分析/机器学习环境。
3. **软件发布**：将基于 conda 的应用打包为原生安装程序，提供给非技术用户。
4. **CI/CD 离线部署**：在无网络环境的服务器上部署预配置的 conda 环境。
5. **conda 发行版制作**：Miniconda、Miniforge、Anaconda 等发行版均使用 constructor 构建。

## 下一步

- [01-快速上手](./01-getting-started.md)：安装 constructor，编写第一个 construct.yaml，构建安装程序。
- [02-架构总览](./02-architecture-overview.md)：了解 constructor 的模块分层和核心构建流程。
