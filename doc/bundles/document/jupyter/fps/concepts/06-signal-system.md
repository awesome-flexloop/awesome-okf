---
type: Concept
title: 信号系统
description: FPS Signal类实现的异步发布-订阅信号机制，支持回调模式和迭代器模式两种监听方式，自动管理断开的流。
tags: [signal, event, publish-subscribe, callback, iterator, async]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T14:54:00+08:00" }
verified: { by: "process:grep-api-verify", at: "2026-08-22T14:54:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: fps-signal-py
    resource: /references/signal-source.md
    title: src/fps/_signal.py
---

## Signal 概述

`Signal` 是FPS提供的轻量级异步发布-订阅机制。与基于类型的服务共享（put/get）不同，Signal用于**事件通知**场景：一部分代码发出（emit）一个值，其他部分可以通过回调或异步迭代器接收这个值。

Signal不涉及资源生命周期管理（没有借用/释放机制），纯粹用于事件分发。

## 基本用法

### 回调模式

使用 `connect()` 注册回调函数，`emit()` 触发信号：

```python
from anyio import run
from fps import Signal

async def main():
    signal = Signal()

    async def async_callback(value):
        print(f"Async received: {value}")

    def sync_callback(value):
        print(f"Sync received: {value}")

    signal.connect(async_callback)
    signal.connect(sync_callback)

    await signal.emit("Hello")
    await signal.emit("World")

run(main)
# 输出:
# Async received: Hello
# Sync received: Hello
# Async received: World
# Sync received: World
```

回调可以是同步函数或协程函数，Signal内部通过 `iscoroutinefunction()` 检测，自动选择直接调用还是通过task_group启动。

### 断开回调

使用 `disconnect()` 取消注册：

```python
signal.disconnect(async_callback)
await signal.emit("after disconnect")
# sync_callback仍会收到，async_callback不会
```

### 迭代器模式

使用 `iterate()` 获取anyio内存流的接收端，通过 `async for` 迭代信号值：

```python
from anyio import TASK_STATUS_IGNORED, create_task_group, run
from anyio.abc import TaskStatus
from fps import Signal

async def main():
    signal = Signal()

    async def listener(*, task_status: TaskStatus[None] = TASK_STATUS_IGNORED):
        async with signal.iterate() as stream:
            task_status.started()
            async for value in stream:
                print(f"Received: {value}")
                if value == "stop":
                    return

    async with create_task_group() as tg:
        await tg.start(listener)
        await signal.emit("Hello")
        await signal.emit("World")
        await signal.emit("stop")

run(main)
```

迭代器模式适合需要持续监听信号流的场景。当listener退出async with块时，对应的send_stream会在下次emit时因`BrokenResourceError`被自动清理。

## API参考

| 方法 | 签名 | 说明 |
|------|------|------|
| `Signal()` | `()` | 创建信号实例 |
| `connect()` | `(callback: Callable[[T], None]) -> None` | 注册回调（同步或异步） |
| `disconnect()` | `(callback: Callable[[T], None]) -> None` | 取消注册回调 |
| `iterate()` | `() -> MemoryObjectReceiveStream[T]` | 返回可异步迭代的接收流 |
| `emit()` | `(value: T) -> None`（async） | 向所有监听者发送值 |

## 并发模型

`emit()` 使用 `anyio.create_task_group()` 并行执行：
1. 所有已注册回调（协程通过 `tg.start_soon`，同步函数直接调用）
2. 向所有 `_send_streams` 中的内存流发送值

这意味着：
- 多个回调是并发执行的，不保证顺序
- emit会等待所有回调（含异步回调）完成后才返回
- 向stream发送是并行的，某个stream断开不影响其他stream

## 自动断开清理

Signal内部维护 `_send_streams: set[MemoryObjectSendStream]` 集合。当迭代器端关闭（退出async with块），下次emit时send会抛出 `BrokenResourceError`，Signal自动将断开的stream加入to_remove列表并在emit结束后清理。

这意味着listener不需要显式通知signal自己断开，资源会被自动回收。

## Signal与Context共享的区别

| 特性 | Signal | Context共享（put/get） |
|------|--------|----------------------|
| 用途 | 事件通知/广播 | 服务/资源共享 |
| 方向 | 一对多广播 | 生产者→消费者 |
| 生命周期 | 无借用管理 | 严格的借用/释放模型 |
| 等待语义 | emit不等待接收方处理完（start_soon） | get等待生产者发布 |
| 背压 | 内存流提供天然背压 | max_borrowers限制并发 |
| 典型场景 | 状态变更通知、事件总线 | 数据库连接、配置对象、服务实例 |

## 多监听者

Signal支持同时有多个回调和多个迭代器监听：

```python
signal = Signal()

# 两个回调
signal.connect(callback_a)
signal.connect(callback_b)

# 两个迭代器
async with create_task_group() as tg:
    tg.start_soon(listener_1, signal)
    tg.start_soon(listener_2, signal)
    await signal.emit("broadcast")  # 所有监听者都收到
```

## 相关概念

- [上下文与共享值](03-context-sharing.md)
- [生命周期阶段](04-lifecycle-phases.md)
- [信号使用示例](../examples/06-signals-usage.md)
