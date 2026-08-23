---
type: Example
title: 分支管理与合并工作流
description: 完整的分支创建、切换、合并、变基和冲突解决操作指南，涵盖功能分支开发模式的最佳实践。
tags: [分支, 合并, 变基, 冲突解决, 功能分支, rebase, merge, branch]
run:
  when: "always"
  command: null
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

## 分支管理概述

分支（Branch）是 Git 最核心的特性之一，它允许你在不影响主代码线的情况下独立开发功能、修复 Bug 或进行实验。jupyterlab-git 提供了完整的分支管理图形界面，支持分支的创建、切换、合并、变基和删除操作。本示例将演示一个典型的功能分支（Feature Branch）开发工作流：从主分支创建功能分支 → 在功能分支上开发提交 → 将功能分支合并回主分支。

## 查看当前分支

### 步骤一：识别当前分支状态

打开 Git 面板后，面板顶部显示当前所在的分支名称（如 `main` 或 `master`），旁边还有当前分支相对于远程的 ahead/behind 计数。分支信息通过 `GitExtension.currentBranch` 属性提供，该属性是一个 `Git.IBranch` 对象，包含以下关键字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | `string` | 分支名称 |
| `is_current_branch` | `boolean` | 是否为当前分支 |
| `is_remote_branch` | `boolean` | 是否为远程分支 |
| `upstream` | `string` | 远程跟踪分支名称（如 `origin/main`） |
| `top_commit` | `string` | 分支最新提交的哈希值 |
| `tag` | `string` | 关联的标签（如果有） |

点击面板顶部的分支按钮，会展开分支列表，列出所有本地分支和远程分支。当前分支在列表中高亮标记。远程分支以 `remotes/` 前缀显示（如 `remotes/origin/main`）。

分支列表通过 `GitExtension.branches` 属性访问，由 `refreshBranch()` 方法刷新，该方法向后端发送 POST `/git/{path}/branch` 请求，执行 `git branch -a -v --no-abbrev` 获取完整的分支信息。

## 创建与切换分支

### 步骤二：创建新分支

在分支列表中点击"New Branch"按钮（或通过 Git 菜单中的分支操作），弹出新建分支对话框。在对话框中输入新分支的名称，例如 `feature/add-data-visualization`。

创建分支时，可以选择"起点"（startpoint）：
- 默认从当前分支的 HEAD（最新提交）创建
- 也可以指定某个特定的提交或标签作为起点

确认后，扩展调用 `GitExtension.checkout()` 方法，传入新建分支的选项：

```typescript
await gitExtension.checkout({
  branchName: 'feature/add-data-visualization',
  startPoint: 'main',  // 从 main 分支创建
  newBranch: true
});
```

该方法向后端发送 POST `/git/{path}/checkout` 请求，后端执行 `git checkout -b <new-branch> <startpoint>`（或等价的 `git switch -c`）。

> **分支命名建议**：使用有意义的前缀加描述的命名方式，如 `feature/xxx`（新功能）、`fix/xxx`（Bug 修复）、`hotfix/xxx`（紧急修复）、`experiment/xxx`（实验性开发），便于团队协作时快速识别分支用途。

### 步骤三：切换分支

在分支列表中点击任意分支名称即可切换到该分支。切换操作同样调用 `GitExtension.checkout()` 方法：

```typescript
await gitExtension.checkout({ branchName: 'feature/add-data-visualization' });
```

后端执行 `git checkout <branch-name>`（或 `git switch <branch-name>`）。

**切换分支的注意事项**：
- 如果当前分支有未提交的更改，而这些更改与目标分支的同一文件有冲突，Git 会阻止切换。此时需要先提交更改、储藏更改（Stash，详见 [Diff查看与Stash使用](/examples/03-diff-and-stash.md)），或丢弃更改
- 切换分支后，`GitExtension.checkout()` 方法会先调用 `_changedFiles()` 获取受影响的文件列表，然后通过 `_revertFile()` 关闭并重新打开这些文件在 JupyterLab 中的文档，确保编辑器中显示的内容与新分支一致
- 切换成功后，面板发出 `headChanged` 信号，触发状态刷新，文件列表更新为新分支的状态

## 在功能分支上开发

### 步骤四：修改文件并提交

切换到功能分支后，正常进行文件编辑、暂存和提交操作（具体流程参见 [基础使用示例](/examples/01-basic-usage.md)）。每完成一个小的功能点或修复，建议做一次提交，保持提交粒度适中、提交信息清晰。

在功能分支上可以进行多次提交，这些提交不会影响主分支。面板顶部始终显示当前所在分支名称，帮助你确认正在哪个分支上工作。

如果需要将功能分支的进度推送到远程仓库进行备份或协作，可以执行 `git:push` 命令。首次推送新分支时，需要设置上游分支（upstream），扩展会自动处理 `-u` 参数。

## 合并分支

### 步骤五：合并功能分支到主分支

当功能开发完成并经过测试后，需要将功能分支的更改合并回主分支：

1. **先切换回主分支**：在分支列表中点击 `main`（或 `master`），切换回主分支
2. **确保主分支是最新的**：执行 `git:pull` 拉取远程最新更改，避免在过时的主分支上合并
3. **触发合并**：通过 Git 菜单执行 `git:merge` 命令（`CommandIDs.gitMerge`），在弹出的分支选择对话框中选择要合并的功能分支（如 `feature/add-data-visualization`）
4. **确认合并**：扩展调用 `GitExtension.merge(branch)` 方法，向后端发送 POST `/git/{path}/merge` 请求，后端执行 `git merge <branch>`

如果合并过程顺利（无冲突），合并自动完成，面板刷新显示新的提交历史。功能分支的提交现在出现在主分支的历史中。

合并成功后，建议执行 `git:push` 将合并后的主分支推送到远程仓库。

### 快进合并（Fast-forward）与三方合并

当主分支在功能分支创建后没有新的提交时，Git 会执行快进合并（fast-forward），直接将主分支指针移动到功能分支的最新提交，不产生额外的合并提交。如果主分支和功能分支都有新的提交，Git 会执行三方合并（three-way merge），自动生成一个合并提交（merge commit）。

如果设置了 `cancelPullMergeConflict` 为 `true`，pull 操作会使用 `--ff-only` 参数，仅允许快进合并。

## 处理合并冲突

### 步骤六：使用 ConflictResolver 解决冲突

当合并的两个分支对同一文件的同一部分做了不同的修改时，Git 无法自动决定保留哪个版本，就会产生合并冲突（merge conflict）。此时：

1. **冲突检测**：后端执行 `git merge` 返回非零退出码，解析出冲突文件列表。前端通过 `refreshStatus()` 检测到仓库状态变为 `MERGING`（`State.MERGING = 2`），冲突文件的状态显示为 `unmerged`
2. **冲突解决面板**：面板切换到冲突解决视图，列出所有存在冲突的文件
3. **打开冲突文件**：点击冲突文件，会打开 Diff 视图（基于 PlainTextDiff Provider，使用 CodeMirror 编辑器），显示三方对比：
   - **Base**（共同祖先版本）：两个分支分叉点的版本
   - **Current**（当前分支版本，即接收合并的分支）：通常是主分支的版本
   - **Incoming**（被合并分支版本）：即功能分支的版本
4. **手动选择或编辑**：在冲突解决界面中，可以选择保留当前版本、保留传入版本，或手动编辑合并后的内容。冲突区域在 CodeMirror 中会有特殊高亮标记
5. **标记为已解决**：对每个冲突文件做出选择后，该文件标记为已解决
6. **完成合并**：所有冲突文件都解决后，暂存已解决的文件，然后提交合并结果（`git commit`），完成合并流程

Notebook 文件（`.ipynb`）的冲突通过 nbdime 库提供语义化的冲突解决视图，可以单元格级别选择保留版本。

> **提示**：合并冲突是正常的开发过程，不必紧张。关键是理解每个冲突区域的代码含义，与相关开发者沟通后做出正确的选择。解决冲突后务必测试合并后的代码是否正常工作。

## 变基操作

### 步骤七：使用 Rebase 整理提交历史

变基（Rebase）是另一种整合分支更改的方式，与 merge 不同，rebase 会将功能分支的提交"重新播放"到目标分支的最新提交之上，产生线性的提交历史，避免了多余的合并提交。

**发起变基**：
1. 切换到功能分支
2. 通过 Git 菜单执行 `git:rebase` 命令（`CommandIDs.gitRebase`）
3. 在对话框中选择目标分支（通常是 `main`）
4. 扩展调用 `GitExtension.rebase(branch)` 方法，后端执行 `git rebase <branch>`

**变基冲突处理**：

如果变基过程中遇到冲突，仓库状态变为 `REBASING`（`State.REBASING = 3`），面板显示冲突解决界面。与合并冲突不同，变基冲突是逐个提交处理的。解决完一个提交的冲突后，需要通过 `git:resolve-rebase` 命令（`CommandIDs.gitResolveRebase`）选择下一步操作：

| 动作 | 参数值 | Git 命令 | 说明 |
|------|--------|---------|------|
| Continue | `'continue'` | `git rebase --continue` | 暂存已解决的文件后继续变基，应用下一个提交 |
| Skip | `'skip'` | `git rebase --skip` | 跳过当前提交，不应用其更改 |
| Abort | `'abort'` | `git rebase --abort` | 放弃变基，回到变基前的状态 |

后端通过 `RebaseAction` 枚举映射这三个动作：`CONTINUE=1`、`SKIP=2`、`ABORT=3`。

> **⚠️ Rebase 安全准则**：
> - **绝对不要**对已经推送到远程公共分支的提交执行 rebase，因为 rebase 会改写提交历史
> - Rebase 只适用于尚未推送的本地分支或你自己的私有分支
> - 如果不确定用 merge 还是 rebase，优先选择 merge（merge 不会改写历史，更安全）
> - Rebase 的优势是提交历史更清晰线性，适合在合并到主分支前整理本地提交

## 删除已合并分支

### 步骤八：清理已合并的分支

合并完成后，功能分支已经完成使命，可以安全删除：

1. 确保当前不在要删除的分支上（先切换到其他分支，如 `main`）
2. 通过分支列表的右键菜单或 Git 菜单找到删除分支选项
3. 选择要删除的分支名称
4. 扩展调用 `GitExtension.deleteBranch(branchName)` 方法，向后端发送 POST `/git/{path}/branch/delete` 请求，后端执行 `git branch -D <branch-name>`

> **注意**：`git branch -D`（大写 D）是强制删除，即使分支未完全合并也会删除。已推送到远程的分支不会被本地删除影响，如需删除远程分支，还需要执行 `git push origin --delete <branch-name>`（目前需通过终端命令执行，可使用 `git:terminal-command` 打开终端）。

## 分支管理最佳实践

### 功能分支模式（Feature Branch Workflow）

这是最常用的 Git 工作流模式，核心规则如下：

1. **主分支保护**：`main`/`master` 分支始终保持可部署状态，不直接在主分支上开发
2. **分支隔离**：每个新功能/修复在独立的分支上开发，分支名使用 `feature/`、`fix/` 等前缀
3. **频繁提交**：在功能分支上小步提交，每个提交对应一个逻辑变更点
4. **定期同步**：开发期间定期从主分支拉取更新（使用 merge 或 rebase），避免最终合并时冲突过多
5. **Pull Request / Merge Request**：通过 PR/MR 进行代码审查后再合并到主分支（jupyterlab-git 本身不提供 PR 功能，需在 Git 平台如 GitHub/GitLab 上操作）
6. **及时清理**：合并后删除已完成的功能分支，保持分支列表整洁

### 分支命名规范建议

| 前缀 | 用途 | 示例 |
|------|------|------|
| `feature/` | 新功能开发 | `feature/user-authentication` |
| `fix/` | Bug 修复 | `fix/login-crash` |
| `hotfix/` | 线上紧急修复 | `hotfix/security-patch` |
| `docs/` | 文档更新 | `docs/api-reference` |
| `experiment/` | 实验性功能 | `experiment/new-ui-layout` |
| `refactor/` | 代码重构 | `refactor/data-model` |

## 相关示例

- [基础使用示例](/examples/01-basic-usage.md)
- [Diff查看与Stash使用](/examples/03-diff-and-stash.md)

## 相关概念

- [GitExtension核心模型](/concepts/04-git-extension-model.md)
- [命令系统与菜单](/concepts/10-commands-and-menu.md)
- [Stash与高级操作](/concepts/12-stash-and-advanced.md)
- [服务端Git执行引擎](/concepts/08-server-git-execution.md)
- [UI组件与Widget体系](/concepts/07-ui-components-and-widgets.md)
