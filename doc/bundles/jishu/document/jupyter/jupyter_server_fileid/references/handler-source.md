---
okf_version: "0.2"
type: reference
title: "handler.py 源码解析"
description: "HTTP API 处理器：BaseHandler 基类、FileIDHandler（路径查ID）和 FilePathHandler（ID查路径）两个 REST 端点。"
tags: [jupyter, fileid, handler, tornado, rest-api, source]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T14:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: handler-py
    resource: "../../../../../external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/handler.py"
    title: "jupyter_server_fileid/handler.py"
---

# handler.py 源码解析

`handler.py` 约 65 行，实现了两个 HTTP API 端点，基于 Jupyter Server 的 `APIHandler` 和 Tornado Web 框架。

## 模块结构

```
handler.py
├── BaseHandler(APIHandler)       # 处理器基类
│   ├── auth_resource = "contents"
│   └── file_id_manager property  # 从 settings 获取管理器实例
├── FileIDHandler(BaseHandler)    # GET /api/fileid/id?path=...
│   └── get()                     # 路径 → 文件 ID
└── FilePathHandler(BaseHandler)  # GET /api/fileid/path?id=...
    └── get()                     # 文件 ID → 路径
```

## BaseHandler 基类

```python
class BaseHandler(APIHandler):
    auth_resource = "contents"

    @property
    def file_id_manager(self) -> BaseFileIdManager:
        manager = self.settings.get("file_id_manager")
        assert isinstance(manager, BaseFileIdManager)
        return manager
```

- 继承 `jupyter_server.base.handlers.APIHandler`
- `auth_resource = "contents"` 表示与 contents 服务共享权限
- `file_id_manager` 属性从 Tornado `settings` 字典中获取由 ExtensionApp 注入的管理器实例
- 使用 `assert isinstance` 做运行时类型检查

## FileIDHandler — 路径查 ID

**路由**: `GET /api/fileid/id`

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `path` | string | 是 | 文件的 API 路径（相对 root_dir，正斜杠分隔） |

**响应** (200 OK):
```json
{"id": "<uuid>", "path": "<requested-path>"}
```

**错误响应**:
| HTTP 状态码 | 触发条件 |
|------------|---------|
| 400 | 缺少 `path` 参数 |
| 404 | 路径未找到（`get_id()` 返回 None） |

**认证**: 使用 `@web.authenticated` 和 `@authorized` 双重装饰器。

核心逻辑：
```python
def get(self) -> None:
    path = self.get_argument("path")       # 抛出 MissingArgumentError → 400
    id = self.file_id_manager.get_id(path)
    if id is None:
        raise web.HTTPError(404, ...)      # 未找到 → 404
    self.write(json_encode({"id": id, "path": path}))
```

## FilePathHandler — ID 查路径

**路由**: `GET /api/fileid/path`

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 文件 ID（UUID 字符串） |

**响应** (200 OK):
```json
{"id": "<requested-id>", "path": "<api-path>"}
```

**错误响应**:
| HTTP 状态码 | 触发条件 |
|------------|---------|
| 400 | 缺少 `id` 参数 |
| 404 | ID 未找到（`get_path()` 返回 None） |

核心逻辑与 FileIDHandler 对称：
```python
def get(self) -> None:
    id = self.get_argument("id")           # 抛出 MissingArgumentError → 400
    path = self.file_id_manager.get_path(id)
    if path is None:
        raise web.HTTPError(404, ...)      # 未找到 → 404
    self.write(json_encode({"id": id, "path": path}))
```

## 设计特点

1. **只读 API**：两个端点都是 GET 请求，不提供写操作。文件索引的增删改由事件监听器自动触发
2. **对称设计**：两个 handler 结构完全对称（path↔id 双向查询），错误处理模式一致
3. **认证复用**：复用 Jupyter Server 内置的认证授权体系，不自行实现
4. **JSON 响应**：使用 `tornado.escape.json_encode` 序列化，响应包含请求参数便于客户端关联

---

**相关文档：**
- [manager.py 源码解析](manager-source.md) — 核心管理器实现
- [REST API 端点](../concepts/06-http-api.md) — API 用法详解
