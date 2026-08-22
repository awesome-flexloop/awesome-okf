---
type: Concept
title: REST API 通信机制
description: requestAPI封装HTTP请求，/git命名空间下30+REST端点，前后端版本校验，GitResponseError含traceback。
tags: [rest-api, http, tornado, request, error-handling, authentication, version-check]
generated:
  by: source-code-to-okf-wiki
  at: "2026-08-22T00:00:00Z"
verified:
  by: process:seven-concepts-v
  at: "2026-08-22T00:00:00Z"
status: stable
stale_after: "2027-08-22"
sources:
  - /references/git-py-source.md
  - /references/handlers-py-source.md
---

## 通信架构概述

jupyterlab-git 前后端通过 HTTP REST API 通信，前端作为 HTTP 客户端，后端基于 Tornado Web 框架提供 REST 服务。所有 API 端点统一挂载在 `/git/` 命名空间下（`NAMESPACE = "/git"`），使用 JSON 作为数据交换格式。

```
前端 GitExtension._requestAPI()
    ↓ HTTP (JSON)
Tornado GitHandler 子类
    ↓ 方法调用
Git 执行引擎
    ↓ subprocess/pexpect
Git 命令行工具
```

前端不直接与 Git 命令行交互，所有 Git 操作必须通过后端 API 中转，这确保了文件系统访问权限统一由 Jupyter Server 控制。

## 前端请求函数：requestAPI

前端通过内部的 `requestAPI` 函数（在 `src/git.ts` 中定义）封装所有 HTTP 请求逻辑。`GitExtension._requestAPI<T>()` 是其上层包装。

### URL 构建

API 端点 URL 使用 JupyterLab 的 `URLExt.join()` 函数拼接：

```typescript
// GitExtension._requestAPI 中
const url = URLExt.join(this._serverSettings.baseUrl, 'git', pathRepository, endPoint);
```

URL 结构为：`<baseUrl>/git/<pathRepository>/<endPoint>`

其中：
- `baseUrl`：Jupyter Server 的基础 URL（由 `ServerConnection` 提供）
- `pathRepository`：当前 Git 仓库根路径（URL 编码）
- `endPoint`：具体 API 端点路径（如 `status`、`add`、`commit`）

`URLExt.join()` 类似 `path.join()`，自动处理路径分隔符，避免重复斜杠问题。

### 请求发送

请求通过 `ServerConnection.makeRequest()` 发送，这是 JupyterLab 提供的 HTTP 客户端：

- 自动附加 Jupyter Server 的认证 Cookie 和 XSRF Token
- 请求头 `Content-Type: application/json`
- 请求体使用 `JSON.stringify(body)` 序列化
- 默认使用 GET 方法，写操作使用 POST/DELETE

### 错误处理：Git.GitResponseError

当 HTTP 响应状态码非 ok（≥400）时，抛出 `Git.GitResponseError` 错误类：

```typescript
class GitResponseError extends Error {
  constructor(
    response: Response,
    public readonly traceback: string = '',
    public readonly json: any = null
  );
}
```

| 属性 | 类型 | 说明 |
|------|------|------|
| `message` | `string` | 错误消息（从 JSON 响应的 `message` 字段提取） |
| `response` | `Response` | 原始 Response 对象，可获取 `status` 状态码 |
| `traceback` | `string` | 服务器端 Python traceback（开发模式下） |
| `json` | `any` | 完整的 JSON 错误响应体 |

后端 `handle_git_error()` 方法统一将异常转换为 JSON 响应：
- `GitParameterError` → HTTP 400（参数错误），响应包含 `message` 字段
- `GitCommandError` → HTTP 500（Git 命令失败），响应包含 `command`、`message`、`traceback` 字段
- 其他异常 → HTTP 500，响应包含 `message` 和 `traceback`

前端可以通过 `error.response.status` 判断错误类型，通过 `error.traceback` 在控制台输出调试信息。

## /git 命名空间与 API 端点列表

所有端点的路由注册在 `setup_handlers()` 函数中，以 `base_url + "/git/"` 为前缀。特殊端点 `/git/settings` 和 `/git/known_hosts` 不包含仓库路径。

### 设置与认证

| HTTP 方法 | 端点 | Handler | 说明 |
|----------|------|---------|------|
| GET | `/git/settings` | `GitSettingsHandler` | 获取服务端版本信息（gitVersion、serverVersion） |
| GET/POST | `/git/known_hosts` | `GitKnownHostsHandler` | 查询/添加 SSH known_hosts |

### 仓库操作

| HTTP 方法 | 端点 | Handler | Git 方法 | 说明 |
|----------|------|---------|---------|------|
| POST | `/git/{path}/clone` | `GitCloneHandler` | `git.clone()` | 克隆仓库 |
| POST | `/git/{path}/init` | `GitInitHandler` | `git.init()` | 初始化仓库 |
| POST | `/git/{path}/show_top_level` | `GitShowTopLevelHandler` | `git.show_top_level()` | 获取仓库根路径 |
| POST | `/git/{path}/show_prefix` | `GitShowPrefixHandler` | `git.show_prefix()` | 获取当前目录相对前缀 |

### 状态与文件操作

| HTTP 方法 | 端点 | Handler | Git 方法 | 说明 |
|----------|------|---------|---------|------|
| POST | `/git/{path}/status` | `GitStatusHandler` | `git.status()` | 获取仓库状态（porcelain v2） |
| POST | `/git/{path}/add` | `GitAddHandler` | `git.add()` | 添加文件到暂存区 |
| POST | `/git/{path}/add_all_unstaged` | `GitAddAllUnstagedHandler` | `git.add()` (all unstaged) | 添加所有未暂存文件 |
| POST | `/git/{path}/add_all_untracked` | `GitAddAllUntrackedHandler` | `git.add()` (all untracked) | 添加所有未跟踪文件 |
| POST | `/git/{path}/reset` | `GitResetHandler` | `git.reset()` | 从暂存区移除文件 |
| POST | `/git/{path}/commit` | `GitCommitHandler` | `git.commit()` | 提交 |
| POST | `/git/{path}/diff` | `GitDiffHandler` | `git.diff()` | 获取差异 |
| GET/POST | `/git/{path}/content` | `GitContentHandler` | 文件读取 | 获取文件内容（diff 用） |

### 分支与标签

| HTTP 方法 | 端点 | Handler | Git 方法 | 说明 |
|----------|------|---------|---------|------|
| POST | `/git/{path}/branch` | `GitBranchHandler` | `git.branch()` | 获取分支列表 |
| POST | `/git/{path}/checkout` | `GitCheckoutHandler` | `git.checkout()` | 切换分支/恢复文件 |
| POST | `/git/{path}/branch/delete` | `GitDeleteBranchHandler` | `git.delete_branch()` | 删除分支 |
| POST | `/git/{path}/merge` | `GitMergeHandler` | `git.merge()` | 合并分支 |
| POST | `/git/{path}/rebase` | `GitRebaseHandler` | `git.rebase()` | 变基/解决变基 |
| POST | `/git/{path}/tags` | `GitTagHandler` | `git.tags()`/`git.tag()` | 列出/创建标签 |
| POST | `/git/{path}/tag_checkout` | `GitCheckoutTagHandler` | `git.checkout_tag()` | 切换到标签 |
| POST | `/git/{path}/reset_to_commit` | `GitResetToCommitHandler` | `git.reset()` | 重置到 commit |
| POST | `/git/{path}/revert_commit` | `GitRevertCommitHandler` | `git.revert()` | 回滚 commit |

### 远程操作

| HTTP 方法 | 端点 | Handler | Git 方法 | 说明 |
|----------|------|---------|---------|------|
| POST | `/git/{path}/remote/fetch` | `GitFetchHandler` | `git.fetch()` | 获取远程更新 |
| POST | `/git/{path}/pull` | `GitPullHandler` | `git.pull()` | 拉取 |
| POST | `/git/{path}/push` | `GitPushHandler` | `git.push()` | 推送 |
| POST | `/git/{path}/remote/add` | `GitRemoteAddHandler` | `git.remote_add()` | 添加远程 |
| DELETE | `/git/{path}/remote/{name}` | `GitRemoteRemoveHandler` | `git.remote_remove()` | 删除远程 |
| GET | `/git/{path}/remote/show` | `GitRemoteShowHandler` | `git.remote_show()` | 显示远程列表 |

### Stash 操作

| HTTP 方法 | 端点 | Handler | Git 方法 | 说明 |
|----------|------|---------|---------|------|
| POST | `/git/{path}/stash` | `GitStashListHandler` | `git.stash_list()` | 列出 stash |
| POST | `/git/{path}/stash_show` | `GitStashShowHandler` | `git.stash_show()` | 显示 stash 内容 |
| POST | `/git/{path}/stash_save` | `GitStashSaveHandler` | `git.stash_save()` | 保存 stash |
| POST | `/git/{path}/stash_apply` | `GitStashApplyHandler` | `git.stash_apply()` | 应用 stash |
| POST | `/git/{path}/stash_pop` | `GitStashPopHandler` | `git.stash_pop()` | 弹出 stash |
| POST | `/git/{path}/stash_drop` | `GitStashDropHandler` | `git.stash_drop()` | 删除 stash |

### 历史与日志

| HTTP 方法 | 端点 | Handler | Git 方法 | 说明 |
|----------|------|---------|---------|------|
| POST | `/git/{path}/log` | `GitLogHandler` | `git.log()` | 获取提交日志 |
| POST | `/git/{path}/detailed_log` | `GitDetailedLogHandler` | `git.detailed_log()` | 获取 commit 详情 |
| POST | `/git/{path}/changed_files` | `GitChangedFilesHandler` | `git.changed_files()` | 获取变更文件列表 |

### 配置与忽略

| HTTP 方法 | 端点 | Handler | Git 方法 | 说明 |
|----------|------|---------|---------|------|
| POST/GET | `/git/{path}/config` | `GitConfigHandler` | `git.config()` | 获取/设置 git 配置 |
| POST/GET | `/git/{path}/ignore` | `GitIgnoreHandler` | `git.ignore()`/`ensure_gitignore()` | 管理 .gitignore |

### Notebook 支持

| HTTP 方法 | 端点 | Handler | Git 方法 | 说明 |
|----------|------|---------|---------|------|
| GET | `/git/{path}/check_notebooks` | `GitCheckNotebooksHandler` | `git.check_notebooks()` | 检查 Notebook 输出 |
| POST | `/git/{path}/strip_notebooks` | `GitStripNotebooksHandler` | `git.strip_notebooks()` | 清除 Notebook 输出 |

## 后端路由注册

`setup_handlers(web_app)` 函数负责将所有 Handler 注册到 Tornado Web 应用：

```python
def setup_handlers(web_app):
    host_pattern = ".*$"
    base_url = web_app.settings["base_url"]
    
    handlers = [
        (url_path_join(base_url, NAMESPACE, "settings"), GitSettingsHandler),
        (url_path_join(base_url, NAMESPACE, path_regex, "clone"), GitCloneHandler),
        (url_path_join(base_url, NAMESPACE, path_regex, "init"), GitInitHandler),
        # ... 所有路由
    ]
    web_app.add_handlers(host_pattern, handlers)
```

其中 `path_regex` 是一个正则表达式，用于匹配 URL 中的仓库路径部分。`url_path_join` 正确处理 base_url 可能包含的前缀（如 JupyterHub 部署时的 `/user/xxx/`）。

## GitHandler 基类

所有 Git 相关 Handler 继承自 `GitHandler` 基类（继承自 `jupyter_server.base.handlers.APIHandler`）：

```python
class GitHandler(APIHandler):
    @property
    def git(self) -> Git:
        return self.settings["git"]
    
    def handle_git_error(self, e: Exception) -> None: ...
    async def prepare(self): ...
    def url2localpath(self, path, with_contents_manager=False): ...
```

### git 属性

`self.git` property 从 `web_app.settings["git"]` 获取在 server extension 加载时创建的 `Git` 单例实例。所有 Handler 共享同一个 `Git` 实例，从而共享全局执行锁和凭证缓存。

### prepare() 请求预处理

在每个请求处理前自动调用，检查路径是否在 `excluded_paths` 配置中（使用 fnmatch 模式匹配），匹配则返回 404 禁止访问。这允许管理员配置某些目录（如 `/data/*`）不可通过 Git 扩展访问。

### url2localpath() 路径转换

将 URL 中的路径参数转换为本地文件系统路径：
- 基于 `contents_manager.root_dir` 和 `url2path()` 方法转换
- 支持 `hybridcontents.HybridContentsManager`（混合内容管理器）
- 可选返回 `contents_manager` 实例供后续使用

### handle_git_error() 错误处理

统一异常到 HTTP 响应的转换：

| 异常类型 | HTTP 状态码 | 响应字段 |
|---------|------------|---------|
| `GitParameterError` | 400 | `message` |
| `GitCommandError` | 500 | `message`、`command`（失败的 git 命令）、`traceback` |
| 其他 Exception | 500 | `message`、`traceback` |

所有 Handler 使用 `@tornado.web.authenticated` 装饰器，要求用户已通过 Jupyter Server 认证。

## 前后端版本校验机制

### getServerSettings()

前端插件激活时调用 `getServerSettings()` 函数：

```typescript
async function getServerSettings(
  settings: ServerConnection.ISettings
): Promise<ServerSettings>
```

该函数向 `GET /git/settings?version=<frontendVersion>` 发送请求：

1. 后端 `GitSettingsHandler.get()` 返回：
   ```json
   {
     "frontendVersion": null,
     "gitVersion": "<检测到的git版本号>",
     "serverVersion": "<Python包版本号>"
   }
   ```
2. 前端检测 `gitVersion`：
   - 使用正则解析版本号
   - 若主版本号 < 2，抛出错误要求升级 Git
3. 前端对比版本：
   ```typescript
   if (frontendVersion && frontendVersion !== serverVersion) {
     throw new Error('前端版本与Python包版本不匹配');
   }
   ```
   这确保了前后端 API 契约一致，避免因版本不匹配导致的 API 调用失败。

## 认证错误处理：AUTH_ERROR_MESSAGES

前端维护一个认证错误消息列表 `AUTH_ERROR_MESSAGES`，用于识别 Git 操作中因认证失败导致的错误：

当 push/pull/fetch 等远程操作返回错误时，前端检查错误消息是否包含列表中的关键词（如 "Authentication failed"、"could not read Username"、"Permission denied" 等）。如果匹配认证错误，设置 `credentialsRequired = true` 并发出 `credentialsRequiredChanged` 信号，UI 弹出凭证输入对话框。

### 双模式认证支持

**1. HTTP/HTTPS 认证（用户名/密码）**

前端检测到认证错误后，弹出对话框收集用户名和密码，在后续 API 请求中通过 `auth` 参数传入：
```typescript
await gitExtension.push({ username: 'user', password: 'pass', cache_credentials: true });
```
后端 `Git.clone()`/`pull()`/`push()`/`fetch()` 方法收到 auth 参数后，切换到 pexpect 执行模式，自动响应 "Username for" 和 "Password for" 提示。

**2. SSH 认证**

通过 `GitKnownHostsHandler` 管理 SSH known_hosts：
- 首次连接 SSH 主机时，调用 `checkKnownHost(hostname)` 检查主机是否可信
- 用户确认后，调用 `addHostToKnownList(hostname)` 添加到 known_hosts
- SSH key 认证由系统 SSH 配置处理，扩展不直接管理私钥

## GitSettingsHandler 特殊说明

`GitSettingsHandler` 不继承 `GitHandler`，直接继承 `APIHandler`，因为它在路径解析之前就需要响应（不需要仓库路径），且不需要 Git 实例即可返回版本信息。

```python
class GitSettingsHandler(APIHandler):
    @tornado.web.authenticated
    def get(self):
        version = self.get_argument("version", None)
        self.finish(json.dumps({
            "frontendVersion": version,
            "gitVersion": self._get_git_version(),
            "serverVersion": __version__
        }))
```

## 内容获取端点：GitContentHandler

`GitContentHandler` 是一个特殊端点（GET/POST `/git/{path}/content`），用于 Diff 功能获取文件的不同版本内容（工作区、暂存区、BASE 版本）。它支持通过 `ref` 参数指定 Git 引用（SpecialRef：WORKING/INDEX/BASE），返回文件内容供前端 Diff 组件渲染。

## 相关概念

- [架构总览](/concepts/02-architecture-overview.md)
- [GitExtension核心模型](/concepts/04-git-extension-model.md)
- [可插拔Diff系统](/concepts/06-diff-provider-system.md)
- [插件系统与五个Plugin](/concepts/03-extension-plugin-system.md)
