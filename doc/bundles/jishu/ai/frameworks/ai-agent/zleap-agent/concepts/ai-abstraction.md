---
type: Concept
title: AI 抽象层
description: "@zleap/ai 包的 ProviderAdapter 统一接口、ProviderCapabilities 能力声明、AssistantStreamEvent 流式事件模型、Anthropic/OpenAI 兼容双 Provider 实现、SSE 流式解析、Embeddings 向量化与 Faux 降级嵌入。"
tags: [zleap-agent, ai, provider, llm, anthropic, openai, sse, streaming, embeddings, rag]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T12:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: ai-types
    resource: ../../../../../../external/libs/models/ai/Zleap-Agent/packages/ai/src/types.ts
    title: "@zleap/ai 类型系统"
  - id: ai-anthropic
    resource: ../../../../../../external/libs/models/ai/Zleap-Agent/packages/ai/src/providers/anthropic.ts
    title: Anthropic Provider
  - id: ai-openai
    resource: ../../../../../../external/libs/models/ai/Zleap-Agent/packages/ai/src/providers/openai-compatible.ts
    title: OpenAI Compatible Provider
  - id: ai-sse
    resource: ../../../../../../external/libs/models/ai/Zleap-Agent/packages/ai/src/providers/sse.ts
    title: SSE 流式解析
  - id: ai-embeddings
    resource: ../../../../../../external/libs/models/ai/Zleap-Agent/packages/ai/src/embeddings.ts
    title: Embeddings 向量化
  - id: ai-registry
    resource: ../../../../../../external/libs/models/ai/Zleap-Agent/packages/ai/src/registry.ts
    title: Provider 注册中心
---

# AI 抽象层

@zleap/ai 是 Zleap-Agent 的 LLM Provider 抽象层，**零运行时外部依赖**（仅使用原生 fetch），通过统一的 `ProviderAdapter` 接口屏蔽不同 AI 服务商的 API 差异，向上层提供一致的流式推理、工具调用、思维链和缓存断点能力。该包与 @zleap/core 并列作为双基础层，互不依赖。

## 设计目标

1. **多 Provider 统一**：Anthropic Claude、OpenAI 及所有 OpenAI 兼容端点（DeepSeek/Qwen/GLM/302.AI 等）通过同一接口调用
2. **流式优先**：所有推理以 `AsyncIterable<AssistantStreamEvent>` 流式返回，支持逐 token 渲染
3. **能力声明**：每个 Provider 显式声明支持的能力（toolCalling/thinking/cacheBreakpoints/tokenizer），上层据此调整行为
4. **零依赖**：不引入任何 SDK，直接使用 fetch + SSE 解析，保持轻量
5. **降级容错**：Embeddings 提供 fauxEmbed 离线降级，Provider 响应支持录制/重放（测试用）

## 包结构

```
@zleap/ai
├── types.ts                    # 核心类型：ProviderAdapter、Message、StreamEvent
├── create.ts                   # Provider 工厂函数
├── registry.ts                 # Provider 注册中心
├── stream.ts                   # 统一流式事件处理
├── embeddings.ts               # 文本向量化 + fauxEmbed 降级
├── providerReplay.ts           # Provider 响应录制/重放
└── providers/
    ├── anthropic.ts            # Anthropic Messages API 原生适配
    ├── openai-compatible.ts    # OpenAI Chat Completions 兼容适配
    └── sse.ts                  # Server-Sent Events 解析器
```

## ProviderAdapter 统一接口

所有 AI Provider 实现 `ProviderAdapter` 接口：

```typescript
// types.ts L147-L155
export interface ProviderAdapter {
  id: string;
  capabilities: ProviderCapabilities;
  stream(
    model: Model,
    request: ProviderRequest,
    options?: ProviderOptions,
  ): AsyncIterable<AssistantStreamEvent>;
}
```

接口极简——一个 `id` 标识、一个 `capabilities` 能力声明、一个 `stream()` 方法。所有推理都是流式的，上层如需完整响应可消费整个 AsyncIterable 后聚合。

### ProviderCapabilities 能力声明

```typescript
// types.ts L83-L94
export type ProviderCapabilities = {
  toolCalling: boolean;        // 是否支持原生 function calling / tool use
  cacheBreakpoints: boolean;   // 是否支持 prompt caching 断点（Anthropic）
  thinking: boolean;           // 是否支持 extended thinking / reasoning
  tokenizer: string;           // 分词器标识（用于 token 预算）
  maxOutputTokens?: number;    // Provider 级输出上限
};
```

能力声明使得上层可以根据 Provider 特性动态调整策略：不支持 toolCalling 的 Provider 可能需要 ReAct 提示词模式；不支持 thinking 的 Provider 跳过思维链相关逻辑。

### Model 模型配置

```typescript
// types.ts L68-L81
export type Model = {
  id: string;
  provider: string;           // Provider ID，如 'anthropic'、'openai'
  model: string;              // 模型名，如 'claude-sonnet-4-20250514'
  baseUrl?: string;           // API 基础 URL
  apiKey?: string;            // API 密钥
  displayName?: string;       // UI 显示名
  contextWindow?: number;     // 上下文窗口大小
  maxOutputTokens?: number;   // 最大输出 token
  supportsTools?: boolean;    // 模型级工具调用覆盖
  supportsThinking?: boolean; // 模型级思维链覆盖
  supportsCache?: boolean;    // 模型级缓存覆盖
  tokenizer?: string;         // 分词器覆盖
};
```

### ProviderRequest 请求结构

```typescript
// types.ts L105-L119
export type ProviderRequest = {
  systemPrompt: string;                          // 系统提示词
  messages: Message[];                           // 对话消息列表
  tools?: ToolSchema[];                          // 可用工具 schema
  cacheBreakpoints?: ProviderCacheBreakpoint[];   // 缓存断点（Anthropic）
};

export type ProviderOptions = {
  signal?: AbortSignal;          // 取消信号
  temperature?: number;          // 温度参数
  maxOutputTokens?: number;      // 最大输出 token
  apiKey?: string;               // 覆盖 API Key
  baseUrl?: string;              // 覆盖 Base URL
  metadata?: Record<string, unknown>;
};
```

## 消息类型系统

AI 层定义了三种消息角色和四种内容块类型：

```typescript
// types.ts L1-L54
export type MessageRole = 'user' | 'assistant' | 'toolResult';

// 内容块类型
export type TextContent = { type: 'text'; text: string };
export type ThinkingContent = { type: 'thinking'; text: string; signature?: string };
export type ToolCallContent = { type: 'toolCall'; id: string; name: string; arguments: unknown };
export type ImageContent = { type: 'image'; mimeType: 'image/png'|'image/jpeg'|'image/webp'; data: string };

export type MessageContent = TextContent | ThinkingContent | ToolCallContent | ImageContent;

// 三种消息
export type UserMessage = {
  id?: string;
  role: 'user';
  content: string | MessageContent[];    // 支持纯文本或多模态内容块
};

export type AssistantMessage = {
  id?: string;
  role: 'assistant';
  content: MessageContent[];
  usage?: Usage;
  status?: 'completed' | 'error' | 'aborted';
};

export type ToolResultMessage = {
  id?: string;
  role: 'toolResult';
  toolCallId: string;       // 关联的 toolCall ID
  toolName: string;
  content: string;          // 工具执行结果（字符串）
  isError?: boolean;
  details?: unknown;
};

export type Message = UserMessage | AssistantMessage | ToolResultMessage;
```

AssistantMessage 的 content 始终是数组——模型的输出可能包含文本、思维链和多个工具调用的混合。UserMessage 的 content 可以是简单字符串或多模态内容块数组。

## 流式事件模型

`AssistantStreamEvent` 是 AI 层流式输出的统一事件协议，所有 Provider 将各自的 SSE 事件转换为此模型：

```typescript
// types.ts L121-L145
export type AssistantStreamEvent =
  // 文本事件
  | { type: 'text_start'; id: string }
  | { type: 'text_delta'; id: string; text: string }
  | { type: 'text_end'; id: string }
  // 思维链事件
  | { type: 'thinking_start'; id: string }
  | { type: 'thinking_delta'; id: string; text: string }
  | { type: 'thinking_end'; id: string }
  // 工具调用事件
  | { type: 'toolcall_start'; id: string; name: string }
  | { type: 'toolcall_delta'; id: string; argumentsText: string }
  | {
      type: 'toolcall_end';
      id: string;
      name: string;
      arguments: unknown;
      rawArguments?: string;
      argumentsParseError?: string;
    }
  // 终止事件
  | { type: 'done'; usage?: Usage; finishReason?: string }
  | { type: 'error'; error: ProviderError };
```

### 事件序列约束

流式事件遵循严格的序列约定：

```
text_start → text_delta* → text_end
thinking_start → thinking_delta* → thinking_end
toolcall_start → toolcall_delta* → toolcall_end

（以上三类事件块可交错出现）
→ done | error
```

每个内容块（文本/思维/工具调用）有独立的 `id`，允许多个同类型块并行输出（如一个文本块后跟两个并行工具调用块）。

### ToolCall 增量聚合

工具调用的参数以 JSON 字符串增量方式流式到达（`toolcall_delta.argumentsText`），在 `toolcall_end` 时尝试 JSON.parse，解析失败时设置 `argumentsParseError` 并保留 `rawArguments` 供上层恢复：

```typescript
// toolcall_end 事件包含解析后的 arguments 和可能的 parseError
{
  type: 'toolcall_end',
  id: 'toolu_xxx',
  name: 'bash',
  arguments: { command: 'ls -la' },   // 成功解析
  rawArguments?: '{"command": "ls -la"}',
  argumentsParseError?: string         // 解析失败时设置
}
```

## Anthropic Provider

`AnthropicProvider` 直接对接 Anthropic Messages API（非 OpenAI 兼容中转），使用原生 wire format 确保工具名称和 tool_use 可靠性：

```typescript
// providers/anthropic.ts L27-L40
export class AnthropicProvider implements ProviderAdapter {
  id = ANTHROPIC_PROVIDER_ID;  // 'anthropic'
  capabilities = {
    toolCalling: true,
    cacheBreakpoints: true,    // Anthropic 独有的 prompt caching
    thinking: true,            // extended thinking
    tokenizer: 'anthropic',
  };

  async *stream(
    model: Model,
    request: ProviderRequest,
    options?: ProviderOptions,
  ): AsyncIterable<AssistantStreamEvent> {
    // 直接 POST 到 Anthropic /v1/messages，stream: true
    // 通过 sseChunks() 解析 SSE，转换为 AssistantStreamEvent
  }
}
```

### Anthropic SSE 事件映射

| Anthropic SSE 事件 | AssistantStreamEvent |
|-------------------|---------------------|
| `message_start` | 记录 usage（input/output tokens） |
| `content_block_start` (type=text) | `text_start` |
| `content_block_start` (type=thinking) | `thinking_start` |
| `content_block_start` (type=tool_use) | `toolcall_start` |
| `content_block_delta` (text_delta) | `text_delta` |
| `content_block_delta` (thinking_delta) | `thinking_delta` |
| `content_block_delta` (input_json_delta) | `toolcall_delta` |
| `content_block_stop` | `text_end` / `thinking_end` / `toolcall_end` |
| `message_delta` (stop_reason) | 记录 finishReason |
| `message_stop` | `done` |

### 关键适配逻辑

```typescript
// providers/anthropic.ts L48-L51 — 工具格式转换
const tools = request.tools && request.tools.length > 0
  ? request.tools.map((tool) => ({
      name: tool.name,
      description: tool.description,
      input_schema: tool.parameters  // Anthropic 使用 input_schema 而非 parameters
    }))
  : undefined;
```

Anthropic 的系统提示是顶层 `system` 字段（非消息列表中的 role=system 消息），`toAnthropicSystem()` 从 ProviderRequest 中提取。工具结果以 `tool_result` content block 类型传递。

### 缓存断点支持

Anthropic Provider 支持 `cacheBreakpoints`，将其转换为 Anthropic 的 `cache_control` 字段，实现 prompt caching 以降低成本和延迟：

```typescript
// cacheBreakpoints 在 toAnthropicMessages 中转换为
// { type: 'text', text: '...', cache_control: { type: 'ephemeral' } }
```

## OpenAI Compatible Provider

`providers/openai-compatible.ts` 适配 OpenAI Chat Completions API 格式，覆盖所有兼容服务（OpenAI 自身、DeepSeek、通义千问、智谱、302.AI 等）。该 Provider 将 OpenAI 的 SSE 格式（`data: {"choices":[{"delta":...}]}`）转换为统一的 AssistantStreamEvent。

### 格式差异处理

| 差异点 | OpenAI 格式 | Zleap 统一格式 |
|--------|-----------|---------------|
| 系统提示 | messages 中 role=system | ProviderRequest.systemPrompt |
| 工具调用 | `tool_calls[{id,type:"function",function:{name,arguments}}]` | ToolCallContent |
| 工具结果 | role=tool, tool_call_id, content | ToolResultMessage |
| 流结束 | `data: [DONE]` | `{type: 'done'}` |
| 思维链 | `reasoning_content` 字段（部分兼容模型） | ThinkingContent |

## SSE 流式解析

`providers/sse.ts` 实现了零依赖的 Server-Sent Events 解析器 `sseChunks()`：

```typescript
// providers/sse.ts
export async function* sseChunks(
  body: ReadableStream<Uint8Array>
): AsyncIterable<string> {
  // 读取 ReadableStream，按 SSE 协议解析
  // 按 \n\n 分割事件块，提取 data: 行
  // 处理 [DONE] 终止标记
  // 正确处理 UTF-8 多字节字符和跨 chunk 的事件拼接
}
```

SSE 解析器处理以下边界情况：
- UTF-8 多字节字符跨 chunk 分割（使用 TextDecoder 的 `stream: true` 选项）
- 事件字段跨多个 chunk（缓冲区拼接）
- `data: [DONE]` 终止标记
- 注释行（以 `:` 开头的行）

## Embeddings 向量化

`embeddings.ts` 提供文本向量化能力，用于记忆的向量存储和语义检索。

### OpenAI 兼容 Embeddings

```typescript
// embeddings.ts L30-L58
export async function embed(request: EmbedRequest): Promise<EmbedResult> {
  // POST 到 {baseUrl}/embeddings
  // body: { model, input: string[] }
  // 返回 { embeddings: number[][], model }
}
```

支持批量文本输入（`input: string[]`），返回等长的向量数组。结果按 `index` 字段排序确保顺序一致。

### FauxEmbed 离线降级

当无 Embedding API 可用时（测试环境、无 pgvector 的开发模式），`fauxEmbed()` 提供确定性的离线向量：

```typescript
// embeddings.ts L65-L78
export function fauxEmbed(text: string, dim = 64): number[] {
  const vector = new Array<number>(dim).fill(0);
  const tokens = text.toLowerCase().match(/[\p{L}\p{N}]+/gu) ?? [];
  for (const token of tokens) {
    // FNV-1a 哈希 → 桶位置 → 计数
    let hash = 2166136261;
    for (let i = 0; i < token.length; i += 1) {
      hash ^= token.charCodeAt(i);
      hash = Math.imul(hash, 16777619);
    }
    const bucket = Math.abs(hash) % dim;
    vector[bucket] += 1;
  }
  return l2normalize(vector);  // L2 归一化
}
```

fauxEmbed 使用 FNV-1a 哈希将 token 映射到 `dim` 个桶中，然后 L2 归一化。相似文本因共享 token 而具有相似的桶分布，余弦相似度具有区分度，足以在开发/测试环境中验证记忆召回流程。默认维度 64（区别于真实 embedding 的 1536 维）。

### 向量工具

```typescript
// embeddings.ts L80-L109
export function l2normalize(vector: number[]): number[];           // L2 归一化
export function cosineSimilarity(a: number[], b: number[]): number; // 余弦相似度
```

## Provider 注册与创建

### ProviderRegistry

`registry.ts` 管理 Provider 的注册和查找，支持运行时动态注册自定义 Provider：

```typescript
// 注册表存储已注册的 ProviderAdapter 工厂
export class ProviderRegistry {
  register(id: string, factory: ProviderFactory): void;
  get(id: string): ProviderAdapter | undefined;
  list(): string[];
}
```

### createProvider 工厂

`create.ts` 提供便捷的 Provider 创建入口，根据 model.provider 自动选择并实例化对应 Provider：

```typescript
export function createProvider(model: Model, options?: ProviderOptions): ProviderAdapter;
```

## Provider Replay（测试录制/重放）

`providerReplay.ts` 支持 Provider 响应的录制和重放，用于单元测试和回归测试：

- **录制模式**：将真实 Provider 的流式事件序列记录为 JSON
- **重放模式**：从录制数据重放 AssistantStreamEvent 序列，无需实际 API 调用

这使得上层逻辑（Turn Loop、工具调用、记忆）的测试可以在无网络、无 API Key 的环境中运行。

## 与上层的集成

ChatEngine（@zleap/agent）在初始化时根据用户配置的 model 创建 ProviderAdapter，并在 Turn Loop 中调用 `provider.stream()` 执行推理：

```
ChatEngine
  ├─ createProvider(model) → ProviderAdapter
  ├─ 组装 ProviderRequest（systemPrompt + messages + tools）
  ├─ for await (const event of provider.stream(model, request, options))
  │   ├─ text_delta → 累积 assistant 文本 → emit workspace_delta
  │   ├─ toolcall_end → 执行工具 → 添加 ToolResultMessage
  │   └─ done → 检查 finishReason
  └─ 循环直到模型产出最终文本（无更多工具调用）
```

### Usage 统计

每个 `done` 事件携带 Usage 信息：

```typescript
// types.ts L96-L103
export type Usage = {
  inputTokens?: number;
  outputTokens?: number;
  cacheReadTokens?: number;   // 缓存命��的 token（Anthropic prompt caching）
  cacheWriteTokens?: number;  // 缓存写入的 token
  totalTokens?: number;
  costUsd?: number;           // 估算成本（USD）
};
```

Usage 信息通过 TurnLifecycleDelta 和 ProviderLifecycleDelta 传递到 UI 层，用于展示 token 消耗和成本估算。

## 默认配置常量

```typescript
// host/src/constants.ts
DEFAULT_EMBED_DIM = '1536';   // OpenAI text-embedding-ada-002 维度
```

pgvector 的向量维度必须与 embedder 输出维度一致，默认 1536 对应 OpenAI ada-002。使用 fauxEmbed 时维度为 64，此时 PgStore 以 faux 模式运行（实际相似度计算仍有效，但精度较低）。

## 相关概念

- [Agent 编排引擎](agent-orchestration.md) — ChatEngine 如何使用 ProviderAdapter 执行 Turn Loop
- [Fiber 执行生命周期](fiber-lifecycle.md) — Fiber 运行时中的工具调用流程
- [状态持久化存储](store-persistence.md) — PgStore 如何使用 Embeddings 实现向量召回
- [Gateway 网关服务](gateway-server.md) — Gateway 如何解析模型配置并创建 Provider
