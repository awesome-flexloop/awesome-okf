---
type: Concept
title: Checkpoint 持久化机制
description: Checkpoint 链表结构、BaseCheckpointSaver 抽象、内存与数据库后端、时间旅行与线程分叉
tags: [checkpoint, persistence, memorysaver, time-travel, durability]
generated:
  by: reference_agent/trae-solo
  at: 2026-08-23T00:00:00Z
status: stable
sources:
  - id: source
    resource: https://github.com/langchain-ai/langgraphjs
    title: LangGraphJS Source
---

# Checkpoint 持久化机制

Checkpoint 是 LangGraphJS 实现持久化、恢复、人机协作和时间旅行的基础机制。每执行完一个超步，Pregel 都会生成一个 checkpoint，记录当前所有通道值、版本号和节点执行进度。

## Checkpoint 结构

当前格式版本为 `v: 4`：

```typescript
interface Checkpoint {
  v: number;                                    // 格式版本，当前 4
  id: string;                                   // uuid6 单调递增
  ts: string;                                   // ISO 8601 时间戳
  channel_values: Record<string, unknown>;      // 通道完整值（DeltaChannel 除外）
  channel_versions: Record<string, number|string>;  // 每通道的版本号
  versions_seen: Record<string, Record<string, number|string>>;  // 节点已见版本
}
```

`channel_versions` 是版本向量：每次通道被写入，其版本递增。节点通过比对自己上次见到的版本（记录在 `versions_seen`）判断是否有新输入需要处理。

## CheckpointTuple 与链表

每个 checkpoint 包装在 `CheckpointTuple` 中：

```typescript
interface CheckpointTuple {
  config: RunnableConfig;           // 定位本 checkpoint
  checkpoint: Checkpoint;
  metadata?: CheckpointMetadata;
  parentConfig?: RunnableConfig;    // 指向上一 checkpoint
  pendingWrites?: CheckpointPendingWrite[];  // 本超步尚未 apply 的写入
}
```

`parentConfig` 形成**单向链表**（对线程分叉而言是树）：

```
checkpoint_A ← checkpoint_B ← checkpoint_C (当前)
```

每个 checkpoint 不可变，新状态总是追加新节点而非修改旧节点。

## BaseCheckpointSaver 抽象

所有持久化后端继承 `BaseCheckpointSaver`：

| 方法 | 职责 |
|---|---|
| `getTuple(config)` | 获取单个 checkpoint 及其 pending writes |
| `list(config, options?)` | 列出线程的 checkpoint 历史（异步生成器） |
| `put(config, checkpoint, metadata, newVersions)` | 保存新 checkpoint |
| `putWrites(config, writes, taskId)` | 保存中间写入（任务执行中、checkpoint 前） |
| `deleteThread(threadId)` | 删除线程所有数据 |
| `getDeltaChannelHistory(options)` | 沿祖先链收集 DeltaChannel 写入 |

默认序列化器为 `JsonPlusSerializer`，支持比标准 JSON 更丰富的类型（Date、Uint8Array、特殊标记对象等）。

## 内置后端

### MemorySaver

进程内存存储，用于开发/测试：

- 三级键：`threadId → checkpointNs → checkpointId`
- `storage` 保存 checkpoint 元组，`writes` 保存 pending writes
- **原型污染防护**：`assertSafeStorageKey` 拦截 `__proto__`/`constructor`/`prototype` 键（CWE-1321），底层对象用 `Object.create(null)`
- `toJSON()` 返回 `[MemorySaver]` 防止序列化后端客户端实例

### 生产后端

| 包 | 适合场景 |
|---|---|
| `@langchain/langgraph-checkpoint-postgres` | 生产环境，支持并发、事务 |
| `@langchain/langgraph-checkpoint-sqlite` | 本地开发、边缘部署、单文件持久化 |
| `@langchain/langgraph-checkpoint-redis` | 低延迟缓存、高频读写 |
| `@langchain/langgraph-checkpoint-mongodb` | 文档型存储、已有 MongoDB 基础设施 |

## 线程（Thread）与配置

通过 `RunnableConfig.configurable.thread_id` 标识会话线程：

```typescript
const config = { configurable: { thread_id: "user-123" } };

await graph.invoke(input, config);
const snapshot = await graph.getState(config);
```

同 `thread_id` 的多次调用共享 checkpoint 历史，自动从上次状态恢复。

**Checkpoint 命名空间**用 `|` 分隔嵌套子图路径（如 `"parent|child"`），让子图 checkpoint 与父图隔离存储。

## 时间旅行（Time Travel）

沿 `parentConfig` 链可以回溯到任意历史状态：

```typescript
const history = [];
for await (const snapshot of graph.getStateHistory(config)) {
  history.push(snapshot);
}

// 从历史 checkpoint 重新执行
const pastConfig = history[2].config;
await graph.invoke(null, pastConfig);
```

## 线程分叉（Fork）

从历史 checkpoint 启动新执行会创建分叉：

```
A ← B ← C (原线程)
      ↖ D ← E (分叉线程)
```

`getDeltaChannelHistory` 沿 `parentConfig` 向上走（而非用 `list({before})`），确保分叉线程只重放自己祖先路径上的 DeltaChannel 写入，不会混入其他分支。

## 持久化级别（Durability）

`Durability` 类型控制 checkpoint 写入时机：

- `"sync"`：每个超步同步落盘，最安全但最慢
- `"async"`：异步写入（默认），平衡性能与持久性
- `"exit"`：仅图结束时写入，最快但崩溃丢失中间进度

## Pending Writes 与中断恢复

节点执行中通过 `putWrites` 增量保存写入。若节点调用 `interrupt()` 暂停：

1. 已完成的写入已持久化
2. 整个 checkpoint 保存
3. 下次以相同 `thread_id` 调用并传入 resume 值时，从断点精确恢复

这使得**人机协作（HITL）**无需额外基础设施——暂停就是写 checkpoint，审批后恢复就是读 checkpoint 继续。

## 相关概念

- [Channels 通道体系](channels.md) — checkpoint 序列化的是通道状态
- [Pregel 执行引擎](pregel-execution.md) — 超步边界触发 checkpoint
- Checkpoint 与流式 API 参考
