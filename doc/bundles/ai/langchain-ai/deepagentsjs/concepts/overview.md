---
type: concept
scope: deepagentsjs
name: overview
version: "1.13.1"
source: https://github.com/langchain-ai/deepagentsjs
description: deepagentsjs 总览——基于 LangGraph 的可控 AI Agent 构建库，内置规划、文件系统、子代理和上下文管理
---

# deepagentsjs 总览

## 什么是 deepagentsjs

**deepagentsjs** 是 LangChain 团队开发的 TypeScript agent harness（智能体运行框架），是 Python 版 [deepagents](https://github.com/langchain-ai/deepagents) 的 1:1 移植。它提供"开箱即用"的生产级 agent 运行时，内置规划、文件操作、子代理委派和上下文管理能力，开发者只需自定义模型、工具和提示词即可构建可控的 AI agent。

- **版本**：1.13.1
- **许可证**：MIT
- **运行时**：Node.js / 浏览器（双入口）
- **核心依赖**：`@langchain/core`、`@langchain/langgraph`、`langchain`、`zod`

## 解决的问题

原生使用 LangChain/LangGraph 构建 agent 时，开发者需要手动组装：
- 系统提示词与工具描述
- 多轮对话的上下文窗口管理（摘要、截断）
- 文件读写工具与状态持久化
- 子代理委派与上下文隔离
- 模型提供商差异（Anthropic/OpenAI/Bedrock 的缓存、工具调用格式）

deepagentsjs 通过**约定优于配置**的方式，将这些能力以确定性顺序的中间件栈预置好，同时保留完全的自定义能力。

## 核心能力

| 能力 | 实现机制 | 对应工具/中间件 |
|---|---|---|
| 规划与任务分解 | `todoListMiddleware`（来自 langchain，Codex profile 自动启用） | `write_todos` |
| 文件系统 | `createFilesystemMiddleware` | `ls`、`read_file`、`write_file`、`edit_file`、`delete`、`glob`、`grep`、`execute` |
| 子代理委派 | `createSubAgentMiddleware` | `task` |
| 异步子代理 | `createAsyncSubAgentMiddleware` | `start/check/update/cancel/list_async_task` |
| 上下文摘要 | `createSummarizationMiddleware` | 自动触发，历史卸载到 `/conversation_history/` |
| 长期记忆 | `createMemoryMiddleware` | 加载 AGENTS.md 文件到 system prompt |
| 技能系统 | `createSkillsMiddleware` | 从 SKILL.md 渐进式加载技能 |
| 工具调用修补 | `createPatchToolCallsMiddleware` | 跨模型提供商兼容性 |

## 架构概览

```
用户调用 createDeepAgent(params)
        │
        ▼
┌─────────────────────────────────────────┐
│  Harness Profile 解析                    │
│  (根据 model 选择 prompt 后缀/工具排除)   │
└─────────────────────┬───────────────────┘
                      ▼
┌─────────────────────────────────────────┐
│  中间件三层组装                           │
│  ┌─────────────────────────────────┐    │
│  │ coreMiddleware (固定顺序)        │    │
│  │  skills → fs → subagent         │    │
│  │  → summarization → patch        │    │
│  │  → asyncSubAgent (可选)         │    │
│  ├─────────────────────────────────┤    │
│  │ customMiddleware (用户自定义)    │    │
│  ├─────────────────────────────────┤    │
│  │ tailMiddleware                  │    │
│  │  profile → cache → memory       │    │
│  │  → HITL (可选)                  │    │
│  └─────────────────────────────────┘    │
└─────────────────────┬───────────────────┘
                      ▼
┌─────────────────────────────────────────┐
│  langchain createAgent()                │
│  → 返回 DeepAgent (ReactAgent 子类)     │
│  → recursionLimit: 10,000              │
└─────────────────────────────────────────┘
```

## 后端抽象

所有文件操作通过可插拔的 `BackendProtocolV2` 接口完成，支持多种存储后端：

- **StateBackend**（默认）：文件存储在 LangGraph state 中，随 checkpoint 持久化
- **FilesystemBackend**：直接操作本地文件系统（Node.js）
- **StoreBackend**：基于 LangGraph BaseStore 的跨线程长期存储
- **CompositeBackend**：按路径前缀组合多个后端
- **LangSmithSandbox / LocalShellBackend**：远程沙箱执行环境

详见 [上下文与 Todo 管理](/ai/langchain-ai/deepagentsjs/concepts/context-todo)。

## 子代理系统

deepagentsjs 支持四类子代理：

1. **SubAgent**（handoff 模式）：完全隔离的临时子代理，只接收任务描述
2. **ForkedSubAgent**（fork 模式）：继承父代理完整对话历史
3. **CompiledSubAgent**：预编译的 ReactAgent/Runnable 实例
4. **AsyncSubAgent**：运行在远程 Agent Protocol 服务器上的后台任务

通用子代理（`general-purpose`）默认自动添加，拥有与主代理相同的工具和技能。详见 [子代理与规划](/ai/langchain-ai/deepagentsjs/concepts/subagent-planning)。

## 快速入口

```typescript
import { createDeepAgent } from "deepagents";

const agent = createDeepAgent();

const result = await agent.invoke({
  messages: [
    { role: "user", content: "研究 LangGraph 并将摘要写入 summary.md" },
  ],
});
```

详见 [基础 Agent 示例](/ai/langchain-ai/deepagentsjs/examples/basic-agent) 和 [API 参考](/ai/langchain-ai/deepagentsjs/references/api)。

## 运行时入口

包提供三个环境特定的入口点（`package.json` exports）：

- `deepagents`：默认 Node.js/服务端入口，完整 API
- `deepagents/browser`：浏览器安全入口，不含 Node.js 专有导出
- `deepagents/node`：显式 Node.js 入口（与默认入口相同）

## 进一步阅读

- [子代理与规划](/ai/langchain-ai/deepagentsjs/concepts/subagent-planning)
- [上下文与 Todo 管理](/ai/langchain-ai/deepagentsjs/concepts/context-todo)
- [API 参考](/ai/langchain-ai/deepagentsjs/references/api)
- [基础 Agent 示例](/ai/langchain-ai/deepagentsjs/examples/basic-agent)
