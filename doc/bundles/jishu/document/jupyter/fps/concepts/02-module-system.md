---
type: Concept
title: 模块系统
description: FPS核心Module类的结构、模块树组织、服务发布与获取机制，以及模块间的父子关系和值冒泡规则。
tags: [module, core, tree, publish, subscribe]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T14:52:00+08:00" }
verified: { by: "process:grep-api-verify", at: "2026-08-22T14:52:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: fps-module-py
    resource: /references/module-source.md
    title: src/fps/_module.py
  - id: fps-context-py
    resource: /references/context-source.md
    title: src/fps/_context.py
---

## Module 类

`Module` 是 FPS 应用的基本构建块。每个模块是一个独立的功能单元，可以：
- 拥有自己的配置参数
- 发布服务（值）给其他模块使用
- 获取其他模块发布的服务
- 添加和管理子模块
- 响应三阶段生命周期（prepare → start → stop）

### 构造函数

```python
class Module:
    def __init__(
        self,
        name: str,
        prepare_timeout: float = 1,
        start_timeout: float = 1,
        stop_timeout: float = 1,
        global_start_timeout: float | None = None,
    ): ...
```

参数说明：
- `name`：模块名称，在父模块的子模块字典中作为key
- `prepare_timeout`：prepare阶段超时秒数，默认1秒
- `start_timeout`：start阶段超时秒数，默认1秒
- `stop_timeout`：stop阶段超时秒数，默认1秒
- `global_start_timeout`：prepare+start阶段总超时，设置后覆盖各自的超时

> **重要**：子类覆盖 `__init__` 时必须调用 `super().__init__(name, ...)`，否则在进入异步上下文时会抛出 `RuntimeError: You must call super().__init__() in the __init__ method of your module`。

### 模块属性

Module提供以下只读property：

| Property | 类型 | 说明 |
|----------|------|------|
| `name` | `str` | 模块名称 |
| `path` | `str` | 从根到当前模块的点分路径（如 `root_module.sub_module`） |
| `parent` | `Module \| None` | 父模块引用，根模块为None |
| `modules` | `dict[str, Module]` | 子模块字典 |
| `prepared` | `anyio.Event` | prepare阶段完成信号 |
| `started` | `anyio.Event` | start阶段完成信号 |
| `stopped` | `anyio.Event` | stop阶段完成信号 |

## 模块树组织

模块以树状结构组织。父模块通过 `add_module()` 添加子模块：

```python
from fps import Module

class ParentModule(Module):
    def __init__(self, name):
        super().__init__(name)
        self.add_module(ChildModule, "child")
        # 也可以用字符串引用（entry-point或Python路径）
        self.add_module("fps:Module", "container")

class ChildModule(Module):
    async def start(self):
        print(f"Child starting, path: {self.path}")  # root_module.child
```

`add_module()` 接受的模块类型可以是：
- Module子类对象本身
- 字符串：Python路径格式（`"module.path:ClassName"`）或entry-point名称（如`"fps_module"`）

添加同名子模块会抛出 `RuntimeError: Module name already exists: <name>`。

## 运行模块

Module 实现了异步上下文管理器协议，通过 `async with` 运行：

```python
import anyio
from fps import Module

class MyApp(Module):
    async def start(self):
        print("App started")

    async def stop(self):
        print("App stopped")

async def main():
    async with MyApp("my_app") as app:
        await app._exit.wait()  # 等待退出信号

anyio.run(main)
```

更简便的方式是使用 `run()` 方法：

```python
MyApp("my_app").run(backend="asyncio")
```

`run()` 内部处理了KeyboardInterrupt的捕获，Ctrl+C可以正常退出。

也可以通过CLI命令 `fps module_path:ClassName` 启动。

## 服务发布（put）

模块通过 `self.put()` 发布服务（值），供其他模块获取：

```python
async def start(self):
    # 发布一个数据库连接，类型为Database
    db = await create_database()
    self.put(db, Database)
```

方法签名：

```python
def put(
    self,
    value: T,
    types: Iterable | Any | None = None,
    max_borrowers: float = float("inf"),
    teardown_callback: Callable | None = None,
) -> None
```

- `value`：要发布的值对象
- `types`：注册的类型，默认为 `type(value)`。可以传入多个类型（如 `[Database, Connection]`），实现一个值对多种类型可见
- `max_borrowers`：最大并发借用者数量，默认为无限
- `teardown_callback`：值被关闭时的清理回调

### 值冒泡机制

子模块调用 `self.put()` 发布的值会**自动冒泡到父模块的context中**。这意味着：
- 子模块发布的值，对父模块和兄弟模块可见
- 父模块发布的值，对子模块**不可见**（查找沿父链向上，不向下）
- 兄弟模块之间通过共同的父模块间接共享值

```
RootModule
├── ModuleA (put Event → 冒泡到RootModule)
└── ModuleB (await self.get(Event) → 从RootModule向上查找，能获取到A发布的值)
```

## 服务获取（get）

模块通过 `await self.get()` 异步获取其他模块发布的服务：

```python
async def start(self):
    # 异步等待Database类型的值被发布
    db = await self.get(Database)
    # 使用db...
```

方法签名：

```python
async def get(
    self,
    value_type: type[T],
    timeout: float = float("inf"),
) -> T
```

- `value_type`：要获取的值的类型
- `timeout`：等待超时秒数，默认永久等待

`get()` 在模块自身context和所有祖先context上并行竞争查找，第一个找到的值立即返回。如果在超时时间内未找到，抛出 `TimeoutError`，并记录critical级别日志 `"Module could not get value"`。

> **注意**：`get()` 返回的是值本身（内部调用了 `value.unwrap()`），不是Value包装器。这意味着你需要手动管理值的drop，或使用Context的独立get获取Value包装器。

## 强制退出

任何模块都可以调用 `self.exit_app()` 强制整个应用退出：

```python
async def start(self):
    # 遇到致命错误，退出应用
    self.exit_app()
```

这会设置根模块的 `_exit` Event，触发应用关闭流程。

## Teardown 回调

可以注册在模块停止时执行的清理回调：

```python
async def start(self):
    resource = await acquire_resource()

    def cleanup():
        resource.close()

    self.add_teardown_callback(cleanup)
```

回调按注册顺序的**逆序**（LIFO）执行，与上下文管理器的栈式退出一致。回调可以是同步或异步函数。

## 相关概念

- [上下文与共享值](03-context-sharing.md)
- [生命周期阶段](04-lifecycle-phases.md)
- [配置系统](05-configuration-system.md)
- [模块间共享对象](../examples/02-sharing-objects.md)
