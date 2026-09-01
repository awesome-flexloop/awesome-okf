---
type: reference
title: Worker 通信源码参考
description: BaseShellWorker、ComlinkShellWorker、CoincidentShellWorker 及 Worker 入口文件 API 参考
tags:
  - cockle
  - worker
  - comlink
  - coincident
generated:
  at: "2026-08-22T00:00:00+08:00"
  by: okf-gen
verified:
  at: "2026-08-22T00:00:00+08:00"
  by: source-extract
status: stable
stale_after: "2027-08-22"
sources:
  - id: worker-base
    resource: /references/worker-source.md
    title: src/base_shell_worker.ts
  - id: worker-comlink
    resource: /references/worker-source.md
    title: src/comlink_shell_worker.ts
  - id: worker-coincident
    resource: /references/worker-source.md
    title: src/coincident_shell_worker.ts
---

## 概述

Cockle 浏览器 Shell 将命令执行逻辑放置在 Web Worker（工作线程）中运行，以避免阻塞浏览器主线程 UI。Worker 通信层提供两种实现：Coincident（基于 SharedArrayBuffer 直接属性赋值的同步通信）和 Comlink（基于 postMessage 的异步 RPC）。BaseShellWorker（Worker 基类）封装了 Shell 初始化、IO 协调、外部命令桥接等公共逻辑，两种 Worker 子类仅在通信机制和 DriveFS 初始化上有所差异。

## BaseShellWorker 抽象基类

BaseShellWorker 是所有 Worker 端 Shell 的抽象基类，实现 IShellWorker 接口。

### initialize 方法

```typescript
async initialize(options: IShellOptions): Promise<void>
```

初始化流程：
1. 创建 StdinContext（标准输入上下文），管理 SAB/SW 两种 stdin 后端的切换
2. 创建 WorkerIO（Worker 端 IO），根据可用性选择 SharedArrayBuffer 或 Service Worker 后端
3. 创建 ShellImpl（Shell 实现）实例，传入文件系统、环境变量、命令注册表等依赖

### 公共方法

| 方法 | 说明 |
|------|------|
| `input(char: number)` | 向 Shell 输入单个字符（用于终端键盘输入） |
| `start()` | 启动 Shell 主循环，开始读取并执行命令 |
| `setSize(size: {rows: number, cols: number})` | 设置终端窗口大小，更新 LINES/COLUMNS 环境变量 |
| `exitCode(): number` | 获取 Shell 退出码 |
| `exitExternalCommand(result: IExternalCommandResult)` | 通知外部命令执行完成，传入结果 |
| `externalInput(maxChars: number \| null): Promise<number[]>` | 外部命令请求输入（跨线程回调到主线程） |
| `externalOutput(text: string, isStderr: boolean): void` | 外部命令输出文本（跨线程回调到主线程） |
| `externalSetTermios(flags: TermiosFlags): void` | 外部命令设置终端属性 |
| `themeChange(isDark?: boolean): void` | 主题切换通知，更新 COCKLE_DARK_MODE 环境变量 |
| `registerCallbacks(callbacks: IWorkerCallbacks): void` | 注册主线程回调函数 |

### enableBufferedStdin 方法

```typescript
async enableBufferedStdin(enable: boolean): Promise<void>
```

协调主线程和 Worker 端 IO 的启用/禁用状态，确保两端同步切换缓冲 stdin 后端。当启用时，stdin 通过共享缓冲通道传输；禁用时回退到 postMessage 方式。

## ComlinkShellWorker

ComlinkShellWorker 继承自 BaseShellWorker，使用 Comlink 库实现主线程与 Worker 之间的异步 RPC（远程过程调用）通信。

```typescript
class ComlinkShellWorker extends BaseShellWorker {
  // initDriveFS 是空操作（no-op）
  // 通过 Comlink.expose 暴露给主线程
}
```

- **initDriveFS()**：空操作方法，Comlink 模式下不需要特殊的 DriveFS 初始化
- **暴露方式**：通过 `Comlink.expose(workerInstance)` 将 Worker 实例的方法暴露给主线程，主线程通过 `Comlink.wrap(worker)` 获取代理对象

Comlink 模式基于 `postMessage` 异步通信，所有方法调用都返回 Promise，不要求 `crossOriginIsolated` 环境。

## CoincidentShellWorker

CoincidentShellWorker 继承自 BaseShellWorker，使用 Coincident 库实现基于 SharedArrayBuffer 的同步/混合通信。

```typescript
class CoincidentShellWorker extends BaseShellWorker implements IShellWorker {
  initProxy(): void;
  // 将所有方法绑定到 proxy 对象
}
```

- **initProxy()**：将所有 Worker 方法直接绑定到 `proxy` 对象上，主线程通过直接访问 `worker.proxy` 的属性调用方法
- **同步能力**：利用 SharedArrayBuffer 和 Atomics 实现零延迟同步调用，支持 SAB 模式的同步 stdin

Coincident 模式要求页面处于 `crossOriginIsolated` 环境（即需要 Cross-Origin-Opener-Policy 和 Cross-Origin-Embedder-Policy 头）。

## Worker 接口类型

### IComlinkShellWorker

```typescript
type IComlinkShellWorker = Remote<IShellWorker>;
```

Comlink 包装后的 Worker 类型，所有方法返回 Promise（由 Comlink 的 `Remote` 类型自动包装）。

### ICoincidentShellWorker

```typescript
interface ICoincidentShellWorker extends IShellWorker, IWorkerCallbacks {
  // 同时继承 Worker 接口和回调接口
  // 通过直接属性赋值实现双向通信
}
```

Coincident Worker 同时实现 Worker 接口（主线程调用 Worker）和回调接口（Worker 调用主线程），通过直接在 `proxy` 对象上赋值回调函数实现双向通信，无需 Comlink 的 wrap/proxy 包装。

## Worker 选择与初始化

### 自动检测 workerType

```typescript
// Shell.initWorker 中根据 crossOriginIsolated 自动选择
const workerType = globalThis.crossOriginIsolated ? 'coincident' : 'comlink';
```

Worker 类型根据全局 `crossOriginIsolated` 属性自动检测：
- **crossOriginIsolated === true**：使用 `coincident.worker.js`，支持 SharedArrayBuffer 同步通信
- **crossOriginIsolated === false**：使用 `comlink.worker.js`，回退到 postMessage 异步通信

### Worker 入口文件

**coincident.worker.ts**：
```typescript
// 创建 CoincidentShellWorker 实例并通过 coincident 暴露
const worker = new CoincidentShellWorker();
worker.initProxy();
// coincident 负责将 worker.proxy 暴露给主线程
```

**comlink.worker.ts**：
```typescript
// 创建 ComlinkShellWorker 实例并通过 Comlink.expose 暴露
const worker = new ComlinkShellWorker();
Comlink.expose(worker);
```

## 远程连接建立

BaseShell.createRemote（主线程端）使用两种不同模式建立与 Worker 的连接：

### Coincident 模式（直接回调赋值）

```typescript
// Coincident: 直接在 worker.proxy 上赋值回调函数
worker.proxy.callbacks = {
  output: (text, isStderr) => { /* 处理输出 */ },
  // ... 其他回调
};
await worker.proxy.initialize(options);
```

回调函数直接赋值到 Worker 的 `proxy` 对象上，Coincident 库通过 SharedArrayBuffer 同步机制使 Worker 端可直接访问这些函数。

### Comlink 模式（wrap + registerCallbacks）

```typescript
// Comlink: 使用 wrap 创建代理，通过 registerCallbacks 注册
const remote = Comlink.wrap<IShellWorker>(worker);
await remote.registerCallbacks(
  Comlink.proxy(callbackObj.output),
  Comlink.proxy(callbackObj.externalInput),
  // ... 其他回调用 Comlink.proxy 包装
);
await remote.initialize(options);
```

Comlink 模式下，回调函数需要用 `Comlink.proxy()` 包装后才能传递到 Worker 端，`registerCallbacks` 方法在 Worker 端接收这些回调代理。

## 通信模式对比

| 特性 | Coincident | Comlink |
|------|-----------|---------|
| 通信机制 | SharedArrayBuffer + Atomics | postMessage |
| 同步调用 | 支持 | 不支持（全部异步） |
| SAB stdin | 支持 | 不支持（仅 SW） |
| crossOriginIsolated | 必须 | 不需要 |
| 回调传递 | 直接赋值 proxy 属性 | Comlink.proxy() 包装 |
| 方法暴露 | worker.initProxy() | Comlink.expose() |
| 主线程获取 | worker.proxy | Comlink.wrap(worker) |

## 初始化序列

完整的 Shell Worker 初始化序列：

```typescript
// 1. 主线程创建 Worker
const worker = new Worker(workerUrl);

// 2. 建立远程连接（coincident 或 comlink 模式）
const remote = createRemote(worker, workerType);

// 3. 注册主线程回调
await remote.registerCallbacks(callbacks);

// 4. 初始化 Worker（创建 ShellImpl、IO、命令注册表）
await remote.initialize(options);

// 5. 启动 Shell 主循环
await remote.start();

// 6. 进入交互循环：用户输入 → remote.input(char) → Worker 执行
```

## 相关概念

- [缓冲 IO 源码参考](buffered-io-source.md)：SAB/SW 两种 stdin 后端与 Worker 的配合
- [命令系统源码参考](command-source.md)：ShellImpl 中的命令注册表与执行逻辑
- [IO 系统源码参考](io-source.md)：Worker 端 IO 与主线程终端的桥接
- [配置与环境源码参考](config-source.md)：终端属性（Termios）跨线程同步
