---
type: Example
title: Diff查看与Stash使用
description: 掌握文件差异对比的三种视图（Notebook/图片/文本）、提交历史Diff查看，以及Stash储藏更改的完整操作流程。
tags: [diff, 差异对比, stash, 储藏, nbdime, notebook-diff, 图片diff, codemirror]
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
  - /references/index-ts-source.md
  - /references/git-py-source.md
---

## Diff 与 Stash 概述

在日常 Git 工作流中，查看文件变更内容（Diff）和临时保存工作进度（Stash）是两个高频操作。jupyterlab-git 提供了智能化的 Diff 查看系统，根据文件类型自动选择最合适的 Diff 视图，并通过图形化界面支持完整的 Stash 工作流。本示例将详细介绍如何使用 Diff 查看功能对比文件变更，以及如何通过 Stash 灵活管理工作进度。

## 查看文件 Diff

### 步骤一：打开文件 Diff 视图

在 Git 面板的文件列表中，点击任意有变更的文件名即可打开 Diff 视图。也可以右键点击文件，在上下文菜单中选择"Diff"（执行 `git:context-diff` 命令），或通过命令面板执行 `git:show-diff` 命令。

Diff 视图的打开由 `getDiffProvider(filename, isText)` 函数驱动，它根据文件扩展名自动选择合适的 Diff Provider：

1. 提取文件扩展名（转为小写）
2. 在已注册的专用 Provider 中查找匹配
3. 若无专用 Provider 且文件是文本类型，使用回退 Provider
4. 二进制文件无对应 Provider 时显示不支持提示

jupyterlab-git 内置三种 Diff Provider，对应三类文件的 Diff 展示。

### 三种 Diff 视图

#### Notebook Diff（.ipynb 文件）

Notebook 文件（`.ipynb`）使用基于 nbdime 库的 Nbdime Provider 进行语义化 Diff，这是最智能的 Diff 视图。

打开 Notebook Diff 后，你会看到：
- **单元格级别对比**：nbdime 理解 Notebook 的 JSON 结构（cell 数组），能够识别单元格的新增、删除、移动和修改，而非逐行对比原始 JSON
- **输入与输出分离**：分别对比每个单元格的输入代码（source）、输出（outputs）和元数据（metadata）
- **输出忽略选项**：Notebook 的输出（如图表、打印结果）通常不应纳入版本对比，nbdime 可以配置忽略输出差异，专注于代码变更
- **单元格操作**：对于有变更的单元格，以行内 Diff 方式显示具体修改内容，新增行高亮为绿色，删除行高亮为红色

后端 `Git.changed_files()` 方法对 `.ipynb` 文件也使用 nbdime 进行语义化 Diff 计算，确保前端和后端对 Notebook 变更的判断一致。提交前，还可以通过"清除 Notebook 输出"功能（`stripNotebooksOutputs()`）移除输出内容，保持仓库整洁。

#### 图片 Diff（.jpeg/.jpg/.png 文件）

图片文件使用 ImageDiff Provider 提供可视化对比。打开图片 Diff 后：
- 左右并排显示图片的两个版本（参考版本和当前版本）
- 可以直观地看到图片的像素级变化
- 适合对比数据可视化图表、截图等图形资源的变更

图片数据通过后端 `/git/{path}/content` 端点以 base64 编码获取，浏览器解码后在 Diff 视图中渲染。

#### 文本 Diff（所有其他文本文件）

对于没有专用 Diff Provider 的文本文件（`.py`、`.md`、`.json`、`.yaml` 等），系统使用 PlainTextDiff Provider，基于 CodeMirror 编辑器提供文本差异对比：

- **语法高亮**：CodeMirror 根据文件类型自动选择语法高亮模式（如 Python、Markdown、JSON），使 Diff 更易阅读
- **行级与字符级 Diff**：通过 diff 算法计算行级别的增删改，并在修改行内进一步标记字符级别的差异
- **增删标记**：新增行显示绿色背景和 `+` 标记，删除行显示红色背景和 `-` 标记，修改行同时显示
- **并排/内联模式**：支持并排（side-by-side）和内联（inline）两种显示模式
- **三方合并视图**：合并冲突时显示 Base（共同祖先）、Reference（参考版本）、Challenger（当前版本）三栏对比

### Diff 的三种比较场景

jupyterlab-git 支持三种不同的 Diff 比较场景，通过 `SpecialRef` 枚举标识引用来源：

| 场景 | previousRef | currentRef | 说明 |
|------|-------------|------------|------|
| 工作区 vs 暂存区 | `SpecialRef.INDEX` | `SpecialRef.WORKING` | 查看工作区中未暂存的更改（点击未暂存文件默认行为） |
| 暂存区 vs HEAD | `SpecialRef.BASE` | `SpecialRef.INDEX` | 查看已暂存但未提交的更改（点击已暂存文件默认行为） |
| 两个 Commit 之间 | Commit A 哈希 | Commit B 哈希 | 查看两次提交之间的文件变更 |

Diff 内容通过 `Git.Diff.IContent` 接口获取，每个内容对象包含异步 `content` getter（从后端 `/git/{path}/content` 端点获取文件内容）、`label`（版本标签，如"Working Directory"、"HEAD"）、`source`（来源引用类型）。

## 提交历史 Diff

### 步骤二：查看历史提交的变更

在 Git 面板的"History"标签页中，提交历史列表显示了每条提交的基本信息。点击任意一条提交记录，可以查看该提交引入的具体变更：

1. **提交详情**：调用 `GitExtension.detailedLog(hash)` 方法，向后端发送 POST `/git/{path}/detailed_log` 请求，执行 `git show --stat <hash>`，获取该提交变更的文件列表和每个文件的增删行数统计
2. **文件级 Diff**：点击提交详情中的文件名，调用 `GitExtension.diff(previous, current)` 方法，获取该文件在此提交中的具体差异
3. **单文件历史**：右键点击文件列表中的文件，执行 `git:context-history` 命令（`ContextCommandIDs.gitFileHistory`），可以查看某个特定文件的全部提交历史，而非整个仓库的历史

通过 History 面板的 Diff 查看，你可以清晰地追溯每次提交改了什么、谁改的、什么时候改的，是代码审查和问题排查的重要工具。

## 使用 Stash 储藏更改

### Stash 的使用场景

Stash（储藏）是 Git 提供的临时保存工作区更改的机制，在以下场景中非常有用：

- 正在开发功能分支时，需要紧急切换到另一个分支修复 Bug，但不想提交半成品代码
- 拉取远程更新前，工作区有未提交的更改可能与远程更新冲突
- 需要在不同分支之间试验代码，但不想创建临时提交
- 清理工作区以测试某些操作，之后恢复工作进度

Stash 类似于一个临时的"剪贴板栈"，可以将当前未提交的更改（包括暂存区和工作区）压入栈中，之后再弹出恢复。

### 步骤三：储藏当前更改

点击 Git 面板中的"Stash"按钮，或通过菜单/命令面板执行 `git:stash` 命令（`CommandIDs.gitStash`），弹出储藏对话框：

1. **输入储藏信息**（可选）：在对话框中输入描述性信息，帮助你记住这次储藏的内容，如"WIP: feature add-login - 未完成的登录功能"
2. **确认储藏**：点击"Stash"按钮，调用 `GitExtension.stashChanges(stashMsg)` 方法

该方法向后端发送 POST `/git/{path}/stash_save` 请求，后端执行：

```bash
git stash push -m "WIP: feature add-login"
```

执行成功后，工作区恢复到干净状态（与 HEAD 一致），面板的文件列表清空，所有未提交的更改被保存到 stash 栈中。

### 步骤四：查看 Stash 列表

储藏后，可以通过 Git 面板的 Stash 区域查看所有 stash 条目。执行 `git:stash-list` 命令（`CommandIDs.gitStashList`）可以聚焦到 Stash 列表区域。

Stash 列表通过 `GitExtension.stash` 属性访问，每个 stash 条目是一个 `Git.IStashEntry` 对象，包含：

| 字段 | 类型 | 说明 |
|------|------|------|
| `index` | `number` | stash 索引号（0 为最新） |
| `branch` | `string` | 创建 stash 时所在的分支名 |
| `message` | `string` | stash 描述信息 |

后端通过 `Git.stash_list(path)` 方法获取 stash 列表，执行 `git stash list` 命令，使用预编译正则解析输出：

```python
GIT_STASH_LIST = re.compile(
    r'stash@\{(?P<index>\d+)\}: (?P<branch>\S+): (?P<message>.*)'
)
```

解析结果通过 `stashChanged` 信号通知前端 UI 更新。Stash 条目按索引号排列，`stash@{0}` 是最近的储藏，`stash@{1}` 是上一个，以此类推。

### 步骤五：应用 Stash

当你需要恢复之前储藏的更改时，有三种操作可选：

#### Apply（应用，不删除）

点击 stash 条目的"Apply"按钮，调用 `GitExtension.applyStash(index)` 方法，向后端发送 POST `/git/{path}/stash_apply` 请求，执行：

```bash
git stash apply stash@{index}
```

Apply 会将储藏的更改应用到当前工作区，但**保留** stash 条目在栈中。这意味着你可以多次应用同一个 stash 到不同分支。如果应用过程中有冲突，需要像解决合并冲突一样手动处理。

#### Pop（弹出，应用并删除）

点击 stash 条目的"Pop"按钮，或通过菜单执行 `git:stash-pop` 命令（`CommandIDs.gitStashPop`，默认弹出 stash@{0}），调用 `GitExtension.popStash(index)` 方法，执行：

```bash
git stash pop stash@{index}
```

Pop 会将储藏的更改应用到当前工作区，并且**删除**对应的 stash 条目。这是最常用的 stash 操作——储藏更改去做别的事，做完后弹出恢复继续工作。右键菜单中也有 `git:context-stash-pop` 命令可用于 stash 条目上的操作。

#### Drop（删除，不应用）

点击 stash 条目的"Drop"按钮（通常是垃圾桶图标），调用 `GitExtension.dropStash(index)` 方法，执行：

```bash
git stash drop stash@{index}
```

Drop 会删除指定的 stash 条目而不应用其更改。用于丢弃不再需要的储藏内容。

### Stash 使用注意事项

1. **Stash 不包含未跟踪文件**：默认情况下 `git stash push` 只储藏已跟踪文件的更改，未跟踪的新文件不会被储藏。如需包含未跟踪文件，目前需要通过终端命令 `git stash push -u` 执行（可使用 `git:terminal-command` 打开终端）
2. **Stash 是栈结构**：新的 stash 添加到栈顶（index=0），pop 默认从栈顶弹出
3. **分支切换后可应用**：Stash 不绑定到特定分支，你可以在 A 分支储藏，切换到 B 分支后应用
4. **冲突处理**：如果 apply/pop 时发生冲突，需要手动解决冲突后提交，stash 条目不会自动删除（pop 冲突时 stash 不会被移除）
5. **Stash 不是长期存储**：Stash 只是临时保存工作进度的机制，不应用于长期保存重要更改。重要更改应该通过分支和提交来管理

## 实践：典型 Stash 工作流

以下是一个常见的 Stash 使用场景——紧急修复 Bug：

1. 你正在 `feature/new-dashboard` 分支上开发新功能，有多个文件修改了一半
2. 突然收到通知：生产环境发现一个紧急 Bug 需要立即修复
3. 执行 `git:stash`，输入信息"WIP: new-dashboard layout"，储藏当前更改
4. 工作区变干净，切换到 `main` 分支，再创建 `hotfix/critical-bug` 分支
5. 修复 Bug，提交并推送，合并回主分支
6. 切换回 `feature/new-dashboard` 分支
7. 执行 `git:stash-pop`（或在 Stash 列表中点击 Pop），恢复之前的工作进度
8. 继续开发新功能

这个工作流避免了在功能分支上创建无意义的"WIP"提交，保持了提交历史的整洁。

## 相关示例

- [基础使用示例](01-basic-usage.md)
- [分支管理与合并工作流](02-branch-merge-workflow.md)

## 相关概念

- [可插拔Diff系统](../concepts/06-diff-provider-system.md)
- [GitExtension核心模型](../concepts/04-git-extension-model.md)
- [Stash与高级操作](../concepts/12-stash-and-advanced.md)
- [插件入口与Diff Provider注册](../concepts/03-extension-plugin-system.md)
- [UI组件与Widget体系](../concepts/07-ui-components-and-widgets.md)
