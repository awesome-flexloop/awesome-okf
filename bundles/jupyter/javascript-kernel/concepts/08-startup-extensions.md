---
type: Concept
title: 启动扩展机制
description: IJavaScriptKernelStartupRegistry Token、前端插件预加载模块和注册 Comm Target
tags: [startup, extension, plugin, preload, registry, token, lumino]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: jk-startup
    title: startup.ts
  - id: jk-kernel
    title: kernel.ts
  - id: jk-ext-index
    title: javascript-kernel-extension/src/index.ts
---

# 启动扩展机制

Startup Extension 机制允许 JupyterLab 前端插件在用户代码执行之前，向 JavaScript 内核的运行时注入代码、预加载模块和注册 comm target。这是前端扩展与 JS 内核集成的主要方式。

## 为什么需要 Startup Extension？

在 Jupyter 架构中，内核和前端运行在不同的执行环境中：
- **内核端**：iframe 或 Web Worker 内（代码执行环境）
- **前端**：JupyterLab 主线程（UI 和插件）

前端插件无法直接在内核运行时中执行代码。Startup Extension 提供了一个桥接机制，让前端插件可以：
1. 在内核启动后、用户执行任何代码前自动执行预加载逻辑
2. 注册自定义 comm target 处理器
3. 预加载 ES 模块到内核全局作用域

## IJavaScriptKernelStartupRegistry Token

`IJavaScriptKernelStartupRegistry` 是一个 Lumino Token，前端插件通过依赖它来注册 startup extension：

```typescript
const IJavaScriptKernelStartupRegistry = new Token<IJavaScriptKernelStartupRegistry>(
  '@jupyterlite/javascript-kernel:IJavaScriptKernelStartupRegistry'
);
```

### 接口定义

```typescript
interface IJavaScriptKernelStartupRegistry {
  registerStartupExtension(extension: IStartupExtension): IDisposable;
}

interface IStartupExtension {
  id: string;
  activate: (context: IRuntimeReadyContext) => Promise<void> | void;
  deactivate?: (context: IRuntimeReadyContext) => Promise<void> | void;
}
```

| 方法/属性 | 说明 |
|----------|------|
| `registerStartupExtension(extension)` | 注册启动扩展，返回 IDisposable |
| `extension.id` | 扩展唯一标识符 |
| `extension.activate(context)` | 内核 ready 后调用的初始化函数 |
| `extension.deactivate(context)` | 可选，扩展被 dispose 时调用的清理函数 |

## IRuntimeReadyContext

`activate` 和 `deactivate` 接收一个上下文对象，提供操作内核运行时的能力：

### 通用方法（两种模式都支持）

| 方法 | 说明 |
|------|------|
| `execute(code, executionCount?)` | 在内核中执行 JavaScript 代码 |
| `preloadModule(moduleName)` | 预加载 ES 模块，导入项自动暴露到 globalThis |
| `registerCommTarget(targetName, moduleName, exportName?)` | 从 ES 模块注册 comm target handler |
| `unregisterCommTarget(targetName)` | 注销 comm target |

### IFrame 模式专属

| 属性 | 说明 |
|------|------|
| `iframe` | iframe DOM 元素引用 |
| `container` | 隐藏的容器 div |
| `globalScope` | iframe 的 window 对象 |
| `executor` | JavaScriptExecutor 实例 |

### Worker 模式限制

Worker 模式的 context **不包含** `iframe`、`container`、`globalScope`、`executor`——Worker 线程的全局作用域无法从主线程直接访问，只能通过 `execute()` 和 `preloadModule()` 间接操作。

## 注册 Startup Extension（前端插件）

```typescript
import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { IJavaScriptKernelStartupRegistry } from '@jupyterlite/javascript-kernel';

const myPlugin: JupyterFrontEndPlugin<void> = {
  id: 'my-extension:js-kernel-startup',
  autoStart: true,
  requires: [IJavaScriptKernelStartupRegistry],
  activate: (app: JupyterFrontEnd, startup: IJavaScriptKernelStartupRegistry) => {
    startup.registerStartupExtension({
      id: 'my-extension:bootstrap',

      activate: async (context) => {
        // 1. 预加载自定义模块
        await context.preloadModule('https://cdn.example.com/my-widgets.js');

        // 2. 注册 comm target
        await context.registerCommTarget(
          'my-extension:comm',
          'https://cdn.example.com/my-comm-handler.js'
        );

        // 3. 直接执行初始化代码（仅 IFrame 模式支持 globalScope）
        await context.execute(`
          globalThis.myExtension = {
            version: '1.0.0',
            initialized: true
          };
          console.log('[MyExtension] Initialized');
        `);
      },

      deactivate: async (context) => {
        // 清理逻辑
        await context.unregisterCommTarget('my-extension:comm');
        await context.execute(`
          delete globalThis.myExtension;
        `);
      }
    });
  }
};

export default myPlugin;
```

## 执行时机

```
JupyterLab 启动
    │
    ├─► 前端插件 activate() 被调用
    │   └─► registerStartupExtension() 注册到注册表
    │
    ├─► 用户创建/选择 JavaScript Kernel
    │   └─► JavaScriptKernel 构造函数
    │       └─► createBackend() → 开始异步初始化
    │
    ├─► 后端 ready（Comlink 通道建立，evaluator 初始化）
    │   └─► onReady(ctx) 回调
    │       └─► 遍历 _startupExtensions，调用 activate(ctx)
    │
    └─► ready Promise resolve → 内核开始接受用户代码执行
```

关键点：
- Startup Extension 的 `activate` 在用户**第一个单元格执行之前**完成
- activate 可以是 async 函数，内核等待所有 activate 完成后才标记 ready
- 注册顺序决定了执行顺序（先注册先执行）

## IDisposable 返回值

`registerStartupExtension` 返回 `IDisposable`：

```typescript
const disposable = startup.registerStartupExtension(extension);

// 稍后需要卸载扩展时：
disposable.dispose();  // 调用 extension.deactivate(ctx) 并从注册表移除
```

dispose 时：
1. 如果内核已 ready，调用 `extension.deactivate(context)`（如果定义了）
2. 从 startup extensions 列表中移除该扩展

## preloadModule 详解

`preloadModule(moduleName)` 导入 ES 模块并将所有命名导出和默认导出暴露到 `globalThis`：

```javascript
// 预加载模块的概念性实现
async function preloadModule(moduleName) {
  const module = await import(moduleName);
  for (const [key, value] of Object.entries(module)) {
    globalThis[key] = value;
  }
  if (module.default) {
    globalThis[moduleName] = module.default;
  }
}
```

这意味着模块的所有顶层导出在用户代码中可以直接使用：

```javascript
// 在 my-module.js 中：
export function greet(name) { return `Hello, ${name}!`; }
export const VERSION = '1.0.0';

// preloadModule 后，用户代码中可以直接调用：
greet("World");  // 'Hello, World!'
console.log(VERSION);  // '1.0.0'
```

## registerCommTarget 详解

`registerCommTarget(targetName, moduleUrl, exportName?)` 通过 URL 加载模块并注册 comm target handler：

```typescript
await context.registerCommTarget(
  'my-target',                    // comm target_name
  './my-comm-module.js',          // 模块 URL（相对于 baseUrl 或绝对 URL）
  'createCommHandler'             // 可选，导出函数名，默认 'create'
);
```

模块需要导出一个异步函数，接收 `{ commManager }` 参数：

```javascript
// my-comm-module.js
export async function create({ commManager }) {
  commManager.registerTarget('my-target', (comm, message) => {
    // 处理前端打开的 comm
    comm.onMsg = ({ data }) => {
      // 处理来自前端的消息
      comm.send({ response: 'received' });
    };
  });
}
```

## 内置 Startup Extensions

扩展包（`@jupyterlite/javascript-kernel-extension`）使用 startup extension 机制注册：

1. **Widget Manager**：确保 widget 基础 comm target（`jupyter.widget`、`jupyter.widget.control`）在内核启动时注册
2. **Console 捕获**：确保 console 重定向在用户代码执行前生效

## 实际应用场景

### 场景1：自定义 Widget 库

第三方 Widget 库可以通过 startup extension 预加载 widget 模块并注册 comm handler，用户无需手动 import：

```typescript
startup.registerStartupExtension({
  id: 'my-widget-lib:setup',
  activate: async (context) => {
    await context.preloadModule('https://cdn.example.com/my-widget-lib.js');
    await context.registerCommTarget(
      'my-widget-lib:comm',
      'https://cdn.example.com/my-widget-comm.js'
    );
  }
});
```

用户在 Notebook 中直接使用：
```javascript
// 不需要 import！myWidgets 已在 globalThis 上
const widget = new myWidgets.CustomChart({ data: [1, 2, 3] });
display(widget);
```

### 场景2：开发环境增强

```typescript
startup.registerStartupExtension({
  id: 'dev-tools:setup',
  activate: async (context) => {
    await context.execute(`
      globalThis.$$ = (sel) => document.querySelector(sel);
      globalThis.$$$ = (sel) => document.querySelectorAll(sel);
      console.log('Dev tools ready: $$, $$$ available');
    `);
  }
});
```

### 场景3：数据预加载

```typescript
startup.registerStartupExtension({
  id: 'data-bootstrap',
  activate: async (context) => {
    await context.execute(`
      globalThis.DATASETS = {};
    `);
    await context.preloadModule('https://cdn.example.com/datasets/iris.js');
  }
});
```

## 相关文档

- [02-内核架构](02-kernel-architecture.md) — JavaScriptKernel 如何应用 startup extensions
- [04-运行时后端](04-runtime-backends.md) — IRuntimeReadyContext 在两种模式下的差异
- [06-Comm 协议](06-comm-protocol.md) — Comm target 注册和消息处理
- [06-前端扩展示例](../references/api-reference.md#jupyter.comm) — Comm 和 Widget 全局 API 参考
