---
type: example
title: "同步 PUB/SUB 发布订阅完整示例"
description: "使用 zmq.Context 单例、PUB/SUB 套接字、bind/connect、subscribe 主题订阅、send_string/recv、Poller 超时轮询实现同步发布订阅模式，含优雅关闭"
tags: [pyzmq, example, pubsub, sync, poller, context]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [../references/constants-enums.md, ../references/attrsettr-options.md]
  facts: [F-015, F-018, F-024, F-025, F-029, F-034, F-035, F-040, F-050, F-051, F-053]
---

# 同步 PUB/SUB 发布订阅完整示例

## 概述

本示例演示 pyzmq 最常用的 **PUB/SUB（发布-订阅）** 模式：一个发布者绑定端口并周期性发布带主题的消息，多个订阅者连接并按主题前缀过滤接收。使用同步 API 和 `Poller` 实现带超时的消息轮询，展示了 Context 单例、socket 上下文管理器、属性式选项设置和优雅关闭。

## 完整代码

### 发布者（publisher.py）

```python
import time
import zmq


def publisher():
    context = zmq.Context.instance()

    publish_socket = context.socket(zmq.PUB)
    publish_socket.linger = 0
    publish_socket.bind("tcp://*:5555")

    time.sleep(0.5)

    topics = ["sports", "tech", "weather"]
    count = 0

    try:
        while count < 20:
            topic = topics[count % len(topics)]
            message = f"{topic} update #{count}"
            publish_socket.send_string(message)
            print(f"[发布] {message}")
            count += 1
            time.sleep(0.5)
    finally:
        publish_socket.close()
        context.destroy(linger=0)


if __name__ == "__main__":
    publisher()
```

### 订阅者（subscriber.py）

```python
import zmq


def subscriber(topic_filter=b""):
    context = zmq.Context.instance()

    subscribe_socket = context.socket(zmq.SUB)
    subscribe_socket.linger = 0
    subscribe_socket.connect("tcp://localhost:5555")
    subscribe_socket.subscribe(topic_filter)

    poller = zmq.Poller()
    poller.register(subscribe_socket, zmq.POLLIN)

    received = 0

    try:
        while received < 10:
            events = dict(poller.poll(timeout=2000))

            if subscribe_socket in events:
                message = subscribe_socket.recv_string()
                topic, _, content = message.partition(" ")
                print(f"[订阅] 主题={topic}, 内容={content}")
                received += 1
            else:
                print("[订阅] 等待消息超时（2秒）...")
    finally:
        poller.unregister(subscribe_socket)
        subscribe_socket.close()
        context.destroy(linger=0)


if __name__ == "__main__":
    import sys
    topic = sys.argv[1].encode("utf-8") if len(sys.argv) > 1 else b""
    subscriber(topic)
```

## 运行说明

1. **启动订阅者**（先启动，避免丢失早期消息）：

   ```bash
   python subscriber.py
   # 或订阅特定主题：
   python subscriber.py tech
   ```

2. **启动发布者**：

   ```bash
   python publisher.py
   ```

3. **多订阅者**：可在不同终端启动多个 subscriber.py，每个独立接收发布者的消息扇出副本。

4. **预期输出**：

   ```
   [发布] sports update #0
   [发布] tech update #1
   [发布] weather update #2
   ...
   ```

   订阅者端：

   ```
   [订阅] 主题=sports, 内容=update #0
   [订阅] 主题=tech, 内容=update #1
   ...
   ```

## 原理解析

### 1. Context 单例

```python
context = zmq.Context.instance()
```

`Context.instance()` 返回全局单例 Context（F-015）。发布者和订阅者可以共享同一 Context（如果在同一进程中），也可以各自创建。单例内部使用双重检查锁，并在 fork 后自动重建。

### 2. linger = 0

```python
publish_socket.linger = 0
```

通过属性赋值设置 LINGER 选项（F-027/F-059）。`linger=0` 表示关闭 socket 时不等待挂起消息发送完成，立即关闭。这避免了进程退出时因未发送消息导致的无限阻塞。详见 [attrsettr 选项系统](/references/attrsettr-options.md)。

### 3. bind 与 connect

```python
publish_socket.bind("tcp://*:5555")      # 发布者绑定
subscribe_socket.connect("tcp://localhost:5555")  # 订阅者连接
```

PUB/SUB 模式中：
- **PUB 端**通常 `bind`（监听端口）
- **SUB 端**通常 `connect`（发起连接）
- 一个 PUB 可被多个 SUB 连接，消息自动扇出

### 4. 主题订阅

```python
subscribe_socket.subscribe(topic_filter)
```

`subscribe(topic)` 方法接受 bytes 或 str，str 自动编码为 utf8（F-029）。空前缀 `b""` 订阅所有消息。订阅是**前缀匹配**——订阅 `b"tech"` 会匹配 `b"tech"`、`b"technology"` 等以 "tech" 开头的主题。

### 5. send_string / recv_string

```python
publish_socket.send_string(message)
message = subscribe_socket.recv_string()
```

`send_string` 将 str 编码为 UTF-8 bytes 后发送（F-034）；`recv_string` 接收 bytes 后解码为 str（F-035）。底层仍然是 bytes 传输，这两个方法只是便捷封装。

消息格式为 `"topic content"`，订阅者用 `partition(" ")` 分离主题和内容。生产环境建议使用 multipart 消息（`send_multipart([b"topic", b"content"])`）以避免主题中的空格歧义。

### 6. Poller 超时轮询

```python
poller = zmq.Poller()
poller.register(subscribe_socket, zmq.POLLIN)

events = dict(poller.poll(timeout=2000))
if subscribe_socket in events:
    message = subscribe_socket.recv_string()
else:
    print("超时...")
```

- `Poller` 注册订阅者 socket，关注 `POLLIN`（可读）事件（F-051）
- `poll(timeout=2000)` 等待最多 2000 毫秒（F-053）
- `dict(poller.poll())` 将结果转为 `{socket: event_mask}` 字典
- 超时返回空字典，允许程序执行周期性检查或优雅退出

### 7. 优雅关闭

```python
try:
    ...
finally:
    poller.unregister(subscribe_socket)
    subscribe_socket.close()
    context.destroy(linger=0)
```

- `finally` 块确保资源释放
- `close()` 关闭 socket
- `context.destroy(linger=0)` 关闭所有由该 Context 创建的 socket 并终止 Context（F-017）

## 关键事实溯源

本示例使用的 API 均来自事实清单：

| API | 事实编号 | 说明 |
|-----|---------|------|
| `zmq.Context.instance()` | F-015 | 全局单例 Context |
| `context.socket(type)` | F-018 | 创建 socket，应用默认选项 |
| `socket.bind(addr)` | F-024 | 绑定端点，返回上下文管理器 |
| `socket.connect(addr)` | F-025 | 连接端点 |
| `socket.subscribe(topic)` | F-029 | 订阅主题，str 自动编码 |
| `socket.send_string(u)` | F-034 | 发送字符串 |
| `socket.recv_string()` | F-035 | 接收字符串 |
| `socket.poll(timeout)` | F-040 | 单 socket 轮询 |
| `zmq.Poller()` | F-050 | 创建多路复用轮询器 |
| `poller.register(s, flags)` | F-051 | 注册 socket 和事件 |
| `poller.poll(timeout)` | F-053 | 轮询等待事件 |

## 扩展练习

1. **multipart 主题**：将消息改为 `send_multipart([topic_bytes, content_bytes])`，订阅者用 `recv_multipart()` 接收，避免空格歧义。
2. **多主题订阅**：在一个 SUB socket 上多次调用 `subscribe()` 订阅多个主题。
3. **XPUB/XSUB**：尝试使用 `zmq.XPUB`/`zmq.XSUB` 构建中间代理，动态感知订阅变化。
4. **监控**：使用 `get_monitor_socket()` 监控连接事件，打印连接/断开日志。

## 相关概念

- [Context 生命周期](/concepts/01-context-lifecycle.md) — 单例、destroy、linger
- [Socket sugar 语法层](/concepts/02-socket-sugar.md) — send_string/subscribe/bind 详解
- [Poller 多路复用](/concepts/04-poller.md) — Poller 完整 API
- [attrsettr 选项系统](/references/attrsettr-options.md) — linger 属性赋值原理
- [常量枚举参考](/references/constants-enums.md) — PUB/SUB/POLLIN 常量
- [asyncio PUSH/PULL 示例](asyncio-pushpull.md) — 异步版本示例
