---
type: reference
scope: langgraph
name: checkpoint-persistence
version: "0.2"
source: https://github.com/langchain-ai/langgraph
description: 检查点、序列化与存储 API 参考——BaseCheckpointSaver、Checkpoint、SerializerProtocol、BaseStore
---

# 检查点与持久化 API 参考

## Checkpoint 数据结构

位于 `langgraph.checkpoint.base`。

```python
class Checkpoint(TypedDict):
    v: int                              # 格式版本，当前为 1
    id: str                             # UUIDv6，唯一且单调递增
    ts: str                             # ISO 8601 时间戳
    channel_values: dict[str, Any]      # 通道当前值
    channel_versions: ChannelVersions   # 通道名 → 版本号
    versions_seen: dict[str, ChannelVersions]  # 节点名 → {通道名: 已见版本}
    updated_channels: list[str] | None  # 本步更新的通道
```

`ChannelVersions = dict[str, str | int | float]`

### CheckpointMetadata

```python
class CheckpointMetadata(TypedDict, total=False):
    source: Literal["input", "loop", "update", "fork"]
    step: int
    parents: dict[str, str]
    run_id: str
    counters_since_delta_snapshot: dict[str, tuple[int, int]]
```

`source` 取值：
- `"input"`：由 invoke/stream/batch 的输入创建
- `"loop"`：由 Pregel 循环内部创建
- `"update"`：由手动状态更新创建
- `"fork"`：从另一个检查点复制创建

`counters_since_delta_snapshot` 是 DeltaChannel 的 beta 字段，映射通道名 → `(updates, supersteps)`。

### CheckpointTuple

```python
class CheckpointTuple(NamedTuple):
    config: RunnableConfig
    checkpoint: Checkpoint
    metadata: CheckpointMetadata
    parent_config: RunnableConfig | None = None
    pending_writes: list[PendingWrite] | None = None
```

### PendingWrite

```python
PendingWrite = tuple[str, str, Any]  # (task_id, channel, value)
```

### StateSnapshot

```python
class StateSnapshot(NamedTuple):
    values: dict[str, Any] | Any
    next: tuple[str, ...]
    config: RunnableConfig
    metadata: CheckpointMetadata | None
    created_at: str | None
    parent_config: RunnableConfig | None
    tasks: tuple[PregelTask, ...]
    interrupts: tuple[Interrupt, ...]
```

## BaseCheckpointSaver

```python
class BaseCheckpointSaver(Generic[V])
```

检查点保存器的基类。使用 `thread_id`（通过 config 的 `configurable.thread_id`）作为主键。

### 核心方法

| 方法 | 说明 |
|---|---|
| `put(config, checkpoint, metadata, new_versions)` | 保存检查点 |
| `aput(config, checkpoint, metadata, new_versions)` | 异步保存检查点 |
| `get_tuple(config)` | 获取 `CheckpointTuple` |
| `aget_tuple(config)` | 异步获取 |
| `list(config, *, filter=None, before=None, limit=None)` | 列出检查点 |
| `alist(config, ...)` | 异步列出 |
| `put_writes(config, writes, task_id)` | 保存待处理写入 |
| `aput_writes(config, writes, task_id)` | 异步保存写入 |

### 序列化器

`BaseCheckpointSaver` 使用 `SerializerProtocol` 序列化通道值。默认使用 `JsonPlusSerializer`。可通过构造函数传入自定义序列化器。

加密序列化通过 `EncryptedSerializer` 实现，实现 `CipherProtocol` 协议。

## UUID6

位于 `langgraph.checkpoint.base.id`。

```python
def uuid6(node: int | None = None, clock_seq: int | None = None) -> UUID
```

生成 UUIDv6，基于 100 纳秒时间戳，字段重排为数据库友好顺序。同纳秒内时间戳自动加1保证单调递增。

`UUID` 类继承自标准库 `uuid.UUID`，支持版本 6-8 的时间戳解码。

## 序列化协议

### SerializerProtocol

位于 `langgraph.checkpoint.serde.base`。

```python
@runtime_checkable
class SerializerProtocol(Protocol):
    def dumps_typed(self, obj: Any) -> tuple[str, bytes]: ...
    def loads_typed(self, data: tuple[str, bytes]) -> Any: ...
```

返回类型标签和字节数据，支持多格式反序列化。`pickle`、`json`、`orjson` 模块都是有效实现。

### UntypedSerializerProtocol

```python
class UntypedSerializerProtocol(Protocol):
    def dumps(self, obj: Any) -> bytes: ...
    def loads(self, data: bytes) -> Any: ...
```

旧式无类型序列化器协议。`maybe_add_typed_methods()` 将其包装为 `SerializerCompat`。

### CipherProtocol

```python
class CipherProtocol(Protocol):
    def encrypt(self, plaintext: bytes) -> tuple[str, bytes]: ...
    def decrypt(self, ciphername: str, ciphertext: bytes) -> bytes: ...
```

`encrypt` 返回 `(cipher_name, ciphertext)`。

### JsonPlusSerializer

位于 `langgraph.checkpoint.serde.jsonplus`。

```python
class JsonPlusSerializer(SerializerProtocol)
```

使用 `ormsgpack` 序列化，带可选 pickle 回退。安全注意事项：不应在不可信对象上使用。设置环境变量 `LANGGRAPH_STRICT_MSGPACK=true` 限制反序列化为内置安全类型允许列表。

构造参数：

- `pickle_fallback: bool = False`
- `allowed_json_modules: set[str] | None = None`
- `allowed_msgpack_modules: set[str] | None = None`

使用 langchain_core 的 `Reviver(allowed_objects="core")` 反序列化 LangChain 对象。

## BaseStore

位于 `langgraph.store.base`。提供跨线程和对话的长期记忆，支持分层命名空间和可选向量搜索。

### Item

```python
class Item:
    value: dict[str, Any]
    key: str
    namespace: tuple[str, ...]
    created_at: datetime
    updated_at: datetime
```

### 核心方法

| 方法 | 说明 |
|---|---|
| `get(namespace, key)` | 获取单项 |
| `aget(namespace, key)` | 异步获取 |
| `put(namespace, key, value)` | 写入项 |
| `aput(namespace, key, value)` | 异步写入 |
| `delete(namespace, key)` | 删除项 |
| `search(namespace, *, filter=None, limit=10, offset=0)` | 搜索命名空间 |
| `asearch(namespace, ...)` | 异步搜索 |
| `list_namespaces(*, prefix=None, suffix=None, max_depth=None)` | 列出命名空间 |

### 操作类型

- `GetOp(namespace, key)` — 获取操作
- `PutOp(namespace, key, value)` — 写入操作
- `SearchOp(namespace, ...)` — 搜索操作
- `ListNamespacesOp(...)` — 命名空间列表操作

### AsyncBatchedBaseStore

位于 `langgraph.store.base.batch`。

```python
class AsyncBatchedBaseStore(BaseStore)
```

在后台 asyncio 任务中批量处理操作以提高效率。通过 `asyncio.Queue` 提交操作，`_check_loop` 装饰器检测在主事件循环中同步调用并抛出 `InvalidStateError`。

## Runtime 上下文

### Runtime

位于 `langgraph.runtime`。

```python
@dataclass(kw_only=True, slots=True, frozen=True)
class Runtime(Generic[ContextT]):
    context: ContextT
    store: BaseStore | None
    stream_writer: StreamWriter
    previous: Any
    execution_info: ExecutionInfo
    server_info: ServerInfo | None
    control: RunControl | None
```

通过节点函数的 `runtime: Runtime[ContextT]` 参数注入。

### ExecutionInfo

```python
@dataclass(frozen=True, slots=True)
class ExecutionInfo:
    checkpoint_id: str
    checkpoint_ns: str
    task_id: str
    thread_id: str | None = None
    run_id: str | None = None
    node_attempt: int = 1
    node_first_attempt_time: float | None = None
```

### RunControl

```python
class RunControl:
    def request_drain(self, reason: str = "shutdown") -> None
    @property
    def drain_requested(self) -> bool
    @property
    def drain_reason(self) -> str | None
```

协作式排空控制，线程安全（单属性写）。

## 配置访问函数

位于 `langgraph.config`。

| 函数 | 返回 | 说明 |
|---|---|---|
| `get_config()` | `RunnableConfig` | 获取当前运行配置 |
| `get_store()` | `BaseStore` | 获取长期存储 |
| `get_stream_writer()` | `StreamWriter` | 获取自定义流写入器 |

这些函数依赖 contextvar 传播，Python < 3.11 在 async 上下文中受限。

## 相关概念

- [检查点机制](/langchain-ai/langgraph/concepts/checkpointing) — 持久化、时间旅行与状态恢复
- [Pregel 引擎](/langchain-ai/langgraph/concepts/pregel-engine) — 检查点在执行循环中的角色
- [通道系统](/langchain-ai/langgraph/concepts/channels) — DeltaChannel 增量检查点
- [错误处理](/langchain-ai/langgraph/concepts/error-handling) — RunControl 协作排空
