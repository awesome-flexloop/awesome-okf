---
type: reference
scope: langgraph
name: graph-state
version: "0.2"
source: https://github.com/langchain-ai/langgraph
description: StateGraph 与 CompiledStateGraph API 参考——图构建器、节点/边/分支、编译与执行
---

# StateGraph API 参考

`StateGraph` 是 LangGraph 的主要用户接口，位于 `langgraph.graph.state`。它是一个构建器类，通过添加节点、边和条件边来定义图结构，编译后生成可执行的 `CompiledStateGraph`。

## StateGraph

```python
class StateGraph(Generic[StateT, ContextT, InputT, OutputT])
```

### 构造函数

```python
StateGraph(
    state_schema: type[StateT],
    context_schema: type[ContextT] | None = None,
    *,
    input_schema: type[InputT] | None = None,
    output_schema: type[OutputT] | None = None,
)
```

**参数：**

| 参数 | 类型 | 说明 |
|---|---|---|
| `state_schema` | `type` | 定义图状态的 schema 类（TypedDict、Pydantic BaseModel 或 dataclass） |
| `context_schema` | `type \| None` | 定义运行时不可变上下文的 schema，通过 `Runtime` 暴露给节点 |
| `input_schema` | `type \| None` | 图输入 schema，默认同 `state_schema` |
| `output_schema` | `type \| None` | 图输出 schema，默认同 `state_schema` |

状态键可用 `Annotated[type, reducer]` 标注聚合函数，reducer 签名为 `(Value, Value) -> Value`。无 reducer 的键每步仅允许一个写入，多写会抛出 `InvalidUpdateError`。

### 实例属性

| 属性 | 类型 | 说明 |
|---|---|---|
| `nodes` | `dict[str, StateNodeSpec]` | 已注册的节点 |
| `edges` | `set[tuple[str, str]]` | 普通有向边 |
| `branches` | `defaultdict[str, dict[str, BranchSpec]]` | 条件边，按源节点分组 |
| `channels` | `dict[str, BaseChannel]` | 从 schema 推导的通道 |
| `managed` | `dict[str, ManagedValueSpec]` | 托管值规格 |
| `schemas` | `dict[type, dict[str, BaseChannel \| ManagedValueSpec]]` | 各 schema 对应的通道映射 |
| `waiting_edges` | `set[tuple[tuple[str, ...], str]]` | 多起点 join 边 |
| `compiled` | `bool` | 图是否已验证/编译 |

### add_node

```python
add_node(
    node: str | StateNode,
    action: StateNode | None = None,
    *,
    defer: bool = False,
    metadata: dict[str, Any] | None = None,
    input_schema: type | None = None,
    retry_policy: RetryPolicy | Sequence[RetryPolicy] | None = None,
    cache_policy: CachePolicy | None = None,
    error_handler: StateNode | None = None,
    destinations: dict[str, str] | tuple[str, ...] | None = None,
    timeout: float | timedelta | TimeoutPolicy | None = None,
    trace_policy: TracePolicy | None = None,
) -> Self
```

添加节点到图。节点名不能为 `END`/`START`，不能包含 `|` 或 `:` 字符。若提供 `error_handler`，自动创建名为 `__error_handler__{node}` 的处理器节点。

`defer=True` 时节点延迟到运行结束前执行，使用 `LastValueAfterFinish` 和 `NamedBarrierValueAfterFinish` 通道。

### add_edge

```python
add_edge(start_key: str | list[str], end_key: str) -> Self
```

添加有向边。单起点直接加入 `edges`；多起点创建 join 屏障，等待所有起点完成后触发终点。`END` 不能作为起点，`START` 不能作为终点。

### add_conditional_edges

```python
add_conditional_edges(
    source: str,
    path: Callable[..., Hashable | Sequence[Hashable]] | Runnable,
    path_map: dict[Hashable, str] | list[str] | None = None,
) -> Self
```

添加条件边。`path` 函数在源节点完成后执行，返回目标节点名、节点名序列或 `Send` 对象。返回 `END` 终止执行。

### add_sequence

```python
add_sequence(
    nodes: Sequence[StateNode | tuple[str, StateNode]]
) -> Self
```

按顺序添加节点序列，自动在相邻节点间添加边。

### set_entry_point / set_finish_point

```python
set_entry_point(key: str) -> Self    # 等价于 add_edge(START, key)
set_finish_point(key: str) -> Self  # 等价于 add_edge(key, END)
```

### set_conditional_entry_point

```python
set_conditional_entry_point(
    path: Callable | Runnable,
    path_map: dict | list | None = None,
) -> Self
```

等价于 `add_conditional_edges(START, path, path_map)`。

### set_node_defaults

```python
set_node_defaults(
    *,
    retry_policy: RetryPolicy | Sequence[RetryPolicy] | None = None,
    cache_policy: CachePolicy | None = None,
    error_handler: StateNode | None = None,
    timeout: float | timedelta | TimeoutPolicy | None = None,
) -> Self
```

设置应用于所有节点的默认策略。每节点值优先。`retry_policy` 和 `timeout` 也应用于错误处理器节点；`cache_policy` 和 `error_handler` 不应用于处理器节点。

### validate

```python
validate(interrupt: Sequence[str] | None = None) -> Self
```

验证图结构：所有边的源和目标必须存在，必须有从 START 出发的入口边。设置 `compiled = True`。

### compile

```python
compile(
    checkpointer: Checkpointer = None,
    *,
    cache: BaseCache | None = None,
    store: BaseStore | None = None,
    interrupt_before: All | list[str] | None = None,
    interrupt_after: All | list[str] | None = None,
    debug: bool = False,
    name: str | None = None,
    transformers: Sequence[Callable] | None = None,
) -> CompiledStateGraph
```

编译图为可执行对象。`checkpointer` 可为 `None`（无持久化）、`True`（启用）、`False`（禁用，不继承父图）或 `BaseCheckpointSaver` 实例。启用 checkpointer 后需在 config 中传 `thread_id`。

## CompiledStateGraph

```python
class CompiledStateGraph(Pregel[StateT, ContextT, InputT, OutputT])
```

编译后的图，继承自 `Pregel`，实现 LangChain 的 `Runnable` 接口。主要方法包括 `invoke()`、`stream()`、`ainvoke()`、`astream()`、`get_state()`、`update_state()`。

### 关键方法

| 方法 | 说明 |
|---|---|
| `invoke(input, config=None)` | 同步执行图，返回最终状态 |
| `stream(input, config=None, stream_mode="values")` | 同步流式执行，逐块产出 |
| `ainvoke(input, config=None)` | 异步执行图 |
| `astream(input, config=None, stream_mode="values")` | 异步流式执行 |
| `get_state(config)` | 获取当前 `StateSnapshot` |
| `update_state(config, values, as_node=None)` | 手动更新状态 |
| `get_graph(config=None)` | 返回可绘制的图结构 |

### stream_mode 选项

| 值 | 产出内容 |
|---|---|
| `"values"` | 每步后的完整状态 |
| `"updates"` | 每步各节点的增量更新 |
| `"messages"` | LLM token 级消息流 |
| `"custom"` | 节点内通过 `StreamWriter` 发射的自定义数据 |
| `"checkpoints"` | 检查点创建事件 |
| `"tasks"` | 任务开始/完成事件 |
| `"debug"` | 检查点和任务调试事件 |

## 公共常量

| 常量 | 值 | 说明 |
|---|---|---|
| `START` | `"__start__"` | 图入口虚拟节点 |
| `END` | `"__end__"` | 图出口虚拟节点 |

## 相关概念

- [状态图](/langchain-ai/langgraph/concepts/state-graph) — StateGraph 的设计理念与使用模式
- [通道系统](/langchain-ai/langgraph/concepts/channels) — 通道类型与 reducer 机制
- [Pregel 引擎](/langchain-ai/langgraph/concepts/pregel-engine) — 底层执行模型
- [检查点](/langchain-ai/langgraph/concepts/checkpointing) — 持久化与状态恢复
