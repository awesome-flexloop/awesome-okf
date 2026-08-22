---
type: Example
title: 快速开始与本地部署
description: 使用pip安装JupyterLite CLI、构建第一个静态站点、本地预览
tags: [quickstart, deploy, build, cli, getting-started]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T15:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: build-source
    resource: /references/build-source.md
    title: 构建系统信源
  - id: meta-source
    resource: /references/metasource.md
    title: 项目元信源
---

## 安装 JupyterLite

使用 pip 安装 JupyterLite CLI 工具：

```bash
pip install jupyterlite-core
```

对于包含 Pyodide 内核的完整安装：

```bash
pip install jupyterlite
```

## 构建第一个站点

在包含 Notebooks 的目录中运行：

```bash
# 创建内容目录
mkdir -p my-jupyterlite/content
# 将Notebook放入content目录
cp my-notebook.ipynb my-jupyterlite/content/
# 构建站点
cd my-jupyterlite
jupyter lite build
```

构建产物在 `_output/` 目录中，是完整的静态站点。

## 本地预览

```bash
jupyter lite serve
```

默认在 `http://localhost:8000` 启动本地服务器。也可以用任意静态文件服务器：

```bash
# 使用Python内置服务器
cd _output
python -m http.server 8000

# 使用node serve
npx serve _output
```

## 部署到静态托管

构建产物 `_output/` 可部署到任意静态文件托管服务：

### GitHub Pages

```bash
# 将_output目录推送到gh-pages分支
# 或使用GitHub Actions自动构建
```

### Vercel / Netlify

将构建命令设为 `jupyter lite build`，输出目录设为 `_output`。

## 构建过程说明

`jupyter lite build` 命令执行以下步骤（基于Doit任务）：

1. **pre_status**：环境检查（Python版本、依赖可用性）
2. **init**：初始化输出目录
3. **build**：核心构建
   - 复制前端应用文件（Lab/REPL/Notebook等）
   - 复制Pyodide内核资源（WASM、Python包）
   - 索引content目录中的Notebook和文件
   - 生成 `__all__.json` 内容索引
   - 生成 `jupyter-lite.json` 配置
4. **post_build**：后处理（Service Worker生成等）

## 常用构建选项

```bash
# 指定内容目录
jupyter lite build --content ./notebooks

# 指定输出目录
jupyter lite build --output-dir ./dist

# 指定应用（只构建lab和repl）
jupyter lite build --apps lab --apps repl

# 禁用特定addon
jupyter lite build --disable-addons serve

# 查看可用任务
jupyter lite list
```

## 添加额外Python包

Pyodide内核支持通过 `micropip` 在运行时安装包，也可以预安装到构建产物中：

```bash
# piplite是jupyterlite的包管理工具
pip install piplite-wasm
jupyter lite build --piplite-wheels ./wheels/
```

或者在Notebook中使用：

```python
import micropip
await micropip.install('numpy')
import numpy as np
```

## 相关概念

- [Python构建系统](/concepts/06-build-system.md)
- [整体架构](/concepts/01-architecture-overview.md)
