---
okf_version: "0.2"
type: Bundle
title: jupyter-chat OKF Wiki
description: JupyterLab 实时协作聊天扩展的完整知识文档，涵盖架构、API、扩展开发和 Bot 集成
---

# jupyter-chat

jupyter-chat 是 JupyterLab 的实时协作聊天扩展，基于 Yjs CRDT 实现多用户实时聊天，支持附件、@提及、斜杠命令和 Bot 扩展。

**版本**：0.25.0-alpha.4  
**许可证**：BSD-3-Clause  
**仓库**：https://github.com/jupyterlab/jupyter-chat

## 核心特性

- **实时协作**：基于 Yjs CRDT 自动处理多用户并发编辑
- **双传输模式**：RTC（Yjs/WebSocket）和纯 WebSocket 模式，统一接口
- **附件系统**：支持文件和 Notebook 单元格作为附件，自动去重
- **可扩展架构**：注册器系统和 Token 依赖注入支持深度定制
- **事件驱动**：生命周期事件和消息观察者支持 Bot 集成
- **JupyterLab 集成**：原生支持文件类型、命令、工具栏、快捷键

## 文档索引

### 概念文档（Concepts）

| 文档 | 说明 |
|---|---|
| [整体架构概览](/concepts/architecture-overview.md) | 包结构、四层架构、双传输模式、核心设计原则 |
| [双传输架构](/concepts/dual-transport.md) | RTC vs WebSocket 模式详解、统一接口设计 |
| [模型层架构](/concepts/model-architecture.md) | IChatModel、AbstractChatModel、InputModel 详解 |
| [组件层次结构](/concepts/component-hierarchy.md) | React 组件树、Lumino Widget 桥接、通信机制 |
| [Yjs CRDT 同步机制](/concepts/crdt-sync.md) | 共享数据结构、时间戳同步、Awareness 协议 |
| [消息生命周期](/concepts/message-lifecycle.md) | 消息从创建到渲染的完整流程 |
| [扩展点系统](/concepts/extension-points.md) | 注册器、Token 注入、元数据扩展 |
| [生命周期事件](/concepts/lifecycle-events.md) | 事件总线、消息观察者、RTC 事件转发 |
| [ChatManager 生命周期管理](/concepts/chat-manager.md) | 模型创建、内存管理、不活跃 GC |
| [附件系统](/concepts/attachment-system.md) | 附件类型、去重存储、ID 引用、打开器 |

### API 参考（References）

| 文档 | 说明 |
|---|---|
| [核心类型参考](/references/api-types.md) | IUser、IMessageContent、IConfig、IAttachment 等 |
| [Model API 参考](/references/api-model.md) | IChatModel、AbstractChatModel、InputModel、Message |
| [Python 后端 API 参考](/references/api-python.md) | BaseChatModel、YChat、WsChatModel、ChatManager |
| [Token 与命令参考](/references/api-tokens.md) | Lumino Token、命令 ID、工厂类、文件类型注册 |

### 示例（Examples）

| 文档 | 说明 |
|---|---|
| [最小聊天示例](/examples/minimal-chat.md) | 创建最基本的 JupyterLab 聊天扩展 |
| [自定义扩展示例](/examples/custom-extension.md) | 自定义工具栏、欢迎消息、元数据扩展 |
| [Bot 集成示例](/examples/bot-integration.md) | 消息观察者实现 Echo Bot、命令 Bot、AI Bot |

## 快速开始

1. 阅读[整体架构概览](/concepts/architecture-overview.md)了解系统设计
2. 按照[最小聊天示例](/examples/minimal-chat.md)创建第一个聊天扩展
3. 通过[扩展点系统](/concepts/extension-points.md)了解如何定制功能
4. 参考[Bot 集成示例](/examples/bot-integration.md)实现自动回复

## 包结构

```
jupyter-chat/
├── packages/
│   ├── jupyter-chat/           # @jupyter/chat - 核心 React UI 库
│   ├── jupyterlab-chat/        # jupyterlab-chat - JupyterLab 集成层
│   └── jupyterlab-chat-extension/ # 扩展入口
└── python/
    └── jupyterlab-chat/        # jupyterlab_chat - Python 后端
```

```{toctree}
:hidden:

concepts/architecture-overview
concepts/attachment-system
concepts/chat-manager
concepts/component-hierarchy
concepts/crdt-sync
concepts/dual-transport
concepts/extension-points
concepts/lifecycle-events
concepts/message-lifecycle
concepts/model-architecture
examples/bot-integration
examples/custom-extension
examples/minimal-chat
references/api-model
references/api-python
references/api-tokens
references/api-types
.spec/facts
.spec/insights
facts
insights
```
