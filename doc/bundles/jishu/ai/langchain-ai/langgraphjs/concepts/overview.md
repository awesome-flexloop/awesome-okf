---
type: Concept
title: LangGraphJS 总览
description: LangGraphJS 是什么、解决什么问题、核心架构分层与设计哲学
tags: [overview, architecture, concepts]
generated:
  by: reference_agent/trae-solo
  at: 2026-08-23T00:00:00Z
status: stable
sources:
  - id: source
    resource: https://github.com/langchain-ai/langgraphjs
    title: LangGraphJS GitHub
---

# LangGraphJS 总览

**LangGraphJS** 是 LangChain 团队推出的 TypeScript/JavaScript 库，用于构建**有状态、可持久化、支持人机协作的 Agent 工作流**。它的执行模型灵感来自 Google 的 Pregel 图计算系统，通过「节点 + 边 + 通道 + 超步」的抽象，让开发者可以用声明式方式构建循环、分支、并行、持久化的复杂 Agent。

## 它解决什么问题

原生 LLM 调用是无状态的，但真实 Agent 需要：

- **多步循环**：调用模型 → 执行工具 → 观察结果 → 再次调用模型，直到任务完成
- **状态管理**：在步骤间维护对话历史、中间产物、错误状态
- **持久化与恢复**：长时运行的 Agent 需要在崩溃后恢复，支持「时间旅行」调试
- **人机协作（HITL）**：在关键节点暂停，等待人工审批或输入后继续
- **流式输出**：token 级流式响应，提升用户体验
- **动态 fan-out/fan-in**：map-reduce 式并行处理

LangGraphJS 将这些能力内建为运行时原语，而非让开发者在业务代码中拼凑。

## 四层架构

LangGraphJS 的代码库严格分为四层，自底向上：

```
┌─────────────────────────────────────┐
│  Graph 层（StateGraph / Annotation）│  ← 用户 API
├─────────────────────────────────────┤
│  Pregel 层（执行引擎/超步/流）       │  ← 运行时
├─────────────────────────────────────┤
│  Channels 层（LastValue/Topic/...） │  ← 状态原语
├─────────────────────────────────────┤
│  Checkpointer 层（持久化后端）       │  ← 存储
└─────────────────────────────────────┘
```

1. **Channels 层**：状态管理的最小原语。每个通道定义「值如何存储、如何更新、如何 checkpoint」。内置 `LastValue`、`BinaryOperatorAggregate`、`Topic`、`DeltaChannel`、`EphemeralValue` 等。
2. **Checkpointer 层**：定义 `BaseCheckpointSaver` 抽象，提供 `MemorySaver` 及 Postgres/SQLite/Redis/MongoDB 后端。Checkpoint 以链表形式组织，支持时间旅行与线程分叉。
3. **Pregel 层**：核心执行引擎。以「超步（superstep）」为调度单位，节点在超步内并行执行，通过通道消息传递，超步边界统一应用写入并做 checkpoint。支持中断、重试、超时、缓存、流式。
4. **Graph 层**：面向用户的高层 API。`StateGraph` 让用户用节点、边、条件边描述工作流，`Annotation` 声明状态结构；编译时翻译为 Pregel 可执行的 `PregelNode` + `ChannelWrite`。

## 核心概念速查

| 概念 | 一句话说明 |
|---|---|
| [StateGraph](state-graph.md) | 有状态工作流构建器，节点+边+条件边 |
| [Annotation](annotation.md) | 状态字段声明 DSL，编译为通道 |
| [Channels](channels.md) | 状态存储与更新原语 |
| [Checkpointing](checkpointing.md) | 状态持久化、恢复、时间旅行 |
| [Pregel 执行引擎](pregel-execution.md) | 超步调度、消息传递、并行执行 |

## 设计哲学

- **通道即状态**：图状态不是普通对象，而是通道实例的集合，状态语义由通道决定。
- **编译期翻译**：用户友好的图 API 在编译时翻译为 Pregel 原语，运行时与 API 演进解耦。
- **持久化优先**：checkpoint 不是可选插件，而是执行模型的一部分；中断、恢复、时间旅行都建立在 checkpoint 链表之上。
- **控制流即数据**：`Command` 和 `Send` 将路由决策与状态更新统一为可序列化对象，支持跨进程/跨语言传输。
- **安全内建**：原型污染防护、序列化边界控制、错误码与故障排查 URL 都在核心代码中体现。

## 下一步

- 阅读[状态图与工作流](state-graph.md)了解如何构建第一个图
- 深入[Annotation 状态定义](annotation.md)理解状态建模
- 理解[Pregel 执行引擎](pregel-execution.md)掌握运行时机制
