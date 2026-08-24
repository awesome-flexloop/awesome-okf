---
type: Reference
title: xeus-core 基类API参考
description: "@jupyterlite/xeus-core 包的核心抽象基类、接口定义和日志系统API"
tags: [api, base-class, kernel, worker, typescript]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: xeus-core-src
    resource: /references/kernel-base-source.md
    title: packages/xeus-core/src/ source files
---

## IXeusWorkerKernel 接口

Worker端内核接口，定义在 [interfaces.ts](file:///d:/spaces/SpecWeave/external/libs/jupyter/xeus/packages/xeus-core/src/interfaces.ts)。

```typescript
interface IXeusWorkerKernel extends IWorkerKernel {
  initialize(options: IXeusWorkerKernel.IOptions): Promise<void>;
  processDriveRequest<T extends TDriveMethod>(data: TDriveRequest<T>): TDriveResponse<T>;
  processMessage(msg: any): void;
  processStdinRequest(inputRequest: KernelMessage.IInputRequestMsg): KernelMessage.IInputReplyMsg;
  processWorkerMessage(msg: any): void;
  ready(): Promise<void>;
  mount(driveName: string, mountpoint: string, baseUrl: string, browsingContextId: string): Promise<void>;
  cd(path: string): Promise<void>;
  isDir(path: string): Promise<boolean>;
  storeAsGlobal(object: any, name: string): Promise<void>;
  callGlobalReceiver(receiverName: string, methodName: string, ...args: any[]): Promise<void>;
}
```

### IOptions 字段

| 字段 | 类型 | 说明 |
|------|------|------|
| baseUrl | string | 服务器基础URL |
| kernelId | string | 内核唯一ID |
| kernelSpec | any | 内核规格（kernel.json内容） |
| mountDrive | boolean | 是否挂载JupyterLite内容目录 |
| browsingContextId | string | 当前页面/浏览上下文ID |

## WebWorkerKernelBase 类

主线程内核抽象基类，定义在 [kernel.base.ts](file:///d:/spaces/SpecWeave/external/libs/jupyter/xeus/packages/xeus-core/src/kernel.base.ts)。

### 构造函数

```typescript
constructor(options: WebWorkerKernelBase.IOptions)
```

初始化顺序：设置id/name/location → 创建DriveContentsProcessor → initWorker() → createRemote() → initRemote() → initFileSystem() → _ready.resolve()

### 抽象方法（子类必须实现）

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `initWorker(options)` | `Worker` | 创建Web Worker实例 |
| `createRemote(options)` | `IXeusWorkerKernel \| Remote<IXeusWorkerKernel>` | 创建远程内核代理 |

### 可覆盖方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `initRemote(options)` | `Promise<void>` | 初始化远程内核（调用remoteKernel.initialize） |

### 公共方法

| 方法 | 说明 |
|------|------|
| `handleMessage(msg)` | 处理来自JupyterLab的消息（async） |
| `processWorkerMessage(msg)` | 处理来自Worker的消息（特殊处理OPEN_TAB和_stream） |
| `dispose()` | 终止Worker，清理资源 |

### 只读属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `id` | string | 内核ID |
| `name` | string | 内核名称 |
| `location` | string | 内核工作目录位置 |
| `ready` | Promise\<void\> | 内核就绪Promise |
| `isDisposed` | boolean | 是否已销毁 |
| `disposed` | ISignal\<this, void\> | 销毁信号 |
| `parentHeader` | KernelMessage.IHeader \| undefined | 最近父消息头 |
| `parent` | KernelMessage.IMessage \| undefined | 最近父消息 |

## XeusRemoteKernelBase 类

Worker端远程内核抽象基类，定义在 [worker.base.ts](file:///d:/spaces/SpecWeave/external/libs/jupyter/xeus/packages/xeus-core/src/worker.base.ts)。

### 核心生命周期方法 initialize()

```typescript
async initialize(options: IXeusWorkerKernel.IOptions): Promise<void>
```

执行顺序：
1. `initializeLogger(options)` — 创建日志器
2. 初始化 toplevel_promise 为 null（处理顶层await）
3. `initializeModule(options)` — 加载WASM模块（抽象）
4. `createXeusModule(this.Module)` — 创建Emscripten Module实例
5. `waitRunDependencies(this.Module)` — 等待运行时依赖
6. `initializeFileSystem(options)` — 初始化文件系统（抽象）
7. `initializeInterpreter(options)` — 初始化解释器（抽象，如Python bootstrap）
8. `initializeStdin(baseUrl, browsingContextId)` — 初始化stdin处理（抽象）
9. 创建 `xkernel` 实例（emscripten<4时fallback无argv）
10. `xserver = xkernel.get_server()` 获取消息服务器
11. `xkernel.start()` 启动内核
12. `setKernelReady()` 标记就绪

### 抽象方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `initializeModule(options)` | `any` | 加载Emscripten模块，返回locateFile配置 |
| `initializeFileSystem(options)` | `Promise<any>` | 初始化Emscripten虚拟文件系统 |
| `initializeInterpreter(options)` | `Promise<any>` | 初始化语言解释器（如Python） |
| `initializeStdin(baseUrl, ctxId)` | `void` | 设置globalThis.get_stdin |
| `mount(...)` | `Promise<void>` | 挂载DriveFS到Emscripten FS |
| `install(options)` | `Promise<void>` | 处理%conda/%pip install |
| `uninstall(options)` | `Promise<void>` | 处理remove/uninstall |
| `listInstalledPackages(options)` | `Promise<void>` | 处理list命令 |
| `emscriptenMajorVersion` (getter) | `number` | Emscripten主版本号 |

### 魔法命令处理

```typescript
protected async processMagics(code: string): Promise<string>
```

使用mambajs-core的`parse()`解析`%conda install`/`%pip install`/`%conda remove`/`%conda list`等魔法命令，执行对应操作后返回剥离魔法后的可执行代码。

## XeusWorkerLoggerBase 类

基于BroadcastChannel的日志系统。

| 方法 | 输出通道 | ANSI颜色 | BroadcastChannel level |
|------|---------|---------|----------------------|
| `log(...msg)` | stdout（_stream） | 无 | info |
| `warn(...msg)` | stdout（_stream） | `\x1b[38;5;208m`（橙色） | warning |
| `error(...msg)` | stderr（_stream，含evalue/traceback） | 无 | critical |

## IOptions

```typescript
interface WebWorkerKernelBase.IOptions extends IKernel.IOptions {
  contentsManager: Contents.IManager;
  mountDrive: boolean;
  kernelSpec: any;
  browsingContextId: string;
}
```

## 相关概念

- [内核生命周期](../concepts/04-kernel-lifecycle.md)
- [双Worker通信模式](../concepts/03-dual-worker-modes.md)
- [xeus具体实现参考](kernel-impl-source.md)
