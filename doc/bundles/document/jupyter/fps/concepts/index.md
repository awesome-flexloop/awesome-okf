# FPS 概念文档索引

本目录包含 FPS 框架的核心概念文档，建议按顺序阅读。

## 入门

| 文档 | 说明 |
|------|------|
| [00-introduction.md](00-introduction.md) | FPS 框架简介、核心特性、技术栈与定位 |
| [01-getting-started.md](01-getting-started.md) | 安装方法、CLI命令用法、第一个FPS应用 |

## 核心概念

| 文档 | 说明 |
|------|------|
| [02-module-system.md](02-module-system.md) | Module类结构、模块树组织、服务发布与获取 |
| [03-context-sharing.md](03-context-sharing.md) | Context/SharedValue/Value三层共享模型、借用机制、teardown回调 |
| [04-lifecycle-phases.md](04-lifecycle-phases.md) | prepare/start/stop三阶段生命周期、done()用法、超时与后台任务 |
| [05-configuration-system.md](05-configuration-system.md) | JSON配置格式、CLI参数覆盖、Pydantic校验、动态导入 |

## 高级主题

| 文档 | 说明 |
|------|------|
| [06-signal-system.md](06-signal-system.md) | Signal异步发布-订阅机制、回调与迭代器两种模式 |
| [07-web-modules.md](07-web-modules.md) | FastAPIModule和ServerModule、模块化路由注册 |
| [08-plugin-architecture.md](08-plugin-architecture.md) | Entry-points插件发现、插件间解耦、Jupyverse实践 |

```{toctree}
:maxdepth: 7

00-introduction
01-getting-started
02-module-system
03-context-sharing
04-lifecycle-phases
05-configuration-system
06-signal-system
07-web-modules
08-plugin-architecture
```
