---
sources:
- ../../../../../external/libs/jupyter/p5-kernel/pyproject.toml
- ../../../../../external/libs/jupyter/p5-kernel/package.json
- ../../../../../external/libs/jupyter/p5-kernel/README.md
- ../../../../../external/libs/jupyter/p5-kernel/setup.py
- ../../../../../external/libs/jupyter/p5-kernel/lerna.json
- ../../../../../external/libs/jupyter/p5-kernel/packages/p5-kernel-extension/package.json
- ../../../../../external/libs/jupyter/p5-kernel/packages/p5-kernel-extension/src/declarations.d.ts
- ../../../../../external/libs/jupyter/p5-kernel/packages/p5-kernel-extension/src/index.ts
- ../../../../../external/libs/jupyter/p5-kernel/packages/p5-kernel-extension/style/index.js
- ../../../../../external/libs/jupyter/p5-kernel/packages/p5-kernel-extension/tsconfig.json
- ../../../../../external/libs/jupyter/p5-kernel/packages/p5-kernel/package.json
- ../../../../../external/libs/jupyter/p5-kernel/packages/p5-kernel/src/executor.ts
- ../../../../../external/libs/jupyter/p5-kernel/packages/p5-kernel/src/index.ts
- ../../../../../external/libs/jupyter/p5-kernel/packages/p5-kernel/src/kernel.ts
- ../../../../../external/libs/jupyter/p5-kernel/packages/p5-kernel/style/index.js
- ../../../../../external/libs/jupyter/p5-kernel/packages/p5-kernel/tsconfig.json
type: Insights
okf_version: '0.2'
title: p5-kernel 架构洞察
generated: '2026-08-22'
tags:
- insights
- architecture
---

# p5-kernel 架构洞察

> I阶段（架构洞察）产出的核心洞察四元组，每个洞察包含陈述、证据、反常识点和行动建议。

## 洞察 1：继承而非重写——280 行代码实现完整内核

**陈述**：P5Kernel 通过继承 JavaScriptKernel 并仅覆写 3 个方法（constructor、kernelInfoRequest、executeRequest、onRuntimeReady），加上一个仅 50 行的 P5Executor 子类，就实现了完整的 p5.js 内核支持，核心代码总计约 280 行。

**证据**：
- P5Kernel 继承 JavaScriptKernel（F-013），强制 iframe runtime（F-016）
- P5Executor 继承 JavaScriptExecutor（F-014），仅覆写 getMimeBundle 和 getBuiltinDocumentation（F-036~F-040）
- 所有 JS 执行、Worker 通信、ES Module import 处理均复用父类能力

**反常识**：通常认为实现一个 Jupyter 内核需要实现完整的消息协议和执行引擎，但 p5-kernel 证明了"特化"而非"重写"的路径——通过强制运行时模式（iframe）+ 覆写关键钩子（executeRequest 增加代码累积和 magic 处理）+ 组合（P5Executor），可以极小的代码量获得内核能力。JavaScriptKernel 的设计本身就是为扩展而优化的。

**行动**：开发 JupyterLite 自定义内核时，优先考虑继承 JavaScriptKernel 而非从零实现 BaseKernel。参考 p5-kernel 的模式：构造函数注入 runtime 和 executorFactory → 覆写 executeRequest 增加预处理/后处理 → 覆写 onRuntimeReady 初始化环境。

## 洞察 2：iframe 沙箱——p5.js 全局模式与 Notebook 的隔离桥接

**陈述**：p5-kernel 是唯一强制使用 iframe runtime 的 JupyterLite 内核，它不在 Worker 中渲染 p5 画布，而是将累积代码注入独立 iframe 执行。这解决了 p5.js 全局模式注入数百个 window 属性和 DOM 操作与 JupyterLab UI 冲突的问题。

**证据**：
- 构造函数强制 `runtime: 'iframe'`（F-016）
- onRuntimeReady 中验证 runtime 必须为 iframe（F-022~F-023）
- %show 生成 iframe srcdoc，包含完整 HTML body 和 script（F-029~F-033）
- 每个 %show 输出都是独立 iframe，互不干扰

**反常识**：直觉上 p5.js 应该在 Worker 中执行（与 Pyodide/Xeus 一致），但 Worker 没有 DOM 和 window 对象，无法运行 p5.js 的全局模式。iframe 虽然引入了额外的序列化和通信成本，但提供了完整 DOM 环境和沙箱隔离，使得 p5.js 可以不加修改地运行。这是"正确的抽象层选择"——不是所有内核都适合 Worker 模式。

**行动**：需要 DOM 访问、全局变量注入、或第三方库操作 DOM 的 JupyterLite 内核应选择 iframe runtime。渲染结果通过 srcdoc iframe 展示，代码在 Worker 中累积和预处理，最终渲染委托给 iframe。

## 洞察 3：AST 代码累积——Notebook Cell 模型与 p5 全局模型的桥接

**陈述**：p5-kernel 使用基于 AST 的 CodeRegistry 累积多个 cell 的代码，后定义的变量/函数自动覆盖前面的定义，%show 时生成去重合并后的完整代码。这让用户可以将 setup()、draw()、变量定义分散在任意 cell 中，符合 Notebook 的增量编程习惯，同时保持 p5.js 全局 sketch 模型的完整性。

**证据**：
- 非 magic 代码通过 registerCode 注册到 CodeRegistry（F-025）
- combinedCode 由 generateCodeFromRegistry 生成（F-030），基于 AST 分析
- imports 通过 extractImports 提取并按 source 去重（F-026, F-067）
- 每次普通代码执行后自动更新所有已显示的 %show 输出（F-034~F-035）

**反常识**：简单的字符串拼接累积代码会导致重复的 `let`/`const` 声明和函数重定义错误。p5-kernel 没有采用"最后一个 cell 覆盖前面全部"的简单策略，而是利用 JavaScriptKernel 已有的 AST 级 CodeRegistry，实现了精细的去重合并。这意味着同一个变量可以在不同 cell 中反复赋值，同一个函数可以反复修改定义，%show 始终拿到语义正确的最新版本。

**行动**：为 Notebook 类环境开发需要"全局状态"的内核（如创意编程、数据可视化）时，不要简单拼接代码字符串，应使用 AST 级别的代码注册表。JavaScriptKernel 的 ICodeRegistry 提供了现成的实现。

## 洞察 4：构建时文档生成——解决运行时内省盲区

**陈述**：p5.js 全局模式下 API 是 bound function，运行时 `console.log(createCanvas)` 只显示 `function bound ()`，无法获取签名。p5-kernel 在构建时从 @types/p5 的 TypeScript 类型定义自动生成 P5_DOCS 映射，为 Shift+Tab 代码内省提供函数签名和描述，解决了全局模式下运行时文档缺失的问题。

**证据**：
- generate-p5-docs.mjs 在构建前从 @types/p5/global.d.ts 解析 JSDoc（F-041~F-047）
- 重载函数保留参数最多的版本（F-043）
- P5Executor.getBuiltinDocumentation 覆写父类方法，从 P5_DOCS 查找文档（F-040）
- 构建流程强制 generate:docs 在 tsc 之前执行（F-047）

**反常识**：运行时内省通常依赖函数对象自身的属性（如 .length、.name、.toString()），但全局模式下的 bound function 丢失了所有元信息。p5-kernel 没有尝试在运行时反推函数签名（不可靠），而是转向构建时——TypeScript 类型定义已经包含了完整的 JSDoc 文档，利用编译器 API 提取这些信息比运行时方案更准确、更完整。

**行动**：为使用全局模式/绑定函数模式的 JS 库开发内核或工具时，考虑构建时从类型定义（@types/*）提取文档，而非运行时内省。TypeScript Compiler API 可以可靠地解析 JSDoc 和函数签名。

## 知识地图

```
p5-kernel 知识体系
├── 入门
│   ├── 是什么 / 为什么用 / 安装
│   └── 生态位置（与 JS/Pyodide/Echo 内核对比）
├── 架构
│   ├── 继承关系（P5Kernel → JavaScriptKernel → BaseKernel）
│   ├── 三层模型（UI主线程 / Worker执行 / iframe渲染）
│   └── 关键数据流（代码执行流 / %show渲染流）
├── 核心机制
│   ├── P5Kernel：bootstrap / executeRequest / onRuntimeReady
│   ├── P5Executor：Graphics→PNG / P5_DOCS内建文档
│   ├── %show magic：参数解析 / srcdoc生成 / display更新
│   └── CodeRegistry：AST代码累积 / import去重 / 实时更新
├── 扩展与配置
│   ├── JupyterLab插件注册
│   ├── CDN配置与覆盖
│   └── KernelSpec定义
└── 构建发布
    ├── TypeScript构建 + p5-docs生成
    ├── Hatchling Python包
    └── 双发布（npm + PyPI）
```
