---
type: reference
title: "异常类层次结构"
description: "Dramatiq 全部异常类的继承关系、触发场景与处理方式"
tags: [dramatiq, reference, errors, exceptions, hierarchy]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  - path: "external/libs/remote/dramatiq/dramatiq/errors.py"
    facts: [F-003, F-095]
  - path: "external/libs/remote/dramatiq/dramatiq/results/errors.py"
    facts: []
---

# 异常类层次结构

## 类继承图

```text
DramatiqError
├── DecodeError
├── QueueJoinTimeout
├── RateLimitExceeded
├── Retry
└── BrokerError
    ├── ActorNotFound
    ├── QueueNotFound
    └── BrokerConnectionError
        ├── ConnectionFailed
        └── ConnectionClosed
```

结果模块额外定义：
```text
ResultError
├── ResultMissing
├── ResultTimeout
└── ResultFailure
```

## 核心异常

### DramatiqError

所有 dramatiq 异常的基类。存储 `message` 属性，`__str__` 返回消息字符串或 repr。

### BrokerError

所有 broker 相关异常的基类。

### ActorNotFound

- **触发**：`Broker.get_actor(actor_name)` 在 `self.actors` 字典中找不到对应 actor
- **场景**：消息发送到了未声明的 actor（worker 未导入对应模块）
- **处理**：ConsumerThread.handle_message 捕获后将消息 fail → nack → DLQ

### QueueNotFound

- **触发**：向未声明的队列 enqueue 或 consume
- **场景**：StubBroker 中队列未创建就操作

### BrokerConnectionError

连接相关异常的基类。旧名 `ConnectionError` 已废弃，v3.0.0 移除。

### ConnectionFailed

- **触发**：broker 连接无法建立
- **场景**：Redis/RabbitMQ 服务未启动、网络不可达

### ConnectionClosed

- **触发**：broker 连接突然断开
- **场景**：Redis 连接超时、RabbitMQ channel 关闭、网络中断
- **处理**：ConsumerThread 捕获后延迟 3 秒重启 consumer；post_process_message 每 5 秒重试 ack/nack

### DecodeError

- **触发**：消息解码失败（JSON 解析错误、UTF-8 解码错误、pickle 反序列化失败）
- **属性**：`data`（原始数据）、`error`（底层异常）
- **处理**：RabbitmqConsumer 解码失败时 nack 消息（进入 DLQ）

### QueueJoinTimeout

- **触发**：`Broker.join(queue_name, timeout=...)` 等待超时
- **场景**：测试中等待队列处理完成但超时

### RateLimitExceeded

- **触发**：actor 执行时超过速率限制
- **处理**：WorkerThread 中以 debug 级别记录（非 error），交给 Retries 中间件重试

### Retry

- **触发**：actor 主动抛出，表示"请重试我"
- **参数**：`message`（描述）、`delay`（可选的重试延迟毫秒数）
- **特点**：不被记录为 error 日志；若指定 delay 则使用该延迟而非指数退避
- **用途**：业务逻辑中判断需要重试时，比普通异常更明确且不污染错误日志

## 中间件异常

### MiddlewareError

中间件相关错误的基类。`emit_before` 中 `MiddlewareError` 直接传播，其他异常被捕获。

### SkipMessage

- **触发**：middleware 在 `before_process_message` 中主动抛出
- **效果**：跳过消息处理，Worker 发射 `after_skip_message` 而非 `after_process_message`
- **典型使用者**：AgeLimit（消息过期时）
- **注意**：若同时 `message.fail()` 则消息进入 DLQ，否则消息被 ack（视为正常跳过）

## 线程中断异常

### Interrupt

- **模块**：`dramatiq.middleware.threading`
- **继承**：`BaseException`（非 Exception）
- **用途**：异步中断工作线程的基类
- **子类**：
  - `Shutdown`：worker 关闭时由 ShutdownNotifications 注入
  - `TimeLimitExceeded`：执行超时时由 TimeLimit 注入
- **设计原因**：继承 BaseException 而非 Exception，避免被 actor 中的 `except Exception` 意外捕获

## 结果异常

### ResultError

结果模块异常基类。

### ResultMissing

- **触发**：`get_result(block=False)` 时结果尚未设置
- **场景**：非阻塞查询结果，任务尚未完成

### ResultTimeout

- **触发**：`get_result(block=True, timeout=N)` 等待超时
- **场景**：任务在指定时间内未完成或未存储结果

### ResultFailure

- **触发**：`unwrap_result` 检测到结果带有 `__t: "dramatiq.results.Result"` 标记
- **属性**：`exn_type`（原始异常类型名）、`exn_msg`（原始异常消息）
- **消息格式**：`"actor raised {type}: {msg}"`
- **场景**：actor 执行失败且 Results 中间件存储了异常，调用 get_result 时重新抛出

## 异常处理策略总结

| 异常 | Worker 处理 | Middleware 处理 |
|------|------------|----------------|
| `SkipMessage` | 发 skip_message 信号 | AgeLimit 等使用 |
| `RateLimitExceeded` | debug 日志，发 process_message(exception) | Retries 重试 |
| `Retry` | 不记录 error，发 process_message(exception) | Retries 重试 |
| 匹配 `throws` 的异常 | info 日志，发 process_message(exception) | Retries 不重试，直接 fail |
| 其他 `BaseException` | error 日志（含 traceback），发 process_message(exception) | Retries 重试或 fail |
| `ConnectionClosed` | ConsumerThread 重启 | post_process 无限重试 |
| `ActorNotFound` | ConsumerThread 直接 nack → DLQ | — |
