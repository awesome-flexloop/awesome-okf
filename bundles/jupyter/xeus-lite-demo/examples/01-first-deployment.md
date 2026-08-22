---
type: Example
title: 创建第一个 xeus-lite 部署
description: 从零开始，通过 GitHub 网页操作完成第一个 JupyterLite 站点的创建和部署
tags: [getting-started, deployment, github-pages, tutorial]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:05:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: readme
    resource: /references/readme-source.md
    title: README 使用说明信源
  - id: deploy-wf
    resource: /references/deploy-workflow-source.md
    title: CI/CD 流水线信源
---

## 前置条件

- 一个 GitHub 账号（免费版即可）
- 不需要安装任何本地工具

## 目标

在 10 分钟内创建一个完全运行在浏览器中的 Jupyter Notebook 站点，URL 为 `https://{你的用户名}.github.io/{仓库名}/`。

## 步骤1：使用模板创建仓库

1. 打开浏览器，访问 https://github.com/jupyterlite/xeus-lite-demo
2. 点击页面右上角绿色的 **"Use this template"** 按钮
3. 在下拉菜单中选择 **"Create a new repository"**
4. 在新页面填写：
   - **Owner**：选择你自己的用户名
   - **Repository name**：输入 `my-first-jupyterlite`（或其他你喜欢的名字）
   - **Description**：可选，如 "My first JupyterLite site"
   - **Public/Private**：选择 **Public**（免费账号使用 GitHub Pages 需要 Public）
5. 点击底部绿色的 **"Create repository from template"** 按钮

稍等几秒钟，你就拥有了一个完整的 xeus-lite 仓库。

## 步骤2：启用 GitHub Pages

1. 在你刚创建的仓库页面，点击顶部的 **Settings**（设置）标签
2. 在左侧边栏中找到 **Pages** 选项（在 Code and automation 分类下）
3. 找到 **Source** 部分，将下拉菜单从 "Deploy from a branch" 改为 **"GitHub Actions"**
4. 页面会自动保存设置，不需要点击其他按钮

> ⚠️ 这一步必须做！如果不设置，GitHub Actions 无法部署到 Pages。

## 步骤3：等待首次构建

1. 点击仓库顶部的 **Actions** 标签
2. 你应该会看到一个正在运行的 workflow（"Initial commit" 触发的）
3. 等待构建完成（首次构建通常需要 3-5 分钟）
4. 当看到绿色的 ✅ 标记时，说明部署成功

## 步骤4：访问你的站点

部署成功后，在浏览器中访问：

```
https://{你的用户名}.github.io/my-first-jupyterlite/
```

例如，如果你的用户名是 `johndoe`：
```
https://johndoe.github.io/my-first-jupyterlite/
```

你应该能看到 JupyterLite 的界面，左侧文件浏览器中有 `demo.ipynb` 和 `README.md`。

## 步骤5：测试 Notebook

1. 点击左侧的 `demo.ipynb` 打开示例 Notebook
2. 如果提示选择内核，选择 **XPython**
3. 选中第一个 cell（`import this`），点击运行按钮 ▶ 或按 `Shift+Enter`
4. 你应该看到 Python 之禅的输出
5. 运行第二个 cell，等待几秒钟，你应该看到一个笑脸图形

🎉 **恭喜！你的 JupyterLite 站点已经成功运行！**

## 步骤6（可选）：添加自己的 Notebook

让我们上传一个简单的自定义 Notebook 来测试：

1. 在本地创建一个文件 `hello.ipynb`，内容如下（或使用 Jupyter 创建）：

```json
{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": ["print('Hello from my JupyterLite site!')"]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "import sys\n",
    "print(f'Python version: {sys.version}')"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "XPython",
   "language": "python",
   "name": "xpython"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
```

2. 回到 GitHub 仓库页面
3. 点击进入 `content/` 目录
4. 点击右上角 **Add file** → **Upload files**
5. 拖拽你创建的 `hello.ipynb` 文件到上传区域
6. 滚动到页面底部，点击 **Commit changes**
7. 等待 Actions 重新构建（约1-2分钟，因为有缓存）
8. 刷新你的 JupyterLite 站点，就能在文件浏览器中看到 `hello.ipynb`

## 常见问题

**Q: Actions 页面显示 build 失败怎么办？**
A: 点击失败的 workflow run，查看具体哪个步骤出错。最常见的原因是 GitHub Pages 未启用（步骤2遗漏）。

**Q: 打开站点 URL 显示 404？**
A: 确认构建已完成（Actions 页面绿色 ✅），确认 URL 中的用户名和仓库名拼写正确。

**Q: Notebook 中 import 某个包报错？**
A: 默认只安装了 xeus-python 和 ipycanvas。如果需要其他包（如 numpy、matplotlib），需要修改 environment.yml，参见[下一个示例](02-numpy-matplotlib.md)。

**Q: 站点加载很慢？**
A: 首次加载需要下载 WASM 模块和包（约几十 MB），取决于网速。后续加载会使用浏览器缓存，会快很多。

## 相关概念

- [GitHub 模板三步部署](/concepts/03-github-template-deploy.md) — 部署流程概念详解
- [双环境模型](/concepts/02-dual-environment.md) — 理解两个配置文件
- [Python 科学计算环境](02-numpy-matplotlib.md) — 下一步：添加 numpy 和 matplotlib
