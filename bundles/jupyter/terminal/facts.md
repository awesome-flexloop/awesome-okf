---
sources:
- ../../../../../external/libs/jupyter/terminal/install.json
- ../../../../../external/libs/jupyter/terminal/deploy/jupyter-lite.json
- ../../../../../external/libs/jupyter/terminal/src/index.ts
- ../../../../../external/libs/jupyter/terminal/src/tokens.ts
- ../../../../../external/libs/jupyter/terminal/src/client.ts
- ../../../../../external/libs/jupyter/terminal/src/shell.ts
- ../../../../../external/libs/jupyter/terminal/jupyterlite_terminal/__init__.py
- ../../../../../external/libs/jupyter/terminal/jupyterlite_terminal/add_on.py
- ../../../../../external/libs/jupyter/terminal/rspack.config.js
- ../../../../../external/libs/jupyter/terminal/worker.rspack.config.js
type: Facts
okf_version: '0.2'
title: terminal 源码事实清单
generated: '2026-08-22'
tags:
- facts
---

# JupyterLite Terminal 源码事实清单

> R阶段产出：零推测事实，每条事实指向具体源码位置。禁止出现"用于"/"目的是"/"设计为"等推断词。

## 项目元数据

- F-001: npm包名 `@jupyterlite/terminal`，版本 `1.7.0-a0`，描述 "A terminal for JupyterLite"
- F-002: Python包名 `jupyterlite_terminal`，构建系统使用 hatchling + hatch-nodejs-version + jupyter-builder
- F-003: Python版本要求 `>=3.10`，支持 Python 3.10-3.14
- F-004: Python核心依赖：`jupyterlite-core>=0.7.0,<0.9.0,!=0.7.4,!=0.7.5`
- F-005: npm核心依赖：`@jupyterlab/apputils ^4.6.0`、`@jupyterlab/coreutils ^6.5.0`、`@jupyterlab/pluginmanager ^4.5.0`、`@jupyterlab/services ^7.5.0`、`@jupyterlab/settingregistry ^4.5.0`、`@jupyterlite/apputils ^0.7.0||^0.8.0`、`@jupyterlite/cockle ^1.8.0-a0`、`@jupyterlite/services ^0.7.0||^0.8.0`、`@lumino/coreutils ^2.2.1`、`@lumino/signaling ^2.1.4`、`coincident ^4.1.1`、`comlink ^4.4.2`、`mock-socket ^9.3.1`
- F-006: License 为 BSD-3-Clause，作者为 JupyterLite Contributors
- F-007: 源码仓库地址 `https://github.com/jupyterlite/terminal`
- F-008: Python entry-points组 `"jupyterlite.addon.v0"` 注册 `jupyterlite-terminal = "jupyterlite_terminal.add_on:TerminalAddon"`
- F-009: JupyterLab扩展配置：`"extension": true`，outputDir为 `jupyterlite_terminal/labextension`，webpackConfig为 `rspack.config.js`
- F-010: JupyterLab共享包配置（singleton）：`@jupyterlab/apputils`、`@jupyterlab/settingregistry`、`@jupyterlite/apputils`、`@jupyterlite/services`
- F-011: TypeScript编译目标 ES2022，模块系统 esnext，outDir为 `lib`，rootDir为 `src`，strict模式开启
- F-012: 构建产物入口 `lib/index.js`，类型声明 `lib/index.d.ts`，样式 `style/index.css`

## 包入口 `src/index.ts`

- F-013: 默认导出6个JupyterFrontEndPlugin插件数组：`terminalClientPlugin`、`terminalContentsPlugin`、`terminalManagerPlugin`、`terminalServiceWorkerPlugin`、`terminalThemeChangePlugin`、`terminalExecPlugin`
- F-014: 具名导出：`ILiteTerminalAPIClient`、`ITerminalShell`、`LiteTerminalAPIClient`、`TerminalShell`

## Token定义 `src/tokens.ts`

- F-015: `ILiteTerminalAPIClient` 是一个 Lumino Token，id为 `'@jupyterlite/terminal:client'`
- F-016: `ILiteTerminalAPIClient` 接口继承自 `Terminal.ITerminalAPIClient`（来自@jupyterlab/services）
- F-017: `ILiteTerminalAPIClient.browsingContextId: string` 属性——用于与Service Worker通信的标识符
- F-018: `ILiteTerminalAPIClient.contentsManager?: Contents.IManager` 属性——JupyterLite内容管理器，用于通过SharedArrayBuffer进行DriveFS请求
- F-019: `ILiteTerminalAPIClient.handleStdin(request: IStdinRequest): Promise<IStdinReply>` 方法——处理来自Service Worker的stdin请求
- F-020: `ILiteTerminalAPIClient.registerAlias(key: string, value: string): void` 方法——注册所有终端可用的别名，key已存在则覆盖
- F-021: `ILiteTerminalAPIClient.registerEnvironmentVariable(key: string, value: string | undefined): void` 方法——注册环境变量，value为undefined时删除已存在的key
- F-022: `ILiteTerminalAPIClient.registerExternalCommand(options: IExternalCommand.IOptions): void` 方法——注册外部命令
- F-023: `ILiteTerminalAPIClient.createHeadlessShell(options): Promise<IShell>` 方法——创建共享stdin路由/别名/环境变量/外部命令的无头shell，返回的shell已启动就绪
- F-024: `createHeadlessShell` 的options参数包含：`shellId: string`、`cwd?: string`、`environment?: {[key:string]:string|undefined}`、`outputCallback: IOutputCallback`、`readyTimeoutMs?: number`
- F-025: `ILiteTerminalAPIClient.terminalDisposed: ISignal<this, string>` 信号——终端关闭时发射，参数为终端name（即shellId）
- F-026: `ILiteTerminalAPIClient.themeChange(isDarkMode?: boolean): void` 方法——通知所有终端主题变更

## 插件1：terminalClientPlugin `src/index.ts`

- F-027: `terminalClientPlugin` 类型为 `ServiceManagerPlugin<Terminal.ITerminalAPIClient>`
- F-028: id为 `'@jupyterlite/terminal:client'`，autoStart: true，provides: ILiteTerminalAPIClient
- F-029: optional依赖：`IServerSettings`
- F-030: activate函数创建并返回 `new LiteTerminalAPIClient({ serverSettings: { ...ServerConnection.makeSettings(), ...serverSettings, WebSocket } })`，其中WebSocket来自mock-socket

## 插件2：terminalManagerPlugin `src/index.ts`

- F-031: `terminalManagerPlugin` 类型为 `ServiceManagerPlugin<Terminal.IManager>`
- F-032: id为 `'@jupyterlite/terminal:manager'`，autoStart: true，provides: ITerminalManager
- F-033: requires: `[ILiteTerminalAPIClient]`
- F-034: activate函数返回 `new TerminalManager({ terminalAPIClient, serverSettings: terminalAPIClient.serverSettings })`

## 插件3：terminalContentsPlugin `src/index.ts`

- F-035: `terminalContentsPlugin` 类型为 `JupyterFrontEndPlugin<void>`
- F-036: id为 `'@jupyterlite/terminal:contents'`，autoStart: true
- F-037: requires: `[ILiteTerminalAPIClient]`
- F-038: activate函数从app.serviceManager获取contentsManager，设置到 `liteTerminalAPIClient.contentsManager`

## 插件4：terminalServiceWorkerPlugin `src/index.ts`

- F-039: `terminalServiceWorkerPlugin` 类型为 `JupyterFrontEndPlugin<void>`
- F-040: id为 `'@jupyterlite/terminal:service-worker'`，autoStart: true
- F-041: requires: `[ILiteTerminalAPIClient]`，optional: `[IServiceWorkerManager]`
- F-042: activate函数在serviceWorkerManager存在时：设置 `browsingContextId`，通过 `serviceWorkerManager.registerStdinHandler('terminal', ...)` 注册stdin处理器，绑定到 `liteTerminalAPIClient.handleStdin`
- F-043: serviceWorkerManager不存在时输出console.warn: 'Service worker is not available for terminals'

## 插件5：terminalThemeChangePlugin `src/index.ts`

- F-044: `terminalThemeChangePlugin` 类型为 `JupyterFrontEndPlugin<void>`
- F-045: id为 `'@jupyterlite/terminal:theme-change'`，autoStart: true
- F-046: requires: `[ILiteTerminalAPIClient, ISettingRegistry]`，optional: `[IThemeManager]`
- F-047: 缓存 `terminalTheme` 变量跟踪当前终端主题
- F-048: 监听 `themeManager.themeChanged` 信号：当terminalTheme为'inherit'时，通过 `themeManager.isLight(changedArgs.newValue)` 判断是否暗色模式，调用 `liteTerminalAPIClient.themeChange(isDarkMode)`
- F-049: 通过 `settingRegistry.load('@jupyterlab/terminal-extension:plugin')` 加载终端设置，监听setting.changed信号，比较newTerminalTheme与缓存的terminalTheme，不同则调用themeChange()并更新缓存

## 核心类：LiteTerminalAPIClient `src/client.ts`

- F-050: `LiteTerminalAPIClient` 类实现 `ILiteTerminalAPIClient` 接口
- F-051: 构造函数接受 `options: { serverSettings?: ServerConnection.ISettings }`，默认值为空对象
- F-052: `serverSettings` 在构造函数中设置为 `options.serverSettings ?? ServerConnection.makeSettings()`
- F-053: `browsingContextId` setter：设置 `this._browsingContextId`
- F-054: `contentsManager` setter：设置 `this._contentsManager`
- F-055: `isAvailable: boolean` getter：读取 `PageConfig.getOption('terminalsAvailable')`，转为小写与'true'比较
- F-056: `handleStdin(request)` 方法：委托给 `Private.shellManager.handleStdin(request)`
- F-057: `startNew(options?: Terminal.ITerminal.IOptions): Promise<Terminal.IModel>` 方法
- F-058: `startNew` 中：name取 `options?.name ?? this._nextAvailableName()`
- F-059: `startNew` 中：从serverSettings获取 `{ baseUrl, wsUrl }`
- F-060: `startNew` 中：调用 `this.createShell()` 创建shell，参数包括：mountpoint='/drive'、cwd、baseUrl、wasmBaseUrl（`URLExt.join(baseUrl, 'extensions/@jupyterlite/terminal/static/wasm/')`）、browsingContextId、contentsManager、aliases、environment、externalCommands、shellId=name、shellManager=Private.shellManager、outputCallback
- F-061: `startNew` 中：outputCallback将shell输出包装为 `JSON.stringify(['stdout', text])` 通过 `shell.socket?.send(msg)` 发送
- F-062: `startNew` 中：shell创建后存入 `Private.shells.set(name, shell)`
- F-063: `startNew` 中：定义hook函数，socket连接时：设置shell.socket、监听message事件（解析JSON，处理'stdin'和'set_size'消息）、发送handshake `JSON.stringify(['setup'])`、调用 `shell.start()`
- F-064: 'stdin'消息处理：调用 `await shell.input(content[0] as string)`
- F-065: 'set_size'消息处理：从content提取rows和columns，调用 `await shell.setSize({ rows, columns })`
- F-066: `startNew` 中：创建 `new WebSocketServer(url)`（url为 `URLExt.join(wsUrl, 'terminals', 'websocket', name)`），监听connection事件调用hook
- F-067: `startNew` 中：shell.disposed信号连接到：调用 `this.shutdown(name)`、关闭wsServer、发射 `_terminalDisposed.emit(shell.shellId)`
- F-068: `startNew` 返回 `{ name }`
- F-069: `listRunning(): Promise<Terminal.IModel[]>` 返回 `this._models`
- F-070: `_models` getter：将Private.shells的keys映射为 `{ name }` 对象数组
- F-071: `registerAlias(key, value)`：如果 `_aliases` 未定义则初始化为空对象，设置 `this._aliases[key] = value`
- F-072: `registerEnvironmentVariable(key, value)`：如果 `_environment` 未定义则初始化为空对象，设置 `this._environment[key] = value`
- F-073: `registerExternalCommand(options)`：将options push到 `this._externalCommands` 数组
- F-074: `createHeadlessShell(options)` 方法
- F-075: `createHeadlessShell` 中：environment合并 `this._environment` 和 `options.environment`（后者覆盖前者）
- F-076: `createHeadlessShell` 中：调用 `this.createShell()` 创建shell，参数包含 `color: true`
- F-077: `createHeadlessShell` 中：使用Promise.race等待shell.ready和超时定时器（默认DEFAULT_READY_TIMEOUT_MS=30000ms），超时则reject并dispose shell
- F-078: `createHeadlessShell` 中：ready成功后调用 `await shell.start()`，返回shell
- F-079: `shutdown(name)` 方法：从Private.shells获取shell，存在则发送 `JSON.stringify(['disconnect'])`、关闭socket、从Map删除、调用 `shell.dispose()`
- F-080: `terminalDisposed` getter：返回 `this._terminalDisposed` Signal
- F-081: `themeChange(isDarkMode?)` 方法：遍历Private.shells中所有shell，调用 `shell.themeChange(isDarkMode)`
- F-082: `createShell(options): Promise<ITerminalShell>`：返回 `new TerminalShell(options)`（protected方法）
- F-083: `_nextAvailableName()`：从i=1开始递增，返回第一个不在Private.shells中的 `${i}` 字符串
- F-084: 私有字段：`_aliases?`、`_environment?`、`_browsingContextId?`、`_contentsManager?`、`_externalCommands: IExternalCommand.IOptions[] = []`、`_terminalDisposed = new Signal<this, string>(this)`
- F-085: Private命名空间：`shellManager: IShellManager = new ShellManager()`（来自@jupyterlite/cockle）、`shells = new Map<string, ITerminalShell>()`

## Shell类：TerminalShell `src/shell.ts`

- F-086: `ITerminalShell` 接口继承自 `IShell`（来自@jupyterlite/cockle），增加 `socket?: WebSocketClient` 属性
- F-087: `ITerminalShell.IOptions` 接口继承自 `IShell.IOptions`，增加 `contentsManager?: Contents.IManager`
- F-088: `TerminalShell` 类继承自 `BaseShell`（来自@jupyterlite/cockle）
- F-089: 构造函数接受 `ITerminalShell.IOptions`，调用 `super(options)`，保存 `this._contentsManager = options.contentsManager`
- F-090: `createRemote(options)` 方法（protected override）：先调用 `super.createRemote(options)` 获取remote
- F-091: `createRemote` 中：当 `this.workerType === 'coincident'` 时，为remote设置 `processDriveRequest` 方法，该方法懒初始化 `DriveContentsProcessor`（来自@jupyterlite/services），调用 `processDriveRequest(data)` 处理DriveFS请求
- F-092: `initWorker(options)` 方法（protected override）：根据 `this.workerType` 选择Worker——'coincident'时加载 `./coincident.worker.js`，否则加载 `./comlink.worker.js`，均使用 `new Worker(new URL(...), { type: 'module' })`
- F-093: 公共字段：`socket?: WebSocketClient`
- F-094: 私有字段：`_contentsManager`、`_contentsProcessor: DriveContentsProcessor | undefined`

## Worker：coincident.worker.ts

- F-095: 定义 `SharedBufferContentsAPI` 类，继承自 `ContentsAPI`（来自@jupyterlite/services）
- F-096: `SharedBufferContentsAPI.request<T>(data)` 方法：调用 `proxy.processDriveRequest(data)` 并强制类型转换返回
- F-097: 定义 `SharedArrayBufferFS` 类，继承自 `DriveFS`（来自@jupyterlite/services）
- F-098: `SharedArrayBufferFS.createAPI(options)` 方法：返回 `new SharedBufferContentsAPI(options)`
- F-099: `ICoincidentTerminalShellWorker` 接口继承自 `ICoincidentShellWorker`，增加 `processDriveRequest<T>(data): Promise<TDriveResponse<T>>` 方法
- F-100: `CoincidentTerminalShellWorker` 类继承自 `CoincidentShellWorker`（来自@jupyterlite/cockle）
- F-101: `initDriveFS(options)` 方法（protected override）：当mountpoint非空且baseUrl存在时，从fileSystem解构FS/ERRNO_CODES/PATH，创建SharedArrayBufferFS实例，调用 `FS.mount(driveFS, {}, mountpoint)` 挂载
- F-102: `initProxy(proxy)` 方法（override）：调用 `super.initProxy(proxy)`，设置 `worker.processDriveRequest = proxy.processDriveRequest.bind(proxy)`
- F-103: 模块顶层：`export const proxy = (await coincident()).proxy as ICoincidentTerminalShellWorker`
- F-104: 模块顶层：`export const worker = new CoincidentTerminalShellWorker()`，然后调用 `worker.initProxy(proxy)`

## Worker：comlink.worker.ts

- F-105: `ComlinkTerminalShellWorker` 类继承自 `ComlinkShellWorker`（来自@jupyterlite/cockle）
- F-106: `initDriveFS(options)` 方法（protected override）：当mountpoint非空、baseUrl存在、browsingContextId存在时，创建DriveFS实例（传入browsingContextId），调用 `FS.mount(driveFS, {}, mountpoint)` 挂载
- F-107: 模块顶层：`const worker = new ComlinkTerminalShellWorker()`，调用 `expose(worker)`（来自comlink库）

## Headless命令执行：exec.ts

- F-108: `DEFAULT_TIMEOUT_MS = 30000`（30秒默认超时）
- F-109: `ShellExecutionStatus` 类型：`'ok' | 'error' | 'timeout'`
- F-110: `IExecuteShellResult` 接口：`success: boolean`、`status: ShellExecutionStatus`、`output: string`、`exitCode: number | null`、`shellName: string`、`duration: number`、`message: string`
- F-111: `IShellListItem` 接口：`name: string`
- F-112: `COMMAND_IDS` 常量对象：`executeShell: '@jupyterlite/terminal:execute-shell'`、`startShell: '@jupyterlite/terminal:start-shell'`、`shutdownShell: '@jupyterlite/terminal:shutdown-shell'`、`listShells: '@jupyterlite/terminal:list-shells'`
- F-113: `IHeadlessSession` 接口：`shell: IShell`、`output: string`、`busy: boolean`、`timedOut: boolean`
- F-114: `HeadlessShellPool` 类管理无头shell会话
- F-115: `HeadlessShellPool` 构造函数接受 `ILiteTerminalAPIClient`，保存为 `_client`
- F-116: `HeadlessShellPool.create(options: {cwd?}): Promise<IHeadlessSession>`：生成name（`headless-${_nextId++}`），通过 `_client.createHeadlessShell()` 创建shell（PS1环境变量设为空字符串），outputCallback累积输出到局部变量output，返回session对象并存入_sessions Map
- F-117: 创建的shell设置environment: `{ PS1: '' }`（空提示符，保持输出干净）
- F-118: session对象包含getter output（闭包引用局部output变量）、shell引用、busy=false、timedOut=false
- F-119: shell.disposed信号连接到从_sessions中删除对应name
- F-120: `HeadlessShellPool.get(name)`：返回_sessions.get(name)
- F-121: `HeadlessShellPool.names()`：返回 `Array.from(_sessions.keys())`
- F-122: `HeadlessShellPool.shutdown(name)`：获取session，不存在则throw Error，从_sessions删除，调用session.shell.dispose()
- F-123: `cleanCapturedOutput(captured, code)` 函数：将\r\n替换为\n，去掉回显的命令行前缀（如果normalized以code+'\n'开头则slice掉）
- F-124: `runOnSession(session, code, timeout)` 异步函数
- F-125: `runOnSession` 中：command为 `code.trim().replace(/\r\n?/g, '\n')`，空command返回error结果
- F-126: `runOnSession` 中：session.timedOut为true时throw Error（超时后的shell不可复用）；session.busy为true时throw Error（不支持重叠命令）
- F-127: `runOnSession` 中：设置session.busy=true，记录startTime和startLen
- F-128: `runOnSession` 中：`inputDone = session.shell.input(command + '\r')`，与setTimeout使用Promise.race竞争
- F-129: `runOnSession` 中：超时则session.timedOut=true；否则通过 `session.shell.exitCode()` 获取exitCode
- F-130: `runOnSession` 中：output为 `cleanCapturedOutput(session.output.slice(startLen), command)`
- F-131: `runOnSession` 中：超时返回status='timeout'、success=false、exitCode=null；正常返回status根据exitCode为'ok'或'error'
- F-132: `registerCommands(commands, pool)` 函数注册4个命令到CommandRegistry
- F-133: execute-shell命令：label='Execute Shell'，参数code(required string)、shellName(optional string)、cwd(optional string)、timeout(optional number)
- F-134: execute-shell的execute函数：参数校验后，有shellName则复用现有session，否则创建新session（disposeAfter=true）；调用runOnSession，finally中如果disposeAfter则pool.shutdown
- F-135: start-shell命令：label='Start Headless Shell'，参数cwd(optional string)；创建session后返回 `{success: true, message, shellName}`
- F-136: shutdown-shell命令：label='Shutdown Headless Shell'，参数shellName(required string)；调用pool.shutdown后返回 `{success: true, message, shellName}`
- F-137: list-shells命令：label='List Headless Shells'，无参数；返回 `{success: true, shells, count, available: true}`
- F-138: `terminalExecPlugin`：JupyterFrontEndPlugin<void>，id='@jupyterlite/terminal:exec'，autoStart: true，requires: [ILiteTerminalAPIClient]
- F-139: terminalExecPlugin的activate：创建HeadlessShellPool，调用registerCommands注册命令

## Python端：jupyterlite_terminal/__init__.py

- F-140: 尝试从 `._version` 导入 `__version__`，失败则设置 `__version__ = "dev"` 并发出warnings.warn
- F-141: `__all__ = ["__version__", "_jupyter_labextension_paths"]`
- F-142: `_jupyter_labextension_paths()` 函数返回 `[{"src": "labextension", "dest": "@jupyterlite/terminal"}]`

## Python端：jupyterlite_terminal/add_on.py

- F-143: `TerminalAddon` 类继承自 `FederatedExtensionAddon`（来自jupyterlite_core.addons.federated_extensions）
- F-144: `__all__ = ["post_build"]`
- F-145: `post_build(self, manager)` 方法是生成器函数，yield dict格式的action
- F-146: post_build中：cockleTool路径为 `node_modules/@jupyterlite/cockle/lib/tools/prepare_wasm.js`
- F-147: post_build中：cockleTool不存在时，在 `.cockle_temp` 目录下执行 `npm install --no-save --prefix .cockle_temp @jupyterlite/cockle`
- F-148: post_build中：assetDir为 `output_dir/extensions/@jupyterlite/terminal/static/wasm`
- F-149: post_build中：执行 `node <cockleTool> --list <tempFilename>` 获取所需WASM文件列表
- F-150: post_build中：逐行读取临时文件，每两行一组（source路径和packageName），yield copy action将文件复制到assetDir/packageName/basename
- F-151: post_build中：最后删除临时文件

## 构建配置

- F-152: rspack.config.js（主构建）：设置 `optimization.realContentHash = false`，禁用realContentHash以避免worker文件中的hash-like字符串导致"circular hash dependency"错误
- F-153: worker.rspack.config.js（Worker构建）：两个entry——coincident.worker和comlink.worker，输出到lib目录，resolve.fallback设置fs/child_process/crypto为false
- F-154: Wheel共享数据：`jupyterlite_terminal/labextension` 映射到 `share/jupyter/labextensions/@jupyterlite/terminal`，`install.json` 映射到同目录
- F-155: hatch-jupyter-builder构建命令：`build:prod`（生产）/`install:extension`（开发），npm命令为jlpm
- F-156: ensured-targets：`jupyterlite_terminal/labextension/static/style.js` 和 `jupyterlite_terminal/labextension/package.json`

## 配置文件

- F-157: install.json：`{"packageManager": "python", "packageName": "jupyterlite_terminal", "uninstallInstructions": "..."}`
- F-158: deploy/jupyter-lite.json示例：设置 `"terminalsAvailable": true`
- F-159: 需要配置jupyter-lite.json中 `jupyter-config-data.terminalsAvailable = true` 才能启用终端
- F-160: SharedArrayBuffer模式需要服务器设置COOP/COEP头：`Cross-Origin-Embedder-Policy=require-corp` 和 `Cross-Origin-Opener-Policy=same-origin`

## 目录结构

- F-161: TypeScript源码目录结构：
  ```
  src/
  ├── __tests__/
  │   └── jupyterlite_terminal.spec.ts  # 单元测试（占位）
  ├── client.ts          # LiteTerminalAPIClient 核心类
  ├── coincident.d.ts    # coincident类型声明
  ├── coincident.worker.ts  # SAB模式Worker
  ├── comlink.worker.ts     # ServiceWorker模式Worker
  ├── exec.ts            # 无头shell命令执行插件
  ├── index.ts           # 插件入口与导出
  ├── shell.ts           # TerminalShell类
  └── tokens.ts          # ILiteTerminalAPIClient Token定义
  ```
- F-162: Python源码目录结构：
  ```
  jupyterlite_terminal/
  ├── __init__.py    # 包入口，版本与labextension路径
  └── add_on.py      # JupyterLite构建插件（WASM文件处理）
  ```
- F-163: 样式文件：style/index.css（仅@import base.css）、style/base.css
- F-164: 部署目录：deploy/（含jupyter-lite.json配置示例、cockle-config-in.json、contents/示例内容）
- F-165: UI测试目录：ui-tests/（Playwright测试，tests/下有command.spec.ts、exec.spec.ts、extension.spec.ts、fs.spec.ts、jupyterlite_terminal.spec.ts、lifetime.spec.ts）

## 命令与Shell能力（来自README和测试）

- F-166: 四个编程式命令的完整列表（见F-112）
- F-167: cockle shell支持管道符`|`、分号`;`、重定向`> >> 2> <`
- F-168: cockle shell不支持`&&`/`||`、命令替换`$(...)`/反引号、环境变量展开`$VAR`、文件描述符复制`2>&1`
- F-169: 通过 `cockle-config stdin` 命令可查看/设置stdin模式（sab/sw）
- F-170: 无头shell会话命名格式为 `headless-${id}`（id从1开始递增）
- F-171: 交互式终端命名格式为 `${i}`（i从1开始递增）
