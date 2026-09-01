---
type: bundle
title: anywidget Jupyter Widget
description: "anywidget 系统化中文源码教程，覆盖 Python 核心包（AnyWidget/MimeBundleDescriptor/ESM协议/HMR）、JS运行时（Runtime/SolidJS响应式/Binding）、TypeScript类型系统与Vite插件的完整知识体系。"
okf_version: "0.2"
---


# anywidget Jupyter Widget 知识库

本知识包是 [anywidget](https://anywidget.dev)（MIT 许可证）的系统化中文源码教程，基于 anywidget 源码（`external/libs/ai/Anything/anywidget/` 目录）深度阅读生成，覆盖从 Python 核心包（AnyWidget 基类、WidgetTrait 描述符、MimeBundleDescriptor、ESM 协议、HMR 热更新）到 JS 运行时（Runtime、AnyModel、Binding、SolidJS 响应式系统）、TypeScript 类型系统以及 Vite 插件的完整知识体系。所有内容均溯源至 anywidget 源码核心模块，遵循 [OKF v0.2 规范](concepts/00-overall-architecture.md)。

## 核心概念篇（concepts/）

* [00 整体架构与ESM协议](concepts/00-overall-architecture.md) — anywidget 设计理念、ESM 零构建契约、双 API 层（Python/JS）架构、五个核心架构洞察。
* [01 Widget基类与生命周期](concepts/01-widget-lifecycle.md) — AnyWidget 类定义、_esm/_css 声明式定义、JS 生命周期钩子（initialize/render）、AbortSignal 统一资源清理机制。
* [02 Trait同步与双向绑定](concepts/02-trait-sync.md) — WidgetTrait 描述符协议、双观察者系统（Python traitlets ↔ JS model）、状态自动适配层、二进制数据零拷贝传输。
* [03 前端通信协议](concepts/03-frontend-communication.md) — Comm 通道建立流程、消息类型定义（update/custom/error）、ESM 导出格式约定、Custom Messages 双向自定义消息。
* [04 HMR热更新](concepts/04-hmr-dev.md) — 文件监视机制（watchfiles）、SolidJS 响应式细粒度更新、Vite 插件集成开发工作流、开发/生产双模式切换。
* [05 多框架桥接](concepts/05-framework-bridges.md) — React/Svelte/Vue 框架适配层、TypeScript 类型推断系统、model proxy 响应式代理、跨框架组件封装模式。

## 实战示例（examples/）

* [Counter Widget入门](examples/counter-widget.md) — 基础 Widget 定义、ESM 模块绑定、Trait 同步演示，覆盖最小组件开发全流程。
* [双向绑定高级用法](examples/two-way-binding.md) — 多 Trait 类型绑定、Custom Messages 自定义消息、二进制数据传输实战。
* [Vite集成与HMR](examples/vite-integration.md) — Vite 开发服务器配置、热更新即时反馈体验、多前端框架集成实战。

## 信源登记簿（references/）

* [widget-base](references/widget-base.md) — AnyWidget 基类与生命周期实现，覆盖 `widget.py`、`__init__.py` 核心模块。
* [traits](references/traits.md) — Trait 同步与数据绑定机制，覆盖 `_traits.py`、`_protocols.py` 核心模块。
* [esm-protocol](references/esm-protocol.md) — ESM 前端协议与通信层，覆盖 `_file_contents.py` 及 JS runtime 核心模块。
* [descriptor](references/descriptor.md) — 描述符协议与文件内容管理，覆盖 `_descriptor.py`、`_file_contents.py` 核心模块。
* [hmr](references/hmr.md) — HMR 热更新与开发工作流，覆盖 JS runtime 及 `packages/vite/` 插件。
* [framework-bridges](references/framework-bridges.md) — 多前端框架桥接层，覆盖 `packages/types`、`packages/react`、`packages/svelte`、`packages/vue` 适配包。

## 信任与生命周期说明

* **status**：stable。全部 15 个内容文档（6 个概念 + 3 个示例 + 6 个信源登记）均基于对 anywidget 源码（`external/libs/ai/Anything/anywidget/` 目录）核心模块的逐文件阅读与事实提取（560 条源码事实 F-001~F-560），经 seven-concepts 方法论 R→I→E 三阶段流程生成。
* **stale_after**：2027-08-23。anywidget 核心架构（ESM 零构建契约/Python WidgetTrait 描述符/JS Runtime 消息循环/SolidJS 响应式 HMR）自 0.x 以来保持稳定，新框架适配和工具不断添加但核心设计不变；该日期作为针对未来大版本（如 1.0 引入 breaking change）的保守重新评估节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻；`verified.at` 记录 V 阶段对抗审查核验事件，两者分离、可追溯。

本知识包共收录 15 个内容文档（6 个概念 + 3 个示例 + 6 个信源登记），另含 3 个子目录 index.md 与根 index.md、log.md。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
