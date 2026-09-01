---
type: concept
title: "Message 与序列化"
description: "Message 不可变 frozen dataclass 的字段结构、encode/decode 编解码、copy 不可变更新、options 路由元数据"
tags: [dramatiq, task-queue, message, serialization, dataclass, immutable]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [../references/error-hierarchy.md]
  facts: [F-018, F-019, F-020, F-021, F-022, F-023, F-024, F-037]
---

# 04 · Message 与序列化

## Message 数据结构

Message 是 `@dataclasses.dataclass(frozen=True)` 装饰的不可变泛型类 `Generic[R]`：

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `queue_name` | `str` | 必填 | 目标队列名 |
| `actor_name` | `str` | 必填 | 目标 actor 名 |
| `args` | `tuple` | 必填 | 位置参数（自动转为 tuple） |
| `kwargs` | `dict` | 必填 | 关键字参数 |
| `options` | `dict` | 必填 | 中间件路由选项 |
| `message_id` | `str` | `uuid4()` | 全局唯一 ID |
| `message_timestamp` | `int` | `time.time()*1000` | 创建时间（毫秒） |

`__post_init__` 强制将 `args` 转为 tuple（因 frozen dataclass 不可直接赋值，使用 `object.__setattr__`），保证不可变哈希一致性。

## 编解码

### encode

```python
def encode(self) -> bytes:
    return global_encoder.encode(self.asdict())
```

将 Message 转为 dict（包含全部 7 个字段），委托给全局 Encoder 序列化为 bytes。

### decode

```python
@classmethod
def decode(cls, data: bytes) -> Message:
    try:
        fields = global_encoder.decode(data)
        fields["args"] = tuple(fields["args"])
        return cls(**fields)
    except Exception as e:
        raise DecodeError("Failed to decode message.", data, e) from e
```

解码失败时统一抛出 `DecodeError`，包含原始数据和底层异常。

## 不可变更新：copy

```python
def copy(self, **attributes) -> Message:
    new_options = attributes.pop("options", {})
    return dataclasses.replace(self, **attributes, options={**self.options, **new_options})
```

`copy` 执行**浅合并**：新 options 与旧 options 合并，新键覆盖旧键。这是 middleware"修改"消息的标准方式——实际创建新的不可变实例。

典型使用场景：
- Retries 中间件重新入队时更新 `retries`/`traceback`
- ConsumerThread 将延迟消息的 queue_name 从 `.DQ` 改为规范名并删除 `eta`
- RedisBroker 为每条入队消息添加 `redis_message_id`

## options 字典：中间件通信总线

`options` 是 Message 上最动态的字段，不同 middleware 读取和写入各自的键：

| 选项键 | 写入者 | 读取者 | 用途 |
|--------|--------|--------|------|
| `eta` | enqueue 延迟消息时 | ConsumerThread | 延迟调度时间戳（毫秒） |
| `retries` | Retries middleware | Retries | 当前重试次数 |
| `max_retries` | actor 声明时 | Retries | 最大重试次数 |
| `traceback` | Retries middleware | — | 上次失败的 traceback |
| `requeue_timestamp` | Retries middleware | — | 重新入队时间 |
| `min_backoff`/`max_backoff` | actor 声明时 | Retries | 退避参数 |
| `throws` | actor 声明时 | Worker/Retries | 不重试的异常类型 |
| `on_success`/`on_failure` | actor 声明时 | Callbacks | 回调 actor 名 |
| `pipe_target` | pipeline 构造时 | Pipelines | 下游消息 dict |
| `pipe_ignore` | actor 声明时 | Pipelines | 是否忽略上游结果 |
| `store_results` | actor 声明时 | Results | 是否存储结果 |
| `result_ttl` | actor 声明时 | Results | 结果过期时间 |
| `time_limit` | actor 声明时 | TimeLimit | 执行超时（毫秒） |
| `max_age` | actor 声明时 | AgeLimit | 消息最大存活时间 |
| `notify_shutdown` | actor 声明时 | ShutdownNotifications | 是否响应关闭信号 |
| `redis_message_id` | RedisBroker.enqueue | RedisBroker ack/nack | Redis 内唯一消息 ID |
| `broker_priority` | send_with_options | RabbitmqBroker | AMQP 消息优先级 |
| `on_retry_exhausted` | actor 声明时 | Retries | 重试耗尽后的通知 actor |

## 管道组合运算符

`Message.__or__` 返回 `pipeline([self, other])`，支持链式表达式：

```python
pipe = add.message(1, 2) | multiply.message(3) | log.message()
```

## get_result

```python
message.get_result(backend=None, block=False, timeout=None)
```

若未指定 backend，从全局 broker 的 Results 中间件获取。支持阻塞等待（block=True）和超时。

## MessageProxy：可变工作副本

Worker 从 Consumer 获取的不是 Message 本身，而是 `MessageProxy`：

```python
class MessageProxy:
    def __init__(self, message):
        self.failed = False
        self._message = message
        self._exception = None
```

- 通过 `__getattr__` 透明代理 Message 所有字段
- 增加可变的 `failed` 标志和 `_exception`
- `fail()` 设置 failed=True
- `stuff_exception(e)` / `clear_exception()` 管理异常引用
- 处理完成后调用 `clear_exception()` 打破引用循环，防止内存泄漏

MessageProxy 的存在使得不可变 Message 在线上传输时保持安全，同时 Worker 内部可以记录可变处理状态。

## 向后兼容

Message 保留了 namedtuple 时代的兼容接口：
- `_asdict = asdict`
- `_fields` 属性返回字段名元组
- `_replace(**changes)` 等价于 `dataclasses.replace`
- `message_datetime` 属性将 timestamp 转为 UTC datetime

## 相关概念

- [整体架构](00-overall-architecture.md)：Message 在五大组件中的位置
- [Actor 装饰器](01-actor-decorator.md)：send 构造 Message 并入队
- [Broker 抽象基类](02-broker-abstraction.md)：MessageProxy 由 Consumer 返回
- [Worker 线程模型](03-worker-threading-model.md)：WorkerThread 处理 MessageProxy
- [Encoder 编码层](06-encoder.md)：Message.encode/decode 委托给全局 Encoder
- [Results 结果后端](07-results-backend.md)：Message.get_result 获取结果
- [异常类层次结构](../references/error-hierarchy.md)：DecodeError 异常
