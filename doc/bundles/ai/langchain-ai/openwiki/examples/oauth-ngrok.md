---
type: example
scope: openwiki
name: oauth-ngrok
version: "0.3.3"
source: https://github.com/langchain-ai/openwiki
description: OAuth 认证与 ngrok 内网穿透示例——为 Slack 连接器配置本地 HTTPS 回调并完成 OAuth 授权
---

# OAuth 认证与 ngrok 隧道示例

本示例演示如何为 OpenWiki 的 Slack 连接器配置 OAuth 认证，包括使用 ngrok 进行本地 HTTPS 内网穿透的完整流程。

## 前置条件

- 已安装 OpenWiki CLI（`npm install -g openwiki` 或从源码构建）
- 已安装 [ngrok](https://ngrok.com/) 并在 PATH 中可用
- 已有 Slack 应用并配置了 OAuth client ID/secret
- Node.js >= 22

## 背景：为什么需要 ngrok

Slack OAuth 要求重定向 URI 使用 HTTPS。OpenWiki 的本地回调服务器运行在 `http://127.0.0.1:53682/callback`，无法直接被 Slack 接受。ngrok 将本地端口暴露为 HTTPS 外网地址，桥接这一差距。

```
Slack OAuth ──HTTPS──▶ ngrok tunnel ──▶ 127.0.0.1:53682/callback
```

OpenWiki 自动化了这一过程：`startNgrokTunnel` 启动 ngrok、发现 HTTPS URL、将配置写入 `~/.openwiki/.env`，后续的 `openwiki auth slack` 自动读取该配置。

## 步骤 1：配置 Slack 凭证

首先在 Slack API 控制台创建应用，获取 Client ID 和 Client Secret，然后写入环境变量：

```bash
# 方式一：写入 ~/.openwiki/.env（推荐）
# 文件内容：
# OPENWIKI_SLACK_CLIENT_ID=your-slack-client-id
# OPENWIKI_SLACK_CLIENT_SECRET=your-slack-client-secret

# 方式二：通过 shell 导出
export OPENWIKI_SLACK_CLIENT_ID="your-slack-client-id"
export OPENWIKI_SLACK_CLIENT_SECRET="your-slack-client-secret"
```

## 步骤 2：启动 ngrok 隧道

### 预留域名模式（推荐）

如果你在 ngrok 配置了预留域名（如 `openwiki.ngrok.app`）：

```bash
openwiki ngrok --url openwiki.ngrok.app
```

输出示例：

```
Saved OPENWIKI_HTTPS_OAUTH_REDIRECT_URI=https://openwiki.ngrok.app/callback
Saved OPENWIKI_OAUTH_CALLBACK_PORT=53682
Register this Slack redirect URL: https://openwiki.ngrok.app/callback
Starting ngrok: ngrok http 53682 --url openwiki.ngrok.app
```

此时需要在 Slack 应用设置中将 `https://openwiki.ngrok.app/callback` 添加为重定向 URI。

### 随机域名模式

如果没有预留域名，ngrok 会分配随机 HTTPS 地址：

```bash
openwiki ngrok
```

输出示例：

```
Saved OPENWIKI_OAUTH_CALLBACK_PORT=53682
Cleared OPENWIKI_HTTPS_OAUTH_REDIRECT_URI; ngrok will choose the URL.
Starting ngrok with a random HTTPS forwarding URL.
Starting ngrok: ngrok http 53682
Discovered ngrok redirect URL: https://a1b2c3d4.ngrok-free.app/callback
Saved OPENWIKI_HTTPS_OAUTH_REDIRECT_URI=https://a1b2c3d4.ngrok-free.app/callback
Register this Slack redirect URL: https://a1b2c3d4.ngrok-free.app/callback
```

将发现的 URL 注册到 Slack 应用的重定向 URI 列表中。

> **注意**：随机域名每次 ngrok 重启都会变化，需要重新注册到 Slack。预留域名更稳定。

### 自定义端口

如果默认端口 53682 被占用：

```bash
openwiki ngrok --port 60000 --url openwiki.ngrok.app
```

## 步骤 3：运行 OAuth 认证

保持 ngrok 在终端 1 运行，打开新终端执行：

```bash
openwiki auth slack
```

完整流程：

1. **加载环境**：从 `~/.openwiki/.env` 读取 Slack client ID/secret 和 ngrok 配置的 redirect URI。
2. **启动回调服务器**：在 `127.0.0.1:53682/callback` 监听。
3. **生成 PKCE 参数**：64 字节 code_verifier，S256 code_challenge，32 字节 state。
4. **构建授权 URL**：
   ```
   https://slack.com/oauth/v2/authorize?
     client_id=...&
     redirect_uri=https://openwiki.ngrok.app/callback&
     response_type=code&
     state=...&
     code_challenge=...&
     code_challenge_method=S256&
     scope=...
   ```
5. **打开浏览器**：macOS 用 `open`，Windows 用 `rundll32 url.dll,FileProtocolHandler`，Linux 用 `xdg-open`。
6. **用户授权**：在 Slack 授权页面点击允许。
7. **回调接收**：Slack 重定向到 ngrok HTTPS URL → ngrok 转发到本地 → 服务器接收 code 和 state。
8. **State 校验**：比对回调 state 与生成的 state，不匹配则拒绝（CSRF 防护）。
9. **交换 token**：POST code + code_verifier 到 Slack token endpoint。
10. **保存凭证**：access token、refresh token、过期时间写入 `~/.openwiki/.env`（原子写入，0o600 权限）。
11. **自动配置**：创建连接器配置文件。
12. **工具发现**：自动发现 MCP 工具（如适用）。

成功输出：

```
Saved slack auth values: OPENWIKI_SLACK_USER_TOKEN, OPENWIKI_SLACK_REFRESH_TOKEN, ...
Config created: ~/.openwiki/connectors/slack.json
- ...
Discovered N MCP tool(s); wrote ~/.openwiki/...
Tools: tool1, tool2, ...
```

## 步骤 4：验证认证状态

列出所有 auth provider：

```bash
openwiki auth list
```

输出：

```
Available auth providers:
  slack   Slack OAuth user token for user-visible conversations
  gmail   Gmail read-only OAuth token
  x       X/Twitter OAuth token for timelines, lists, and bookmarks
  notion  Notion hosted MCP OAuth using dynamic client registration
```

## 步骤 5：在 OpenWiki 运行中使用连接器

认证完成后，Slack 连接器工具会在 agent 运行时自动可用。Token 过期时，`getOAuthAccessToken` 自动用 refresh token 刷新（提前 60 秒判定过期），无需重新手动认证。

```bash
# 初始化 wiki（agent 可访问 Slack 数据作为证据源）
openwiki init

# 或更新 wiki
openwiki update
```

## Gmail / X / Notion 的差异

| Provider | 认证方式 | ngrok 需求 | Token 位置 |
|---|---|---|---|
| Slack | OAuth 2.0 + PKCE | 是（HTTPS 回调） | `authed_user` 嵌套 |
| Gmail | OAuth 2.0 + PKCE | 否（本地回调） | 顶层 |
| X/Twitter | OAuth 2.0 + PKCE | 否（本地回调） | 顶层 |
| Notion | MCP 动态注册 + PKCE | 否（本地回调） | 顶层 |

Gmail、X 和 Notion 支持 `http://127.0.0.1` 回调，无需 ngrok：

```bash
openwiki auth gmail
openwiki auth x
openwiki auth notion
```

Notion 使用 RFC 7591 动态客户端注册，无需预先配置 client ID/secret——OpenWiki 自动发现 Notion 的 OAuth 服务器元数据并注册临时客户端。

## 编程式调用

```typescript
import { runOAuthAuth } from "openwiki/auth/oauth.js";
import { startNgrokTunnel } from "openwiki/auth/ngrok.js";
import { getOAuthAccessToken } from "openwiki/auth/tokens.js";

// 启动 ngrok（保持运行）
const tunnel = await startNgrokTunnel({
  url: "openwiki.ngrok.app",
  port: 53682,
});

// 运行 OAuth
const result = await runOAuthAuth("slack", {
  onAuthorizationUrl: ({ url, openedBrowser }) => {
    console.log(`Auth URL: ${url}, opened: ${openedBrowser}`);
  },
  silent: false,
});

console.log(`Saved keys: ${result.savedEnvKeys.join(", ")}`);

// 后续获取 token（自动刷新）
const accessToken = await getOAuthAccessToken("slack");
```

## 故障排查

### ngrok 启动失败

- 确认 ngrok 已安装：`ngrok version`
- 确认端口未被占用：`lsof -i :53682`（macOS/Linux）或 `netstat -ano | findstr :53682`（Windows）
- 预留域名需在 ngrok 账户中配置

### OAuth 回调超时

- 确认 ngrok 进程仍在运行
- 检查 Slack 应用中的重定向 URI 是否与 `OPENWIKI_HTTPS_OAUTH_REDIRECT_URI` 完全一致
- 查看 ngrok Web 界面（`http://127.0.0.1:4040`）检查请求是否到达

### State mismatch 错误

- 不要在多个终端同时运行 OAuth
- 清除浏览器中的旧 OAuth 会话后重试

### Token 刷新失败

- 运行 `openwiki auth slack --force` 重新配置
- 检查 `~/.openwiki/.env` 中的 refresh token 是否完整
- 使用 `OPENWIKI_DEBUG=1 openwiki auth slack` 查看详细日志

## 进一步阅读

- [Auth 与 CLI 认证体系](/ai/langchain-ai/openwiki/concepts/auth-cli)
- [配置与环境变量参考](/ai/langchain-ai/openwiki/references/env-config)
- [Agent API 参考](/ai/langchain-ai/openwiki/references/api)
