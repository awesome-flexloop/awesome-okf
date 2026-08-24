# 概念文档索引

本目录包含 Try Jupyter 项目的10个核心概念文档，按学习路径排列。

## 入门篇

| 编号 | 文档 | 内容 |
|------|------|------|
| 00 | [项目概述](00-introduction.md) | Try Jupyter是什么、核心特性、技术栈、仓库结构 |
| 01 | [快速开始](01-getting-started.md) | 本地环境搭建、pixi安装依赖、构建站点、本地预览 |

## 架构篇

| 编号 | 文档 | 内容 |
|------|------|------|
| 02 | [架构总览](02-architecture-overview.md) | 双内核体系（Pyodide+Xeus）、静态站点生成、配置驱动架构、禁用扩展策略 |
| 03 | [配置系统](03-configuration-system.md) | jupyter-lite.json、jupyter_lite_config.json、cockle-config-in.json、repl配置详解 |
| 04 | [内核生态](04-kernel-ecosystem.md) | Pyodide内核、Xeus-Python/C++/R/SQLite内核、environment-*.yml环境定义、内核过滤机制 |

## 构建篇

| 编号 | 文档 | 内容 |
|------|------|------|
| 05 | [构建管线](05-build-pipeline.md) | Pixi任务编排、jupyter lite build、后处理脚本（内核过滤+Plausible注入）、CI构建流程 |
| 06 | [Notebook内容与数据](06-notebooks-and-content.md) | 7个演示notebook详解、8个数据文件（GeoJSON/FASTA/CSV/音频/图片）、文件查看器扩展 |

## 质量保障与部署篇

| 编号 | 文档 | 内容 |
|------|------|------|
| 07 | [UI测试框架](07-ui-testing.md) | Playwright E2E测试、fixtures设计、notebook参数化、cell执行监控、stderr错误检测 |
| 08 | [部署](08-deployment.md) | GitHub Actions三阶段流水线、GitHub Pages正式部署、ReadTheDocs PR预览、权限配置 |
| 09 | [终端支持](09-terminal-support.md) | Cockle WASM终端、预安装包（git/vim/nano等）、命令别名、Git环境变量、终端限制 |

```{toctree}
:hidden:

00-introduction
01-getting-started
02-architecture-overview
03-configuration-system
04-kernel-ecosystem
05-build-pipeline
06-notebooks-and-content
07-ui-testing
08-deployment
09-terminal-support
```
