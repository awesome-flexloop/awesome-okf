---
type: Concept
title: "会话管理"
description: "Session 关联 Notebook 文件与内核实例的映射、会话 REST API 与多前端支持"
tags: [sessions, kernel-session, notebook-kernel-mapping, websocket, multi-frontend]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:55:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: services
    resource: /references/services-source.md
    title: 其他服务模块源码信源
---

# 会话管理

Session（会话）是连接 Notebook 文件与内核实例的桥梁。一个 Session 将一个文件路径（path）、一个文件类型（type）和一个内核（kernel）绑定在一起，确保打开同一文件的多个前端能够共享同一个内核。

## 会话模型

```json
{
  "id": "session-uuid",
  "path": "notebooks/example.ipynb",
  "name": "example.ipynb",
  "type": "notebook",
  "kernel": {
    "id": "kernel-uuid",
    "name": "python3",
    "last_activity": "2024-01-01T12:00:00Z",
    "execution_state": "idle",
    "connections": 1
  },
  "notebook": {
    "path": "notebooks/example.ipynb",
    "name": "example.ipynb"
  }
}
```

| 字段 | 说明 |
|------|------|
| `id` | 会话唯一 ID |
| `path` | 关联的文件路径 |
| `name` | 文件名 |
| `type` | 文件类型（`notebook`/`file`/`console`） |
| `kernel` | 关联的内核信息（内核模型） |
| `notebook` | Notebook 文件信息（向后兼容字段） |

## REST API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/sessions` | 列出所有会话 |
| POST | `/api/sessions` | 创建新会话（启动内核） |
| GET | `/api/sessions/<session_id>` | 获取会话信息 |
| PATCH | `/api/sessions/<session_id>` | 更新会话（重命名文件等） |
| DELETE | `/api/sessions/<session_id>` | 删除会话（关闭内核） |

### API 示例

```bash
# 列出所有会话
curl http://localhost:8888/api/sessions?token=xxx

# 创建新会话（打开 Notebook）
curl -X POST http://localhost:8888/api/sessions?token=xxx \
  -H "Content-Type: application/json" \
  -d '{
    "path": "notebooks/example.ipynb",
    "type": "notebook",
    "name": "example.ipynb",
    "kernel": {"name": "python3"}
  }'

# 获取会话信息
curl http://localhost:8888/api/sessions/<session_id>?token=xxx

# 更新会话（重命名文件）
curl -X PATCH http://localhost:8888/api/sessions/<session_id>?token=xxx \
  -H "Content-Type: application/json" \
  -d '{"path": "notebooks/renamed.ipynb", "name": "renamed.ipynb"}'

# 删除会话（关闭内核）
curl -X DELETE http://localhost:8888/api/sessions/<session_id>?token=xxx
```

## SessionManager 核心逻辑

### 创建会话

```python
async def create_session(path=None, name=None, type=None, kernel_name=None):
    # 1. 如果 path+type 已有会话，返回现有会话（避免重复内核）
    # 2. 检查文件是否存在（path 必须是已存在的文件/Notebook）
    # 3. 启动新内核
    # 4. 注册会话映射
    # 5. 返回会话模型
```

关键点：**同一 path+type 组合只能有一个会话**。如果尝试为已打开的文件创建新会话，会返回现有会话而非启动新内核。这保证了多标签/多前端打开同一 Notebook 时共享内核。

### 删除会话

1. 查找对应内核
2. 关闭内核（发送 shutdown 请求）
3. 移除会话记录

### 路径跟踪

SessionManager 追踪文件重命名操作：当文件被重命名时（通过 ContentsManager），所有指向该文件的会话路径自动更新。

## 多前端共享内核

Session 的设计核心是支持**多前端**（JupyterLab、Notebook Classic、Voilà、第三方前端）共享同一个内核：

```
前端 A (JupyterLab) ──┐
                      ├── WebSocket ──┐
前端 B (Classic)  ────┤               │
                      │          ZMQ Channels ──── Kernel
前端 C (Voilà)   ─────┘               │
                                      │
                                 Session 映射
                                 (path ↔ kernel)
```

同一文件路径的会话共享同一个内核，这意味着：
- 在 A 中定义的变量在 B 中可见
- 在 B 中执行的代码影响 A 的状态
- 任何一个前端关闭都不会立即关闭内核（需要所有连接断开或显式关闭会话）

## Terminal 终端管理

终端功能由 `TerminalManager` 和 `TerminalsAPIHandler` 管理：

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/terminals` | 列出终端 |
| POST | `/api/terminals` | 创建终端 |
| GET | `/api/terminals/<name>` | 获取终端信息 |
| DELETE | `/api/terminals/<name>` | 删除终端 |
| WebSocket | `/api/terminals/websocket/<name>` | 终端 WebSocket |

终端通过 `ptyprocess`（macOS/Linux）或 `pywin32`（Windows）创建伪终端，通过 WebSocket 进行数据交互。

配置项：`ServerApp.terminals_enabled` 控制是否启用终端功能。

## NbConvert 转换服务

`NbconvertHandler` 提供 Notebook 格式转换能力：

| 端点 | 说明 |
|------|------|
| POST `/api/nbconvert` | 转换 Notebook 格式 |
| GET `/nbconvert/<format>/<path>` | 将 Notebook 转换为指定格式并下载 |

支持格式：html、pdf、latex、markdown、rst、script、slides 等（通过 nbconvert 后端）。

## 其他 API 端点

### `/api/status`

服务器状态端点（兼容 Jupyter Server 早期版本），返回服务器版本、连接状态等。

### `/api/me`

返回当前认证用户信息（v2.0 IdentityProvider 提供）：

```json
{
  "username": "user",
  "name": "User Name",
  "display_name": "User",
  "initials": "U",
  "color": "blue"
}
```

### `/api/events`

事件订阅端点（Server-Sent Events），用于实时推送服务器事件。

### `/api/metrics`

Prometheus 指标端点（需配置 `ServerApp.prometheus_enabled=True`），暴露内核数量、请求延迟等监控指标。

## 相关概念

- [内核管理](08-kernel-management.md) — 内核生命周期与进程管理
- [WebSocket 通信](11-websocket-communication.md) — 会话与内核的实时消息通道
- [认证授权系统](05-auth-system.md) — /api/me 端点与身份模型
