---
okf_version: "0.2"
type: concept
title: "Tornado异步测试支持"
description: "深入理解内嵌的pytest_tornasync模块：IOLoop桥接、自动端口分配、HTTP测试服务器/客户端、AsyncHTTPServerClient自定义类。"
tags: [tornado, async-testing, ioloop, http-server, http-client, websocket, vendored, port-binding]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:45:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T14:45:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: pytest-tornasync-source
    resource: "/references/pytest-tornasync-source.md"
    title: "Tornado异步测试源码信源"
---

# Tornado异步测试支持

pytest-jupyter 内嵌了一个 **pytest-tornasync** 的fork（`pytest_jupyter.pytest_tornasync`），提供Tornado异步HTTP测试基础设施。Jupyter Server基于Tornado框架构建，因此需要Tornado的测试工具来模拟HTTP请求和WebSocket连接。

## 为什么内嵌而非作为依赖？

pytest-tornasync是一个第三方pytest插件，但pytest-jupyter选择将其源码直接vendored到代码库中（文件头注释标明了来源和commit hash）。这样做的原因：

1. **版本控制**：确保与特定版本Tornado的兼容性，不受外部插件更新影响
2. **定制化修改**：可以针对Jupyter测试场景做调整（如桥接jp_asyncio_loop）
3. **避免插件冲突**：作为pytest_jupyter内部模块，不与外部安装的pytest-tornasync冲突
4. **零额外依赖**：用户不需要单独安装pytest-tornasync

[F-050]

## 模块导入与容错

```python
try:
    import tornado.ioloop
    import tornado.testing
    from tornado.simple_httpclient import SimpleAsyncHTTPClient
except ImportError:
    SimpleAsyncHTTPClient = object
```

如果tornado未安装（即只安装了core而没装server），模块不会崩溃，只是`SimpleAsyncHTTPClient`被设为`object`占位。实际使用这些fixtures时如果tornado不可用，会在fixture执行时（而非模块加载时）报错。

[F-051]

## IOLoop桥接

### io_loop fixture

```python
@pytest.fixture
def io_loop(jp_asyncio_loop):
    return tornado.ioloop.IOLoop.current()
```

`io_loop`是连接pytest-jupyter的asyncio事件循环和Tornado IOLoop的关键fixture：

1. 依赖`jp_asyncio_loop`确保asyncio事件循环已创建
2. 调用`tornado.ioloop.IOLoop.current()`获取与当前asyncio循环绑定的Tornado IOLoop
3. Tornado 5+默认使用asyncio事件循环作为底层，所以IOLoop.current()自动包装已有的asyncio loop

**为什么需要这层桥接？** Tornado的HTTPServer和AsyncHTTPClient需要Tornado IOLoop来调度异步操作，而pytest-jupyter通过pytest钩子直接运行asyncio协程。`io_loop`fixture确保两者使用同一个事件循环。

[F-052]

## 端口管理

### http_server_port fixture

```python
@pytest.fixture
def http_server_port():
    return tornado.testing.bind_unused_port()
```

调用`tornado.testing.bind_unused_port()`自动绑定一个空闲端口，返回`(socket, port)`元组：
- `socket`：已绑定的socket对象（用于HTTPServer.add_socket()）
- `port`：绑定的端口号（整数）

**为什么不手动指定端口？**
- 避免并行测试时端口冲突
- 避免端口被其他进程占用导致测试失败
- tornado的`bind_unused_port()`通过绑定port=0让操作系统分配空闲端口

[F-053]

## HTTP测试服务器

### http_server fixture

```python
@pytest.fixture
def http_server(jp_asyncio_loop, http_server_port, jp_web_app):
    async def get_server():
        server = tornado.httpserver.HTTPServer(jp_web_app)
        server.add_socket(http_server_port[0])
        return server
    server = jp_asyncio_loop.run_until_complete(get_server())
    yield server
    server.stop()
    if hasattr(server, "close_all_connections"):
        try:
            jp_asyncio_loop.run_until_complete(server.close_all_connections())
        except asyncio.TimeoutError:
            pass
    http_server_port[0].close()
```

**工作流程：**
1. 创建`tornado.httpserver.HTTPServer(jp_web_app)`——jp_web_app是ServerApp的tornado Application
2. 通过`server.add_socket()`使用预先绑定的socket（而非`server.listen()`），这样端口已知且不会冲突
3. yield server给测试使用
4. 清理阶段：
   - `server.stop()`停止接受新连接
   - `close_all_connections()`关闭现有连接（捕获TimeoutError防止阻塞）
   - 关闭底层socket

[F-054]

**关键设计：使用add_socket而非listen**

通常Tornado应用使用`server.listen(port)`启动，但pytest-jupyter使用预先绑定的socket：
1. 先通过`bind_unused_port()`获取空闲端口和已绑定socket
2. 将socket传给server，避免listen()内部再次绑定可能引发的竞争条件
3. 端口号确定，jp_http_port和其他fixture可以安全使用

## HTTP测试客户端

### http_server_client fixture

```python
@pytest.fixture
def http_server_client(http_server, jp_asyncio_loop):
    async def get_client():
        return AsyncHTTPServerClient(http_server=http_server)
    client = jp_asyncio_loop.run_until_complete(get_client())
    with closing(client) as context:
        yield context
```

创建`AsyncHTTPServerClient`实例，使用`contextlib.closing`确保客户端正确关闭。

[F-055]

### AsyncHTTPServerClient类

```python
class AsyncHTTPServerClient(SimpleAsyncHTTPClient):
    def initialize(self, *, http_server=None):
        super().initialize()
        self._http_server = http_server

    def fetch(self, path, **kwargs):
        return super().fetch(self.get_url(path), **kwargs)

    def get_protocol(self):
        return "http"

    def get_http_port(self):
        for sock in self._http_server._sockets.values():
            return sock.getsockname()[1]
        return None

    def get_url(self, path):
        return f"{self.get_protocol()}://127.0.0.1:{self.get_http_port()}{path}"
```

**为什么自定义HTTP客户端？**

`SimpleAsyncHTTPClient.fetch()`需要完整URL，但测试中通常只知道路径。`AsyncHTTPServerClient`封装了：
1. **自动URL构造**：`get_url(path)`自动拼接`http://127.0.0.1:{port}{path}`
2. **动态端口发现**：`get_http_port()`从server的sockets中获取实际端口
3. **协议固定**：`get_protocol()`返回`"http"`（测试环境不需要HTTPS）

这使得测试代码可以写`client.fetch("/api/spec.yaml")`而非`client.fetch("http://127.0.0.1:54321/api/spec.yaml")`。

[F-056]~[F-060]

**为什么用SimpleAsyncHTTPClient而非AsyncHTTPClient？**

`SimpleAsyncHTTPClient`是Tornado提供的更简单的HTTP客户端实现：
- 不支持HTTP/2和某些高级特性
- 但足够测试使用
- 更轻量、更快、更可预测
- 适合测试环境（不需要生产级客户端的复杂性）

## 与Server插件的协作

pytest_tornasync提供的fixtures与Server插件fixtures形成以下协作链：

```
pytest_tornasync提供:                   Server插件提供:
┌─────────────────────┐                ┌──────────────────────┐
│ http_server_port    │◄───jp_http_port │                      │
│ (socket, port)      │                │                      │
└─────────┬───────────┘                │                      │
          │                            │                      │
          ▼                            │                      │
┌─────────────────────┐    jp_web_app  │                      │
│ http_server         │◄───────────────┤ jp_serverapp         │
│ (HTTPServer)        │                │ (ServerApp实例)      │
└─────────┬───────────┘                │                      │
          │                            │                      │
          ▼                            │                      │
┌─────────────────────┐                │                      │
│ http_server_client  │◄───jp_fetch───►│ jp_auth_header       │
│ (AsyncHTTPClient)   │    jp_ws_fetch │ jp_base_url          │
└─────────────────────┘                └──────────────────────┘
```

- `jp_web_app`从`jp_serverapp.web_app`获取tornado Application
- `jp_http_port`从`http_server_port`提取端口号并负责关闭socket
- `jp_fetch`使用`http_server_client`发送请求，自动添加认证头和base URL
- `jp_ws_fetch`直接使用`tornado.websocket.websocket_connect`，连接到同一端口

## 测试中的fixture组合

典型的Server测试使用以下fixture组合（大多数是自动注入的，不需要显式声明）：

```python
async def test_api(jp_fetch):  # 只需要jp_fetch
    # jp_fetch 背后依赖:
    #   - jp_serverapp → jp_configurable_serverapp → jp_environ → ...（完整链）
    #   - http_server_client → http_server → http_server_port, jp_web_app
    #   - jp_auth_header, jp_base_url
    response = await jp_fetch("api", "spec.yaml")
    assert response.code == 200
```

pytest的fixture依赖解析自动处理所有这些依赖，测试代码只需要声明直接使用的fixture。

## Tornasync层使用建议

1. **通常不需要直接使用tornasync fixtures**：`jp_fetch`和`jp_ws_fetch`已经封装了HTTP/WebSocket客户端的使用细节，除非你需要直接控制Tornado IOLoop或创建自定义服务器
2. **io_loop用于在fixture中运行协程**：如果你的fixture需要运行异步代码，可以使用`io_loop.run_until_complete(coro)`或`jp_asyncio_loop.run_until_complete(coro)`
3. **不要手动创建HTTPServer**：使用`http_server` fixture，它正确处理端口绑定和清理
4. **SimpleAsyncHTTPClient的局限**：不支持HTTPS、HTTP/2、cookie持久化等高级特性，但测试场景通常不需要这些

---

**下一步阅读：**
- [Server插件详解](05-server-plugin.md) — jp_fetch/jp_ws_fetch如何在tornasync基础上构建
- [Fixture工厂模式](08-fixture-factories.md) — 可配置fixtures的设计模式
