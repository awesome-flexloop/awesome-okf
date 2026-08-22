---
type: spec
scope: langgraph
name: insights
version: "0.2"
source: https://github.com/langchain-ai/langgraph
description: LangGraph 深度洞察——从源码中提炼的架构决策、执行模型与关键机制
---

# LangGraph 深度洞察

## 1. Channel 抽象：状态即通道，节点即 Actor

LangGraph 的核心架构建立在 **Pregel/BSP 计算模型**之上，其最精妙的设计是将"共享状态"拆解为一组类型化的 **Channel**，将"节点"实现为订阅/发布通道的 **Actor**。

`BaseChannel[Value, Update, Checkpoint]` 三元泛型设计（`channels/base.py`）将三个关注点正交分离：

- **Value**：通道持有的当前值类型（节点读取时看到的类型）。
- **Update**：通道接收的写入类型（节点返回值的类型）。
- **Checkpoint**：通道序列化时的表示类型（持久化格式）。

这三个类型不必相同。例如 `Topic` 通道的 Value 是 `Sequence[Value]`、Update 是 `Value | list[Value]`、Checkpoint 是 `list[Value]`。这种分离使得通道可以独立控制"读取语义""写入聚合"和"持久化表示"。

每种内置通道对应一种并发写入聚合策略：

| 通道 | 聚合语义 | 典型用途 |
|---|---|---|
| `LastValue` | 每步仅允许一个写入，多写报错 | 单生产者状态键 |
| `BinaryOperatorAggregate` | 用 reducer 函数 fold 所有写入 | 列表追加、计数器、消息合并 |
| `Topic` | 收集所有写入为序列（PubSub） | map-reduce 的 fan-out 结果 |
| `EphemeralValue` | 仅保留上一步值，读后清空 | 输入通道、触发信号 |
| `NamedBarrierValue` | 等待所有命名值到达后释放 | 多起点 join（fan-in 屏障） |
| `DeltaChannel` | 不存全量值，重放写入重建状态 | 大状态增量检查点 |

`StateGraph` 在编译时根据状态 schema 的 `Annotated` 元数据自动选择通道类型：无 reducer 的键映射为 `LastValue`，有 reducer 的键映射为 `BinaryOperatorAggregate`。这使得用户只需声明 `Annotated[list, operator.add]` 即可获得正确的并发聚合行为，而无需理解底层通道机制。

## 2. 超步（Superstep）执行循环：Plan → Execute → Update

Pregel 的执行遵循严格的 BSP（Bulk Synchronous Parallel）模型，每一步（超步）分三阶段（`pregel/main.py` 第464-477行）：

1. **Plan（`prepare_next_tasks`）**：检查每个节点的 triggers 通道在上一步是否有新版本。比较 `checkpoint["channel_versions"][chan]` 与 `versions_seen[node][chan]`，若通道版本更新则该节点被调度。`Send` 对象创建的 push 式任务也在此阶段加入。
2. **Execute（`PregelRunner`）**：通过 `BackgroundExecutor`/`AsyncBackgroundExecutor` 并行执行所有选中节点。节点执行期间，其写入通过 `CONFIG_KEY_SEND` 收集到待写入队列，但**对同一步的其他节点不可见**——这保证了 BSP 的隔离性。
3. **Update（`apply_writes`）**：所有节点完成后，按通道分组写入并调用 `channel.update(vals)`。更新通道版本号，记录 `versions_seen`。若通道更新后 `is_available()` 为 True，则该通道可触发下一步的节点。

循环在以下条件终止：
- 无节点被选中（`updated_channels.isdisjoint(trigger_to_nodes)`）→ 正常完成。
- 达到 `recursion_limit`（默认 10007）→ 抛出 `GraphRecursionError`。
- 节点调用 `interrupt()` → 抛出 `GraphInterrupt`，保存检查点后暂停。
- `RunControl.request_drain()` → 协作式排空，抛出 `GraphDrained`。

这种模型的关键优势是**确定性**：同一检查点恢复后的执行路径完全一致，因为节点间没有隐式的执行顺序依赖，只通过通道版本驱动。

## 3. 检查点即版本向量：时间旅行与增量持久化

LangGraph 的检查点系统不是简单的状态快照，而是一个**版本向量 + 写入日志**的结构（`checkpoint/base/__init__.py`）：

```python
Checkpoint = {
    "v": int,                    # 格式版本
    "id": str,                   # UUIDv6，单调递增可排序
    "ts": str,                   # ISO 8601 时间戳
    "channel_values": dict,      # 通道当前值
    "channel_versions": dict,    # 通道名 → 版本号
    "versions_seen": dict,       # 节点名 → {通道名: 已见版本}
    "updated_channels": list,    # 本步更新的通道
}
```

`versions_seen` 是调度的核心：它记录每个节点上次执行时看到的各通道版本。当通道版本号大于节点已见版本时，节点在下一步被触发。这使得检查点不仅能恢复状态，还能精确恢复"哪些节点应该执行"的调度决策。

检查点 ID 使用 **UUIDv6**（`checkpoint/base/id.py`），这是 UUIDv1 的字段重排版本，时间戳在前，保证数据库局部性和单调性。当同纳秒内生成多个 ID 时，时间戳自动加1确保唯一。

**DeltaChannel**（beta）将检查点优化推向极致：普通通道每步都序列化完整值，而 DeltaChannel 在检查点中仅存 `MISSING` 哨兵，状态重建通过重放祖先检查点中的 `PendingWrite` 日志实现。快照频率由 `snapshot_frequency`（默认1000次更新）和系统级 `DELTA_MAX_SUPERSTEPS_SINCE_SNAPSHOT`（默认5000步）双阈值控制，避免无限重放。reducer 必须满足**批处理不变性** `reducer(reducer(state, xs), ys) == reducer(state, xs + ys)`，使框架可以任意合并重放批次。

## 4. 控制流与数据流统一：Command、Send 与分支通道

LangGraph 将图的控制流（节点跳转）和数据流（状态更新）统一到通道写入机制中：

- **普通边** `add_edge(A, B)` 编译为：A 的 writers 中追加 `ChannelWriteEntry("branch:to:B", None)`；B 的 triggers 包含 `"branch:to:B"`。边的"触发"本质是向一个 `EphemeralValue` 通道写入 None。
- **条件边** `add_conditional_edges(A, path)` 编译为：A 的 writers 中追加一个 Runnable，执行 `path` 函数后根据返回值写入对应的 `branch:to:{target}` 通道或创建 `Send` 对象。
- **多起点 join** `add_edge([A, B], C)` 编译为：创建 `NamedBarrierValue(str, {"A", "B"})` 通道 `join:A+B:C`，A 和 B 完成时各写入自己的名称，屏障在两者都到达后释放，触发 C。
- **`Send(node, arg)`** 绕过通道版本机制，直接创建 push 式任务，允许动态扇出（map-reduce）。多个 Send 可以并行调用同一节点的不同实例。
- **`Command(update=..., goto=..., resume=..., graph=...)`** 是统一控制原语：`update` 更新状态通道，`goto` 跳转到节点（转换为分支通道写入或 Send），`resume` 恢复中断，`graph=Command.PARENT` 将命令冒泡到父图（抛出 `ParentCommand`）。

这种设计的优雅之处在于：**所有控制流都退化为通道写入**，Pregel 循环不需要理解"边"的概念，只需要处理通道更新和任务调度。`StateGraph` 到 `Pregel` 的编译过程本质上是将声明式图结构翻译为通道订阅/发布拓扑。

## 5. 可恢复中断与人机协同：interrupt/resume 协议

LangGraph 的人机协同（human-in-the-loop）机制建立在检查点系统之上，其核心是 `interrupt()` 函数（`types.py` 第851-974行）和 `Interrupt` 数据类：

1. 节点首次调用 `interrupt(value)` 时，通过 scratchpad 的中断计数器获取索引，检查是否有已存储的 resume 值。若无，构造 `Interrupt.from_ns(value, ns)`（ID 由命名空间的 `xxh3_128` 哈希确定性生成），抛出 `GraphInterrupt` 异常。
2. PregelLoop 捕获 `GraphInterrupt`，将中断信息存入检查点，保存当前状态后暂停执行。客户端通过 `stream_mode="updates"` 收到 `{"__interrupt__": (Interrupt(...),)}`。
3. 客户端使用 `Command(resume=value)` 恢复执行。框架将 resume 值存入 scratchpad，从检查点重新执行被中断的节点。
4. 节点重新执行时再次调用 `interrupt()`，此时 scratchpad 中有匹配索引的 resume 值，直接返回该值，节点继续执行后续逻辑。

关键设计决策：**中断恢复通过重新执行节点实现**，而非从中断点续执行。这要求节点函数是确定性的（或幂等的），因为中断前的逻辑会被重放。多中断按节点内调用顺序匹配 resume 值，每个任务的 resume 列表独立。

`interrupt_before`/`interrupt_after` 提供了更粗粒度的中断控制，在 `should_interrupt()` 中检查：自上次中断以来有任何通道更新，且触发节点在中断列表中。这不需要节点代码配合，在调度层即可实现。

## 6. 错误处理三层架构

LangGraph 的错误处理分为三个层次：

1. **节点级重试（`RetryPolicy`）**：`RetryPolicy` NamedTuple 配置指数退避重试（`initial_interval=0.5`、`backoff_factor=2.0`、`max_interval=128.0`、`max_attempts=3`、`jitter=True`），`retry_on` 可指定异常类型或谓词函数。`NodeTimeoutError` 默认可重试。
2. **节点级错误处理器（`error_handler`）**：通过 `add_node(..., error_handler=handler)` 或 `set_node_defaults(error_handler=...)` 注册。处理器接收失败节点的状态和 `NodeError`（含 `node` 和 `error`），可以返回 `Command` 进行恢复（更新状态、跳转节点）。处理器节点名为 `__error_handler__{node}`，不会捕获自身异常。
3. **图级冒泡**：未被处理器捕获的异常导致整个超步失败，异常通过 `GraphBubbleUp` 层次体系传播。`GraphDrained`（协作排空）、`GraphInterrupt`（中断）、`ParentCommand`（父图命令）都继承自 `GraphBubbleUp`，在执行器中被特殊处理——不视为错误，而是控制信号。

`NodeCancelledError` 解决了一个微妙的问题：`asyncio.CancelledError` 是 `BaseException` 子类，Pregel runner 将框架发起的取消（如同级任务失败后取消兄弟任务）视为静默清理。但用户节点自身抛出的 `CancelledError` 应被视为节点失败，重试层将其转换为 `NodeCancelledError` 使其流经正常错误路径。
