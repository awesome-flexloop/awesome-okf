---
type: reference
title: "认证体系参考"
description: "Coze SDK 全部认证方式的 API 参考，包括 TokenAuth、JWTAuth、OAuthApp 及其四种 OAuth 授权流程的同步/异步实现。"
tags: [auth, oauth, jwt, token, pkce, device-flow]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T02:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T02:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: F-cp-002
    resource: /references/auth-model.md
    title: "认证体系参考"
---

# 认证体系参考

本文档登记 Coze Python SDK 的全部认证类与模型，涵盖简单 Token 认证、JWT 认证以及 OAuth 2.0 四种授权流程的同步/异步实现。

## 继承体系总览

```
Auth (基类)
├── SyncAuth (同步认证基类)
│   ├── TokenAuth          — 简单 Token 认证（PAT）
│   ├── JWTAuth            — JWT 认证
│   └── OAuthApp 家族      — OAuth 2.0 应用认证
│       ├── WebOAuthApp
│       ├── PKCEOAuthApp
│       └── DeviceOAuthApp
│
└── AsyncAuth (异步认证基类)
    ├── AsyncTokenAuth     — 异步简单 Token 认证
    ├── AsyncJWTAuth       — 异步 JWT 认证
    └── AsyncOAuthApp 家族 — 异步 OAuth 2.0 应用认证
        ├── AsyncWebOAuthApp
        ├── AsyncPKCEOAuthApp
        └── AsyncDeviceOAuthApp
```

## 简单 Token 认证

### TokenAuth / AsyncTokenAuth

**适用场景**：使用个人访问令牌（Personal Access Token）或已获取的 API Token 直接访问。

```python
from cozepy import TokenAuth, AsyncTokenAuth

auth = TokenAuth(token="your_pat_token_here")
async_auth = AsyncTokenAuth(token="your_pat_token_here")
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `token` | `str` | 个人访问令牌或 API Token |

这是最简单的认证方式，适合服务端脚本、个人工具等场景。

## JWT 认证

### JWTAuth / AsyncJWTAuth

**适用场景**：通过 JWT（JSON Web Token）进行服务端到服务端的认证，适用于企业级 OAuth 应用。

### JWTOAuthApp / AsyncJWTOAuthApp

JWT OAuth 应用类，用于获取和管理基于 JWT 的访问令牌。

## OAuth 基类

### OAuthApp（同步基类）

所有同步 OAuth 应用的基类，封装 OAuth 2.0 通用流程：client_id、client_secret 管理、token 刷新等。

### AsyncOAuthApp（异步基类）

`OAuthApp` 的异步版本，提供相同的接口但使用 async/await。

## Web OAuth 流程

### WebOAuthApp / AsyncWebOAuthApp

**适用场景**：Web 应用授权码（Authorization Code）流程。用户在浏览器中完成授权后，通过回调 URL 获取 authorization_code，再用此 code 换取 access_token。

典型流程：
1. 构造授权 URL，引导用户访问
2. 用户授权后回调至 redirect_uri，携带 code
3. 使用 code 换取 `OAuthToken`

## PKCE OAuth 流程

### PKCEOAuthApp / AsyncPKCEOAuthApp

**适用场景**：公共客户端（如桌面应用、移动端、单页应用）无法安全存储 client_secret 的场景。使用 PKCE（Proof Key for Code Exchange）扩展增强安全性。

关键步骤：
1. 生成 `code_verifier` 和 `code_challenge`（使用 `gen_s256_code_challenge()`）
2. 构造授权 URL（携带 code_challenge）
3. 用户授权后获取 code
4. 使用 code + code_verifier 换取 token

### CozePKCEAuthError / CozePKCEAuthErrorType

PKCE 流程轮询 token 时可能遇到的错误：

| 错误类型 | 含义 | 处理方式 |
|----------|------|----------|
| `AUTHORIZATION_PENDING` | 用户尚未授权 | 继续轮询 |
| `SLOW_DOWN` | 请求过于频繁 | 增加轮询间隔 |
| `ACCESS_DENIED` | 用户拒绝授权 | 终止流程 |
| `EXPIRED_TOKEN` | Token 已过期 | 重新授权 |

## 设备授权码流程（Device Flow）

### DeviceOAuthApp / AsyncDeviceOAuthApp

**适用场景**：输入受限设备（如智能电视、CLI 工具、IoT 设备），用户在另一台设备（手机/电脑）上完成授权。

典型流程：
1. 调用设备授权接口，获取 `DeviceAuthCode`（包含 verification_uri、user_code、device_code）
2. 提示用户访问 verification_uri 并输入 user_code
3. 使用 device_code 轮询 token 端点，直到用户完成授权

## OAuth 数据模型

### OAuthToken

OAuth 令牌模型：

| 字段 | 类型 | 说明 |
|------|------|------|
| `access_token` | `str` | 访问令牌 |
| `refresh_token` | `str` | 刷新令牌（可选） |
| `expires_in` | `int` | 令牌有效期（秒） |
| `token_type` | `str` | 令牌类型，通常为 "Bearer" |
| `scope` | `str` | 授权范围 |

### DeviceAuthCode

设备授权码模型：

| 字段 | 类型 | 说明 |
|------|------|------|
| `device_code` | `str` | 设备码（用于轮询 token） |
| `user_code` | `str` | 用户码（用户在浏览器中输入） |
| `verification_uri` | `str` | 用户访问的授权页面 URL |
| `expires_in` | `int` | 设备码有效期（秒） |
| `interval` | `int` | 建议的轮询间隔（秒） |

### Scope

OAuth 授权范围枚举，定义应用可访问的权限范围。

### ScopeAccountPermission

账户级权限范围模型，描述特定账户权限的详细信息。

## 工厂函数

### load_oauth_app_from_config

```python
load_oauth_app_from_config(config: dict) -> OAuthApp
```

从配置字典加载 OAuth 应用实例。根据配置中的类型字段自动选择创建 WebOAuthApp、PKCEOAuthApp 或 DeviceOAuthApp。

| 参数 | 类型 | 说明 |
|------|------|------|
| `config` | `dict` | 配置字典，包含 client_id、client_secret、redirect_uri 等 |

## 认证方式选择指南

| 场景 | 推荐认证方式 | 说明 |
|------|-------------|------|
| 个人脚本/测试 | `TokenAuth` | 最简单，直接使用 PAT |
| 服务端 Web 应用 | `WebOAuthApp` | 标准授权码流程 |
| 桌面/CLI/移动端 | `PKCEOAuthApp` | 公共客户端，PKCE 保护 |
| 输入受限设备 | `DeviceOAuthApp` | 设备码流程 |
| 企业级服务端 | `JWTAuth` / `JWTOAuthApp` | JWT 服务端认证 |
