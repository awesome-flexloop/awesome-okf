---
type: Concept
title: 运行时后端
description: IFrame 和 Web Worker 两种运行时后端的实现机制、Comlink RPC 通信和初始化流程
tags: [runtime, iframe, worker, comlink, rpc, backend, isolation]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: jk-backends
    title: runtime_backends.ts
  - id: jk-remote
    title: runtime_remote.ts
  - id: jk-protocol
    title: runtime_protocol.ts
  - id: jk-evaluator
    title: runtime_evaluator.ts
  - id: jk-worker
    title: worker-runtime.ts
---

# 运行时后端

JavaScript Kernel 通过 `IRuntimeBackend` 接口抽象代码执行环境，提供两种实现：`IFrameRuntimeBackend` 和 `WorkerRuntimeBackend`。两者都使用 [Comlink](https://github.com/GoogleChromeLabs/comlink) 库实现主线程与隔离环境之间的 RPC 通信。

## 架构概览

```
┌───────────────── 主线程 ─────────────────┐
│                                          │
│  JavaScriptKernel                        │
│       │                                  │
│       ▼                                  │
│  AbstractRuntimeBackend                  │
│       │                                  │
│       ├──────────────────────────┐       │
│       │                          │       │
│  IFrameRuntimeBackend    WorkerRuntimeBackend
│       │                          │       │
│       │ Comlink              Comlink     │
│       │ windowEndpoint         wrap(worker)
│       │                          │       │
│  ┌────┴─────┐              ┌─────┴────┐  │
│  │ 隐藏     │              │ Web      │  │
│  │ <iframe> │              │ Worker   │  │
│  │          │              │          │  │
│  │ 执行环境  │              │ 执行环境  │  │
│  └──────────┘              └──────────┘  │
└──────────────────────────────────────────┘
```

## IRuntimeBackend 接口

所有后端实现统一接口：

```typescript
interface IRuntimeBackend {
  readonly ready: Promise<void>;
  dispose(): void;
  execute(code: string, executionCount: number, parentMessageId?: string): Promise<IExecuteReply>;
  complete(code: string, cursorPos: number): Promise<ICompleteReply>;
  inspect(code: string, cursorPos: number, detailLevel: number): Promise<IInspectReply>;
  isComplete(code: string): Promise<IIsCompleteReply>;
  handleCommOpen(commId, targetName, data, buffers?, parentMessageId?): Promise<void>;
  handleCommMsg(commId, data, buffers?, parentMessageId?): Promise<void>;
  handleCommClose(commId, data, buffers?, parentMessageId?): Promise<void>;
}
```

## AbstractRuntimeBackend

抽象基类封装了 Comlink 代理逻辑，子类只需设置 `_remote` 和调用 `_ready.resolve()`/`_ready.reject()`：

```typescript
abstract class AbstractRuntimeBackend implements IRuntimeBackend {
  get ready(): Promise<void> { return this._ready.promise; }

  async execute(code, executionCount, parentMessageId?) {
    await this.ready;
    return this._getRemote().execute(code, executionCount, parentMessageId);
  }

  // complete/inspect/isComplete/handleComm* 方法结构相同
  // 全部 await this.ready 后委托给 _remote

  private _getRemote(): Comlink.Remote<IRemoteRuntimeApi> {
    if (!this._remote) {
      throw new Error(`${this._runtimeLabel} runtime is not initialized`);
    }
    return this._remote;
  }
}
```

所有远程方法调用前都先 `await this.ready`，确保后端初始化完成。

## IFrameRuntimeBackend

### 初始化流程

```
构造函数
  ├─► 创建隐藏 <div> 容器（display:none，添加到 document.body）
  ├─► 创建 <iframe>，srcdoc 为最简 HTML 文档
  ├─► 等待 iframe onload（10秒超时）
  ├─► 获取 iframe.contentWindow 作为 globalScope
  ├─► 创建 JavaScriptExecutor（或使用自定义 executorFactory）
  ├─► 建立 Comlink 双向通道：
  │   ├─► 主窗口 expose API（供 iframe 调用）
  │   └─► 主窗口 wrap iframe endpoint（调用 iframe）
  ├─► 创建 outputProxy（Comlink.proxy 包装输出回调）
  ├─► remote.initialize({ baseUrl }, outputProxy)（10秒超时）
  ├─► 调用 onReady(ctx) 回调
  └─► _ready.resolve()
```

### iframe 文档内容

iframe 使用 `srcdoc` 创建空文档，不加载任何外部资源：

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>JavaScript Kernel</title>
</head>
<body></body>
</html>
```

### Comlink 通道建立

IFrame 模式使用 `Comlink.windowEndpoint` 在两个 window 之间建立通信：

```typescript
// 主窗口暴露 API 给 iframe
const exposedEndpoint = Comlink.windowEndpoint(window, iframe.contentWindow, '*');
Comlink.expose(createRemoteRuntimeApi(globalScope, executor), exposedEndpoint);

// 主窗口获取 iframe 端的代理
const endpoint = Comlink.windowEndpoint(iframe.contentWindow, window, '*');
const remote = Comlink.wrap<IRemoteRuntimeApi>(endpoint);
```

### IFrame IReadyContext

IFrame 后端就绪后提供更丰富的上下文：

```typescript
interface IReadyContext {
  iframe: HTMLIFrameElement;          // iframe DOM 元素
  container: HTMLDivElement;          // 隐藏容器
  globalScope: Record<string, any>;   // iframe 的 window 对象
  executor: JavaScriptExecutor;       // 执行器实例
  execute: (code, executionCount?) => Promise<IExecuteReply>;
  preloadModule: (moduleName) => Promise<void>;
  registerCommTarget: (targetName, moduleName, exportName?) => Promise<void>;
  unregisterCommTarget: (targetName) => Promise<void>;
}
```

### 资源清理

dispose 时：
1. reject ready Promise（防止后续调用挂起）
2. 调用 `remote.dispose()` 并释放 Comlink proxy（`releaseProxy()`）
3. 移除 iframe 元素
4. 移除 container div
5. 清空所有引用

## WorkerRuntimeBackend

### 初始化流程

```
构造函数
  ├─► 检查 Web Worker 可用性
  ├─► new Worker('./worker-runtime.js', { type: 'module' })
  ├─► 注册 worker.onerror / worker.onmessageerror
  ├─► Comlink.wrap(worker) 获取 remote 代理
  ├─► 创建 outputProxy
  └─► 启动 _init()（异步）

_init()
  ├─► remote.initialize({ baseUrl }, outputProxy)（10秒超时）
  ├─► 调用 onReady(ctx) 回调
  └─► _ready.resolve()
```

### Worker 入口 (worker-runtime.ts)

Worker 端代码极其简洁：

```typescript
import * as Comlink from 'comlink';
import { createRemoteRuntimeApi } from './runtime_remote';

const runtimeGlobal = self as unknown as Record<string, any>;
Comlink.expose(createRemoteRuntimeApi(runtimeGlobal));
```

Worker 的 `self` 作为 globalScope，通过 Comlink.expose 暴露远程 API。

### Worker IReadyContext

Worker 后端的上下文不暴露 DOM 相关对象：

```typescript
interface IReadyContext {
  execute: (code, executionCount?) => Promise<IExecuteReply>;
  preloadModule: (moduleName) => Promise<void>;
  registerCommTarget: (targetName, moduleName, exportName?) => Promise<void>;
  unregisterCommTarget: (targetName) => Promise<void>;
}
```

### 资源清理

dispose 时：
1. reject ready Promise
2. 释放 Comlink proxy
3. 调用 `worker.terminate()` 终止 Worker 线程
4. 清空所有引用

## Comlink 远程 API (IRemoteRuntimeApi)

两端通过统一的远程接口通信：

| 方法 | 说明 |
|------|------|
| `initialize(options, onOutput)` | 初始化运行时，设置输出回调 |
| `execute(code, executionCount, parentMessageId?)` | 执行代码 |
| `preloadModule(moduleName)` | 预加载 ES 模块 |
| `registerCommTarget(targetName, moduleName, exportName?)` | 注册 comm 处理器 |
| `unregisterCommTarget(targetName)` | 注销 comm 处理器 |
| `complete(code, cursorPos)` | 代码补全 |
| `inspect(code, cursorPos, detailLevel)` | 对象检查 |
| `isComplete(code)` | 代码完整性检查 |
| `handleCommOpen(commId, targetName, data, buffers?, parentMessageId?)` | 处理 comm 打开 |
| `handleCommMsg(commId, data, buffers?, parentMessageId?)` | 处理 comm 消息 |
| `handleCommClose(commId, data, buffers?, parentMessageId?)` | 处理 comm 关闭 |
| `dispose()` | 清理运行时 |

## 输出消息类型 (RuntimeOutputMessage)

运行时通过 `onOutput` 回调发送 10 种消息：

| type | 说明 | 对应 Jupyter 消息 |
|------|------|-----------------|
| `stream` | 控制台输出（stdout/stderr） | stream |
| `input_request` | 输入请求 | input_request |
| `display_data` | 富媒体显示 | display_data |
| `update_display_data` | 更新已有显示 | update_display_data |
| `clear_output` | 清除输出 | clear_output |
| `execute_result` | 执行结果 | execute_result |
| `execute_error` | 执行错误 | error |
| `comm_open` | 打开 comm 通道 | comm_open |
| `comm_msg` | comm 消息 | comm_msg |
| `comm_close` | 关闭 comm 通道 | comm_close |

## createRemoteRuntimeApi — 远程 API 工厂

`createRemoteRuntimeApi(globalScope, executor?)` 创建绑定到特定 globalScope 的远程 API 实现：

```typescript
function createRemoteRuntimeApi(globalScope, executor?): IRemoteRuntimeApi {
  let evaluator: JavaScriptRuntimeEvaluator | null = null;

  return {
    async initialize(options, onOutput) {
      evaluator?.dispose();
      evaluator = new JavaScriptRuntimeEvaluator({
        globalScope,
        executor,
        onOutput: message => emitOutput(onOutput, message)
      });
    },

    async execute(code, executionCount, parentMessageId?) {
      return ensureEvaluator().execute(code, executionCount, parentMessageId);
    },
    // ... 其他方法类似，全部委托给 evaluator

    async dispose() {
      evaluator?.dispose();
      evaluator = null;
    }
  };
}
```

### 跨线程安全 (makeCloneSafe)

输出消息通过 Comlink 传输前，使用 `makeCloneSafe` 确保数据可以被结构化克隆：

- 使用 `structuredClone` 尝试克隆
- 失败时递归 sanitize：
  - 基本类型直接返回
  - bigint → 字符串
  - symbol/function → `String(value)`
  - ArrayBuffer 保留
  - Error → `{name, message, stack}`
  - 循环引用 → `'[Circular]'`
  - 深度 > 8 → `'[Truncated]'`
- emitOutput 中 Promise.resolve(callback(...)).catch() 忽略回调失败，确保执行回复不被输出回调故障阻塞

## JavaScriptRuntimeEvaluator — 运行时求值器

Evaluator 是在隔离环境中实际执行代码的组件：

```
JavaScriptRuntimeEvaluator
  ├─► _globalScope    // 执行全局作用域
  ├─► _executor       // JavaScriptExecutor 实例
  ├─► _commManager    // CommManager 实例
  ├─► _setupWidgets()          → createWidgetClasses(commManager)
  ├─► _setupJupyterGlobal()    → globalThis.Jupyter = { comm, widgets }
  ├─► _setupDisplay()          → globalThis.display = display函数
  └─► _setupConsoleOverrides() → 替换 console 方法
```

### Console 重写

| console 方法 | 重定向到 | 说明 |
|-------------|---------|------|
| `log`/`info`/`debug`/`dir`/`trace`/`table` | stdout stream | 参数通过 getMimeBundle 格式化 |
| `error`/`warn` | stderr stream | 同上 |
| `onerror` | stderr stream | 全局错误处理 |

原始 console 方法在 `_originalConsole` 中保存，dispose 时恢复。

### 全局环境注入

| 全局对象 | 内容 | 来源 |
|---------|------|------|
| `display(obj, metadata?)` | 显示函数 | Display 系统 |
| `Jupyter.comm` | CommManager 实例 | Comm 系统 |
| `Jupyter.widgets` | 绑定的 widget 类 | Widget 系统 |
| `console.*` | 重定向的 console | Console 系统 |

## 超时控制

- 两个后端的启动超时均为 **10 秒**（`STARTUP_TIMEOUT_MS = 10000`）
- `withTimeout(promise, timeoutMs, errorMessage)` 为初始化操作添加超时
- 超时后 reject ready Promise，后端进入错误状态

## Base URL 解析

```typescript
function resolveBaseUrl(baseUrl?: string): string {
  if (typeof baseUrl === 'string' && baseUrl.length > 0) return baseUrl;
  try { return PageConfig.getBaseUrl(); }
  catch { return '/'; }
}
```

优先使用传入的 baseUrl，其次从 JupyterLab PageConfig 获取，兜底使用 `'/'`。baseUrl 用于 Magic Imports 的相对路径解析。

## 两种模式对比

| 特性 | IFrame | Web Worker |
|------|--------|-----------|
| 执行环境 | 隐藏 iframe | Dedicated Worker |
| DOM 访问 | ✅（通过 iframe.contentWindow） | ❌ |
| 主线程阻塞 | ⚠️ 同线程，可阻塞 UI | ✅ 独立线程 |
| window.parent | ✅ 可访问主页面 | ❌ |
| globalScope 暴露 | ✅ 可从主线程访问 | ❌ |
| 通信方式 | window.postMessage (Comlink) | Worker.postMessage (Comlink) |
| 启动方式 | srcdoc 创建空 HTML | new Worker('./worker-runtime.js') |
| 销毁方式 | iframe.remove() | worker.terminate() |
| 隔离级别 | 中等（同源 iframe） | 强（线程级隔离） |
| 适用场景 | DOM 操作、可视化 | 计算密集、纯逻辑 |

## 相关文档

- [02-内核架构](02-kernel-architecture.md) — JavaScriptKernel 类如何使用后端
- [03-执行模型](03-execution-model.md) — 代码在 evaluator 中的执行流程
- [06-Comm 协议](06-comm-protocol.md) — Comm 消息跨环境传递
- [05-IFrame DOM 操作](../examples/05-iframe-dom.md) — IFrame 模式访问主页面示例
