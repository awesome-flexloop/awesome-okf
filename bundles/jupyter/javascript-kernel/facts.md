---
type: Facts
title: javascript-kernel 源码事实清单
description: R阶段产出：从零推测事实，每条事实指向具体源码位置
tags:
- facts
- source-code
- evidence
- verification
generated:
  by: agent:source-code-to-okf-wiki
  at: '2026-08-22T00:00:00+08:00'
status: stable
stale_after: 2027-08-22
sources:
- ../../../../../external/libs/jupyter/javascript-kernel/pyproject.toml
- ../../../../../external/libs/jupyter/javascript-kernel/package.json
- ../../../../../external/libs/jupyter/javascript-kernel/README.md
- ../../../../../external/libs/jupyter/javascript-kernel/setup.py
- ../../../../../external/libs/jupyter/javascript-kernel/lerna.json
- ../../../../../external/libs/jupyter/javascript-kernel/packages/javascript-kernel-extension/package.json
- ../../../../../external/libs/jupyter/javascript-kernel/packages/javascript-kernel-extension/src/declarations.d.ts
- ../../../../../external/libs/jupyter/javascript-kernel/packages/javascript-kernel-extension/src/index.ts
- ../../../../../external/libs/jupyter/javascript-kernel/packages/javascript-kernel-extension/tsconfig.json
- ../../../../../external/libs/jupyter/javascript-kernel/packages/javascript-kernel/package.json
- ../../../../../external/libs/jupyter/javascript-kernel/packages/javascript-kernel/src/comm/index.ts
- ../../../../../external/libs/jupyter/javascript-kernel/packages/javascript-kernel/src/comm/manager.ts
- ../../../../../external/libs/jupyter/javascript-kernel/packages/javascript-kernel/src/display.ts
- ../../../../../external/libs/jupyter/javascript-kernel/packages/javascript-kernel/src/errors.ts
- ../../../../../external/libs/jupyter/javascript-kernel/packages/javascript-kernel/src/executor.ts
- ../../../../../external/libs/jupyter/javascript-kernel/packages/javascript-kernel/src/index.ts
- ../../../../../external/libs/jupyter/javascript-kernel/packages/javascript-kernel/src/kernel.ts
- ../../../../../external/libs/jupyter/javascript-kernel/packages/javascript-kernel/src/runtime_backends.ts
- ../../../../../external/libs/jupyter/javascript-kernel/packages/javascript-kernel/src/runtime_evaluator.ts
- ../../../../../external/libs/jupyter/javascript-kernel/packages/javascript-kernel/src/runtime_protocol.ts
- ../../../../../external/libs/jupyter/javascript-kernel/packages/javascript-kernel/src/runtime_remote.ts
- ../../../../../external/libs/jupyter/javascript-kernel/packages/javascript-kernel/src/startup.ts
- ../../../../../external/libs/jupyter/javascript-kernel/packages/javascript-kernel/src/widgets/index.ts
- ../../../../../external/libs/jupyter/javascript-kernel/packages/javascript-kernel/src/widgets/version.ts
- ../../../../../external/libs/jupyter/javascript-kernel/packages/javascript-kernel/src/widgets/widget.ts
okf_version: '0.2'
---

# JavaScript Kernel 源码事实清单

> R阶段产出：零推测事实，每条事实指向具体源码位置。禁止出现"用于"/"目的是"/"设计为"等推断词。

## 项目元数据

- F-001: 包名 `@jupyterlite/javascript-kernel`，版本 `0.4.0-alpha.5`，描述 "JupyterLite - JavaScript Kernel"
- F-002: 包名 `@jupyterlite/javascript-kernel-extension`，版本 `0.4.0-alpha.5`，描述 "JupyterLite - JavaScript Kernel Extension"
- F-003: License 为 BSD-3-Clause，作者 JupyterLite Contributors
- F-004: 源码仓库地址 `https://github.com/jupyterlite/javascript-kernel`
- F-005: 核心包 `@jupyterlite/javascript-kernel` 入口 `lib/index.js`，类型入口 `lib/index.d.ts`
- F-006: 核心包运行时依赖：`@jupyterlab/coreutils ^6.6.0`、`@jupyterlab/nbformat ^4.6.0`、`@jupyterlite/services ^0.8.0`、`@lumino/coreutils ^2.2.2`、`@lumino/disposable ^2.1.5`、`astring ^1.9.0`、`comlink ^4.3.1`、`meriyah ^4.3.9`
- F-007: 扩展包运行时依赖：`@jupyterlab/application ^4.6.0`、`@jupyterlite/javascript-kernel ^0.4.0-alpha.5`、`@jupyterlite/services ^0.8.0`、`@lumino/disposable ^2.1.5`、`@lumino/signaling ^2.1.5`
- F-008: monorepo 包含两个包：`packages/javascript-kernel`（核心逻辑）和 `packages/javascript-kernel-extension`（JupyterLab 扩展注册）
- F-009: 要求 JupyterLite >= 0.3.0
- F-010: pip 包名 `jupyterlite-javascript-kernel`
- F-011: 核心包构建命令 `tsc -b`，测试框架 jest
- F-012: 扩展包配置了 `jupyterlab.extension: true` 和 `jupyterlite.liteExtension: true`

## 目录结构

- F-013: 核心包源码位于 `packages/javascript-kernel/src/`
- F-014: 核心包 src 目录文件列表：`kernel.ts`、`executor.ts`、`display.ts`、`errors.ts`、`runtime_protocol.ts`、`runtime_backends.ts`、`runtime_evaluator.ts`、`runtime_remote.ts`、`startup.ts`、`worker-runtime.ts`、`index.ts`
- F-015: 核心包 src 子目录：`comm/`（含 `index.ts`、`manager.ts`）、`widgets/`（含 18 个 widget 文件）
- F-016: 扩展包源码位于 `packages/javascript-kernel-extension/src/`，仅含 `index.ts` 和 `declarations.d.ts`

## 运行时模式与类型 `runtime_protocol.ts`

- F-017: `RuntimeMode` 类型定义为 `'iframe' | 'worker'`（L10）
- F-018: `RuntimeOutputMessage` 是联合类型，包含 9 种消息类型：`stream`、`input_request`、`display_data`、`update_display_data`、`clear_output`、`execute_result`、`execute_error`、`comm_open`、`comm_msg`、`comm_close`（L15-L72）
- F-019: `IRemoteRuntimeApi` 接口定义了 Comlink 远程 API 方法：`initialize`、`execute`、`preloadModule`、`registerCommTarget`、`unregisterCommTarget`、`complete`、`inspect`、`isComplete`、`handleCommOpen`、`handleCommMsg`、`handleCommClose`、`dispose`（L89-L138）

## 核心 Kernel 类 `kernel.ts`

- F-020: `JavaScriptKernel` 类继承 `BaseKernel` 并实现 `IKernel` 接口（L20）
- F-021: `JavaScriptKernel` 构造函数接受 `IOptions` 参数，包含 `runtime?: RuntimeMode`（默认 `'iframe'`）、`executorFactory?`、`startupExtensions?`（L26-L32）
- F-022: 构造函数中调用 `this.createBackend(this._runtimeMode)` 创建运行时后端（L31）
- F-023: `ready` 属性返回 `this._backend.ready`（L52-L54）
- F-024: `kernelInfoRequest()` 返回 implementation=`'JavaScript'`，language_info.name=`'javascript'`，file_extension=`'.js'`，mimetype=`'text/javascript'`，protocol_version=`'5.3'`（L66-L96）
- F-025: `executeRequest()` 委托给 `this._backend.execute(code, executionCount, parentHeader.msg_id)`（L101-L131）
- F-026: `completeRequest()` 委托给 `this._backend.complete(code, cursor_pos)`，异常时返回空 matches（L136-L151）
- F-027: `inspectRequest()` 委托给 `this._backend.inspect(code, cursor_pos, detail_level)`，异常时返回 found=false（L156-L174）
- F-028: `isCompleteRequest()` 委托给 `this._backend.isComplete(code)`，异常时返回 status='unknown'（L179-L190）
- F-029: `createBackend(mode)` 方法：mode='iframe' 时创建 `IFrameRuntimeBackend`，mode='worker' 时创建 `WorkerRuntimeBackend`
- F-030: `applyStartupExtension(extension)` 在 backend ready 后调用 extension.activate(context)
- F-031: `removeStartupExtension(extension)` 调用 extension.deactivate(context)（如果存在）
- F-032: `IOptions` 接口包含 `id`、`name`、`sendMessage`、`runtime?`、`executorFactory?`、`startupExtensions?`
- F-033: `IStartupExtension` 接口包含 `id: string`、`activate(context)`、`deactivate?(context)`
- F-034: dispose() 清理 `_comms`、`_backend`、`_runtimeReadyContext`、`_appliedStartupExtensions`（L37-L47）

## 运行时后端 `runtime_backends.ts`

- F-035: `IRuntimeBackend` 接口定义：`ready: Promise<void>`、`dispose()`、`execute()`、`complete()`、`inspect()`、`isComplete()`、`handleCommOpen()`、`handleCommMsg()`、`handleCommClose()`（L32-L71）
- F-036: `AbstractRuntimeBackend` 抽象类实现 `IRuntimeBackend`，通过 Comlink 代理调用远程 API（L79-L205）
- F-037: `AbstractRuntimeBackend` 所有方法先 `await this.ready` 再调用 `this._getRemote()` 上的对应方法（L92-L189）
- F-038: `IFrameRuntimeBackend` 继承 `AbstractRuntimeBackend`（L210）
- F-039: `IFrameRuntimeBackend` 构造函数中创建隐藏 `<div>` 容器和 `<iframe>`，iframe.srcdoc 为最简 HTML 文档（L255-L270）
- F-040: `IFrameRuntimeBackend._init()` 使用 `Comlink.windowEndpoint` 在主窗口和 iframe 之间建立双向通信（L318-L333）
- F-041: `IFrameRuntimeBackend` 通过 `createRemoteRuntimeApi(globalScope, executor)` 在主窗口暴露 API，iframe 端通过 Comlink.wrap 获取 remote 引用（L323-L333）
- F-042: `IFrameRuntimeBackend` 默认使用 `JavaScriptExecutor`，也支持自定义 `executorFactory`（L312-L314）
- F-043: `IFrameRuntimeBackend` 初始化完成后调用 `options.onReady?.(context)`，context 包含 iframe、container、globalScope、executor、execute、preloadModule、registerCommTarget、unregisterCommTarget（L356-L368）
- F-044: `IFrameRuntimeBackend.STARTUP_TIMEOUT_MS = 10000`（10秒超时）（L401）
- F-045: `IFrameRuntimeBackend` dispose 时释放 Comlink proxy、移除 iframe 和 container（L230-L250）
- F-046: `WorkerRuntimeBackend` 继承 `AbstractRuntimeBackend`（L441）
- F-047: `WorkerRuntimeBackend` 构造函数创建 `new Worker(new URL('./worker-runtime.js', import.meta.url), { type: 'module' })`（L454-L456）
- F-048: `WorkerRuntimeBackend` 通过 `Comlink.wrap<IRemoteRuntimeApi>(worker)` 获取远程 API（L474）
- F-049: `WorkerRuntimeBackend` 注册 worker.onerror 和 worker.onmessageerror 处理器（L458-L471）
- F-050: `WorkerRuntimeBackend.STARTUP_TIMEOUT_MS = 10000`（L560）
- F-051: `WorkerRuntimeBackend` dispose 时调用 `worker.terminate()`（L494）
- F-052: `resolveBaseUrl(baseUrl?)` 函数：优先使用传入参数，其次 `PageConfig.getBaseUrl()`，兜底返回 `'/'`（L621-L631）
- F-053: `withTimeout(promise, timeoutMs, errorMessage)` 为异步操作添加超时包装（L595-L616）

## Worker 入口 `worker-runtime.ts`

- F-054: `worker-runtime.ts` 仅 10 行：以 `self` 为 globalScope 调用 `createRemoteRuntimeApi(runtimeGlobal)`，通过 `Comlink.expose` 暴露（L8-L10）

## 远程 API 桥接 `runtime_remote.ts`

- F-055: `createRemoteRuntimeApi(globalScope, executor?)` 函数返回实现 `IRemoteRuntimeApi` 的对象（L14-L137）
- F-056: `createRemoteRuntimeApi` 内部使用 `ensureEvaluator()` 懒加载 `JavaScriptRuntimeEvaluator`（L20-L25）
- F-057: `initialize(options, onOutput)` 创建 `JavaScriptRuntimeEvaluator` 实例，传入 globalScope、executor 和 onOutput 回调（L37-L52）
- F-058: `makeCloneSafe(value)` 函数使用 `structuredClone` 或自定义 `sanitize` 函数确保 Comlink 传输安全（L142-L152）
- F-059: `sanitize(value, seen, depth)` 递归处理值：基本类型直接返回、bigint 转字符串、symbol/function 转 String、ArrayBuffer 保留、Error 转普通对象、数组递归、普通对象递归（检测循环引用，深度>8截断）（L157-L213）
- F-060: emitOutput 函数用 `Promise.resolve(callback(...)).catch()` 忽略输出回调失败，确保执行回复仍能 resolve（L27-L34）

## 运行时求值器 `runtime_evaluator.ts`

- F-061: `JavaScriptRuntimeEvaluator` 类构造函数接受 `IOptions`：`globalScope`、`onOutput`、`executor?`（L20-L31）
- F-062: 构造函数依次执行：创建 `CommManager`、`_setupWidgets()`、`_setupJupyterGlobal()`、`_setupDisplay()`、`_setupConsoleOverrides()`（L26-L30）
- F-063: `execute(code, executionCount, parentMessageId?)` 方法：调用 `executor.makeAsyncFromCode(code)` 生成异步函数，解析错误返回语法错误；运行时错误返回含堆栈的错误；成功时如果结果是 Widget 则 displayWidget，否则通过 getMimeBundle 生成 execute_result（L61-L115）
- F-064: `execute` 使用 `_withParentMessageId` 包裹执行，设置/恢复 CommManager 的 currentMessageId（L249-L260）
- F-065: `complete(code, cursorPos)` 委托给 `executor.completeRequest(code, cursorPos)`（L120-L133）
- F-066: `inspect(code, cursorPos, detailLevel)` 委托给 `executor.inspect(code, cursorPos, detailLevel)`（L138-L144）
- F-067: `isComplete(code)` 委托给 `executor.isComplete(code)`（L149-L151）
- F-068: `preloadModule(moduleName)` 调用 `executor.importModule(moduleName)`（L163-L165）
- F-069: `registerCommTarget(targetName, moduleName, exportName='default')` 动态 import 模块并注册 handler 到 CommManager（L170-L187）
- F-070: `_setupConsoleOverrides()` 重写 console.log/info/error/warn/debug/dir/trace/table，log/info/debug/dir/trace/table 输出到 stdout 流，error/warn 输出到 stderr 流（L295-L367）
- F-071: console 重写中 `toText(args)` 将参数通过 `executor.getMimeBundle(arg)` 转为 text/plain 后拼接（L312-L335）
- F-072: `_setupDisplay()` 在 globalScope 上安装 `display` 函数：Widget 实例调用 displayWidget，其他值通过 getMimeBundle 发送 display_data（L400-L419）
- F-073: `_setupWidgets()` 调用 `createWidgetClasses(this._commManager)` 创建运行时本地 widget 类（L437-L439）
- F-074: `_setupJupyterGlobal()` 在 globalScope 上安装 `Jupyter` 对象，包含 `comm: CommManager` 和 `widgets: widgetClasses`（L451-L463）
- F-075: dispose() 逆序恢复：console overrides、display、widgets、Jupyter global，最后 CommManager.dispose()（L36-L42）
- F-076: `_emitError(executionCount, error, includeStack)` 生成 execute_error 消息，includeStack=true 时用 cleanStackTrace 清理堆栈（L265-L290）

## 代码执行器 `executor.ts`

- F-077: `JavaScriptExecutor` 类构造函数接受 `globalScope: Record<string, any>` 和可选 `config?: ExecutorConfig`（L123-L126）
- F-078: `ExecutorConfig` 默认 magicImports 配置：`enabled: true`、`baseUrl: 'https://cdn.jsdelivr.net/'`、`enableAutoNpm: true`（L106-L110）
- F-079: `makeAsyncFromCode(code)` 方法：使用 meriyah 的 `parseScript(code, { ranges: true, module: true })` 解析 AST（L142-L145）
- F-080: `makeAsyncFromCode` 依次执行：`_addToGlobalScope(ast)` 处理顶层变量声明、`_handleLastStatement(code, ast)` 处理末尾表达式返回值、`_rewriteImportStatements(finalCode, ast)` 重写 import 语句（L148-L158）
- F-081: `makeAsyncFromCode` 最终组合代码通过 `_createScopedFunction` 创建 async function 工厂，以 globalScope 为 this 调用返回 asyncFunction（L160-L176）
- F-082: `_rewriteImportStatements` 将 ES import 转换为动态 `await import(url)` 调用，通过 `_transformImportSource` 将裸模块名转为 CDN URL
- F-083: `_transformImportSource(source)`：相对/绝对 URL 保持不变，裸模块名转为 `https://cdn.jsdelivr.net/npm/{source}/+esm`（magic imports 启用时）
- F-084: `importModule(source)` 通过 `_createScopedFunction('source', 'return import(source);')` 在 globalScope 上下文中动态 import（L298-L305）
- F-085: `getMimeBundle(value)` 方法支持丰富的 MIME 类型输出（L495-L663）
- F-086: getMimeBundle 处理：null/undefined、自定义 _toHtml/_toSvg/_toPng/_toJpeg/_toMime/inspect 方法、string（HTML 检测）、number/boolean、Symbol、BigInt（加n后缀）、function（显示函数名和源码）、Error（stack+JSON）、Date（ISO字符串）、RegExp、Map、Set、DOM元素（HTMLElement/Canvas等）、Array、TypedArray、Promise（显示pending）、普通对象（JSON+预览）
- F-087: HTML 字符串检测正则：`/^<(?:[a-zA-Z][a-zA-Z0-9-]*[\s/>]|!(?:DOCTYPE|--))/` 且 trim 后以 `>` 结尾（L517-L520）
- F-088: `completeRequest(code, cursorPos)` 多行补全：定位光标所在行，调用 `completeLine` 处理单行补全，计算 cursor_start 和 cursor_end（L745-L777）
- F-089: `completeLine(codeLine, globalScope)` 单行补全：解析 stopChars 和 expStopChars（`.]`），通过 `with(scope) { return expr; }` 求值根对象，收集原型链所有属性（L672-L736）
- F-090: `cleanStackTrace(error)` 清理堆栈：移除 makeAsyncFromCode/new Function/asyncFunction 等内部帧，保留含 eval 或 `<anonymous>` 的用户帧（L785-L822）
- F-091: `isComplete(code)` 通过 meriyah 解析检测代码完整性：解析成功返回 complete；遇到 "unexpected end of input"/"unterminated string" 等模式返回 incomplete 并建议缩进；其他语法错误返回 invalid（L831-L872）
- F-092: `inspect(code, cursorPos, detailLevel)` 提取光标处表达式，在 globalScope 中求值，构建 inspectionData，附加内置文档（L883-L934）
- F-093: `extractImports(code)` 使用 meriyah 解析 AST，提取所有 ImportDeclaration 信息（source、url、defaultImport、namespaceImport、namedImports）（L186-L233）
- F-094: `generateImportCode(imports)` 生成将 import 结果赋值到 globalThis 的代码字符串（L242-L293）
- F-095: `ICodeRegistry` 接口包含 `functions: Map<string, any>`、`variables: Map<string, any>`、`classes: Map<string, any>`、`statements: any[]`（L77-L86）
- F-096: `registerCode(code, registry)` 将代码中的 FunctionDeclaration、ClassDeclaration、VariableDeclaration（含解构）、ExpressionStatement 注册到 registry，ImportDeclaration 跳过（L327-L414）
- F-097: `generateCodeFromRegistry(registry)` 从 registry 生成去重代码，按 variables→classes→functions→statements 顺序，附加 globalThis 赋值（L424-L480）
- F-098: `_createScopedFunction(...args)` 使用 new Function 创建沙箱函数

## Display 辅助 `display.ts`

- F-099: `DisplayHelper` 类提供链式富媒体输出 API（L29-L243）
- F-100: DisplayHelper 方法：`html(content, metadata?)`、`svg(content, metadata?)`、`png(base64Content, metadata?)`、`jpeg(base64Content, metadata?)`、`text(content, metadata?)`、`markdown(content, metadata?)`、`latex(content, metadata?)`、`json(content, metadata?)`、`mime(mimeBundle, metadata?)`、`clear(options?)`、`display(id?)`（L89-L216）
- F-101: DisplayHelper 构造函数接受可选 `displayId?` 用于 update_display_data（L35-L37）
- F-102: DisplayHelper 在无 callback 时将结果存储在 `_result` 中供同步返回（L234-L236）

## Comm 通信 `comm/manager.ts`

- F-103: `IComm` 接口定义：`commId: string`、`targetName: string`、`send(data, metadata?, buffers?)`、`close(data?)`、`display()`、`onMsg`、`onClose`（L9-L25）
- F-104: `CommManager` 类管理 comm 生命周期（L39-L258）
- F-105: `CommManager.open(targetName, data?, metadata?, buffers?, commId?)` 方法：commId 默认 `crypto.randomUUID()`，发送 comm_open 消息，返回 IComm（L47-L70）
- F-106: `CommManager.registerTarget(targetName, handler)`/`unregisterTarget(targetName)`/`hasTarget(targetName)` 管理 comm target 处理器（L75-L91）
- F-107: `CommManager.registerWidget(commId, widget)`/`getWidget(commId)`/`unregisterWidget(commId)` 管理 widget 实例映射（L96-L112）
- F-108: `CommManager.handleCommOpen(commId, targetName, data, buffers?)` 查找 target handler，创建 comm 并调用 handler（L131-L147）
- F-109: `CommManager.handleCommMsg(commId, data, buffers?)` 调用对应 comm 的 onMsg 回调（L152-L159）
- F-110: `CommManager.handleCommClose(commId, data, buffers?)` 调用 onClose，移除 widget 和 comm（L164-L175）
- F-111: `CommManager.displayWidget(commId)` 发送 display_data 消息，MIME 类型为 `application/vnd.jupyter.widget-view+json`，version_major=2, version_minor=0（L180-L196）
- F-112: `CommManager.setCurrentMessageId(messageId)`/`getCurrentMessageId()` 追踪当前父消息 ID（L117-L126）
- F-113: IComm.send() 发送 comm_msg 消息；IComm.close() 发送 comm_close 消息并触发 onClose、移除 widget 和 comm；IComm.display() 调用 displayWidget（L218-L251）

## Widget 基类 `widgets/widget.ts`

- F-114: `Widget` 基类定义（L35），`DOMWidget` 继承 `Widget`
- F-115: Widget 静态属性：`modelName=''`、`viewName=''`、`modelModule=CONTROLS_MODULE`、`modelModuleVersion=CONTROLS_MODULE_VERSION`、`viewModule=CONTROLS_MODULE`、`viewModuleVersion=CONTROLS_MODULE_VERSION`（L36-L41）
- F-116: Widget 使用 `_defaultManager: CommManager | null` 静态属性，通过 `setDefaultManager(manager)` 设置（L43-L50）
- F-117: Widget 构造函数接受 `state?: Record<string, unknown>`，合并 `_defaults()`、传入 state 和 `_modelState(ctor)`（L52-L66）
- F-118: Widget 构造函数中通过 `manager.open('jupyter.widget', { state, buffer_paths: [] }, { version: WIDGET_PROTOCOL_VERSION })` 打开 comm（L70-L74）
- F-119: WIDGET_PROTOCOL_VERSION 从 `./version` 导入
- F-120: Widget 注册 `_comm.onMsg` 处理 update/custom 消息，`_comm.onClose` 处理关闭（L76-L83）
- F-121: `Widget.get(name)` 返回 `_state[name]`（L96-L98）
- F-122: `Widget.set(name, value)` 或 `Widget.set(state)` 更新状态，检测值变化后发送 comm_msg update，触发 `change:key` 和 `change` 事件（L103-L129）
- F-123: `Widget.on(event, callback)`/`Widget.off(event, callback)` 管理事件监听器（L139-L153）
- F-124: `Widget.observe(callback, names?)` ipywidgets 风格观察 API，names 为字符串或字符串数组，'*' 表示所有属性（L158-L165）
- F-125: `Widget.unobserve(callback, names?)` 移除观察回调（L170-L194）
- F-126: `Widget.commId` getter 返回 `this._comm.commId`（L199-L200）
- F-127: DOMWidget 添加 `layout` 属性（Layout 实例）和 DOM 相关的样式/标签属性
- F-128: Widget._handleMsg 处理 comm 消息：`method: 'update'` 更新状态并触发 change 事件；`method: 'custom'` 触发 custom 事件（L45-L57 in widget_button.ts 模式）

## Widget 注册表 `widgets/index.ts`

- F-129: `widgetClasses` 记录了 55 个 widget 类（L83-L140），包括：Widget、DOMWidget、Layout、Style、各种 Style 子类、IntSlider/FloatSlider 等数值控件、Checkbox/ToggleButton 等布尔控件、Dropdown/RadioButtons 等选择控件、Text/Textarea/Password 等字符串控件、Output、Button、ColorPicker、Box/HBox/VBox/GridBox、Accordion/Tab/Stack、Link/DirectionalLink
- F-130: `createWidgetClasses(manager)` 函数为每个 widget 类创建运行时绑定的子类（通过 `class extends cls {}`），设置类名，调用 `setDefaultManager(manager)`（L145-L155）
- F-131: createWidgetClasses 添加 `jslink(source, target)` 和 `jsdlink(source, target)` 辅助函数（L161-L164）

## Widget 实现示例

- F-132: `IntSlider` 继承 `_SliderBase`，modelName=`'IntSliderModel'`，viewName=`'IntSliderView'`，默认 readout_format=`'d'`（widget_int.ts L12-L29）
- F-133: `Button` 继承 `DOMWidget`，modelName=`'ButtonModel'`，viewName=`'ButtonView'`，有 `onClick(callback)` 方法（L22-L24），处理 `custom` 消息中 `event: 'click'` 触发 click 事件（L45-L57）
- F-134: `Output` 继承 `DOMWidget`，modelName=`'OutputModel'`，viewName=`'OutputView'`，使用 OUTPUT_MODULE/OUTPUT_MODULE_VERSION（widget_output.ts L12-L18）
- F-135: Output 方法：`appendStdout(text)`、`appendStderr(text)`、`appendDisplayData(data, metadata?)`、`clearOutput(options?)`、`capture(callback, options?)`（L46-L98）
- F-136: Output.capture() 支持三种调用形式：`capture(callback)`、`capture(callback, options)`、`capture(options?)` 返回装饰器函数（L69-L87）
- F-137: Output._captureWrapper 使用引用计数 `_captureDepth` 追踪嵌套捕获，支持 Promise（L103-L143）

## 错误处理 `errors.ts`

- F-138: `normalizeError(error, fallbackName='Error')` 函数处理跨 realm Error 对象（如 iframe 抛出的错误，instanceof Error 可能为 false）（L17-L39）
- F-139: normalizeError 检查 isErrorLike（有 name/message/stack 任一属性），保留 name/message/stack；否则将值转为字符串（L41-L55）

## 启动扩展注册 `startup.ts`

- F-140: `IJavaScriptKernelStartupRegistry` 接口定义：`startupExtensions: readonly IStartupExtension[]`、`registerStartupExtension(extension): IDisposable`（L12-L17）
- F-141: `IJavaScriptKernelStartupRegistry` Token 使用 `'@jupyterlite/javascript-kernel:IJavaScriptKernelStartupRegistry'` 作为标识（L22-L25）

## 扩展注册 `javascript-kernel-extension/src/index.ts`

- F-142: 扩展注册了三个 JupyterFrontEndPlugin：`startupExtensionsRegistry`、`kernelIFrame`、`kernelWorker`（L166-L209）
- F-143: `kernelIFrame` 插件 id=`'@jupyterlite/javascript-kernel-extension:kernel-iframe'`，注册 kernelspec name=`'javascript'`，display_name=`'JavaScript (IFrame)'`，runtime=`'iframe'`（L177-L188）
- F-144: `kernelWorker` 插件 id=`'@jupyterlite/javascript-kernel-extension:kernel-worker'`，注册 kernelspec name=`'javascript-worker'`，display_name=`'JavaScript (Web Worker)'`，runtime=`'worker'`（L193-L204）
- F-145: kernelspec 注册时 language=`'javascript'`，interrupt_mode=`'message'`，metadata 包含 runtime 字段（L42-L56）
- F-146: `JavaScriptKernelStartupRegistry` 实现 `IJavaScriptKernelStartupRegistry`，使用 `Private.startupExtensions` 数组存储扩展（L77-L124）
- F-147: registerStartupExtension 检测 id 重复抛出 Error；对已存在的 kernel 异步 applyStartupExtension；返回 DisposableDelegate 在 dispose 时移除扩展并调用 deactivate（L82-L123）
- F-148: `Private.kernelCreated` Signal 在 kernel 创建时触发，trackKernel 将 kernel 加入 Set 并应用已注册的 startup extensions，kernel disposed 时从 Set 移除（L126-L161）

## 包导出 `index.ts`

- F-149: 核心包 index.ts 导出：`./kernel`、`./executor`、`./display`、`./runtime_protocol`、`./runtime_backends`、`./runtime_evaluator`、`./comm`、`./widgets`、`./startup`（L4-L12）
