---
type: Facts
okf_version: '0.2'
generated: '2026-08-22'
tags:
- jupyter
- jupyterlab
- git
- version-control
- extension
- diff
sources:
- ../../../../../external/libs/jupyter/jupyterlab-git/package.json
- ../../../../../external/libs/jupyter/jupyterlab-git/packages/core/pyproject.toml
- ../../../../../external/libs/jupyter/jupyterlab-git/schema/plugin.json
- ../../../../../external/libs/jupyter/jupyterlab-git/specification/Git_REST_API.yml
- ../../../../../external/libs/jupyter/jupyterlab-git/src/tokens.ts
- ../../../../../external/libs/jupyter/jupyterlab-git/src/model.ts
- ../../../../../external/libs/jupyter/jupyterlab-git/src/git.ts
- ../../../../../external/libs/jupyter/jupyterlab-git/packages/core/jupyterlab_git_core/git.py
- ../../../../../external/libs/jupyter/jupyterlab-git/src/taskhandler.ts
title: jupyterlab-git 源码事实清单
---

# jupyterlab-git Facts

## 项目元数据

- F-001: package.json:2 — npm 包名为 `@jupyterlab/git`。
- F-002: package.json:3 — 版本号为 `0.54.1`。
- F-003: package.json:4 — 描述为 "A JupyterLab extension for version control using git"。
- F-004: package.json:8 — 许可证为 BSD-3-Clause。
- F-005: package.json:58 — 包管理器使用 `yarn@3.5.0`。
- F-006: packages/core/pyproject.toml:6 — Python 核心包名为 `jupyterlab-git-core`。
- F-007: packages/core/pyproject.toml:9 — 要求 Python >= 3.10，支持 3.10-3.14。

## 项目结构

- F-008: packages/core/ — Python 后端核心包（jupyterlab_git_core），包含 git.py、handlers.py、log.py、ssh.py。
- F-009: packages/jupyterlab/ — JupyterLab 服务器扩展包（jupyterlab_git），包含 handlers.py。
- F-010: src/ — TypeScript 前端源码，包含 components/、widgets/、style/ 等目录。
- F-011: src/components/ — React UI 组件：GitPanel、CommitBox、FileList、HistorySideBar、BranchMenu、Diff 组件等 25+ 组件。
- F-012: src/components/diff/ — Diff 视图组件：PlainTextDiff、NotebookDiff、ImageDiff、DiffModel。
- F-013: src/widgets/ — Lumino Widget：GitWidget、GitCloneForm、CredentialsBox、AuthorBox 等。
- F-014: schema/plugin.json — JupyterLab 设置 schema。
- F-015: specification/Git_REST_API.yml — REST API 规范定义。
- F-016: ui-tests/ — Playwright UI 端到端测试，包含 10 个测试 spec。

## 核心依赖

- F-017: package.json:90 — 使用 `diff-match-patch: ^1.0.4` 进行文本差异计算。
- F-018: package.json:91 — 使用 `filesize: ^10.0.7` 格式化文件大小。
- F-019: package.json:92-93 — 集成 `nbdime: ^7.0.1` 和 `nbdime-jupyterlab: ^3.0.1` 处理 Notebook 差异。
- F-020: package.json:94-95 — 使用 `react: ^18.2.0` 和 `react-dom: ^18.2.0`。
- F-021: package.json:96-97 — 使用 `react-virtualized-auto-sizer` 和 `react-window` 实现虚拟滚动文件列表。
- F-022: package.json:98 — 使用 `typestyle: ^2.0.1` 进行 CSS-in-JS 样式。
- F-023: package.json:86-89 — UI 组件库使用 MUI v5（@mui/material、@mui/icons-material、@mui/lab、@mui/styles）。
- F-024: packages/core/pyproject.toml:26-31 — Python 后端依赖：anyio、nbformat、packaging、pexpect、traitlets。
- F-025: packages/core/pyproject.toml:37 — nbdime 作为可选依赖（`nbdime~=4.0.1`）。

## 扩展 Token 与接口

- F-026: src/tokens.ts:11 — 扩展 ID 为 `jupyter.extensions.git_plugin`。
- F-027: src/tokens.ts:13 — `IGitExtension` Token 是扩展的核心依赖注入标识。
- F-028: src/tokens.ts:16 — `IGitExtension` 接口继承 `IDisposable`，定义了 Git 扩展的完整 API 表面。

## 核心数据模型

- F-029: src/tokens.ts:20-40 — 维护核心仓库状态：branches、remotes、tagsList、currentBranch、submodules。
- F-030: src/tokens.ts:116 — `status` 属性返回 `Git.IStatus`，包含 branch、remote、ahead、behind、state、files。
- F-031: src/tokens.ts:913-934 — `Git.State` 枚举定义 5 种仓库状态：DEFAULT(0)、DETACHED、MERGING、REBASING、CHERRY_PICKING。
- F-032: src/tokens.ts:1348-1357 — 文件状态类型：untracked、staged、unstaged、partially-staged、remote-changed、unmodified、unmerged、stashed、null。
- F-033: src/tokens.ts:1022-1029 — `Git.IBranch` 接口包含 is_current_branch、is_remote_branch、name、upstream、top_commit、tag。
- F-034: src/tokens.ts:1127-1129 — `Git.IStatusFile` 扩展 IStatusFileResult，添加 status 字段。
- F-035: src/tokens.ts:1220-1233 — `Git.ISingleCommitInfo` 包含 commit hash、author、date、commit_msg、pre_commits 等。

## 信号系统

- F-036: src/tokens.ts:45 — `branchesChanged` 信号在分支列表变化时发射。
- F-037: src/tokens.ts:50 — `headChanged` 信号在 HEAD 变化时发射。
- F-038: src/tokens.ts:55 — `tagsChanged` 信号在标签列表变化时发射。
- F-039: src/tokens.ts:60 — `submodulesChanged` 信号在子模块变化时发射。
- F-040: src/tokens.ts:70-73 — `repositoryChanged` 信号在当前仓库路径变化时发射，携带 IChangedArgs<string | null>。
- F-041: src/tokens.ts:121 — `statusChanged` 信号在仓库状态变化时发射，携带 Git.IStatus。
- F-042: src/tokens.ts:126 — `taskChanged` 信号在模型任务事件发生时发射。
- F-043: src/tokens.ts:111 — `credentialsRequiredChanged` 信号在凭据需求变化时发射。
- F-044: src/tokens.ts:154 — `dirtyFilesStatusChanged` 信号在暂存区脏文件状态变化时发射。

## Git 操作 API

- F-045: src/tokens.ts:170 — `add(...filename)` 方法将文件添加到暂存区，无参数则添加所有文件。
- F-046: src/tokens.ts:181 — `addAllUnstaged()` 添加所有未暂存文件。
- F-047: src/tokens.ts:192 — `addAllUntracked()` 添加所有未跟踪文件。
- F-048: src/tokens.ts:244 — `checkout(options?)` 支持切换分支、创建新分支、检出文件。
- F-049: src/tokens.ts:255 — `checkoutTag(tag)` 检出指定标签版本。
- F-050: src/tokens.ts:282-288 — `clone(path, url, auth?, versioning?, submodules?)` 支持克隆仓库，可选递归子模块。
- F-051: src/tokens.ts:300 — `commit(message)` 提交所有暂存更改。
- F-052: src/tokens.ts:324 — `deleteBranch(branchName)` 删除分支。
- F-053: src/tokens.ts:352 — `diff(previous?, current?)` 获取两个提交之间的差异。
- F-054: src/tokens.ts:385 — `fetch(auth?)` 拉取远程更新以获取 ahead/behind 状态。
- F-055: src/tokens.ts:454 — `log(historyCount?)` 获取提交日志。
- F-056: src/tokens.ts:466 — `merge(branch)` 合并分支。
- F-057: src/tokens.ts:489 — `pull(auth?)` 从远程拉取更改。
- F-058: src/tokens.ts:502-506 — `push(auth?, force?, remote?)` 推送更改到远程，支持强制推送。
- F-059: src/tokens.ts:518 — `rebase(branch)` 将当前分支变基到指定分支。
- F-060: src/tokens.ts:530-532 — `resolveRebase(action)` 支持 continue/skip/abort 三种变基解决操作。
- F-061: src/tokens.ts:639 — `reset(filename?)` 将文件从暂存区移回未暂存区。
- F-062: src/tokens.ts:655 — `resetToCommit(hash)` 将仓库重置到指定提交。
- F-063: src/tokens.ts:668 — `revertCommit(message, hash)` 回滚指定提交之后的更改。
- F-064: src/tokens.ts:717 — `stashChanges(stashMsg?)` 储藏当前更改。
- F-065: src/tokens.ts:224 — `applyStash(index)` 应用指定储藏。
- F-066: src/tokens.ts:364 — `dropStash(index?)` 删除指定储藏或清空所有储藏。
- F-067: src/tokens.ts:477 — `popStash(index?)` 弹出储藏。
- F-068: src/tokens.ts:213 — `addRemote(url, name?)` 添加远程仓库。
- F-069: src/tokens.ts:600 — `removeRemote(name)` 删除远程仓库。
- F-070: src/tokens.ts:431 — `ignore(filename, useExtension)` 添加 .gitignore 条目。

## 轮询与自动刷新

- F-071: src/model.ts:15 — 默认状态刷新间隔为 3000ms。
- F-072: src/model.ts:84-92 — 使用 Lumino Poll 进行状态轮询，支持 backoff 退避（最大 300 秒）。
- F-073: src/model.ts:93-102 — 远程 fetch 轮询默认不自动启动（auto: false），同样支持 backoff。
- F-074: src/model.ts:91-101 — 轮询支持 standby 条件（`_refreshStandby`），在不可见时暂停。
- F-075: src/tokens.ts:90 — `refreshStandbyCondition` 允许自定义模型刷新待机条件。

## Diff 提供者系统

- F-076: src/tokens.ts:608-612 — `registerDiffProvider(name, fileExtensions, factory)` 为指定文件扩展名注册 diff 提供者。
- F-077: src/tokens.ts:623 — `registerFallbackDiffProvider(factory)` 注册文本文件的回退 diff 提供者，仅一个生效。
- F-078: src/model.ts:39-53 — `getDiffProvider(filename, isText?)` 查找逻辑：先按扩展名查找，找不到且 isText 为 true 时使用回退提供者。
- F-079: src/tokens.ts:900-907 — `Git.Diff.SpecialRef` 枚举定义三个特殊引用：WORKING(0)、INDEX(1)、BASE(2)。
- F-080: src/tokens.ts:855-888 — `Git.Diff.IModel` 接口包含 challenger/reference/base 内容、filename、repositoryPath、hasConflict。
- F-081: src/tokens.ts:753-773 — `Git.Diff.IDiffWidget` 接口要求实现 model、getResolvedFile()、isFileResolved、refresh()。

## 命令系统

- F-082: src/tokens.ts:1433-1450 — `ContextCommandIDs` 枚举定义 15 个上下文菜单命令（git:context-add、git:context-diff、git:context-discard 等）。
- F-083: src/tokens.ts:1455-1475 — `CommandIDs` 枚举定义 17 个全局命令（git:ui、git:clone、git:push、git:pull 等）。
- F-084: src/tokens.ts:1460 — `git:terminal-command` 命令用于在终端中执行 Git 命令。
- F-085: src/tokens.ts:1460 — `git:toggle-simple-staging` 切换简单暂存模式。

## 前端 API 通信层

- F-086: src/git.ts:29-80 — `requestAPI<T>()` 函数封装 Jupyter ServerConnection 请求，自动处理 JSON 解析和错误。
- F-087: src/git.ts:9-14 — 定义 4 种认证错误消息：Invalid username/password、could not read Username/Password、Authentication error。
- F-088: src/git.ts:70-76 — 错误响应时抛出 `Git.GitResponseError`，包含 message、traceback 和 JSON 响应体。

## Python 后端

- F-089: packages/core/jupyterlab_git_core/git.py:5 — 使用 anyio 进行异步 I/O，pexpect 处理交互式 Git 命令（如 SSH 认证）。
- F-090: packages/core/jupyterlab_git_core/git.py:23-27 — nbdime 为可选导入，提供 Notebook diff/merge 能力。
- F-091: packages/core/jupyterlab_git_core/git.py:58-66 — 使用进程级 `anyio.Lock`（`_execution_lock`）串行化 Git 命令执行。
- F-092: packages/core/jupyterlab_git_core/git.py:38-40 — 设置 NFS 等文件系统的锁等待：最多等待 5 秒，每 0.1 秒检查一次。
- F-093: packages/core/jupyterlab_git_core/git.py:42 — 使用正则 `GIT_VERSION_REGEX` 解析 Git 版本输出。
- F-094: packages/core/jupyterlab_git_core/git.py:44-46 — 使用正则 `GIT_BRANCH_STATUS` 解析 `git status -b` 输出获取分支和 ahead/behind 信息。
- F-095: packages/core/jupyterlab_git_core/git.py:54-56 — 使用正则 `GIT_STASH_LIST` 解析 `git stash list` 输出。

## 错误类型

- F-096: src/tokens.ts:1376-1404 — `Git.GitResponseError` 继承 ServerConnection.ResponseError，添加 traceback 和 JSON 响应体。
- F-097: src/tokens.ts:1405-1409 — `Git.NotInRepository` 错误表示当前路径不在 Git 仓库中。
- F-098: src/tokens.ts:1411-1417 — `Git.HiddenFile` 错误表示文件是隐藏文件无法访问。
- F-099: packages/core/jupyterlab_git_core/git.py:69-72 — `GitParameterError` 表示 Git 操作缺少必需参数。
- F-100: packages/core/jupyterlab_git_core/git.py:75-80 — `GitCommandError` 表示 Git 命令意外失败，携带 command 属性。

## 设置与配置

- F-101: src/tokens.ts:743-747 — `FileClickAction` 类型控制文件点击行为：select-only、open-on-double、diff-on-double、diff-on-single。
- F-102: package.json:167-201 — JupyterLab 扩展配置标记为 extension: true，schemaDir: "schema"，输出到 packages/core/jupyterlab_git_core/labextension。
- F-103: package.json:191-198 — nbdime 和 nbdime-jupyterlab 作为共享包（singleton）不打包，使用外部安装版本。
- F-104: packages/core/pyproject.toml:65-83 — 使用 hatch-jupyter-builder 构建，开发模式下 build_cmd 为 install:extension。

## 版本生成

- F-105: package.json:20 — 构建时使用 `genversion --es6 --semi src/version.ts` 自动生成版本文件。
- F-106: package.json:36 — prepare 脚本也运行 genversion 确保版本文件存在。

## TaskHandler

- F-107: src/model.ts:78 — GitExtension 构造时创建 `TaskHandler` 实例管理异步任务。
- F-108: src/taskhandler.ts — TaskHandler 用于跟踪和管理 Git 操作的异步任务执行（从 model.ts 导入）。

## 凭据与认证

- F-109: src/tokens.ts:106 — `credentialsRequired` 布尔值指示是否需要用户提供凭据。
- F-110: src/tokens.ts:1279-1283 — `Git.IAuth` 接口包含 username、password、cache_credentials 字段。
- F-111: src/widgets/CredentialsBox.tsx — 凭据输入对话框组件。

## 虚拟列表与性能

- F-112: package.json:96-97 — 使用 react-window + react-virtualized-auto-sizer 实现文件列表虚拟滚动，处理大量文件时的性能问题。
