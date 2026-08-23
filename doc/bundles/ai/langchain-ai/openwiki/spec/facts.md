# OpenWiki 事实清单

## 项目元信息

F-001: 文件 `package.json` 第2-12行，项目名称为 `openwiki`，版本 `0.3.3`，描述为 "A CLI that uses a DeepAgents documentation agent to generate and maintain an OpenWiki for a codebase."，许可证 MIT，`type: "module"`，要求 Node >=22，CLI 入口 `bin.openwiki` 指向 `./dist/cli/cli.js`。

F-002: 文件 `package.json` 第61-87行，核心依赖包括 `deepagents@1.12.0`、`langchain@^1.5.3`、`@langchain/core@^1.2.4`、`@langchain/openai@^1.5.5`、`@langchain/anthropic@^1.5.1`、`@langchain/google@^0.2.1`、`@langchain/aws@^1.4.2`、`@langchain/openrouter@^0.4.3`、`@langchain/langgraph-checkpoint-sqlite@^1.0.3`、`@modelcontextprotocol/sdk@^1.30.0`、`ink@^5.1.0`、`react@^18.3.1`、`zod@^4.4.3`、`yaml@^2.9.0`、`marked@^18.0.5`、`posthog-node@^5.39.4`。

F-003: 文件 `package.json` 第37-59行，脚本包括 `dev: tsx src/cli/cli.tsx`、`build: tsc -p tsconfig.json && tsc -p tsconfig.client.json`、`test: pnpm run typecheck && pnpm run build && pnpm run coverage`、`typecheck: tsc --noEmit`。测试框架为 vitest。

F-004: 文件 `src/version.ts` 第45-67行，函数 `readOwnVersion()` 从 `import.meta.url` 所在目录向上查找 `name === "openwiki"` 的 `package.json`，读取其 `version` 字段；找不到时返回 `"0.0.0-unknown"`。第73行导出常量 `OPENWIKI_VERSION`。

F-005: 文件 `src/version.ts` 第81行，导出常量 `OPENWIKI_PRODUCER_ACTOR = \`openwiki/${OPENWIKI_VERSION}\``，用于 OKF v0.2 §7 的 `<producer>/<version>` 溯源标识。

## Agent 核心模块（src/agent/）

F-006: 文件 `src/agent/types.ts` 第1行，导出类型 `OpenWikiCommand = "chat" | "init" | "update"`。第2行导出 `OpenWikiOutputMode = "local-wiki" | "repository"`。

F-007: 文件 `src/agent/types.ts` 第4-8行，导出类型 `OpenWikiRunResult = { command: OpenWikiCommand; model: string; skipped?: boolean }`。第10-32行导出联合类型 `OpenWikiRunEvent`，包含 `text`、`tool_start`、`tool_end`、`debug` 四种事件。

F-008: 文件 `src/agent/types.ts` 第34-44行，导出类型 `OpenWikiRunOptions`，字段包括 `debug?`、`isFollowup?`、`language?`、`modelId?`、`onEvent?`、`outputMode?`、`threadId?`、`userMessage?`、`telemetryFile?`。

F-009: 文件 `src/agent/index.ts` 第161-347行，导出异步函数 `runOpenWikiAgent(command, cwd?, options?, telemetryContext?)`，返回 `Promise<OpenWikiRunResult>`。这是完整的持久化运行入口，负责加载环境、同步 skills、Claims 预检、update no-op 检测、provider 解析、模型创建、agent 流式执行、元数据持久化、wiki 替换事务。

F-010: 文件 `src/agent/index.ts` 第466-502行，导出异步函数 `createOpenWikiAgent(options: OpenWikiAgentOptions)`，返回 `Promise<ReturnType<typeof createDeepAgent>>`。这是低层工厂，从已初始化的 chat model 创建 DeepAgent 图，不拥有持久化元数据。

F-011: 文件 `src/agent/index.ts` 第447-454行，导出类型 `OpenWikiAgentOptions = { command; cwd; language?; model: BaseChatModel; onEvent?; outputMode }`。

F-012: 文件 `src/agent/index.ts` 第1309-1480行，导出函数 `createModel(provider, modelId, providerRetryAttempts, maxOutputTokens?, streamIdleTimeout?)`，根据 `OpenWikiProvider` 创建对应的 LangChain chat model 实例。支持的 provider 分支包括：`gemini`（ChatGoogle, gai）、`gemini-enterprise`（createGeminiEnterpriseModel）、`anthropic`（ChatAnthropic）、`openai-chatgpt`（ChatOpenAI + Codex Responses API）、`openrouter`（ChatOpenRouter）、`bedrock`（ChatBedrockConverse），默认分支为 ChatOpenAI（openai/openai-compatible/baseten/fireworks/nvidia/copilot/nebius）。

F-013: 文件 `src/agent/index.ts` 第988-1005行，导出函数 `createAgentBackend(wikiBackend, options?)`，创建 `CompositeBackend`，挂载两个虚拟目录：`/conversation_history/`（FilesystemBackend 指向 `~/.openwiki/conversation_history`）和 `/skills/`（FilesystemBackend 指向 `~/.openwiki/skills`），均为 virtualMode。

F-014: 文件 `src/agent/index.ts` 第952行，导出常量 `CONVERSATION_HISTORY_MOUNT = "/conversation_history/"`。第965-972行导出常量 `AGENT_FILESYSTEM_PERMISSIONS: FilesystemPermission[]`，拒绝对 `/skills/**` 和 `/conversation_history/**` 的 write 操作。

F-015: 文件 `src/agent/index.ts` 第1110-1124行，导出函数 `resolveCheckpointTarget(command)`：`chat` 命令返回持久化 SQLite（`~/.openwiki/openwiki.sqlite`，`persistent: true`）；`init`/`update` 返回内存 SQLite（`":memory:"`，`persistent: false`）。

F-016: 文件 `src/agent/index.ts` 第1136-1138行，导出函数 `createOpenWikiThreadId(cwd?)`，内部调用 `createThreadId(cwd, createRunThreadId())`。`createThreadId` 使用 SHA-256 哈希 cwd 绝对路径，格式为 `openwiki-<32位hex>-<base36时间戳>-<随机串>`。

F-017: 文件 `src/agent/index.ts` 第1052-1090行，导出函数 `pruneCheckpointHistory(checkpointer, threadId)`，在 SQLite 事务中删除每个 checkpoint namespace 中非最新的 checkpoint 行及其关联 writes，防止 chat 会话 sqlite 文件无限增长。

F-018: 文件 `src/agent/index.ts` 第1662-1682行，导出函数 `parseAgentStreamChunk(chunk)`，将 LangGraph stream chunk 三元组 `[namespace, mode, payload]` 解析为 `OpenWikiRunEvent`，区分 `messages` 和 `tools` 模式。第1687-1709行导出 `parseStreamEvent(chunk)` 解析 Agent Protocol 事件。

F-019: 文件 `src/agent/index.ts` 第2357-2369行，导出函数 `sanitizeOpenRouterResponseBody(body)`，使用正则匹配 JSON key 中含 secret 关键词的字符串值并替换为 `"[REDACTED]"`。

F-020: 文件 `src/agent/index.ts` 第2406-2456行，导出函数 `formatEnvironmentDebugValue(key, value)`，对 API key 仅显示长度、对 URL 脱敏认证信息和查询参数、对非敏感配置显示值。

F-021: 文件 `src/agent/index.ts` 第1252-1278行，导出函数 `resolveModelId(options, provider)`，优先级为 `options.modelId` > `OPENWIKI_MODEL_ID` 环境变量 > provider 默认模型，并校验 model ID 合法性、警告 provider/model 不匹配。

F-022: 文件 `src/agent/index.ts` 第533-635行，内部函数 `createOpenWikiAgentGraph(options)` 调用 `createDeepAgent`，配置 model、tools（connector tools + claims tools）、checkpointer、backend、middleware（翻译中间件、claims 中间件、index 中间件）、skills（`/skills/`）、subagents（review subagents）、permissions、systemPrompt。

F-023: 文件 `src/agent/index.ts` 第536-544行，`OpenWikiLocalShellBackend` 配置为 `docsOnly: command !== "chat"`、`maxOutputBytes: 100_000`、`timeout: 120`、`virtualMode: true`。

F-024: 文件 `src/agent/index.ts` 第1007-1025行，内部类 `OpenWikiCompositeBackend extends CompositeBackend`，重写 `glob()` 方法捕获 `RangeError: Maximum call stack size exceeded`，返回友好的"glob 过宽"错误。

F-025: 文件 `src/agent/index.ts` 第1527-1530行，常量 `GEMINI_THOUGHT_SIGNATURE_OPTIONS = { disableStreaming: true, outputVersion: "v0" }`，用于 Gemini 3.x thought-signature 往返问题。

F-026: 文件 `src/agent/index.ts` 第1545-1560行，内部函数 `resolveAnthropicMaxOutputTokens(modelId, configuredMaxOutputTokens)`，对现代 Claude 4/5 模型（正则 `/^claude-(?:haiku|sonnet|opus)-(?:4|5)/`）默认返回 `DEFAULT_ANTHROPIC_MAX_OUTPUT_TOKENS = 16384`。

F-027: 文件 `src/agent/index.ts` 第1569-1660行，内部函数 `createGeminiEnterpriseModel` 根据 `resolveVertexSurface(modelId)` 分三种 surface：`"anthropic"`（ChatAnthropic + AnthropicVertex ADC 桥接）、`"openai-maas"`（ChatOpenAI + Vertex OpenAI 兼容端点 + auth fetch）、默认（ChatGoogle gcp + ADC）。

F-028: 文件 `src/agent/index.ts` 第1492-1506行，内部异步函数 `ensureFreshChatGptTokens()`，启动时检查 ChatGPT OAuth token 是否过期，过期则用 refresh token 刷新并通过 `saveOpenWikiEnv` 写回 `~/.openwiki/.env`，同步更新 `process.env`。

## Agent 工具模块（src/agent/utils.ts）

F-029: 文件 `src/agent/utils.ts` 第60-82行，导出异步函数 `createRunContext(cwd, outputMode?, language?)`，读取上次更新元数据、解析有效语言（请求语言 > wiki 持久化语言 > "en"）、读取 wiki goal，返回 `RunContext`。

F-030: 文件 `src/agent/utils.ts` 第111-180行，导出异步函数 `getUpdateNoopStatus(cwd, openWikiIgnore?, requestedLanguage?)`，判断 update 是否可跳过模型调用。跳过条件：上次更新 git head 存在、状态非 interrupted、语言未变、worktree 无有意义变更、git head 未变或仅 openwiki/ignored 路径变更。返回 `UpdateNoopStatus` 联合类型。

F-031: 文件 `src/agent/utils.ts` 第182-184行，导出函数 `shouldCheckUpdateNoop(options)`，当 `options.userMessage` 为空或纯空白时返回 true。

F-032: 文件 `src/agent/utils.ts` 第191-215行，导出异步函数 `writeLastUpdateMetadata(command, cwd, modelId, outputMode?, status?, language?)`，写入 `.last-update.json`（repository 模式在 `openwiki/.last-update.json`，local-wiki 模式在 `.last-update.json`），包含 updatedAt、command、gitHead、model、status、language。

F-033: 文件 `src/agent/utils.ts` 第225-248行，导出异步函数 `persistRunMetadataIfChanged(...)`，chat 命令或 snapshot 为 null 时返回 false，否则调用 `writeLastUpdateMetadata` 并返回 true。

F-034: 文件 `src/agent/utils.ts` 第257-276行，导出异步函数 `removeTemporaryWorkingFiles(cwd, outputMode)`，删除 wiki 根目录下的 `_plan.md` 和 `_skeleton.md`，返回被删除文件名列表。

F-035: 文件 `src/agent/utils.ts` 第281-291行，导出异步函数 `createOpenWikiContentSnapshot(cwd, outputMode?)`，递归遍历 wiki 目录，对文件路径和内容计算 SHA-256 哈希，返回 hex 摘要。排除 `.last-update.json` 和临时工作文件。

F-036: 文件 `src/agent/utils.ts` 第32行，常量 `TEMPORARY_WORKING_FILES = ["_plan.md", "_skeleton.md"]`。第31行常量 `LOCAL_WIKI_METADATA_PATH = ".last-update.json"`。

## Auth 模块（src/auth/）

F-037: 文件 `src/auth/types.ts` 第1行，导出类型 `AuthProviderId = "gmail" | "notion" | "slack" | "x"`。第3行导出 `OAuthClientAuth = "client_secret_post" | "none"`。

F-038: 文件 `src/auth/types.ts` 第5-18行，导出类型 `OAuthProviderConfig`，字段包括 `id`、`displayName`、`scopes`、`clientAuth`、`authUrl?`、`tokenUrl?`、`clientIdEnvKey?`、`clientSecretEnvKey?`、`extraAuthParams?`、`mcpResourceUrl?`、`oauthAllowedHosts?`、`tokenMapping`。第20-26行导出 `OAuthTokenMapping`。

F-039: 文件 `src/auth/types.ts` 第28-34行，导出类型 `OAuthClientRegistration = { authUrl; clientAuth; clientId; clientSecret?; tokenUrl }`。第36-39行导出 `OAuthRunResult = { provider; savedEnvKeys }`。

F-040: 文件 `src/auth/oauth.ts` 第47-105行，导出异步函数 `runOAuthAuth(providerId, options?)`，返回 `Promise<OAuthRunResult>`。流程：加载环境 → 创建回调服务器 → 生成 state（32字节）和 PKCE code_verifier（64字节）→ 解析客户端注册 → 构建授权 URL → 打开浏览器/复制剪贴板 → 等待回调 code → 交换 token → 映射并保存环境变量。

F-041: 文件 `src/auth/oauth.ts` 第31-35行，常量 `CALLBACK_HOST = "127.0.0.1"`、`CALLBACK_PATH = "/callback"`、`DEFAULT_CALLBACK_PORT = 53682`、`OAUTH_CALLBACK_PORT_ENV_KEY = "OPENWIKI_OAUTH_CALLBACK_PORT"`、`HTTPS_OAUTH_REDIRECT_URI_ENV_KEY = "OPENWIKI_HTTPS_OAUTH_REDIRECT_URI"`。

F-042: 文件 `src/auth/oauth.ts` 第385-467行，导出异步函数 `createCallbackServer(provider)`，创建 HTTP 服务器监听回调端口，返回 `{ close, redirectUri, waitForCode }`。`waitForCode` 校验 state 匹配后返回 authorization code。非 `/callback` 路径返回 404。

F-043: 文件 `src/auth/oauth.ts` 第154-243行，内部异步函数 `registerMcpOAuthClient(provider, redirectUri)`，实现 RFC 7591 动态客户端注册：发现 Protected Resource Metadata → Authorization Server Metadata → POST registration_endpoint（client_name="OpenWiki", grant_types=["authorization_code","refresh_token"], token_endpoint_auth_method="none"），返回注册的 client_id。

F-044: 文件 `src/auth/oauth.ts` 第334-383行，内部函数 `mapTokenResponse(provider, registration, tokenResponse)`，Slack 从 `authed_user` 嵌套对象提取 token，其他 provider 从顶层提取。将 access_token、refresh_token、token_type、expires_in（转为 ISO 时间戳）、client_id 映射到环境变量键名。

F-045: 文件 `src/auth/oauth.ts` 第619-625行，内部函数 `createRandomUrlToken(byteLength=32)` 使用 `randomBytes(byteLength).toString("base64url")`；`createCodeChallenge(codeVerifier)` 使用 `createHash("sha256").update(codeVerifier).digest("base64url")`（S256）。

F-046: 文件 `src/auth/oauth.ts` 第560-583行，内部异步函数 `openBrowser(url)`：macOS 用 `open`、Windows 用 `rundll32 url.dll,FileProtocolHandler`（避免 cmd start 的 `&` 截断问题）、Linux 用 `xdg-open`。

F-047: 文件 `src/auth/oauth.ts` 第107-122行，导出函数 `formatAuthProviderList()`，返回 Slack/Gmail/X/Notion 四个 auth provider 的帮助文本。

F-048: 文件 `src/auth/tokens.ts` 第32-45行，导出异步函数 `getOAuthAccessToken(providerId)`，先检查缓存的 access token 是否未过期，未过期直接返回，否则调用 `refreshOAuthAccessToken`。

F-049: 文件 `src/auth/tokens.ts` 第47-123行，导出异步函数 `refreshOAuthAccessToken(providerId)`，使用 refresh_token grant 刷新 access token，通过 `saveOpenWikiEnv` 持久化新 token。第30行常量 `REFRESH_EXPIRY_SKEW_MS = 60_000`（提前 1 分钟判定过期）。

F-050: 文件 `src/auth/tokens.ts` 第125-140行，导出函数 `isOAuthAccessTokenExpired(providerId)`，读取 `expiresAtEnvKey` 对应的 ISO 时间戳，与 `Date.now() + 60_000` 比较。无过期时间时返回 false（不过期）。

F-051: 文件 `src/auth/tokens.ts` 第142-155行，导出函数 `getOAuthProviderIdForAccessTokenEnvKey(envKey)`，遍历 gmail/notion/slack/x 四个 provider，返回匹配 accessTokenEnvKey 的 providerId。

F-052: 文件 `src/auth/ngrok.ts` 第23-84行，导出异步函数 `startNgrokTunnel({ port?, url? })`，返回 `Promise<NgrokStartResult>`。功能：保存回调端口和 HTTPS redirect URI 到环境变量 → spawn `ngrok http <port>` 或 `ngrok http <port> --url <baseUrl>` → 随机 URL 模式下轮询 ngrok 本地 API 发现转发地址。

F-053: 文件 `src/auth/ngrok.ts` 第8-10行，常量 `NGROK_API_URL = "http://127.0.0.1:4040/api/tunnels"`、`NGROK_DISCOVERY_TIMEOUT_MS = 15_000`、`NGROK_DISCOVERY_POLL_MS = 500`。

F-054: 文件 `src/auth/ngrok.ts` 第86-103行，导出函数 `getRedirectUriFromNgrokTunnels(value, port)`，从 ngrok API 的 tunnels 数组中筛选 HTTPS 隧道，优先匹配指定端口，返回 `<baseUrl>/callback` 或 null。

F-055: 文件 `src/auth/ngrok.ts` 第105-145行，内部函数 `normalizeNgrokUrl(value)`，验证自定义 ngrok URL：必须 https、不含凭证/查询/fragment/端口、pathname 为空或 `/callback`、hostname 符合 DNS 规范，返回 `{ baseUrl, redirectUri }`。

## CLI 模块（src/cli/）

F-056: 文件 `src/cli/cli.tsx` 第1行 shebang `#!/usr/bin/env node`。第42行在任何运行前调用 `installCrashGuard()` 注册最后兜底的进程级错误处理。

F-057: 文件 `src/cli/cli.tsx` 第44-53行，解析 `process.argv.slice(2)` 得到 `parsedCommand`，`integrations` 和 `mcp` 命令直接分派，其余进入 `runStandardCommand`。

F-058: 文件 `src/cli/cli.tsx` 第60-115行，异步函数 `runStandardCommand`：加载环境 → `resolveStartupCommand` → 检查首次运行通知 → 按 kind 分派 auth/ngrok/cron/ingest/visualize/print/TUI。交互模式使用 Ink `render()` 渲染 `<FirstRunNotice />` + `<App command={command} />`，`exitOnCtrlC: false`。

F-059: 文件 `src/cli/guards.ts` 第6-8行，导出函数 `isRecord(value): value is Record<string, unknown>`，判断 `typeof value === "object" && value !== null`。第16-23行导出 `isDiagnosticValue(value): value is string | number | boolean`。

F-060: 文件 `src/cli/runners.ts` 第47-60行，导出异步函数 `runNgrokCommand(command)`，调用 `startNgrokTunnel`。第65-90行导出 `runVisualizeCommand`（支持静态导出或服务器模式）。第92-129行导出 `runCronCommand`（list/pause/resume/delete）。第150-183行导出 `runIngestCommand`。第185-254行导出 `runAuthCommand`（list/configure/tools/OAuth）。

F-061: 文件 `src/cli/runners.ts` 第260-337行，导出异步函数 `runPrintCommand(command)`，非交互模式运行入口。通过 `withRunTelemetry` 包裹：code 模式先 `ensureCodeModeRepoSetup` 和 `runCodeModeConnectors`，然后调用 `runOpenWikiAgent`，收集 text 事件输出到 stdout。失败时写入 auth fix 和 error diagnostics 到 stderr。

F-062: 文件 `src/cli/runners.ts` 第344-361行，导出函数 `writePrintAuthFix(error, message)`，通过 `getAuthFix` 检测认证错误，向 stderr 写入分步修复指引。第363-375行导出 `writePrintErrorDiagnostics(error)`。

F-063: 文件 `src/cli/startup.ts` 第24-93行，导出异步函数 `resolveStartupCommand(command, options?)`，执行启动前守卫：交互 chat 需要 TTY、非交互 start 需要凭证、用户消息不能为空。对于 `--print` 的 clean update，可通过 `canSkipCleanUpdateBeforeCredentials` 跳过凭证检查。

F-064: 文件 `src/cli/startup.ts` 第95-110行，内部异步函数 `getMissingNonInteractiveProviderEnvKey(provider, env)`，处理 external CLI auth 和 OAuth（ChatGPT token 集）两种非标准凭证方式。

F-065: 文件 `src/cli/debug.ts` 第6-8行，导出函数 `isDebugMode()`，判断 `process.env.OPENWIKI_DEBUG === "1"`。第14-16行导出 `shouldShowCredentialDiagnostics()`，debug 模式或 `OPENWIKI_DEBUG_CREDENTIALS === "1"`。

F-066: 文件 `src/cli/format.ts` 第11-15行，导出函数 `isExitMessage(message)`，判断 trim+lowercase 后是否为 `/exit`。第20-26行导出 `formatCount(count, singular, plural)`。第32-40行导出 `formatCwd(cwd)`，将 HOME 前缀替换为 `~`。第46-52行导出 `getDisplayModelId(modelId)`，优先级 modelId > env > provider 默认。

## Config 模块（src/config/）

F-067: 文件 `src/config/env.ts` 第78-79行，导出 `openWikiEnvDir = openWikiHomeDir`（即 `~/.openwiki`）和 `openWikiEnvPath = path.join(openWikiEnvDir, ".env")`。

F-068: 文件 `src/config/env.ts` 第99-163行，导出常量 `MANAGED_ENV_KEYS`（readonly 数组），包含 60+ 个 OpenWiki 读取或持久化的环境变量键名，按写入 `.env` 的顺序排列，是凭证诊断和 debug dump 的唯一真相源。

F-069: 文件 `src/config/env.ts` 第178-184行，导出常量 `CREDENTIAL_DIAGNOSTIC_ENV_KEYS`，从 `MANAGED_ENV_KEYS` 派生，将 `OPENWIKI_PROVIDER` 置顶，排除 `LANGCHAIN_PROJECT` 和 `LANGCHAIN_TRACING_V2`。第191-194行导出 `DEBUG_ENV_KEYS = [...MANAGED_ENV_KEYS, "LANGCHAIN_ENDPOINT"]`。

F-070: 文件 `src/config/env.ts` 第262-282行，导出异步函数 `loadOpenWikiEnv()`，捕获 shell 环境快照 → 读取 `.env` 文件 → 仅当 `process.env[key] === undefined` 时填充（shell 导出优先），返回文件环境变量 map。

F-071: 文件 `src/config/env.ts` 第300-311行，导出函数 `saveOpenWikiEnv(updates)`，使用 Promise 队列串行化写入。第313-370行内部函数 `saveOpenWikiEnvLocked` 实现原子写入：mkdir 0o700 → 写临时文件（pid+uuid，0o600）→ rename 覆盖。空值删除键。shell 已导出的键不覆盖 process.env。

F-072: 文件 `src/config/env.ts` 第615-648行，导出函数 `parseEnv(content)`，解析 `.env` 文件格式，支持 `export KEY=value` 语法、双引号转义（`\n`、`\r`、`\"`、`\\`），键名必须匹配 `/^[A-Z_][A-Z0-9_]*$/`。第663-672行导出 `formatEnv(env)`，managed keys 按序排列，其余键按字母排序。

F-073: 文件 `src/config/env.ts` 第284-296行，导出异步函数 `getCredentialDiagnostics()`，返回 `CredentialDiagnostic[]`，每个键包含 key、source（process.env / 文件 / unset）、length、preview（密钥显示前6后4，非敏感显示值）、warnings。

F-074: 文件 `src/config/env.ts` 第241-243行导出 `getShellEnvValue(key)`，第258-260行导出 `getSavedEnvValue(key)`，分别返回启动时 shell 快照和文件快照中的值。

F-075: 文件 `src/config/constants.ts` 第102-115行，导出类型 `OpenWikiProvider`，包含 13 个 provider：`anthropic`、`baseten`、`bedrock`、`copilot`、`fireworks`、`gemini`、`gemini-enterprise`、`nebius`、`nvidia`、`openai`、`openai-chatgpt`、`openai-compatible`、`openrouter`。

F-076: 文件 `src/config/constants.ts` 第99行，导出常量 `DEFAULT_PROVIDER = "openai"`。第68行 `DEFAULT_PROVIDER_RETRY_ATTEMPTS = 3`。第69行 `DEFAULT_ANTHROPIC_MAX_OUTPUT_TOKENS = 16384`。第100行 `OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"`。
