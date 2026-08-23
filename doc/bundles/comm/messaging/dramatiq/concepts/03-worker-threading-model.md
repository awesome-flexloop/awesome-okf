---
type: concept
title: "Worker 线程模型"
description: "ConsumerThread 与 WorkerThread 的流水线协作、PriorityQueue 优先级调度、优雅关闭与信号处理"
tags: [dramatiq, task-queue, worker, threading, consumer, priority-queue, graceful-shutdown]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [../references/redis-broker-internals.md, ../references/rabbitmq-broker-internals.md]
  facts: [F-057, F-058, F-059, F-060, F-061, F-062, F-063, F-064, F-065]
---

# 03 · Worker 线程模型

## 架构概览

Worker 采用 SEDA（分阶段事件驱动）风格：

```text
Broker ──> ConsumerThread ──> PriorityQueue ──> WorkerThread ──> Actor
            (网络IO阶段)        (工作队列)        (计算阶段)
```

- **ConsumerThread**：每个队列一个，负责从 broker 拉取消息、处理延迟调度、ack/nack
- **WorkerThread**：N 个（默认 8），负责从 PriorityQueue 取消息并执行 actor
- **PriorityQueue**：线程间共享，按 actor.priority 和入队时间排序

## Worker 初始化

```python
Worker(broker, *, queues=None, worker_timeout=1000, worker_threads=8)
```

关键参数：
- `queue_prefetch = min(worker_threads * 2, 65535)`：普通消息预取数
- `delay_prefetch = min(worker_threads * 1000, 65535)`：延迟消息预取数（更大，因为延迟消息可能有远期 eta）
- `work_queue`：`PriorityQueue[_WorkQueueItem]` 实例，ConsumerThread 和 WorkerThread 共享

## ConsumerThread.run() 主循环

1. 调用 `broker.consume(queue_name, prefetch, timeout)` 获取 Consumer 迭代器
2. 遍历消息：非 None 消息调用 `handle_message`，None 时检查暂停状态
3. 每次迭代后调用 `handle_delayed_messages` 检查延迟消息到期
4. 遇到 `BrokerConnectionError`：重置 delay_queue，等待 3 秒（`CONSUMER_RESTART_DELAY`）后重启 consumer
5. 遇到其他异常：关闭 consumer，等待 3 秒后重启

### handle_message

- 消息有 `eta` 选项：校验 eta 有效性后放入 `self.delay_queue`（PriorityQueue，优先级=eta 时间戳）
- 消息无 eta：查找 actor，放入 `self.work_queue`（PriorityQueue，优先级=actor.priority）
- actor 不存在：标记 `message.fail()`，记录异常，进入 post_process（nack → DLQ）

### handle_delayed_messages

遍历 delay_queue：
- 若 `eta > current_millis()`：放回队列并 break（PriorityQueue 保证队首最早到期）
- 若到期：`message.copy(queue_name=q_name(...))` 删除 eta 选项，重新 `broker.enqueue`

## WorkerThread.run() 主循环

1. `work_queue.get(timeout=worker_timeout/1000)` 取出 `_WorkQueueItem`
2. 调用 `process_message(message)`
3. 队列为空（Empty）时 continue

### process_message

```text
emit_before("process_message")
  └─> actor(*message.args, **message.kwargs)
emit_after("process_message", result=res)       # 成功
或
emit_after("process_message", exception=e)       # 失败
或
emit_after("skip_message")                        # SkipMessage
finally:
  consumers[queue_name].post_process_message(message)
  work_queue.task_done()
  message.clear_exception()
```

异常处理：
- `SkipMessage`：记录 warning，发 skip_message 信号
- `RateLimitExceeded`：debug 日志，发 process_message(exception)
- 匹配 `throws` 选项的异常：info 日志，发 process_message(exception)
- `Retry` 异常：不记录 error，发 process_message(exception)
- 其他 `BaseException`：error 日志（含 traceback），发 process_message(exception)

### post_process_message（在 ConsumerThread 上）

- `message.failed == True`：`emit_before("nack") → consumer.nack() → emit_after("nack")`
- `message.failed == False`：`emit_before("ack") → consumer.ack() → emit_after("ack")`
- 遇到 `BrokerConnectionError`：每 5 秒无限重试，直到成功

## _WorkQueueItem 与优先级

```python
@dataclasses.dataclass(frozen=True, slots=True, eq=True, order=True)
class _WorkQueueItem:
    priority: int                    # actor.priority 或 eta
    message: MessageProxy = field(compare=False)
    _queued_time: int = field(default_factory=time.monotonic_ns)
```

PriorityQueue 按 `(priority, _queued_time)` 排序：priority 数值越小越先执行，相同 priority 按入队时间 FIFO。

## 优雅关闭

`Worker.stop(timeout=600000)` 顺序：

1. `emit_before("worker_shutdown")`
2. **先停 WorkerThread**：`thread.stop()` → join（让正在执行的任务完成）
3. **再停 ConsumerThread**：`thread.stop()` → join（保持心跳直到 worker 停止）
4. **重队列内存消息**：遍历 work_queue，按 queue 分组调用 `consumer.requeue_messages()`
5. 关闭所有 consumer
6. `emit_after("worker_shutdown")`

关键设计：先停 WorkerThread 是因为它们是消费者；ConsumerThread 保持存活以维持 broker 心跳，防止 worker 关闭期间 broker 认为消费者已死。

## pause / resume

- `pause()`：对所有 consumer 和 worker 调用 `pause()`，然后等待所有 `paused_event` 被 set
- `resume()`：清除 paused 状态和 paused_event
- 线程在 paused 时 sleep `worker_timeout` 后检查状态

## 相关概念

- [整体架构](/concepts/00-overall-architecture.md)：Worker 在五大组件中的位置
- [Broker 抽象基类](/concepts/02-broker-abstraction.md)：Worker 通过 broker.consume 获取 Consumer
- [Message 与序列化](/concepts/04-message-and-serialization.md)：MessageProxy 包装 Message 增加 failed 状态
- [Middleware 中间件管道](/concepts/05-middleware-pipeline.md)：process_message 触发的 before/after 钩子
- [CLI 与 Watcher](/concepts/08-cli-and-watcher.md)：多进程 fork 与信号处理
- [RedisBroker 内部结构](/references/redis-broker-internals.md)：Redis consumer 的 fetch/ack 实现
- [RabbitmqBroker 内部结构](/references/rabbitmq-broker-internals.md)：RabbitMQ consumer 的线程模型
