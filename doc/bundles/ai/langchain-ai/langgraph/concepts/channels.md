---
type: concept
scope: langgraph
name: channels
version: "0.2"
source: https://github.com/langchain-ai/langgraph
description: 通道系统详解——BaseChannel 抽象、内建通道类型、reducer 机制与 DeltaChannel
---

# 通道系统（Channels）

通道是 LangGraph 中节点间通信的核心抽象。每个状态键对应一个通道实例，通道定义了三个正交语义：**如何存储值**、**如何聚合并发写入**、**如何序列化检查点**。

## BaseChannel 抽象

```python
class BaseChannel(Generic[Value, Update, Checkpoint], ABC):
    @abstractmethod
    def get(self) -> Value: ...

    @abstractmethod
    def update(self, values: Sequence[Update]) -> bool: ...

    @abstractmethod
    def from_checkpoint(self, checkpoint: Checkpoint) -> Self: ...
```

三个泛型参数：

| 参数 | 含义 | 示例（Topic） |
|---|---|---|
| `Value` | `get()` 返回的值类型 | `Sequence[Value]` |
| `Update` | `update()` 接收的写入类型 | `Value \| list[Value]` |
| `Checkpoint` | 序列化表示类型 | `list[Value]` |

生命周期方法：
- `consume()`：订阅任务运行后调用，可清空值（用于临时通道）
- `finish()`：Pregel 运行结束时调用，可使延迟值可用
- `is_available()`：通道是否有值可读
- `checkpoint()`：返回可序列化状态

## 内建通道类型

### LastValue

存储最后接收的值，每步最多一个写入。无 reducer 的状态键默认使用。

```python
class State(TypedDict):
    name: str  # LastValue 通道
```

同一步多个节点写入同一 `LastValue` 通道会抛出 `InvalidUpdateError`，错误码 `INVALID_CONCURRENT_GRAPH_UPDATE`。

### BinaryOperatorAggregate

用二元运算符（reducer）聚合所有写入。有 reducer 的 `Annotated` 键默认使用。

```python
from typing import Annotated
import operator

class State(TypedDict):
    count: Annotated[int, operator.add]      # 求和
    items: Annotated[list, operator.add]    # 列表拼接
```

`update(values)` 依次执行 `self.value = operator(self.value, value)`。第一个值作为初始值，后续值 fold。

#### Overwrite

`Overwrite` 值可绕过 reducer 直接设置通道值：

```python
from langgraph.types import Overwrite

def node(state):
    return {"items": Overwrite(["reset"])}  # 直接替换，而非追加
```

同一步多个 Overwrite 会报错。支持三种序列化形式：`Overwrite` 实例、`{"__overwrite__": value}` 字典、`{"value": ..., "type": "__overwrite__"}` JSON 形式。

### Topic

PubSub 主题通道，收集所有写入为序列。

```python
from langgraph.channels import Topic

# accumulate=False（默认）：每步清空
# accumulate=True：跨步累积
channel = Topic(str, accumulate=True)
```

`update()` 展平嵌套列表后 extend 到内部 values。`get()` 返回值列表的副本。

### EphemeralValue

仅保留前一步的值，之后自动清空。用于输入通道和触发信号。

```python
EphemeralValue(str)           # guard=True：每步最多一个写入
EphemeralValue(str, guard=False)  # 多写入时取最后一个
```

无更新（空序列）时将值设为 `MISSING`。START 节点的输入通道使用此类。

### NamedBarrierValue

屏障通道，等待所有命名值到达后才可用。用于多起点 join 边。

```python
NamedBarrierValue(str, names={"node_a", "node_b"})
```

每个起点完成时写入自己的名称，`seen == names` 时 `is_available()` 返回 True。`consume()` 清空 seen 集合。

### LastValueAfterFinish / NamedBarrierValueAfterFinish

这两个变体分别对应 `LastValue` 和 `NamedBarrierValue`，但值仅在 `finish()` 调用后可用。用于 `defer=True` 的延迟节点——延迟节点在所有普通节点完成后的 finish 阶段才看到值。

### DeltaChannel（Beta）

DeltaChannel 是一种优化通道，不在检查点中存储全量值，而是通过重放祖先写入日志重建状态。

```python
from langgraph.channels.delta import DeltaChannel

def batch_reducer(state, writes):
    # state: 当前累积值
    # writes: 本批写入列表
    return state + writes

class State(TypedDict):
    messages: Annotated[list, DeltaChannel(batch_reducer, snapshot_frequency=1000)]
```

关键特性：
- **批量 reducer**：签名 `(state, list[writes]) -> new_state`，而非 `(old, new) -> merged`
- **批处理不变性**：`reducer(reducer(state, xs), ys) == reducer(state, xs + ys)`
- **快照频率**：每 N 次更新写一次全量快照（默认 1000）
- **系统级上限**：`DELTA_MAX_SUPERSTEPS_SINCE_SNAPSHOT`（默认 5000 步）强制快照，防止无限重放
- **检查点表示**：非快照步返回 `MISSING`，重建时通过 saver 的 `get_delta_channel_history` 获取祖先写入

## 通道与 Schema 的映射

`StateGraph` 在 `_add_schema()` 中通过 `_get_channels(schema)` 检查类型注解：

```python
# 无 reducer → LastValue
name: str

# 有 reducer（Annotated 第二个参数是 callable）→ BinaryOperatorAggregate
items: Annotated[list, operator.add]

# 显式通道实例 → 使用该通道
messages: Annotated[list, DeltaChannel(reducer)]
```

相同键在不同 schema（state/input/output）中必须映射到兼容的通道类型。`LastValue` 可以与其他通道共存（因为它是无 reducer 的默认值），但不同 reducer 的 `BinaryOperatorAggregate` 不能映射同一键。

## 通道在执行循环中的角色

在 Pregel 超步中，通道经历以下阶段：

1. **Plan**：检查通道 `channel_versions` 是否大于节点的 `versions_seen`，决定触发哪些节点
2. **Execute**：节点读取通道值（通过 `CONFIG_KEY_READ`），写入暂存（通过 `CONFIG_KEY_SEND`）
3. **Update**：
   - 对触发通道调用 `consume()`（清空临时值）
   - 按通道分组写入，调用 `channel.update(vals)`
   - 对未更新通道调用 `update([])`（通知新步）
   - 若无通道触发节点，调用所有通道的 `finish()`
4. **Checkpoint**：调用 `channel.checkpoint()` 获取序列化值，保存到检查点

## 选择合适的通道

| 场景 | 推荐通道 |
|---|---|
| 单生产者状态值 | `LastValue`（默认） |
| 多节点追加列表 | `BinaryOperatorAggregate` + `operator.add` |
| 消息历史合并 | `BinaryOperatorAggregate` + `add_messages` |
| Map-reduce 扇出结果 | `Topic(accumulate=True)` |
| 多节点 fan-in 同步 | `NamedBarrierValue`（通过多起点边自动创建） |
| 图输入/触发信号 | `EphemeralValue`（自动用于 START） |
| 超大状态增量检查点 | `DeltaChannel`（beta） |

## 相关概念

- 状态图 — Schema 如何映射到通道
- Pregel 引擎 — 通道在超步中的生命周期
- 检查点机制 — DeltaChannel 的持久化优化
- API 参考 — 通道完整 API
