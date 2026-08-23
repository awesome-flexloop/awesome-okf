---
type: Reference
title: GitHub 仓库提供者信源
description: repoproviders/github.py GitHubRepoProvider 类的API登记，包含异步API请求、引用解析、缓存和认证
tags: [github, provider, repoprovider, tornado, traitlets, async, api, cache]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T16:00:00+08:00" }
verified: { by: "process:grep-api-verify", at: "2026-08-22T16:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: github-py
    resource: ../../../../../../external/libs/jupyter/repo2jupyterlite/repoproviders/github.py
    title: repoproviders/github.py 源码
---

## 类概览

`GitHubRepoProvider(LoggingConfigurable)` 继承自 `traitlets.config.LoggingConfigurable`，提供 GitHub 仓库引用解析和 API 交互能力。

## 类级别属性

| 属性 | 类型 | 默认值 | 可配置 | 说明 |
|------|------|--------|--------|------|
| `name` | Unicode | `"GitHub"` | 否 | Provider 显示名 |
| `cache` | Cache | `Cache(1024)` | 否 | 成功结果LRU缓存（无TTL） |
| `cache_404` | Cache | `Cache(1024, max_age=300)` | 否 | 404结果缓存（5分钟TTL） |
| `hostname` | Unicode | `"github.com"` | 是 | GitHub主机名（支持GitHub Enterprise） |
| `api_base_path` | Unicode | `"https://api.{hostname}"` | 是 | API基础路径模板 |
| `client_id` | Unicode | `""`（环境变量`GITHUB_CLIENT_ID`） | 是 | OAuth App Client ID |
| `client_secret` | Unicode | `""`（环境变量`GITHUB_CLIENT_SECRET`） | 是 | OAuth App Client Secret |
| `access_token` | Unicode | `""`（环境变量`GITHUB_ACCESS_TOKEN`） | 是 | Personal Access Token |

## 实例属性

| 属性 | 类型 | 设置位置 | 说明 |
|------|------|---------|------|
| `user` | str | `__init__` | GitHub 用户名/组织名 |
| `repo` | str | `__init__` | 仓库名 |
| `unresolved_ref` | str | `__init__` | 未解析的引用（分支/tag/HEAD） |
| `resolved_ref` | str | `get_resolved_ref()` | 解析后的commit SHA（缓存） |

## 公共方法

### `from_spec_and_path(cls, spec_and_path: str)`（类方法）

**签名**：`from_spec_and_path(cls, spec_and_path: str) -&gt; tuple[GitHubRepoProvider, str]`

**行为**：
- 将 `spec_and_path` 按 `/` 分割（maxsplit=3）
- 3段时（user/repo/ref）追加空path
- 4段时取第4段为path
- 返回 `(cls(user, repo, ref), path)`

### `__init__(self, user, repo, unresolved_ref)`

设置 `self.user`、`self.repo`、`self.unresolved_ref`。

### `get_resolved_ref(self)`（异步）

**签名**：`async get_resolved_ref(self) -&gt; str | None`

**行为**：
1. 实例属性 `resolved_ref` 已存在时直接返回
2. 构造 API URL：`{api_base_path}/repos/{user}/{repo}/commits/{ref}`
3. 先查 `self.cache.get(api_url)`：命中则使用缓存的 etag
4. 未命中再查 `self.cache_404.get(api_url)`：命中则返回 None
5. 调用 `_github_api_request(api_url, etag=etag)`
6. resp 为 None（404/422）：缓存到 cache_404，返回 None
7. resp.code == 304：使用缓存的 sha，move_to_end 刷新 LRU
8. 正常响应：解析 JSON 取 `sha` 字段，存入 `self.resolved_ref`，缓存 etag+sha
9. 响应中无 `sha` 字段：记录 warning，返回 None

### `get_resolved_spec(self)`（异步）

**签名**：`async get_resolved_spec(self) -&gt; str`

**行为**：调用 `await self.get_resolved_ref()`，返回 `f"{self.user}/{self.repo}/{resolved_ref}"`。

### `get_resolved_repo(self)`

**签名**：`get_resolved_repo(self) -&gt; str`

**行为**：返回 `f"https://{self.hostname}/{self.user}/{self.repo}"`。

## 内部方法

### `_github_api_request(self, api_url, etag=None)`（异步）

**签名**：`async _github_api_request(self, api_url: str, etag: str | None = None) -&gt; tornado.httpclient.HTTPResponse | None`

**认证优先级**：
1. `client_id` + `client_secret`：HTTP Basic Auth
2. `access_token`：Authorization header `token &lt;access_token&gt;`

**错误处理**：
| HTTP状态码 | 处理 |
|-----------|------|
| 304 | 返回 e.response（Not Modified，使用缓存） |
| 403 + rate limit=0 | 抛出 ValueError，附带重置时间 |
| 404, 422 | 返回 None（引用不存在） |
| 其他 | raise HTTPError |

**Rate limit 日志**：根据剩余配额比例分级别记录：&lt;20% → warning，&lt;50% → info，其余 → debug。

### `_default_git_credentials(self)`（属性默认值）

- `access_token` + `client_id`：`username={client_id}\npassword={token}`
- `access_token` 无 `client_id`：`username={token}\npassword=x-oauth-basic`
- 无 token：返回空字符串
