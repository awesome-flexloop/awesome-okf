---
type: Concept
title: p5-kernel 简介
description: JupyterLite p5.js 内核是什么、核心特性、设计理念、安装方法，以及它在 JupyterLite 内核生态中的位置
tags: [introduction, overview, p5-kernel, jupyterlite, p5js, creative-coding]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T17:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: meta
    resource: /references/metasource.md
    title: p5-kernel 项目元信源
  - id: readme
    resource: https://github.com/jupyterlite/p5-kernel/blob/main/README.md
    title: README.md
---

## p5-kernel 是什么

p5-kernel 是 [JupyterLite](https://jupyterlite.readthedocs.io/) 的一个 **p5.js 内核**，让用户可以在 Jupyter Notebook 中直接编写和运行 [p5.js](https://p5js.org/) 创意编程草图（sketch）。它构建在 JupyterLite 的 JavaScript 内核之上，通过 iframe 沙箱渲染 p5.js 画布，支持增量式 cell 编程和实时预览。

p5.js 是 Processing 语言的 JavaScript 实现，专注于创意编程、可视化和交互式艺术。p5-kernel 让创意编程工作流获得了 Jupyter Notebook 的 cell 执行、文档混合、变量持久化等能力。

## 核心特性

| 特性 | 说明 |
|------|------|
| 🎨 **p5.js 原生支持** | 直接编写 setup()/draw() 函数，使用全部 p5.js API |
| 📝 **增量式编程** | 可在多个 cell 中分散定义变量和函数，内核自动累积代码 |
| 🖼️ **iframe 沙箱渲染** | 通过 `%show` magic 在独立 iframe 中渲染 sketch，与 Notebook 环境隔离 |
| 📦 **ES Module 导入** | 支持 `import confetti from 'canvas-confetti'` 直接加载 npm 包 |
| 🖼️ **Graphics 自动渲染** | p5.Graphics 离屏画布自动转为 PNG 图像输出 |
| 📖 **内置 API 文档** | Shift+Tab 代码内省显示 p5.js 函数签名和描述 |
| 🔄 **实时更新** | 修改变量后重新执行 `%show` 即可看到更新后的动画 |
| 🌐 **零后端** | 完全在浏览器中运行，无需服务器端 Python 进程 |

## 安装

```bash
pip install jupyterlite-p5-kernel
jupyter lite build
```

安装后构建 JupyterLite 站点，即可在内核选择器中看到 **p5.js** 内核。

## 快速体验

安装后在 Notebook 中选择 p5.js 内核，编写以下代码：

```javascript
function setup() {
  createCanvas(400, 400);
}

function draw() {
  background(220);
  ellipse(mouseX, mouseY, 50, 50);
}
```

然后执行 `%show` 即可看到一个跟随鼠标移动的圆形。

## 在 JupyterLite 内核生态中的位置

| 内核 | 语言 | 渲染方式 | 特点 |
|------|------|---------|------|
| Pyodide Kernel | Python (WASM) | Worker 内嵌 | CPython 科学计算栈 |
| Xeus Kernel | C++/多语言 | Worker 内嵌 | 原生 WASM 内核框架 |
| JavaScript Kernel | JavaScript | Web Worker | 基础 JS 执行，无图形输出 |
| **p5 Kernel** | JavaScript (p5js) | **iframe 沙箱** | **p5.js 创意编程，画布渲染** |
| Echo Kernel | Text | Worker | 最小示例内核，仅回显输入 |

p5-kernel 是目前唯一使用 **iframe 运行时模式** 的 JupyterLite 内核——它不直接在 Worker 中渲染输出，而是将累积的代码注入独立 iframe 中执行，确保 p5.js 的 DOM 操作和全局模式与 JupyterLab UI 完全隔离。

## 与传统 p5.js 开发的区别

| 方面 | 传统 p5.js（编辑器/HTML） | Jupyter p5-kernel |
|------|------------------------|-------------------|
| 代码组织 | 单个 JS 文件或 HTML | 多个 Notebook cells |
| 执行模式 | 刷新页面重新运行 | Cell 增量执行，变量持久化 |
| 预览方式 | 页面自动运行 setup/draw | `%show` magic 触发渲染 |
| 文档 | 外部文档 | Markdown cells 混排 |
| 外部库 | script 标签引入 | ES `import` 语法 |
| 输出 | 单一画布 | 可输出文本、图像、画布 |

## 相关概念

- [架构概览](01-architecture-overview.md)
- [P5Kernel 实现详解](02-kernel-implementation.md)
- [P5Executor 与渲染机制](03-executor-and-rendering.md)
- [%show 魔法命令](04-magic-commands.md)
