---
type: spec
scope: openwiki
name: insights
version: "0.3.3"
source: https://github.com/langchain-ai/openwiki
description: OpenWiki 深度洞察——从源码中提炼的 Agent-CLI 架构、OAuth 令牌管理与 ngrok 内网穿透设计决策
---

# OpenWiki 深度洞察

## 1. Agent-CLI 分层架构：运行入口与图工厂的职责分离

OpenWiki 的 agent 层最显著的设计是**两级 API 分离**：`runOpenWikiAgent` 作为完整的持久化运行边界，而 `createOpenWikiAgent` 作为低层图工厂。这种分离使得 CLI 的交互模式（Ink TUI）和非交互模式（`--print`）可以复用同一个 agent 图，同时各自拥有不同的生命周期管理。

**`runOpenWikiAgent`（高层边界）** 承担了所有横切关注点：

- **环境与 Skills 同步**：启动时 `loadOpenWikiEnv()` 加载 `~/.openwiki/.env`，`syncBundledSkills()` 同步内置 skills。
- **Claims 预检与延迟初始化**：repository init 模式下先执行 wiki 替换再创建 Claims 会话，避免旧 sidecar 被读入全新 wiki；update 模式则 fail-fast 预检。
- **Update no-op 短路**：通过 `getUpdateNoopStatus` 检查 git head、worktree 变更、语言切换、上次 interrupted 状态，无实质变更时跳过模型调用并刷新元数据。
- **Provider 解析与凭证校验**：`resolveRunConfig` 在 agent 构建前完成 provider/model/retry/maxTokens/streamTimeout 的全部解析，并在 ChatGPT OAuth provider 上提前刷新 token，使 `createModel` 保持同步。
- **Wiki 替换事务**：repository init 时通过 `beginRepositoryWikiReplacement` 创建替换上下文，成功 commit、失败 rollback（`AggregateError` 包装双重失败）。
- **崩溃守卫注册**：仅在 stream 消费窗口注册 `registerActiveRun`，使逃逸的运行时错误被标记为 interrupted 而非静默进程中止。
- **元数据持久化**：成功写 `"complete"`，流失败时尽力写 `"interrupted"`，确保下次 update 不会被 no-op 跳过。
- **Checkpoint 清理**：持久化 checkpoint（chat）在每次运行后 `pruneCheckpointHistory`，删除每个 namespace 的非最新行，防止 sqlite 无限增长。

**`createOpenWikiAgent`（低层工厂）** 只做一件事：从已初始化的 `BaseChatModel` 构建 DeepAgent 图。它不碰元数据、不碰 telemetry 边界、不碰凭证刷新，适合测试和编程式调用。

**图构建的关键组合**（`createOpenWikiAgentGraph`，内部函数）：

```
createDeepAgent({
  model,
  tools: [...connectorTools, ...claimsTools],
  checkpointer,           // chat: SQLite 持久化; init/update: 内存
  backend: CompositeBackend,  // wiki backend + /skills/ + /conversation_history/
  middleware: [translation?, claims?, index],
  skills: ["/skills/"],
  subagents: reviewSubagents,
  permissions: AGENT_FILESYSTEM_PERMISSIONS,  // 拒绝写 /skills/** 和 /conversation_history/**
  systemPrompt,
})
```

这种分层的核心收益是：**agent 图本身是纯函数式的组装**，所有副作用（文件系统、环境变量、OAuth、telemetry）都被推到边界层，使得图的创建可在同步上下文中完成，也使得 `--print` 模式和 TUI 模式能通过同一个 `runOpenWikiAgent` 入口获得完全一致的 agent 行为。

**CLI 分派层**（`cli.tsx`）则在更上层做模式选择：TTY 环境下用 Ink `render()` 渲染 React TUI，非 TTY 或 `--print` 下用 `runPrintCommand` 收集 text 事件输出到 stdout。`startup.ts` 的 `resolveStartupCommand` 在分派前执行守卫检查（交互 chat 需要 TTY、非交互需要凭证、消息非空），将错误转化为结构化的 `{ kind: "error" }` 命令。

## 2. OAuth + Token 管理：PKCE 流程、动态客户端注册与统一环境变量持久化

OpenWiki 的 auth 子系统为 Slack、Gmail、X/Twitter、Notion 四个数据源 provider 实现了完整的 OAuth 2.0 授权码流程，其设计围绕**三个核心机制**展开。

### 2.1 PKCE + State 的本地回调服务器

`runOAuthAuth` 的流程遵循 OAuth 2.0 PKCE（RFC 7636）最佳实践：

1. **生成 code_verifier**：64 字节随机数 base64url 编码（远超 RFC 最低 43 字符要求）。
2. **计算 code_challenge**：SHA-256(code_verifier) 的 base64url 编码，方法 `S256`。
3. **生成 state**：32 字节随机数 base64url，防 CSRF。
4. **启动本地 HTTP 服务器**：`createCallbackServer` 监听 `127.0.0.1:53682/callback`（端口可通过 `OPENWIKI_OAUTH_CALLBACK_PORT` 配置）。
5. **构建授权 URL**：设置 client_id、redirect_uri、response_type=code、state、code_challenge、code_challenge_method=S256、scope、resource（MCP provider）。
6. **等待回调**：Promise  resolve 时解析 `state:code`，严格校验 state 匹配后返回 code。
7. **交换 token**：POST 到 token endpoint，body 包含 code、code_verifier、grant_type=authorization_code、redirect_uri，支持 `client_secret_post` 认证。

回调服务器的健壮性设计：非 `/callback` 路径返回 404；error 参数返回 400 并 reject；`close()` 有 1 秒强制关闭定时器和 `closeIdleConnections`，避免浏览器悬挂请求阻塞退出。

### 2.2 MCP 动态客户端注册（RFC 7591）

对于配置了 `mcpResourceUrl` 的 provider（如 Notion），`registerMcpOAuthClient` 实现了自动化的客户端注册：

1. 发现 **Protected Resource Metadata**（RFC 9728）：GET `{mcpResourceUrl}/.well-known/oauth-protected-resource`，获取 `authorization_servers` 列表。
2. 发现 **Authorization Server Metadata**（RFC 8414）：GET `{authServer}/.well-known/oauth-authorization-server`，获取 `authorization_endpoint`、`token_endpoint`、`registration_endpoint`。
3. **动态注册**：POST registration_endpoint，提交 `client_name: "OpenWiki"`、`grant_types: ["authorization_code", "refresh_token"]`、`redirect_uris`、`token_endpoint_auth_method: "none"`（公共客户端，无 secret）。
4. 返回注册获得的 `client_id`，后续授权和 token 刷新使用此动态 client_id。

所有 endpoint URL 都通过 `validateOAuthEndpointUrl` 校验，限制在 `oauthAllowedHosts` 白名单内，防止 SSRF。

### 2.3 Token 刷新与统一持久化

`tokens.ts` 提供运行时 token 获取：

- `getOAuthAccessToken(providerId)`：先检查缓存 token 是否过期（`isOAuthAccessTokenExpired`），未过期直接返回，否则刷新。
- `refreshOAuthAccessToken(providerId)`：使用 refresh_token grant，支持静态 token URL 和 MCP 动态发现的 token endpoint。刷新后通过 `saveOpenWikiEnv` 原子写回 `.env`。
- 过期判定有 **60 秒时钟偏移容差**（`REFRESH_EXPIRY_SKEW_MS`），提前刷新避免临界过期。

**Slack 特殊性**：Slack 的 token 响应嵌套在 `authed_user` 对象中，`mapTokenResponse` 和 `getTokenValue` 对 Slack 做特殊路径提取。Slack 也是唯一使用 HTTPS redirect URI override 的 provider（用于 ngrok 内网穿透，见洞察 3）。

**与 LLM provider 的 OAuth 区分**：auth/ 模块的 OAuth 用于数据源连接器（Slack/Gmail/X/Notion）；而 ChatGPT/Code MODE 的 OAuth 在 `agent/openai-chatgpt-oauth.ts` 中独立实现，通过 `ensureFreshChatGptTokens` 在 agent 启动时单次刷新（CLI 短生命周期进程无需后台刷新循环）。两套体系共用 `saveOpenWikiEnv` 持久化机制但 token 环境变量前缀不同。

## 3. auth-ngrok 内网穿透：本地开发的 HTTPS 回调桥接

OAuth 提供商（尤其是 Slack）通常要求 HTTPS 重定向 URI，而本地开发服务器运行在 `http://127.0.0.1:53682`。`ngrok.ts` 解决了这一矛盾，其设计体现了对开发者体验和安全性的细致考量。

### 3.1 两种隧道模式

`startNgrokTunnel` 支持两种模式：

- **预留域名模式**（`--url` 参数）：用户在 ngrok 配置了预留域名（如 `openwiki.ngrok.app`），spawn `ngrok http <port> --url <baseUrl>`。URL 经过严格验证：必须 https、不含端口/凭证/查询/fragment、hostname 符合 DNS 规范（长度 ≤253，标签正则校验）。
- **随机域名模式**（无 `--url`）：spawn `ngrok http <port>`，ngrok 分配随机 HTTPS 地址。启动后轮询 ngrok 本地 API（`http://127.0.0.1:4040/api/tunnels`），每 500ms 一次，超时 15 秒，通过 `getRedirectUriFromNgrokTunnels` 从 tunnels 数组中找到匹配端口的 HTTPS 隧道。

### 3.2 环境变量桥接

隧道启动后，ngrok 模块将配置写入 `~/.openwiki/.env`：

- `OPENWIKI_OAUTH_CALLBACK_PORT`：本地回调端口。
- `OPENWIKI_HTTPS_OAUTH_REDIRECT_URI`：外网 HTTPS 回调地址（`<baseUrl>/callback`），随机模式下在发现后写入；清除时设为空字符串（`saveOpenWikiEnv` 将空值删除）。

`oauth.ts` 的 `getProviderRedirectUri` 读取这些环境变量：仅 Slack provider 使用 HTTPS override，其他 provider 使用本地 `http://127.0.0.1:port/callback`。这意味着 ngrok 启动后，后续 `openwiki auth slack` 自动使用外网 HTTPS 回调，无需手动配置。

### 3.3 隧道发现的健壮性

`getRedirectUriFromNgrokTunnels` 的筛选逻辑：

1. 过滤出 HTTPS 协议的隧道。
2. 排除含凭证/查询/fragment/端口的 public_url。
3. 通过 `config.addr` 匹配目标端口（支持 `"53682"`、`"localhost:53682"`、URL 对象三种格式）。
4. 优先返回端口匹配的隧道；如果只有一个 HTTPS 隧道则兜底返回它。

ngrok 进程使用 `spawn("ngrok", args, { stdio: "inherit" })` 直接继承终端，用户可看到 ngrok 的实时状态面板。`waitForNgrokExit` 处理正常退出（code 0）和信号终止（SIGINT/SIGTERM），其他退出码 reject 为错误。

### 3.4 安全考量

- ngrok 自定义 URL 强制 HTTPS，禁止在 URL 中嵌入凭证。
- OAuth state 参数在回调时严格校验，即使 ngrok 隧道是公开的，攻击者也无法伪造回调（缺少 state）。
- 回调服务器仅绑定 `127.0.0.1`，不监听外部接口；ngrok 负责外网到本地的转发。
- `.env` 文件权限为 0o600，目录为 0o700，Windows 上通过 `restrictDirToCurrentUser` 设置 ACL。
