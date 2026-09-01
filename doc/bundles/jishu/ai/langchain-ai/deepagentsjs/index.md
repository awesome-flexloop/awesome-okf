---
type: bundle
okf_version: "0.2"
scope: deepagentsjs
name: deepagentsjs
version: "1.13.1"
source: https://github.com/langchain-ai/deepagentsjs
description: deepagentsjs——LangChain 开源的 TypeScript Agent Harness，基于 LangGraph 构建可控 AI Agent，内置规划、文件系统、子代理、上下文摘要和技能系统
---

# deepagentsjs

**deepagentsjs** 是 LangChain 团队开发的 TypeScript agent harness（智能体运行框架），是 Python 版 [deepagents](https://github.com/langchain-ai/deepagents) 的 1:1 移植。它提供"开箱即用"的生产级 agent 运行时，内置任务规划、文件操作、子代理委派、上下文管理和技能系统，开发者只需自定义模型、工具和提示词即可构建可控的 AI agent。

- **版本**：1.13.1
- **许可证**：MIT
- **运行时**：Node.js / 浏览器（双入口）
- **核心依赖**：`@langchain/core` ≥1.2.9、`@langchain/langgraph` ≥1.4.10、`langchain` ≥1.5.10、`zod` ^4.3.6

## 核心特性

- **中间件分层架构**：确定性的"核心-自定义-尾部"三段式中间件组装，核心能力（文件系统、子代理、摘要）固定顺序，用户中间件插入中间，横切关注点（缓存、HITL、记忆）在尾部。
- **四类子代理**：SubAgent（handoff 隔离）、ForkedSubAgent（fork 继承父上下文）、CompiledSubAgent（预编译实例）、AsyncSubAgent（远程 Agent Protocol 服务器），通过统一的 `task` 工具委派。
- **可插拔后端**：StateBackend（默认，state 中临时存储）、FilesystemBackend（本地磁盘）、StoreBackend（BaseStore 长期存储）、CompositeBackend（前缀路由）、沙箱后端（LangSmith/LocalShell），统一 `BackendProtocolV2` 接口。
- **自动上下文管理**：接近 token 限制时自动摘要旧消息，历史卸载到 `/conversation_history/{thread_id}.md`；工具结果过大时自动驱逐到文件系统并保留预览。
- **Harness Profile 系统**：根据模型自动应用 prompt 后缀、工具排除、额外中间件（如 Codex 模型自动启用 `todoListMiddleware` 提供 `write_todos` 规划工具）。
- **技能与记忆**：支持 AGENTS.md 长期记忆（启动时加载到 system prompt）和 SKILL.md 技能（渐进式披露），均通过后端抽象访问，可移植到任意存储。
- **v3 流式接口**：`streamEvents(state, { version: "v3" })` 返回类型安全的 `DeepAgentRunStream`，提供 messages、toolCalls、subagents、middleware、values 等投影。
- **完善的 TypeScript 类型**：泛型推断子代理类型、中间件状态、结构化响应类型，支持类型安全的流式传输和委托。

## 快速开始

```bash
npm install deepagents
```

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
```

自定义模型、工具和子代理：

```typescript
import { createDeepAgent, FilesystemBackend } from "deepagents";
import { ChatOpenAI } from "@langchain/openai";
import { todoListMiddleware } from "langchain";

const agent = createDeepAgent({
  model: new ChatOpenAI({ model: "gpt-4o", temperature: 0 }),
  backend: new FilesystemBackend({ rootDir: "/workspace" }),
  middleware: [todoListMiddleware()],
  subagents: [
    {
      name: "researcher",
      description: "研究助手，负责网络搜索和信息分析",
      systemPrompt: "你是一个专业研究助手。",
    },
  ],
  memory: ["~/.deepagents/AGENTS.md"],
  skills: ["/skills/"],
});
```

## 文档导航

### 核心概念

- 总览 — deepagentsjs 是什么、解决什么问题、核心能力与架构概览
- 子代理与规划 — handoff/fork 双模式、四类子代理、task 工具、write_todos、异步远程子代理
- 上下文与 Todo 管理 — 摘要卸载、后端抽象、filesValue 状态归约、内存/技能/权限系统

### API 参考

- API 参考 — createDeepAgent、中间件工厂、后端类、子代理类型、Harness Profile

### 使用示例

- 基础 Agent 示例 — 最简 Agent、自定义工具、子代理、文件后端、流式调用、持久化

## 目录结构

```
deepagentsjs/
├── spec/
│   ├── facts.md           # 源码事实验证清单（83条编号事实）
│   └── insights.md        # 架构设计洞察（3篇深度分析）
├── concepts/              # 核心概念（3篇）
│   ├── overview.md
│   ├── subagent-planning.md
│   └── context-todo.md
├── references/            # API参考（1篇）
│   └── api.md
├── examples/              # 使用示例（1篇）
│   └── basic-agent.md
└── index.md               # 本文件
```

## 与 Python 版的关系

deepagentsjs 在源码注释中明确声明保持与 Python 版 deepagents 的 1:1 兼容性（`src/index.ts:1-6`）。关键对应关系：

| 概念 | Python 版 | TypeScript 版 |
|---|---|---|
| 入口函数 | `create_deep_agent()` | `createDeepAgent()` |
| 子代理 | `SubAgent` / `CompiledSubAgent` / `ForkedSubAgent` | 同名类型 |
| 后端协议 | `BackendProtocol` | `BackendProtocolV2`（含 v1 兼容） |
| 摘要默认值 | `_compute_summarization_defaults` | `computeSummarizationDefaults` |
| 状态发送 | `CONFIG_KEY_SEND` | `__pregel_send` |

## 运行时入口

包提供三个环境特定的入口点（`package.json` exports）：

- `deepagents`：默认 Node.js/服务端入口，完整 API
- `deepagents/browser`：浏览器安全入口，不含 Node.js 专有导出
- `deepagents/node`：显式 Node.js 入口（与默认入口 API 相同）

## 安全说明

deepagentsjs 遵循"信任 LLM"模型。agent 可以执行其工具允许的任何操作。应在工具/沙箱级别强制执行边界，而非期望模型自我约束。文件系统权限通过 `permissions` 参数配置，支持基于 glob 的读写允许/拒绝规则。

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
