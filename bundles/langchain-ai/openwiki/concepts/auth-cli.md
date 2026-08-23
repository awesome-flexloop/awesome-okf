---
type: concept
scope: openwiki
name: auth-cli
version: "0.3.3"
source: https://github.com/langchain-ai/openwiki
description: OpenWiki Auth 与 CLI 认证体系——OAuth 2.0 PKCE 流程、动态客户端注册、token 刷新与 ngrok 内网穿透
---

# Auth 与 CLI 认证体系

OpenWiki 的认证体系分为两个独立层面：**LLM provider 认证**（API key、OAuth、云 SDK）和**数据源连接器 OAuth**（Slack/Gmail/X/Notion）。本文档聚焦后者，即 `src/auth/` 模块实现的 OAuth 2.0 授权码流程、PKCE、动态客户端注册、token 刷新以及 ngrok 内网穿透机制。

## 认证架构概览

```
┌──────────────────────────────────────────────────┐
│  CLI 命令 (cli.tsx)                              │
│  openwiki auth slack / openwiki ngrok            │
└───────────────┬──────────────────────────────────┘
                │
                ▼
┌──────────────────────────┐   ┌───────────────────┐
│  runners.ts              │   │  startup.ts       │
│  runAuthCommand()        │   │  resolveStartup   │
│  runNgrokCommand()       │   │  Command()        │
└───────┬──────────────────┘   └───────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────┐
│  auth/oauth.ts                                   │
│  runOAuthAuth() ─ PKCE + callback server         │
│  createCallbackServer() ─ 127.0.0.1:53682        │
└───────┬──────────────────┬───────────────────────┘
        │                  │
        ▼                  ▼
┌──────────────────┐  ┌──────────────────────────┐
│  auth/tokens.ts  │  │  auth/ngrok.ts           │
│  getOAuth        │  │  startNgrokTunnel()      │
│  AccessToken()   │  │  ngrok http <port>       │
│  refreshOAuth    │  │  发现随机 HTTPS URL       │
│  AccessToken()   │  └──────────────────────────┘
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────────────────────────┐
│  config/env.ts                                   │
│  loadOpenWikiEnv() / saveOpenWikiEnv()           │
│  ~/.openwiki/.env (0o600, 原子写入)             │
└──────────────────────────────────────────────────┘
```

## OAuth 2.0 PKCE 授权流程

`runOAuthAuth(providerId, options?)` 是 OAuth 认证的入口，实现了带 PKCE 的授权码流程：

### 步骤详解

1. **加载环境与 provider 配置**：`getAuthProvider(providerId)` 获取 `OAuthProviderConfig`，包含 authUrl、tokenUrl、scopes、clientAuth 方式、tokenMapping 等。

2. **启动回调服务器**：`createCallbackServer(provider)` 在 `127.0.0.1:53682`（可配置）启动 HTTP 服务器，返回 `{ close, redirectUri, waitForCode }`。

3. **生成 PKCE 参数**：
   - `code_verifier`：64 字节随机数，base64url 编码。
   - `code_challenge`：SHA-256(code_verifier) 的 base64url 编码，方法 `S256`。
   - `state`：32 字节随机数，base64url 编码，用于 CSRF 防护。

4. **客户端注册**：
   - 静态 provider：从环境变量读取 `clientId`/`clientSecret`。
   - MCP provider（有 `mcpResourceUrl`）：调用 `registerMcpOAuthClient` 做动态注册。

5. **构建授权 URL**：设置 `client_id`、`redirect_uri`、`response_type=code`、`state`、`code_challenge`、`code_challenge_method=S256`、`scope`、`resource`（MCP）。

6. **浏览器授权**：`openBrowser(url)` 跨平台打开浏览器（macOS `open`、Windows `rundll32`、Linux `xdg-open`），macOS 同时 `pbcopy` 复制 URL。

7. **等待回调**：`waitForCode(state)` 返回 Promise，回调到达时解析 `state:code`，严格校验 state 匹配。

8. **交换 token**：POST 到 token endpoint，body 包含 `code`、`code_verifier`、`grant_type=authorization_code`、`redirect_uri`，`client_secret_post` 类型附加 client_secret。

9. **映射与持久化**：`mapTokenResponse` 将 token 响应映射到环境变量键名，`saveOpenWikiEnv` 原子写入 `~/.openwiki/.env`。

### 回调服务器安全

- 仅绑定 `127.0.0.1`，不监听外部接口。
- State 参数在 Promise resolve 时严格比对，不匹配抛出错误。
- 非 `/callback` 路径返回 404。
- OAuth error 参数返回 400 并 reject Promise。
- `close()` 有 1 秒强制关闭定时器，防止浏览器悬挂请求阻塞。

## 动态客户端注册（RFC 7591）

对于 Notion 等 MCP provider，OpenWiki 实现了全自动的 OAuth 客户端发现与注册：

```
MCP Resource URL
      │
      ▼ GET .well-known/oauth-protected-resource (RFC 9728)
Protected Resource Metadata → authorization_servers[0]
      │
      ▼ GET .well-known/oauth-authorization-server (RFC 8414)
Authorization Server Metadata → registration_endpoint
      │
      ▼ POST registration_endpoint
{
  client_name: "OpenWiki",
  grant_types: ["authorization_code", "refresh_token"],
  redirect_uris: [redirectUri],
  response_types: ["code"],
  token_endpoint_auth_method: "none"   ← 公共客户端
}
      │
      ▼
{ client_id: "..." }  ← 后续授权使用此动态 ID
```

所有 endpoint URL 都通过 `validateOAuthEndpointUrl` 校验，限制在 provider 配置的 `oauthAllowedHosts` 白名单内。

## Token 管理与刷新

`tokens.ts` 提供运行时 token 获取，供连接器工具在调用 API 时使用：

### 获取 access token

```typescript
const token = await getOAuthAccessToken("slack");
```

流程：
1. 加载环境变量。
2. 检查缓存的 access token 是否存在且未过期。
3. 未过期直接返回。
4. 过期则调用 `refreshOAuthAccessToken`。

### 刷新 token

`refreshOAuthAccessToken(providerId)`：

1. 读取 refresh token、client ID、client secret。
2. 校验必要凭证存在。
3. 解析 token URL（静态配置或 MCP 动态发现）。
4. POST `grant_type=refresh_token`，MCP provider 附加 `resource` 参数。
5. `mapTokenResponse` 映射新 token，`saveOpenWikiEnv` 持久化。
6. 返回新的 access token。

### 过期判定

`isOAuthAccessTokenExpired(providerId)`：

- 无过期时间 → 返回 `false`（永不过期）。
- 时间戳无法解析 → 返回 `true`（视为过期）。
- 有过期时间 → `timestamp <= Date.now() + 60_000`（提前 1 分钟判定过期，时钟偏移容差）。

### Slack 特殊性

Slack 的 token 响应将用户 token 嵌套在 `authed_user` 对象中：

```json
{
  "authed_user": {
    "access_token": "...",
    "refresh_token": "...",
    "expires_in": 3600,
    "token_type": "..."
  }
}
```

`getTokenValue` 和 `mapTokenResponse` 对 `provider.id === "slack"` 做特殊路径提取。Slack 也是唯一使用 HTTPS redirect URI override 的 provider。

## ngrok 内网穿透

Slack 等 OAuth provider 要求 HTTPS 重定向 URI，本地开发时需要内网穿透。`ngrok.ts` 自动化了这一过程。

### 启动隧道

```typescript
const result = await startNgrokTunnel({
  port: 53682,        // 可选，默认 53682
  url: "openwiki.ngrok.app"  // 可选，预留域名
});
```

**预留域名模式**：
- 验证 URL（https、无端口、无凭证、合法 hostname）。
- 保存 `OPENWIKI_OAUTH_CALLBACK_PORT` 和 `OPENWIKI_HTTPS_OAUTH_REDIRECT_URI` 到 `.env`。
- spawn `ngrok http <port> --url <baseUrl>`。

**随机域名模式**：
- 保存端口，清空 HTTPS redirect URI。
- spawn `ngrok http <port>`。
- 轮询 `http://127.0.0.1:4040/api/tunnels`（每 500ms，超时 15s）。
- 通过 `getRedirectUriFromNgrokTunnels` 发现 HTTPS 转发 URL。
- 发现后保存完整 redirect URI 到 `.env`。

### 隧道发现

`getRedirectUriFromNgrokTunnels(value, port)`：

1. 从 ngrok API 响应的 `tunnels` 数组中筛选 HTTPS 隧道。
2. 排除含凭证/查询/fragment/端口的 public_url。
3. 通过 `config.addr` 匹配目标端口（支持 `"53682"`、`"localhost:53682"`、URL 对象）。
4. 优先返回端口匹配的隧道；仅有一个 HTTPS 隧道时兜底返回。
5. 返回 `<baseUrl>/callback`。

### 与 OAuth 流程的集成

`oauth.ts` 的 `getProviderRedirectUri` 读取环境变量：

- Slack provider 使用 `OPENWIKI_HTTPS_OAUTH_REDIRECT_URI`（ngrok 配置的外网地址）。
- 其他 provider 使用本地 `http://127.0.0.1:<port>/callback`。

因此典型工作流为：

```bash
# 终端 1：启动 ngrok（保持运行）
openwiki ngrok --url openwiki.ngrok.app

# 终端 2：运行 OAuth（自动使用 ngrok HTTPS 回调）
openwiki auth slack
```

## CLI 启动守卫

`startup.ts` 的 `resolveStartupCommand` 在运行前执行认证检查：

- **交互 chat 无 TTY**：返回错误，提示使用 `--init`/`--update` 或传入消息。
- **非交互 start 缺凭证**：检查 provider 必需的环境变量，OAuth provider（ChatGPT）检查完整 token 集。返回错误提示在交互终端保存凭证。
- **空用户消息**：返回错误。
- **Clean --print update 例外**：如果 update 无用户消息且 no-op 检测确认可跳过，即使缺凭证也放行（no-op 不需要调用模型）。

## 环境变量安全

- `.env` 文件权限 0o600，目录 0o700，Windows 通过 ACL 限制。
- 原子写入：临时文件（pid + uuid）+ rename，防止写入中断导致凭证丢失。
- `saveOpenWikiEnv` 使用 Promise 队列串行化，避免并发写入竞争。
- Shell 导出的环境变量优先于文件值，且不会被文件保存覆盖（启动时快照 shell 环境）。
- 凭证诊断对密钥做脱敏（`"abcdef...wxyz"`），对 URL 去除认证信息和查询参数。

## 进一步阅读

- [总览](/langchain-ai/openwiki/concepts/overview)
- [Agent 系统](/langchain-ai/openwiki/concepts/agent-system)
- [OAuth 认证与 ngrok 示例](/langchain-ai/openwiki/examples/oauth-ngrok)
- [配置与环境变量参考](/langchain-ai/openwiki/references/env-config)
