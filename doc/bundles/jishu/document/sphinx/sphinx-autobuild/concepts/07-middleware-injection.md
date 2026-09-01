---
type: Concept
title: 中间件注入机制
description: JavascriptInjectorMiddleware 的 ASGI 中间件实现——WebSocket 脚本注入原理、HTTP 响应拦截、Content-Length 修正、Cache-Control 处理
tags: [sphinx-autobuild, middleware, ASGI, Starlette, hot-reload, javascript-injection]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T14:50:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: sphinx-autobuild-source
    resource: /references/sphinx-autobuild-source.md
    title: sphinx-autobuild 源码信源登记
---

# 中间件注入机制

## 为什么需要中间件注入？

sphinx-autobuild 的热重载功能依赖于浏览器与服务器之间的 WebSocket 连接。要让浏览器在文档重建完成后自动刷新，需要在每个 HTML 页面中插入一段 JavaScript 代码，用于建立 WebSocket 连接并响应重载信号。

传统做法要求用户修改 Sphinx 主题模板，在 `<head>` 或 `<body>` 中手动添加脚本。这种方式侵入性强：需要主题支持、需要额外配置、对非 HTML 构建器无效。

sphinx-autobuild 采用了一种**非侵入式**方案：通过 ASGI 中间件在 HTTP 响应层面动态注入脚本，完全不需要修改 Sphinx 的任何配置或模板。

## 注入的 JavaScript 代码

`web_socket_script(ws_url)` 函数生成注入的脚本：

```python
def web_socket_script(ws_url: str) -> str:
    return f"""
<script>
const ws = new WebSocket("ws://{ws_url}/websocket-reload");
ws.onmessage = () => window.location.reload();
</script>
"""
```

这段脚本非常简洁：
1. 创建一个 WebSocket 连接到 `ws://{host}:{port}/websocket-reload`
2. 监听 `onmessage` 事件——收到任何消息就调用 `window.location.reload()` 刷新页面

服务器在构建完成后发送的消息就是字符串 `"refresh"`，但客户端代码并不检查消息内容——任何消息都触发刷新。这种设计简化了协议，因为服务器只会在构建完成时发送消息。

## JavascriptInjectorMiddleware 类

`JavascriptInjectorMiddleware` 位于 `sphinx_autobuild/middleware.py`，是一个标准的 Starlette ASGI 中间件。

### 初始化

```python
class JavascriptInjectorMiddleware:
    def __init__(self, app: ASGIApp, ws_url: str) -> None:
        self.app = app
        self.script = web_socket_script(ws_url).encode("utf-8")
```

- `app`：下游 ASGI 应用（即 StaticFiles）
- `ws_url`：WebSocket 服务器地址（`host:port` 格式）
- `self.script`：预编码为 UTF-8 字节的脚本标签，避免每次请求都编码

### ASGI 调用接口

```python
async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
    add_script = False
    if scope["type"] != "http":
        await self.app(scope, receive, send)
        return

    async def send_wrapper(message: Message) -> None:
        nonlocal add_script
        if message["type"] == "http.response.start":
            headers = MutableHeaders(scope=message)
            if headers.get("Content-Type", "").startswith("text/html"):
                add_script = True
                if "Content-Length" in headers:
                    length = int(headers["Content-Length"]) + len(self.script)
                    headers["Content-Length"] = str(length)
            headers["Cache-Control"] = "no-cache"
        elif message["type"] == "http.response.body":
            request_complete = not message.get("more_body", False)
            if add_script and request_complete:
                message["body"] += self.script
        await send(message)

    await self.app(scope, receive, send_wrapper)
```

## 响应拦截流程

中间件通过包装 `send` 回调来拦截和修改响应。ASGI 协议中，HTTP 响应分为两类消息：

1. **`http.response.start`**：响应头，包含状态码和 headers
2. **`http.response.body`**：响应体，可能分块发送（`more_body=True` 表示后续还有数据）

### 步骤1：非 HTTP 请求快速透传

```python
if scope["type"] != "http":
    await self.app(scope, receive, send)
    return
```

WebSocket 请求（`scope["type"] == "websocket"`）不经过中间件处理，直接透传给下游应用。这确保 `/websocket-reload` 的 WebSocket 连接不受影响。

### 步骤2：拦截响应头（http.response.start）

当收到响应头消息时：

```python
if message["type"] == "http.response.start":
    headers = MutableHeaders(scope=message)
    if headers.get("Content-Type", "").startswith("text/html"):
        add_script = True
        if "Content-Length" in headers:
            length = int(headers["Content-Length"]) + len(self.script)
            headers["Content-Length"] = str(length)
    headers["Cache-Control"] = "no-cache"
```

关键操作：

1. **Content-Type 检测**：只对 `text/html` 类型的响应注入脚本，跳过 CSS、JS、图片等静态资源
2. **Content-Length 修正**：如果原始响应包含 `Content-Length` 头，需要加上注入脚本的字节长度，否则浏览器会因 Content-Length 与实际 body 大小不匹配而出错
3. **Cache-Control 设置**：对所有响应（不只是 HTML）添加 `Cache-Control: no-cache`，防止浏览器缓存导致刷新后看到旧版本

### 步骤3：拦截响应体（http.response.body）

```python
elif message["type"] == "http.response.body":
    request_complete = not message.get("more_body", False)
    if add_script and request_complete:
        message["body"] += self.script
```

关键操作：

1. **最后一个 body 块才注入**：只在 `more_body=False`（最后一个响应块）时追加脚本，确保脚本注入在 HTML 文档末尾（`</body>` 之前或之后，浏览器都能正确解析）
2. **仅对 HTML 注入**：`add_script` 标志在响应头阶段根据 Content-Type 设置，非 HTML 响应不修改 body
3. **字节拼接**：`self.script` 已预编码为 bytes，直接与 `message["body"]`（也是 bytes）拼接

### 步骤4：转发消息

```python
await send(message)
```

无论是修改后的还是未修改的消息，最终都通过原始的 `send` 回调发送给客户端。

## MutableHeaders 的使用

中间件使用 Starlette 提供的 `MutableHeaders` 类来修改响应头：

```python
from starlette.datastructures import MutableHeaders
headers = MutableHeaders(scope=message)
```

`MutableHeaders` 是对 ASGI headers 列表（`list[tuple[bytes, bytes]]`）的可变视图，支持类似字典的接口（`get()`、`__setitem__()` 等），会自动处理 key 的大小写不敏感性和 bytes/str 转换。

## 为什么添加 Cache-Control: no-cache？

开发过程中浏览器缓存是常见的痛点。如果浏览器缓存了 HTML 页面，即使服务器文件已更新，刷新后可能仍然显示旧版本。通过在中间件中统一添加 `Cache-Control: no-cache`，强制浏览器每次都向服务器验证资源新鲜度，确保预览始终是最新构建的结果。

这个设置对所有 HTTP 响应生效（不仅是 HTML），因为 CSS、JS、图片等静态资源也可能被缓存。

## 脚本注入位置

由于脚本被追加到最后一个 body 块的末尾，它实际上被注入到 HTML 文档的最末尾（`</html>` 之后）。浏览器对此非常宽容——即使 `<script>` 在 `<html>` 标签外部，它仍然会被解析和执行。这种注入位置选择的好处：

1. **不依赖 HTML 结构**：不需要查找 `</body>` 标签，不假设文档格式正确
2. **不阻塞渲染**：脚本在文档末尾加载，不阻塞页面渲染
3. **实现简单**：只需追加到最后一个 body 块，不需要解析或修改 HTML 内容

## Type Hints 和 TYPE_CHECKING

模块使用了 `TYPE_CHECKING` 条件导入来避免运行时循环导入：

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from starlette.types import ASGIApp, Message, Receive, Scope, Send
```

`TYPE_CHECKING` 在静态类型检查时为 `True`，运行时为 `False`，这样类型注解不会导致运行时导入开销或循环依赖。

## 与 StaticFiles 的协作

中间件包装的下游应用是 `StaticFiles(directory=out_dir, html=True)`。StaticFiles 负责：

- 将 URL 路径映射到文件系统路径
- 设置正确的 Content-Type（基于文件扩展名）
- 处理目录请求，返回 `index.html`
- 支持 `304 Not Modified` （但中间件添加的 `no-cache` 会禁用缓存验证）

中间件不关心文件如何被提供，只关心响应头中的 Content-Type 和最终的响应体。

## 可测试性

中间件的设计使其易于测试。在 `tests/test_application.py` 中：

```python
response = client.get("/")
assert response.status_code == 200
assert response.headers["Cache-Control"] == "no-cache"
```

使用 Starlette 的 `TestClient` 可以直接验证中间件的效果——返回 200 状态码，且 `Cache-Control` 头被正确设置。更完整的测试可以检查响应体中是否包含 WebSocket 脚本。

## 相关概念

- [架构概览](02-architecture-overview.md)
- [服务器与热重载](06-server-and-hotreload.md)
- [文件监听与过滤](05-file-watching.md)
- [sphinx-autobuild 源码信源登记](../references/sphinx-autobuild-source.md)
