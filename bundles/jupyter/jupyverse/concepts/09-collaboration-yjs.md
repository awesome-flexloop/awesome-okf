---
type: Concept
title: "协作编辑 Yjs"
description: "Yjs 模块基于 pycrdt 实现 CRDT 实时协作，通过 WebSocket 广播文档更新，支持多用户同时编辑 Notebook 和文本文件，提供房间管理和文档持久化。"
tags: [yjs, collaboration, crdt, pycrdt, websocket, real-time, multi-user, awareness]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T06:55:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: yjs_api
    resource: /references/yjs-api-source.md
    title: Yjs API 信源
  - id: yrooms_api
    resource: /references/yrooms-api-source.md
    title: YRooms API 信源
---

# 协作编辑 Yjs

Jupyverse 通过 Yjs 模块提供基于 CRDT（Conflict-free Replicated Data Type）的实时协作编辑功能，允许多个用户同时编辑同一 Notebook 或文本文件。

## CRDT 基础

CRDT（无冲突复制数据类型）是一种特殊的数据结构，允许多个副本独立更新，然后自动合并变更，无需中心化协调。Jupyverse 使用 `pycrdt`（Yjs 的 Python 绑定）实现服务端 CRDT 文档管理。

核心概念：
- **Doc**：CRDT 文档容器，包含多个共享类型（YMap、YArray、YText）
- **Update（更新）**：文档变更的二进制编码，可以在副本间传播
- **Awareness（感知）**：用户在线状态信息（光标位置、用户名、颜色等）
- **Room（房间）**：一个文档的协作空间，包含文档状态和所有连接的用户

## Yjs 模块架构

```
Yjs (ABC, Router)
 ├── WebSocket 端点: /api/collaboration/room/{room_id}
 ├── 端点: /api/collaboration/session/{path}（创建/获取会话）
 └── 依赖:
     ├── Auth (WebSocket 认证)
     ├── Contents (文件读写)
     ├── FileId (路径↔房间ID映射)
     └── YRooms (房间管理器)

YRooms (ABC)
 ├── YRoom 实例管理
 ├── 文档加载/持久化钩子
 └── 依赖:
     └── YStore (文档存储，如 SQLite)

YRoom
 ├── doc: pycrdt.Doc (CRDT 文档)
 ├── background_tasks: 文档异步写入
 ├── websockets: 当前连接的 WebSocket 列表
 ├── ysrv: YDocServer (更新同步逻辑)
 └── awareness: Awareness 实例
```

## WebSocket 通信

协作通过 WebSocket 端点进行：

```
WebSocket /api/collaboration/room/{room_id}
```

### 消息格式

Yjs WebSocket 协议使用二进制消息，第一个字节标识消息类型：

| 类型 | 方向 | 说明 |
|------|------|------|
| `0` (SYNC) | 双向 | 文档同步（sync step 1/2, update） |
| `1` (AWARENESS) | 双向 | 用户感知信息（位置、名称、颜色） |

### 连接建立流程

1. 前端打开 WebSocket 连接，携带认证信息（token）
2. Yjs 模块通过 `auth.websocket_auth()` 验证用户权限
3. 获取或创建对应文档的 YRoom
4. 前端发送 sync step 1（本地文档状态向量）
5. 服务端回复 sync step 2（缺失的更新）
6. 双向开始传播实时更新

### Awareness（感知信息）

Awareness 消息包含用户的在线状态：
- 用户名和显示名
- 用户颜色和头像
- 当前光标位置
- 选中内容范围
- 用户是否活跃

新用户加入时，服务端广播其 awareness 给所有已连接用户；用户断开时广播移除消息。

## YRoom（协作房间）

```python
class YRoom:
    def __init__(self, ydoc: Doc, update_timeout: float = 0.001):
        self.ydoc = ydoc
        self.background_tasks = set()
        self.websockets: list[Any] = []
        self.ysrv = YDocServer(ydoc)
        self.awareness = self.ysrv.awareness
        self._update_timeout = update_timeout
```

### 文档持久化

YRoom 配置了更新观察器，当文档发生变化时延迟批量写入存储：

```python
self.ydoc.observe(self._on_update)
```

`_on_update` 在 `update_timeout`（默认 1ms）后触发一次写入，将更新序列化到后端存储（如 SQLite 的 `fps-ystore-sqlite`）。

### 文件ID映射

协作使用 `room_id`（不是文件路径）标识文档，FileId 服务负责路径和房间 ID 之间的映射。这允许文件被重命名而不影响正在进行的协作会话。

## 会话管理

`/api/collaboration/session/{path}` 端点用于创建或获取协作会话：

- **POST**：为指定路径创建协作会话（如果不存在），返回 `format`、`fileId`（room_id）、`sessionId`
- **PATCH**：重命名文件时更新路径映射
- **DELETE**：结束协作会话，清理房间

```json
// 响应示例
{
  "format": "json",
  "fileId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "sessionId": "f9e8d7c6-b5a4-3210-fedc-ba0987654321"
}
```

## YStore（文档存储）

YStore 是文档持久化的抽象接口，默认实现为 `fps-ystore-sqlite`（SQLite 存储）。YStore 负责：
- 初始化文档存储
- 写入文档更新（增量）
- 读取文档状态（初始化新房间时加载历史）

## 协作模式启用

启动时通过 `--set frontend.collaborative=true` 启用协作：

```bash
pip install "jupyverse[jupyterlab,auth,yjs,noauth]"
jupyverse --set "frontend.collaborative=true"
```

启用后：
1. PageConfig 中 `collaborative` 设为 `true`
2. 前端加载协作扩展
3. 打开文件时通过 `/api/collaboration/session/` 创建会话
4. 通过 WebSocket 连接到 `/api/collaboration/room/` 进行实时同步
5. 用户光标和选区实时显示
6. 文档变更自动同步到所有连接者

## 与内核的集成

Kernels 模块通过 `require_yjs` 配置与 Yjs 集成：
- 内核执行前确保文档 CRDT 状态已同步
- 代码单元格的输出广播给所有协作用户
- 共享 Notebook 的执行状态

## 相关概念

- [内核管理](07-kernel-management.md) — 内核与协作的集成
- [Lab 前端服务](08-lab-frontend.md) — PageConfig 中的 collaborative 配置
- [认证授权系统](05-auth-system.md) — WebSocket 连接认证
- [FPS 模块系统](03-fps-module-system.md) — YjsModule 的依赖关系
