---
type: example
scope: deepagentsjs
name: basic-agent
version: "1.13.1"
source: https://github.com/langchain-ai/deepagentsjs
description: deepagentsjs 基础使用示例——创建 Agent、配置子代理、自定义中间件、文件系统后端、流式调用
---

# 基础 Agent 示例

本示例演示 deepagentsjs 的核心使用流程：从最简 agent 到带自定义工具、子代理和持久化的完整配置。

## 前置条件

```bash
npm install deepagents
npm install @langchain/core @langchain/langgraph @langchain/langgraph-checkpoint @langchain/langgraph-sdk langchain langsmith
```

Yarn 用户需显式安装 peer dependencies（npm 7+ 和 pnpm 8+ 自动安装）。

## 最简 Agent

使用全部默认值：Claude Sonnet 4.6 模型、StateBackend、通用子代理、文件系统工具。

```typescript
import { createDeepAgent } from "deepagents";

const agent = createDeepAgent();

const result = await agent.invoke({
  messages: [
    {
      role: "user",
      content: "研究 LangGraph 并将摘要写入 summary.md",
    },
  ],
});

console.log(result.messages[result.messages.length - 1].content);
```

agent 会自动规划任务、使用文件工具读写文件、在需要时委派给通用子代理。

## 自定义模型和工具

```typescript
import { ChatOpenAI } from "@langchain/openai";
import { tool } from "langchain";
import { z } from "zod";
import { createDeepAgent } from "deepagents";

const calculatorTool = tool(
  async ({ expression }: { expression: string }) => {
    try {
      const result = Function(`"use strict"; return (${expression})`)();
      return String(result);
    } catch {
      return "Error: invalid expression";
    }
  },
  {
    name: "calculator",
    description: "计算数学表达式",
    schema: z.object({
      expression: z.string().describe("要计算的数学表达式，如 '2 + 3 * 4'"),
    }),
  },
);

const agent = createDeepAgent({
  model: new ChatOpenAI({ model: "gpt-4o", temperature: 0 }),
  tools: [calculatorTool],
  systemPrompt: "你是一个有用的助手。",
});

const result = await agent.invoke({
  messages: [{ role: "user", content: "计算 (15 + 27) * 3 等于多少？" }],
});
```

## 配置子代理

### 声明式 SubAgent（handoff 模式）

```typescript
import { createDeepAgent, type SubAgent } from "deepagents";

const researcher: SubAgent = {
  name: "researcher",
  description: "研究助手，负责搜索网络和分析信息",
  systemPrompt: "你是一个专业的研究助手。彻底搜索后返回结构化报告。",
  tools: [webSearchTool],
  skills: ["/skills/research/"],
};

const writer: SubAgent = {
  name: "writer",
  description: "技术写作专家，将研究结果转化为清晰的文档",
  systemPrompt: "你是一个技术写作专家。根据提供的研究材料撰写文档。",
};

const agent = createDeepAgent({
  model: "anthropic:claude-sonnet-4-6",
  subagents: [researcher, writer],
});
```

主 agent 通过 `task` 工具委派任务，可在一条消息中并行调用多个子代理。

### ForkedSubAgent（继承父上下文）

```typescript
import type { ForkedSubAgent } from "deepagents";

const continuator: ForkedSubAgent = {
  name: "continuator",
  description: "继承当前对话上下文继续深入调查",
  mode: "fork",
  tools: [webSearchTool, readFileTool],
};
```

fork 模式子代理继承父代理完整消息历史，但不能有自己的 systemPrompt。

### AsyncSubAgent（远程服务器）

```typescript
import type { AsyncSubAgent } from "deepagents";

const remoteWorker: AsyncSubAgent = {
  name: "long-running-worker",
  description: "在远程服务器上执行长时间运行的数据处理任务",
  graphId: "data-processor",
  url: "https://langgraph-server.example.com",
  headers: { Authorization: `Bearer ${process.env.LANGGRAPH_API_KEY}` },
};

const agent = createDeepAgent({
  subagents: [remoteWorker],
});
```

异步子代理注入 `start_async_task`、`check_async_task` 等工具，主 agent 启动任务后立即返回，不阻塞。

## 使用文件系统后端

```typescript
import { createDeepAgent, FilesystemBackend } from "deepagents";

const agent = createDeepAgent({
  backend: new FilesystemBackend({ rootDir: "/home/user/agent-workspace" }),
  // 可选：配置权限
  permissions: [
    { operations: ["read"], paths: ["/workspace/**"] },
    { operations: ["write"], paths: ["/workspace/output/**"] },
    { operations: ["read", "write"], paths: ["/**"], mode: "deny" },
  ],
});
```

权限规则按声明顺序求值，首次匹配优先。子代理可指定自己的权限（完全替换父代理权限）。

## 启用规划（Todo）

```typescript
import { todoListMiddleware } from "langchain";
import { createDeepAgent } from "deepagents";

const agent = createDeepAgent({
  model: "openai:gpt-5.1-codex",  // Codex 模型自动启用 todoListMiddleware
  // 或手动为其他模型启用：
  // middleware: [todoListMiddleware()],
});
```

`write_todos` 工具让 agent 可以创建和跟踪任务列表。Codex harness profile（`openai:gpt-5.1-codex` 等）自动添加此中间件。

## 启用记忆和技能

```typescript
import { createDeepAgent, FilesystemBackend } from "deepagents";

const agent = createDeepAgent({
  backend: new FilesystemBackend({ rootDir: "/home/user/.deepagents" }),
  memory: [
    "~/.deepagents/AGENTS.md",
    "./.deepagents/AGENTS.md",
  ],
  skills: [
    "/skills/user/",
    "/skills/project/",
  ],
});
```

- **memory**：AGENTS.md 文件在启动时加载到 system prompt，提供持久上下文
- **skills**：SKILL.md 技能目录，支持渐进式披露

## 结构化输出

```typescript
import { z } from "zod";
import { createDeepAgent } from "deepagents";

const agent = createDeepAgent({
  model: "anthropic:claude-sonnet-4-6",
  responseFormat: z.object({
    summary: z.string(),
    keyPoints: z.array(z.string()),
    confidence: z.number().min(0).max(1),
  }),
});

const result = await agent.invoke({
  messages: [{ role: "user", content: "分析 TypeScript 的优缺点" }],
});

console.log(result.structuredResponse);
// { summary: "...", keyPoints: [...], confidence: 0.9 }
```

## 流式调用（v3 接口）

```typescript
const agent = createDeepAgent({ model: "anthropic:claude-sonnet-4-6" });

const run = await agent.streamEvents(
  {
    messages: [{ role: "user", content: "写一首关于编程的诗" }],
  },
  { version: "v3" },
);

// 流式输出消息文本
for await (const msg of run.messages) {
  for await (const token of msg.text) {
    process.stdout.write(token);
  }
}

// 观察工具调用
for await (const call of run.toolCalls) {
  console.log(`\n[工具调用] ${call.name}`);
  console.log(`输入:`, call.input);
  console.log(`输出:`, await call.output);
}

// 观察子代理委派
for await (const subagent of run.subagents) {
  console.log(`\n[子代理] ${subagent.name}`);
  for await (const msg of subagent.messages) {
    for await (const token of msg.text) {
      process.stdout.write(token);
    }
  }
}

// 获取最终状态
const finalState = await run.output;
```

## 持久化与检查点

```typescript
import { MemorySaver } from "@langchain/langgraph-checkpoint";
import { createDeepAgent } from "deepagents";

const checkpointer = new MemorySaver();

const agent = createDeepAgent({
  checkpointer,
  name: "my-agent",
});

// 第一次调用
await agent.invoke(
  { messages: [{ role: "user", content: "记住我叫张三" }] },
  { configurable: { thread_id: "user-123" } },
);

// 后续调用（同 thread_id，自动恢复状态）
const result = await agent.invoke(
  { messages: [{ role: "user", content: "我叫什么名字？" }] },
  { configurable: { thread_id: "user-123" } },
);
```

## 浏览器环境

使用浏览器安全入口（不包含 Node.js 专有导出如 FilesystemBackend）：

```typescript
import { createDeepAgent, StateBackend } from "deepagents/browser";

const agent = createDeepAgent({
  // 浏览器环境默认使用 StateBackend
});
```

## 自定义 State Schema

```typescript
import { StateSchema } from "@langchain/langgraph";
import { z } from "zod";
import { createDeepAgent, filesValue } from "deepagents";

const agent = createDeepAgent({
  stateSchema: new StateSchema({
    files: filesValue,
    author: z.string().default("unknown"),
    researchNotes: z.array(z.string()).default([]),
  }),
});

const result = await agent.invoke({
  messages: [{ role: "user", content: "做笔记" }],
  author: "张三",
  researchNotes: ["TypeScript 很有趣"],
});
```

与 `contextSchema` 不同，`stateSchema` 定义的字段在使用 checkpointer 时跨调用持久化。

## 注意事项

1. **工具名保留**：不能使用 `ls`、`read_file`、`write_file`、`edit_file`、`delete`、`glob`、`grep`、`execute`、`task`、`start_async_task` 等内置工具名。
2. **默认后端为 StateBackend**：文件仅在对话线程内持久化，生产环境建议使用 FilesystemBackend 或 StoreBackend。
3. **Peer Dependencies**：deepagents 将 LangChain 运行时包声明为 peer dependencies，确保整个应用使用同一副本。
4. **递归限制**：agent 默认 recursionLimit 为 10,000，足够绝大多数任务使用。
5. **子代理技能隔离**：自定义子代理默认不继承主代理的 skills，只有 general-purpose 子代理继承。

相关参考：
- [API 参考](/langchain-ai/deepagentsjs/references/api)
- [总览](/langchain-ai/deepagentsjs/concepts/overview)
- [子代理与规划](/langchain-ai/deepagentsjs/concepts/subagent-planning)
