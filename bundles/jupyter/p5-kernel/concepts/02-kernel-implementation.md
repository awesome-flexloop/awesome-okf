---
type: Concept
title: P5Kernel 实现详解
description: P5Kernel 类的构造函数、bootstrap 机制、kernelInfoRequest、executeRequest 执行流程、onRuntimeReady 生命周期的逐行解析
tags: [p5kernel, implementation, constructor, bootstrap, execute-request, lifecycle, typescript]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T17:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: kernel
    resource: /references/kernel-source.md
    title: P5Kernel 类 API 信源
---

## P5Kernel 类概述

`P5Kernel` 是 p5-kernel 的核心类，继承自 `JavaScriptKernel`（来自 `@jupyterlite/javascript-kernel`）。它的核心职责是：在 JavaScript 内核的基础上增加 p5.js 的加载、代码累积、%show 渲染和 display 更新能力。

类定义位于 [kernel.ts](https://github.com/jupyterlite/p5-kernel/blob/main/packages/p5-kernel/src/kernel.ts)。

## 构造函数

```typescript
constructor(options: P5Kernel.IOptions) {
  super({
    ...options,
    runtime: 'iframe',
    executorFactory: globalScope =>
      new P5Executor(globalScope as unknown as Window)
  });
  const { p5Url } = options;
  this._displayId = this.id;
  this._bootstrap = `
    import('${p5Url}').then(() => {
      window.__globalP5 = new p5();
      return Promise.resolve();
    })
  `;
}
```

构造函数完成三件事：

1. **调用父类构造函数**：传入 `runtime: 'iframe'` 强制使用 iframe 运行时（而非 Web Worker），并指定 `executorFactory` 创建 `P5Executor` 实例。`globalScope` 在 iframe 模式下是 iframe 的 window 对象。

2. **设置 display id**：`this._displayId = this.id` 使用内核的唯一 id 作为 display data 的标识，后续 `updateDisplayData` 需要此 id 来定位要更新的输出。

3. **生成 bootstrap 代码**：`_bootstrap` 是一段 JavaScript 代码字符串，通过动态 `import()` 加载 p5.js（URL 由 p5Url 参数指定），加载完成后创建全局 p5 实例 `window.__globalP5 = new p5()`。`new p5()` 在全局模式下会自动查找 setup()/draw() 函数，但这里先创建实例、稍后通过 `_start()` 启动。

### IOptions 接口

```typescript
interface IOptions extends JavaScriptKernel.IOptions {
  p5Url: string;       // p5.js 的 CDN URL，必填
  runtime?: 'iframe';  // 运行时模式，固定为 iframe
}
```

`p5Url` 由扩展注册时传入（默认 CDN 为 `https://cdn.jsdelivr.net/npm/p5@1.9.0/lib/p5.js`）。

## kernelInfoRequest()

```typescript
override async kernelInfoRequest(): Promise<KernelMessage.IInfoReplyMsg['content']>
```

当 Jupyter 客户端发送 `kernel_info_request` 消息时调用，返回内核元信息。p5-kernel 的关键信息：

- **implementation**: `'p5.js'` — 内核实现名称
- **implementation_version**: `'0.1.0'` — 内核版本（注意：这是内核实现版本，不是 p5.js 版本）
- **language_info.name**: `'p5js'` — 语言名，在 Notebook 界面显示为 "p5js"
- **codemirror_mode.name**: `'javascript'` — 代码编辑器使用 JavaScript 语法高亮
- **file_extension**: `'.js'` — Notebook 文件扩展名
- **pygments_lexer**: `'javascript'` — 导出时使用 JavaScript 词法分析器
- **protocol_version**: `'5.3'` — Jupyter 内核协议版本

这个覆写确保 JupyterLab/Notebook 将 p5.js 内核识别为一种独立语言，但代码编辑体验保持 JavaScript 的语法高亮和自动补全。

## executeRequest() 执行流程

`executeRequest()` 是内核最核心的方法，处理 `execute_request` 消息（即用户执行 cell 时发送的消息）。

### 处理流程

```
executeRequest(content)
  │
  ├─ 提取 code 和构造 transient (display_id)
  │
  ├─ code.startsWith('%show')?
  │    ├─ YES: _magics(code) → displayData() → 记录 parentHeader → 返回 ok
  │    └─ NO:  ↓
  │
  ├─ super.executeRequest(content)  // JavaScriptKernel 执行 JS 代码
  │    └─ 若 status !== 'ok'，直接返回错误
  │
  ├─ code 不以 '%' 开头?
  │    ├─ registerCode(code, _codeRegistry)  // AST 累积代码
  │    └─ extractImports(code) → 去重加入 _imports
  │
  └─ _magics() → updateDisplayData() 更新所有已有 display
       └─ 返回 reply
```

### %show magic 优先处理

当代码以 `%show` 开头时，内核不执行 JavaScript 代码，而是直接调用 `_magics(code)` 生成 iframe HTML，通过 `displayData()` 发送到前端显示。同时将当前消息头存入 `_parentHeaders` 数组，用于后续的 `updateDisplayData`。

### 普通代码执行

非 magic 代码通过 `super.executeRequest()` 交给 JavaScriptKernel 处理。这一步在 iframe 中执行 JavaScript 代码，变量和函数定义生效（在 iframe 的 window 作用域中）。

如果代码不是 magic 命令（不以 `%` 开头），还会额外执行两个操作：
1. **代码注册**：`_p5Executor.registerCode(code, this._codeRegistry)` 将代码注册到 AST 代码注册表，后续 `%show` 时通过 AST 分析生成去重合并后的完整代码
2. **Import 追踪**：`executor.extractImports(code)` 提取 ES import 语句，去重后存入 `_imports` 数组

### 自动更新已有显示

每次执行非 magic 代码后，内核调用 `_magics()`（无参数，使用当前累积的代码）生成最新的 iframe HTML，然后遍历 `_parentHeaders` 数组，对每个已显示的 `%show` 输出调用 `updateDisplayData()` 更新内容。这意味着：**用户在任意 cell 中修改变量或函数后，所有已显示的 sketch 会自动更新**，无需重新执行 `%show`。

## onRuntimeReady() 生命周期

```typescript
protected override async onRuntimeReady(
  context: JavaScriptKernel.IRuntimeReadyContext
): Promise<void>
```

这是父类 JavaScriptKernel 定义的生命周期钩子，在 iframe 运行时初始化完成后调用。

```typescript
if (context.runtime !== 'iframe') {
  throw new Error('P5Kernel requires iframe runtime');
}
this._p5Executor = context.executor as P5Executor;
this._codeRegistry = this._p5Executor.createCodeRegistry();
await context.execute(this._bootstrap);
```

执行步骤：

1. **运行时断言**：检查 `context.runtime === 'iframe'`，不是 iframe 则抛出错误。这是一个防御性检查，确保 P5Kernel 不会意外在 Worker 模式下运行。
2. **获取 Executor**：将 `context.executor` 保存为 `P5Executor` 类型，后续代码注册和 import 处理都需要它。
3. **创建 CodeRegistry**：调用 `createCodeRegistry()` 创建代码注册表实例。
4. **执行 Bootstrap**：在 iframe 中执行 `_bootstrap` 代码，加载 p5.js 并创建全局 `window.__globalP5` 实例。这一步是异步的，确保 p5.js 加载完成后才接受后续执行请求。

## 私有字段一览

| 字段 | 类型 | 初始值 | 设置时机 | 用途 |
|------|------|--------|---------|------|
| `_displayId` | `string` | `this.id` | 构造函数 | display_data 的 display_id，用于更新已有输出 |
| `_bootstrap` | `string` | 动态 import 代码 | 构造函数 | p5.js 加载和全局实例创建的引导代码 |
| `_p5Executor` | `P5Executor \| undefined` | `undefined` | onRuntimeReady | P5Executor 实例引用 |
| `_codeRegistry` | `ICodeRegistry \| undefined` | `undefined` | onRuntimeReady | AST 代码注册表，累积用户代码 |
| `_imports` | `IImportInfo[]` | `[]` | executeRequest | 去重后的 import 语句列表 |
| `_parentHeaders` | `IHeader[]` | `[]` | executeRequest | 已发送 display_data 的消息头列表 |

## 设计要点

1. **bootstrap 只执行一次**：`_bootstrap` 在 `onRuntimeReady` 中执行一次，p5.js 全局实例只创建一次。后续每次 `%show` 的 iframe 中也会重新执行 bootstrap（因为每个 iframe 是独立的），但 Worker 侧的代码累积是持久的。

2. **代码累积是 AST 级别的**：`registerCode` 不是简单的字符串拼接，而是通过 AST 分析理解代码结构（变量声明、函数定义等），后定义的同名变量/函数自动覆盖前面的，避免了简单字符串拼接导致的重复定义问题。

3. **display 自动更新是全量替换**：每次普通代码执行后，所有 `%show` 输出都会被更新为最新累积代码生成的 iframe。这不是增量更新 DOM，而是替换整个 iframe srcdoc，但由于 iframe 是独立的，用户不会察觉到闪烁。

## 相关概念

- [P5Executor 与渲染机制](/concepts/03-executor-and-rendering.md)
- [%show 魔法命令详解](/concepts/04-magic-commands.md)
- [架构概览](/concepts/01-architecture-overview.md)
