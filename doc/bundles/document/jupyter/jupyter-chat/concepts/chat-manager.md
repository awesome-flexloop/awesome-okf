---
type: Concept
title: ChatManager 生命周期管理
description: ChatManager 的职责、模型生命周期、内存管理策略与 WebSocket/RTC 模型创建
tags: [chat-manager, lifecycle, memory, backend, architecture]
sources:
  - id: chat-manager-py
    resource: external/libs/jupyter/jupyter-chat/python/jupyterlab-chat/jupyterlab_chat/chat_manager.py
    title: chat_manager.py
  - id: ws-model-py
    resource: external/libs/jupyter/jupyter-chat/python/jupyterlab-chat/jupyterlab_chat/websocket_model.py
    title: websocket_model.py
  - id: events-py
    resource: external/libs/jupyter/jupyter-chat/python/jupyterlab-chat/jupyterlab_chat/events.py
    title: events.py
status: stable
generated:
  by: reference_agent/source-code-to-okf-wiki
  at: 2025-12-22
---

# ChatManager 生命周期管理

`ChatManager` 是 Python 后端的核心管理器，统一负责聊天模型的创建、获取、事件发射和内存管理。

## 三大职责

```python
class ChatManager(LoggingConfigurable):
    """
    Responsibilities:
    1. 事件总线: observe_chats/emit_event（Jupyter Events）
    2. 模型访问: get/create RTC 和 WebSocket 模型
    3. 内存管理: 定时轮询，清理不活跃模型
    """
```

[^chat-manager-py]

## 可配置参数

```python
inactivity_timeout_s = Float(300.0).tag(config=True)  # 不活跃超时（5分钟）
poll_interval_s = Float(60.0).tag(config=True)        # 轮询间隔（1分钟）
```

通过 Jupyter Server 的配置系统设置：

```python
# jupyter_server_config.py
c.ChatManager.inactivity_timeout_s = 600  # 10分钟
c.ChatManager.poll_interval_s = 30        # 30秒轮询
```

## 内部状态

```python
def __init__(self, serverapp, rtc_enabled: bool, start_poller: bool = True):
    self._chats_by_id: dict[str, BaseChatModel] = {}   # chat_id → 模型
    self._last_activity_by_id: dict[str, float] = {}   # chat_id → 最后活跃时间
    self._pending_close: dict[str, PeriodicCallback] = {}  # 待关闭的定时器

    # RTC 模式下启动事件转发
    if rtc_enabled:
        self._wire_rtc_forwarding()

    # 启动内存管理轮询
    if start_poller:
        self._poller = PeriodicCallback(self._poll, self.poll_interval_s * 1000)
        self._poller.start()
```

模型实例存储在 `server_app.web_app.settings["chats_by_id"]` 中，供 WebSocket handler 访问。

## WebSocket 模型生命周期

### 连接：ws_open()

```python
def ws_open(self, path: str) -> WsChatModel:
    """WebSocket 连接入口，获取或创建模型"""
    # 检查是否已有模型（路径匹配）
    for chat_id, model in self._chats_by_id.items():
        if model.get_path() == path:
            self.ws_activity(chat_id)
            return model

    # 创建新模型
    model = WsChatModel(
        path=path,
        root_dir=Path(self.serverapp.root_dir),
        event_logger=self.event_logger
    )
    model.load_from_file()  # 从磁盘加载已有数据

    chat_id = model.get_id()
    self._chats_by_id[chat_id] = model
    self._last_activity_by_id[chat_id] = time.time()

    # 发射 OPENED 事件（仅首次创建）
    self.emit_event(path, ChatEventAction.OPENED, chat_id=chat_id)
    return model
```

### 客户端断开：ws_client_gone()

```python
def ws_client_gone(self, chat_id: str):
    """最后一个客户端断开后，启动宽限期计时器"""
    if chat_id in self._pending_close:
        return  # 已有计时器

    def close_if_idle():
        model = self._chats_by_id.get(chat_id)
        if model and len(model.handlers) == 0:
            # 确实没有客户端连接，释放模型
            self._close_chat(chat_id)

    # 延迟 inactivity_timeout_s 后检查
    timer = PeriodicCallback(close_if_idle, self.inactivity_timeout_s * 1000)
    timer.start()
    self._pending_close[chat_id] = timer
```

**宽限期设计**：客户端断开后不立即释放模型，而是等待一段时间。如果客户端在宽限期内重连（如页面刷新），复用已有模型状态。

### 客户端重连

如果宽限期内有新客户端连接到同一路径，`ws_open()` 会找到现有模型并取消待关闭的计时器：

```python
def ws_open(self, path):
    for chat_id, model in self._chats_by_id.items():
        if model.get_path() == path:
            # 取消待关闭计时器
            if chat_id in self._pending_close:
                self._pending_close.pop(chat_id).stop()
            self.ws_activity(chat_id)
            return model
```

## RTC 模型生命周期

RTC 模型由 jupyter_collaboration 管理，ChatManager 通过 room_id 查找和缓存：

```python
def get_rtc_chat(self, room_id: str) -> YChat | None:
    """通过 room_id 获取 RTC 聊天模型"""
    # 从 collaboration 的文档管理器获取 YDoc
    collaborator = self._collaboration.get_document(room_id)
    if collaborator is None:
        return None
    return collaborator.document  # YChat 实例
```

RTC 模型的生命周期由 jupyter_collaboration 管理，ChatManager 仅负责事件转发和 chat_id 映射。

## 客户端连接/断开事件

```python
def on_client_connect(self, path: str, client_id: str, chat_id: str):
    """客户端连接，取消待关闭计时器，发射 CLIENT_CONNECTED 事件"""
    if chat_id in self._pending_close:
        self._pending_close.pop(chat_id).stop()
    self.emit_event(path, ChatEventAction.CLIENT_CONNECTED,
                   client_id=client_id, chat_id=chat_id)

def on_client_disconnect(self, path: str, client_id: str, chat_id: str):
    """客户端断开"""
    self.emit_event(path, ChatEventAction.CLIENT_DISCONNECTED,
                   client_id=client_id, chat_id=chat_id)
```

## 内存管理：_poll()

定时轮询执行两项检查：

```python
async def _poll(self):
    now = time.time()
    to_close = []

    for chat_id, last_activity in self._last_activity_by_id.items():
        model = self._chats_by_id.get(chat_id)
        if model is None:
            continue

        # 1. 检查文件是否被删除
        path = model.get_path()
        full_path = Path(self.serverapp.root_dir) / path
        if not full_path.exists():
            self.emit_event(path, ChatEventAction.DELETED, chat_id=chat_id)
            to_close.append(chat_id)
            continue

        # 2. 检查不活跃超时（仅 WebSocket 模式）
        if isinstance(model, WsChatModel) and len(model.handlers) == 0:
            if now - last_activity > self.inactivity_timeout_s:
                to_close.append(chat_id)

    # 释放过期模型
    for chat_id in to_close:
        self._close_chat(chat_id)
```

### _close_chat()

```python
def _close_chat(self, chat_id: str):
    """释放模型资源"""
    model = self._chats_by_id.pop(chat_id, None)
    self._last_activity_by_id.pop(chat_id, None)
    self._pending_close.pop(chat_id, None)

    if model:
        path = model.get_path()
        model.dispose()  # 移除事件监听器
        self.emit_event(path, ChatEventAction.CLOSED, chat_id=chat_id)
```

## 活跃时间更新

```python
def ws_activity(self, chat_id: str):
    """更新最后活跃时间（收到消息或连接时调用）"""
    self._last_activity_by_id[chat_id] = time.time()
```

在以下场景调用：
- WebSocket 连接建立（ws_open）
- 收到客户端消息（WSChatHandler.on_message）
- 已有模型被重用（ws_open 路径匹配）

## 全局访问

ChatManager 实例注册到 Jupyter Server 的 web_app settings 中：[^__init__.py]

```python
# __init__._load_jupyter_server_extension()
chat_manager = ChatManager(serverapp, rtc_enabled=rtc_info.enabled)
web_app.settings["chat_manager"] = chat_manager
web_app.settings["chats_by_id"] = chat_manager._chats_by_id
```

WebSocket handler 通过 `self.settings["chat_manager"]` 访问。

## WebSocket 端点注册

```python
if not rtc_info.enabled:
    # 仅在非 RTC 模式下注册 WebSocket 端点
    ws_url = ujoin(base_url, "api/jupyter-chat")
    web_app.add_handlers(".*", [
        (urljoin(ws_url, "ws"), WSChatHandler)
    ])
```

## 模型查找

```python
def get_chat(self, chat_id: str) -> BaseChatModel | None:
    """通过 chat_id 获取模型"""
    return self._chats_by_id.get(chat_id)

def get_chat_by_path(self, path: str) -> BaseChatModel | None:
    """通过文件路径获取模型"""
    for model in self._chats_by_id.values():
        if model.get_path() == path:
            return model
    return None
```

## 事件发射

```python
def emit_event(self, path: str, action: ChatEventAction,
               client_id: str | None = None, chat_id: str | None = None):
    """发射 ChatEvent 到 Jupyter Events 总线"""
    event = ChatEvent(path=path, action=action,
                      chat_id=chat_id or "", client_id=client_id)
    self.event_logger.emit(
        schema_id=CHAT_ROOM_EVENT_SCHEMA_ID,
        data=event.to_data()
    )
```

## 相关概念

- [生命周期事件](lifecycle-events.md)
- [双传输架构](dual-transport.md)
- [Yjs CRDT 同步机制](crdt-sync.md)

[^__init__.py]: __init__.py 初始化模块
[^chat-manager-py]: chat_manager.py
