---
type: bundle
okf_version: "0.2"
scope: langgraphjs
name: langgraphjs
version: "0.1.0"
source: https://github.com/langchain-ai/langgraphjs
description: LangGraphJS —— LangChain 团队推出的 TypeScript/JavaScript 有状态 Agent 工作流框架，基于 Pregel 超步模型，提供通道状态管理、checkpoint 持久化、人机协作中断、流式输出与多后端支持
---

# LangGraphJS

**LangGraphJS** 是用于构建**有状态、多参与者、可持久化 Agent 应用**的 TypeScript/JavaScript 框架。它将 Agent 工作流建模为图——节点是计算步骤（调用 LLM、执行工具、人工审批），边定义流转逻辑（含条件分支和动态 fan-out），状态通过通道在节点间传递。执行引擎基于 Google Pregel 的超步（superstep）模型，内建 checkpoint 持久化、时间旅行、人机协作中断和多级流式能力。

- **语言**：TypeScript（ES2021, NodeNext modules, strict）
- **核心包**：`@langchain/langgraph`（langgraph-core）、`@langchain/langgraph-checkpoint`
- **生态依赖**：`@langchain/core`（Runnable、messages、tools）
- **校验后端**：Memory、Postgres、SQLite、Redis、MongoDB

## 核心特性

- **超步执行引擎（Pregel）**：节点在超步内并行执行，通过通道消息传递，超步边界统一应用状态更新与 checkpoint，默认递归限制 25 步。
- **通道状态抽象**：内置 `LastValue`（单写覆盖）、`BinaryOperatorAggregate`（归约聚合）、`Topic`（PubSub）、`DeltaChannel`（增量重放）等通道，状态语义可插拔。
- **Annotation 状态 DSL**：`Annotation.Root` + reducer 声明式定义状态，自动推导 `State`/`Update`/`Node` 类型，支持 Zod schema 互操作。
- **Checkpoint 持久化与时间旅行**：checkpoint 以链表组织，支持线程分叉、历史回放、从任意状态恢复；提供内存/Postgres/SQLite/Redis/MongoDB 后端。
- **人机协作（HITL）**：`interrupt()` 在任意节点深度暂停并持久化，审批后以 `Command({ resume })` 精确恢复；支持静态断点 `interruptBefore`/`interruptAfter`。
- **动态 Map-Reduce**：条件边返回 `Send` 数组实现动态 fan-out，同一节点携带不同输入并行执行，结果经 reducer 聚合。
- **Command 统一控制流**：节点返回 `Command` 同时完成状态更新、路由跳转和中断恢复，`Command.PARENT` 支持子图→父图控制。
- **八级流式模式**：`values`/`updates`/`messages`/`debug`/`checkpoints`/`tasks`/`custom`/`tools`，支持 token 级消息流、子图命名空间、SSE 编码和可组合 Transformer 管线。
- **节点级弹性策略**：每节点可配置 `RetryPolicy`（指数退避）、`CachePolicy`（TTL 缓存）、`TimeoutPolicy`（运行/空闲超时）和 `errorHandler`（saga 补偿）。
- **函数式 API**：除 `StateGraph` 外，`entrypoint()` + `task()` 提供命令式工作流定义，同样获得 Pregel 的持久化和流式能力。

## 快速开始

```typescript
import { StateGraph, MessagesAnnotation, START, END, MemorySaver } from "@langchain/langgraph";
import { ChatOpenAI } from "@langchain/openai";

const model = new ChatOpenAI({ model: "gpt-4o" });

async function agent(state: typeof MessagesAnnotation.State) {
  const response = await model.invoke(state.messages);
  return { messages: [response] };
}

const graph = new StateGraph(MessagesAnnotation)
  .addNode("agent", agent)
  .addEdge(START, "agent")
  .addEdge("agent", END)
  .compile({ checkpointer: new MemorySaver() });

const config = { configurable: { thread_id: "demo" } };
const result = await graph.invoke(
  { messages: [{ role: "user", content: "你好" }] },
  config
);
```

## 文档导航

### 核心概念

- [总览](/langchain-ai/langgraphjs/concepts/overview) — 四层架构、设计哲学、概念速查
- [状态图与工作流](/langchain-ai/langgraphjs/concepts/state-graph) — 节点、边、条件边、编译、循环、节点策略
- [Annotation 状态定义](/langchain-ai/langgraphjs/concepts/annotation) — 状态 DSL、reducer、类型推导、Zod 互操作
- [Channels 通道体系](/langchain-ai/langgraphjs/concepts/channels) — BaseChannel 抽象与内置通道类型
- [Checkpoint 持久化机制](/langchain-ai/langgraphjs/concepts/checkpointing) — 链表结构、后端、时间旅行、线程分叉
- [Pregel 执行引擎](/langchain-ai/langgraphjs/concepts/pregel-execution) — 超步调度、任务、中断、重试、函数式 API

### API 参考

- [Graph 核心 API](/langchain-ai/langgraphjs/references/graph-core) — StateGraph、Annotation、Command、Send、Branch
- [Checkpoint 与流式 API](/langchain-ai/langgraphjs/references/checkpoint-streaming) — Checkpointer、StreamMode、Pregel 方法

### 使用示例

- [基础 ReAct Agent](/langchain-ai/langgraphjs/examples/basic-agent) — 工具调用循环、持久化、流式
- [Map-Reduce 与 Command 控制流](/langchain-ai/langgraphjs/examples/map-reduce-command) — Send 并行、Command 路由、HITL

### 溯源与洞察

- [源码事实清单](spec/facts) — 从源码提取的 14 组编号事实
- [架构洞察](spec/insights) — 7 条设计决策与深层权衡

## 目录结构

```
langgraphjs/
├── spec/
│   ├── facts.md           # 源码事实验证清单（14 组）
│   └── insights.md        # 7 条架构洞察
├── concepts/              # 核心概念（6 篇）
├── references/            # API 参考（2 篇）
├── examples/              # 使用示例（2 篇）
├── log.md                 # 更新历史
└── index.md               # 本文件
```
