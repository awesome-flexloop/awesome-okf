---
type: Example
title: 信号使用
description: 使用FPS的Signal实现事件通知，包括回调模式和迭代器模式两种监听方式。
tags: [example, signal, event, callback, iterator]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T14:55:00+08:00" }
verified: { by: "process:grep-api-verify", at: "2026-08-22T14:55:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: fps-guide
    resource: /references/signal-source.md
    title: docs/guide.md Signals
  - id: fps-signal-py
    resource: /references/signal-source.md
    title: src/fps/_signal.py
---

## 概述

Signal用于事件通知场景：一部分代码发出值，其他部分通过回调或异步迭代器接收。本示例演示Signal的两种监听模式。

## 回调模式

```python
from anyio import run
from fps import Signal

async def main():
    signal = Signal()

    # 异步回调
    async def async_callback(value):
        print(f"Async received: {value}")

    # 同步回调
    def sync_callback(value):
        print(f"Sync received: {value}")

    signal.connect(async_callback)
    signal.connect(sync_callback)

    await signal.emit("Hello")
    await signal.emit("World!")

run(main)
```

输出：
```
Async received: Hello
Sync received: Hello
Async received: World!
Sync received: World!
```

## 迭代器模式

```python
from anyio import TASK_STATUS_IGNORED, create_task_group, run
from anyio.abc import TaskStatus
from fps import Signal

async def main():
    signal = Signal()

    async def iterate_signal(*, task_status: TaskStatus[None] = TASK_STATUS_IGNORED):
        async with signal.iterate() as iterator:
            task_status.started()
            async for value in iterator:
                if not value:
                    return
                print(f"Received: {value}")

    async with create_task_group() as tg:
        await tg.start(iterate_signal)

        await signal.emit("Hello")
        await signal.emit("World!")
        await signal.emit("")  # 空字符串作为终止信号

run(main)
```

输出：
```
Received: Hello
Received: World!
```

## 在Module中使用Signal

Signal在模块间的事件通知场景中非常有用：

```python
from fps import Module, Signal

class EventBus(Module):
    def __init__(self, name):
        super().__init__(name)
        self.user_logged_in = Signal()
        self.user_logged_out = Signal()

    async def start(self):
        self.put(self.user_logged_in, Signal)
        self.put(self.user_logged_out, Signal)
        self.done()

class AuthModule(Module):
    async def start(self):
        self.login_signal = await self.get(Signal)  # 注意：这里会有问题，见下方说明
        # 登录时触发信号
        # await self.login_signal.emit(user_id)

class LoggerModule(Module):
    async def start(self):
        login_signal = await self.get(Signal)  # 同样的问题
        login_signal.connect(self.on_login)

    def on_login(self, user_id):
        print(f"User logged in: {user_id}")
```

> **注意**：如果需要多个Signal，不能都按 `Signal` 类型发布（同类型只能注册一个）。解决方案是创建子类或使用封装类型：

```python
class LoginSignal(Signal): pass
class LogoutSignal(Signal): pass

class EventBus(Module):
    async def start(self):
        self.put(LoginSignal(), LoginSignal)
        self.put(LogoutSignal(), LogoutSignal)
        self.done()
```

## 多监听者场景

Signal支持任意数量的回调和迭代器同时监听：

```python
from anyio import create_task_group, run
from fps import Signal

async def main():
    signal = Signal()
    results = []

    def callback_a(v):
        results.append(f"A:{v}")

    def callback_b(v):
        results.append(f"B:{v}")

    signal.connect(callback_a)
    signal.connect(callback_b)

    async def listener(name):
        async with signal.iterate() as stream:
            async for v in stream:
                if v == "stop":
                    return
                results.append(f"{name}:{v}")

    async with create_task_group() as tg:
        await tg.start(listener, "L1")
        await tg.start(listener, "L2")

        await signal.emit("hello")
        await signal.emit("stop")

    print(results)
    # 可能输出（顺序不保证）:
    # ['A:hello', 'B:hello', 'L1:hello', 'L2:hello']

run(main)
```

## 断开与清理

```python
from anyio import run
from fps import Signal

async def main():
    signal = Signal()

    def handler(value):
        print(f"Got: {value}")

    signal.connect(handler)
    await signal.emit("first")  # Got: first

    signal.disconnect(handler)
    await signal.emit("second")  # 无输出（handler已断开）

run(main)
```

迭代器模式下，接收方退出async with块时，对应的send_stream会在下次emit时被自动清理（抛出BrokenResourceError后移除）。

## 关键要点

- Signal用于事件广播，不涉及资源生命周期管理（与Context/SharedValue不同）
- 回调支持同步和异步函数，框架自动检测并并发执行
- 迭代器模式适合持续监听事件流的场景
- 多个回调和迭代器可以同时监听同一个Signal
- `disconnect()` 用于取消回调注册
- 迭代器断开时自动清理，无需手动通知
- emit会等待所有回调（含异步）完成后才返回
- 如果需要多个不同的Signal实例，通过子类化区分类型

## Signal与Context共享的选择

| 场景 | 使用Signal | 使用Context put/get |
|------|-----------|---------------------|
| 事件通知（状态变化、消息广播） | ✅ | ❌ |
| 服务/资源共享（数据库连接、配置对象） | ❌ | ✅ |
| 一对多即时通知 | ✅ | ❌ |
| 需要等待资源可用 | ❌ | ✅ |
| 需要背压/并发控制 | ❌ | ✅（max_borrowers） |
| 生命周期管理（自动清理） | ❌ | ✅（teardown_callback） |

## 相关概念

- [信号系统](../concepts/06-signal-system.md)
- [上下文与共享值](../concepts/03-context-sharing.md)
- [独立使用Context](05-standalone-context.md)
