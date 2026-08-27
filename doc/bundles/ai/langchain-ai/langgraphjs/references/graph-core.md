---
type: Reference
title: Graph 核心 API 参考
description: StateGraph、Graph、CompiledGraph、Branch、Annotation 等核心类与函数的 API 参考
tags: [api, graph, stategraph, annotation, reference]
generated:
  by: reference_agent/trae-solo
  at: 2026-08-23T00:00:00Z
status: stable
sources:
  - id: source
    resource: https://github.com/langchain-ai/langgraphjs
    title: LangGraphJS Source
---

# Graph 核心 API 参考

本篇覆盖 `@langchain/langgraph` 中 Graph 层的公共 API，包括图构建、状态定义、节点与边。

## StateGraph

`StateGraph` 是构建有状态 Agent 工作流的主入口类。

```typescript
import { StateGraph, Annotation } from "@langchain/langgraph";

const State = Annotation.Root({
  messages: Annotation<BaseMessage[]>({
    reducer: (a, b) => a.concat(b),
    default: () => [],
  }),
});

const graph = new StateGraph(State)
  .addNode("agent", agentNode)
  .addNode("tools", toolNode)
  .addEdge("__start__", "agent")
  .addConditionalEdges("agent", route)
  .compile();
```

### 关键方法

| 方法 | 说明 |
|---|---|
| `addNode(name, action, options?)` | 添加节点；`options` 可含 `retryPolicy`、`cachePolicy`、`timeout`、`errorHandler` |
| `addEdge(source, destination)` | 添加普通边 |
| `addConditionalEdges(source, pathFn, pathMap?)` | 添加条件边；`pathFn` 返回节点名、`Send` 或其数组 |
| `setNodeDefaults(policies)` | 设置图级节点默认策略（重试/缓存/超时/错误处理器） |
| `compile(options?)` | 编译图，返回 `CompiledGraph`（继承 `Pregel`） |

### 节点策略选项（NodePolicyOptions）

- `retryPolicy?: RetryPolicy`：控制退避、最大尝试次数、可重试错误类型
- `cachePolicy?: CachePolicy | boolean`：`true` 启用默认缓存，对象可自定义 `keyFunc`、`ttl`
- `timeout?: number | TimeoutPolicy`：单次尝试的硬墙钟上限（毫秒），超时抛 `NodeTimeoutError`

## Graph 基类

`Graph` 是 `StateGraph` 的基类，提供无状态图能力。`CompiledGraph` 继承自 `Pregel`，编译后即可调用 `invoke`、`stream`、`getState`、`updateState` 等方法。

## Branch（条件边）

`Branch` 类封装条件路由逻辑：

- 持有 `path: Runnable`（路由函数）和可选 `ends: Record<string, N | typeof END>`（路径映射）
- `run(writer, reader?)` 注册一个 writer，在源节点完成后执行路由
- `_route` 调用 `path.invoke`，将字符串结果转为通道写入，将 `Send` 转为动态任务

在条件边中抛出 `NodeInterrupt` 会被检测并打印警告——中断只能在节点内抛出，不能在边条件中抛出。

## Annotation

`Annotation` 是状态通道的工厂函数：

```typescript
// 无 reducer：LastValue 通道（last write wins，同一步多写报错）
const name: Annotation<string> = Annotation<string>();

// 有 reducer：BinaryOperatorAggregate 通道
const items = Annotation<string[]>({
  reducer: (left, right) => left.concat(right),
  default: () => [],
});

// 根状态定义
const State = Annotation.Root({ name, items });
// State.State    → 完整状态类型
// State.Update   → 部分更新类型
// State.Node     → 节点函数类型
```

`Annotation.Root(sd)` 返回 `AnnotationRoot` 实例，携带 `lc_graph_name = "AnnotationRoot"` 标记，`spec` 属性保存原始定义。

## 保留节点名

| 常量 | 值 | 含义 |
|---|---|---|
| `START` | `"__start__"` | 图入口 |
| `END` | `"__end__"` | 图出口 |

## Command 与 Send

### `Command`

节点返回 `Command` 可同时更新状态并路由：

```typescript
return new Command({
  update: { foo: "bar" },
  goto: "nextNode",           // 或 Send 数组
  resume: resumeValue,        // 配合 interrupt 使用
  graph: Command.PARENT,      // 子图→父图
});
```

- `Command.PARENT = "__parent__"`：向最近父图发命令
- `_updateAsTuples()`：内部方法，将 update 转为 `[channel, value]` 元组

### `Send`

条件边中动态向节点发送自定义输入（map-reduce 模式）：

```typescript
return items.map((item) => new Send("process", { item }));
```

`Send` 字段：`node: string`、`args: unknown`、可选 `timeout?: TimeoutPolicy`。

### `Overwrite`

绕过 reducer 直接替换通道值：

```typescript
return { messages: new Overwrite(["replacement"]) };
```

同一步多个 `Overwrite` 写入同一通道抛 `InvalidUpdateError`。

## 相关概念

- 状态图与工作流
- Annotation 状态定义
- Pregel 执行引擎
