---
type: concept
scope: langgraph
name: message-graph
version: "0.2"
source: https://github.com/langchain-ai/langgraph
description: 消息图——MessagesState、add_messages reducer、MessageGraph 与消息管理
---

# 消息图（Message Graph）

聊天是 LangGraph 最常见的用例。框架提供了 `MessagesState`、`add_messages` reducer 和相关工具，简化消息列表的管理。

## MessagesState

`MessagesState` 是一个预定义的 TypedDict：

```python
class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
```

它等价于：

```python
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage

class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
```

直接使用或扩展：

```python
from langgraph.graph import MessagesState, StateGraph, START, END

class AgentState(MessagesState):
    # messages 键已由 MessagesState 提供
    context: dict  # 额外状态键

builder = StateGraph(AgentState)
```

## add_messages reducer

`add_messages(left, right, *, format=None)` 是消息列表的合并函数，作为 `BinaryOperatorAggregate` 通道的 reducer：

### 基本合并

- 将 `right` 中的消息合并到 `left`
- 无 ID 的消息自动生成 `uuid4()`
- 默认追加新消息（append-only）
- 相同 ID 的消息：新消息替换旧消息

```python
from langchain_core.messages import HumanMessage, AIMessage

msgs1 = [HumanMessage(content="Hello", id="1")]
msgs2 = [AIMessage(content="Hi", id="2")]
add_messages(msgs1, msgs2)
# [HumanMessage(content='Hello', id='1'), AIMessage(content='Hi', id='2')]
```

### 按 ID 覆盖

```python
msgs1 = [HumanMessage(content="Hello", id="1")]
msgs2 = [HumanMessage(content="Hello again", id="1")]
add_messages(msgs1, msgs2)
# [HumanMessage(content='Hello again', id='1')]
```

### 删除消息

使用 `RemoveMessage` 删除指定 ID 的消息：

```python
from langchain_core.messages import RemoveMessage

# 删除单条消息
add_messages(msgs, [RemoveMessage(id="1")])

# 删除所有消息
add_messages(msgs, [RemoveMessage(id="__remove_all__")])
```

`REMOVE_ALL_MESSAGES = "__remove_all__"` 是特殊 ID，`add_messages` 遇到它时返回该标记之后的所有消息（即清空列表）。

删除不存在 ID 的消息会抛出 `ValueError`。

### OpenAI 格式

`format="langchain-openai"` 将消息转换为 OpenAI 格式（内容为 text/image_url block，工具响应为独立 ToolMessage）。需要 `langchain-core>=0.3.11`。

### 部分应用

`add_messages` 通过 `@_add_messages_wrapper` 装饰，无参数调用时返回 partial：

```python
reducer = add_messages(format="langchain-openai")
# 等价于 lambda left, right: add_messages(left, right, format="langchain-openai")
```

### 在 StateGraph 中使用

```python
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]

def chatbot(state: State):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

builder = StateGraph(State)
builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")
graph = builder.compile()

graph.invoke({"messages": [("user", "Hello")]})
```

多节点同时写入 messages 时，`add_messages` 自动合并所有节点的返回消息。

## push_message

`push_message(message, *, state_key="messages")` 允许在节点执行期间手动向流和状态写入消息：

```python
from langgraph.graph.message import push_message

def node(state):
    # 手动发射一条消息到 messages 流
    push_message(AIMessage(content="Thinking..."))
    # 继续节点逻辑...
```

- 需要消息 ID（无 ID 时抛出 ValueError）
- 通过 `StreamMessagesHandler` 发射到 `messages` 流模式
- 通过 `CONFIG_KEY_SEND` 写入状态通道
- `state_key=None` 时只发射流不写状态

## MessageGraph（已弃用）

`MessageGraph` 是 `StateGraph` 的子类，整个状态是单个 append-only 消息列表：

```python
# 已弃用（v1.0.0，将在 v2.0.0 移除）
from langgraph.graph import MessageGraph

builder = MessageGraph()
builder.add_node("chatbot", lambda state: llm.invoke(state))
```

它内部等价于 `StateGraph(Annotated[list[AnyMessage], add_messages])`。新代码应直接使用 `StateGraph` + `MessagesState` 或自定义 `messages` 键。

## _messages_delta_reducer

`_messages_delta_reducer(state, writes)` 是为 `DeltaChannel` 设计的批量 reducer：

- 单次处理所有写入（按 ID 去重、RemoveMessage tombstone）
- 不调用 `add_messages`，直接操作列表
- 满足批处理不变性
- 自动将 dict/str/tuple 输入转换为 `BaseMessage`
- 不处理 `REMOVE_ALL_MESSAGES`、未知 ID 删除、缺失 ID 的 UUID 分配、`BaseMessageChunk` 转换（实验性功能）

```python
from langgraph.channels.delta import DeltaChannel
from langgraph.graph.message import _messages_delta_reducer

class State(TypedDict):
    messages: Annotated[list, DeltaChannel(_messages_delta_reducer)]
```

## 消息与流式

`stream_mode="messages"` 提供 LLM token 级流式输出：

```python
for msg, metadata in graph.stream(input, stream_mode="messages"):
    print(msg.content, end="", flush=True)
```

每个产出是 `(message_chunk, metadata)` 元组，metadata 包含 `langgraph_step`、`langgraph_node`、`langgraph_triggers` 等键。`StreamMessagesHandler` 和 `StreamMessagesHandlerV2` 负责从 LLM 回调中捕获 token 并转发到流。

## 典型消息工作流

### 简单聊天机器人

```python
from langgraph.graph import StateGraph, START, MessagesState

builder = StateGraph(MessagesState)
builder.add_node("chatbot", lambda state: {"messages": [llm.invoke(state["messages"])]})
builder.add_edge(START, "chatbot")
graph = builder.compile()
```

### 带工具的 Agent

```python
from langgraph.prebuilt import ToolNode

tools = [search, calculator]
builder = StateGraph(MessagesState)
builder.add_node("chatbot", lambda state: {"messages": [llm.bind_tools(tools).invoke(state["messages"])]})
builder.add_node("tools", ToolNode(tools))
builder.add_conditional_edges("chatbot", route_tools)
builder.add_edge("tools", "chatbot")
```

### 消息历史裁剪

使用 `RemoveMessage` 防止消息列表无限增长：

```python
def manage_history(state: MessagesState):
    messages = state["messages"]
    if len(messages) > 100:
        # 删除前90条
        return {"messages": [RemoveMessage(id=m.id) for m in messages[:-10]]}
    return {}
```

## 相关概念

- [状态图](/langchain-ai/langgraph/concepts/state-graph) — StateGraph 与 reducer 机制
- [通道系统](/langchain-ai/langgraph/concepts/channels) — BinaryOperatorAggregate 通道
- [流式处理](/langchain-ai/langgraph/concepts/streaming) — messages 流模式
- [检查点机制](/langchain-ai/langgraph/concepts/checkpointing) — 消息状态持久化
