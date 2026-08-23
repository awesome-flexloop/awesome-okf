---
type: reference
title: "RedisBroker 内部结构"
description: "RedisBroker 的 Lua 脚本、Redis key 命名空间、消息生命周期与维护机制"
tags: [dramatiq, reference, redis, broker, lua]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  - path: "external/libs/remote/dramatiq/dramatiq/brokers/redis.py"
    facts: [F-038, F-039, F-040, F-046]
  - path: "external/libs/remote/dramatiq/dramatiq/brokers/redis/dispatch.lua"
    facts: [F-041, F-042, F-043, F-044, F-045]
---

# RedisBroker 内部结构

## Redis Key 命名空间

所有 key 以 `namespace`（默认 `"dramatiq"`）为前缀：

| Key 模式 | 类型 | 用途 |
|----------|------|------|
| `{ns}:{queue}` | List | 消息 ID 队列（RPUSH 入队，LPOP 消费） |
| `{ns}:{queue}.msgs` | Hash | message_id → 编码后的消息数据 |
| `{ns}:{queue}.XQ` | ZSet | 死信队列，score 为 nack 时间戳 |
| `{ns}:{queue}.XQ.msgs` | Hash | 死信消息数据 |
| `{ns}:__acks__.{worker_id}.{queue}` | Set | 该 worker 已拉取但未 ack 的 message_id 集合 |
| `{ns}:__heartbeats__` | ZSet | worker_id → 最后心跳时间戳 |

延迟队列使用与普通队列相同的 List 结构，key 为 `{ns}:{queue}.DQ`，消息在 ConsumerThread 内存中调度到期后重新 enqueue 到主队列。

## Lua 脚本：dispatch.lua

所有 broker 操作通过单个 Lua 脚本 `dispatch` 执行，保证原子性。脚本接收 8 个固定参数加命令特定参数：

```text
ARGV = [command, timestamp, queue_name, worker_id, heartbeat_timeout,
        dead_message_ttl, do_maintenance, max_unpack_size, ...]
KEYS = [namespace]
```

### 命令：enqueue

```lua
redis.call("hset", queue_messages, message_id, message_data)
redis.call("rpush", queue_full_name, message_id)
```

消息数据存入 Hash，message_id 推入 List 尾部。

### 命令：fetch

```lua
for i=1,prefetch do
    local message_id = redis.call("lpop", queue_full_name)
    if not message_id then break end
    message_ids[i] = message_id
    redis.call("sadd", queue_acks, message_id)
end
return redis.call("hmget", queue_messages, unpack(message_ids))
```

从 List 头部 LPOP 最多 prefetch 个消息，将 message_id 加入 acks Set（标记为"处理中"），再 HMGET 返回消息数据。

### 命令：ack

```lua
if redis.call("srem", queue_acks, message_id) > 0 then
    redis.call("hdel", queue_messages, message_id)
end
```

从 acks Set 移除 message_id，若成功则从 Hash 删除消息数据。SREM 返回 0 表示消息已被确认或不存在（幂等）。

### 命令：nack

```lua
if redis.call("srem", queue_acks, message_id) > 0 then
    local message = redis.call("hget", queue_messages, message_id)
    if message then
        redis.call("zadd", xqueue_full_name, timestamp, message_id)
        redis.call("hset", xqueue_messages, message_id, message)
        redis.call("hdel", queue_messages, message_id)
    end
end
```

从 acks Set 移除，将消息从主 Hash 移到 DLQ ZSet（score=nack 时间戳）和 DLQ Hash。

### 命令：requeue

```lua
for each message_id:
    if redis.call("srem", queue_acks, message_id) > 0 then
        if redis.call("hexists", queue_messages, message_id) > 0 then
            redis.call("rpush", queue_full_name, message_id)
        end
    end
```

将未确认的消息从 acks Set 移回 List 尾部，消息仍在 Hash 中。Worker 关闭时调用，防止消息丢失。

### 命令：purge

删除队列相关的所有 key（List、acks Set、消息 Hash、DLQ ZSet、DLQ Hash）。

### 命令：qsize

返回队列大小 = DQ.msgs 哈希长度 + DQ.acks 集合大小 + 主队列 msgs 哈希长度 + 主队列 acks 集合大小。

## 维护机制

每次 dispatch 调用有 `maintenance_chance`（默认 1000/1,000,000 = 0.1%）概率触发维护：

1. **清理死亡 worker 的未确认消息**：
   - 从 `__heartbeats__` ZSet 找出心跳超时（`timestamp - heartbeat_timeout`）的 worker
   - 遍历该 worker 的所有 acks Set，将其中仍存在于消息 Hash 的 message_id RPUSH 回队列
   - 删除空的 acks Set，从 heartbeats ZSet 移除该 worker

2. **清理过期死信**：
   - 从 DLQ ZSet 找出超过 `dead_message_ttl`（默认 7 天）的 message_id
   - 批量 ZREM + HDEL（分批处理避免 Lua 栈溢出）

`ack` 和 `nack` 命令在黑名单中（`MAINTENANCE_COMMAND_BLACKLIST`），不触发维护，因为它们已经是高频操作。

## Python 端分派

`RedisBroker.__getattr__` 将 `do_<command>` 调用转换为 Lua 脚本调用：

```python
def __getattr__(self, name):
    if not name.startswith("do_"):
        raise AttributeError(...)
    command = name[len("do_"):]
    return self._dispatch(command)
```

`_dispatch` 返回闭包，预绑定脚本和 keys，避免每次调用重复分配列表。

## Consumer 端

`_RedisConsumer` 维护本地 `message_cache`（列表）和 `queued_message_ids`（Set）：

- `__next__` 先从 cache pop，cache 空时调用 `do_fetch` 批量拉取
- `outstanding_message_count = len(queued_message_ids) + len(message_cache)`，据此决定是否需要 fetch
- 无消息时用 `compute_backoff` 渐进式长轮询（misses 递增，backoff 最大为 timeout）
- `ack`/`nack` 后从 `queued_message_ids` 中 discard

## 延迟消息

RedisBroker 不使用 Redis ZSet 做延迟调度。延迟消息在 enqueue 时路由到 `.DQ` List，由 ConsumerThread 的内存 PriorityQueue（`delay_queue`）管理到期时间。到期后 ConsumerThread 将消息重新 enqueue 到主队列。这意味着：
- 延迟精度受 worker_timeout 影响
- Worker 重启会丢失内存中的延迟消息（但消息仍在 `.DQ` List 中，重启后重新拉取）
- `.DQ` 队列的 prefetch 因子远大于普通队列（1000×线程数 vs 2×线程数）
