---
type: OKF
title: JupyterLite JavaScript Kernel 教程
description: JupyterLite JavaScript 内核完全指南 — 在浏览器中运行 JavaScript 代码，支持 Magic Imports、内置 Widgets、双运行时模式
tags: [javascript, jupyterlite, kernel, browser, iframe, worker, widgets, comlink]
version: 0.1.0
source: https://github.com/jupyterlite/javascript-kernel
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
---

# JupyterLite JavaScript Kernel 教程

JavaScript Kernel 是 [JupyterLite](https://jupyterlite.rtfd.io/) 的官方 JavaScript 内核，允许在浏览器中直接执行 JavaScript 代码，无需后端 Python 服务器。它通过 IFrame 或 Web Worker 隔离执行环境，使用 Comlink 实现主线程与执行环境间的 RPC 通信，内置完整的 ipywidgets 兼容控件集和 Magic Imports 包管理。

## 📚 快速导航

### [概念文档](concepts/index.md)
- [00-简介](concepts/00-introduction.md) — JavaScript Kernel 是什么、核心特性、双运行时模式、技术栈
- [01-快速开始](concepts/01-getting-started.md) — 安装、第一个 Notebook、模式选择、Console 输出
- [02-内核架构](concepts/02-kernel-architecture.md) — JavaScriptKernel 类、IRuntimeBackend、启动扩展、生命周期
- [03-执行模型](concepts/03-execution-model.md) — AST 转换、Magic Imports、异步函数包装、MIME 输出、错误处理
- [04-运行时后端](concepts/04-runtime-backends.md) — IFrame/Worker 双后端、Comlink RPC、初始化流程、模式对比
- [05-Widget 系统](concepts/05-widget-system.md) — 内置 ipywidgets 兼容层、55+ 控件、事件系统、双向绑定
- [06-Comm 协议](concepts/06-comm-protocol.md) — 自定义消息通道、CommManager、Widget 通信原理
- [07-富媒体输出系统](concepts/07-display-system.md) — display() 函数、MIME bundle、display_id 动态更新
- [08-启动扩展机制](concepts/08-startup-extensions.md) — IJavaScriptKernelStartupRegistry、前端插件集成
- [09-常见问题与限制](concepts/09-faq-limitations.md) — FAQ、浏览器限制、调试技巧、最佳实践

### [实践示例](examples/index.md)
- [01-第一个 Notebook](examples/01-first-notebook.md) — 创建 Notebook、运行代码、变量和 await
- [02-Magic Imports](examples/02-magic-imports.md) — 导入 npm 包、CDN 加载、版本指定、可视化库
- [03-使用 Widgets](examples/03-using-widgets.md) — 滑块、按钮、进度条、容器、双向绑定、综合示例
- [04-富媒体输出](examples/04-rich-output.md) — HTML/SVG/Canvas/Markdown/LaTeX/display_id 动态更新
- [05-IFrame DOM 操作](examples/05-iframe-dom.md) — DOM 创建、Canvas 绘图、window.parent 访问主页面
- [06-异步编程与数据获取](examples/06-async-data.md) — fetch API、Promise、WebSocket、实时数据

### [信源参考](references/index.md)
- [全局 API 参考](references/api-reference.md) — display()、console、Jupyter 对象、Widget API
- [源码文件索引](references/source-files.md) — 核心源码文件职责和依赖关系
- [事实清单](facts.md) — 从源码采集的 149 条零推测事实
- [架构洞察](insights.md) — 5 个核心架构洞察与知识地图

## 🚀 快速开始

```bash
pip install jupyterlite-javascript-kernel
```

打开 JupyterLite，新建 Notebook，选择 **JavaScript (IFrame)** 内核，开始编写：

```javascript
// Hello World
console.log("Hello, JavaScript Kernel!");

// Magic Import — 自动从 CDN 加载
import confetti from 'canvas-confetti';
confetti();

// 内置 Widget
const { IntSlider } = Jupyter.widgets;
display(new IntSlider({ value: 50, min: 0, max: 100 }));
```

## 🎯 核心特性

| 特性 | 说明 |
|------|------|
| 🌐 纯浏览器执行 | 无需后端，代码完全在浏览器中运行 |
| 🔀 双运行时模式 | IFrame（DOM 访问）和 Web Worker（强隔离） |
| 📦 Magic Imports | 直接 `import` npm 包，自动通过 jsdelivr CDN 加载 |
| 🎨 富媒体输出 | HTML、SVG、PNG、Markdown、LaTeX、JSON、Canvas |
| 🧩 内置 Widgets | 55+ ipywidgets 兼容控件，纯 JS 实现 |
| 🔌 Comm 协议 | 自定义双向通信通道，支持前端扩展集成 |
| ⚡ 顶层 await | 单元格中直接使用 `await` |
| 🧠 智能补全 | 基于运行时对象自省的代码补全 |
| 🪝 启动扩展 | 前端插件可预加载模块和注册 comm target |

## 🏗️ 架构概览

```
┌─────────────────────────────────────────────────────┐
│                    浏览器主线程                       │
│  ┌──────────────┐     Jupyter      ┌──────────────┐ │
│  │  JupyterLite  │◄───Protocol────►│JavaScriptKernel│ │
│  │   前端 UI    │                  │  (BaseKernel) │ │
│  └──────────────┘                  └──────┬───────┘ │
│                                          │          │
│                          ┌───────────────┼────────┐ │
│                          │  AbstractRuntimeBackend │ │
│                          │     (Comlink RPC)       │ │
│                          └───┬───────────────┬────┘ │
│                              │               │       │
│                     ┌────────┴──┐     ┌─────┴─────┐ │
│                     │  IFrame   │     │Web Worker │ │
│                     │ Backend   │     │  Backend  │ │
│                     └─────┬─────┘     └─────┬─────┘ │
│                           │    Comlink        │      │
│  ┌────────────────────────┼──────┐    ┌──────┼─────────────────┐
│  │ 隐藏 <iframe>          │      │    │Worker│ postMessage      │
│  │  ┌─────────────────────┴───┐  │    │ ┌────┴──────────────┐  │
│  │  │JavaScriptRuntimeEvaluator│  │    │ │JS RuntimeEvaluator│  │
│  │  │  ├─JavaScriptExecutor   │  │    │ │  ├─JSExecutor      │  │
│  │  │  ├─CommManager          │  │    │ │  ├─CommManager     │  │
│  │  │  ├─Widget Classes       │  │    │ │  ├─Widget Classes  │  │
│  │  │  ├─DisplayHelper        │  │    │ │  └─Console重写     │  │
│  │  │  └─Console 重写         │  │    │ └───────────────────┘  │
│  │  └─────────────────────────┘  │    └────────────────────────┘
│  └───────────────────────────────┘                              │
└─────────────────────────────────────────────────────────────────┘
```

## 📖 阅读路径

### 初学者路径
1. [00-简介](concepts/00-introduction.md) → [01-快速开始](concepts/01-getting-started.md)
2. [01-第一个 Notebook](examples/01-first-notebook.md)
3. [02-Magic Imports](examples/02-magic-imports.md)

### 交互式可视化路径
1. [03-执行模型](concepts/03-execution-model.md) → [04-运行时后端](concepts/04-runtime-backends.md)
2. [03-使用 Widgets](examples/03-using-widgets.md)
3. [05-IFrame DOM 操作](examples/05-iframe-dom.md) → [04-富媒体输出](examples/04-rich-output.md)

### 扩展开发者路径
1. [02-内核架构](concepts/02-kernel-architecture.md) → [06-Comm 协议](concepts/06-comm-protocol.md)
2. [08-启动扩展机制](concepts/08-startup-extensions.md)
3. [源码文件索引](references/source-files.md)

## 🔗 外部资源

- [GitHub 仓库](https://github.com/jupyterlite/javascript-kernel)
- [JupyterLite 文档](https://jupyterlite.readthedocs.io/)
- [Jupyter Widgets 文档](https://ipywidgets.readthedocs.io/)
- [Comlink 文档](https://github.com/GoogleChromeLabs/comlink)

```{toctree}
:hidden:

concepts/index
examples/index
references/index
facts
insights
log
```
