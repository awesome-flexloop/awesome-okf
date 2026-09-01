---
type: reference
title: 缓冲 IO 源码参考
description: SharedArrayBuffer 和 Service Worker 两种缓冲 IO 实现的 API 参考
tags:
  - cockle
  - buffered-io
  - sharedarraybuffer
  - service-worker
  - stdin
generated:
  at: "2026-08-22T00:00:00+08:00"
  by: okf-gen
verified:
  at: "2026-08-22T00:00:00+08:00"
  by: source-extract
status: stable
stale_after: "2027-08-22"
sources:
  - id: buffered-io
    resource: /references/buffered-io-source.md
    title: src/buffered_io/
  - id: stdin-context
    resource: /references/buffered-io-source.md
    title: src/context/stdin_context.ts
---

## 概述

Cockle 浏览器 Shell 的缓冲 IO（Buffered IO）系统解决了 Web Worker 与主线程之间的标准输入（stdin）传输问题。由于 Web Worker 无法直接访问 DOM 和终端输入事件，用户键盘输入必须从主线程传递到 Worker。缓冲 IO 提供两种后端实现：SharedArrayBuffer（SAB，基于共享内存的零延迟同步通信）和 Service Worker（SW，基于 fetch 拦截的异步通信）。系统在运行时自动检测可用后端并支持动态切换。

## 双后端架构

缓冲 IO 采用主线程端（Main IO）和 Worker 端（Worker IO）成对设计，每种后端都提供对应的 IMainIO 和 IWorkerIO 实现：

| 后端 | 主线程类 | Worker 类 | 通信机制 | 同步能力 |
|------|---------|----------|---------|---------|
| SharedArrayBuffer | SharedArrayBufferMainIO | SharedArrayBufferWorkerIO | Atomics.wait/notify | 同步 |
| Service Worker | ServiceWorkerMainIO | ServiceWorkerWorkerIO | Service Worker fetch 拦截 | 异步 |

## IMainIO 接口

IMainIO（主线程 IO 接口）定义了主线程端 stdin 管理的契约：

```typescript
interface IMainIO {
  enabled: boolean;
  push(char: number): Promise<void>;
  write(text: string): void;
  enable(): Promise<void>;
  disable(): Promise<void>;
  canEnable(): Promise<boolean>;
  testWithTimeout(ms: number): Promise<boolean>;
  registerSendStdinNow(callback: () => void): void;
  handleStdin?(request: Request): Promise<Response>;
  dispose(): void;
}
```

各成员说明：
- **enabled**：当前后端是否已启用
- **push(char)**：向缓冲区推入单个字符（键盘输入），返回 Promise
- **write(text)**：向缓冲区写入文本字符串
- **enable()**：启用此后端，执行必要的初始化（如创建 SAB、注册 SW）
- **disable()**：禁用此后端，释放资源
- **canEnable()**：检测此后端是否可用（如 SAB 需要 crossOriginIsolated）
- **testWithTimeout(ms)**：在指定超时内测试后端是否正常工作
- **registerSendStdinNow(callback)**：注册"立即发送 stdin"回调，当 Worker 请求输入时通知主线程
- **handleStdin?(request)**：可选方法，Service Worker 后端用于处理 fetch 拦截到的 stdin 请求
- **dispose()**：释放所有资源

## IWorkerIO 接口

IWorkerIO（Worker 端 IO 接口）定义了 Worker 端 stdin 读取的契约，与 [IInput](io-source.md) 兼容：

```typescript
interface IWorkerIO {
  enabled: boolean;
  read(maxChars: number | null): number[];
  readAsync(maxChars: number | null, timeoutMs?: number): Promise<number[]>;
  pollInput(timeoutMs: number): number[];
  write(text: string): void;
  enable(): Promise<void>;
  disable(): Promise<void>;
  canEnable(): Promise<boolean>;
  dispose(): void;
}
```

IWorkerIO 的 `read`、`readAsync`、`pollInput` 方法与 IInput 接口签名一致，可直接作为命令的标准输入源使用。`write` 方法用于 Worker 端向输出通道写入数据。

## SharedArrayBuffer 后端

### SharedArrayBufferMainIO

SharedArrayBufferMainIO 使用 SharedArrayBuffer（共享数组缓冲区）配合 Atomics API 实现主线程与 Worker 之间的零延迟同步通信：

```typescript
class SharedArrayBufferMainIO implements IMainIO {
  // 使用 Atomics.wait/notify 进行线程同步
  // requires: crossOriginIsolated === true
}
```

**工作原理**：
1. 主线程创建 SharedArrayBuffer，与 Worker 共享同一块内存
2. 主线程通过 `push()` 将键盘输入字符写入共享缓冲区
3. Worker 端通过 `Atomics.wait()` 在共享内存上等待输入到达
4. 字符到达后通过 `Atomics.notify()` 唤醒等待的 Worker 线程
5. Worker 直接从共享内存读取字符，无需 postMessage 序列化

**优势**：零延迟同步通信，Worker 端的同步 `read()` 调用可直接阻塞等待输入，完美模拟 POSIX 终端的阻塞读取行为。

**限制**：要求页面处于 `crossOriginIsolated` 环境（需要 COOP/COEP 响应头）。

### SharedArrayBufferWorkerIO

SharedArrayBufferWorkerIO 是 Worker 端的 SAB 实现：

```typescript
class SharedArrayBufferWorkerIO implements IWorkerIO {
  // 通过 Atomics.wait 阻塞读取共享缓冲区
  // 支持同步 read() 方法
}
```

Worker 端在 `read()` 调用中通过 `Atomics.wait()` 实现真正的阻塞读取——当缓冲区为空时，Worker 线程挂起等待直到主线程写入字符并发出 notify 通知。这是唯一支持同步阻塞 stdin 的后端。

## Service Worker 后端

### ServiceWorkerMainIO

ServiceWorkerMainIO 利用 Service Worker 的 fetch 拦截能力实现异步 stdin：

```typescript
class ServiceWorkerMainIO implements IMainIO {
  constructor(browsingContextId: string, baseUrl: string);
  // 通过 Service Worker 拦截特定 URL 的 fetch 请求
  // 当 Worker 调用 readAsync 时，fetch 请求被 SW 拦截
  // SW 将请求转发到主线程，等待键盘输入后响应
}
```

**工作原理**：
1. 主线程注册 Service Worker，拦截特定 URL 模式的 fetch 请求
2. Worker 端需要输入时，发起对约定 URL 的 `fetch()` 调用
3. Service Worker 拦截此请求，将其转发给主线程
4. 主线程等待键盘输入，输入到达后通过 SW 响应 fetch
5. Worker 的 `fetch()` Promise resolve，获得输入数据

**参数要求**：
- **browsingContextId**：浏览上下文 ID，用于在多个 Shell 实例间路由 stdin 请求
- **baseUrl**：Service Worker 注册的基础 URL

**限制**：仅支持异步读取（`readAsync`），同步 `read()` 和 `pollInput()` 无法实现真正的阻塞（需轮询）。不需要 `crossOriginIsolated` 环境，兼容性更好。

### ServiceWorkerWorkerIO

ServiceWorkerWorkerIO 是 Worker 端的 SW 实现：

```typescript
class ServiceWorkerWorkerIO implements IWorkerIO {
  // 通过 fetch() 向 Service Worker 请求输入
  // 仅支持异步 readAsync
}
```

Worker 端通过 `fetch()` 请求等待输入，异步获取字符数据。

## StdinContext 类

StdinContext（标准输入上下文）管理两种后端之间的切换和可用性检测：

```typescript
class StdinContext {
  setAvailable(shortName: string, available: boolean): void;
  setEnabled(shortName: string): Promise<void>;
}
```

- **setAvailable(shortName, available)**：标记指定后端（`'sab'` 或 `'sw'`）是否可用。初始化时依次检测 SAB（检查 crossOriginIsolated）和 SW（检查 Service Worker 注册状态），标记可用状态
- **setEnabled(shortName)**：启用指定后端，同时禁用当前正在使用的后端。通过 IMainIO/IWorkerIO 的 enable/disable 方法协调两端状态

StdinContext 在 BaseShellWorker.initialize() 中创建，持有对主线程 IO 和 Worker IO 的引用，作为 stdin 切换的协调中心。

## 运行时切换

Shell 支持在运行时动态切换 stdin 后端：

### 主线程切换

```typescript
// BaseShell._setMainIO(shortName)
async _setMainIO(shortName: 'sab' | 'sw'): Promise<void> {
  // 禁用当前后端
  await this._mainIO.disable();
  // 启用新后端
  await this._getMainIO(shortName).enable();
  // 通知 Worker 端切换
  await this._worker.enableBufferedStdin(false);
  await this._worker.enableBufferedStdin(true);
}
```

### Worker 端切换

```typescript
// BaseShellWorker._setWorkerIO(shortName)
async _setWorkerIO(shortName: 'sab' | 'sw'): Promise<void> {
  // 类似地禁用旧 IO、启用新 IO
  // 更新 StdinContext 状态
}
```

用户可通过 `cockle-config` 内置命令在运行时切换 stdin 后端，切换过程对正在运行的命令透明。

## Worker 类型与 IO 支持矩阵

不同 Worker 类型支持的 stdin 后端不同：

| Worker 类型 | SAB 同步 stdin | SW 异步 stdin |
|------------|---------------|---------------|
| Coincident | ✅ 支持 | ✅ 支持 |
| Comlink | ❌ 不支持 | ✅ 仅 SW |

- **Coincident Worker**：基于 SharedArrayBuffer 构建，天然支持 SAB 同步 stdin；同时也支持 SW 后端
- **Comlink Worker**：基于 postMessage 构建，无法使用 SAB 同步 stdin，只能使用 Service Worker 异步 stdin

## 降级与错误处理

当两种后端都不可用时（既没有 crossOriginIsolated 环境，也无法注册 Service Worker），Shell 无法获得可靠的 stdin 通道：

```
if (!sabAvailable && !swAvailable) {
  // 两种缓冲 IO 都不可用
  shell.dispose();
  // 显示错误信息：无法初始化标准输入
}
```

Shell 会执行 dispose 清理并显示错误消息，告知用户无法在当前浏览器环境中运行。

## 初始化顺序

缓冲 IO 的完整初始化流程：

1. Shell 创建时根据 `crossOriginIsolated` 决定 Worker 类型（coincident/comlink）
2. 创建 Worker，建立远程连接
3. BaseShellWorker.initialize() 创建 StdinContext
4. 依次检测 SAB 和 SW 的可用性：
   - 调用 `canEnable()` 检测各后端
   - 通过 `setAvailable()` 标记可用状态
5. 选择优先级最高的可用后端（SAB 优先于 SW）
6. 协调主线程和 Worker 端同时启用所选后端：
   - 主线程：`mainIO.enable()`
   - Worker：`workerIO.enable()`
7. `enableBufferedStdin(true)` 确认两端同步
8. stdin 通道就绪，Shell 可以开始读取用户输入

```typescript
// 伪代码：后端选择逻辑
async function selectBestBackend() {
  if (await sabIO.canEnable()) {
    await stdinContext.setEnabled('sab');
    return 'sab';
  }
  if (await swIO.canEnable()) {
    await stdinContext.setEnabled('sw');
    return 'sw';
  }
  throw new Error('No stdin backend available');
}
```

## 相关概念

- [IO 系统源码参考](io-source.md)：IInput/IOutput 基础接口与终端/文件 IO 实现
- [Worker 通信源码参考](worker-source.md)：Coincident/Comlink Worker 类型与 StdinContext 初始化
- [配置与环境源码参考](config-source.md)：cockle-config 命令与 stdin 后端切换
- [内置命令源码参考](builtin-source.md)：cockle-config 命令触发运行时 IO 切换
