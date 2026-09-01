---
type: concept
title: "异步双路径：Future 状态机与 asyncio 集成"
description: "pyzmq 的 _AsyncSocket 事件状态机、recv/send Future 双端队列、shadow socket 非阻塞短路、DONTWAIT 优化、asyncio add_reader 集成、tornado future 兼容、Windows ProactorEventLoop 适配、ZMQEventLoop 废弃"
tags: [pyzmq, zeromq, async, asyncio, future, tornado, nonblocking]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [../references/constants-enums.md, ../references/error-hierarchy.md]
  facts: [F-062, F-063, F-064, F-065, F-066, F-067, F-068, F-069, F-070, F-071, F-072, F-073, F-074, F-075, F-076, F-107]
---

# 异步双路径：Future 状态机与 asyncio 集成

## 核心理解

pyzmq 提供两套异步 API：`zmq.asyncio`（原生 asyncio/await）和 `zmq.eventloop.future`（tornado Future）。两者共享同一个核心事件状态机（`_future._AsyncSocket`/`_AsyncPoller`），只通过薄 mixin 替换 Future 类型和事件循环注册方式。这种"状态机 + 可注入 loop 抽象"的设计，使同一份队列消费逻辑可服务 tornado、asyncio 两个时代，而 gevent 走第三条路（greenlet 让出而非 Future）。

异步 Socket 的核心技巧是：内部维护一个**影子同步 Socket**（shadow socket），在其上用 `DONTWAIT` 做非阻塞尝试——成功则立即完成 Future，失败（EAGAIN）才注册 IO 事件入队等待。这避免了不必要的事件循环往返。

## 架构总览

```
┌─────────────────────────────────────────────────────┐
│                   用户异步代码                         │
│  await socket.recv()  /  await socket.send(data)    │
├─────────────────────────────────────────────────────┤
│            zmq.asyncio.Socket / Poller               │
│  _AsyncIO mixin: _Future=asyncio.Future              │
│  add_reader/remove_reader (selector)                 │
├─────────────────────────────────────────────────────┤
│         zmq.eventloop.future.Socket / Poller         │
│  _AsyncTornado mixin: _Future=TornadoFuture          │
│  IOLoop.READ/WRITE                                   │
├─────────────────────────────────────────────────────┤
│            _future._AsyncSocket (核心状态机)          │
│  _recv_futures / _send_futures 双端队列              │
│  _shadow_sock (影子同步 Socket)                      │
│  _add_recv_event / _add_send_event                   │
│  _handle_recv / _handle_send (事件回调)              │
├─────────────────────────────────────────────────────┤
│              zmq.Socket (同步 sugar 层)               │
├─────────────────────────────────────────────────────┤
│              backend Socket (C 绑定)                  │
└─────────────────────────────────────────────────────┘
```

## _Async mixin 抽象点

### F-062：可注入的异步抽象

`_Async` mixin 定义了异步适配的抽象点：

```python
class _Async:
    _current_loop = None
    _Future = None           # 子类设置：asyncio.Future / TornadoFuture

    def _get_loop(self):     # 检测 loop 变化并重新初始化 IO
        ...

    def _default_loop(self): # 子类实现：获取当前事件循环
        raise NotImplementedError

    def _init_io_state(self, loop):  # 子类实现：注册 FD 到 loop
        pass

    def _clear_io_state(self):       # 子类实现：注销 FD
        pass
```

关键设计：`_Future` 是类属性，子类只需替换为不同的 Future 类即可适配不同的异步框架。`_get_loop` 检测当前 loop 是否变化，若变化则重新初始化 IO 状态，支持在多 loop 间迁移 socket。

## _AsyncSocket 事件状态机

### F-064：内部数据结构

```python
class _AsyncSocket(_Async, zmq.Socket[_FutureT]):
    def __init__(self, ...):
        self._recv_futures = deque()   # 接收 Future 队列
        self._send_futures = deque()   # 发送 Future 队列
        self._shadow_sock = zmq.Socket.shadow(self.underlying)
        # _shadow_sock 是同步 Socket，用于实际非阻塞调用
```

**影子 Socket（shadow socket）** 是关键设计：异步 Socket 不直接在自身上调用 recv/send（因为自身的方法被覆写为返回 Future），而是创建一个共享同一底层 `zmq_msg_t` 的影子同步 Socket，在其上执行 `DONTWAIT` 非阻塞调用。两个 Socket 共享同一个 libzmq socket 指针，但 Python 层一个异步一个同步。

### F-065：异步方法签名

所有 I/O 方法均返回 Future/Awaitable：

```python
# 异步 Socket
msg = await socket.recv()
await socket.send(data)
parts = await socket.recv_multipart()
await socket.send_multipart([b"a", b"b"])
n = await socket.recv_into(buf)
```

这些方法不直接执行 I/O，而是通过 `_add_recv_event`/`_add_send_event` 入队，返回 Future。

### F-066：_add_recv_event 接收路径

```
await socket.recv()
  │
  ├─ 带 DONTWAIT 标志？
  │   └─ 是 → 直接在 _shadow_sock 上非阻塞 recv
  │           ├─ 成功 → future.set_result(msg)
  │           └─ EAGAIN → future.set_exception(Again)
  │
  └─ 否（阻塞模式）
      ├─ 先尝试 DONTWAIT recv（优化：可能立即就绪）
      │   └─ 成功 → 立即完成 Future（不注册事件）
      │
      └─ EAGAIN → 创建 _FutureEvent
          ├─ 根据 RCVTIMEO 添加超时定时器
          ├─ 加入 _recv_futures 队列
          └─ _add_io_state(POLLIN) 注册读事件
              │
              │  ... 事件循环等待 ...
              │
              └─ 可读 → _handle_recv 回调
```

**DONTWAIT 短路优化**：即使调用者没有传 NOBLOCK，内部也会先尝试一次非阻塞 recv。如果消息已经在内核缓冲区中（常见于批量处理），立即完成 Future，避免了事件循环注册和回调的开销。

### F-067：_add_send_event 发送路径

```
await socket.send(data)
  │
  ├─ 队列为空？→ 先尝试 DONTWAIT 非阻塞发送
  │   ├─ 成功 → 立即完成 Future
  │   └─ EAGAIN 且未要求 DONTWAIT → 降级为异步等待
  │
  ├─ 队列非空 → 不能尝试（保证发送顺序）
  │
  └─ 异步等待
      ├─ 根据 SNDTIMEO 添加超时定时器
      ├─ 加入 _send_futures 队列
      └─ 注册 POLLOUT 事件
          │
          └─ 可写 → _handle_send 回调
```

发送路径在队列非空时不能尝试直接发送——必须排队保证消息顺序。只有队列为空时才做短路尝试。

### F-068：_handle_recv / _handle_send

当 IO 事件触发时，回调从队列弹出第一个未完成 Future：

```python
def _handle_recv(self):
    while self._recv_futures:
        future_event = self._recv_futures[0]
        try:
            msg = self._shadow_sock.recv(flags=DONTWAIT)
            future_event.set_result(msg)
            self._recv_futures.popleft()
        except Again:
            break  # 没有更多消息可读，等待下次事件
```

回调循环处理所有已就绪的 Future，直到 EAGAIN（无更多数据）。`kind='poll'` 时只 signal ready 而非实际 recv（用于 Poller）。

### F-069：_deserialize 链式 Future

异步 Socket 覆写了 `_deserialize` 以支持 `await recv_json()` 链式调用：

```python
def _deserialize(self, recvd, load):
    future = self._Future()
    def _chain(f):
        if f.cancelled():
            future.cancel()
        elif f.exception():
            future.set_exception(f.exception())
        else:
            try:
                future.set_result(load(f.result()))
            except Exception as e:
                future.set_exception(e)
    recvd.add_done_callback(_chain)
    return future
```

当 `await socket.recv_json()` 时：
1. `recv()` 返回一个 recv Future
2. `_deserialize` 创建新的 json Future
3. recv Future 完成时，在回调中执行 `json.loads(result)` 并传递给 json Future
4. 取消事件从 json Future 传播回 recv Future

### F-070：close 清理

```python
def close(self, linger=None):
    # 取消所有未完成的 Future
    for f in self._recv_futures:
        f.cancel()
    for f in self._send_futures:
        f.cancel()
    # 清理 IO 注册
    self._clear_io_state()
    # 关闭影子 socket 和自身
    self._shadow_sock.close()
    super().close(linger)
```

关闭时必须取消所有未完成 Future，否则调用方会永远 await。

## _AsyncPoller

### F-063：异步 Poller

`_AsyncPoller` 继承 `_Async` 和 `zmq.Poller`，其 `poll(timeout=-1)` 返回 Awaitable/Future：

```python
async def poller_example():
    poller = zmq.asyncio.Poller()
    poller.register(sock1, zmq.POLLIN)
    poller.register(sock2, zmq.POLLIN)

    events = await poller.poll(timeout=1000)
    for sock, mask in events:
        if mask & zmq.POLLIN:
            msg = await sock.recv()
```

**实现策略**：
- `timeout=0`：立即尝试非阻塞 `super().poll(0)`，返回已完成 Future
- `timeout>0`：创建 watcher Future，对每个注册的 socket/ fd 注册 IO 事件，事件就绪后用 `super().poll(0)` 取结果
- 对 zmq.Socket 调 `_add_recv_event`/`_add_send_event`
- 对原生 fd 调 `_watch_raw_socket`（由子类实现）

## asyncio 集成

### F-071：_AsyncIO mixin

```python
class _AsyncIO:
    _Future = asyncio.Future
    _READ = selectors.EVENT_READ
    _WRITE = selectors.EVENT_WRITE

    def _default_loop(self):
        try:
            return asyncio.get_running_loop()
        except RuntimeError:
            warnings.warn("No running event loop", RuntimeWarning)
            return asyncio.get_event_loop()
```

使用标准库 `asyncio.Future`，通过 `asyncio.get_running_loop()` 获取当前运行的循环（Python 3.7+ 推荐方式），无运行 loop 时回退 `get_event_loop()` 并发警告。

### F-072：asyncio.Socket

```python
class Socket(_AsyncIO, _future._AsyncSocket):
    def _init_io_state(self, loop):
        loop.add_reader(self._fd, self._handle_events)
    def _clear_io_state(self):
        loop.remove_reader(self._fd)
```

通过 asyncio loop 的 `add_reader`/`remove_reader`（底层 selector）注册 zmq FD 的可读事件。`self._fd` 是 `socket.fileno()` 返回的边缘触发文件描述符。

### F-073：asyncio.Poller

```python
class Poller(_AsyncIO, _AsyncPoller):
    _socket_class = Socket

    def _watch_raw_socket(self, loop, socket, evt, f):
        if evt & self._READ:
            loop.add_reader(socket, ...)
        if evt & self._WRITE:
            loop.add_writer(socket, ...)
```

原生 fd 用 `add_reader`/`add_writer` 注册。`_socket_class = Socket` 确保通过 Poller 创建的 socket 也是异步 Socket。

### F-074：asyncio.Context

```python
class Context(zmq.Context[Socket]):
    _socket_class = Socket
    _instance = None  # 重置单例，避免与同步 Context 共享
```

只需设置 `_socket_class = Socket`，`ctx.socket()` 即产出异步 Socket。重置 `_instance` 因为异步 Context 不能与同步 Context 共享单例（socket 类型不同）。

### F-075：Windows ProactorEventLoop 兼容

Windows 上 Python 3.8+ 默认使用 `ProactorEventLoop`，它**不支持 `add_reader`/`add_writer`**（ProactorIOCP 模型没有文件描述符复用器）。pyzmq 的解决方案：

1. 检测当前 loop 是否有 `add_reader` 方法
2. 若无（ProactorEventLoop），尝试用 tornado 的 `AddThreadSelectorEventLoop` 在后台线程运行一个 SelectorEventLoop 包装
3. patch loop.close 以在关闭时清理 selector 线程
4. 找不到 tornado 则抛 RuntimeError，提示用户切换到 `SelectorEventLoop`

非 Windows 平台用 `_get_selector_noop` 直接返回原 loop（Unix 上默认就是 SelectorEventLoop）。

```python
import sys
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
```

在 Windows 上使用 pyzmq asyncio 的推荐做法是切换到 SelectorEventLoop。

### F-076：废弃的 ZMQEventLoop

`ZMQEventLoop` 和 `install()` 自 pyzmq 17 起废弃。早期 pyzmq 需要自定义 IOLoop 来集成 zmq FD，现代 pyzmq 可直接在任意 asyncio event loop 上工作，无需自定义 loop。

## tornado future 路径

### F-107：eventloop.future

`zmq.eventloop.future` 提供 tornado 版异步 Socket/Poller：

```python
class _AsyncTornado:
    _Future = _TornadoFuture   # 恢复 cancel 能力的 tornado Future
    _READ = IOLoop.READ
    _WRITE = IOLoop.WRITE

    def _default_loop(self):
        return IOLoop.current()
```

与 asyncio 版的差异：
- Future 类用 tornado 的 Future（包装了 cancel 支持）
- 事件标志用 `IOLoop.READ`/`WRITE` 而非 `selectors.EVENT_READ/WRITE`
- loop 用 `IOLoop.current()` 而非 `asyncio.get_running_loop()`

核心队列状态机（`_AsyncSocket`）完全复用，只替换了 loop 抽象。

## gevent 第三条路

gevent 适配（`zmq.green`）不使用 Future 模型，而是直接覆写 send/recv，在 EAGAIN 时用 gevent `AsyncResult` 让出当前 greenlet：

```python
# zmq.green 不是 Future 风格
import zmq.green as zmq
# send/recv 看起来是同步的，但在 EAGAIN 时自动让出 greenlet
```

这是因为 gevent 的协作模型是 greenlet 而非 Future/await，无法直接复用 `_AsyncSocket` 的状态机。详见 [生态篇](07-ecosystem-eventloop-green-devices-log.md)。

## 同步与异步共享底层 Socket

通过 shadow 机制，同步和异步 Socket 可以共享同一个底层 libzmq socket：

```python
ctx = zmq.Context()
sync_sock = ctx.socket(zmq.PAIR)
sync_sock.bind("inproc://shared")

# 异步 Socket shadow 同步 Socket 的底层地址
async_ctx = zmq.asyncio.Context()
async_sock = async_ctx.socket(zmq.PAIR)
async_sock.connect("inproc://shared")
```

在 auth 模块中，`ThreadAuthenticator` 就在后台线程用 asyncio Poller，而主线程可以使用同步 Socket（F-103），两套 API 在同一进程共存。

## 相关概念

- [Socket sugar 语法层](02-socket-sugar.md) — 同步 Socket 的基类
- [Context 生命周期](01-context-lifecycle.md) — asyncio.Context 覆写 _socket_class
- [Poller 多路复用](04-poller.md) — 同步 Poller 基类
- [认证与 ZAP](06-auth-zap.md) — ThreadAuthenticator 使用 asyncio Poller
- [生态：eventloop/green/devices/log](07-ecosystem-eventloop-green-devices-log.md) — tornado future 和 gevent 适配
- [错误层次结构](../references/error-hierarchy.md) — Again 异常在 DONTWAIT 短路中的作用
