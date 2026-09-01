---
okf_version: "0.2"
type: index
title: "核心概念"
description: "jupyterlab_server 核心概念文档索引"
---

# 核心概念

本目录按由浅入深的顺序讲解 jupyterlab_server 的核心概念和设计原理。

## 文档清单

| 序号 | 文档 | 主题 | 前置阅读 |
|------|------|------|---------|
| 00 | [简介](00-introduction.md) | 项目定位、六大子系统、模块速览 | 无 |
| 01 | [快速上手](01-getting-started.md) | 安装、启动、配置、API体验 | 00 |
| 02 | [架构总览](02-architecture-overview.md) | 四层架构、模块依赖、请求流程、设计模式 | 01 |
| 03 | [应用与配置系统](03-app-and-config.md) | LabServerApp、LabConfig Mixin、traitlets、page_config | 02 |
| 04 | [Handler与路由系统](04-handlers-and-routing.md) | add_handlers()、URL模式、LabHandler、NotFoundHandler | 03 |
| 05 | [设置系统](05-settings-system.md) | JSON Schema验证、三层覆盖、overrides、REST API | 04 |
| 06 | [工作区管理](06-workspaces.md) | slugify、WorkspacesManager、CRUD、工作区CLI | 04 |
| 07 | [主题、扩展列表与许可证](07-themes-listings-licenses.md) | CSS URL重写、黑白名单、许可证报告 | 04 |
| 08 | [国际化系统](08-internationalization.md) | TranslationBundle、translator、语言包、Schema翻译 | 04 |
| 09 | [进程管理与CLI工具](09-process-and-cli.md) | Process、WatchHelper、ProcessApp、测试fixtures | 03 |

## 阅读路径

### 入门路径（新用户）
00 → 01 → 02 → 03 → 04

### 子系统深入（开发者）
- 设置系统：05 → [settings-source.md](../references/settings-source.md)
- 工作区：06 → [workspaces-source.md](../references/workspaces-source.md)
- 国际化：08 → [i18n-source.md](../references/i18n-source.md)
- 扩展开发：03 → 04 → 05 → 08

### 二次开发（基于LabServerApp构建）
00 → 02 → 03 → [app-source.md](../references/app-source.md) → [config-source.md](../references/config-source.md)

```{toctree}
:hidden:
:maxdepth: 7

00-introduction
01-getting-started
02-architecture-overview
03-app-and-config
04-handlers-and-routing
05-settings-system
06-workspaces
07-themes-listings-licenses
08-internationalization
09-process-and-cli
```
