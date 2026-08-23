---
type: reference
scope: langchainjs
name: core-runnable
version: "0.1.0"
source: https://github.com/langchain-ai/langchainjs
description: LangChain.js Runnable 核心 API 参考——Runnable 抽象类、RunnableConfig、RunnableSequence 等组合子
---

# Runnable 核心 API 参考

本参考覆盖 `@langchain/core/runnables` 模块的核心抽象。所有 LangChain 主要组件（模型、提示模板、输出解析器、工具、Agent）都继承自 `Runnable`。

## Runnable 抽象类

**源码位置**：`libs/langchain-core/src/runnables/base.ts:124`

```typescript
abstract class Runnable<RunInput, RunOutput, CallOptions extends RunnableConfig>
  extends Serializable
  implements RunnableInterface<RunInput, RunOutput, CallOptions>
```

### 核心方法

| 方法 | 签名 | 说明 |
|---|---|---|
| `invoke` | `(input: RunInput, options?: Partial<CallOptions>) => Promise<RunOutput>` | 抽象方法，单次调用（base.ts:145） |
| `batch` | `(inputs: RunInput[], options?, batchOptions?) => Promise<(RunOutput \| Error)[]>` | 批量调用，默认用 AsyncCaller 并发执行 invoke（base.ts:243） |
| `stream` | `(input: RunInput, options?) => Promise<IterableReadableStream<RunOutput>>` | 流式调用，缓冲首 chunk 以暴露初始错误（base.ts:310） |
| `transform` | `(generator: AsyncGenerator<RunInput>, options) => AsyncGenerator<RunOutput>` | 流变换，默认缓冲后调用 stream |
| `getName` | `(suffix?: string) => string` | 返回运行名称，优先级：`this.name` > `lc_name()` > `constructor.name`（base.ts:138） |

### 组合子方法

| 方法 | 返回类型 | 说明 |
|---|---|---|
| `pipe(coerceable)` | `Runnable<RunInput, NewRunOutput>` | 创建 RunnableSequence（base.ts:615） |
| `withRetry(fields?)` | `RunnableRetry` | 添加重试，参数 `stopAfterAttempt`、`onFailedAttempt`（base.ts:156） |
| `withConfig(config)` | `Runnable` | 绑定配置到新 RunnableBinding（base.ts:175） |
| `withFallbacks(fields)` | `RunnableWithFallbacks` | 添加回退 Runnable（base.ts:192） |
| `pick(keys)` | `Runnable` | 从字典输出中选取键（base.ts:628） |
| `assign(mapping)` | `Runnable` | 向字典输出追加字段（base.ts:636） |

### 受保护方法

- `_streamIterator(input, options?)`：默认 `yield this.invoke()`，子类覆盖以支持真正流式（base.ts:297）
- `_callWithConfig(func, input, options?)`：模板方法，封装回调管理器的 start/error/end 生命周期（base.ts:359）
- `_batchWithConfig(func, inputs, options?, batchOptions?)`：批量版本的回调封装（base.ts:403）
- `_separateRunnableConfigFromCallOptions(options?)`：拆分标准配置与调用选项（base.ts:325）

## RunnableConfig

**源码位置**：`libs/langchain-core/src/runnables/types.ts:80`、`runnables/config.ts`

```typescript
interface RunnableConfig<ConfigurableFieldType = Record<string, any>>
  extends BaseCallbackConfig {
  configurable?: ConfigurableFieldType;
  recursionLimit?: number;   // 默认 25
  maxConcurrency?: number;
  timeout?: number;          // 毫秒
  signal?: AbortSignal;
}
```

`BaseCallbackConfig`（来自 `callbacks/manager.ts`）额外包含 `callbacks?`、`tags?`、`metadata?`、`runName?`、`runId?`。

### 关键工具函数

| 函数 | 位置 | 说明 |
|---|---|---|
| `ensureConfig(config?)` | config.ts:153 | 填充默认值（tags/metadata/recursionLimit=25），从 AsyncLocalStorage 继承隐式配置 |
| `mergeConfigs(...configs)` | config.ts:49 | 深度合并：metadata 浅合并、tags 去重、timeout 取 min、signal 用 AbortSignal.any |
| `patchConfig(config, callbacks?)` | config.ts | 创建带补丁的新配置 |
| `getCallbackManagerForConfig(config?)` | config.ts:33 | 从配置构建 CallbackManager |

常量 `DEFAULT_RECURSION_LIMIT = 25`（config.ts:5）。

## 内置 Runnable 实现

### RunnableSequence

**源码位置**：`base.ts:1925`

由 `first`、`middle: Runnable[]`、`last` 三部分组成。`pipe` 方法在合并两个 Sequence 时做扁平化优化（base.ts:2186-2208），避免深层嵌套。

静态方法 `RunnableSequence.from([...runnables])` 从数组创建序列。

### RunnableMap / RunnableParallel

**源码位置**：`base.ts:2261`、`base.ts:2852`

`RunnableMap` 接收 `steps: Record<string, RunnableLike>`，并行执行所有步骤并返回 `{ key: result }` 对象。`RunnableParallel` 是其子类别名。

### RunnableLambda

**源码位置**：`base.ts:2536`

将普通函数 `(input, options?) => output | Promise<output>` 包装为 Runnable。支持函数返回异步生成器以实现流式。

### RunnableBinding

**源码位置**：`base.ts:1302`

绑定 config 和 kwargs 到 Runnable，由 `withConfig()` 和 `bind()` 创建。

### RunnableRetry

**源码位置**：`base.ts:1727`

使用 `p-retry` 库实现重试逻辑，由 `withRetry()` 创建。

### RunnableWithFallbacks

**源码位置**：`base.ts:2922`

主 Runnable 失败时依次尝试 fallback 列表，由 `withFallbacks()` 创建。

### RunnableEach

**源码位置**：`base.ts:1605`

对输入数组的每个元素调用绑定的 Runnable。

## Graph

**源码位置**：`libs/langchain-core/src/runnables/graph.ts:53`

`Graph` 是用于可视化和序列化的图数据结构（非执行引擎）：

```typescript
class Graph {
  nodes: Record<string, Node>;
  edges: Edge[];
  addNode(data: RunnableInterface | RunnableIOSchema, id?, metadata?): Node;
  removeNode(node: Node): void;
  addEdge(source: Node, target: Node, data?, conditional?): Edge;
  extend(graph: Graph, prefix?): [Node?, Node?];
  firstNode(): Node | undefined;
  lastNode(): Node | undefined;
  trimFirstNode(): void;
  trimLastNode(): void;
  toJSON(): Record<string, any>;
}
```

`Node`（types.ts:72）包含 `id`、`name`、`data`（Runnable 或 IOSchema）、`metadata?`。`Edge`（types.ts:65）包含 `source`、`target`、`data?`、`conditional?`。

`toJSON()` 将 UUID 节点 ID 替换为数字索引以保证序列化稳定性，节点数据区分 `"runnable"` 类型和 `"schema"` 类型。

## 类型定义

### RunnableLike

```typescript
type RunnableLike<RunInput, RunOutput, CallOptions> =
  | RunnableInterface<RunInput, RunOutput, CallOptions>
  | RunnableFunc<RunInput, RunOutput, CallOptions>
  | RunnableMapLike<RunInput, RunOutput>;
```

允许 Runnable 实例、普通函数或 `{ key: RunnableLike }` 对象映射。

### RunnableFunc

```typescript
type RunnableFunc<RunInput, RunOutput, CallOptions> = (
  input: RunInput,
  options: CallOptions | Record<string, any>
) => RunOutput | Promise<RunOutput>;
```

### RunnableBatchOptions

```typescript
type RunnableBatchOptions = {
  maxConcurrency?: number;  // @deprecated 通过 config 传入
  returnExceptions?: boolean;
};
```

## 相关文档

- [Runnable 接口概念](/langchain-ai/langchainjs/concepts/runnable-interface) — 深入理解 Runnable 设计理念
- [消息与工具 API](/langchain-ai/langchainjs/references/messages-tools) — Message 与 Tool 参考
- [Agent 与 Middleware API](/langchain-ai/langchainjs/references/agents-middleware) — ReactAgent 参考
