---
type: spec
scope: deepagentsjs
name: insights
version: "1.13.1"
source: https://github.com/langchain-ai/deepagentsjs
description: deepagentsjs 深度洞察——从 TypeScript 源码中提炼的架构设计决策与实现机制
---

# deepagentsjs 深度洞察

## 1. 中间件分层组装：确定性顺序的"核心-自定义-尾部"三段式架构

deepagentsjs 最核心的设计决策是将 agent 能力完全构建在 langchain 的 `AgentMiddleware` 机制之上，并采用**三层确定性组装**策略。在 `createDeepAgent` 中（`agent.ts:476-480`），中间件通过 `mergeMiddlewareStack(coreMiddleware, customMiddleware, tailMiddleware)` 合并：

- **coreMiddleware**（`agent.ts:453-464`）：按固定顺序提供基础能力——skills（可选）→ filesystem → subagent → summarization → patchToolCalls → asyncSubAgent（可选）。这些中间件注入工具、包装模型调用，是 agent 运行的骨架。
- **customMiddleware**：用户通过 `middleware` 参数传入的中间件，插入在核心能力之后、尾部增强之前。这保证了用户中间件既能访问核心工具，又不会被尾部中间件（如缓存、HITL）覆盖。
- **tailMiddleware**（`agent.ts:465-474`）：profile extraMiddleware → prompt caching → memory（可选）→ human-in-the-loop（可选）。这些是"横切关注点"，需要在所有业务逻辑之后生效。

**设计意图**：这种分层解决了中间件顺序敏感的问题。例如，prompt caching 必须在 system prompt 最终组装完成后才能标记缓存断点；HITL 中断必须在所有工具注入完成后才能配置拦截规则。用户无需关心这些顺序约束，只需将自定义逻辑放入中间层。

此外，harness profile 还可以通过 `excludedMiddleware`（`agent.ts:483-486`）在组装后过滤掉特定中间件，但 `FilesystemMiddleware` 和 `SubAgentMiddleware` 被标记为必需（`profiles/harness/types.ts:11-14`），不可排除——它们构成了 agent 与外部世界交互的最小集合。

## 2. 子代理隔离与状态过滤：handoff/fork 双模式与 EXCLUDED_STATE_KEYS 边界

deepagentsjs 的子代理系统实现了两种上下文继承模式，其核心是**状态边界的精确控制**：

- **handoff 模式**（默认）：子代理完全隔离，只看到 `new HumanMessage({ content: description })`（`subagents.ts:689`）。父代理的对话历史、system prompt 对子代理不可见。这适用于独立任务，避免上下文膨胀。
- **fork 模式**（`ForkedSubAgent`，`subagents.ts:275-284`）：子代理继承父代理的完整消息历史和 system prompt，但仍然有独立的状态通道。代码通过 `stripInFlightAIMessage` 移除尾部未完成的 AIMessage（防止工具调用状态不一致），再通过 `getEffectiveMessages` 应用摘要过滤，最后追加任务描述（`subagents.ts:680-687`）。

**关键机制**是 `EXCLUDED_STATE_KEYS`（`subagents.ts:49-57`）：在将状态传递给子代理和从子代理返回更新时，`messages`、`todos`、`structuredResponse`、`skillsMetadata`、`memoryContents`、`_summarizationEvent`、`_summarizationSessionId` 这7个键被过滤。这意味着：

- 子代理有自己独立的 messages 通道（不污染父代理对话）
- 子代理的 todos 不回传父代理（避免任务列表冲突）
- 摘要相关的 cutoffIndex 不跨代理共享（因为它们只对各自的消息列表有效）
- 但自定义 state 字段（如用户通过 stateSchema 定义的字段）会透传，允许父子共享业务数据

此外，子代理还获得独立的 `_summarizationSessionId`（`subagents.ts:691`，格式为 `session_{8位UUID}`），确保摘要中间件的会话追踪不会串扰。general-purpose 子代理是特殊的——它继承主代理的 skills 和 tools，是唯一默认存在的子代理（`agent.ts:385-411`）。

## 3. 可插拔后端抽象：从 StateBackend 到 Sandbox 的统一文件操作协议

deepagentsjs 将所有文件操作抽象为 `BackendProtocolV2` 接口，实现了**存储后端与 agent 逻辑的完全解耦**。核心设计体现在三个层面：

**协议版本化**（`backends/protocol.ts`）：定义了 v1（已废弃，content 为 `string[]` 行数组，仅文本）和 v2（当前，content 为 `string | Uint8Array`，支持二进制和 mimeType）两种文件数据格式，并提供 `adaptBackendProtocol` 将 v1 后端适配为 v2。`StateBackend` 同时支持两种格式（`state.ts:61`，通过 `fileFormat` 选项控制）。

**后端多样性**（`backends/index.ts:55-78`）：
- `StateBackend`：默认后端，文件存储在 LangGraph state 中，随 checkpoint 持久化，通过 Pregel 内部的 `__pregel_send`/`__pregel_read` 通道进行状态更新（`state.ts:45-46,133-144`），零外部依赖。
- `FilesystemBackend`：直接操作本地文件系统，适合 Node.js 环境。
- `StoreBackend`：基于 LangGraph BaseStore 的长期存储，跨线程持久化。
- `CompositeBackend`：组合多个后端，按路径前缀路由。
- `ContextHubBackend`、`LangSmithSandbox`、`LocalShellBackend`：远程/沙箱执行环境。

**中间件与后端的桥接**：所有需要文件操作的中间件（filesystem、memory、skills、summarization）都通过 `resolveBackend` 获取后端实例，接受 `AnyBackendProtocol | BackendFactory | ((config) => StateBackend)` 三种形式。后端工厂函数接收 `{ state, store }` 运行时配置，使得同一个后端定义可以在不同执行上下文中实例化。

文件状态通过 `filesValue`（`values.ts:34-40`）这个预配置的 `ReducedValue` 管理，其 reducer 支持并发更新合并和 null 值删除——这使得并行子代理可以安全地同时写入文件系统，由 LangGraph 的状态归约机制保证一致性。
