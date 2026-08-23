---
type: Concept
title: 状态图与工作流
description: StateGraph 的节点、边、条件边、编译模型与工作流模式
tags: [stategraph, graph, workflow, nodes, edges]
generated:
  by: reference_agent/trae-solo
  at: 2026-08-23T00:00:00Z
status: stable
sources:
  - id: source
    resource: https://github.com/langchain-ai/langgraphjs
    title: LangGraphJS Source
---

# 状态图与工作流

`StateGraph` 是 LangGraphJS 中构建 Agent 工作流的核心类。它将工作流建模为**节点（nodes）**和**边（edges）**的有向图，状态在节点间通过共享通道流动。

## 基本结构

```typescript
import { StateGraph, Annotation, START, END } from "@langchain/langgraph";

const State = Annotation.Root({
  count: Annotation<number>,
});

const graph = new StateGraph(State)
  .addNode("increment", (state) => ({ count: state.count + 1 }))
  .addNode("double", (state) => ({ count: state.count * 2 }))
  .addEdge(START, "increment")
  .addEdge("increment", "double")
  .addEdge("double", END)
  .compile();

await graph.invoke({ count: 1 });  // { count: 4 }
```

## 节点（Nodes）

节点是一个可调用对象（函数、Runnable 或另一个编译后的子图），接收当前状态，返回**部分状态更新**：

```typescript
addNode(name: string, action: RunnableLike, options?: AddNodeOptions)
```

### 节点策略

每个节点可配置重试、缓存、超时策略：

```typescript
.addNode("flaky", callExternalAPI, {
  retryPolicy: { maxAttempts: 3, initialInterval: 1000 },
  cachePolicy: { ttl: 60_000 },
  timeout: 30_000,
  errorHandler: async (state, error: NodeError) => {
    return new Command({ goto: "fallback", update: { error: error.message } });
  },
})
```

- **retryPolicy**：指数退避重试，可指定 `retryOn` 错误类型
- **cachePolicy**：按输入哈希缓存节点结果
- **timeout**：毫秒数或 `TimeoutPolicy`（区分 `runTimeout`/`idleTimeout`）
- **errorHandler**：重试耗尽后执行，可返回 `Command` 路由到恢复分支（saga 模式）

图级默认策略通过 `setNodeDefaults` 设置，节点自身配置优先。

## 边（Edges）

### 普通边

`addEdge(source, destination)`：源节点完成后无条件触发目标节点。

### 条件边

`addConditionalEdges(source, pathFn, pathMap?)`：源节点完成后调用 `pathFn`，根据返回值路由：

```typescript
.addConditionalEdges("agent", (state) => {
  if (state.messages.at(-1)?.tool_calls?.length) return "tools";
  return END;
}, { tools: "tools", [END]: END })
```

`pathFn` 可返回：

- 节点名字符串
- `Send` 对象（动态 fan-out，携带自定义输入）
- 上述的数组（多目标并行）
- `Command` 对象（同时更新状态与路由）

### 动态 fan-out（Map-Reduce）

使用 `Send` 在条件边中动态创建并行任务：

```typescript
.addConditionalEdges(START, (state) =>
  state.items.map((item) => new Send("process", { item }))
)
```

每个 `Send` 携带独立输入，目标节点的多次调用在同一超步并行执行，结果通过 reducer 聚合。

## 编译

调用 `.compile(options?)` 将图翻译为 Pregel 可执行实例（`CompiledGraph`，继承 `Pregel`）：

```typescript
const graph = builder.compile({
  checkpointer: new MemorySaver(),
  interruptBefore: ["human_review"],
  interruptAfter: ["risky_action"],
});
```

编译选项包括 checkpointer、中断点、流式配置等。编译后图是一个 LangChain `Runnable`，可直接 `invoke`、`stream`、`batch`。

## 循环与终止

图可以包含循环（Agent 调用模型直到满足条件）。终止通过路由到 `END` 实现：

```typescript
.addConditionalEdges("agent", (state) =>
  shouldContinue(state) ? "tools" : END
)
```

为防止无限循环，Pregel 有默认递归限制 25 个超步（`RECURSION_LIMIT_DEFAULT`），超限抛 `GraphRecursionError`。

## MessageGraph（已废弃风格）

`MessageGraph` 是 `StateGraph<BaseMessage[]>` 的特化，内置消息归约通道。新项目推荐使用 `MessagesAnnotation` 或自定义 `Annotation.Root`。

## 相关概念

- [Annotation 状态定义](annotation) — 如何声明状态结构
- [Channels 通道体系](channels) — 状态更新语义
- [Pregel 执行引擎](pregel-execution) — 超步调度与并行
- [Graph 核心 API 参考](/langchain-ai/langgraphjs/references/graph-core)
