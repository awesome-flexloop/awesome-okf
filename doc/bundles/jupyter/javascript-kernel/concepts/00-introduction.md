---
type: Concept
title: JavaScript Kernel 简介
description: JupyterLite JavaScript 内核概述，核心特性、双运行时模式和技术栈
tags: [javascript, jupyterlite, kernel, browser, overview]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: jk-readme
    title: README.md
  - id: jk-pkg
    title: package.json
---

# JavaScript Kernel 简介

JavaScript Kernel 是 [JupyterLite](https://jupyterlite.rtfd.io/) 的官方 JavaScript 内核，允许在浏览器中直接执行 JavaScript 代码，无需后端 Python 服务器。它是 JupyterLite 生态的核心组件之一。

## 什么是 JavaScript Kernel？

JavaScript Kernel 是一个完全运行在浏览器中的 Jupyter 内核实现。与传统的 IPython 内核（需要 Python 后端）不同，它将用户的 JavaScript 代码在浏览器的隔离环境中执行，并通过 Jupyter 标准协议与前端通信。

```
┌──────────────────────────────────────────────────┐
│                  浏览器页面                       │
│  ┌────────────┐   Jupyter Protocol    ┌────────┐ │
│  │ JupyterLite │◄────────────────────►│  JS    │ │
│  │  前端 UI    │     (WebSocket       │ Kernel │ │
│  │            │      over postMessage)│        │ │
│  └────────────┘                      └───┬────┘ │
│                                          │      │
│                          ┌───────────────┼────┐ │
│                          │  隔离执行环境  │    │ │
│                          │  ┌─────────┐  │    │ │
│                          │  │ IFrame  │  │    │ │
│                          │  │ 或 Worker│  │    │ │
│                          │  └─────────┘  │    │ │
│                          └───────────────┴────┘ │
└──────────────────────────────────────────────────┘
```

## 两种运行时模式

内核注册了两个 kernelspec，对应两种代码执行模式：

| 模式 | Kernelspec 名称 | 执行环境 | 适用场景 |
|------|----------------|---------|---------|
| **IFrame** | `JavaScript (IFrame)` | 隐藏的 `<iframe>` 元素 | 需要 DOM API（`document`、`window`、canvas） |
| **Web Worker** | `JavaScript (Web Worker)` | 专用 Web Worker | 需要强隔离、不阻塞主线程 |

选择方法：在 Notebook 工具栏的内核选择器中切换。

### IFrame 模式特点

- 代码在与主页面同源的隐藏 iframe 中执行
- 可以通过 `window.parent` 访问主页面 DOM
- 模块导入的副作用默认留在 iframe 内
- 适合需要 canvas 渲染、DOM 操作的可视化场景

### Web Worker 模式特点

- 代码在独立线程的 Web Worker 中执行
- **无法访问 DOM API**（无 `document`、无 `window`）
- 不阻塞主线程 UI 渲染
- 适合计算密集型任务和需要强隔离的场景

> ⚠️ **Worker 模式限制**：`document`、直接元素访问、以及其他仅主线程可用的浏览器 API 在 Worker 模式下不可用。

## 核心特性

| 特性 | 说明 |
|------|------|
| 🌐 纯浏览器执行 | 无需后端服务器，代码完全在浏览器中运行 |
| 📦 Magic Imports | 直接使用 ES `import` 语法导入 npm 包，自动通过 CDN 加载 |
| 🎨 富媒体输出 | 支持 HTML、SVG、PNG、JPEG、Markdown、LaTeX、JSON 等 MIME 类型输出 |
| 🧩 内置 Widgets | 完整的 ipywidgets 兼容层，55+ 内置控件 |
| 🔗 Comm 协议 | 支持自定义 comm 通道，可与前端扩展双向通信 |
| 🔌 启动扩展 | 前端插件可在用户代码执行前预加载模块和注册 comm target |
| ⚡ 顶层 await | 支持在单元格中直接使用 `await` |
| 🧠 智能补全 | 基于运行时对象自省的代码补全 |
| 🔍 对象检查 | Shift+Tab 查看对象文档和类型信息 |

## 技术栈

| 依赖 | 用途 |
|------|------|
| [Comlink](https://github.com/GoogleChromeLabs/comlink) | 主线程与 iframe/Worker 之间的 RPC 通信 |
| [meriyah](https://github.com/meriyah/meriyah) | JavaScript AST 解析器（用于代码转换和补全） |
| [astring](https://github.com/davidbonnet/astring) | AST 代码生成器 |
| `@jupyterlite/services` | JupyterLite 内核基类和服务接口 |
| `@lumino/coreutils` | PromiseDelegate、Token 等基础工具 |
| `@jupyterlab/coreutils` | PageConfig 等 JupyterLab 工具 |

## 安装要求

- JupyterLite >= 0.3.0
- 支持 ES2017+ 的现代浏览器

```bash
pip install jupyterlite-javascript-kernel
```

## 相关文档

- [01-快速开始](01-getting-started.md) — 安装和第一个 Notebook
- [02-内核架构](02-kernel-architecture.md) — JavaScriptKernel 类和后端架构
- [03-执行模型](03-execution-model.md) — AST 转换、Magic Imports、MIME 输出
