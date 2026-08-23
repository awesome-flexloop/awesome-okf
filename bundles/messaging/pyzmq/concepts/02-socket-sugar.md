---
type: concept
title: "Socket 与 sugar 语法层"
description: "pyzmq Socket 的 bind/connect 上下文管理器、send/recv 的 flags/copy/track 参数、多帧消息、字符串/JSON/pickle 序列化、订阅机制、轮询、监控套接字、随机端口、hwm 与装饰器"
tags: [pyzmq, zeromq, socket, sugar, send, recv, serialize, monitor]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [../references/attrsettr-options.md, ../references/constants-enums.md, ../references/error-hierarchy.md]
  facts: [F-022, F-023, F-024, F-025, F-026, F-027, F-028, F-029, F-030, F-031, F-032, F-033, F-034, F-035, F-036, F-037, F-038, F-039, F-040, F-041, F-042, F-043, F-044, F-045, F-096, F-097]
---

# Socket 与 sugar 语法层

## 核心理解

`zmq.Socket` 是用户与 ZeroMQ 交互的主要接口。sugar 层的 Socket 类继承自后端 C 扩展基类，在薄绑定之上叠加了丰富的 Pythonic 功能：上下文管理器、自动序列化（字符串/JSON/pickle）、多帧消息便捷方法、属性式选项访问、订阅语法糖、内置轮询、套接字监控和随机端口绑定。这些功能使 pyzmq 的 Socket 远比裸 C API 易用，同时保持了零抽象泄漏——高级方法最终都通过 `super()` 调用后端的 `send`/`recv`/`set`/`get`。

## Socket 类层次与创建

### F-022、F-023：类结构与初始化

```python
class Socket(
    zmq.backend.Socket,        # C 扩展基类
    AttributeSetter,            # 动态选项属性
    Generic[_SocketReturnT_co], # 泛型协变返回类型
):
    _repr_cls = "zmq.Socket"
```

Socket 支持三种创建形态：

```python
# 形态一：通过 Context 创建（最常用）
sock = ctx.socket(zmq.PUB)

# 形态二：shadow 已有 socket 的底层地址
sock2 = zmq.Socket(shadow=other_sock.underlying)

# 形态三：shadow 另一个 Socket 实例（保留 context 引用）
sock3 = zmq.Socket(other_sock)
```

初始化后，Socket 通过 `self.get(zmq.TYPE)` 查询实际类型并设置 `_type_name`，用于 repr 显示。

### F-026：上下文管理器

```python
with ctx.socket(zmq.REP) as sock:
    sock.bind("tcp://*:5555")
    msg = sock.recv_string()
# 退出时自动调用 sock.close()
```

## bind 与 connect

### F-024、F-025：上下文管理器式绑定

`bind(addr)` 和 `connect(addr)` 都返回 `_SocketContext` 上下文管理器，退出时自动 unbind/disconnect：

```python
# 手动管理
sock.bind("tcp://*:5555")
sock.unbind("tcp://*:5555")

# 上下文管理器（自动 unbind）
with sock.bind("tcp://*:5555"):
    # 在此端口上工作
    ...
# 退出 with 块时自动 unbind

# connect 同理
with sock.connect("tcp://localhost:5555"):
    ...
# 退出时自动 disconnect
```

`_SocketContext` 通过 `LAST_ENDPOINT` 获取实际绑定地址，以支持端口 0（随机端口）：

```python
with sock.bind("tcp://127.0.0.1:0") as endpoint:
    print(endpoint)  # 实际绑定的地址，如 tcp://127.0.0.1:52341
```

### F-043：bind_to_random_port

```python
port = sock.bind_to_random_port(
    "tcp://127.0.0.1",
    min_port=49152,
    max_port=65536,
    max_tries=100,
)
```

在默认范围内，通过绑定 `addr:*` 让操作系统选择端口并从 `LAST_ENDPOINT` 解析实际端口号。指定范围时则随机尝试端口，遇到 `EADDRINUSE` 或 Windows 上的 `EACCES` 重试，超过 `max_tries` 抛 `ZMQBindError`。

## 消息发送与接收

### F-031：send 核心方法

```python
Socket.send(
    data,           # bytes / Frame / buffer-protocol 对象
    flags=0,        # 0 / NOBLOCK / SNDMORE
    copy=True,      # True=复制数据；False=zero-copy
    track=False,    # True=返回 MessageTracker
    routing_id=None,  # SERVER 套接字（draft）
    group=None,     # RADIO 套接字（draft）
)
```

**返回值**：

| 条件 | 返回类型 |
|------|---------|
| `copy=True`（默认） | `None` |
| `copy=False` 且 `track=False` | `None` |
| `copy=False` 且 `track=True` | `MessageTracker` |
| 传入 Frame 对象 | `MessageTracker`（受 track 参数影响） |

**flags 参数**：

| 标志 | 值 | 说明 |
|------|----|------|
| `0` | 0 | 阻塞模式（默认） |
| `zmq.NOBLOCK` / `zmq.DONTWAIT` | 1 | 非阻塞，无法发送时抛 `Again`（EAGAIN） |
| `zmq.SNDMORE` | 2 | 标记后续还有更多帧 |

非 Frame 数据会被自动包装成 Frame 后发送。当 `copy=False` 但消息小于 `COPY_THRESHOLD`（64KB）时，后端自动切换到 copy 路径并返回 `_FINISHED_TRACKER`。

### F-033：recv 核心方法

```python
data = sock.recv(flags=0, copy=True, track=False)
```

返回值取决于 `copy`：`copy=True` 返回 `bytes`，`copy=False` 返回 `Frame`。

### F-032、F-033：多帧消息

```python
# 发送多帧消息
sock.send_multipart([b"topic", b"message part 1", b"message part 2"])

# 接收多帧消息
parts = sock.recv_multipart()  # [b"topic", b"message part 1", b"message part 2"]
```

`send_multipart` 对除最后一部分外的所有 part 加 `SNDMORE` 标志发送。`recv_multipart` 先 recv 第一部分，然后循环检查 `getsockopt(zmq.RCVMORE)` 直到没有更多部分。

## 序列化便捷方法

### F-034、F-035：字符串

```python
sock.send_string("hello", encoding="utf-8")
text = sock.recv_string(encoding="utf-8")
```

`send_string` 校验输入为 str 后编码为 bytes 发送。`recv_string` 接收后解码。别名 `send_unicode`/`recv_unicode`。

### F-038、F-039：JSON

```python
sock.send_json({"key": "value", "count": 42})
obj = sock.recv_json()
```

使用 `zmq.utils.jsonapi` 进行序列化（标准库 json，UTF-8 编码）。`routing_id`/`group` 关键字参数被提取后透传给 `send`。

### F-036、F-037：Python 对象（pickle）

```python
sock.send_pyobj({"complex": object(), "list": [1, 2, 3]})
obj = sock.recv_pyobj()
```

使用 `pickle.dumps`/`pickle.loads`。`DEFAULT_PROTOCOL` 取 `pickle.DEFAULT_PROTOCOL`（旧版 Python 回退到 `pickle.HIGHEST_PROTOCOL`）。

> **安全警告**：pickle 反序列化不可信消息存在任意代码执行风险。只在完全信任消息来源时使用 `recv_pyobj()`。面向外部网络的应用应使用 JSON 或其他安全序列化格式。

### F-039：_deserialize 钩子

`_deserialize(recvd, load)` 是可被子类覆写的反序列化钩子。`_AsyncSocket` 覆写此方法以链式 Future（F-069），使 `await socket.recv_json()` 直接返回解析后的对象而非 bytes。

## 订阅机制

### F-028、F-029：四种等价订阅方式

```python
# 方式一：底层 set
sock.set(zmq.SUBSCRIBE, b"topic")

# 方式二：setsockopt 别名
sock.setsockopt(zmq.SUBSCRIBE, b"topic")

# 方式三：属性赋值
sock.subscribe = b"topic"

# 方式四：方法调用（接受 str 或 bytes）
sock.subscribe("topic")      # str 自动编码为 utf8
sock.subscribe(b"topic")
```

`subscribe(topic)`/`unsubscribe(topic)` 方法接受 str 或 bytes，str 自动编码为 utf8。属性赋值方式在 `__setattr__` 中被特判（大小写不敏感），字符串值自动编码。

空前缀订阅所有消息：

```python
sock.subscribe("")  # 或 sock.subscribe(b"")
```

## 选项访问

### F-027：三层等价访问

```python
# 第一层：set/get
sock.set(zmq.LINGER, 1000)
v = sock.get(zmq.LINGER)

# 第二层：setsockopt/getsockopt（直接别名）
sock.setsockopt(zmq.LINGER, 1000)
v = sock.getsockopt(zmq.LINGER)

# 第三层：属性访问
sock.linger = 1000
v = sock.linger
```

`setsockopt` 和 `getsockopt` 是后端 `set`/`get` 的直接别名，无任何包装。属性访问通过 `AttributeSetter` mixin 实现，详见 [attrsettr 选项系统](/references/attrsettr-options.md)。

### F-030：字符串选项

```python
sock.set_string(zmq.IDENTITY, "my-id", encoding="utf-8")
name = sock.get_string(zmq.IDENTITY, encoding="utf-8")
```

`set_string` 把 unicode 字符串编码后调 `self.set`；`get_string` 校验选项类型为 bytes 后解码。别名包括 `setsockopt_string`、`setsockopt_unicode` 等。

### F-044：hwm 便利属性

```python
sock.hwm = 1000  # 同时设置 SNDHWM 和 RCVHWM
v = sock.hwm      # getter 优先返回 SNDHWM，失败回退 RCVHWM
```

`hwm` 是 property，setter 同时设置发送和接收高水位标记；getter 优先返回发送高水位。

## 轮询

### F-040：Socket.poll 便捷方法

```python
events = sock.poll(timeout=1000, flags=zmq.POLLIN)
if events & zmq.POLLIN:
    msg = sock.recv(flags=zmq.NOBLOCK)
```

内部创建 `Poller` 实例，注册自身后 poll，返回事件位掩码。`timeout=None` 表示无限等待，`timeout=0` 表示非阻塞检查。返回 0 表示超时无事件。socket 已关闭时抛 `ZMQError(ENOTSUP)`。

多 socket 轮询应使用独立的 `zmq.Poller`，详见 [Poller 概念](/concepts/04-poller.md)。

## 套接字监控

### F-041、F-042：监控连接事件

```python
# 获取监控 socket（PAIR 类型）
monitor_sock = sock.get_monitor_socket(
    events=zmq.EVENT_ALL,        # 监控所有事件
    addr="inproc://monitor.s-1", # 自定义端点（可选）
)

# 在另一线程/循环中读取事件
while True:
    event = monitor_sock.recv_multipart()
    # event[0] = 事件帧（包含事件类型和关联值）
    # event[1] = 端点地址

# 禁用监控
sock.disable_monitor()
```

`get_monitor_socket` 要求 libzmq ≥4。默认端点为 `inproc://monitor.s-{FD}`，默认事件为 `EVENT_ALL`。内部调用 `self.monitor(addr, events)` 并创建一个 PAIR socket connect 到该端点。重复调用返回缓存的 `_monitor_socket`。

可监控的事件包括连接建立/延迟/重试、监听成功/失败、接受成功/失败、关闭/断开等，详见 [常量枚举参考](/references/constants-enums.md) 的 Event 部分。

## 文件描述符

### F-045：fileno()

```python
fd = sock.fileno()  # 返回 self.FD 的值
```

返回 edge-triggered（边缘触发）文件描述符，可用于集成到外部事件循环（`select`、`poll`、`epoll`、asyncio `add_reader` 等）。

> **重要**：FD 是边缘触发的——事件发生后必须消费（执行相应的 recv/send 操作），否则不会再次触发。这是 ZeroMQ 的设计特性，不是 bug。

## 装饰器

### F-096、F-097：@context 和 @socket

```python
@zmq.decorators.context()
def worker(ctx):
    """ctx 是自动创建的 Context，with 语句管理生命周期"""
    with ctx.socket(zmq.REP) as sock:
        sock.bind("tcp://*:5555")
        while True:
            msg = sock.recv_string()
            sock.send_string("reply")

@zmq.decorators.socket(zmq.PUB)
def publisher(pub, context=None):
    """pub 是自动创建的 PUB socket
    从函数参数查找 context，找不到则用 Context.instance()"""
    pub.send_string("news")
```

装饰器基于 `_Decorator` 通用工厂，wrapper 内用 `with target(*args, **kwargs) as obj` 创建对象并注入被装饰函数参数。

## 方法速查表

| 类别 | 方法 | 说明 |
|------|------|------|
| 连接 | `bind(addr)` / `unbind(addr)` | 绑定/解绑端点 |
| 连接 | `connect(addr)` / `disconnect(addr)` | 连接/断开端点 |
| 连接 | `bind_to_random_port(addr, ...)` | 绑定随机端口 |
| 发送 | `send(data, flags, copy, track)` | 核心发送 |
| 发送 | `send_multipart(parts, ...)` | 多帧发送 |
| 发送 | `send_string(u, ...)` | 字符串发送 |
| 发送 | `send_json(obj, ...)` | JSON 发送 |
| 发送 | `send_pyobj(obj, ...)` | pickle 发送 |
| 接收 | `recv(flags, copy, track)` | 核心接收 |
| 接收 | `recv_multipart(flags, ...)` | 多帧接收 |
| 接收 | `recv_string(flags)` | 字符串接收 |
| 接收 | `recv_json(flags)` | JSON 接收 |
| 接收 | `recv_pyobj(flags)` | pickle 接收 |
| 选项 | `set/get(option, value)` | 底层选项 |
| 选项 | `setsockopt/getsockopt(option)` | POSIX 别名 |
| 选项 | `set_string/get_string(option)` | 字符串选项 |
| 订阅 | `subscribe(topic)` / `unsubscribe(topic)` | 订阅/退订 |
| 监控 | `get_monitor_socket(events, addr)` | 获取监控 socket |
| 监控 | `disable_monitor()` | 禁用监控 |
| 轮询 | `poll(timeout, flags)` | 单 socket 轮询 |
| 其他 | `fileno()` | 获取文件描述符 |
| 其他 | `close()` | 关闭 socket |

## 相关概念

- [Context 生命周期](/concepts/01-context-lifecycle.md) — Socket 由 Context 创建并跟踪
- [Frame 与消息](/concepts/03-frame-message.md) — send/recv 的底层消息单元
- [Poller 多路复用](/concepts/04-poller.md) — 多 socket 事件轮询
- [异步与 asyncio](/concepts/05-async-future-asyncio.md) — Socket 的异步子类
- [attrsettr 选项系统](/references/attrsettr-options.md) — 属性访问的底层机制
- [常量枚举参考](/references/constants-enums.md) — SocketType/Flag/SocketOption 定义
- [错误层次结构](/references/error-hierarchy.md) — Again/ZMQBindError 等异常
