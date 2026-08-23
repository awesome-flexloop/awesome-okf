---
type: example
scope: langgraph
name: map-reduce
version: "0.2"
source: https://github.com/langchain-ai/langgraph
description: Map-Reduce 示例——使用 Send 动态扇出并行处理，BinaryOperatorAggregate 聚合结果
---

# Map-Reduce 示例：并行文档处理

本示例演示如何使用 `Send` 对象实现动态扇出（fan-out），并行处理多个文档，然后通过 `BinaryOperatorAggregate` 通道聚合结果。

## 完整代码

```python
import operator
from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send


class OverallState(TypedDict):
    documents: list[str]
    summaries: Annotated[list[str], operator.add]
    total_words: Annotated[int, operator.add]


class WorkerState(TypedDict):
    document: str


def fan_out(state: OverallState) -> list[Send]:
    return [
        Send("process_document", {"document": doc})
        for doc in state["documents"]
    ]


def process_document(state: WorkerState) -> dict:
    doc = state["document"]
    summary = doc[:50] + "..." if len(doc) > 50 else doc
    word_count = len(doc.split())
    return {
        "summaries": [summary],
        "total_words": word_count,
    }


def finalize(state: OverallState) -> dict:
    return {
        "summaries": [f"Processed {len(state['summaries'])} docs, "
                      f"{state['total_words']} total words"]
    }


builder = StateGraph(OverallState)
builder.add_node("process_document", process_document)
builder.add_node("finalize", finalize)

builder.add_conditional_edges(START, fan_out)
builder.add_edge("process_document", "finalize")
builder.add_edge("finalize", END)

graph = builder.compile()
```

## 执行流程

```
                    ┌─ Send → process_document(doc1) ─┐
START → fan_out ───┼─ Send → process_document(doc2) ─┼→ finalize → END
                    └─ Send → process_document(doc3) ─┘
                         （并行执行，结果通过 reducer 聚合）
```

## 运行

```python
result = graph.invoke({
    "documents": [
        "LangGraph is a framework for building stateful agents.",
        "It supports cycles, persistence, and human-in-the-loop.",
        "Channels aggregate concurrent writes using reducers.",
    ]
})

print(result["summaries"])
print(result["total_words"])
```

输出：

```python
[
    "LangGraph is a framework for building stateful agents.",
    "It supports cycles, persistence, and human-in-the-...",
    "Channels aggregate concurrent writes using reducers.",
    "Processed 3 docs, 23 total words"
]
23
```

## 关键机制

### Send 动态扇出

`Send(node, arg)` 创建 push 式任务：
- `node`：目标节点名
- `arg`：传递给节点的输入（可以是任意类型，不必匹配图状态）
- 多个 Send 并行执行同一节点的不同实例
- Send 在条件边中返回，由框架收集为 `TASKS` 通道写入

### Reducer 聚合

```python
summaries: Annotated[list[str], operator.add]
total_words: Annotated[int, operator.add]
```

`operator.add` 作为 reducer：
- 列表使用 `+` 拼接所有并行结果
- 整数使用 `+` 求和
- 底层通道为 `BinaryOperatorAggregate`

如果没有 reducer，并行写入 `LastValue` 通道会抛出 `InvalidUpdateError`。

### 独立 Worker 状态

`WorkerState` 是 `process_document` 节点的独立输入 schema，通过 `input_schema` 参数或类型注解推断。每个 Send 传入不同的 document，节点间状态隔离。

## 带条件聚合的变体

```python
def fan_out_filtered(state: OverallState) -> list[Send]:
    return [
        Send("process_document", {"document": doc})
        for doc in state["documents"]
        if len(doc) > 10
    ]
```

## 相关概念

- [状态图](/langchain-ai/langgraph/concepts/state-graph) — 条件边与 Send
- [通道系统](/langchain-ai/langgraph/concepts/channels) — BinaryOperatorAggregate reducer
- [Pregel 引擎](/langchain-ai/langgraph/concepts/pregel-engine) — push 式任务与并行执行
- [API 参考](/langchain-ai/langgraph/references/graph-state) — add_conditional_edges API
