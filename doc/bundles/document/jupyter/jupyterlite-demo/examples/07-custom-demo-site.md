---
type: Example
title: 构建自定义 JupyterLite 站点
description: 从 Demo 模板出发，逐步自定义一个 JupyterLite 站点，包括添加自己的笔记本、选择扩展、配置主题、设置语言包
tags: [customization, tutorial, build, theme, extensions, language-pack, branding]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T18:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: requirements
    resource: /references/requirements-source.md
    title: 依赖配置信源
  - id: config
    resource: /references/config-source.md
    title: 站点配置信源
---

## 概述

本文档演示如何基于 jupyterlite/demo 模板，构建一个自定义的 JupyterLite 站点——包含自己的笔记本、选择需要的扩展、配置主题和语言。

## 步骤 1：创建项目

使用 GitHub Template 或手动创建：

```bash
# 方式一：从 GitHub 模板创建（推荐）
# 访问 https://github.com/jupyterlite/demo → Use this template

# 方式二：手动创建
mkdir my-jupyterlite-site
cd my-jupyterlite-site
git init
```

## 步骤 2：定制 requirements.txt

根据需要选择依赖。以下是一个教学站点的配置示例：

```txt
# ===== 核心（必选）=====
jupyterlite-core==0.8.0
jupyterlab~=4.6.0
notebook~=7.6.0

# ===== 内核（按需选择）=====
jupyterlite-pyodide-kernel==0.8.0     # Python 内核（推荐保留）
# jupyterlite-javascript-kernel==0.3.0  # JS 内核（按需）
# jupyterlite-p5-kernel==0.3.0          # p5 内核（创意编程需要）

# ===== 中文界面（中文用户推荐）=====
jupyterlab-language-pack-zh-CN

# ===== 暗色主题 =====
jupyterlab-night

# ===== 数据科学扩展 =====
ipywidgets>=8.1.3,<9
ipympl>=0.8.2        # matplotlib 交互式后端
plotly>=6,<7         # 交互式图表
bqplot               # Jupyter 原生图表

# ===== 文件渲染器 =====
jupyterlab-geojson>=3.4.0,<4
jupyterlab-fasta>=3.3.0,<4
```

如果站点不需要 p5 内核或 JS 内核，注释掉可以减小构建产物体积。

## 步骤 3：准备内容

创建 content/ 目录，放入自己的笔记本和数据：

```
content/
├── welcome.ipynb          # 欢迎页面
├── tutorials/             # 教程笔记本
│   ├── 01-intro.ipynb
│   ├── 02-data-analysis.ipynb
│   └── 03-visualization.ipynb
├── exercises/             # 练习
│   └── exercise-01.ipynb
└── data/                  # 数据文件
    └── sample-data.csv
```

### 创建欢迎笔记本

在 content/ 根目录创建 welcome.ipynb，添加：

```python
# Welcome to My JupyterLite Site!
print("🚀 欢迎来到我的 JupyterLite 站点！")
print("所有代码在浏览器中运行，无需安装任何软件。")
```

```python
import sys
print(f"Python 版本: {sys.version.split()[0]}")
import pyodide_kernel
print(f"Pyodide 内核版本: {pyodide_kernel.__version__}")
```

### 笔记本中的 %pip 安装

对于没有预装的包，在笔记本开头使用 %pip install：

```python
# 在需要 pandas 的笔记本中
%pip install -q pandas
import pandas as pd
```

## 步骤 4：配置站点

创建配置文件。如果只需要简单配置，创建 `repl/jupyter-lite.json`：

```bash
mkdir -p repl
```

编辑 `repl/jupyter-lite.json`：

```json
{
  "jupyter-lite-schema-version": 0,
  "jupyter-config-data": {
    "disabledExtensions": [
      "@jupyterlab/drawio-extension"
    ],
    "settingsOverrides": {
      "@jupyterlab/apputils-extension:themes": {
        "theme": "JupyterLab Dark"
      }
    }
  }
}
```

上述配置：
- 禁用 drawio 扩展
- 默认使用暗色主题

### 高级配置选项

设置默认内核为 Python：

```json
{
  "jupyter-lite-schema-version": 0,
  "jupyter-config-data": {
    "defaultKernel": "python"
  }
}
```

## 步骤 5：配置 CI/CD

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
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: python -m pip install -r requirements.txt
      - name: Build JupyterLite
        run: |
          jupyter lite build --contents content --output-dir dist
      - uses: actions/upload-pages-artifact@v3
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
      - id: deployment
        uses: actions/deploy-pages@v4
```

创建 `.nojekyll` 空文件：

```bash
touch .nojekyll
```

## 步骤 6：本地测试

推送到 GitHub 之前，在本地构建和预览：

```bash
# 安装依赖
pip install -r requirements.txt

# 构建
jupyter lite build --contents content --output-dir dist

# 预览
jupyter lite serve --output-dir dist
# 浏览器访问 http://localhost:8000
```

验证：
- 笔记本在文件浏览器中可见
- 内核选择器中只有需要的内核
- 主题正确加载
- %pip install 可以正常安装包

## 步骤 7：部署到 GitHub Pages

```bash
git add .
git commit -m "Custom JupyterLite site"
git branch -M main
git remote add origin https://github.com/<username>/<repo>.git
git push -u origin main
```

在 GitHub 仓库 Settings → Pages 中，将 Source 设置为 **GitHub Actions**。等待构建完成后访问站点。

## 常见定制场景

### 场景 A：纯教学站点（最小体积）

只保留 Pyodide 内核，禁用不需要的 UI：

```txt
jupyterlite-core==0.8.0
jupyterlab~=4.6.0
notebook~=7.6.0
jupyterlite-pyodide-kernel==0.8.0
jupyterlab-language-pack-zh-CN
```

### 场景 B：数据科学工作站

预装所有数据科学包：

```txt
# 核心
jupyterlite-core==0.8.0
jupyterlab~=4.6.0
notebook~=7.6.0
jupyterlite-pyodide-kernel==0.8.0

# 数据科学
ipywidgets>=8.1.3,<9
ipympl>=0.8.2
ipycanvas>=0.9.1
ipyleaflet
plotly>=6,<7
bqplot

# 扩展
jupyterlab-language-pack-zh-CN
jupyterlab-night
jupyterlab-geojson>=3.4.0,<4
```

### 场景 C：创意编程站点

包含 p5 内核和 Canvas：

```txt
# 核心
jupyterlite-core==0.8.0
jupyterlab~=4.6.0
notebook~=7.6.0
jupyterlite-pyodide-kernel==0.8.0
jupyterlite-p5-kernel==0.3.0

# 创意编程
ipycanvas>=0.9.1
ipywidgets>=8.1.3,<9

# 主题
jupyterlab_miami_nights
```

## 减小构建体积的技巧

1. **不安装不需要的内核**：每个内核增加数 MB 的 WASM 文件
2. **少预装 Python 包**：纯 Python 包可以通过 %pip 按需安装
3. **禁用不需要的扩展**：减少前端 JS 体积
4. **不安装语言包**：如果只需要英文界面，不安装 language-pack
5. **只构建需要的应用**：使用 `--apps lab` 只构建 JupyterLab

```bash
jupyter lite build --contents content --output-dir dist --apps lab
```

## 相关概念

- [自定义 Demo 站点指南](../concepts/07-customization-guide.md)
- [GitHub Pages 部署流水线](../concepts/06-deployment-github-pages.md)
- [站点配置详解](../concepts/02-site-configuration.md)
- [从零部署到 GitHub Pages](01-first-deployment.md)
