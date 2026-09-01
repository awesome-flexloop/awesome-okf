---
sources:
- ../../../../../external/libs/jupyter/plugin-playground/src/types.ts
- ../../../../../external/libs/jupyter/plugin-playground/src/transpiler.ts
- ../../../../../external/libs/jupyter/plugin-playground/src/loader.ts
- ../../../../../external/libs/jupyter/plugin-playground/src/resolver.ts
- ../../../../../external/libs/jupyter/plugin-playground/src/modules.ts
- ../../../../../external/libs/jupyter/plugin-playground/src/known-modules.ts
- ../../../../../external/libs/jupyter/plugin-playground/src/requirejs.ts
- ../../../../../external/libs/jupyter/plugin-playground/src/runtime-shared-modules.ts
- ../../../../../external/libs/jupyter/plugin-playground/src/contents.ts
- ../../../../../external/libs/jupyter/plugin-playground/src/command-completion.ts
- ../../../../../external/libs/jupyter/plugin-playground/src/index.ts
type: Facts
okf_version: '0.2'
title: plugin-playground 源码事实清单
generated: '2026-08-22'
tags:
- facts
---

# Plugin Playground 源码事实清单 (Facts)

> R阶段产出：所有事实均为可验证的源码客观描述，编号 F-xxx，禁止推断性表述。

## 项目元数据

F-001: package.json 中 name 字段为 "@jupyterlab/plugin-playground"，version 为 "1.0.0"
F-002: package.json 中 license 为 "BSD-3-Clause"，homepage 指向 "https://github.com/jupyterlab/plugin-playground"
F-003: package.json 中 main 入口为 "lib/index.js"，types 入口为 "lib/index.d.ts"，style 入口为 "style/index.css"
F-004: package.json 中 packageManager 为 "yarn@3.5.0"
F-005: package.json 中 jupyterlab.extension 为 true，outputDir 为 "jupyterlab_plugin_playground/labextension"，schemaDir 为 "schema"
F-006: package.json 中 jupyterlab.disabledExtensions 包含 "jupyterlab-tour:default-tours"
F-007: package.json 中 jupyterlab.sharedPackages 配置了 "jupyterlab-js-logs" 为 singleton: true
F-008: package.json 中 dependencies 包含 @jupyterlab/application ^4.5.5, @jupyterlab/apputils ^4.6.5, @jupyterlab/codemirror ^4.5.5, @jupyterlab/completer ^4.5.5, typescript ~5.5.4, requirejs ^2.3.6, semver ^7.7.4
F-009: 构建脚本: build:lib 使用 tsc，build:labextension 使用 "jupyter labextension build"，watch 使用 tsc -w + labextension watch

## 目录结构

F-010: src/ 目录包含以下 TypeScript/TSX 文件: archive.ts, command-completion.ts, contents.ts, dialogs.tsx, encoding.ts, errors.tsx, example-sidebar.tsx, export-template.ts, export-toolbar.tsx, icons.ts, index.ts, known-modules.ts, loaded-plugins-sidebar.tsx, loader.ts, modules.ts, raw-loader.d.ts, requirejs.ts, resolver.ts, runtime-shared-modules.ts, semver-functions.d.ts, share-link.ts, share-toolbar.tsx, share-via-link-controller.ts, share-via-link-utils.tsx, split-action.tsx, token-insertion.ts, token-sidebar.tsx, tour.ts, transpiler.ts, types.ts, wheel.ts
F-011: src/components/ 目录包含 url-load-hint.ts 组件

## 类型定义 (src/types.ts)

F-012: IModule 接口定义为 { [member: string]: IModuleMember }
F-013: IModuleMember 接口包含 _isModuleMember: boolean 属性

## 转译器 (src/transpiler.ts)

F-020: PluginTranspiler 类定义于 src/transpiler.ts
F-021: PluginTranspiler 构造函数接受 PluginTranspiler.IOptions 参数，其中 compilerOptions 必须包含 target: ts.ScriptTarget，且禁止设置 module 选项
F-022: PluginTranspiler.importFunctionName 只读属性值为 'require'
F-023: PluginTranspiler.transpile(code: string, requireDefaultExport: boolean, fileName?: string): string 方法使用 ts.transpileModule 进行转译
F-024: transpile 方法中 compilerOptions.module 强制设置为 ts.ModuleKind.CommonJS
F-025: transpile 方法的 transformers.before 在 requireDefaultExport=true 时包含 _requireDefaultExportTransformer()
F-026: transpile 方法的 transformers.after 包含 _awaitRequireTransformer() 和 _exportWrapperTransformer()
F-027: _exportWrapperTransformer 创建 exports 对象字面量，在源码末尾添加 return exports 语句，并将 'use strict' 语句置顶
F-028: _awaitRequireTransformer 将 require() 调用包装为 await require()
F-029: _requireDefaultExportTransformer 遍历 AST 查找 export default 语句，未找到时抛出 NoDefaultExportError
F-030: NoDefaultExportError 类继承自 Error，定义于 src/transpiler.ts

## 插件加载器 (src/loader.ts)

F-040: PluginLoader 类定义于 src/loader.ts
F-041: PluginLoader.IOptions 接口包含: transpiler: PluginTranspiler, importFunction, tokenMap: Map<string, Token<any>>, requirejs: IRequireJS, serviceManager: ServiceManager.IManager | null
F-042: PluginLoader.IResult 接口包含: plugins: IPlugin<any, any>[], code: string, transpiled: boolean, schemas: Record<string, string>, declaredStylePaths: string[]
F-043: PluginLoader 构造函数接受 PluginLoader.IOptions 参数并存储为 _options
F-044: PluginLoader.loadFile(code: string): Promise<IModule> 方法调用 transpiler.transpile(code, false) 并通过 _createAsyncFunctionModule 执行
F-045: PluginLoader.load(code: string, basePath: string | null): Promise<PluginLoader.IResult> 是主要加载方法
F-046: load() 方法首先尝试 transpiler.transpile(code, true)，若抛出 NoDefaultExportError 则回退到对象风格插件定义: 'use strict';\nreturn (${code})
F-047: load() 方法在 transpiled=true 时通过 _createAsyncFunctionModule 创建 AsyncFunction 执行模块，从 module.default 获取插件源
F-048: load() 方法在 transpiled=false 时通过 new Function('require','requirejs','define', body)(requirejs.require, requirejs.require, requirejs.define) 执行
F-049: _createAsyncFunctionModule 使用 AsyncFunction 构造函数，参数为 importFunctionName 和转译后的代码体
F-050: AsyncFunction 通过 Object.getPrototypeOf(async () => {}).constructor 获取
F-051: _resolvePlugins(pluginSource) 处理函数/数组/Promise 形式的插件源，返回 IPlugin<any, any>[]
F-052: _resolvePluginTokens(plugin) 将 plugin.requires 和 plugin.optional 中的字符串 token 名称通过 tokenMap 解析为 Token 实例
F-053: _discoverSchema(pluginPath, plugins) 方法查找插件的 JSON schema 文件，支持单插件和多插件场景
F-054: _discoverSchema 查找 package.json 中 jupyterlab.schemaDir 指定的目录，或 plugin.json 文件
F-055: 多插件场景下，schema 文件按插件 id 后缀命名（如 ":advanced" -> "advanced.json"）
F-056: _discoverDeclaredStyles(pluginPath) 方法从 package.json 的 style 字段发现声明的 CSS 文件路径
F-057: _packageJsonCandidates(pluginPath) 返回同级和上级目录的 package.json 路径候选
F-058: PluginLoadingError 类继承自 Error，包含 error: Error 和 partialResult 属性
F-059: isString 函数判断值是否为 string 或 String 实例

## 模块解析器 (src/resolver.ts)

F-060: ImportResolver 类定义于 src/resolver.ts
F-061: ImportResolver.IOptions 接口包含: loadKnownModule, tokenMap, requirejs, settings: ISettingRegistry.ISettings, serviceManager, dynamicLoader?, basePath
F-062: CDNPolicy 类型为 'awaiting-decision' | 'always-insecure' | 'never'
F-063: ImportResolver.resolve(module: string): Promise<Token<any> | IModule | IModuleMember> 方法按以下顺序解析模块: runtime module -> federated extension -> local file -> CDN AMD module
F-064: resolve 方法中 _resolveRuntimeModule 先调用 loadKnownModule，再尝试 loadSharedScopeModule
F-065: resolve 方法中 _resolveFederatedExtensionModule 通过 window._JUPYTERLAB[module].get('./extension') 加载联邦扩展模块
F-066: resolve 方法中 _resolveLocalFile 处理以 '.' 开头的相对路径导入，支持 .ts/.tsx/.js/.css 文件及 index 文件
F-067: resolve 方法中 _resolveAMDModule 通过 requirejs 从 CDN 加载 AMD 模块
F-068: _resolveLocalFile 中 .css 文件通过 _loadLocalStyle 注入 <style> 标签，.svg 文件返回 {__esModule: true, default: content}
F-069: _createTokenAwareModule 使用 Proxy 包装模块，在访问 module:prop 时优先从 tokenMap 查找 Token
F-070: _createTokenAwareModule 中访问 default 属性且目标模块无 default 时返回模块本身（合成默认导入）
F-071: _getCDNConsent 方法根据 settings.composite.allowCDN 设置决定是否允许 CDN 加载，首次需用户确认弹窗
F-072: askUserForCDNPolicy 函数弹出对话框让用户选择 Forbid/Abort/Allow
F-073: _packageNameForImportSpecifier 从导入路径解析包名，支持 @scope/name 格式
F-074: _requiredVersionForPackage 从最近的 package.json 的 dependencies/peerDependencies 中读取版本范围
F-075: _loadNearestPackageDependencyRanges 向上遍历目录查找最近的 package.json
F-076: _localImportCandidates 为本地导入生成路径候选：.ts/.tsx/.js/.css 及对应 index 文件
F-077: _loadLocalStyle 方法通过 _snapshotLocalStyle 保存快照、_ensureLocalStyleElement 创建/获取 style 元素、_rewriteRelativeCssImports 重写 CSS @import
F-078: _rewriteRelativeCssImports 使用正则替换 CSS 中相对路径的 @import 为 Jupyter files/ URL
F-079: rollbackLocalStyleMutations() 回滚本地样式变更到快照状态
F-080: commitLocalStyleMutations() 提交本地样式变更
F-081: ImportResolver._localCssStyles 为静态 Map<string, HTMLStyleElement>，存储路径对应的 style 元素
F-082: ImportResolver._localCssSnapshotStacks 为静态 Map，存储每个路径的快照栈
F-083: loadedLocalStylePaths 属性返回只读 Set<string>
F-084: dynamicLoader setter 设置 _options.dynamicLoader
F-085: handleImportError 函数调用 showDialog 显示导入错误对话框，使用 formatImportError 格式化

## 已知模块 (src/modules.ts)

F-090: KNOWN_MODULE_NAMES 为 ReadonlyArray<string>，包含约80个已知模块名
F-091: KNOWN_MODULE_NAMES 包含 @jupyterlab/* 系列（application, apputils, codemirror, completer, notebook, services, settingregistry 等）
F-092: KNOWN_MODULE_NAMES 包含 @lumino/* 系列（algorithm, application, commands, coreutils, disposable, signaling, widgets 等）
F-093: KNOWN_MODULE_NAMES 包含 react, react-dom, yjs, @codemirror/*, @lezer/*, @rjsf/utils 等
F-094: loadKnownModule(name: string): Promise<IModule | null> 函数使用 switch 语句动态 import() 对应模块
F-095: loadKnownModule 对未知模块返回 Promise.resolve(null)

## 模块注册与发现 (src/known-modules.ts)

F-100: IKnownModule 接口包含: name: string, load?: () => Promise<unknown>, urls?: {docHtml?, sourceHtml?, typeDocJson?, npmHtml?, packageJson?, homepageHtml?, repositoryHtml?}, description?, origin?
F-101: KNOWN_MODULES 为 Map<string, IKnownModule> 存储所有注册的已知模块
F-102: _coreRegistered 布尔标志防止重复注册核心模块
F-103: registerKnownModule(known: IKnownModule): void 注册/合并单个已知模块，URLs 会合并
F-104: registerKnownModules(knownModules) 批量注册已知模块
F-105: listKnownModules(): ReadonlyArray<IKnownModule> 返回按名称排序的已知模块数组
F-106: registerCoreKnownModules(): void 为 KNOWN_MODULE_NAMES 中每个模块注册，@jupyterlab/* 和 @lumino/* 包自动生成文档和仓库 URL
F-107: discoverFederatedKnownModules(options?: {force?}) 发现联邦扩展模块，防止重复发现
F-108: _discoverFederatedKnownModules 从 PageConfig.getOption('federated_extensions') 读取扩展列表，逐个 fetch package.json 注册
F-109: _federatedExtensionsFromPageConfig 解析 JSON 格式的 federated_extensions 配置
F-110: _sharedPackageNames 从 package.json 的 jupyterlab.sharedPackages 提取共享包名
F-111: _gitUrlToHttp 将 github:、git@、ssh://、git+、git: 等格式 URL 转换为 HTTP URL
F-112: _npmPackageUrl 生成 https://www.npmjs.com/package/{name}  URL

## RequireJS 隔离加载 (src/requirejs.ts)

F-120: IRequireJS 接口包含 readonly require: Require 和 readonly define: RequireDefine
F-121: loadInIsolated(source: string): Promise<IRequireJS> 在隐藏 iframe 中加载 require.js 源码以避免污染 window 对象
F-122: loadInIsolated 创建 iframe，设置 display:none，在 iframe.onload 中 eval(source)，提取 iframeWindow.require 和 iframeWindow.define
F-123: 注释指出不能移除 iframe（否则 require.js 的定时器无法工作）
F-124: RequireJSLoader 类包含 async load(): Promise<IRequireJS> 方法，调用 loadInIsolated(requireJsSource)
F-125: requireJsSource 通过 raw-loader 从 '../node_modules/requirejs/require.js' 导入

## 运行时共享模块 (src/runtime-shared-modules.ts)

F-130: loadSharedScopeModule(name: string, options?: {requiredVersion?}): Promise<IModule | null> 从 webpack/rspack 共享作用域加载模块
F-131: loadSharedScopeModule 调用 initializeDefaultShareScope() 初始化，collectSharedProviders 收集提供者，pickCompatibleSharedProvider 选择版本
F-132: initializeDefaultShareScope 调用 __webpack_require__.I('default') 初始化默认共享作用域
F-133: pickCompatibleSharedProvider 使用 semver 的 maxSatisfying 选择满足版本范围的最高版本，优先稳定版
F-134: normalizeRequiredVersionRange 处理 workspace:, npm:, file:, link:, github:, git+, git: 等版本前缀，使用 semver.validRange 验证
F-135: collectSharedProviders 从多个共享作用域收集提供者并合并
F-136: collectSharedScopes 从 __webpack_require__.S?.default、__webpack_share_scopes__?.default、window.__webpack_share_scopes__?.default 三个来源收集作用域
F-137: 共享模块提供者通过 provider.get() 获取模块工厂/模块，函数类型则调用获取模块

## 内容工具 (src/contents.ts)

F-140: ContentUtils 命名空间定义于 src/contents.ts
F-141: ContentUtils.normalizeContentsPath(path) 去除路径开头的斜杠
F-142: ContentUtils.isSafeRelativePath(path) 检查路径段不包含 '.'、'..'、'\0'
F-143: ContentUtils.contentsPathCandidates(path) 返回带/不带开头斜杠的两种路径候选（兼容 Jupyter Server 和 JupyterLite）
F-144: ContentUtils.getDirectoryModel(serviceManager, path) 获取目录模型，遍历路径候选
F-145: ContentUtils.getFileModel(serviceManager, path) 获取文件模型，支持 text/json/base64 格式
F-146: ContentUtils.fileModelToText(fileModel) 将文件模型转为文本，处理 base64 解码
F-147: ContentUtils.fileModelToBytes(fileModel) 将文件模型转为 Uint8Array
F-148: ContentUtils.ensureContentsDirectory(serviceManager, path) 递归创建目录
F-149: ContentUtils.readContentsFileAsText(serviceManager, path) 读取文件内容为文本
F-150: ContentUtils.copyValueToClipboard(value) 使用 navigator.clipboard 或 Clipboard.copyToSystem
F-151: ContentUtils.highlightEditorLines(editor, lines, timeoutMs?) 使用 CodeMirror StateField/StateEffect 实现行高亮，超时自动清除
F-152: LINE_CHANGE_DECORATION 使用 Decoration.line 创建行装饰
F-153: LINE_HIGHLIGHT_EFFECT 使用 StateEffect.define<{pos: number[]}> 定义高亮效果
F-154: LINE_CHANGE_STATE 使用 StateField.define 管理装饰状态
F-155: IDirectoryModel 类型为 Contents.IModel & {type: 'directory', content: Contents.IModel[]}
F-156: IFileModel 类型为 Contents.IModel & {type: 'file'|'notebook', content: unknown, format?}

## 错误处理 (src/errors.tsx)

F-160: formatErrorWithResult(error: Error, result: Omit<PluginLoader.IResult, 'plugins'>): JSX.Element 渲染错误信息和最终代码的 React 组件
F-161: formatImportError(error: Error, module: string): JSX.Element 渲染模块导入错误的 React 组件

## 命令补全 (src/command-completion.ts)

F-170: CommandCompletionProvider 类实现 ICompletionProvider 接口
F-171: CommandCompletionProvider.identifier = 'CompletionProvider:plugin-playground-commands'，rank = 1200，renderer = null
F-172: CommandCompletionProvider.isApplicable(context) 检查编辑器 MIME 类型是否匹配 typescript/javascript/jsx/tsx
F-173: CommandCompletionProvider.fetch(request, context) 提取命令查询并返回补全项
F-174: getCommandRecords(app) 返回所有非隐藏命令的 ICommandRecord 数组，按 id 排序
F-175: ICommandRecord 包含 id, label, caption 字段
F-176: getCommandArgumentDocumentation(app, commandId) 获取命令的 usage 和 args schema
F-177: getCommandArgumentCount(app, commandId) 获取命令参数数量
F-178: formatCommandDescription(record) 拼接 label 和 caption 为描述文本
F-179: Private.extractCommandQuery 使用正则匹配 commands.execute/label/caption 等方法调用中的命令 ID
F-180: Private.isHiddenCommand 判断命令 ID 是否以 '__internal:' 开头

## 主入口 (src/index.ts) - 命令注册

F-190: CommandIDs 命名空间定义命令 ID 常量: createNewFile, createNewFileWithAI, takeTour, loadCurrentAsExtension, exportAsExtension, shareViaLink, openJSImportExplorer, listTokens, listCommands, listExtensionExamples 等
F-191: IPluginPlayground 接口定义 registerKnownModule 和 shareViaLink 方法
F-192: IPluginPlayground Token 使用 '@jupyterlab/plugin-playground:IPluginPlayground' 作为标识符
F-193: PluginPlayground 类构造函数接收 app: JupyterFrontEnd, settingRegistry, commandPalette, editorTracker, fileBrowserFactory, launcher, documentManager, settings, requirejs, toolbarWidgetRegistry, logConsoleTracker
F-194: PluginPlayground 构造函数中调用 registerCoreKnownModules()
F-195: PLUGIN_TEMPLATE 常量为 hello world 插件模板字符串
F-196: EXTENSION_EXAMPLES_ROOT = 'extension-examples'
F-197: loadCurrentAsExtension 命令标签为 'Load Current File As Extension'，从当前编辑器获取文本并调用 _queuePluginLoad
F-198: exportAsExtension 命令支持 zip/wheel 格式导出
F-199: createNewFile 命令创建 .ts 文件并写入 PLUGIN_TEMPLATE，支持 cwd/path 参数
F-200: listTokens 命令返回可用 Token 列表，支持 query 参数过滤
F-201: listCommands 命令返回可用命令列表，支持 query 参数过滤
F-202: listExtensionExamples 命令返回扩展示例列表
F-203: 工具栏注册了三个 Editor 工具栏项: SHARE_LINK_TOOLBAR_ITEM, LOAD_AS_EXTENSION_TOOLBAR_ITEM, LOAD_ON_SAVE_TOGGLE_TOOLBAR_ITEM, EXPORT_EXTENSION_TOOLBAR_ITEM
F-204: editorTracker.widgetAdded 连接后监听 saveState 信号，保存完成时若启用"Run on save"则自动加载插件
F-205: 侧边栏创建三个面板: TokenSidebar (Extension Points)、ExampleSidebar (Extension Examples)、LoadedPluginsSidebar (Currently Loaded Plugins)
F-206: 侧边栏添加到 app.shell 的 'right' 区域，rank: 650
F-207: CommandCompletionProvider 注册到 ICompletionProviderManager
F-208: ARCHIVE_EXCLUDED_DIRECTORIES 排除 .git, .ipynb_checkpoints, __pycache__, node_modules
F-209: ARCHIVE_FILE_READ_CONCURRENCY = 8

## 主入口 (src/index.ts) - 插件激活

F-210: 默认导出 JupyterFrontEndPlugin 对象，id 为 '@jupyterlab/plugin-playground:plugin'
F-211: 插件 requires 包含: ISettingRegistry, ICommandPalette, IEditorTracker, IToolbarWidgetRegistry, ICompletionProviderManager
F-212: 插件 optional 包含: ILauncher, IFileBrowserFactory, IDocumentManager, IMainMenu, ILogConsoleTracker
F-213: 插件 autoStart 为 true
F-214: activate 函数创建 PluginPlayground 实例并返回 IPluginPlayground Token
F-215: 插件设置 schema 包含 allowCDN, requirejsCDN, loadOnSave, commandInsertDefaultMode 等配置项
