---
type: Concept
title: GitExtension 核心模型
description: GitExtension实现IGitExtension，管理双Poll轮询、TaskHandler队列、pathRepository发现和所有Git API。
tags: [git-extension, model, polling, task-handler, state-management, path-discovery]
generated:
  by: source-code-to-okf-wiki
  at: "2026-08-22T00:00:00Z"
verified:
  by: process:seven-concepts-v
  at: "2026-08-22T00:00:00Z"
status: stable
stale_after: "2027-08-22"
sources:
  - /references/model-ts-source.md
  - /references/tokens-ts-source.md
---

## GitExtension 类概述

`GitExtension` 类位于 `src/model.ts`，是 jupyterlab-git 前端扩展的核心模型，实现了 `IGitExtension` 接口。它负责管理 Git 仓库的前端状态、调度轮询刷新、封装所有 Git 操作的 HTTP 请求，并通过 Lumino Signal 向 UI 层发布状态变更事件。

```typescript
class GitExtension implements IGitExtension {
  constructor(
    docmanager: IDocumentManager | null = null,
    docRegistry: DocumentRegistry | null = null,
    settings?: ISettingRegistry.ISettings,
    serverSettings?: ServerConnection.ISettings
  );
  // ... 所有公共属性和方法
}
```

### 构造函数参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `docmanager` | `IDocumentManager \| null` | 文档管理器实例，用于脏文件检测和 checkout 时的文档刷新 |
| `docRegistry` | `DocumentRegistry \| null` | 文档注册表，用于解析文件类型（判断是否为二进制/文本） |
| `settings` | `ISettingRegistry.ISettings` | 插件设置，用于读取轮询间隔、文件点击行为等配置 |
| `serverSettings` | `ServerConnection.ISettings` | 服务端连接设置，包含版本信息和 base URL |

构造函数执行以下初始化：
- 保存 `_docmanager` 和 `_docRegistry` 引用
- 创建 `_taskHandler = new TaskHandler(this)` 任务处理器
- 创建 `_statusPoll` Poll 实例（auto: true，3 秒默认间隔，指数退避最大 300 秒）
- 创建 `_fetchPoll` Poll 实例（auto: false，按需启动）
- 连接 `settings.changed` 信号，响应设置变化（如动态调整轮询间隔）
- 初始化所有内部状态变量

## 双 Poll 轮询机制

GitExtension 使用 `@lumino/polling` 的 `Poll` 类实现两种自动轮询，定期从后端获取最新仓库状态。

### _statusPoll（状态轮询）

- **factory 方法**：`_refreshModel()`，一次刷新操作包括 `refreshStatus()` + `refreshBranch()`
- **默认频率**：3 秒间隔
- **退避策略**：指数退避（exponential backoff），最大间隔 300 秒
- **auto 启动**：`true`，插件激活后立即开始
- **standby 条件**：页面不可见时自动增大间隔，节省资源
- **用途**：持续刷新工作区状态（变更文件列表、暂存状态）和分支列表

### _fetchPoll（远程获取轮询）

- **factory 方法**：`_fetchRemotes()`，执行 `git fetch`
- **默认频率**：与状态轮询相同
- **退避策略**：同上
- **auto 启动**：`false`，不自动启动
- **启动条件**：当 `refreshBranch()` 检测到当前分支有远程跟踪分支（upstream）时，调用 `_fetchPoll.start()` 启动；当没有远程分支时，调用 `_fetchPoll.stop()` 停止
- **用途**：定期 fetch 远程更新，使 ahead/behind 计数保持最新

### 轮询的 standby 模式

Poll 支持自定义 standby 条件（通过 `refreshStandbyCondition`），当 JupyterLab 页面不可见（如切换到其他浏览器标签）时，轮询自动进入 standby 模式，增大轮询间隔以减少资源消耗。页面重新可见时恢复正常频率。

## 核心方法分类

`IGitExtension` 接口定义了 40+ 个公共方法，按功能分类如下：

### 仓库操作

| 方法 | HTTP 请求 | 说明 |
|------|----------|------|
| `init(path: string): Promise<void>` | POST `/git/{path}/init` | 在指定路径初始化新的 Git 仓库 |
| `clone(path, url, auth?, versioning?, submodules?): Promise<Git.IResultWithMessage>` | POST `/git/{path}/clone` | 克隆远程仓库到本地；`versioning=false` 时仅复制文件不创建 `.git` |

### 文件暂存操作

| 方法 | HTTP 请求 | 说明 |
|------|----------|------|
| `add(...filename: string[]): Promise<void>` | POST `/git/{path}/add` | 添加指定文件到暂存区 |
| `addAllUnstaged(): Promise<void>` | POST `/git/{path}/add_all_unstaged` | 添加所有未暂存（unstaged）文件 |
| `addAllUntracked(): Promise<void>` | POST `/git/{path}/add_all_untracked` | 添加所有未跟踪（untracked）文件 |
| `reset(filename?: string): Promise<void>` | POST `/git/{path}/reset` | 从暂存区移除文件（`git reset HEAD`），不指定 filename 时重置所有暂存 |

### 提交操作

| 方法 | HTTP 请求 | 说明 |
|------|----------|------|
| `commit(message: string): Promise<void>` | POST `/git/{path}/commit` | 提交暂存的更改，支持 amend |
| `checkout(options?: Git.ICheckoutOptions): Promise<Git.ICheckoutResult>` | POST `/git/{path}/checkout` | 切换分支或丢弃文件更改；新建分支时传入 `startpoint` |
| `checkoutTag(tag: string): Promise<Git.ICheckoutResult>` | POST `/git/{path}/tag_checkout` | 切换到指定标签（detached HEAD） |
| `resetToCommit(hash: string): Promise<void>` | POST `/git/{path}/reset_to_commit` | 重置到指定 commit（硬重置） |
| `revertCommit(message, hash): Promise<void>` | POST `/git/{path}/revert_commit` | 回滚指定 commit 之后的更改 |

### 分支操作

| 方法 | HTTP 请求 | 说明 |
|------|----------|------|
| `refreshBranch(): Promise<void>` | POST `/git/{path}/branch` | 刷新分支列表（内部方法 `_branch()`），检测 HEAD 变化，启停 fetchPoll |
| `deleteBranch(branchName: string): Promise<void>` | POST `/git/{path}/branch/delete` | 删除指定分支（`git branch -D`） |
| `merge(branch: string): Promise<Git.IResultWithMessage>` | POST `/git/{path}/merge` | 合并指定分支到当前分支 |
| `rebase(branch: string): Promise<Git.IResultWithMessage>` | POST `/git/{path}/rebase` | 变基操作 |
| `resolveRebase(action: 'continue'\|'skip'\|'abort')` | POST `/git/{path}/rebase` | 解决变基冲突（continue/skip/abort） |

### 远程操作

| 方法 | HTTP 请求 | 说明 |
|------|----------|------|
| `fetch(auth?): Promise<Git.IResultWithMessage>` | POST `/git/{path}/remote/fetch` | 获取远程更新（不合并） |
| `pull(auth?): Promise<Git.IResultWithMessage>` | POST `/git/{path}/pull` | 拉取远程更新并合并 |
| `push(auth?, force?, remote?): Promise<Git.IResultWithMessage>` | POST `/git/{path}/push` | 推送到远程；`force=true` 强制推送 |
| `addRemote(url, name?): Promise<void>` | POST `/git/{path}/remote/add` | 添加远程仓库 |
| `removeRemote(name: string): Promise<void>` | DELETE `/git/{path}/remote/{name}` | 删除远程仓库 |
| `getRemotes(): Promise<Git.IGitRemote[]>` | GET `/git/{path}/remote/show` | 获取远程仓库列表 |
| `refreshRemotes(): Promise<void>` | — | 刷新远程列表并发出 `remotesChanged` 信号 |

### 标签操作

| 方法 | HTTP 请求 | 说明 |
|------|----------|------|
| `tags(): Promise<Git.ITagResult>` | POST `/git/{path}/tags` | 列出所有标签 |
| `setTag(tagName, commitId): Promise<void>` | POST `/git/{path}/tags` | 在指定 commit 上创建标签 |
| `refreshTag(): Promise<void>` | — | 刷新标签列表并发出 `tagsChanged` 信号 |

### Stash（储藏）操作

| 方法 | HTTP 请求 | 说明 |
|------|----------|------|
| `stashChanges(stashMsg?): Promise<void>` | POST `/git/{path}/stash_save` | 储藏当前工作区更改 |
| `applyStash(index: number): Promise<void>` | POST `/git/{path}/stash_apply` | 应用指定 stash（不删除） |
| `popStash(index?: number): Promise<void>` | POST `/git/{path}/stash_pop` | 弹出并应用 stash（删除 stash 条目） |
| `dropStash(index?: number): Promise<void>` | POST `/git/{path}/stash_drop` | 删除指定 stash 条目 |

### 历史与 Diff

| 方法 | HTTP 请求 | 说明 |
|------|----------|------|
| `log(count?: number): Promise<Git.ILogResult>` | POST `/git/{path}/log` | 获取提交日志（默认 25 条） |
| `detailedLog(hash: string): Promise<Git.ISingleCommitFilePathInfo>` | POST `/git/{path}/detailed_log` | 获取单个 commit 的详细文件变更信息 |
| `diff(previous?, current?): Promise<Git.IDiffResult>` | POST `/git/{path}/diff` | 获取两个引用之间的差异 |

### .gitignore 管理

| 方法 | HTTP 请求 | 说明 |
|------|----------|------|
| `ensureGitignore(): Promise<void>` | POST/GET `/git/{path}/ignore` | 确保 `.gitignore` 文件存在 |
| `ignore(filename, useExtension): Promise<void>` | POST/GET `/git/{path}/ignore` | 添加忽略规则（支持按文件或按扩展名） |
| `readGitIgnore(): Promise<string>` | POST/GET `/git/{path}/ignore` | 读取 `.gitignore` 内容 |
| `writeGitIgnore(content): Promise<void>` | POST/GET `/git/{path}/ignore` | 写入 `.gitignore` 内容 |

### 刷新方法

| 方法 | 说明 |
|------|------|
| `refresh(): Promise<void>` | 全量刷新：刷新状态、分支、标签、stash、远程列表 |
| `refreshStatus(): Promise<void>` | 仅刷新仓库状态（变更文件列表） |
| `refreshDirtyStatus(): Promise<void>` | 检查脏文件（文档管理器中未保存的暂存文件） |

### SSH/Host 管理

| 方法 | HTTP 请求 | 说明 |
|------|----------|------|
| `checkKnownHost(hostname): Promise<boolean>` | GET/POST `/git/known_hosts` | 检查主机是否在 known_hosts 中 |
| `addHostToKnownList(hostname): Promise<void>` | GET/POST `/git/known_hosts` | 添加主机到 known_hosts |

### Diff Provider 注册

| 方法 | 说明 |
|------|------|
| `registerDiffProvider(name, fileExtensions, factory): void` | 按文件扩展名注册专用 Diff Provider |
| `registerFallbackDiffProvider(factory): void` | 注册纯文本回退 Diff Provider（全局唯一） |

## pathRepository Setter：路径发现机制

`pathRepository` 属性表示当前 Git 仓库的根路径，其 setter 实现了核心的仓库路径自动发现机制。当用户在文件浏览器中导航时，主插件 `activate` 函数监听 `fileBrowser.model.pathChanged` 事件，将当前文件夹路径设置给 `gitExtension.pathRepository`。

### Setter 执行流程

1. **调用 showPrefix API**：向 `POST /git/{currentFolder}/show_prefix` 发送请求，执行 `git rev-parse --show-prefix`，获取当前目录相对于仓库根的路径前缀
2. **路径切片计算仓库根**：
   - 如果 `show_prefix` 返回空字符串，说明当前目录就是仓库根，`pathRepository = currentFolder`
   - 如果返回相对前缀 `subdir/`，说明当前目录是仓库根下的子目录，通过字符串切片移除后缀得到仓库根路径：`pathRepository = currentFolder.slice(0, -prefix.length)`
3. **触发刷新**：设置新路径后调用 `refresh()` 全量刷新状态
4. **发出信号**：发出 `repositoryChanged` 信号（参数为 `{ oldValue, newValue }`），通知 UI 仓库路径已变更

### 路径安全检查

内部方法 `_getPathRepository()` 在每次 API 调用前检查 `pathRepository` 是否为 `null`，若为 `null` 则抛出 `Git.NotInRepository` 错误，防止在非 Git 仓库中执行 Git 操作。

## 状态刷新流程

### refreshStatus() 方法

`refreshStatus()` 是最频繁执行的刷新方法，完整流程如下：

1. **发送请求**：向 `POST /git/{path}/status` 发送请求，后端执行 `git status --porcelain=v2 -b`，返回原始状态数据（包含分支信息和文件 xy 状态码）
2. **解码文件状态**：使用 `decodeStage(x, y)` 函数将每个文件的 xy 状态码转换为 `Git.Status` 枚举值：
   - `'??'` → `'untracked'`（未跟踪）
   - x 位为 `M`/`A`/`D`/`R`（index 状态）→ `'staged'`（已暂存）
   - y 位为 `M`/`D`（worktree 状态）→ `'unstaged'`（未暂存）
   - x 位和 y 位都有变更 → `'partially-staged'`（部分暂存）
   - `'DD'`/`'AA'`/`'UU'` 等 → `'unmerged'`（合并冲突）
3. **解析文件类型**：调用 `_resolveFileType(path)` 通过 `docRegistry` 判断文件是文本还是二进制
4. **更新内部状态**：调用 `_setStatus(status)` 更新 `_status` 属性
5. **发出信号**：`_setStatus` 内部发出 `statusChanged` 信号，UI 组件接收到信号后重新渲染变更文件列表
6. **检查脏文件**：调用 `refreshDirtyStatus()` 检查已暂存/修改的文件在文档管理器中是否有未保存的更改（`context.model.dirty`），更新 `hasDirtyFiles` 属性并发出 `dirtyFilesStatusChanged` 信号

### refreshBranch() 方法

1. **发送请求**：调用内部 `_branch()` 方法，向 `POST /git/{path}/branch` 发送请求，后端执行 `git branch -a -v --no-abbrev`，返回分支列表
2. **比较变化**：比较新的分支列表与缓存列表，检测当前分支是否改变、分支列表是否增减
3. **发出信号**：
   - 当前分支（HEAD）改变 → 发出 `headChanged` 信号
   - 分支列表变化 → 发出 `branchesChanged` 信号
4. **管理 fetchPoll**：如果当前分支有远程跟踪分支（upstream），启动 `_fetchPoll`；否则停止
5. **检查远程变更通知**：调用 `checkRemoteChangeNotified()` 检测打开的文件是否落后于远程分支，若设置了 `openFilesBehindWarning`，发出 `remoteChanged` 信号

## TaskHandler：任务执行包装

所有会变更仓库状态的操作（add/commit/push/pull/checkout/merge/rebase/stash 等）都通过 `TaskHandler.execute()` 包装执行。

```typescript
await this._taskHandler.execute<void>('git:add:files', async () => {
  await this._requestAPI<void>(URLExt.join(path, 'add'), 'POST', { filename: files });
});
```

### TaskHandler 的作用

- **任务序列化**：确保同一时间只有一个变更操作在执行，避免并发写操作导致状态不一致
- **进度通知**：执行前通过 `taskChanged` 信号发出任务 ID（如 `'git:add:files'`），UI 可以显示加载指示器；完成后再次发出信号清除指示器
- **错误传递**：操作失败时错误正常抛出，由调用方的 UI 代码处理（显示错误对话框）

### 任务 ID 命名规范

任务 ID 使用 `git:<动作>:<对象>` 格式，例如：
- `'git:add:files'` - 添加文件
- `'git:commit'` - 提交
- `'git:push'` - 推送
- `'git:checkout'` - 切换分支
- `'git:stash:save'` - 保存 stash

## _requestAPI：内部 HTTP 请求方法

所有 API 请求最终通过私有方法 `_requestAPI<T>()` 发送：

```typescript
private async _requestAPI<T>(
  endPoint: string,
  method = 'GET',
  body?: Partial<ReadonlyJSONObject> | null
): Promise<T>
```

- **URL 拼接**：使用 `URLExt.join(pathRepository, endpoint)` 拼接完整 URL
- **方法**：默认 GET，写操作使用 POST/DELETE
- **请求体**：自动 JSON 序列化
- **错误处理**：响应非 ok 时抛出 `Git.GitResponseError`，包含 HTTP 状态码、traceback 和 JSON 响应体
- **基础 URL**：使用 JupyterLab 的 `ServerConnection` 配置，自动附加 base URL 和认证信息

## 内部辅助方法

| 方法 | 说明 |
|------|------|
| `_getPathRepository()` | 确保 pathRepository 不为 null，否则抛出 NotInRepository |
| `_changedFiles(prev, curr, base?)` | 获取两次 commit 之间的变更文件列表（checkout 前使用） |
| `_revertFile(file)` | 关闭并重新打开 JupyterLab 中的文件（checkout 后刷新文档内容） |
| `_resolveFileType(path)` | 通过 docRegistry 解析文件类型（文本/二进制/Notebook） |
| `_clearStatus()` | 清空所有内部状态数据（切换仓库时使用） |
| `_setStatus(status)` | 更新 `_status` 属性并发出 `statusChanged` 信号 |
| `_branch()` | 内部请求分支列表（不触发信号） |
| `_setMarker(repo, branch)` | 创建 BranchMarker 跟踪文件选择状态 |
| `_onSettingsChange(settings)` | 响应设置变化，更新轮询间隔等配置 |

## BranchMarker 内部类

`BranchMarker` 是 GitExtension 内部用于跟踪文件选择状态（Git 面板中每个文件前的复选框）的辅助类：

```typescript
class BranchMarker implements Git.IBranchMarker {
  add(fname: string, mark: boolean): void;    // 标记文件
  get(fname: string): boolean;                // 获取文件标记状态
  set(fname: string, mark: boolean): void;    // 设置文件标记
  toggle(fname: string): void;                // 切换文件标记
}
```

## 错误类型

| 错误类 | 触发条件 |
|--------|---------|
| `Git.NotInRepository` | `pathRepository` 为 `null` 时尝试执行 Git 操作 |
| `Git.GitResponseError` | 后端返回非 ok HTTP 响应（含 traceback 和 json body） |
| `Git.HiddenFile` | 尝试访问 `.git` 目录等隐藏文件 |
| `ServerConnection.NetworkError` | 网络请求失败（后端未启动或网络断开） |

## 模块导出

```typescript
export { GitExtension, getDiffProvider } from './model';
```

除了 `GitExtension` 类外，还导出模块级函数 `getDiffProvider(filename, isText?)`，供 Diff 组件根据文件名查找合适的 Diff Provider 工厂。

## 相关概念

- [插件系统与五个Plugin](/concepts/03-extension-plugin-system.md)
- [REST API通信机制](/concepts/05-rest-api-and-communication.md)
- [可插拔Diff系统](/concepts/06-diff-provider-system.md)
- [架构总览](/concepts/02-architecture-overview.md)
