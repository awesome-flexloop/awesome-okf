---
type: concept
title: "Broker 抽象基类"
description: "Broker 的模板方法模式、emit 信号机制、Consumer/MessageProxy 抽象、三种后端对比"
tags: [dramatiq, task-queue, broker, abstraction, consumer, message-proxy]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [../references/redis-broker-internals.md, ../references/rabbitmq-broker-internals.md, ../references/error-hierarchy.md]
  facts: [F-004, F-005, F-006, F-028, F-029, F-030, F-031, F-032, F-033, F-034, F-035, F-036, F-037]
---

# 02 · Broker 抽象基类

## Broker 的角色

Broker 是 dramatiq 的消息中间件抽象层，负责：
- 维护 actor 注册表（`self.actors: dict[str, Actor]`）
- 维护 queue 和 delay_queue 声明
- 管理 middleware 列表和 actor_options 集合
- 发射生命周期信号（emit_before/emit_after）
- 定义子类必须实现的消息操作接口

## 全局 Broker

```python
global_broker: Optional[Broker] = None

def get_broker() -> Broker:
    # 惰性初始化：先尝试 RabbitmqBroker，ImportError 则回退 RedisBroker
    ...

def set_broker(broker: Broker) -> None:
    global global_broker
    global_broker = broker
```

`get_broker()` 的惰性回退机制使得用户只需安装 `dramatiq[redis]` 或 `dramatiq[rabbitmq]` 即可自动选择后端。默认尝试创建 `RabbitmqBroker(host="127.0.0.1", port=5672, heartbeat=5, connection_attempts=5, blocked_connection_timeout=30)`，若 pika 未安装则回退到 `RedisBroker()`。

## 模板方法：declare_actor

`declare_actor` 是基类中的具体方法，封装了通用流程：

```python
def declare_actor(self, actor):
    self.emit_before("declare_actor", actor)
    self.declare_queue(actor.queue_name)       # 子类实现
    self.actors[actor.actor_name] = actor
    self.emit_after("declare_actor", actor)
```

子类只需实现 `declare_queue`，actor 注册逻辑由基类统一处理。

## 信号发射：emit_before / emit_after

```python
def emit_before(self, signal, *args, **kwargs):
    signal = "before_" + signal
    for middleware in self.middleware:
        try:
            getattr(middleware, signal)(self, *args, **kwargs)
        except MiddlewareError:
            raise
        except Exception:
            self.logger.critical(...)

def emit_after(self, signal, *args, **kwargs):
    signal = "after_" + signal
    for middleware in reversed(self.middleware):
        try:
            getattr(middleware, signal)(self, *args, **kwargs)
        except Exception:
            self.logger.critical(...)
```

- **before 正序**：外层 middleware 先进入，`MiddlewareError` 向上传播（fail-fast），其他异常仅记录 critical 日志
- **after 逆序**：内层 middleware 先退出（洋葱展开），所有异常被吞掉仅记录日志（尽力执行）

## 抽象方法清单

| 方法 | 职责 |
|------|------|
| `consume(queue_name, prefetch, timeout) -> Consumer` | 创建消息迭代器 |
| `declare_queue(queue_name)` | 声明队列（幂等） |
| `enqueue(message, *, delay=None) -> Message` | 入队消息 |
| `flush(queue_name)` | 清空队列 |
| `flush_all()` | 清空所有队列 |
| `join(queue_name, *, timeout=None)` | 等待队列处理完成（测试用） |

以上方法在基类中均抛出 `NotImplementedError`，子类必须实现。

## Consumer 抽象

Consumer 是消息迭代器协议：

```python
class Consumer:
    def __iter__(self): return self
    def __next__(self) -> MessageProxy | None: ...
    def ack(self, message): ...
    def nack(self, message): ...
    def requeue(self, messages): ...  # 默认 no-op
    def close(self): ...
```

`__next__` 应阻塞有限时间（timeout），超时返回 `None`。`ack`/`nack` 在基类中抛出 `NotImplementedError`，`requeue`/`close` 默认是空操作。

## MessageProxy

`MessageProxy` 包装 `Message`，增加可变处理状态：

- `failed: bool`：消息是否处理失败
- `stuff_exception(exception)` / `clear_exception()`：存取处理异常
- `fail()`：标记为失败
- `__getattr__`：透明代理 Message 的所有字段

后端可以继承 MessageProxy 添加特定元数据（如 RabbitMQ 的 `delivery_tag`、Redis 的 `redis_message_id`）。

## add_middleware

支持 `before`/`after` 参数控制插入位置。添加后：
1. 检查同类 middleware 重复添加并发出 warning
2. 将 middleware 的 `actor_options` 合并到 broker 的 `actor_options`
3. 对所有已声明 actor 调用 `after_declare_actor`
4. 对所有已声明 queue 调用 `after_declare_queue`/`after_declare_delay_queue`

这确保后添加的 middleware 也能感知已存在的 actor 和 queue。

## 相关概念

- [整体架构](00-overall-architecture.md)：Broker 在五大组件中的位置
- [Actor 装饰器](01-actor-decorator.md)：Actor 注册时调用 broker.declare_actor
- [Worker 线程模型](03-worker-threading-model.md)：Worker 通过 broker.consume 获取消息
- [Middleware 中间件管道](05-middleware-pipeline.md)：emit_before/emit_after 的洋葱模型
- [RedisBroker 内部结构](../references/redis-broker-internals.md)：Redis 后端实现详解
- [RabbitmqBroker 内部结构](../references/rabbitmq-broker-internals.md)：RabbitMQ 后端实现详解
- [异常类层次结构](../references/error-hierarchy.md)：ActorNotFound、BrokerConnectionError 等
