# Pyodide Kernel 事实清单

> R阶段产出：零推测，纯代码事实。每个事实指向具体源码路径。

## 项目基本信息

- F-001: 项目名称为 `jupyterlite-pyodide-kernel`，定义于 `pyproject.toml` L9
- F-002: 版本号 `0.9.0a1`，定义于 `jupyterlite_pyodide_kernel/_version.py` L3 和 `packages/pyodide-kernel/py/pyodide-kernel/pyodide_kernel/__init__.py` L3
- F-003: 项目描述为 "Python kernel for JupyterLite powered by Pyodide"，定义于 `pyproject.toml` L12
- F-004: 许可证为 BSD-3-Clause，定义于 `pyproject.toml` L24
- F-005: 要求 Python >=3.10，定义于 `pyproject.toml` L26
- F-006: 核心依赖为 `jupyterlite-core >=0.9.0a0,<0.10.0` 和 `pkginfo`，定义于 `pyproject.toml` L39-42
- F-007: 可选依赖 `[lock]` 包含 `pyodide-lock[uv] >=0.1.3,<0.3.0`，定义于 `pyproject.toml` L60-62
- F-008: 默认 Pyodide 版本为 `314.0.4`，定义于 `jupyterlite_pyodide_kernel/constants.py` L34
- F-009: 默认 Pyodide CDN URL 为 `https://cdn.jsdelivr.net/pyodide/v314.0.4/full`，定义于 `constants.py` L63
- F-010: 浏览器端 Python 版本为 `3.14`，定义于 `constants.py` L37

## 目录结构

- F-011: 项目根目录包含 Python 包 `jupyterlite_pyodide_kernel/` 和 JS 工作空间 `packages/`
- F-012: `packages/` 目录包含两个 npm 包：`pyodide-kernel` 和 `pyodide-kernel-extension`
- F-013: `packages/pyodide-kernel/py/` 目录包含浏览器端运行的 Python 包：`pyodide-kernel`、`ipykernel`、`piplite`、`widgetsnbextension3`、`widgetsnbextension4`
- F-014: Python 构建后端为 hatchling，定义于 `pyproject.toml` L2-6
- F-015: JS 包管理器为 yarn 3.5.0，定义于根 `package.json` L145

## Python CLI 端（构建时 Addon）

- F-016: CLI 入口点 `jupyter-piplite` 指向 `jupyterlite_pyodide_kernel.app:main`，定义于 `pyproject.toml` L52
- F-017: JupyterLite addon 入口点注册了三个 addon：`PyodideLockAddon`、`PipliteAddon`、`PyodideAddon`，定义于 `pyproject.toml` L54-57
- F-018: `PyodideAddon` 类定义于 `addons/pyodide.py` L23，继承自 `_BaseAddon`
- F-019: `PyodideAddon.pyodide_url` 为 Unicode trait，可通过 CLI `--pyodide` 设置，定义于 `pyodide.py` L27-34
- F-020: `PyodideAddon` 的生命周期方法包括 `status`、`post_init`、`build`、`post_build`、`check`，定义于 `pyodide.py` L24
- F-021: `PyodideAddon.post_build` 将 pyodide URL 指向 `pyodide.mjs`（ES module），定义于 `pyodide.py` L118
- F-022: `PipliteAddon` 类定义于 `addons/piplite.py` L32，继承自 `_BaseAddon`
- F-023: `PipliteAddon.piplite_urls` 为 List trait，可通过 CLI `--piplite-wheels` 设置，定义于 `piplite.py` L36-43
- F-024: `PipliteAddon` 生成 Warehouse-like API 格式的 `all.json` wheel 索引，定义于 `piplite.py` L334-352
- F-025: `get_wheel_fileinfo` 函数生成包含 sha256/md5 摘要的 wheel 元数据，定义于 `piplite.py` L297-331
- F-026: `PyodideLockAddon` 类定义于 `addons/lock.py` L63，继承自 `_BaseAddon
- F-027: `PyodideLockAddon.enabled` 默认 False，通过 `--pyodide-lock` flag 启用，定义于 `lock.py` L89-92
- F-028: `PyodideLockAddon` 使用 `pyodide_lock.uv_pip_compile.UvPipCompile` 解析依赖，定义于 `lock.py` L389
- F-029: `PyodideLockAddon` 默认预取包为 `ipykernel`、`comm`、`pyodide-kernel`、`ipython`，定义于 `lock.py` L158-166
- F-030: `PyodideLockAddon` 默认排除包为 `jupyter-server`、`jupyterlab`、`notebook`，定义于 `lock.py` L126-134
- F-031: `_BaseAddon` 类定义于 `addons/_base.py` L31，继承自 `jupyterlite_core.addons.base.BaseAddon`
- F-032: `_BaseAddon` 提供 `get_pyodide_settings`/`set_pyodide_settings` 方法读写插件配置，定义于 `_base.py` L37-45
- F-033: `_BaseAddon.get_lite_plugin_settings` 从 `jupyter-lite.json` 或 notebook metadata 中读取插件设置，定义于 `_base.py` L59-84
- F-034: `PipliteApp` 类定义于 `app.py` L52，继承自 `DescribedMixin` 和 `JupyterApp`
- F-035: `PipliteIndex` 子命令用于生成 wheel 目录的 `all.json` 索引，定义于 `app.py` L13-49
- F-036: 工具函数 `normalize_names` 使用 `packaging.utils.canonicalize_name` 规范化包名，定义于 `utils.py` L31-35
- F-037: 工具函数 `is_pyodide_wheel` 检查文件名是否匹配 pyodide 支持的 wheel 模式，定义于 `utils.py` L73-75
- F-038: 支持的 wheel 模式包括 `py3-none-any.whl`、`emscripten_*_wasm32.whl`、`pyodide_*_wasm32.whl`、`pyemscripten_*_wasm32.whl`，定义于 `constants.py` L40-57
- F-039: 工具函数 `iter_pep508_specs` 解析 PEP-508 规范，支持 `-r requirements.txt` 和 `-g group` 语法，定义于 `utils.py` L110-132
- F-040: 工具函数 `patch_dict` 递归更新字典，定义于 `utils.py` L92-101

## 常量定义

- F-041: `PYODIDE_KERNEL_PLUGIN_ID` 值为 `@jupyterlite/pyodide-kernel-extension:kernel`，定义于 `constants.py` L14
- F-042: `PIPLITE_URLS` 配置键值为 `pipliteUrls`，定义于 `constants.py` L5
- F-043: `DISABLE_PYPI_FALLBACK` 配置键值为 `disablePyPIFallback`，定义于 `constants.py` L6
- F-044: `PYODIDE_URL` 配置键值为 `pyodideUrl`，定义于 `constants.py` L23
- F-045: `LOAD_PYODIDE_OPTIONS` 配置键值为 `loadPyodideOptions`，定义于 `constants.py` L72
- F-046: `OPTION_LOCK_FILE_URL` 值为 `lockFileURL`，定义于 `constants.py` L75
- F-047: `OPTION_PACKAGES` 值为 `packages`，定义于 `constants.py` L78

## JS/TS 主线程 Kernel

- F-048: `PyodideKernel` 类定义于 `packages/pyodide-kernel/src/kernel.ts` L35，继承自 `BaseKernel`（来自 `@jupyterlite/services`）
- F-049: `PyodideKernel.constructor` 接受 `PyodideKernel.IOptions`，初始化 worker 和 remote kernel，定义于 `kernel.ts` L41-47
- F-050: `PyodideKernel.initWorker` 根据 `crossOriginIsolated` 选择 coincident 或 comlink worker，定义于 `kernel.ts` L62-77
- F-051: 当 `crossOriginIsolated` 为 true 时使用 `coincident.worker.js`，否则使用 `comlink.worker.js`，定义于 `kernel.ts` L65-76
- F-052: `PyodideKernel.initRemote` 根据 crossOriginIsolated 选择 remote 通信方式，定义于 `kernel.ts` L86-150
- F-053: coincident 模式下通过 `(worker as any).proxy` 获取 remote 代理，定义于 `kernel.ts` L89
- F-054: comlink 模式下通过 `wrap(worker)` 获取 remote 代理，定义于 `kernel.ts` L126
- F-055: `PyodideKernel._processWorkerMessage` 处理来自 worker 的消息类型：`stream`、`input_request`、`display_data`、`update_display_data`、`clear_output`、`execute_result`、`execute_error`、`comm_msg`/`comm_open`/`comm_close`，定义于 `kernel.ts` L211-269
- F-056: `PyodideKernel.kernelInfoRequest` 返回 kernel 信息，language_info 中 name 为 `python`，version 为 `3.8`，定义于 `kernel.ts` L274-301
- F-057: `PyodideKernel.executeRequest` 等待 ready 后调用 `_remoteKernel.execute`，定义于 `kernel.ts` L308-315
- F-058: `PyodideKernel` 实现了 `completeRequest`、`inspectRequest`、`isCompleteRequest`、`commInfoRequest`、`commOpen`、`commMsg`、`commClose`、`inputReply` 方法，分别代理到 remote kernel，定义于 `kernel.ts` L322-402
- F-059: `importModule` 函数使用 `new Function('url', 'return import(url)')` 动态导入 ES module，定义于 `loader.ts` L16-20

## JS/TS Token 接口定义

- F-060: `IPyodideWorkerKernel` 接口继承自 `IWorkerKernel`，定义于 `tokens.ts` L23-36
- F-061: `IPyodideWorkerKernel.initialize` 接受 `IPyodideWorkerKernel.IOptions` 参数，返回 `Promise<void>`，定义于 `tokens.ts` L27
- F-062: `IPyodideWorkerKernel.IOptions` 包含字段：`pyodideUrl`、`indexUrl`、`pipliteWheelUrl`、`pipliteUrls`、`disablePyPIFallback`、`location`、`mountDrive`、`browsingContextId`、`loadPyodideOptions`、`kernelId`，定义于 `tokens.ts` L92-148
- F-063: `IComlinkPyodideKernel` 接口继承 `IPyodideWorkerKernel`，添加 `registerWorkerMessageCallback` 和 `registerLogMessageCallback` 方法，定义于 `tokens.ts` L41-51
- F-064: `ICoincidentPyodideWorkerKernel` 接口继承 `IPyodideWorkerKernel`，添加 `processLogMessage`、`processWorkerMessage`、`processStdinRequest`、`processDriveRequest` 方法，定义于 `tokens.ts` L57-78

## JS/TS Web Worker 端

- F-065: `PyodideRemoteKernel` 抽象类定义于 `worker.ts` L16，是 Web Worker 中 kernel 的基类
- F-066: `PyodideRemoteKernel.initialize` 依次调用 `initRuntime`、`initFilesystem`、`initPackageManager`、`initKernel`、`initGlobals`，定义于 `worker.ts` L26-44
- F-067: `PyodideRemoteKernel.initRuntime` 通过 `importModule` 动态加载 pyodide.mjs，调用 `loadPyodide` 初始化，设置 stdout/stderr 回调和 fatal error 处理，定义于 `worker.ts` L46-79
- F-068: `PyodideRemoteKernel.initPackageManager` 加载 `micropip` 和 `piplite` 包，设置 piplite URLs 和 PyPI fallback 配置，定义于 `worker.ts` L81-110
- F-069: `PyodideRemoteKernel.initKernel` 加载 `ipykernel`、`comm`、`pyodide-kernel`、`jedi`、`ipython` 包，import `pyodide_kernel`，定义于 `worker.ts` L112-136
- F-070: `PyodideRemoteKernel.initGlobals` 从 pyodide globals 获取 `kernel_instance`、`stdout_stream`、`stderr_stream`、`interpreter` 引用，定义于 `worker.ts` L138-145
- F-071: `PyodideRemoteKernel.initFilesystem` 在 mountDrive 为 true 时创建 DriveFS 并挂载到 `/drive`，定义于 `worker.ts` L150-174
- F-072: `PyodideRemoteKernel.execute` 设置回调函数后调用 `_kernel.run(content.code)`，定义于 `worker.ts` L238-348
- F-073: `PyodideComlinkKernel` 类定义于 `comlink.worker.ts` L20，继承自 `PyodideRemoteKernel`，使用 comlink 的 `expose` 暴露 worker
- F-074: `PyodideComlinkKernel.sendInputRequest` 通过同步 XMLHttpRequest 发送 stdin 请求到 service worker，定义于 `comlink.worker.ts` L62-108
- F-075: `PyodideCoincidentKernel` 类定义于 `coincident.worker.ts` L40，继承自 `PyodideRemoteKernel`，使用 coincident 的 SharedArrayBuffer 通信
- F-076: `SharedBufferContentsAPI` 类继承自 `ContentsAPI`，通过 `workerAPI.processDriveRequest` 同步调用，定义于 `coincident.worker.ts` L25-29
- F-077: `PyodideDriveFS` 类继承自 `DriveFS`，使用 `SharedBufferContentsAPI`，定义于 `coincident.worker.ts` L34-38
- F-078: coincident worker 将所有 kernel 方法绑定到 `workerAPI`，定义于 `coincident.worker.ts` L81-89

## 浏览器端 Python Kernel

- F-079: 浏览器端 Python 包名 `pyodide_kernel`，版本 `0.9.0a1`，定义于 `py/pyodide-kernel/pyodide_kernel/__init__.py` L3
- F-080: `__init__.py` 执行顺序：1) 应用 mocks → 2) 应用 patches → 3) 创建 LiteStream 和 LitePythonShellApp → 4) 替换 sys.stdout/sys.stderr，定义于 `__init__.py` L7-33
- F-081: `PyodideKernel` 类定义于 `kernel.py` L29，继承自 `LoggingConfigurable`
- F-082: `PyodideKernel` 包含 trait：`interpreter`（Interpreter 实例）、`comm_manager`（CommManager 实例）、`parent_header`、`lite_transform_manager`，定义于 `kernel.py` L30-35
- F-083: `PyodideKernel.run` 是 async 方法，执行流程：lite_transform → loadPackagesFromImports → transform_cell → run_cell/run_cell_async，定义于 `kernel.py` L102-157
- F-084: `PyodideKernel.run` 通过 `pyodide_js.loadPackagesFromImports` 自动加载代码中 import 的包，定义于 `kernel.py` L115-117
- F-085: `PyodideKernel.complete` 方法支持 IPython 6.0 实验性补全（Jedi）和传统补全两种模式，定义于 `kernel.py` L84-100 和 L159-197
- F-086: `PyodideKernel.inspect` 使用 `interpreter.object_inspect_mime` 进行对象内省，定义于 `kernel.py` L55-70
- F-087: `PyodideKernel.is_complete` 使用 `input_transformer_manager.check_complete` 检查代码完整性，定义于 `kernel.py` L72-82
- F-088: `Interpreter` 类定义于 `interpreter.py` L22，继承自 `InteractiveShell`（IPython）
- F-089: `Interpreter.__init__` 创建 `PyodideKernel` 实例，启用 Jedi 补全，初始化 `_last_traceback`、`_input`、`_getpass`，定义于 `interpreter.py` L23-29
- F-090: `Interpreter.input` 属性 setter 将 `builtins.input` 替换为 JsProxy 回调，定义于 `interpreter.py` L31-39
- F-091: `Interpreter.getpass` 属性 setter 将 `getpass.getpass` 替换为回调，定义于 `interpreter.py` L41-48
- F-092: `Interpreter.init_history` 使用禁用的 `CustomHistoryManager`，定义于 `interpreter.py` L50-52
- F-093: `Interpreter._showtraceback` 捕获 traceback 到 `_last_traceback` 字典，定义于 `interpreter.py` L58-63
- F-094: `LitePythonShellApp` 类定义于 `interpreter.py` L66，继承自 `BaseIPythonApplication` 和 `InteractiveShellApp`
- F-095: `LitePythonShellApp.initialize` 依次调用 `init_path`、`init_shell`、`init_extensions`、`init_code`，定义于 `interpreter.py` L67-75
- F-096: `LitePythonShellApp.init_shell` 使用 `LiteDisplayHook` 和 `LiteDisplayPublisher` 创建 Interpreter 实例，定义于 `interpreter.py` L77-82

## 浏览器端 Python Display/Stream

- F-097: `LiteStream` 类定义于 `display.py` L12，包含 `name` 属性和 `publish_stream_callback` 回调
- F-098: `LiteStream.write` 通过 `publish_stream_callback` 将输出发送到 JS 端，定义于 `display.py` L19-21
- F-099: `LiteDisplayPublisher` 类继承自 `DisplayPublisher`，包含 `clear_output_callback`、`update_display_data_callback`、`display_data_callback`，定义于 `display.py` L30-55
- F-100: `LiteDisplayHook` 类继承自 `DisplayHook`，包含 `publish_execution_result` 回调，定义于 `display.py` L57-81
- F-101: `LiteDisplayHook.write_format_data` 使用 `json_clean` 和 `encode_images` 处理输出数据，定义于 `display.py` L69-71

## 浏览器端 Python Comm/Mocks/Patches

- F-102: `Comm` 类定义于 `comm.py` L7，继承自 ipykernel mock 的 `BaseComm`
- F-103: `Comm.publish_msg` 通过 `get_ipython().send_comm` 发送 comm 消息到 JS 端，定义于 `comm.py` L8-23
- F-104: `apply_mocks` 函数 mock 了 `termios`、`fcntl`、`resource`、`tornado`、`pexpect` 五个 POSIX-only 模块，定义于 `mocks.py` L40-57
- F-105: `apply_patches` 函数目前只包含 `patch_matplotlib`，设置 `MPLBACKEND` 环境变量为 `module://matplotlib_inline.backend_inline`，定义于 `patches.py` L1-19
- F-106: `LiteTransformerManager` 类继承自 IPython 的 `TransformerManager`，定义于 `litetransform.py` L19
- F-107: `LiteTransformerManager.line_transforms` 包含 `pip_magic` 转换，定义于 `litetransform.py` L23
- F-108: `pip_magic` 函数将 `%pip` 魔法命令转换为 `piplite.install` 调用，定义于 `litetransform.py` L78-96

## piplite 包

- F-109: `piplite.install` 函数是 `micropip.install` 的包装器，定义于 `piplite.py` L146-276
- F-110: `piplite._install` 使用 `unittest.mock.patch` 替换 `micropip.package_index.query_package` 为自定义的 `_query_package`，定义于 `piplite.py` L119-143
- F-111: `piplite._query_package` 先遍历 `_PIPLITE_URLS` 中的本地 all.json 索引查找包，找不到时根据 `_PIPLITE_DISABLE_PYPI` 决定是否回退到 PyPI，定义于 `piplite.py` L84-116
- F-112: `piplite._get_pypi_json_from_index` 从 all.json 索引中查找包并重写本地 wheel URL，定义于 `piplite.py` L41-81
- F-113: `_PIPLITE_URLS` 是模块级列表，存储 Warehouse-like API 端点 URL，定义于 `piplite.py` L24
- F-114: `_PIPLITE_DISABLE_PYPI` 是模块级布尔值，控制是否禁用 PyPI 回退，定义于 `piplite.py` L30
- F-115: `PiplitePyPIDisabled` 异常类继承自 `ValueError`，定义于 `piplite.py` L36-38
- F-116: `piplite.cli.get_transformed_code` 解析 CLI 参数并生成 `await piplite.install(...)` 代码字符串，定义于 `cli.py` L114-128

## JupyterLab Extension

- F-117: Extension 插件 ID 为 `@jupyterlite/pyodide-kernel-extension:kernel`，定义于 `packages/pyodide-kernel-extension/src/index.ts` L30
- F-118: Extension 注册 kernel spec：name 为 `python`，display_name 为 `Python (Pyodide)`，language 为 `python`，定义于 `extension/src/index.ts` L94-104
- F-119: Extension 的 `activate` 函数从 `litePluginSettings` 读取配置：`pyodideUrl`、`pipliteWheelUrl`、`pipliteUrls`、`disablePyPIFallback`、`loadPyodideOptions`，定义于 `extension/src/index.ts` L49-69
- F-120: 默认 CDN URL 为 `https://cdn.jsdelivr.net/pyodide/v314.0.4/full/pyodide.mjs`，定义于 `extension/src/index.ts` L25
- F-121: `mountDrive` 条件为 `serviceWorkerManager?.enabled || crossOriginIsolated`，定义于 `extension/src/index.ts` L108
- F-122: Extension 可选依赖 `IServiceWorkerManager` 和 `ILoggerRegistry`，定义于 `extension/src/index.ts` L40

## 内嵌 Wheel 包

- F-123: `packages/pyodide-kernel/py/ipykernel/` 提供 ipykernel mock，版本 `6.9.2`，导出 `Comm` 和 `CommManager`，定义于 `py/ipykernel/ipykernel/__init__.py`
- F-124: `packages/pyodide-kernel/py/widgetsnbextension3/` 和 `widgetsnbextension4/` 提供 ipywidgets 兼容层

## npm 包依赖

- F-125: `@jupyterlite/pyodide-kernel` npm 包依赖：`@jupyterlab/coreutils`、`@jupyterlab/logconsole`、`@jupyterlite/services`、`coincident: ^4.1.1`、`comlink: ^4.4.2`，定义于 `packages/pyodide-kernel/package.json` L52-58
- F-126: Worker 文件使用 esbuild 构建为独立的 ES module bundle，定义于 `package.json` L40-42
- F-127: `@jupyterlite/pyodide-kernel-extension` npm 包依赖 `@jupyterlab/application`、`@jupyterlab/coreutils`、`@jupyterlab/logconsole`、`@jupyterlite/apputils`、`@jupyterlite/pyodide-kernel`、`@jupyterlite/services`，定义于 `extension/package.json` L49-56
- F-128: extension 的 labextension 输出目录为 `../../jupyterlite_pyodide_kernel/labextension`，定义于 `extension/package.json` L67
- F-129: extension 的 `piplite.wheelDir` 为 `static/pypi`，定义于 `extension/package.json` L76-78
