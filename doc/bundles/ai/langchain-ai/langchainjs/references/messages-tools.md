---
type: reference
scope: langchainjs
name: messages-tools
version: "0.1.0"
source: https://github.com/langchain-ai/langchainjs
description: LangChain.js Message 与 Tool API 参考——消息类型层次、ToolCall、StructuredTool 与 tool 工厂
---

# Message 与 Tool API 参考

本参考覆盖 `@langchain/core/messages` 和 `@langchain/core/tools` 两个核心模块。

## Message 类型层次

所有消息类继承自 `BaseMessage`（`messages/base.ts`），通过 `readonly type` 字面量类型区分角色。

### BaseMessage

**源码位置**：`messages/base.ts`

```typescript
abstract class BaseMessage<TStructure, TRole extends MessageType> {
  content: MessageContent;           // string | ContentBlock[]
  additional_kwargs?: Record<string, unknown>;  // @deprecated
  response_metadata?: Record<string, unknown>;
  id?: string;
  name?: string;
  abstract readonly type: MessageType;
}
```

`MessageContent = string | Array<ContentBlock>`（base.ts:52）。ContentBlock 支持 text、image、tool_call、tool_result 等多模态块类型。

核心工具函数：
- `mergeContent(first, second): MessageContent`（base.ts:110）——合并两段内容，处理字符串/数组的各种组合
- `coerceMessageLikeToMessage(messageLike)`——将 `[role, content]` 元组或普通对象转换为消息实例
- `isBaseMessage(x)`——类型守卫

### HumanMessage

**源码位置**：`messages/human.ts:18`

```typescript
class HumanMessage extends BaseMessage<TStructure, "human"> {
  readonly type = "human";
}
```

表示用户输入消息。对应 Chunk 类 `HumanMessageChunk`，支持 `concat` 拼接。

### SystemMessage

**源码位置**：`messages/system.ts:18`

```typescript
class SystemMessage extends BaseMessage<TStructure, "system"> {
  readonly type = "system";
  concat(chunk: string | SystemMessage): SystemMessage;
}
```

表示系统指令消息。`concat` 支持字符串参数直接拼接。

### AIMessage

**源码位置**：`messages/ai.ts:46`

```typescript
class AIMessage extends BaseMessage<TStructure, "ai"> {
  readonly type = "ai";
  tool_calls?: ToolCall[];
  invalid_tool_calls?: InvalidToolCall[];
  usage_metadata?: UsageMetadata;
}
```

表示模型响应。工具调用是一等字段而非藏在 additional_kwargs 中。构造函数自动从 `additional_kwargs.tool_calls` 迁移并发出弃用警告（ai.ts:81-96）。

`lc_aliases` 覆盖确保 `tool_calls`、`invalid_tool_calls`、`usage_metadata` 在序列化时保持 snake_case。

### ToolMessage

**源码位置**：`messages/tool.ts:53`

```typescript
class ToolMessage extends BaseMessage<TStructure, "tool">
  implements DirectToolOutput {
  readonly type = "tool";
  lc_direct_tool_output = true;
  tool_call_id: string;
  status?: "success" | "error";
  artifact?: any;
  metadata?: Record<string, unknown>;
}
```

表示工具执行结果。`tool_call_id` 必填，关联对应的 `AIMessage.tool_calls[].id`。`status` 字段原生表达工具成功/失败。

构造函数支持两种签名：
- `new ToolMessage(fields, tool_call_id, name?)`
- `new ToolMessage(fields: ToolMessageFields)`

### ToolCall

**源码位置**：`messages/tool.ts:228`

```typescript
interface ToolCall<TName extends string = string, TArgs = Record<string, any>> {
  readonly type?: "tool_call";
  id?: string;
  name: TName;
  args: TArgs;
}
```

流式传输中的增量形式为 `ToolCallChunk`（tool.ts:293），其中 `args?: string` 为 JSON 字符串片段。

### DirectToolOutput

**源码位置**：`messages/tool.ts:37`

```typescript
interface DirectToolOutput {
  readonly lc_direct_tool_output: true;
}
```

标记接口。`isDirectToolOutput(x)` 类型守卫检查该标记。工具返回值实现此接口时，不自动包装为 ToolMessage。

## Tool 类型层次

### StructuredTool

**源码位置**：`tools/index.ts:95`

```typescript
abstract class StructuredTool<SchemaT, SchemaOutputT, SchemaInputT, ToolOutputT, ToolEventT>
  extends BaseLangChain<StructuredToolCallInput, ToolOutputT | ToolMessage>
  implements StructuredToolInterface {
  abstract name: string;
  abstract description: string;
  abstract schema: SchemaT;
  extras?: Record<string, unknown>;
  returnDirect = false;
  responseFormat: ResponseFormat = "content";
  defaultConfig?: ToolRunnableConfig;

  protected abstract _call(
    arg: SchemaOutputT,
    runManager?: CallbackManagerForToolRun,
    parentConfig?: ToolRunnableConfig
  ): Promise<ToolOutputT> | AsyncGenerator<ToolEventT, ToolOutputT>;
}
```

**关键方法**：

- `invoke(input, config?)`（index.ts:175）——若 input 是 ToolCall 则提取 args 并注入 toolCall 到 config，委托给 `call`
- `call(arg, configArg?, tags?)`（index.ts:222，@deprecated）——完整的工具执行流程：schema 校验 → 回调 start → `_call` 执行 → ToolMessage 包装
- `_call` 支持返回 `AsyncGenerator`，通过 `consumeAsyncGenerator` 消费并触发 `handleToolEvent`

**Schema 校验**（index.ts:236-272）：
- Zod schema：使用 `interopParseAsync`（兼容 Zod v3/v4），错误用 `z4.prettifyError` 格式化
- JSON Schema：使用 `@cfworker/json-schema` 的 `validate`
- 失败抛出 `ToolInputParsingException`

### Tool

**源码位置**：`tools/index.ts:356`

```typescript
abstract class Tool<ToolOutputT, ToolEventT>
  extends StructuredTool<StringInputToolSchema, ...> {
  schema = z.object({ input: z.string().optional() })
    .transform((obj) => obj.input);
}
```

字符串输入工具的便捷基类。`call` 重写以自动将字符串参数包装为 `{ input: arg }`。

### DynamicTool

**源码位置**：`tools/index.ts:412`

从函数动态创建的字符串工具。属性 `name`、`description`、`func`。`_call` 直接调用 `this.func(input, runManager, parentConfig)`。

### DynamicStructuredTool

**源码位置**：`tools/index.ts:478`

从函数动态创建的结构化工具。比 DynamicTool 多一个 `schema: SchemaT` 属性，支持 Zod 或 JSON Schema。

### BaseToolkit

**源码位置**：`tools/index.ts:571`

```typescript
abstract class BaseToolkit {
  abstract tools: StructuredToolInterface[];
  getTools(): StructuredToolInterface[];
}
```

工具集合基类，用于将相关工具分组提供给 Agent。

## tool 工厂函数

**源码位置**：`tools/index.ts:642`

```typescript
function tool<SchemaT, ToolOutputT, NameT, ...>(
  func: RunnableFunc | ((input, runtime: ToolRuntime) => ...),
  fields: ToolWrapperParams<SchemaT, NameT>
): DynamicTool | DynamicStructuredTool<...>;
```

**参数 fields**：

| 字段 | 类型 | 说明 |
|---|---|---|
| `name` | `string` | 工具名称（必填） |
| `description?` | `string` | 工具描述，默认取 schema 描述或 `${name} tool` |
| `schema?` | `ZodType \| JSONSchema` | 输入 schema，未提供时为字符串 schema |
| `responseFormat?` | `"content" \| "content_and_artifact"` | 输出格式 |
| `returnDirect?` | `boolean` | Agent 调用后是否停止循环 |
| `verboseParsingErrors?` | `boolean` | 校验错误是否显示详情 |

**返回值推断逻辑**（index.ts:914-918）：
- schema 未提供、为简单字符串 Zod schema、或仅验证字符串的 JSON Schema → 返回 `DynamicTool`
- 否则 → 返回 `DynamicStructuredTool`

工厂函数内部通过 `AsyncLocalStorageProviderSingleton.runWithConfig` 在正确的异步上下文中执行用户函数，并处理 AbortSignal（index.ts:965-1014）。

## 核心类型

### ToolRunnableConfig

**源码位置**：`tools/types.ts:120`

```typescript
type ToolRunnableConfig<ConfigurableFieldType, ContextSchema> =
  RunnableConfig<ConfigurableFieldType> & {
    toolCall?: ToolCall;
    context?: ContextSchema;
  };
```

### ResponseFormat

```typescript
type ResponseFormat = "content" | "content_and_artifact" | string;
```

`"content_and_artifact"` 时 `_call` 必须返回 `[content, artifact]` 二元组。

### ToolReturnType（条件类型）

**源码位置**：`tools/types.ts:64`

```typescript
type ToolReturnType<TInput, TConfig, TOutput> =
  TOutput extends DirectToolOutput ? TOutput
  : TConfig extends { toolCall: { id: string } } ? ToolMessage
  : TConfig extends { toolCall: { id: undefined } } ? TOutput
  : TConfig extends { toolCall: { id?: string } } ? TOutput | ToolMessage
  : TInput extends ToolCall ? ToolMessage
  : TOutput;
```

根据输入和配置自动决定返回 ToolMessage 还是原始输出。

### ClientTool / ServerTool

**源码位置**：`tools/index.ts:1075`

```typescript
type ServerTool = Record<string, unknown>;
type ClientTool = StructuredToolInterface | DynamicTool | RunnableToolLike;
```

ServerTool 是由模型 provider 端处理的工具（如 OpenAI hosted tools），ClientTool 是本地执行的工具。

## 相关文档

- [Runnable 核心 API](/ai/langchain-ai/langchainjs/references/core-runnable) — Runnable 抽象参考
- [消息系统概念](/ai/langchain-ai/langchainjs/concepts/message-system) — 消息类型设计理念
- [工具定义概念](/ai/langchain-ai/langchainjs/concepts/tool-definition) — 工具创建与 Schema 设计
