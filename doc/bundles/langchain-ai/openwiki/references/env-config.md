---
type: reference
scope: openwiki
name: env-config
version: "0.3.3"
source: https://github.com/langchain-ai/openwiki
description: OpenWiki 配置与环境变量参考——.env 管理、凭证诊断、OAuth 与 provider 配置
---

# 配置与环境变量参考

## 环境文件管理

OpenWiki 所有配置持久化在 `~/.openwiki/.env` 文件中，由 `src/config/env.ts` 统一管理。

### openWikiEnvDir / openWikiEnvPath

```typescript
openWikiEnvDir = openWikiHomeDir   // ~/.openwiki
openWikiEnvPath = "~/.openwiki/.env"
```

### loadOpenWikiEnv

```typescript
loadOpenWikiEnv(): Promise<EnvMap>
```

加载 `.env` 文件到 `process.env`。**shell 导出的环境变量优先**：仅当 `process.env[key] === undefined` 时才从文件填充。首次调用时捕获 shell 环境快照，用于检测值遮蔽。

**行为：**
1. `captureShellEnv()` 快照 shell 中的凭证值（仅首次）。
2. 读取并解析 `.env` 文件。
3. 首次加载时保存文件快照（`savedEnvAtStartup`）。
4. 跳过 deprecated keys（`OPENAI_ORG_ID`、`OPENAI_PROJECT`）。
5. 文件值仅在 process.env 未设置时填充。

### saveOpenWikiEnv

```typescript
saveOpenWikiEnv(updates: EnvMap): Promise<void>
```

原子写入更新到 `.env`。使用 Promise 队列串行化，避免并发写入竞争。

**写入流程：**
1. 读取当前文件内容。
2. 合并 updates（updates 覆盖）。
3. 删除 deprecated keys 和空值（`""` 表示"未设置"）。
4. `mkdir -p ~/.openwiki`（mode 0o700）。
5. 写入临时文件 `<env>.<pid>.<uuid>.tmp`（mode 0o600）。
6. `rename` 临时文件到 `.env`（原子替换）。
7. 更新 `process.env`：shell 已导出的键不覆盖，空值删除。

**安全特性：**
- 临时文件 + rename 防止写入中断（ENOSPC/崩溃）导致凭证文件截断。
- 文件权限 0o600（仅所有者可读写）。
- 目录权限 0o700。
- Windows 通过 `restrictDirToCurrentUser` 设置 ACL。

### parseEnv

```typescript
parseEnv(content: string): EnvMap
```

解析 `.env` 文件格式：
- 跳过空行和 `#` 注释行。
- 支持 `export KEY=value` 语法。
- 键名必须匹配 `/^[A-Z_][A-Z0-9_]*$/`。
- 双引号值支持转义：`\n`、`\r`、`\"`、`\\`。

### formatEnv

```typescript
formatEnv(env: EnvMap): string
```

序列化为 `.env` 格式。Managed keys 按 `MANAGED_ENV_KEYS` 顺序排列，其余键按字母排序。值始终用双引号包裹并转义。

## 受管环境变量

### MANAGED_ENV_KEYS

`MANAGED_ENV_KEYS` 是 OpenWiki 读取或持久化的所有环境变量的唯一真相源（60+ 键），按写入 `.env` 的顺序排列。`CREDENTIAL_DIAGNOSTIC_ENV_KEYS` 和 `DEBUG_ENV_KEYS` 均从此派生，不能静默漂移。

### LLM Provider 配置

| 环境变量 | Provider | 说明 |
|---|---|---|
| `OPENWIKI_PROVIDER` | 全部 | Provider 选择（默认 `openai`） |
| `OPENWIKI_MODEL_ID` | 全部 | 模型 ID 覆盖 |
| `OPENAI_API_KEY` | openai | OpenAI API key |
| `OPENAI_BASE_URL` | openai | OpenAI base URL 覆盖 |
| `ANTHROPIC_API_KEY` | anthropic | Anthropic API key |
| `ANTHROPIC_BASE_URL` | anthropic | Anthropic base URL 覆盖 |
| `GEMINI_API_KEY` | gemini | Google AI Studio API key |
| `GOOGLE_CLOUD_PROJECT` | gemini-enterprise | GCP 项目 ID |
| `GOOGLE_CLOUD_LOCATION` | gemini-enterprise | GCP 区域（默认 `global`） |
| `GOOGLE_APPLICATION_CREDENTIALS` | gemini-enterprise/bedrock | ADC 凭证文件路径 |
| `OPENAI_CHATGPT_ACCESS_TOKEN` | openai-chatgpt | ChatGPT OAuth access token |
| `OPENAI_CHATGPT_REFRESH_TOKEN` | openai-chatgpt | ChatGPT OAuth refresh token |
| `OPENAI_CHATGPT_EXPIRES_AT` | openai-chatgpt | Token 过期时间（ISO） |
| `OPENAI_CHATGPT_ACCOUNT_ID` | openai-chatgpt | ChatGPT account ID |
| `OPENROUTER_API_KEY` | openrouter | OpenRouter API key |
| `BEDROCK_AWS_ACCESS_KEY_ID` | bedrock | AWS access key |
| `BEDROCK_AWS_SECRET_ACCESS_KEY` | bedrock | AWS secret key |
| `BEDROCK_AWS_REGION` | bedrock | AWS region |
| `OPENAI_COMPATIBLE_API_KEY` | openai-compatible | 兼容端点 API key |
| `OPENAI_COMPATIBLE_BASE_URL` | openai-compatible | 兼容端点 base URL |

**OpenAI 兼容网关 Provider：**

| 环境变量 | Provider |
|---|---|
| `BASETEN_API_KEY` / `BASETEN_BASE_URL` | baseten |
| `FIREWORKS_API_KEY` / `FIREWORKS_BASE_URL` | fireworks |
| `NVIDIA_API_KEY` / `NVIDIA_BASE_URL` | nvidia |
| `COPILOT_API_KEY` / `COPILOT_BASE_URL` | copilot |
| `NEBIUS_API_KEY` | nebius（内置 base URL） |

### 运行时调优

| 环境变量 | 默认 | 说明 |
|---|---|---|
| `OPENWIKI_MAX_OUTPUT_TOKENS` | provider 默认 | 最大输出 token |
| `OPENWIKI_PROVIDER_RETRY_ATTEMPTS` | `3` | Provider 重试次数 |
| `OPENWIKI_STREAM_IDLE_TIMEOUT` | provider 默认 | 流式空闲超时（毫秒），Bedrock 支持 0 禁用 |
| `OPENWIKI_REASONING_EFFORT` | — | 推理努力度（low/medium/high） |
| `OPENWIKI_OPENROUTER_MAX_TOKENS` | — | OpenRouter 旧版 max tokens |
| `OPENWIKI_OPENROUTER_PROVIDER_ONLY` | — | OpenRouter provider 路由限制 |
| `OPENWIKI_OPENAI_COMPATIBLE_STREAMING` | — | 强制流式传输 |
| `OPENWIKI_OPENAI_COMPATIBLE_USE_RESPONSES_API` | — | 使用 Responses API |
| `OPENWIKI_OPENAI_COMPATIBLE_STREAM_MESSAGES` | — | 使用 messages stream mode |

### OAuth 连接器配置

| 环境变量 | Provider | 说明 |
|---|---|---|
| `OPENWIKI_SLACK_CLIENT_ID` | slack | Slack OAuth client ID |
| `OPENWIKI_SLACK_CLIENT_SECRET` | slack | Slack OAuth client secret |
| `OPENWIKI_SLACK_USER_TOKEN` | slack | Slack user access token |
| `OPENWIKI_SLACK_BOT_TOKEN` | slack | Slack bot token |
| `OPENWIKI_GMAIL_ACCESS_TOKEN` | gmail | Gmail OAuth access token |
| `OPENWIKI_GMAIL_REFRESH_TOKEN` | gmail | Gmail OAuth refresh token |
| `OPENWIKI_GOOGLE_CLIENT_ID` | gmail | Google OAuth client ID |
| `OPENWIKI_GOOGLE_CLIENT_SECRET` | gmail | Google OAuth client secret |
| `OPENWIKI_GOOGLE_ACCESS_TOKEN` | gmail | Google access token |
| `OPENWIKI_GOOGLE_REFRESH_TOKEN` | gmail | Google refresh token |
| `OPENWIKI_X_CLIENT_ID` | x | X/Twitter OAuth client ID |
| `OPENWIKI_X_CLIENT_SECRET` | x | X/Twitter OAuth client secret |
| `OPENWIKI_X_ACCESS_TOKEN` | x | X access token |
| `OPENWIKI_X_REFRESH_TOKEN` | x | X refresh token |
| `OPENWIKI_NOTION_TOKEN` | notion | Notion token |
| `OPENWIKI_NOTION_MCP_CLIENT_ID` | notion | Notion MCP 动态注册 client ID |
| `OPENWIKI_NOTION_MCP_ACCESS_TOKEN` | notion | Notion MCP access token |
| `OPENWIKI_NOTION_MCP_REFRESH_TOKEN` | notion | Notion MCP refresh token |

### ngrok 与回调

| 环境变量 | 默认 | 说明 |
|---|---|---|
| `OPENWIKI_OAUTH_CALLBACK_PORT` | `53682` | 本地 OAuth 回调端口 |
| `OPENWIKI_HTTPS_OAUTH_REDIRECT_URI` | — | HTTPS 外网回调 URI（Slack + ngrok） |

### 其他

| 环境变量 | 说明 |
|---|---|
| `TAVILY_API_KEY` | Tavily 搜索 API key |
| `LANGSMITH_API_KEY` | LangSmith API key |
| `LANGCHAIN_PROJECT` | LangChain 项目名 |
| `LANGCHAIN_TRACING_V2` | LangSmith 追踪开关 |
| `LANGCHAIN_ENDPOINT` | LangChain endpoint（只读不持久化） |
| `OPENWIKI_DEBUG` | 设为 `1` 启用 debug 输出 |
| `OPENWIKI_DEBUG_CREDENTIALS` | 设为 `1` 仅显示凭证诊断 |

## 凭证诊断

### getCredentialDiagnostics

```typescript
getCredentialDiagnostics(): Promise<CredentialDiagnostic[]>
```

返回所有受管凭证键的诊断信息：

```typescript
type CredentialDiagnostic = {
  key: string;
  source: string;           // "process.env" | "~/.openwiki/.env" | "process.env over ~/.openwiki/.env" | "unset"
  length: number | null;
  preview: string;          // 密钥: "abcdef...wxyz"；非敏感: JSON.stringify(value)
  warnings: string[];       // 空白、换行、引号、括号后缀等
}
```

**非敏感键**（显示明文值）：provider、model ID、max tokens、stream timeout、retry attempts、reasoning effort、boolean 开关、base URL、region、project ID、ADC 路径。

**密钥键**（脱敏）：所有 `*_API_KEY`、AWS access/secret/session token。长度 ≤10 显示等长星号，否则显示前6后4。

**警告类型：**
- `leading/trailing whitespace`
- `contains newline`
- `contains quote character`
- `contains bracketed suffix/text`
- `invalid model ID`
- `invalid provider`
- `invalid boolean`
- `invalid retry attempts`
- `invalid output token limit`
- `invalid stream idle timeout`（Bedrock 0 值警告 watchdog 禁用）
- base URL 格式警告

### getShellEnvValue / getSavedEnvValue

```typescript
getShellEnvValue(key: string): string | undefined
getSavedEnvValue(key: string): string | undefined
```

分别返回启动时 shell 快照和 `.env` 文件快照中的值。用于 setup wizard 预填充字段（避免 shell 遮蔽导致误捕获）。

## OAuth API 参考

### runOAuthAuth

```typescript
runOAuthAuth(
  providerId: AuthProviderId,
  options?: OAuthAuthOptions,
): Promise<OAuthRunResult>
```

执行完整 OAuth 2.0 PKCE 授权流程。`AuthProviderId = "gmail" | "notion" | "slack" | "x"`。

### createCallbackServer

```typescript
createCallbackServer(provider: OAuthProviderConfig): Promise<{
  close: () => Promise<void>;
  redirectUri: string;
  waitForCode: (expectedState: string) => Promise<string>;
}>
```

创建本地 HTTP 回调服务器，监听 `127.0.0.1:<port>/callback`。

### getOAuthAccessToken

```typescript
getOAuthAccessToken(providerId: AuthProviderId): Promise<string>
```

获取有效的 access token，过期时自动刷新。

### refreshOAuthAccessToken

```typescript
refreshOAuthAccessToken(providerId: AuthProviderId): Promise<string>
```

强制刷新 access token 并持久化。

### isOAuthAccessTokenExpired

```typescript
isOAuthAccessTokenExpired(providerId: AuthProviderId): boolean
```

检查 token 是否过期（60 秒提前量）。

### startNgrokTunnel

```typescript
startNgrokTunnel(options: NgrokStartOptions): Promise<NgrokStartResult>
```

启动 ngrok 隧道。`options` 包含 `port?`（默认 53682）和 `url?`（预留域名）。

### getRedirectUriFromNgrokTunnels

```typescript
getRedirectUriFromNgrokTunnels(
  value: unknown,
  port: number,
): string | null
```

从 ngrok API 响应中提取匹配端口的 HTTPS 回调 URL。

## 类型定义

### OAuthProviderConfig

```typescript
type OAuthProviderConfig = {
  id: AuthProviderId;
  displayName: string;
  scopes: string[];
  clientAuth: "client_secret_post" | "none";
  authUrl?: string;
  tokenUrl?: string;
  clientIdEnvKey?: string;
  clientSecretEnvKey?: string;
  extraAuthParams?: Record<string, string>;
  mcpResourceUrl?: string;
  oauthAllowedHosts?: string[];
  tokenMapping: OAuthTokenMapping;
}
```

### OAuthTokenMapping

```typescript
type OAuthTokenMapping = {
  accessTokenEnvKey: string;
  refreshTokenEnvKey?: string;
  expiresAtEnvKey?: string;
  tokenTypeEnvKey?: string;
  clientIdEnvKey?: string;
}
```

## 进一步阅读

- [Agent API 参考](/langchain-ai/openwiki/references/api)
- [Auth 与 CLI 认证体系](/langchain-ai/openwiki/concepts/auth-cli)
- [OAuth 认证与 ngrok 示例](/langchain-ai/openwiki/examples/oauth-ngrok)
