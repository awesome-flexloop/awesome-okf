---
type: concept
title: "Results 结果后端"
description: "ResultBackend 抽象、Redis/Stub 后端实现、Results 中间件工作流程、结果获取与异常包装"
tags: [dramatiq, task-queue, results, backend, redis, middleware]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [../references/built-in-middleware.md, ../references/error-hierarchy.md]
  facts: [F-035, F-083, F-084, F-085, F-086, F-087, F-088]
---

# 07 · Results 结果后端

## 架构

结果存储由两部分组成：
1. **Results 中间件**：在 `after_process_message` 钩子中自动存储 actor 返回值或异常
2. **ResultBackend**：抽象存储接口，有 Redis 和 Stub 两种实现

```text
Actor 返回值
    │
    ▼
Results.after_process_message
    │
    ├── 成功 → backend.store_result(message, result, ttl)
    └── 失败 → backend.store_exception(message, exception, ttl)
                    │
                    ▼
            Redis List / 内存 dict
```

## ResultBackend 抽象

### 核心方法

| 方法 | 说明 |
|------|------|
| `get_result(message, block=False, timeout=10000)` | 获取结果（模板方法） |
| `store_result(message, result, ttl)` | 存储成功结果 |
| `store_exception(message, exception, ttl)` | 存储异常 |
| `build_message_key(message)` | 生成存储 key |

### get_result 模板方法

基类实现了轮询逻辑：
1. 调用子类 `_get(key)` 获取结果
2. 结果为 `Missing` 且 `block=True`：用 `compute_backoff` 指数退避重试，超时抛出 `ResultTimeout`
3. 结果为 `Missing` 且 `block=False`：抛出 `ResultMissing`
4. 结果存在：调用 `unwrap_result` 解包

### Key 生成

```python
message_key = f"{namespace}:{queue_name}:{actor_name}:{message_id}"
# 默认：hashlib.md5(message_key.encode()).hexdigest()
# use_namespace_prefix_keys=True：直接使用明文 key
```

### 结果包装

- `wrap_result(res)`：no-op（前向兼容设计）
- `wrap_exception(e)`：`{"__t": "dramatiq.results.Result", "exn": {"type":..., "msg":...}}`
- `unwrap_result(res)`：检测到 `__t` 标记则抛出 `ResultFailure`，否则直接返回

## RedisBackend

使用 Redis List 存储结果：

```python
def _store(self, message_key, result, ttl):
    with self.client.pipeline() as pipe:
        pipe.delete(message_key)
        pipe.lpush(message_key, self.encoder.encode(result))
        pipe.pexpire(message_key, ttl)
        pipe.execute()
```

获取方式：
- 阻塞：`BRPOPLPUSH key key timeout`（原子地弹出并推回，实现长轮询）
- 非阻塞：`LINDEX key 0`

注意：子秒级超时不被尊重（Redis 命令精度为秒）。

## StubBackend

内存实现，用于测试：

```python
results: dict[str, tuple[Optional[str], Optional[float]]] = {}

def _get(self, message_key):
    data, expiration = self.results.get(message_key, (None, None))
    if data is not None and time.monotonic() < expiration:
        return self.encoder.decode(data)
    return Missing
```

## Results 中间件

### 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `backend` | 必填 | ResultBackend 实例 |
| `store_results` | `False` | 是否默认存储结果（可按 actor 覆盖） |
| `result_ttl` | `600000`（10分钟） | 结果过期时间（毫秒） |

### actor_options

- `store_results`（bool）：该 actor 是否存储结果
- `result_ttl`（int）：该 actor 的结果 TTL

### 钩子逻辑

- **after_process_message**：若 `store_results=True` 且无异常，调用 `store_result`；若返回值非 None 但未开启存储，发出 warning
- **after_skip_message**：若消息被跳过但未失败，存储 None
- **after_nack**：若消息失败，调用 `store_exception`

选项查找优先级：message.options → actor.options → middleware 默认值。

## 使用方式

```python
from dramatiq.results import Results
from dramatiq.results.backends import RedisBackend

backend = RedisBackend()
broker.add_middleware(Results(backend=backend))

@dramatiq.actor(store_results=True)
def add(x, y):
    return x + y

message = add.send(1, 2)
result = message.get_result(backend=backend, block=True, timeout=5000)
```

## MemcachedBackend

通过懒加载提供（`dramatiq[memcached]` extra），导入失败时发出 ImportWarning。

## 相关概念

- [整体架构](00-overall-architecture.md)：Results 是可选中间件
- [Broker 抽象基类](02-broker-abstraction.md)：broker.get_results_backend() 查找 Results 中间件
- [Message 与序列化](04-message-and-serialization.md)：Message.get_result 从 broker 获取 backend
- [Middleware 中间件管道](05-middleware-pipeline.md)：Results 作为中间件接入洋葱模型
- [Encoder 编码层](06-encoder.md)：ResultBackend 使用 Encoder 序列化结果
- [异常类层次结构](../references/error-hierarchy.md)：ResultMissing/ResultTimeout/ResultFailure
