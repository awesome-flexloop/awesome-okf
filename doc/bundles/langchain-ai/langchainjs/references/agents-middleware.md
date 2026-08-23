---
type: reference
scope: langchainjs
name: agents-middleware
version: "0.1.0"
source: https://github.com/langchain-ai/langchainjs
description: LangChain.js ReactAgent 与 Middleware API 参考——createAgent、AgentMiddleware、状态注解
---

# Agent 与 Middleware API 参考

本参考覆盖 `langchain/agents` 模块的 `createAgent` 工厂、`ReactAgent` 类、`createMiddleware` 以及状态注解系统。

## createAgent 工厂

**源码位置**：`libs/langchain/src/agents/index.ts:672`

```typescript
function createAgent<Types>(params: CreateAgentParams): ReactAgent<Types>;
```

`createAgent` 是创建生产级 ReAct Agent 的唯一推荐入口。它返回 `ReactAgent` 实例，内部编译为 LangGraph `CompiledStateGraph`。

### CreateAgentParams

| 参数 | 类型 | 说明 |
|---|---|---|
| `model` / `llm` | `BaseChatModel \| string` | 聊天模型实例或字符串标识（如 `"openai:gpt-4o"`）。必填，不可预绑定工具 |
| `tools?` | `(ClientTool \| ServerTool)[]` | 客户端工具（本地执行）或服务端工具（provider 托管） |
| `systemPrompt?` | `string \| SystemMessage \| Function` | 系统提示，支持动态函数 |
| `middleware?` | `AnyAgentMiddleware[]` | 中间件数组，按顺序执行 |
| `responseFormat?` | Zod/JSONSchema/Strategy | 结构化输出格式 |
| `stateSchema?` | `StateDefinitionInit` | 自定义状态 schema |
| `contextSchema?` | `InteropZodObject \| AnnotationRoot` | 上下文 schema |
| `name?` | `string` | Agent 名称 |
| `version?` | `"v1" \| "v2"` | 工具行为版本，默认 `"v2"` |
| `signal?` | `AbortSignal` | 中止信号 |

### 返回值 ReactAgent

`ReactAgent` 实例具有以下方法（继承自编译后的图）：

- `invoke(input, config?)` — 单次调用，input 为 `{ messages: BaseMessageLike[] }`
- `stream(input, config?)` — 流式调用，支持多种 streamMode
- `getState(config?)` — 获取当前状态
- `updateState(input, config?)` — 更新状态
- `streamEvents(input, config?)` — 细粒度事件流

### 重载签名

`createAgent` 具有13个类型重载（index.ts:176-669），根据 `responseFormat` 的类型精确推断返回类型：
- 单个 InteropZodType → 推断结构化响应类型
- InteropZodType[] → 推断联合类型
- JsonSchemaFormat / JsonSchemaFormat[]
- SerializableSchema / SerializableSchema[]
- ToolStrategy / TypedToolStrategy / ProviderStrategy
- 无 responseFormat / responseFormat: undefined

## ReactAgent 类

**源码位置**：`libs/langchain/src/agents/ReactAgent.ts:164`

```typescript
class ReactAgent<Types extends AgentTypeConfig> {
  declare readonly "~agentTypes": Types;
  readonly options: CreateAgentParams;
}
```

### 图结构

ReactAgent 内部构建以下节点拓扑（ReactAgent.ts:257-402）：

```
START → [beforeAgent nodes...] → [beforeModel nodes...] → AgentNode
                                                              ↓
                                              [afterModel nodes...] (逆序)
                                                              ↓
                                          ┌── 有 tool_calls → ToolNode
                                          │                      ↓
                                          └── 回到 loopEntry ────┘
                                                              ↓
                                              [afterAgent nodes...] → END
```

- **AgentNode**：绑定工具、注入系统提示、调用模型
- **ToolNode**：执行客户端工具，支持 `wrapToolCall` middleware 包装
- **入口节点**优先级：beforeAgent → beforeModel → AgentNode
- **循环入口**（工具返回后）：beforeModel → AgentNode
- **出口节点**：最后一个 afterAgent 或 END

### 核心私有字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `#graph` | `CompiledStateGraph` | 编译后的 LangGraph 图 |
| `#toolBehaviorVersion` | `"v1" \| "v2"` | 工具行为版本 |
| `#agentNode` | `AgentNode` | 模型调用节点 |
| `#defaultConfig` | `RunnableConfig` | 默认配置，含 `ls_integration: "langchain_create_agent"` |

### BaseGraphDestination

```typescript
type BaseGraphDestination =
  | typeof TOOLS_NODE_NAME   // "tools"
  | typeof AGENT_NODE_NAME   // "model_request"
  | typeof END;
```

middleware 的 `jumpTo` 只能跳转到这三个目标之一。

## AgentMiddleware

**源码位置**：`libs/langchain/src/agents/middleware/types.ts`

### 接口定义

```typescript
interface AgentMiddleware<TSchema, TContextSchema, ...> {
  name: string;
  stateSchema?: StateDefinitionInit;
  contextSchema?: InteropZodObject;
  tools?: readonly (ClientTool | ServerTool)[];
  streamTransformers?: ReadonlyArray<() => StreamTransformer>;

  beforeAgent?: BeforeAgentHook;
  beforeModel?: BeforeModelHook;
  afterModel?: AfterModelHook;
  afterAgent?: AfterAgentHook;
  wrapModelCall?: WrapModelCallHook;
  wrapToolCall?: WrapToolCallHook;
}
```

### 钩子类型

| 钩子 | 执行时机 | 执行次数 | 图节点 |
|---|---|---|---|
| `beforeAgent` | Agent 启动时 | 一次 | `${name}.before_agent` |
| `beforeModel` | 每次模型调用前 | 循环内 | `${name}.before_model` |
| `afterModel` | 模型调用后 | 循环内（逆序） | `${name}.after_model` |
| `afterAgent` | Agent 结束时 | 一次 | `${name}.after_agent` |
| `wrapModelCall` | 包装模型调用 | 每次模型调用 | 注入 AgentNode |
| `wrapToolCall` | 包装工具调用 | 每次工具调用 | 注入 ToolNode |

### 钩子返回值

`MiddlewareResult<TState>`（types.ts:135）：

```typescript
type MiddlewareResult<TState> =
  | (TState & { jumpTo?: JumpToTarget })
  | void;
```

钩子可返回部分状态更新，或通过 `jumpTo` 控制流跳转。`JumpToTarget = "model_request" | "tools" | "end" | undefined`。

### createMiddleware 工厂

**源码位置**：`libs/langchain/src/agents/middleware.ts:76`

```typescript
function createMiddleware<TSchema, TContextSchema, TTools>(
  config: {
    name: string;
    stateSchema?: TSchema;
    contextSchema?: TContextSchema;
    beforeAgent?, beforeModel?, afterModel?, afterAgent?,
    wrapModelCall?, wrapToolCall?,
    tools?, streamTransformers?
  }
): AgentMiddleware<...>;
```

提供自动 schema 推断，支持 Zod 和 StateSchema 两种形式。

## 内置 Middleware

**源码位置**：`libs/langchain/src/agents/middleware/index.ts`

| Middleware | 工厂函数 | 功能 |
|---|---|---|
| HITL | — | 人类在环审批 |
| Summarization | `summarizationMiddleware` | 上下文摘要压缩 |
| Dynamic System Prompt | `dynamicSystemPromptMiddleware` | 动态系统提示 |
| LLM Tool Selector | `llmToolSelectorMiddleware` | LLM 驱动的工具选择 |
| PII | `piiMiddleware` | PII 检测 |
| PII Redaction | `piiRedactionMiddleware` | PII 脱敏 |
| Context Editing | `contextEditingMiddleware` | 上下文编辑/清理 |
| Tool Call Limit | `toolCallLimitMiddleware` | 工具调用次数限制 |
| TODO List | `todoListMiddleware` | TODO 列表管理 |
| Model Call Limit | `modelCallLimitMiddleware` | 模型调用次数限制 |
| Model Fallback | `modelFallbackMiddleware` | 模型失败回退 |
| Model Retry | `modelRetryMiddleware` | 模型调用重试 |
| Tool Retry | `toolRetryMiddleware` | 工具调用重试 |
| Tool Error | `toolErrorMiddleware` | 工具错误处理 |
| Tool Emulator | `toolEmulatorMiddleware` | 工具模拟 |
| Provider Tool Search | `providerToolSearchMiddleware` | Provider 工具搜索 |
| OpenAI Moderation | `openAIModerationMiddleware` | OpenAI 内容审核 |
| Anthropic Prompt Caching | `anthropicPromptCachingMiddleware` | Anthropic 提示缓存 |
| Bedrock Prompt Caching | `bedrockPromptCachingMiddleware` | AWS Bedrock 提示缓存 |

## 状态注解系统

### createAgentState

**源码位置**：`libs/langchain/src/agents/annotation.ts:24`

```typescript
function createAgentState(
  hasStructuredResponse: boolean,
  stateSchema: TStateSchema | undefined,
  middlewareList: AnyAgentMiddleware[]
): {
  state: StateSchema;
  input: StateSchema;
  output: StateSchema;
};
```

合并内置状态、用户自定义状态和 middleware 状态，生成三个 StateSchema：
- **state**：完整状态，包含 `messages: MessagesValue` 和所有字段（含私有）
- **input**：输入通道，仅非私有字段
- **output**：输出通道，仅非私有字段，有结构化响应时含 `structuredResponse: UntrackedValue`

### 内置状态字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `messages` | `MessagesValue` | 消息列表，使用消息 reducer 自动追加 |
| `jumpTo` | `UntrackedValue<JumpToTarget>` | 瞬态控制流信号，不持久化 |
| `structuredResponse` | `UntrackedValue` | 结构化输出（仅 responseFormat 存在时） |

### Schema 处理规则

- **StateSchema 实例**：直接遍历 `.fields`，识别 `ReducedValue` 的 inputSchema/valueSchema
- **Zod v3/v4 对象**：通过 `getInteropZodObjectShape` 提取 shape；Zod v4 支持 `schemaMetaRegistry` 中的 reducer 元数据，自动包装为 `ReducedValue`
- **下划线前缀字段**（如 `_internal`）：持久化在 state 中但不暴露为 input/output 通道

### 关键 LangGraph 类型

从 `@langchain/langgraph` 导入：
- `StateSchema` — 状态定义类
- `MessagesValue` — 消息列表 reducer
- `ReducedValue` — 带自定义 reducer 的字段
- `UntrackedValue` — 不参与快照/检查点的瞬态字段
- `StateGraph` — 状态图构建器
- `Command` — 状态更新命令
- `Send` — 映射到特定节点的命令
- `START` / `END` — 图入口/出口常量

## 相关文档

- [Runnable 核心 API](/langchain-ai/langchainjs/references/core-runnable) — Runnable 抽象参考
- [消息与工具 API](/langchain-ai/langchainjs/references/messages-tools) — Message 与 Tool 参考
- [ReAct Agent 概念](/langchain-ai/langchainjs/concepts/react-agent) — Agent 设计理念
- [Middleware 概念](/langchain-ai/langchainjs/concepts/middleware) — 中间件系统
