---
type: Reference
title: Python 后端 API 参考
description: Python 后端核心类与方法参考，包含 BaseChatModel、YChat、WsChatModel、ChatManager
tags: [python, api, backend, reference]
sources:
  - id: models-py
    resource: external/libs/jupyter/jupyter-chat/python/jupyterlab-chat/jupyterlab_chat/models.py
    title: models.py
  - id: ychat-py
    resource: external/libs/jupyter/jupyter-chat/python/jupyterlab-chat/jupyterlab_chat/ychat.py
    title: ychat.py
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

# Python 后端 API 参考

本页介绍 Python 后端的核心类、抽象基类和事件系统。

## BaseChatModel（抽象基类）

所有聊天模型的抽象基类，定义统一接口使 RTC 和 WebSocket 模式行为一致。[^models-py]

```python
class BaseChatModel(ABC):
    # 标识与路径
    @abstractmethod
    def get_id(self) -> str: ...           # 稳定的 chat ID（UUID hex）

    @abstractmethod
    def get_path(self) -> str: ...         # .chat 文件路径

    # 数据访问
    @abstractmethod
    def get_message(self, id: str) -> Optional[Message]: ...
    @abstractmethod
    def get_messages(self) -> list[Message]: ...
    @abstractmethod
    def get_users(self) -> dict[str, User]: ...
    @abstractmethod
    def get_metadata(self) -> dict: ...
    @abstractmethod
    def get_attachments(self) -> dict: ...

    # 写入操作
    @abstractmethod
    def add_message(self, new_message: NewMessage,
                    trigger_actions: list[Callable] | None = None) -> str: ...
    @abstractmethod
    def update_message(self, update: Message, append: bool = False,
                       trigger_actions: list[Callable] | None = None) -> None: ...
    @abstractmethod
    def set_attachment(self, attachment) -> str: ...
    @abstractmethod
    def set_user(self, user: User) -> None: ...
    @abstractmethod
    def set_metadata(self, name: str, metadata: Any) -> None: ...

    # 观察者模式
    @abstractmethod
    def observe_messages(self, callback: MessageObserverCallback) -> MessageObserver: ...
    @abstractmethod
    def unobserve_messages(self, observer: MessageObserver) -> None: ...

    # 写作状态
    @abstractmethod
    def broadcast_writing_status(self, user: User, status=None) -> None: ...
```

## YChat（RTC 模式模型）

基于 Yjs (pycrdt) 的 CRDT 共享文档实现，同时继承 `YBaseDoc` 和 `BaseChatModel`。[^ychat-py]

### 构造与初始化

```python
class YChat(YBaseDoc, BaseChatModel):
    def __init__(self, awareness: Awareness | None = None,
                 file_id_manager: IFileIdManager | None = None):
        # 初始化 Yjs 共享结构
        self._yusers: YMap       # 用户 Map (username -> user JSON)
        self._ymessages: YArray  # 消息 Array
        self._yattachments: YMap # 附件 Map (attachment_id -> attachment JSON)
        self._ymetadata: YMap    # 元数据 Map
        self._writers: dict[str, dict]  # 写作用户状态

        # 订阅 Yjs 事件
        self._ymessages.observe(self._on_messages_change)
        self._ystate.observe(self._initialize)
```

### 关键属性与方法

| 属性/方法 | 说明 |
|---|---|
| `version = "1.0.0"` | 文档版本号 |
| `get_id()` | 从 metadata 获取 id，不存在则生成 uuid4 |
| `get_path()` | 通过 file_id_manager 从 room_id 解析路径 |
| `add_message()` | 生成 timestamp+uuid，按时间排序插入 YArray，执行 trigger_actions |
| `update_message()` | 更新消息，append=True 追加 body |
| `set_attachment()` | JSON 序列化去重，存储到 YMap，返回 attachment ID |
| `broadcast_writing_status()` | 更新 _writers dict，通过 awareness 发布 WRITERS_AWARENESS_KEY |
| `observe_messages()` | 订阅 _ymessages 变化，分发 ChatMessageEvent；dirty 状态跳过事件 |
| `get()` | 返回 JSON 字符串 `{messages, users, attachments, metadata}` |
| `set(value)` | 从 JSON 重建所有 Yjs 结构（users→attachments→messages→metadata 顺序） |

### 时间戳处理

- 新消息创建时 `raw_time=true`，使用客户端时间戳
- `_on_messages_change()` 检测到 `raw_time` 时调用 `_set_timestamp()` 更新为服务器时间
- `_set_timestamp()` 更新后重新按时间排序插入消息

## WsChatModel（WebSocket 模式模型）

内存 dict + JSON 文件持久化的模型实现，继承 `BaseChatModel`。[^ws-model-py]

```python
class WsChatModel(BaseChatModel):
    def __init__(self, path: str, root_dir: Path,
                 event_logger: EventLogger | None = None):
        self.path = path
        self.root_dir = root_dir
        self.handlers: dict[str, websocket.WebSocketHandler] = {}
        self._messages: list[dict] = []
        self._indexes_by_id: dict[str, int] = {}
        self._users: dict[str, dict] = {}
        self._attachments: dict[str, dict] = {}
        self._metadata: dict[str, object] = {}
```

### 关键方法

| 方法 | 说明 |
|---|---|
| `load_from_file()` | 从磁盘 JSON 文件加载数据，重建 _indexes_by_id |
| `save()` | 将内存状态写入磁盘 JSON 文件 |
| `broadcast(message)` | 向所有连接的 WebSocket handler 广播消息 |
| `broadcast_writing_status()` | 广播 ephemeral 写作状态（不持久化） |
| `resolve_message(message)` | 将消息中的 attachment ID 替换为完整附件对象 |
| `add_message()` | 生成 timestamp+uuid，按时间插入，save() 后广播，发射 SERVER_MSG_SENT 事件 |
| `_on_contents_event()` | 监听 ContentsManager rename 事件，更新文件路径 |

## ChatManager

聊天模型生命周期管理器，继承 `LoggingConfigurable`。[^chat-manager-py]

```python
class ChatManager(LoggingConfigurable):
    inactivity_timeout_s = Float(300.0).tag(config=True)  # 不活跃超时（秒）
    poll_interval_s = Float(60.0).tag(config=True)       # 轮询间隔（秒）
```

### 关键方法

| 方法 | 说明 |
|---|---|
| `observe_chats(callback)` | 订阅 chat 生命周期事件（CHAT_ROOM_EVENT_SCHEMA_ID） |
| `get_chat(chat_id)` | 通过 chat ID 获取模型 |
| `get_chat_by_path(path)` | 通过路径获取模型 |
| `ws_open(path)` | WebSocket 连接入口，获取或创建 WsChatModel，首次创建发 OPENED 事件 |
| `on_client_connect(path, client_id, chat_id)` | 客户端连接，发 CLIENT_CONNECTED 事件 |
| `on_client_disconnect(path, client_id, chat_id)` | 客户端断开，发 CLIENT_DISCONNECTED 事件 |
| `ws_client_gone(chat_id)` | 最后客户端离开，启动不活跃计时器 |
| `ws_activity(chat_id)` | 更新最后活跃时间 |
| `get_rtc_chat(room_id)` | RTC 模式下通过 room_id 获取或创建 YChat |

### 事件系统

ChatManager 通过 Jupyter Events 发射传输无关的生命周期事件：[^events-py]

```python
@dataclass(frozen=True)
class ChatEvent:
    path: str
    action: ChatEventAction  # OPENED | CLOSED | DELETED | CLIENT_CONNECTED | CLIENT_DISCONNECTED
    chat_id: str             # 稳定的 chat ID
    client_id: str | None = None  # 仅 client_* 事件
```

Schema ID: `https://schema.jupyter.org/jupyterlab_chat/room/v1`

### RTC 事件转发

RTC 模式下，ChatManager 监听 jupyter_collaboration 的 session 事件：
- room_id 格式: `{format}:{type}:{file_id}`，type=="chat" 时转发
- 解析出 file_id 后映射为 chat path
- 将 collaboration 事件转换为统一的 ChatEvent

## ChatMessageEvent（消息事件）

```python
class ChatMessageAction(str, Enum):
    CLIENT_MSG_RECEIVED = "client_msg_received"   # 收到客户端新消息
    CLIENT_MSG_EDITED = "client_msg_edited"       # 客户端编辑消息
    SERVER_MSG_SENT = "server_msg_sent"           # 服务器发送消息
    SERVER_MSG_UPDATED = "server_msg_updated"     # 服务器更新消息

@dataclass
class ChatMessageEvent:
    action: ChatMessageAction
    message: Message
```

通过 `model.observe_messages(callback)` 注册的回调接收此事件。
