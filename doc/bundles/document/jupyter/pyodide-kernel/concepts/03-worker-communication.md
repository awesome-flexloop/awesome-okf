---
type: Concept
title: Worker 通信模式
description: Comlink（postMessage）与 Coincident（SharedArrayBuffer）两种 Worker 通信模式的工作原理、差异和选择策略
tags: [worker, comlink, coincident, sharedarraybuffer, crossoriginisolated, communication]
prerequisites: ["02-architecture-overview"]
objectives: ["理解两种 Worker 通信模式的工作原理", "掌握 crossOriginIsolated 的影响", "理解文件系统和 stdin 在两种模式下的差异"]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: kernel-ts
    resource: /references/kernel-ts-source.md
    title: kernel.ts
  - id: comlink-worker
    resource: /references/kernel-ts-source.md
    title: comlink.worker.ts
  - id: coincident-worker
    resource: /references/kernel-ts-source.md
    title: coincident.worker.ts
---

# Worker 通信模式

## 为什么需要两种通信模式

Web Worker 的标准通信方式是 `postMessage`，但它有一个根本限制：所有消息都是异步的。Python 代码中 `input()` 是同步调用——代码会阻塞等待用户输入。在 `postMessage` 模式下无法实现真正的同步等待。

SharedArrayBuffer + Atomics 提供了共享内存和同步等待能力，使主线程和 Worker 之间可以同步通信。但 SharedArrayBuffer 要求跨源隔离（crossOriginIsolated），需要特殊的 HTTP 头支持，并非所有部署环境都满足。

pyodide-kernel 根据运行环境自动选择两种模式之一。

## 自动选择机制

在 `PyodideKernel.initWorker()` 中（F-050/F-051）：

```typescript
async initWorker(): Promise<Worker> {
  let worker: Worker;
  if (crossOriginIsolated) {
    // 跨源隔离模式：使用 Coincident（SharedArrayBuffer）
    worker = new Worker(new URL('./coincident.worker.js', import.meta.url), { type: 'module' });
    this._remoteKernel = coincident(worker) as IPyodideWorkerKernel;
  } else {
    // 非跨源隔离模式：使用 Comlink（postMessage）
    worker = new Worker(new URL('./comlink.worker.js', import.meta.url), { type: 'module' });
    this._remoteKernel = Comlink.wrap(worker) as IPyodideWorkerKernel;
  }
  return worker;
}
```

`crossOriginIsolated` 是浏览器全局属性，当且仅当页面同时发送以下 HTTP 头时为 `true`：

```
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp
```

## Comlink 模式详解

### 工作原理

Comlink 是一个基于 `postMessage` 的 RPC 库，它将 Worker 端的对象代理到主线程，使得跨线程调用看起来像普通函数调用。

```
主线程 (PyodideKernel)                    Worker (PyodideComlinkKernel)
     │                                            │
     │  Comlink.wrap(worker)                      │
     │  → 创建 Proxy 对象                          │
     │                                            │
     │  remote.execute(content) ──postMessage──→ │
     │  (消息被序列化为 JSON)                      │  kernel.execute(content)
     │                                            │  → PyodideKernel.run(code)
     │                                            │  → publish_stream_callback
     │  ←──────postMessage─────────────────────  │
     │  (响应/回调消息)                            │
```

### stdin 实现

在 Comlink 模式下，`input()` 需要同步获取用户输入，但 postMessage 是异步的。解决方案是使用**同步 XMLHttpRequest**（F-073）：

```typescript
// comlink.worker.ts
function stdin() {
  // 使用同步 XHR 向 Service Worker 发送请求
  // Service Worker 将请求转发到主线程
  // 同步 XHR 会阻塞 Worker 线程直到收到响应
  const xhr = new XMLHttpRequest();
  xhr.open('POST', '/stdin', false); // false = 同步
  xhr.send(JSON.stringify({ prompt, password }));
  return xhr.responseText;
}
```

这要求部署时注册 Service Worker 来处理 `/stdin` 请求。Service Worker 收到请求后，通过 `postMessage` 通知主线程显示输入框，然后等待主线程的响应，最后通过 `respondWith()` 返回给 Worker。

### 文件系统

Comlink 模式下，Pyodide 使用 Emscripten 默认的 MEMFS（内存文件系统）：
- 所有文件操作都在内存中
- 刷新页面后数据丢失
- 无法与主线程同步文件
- F-078 注释说明：Firefox 隐私模式下即使尝试挂载 DriveFS，文件系统也不会同步

## Coincident 模式详解

### 工作原理

Coincident 使用 `SharedArrayBuffer` 在主线程和 Worker 之间共享内存，配合 `Atomics.wait()` / `Atomics.notify()` 实现同步等待：

```
主线程 (PyodideKernel)                    Worker (PyodideCoincidentKernel)
     │                                            │
     │  coincident(worker)                         │
     │  → 基于 SharedArrayBuffer 创建代理          │
     │                                            │
     │  ┌─── SharedArrayBuffer (共享内存) ───┐     │
     │  │  请求/响应数据直接在共享内存中交换  │     │
     │  └────────────────────────────────────┘     │
     │                                            │
     │  remote.execute(content) ──直接调用──→     │
     │  (通过 SharedArrayBuffer + Atomics)         │  kernel.execute(content)
     │                                            │
     │  stdin 时:                                  │
     │  Atomics.wait(lock) ←─ Atomics.notify ─── │
     │  (Worker 阻塞等待)    (主线程写入后唤醒)     │
```

### stdin 实现

Coincident 模式下，stdin 通过 `SharedBufferContentsAPI` 实现真正的同步调用（F-075）：

```typescript
// coincident.worker.ts
class SharedBufferContentsAPI implements ContentsAPI {
  // 同步文件操作：通过 SharedArrayBuffer 直接调用主线程的 Contents API
  get(path: string, options?: any): Contents.IModel { ... }
  save(path: string, model: Partial<Contents.IModel>): void { ... }
  // ...
}

// stdin 回调直接通过 coincident 的同步代理调用主线程方法
const stdin = () => {
  return this.sendInputRequest(prompt, password);
  // sendInputRequest 在 coincident 模式下是同步的
  // 内部使用 Atomics.wait 等待主线程响应
};
```

### 文件系统

Coincident 模式下通过 `PyodideDriveFS` 类将 Emscripten 的文件系统与主线程的 Jupyter Contents API 同步（F-076）：

```typescript
class PyodideDriveFS {
  constructor(contentsAPI: SharedBufferContentsAPI, mountPoint: string) {
    // 挂载 Emscripten IDBFS 或 MEMFS
    // 通过 SharedBufferContentsAPI 与主线程 Contents API 同步
  }

  async syncfs(populate: boolean): Promise<void> {
    // populate=true: 从主线程拉取文件到 WASM
    // populate=false: 将 WASM 文件推送到主线程
  }
}
```

这意味着：
- Notebook 中创建的文件可以在 Jupyter 文件浏览器中看到
- 文件在刷新后仍然保留（如果使用了 IDBFS）
- 支持跨标签页/会话的文件持久化

## 两种模式对比

| 特性 | Comlink 模式 | Coincident 模式 |
|------|-------------|----------------|
| **启用条件** | `!crossOriginIsolated` | `crossOriginIsolated` |
| **通信机制** | postMessage（JSON 序列化） | SharedArrayBuffer + Atomics |
| **性能** | 每次调用有序列化开销 | 直接共享内存，开销更小 |
| **stdin** | 同步 XMLHttpRequest → Service Worker | Atomics.wait 同步等待 |
| **文件系统** | MEMFS（内存，刷新丢失） | DriveFS（与主线程同步） |
| **Service Worker** | 需要（处理 stdin XHR） | 不需要 |
| **HTTP 头要求** | 无 | COOP + COEP |
| **浏览器兼容性** | 所有现代浏览器 | 需要 SAB 支持（现代浏览器均支持） |
| **Firefox 隐私模式** | 文件系统不同步 | 不受影响 |
| **部署复杂度** | 低 | 高（需要配置 HTTP 头） |

## 部署建议

### 何时需要 Coincident 模式？

1. 需要文件持久化（保存 .py 文件、数据文件等）
2. 需要频繁的 stdin 交互（input()、getpass()）
3. 对性能有较高要求（大量数据传递）

### 如何启用 crossOriginIsolated？

根据部署平台不同：

**静态文件服务器（Node.js/http-server 等）**：需要使用反向代理（如 nginx）添加响应头：

```nginx
add_header Cross-Origin-Opener-Policy same-origin;
add_header Cross-Origin-Embedder-Policy require-corp;
```

**GitHub Pages**：目前不支持自定义 HTTP 头，无法启用 Coincident 模式。

**Vercel/Netlify**：在配置文件中添加 headers：

```json
// vercel.json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "Cross-Origin-Opener-Policy", "value": "same-origin" },
        { "key": "Cross-Origin-Embedder-Policy", "value": "require-corp" }
      ]
    }
  ]
}
```

## 跨模式兼容性

kernel 的设计确保两种模式对外暴露相同的 `IPyodideWorkerKernel` 接口：

```typescript
interface IPyodideWorkerKernel {
  initialize(options: IOptions): Promise<void>;
  execute(content, parent): Promise<object>;
  complete(content, parent): Promise<object>;
  inspect(content, parent): Promise<object>;
  isComplete(content, parent): Promise<object>;
  commInfo(content, parent): Promise<object>;
  commOpen(content, parent): Promise<void>;
  commMsg(content, parent): Promise<void>;
  commClose(content, parent): Promise<void>;
}
```

主线程代码无需关心使用的是哪种模式——消息类型和处理逻辑完全一致。两种模式的差异完全封装在 Worker 端实现和代理层。

## 下一步

- [消息桥接机制](07-message-bridge.md) — Python↔JS 的回调机制
- [Python 兼容性层](06-python-compatibility.md) — IPython 在 WASM 中的适配
- [架构总览](02-architecture-overview.md) — 返回架构总览

## 源码参考

- [TypeScript Kernel 源码](../references/kernel-ts-source.md)
