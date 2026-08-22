---
type: Facts
okf_version: '0.2'
generated: '2026-08-22'
tags:
- jupyter
- real-time-collaboration
- yjs
- crdt
- websocket
- jupyterlab-extension
sources:
- ../../../../../external/libs/jupyter/jupyter-collaboration/package.json
- ../../../../../external/libs/jupyter/jupyter-collaboration/pyproject.toml
- ../../../../../external/libs/jupyter/jupyter-collaboration/projects/jupyter-server-ydoc/jupyter_server_ydoc/rooms.py
- ../../../../../external/libs/jupyter/jupyter-collaboration/projects/jupyter-server-ydoc/jupyter_server_ydoc/handlers.py
- ../../../../../external/libs/jupyter/jupyter-collaboration/projects/jupyter-server-ydoc/jupyter_server_ydoc/stores.py
- ../../../../../external/libs/jupyter/jupyter-collaboration/projects/jupyter-server-ydoc/jupyter_server_ydoc/app.py
- ../../../../../external/libs/jupyter/jupyter-collaboration/projects/jupyter-server-ydoc/jupyter_server_ydoc/utils.py
- ../../../../../external/libs/jupyter/jupyter-collaboration/projects/jupyter-server-ydoc/jupyter_server_ydoc/loaders.py
- ../../../../../external/libs/jupyter/jupyter-collaboration/packages/collaboration/src/index.ts
- ../../../../../external/libs/jupyter/jupyter-collaboration/packages/collaboration/src/cursors.ts
- ../../../../../external/libs/jupyter/jupyter-collaboration/packages/collaboration-extension/src/index.ts
- ../../../../../external/libs/jupyter/jupyter-collaboration/packages/docprovider-extension/src/index.ts
- ../../../../../external/libs/jupyter/jupyter-collaboration/packages/docprovider/src/notebookCellExecutor.ts
title: jupyter-collaboration 源码事实清单
---

# jupyter-collaboration 事实集

## 项目元数据

- F-001: package.json:2 — 根包名为 `@jupyter/real-time-collaboration`，私有包（private: true）。
- F-002: package.json:4 — 版本号为 `5.0.0`。
- F-003: package.json:5 — 项目描述为 "JupyterLab Extension enabling Real-Time Collaboration"。
- F-004: package.json:19 — 使用 BSD-3-Clause 许可证。
- F-005: package.json:24-26 — 使用 Yarn workspaces，工作区模式为 `packages/*`。
- F-006: package.json:27-30 — resolutions 锁定 `lib0` 版本 `<=0.2.98`，`@jupyterlab/rendermime` 版本 `^4.6.0`。
- F-007: package.json:33 — 构建命令使用 lerna：`lerna run build`。
- F-008: package.json:72 — TypeScript 版本为 `~5.9.3`。
- F-009: pyproject.toml:9 — Python 后端包名为 `jupyter-server-ydoc`。
- F-010: pyproject.toml:12 — Python 版本要求 `>=3.10`，支持 3.10-3.14。
- F-011: pyproject.toml:30-38 — 核心依赖：jupyter_server>=2.19.0,<3.0.0、jupyter_ydoc>=4.1.1,<5.0.0、pycrdt、pycrdt-websocket>=0.16.4,<0.17.0、jupyter_events>=0.11.0、jupyter_server_fileid>=0.7.0,<1、jsonschema>=4.18.0。
- F-012: pyproject.toml:5 — 构建系统使用 hatchling（非 setuptools）。

## 包结构

- F-013: packages/collaboration/ — 前端 UI 协作包（协作者面板、光标、菜单、共享链接、用户信息面板）。
- F-014: packages/collaboration-extension/ — 前端 JupyterLab 扩展插件，注册用户菜单、协作面板、全局 Awareness 等。
- F-015: packages/collaborative-drive/ — 协作 Drive Token 定义包，导出 `ICollaborativeContentProvider`、`IGlobalAwareness`、`IDocumentProvider` 等核心接口。
- F-016: packages/docprovider/ — 核心文档提供器包，包含 WebSocketProvider、AwarenessProvider、ForkManager、RtcContentProvider 等核心实现。
- F-017: packages/docprovider-extension/ — 文档提供器扩展插件，注册 RTC 内容提供器、Y 文件/notebook 工厂、单元格执行器、ForkManager 等。
- F-018: projects/jupyter-server-ydoc/ — Python 后端服务，提供 WebSocket 服务、房间管理、YStore 持久化、文档会话/分叉/时间线 API。
- F-019: projects/jupyter-collaboration/ — Python 元包，用于整体安装。
- F-020: projects/jupyter-collaboration-ui/ — Python UI 扩展元数据包。
- F-021: projects/jupyter-docprovider/ — Python 文档提供器扩展包。

## 核心 Token 与接口定义

- F-022: collaborative-drive/src/tokens.ts:17-20 — 定义 `ICollaborativeContentProvider` Token，标识字符串为 `@jupyter/collaboration-extension:ICollaborativeContentProvider`。
- F-023: collaborative-drive/src/tokens.ts:25-27 — 定义 `IGlobalAwareness` Token，类型为 `IAwareness`，标识字符串为 `@jupyter/collaboration:IGlobalAwareness`。
- F-024: collaborative-drive/src/tokens.ts:29-36 — `ICollaborativeContentProvider` 接口继承 `IContentProvider`，包含 `sharedModelFactory` 和 `providers` Map 属性。
- F-025: collaborative-drive/src/tokens.ts:59-63 — `IDocumentProvider` 接口继承 `IDisposable`，包含 `ready: Promise<void>` 属性。
- F-026: docprovider/src/tokens.ts:15-20 — `IForkInfo` 接口包含 `description`、`root_roomid`、`synchronize`、`title` 字段。
- F-027: docprovider/src/tokens.ts:22-26 — `IForkCreationResponse` 接口包含 `fork_info`、`fork_roomid`、`sessionId` 字段。
- F-028: docprovider/src/tokens.ts:45-115 — `IForkManager` 接口定义了 `getProvider`、`createFork`、`getAllForks`、`deleteFork` 方法及 `forkAdded`/`forkDeleted` 信号。
- F-029: docprovider/src/tokens.ts:120-122 — `IForkManagerToken` 标识为 `@jupyter/docprovider:IForkManagerToken`。
- F-030: docprovider/src/tokens.ts:127-137 — `IDocumentProviderFactory` 接口包含 `create` 方法，创建 `IDocumentProvider & IForkProvider`。
- F-031: docprovider/src/tokens.ts:146-191 — `IDocumentProviderFactory.IOptions` 包含 url、path、contentType、format、model(YDocument)、user、translator、serverSettings、drive 参数。
- F-032: docprovider/src/tokens.ts:204-209 — `IAwarenessProvider` 接口包含 `awareness: IAwareness` 只读属性。
- F-033: docprovider/src/tokens.ts:261-266 — `ISessionClosePayload` 接口定义 reason 类型为 `'unknown_session' | 'version_mismatch' | 'initialization_error'`。

## WebSocketProvider（前端文档同步核心）

- F-034: docprovider/src/yprovider.ts:6 — 基于 `y-websocket` 的 `WebsocketProvider` 封装。
- F-035: docprovider/src/yprovider.ts:49 — `WebSocketProvider` 类实现 `IDocumentProvider` 和 `IForkProvider` 接口。
- F-036: docprovider/src/yprovider.ts:30 — WebSocket 端点 URL 为 `api/collaboration/room`。
- F-037: docprovider/src/yprovider.ts:36 — 加载超时时间 `LOAD_TIMEOUT` 为 5000ms，超时后弹出重试对话框。
- F-038: docprovider/src/yprovider.ts:41 — 原始消息类型常量 `RAW_MESSAGE_TYPE` 值为 2。
- F-039: docprovider/src/yprovider.ts:55-82 — 构造函数初始化路径、内容类型、格式、共享模型、Awareness，并在 user.ready 后设置用户信息，自动调用 `_connect()` 和 `_startLoadTimeout()`。
- F-040: docprovider/src/yprovider.ts:133-189 — `save()` 方法通过 WebSocket 发送 RAW 类型的 'save' 消息（带 saveId），等待服务端回复 success/skipped/failed 状态。
- F-041: docprovider/src/yprovider.ts:198-221 — `_connect()` 方法先调用 `requestDocSession` 获取会话信息（format/type/fileId/sessionId），再创建 `YWebsocketProvider`，room ID 格式为 `${format}:${type}:${fileId}`。
- F-042: docprovider/src/yprovider.ts:216 — YWebsocketProvider 配置 `disableBc: true`，禁用 BroadcastChannel 回退。
- F-043: docprovider/src/yprovider.ts:260-303 — `_onLoadTimeout` 弹出三按钮对话框：Cancel（取消加载）、Continue waiting（继续等待）、Retry（重连）。
- F-044: docprovider/src/yprovider.ts:305-323 — `connectToForkDoc()` 方法断开当前连接，连接到 fork 房间。
- F-045: docprovider/src/yprovider.ts:335-337 — 用户信息变更时通过 `awareness.setLocalStateField('user', user.identity)` 同步用户身份。

## RtcContentProvider（前端内容提供器）

- F-046: docprovider/src/ydrive.ts:31-32 — 通过 `PageConfig.getOption('disableRTC') === 'true'` 判断是否禁用 RTC。
- F-047: docprovider/src/ydrive.ts:34-40 — `IForkProvider` 接口定义 `connectToForkDoc`、`reconnect`、`contentType`、`format`、`save` 方法。
- F-048: docprovider/src/ydrive.ts:62 — `RtcContentProvider` 类实现 `IContentProvider` 接口。
- F-049: docprovider/src/ydrive.ts:70 — 内部维护 `_providers: Map<string, IDocumentProvider & IForkProvider>` 映射，key 格式为 `${format}:${type}:${path}`。
- F-050: docprovider/src/ydrive.ts:95-136 — `get()` 方法对于协作文档，通过 `Promise.all` 同时等待底层 drive.get(content:false) 和 provider.ready，不通过 REST 获取内容（内容通过 WebSocket 同步）。
- F-051: docprovider/src/ydrive.ts:148-179 — `save()` 方法优先调用 provider.save()，找不到 provider 时回退到 REST API save 并打印警告。
- F-052: docprovider/src/ydrive.ts:188-401 — `_onCreate` 回调在共享模型创建时执行：设置 autosave awareness 状态、创建 WebSocketProvider、注册路径变更处理、监听 hash 变更（服务端保存通知）、注册 disposed 清理。
- F-053: docprovider/src/ydrive.ts:196-203 — autosave 状态从 DocumentManager.autosave 或旧版 docmanagerSettings 获取，默认为 true。
- F-054: docprovider/src/ydrive.ts:205 — 通过 `sharedModel.awareness.setLocalStateField('autosave', getAutosave())` 同步自动保存偏好。
- F-055: docprovider/src/ydrive.ts:247-252 — 文档打开时将路径加入全局 Awareness 的 `documents` 字段列表。
- F-056: docprovider/src/ydrive.ts:306-313 — 文件重命名通过两种途径检测：sharedModel 的 stateChange 信号和 drive 的 fileChanged 信号，两种方式互补以避免竞态。
- F-057: docprovider/src/ydrive.ts:360-372 — hash 变更表示服务端保存（如协作者保存），触发 `_providerFileChanged` 信号通知观察者。
- F-058: docprovider/src/ydrive.ts:421 — `SharedModelFactory` 类实现 `ISharedModelFactory` 接口。
- F-059: docprovider/src/ydrive.ts:441 — `collaborative` 属性为 `!DISABLE_RTC`，决定是否启用协作模式。
- F-060: docprovider/src/ydrive.ts:449-457 — `registerDocumentFactory` 按 ContentType 注册工厂，重复注册抛出 Error。
- F-061: docprovider/src/ydrive.ts:472-476 — `createNew` 在非协作模式或 options.collaborative 为 false 时返回 undefined（回退到默认共享模型）。

## Awareness 提供器

- F-062: docprovider/src/awareness.ts:25-28 — `WebSocketAwarenessProvider` 继承 `YWebsocketProvider` 并实现 `IAwarenessProvider`。
- F-063: docprovider/src/awareness.ts:35-37 — 构造函数调用 super(url, roomID, awareness.doc, {awareness})，直接使用传入的 awareness 对象。
- F-064: docprovider/src/awareness.ts:42-45 — 监听 user.ready 和 userChanged 事件，同步用户身份到 awareness。
- F-065: docprovider/src/awareness.ts:62-64 — `_onUserChanged` 通过 `awareness.setLocalStateField('user', user.identity)` 设置本地用户状态。

## ForkManager（分叉管理）

- F-066: docprovider/src/forkManager.ts:20-21 — Fork 事件 Schema URI 为 `https://schema.jupyter.org/jupyter_collaboration/fork/v1`。
- F-067: docprovider/src/forkManager.ts:23 — `ForkManager` 类实现 `IForkManager` 接口。
- F-068: docprovider/src/forkManager.ts:28 — 构造函数通过 `eventManager.stream.connect` 监听服务端事件流。
- F-069: docprovider/src/forkManager.ts:49-67 — `createFork()` 发送 PUT 请求到 `api/collaboration/fork/{rootId}`，body 包含 title/description/synchronize。
- F-070: docprovider/src/forkManager.ts:69-78 — `getAllForks()` 发送 GET 请求到 `api/collaboration/fork/{rootId}`。
- F-071: docprovider/src/forkManager.ts:80-86 — `deleteFork()` 发送 DELETE 请求到 `api/collaboration/fork/{forkId}?merge=true/false`。
- F-072: docprovider/src/forkManager.ts:87-102 — `getProvider()` 从 contentProvider.providers Map 中按 `${format}:${type}:${documentPath}` 查找文档提供器。
- F-073: docprovider/src/forkManager.ts:104-118 — `_handleEvent` 监听 Fork 事件流，根据 action（create/delete）发射 forkAdded/forkDeleted 信号。

## API 请求模块

- F-074: docprovider/src/requests.ts:13 — 文档会话端点：`api/collaboration/session`。
- F-075: docprovider/src/requests.ts:14 — 撤销/重做端点：`api/collaboration/undo_redo`。
- F-076: docprovider/src/requests.ts:15 — 时间线端点：`api/collaboration/timeline`。
- F-077: docprovider/src/requests.ts:17 — Fork 端点：`api/collaboration/fork`。
- F-078: docprovider/src/requests.ts:22-39 — `ISessionModel` 接口包含 format、type、fileId、sessionId 字段。
- F-079: docprovider/src/requests.ts:48-79 — `requestAPI()` 通用 API 请求函数，处理网络错误和 JSON 解析错误。
- F-080: docprovider/src/requests.ts:81-120 — `requestDocSession()` 发送 PUT 请求创建/获取文档会话，传入 format/type/path。
- F-081: docprovider/src/requests.ts:122-144 — `requestDocumentTimeline()` 发送 GET 请求获取文档时间线。
- F-082: docprovider/src/requests.ts:146-186 — `requestUndoRedo()` 发送 PUT 请求执行 undo/redo/restore 操作，参数为 roomid、action、steps、forkRoom。

## Python 后端：房间管理

- F-083: projects/jupyter-server-ydoc/jupyter_server_ydoc/rooms.py:28 — `DocumentRoom` 类继承 `YRoom`（来自 pycrdt-websocket），表示可能持久化的文档房间（如 notebook）。
- F-084: projects/jupyter-server-ydoc/jupyter_server_ydoc/rooms.py:33-46 — 构造函数接收 room_id、file_format、file_type、file(FileLoader)、logger、ystore、log、save_delay、document_load_progressively、notebook_output_delay_threshold_mb、exception_handler。
- F-085: projects/jupyter-server-ydoc/jupyter_server_ydoc/rooms.py:53 — 通过 `YDOCS.get(self._file_type, YFILE)(self.ydoc, self.awareness)` 创建对应的 Y 文档对象。
- F-086: projects/jupyter-server-ydoc/jupyter_server_ydoc/rooms.py:67 — 使用 `asyncio.Lock()` 作为更新锁 `_update_lock`。
- F-087: projects/jupyter-server-ydoc/jupyter_server_ydoc/rooms.py:72 — `_document_progressively_loaded: asyncio.Future[None]` 用于渐进式加载完成通知。
- F-088: projects/jupyter-server-ydoc/jupyter_server_ydoc/rooms.py:75-76 — 监听文档变更 `_document.observe(self._on_document_change)` 和文件带外变更 `_file.observe(...)`。
- F-089: projects/jupyter-server-ydoc/jupyter_server_ydoc/rooms.py:111-219 — `initialize()` 方法线程安全：优先从 YStore 加载 Y 更新，若 YStore 内容与磁盘文件不同步则从磁盘加载，支持渐进式加载。
- F-090: projects/jupyter-server-ydoc/jupyter_server_ydoc/rooms.py:137-157 — YStore 存在时先尝试 `ystore.apply_updates(self.ydoc)`，YDocNotFound 异常时回退到磁盘加载。
- F-091: projects/jupyter-server-ydoc/jupyter_server_ydoc/rooms.py:165 — 从 YStore 加载后比较文档内容与磁盘内容，不一致则标记为需要从源重新加载。
- F-092: projects/jupyter-server-ydoc/jupyter_server_ydoc/rooms.py:187-206 — 渐进式加载模式下调用 `_finish_progressive_initialization`，设置 initialized 事件、ready=True、等待 ydoc_observed、设置 finish 事件。
- F-093: projects/jupyter-server-ydoc/jupyter_server_ydoc/rooms.py:245-276 — `_apply_deterministic_source_content` 使用 `Doc(client_id=0)` 创建确定性源文档（固定 client_id=0），确保从磁盘重建时产生相同的 Yjs 历史，避免重连客户端合并重复内容。
- F-094: projects/jupyter-server-ydoc/jupyter_server_ydoc/rooms.py:316-340 — `_handle_sync_message_error` 拦截 "block parent" 冲突（过期客户端重连到重建房间），发送 RAW 类型 conflict 通知，返回 True 保持服务循环继续。
- F-095: projects/jupyter-server-ydoc/jupyter_server_ydoc/rooms.py:342-360 — `_on_outofband_change` 处理文件带外变更（外部直接修改文件），从磁盘重新加载内容覆盖房间。
- F-096: projects/jupyter-server-ydoc/jupyter_server_ydoc/rooms.py:383-404 — `_on_document_change` 收集所有客户端的 autosave awareness 状态，任一客户端开启 autosave 即启用，变更防抖创建保存任务。
- F-097: projects/jupyter-server-ydoc/jupyter_server_ydoc/rooms.py:418-488 — `_maybe_save_document` 实现防抖保存（默认 save_delay 秒后保存），save_now=True 时立即保存，处理 OutOfBandChanges 异常。
- F-098: projects/jupyter-server-ydoc/jupyter_server_ydoc/rooms.py:461 — 保存成功后设置 `self._document.hash = saved_model["hash"]`。
- F-099: projects/jupyter-server-ydoc/jupyter_server_ydoc/rooms.py:491 — `TransientRoom` 类继承 `YRoom`，用于共享状态（如 awareness），不关联文件。
- F-100: projects/jupyter-server-ydoc/jupyter_server_ydoc/rooms.py:160 — 特殊房间 ID `JupyterLab:globalAwareness` 用于全局用户状态共享。

## Python 后端：WebSocket Handler

- F-101: projects/jupyter-server-ydoc/jupyter_server_ydoc/handlers.py:49 — `YDocWebSocketHandler` 继承 `WebSocketHandler` 和 `JupyterHandler`，适配 Tornado WebSocket API 到 pycrdt-websocket 的异步迭代器协议。
- F-102: projects/jupyter-server-ydoc/jupyter_server_ydoc/handlers.py:71 — 设置 `auth_resource = "contents"` 以启用 `@authorized` 装饰器。
- F-103: projects/jupyter-server-ydoc/jupyter_server_ydoc/handlers.py:73-74 — 使用 `asyncio.Queue` 作为消息队列，`_background_tasks` 集合管理后台任务。
- F-104: projects/jupyter-server-ydoc/jupyter_server_ydoc/handlers.py:87-183 — `prepare()` 方法：启动 WebSocket 服务器、解析 room_id、创建或获取房间，room_id 含 `:` 数量>=2 为 DocumentRoom，否则为 TransientRoom。
- F-105: projects/jupyter-server-ydoc/jupyter_server_ydoc/handlers.py:130-134 — DocumentRoom 的 YStore 路径格式为 `f".{file_type}:{file_id}.y"`。
- F-106: projects/jupyter-server-ydoc/jupyter_server_ydoc/handlers.py:191-209 — `initialize()` 接收 ywebsocket_server、file_loaders、ystore_class、room_locks、cleanup_delay(默认60s)、save_delay(默认1s)、load_progressively、output_threshold_mb(默认100) 等参数。
- F-107: projects/jupyter-server-ydoc/jupyter_server_ydoc/handlers.py:224 — `max_message_size` 覆盖为 1GB（1024*1024*1024）。
- F-108: projects/jupyter-server-ydoc/jupyter_server_ydoc/handlers.py:226-235 — 实现 `__aiter__`/`__anext__` 异步迭代器协议，从消息队列获取消息，空消息表示停止迭代。
- F-109: projects/jupyter-server-ydoc/jupyter_server_ydoc/handlers.py:246-345 — `open()` 方法：验证会话兼容性、取消清理任务、初始化房间、启动服务、发射 join 事件。
- F-110: projects/jupyter-server-ydoc/jupyter_server_ydoc/handlers.py:258-265 — 使用 `save_current_session` 持久化当前会话信息（SERVER_SESSION UUID + YDOC_SERVER_VERSION + document_version）。
- F-111: projects/jupyter-server-ydoc/jupyter_server_ydoc/handlers.py:266-284 — 会话不兼容时关闭 WebSocket（code 1003），payload 包含 reason/sessionId/reloadable，让客户端提示用户刷新。
- F-112: projects/jupyter-server-ydoc/jupyter_server_ydoc/handlers.py:302-332 — 初始化失败时使用自定义错误码：4404(文件未找到)、4400(错误请求)、4500(内部错误)。
- F-113: projects/jupyter-server-ydoc/jupyter_server_ydoc/handlers.py:363-396 — `on_message()` 解析消息头，RAW 类型消息处理 save 请求（回复 success/skipped/failed），其他消息放入队列。
- F-114: projects/jupyter-server-ydoc/jupyter_server_ydoc/handlers.py:404-416 — `on_close()` 放入空消息停止迭代，最后一个客户端离开时创建延迟清理任务（cleanup_delay 秒后清理房间）。
- F-115: projects/jupyter-server-ydoc/jupyter_server_ydoc/handlers.py:437-473 — `_clean_room()` 延迟清理：等待 cleanup_delay 后删除房间、移除无订阅的文件加载器、删除房间锁。
- F-116: projects/jupyter-server-ydoc/jupyter_server_ydoc/handlers.py:475-497 — `_on_global_awareness_event` 监听全局 Awareness 变更，维护 `connected_users` 字典映射 clientID→用户名。

## Python 后端：REST API Handlers

- F-117: projects/jupyter-server-ydoc/jupyter_server_ydoc/handlers.py:506 — `DocSessionHandler` 继承 `APIHandler`，处理文档会话创建/查询。
- F-118: projects/jupyter-server-ydoc/jupyter_server_ydoc/handlers.py:515-560 — PUT 方法：根据 path 获取或创建 fileId 索引，返回 format/type/fileId/sessionId，已索引文件返回 200，新索引返回 201，不存在返回 404。
- F-119: projects/jupyter-server-ydoc/jupyter_server_ydoc/handlers.py:563 — `TimelineHandler` 提供文档时间线功能。
- F-120: projects/jupyter-server-ydoc/jupyter_server_ydoc/handlers.py:574-627 — GET 方法：创建临时 fork 文档，从 YStore 重放更新记录时间戳（undo_stack 增长时），返回 roomId/timestamps/forkRoom/sessionId。
- F-121: projects/jupyter-server-ydoc/jupyter_server_ydoc/handlers.py:630 — `UndoRedoHandler` 处理 undo/redo/restore 操作。
- F-122: projects/jupyter-server-ydoc/jupyter_server_ydoc/handlers.py:638-683 — PUT 方法：查询参数 action/steps/forkRoom，支持 undo（撤销 steps 步）、redo（重做 steps 步）、restore（清理 undo manager）。
- F-123: projects/jupyter-server-ydoc/jupyter_server_ydoc/handlers.py:706 — `DocForkHandler` 处理文档分叉的创建、删除、查询。
- F-124: projects/jupyter-server-ydoc/jupyter_server_ydoc/handlers.py:724-734 — GET 方法：返回指定 root_roomid 的所有 fork 信息字典。
- F-125: projects/jupyter-server-ydoc/jupyter_server_ydoc/handlers.py:738-775 — PUT 方法：创建 fork，复制根文档状态，synchronize=true 时通过 observe 保持 fork 与根文档同步，注册 fork 房间并启动。
- F-126: projects/jupyter-server-ydoc/jupyter_server_ydoc/handlers.py:779-798 — DELETE 方法：删除 fork，merge=true 时将 fork 更新应用回根文档。

## Python 后端：YStore 持久化

- F-127: projects/jupyter-server-ydoc/jupyter_server_ydoc/stores.py:14-15 — `TempFileYStore` 继承 LoggingConfigurable 和 pycrdt 的 TempFileYStore，prefix_dir 为 `jupyter_ystore_`。
- F-128: projects/jupyter-server-ydoc/jupyter_server_ydoc/stores.py:22-44 — `SQLiteYStore` 继承 LoggingConfigurable 和 pycrdt 的 SQLiteYStore，db_path 默认 `.jupyter_ystore.db`，支持 `squash_after_inactivity_of` 配置压缩历史。

## Python 后端：ExtensionApp 配置

- F-129: projects/jupyter-server-ydoc/jupyter_server_ydoc/app.py:38-39 — `YDocExtension` 继承 `ExtensionApp`，name 为 `jupyter_server_ydoc`，app_name 为 "Collaboration"。
- F-130: projects/jupyter-server-ydoc/jupyter_server_ydoc/app.py:45 — `disable_rtc` Bool 配置项，默认 False。
- F-131: projects/jupyter-server-ydoc/jupyter_server_ydoc/app.py:47-53 — `file_poll_interval` Float 配置项，默认 1 秒，控制磁盘文件变更轮询间隔。
- F-132: projects/jupyter-server-ydoc/jupyter_server_ydoc/app.py:63-69 — `document_cleanup_delay` Float 配置项，默认 60 秒，控制客户端全部断开后房间内存保留时间。
- F-133: projects/jupyter-server-ydoc/jupyter_server_ydoc/app.py:71-77 — `document_save_delay` Float 配置项，默认 1 秒，控制变更防抖保存延迟。
- F-134: projects/jupyter-server-ydoc/jupyter_server_ydoc/app.py:79-85 — `document_load_progressively` Bool 配置项，默认 False，启用渐进式文档加载。
- F-135: projects/jupyter-server-ydoc/jupyter_server_ydoc/app.py:87-93 — `notebook_output_delay_threshold_mb` Float 配置项，默认 100MB，超过此大小的 notebook 输出延迟加载。
- F-136: projects/jupyter-server-ydoc/jupyter_server_ydoc/app.py:95-102 — `ystore_class` Type 配置项，默认 SQLiteYStore。
- F-137: projects/jupyter-server-ydoc/jupyter_server_ydoc/app.py:104-110 — `server_side_execution` Bool 配置项，默认 False，启用后通过 REST API 在服务端执行 notebook 单元格。
- F-138: projects/jupyter-server-ydoc/jupyter_server_ydoc/app.py:146-216 — `initialize_handlers()` 注册 5 组路由：fork、room(WebSocket)、session、timeline、undo_redo。
- F-139: projects/jupyter-server-ydoc/jupyter_server_ydoc/app.py:218-319 — `get_document()` 方法：通过 room_id 或 path+content_type+file_format 获取共享模型，copy=true 返回 fork（不传播更改），create=true 自动创建不存在的房间。

## Python 后端：工具函数

- F-140: projects/jupyter-server-ydoc/jupyter_server_ydoc/utils.py:22 — `SERVER_SESSION` 在模块加载时生成 UUID4，用于标识服务端会话版本。
- F-141: projects/jupyter-server-ydoc/jupyter_server_ydoc/utils.py:23 — `YDOC_SERVER_VERSION` 取自包的 `__version__`。
- F-142: projects/jupyter-server-ydoc/jupyter_server_ydoc/utils.py:26-30 — `MessageType` IntEnum 定义：SYNC=0, AWARENESS=1, RAW=2, CHAT=125。
- F-143: projects/jupyter-server-ydoc/jupyter_server_ydoc/utils.py:33-38 — `LogLevel` Enum 定义：INFO、DEBUG、WARNING、ERROR、CRITICAL。
- F-144: projects/jupyter-server-ydoc/jupyter_server_ydoc/utils.py:41 — `OutOfBandChanges` 异常类，用于文件带外变更信号。
- F-145: projects/jupyter-server-ydoc/jupyter_server_ydoc/utils.py:53-66 — `decode_file_path` 按 `:` 分割路径为 (format, file_type, file_id) 三元组，最多分割 2 次。
- F-146: projects/jupyter-server-ydoc/jupyter_server_ydoc/utils.py:69-82 — `encode_file_path` 将 format/type/file_id 编码为 `f"{format}:{file_type}:{file_id}"` 格式。
- F-147: projects/jupyter-server-ydoc/jupyter_server_ydoc/utils.py:90-115 — 会话存储默认路径为 `<root_dir>/.jupyter/collaboration_sessions.json`，可通过 session_store_path 配置。

## Python 后端：FileLoader

- F-148: projects/jupyter-server-ydoc/jupyter_server_ydoc/loaders.py:24 — `FileLoader` 类集中管理对单个文件的操作。
- F-149: projects/jupyter-server-ydoc/jupyter_server_ydoc/loaders.py:41 — 使用 `asyncio.Lock()` 保护文件操作。
- F-150: projects/jupyter-server-ydoc/jupyter_server_ydoc/loaders.py:49-50 — 维护 `_subscriptions` 和 `_filepath_subscriptions` 字典，支持多房间订阅同一文件。
- F-151: projects/jupyter-server-ydoc/jupyter_server_ydoc/loaders.py:52 — poll_interval 非 None 时创建 `_watch_file()` 异步任务轮询文件变更。
- F-152: projects/jupyter-server-ydoc/jupyter_server_ydoc/loaders.py:66-69 — path 属性通过 file_id_manager 从 file_id 反查路径，路径不存在时抛出 RuntimeError。
- F-153: projects/jupyter-server-ydoc/jupyter_server_ydoc/loaders.py:76 — `number_of_subscriptions` 返回订阅该文件的房间数量。

## 前端协作 UI

- F-154: packages/collaboration/src/index.ts:8-13 — collaboration 包导出 tokens、collaboratorspanel、cursors、menu、sharedlink、userinfopanel、users-item 模块。
- F-155: packages/collaboration/src/cursors.ts:9-18 — 基于 CodeMirror 6 扩展实现远程光标和选区显示，使用 @codemirror/state 和 @codemirror/view。
- F-156: packages/collaboration/src/cursors.ts:23-29 — 使用 Yjs 的 RelativePosition（createAbsolutePositionFromRelativePosition/createRelativePositionFromTypeIndex）转换光标位置，确保在文档编辑时光标位置正确映射。
- F-157: packages/collaboration-extension/src/index.ts:22-29 — 注册 6 个前端插件：userMenuPlugin、menuBarPlugin、rtcGlobalAwarenessPlugin、rtcPanelPlugin、sharedLink、userEditorCursors。
- F-158: packages/docprovider-extension/src/index.ts:27-37 — 注册 9 个前端插件：rtcContentProvider、yfile、ynotebook、logger、notebookCellExecutor、statusBarTimeline、forkManagerPlugin、documentProviderFactoryPlugin、awarenessProviderFactoryPlugin。
- F-159: packages/docprovider/src/notebookCellExecutor.ts:16 — `NotebookCellServerExecutor` 实现 `INotebookCellExecutor`，通过服务端 REST API 执行单元格（服务端执行模式）。

## 事件系统

- F-160: projects/jupyter-server-ydoc/jupyter_server_ydoc/utils.py:14-21 — 定义三种事件 Schema URI：session/v1、awareness/v1、fork/v1，对应的 YAML Schema 文件位于 events/ 目录。
- F-161: projects/jupyter-server-ydoc/jupyter_server_ydoc/app.py:127-129 — initialize() 时注册三种事件 Schema 到 event_logger。
- F-162: projects/jupyter-server-ydoc/jupyter_server_ydoc/rooms.py:278-285 — `_emit()` 方法通过 event_logger 发射事件，包含 level、room、path、action、msg 字段。
