---
type: Concept
title: 双传输架构
description: RTC 与 WebSocket 两种传输模式的设计原理、切换机制与统一接口
tags: [architecture, transport, rtc, websocket, core]
sources:
  - id: factory-ts
    resource: external/libs/jupyter/jupyter-chat/packages/jupyterlab-chat/src/factory.ts
    title: factory.ts
  - id: ws-handler-ts
    resource: external/libs/jupyter/jupyter-chat/packages/jupyterlab-chat/src/websocket-handler.ts
    title: websocket-handler.ts
  - id: ychat-py
    resource: external/libs/jupyter/jupyter-chat/python/jupyterlab-chat/jupyterlab_chat/ychat.py
    title: ychat.py
  - id: ws-model-py
    resource: external/libs/jupyter/jupyter-chat/python/jupyterlab-chat/jupyterlab_chat/websocket_model.py
    title: websocket_model.py
  - id: init-py
    resource: external/libs/jupyter/jupyter-chat/python/jupyterlab-chat/jupyterlab_chat/__init__.py
    title: __init__.py
status: stable
generated:
  by: reference_agent/source-code-to-okf-wiki
  at: 2025-12-22
---

# 双传输架构

jupyter-chat 设计了双传输架构，支持 RTC（实时协作）和 WebSocket 两种通信模式，通过 `BaseChatModel` 抽象基类统一接口。

## 模式选择

传输模式在服务端启动时由 `jupyter_collaboration` 是否启用决定：[^init-py]

```python
# __init__.py 中
rtc_info = rtc_lib.RTCInfo()
if not rtc_info.enabled:
    # WebSocket 模式：注册 /api/jupyter-chat/ws 端点
    web_app.add_handlers(".*", [(url_path_join(ws_url, "api/jupyter-chat/ws"), WSChatHandler)])
```

前端通过 `ChatWidgetFactory.contentProviderId` 属性对应：[^factory-ts]

```typescript
get contentProviderId(): string | undefined {
  return this._collaborative ? 'rtc' : undefined;
}
```

- `collaborative=true`（默认）：返回 `'rtc'`，jupyter_collaboration 自动创建 RtcContentProvider
- `collaborative=false`：返回 `undefined`，使用默认 HTTP provider

## RTC 模式

### 架构

RTC 模式基于 Yjs CRDT（Conflict-free Replicated Data Type），通过 jupyter_collaboration 扩展提供的 WebSocket 通道同步共享文档：

```
┌──────────────────────────────────────────────────────────┐
│                      RTC 模式                            │
│                                                          │
│  Frontend (TS)              Backend (Python)             │
│  ┌─────────────┐            ┌─────────────┐              │
│  │  YChat (TS) │◄─Yjs WS──►│  YChat (py) │              │
│  │  - Y.Map    │  (y-proto- │  - pycrdt   │              │
│  │  - Y.Array  │   cols)    │  - YDoc     │              │
│  │  - Awareness│            │  - Awareness│              │
│  └──────┬──────┘            └──────┬──────┘              │
│         │                          │                     │
│         ▼                          ▼                     │
│  ┌─────────────┐            ┌─────────────┐              │
│  │ LabChatModel│            │ ChatManager │              │
│  │ (extends    │            │ (生命周期)   │              │
│  │  Abstract-  │            │  - get_rtc  │              │
│  │  ChatModel) │            │    _chat()  │              │
│  └─────────────┘            └─────────────┘              │
└──────────────────────────────────────────────────────────┘
```

### 后端实现：YChat

`YChat` 同时继承 `YBaseDoc`（jupyter_ydoc）和 `BaseChatModel`：[^ychat-py]

```python
class YChat(YBaseDoc, BaseChatModel):
    def __init__(self, awareness=None, file_id_manager=None):
        self._yusers = self._ydoc.get(Map, "users")       # Y.Map: username -> user JSON
        self._ymessages = self._ydoc.get(Array, "messages") # Y.Array: 消息列表
        self._yattachments = self._ydoc.get(Map, "attachments") # Y.Map: id -> attachment JSON
        self._ymetadata = self._ydoc.get(Map, "metadata")   # Y.Map: 元数据（含 id）
```

- **消息同步**：所有客户端共享同一个 YDoc，修改自动通过 CRDT 合并
- **写作状态**：通过 Yjs Awareness 的 `WRITERS_AWARENESS_KEY="writers"` 通道发布
- **事件分发**：`_ymessages.observe()` 监听 YArray 变化，转换为 `ChatMessageEvent` 分发给观察者
- **时间同步**：客户端创建消息时设 `raw_time=true`，服务器在 `_on_messages_change()` 中校正为服务器时间

详见 [Yjs CRDT 同步机制](/concepts/crdt-sync.md)。

## WebSocket 模式

### 架构

WebSocket 模式使用自定义 JSON 帧协议，后端维护内存状态并持久化到 `.chat` JSON 文件：

```
┌──────────────────────────────────────────────────────────┐
│                   WebSocket 模式                          │
│                                                          │
│  Frontend (TS)              Backend (Python)             │
│  ┌─────────────────┐        ┌─────────────────┐          │
│  │ WebSocketHandler│◄─JSON─►│ WSChatHandler   │          │
│  │  - 自动重连     │  WS    │  (Tornado WS)   │          │
│  │  - 消息解析     │        │  - 认证鉴权     │          │
│  │  - 用户映射     │        │  - 帧路由       │          │
│  └────────┬────────┘        └────────┬────────┘          │
│           │                          │                   │
│           ▼                          ▼                   │
│  ┌─────────────────┐        ┌─────────────────┐          │
│  │ LabChatModel    │        │ WsChatModel     │          │
│  │ (AbstractChat-  │        │  - _messages    │          │
│  │  Model)         │        │  - _users       │          │
│  │                 │        │  - _attachments │          │
│  │                 │        │  - save/load    │          │
│  └─────────────────┘        └────────┬────────┘          │
│                                      │                   │
│                                      ▼                   │
│                              ┌─────────────────┐          │
│                              │ .chat JSON 文件 │          │
│                              │ (磁盘持久化)    │          │
│                              └─────────────────┘          │
└──────────────────────────────────────────────────────────┘
```

### 前端：WebSocketHandler

负责单个聊天文件的 WebSocket 连接管理：[^ws-handler-ts]

- **自动重连**：code 1006（异常关闭）时 1 秒后重连
- **连接初始化**：URL 格式 `ws://host/api/jupyter-chat/ws?path=<path>&token=<token>&user=<user>`
- **帧处理**：
  - `connection`：接收历史消息和用户列表，resolve `ready` promise
  - `users`：更新用户映射
  - `msg`：接收新消息或更新，转换为 `IMessageContent` 通过 `messageReceived` 信号发射
  - `writing`：服务器推送的写作状态（AI 机器人等）

### 后端：WsChatModel

内存模型实现 `BaseChatModel`：[^ws-model-py]

- **持久化**：`save()` 写入 JSON 文件，`load_from_file()` 从文件加载
- **广播**：`broadcast()` 向所有连接的 handler 发送消息
- **附件解析**：`resolve_message()` 将消息中的 attachment ID 替换为完整对象
- **路径追踪**：监听 ContentsManager 的 rename 事件，追踪文件移动
- **用户合并**：优先使用客户端传入的 user 对象（与 RTC 模式一致），回退到认证用户

### WebSocket 帧协议

**客户端发送帧**：

```jsonc
// 新消息
{ "type": "msg", "id": "<uuid>", "body": "hello", "user": {...}, "mentions": [...], "metadata": {...} }

// 更新消息
{ "type": "msg", "is_update": true, "id": "<msg-id>", "body": "edited", "edited": true }

// 删除消息
{ "type": "msg", "is_update": true, "id": "<msg-id>", "body": "", "deleted": true }
```

**服务端发送帧**：

```jsonc
// 连接响应
{ "type": "connection", "client_id": "<id>", "id": "<chat-id>", "messages": [...], "users": {...} }

// 用户更新
{ "type": "users", "users": {...} }

// 新消息/更新
{ "type": "msg", "message": {...} }

// 写作状态
{ "type": "writing", "user": {...}, "state": true, "messageID": "...", "typingIndicator": "..." }
```

## 统一接口：BaseChatModel

两种模式共享 `BaseChatModel` 抽象基类，确保 trigger actions（如 `find_mentions`）和 bot 扩展在两种模式下行为一致：[^ws-model-py]

```python
class BaseChatModel(ABC):
    """统一接口，使 trigger actions 和 bot 工作方式与 RTC 模式相同。"""
    @abstractmethod
    def add_message(self, new_message: NewMessage, trigger_actions=None) -> str: ...
    @abstractmethod
    def observe_messages(self, callback) -> MessageObserver: ...
    # ...
```

这一设计使得上层应用代码无需关心底层传输方式，切换模式对 UI 和业务逻辑透明。

## 稳定标识：chat_id vs room_id

两种模式都使用稳定的 `chat_id`（存储在 metadata 中，UUID hex）作为跨传输的唯一标识：

- RTC 模式：`room_id` 是 jupyter_collaboration 的内部标识（格式 `{format}:{type}:{file_id}`），不作为 chat 的稳定 ID
- WebSocket 模式：不使用 room_id，直接通过 path 定位
- `ChatEvent` 始终携带 `chat_id`，不携带 `room_id`[^events-py 注释]

## 相关概念

- [Yjs CRDT 同步机制](/concepts/crdt-sync.md)
- [消息生命周期](/concepts/message-lifecycle.md)
- [ChatManager 生命周期管理](/concepts/chat-manager.md)
- [生命周期事件](/concepts/lifecycle-events.md)

[^factory-ts]: factory.ts
[^init-py]: jupyterlite_echo_kernel/__init__.py
[^ws-handler-ts]: websocket-handler.ts
[^ws-model-py]: websocket_model.py
[^ychat-py]: ychat.py
