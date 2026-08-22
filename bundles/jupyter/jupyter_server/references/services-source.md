---
type: Reference
title: "其他服务模块源码信源"
description: "Sessions 会话管理、Events 事件系统、Prometheus 监控、Terminal 终端、Nbconvert 转换、Files 静态文件、View 预览"
tags: [sessions, events, prometheus, terminal, nbconvert, files, view, api]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:40:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: sessions-py
    resource: ../../../../../../external/libs/jupyter/jupyter_server/jupyter_server/services/sessions/sessionmanager.py
    title: jupyter_server/services/sessions/sessionmanager.py
  - id: events-handlers-py
    resource: ../../../../../../external/libs/jupyter/jupyter_server/jupyter_server/services/events/handlers.py
    title: jupyter_server/services/events/handlers.py
  - id: prometheus-metrics-py
    resource: ../../../../../../external/libs/jupyter/jupyter_server/jupyter_server/prometheus/metrics.py
    title: jupyter_server/prometheus/metrics.py
  - id: terminal-py
    resource: ../../../../../../external/libs/jupyter/jupyter_server/jupyter_server/terminal/terminalmanager.py
    title: jupyter_server/terminal/terminalmanager.py
  - id: files-handlers-py
    resource: ../../../../../../external/libs/jupyter/jupyter_server/jupyter_server/files/handlers.py
    title: jupyter_server/files/handlers.py
  - id: view-handlers-py
    resource: ../../../../../../external/libs/jupyter/jupyter_server/jupyter_server/view/handlers.py
    title: jupyter_server/view/handlers.py
  - id: api-handlers-py
    resource: ../../../../../../external/libs/jupyter/jupyter_server/jupyter_server/services/api/handlers.py
    title: jupyter_server/services/api/handlers.py
---

# 其他服务模块源码信源

## SessionManager (services/sessions/)

管理内核会话（Kernel ↔ Notebook 文件映射）。

**核心配置**：
- `kernel_manager`: MappingKernelManager 实例
- `contents_manager`: ContentsManager 实例

**核心方法**：
- `create_session(path, name, type, kernel_name)`: 创建会话
- `get_session(**kwargs)`: 查询会话
- `list_sessions()`: 列出所有会话
- `update_session(session_id, **kwargs)`: 更新会话
- `delete_session(session_id)`: 删除会话
- `row_to_model(row)`: 数据库行 → JSON 模型
- `start_kernel_for_session(session, kernel_name, path)`: 为会话启动内核

**会话模型**：
```python
{
    "id": "session-uuid",
    "path": "notebooks/example.ipynb",
    "name": "example.ipynb",
    "type": "notebook",
    "kernel": { ...kernel model... },
    "notebook": {"path": ..., "name": ...},
}
```

会话默认存储在内存中（SQLite 可选）。

## Events 事件系统 (services/events/)

基于 `jupyter_events` 库的结构化事件系统。

- `SubscribeWebsocket` (handlers.py L27): WebSocket 端点 `/api/events/subscribe`，实时推送事件
- `EventHandler` (handlers.py L129): REST API `/api/events/schema`，查询事件 Schema

事件 Schema 文件位于 `event_schemas/` 目录：
- `contents_service/v1.yaml`: 内容服务事件
- `kernel_actions/v1.yaml`: 内核操作事件
- `gateway_client/v1.yaml`: 网关客户端事件

## Prometheus 监控 (prometheus/)

内置 Prometheus 指标端点 `/metrics`：

| 指标 | 类型 | 说明 |
|------|------|------|
| `SERVER_INFO` | Info | 服务器信息（版本、工作目录等） |
| `SERVER_STARTED` | Counter | 服务器启动次数 |
| `SERVER_EXTENSION_INFO` | Gauge | 扩展加载状态 |
| `KERNEL_CURRENTLY_RUNNING_TOTAL` | Gauge | 当前运行内核总数 |
| `ACTIVE_DURATION` | Histogram | 请求持续时间 |
| `LAST_ACTIVITY` | Gauge | 内核最后活动时间 |
| `HTTP_REQUEST_DURATION_SECONDS` | Histogram | HTTP 请求耗时 |
| `TERMINAL_CURRENTLY_RUNNING_TOTAL` | Gauge | 当前运行终端总数 |

`log_request()` 函数在每个 HTTP 请求完成后记录指标。

## Terminal 终端 (terminal/)

- `TerminalManager`: 终端管理器（委托 jupyter_server_terminals）
- `TerminalAPIHandler` (terminal/api_handlers.py): REST API `/api/terminals`
- `TerminalHandler` (terminal/handlers.py): WebSocket `/terminals/websocket/<name>`

终端功能依赖 `jupyter_server_terminals>=0.4.4` 包。

## Nbconvert 转换 (nbconvert/)

Notebook 格式转换服务：
- `NbconvertFileHandler` (handlers.py L89): GET `/nbconvert/<format>/<path>` 转换并返回
- `NbconvertPostHandler` (handlers.py L178): POST `/nbconvert` 提交 Notebook 内容转换
- 支持格式: html, latex, pdf, markdown, rst, script, slides

## Files 静态文件 (files/)

- `FilesHandler` (handlers.py L23): GET `/files/(.*)` 服务 root_dir 下的文件
- 继承 JupyterHandler + StaticFileHandler，需要认证
- 支持隐藏文件检查、Range 请求

## View 预览 (view/)

- `ViewHandler` (handlers.py L16): GET `/view/(.*)` 在浏览器中渲染 Notebook（HTML 视图）
- 使用 nbconvert 将 Notebook 转换为 HTML 展示

## API 端点 (services/api/)

| Handler | 路由 | 说明 |
|---------|------|------|
| APISpecHandler | /api/spec.yaml | OpenAPI 规范 |
| APIStatusHandler | /api/status | 服务器状态（连接数、内核数、版本） |
| IdentityHandler | /api/me | 当前用户身份信息 |
| PathResolverHandler | /api/path | 路径解析 |
