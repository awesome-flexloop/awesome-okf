---
type: Reference
title: xeus empack内核实现API参考
description: "@jupyterlite/xeus 包的WebWorkerKernel和EmpackedXeusRemoteKernel具体实现API"
tags: [api, kernel, empack, mambajs, typescript]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: xeus-src
    resource: /references/kernel-impl-source.md
    title: packages/xeus/src/ source files
---

## WebWorkerKernel 类

主线程内核实现，继承 `WebWorkerKernelBase`，定义在 [kernel.ts](file:///d:/spaces/SpecWeave/external/libs/jupyter/xeus/packages/xeus/src/kernel.ts)。

### IOptions 扩展

```typescript
interface WebWorkerKernel.IOptions extends WebWorkerKernelBase.IOptions {
  empackEnvMetaLink?: string;
}
```

### initWorker 实现

根据 `crossOriginIsolated` 全局变量选择Worker入口：

```typescript
initWorker(options: WebWorkerKernel.IOptions): Worker {
  if (crossOriginIsolated) {
    return new Worker(new URL('./coincident.worker.js', import.meta.url), { type: 'module' });
  } else {
    return new Worker(new URL('./comlink.worker.js', import.meta.url), { type: 'module' });
  }
}
```

### createRemote 实现

- 添加 `worker.addEventListener('message', e => processWorkerMessage(e.data))` 监听所有Worker消息
- coincident模式：使用 `coincident(this.worker)` 代理，额外设置：
  - `processDriveRequest`：委托给 `DriveContentsProcessor.processDriveRequest`
  - `processStdinRequest`：使用 `PromiseDelegate` 异步等待input_reply
  - `globalThis.storeAsGlobal`：使用 `coincident.transfer()` 传输对象
- comlink模式：使用 `comlink.wrap(this.worker)` 代理
  - `globalThis.storeAsGlobal`：使用 `comlink.transfer()` 传输对象
- 通用设置：`globalThis.callGlobalReceiver` 转发调用到Worker

### initRemote 重写

```typescript
protected async initRemote(options: WebWorkerKernel.IOptions) {
  return (this.remoteKernel as IEmpackXeusWorkerKernel).initialize({
    baseUrl: PageConfig.getBaseUrl(),
    kernelId: this.id,
    mountDrive: options.mountDrive,
    kernelSpec: options.kernelSpec,
    browsingContextId: options.browsingContextId,
    empackEnvMetaLink: options.empackEnvMetaLink
  });
}
```

## EmpackedXeusRemoteKernel 类

Worker端empack内核基类，继承 `XeusRemoteKernelBase`，定义在 [worker.ts](file:///d:/spaces/SpecWeave/external/libs/jupyter/xeus/packages/xeus/src/worker.ts)。

### initializeModule 实现

加载内核二进制文件（.js/.wasm/.data）和共享库：

1. 拼接URL：`binaryJS = baseUrl + kernelSpec.argv[0]`，binaryWASM/binaryDATA通过替换.js后缀获得
2. `kernelRootUrl = baseUrl/xeus/{envName}`
3. 从 `kernelSpec.metadata.shared` 获取共享库映射
4. 调用 `importScripts(binaryJS)` 加载内核JS
5. 返回包含 `locateFile` 函数的对象：
   - sharedLibs中的文件 → `kernelRootUrl/{kernelName}/{file}`
   - libxeus.so → `kernelRootUrl/libxeus.so`
   - .wasm → binaryWASM路径
   - .data → binaryDATA路径

### initializeFileSystem 实现

从empack打包的环境引导文件系统：

1. 构造 `kernelRootUrl = baseUrl/xeus/kernels/{kernelSpec.dir}`
2. `empackEnvMetaLocation = empackEnvMetaLink || kernelRootUrl`
3. fetch `{empackEnvMetaLocation}/empack_env_meta.json`
4. `_pkgRootUrl = baseUrl/xeus/{envName}/kernel_packages`
5. 调用 `empackLockToMambajsLock()` 转换锁文件格式
6. 检查 `Module.FS` 是否存在（不存在则警告返回）
7. 设置 `_prefix = empackEnvMeta.prefix`
8. 调用 `bootstrapEmpackPackedEnvironment()` 解压所有包到Emscripten FS
9. 保存返回的 `paths/pythonVersion/sharedLibs`

### initializeInterpreter 实现

1. 如果 `Module.FS` 不存在则返回
2. 如果 `kernelSpec.name === 'xpython'`：检查 `_pythonVersion` 存在 → 调用 `bootstrapPython({prefix, pythonVersion, Module})`
3. 如果 `emscriptenMajorVersion < 4`：调用 `loadSharedLibs()` 加载共享库

### emscriptenMajorVersion getter

遍历 `_lock.packages`，查找名为 `emscripten-abi` 的包，解析版本号主版本号。未找到时 fallback 为 0（触发加载所有共享库的安全路径）。

### 动态包管理方法

```typescript
// 安装包
protected async install(options: IInstallationCommandOptions): Promise<void>
// conda: install(specs, lock, channels, logger)
// pip: pipInstall(specs, lock, logger)

// 卸载包
protected async uninstall(options: IUninstallationCommandOptions): Promise<void>
// conda: remove(specs, lock, logger)
// pip: pipUninstall(specs, lock, logger)

// 列出已安装包
protected listInstalledPackages(options: IListCommandOptions): Promise<void>
// conda: showPackagesList({packages, pipPackages}, logger)
// pip: showPipPackagesList(pipPackages, logger)
```

安装/卸载后调用 `_reloadPackagesInFS(newLock)` 更新文件系统。

### _reloadPackagesInFS 方法

```typescript
private async _reloadPackagesInFS(newLock: ILock)
```

1. 保存当前工作目录 `pwd = FS.cwd()`
2. `FS.chdir('/')` 避免触发自定义FS的API
3. 调用 `updatePackagesInEmscriptenFS()` 计算新旧lock差异并更新FS
4. 过滤共享库（排除已链接的内核共享库）
5. emscripten<4时加载新的共享库
6. 更新 `_lock = newLock`
7. finally 恢复 `FS.chdir(pwd)`

## IEmpackXeusWorkerKernel 接口

```typescript
interface IEmpackXeusWorkerKernel extends IXeusWorkerKernel {
  initialize(options: IEmpackXeusWorkerKernel.IOptions): Promise<void>;
}

namespace IEmpackXeusWorkerKernel {
  interface IOptions extends IXeusWorkerKernel.IOptions {
    empackEnvMetaLink?: string;
  }
}
```

## 全局函数注入

WebWorkerKernel.createRemote 在主线程 globalThis 上注入两个函数：

| 函数 | 签名 | 说明 |
|------|------|------|
| `storeAsGlobal` | `(object: any, name: string) => Promise<void>` | 将对象（如OffscreenCanvas）存储到Worker全局作用域 |
| `callGlobalReceiver` | `(receiverName, methodName, ...args) => Promise<any>` | 调用Worker全局对象上的方法 |

## 相关概念

- [xeus-core基类API](kernel-base-source.md)
- [双Worker模式参考](worker-modes-source.md)
- [内核生命周期](../concepts/04-kernel-lifecycle.md)
- [文件系统桥接](../concepts/07-filesystem-bridge.md)
- [包管理](../concepts/06-package-management.md)
