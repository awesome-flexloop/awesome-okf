---
type: concept
scope: langgraph
name: overview
version: "0.2"
source: https://github.com/langchain-ai/langgraph
description: LangGraph 总览——用于构建有状态、多参与者 Agent 的框架
---

# LangGraph 总览

## 什么是 LangGraph

LangGraph 是 LangChain AI 开发的开源框架，用于构建**有状态、多参与者**的 LLM 应用。它的核心抽象是一张图：节点表示计算单元（函数、Runnable、Agent），边表示控制流，节点通过读写共享状态进行通信。

与简单的链式调用不同，LangGraph 支持：

- **循环和条件分支**：图可以包含环，支持 Agent 的推理-行动循环
- **持久化状态**：内置检查点系统，支持暂停、恢复和时间旅行
- **人机协同**：通过 `interrupt()` 在任意节点暂停，等待人工输入后恢复
- **流式输出**：多种流模式，包括 token 级消息流和自定义流
- **并行执行**：基于 BSP 模型的节点级并行
- **子图嵌套**：图可以作为节点嵌入更大的图中

## 核心抽象

LangGraph 的架构建立在三个层次上：

```
┌─────────────────────────────────────────────┐
│           StateGraph（用户 API）              │
│   节点 · 边 · 条件边 · 编译                   │
├─────────────────────────────────────────────┤
│           Pregel（执行引擎）                  │
│   超步循环 · 通道 · Actor · BSP              │
├─────────────────────────────────────────────┤
│        Checkpoint + Store（持久化）           │
│   检查点 · 序列化 · 长期存储                  │
└─────────────────────────────────────────────┘
```

### StateGraph

`StateGraph` 是用户直接交互的构建器。用户定义状态 schema（TypedDict、Pydantic 模型或 dataclass），添加节点和边，然后编译为可执行图。

```python
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    count: int

def increment(state: State) -> dict:
    return {"count": state["count"] + 1}

builder = StateGraph(State)
builder.add_node("increment", increment)
builder.add_edge(START, "increment")
builder.add_edge("increment", END)
graph = builder.compile()

graph.invoke({"count": 0})  # {'count': 1}
```

### Pregel 引擎

编译后的图由 Pregel 引擎执行，采用 BSP（Bulk Synchronous Parallel）模型。每一步（超步）分三阶段：

1. **Plan**：确定哪些节点因通道更新而被触发
2. **Execute**：并行执行所有触发节点，写入暂存不可见
3. **Update**：将所有写入应用到通道，推进版本号

详见 [Pregel 引擎](/ai/langchain-ai/langgraph/concepts/pregel-engine)。

### 通道系统

通道是节点间通信的媒介。每个状态键对应一个通道，通道类型决定并发写入的聚合方式：

- 无 reducer 的键 → `LastValue`（每步仅允许一个写入）
- 有 reducer 的键 → `BinaryOperatorAggregate`（用函数聚合）
- 特殊通道 → `Topic`、`EphemeralValue`、`NamedBarrierValue` 等

详见 [通道系统](/ai/langchain-ai/langgraph/concepts/channels)。

### 检查点

检查点系统在每步后保存图的完整状态快照（通道值、版本号、调度信息），支持：

- **暂停/恢复**：中断后从检查点恢复
- **时间旅行**：回退到历史检查点重新执行
- **持久化记忆**：跨对话保持状态

详见 [检查点机制](/ai/langchain-ai/langgraph/concepts/checkpointing)。

## 关键能力

### 人机协同

通过 `interrupt()` 函数在节点内暂停执行，将值返回给客户端，客户端用 `Command(resume=value)` 恢复：

```python
from langgraph.types import interrupt, Command

def human_node(state):
    answer = interrupt("需要人工确认")
    return {"result": answer}

# 恢复时
graph.invoke(Command(resume="确认通过"), config)
```

详见 [错误处理与中断](/ai/langchain-ai/langgraph/concepts/error-handling)。

### 动态扇出（Map-Reduce）

通过 `Send` 对象在条件边中动态创建多个并行任务：

```python
from langgraph.types import Send

def fan_out(state):
    return [Send("process", {"item": x}) for x in state["items"]]
```

### 流式输出

支持七种流模式：`values`（完整状态）、`updates`（增量更新）、`messages`（token 流）、`custom`（自定义数据）、`checkpoints`、`tasks`、`debug`。

详见 [流式处理](/ai/langchain-ai/langgraph/concepts/streaming)。

### 消息状态

`MessagesState` 和 `add_messages` 为聊天场景提供开箱即用的消息管理：

```python
from langgraph.graph import MessagesState
# 等价于:
# class MessagesState(TypedDict):
#     messages: Annotated[list[AnyMessage], add_messages]
```

详见 [消息图](/ai/langchain-ai/langgraph/concepts/message-graph)。

## 架构概览

```
langgraph/
├── graph/
│   ├── state.py          # StateGraph, CompiledStateGraph
│   └── message.py        # MessageGraph, MessagesState, add_messages
├── channels/
│   ├── base.py           # BaseChannel 抽象
│   ├── last_value.py     # LastValue, LastValueAfterFinish
│   ├── binop.py          # BinaryOperatorAggregate
│   ├── topic.py          # Topic (PubSub)
│   ├── ephemeral_value.py
│   ├── named_barrier_value.py
│   └── delta.py          # DeltaChannel (beta)
├── pregel/
│   ├── main.py           # Pregel, NodeBuilder
│   ├── _loop.py          # PregelLoop, Sync/Async variants
│   ├── _algo.py          # prepare_next_tasks, apply_writes
│   ├── _executor.py      # BackgroundExecutor
│   ├── _read.py          # PregelNode, ChannelRead
│   └── _write.py         # ChannelWrite, ChannelWriteEntry
├── checkpoint/           # (独立包 langgraph-checkpoint)
│   ├── base/             # BaseCheckpointSaver, Checkpoint
│   └── serde/            # SerializerProtocol, JsonPlusSerializer
├── types.py              # Command, Send, Interrupt, RetryPolicy...
├── errors.py             # 异常层次
├── config.py             # get_config, get_store, get_stream_writer
└── runtime.py            # Runtime, ExecutionInfo, RunControl
```

## 进一步阅读

- [状态图](/ai/langchain-ai/langgraph/concepts/state-graph) — StateGraph 的使用模式
- [通道系统](/ai/langchain-ai/langgraph/concepts/channels) — 通道类型与 reducer
- [Pregel 引擎](/ai/langchain-ai/langgraph/concepts/pregel-engine) — BSP 执行模型
- [检查点机制](/ai/langchain-ai/langgraph/concepts/checkpointing) — 持久化与恢复
- [消息图](/ai/langchain-ai/langgraph/concepts/message-graph) — 聊天应用构建
- [流式处理](/ai/langchain-ai/langgraph/concepts/streaming) — 流模式详解
- [错误处理](/ai/langchain-ai/langgraph/concepts/error-handling) — 重试、中断与恢复
