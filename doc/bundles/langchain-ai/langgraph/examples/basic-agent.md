---
type: example
scope: langgraph
name: basic-agent
version: "0.2"
source: https://github.com/langchain-ai/langgraph
description: 基础示例——构建带检查点和人机协同中断的聊天 Agent
---

# 基础示例：带中断的聊天 Agent

本示例演示如何使用 `StateGraph`、`MessagesState`、检查点和 `interrupt()` 构建一个支持人机协同的聊天 Agent。

## 完整代码

```python
from typing import Annotated
from typing_extensions import TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command, RetryPolicy


class AgentState(MessagesState):
    approved: bool


def chatbot(state: AgentState) -> dict:
    messages = state["messages"]
    response = f"Echo: {messages[-1].content}"
    return {"messages": [{"role": "assistant", "content": response}]}


def human_review(state: AgentState) -> dict:
    decision = interrupt(
        {"draft": state["messages"][-1].content, "action": "approve or reject"}
    )
    return {"approved": decision == "approve"}


def route_after_review(state: AgentState) -> str:
    return "chatbot" if state["approved"] else END


builder = StateGraph(AgentState)
builder.add_node("chatbot", chatbot, retry_policy=RetryPolicy(max_attempts=2))
builder.add_node("human_review", human_review)

builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", "human_review")
builder.add_conditional_edges("human_review", route_after_review)

checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)
```

## 执行流程

```
START → chatbot → human_review → [approved?]
                                  ├─ yes → chatbot
                                  └─ no  → END
```

## 运行：首次调用（触发中断）

```python
config = {"configurable": {"thread_id": "review-1"}}

for chunk in graph.stream(
    {"messages": [{"role": "user", "content": "Hello"}]},
    config,
    stream_mode="updates",
):
    print(chunk)
```

输出：

```python
{"chatbot": {"messages": [AIMessage(content="Echo: Hello")]}}
{"__interrupt__": (Interrupt(value={"draft": "Echo: Hello", "action": "approve or reject"}, id="..."),)}
```

图在 `human_review` 节点暂停，检查点已保存。

## 恢复：提供人工输入

```python
for chunk in graph.stream(Command(resume="approve"), config, stream_mode="updates"):
    print(chunk)
```

输出：

```python
{"human_review": {"approved": True}}
{"chatbot": {"messages": [AIMessage(content="Echo: Echo: Hello")]}}
```

## 检查状态历史

```python
history = list(graph.get_state_history(config))
for snapshot in history:
    print(snapshot.metadata["step"], snapshot.next)
```

## 关键 API 说明

| API | 作用 |
|---|---|
| `MessagesState` | 预定义 `messages: Annotated[list, add_messages]` 状态 |
| `InMemorySaver()` | 内存检查点保存器 |
| `interrupt(value)` | 暂停节点，将 value 返回给客户端 |
| `Command(resume=value)` | 恢复中断，提供 resume 值 |
| `RetryPolicy(max_attempts=2)` | 节点失败时最多重试2次 |
| `get_state_history(config)` | 获取检查点历史（时间旅行） |

## 相关概念

- [状态图](/langchain-ai/langgraph/concepts/state-graph) — StateGraph 构建 API
- [消息图](/langchain-ai/langgraph/concepts/message-graph) — MessagesState 与 add_messages
- [错误处理](/langchain-ai/langgraph/concepts/error-handling) — interrupt 与 RetryPolicy
- [检查点](/langchain-ai/langgraph/concepts/checkpointing) — InMemorySaver 与状态历史
