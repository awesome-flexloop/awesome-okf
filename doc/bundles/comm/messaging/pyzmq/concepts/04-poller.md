---
type: concept
title: "Poller 多路复用与 select 兼容"
description: "pyzmq Poller 的 register/modify/unregister 管理、POLLIN/POLLOUT/POLLERR 事件位掩码、zmq_poll 后端调用、原生 fd 支持、select() 兼容封装、字典转换与超时处理"
tags: [pyzmq, zeromq, poller, poll, multiplexing, select]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [../references/constants-enums.md]
  facts: [F-050, F-051, F-052, F-053, F-054]
---

# Poller 多路复用与 select 兼容

## 核心理解

`zmq.Poller` 是 pyzmq 对 ZeroMQ `zmq_poll` 多路复用函数的面向对象封装。它允许在单个线程中同时等待多个 socket（以及原生文件描述符）的可读/可写事件，是构建高性能 ZeroMQ 应用的核心组件——比为每个 socket 创建阻塞线程高效得多。

Poller 的 API 设计模仿了 Python 标准库的 `select.poll`，但额外支持 ZeroMQ socket。pyzmq 还提供了 `zmq.select` 函数，完全兼容 `select.select()` 的三元组接口，使从标准库 select 迁移到 zmq_poll 几乎零成本。

## Poller 内部结构

### F-050：初始化

```python
class Poller:
    def __init__(self):
        self.sockets = []   # list of (socket, flags) 元组
        self._map = {}       # socket → sockets 列表中的索引
```

两个数据结构配合实现 O(1) 查找：

| 数据结构 | 类型 | 用途 |
|---------|------|------|
| `self.sockets` | `list[tuple]` | 有序的 `(socket, flags)` 列表，直接传给后端 `zmq_poll` |
| `self._map` | `dict` | socket → 索引的映射，用于快速查找、更新和注销 |

`sockets` 列表保持有序是因为后端 `zmq_poll` 接受数组指针；`_map` 字典使 `register`/`modify`/`unregister` 不需要线性扫描。

## 注册与管理

### F-051：register

```python
poller.register(socket, flags=zmq.POLLIN | zmq.POLLOUT)
```

**参数**：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `socket` | `zmq.Socket \| 有 fileno() 的对象` | — | 要注册的 zmq socket 或原生 fd |
| `flags` | `int`（PollEvent 位掩码） | `POLLIN \| POLLOUT` | 关注的事件类型 |

**行为**：

- flags 非零：如果 socket 已注册则更新 flags，否则追加到列表
- flags 为 0：等价于 `unregister(socket)`（注销）

**事件标志**：

| 标志 | 值 | 含义 |
|------|----|------|
| `zmq.POLLIN` | 1 | 可读事件（有消息可接收） |
| `zmq.POLLOUT` | 2 | 可写事件（可发送消息） |
| `zmq.POLLERR` | 4 | 错误事件 |

可组合使用：`zmq.POLLIN | zmq.POLLOUT` 同时关注读写。

**原生 fd 支持**：Poller 不仅支持 zmq.Socket，任何有 `fileno()` 方法返回文件描述符的对象都可注册（如原生 TCP socket、pipe、eventfd 等）。这使得可以在同一个 poll 循环中混合处理 ZeroMQ 消息和传统 I/O。

### F-052：modify 与 unregister

```python
# 修改关注的事件
poller.modify(socket, zmq.POLLIN)

# 注销 socket
poller.unregister(socket)
```

- `modify(socket, flags)` 直接委托给 `register(socket, flags)`，是语义别名
- `unregister(socket)` 从 `_map` 弹出索引后，需要把 `sockets` 列表中后续元素的索引整体减 1，以保持 `_map` 的一致性

```python
def unregister(self, socket):
    idx = self._map.pop(socket)
    self.sockets.pop(idx)
    # 后续元素索引减 1
    for i in range(idx, len(self.sockets)):
        s, f = self.sockets[i]
        self._map[s] = i
```

## 轮询

### F-053：poll 方法

```python
events = poller.poll(timeout=None)
```

**参数**：

| timeout 值 | 行为 |
|-----------|------|
| `None` 或负值 | 无限等待，直到有事件 |
| `0` | 非阻塞，立即返回当前就绪事件 |
| 正数（float/int） | 等待指定毫秒数后超时 |

float 会被转为 int（毫秒）。内部调用后端 `zmq_poll(self.sockets, timeout=timeout)`。

**返回值**：`[(socket, event_mask), ...]` 列表，每个元素是就绪的 socket 和实际触发的事件位掩码：

```python
poller = zmq.Poller()
poller.register(sub, zmq.POLLIN)
poller.register(pub, zmq.POLLOUT)

events = dict(poller.poll(timeout=1000))

if sub in events and events[sub] & zmq.POLLIN:
    msg = sub.recv_string()
if pub in events and events[pub] & zmq.POLLOUT:
    pub.send_string("data")
```

`dict(poller.poll())` 是惯用法，将结果转为 `{socket: event_mask}` 字典方便查询。返回空列表/空字典表示超时。

### 典型事件循环

```python
poller = zmq.Poller()
poller.register(receiver, zmq.POLLIN)
poller.register(control, zmq.POLLIN)

while True:
    events = dict(poller.poll(timeout=1000))
    if not events:
        print("超时，检查中...")
        continue
    for sock in events:
        if sock is receiver:
            data = sock.recv_string()
            process(data)
        elif sock is control:
            cmd = sock.recv_string()
            if cmd == "stop":
                break
```

## select 兼容封装

### F-054：zmq.select

```python
read_ok, write_ok, err_ok = zmq.select(rlist, wlist, xlist, timeout=None)
```

完全兼容 Python 标准库 `select.select()` 的接口：

| 参数 | 说明 |
|------|------|
| `rlist` | 等待可读的对象列表 |
| `wlist` | 等待可写的对象列表 |
| `xlist` | 等待错误的对象列表 |
| `timeout` | 超时时间（秒，与标准库一致） |
| **返回** | `(read_ready, write_ready, error_ready)` 三元组 |

与标准库 `select.select()` 的区别：

1. **支持 zmq.Socket**：标准库 select 不支持 ZeroMQ socket，`zmq.select` 支持
2. **超时单位**：标准库 select 也是秒，`zmq.select` 保持一致（内部将秒转为毫秒传给 `zmq_poll`）
3. **底层实现**：使用 `zmq_poll` 而非操作系统的 select/poll/epoll，因此在 ZeroMQ socket 上行为更正确

**内部实现**：

1. 将秒级 timeout 转为毫秒
2. 合并三个列表，为每个对象构造 flags（rlist→POLLIN，wlist→POLLOUT，xlist→POLLERR）
3. 构造临时 Poller 并调用 `zmq_poll`
4. 将结果按 POLLIN/POLLOUT/POLLERR 拆分回三个列表

```python
import zmq

# 从标准库 select 迁移只需改 import：
# from select import select
# 改为：
from zmq import select

readable, writable, errors = select([sock1, sock2], [sock3], [], timeout=5.0)
```

这使得已有使用 `select.select()` 的代码可以几乎零修改地获得 ZeroMQ socket 支持。

## Poller vs socket.poll

pyzmq 提供两个层级的轮询 API：

| API | 适用场景 | 底层 |
|-----|---------|------|
| `socket.poll(timeout, flags)` | 只等单个 socket | 内部创建临时 Poller（F-040） |
| `zmq.Poller` | 同时等多个 socket | 直接调用 `zmq_poll` |
| `zmq.select` | select.select 兼容接口 | 临时 Poller + 结果拆分 |

单 socket 场景用 `socket.poll` 更简洁；多 socket 场景应使用 `Poller`。

## 与异步 Poller 的关系

同步 `zmq.Poller` 是所有异步 Poller 的基类：

- `zmq.asyncio.Poller` 继承 `zmq.Poller`，覆写 `poll()` 返回 awaitable（F-073）
- `zmq.eventloop.future.Poller` 是 tornado 版异步 Poller（F-107）
- `zmq.green._Poller` 覆写 `poll()` 用 gevent 让出 greenlet（F-110）

异步 Poller 复用同步 Poller 的 `sockets`/`_map` 数据结构和 `register`/`modify`/`unregister` 方法，只改变等待机制。详见 [异步与 asyncio](/concepts/05-async-future-asyncio.md)。

## 注意事项

1. **FD 是边缘触发的**：`socket.fileno()` 返回的 FD 是 edge-triggered（边缘触发），但 Poller 内部使用的 `zmq_poll` 是 level-triggered（水平触发）的。直接用 `fileno()` 做外部事件循环集成时需注意消费事件。
2. **Poller 不是线程安全的**：不应在多线程中并发操作同一个 Poller。
3. **socket 关闭后自动移除**：关闭的 socket 在下次 poll 时会被自动跳过。
4. **超时精度**：timeout 是毫秒级整数，float 会被截断。

## 相关概念

- [Socket sugar 语法层](/concepts/02-socket-sugar.md) — socket.poll() 单 socket 便捷方法
- [异步与 asyncio](/concepts/05-async-future-asyncio.md) — asyncio.Poller 的 awaitable poll
- [生态：eventloop/green/devices/log](/concepts/07-ecosystem-eventloop-green-devices-log.md) — green._Poller 的 gevent 适配
- [常量枚举参考](/references/constants-enums.md) — PollEvent 标志定义
