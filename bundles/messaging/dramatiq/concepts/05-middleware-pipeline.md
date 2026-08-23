---
type: concept
title: "Middleware 中间件管道"
description: "洋葱模型钩子生命周期、默认中间件顺序与职责、SkipMessage 机制、actor_options 扩展点"
tags: [dramatiq, task-queue, middleware, aop, onion-model, retries, pipelines]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [../references/built-in-middleware.md]
  facts: [F-029, F-030, F-031, F-066, F-067, F-068, F-069, F-070, F-071, F-072, F-073, F-074]
---

# 05 · Middleware 中间件管道

## 洋葱模型

Middleware 管道采用经典的洋葱模型：

```text
before_process_message (正序)
  ┌─ AgeLimit ─────────────────────────┐
  │ ┌─ TimeLimit ────────────────────┐ │
  │ │ ┌─ ShutdownNotifications ────┐ │ │
  │ │ │ ┌─ Callbacks ────────────┐ │ │ │
  │ │ │ │ ┌─ Pipelines ────────┐ │ │ │ │
  │ │ │ │ │ ┌─ Retries ──────┐ │ │ │ │ │
  │ │ │ │ │ │  actor()       │ │ │ │ │ │
  │ │ │ │ │ └────────────────┘ │ │ │ │ │
  │ │ │ │ └────────────────────┘ │ │ │ │
  │ │ │ └────────────────────────┘ │ │ │
  │ │ └────────────────────────────┘ │ │
  │ └────────────────────────────────┘ │
  └────────────────────────────────────┘
after_process_message (逆序: Retries → Pipelines → Callbacks → ...)
```

- `emit_before(signal)` 按 middleware 列表**正序**调用 `before_<signal>`
- `emit_after(signal)` 按 middleware 列表**逆序**调用 `after_<signal>`

## 完整钩子清单

### Actor/Queue 声明
- `before_declare_actor` / `after_declare_actor`
- `before_declare_queue` / `after_declare_queue`
- `after_declare_delay_queue`

### 消息入队
- `before_enqueue` / `after_enqueue`
- `before_delay_message`

### Worker 生命周期
- `before_worker_boot` / `after_worker_boot`
- `before_worker_shutdown` / `after_worker_shutdown`
- `after_process_boot`（子进程启动后）
- `after_consumer_thread_boot` / `before_consumer_thread_shutdown`
- `after_worker_thread_boot` / `before_worker_thread_shutdown`

### 消息处理
- `before_process_message`（可抛 SkipMessage 跳过）
- `after_process_message(broker, message, *, result=None, exception=None)`
- `after_skip_message`
- `before_ack` / `after_ack`
- `before_nack` / `after_nack`

## 默认中间件

默认顺序（`default_middleware`）：

| 顺序 | 中间件 | 职责 | actor_options |
|------|--------|------|---------------|
| 1 | `AgeLimit` | 丢弃超过 max_age 的消息 | `max_age` |
| 2 | `TimeLimit` | 超时中断 actor 执行 | `time_limit` |
| 3 | `ShutdownNotifications` | worker 关闭时通知 actor | `notify_shutdown` |
| 4 | `Callbacks` | 成功/失败回调 | `on_success`, `on_failure` |
| 5 | `Pipelines` | 将结果传递给下游 actor | `pipe_target`, `pipe_ignore` |
| 6 | `Retries` | 指数退避自动重试 | `max_retries`, `min_backoff`, `max_backoff`, `retry_when`, `throws`, `on_retry_exhausted` |

### 顺序的重要性

- **AgeLimit 在最外层**：最先检查消息年龄，过期则直接 SkipMessage，不进入 TimeLimit 等内层
- **Retries 在最内层**：after_process_message 时 Retries 最先执行（逆序），它看到异常后决定是否重新入队；Pipelines/Callbacks 在 Retries 之后执行，处理的是最终结果
- **TimeLimit 在 Retries 外层**：before_process_message 时 TimeLimit 在 Retries 之前注册超时，保证重试逻辑也在超时保护内

## SkipMessage 机制

在 `before_process_message` 中抛出 `SkipMessage` 可跳过消息处理：

```python
class AgeLimit(Middleware):
    def before_process_message(self, broker, message):
        if current_millis() - message.message_timestamp >= max_age:
            message.fail()
            raise SkipMessage("Message age limit exceeded")
```

Worker 捕获 SkipMessage 后：
1. 若 message.failed，将异常塞入 message
2. 发射 `after_skip_message` 信号（而非 `after_process_message`）
3. ConsumerThread 最终执行 nack

## actor_options 扩展点

每个 middleware 通过 `actor_options` 属性声明它支持的选项：

```python
class Retries(Middleware):
    @property
    def actor_options(self):
        return {"max_retries", "min_backoff", "max_backoff", "retry_when", "throws", "on_retry_exhausted"}
```

Broker 汇总所有 middleware 的 actor_options。Actor 装饰器在注册时校验传入的 options 是否在合法集合中，非法选项立即抛出 ValueError。

选项优先级（从高到低）：
1. `message.options`（send_with_options 传入）
2. `actor.options`（@actor 装饰器传入）
3. middleware 构造函数默认值

## 异常处理策略

- **before 阶段**：`MiddlewareError` 直接向上传播（中断处理），其他异常记录 critical 日志后继续执行下一个 middleware
- **after 阶段**：所有异常被捕获，仅记录 critical 日志，不影响其他 after 钩子执行

这种非对称设计的原因：before 是前置条件检查，失败应阻止操作；after 是清理/通知，应尽力全部执行。

## 自定义中间件

继承 `Middleware` 并实现所需钩子：

```python
class MyMiddleware(Middleware):
    @property
    def actor_options(self):
        return {"my_option"}

    def before_process_message(self, broker, message):
        value = message.options.get("my_option") or actor.options.get("my_option")
        ...

    def after_process_message(self, broker, message, *, result=None, exception=None):
        ...

broker.add_middleware(MyMiddleware(), before=Retries)
```

使用 `before`/`after` 参数控制插入位置。

## 相关概念

- [整体架构](/concepts/00-overall-architecture.md)：Middleware 是五大组件之一
- [Broker 抽象基类](/concepts/02-broker-abstraction.md)：emit_before/emit_after 实现在 Broker 基类
- [Worker 线程模型](/concepts/03-worker-threading-model.md)：process_message 触发中间件钩子
- [Message 与序列化](/concepts/04-message-and-serialization.md)：options 字典是 middleware 间通信总线
- [Results 结果后端](/concepts/07-results-backend.md)：Results 本身也是一个 Middleware
- [内置中间件详解](/references/built-in-middleware.md)：每个内置中间件的参数与钩子逻辑
