---
type: Example
title: 模块间共享对象
description: 通过put/get机制在模块间共享对象，演示基于类型的异步发布-订阅依赖注入和CLI嵌套参数配置。
tags: [example, sharing, put, get, dependency-injection]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T14:55:00+08:00" }
verified: { by: "process:grep-api-verify", at: "2026-08-22T14:55:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: fps-guide
    resource: /references/module-source.md
    title: docs/guide.md Sharing objects between modules
  - id: fps-module-py
    resource: /references/module-source.md
    title: src/fps/_module.py
---

## 概述

本示例演示模块之间如何通过 `put()` 和 `get()` 共享对象，以及FPS的异步依赖注入如何自动协调模块启动顺序。

## 完整代码

创建 `share.py`：

```python
from anyio import Event, sleep
from fps import Module

class Main(Module):
    def __init__(self, name):
        super().__init__(name)
        self.add_module(Publisher, "publisher")
        self.add_module(Consumer, "consumer")

class Publisher(Module):
    async def start(self):
        self.shared = Event()
        self.put(self.shared, Event)
        print(f"Published: {self.shared.is_set()}")
        await self.shared.wait()
        self.exit_app()

    async def stop(self):
        print(f"Got: {self.shared.is_set()}")

class Consumer(Module):
    def __init__(self, name, wait=0.0):
        super().__init__(name)
        self.wait = float(wait)

    async def start(self):
        shared = await self.get(Event)
        print(f"Acquired: {shared.is_set()}")
        await sleep(self.wait)
        shared.set()
        print(f"Updated: {shared.is_set()}")
```

## 运行

```bash
fps share:Main
```

输出：
```
Published: False
Acquired: False
Updated: True
Got: True
```

设置延迟参数：
```bash
fps share:Main --set consumer.wait=0.5
```

Consumer会等待0.5秒后再更新Event，可以观察到应用短暂挂起。

传入错误参数名会得到清晰的错误：
```bash
fps share:Main --set consumer.wrong_parameter=0.5
# RuntimeError: Cannot instantiate module 'root_module.consumer':
#   Consumer.__init__() got an unexpected keyword argument 'wrong_parameter'
```

## 代码解析

### add_module添加子模块

```python
class Main(Module):
    def __init__(self, name):
        super().__init__(name)
        self.add_module(Publisher, "publisher")
        self.add_module(Consumer, "consumer")
```

`add_module()` 将子模块添加到模块树中。FPS自动并行启动所有子模块。

### put发布对象

```python
class Publisher(Module):
    async def start(self):
        self.shared = Event()
        self.put(self.shared, Event)
```

`self.put(value, Type)` 将值以指定类型发布到Context。值自动冒泡到父模块，兄弟模块也能获取。

### get异步获取对象

```python
class Consumer(Module):
    async def start(self):
        shared = await self.get(Event)
```

`await self.get(Type)` 异步等待该类型的对象被发布。如果Publisher尚未发布，Consumer会自动挂起等待，无需手动协调启动顺序。

### exit_app退出应用

```python
await self.shared.wait()
self.exit_app()
```

Publisher等待Event被设置后调用 `self.exit_app()` 主动退出应用。

### CLI嵌套参数

```bash
fps share:Main --set consumer.wait=0.5
```

点分路径 `consumer.wait` 定位到名为"consumer"的子模块，设置其 `wait` 参数。

## 执行时序

```
Publisher.start()              Consumer.start()
     |                              |
     |-- put(Event) --------------->|  (值冒泡到Main)
     |-- print("Published: False")  |
     |-- await shared.wait()        |-- await self.get(Event) → 立即获取
     |                              |-- print("Acquired: False")
     |                              |-- await sleep(0.5)
     |                              |-- shared.set()
     |                              |-- print("Updated: True")
     |-- shared.wait() 返回         |
     |-- print("Got: True")         |
     |-- exit_app()                 |
```

## 关键要点

- `put()`/`get()` 实现了基于类型的异步依赖注入：消费者不需要知道生产者是谁，只需声明需要什么类型
- `await self.get()` 自动处理等待逻辑，不需要事件循环或回调
- 子模块发布的值自动冒泡到父模块，兄弟模块通过父Context共享
- `--set` 支持点分路径配置任意深度的嵌套子模块参数
- `self.exit_app()` 可从任何模块调用以终止应用

## 相关概念

- [模块系统](/concepts/02-module-system.md)
- [上下文与共享值](/concepts/03-context-sharing.md)
- [生命周期阶段](/concepts/04-lifecycle-phases.md)
- [第一个FPS应用](01-first-app.md)
- [可插拔Web服务器](03-web-server.md)
