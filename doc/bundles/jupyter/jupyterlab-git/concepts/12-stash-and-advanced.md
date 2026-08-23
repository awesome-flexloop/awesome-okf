---
type: Concept
title: Stash与高级操作
description: Stash储藏/应用/弹出/删除、Rebase冲突解决、Merge冲突处理、Reset重置、Tag管理、Submodule支持、SSH known_hosts管理和凭证处理等高级Git功能。
tags: [stash, rebase, merge, reset, tag, submodule, ssh, credentials, notebook-output, dirty-files, advanced]
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
  - /references/git-py-source.md
---

## Stash与高级操作概述

除了基础的 add/commit/push/pull 操作外，jupyterlab-git 还实现了完整的 Git 高级功能集，包括 Stash（储藏）管理、Rebase/Merge 冲突解决、Reset 重置、Tag 标签管理、Submodule 子模块支持、SSH known_hosts 管理、Notebook 输出处理、远程变更通知、脏文件检测和凭证管理。这些功能覆盖了日常 Git 工作流中的高级场景，使 jupyterlab-git 成为一个功能完备的 Git GUI。

## Stash（储藏）功能

Stash 是 Git 提供的临时保存工作区更改的机制，允许用户在不提交的情况下切换分支或拉取远程更新。jupyterlab-git 通过 GitExtension 的四个 Stash 方法和 GitStash UI 组件提供完整的 Stash 操作支持。

### Stash API方法

| 方法 | HTTP请求 | 后端Git命令 | 说明 |
|------|---------|------------|------|
| `stashChanges(stashMsg?)` | POST `/git/{path}/stash_save` | `git stash push -m <msg>` | 储藏当前工作区更改，可选消息 |
| `applyStash(index: number)` | POST `/git/{path}/stash_apply` | `git stash apply stash@{index}` | 应用指定 stash（不删除 stash 条目） |
| `popStash(index?: number)` | POST `/git/{path}/stash_pop` | `git stash pop stash@{index}` | 弹出并应用 stash（删除 stash 条目） |
| `dropStash(index?: number)` | POST `/git/{path}/stash_drop` | `git stash drop stash@{index}` | 删除指定 stash 条目 |

### Stash列表获取

Stash 列表通过后端 `stash_list(path)` 方法获取，执行 `git stash list` 命令，使用预编译正则 `GIT_STASH_LIST` 解析输出：

```python
GIT_STASH_LIST = re.compile(
    r'stash@\{(?P<index>\d+)\}: (?P<branch>\S+): (?P<message>.*)'
)
```

解析出每个 stash 条目的索引号、所属分支和消息。前端通过 refresh 流程更新 `stash` 属性，并通过 `stashChanged` 信号通知 GitStash 组件。

### GitStash UI组件

GitStash 组件展示 stash 列表并提供操作入口：
- 显示每个 stash 条目的索引号、分支名和消息
- 提供 Apply/Pop/Drop 操作按钮
- 通过 `stashChanged` 信号自动更新列表
- 在面板中作为可展开区域，与文件列表共享空间

### 全局Stash命令

命令系统提供三个 Stash 相关的全局命令：
- `git:stash`（`git:stash`）：储藏当前更改，弹出输入框输入可选消息
- `git:stash-pop`（`git:stash-pop`）：弹出最近的 stash（index=0）
- `git:stash-list`（`git:stash-list`）：显示/聚焦 stash 列表区域

上下文菜单中还有 `git:context-stash-pop`，用于在 stash 条目上右键弹出。

## Rebase（变基）操作

Rebase 是 Git 中用于整理提交历史的高级操作，jupyterlab-git 支持发起 rebase 和解决 rebase 冲突。

### 发起Rebase

```typescript
async rebase(branch: string): Promise<Git.IResultWithMessage>
```

发送 POST 请求到 `/git/{path}/rebase`，后端执行 `git rebase <branch>`。如果 rebase 顺利完成（无冲突），返回成功消息并触发刷新。如果遇到冲突，Git 返回非零退出码，后端解析冲突文件列表，前端进入冲突解决状态。

### 解决Rebase冲突

```typescript
async resolveRebase(action: 'continue' | 'skip' | 'abort')
```

当 rebase 遇到冲突时，用户可以通过三个动作解决：

| 动作 | Git命令 | 说明 |
|------|---------|------|
| `'continue'` | `git rebase --continue` | 解决冲突后继续 rebase（需先暂存解决后的文件） |
| `'skip'` | `git rebase --skip` | 跳过当前 commit |
| `'abort'` | `git rebase --abort` | 放弃 rebase，回到操作前状态 |

后端通过 `RebaseAction` 枚举映射：
```python
class RebaseAction(Enum):
    CONTINUE = 1
    SKIP = 2
    ABORT = 3
```

### Rebase状态检测

后端 `status()` 方法通过 `GIT_REBASING_BRANCH` 正则检测是否处于 rebase 状态。当检测到 rebase 中时，仓库状态（State）为 `REBASING`，前端显示冲突解决面板而非正常的文件列表。

全局命令 `git:resolve-rebase`（`CommandIDs.gitResolveRebase`）在冲突状态下可用，触发冲突解决流程。

## Merge（合并）操作

```typescript
async merge(branch: string): Promise<Git.IResultWithMessage>
```

发送 POST 请求到 `/git/{path}/merge`，后端执行 `git merge <branch>`。合并操作的处理逻辑与 rebase 类似：
- 无冲突时：合并成功，刷新状态
- 有冲突时：后端返回冲突信息，前端显示冲突文件列表，用户手动解决冲突后通过暂存+commit 完成合并

### cancelPullMergeConflict设置

当 `cancelPullMergeConflict` 设置为 `true` 时，pull 命令使用 `--ff-only` 参数执行快进合并。如果无法快进（存在分叉），pull 被拒绝而不产生合并提交，避免意外的 merge commit。

## Reset（重置）操作

jupyterlab-git 提供两种级别的 Reset 操作：

### reset()：重置暂存区

```typescript
async reset(filename?: string): Promise<void>
```

执行 `git reset HEAD <filename>`，将指定文件从暂存区移除（取消暂存）。如果不指定 filename，重置所有暂存文件。这对应 FileItem 中取消勾选文件的操作，是一个"软重置"，不影响工作区文件内容。

后端对应 `Git.reset()` 方法：
```python
async def reset(self, path: str, filename: Optional[str] = None):
    if filename:
        return await self.__execute(['git', 'reset', 'HEAD', '--', filename], cwd=top_repo_path)
    else:
        return await self.__execute(['git', 'reset', 'HEAD'], cwd=top_repo_path)
```

### resetToCommit()：硬重置到指定Commit

```typescript
async resetToCommit(hash: string): Promise<void>
```

发送 POST 请求到 `/git/{path}/reset_to_commit`，后端执行 `git reset --hard <hash>`，将当前分支硬重置到指定 commit。这是一个**危险操作**，会丢弃工作区所有未提交的更改，前端在执行前显示确认对话框。

### gitResetToRemote：重置到远程状态

全局命令 `git:reset-to-remote`（`CommandIDs.gitResetToRemote`）执行硬重置到远程分支状态（`git reset --hard origin/<branch>`），放弃所有本地未推送的提交，使本地与远程完全一致。

## Tag（标签）管理

Tag 用于标记特定的提交点（如版本发布），jupyterlab-git 支持标签的列出、创建和检出。

### 标签API

| 方法 | HTTP请求 | 说明 |
|------|---------|------|
| `tags(): Promise<Git.ITagResult>` | POST `/git/{path}/tags` | 列出所有标签 |
| `setTag(tagName: string, commitId: string): Promise<void>` | POST `/git/{path}/tags` | 在指定 commit 上创建标签 |
| `checkoutTag(tag: string): Promise<Git.ICheckoutResult>` | POST `/git/{path}/tag_checkout` | 切换到标签（detached HEAD） |
| `refreshTag(): Promise<void>` | — | 刷新标签列表并发出 `tagsChanged` 信号 |

后端 Git 类对应方法：
- `tags(path)` → `git tag -l`，解析输出为标签列表
- `tag(path, tag_name, commit_id)` → `git tag <tag_name> <commit_id>`
- `checkout_tag(path, tag)` → `git checkout tags/<tag>`（进入 detached HEAD 状态）

### 标签数据结构

```typescript
interface ITag {
  name: string;          // 标签名
  baseCommitId: string;  // 标签指向的 commit hash
}
```

### 新建标签对话框

NewTagDialog 模态对话框提供标签创建 UI：输入标签名称，选择目标 commit（默认当前 HEAD），确认后调用 `setTag()`。上下文菜单中的 `git:context-tag-add`（`ContextCommandIDs.gitTagAdd`）在历史提交节点上右键可用，直接在该 commit 上创建标签。

## Submodule（子模块）支持

jupyterlab-git 支持 Git Submodule（子模块）的基本展示：

```typescript
// IGitExtension 接口
readonly submodules: Git.ISubmodule[];
readonly submodulesChanged: ISignal<this, void>;
```

- `submodules` 属性列出当前仓库的子模块
- `submodulesChanged` 信号在子模块列表变化时发出
- 子模块信息通过 `git submodule status` 获取并解析

当前版本中子模块支持主要是状态展示，子模块的更新、初始化等操作需要通过命令行完成。

## SSH known_hosts管理

当通过 SSH 协议连接远程仓库（如 `git@github.com:user/repo.git`）时，首次连接需要验证远程主机的 SSH 指纹。jupyterlab-git 提供了 known_hosts 管理功能：

### SSH API

| 方法 | HTTP请求 | 说明 |
|------|---------|------|
| `checkKnownHost(hostname: string): Promise<boolean>` | GET/POST `/git/known_hosts` | 检查主机是否在 known_hosts 中 |
| `addHostToKnownList(hostname: string): Promise<void>` | GET/POST `/git/known_hosts` | 将主机添加到 known_hosts |

后端通过 `jupyterlab_git_core.ssh.SSH` 类实现：

```python
class SSH:
    def check_known_host(self, hostname: str) -> bool:
        """检查主机是否在 ~/.ssh/known_hosts 中"""
    def add_host_to_known(self, hostname: str) -> None:
        """添加主机到 known_hosts（通过 ssh-keyscan 获取指纹）"""
```

### SSHHandler基类

SSH 相关 Handler 继承自 `SSHHandler` 基类：

```python
class SSHHandler(APIHandler):
    auth_resource = SSH_AUTH_RESOURCE  # "ssh"
    @property
    def ssh(self) -> SSH:
        return SSH()
```

当用户执行 push/pull 操作且远程 URL 使用 SSH 协议时，前端先调用 `checkKnownHost()` 检查主机是否可信。如果不在 known_hosts 中，显示主机指纹确认对话框，用户确认后调用 `addHostToKnownList()` 添加主机。

## Notebook输出检查与清除

针对 Jupyter Notebook 工作流，jupyterlab-git 提供了 Notebook 输出管理功能：

### checkNotebooksForOutputs()

```typescript
async checkNotebooksForOutputs(notebooks?: string[]): Promise<boolean>
```

GET `/git/{path}/check_notebooks`，后端使用 nbdime 检查暂存区中的 Notebook 文件是否包含输出（outputs）。Notebook 的输出（如图表、打印结果）通常不应提交到版本控制，此功能在提交前提醒用户清除输出。

后端 `Git.check_notebooks()` 方法：
```python
async def check_notebooks(self, path, notebooks):
    """使用 nbdime 检查暂存的 Notebook 是否有输出"""
```

### stripNotebooksOutputs()

```typescript
async stripNotebooksOutputs(notebooks: string[]): Promise<void>
```

POST `/git/{path}/strip_notebooks`，后端使用 nbconvert 清除 Notebook 输出：

```python
async def strip_notebooks(self, path, notebooks):
    for nb in notebooks:
        # 使用配置的 output_cleaning_command 和 output_cleaning_options
        # 默认: jupyter nbconvert --ClearOutputPreprocessor.enabled=True --inplace <notebook>
```

清除后自动暂存文件，用户可以直接提交不含输出的 Notebook。

输出清理命令可通过 `output_cleaning_command` 和 `output_cleaning_options` 配置自定义。

## 远程变更通知：checkRemoteChangeNotified

```typescript
checkRemoteChangeNotified(): Promise<void>
```

此方法在 `refreshBranch()` 中被调用，检测当前打开的文件是否落后于远程分支的版本：

1. 遍历文档管理器中当前打开的文件
2. 检查这些文件是否在 Git 跟踪中
3. 比较文件的本地版本与远程分支版本（通过 `git diff` 或 `git fetch` 后的 ahead/behind 信息）
4. 如果检测到远程有更新但本地文件未刷新，通过 `remoteChanged` 信号发出通知
5. 仅当 `openFilesBehindWarning` 设置为 `true` 时启用

通知通过 `IRemoteChangedNotification` 数据结构传递：

```typescript
interface IRemoteChangedNotification {
  files: string[];  // 落后于远程的文件列表
}
```

前端接收到通知后可以显示提示，建议用户刷新文件或拉取更新。

## 脏文件检测：hasDirtyFiles

脏文件（dirty files）指在 JupyterLab 文档管理器中有未保存修改、但已经被 Git 暂存（staged）或修改（modified）的文件。提交这类文件会导致提交内容与磁盘上的文件不一致（提交的是旧版本）。

### 检测机制

`refreshDirtyStatus()` 方法在每次 `refreshStatus()` 之后调用：

1. 遍历当前状态中的 staged/unstaged/partially-staged 文件
2. 对每个文件检查文档管理器中是否有对应的打开上下文
3. 检查 `context.model.dirty` 属性（文档是否有未保存更改）
4. 如果存在任何脏文件，设置 `hasDirtyFiles = true`
5. 脏文件状态变化时发出 `dirtyFilesStatusChanged` 信号

### 信号与UI响应

```typescript
readonly hasDirtyFiles: boolean;
readonly dirtyFilesStatusChanged: ISignal<this, boolean>;
```

CommitBox 组件订阅 `dirtyFilesStatusChanged` 信号，当有脏文件时：
- 在提交按钮旁显示警告提示
- 提醒用户先保存文件再提交，避免提交不完整的更改

## 凭证处理

jupyterlab-git 实现了完整的 HTTPS 认证流程，处理 push/pull/fetch/clone 时的用户名密码输入。

### credentialsRequired 状态

```typescript
readonly credentialsRequired: boolean;
readonly credentialsRequiredChanged: ISignal<this, boolean>;
```

- 当 Git 操作因缺少认证失败时，模型设置 `credentialsRequired = true` 并发出信号
- CredentialsBox 组件接收到信号后显示用户名/密码输入表单
- 用户提交凭证后，原始操作携带凭证重试

### IAuth认证信息

```typescript
interface IAuth {
  username: string;
  password: string;
  cache_credentials: boolean;  // 是否缓存凭证
}
```

- `cache_credentials`：用户勾选"记住我"时为 true，后端通过 `credential-cache` helper 缓存凭证
- 凭证通过 `POST /git/{path}/push|pull|fetch|clone` 的请求体传递给后端
- 后端 `execute()` 函数检测到 username/password 参数时切换到 pexpect 认证模式

### 后端凭证缓存

后端 Git 类管理 `git credential-cache` daemon 进程：
- 默认缓存超时 3600 秒（1小时），由 `credential_helper` 配置控制
- `_GIT_CREDENTIAL_CACHE_DAEMON_PROCESS` 类变量跟踪 daemon 进程
- Git 对象析构时终止 daemon 进程，防止进程泄漏
- 管理员可配置 `credential_helper` 使用 `store`（文件持久化）或其他自定义 helper

### 认证流程

```
用户点击 Push
    ↓
model.push() → POST /git/{path}/push（无凭证）
    ↓
后端执行 git push → HTTPS认证失败
    ↓
返回错误（需要认证）
    ↓
前端设置 credentialsRequired = true → 发出信号
    ↓
CredentialsBox 显示，用户输入用户名/密码
    ↓
model.push(auth) → POST /git/{path}/push（含IAuth）
    ↓
后端 execute(cmd, username, password) → pexpect模式
    ↓
pexpect等待 Username/Password 提示并自动发送
    ↓
推送成功 → credentialsRequired = false
```

如果用户勾选了缓存凭证，后续的 push/pull 操作在缓存有效期内不需要再次输入密码。

## revertCommit：回滚提交

```typescript
async revertCommit(message: string, hash: string): Promise<void>
```

POST `/git/{path}/revert_commit`，执行 `git revert <hash>` 创建一个新的提交来撤销指定 commit 的更改。与 reset 不同，revert 不会改写历史，而是创建一个反向提交，适合在已推送的分支上安全地撤销更改。

## Git.GitResponseError与错误处理

高级操作涉及更多错误场景，统一通过 `Git.GitResponseError` 处理：

```typescript
class GitResponseError extends Error {
  constructor(response: IGitResponse);
  readonly response: IGitResponse;
}
```

错误响应体包含 HTTP 状态码、错误消息和 traceback，前端根据错误类型显示不同的处理 UI：
- 认证错误（401/403）→ 显示 CredentialsBox
- 合并冲突 → 显示冲突解决面板
- 网络错误 → 显示网络错误提示
- Git 命令错误 → 显示 stderr 内容

## 相关概念

- [GitExtension核心模型](/concepts/04-git-extension-model.md)
- [服务端Git执行引擎](/concepts/08-server-git-execution.md)
- [命令系统与菜单](/concepts/10-commands-and-menu.md)
- [UI组件与Widget体系](/concepts/07-ui-components-and-widgets.md)
- [轮询与信号系统](/concepts/09-polling-and-signals.md)
- [配置系统](/concepts/11-configuration-and-settings.md)
