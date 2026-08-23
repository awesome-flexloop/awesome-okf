---
type: Reference
title: "Yjs API 信源"
description: "实时协作抽象层，定义 Yjs ABC，基于 pycrdt 提供 CRDT 文档协作的 WebSocket 和 REST 端点。"
tags: [yjs, collaboration, crdt, websocket, pycrdt, real-time]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T06:55:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: yjs_init
    resource: /external/libs/jupyter/jupyverse/api/yjs/src/jupyverse_yjs/__init__.py
    title: jupyverse_yjs/__init__.py
  - id: yjs_models
    resource: /external/libs/jupyter/jupyverse/api/yjs/src/jupyverse_yjs/models.py
    title: jupyverse_yjs/models.py
---

# Yjs API 信源

## Yjs 抽象基类

Yjs 继承 Router 和 ABC，提供实时协作的 WebSocket 和 REST 端点。

### 端点

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| WebSocket | `/api/collaboration/room/{path}` | yjs:read,write | 协作房间 WebSocket |
| PUT | `/api/collaboration/session/{path}` | contents:read | 创建/获取房间 ID |

### 抽象方法

```python
@abstractmethod
async def collaboration_room_websocket(self, path, websocket_permissions): ...

@abstractmethod
async def create_roomid(self, path, request, response, user): ...

@abstractmethod
async def get_room(self, id: str, doc: Doc | None = None): ...
```

`get_room()` 方法供其他插件（如 Kernels）获取 YRoom 实例以进行文档同步。

## 协作架构

Yjs 依赖以下组件：
- `pycrdt.Doc`：CRDT 共享文档
- `jupyverse_yrooms.YRooms`：房间管理器
- `jupyverse_yrooms.YRoomFactory`：房间工厂
- `jupyverse_file_id.FileId`：文件 ID 映射服务

WebSocket 端点使用 `auth.websocket_auth(permissions={"yjs": ["read", "write"]})` 进行认证。
