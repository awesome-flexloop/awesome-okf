---
type: concept
title: "认证与中间件体系"
description: "Coze Studio 的 7 层中间件链、SessionAuthMW/AdminAuthMW 双层认证机制、Cookie 会话管理与国际化处理"
tags: [认证, 中间件, Session, 权限, Hertz, i18n]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T02:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T02:30:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: F-cs-025
    resource: /references/backend-architecture.md
    title: "7 个中间件"
  - id: F-cs-026
    resource: /references/backend-architecture.md
    title: "SessionAuthMW Cookie 认证"
  - id: F-cs-027
    resource: /references/backend-architecture.md
    title: "AdminAuthMW 管理员认证"
---

# 认证与中间件体系

Coze Studio 后端基于 Hertz 框架构建了一条完整的 HTTP 中间件处理链，共 7 个中间件，覆盖请求上下文中的 Host/Scheme 注入、国际化语言检测、访问日志与链路追踪、会话认证、OpenAPI 认证、请求检查和上下文缓存。认证体系采用 SessionAuthMW 和 AdminAuthMW 双层设计，分别处理普通用户认证和管理员权限验证。

## 中间件处理链

请求经过的中间件顺序如下：

```
HTTP Request
    │
    ▼
┌─────────────┐  1. Host 中间件
│  host.go    │  → 注入 request.Host 和 request.Scheme 到 context
└──────┬──────┘
       ▼
┌─────────────┐  2. i18n 中间件
│  i18n.go    │  → 从请求头/参数提取语言，设置 i18n 上下文
└──────┬──────┘
       ▼
┌─────────────┐  3. Log 中间件
│  log.go     │  → 记录访问日志，生成并设置 LogID 到 context
└──────┬──────┘
       ▼
┌─────────────────────────────────────────┐
│  4. 认证中间件（根据路径选择）            │
│  ┌─────────────┐  ┌──────────────────┐  │
│  │ session.go  │  │ openapi_auth.go  │  │
│  │SessionAuthMW│  │ OpenAPI 认证     │  │
│  └──────┬──────┘  └────────┬─────────┘  │
│         └────────┬────────┘             │
│                  ▼                       │
│         ┌──────────────┐                │
│         │ AdminAuthMW  │  → 管理员验证  │
│         └──────┬───────┘                │
└────────────────┼────────────────────────┘
                 ▼
┌─────────────────────┐  5. 请求检查
│ request_inspector.go│  → 请求检查与审计
└──────────┬──────────┘
           ▼
┌─────────────┐  6. 上下文缓存
│ ctx_cache.go│  → 请求级缓存
└──────┬──────┘
       ▼
┌─────────────┐
│   Handler   │  → 业务处理器
└─────────────┘
```

## Host 中间件

`middleware/host.go` 是处理链的第一个中间件，负责从 HTTP 请求中提取 Host 和 Scheme 信息，并存入请求上下文。后续中间件和 Handler 可以通过上下文获取原始请求的 Host 和协议信息，用于构建回调 URL、区分多租户等场景。

## i18n 国际化中间件

`middleware/i18n.go` 实现国际化语言检测。它从以下来源按优先级提取用户语言偏好：

1. HTTP 请求头中的 `Accept-Language`
2. URL 查询参数中的语言参数
3. 请求体中的语言字段

检测到的语言设置到请求上下文中，后续业务逻辑和错误消息可以根据语言返回对应翻译。Coze Studio 使用 `pkg/i18n/` 包提供国际化能力。

## Log 中间件

`middleware/log.go` 承担两个关键职责：

1. **访问日志记录**：记录每个请求的方法、路径、状态码、耗时等信息
2. **LogID 生成与注入**：为每个请求生成唯一的 LogID（链路追踪 ID），设置到上下文中。LogID 贯穿整个请求生命周期，在 `base.thrift` 的 `Base` 结构体中作为 `LogID` 字段传递，用于日志关联和问题排查

这与 `base.thrift` 中定义的 `Base.LogID` 字段形成完整的链路追踪体系：前端请求到达后，Log 中间件生成 LogID → 注入 context → 跨服务调用时通过 Base 结构体传递 → 所有日志输出携带 LogID。

## SessionAuthMW — 用户认证

`middleware/session.go` 实现基于 Cookie 的会话认证，是普通用户访问受保护 API 的门禁。

### 认证流程

```
┌──────────┐     请求携带 Cookie?     ┌──────────────┐
│  客户端   │─────────────────────────▶│ SessionAuthMW│
└──────────┘   SessionKey cookie      └──────┬───────┘
                                            │
                              ┌─────────────┴─────────────┐
                              │                           │
                         有 Cookie                   无 Cookie
                              │                           │
                              ▼                           ▼
                     验证 Session 有效性          路径在白名单中?
                              │                           │
                     ┌────────┴────────┐           ┌──────┴──────┐
                     │                 │           │             │
                  有效             无效          是             否
                     │                 │           │             │
                     ▼                 ▼           ▼             ▼
                设置用户         清除Session    放行请求      返回 401
                到 context       返回 401                    未授权
```

### 认证机制

- **Session 标识**：通过名为 `SessionKey` 的 Cookie 传递会话标识。`SessionKey` 常量定义在 `types/consts/consts.go` 中
- **会话验证**：后端根据 SessionKey 查询会话存储（Redis/缓存），验证会话是否有效
- **用户信息注入**：验证通过后，将用户信息注入请求上下文，后续 Handler 直接从上下文获取当前用户

### 白名单路径

以下路径无需认证即可访问：

| 路径 | 说明 |
|------|------|
| `/api/passport/web/email/login/` | 邮箱登录接口 |
| `/api/passport/web/email/register/v2/` | 邮箱注册接口（V2版本） |

这两个接口是用户获取 Session 的入口，必须在认证之前开放访问。

## AdminAuthMW — 管理员认证

在 SessionAuthMW 验证用户已登录的基础上，`AdminAuthMW` 进一步验证当前用户是否具有管理员权限。

### 管理员配置

管理员权限通过邮箱白名单控制，配置来源：

1. **配置文件**：`baseConf.AdminEmails`（基础配置中的管理员邮箱列表）
2. **环境变量**：`ALLOW_REGISTRATION_EMAIL`（逗号分隔的邮箱白名单）

当 `ALLOW_REGISTRATION_EMAIL` 被设置时，它同时承担两个作用：
- 限制只有白名单中的邮箱可以注册（注册控制）
- 白名单中的邮箱自动获得管理员权限

### 注册控制

与管理员认证相关的注册控制机制：

| 环境变量 | 作用 |
|----------|------|
| `DISABLE_USER_REGISTRATION` | 设为 true 时完全禁止新用户注册 |
| `ALLOW_REGISTRATION_EMAIL` | 逗号分隔的邮箱白名单，只有列表中的邮箱可以注册；同时这些邮箱为管理员 |

这为私有部署场景提供了灵活的访问控制能力：完全开放注册、邮箱白名单注册、或完全禁止注册。

## OpenAPI 认证

`middleware/openapi_auth.go` 为开放 API 提供独立的认证机制。当请求路径匹配 OpenAPI 模式（通常带有 API Key 或 Access Token）时，使用此中间件而非 SessionAuthMW 进行认证。这对应 IDL 中定义的 `OpenAPIAuthService` 服务。

## 请求检查中间件

`middleware/request_inspector.go` 对请求进行安全检查和审计，用于识别异常请求模式、记录请求元数据等。

## 上下文缓存中间件

`middleware/ctx_cache.go` 为每个请求创建请求级别的缓存（使用 `pkg/ctxcache/` 包）。在同一个请求生命周期内，多次查询相同数据时可以直接从缓存获取，避免重复的数据库查询或远程调用。请求结束后缓存自动销毁。

## 错误处理体系

认证失败和其他业务错误通过统一的错误码体系返回：

- **错误码注册**：使用 `code.Register()` 注册模块级错误码，支持 `WithAffectStability(bool)` 标记是否影响系统稳定性
- **错误类型**：`errorx` 包提供 `StatusError` 接口，包含错误码、键值对参数和堆栈追踪
- **错误码文件**：`types/errno/` 下每个模块一个文件（agent.go、app.go、conversation.go 等），Knowledge 模块独占 105000000~105999999 范围，定义了 38 个错误码
- **基础响应**：`api/handler/coze/base.go` 提供 `invalidParam()` 和 `internalError()` 等标准错误响应函数

## 安全 goroutine

在中间件和业务逻辑中启动异步 goroutine 时，Coze Studio 强制使用 `pkg/safego/` 包提供的安全 goroutine 机制：

```go
safego.Go(func() {
    // 异步任务逻辑
    // panic 会被自动捕获，不会导致进程崩溃
})
```

`safego.Go()` 方法自动添加 panic 恢复逻辑，防止异步任务中的 panic 导致整个服务崩溃。

## 相关概念

- [整体架构概览](00-overview-ddd-architecture.md)
- [DDD 分层详解](01-ddd-layers.md)
- [Thrift IDL 与代码生成](02-thrift-idl-codegen.md)
- [部署与运维](08-deployment-operations.md)
- [后端架构参考](../references/backend-architecture.md)
