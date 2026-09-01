---
type: concept
title: 07 - 缓冲 IO 系统
description: SharedArrayBuffer 零延迟同步 stdin 与 Service Worker 异步 stdin 的原理、配置和切换
tags: [buffered-io, stdin, sharedarraybuffer, service-worker, atomics, sab, sw]
generated:
  by: "agent:source-code-to-okf-wiki"
  at: "2026-08-22T00:00:00+08:00"
verified:
  by: "process:seven-concepts-v"
  at: "2026-08-22T00:00:00+08:00"
status: stable
stale_after: "2027-08-22"
sources:
  - id: buffered-io-source
    resource: /references/buffered-io-source.md
    title: 缓冲IO参考
---

# 缓冲 IO 系统

缓冲 IO（Buffered IO）是 Cockle（浏览器Shell）实现 WASM（WebAssembly）命令同步标准输入（stdin）读取的核心机制。浏览器主线程是单线程的，无法直接阻塞等待用户输入，但 WASM 编译的 Unix 工具（如 `cat`、`vim`、`nano`）期望 `read()` 系统调用能同步阻塞直到有数据可用。Cockle 提供两种解决方案：SharedArrayBuffer（共享数组缓冲区）零延迟同步模式和 Service Worker（服务工作线程）异步阻塞模式。

## 为什么需要缓冲 stdin

传统 Unix shell 中，当程序调用 `read(0, buf, size)` 从标准输入读取数据时：

1. 如果有数据可用，立即返回读取的字节数
2. 如果没有数据，**阻塞**当前线程直到用户输入并按回车
3. 返回读取的数据

但在浏览器环境中：

- **主线程不能阻塞**：阻塞主线程会导致 UI 冻结，浏览器甚至会杀死无响应的页面
- **Worker 线程可以阻塞**：Web Worker 运行在独立线程，阻塞不会影响 UI
- **WASM 需要同步语义**：Emscripten 编译的程序期望 `read()` 是同步阻塞的

Cockle 的解决方案是将 Shell 运行在 Web Worker 中，通过缓冲 IO 机制实现 Worker 内的同步阻塞读取：

```
┌─────────────────┐         ┌──────────────────┐
│   主线程 (UI)   │         │  Worker (Shell)  │
│                 │         │                  │
│  用户输入 ──────┼────────►│  WASM read()     │
│                 │  缓冲通道 │    ↓ 阻塞等待    │
│  渲染输出 ◄─────┼─────────┤  Atomics.wait /  │
│                 │         │  fetch 拦截      │
└─────────────────┘         └──────────────────┘
```

两种模式的核心区别在于"阻塞等待"的实现方式：SAB 使用 Atomics 等待，SW 使用 Service Worker 拦截同步 XHR。

## SAB 同步 stdin

SAB（SharedArrayBuffer）模式使用共享内存和原子操作实现**零延迟**的同步 stdin，是性能最优的方案。

### 工作原理

SharedArrayBuffer 是一块可以在主线程和 Worker 之间共享的内存区域。配合 Atomics API，可以实现跨线程的同步等待：

```
主线程                          Worker (SAB IO)
   │                               │
   │                               │ 调用 read()
   │                               │ Atomics.wait(int32Array, 0, 0)
   │                               │ ◄── 线程在此阻塞
   │                               │
   │ 用户输入数据                   │
   │ 写入 SAB 数据区               │
   │ Atomics.store(int32Array,0,1) │
   │ Atomics.notify(int32Array,0)  │
   │ ─────────────────────────────►│
   │                               │ 被唤醒
   │                               │ 从 SAB 读取数据
   │                               │ 返回数据给 WASM
```

### SAB 数据结构

Cockle 使用的 SAB 布局大致如下：

```
SharedArrayBuffer 布局：
┌─────────────────────────────────────────┐
│ Offset 0: int32 状态标志                  │
│   0 = 无数据（Worker等待）                │
│   1 = 有数据（主线程写入）                │
│   2 = 流结束                             │
├─────────────────────────────────────────┤
│ Offset 4: int32 数据长度                 │
├─────────────────────────────────────────┤
│ Offset 8: 数据缓冲区（可配置大小）         │
└─────────────────────────────────────────┘
```

### 代码实现要点

`SharedArrayBufferMainIO` 和 `SharedArrayBufferWorkerIO` 是一对实现：

```typescript
// Worker 端：SharedArrayBufferWorkerIO.read()
async read(): Promise<string> {
  const int32 = new Int32Array(this._sab);
  // 阻塞等待，直到状态变为非0
  Atomics.wait(int32, 0, 0);
  // 被唤醒后读取状态
  const status = Atomics.load(int32, 0);
  if (status === 2) {
    return '';  // EOF
  }
  // 读取数据长度
  const length = Atomics.load(int32, 1);
  // 读取数据
  const bytes = new Uint8Array(this._sab, 8, length);
  const decoder = new TextDecoder();
  const data = decoder.decode(bytes);
  // 重置状态为0
  Atomics.store(int32, 0, 0);
  return data;
}

// 主线程端：SharedArrayBufferMainIO.push()
push(data: string): void {
  const int32 = new Int32Array(this._sab);
  // 等待Worker消费完上一批数据
  while (Atomics.load(int32, 0) !== 0) {
    // 自旋等待（数据量小，不会长时间阻塞）
  }
  // 编码数据
  const encoder = new TextEncoder();
  const bytes = encoder.encode(data);
  // 写入数据长度
  Atomics.store(int32, 1, bytes.length);
  // 写入数据
  const buffer = new Uint8Array(this._sab, 8, bytes.length);
  buffer.set(bytes);
  // 设置状态为"有数据"并唤醒Worker
  Atomics.store(int32, 0, 1);
  Atomics.notify(int32, 0);
}
```

### crossOriginIsolated 要求

SAB 模式要求页面处于**跨域隔离**（cross-origin isolated）状态，需要服务器发送以下 HTTP 头：

```http
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp
```

当 `crossOriginIsolated === true` 时，浏览器才允许创建 SharedArrayBuffer。如果这两个头没有正确设置，SAB 将不可用，Cockle 会自动降级到 Service Worker 模式。

## Service Worker 异步 stdin

当 SAB 不可用时（未配置跨域隔离头），Cockle 使用 Service Worker 模式实现同步 stdin 阻塞。

### 工作原理

Service Worker 可以拦截页面发起的 fetch 请求。Worker 端利用同步 XHR（XMLHttpRequest）发起请求，Service Worker 拦截该请求后不立即响应，而是等到主线程有输入数据时才返回响应：

```
主线程                  Service Worker              Worker (Shell)
   │                         │                          │
   │                         │                          │ 调用 read()
   │                         │                          │ 发起同步 XHR
   │                         │                          │ GET /__cockle_stdin__
   │                         │                          │ ◄── XHR 阻塞等待响应
   │                         │                          │
   │                         │ 拦截 fetch 事件           │
   │                         │ 保存 fetchEvent          │
   │                         │ 等待数据...              │
   │                         │                          │
   │ 用户输入数据             │                          │
   │ postMessage 到 SW ─────►│                          │
   │                         │ 用输入数据响应请求        │
   │                         │ fetchEvent.respondWith() │
   │                         │ ────────────────────────►│
   │                         │                          │ XHR 返回
   │                         │                          │ 获得输入数据
```

### 同步 XHR 阻塞

Worker 中的同步 XHR 会阻塞 Worker 线程，但不会影响主线程：

```typescript
// Worker 端：ServiceWorkerWorkerIO.read()
read(): string {
  const xhr = new XMLHttpRequest();
  // false = 同步请求，会阻塞Worker线程
  xhr.open('GET', '/__cockle_stdin__?id=' + this._shellId, false);
  xhr.send();
  if (xhr.status === 204) {
    return '';  // EOF
  }
  return xhr.responseText;
}
```

注意：Service Worker 模式下 `read()` 是同步方法（直接返回 string，不是 Promise），这是因为同步 XHR 本身就是阻塞的。

### Service Worker 端实现

Service Worker 需要注册并拦截特定路径的请求：

```typescript
// service_worker.ts 核心逻辑
const pendingRequests = new Map<string, FetchEvent>();

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  
  if (url.pathname === '/__cockle_stdin__') {
    const shellId = url.searchParams.get('id');
    // 不立即响应，保存请求等待主线程提供数据
    event.respondWith(new Promise(resolve => {
      pendingRequests.set(shellId, { event, resolve });
    }));
    return;
  }
  
  // 其他请求正常处理
});

// 接收主线程消息，提供stdin数据
self.addEventListener('message', (event) => {
  if (event.data.type === 'stdin-data') {
    const { shellId, data } = event.data;
    const pending = pendingRequests.get(shellId);
    if (pending) {
      pending.resolve(new Response(data, {
        status: 200,
        headers: { 'Content-Type': 'text/plain' }
      }));
      pendingRequests.delete(shellId);
    }
  }
});
```

### 不需要 crossOriginIsolated

Service Worker 模式**不需要**跨域隔离头，但需要：

1. 注册 Service Worker（`navigator.serviceWorker.register()`）
2. Service Worker 与页面同源
3. 页面通过 HTTPS 或 localhost 访问（Service Worker 安全限制）

## IMainIO / IWorkerIO 接口

两种 IO 模式实现统一的接口，使得上层代码可以透明切换。

### IMainIO（主线程端接口）

```typescript
interface IMainIO {
  // 启用IO（注册事件监听器等）
  enable(): void;
  
  // 禁用IO（清理资源）
  disable(): void;
  
  // 向Worker推送输入数据
  write(data: string): void;
  
  // 检查此IO模式是否可用
  canEnable(): boolean;
  
  // 推送输入到缓冲区（用于缓冲模式）
  push(data: string): void;
  
  // 轮询输入（从缓冲区取数据）
  pollInput(): string | null;
}
```

### IWorkerIO（Worker端接口）

```typescript
interface IWorkerIO {
  // 启用IO
  enable(): void;
  
  // 禁用IO
  disable(): void;
  
  // 读取数据（SAB模式返回Promise，SW模式同步返回）
  read(): string | Promise<string>;
  
  // 向输出写入数据（传递到主线程）
  write(data: string): void;
}
```

两种模式都实现了这两个接口，`BaseShell` 通过 `_setMainIO` 和 `_setWorkerIO` 方法在运行时切换具体实现。

## stdin 自动检测

Cockle 初始化时（`BaseShell._initialize` 方法）会自动检测可用的 stdin 后端：

```typescript
// _initialize 中的检测逻辑（简化）
private async _initialize(): Promise<void> {
  // 1. 检测SAB是否可用
  const sabAvailable = typeof SharedArrayBuffer !== 'undefined' && crossOriginIsolated;
  
  // 2. 检测Service Worker是否可用
  let swAvailable = false;
  if ('serviceWorker' in navigator) {
    const registration = await navigator.serviceWorker.getRegistration();
    swAvailable = !!registration;
  }
  
  // 3. SAB优先（性能更好）
  if (sabAvailable) {
    await this._initSABIO();
  } else if (swAvailable) {
    await this._initServiceWorkerIO();
  } else {
    // 两者都不可用，报错
    throw new Error(
      'Cockle requires either crossOriginIsolated (for SAB) or ' +
      'Service Worker registration for stdin support. ' +
      'Please set COOP/COEP headers or register a Service Worker.'
    );
  }
}
```

检测优先级：
1. **SAB 优先**：当 `crossOriginIsolated === true` 时优先使用 SAB，因为它零延迟、不依赖 Service Worker
2. **SW 降级**：SAB 不可用时使用 Service Worker 模式
3. **报错**：两者都不可用时抛出错误，Shell 无法启动

### COOP/COEP 头配置

要启用 SAB 模式，服务器需要配置以下响应头：

```nginx
# Nginx 配置示例
add_header Cross-Origin-Opener-Policy "same-origin" always;
add_header Cross-Origin-Embedder-Policy "require-corp" always;
```

```apache
# Apache .htaccess 配置
Header set Cross-Origin-Opener-Policy "same-origin"
Header set Cross-Origin-Embedder-Policy "require-corp"
```

如果无法配置这些头，请使用 Service Worker 模式。

## 运行时切换

Cockle 支持在运行时动态切换 stdin 后端，通过 `cockle-config` 命令或 Shell API 触发。

### cockle-config stdin 命令

```bash
# 检查当前stdin后端
cockle-config stdin
# 输出: sab 或 sw

# 切换到SAB模式
cockle-config stdin sab

# 切换到Service Worker模式
cockle-config stdin sw
```

### _setMainIO / _setWorkerIO

切换流程通过 `_setMainIO` 和 `_setWorkerIO` 方法实现：

```typescript
private _setMainIO(io: IMainIO): void {
  // 1. 先禁用旧IO
  if (this._mainIO) {
    this._mainIO.disable();
  }
  // 2. 设置新IO
  this._mainIO = io;
  // 3. 启用新IO
  if (this._stdinEnabled) {
    this._mainIO.enable();
  }
}
```

切换步骤：
1. 调用旧 IO 的 `disable()` 方法，清理事件监听器、释放资源
2. 设置新的 IO 实例
3. 如果 stdin 当前是启用状态，调用新 IO 的 `enable()` 方法

注意：切换过程中如果有正在等待输入的命令，可能会导致异常。建议在命令提示符下（没有命令运行时）切换 stdin 后端。

## StdinContext 管理

`StdinContext` 类负责协调主线程和 Worker 的 IO 启用顺序，确保两边的 IO 实例正确配对。

### 状态管理

```typescript
class StdinContext {
  private _available: boolean = false;
  private _enabled: boolean = false;
  
  // 设置IO是否可用（由后端可用性决定）
  setAvailable(available: boolean): void {
    this._available = available;
    this._updateState();
  }
  
  // 设置用户是否启用了stdin
  setEnabled(enabled: boolean): void {
    this._enabled = enabled;
    this._updateState();
  }
  
  private _updateState(): void {
    if (this._available && this._enabled) {
      this._mainIO.enable();
      this._notifyWorkerEnable();
    } else {
      this._mainIO.disable();
      this._notifyWorkerDisable();
    }
  }
}
```

### 启用顺序

当缓冲模式开启时（WASM命令执行期间），IO 的启用需要遵循特定顺序：

1. 主线程创建 IMainIO 实例并准备接收数据
2. 通知 Worker 端创建对应的 IWorkerIO 实例
3. Worker 端启用 IWorkerIO，开始接收 read() 调用
4. 主线程启用 IMainIO，开始转发用户输入

`StdinContext` 确保这个顺序正确执行，避免数据丢失或死锁。

## buffered stdin 模式

在命令执行期间，Cockle 会自动启用缓冲 stdin 模式，减少跨线程通信次数。

### 缓冲原理

当用户快速输入时（比如粘贴一大段文本），每个字符都通过 postMessage 或 Atomics.notify 传递会造成不必要的开销。缓冲模式将输入先存入主线程的缓冲区：

```typescript
class MainIOWithBuffer implements IMainIO {
  private _buffer: string[] = [];
  private _workerWaiting: boolean = false;
  
  push(data: string): void {
    if (this._workerWaiting) {
      // Worker正在等待，直接发送
      this._sendToWorker(data);
      this._workerWaiting = false;
    } else {
      // Worker没有在等待，先存入缓冲区
      this._buffer.push(data);
    }
  }
  
  pollInput(): string | null {
    if (this._buffer.length > 0) {
      return this._buffer.shift()!;
    }
    this._workerWaiting = true;
    return null;
  }
}
```

### 自动启用时机

缓冲 stdin 在以下时机自动启用：

1. **WASM 命令执行前**：自动调用 `enableBufferedStdin()`
2. **外部命令执行前**：同样启用缓冲模式
3. **内置命令执行时**：默认不启用（内置命令通常不需要交互输入）

命令执行完毕后自动禁用缓冲模式，回到行编辑模式。

### 与行编辑器的交互

在命令提示符状态下，输入由 xterm.js 的行编辑器处理（支持方向键、历史、Tab补全等），此时 stdin 是"禁用"状态（不直接传递到 Shell）。当用户按回车执行命令后：

1. 行编辑器将整行命令传给 Shell 解析
2. 如果命令需要交互输入，缓冲 stdin 启用
3. 后续按键直接通过缓冲 IO 传递给运行中的命令
4. 命令结束后，缓冲 stdin 禁用，回到行编辑模式

## 相关概念

- [05 - IO 系统](05-io-system.md)：基础 IO 抽象、终端 IO、管道
- [06 - 文件系统](06-filesystem.md)：FileInput/FileOutput 的实现
- [11 - Worker 通信机制](11-worker-communication.md)：Comlink/Coincident 与 IO 的关系
- [10 - WASM 与 JavaScript 命令](10-wasm-js-commands.md)：WASM命令为何需要同步stdin
- [09 - 外部命令](09-external-commands.md)：外部命令的IO环境
- [缓冲IO参考](../references/buffered-io-source.md)：IMainIO/IWorkerIO 完整接口定义
