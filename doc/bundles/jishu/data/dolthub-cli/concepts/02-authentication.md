---
type: Concept
title: "认证与凭据管理"
description: "dh 的 OAuth PKCE 浏览器登录、keyring/文件双源凭据存储、token 自动刷新与敏感信息脱敏，对应 F-022~F-031、F-060"
tags: [dh, dolthub, cli, oauth, pkce, credentials, security]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-09-09" }
verified: { by: "process:seven-concepts-v", at: "2026-09-09" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: dh-cli-source
    resource: /references/source.md
    title: "dh CLI 源码事实登记"
---

# 认证与凭据管理

> 本文档拆解 `dh` 的认证链路：OAuth PKCE 浏览器登录、双源凭据存储、token 自动刷新与安全脱敏。对应 [F-022~F-031、F-060](/references/source.md)。

CLI 的难点往往不在"发 HTTP 请求"，而在"安全地管理身份"。`dh` 的凭据子系统（`internal/credentials` + `internal/oauth` + `internal/authflow` + `internal/httptransport`）占了相当比重，是观察"生产级 CLI 身份工程"的绝佳样本。

## 认证方式

`dh` 支持两种认证（F-024、F-029）：

| 方式 | 说明 |
|------|------|
| 浏览器登录 `dh auth login` | OAuth 授权码 + PKCE，无 client secret |
| 环境变量 `DH_TOKEN` | 静态 token，优先级最高，登录时需先 unset（F-060） |

## OAuth PKCE 浏览器登录

生产构建内置了公开的 OAuth client ID（`productionOAuthClientID`），可用 `DH_OAUTH_CLIENT_ID` 覆盖；非生产 host 必须显式配置（F-029）。

流程（F-028、F-030）：

1. `oauth.Client.NewAuthorization` 生成 state（32 字节随机）+ PKCE verifier，计算 S256 challenge，拼出 `/oauth/authorize` URL
2. `BrowserAuthenticator` 启动本地 loopback HTTP server（默认 `http://localhost:53682/callback`），打开浏览器
3. 回调校验 state 一致性、提取授权码
4. `ExchangeCode` 用 `code` + `verifier` 换 token（端点 `/api/oauth/access_token`）
5. `CurrentUsername` 用 access token 调 `/api/v2/user` 校验身份

登录成功后 `SetOAuthTokenPreferred` 存凭据、`SetActiveUser` 记用户、`Write` 落配置；任何一步失败都 rollback 凭据与配置（F-060）。

## 凭据存储：双源回退

`Store` 接口只有 Get/Set/Delete 三方法（F-022），但实现了"来源"概念——`SourceKeyring`（系统钥匙串）与 `SourceFile`（JSON 文件）两种（F-022）。

- `KeyringStore`：用 go-keyring，service 名 `"dh"`，account 形如 `host:user`（F-023）
- `FileStore`：存 `os.UserConfigDir()/dh/credentials.json`，非 Windows 要求目录 0700、文件 0600（F-025）
- `FallbackStore`：读优先文件、写优先 keyring；keyring 不可用时回退文件并打印"未加密保存"警告（F-026）
- `EnvironmentStore`：让 `DH_TOKEN` 优先（F-024）

OAuth 凭据作为"版本化 secret"整体序列化——`OAuthToken` 以 `dh.oauth.v1:` 前缀 + JSON 存为单个值（F-027），包含 access token、refresh token、token type、过期时间。

## token 自动刷新

`TokenSource` 负责"加载 + 至多刷新一次"（F-031）：

- access token 未过期（默认 skew 1 分钟）直接返回
- 过期则用 refresh token 调 `Refresh` 轮换
- **轮换后先持久化新凭据，再返回新 token**——避免"refresh token 的后继已丢失却还在用旧 token"的竞态

## 安全边界（洞察）

`dh` 在凭据安全上做了大量"看似多余"的防御：

| 防御 | 位置 | 作用 |
|------|------|------|
| `safeServerText` | `dolthub` | 过滤控制字符 + 正则 `(?i)bearer\s+[^\s]+` 脱敏为 `Bearer [REDACTED]`（F-038） |
| `ExchangeError` | `oauth` | 不保留服务器自由文本（可能回显凭据）（F-038） |
| 同源校验 | `resolveSameOrigin` | 防止带凭据客户端向异源发送 token（F-033） |
| 权限 0600/0700 | `FileStore`/`config.File` | 非 Windows 强制收紧凭据文件权限（F-025） |

这些防御的共性：把"凭据绝不外泄"作为第一优先级，宁可多写校验代码，也不依赖"调用方不会传坏数据"的假设。

## 相关概念

* [dh CLI 架构与分层](/concepts/01-architecture.md)
* [SQL 查询与表导入](/concepts/03-sql-and-import.md)
