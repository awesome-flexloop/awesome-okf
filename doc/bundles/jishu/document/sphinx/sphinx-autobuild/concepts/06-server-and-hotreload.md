---
type: Concept
title: 服务器与热重载
description: RebuildServer 的异步架构——Starlette ASGI 应用、WebSocket 通信、Event 信号机制、lifespan 生命周期管理
tags: [sphinx-autobuild, server, websocket, hot-reload, asyncio, Starlette, Uvicorn]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T14:50:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: sphinx-autobuild-source
    resource: /references/sphinx-autobuild-source.md
    title: sphinx-autobuild 源码信源登记
---

# 服务器与热重载

## 技术栈

sphinx-autobuild 的服务器层基于现代 Python 异步 Web 生态：

| 组件 | 库 | 版本要求 | 用途 |
|------|-----|---------|------|
| ASGI 框架 | Starlette | >=0.35 | 路由、中间件、WebSocket、静态文件 |
| ASGI 服务器 | Uvicorn | >=0.25 | HTTP/WebSocket 协议实现 |
| 文件监听 | watchfiles | >=0.20 | 异步文件系统变化通知 |
| WebSocket | starlette.websockets | （随 Starlette） | WebSocket 连接封装 |

## ASGI 应用组装

在 `__main__._create_app()` 函数中完成 Starlette 应用的组装：

```python
def _create_app(watch_dirs, ignore_handler, builder, out_dir, url_host):
    watcher = RebuildServer(watch_dirs, ignore_handler, change_callback=builder)

    return Starlette(
        routes=[
            WebSocketRoute("/websocket-reload", watcher, name="reload"),
            Mount("/", app=StaticFiles(directory=out_dir, html=True), name="static"),
        ],
        middleware=[Middleware(JavascriptInjectorMiddleware, ws_url=url_host)],
        lifespan=watcher.lifespan,
    )
```

### 路由配置

| 路由 | 类型 | 处理者 | 说明 |
|------|------|--------|------|
| `/websocket-reload` | WebSocketRoute | `watcher`（RebuildServer 实例） | 浏览器热重载 WebSocket 端点 |
| `/` | Mount (StaticFiles) | `StaticFiles(directory=out_dir, html=True)` | 托管构建输出的静态 HTML 文件 |

`StaticFiles(html=True)` 启用了 HTML 模式，即访问目录时自动查找 `index.html`。

### Lifespan 绑定

Starlette 的 `lifespan` 参数绑定到 `watcher.lifespan`，这是一个 `@asynccontextmanager` 装饰的异步上下文管理器，负责管理文件监听后台任务的生命周期。

## RebuildServer 类

`RebuildServer` 位于 `sphinx_autobuild/server.py`，是一个同时承担 WebSocket 处理和文件监听的双职责类。它之所以可以同时作为 WebSocket 路由处理器（传给 `WebSocketRoute`），是因为它实现了 ASGI 可调用接口 `__call__(scope, receive, send)`。

### 初始化

```python
class RebuildServer:
    def __init__(
        self,
        paths: list[os.PathLike[str]],
        ignore_filter: IgnoreFilter,
        change_callback: Callable[[Sequence[Path]], None],
    ) -> None:
        self.paths = [Path(path).resolve(strict=True) for path in paths]
        self.ignore = ignore_filter
        self.change_callback = change_callback
        self.flag = asyncio.Event()
        self.should_exit = asyncio.Event()
```

两个 `asyncio.Event` 是核心同步原语：

| Event | 用途 |
|-------|------|
| `self.flag` | 构建完成信号。watch() 设置它，watch_reloads() 等待它 |
| `self.should_exit` | 服务器关闭信号。lifespan 关闭时设置它，main() 等待它 |

### Lifespan 生命周期

```python
@asynccontextmanager
async def lifespan(self, _app) -> AbstractAsyncContextManager[None]:
    task = asyncio.create_task(self.main())
    yield
    self.should_exit.set()
    await task
    return
```

Lifespan 流程：
1. **启动时**（`yield` 之前）：创建 `main()` 后台任务
2. **运行中**（`yield` 期间）：应用正常服务请求
3. **关闭时**（`yield` 之后）：设置 `should_exit` 事件，等待 `main()` 任务结束

这确保了文件监听循环在应用关闭时被优雅地清理，不会留下孤儿任务。

### 主循环

```python
async def main(self) -> None:
    tasks = (
        asyncio.create_task(self.watch()),
        asyncio.create_task(self.should_exit.wait()),
    )
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    [task.cancel() for task in pending]
    [task.result() for task in done]
```

使用 `asyncio.wait(FIRST_COMPLETED)` 实现竞赛模式：
- `self.watch()`：文件监听循环（长运行任务）
- `self.should_exit.wait()`：等待关闭信号

任一个完成（watch 异常退出，或收到关闭信号），就取消其他任务并收集结果。`task.result()` 会重新抛出任务中的异常，确保错误不会被静默吞掉。

### 文件监听循环

```python
async def watch(self) -> None:
    async for changes in watchfiles.awatch(
        *self.paths,
        watch_filter=lambda _, path: not self.ignore(path),
    ):
        changed_paths = [Path(path).resolve() for (_, path) in changes]
        with ProcessPoolExecutor() as pool:
            fut = pool.submit(self.change_callback, changed_paths=changed_paths)
            await asyncio.wrap_future(fut)
        self.flag.set()
```

工作流程：
1. `watchfiles.awatch()` 异步迭代文件变化事件
2. 过滤后的变化路径被收集
3. 通过 `ProcessPoolExecutor` 在子进程中执行 `change_callback`（即 Builder），用 `asyncio.wrap_future()` 桥接到 asyncio
4. 构建完成后 `self.flag.set()` 通知 WebSocket 推送循环

### WebSocket 连接处理

```python
async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
    assert scope["type"] == "websocket"
    ws = WebSocket(scope, receive, send)
    await ws.accept()

    tasks = (
        asyncio.create_task(self.watch_reloads(ws)),
        asyncio.create_task(self.wait_client_disconnect(ws)),
    )
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    [task.cancel() for task in pending]
    [task.result() for task in done]
```

每个 WebSocket 连接也使用竞赛模式，同时运行两个任务：
- `watch_reloads(ws)`：等待构建信号并发送刷新消息
- `wait_client_disconnect(ws)`：等待客户端断开（迭代接收消息直到连接关闭）

任一个完成（页面刷新触发新连接，或用户关闭标签页），取消另一个任务。

### 热重载推送

```python
async def watch_reloads(self, ws: WebSocket) -> None:
    while True:
        await self.flag.wait()
        self.flag.clear()
        await ws.send_text("refresh")
```

这是热重载的核心循环：
1. 等待 `self.flag` 被设置（构建完成）
2. 立即清除 flag（准备下一次信号）
3. 通过 WebSocket 发送文本消息 `"refresh"`

浏览器端收到消息后执行 `window.location.reload()` 刷新页面。

### 客户端断开检测

```python
@staticmethod
async def wait_client_disconnect(ws: WebSocket) -> None:
    async for _ in ws.iter_text():
        pass
```

简单地迭代 WebSocket 文本消息，当连接关闭时迭代结束，任务完成。这利用了 Starlette WebSocket 的 `iter_text()` 异步迭代器，在客户端断开时自动退出。

## Event 信号机制

`self.flag`（`asyncio.Event`）是连接文件监听循环和 WebSocket 推送循环的桥梁：

```
watch() 线程                    watch_reloads() 协程
    │                                │
    │  检测到文件变化                  │
    │  → ProcessPoolExecutor          │
    │  → Builder 执行构建              │
    │                                │  await self.flag.wait()
    │  构建完成                       │  （挂起，等待信号）
    │  self.flag.set() ──────────────→│
    │                                │  self.flag.clear()
    │  （继续监听）                    │  await ws.send_text("refresh")
    │                                │  → 浏览器收到消息，刷新页面
    │                                │  await self.flag.wait()
    │                                │  （再次挂起，等待下一次）
```

`asyncio.Event` 的 `wait()` + `set()` + `clear()` 模式实现了一个简单的**一次性信号量**：构建完成产生一个信号，所有等待的 WebSocket 连接收到信号后立即消费（clear），准备下一轮。

## 多客户端支持

由于每个 WebSocket 连接都独立运行 `watch_reloads()` 协程，而它们共享同一个 `self.flag` Event，所以多个浏览器标签页/窗口同时连接时：

- 构建完成后 `flag.set()` 会唤醒所有等待的 `watch_reloads()` 协程
- 第一个被唤醒的协程 `flag.clear()` 会清除信号，但其他已经通过 `wait()` 的协程不受影响（它们已经在 `wait()` 返回后的执行路径上）
- 所有连接的浏览器都会收到刷新消息

> **注意**：如果两个构建快速连续发生，`flag.set()` 在 `clear()` 之前被再次调用，第二次信号可能丢失。但在实际使用中，sphinx-build 构建需要数秒时间，这种竞态条件几乎不会发生。

## Uvicorn 启动

最终通过 `uvicorn.run()` 启动服务器：

```python
uvicorn.run(app, host=host_name, port=port_num, log_level="warning")
```

- `log_level="warning"`：只显示警告及以上级别的日志，避免 Uvicorn 的访问日志干扰 sphinx-build 的输出
- 默认 host `127.0.0.1`：只监听本地回环，不暴露到局域网（安全默认）
- 默认端口 `8000`：常见的 Web 开发端口

## 相关概念

- [架构概览](02-architecture-overview.md)
- [中间件注入机制](07-middleware-injection.md)
- [文件监听与过滤](05-file-watching.md)
- [构建系统](04-builder-system.md)
- [sphinx-autobuild 源码信源登记](../references/sphinx-autobuild-source.md)
