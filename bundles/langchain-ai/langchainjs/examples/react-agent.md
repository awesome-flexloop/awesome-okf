---
type: example
scope: langchainjs
name: react-agent
version: "0.1.0"
source: https://github.com/langchain-ai/langchainjs
description: 创建 ReAct Agent——使用 createAgent、tool、createMiddleware 构建带工具和中间件的智能体
---

# 创建 ReAct Agent

本示例演示如何使用 LangChain.js 的 `createAgent` 工厂构建一个生产级 ReAct Agent，包括工具定义、中间件、结构化输出和流式传输。

## 前置条件

```bash
npm install langchain @langchain/core @langchain/openai zod
```

设置 OpenAI API Key：

```bash
export OPENAI_API_KEY="sk-..."
```

## 基础 Agent

```typescript
import { createAgent, tool } from "langchain";
import { z } from "zod";

// 1. 定义工具
const search = tool(
  async ({ query }) => {
    // 实际场景中调用搜索 API
    return `关于"${query}"的搜索结果：LangChain 是一个 LLM 应用框架。`;
  },
  {
    name: "search",
    description: "搜索网络获取信息",
    schema: z.object({
      query: z.string().describe("搜索关键词"),
    }),
  }
);

const calculator = tool(
  async ({ expression }) => {
    // 安全的数学表达式求值（示例）
    const result = Function('"use strict";return (' + expression + ")")();
    return String(result);
  },
  {
    name: "calculator",
    description: "计算数学表达式",
    schema: z.object({
      expression: z.string().describe("数学表达式，如 2+3*4"),
    }),
  }
);

// 2. 创建 Agent
const agent = createAgent({
  model: "openai:gpt-4o-mini",
  tools: [search, calculator],
  systemPrompt: "你是一个有帮助的研究助手，可以搜索信息和进行计算。",
});

// 3. 调用
const result = await agent.invoke({
  messages: [
    { role: "user", content: "LangChain 是什么？然后计算 123*456" },
  ],
});

console.log(result.messages[result.messages.length - 1].content);
```

### Agent 内部发生了什么

1. AgentNode 将系统提示、用户消息和工具定义发送给模型
2. 模型返回 AIMessage，包含 `tool_calls`（可能同时调用 search 和 calculator）
3. ToolNode 并行执行工具，生成对应的 ToolMessage（含 `tool_call_id`）
4. 工具结果作为消息追加到对话，回到 AgentNode
5. 模型根据工具结果生成最终回答（无 tool_calls），循环结束

## 带状态的 Agent

使用 `stateSchema` 添加自定义状态：

```typescript
import { StateSchema, ReducedValue } from "@langchain/langgraph";

const AgentState = new StateSchema({
  // 普通字段
  userId: z.string(),
  // 带 reducer 的字段：输入是 string，状态是 string[]
  searchHistory: new ReducedValue(
    z.array(z.string()).default([]),
    {
      inputSchema: z.string(),
      reducer: (current, next) => [...current, next],
    }
  ),
  queryCount: z.number().default(0),
});

const countingAgent = createAgent({
  model: "openai:gpt-4o-mini",
  tools: [search],
  stateSchema: AgentState,
});

const result = await countingAgent.invoke({
  messages: [{ role: "user", content: "搜索 LangChain" }],
  userId: "user-123",
  queryCount: 0,
});
```

## 使用 Middleware

### 工具调用次数限制

```typescript
import { toolCallLimitMiddleware } from "langchain/agents";

const limitedAgent = createAgent({
  model: "openai:gpt-4o-mini",
  tools: [search, calculator],
  middleware: [
    toolCallLimitMiddleware({ maxCalls: 5 }),
  ],
});
```

### 自定义 Middleware

```typescript
import { createMiddleware } from "langchain/agents";

const loggingMiddleware = createMiddleware({
  name: "LoggingMiddleware",
  beforeModel: async (state, runtime) => {
    console.log(`[${new Date().toISOString()}] 模型调用 #${state.messages.length}`);
  },
  afterModel: async (state, runtime) => {
    const lastMessage = state.messages[state.messages.length - 1];
    if (lastMessage._getType() === "ai") {
      const aiMessage = lastMessage as AIMessage;
      if (aiMessage.tool_calls?.length) {
        console.log(`模型决定调用: ${aiMessage.tool_calls.map(t => t.name).join(", ")}`);
      }
    }
  },
});

const agentWithLogging = createAgent({
  model: "openai:gpt-4o-mini",
  tools: [search],
  middleware: [loggingMiddleware],
});
```

### 动态系统提示

```typescript
import { dynamicSystemPromptMiddleware } from "langchain/agents";

const agent = createAgent({
  model: "openai:gpt-4o-mini",
  tools: [search],
  middleware: [
    dynamicSystemPromptMiddleware(async (state) => {
      return `当前时间: ${new Date().toLocaleString("zh-CN")}\n用户ID: ${state.configurable?.userId ?? "unknown"}`;
    }),
  ],
});
```

### Middleware 注册工具

Middleware 可以提供自己的工具，对模型透明可用：

```typescript
const middlewareWithTools = createMiddleware({
  name: "MathTools",
  tools: [calculator],
  beforeModel: async (state) => {
    // 可以在模型调用前做预处理
  },
});

const agent = createAgent({
  model: "openai:gpt-4o-mini",
  tools: [search],  // 用户工具
  middleware: [middlewareWithTools],  // middleware 工具自动合并
});
// Agent 实际拥有 search + calculator 两个工具
```

## 结构化输出

使用 Zod schema 获取类型化响应：

```typescript
const ResearchResult = z.object({
  summary: z.string().describe("研究摘要"),
  keyPoints: z.array(z.string()).describe("关键要点列表"),
  confidence: z.number().min(0).max(1).describe("置信度 0-1"),
});

const researchAgent = createAgent({
  model: "openai:gpt-4o",
  tools: [search],
  responseFormat: ResearchResult,
  systemPrompt: "你是一个研究员，搜索后输出结构化的研究结果。",
});

const result = await researchAgent.invoke({
  messages: [{ role: "user", content: "研究 RAG 的最新进展" }],
});

console.log(result.structuredResponse);
// {
//   summary: "...",
//   keyPoints: ["...", "..."],
//   confidence: 0.85
// }
```

## 流式传输

```typescript
const stream = await agent.stream(
  { messages: [{ role: "user", content: "搜索并计算：(100+200)*3" }] },
  { streamMode: "values" }
);

for await (const chunk of stream) {
  const lastMessage = chunk.messages[chunk.messages.length - 1];
  if (lastMessage._getType() === "ai") {
    if (lastMessage.tool_calls?.length) {
      console.log("🔧 调用工具:", lastMessage.tool_calls.map(t => t.name));
    } else if (lastMessage.content) {
      console.log("🤖", lastMessage.content);
    }
  } else if (lastMessage._getType() === "tool") {
    console.log("📎 工具结果:", String(lastMessage.content).slice(0, 100));
  }
}
```

### streamEvents 细粒度事件

```typescript
const eventStream = agent.streamEvents(
  { messages: [{ role: "user", content: "你好" }] },
  { version: "v2" }
);

for await (const event of eventStream) {
  if (event.event === "on_chat_model_stream") {
    process.stdout.write(event.data.chunk.content ?? "");
  }
}
```

## content_and_artifact 模式

工具可以同时返回给模型的内容和给程序的完整数据：

```typescript
const readDocument = tool(
  async ({ docId }, runtime) => {
    const fullText = await database.get(docId);
    const summary = fullText.slice(0, 500);
    return [summary, { docId, fullText }] as const;
  },
  {
    name: "read_document",
    description: "读取文档",
    schema: z.object({ docId: z.string() }),
    responseFormat: "content_and_artifact",
  }
);
```

## 关键 API 速查

| API | 说明 |
|---|---|
| `createAgent(params)` | 创建 ReactAgent，参数含 model/tools/systemPrompt/middleware/responseFormat/stateSchema |
| `tool(func, fields)` | 创建工具，func 为执行函数，fields 含 name/description/schema |
| `createMiddleware(config)` | 创建中间件，含 beforeAgent/beforeModel/afterModel/afterAgent/wrapModelCall/wrapToolCall |
| `agent.invoke(input)` | 单次调用，input 为 `{ messages: BaseMessageLike[] }` |
| `agent.stream(input, config)` | 流式调用 |
| `agent.streamEvents(input, config)` | 细粒度事件流 |
| `toolCallLimitMiddleware(config)` | 工具调用次数限制中间件 |
| `dynamicSystemPromptMiddleware(fn)` | 动态系统提示中间件 |
| `summarizationMiddleware(config)` | 上下文摘要中间件 |

## 相关文档

- [ReAct Agent 概念](/langchain-ai/langchainjs/concepts/react-agent)
- [Middleware 概念](/langchain-ai/langchainjs/concepts/middleware)
- [工具定义概念](/langchain-ai/langchainjs/concepts/tool-definition)
- [Agent 与 Middleware API](/langchain-ai/langchainjs/references/agents-middleware)
- [构建 LCEL 链示例](/langchain-ai/langchainjs/examples/lcel-chain)
