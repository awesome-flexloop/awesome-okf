---
type: Reference
title: TypeScript Kernel 源码参考
description: "@jupyterlite/pyodide-kernel npm 包的 TypeScript 源码结构，包括主线程 Kernel、Worker 抽象、Comlink/Coincident 两种 Worker 实现"
tags: [typescript, kernel, worker, comlink, coincident]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: kernel-ts
    resource: /references/kernel-ts-source.md
    title: "packages/pyodide-kernel/src/kernel.ts"
  - id: worker-ts
    resource: /references/kernel-ts-source.md
    title: "packages/pyodide-kernel/src/worker.ts"
  - id: comlink-worker
    resource: /references/kernel-ts-source.md
    title: "packages/pyodide-kernel/src/comlink.worker.ts"
  - id: coincident-worker
    resource: /references/kernel-ts-source.md
    title: "packages/pyodide-kernel/src/coincident.worker.ts"
---

## 源码文件位置

TypeScript 核心包位于 `packages/pyodide-kernel/src/`，源码路径：
`external/libs/jupyter/pyodide-kernel/packages/pyodide-kernel/src/`

## 核心模块清单

| 文件 | 导出 | 说明 |
|------|------|------|
| `index.ts` | 重新导出所有模块 | 包入口 |
| `tokens.ts` | `IPyodideWorkerKernel`、`IComlinkPyodideKernel`、`ICoincidentPyodideWorkerKernel` | 接口定义 |
| `kernel.ts` | `PyodideKernel` | 主线程 Kernel 类 |
| `worker.ts` | `PyodideRemoteKernel` | Worker 抽象基类 |
| `comlink.worker.ts` | `PyodideComlinkKernel` | Comlink（postMessage）Worker 实现 |
| `coincident.worker.ts` | `PyodideCoincidentKernel`、`SharedBufferContentsAPI`、`PyodideDriveFS` | Coincident（SharedArrayBuffer）Worker 实现 |
| `loader.ts` | `importModule()` | 动态 ES module 导入工具 |

## PyodideKernel（主线程）

```typescript
class PyodideKernel extends BaseKernel implements IKernel {
  constructor(options: PyodideKernel.IOptions);
  readonly ready: Promise<void>;

  // Kernel message handlers
  async kernelInfoRequest(): Promise<KernelMessage.IInfoReplyMsg['content']>;
  async executeRequest(content): Promise<KernelMessage.IExecuteReplyMsg['content']>;
  async completeRequest(content): Promise<KernelMessage.ICompleteReplyMsg['content']>;
  async inspectRequest(content): Promise<KernelMessage.IInspectReplyMsg['content']>;
  async isCompleteRequest(content): Promise<KernelMessage.IIsCompleteReplyMsg['content']>;
  async commInfoRequest(content): Promise<KernelMessage.ICommInfoReplyMsg['content']>;
  async commOpen(msg): Promise<void>;
  async commMsg(msg): Promise<void>;
  async commClose(msg): Promise<void>;
  async inputReply(content): Promise<void>;
  dispose(): void;
}
```

初始化流程：
1. `initWorker()` — 根据 `crossOriginIsolated` 选择 Worker 类型
2. `initRemote()` — 初始化远程代理（coincident proxy 或 comlink wrap）
3. `remote.initialize(options)` — 异步初始化 Worker 端

Worker 消息处理（`_processWorkerMessage`）支持的消息类型：
- `stream` — stdout/stderr 输出
- `input_request` — stdin 输入请求
- `display_data` / `update_display_data` — 富媒体显示
- `clear_output` — 清除输出
- `execute_result` / `execute_error` — 执行结果/错误
- `comm_open` / `comm_msg` / `comm_close` — Comm 通信

## PyodideRemoteKernel（Worker 抽象基类）

```typescript
abstract class PyodideRemoteKernel {
  async initialize(options: IPyodideWorkerKernel.IOptions): Promise<void>;
  async execute(content, parent);
  async complete(content, parent);
  async inspect(content, parent);
  async isComplete(content, parent);
  async commInfo(content, parent);
  async commOpen(content, parent);
  async commMsg(content, parent);
  async commClose(content, parent);

  protected abstract sendInputRequest(prompt: string, password: boolean): string | undefined;
  protected async initRuntime(options): Promise<void>;
  protected async initFilesystem(options): Promise<void>;
  protected async initPackageManager(options): Promise<void>;
  protected async initKernel(options): Promise<void>;
  protected async initGlobals(options): Promise<void>;
}
```

initialize 五步流程：
1. `initRuntime` — 动态 import pyodide.mjs，调用 loadPyodide
2. `initFilesystem` — 挂载 DriveFS（条件性）
3. `initPackageManager` — 加载 micropip、安装 piplite、配置 URLs
4. `initKernel` — 加载 ipykernel/comm/pyodide-kernel/jedi/ipython，import pyodide_kernel
5. `initGlobals` — 从 pyodide globals 获取 kernel/streams/interpreter 引用

## IPyodideWorkerKernel.IOptions

```typescript
interface IOptions extends IWorkerKernel.IOptions {
  pyodideUrl: string;              // pyodide.mjs URL
  indexUrl: string;                // pyodide 包索引基础 URL
  pipliteWheelUrl: string;         // piplite wheel URL
  pipliteUrls: string[];           // Warehouse-like 索引 URL 列表
  disablePyPIFallback: boolean;    // 禁用 PyPI 回退
  location: string;                // 初始工作目录
  mountDrive: boolean;             // 是否挂载 Emscripten DriveFS
  browsingContextId?: string;      // Service Worker 浏览上下文 ID
  loadPyodideOptions: {            // loadPyodide 额外选项
    lockFileURL: string;
    packages: string[];
  };
  kernelId?: string;
}
```

## 两种 Worker 实现对比

| 特性 | PyodideComlinkKernel | PyodideCoincidentKernel |
|------|---------------------|------------------------|
| 通信机制 | Comlink (postMessage) | coincident (SharedArrayBuffer + Atomics) |
| 文件系统 | DriveFS 通过 postMessage | SharedBufferContentsAPI 同步调用 |
| stdin 实现 | 同步 XMLHttpRequest → Service Worker | 同步 processStdinRequest → Atomics.wait |
| 启用条件 | !crossOriginIsolated | crossOriginIsolated |

## 相关概念

- [架构总览](/concepts/02-architecture-overview.md)
- [Worker 通信模式](/concepts/03-worker-communication.md)
- [消息桥接机制](/concepts/07-message-bridge.md)
