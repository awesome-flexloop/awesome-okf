---
type: Reference
title: 双Worker模式实现参考
description: coincident（SharedArrayBuffer同步模式）和comlink（postMessage异步模式）的Worker实现细节
tags: [worker, coincident, comlink, filesystem, stdin, cross-origin-isolation]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: worker-modes-src
    resource: /references/worker-modes-source.md
    title: packages/xeus/src/coincident.worker.ts and comlink.worker.ts
---

## 模式选择条件

```typescript
if (crossOriginIsolated) {
  return new Worker(new URL('./coincident.worker.js', import.meta.url), { type: 'module' });
} else {
  return new Worker(new URL('./comlink.worker.js', import.meta.url), { type: 'module' });
}
```

`crossOriginIsolated` 是浏览器全局变量，仅当页面发送正确的 COOP/COEP 响应头时为 `true`。

---

## XeusCoincidentKernel（coincident模式）

定义在 coincident.worker.ts。

### SharedBufferContentsAPI

coincident模式定义了一个自定义ContentsAPI，通过coincident的workerAPI代理将文件请求转发到主线程：

```typescript
export class SharedBufferContentsAPI extends ContentsAPI {
  request<T extends TDriveMethod>(data: TDriveRequest<T>): TDriveResponse<T> {
    return workerAPI.processDriveRequest(data);
  }
}
```

### XeusDriveFS

```typescript
class XeusDriveFS extends DriveFS {
  createAPI(options: DriveFS.IOptions): ContentsAPI {
    return new SharedBufferContentsAPI(options);
  }
}
```

XeusDriveFS继承DriveFS，重写createAPI返回SharedBufferContentsAPI，实现基于SharedArrayBuffer的同步文件操作。

### mount 实现

```typescript
async mount(
  driveName: string,
  mountpoint: string,
  baseUrl: string,
  browsingContextId: string
): Promise<void> {
  const { FS, PATH, ERRNO_CODES } = globalThis.Module;
  if (!FS) return;

  const drive = new XeusDriveFS({
    FS, PATH, ERRNO_CODES,
    baseUrl, driveName, mountpoint, browsingContextId
  });
  FS.mkdir(mountpoint);
  FS.mount(drive, {}, mountpoint);
  FS.chdir(mountpoint);  // 切换到挂载点
}
```

### initializeStdin 实现

coincident模式的stdin非常简洁——直接通过workerAPI同步调用主线程：

```typescript
protected initializeStdin(baseUrl: string, browsingContextId: string): void {
  globalThis.get_stdin = (
    inputRequest: KernelMessage.IInputRequestMsg
  ): KernelMessage.IInputReplyMsg =>
    workerAPI.processStdinRequest(inputRequest);
}
```

workerAPI.processStdinRequest在主线程的createRemote中被设置为使用PromiseDelegate等待input_reply，coincident的同步特性使得Worker端可以阻塞等待主线程异步操作完成。

### storeAsGlobal / callGlobalReceiver

```typescript
async storeAsGlobal(object: any, name: string): Promise<void> {
  globalThis[name] = object;
}
async callGlobalReceiver(
  receiverName: string, methodName: string, ...args: any[]
): Promise<void> {
  const receiver = globalThis[receiverName];
  receiver[methodName](...args);
}
```

### Worker 启动

```typescript
const workerAPI = coincident(self) as IXeusWorkerKernel;
const worker = new XeusCoincidentKernel();
// 将worker方法绑定到coincident代理
workerAPI.initialize = worker.initialize.bind(worker);
workerAPI.mount = worker.mount.bind(worker);
workerAPI.ready = worker.ready.bind(worker);
workerAPI.cd = worker.cd.bind(worker);
workerAPI.isDir = worker.isDir.bind(worker);
workerAPI.processMessage = worker.processMessage.bind(worker);
workerAPI.storeAsGlobal = worker.storeAsGlobal.bind(worker);
workerAPI.callGlobalReceiver = worker.callGlobalReceiver.bind(worker);
```

coincident模式通过`coincident(self)`创建主线程代理，主线程通过同一代理调用Worker方法。不需要onmessage监听——coincident库内部处理消息路由。

**关键特性**：
- 不需要 Service Worker 支持 stdin
- 文件系统通过 SharedBufferContentsAPI + XeusDriveFS 实现同步调用
- stdin 通过 coincident 同步代理直接调用主线程 processStdinRequest
- 需要页面设置 COOP/COEP 头

---

## XeusComlinkKernel（comlink模式）

定义在 comlink.worker.ts。

### mount 实现

```typescript
async mount(
  driveName: string,
  mountpoint: string,
  baseUrl: string,
  browsingContextId: string
): Promise<void> {
  const { FS, PATH, ERRNO_CODES } = globalThis.Module;
  if (!FS) return;

  const drive = new DriveFS({
    FS, PATH, ERRNO_CODES,
    baseUrl, driveName, mountpoint, browsingContextId
  });
  FS.mkdir(mountpoint);
  FS.mount(drive, {}, mountpoint);
  FS.chdir(mountpoint);  // 切换到挂载点
}
```

注意：comlink模式的DriveFS构造函数不直接传入contents代理——DriveFS内部通过JupyterLite的browsingContextId机制路由到正确的Contents API。不需要`await drive.ready`。

### initializeStdin 实现

使用**同步XMLHttpRequest**阻塞等待Service Worker响应：

```typescript
protected initializeStdin(baseUrl: string, browsingContextId: string): void {
  globalThis.get_stdin = (inputRequest: any): any => {
    try {
      const xhr = new XMLHttpRequest();
      const url = URLExt.join(baseUrl, '/api/stdin/kernel');
      xhr.open('POST', url, false); // 同步XMLHttpRequest
      const msg = JSON.stringify({
        browsingContextId,
        data: inputRequest
      });
      xhr.send(msg);
      const inputReply = JSON.parse(xhr.response as string);
      if ('error' in inputReply) {
        throw new Error(inputReply['error']);
      }
      return inputReply;
    } catch (err) {
      return { error: `Failed to request stdin via service worker: ${err}` };
    }
  };
}
```

**关键差异**：
- stdin请求URL是`{baseUrl}/api/stdin/kernel`（不带kernel_id）
- 请求体包含`browsingContextId`字段（用于Service Worker路由到正确的tab）
- 不需要先通过xserver.send_msg发送消息——Service Worker和主线程协作处理
- 包含error处理逻辑

### storeAsGlobal / callGlobalReceiver

```typescript
storeAsGlobal(object: any, name: string) {
  console.log(`Storing object as globalThis.${name}`);
  globalThis[name] = object;
  console.log(`Stored object as globalThis.${name}`);
}
async callGlobalReceiver(
  receiverName: string, methodName: string, ...args: any[]
): Promise<void> {
  const receiver = globalThis[receiverName];
  receiver[methodName](...args);
}
```

注意：storeAsGlobal不是async方法，不使用comlink.proxy——直接赋值到globalThis（comlink的expose机制自动处理跨线程对象传输）。

### Worker 启动

```typescript
const worker = new XeusComlinkKernel();
expose(worker);
```

极其简洁——`expose(worker)`将整个worker实例通过comlink暴露给主线程，主线程使用`comlink.wrap(worker)`获取代理。

**关键特性**：
- stdin 依赖 Service Worker 拦截 `/api/stdin/kernel` POST请求
- 同步 XHR 是 Emscripten C++ 内核调用 get_stdin 时阻塞的方式
- 文件系统通过标准 DriveFS + postMessage 异步桥接
- 不需要 crossOriginIsolated，JupyterLite默认Service Worker即可工作
- Worker启动极简：`new XeusComlinkKernel(); expose(worker);`

---

## 两种模式对比

| 特性 | coincident模式 | comlink模式 |
|------|---------------|-------------|
| 前提条件 | crossOriginIsolated=true（COOP/COEP头） | Service Worker注册 |
| 文件系统API | XeusDriveFS → SharedBufferContentsAPI（SAB同步） | DriveFS（postMessage异步） |
| stdin实现 | workerAPI.processStdinRequest()（coincident同步代理） | 同步XHR → POST /api/stdin/kernel → Service Worker |
| stdin需要Service Worker | 否 | 是 |
| Worker启动 | coincident(self) + 手动bind方法 | expose(worker)（一行） |
| mount后行为 | FS.chdir(mountpoint) | FS.chdir(mountpoint) |
| storeAsGlobal | 直接赋值 | 直接赋值（带console.log） |
| 性能 | 更好（SAB同步调用） | 标准（postMessage异步） |
| 浏览器兼容性 | 需要支持SharedArrayBuffer | 更广（所有现代浏览器） |
| 部署配置 | 需配置COOP/COEP响应头 | JupyterLite默认即可 |

---

## 主线程 createRemote 差异

两种模式在主线程WebWorkerKernel.createRemote()中的设置不同：

### coincident模式

```typescript
const remoteKernel = coincident(this.worker) as IXeusWorkerKernel;
// processDriveRequest直接委托给DriveContentsProcessor
remoteKernel.processDriveRequest = (data) =>
  this._contentsProcessor.processDriveRequest(data);
// processStdinRequest使用PromiseDelegate等待input_reply
remoteKernel.processStdinRequest = (inputRequest) => {
  const delegate = new PromiseDelegate<string>();
  this._stdinDelegate = delegate;
  // 发送input_request消息到JupyterLab
  this.sendInputRequest(inputRequest);
  return delegate.promise;  // coincident使Worker可以同步等待这个Promise
};
```

### comlink模式

```typescript
const remoteKernel = comlink.wrap(this.worker) as Remote<IXeusWorkerKernel>;
// onmessage监听和storeAsGlobal/callGlobalReceiver设置
```

comlink模式下stdin通过Service Worker处理，不需要在主线程设置processStdinRequest。

---

## 相关概念

- [双Worker通信模式](../concepts/03-dual-worker-modes.md)
- [文件系统桥接](../concepts/07-filesystem-bridge.md)
- [内核生命周期](../concepts/04-kernel-lifecycle.md)
- [empack内核实现参考](kernel-impl-source.md)
