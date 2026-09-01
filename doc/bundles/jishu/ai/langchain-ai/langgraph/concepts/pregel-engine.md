---
type: concept
scope: langgraph
name: pregel-engine
version: "0.2"
source: https://github.com/langchain-ai/langgraph
description: Pregel 执行引擎——BSP 超步模型、任务调度、写入应用与循环终止
---

# Pregel 引擎

Pregel 是 LangGraph 的底层执行引擎，实现了 **BSP（Bulk Synchronous Parallel）** 计算模型。`StateGraph.compile()` 将声明式图结构翻译为 Pregel 的通道订阅/发布拓扑，由 Pregel 循环驱动执行。

## BSP 超步模型

Pregel 的执行由一系列**超步（superstep）**组成，每个超步严格分三阶段：

```
┌──────────────────────────────────────────────────┐
│                 超步 N                            │
│                                                  │
│  ┌──────────┐   ┌───────────┐   ┌────────────┐  │
│  │  Plan    │ → │ Execute   │ → │  Update    │  │
│  │ 选择节点  │   │ 并行执行   │   │ 应用写入    │  │
│  └──────────┘   └───────────┘   └────────────┘  │
│                                                  │
│  有节点被触发？ ──是──→ 超步 N+1                  │
│       └─否──→ 运行结束                           │
└──────────────────────────────────────────────────┘
```

### Plan 阶段

`prepare_next_tasks()` 检查每个节点的 triggers 通道：

1. 对每个节点，比较其 `triggers` 通道的当前版本（`channel_versions`）与节点已见版本（`versions_seen[node]`）
2. 若任一 trigger 通道版本更新，节点被调度执行
3. `Send` 对象创建的 push 式任务也在此阶段加入
4. 检查 `interrupt_before`/`interrupt_after`，若需要则暂停

### Execute 阶段

- 通过 `BackgroundExecutor`（同步，线程池）或 `AsyncBackgroundExecutor`（异步，asyncio）并行执行所有选中节点
- 节点执行期间，其输出通过 `CONFIG_KEY_SEND` 收集到 `writes` 双端队列
- **写入对同一步的其他节点不可见**——这保证了 BSP 的隔离性
- 节点可通过 `CONFIG_KEY_READ` 的 `fresh=True` 读取包含自身局部写入的状态副本（用于条件边）
- 任一节点失败时，根据 retry_policy 重试；最终失败则取消同级任务

### Update 阶段

`apply_writes()` 按确定性顺序处理写入：

1. 按 `task.path[:3]` 排序任务，保证更新顺序确定
2. 更新每个节点的 `versions_seen`
3. 对触发通道调用 `consume()`（清空临时通道值）
4. 按通道分组所有写入，调用 `channel.update(vals)`
5. 更新的通道获得新版本号
6. 对本步未更新的通道调用 `update([])`（通知新步）
7. 若无更新通道能触发后续节点，调用所有通道的 `finish()`（释放延迟节点）

## PregelLoop

`PregelLoop`（`pregel/_loop.py`）是循环的核心协调器，管理：

- **检查点生命周期**：加载父检查点、创建新检查点、保存写入
- **任务队列**：`tasks: dict[str, PregelExecutableTask]`
- **状态**：`status` 字段取值 `"input"`/`"pending"`/`"done"`/`"draining"`/`"interrupt_before"`/`"interrupt_after"`/`"out_of_steps"`
- **流输出**：通过 `StreamProtocol` 发射值和调试事件
- **中断处理**：捕获 `GraphInterrupt`，保存检查点后暂停

### 同步与异步

- `SyncPregelLoop`：同步执行，使用 `BackgroundExecutor`（线程池）
- `AsyncPregelLoop`：异步执行，使用 `AsyncBackgroundExecutor`（asyncio + 可选信号量限流）

两者共享大部分逻辑，通过 submit 函数抽象执行差异。

## PregelNode 与任务

`PregelNode` 是节点的静态定义（容器），`PregelExecutableTask` 是运行时任务实例：

```python
@dataclass(frozen=True, slots=True)
class PregelExecutableTask:
    name: str
    input: Any
    proc: Runnable               # 节点核心逻辑（bound + writers）
    writes: deque[tuple[str, Any]]
    config: RunnableConfig
    triggers: Sequence[str]
    retry_policy: Sequence[RetryPolicy]
    cache_key: CacheKey | None
    id: str
    path: tuple[str | int | tuple, ...]
    writers: Sequence[Runnable]
    subgraphs: Sequence[PregelProtocol]
    timeout: TimeoutPolicy | None
```

`proc` 是一个 RunnableSequence，包含：
1. 通道读取（`ChannelRead`）
2. mapper（状态转换，如 dict → Pydantic 模型）
3. bound（用户节点函数）
4. writers（`ChannelWrite` 将输出写入通道）

## 版本向量与调度

检查点中的版本数据结构驱动整个调度：

```python
checkpoint = {
    "channel_versions": {
        "branch:to:node_a": 1,   # 通道当前版本
        "branch:to:node_b": 2,
        "messages": 3,
    },
    "versions_seen": {
        "node_a": {"branch:to:node_a": 1},  # node_a 已见版本
        "node_b": {"branch:to:node_b": 1},  # node_b 已见版本（过期！）
    },
}
```

node_b 的 trigger 通道版本（2）大于其已见版本（1），所以 node_b 在下一步被触发。node_a 已见最新版本，不触发。

默认版本函数 `increment(current, channel)` 返回整数递增。检查点 ID 使用 UUIDv6（时间排序），但通道版本可以是 int、str 或 float，取决于 checkpointer 实现。

## 控制流机制

### 普通边

编译为通道写入：
- A → B：A 的 writer 写入 `branch:to:B`（EphemeralValue）
- B 的 triggers 包含 `branch:to:B`

### 条件边

编译为在 A 的 writer 中插入一个 Runnable，执行 path 函数后：
- 返回节点名 → 写入对应 `branch:to:{node}`
- 返回 `Send(node, arg)` → 写入 `TASKS` 通道（push 式任务）
- 返回 `END` → 不写入，图可能终止

### Join（多起点边）

编译为 `NamedBarrierValue` 屏障：
- 通道名 `join:A+B:C`，names = `{"A", "B"}`
- A 和 B 完成时各写入自己的名称
- C 的 triggers 包含屏障通道，屏障在 seen == names 后释放

### Command

节点返回 `Command(update=..., goto=..., resume=...)` 时：
- `update` 通过 `_get_updates` 写入状态通道
- `goto` 通过 `_control_branch` 转换为分支通道写入或 Send
- `graph=Command.PARENT` 抛出 `ParentCommand` 冒泡到父图

## 循环终止条件

Pregel 循环在以下情况终止：

1. **正常完成**：`apply_writes` 返回的 `updated_channels` 与 `trigger_to_nodes` 无交集（没有更新的通道能触发任何节点）
2. **递归限制**：`step >= recursion_limit`（默认 10007，环境变量 `LANGGRAPH_DEFAULT_RECURSION_LIMIT`），抛出 `GraphRecursionError`
3. **中断**：`should_interrupt()` 返回非空任务列表，抛出 `GraphInterrupt`
4. **排空**：`RunControl.request_drain()` 被调用，抛出 `GraphDrained`
5. **节点失败**：重试耗尽后异常传播

## 检查点在循环中的位置

每个超步结束后，PregelLoop 调用 `create_checkpoint()` 保存状态：

1. 从当前通道值创建 `Checkpoint` 字典
2. 分配新的 UUIDv6 检查点 ID
3. 调用 checkpointer 的 `put()` 异步/同步保存
4. 将本步写入通过 `put_writes()` 持久化（用于 DeltaChannel 重放和崩溃恢复）

Durability 模式控制持久化时机：
- `"sync"`：下一步开始前同步持久化
- `"async"`：下一步执行时异步持久化
- `"exit"`：仅运行结束时持久化

## 直接使用 Pregel

大多数用户应使用 `StateGraph`。高级用户可直接用 `NodeBuilder` 构建 Pregel 应用：

```python
from langgraph.channels import EphemeralValue
from langgraph.pregel import Pregel, NodeBuilder

node = (
    NodeBuilder()
    .subscribe_only("input")
    .do(lambda x: x.upper())
    .write_to("output")
    .build()
)

app = Pregel(
    nodes={"process": node},
    channels={
        "input": EphemeralValue(str),
        "output": EphemeralValue(str),
    },
    input_channels=["input"],
    output_channels=["output"],
)
```

## 相关概念

- 状态图 — StateGraph 如何编译为 Pregel
- 通道系统 — 通道类型与生命周期
- 检查点机制 — 持久化在循环中的作用
- API 参考 — Pregel 完整 API
