---
type: example
title: "asyncio PUSH/PULL 管道示例"
description: "使用 zmq.asyncio.Context 和 Socket 的 await send/recv 实现 PUSH/PULL 管道模式，与 asyncio.gather 集成并发处理任务，展示异步轮询和优雅关闭"
tags: [pyzmq, example, asyncio, pushpull, async, pipeline]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [../references/constants-enums.md, ../references/attrsettr-options.md]
  facts: [F-062, F-064, F-065, F-071, F-072, F-073, F-074]
---

# asyncio PUSH/PULL 管道示例

## 概述

本示例演示 pyzmq 的 **asyncio 集成**：使用 `zmq.asyncio.Context` 创建异步 Socket，`send`/`recv` 返回 `asyncio.Future`，可直接 `await`。采用 **PUSH/PULL（管道）** 模式构建一个简单的任务分发系统：一个 PUSH 端分发任务，多个 PULL worker 并发处理，与 `asyncio.gather` 集成实现并发。

## 完整代码

### ventilator（任务分发器）

```python
import asyncio
import zmq
import zmq.asyncio


async def ventilator(task_count: int = 20):
    ctx = zmq.asyncio.Context()
    sender = ctx.socket(zmq.PUSH)
    sender.linger = 0
    sender.bind("tcp://*:5557")

    sink = ctx.socket(zmq.PUSH)
    sink.linger = 0
    sink.connect("tcp://localhost:5558")

    await asyncio.sleep(0.3)

    print(f"[分发器] 开始发送 {task_count} 个任务")
    for task_id in range(task_count):
        workload = f"task-{task_id}"
        await sender.send_string(workload)
        print(f"[分发器] 已分发: {workload}")
        await sink.send_string(str(task_id))
        await asyncio.sleep(0.05)

    print("[分发器] 所有任务已分发")

    sender.close()
    sink.close()
    ctx.destroy(linger=0)


if __name__ == "__main__":
    asyncio.run(ventilator())
```

### worker（工作节点）

```python
import asyncio
import random
import zmq
import zmq.asyncio


async def worker(worker_id: int):
    ctx = zmq.asyncio.Context()
    receiver = ctx.socket(zmq.PULL)
    receiver.linger = 0
    receiver.connect("tcp://localhost:5557")

    print(f"[Worker-{worker_id}] 已启动，等待任务...")

    while True:
        try:
            task = await receiver.recv_string()
        except zmq.ContextTerminated:
            break

        print(f"[Worker-{worker_id}] 收到任务: {task}")

        process_time = random.uniform(0.1, 0.5)
        await asyncio.sleep(process_time)

        print(f"[Worker-{worker_id}] 完成任务: {task} (耗时 {process_time:.2f}s)")


async def run_workers(num_workers: int = 3):
    await asyncio.gather(*[worker(i) for i in range(num_workers)])


if __name__ == "__main__":
    try:
        asyncio.run(run_workers())
    except KeyboardInterrupt:
        print("\n[Worker] 收到中断信号，退出")
```

### sink（结果收集器）

```python
import asyncio
import zmq
import zmq.asyncio


async def sink(expected_count: int = 20):
    ctx = zmq.asyncio.Context()
    receiver = ctx.socket(zmq.PULL)
    receiver.linger = 0
    receiver.bind("tcp://*:5558")

    poller = zmq.asyncio.Poller()
    poller.register(receiver, zmq.POLLIN)

    collected = 0
    print(f"[收集器] 等待 {expected_count} 个任务完成信号...")

    while collected < expected_count:
        events = dict(await poller.poll(timeout=5000))

        if receiver in events:
            task_id = await receiver.recv_string()
            collected += 1
            print(f"[收集器] 收到任务 {task_id} 完成 ({collected}/{expected_count})")
        else:
            print("[收集器] 5秒无消息，检查中...")

    print(f"[收集器] 所有 {expected_count} 个任务已完成")

    poller.unregister(receiver)
    receiver.close()
    ctx.destroy(linger=0)


if __name__ == "__main__":
    asyncio.run(sink())
```

## 运行说明

需要在三个终端中分别启动（启动顺序：sink → workers → ventilator）：

```bash
# 终端 1：启动收集器
python sink.py

# 终端 2：启动工作节点（3个 worker 并发）
python worker.py

# 终端 3：启动分发器
python ventilator.py
```

**预期输出**：

```
[收集器] 等待 20 个任务完成信号...
[Worker-0] 已启动，等待任务...
[Worker-1] 已启动，等待任务...
[Worker-2] 已启动，等待任务...
[分发器] 开始发送 20 个任务
[分发器] 已分发: task-0
[Worker-0] 收到任务: task-0
[分发器] 已分发: task-1
[Worker-1] 收到任务: task-1
...
[收集器] 所有 20 个任务已完成
```

## 原理解析

### 1. asyncio Context

```python
ctx = zmq.asyncio.Context()
```

`zmq.asyncio.Context` 继承 `zmq.Context`，覆写 `_socket_class = Socket`（F-074），使 `ctx.socket()` 返回异步 Socket。它重置了 `_instance = None`，不与同步 Context 共享单例——同步和异步 Context 的 socket 类型不同，不能混用。

### 2. await send/recv

```python
await sender.send_string(workload)
task = await receiver.recv_string()
```

异步 Socket 的 `send`/`recv`/`send_string`/`recv_string` 等方法返回 `asyncio.Future`（F-065），可直接 `await`。底层机制：

1. 先尝试用 `DONTWAIT` 非阻塞发送/接收（短路优化，F-066/F-067）
2. 成功则立即完成 Future
3. EAGAIN 时将 Future 加入队列，通过 `loop.add_reader(fd, callback)` 注册 IO 事件
4. 事件就绪时回调执行实际的非阻塞 send/recv

在等待期间，asyncio 事件循环可以运行其他协程，实现单线程并发。

### 3. asyncio.Poller

```python
poller = zmq.asyncio.Poller()
poller.register(receiver, zmq.POLLIN)
events = dict(await poller.poll(timeout=5000))
```

`zmq.asyncio.Poller` 继承同步 `zmq.Poller`（F-073），覆写 `poll()` 返回 awaitable。`await poller.poll()` 在超时内等待事件，不会阻塞事件循环。返回值格式与同步 Poller 相同：`[(socket, event_mask), ...]`。

### 4. asyncio.gather 并发

```python
await asyncio.gather(*[worker(i) for i in range(num_workers)])
```

`asyncio.gather` 并发运行多个 worker 协程。每个 worker 在 `await recv_string()` 时让出控制权，事件循环在多个 worker 之间切换。这实现了**协作式并发**——不需要多线程，但多个 worker 可以同时处理任务（当一个在 `asyncio.sleep` 模拟处理时，其他 worker 可以接收消息）。

### 5. PUSH/PULL 模式

```
分发器 (PUSH) ──→ Worker 0 (PULL)
             ──→ Worker 1 (PULL)    ──→ 收集器 (PULL)
             ──→ Worker 2 (PULL)
```

PUSH/PULL 是**管道模式**：
- PUSH 端将任务**循环分发**（round-robin）给连接的 PULL 端
- PULL 端**公平排队**接收消息
- 消息不会重复（每个任务只发给一个 worker）
- 适合并行任务处理（map 风格）

ventilator 同时作为 PUSH（分发任务给 worker）和 PUSH（发送完成信号给 sink），使用两个独立 socket。

### 6. 优雅关闭

```python
try:
    task = await receiver.recv_string()
except zmq.ContextTerminated:
    break
```

当 Context 被 `destroy()` 终止时，阻塞的 `recv` 会抛 `ContextTerminated` 异常（ETERM），worker 捕获后退出循环。这是 ZeroMQ 的标准关闭模式。

`linger = 0` 确保关闭时不等待挂起消息，避免进程挂起。

## 同步 vs 异步对比

| 特性 | 同步 PUB/SUB | asyncio PUSH/PULL |
|------|-------------|-------------------|
| Context | `zmq.Context()` | `zmq.asyncio.Context()` |
| send/recv | 阻塞线程 | 返回 Future，需 await |
| Poller | `zmq.Poller()` | `zmq.asyncio.Poller()` |
| 并发模型 | 多线程/多进程 | 单线程协程 |
| 代码风格 | 同步调用 | `async/await` |
| 适用场景 | CPU 密集、简单脚本 | I/O 密集、高并发 |

## Windows 注意事项

在 Windows 上使用 asyncio 时，如果使用默认的 `ProactorEventLoop`，pyzmq 无法注册 FD 事件（F-075）。解决方案：

```python
import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

asyncio.run(main())
```

或安装 tornado（pyzmq 会自动用 `AddThreadSelectorEventLoop` 包装 ProactorEventLoop）。

## 关键事实溯源

| API | 事实编号 | 说明 |
|-----|---------|------|
| `zmq.asyncio.Context()` | F-074 | 异步 Context，覆写 _socket_class |
| `zmq.asyncio.Socket` | F-072 | 异步 Socket，add_reader 集成 |
| `await socket.recv_string()` | F-065 | recv 返回 Future |
| `await socket.send_string()` | F-065 | send 返回 Future |
| `zmq.asyncio.Poller()` | F-073 | 异步 Poller |
| `await poller.poll(timeout)` | F-063 | 返回 awaitable |
| `loop.add_reader(fd, cb)` | F-072 | 注册 FD 到 asyncio loop |
| `ContextTerminated` | F-093 | Context 终止异常 |

## 扩展练习

1. **增加动态 worker**：运行中动态启动新的 worker 协程，观察 PUSH 自动分发。
2. **任务结果回传**：让 worker 处理完后通过另一个 PUSH socket 将结果发给 sink，而非简单完成信号。
3. **超时控制**：用 `asyncio.wait_for(await recv(), timeout=5.0)` 实现任务接收超时。
4. **信号处理**：捕获 SIGINT/SIGTERM，在协程中优雅关闭所有 socket。

## 相关概念

- [异步与 asyncio](../concepts/05-async-future-asyncio.md) — Future 状态机与 add_reader 详解
- [Context 生命周期](../concepts/01-context-lifecycle.md) — asyncio.Context 的单例重置
- [Poller 多路复用](../concepts/04-poller.md) — 同步/异步 Poller 继承关系
- [Socket sugar 语法层](../concepts/02-socket-sugar.md) — send_string 等序列化方法
- [错误层次结构](../references/error-hierarchy.md) — ContextTerminated/Again 异常
- [同步 PUB/SUB 示例](sync-pubsub.md) — 同步版本对比
