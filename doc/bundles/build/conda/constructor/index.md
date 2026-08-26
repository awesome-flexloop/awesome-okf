---
type: index
title: "constructor OKF Wiki"
description: "constructor 源码学习教程 — 从 conda 包创建跨平台自包含安装程序的工具。"
tags: [constructor, conda, 安装程序, 跨平台, 打包]
status: stable
generated: { by: "index_agent/trae-cn", at: "2026-08-21T00:00:00Z" }
---

# constructor OKF Wiki

**constructor** 是一个 Python 工具，用于从 conda 包创建跨平台、自包含的二进制安装程序。它是 Miniconda、Anaconda、Miniforge 等 conda 发行版安装程序的底层构建工具。

- **源码位置**：`external/libs/conda-dev/constructor/`
- **上游仓库**：[conda/constructor](https://github.com/conda/constructor)
- **许可证**：BSD-3-Clause
- **Python 要求**：>=3.10
- **最低 conda 版本**：>=24.1.0

## 📚 知识地图

### 入门篇（先读这三篇）

| 序号 | 文档 | 说明 | 时间 |
|------|------|------|------|
| 00 | [constructor 简介](concepts/00-introduction.md) | constructor 是什么、支持的平台、核心特性 | 5 min |
| 01 | [快速上手](concepts/01-getting-started.md) | 安装、写第一个 construct.yaml、构建安装程序 | 10 min |
| 02 | [架构总览](concepts/02-architecture-overview.md) | 模块分层、核心流程、设计模式全景 | 12 min |

### 核心配置篇

| 序号 | 文档 | 说明 | 时间 |
|------|------|------|------|
| 03 | [construct.yaml 配置规范](concepts/03-construct-yaml-schema.md) | 完整字段参考、Selector、Jinja2、Schema 校验 | 18 min |
| 04 | [安装程序类型](concepts/04-installer-types.md) | sh/pkg/exe/msi/docker 五种类型详解与选型 | 10 min |
| 05 | [CLI 命令行入口](concepts/05-cli-and-entrypoint.md) | 命令行参数、环境变量、main_build 流程 | 10 min |

### 核心流程篇

| 序号 | 文档 | 说明 | 时间 |
|------|------|------|------|
| 06 | [FCP 依赖求解与包下载](concepts/06-fcp-fetch-and-solve.md) | Solver求解、ProgressiveFetchExtract下载、重复检测 | 14 min |
| 07 | [conda_interface 防腐层](concepts/07-conda-interface.md) | conda API 统一封装、repodata 精简、平台兼容 | 10 min |
| 08 | [Preconda Payload 准备](concepts/08-preconda-payload.md) | urls/repodata/conda-meta/condarc/frozen 文件准备 | 10 min |
| 09 | [平台安装器实现](concepts/09-platform-installers.md) | shar/winexe/osxpkg/briefcase 统一接口与平台差异 | 12 min |

### 高级特性篇

| 序号 | 文档 | 说明 | 时间 |
|------|------|------|------|
| 10 | [Docker 构建支持](concepts/10-docker-build.md) | Dockerfile 生成、buildx 镜像构建、容器部署 | 8 min |
| 11 | [多环境与通道配置](concepts/11-multi-env-and-channels.md) | extra_envs、channels_remap、mirrored_channels | 10 min |
| 12 | [构建输出产物](concepts/12-build-outputs.md) | hash/info.json/licenses/lockfile/pkgs_list | 8 min |
| 13 | [签名与安全](concepts/13-signing-and-security.md) | 代码签名、frozen 环境保护、路径安全、UAC | 10 min |
| 14 | [工具集与辅助函数](concepts/14-utils-and-helpers.md) | StandaloneExe、yaml处理、哈希、模板、图片、异常 | 10 min |

## 🚀 实践示例

| 示例 | 说明 | 前置 |
|------|------|------|
| [构建基础 Miniconda 风格安装程序](examples/basic-miniconda.md) | 最小化 Python+conda 安装程序 | 入门篇 |
| [自定义品牌安装程序](examples/custom-installer.md) | 许可证、Logo、安装脚本、NSIS 自定义页面 | basic-miniconda |
| [多环境安装程序](examples/multi-env-installer.md) | 一个安装程序包含多个 conda 环境（分析/DL/文档） | basic-miniconda |
| [Docker 镜像构建](examples/docker-installer.md) | 生成 Dockerfile 和镜像 tar 包 | basic-miniconda |
| [签名安装程序](examples/signed-installer.md) | Windows signtool/AzureSignTool、macOS codesign | custom-installer |

## 📖 信源参考

| 信源 | 模块 |
|------|------|
| [CLI 入口点](references/main-cli.md) | `main.py` — main()/main_build()/get_installer_type() |
| [FCP 求解与下载](references/fcp-solver.md) | `fcp.py` — Solver/ProgressiveFetchExtract/重复检测 |
| [construct.yaml Schema](references/construct-schema.md) | `construct.py` + `_schema.py` — Pydantic模型/Selector/Jinja2 |
| [SH 安装器](references/shar-installer.md) | `shar.py` + `header.sh` — Shell自解压脚本 |
| [Windows EXE 安装器](references/winexe-installer.md) | `winexe.py` + `nsis/` — NSIS GUI 安装程序 |

## 🔑 核心架构洞察

constructor 的设计体现了以下架构原则：

1. **策略模式**：每个平台安装器实现统一的 `create(info, verbose)` 接口，通过延迟导入分发
2. **防腐层（ACL）**：`conda_interface.py` 隔离 constructor 与 conda 内部 API 的耦合
3. **配置驱动**：所有行为由 construct.yaml 驱动，JSON Schema + Pydantic 双重校验
4. **两阶段管线**：FCP 将"求解"与"下载"分离，支持 `--dry-run` 预验证
5. **离线优先**：Payload 内置精简 repodata 缓存，安装时完全离线
6. **模板方法**：Jinja2 模板分离 Python 逻辑与脚本内容（header.sh/main.nsi.tmpl）

```{toctree}
:maxdepth: 7

concepts/00-introduction
concepts/01-getting-started
concepts/02-architecture-overview
concepts/03-construct-yaml-schema
concepts/04-installer-types
concepts/05-cli-and-entrypoint
concepts/06-fcp-fetch-and-solve
concepts/07-conda-interface
concepts/08-preconda-payload
concepts/09-platform-installers
concepts/10-docker-build
concepts/11-multi-env-and-channels
concepts/12-build-outputs
concepts/13-signing-and-security
concepts/14-utils-and-helpers
examples/basic-miniconda
examples/custom-installer
examples/docker-installer
examples/multi-env-installer
examples/signed-installer
references/construct-schema
references/fcp-solver
references/main-cli
references/shar-installer
references/winexe-installer
log
```
