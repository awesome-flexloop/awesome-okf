---
type: Facts
title: cockle 源码事实清单
description: R阶段产出：从零推测事实，每条事实指向具体源码位置
tags:
- facts
- source-code
- evidence
- verification
- shell
- wasm
- browser
generated:
  by: agent:source-code-to-okf-wiki
  at: '2026-08-22T00:00:00+08:00'
status: stable
stale_after: 2027-08-22
sources:
- ../../../../../external/libs/jupyter/cockle/src/defs.ts
- ../../../../../external/libs/jupyter/cockle/src/shell.ts
- ../../../../../external/libs/jupyter/cockle/src/base_shell.ts
- ../../../../../external/libs/jupyter/cockle/src/shell_impl.ts
- ../../../../../external/libs/jupyter/cockle/src/parse.ts
- ../../../../../external/libs/jupyter/cockle/src/tokenize.ts
okf_version: '0.2'
---

# Cockle 源码事实清单

> R阶段产出：零推测事实，每条事实指向具体源码位置。禁止出现"用于"/"目的是"/"设计为"等推断词。

## 项目元数据

- F-001: 包名 `@jupyterlite/cockle`，版本 `1.8.0-a0`，描述 "In browser bash-like shell"（package.json L2-4）
- F-002: License 为 BSD-3-Clause，作者 Ian Thomas，主页 https://github.com/jupyterlite/cockle（package.json L6-7, L10）
- F-003: 入口文件 `lib/index.js`，类型入口 `lib/index.d.ts`（package.json L21-22）
- F-004: 运行时依赖：`@lumino/coreutils ^2.2.0`、`@lumino/disposable ^2.1.3`、`@lumino/signaling ^2.1.3`、`coincident ^4.1.1`、`comlink ^4.4.2`、`deepmerge-ts ^7.1.4`、`rimraf ^6.0.1`、`zod ^3.23.8`（package.json L36-45）
- F-005: 构建命令 `tsc && npm run build:copy-dts`（package.json L25-26）
- F-006: 发布文件包含 `lib/**/*.{d.ts,eot,gif,html,jpg,js,js.map,json,png,svg,wasm,woff2,ttf}`、`src/**/*.ts`、`src/**/*.d.ts`、`cockle-config-base.json`（package.json L15-20）
- F-007: README 描述为 "In-browser bash-like shell implemented in a combination of TypeScript and WebAssembly"（README.md L3）
- F-008: README 说明被用于 JupyterLite terminal extension（README.md L5）

## 目录结构

- F-009: 源码位于 `src/` 目录
- F-010: `src/` 包含以下顶层文件：`aliases.ts`、`ansi.ts`、`argument.ts`、`arguments.ts`、`base_shell.ts`、`base_shell_worker.ts`、`callback.ts`、`callback_internal.ts`、`coincident.worker.ts`、`coincident_shell_worker.ts`、`comlink.worker.ts`、`comlink_shell_worker.ts`、`command_line.ts`、`defs.ts`、`defs_internal.ts`、`download_tracker.ts`、`drive_fs.ts`、`environment.ts`、`error_exit_code.ts`、`exit_code.ts`、`external_command.ts`、`external_environment.ts`、`external_termios.ts`、`file_system.ts`、`history.ts`、`index.ts`、`parse.ts`、`service_worker.ts`、`service_worker_manager.ts`、`shell.ts`、`shell_impl.ts`、`shell_manager.ts`、`tab_complete.ts`、`tab_completer.ts`、`termios.ts`、`tokenize.ts`、`utils.ts`
- F-011: `src/` 包含子目录：`builtin/`、`buffered_io/`、`commands/`、`context/`、`io/`、`layout/`、`types/`、`tools/`
- F-012: `src/builtin/` 包含：`alias_command.ts`、`bool_commands.ts`、`builtin_command.ts`、`cd_command.ts`、`clear_command.ts`、`cockle_config_command.ts`、`exit_command.ts`、`export_command.ts`、`help_command.ts`、`history_command.ts`、`index.ts`、`unset_command.ts`、`which_command.ts`
- F-013: `src/commands/` 包含：`command_module.ts`、`command_module_cache.ts`、`command_module_loader.ts`、`command_package.ts`、`command_registry.ts`、`command_runner.ts`、`command_type.ts`、`dynamically_loaded_command_runner.ts`、`external_command_runner.ts`、`index.ts`、`javascript_command_runner.ts`、`wasm_command_runner.ts`
- F-014: `src/io/` 包含：`buffered_output.ts`、`console_output.ts`、`dummy_input.ts`、`dummy_output.ts`、`external_input.ts`、`external_output.ts`、`file_input.ts`、`file_output.ts`、`index.ts`、`input.ts`、`input_all.ts`、`javascript_input.ts`、`output.ts`、`pipe.ts`、`pipe_input.ts`、`redirect_output.ts`、`terminal_input.ts`、`terminal_output.ts`
- F-015: `src/buffered_io/` 包含：`defs.ts`、`index.ts`、`main_io.ts`、`sab.ts`、`service_worker_main_io.ts`、`service_worker_utils.ts`、`service_worker_worker_io.ts`、`shared_array_buffer_main_io.ts`、`shared_array_buffer_worker_io.ts`、`worker_io.ts`
- F-016: `src/context/` 包含：`external_context.ts`、`index.ts`、`javascript_context.ts`、`run_context.ts`、`stdin_context.ts`、`tab_complete.ts`
- F-017: `src/layout/` 包含：`index.ts`、`table.ts`
- F-018: `src/types/` 包含：`coincident.d.ts`、`javascript_module.ts`、`wasm_module.d.ts`

## 核心接口 IShell `src/defs.ts`

- F-100: `IShell` 接口继承 `IObservableDisposable`（L7）
- F-101: `IShell` 定义属性：`commandStateChanged: ISignal<this, IShell.ICommandStateChangedArgs>`（L11）
- F-102: `IShell` 定义方法：`exitCode(): Promise<number>`（L16）
- F-103: `IShell` 定义方法：`input(char: string): Promise<void>`（L21）
- F-104: `IShell` 定义属性：`ready: Promise<void>`（L26）
- F-105: `IShell` 定义方法重载：`setSize(size: ISize): Promise<void>` 和 `setSize(rows: number, columns: number): Promise<void>`（L33-34）
- F-106: `IShell` 定义属性：`shellId: string`（L39）
- F-107: `IShell` 定义属性：`size: ISize`（L44）
- F-108: `IShell` 定义方法：`start(): Promise<void>`（L49）
- F-109: `IShell` 定义方法：`themeChange(isDark?: boolean): void`（L56）
- F-110: `IShell.IOptions` 接口包含字段：`shellId?: string`、`color?: boolean`、`mountpoint?: string`、`cwd?: string`、`baseUrl: string`、`wasmBaseUrl: string`、`wasmUrlQueryParams?: IQueryParamsCallback`、`browsingContextId?: string`、`shellManager?: IShellManager`、`aliases?: Record<string, string>`、`environment?: Record<string, string | undefined>`、`externalCommands?: IExternalCommand.IOptions[]`、`initialDirectories?: string[]`、`initialFiles?: IShell.IFiles`、`outputCallback: IOutputCallback`（L60-142）
- F-111: `IShell.CommandState` 类型为 `'loading' | 'running' | 'finished'`（L146）
- F-112: `IShell.ICommandStateChangedArgs` 包含：`commandId: number`、`state: CommandState`、`name?: string`、`args?: string[]`、`exitCode?: number`（L148-177）
- F-113: `IShellManager` 接口定义方法：`handleStdin(request: IStdinRequest): Promise<IStdinReply>`、`registerShell(shellId: string, shell: IShell, handleStdin: IHandleStdin): void`、`shellIds(): string[]`（L180-184）

## Shell 类 `src/shell.ts`

- F-120: `Shell` 类继承 `BaseShell`（L7）
- F-121: `Shell` 构造函数接受 `IShell.IOptions` 参数，调用 `super(options)`（L13-15）
- F-122: `Shell.initWorker(options)` 为 protected override 方法（L20）
- F-123: `initWorker` 中当 `workerType === 'coincident'` 时创建 `new Worker(new URL('./coincident.worker.js', import.meta.url), { type: 'module' })`（L23-24）
- F-124: `initWorker` 中其他情况创建 `new Worker(new URL('./comlink.worker.js', import.meta.url), { type: 'module' })`（L25-27）

## BaseShell 抽象类 `src/base_shell.ts`

- F-130: `BaseShell` 抽象类实现 `IShell` 接口（L28）
- F-131: 构造函数中设置 `this._shellId = options.shellId ?? UUID.uuid4()`（L30）
- F-132: 构造函数中若 `options.shellManager !== undefined`，调用 `options.shellManager.registerShell(this._shellId, this, this._serviceWorkerHandleStdin.bind(this))`（L32-38）
- F-133: `createRemote` 方法接受 `IShell.IOptions & { worker: Worker }` 参数，返回 `ICoincidentShellWorker | IComlinkShellWorker`（L49-51）
- F-134: `createRemote` 中当 `workerType === 'coincident'` 时，直接在 worker 的 proxy 对象上设置回调方法（callExternalCommand、callExternalTabComplete、commandStateChangedCallback 等）（L53-74）
- F-135: `createRemote` 中当 workerType 为 comlink 时，调用 `wrap(worker)` 并通过 `remote.registerCallbacks(proxy(...), ...)` 注册回调（L76-91）
- F-136: `dispose()` 方法终止 worker、清理 downloadTracker、SAB IO、ServiceWorker IO、mainIO（L95-122）
- F-137: `exitCode()` 方法调用 `this._remote?.exitCode()`，默认返回 1（L128-130）
- F-138: `input(char)` 方法：如果 `_mainIO?.enabled` 则调用 `_mainIO.push(char)`，否则调用 `_remote!.input(char)`（L180-190）
- F-139: `ready` 属性返回 `this._ready.promise`（L199-201）
- F-140: `start()` 方法先 `await this.ready`，再 `await this._remote!.start()`（L230-237）
- F-141: `useCoincidentWorker()` protected 方法返回 `crossOriginIsolated`（L245-247）
- F-142: `workerType` getter：当 `_workerType === undefined` 时根据 `useCoincidentWorker()` 设置为 `'coincident'` 或 `'comlink'`（L249-254）
- F-143: `_initialize` 方法中检测 `window.crossOriginIsolated`，若支持则创建 `SharedArrayBufferMainIO`（L374-377）
- F-144: `_initialize` 方法中若 `options.browsingContextId !== undefined`，创建 `ServiceWorkerMainIO` 并测试其可用性（1秒超时）（L380-399）
- F-145: 若 SAB 和 ServiceWorker 都不可用，输出错误消息并 dispose（L401-410）
- F-146: `_mainIO` 优先使用 `_sharedArrayBufferMainIO`，否则使用 `_serviceWorkerMainIO`（L412）
- F-147: `_initialize` 中 coincident 模式下使用 `coincident()` 修补 Worker（L417-422）
- F-148: `_callExternalCommand` 方法创建 ExternalEnvironment、ExternalInput、ExternalOutput、ExternalTermios，组装 IExternalRunContext 调用 command（L259-300）
- F-149: `_downloadWasmModuleCallback` 方法在 start=true 时创建 DownloadTracker 并 start，stop 时停止（L330-351）
- F-150: `_setMainIO(shortName)` 方法支持切换到 `'sab'` 或 `'sw'`，切换前禁用旧 IO（L460-473）

## ShellImpl 类 `src/shell_impl.ts`

- F-160: `ShellImpl` 类实现 `IShellImpl` 接口（L34）
- F-161: 构造函数接受 `IShellImpl.IOptions` 参数（L35）
- F-162: 构造函数中创建 `CommandModuleLoader`（L37-41）
- F-163: 构造函数初始化 `_fileSystem`，FS/PATH/ERRNO_CODES/PROXYFS 初始为 undefined，mountpoint 默认为 `'/drive'`（L44-50）
- F-164: 构造函数创建 `_runContext`，包含：commandId=-1、name=''、args=[]、fileSystem、Aliases、CommandRegistry、Environment、History、stdin/stdout/stderr 为 DummyInput/DummyOutput、size、termios、workerIO、workerType、commandModuleCache、stdinContext（L55-79）
- F-165: 构造函数中遍历 externalCommandConfigs 调用 `commandRegistry.registerExternalCommand`（L82-84）
- F-166: 构造函数创建 `_stderr: TerminalOutput`，color 模式下使用 ansi.styleRed/styleReset（L86-90）
- F-167: 构造函数创建 `_tabCompleter: TabCompleter`（L92-96）
- F-168: `initialize()` 方法依次调用 `_initWasmPackages()`、设置 aliases、设置 environment、调用 `_initFileSystem()`（L165-182）
- F-169: `input(chars)` 方法处理键盘输入：回车(13)执行命令、退格(127)删除字符、Tab(9)补全、Escape(27)方向键导航、Ctrl-D(4)、普通字符插入（L184-246）
- F-170: 回车处理中：输出换行、获取命令文本、清空命令行、若有文本则 `_runCommands(cmdText)`、然后输出提示符（L198-208）
- F-171: 方向键上(A/1A)/下(B/1B)调用 `history.scrollCurrent()` 浏览历史命令（L314-328）
- F-172: 方向键左(D/1D)/右(C/1C)移动光标（L329-342）
- F-173: Delete(3~)删除光标后字符，Home(H)/End(F)移动光标到行首/行尾（L343-366）
- F-174: `_runCommands(cmdText)` 方法：处理 `!N` 历史引用、创建 TerminalInput/TerminalOutput、调用 `parse(cmdText, true, aliases)` 解析、遍历 Node 数组执行命令或管道（L649-713）
- F-175: 管道处理：创建 Pipe 连接多个命令，前一个命令的输出作为后一个的输入（L687-694）
- F-176: `_runCommand` 方法：获取 runner、处理重定向（>/>>/2>/2>>/<）、文件名通配符展开、设置 runContext 属性、发送 'loading' 状态、调用 runner.run()、发送 'finished' 状态（L715-776）
- F-177: 重定向处理：`>`/`>>` 创建 FileOutput（append 模式由第二个参数控制），`2>`/`2>>` 创建错误 FileOutput，`<` 创建 FileInput（L728-743）
- F-178: `_filenameExpansion` 方法处理 `*` 和 `?` 通配符，将通配符转为正则表达式匹配 FS.readdir 结果（L399-463）
- F-179: `_initWasmPackages()` 方法：fetch `cockle-config.json`、解析 packages、为每个包创建 CommandModule 和 CommandPackage、注册到 CommandRegistry、初始化 aliases 和 environment（L569-633）
- F-180: `_initFileSystem()` 方法：加载 `cockle_fs` WASM 模块、获取 FS/PATH/ERRNO_CODES/PROXYFS、创建 mountpoint 目录、调用 initDriveFSCallback、chdir 到 mountpoint、创建初始目录和文件、设置 PWD 环境变量（L515-567）
- F-181: `_outputPrompt()` 方法输出 `\n${this.environment.getPrompt()}`（L639-647）
- F-182: `_setExitCode(exitCode)` 设置 `_exitCode` 并设置环境变量 `?` 为退出码字符串（L802-805）
- F-183: `_handleThemeChange()` 方法：发送 OSC 11 序列查询终端背景色、解析 RGB 值、计算亮度确定暗色/亮色模式（L465-513）
- F-184: `_setDarkMode(darkMode)` 方法：设置 PS1 提示符颜色、设置/删除 COCKLE_DARK_MODE 环境变量（L778-800）
- F-185: `callExternalCommand` 使用 PromiseDelegate 分离外部命令启动和结束（L103-132）
- F-186: ThemeStatus 枚举：Ok=0, PendingChange=1, Changing=2（L842-846）

## 命令系统 `src/commands/`

- F-200: `ICommandRunner` 接口定义：`commandType: CommandType`、`moduleName: string`、`names(): string[]`、`packageName: string`、`run(context: IRunContext): Promise<number>`、可选 `tabComplete?(context: ITabCompleteContext): Promise<ITabCompleteResult>`（command_runner.ts L8-18）
- F-201: `CommandType` 枚举：None=0, Unknown=1<<0, Builtin=1<<1, External=1<<2, JavaScript=1<<3, Wasm=1<<4, All=Unknown|Builtin|External|JavaScript|Wasm（command_type.ts L4-12）
- F-202: `ExitCode` 常量：SUCCESS=0, GENERAL_ERROR=1, IMPROPER_USE=2, CANNOT_RUN_COMMAND=126, CANNOT_FIND_COMMAND=127（exit_code.ts L1-7）
- F-203: `CommandRegistry` 类构造函数接受 commandStateChangedCallback、callExternalCommand、callExternalTabComplete 三个参数，并调用 `registerBuiltinCommands(AllBuiltinCommands)`（command_registry.ts L13-20）
- F-204: `CommandRegistry.registerBuiltinCommands` 遍历 AllBuiltinCommands 导出，找到以 'Command' 结尾且不以 'Builtin' 开头的类，实例化后如果是 BuiltinCommand 子类则注册（L64-78）
- F-205: `CommandRegistry.get(name)` 返回 `_map.get(name) ?? null`（L56-58）
- F-206: `CommandRegistry.registerCommandPackage(commandPackage)` 将包注册到 commandPackageMap，并注册包中所有 module 的 runner（L80-86）
- F-207: `CommandRegistry.registerExternalCommand(name, hasTabComplete)` 创建 ExternalCommandRunner 注册到 _map（L88-100）
- F-208: 命令名校验正则 `/^[\w-]+$/`，无效名称 console.warn 不抛出错误（L120-126）
- F-209: `DynamicallyLoadedCommandRunner` 抽象类实现 ICommandRunner，包含懒加载的 `_runner: ICommandRunner | null`（dynamically_loaded_command_runner.ts）
- F-210: `WasmCommandRunner` 继承 DynamicallyLoadedCommandRunner，commandType 为 Wasm（wasm_command_runner.ts）
- F-211: `JavaScriptCommandRunner` 继承 DynamicallyLoadedCommandRunner，commandType 为 JavaScript（javascript_command_runner.ts）
- F-212: `ExternalCommandRunner` 直接实现 ICommandRunner，commandType 为 External，run 方法调用 callExternalCommand 回调（external_command_runner.ts）
- F-213: `CommandModule` 类包含 name、commands 列表、packageName、wasm 标志，runner 属性使用惰性初始化（command_module.ts）
- F-214: `CommandPackage` 类包含 name、version、build_string、channel、platform、wasm 标志、modules 数组（command_package.ts）
- F-215: `CommandModuleLoader` 类负责从 wasmBaseUrl 加载 WASM/JS 模块，维护 cache（command_module_loader.ts）

## 解析器 `src/parse.ts` 和 `src/tokenize.ts`

- F-220: `Node` 抽象类定义 `abstract lastToken(): [Token | null, boolean]`（parse.ts L9-12）
- F-221: `CommandNode` 继承 Node，包含 `name: Token`、`suffix: Token[]`、`redirects?: RedirectNode[]`（L14-32）
- F-222: `PipeNode` 继承 Node，包含 `commands: CommandNode[]`（至少2个命令）（L34-47）
- F-223: `RedirectNode` 继承 Node，包含 `token: Token`、`target: Token`（L49-60）
- F-224: `parse(source, throwErrors?, aliases?)` 函数调用 tokenize，按 `;&` 分隔命令，按 `|` 创建管道（L62-109）
- F-225: 解析支持重定向：`>`、`>>`、`2>`、`2>>`、`<`（L144-146）
- F-226: `Token` 类型包含 `offset: number` 和 `value: string`（tokenize.ts L7-11）
- F-227: `tokenize(source, throwErrors?, aliases?)` 函数创建 Tokenizer 实例并运行（L13-17）
- F-228: Tokenizer 内部 CharType 枚举：None, Delimiter, DoubleQuote, SingleQuote, Whitespace, Other（L19-26）
- F-229: 分隔符集合 `';|&|><'`（L4），空白字符 `' '`（L5）
- F-230: Tokenizer 支持别名展开：当当前 token 是命令名（tokens 为空或前一个 token 以 ;&| 结尾）时，通过 aliases.getRecursive(value) 获取别名值，替换源码后重新分词（L58-78）
- F-231: Tokenizer 特殊处理 `2>` 作为 stderr 重定向（L137-139）
- F-232: Tokenizer 支持单引号和双引号字符串，引号内内容作为一个 token（L90-127）

## 内置命令 `src/builtin/`

- F-240: `BuiltinCommand` 抽象类实现 ICommandRunner，commandType 返回 CommandType.Builtin，moduleName 返回 '<builtin>'，packageName 返回 ''（builtin_command.ts L6-17）
- F-241: BuiltinCommand.run(context) 检查 name 匹配，发送 'running' 状态，调用抽象方法 _run（L25-33）
- F-242: BuiltinCommand 定义抽象属性 `name: string` 和抽象方法 `_run(context): Promise<number>`（L23, L35）
- F-243: `AliasCommand`（alias）：别名管理命令（alias_command.ts）
- F-244: `CdCommand`（cd）：切换当前工作目录（cd_command.ts）
- F-245: `ClearCommand`（clear）：清屏（clear_command.ts）
- F-246: `CockleConfigCommand`（cockle-config）：配置管理（cockle_config_command.ts）
- F-247: `ExitCommand`（exit）：退出 shell（exit_command.ts）
- F-248: `ExportCommand`（export）：设置/导出环境变量（export_command.ts）
- F-249: `HelpCommand`（help）：显示帮助信息（help_command.ts）
- F-250: `HistoryCommand`（history）：显示命令历史（history_command.ts）
- F-251: `UnsetCommand`（unset）：删除环境变量（unset_command.ts）
- F-252: `WhichCommand`（which）：查找命令位置（which_command.ts）
- F-253: `BoolCommands` 包含 true/false 命令，返回 0/1 退出码（bool_commands.ts）

## IO 系统 `src/io/`

- F-260: `IInput` 接口定义方法：`read(maxChars: number | null): number[]`、`readAsync(maxChars: number | null, timeoutMs?: number): Promise<number[]>`、`pollInput(timeoutMs: number): number[]`、`atEof(): boolean`、`setRawMode?(rawMode: boolean): void`（input.ts）
- F-261: `IOutput` 接口定义方法：`write(text: string): void`、`flush(): void`、`canList(): boolean`、`list(): string[]`、`clone(): IOutput`（output.ts）
- F-262: `TerminalInput` 实现 IInput，接受 pollInput、read、readAsync 三个回调函数（terminal_input.ts）
- F-263: `TerminalOutput` 实现 IOutput，构造函数接受 outputCallback 和可选 prefix/suffix（terminal_output.ts）
- F-264: `FileInput` 实现 IInput，从 FS 读取文件内容（file_input.ts）
- F-265: `FileOutput` 实现 IOutput，将输出写入 FS 文件，支持 append 模式（file_output.ts）
- F-266: `Pipe` 实现 IInput 和 IOutput，使用缓冲区在命令间传递数据（pipe.ts）
- F-267: `DummyInput` 实现 IInput，read 返回空数组，atEof 返回 true（dummy_input.ts）
- F-268: `DummyOutput` 实现 IOutput，write/flush 为空操作（dummy_output.ts）
- F-269: `ExternalInput` 不继承 IInput，readAsync 返回 Promise<string>（external_input.ts）
- F-270: `ExternalOutput` 构造函数接受 write 回调和 isTerminal 标志（external_output.ts）
- F-271: `InputAll` 抽象类实现 IInput，read 方法每次读取一个字符（input_all.ts）
- F-272: `BufferedOutput` 抽象类实现 IOutput，维护内部缓冲区（buffered_output.ts）
- F-273: `RedirectOutput` 实现 IOutput，支持输出重定向（redirect_output.ts）
- F-274: `ConsoleOutput` 实现 IOutput，输出到 console（console_output.ts）

## Worker 通信层

- F-280: `BaseShellWorker` 抽象类实现 IShellWorker（base_shell_worker.ts L26）
- F-281: BaseShellWorker.initialize(options) 创建 StdinContext、ServiceWorkerWorkerIO/SharedArrayBufferWorkerIO、ShellImpl 实例并初始化（L27-94）
- F-282: BaseShellWorker 优先使用 SharedArrayBufferWorkerIO，其次 ServiceWorkerWorkerIO（L57）
- F-283: `ComlinkShellWorker` 继承 BaseShellWorker，initDriveFS 为空实现（comlink_shell_worker.ts L12-17）
- F-284: `CoincidentShellWorker` 继承 BaseShellWorker 并实现 IShellWorker，initProxy 方法将所有方法绑定到 proxy 对象（coincident_shell_worker.ts L12-44）
- F-285: `IComlinkShellWorker` 是 `Remote<IShellWorker>` 类型别名（comlink_shell_worker.ts L7）
- F-286: `ICoincidentShellWorker` 继承 IShellWorker 和 IWorkerCallbacks（coincident_shell_worker.ts L7）
- F-287: coincident.worker.ts 创建 CoincidentShellWorker 实例并通过 coincident 暴露
- F-288: comlink.worker.ts 创建 ComlinkShellWorker 实例并通过 Comlink.expose 暴露

## 缓冲 IO `src/buffered_io/`

- F-290: 缓冲 IO 支持两种后端：SharedArrayBuffer（SAB）和 Service Worker（SW）
- F-291: IMainIO 接口包含 enabled 属性、push/write、enable/disable、canEnable、testWithTimeout 等方法（defs.ts）
- F-292: IWorkerIO 接口包含 enabled 属性、read/readAsync/pollInput/write、enable/disable、canEnable 等方法（defs.ts）
- F-293: SharedArrayBufferMainIO 使用 SharedArrayBuffer 在主线程和 Worker 间同步传输数据
- F-294: ServiceWorkerMainIO 通过 Service Worker 中转 stdin 数据
- F-295: SAB 支持同步 stdin 读取（无需 Service Worker），需要 crossOriginIsolated 环境
- F-296: Service Worker 方式通过 fetch 事件拦截和消息传递实现 stdin

## 环境与别名

- F-300: `Environment` 类继承 `Map<string, string>`（environment.ts L8）
- F-301: Environment 构造函数设置默认变量：COCKLE_SHELL_ID、COCKLE_BROWSING_CONTEXT_ID、PS1、TERM=xterm-256color（color模式）、TERMINFO（L9-24）
- F-302: color 模式下 PS1 为绿色 `js-shell:` 提示符，非 color 模式为 `js-shell: `（L18-23）
- F-303: Environment.copyIntoCommand(target) 将所有环境变量复制到 target 对象（L29-33）
- F-304: Environment.setSize(size) 设置 LINES 和 COLUMNS 环境变量（L57-72）
- F-305: `Aliases` 类管理命令别名，支持 getRecursive 递归解析别名
- F-306: `History` 类管理命令历史，支持 scrollCurrent（上下键浏览）、add、at 方法
- F-307: `IFileSystem` 接口包含 FS、PATH、ERRNO_CODES、PROXYFS（any 类型）和 mountpoint: string（file_system.ts L1-7）

## 其他关键模块

- F-310: `Termios` 类管理终端设置，提供 setDefaultShell/setDefaultWasm/setRawMode 等方法
- F-311: `TabCompleter` 类实现 Tab 补全逻辑，支持命令名补全、文件名补全、外部命令补全
- F-312: `DownloadTracker` 类在 WASM 模块下载时显示进度条
- F-313: `ShellManager` 类管理多个 shell 实例和 Service Worker stdin 路由
- F-314: `ServiceWorkerManager` 类管理 Service Worker 注册和通信
- F-315: `ansi` 对象提供 ANSI 转义码：cursorLeft/cursorRight/eraseEndLine/eraseStartLine/styleRed/styleGreen/styleReset/styleBoldRed/styleBoldGreen/styleBrightRed 等
- F-316: `ExternalEnvironment` 类包装环境变量，追踪变更（changed 属性）
- F-317: `ExternalTermios` 类包装 termios 标志，通过回调同步到主线程
- F-318: IRunContext 接口包含 commandId/name/args/fileSystem/aliases/commandRegistry/environment/history/shellId/terminate/stdin/stdout/stderr/size/termios/workerIO/workerType/commandModuleCache/stdinContext（context/run_context.ts）
- F-319: IExternalCommand.IOptions 接口包含 name: string、command: 函数、tabComplete?: 函数（external_command.ts）
- F-320: callback.ts 定义 IOutputCallback/IInitDriveFSCallback/IQueryParamsCallback/ISize/ISizeCallback 接口
- F-321: layout/table.ts 提供终端表格格式化功能
- F-322: utils.ts 提供 delay、joinURL、stringFromCharCodes 等工具函数

## 命令类型支持（README）

- F-330: 支持 4 种命令类型：Builtin TypeScript commands、WebAssembly commands、JavaScript commands、External commands（README.md L11-25）
- F-331: Emscripten-forge 支持的 WASM 包：coreutils (cat/cp/echo/ls/mkdir/mv/rm/touch/uname/wc)、git2cpp (git)、grep、less、lua、nano、sed、tree、vim（README.md L31-39）
- F-332: cockle >= 1.4.0 使用 emscripten 4.0.9，对应 prefix.dev channel 为 emscripten-forge-4x（README.md L48-51）
- F-333: Demo 提供两种 Worker 模式：Comlink（端口 4500，无 CORS 头）和 Coincident（端口 4501，有 CORS 头）（README.md L81-83）
- F-334: Coincident Worker 支持 SharedArrayBuffer 和 Service Worker 同步 stdin；Comlink Worker 仅支持 Service Worker（README.md L86-89）
