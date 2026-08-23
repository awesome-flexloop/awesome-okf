---
type: example
title: "基础 Actor 与 Worker 示例"
description: "定义 actor、配置 broker、发送消息、启动 Worker 的完整代码与执行流程追踪"
tags: [dramatiq, example, actor, worker, redis, stub-broker]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [../references/redis-broker-internals.md, ../references/built-in-middleware.md]
  facts: [F-006, F-007, F-009, F-010, F-011, F-013, F-018, F-020, F-038, F-039, F-041, F-042, F-043, F-053, F-055, F-057, F-058, F-059, F-062, F-067]
---

# 基础 Actor 与 Worker 示例

## 完整代码

```python
# app.py
import dramatiq
from dramatiq.brokers.redis import RedisBroker

broker = RedisBroker(host="127.0.0.1", port=6379)
dramatiq.set_broker(broker)

@dramatiq.actor(queue_name="default")
def count_words(url):
    response = requests.get(url)
    count = len(response.text.split())
    print(f"There are {count} words at {url!r}.")
    return count

if __name__ == "__main__":
    # 同步调用（直接执行，不经过队列）
    result = count_words("https://example.com")
    print(f"Sync result: {result}")

    # 异步发送（经过 Redis 队列）
    message = count_words.send("https://example.com")
    print(f"Enqueued message: {message.message_id}")
```

## 启动 Worker

```bash
dramatiq app:broker --processes 2 --threads 4
```

## 执行流程追踪

### 1. 导入时

1. `set_broker(RedisBroker(...))` 设置全局 broker
2. `@dramatiq.actor` 装饰器执行：
   - `actor_name = "count_words"`（默认函数名）
   - `broker = get_broker()` 获取全局 broker
   - 校验 options 为空（合法）
   - 创建 `Actor(fn=count_words, actor_name="count_words", queue_name="default", priority=0, options={})`
   - `Actor.__init__` 调用 `broker.declare_actor(self)`
3. `Broker.declare_actor`：
   - `emit_before("declare_actor", actor)` — 中间件 before 钩子
   - `declare_queue("default")` — RedisBroker 将 "default" 和 "default.DQ" 加入 queues set
   - `self.actors["count_words"] = actor`
   - `emit_after("declare_actor", actor)` — 中间件 after 钩子
4. `_WorkerMiddleware.after_declare_queue` 被触发（Worker 启动后），创建 ConsumerThread

### 2. send() 调用时

1. `count_words.send("https://example.com")`
2. → `send_with_options(args=("https://example.com",), kwargs={}, delay=None)`
3. → `message_with_options(args=..., kwargs={})` 构造 Message：
   ```python
   Message(
       queue_name="default",
       actor_name="count_words",
       args=("https://example.com",),
       kwargs={},
       options={},
       message_id="a1b2c3d4-...",
       message_timestamp=1700000000000,
   )
   ```
4. → `broker.enqueue(message, delay=None)`
5. RedisBroker.enqueue：
   - 生成 `redis_message_id = str(uuid4())`，message.copy 添加此 option
   - `emit_before("enqueue", message, None)`
   - `do_enqueue("default", redis_message_id, message.encode())`
   - Lua 脚本：HSET `dramatiq:default.msgs` 存储消息数据，RPUSH `dramatiq:default` 推入消息 ID
   - `emit_after("enqueue", message, None)`

### 3. Worker 消费时

1. ConsumerThread.run() 调用 `broker.consume("default", prefetch=8, timeout=1000)`
2. `_RedisConsumer.__next__` 调用 `do_fetch("default", 8)`：
   - Lua 脚本 LPOP 最多 8 个 message_id
   - SADD 到 `dramatiq:__acks__.<worker_id>.default`
   - HMGET 返回消息数据
3. Message.decode(data) 反序列化
4. 包装为 MessageProxy
5. ConsumerThread.handle_message：无 eta，查找 actor，放入 PriorityQueue（priority=actor.priority=0）
6. WorkerThread.run() 从 PriorityQueue 获取消息
7. WorkerThread.process_message：
   - `emit_before("process_message", message)`：
     - AgeLimit 检查年龄（未过期）
     - TimeLimit 注册 10 分钟超时
     - ShutdownNotifications 注册线程 ID
   - `actor(*message.args, **message.kwargs)` 即 `count_words("https://example.com")`
   - `emit_after("process_message", message, result=count)`：
     - Retries：无异常，直接返回
     - Pipelines：无 pipe_target，直接返回
     - Callbacks：无 on_success，直接返回
     - ShutdownNotifications 移除通知
     - TimeLimit 移除超时
8. finally：ConsumerThread.post_process_message(message)：
   - `message.failed == False`
   - `emit_before("ack")` → `consumer.ack(message)` → `do_ack("default", redis_message_id)`
   - Lua 脚本：SREM 从 acks set 移除，HDEL 从 msgs hash 删除消息数据
   - `emit_after("ack")`
9. `work_queue.task_done()`，`message.clear_exception()`

## StubBroker 测试示例

```python
from dramatiq.brokers.stub import StubBroker

broker = StubBroker()
dramatiq.set_broker(broker)

@dramatiq.actor
def add(x, y):
    return x + y

# 发送消息
add.send(1, 2)

# 验证消息入队
assert len(broker.queues["default"].queue) == 1

# Worker 处理（测试中可用 broker.join 等待）
broker.join("default")
```

StubBroker 使用 Python `queue.Queue` 存储消息，`broker.join(queue_name)` 会阻塞直到所有消息处理完毕。
