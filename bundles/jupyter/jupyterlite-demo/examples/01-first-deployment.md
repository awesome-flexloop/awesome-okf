---
type: Example
title: 从零部署 JupyterLite 到 GitHub Pages
description: 从空仓库开始，基于 jupyterlite/demo 模板完成第一个 JupyterLite 站点的完整部署流程
tags: [deploy, github-pages, quickstart, first-site, ci-cd]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T18:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: workflow
    resource: /references/deploy-workflow-source.md
    title: 部署流水线信源
  - id: meta
    resource: /references/repo-readme.md
    title: 仓库元信源
---

## 概述

本文档演示如何从零开始，基于 JupyterLite Demo 模板，将一个 JupyterLite 站点部署到 GitHub Pages。整个过程约 10 分钟。

## 前置条件

- GitHub 账号
- 基本的 Git 操作能力
- 本地已安装 Python 3.10+ 和 pip（本地预览需要）

## 步骤 1：创建仓库

方式一：使用 GitHub Template（推荐）

1. 访问 https://github.com/jupyterlite/demo
2. 点击 **Use this template** → **Create a new repository**
3. 输入仓库名（如 `my-jupyterlite-site`），选择 Public
4. 点击 **Create repository from template**

方式二：手动创建

```bash
# 创建仓库目录
mkdir my-jupyterlite-site
cd my-jupyterlite-site
git init
```

然后将 demo 仓库的核心文件复制进去：
- `requirements.txt`
- `.github/workflows/deploy.yml`
- `.gitignore`
- `.nojekyll`
- `repl/jupyter-lite.json`（可选）
- `content/` 目录（可以放入自己的笔记本）

## 步骤 2：配置 requirements.txt

创建 `requirements.txt`，最小配置：

```txt
# 核心模块
jupyterlite-core==0.8.0
jupyterlab~=4.6.0
notebook~=7.6.0

# Python 内核
jupyterlite-pyodide-kernel==0.8.0
```

如果需要其他内核和扩展，参考 [依赖配置信源](/references/requirements-source.md) 添加。

## 步骤 3：添加内容

创建 `content/` 目录，放入笔记本文件：

```bash
mkdir -p content
# 将你的 .ipynb 文件复制到 content/ 目录
cp /path/to/your/notebook.ipynb content/
```

至少放一个笔记本，如创建一个简单的 `welcome.ipynb`：

```python
print("Hello, JupyterLite!")
import sys
print(f"Python version: {sys.version}")
```

## 步骤 4：配置 GitHub Actions

创建 `.github/workflows/deploy.yml`：

```yaml
name: Build and Deploy

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - '*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install the dependencies
        run: |
          python -m pip install -r requirements.txt
      - name: Build the JupyterLite site
        run: |
          jupyter lite build --contents content --output-dir dist
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: ./dist

  deploy:
    needs: build
    if: github.ref == 'refs/heads/main'
    permissions:
      pages: write
      id-token: write
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

如果想将 README 包含在站点中，在构建步骤中添加 `cp README.md content`。

## 步骤 5：配置 .nojekyll

在仓库根目录创建空文件 `.nojekyll`，告诉 GitHub Pages 不要用 Jekyll 处理静态文件：

```bash
touch .nojekyll
```

## 步骤 6：推送代码到 GitHub

```bash
git add .
git commit -m "Initial JupyterLite site"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

## 步骤 7：启用 GitHub Pages

1. 进入仓库的 **Settings** 页面
2. 点击左侧 **Pages**
3. 在 **Source** 下拉菜单中选择 **GitHub Actions**
4. 保存设置

## 步骤 8：等待构建完成

1. 进入仓库的 **Actions** 标签页
2. 等待 Build and Deploy 工作流完成（通常 3-5 分钟）
3. 绿色勾号表示部署成功
4. 点击工作流运行记录中的 deploy 步骤，可看到站点 URL

## 步骤 9：访问站点

站点 URL 格式为：`https://<your-username>.github.io/<your-repo>/`

打开后会看到 JupyterLab 界面，左侧文件浏览器中可以看到 content/ 目录下的笔记本。

## 本地预览（可选）

推送到 GitHub 之前，可以在本地构建预览：

```bash
# 安装依赖
pip install -r requirements.txt

# 构建
jupyter lite build --contents content --output-dir dist

# 启动预览服务器
jupyter lite serve --output-dir dist
# 访问 http://localhost:8000
```

## 常见问题

### Q: 构建失败，提示找不到 jupyter 命令？
确保 requirements.txt 已正确安装：`pip install -r requirements.txt`。如果是 CI 中失败，检查 deploy.yml 中的 pip install 步骤是否执行成功。

### Q: 部署后访问 404？
检查 GitHub Pages 设置是否正确选择了 "GitHub Actions" 作为 Source。首次部署可能需要等待 1-2 分钟。

### Q: 笔记本中的 %pip install 很慢？
这是正常现象——包从 PyPI 下载到浏览器需要时间。对于常用包，考虑添加到 requirements.txt 中预装。

### Q: 如何更新站点？
直接修改 content/ 中的笔记本或 requirements.txt，push 到 main 分支即可自动重新构建和部署。

## 相关概念

- [GitHub Pages 部署流水线](/concepts/06-deployment-github-pages.md)
- [Demo 仓库结构与三件套模式](/concepts/01-demo-overview.md)
- [站点配置详解](/concepts/02-site-configuration.md)
- [自定义 Demo 站点](/examples/07-custom-demo-site.md)
