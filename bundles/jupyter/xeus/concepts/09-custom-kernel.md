---
type: Concept
title: 自定义xeus内核集成
description: 如何基于xeus-core抽象层开发自定义WASM内核集成，包括扩展基类、实现抽象方法、创建Worker入口和注册JupyterLab插件
tags: [custom-kernel, extension, advanced, wasm, abstraction]
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
  - id: worker-modes
    resource: /references/worker-modes-source.md
    title: Worker模式参考
  - id: insight-3
    resource: /concepts/09-custom-kernel.md
    title: 洞察I-3 三层抽象
---

## 扩展场景分类

基于三层抽象架构，扩展xeus内核系统有以下场景：

| 场景 | 需要修改的层 | 复杂度 |
|------|------------|--------|
| 新增xeus语言内核（已有WASM二进制） | 仅构建配置（Python端） | 低 |
| 新的包分发格式（不用empack） | Layer 2：新的RemoteKernel | 中 |
| 新的通信机制（不用coincident/comlink） | Layer 2：新Worker+Kernel子类 | 中 |
| 完全自定义内核（不用xeus C++框架） | Layer 1+2+3 | 高 |

本文档覆盖前三类场景。第四类（完全自定义内核）应直接参考 `@jupyterlite/kernel` 的IKernel接口，不必基于xeus-core。

## 场景1：新增xeus语言内核

如果已有xeus-xxx内核编译好的WASM二进制（如xeus-rust、xeus-java等），只需在构建端配置即可，无需修改TypeScript。

### 步骤

1. **确保内核包在emscripten-forge中可用**：
   - 检查 `https://prefix.dev/emscripten-forge-4x` 是否有 `xeus-yourlang` 包
   - 如果没有，需要先将内核添加到emscripten-forge仓库

2. **创建environment.yml**：

```yaml
name: xeus-yourlang-kernel
channels:
  - https://prefix.dev/emscripten-forge-4x
  - https://prefix.dev/conda-forge
dependencies:
  - xeus-yourlang  # 你的内核包
  - yourlang-libs  # 该语言需要的其他库
```

3. **构建JupyterLite**：

```bash
jupyter lite build --XeusAddon.environment_file=environment.yml
```

4. **验证kernels.json**：构建后检查 `_output/xeus/kernels.json` 是否包含你的内核

### 工作原理

XeusAddon.post_build() 流程：
1. micromamba创建包含xeus-yourlang的emscripten-wasm32环境
2. `copy_xpython_static` 通用化——它读取conda-meta中xeus-xxx的files列表，复制所有文件
3. empack打包整个环境
4. write_kernelspecs为每个xeus内核生成kernel.json

如果内核包的conda recipe正确设置了文件列表和kernel.json模板，这一切自动完成。

## 场景2：新的包分发格式（替换empack+mambajs）

如果你不想使用empack打包格式（例如想用自定义的包分发机制），需要继承 `XeusRemoteKernelBase` 实现新的RemoteKernel。

### 实现步骤

#### 2.1 创建自定义RemoteKernel

```typescript
// packages/your-kernel/src/worker.ts
import { XeusRemoteKernelBase } from '@jupyterlite/xeus-core';

export abstract class YourRemoteKernel extends XeusRemoteKernelBase {
  /**
   * 加载WASM模块——替换empack的locateFile逻辑
   */
  initializeModule(options: IXeusWorkerKernel.IOptions): any {
    const baseUrl = options.baseUrl;
    const kernelBinary = baseUrl + 'your-kernels/' + options.kernelSpec.name + '/kernel.js';

    // 加载你的WASM模块
    importScripts(kernelBinary);

    return {
      locateFile: (path: string, scriptDirectory: string) => {
        // 自定义文件定位逻辑
        if (path.endsWith('.wasm')) {
          return baseUrl + 'your-kernels/' + options.kernelSpec.name + '/' + path;
        }
        return scriptDirectory + path;
      },
    };
  }

  /**
   * 初始化文件系统——替换bootstrapEmpackPackedEnvironment
   */
  async initializeFileSystem(options: IXeusWorkerKernel.IOptions): Promise<any> {
    // 你的文件系统初始化逻辑
    // 例如下载自定义格式的包、解压到MEMFS
    const baseUrl = options.baseUrl;
    const fsDataUrl = baseUrl + 'your-kernels/' + options.kernelSpec.name + '/fs-data.bin';

    // 下载并解压...
    // 调用 this.Module.FS.createPath / FS.writeFile 等

    // 设置前缀路径
    this._prefix = '/usr/local';

    // 返回共享库信息
    return {
      paths: new Map(),
      pythonVersion: [3, 12, 0] as any, // 如果不是Python内核则不需要
      sharedLibs: [] as any,
    };
  }

  /**
   * 初始化解释器——如果不是Python，可能不需要bootstrapPython
   */
  async initializeInterpreter(options: IXeusWorkerKernel.IOptions): Promise<any> {
    // 非Python内核可能不需要此步骤
    // Python内核需要调用bootstrapPython
  }

  /**
   * 包管理——替换mambajs
   */
  async install(options: IInstallationCommandOptions): Promise<void> {
    if (options.type === 'your-pkg-manager') {
      // 你的包安装逻辑
      // 下载包、解压到FS、加载共享库
    }
    // 更新lock文件
    await this._reloadPackagesInFS(newLock);
  }

  async uninstall(options: IUninstallationCommandOptions): Promise<void> {
    // 你的包卸载逻辑
  }

  async listInstalledPackages(options: IListCommandOptions): Promise<void> {
    // 列出已安装包
  }

  get emscriptenMajorVersion(): number {
    // 返回Emscripten版本号
    return 4;
  }

  // mount和initializeStdin根据通信模式由子类实现
}
```

#### 2.2 创建主线程Kernel类

```typescript
// packages/your-kernel/src/kernel.ts
import { WebWorkerKernelBase } from '@jupyterlite/xeus-core';
import type { IXeusWorkerKernel } from '@jupyterlite/xeus-core';

export class YourWebWorkerKernel extends WebWorkerKernelBase {
  constructor(options: YourWebWorkerKernel.IOptions) {
    super(options);
  }

  initWorker(options: WebWorkerKernelBase.IOptions): Worker {
    // 你可以选择复用coincident/comlink模式，或创建新的Worker
    if (crossOriginIsolated) {
      return new Worker(new URL('./coincident.worker.js', import.meta.url), { type: 'module' });
    } else {
      return new Worker(new URL('./comlink.worker.js', import.meta.url), { type: 'module' });
    }
  }

  createRemote(options: WebWorkerKernelBase.IOptions): IXeusWorkerKernel | Remote<IXeusWorkerKernel> {
    // 复用或自定义远程代理创建逻辑
    // 参考WebWorkerKernel.createRemote()
  }

  protected async initRemote(options: WebWorkerKernelBase.IOptions): Promise<void> {
    // 调用远程initialize，传递你的自定义参数
    return (this.remoteKernel as any).initialize({
      baseUrl: PageConfig.getBaseUrl(),
      kernelId: this.id,
      mountDrive: options.mountDrive,
      kernelSpec: options.kernelSpec,
      browsingContextId: options.browsingContextId,
      // 你的自定义参数...
    });
  }
}
```

#### 2.3 创建Worker入口文件

复用coincident/comlink模式（推荐），只需继承你的RemoteKernel：

```typescript
// packages/your-kernel/src/coincident.worker.ts
import { YourRemoteKernel } from './worker';

class YourCoincidentKernel extends YourRemoteKernel {
  async mount(driveName: string, mountpoint: string, baseUrl: string, browsingContextId: string) {
    // 复用SharedBufferContentsAPI或自定义
    const drive = new SharedBufferContentsAPI({ baseUrl, contentsApiUrl: baseUrl + 'api/contents/' });
    drive.activate(this.workerThis, browsingContextId);
    FS.mkdir(mountpoint);
    FS.mount(drive, {}, mountpoint);
  }

  initializeStdin(baseUrl: string, browsingContextId: string) {
    // 复用coincident的PromiseDelegate模式
    // 参考XeusCoincidentKernel.initializeStdin()
  }

  async storeAsGlobal(object: any, name: string) {
    globalThis[name] = object;
  }

  async callGlobalReceiver(receiverName: string, methodName: string, ...args: any[]) {
    return globalThis[receiverName][methodName](...args);
  }
}

// Worker启动逻辑
const kernel = new YourCoincidentKernel();
// 参考coincident.worker.js的启动方式
```

## 场景3：新的通信机制

如果需要支持新的浏览器通信API（如未来的Atomics.waitAsync、其他postMessage封装库等），需要：

1. **创建新的Worker入口类**：继承 `EmpackedXeusRemoteKernel`（或你自己的RemoteKernel），实现mount/initializeStdin/storeAsGlobal/callGlobalReceiver
2. **在主线程Kernel的initWorker/createRemote中添加新模式**：检测环境条件，创建对应的Worker和代理

### 模板

```typescript
// Worker端
class YourNewCommKernel extends EmpackedXeusRemoteKernel {
  async mount(...) {
    // 你的通信机制下的文件系统桥接
  }

  initializeStdin(...) {
    // 你的通信机制下的stdin实现
  }

  async storeAsGlobal(object, name) {
    // 对象传输逻辑
  }

  async callGlobalReceiver(receiverName, methodName, ...args) {
    // 方法调用转发
  }
}

// 主线程
initWorker(options) {
  if (yourCondition) {
    return new Worker(new URL('./your-new-comm.worker.js', import.meta.url), { type: 'module' });
  }
  // fallback到coincident/comlink
  return super.initWorker(options);
}
```

## 关键抽象方法契约

实现自定义Kernel时，必须正确实现以下从基类继承/继承的方法：

### XeusRemoteKernelBase 抽象方法

| 方法 | 必须实现 | 说明 |
|------|---------|------|
| `initializeModule(options)` | ✅ | 返回{locateFile}配置，importScripts加载WASM JS |
| `initializeFileSystem(options)` | ✅ | 返回{paths, pythonVersion?, sharedLibs} |
| `initializeInterpreter(options)` | ✅ | 引导语言解释器（Python需bootstrapPython） |
| `initializeStdin(baseUrl, ctxId)` | ✅ | 设置globalThis.get_stdin函数 |
| `mount(driveName, mountpoint, baseUrl, ctxId)` | ✅ | 将Contents API挂载到Emscripten FS |
| `install(options)` | ✅ | 处理包安装（无包管理可throw "not supported"） |
| `uninstall(options)` | ✅ | 处理包卸载 |
| `listInstalledPackages(options)` | ✅ | 列出已安装包 |
| `emscriptenMajorVersion` (getter) | ✅ | 返回Emscripten主版本号 |

### WebWorkerKernelBase 抽象方法

| 方法 | 必须实现 | 说明 |
|------|---------|------|
| `initWorker(options)` | ✅ | 返回new Worker()实例 |
| `createRemote(options)` | ✅ | 返回Worker的代理对象（coincident/comlink/wrap） |

## 消息协议

Worker端必须正确处理以下消息类型（基类已实现大部分，自定义时注意）：

| 消息event类型 | 发送方向 | 基类处理 | 说明 |
|--------------|---------|---------|------|
| `message` | 主线程→Worker | processMessage | Jupyter协议消息（execute_request等） |
| `stream` | Worker→主线程 | processWorkerMessage | 输出消息（stdout/stderr/display_data等） |
| `OPEN_TAB` | Worker→主线程 | processWorkerMessage | 在新标签页打开URL |
| `worker-message` | Worker→主线程 | Comlink自动处理 | Comlink RPC响应 |

## 内核消息处理循环

基类的 `processMessage()` 将消息传递给C++内核：

```typescript
processMessage(msg: any): void {
  // msg是Jupyter协议消息（来自JupyterLab）
  const jupyterMsg = msg;
  this.xserver.notify_listeners(JSON.stringify(jupyterMsg));
}
```

输出消息通过 `_stream` 回调从C++内核传回：

```typescript
// 在initialize()中xkernel创建后
this.xserver = this.xkernel.get_server();
// C++内核调用publish时触发_stream回调
// 基类构造函数中已设置this._stream = (msg) => self.postMessage({event:'stream', data:msg})
```

自定义内核如果不走xeus C++框架，需要自己实现消息序列化和分发。

## 注册JupyterLab插件

参考 [extension-source.md](../references/extension-source.md) 创建你自己的JupyterLab插件，注册你的Kernel类：

```typescript
const yourKernelPlugin: JupyterFrontEndPlugin<void> = {
  id: 'your-org/your-kernel:kernel',
  autoStart: true,
  requires: [IServiceManager, IKernelSpecs, IBrowserContext],
  activate: (app, serviceManager, kernelSpecs, browserContext) => {
    // fetch你的kernel.json
    // kernelSpecs.register({
    //   name: 'your-kernel',
    //   spec: kernelSpec,
    //   create: async (options) => new YourWebWorkerKernel({...})
    // });
  }
};
```

## 测试验证清单

开发自定义内核后，验证以下功能：

- [ ] 内核在Launcher中显示正确图标和名称
- [ ] 创建Notebook能成功启动内核（无Worker错误）
- [ ] 执行简单代码（如`print("hello")`）返回正确结果
- [ ] stdout/stderr正确显示在Notebook输出中
- [ ] `input()` 函数能弹出输入框并接收输入（两种Worker模式都测试）
- [ ] 文件操作（`open("test.txt", "w").write("hi")`）正确持久化
- [ ] 内核重启/关闭/切换正常
- [ ] crossOriginIsolated=true和false两种环境都测试
- [ ] 错误和异常正确显示（traceback）
- [ ] display_data（rich output）正确渲染

## 相关API

- [IXeusWorkerKernel 接口](../references/kernel-base-source.md#ixeusworkerkernel-接口)
- [WebWorkerKernelBase 类](../references/kernel-base-source.md#webworkerkernelbase-类)
- [XeusRemoteKernelBase 类](../references/kernel-base-source.md#xeusremotekernelbase-类)
- [EmpackedXeusRemoteKernel 类](../references/kernel-impl-source.md#empackedxuesremoterkernel-类)
- [Worker模式参考](../references/worker-modes-source.md)

## 相关概念

- [双语言分层架构](02-architecture.md)
- [双Worker通信模式](03-dual-worker-modes.md)
- [内核生命周期](04-kernel-lifecycle.md)
- [JupyterLab扩展注册](08-extension-registration.md)
