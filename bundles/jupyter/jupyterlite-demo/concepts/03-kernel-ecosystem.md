---
type: Concept
title: 三大内核生态对比
description: JupyterLite Demo 中三种内核（Pyodide、JavaScript、p5.js）的特性、能力边界、适用场景和选择策略
tags: [kernels, pyodide, javascript-kernel, p5-kernel, kernel-comparison, wasm]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T18:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: requirements
    resource: /references/requirements-source.md
    title: 依赖配置信源
  - id: notebook-catalog
    resource: /references/notebook-catalog.md
    title: 笔记本目录信源
---

## 内核概览

JupyterLite Demo 预装三种内核，覆盖了从数据科学到创意编程的主要场景：

| 内核 | 语言 | 版本 | 运行时 | 渲染方式 |
|------|------|------|--------|----------|
| Pyodide Kernel | Python | 0.8.0 | Web Worker (WASM CPython) | Worker 内嵌 + MIME bundle |
| JavaScript Kernel | JavaScript | 0.3.0 | Web Worker (浏览器 JS 引擎) | console 输出 |
| p5 Kernel | JavaScript (p5js) | 0.3.0 | iframe 沙箱 | iframe 画布渲染 |

## Pyodide 内核

Pyodide 内核将 CPython 编译为 WebAssembly，在 Web Worker 中运行。它是 JupyterLite 中功能最强大、生态最丰富的内核。

### 核心能力

- **完整 CPython 3.12 运行时**：支持绝大多数 Python 语法和标准库
- **科学计算栈**：numpy、pandas、scipy、scikit-learn 等已编译为 WASM 的包可直接使用
- **数据可视化**：matplotlib、altair、plotly、bqplot 等主流图表库
- **JS 互操作**：通过 `from js import ...` 直接调用浏览器 API（fetch、document 等）
- **top-level await**：支持在笔记本顶层使用 `await` 语法
- **%pip install**：在笔记本中动态安装纯 Python wheel 包
- **IPython magics**：支持 `%cd`、`%pwd`、`%writefile`、`%%timeit`、`%matplotlib` 等魔法命令
- **富媒体输出**：HTML、Markdown、LaTeX、JSON、GeoJSON、ProgressBar 等 MIME 类型
- **交互式控件**：ipywidgets、ipympl、ipycanvas、ipyleaflet 等控件库

### 限制

- 不支持包含 C 扩展的 pip 包（除非已被 Pyodide 交叉编译为 WASM）
- 网络请求受浏览器 CORS 策略限制
- 文件系统基于 Emscripten FS，与本地文件系统隔离
- 多线程/多进程受限（WASM 线程支持仍在改进中）

### 适用场景

- 数据分析和可视化
- 科学计算和教学
- 交互式文档和教程
- 浏览器端 Python 原型验证

## JavaScript 内核

JavaScript 内核在 Web Worker 中直接运行浏览器原生 JavaScript 代码。

### 核心能力

- **原生 JS 执行**：无需编译，直接运行 ES2020+ JavaScript
- **标准流输出**：`console.log()` 和 `console.error()` 分别映射到 stdout 和 stderr
- **异步操作**：setTimeout、Promise、async/await 等原生支持
- **Markdown 混排**：Markdown 单元格支持 LaTeX 数学公式

### 限制

- 无图形/画布直接渲染（需要通过 display 机制或配合 p5 内核）
- 无法直接访问 DOM（运行在 Worker 中）
- 无包管理系统（不能 npm install）
- 生态远不如 Python 丰富

### 适用场景

- JavaScript 语法教学
- 简单算法演示
- JS API 测试和验证
- 作为其他内核（如 p5）的基础

## p5.js 内核

p5 内核构建在 JavaScript 内核之上，专门用于 [p5.js](https://p5js.org/) 创意编程。它通过 iframe 沙箱渲染 p5.js 画布。

### 核心能力

- **setup/draw 编程模型**：原生支持 p5.js 的 setup() 和 draw() 函数
- **%show 魔法命令**：在 iframe 中渲染动画画布
- **增量式编程**：变量和函数可分散在多个 cell，内核自动累积代码
- **实时参数调整**：在后续 cell 修改变量值，重新 %show 即可看到更新
- **ES Module 导入**：支持 `import confetti from 'canvas-confetti'` 加载 npm 包

### 独特机制：iframe 沙箱渲染

p5 内核是目前唯一使用 iframe 渲染的 JupyterLite 内核。代码执行流程：

1. 用户代码在 Web Worker 中的 JavaScript 运行时执行
2. 内核将累积的代码打包为 iframe srcdoc HTML
3. iframe 加载 p5.js CDN，执行累积代码
4. p5.js 的 draw() 循环在 iframe 中运行动画
5. 画布通过 iframe 与 Notebook UI 隔离，避免 DOM 冲突

### 适用场景

- 创意编程和生成艺术
- 交互式动画和视觉效果
- p5.js 教学
- 浏览器端图形演示

## 内核选择策略

| 需求 | 推荐内核 | 原因 |
|------|----------|------|
| 数据分析/科学计算 | Pyodide | numpy/pandas/matplotlib 生态成熟 |
| 交互式可视化 | Pyodide | plotly/bqplot/altair 功能强大 |
| 地图/GIS 应用 | Pyodide | folium/ipyleaflet 可用 |
| JavaScript 学习/测试 | JavaScript | 原生 JS，无额外开销 |
| 创意编程/动画 | p5.js | setup/draw 模型 + iframe 画布 |
| 需要 DOM 操作 | p5.js | iframe 可操作自己的 DOM |
| 教学演示（多语言） | 全部 | 三种内核展示不同编程范式 |

## Xeus 内核（可选）

Demo 未包含 Xeus Python 内核，但它是一个重要的替代方案。Xeus 是一个 C++ 原生 WASM 内核框架，支持更多编译型扩展包。如需使用，可参考 [jupyterlite/xeus-python-demo](https://github.com/jupyterlite/xeus-python-demo) 模板。

| 对比项 | Pyodide 内核 | Xeus Python 内核 |
|--------|-------------|-----------------|
| CPython 编译方式 | Emscripten (Pyodide 项目) | 原生 WASM (emscripten-forge) |
| 包管理 | micropip（PyPI wheel） | empack（conda 包） |
| 包兼容性 | Pyodide 预编译包丰富 | 支持更多 C 扩展 |
| 启动速度 | 较快 | 较慢 |
| JS 互操作 | 成熟（js 模块） | 正在完善 |

## 相关概念

- [Demo 仓库结构与三件套模式](/concepts/01-demo-overview.md)
- [Pyodide 生态库与 %pip 安装](/concepts/05-pyodide-libraries.md)
- [内容目录与数据文件组织](/concepts/04-content-and-data.md)
- [Python 内核基础使用](/examples/02-python-basics.md)
- [创意编程与物理模拟](/examples/06-creative-coding.md)
