---
type: concept
scope: langgraph
name: checkpointing
version: "0.2"
source: https://github.com/langchain-ai/langgraph
description: 检查点机制——状态持久化、版本向量、时间旅行、DeltaChannel 增量检查点
---

# 检查点机制（Checkpointing）

检查点是 LangGraph 有状态能力的基石。它在每个超步后保存图的完整状态快照，支持暂停/恢复、时间旅行、人机协同和崩溃恢复。

## Checkpoint 结构

检查点是一个 TypedDict，包含状态值和调度元数据：

```python
Checkpoint = {
    "v": 1,                              # 格式版本
    "id": "0f8fad5b-d9cb-6967-...",      # UUIDv6，单调递增可排序
    "ts": "2026-08-23T10:00:00+00:00",   # ISO 8601 时间戳
    "channel_values": {                  # 通道当前值
        "messages": [...],
        "branch:to:chatbot": None,
    },
    "channel_versions": {                # 通道版本号
        "messages": 5,
        "branch:to:chatbot": 3,
    },
    "versions_seen": {                   # 各节点已见的通道版本
        "chatbot": {"branch:to:chatbot": 3, "messages": 4},
    },
    "updated_channels": ["messages"],    # 本步更新的通道
}
```

`versions_seen` 是调度的核心——它记录每个节点上次执行时看到的版本，版本不匹配时节点被重新触发。这使得检查点不仅保存数据，还保存"执行到哪了"的调度状态。

## 检查点 ID

检查点使用 **UUIDv6**（`checkpoint/base/id.py`），这是 UUIDv1 的字段重排版本：

- 时间戳在前 60 位，保证数据库索引局部性和时间排序
- 同纳秒内多个 ID 自动递增时间戳，保证单调性
- 48 位随机 node ID 和 14 位随机 clock_seq

因此检查点 ID 既是唯一标识符，又可按时间排序。

## Checkpointer

`BaseCheckpointSaver` 是检查点保存器的基类。核心方法：

| 方法 | 职责 |
|---|---|
| `put(config, checkpoint, metadata, new_versions)` | 保存检查点 |
| `get_tuple(config)` | 获取检查点及其元数据 |
| `list(config, filter, before, limit)` | 列出历史检查点 |
| `put_writes(config, writes, task_id)` | 保存待处理写入 |

内置实现：
- `InMemorySaver`：内存存储，用于开发测试
- `SqliteSaver`：SQLite 持久化
- `PostgresSaver`/`AsyncPostgresSaver`：PostgreSQL 持久化

### thread_id

检查点通过 `thread_id`（config 的 `configurable.thread_id`）分区。同一 thread 的检查点形成线性历史链，不同 thread 完全隔离：

```python
config = {"configurable": {"thread_id": "user-123-conversation"}}
graph.invoke(input, config)
```

- 单次工作流：每次运行使用唯一 thread_id
- 对话记忆：同一会话复用 thread_id，状态跨调用累积
- 子图：使用 `checkpoint_ns`（命名空间）隔离，格式 `graph|subgraph|subsubgraph`

## Checkpointer 类型

编译时 `checkpointer` 参数接受三种值：

| 值 | 行为 |
|---|---|
| `None` | 无 checkpointer；作为子图时继承父图的 checkpointer |
| `False` | 显式禁用，不继承父图 checkpointer |
| `True` | 启用（使用继承的或默认的 checkpointer） |
| `BaseCheckpointSaver` 实例 | 使用指定的保存器 |

## 状态访问 API

编译后的图提供状态访问方法：

```python
# 获取当前状态快照
snapshot = graph.get_state(config)
# StateSnapshot(values, next, config, metadata, tasks, interrupts)

# 列出历史检查点（时间旅行）
for state in graph.get_state_history(config):
    print(state.values, state.metadata["step"])

# 手动更新状态
graph.update_state(config, values={"key": "new_value"}, as_node="node_name")
```

### StateSnapshot

```python
StateSnapshot = NamedTuple(
    values: dict,           # 当前通道值
    next: tuple[str, ...],  # 下一步要执行的节点
    config: RunnableConfig,
    metadata: CheckpointMetadata,
    created_at: str | None,
    parent_config: RunnableConfig | None,
    tasks: tuple[PregelTask, ...],
    interrupts: tuple[Interrupt, ...],
)
```

## 时间旅行

利用检查点历史，可以回退到任意历史状态并重新执行：

```python
# 找到要回退到的检查点
history = list(graph.get_state_history(config))
target = history[5]  # 回退5步

# 从该检查点重新执行
graph.invoke(None, target.config)
```

`update_state()` 可以在不执行节点的情况下修改状态，创建"fork"（`source="fork"`），用于纠正错误或注入数据。

## Pending Writes

除了检查点，LangGraph 还持久化**待处理写入**（`PendingWrite`）：

```python
PendingWrite = tuple[str, str, Any]  # (task_id, channel, value)
```

这些写入在检查点之间保存，用于：
1. **崩溃恢复**：节点已执行但检查点未保存时，写入不丢失
2. **DeltaChannel 重放**：增量通道通过重放写入日志重建状态
3. **中断恢复**：中断时节点的部分写入被保留

## DeltaChannel 增量检查点

对于大状态（如长消息历史），每步序列化全量值开销很大。`DeltaChannel`（beta）优化了这一点：

### 工作原理

1. 普通通道每步在 `channel_values` 中存全量值
2. DeltaChannel 的 `checkpoint()` 返回 `MISSING`（哨兵），不存全量值
3. 节点写入通过 `put_writes()` 持久化为 `PendingWrite` 日志
4. 重建状态时，从最近的快照开始，重放后续写入

### 快照策略

快照（全量值）在两种情况下写入：
- **更新计数**：通道更新次数达到 `snapshot_frequency`（默认 1000）
- **超步上限**：距上次快照的超步数达到 `DELTA_MAX_SUPERSTEPS_SINCE_SNAPSHOT`（默认 5000，环境变量可配）

超步上限确保即使通道停止更新，也不会无限增长重放链。

### Reducer 要求

DeltaChannel 使用**批量 reducer**，签名不同于 BinaryOperatorAggregate：

```python
def batch_reducer(state, writes):
    # state: 当前累积值
    # writes: 本批所有写入的列表
    # return: 新状态
    return state + writes
```

必须满足**批处理不变性**：

```
reducer(reducer(state, xs), ys) == reducer(state, xs + ys)
```

这允许框架任意合并重放批次，而不改变重建结果。Overwrite 值作为重放中的重置点——最后一个 Overwrite 之后的写入才会被应用。

## 序列化

检查点值通过 `SerializerProtocol` 序列化：

```python
class SerializerProtocol(Protocol):
    def dumps_typed(self, obj: Any) -> tuple[str, bytes]: ...
    def loads_typed(self, data: tuple[str, bytes]) -> Any: ...
```

返回类型标签和字节数据，支持多格式。默认使用 `JsonPlusSerializer`（基于 ormsgpack），带可选 pickle 回退。

### 安全考虑

`JsonPlusSerializer` 在反序列化时可执行任意代码（通过 LangChain 的 Reviver 机制）。生产环境应：
- 设置 `LANGGRAPH_STRICT_MSGPACK=true` 限制为安全类型允许列表
- 或在构造时传入 `allowed_msgpack_modules`
- 保护检查点数据库的访问权限

### 加密

`EncryptedSerializer` 实现 `CipherProtocol`，在序列化后加密、反序列化前解密，支持自定义加密后端。

## Metadata

每个检查点关联 `CheckpointMetadata`：

```python
{
    "source": "input" | "loop" | "update" | "fork",
    "step": int,
    "parents": dict[str, str],     # 父图命名空间 → 检查点 ID
    "run_id": str,
    "counters_since_delta_snapshot": dict[str, tuple[int, int]],  # beta
}
```

`source` 标识检查点来源：
- `"input"`：首次接收输入时创建（step=-1）
- `"loop"`：Pregel 循环内部创建（step=0,1,2,...）
- `"update"`：`update_state()` 手动更新
- `"fork"`：从历史检查点分叉

## Store：长期记忆

除了检查点（短期记忆，与 thread 绑定），LangGraph 还提供 `BaseStore`（长期记忆，跨 thread 持久化）：

```python
store = InMemoryStore()
graph = builder.compile(store=store)

# 节点内访问
def node(state, config):
    store = get_store()
    item = store.get(("user_data", "user123"), "preferences")
    store.put(("user_data", "user123"), "preferences", {"theme": "dark"})
```

Store 支持分层命名空间（元组路径）、键值存储和可选向量搜索。`AsyncBatchedBaseStore` 在后台批量异步操作以提高效率。

## 相关概念

- [Pregel 引擎](/ai/langchain-ai/langgraph/concepts/pregel-engine) — 检查点在超步中的角色
- [通道系统](/ai/langchain-ai/langgraph/concepts/channels) — DeltaChannel 与通道检查点表示
- [错误处理](/ai/langchain-ai/langgraph/concepts/error-handling) — 中断与恢复机制
- [API 参考](/ai/langchain-ai/langgraph/references/checkpoint-persistence) — 检查点完整 API
