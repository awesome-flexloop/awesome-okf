---
type: spec
scope: deepagentsjs
name: facts
version: "1.13.1"
source: https://github.com/langchain-ai/deepagentsjs
description: deepagentsjs 源码事实验证清单——从 TypeScript 源码中提取的编号事实，含文件路径与行号
---

# deepagentsjs 事实清单

## 项目元信息

F-001: 文件 `libs/deepagents/package.json` 第2-4行，包名为 `deepagents`，版本 `1.13.1`，描述为 "Deep Agents - a library for building controllable AI agents with LangGraph"，作者 LangChain，许可证 MIT。

F-002: 文件 `libs/deepagents/package.json` 第40-44行，运行时依赖为 `fast-glob: ^3.3.3`、`micromatch: ^4.0.8`、`yaml: ^2.8.2`、`zod: ^4.3.6`。

F-003: 文件 `libs/deepagents/package.json` 第101-108行，peerDependencies 包含 `@langchain/core: ^1.2.9`、`@langchain/langgraph: ^1.4.10`、`@langchain/langgraph-checkpoint: ^1.1.5`、`@langchain/langgraph-sdk: ^1.9.23`、`langchain: ^1.5.10`、`langsmith: >=0.7.1 <0.10.0`。

F-004: 文件 `libs/deepagents/package.json` 第67-99行，exports 字段定义了三个入口：`.`（默认 Node.js 入口，含 browser/import/require 条件）、`./browser`（浏览器安全入口）、`./node`（显式 Node.js 入口），以及 `./package.json`。

## 公共 API 导出（src/index.ts）

F-005: 文件 `libs/deepagents/src/index.ts` 第8行，从 `./agent.js` 导出 `createDeepAgent` 函数，这是库的主入口函数。

F-006: 文件 `libs/deepagents/src/index.ts` 第9-14行，从 `./compat.js` 导出四个已废弃的 prompt 常量：`BASE_AGENT_PROMPT`、`TASK_SYSTEM_PROMPT`、`ASYNC_TASK_SYSTEM_PROMPT`、`EXECUTION_SYSTEM_PROMPT`。

F-007: 文件 `libs/deepagents/src/index.ts` 第15行，从 `./errors.js` 导出 `ConfigurationError` 类和 `ConfigurationErrorCode` 类型。

F-008: 文件 `libs/deepagents/src/index.ts` 第18-32行，导出 harness profiles 相关 API：`HarnessProfile`、`HarnessProfileOptions`、`createHarnessProfile`、`serializeProfile`、`parseHarnessProfileConfig`、`registerHarnessProfile`、`getHarnessProfile`、`harnessProfileConfigSchema`、`generalPurposeSubagentConfigSchema`、`EMPTY_HARNESS_PROFILE`、`REQUIRED_MIDDLEWARE_NAMES`。

F-009: 文件 `libs/deepagents/src/index.ts` 第74-110行，导出 middleware 工厂函数：`createFilesystemMiddleware`、`createSubAgentMiddleware`、`createPatchToolCallsMiddleware`、`createSummarizationMiddleware`、`computeSummarizationDefaults`、`createMemoryMiddleware`、`createAsyncSubAgentMiddleware`、`isAsyncSubAgent`、`createSkillsMiddleware`、`createCompletionCallbackMiddleware`、`createAgentMemoryMiddleware`。

F-010: 文件 `libs/deepagents/src/index.ts` 第92-94行，导出 subagent 相关常量：`GENERAL_PURPOSE_SUBAGENT`、`DEFAULT_GENERAL_PURPOSE_DESCRIPTION`、`DEFAULT_SUBAGENT_PROMPT`。

F-011: 文件 `libs/deepagents/src/index.ts` 第113行，从 `./values.js` 导出 `filesValue`，这是一个预配置的 `ReducedValue` 实例，用于文件状态管理。

F-012: 文件 `libs/deepagents/src/index.ts` 第130-193行，导出 backends 相关类和类型：`StateBackend`、`StoreBackend`、`FilesystemBackend`、`CompositeBackend`、`ContextHubBackend`、`BaseSandbox`、`LangSmithSandbox`、`LocalShellBackend`，以及协议类型 `BackendProtocolV1/V2`、`SandboxBackendProtocolV1/V2` 等。

F-013: 文件 `libs/deepagents/src/index.ts` 第195-198行，从 `./middleware/subagents.js` 额外导出 `SUBAGENT_RESPONSE_FORMAT_CONFIG_KEY` 常量和 `createSubAgent` 函数。

## createDeepAgent 主函数（src/agent.ts）

F-014: 文件 `libs/deepagents/src/agent.ts` 第144-173行，`createDeepAgent` 是泛型函数，接受7个类型参数：`TResponse`、`ContextSchema`、`TMiddleware`、`TSubagents`、`TTools`、`TStreamTransformers`、`TStateSchema`，参数类型为 `CreateDeepAgentParams`，默认空对象。

F-015: 文件 `libs/deepagents/src/agent.ts` 第175行，默认模型为 `"anthropic:claude-sonnet-4-6"`。

F-016: 文件 `libs/deepagents/src/agent.ts` 第185行，默认 backend 为 `(config) => new StateBackend(config)`，即文件默认存储在 LangGraph agent state 中（临时存储）。

F-017: 文件 `libs/deepagents/src/agent.ts` 第107-111行，`BUILTIN_TOOL_NAMES` 集合包含所有 `FILESYSTEM_TOOL_NAMES`、`ASYNC_TASK_TOOL_NAMES` 以及 `"task"`。用户自定义工具不能与这些内置工具同名，否则第198-204行抛出 `ConfigurationError`（错误码 `TOOL_NAME_COLLISION`）。

F-018: 文件 `libs/deepagents/src/agent.ts` 第206-212行，通过 `resolveHarnessProfile` 根据 model 字符串或 provider/identifier 提示解析 harness profile，用于模型特定的 prompt 后缀、工具排除和中间件配置。

F-019: 文件 `libs/deepagents/src/agent.ts` 第236-256行，当检测到 Anthropic 模型时，添加 `anthropicPromptCachingMiddleware` 和 `createCacheBreakpointMiddleware`；当检测到 Bedrock Converse 模型时，添加 `bedrockPromptCachingMiddleware`。

F-020: 文件 `libs/deepagents/src/agent.ts` 第258-267行，当配置了 `memory`（AGENTS.md 文件路径数组）时，创建 `createMemoryMiddleware`，传入 backend、sources 和 `addCacheControl`（Anthropic 模型时为 true）。

F-021: 文件 `libs/deepagents/src/agent.ts` 第289-315行，`createSubagentDefaultMiddleware` 为子代理创建默认中间件栈：`createFilesystemMiddleware`、`createSummarizationMiddleware`、`createPatchToolCallsMiddleware`，以及可选的 `createSkillsMiddleware`（当子代理配置了自己的 skills 时）。

F-022: 文件 `libs/deepagents/src/agent.ts` 第357-380行，将统一的 subagents 数组拆分为 sync 和 async 两类：通过 `isAsyncSubAgent`（检测 `graphId` 字段）识别 AsyncSubAgent；sync 子代理中，有 `runnable` 字段的为 CompiledSubAgent（原样使用），`mode: "fork"` 的为 ForkedSubAgent（继承父对话历史），其余为普通 SubAgent。

F-023: 文件 `libs/deepagents/src/agent.ts` 第382-411行，当 harness profile 未禁用 general-purpose 子代理且用户未提供同名子代理时，自动添加 `GENERAL_PURPOSE_SUBAGENT`（name: `"general-purpose"`），它继承主代理的 skills、tools 和 model，并合并用户自定义 middleware。

F-024: 文件 `libs/deepagents/src/agent.ts` 第421-443行，`builtInMiddleware` 元组按顺序包含：`createFilesystemMiddleware`、`createSubAgentMiddleware`、`createSummarizationMiddleware`、`createPatchToolCallsMiddleware`。

F-025: 文件 `libs/deepagents/src/agent.ts` 第453-464行，`coreMiddleware` 数组顺序为：可选的 skillsMiddleware、fsMiddleware、subagentMiddleware、summarizationMiddleware、patchToolCallsMiddleware、可选的 asyncSubAgentMiddleware（当存在 async 子代理时）。

F-026: 文件 `libs/deepagents/src/agent.ts` 第465-474行，`tailMiddleware` 数组包含：profile extraMiddleware、cacheMiddleware、memoryMiddleware、可选的 `humanInTheLoopMiddleware`（当配置了 interruptOn 时）。

F-027: 文件 `libs/deepagents/src/agent.ts` 第476-480行，使用 `mergeMiddlewareStack(coreMiddleware, customMiddleware, tailMiddleware)` 合并三层中间件，确保用户自定义中间件插入到核心和尾部中间件之间。

F-028: 文件 `libs/deepagents/src/agent.ts` 第496-514行，最终调用 langchain 的 `createAgent` 创建代理，设置 `recursionLimit: 10_000`，metadata 包含 `ls_integration: "deepagents"` 和 `lc_agent_name`。

## 类型系统（src/types.ts）

F-029: 文件 `libs/deepagents/src/types.ts` 第89-93行，`AnySubAgent` 类型为联合类型：`SubAgent | CompiledSubAgent | ForkedSubAgent | AsyncSubAgent`。

F-030: 文件 `libs/deepagents/src/types.ts` 第210-238行，`DeepAgentTypeConfig` 接口继承自 langchain 的 `AgentTypeConfig`，额外增加了 `Subagents: TSubagents` 类型参数，用于类型安全的流式传输和委托。

F-031: 文件 `libs/deepagents/src/types.ts` 第270-363行，`DeepAgent` 接口继承 `ReactAgent<TTypes>`，添加了 `readonly "~deepAgentTypes": TTypes` 类型品牌，并重载了 `streamEvents` 方法，支持 `version: "v3"` 参数返回 `DeepAgentRunStream`。

F-032: 文件 `libs/deepagents/src/types.ts` 第510-661行，`CreateDeepAgentParams` 接口包含字段：`model`、`tools`、`systemPrompt`、`stateSchema`、`middleware`、`subagents`、`responseFormat`、`contextSchema`、`checkpointer`、`store`、`backend`、`interruptOn`、`name`、`memory`、`skills`、`permissions`、`streamTransformers`。

F-033: 文件 `libs/deepagents/src/types.ts` 第525行注释，`model` 参数默认为 `claude-sonnet-4-5-20250929`（注释值，实际代码默认值为 `anthropic:claude-sonnet-4-6`）。

F-034: 文件 `libs/deepagents/src/types.ts` 第536-560行，`stateSchema` 允许定义自定义 agent state 属性，超越内置的 `messages` 和 `files`。与 `contextSchema` 不同，state 在使用 checkpointer 时会在代理调用之间持久化。

## 子代理系统（src/middleware/subagents.ts）

F-035: 文件 `libs/deepagents/src/middleware/subagents.ts` 第34-35行，`SUBAGENT_RESPONSE_FORMAT_CONFIG_KEY` 常量值为 `"__deepagents_subagent_response_format"`，用于通过 config.configurable 动态指定子代理响应格式。

F-036: 文件 `libs/deepagents/src/middleware/subagents.ts` 第41-42行，`DEFAULT_SUBAGENT_PROMPT` 值为 `"In order to complete the objective that the user asks of you, you have access to a number of standard tools."`。

F-037: 文件 `libs/deepagents/src/middleware/subagents.ts` 第49-57行，`EXCLUDED_STATE_KEYS` 常量数组包含：`"messages"`、`"todos"`、`"structuredResponse"`、`"skillsMetadata"`、`"memoryContents"`、`"_summarizationEvent"`、`"_summarizationSessionId"`。这些键在传递状态给子代理和从子代理返回更新时被排除。

F-038: 文件 `libs/deepagents/src/middleware/subagents.ts` 第63-64行，`DEFAULT_GENERAL_PURPOSE_DESCRIPTION` 描述通用子代理用于"研究复杂问题、搜索文件和内容、执行多步骤任务"。

F-039: 文件 `libs/deepagents/src/middleware/subagents.ts` 第91-107行，`CompiledSubAgent` 接口包含 `name`、`description`、`runnable`（ReactAgent 或 Runnable 实例），以及可选的 `mode: "handoff" | "fork"`。

F-040: 文件 `libs/deepagents/src/middleware/subagents.ts` 第240-249行，`SubAgent` 接口继承 `SubAgentBase`，`systemPrompt` 为可选，`mode` 只能是 `"handoff"`（默认，完全隔离）。

F-041: 文件 `libs/deepagents/src/middleware/subagents.ts` 第275-284行，`ForkedSubAgent` 接口继承 `SubAgentBase`，`systemPrompt` 必须为 `undefined`（始终继承父代理的），`mode` 必须为 `"fork"`（继承父代理完整对话历史）。

F-042: 文件 `libs/deepagents/src/middleware/subagents.ts` 第330-335行，`GENERAL_PURPOSE_SUBAGENT` 常量对象：name 为 `"general-purpose"`，使用默认描述和 prompt，mode 为 `"handoff"`。

F-043: 文件 `libs/deepagents/src/middleware/subagents.ts` 第430-463行，`createSubAgent` 函数从声明式 `SubAgent` spec 编译出 `ReactAgent`。要求 spec 必须有 `model` 和 `tools`，否则抛出错误。支持可选的 `interruptOn` 和 `responseFormat`。

F-044: 文件 `libs/deepagents/src/middleware/subagents.ts` 第659-749行，`createTaskTool` 创建名为 `"task"` 的工具，schema 为 `z.object({ description: z.string(), subagent_type: z.string() })`。工具执行时：验证 subagent_type、根据 mode 决定是否 fork 父消息、创建独立的 summarizationSessionId、调用 `subagent.invoke`、返回 `Command` 更新或字符串结果。

F-045: 文件 `libs/deepagents/src/middleware/subagents.ts` 第679-690行，fork 模式下，子代理状态的 messages 为 `[...getEffectiveMessages(trimmed, currentState), new HumanMessage(description)]`；handoff 模式下仅为 `[new HumanMessage(description)]`。

F-046: 文件 `libs/deepagents/src/middleware/subagents.ts` 第784-825行，`createSubAgentMiddleware` 返回名为 `"subAgentMiddleware"` 的中间件，通过 `tools: [taskTool]` 注入 task 工具，并在 `wrapModelCall` 中可选地追加 systemPrompt。

## 文件系统中间件（src/middleware/fs.ts）

F-047: 文件 `libs/deepagents/src/middleware/fs.ts` 第100-109行，`FILESYSTEM_TOOL_NAMES` 常量数组为 `["ls", "read_file", "write_file", "edit_file", "delete", "glob", "grep", "execute"]`（共8个工具）。

F-048: 文件 `libs/deepagents/src/middleware/fs.ts` 第117-119行，`TOOLS_EXCLUDED_FROM_EVICTION` 为除 `"execute"` 外的所有文件系统工具名，即 ls/read_file/write_file/edit_file/delete/glob/grep 的结果不会被驱逐到文件系统。

F-049: 文件 `libs/deepagents/src/middleware/fs.ts` 第126行，`NUM_CHARS_PER_TOKEN` 常量为 4，用于截断计算中的字符/token 近似换算。

F-050: 文件 `libs/deepagents/src/middleware/fs.ts` 第131-132行，`DEFAULT_READ_LINE_OFFSET = 0`，`DEFAULT_READ_LINE_LIMIT = 100`，read_file 工具的默认分页参数。

F-051: 文件 `libs/deepagents/src/middleware/fs.ts` 第139行，`MAX_BINARY_READ_SIZE_BYTES = 10 * 1024 * 1024`（10MB），二进制文件通过 read_file 读取的最大大小。

F-052: 文件 `libs/deepagents/src/middleware/fs.ts` 第161行，`DEFAULT_GREP_MAX_COUNT = 1000`，grep 工具默认返回的最大匹配数。

## 摘要中间件（src/middleware/summarization.ts）

F-053: 文件 `libs/deepagents/src/middleware/summarization.ts` 第83-88行，`ContextSize` 接口包含 `type: "messages" | "tokens" | "fraction"` 和 `value: number`，用于配置摘要触发阈值和保留策略。

F-054: 文件 `libs/deepagents/src/middleware/summarization.ts` 第175行，`DEFAULT_MESSAGES_TO_KEEP = 20`，摘要后默认保留的消息数。

F-055: 文件 `libs/deepagents/src/middleware/summarization.ts` 第178-183行，回退默认值（当模型无 profile 时）：trigger 为 170,000 tokens，keep 为 6 messages，truncateArgs 触发于 20 messages。

F-056: 文件 `libs/deepagents/src/middleware/summarization.ts` 第186-191行，profile 默认值（当模型有 maxInputTokens 时）：trigger 为 0.85（85% 上下文），keep 为 0.1（10%），truncateArgs 同样使用分数比例。

F-057: 文件 `libs/deepagents/src/middleware/summarization.ts` 第27行注释，卸载的消息以 Markdown 格式存储在 `/conversation_history/{thread_id}.md`，每次摘要事件追加新段落。

## 内存中间件（src/middleware/memory.ts）

F-058: 文件 `libs/deepagents/src/middleware/memory.ts` 第82-106行，`MemoryMiddlewareOptions` 接口包含 `backend`（BackendProtocol 或工厂函数）、`sources`（AGENTS.md 文件路径数组）、`addCacheControl`（布尔值，是否为 Anthropic 添加缓存断点）。

F-059: 文件 `libs/deepagents/src/middleware/memory.ts` 第111-118行，MemoryStateSchema 使用 `StateSchema` 定义，包含 `memoryContents`（z.record(z.string(), z.string())，私有字段）和 `files: filesValue`。

## 异步子代理（src/middleware/async_subagents.ts）

F-060: 文件 `libs/deepagents/src/middleware/async_subagents.ts` 第26-41行，`AsyncSubAgent` 接口包含 `name`、`description`、`graphId`（远程 Agent Protocol 服务器上的图名/助手 ID）、可选的 `url` 和 `headers`。通过 `graphId` 字段的存在性与 sync 子代理区分。

F-061: 文件 `libs/deepagents/src/middleware/async_subagents.ts` 第49-56行，`AsyncTaskStatus` 类型为联合类型：`"pending" | "running" | "success" | "error" | "cancelled" | "timeout" | "interrupted"`。

F-062: 文件 `libs/deepagents/src/middleware/async_subagents.ts` 第65-92行，`AsyncTask` 接口包含 `taskId`（与 threadId 相同）、`agentName`、`threadId`、`runId`、`status`、`createdAt`、可选的 `description`、`updatedAt`、`checkedAt`。

F-063: 文件 `libs/deepagents/src/middleware/async_subagents.ts` 第156-164行，AsyncTaskStateSchema 将 `asyncTasks` 声明为 `ReducedValue`，使用 `asyncTasksReducer` 进行浅合并，允许单个工具更新而不替换整个任务字典。

F-064: 文件 `libs/deepagents/src/middleware/async_subagents.ts` 第190-200行，异步任务工具集包含5个工具：`start_async_task`、`check_async_task`、`update_async_task`、`cancel_async_task`、`list_async_tasks`。

## 状态值管理（src/values.ts）

F-065: 文件 `libs/deepagents/src/values.ts` 第34-40行，`filesValue` 是 `ReducedValue` 实例，schema 为 `z.record(z.string(), FileDataSchema).default(() => ({}))`，inputSchema 允许 nullable 值（用于删除），reducer 为 `fileDataReducer`。支持并行子代理的并发文件更新自动合并。

## 后端系统

F-066: 文件 `libs/deepagents/src/backends/state.ts` 第59行，`StateBackend` 类实现 `BackendProtocolV2` 接口，将文件存储在 LangGraph agent state 中（临时存储），文件在对话线程内持久化但不跨线程。

F-067: 文件 `libs/deepagents/src/backends/state.ts` 第45-46行，StateBackend 使用 LangGraph 内部的 `__pregel_send` 和 `__pregel_read` 键进行状态读写，镜像了 Python 版的 `CONFIG_KEY_SEND` 机制。

F-068: 文件 `libs/deepagents/src/backends/index.ts` 第55-71行，导出的后端类包括：`StateBackend`、`StoreBackend`、`FilesystemBackend`、`CompositeBackend`、`ContextHubBackend`、`LocalShellBackend`、`BaseSandbox`（抽象类）、`LangSmithSandbox`。

F-069: 文件 `libs/deepagents/src/backends/protocol.ts` 第119-146行，定义了两种文件数据格式：`FileDataV1`（content 为 string[]，按行分割，仅支持文本）和 `FileDataV2`（content 为 string | Uint8Array，支持二进制，含 mimeType 字段）。

## Harness Profile 系统

F-070: 文件 `libs/deepagents/src/profiles/harness/types.ts` 第11-14行，`REQUIRED_MIDDLEWARE_NAMES` 集合包含 `"FilesystemMiddleware"` 和 `"SubAgentMiddleware"`，这两个中间件不能通过 profile 的 `excludedMiddleware` 排除。

F-071: 文件 `libs/deepagents/src/profiles/harness/types.ts` 第61-136行，`HarnessProfileOptions` 接口包含：`baseSystemPrompt`、`systemPromptSuffix`、`toolDescriptionOverrides`、`excludedTools`、`excludedMiddleware`、`extraMiddleware`、`generalPurposeSubagent`。

F-072: 文件 `libs/deepagents/src/profiles/harness/builtins/openai-codex.ts` 第12-16行，Codex profile 注册到三个模型规格：`"openai:gpt-5.1-codex"`、`"openai:gpt-5.2-codex"`、`"openai:gpt-5.3-codex"`。

F-073: 文件 `libs/deepagents/src/profiles/harness/builtins/openai-codex.ts` 第45-47行，Codex profile 的 `extraMiddleware` 工厂返回 `[todoListMiddleware()]`，即自动启用从 langchain 导入的待办事项列表中间件（提供 `write_todos` 工具）。

F-074: 文件 `libs/deepagents/src/profiles/harness/builtins/anthropic-sonnet-4-6.ts` 第31-36行，Sonnet 4.6 profile 仅添加 systemPromptSuffix（并行工具调用、先调查再回答、工具结果反思），不添加额外中间件。

## 技能系统（src/middleware/skills.ts）

F-075: 文件 `libs/deepagents/src/middleware/skills.ts` 第68行，`MAX_SKILL_FILE_SIZE = 10 * 1024 * 1024`（10MB），SKILL.md 文件的最大大小限制。

F-076: 文件 `libs/deepagents/src/middleware/skills.ts` 第73-75行，技能名称最大长度 64 字符，描述最大长度 1024 字符，兼容性字段最大长度 500 字符。

F-077: 文件 `libs/deepagents/src/middleware/skills.ts` 第80-89行，技能模块入口文件支持的扩展名：`.js`、`.mjs`、`.cjs`、`.ts`、`.mts`、`.cts`、`.jsx`、`.tsx`。

## 权限系统（src/permissions/types.ts）

F-078: 文件 `libs/deepagents/src/permissions/types.ts` 第4行，`FilesystemOperation` 类型为 `"read" | "write"`。

F-079: 文件 `libs/deepagents/src/permissions/types.ts` 第7行，`PermissionMode` 类型为 `"allow" | "deny"`。

F-080: 文件 `libs/deepagents/src/permissions/types.ts` 第23-40行，`FilesystemPermission` 接口包含 `operations`（只读/只写/读写）、`paths`（绝对 glob 模式数组，必须以 `/` 开头，不允许 `..` 或 `~`）、可选的 `mode`（默认 `"allow"`）。规则按声明顺序求值，首次匹配优先，无匹配则默认允许。

## 与 Python 版的对应关系

F-081: 文件 `libs/deepagents/src/index.ts` 第1-6行注释，明确声明这是 "Deep Agents TypeScript Implementation"，是 Python Deep Agents 库的 TypeScript 移植，保持与 Python 版的 1:1 兼容性。

F-082: 文件 `libs/deepagents/src/middleware/summarization.ts` 第195行注释，`computeSummarizationDefaults` 函数镜像 Python 版的 `_compute_summarization_defaults`。

F-083: 文件 `libs/deepagents/src/middleware/subagents.ts` 第223行注释，子代理默认中间件栈中不包含 todoListMiddleware，需要显式添加（与 Python 版行为一致）。
