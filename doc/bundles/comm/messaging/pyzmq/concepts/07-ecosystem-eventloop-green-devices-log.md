---
type: concept
title: "生态模块：eventloop、green、devices、log 与 utils"
description: "pyzmq 周边生态：tornado eventloop 与 ZMQStream 回调、zmq.green gevent 协程适配、devices 消息代理设备、PUBHandler 日志发布、TopicLogger 主题日志、jsonapi 与 strtypes 工具"
tags: [pyzmq, zeromq, ecosystem, eventloop, tornado, gevent, devices, logging, utils]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [../references/constants-enums.md]
  facts: [F-106, F-107, F-108, F-109, F-110, F-111, F-112, F-113, F-114, F-115, F-116, F-117, F-118]
---

# 生态模块：eventloop、green、devices、log 与 utils

## 核心理解

pyzmq 核心（sugar + backend）之外，还提供了一组生态模块解决特定集成场景：与 tornado IOLoop 的历史集成、与 gevent 协程的适配、消息代理设备（devices）、通过 PUB socket 发布 Python 日志的 handler，以及 JSON/字符串工具。这些模块不是消息传递的核心，但展示了 pyzmq 如何通过子类覆写和 mixin 组合适配不同的并发模型和应用场景。

理解这些模块有助于为特定运行时选择正确的 pyzmq 使用方式，并理解 pyzmq 异步适配的演进路径——从 tornado 回调到 asyncio 原生协程，再到 gevent 猴子补丁风格。

## eventloop：tornado 集成

### F-106：废弃的 IOLoop 与保留的 ZMQStream

`zmq.eventloop` 自 pyzmq 17 起大部分废弃：

```python
# zmq/eventloop/ioloop.py
from tornado.ioloop import IOLoop
ZMQIOLoop = IOLoop  # 直接别名，不再有自定义实现
```

历史上 pyzmq 需要自定义 `ZMQIOLoop` 来把 ZeroMQ 的 FD 集成到 tornado IOLoop。tornado 原生支持 `add_handler` 后，pyzmq 不再需要自定义 IOLoop。

**ZMQStream** 仍保留，用于基于 tornado IOLoop 的回调式消息收发：

```python
from zmq.eventloop import ioloop, zmqstream

stream = zmqstream.ZMQStream(socket, io_loop=ioloop.IOLoop.current())
stream.on_recv(lambda msg: print("收到:", msg))
stream.send_multipart([b"hello"])
```

ZMQStream 的构造时若传入 `_AsyncSocket` 子类（Future 风格），会发 RuntimeWarning 并 shadow 回基础 `zmq.Socket`——因为 ZMQStream 是回调风格而非 Future 风格，不能混用。

### F-107：tornado Future 版异步 Socket

`zmq.eventloop.future` 提供 tornado 版异步 API：

```python
from zmq.eventloop.future import Context, Socket, Poller

async def fetch():
    ctx = Context()
    sock = ctx.socket(zmq.REQ)
    sock.connect("tcp://localhost:5555")
    await sock.send(b"request")
    reply = await sock.recv()
```

**`_AsyncTornado` mixin**：

| 抽象点 | tornado 版 | asyncio 版对比 |
|--------|-----------|---------------|
| `_Future` | `_TornadoFuture`（恢复 cancel 能力） | `asyncio.Future` |
| `_READ/_WRITE` | `IOLoop.READ/WRITE` | `selectors.EVENT_READ/WRITE` |
| `_default_loop()` | `IOLoop.current()` | `asyncio.get_running_loop()` |

核心状态机（`_future._AsyncSocket`）完全复用，详见 [异步与 asyncio](05-async-future-asyncio.md)。

## green：gevent 适配

### F-108：猴子补丁风格

`zmq.green` 通过 `import zmq.green as zmq` 使用，提供与标准 pyzmq 相同的 API，但 send/recv 在 EAGAIN 时自动让出当前 greenlet 而非阻塞 OS 线程：

```python
import zmq.green as zmq  # 替换 import zmq

ctx = zmq.Context()
sock = ctx.socket(zmq.REP)
sock.bind("tcp://*:5555")

# 看起来是同步阻塞，但实际在 EAGAIN 时让出 greenlet
while True:
    msg = sock.recv_string()  # 不阻塞 OS 线程
    sock.send_string("reply")
```

**内部结构**：

- `_Context` 继承 `zmq.Context`，设 `_socket_class = _Socket`，重置 `_instance`
- `_Socket` 覆写 `send`/`recv`/`recv_into`/`send_multipart`/`recv_multipart`/`get`/`set`
- 覆写方法用 gevent `AsyncResult` 在 EAGAIN 时让出当前 greenlet

### F-109：FD 监听与让出机制

`_Socket` 用 gevent hub 的 loop 监听 zmq FD：

```python
get_hub().loop.io(socket.FD, 1)  # 1 = 读事件
```

`__state_changed` 回调查询 `EVENTS` 选项并设置 `__readable`/`__writable` AsyncResult：

```
sock.recv()
  │
  ├─ DONTWAIT 非阻塞 recv
  │   ├─ 成功 → 返回消息
  │   └─ EAGAIN → _wait_read()
  │       ├─ 监听 socket.FD 读事件
  │       ├─ AsyncResult.wait() → 让出 greenlet
  │       └─ 可读时回调设置 AsyncResult → 唤醒 greenlet
  │
  └─ 重试 recv（循环直到成功或超时）
```

### F-110：green Poller

`_Poller` 覆写 `poll`：
1. 先非阻塞 `super().poll(0)` 尝试取事件
2. 无事件时用 gevent `select.select` 等待 FD
3. 带 1.33 秒超时兜底（规避 gevent select 的已知 bug）
4. 避免阻塞整个 OS 线程

与 `zmq.Poller` API 完全兼容，可直接替换。

### 三种并发模型对比

| 特性 | 同步 | asyncio | gevent |
|------|------|---------|--------|
| 导入 | `import zmq` | `import zmq.asyncio` | `import zmq.green as zmq` |
| 阻塞行为 | 阻塞 OS 线程 | await 让出事件循环 | 让出 greenlet |
| API 风格 | 同步调用 | `await` 协程 | 同步调用（看起来） |
| Future | 无 | `asyncio.Future` | 无（用 AsyncResult） |
| 多核利用 | 多进程/多线程 | 单线程并发 | 单线程多 greenlet |
| 猴子补丁 | 不需要 | 不需要 | 需要（gevent.monkey.patch_all） |

## devices：消息代理设备

### F-111：Device 基类

`zmq.devices.Device` 是消息代理（queue/forwarder/streamer）的配置式封装：

```python
from zmq.devices import ThreadDevice

dev = ThreadDevice(zmq.FORWARDER, zmq.SUB, zmq.PUB)
dev.setsockopt_in(zmq.SUBSCRIBE, b"")
dev.bind_in("tcp://*:5555")
dev.bind_out("tcp://*:5556")
dev.start()  # 后台线程运行
```

Device 接受**套接字类型**（而非实例），通过方法排队配置：

| 方法 | 说明 |
|------|------|
| `bind_in(addr)` | 前端 socket bind 地址 |
| `connect_in(addr)` | 前端 socket connect 地址 |
| `setsockopt_in(opt, val)` | 前端 socket 选项 |
| `bind_out(addr)` | 后端 socket bind 地址 |
| `connect_out(addr)` | 后端 socket connect 地址 |
| `setsockopt_out(opt, val)` | 后端 socket 选项 |

`_setup_sockets` 在运行时创建 Context 和两个 Socket，`run_device` 调用 `zmq.proxy(ins, outs)`。

### F-112：ThreadDevice 与 ProcessDevice

| 类 | 运行方式 | Context 工厂 |
|----|---------|-------------|
| `ThreadDevice` | `threading.Thread` 后台线程 | `Context.instance()` |
| `ProcessDevice` | `multiprocessing.Process` 子进程 | `Context`（新实例，非单例） |

ProcessDevice 使用 `context_factory = Context`（而非 `Context.instance`），因为 fork 后子进程不能复用父进程的 Context 单例（文件描述符状态不一致）。

### F-113：Proxy 设备（带监控）

`ProxyBase` 在 Device 基础上增加第三个监控 socket：

```python
from zmq.devices import ThreadProxy

proxy = ThreadProxy(zmq.QUEUE, zmq.ROUTER, zmq.DEALER, zmq.PUB)
proxy.bind_in("tcp://*:5555")
proxy.bind_out("tcp://*:5556")
proxy.bind_mon("tcp://*:5557")  # 监控端点
proxy.start()
```

监控 socket（`mon_type`，默认 PUB）可捕获经过代理的所有消息。配置方法增加：
- `bind_mon(addr)` / `connect_mon(addr)` / `setsockopt_mon(opt, val)`

`run_device` 调用 `zmq.proxy(ins, outs, mons)` 三参数版本。

类继承组合：

```
ProxyBase
├── Proxy(ProxyBase, Device)
├── ThreadProxy(ProxyBase, ThreadDevice)
└── ProcessProxy(ProxyBase, ProcessDevice)
```

## log：通过 PUB socket 发布日志

### F-114：PUBHandler

`PUBHandler` 继承 `logging.Handler`，将 Python 标准日志通过 ZeroMQ PUB socket 发布：

```python
import logging
from zmq.log.handlers import PUBHandler

pub = ctx.socket(zmq.PUB)
pub.bind("tcp://*:5555")

handler = PUBHandler(pub)
handler.setFormatter(logging.Formatter('%(message)s'))
logger = logging.getLogger("zmq")
logger.addHandler(handler)
logger.setLevel(logging.INFO)

logger.info("server started")
# 发布两帧 multipart：
# [b"server.INFO", b"server started"]
```

**构造方式**：
- 接受已有 PUB socket
- 或接受地址字符串（内部创建 Context + PUB socket 并 bind）

**emit 格式**：每条日志发布为两帧 multipart 消息：
- **第一帧（主题）**：`[root_topic.]LEVEL[.subtopic]`，如 `myserver.INFO.auth`
- **第二帧（消息体）**：格式化后的日志文本

订阅者可按级别或主题前缀订阅：

```python
sub.connect("tcp://localhost:5555")
sub.subscribe(b"INFO")   # 只收 INFO 级别
sub.subscribe(b"ERROR")  # 只收 ERROR 级别
```

### F-115：按级别格式化

`PUBHandler.formatters` 是按日志级别映射到不同 Formatter 的字典：

```python
handler.formatters = {
    logging.DEBUG: logging.Formatter('DEBUG: %(message)s'),
    logging.INFO: logging.Formatter('%(message)s'),
    logging.WARN: logging.Formatter('WARN: %(message)s'),
    logging.ERROR: logging.Formatter('ERROR: %(name)s: %(message)s'),
    logging.CRITICAL: logging.Formatter('CRITICAL: %(message)s'),
}

# 设置某一级别的格式
handler.setFormatter(error_formatter, level=logging.ERROR)

# 不指定 level 则设置所有级别
handler.setFormatter(default_formatter)
```

### F-116：TopicLogger

`TopicLogger` 继承 `logging.Logger`，扩展了主题支持：

```python
from zmq.log.handlers import TopicLogger

logger = TopicLogger("zmq")
logger.log(logging.INFO, "auth", "user %s logged in", username)
# 内部：topic + "::" + msg → PUBHandler 解析
# 发布主题：INFO.auth
```

所有 log 方法签名变为 `(level, topic, msg, ...)`。内部把 `topic + "::" + msg` 传给基类方法，PUBHandler 的 `emit` 用 `str(record.msg).split("::", 1)` 解析出子主题。这允许在日志消息中携带 ZeroMQ 主题前缀。

## utils：工具模块

### F-117：jsonapi

`zmq.utils.jsonapi` 是标准库 json 的轻量封装：

```python
from zmq.utils import jsonapi

data = jsonapi.dumps({"key": "value"})  # bytes（UTF-8 编码）
obj = jsonapi.loads(data)               # 接受 bytes 或 str
```

| 函数 | 实现 | 返回 |
|------|------|------|
| `dumps(o, **kwargs)` | `json.dumps(o, **kwargs).encode("utf8")` | `bytes` |
| `loads(s, **kwargs)` | bytes 先 utf8 解码再 `json.loads` | Python 对象 |

pyzmq 22.2 起不再尝试可选 JSON 库（如 simplejson、ujson），无条件使用标准库 `json`。这是 `Socket.send_json`/`recv_json`（F-038/F-039）的底层序列化器。

### F-118：strtypes（已废弃）

`zmq.utils.strtypes` 自 pyzmq 23 起废弃，提供 Python 2/3 兼容的字符串转换：

```python
from zmq.utils.strtypes import cast_bytes, cast_unicode, b, u

b("hello")  # bytes: b"hello"
u("hello")  # str: "hello"
```

模块显式声明了兼容别名：
- `bytes = bytes`
- `unicode = str`
- `basestring = (str,)`

这些在 Python 3 中是无操作（no-op），仅为兼容旧代码保留。新代码应直接使用 `str.encode()`/`bytes.decode()`。

## 模块选择指南

| 场景 | 推荐模块 |
|------|---------|
| 现代 asyncio 应用 | `zmq.asyncio` |
| 已有 tornado 应用 | `zmq.eventloop.future` 或 `ZMQStream` |
| gevent 应用 | `zmq.green as zmq` |
| 构建消息代理 | `zmq.devices.ThreadDevice/ThreadProxy` |
| 分布式日志收集 | `zmq.log.handlers.PUBHandler` |
| 简单同步应用 | 核心 `zmq`（不需要生态模块） |

## 相关概念

- [异步与 asyncio](05-async-future-asyncio.md) — asyncio 和 tornado future 的核心状态机
- [Socket sugar 语法层](02-socket-sugar.md) — send_json/recv_json 使用 jsonapi
- [整体架构与双后端](00-architecture-dual-backend.md) — 后端选择与 public_api 契约
- [Context 生命周期](01-context-lifecycle.md) — ProcessDevice 的 fork 安全 Context
- [常量枚举参考](../references/constants-enums.md) — DeviceType 枚举（QUEUE/FORWARDER/STREAMER）
