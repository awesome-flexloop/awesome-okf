---
type: Concept
title: 内核架构
description: JavaScriptKernel 类的设计、IRuntimeBackend 接口、后端创建和请求处理流程
tags: [kernel, architecture, backend, basekernel, lifecycle]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: jk-kernel
    title: kernel.ts
  - id: jk-startup
    title: startup.ts
---

# 内核架构

JavaScript Kernel 的核心是 `JavaScriptKernel` 类，它继承 JupyterLite 的 `BaseKernel`，通过可插拔的运行时后端（`IRuntimeBackend`）在隔离环境中执行代码。

## 类层次结构

```
BaseKernel (@jupyterlite/services)
    └── JavaScriptKernel (@jupyterlite/javascript-kernel)
            ├── _runtimeMode: 'iframe' | 'worker'
            ├── _backend: IRuntimeBackend
            ├── _executorFactory?: (scope) => JavaScriptExecutor
            └── _startupExtensions: IStartupExtension[]
```

## JavaScriptKernel 构造

```typescript
class JavaScriptKernel extends BaseKernel implements IKernel {
  constructor(options: JavaScriptKernel.IOptions) {
    super(options);
    this._runtimeMode = options.runtime ?? 'iframe';
    this._executorFactory = options.executorFactory;
    this._startupExtensions = [...(options.startupExtensions ?? [])];
    this._backend = this.createBackend(this._runtimeMode);
  }
}
```

`IOptions` 接口包含：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `id` | `string` | 必填 | 内核 ID |
| `name` | `string` | 必填 | 内核名称 |
| `sendMessage` | `function` | 必填 | 消息发送回调 |
| `runtime` | `'iframe' \| 'worker'` | `'iframe'` | 运行时模式 |
| `executorFactory` | `(scope) => JavaScriptExecutor` | `undefined` | 自定义执行器工厂 |
| `startupExtensions` | `IStartupExtension[]` | `[]` | 启动扩展列表 |

## 请求处理流程

所有 Jupyter 协议请求都遵循统一模式：先 `await this.ready`，再委托给后端。

```
用户执行单元格
    │
    ▼
executeRequest(content)
    │
    ├─► await this.ready  (等待后端初始化)
    │
    ├─► this._backend.execute(code, executionCount, parentMsgId)
    │       │
    │       ▼
    │   Comlink 远程调用 (postMessage)
    │       │
    │       ▼
    │   JavaScriptRuntimeEvaluator.execute()
    │       │
    │       ├─► makeAsyncFromCode(code)  → AST 转换
    │       ├─► asyncFunction.call(globalScope)  → 执行
    │       └─► getMimeBundle(result)  → 格式化输出
    │
    └─► 返回执行结果 / 捕获错误
```

### 各请求处理器

| 方法 | Jupyter 请求 | 委托方法 | 异常降级 |
|------|-------------|---------|---------|
| `executeRequest()` | execute_request | `_backend.execute()` | 返回错误状态，publishExecuteError |
| `completeRequest()` | complete_request | `_backend.complete()` | 返回空 matches |
| `inspectRequest()` | inspect_request | `_backend.inspect()` | 返回 found=false |
| `isCompleteRequest()` | is_complete_request | `_backend.isComplete()` | 返回 status='unknown' |
| `kernelInfoRequest()` | kernel_info_request | 直接返回 | — |

### kernelInfoReply 内容

| 字段 | 值 |
|------|-----|
| `implementation` | `'JavaScript'` |
| `implementation_version` | `'0.1.0'` |
| `language_info.name` | `'javascript'` |
| `language_info.file_extension` | `'.js'` |
| `language_info.mimetype` | `'text/javascript'` |
| `language_info.codemirror_mode` | `{ name: 'javascript' }` |
| `language_info.version` | `'es2017'` |
| `protocol_version` | `'5.3'` |
| `banner` | `'A JavaScript kernel running in the browser (IFrame/Web Worker)'` |

## 后端创建

`createBackend(mode)` 方法根据 runtime 模式创建对应后端：

```typescript
protected createBackend(mode: RuntimeMode): IRuntimeBackend {
  switch (mode) {
    case 'iframe':
      return new IFrameRuntimeBackend({
        onOutput: (msg) => this._handleOutputMessage(msg),
        baseUrl: this.baseUrl,
        executorFactory: this._executorFactory,
        onReady: (ctx) => this._handleRuntimeReady(ctx)
      });
    case 'worker':
      return new WorkerRuntimeBackend({
        onOutput: (msg) => this._handleOutputMessage(msg),
        baseUrl: this.baseUrl,
        onReady: (ctx) => this._handleRuntimeReady(ctx)
      });
  }
}
```

## 启动扩展生命周期

1. 内核创建时保存 `startupExtensions` 列表
2. 后端 `ready` 后，遍历 extensions 调用 `applyStartupExtension()`
3. `activate(context)` 在运行时上下文中执行（预加载模块、注册 comm target）
4. 扩展被 dispose 时调用 `deactivate(context)` 清理

```typescript
interface IStartupExtension {
  id: string;
  activate: (context: IRuntimeReadyContext) => Promise<void> | void;
  deactivate?: (context: IRuntimeReadyContext) => Promise<void> | void;
}
```

### Startup Extension 注册

前端扩展通过 Lumino Token 注入注册表：

```typescript
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'my-extension:startup',
  autoStart: true,
  requires: [IJavaScriptKernelStartupRegistry],
  activate: (app, startup) => {
    startup.registerStartupExtension({
      id: 'my-extension:bootstrap',
      activate: async (context) => {
        await context.preloadModule('https://cdn.example.com/my-module.js');
      }
    });
  }
};
```

注册返回 `IDisposable`，dispose 时自动调用 deactivate。

## 就绪上下文 (IReadyContext)

后端初始化完成后，`onReady` 回调接收上下文对象：

| 属性/方法 | IFrame | Worker | 说明 |
|----------|--------|--------|------|
| `iframe` | ✅ | ❌ | iframe 元素引用 |
| `container` | ✅ | ❌ | 隐藏容器 div |
| `globalScope` | ✅ | ❌ | iframe 的 window 对象 |
| `executor` | ✅ | ❌ | JavaScriptExecutor 实例 |
| `execute()` | ✅ | ✅ | 直接执行代码 |
| `preloadModule()` | ✅ | ✅ | 预加载 ES 模块 |
| `registerCommTarget()` | ✅ | ✅ | 注册 comm 处理器 |
| `unregisterCommTarget()` | ✅ | ✅ | 注销 comm 处理器 |

> **注意**：Worker 模式的 IReadyContext 不暴露 globalScope 和 executor——Worker 线程的全局作用域无法从主线程直接访问。

## 内核生命周期

```
构造函数
  ├─► super(options)          // BaseKernel 初始化
  ├─► 设置 _runtimeMode
  ├─► 设置 _executorFactory
  ├─► 设置 _startupExtensions
  └─► createBackend()         // 创建后端（开始异步初始化）
       │
       ▼
  后端 _init() 异步执行
  ├─► IFrame: 创建 iframe/container，建立 Comlink 通道
  ├─► Worker: 创建 Worker，建立 Comlink 通道
  ├─► remote.initialize()    // 初始化远程 evaluator
  └─► onReady(ctx)           // 触发就绪回调
       │
       ▼
  ready Promise resolve
  ├─► 应用 startup extensions
  └─► 开始处理用户请求
       │
       ▼
  dispose()
  ├─► _comms.clear()
  ├─► _backend.dispose()     // 释放 Comlink proxy，销毁 iframe/terminate worker
  └─► super.dispose()
```

## 错误处理

- **后端初始化失败**：ready Promise reject，所有请求降级处理
- **执行错误**：通过 `normalizeError()` 处理跨 realm Error 对象，publishExecuteError 通知前端
- **补全/检查错误**：静默降级，返回空结果而不是抛出异常
- **Comlink 通信错误**：后端 dispose 时释放 proxy，防止内存泄漏

## 相关文档

- [04-运行时后端](04-runtime-backends.md) — IFrame/Worker 后端实现细节
- [03-执行模型](03-execution-model.md) — 代码执行和 AST 转换
- [08-启动扩展](08-startup-extensions.md) — 插件集成机制
