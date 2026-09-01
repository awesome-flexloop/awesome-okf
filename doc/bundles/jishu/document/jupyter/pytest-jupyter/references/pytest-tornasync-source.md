---
okf_version: "0.2"
type: reference
title: "Tornado异步测试源码（pytest_tornasync.py）"
description: "pytest_jupyter/pytest_tornasync.py 的完整API：内嵌的pytest-tornasync分支、IOLoop管理、HTTP服务器/客户端fixtures、AsyncHTTPServerClient类"
tags: [tornado, async-testing, http-server, http-client, ioloop, pytest-tornasync, websocket, vendored]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:45:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T14:45:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: pytest-tornasync-py
    resource: "../../../../../external/libs/jupyter/pytest-jupyter/pytest_jupyter/pytest_tornasync.py"
    title: "pytest_jupyter/pytest_tornasync.py"
---

# Tornado异步测试源码（pytest_tornasync.py）

本信源登记 `pytest_jupyter/pytest_tornasync.py`（约101行）的核心fixtures和类。pytest_tornasync.py是内嵌（vendored）的pytest-tornasync插件分支，提供Tornado异步HTTP测试基础设施。它通过`from pytest_jupyter.jupyter_core import *`继承core插件的fixtures。

## 模块来源说明

文件头部注释标明这是来自 [pytest-tornasync](https://github.com/eukaryote/pytest-tornasync) 的vendored fork，提交哈希为 `9f1bdeec3eb5816e0183f975ca65b5f6f29fbfbb`。

[F-050]

## 模块级导入处理

```python
try:
    import tornado.ioloop
    import tornado.testing
    from tornado.simple_httpclient import SimpleAsyncHTTPClient
except ImportError:
    SimpleAsyncHTTPClient = object
```

- 若tornado未安装，将`SimpleAsyncHTTPClient`设为`object`作为占位
- 导入`tornado.ioloop`、`tornado.testing`、`SimpleAsyncHTTPClient`

[F-051]

## 核心Fixtures

### io_loop(jp_asyncio_loop) -> IOLoop

返回当前Tornado IOLoop实例。

**行为：**
- 调用`tornado.ioloop.IOLoop.current()`获取当前事件循环
- 依赖`jp_asyncio_loop`确保asyncio事件循环已创建

[F-052]

### http_server_port() -> tuple

绑定一个未使用的端口，返回 `(socket, port)` 元组。

**行为：**
- 调用`tornado.testing.bind_unused_port()`获取空闲端口
- 返回值是一个元组：第一个元素是socket对象，第二个是端口号
- 此fixture被`http_server`和`jp_http_port`等fixture使用

[F-053]

### http_server(jp_asyncio_loop, http_server_port, jp_web_app) -> HTTPServer

启动一个Tornado HTTP服务器。

**行为：**
1. 定义异步`get_server()`协程：
   - 创建`tornado.httpserver.HTTPServer(jp_web_app)`
   - 调用`server.add_socket(http_server_port[0])`绑定socket
   - 返回server
2. 在事件循环上运行`get_server()`获取server实例
3. yield server给测试使用
4. 清理阶段（yield之后）：
   - 调用`server.stop()`停止服务器
   - 若有`close_all_connections`方法，尝试调用并捕获TimeoutError
   - 关闭socket：`http_server_port[0].close()`

[F-054]

### http_server_client(http_server, jp_asyncio_loop) -> AsyncHTTPServerClient

创建异步HTTP测试客户端。

**行为：**
1. 定义异步`get_client()`协程，返回`AsyncHTTPServerClient(http_server=http_server)`
2. 在事件循环上运行获取client
3. 使用`contextlib.closing`上下文管理器管理client生命周期
4. yield client给测试使用

[F-055]

## 核心类

### class AsyncHTTPServerClient(SimpleAsyncHTTPClient)

继承自`tornado.simple_httpclient.SimpleAsyncHTTPClient`的自定义HTTP客户端。

#### initialize(self, *, http_server=None)

初始化方法（覆盖SimpleAsyncHTTPClient的initialize）。

**行为：**
1. 调用`super().initialize()`
2. 存储`self._http_server = http_server`

[F-056]

#### fetch(self, path, **kwargs)

从测试服务器获取路径（覆盖SimpleAsyncHTTPClient的fetch）。

**行为：**
- 调用`self.get_url(path)`获取完整URL
- 委托给`super().fetch(self.get_url(path), **kwargs)`发送请求

[F-057]

#### get_protocol(self) -> str

返回协议字符串 `"http"`。

[F-058]

#### get_http_port(self) -> int | None

从服务器socket获取端口号。

**行为：**
- 遍历`self._http_server._sockets.values()`
- 返回第一个socket的`sock.getsockname()[1]`（即绑定的端口号）
- 若无socket则返回None

[F-059]

#### get_url(self, path) -> str

构造完整URL。

**行为：**
- 返回 `f"{self.get_protocol()}://127.0.0.1:{self.get_http_port()}{path}"`

[F-060]

## 设计要点

1. **Vendored依赖**：直接内嵌pytest-tornasync源码而非作为外部依赖，避免版本兼容问题
2. **桥接asyncio**：`io_loop`fixture依赖`jp_asyncio_loop`，确保Tornado IOLoop与pytest-jupyter管理的asyncio循环一致
3. **自动端口分配**：使用`tornado.testing.bind_unused_port()`自动获取空闲端口，避免端口冲突
4. **资源安全清理**：http_server在yield后执行多层清理（stop→close_all_connections→close socket），防止资源泄漏
5. **contextlib.closing**：http_server_client使用`closing`上下文管理器确保客户端正确关闭
6. **SimpleAsyncHTTPClient基类**：继承SimpleAsyncHTTPClient而非AsyncHTTPClient，更轻量且适合测试场景
