---
type: Concept
title: 架构概览
description: p5-kernel 的整体架构设计、继承关系、三层结构、关键数据流与核心设计决策
tags: [architecture, inheritance, iframe-runtime, code-registry, data-flow, design]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T17:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: kernel-src
    resource: /references/kernel-source.md
    title: P5Kernel 类 API 信源
  - id: executor-src
    resource: /references/executor-source.md
    title: P5Executor 类 API 信源
  - id: ext-src
    resource: /references/extension-source.md
    title: JupyterLab 扩展注册信源
---

## 整体架构

p5-kernel 采用**继承+组合**的设计模式，在 JupyterLite JavaScript 内核之上通过最小化扩展实现 p5.js 创意编程支持。整个内核仅包含约 280 行核心 TypeScript 代码（kernel.ts ~230行 + executor.ts ~50行），通过三个关键扩展点工作：

1. **强制 iframe 运行时**：将代码执行环境从 Web Worker 切换到 iframe
2. **P5Executor 特化**：覆写 MIME 渲染和内置文档
3. **%show magic 命令**：在 iframe 中渲染完整 p5 sketch

## 继承关系图

```
┌─────────────────────────────────────────────────────────┐
│           @jupyterlite/services                         │
│  IKernelSpecs, IKernel, KernelMessage types             │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│     @jupyterlite/javascript-kernel                      │
│  ┌──────────────────┐  ┌──────────────────────┐         │
│  │ JavaScriptKernel │  │ JavaScriptExecutor   │         │
│  │ (基础内核类)     │──│ (基础执行器类)       │         │
│  │ - Worker 通信    │  │ - MIME 渲染          │         │
│  │ - executeRequest │  │ - 代码注册表管理      │         │
│  │ - import 处理    │  │ - import 提取/生成    │         │
│  │ - iframe/Worker  │  │ - 内置文档查询       │         │
│  │   双 runtime     │  │ - getMimeBundle()    │         │
│  └────────┬─────────┘  └──────────┬───────────┘         │
└───────────┼───────────────────────┼─────────────────────┘
            │ extends               │ extends
┌───────────▼───────────────────────▼─────────────────────┐
│              @jupyterlite/p5-kernel                      │
│  ┌──────────────────┐  ┌──────────────────────┐         │
│  │    P5Kernel      │  │     P5Executor       │         │
│  │ - 强制 iframe    │  │ - p5.Graphics → PNG  │         │
│  │ - p5 bootstrap   │  │ - P5_DOCS 内建文档    │         │
│  │ - %show magic    │  │                      │         │
│  │ - CodeRegistry   │  │                      │         │
│  │ - import 追踪    │  │                      │         │
│  │ - display 更新   │  │                      │         │
│  └──────────────────┘  └──────────────────────┘         │
└─────────────────────────────────────────────────────────┘
            ▲
            │ create()
┌───────────┴─────────────────────────────────────────────┐
│        @jupyterlite/p5-kernel-extension                  │
│  - JupyterFrontEndPlugin 注册                           │
│  - KernelSpec 定义 (name='p5js')                        │
│  - p5Url CDN 配置与解析                                 │
│  - P5Kernel 实例工厂                                    │
└─────────────────────────────────────────────────────────┘
```

## 三层线程/渲染模型

```
┌─────────────────────────────────────────────────────────┐
│  主线程 (JupyterLab UI)                                  │
│  ┌───────────────────────────────────────────────────┐  │
│  │ JupyterLab Notebook 插件                          │  │
│  │ ├─ KernelSpec 注册 (p5js)                         │  │
│  │ ├─ 内核选择器显示 p5.js logo                      │  │
│  │ └─ display_data 渲染 iframe                       │  │
│  └───────────────────────┬───────────────────────────┘  │
│                          │ Jupyter 内核协议消息          │
│                          │ (execute_request 等)         │
└──────────────────────────┼──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│  Web Worker (JavaScript 运行时)                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │ P5Kernel (extends JavaScriptKernel)               │  │
│  │ ├─ 执行用户 JS 代码（变量、函数定义）               │  │
│  │ ├─ 累积代码到 CodeRegistry (AST 去重)              │  │
│  │ ├─ 提取并追踪 import 语句                         │  │
│  │ ├─ 生成 iframe srcdoc（bootstrap+imports+code）   │  │
│  │ └─ 通过 display_data 发送 iframe HTML             │  │
│  │                                                    │  │
│  │ P5Executor (extends JavaScriptExecutor)           │  │
│  │ ├─ 管理 CodeRegistry                              │  │
│  │ ├─ 提取/生成 import 代码                          │  │
│  │ └─ p5.Graphics → PNG 渲染                         │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                           │ iframe srcdoc
                           ▼
┌─────────────────────────────────────────────────────────┐
│  iframe (p5.js 渲染沙箱)                                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │ <body>                                            │  │
│  │ <script>                                          │  │
│  │   import(p5Url).then(() => {                     │  │
│  │     window.__globalP5 = new p5();  // bootstrap  │  │
│  │     // → 加载 imports                             │  │
│  │     // → 执行累积的用户代码（setup/draw/变量）     │  │
│  │     window.__globalP5._start();  // 启动 sketch   │  │
│  │   });                                             │  │
│  │ </script>                                         │  │
│  │ </body>                                           │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## 关键数据流

### 1. 代码执行流（非 magic cell）

```
用户执行 cell 代码
    │
    ▼
P5Kernel.executeRequest(code)
    │
    ├─ super.executeRequest(content)
    │     └─ JavaScriptKernel 在 Worker 中执行 JS
    │        ├─ 变量/函数定义生效（Worker 全局作用域）
    │        └─ 返回执行结果（文本输出等）
    │
    ├─ _p5Executor.registerCode(code, _codeRegistry)
    │     └─ AST 分析代码，后定义覆盖前定义
    │
    ├─ executor.extractImports(code)
    │     └─ 提取 ES import 语句，去重存入 _imports
    │
    └─ _magics() → 重新生成 iframe HTML
          └─ updateDisplayData() 更新所有已显示的 %show 输出
```

### 2. %show 渲染流

```
用户执行 %show [width] [height]
    │
    ▼
P5Kernel.executeRequest('%show ...')
    │
    ├─ code.startsWith('%show') → true
    │
    ├─ _magics(code)
    │     ├─ generateImportCode(_imports) → import 加载代码
    │     ├─ generateCodeFromRegistry(_codeRegistry) → 去重合并代码
    │     ├─ 组装 script: bootstrap → imports → code → _start()
    │     ├─ 解析 width/height 参数（默认 100% / 400px）
    │     ├─ 构造 iframe srcdoc HTML
    │     └─ HTML 转义 srcdoc 属性值
    │
    ├─ displayData({ 'text/html': iframe }, { display_id })
    │     └─ 父消息头入栈 _parentHeaders
    │
    └─ 返回 { status: 'ok' }
```

## 核心设计决策

### 决策 1：iframe 运行时而非 Worker 内渲染

p5.js 的全局模式（global mode）会向 window 对象注入数百个全局函数（setup、draw、circle、fill 等），并操作 DOM 创建 canvas。Web Worker 没有 DOM 和 window 对象，无法直接运行 p5.js。P5Kernel 强制使用 `runtime: 'iframe'` 模式，让 p5.js 在拥有完整 DOM 环境的 iframe 中运行。

### 决策 2：代码累积而非单 cell 全量

传统 Notebook 中每个 cell 独立执行，而 p5 sketch 需要 setup() 和 draw() 配合工作。P5Kernel 使用 CodeRegistry（基于 AST 分析）累积所有 cell 的非 magic 代码，后定义的函数/变量自动覆盖前面的，然后 `%show` 时一次性在 iframe 中执行。这让用户可以将变量定义、setup()、draw() 分散在不同 cell 中，符合 Notebook 的 cell-by-cell 工作习惯。

### 决策 3：继承而非重写

P5Kernel 不重新实现 JS 执行、import 处理、Worker 通信等基础能力，而是继承 JavaScriptKernel，仅覆写三个关键方法：`kernelInfoRequest()`（修改内核信息）、`executeRequest()`（增加 %show 和代码累积）、`onRuntimeReady()`（初始化 p5 环境）。这使得核心代码极精简，同时自动获得 JavaScriptKernel 的所有能力（包括 ES Module import 支持）。

### 决策 4：srcdoc iframe 隔离

每次 `%show` 都生成新的 iframe，使用 `srcdoc` 属性直接嵌入完整 HTML。这确保了：
- sketch 崩溃不影响 Notebook UI
- sketch 的 DOM 操作不泄露到宿主页面
- 多次 `%show` 产生的 sketch 互不干扰
- 无需额外服务器或 iframe 通信

## 相关概念

- [P5Kernel 实现详解](/concepts/02-kernel-implementation.md)
- [P5Executor 与渲染机制](/concepts/03-executor-and-rendering.md)
- [%show 魔法命令](/concepts/04-magic-commands.md)
- [扩展注册与 CDN 配置](/concepts/05-extension-registration.md)
