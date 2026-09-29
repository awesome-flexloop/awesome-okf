---
type: concept
scope: langchainjs
name: overview
version: "0.1.0"
source: https://github.com/langchain-ai/langchainjs
description: LangChain.js 总览——TypeScript LLM 应用框架的核心架构与组件生态
---

# LangChain.js 总览

## 什么是 LangChain.js

LangChain.js 是 LangChain 框架的 TypeScript/JavaScript 实现，用于构建基于大语言模型（LLM）的应用。它提供标准化的抽象接口，使开发者能够将模型、提示模板、工具、向量存储、Agent 等组件组合为可互操作的流水线。

- **仓库**：https://github.com/langchain-ai/langchainjs
- **核心包**：`@langchain/core`（`libs/langchain-core/`）
- **主包**：`langchain`（`libs/langchain/`，含 Agent、Prompt 编排等）
- **Monorepo 管理**：pnpm workspaces + Turborepo
- **TypeScript 目标**：ES2022，ESNext 模块，strict 模式

## 支持的运行环境

LangChain.js 设计为同构（isomorphic）库，支持：

- Node.js 20.x / 22.x / 24.x
- Cloudflare Workers
- Vercel / Next.js（Browser、Serverless、Edge Functions）
- Supabase Edge Functions
- 浏览器、Deno、Bun

## 核心架构分层

LangChain.js 的架构分为三个层次：

```
┌─────────────────────────────────────────────────┐
│  langchain（主包）                                │
│  ReactAgent · createAgent · Middleware · Prompts │
├─────────────────────────────────────────────────┤
│  @langchain/core（核心抽象）                      │
│  Runnable · Messages · Tools · Prompts           │
│  Documents · Callbacks · OutputParsers · Embeddings│
├─────────────────────────────────────────────────┤
│  集成包（@langchain/openai, @langchain/anthropic…）│
│  具体模型 Provider、向量存储、文档加载器           │
└─────────────────────────────────────────────────┘
```

### @langchain/core

核心抽象层，定义了所有组件的标准接口。主要模块：

| 模块 | 核心抽象 | 说明 |
|---|---|---|
| Runnable | `Runnable` 类 | 一切组件的统一执行接口 |
| Messages | `BaseMessage` 类族 | 对话消息类型系统 |
| Tools | `StructuredTool` 类 | 工具定义与调用 |
| Prompts | `BasePromptTemplate` 类 | 提示模板 |
| Documents | `Document` 类 | 文本文档与元数据 |
| Embeddings | `Embeddings` 抽象类 | 文本向量化 |
| Callbacks | `BaseCallbackHandler` | 生命周期事件钩子 |
| Output Parsers | `BaseOutputParser` 类 | LLM 输出解析 |
| Serializable | `Serializable` 类 | 跨语言序列化协议 |

### langchain（主包）

在核心抽象之上提供高层编排能力：

| 模块 | 核心 API | 说明 |
|---|---|---|
| ReactAgent | `createAgent()` | 生产级 ReAct Agent |
| Middleware | `createMiddleware()` | Agent 横切扩展系统 |
| Chat Models | 通用聊天模型封装 | 统一模型接口 |

## 设计哲学

### 1. Runnable 统一一切

所有核心组件——LLM、Chat Model、Prompt Template、Output Parser、Tool、Retriever——都继承自 `Runnable`。这意味着它们共享同一套执行接口（`invoke`/`batch`/`stream`）和组合子（`pipe`/`withRetry`/`withFallbacks`）。详见 Runnable 接口。

### 2. 组合优于继承

通过 `RunnableSequence`（`pipe`）和 `RunnableMap`（`RunnableParallel`），组件以函数式管道组合，而非深层继承树。LCEL（LangChain Expression Language）表达式 `prompt.pipe(model).pipe(parser)` 自动获得流式、批处理和追踪能力。

### 3. 跨语言序列化

`Serializable` 基类通过 `lc_namespace` + `lc_name` 构成全限定 ID，`lc_secrets` 保护敏感字段，`lc_aliases` 处理 JS/Python 命名差异，实现与 Python LangChain 的序列化格式互通。

### 4. Schema 双轨制

工具同时支持 Zod（运行时校验 + 类型推断 + transform）和 JSON Schema（跨平台、动态场景），通过 `InteropZodType` 和 `JSONSchema` 统一抽象。

## 典型应用模式

### LCEL 管道

```typescript
import { PromptTemplate } from "@langchain/core/prompts";
import { StringOutputParser } from "@langchain/core/output_parsers";

const chain = PromptTemplate.fromTemplate("讲一个关于{topic}的笑话")
  .pipe(model)
  .pipe(new StringOutputParser());

const result = await chain.invoke({ topic: "猫" });
```

### ReAct Agent

```typescript
import { createAgent, tool } from "langchain";

const search = tool(({ query }) => `搜索结果: ${query}`, {
  name: "search",
  description: "搜索网络",
  schema: z.object({ query: z.string() }),
});

const agent = createAgent({
  model: "openai:gpt-4o",
  tools: [search],
  systemPrompt: "你是一个有帮助的助手",
});

await agent.invoke({
  messages: [{ role: "user", content: "LangChain 是什么？" }],
});
```

## 文档导航

### 核心概念

- Runnable 接口 — 统一执行抽象与组合子
- 消息系统 — Message 类型层次与 tool_call
- 工具定义 — StructuredTool 与 tool 工厂
- 提示模板 — PromptTemplate 与 ChatPromptTemplate
- ReAct Agent — createAgent 与图编排
- Middleware — Agent 横切扩展
- Document 与 Embedding — 文档与向量化

### API 参考

- Runnable 核心 API
- Message 与 Tool API
- Agent 与 Middleware API

### 使用示例

- 构建 LCEL 链 — Prompt → Model → Parser 管道
- 创建 ReAct Agent — 工具调用 Agent 完整示例
