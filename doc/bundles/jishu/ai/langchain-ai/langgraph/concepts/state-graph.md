---
type: concept
scope: langgraph
name: state-graph
version: "0.2"
source: https://github.com/langchain-ai/langgraph
description: StateGraph 核心概念——状态 schema、节点、边、条件边、编译与 reducer 机制
---

# 状态图（StateGraph）

`StateGraph` 是 LangGraph 的主要用户接口。它是一个构建器，用户通过声明状态 schema、添加节点和边来定义图结构，编译后生成可执行的 `CompiledStateGraph`。

## 状态 Schema

状态 schema 定义了图的共享数据结构。每个键对应一个通道，通道类型由注解决定：

```python
from typing import Annotated
from typing_extensions import TypedDict
import operator

class State(TypedDict):
    # 无 reducer：每步仅允许一个节点写入，多写报错
    current_step: int
    # 有 reducer：多节点写入用 operator.add 聚合
    results: Annotated[list[str], operator.add]
    # 使用自定义 reducer
    messages: Annotated[list, add_messages]
```

支持的 schema 类型：
- **TypedDict**：最常用，声明式定义键和类型
- **Pydantic BaseModel**：提供运行时验证和 JSON Schema
- **dataclass**：轻量级替代
- **`Annotated[type, reducer]`**：为键指定 reducer 函数

Reducer 签名为 `(Value, Value) -> Value`，接收当前值和新值，返回合并后的值。无 reducer 的键使用 `LastValue` 通道，同一步多个节点写入会抛出 `InvalidUpdateError`。

### Input/Output Schema

可以为图指定独立的输入和输出 schema：

```python
builder = StateGraph(State, input_schema=InputState, output_schema=OutputState)
```

未指定时默认为 `state_schema`。Input/Output schema 中不允许包含 managed channels。

### Context Schema

`context_schema` 定义运行时不可变上下文，通过 `Runtime` 暴露给节点：

```python
class Context(TypedDict):
    user_id: str
    db_conn: Any

builder = StateGraph(State, context_schema=Context)

def node(state: State, runtime: Runtime[Context]):
    user = runtime.context["user_id"]
```

## 节点

节点是图中的计算单元，签名为 `State -> Partial<State>`，即接收当前状态，返回要更新的状态子集。

### 添加节点

```python
builder.add_node("node_name", node_function)
# 或使用函数名作为节点名
builder.add_node(node_function)
```

节点可以是普通函数、Runnable 或任何可调用对象。若节点只有一个参数且有类型注解，LangGraph 会推断其 input_schema。

### 节点策略

通过 `add_node()` 或 `set_node_defaults()` 可为节点配置：

| 参数 | 类型 | 说明 |
|---|---|---|
| `retry_policy` | `RetryPolicy \| Sequence[RetryPolicy]` | 重试策略 |
| `cache_policy` | `CachePolicy` | 缓存策略 |
| `error_handler` | `callable` | 错误处理器 |
| `timeout` | `float \| timedelta \| TimeoutPolicy` | 超时 |
| `trace_policy` | `TracePolicy` | Trace 输入/输出转换 |
| `defer` | `bool` | 延迟到运行结束前执行 |

### 延迟节点（defer）

`defer=True` 的节点在所有普通节点完成后才执行，使用 `LastValueAfterFinish` 和 `NamedBarrierValueAfterFinish` 通道。适用于清理、汇总等收尾逻辑。

## 边

### 普通边

```python
builder.add_edge("node_a", "node_b")
```

A 完成后触发 B。编译为 A 的 writer 向 `branch:to:B` 通道写入 None，B 订阅该通道。

### 入口和出口

```python
builder.add_edge(START, "first_node")   # 或 builder.set_entry_point("first_node")
builder.add_edge("last_node", END)      # 或 builder.set_finish_point("last_node")
```

`START = "__start__"` 和 `END = "__end__"` 是虚拟节点。

### 多起点 Join

```python
builder.add_edge(["node_a", "node_b"], "node_c")
```

C 在 A 和 B **都完成后**才执行。编译为 `NamedBarrierValue` 屏障通道，收集所有起点名称后释放。

### 条件边

```python
def route(state) -> str:
    if state["count"] > 10:
        return "end_node"
    return "loop_node"

builder.add_conditional_edges("node_a", route)
```

`path` 函数返回目标节点名、节点名列表或 `Send` 对象。返回 `END` 终止执行。可通过 `path_map` 将返回值映射到节点名。

```python
builder.add_conditional_edges(
    "router",
    lambda state: state["next"],
    {"search": "search_node", "chat": "chat_node", END: END}
)
```

### 序列

```python
builder.add_sequence([node_a, node_b, node_c])
# 等价于逐个 add_node + add_edge 串联
```

## 编译

```python
graph = builder.compile(
    checkpointer=InMemorySaver(),  # 启用持久化
    store=InMemoryStore(),         # 长期存储
    interrupt_before=["human"],    # 在节点前中断
    interrupt_after=["review"],    # 在节点后中断
    name="my_graph",
)
```

编译过程：
1. 验证图结构（入口边、节点存在性）
2. 为每个状态键创建通道实例
3. 将节点翻译为 `PregelNode`（订阅/发布通道）
4. 将边翻译为通道写入和屏障
5. 创建 `CompiledStateGraph`（Pregel 子类）

### Checkpointer

编译时传入 checkpointer 启用持久化。调用时需在 config 中指定 `thread_id`：

```python
config = {"configurable": {"thread_id": "conversation-123"}}
graph.invoke(input, config)
```

## Command 原语

节点可以返回 `Command` 对象统一控制状态更新和路由：

```python
from langgraph.types import Command

def node(state):
    return Command(
        update={"status": "done"},
        goto="next_node",          # 或 Send("node", arg) 或 ["node_a", "node_b"]
        # graph=Command.PARENT,    # 冒泡到父图
    )
```

`Command` 将数据流（update）和控制流（goto）统一为一个返回值，编译后通过 `_control_branch` 函数分别处理。

## 相关概念

- 通道系统 — 状态键如何映射到通道
- Pregel 引擎 — 编译后的执行模型
- 检查点机制 — 持久化与恢复
- 错误处理 — 重试与错误处理器
- API 参考 — StateGraph 完整 API
