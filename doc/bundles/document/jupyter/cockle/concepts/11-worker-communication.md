---
type: concept
title: 11 - Worker 通信机制
description: Comlink 和 Coincident 两种 Worker 通信模式的原理、区别、选择策略和回调注册机制
tags: [worker, comlink, coincident, rpc, cross-origin, worker-thread]
generated:
  by: "agent:source-code-to-okf-wiki"
  at: "2026-08-22T00:00:00+08:00"
verified:
  by: "process:seven-concepts-v"
  at: "2026-08-22T00:00:00+08:00"
status: stable
stale_after: "2027-08-22"
sources:
  - id: worker-source
    resource: /references/worker-source.md
    title: Worker通信参考
---

# Worker 通信机制

Cockle（浏览器Shell）将 Shell 核心运行在 Web Worker（工作线程）中，避免 WASM（WebAssembly）命令阻塞主线程 UI。主线程与 Worker 之间的通信支持两种模式：**Comlink**（兼容性优先）和 **Coincident**（性能优先，支持 SAB 同步 stdin）。两种模式自动选择，对上层 API 透明。

## 为什么需要两种通信模式

浏览器的 Web Worker 通过 `postMessage` 进行消息传递，这种方式天然是**异步**的——所有参数都需要被结构化克隆（structured clone）序列化后传输。但 Cockle 的一些场景需要更紧密的线程协作：

1. **同步 stdin 阻塞**：WASM 命令的 `read()` 需要同步阻塞，需要 SharedArrayBuffer（SAB）支持
2. **回调传递**：外部命令（在主线程执行）需要 Worker 端能回调主线程函数
3. **跨域部署**：某些部署场景下 CORS（跨域资源共享）头配置受限

两种模式的核心差异：

| 特性 | Comlink | Coincident |
|------|---------|------------|
| 通信方式 | postMessage + MessageChannel 序列化 RPC | 共享内存 + 同步 Proxy |
| SAB 同步 stdin | ❌ 不支持（只能用 Service Worker） | ✅ 支持 |
| CORS 头要求 | ❌ 不需要 | ✅ 需要 |
| 端口 | 4500 | 4501 |
| 回调注册 | `wrap(worker).registerCallbacks(proxy(...))` | 直接赋值 `worker.proxy.cb = fn` |
| 性能 | 标准（序列化开销） | 更优（直接共享） |
| 兼容性 | 所有现代浏览器 | 需要 crossOriginIsolated |
| Worker 文件 | `comlink.worker.ts` | `coincident.worker.ts` |

### 自动选择策略

Cockle 根据页面的 `crossOriginIsolated` 状态自动选择通信模式：

```
页面加载
  │
  ├─ crossOriginIsolated === true？
  │   ├─ 是 → 使用 Coincident 模式（端口4501）
  │   │        → 支持 SAB 零延迟同步 stdin
  │   │        → 需要 COOP/COEP CORS 头
  │   │
  │   └─ 否 → 使用 Comlink 模式（端口4500）
  │            → Service Worker stdin
  │            → 不需要特殊 CORS 头
  │
  └─ 两者都无法初始化 → 抛出错误
```

`useCoincidentWorker()` 函数封装了这个检测逻辑：

```typescript
function useCoincidentWorker(): boolean {
  // crossOriginIsolated 表示页面发送了正确的COOP/COEP头
  // 此时 SharedArrayBuffer 可用，Coincident 可以发挥全部性能
  return typeof crossOriginIsolated !== 'undefined' && crossOriginIsolated;
}
```

## Comlink 模式

Comlink 是 Google 开发的一个库，通过 ES6 Proxy 封装 postMessage，提供类似本地函数调用的 RPC（远程过程调用）体验。Cockle 在非跨域隔离环境下使用 Comlink。

### 工作原理

Comlink 在主线程和 Worker 两端各创建一个 Proxy 对象：

```
主线程                           Worker
  │                                │
  │  const worker =                 │
  │    wrap(worker)                 │  Comlink.expose(workerImpl)
  │                                │
  │  await worker.initialize(...)   │
  │  ──── postMessage ────────────► │
  │       {type: "initialize", ...} │
  │                                │ 执行 initialize(...)
  │  ◄─── postMessage ───────────── │
  │       {type: "response", ...}   │
  │                                │
  │  await worker.input(data)       │
  │  ──── postMessage ────────────► │
  │  ◄────────── 返回结果 ────────── │
```

每次函数调用都会：
1. 将函数名和参数序列化为消息
2. 通过 postMessage 发送
3. 对方接收消息、反序列化、执行
4. 将返回值序列化发回
5. 调用方的 Promise resolve

### 端口与 Worker 创建

Comlink 模式使用专用的 Worker 入口文件 `comlink.worker.ts`，通常在开发服务器端口 4500 上提供：

```typescript
// 主线程创建 Comlink Worker
import { wrap } from 'comlink';

const workerUrl = new URL('./comlink.worker.ts', import.meta.url);
const worker = new Worker(workerUrl, { type: 'module' });

// 用 Comlink 包装 Worker
const shellWorker = wrap<IComlinkShellWorker>(worker);
```

开发环境下，vite/webpack 等打包工具会处理 `.worker.ts` 文件，生产环境则打包为独立的 JS 文件。

### 不需要 CORS 头

Comlink 模式的重要优势是**不需要**配置跨域隔离头：

```http
# 不需要这些头
# Cross-Origin-Opener-Policy: same-origin
# Cross-Origin-Embedder-Policy: require-corp
```

这使得 Cockle 可以在任意静态网页上部署（不需要控制服务器配置）。代价是无法使用 SAB 同步 stdin，只能使用 Service Worker 模式。

### Comlink.wrap 与 registerCallbacks

Comlink 模式下，回调函数的注册需要使用 Comlink 的 `proxy()` 函数包装，因为函数无法直接通过 postMessage 传递：

```typescript
// BaseShell.createRemote 中的 Comlink 回调注册
import { wrap, proxy } from 'comlink';

private _createComlinkRemote(worker: Worker): void {
  const workerProxy = wrap<IComlinkShellWorker>(worker);
  
  // 使用 proxy() 将回调函数标记为可转移
  const callbacks = {
    callback: proxy((data: any) => this._handleCallback(data)),
    stdout: proxy((data: string) => this._handleStdout(data)),
    stderr: proxy((data: string) => this._handleStderr(data)),
    externalOutput: proxy((data: any) => this._handleExternalOutput(data)),
    initDriveFS: proxy(async (info: any) => {
      return await this._initDriveFSCallback(info);
    }),
    callExternalCommand: proxy(async (name: string, context: any) => {
      return await this._callExternalCommand(name, context);
    })
  };
  
  // 注册回调到 Worker
  workerProxy.registerCallbacks(callbacks);
  this._remote = workerProxy;
}
```

关键点：
- `wrap(worker)` 创建 Worker 对象的异步 Proxy
- `proxy(fn)` 将回调函数包装为 Comlink 可识别的远程引用
- `registerCallbacks` 将所有回调一次性传递给 Worker

### IComlinkShellWorker 接口

Comlink Worker 暴露的接口定义在 comlink_shell_worker.ts：

```typescript
interface IComlinkShellWorker {
  initialize(config: ShellConfig): Promise<void>;
  input(data: string): Promise<void>;
  start(): Promise<void>;
  setSize(lines: number, columns: number): Promise<void>;
  setBufferedStdinEnabled(enabled: boolean): Promise<void>;
  getExitCode(): Promise<number>;
  registerCallbacks(callbacks: ICallbacks): void;
}
```

所有方法都是异步的（返回 Promise），因为底层是 postMessage 通信。

## Coincident 模式

Coincident 是一个利用 SharedArrayBuffer 和 Atomics 实现 Worker 与主线程之间**同步**通信的库。在跨域隔离环境下，它能提供更优的性能和同步 stdin 支持。

### 工作原理

Coincident "修补"（patch）了 Worker 的全局构造函数，使得 Worker 可以直接访问主线程的对象，仿佛它们在同一个线程中：

```
主线程                            Worker (Coincident)
  │                                 │
  │ coincident = new Coincident     │
  │ (worker)                        │
  │                                 │
  │ worker.proxy.callback = fn      │ 全局对象被修补
  │        ▲                        │ 可以直接访问worker.proxy
  │        │ 共享内存               │
  │        │                        │
  │                                 │ worker.proxy.callback(data)
  │                                 │ → 直接在主线程执行fn(data)
  │                                 │ （通过SAB+Atomics同步）
```

核心机制：
1. Coincident 在主线程和 Worker 之间建立共享内存通道
2. Worker 端通过 Proxy 拦截对 `worker.proxy` 的属性访问和函数调用
3. 函数调用通过 Atomics 进行同步，不需要序列化/反序列化
4. 主线程执行回调后通过共享内存通知 Worker

### 端口与 Worker 创建

Coincident 模式使用独立的入口文件 `coincident.worker.ts`，开发服务器端口 4501：

```typescript
// 主线程创建 Coincident Worker
import coincident from 'coincident';

const workerUrl = new URL('./coincident.worker.ts', import.meta.url);
const worker = new Worker(workerUrl, { type: 'module' });

// 用 Coincident 包装
const { proxy } = coincident(worker);
```

两个不同端口（4500/4501）的原因是开发服务器需要为不同的 Worker 配置不同的 HTTP 头——Coincident Worker 需要跨域隔离头。

### 需要 CORS 头

Coincident 模式需要页面发送 COOP/COEP 头以启用 `crossOriginIsolated`：

```nginx
# Nginx 配置
add_header Cross-Origin-Opener-Policy "same-origin" always;
add_header Cross-Origin-Embedder-Policy "require-corp" always;

# 对于Worker文件，可能还需要
add_header Cross-Origin-Resource-Policy "cross-origin" always;
```

如果这些头缺失：
- `crossOriginIsolated` 为 `false`
- `SharedArrayBuffer` 构造函数抛出错误
- Coincident 无法初始化

此时 Cockle 会降级到 Comlink 模式。

### 直接 proxy 属性赋值

Coincident 模式下回调注册更直接——直接赋值属性即可：

```typescript
// BaseShell.createRemote 中的 Coincident 回调注册
private _createCoincidentRemote(worker: Worker): void {
  const { proxy } = coincident(worker);
  
  // 直接赋值，不需要proxy()包装
  proxy.callback = (data: any) => this._handleCallback(data);
  proxy.stdout = (data: string) => this._handleStdout(data);
  proxy.stderr = (data: string) => this._handleStderr(data);
  proxy.externalOutput = (data: any) => this._handleExternalOutput(data);
  proxy.initDriveFS = async (info: any) => {
    return await this._initDriveFSCallback(info);
  };
  proxy.callExternalCommand = async (name: string, context: any) => {
    return await this._callExternalCommand(name, context);
  };
  
  this._remote = proxy;
}
```

对比 Comlink 模式：
- **Comlink**：需要 `proxy()` 包装每个回调，通过 `registerCallbacks` 方法注册
- **Coincident**：直接赋值 `proxy.callback = fn`，像操作本地对象一样

### SAB 同步 stdin 支持

Coincident 模式的最大优势是支持 SharedArrayBuffer 同步 stdin。在 Comlink 模式下，Worker 读取 stdin 需要：

```
Worker read() → postMessage请求输入 → 等待消息 → 主线程转发用户输入
```

而 Coincident + SAB 模式下：

```
Worker read() → Atomics.wait(SAB) → 零等待（主线程Atomics.notify时立即唤醒）
```

延迟从毫秒级（postMessage 往返）降低到微秒级（原子操作），用户输入体验更接近原生终端。

### ICoincidentShellWorker 接口

Coincident Worker 暴露的接口定义在 coincident_shell_worker.ts：

```typescript
interface ICoincidentShellWorker {
  initialize(config: ShellConfig): void;
  input(data: string): void;
  start(): void;
  setSize(lines: number, columns: number): void;
  setBufferedStdinEnabled(enabled: boolean): void;
  getExitCode(): number;
  // 回调通过proxy属性赋值，不在接口中声明
}
```

与 Comlink 接口的区别：方法可以是同步的（不返回 Promise），因为底层通过共享内存同步。

## Worker 入口文件

每种模式有独立的 Worker 入口文件，它们在初始化 IO 和代理时有细微差异。

### comlink.worker.ts

Comlink Worker 入口：

```typescript
// comlink.worker.ts
import { expose } from 'comlink';
import { ComlinkShellWorker } from './comlink_shell_worker';

const worker = new ComlinkShellWorker();
expose(worker);
```

它创建 `ComlinkShellWorker` 实例并通过 `Comlink.expose()` 暴露给主线程。

### coincident.worker.ts

Coincident Worker 入口：

```typescript
// coincident.worker.ts
import './coincident-sync/polyfill';  // 修补全局对象
import { CoincidentShellWorker } from './coincident_shell_worker';

const worker = new CoincidentShellWorker();
// Coincident自动处理暴露，通过全局proxy属性
(self as any).worker = worker;
```

注意 Coincident 需要先加载 polyfill 修补全局环境，然后 Worker 实例直接挂到 `self.worker` 上供主线程访问。

### initDriveFS 和 initProxy 差异

`ComlinkShellWorker` 和 `CoincidentShellWorker` 都继承自 `BaseShellWorker`，但在两个方法上有差异：

| 方法 | ComlinkShellWorker | CoincidentShellWorker |
|------|-------------------|----------------------|
| `initDriveFS` | 通过 Comlink 回调调用主线程，异步等待结果 | 通过 proxy 直接调用主线程，同步语义 |
| `initProxy` | 创建 Comlink 专用的消息通道代理 | 创建 SAB + Coincident 代理 |

## BaseShellWorker 公共逻辑

`BaseShellWorker` 是两种模式的公共基类，封装了 Shell 初始化、IO 协调、命令执行等核心逻辑。

### initialize 方法

```typescript
abstract class BaseShellWorker {
  protected _shell: ShellImpl | null = null;
  protected _mainIO: IWorkerIO | null = null;
  protected _stdinContext: StdinContext;
  
  async initialize(config: ShellConfig): Promise<void> {
    // 1. 创建缓冲IO
    this._mainIO = this._createWorkerIO(config);
    
    // 2. 创建ShellImpl实例
    this._shell = new ShellImpl({
      ...config,
      mainIO: this._mainIO,
      // 回调由子类提供
    });
    
    // 3. 初始化文件系统
    await this._shell.init();
    
    // 4. 初始化WASM包
    await this._shell.initWasmPackages();
  }
  
  protected abstract _createWorkerIO(config: ShellConfig): IWorkerIO;
  protected abstract _createCallback(): IShellCallback;
}
```

### 公共方法

两种模式都提供以下公共方法（签名可能因模式而异——Comlink 返回 Promise，Coincident 可以同步）：

```typescript
class BaseShellWorker {
  // 发送用户输入到Shell
  input(data: string): void {
    this._mainIO?.write(data);
  }
  
  // 启动Shell（开始解析和执行命令）
  start(): void {
    this._shell?.start();
  }
  
  // 设置终端大小（触发SIGWINCH）
  setSize(lines: number, columns: number): void {
    this._shell?.setSize(lines, columns);
  }
  
  // 启用/禁用缓冲stdin
  setBufferedStdinEnabled(enabled: boolean): void {
    this._stdinContext.setEnabled(enabled);
  }
  
  // 获取退出码
  getExitCode(): number {
    return this._shell?.exitCode ?? 0;
  }
}
```

### enableBufferedStdin 协调

缓冲 stdin 的启用需要主线程和 Worker 协调顺序：

```typescript
class BaseShellWorker {
  async setBufferedStdinEnabled(enabled: boolean): Promise<void> {
    if (enabled) {
      // 启用顺序：先Worker，后主线程（避免数据丢失）
      this._stdinContext.setAvailable(true);
      this._stdinContext.setEnabled(true);
      await this._notifyMainEnable();
    } else {
      // 禁用顺序：先主线程，后Worker（避免Worker等待永远不会来的数据）
      await this._notifyMainDisable();
      this._stdinContext.setEnabled(false);
      this._stdinContext.setAvailable(false);
    }
  }
}
```

这个顺序很重要：
- **启用时**：Worker 先准备好接收数据，再让主线程开始发送
- **禁用时**：主线程先停止发送，再让 Worker 退出等待

## 回调注册机制对比

回调是主线程向 Worker 提供的服务（如 stdout 输出、外部命令调用、DriveFS 初始化等）。两种模式注册回调的方式截然不同。

### 回调接口

Worker 需要的回调在 `IShellCallback` 接口中定义：

```typescript
interface IShellCallback {
  // 标准输出
  stdout(data: string): void;
  // 标准错误
  stderr(data: string): void;
  // 外部输出（非文本数据）
  externalOutput(data: any): void;
  // 通用回调
  callback(data: any): void;
  // 初始化DriveFS（在主线程挂载PROXYFS）
  initDriveFS(info: {
    fileSystem: any;
    mountpoint: string;
    baseUrl: string;
    browsingContextId: string;
  }): Promise<void>;
  // 调用外部命令（在主线程执行）
  callExternalCommand(
    name: string,
    context: IExternalCommand.IRunContext
  ): Promise<number>;
}
```

### Comlink 注册流程

```
主线程                                    Comlink Worker
  │                                         │
  │ 1. wrap(worker)                         │
  │    → 创建workerProxy                    │
  │                                         │
  │ 2. 定义回调函数                          │
  │    const cbs = {                        │
  │      stdout: (data) => {...},           │
  │      stderr: (data) => {...},           │
  │      ...                                │
  │    }                                    │
  │                                         │
  │ 3. 用proxy()包装每个回调                 │
  │    cbs.stdout = proxy(cbs.stdout)       │
  │                                         │
  │ 4. workerProxy.registerCallbacks(cbs)   │
  │ ──── postMessage ─────────────────────► │
  │                                         │ 5. 接收回调对象
  │                                         │    保存到this._callbacks
  │                                         │
  │ 6. workerProxy.initialize(config)       │
  │ ──── postMessage ─────────────────────► │
  │                                         │ 7. 执行initialize
  │                                         │    使用this._callbacks
```

关键点：`proxy()` 包装是必须的，因为 Comlink 需要知道哪些参数是函数（需要建立反向消息通道）。没有 `proxy()` 包装，函数会被结构化克隆算法丢弃或报错。

### Coincident 注册流程

```
主线程                                    Coincident Worker
  │                                         │
  │ 1. coincident(worker)                   │
  │    → 获取proxy对象                      │
  │                                         │
  │ 2. 直接赋值回调                          │
  │    proxy.stdout = (data) => {...}       │
  │    proxy.stderr = (data) => {...}       │
  │    proxy.callExternalCommand = ...      │
  │                                         │ 3. Worker启动后通过
  │                                         │    self.proxy访问这些回调
  │                                         │
  │ 4. proxy.initialize(config)             │
  │ ──── SAB同步调用 ──────────────────────► │
  │                                         │ 5. 同步执行initialize
  │                                         │    通过self.proxy.stdout调用回调
```

关键点：Coincident 通过 Proxy 拦截 `proxy.xxx = fn` 的赋值操作，通过共享内存将函数引用同步到 Worker。Worker 端调用 `self.proxy.stdout(data)` 时，Coincident 运行时通过 SAB + Atomics 让主线程执行实际的函数。

### 外部命令调用差异

外部命令调用（`callExternalCommand`）最能体现两种模式的区别：

**Comlink 模式：**
```typescript
// Worker 端
async _callExternalCommand(name: string, ctx: any): Promise<number> {
  // ctx中包含回调（如stdin的data事件），需要Comlink处理
  return await this._callbacks.callExternalCommand(name, ctx);
  // → postMessage到主线程
  // → 主线程执行命令函数
  // → 结果postMessage回来
  // → Promise resolve
}
```

**Coincident 模式：**
```typescript
// Worker 端
_callExternalCommand(name: string, ctx: any): number {
  // ctx是普通对象，回调是通过SAB同步调用的
  return this._callbacks.callExternalCommand(name, ctx);
  // → 通过SAB触发主线程执行
  // → Atomics.wait等待结果
  // → 结果直接返回（看起来是同步的）
}
```

Coincident 版本看起来是同步调用（直接返回 number），底层利用 Atomics 等待实现阻塞语义。

## 跨 origin 部署

在不同的部署场景下，需要根据服务器配置能力选择合适的模式。

### 场景1：完全控制服务器（推荐 Coincident）

如果可以配置 HTTP 响应头，推荐使用 Coincident + SAB 模式获得最佳性能：

```nginx
# nginx.conf
server {
    listen 443 ssl;
    server_name cockle.example.com;
    
    # 跨域隔离头
    add_header Cross-Origin-Opener-Policy "same-origin" always;
    add_header Cross-Origin-Embedder-Policy "require-corp" always;
    
    # 静态文件
    location / {
        root /var/www/cockle;
        try_files $uri $uri/ /index.html;
    }
    
    # Coincident Worker 在端口4501（开发）或单独路径（生产）
    location /coincident.worker.js {
        add_header Cross-Origin-Resource-Policy "cross-origin" always;
    }
}
```

### 场景2：无法配置 CORS 头（使用 Comlink）

如果在静态托管平台（如 GitHub Pages、无服务器配置的 CDN）上部署，无法设置 COOP/COEP 头，则自动降级到 Comlink 模式：

```javascript
// 不需要任何特殊配置
const shell = new CockleShell({
  // ... 基础配置
  // serviceWorker必须注册
});
```

确保：
1. 注册 Service Worker（用于 stdin）
2. 页面通过 HTTPS 或 localhost 访问（Service Worker 安全限制）

### 场景3：混合部署

可以在不同页面使用不同模式：

```
/app/advanced     → 配置了CORS头 → Coincident + SAB stdin
/app/basic        → 无CORS头      → Comlink + Service Worker stdin
```

`cockle-config worker` 命令可以在运行时查看当前模式：

```bash
cockle-config worker
# 输出: coincident 或 comlink
```

### CORS 头验证

部署后可以在浏览器控制台验证 crossOriginIsolated 状态：

```javascript
// 浏览器开发者工具Console
console.log(crossOriginIsolated);  // true = Coincident可用
console.log(typeof SharedArrayBuffer);  // "function" = SAB可用
```

如果 `crossOriginIsolated` 为 `false`，检查：
1. COOP 头是否精确为 `same-origin`（不是 `same-origin-allow-popups`）
2. COEP 头是否为 `require-corp`
3. 所有 iframe 和 Worker 资源也发送了正确的 CORS 头
4. 没有非跨域隔离的第三方资源（可以用 `credentialless` 放宽限制）

### Service Worker 注册

无论哪种模式，如果需要 stdin 支持（Comlink 必须，Coincident 可选），都需要注册 Service Worker：

```typescript
// 在主线程注册Service Worker
if ('serviceWorker' in navigator) {
  const registration = await navigator.serviceWorker.register(
    '/cockle-service-worker.js',
    { scope: '/' }
  );
  await navigator.serviceWorker.ready;
}

// 然后创建Shell
const shell = new CockleShell({
  serviceWorkerRegistration: registration,
  // ...
});
```

Coincident 模式下如果 SAB 可用，Service Worker 仅作为备用 stdin 后端。

## 相关概念

- [07 - 缓冲 IO 系统](07-buffered-io.md)：SAB 和 Service Worker stdin 的实现细节
- [09 - 外部命令](09-external-commands.md)：外部命令如何通过回调桥接执行
- [06 - 文件系统](06-filesystem.md)：DriveFS 初始化回调如何跨线程工作
- [02 - 架构总览](02-architecture-overview.md)：主线程/Worker分层架构
- [Shell API 参考](../references/shell-api.md)：Shell 构造函数完整选项
- [Worker通信参考](../references/worker-source.md)：IComlinkShellWorker/ICoincidentShellWorker完整接口
