---
type: Concept
title: JupyterLite Demo 简介
description: JupyterLite Demo 是什么、核心特性、能做什么，以及它在 JupyterLite 生态中的定位
tags: [introduction, overview, jupyterlite-demo, jupyterlite, getting-started]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T18:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: meta
    resource: /references/repo-readme.md
    title: JupyterLite Demo 仓库元信源
  - id: readme
    resource: https://github.com/jupyterlite/demo/blob/main/README.md
    title: README.md
---

## JupyterLite Demo 是什么

JupyterLite Demo 是 [JupyterLite](https://jupyterlite.readthedocs.io/) 的官方演示站点部署模板。它展示了如何将 JupyterLite 部署为一个完全静态的网站——不需要服务器、不需要 Docker、不需要云服务，只需要一个能托管静态文件的 Web 服务器（如 GitHub Pages），就能运行完整的 Jupyter 环境。

在线演示地址：[jupyterlite.github.io/demo](https://jupyterlite.github.io/demo)

JupyterLite Demo 仓库本身**不包含任何源代码**——它是一个最小化的「部署模板」，由三个核心部分组成：

1. **依赖声明**（requirements.txt）：告诉构建工具需要预装哪些内核、扩展和主题
2. **内容目录**（content/）：随站点分发的笔记本（.ipynb）和数据文件
3. **部署配置**（GitHub Actions + jupyter-lite.json）：自动化构建和站点配置

## 核心特性

| 特性 | 说明 |
|------|------|
| 🌐 **零后端** | 所有计算在浏览器中通过 WebAssembly 运行，无需服务器端 Python |
| 📦 **静态部署** | 构建产物是纯 HTML/JS/WASM 文件，可部署到 GitHub Pages、Vercel、Netlify、任意 CDN |
| 🐍 **三大内核** | Pyodide（Python）、JavaScript、p5.js 三种内核开箱即用 |
| 📊 **科学计算栈** | 通过 Pyodide 支持 numpy、pandas、matplotlib、altair、plotly 等 |
| 🎨 **多主题** | 内置 JupyterLab 暗色主题和 Miami Nights 主题 |
| 🌍 **多语言** | 支持英语、法语、中文界面 |
| 🗺️ **富交互** | ipywidgets、bqplot、ipyleaflet、ipycanvas 等交互式控件库 |
| 📝 **笔记本兼容** | 标准 .ipynb 格式，与传统 Jupyter 笔记本互通 |

## 支持的浏览器

JupyterLite 针对现代浏览器测试：

- Firefox 90+
- Chromium 89+（Chrome、Edge、Brave 等）

Safari 也可以使用，但可能存在兼容性问题。

## 与传统 Jupyter 部署的区别

| 方面 | 传统 Jupyter（Jupyter Notebook/Lab） | JupyterLite Demo |
|------|-------------------------------------|------------------|
| 运行环境 | 服务器端 Python 进程 | 浏览器 WebAssembly (WASM) |
| 部署方式 | 需要服务器、Docker、Kubernetes 等 | 纯静态文件，任意 CDN |
| Python 包 | pip/conda 安装到服务器环境 | `%pip install` 安装到浏览器，仅纯 Python wheel 可用 |
| 文件系统 | 服务器本地磁盘 | 浏览器 IndexedDB（持久化）+ Emscripten MEMFS（临时） |
| 内核 | IPython 内核（CPython 进程） | Pyodide（CPython WASM）、JS Kernel、p5 Kernel |
| 网络请求 | 服务器端网络 | 通过浏览器 Fetch API（受 CORS 限制） |
| 启动速度 | 需启动服务器进程 | 首次加载需下载 WASM（约15MB），后续离线可用 |
| 多用户 | 需要 JupyterHub 管理 | 每个浏览器标签页是独立实例 |

## 在 JupyterLite 生态中的位置

JupyterLite Demo 是 JupyterLite 生态中「使用端」的模板项目：

```
┌─────────────────────────────────────────────────────┐
│  JupyterLite 核心框架                                │
│  jupyterlite-core + jupyterlab + notebook           │
├─────────────────────────────────────────────────────┤
│  内核                                                │
│  pyodide-kernel | javascript-kernel | p5-kernel     │
│  xeus-python-kernel（另一个模板）                     │
├─────────────────────────────────────────────────────┤
│  部署模板                                            │
│  ★ jupyterlite/demo（本教程）— 官方 Pyodide 模板    │
│  jupyterlite/xeus-python-demo — Xeus 内核模板        │
└─────────────────────────────────────────────────────┘
```

如果需要基于 Xeus（C++ 原生 WASM 内核，支持更多编译型扩展）部署，应使用 xeus-python-demo 模板。

## 相关概念

- [Demo 仓库结构与三件套模式](/concepts/01-demo-overview.md)
- [三大内核生态对比](/concepts/03-kernel-ecosystem.md)
- [GitHub Pages 部署实战](/concepts/06-deployment-github-pages.md)
