---
type: reference
scope: langgraph
name: channels-pregel
version: "0.2"
source: https://github.com/langchain-ai/langgraph
description: 通道系统与 Pregel 引擎 API 参考——BaseChannel 层次、Pregel/PregelNode/NodeBuilder
---

# 通道与 Pregel 引擎 API 参考

## BaseChannel

所有通道的抽象基类，位于 `langgraph.channels.base`。

```python
class BaseChannel(Generic[Value, Update, Checkpoint], ABC)
```

### 抽象成员

| 成员 | 签名 | 说明 |
|---|---|---|
| `ValueType` | `property -> Any` | 通道存储值的类型 |
| `UpdateType` | `property -> Any` | 通道接收更新的类型 |
| `from_checkpoint` | `(checkpoint) -> Self` | 从检查点恢复通道 |
| `get` | `() -> Value` | 获取当前值，空时抛出 `EmptyChannelError` |
| `update` | `(values: Sequence[Update]) -> bool` | 用一批更新修改通道值，返回是否变更 |

### 具体方法

| 方法 | 说明 |
|---|---|
| `copy()` | 复制通道，默认委托 `checkpoint()` + `from_checkpoint()` |
| `checkpoint()` | 返回可序列化状态，空通道返回 `MISSING` |
| `is_available()` | 通道是否有值 |
| `consume()` | 通知通道订阅任务已运行，默认 no-op |
| `finish()` | 通知通道 Pregel 运行结束，默认 no-op |

## 内建通道

### LastValue

```python
class LastValue(Generic[Value], BaseChannel[Value, Value, Value])
```

存储最后接收的值，每步最多接收一个写入。多写抛出 `InvalidUpdateError`（`INVALID_CONCURRENT_GRAPH_UPDATE`）。无 reducer 的状态键默认使用此通道。

### LastValueAfterFinish

```python
class LastValueAfterFinish(Generic[Value], BaseChannel[Value, Value, tuple[Value, bool]])
```

值仅在 `finish()` 后可用，`consume()` 时清空。用于 `defer=True` 的延迟节点。

### BinaryOperatorAggregate

```python
class BinaryOperatorAggregate(Generic[Value], BaseChannel[Value, Value, Value])
```

用二元运算符聚合所有写入。构造参数：

- `typ: type[Value]`
- `operator: Callable[[Value, Value], Value]`

支持 `Overwrite` 值绕过 reducer 直接设置值，同一步最多一个 Overwrite。有 reducer 的状态键（`Annotated[T, reducer]`）默认使用此通道。

### Topic

```python
class Topic(Generic[Value], BaseChannel[Sequence[Value], Value | list[Value], list[Value]])
```

PubSub 主题通道。构造参数 `accumulate: bool = False`。非累积模式每步清空，累积模式跨步保留。`get()` 返回值序列。

### EphemeralValue

```python
class EphemeralValue(Generic[Value], BaseChannel[Value, Value, Value])
```

仅保留前一步值，之后清空。构造参数 `guard: bool = True`，`guard=True` 时每步最多一个写入。START 节点的输入通道使用此类。

### NamedBarrierValue

```python
class NamedBarrierValue(Generic[Value], BaseChannel[Value, Value, set[Value]])
```

等待所有命名值到达后释放。构造参数 `names: set[Value]`。用于多起点 join 边。`consume()` 在全部到达后清空 seen 集合。

### NamedBarrierValueAfterFinish

类似 `NamedBarrierValue`，但额外要求 `finish()` 后才可用，用于 defer 节点的 join。

### DeltaChannel

```python
class DeltaChannel(Generic[Value], BaseChannel[Any, Any, Any])
```

Beta 功能。检查点中仅存哨兵，通过重放祖先写入重建状态。构造参数：

- `reducer: Callable[[Any, Sequence[Any]], Any]` — 签名 `(state, list[writes]) -> new_state`
- `typ: type | None = None`
- `snapshot_frequency: int = 1000`

reducer 必须确定性且满足批处理不变性：`reducer(reducer(state, xs), ys) == reducer(state, xs + ys)`。

关键方法 `replay_writes(writes: Sequence[PendingWrite])` 从旧到新重放写入，Overwrite 作为重置点。

## Pregel

```python
class Pregel(PregelProtocol[StateT, ContextT, InputT, OutputT], Generic[...])
```

位于 `langgraph.pregel.main`。结合 actors 和 channels，按 BSP 模型执行。通常不直接使用，通过 `StateGraph.compile()` 或 `@entrypoint` 间接创建。

### 执行模型

每超步三阶段：

1. **Plan** — `prepare_next_tasks()` 确定哪些节点的 triggers 通道有新版本
2. **Execute** — `BackgroundExecutor`/`AsyncBackgroundExecutor` 并行执行节点
3. **Update** — `apply_writes()` 将节点写入应用到通道

### 关键属性

| 属性 | 类型 | 说明 |
|---|---|---|
| `nodes` | `dict[str, PregelNode]` | 节点容器映射 |
| `channels` | `dict[str, BaseChannel]` | 通道实例映射 |
| `input_channels` | `str \| Sequence[str]` | 输入通道 |
| `output_channels` | `str \| Sequence[str]` | 输出通道 |
| `stream_channels` | `str \| Sequence[str]` | 流式输出通道 |
| `checkpointer` | `BaseCheckpointSaver \| None` | 检查点保存器 |
| `store` | `BaseStore \| None` | 长期存储 |
| `step` | `int` | 当前步数 |

## PregelNode

位于 `langgraph.pregel._read`。

```python
class PregelNode:
    channels: str | list[str]       # 读取的通道
    triggers: list[str]             # 触发此节点的通道
    mapper: Callable | None         # 输入转换
    writers: list[Runnable]         # 后处理写入器
    bound: Runnable[Any, Any]       # 节点核心逻辑
    retry_policy: Sequence[RetryPolicy] | None
    cache_policy: CachePolicy | None
    timeout: TimeoutPolicy | None
    tags: Sequence[str] | None
    metadata: Mapping[str, Any] | None
    is_error_handler: bool
    error_handler_node: str | None
```

节点不直接被图调用，而是作为创建 `PregelExecutableTask` 的容器。

## NodeBuilder

位于 `langgraph.pregel.main`。流式构建 PregelNode 的 API：

```python
node = (
    NodeBuilder()
    .subscribe_to("channel_a", "channel_b")  # 订阅并读取
    .read_from("channel_c")                  # 仅读取不触发
    .do(my_runnable)                          # 核心逻辑
    .write_to("output_channel")               # 写入通道
    .add_retry_policies(RetryPolicy(max_attempts=5))
    .set_timeout(30)
    .build()
)
```

| 方法 | 说明 |
|---|---|
| `subscribe_only(channel)` | 订阅单通道，节点接收值而非 dict |
| `subscribe_to(*channels, read=True)` | 订阅多通道，read=False 仅触发不读取 |
| `read_from(*channels)` | 读取通道但不订阅 |
| `do(node)` | 添加核心逻辑 runnable |
| `write_to(*channels, **kwargs)` | 添加通道写入 |
| `meta(*tags, **metadata)` | 添加标签和元数据 |
| `add_retry_policies(*policies)` | 添加重试策略 |
| `add_cache_policy(policy)` | 设置缓存策略 |
| `set_timeout(timeout)` | 设置超时 |
| `build()` | 构建 `PregelNode` |

## ChannelWrite / ChannelRead

### ChannelWriteEntry

```python
class ChannelWriteEntry(NamedTuple):
    channel: str
    value: Any = PASSTHROUGH        # PASSTHROUGH 表示使用节点输出
    skip_none: bool = False
    mapper: Callable | None = None
```

### ChannelWriteTupleEntry

```python
class ChannelWriteTupleEntry(NamedTuple):
    mapper: Callable[[Any], Sequence[tuple[str, Any]] | None]
    value: Any = PASSTHROUGH
    static: Sequence[tuple[str, Any, str | None]] | None = None
```

### ChannelRead

静态方法 `ChannelRead.do_read(config, *, select, fresh=False, mapper=None)` 从 `CONFIG_KEY_READ` 读取状态。`fresh=True` 时复制通道并应用当前任务的局部写入，供条件边使用。

## 执行器

### BackgroundExecutor

同步后台执行器，基于线程池。上下文管理器返回 `submit` 函数。

### AsyncBackgroundExecutor

异步后台执行器，基于 asyncio 事件循环，支持 `max_concurrency` 信号量限流。`GraphBubbleUp` 异常不被视为错误。

## 算法函数

| 函数 | 说明 |
|---|---|
| `prepare_next_tasks(...)` | 根据通道版本和 versions_seen 确定下一步执行的节点 |
| `apply_writes(checkpoint, channels, tasks, get_next_version, trigger_to_nodes)` | 将任务写入应用到通道和检查点 |
| `should_interrupt(checkpoint, interrupt_nodes, tasks)` | 检查是否应中断 |
| `local_read(scratchpad, channels, managed, task, select, fresh)` | 读取节点可见状态 |
| `increment(current, channel)` | 默认版本号递增函数 |

## 相关概念

- [通道系统](/langchain-ai/langgraph/concepts/channels) — 通道类型详解与选择指南
- [Pregel 引擎](/langchain-ai/langgraph/concepts/pregel-engine) — BSP 执行模型深度解析
- [状态图](/langchain-ai/langgraph/concepts/state-graph) — StateGraph 如何编译为 Pregel
- [检查点持久化](/langchain-ai/langgraph/references/checkpoint-persistence) — Checkpoint 与序列化 API
