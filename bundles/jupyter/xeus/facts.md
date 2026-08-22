---
sources:
- ../../../../../external/libs/jupyter/xeus/pyproject.toml
- ../../../../../external/libs/jupyter/xeus/package.json
- ../../../../../external/libs/jupyter/xeus/README.md
- ../../../../../external/libs/jupyter/xeus/setup.py
- ../../../../../external/libs/jupyter/xeus/lerna.json
- ../../../../../external/libs/jupyter/xeus/packages/xeus-core/package.json
- ../../../../../external/libs/jupyter/xeus/packages/xeus-core/src/index.ts
- ../../../../../external/libs/jupyter/xeus/packages/xeus-core/src/interfaces.ts
- ../../../../../external/libs/jupyter/xeus/packages/xeus-core/src/kernel.base.ts
- ../../../../../external/libs/jupyter/xeus/packages/xeus-core/src/worker.base.ts
- ../../../../../external/libs/jupyter/xeus/packages/xeus-core/tsconfig.json
- ../../../../../external/libs/jupyter/xeus/packages/xeus-extension/lab.webpack.config.js
- ../../../../../external/libs/jupyter/xeus/packages/xeus-extension/package.json
- ../../../../../external/libs/jupyter/xeus/packages/xeus-extension/src/index.ts
- ../../../../../external/libs/jupyter/xeus/packages/xeus-extension/src/tokens.ts
- ../../../../../external/libs/jupyter/xeus/packages/xeus-extension/style/index.js
- ../../../../../external/libs/jupyter/xeus/packages/xeus-extension/tsconfig.json
- ../../../../../external/libs/jupyter/xeus/packages/xeus/package.json
- ../../../../../external/libs/jupyter/xeus/packages/xeus/src/coincident.worker.ts
- ../../../../../external/libs/jupyter/xeus/packages/xeus/src/comlink.worker.ts
- ../../../../../external/libs/jupyter/xeus/packages/xeus/src/index.ts
- ../../../../../external/libs/jupyter/xeus/packages/xeus/src/interfaces.ts
- ../../../../../external/libs/jupyter/xeus/packages/xeus/src/kernel.ts
- ../../../../../external/libs/jupyter/xeus/packages/xeus/src/worker.ts
- ../../../../../external/libs/jupyter/xeus/packages/xeus/tsconfig.json
type: Facts
okf_version: '0.2'
title: xeus 源码事实清单
generated: '2026-08-22'
tags:
- facts
---

# jupyterlite-xeus 源码事实清单

> R阶段产出：零推测事实，每条事实指向具体源码位置。禁止出现"用于"/"目的是"/"设计为"等推断词。

## 项目元数据

- F-001: npm 根包名 `@jupyterlite/xeus-root`，版本 `5.0.0`，`private: true`，描述 "JupyterLite loader for Xeus kernels"
- F-002: Python 包名 `jupyterlite_xeus`，版本从 `package.json` 的 nodejs 字段动态获取（`tool.hatch.version.source = "nodejs"`）
- F-003: License 为 BSD-3-Clause，作者为 JupyterLite Contributors
- F-004: 源码仓库地址 `https://github.com/jupyterlite/xeus.git`
- F-005: Python 构建系统使用 hatchling（`requires = ["hatchling>=1.5.0", "hatch-nodejs-version>=0.3.2", "jupyter-builder>=1.0.0,<2"]`），`build-backend = "hatchling.build"`
- F-006: Python 版本要求 `>=3.10`，classifiers 声明支持 Python 3.10-3.14
- F-007: Python 运行时依赖：`empack>=5.1.1,<7`、`traitlets`、`jupyterlite-core>=0.7.0,<0.9.0`、`pyyaml`、`requests`
- F-008: npm workspaces 配置为 `packages/*`，使用 lerna 管理 monorepo
- F-009: Python entry-points 组 `"jupyterlite.addon.v0"` 注册 `jupyterlite-xeus = "jupyterlite_xeus.add_on:XeusAddon"`
- F-010: 前端要求 JupyterLab >= 4.0.0

## 目录结构

- F-011: 源码包含三个 npm 包，位于 `packages/` 目录：`xeus-core`、`xeus`、`xeus-extension`
- F-012: Python 源码位于 `jupyterlite_xeus/` 目录，包含 `__init__.py`、`add_on.py`、`constants.py`、`create_conda_env.py`、`_pip.py`
- F-013: `jupyterlite_xeus/labextension/` 为前端扩展构建输出目录（wheel 中映射到 `share/jupyter/labextensions/@jupyterlite/xeus`）
- F-014: `install.json` 文件在 wheel 中映射到 `share/jupyter/labextensions/@jupyterlite/xeus/install.json`

## 包 `@jupyterlite/xeus-core`（packages/xeus-core/）

- F-015: 包名 `@jupyterlite/xeus-core`，版本 `5.0.0`，描述 "JupyterLite Xeus core library"
- F-016: 入口文件 `src/index.ts` 导出三个模块：`./interfaces`、`./kernel.base`、`./worker.base`
- F-017: 依赖：`@emscripten-forge/mambajs-core@^0.21.2`、`@jupyterlab/coreutils@^6.5.0`、`@jupyterlab/services@^7.5.0`、`@jupyterlite/services@^0.7.0 || ^0.8.0`、`@lumino/coreutils@^2`、`@lumino/signaling@^2`

### 接口定义（packages/xeus-core/src/interfaces.ts）

- F-018: `IXeusWorkerKernel` 接口继承自 `IWorkerKernel`（来自 `@jupyterlite/services`）
- F-019: `IXeusWorkerKernel` 声明方法：`initialize(options)`、`processDriveRequest(data)`、`processMessage(msg)`、`processStdinRequest(inputRequest)`、`processWorkerMessage(msg)`、`ready()`、`mount(driveName, mountpoint, baseUrl, browsingContextId)`、`cd(path)`、`isDir(path)`、`storeAsGlobal(object, name)`、`callGlobalReceiver(receiverName, methodName, ...args)`
- F-020: `IXeusWorkerKernel.IOptions` 继承自 `IWorkerKernel.IOptions`，字段包括：`baseUrl: string`、`kernelId: string`、`kernelSpec: any`、`mountDrive: boolean`、`browsingContextId: string`

### WebWorkerKernelBase 类（packages/xeus-core/src/kernel.base.ts）

- F-021: `WebWorkerKernelBase` 是抽象类，实现 `IKernel` 接口（来自 `@jupyterlite/services`），定义在第19行
- F-022: 构造函数接受 `WebWorkerKernelBase.IOptions` 参数，从中解构 `id, name, sendMessage, location, contentsManager`
- F-023: 构造函数中初始化顺序：设置 `_id/_name/_location` → 创建 `DriveContentsProcessor` → 设置 `sendMessage` → 调用 `initWorker(options)` 创建 Worker → 调用 `createRemote(options)` 创建远程代理 → 链式调用 `initRemote(options).then(() => this.initFileSystem(options)).then(this._ready.resolve.bind(this._ready))`
- F-024: `initWorker(options)` 和 `createRemote(options)` 是抽象方法，由子类实现
- F-025: `initRemote(options)` 方法（protected）调用 `this.remoteKernel.initialize()`，传入 `baseUrl`（来自 `PageConfig.getBaseUrl()`）、`kernelId`（`this.id`）、`mountDrive`、`kernelSpec`、`browsingContextId`
- F-026: `handleMessage(msg)` 方法（async）：设置 `_parent/_parentHeader`，调用 `_sendMessageToWorker(msg)`
- F-027: `processWorkerMessage(msg)` 方法：处理来自 Worker 的消息；无 `msg.header` 时特殊处理 `OPEN_TAB`（调用 `window.open`）和 `_stream`（自定义流消息，包含 stderr 错误处理和 stdout/stderr 流转发）；有 `msg.header` 时设置 session 后调用 `sendMessage(msg)`
- F-028: `_sendMessageToWorker(msg)` 方法：`input_reply` 类型消息通过 `inputDelegate.resolve(msg)` 处理；其他消息调用 `remoteKernel.processMessage({ msg, parent: this._parent })`
- F-029: 提供只读属性：`parentHeader`、`parent`、`location`、`ready`（返回 `_ready.promise`）、`isDisposed`、`disposed`（Signal）、`id`、`name`
- F-030: `dispose()` 方法：调用 `worker.terminate()`，置空 worker 和 remoteKernel，设置 `_isDisposed=true`，发射 `_disposed` 信号
- F-031: `initFileSystem(options)` 方法（private）：解析 `location` 中的 driveName 和 localPath → 等待 `remoteKernel.ready()` → 调用 `remoteKernel.mount()` 挂载 drive → 根据路径存在性调用 `remoteKernel.cd()` 切换工作目录（优先级：`/files/{localPath}` > `/files` > `/drive/{localPath}`）
- F-032: 受保护属性：`contentsManager: Contents.IManager`、`contentsProcessor: DriveContentsProcessor`、`remoteKernel`、`worker: Worker`、`sendMessage: IKernel.SendMessage`、`inputDelegate`（PromiseDelegate）
- F-033: `WebWorkerKernelBase.IOptions` 继承自 `IKernel.IOptions`，字段包括：`contentsManager: Contents.IManager`、`mountDrive: boolean`、`kernelSpec: any`、`browsingContextId: string`

### XeusRemoteKernelBase 类（packages/xeus-core/src/worker.base.ts）

- F-034: `XeusWorkerLoggerBase` 类实现 `ILogger` 接口（来自 `@emscripten-forge/mambajs-core`），定义在第37行
- F-035: `XeusWorkerLoggerBase` 构造函数接受 `kernelId: string`，创建 `BroadcastChannel('/xeus-kernel-logs-broadcast')`
- F-036: `XeusWorkerLoggerBase.log(...msg)` 通过 `postMessage({_stream: {name:'stdout', ...}})` 发送消息，同时通过 BroadcastChannel 发送 `{kernelId, payload: {type:'text', level:'info', data}}`
- F-037: `XeusWorkerLoggerBase.warn(...msg)` 发送带 ANSI 颜色码 `\x1b[38;5;208m` 的 stdout 消息，BroadcastChannel level 为 `'warning'`
- F-038: `XeusWorkerLoggerBase.error(...msg)` 发送 stderr 消息（含 `evalue`、`traceback:[]`、`executionCount`），BroadcastChannel level 为 `'critical'`
- F-039: `XeusWorkerLoggerBase.executionCount` 初始值为 0
- F-040: `XeusRemoteKernelBase` 是抽象类，定义在第107行
- F-041: `XeusRemoteKernelBase` 构造函数初始化 `_ready` Promise，设置 `setKernelReady = resolve`
- F-042: `ready()` 方法返回 `this._ready`
- F-043: `cd(path)` 方法：如果 path 存在且 `Module.FS` 存在，调用 `Module.FS.chdir(path)`
- F-044: `isDir(path)` 方法：try 调用 `Module.FS.lookupPath(path)` 后用 `Module.FS.isDir()` 判断，catch 返回 false
- F-045: `processMessage(event)` 方法（async）：获取 `msg_type` → 等待 `globalThis.ready` → 处理顶层 await Promise（`toplevel_promise`）→ `input_reply` 消息不处理 → `execute_request` 消息时递增 `executionCount`、调用 `processMagics()` 处理魔法命令、调用 `xserver.notify_listener(event.msg)` → 其他消息直接 `xserver.notify_listener(event.msg)`
- F-046: `Module` getter/setter 操作 `globalThis.Module`
- F-047: `emscriptenMajorVersion` 是抽象 getter，返回 number
- F-048: `initialize(options)` 方法（async）流程：调用 `initializeLogger()` → 初始化 `globalThis.toplevel_promise=null` 和 `toplevel_promise_py_proxy=null` → 调用 `initializeModule()` 获取 Module 配置 → 调用 `createXeusModule(this.Module)` 创建 Module → 调用 `waitRunDependencies(this.Module)` → 调用 `initializeFileSystem()` → 调用 `initializeInterpreter()` → 调用 `initializeStdin()` → 创建 `xkernel`（emscripten<4时先试带argv再fallback无参，emscripten>=4时直接带argv）→ 获取 `xserver = xkernel.get_server()` → 调用 `xkernel.start()` → 调用 `setKernelReady()`
- F-049: `initializeLogger()` 默认返回 `new XeusWorkerLoggerBase(options.kernelId)`
- F-050: 抽象方法：`initializeModule(options)`、`initializeFileSystem(options)`、`initializeInterpreter(options)`、`initializeStdin(baseUrl, browsingContextId)`、`mount(...)`、`install(options)`、`listInstalledPackages(options)`、`uninstall(options)`
- F-051: `processMagics(code)` 方法：调用 `parse(code)`（来自 mambajs-core）解析魔法命令 → 遍历 commands 按类型 dispatch（`install`/`list`/`remove`）→ 返回 `run`（剥离魔法后的可执行代码）
- F-052: 受保护属性：`xkernel: any`、`xserver: any`、`logger: XeusWorkerLoggerBase`、`setKernelReady`

## 包 `@jupyterlite/xeus`（packages/xeus/）

- F-053: 包名 `@jupyterlite/xeus`，版本 `5.0.0`，描述 "JupyterLite Xeus kernels"
- F-054: 入口文件 `src/index.ts` 重新导出 `./kernel` 和 `./worker`
- F-055: 依赖：`@emscripten-forge/mambajs@^0.21.4`、`@jupyterlab/coreutils@^6.5.0`、`@jupyterlab/services@^7.5.0`、`@jupyterlite/services@^0.7.0 || ^0.8.0`、`@jupyterlite/xeus-core@^5.0.0`、`@lumino/coreutils@^2`、`@lumino/signaling@^2`、`coincident@^1.2.3`、`comlink@^4.4.1`
- F-056: 构建脚本：`build:lib` 使用 `tsc --sourceMap`，`build:worker` 使用 `webpack --config worker.webpack.config.js`

### WebWorkerKernel 类（packages/xeus/src/kernel.ts）

- F-057: `WebWorkerKernel` 继承自 `WebWorkerKernelBase`，定义在第21行
- F-058: `initWorker(options)` 方法：`crossOriginIsolated` 为 true 时创建 `new Worker('./coincident.worker.js', {type:'module'})`，否则创建 `new Worker('./comlink.worker.js', {type:'module'})`
- F-059: `createRemote(options)` 方法：为 worker 添加 `message` 事件监听器调用 `this.processWorkerMessage(e.data)` → `crossOriginIsolated` 为 true 时使用 `coincident(this.worker)` 创建远程代理，并设置 `processDriveRequest`（通过 `DriveContentsProcessor.processDriveRequest`）、`processStdinRequest`（通过 `PromiseDelegate` 异步等待）、`globalThis.storeAsGlobal`（使用 `coincident.transfer` 传输对象）→ 否则使用 `comlink.wrap(this.worker)` 创建远程代理，并设置 `globalThis.storeAsGlobal`（使用 `comlink.transfer`）→ 无论哪种模式都设置 `globalThis.callGlobalReceiver` 调用远程方法
- F-060: `initRemote(options)` 方法（protected, override）：调用 `remoteKernel.initialize()` 传入 `baseUrl`（PageConfig）、`kernelId`（this.id）、`mountDrive`、`kernelSpec`、`browsingContextId`、`empackEnvMetaLink`（来自 options）
- F-061: `WebWorkerKernel.IOptions` 继承自 `WebWorkerKernelBase.IOptions`，新增可选字段 `empackEnvMetaLink?: string`

### 接口扩展（packages/xeus/src/interfaces.ts）

- F-062: `IEmpackXeusWorkerKernel` 继承自 `IXeusWorkerKernel`，声明 `initialize(options): Promise<void>`
- F-063: `IEmpackXeusWorkerKernel.IOptions` 继承自 `IXeusWorkerKernel.IOptions`，新增可选字段 `empackEnvMetaLink?: string`

### EmpackedXeusRemoteKernel 抽象类（packages/xeus/src/worker.ts）

- F-064: `EmpackedXeusRemoteKernel` 继承自 `XeusRemoteKernelBase`，定义在第43行
- F-065: 模块顶部定义 `fetchJson(url)` 异步函数：fetch URL，response.ok 检查，返回 `response.json()`
- F-066: 从 `@emscripten-forge/mambajs` 导入：`install`、`pipInstall`、`pipUninstall`、`remove`
- F-067: 从 `@emscripten-forge/mambajs-core` 导入类型：`ILock`、`IInstallationCommandOptions`、`IListCommandOptions`、`IUninstallationCommandOptions`；导入函数：`empackLockToMambajsLock`、`bootstrapEmpackPackedEnvironment`、`bootstrapPython`、`loadSharedLibs`、`showPackagesList`、`showPipPackagesList`、`updatePackagesInEmscriptenFS`
- F-068: `initializeModule(options)` 方法（async）：从 options 获取 `baseUrl, kernelSpec` → 拼接 `binaryJS = URLExt.join(baseUrl, kernelSpec.argv[0])`、`binaryWASM = binaryJS.replace('.js','.wasm')`、`binaryDATA = binaryJS.replace('.js','.data')`、`kernelRootUrl = URLExt.join(baseUrl, 'xeus', kernelSpec.envName)` → 从 `kernelSpec.metadata.shared` 获取 sharedLibs 字典 → 将 sharedLibs 的值和 `'lib/libxeus.so'` 加入 `_kernelSharedLibs` Set → 调用 `importScripts(binaryJS)` → 返回 `{ locateFile: (file) => {...} }` 对象
- F-069: `locateFile` 逻辑：sharedLibs 中的文件映射到 `kernelRootUrl/kernelSpec.name/file`；`libxeus.so` 映射到 `kernelRootUrl/file`；`.wasm` 文件映射到 binaryWASM；`.data` 文件映射到 binaryDATA；其他返回原文件名
- F-070: `initializeFileSystem(options)` 方法（async）：从 options 获取 `baseUrl, kernelSpec, empackEnvMetaLink` → 拼接 `kernelRootUrl = baseUrl/xeus/kernels/kernelSpec.dir` → `empackEnvMetaLocation = empackEnvMetaLink || kernelRootUrl` → 获取 `packagesJsonUrl = {empackEnvMetaLocation}/empack_env_meta.json` → fetch 获取 `empackEnvMeta`（IEmpackEnvMeta 类型）→ 调用 `empackLockToMambajsLock()` 将 empack 锁转换为 mambajs 锁 → 检查 `this.Module.FS` 是否存在 → 设置 `_prefix = empackEnvMeta.prefix` → 调用 `bootstrapEmpackPackedEnvironment()` 引导环境 → 保存返回的 `paths`、`pythonVersion`、`sharedLibs`
- F-071: `initializeInterpreter(options)` 方法（async）：如果 Module.FS 不存在则提前返回 → 如果 kernelSpec.name === 'xpython'，调用 `bootstrapPython({prefix, pythonVersion, Module})` → 如果 emscriptenMajorVersion < 4，调用 `loadSharedLibs({sharedLibs, prefix:'/', Module, logger})`
- F-072: `emscriptenMajorVersion` getter：遍历 `_lock.packages` 查找名为 `'emscripten-abi'` 的包，解析版本号主版本号；未找到时 fallback 为 0
- F-073: `install(options)` 方法（async, protected）：按 `options.type` 分支，`'conda'` 调用 `install(options.specs, this._lock, options.channels, this.logger)`，`'pip'` 调用 `pipInstall(options.specs, this._lock, this.logger)` → 调用 `_reloadPackagesInFS(env)`
- F-074: `uninstall(options)` 方法（async, protected）：按 type 分支，`'conda'` 调用 `remove()`，`'pip'` 调用 `pipUninstall()` → 调用 `_reloadPackagesInFS(env)`
- F-075: `listInstalledPackages(options)` 方法：`type === 'conda'` 调用 `showPackagesList({packages, pipPackages}, logger)`，否则调用 `showPipPackagesList(pipPackages, logger)`
- F-076: `_reloadPackagesInFS(newLock)` 方法（private）：保存当前工作目录 `pwd = Module.FS.cwd()` → `chdir('/')` → 调用 `updatePackagesInEmscriptenFS({newLock, oldLock, pythonVersion, Module, logger, paths})` → 更新 `_paths` → 过滤 `_sharedLibs` 排除已链接的内核共享库 → emscripten<4 时调用 `loadSharedLibs()` → 更新 `_lock = newLock` → finally 中 `chdir(pwd)` 恢复工作目录
- F-077: 私有属性：`_emscriptenVersion: number|undefined`、`_pythonVersion: number[]|undefined`、`_prefix: string`（初始''）、`_pkgRootUrl: string`（初始''）、`_sharedLibs: TSharedLibsMap`、`_kernelSharedLibs: Set<string>`（new Set）、`_lock: ILock`、`_paths = {}`

### XeusCoincidentKernel 类（packages/xeus/src/coincident.worker.ts）

- F-078: `SharedBufferContentsAPI` 继承自 `ContentsAPI`（来自 `@jupyterlite/services`），定义在第24行
- F-079: `SharedBufferContentsAPI.request(data)` 调用 `workerAPI.processDriveRequest(data)`（workerAPI 是 `coincident(self)` 的返回值）
- F-080: `XeusDriveFS` 继承自 `DriveFS`，`createAPI(options)` 返回 `new SharedBufferContentsAPI(options)`
- F-081: `XeusCoincidentKernel` 继承自 `EmpackedXeusRemoteKernel`，定义在第39行
- F-082: `mount(driveName, mountpoint, baseUrl, browsingContextId)` 方法：从 `globalThis.Module` 获取 `FS, PATH, ERRNO_CODES` → 如果 FS 不存在则返回 → 创建 `new XeusDriveFS({...})` → `FS.mkdir(mountpoint)` → `FS.mount(drive, {}, mountpoint)` → `FS.chdir(mountpoint)`
- F-083: `initializeStdin(baseUrl, browsingContextId)` 方法：设置 `globalThis.get_stdin = (inputRequest) => workerAPI.processStdinRequest(inputRequest)`
- F-084: `storeAsGlobal(object, name)` 方法：`globalThis[name] = object`
- F-085: `callGlobalReceiver(receiverName, methodName, ...args)` 方法：`globalThis[receiverName][methodName](...args)`
- F-086: 文件末尾创建 `const worker = new XeusCoincidentKernel()`，并将所有 worker 方法 bind 到 `workerAPI`（coincident(self)）上：`initialize`、`mount`、`ready`、`cd`、`isDir`、`processMessage`、`storeAsGlobal`、`callGlobalReceiver`

### XeusComlinkKernel 类（packages/xeus/src/comlink.worker.ts）

- F-087: `XeusComlinkKernel` 继承自 `EmpackedXeusRemoteKernel`，定义在第16行
- F-088: `mount(driveName, mountpoint, baseUrl, browsingContextId)` 方法：与 coincident 版本类似，但使用普通 `DriveFS`（非 XeusDriveFS）
- F-089: `storeAsGlobal(object, name)` 方法：console.log 存储信息，然后 `globalThis[name] = object`
- F-090: `callGlobalReceiver(receiverName, methodName, ...args)` 方法：与 coincident 版本相同
- F-091: `initializeStdin(baseUrl, browsingContextId)` 方法：设置 `globalThis.get_stdin = (inputRequest) => {...}`，内部使用**同步** `XMLHttpRequest`（`xhr.open('POST', url, false)`）POST 到 `{baseUrl}/api/stdin/kernel`，发送 `{browsingContextId, data: inputRequest}`，阻塞等待响应，解析 JSON 返回；catch 返回 `{error}` 对象
- F-092: 文件末尾创建 `const worker = new XeusComlinkKernel()`，调用 `expose(worker)`（comlink 的 expose 函数）

## 包 `@jupyterlite/xeus-extension`（packages/xeus-extension/）

- F-093: 包名 `@jupyterlite/xeus-extension`，版本 `5.0.0`，描述 "JupyterLite loader for Xeus kernels"
- F-094: 依赖：`@jupyterlab/application@^4.5.0`、`@jupyterlab/coreutils@^6.5.0`、`@jupyterlab/logconsole@^4.5.0`、`@jupyterlite/apputils@^0.7.0 || ^0.8.0`、`@jupyterlite/services@^0.7.0 || ^0.8.0`、`@jupyterlite/xeus@^5.0.0`、`@lumino/coreutils@^2`
- F-095: `jupyterlab` 配置：`extension: true`、`outputDir: ../../jupyterlite_xeus/labextension`、`webpackConfig: lab.webpack.config.js`、sharedPackages 配置 `@jupyterlite/apputils` 和 `@jupyterlite/services` 为 `bundled:false, singleton:true`
- F-096: 入口文件 `src/index.ts` 默认导出两个插件：`empackEnvMetaPlugin` 和 `kernelPlugin`

### tokens.ts（packages/xeus-extension/src/tokens.ts）

- F-097: `IEmpackEnvMetaFile` 接口声明 `getLink(kernelspec): Promise<string>` 方法
- F-098: `IEmpackEnvMetaFile` Token 使用 `new Token<IEmpackEnvMetaFile>('@jupyterlite/xeus:IEmpackEnvMetaFile')` 创建

### kernelPlugin（packages/xeus-extension/src/index.ts）

- F-099: `kernelPlugin` 是 `JupyterFrontEndPlugin<void>`，id 为 `'@jupyterlite/xeus-kernel:register'`，`autoStart: true`
- F-100: kernelPlugin requires `[IKernelSpecs]`，optionals `[IServiceWorkerManager, IEmpackEnvMetaFile, ILoggerRegistry]`
- F-101: activate 函数中：fetch `xeus/kernels.json` 获取 kernelList → 获取 `contentsManager = app.serviceManager.contents` → 检测重复 kernel 名称 → 遍历 kernelList：fetch 每个 kernel 的 `xeus/{env_name}/{kernel}/kernel.json` → 设置 `kernelspec.name/dir/envName` → 重名时修改 name 和 display_name → 解析 resources 为完整 URL → 调用 `kernelspecs.register({spec, create})`
- F-102: create 工厂函数：处理 name 中的空格（取空格前部分作为实际内核名）→ 确定 `mountDrive = !!(serviceWorker?.enabled || crossOriginIsolated)` → 获取 `empackEnvMetaLink`（通过 empackEnvMetaFile.getLink）→ 返回 `new WebWorkerKernel({...options, contentsManager, mountDrive, kernelSpec, empackEnvMetaLink, browsingContextId})`
- F-103: 注册完成后发射 `_specsChanged` 信号刷新 kernelspecs
- F-104: 如果 loggerRegistry 存在，创建 BroadcastChannel 监听 `/xeus-kernel-logs-broadcast`，将日志转发到对应 session path 的 JupyterLab logger

### empackEnvMetaPlugin（packages/xeus-extension/src/index.ts）

- F-105: `empackEnvMetaPlugin` 是 `JupyterFrontEndPlugin<IEmpackEnvMetaFile>`，id 为 `'@jupyterlite/xeus:empack-env-meta'`，`autoStart: true`，`provides: IEmpackEnvMetaFile`
- F-106: activate 返回对象 `{ getLink: async (kernelspec) => URLExt.join(PageConfig.getBaseUrl(), 'xeus/{envName}') }`

### 辅助函数

- F-107: `getJson(url)` 异步函数：使用 `URLExt.join(PageConfig.getBaseUrl(), url)` 构建完整 URL，fetch GET，response.ok 检查，返回 `response.json()`

## Python 端 - jupyterlite_xeus 包

### 常量（jupyterlite_xeus/constants.py）

- F-108: `DEFAULT_CHANNELS = ["https://prefix.dev/emscripten-forge-4x", "https://prefix.dev/conda-forge"]`
- F-109: `EXTENSION_NAME = "xeus"`
- F-110: `STATIC_DIR = Path("@jupyterlite") / EXTENSION_NAME / "static"`

### 入口（jupyterlite_xeus/__init__.py）

- F-111: 尝试从 `._version` 导入 `__version__`，失败时 fallback 为 `"dev"` 并发出 warning
- F-112: `_jupyter_labextension_paths()` 返回 `[{"src": "labextension", "dest": "@jupyterlite/xeus"}]`

### get_kernel_binaries 函数（jupyterlite_xeus/add_on.py）

- F-113: `get_kernel_binaries(path)` 函数：读取 `path/kernel.json` → 获取 `argv[0]` 作为 kernel_binary → 构造 `kernel_binary_js/.wasm/.data` 路径 → 如果 .js 和 .wasm 都存在返回三元组 `(js, wasm, data|None)`，否则发出 warning 返回 None

### ListLike 类（jupyterlite_xeus/add_on.py）

- F-114: `ListLike(List)` 继承自 traitlets.List，`from_string(self, s)` 返回 `[s]`

### XeusAddon 类（jupyterlite_xeus/add_on.py）

- F-115: `XeusAddon` 继承自 `FederatedExtensionAddon`（来自 `jupyterlite_core.addons.federated_extensions`），定义在第80行
- F-116: `__all__ = ["post_build"]`
- F-117: 配置 Traitlets：
  - `empack_config: Unicode`（allow_none=True）— empack 配置文件路径或URL
  - `environment_file: ListLike`（默认[]）— 环境文件路径列表
  - `prefix: ListLike`（默认[]）— wasm prefix 路径列表
  - `default_channels: ListLike`（默认[]）— conda channels
  - `mount_jupyterlite_content: Bool`（allow_none=True）— 是否挂载 jupyterlite 内容
  - `mounts: ListLike`（默认[]）— 挂载点列表，格式 `<host_path>:<mount_path>`
  - `package_url_factory: Callable`（allow_none=True）— 包下载URL工厂函数
- F-118: `__init__` 方法：调用 `super().__init__()`，设置 `self.xeus_output_dir = Path(self.manager.output_dir) / "xeus"`，创建 `TemporaryDirectory()` 作为 `self.cwd`，设置 `self.cwd_name = self.cwd.name`
- F-119: `post_build(self, manager)` 方法（generator）：
  - 如果未设置 environment_file，自动检测 `lite_dir/environment.yml` 或 `environment.yaml`
  - 检查 prefix 或 environment_file 至少设置一个
  - 初始化 `self.prefixes = {}`、`self.specs = {}`、`self.channels = {}`
  - 如果未设置 prefix：遍历 environment_file，调用 `create_prefix()` 创建前缀
  - 如果设置了 prefix：验证目录存在，提取 env_name，调用 `get_environment_specs()` 和 `get_environment_channels()`
  - 遍历 prefixes：调用 `copy_kernels_from_prefix()` 复制内核，调用 `copy_jupyterlab_extensions_from_prefix()` 复制扩展
  - 写入 `kernels.json` 文件到输出目录
- F-120: `get_environment_specs(self, prefix)` 方法：读取 `prefix/conda-meta/history` 文件，解析以 `# update specs:` 开头的行，使用 `ast.literal_eval()` 解析 specs 列表
- F-121: `get_environment_channels(self, prefix)` 方法：读取 `conda-meta/history`，解析 `# cmd:` 行，用 shlex.split 提取 `-c/--channel/--channel=` 参数；未找到时使用 default_channels，default_channels 也为空则抛出 RuntimeError
- F-122: `create_prefix(self, env_file: Path)` 方法：读取 YAML 环境文件 → 获取 env_name 和 dependencies → 分离 conda 包和 pip 包 → 调用 `create_conda_env_from_env_file()` 创建环境 → 返回 `(env_name, env_prefix)`
- F-123: `copy_kernels_from_prefix(self, env_name, prefix)` 方法（generator）：构造 `kernel_spec_path = prefix/share/jupyter/kernels` → 遍历子目录 → 调用 `get_kernel_binaries()` 获取二进制文件 → 收集 all_kernels → 调用 `copy_kernel()` 复制每个内核 → 复制 `lib/libxeus.so` 到输出 → 调用 `pack_prefix()` 打包环境
- F-124: `copy_kernel(self, env_name, prefix, kernel_dir, ...)` 方法（generator）：读取 kernel.json → 更新 argv[0] 路径为 `xeus/{env_name}/bin/{js_name}` → 查找 logo 文件（.jpg/.png/.svg）→ 复制 logo 文件 → 如果 kernelSpec.metadata.shared 存在，复制共享库文件 → 写入更新后的 kernel.json 到临时目录 → 复制 .js/.wasm/.data 二进制文件 → 复制 kernel.json 到最终位置
- F-125: `update_empack_meta(self, file_path, new_data)` 方法：读取现有 JSON（或空对象）→ update 新数据 → 写回文件
- F-126: `pack_prefix(self, env_name, prefix)` 方法（generator）：
  - 构造输出目录 `env_dir = xeus_output_dir/env_name`、`packages_dir = env_dir/kernel_packages`
  - 创建临时 out_path
  - 处理 empack_config（URL 则 requests.get，本地路径则 pkg_file_filter_from_yaml，默认使用 DEFAULT_CONFIG_PATH）
  - 设置 package_url_factory（如果存在）
  - 调用 `pack_env(env_prefix=prefix, relocate_prefix='/', outdir=out_path, use_cache=False, **pack_kwargs)`
  - 处理 mounts：验证格式 `<host>:<mount>`、mount_path 为绝对路径、不以 `/files` 开头 → 目录调用 `pack_directory()`、文件调用 `pack_file()` → 调用 `add_tarfile_to_env_meta()` 添加到环境元数据
  - 处理 mount_jupyterlite_content：如果启用或（唯一 app 是 voici 且未显式设置），打包 output_dir/files 目录到 `/files` 挂载点
  - 复制所有 .tar.gz 包到 packages_dir
  - 更新 empack_env_meta.json 添加 specs 和 channels，复制到 env_dir
- F-127: `copy_jupyterlab_extensions_from_prefix(self, prefix)` 方法（generator）：调用 `self.env_extensions(prefix/SHARE_LABEXTENSIONS)` 获取联邦扩展 → 遍历调用 `safe_copy_jupyterlab_extension()` → patch jupyterlite_json 添加 federated_extensions → patch all_federated_json 聚合设置
- F-128: `patch_federated_settings(self, manager, lab_extensions, all_federated_json)` 方法：收集所有扩展的 federated settings → 读取现有 JSON → 追加 settings → 写回
- F-129: `safe_copy_jupyterlab_extension(self, pkg_json)` 方法（generator）：获取包路径和 name → 收集所有非目录非sourcemap文件作为 file_dep → yield copy 任务
- F-130: `dedupe_federated_extensions(self, config)` 方法：按 name 去重 federated_extensions，保留最新版本

### create_conda_env.py（jupyterlite_xeus/create_conda_env.py）

- F-131: `MICROMAMBA_COMMAND = shutil.which("micromamba")`，`PLATFORM = "emscripten-wasm32"`
- F-132: `_extract_specs(env_location, env_data)` 函数：遍历 dependencies，字符串加入 specs，dict 类型的 pip 依赖加入 pip_dependencies（本地目录转换为绝对路径）
- F-133: `create_conda_env_from_env_file(root_prefix, env_file_content, env_file_location)` 函数：获取 env_name（默认"xeus-env"）、channels（默认 DEFAULT_CHANNELS）、调用 _extract_specs → 调用 create_conda_env_from_specs
- F-134: `create_conda_env_from_specs(env_name, root_prefix, specs, channels, pip_dependencies)` 函数：调用 `_create_conda_env_from_specs_impl()` → 如果有 pip_dependencies，调用 `_install_pip_dependencies()`
- F-135: `_create_conda_env_from_specs_impl(...)` 函数：创建 prefix_path 目录 → 构造 channels_args → 检查 MICROMAMBA_COMMAND 存在 → subprocess_run micromamba create，参数包括：`--yes`、`--no-pyc`、`--prefix`、`--relocate-prefix ""`、`--root-prefix`、`--platform=emscripten-wasm32`、channels、specs

### _pip.py（jupyterlite_xeus/_pip.py）

- F-136: `_get_python_version(prefix_path)` 函数：glob 查找 `conda-meta/python-3.*.json`，读取版本号返回 `"{major}.{minor}"`
- F-137: `_install_pip_dependencies(prefix_path, dependencies, log=None)` 函数：
  - 创建 TemporaryDirectory 作为 pkg_dir
  - 获取 python_version
  - subprocess_run `pip install --target {pkg_dir} --python-version {version} --no-deps --no-input --verbose *dependencies`
  - 遍历 pkg_dir 中的 .dist-info 目录
  - 读取 RECORD 文件（CSV 格式），解析所有文件路径
  - 判断每个文件是否在 site-packages 内（路径不以 `../../` 开头）
  - 将 RECORD 中的 `../../` 替换为 `../../../` 以修正路径深度
  - 检查非支持文件后缀（`.so/.a/.dylib/.lib/.exe.dll`），存在则抛出 RuntimeError
  - 将文件复制到目标路径（site-packages 或 prefix 根目录）
