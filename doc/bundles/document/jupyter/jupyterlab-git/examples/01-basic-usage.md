---
type: Example
title: 基础使用示例
description: 从零开始使用jupyterlab-git的完整流程，覆盖安装、仓库初始化/克隆、暂存提交、推送拉取和历史查看等日常操作。
tags: [入门, 基础, 安装, 克隆, 提交, 推送, 拉取, 新手教程]
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
  - /references/index-ts-source.md
  - /references/model-ts-source.md
  - /references/tokens-ts-source.md
---

## 安装与启动

### 步骤一：安装 jupyterlab-git

使用 pip 安装 jupyterlab-git 扩展及其服务端依赖：

```bash
pip install jupyterlab-git
```

安装完成后，jupyterlab-git 会作为 JupyterLab 的服务端扩展（server extension）自动注册，无需手动启用。服务端采用双 Python 包结构：`jupyterlab_git_core` 提供 Git 命令执行引擎，`jupyterlab_git` 提供 Tornado REST API 端点。前端扩展通过 `_jupyter_labextension_paths()` 入口点告知 JupyterLab 静态资源位置，会随 JupyterLab 启动自动加载。

> **前置条件**：系统需安装 Git 2.0 及以上版本，JupyterLab 版本需 ≥ 4.0.6。前端启动时会自动校验前后端版本一致性，版本不匹配将抛出错误。

### 步骤二：启动 JupyterLab 并定位 Git 面板

启动 JupyterLab：

```bash
jupyter lab
```

启动后，在 JupyterLab 界面左侧可以看到 Git 面板图标（一个 Git 分支形状的图标），该面板的 rank 值为 200，位于文件浏览器等核心面板附近。点击该图标即可打开 Git 面板，也可以通过命令面板（快捷键 `Ctrl+Shift+C`）搜索 "Git" 执行 `git:ui` 命令来激活面板。

如果当前工作目录不在任何 Git 仓库中，面板会显示提示信息，提供初始化仓库和克隆仓库两个操作入口。

## 仓库初始化与克隆

### 步骤三A：克隆远程仓库

如果需要从远程仓库获取代码，点击面板中的"Clone a Repository"按钮，或通过命令面板执行 `git:clone` 命令，将弹出克隆对话框。

在克隆对话框中：
1. **仓库 URL**：输入远程仓库地址，支持 HTTPS（如 `https://github.com/user/repo.git`）和 SSH（如 `git@github.com:user/repo.git`）两种协议
2. **目标路径**：选择克隆到本地的目录
3. **认证信息**（HTTPS 私有仓库需要）：输入用户名和密码/Token，可勾选"记住凭证"选项缓存认证信息

点击"Clone"按钮后，扩展调用 `GitExtension.clone()` 方法，向后端发送 POST `/git/{path}/clone` 请求，后端执行 `git clone` 命令。克隆成功后，文件浏览器自动导航到新克隆的目录，Git 面板刷新显示仓库状态。

### 步骤三B：初始化新仓库

如果要从零开始创建 Git 仓库，先在 JupyterLab 文件浏览器中导航到目标目录，然后点击面板中的"Initialize a Repository"按钮，或通过命令面板执行 `git:init` 命令。该命令调用 `GitExtension.init(path)` 方法，向后端发送 POST `/git/{path}/init` 请求，执行 `git init` 初始化仓库。初始化成功后，面板自动刷新，显示当前分支为 `main`（或 `master`，取决于 Git 全局配置）。

## 基本文件操作

### 步骤四：创建与编辑文件

在 JupyterLab 中正常创建和编辑文件即可：新建 Notebook（`.ipynb`）、Python 脚本（`.py`）、Markdown 文档（`.md`）等。文件保存后，Git 面板会通过 Poll 轮询机制（默认 3 秒间隔）自动检测到文件变更。

文件在面板中按状态分组显示：
- **未跟踪（Untracked）**：新建的、从未被 Git 跟踪的文件，标记为 `??`
- **未暂存（Unstaged）**：已被跟踪但有修改、尚未添加到暂存区的文件
- **已暂存（Staged）**：已添加到暂存区、等待提交的文件

每个文件前有复选框，用于选择要暂存/取消暂存的文件。

### 步骤五：暂存文件

暂存文件有以下几种方式：

**单个文件暂存**：点击文件名旁边的 `+` 号按钮，或勾选文件前的复选框。这会调用 `GitExtension.add(filename)` 方法，将文件添加到暂存区，对应执行 `git add <filename>`。

**暂存所有未暂存文件**：点击面板中的"全部暂存"按钮（一个双 `+` 号图标），调用 `addAllUnstaged()` 方法，对应执行批量 `git add`。

**跟踪未跟踪文件**：对于未跟踪的新文件，点击文件旁的 `+` 号会调用 `add()` 方法，将新文件纳入 Git 跟踪并加入暂存区。也可以通过右键菜单执行 `git:context-track` 命令。

**取消暂存**：对于已暂存的文件，点击 `-` 号按钮或取消勾选复选框，调用 `GitExtension.reset(filename)` 方法，对应执行 `git reset HEAD <filename>`，将文件从暂存区移除但不影响工作区内容。

也可以右键点击文件，在上下文菜单中选择"Stage"（`git:context-stage`）或"Unstage"（`git:context-unstage`）。

### 步骤六：提交更改

暂存文件后，面板底部的 CommitBox（提交框）变为可用状态：

1. **输入提交信息**：在 CommitBox 的文本框中输入提交说明（commit message），简要描述本次更改的内容
2. **提交**：点击"Commit"按钮，或按 `Ctrl+Enter`（当 CommitBox 聚焦时），这会执行 `git:submit-commit` 命令

提交操作调用 `GitExtension.commit(message)` 方法，向后端发送 POST `/git/{path}/commit` 请求，执行 `git commit -m <message>`。提交成功后，面板自动刷新状态，已暂存的文件消失，提交历史更新。

> **脏文件警告**：如果 JupyterLab 中有未保存的文件（文档管理器中 `context.model.dirty === true`），CommitBox 旁会显示警告提示，提醒先保存文件再提交，避免提交磁盘上的旧版本。

> **修改上一次提交（Amend）**：在有暂存文件的情况下，右键菜单中的 `git:context-commitAmendStaged` 命令可用于修改上一次提交（`git commit --amend`）。

## 远程同步

### 步骤七：推送到远程仓库

提交本地更改后，需要推送到远程仓库。点击面板工具栏的"Push"按钮（上箭头图标），或通过菜单/命令面板执行 `git:push` 命令。

推送操作调用 `GitExtension.push()` 方法：
- 如果是首次推送且未设置远程仓库，需要先通过 `git:manage-remote` 命令添加远程仓库（调用 `addRemote(url, name)`，默认名称为 `origin`）
- 向后端发送 POST `/git/{path}/push` 请求，执行 `git push`
- 推送成功后，面板的 ahead/behind 计数更新

**凭证处理**：如果远程仓库需要认证（如 HTTPS 私有仓库），推送失败后扩展会自动检测到需要凭证，设置 `credentialsRequired = true`，面板显示 CredentialsBox（凭证输入框）。输入用户名和密码/Token 后，扩展携带凭证重新推送。若勾选"记住我"，后端使用 `git credential-cache` 缓存凭证（默认 1 小时）。

**SSH 主机信任**：首次通过 SSH 连接远程主机时，扩展会调用 `checkKnownHost(hostname)` 检查主机是否在 `known_hosts` 中。若不在，弹出 SSH 指纹确认对话框，确认后调用 `addHostToKnownList(hostname)` 添加主机信任。

### 步骤八：从远程拉取更新

当远程仓库有新的提交时，需要拉取更新到本地。点击面板工具栏的"Pull"按钮（下箭头图标），或执行 `git:pull` 命令。

拉取操作调用 `GitExtension.pull()` 方法，向后端发送 POST `/git/{path}/pull` 请求，执行 `git pull`，将远程分支的更新拉取并合并到本地。如果拉取过程中遇到合并冲突，面板会切换到冲突解决视图。

如果设置了 `cancelPullMergeConflict` 为 `true`，pull 命令会使用 `--ff-only` 参数执行快进合并，无法快进时拒绝合并以避免产生意外的 merge commit。

面板顶部会显示当前分支相对于远程的 ahead/behind 计数（如 `↑2 ↓1` 表示本地领先 2 个提交、落后 1 个提交），帮助判断是否需要推送或拉取。

## 查看提交历史

### 步骤九：浏览历史记录

点击 Git 面板顶部的"History"标签页，可以查看当前分支的提交历史。历史记录通过调用 `GitExtension.log(count)` 方法获取，后端执行 `git log` 命令，默认显示最近 25 条提交。

每条历史记录显示：
- **提交哈希**（短格式）
- **提交作者**
- **提交日期**
- **提交信息**

点击某条提交记录，可以查看该提交的详细变更信息，包括变更的文件列表和每个文件的具体 Diff（通过 `detailedLog(hash)` 和 `diff()` 方法获取）。

在 History 标签页中，还可以在历史提交节点上右键执行 `git:context-tag-add` 命令创建标签（Tag），用于标记版本发布点。

## 常见问题

### Q1：点击 git:init 提示"Not in a Git repository"怎么办？

这个错误（`Git.NotInRepository`）表示当前 `pathRepository` 为 null，即当前目录不在任何 Git 仓库中且初始化未成功。请确保：
- 你有当前目录的写入权限
- 当前目录路径不含特殊字符
- 尝试通过文件浏览器导航到目标目录后再执行初始化

### Q2：推送时提示需要凭证但无法输入？

当推送需要认证时，面板会自动显示 CredentialsBox 凭证输入框。如果没有显示，请检查：
- 远程 URL 是否正确（执行 `git:manage-remote` 查看远程配置）
- 网络连接是否正常
- 如果使用 HTTPS，密码应为 Personal Access Token（GitHub 等平台已不再支持密码认证）
- 如果使用 SSH，请确保 SSH 密钥已配置且已添加主机信任

### Q3：Git 面板不显示或按钮灰显？

这通常是因为服务端扩展未正确安装或加载：
1. 确认已执行 `pip install jupyterlab-git`
2. 运行 `jupyter server extension list` 检查 `jupyterlab_git` 是否在列表中且状态为 enabled
3. 检查浏览器控制台是否有版本不匹配错误（前后端版本必须一致）
4. 重启 JupyterLab 服务

### Q4：文件变更不自动刷新？

Git 面板通过 Poll 轮询机制（默认 3 秒间隔）自动刷新状态。如果变更不显示：
- 确认文件已保存（未保存的文件不会被 Git 检测到）
- 检查面板顶部是否显示当前分支名称（表明仓库已正确识别）
- 可点击面板中的刷新按钮手动触发刷新

## 相关示例

- [分支管理与合并工作流](02-branch-merge-workflow.md)
- [Diff查看与Stash使用](03-diff-and-stash.md)

## 相关概念

- [jupyterlab-git简介](../concepts/00-introduction.md)
- [安装与快速上手](../concepts/01-getting-started.md)
- [GitExtension核心模型](../concepts/04-git-extension-model.md)
- [命令系统与菜单](../concepts/10-commands-and-menu.md)
- [可插拔Diff系统](../concepts/06-diff-provider-system.md)
