---
type: Concept
title: 消息生命周期
description: 消息从创建、发送、同步、渲染到编辑/删除的完整生命周期
tags: [message, lifecycle, core]
sources:
  - id: model-ts
    resource: external/libs/jupyter/jupyter-chat/packages/jupyter-chat/src/model.ts
    title: model.ts
  - id: message-ts
    resource: external/libs/jupyter/jupyter-chat/packages/jupyter-chat/src/message.ts
    title: message.ts
  - id: input-model-ts
    resource: external/libs/jupyter/jupyter-chat/packages/jupyter-chat/src/input-model.ts
    title: input-model.ts
  - id: ychat-py
    resource: external/libs/jupyter/jupyter-chat/python/jupyterlab-chat/jupyterlab_chat/ychat.py
    title: ychat.py
  - id: ws-model-py
    resource: external/libs/jupyter/jupyter-chat/python/jupyterlab-chat/jupyterlab_chat/websocket_model.py
    title: websocket_model.py
  - id: models-py
    resource: external/libs/jupyter/jupyter-chat/python/jupyterlab-chat/jupyterlab_chat/models.py
    title: models.py
status: stable
generated:
  by: reference_agent/source-code-to-okf-wiki
  at: 2025-12-22
---

# 消息生命周期

本文档描述消息从创建到最终展示的完整生命周期，涵盖前端输入、后端处理、同步分发和 UI 渲染。

## 生命周期总览

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  1. 输入撰写  │───►│  2. 发送     │───►│  3. 后端处理 │───►│  4. 同步分发 │
│  InputModel  │    │  sendMessage │    │  add_message │    │  CRDT/广播   │
└──────────────┘    └──────────────┘    └──────────────┘    └──────┬───────┘
                                                                    │
┌──────────────┐    ┌──────────────┐    ┌──────────────┐           │
│  7. 清理归档  │◄───│  6. 编辑/删除 │◄───│  5. 渲染展示 │◄──────────┘
│  (未来扩展)   │    │ updateMessage│    │ MessageRenderer
└──────────────┘    └──────────────┘    └──────────────┘
```

## 1. 输入撰写阶段

消息在 `InputModel` 中准备：[^input-model-ts]

```typescript
// 用户输入文本
inputModel.value = "Hello @user";

// 添加附件（自动去重）
inputModel.addAttachment({ type: 'file', value: '/path/to/file.py' });

// @提及用户自动填充
inputModel.mentions = [user1, user2];

// 可选：设置元数据
inputModel.updateMetadata({ customField: 'value' });
```

**输入状态**：
- `value`: 文本内容
- `attachments`: 附件列表（JSON.stringify 去重）
- `mentions`: @提及用户列表
- `cursorIndex`: 光标位置（用于 @mention 检测）
- `currentWord`: 光标处词（实时更新）

**写作状态广播**：

```typescript
// 输入时通知其他用户"正在输入"
model.setWritingStatus(user, { typingIndicator: "正在输入..." }, 3000);
// 3 秒无输入后自动清除
```

## 2. 发送阶段

用户触发发送（Enter 或点击发送按钮）：[^input-model-ts]

```typescript
// InputModel.send()
send(): void {
  const message: INewMessage = {
    body: this.value,
    attachments: this._attachments,
    mentions: this._mentions,
    metadata: structuredClone(this._metadata)
  };
  this._onSend(message);  // → model.sendMessage(message)

  // 清空输入状态
  this.value = '';
  this._attachments = [];
  this._mentions = [];
  this._metadata = {};
}
```

**前端乐观更新**（RTC 模式）：
- 消息直接写入本地 YDoc，Yjs 立即通知 UI 显示
- 无需等待服务器确认（CRDT 保证最终一致性）

**WebSocket 模式**：
- `WebSocketHandler.sendMessage()` 生成 UUID，构造帧发送
- 帧格式：`{ type: 'msg', id, body, attachments, mentions, metadata, user }`

## 3. 后端处理阶段

### RTC 模式：YChat.add_message()

```python
def add_message(self, new_message: NewMessage, trigger_actions=None) -> str:
    # 1. 生成时间戳和 ID
    timestamp = time.time()
    msg_id = str(uuid.uuid4())

    # 2. 创建 Message 对象
    message = Message(**asdict(new_message), time=timestamp, id=msg_id)

    # 3. 执行 trigger actions（如 find_mentions 查找 @提及）
    if trigger_actions:
        for callback in trigger_actions:
            callback(message, self)

    # 4. 在 transaction 中按时间插入 YArray
    with self._ydoc.transaction():
        msg_dict = asdict(message, dict_factory=message_asdict_factory)
        # 找到正确位置按时间排序
        for i, existing in enumerate(self._ymessages):
            if existing.get("time", 0) > timestamp:
                self._ymessages.insert(i, msg_dict)
                break
        else:
            self._ymessages.append(msg_dict)

    # 5. 发射 SERVER_MSG_SENT 事件给观察者
    self._emit_message_event(ChatMessageAction.SERVER_MSG_SENT, message)
    return msg_id
```

### WebSocket 模式：WsChatModel.add_message()

```python
def add_message(self, new_message, trigger_actions=None) -> str:
    # 类似 RTC 模式，但额外：
    # 1. save() 写入磁盘 JSON 文件
    # 2. broadcast() 向所有 WebSocket 客户端广播
    # 3. resolve_message() 将 attachment ID 替换为完整对象
    self.save()
    self.broadcast(json.dumps({
        "type": "msg",
        "message": self.resolve_message(msg_dict)
    }))
```

### Trigger Actions

`add_message` 接受 `trigger_actions` 参数，在消息持久化前执行：

```python
# 示例：find_mentions 动作
def find_mentions(message: Message, model: BaseChatModel):
    """从消息正文中提取 @提及的用户"""
    for username in extract_mentions(message.body):
        if username not in message.mentions:
            message.mentions.append(username)
```

### 客户端时间戳校正

RTC 模式下，客户端消息可能带有 `raw_time=true`（使用客户端时间）：[^ychat-py]

```python
def _on_messages_change(self, event):
    for delta in event.delta:
        if "insert" in delta:
            for msg in delta["insert"]:
                if msg.get("raw_time"):
                    # 调度时间戳校正
                    self._ydoc.transact(lambda: self._set_timestamp(msg["id"], time.time()))
```

`_set_timestamp()` 更新为服务器时间后重新插入到正确位置。

## 4. 同步分发阶段

### RTC 模式

Yjs CRDT 自动处理同步：
1. 本地修改通过 y-protocols 发送到服务器
2. 服务器通过 jupyter_collaboration 转发给其他客户端
3. 其他客户端的 YDoc 自动更新，`_ymessages.observe` 回调触发
4. `observe_messages` 注册的观察者收到 CLIENT_MSG_RECEIVED/SERVER_MSG_SENT 事件

### WebSocket 模式

```python
# WsChatModel.broadcast()
def broadcast(self, message: str):
    for handler in list(self.handlers.values()):
        try:
            handler.write_message(message)
        except websocket.WebSocketClosedError:
            pass
```

WebSocketHandler 收到帧后：
```typescript
private _handleMessage(data: any): void {
  if (data.type === 'msg' && data.message) {
    this._messageReceived.emit(this._toMessageContent(data.message));
  }
  // ... connection, users, writing
}
```

## 5. 渲染阶段

### Message 实例化

```typescript
// AbstractChatModel.messagesInserted()
messagesInserted(index: number, contents: IMessageContent[]): void {
  const newMessages = contents.map(content => {
    const msg = new Message(content);
    // 处理堆叠逻辑
    if (this._config.stackMessages && previousSender === msg.sender.username) {
      msg.stacked = true;
    }
    return msg;
  });
  this._messages.splice(index, 0, ...newMessages);
  this.messagesUpdated.emit();
}
```

### React 渲染

`MessageRenderer` 组件订阅 `message.changed` 信号，在消息更新时重渲染：[^message-ts]

```typescript
// Message.renderedDelegate 用于异步渲染完成通知
// 例如 Markdown 渲染、代码高亮等异步操作完成后 resolve
await message.renderedDelegate.promise;
```

### 消息通知

新消息到达时，如果聊天面板不可见：[^model-ts]

```typescript
_notify(message: IMessage): void {
  // 通过 JupyterLab 命令系统发送通知
  this._commands.execute('apputils:notify', {
    message: `${sender.display_name}: ${body.slice(0, 50)}`,
    type: 'info',
    options: { autoClose: 5000 }
  });
}
```

### 未读标记

消息索引加入 `unreadMessages` 数组，UI 显示未读数标记。当用户滚动到该消息位置时标记为已读。

## 6. 编辑/删除阶段

### 编辑消息

```typescript
// 前端
model.updateMessage(messageId, { ...message, body: "编辑后的内容", edited: true });

// 后端 YChat
def update_message(self, update: Message, append: bool = False, trigger_actions=None):
    idx = self._indexes_by_id.get(update.id)
    msg = self._ymessages[idx]
    if update.body and append:
        update.body = msg.get("body", "") + update.body
    # 更新字段...
    msg["edited"] = True
    # 发射 SERVER_MSG_UPDATED 事件
```

WebSocket 模式编辑帧：
```json
{ "type": "msg", "is_update": true, "id": "<msg-id>", "body": "新内容", "edited": true }
```

### 删除消息

```typescript
model.deleteMessage(messageId);
```

WebSocket 删除帧：
```json
{ "type": "msg", "is_update": true, "id": "<msg-id>", "body": "", "deleted": true }
```

删除后消息仍保留在列表中（`deleted=true`），UI 根据 `showDeleted` 配置决定是否显示。

### Message.update() 信号

```typescript
class Message {
  update(content: IMessageContent): void {
    // 检测关键属性变化
    const needsRerender = content.body !== this._content.body
      || content.deleted !== this._content.deleted
      || content.mentions !== this._content.mentions
      || content.mime_model !== this._content.mime_model;

    Object.assign(this._content, content);

    if (needsRerender) {
      this.renderedDelegate = new PromiseDelegate();  // 重置渲染委托
    }
    this.changed.emit();  // 通知 UI 更新
  }
}
```

## 消息事件类型

ChatMessageAction 枚举定义了 4 种消息事件：[^models-py]

| 事件 | 触发时机 | 方向 |
|---|---|---|
| `CLIENT_MSG_RECEIVED` | 服务器收到客户端新消息 | 客户端→服务器 |
| `CLIENT_MSG_EDITED` | 服务器收到客户端编辑 | 客户端→服务器 |
| `SERVER_MSG_SENT` | 服务器处理并发送消息 | 服务器→广播 |
| `SERVER_MSG_UPDATED` | 服务器处理消息更新 | 服务器→广播 |

## 相关概念

- [Yjs CRDT 同步机制](/concepts/crdt-sync.md)
- [模型层架构](/concepts/model-architecture.md)
- [双传输架构](/concepts/dual-transport.md)
- [生命周期事件](/concepts/lifecycle-events.md)
- [附件系统](/concepts/attachment-system.md)
