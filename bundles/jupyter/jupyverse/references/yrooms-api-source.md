---
type: Reference
title: "YRooms API 信源"
description: "Yjs 协作房间管理，定义 YRoom ABC 和 YRooms 管理器，基于 pycrdt 实现 CRDT 文档同步和客户端消息广播。"
tags: [yrooms, collaboration-room, crdt-sync, client-broadcast, pycrdt]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T06:55:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: yrooms_init
    resource: /external/libs/jupyter/jupyverse/api/yrooms/src/jupyverse_yrooms/__init__.py
    title: jupyverse_yrooms/__init__.py
  - id: yrooms_server
    resource: /external/libs/jupyter/jupyverse/api/yrooms/src/jupyverse_yrooms/server.py
    title: jupyverse_yrooms/server.py
  - id: yrooms_channel
    resource: /external/libs/jupyter/jupyverse/api/yrooms/src/jupyverse_yrooms/channel.py
    title: jupyverse_yrooms/channel.py
---

# YRooms API 信源

## YRoom 抽象基类

YRoom 表示一个协作房间，管理共享文档和客户端连接。

### 核心属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `id` | str | 房间 ID |
| `doc` | pycrdt.Doc | CRDT 共享文档 |
| `clients` | set[AsyncChannel] | 已连接的客户端集合 |
| `synced` | bool | 是否正在同步 |
| `jupyter_ydoc` | YBaseDoc | Jupyter 特定的 YDoc 包装 |
| `task_group` | TaskGroup | 后台任务组 |

### 核心方法

| 方法 | 说明 |
|------|------|
| `run(*, task_status)` | 后台同步任务：监听 doc 事件，广播 update 消息到所有客户端 |
| `serve(client)` | 处理客户端连接：发送同步消息→接收处理消息→清理断开 |
| `handle_message(message, client)` | 抽象方法，处理来自客户端的消息（子类实现） |
| `sync()` | 如果未同步，启动同步任务 |
| `close()` | 设置关闭事件，清理房间 |

### 同步流程

1. 客户端连接 → `serve()` 添加客户端
2. 新事务中创建 sync_message → 发送给客户端
3. 后台 `run()` 任务监听 doc events
4. doc 更新时创建 update_message → 广播给所有客户端
5. 客户端断开 → `_remove_client()` → 无客户端时自动 close()

### 消息类型

使用 pycrdt 的消息创建函数：
- `create_sync_message(doc)`：创建初始同步消息（发送文档状态）
- `create_update_message(update)`：创建增量更新消息

## YRooms 管理器

YRooms 管理所有 YRoom 实例的生命周期。

### 核心方法

```python
class YRooms(AsyncContextManagerMixin):
    async def get_room(self, id: str, **kwargs) -> YRoom:
        # 带锁的房间获取：不存在则创建，存在则返回
        async with self._lock(id):
            if id not in self._rooms:
                room = await self._task_group.start(partial(self._create_room, id, **kwargs))
                self._rooms[id] = room
            return self._rooms[id]

    async def serve(self, channel: AsyncChannel, **kwargs):
        room = await self.get_room(channel.id, **kwargs)
        await room.serve(channel)
```

### 房间生命周期

1. `get_room(id)` 检查房间是否存在
2. 不存在则通过 `_create_room()` 创建，启动 room 的后台任务
3. 房间关闭后自动从 `_rooms` 字典中删除
4. 使用 `ResourceLock` 确保并发安全

## AsyncChannel / AsyncWebSocket

channel.py 定义了异步通信通道抽象，封装 WebSocket 连接。
