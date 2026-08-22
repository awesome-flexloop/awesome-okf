---
type: Concept
title: 生命周期事件
description: Chat 生命周期事件总线、消息观察者模式与事件驱动架构设计
tags: [events, lifecycle, observer, architecture]
sources:
  - id: events-py
    resource: external/libs/jupyter/jupyter-chat/python/jupyterlab-chat/jupyterlab_chat/events.py
    title: events.py
  - id: chat-manager-py
    resource: external/libs/jupyter/jupyter-chat/python/jupyterlab-chat/jupyterlab_chat/chat_manager.py
    title: chat_manager.py
  - id: models-py
    resource: external/libs/jupyter/jupyter-chat/python/jupyterlab-chat/jupyterlab_chat/models.py
    title: models.py
status: stable
generated:
  by: reference_agent/source-code-to-okf-wiki
  at: 2025-12-22
---

# 生命周期事件

jupyter-chat 后端采用双层事件系统：**Chat 生命周期事件总线**（房间级）和**消息观察者模式**（消息级），实现事件驱动的插件架构。

## 事件架构总览

```
┌─────────────────────────────────────────────────────────────┐
│                    事件系统架构                               │
│                                                             │
│  ┌─────────────────────────────┐   ┌─────────────────────┐  │
│  │  Chat 生命周期事件总线        │   │  消息观察者模式       │  │
│  │  (Jupyter Events)            │   │  (MessageObserver)  │  │
│  │                             │   │                     │  │
│  │  房间级事件:                 │   │  消息级事件:         │  │
│  │  - opened                   │   │  - CLIENT_MSG_RECEIVED
│  │  - closed                   │   │  - CLIENT_MSG_EDITED │
│  │  - deleted                  │   │  - SERVER_MSG_SENT  │
│  │  - client_connected         │   │  - SERVER_MSG_UPDATED
│  │  - client_disconnected      │   │                     │  │
│  │                             │   │  作用域: 单个 chat  │  │
│  │  作用域: 全局所有 chat       │   │  模型               │  │
│  └──────────────┬──────────────┘   └──────────┬──────────┘  │
│                 │                             │             │
│                 ▼                             ▼             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    ChatManager                        │   │
│  │  - 事件转发（RTC rooms → ChatEvent）                  │   │
│  │  - 模型生命周期管理（创建/获取/释放）                  │   │
│  │  - 内存管理（不活跃超时 GC）                          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Chat 生命周期事件总线

基于 Jupyter Events 系统，提供传输无关的 chat 房间生命周期事件。[^events-py]

### Event Schema

Schema ID：`https://schema.jupyter.org/jupyterlab_chat/room/v1`

```python
CHAT_ROOM_EVENT_SCHEMA = {
    "$id": CHAT_ROOM_EVENT_SCHEMA_ID,
    "version": "1",
    "type": "object",
    "required": ["path", "action", "chat_id"],
    "properties": {
        "path": {"type": "string", "description": ".chat 文件的服务器相对路径"},
        "action": {
            "enum": ["opened", "closed", "deleted",
                     "client_connected", "client_disconnected"]
        },
        "chat_id": {"type": "string", "description": "稳定的 chat ID"},
        "client_id": {"type": "string", "description": "仅 client_* 事件"}
    },
    "additionalProperties": False
}
```

### ChatEvent 数据类

```python
@dataclass(frozen=True)
class ChatEvent:
    path: str
    action: ChatEventAction
    chat_id: str           # 稳定的传输无关 ID
    client_id: str | None = None

    def to_data(self) -> dict:
        data = {"path": self.path, "action": self.action.value, "chat_id": self.chat_id}
        if self.client_id:
            data["client_id"] = self.client_id
        return data
```

### ChatEventAction 枚举

| 动作 | 级别 | 触发时机 | client_id |
|---|---|---|---|
| `OPENED` | 房间级 | chat 模型首次创建（第一个客户端连接） | 无 |
| `CLOSED` | 房间级 | chat 模型被释放（不活跃超时/GC） | 无 |
| `DELETED` | 房间级 | chat 文件被删除 | 无 |
| `CLIENT_CONNECTED` | 客户端级 | 每个客户端连接 | 有 |
| `CLIENT_DISCONNECTED` | 客户端级 | 每个客户端断开 | 有 |

### 设计要点：chat_id vs room_id

事件中**始终携带 `chat_id` 而非 `room_id`**：
- `chat_id`：稳定的 UUID，存储在 metadata 中，跨传输一致
- `room_id`：RTC 传输内部标识（格式 `{format}:{type}:{file_id}`），仅 ChatManager/YChat 内部使用
- 这确保了事件消费者无需关心底层传输方式

## 消息观察者模式

每个 chat 模型实例支持消息级观察者，用于实现 bot 响应、日志记录等功能。[^models-py]

### 事件类型

```python
class ChatMessageAction(str, Enum):
    CLIENT_MSG_RECEIVED = "client_msg_received"   # 服务器收到客户端消息
    CLIENT_MSG_EDITED = "client_msg_edited"       # 服务器收到客户端编辑
    SERVER_MSG_SENT = "server_msg_sent"           # 服务器广播新消息
    SERVER_MSG_UPDATED = "server_msg_updated"     # 服务器广播消息更新
```

### ChatMessageEvent

```python
@dataclass
class ChatMessageEvent:
    action: ChatMessageAction
    message: Message    # 完整消息对象（含 body, sender, time 等）
```

### 注册与注销

```python
# 注册观察者
observer = model.observe_messages(callback)

# 注销观察者
model.unobserve_messages(observer)
```

### 实现差异

**YChat（RTC 模式）**：通过 `YArray.observe()` 监听 CRDT 变化：

```python
def observe_messages(self, callback):
    self._message_observers.append(callback)
    return MessageObserver(_handle=callback)

def _dispatch_message_event(self, event: Y.YArrayEvent):
    # dirty 状态下跳过事件（文档加载中）
    if self.dirty:
        return
    for delta in event.delta:
        if "insert" in delta:
            for msg_dict in delta["insert"]:
                message = Message(**msg_dict)
                # 判断是新消息还是更新...
                self._emit_message_event(action, message)
```

**WsChatModel（WebSocket 模式）**：在 add_message/update_message 后直接发射：

```python
def add_message(self, new_message, trigger_actions=None):
    # ... 处理消息 ...
    self._emit_message_event(ChatMessageAction.SERVER_MSG_SENT, message)
```

### 错误处理

观察者中的异常被捕获并记录日志，**不会中断消息处理流程**：

```python
def _emit_message_event(self, action, message):
    for callback in list(self._message_observers):
        try:
            callback(ChatMessageEvent(action=action, message=message))
        except Exception:
            _log.exception("Message observer failed for %s", action)
```

## RTC 事件转发

RTC 模式下，ChatManager 监听 jupyter_collaboration 的房间事件并转发为统一的 ChatEvent：[^chat-manager-py]

```python
def _wire_rtc_forwarding(self):
    """监听 jupyter_collaboration 事件，转发到 ChatEvent 总线"""
    async def on_rtc_event(logger, schema_id, data):
        room_id = data.get("room_id")
        if not room_id:
            return

        # 解析 room_id: "{format}:{type}:{file_id}"
        parts = room_id.rsplit(":", 1)
        if len(parts) != 2:
            return
        room_type, file_id = parts

        # 只处理 chat 类型的房间
        if room_type != "chat":
            return

        # 解析路径和 chat_id
        path = self._file_id_manager.get_path(file_id)
        chat = self.get_rtc_chat(room_id)
        chat_id = chat.get_id() if chat else None

        # 映射 collaboration 事件到 ChatEvent
        rtc_action = data.get("action")
        if rtc_action == "connect":
            self.emit_event(path, ChatEventAction.CLIENT_CONNECTED,
                          client_id=data.get("client_id"), chat_id=chat_id)
        elif rtc_action == "disconnect":
            self.emit_event(path, ChatEventAction.CLIENT_DISCONNECTED,
                          client_id=data.get("client_id"), chat_id=chat_id)
```

## 事件监听示例

### 监听房间生命周期

```python
async def on_chat_event(logger, schema_id: str, data: dict):
    action = data["action"]
    chat_id = data["chat_id"]
    path = data["path"]

    if action == "opened":
        # 新 chat 被打开，可以初始化 bot 状态
        await setup_bot_for_chat(chat_id, path)
    elif action == "client_connected":
        # 用户加入，可以发送欢迎消息
        client_id = data["client_id"]
        await send_welcome(chat_id, client_id)
    elif action == "closed":
        # chat 被关闭，清理资源
        cleanup_bot_state(chat_id)

event_logger.add_listener(
    schema_id=CHAT_ROOM_EVENT_SCHEMA_ID,
    listener=on_chat_event
)
```

### 实现简单 Echo Bot

```python
def echo_bot(event: ChatMessageEvent):
    if event.action != ChatMessageAction.CLIENT_MSG_RECEIVED:
        return

    msg = event.message
    if msg.body.startswith("/echo "):
        reply = NewMessage(
            body=msg.body[6:],
            sender="echo-bot"
        )
        # 通过 model 发送回复
        # 注意：需要获取 model 引用

# 在 chat 打开时注册
model.observe_messages(echo_bot)
```

## 相关概念

- [ChatManager 生命周期管理](/concepts/chat-manager.md)
- [双传输架构](/concepts/dual-transport.md)
- [消息生命周期](/concepts/message-lifecycle.md)
- [扩展点系统](/concepts/extension-points.md)
