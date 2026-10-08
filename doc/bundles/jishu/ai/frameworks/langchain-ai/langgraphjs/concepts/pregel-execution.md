---
type: Concept
title: Pregel 执行引擎
description: 超步调度模型、PregelLoop、任务准备与写入应用、中断与重试机制
tags: [pregel, execution, superstep, scheduler, runtime]
generated:
  by: reference_agent/trae-solo
  at: 2026-08-23T00:00:00Z
status: stable
sources:
  - id: source
    resource: https://github.com/langchain-ai/langgraphjs
    title: LangGraphJS Source
---

# Pregel 执行引擎

`Pregel` 类是 LangGraphJS 的核心运行时，实现了受 Google Pregel 启发的**消息传递图计算模型**。用户通常不直接实例化 `Pregel`，而是通过 `StateGraph.compile()` 获得其 `CompiledGraph` 子类，或通过函数式 `entrypoint()` API 获得 Pregel 实例。

## 超步（Superstep）模型

Pregel 以离散的超步为调度单位：

```
超步 0          超步 1          超步 2
┌──────┐       ┌──────┐       ┌──────┐
│节点A │ ──→   │节点B │ ──→   │节点D │
│节点C │       │节点E │       │      │
└──────┘       └──────┘       └──────┘
  并行           并行           并行
  写入           写入           写入
  通道           通道           通道
```

每个超步内：

1. **准备任务**：`_prepareNextTasks` 检查哪些通道自上次被节点见到以来有更新，为受触发的节点创建 `PregelExecutableTask`
2. **并行执行**：`PregelRunner` 并发执行所有任务，任务输出通过 `CONFIG_KEY_SEND` 写入待处理队列
3. **应用写入**：`_applyWrites` 将所有待处理写入批量传给对应通道的 `update()` 方法
4. **检查中断**：`shouldInterrupt` 判断是否配置了 `interruptBefore/After` 断点
5. **Checkpoint**：根据 durability 级别保存 checkpoint
6. **流输出**：通过 `IterableReadableWritableStream` 推送本超步的更新/值/消息

若无任务可执行（图耗尽）或达到 `stop` 条件，循环终止。默认递归限制为 25 个超步（`RECURSION_LIMIT_DEFAULT`），超限抛 `GraphRecursionError`。

## PregelLoop

`PregelLoop` 类封装单次图运行的主循环状态：

```typescript
class PregelLoop {
  checkpoint: Checkpoint;
  channels: Record<string, BaseChannel>;
  step: number;
  stop: number;
  nodes: Record<string, PregelNode>;
  stream: IterableReadableWritableStream;
  // ...
}
```

初始化时（`PregelLoopInitializeParams`）：

- 从 checkpointer 读取最新 checkpoint（或创建空 checkpoint）
- 通过 `emptyChannels` 从 checkpoint 恢复所有通道
- 加载 pending writes（上次未完成的写入）
- 配置中断点、durability、debug 等

主循环在 `tick()` 方法中推进一个超步。

## PregelNode 与通道订阅

`PregelNode` 是运行时的节点表示，通过 `Channel.subscribeTo` 创建：

```typescript
// 订阅单通道
const node = Channel.subscribeTo("messages");

// 订阅多通道
const node = Channel.subscribeTo(["messages", "events"]);
```

每个 `PregelNode` 持有：

- `triggers: string[]`：触发该节点的通道名
- `channels`：要读取的通道映射
- `writes`：节点执行后要写入的通道（通过 `ChannelWrite`）

节点只在**任一触发器通道有新版本**时才执行，通过 `versions_seen` 追踪。

## 写入与读取机制

### 写入（ChannelWrite）

`Channel.writeTo(channels, writes?)` 创建 `ChannelWrite`，它是一个 Runnable，在节点执行后将返回值路由到对应通道：

- 通道名在 `channels` 列表中 → 用 `PASSTHROUGH` 把节点返回值的对应字段写入
- `writes` 映射中的函数 → 先映射再写入
- 节点返回 `Command` → 从 `_updateAsTuples()` 提取元组写入
- 条件边返回 `Send` → 转为动态任务加入下一步

### 读取（ChannelRead / _localRead）

节点执行期间通过 `CONFIG_KEY_READ` 提供的函数读取通道：

- 普通读取：返回通道当前值
- `_localRead(fresh=true)`：返回包含**本超步已写入但尚未 apply** 的「新鲜值」，让节点能看到同一步其他节点的中间结果

## 控制流机制

### 中断（Interrupt）

节点调用 `interrupt(value)` 抛出 `NodeInterrupt`（继承 `GraphBubbleUp`），沿调用栈冒泡到 PregelLoop：

1. 当前超步已完成的写入通过 `putWrites` 持久化
2. checkpoint 保存（含 `INTERRUPT` 通道）
3. 返回 `{ __interrupt__: [{ value }] }` 给调用者
4. 恢复时传入 `resume` 值，写入 `RESUME` 通道，节点从 `interrupt()` 调用处返回该值

`shouldInterrupt` 也支持静态断点：编译时配置 `interruptBefore`/`interruptAfter`，在指定节点执行前后自动中断，无需修改节点代码。

### 排空（Drain）

`RunControl.requestDrain()`（如收到 SIGTERM）抛出 `GraphDrained`，在超步边界协作式停止：当前超步完成、checkpoint 保存、运行退出，稍后可恢复。

### 重试与超时

- `RetryPolicy`：节点失败后按指数退避重试，可配置 `maxAttempts`、`retryOn`
- `TimeoutPolicy`：区分 `runTimeout`（总执行时间）和 `idleTimeout`（无活动时间），超时可触发重试
- 重试耗尽后执行节点级 `errorHandler`，支持 saga 补偿模式

## 任务路径（TaskPath）

`PregelExecutableTask` 携带 `path: TaskPath` 追踪任务在嵌套图/扇出中的位置，支持：

- `SimpleTaskPath`：简单线性路径
- `VariadicTaskPath`：fan-out 任务的索引路径

这使得 `Send` 创建的动态任务和子图任务能被正确追踪、checkpoint 和流式输出。

## Stream 集成

PregelLoop 持有 `IterableReadableWritableStream`，在每个超步的不同阶段推送事件：

- 任务创建 → `tasks` 模式
- 节点返回 → `updates` 模式
- 通道更新后 → `values` 模式
- LLM token → `messages` 模式（通过 `StreamMessagesHandler`）
- checkpoint 保存 → `checkpoints` 模式

新版 `GraphRunStream` + `StreamTransformer` 管线在 Pregel 之上提供可组合的事件投影，用户可注入自定义 transformer。

## 函数式 API

除了 `StateGraph`，`entrypoint()` 也创建 Pregel 实例：

```typescript
const workflow = entrypoint({ name: "wf", checkpointer }, async (input) => {
  const result = await task("step1", async (x) => x + 1)(input);
  return result;
});
```

`task()` 声明可组合的任务单元，`entrypoint` 自动将其包装为 Pregel 节点和通道，适合偏好命令式风格的场景。`getPreviousState()` 在 entrypoint 内访问同线程历史状态。

## 相关概念

- [状态图与工作流](state-graph.md) — 声明式构建 Pregel 程序
- [Channels 通道体系](channels.md) — 节点通信的媒介
- [Checkpoint 持久化](checkpointing.md) — 超步边界的状态保存
