---
type: concept
scope: openwiki
name: agent-system
version: "0.3.3"
source: https://github.com/langchain-ai/openwiki
description: OpenWiki Agent 系统——DeepAgent 图构建、命令模式、checkpoint 策略与中间件管道
---

# Agent 系统

OpenWiki 的 agent 层基于 [DeepAgents](https://github.com/langchain-ai/deepagents) 框架构建，将 LangGraph 代理与文件系统后端、工具、中间件组合为完整的文档生成图。本文档解析 agent 的构建流程、三种命令模式的差异、checkpoint 策略和中间件管道。

## 两级 API 架构

Agent 层暴露两个层级的 API（见 [API 参考](/langchain-ai/openwiki/references/api)）：

### `runOpenWikiAgent`（高层运行边界）

```typescript
runOpenWikiAgent(
  command: OpenWikiCommand,
  cwd?: string,
  options?: OpenWikiRunOptions,
  telemetryContext?: RunTelemetryContext,
): Promise<OpenWikiRunResult>
```

这是 CLI 使用的完整入口，按以下顺序执行：

1. **环境加载**：`loadOpenWikiEnv()` 加载 `~/.openwiki/.env`，`syncBundledSkills()` 同步内置 skills。
2. **Ignore 规则**：repository 模式加载 `.openwikiignore`，local-wiki 模式使用空规则。
3. **Claims 预检**：非 repository-init 模式下，`prepareClaimsRuntime` 做 fail-fast 证据验证。
4. **No-op 检测**（仅 update）：`getUpdateNoopStatus` 检查 git head/worktree/语言/中断状态，决定是否跳过 LLM 调用。
5. **Provider 解析**：`resolveRunConfig` 解析 provider、凭证、model ID、重试次数、max output tokens、stream idle timeout。
6. **Wiki 替换事务**（仅 repository init）：`beginRepositoryWikiReplacement` 备份旧 wiki，成功 commit、失败 rollback。
7. **核心执行**：`runOpenWikiAgentCore` 创建模型、checkpointer、agent 图，流式消费事件。
8. **崩溃守卫**：仅在 stream 消费窗口注册 active run，逃逸错误标记为 interrupted。
9. **持久化**：成功写 `"complete"` 元数据；失败尽力写 `"interrupted"`；清理临时文件（`_plan.md`、`_skeleton.md`）。

### `createOpenWikiAgent`（低层图工厂）

```typescript
createOpenWikiAgent(options: OpenWikiAgentOptions): Promise<DeepAgent>
```

从已初始化的 `BaseChatModel` 创建 agent 图，不涉及环境加载、凭证、telemetry 或元数据。适合测试和编程式调用。内部调用 `createOpenWikiAgentGraph` 完成实际组装。

## 命令模式差异

三种命令（`chat`/`init`/`update`）在 agent 行为上有系统性差异：

| 维度 | chat | init | update |
|---|---|---|---|
| Checkpoint | SQLite 持久化 | 内存 | 内存 |
| Docs-only backend | 否（可执行命令） | 是 | 是 |
| 翻译中间件 | 否 | 条件启用 | 条件启用 |
| Claims 中间件 | 否 | 是 | 是 |
| Index 中间件 | 否 | 是 | 是 |
| Review subagents | 否 | 是 | 是 |
| 元数据持久化 | 否 | 是 | 是 |
| 内容快照 | null | SHA-256 | SHA-256 |
| 临时文件清理 | 否 | 是 | 是 |

- **chat**：对话模式，不修改 wiki，使用持久化 checkpoint 支持多轮对话恢复，不启用文档专用中间件。
- **init**：首次生成，docs-only 后端限制文件写入范围到 wiki 目录，启用完整的翻译/Claims/index 中间件和 review subagents。
- **update**：增量更新，在 init 的基础上增加 no-op 检测、语言切换翻译、待修复页面重试。

## Checkpoint 策略

`resolveCheckpointTarget(command)` 决定 checkpoint 存储：

```typescript
// chat: 持久化 SQLite
{ connString: "~/.openwiki/openwiki.sqlite", persistent: true }

// init/update: 内存
{ connString: ":memory:", persistent: false }
```

**持久化 checkpoint 的清理**：chat 会话复用同一 `thread_id`，deepagents 的摘要中间件会在每个 graph step 写入完整状态快照，sqlite 文件会无限增长。`pruneCheckpointHistory` 在每次运行后执行 SQL 清理：

- 对每个 `checkpoint_ns`，仅保留最新的 `checkpoint_id`（`ROW_NUMBER() OVER (PARTITION BY checkpoint_ns ORDER BY checkpoint_id DESC)`）。
- 删除不属于任何存活 checkpoint 的 writes 行。
- 整个操作在 SQLite 事务中执行。

Checkpoint 文件权限设置为 0o600，目录权限 0o700。

## Agent 图组装

`createOpenWikiAgentGraph` 调用 `createDeepAgent` 时传入以下组件：

### Backend（文件系统抽象）

`createAgentBackend` 创建 `CompositeBackend`，叠加三层：

1. **Wiki backend**（`OpenWikiLocalShellBackend`）：文档根目录，docs-only 模式限制写入，`maxOutputBytes: 100_000`，`timeout: 120` 秒，virtualMode。
2. **`/conversation_history/`**：挂载到 `~/.openwiki/conversation_history`，供摘要中间件卸载对话历史。
3. **`/skills/`**：挂载到 `~/.openwiki/skills`，只读供 agent 加载技能。

`OpenWikiCompositeBackend` 重写 `glob()` 捕获栈溢出错误（过宽的 glob 模式），返回友好错误而非崩溃。

### 权限控制

`AGENT_FILESYSTEM_PERMISSIONS` 拒绝 agent 工具对两个虚拟路径的写入：

```typescript
[
  { operations: ["write"], paths: ["/skills/**"], mode: "deny" },
  { operations: ["write"], paths: ["/conversation_history/**"], mode: "deny" },
]
```

`/skills/` 由 CLI 安装，agent 不可修改；`/conversation_history/` 仅摘要中间件可通过 backend 直接写入，拒绝工具写入防止 prompt 注入持久化到未来会话。

### Tools

工具列表由两部分组成：
- **Connector tools**（`createOpenWikiConnectorTools`）：文件读写、搜索等文档操作工具。
- **Claims tools**（条件启用）：证据验证相关工具。

### Middleware（中间件管道）

非 chat 命令按顺序组装：

1. **翻译中间件**（`createWikiTranslationMiddleware`，条件）：当请求语言与 wiki 持久化语言不同时，在 agent 运行前重翻译所有页面；update 时重试上次中断的待翻译页面。
2. **Claims 中间件**（条件）：证据收集和验证。
3. **Index 中间件**（`createOpenWikiIndexMiddleware`）：生成本地化目录索引标签、stamp 概念类型、记录 provenance 时间戳。

### Subagents

`resolveRepositoryReviewSubagents` 根据命令和输出模式返回 review 子代理，用于文档质量审查。

### System Prompt

`createSystemPrompt` 根据命令、输出模式、语言和 ignore 规则生成系统提示。

## 模型创建

`createModel(provider, modelId, retryAttempts, maxOutputTokens?, streamIdleTimeout?)` 是模型工厂，根据 provider 类型分支创建不同的 LangChain chat model：

- **gemini**：`ChatGoogle`（AI Studio，`platformType: "gai"`），禁用流式以保留 thought-signature。
- **gemini-enterprise**：Vertex AI，按模型 ID 路由到 anthropic/openai-maas/原生 Gemini 三种 surface。
- **anthropic**：`ChatAnthropic`，现代 Claude 4/5 默认 16384 max tokens。
- **openai-chatgpt**：`ChatOpenAI` 指向 Codex Responses API，强制流式，携带 account-id/originator/beta headers。
- **openrouter**：`ChatOpenRouter`，siteName 设为 "OpenWiki"。
- **bedrock**：`ChatBedrockConverse`，AWS SDK 凭证链。
- **默认**：`ChatOpenAI`（openai、openai-compatible、baseten、fireworks、nvidia、copilot、nebius）。

## 流式事件解析

Agent 以 LangGraph stream 模式运行（`streamMode: ["messages", "tools"]`，`subgraphs: true`）。`parseAgentStreamChunk` 将三元组 `[namespace, mode, payload]` 转换为 `OpenWikiRunEvent`：

- **messages 模式**：递归提取消息文本，跳过 tool/reasoning/file/image 类型的 content block，区分 main graph 和 subgraph。
- **tools 模式**：解析 `on_tool_start`/`on_tool_end`/`on_tool_error`，生成 `tool_start`/`tool_end` 事件，工具调用参数经过 `sanitizeDiagnosticText` 脱敏。

`--print` 模式仅收集 text 事件拼接输出；TUI 模式通过 `onEvent` 回调实时渲染。

## 进一步阅读

- [总览](/langchain-ai/openwiki/concepts/overview)
- [Auth 与 CLI 认证体系](/langchain-ai/openwiki/concepts/auth-cli)
- [API 参考](/langchain-ai/openwiki/references/api)
