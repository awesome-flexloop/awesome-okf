---
type: Concept
title: API Handler 开发
description: 掌握 Jupyter Server API Handler 的编写方法，包括继承体系、认证装饰器、HTTP 动词方法、请求数据获取和 JSON 响应。
tags: [api-handler, handler, tornado, authentication, http, json]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T13:10:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:10:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: handler-py
    resource: /references/handler-source.md
    title: PingHandler 请求处理器源码解析
---

## Handler 继承体系

Jupyter Server 的 API Handler 使用多重继承，标准模式是：

```python
from jupyter_server.extension.handler import ExtensionHandlerMixin
from jupyter_server.base.handlers import APIHandler

class MyHandler(ExtensionHandlerMixin, APIHandler):
    pass
```

继承链：`MyHandler → ExtensionHandlerMixin → APIHandler → JupyterHandler → tornado.web.RequestHandler`

### ExtensionHandlerMixin

提供扩展上下文：
- `self.extension_name`：当前扩展的名称
- `self.extensionapp`：关联的 ExtensionApp 实例引用
- `self.config`：扩展配置访问
- 处理扩展 URL 前缀解析

### APIHandler

API 端点基类，预置：
- `Content-Type: application/json` 响应头
- JSON 格式错误响应
- Jupyter Server 认证集成
- CORS 头处理

### 继承顺序

**ExtensionHandlerMixin 必须放在最前面**（MRO 要求），否则扩展上下文无法正确初始化。

## 认证装饰器

所有 HTTP 动词方法**必须**添加 `@tornado.web.authenticated` 装饰器：

```python
import tornado

class MyHandler(ExtensionHandlerMixin, APIHandler):
    @tornado.web.authenticated
    def get(self):
        ...

    @tornado.web.authenticated
    def post(self):
        ...
```

此装饰器确保请求经过 Jupyter Server 的身份验证。未认证请求将：
- 浏览器请求：重定向到登录页面
- API 请求（带 `Authorization` 头）：返回 403 Forbidden

模板源码注释强调："The following decorator should be present on all verb methods (head, get, post, patch, put, delete, options) to ensure only authorized user can request the Jupyter server"。

## HTTP 动词方法

Tornado 通过方法名映射 HTTP 动词，每个 Handler 可以实现需要的方法：

| 方法 | HTTP 动词 | 典型用途 |
|------|---------|---------|
| `get(self, ...)` | GET | 查询数据、获取资源 |
| `post(self, ...)` | POST | 创建资源、提交数据 |
| `put(self, ...)` | PUT | 全量更新资源 |
| `patch(self, ...)` | PATCH | 部分更新资源 |
| `delete(self, ...)` | DELETE | 删除资源 |
| `head(self, ...)` | HEAD | 获取响应头（无 body） |
| `options(self, ...)` | OPTIONS | CORS 预检请求 |

## 访问配置值

从 ExtensionApp settings 中访问配置的标准模式是使用 `@property`：

```python
class MyHandler(ExtensionHandlerMixin, APIHandler):
    @property
    def data_dir(self):
        return self.settings["data_dir"]

    @property
    def max_retries(self):
        return self.settings["max_retries"]
```

这样在 HTTP 方法中可以通过 `self.data_dir` 访问配置值，代码更简洁也便于测试 mock。

## URL 参数捕获

在 handlers 注册时使用正则表达式捕获路径参数：

```python
# extension.py
handlers = [
    (r"my-ext/items/(\w+)", ItemHandler),          # 单个捕获组
    (r"my-ext/(\w+)/(\d+)", NestedHandler),         # 多个捕获组
]
```

捕获的值作为位置参数传给 HTTP 方法：

```python
class ItemHandler(ExtensionHandlerMixin, APIHandler):
    @tornado.web.authenticated
    def get(self, item_id):
        # item_id 是 URL 中 (\w+) 捕获的字符串
        self.finish(json.dumps({"id": item_id}))
```

## 查询参数

使用 `self.get_argument()` 获取 URL 查询参数：

```python
@tornado.web.authenticated
def get(self):
    limit = int(self.get_argument("limit", default="10"))
    offset = int(self.get_argument("offset", default="0"))
    keyword = self.get_argument("q", default=None)
    # ...
```

`get_argument(name, default=..., strip=True)` 参数：
- `name`：参数名
- `default`：默认值（未提供时返回此值，不设则抛 400 错误）
- `strip`：是否去除首尾空白（默认 True）

## 请求体（POST/PUT）

处理 POST/PUT 请求的 JSON 请求体：

```python
@tornado.web.authenticated
def post(self):
    try:
        data = json.loads(self.request.body)
    except json.JSONDecodeError:
        self.set_status(400)
        self.finish(json.dumps({"error": "Invalid JSON body"}))
        return

    name = data.get("name")
    if not name:
        self.set_status(400)
        self.finish(json.dumps({"error": "name is required"}))
        return

    # 处理数据...
    result = {"id": "new-id", "name": name}
    self.set_status(201)  # Created
    self.finish(json.dumps(result))
```

注意点：
- `self.request.body` 是 bytes 类型，需要 `json.loads()` 解析
- 始终处理 JSON 解析错误
- 验证必填字段
- 使用合适的 HTTP 状态码（201 Created, 400 Bad Request 等）

## JSON 响应

所有响应通过 `self.finish()` 发送 JSON 字符串：

```python
self.finish(json.dumps({"key": "value"}))
```

`self.finish()` 完成响应并关闭连接。如果需要分块发送，可以使用 `self.write()` + `self.finish()`：

```python
self.write(json.dumps({"partial": True}))
self.write(json.dumps({"more": "data"}))
self.finish()  # 必须调用 finish
```

但对于 API 端点，通常直接 `self.finish(json.dumps(...))` 即可。

## 设置状态码

```python
self.set_status(201)  # Created
self.set_status(400)  # Bad Request
self.set_status(404)  # Not Found
self.set_status(500)  # Internal Server Error
```

常用 HTTP 状态码：

| 状态码 | 含义 | 使用场景 |
|--------|------|---------|
| 200 | OK | 成功的 GET/PUT/PATCH 请求 |
| 201 | Created | 成功的 POST 请求（创建资源） |
| 204 | No Content | 成功的 DELETE 请求（无返回内容） |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未认证 |
| 403 | Forbidden | 已认证但无权限 |
| 404 | Not Found | 资源不存在 |
| 500 | Internal Server Error | 服务器内部错误 |

## 请求头和响应头

```python
# 获取请求头
content_type = self.request.headers.get("Content-Type", "application/json")

# 设置响应头
self.set_header("X-Custom-Header", "value")
self.set_header("Cache-Control", "no-cache")
```

## 完整 CRUD Handler 示例

```python
import json
import tornado
from jupyter_server.extension.handler import ExtensionHandlerMixin
from jupyter_server.base.handlers import APIHandler


class ItemsHandler(ExtensionHandlerMixin, APIHandler):
    @property
    def data_store(self):
        return self.settings["data_store"]

    # GET /items?limit=10&offset=0
    @tornado.web.authenticated
    def get(self):
        limit = int(self.get_argument("limit", default="10"))
        items = self.data_store.list_items(limit=limit)
        self.finish(json.dumps({"items": items}))

    # POST /items
    @tornado.web.authenticated
    def post(self):
        try:
            data = json.loads(self.request.body)
        except json.JSONDecodeError:
            self.set_status(400)
            self.finish(json.dumps({"error": "Invalid JSON"}))
            return

        item = self.data_store.create_item(data)
        self.set_status(201)
        self.finish(json.dumps(item))


class ItemHandler(ExtensionHandlerMixin, APIHandler):
    @property
    def data_store(self):
        return self.settings["data_store"]

    # GET /items/{id}
    @tornado.web.authenticated
    def get(self, item_id):
        item = self.data_store.get_item(item_id)
        if item is None:
            self.set_status(404)
            self.finish(json.dumps({"error": "Not found"}))
            return
        self.finish(json.dumps(item))

    # PUT /items/{id}
    @tornado.web.authenticated
    def put(self, item_id):
        data = json.loads(self.request.body)
        item = self.data_store.update_item(item_id, data)
        if item is None:
            self.set_status(404)
            self.finish(json.dumps({"error": "Not found"}))
            return
        self.finish(json.dumps(item))

    # DELETE /items/{id}
    @tornado.web.authenticated
    def delete(self, item_id):
        success = self.data_store.delete_item(item_id)
        if not success:
            self.set_status(404)
            self.finish(json.dumps({"error": "Not found"}))
            return
        self.set_status(204)
        self.finish()
```

注册路由：

```python
handlers = [
    (r"my-ext/items", ItemsHandler),
    (r"my-ext/items/(\w+)", ItemHandler),
]
```

## 相关概念

- [ExtensionApp 开发](/concepts/04-extension-app.md)
- [测试策略](/concepts/07-testing.md)
- [PingHandler 源码解析](/references/handler-source.md)
