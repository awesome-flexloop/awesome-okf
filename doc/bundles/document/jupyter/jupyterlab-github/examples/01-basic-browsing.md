---
okf_version: "0.2"
type: example
title: "基础浏览：浏览 GitHub 仓库"
description: "从零开始，在 JupyterLab 中浏览 GitHub 仓库、打开 Notebook 并运行、使用 MyBinder 启动仓库的完整流程"
tags: [browsing, navigation, notebook, mybinder, quickstart, file-browser]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T14:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: readme
    resource: "../../../../../external/libs/jupyter/jupyterlab-github/README.md"
    title: "README.md"
  - id: browser-ts
    resource: "/references/browser-ts-source.md"
    title: "浏览器 UI 组件源码"
---

# 基础浏览：浏览 GitHub 仓库

本示例演示如何在 JupyterLab 中使用 jupyterlab-github 扩展浏览 GitHub 仓库、查看文件和运行 Notebook。

## 前置条件

- JupyterLab 4.x 已安装
- jupyterlab-github 已通过 `pip install jupyterlab-github` 安装
- 推荐配置服务端 Access Token（避免速率限制），参见[认证配置示例](02-setup-authentication.md)

## 步骤 1：打开 GitHub 浏览器

1. 启动 JupyterLab：`jupyter lab`
2. 查看左侧面板，找到 GitHub 标签页（Octocat 猫图标）
3. 点击该标签页，进入 GitHub 文件浏览器

初始状态下，文件列表区域显示提示 "Please enter a GitHub user name"，顶部输入框显示占位文字 "GitHub User"。

## 步骤 2：输入用户名/组织名

1. 点击顶部的输入框
2. 输入一个 GitHub 用户名或组织名，例如 `jupyterlab`
3. 按 **Enter** 键或点击输入框外部（blur）

文件浏览器会导航到该用户/组织的仓库列表，每个仓库显示为一个"文件夹"。

> 如果输入的用户名不存在，会显示红色错误面板："username" appears to be an invalid user name!

## 步骤 3：浏览仓库列表

仓库列表中，每个条目显示仓库名称。点击仓库名（文件夹）进入该仓库。

以 `jupyterlab/jupyterlab-github` 为例：
1. 输入 `jupyterlab`，看到该组织下的所有仓库
2. 找到并点击 `jupyterlab-github` 文件夹

进入仓库后，你会看到仓库根目录的文件列表，例如：
- `README.md`
- `package.json`
- `pyproject.toml`
- `src/`（目录）
- `jupyterlab_github/`（目录）
- `binder/`（目录）等

## 步骤 4：打开文件

### 打开 Markdown 文件

点击 `README.md` 文件，JupyterLab 会用 Markdown 预览器打开它。

### 打开 Notebook

如果仓库中有 `.ipynb` 文件（如 `examples/` 目录下），点击即可在 Notebook 编辑器中打开。打开后：
1. Notebook 以只读模式加载（文件内容来自 GitHub）
2. 可以选择 Kernel（如 Python 3）
3. 可以执行单元格——代码在**你的本地 JupyterLab 环境**中运行，不是在 GitHub 上
4. 但**无法保存**回 GitHub（所有写入操作返回 "Repository is read only"）

### 打开文本文件

点击 `.py`、`.json`、`.ts` 等文本文件，会用对应的编辑器打开，可以查看代码内容。

## 步骤 5：使用工具栏按钮

### 刷新按钮

点击工具栏上的刷新图标（圆形箭头），手动刷新当前目录的文件列表。注意自动刷新间隔为 5 分钟，频繁刷新容易触发速率限制。

### 在 GitHub 中打开

点击 GitHub 猫图标按钮（第二个工具栏按钮），会在浏览器新标签页中打开当前路径对应的 GitHub 网页：
- 在用户列表页：打开 https://github.com/jupyterlab
- 在仓库根目录：打开 https://github.com/jupyterlab/jupyterlab-github
- 在子目录：打开 https://github.com/jupyterlab/jupyterlab-github/tree/master/src

> 注意：当前代码硬编码分支名为 `master`。如果仓库的默认分支是 `main`，链接可能 404。

### Launch Binder 按钮

如果仓库根目录存在 Binder 配置文件（`requirements.txt`、`environment.yml`、`apt.txt`、`REQUIRE`、`Dockerfile` 或 `binder/` 目录），Binder 按钮（binder 图标）会变为可用状态。点击该按钮：
1. 在新标签页打开 MyBinder
2. URL 格式：`https://mybinder.org/v2/gh/{user}/{repo}/master?urlpath=lab/tree/{path}`
3. Binder 会构建仓库环境并启动 JupyterLab
4. 在 Binder 环境中可以运行代码（与你的本地环境无关）

## 步骤 6：设置默认仓库

如果你经常访问某个仓库，可以设置为启动默认打开：

1. 打开 Settings → Advanced Settings Editor
2. 选择 "GitHub" 插件
3. 在 User Preferences 中输入：

```json
{
  "defaultRepo": "jupyterlab/jupyterlab-github"
}
```

4. 保存设置，刷新 JupyterLab 页面
5. 下次打开时 GitHub 浏览器会自动导航到该仓库

## 常见问题

**Q: 看到 "You have been rate limited by GitHub!" 错误面板怎么办？**
A: 你被 GitHub API 限流了。等待约1小时自动恢复，或配置服务端 Access Token 获得5000次/小时的限制。

**Q: 打开文件时报错 "Cannot open xxx because it is a submodule"？**
A: Git 子模块不支持浏览，这是预期行为。

**Q: 为什么修改文件后保存不了？**
A: 这是只读浏览器，无法保存回 GitHub。可以通过 File → Save As 保存到本地文件系统。

**Q: Binder 按钮是灰色的（不可点击）？**
A: 需要在仓库根目录有 Binder 配置文件才会启用。或者你可能不在仓库根目录（源码中存在已知限制：直接导航到子目录不会触发 Binder 检测）。

---

**相关概念**：
- [GitHubDrive 虚拟文件系统](../concepts/03-github-drive.md)
- [浏览器 UI 组件与交互](../concepts/04-browser-ui.md)
- [认证配置示例](02-setup-authentication.md)
