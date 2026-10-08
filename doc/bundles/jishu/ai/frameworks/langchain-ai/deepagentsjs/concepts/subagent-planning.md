---
type: concept
scope: deepagentsjs
name: subagent-planning
version: "1.13.1"
source: https://github.com/langchain-ai/deepagentsjs
description: deepagentsjs 子代理系统与任务规划——handoff/fork 双模式、通用子代理、异步远程子代理、write_todos 规划工具
---

# 子代理与规划

## 子代理架构概述

deepagentsjs 的子代理系统通过 `createSubAgentMiddleware` 实现，它注入一个名为 `task` 的工具，使主 agent 能够将复杂任务委派给专门的子代理。每个子代理在独立的上下文窗口中运行，返回单一结果，从而实现：

- **上下文隔离**：子代理的中间推理不污染主代理对话
- **并行执行**：主代理可在一条消息中发起多个 `task` 工具调用
- **专业化**：不同子代理可配置不同模型、工具、技能和权限

## 四类子代理

### SubAgent（handoff 模式，默认）

完全隔离的声明式子代理。主代理只传递任务描述字符串，子代理从空对话开始。

```typescript
const researcher: SubAgent = {
  name: "researcher",
  description: "研究助手，负责搜索和分析信息",
  systemPrompt: "你是一个研究助手。",
  tools: [webSearchTool],
  skills: ["/skills/research/"],
};
```

子代理自动获得默认中间件栈：filesystem → summarization → patchToolCalls（`agent.ts:297-314`）。

### ForkedSubAgent（fork 模式）

继承父代理完整对话历史和 system prompt 的子代理，适用于需要延续当前调查上下文的场景。

```typescript
const continuator: ForkedSubAgent = {
  name: "continuator",
  description: "继承当前上下文继续调查",
  mode: "fork",
  tools: [webSearchTool],
};
```

ForkedSubAgent 不能有自己的 `systemPrompt`（`subagents.ts:277`），始终使用父代理的 system prompt。代码会移除尾部未完成的 AIMessage（`stripInFlightAIMessage`），防止工具调用状态不一致。

### CompiledSubAgent（预编译子代理）

接受任意已编译的 `ReactAgent` 或 `Runnable` 实例，提供最大灵活性。

```typescript
const compiled: CompiledSubAgent = {
  name: "custom",
  description: "自定义预编译代理",
  runnable: myPrebuiltAgent,
};
```

CompiledSubAgent 绕过默认中间件组装，使用用户提供的 runnable 原样执行。

### AsyncSubAgent（异步远程子代理）

运行在远程 [Agent Protocol](https://github.com/langchain-ai/agent-protocol) 服务器上的后台任务，通过 LangGraph SDK 通信。

```typescript
const remoteWorker: AsyncSubAgent = {
  name: "remote-worker",
  description: "在远程服务器上运行长时间任务",
  graphId: "my-agent-graph",
  url: "https://langgraph-server.example.com",
  headers: { Authorization: "Bearer xxx" },
};
```

AsyncSubAgent 通过 `graphId` 字段的存在性与 sync 子代理区分（`agent.ts:361-363`），自动路由到 `createAsyncSubAgentMiddleware`。

## task 工具工作流程

1. 主代理决定委派任务，调用 `task({ description, subagent_type })`
2. 中间件验证 `subagent_type` 是否在已注册的子代理中
3. 根据 mode 构造子代理初始状态：
   - handoff：`messages = [HumanMessage(description)]`
   - fork：`messages = [...父代理有效消息, HumanMessage(description)]`
4. 为子代理生成独立的 `_summarizationSessionId`
5. 调用 `subagent.invoke(state, config)`
6. 提取结果：如果有 `structuredResponse` 则 JSON 序列化，否则提取最后一条 AIMessage 的文本
7. 返回 `Command` 更新父代理状态，将结果包装为 `ToolMessage`

## 状态隔离边界

子代理状态传递时，以下键被排除（`subagents.ts:49-57`）：

| 排除键 | 原因 |
|---|---|
| `messages` | 子代理有独立的对话通道 |
| `todos` | 子代理的任务列表不回传父代理 |
| `structuredResponse` | 结构化响应不跨代理共享 |
| `skillsMetadata` | 技能元数据作用域独立 |
| `memoryContents` | 内存内容不跨代理泄漏 |
| `_summarizationEvent` | 摘要事件仅对各自消息列表有效 |
| `_summarizationSessionId` | 每个子代理有独立会话 ID |

用户通过 `stateSchema` 定义的自定义状态字段会透传，允许父子共享业务数据。

## 通用子代理（general-purpose）

默认情况下，`createDeepAgent` 自动添加一个名为 `general-purpose` 的子代理（`agent.ts:385-411`），它：

- 拥有与主代理相同的工具（`effectiveTools`）
- 继承主代理的 skills
- 使用与主代理相同的模型
- 合并用户自定义 middleware（`appendNew: false`，即用户中间件前置）

可以通过 harness profile 的 `generalPurposeSubagent.enabled = false` 禁用。

## 规划：write_todos

规划能力通过 langchain 内置的 `todoListMiddleware()` 提供，它注入 `write_todos` 工具，允许 agent 创建和管理任务列表。

**默认不启用**——deepagentsjs 核心中间件栈不包含 todoListMiddleware（`subagents.ts:223` 注释明确说明）。启用方式：

1. **使用 Codex profile**：当模型为 `openai:gpt-5.1-codex`/`5.2-codex`/`5.3-codex` 时，harness profile 自动添加 `todoListMiddleware()`（`openai-codex.ts:45-47`）
2. **手动添加**：在 `middleware` 中显式传入

```typescript
import { todoListMiddleware } from "langchain";

const agent = createDeepAgent({
  model: "anthropic:claude-sonnet-4-6",
  middleware: [todoListMiddleware()],
});
```

`todos` 状态键在子代理状态过滤中被排除（见上表），意味着每个代理维护独立的任务列表。

## 异步子代理工具集

配置了 AsyncSubAgent 时，中间件注入5个工具：

| 工具 | 功能 |
|---|---|
| `start_async_task` | 启动后台任务，立即返回 task ID |
| `check_async_task` | 查询任务状态和结果 |
| `update_async_task` | 向运行中的任务发送新指令（中断当前 run，在同一 thread 上启动新 run） |
| `cancel_async_task` | 取消运行中的任务 |
| `list_async_tasks` | 列出所有跟踪任务的实时状态 |

任务状态持久化在 agent state 的 `asyncTasks` 字段中，使用 `ReducedValue` + `asyncTasksReducer` 进行浅合并（`async_subagents.ts:177-182`），支持并发更新。

## 动态响应格式

通过 config 中的 `SUBAGENT_RESPONSE_FORMAT_CONFIG_KEY`（值为 `"__deepagents_subagent_response_format"`），可以在调用 task 工具时动态指定子代理的响应格式 schema，触发子代理重新编译。此功能仅对声明式 SubAgent 有效，CompiledSubAgent 会抛出错误（`subagents.ts:642-647`）。

## 相关阅读

- 总览
- 上下文与 Todo 管理
- API 参考
