---
type: reference
title: "RabbitmqBroker 内部结构"
description: "RabbitmqBroker 的线程局部 Channel、exchange/queue 声明、confirm_delivery、consumer 模型与死信机制"
tags: [dramatiq, reference, rabbitmq, broker, pika, amqp]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  - path: "external/libs/remote/dramatiq/dramatiq/brokers/rabbitmq.py"
    facts: [F-047, F-048, F-049, F-050, F-051, F-052]
---

# RabbitmqBroker 内部结构

## 连接管理：线程局部 Channel

RabbitmqBroker 使用 `threading.local()` 为每个线程维护独立的 pika 连接和 channel：

```python
self.state = local()

@property
def connection(self):
    connection = getattr(self.state, "connection", None)
    if connection is None:
        connection = self.state.connection = pika.BlockingConnection(parameters=self.parameters)
        self.connections.add(connection)
    return connection

@property
def channel(self):
    channel = getattr(self.state, "channel", None)
    if channel is None:
        channel = self.state.channel = self.connection.channel()
        if self.confirm_delivery:
            channel.confirm_delivery()
        self.channels.add(channel)
    return channel
```

pika 的 `BlockingConnection` 不是线程安全的，因此每个线程（主进程、WorkerThread、ConsumerThread）获得自己的 channel。删除 `broker.connection` 属性会关闭并清理当前线程的连接。

## 连接参数

支持三种参数指定方式：
1. `url`（str 或 list[str]）：单个 URL 或分号分隔的多个 URL（用于集群）
2. `parameters`（list[dict]）：多个 pika 连接参数字典
3. `**kwargs`：单个 pika 连接参数

`url` 不能与其他参数混用。默认连接 `host="127.0.0.1", port=5672, heartbeat=5, connection_attempts=5, blocked_connection_timeout=30`。

## Queue 声明

### 三种队列

每个逻辑队列对应三个 RabbitMQ 队列：

| 队列 | 后缀 | 用途 |
|------|------|------|
| 主队列 | （无） | 正常消息投递 |
| 延迟队列 | `.DQ` | 延迟消息暂存 |
| 死信队列 | `.XQ` | nack 后的消息 |

### 声明参数

主队列和延迟队列声明时设置：
```python
arguments = {
    "x-dead-letter-exchange": "",           # 默认 exchange
    "x-dead-letter-routing-key": xq_name,   # nack 路由到 .XQ
}
if max_priority:
    arguments["x-max-priority"] = max_priority
```

死信队列设置：
```python
arguments = {"x-message-ttl": DEAD_MESSAGE_TTL}  # 默认 7 天
```

所有队列 `durable=True`。

### 惰性创建

`declare_queue` 只在 broker 内存中记录队列名（`self.queues` set 和 `self.queues_pending` set），不立即在 RabbitMQ 上创建。实际创建发生在：
- `consume(ensure=True)` 时：创建 consumer 前确保队列存在
- `enqueue(ensure=True)` 时：发布消息前确保队列存在

`_ensure_queue` 遇到连接错误时删除连接并重试，最多 `MAX_DECLARE_ATTEMPTS=2` 次。

## 消息发布

```python
self.channel.basic_publish(
    exchange="",
    routing_key=queue_name,
    body=message.encode(),
    properties=pika.BasicProperties(
        delivery_mode=2,                                    # 持久化
        priority=message.options.get("broker_priority"),    # AMQP 优先级
    ),
    mandatory=self.confirm_delivery,
)
```

- `exchange=""` 使用 RabbitMQ 默认 exchange，routing_key 即队列名
- `delivery_mode=2` 消息持久化
- `mandatory=True`（仅 confirm_delivery 时）确保消息可达队列，不可路由时抛 `UnroutableError`
- 连接错误最多重试 `MAX_ENQUEUE_ATTEMPTS=6` 次
- `UnroutableError` 时将队列加回 `queues_pending` 以便下次重试时重新声明

### broker_priority 与 actor.priority 的区别

- `broker_priority`（AMQP 优先级）：数值越**大**优先级越高，0-255
- `actor.priority`（dramatiq 优先级）：数值越**小**优先级越高

两者方向相反，因为它们由不同层处理。

## Consumer 模型

`_RabbitmqConsumer` 创建自己的独立连接（非线程局部的 broker 连接）：

```python
self.connection = pika.BlockingConnection(parameters=self.broker.parameters)
self.channel = self.connection.channel()
self.channel.basic_qos(prefetch_count=prefetch)
self.iterator = self.channel.consume(queue_name, inactivity_timeout=timeout/1000)
```

### ack/nack

由于 consumer 的 channel 运行在 ConsumerThread 中，而 ack/nack 由 ConsumerThread 调用（实际在同一线程），使用 `connection.add_callback_threadsafe` 调度：

```python
def ack(self, message):
    self.known_tags.remove(message._tag)
    self.connection.add_callback_threadsafe(
        partial(self.channel.basic_ack, message._tag)
    )
```

nack 使用 `basic_nack(tag, requeue=False)`，消息通过 dead-letter-exchange 自动路由到 `.XQ`。

`known_tags` Set 跟踪已知的 delivery_tag，防止连接重置后发送无效 tag。

### requeue 是 no-op

RabbitMQ 在消费者断开时自动将未 ack 的消息重新入队，因此 `requeue` 方法为空。

### 消息解码

从 consumer 迭代器获取 `(method, properties, body)`：
- `method is None` 表示超时无消息，返回 None
- 消息解码失败时记录日志并 nack（进入 DLQ），返回 None
- 成功则包装为 `_RabbitmqMessage(redelivered, delivery_tag, message)`

## confirm_delivery 模式

`confirm_delivery=False`（默认）：发布后不等待 RabbitMQ 确认，性能更高但可能丢消息。
`confirm_delivery=True`：每条消息发布后等待确认，可检测队列不存在并自动重新声明，但吞吐量降低。

此模式是检测和重新声明缺失队列的必要条件。

## 关闭

`close()` 遍历所有 channels 和 connections 并关闭，过滤 pika 的 `AMQPError`。使用 `_IgnoreScaryLogs` 过滤器抑制关闭时的 "Broken pipe" 警告日志。
