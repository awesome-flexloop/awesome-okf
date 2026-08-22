---
type: Facts
okf_version: '0.2'
title: jupyterlite 源码事实清单
generated: '2026-08-22'
tags:
- jupyter
- jupyterlite
- wasm
- pyodide
- browser
sources:
- ../../../../../external/libs/jupyter/jupyterlite/pyproject.toml
- ../../../../../external/libs/jupyter/jupyterlite/py/jupyterlite-core/pyproject.toml
- ../../../../../external/libs/jupyter/jupyterlite/py/jupyterlite/pyproject.toml
- ../../../../../external/libs/jupyter/jupyterlite/py/jupyterlite-core/jupyterlite_core/__init__.py
- ../../../../../external/libs/jupyter/jupyterlite/py/jupyterlite-core/jupyterlite_core/app.py
- ../../../../../external/libs/jupyter/jupyterlite/py/jupyterlite-core/jupyterlite_core/manager.py
- ../../../../../external/libs/jupyter/jupyterlite/py/jupyterlite-core/jupyterlite_core/config.py
- ../../../../../external/libs/jupyter/jupyterlite/py/jupyterlite-core/jupyterlite_core/constants.py
- ../../../../../external/libs/jupyter/jupyterlite/py/jupyterlite-core/jupyterlite_core/addons/__init__.py
- ../../../../../external/libs/jupyter/jupyterlite/py/jupyterlite-core/jupyterlite_core/addons/base.py
- ../../../../../external/libs/jupyter/jupyterlite/py/jupyterlite-core/jupyterlite_core/addons/static.py
- ../../../../../external/libs/jupyter/jupyterlite/py/jupyterlite-core/jupyterlite_core/addons/contents.py
- ../../../../../external/libs/jupyter/jupyterlite/py/jupyterlite-core/jupyterlite_core/addons/lite.py
- ../../../../../external/libs/jupyter/jupyterlite/py/jupyterlite-core/jupyterlite_core/addons/serve.py
- ../../../../../external/libs/jupyter/jupyterlite/py/jupyterlite-core/jupyterlite_core/addons/serviceworker.py
- ../../../../../external/libs/jupyter/jupyterlite/py/jupyterlite/jupyterlite/__init__.py
- ../../../../../external/libs/jupyter/jupyterlite/package.json
- ../../../../../external/libs/jupyter/jupyterlite/app/package.json
- ../../../../../external/libs/jupyter/jupyterlite/packages/application/src/index.ts
- ../../../../../external/libs/jupyter/jupyterlite/packages/application/src/router.ts
- ../../../../../external/libs/jupyter/jupyterlite/packages/application-extension/src/index.tsx
- ../../../../../external/libs/jupyter/jupyterlite/packages/apputils/src/index.ts
- ../../../../../external/libs/jupyter/jupyterlite/packages/apputils/src/tokens.ts
- ../../../../../external/libs/jupyter/jupyterlite/packages/apputils/src/service-worker-manager.ts
- ../../../../../external/libs/jupyter/jupyterlite/packages/apputils/src/service-worker.ts
- ../../../../../external/libs/jupyter/jupyterlite/packages/services/src/index.ts
- ../../../../../external/libs/jupyter/jupyterlite/packages/services/src/kernel/base.ts
- ../../../../../external/libs/jupyter/jupyterlite/packages/services/src/kernel/client.ts
- ../../../../../external/libs/jupyter/jupyterlite/packages/services/src/kernel/tokens.ts
- ../../../../../external/libs/jupyter/jupyterlite/packages/services/src/kernel/kernelspecs.ts
- ../../../../../external/libs/jupyter/jupyterlite/packages/services/src/contents/drive.ts
- ../../../../../external/libs/jupyter/jupyterlite/packages/services/src/contents/tokens.ts
- ../../../../../external/libs/jupyter/jupyterlite/packages/services/src/session/client.ts
- ../../../../../external/libs/jupyter/jupyterlite/packages/services/src/settings/settings.ts
- ../../../../../external/libs/jupyter/jupyterlite/packages/services/src/nbconvert/manager.ts
- ../../../../../external/libs/jupyter/jupyterlite/packages/server/src/index.ts
- ../../../../../external/libs/jupyter/jupyterlite/packages/kernel/src/index.ts
- ../../../../../external/libs/jupyter/jupyterlite/packages/contents/src/index.ts
- ../../../../../external/libs/jupyter/jupyterlite/packages/localforage/src/index.ts
---

# JupyterLite 源码事实清单

## 项目元数据

- F-001: 根项目名 "jupyterlite-root"，版本 "0.9.0a1"（pyproject.toml L2-3）
- F-002: jupyterlite-core 包名 "jupyterlite-core"，build-backend 为 hatchling（py/jupyterlite-core/pyproject.toml L2-6）
- F-003: jupyterlite-core 运行时依赖 doit>=0.34,<1 和 jupyter_core>=4.7（py/jupyterlite-core/pyproject.toml L10-13）
- F-004: jupyterlite-core 注册 CLI 入口点 jupyter-lite = "jupyterlite_core.app:main"（py/jupyterlite-core/pyproject.toml L52-53）
- F-005: jupyterlite-core 注册 entry-points "jupyterlite.addon.v0"，包含 archive/contents/federated_extensions/icons/lite/mimetypes/report/serve/settings/static/translation/workspaces 共 12 个 addon（py/jupyterlite-core/pyproject.toml L94-106）
- F-006: jupyterlite 元包依赖 jupyterlite-core >=0.9.0a1，自身不包含额外代码逻辑（py/jupyterlite/pyproject.toml L10-11）
- F-007: jupyterlite-core 和 jupyterlite 均要求 Python >=3.10（py/jupyterlite-core/pyproject.toml L27; py/jupyterlite/pyproject.toml L24）
- F-008: jupyterlite-core 使用 hatch 构建，wheel/sdist 包含 jupyterlite_core 目录和 jupyterlite-*.tgz 归档文件（py/jupyterlite-core/pyproject.toml L108-126）
- F-009: jupyterlite-core 版本号在 __init__.py 中定义为 "0.9.0a1"（py/jupyterlite-core/jupyterlite_core/__init__.py L3）
- F-010: jupyterlite 元包版本号在 __init__.py 中定义为 "0.9.0a1"（py/jupyterlite/jupyterlite/__init__.py L3）
- F-011: 前端根包名为 @jupyterlite/root，私有包，使用 yarn 3.5.0 作为包管理器（package.json L2-4, L95）
- F-012: 前端构建工具使用 rspack（非 webpack），脚本为 build/build:prod/watch（app/package.json L16-20）
- F-013: 前端 app 包定义了 6 个应用：lab/repl/tree/edit/notebooks/consoles（app/package.json L33-42）
- F-014: License 为 BSD-3-Clause（package.json L13）

## CLI 应用架构

- F-015: LiteApp 继承自 BaseLiteApp，定义子命令 list/status/init/build/check/serve/archive/doit（app.py L323-341）
- F-016: BaseLiteApp 继承 JupyterApp、LiteBuildConfig、DescribedMixin，配置文件名固定为 "jupyter_lite_config"（app.py L78-83）
- F-017: ManagedApp 在 start() 中调用 lite_manager.initialize()（app.py L220-222）
- F-018: LiteDoitApp 在 start() 中调用 lite_manager.doit_run(*self._doit_cmd)（app.py L230-232）
- F-019: LiteTaskApp 使用 PHASES 前缀生成 doit 任务名，格式为 "{phase}{task}"（app.py L276-277）
- F-020: CLI flags 包含 ignore-sys-prefix/no-sourcemaps/no-unused-shared-packages/no-libarchive（app.py L23-39）
- F-021: CLI aliases 包含 disable-addons/app-archive/apps/lite-dir/contents/settings-overrides/output-dir/port/base-url/workspaces 等（app.py L41-67）
- F-022: 配置文件搜索路径包含当前目录、jupyter_config_path() 返回的路径，以及 lite_dir（app.py L99-107）
- F-023: main 函数为 LiteApp.launch_instance（app.py L344）

## LiteManager 与 Addon 系统

- F-024: LiteManager 继承 LiteBuildConfig，负责将 addons 映射为 doit 任务并调用 doit API（manager.py L13-18）
- F-025: LiteManager.strict 默认为 True，遇到第一个错误即停止工作流（manager.py L20-22）
- F-026: doit 配置使用 sqlite3 后端，依赖文件为 .jupyterlite.doit.db，verbosity=2（manager.py L92-98）
- F-027: 任务生成遍历 HOOKS×PHASES 组合，HOOKS 为 [status,init,build,check,serve,archive]，PHASES 为 [pre_, "", post_]（manager.py L106-112; constants.py L129-147）
- F-028: HOOK_PARENTS 定义了钩子依赖关系：build→init, check→build, serve→build, archive→build（constants.py L139-144）
- F-029: 每个 addon 通过 __all__ 列表声明支持的钩子方法（manager.py L77）
- F-030: Addon 实现通过 entry_points 发现，使用 @lru_cache(1) 缓存（addons/__init__.py L53-65）
- F-031: Addon entry point 组名为 "jupyterlite.addon.v0"（constants.py L28; addons/__init__.py L8）
- F-032: merge_addon_aliases 合并 addon 定义的 CLI 别名，冲突时发出警告（addons/__init__.py L11-24）
- F-033: merge_addon_flags 合并 addon 定义的 CLI flags，同名 flag 合并配置类（addons/__init__.py L27-50）
- F-034: doit 任务名格式为 "{task_prefix}{phase}{hook}"（manager.py L111）
- F-035: _gather_tasks 使用 doit.create_after 装饰器确保任务按顺序执行（manager.py L135-138）

## 配置系统 (LiteBuildConfig)

- F-036: LiteBuildConfig 继承 LoggingConfigurable，是 traitlets 配置对象（config.py L19-31）
- F-037: apps 配置项为 TypedTuple(Unicode())，指定要构建的应用如 lab/tree/repl（config.py L38-41）
- F-038: lite_dir 默认从 JUPYTERLITE_DIR 环境变量或当前目录获取（config.py L175-177）
- F-039: output_dir 默认值为 lite_dir/_output（config.py L165-169; constants.py L88）
- F-040: contents 默认值为 lite_dir/files 目录（config.py L179-186）
- F-041: cache_dir 默认值为 lite_dir/.cache（config.py L171-173）
- F-042: port 默认值为 8000，从 JUPYTERLITE_PORT 环境变量读取（config.py L282-284）
- F-043: base_url 默认值为 "/"，从 JUPYTERLITE_BASE_URL 环境变量读取（config.py L286-288）
- F-044: ignore_contents 默认忽略模式包含 /_build/,/.cache/,/.git,/node_modules/,/venvs/ 等（config.py L198-224）
- F-045: ignore_sys_prefix 可以是 bool 或 tuple[str]，用于跳过从 sys.prefix 复制组件（config.py L71-73）
- F-046: source_date_epoch 从 SOURCE_DATE_EPOCH 环境变量读取，用于可复现构建（config.py L126-130, L275-280）
- F-047: file_types 配置项是 Dict 类型，定义了浏览器可用的文件类型映射（config.py L140-142）
- F-048: DEFAULT_FILE_TYPES 定义了 text/json/base64 三类共 30+ 种文件扩展名及 MIME 类型（constants.py L155-199）
- F-049: 支持的压缩归档扩展名包括 .whl/.zip/.conda/.tgz/.tar.bz2/.tar.gz（constants.py L106-109）
- F-050: 服务 worker 相关配置通过 jupyter-config-data 注入页面，key 为 litePluginSettings（constants.py L72）

## 常量定义

- F-051: JUPYTERLITE_JSON = "jupyter-lite.json"，JUPYTERLITE_IPYNB = "jupyter-lite.ipynb"（constants.py L80-83）
- F-052: JUPYTERLITE_SCHEMA = "jupyterlite.schema.v0.json"（constants.py L77）
- F-053: JUPYTER_CONFIG_DATA = "jupyter-config-data"，为 script DOM ID（constants.py L51）
- F-054: API_CONTENTS = "api/contents"，API_TRANSLATIONS = "api/translations"，API_WORKSPACES = "api/workspaces"（constants.py L114-120）
- F-055: FEDERATED_EXTENSIONS = "federated_extensions"，DISABLED_EXTENSIONS = "disabledExtensions"（constants.py L54-57）
- F-056: SETTINGS_OVERRIDES = "settingsOverrides"，OVERRIDES_JSON = "overrides.json"（constants.py L36, L60）
- F-057: MOD_DIRECTORY = 0o755，MOD_FILE = 0o644（constants.py L7-10）
- F-058: SOURCEMAPS = [".js.map", ".mjs.map", ".css.map"]（constants.py L151）
- F-059: WORKSPACE_FILE = ".jupyterlab-workspace"（constants.py L95）

## Addon: StaticAddon（静态资源）

- F-060: StaticAddon 负责将"gold master"归档（npm tarball）解包到 output_dir（addons/static.py L17-18）
- F-061: StaticAddon.__all__ 包含 pre_status/pre_init/init/post_init（addons/static.py L29）
- F-062: pre_init 阶段清理 output_dir 并创建目录，当 app_archive 或 apps/no_sourcemaps/no_unused_shared_packages 变化时重新执行（addons/static.py L51-74）
- F-063: init 阶段解包 tarball，目标文件为 output_dir/jupyter-lite.json（addons/static.py L76-84）
- F-064: post_init 阶段根据 apps 配置裁剪不需要的应用目录，可选裁剪未使用的共享 webpack chunk（addons/static.py L86-117）
- F-065: 归档中 package/package.json 的 jupyterlite.apps 字段列出所有可用应用（addons/static.py L90-93）
- F-066: prune_unused_shared_packages 通过正则解析 bundle.js 中的 chunk 引用模式来识别未使用的 chunk（addons/static.py L134-160）

## Addon: ContentsAddon（内容索引）

- F-067: ContentsAddon 负责将 lite_dir 中的文件复制到 output_dir/files 并生成 Contents API 响应（addons/contents.py L22-24）
- F-068: ContentsAddon.__all__ 包含 build/post_build/check/status（addons/contents.py L25）
- F-069: post_build 阶段为 files/ 下每个子目录生成 api/contents/{path}/all.json（addons/contents.py L68-91）
- F-070: one_contents_path 使用 jupyter_server 的 FileContentsManager 生成目录列表（addons/contents.py L160-186）
- F-071: patch_contents_config 在 jupyter-lite.json 中设置 contentsAllJsonFile 字段为 "all.json"（addons/contents.py L231-248）
- F-072: 当 source_date_epoch 设置时，Contents 列表中的 created/last_modified 时间戳会被截断（addons/contents.py L250-277）
- F-073: DateTimeEncoder 将 datetime 对象序列化为 ISO 格式，UTC 时区标记为 Z（addons/contents.py L280-291）

## Addon: BaseAddon（基类工具）

- F-074: BaseAddon 继承 LoggingConfigurable，持有 manager 引用（addons/base.py L38-44）
- F-075: BaseAddon.copy_one 支持复制文件/目录，可选忽略 sourcemap 文件（addons/base.py L66-92）
- F-076: BaseAddon.extract_one 支持 zip/tar/tar.bz2/tar.gz 格式，优先使用 libarchive-c（addons/base.py L302-331）
- F-077: BaseAddon.merge_one_jupyterlite 合并多个 jupyter-lite.json/ipynb 配置文件（addons/base.py L187-239）
- F-078: merge_jupyter_config_data 对 federated_extensions 和 disabledExtensions 做列表合并，对 settingsOverrides 做深度合并（addons/base.py L241-260）
- F-079: get_lite_plugin_settings/set_lite_plugin_settings 读写 jupyter-lite.json 中的 litePluginSettings[pluginId]（addons/base.py L372-404）
- F-080: safe_extract_all 检查 tar 成员路径，防止路径遍历攻击（addons/base.py L339-344）
- F-081: maybe_timestamp/timestamp_one 将文件时间戳截断到 source_date_epoch（addons/base.py L122-144）

## Addon: LiteAddon（配置合并与验证）

- F-082: LiteAddon.__all__ 包含 build/check/status（addons/lite.py L17）
- F-083: build 阶段将 lite_dir 中的 jupyter-lite.json/ipynb 合并到 output_dir（addons/lite.py L30-56）
- F-084: check 阶段使用 schema 验证所有 jupyter-lite.json 和 jupyter-lite.ipynb（metadata.jupyter-lite 段）（addons/lite.py L58-85）
- F-085: lite_files 属性遍历 lite_dir 下所有 jupyter-lite.json 和 jupyter-lite.ipynb，排除忽略目录（addons/lite.py L87-104）

## Addon: ServeAddon（本地服务）

- F-086: ServeAddon 优先使用 tornado，否则回退到 Python stdlib http.server（addons/serve.py L45-51）
- F-087: 服务地址固定为 http://127.0.0.1:{port}{base_url}（addons/serve.py L14, L42-43）
- F-088: tornado 模式下支持 /shutdown 端点关闭服务器（addons/serve.py L94-97, L113）
- F-089: _patch_mime 从 jupyter-lite.json 读取 fileTypes 并注册到 mimetypes 模块（addons/serve.py L60-81）
- F-090: Windows 平台下 _patch_mime 会清空系统 mimetypes 注册表以避免错误信息（addons/serve.py L69-71）

## Service Worker

- F-091: serviceworker.py addon 目前仅包含 TODO 注释，尚未实现实际功能（addons/serviceworker.py L1-7）
- F-092: Service Worker 脚本使用 BroadcastChannel('/sw-api.v1') 与主线程通信（apputils/src/service-worker.ts L9; apputils/src/service-worker-manager.ts L19）
- F-093: Service Worker 监听 install/activate/fetch 事件（apputils/src/service-worker.ts L19-21）
- F-094: install 事件调用 skipWaiting() 和 cacheAll()（apputils/src/service-worker.ts L28-31）
- F-095: activate 事件从 URL 参数 enableCache 读取缓存开关，调用 clients.claim()（apputils/src/service-worker.ts L36-41）
- F-096: fetch 事件对 /api/service-worker-heartbeat 返回 'ok' 以保持 SW 活跃（apputils/src/service-worker.ts L50-53）
- F-097: shouldBroadcast 判断同源且路径包含 /api/drive 或 /api/stdin/ 的请求转发到主线程（apputils/src/service-worker.ts L116-121）
- F-098: shouldDrop 丢弃非 GET 请求、非 HTTP 源、以及包含 /api/ 的请求（apputils/src/service-worker.ts L126-132）
- F-099: 缓存策略：命中缓存时返回缓存并后台 refetch；未命中时 fetch 并更新缓存（apputils/src/service-worker.ts L70-87）
- F-100: ServiceWorkerManager 每 20 秒发送心跳 ping 到 /api/service-worker-heartbeat（apputils/src/service-worker-manager.ts L29-34, L178-184）
- F-101: ServiceWorkerManager 注册时检查版本变更，版本不同则注销所有旧 SW（apputils/src/service-worker-manager.ts L155-173）
- F-102: ServiceWorkerManager 使用 browsingContextId (UUID) 区分不同浏览器标签页/窗口（apputils/src/service-worker-manager.ts L52, L84-86）
- F-103: registerStdinHandler 允许注册 stdin 请求处理器，按 URL 路径后缀匹配（如 "kernel"、"terminal"）（apputils/src/service-worker-manager.ts L100-105, L236-252）
- F-104: DriveContentsProcessor 处理 Service Worker 转发的 drive API 请求（apputils/src/service-worker-manager.ts L57-59, L223-234）
- F-105: IServiceWorkerManager token 定义为 '@jupyterlite/apputils:IServiceWorkerManager'（apputils/src/tokens.ts L12-15）
- F-106: WORKER_NAME 从 service-worker?text 导入的 URL 中提取文件名（apputils/src/tokens.ts L7, L86）

## 内核系统 (Kernel)

- F-107: BaseKernel 是抽象类，实现 IKernel 接口，处理 kernel message 分发（services/src/kernel/base.ts L11）
- F-108: BaseKernel.handleMessage 处理 kernel_info_request/execute_request/input_reply/inspect_request/is_complete_request/complete_request/history_request/comm_open/comm_msg/comm_close 共 10 种消息类型（services/src/kernel/base.ts L104-146）
- F-109: 每个消息处理前后发送 status: busy 和 status: idle 消息（services/src/kernel/base.ts L105, L145）
- F-110: BaseKernel 定义了 9 个抽象方法：kernelInfoRequest/executeRequest/completeRequest/inspectRequest/isCompleteRequest/commInfoRequest/inputReply/commOpen/commMsg/commClose（services/src/kernel/base.ts L153-232）
- F-111: BaseKernel 提供 stream/displayData/inputRequest/publishExecuteResult/publishExecuteError/updateDisplayData/clearOutput 等受保护方法发送 iopub/stdin 消息（services/src/kernel/base.ts L240-431）
- F-112: execute_request 处理递增 executionCount（当 store_history=true），记录 history，发送 execute_input 消息（services/src/kernel/base.ts L534-548）
- F-113: LiteKernelClient 使用 mock-socket 库的 WebSocketServer 在浏览器内模拟内核 WebSocket 服务（services/src/kernel/client.ts L20-21, L284-292）
- F-114: LiteKernelClient.startNew 为每个内核创建 WebSocketServer，URL 基于 WS_BASE_URL + /api/kernels/{id}/channels（services/src/kernel/client.ts L224-229）
- F-115: LiteKernelClient 使用 async-mutex 确保同一时间只处理一条消息（services/src/kernel/client.ts L18, L82）
- F-116: 内核中断通过 mutex.cancel() 实现，cancelReason 为 'interrupt'/'interrupt-subsequent'/'error'（services/src/kernel/client.ts L107-173, L467-470）
- F-117: iopub 消息广播到所有连接该 kernel 的 client（services/src/kernel/client.ts L249-255）
- F-118: execute_reply 错误状态（非 interrupt 导致）会触发 mutex.cancel() 取消后续 cell 执行（services/src/kernel/client.ts L259-268）
- F-119: LiteKernelClient.restart 标记 kernel 为 restarting 状态，dispose 旧 kernel 后 startNew 同名 kernel（services/src/kernel/client.ts L325-356）
- F-120: LiteKernelClient.interrupt 等待 kernel ready 后取消 mutex（services/src/kernel/client.ts L370-387）
- F-121: LiteKernelClient.handleStdin 通过 PromiseDelegate 等待 input_reply 消息（services/src/kernel/client.ts L429-445）
- F-122: WebSocket 协议使用 v1KernelWebsocketJupyterOrg 版本（services/src/kernel/client.ts L29-30）
- F-123: FALLBACK_KERNEL 常量为 "javascript"（services/src/kernel/tokens.ts L21）
- F-124: IKernel 接口要求 id/name/location/ready 属性和 handleMessage 方法（services/src/kernel/tokens.ts L67-94）
- F-125: IWorkerKernel 接口定义了 comlink worker 内核的 10 个方法，包括 initialize/execute/complete/inspect/isComplete/commInfo/commOpen/commMsg/commClose/inputReply（services/src/kernel/tokens.ts L173-205）
- F-126: KernelSpecs 类维护 spec 和 factory 的 Map，register 方法注册内核规范和工厂函数（services/src/kernel/kernelspecs.ts L63-70）
- F-127: KernelSpecs.defaultKernelName 优先从 PageConfig 获取，否则取字典序第一个 spec name，最后回退到 FALLBACK_KERNEL（services/src/kernel/kernelspecs.ts L32-42）

## 内容存储 (Contents/Drive)

- F-128: BrowserStorageDrive 实现 Contents.IDrive 接口，drive 名称为 "BrowserStorage"（services/src/contents/drive.ts L29, L140）
- F-129: BrowserStorageDrive 使用 localforage 作为持久化存储，分三个 store：files/counters/checkpoints（services/src/contents/drive.ts L24, L304-331）
- F-130: 默认存储名 "JupyterLite Storage"，每个文件最多保留 5 个 checkpoint（services/src/contents/drive.ts L24, L34）
- F-131: newUntitled 支持创建 directory/notebook/file 三种类型，notebook 使用空 nbformat 4.5 结构（services/src/contents/drive.ts L354-445）
- F-132: BrowserStorageDrive.get 支持 contentProvider 委托，否则合并本地存储和服务器静态文件（services/src/contents/drive.ts L503-598）
- F-133: 文件内容支持三种格式：json/text/base64，自动转换（services/src/contents/drive.ts L45-135）
- F-134: save 支持多 chunk 上传，chunk>1 或 chunk===-1 时追加内容（services/src/contents/drive.ts L734-771）
- F-135: getDownloadUrl 对于浏览器存储文件创建 Blob URL，对于服务器文件返回 /files/{path} URL（services/src/contents/drive.ts L208-239）
- F-136: delete 递归删除路径前缀匹配的所有文件（services/src/contents/drive.ts L817-829）
- F-137: _getServerContents 从 api/contents/{path}/all.json 获取静态文件列表，fetch /files/{path} 获取文件内容（services/src/contents/drive.ts L1005-1079）
- F-138: contentProviderRegistry 支持可插拔的内容提供者（实验性功能）（services/src/contents/drive.ts L149-155, L164）
- F-139: FILE.getType 和 FILE.hasFormat 从 PageConfig.fileTypes 构建时配置和 mime 库获取 MIME 信息（services/src/contents/tokens.ts L17-60）
- F-140: @jupyterlite/contents、@jupyterlite/kernel、@jupyterlite/server 三个包均为 deprecated shim，重新导出 @jupyterlite/services 或 @jupyterlite/apputils 的内容（contents/src/index.ts L5-28; kernel/src/index.ts L5-35; server/src/index.ts L5-25）

## 会话管理 (Session)

- F-141: LiteSessionClient 实现 ISessionAPIClient，维护内存中的 Session.IModel[] 列表（services/src/session/client.ts L21）
- F-142: LiteSessionClient 监听 kernelClient.changed 信号，kernel 被移除时自动清理关联 session（services/src/session/client.ts L34-46）
- F-143: startNew 支持 kernel.id 复用来共享内核，否则创建新 kernel（services/src/session/client.ts L130-186）
- F-144: shutdown 先移除 session 再关闭 kernel，避免重复清理（services/src/session/client.ts L193-206）

## 设置管理 (Settings)

- F-145: Settings 类继承 SettingManager，使用 localforage 的 'settings' store 存储用户设置（services/src/settings/settings.ts L27, L87-93）
- F-146: Settings.list 合并 all.json（核心插件）和 all_federated.json（联邦扩展）的设置（services/src/settings/settings.ts L116-129）
- F-147: 用户设置覆盖默认 raw 值，使用 json5 解析（services/src/settings/settings.ts L133-143）
- F-148: Private.override 从 PageConfig.settingsOverrides 读取覆盖值并注入 schema.default（services/src/settings/settings.ts L216-236）

## 前端插件体系 (application-extension)

- F-149: application-extension 导出 14 个 JupyterFrontEndPlugin：about/clearBrowserData/downloadPlugin/liteRouter/liteLogo/lspConnectionManager/modeSupport/notifyCommands/opener/router/serviceWorkerManagerPlugin/sessionContextPatch/shareFile/siteDrive（application-extension/src/index.tsx L978-993）
- F-150: siteDrive 插件默认禁用（需 setting enabled=true），提供只读的 JupyterLite 配置文件浏览器（application-extension/src/index.tsx L113-160）
- F-151: liteRouter 插件提供 ILiteRouter（含 addTransformer 方法），router 插件将其作为 IRouter 暴露（application-extension/src/index.tsx L167-204）
- F-152: LiteRouter 继承 Router，维护 IURLTransformer 列表，navigate 时依次应用转换器（application/src/router.ts L44-83）
- F-153: opener 插件注册 URL 路径路由，根据 path 查询参数打开文件，URL_PATTERN 匹配 /(lab|tree|notebooks|edit|consoles)/（application-extension/src/index.tsx L77, L550-676）
- F-154: downloadPlugin 通过创建 data: URL 实现浏览器端文件下载，支持 json/text/base64 三种格式（application-extension/src/index.tsx L335-472）
- F-155: serviceWorkerManagerPlugin 创建 ServiceWorkerManager 并注册 kernel stdin handler（application-extension/src/index.tsx L681-698）
- F-156: sessionContextPatch 插件在 widget 打开时将 sessionContext 的 _name/_path 设置为包含 drive 名称的完整路径（application-extension/src/index.tsx L705-737）
- F-157: modeSupport 插件支持 single-document/multiple-document 模式切换，URL ?mode= 参数优先（application-extension/src/index.tsx L927-976）
- F-158: clearBrowserData 插件可清除 contents/settings/workspaces 三类浏览器存储（application-extension/src/index.tsx L815-922）
- F-159: lspConnectionManager 创建 LanguageServerManager（fetchSessions 为空操作）和 DocumentConnectionManager（application-extension/src/index.tsx L505-527）

## NbConvert（客户端导出）

- F-160: LiteNbConvertManager 继承 NbConvertManager，使用客户端 IExporter 注册表而非服务器 API（services/src/nbconvert/manager.ts L27-37）
- F-161: Exporters 类维护 Map<string, IExporter>，register 方法注册导出器（services/src/nbconvert/manager.ts L69-105）

## 其他包

- F-162: localforage 包重新导出 tokens 和 memory 模块（localforage/src/index.ts L4-5）
- F-163: types 包导出 tokens 和 index.ts 定义的类型（packages/types/src/index.ts）
- F-164: ui-components 包提供 liteIcon 和 liteWordmark SVG 图标（application-extension/src/index.tsx L52; ui-components/src/icon/index.ts）
- F-165: repl-extension 提供 REPL 按钮 schema 配置（packages/repl-extension/schema/buttons.json）
- F-166: services-extension 提供 configsection/event 插件，处理配置节和事件（packages/services-extension/src/index.ts）
- F-167: apputils 包包含 licenses/pluginmanager/translation/statedb/tokens/workspaces/workspace-router/service-worker-manager 模块（apputils/src/index.ts L4-11）
