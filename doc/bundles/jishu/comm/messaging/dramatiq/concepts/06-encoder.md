---
type: concept
title: "Encoder 编码层"
description: "Encoder 抽象基类、JSONEncoder/PickleEncoder 实现、全局编码器管理、MessageData 类型别名"
tags: [dramatiq, task-queue, encoder, serialization, json, pickle]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [../references/error-hierarchy.md]
  facts: [F-024, F-025, F-026, F-027]
---

# 06 · Encoder 编码层

## 职责

Encoder 负责 Message 在内存对象与线上 bytes 之间的双向转换。所有进入 broker 的消息都先经过 Encoder.encode()，所有从 broker 消费的消息都经过 Encoder.decode()。

## Encoder 抽象基类

```python
class Encoder(abc.ABC):
    @abc.abstractmethod
    def encode(self, data: MessageData) -> bytes: ...

    @abc.abstractmethod
    def decode(self, data: bytes) -> MessageData: ...
```

`MessageData = dict[str, typing.Any]`，即 Message.asdict() 的返回类型。

## JSONEncoder（默认）

```python
class JSONEncoder(Encoder):
    def encode(self, data):
        return json.dumps(data, separators=(",", ":")).encode("utf-8")

    def decode(self, data):
        data_str = data.decode("utf-8")
        return json.loads(data_str)
```

特点：
- 使用紧凑分隔符（无空格），最小化消息体积
- UTF-8 编码
- 解码时分别处理 `UnicodeDecodeError` 和 `JSONDecodeError`，统一包装为 `DecodeError`
- 安全：可解码不可信来源的数据
- 限制：args/kwargs 中的值必须是 JSON 可序列化类型

## PickleEncoder

```python
class PickleEncoder(Encoder):
    def encode(self, data):
        return pickle.dumps(data)

    def decode(self, data):
        return pickle.loads(data)
```

特点：
- 支持任意 Python 对象（包括 datetime、自定义类实例等）
- **不安全**：文档明确警告"not secure against maliciously-constructed data"
- 反序列化不可信数据可导致任意代码执行
- 适用于完全控制消息生产者和消费者的可信环境

## 全局编码器管理

```python
global_encoder: Encoder = JSONEncoder()

def get_encoder() -> Encoder:
    return global_encoder

def set_encoder(encoder: Encoder) -> None:
    global global_encoder
    global_encoder = encoder
```

默认使用 JSONEncoder。可通过 `set_encoder(PickleEncoder())` 全局替换。Message.encode/decode 内部调用 `global_encoder`，因此编码器选择对业务代码透明。

## 与 ResultBackend 的关系

ResultBackend 也持有 encoder 引用（默认 `get_encoder()`），用于结果的序列化/反序列化。可通过构造函数传入独立的 encoder 实例，实现消息和结果使用不同编码方式。

## 扩展自定义 Encoder

继承 `Encoder` 并实现 `encode`/`decode`：

```python
class MsgPackEncoder(Encoder):
    def encode(self, data):
        return msgpack.packb(data, use_bin_type=True)

    def decode(self, data):
        return msgpack.unpackb(data, raw=False)

set_encoder(MsgPackEncoder())
```

需注意生产者和所有消费者必须使用相同编码器，否则 decode 会失败。

## 相关概念

- [整体架构](00-overall-architecture.md)：Encoder 是消息序列化的基础组件
- [Message 与序列化](04-message-and-serialization.md)：Message.encode/decode 委托给全局 Encoder
- [Results 结果后端](07-results-backend.md)：ResultBackend 也使用 Encoder 序列化结果
- [异常类层次结构](../references/error-hierarchy.md)：DecodeError 在解码失败时抛出
