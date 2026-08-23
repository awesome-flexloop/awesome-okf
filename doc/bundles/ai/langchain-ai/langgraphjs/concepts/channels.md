---
type: Concept
title: Channels 通道体系
description: BaseChannel 抽象与内置通道类型（LastValue、BinaryOperatorAggregate、Topic、DeltaChannel 等）
tags: [channels, state, basechannel, lastvalue, topic, delta]
generated:
  by: reference_agent/trae-solo
  at: 2026-08-23T00:00:00Z
status: stable
sources:
  - id: source
    resource: https://github.com/langchain-ai/langgraphjs
    title: LangGraphJS Source
---

# Channels 通道体系

通道（Channel）是 LangGraphJS 状态管理的最小原语。图状态的每个字段就是一个通道实例，节点通过通道读写通信，[Pregel 执行引擎](pregel-execution)在超步边界统一更新所有通道。

## BaseChannel 抽象

所有通道继承 `BaseChannel<ValueType, UpdateType, CheckpointType>`，定义四个核心抽象方法：

| 方法 | 职责 |
|---|---|
| `update(values: UpdateType[]): boolean` | 接收一批更新，返回是否有变化；由 Pregel 在每步结束时调用 |
| `get(): ValueType` | 返回当前值；空通道抛 `EmptyChannelError` |
| `checkpoint(): CheckpointType \| undefined` | 序列化当前状态用于持久化 |
| `fromCheckpoint(cp?): this` | 从 checkpoint 恢复一个新通道实例 |

两个生命周期钩子：

- `consume()`：标记值已消费，通道可修改状态防止重复消费
- `finish()`：通知通道 Pregel 运行即将结束

通道通过 `lg_is_channel = true` 标记和 `lc_graph_name` 字符串名做结构类型识别，避免跨版本 instanceof 问题。

## 内置通道类型

### LastValue

存储最近一次写入的值，**每步最多接收一个值**：

```typescript
class LastValue<Value> extends BaseChannel<Value, Value, Value>
```

- 同一步收到多个值 → 抛 `InvalidUpdateError`（code `INVALID_CONCURRENT_GRAPH_UPDATE`）
- 内部用 `[Value] | []` 元组区分「未写入」与「写入了 undefined」
- `Annotation<T>()` 无 reducer 时默认使用此通道
- 适用于单一来源更新的状态（当前路由、最终答案）

### LastValueAfterFinish

变体：值在 `finish()` 被调用后才可读，`consume()` 后清空。用于「图结束时才暴露」的值。

### BinaryOperatorAggregate

用二元归约函数将所有更新聚合：

```typescript
class BinaryOperatorAggregate<ValueType, UpdateType = ValueType>
  extends BaseChannel<ValueType, OverwriteOrValue<ValueType, UpdateType>, ValueType>
```

- 持有 `operator: (a: V, b: U) => V`
- 支持 `OverwriteValue` 绕过 reducer 直接替换（同一步多个 Overwrite 抛错）
- `equals()` 比较 operator 函数引用，判断两通道是否语义等价
- `Annotation<T>({ reducer, default })` 使用此通道
- 适用于列表拼接、计数器、字典合并

### Topic

可配置的发布-订阅通道：

```typescript
class Topic<Value> extends BaseChannel<Array<Value>, Value | Value[], Value[] | [Value[], Value[]]>
```

选项：

- `unique: boolean`：引用相等去重，维护 `seen: Set`
- `accumulate: boolean`：跨超步累积值（默认 false，每步清空）

Checkpoint 格式：
- `unique: true` → `[seen[], values[]]`（去重历史需跨恢复保留）
- 其他 → 扁平 `values[]`（与 Python 实现对齐）

适用于事件广播、多生产者-多消费者场景。

### EphemeralValue

临时值通道，值在消费后即清除，不跨超步保留。用于瞬态信号。

### UntrackedValueChannel

值不被 checkpoint 追踪的通道，用于不需要持久化的临时计算结果。

### DeltaChannel（增量通道）

不将完整值存入 `channel_values`，而是将每次写入作为 pending write 落库，读取时沿 checkpoint 祖先链重放写入直到最近快照：

- `snapshotFrequency`：控制多久写一次全量快照
- 系统级上限 `LANGGRAPH_DELTA_MAX_SUPERSTEPS_SINCE_SNAPSHOT`（默认 5000）强制快照，防止无界祖先遍历
- `getDeltaChannelHistory` 沿 `parentConfig`（而非 `list({before})`）行走，确保分叉线程只重放自己路径上的写入
- `ensureMessageIds` 递归为缺失 ID 的 `BaseMessage` 分配 uuid4，保证重放时消息身份一致

适用于长消息列表等频繁增量更新但全量序列化成本高的场景。

### NamedBarrierValue / DynamicBarrierValue

屏障通道，用于节点间同步：等待所有命名输入到达后才放行。支持静态命名集合与动态注册。

## 通道与 Checkpoint

`emptyChannels(channels, checkpoint)` 是恢复通道集合的入口：

1. 过滤出真正的 `BaseChannel` 实例（通过 `getOnlyChannels`）
2. 对每个通道调用 `fromCheckpoint(checkpoint.channel_values[key])`
3. 返回新通道实例集合

这意味着每个通道自己控制序列化格式，Pregel 和 checkpointer 不介入值的编码——这是跨后端持久化的关键。

## 自定义通道

实现 `BaseChannel` 的四个抽象方法即可创建自定义状态语义：

```typescript
class MyChannel<T> extends BaseChannel<T, T, T> {
  lc_graph_name = "MyChannel";
  private value: T | undefined;

  update(values: T[]): boolean {
    if (!values.length) return false;
    this.value = values[values.length - 1];
    return true;
  }

  get(): T {
    if (this.value === undefined) throw new EmptyChannelError();
    return this.value;
  }

  checkpoint(): T | undefined {
    return this.value;
  }

  fromCheckpoint(cp?: T): this {
    const empty = new MyChannel<T>();
    if (cp !== undefined) empty.value = cp;
    return empty as this;
  }
}
```

## 相关概念

- [Annotation 状态定义](annotation) — 用 DSL 声明通道
- [Pregel 执行引擎](pregel-execution) — 通道如何在超步中被调度
- [Checkpoint 持久化](checkpointing) — 通道状态如何持久化
