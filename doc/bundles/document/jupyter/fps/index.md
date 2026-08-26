---
type: OKF
title: FPS 教程
description: FPS (Fast Pluggable System) 是一个用于创建模块化、可配置、可插拔、并发应用的框架。本教程系统讲解FPS的核心概念、API和实践用法。
tags: [fps, python, async, modular, plugin, jupyter]
version: 0.6.7
source: https://github.com/jupyter-server/fps
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T14:55:00+08:00" }
status: stable
stale_after: 2027-08-22
---

# FPS (Fast Pluggable System) 教程

FPS 是一个用于创建模块化、可配置、可插拔、并发应用的Python框架。它通过基于树的模块组织、三阶段生命周期管理和类型驱动的服务共享，让开发者能够构建高度可组合的异步应用。

FPS 是 [Jupyverse](https://github.com/jupyter-server/jupyverse)（Jupyter的现代化服务器实现）的底层框架。

## 📚 快速导航

### [概念文档](concepts/index.md)
- [00-简介](concepts/00-introduction.md) — FPS是什么、核心特性、技术栈
- [01-安装与快速开始](concepts/01-getting-started.md) — 安装方法、CLI命令、第一个应用
- [02-模块系统](concepts/02-module-system.md) — Module类、模块树、服务发布与获取
- [03-上下文与共享值](concepts/03-context-sharing.md) — Context/SharedValue/Value、借用机制、teardown
- [04-生命周期阶段](concepts/04-lifecycle-phases.md) — prepare/start/stop三阶段、done()、超时控制
- [05-配置系统](concepts/05-configuration-system.md) — JSON配置、CLI参数、Pydantic校验、动态导入
- [06-信号系统](concepts/06-signal-system.md) — Signal回调/迭代器模式、事件通知
- [07-Web模块](concepts/07-web-modules.md) — FastAPIModule、ServerModule、模块化路由
- [08-插件架构](concepts/08-plugin-architecture.md) — Entry-points发现、插件解耦、Jupyverse实践

### [实践示例](examples/index.md)
- [01-第一个FPS应用](examples/01-first-app.md) — 最简应用与生命周期
- [02-模块间共享对象](examples/02-sharing-objects.md) — put/get依赖注入
- [03-可插拔Web服务器](examples/03-web-server.md) — FastAPI模块化Web应用
- [04-声明式JSON配置](examples/04-declarative-config.md) — 零代码组装应用
- [05-独立使用Context](examples/05-standalone-context.md) — 资源生命周期管理
- [06-信号使用](examples/06-signals-usage.md) — 事件通知的两种模式

### [信源参考](references/index.md)
- [模块系统API](references/module-source.md) — Module类完整API
- [上下文系统API](references/context-source.md) — Context/SharedValue/Value API
- [配置系统API](references/config-source.md) — Configuration/import_from_string API
- [信号系统API](references/signal-source.md) — Signal类API
- [CLI命令](references/cli-source.md) — CLI参数与命令
- [Web模块API](references/web-source.md) — FastAPIModule/ServerModule API
- [事实清单](facts.md) — 从源码采集的零推测事实
- [架构洞察](insights.md) — 核心洞察四元组与知识地图

## 🚀 快速开始

```bash
pip install fps
```

创建最简单的应用：

```python
from fps import Module

class Hello(Module):
    async def start(self):
        print("Hello, FPS!")
```

运行：
```bash
fps hello:Hello
```

## 🎯 核心特性

| 特性 | 说明 |
|------|------|
| 🌳 模块树组织 | 应用由Module树组成，支持任意深度嵌套 |
| 🔄 三阶段生命周期 | prepare→start→stop，阶段间全屏障同步 |
| 📦 类型驱动共享 | put/get基于Python类型的异步发布-订阅依赖注入 |
| 🔒 借用资源管理 | SharedValue/Value类似Rust的借用机制，max_borrowers并发控制 |
| ⚙️ 声明式配置 | JSON配置+CLI参数+Pydantic校验，支持动态导入 |
| 📡 事件信号 | Signal支持回调和异步迭代器两种监听模式 |
| 🔌 插件架构 | 基于entry-points的自动发现，零粘合代码组装 |
| 🌐 Web集成 | 内置FastAPI+anycorn Web模块 |
| ⚡ 并发运行 | 基于anyio异步框架，兼容asyncio/trio |

## 📖 推荐学习路径

1. **概念入门**：阅读 [00-简介](concepts/00-introduction.md) 和 [01-安装与快速开始](concepts/01-getting-started.md)
2. **动手实践**：跟着 [01-第一个FPS应用](examples/01-first-app.md) 写第一个程序
3. **理解核心**：学习 [02-模块系统](concepts/02-module-system.md)、[03-上下文共享](concepts/03-context-sharing.md)、[04-生命周期](concepts/04-lifecycle-phases.md)
4. **掌握配置**：阅读 [05-配置系统](concepts/05-configuration-system.md) 和 [04-声明式配置](examples/04-declarative-config.md)
5. **高级主题**：学习 [06-信号](concepts/06-signal-system.md)、[07-Web模块](concepts/07-web-modules.md)、[08-插件架构](concepts/08-plugin-architecture.md)

## 📊 架构概览

```
┌─────────────────────────────────────────────────┐
│                   Application                    │
│  ┌───────────────────────────────────────────┐  │
│  │              Root Module                   │  │
│  │  ┌──────────┐ ┌──────────┐ ┌───────────┐  │  │
│  │  │ Module A │ │ Module B │ │ Module C  │  │  │
│  │  │  (child) │ │  (child) │ │  (child)  │  │  │
│  │  └──────────┘ └──────────┘ └───────────┘  │  │
│  └───────────────────────────────────────────┘  │
│                                                  │
│  Lifecycle: prepare ──→ start ──→ stop          │
│                                                  │
│  Sharing:  put(Type, value)  ←→  get(Type)      │
│                                                  │
│  Events:   signal.emit(value) ←→ signal.connect │
│                                                  │
│  Config:   JSON config file + CLI --set          │
└─────────────────────────────────────────────────┘
```

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
facts
insights
log
```
