---
type: concept
title: "Actor 装饰器"
description: "@dramatiq.actor 的注册机制、send 与 __call__ 双模态、GenericActor 类式 actor"
tags: [dramatiq, task-queue, actor, decorator, generic-actor]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [../references/built-in-middleware.md, ../references/error-hierarchy.md]
  facts: [F-007, F-008, F-009, F-010, F-011, F-012, F-013, F-014, F-015, F-016, F-017]
---

# 01 · Actor 装饰器

## 装饰器的两种用法

`dramatiq.actor` 同时支持无括号和带括号两种调用方式：

```python
@dramatiq.actor
def add(x, y):
    return x + y

@dramatiq.actor(queue_name="math", max_retries=5)
def multiply(x, y):
    return x * y
```

实现原理：`actor()` 函数的 `fn` 参数默认为 `None`。若 `fn is None`，返回内部 `decorator` 函数等待二次调用；否则直接调用 `decorator(fn)`。

## Actor.__init__ 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `fn` | callable | 被包装的函数（支持 sync/async） |
| `broker` | Broker | 绑定的 broker，默认 `get_broker()` |
| `actor_name` | str | 唯一名称，默认 `fn.__name__` |
| `queue_name` | str | 队列名，默认 `"default"`，正则 `[a-zA-Z_][a-zA-Z0-9._-]*` |
| `priority` | int | 优先级，数值越小越高，默认 0 |
| `options` | dict | 传递给 middleware 的任意选项 |

构造时若 `actor_name` 已存在于 `broker.actors` 中则抛出 `ValueError`。末尾调用 `broker.declare_actor(self)` 完成注册。

## 双模态调用

### 同步执行：`__call__`

```python
result = add(1, 2)  # 直接调用 self.fn(1, 2)，返回 3
```

`Actor.__call__` 直接执行底层函数，记录 debug 日志和耗时，**不经过 broker 或 middleware**。适合测试和简单场景。

### 异步入队：`send`

```python
message = add.send(1, 2)  # 构造 Message 并 broker.enqueue，返回 Message
```

调用链：`send(*args, **kwargs)` → `send_with_options(args, kwargs, delay)` → `message_with_options()` 构造 Message → `broker.enqueue(message, delay=delay)`。

### 消息构造：`message` / `message_with_options`

`message(*args, **kwargs)` 返回一个未入队的 Message，可用于组合（pipeline/group）：

```python
pipe = add.message(1, 2) | multiply.message(3)
```

`message_with_options` 会将 `on_failure`/`on_success` 选项中的 Actor 实例转换为其 `actor_name` 字符串。

## 协程支持

若被装饰函数是 `async def`，`Actor.__init__` 用 `async_to_sync(fn)` 包装，将协程提交到全局 `EventLoopThread` 执行。这要求添加 `AsyncIO` 中间件以启动事件循环线程。

## GenericActor：类式 Actor

`GenericActor` 使用元类 `generic_actor`，支持以类定义方式声明 actor：

```python
class MyTask(GenericActor):
    class Meta:
        queue_name = "tasks"
        max_retries = 10

    def perform(self, x):
        return x * 2

MyTask.send(42)
```

- `Meta.abstract = True` 的类是抽象基类，不会注册为 actor
- 子类必须实现 `perform()` 方法
- Meta 中非下划线开头的属性自动作为 actor options

## 相关概念

- [整体架构](/concepts/00-overall-architecture.md)：Actor 在五大组件中的位置
- [Broker 抽象基类](/concepts/02-broker-abstraction.md)：Actor 通过 broker.declare_actor 注册
- [Message 与序列化](/concepts/04-message-and-serialization.md)：send 构造的不可变消息结构
- [Middleware 中间件管道](/concepts/05-middleware-pipeline.md)：actor options 如何被 middleware 消费
- [内置中间件详解](/references/built-in-middleware.md)：各 middleware 支持的 actor_options
- [异常类层次结构](/references/error-hierarchy.md)：ActorNotFound 等异常
