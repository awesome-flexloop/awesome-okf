---
type: Concept
title: 整体架构概览
description: jupyter-chat 的整体架构、包结构、前后端通信模式与核心设计原则
tags: [architecture, overview, core]
sources:
  - id: pkg-json
    resource: external/libs/jupyter/jupyter-chat/package.json
    title: root package.json
  - id: index-ts
    resource: external/libs/jupyter/jupyter-chat/packages/jupyter-chat/src/index.ts
    title: "@jupyter/chat index.ts"
  - id: pyproject
    resource: external/libs/jupyter/jupyter-chat/python/jupyterlab-chat/pyproject.toml
    title: pyproject.toml
status: stable
generated:
  by: reference_agent/source-code-to-okf-wiki
  at: 2025-12-22
---

# 整体架构概览

jupyter-chat 是 JupyterLab 的实时协作聊天扩展，采用 Monorepo 结构，包含 3 个 TypeScript 包和 1 个 Python 包。

## 包结构

```
jupyter-chat/
├── packages/
│   ├── jupyter-chat/           # @jupyter/chat - 核心 UI 组件库（React）
│   │   └── src/
│   │       ├── components/     # React 组件（消息列表、输入框、附件等）
│   │       ├── widgets/        # Lumino Widget 封装（ChatWidget、MultiChatPanel）
│   │       ├── registers/      # 扩展点注册器
│   │       ├── model.ts        # AbstractChatModel、IChatModel
│   │       ├── input-model.ts  # InputModel
│   │       ├── message.ts      # Message 类
│   │       ├── types.ts        # 核心类型定义
│   │       ├── context.ts      # React Context
│   │       ├── tokens.ts       # Lumino Token
│   │       └── index.ts        # 包入口
│   ├── jupyterlab-chat/        # jupyterlab-chat - JupyterLab 集成层
│   │   └── src/
│   │       ├── factory.ts      # ChatWidgetFactory、LabChatModelFactory
│   │       ├── model.ts        # LabChatModel
│   │       ├── widget.tsx      # LabChatPanel
│   │       ├── rtc/            # RTC 同步实现
│   │       ├── websocket-handler.ts # WebSocket 客户端
│   │       ├── ychat.ts        # Yjs 前端绑定
│   │       └── token.ts        # 集成层 Token 和命令
│   └── jupyterlab-chat-extension/ # JupyterLab 扩展入口
└── python/
    └── jupyterlab-chat/        # jupyterlab_chat - Python 后端
        └── jupyterlab_chat/
            ├── __init__.py     # 扩展注册入口
            ├── models.py       # BaseChatModel、Message、User、事件类型
            ├── ychat.py        # YChat（Yjs/CRDT 共享文档）
            ├── websocket_model.py  # WsChatModel（WebSocket 内存模型）
            ├── websocket_handler.py # WSChatHandler（WebSocket 端点）
            ├── chat_manager.py # ChatManager（生命周期管理）
            ├── events.py       # ChatEvent schema
            └── rtc_lib.py      # RTC 辅助库
```

## 四层架构

```
┌─────────────────────────────────────────────────────────┐
│  Extension Layer (jupyterlab-chat-extension)            │
│  命令注册、菜单、设置、插件激活                          │
├─────────────────────────────────────────────────────────┤
│  Integration Layer (jupyterlab-chat)                    │
│  LabChatModel、ChatWidgetFactory、WebSocket/RTC 客户端   │
├─────────────────────────────────────────────────────────┤
│  Core UI Layer (@jupyter/chat)                          │
│  React 组件、AbstractChatModel、InputModel、注册器       │
├─────────────────────────────────────────────────────────┤
│  Backend Layer (jupyterlab_chat Python)                 │
│  YChat(Yjs/CRDT) / WsChatModel、ChatManager、WS Handler │
└─────────────────────────────────────────────────────────┘
```

## 双传输模式

jupyter-chat 支持两种实时通信模式，通过统一接口抽象：

| 特性 | RTC 模式（默认） | WebSocket 模式 |
|---|---|---|
| 同步协议 | Yjs CRDT over WebSocket（jupyter_collaboration） | 自定义 JSON over WebSocket |
| 后端模型 | `YChat`（Yjs shared document） | `WsChatModel`（内存 dict + JSON 文件） |
| 前端同步 | Yjs awareness + document provider | `WebSocketHandler`（自动重连） |
| 多用户协作 | 原生 CRDT 实时协作 | 广播式同步 |
| 离线支持 | Yjs 文档持久化 | JSON 文件持久化 |
| 内容提供者 | `contentProviderId = 'rtc'` | 默认 HTTP provider |

详见 [双传输架构](/concepts/dual-transport.md)。

## 核心设计原则

### 1. 模型驱动的 UI

所有 UI 状态由 `IChatModel` 管理，React 组件通过 Lumino Signal 订阅模型变化。组件不直接持有业务状态。

### 2. 可扩展注册器

通过 5 个注册器系统提供扩展点：
- 附件打开器（Attachment Openers）
- 聊天命令（Chat Commands）
- 消息页脚（Footers）
- 消息导言（Preambles）
- 输入工具栏（Input Toolbar）

详见 [扩展点系统](/concepts/extension-points.md)。

### 3. Token 依赖注入

使用 Lumino Token 系统进行依赖注入，第三方扩展可通过提供 Token 实现替换默认行为（如自定义欢迎消息、自定义活动单元格管理器等）。

### 4. 事件驱动

后端通过 Jupyter Events 发射传输无关的生命周期事件，通过 MessageObserver 模式发射消息事件，支持插件监听和响应。

详见 [生命周期事件](/concepts/lifecycle-events.md)。

## 前后端通信

### RTC 模式

```
前端 (Yjs Doc)          Yjs Protocol           后端 (YChat)
┌──────────┐    ┌─────────────────────┐    ┌──────────┐
│ YChat    │◄──►│ awareness + doc     │◄──►│ YChat    │
│ (前端)   │    │ sync (y-protocols)  │    │ (pycrdt) │
└──────────┘    └─────────────────────┘    └──────────┘
                      WebSocket
               (jupyter_collaboration)
```

### WebSocket 模式

```
前端                    JSON frames            后端
┌──────────────────┐    ┌──────────────┐    ┌──────────────┐
│ WebSocketHandler │◄──►│ /api/jupyter │◄──►│ WSChatHandler│
│ (自动重连)        │    │ -chat/ws     │    │ (Tornado WS) │
└──────────────────┘    └──────────────┘    └──────────────┘
                                                 │
                                                 ▼
                                          ┌──────────────┐
                                          │ WsChatModel  │
                                          │ (内存+JSON)  │
                                          └──────────────┘
```

消息帧类型（WebSocket 模式）：
- `connection`：连接建立，发送历史消息和用户列表
- `msg`：新消息或消息更新（is_update=true）
- `users`：用户列表更新
- `writing`：服务器推送的写作状态（如 AI 机器人）

## 相关概念

- [模型层架构](/concepts/model-architecture.md)
- [组件层次结构](/concepts/component-hierarchy.md)
- [Yjs CRDT 同步机制](/concepts/crdt-sync.md)
- [消息生命周期](/concepts/message-lifecycle.md)
- [ChatManager 生命周期管理](/concepts/chat-manager.md)
- [附件系统](/concepts/attachment-system.md)
