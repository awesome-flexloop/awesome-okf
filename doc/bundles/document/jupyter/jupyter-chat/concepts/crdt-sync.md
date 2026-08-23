---
type: Concept
title: Yjs CRDT 同步机制
description: Yjs 共享文档的数据结构、消息同步流程、Awareness 协议与时间戳处理策略
tags: [yjs, crdt, rtc, synchronization, core]
sources:
  - id: ychat-py
    resource: external/libs/jupyter/jupyter-chat/python/jupyterlab-chat/jupyterlab_chat/ychat.py
    title: ychat.py
  - id: ychat-ts
    resource: external/libs/jupyter/jupyter-chat/packages/jupyterlab-chat/src/ychat.ts
    title: ychat.ts (TS)
  - id: rtc-lib
    resource: external/libs/jupyter/jupyter-chat/python/jupyterlab-chat/jupyterlab_chat/rtc_lib.py
    title: rtc_lib.py
status: stable
generated:
  by: reference_agent/source-code-to-okf-wiki
  at: 2025-12-22
---

# Yjs CRDT 同步机制

jupyter-chat 的 RTC 模式基于 Yjs（CRDT - Conflict-free Replicated Data Type）实现实时协作同步。Python 端使用 pycrdt（Yjs 的 Python 绑定），前端使用 yjs + y-protocols。

## 共享数据结构

`YChat` 在 YDoc 中创建 4 个顶层共享类型：[^ychat-py]

```python
class YChat(YBaseDoc, BaseChatModel):
    def __init__(self, awareness=None, file_id_manager=None):
        self._yusers = self._ydoc.get(Map, "users")         # Y.Map<username, User JSON>
        self._ymessages = self._ydoc.get(Array, "messages")  # Y.Array<Message JSON>
        self._yattachments = self._ydoc.get(Map, "attachments")  # Y.Map<att_id, Attachment JSON>
        self._ymetadata = self._ydoc.get(Map, "metadata")    # Y.Map<string, Any>
```

### 数据结构选择理由

| 数据 | Yjs 类型 | 原因 |
|---|---|---|
| 用户列表 | `Y.Map` | 用户通过 username 快速查找更新 |
| 消息列表 | `Y.Array` | 消息是有序列表，按时间排序 |
| 附件 | `Y.Map` | 通过 attachment ID 快速查找和去重 |
| 元数据 | `Y.Map` | 包含 chat_id 等键值对 |

## 文档序列化

### get() - 序列化为 JSON

```python
def get(self) -> str:
    """返回文档的 JSON 字符串表示"""
    return json.dumps({
        "messages": list(self._ymessages),
        "users": dict(self._yusers),
        "attachments": dict(self._yattachments),
        "metadata": dict(self._ymetadata),
    })
```

### set() - 从 JSON 重建

```python
def set(self, value: str):
    """从 JSON 字符串重建文档"""
    data = json.loads(value)
    with self._ydoc.transaction():
        # 清空现有内容
        self._ymessages.clear()
        self._yusers.clear()
        self._yattachments.clear()
        self._ymetadata.clear()

        # 按依赖顺序重建：users → attachments → messages → metadata
        for username, user in data.get("users", {}).items():
            self._yusers[username] = user
        for att_id, att in data.get("attachments", {}).items():
            self._yattachments[att_id] = att
        for msg in data.get("messages", []):
            self._ymessages.append(msg)
        for key, val in data.get("metadata", {}).items():
            self._ymetadata[key] = val
```

**顺序很重要**：messages 可能引用 users 和 attachments（通过 username 和 attachment_id），所以必须先建立引用目标。

## 消息插入与排序

### 按时间戳插入

`add_message()` 不直接 append，而是遍历找到正确的插入位置：

```python
def add_message(self, new_message, trigger_actions=None) -> str:
    timestamp = time.time()
    msg_id = str(uuid.uuid4())
    message = Message(**asdict(new_message), time=timestamp, id=msg_id)

    # 执行 trigger actions（如 find_mentions）
    if trigger_actions:
        for callback in trigger_actions:
            callback(message, self)

    # 在 transaction 中插入
    with self._ydoc.transaction():
        msg_dict = asdict(message, dict_factory=message_asdict_factory)
        # 找到第一个时间戳大于当前消息的位置
        for i, existing in enumerate(self._ymessages):
            if existing.get("time", 0) > timestamp:
                self._ymessages.insert(i, msg_dict)
                break
        else:
            self._ymessages.append(msg_dict)
```

### 索引维护

```python
def _on_messages_change(self, event):
    """YArray observe 回调，维护索引表"""
    # 重建索引表（简单但正确）
    self._indexes_by_id = {
        m["id"]: i for i, m in enumerate(self._ymessages) if "id" in m
    }

    for delta in event.delta:
        if "insert" in delta:
            for msg in delta["insert"]:
                # 处理 raw_time：客户端设置的时间戳需要服务器校正
                if msg.get("raw_time"):
                    # 延迟到 transaction 提交后调整
                    self._ydoc.transact(
                        lambda: self._set_timestamp(msg["id"], time.time())
                    )
```

## 时间戳同步策略

### 问题

不同客户端的时钟可能不一致，直接使用客户端时间戳会导致消息顺序错乱。

### 解决方案：raw_time 两阶段提交

```
1. 客户端发送消息
   ├── 使用客户端本地时间
   └── 设置 raw_time: true

2. Yjs 同步到服务器
   ├── _on_messages_change 检测到 raw_time
   └── 调度 _set_timestamp（在新 transaction 中）

3. 服务器校正
   ├── _set_timestamp(id, server_time)
   │   ├── 从 YArray 移除原消息
   │   ├── 设置 time = server_time, raw_time = false
   │   └── 重新按时间插入正确位置
   └── 通过 CRDT 同步回所有客户端
```

```python
def _set_timestamp(self, msg_id: str, new_time: float):
    """更新消息时间戳并重新排序"""
    idx = self._indexes_by_id.get(msg_id)
    if idx is None:
        return

    with self._ydoc.transaction():
        msg = self._ymessages[idx]
        msg["time"] = new_time
        msg["raw_time"] = False
        # 移除后重新插入到正确位置
        del self._ymessages[idx]
        insert_idx = next(
            (i for i, m in enumerate(self._ymessages) if m.get("time", 0) > new_time),
            len(self._ymessages)
        )
        self._ymessages.insert(insert_idx, msg)
```

这个两阶段策略确保了：
- 客户端发送后立即显示（使用本地时间）
- 最终消息顺序由服务器时间戳决定
- 所有客户端最终看到相同的消息顺序（CRDT 收敛）

## Awareness 协议

写作状态（typing indicator）不持久化到 YDoc，而是通过 Yjs Awareness 协议实时广播：[^ychat-py]

```python
WRITERS_AWARENESS_KEY = "writers"

def broadcast_writing_status(self, user: User, status=None):
    if status is None:
        # 停止写作：从 writers 移除
        self._writers.pop(user.username, None)
    else:
        # 开始/更新写作状态
        self._writers[user.username] = {
            "user": asdict(user),
            "messageID": status.get("messageID"),
            "typingIndicator": status.get("typingIndicator"),
        }
    # 发布到 awareness
    self._publish_writers()

def _publish_writers(self):
    if self.awareness is not None:
        self.awareness.set_local_state_field(
            WRITERS_AWARENESS_KEY, list(self._writers.values())
        )
```

**Awareness vs YDoc**：
- **YDoc**：持久化数据（消息、用户、附件、元数据），CRDT 自动合并，离线支持
- **Awareness**：临时状态（谁在输入），不持久化，仅在线用户可见，断开自动清除

## Chat ID 管理

每个聊天文档有一个稳定的 UUID 作为 `chat_id`：

```python
def get_id(self) -> str:
    """获取 chat 的稳定 ID"""
    chat_id = self._ymetadata.get("id")
    if chat_id is None:
        # 异步创建 ID（避免在 transaction 内）
        self._ydoc.transact(self.create_id)
        chat_id = self._ymetadata.get("id")
    return chat_id

def create_id(self):
    """在 metadata 中生成新 UUID"""
    if self._ymetadata.get("id") is None:
        new_id = uuid.uuid4().hex
        self._ymetadata["id"] = new_id
```

**初始化时机**：`_initialize()` 在 dirty=false（首次加载）且 metadata 无 id 时调度 create_id。

## 路径解析

RTC 模式下，YChat 通过 `file_id_manager` 将 room_id 映射到文件路径：[^ychat-py]

```python
def get_path(self) -> str:
    if self._path is not None:
        return self._path

    if self.file_id_manager is not None and self.room_id is not None:
        # room_id 格式: "{format}:{type}:{file_id}"
        parts = self.room_id.rsplit(":", 1)
        if len(parts) == 2:
            file_id = parts[1]
            path = self.file_id_manager.get_path(file_id)
            if path is not None:
                self._path = path
                return path
    # 回退到 initial_path
    return self._initial_path or ""
```

## 版本号

```python
@property
def version(self) -> str:
    return "1.0.0"
```

YChat 通过 jupyter_ydoc 的 entry-point 系统注册：[^pyproject.toml]

```toml
[project.entry-points."jupyter_ydoc"]
chat = "jupyterlab_chat.ychat:YChat"
```

这使得 jupyter_collaboration 能通过内容类型 `chat` 自动找到对应的 YDoc 实现。

## 相关概念

- [双传输架构](/concepts/dual-transport.md)
- [消息生命周期](/concepts/message-lifecycle.md)
- [ChatManager 生命周期管理](/concepts/chat-manager.md)
