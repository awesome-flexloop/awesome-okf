---
type: Concept
title: REST API 处理器
description: 终端 REST API 详解——TerminalRootHandler 和 TerminalHandler 的路由、认证、cwd 路径解析、HTTP 方法语义
tags: [jupyter, terminals, REST, API, TerminalRootHandler, TerminalHandler, HTTP]
generated: { by: "reference_agent/trae-glm", at: "2026-08-22T06:47:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T07:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: jst-source
    resource: /references/jupyter-server-terminals-source.md
---

# REST API 处理器

## API 路由总览

jupyter_server_terminals 注册了两个 REST 端点，定义在 [api_handlers.py](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_terminals/jupyter_server_terminals/api_handlers.py) 中：

```python
default_handlers: list[tuple[str, type[Any]]] = [
    (r"/api/terminals", TerminalRootHandler),
    (r"/api/terminals/(\w+)", TerminalHandler),
]
```

| 方法 | 路径 | Handler | 说明 |
|------|------|---------|------|
| GET | `/api/terminals` | TerminalRootHandler | 获取所有终端列表 |
| POST | `/api/terminals` | TerminalRootHandler | 创建新终端 |
| GET | `/api/terminals/{name}` | TerminalHandler | 获取指定终端信息 |
| DELETE | `/api/terminals/{name}` | TerminalHandler | 删除指定终端 |

这些路由通过 `initialize_handlers()` 注册到 Jupyter Server 的 Tornado Web Application。

## 基类与认证

所有 API Handler 继承自一个公共基类：

```python
class TerminalAPIHandler(APIHandler):
    """The base terminal handler."""
    auth_resource = "terminals"
```

- `APIHandler` 来自 `jupyter_server.base.handlers`，提供 Jupyter Server 的基础 API 功能
- `auth_resource = "terminals"` 将所有终端 API 操作标记为 `terminals` 资源，供授权系统使用

每个处理方法都使用两个装饰器：
- `@web.authenticated`：Tornado 内置认证装饰器，确保用户已登录
- `@authorized`：来自 `jupyter_server.auth.decorator`，确保用户有对应资源的操作权限

授权动作映射：
- HTTP GET → `"read"` 动作
- HTTP POST → `"write"` 动作
- HTTP DELETE → `"write"` 动作
- WebSocket → `"execute"` 动作

## TerminalsMixin 混入类

```python
class TerminalsMixin(ExtensionHandlerMixin):
    """An extension mixin for terminals."""

    @property
    def terminal_manager(self) -> TerminalManager:
        return self.settings["terminal_manager"]
```

`TerminalsMixin` 是一个轻量 Mixin，通过 `self.settings["terminal_manager"]` 提供对 TerminalManager 实例的便捷访问。REST Handler 和 WebSocket Handler 都继承了这个 Mixin。

## TerminalRootHandler

`TerminalRootHandler` 处理终端集合级别的操作（列表和创建）：

```python
class TerminalRootHandler(TerminalsMixin, TerminalAPIHandler):
    """The root terminal API handler."""
```

MRO：`TerminalRootHandler → TerminalsMixin → TerminalAPIHandler → APIHandler`

### GET /api/terminals — 获取终端列表

```python
@web.authenticated
@authorized
def get(self) -> None:
    """Get the list of terminals."""
    models = self.terminal_manager.list()
    self.finish(json.dumps(models))
```

调用 `terminal_manager.list()` 获取所有终端模型，序列化为 JSON 数组返回。响应示例：

```json
[
    {"name": "1", "last_activity": "2026-08-22T06:00:00.000000Z"},
    {"name": "2", "last_activity": "2026-08-22T06:05:00.000000Z"}
]
```

### POST /api/terminals — 创建新终端

```python
@web.authenticated
@authorized
def post(self) -> None:
    """POST /terminals creates a new terminal and redirects to it"""
```

创建新终端的流程：

1. **解析请求体**：`data = self.get_json_body() or {}`,获取 JSON 数据
2. **处理 cwd 参数**（工作目录）：
   - 如果请求体包含 `"cwd"`，将其解析为 `Path` 对象
   - 如果是相对路径，尝试相对于 `server_root_dir` 解析
   - 如果路径不存在，**静默删除** `cwd` 字段（使用默认工作目录），并记录 debug 日志
   - 如果路径存在，解析为绝对路径
3. **创建终端**：`model = self.terminal_manager.create(**data)`，将处理后的参数透传给 TerminalManager
4. **返回响应**：`self.finish(json.dumps(model))`，返回新创建的终端模型

请求示例：

```bash
# 创建默认终端
curl -X POST http://localhost:8888/api/terminals

# 在指定目录创建终端
curl -X POST http://localhost:8888/api/terminals \
  -H "Content-Type: application/json" \
  -d '{"cwd": "/home/user/projects"}'
```

响应示例：

```json
{"name": "1", "last_activity": "2026-08-22T06:00:00.000000Z"}
```

### cwd 路径解析逻辑

cwd 参数的解析逻辑值得注意，它处理三种情况：

| cwd 值 | 处理方式 |
|--------|---------|
| 绝对路径，存在 | 直接使用 `cwd.resolve()` |
| 相对路径，相对于 server_root_dir 存在 | 拼接为 `server_root_dir / cwd`，解析绝对路径 |
| 路径不存在 | 删除 cwd 参数，终端使用默认工作目录 |

这确保了即使请求无效路径，也不会报错，而是优雅降级到默认目录。

## TerminalHandler

`TerminalHandler` 处理单个终端的操作（查询和删除）：

```python
class TerminalHandler(TerminalsMixin, TerminalAPIHandler):
    """A handler for a specific terminal."""
    SUPPORTED_METHODS = ("GET", "DELETE", "OPTIONS")
```

注意 `SUPPORTED_METHODS` 显式限制只支持 GET、DELETE、OPTIONS，不支持 PUT/POST/PATCH。

### GET /api/terminals/{name} — 获取终端信息

```python
@web.authenticated
@authorized
def get(self, name: str) -> None:
    """Get a terminal by name."""
    model = self.terminal_manager.get(name)
    self.finish(json.dumps(model))
```

URL 中的 `(\w+)` 捕获组作为 `name` 参数传入。如果终端不存在，`terminal_manager.get()` → `get_terminal_model()` → `_check_terminal()` 会抛出 `HTTPError(404)`。

### DELETE /api/terminals/{name} — 删除终端

```python
@web.authenticated
@authorized
async def delete(self, name: str) -> None:
    """Remove a terminal by name."""
    await self.terminal_manager.terminate(name, force=True)
    self.set_status(204)
    self.finish()
```

异步方法，调用 `terminal_manager.terminate(name, force=True)` 强制终止终端进程，返回 `204 No Content`（无响应体）。

## OpenAPI 规范

项目包含 `rest-api.yml` OpenAPI 3.0.1 规范文件，完整定义了 API 的 schema：

- **Terminal 模型**：`name`（string, required）+ `last_activity`（ISO 8601 UTC timestamp string）
- **错误响应**：403 Forbidden（未授权）、404 Not Found（终端不存在）
- **DELETE 成功响应**：204 No Content

## 认证与授权流程

每个 API 请求的完整安全检查链：

```
请求到达
  │
  ├─ @web.authenticated ─── 未登录 → 403
  │
  ├─ @authorized ─── 无权限 → 403
  │   └─ authorizer.is_authorized(handler, user, action, "terminals")
  │
  ├─ 业务逻辑 ─── 终端不存在 → 404
  │
  └─ 返回 JSON 响应
```

## 相关概念

- [TerminalManager 终端管理器](/concepts/03-terminal-manager.md)
- [WebSocket 处理器](/concepts/05-websocket.md)
- [TerminalsExtensionApp 扩展应用](/concepts/02-extension-app.md)
- [基础终端操作示例](/examples/basic-operations.md)
- [配置自动清理与指定工作目录](/examples/culler-and-cwd.md)
- [jupyter_server_terminals 源码信源登记](/references/jupyter-server-terminals-source.md)

[^jst-source]: jupyter_server_terminals 源码信源，见 [jupyter-server-terminals-source.md](/references/jupyter-server-terminals-source.md)。
