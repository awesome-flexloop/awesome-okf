---
type: Reference
title: HTTP/WebSocket处理器源码分析
description: YDocWebSocketHandler、DocSessionHandler、TimelineHandler、UndoRedoHandler、DocForkHandler 的完整API索引
tags: [backend, websocket, http, handler]
sources:
  - id: handlers-py
    title: jupyter_server_ydoc/handlers.py
    resource: file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter-collaboration/projects/jupyter-server-ydoc/jupyter_server_ydoc/handlers.py
generated: { by: source-code-to-okf-wiki/agent, at: "2026-04-21T00:00:00Z" }
status: stable
---

# HTTP/WebSocket 处理器源码分析

## 文件定位

- **源码路径**：`projects/jupyter-server-ydoc/jupyter_server_ydoc/handlers.py`
- **包含类**：`YDocWebSocketHandler`、`DocSessionHandler`、`TimelineHandler`、`UndoRedoHandler`、`DocForkHandler`

---

## YDocWebSocketHandler

**继承**：`WebSocketHandler, JupyterHandler`

这是核心的 WebSocket 处理器，管理客户端与文档房间之间的 Yjs CRDT 同步。

### 适配 Tornado WebSocket API

由于 pycrdt 的 `WebsocketServer` 期望特定的 WebSocket 接口，`YDocWebSocketHandler` 进行了适配：

- 实现 `__aiter__`/`__anext__` 异步迭代器，从 `_message_queue` 中取出消息
- 实现 `async send(message)` 调用 `write_message(message, binary=True)`
- 实现 `async recv()` 从队列接收消息
- `max_message_size` 设为 1GB（`1024*1024*1024`）

### 生命周期

1. **`prepare()`**：在 WebSocket 握手前执行
   - 确保 WebsocketServer 已启动
   - 从 URL 路径提取 `room_id`
   - 获取或创建 `DocumentRoom`/`TransientRoom`
   - 房间级别的异步锁保证线程安全

2. **`open(room_id)`**：WebSocket 连接建立
   - DocumentRoom：检查会话兼容性（sessionId版本校验）
   - 取消房间清理任务
   - 调用 `room.initialize()` 初始化文档
   - 启动 `WebsocketServer.serve(self)` 开始消息转发
   - 发送 awareness join 事件
   - TransientRoom（如 `JupyterLab:globalAwareness`）：直接开始服务

3. **`on_message(message)`**：接收二进制消息
   - 解析消息头（var_uint）
   - `MessageType.RAW` (2)：处理自定义消息（如 `save`）
   - 其他消息（SYNC=0, AWARENESS=1）：放入 `_message_queue` 由 WebsocketServer 处理

4. **`on_close()`**：连接关闭
   - 向队列放入空字节终止迭代
   - 如果是房间最后一个客户端，调度延迟清理任务
   - 发送 awareness leave 事件

### 自定义 RAW 消息协议

| 消息 | 方向 | 格式 | 说明 |
|---|---|---|---|
| `save` | C→S | `RAW(2) + "save" + save_id(var_uint)` | 请求手动保存 |
| save回复 | S→C | `RAW(2) + JSON({type:"save", responseTo, status})` | 保存结果（success/skipped/failed） |
| `conflict` | S→C | `RAW(2) + JSON({type:"conflict"})` | 文档冲突通知 |

### 会话兼容性检查

`open()` 中通过 `check_session_compatibility()` 验证客户端 sessionId：

- **unknown_session**：sessionId不在记录中 → 关闭连接（code 1003），要求重载
- **version_mismatch**：协作包版本或文档版本不匹配 → 关闭连接，要求重载
- **兼容**：接受旧session，无需重载

### 错误码映射

| HTTP状态码 | WebSocket关闭码 | 含义 |
|---|---|---|
| 404 | 4404 | 文件不存在 |
| 400 | 4400 | 错误请求 |
| 500 | 4500 | 服务器内部错误 |
| 初始化错误 | 1003 | `{reason: "initialization_error", reloadable: false}` |

### 房间清理（_clean_room）

```python
async def _clean_room(self):
    await asyncio.sleep(self._cleanup_delay)  # 默认60秒
    async with self._room_lock(self._room_id):
        await self._websocket_server.delete_room(room=self.room)
        # 如果文件加载器无订阅，移除它
        if file.number_of_subscriptions == 0:
            await self._file_loaders.remove(file_id)
        del self._room_locks[self._room_id]
```

---

## DocSessionHandler

**继承**：`APIHandler`
**路由**：`PUT /api/collaboration/session/(.*)`

为指定文档创建或返回现有会话信息：

**请求体**：
```json
{ "format": "text", "type": "notebook" }
```

**响应**：
```json
{
  "format": "text",
  "type": "notebook",
  "fileId": "<uuid>",
  "sessionId": "<server-session-uuid>"
}
```

- 200：文件已索引，返回现有 fileId
- 201：新创建索引
- 404：文件不存在

---

## TimelineHandler

**继承**：`APIHandler`
**路由**：`GET /api/collaboration/timeline/(.*)?format=...&type=...`

为时间线滑块提供文档历史版本：

1. 创建独立的 fork YDoc
2. 从 YStore 逐次 apply updates，记录 UndoManager 栈增长对应的时间戳
3. 返回 `{ roomId, timestamps, forkRoom, sessionId }`
4. forkRoom 是一个临时房间ID，客户端可连接查看历史版本

---

## UndoRedoHandler

**继承**：`APIHandler`
**路由**：`PUT /api/collaboration/undoredo/(.*)?action=...&steps=...&forkRoom=...`

在时间线 fork 文档上执行撤销/重做/恢复操作：

| action | 说明 |
|---|---|
| `undo` | 撤销N步 |
| `redo` | 重做N步 |
| `restore` | 将 fork 文档恢复为主文档（清理UndoManager） |

---

## DocForkHandler

**继承**：`APIHandler`
**路由**：
- `GET /api/collaboration/fork/(root_roomid)` — 获取root文档的所有fork
- `PUT /api/collaboration/fork/(root_roomid)` — 创建fork
- `DELETE /api/collaboration/fork/(fork_roomid)?merge=true|false` — 删除fork（可选合并）

**创建fork请求体**：
```json
{
  "synchronize": false,
  "title": "实验分支",
  "description": "尝试新的分析方法"
}
```

**synchronize=true** 时，root文档的变更会通过 `observe` 实时同步到fork。

**全局状态**：
- `FORK_DOCUMENTS: dict[str, YDoc]` — fork文档实例映射
- `FORK_ROOMS: dict[str, dict]` — fork元信息（root_roomid, synchronize, title, description）

## 事件发射

所有处理器通过 `event_logger.emit()` 发射三类事件：

| Schema URI | 事件类型 |
|---|---|
| `JUPYTER_COLLABORATION_EVENTS_URI` | session事件（initialize/load/save/clean/overwrite） |
| `JUPYTER_COLLABORATION_AWARENESS_EVENTS_URI` | awareness事件（join/leave） |
| `JUPYTER_COLLABORATION_FORK_EVENTS_URI` | fork事件（create/delete） |

## 相关概念

- [文档房间管理](../concepts/03-document-room.md)
- [WebSocket通信协议](../concepts/05-websocket-protocol.md)
- [文档分叉与时间线](../concepts/08-fork-timeline.md)
