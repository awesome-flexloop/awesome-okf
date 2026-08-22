---
type: concept
scope: langchainjs
name: tool-definition
version: "0.1.0"
source: https://github.com/langchain-ai/langchainjs
description: LangChain.js 工具定义——StructuredTool 类层次、Zod/JSON Schema 双轨制与 tool 工厂函数
---

# 工具定义

## 工具是什么

工具（Tool）是 Agent 与外部世界交互的桥梁。当模型决定"我需要搜索网络"或"我需要查询数据库"时，它发出一个 tool call，框架执行对应的工具函数，并将结果作为 ToolMessage 返回给模型。

LangChain.js 的工具系统设计目标是：
1. **类型安全**：工具输入通过 schema 校验，TypeScript 类型自动推断
2. **灵活的 schema**：同时支持 Zod 和 JSON Schema
3. **统一的执行接口**：工具本身是 Runnable，享受 invoke/batch/stream/回调/重试能力
4. **自动消息包装**：在 Agent 循环中自动将结果包装为 ToolMessage

## 类层次

```
BaseLangChain (extends Runnable)
└── StructuredTool (abstract)
    ├── Tool (abstract)             // 字符串输入
    │   └── DynamicTool             // 从函数创建
    └── DynamicStructuredTool       // 结构化输入，从函数创建
```

### StructuredTool

**源码位置**：`tools/index.ts:95`

所有工具的抽象基类。三个抽象成员：

```typescript
abstract class StructuredTool<SchemaT, SchemaOutputT, ...> extends BaseLangChain {
  abstract name: string;
  abstract description: string;
  abstract schema: SchemaT;
  returnDirect = false;
  responseFormat: ResponseFormat = "content";

  protected abstract _call(
    arg: SchemaOutputT,
    runManager?: CallbackManagerForToolRun,
    parentConfig?: ToolRunnableConfig
  ): Promise<ToolOutputT> | AsyncGenerator<ToolEventT, ToolOutputT>;
}
```

- `name`：工具的唯一标识，模型通过此名称调用工具
- `description`：告诉模型工具的用途，直接影响模型是否选择该工具
- `schema`：输入校验 schema（Zod 或 JSON Schema）
- `returnDirect`：为 true 时 Agent 调用此工具后直接返回结果，停止循环
- `responseFormat`：`"content"` 或 `"content_and_artifact"`

### Tool（字符串输入基类）

**源码位置**：`tools/index.ts:356`

固定 schema 为 `{ input?: string }`：

```typescript
abstract class Tool extends StructuredTool<StringInputToolSchema, ...> {
  schema = z.object({ input: z.string().optional() })
    .transform((obj) => obj.input);
}
```

适合只接受单个字符串参数的简单工具。

### DynamicTool / DynamicStructuredTool

具体实现类，通过构造函数传入 `name`、`description`、`func`、`schema`，`_call` 直接委托给 `func`。通常不直接 `new`，而是通过 `tool()` 工厂创建。

## tool() 工厂函数

**源码位置**：`tools/index.ts:642`

创建工具的推荐方式：

```typescript
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const search = tool(
  async ({ query }) => {
    return `搜索结果: ${query}`;
  },
  {
    name: "search",
    description: "搜索网络获取信息",
    schema: z.object({
      query: z.string().describe("搜索关键词"),
    }),
  }
);
```

### 重载与返回类型推断

`tool()` 具有大量重载，根据 schema 类型在编译期决定返回类型：

| schema 类型 | 返回类型 |
|---|---|
| `ZodString`（v3 或 v4） | `DynamicTool` |
| 未提供 schema | `DynamicTool`（字符串输入） |
| `ZodObject`（v3 或 v4） | `DynamicStructuredTool` |
| `JSONSchema`（验证字符串） | `DynamicTool` |
| `JSONSchema`（验证对象） | `DynamicStructuredTool` |

判断逻辑在 `index.ts:914-918`：

```typescript
const isSimpleStringSchema = isSimpleStringZodSchema(fields.schema);
const isStringJSONSchema = validatesOnlyStrings(fields.schema);
if (!fields.schema || isSimpleStringSchema || isStringJSONSchema) {
  return new DynamicTool(...);
}
return new DynamicStructuredTool(...);
```

### 带 Runtime 的工具签名

工具函数可以接收第二个参数 `ToolRuntime<TState, TContext>`，访问 Agent 状态和上下文：

```typescript
const myTool = tool(
  async (input, runtime) => {
    // runtime.context 访问上下文
    // runtime.config 访问 RunnableConfig
    return result;
  },
  { name: "my_tool", schema: z.object({ ... }) }
);
```

## Schema 双轨制

### Zod Schema

Zod 是首选方案，提供：
- 编译时类型推断
- 运行时校验
- Transform 支持（输入类型和输出类型可以不同）
- `.describe()` 为字段生成文档

```typescript
schema: z.object({
  location: z.string().describe("城市名称"),
  units: z.enum(["celsius", "fahrenheit"]).default("celsius"),
})
```

代码同时兼容 Zod v3（`zod/v3`）和 v4（`zod/v4`），通过 `InteropZodType` 统一抽象。

### JSON Schema

适用于动态场景或跨平台场景：

```typescript
schema: {
  type: "object",
  properties: {
    query: { type: "string", description: "搜索关键词" }
  },
  required: ["query"]
}
```

JSON Schema 通过 `@cfworker/json-schema` 的 `validate` 函数校验。

### 校验流程

在 `StructuredTool.call`（`index.ts:236-272`）中：

1. 若 input 是 ToolCall，提取 `.args`
2. Zod schema：调用 `interopParseAsync`，失败时用 `z4.prettifyError` 格式化错误
3. JSON Schema：调用 `validate`，失败时收集 `keywordLocation` 和 error
4. 校验失败抛出 `ToolInputParsingException`，包含原始输入
5. `verboseParsingErrors: true` 时在错误消息中包含详细信息

## 工具执行流程

`StructuredTool.invoke`（`index.ts:175-209`）的执行流程：

```
invoke(input, config)
  ├─ input 是 ToolCall? → 提取 args，注入 toolCall 到 config
  └─ call(toolInput, enrichedConfig)
       ├─ Schema 校验（Zod 或 JSON Schema）
       ├─ CallbackManager.handleToolStart(..., toolCallId)
       ├─ _call(parsed, runManager, config)
       │    ├─ 返回 Promise → await
       │    └─ 返回 AsyncGenerator → consumeAsyncGenerator + handleToolEvent
       ├─ responseFormat === "content_and_artifact"?
       │    └─ 解构 [content, artifact]
       └─ _formatToolOutput(content, artifact, toolCallId, ...)
            ├─ 有 toolCallId 且 content 非 DirectToolOutput?
            │    └─ 创建 ToolMessage { status: "success", content, tool_call_id, ... }
            └─ 否则直接返回 content
```

### 条件返回类型

`ToolReturnType<TInput, TConfig, TOutput>`（`types.ts:64-75`）根据调用上下文决定返回类型：

- input 是 `ToolCall` → 返回 `ToolMessage`
- config 含 `toolCall.id`（string）→ 返回 `ToolMessage`
- config 含 `toolCall.id: undefined` → 返回原始输出
- output 实现 `DirectToolOutput` → 返回 output 本身
- 其他 → 返回原始输出

这让同一个工具既能在 Agent 中自动包装为消息，也能在代码中直接调用获得类型化结果。

### content_and_artifact 模式

当工具需要同时返回"给模型看的内容"和"给程序用的完整数据"时：

```typescript
const fileReader = tool(
  async ({ path }) => {
    const fullText = await readFile(path, "utf-8");
    const summary = fullText.slice(0, 500);
    return [summary, { fullText, path }] as const;
  },
  {
    name: "read_file",
    description: "读取文件内容",
    schema: z.object({ path: z.string() }),
    responseFormat: "content_and_artifact",
  }
);
```

`content`（摘要）发送给模型，`artifact`（完整文本）可在代码中通过 `ToolMessage.artifact` 访问。

## BaseToolkit

**源码位置**：`tools/index.ts:571`

工具集合基类，将相关工具分组：

```typescript
abstract class BaseToolkit {
  abstract tools: StructuredToolInterface[];
  getTools(): StructuredToolInterface[];
}
```

适用于一组相关工具（如数据库 toolkit 包含 query_tables、describe_table、execute_sql 等）。

## ClientTool vs ServerTool

```typescript
type ClientTool = StructuredToolInterface | DynamicTool | RunnableToolLike;
type ServerTool = Record<string, unknown>;
```

- **ClientTool**：在本地执行的工具，框架负责调用和消息包装
- **ServerTool**：由模型 provider 端托管的工具（如 OpenAI 的 web_search），仅传递配置，不在本地执行

## 相关文档

- [消息系统](/langchain-ai/langchainjs/concepts/message-system) — ToolMessage 与 ToolCall
- [ReAct Agent](/langchain-ai/langchainjs/concepts/react-agent) — 工具在 Agent 循环中的调用
- [Message 与 Tool API](/langchain-ai/langchainjs/references/messages-tools) — 完整 API 参考
