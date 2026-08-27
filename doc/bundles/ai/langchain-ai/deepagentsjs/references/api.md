---
type: reference
scope: deepagentsjs
name: api
version: "1.13.1"
source: https://github.com/langchain-ai/deepagentsjs
description: deepagentsjs 公共 API 参考——createDeepAgent、中间件工厂、后端类、类型定义
---

# API 参考

## createDeepAgent

库的主入口函数，创建并返回一个配置完整的 `DeepAgent` 实例。

```typescript
function createDeepAgent<
  TResponse, ContextSchema, TMiddleware, TSubagents,
  TTools, TStreamTransformers, TStateSchema
>(
  params?: CreateDeepAgentParams<...>
): DeepAgent<DeepAgentTypeConfig<...>>
```

### 参数

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `model` | `BaseLanguageModel \| string` | `"anthropic:claude-sonnet-4-6"` | 使用的模型 |
| `tools` | `(ClientTool \| ServerTool)[]` | `[]` | 用户自定义工具 |
| `systemPrompt` | `string \| SystemMessage \| SystemPromptConfig` | `undefined` | 自定义系统提示词 |
| `stateSchema` | `AnyStateSchema \| InteropZodObject` | `undefined` | 自定义 agent state schema |
| `middleware` | `readonly AgentMiddleware[]` | `[]` | 用户自定义中间件（插入核心与尾部之间） |
| `subagents` | `readonly AnySubAgent[]` | `[]` | 子代理配置数组 |
| `responseFormat` | `SupportedResponseFormat` | `undefined` | 结构化输出格式（Zod schema 等） |
| `contextSchema` | `AnnotationRoot \| InteropZodObject` | `undefined` | 上下文 schema（不跨调用持久化） |
| `checkpointer` | `BaseCheckpointSaver \| boolean` | `undefined` | 状态检查点保存器 |
| `store` | `BaseStore` | `undefined` | 长期记忆存储 |
| `backend` | `AnyBackendProtocol \| BackendFactory` | `StateBackend` 工厂 | 文件操作后端 |
| `interruptOn` | `Record<string, boolean \| InterruptOnConfig>` | `undefined` | 工具中断配置（HITL） |
| `name` | `string` | `undefined` | agent 名称 |
| `memory` | `string[]` | `undefined` | AGENTS.md 文件路径数组 |
| `skills` | `string[]` | `undefined` | 技能源路径数组 |
| `permissions` | `FilesystemPermission[]` | `[]` | 文件系统权限规则 |
| `streamTransformers` | `ReadonlyArray<() => StreamTransformer>` | `[]` | 自定义流式转换器 |

### 返回值

返回 `DeepAgent` 实例，它继承自 langchain 的 `ReactAgent`，额外提供：

- `~deepAgentTypes`：类型品牌，用于 TypeScript 类型推断
- `streamEvents(state, { version: "v3" })`：v3 流式接口，返回 `DeepAgentRunStream`，提供 `messages`、`toolCalls`、`subagents`、`middleware`、`values`、`output` 等投影

### 异常

- `ConfigurationError`（错误码 `TOOL_NAME_COLLISION`）：当用户工具名与内置工具（`ls`、`read_file`、...、`task`、异步任务工具）冲突时抛出。

### 默认中间件栈

创建的 agent 按以下顺序组装中间件：

1. `SkillsMiddleware`（当配置了 skills 时）
2. `FilesystemMiddleware`
3. `SubAgentMiddleware`（注入 `task` 工具）
4. `SummarizationMiddleware`
5. `PatchToolCallsMiddleware`
6. `AsyncSubAgentMiddleware`（当存在 async 子代理时）
7. 用户自定义 middleware
8. Profile extraMiddleware
9. Prompt caching middleware（Anthropic/Bedrock 模型时）
10. `MemoryMiddleware`（当配置了 memory 时）
11. `HumanInTheLoopMiddleware`（当配置了 interruptOn 时）

递归限制固定为 `10,000`。

---

## 中间件工厂函数

### createFilesystemMiddleware

```typescript
function createFilesystemMiddleware(options: {
  backend: AnyBackendProtocol | BackendFactory;
  permissions?: FilesystemPermission[];
  tools?: readonly FsToolName[];
}): AgentMiddleware
```

注入文件系统工具（ls/read_file/write_file/edit_file/delete/glob/grep/execute）。中间件名为 `FilesystemMiddleware`，不可通过 profile 排除。

### createSubAgentMiddleware

```typescript
function createSubAgentMiddleware(options: SubAgentMiddlewareOptions): AgentMiddleware
```

注入 `task` 工具用于子代理委派。中间件名为 `SubAgentMiddleware`，不可排除。

**SubAgentMiddlewareOptions：**

| 字段 | 类型 | 说明 |
|---|---|---|
| `defaultModel` | `LanguageModelLike \| string` | 子代理默认模型 |
| `defaultTools` | `StructuredTool[]` | 默认工具集 |
| `defaultMiddleware` | `AgentMiddleware[] \| null` | 自定义子代理默认中间件 |
| `generalPurposeMiddleware` | `AgentMiddleware[] \| null` | 通用子代理专用中间件（含 skills） |
| `defaultInterruptOn` | `InterruptOnConfig \| null` | 默认 HITL 配置 |
| `subagents` | `(SubAgent \| CompiledSubAgent \| ForkedSubAgent)[]` | 子代理列表 |
| `generalPurposeAgent` | `boolean` | 是否自动添加通用子代理（默认 true） |
| `taskDescription` | `string \| null` | 自定义 task 工具描述 |
| `parentSystemPrompt` | `string \| SystemMessage \| null` | ForkedSubAgent 继承的父系统提示词 |

### createSummarizationMiddleware

```typescript
function createSummarizationMiddleware(
  options: SummarizationMiddlewareOptions
): AgentMiddleware
```

自动在上下文接近限制时摘要旧消息并卸载到后端。

**SummarizationMiddlewareOptions：**

| 字段 | 类型 | 说明 |
|---|---|---|
| `model` | `string \| BaseChatModel` | 摘要模型（默认使用请求模型） |
| `backend` | `BackendProtocol \| BackendFactory` | **必填**，历史卸载后端 |
| `trigger` | `ContextSize \| ContextSize[]` | 触发摘要的阈值 |
| `keep` | `ContextSize` | 摘要后保留策略（默认 20 messages） |
| `summaryPrompt` | `string` | 自定义摘要提示词模板 |
| `trimTokensToSummarize` | `number` | 摘要时最大 token 数 |
| `historyPathPrefix` | `string` | 历史存储路径前缀（默认 `/conversation_history`） |
| `truncateArgsSettings` | `TruncateArgsSettings` | 工具参数截断配置 |

### createMemoryMiddleware

```typescript
function createMemoryMiddleware(options: {
  backend: AnyBackendProtocol | BackendFactory;
  sources: string[];
  addCacheControl?: boolean;
}): AgentMiddleware
```

从 AGENTS.md 文件加载记忆并注入 system prompt。

### createSkillsMiddleware

```typescript
function createSkillsMiddleware(options: {
  backend: AnyBackendProtocol | BackendFactory;
  sources: string[];
}): AgentMiddleware
```

从后端路径加载 Agent Skills（SKILL.md），实现渐进式披露。

### createAsyncSubAgentMiddleware

```typescript
function createAsyncSubAgentMiddleware(options: {
  asyncSubAgents: AsyncSubAgent[];
}): AgentMiddleware
```

注入5个异步任务工具（start/check/update/cancel/list_async_task），通过 LangGraph SDK 与远程 Agent Protocol 服务器通信。

### createPatchToolCallsMiddleware

```typescript
function createPatchToolCallsMiddleware(): AgentMiddleware
```

修补工具调用以确保跨模型提供商的兼容性。

### createCompletionCallbackMiddleware

```typescript
function createCompletionCallbackMiddleware(
  options: CompletionCallbackOptions
): AgentMiddleware
```

异步子代理完成回调中间件。

### createAgentMemoryMiddleware（已废弃）

```typescript
function createAgentMemoryMiddleware(options: {
  settings: Settings;
  assistantId: string;
  systemPromptTemplate?: string;
}): AgentMiddleware
```

**已废弃**，使用 `createMemoryMiddleware` 替代。直接使用 Node.js fs 模块，不可移植。

---

## 子代理相关

### 类型定义

```typescript
interface SubAgent {
  name: string;
  description: string;
  systemPrompt?: string | SystemMessage;
  mode?: "handoff";           // 默认，完全隔离
  tools?: StructuredTool[];
  model?: LanguageModelLike | string;
  middleware?: readonly AgentMiddleware[];
  interruptOn?: Record<string, boolean | InterruptOnConfig>;
  skills?: string[];
  responseFormat?: CreateAgentParams["responseFormat"];
  permissions?: FilesystemPermission[];
}

interface ForkedSubAgent extends SubAgentBase {
  systemPrompt?: undefined;   // 必须无自己的 prompt
  mode: "fork";               // 必须是 fork
}

interface CompiledSubAgent<TRunnable = ReactAgent | Runnable> {
  name: string;
  description: string;
  runnable: TRunnable;
  mode?: "handoff" | "fork";
}

interface AsyncSubAgent {
  name: string;
  description: string;
  graphId: string;            // 远程图名/助手 ID
  url?: string;
  headers?: Record<string, string>;
}

type AnySubAgent = SubAgent | CompiledSubAgent | ForkedSubAgent | AsyncSubAgent;
```

### createSubAgent

```typescript
function createSubAgent(
  spec: SubAgent,
  options?: { responseFormat?: CreateAgentParams["responseFormat"] }
): ReactAgent
```

从声明式 SubAgent spec 编译出 ReactAgent。要求 spec 必须有 `model` 和 `tools`。

### 常量

| 常量 | 值 | 说明 |
|---|---|---|
| `GENERAL_PURPOSE_SUBAGENT` | `{ name: "general-purpose", ... }` | 通用子代理默认配置 |
| `DEFAULT_GENERAL_PURPOSE_DESCRIPTION` | 见源码 | 通用子代理描述文本 |
| `DEFAULT_SUBAGENT_PROMPT` | `"In order to complete..."` | 子代理默认系统提示词 |
| `SUBAGENT_RESPONSE_FORMAT_CONFIG_KEY` | `"__deepagents_subagent_response_format"` | 动态响应格式 config 键 |

---

## 后端类

### StateBackend（默认）

```typescript
class StateBackend implements BackendProtocolV2 {
  constructor(options?: BackendOptions);
  constructor(runtime: BackendRuntime, options?: BackendOptions); // 已废弃
}
```

文件存储在 LangGraph agent state 中，随 checkpoint 持久化。零外部依赖，适合快速开始和无状态部署。

### FilesystemBackend

```typescript
class FilesystemBackend implements BackendProtocolV2 {
  constructor(options: { rootDir: string });
}
```

直接操作本地文件系统，适合 Node.js 环境。

### StoreBackend

```typescript
class StoreBackend implements BackendProtocolV2 {
  constructor(options: StoreBackendOptions);
}
```

基于 LangGraph BaseStore 的长期存储，支持跨线程持久化。

### CompositeBackend

```typescript
class CompositeBackend implements BackendProtocolV2 {
  constructor(backends: Array<{ prefix: string; backend: AnyBackendProtocol }>);
}
```

按路径前缀将操作路由到不同后端。

### LangSmithSandbox

```typescript
class LangSmithSandbox extends BaseSandbox {
  constructor(options: LangSmithSandboxOptions);
}
```

LangSmith 托管沙箱环境，支持快照捕获和恢复。

### LocalShellBackend

```typescript
class LocalShellBackend implements BackendProtocolV2 {
  constructor(options?: LocalShellBackendOptions);
}
```

本地 shell 执行后端。

---

## 状态值

### filesValue

```typescript
const filesValue: ReducedValue<
  z.ZodRecord<z.ZodString, FileDataSchema>,
  z.ZodOptional<z.ZodRecord<z.ZodString, FileDataSchema.Nullable>>
>
```

预配置的文件状态 ReducedValue，可在自定义 StateSchema 中复用：

```typescript
const MyStateSchema = new StateSchema({
  files: filesValue,
  customField: z.string().default(""),
});
```

---

## 权限类型

```typescript
type FilesystemOperation = "read" | "write";
type PermissionMode = "allow" | "deny";

interface FilesystemPermission {
  operations: readonly FilesystemOperation[];
  paths: string[];              // 绝对 glob 模式，以 / 开头
  mode?: PermissionMode;        // 默认 "allow"
}
```

---

## Harness Profile API

```typescript
interface HarnessProfileOptions {
  baseSystemPrompt?: string;
  systemPromptSuffix?: string;
  toolDescriptionOverrides?: Record<string, string>;
  excludedTools?: string[];
  excludedMiddleware?: string[];
  extraMiddleware?: AgentMiddleware[] | (() => AgentMiddleware[]);
  generalPurposeSubagent?: GeneralPurposeSubagentConfig;
}

function createHarnessProfile(options: HarnessProfileOptions): HarnessProfile;
function registerHarnessProfile(spec: string, profile: HarnessProfile): void;
function getHarnessProfile(spec: string): HarnessProfile | undefined;
```

内置注册的 profile：
- `anthropic:claude-sonnet-4-6`（及其他 Anthropic 模型）
- `anthropic:claude-haiku-4-5`
- `anthropic:claude-opus-4-7`
- `openai:gpt-5.1-codex` / `5.2-codex` / `5.3-codex`（自动启用 todoListMiddleware）

`REQUIRED_MIDDLEWARE_NAMES` = `{"FilesystemMiddleware", "SubAgentMiddleware"}`，不可排除。

---

## 错误类

### ConfigurationError

```typescript
class ConfigurationError extends Error {
  constructor(message: string, code: ConfigurationErrorCode);
}
```

错误码包括 `TOOL_NAME_COLLISION`。

---

## 工具名常量

```typescript
const FILESYSTEM_TOOL_NAMES = [
  "ls", "read_file", "write_file", "edit_file",
  "delete", "glob", "grep", "execute"
] as const;

const ASYNC_TASK_TOOL_NAMES = [
  "start_async_task", "check_async_task",
  "update_async_task", "cancel_async_task", "list_async_tasks"
] as const;
```

所有内置工具名（含 `task`）构成保留名集合，用户工具不能使用这些名称。

## 相关阅读

- 总览
- 子代理与规划
- 上下文与 Todo 管理
- 基础 Agent 示例
