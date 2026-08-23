---
type: Concept
title: 轮询与信号系统
description: @lumino/polling双Poll轮询(_statusPoll 3s/backoff、_fetchPoll按需)和@lumino/signaling事件驱动20+信号，实现自动状态同步与UI响应。
tags: [polling, signal, lumino, event-driven, refresh, standby, poll, status-poll, fetch-poll, reactivity]
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

## 轮询与信号系统概述

jupyterlab-git 的前端状态同步采用"轮询（Polling）+ 信号（Signaling）"的混合架构。轮询机制负责定期从后端拉取最新仓库状态（解决多客户端/外部命令导致的状态不一致问题），信号机制负责在状态变化时即时通知 UI 组件重渲染。这两种机制分别由 `@lumino/polling` 和 `@lumino/signaling` 两个 Lumino 核心包提供，共同构成了 GitExtension 模型层与 UI 层之间的响应式通信基础。

```
后端 Git 仓库状态
    ↑ 轮询（定期拉取）
GitExtension 模型
    ↓ 信号（即时推送）
React UI 组件
```

轮询解决"外部变化感知"问题（用户在终端执行 git 命令、其他客户端推送等），信号解决"内部变化通知"问题（用户通过 UI 执行操作后模型状态已更新）。两者互补，确保 UI 始终与仓库状态保持同步。

## 双Poll轮询机制

GitExtension 构造时创建两个 Poll 实例，分别负责不同的轮询任务：

### _statusPoll：状态轮询

`_statusPoll` 是核心的状态轮询器，负责定期获取仓库的最新状态（文件变更列表和分支信息）。

| 配置项 | 值 | 说明 |
|--------|-----|------|
| factory | `_refreshModel()` | 轮询工厂方法，执行一次完整的状态刷新 |
| 默认频率 | 3 秒 | 正常情况下每 3 秒轮询一次 |
| 退避策略 | 指数退避（exponential backoff） | 连续失败时自动增大间隔 |
| 最大间隔 | 300 秒（5 分钟） | 退避上限，防止轮询完全停止 |
| auto 启动 | `true` | 插件激活后立即开始轮询 |
| standby | 页面不可见时增大间隔 | 减少后台资源消耗 |

**factory 方法执行内容**：

```typescript
// _refreshModel 执行流程
async function _refreshModel(): Promise<void> {
  await this.refreshStatus();   // POST /git/{path}/status → 文件变更列表
  await this.refreshBranch();   // POST /git/{path}/branch → 分支列表
}
```

`refreshStatus()` 调用 `POST /git/{path}/status` 获取文件变更状态，解析每个文件的 xy 状态码并更新内部 `_status` 属性；`refreshBranch()` 调用 `POST /git/{path}/branch` 获取分支列表，检测 HEAD 变化并管理 _fetchPoll 的启停。

### _fetchPoll：远程获取轮询

`_fetchPoll` 负责定期执行 `git fetch`，使 ahead/behind 提交计数保持最新。

| 配置项 | 值 | 说明 |
|--------|-----|------|
| factory | `_fetchRemotes()` | 执行 git fetch |
| 默认频率 | 与状态轮询相同 | 共享相同的间隔和退避策略 |
| auto 启动 | `false` | 不自动启动，按需启停 |
| 启动条件 | 当前分支有远程跟踪分支 | refreshBranch 检测到 upstream 时调用 `_fetchPoll.start()` |
| 停止条件 | 当前分支无远程跟踪分支 | refreshBranch 未检测到 upstream 时调用 `_fetchPoll.stop()` |

这种按需启动设计避免了在本地分支（无远程跟踪）上执行无意义的 fetch 操作，减少网络请求。当用户切换到有远程跟踪的分支时，fetchPoll 自动开始工作；切换到纯本地分支时自动停止。

### 指数退避策略

Poll 的指数退避（exponential backoff）机制处理后端暂时不可用的情况：

1. 轮询正常时保持 3 秒间隔
2. 某次请求失败（如网络错误、后端超时），下次轮询间隔自动翻倍
3. 间隔持续增大，直到达到 300 秒上限
4. 请求成功后立即恢复 3 秒正常间隔

这种设计在后端临时不可用时不会产生密集的失败请求（雪崩效应），同时在后端恢复后能快速恢复正常轮询。

### standby条件：页面可见性感知

Poll 支持自定义 standby 条件，通过 `refreshStandbyCondition` 可配置。当 JupyterLab 页面不可见时（用户切换到其他浏览器标签或最小化窗口），轮询自动进入 standby 模式：

- 大幅增大轮询间隔（使用退避上限）
- 减少网络请求和 CPU 使用
- 页面重新可见时立即触发一次刷新，恢复正常频率

这是通过浏览器 Page Visibility API 实现的，是前端性能优化的常见模式。

## @lumino/signaling信号系统

信号（Signal）是 Lumino 框架提供的类型安全的事件发布-订阅机制，类似于 Node.js 的 EventEmitter 但具备更好的 TypeScript 类型支持。

### Signal 基本用法

```typescript
import { Signal } from '@lumino/signaling';

// 定义信号
get statusChanged(): ISignal<this, Git.IStatus> {
  return Private.getStatusChangedSignal(this);
}

// 发送信号
this._setStatus(newStatus); // 内部调用 statusChanged.emit(newStatus)

// 订阅信号（React组件中使用UseSignal Hook）
const [status] = UseSignal(model.statusChanged, model.status);
```

每个信号是一个 `ISignal<sender, args>` 类型，sender 是发送信号的对象（this），args 是信号携带的数据类型。

### GitExtension定义的全部信号

`IGitExtension` 接口定义了 13 个核心信号，覆盖所有状态变化场景：

| 信号 | 参数类型 | 触发时机 | 订阅者 |
|------|---------|---------|--------|
| `headChanged` | `void` | HEAD 改变（切换分支、提交、拉取、重置到commit） | 文件浏览器刷新、历史侧栏更新、Diff视图更新 |
| `statusChanged` | `Git.IStatus` | 仓库状态变化（文件变更列表更新） | FileList、CommitBox、StatusWidget |
| `branchesChanged` | `void` | 分支列表变化（新建/删除分支） | BranchMenu/BranchPicker 分支选择器 |
| `repositoryChanged` | `IChangedArgs<string \| null>` | 当前仓库路径变化（切换目录到不同仓库） | 所有需要仓库路径的组件重置状态 |
| `tagsChanged` | `void` | 标签列表变化 | 标签相关UI |
| `stashChanged` | `IChangedArgs<Git.IStash[]>` | Stash列表变化 | GitStash组件 |
| `remotesChanged` | `void` | 远程仓库列表变化 | ManageRemoteDialogue |
| `remoteChanged` | `Git.IRemoteChangedNotification \| null` | 远程分支变化通知（打开文件落后于远程） | 远程变更通知UI |
| `taskChanged` | `string` | 任务执行状态变化（任务开始/结束） | 加载指示器、按钮禁用状态 |
| `selectedHistoryFileChanged` | `Git.IStatusFile \| null` | 历史面板选中的文件变化 | 单文件历史Diff |
| `dirtyFilesStatusChanged` | `boolean` | 脏文件状态变化（有/无未保存的暂存文件） | 提交警告提示 |
| `credentialsRequiredChanged` | `boolean` | 凭证需求变化（需要/不需要认证） | CredentialsBox 显示/隐藏 |
| `submodulesChanged` | `void` | 子模块列表变化 | 子模块UI |

这些信号覆盖了 Git 面板中所有需要响应状态变化的 UI 场景。每个信号的触发都是精确的——只在对应数据实际变化时发出，避免不必要的重渲染。

## 刷新链路：refresh→refreshStatus→refreshBranch→refreshDirtyStatus

GitExtension 实现了分层的刷新方法，从全量刷新到专项刷新，按需调用：

### refresh()：全量刷新

```typescript
async refresh(): Promise<void> {
  await this.refreshStatus();
  await this.refreshBranch();
  await this.refreshRemotes();
  await this.refreshTag();
  // 刷新stash列表
}
```

在以下场景触发：
- `pathRepository` 切换到新仓库时（setter 中调用）
- 用户点击工具栏刷新按钮时
- 执行重大状态变更操作后（如 checkout 分支）

全量刷新确保所有数据都与后端同步，但开销较大，因此不频繁调用。

### refreshStatus()：状态刷新

最频繁执行的刷新方法，也是 `_statusPoll` 的核心调用对象：

1. 发送 `POST /git/{path}/status` 请求
2. 后端执行 `git status --porcelain=v2 -b`，返回 JSON 格式的状态数据
3. 使用 `decodeStage(x, y)` 将 xy 标志转换为 Status 枚举
4. 调用 `_resolveFileType(path)` 通过 docRegistry 判断文件类型
5. 调用 `_setStatus(status)` 更新 `_status` 属性并发出 `statusChanged` 信号
6. 调用 `refreshDirtyStatus()` 检查脏文件

### refreshBranch()：分支刷新

1. 调用内部 `_branch()` 方法（不触发信号的底层请求）发送 `POST /git/{path}/branch`
2. 比较新分支列表与缓存的 `_branches`
3. 检测变化：
   - HEAD 分支改变 → 发出 `headChanged` 信号
   - 分支列表增减 → 发出 `branchesChanged` 信号
4. 管理 _fetchPoll：当前分支有 upstream 时 start，无 upstream 时 stop
5. 调用 `checkRemoteChangeNotified()` 检查远程变更

### refreshDirtyStatus()：脏文件检查

检查当前处于 staged/modified 状态的文件在 JupyterLab 文档管理器中是否有未保存的更改：

1. 遍历 `_status.files` 中状态为 staged/unstaged/partially-staged 的文件
2. 检查每个文件在 docmanager 中是否有打开的文档上下文
3. 检查 `context.model.dirty` 属性（文档是否有未保存修改）
4. 更新 `hasDirtyFiles` 属性
5. 若脏文件状态改变，发出 `dirtyFilesStatusChanged` 信号

此机制防止用户提交时丢失文档管理器中未保存的更改。

## 路径同步机制：pathChanged→pathRepository→showPrefix→refresh

Git 面板需要自动跟随用户在文件浏览器中的导航切换仓库上下文，这通过一条完整的事件链路实现：

### 1. 监听文件浏览器路径变化

在主插件 `activate` 函数中：

```typescript
fileBrowser.model.pathChanged.connect((_, path) => {
  gitExtension.pathRepository = path;
}, this);
```

当用户在文件浏览器中点击导航到不同目录时，`fileBrowser.model.pathChanged` 信号触发，将当前路径设置给 GitExtension。

### 2. pathRepository setter 执行路径发现

```typescript
set pathRepository(value: string | null) {
  // 1. 调用 showPrefix API 获取相对路径前缀
  const prefix = await this._requestAPI<string>(
    URLExt.join(value, 'show_prefix'), 'POST'
  );
  // 2. 通过字符串切片计算仓库根路径
  if (prefix === '') {
    // 当前目录就是仓库根
    this._pathRepository = value;
  } else {
    // 切片移除后缀得到仓库根
    this._pathRepository = value.slice(0, -prefix.length);
  }
  // 3. 触发全量刷新
  await this.refresh();
  // 4. 发出 repositoryChanged 信号
  this._repositoryChanged.emit({ oldValue, newValue: this._pathRepository });
}
```

**showPrefix 原理**：后端执行 `git rev-parse --show-prefix`，返回当前目录相对于 Git 仓库根目录的路径前缀（如 `subdir/nested/`）。如果当前目录本身是仓库根，返回空字符串。通过这个前缀，前端可以精确计算出仓库根路径，而不需要遍历文件系统查找 `.git` 目录。

### 3. 文件变更触发刷新

```typescript
app.serviceManager.contents.fileChanged.connect(() => {
  gitExtension.refreshStatus().catch(console.error);
});
```

监听 JupyterLab 内容管理器的 `fileChanged` 信号——当用户在 JupyterLab 中创建、删除、重命名文件时，立即刷新 Git 状态。这补充了轮询机制的延迟（3 秒间隔），使用户操作后立刻看到状态更新。

### 4. HEAD变化触发文件浏览器刷新

```typescript
gitExtension.headChanged.connect(() => {
  fileBrowser.model.refresh();
});
```

当 HEAD 改变（如 checkout 分支、pull 更新）时，文件浏览器需要刷新以反映可能变化的文件列表（不同分支可能有不同文件）。

### 5. 路径同步链路总结

```
用户在文件浏览器中点击目录
    ↓ pathChanged信号
gitExtension.pathRepository = newPath
    ↓ setter触发
POST /git/{newPath}/show_prefix → 获取相对路径前缀
    ↓ 路径切片
pathRepository = 仓库根路径
    ↓
refresh() 全量刷新（status + branch + remotes + tags）
    ↓ statusChanged/headChanged/branchesChanged信号
React UI 组件重渲染
```

## 事件连接与生命周期

### 信号连接模式

所有外部信号连接（fileBrowser、contents 等）在主插件 activate 函数中建立。GitExtension 内部的信号在模型状态变更方法中发出。

信号连接需要注意内存泄漏：
- Lumino Signal 不依赖 DOM 事件系统，不会自动断开
- GitExtension 实现 `IDisposable` 接口，在 `dispose()` 方法中断开所有信号连接
- React 组件通过 `UseSignal` Hook 自动管理订阅/取消订阅

### 操作触发的即时刷新

用户通过 UI 执行变更操作（add/commit/push/pull 等）后，TaskHandler 在操作完成后不等待下一次轮询，而是立即触发对应的刷新：

```typescript
await this._taskHandler.execute<void>('git:commit', async () => {
  await this._requestAPI<void>(...);
});
// 操作完成后立即刷新
await this.refreshStatus();
await this.refreshBranch();
```

这种"操作后即时刷新 + 定期轮询兜底"的策略兼顾了响应速度和一致性。

## Poll与Signal的协同

轮询和信号不是独立工作的，它们形成一个闭环：

1. **轮询拉取变化**：_statusPoll 定期调用后端，发现外部变化（终端命令、其他客户端操作）
2. **数据更新发出信号**：refreshStatus 中 `_setStatus()` 发出 statusChanged 信号
3. **UI响应信号重渲染**：React 组件通过 UseSignal 订阅信号，读取最新 model 数据重渲染
4. **用户操作触发命令**：UI 操作调用 model 方法（如 commit）
5. **命令执行后即时刷新**：TaskHandler 包装的操作完成后立即刷新，发出信号
6. **轮询继续兜底**：即时刷新之后轮询继续运行，捕获任何遗漏的外部变化

这个闭环确保无论变化来自外部（终端）还是内部（UI 操作），UI 最终都能正确反映当前状态。

## 相关概念

- [GitExtension核心模型](/concepts/04-git-extension-model.md)
- [UI组件与Widget体系](/concepts/07-ui-components-and-widgets.md)
- [命令系统与菜单](/concepts/10-commands-and-menu.md)
- [架构总览](/concepts/02-architecture-overview.md)
- [插件系统与五个Plugin](/concepts/03-extension-plugin-system.md)
