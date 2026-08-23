---
type: reference
scope: langsmith-cli
name: data-structures
version: "0.1.0"
source: https://github.com/langchain-ai/langsmith-cli
description: langsmith-cli 核心数据结构——Client、Options、FilterFlags、配置与 OAuth 类型
---

# 核心数据结构

本参考记录 CLI 内部包中的关键 Go 类型定义。

## client.Client

`internal/client/client.go:22-36`

```go
type Client struct {
    SDK              *langsmith.Client
    apiKey           string
    oauthAccessToken string
    apiURL           string
    workspaceID      string
    platformPrefix   string
    sessionCache     map[string]string
    cachedUseV2API   *bool
}
```

| 字段 | 说明 |
|---|---|
| `SDK` | 自动生成的 langsmith-go SDK 客户端，覆盖标准端点 |
| `apiKey` | API Key（用于原始 HTTP 的 `x-api-key` 头） |
| `oauthAccessToken` | OAuth Bearer token |
| `apiURL` | 规范化后的 API 基础 URL |
| `workspaceID` | 工作区/租户 ID（`x-tenant-id` 头） |
| `platformPrefix` | 平台路径前缀（`/api/v1/platform` 或 `/v1/platform`） |
| `sessionCache` | project name → UUID 缓存（单次调用有效） |
| `cachedUseV2API` | v2 API 探测结果缓存 |

## client.Options

`internal/client/client.go:39-45`

```go
type Options struct {
    APIKey           string
    OAuthAccessToken string
    APIURL           string
    WorkspaceID      string
    ProfileName      string
}
```

## cmd.FilterFlags

`internal/cmd/filters.go:14-33`

```go
type FilterFlags struct {
    TraceIDs     string
    Limit        int
    Project      string
    ProjectID    string
    LastNMinutes int
    Since        string
    Before       string
    Cursor       string
    ErrorFlag    bool
    NoErrorFlag  bool
    Name         string
    RunType      string
    MinLatency   float64
    MaxLatency   float64
    MinTokens    int
    Tags         string
    Metadata     string
    RawFilter    string
}
```

## config.Config / Profile / OAuth

`internal/config/config.go:20-38`

```go
type Profile struct {
    APIKey      string `json:"api_key,omitempty"`
    APIURL      string `json:"api_url,omitempty"`
    WorkspaceID string `json:"workspace_id,omitempty"`
    OAuth       OAuth  `json:"oauth,omitempty"`
}

type OAuth struct {
    AccessToken  string `json:"access_token,omitempty"`
    RefreshToken string `json:"refresh_token,omitempty"`
    ExpiresAt    string `json:"expires_at,omitempty"`
}

type Config struct {
    CurrentProfile string             `json:"current_profile,omitempty"`
    Profiles       map[string]Profile `json:"profiles,omitempty"`
}
```

配置文件路径：`~/.langsmith/config.json`（可通过 `LANGSMITH_CONFIG_FILE` 覆盖）。

## client.OAuthMetadata

`internal/client/oauth.go:29-36`

```go
type OAuthMetadata struct {
    Issuer                      string
    DeviceAuthorizationEndpoint string
    TokenEndpoint               string
    RegistrationEndpoint        string
    Resource                    string
}
```

通过 RFC 8414 `/.well-known/oauth-authorization-server` 发现，或回退到 `<base>/oauth/*` 硬编码路径。

## output.RunTreeData

`internal/output/output.go:94-101`

```go
type RunTreeData struct {
    ID          string
    ParentRunID string
    Name        string
    RunType     string
    DurationMs  *int64
    HasError    bool
}
```

用于 `treeprint` 渲染 trace 层级树。

## 关键方法签名

### Client 方法

```go
func NewWithOptions(options Options) *Client
func (c *Client) ResolveSessionID(ctx context.Context, projectName string) (string, error)
func (c *Client) UseV2API(ctx context.Context) (bool, error)
func (c *Client) PlatformPath(elem ...string) string
func (c *Client) RawGet(ctx, path, result) error
func (c *Client) RawPost(ctx, path, body, result) error
func (c *Client) RawPatch(ctx, path, body, result) error
func (c *Client) RawDelete(ctx, path, result) error
func (c *Client) RawDo(ctx, method, path, body, headers) (statusCode int, ..., err error)
```

### cmd 包函数

```go
func NewRootCmd(rawVersion, displayVersion string) *cobra.Command
func GetAPIKey() string
func GetAPIURL() string
func GetWorkspaceID() string
func GetFormat() string
func MustGetClient() *client.Client
func BuildRunQueryParams(f *FilterFlags, isRoot bool, defaultLimit int) langsmith.RunQueryParams
func ExtractRun(run, includeMetadata, includeIO, includeFeedback) map[string]any
```

## 相关参考

- [命令参考](/ai/langchain-ai/langsmith-cli/references/commands) — 全部命令与标志
- [API 客户端架构](/ai/langchain-ai/langsmith-cli/concepts/api-client) — v1/v2 适配机制
