---
type: bundle
okf_version: "0.2"
scope: langchainjs
name: langchainjs
version: "0.1.0"
source: https://github.com/langchain-ai/langchainjs
description: LangChain.js——TypeScript LLM 应用框架，提供 Runnable 统一抽象、消息/工具/提示模板核心组件与基于 LangGraph 的 ReAct Agent 编排
---

# LangChain.js

**LangChain.js** 是 LangChain 框架的 TypeScript/JavaScript 实现，用于构建基于大语言模型（LLM）的应用。它以 `Runnable` 为统一执行抽象，将模型、提示模板、工具、输出解析器、Agent 等组件组合为可流式、可批处理、可追踪的管道，并在主包中提供基于 LangGraph StateGraph 的生产级 ReAct Agent 与 Middleware 横切扩展系统。

- **仓库**：https://github.com/langchain-ai/langchainjs
- **核心包**：`@langchain/core`（`libs/langchain-core/`）
- **主包**：`langchain`（`libs/langchain/`）
- **Monorepo**：pnpm workspaces + Turborepo
- **TypeScript**：target ES2022，ESNext 模块，strict 模式
- **运行环境**：Node.js 20/22/24、Cloudflare Workers、Vercel/Next.js、Bun、Deno、浏览器

## 核心特性

- **Runnable 统一抽象**：所有组件实现 `invoke`/`batch`/`stream`/`transform` 四维执行接口，通过 `pipe` 组合为 LCEL 管道，自动获得流式、批处理、重试、回退和回调追踪。
- **强类型消息系统**：`HumanMessage`/`SystemMessage`/`AIMessage`/`ToolMessage` 类型层次，`tool_calls` 作为 AIMessage 一等字段，`ToolMessage.tool_call_id` 建立请求-响应关联，支持多模态 ContentBlock。
- **双轨 Schema 工具**：`StructuredTool` 同时支持 Zod（类型推断 + transform）和 JSON Schema，`tool()` 工厂根据 schema 类型自动选择 `DynamicTool` 或 `DynamicStructuredTool`，条件返回类型自动包装 ToolMessage。
- **ReAct Agent 图编排**：`createAgent` 编译为 LangGraph `StateGraph`，核心 AgentNode/ToolNode 条件边形成 ReAct 循环，支持状态持久化、检查点和流式传输。
- **Middleware 横切扩展**：六个钩子（beforeAgent/beforeModel/afterModel/afterAgent/wrapModelCall/wrapToolCall）织入为图节点，afterModel 逆序执行形成洋葱模型，内置 20+ 生产级中间件。
- **跨语言序列化**：`Serializable` 基类通过 `lc_namespace`/`lc_name`/`lc_secrets`/`lc_aliases` 实现与 Python LangChain 的序列化互通。

## 快速开始

```typescript
import { createAgent, tool } from "langchain";
import { z } from "zod";

const search = tool(
  async ({ query }) => `搜索结果: ${query}`,
  {
    name: "search",
    description: "搜索网络",
    schema: z.object({ query: z.string() }),
  }
);

const agent = createAgent({
  model: "openai:gpt-4o",
  tools: [search],
  systemPrompt: "你是一个有帮助的助手",
});

const result = await agent.invoke({
  messages: [{ role: "user", content: "LangChain 是什么？" }],
});
```

## LCEL 管道示例

```typescript
import { PromptTemplate } from "@langchain/core/prompts";
import { StringOutputParser } from "@langchain/core/output_parsers";

const chain = PromptTemplate.fromTemplate("讲一个关于{topic}的笑话")
  .pipe(model)
  .pipe(new StringOutputParser());

const stream = await chain.stream({ topic: "猫" });
for await (const chunk of stream) {
  process.stdout.write(chunk);
}
```

## 文档导航

### 核心概念

- [总览](/ai/langchain-ai/langchainjs/concepts/overview) — 架构分层、设计哲学与组件生态
- [Runnable 接口](/ai/langchain-ai/langchainjs/concepts/runnable-interface) — 统一执行抽象、四维调用模型与 LCEL 组合子
- [消息系统](/ai/langchain-ai/langchainjs/concepts/message-system) — BaseMessage 类型层次、tool_call 与多模态内容
- [工具定义](/ai/langchain-ai/langchainjs/concepts/tool-definition) — StructuredTool、Zod/JSON Schema 与 tool 工厂
- [提示模板](/ai/langchain-ai/langchainjs/concepts/prompt-templates) — PromptTemplate、ChatPromptTemplate 与 MessagesPlaceholder
- [ReAct Agent](/ai/langchain-ai/langchainjs/concepts/react-agent) — createAgent、图拓扑、状态管理与结构化输出
- [Middleware](/ai/langchain-ai/langchainjs/concepts/middleware) — 六钩子织入、洋葱模型与内置中间件
- [Document 与 Embedding](/ai/langchain-ai/langchainjs/concepts/document-embedding) — 文档数据模型、向量化抽象与 RAG 基础

### API 参考

- [Runnable 核心 API](/ai/langchain-ai/langchainjs/references/core-runnable) — Runnable 类、RunnableConfig、内置 Runnable 实现与 Graph
- [Message 与 Tool API](/ai/langchain-ai/langchainjs/references/messages-tools) — 消息类型、ToolCall、StructuredTool 与 tool 工厂
- [Agent 与 Middleware API](/ai/langchain-ai/langchainjs/references/agents-middleware) — createAgent、ReactAgent、AgentMiddleware 与状态注解

### 使用示例

- [构建 LCEL 链](/ai/langchain-ai/langchainjs/examples/lcel-chain) — Prompt → Model → Parser 管道与流式/批量/并行
- [创建 ReAct Agent](/ai/langchain-ai/langchainjs/examples/react-agent) — 工具、Middleware、结构化输出与流式传输

### 规格文档

- [事实清单](/ai/langchain-ai/langchainjs/spec/facts) — 109 条从源码提取的可验证事实
- [架构洞察](/ai/langchain-ai/langchainjs/spec/insights) — 5 个核心设计决策与机制分析

## 目录结构

```
langchainjs/
├── spec/
│   ├── facts.md           # 源码事实验证清单（109 条）
│   └── insights.md        # 设计决策与深度洞察（5 篇）
├── concepts/              # 核心概念（8 篇）
│   ├── overview.md
│   ├── runnable-interface.md
│   ├── message-system.md
│   ├── tool-definition.md
│   ├── prompt-templates.md
│   ├── react-agent.md
│   ├── middleware.md
│   └── document-embedding.md
├── references/            # API 参考（3 篇）
│   ├── core-runnable.md
│   ├── messages-tools.md
│   └── agents-middleware.md
├── examples/              # 使用示例（2 篇）
│   ├── lcel-chain.md
│   └── react-agent.md
└── index.md               # 本文件
```

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
