---
type: spec
title: "myst-execute + thebe 源码事实清单"
---

# myst-execute + thebe 源码事实清单

> R阶段产出：编号事实清单 F-001~F-080，零推测纯客观描述

## 项目基本信息

- F-001: myst-execute 包名为 "myst-execute"，版本为 0.4.0（package.json 第3行）
- F-002: myst-execute 许可证为 MIT，描述为 "Execute MyST content with Jupyter"
- F-003: myst-execute 入口为 "./dist/index.js"（ESM），类型定义为 "./dist/index.d.ts"
- F-004: myst-execute 运行时依赖：@jupyterlab/services ^7.6.0、@jupyterlab/nbformat ^3.5.2、myst-cli-utils ^2.0.13、myst-common ^1.10.0、myst-frontmatter ^1.10.0、myst-spec ^0.0.5、unified ^10.1.2、unist-util-select ^4.0.3、vfile ^5.3.7
- F-005: thebe-core 包默认导出类：ThebeServer、ThebeSession、ThebeNotebook、ThebeCodeCell、ThebeMarkdownCell、PassiveCellRenderer
- F-006: thebe-core 重新导出：options、events、thebe/api、thebe/entrypoint、utils、manager、rendermime、types、config 模块全部导出
- F-007: thebe-lite 导出 startJupyterLiteServer 函数和 ThebeLiteGlobal 类型，在浏览器加载时自动挂载到 window.thebeLite
- F-008: thebe-react 导出：OutputAreaByRef、ThebeLoaderProvider、ThebeServerProvider、ThebeSessionProvider、ThebeRenderMimeRegistryProvider、hooks 模块
- F-009: thebe-react 提供 ThebeBundleLoaderProvider 用于通过 script 标签加载 thebe-core 和 thebe-lite 的 UMD bundle

## myst-execute 核心模块

- F-010: index.ts 导出 kernelExecutionTransform（unified 插件）、JupyterServerSettings 类型、findExistingJupyterServer、launchJupyterServer、NotebookExecutionCache、LegacyExecutionCache、LocalDiskCache、TieredExecutionCache、ICache、LocalExecutionCache 类型
- F-011: execute.ts 定义 computeExecutableNodes(kernel, nodes, opts) 异步函数，接收 IKernelConnection、ExecutableNode[]、VFile选项，返回 {results, errorOccurred}
- F-012: computeExecutableNodes 对每个可执行节点：若是 code block 调用 executeCodeCell，若是 inlineExpression 调用 evaluateInlineExpression
- F-013: executeCodeCell 遇到 error 状态且节点未标记 raises-exception 时，调用 fileError 报告错误并设置 errorOccurred=true 后 break 终止执行
- F-014: applyComputedOutputsToNodes(nodes, computedResult) 将执行结果应用到 MDAST 节点，code block 的 outputs 子节点设置 jupyter_data，inlineExpression 设置 result 属性
- F-015: getExecutableNodes(tree) 使用 unist-util-select 的 selectAll 选择 `block[kind=code]` 和 `inlineExpression` 节点，并过滤掉标记 skip-execution 的 code block
- F-016: kernel.ts 中 KERNEL_READY_TIMEOUT_MS = 10000（10秒），KERNEL_READY_ATTEMPTS = 3（最多重试3次）
- F-017: createKernelConnection(sessionManager, basePath, kernelspec, vfile, log) 创建 Jupyter Session 连接，路径使用正斜杠规范化（跨平台兼容）
- F-018: createKernelConnection 对 kernel.info 设置 10 秒超时竞态，超时后 shutdown 连接并重试，最多 3 次
- F-019: executeCodeCell(kernel, code) 调用 kernel.requestExecute({code, allow_stdin:false, stop_on_error:false})，通过 future.onIOPub 收集输出
- F-020: executeCodeCell 的 IOPub 处理：忽略 status/execute_input/clear_output；收集 stream/execute_result/error/display_data；处理 update_display_data 通过 display_id 更新已有输出
- F-021: evaluateInlineExpression(kernel, expr) 使用 kernel.requestExecute({code:'', user_expressions:{expr}}) 执行表达式，通过 future.onReply 获取结果
- F-022: types.ts 定义 ExecutableNode = CodeBlock | InlineExpression，CodeResult = {type:'code', responses:IOutput[]}，ExpressionResult = {type:'inlineExpression', response:IExpressionResult}
- F-023: types.ts 定义 DocumentExecutionResult = {context: Record<string,any>, results: ExecutionResult[]}

## myst-execute 缓存系统

- F-024: cache.ts 定义 ICache<T> 接口：test(key):boolean、get(key):T|undefined、set(key,result):void
- F-025: LocalDiskCache<T> 实现 ICache<T>，构造函数接收 cachePath 和 extension，使用 JSON 文件存储（mkdirSync 递归创建目录）
- F-026: LocalDiskCache._makeKeyPath(key) 返回 path.join(cachePath, `${key}${extension}`)
- F-027: LegacyExecutionCache 包装 LocalDiskCache，将旧格式 IOutput[]/IExpressionResult[] 转换为新的 DocumentExecutionResult 格式
- F-028: NotebookExecutionCache 将执行结果存储为 ipynb 格式（INotebookContent），通过 baseCache（ICache<INotebookContent>）委托存储
- F-029: NotebookExecutionCache.get() 将 notebook cells 的 outputs 和 metadata.mystResultType 转换为 DocumentExecutionResult
- F-030: NotebookExecutionCache.set() 将 ExecutionResult[] 转换为 nbformat 4.5 格式的 notebook 对象，code 结果存 outputs，inlineExpression 结果转 display_data/error 输出
- F-031: TieredExecutionCache 实现两级缓存：primary 读写，get 时优先 primary 回退 secondary，set 只写 primary
- F-032: transform.ts 的 buildCacheKey(kernelSpec, nodes, envVars) 使用 MD5 哈希：kernelspec.name + JSON.stringify(hashableItems) + 可选的环境变量哈希
- F-033: hashableItems 包含每个节点的 kind（block/inlineExpression）、content（代码/表达式文本）、raisesException 标志
- F-034: kernelExecutionTransform 是 unified Plugin，Options 包含 basePath、cache（IDocumentExecutionCache）、sessionFactory、frontmatter、ignoreCache、errorIsFatal、log
- F-035: kernelExecutionTransform 流程：获取可执行节点 → 检查 kernelspec 是否存在 → 构建缓存键 → 检查缓存 → 命中则直接应用 → 未命中则创建 SessionManager 和 Kernel 连接 → 执行 → 成功则写入缓存 → 应用结果 → finally 中 shutdown session

## myst-execute Jupyter 服务器管理

- F-036: manager.ts 定义 JupyterServerSettings = Partial<ServerConnection.ISettings> & {dispose?: ()=>void}
- F-037: findExistingJupyterServer(session) 通过 `python -m jupyter_server list --json` 列出运行中的服务器，按 PID 排序，通过 fetch 检测存活，返回第一个存活服务器的 {baseUrl, token}
- F-038: launchJupyterServer(contentPath, log) 使用 get-port 获取空闲端口，spawn `python -m jupyter_server --ServerApp.root_dir=contentPath --ServerApp.port=port --ServerApp.port_retries=0`
- F-039: launchJupyterServer 从 stderr 中正则匹配 `([^\s]*?)\?token=([^\s]*)` 提取服务器地址和 token，20秒超时
- F-040: launchJupyterServer 返回的 settings 包含 dispose 方法，调用 killProcessTree(proc) 终止服务器进程树

## myst-execute 工具函数

- F-041: utils.ts 中 isCodeBlock(node) 判断 node.type==='block' && node.kind===NotebookCell.code
- F-042: utils.ts 中 codeBlockRaisesException(node) 检查 node.data.tags 是否包含 NotebookCellTags.raisesException
- F-043: utils.ts 中 codeBlockSkipsExecution(node) 检查 node.data.tags 是否包含 NotebookCellTags.skipExecution
- F-044: utils.ts 中 isInlineExpression(node) 判断 node.type==='inlineExpression'

## thebe-core 配置系统

- F-045: config.ts 定义 Config 类，构造函数接收 CoreOptions，内部维护 _options（mathjaxUrl/mathjaxConfig）、_binderOptions、_savedSessions、_kernelOptions、_serverSettings、_events
- F-046: Config 默认 mathjaxUrl = 'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js'，mathjaxConfig = 'TeX-AMS_CHTML-full,Safe'
- F-047: options.ts 的 makeBinderOptions 默认值：repo='executablebooks/thebe-binder-base'、ref='HEAD'、binderUrl='https://mybinder.org'、repoProvider='github'
- F-048: options.ts 的 makeSavedSessionOptions 默认值：enabled=true、maxAge=86400、storagePrefix='thebe-binder'
- F-049: options.ts 的 makeKernelOptions 默认值：path='/'、kernelName='python'
- F-050: options.ts 的 makeServerSettings 默认值：baseUrl='http://localhost:8888'、token=shortId()（随机）、appendToken=true、wsUrl 自动从 http 转为 ws

## thebe-core 服务器连接

- F-051: server.ts 定义 ThebeServer 类，实现 ServerRuntime 和 ServerRestAPI 接口
- F-052: ThebeServer 构造函数生成短 ID，创建 ready Promise、EventEmitter，初始状态 _isDisposed=false
- F-053: ThebeServer.connectToJupyterServer() 流程：ping api/status → 创建 KernelManager → 创建 SessionManager → 等待 sessionManager.ready → resolve ready Promise
- F-054: ThebeServer.connectToJupyterLiteServer() 需要 window.thebeLite 存在，调用 window.thebeLite.startJupyterLiteServer(config) 获取 serviceManager
- F-055: ThebeServer.connectToServerViaBinder() 使用 EventSource 连接 Binder build URL，监听 SSE 事件：failed 时 reject，ready 时创建 KernelManager/SessionManager
- F-056: Binder 连接支持 saved sessions：检查 localStorage 中保存的服务器信息，若仍存活则直接复用
- F-057: ThebeServer.startNewSession(rendermime, kernelOptions) 等待 ready 后调用 sessionManager.startNew({name, path, type:'notebook', kernel:{name}})，返回 ThebeSession
- F-058: ThebeServer 实现 REST API 方法：getContents、duplicateFile、renameContents、uploadFile、createDirectory、getKernelSpecs
- F-059: ThebeServer 静态方法 status(serverSettings) 调用 ServerConnection.makeRequest 访问 `${baseUrl}api/status`

## thebe-core API 和入口

- F-060: thebe/api.ts 导出 connectToBinder(config)、connectToJupyter(config)、connectToJupyterLite(config)、makeEvents()、makeServer(config)、setupNotebookFromBlocks()、setupNotebookFromIpynb()
- F-061: thebe/api.ts 的 setupThebeCore() 将 coreModule 和 api 对象挂载到 window.thebeCore，包含 version
- F-062: thebe/entrypoint.ts 定义 JsApi 接口：makeEvents、makeConfiguration、makeServer、makeRenderMimeRegistry、connectToBinder、connectToJupyter、connectToJupyterLite、setupNotebookFromBlocks、setupNotebookFromIpynb
- F-063: entrypoint.ts 在浏览器环境中（typeof window !== 'undefined'）自动调用 setupThebeCore()

## thebe-core 类型系统

- F-064: types.ts 定义 CoreOptions 接口：mathjaxUrl?、mathjaxConfig?、binderOptions?、savedSessionOptions?、kernelOptions?、serverSettings?
- F-065: types.ts 定义 BinderOptions 接口：repo?、ref?、binderUrl?、repoProvider?（'git'|'github'|'gitlab'|'gist'|string）
- F-066: types.ts 定义 ServerSettings 接口：baseUrl?、token?、appendToken?、wsUrl?
- F-067: types.ts 定义 KernelOptions 接口：kernelName?、path?
- F-068: types.ts 定义 IThebeCell 接口：kind('code'|'markdown')、source、session、metadata、notebookId、isBusy、isAttached、tags、executionCount、attachSession、detachSession、execute、setAsBusy/Idle、initOutputs、reset
- F-069: types.ts 定义 ServerRuntime 接口：ready(Promise)、isReady、settings、shutdownSession、shutdownAllSessions
- F-070: types.ts 定义 ServerRestAPI 接口：getContents、duplicateFile、renameContents、uploadFile、createDirectory、getKernelSpecs

## thebe-lite（Pyodide 无服务器执行）

- F-071: thebe-lite 的 startJupyterLiteServer(config?) 是 async 函数，返回 ServiceManager
- F-072: startJupyterLiteServer 调用 PageConfig.setOption 配置 litePluginSettings（pipliteUrls 指向 @jupyterlite/pyodide-kernel-extension@0.4.7）
- F-073: startJupyterLiteServer 默认 enableMemoryStorage=true、settingsStorageDrivers=['memoryStorageDriver']
- F-074: startJupyterLiteServer 动态 import @jupyterlite/server-extension 和 @jupyterlite/pyodide-kernel-extension，创建 JupyterLiteServer 实例，注册插件，启动后返回 serviceManager
- F-075: thebe-lite 在 UMD bundle 加载时自动执行 setupThebeLite()，挂载到 window.thebeLite

## thebe-react（React 集成）

- F-076: ThebeLoaderProvider 是 React Context Provider，动态 import('thebe-core') 或通过 script 标签加载 thebe-core.min.js，提供 {core, error, loading, load}
- F-077: ThebeServerProvider 创建 Config 和 ThebeServer 实例，提供 {connecting, ready, config, events, server, error, connect, disconnect}，支持 useBinder/useJupyterLite/customConnectFn 三种连接方式
- F-078: ThebeSessionProvider 在 server ready 后自动 startNewSession，提供 {starting, ready, session, error, start, shutdown}
- F-079: hooks/notebook.ts 提供 useNotebook(name, fetchNotebook, opts?) 和 useNotebookFromSource(sourceCode, opts?) 两个 Hook，内部使用 useNotebookBase()
- F-080: useNotebookBase 提供 executeAll(options?)、executeSome(predicate, options?)、clear() 方法，以及 ready/attached/executing/executed/errors/notebook/refs 状态
