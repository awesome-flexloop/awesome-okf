---
type: Concept
title: "异步编程模型"
description: "anyio 异步抽象、async/await Handler、同步/异步双版本 Manager、to_thread 桥接与异步最佳实践"
tags: [async, asyncio, tornado, anyio, await, async-handler, concurrency]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T15:05:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: serverapp
    resource: /references/serverapp-source.md
    title: ServerApp 源码信源
---

# 异步编程模型

Jupyter Server 2.x 全面拥抱异步，基于 Tornado 的异步 I/O 循环和 anyio 抽象层，所有核心 Handler 和 Manager 均提供异步实现。

## 异步架构概览

```
Tornado IOLoop (asyncio)
    │
    ├── async Handler 处理 HTTP 请求
    │   ├── async def get() / post() / put() / delete()
    │   └── await 异步 Manager 方法
    │
    ├── async Manager 提供服务
    │   ├── AsyncFileContentsManager
    │   ├── AsyncMappingKernelManager
    │   ├── AsyncSessionManager
    │   └── await anyio.to_thread.run_sync() 桥接同步代码
    │
    └── PeriodicCallback 定时任务
        ├── cull_idle_kernels
        ├── last_activity 更新
        └── 统计信息收集
```

## anyio 抽象层

Jupyter Server 使用 `anyio` 库提供异步后端无关的抽象：

```python
import anyio

# 支持 asyncio 和 trio 后端
# 默认为 asyncio（Tornado 使用）
```

### anyio.to_thread 桥接

同步代码可以通过 `anyio.to_thread.run_sync()` 在线程池中执行，避免阻塞 I/O 循环：

```python
from anyio.to_thread import run_sync

class AsyncFileContentsManager(FileContentsManager):
    async def get(self, path, content=True, type=None, format=None):
        # 将同步文件 IO 操作放到线程池
        return await run_sync(super().get, path, content=content, type=type, format=format)
```

这使得同步 Manager 可以零改造地适配异步 Handler。

## 异步 Handler 编写

所有 v2.x 核心 API Handler 都是异步的：

```python
from jupyter_server.base.handlers import APIHandler
from tornado import web

class MyAPIHandler(APIHandler):
    @web.authenticated
    async def get(self, path):
        # 异步获取数据
        model = await self.contents_manager.get(path, content=True)
        self.finish(json.dumps(model))

    @web.authenticated
    async def post(self, path):
        body = self.get_json_body()
        # 异步启动内核
        kernel = await self.kernel_manager.start_kernel()
        self.set_status(201)
        self.finish(json.dumps({"id": kernel}))
```

### 关键点

- Handler 方法使用 `async def` 定义
- 调用异步 Manager 方法使用 `await`
- 长时间操作不会阻塞其他请求
- 保持认证装饰器 `@web.authenticated` 不变

## 同步/异步双版本 Manager

Jupyter Server 为核心服务提供同步和异步两个版本：

| 同步版本 | 异步版本（默认） |
|---------|----------------|
| `FileContentsManager` | `AsyncFileContentsManager` |
| `MappingKernelManager` | `AsyncMappingKernelManager` |
| `FileCheckpoints` | `AsyncFileCheckpoints` |
| `KernelSpecManager` | `AsyncKernelSpecManager` |
| `SessionManager` | `AsyncSessionManager` |

### 默认配置

默认使用异步版本：

```python
c.ServerApp.contents_manager_class = AsyncFileContentsManager
c.ServerApp.kernel_manager_class = AsyncMappingKernelManager
```

### 编写自定义异步 Manager

推荐继承异步基类：

```python
from jupyter_server.services.contents.manager import AsyncContentsManager

class MyAsyncContentsManager(AsyncContentsManager):
    async def get(self, path, content=True, type=None, format=None):
        # 使用异步 IO（如 aiofiles、aiohttp）
        async with aiofiles.open(self._to_os_path(path)) as f:
            content = await f.read()
        return self._to_model(content, path)

    async def save(self, model, path):
        async with aiofiles.open(self._to_os_path(path), 'w') as f:
            await f.write(model['content'])
```

### 编写同步 Manager 兼容异步

如果同步 Manager 不需要修改，继承同步基类即可，异步桥接自动通过 `to_thread` 实现：

```python
class MySyncContentsManager(ContentsManager):
    def get(self, path, content=True, type=None, format=None):
        # 同步实现
        with open(path) as f:
            return json.load(f)

# 配置时使用自动生成的异步版本
c.ServerApp.contents_manager_class = MySyncContentsManager
# AsyncMySyncContentsManager 会自动通过 anyio.to_thread 适配
```

## WebSocket 异步模型

WebSocket Handler 也是异步的：

```python
class MyWSHandler(WebSocketHandler):
    async def open(self, *args):
        self.queue = anyio.create_task_group()
        await self.start_background_tasks()

    async def on_message(self, message):
        # 异步处理消息
        response = await self.process_message(message)
        await self.write_message(response)

    def on_close(self):
        # 注意：on_close 不是 async（Tornado 限制）
        # 使用 self.ioloop.add_callback 调度异步清理
        self.ioloop.add_callback(self.async_cleanup)

    async def async_cleanup(self):
        await self.close_resources()
```

## 异步启动和停止

ServerApp 的初始化和关闭完全异步：

```python
# ServerApp.initialize() 是同步的（traitlets 限制）
# ServerApp.start() 是异步的
async def start(self):
    self.init_webapp()
    # 异步初始化所有扩展
    await self.extension_manager.start_extensions()
    # 启动 HTTP 服务器
    self.http_server.listen(self.port, self.ip)
    # 启动定时任务
    self.init_shutdown_cull_callback()
    self.init_terminals_cull_callback()

async def shutdown_server(self):
    # 异步关闭所有内核
    for kid in list(self.kernel_manager._kernels):
        await self.kernel_manager.shutdown_kernel(kid)
    # 关闭 HTTP 服务器
    self.http_server.stop()
```

## 异步陷阱与注意事项

### ⚠️ 不要阻塞 I/O 循环

错误：在 async Handler 中执行耗时同步操作

```python
# 错误：阻塞事件循环
async def get(self, path):
    time.sleep(10)           # ❌ 阻塞整个服务器
    data = requests.get(url) # ❌ 同步 HTTP 请求阻塞
```

正确：

```python
async def get(self, path):
    await anyio.sleep(10)    # ✅ 异步等待
    async with aiohttp.ClientSession() as s:  # ✅ 异步 HTTP
        async with s.get(url) as resp:
            data = await resp.json()
    # 或使用 to_thread 桥接
    data = await run_sync(requests.get, url)
```

### ⚠️ 正确使用 asyncio.Lock

在 Manager 中共享资源需要加锁：

```python
class AsyncMappingKernelManager:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._kernel_lock = anyio.Lock()

    async def start_kernel(self, **kwargs):
        async with self._kernel_lock:
            # 原子操作
            kernel_id = uuid.uuid4().hex
            km = await self._async_launch_kernel(kernel_id, **kwargs)
            self._kernels[kernel_id] = km
            return kernel_id
```

### ⚠️ PeriodicCallback 使用同步回调

Tornado 的 `PeriodicCallback` 期望同步回调：

```python
from tornado.ioloop import PeriodicCallback

# 同步回调
self.cull_callback = PeriodicCallback(
    self._cull_idle_kernels,  # 如果是 async def，需要包装
    self.cull_interval * 1000,
)

# 如果 _cull_idle_kernels 是 async def，需要这样包装：
async def _cull_idle_kernels(self):
    ...

def _cull_callback(self):
    self.io_loop.add_callback(self._cull_idle_kernels)
```

## 性能优势

异步模型的优势场景：

| 场景 | 同步模型 | 异步模型 |
|------|---------|---------|
| 100 并发短请求 | 线程切换开销 | 单线程高效 |
| 大文件上传/下载 | 线程阻塞 | 流式传输，不阻塞 |
| 内核启动等待 | 线程等待 | 并发等待多个内核启动 |
| WebSocket 连接 | 每个连接一个线程 | 单线程管理数千连接 |
| Gateway 代理 | 线程阻塞等待 | 并发多个上游请求 |

## 测试异步代码

使用 pytest + tornado 的异步测试支持：

```python
import pytest
from jupyter_server.utils import async_requests

async def test_api_get(jp_fetch):
    # jp_fetch 是异步测试客户端
    response = await jp_fetch("api/contents")
    assert response.code == 200
    data = json.loads(response.body)
    assert "content" in data
```

## 相关概念

- [Handler 继承体系](04-handler-hierarchy.md) — APIHandler 异步方法
- [内容管理服务](07-contents-service.md) — AsyncContentsManager
- [ServerApp 生命周期](03-serverapp-lifecycle.md) — 异步启动/关闭
