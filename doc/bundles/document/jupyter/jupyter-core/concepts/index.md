---
okf_version: "0.2"
type: concepts
title: "核心概念"
description: "jupyter_core v5.9.1 核心概念文档索引，涵盖从入门到进阶的完整知识体系。"
tags: [jupyter, core, concepts, index]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:30:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T12:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: version-py
    resource: "../../../../../external/libs/jupyter/jupyter_core/jupyter_core/version.py"
    title: "jupyter_core/version.py"
---

# 核心概念

本章节系统讲解 jupyter_core v5.9.1 的核心概念，分为入门、核心、进阶三个层次。

## 📘 入门

| 文档 | 简介 |
|------|------|
| [00 - jupyter_core 简介](00-introduction.md) | 了解 jupyter_core 在 Jupyter 生态中的定位、四大核心能力、项目信息与 CLI 命令概览。 |
| [01 - 5分钟快速上手](01-getting-started.md) | 安装 jupyter_core，掌握路径 API、命令行用法、环境诊断与配置迁移的基本操作。 |

## 📗 核心

| 文档 | 简介 |
|------|------|
| [02 - 架构总览](02-architecture-overview.md) | 理解 jupyter_core 的四层架构（工具→路径→命令→应用）、外围模块、外部依赖与设计哲学。 |
| [03 - 路径系统详解](03-path-system.md) | 深入理解三类核心目录、跨平台默认位置、四级搜索优先级、secure_write 原子写入与 is_hidden 检测。 |
| [04 - 命令行调度器](04-command-dispatcher.md) | 掌握 jupyter CLI 的 PATH 子命令发现机制、JupyterParser 参数解析、跨平台 _execvp 与 argcomplete 补全。 |
| [05 - 应用基类 JupyterApp](05-application-base.md) | 学习 JupyterApp 的继承体系、traitlets 配置管理、初始化流程、子命令分发与 JupyterAsyncApp 异步支持。 |

## 📙 进阶

| 文档 | 简介 |
|------|------|
| [06 - 异步支持机制](06-async-support.md) | 深入理解 run_sync 装饰器、_TaskRunner 后台线程、ensure_event_loop 与 ensure_async 的 sync/async 桥接。 |
| [07 - 配置迁移与环境诊断](07-migration-and-troubleshoot.md) | 掌握 IPython 3.x→Jupyter 4.x 配置迁移机制，以及基于标准库的极简环境诊断工具。 |
| [08 - 环境变量参考](08-environment-variables.md) | jupyter_core 支持的所有环境变量的完整参考：类型、作用、默认值与使用示例。 |

---

**导航：**
- [示例代码](../examples/index.md) — 可运行的代码示例
- [源码信源](../references/index.md) — 源码信源文档
- [返回首页](../index.md)

```{toctree}
:hidden:

00-introduction
01-getting-started
02-architecture-overview
03-path-system
04-command-dispatcher
05-application-base
06-async-support
07-migration-and-troubleshoot
08-environment-variables
```
