---
type: concept
scope: langgraph
name: error-handling
version: "0.2"
source: https://github.com/langchain-ai/langgraph
description: 错误处理与中断——RetryPolicy、节点级错误处理器、interrupt/resume、NodeTimeoutError、GraphBubbleUp
---

# 错误处理与中断

LangGraph 提供三层错误处理机制（重试、节点错误处理器、图级冒泡）和人机协同中断能力。

## 异常层次

```
Exception
├── GraphBubbleUp                    # 控制信号基类（非错误）
│   ├── GraphDrained                 # 协作排空
│   ├── GraphInterrupt               # 子图中断（对根图抑制）
│   └── ParentCommand                # Command 冒泡到父图
├── GraphRecursionError              # 超过递归限制
├── InvalidUpdateError               # 通道更新无效
├── EmptyInputError                  # 空输入
├── TaskNotFound                     # 分布式模式任务未找到
├── NodeCancelledError               # 节点自身抛出 CancelledError
└── NodeTimeoutError                 # 节点超时
```

`GraphBubbleUp` 及其子类是**控制信号**而非错误，在执行器中被特殊处理——不触发错误处理器，不导致运行失败。

`EmptyChannelError` 从 `langgraph.checkpoint.base` 重新导出，在通道为空时由 `get()` 抛出。

## RetryPolicy

`RetryPolicy` 是 NamedTuple，配置节点重试：

```python
class RetryPolicy(NamedTuple):
    initial_interval: float = 0.5      # 首次重试等待（秒）
    backoff_factor: float = 2.0        # 退避乘数
    max_interval: float = 128.0        # 最大重试间隔（秒）
    max_attempts: int = 3              # 最大尝试次数（含首次）
    jitter: bool = True                # 添加随机抖动
    retry_on: type[Exception] | Sequence | Callable = default_retry_on
```

使用方式：

```python
from langgraph.types import RetryPolicy

# 节点级
builder.add_node("flaky", flaky_node, retry_policy=RetryPolicy(max_attempts=5))

# 图级默认
builder.set_node_defaults(retry_policy=RetryPolicy(max_attempts=3))

# 多策略序列（第一个匹配的生效）
builder.add_node("node", node, retry_policy=[
    RetryPolicy(retry_on=ConnectionError, max_attempts=5),
    RetryPolicy(retry_on=TimeoutError, max_attempts=2),
])
```

`retry_on` 可以是异常类、异常类序列或谓词函数 `(Exception) -> bool`。`NodeTimeoutError` 默认可重试。

退避间隔计算：`min(initial_interval * backoff_factor^(attempt-1), max_interval)`，启用 jitter 时添加随机抖动。

## 节点级错误处理器

错误处理器是在节点失败时执行的恢复函数。它接收失败节点的状态和 `NodeError`，可以返回 `Command` 进行恢复。

```python
from langgraph.errors import NodeError
from langgraph.types import Command

def handler(state, error: NodeError):
    # error.node: 失败节点名
    # error.error: 原始异常
    return Command(
        update={"status": f"recovered from {error.node}: {error.error}"},
        goto="fallback_node",
    )

builder.add_node("risky", risky_node, error_handler=handler)
```

也可通过 `set_node_defaults(error_handler=...)` 设为图级默认。

### 关键规则

- 错误处理器节点名为 `__error_handler__{node_name}`
- 图级默认处理器名为 `__default_error_handler__`
- 处理器**不会捕获自身异常**——处理器失败直接导致运行失败
- `retry_policy` 和 `timeout` 默认也应用于处理器节点
- `cache_policy` **不**应用于处理器（缓存错误结果不安全）
- 每节点值优先于图级默认值
- 处理器不能是 error_handler 节点本身

### NodeError

```python
@dataclass(frozen=True, slots=True)
class NodeError:
    node: str           # 失败节点名
    error: BaseException  # 原始异常
```

通过在处理器签名中声明 `error: NodeError` 参数注入。

## NodeTimeoutError

```python
class NodeTimeoutError(Exception):
    node: str
    timeout: float
    run_timeout: float | None
    idle_timeout: float | None
    elapsed: float
    kind: Literal["idle", "run"]
```

### TimeoutPolicy

```python
@dataclass(kw_only=True, slots=True, frozen=True)
class TimeoutPolicy:
    run_timeout: float | timedelta | None = None     # 硬墙钟上限
    idle_timeout: float | timedelta | None = None    # 无进度最大时间
    refresh_on: Literal["auto", "heartbeat"] = "auto"
```

- `run_timeout`：单次尝试的总时间上限，不被任何信号刷新
- `idle_timeout`：无"可观察进度"的最大时间，可由回调事件或 `runtime.heartbeat()` 刷新
- `refresh_on="auto"`：标准进度信号和显式 heartbeat 都刷新
- `refresh_on="heartbeat"`：仅 `runtime.heartbeat()` 刷新

```python
builder.add_node("slow", slow_node, timeout=30)  # 30秒硬超时
builder.add_node("slow", slow_node, timeout=TimeoutPolicy(
    run_timeout=120,
    idle_timeout=30,
    refresh_on="auto",
))
```

超时仅支持异步节点——同步节点阻塞 GIL，无法安全取消。超时后 `NodeTimeoutError` 被 retry_policy 视为可重试。

### Send 级超时

`Send` 对象可携带独立的超时策略：

```python
Send("node", arg, timeout=TimeoutPolicy(run_timeout=10))
```

## NodeCancelledError

`asyncio.CancelledError` 是 `BaseException` 子类，Pregel runner 将框架发起的取消（如同级任务失败后取消兄弟任务）视为静默清理。但用户节点自身抛出的 `CancelledError` 应被视为节点失败，重试层将其转换为 `NodeCancelledError` 使其流经正常错误路径，报告为 `error` 而非静默成功。

## interrupt / resume

`interrupt(value)` 实现人机协同——暂停执行，将值返回给客户端，等待人工输入后恢复。

### 使用流程

```python
from langgraph.types import interrupt, Command

def review_node(state):
    # 首次调用：暂停并返回值给客户端
    decision = interrupt({
        "summary": state["draft"],
        "ask": "approve or reject?",
    })
    # 恢复时：decision 是客户端提供的 resume 值
    return {"approved": decision == "approve"}

# 第一次调用：暂停
for chunk in graph.stream(input, config):
    print(chunk)  # {"__interrupt__": (Interrupt(value=...),)}

# 恢复执行
graph.invoke(Command(resume="approve"), config)
```

### 工作机制

1. 节点调用 `interrupt(value)` 时，通过 scratchpad 检查是否有已存储的 resume 值
2. 若无，构造 `Interrupt`（ID 由 checkpoint_ns 的 xxh3_128 哈希确定性生成），抛出 `GraphInterrupt`
3. PregelLoop 捕获异常，保存检查点（含中断信息），暂停运行
4. 客户端通过 `Command(resume=value)` 恢复
5. 框架从检查点**重新执行被中断的节点**（不是从中断点续执行，而是重放整个节点）
6. 节点再次调用 `interrupt()` 时，scratchpad 中有匹配的 resume 值，直接返回

### 多中断

节点可包含多个 `interrupt()` 调用，按调用顺序匹配 resume 值。每个任务的 resume 列表独立，不跨任务共享。

### 前置条件

必须启用 checkpointer，因为中断状态需要持久化。`thread_id` 用于标识暂停的会话。

### Interrupt 对象

```python
@final
@dataclass(init=False, slots=True)
class Interrupt:
    value: Any
    id: str

    @classmethod
    def from_ns(cls, value: Any, ns: str) -> Interrupt
```

ID 在相同命名空间下是确定性的（xxh3_128 哈希），支持幂等恢复。

### interrupt_before / interrupt_after

编译时可配置粗粒度中断，无需节点代码配合：

```python
graph = builder.compile(
    interrupt_before=["human_review"],   # 在节点执行前暂停
    interrupt_after=["auto_review"],     # 在节点执行后暂停
)
```

`"*"` 表示在所有节点前/后中断。由 `should_interrupt()` 在调度层检查：自上次中断以来有通道更新，且触发节点在中断列表中。

## GraphDrained 与协作排空

`RunControl` 支持优雅关闭：

```python
from langgraph.runtime import RunControl

control = RunControl()
graph = builder.compile()

# 在另一个线程中
control.request_drain("SIGTERM received")
```

PregelLoop 在超步边界检查 `drain_requested`，抛出 `GraphDrained(reason)`。当前检查点被保存，运行可在之后恢复。这用于生产环境中的滚动更新和优雅关闭。

`GraphDrained` 继承自 `GraphBubbleUp`，不被视为错误。

## ParentCommand

节点返回 `Command(graph=Command.PARENT)` 时，命令冒泡到最近的父图。框架抛出 `ParentCommand(command)`，子图循环将其作为特殊信号处理，父图接收命令并执行 update/goto。

```python
def subgraph_node(state):
    return Command(
        graph=Command.PARENT,
        update={"parent_key": "value"},
        goto="parent_node",
    )
```

## GraphRecursionError

当超步数超过 `recursion_limit`（默认 10007）时抛出，防止无限循环。可通过 config 调整：

```python
graph.invoke(input, {"recursion_limit": 1000})
```

错误消息包含故障排除链接。

## InvalidUpdateError

在以下情况抛出：
- `LastValue` 通道同一步收到多个写入
- `EphemeralValue(guard=True)` 同一步收到多个写入
- `BinaryOperatorAggregate`/`DeltaChannel` 同一步收到多个 Overwrite
- 写入 `TASKS` 保留通道
- 通道更新类型无效

错误码通过 `ErrorCode` 枚举标识，附加文档链接。

## ErrorCode

```python
class ErrorCode(Enum):
    GRAPH_RECURSION_LIMIT = "GRAPH_RECURSION_LIMIT"
    INVALID_CONCURRENT_GRAPH_UPDATE = "INVALID_CONCURRENT_GRAPH_UPDATE"
    INVALID_GRAPH_NODE_RETURN_VALUE = "INVALID_GRAPH_NODE_RETURN_VALUE"
    MULTIPLE_SUBGRAPHS = "MULTIPLE_SUBGRAPHS"
    INVALID_CHAT_HISTORY = "INVALID_CHAT_HISTORY"
```

`create_error_message()` 附加 URL：`https://docs.langchain.com/oss/python/langgraph/errors/{code}`。

## 相关概念

- [Pregel 引擎](/langchain-ai/langgraph/concepts/pregel-engine) — 错误在超步中的传播
- [检查点机制](/langchain-ai/langgraph/concepts/checkpointing) — 中断状态持久化
- [状态图](/langchain-ai/langgraph/concepts/state-graph) — retry_policy/error_handler 配置
- [API 参考](/langchain-ai/langgraph/references/graph-state) — RetryPolicy/TimeoutPolicy API
