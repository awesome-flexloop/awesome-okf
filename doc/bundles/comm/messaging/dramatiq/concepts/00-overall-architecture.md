---
type: concept
title: "Dramatiq 整体架构"
description: "Dramatiq 五大核心组件（Actor/Broker/Worker/Middleware/Message）的关系与数据流"
tags: [dramatiq, task-queue, architecture, actor, broker, worker]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [../references/redis-broker-internals.md, ../references/rabbitmq-broker-internals.md, ../references/built-in-middleware.md, ../references/error-hierarchy.md]
  facts: [F-001, F-002, F-004, F-005, F-007, F-010, F-011, F-018, F-028, F-033, F-057, F-058, F-066, F-067, F-075]
---

# 00 · 整体架构

Dramatiq 是一个 Python 分布式任务队列库，核心由五大组件构成。

## 组件关系

```text
┌─────────────┐   send()    ┌──────────┐   enqueue()   ┌─────────────┐
│   Actor     │ ──────────> │  Message  │ ────────────> │   Broker    │
│ (业务函数)   │             │ (不可变信封)│               │ (消息中间件)  │
└─────────────┘             └──────────┘               └──────┬──────┘
       ▲                                                      │
       │ __call__() 同步执行                                    │ consume()
       │                                                      ▼
       │                                            ┌─────────────────┐
       │                                            │  ConsumerThread  │
       │                                            │  (网络IO/拉取)    │
       │                                            └────────┬────────┘
       │                                                     │ PriorityQueue
       │                                                     ▼
       │                                            ┌─────────────────┐
       │                                            │   WorkerThread   │
       │                                            │  (执行 actor)     │
       │                                            └────────┬────────┘
       │                                                     │
       └─────────────────────────────────────────────────────┘
                        actor(*args, **kwargs)
```

## 五大组件

| 组件 | 职责 | 关键文件 |
|------|------|---------|
| **Actor** | 包装业务函数，提供 `send()` 异步入队和 `__call__()` 同步执行 | `actor.py` |
| **Message** | 不可变数据信封，携带 actor_name/args/kwargs/options，可 encode/decode | `message.py` |
| **Broker** | 抽象消息中间件，管理 actors/queues/middleware，定义 enqueue/consume/ack 接口 | `broker.py` |
| **Worker** | 多线程消费引擎，ConsumerThread 拉取消息，WorkerThread 执行任务 | `worker.py` |
| **Middleware** | 洋葱模型管道，在消息生命周期各节点插入横切逻辑（重试/超时/回调等） | `middleware/` |

## 消息生命周期

1. **生产**：`actor.send(*args)` → `Actor.send_with_options()` → 构造 `Message` → `broker.enqueue(message, delay=delay)`
2. **入队**：Broker 触发 `before_enqueue`/`after_enqueue` 中间件钩子，将编码后的消息写入后端
3. **消费**：`ConsumerThread` 从 broker 拉取消息，包装为 `MessageProxy`，根据 `eta` 放入延迟队列或工作队列
4. **执行**：`WorkerThread` 从 PriorityQueue 取出消息，触发 `before_process_message` → `actor(*args, **kwargs)` → `after_process_message`
5. **确认**：根据执行结果（成功/失败/跳过），ConsumerThread 调用 `consumer.ack()` 或 `consumer.nack()`

## 进程模型

CLI 启动时采用**多进程 × 多线程**模型：

- 主进程：管理子进程生命周期、信号转发、日志聚合、文件监听
- Worker 进程（N 个，默认 CPU 核数）：每个进程运行一个 Worker 实例
- Worker 进程内：M 个 WorkerThread（默认 8）+ 每队列一个 ConsumerThread

## 后端可插拔

Broker 抽象层支持三种后端：

- **RedisBroker**：基于 redis-py，List 做队列 + ZSet 做死信 + Lua 脚本保证原子性
- **RabbitmqBroker**：基于 pika，AMQP 协议原生支持持久化和死信
- **StubBroker**：内存 Queue，用于单元测试

Worker 和 Actor 完全不感知后端差异，通过 Broker 抽象接口解耦。

## 相关概念

- [Actor 装饰器](01-actor-decorator.md)：业务函数如何变为可异步入队的任务单元
- [Broker 抽象基类](02-broker-abstraction.md)：消息中间件的防腐层设计
- [Worker 线程模型](03-worker-threading-model.md)：ConsumerThread 与 WorkerThread 的流水线协作
- [Message 与序列化](04-message-and-serialization.md)：不可变信封的字段结构与编解码
- [Middleware 中间件管道](05-middleware-pipeline.md)：洋葱模型与默认中间件顺序
- [Encoder 编码层](06-encoder.md)：JSON/Pickle 编码器与全局编码器管理
- [Results 结果后端](07-results-backend.md)：任务结果存储与获取
- [CLI 与 Watcher](08-cli-and-watcher.md)：多进程启动与热重载
