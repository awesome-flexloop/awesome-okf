---
type: concept
scope: langsmith-cli
name: api-client
version: "0.1.0"
source: https://github.com/langchain-ai/langsmith-cli
description: API 客户端架构——langsmith-go SDK 封装、v1/v2 透明切换、认证与原始 HTTP
---

# API 客户端架构

## Client 封装层

`internal/client/Client` 是 CLI 与 LangSmith API 交互的核心封装（`client.go:22-36`）。它组合了两种访问方式：

1. **SDK 优先**：`SDK *langsmith.Client` 字段持有自动生成的 [`langsmith-go`](https://github.com/langchain-ai/langsmith-go) SDK 客户端，覆盖绝大多数标准端点。
2. **原始 HTTP 补充**：`RawGet`/`RawPost`/`RawPatch`/`RawDelete`/`RawDo` 方法用于 SDK 尚未覆盖的端点（如 evaluator CRUD 的 `/api/v1/runs/rules`）。

项目规范（AGENTS.md）明确要求：新代码应优先使用 SDK，不要为已有 SDK 方法的端点添加原始 HTTP 调用。缺失的端点应通过更新 OpenAPI/Stainless 定义、发布新版 SDK 来解决。

```
┌─────────────────────────────────────┐
│         internal/cmd/               │  命令层
│  trace / run / evaluator / ...      │
└──────────────┬──────────────────────┘
               │ MustGetClient()
               ▼
┌─────────────────────────────────────┐
│         client.Client               │  封装层
│  ┌─────────────────────────────┐    │
│  │  SDK *langsmith.Client      │    │  生成式 SDK
│  │  (Sessions/Runs/Datasets/   │    │  类型安全
│  │   Evaluators/...)           │    │
│  └─────────────────────────────┘    │
│  ┌─────────────────────────────┐    │
│  │  RawGet/RawPost/RawPatch/   │    │  原始 HTTP
│  │  RawDelete/RawDo            │    │  逃生舱
│  └─────────────────────────────┘    │
│  sessionCache / cachedUseV2API      │  缓存
└─────────────────────────────────────┘
```

## 客户端创建与选项

`Options` 结构体（`client.go:39-45`）携带认证和路由信息：

```go
type Options struct {
    APIKey           string
    OAuthAccessToken string
    APIURL           string
    WorkspaceID      string
    ProfileName      string
}
```

`NewWithOptions(options)` 构造客户端时（`client.go:65-99`），按优先级配置 SDK：

1. **Profile 模式**（`ProfileName != ""`）：使用 `langsmith.WithProfile(profileName)`，让 SDK 自行管理该 profile 的认证和租户上下文。
2. **API Key 模式**：使用 `option.WithAPIKey(apiKey)`。
3. **OAuth 模式**：使用 `option.WithHeader("authorization", "Bearer "+token)`。

BaseURL 仅在非默认值时设置（SDK 自身也会读取 `LANGSMITH_ENDPOINT`）。Workspace 通过 `option.WithTenantID(workspaceID)` 设置。

### URL 规范化

`NormalizeURL(apiURL)` 去除尾部 `/` 和 `/api/v1` 后缀（`client.go:50-53`）。这是因为 SDK 会自行追加 `api/v1`，而自托管用户常将 `LANGSMITH_ENDPOINT` 设为 `https://host/api/v1`，直接拼接会导致路径重复。

## v1/v2 API 透明切换

### 版本探测

`UseV2API(ctx)` 在首次调用时通过 `SDK.Info.List(ctx)` 获取部署版本（`client.go:126-137`），结果缓存到 `cachedUseV2API`。版本判定逻辑（`client.go:142-151`）：

```
版本字符串 "dev" 或非 semver  → v2（Cloud）
major != 0                    → v2（未来大版本）
major == 0, minor >= 16       → v2（自托管 0.16+，SmithDB）
major == 0, minor < 16        → v1（旧版自托管）
```

### 查询分发

`queryRunsAuto(ctx, c, params, v2Selects, sessionID, limit, minTokens)` 是所有 run/trace 查询的统一入口（`helpers.go:124-133`）：

```go
func queryRunsAuto(...) {
    useV2, _ := c.UseV2API(ctx)
    if useV2 {
        return queryRunsV2(ctx, c, toV2Params(params, v2Selects), ...)
    }
    return queryRuns(ctx, c, params, ...)
}
```

### 参数翻译

`toV2Params(p, selects)` 将 v1 `RunQueryParams` 映射为 v2 `RunQueryV2Params`（`helpers.go:137-170`）：

| v1 字段 | v2 字段 | 说明 |
|---|---|---|
| `Trace` | `TraceID` | 重命名 |
| `IsRoot` | `IsRoot` | 直接映射 |
| `RunType` | `RunType` | 值转大写 |
| `Error` | `HasError` | 重命名 |
| `StartTime` | `MinStartTime` | 重命名 |
| `EndTime` | `MaxStartTime` | 重命名 |
| `ID` | `IDs` | 重命名 |
| `Limit` | `PageSize` | 重命名 |
| `Order` | — | 丢弃（v2 固定 newest-first） |
| `Select` | `Selects` | 使用独立的 v2 字段枚举 |

### 响应归一化

`runV2ToSchema(r)` 将 v2 `Run` 转回 v1 `RunSchema`（`helpers.go:228-276`），关键映射：

- `ProjectID` → `SessionID`（v2 用 "project" 术语，v1 用 "session"）
- `ParentRunIDs[len-1]` → `ParentRunID`（v1 只有直接父 ID）
- `RunType` 转小写
- v2 `Metadata` 合并到 `Extra["metadata"]`
- `FeedbackStats` 和 `Events` 通过 JSON round-trip 转换为松散类型 map

这使得下游的 `extract.ExtractRun` 和输出管道无需修改即可同时支持两代 API。

### Select 字段集

v1 和 v2 使用不同的枚举类型指定返回字段：

- v1：`[]langsmith.RunQueryParamsSelect`，通过 `buildRunSelect(includeIO, includeFeedback)` 构建。
- v2：`[]langsmith.RunSelectField`，通过 `buildRunSelectV2(includeIO, includeFeedback)` 构建。

两个函数都包含 ID、TraceID、Name、RunType、时间、token、成本、延迟等基础字段，并根据 `includeIO`/`includeFeedback` 追加 inputs/outputs/error/events 和 feedback_stats。

## 认证体系

### 配置解析链

`resolveClientOptions(refreshOAuth)` 在 `root.go:143-227` 实现，优先级从高到低：

**API URL：**
```
--api-url flag → LANGSMITH_ENDPOINT env → profile.APIURL → DefaultAPIURL
```

**Workspace：**
```
--workspace flag → LANGSMITH_WORKSPACE_ID env → LANGSMITH_TENANT_ID env → profile.WorkspaceID
```

**认证凭证：**
```
--api-key flag → LANGSMITH_API_KEY env → profile OAuth token（自动刷新）→ profile APIKey
```

当 `--profile` 与环境变量冲突时，CLI 输出警告到 stderr（如"LANGSMITH_API_KEY takes precedence over saved profile auth"）。

### OAuth 2.0 设备码流

`langsmith auth login` 实现 OAuth 2.0 设备授权流程（`login.go`）：

1. **发现**：`client.ResolveOAuth(ctx, apiURL)` 探测 RFC 8414 `/.well-known/oauth-authorization-server` 元数据，获取 device/token/register 端点。发现失败时回退到 `<base>/oauth/device/code` 等硬编码路径。
2. **注册**：使用 client ID `"langsmith-cli"` 动态注册客户端。
3. **设备码**：请求 device code，展示 user_code 和 verification_uri，自动打开浏览器。
4. **轮询**：每 5 秒轮询 token endpoint，直到用户授权或超时。
5. **存储**：access_token、refresh_token、expires_at 写入 profile 配置。

### Token 自动刷新

当 `refreshOAuth=true`（命令需要发起 API 请求时），若 access token 为空或 `TokenExpiresSoon(now, 1 minute)`（`config.go:214-220`），CLI 自动用 refresh token 获取新 token 并保存。刷新失败时提示用户重新运行 `langsmith auth login`。

### OAuth 安全校验

`validateOAuthMetadata`（`oauth.go:173-194`）强制执行：
- **Issuer 匹配**：元数据的 issuer 必须与探测 URL 一致。
- **同源约束**：所有 endpoint URL 必须与 issuer 同 scheme+host。

这防止了恶意或配置错误的发现文档将 refresh token 和 device code 发送到第三方主机。

## 原始 HTTP 辅助

### 方法

| 方法 | 用途 |
|---|---|
| `RawGet(ctx, path, result)` | GET 请求，JSON 解码到 result |
| `RawPost(ctx, path, body, result)` | POST 请求，JSON body |
| `RawPatch(ctx, path, body, result)` | PATCH 请求 |
| `RawDelete(ctx, path, result)` | DELETE 请求 |
| `RawDo(ctx, method, path, body, headers)` | 任意请求，返回原始响应（不将 4xx/5xx 视为错误） |
| `FetchCustomAppSource(ctx, appID)` | 下载二进制 .tar.gz |

### 请求细节

`doHTTP` 底层方法（`client.go:336-384`）：

- 30 秒 HTTP 客户端超时。
- 认证头：API key 用 `x-api-key`，OAuth 用 `Authorization: Bearer`。
- 始终设置 `Content-Type: application/json`。
- Workspace 设置 `x-tenant-id` 头。
- 支持自定义额外 header。
- 错误体解析：`httpErrorBody` 尝试提取 error/message/error_description/detail 字段，生成可读错误消息。
- 错误类型判断：`IsNotFound`/`IsConflict`/`IsForbidden`/`IsBadRequest` 通过 status code 判断。

### 平台路径

`PlatformPath(elem...)` 构建平台服务路径（`client.go:207-216`），自动处理单源/多源前缀：

- 单源部署：`/api/v1/platform/custom-apps`
- 多源部署：`/v1/platform/custom-apps`

前缀由 `derivePlatformPrefix(apiURL)` 根据原始 endpoint 是否以 `/api/v1` 或 `/api` 结尾决定。

## Session 缓存

`ResolveSessionID(ctx, projectName)` 将 project name 解析为 session UUID（`client.go:102-119`），结果缓存在 `sessionCache map[string]string` 中。缓存仅在单次 CLI 调用内有效，避免同一命令中多次查询同一 project 时重复 API 请求。

`resolveSessionID`（`helpers.go:27-39`）在此基础上增加了 `--project-id` 快速路径：当提供 UUID 格式的 project-id 时直接返回，跳过名称查找。

## 相关概念

- CLI 命令体系 — 过滤器 DSL、分页、输出模式
- 总览 — 项目定位与架构概览
