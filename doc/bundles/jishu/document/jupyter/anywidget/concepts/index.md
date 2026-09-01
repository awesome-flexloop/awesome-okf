---
type: concept_index
title: "anywidget 核心概念索引"
description: "anywidget 核心概念文档导航"
generated: true
verified: grep
status: stable
stale_after: 2027-08-23
---

# anywidget 概念文档

| 编号 | 概念 | 前置依赖 | 一句话简介 |
|------|------|---------|-----------|
| 00 | [整体架构与ESM协议](00-overall-architecture.md) | — | anywidget设计理念、ESM零构建、双API层架构 |
| 01 | [Widget基类与生命周期](01-widget-lifecycle.md) | 00 | AnyWidget类、ESM/CSS定义、JS生命周期、AbortSignal清理 |
| 02 | [Trait同步与双向绑定](02-trait-sync.md) | 01 | WidgetTrait、双观察者系统、状态自动适配、二进制数据 |
| 03 | [前端通信协议](03-frontend-communication.md) | 02 | Comm通道、消息类型、ESM导出格式、Custom Messages |
| 04 | [HMR热更新](04-hmr-dev.md) | 01 | 文件监视、SolidJS响应式更新、Vite插件集成 |
| 05 | [多框架桥接](05-framework-bridges.md) | 03 | React/Svelte/Vue集成、TypeScript类型、model proxy |

```{toctree}
:hidden:
:maxdepth: 7

00-overall-architecture
01-widget-lifecycle
02-trait-sync
03-frontend-communication
04-hmr-dev
05-framework-bridges
```
