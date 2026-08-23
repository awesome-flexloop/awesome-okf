---
type: Concept
title: Annotation 状态定义
description: 使用 Annotation.Root 声明图状态，理解 reducer、默认值与类型推导
tags: [annotation, state, typing, reducer]
generated:
  by: reference_agent/trae-solo
  at: 2026-08-23T00:00:00Z
status: stable
sources:
  - id: source
    resource: https://github.com/langchain-ai/langgraphjs
    title: LangGraphJS Source
---

# Annotation 状态定义

`Annotation` 是 LangGraphJS 中声明图状态结构的 DSL。它将每个状态字段映射为一个[通道](channels)实例，决定该字段的更新语义、默认值和类型。

## 基本用法

```typescript
import { Annotation } from "@langchain/langgraph";

const State = Annotation.Root({
  // 无 reducer：LastWriteWins 通道
  query: Annotation<string>(),

  // 有 reducer：归约聚合通道
  results: Annotation<string[]>({
    reducer: (current, update) => current.concat(update),
    default: () => [],
  }),
});
```

`Annotation.Root(spec)` 返回 `AnnotationRoot` 实例，它携带三个类型插槽供 TypeScript 使用：

- `State.State`：完整状态类型 `{ query: string; results: string[] }`
- `State.Update`：部分更新类型 `{ query?: string; results?: string[] }`
- `State.Node`：节点函数类型 `(state: State) => Update | Promise<Update>`

```typescript
const myNode = (state: typeof State.State): typeof State.Update => {
  return { results: ["new result"] };
};
```

## 两种通道模式

### 无参数：LastValue（Last Write Wins）

`Annotation<T>()` 创建 `LastValue<T>` 通道：

- 每步只允许一个节点写入该字段
- 多节点同一步写入同一字段抛 `INVALID_CONCURRENT_GRAPH_UPDATE`
- 适合「单一来源更新」的状态，如当前路由决策、最终答案

### 带 reducer：BinaryOperatorAggregate

`Annotation<T>({ reducer, default? })` 创建归约通道：

- `reducer: (current: T, update: U) => T`：将新更新与当前值合并
- `default?: () => T`：初始值工厂（首次读取前调用）
- 适合列表累积、计数器、合并字典等场景

```typescript
const State = Annotation.Root({
  messages: Annotation<BaseMessage[]>({
    reducer: (left, right) => left.concat(right),
    default: () => [],
  }),
  score: Annotation<number>({
    reducer: (a, b) => a + b,
    default: () => 0,
  }),
});
```

## 内置消息注解

`MessagesAnnotation` 是预构建的消息状态，等价于：

```typescript
Annotation.Root({
  messages: Annotation<BaseMessage[]>({
    reducer: messagesStateReducer,
    default: () => [],
  }),
});
```

`messagesStateReducer`（别名 `addMessages`）智能处理消息 ID：相同 ID 的消息会被覆盖而非重复追加，支持 `RemoveMessage` 删除消息，`REMOVE_ALL_MESSAGES` 哨兵清空列表。

## Overwrite：绕过 Reducer

即使字段配置了 reducer，节点也可以返回 `Overwrite` 直接替换值：

```typescript
import { Overwrite } from "@langchain/langgraph";

return { messages: new Overwrite([new AIMessage("reset")]) };
```

同一步多个 Overwrite 写入同一通道会抛错。

## 单 Reducer 类型

`SingleReducer<V, U>` 类型支持三种形式：

```typescript
type SingleReducer<V, U = V> =
  | { reducer: BinaryOperator<V, U>; default?: () => V }
  | { value: BinaryOperator<V, U>; default?: () => V }  // 已废弃
  | null;
```

`getChannel` 工厂根据配置决定实例化 `BinaryOperatorAggregate` 还是 `LastValue`。

## Zod Schema 互操作

LangGraphJS 支持用 Zod 定义状态 schema 并自动转换为通道定义：

```typescript
import { z } from "zod/v4";

const stateSchema = z.object({
  query: z.string(),
  results: z.array(z.string()),
});
```

`graph/zod/` 模块提供 Zod 插件、meta 注册表和 schema 注册，`isInteropZodObject`、`interopParse` 等工具函数处理跨运行时 schema 兼容。

## 状态与通道的关系

Annotation 本质是**通道的工厂声明**：

| Annotation 写法 | 编译为通道 | 更新语义 |
|---|---|---|
| `Annotation<T>()` | `LastValue<T>` | 单写，覆盖 |
| `Annotation<T>({ reducer, default })` | `BinaryOperatorAggregate<T>` | 多写归约 |
| `Topic<T>`（直接用通道） | `Topic<T>` | PubSub，可去重/累积 |
| `DeltaChannel<T>` | `DeltaChannel<T>` | 增量写入，周期性快照 |

编译期 `StateGraph` 将 `AnnotationRoot.spec` 转换为通道规格表传入 `Pregel`，运行时只认通道实例。

## 相关概念

- [Channels 通道体系](channels) — 通道的完整类型与语义
- [状态图与工作流](state-graph) — 使用状态构建图
- [Graph 核心 API 参考](/ai/langchain-ai/langgraphjs/references/graph-core)
