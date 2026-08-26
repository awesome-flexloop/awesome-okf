---
okf_version: "0.2"
type: bundle
title: "jupyter_core"
description: "Jupyter 生态的核心基础库：跨平台路径管理、命令行调度、应用基类与工具函数。本知识包从源码出发，系统讲解 jupyter_core v5.9.1 的架构、API和实战用法。"
---

# jupyter_core

> Jupyter 生态的核心基础库：跨平台路径管理、命令行调度、应用基类与工具函数。

`jupyter_core` 是所有 Jupyter 项目（Notebook、JupyterLab、Jupyter Server、IPython 等）共同依赖的底层基础包。它提供跨平台路径管理、`jupyter` 命令行调度器、应用基类 `JupyterApp`、以及异步桥接等核心能力，是理解和扩展 Jupyter 生态的基石。

## 快速导航

### 📘 核心概念（10 篇）

**入门**
- [简介](concepts/00-introduction.md) — jupyter_core 在 Jupyter 生态中的定位、四大核心能力、项目信息与 CLI 概览
- [5分钟快速上手](concepts/01-getting-started.md) — 安装、路径 API、命令行用法、环境诊断与配置迁移

**核心**
- [架构总览](concepts/02-architecture-overview.md) — 四层架构（工具→路径→命令→应用）、外围模块、外部依赖与设计哲学
- [路径系统详解](concepts/03-path-system.md) — 三类核心目录、跨平台默认位置、四级搜索优先级、secure_write 原子写入、is_hidden 检测
- [命令行调度器](concepts/04-command-dispatcher.md) — jupyter CLI 的 PATH 子命令发现、JupyterParser、跨平台 _execvp、argcomplete 补全
- [应用基类 JupyterApp](concepts/05-application-base.md) — 继承体系、traitlets 配置、初始化流程、子命令分发、JupyterAsyncApp 异步支持

**进阶**
- [异步支持机制](concepts/06-async-support.md) — run_sync 装饰器、_TaskRunner 后台线程、ensure_event_loop、ensure_async 的 sync/async 桥接
- [配置迁移与环境诊断](concepts/07-migration-and-troubleshoot.md) — IPython 3.x→Jupyter 4.x 配置迁移、基于标准库的极简环境诊断工具
- [环境变量参考](concepts/08-environment-variables.md) — 所有环境变量的完整参考：类型、作用、默认值与使用示例
- [概念文档索引](concepts/index.md) — 概念文档总目录

### 💻 示例代码（3 个）

- [基础使用示例](examples/01-basic-usage.md) — 查询路径、安全写入文件、环境诊断、发现子命令
- [自定义 JupyterApp 应用](examples/02-custom-app.md) — 创建完整的自定义 Jupyter 应用，包含配置项、异步方法、命令行选项
- [路径定制与环境变量](examples/03-path-customization.md) — 目录重定向、附加搜索路径、虚拟环境隔离、多环境配置
- [示例文档索引](examples/index.md) — 示例总目录

### 📄 源码信源（7 个文件）

- [paths.py](references/paths-source.md) — 跨平台路径管理
- [command.py](references/command-source.md) — 命令行调度器
- [application.py](references/application-source.md) — JupyterApp 应用基类
- [utils/\_\_init\_\_.py](references/utils-source.md) — 工具函数与异步桥接
- [migrate.py](references/migrate-source.md) — IPython 配置迁移
- [troubleshoot.py](references/troubleshoot-source.md) — 环境诊断
- [源码信源索引](references/index.md) — 信源文档总目录（含 version.py 等模块信息）

## 版本信息

| 属性 | 值 |
|------|-----|
| 版本 | **v5.9.1** |
| Python 版本要求 | ≥ 3.10 |
| 构建系统 | Hatchling ≥ 1.4 |
| 必需依赖 | platformdirs ≥ 2.5, traitlets ≥ 5.3 |
| 可选依赖 | argcomplete（Tab 补全）、pywin32（Windows 权限） |
| 许可证 | BSD-3-Clause |
| CLI 命令 | `jupyter`, `jupyter-migrate`, `jupyter-troubleshoot` |
| 源码路径 | `external/libs/jupyter/jupyter_core/` |

---

**推荐阅读顺序：** [简介](concepts/00-introduction.md) → [快速上手](concepts/01-getting-started.md) → [架构总览](concepts/02-architecture-overview.md) → [路径系统](concepts/03-path-system.md) → [命令行调度器](concepts/04-command-dispatcher.md) → [应用基类](concepts/05-application-base.md)

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
facts
insights
log
```
