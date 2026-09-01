---
type: Reference
title: GitExtension核心模型 src/model.ts
description: GitExtension类——IGitExtension接口的实现，管理仓库状态、轮询刷新、任务执行和API请求
tags: [model, git-extension, polling, state-management]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: model-ts
    resource: /references/model-ts-source.md
    title: "src/model.ts 源码分析"
---

# GitExtension核心模型 src/model.ts

## 文件位置

`src/model.ts` 实现了 `GitExtension` 类，是整个前端扩展的核心状态管理和业务逻辑层。

## GitExtension类

### 构造函数

```typescript
constructor(
  docmanager: IDocumentManager | null = null,
  docRegistry: DocumentRegistry | null = null,
  settings?: ISettingRegistry.ISettings,
  serverSettings?: ServerConnection.ISettings
)
```

构造函数初始化：
- `_docmanager` / `_docRegistry` - 文档管理器引用
- `_taskHandler = new TaskHandler(this)` - 任务处理器
- `_statusPoll` - Poll实例，默认3秒间隔，指数退避最大300秒
- `_fetchPoll` - Poll实例，auto:false，按需启动fetch轮询
- 设置变化监听 `settings.changed.connect`

### 轮询机制（Poll）

使用 `@lumino/polling` 的 `Poll` 类实现两种轮询：

| Poll | factory | 频率 | auto | 用途 |
|------|---------|------|------|------|
| `_statusPoll` | `_refreshModel` | 3s默认，max 300s，backoff | true | 刷新状态/分支 |
| `_fetchPoll` | `_fetchRemotes` | 同上 | false | 远程fetch（有远程分支时启动） |

standby条件通过 `refreshStandbyCondition` 可自定义。

### Diff Provider注册表

模块级别的全局注册表：

```typescript
const DIFF_PROVIDERS: { [key: string]: { name: string; factory: Git.Diff.Factory } } = {};
const FALLBACK_DIFF_PROVIDER: { factory: Git.Diff.Factory | null } = { factory: null };
```

`getDiffProvider(filename, isText?)` 函数按文件扩展名查找provider：
1. 先查找扩展名匹配的专用provider
2. 如果是文本文件且无专用provider，返回fallback provider

`registerDiffProvider` 按文件扩展名注册，`registerFallbackDiffProvider` 注册文本回退provider（全局唯一）。

### 核心API请求方法

所有Git操作都通过 `_requestAPI` 内部方法：

```typescript
private async _requestAPI<T>(
  endPoint: string,
  method = 'GET',
  body?: Partial<ReadonlyJSONObject> | null
): Promise<T>
```

端点路径拼接：`URLExt.join(pathRepository, endpoint)`，使用 `requestAPI` 函数发送HTTP请求。

### 任务执行包装

所有变更操作都通过 `TaskHandler.execute` 包装：

```typescript
await this._taskHandler.execute<void>('git:add:files', async () => {
  await this._requestAPI<void>(URLExt.join(path, 'add'), 'POST', { ... });
});
```

TaskHandler管理异步任务队列，通过 `taskChanged` 信号通知UI任务状态变化。

### pathRepository setter

路径设置是核心机制——当文件浏览器导航到新路径时：

1. 调用 `showPrefix(currentFolder)` 获取当前目录相对于仓库根的路径
2. 通过路径切片计算仓库根路径 `pathRepository`
3. 触发 `refresh()` 刷新状态
4. 发出 `repositoryChanged` 信号

### 状态刷新流程

`refreshStatus()` 方法：
1. POST `/git/{path}/status` 获取原始状态数据
2. 使用 `decodeStage(x, y)` 将xy状态码转换为Status枚举
3. 通过 `_resolveFileType` 解析文件类型
4. 调用 `_setStatus()` 更新内部状态并发出 `statusChanged`
5. 调用 `refreshDirtyStatus()` 检查脏文件

`refreshBranch()` 方法：
1. 调用 `_branch()` 获取分支列表
2. 比较前后分支/HEAD变化，发出 `headChanged`/`branchesChanged` 信号
3. 如果有远程分支，启动 `_fetchPoll`；否则停止

### 文件状态解码（decodeStage）

`src/utils.ts` 中的 `decodeStage` 函数将Git status的xy标志转换为Status：

| x/y状态 | 映射 |
|---------|------|
| '??' | untracked |
| 'M' / 'A' / 'D' / 'R' in x (index) | staged |
| 'M' / 'D' in y (worktree) | unstaged |
| 部分暂存 | partially-staged |
| 'DD'/'AA'/'UU'等 | unmerged |

### 脏文件检测

`refreshDirtyStatus()` 检查当前处于staged/modified状态的文件在文档管理器中是否有未保存的更改（`context.model.dirty`），设置 `hasDirtyFiles` 属性。

### 远程变更通知

`checkRemoteChangeNotified()` 检测打开的文件是否落后于远程分支，通过 `remoteChanged` 信号发出通知（需设置 `openFilesBehindWarning`）。

### Notebook输出处理

- `checkNotebooksForOutputs()` - 检查暂存的Notebook是否有输出
- `stripNotebooksOutputs(notebooks)` - 清除Notebook输出

### Checkout流程

`checkout()` 方法：
1. 构建请求body（区分分支checkout和文件checkout）
2. 新建分支时传入startpoint
3. checkout前先调用 `_changedFiles` 获取将被影响的文件列表
4. checkout后调用 `_revertFile(file)` 关闭这些文件在JupyterLab中的文档（避免脏状态）
5. 分支checkout后刷新分支列表，文件checkout后刷新状态

### 内部辅助方法

- `_getPathRepository()` - 确保pathRepository不为null，否则抛出NotInRepository
- `_changedFiles(prev, curr, base?)` - 获取两次commit间的变更文件列表
- `_revertFile(file)` - 关闭并重新打开文件以刷新内容
- `_resolveFileType(path)` - 通过docRegistry解析文件类型
- `_clearStatus()` - 清空所有状态数据
- `_setStatus(status)` - 设置状态并发出statusChanged信号
- `_branch()` - 内部请求分支列表
- `_openGitignore()` - 在JupyterLab中打开.gitignore文件
- `_setMarker(repo, branch)` - 设置分支标记（用于文件选择状态）
- `_onSettingsChange(settings)` - 响应设置变化，更新轮询间隔等

### BranchMarker内部类

`BranchMarker` 类跟踪文件选择状态（哪些文件被勾选）：

```typescript
class BranchMarker implements Git.IBranchMarker {
  add(fname: string, mark: boolean): void;
  get(fname: string): boolean;
  set(fname: string, mark: boolean): void;
  toggle(fname: string): void;
}
```

### 错误处理

- `Git.NotInRepository` - 当pathRepository为null时抛出
- `Git.GitResponseError` - 服务器返回非ok响应时抛出
- `Git.HiddenFile` - .gitignore不可访问时抛出（隐藏文件）
- `ServerConnection.NetworkError` - 网络请求失败

## 模块导出

```typescript
export { GitExtension, getDiffProvider } from './model';
```

`getDiffProvider` 作为模块级函数导出，供diff组件使用。

## 相关概念

- [插件入口](index-ts-source.md)
- [REST API通信机制](../concepts/05-rest-api-and-communication.md)
- [轮询与信号系统](../concepts/09-polling-and-signals.md)
- [可插拔Diff系统](../concepts/06-diff-provider-system.md)
- [UI组件与Widget](../concepts/07-ui-components-and-widgets.md)
