---
type: reference
scope: openwiki
name: api
version: "0.3.3"
source: https://github.com/langchain-ai/openwiki
description: OpenWiki Agent 与 CLI 公共 API 参考——runOpenWikiAgent、createModel、createAgentBackend 等
---

# Agent API 参考

## Agent 运行入口

### runOpenWikiAgent

```typescript
runOpenWikiAgent(
  command: OpenWikiCommand,
  cwd?: string,
  options?: OpenWikiRunOptions,
  telemetryContext?: RunTelemetryContext,
): Promise<OpenWikiRunResult>
```

完整的持久化运行入口。负责环境加载、skills 同步、Claims 预检、update no-op 检测、provider 解析、模型创建、agent 流式执行、wiki 替换事务、元数据持久化和临时文件清理。

**参数：**

| 参数 | 类型 | 说明 |
|---|---|---|
| `command` | `"chat" \| "init" \| "update"` | 运行命令 |
| `cwd` | `string` | 工作目录，默认为 `openWikiLocalWikiDir` |
| `options` | `OpenWikiRunOptions` | 运行选项 |
| `telemetryContext` | `RunTelemetryContext` | 遥测上下文，provider/outcome 在此记录 |

**返回值：** `OpenWikiRunResult`，包含 `command`、`model`（model ID）、可选 `skipped`（no-op 时为 true）。

**关键行为：**
- update 无用户消息时执行 no-op 检测，无实质变更直接返回 `{ skipped: true }`。
- repository init 时启动 wiki 替换事务，失败自动 rollback。
- ChatGPT OAuth provider 在模型创建前刷新过期 token。
- 流失败时尽力写入 `"interrupted"` 状态元数据。

### createOpenWikiAgent

```typescript
createOpenWikiAgent(
  options: OpenWikiAgentOptions,
): Promise<ReturnType<typeof createDeepAgent>>
```

低层工厂，从已初始化的 chat model 创建 DeepAgent 图。不拥有持久化元数据和 Claims finalization。

**参数 `OpenWikiAgentOptions`：**

| 字段 | 类型 | 说明 |
|---|---|---|
| `command` | `OpenWikiCommand` | 命令模式 |
| `cwd` | `string` | 绝对路径工作目录（非绝对路径抛错） |
| `language` | `string \| null` | 输出语言 |
| `model` | `BaseChatModel` | 已初始化的 LangChain chat model |
| `onEvent` | `(event: OpenWikiRunEvent) => void` | 事件回调 |
| `outputMode` | `"local-wiki" \| "repository"` | 输出模式 |

## 模型工厂

### createModel

```typescript
createModel(
  provider: OpenWikiProvider,
  modelId: string,
  providerRetryAttempts: number,
  maxOutputTokens?: number,
  streamIdleTimeout?: number,
): BaseChatModel
```

根据 provider 创建对应的 LangChain chat model 实例（同步函数）。

**支持的 Provider：**

| Provider | 模型类 | 认证方式 | 特殊处理 |
|---|---|---|---|
| `openai` | `ChatOpenAI` | `OPENAI_API_KEY` | Responses API 按模型判定 |
| `anthropic` | `ChatAnthropic` | `ANTHROPIC_API_KEY` | Claude 4/5 默认 16384 max tokens |
| `gemini` | `ChatGoogle` (gai) | `GEMINI_API_KEY` | 禁用流式，outputVersion v0 |
| `gemini-enterprise` | 三种 surface | ADC + project | 按模型 ID 路由 |
| `openai-chatgpt` | `ChatOpenAI` | OAuth tokens | Codex Responses API，强制流式 |
| `openrouter` | `ChatOpenRouter` | `OPENROUTER_API_KEY` | siteName="OpenWiki" |
| `bedrock` | `ChatBedrockConverse` | AWS SDK 凭证链 | stream idle timeout |
| `openai-compatible` | `ChatOpenAI` | 自定义 API key | 默认 "updates" stream mode |
| `baseten`/`fireworks`/`nvidia`/`copilot`/`nebius` | `ChatOpenAI` | API key + base URL | OpenAI 兼容 |

**Gemini Enterprise 三种 surface（`resolveVertexSurface(modelId)`）：**
- `"anthropic"`：`ChatAnthropic` + `AnthropicVertex` ADC 桥接，`dangerouslyAllowBrowser: true`（绕过 jsdom DOM 检测）。
- `"openai-maas"`：`ChatOpenAI` 指向 Vertex OpenAI 兼容端点，`createVertexAuthFetch` 每请求注入 ADC bearer token。
- 默认：`ChatGoogle` (gcp)，强制 ADC（空 apiKey 阻止 API key 回退）。

### resolveModelId

```typescript
resolveModelId(
  options: OpenWikiRunOptions,
  provider: OpenWikiProvider,
): string
```

解析模型 ID，优先级：`options.modelId` > `OPENWIKI_MODEL_ID` 环境变量 > provider 默认模型。校验 ID 合法性，对模型属于其他 provider 的情况发出非致命警告。

## Backend 与权限

### createAgentBackend

```typescript
createAgentBackend(
  wikiBackend: OpenWikiLocalShellBackend,
  options?: {
    historyDir?: string;
    skillsDir?: string;
  },
): CompositeBackend
```

创建组合文件系统后端，挂载三个虚拟层：

| 挂载点 | 后端 | 物理路径 | 用途 |
|---|---|---|---|
| `/` | `OpenWikiLocalShellBackend` | wiki 根目录 | 文档读写 |
| `/conversation_history/` | `FilesystemBackend` | `~/.openwiki/conversation_history` | 摘要中间件历史卸载 |
| `/skills/` | `FilesystemBackend` | `~/.openwiki/skills` | Agent 技能加载 |

### AGENT_FILESYSTEM_PERMISSIONS

```typescript
const AGENT_FILESYSTEM_PERMISSIONS: FilesystemPermission[]
```

Agent 文件系统权限，拒绝对 `/skills/**` 和 `/conversation_history/**` 的 write 操作。Skills 由 CLI 安装，conversation history 仅摘要中间件可通过 backend 直接写入。

### CONVERSATION_HISTORY_MOUNT

```typescript
const CONVERSATION_HISTORY_MOUNT = "/conversation_history/"
```

对话历史虚拟挂载前缀，需与 deepagents 默认的 `"/conversation_history"` 保持同步。

## Checkpoint

### resolveCheckpointTarget

```typescript
resolveCheckpointTarget(command: OpenWikiCommand): CheckpointTarget
```

| 命令 | connString | persistent |
|---|---|---|
| `chat` | `~/.openwiki/openwiki.sqlite` | `true` |
| `init`/`update` | `":memory:"` | `false` |

### pruneCheckpointHistory

```typescript
pruneCheckpointHistory(
  checkpointer: SqliteSaver,
  threadId: string,
): void
```

在 SQLite 事务中删除每个 checkpoint namespace 的非最新行及其关联 writes，防止 chat 会话 sqlite 文件无限增长。

### createOpenWikiThreadId

```typescript
createOpenWikiThreadId(cwd?: string): string
```

生成线程 ID，格式 `openwiki-<32位SHA-256(cwd)>-<base36时间戳>-<随机串>`。

## 流式事件

### parseAgentStreamChunk

```typescript
parseAgentStreamChunk(chunk: unknown): OpenWikiRunEvent | null
```

将 LangGraph stream chunk 三元组 `[namespace, mode, payload]` 解析为 `OpenWikiRunEvent`。支持 `messages`（文本提取）和 `tools`（工具开始/结束）模式。

### parseStreamEvent

```typescript
parseStreamEvent(chunk: unknown): OpenWikiRunEvent | null
```

解析 Agent Protocol 事件（`@langchain/protocol` 的 `Event` 类型），支持 `messages` 和 `tools` method。

### OpenWikiRunEvent 类型

```typescript
type OpenWikiRunEvent =
  | { source?: "main" | "subgraph"; type: "text"; text: string }
  | { type: "tool_start"; call: string; id: string; input: unknown; name: string }
  | { type: "tool_end"; id: string; name: string; status: "error" | "finished" }
  | { type: "debug"; message: string }
```

### OpenWikiRunOptions 类型

```typescript
type OpenWikiRunOptions = {
  debug?: boolean;
  isFollowup?: boolean;
  language?: string | null;
  modelId?: string | null;
  onEvent?: (event: OpenWikiRunEvent) => void;
  outputMode?: OpenWikiOutputMode;
  threadId?: string;
  userMessage?: string | null;
  telemetryFile?: string;
}
```

## 工具函数

### sanitizeOpenRouterResponseBody

```typescript
sanitizeOpenRouterResponseBody(body: string): string
```

使用正则匹配 JSON key 中含 secret 关键词的字符串值，替换为 `"[REDACTED]"`。用于 OpenRouter 调试输出脱敏。

### formatEnvironmentDebugValue

```typescript
formatEnvironmentDebugValue(
  key: string,
  value: string | undefined,
): string
```

格式化环境变量用于 debug 输出：
- API key 仅显示 `set(length=N)`。
- URL 去除认证信息和查询参数。
- 非敏感配置显示值。
- 长值显示前6后4预览。

## CLI Runners

### runPrintCommand

```typescript
runPrintCommand(
  command: Extract<CliCommand, { kind: "run" }>,
): Promise<void>
```

非交互模式（`--print` 或非 TTY）运行入口。通过 `withRunTelemetry` 包裹，code 模式先执行 repo setup 和 connector pull，然后调用 `runOpenWikiAgent`，收集 text 事件输出到 stdout。

### runAuthCommand

```typescript
runAuthCommand(
  command: Extract<CliCommand, { kind: "auth" }>,
): Promise<void>
```

处理 `openwiki auth` 子命令：`list`（列出 provider）、`configure`（配置连接器）、`tools`（发现 MCP 工具）、默认（OAuth 认证 + 自动配置 + 工具发现）。

### runNgrokCommand

```typescript
runNgrokCommand(
  command: Extract<CliCommand, { kind: "ngrok" }>,
): Promise<void>
```

调用 `startNgrokTunnel` 启动 ngrok 内网穿透。

### writePrintAuthFix

```typescript
writePrintAuthFix(error: unknown, message: string): void
```

在非交互模式失败时，向 stderr 写入认证错误的分步修复指引。

### writePrintErrorDiagnostics

```typescript
writePrintErrorDiagnostics(error: unknown): void
```

向 stderr 写入结构化错误诊断信息。

## CLI Guards

### isRecord

```typescript
isRecord(value: unknown): value is Record<string, unknown>
```

类型守卫，判断值为非 null 对象。

### isDiagnosticValue

```typescript
isDiagnosticValue(value: unknown): value is string | number | boolean
```

类型守卫，判断值为可安全渲染的标量（string/number/boolean）。

## CLI Startup

### resolveStartupCommand

```typescript
resolveStartupCommand(
  command: CliCommand,
  options?: { cwd?: string; isStdinTTY?: boolean },
): Promise<CliCommand>
```

启动前守卫检查：
1. 交互 chat 无 TTY → 返回 error 命令。
2. 非交互 start 缺凭证 → 返回 error 命令（clean update no-op 例外）。
3. 空用户消息 → 返回 error 命令。
4. 否则原样返回 command。

## CLI Format

| 函数 | 说明 |
|---|---|
| `isExitMessage(message: string): boolean` | 判断是否为 `/exit` 命令 |
| `formatCount(count, singular, plural): string` | 单复数格式化 |
| `formatCwd(cwd: string): string` | HOME 前缀缩写为 `~` |
| `getDisplayModelId(modelId): string` | 解析显示用 model ID |

## CLI Debug

| 函数 | 环境变量 | 说明 |
|---|---|---|
| `isDebugMode()` | `OPENWIKI_DEBUG=1` | 详细 debug 输出 |
| `shouldShowCredentialDiagnostics()` | `OPENWIKI_DEBUG=1` 或 `OPENWIKI_DEBUG_CREDENTIALS=1` | 凭证诊断面板 |

## 版本信息

| 导出 | 说明 |
|---|---|
| `OPENWIKI_VERSION` | 从 package.json 读取的运行时版本 |
| `OPENWIKI_PRODUCER_ACTOR` | `openwiki/<version>`，OKF v0.2 溯源标识 |
