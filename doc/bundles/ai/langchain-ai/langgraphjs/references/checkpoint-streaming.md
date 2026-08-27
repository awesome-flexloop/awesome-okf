---
type: Reference
title: Checkpoint 持久化与流式 API 参考
description: BaseCheckpointSaver、MemorySaver、Checkpoint 结构、StreamMode、Pregel 流式方法的 API 参考
tags: [api, checkpoint, streaming, persistence, reference]
generated:
  by: reference_agent/trae-solo
  at: 2026-08-23T00:00:00Z
status: stable
sources:
  - id: source
    resource: https://github.com/langchain-ai/langgraphjs
    title: LangGraphJS Source
---

# Checkpoint 持久化与流式 API 参考

## Checkpoint 数据结构

当前 checkpoint 格式版本为 `v: 4`。

```typescript
interface Checkpoint {
  v: number;                              // 格式版本，当前 4
  id: string;                             // uuid6
  ts: string;                             // ISO 时间戳
  channel_values: Record<string, unknown>;
  channel_versions: Record<string, number | string>;
  versions_seen: Record<string, Record<string, number | string>>;
}
```

`CheckpointTuple` 将 checkpoint 与其上下文打包：

```typescript
interface CheckpointTuple {
  config: RunnableConfig;
  checkpoint: Checkpoint;
  metadata?: CheckpointMetadata;
  parentConfig?: RunnableConfig;          // 形成链表
  pendingWrites?: CheckpointPendingWrite[];
}
```

## BaseCheckpointSaver

所有 checkpointer 的抽象基类：

```typescript
abstract class BaseCheckpointSaver<V extends string | number = number> {
  serde: SerializerProtocol;             // 默认 JsonPlusSerializer

  get(config): Promise<Checkpoint | undefined>;
  abstract getTuple(config): Promise<CheckpointTuple | undefined>;
  abstract list(config, options?): AsyncGenerator<CheckpointTuple>;
  abstract put(config, checkpoint, metadata, newVersions): Promise<RunnableConfig>;
  abstract putWrites(config, writes, taskId): Promise<void>;
  abstract deleteThread(threadId): Promise<void>;
  getDeltaChannelHistory(options): Promise<Record<string, DeltaChannelHistory>>;
}
```

### 内置实现

| Saver | 包 | 用途 |
|---|---|---|
| `MemorySaver` | `@langchain/langgraph-checkpoint` | 开发/测试，进程内存 |
| Postgres saver | `@langchain/langgraph-checkpoint-postgres` | 生产持久化 |
| SQLite saver | `@langchain/langgraph-checkpoint-sqlite` | 本地/边缘持久化 |
| Redis saver | `@langchain/langgraph-checkpoint-redis` | 缓存/快速存取 |
| MongoDB saver | `@langchain/langgraph-checkpoint-mongodb` | 文档存储 |

### MemorySaver 安全设计

`MemorySaver` 使用三级键 `threadId → checkpointNs → checkpointId`，并实施两层原型污染防护（CWE-1321）：

1. `assertSafeStorageKey` 拦截 `__proto__`、`constructor`、`prototype` 键
2. 底层 `storage` 与 `writes` 对象使用 `Object.create(null)`

## 持久化配置

编译图时传入 checkpointer 即可启用持久化：

```typescript
import { MemorySaver } from "@langchain/langgraph";

const checkpointer = new MemorySaver();
const graph = builder.compile({ checkpointer });

const config = { configurable: { thread_id: "user-123" } };
await graph.invoke(input, config);
const state = await graph.getState(config);
```

### Durability 级别

`Durability` 类型控制 checkpoint 写入时机：

- `"sync"`：每个超步同步写入（最安全，最慢）
- `"async"`：异步写入（默认，平衡性能与安全）
- `"exit"`：仅在图结束时写入（最快，但崩溃丢失中间状态）

## 流式 API

### StreamMode

```typescript
type StreamMode =
  | "values"        // 每步完整状态
  | "updates"       // 每步节点增量更新（默认）
  | "messages"      // LLM token 级消息流
  | "debug"         // 调试事件
  | "checkpoints"   // checkpoint 事件
  | "tasks"         // 任务创建/完成
  | "custom"        // 用户自定义流
  | "tools";        // 工具调用事件
```

默认模式为 `"updates"`。

### 调用方式

```typescript
// 单模式
for await (const chunk of graph.stream(input, { streamMode: "values" })) {
  console.log(chunk);
}

// 多模式
for await (const [mode, chunk] of graph.stream(input, {
  streamMode: ["updates", "messages"],
})) {
  console.log(mode, chunk);
}

// 子图流式
for await (const [namespace, chunk] of graph.stream(input, {
  streamMode: "updates",
  subgraphs: true,
})) {
  console.log(namespace, chunk);
}

// SSE 编码
const response = await graph.stream(input, {
  encoding: "text/event-stream",
});
```

### 消息推送

节点执行过程中可手动推送消息：

```typescript
import { pushMessage } from "@langchain/langgraph";

pushMessage(new AIMessage({ content: "processing..." }), config);
```

`pushMessage` 要求消息有 `id`；默认写入 `"messages"` 状态键，`stateKey: null` 可禁止持久化。

### 新版 StreamTransformer 管线

`stream/` 模块提供可组合的 transformer：

- `createMessagesTransformer`：消息 token 流
- `createValuesTransformer`：完整状态值
- `createLifecycleTransformer`：生命周期事件（on_chain_start/end 等）
- `createSubgraphDiscoveryTransformer`：子图命名空间发现

通过 `createGraphRunStream` 创建 `GraphRunStream`，用户可注入自定义 `StreamTransformer` 投影自定义事件。

## Pregel 实例方法

编译后的图（`CompiledGraph extends Pregel`）提供：

| 方法 | 说明 |
|---|---|
| `invoke(input, config?)` | 执行图并返回最终状态 |
| `stream(input, config?)` | 流式执行，返回 `AsyncIterable` |
| `streamEvents(input, config?)` | LangChain v2 事件流 |
| `getState(config)` | 获取当前 `StateSnapshot` |
| `getStateHistory(config, options?)` | 遍历 checkpoint 历史 |
| `updateState(config, values, asNode?)` | 手动更新状态 |
| `withConfig(config)` | 返回绑定配置的新实例 |

## 相关概念

- Checkpoint 持久化机制
- Channels 通道体系
- Pregel 执行引擎
