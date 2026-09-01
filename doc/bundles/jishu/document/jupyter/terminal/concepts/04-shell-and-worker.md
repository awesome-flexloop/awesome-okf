---
type: Concept
title: Shell与Worker机制
description: TerminalShell的创建、双Worker通信模式（Coincident/Comlink）、WASM加载和DriveFS挂载机制
tags: [shell, worker, wasm, coincident, comlink, sharedarraybuffer, service-worker, drivefs]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: shell-source
    resource: /references/shell-source.md
    title: Shell与Worker源码信源
  - id: client-source
    resource: /references/client-source.md
    title: LiteTerminalAPIClient API信源
---

# Shell与Worker机制

TerminalShell 是每个终端会话的核心对象，它负责在Web Worker中初始化cockle WASM shell，并通过mock-socket WebSocket与xterm.js前端通信。

## TerminalShell类层级

```
cockle/BaseShell (来自@jupyterlite/cockle)
    ↑ extends
TerminalShell (本包)
```

TerminalShell继承自cockle的BaseShell，重写了两个关键方法：
- `initWorker()`：选择加载coincident或comlink Worker
- `createRemote()`：为coincident模式注册DriveFS请求回调

## Shell创建流程

当调用`LiteTerminalAPIClient.startNew()`时：

```typescript
// 1. 创建shell（mountpoint='/drive'挂载JupyterLite文件系统）
const shell = await this.createShell({ mountpoint: '/drive', ... });

// 2. 设置输出回调：将shell stdout通过WebSocket发送给前端
shell.outputCallback = (text: string) => {
  socket?.send(JSON.stringify(['stdout', text]));
};

// 3. 建立WebSocket hook
const hook = socketFactory.on('connection', (socket) => {
  shell.socket = socket as WebSocketClient;
  
  socket.on('message', async (data) => {
    const msg = JSON.parse(data.toString());
    switch (msg[0]) {
      case 'stdin': await shell.input(msg[1]); break;
      case 'set_size': shell.setSize(msg[1], msg[2]); break;
    }
  });
  
  socket.send(JSON.stringify(['setup', {}]));  // xterm.js握手
  await shell.start();
});

// 4. 创建mock WebSocket服务器
const wsUrl = baseUrl.replace(/^http/, 'ws');
new WebSocketServer(`${wsUrl}/terminals/websocket/${name}`);
```

对于无头shell（`createHeadlessShell()`），跳过WebSocket步骤，直接设置outputCallback并调用shell.start()。

## Worker初始化

TerminalShell.initWorker()根据`this.workerType`选择Worker：

```typescript
protected override initWorker(options: ITerminalShell.IOptions): Worker {
  if (this.workerType === 'coincident') {
    return new Worker(new URL('./coincident.worker.js', import.meta.url), { type: 'module' });
  }
  // 默认comlink
  return new Worker(new URL('./comlink.worker.js', import.meta.url), { type: 'module' });
}
```

`workerType`由cockle BaseShell在构造时自动检测：
- 浏览器支持SharedArrayBuffer且页面设置了COOP/COEP头 → `'coincident'`
- 否则 → `'comlink'`

## Coincident模式（SAB同步通信）

### 工作原理

Coincident库利用SharedArrayBuffer（SAB）和Atomics API实现主线程与Worker之间的**同步**函数调用：

```
主线程                         Worker线程
   │                              │
   │  proxy.method(args)          │
   │  ──────► Atomics.postMessage │
   │         Atomics.wait (阻塞)   │
   │                              │ 执行方法
   │                              │ 通过SAB写入结果
   │  Atomics.notify ◄──────       │
   │  从SAB读取结果                │
   │  ◄───── 返回值               │
```

从Worker代码的视角，`proxy.processDriveRequest(data)`看起来是一个普通的同步函数调用——但实际上它通过SAB同步调用了主线程的方法。

### coincident.worker.ts 关键实现

```typescript
// 1. 自定义ContentsAPI：通过coincident proxy同步调用主线程
class SharedBufferContentsAPI extends ContentsAPI {
  request<T extends TDriveMethod>(data: TDriveRequest<T>): TDriveResponse<T> {
    return proxy.processDriveRequest(data) as TDriveResponse<T>;
  }
}

// 2. 自定义DriveFS：使用SharedBufferContentsAPI
class SharedArrayBufferFS extends DriveFS {
  createAPI(options: DriveFS.IOptions): ContentsAPI {
    return new SharedBufferContentsAPI(options);
  }
}

// 3. TerminalShell Worker子类
class CoincidentTerminalShellWorker extends CoincidentShellWorker {
  protected override initDriveFS(options: IDriveFSOptions): void {
    if (mountpoint && baseUrl) {
      const driveFS = new SharedArrayBufferFS({ FS, PATH, ERRNO_CODES, baseUrl, driveName: '', mountpoint });
      FS.mount(driveFS, {}, mountpoint);
    }
  }

  override initProxy(proxy: ICoincidentTerminalShellWorker): void {
    super.initProxy(proxy);
    worker.processDriveRequest = proxy.processDriveRequest.bind(proxy);
  }
}

// 4. 顶层初始化（top-level await）
export const proxy = (await coincident()).proxy as ICoincidentTerminalShellWorker;
export const worker = new CoincidentTerminalShellWorker();
worker.initProxy(proxy);
```

### 主线程侧回调注册

在TerminalShell.createRemote()中：

```typescript
if (this.workerType === 'coincident') {
  const remote = super.createRemote(options) as ICoincidentTerminalShellWorker;
  remote.processDriveRequest = async <T extends TDriveMethod>(data: TDriveRequest<T>) => {
    if (!this._contentsProcessor) {
      this._contentsProcessor = new DriveContentsProcessor({
        contentsManager: this._contentsManager
      });
    }
    return this._contentsProcessor.processDriveRequest(data);
  };
  return remote;
}
```

Worker中的`proxy.processDriveRequest(data)`通过SAB同步调用主线程的这个async函数。注意虽然主线程侧函数是async，但coincident会等待Promise resolve后再返回结果给Worker。

## Comlink模式（Service Worker异步通信）

### 工作原理

Comlink库基于postMessage实现RPC（远程过程调用）。在comlink模式下，DriveFS的请求通过Service Worker中转：

```
主线程                    Service Worker               Worker线程
   │                           │                           │
   │  registerStdinHandler     │                           │
   │  ('terminal', handler)    │                           │
   │  ──────────────────────►  │                           │
   │                           │  DriveFS.request()        │
   │                           │  postMessage(browsingCtxId)│
   │                           │  ◄───────────────────────  │
   │  handleStdin(data)        │                           │
   │  ◄──────────────────────  │                           │
   │  ContentsManager操作      │                           │
   │  ──────────────────────►  │                           │
   │                           │  postMessage(result)       │
   │                           │  ──────────────────────►  │
```

### comlink.worker.ts 关键实现

```typescript
class ComlinkTerminalShellWorker extends ComlinkShellWorker {
  protected override initDriveFS(options: IDriveFSOptions): void {
    if (mountpoint && baseUrl && browsingContextId) {
      const driveFS = new DriveFS({
        FS, PATH, ERRNO_CODES,
        baseUrl,
        driveName: '',
        mountpoint,
        browsingContextId  // 关键：用于SW路由
      });
      FS.mount(driveFS, {}, mountpoint);
    }
  }
}

const worker = new ComlinkTerminalShellWorker();
expose(worker);  // comlink.expose()将worker暴露给主线程
```

### 主线程侧StdinHandler注册

在terminalServiceWorkerPlugin中：

```typescript
if (serviceWorkerManager) {
  liteTerminalAPIClient.browsingContextId = serviceWorkerManager.browsingContextId;
  serviceWorkerManager.registerStdinHandler(
    'terminal',
    liteTerminalAPIClient.handleStdin.bind(liteTerminalAPIClient)
  );
}
```

`handleStdin`委托给模块级单例`Private.shellManager`（cockle的ShellManager），它根据shellId将stdin请求路由到正确的shell实例。

## 两种模式对比

| 维度 | Coincident (SAB) | Comlink (SW) |
|------|------------------|--------------|
| 通信原语 | SharedArrayBuffer + Atomics | postMessage + Service Worker |
| 调用语义 | 同步（Worker侧阻塞等待） | 异步（Promise） |
| 文件IO延迟 | 低 | 较高 |
| HTTP头要求 | COOP: same-origin + COEP: require-corp | 无 |
| 浏览器兼容性 | 需要较新浏览器（SAB支持） | 广泛兼容 |
| Stdin路由 | coincident proxy.processDriveRequest | serviceWorkerManager.registerStdinHandler |
| Worker大小 | 较大（包含coincident库） | 较小 |
| 自定义类 | SharedBufferContentsAPI + SharedArrayBufferFS | 仅ComlinkTerminalShellWorker |
| browsingContextId | 不需要 | 必需 |

## Shell生命周期

每个TerminalShell实例经历以下状态：

```
创建(new) → initWorker() → createRemote() → Worker就绪
    │
    ├── 交互式终端：socket连接 → start() → 运行中
    │       ├── input() 接收用户输入
    │       ├── outputCallback 发送输出
    │       ├── setSize() 处理终端大小变化
    │       └── dispose() → 关闭
    │
    └── 无头shell：outputCallback设置 → start() → 运行中
            ├── input() 发送命令
            ├── exitCode() 等待退出码
            └── dispose() → 关闭
```

### 关键属性

| 属性/方法 | 说明 |
|----------|------|
| `socket` | WebSocketClient实例（仅交互式终端有） |
| `outputCallback` | 输出回调函数，stdout文本通过此函数传递 |
| `workerType` | 'coincident' 或 'comlink'（自动检测） |
| `ready` | Promise，Worker初始化完成时resolve |
| `disposed` | ISignal，shell关闭时发射 |
| `input(text)` | 发送输入到shell（'\r'表示回车执行） |
| `setSize(rows, cols)` | 设置终端尺寸 |
| `start()` | 启动shell（在socket连接后调用） |
| `themeChange(isDark?)` | 通知主题变更 |
| `exitCode()` | Promise，等待命令执行完成并返回退出码 |
| `dispose()` | 释放资源、终止Worker |

## Worker构建

Worker文件通过独立的rspack配置（worker.rspack.config.js）打包：

```javascript
// web worker bundle
module.exports = {
  entry: {
    'coincident.worker': './lib/coincident.worker.js',
    'comlink.worker': './lib/comlink.worker.js'
  },
  output: {
    filename: '[name].js',
    path: path.resolve(__dirname, 'lib'),
    globalObject: 'self'
  },
  resolve: {
    fallback: {
      fs: false,
      child_process: false,
      crypto: false
    }
  }
};
```

- `globalObject: 'self'`：Web Worker中全局对象是self而非window
- `fallback`：Node.js内置模块在浏览器中不可用，设置为false
- Worker入口是TypeScript编译后的`lib/`目录文件（先tsc再rspack）

## 相关概念

- [文件系统与Stdin路由](06-drivefs-and-stdin.md)：DriveFS挂载细节和stdin请求路由
- [无头命令执行](05-headless-exec.md)：createHeadlessShell的特殊行为
- [LiteTerminalAPIClient API参考](../references/client-source.md)：API完整签名
- [Shell与Worker源码信源](../references/shell-source.md)：完整源码细节
