---
type: bundle
okf_version: "0.2"
scope: langgraph
name: langgraph
version: "0.2"
source: https://github.com/langchain-ai/langgraph
description: LangGraph——用于构建有状态、多参与者 LLM Agent 的 Python 框架，基于 Pregel/BSP 执行模型，支持循环、检查点、人机协同与流式输出
---

# LangGraph

**LangGraph** 是 LangChain AI 开发的开源 Python 框架，用于构建**有状态、多参与者**的 LLM 应用。它将应用建模为一张图——节点是计算单元，边是控制流，节点通过类型化通道读写共享状态——并由 Pregel/BSP 引擎驱动执行，内置检查点持久化、人机协同中断和多种流式输出模式。

- **源码**：https://github.com/langchain-ai/langgraph
- **核心包**：`langgraph`（框架）、`langgraph-checkpoint`（检查点基类）
- **执行模型**：Pregel / Bulk Synchronous Parallel（BSP）
- **关键依赖**：langchain-core、pydantic、ormsgpack、xxhash

## 核心特性

- **状态图（StateGraph）**：用 TypedDict/Pydantic/dataclass 定义状态 schema，`Annotated[type, reducer]` 声明并发写入聚合策略
- **Pregel 引擎**：每超步分 Plan→Execute→Update 三阶段，节点并行执行，写入在步末统一应用，保证确定性
- **通道系统**：LastValue、BinaryOperatorAggregate、Topic、EphemeralValue、NamedBarrierValue、DeltaChannel 等内建通道
- **检查点持久化**：每步保存通道值+版本向量，支持暂停/恢复、时间旅行、崩溃恢复；DeltaChannel 支持增量检查点
- **人机协同**：`interrupt()` 暂停节点等待人工输入，`Command(resume=...)` 恢复执行
- **动态扇出**：`Send` 对象在条件边中创建并行 push 式任务，支持 map-reduce 模式
- **统一控制流**：`Command(update, goto, resume, graph)` 将状态更新和路由统一为节点返回值
- **流式输出**：values/updates/messages/custom/checkpoints/tasks/debug 七种流模式，支持 token 级消息流
- **错误处理**：RetryPolicy 指数退避重试、节点级 error_handler、NodeTimeoutError 超时、RunControl 协作排空
- **子图嵌套**：图可作为节点嵌入父图，检查点命名空间隔离

## 快速开始

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

result = graph.invoke({"count": 0})
# {"count": 1}
```

带 reducer 的并发聚合：

```python
import operator
from typing import Annotated

class State(TypedDict):
    values: Annotated[list[int], operator.add]

def node_a(state): return {"values": [1, 2]}
def node_b(state): return {"values": [3, 4]}
# 两个节点并行写入 values，结果为 [1, 2, 3, 4]
```

## 文档导航

### 核心概念

- [总览](/ai/langchain-ai/langgraph/concepts/overview) — LangGraph 是什么、三层架构、关键能力
- [状态图](/ai/langchain-ai/langgraph/concepts/state-graph) — StateSchema、节点/边/条件边、编译、Command 原语
- [通道系统](/ai/langchain-ai/langgraph/concepts/channels) — BaseChannel 抽象与六种内建通道
- [Pregel 引擎](/ai/langchain-ai/langgraph/concepts/pregel-engine) — BSP 超步模型、版本向量调度、循环终止
- [检查点机制](/ai/langchain-ai/langgraph/concepts/checkpointing) — 持久化、时间旅行、DeltaChannel 增量检查点
- [消息图](/ai/langchain-ai/langgraph/concepts/message-graph) — MessagesState、add_messages、消息合并删除
- [流式处理](/ai/langchain-ai/langgraph/concepts/streaming) — 七种流模式、StreamWriter、v2 流部分
- [错误处理与中断](/ai/langchain-ai/langgraph/concepts/error-handling) — RetryPolicy、error_handler、interrupt/resume、超时

### API 参考

- [StateGraph API](/ai/langchain-ai/langgraph/references/graph-state) — 图构建器、节点/边/分支、编译与执行
- [通道与 Pregel API](/ai/langchain-ai/langgraph/references/channels-pregel) — BaseChannel 层次、Pregel/PregelNode/NodeBuilder
- [检查点与持久化 API](/ai/langchain-ai/langgraph/references/checkpoint-persistence) — BaseCheckpointSaver、SerializerProtocol、BaseStore、Runtime

### 使用示例

- [基础聊天 Agent](/ai/langchain-ai/langgraph/examples/basic-agent) — 检查点 + interrupt/resume 人机协同
- [Map-Reduce 并行处理](/ai/langchain-ai/langgraph/examples/map-reduce) — Send 动态扇出 + reducer 聚合

### 设计洞察

- [事实清单](/ai/langchain-ai/langgraph/spec/facts) — 从源码提取的 128 条编号事实
- [架构洞察](/ai/langchain-ai/langgraph/spec/insights) — Channel/Actor 模型、BSP 超步、版本向量、统一控制流、中断协议、错误处理三层架构

## 目录结构

```
langgraph/
├── spec/
│   ├── facts.md           # 源码事实验证清单（128条）
│   └── insights.md        # 设计决策与深度洞察
├── concepts/              # 核心概念（8篇）
├── references/            # API参考（3篇）
├── examples/              # 使用示例（2篇）
├── log.md                 # 更新历史
└── index.md               # 本文件
```

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
