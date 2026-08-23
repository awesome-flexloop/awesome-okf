---
type: Reference
title: Token与类型定义 src/tokens.ts
description: IGitExtension接口、Git命名空间类型、CommandIDs枚举——前后端契约的TypeScript类型定义
tags: [typescript, interface, token, api-contract, types]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: tokens-ts
    resource: /references/tokens-ts-source.md
    title: "src/tokens.ts 源码分析"
---

# Token与类型定义 src/tokens.ts

## 文件位置

`src/tokens.ts` 定义了 jupyterlab-git 的所有公共TypeScript类型和Lumino Token，是前端与后端API契约的核心文件。

## 核心Token

```typescript
export const EXTENSION_ID = 'jupyter.extensions.git_plugin';
export const IGitExtension = new Token<IGitExtension>(EXTENSION_ID);
```

`IGitExtension` 是Lumino依赖注入Token，其他插件通过它获取GitExtension实例。

## IGitExtension 接口

`IGitExtension` 继承自 `IDisposable`，定义了Git扩展的完整公共API。

### 数据属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `branches` | `Git.IBranch[]` | 当前仓库的分支列表 |
| `remotes` | `Git.IGitRemote[]` | 远程仓库列表 |
| `tagsList` | `Git.ITag[]` | 标签列表 |
| `currentBranch` | `Git.IBranch \| null` | 当前分支 |
| `submodules` | `Git.ISubmodule[]` | 子模块列表 |
| `pathRepository` | `string \| null` | 仓库根路径 |
| `status` | `Git.IStatus` | 仓库状态 |
| `isReady` | `boolean` | 模型是否就绪 |
| `ready` | `Promise<void>` | 就绪Promise |
| `selectedHistoryFile` | `Git.IStatusFile \| null` | 选中的单文件历史文件 |
| `hasDirtyFiles` | `boolean` | 是否有脏文件（未保存的暂存文件） |
| `credentialsRequired` | `boolean` | 是否需要用户凭证 |
| `stash` | `Git.IStash[]` | Stash列表 |
| `lastAuthor` | `Git.IIdentity \| null` | 最后提交的作者 |

### 信号属性（ISignal）

| 信号 | 参数类型 | 触发时机 |
|------|---------|---------|
| `branchesChanged` | `void` | 分支列表变化 |
| `headChanged` | `void` | HEAD改变（切换分支/提交/拉取等） |
| `tagsChanged` | `void` | 标签变化 |
| `submodulesChanged` | `void` | 子模块变化 |
| `repositoryChanged` | `IChangedArgs<string \| null>` | 当前仓库路径变化 |
| `statusChanged` | `Git.IStatus` | 仓库状态变化 |
| `taskChanged` | `string` | 模型任务事件 |
| `selectedHistoryFileChanged` | `Git.IStatusFile \| null` | 选中的历史文件变化 |
| `remoteChanged` | `Git.IRemoteChangedNotification \| null` | 远程分支变化通知 |
| `remotesChanged` | `void` | 远程列表变化 |
| `dirtyFilesStatusChanged` | `boolean` | 脏文件状态变化 |
| `credentialsRequiredChanged` | `boolean` | 凭证需求变化 |
| `stashChanged` | `IChangedArgs<Git.IStash[]>` | Stash变化 |

### 核心方法

#### 仓库操作
- `init(path: string): Promise<void>` - 初始化新仓库
- `clone(path, url, auth?, versioning?, submodules?): Promise<Git.IResultWithMessage>` - 克隆仓库

#### 文件暂存
- `add(...filename: string[]): Promise<void>` - 添加文件到暂存区
- `addAllUnstaged(): Promise<void>` - 添加所有未暂存文件
- `addAllUntracked(): Promise<void>` - 添加所有未跟踪文件
- `reset(filename?: string): Promise<void>` - 从暂存区移除文件

#### 提交操作
- `commit(message: string): Promise<void>` - 提交暂存的更改
- `checkout(options?: Git.ICheckoutOptions): Promise<Git.ICheckoutResult>` - 切换分支/丢弃文件更改
- `checkoutTag(tag: string): Promise<Git.ICheckoutResult>` - 切换到标签
- `resetToCommit(hash: string): Promise<void>` - 重置到指定commit
- `revertCommit(message, hash): Promise<void>` - 回滚指定commit之后的更改

#### 分支操作
- `refreshBranch(): Promise<void>` - 刷新分支列表
- `deleteBranch(branchName: string): Promise<void>` - 删除分支
- `merge(branch: string): Promise<Git.IResultWithMessage>` - 合并分支
- `rebase(branch: string): Promise<Git.IResultWithMessage>` - 变基
- `resolveRebase(action: 'continue'|'skip'|'abort')` - 解决变基冲突

#### 远程操作
- `fetch(auth?): Promise<Git.IResultWithMessage>` - 获取远程更新
- `pull(auth?): Promise<Git.IResultWithMessage>` - 拉取
- `push(auth?, force?, remote?): Promise<Git.IResultWithMessage>` - 推送
- `addRemote(url, name?): Promise<void>` - 添加远程
- `removeRemote(name: string): Promise<void>` - 删除远程
- `getRemotes(): Promise<Git.IGitRemote[]>` - 获取远程列表
- `refreshRemotes(): Promise<void>` - 刷新远程列表

#### 标签操作
- `tags(): Promise<Git.ITagResult>` - 列出标签
- `setTag(tagName, commitId): Promise<void>` - 创建标签
- `refreshTag(): Promise<void>` - 刷新标签列表

#### Stash操作
- `stashChanges(stashMsg?): Promise<void>` - 储藏更改
- `applyStash(index: number): Promise<void>` - 应用stash
- `popStash(index?: number): Promise<void>` - 弹出stash
- `dropStash(index?: number): Promise<void>` - 删除stash

#### 历史与Diff
- `log(count?: number): Promise<Git.ILogResult>` - 获取提交日志
- `detailedLog(hash: string): Promise<Git.ISingleCommitFilePathInfo>` - 获取commit详情
- `diff(previous?, current?): Promise<Git.IDiffResult>` - 获取diff

#### .gitignore管理
- `ensureGitignore(): Promise<void>` - 确保.gitignore存在
- `ignore(filename, useExtension): Promise<void>` - 添加忽略规则
- `readGitIgnore(): Promise<string>` - 读取.gitignore内容
- `writeGitIgnore(content): Promise<void>` - 写入.gitignore

#### Diff Provider注册
- `registerDiffProvider(name, fileExtensions, factory): void` - 注册diff provider
- `registerFallbackDiffProvider(factory): void` - 注册回退diff provider

#### SSH/Host管理
- `checkKnownHost(hostname): Promise<boolean>` - 检查已知主机
- `addHostToKnownList(hostname): Promise<void>` - 添加已知主机

#### 刷新方法
- `refresh(): Promise<void>` - 全量刷新
- `refreshStatus(): Promise<void>` - 刷新状态
- `refreshDirtyStatus(): Promise<void>` - 刷新脏文件状态

## Git命名空间类型

### 枚举类型

```typescript
// 文件状态枚举
type Status = 'untracked' | 'staged' | 'unstaged' | 'partially-staged' 
  | 'remote-changed' | 'unmodified' | 'unmerged' | 'stashed' | null;

// 仓库状态枚举
enum State {
  DEFAULT = 0,
  DETACHED = 1,
  MERGING = 2,
  REBASING = 3,
  CHERRY_PICKING = 4
}

// Diff特殊引用
enum SpecialRef { WORKING, INDEX, BASE }

// 文件点击行为
type FileClickAction = 'select-only' | 'open-on-double' | 'diff-on-double' | 'diff-on-single';
```

### 核心数据接口

| 接口 | 关键字段 | 用途 |
|------|---------|------|
| `IStatus` | branch, remote, ahead, behind, state, files | 仓库完整状态 |
| `IStatusFile` | x, y, to, from, is_binary, status, type | 单个变更文件状态 |
| `IBranch` | is_current_branch, is_remote_branch, name, upstream, top_commit, tag | 分支信息 |
| `ISingleCommitInfo` | commit, author, date, commit_msg, pre_commits | 单条提交记录 |
| `IAuth` | username, password, cache_credentials | 认证信息 |
| `IDiffResult` | code, command, message, result[] | Diff结果 |
| `IStashEntry` | index, branch, message | Stash条目 |
| `ITag` | name, baseCommitId | 标签 |
| `IGitRemote` | name, url | 远程仓库 |

### Diff相关接口

- `Git.Diff.IModel` - diff模型（challenger/reference/base内容、filename、changed信号）
- `Git.Diff.IContent` - diff内容（content异步getter、label、source、updateAt）
- `Git.Diff.IContext` - diff上下文（currentRef/previousRef/baseRef）
- `Git.Diff.IFactoryOptions` - diff widget创建选项
- `Git.Diff.Factory` - diff widget工厂函数类型
- `Git.Diff.IDiffWidget` - diff widget接口（model、getResolvedFile、isFileResolved、refresh）

### 错误类

- `Git.GitResponseError` - HTTP响应错误（含traceback和json body）
- `Git.NotInRepository` - 不在Git仓库中
- `Git.HiddenFile` - 隐藏文件不可访问

## 命令ID枚举

### CommandIDs（全局命令）

```typescript
enum CommandIDs {
  gitUI = 'git:ui',
  gitTerminalCommand = 'git:terminal-command',
  gitInit = 'git:init',
  gitOpenUrl = 'git:open-url',
  gitToggleSimpleStaging = 'git:toggle-simple-staging',
  gitManageRemote = 'git:manage-remote',
  gitClone = 'git:clone',
  gitMerge = 'git:merge',
  gitOpenGitignore = 'git:open-gitignore',
  gitPush = 'git:push',
  gitPull = 'git:pull',
  gitRebase = 'git:rebase',
  gitResolveRebase = 'git:resolve-rebase',
  gitResetToRemote = 'git:reset-to-remote',
  gitSubmitCommand = 'git:submit-commit',
  gitShowDiff = 'git:show-diff',
  gitStash = 'git:stash',
  gitStashPop = 'git:stash-pop',
  gitStashList = 'git:stash-list'
}
```

### ContextCommandIDs（上下文菜单命令）

```typescript
enum ContextCommandIDs {
  gitCommitAmendStaged = 'git:context-commitAmendStaged',
  gitFileAdd = 'git:context-add',
  gitFileDiff = 'git:context-diff',
  gitFileDiscard = 'git:context-discard',
  gitFileDelete = 'git:context-delete',
  gitFileOpen = 'git:context-open',
  gitFileUnstage = 'git:context-unstage',
  gitFileStage = 'git:context-stage',
  gitFileTrack = 'git:context-track',
  gitFileHistory = 'git:context-history',
  gitIgnore = 'git:context-ignore',
  gitIgnoreExtension = 'git:context-ignoreExtension',
  gitNoAction = 'git:no-action',
  openFileFromDiff = 'git:open-file-from-diff',
  gitFileStashPop = 'git:context-stash-pop',
  gitTagAdd = 'git:context-tag-add'
}
```

## 相关概念

- [GitExtension核心模型](/concepts/04-git-extension-model.md)
- [REST API通信机制](/concepts/05-rest-api-and-communication.md)
- [插件系统与五个Plugin](/concepts/03-extension-plugin-system.md)
- [可插拔Diff系统](/concepts/06-diff-provider-system.md)
