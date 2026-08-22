---
type: Concept
title: 内核生命周期
description: xeus内核从JupyterLab插件激活到用户代码执行的完整生命周期，包括插件注册、Worker创建、WASM加载、文件系统初始化、内核启动和消息循环
tags: [lifecycle, initialization, wasm, kernel, worker, message-loop]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: kernel-base
    resource: /references/kernel-base-source.md
    title: xeus-core基类
  - id: kernel-impl
    resource: /references/kernel-impl-source.md
    title: xeus具体实现
  - id: extension
    resource: /references/extension-source.md
    title: 扩展注册
---

## 生命周期总览

xeus 内核的生命周期分为5个阶段：

```
阶段1: JupyterLab插件激活
  ↓
阶段2: 主线程Kernel创建 + Worker启动
  ↓
阶段3: Worker端WASM模块加载
  ↓
阶段4: 文件系统初始化 + 解释器引导
  ↓
阶段5: 内核启动 + 消息循环就绪
```

## 阶段1：JupyterLab插件激活

触发时机：JupyterLab启动时，`@jupyterlite/xeus-extension:kernel` 插件autoStart。

执行流程（[kernelPlugin](../references/extension-source.md#kernelplugin内核注册)）：

1. 等待 `IServiceManager.ready`
2. Fetch `{baseUrl}xeus/kernels.json` 获取可用内核列表
3. 对每个内核规格：
   a. Fetch `{baseUrl}xeus/kernels/{dir}/kernel.json` 获取完整规格
   b. 构造resources映射（logo图片路径）
   c. 通过 `IKernelSpecs.register()` 注册到JupyterLab
4. 每个注册的KernelSpec提供一个 `create` 工厂函数

此时内核尚未启动，只是注册了"可以创建这个内核"的元信息。

## 阶段2：主线程Kernel创建 + Worker启动

触发时机：用户在Notebook中选择xeus内核，JupyterLab调用create工厂。

执行流程（[WebWorkerKernel](../references/kernel-impl-source.md#webworkerkernel-类) 构造函数 → [WebWorkerKernelBase](../references/kernel-base-source.md#webworkerkernelbase-类)）：

```typescript
constructor(options: WebWorkerKernelBase.IOptions) {
  this._id = options.id;
  this._name = options.name;
  this._location = options.location;
  this._contentsProcessor = new DriveContentsProcessor(...);
  this._worker = this.initWorker(options);       // ← 创建Worker
  this._remoteKernel = this.createRemote(options); // ← 创建远程代理
  this.initRemote(options);                        // ← 初始化Worker
  this.initFileSystem(options);                    // ← 切换工作目录
  this._ready.resolve();                           // ← 标记就绪
}
```

### initWorker：选择并创建Worker

根据 `crossOriginIsolated` 创建不同的Worker入口文件：
- `true` → `new Worker('./coincident.worker.js', {type: 'module'})`
- `false` → `new Worker('./comlink.worker.js', {type: 'module'})`

### createRemote：设置通信代理

**coincident模式**：
```typescript
const remoteKernel = coincident(this.worker) as IXeusWorkerKernel;
remoteKernel.processDriveRequest = (data) => this._contentsProcessor.processDriveRequest(data);
remoteKernel.processStdinRequest = (inputRequest) => { /* PromiseDelegate等待input_reply */ };
globalThis.storeAsGlobal = coincident.transfer((obj, name) => { ... });
```

**comlink模式**：
```typescript
const remoteKernel = comlink.wrap(this.worker) as Remote<IXeusWorkerKernel>;
globalThis.storeAsGlobal = comlink.transfer((obj, name) => { ... });
```

两种模式都：
- 设置 `worker.onmessage` 监听所有Worker消息
- 设置 `globalThis.callGlobalReceiver` 转发方法调用

### initRemote：触发Worker端初始化

```typescript
await this.remoteKernel.initialize({
  baseUrl: PageConfig.getBaseUrl(),
  kernelId: this.id,
  mountDrive: options.mountDrive,
  kernelSpec: options.kernelSpec,
  browsingContextId: options.browsingContextId,
  empackEnvMetaLink: options.empackEnvMetaLink,
});
```

这通过coincident/comlink代理调用Worker端的 `initialize()` 方法。

## 阶段3：Worker端WASM模块加载

触发时机：Worker端收到initialize调用，执行[XeusRemoteKernelBase.initialize()](../references/kernel-base-source.md#核心生命周期方法-initialize)。

### 3.1 日志初始化

```typescript
this.initializeLogger(options);
```
创建 [XeusWorkerLogger](../references/kernel-base-source.md#xeusworkerloggerbase-类) 实例，通过BroadcastChannel发送日志。

### 3.2 WASM模块加载（[EmpackedXeusRemoteKernel.initializeModule()](../references/kernel-impl-source.md#initializemodule-实现)）

1. 构造URL：
   - `binaryJS = baseUrl + kernelSpec.argv[0]`（内核JS入口，如`xeus/kernels/xpython/xpython.js`）
   - `binaryWASM = binaryJS.replace('.js', '.wasm')`
   - `binaryDATA = binaryJS.replace('.js', '.data')`
   - `kernelRootUrl = baseUrl + 'xeus/' + envName`
2. 从 `kernelSpec.metadata.shared` 获取预链接的共享库映射
3. `importScripts(binaryJS)` 加载内核JS（这会注入 `createXeusModule` 全局函数）
4. 返回配置对象，包含 `locateFile` 函数：
   - 共享库 → `kernelRootUrl/{kernelName}/{file}`
   - libxeus.so → `kernelRootUrl/libxeus.so`
   - .wasm → binaryWASM路径
   - .data → binaryDATA路径

### 3.3 创建Emscripten Module实例

```typescript
this.Module = createXeusModule({
  ...this.initializeModule(options),
  // locateFile, preRun等配置
});
```

`createXeusModule` 是内核JS通过 `importScripts` 注入到globalThis的函数，由xeus C++内核通过Emscripten编译生成。

### 3.4 等待运行时依赖

```typescript
await waitRunDependencies(this.Module);
```

等待Emscripten运行时初始化完成。

## 阶段4：文件系统初始化 + 解释器引导

### 4.1 初始化文件系统（[initializeFileSystem()](../references/kernel-impl-source.md#initializefilesystem-实现)）

1. Fetch `empack_env_meta.json`（环境元数据：prefix、packages列表、channels等）
2. `_pkgRootUrl = baseUrl + 'xeus/{envName}/kernel_packages'`
3. 调用 `empackLockToMambajsLock()` 转换锁文件格式
4. 调用 `bootstrapEmpackPackedEnvironment()` 下载并解压所有conda包到Emscripten MEMFS：
   - 每个包是一个tar.gz文件
   - 解压到 `_prefix`（如 `/usr/local`）
   - 返回 `paths/pythonVersion/sharedLibs`
5. 保存 `_sharedLibs`、`_paths`、`_pythonVersion`

### 4.2 初始化解释器（[initializeInterpreter()](../references/kernel-impl-source.md#initializeinterpreter-实现)）

对于xeus-python：
1. 检查 `_pythonVersion` 是否存在
2. 调用 `bootstrapPython({prefix, pythonVersion, Module})` 初始化Python解释器
3. emscripten<4时调用 `loadSharedLibs()` 加载共享库

### 4.3 初始化stdin

由具体子类实现：
- coincident模式：设置 `globalThis.get_stdin` 使用coincident同步调用
- comlink模式：设置 `globalThis.get_stdin` 使用同步XHR→Service Worker

详见 [双Worker通信模式](03-dual-worker-modes.md)。

### 4.4 挂载DriveFS（由子类mount()实现）

```typescript
await this.mount('drive', '/drive', baseUrl, browsingContextId);
// coincident: SharedBufferContentsAPI
// comlink: DriveFS
```

将JupyterLite Contents API挂载到Emscripten FS的 `/drive` 目录。

## 阶段5：内核启动 + 消息循环就绪

### 5.1 创建xeus内核实例

```typescript
if (this.emscriptenMajorVersion >= 4) {
  this.xkernel = new this.Module.xkernel(this.Module, {
    kernel_name: kernelSpec.name,
    token: '',
  });
} else {
  // fallback: 无argv方式
  this.xkernel = new this.Module.xkernel(this.Module);
}
this.xserver = this.xkernel.get_server();
```

`Module.xkernel` 是C++ xeus内核类通过Emscripten绑定暴露的JS构造函数。

### 5.2 启动内核

```typescript
this.xkernel.start();
```

这会启动xeus的消息处理循环，开始监听来自xserver的消息。

### 5.3 切换工作目录

[WebWorkerKernelBase.initFileSystem()](../references/kernel-base-source.md#webworkerkernelbase-类)：

```typescript
const tryCd = async (path: string) => {
  if (await this.remoteKernel.isDir(path)) {
    await this.remoteKernel.cd(path);
  }
};
// 优先级：/files/{localPath} > /files > /drive/{localPath}
await tryCd('/files/' + localPath);
await tryCd('/files');
await tryCd('/drive/' + localPath);
```

### 5.4 标记就绪

```typescript
this.setKernelReady();
// 主线程 _ready.resolve() 在构造函数中已完成
// Worker端通过消息通知主线程内核已就绪
```

## 运行时消息循环

内核就绪后进入消息循环：

### 主线程 → Worker（代码执行）

1. JupyterLab发送execute_request消息到WebWorkerKernel
2. `handleMessage(msg)` → 通过remoteKernel发送到Worker
3. Worker端：`processMessage(msg)` → `xserver.notify_listeners(msg)` → C++内核执行代码
4. 执行结果（stream/display_data/execute_result等）通过 `_stream` 回调发送回主线程

### Worker → 主线程（输出/状态）

1. C++内核通过xserver发送消息（stdout/stderr/display_data等）
2. Worker端 `_stream` 回调：`self.postMessage({event: 'stream', data: msg})`
3. 主线程Worker onmessage → `processWorkerMessage(msg)`
4. 特殊消息处理：
   - `OPEN_TAB`：`window.open(msg.url)`
   - 其他：Comlink.exposed的消息通过Comlink机制自动处理
5. 通过 `this._parentHeader` 关联消息到正确的cell

### stdin流程

1. C++内核调用 `get_stdin()`
2. Worker端根据模式不同走不同路径（见[双Worker模式](03-dual-worker-modes.md)）
3. 最终用户输入通过 `onstdin` 回调或XHR响应返回给C++内核

## 销毁流程

```typescript
dispose(): void {
  this._worker.terminate(); // 立即终止Worker
  // 触发 disposed 信号
}
```

Worker终止后，WASM实例、Emscripten FS、所有内存状态全部释放。

## 时序图

```
JupyterLab  MainThread  WebWorker  C++Kernel  ServiceWorker
    │           │           │          │           │
    ├─activate──→│           │          │           │
    │  fetch     │           │          │           │
    │  kernels   │           │          │           │
    │           register    │          │           │
    │           factory     │          │           │
    │           │           │          │           │
    ├─create───→│           │          │           │
    │           ├─new Worker→│         │           │
    │           ├─wrap/wrap─→│         │           │
    │           ├─initialize→│         │           │
    │           │           ├─importScripts       │
    │           │           ├─createXeusModule     │
    │           │           ├─bootstrap FS         │
    │           │           │  (fetch tar.gz)      │
    │           │           ├─bootstrap Python     │
    │           │           ├─init stdin           │
    │           │           ├─FS.mount(drive)      │
    │           │           ├─new xkernel()──→│    │
    │           │           ├─xkernel.start()─→│    │
    │           │  ←ready──│           │           │
    │  ←ready──│           │           │           │
    │           │           │          │           │
    │  execute  │           │          │           │
    ├──────────→├─processMsg→│         │           │
    │           │           ├─notify_listeners──→│ │
    │           │           │          execute     │
    │           │  ←stream──←──────────│           │
    │  ←output──│           │          │           │
    │           │           │          │           │
    │  (comlink模式stdin)    │          │           │
    │  input    │           │          │           │
    ├──────────→├─send msg──→│         │           │
    │           │  (input)   ├─XHR POST────────→│  │ (hold)
    │  reply    │           │          │     ←─────│ (return)
    ├──────────→│  postMsg  │→onstdin──│           │
    │           │           │←value────│           │
```

## 关键API引用

| API | 位置 | 作用 |
|-----|------|------|
| `kernelPlugin.activate` | xeus-extension/src/index.ts | 插件激活入口 |
| `WebWorkerKernelBase` | xeus-core/src/kernel.base.ts | 主线程内核基类 |
| `XeusRemoteKernelBase.initialize()` | xeus-core/src/worker.base.ts | Worker端初始化模板方法 |
| `EmpackedXeusRemoteKernel.initializeModule()` | xeus/src/worker.ts | WASM模块加载 |
| `EmpackedXeusRemoteKernel.initializeFileSystem()` | xeus/src/worker.ts | empack文件系统bootstrap |
| `XeusCoincidentKernel.mount()` | xeus/src/coincident.worker.ts | SAB文件系统挂载 |
| `XeusComlinkKernel.initializeStdin()` | xeus/src/comlink.worker.ts | 同步XHR stdin实现 |

## 相关概念

- [双语言分层架构](02-architecture.md)
- [双Worker通信模式](03-dual-worker-modes.md)
- [文件系统桥接](07-filesystem-bridge.md)
- [扩展注册机制](08-extension-registration.md)
