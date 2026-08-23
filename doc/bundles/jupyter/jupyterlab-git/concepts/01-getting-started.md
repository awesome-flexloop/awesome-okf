---
type: Concept
title: 安装与快速上手
description: pip一键安装前后端组件，需Git>=2.0和JupyterLab>=4.0.6，启动后左侧出现Git面板，支持初始化→暂存→提交→推送工作流。
tags: [installation, getting-started, setup, pip, workflow]
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
  - /references/init-py-source.md
---

## 环境要求

在安装 jupyterlab-git 之前，请确保系统满足以下前置条件：

| 依赖 | 最低版本 | 说明 |
|------|---------|------|
| Git | ≥ 2.0 | 系统必须安装 Git 命令行工具，扩展通过调用 git 命令执行所有版本控制操作 |
| JupyterLab | ≥ 4.0.6 | 扩展运行于 JupyterLab 环境，使用 JupyterFrontEndPlugin 机制 |
| Python | ≥ 3.7 | 后端基于 Python 异步框架（anyio/Tornado） |

前端在激活时会通过 `GET /git/settings` 接口检测 Git 版本，若版本低于 2 将无法正常工作。同时会严格校验前后端版本一致性，版本不匹配将抛出错误。

## 安装方法

### pip 一键安装

jupyterlab-git 采用双包结构（前端 labextension + 后端 server extension），通过 pip 安装时会自动安装前后端组件，无需额外的 `jupyter labextension install` 步骤：

```bash
pip install jupyterlab-git
```

安装完成后，pip 包 `jupyterlab-git` 包含两个 Python 包：

- **jupyterlab_git_core**：位于 `packages/core/`，包含 Git 执行引擎（`Git` 类）和构建后的前端静态资源（labextension 目录），通过 `_jupyter_labextension_paths()` 告知 JupyterLab 前端资源位置（映射到 npm 包名 `@jupyterlab/git`）
- **jupyterlab_git**：位于 `packages/jupyterlab/`，包含 Tornado Handlers 和 server extension 注册入口，从 `jupyterlab_git_core` 导入 `__version__` 和 `Git` 类

### 开发模式安装

如果需要从源码开发或修改，可使用开发模式安装：

```bash
git clone https://github.com/jupyterlab/jupyterlab-git.git
cd jupyterlab-git
pip install -e packages/core
pip install -e packages/jupyterlab
jupyter labextension develop packages/core --overwrite
jlpm build
```

## 验证安装

安装完成后，启动 JupyterLab：

```bash
jupyter lab
```

启动后在浏览器中打开 JupyterLab 界面，验证以下内容：

1. **左侧面板出现 Git 图标**：在左侧侧边栏（Sidebar）中应看到 Git 面板图标，rank 为 200
2. **命令面板可用**：按 `Ctrl+Shift+C`（或 `Cmd+Shift+C`）打开命令面板，输入 "git" 应能看到所有 git 相关命令
3. **服务端扩展已加载**：可通过 `jupyter server extension list` 命令检查 `jupyterlab_git` 是否在列表中

## 基本工作流

### 步骤一：初始化或克隆仓库

**方式 A：初始化新仓库**

1. 在 JupyterLab 文件浏览器中导航到目标文件夹
2. 点击 Git 面板顶部的 "Initialize a Repository" 按钮
3. 或使用命令面板执行 `Git: Initialize Repository` 命令
4. 这会调用后端 `POST /git/{path}/init` 接口，执行 `git init`

**方式 B：克隆远程仓库**

1. 点击 Git 面板中的 "Clone a Repository" 按钮
2. 或使用命令面板执行 `Git: Clone a Repository` 命令（`git:clone` CommandID）
3. 在弹出的克隆对话框中输入远程仓库 URL 和本地路径
4. 这会调用后端 `POST /git/{path}/clone` 接口，执行 `git clone`

### 步骤二：查看变更

在 Git 面板中可以查看文件变更状态，文件按以下分类显示：

- **Changed（未暂存）**：工作区中已修改但未暂存的文件，状态为 `unstaged`
- **Staged（已暂存）**：已添加到暂存区的文件，状态为 `staged`
- **Untracked（未跟踪）**：新创建尚未纳入版本控制的文件，状态为 `untracked`

文件状态通过 Poll 轮询自动刷新（默认 3 秒间隔）。点击文件名可以查看 Diff；双击行为可通过设置中的 `fileClickAction` 配置。

### 步骤三：暂存文件

有三种方式暂存文件：

- **暂存单个文件**：悬停在文件名上点击 "+" 按钮，或右键选择 "Stage"，调用 `add(filename)` 方法
- **暂存所有未暂存文件**：点击 Changed 分组标题旁的 "+" 按钮，调用 `addAllUnstaged()` 方法
- **暂存所有未跟踪文件**：点击 Untracked 分组标题旁的 "+" 按钮，调用 `addAllUntracked()` 方法

暂存操作通过 `POST /git/{path}/add` 等接口执行 `git add` 命令。所有变更操作均通过 `TaskHandler` 包装，UI 会显示任务进度。

### 步骤四：提交更改

1. 在暂存区确认要提交的文件
2. 在提交信息输入框中填写提交描述
3. 点击 "Commit" 按钮，或使用 `Git: Commit from Staged` 命令
4. 这会调用 `POST /git/{path}/commit` 接口，执行 `git commit`

提交时系统会自动检查暂存的 Notebook 文件是否包含输出（`checkNotebooksForOutputs()`），可配置为自动清除输出。

### 步骤五：推送到远程

1. 如果已配置远程仓库，点击 "Push" 按钮（或执行 `Git: Push` 命令）
2. 调用 `POST /git/{path}/push` 接口执行 `git push`
3. 首次推送可能需要认证，扩展通过 pexpect 模式支持用户名/密码认证，通过 credential-cache 默认缓存凭证 1 小时

拉取操作类似，点击 "Pull" 按钮执行 `git pull`。

## 常见问题排查

### 问题一：Git 面板不显示

可能原因：
- 服务端扩展未安装：运行 `pip install jupyterlab-git` 确保安装了服务端包
- JupyterLab 需要重启：安装扩展后完全重启 JupyterLab（刷新浏览器可能不够）
- 检查浏览器控制台是否有前端版本不匹配错误

排查命令：
```bash
jupyter server extension list  # 检查 jupyterlab_git 是否启用
jupyter labextension list     # 检查 @jupyterlab/git 是否安装
```

### 问题二：前后端版本不匹配

症状：启动时抛出 "前端版本与Python包版本不匹配" 错误。

原因：前端 npm 包和后端 Python 包版本不一致，通常是由于升级时只升级了其中一方。

解决方案：
```bash
pip install --upgrade jupyterlab-git
jupyter lab build  # 如果需要重建前端
```

### 问题三：Git 命令执行超时

症状：操作长时间无响应后失败。

原因：大仓库或网络问题导致 Git 命令超过默认的 20 秒超时。

解决方案：在 Jupyter 配置文件（`jupyter_server_config.py`）中增加超时时间：

```python
c.JupyterLabGit.git_command_timeout = 60.0
```

### 问题四：认证失败

症状：push/pull 时提示需要凭证但无法输入。

解决方案：
- 扩展支持通过 `AUTH_ERROR_MESSAGES` 列表识别认证错误，自动弹出凭证对话框
- 可配置 `credential_helper` 使用 `store` 持久化凭证：
  ```python
  c.JupyterLabGit.credential_helper = 'store --file ~/.git-credentials'
  ```
- SSH 协议推荐提前在系统中配置好 SSH key 和 known_hosts

### 问题五：面板不自动刷新

症状：文件变更后 Git 面板没有更新。

原因：Poll 轮询可能在页面不可见时进入 standby 模式（指数退避最大 300 秒）。

解决方案：点击 Git 面板中的刷新按钮手动触发 `refresh()`，或等待页面重新获得焦点。

## 配置选项

jupyterlab-git 支持通过 Jupyter 配置文件自定义行为：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `git_command_timeout` | 20.0 | Git 命令执行超时（秒） |
| `credential_helper` | `cache --timeout=3600` | 凭证缓存方式 |
| `excluded_paths` | `[]` | 排除的路径模式（fnmatch 匹配） |
| `actions` | `{}` | Git 命令后执行的钩子命令 |
| `output_cleaning_command` | `jupyter nbconvert` | Notebook 输出清理命令 |
| `output_cleaning_options` | `--ClearOutputPreprocessor.enabled=True --inplace` | 清理命令选项 |

前端设置可通过 JupyterLab Settings Editor 配置，包括 `fileClickAction`（文件点击行为）、`openFilesBehindWarning`（远程变更通知）等。

## 相关概念

- [jupyterlab-git 简介](/concepts/00-introduction.md)
- [架构总览](/concepts/02-architecture-overview.md)
- [GitExtension核心模型](/concepts/04-git-extension-model.md)
- [REST API通信机制](/concepts/05-rest-api-and-communication.md)
