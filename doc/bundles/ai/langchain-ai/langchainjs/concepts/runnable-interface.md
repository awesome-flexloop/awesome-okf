---
type: concept
scope: langchainjs
name: runnable-interface
version: "0.1.0"
source: https://github.com/langchain-ai/langchainjs
description: LangChain.js Runnable 接口——统一执行抽象、四维调用模型与 LCEL 组合子体系
---

# Runnable 接口

## 为什么需要 Runnable

在 LLM 应用中，组件种类繁多——聊天模型、LLM、提示模板、输出解析器、检索器、工具、Agent。如果每种组件都有自己的调用方式，组合它们将变得极其困难。

LangChain.js 的解法是：**让所有组件实现同一个接口**。这个接口就是 `Runnable`。

`Runnable` 定义在 `@langchain/core/runnables`，是整个框架的基石。Prompt Template 是 Runnable，Chat Model 是 Runnable，Output Parser 是 Runnable，Tool 也是 Runnable。这意味着它们可以用统一的方式调用、组合、流式处理和监控。

## 四维执行模型

`RunnableInterface`（`runnables/types.ts:23`）声明了四个执行维度：

```typescript
interface RunnableInterface<RunInput, RunOutput, CallOptions> {
  // 1. 单次调用
  invoke(input: RunInput, options?): Promise<RunOutput>;

  // 2. 批量调用
  batch(inputs: RunInput[], options?, batchOptions?): Promise<RunOutput[]>;

  // 3. 流式输出
  stream(input: RunInput, options?): Promise<IterableReadableStream<RunOutput>>;

  // 4. 流变换
  transform(generator: AsyncGenerator<RunInput>, options): AsyncGenerator<RunOutput>;

  getName(suffix?): string;
}
```

### invoke：单次调用

最基本的执行方式。接收一个输入，返回一个输出的 Promise。所有 Runnable 子类**必须**实现 `invoke`（抽象方法，`base.ts:145`）。

```typescript
const message = await model.invoke([new HumanMessage("你好")]);
```

### batch：批量调用

接收输入数组，默认使用 `AsyncCaller` 控制并发，对每个输入调用 `invoke`（`base.ts:243-289`）。支持 `returnExceptions: true` 将错误作为返回值而非抛出：

```typescript
const results = await parser.batch([text1, text2, text3], {
  maxConcurrency: 5,
});
```

子类可以覆盖 `batch` 以提供更高效的批量实现（如 API 原生批处理）。

### stream：流式输出

返回 `IterableReadableStream`，逐 chunk 产出结果（`base.ts:310-323`）。默认实现 `_streamIterator` 只是 `yield invoke()`（`base.ts:297-302`），不支持真正流式的组件自动退化为"一次性返回"。

```typescript
const stream = await model.stream([new HumanMessage("写一首诗")]);
for await (const chunk of stream) {
  process.stdout.write(chunk.content);
}
```

`stream` 方法会缓冲第一个 chunk，确保初始化错误（如认证失败）能立即抛出而非在流中延迟出现。

### transform：流变换

最底层的流式 API，接收一个 AsyncGenerator 输入，返回一个 AsyncGenerator 输出。这使得 Runnable 可以作为流式管道中的变换节点：

```typescript
async function* inputGenerator() {
  yield "hello";
  yield "world";
}
const outputGen = runnable.transform(inputGenerator(), config);
```

## LCEL 组合子

Runnable 的真正威力来自**组合子**——这些方法返回新的 Runnable，形成不可变的构建器模式。

### pipe：序列组合

`pipe`（`base.ts:615-623`）是最核心的组合子，将两个 Runnable 串联为 `RunnableSequence`：

```typescript
const chain = prompt.pipe(model).pipe(parser);
// 等价于 RunnableSequence.from([prompt, model, parser])
```

`RunnableSequence` 内部存储 `first`、`middle: Runnable[]`、`last`。当对 Sequence 再次 `pipe` 另一个 Sequence 时，会做**扁平化优化**（`base.ts:2186-2208`），将两个 Sequence 的 middle 数组合并，避免深层嵌套。

### 并行组合

`RunnableMap`（`base.ts:2261`，别名 `RunnableParallel`）并行执行多个 Runnable 并将结果组装为对象：

```typescript
import { RunnableParallel } from "@langchain/core/runnables";

const map = RunnableParallel.from({
  joke: prompt.pipe(model),
  poem: prompt2.pipe(model),
});
const result = await map.invoke({ topic: "猫" });
// { joke: "...", poem: "..." }
```

### withConfig / withRetry / withFallbacks

```typescript
const withConfig = runnable.withConfig({ tags: ["production"], maxConcurrency: 10 });
const withRetry = runnable.withRetry({ stopAfterAttempt: 3 });
const withFallback = runnable.withFallbacks([backupRunnable]);
```

- `RunnableRetry`（`base.ts:1727`）使用 p-retry 库实现重试
- `RunnableWithFallbacks`（`base.ts:2922`）在主 Runnable 失败时依次尝试回退

### pick / assign

```typescript
runnable.pick(["joke"]);          // 从输出对象中选取键
runnable.assign({ extra: fn });   // 向输出对象追加字段
```

## RunnableConfig：执行上下文

每次调用都可以传入 `RunnableConfig`（`types.ts:80-109`）控制执行行为：

```typescript
interface RunnableConfig extends BaseCallbackConfig {
  configurable?: Record<string, any>;  // 运行时可配置参数
  recursionLimit?: number;            // 递归深度限制，默认 25
  maxConcurrency?: number;            // 最大并发
  timeout?: number;                   // 超时（毫秒）
  signal?: AbortSignal;               // 中止信号
  callbacks?: CallbackManager | Handler[];
  tags?: string[];
  metadata?: Record<string, unknown>;
  runName?: string;
}
```

### 配置合并

`mergeConfigs`（`config.ts:49-148`）实现智能合并：
- `metadata` 浅合并
- `tags` 去重合并
- `configurable` 浅合并
- `timeout` 取最小值
- `signal` 使用 `AbortSignal.any` 合并
- `callbacks` 支持数组与管理器的六种组合

### 隐式配置传播

`ensureConfig`（`config.ts:153-200`）从 `AsyncLocalStorageProviderSingleton` 继承隐式配置，但**排除 `runId` 和 `runName`**，防止子运行错误继承父运行 ID。这使得在 AsyncLocalStorage 中设置的配置自动传播到所有子 Runnable，无需逐层传递。

## RunnableLike：灵活的输入类型

`pipe` 等组合子不仅接受 Runnable 实例，还接受 `RunnableLike`（`base.ts:90-99`）：

```typescript
type RunnableLike<RunInput, RunOutput> =
  | RunnableInterface<RunInput, RunOutput>
  | RunnableFunc<RunInput, RunOutput>       // 普通函数
  | RunnableMapLike<RunInput, RunOutput>;   // { key: RunnableLike }
```

普通函数通过 `RunnableLambda`（`base.ts:2536`）自动升格为 Runnable，对象映射通过 `RunnableMap` 自动包装。这使得管道表达式非常简洁：

```typescript
prompt
  .pipe(model)
  .pipe((message) => message.content)  // 函数自动包装
  .pipe(JSON.parse);
```

## 回调与可观测性

`Runnable._callWithConfig`（`base.ts:359-392`）是所有标准调用的内部模板方法，它：

1. 通过 `getCallbackManagerForConfig` 获取回调管理器
2. 触发 `handleChainStart` 事件
3. 使用 `raceWithSignal` 执行实际逻辑（支持超时和中止）
4. 错误时触发 `handleChainError`，成功时触发 `handleChainEnd`

这意味着**所有 Runnable 自动获得 LangSmith 追踪能力**，无需额外埋点。

## 相关文档

- 总览
- 消息系统
- Runnable 核心 API
- 构建 LCEL 链示例
