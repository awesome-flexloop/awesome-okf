---
type: Facts
okf_version: '0.2'
title: jupyter_server 源码事实清单
tags:
- jupyter
- server
- backend
- tornado
- websocket
generated: '2026-08-22'
sources:
- ../../../../../external/libs/jupyter/jupyter_server/pyproject.toml
- ../../../../../external/libs/jupyter/jupyter_server/jupyter_server/serverapp.py
- ../../../../../external/libs/jupyter/jupyter_server/jupyter_server/services/kernels/kernelmanager.py
- ../../../../../external/libs/jupyter/jupyter_server/jupyter_server/services/contents/manager.py
- ../../../../../external/libs/jupyter/jupyter_server/jupyter_server/services/contents/filemanager.py
- ../../../../../external/libs/jupyter/jupyter_server/jupyter_server/services/contents/largefilemanager.py
- ../../../../../external/libs/jupyter/jupyter_server/jupyter_server/services/contents/checkpoints.py
- ../../../../../external/libs/jupyter/jupyter_server/jupyter_server/services/contents/handlers.py
- ../../../../../external/libs/jupyter/jupyter_server/jupyter_server/services/sessions/sessionmanager.py
- ../../../../../external/libs/jupyter/jupyter_server/jupyter_server/services/sessions/handlers.py
- ../../../../../external/libs/jupyter/jupyter_server/jupyter_server/services/kernels/handlers.py
- ../../../../../external/libs/jupyter/jupyter_server/jupyter_server/services/kernels/websocket.py
- ../../../../../external/libs/jupyter/jupyter_server/jupyter_server/services/kernels/connection/base.py
- ../../../../../external/libs/jupyter/jupyter_server/jupyter_server/services/kernels/connection/channels.py
- ../../../../../external/libs/jupyter/jupyter_server/jupyter_server/services/kernels/connection/abc.py
- ../../../../../external/libs/jupyter/jupyter_server/jupyter_server/extension/manager.py
- ../../../../../external/libs/jupyter/jupyter_server/jupyter_server/extension/application.py
- ../../../../../external/libs/jupyter/jupyter_server/jupyter_server/extension/handler.py
- ../../../../../external/libs/jupyter/jupyter_server/jupyter_server/auth/identity.py
- ../../../../../external/libs/jupyter/jupyter_server/jupyter_server/auth/authorizer.py
- ../../../../../external/libs/jupyter/jupyter_server/jupyter_server/auth/decorator.py
- ../../../../../external/libs/jupyter/jupyter_server/jupyter_server/auth/login.py
- ../../../../../external/libs/jupyter/jupyter_server/jupyter_server/gateway/gateway_client.py
- ../../../../../external/libs/jupyter/jupyter_server/jupyter_server/gateway/managers.py
- ../../../../../external/libs/jupyter/jupyter_server/jupyter_server/gateway/connections.py
- ../../../../../external/libs/jupyter/jupyter_server/jupyter_server/base/handlers.py
- ../../../../../external/libs/jupyter/jupyter_server/jupyter_server/base/websocket.py
- ../../../../../external/libs/jupyter/jupyter_server/jupyter_server/terminal/terminalmanager.py
- ../../../../../external/libs/jupyter/jupyter_server/jupyter_server/prometheus/metrics.py
- ../../../../../external/libs/jupyter/jupyter_server/jupyter_server/config_manager.py
- ../../../../../external/libs/jupyter/jupyter_server/jupyter_server/__init__.py
---

# jupyter_server 源码事实清单

## 项目元数据

- F-001: pyproject.toml:5-11 — 项目名称为 jupyter_server，描述为 "The backend—i.e. core services, APIs, and REST endpoints—to Jupyter web applications."
- F-002: pyproject.toml:24 — 要求 Python 版本 >=3.10
- F-003: pyproject.toml:9 — 许可证为 BSD License
- F-004: pyproject.toml:1-3 — 构建系统使用 hatchling >=1.11，build-backend 为 hatchling.build
- F-005: _version.py:9 — 当前版本为 2.21.0.dev0（开发版）
- F-006: pyproject.toml:25-49 — 核心运行时依赖包括 anyio>=3.1.0, jinja2>=3.0.3, jupyter_client>=7.4.4, jupyter_core>=4.12, pyzmq>=24, tornado>=6.2.0, traitlets>=5.6.0, terminado>=0.8.3, prometheus_client>=0.9 等
- F-007: pyproject.toml:31 — jupyter_server_terminals>=0.4.4 是独立依赖包（终端功能已从 jupyter_server 拆分）
- F-008: pyproject.toml:47 — jupyter_events>=0.11.0 用于结构化事件日志
- F-009: pyproject.toml:46 — websocket-client>=1.7 用于 Gateway WebSocket 客户端连接
- F-010: pyproject.toml:92-93 — CLI 入口点 jupyter-server 映射到 jupyter_server.serverapp:main
- F-011: __init__.py:12 — 默认服务器端口常量 DEFAULT_JUPYTER_SERVER_PORT = 8888
- F-012: __init__.py:13 — 事件 URI 常量 JUPYTER_SERVER_EVENTS_URI = "https://events.jupyter.org/jupyter_server"
- F-013: pyproject.toml:14 — 开发状态分类为 Production/Stable（5 - Production/Stable）

## 目录结构

- F-014: jupyter_server/ — 顶层 Python 包目录
- F-015: jupyter_server/auth/ — 认证与授权模块，包含 identity.py、authorizer.py、decorator.py、login.py、logout.py、security.py
- F-016: jupyter_server/base/ — 基础处理器，包含 handlers.py（AuthenticatedHandler/JupyterHandler/APIHandler）、websocket.py（WebSocketMixin）、zmqhandlers.py、call_context.py
- F-017: jupyter_server/services/ — 核心服务目录，包含 api/、config/、contents/、events/、kernels/、kernelspecs/、nbconvert/、security/、sessions/ 子模块
- F-018: jupyter_server/services/kernels/ — 内核管理服务，含 kernelmanager.py、handlers.py、websocket.py、connection/ 子目录
- F-019: jupyter_server/services/kernels/connection/ — 内核 WebSocket 连接层，含 abc.py（抽象基类）、base.py（基础实现）、channels.py（ZMQ 通道实现）
- F-020: jupyter_server/services/contents/ — 内容管理服务，含 manager.py（抽象基类）、filemanager.py（文件系统实现）、largefilemanager.py（大文件分块上传）、filecheckpoints.py、checkpoints.py、handlers.py、fileio.py
- F-021: jupyter_server/services/sessions/ — 会话管理服务，含 sessionmanager.py、handlers.py
- F-022: jupyter_server/extension/ — 扩展系统，含 application.py（ExtensionApp 基类）、manager.py（ExtensionManager/ExtensionPackage/ExtensionPoint）、handler.py（ExtensionHandlerMixin）、config.py、serverextension.py、utils.py
- F-023: jupyter_server/gateway/ — 远程内核网关支持，含 gateway_client.py（GatewayClient 单例配置）、managers.py（GatewayMappingKernelManager 等）、connections.py（GatewayWebSocketConnection）、handlers.py
- F-024: jupyter_server/terminal/ — 终端模块仅做转发，terminalmanager.py 直接从 jupyter_server_terminals 导入 TerminalManager
- F-025: jupyter_server/files/ — 文件服务 handlers.py
- F-026: jupyter_server/kernelspecs/ — 内核规格 handlers.py
- F-027: jupyter_server/nbconvert/ — Notebook 转换 handlers.py
- F-028: jupyter_server/prometheus/ — Prometheus 指标，含 metrics.py、log_functions.py
- F-029: jupyter_server/view/ — 视图 handlers.py
- F-030: jupyter_server/event_schemas/ — 事件 Schema YAML 文件，含 contents_service/v1.yaml、gateway_client/v1.yaml、kernel_actions/v1.yaml
- F-031: jupyter_server/templates/ — Jinja2 HTML 模板，含 login.html、logout.html、error.html、main.html、page.html、404.html、view.html、browser-open.html
- F-032: jupyter_server/static/ — 静态资源，含 favicons/、logo/、style/ 目录
- F-033: jupyter_server/i18n/ — 国际化支持，含 zh_CN/ 中文翻译等

## ServerApp 核心

- F-034: serverapp.py:870 — ServerApp 继承自 JupyterApp（jupyter_core），是整个服务器的应用入口类
- F-035: serverapp.py:873 — ServerApp.name = "jupyter-server"
- F-036: serverapp.py:184-206 — JUPYTER_SERVICE_HANDLERS 字典定义了所有内置服务及其 handler 模块映射，包含 auth/api/config/contents/files/kernels/kernelspecs/nbconvert/security/sessions/shutdown/view/events
- F-037: serverapp.py:928-942 — default_services 元组列出了默认启用的 13 个服务：api、auth、config、contents、files、kernels、kernelspecs、nbconvert、security、sessions、shutdown、view、events
- F-038: serverapp.py:906-923 — ServerApp 定义了 4 个子命令：list（列出运行中服务器）、stop（停止服务器）、password（设置密码）、extension（管理扩展）
- F-039: serverapp.py:240 — ServerWebApplication 继承自 tornado.web.Application，封装了 Tornado Web 应用初始化
- F-040: serverapp.py:307-323 — ServerWebApplication.__init__ 中检查所有 handler 方法是否有认证装饰器（@allow_unauthenticated、@ws_authenticated 或 @web.authenticated），未装饰的端点在严格模式下会抛异常
- F-041: serverapp.py:486-542 — init_handlers 方法按优先级加载 handler：extra_services → default_services → contents_manager 额外 handler → identity_provider handler → base handlers → 根路径重定向 → 404 handler
- F-042: serverapp.py:413-476 — Tornado settings 字典包含 kernel_manager、contents_manager、session_manager、kernel_spec_manager、config_manager、authorizer、identity_provider、event_logger、kernel_websocket_connection_class 等核心管理器引用
- F-043: serverapp.py:1014-1018 — 默认监听 IP 为 "localhost"，默认端口 8888
- F-044: serverapp.py:1617-1622 — contents_manager_class 默认值为 AsyncLargeFileManager（大文件异步内容管理器）
- F-045: serverapp.py:1624-1634 — kernel_manager_class 在 gateway 启用时为 GatewayMappingKernelManager，否则为 AsyncMappingKernelManager
- F-046: serverapp.py:1636-1645 — session_manager_class 在 gateway 启用时为 GatewaySessionManager，否则为 SessionManager
- F-047: serverapp.py:1647-1659 — kernel_websocket_connection_class 在 gateway 启用时为 GatewayWebSocketConnection，否则为 ZMQChannelsWebsocketConnection
- F-048: serverapp.py:1706-1710 — kernel_spec_manager_class 在 gateway 启用时为 GatewayKernelSpecManager，否则为 KernelSpecManager（jupyter_client）
- F-049: serverapp.py:1729-1734 — authorizer_class 默认值为 AllowAllAuthorizer
- F-050: serverapp.py:1736-1741 — identity_provider_class 默认值为 PasswordIdentityProvider
- F-051: serverapp.py:2082-2197 — init_configurables 方法初始化所有核心管理器实例：kernel_spec_manager → kernel_manager → contents_manager → session_manager → config_manager → identity_provider → authorizer
- F-052: serverapp.py:2817-2886 — initialize 方法按序执行：_init_asyncio_patch → super().initialize → init_ioloop → find_server_extensions → init_logging → init_event_logger → init_server_extensions → starter_extension 配置 → init_resources → init_configurables → init_components → init_webapp → init_signal → load_server_extensions → init_mime_overrides → init_shutdown_no_activity → init_metrics → init_httpserver
- F-053: serverapp.py:2771-2793 — _init_asyncio_patch 在 Windows 上将 asyncio 事件循环策略从 ProactorEventLoop 切换为 SelectorEventLoop，以兼容 Tornado + pyzmq
- F-054: serverapp.py:2232-2307 — init_webapp 方法创建 ServerWebApplication 实例，传入所有管理器和配置
- F-055: serverapp.py:2645-2664 — init_httpserver 创建 tornado.httpserver.HTTPServer 实例，配置 ssl_options、xheaders（trust_xheaders）、max_body_size（默认 512MB）、max_buffer_size（默认 512MB）
- F-056: serverapp.py:2667-2669 — HTTP 服务器端口绑定通过 io_loop.add_callback 调度到事件循环中执行
- F-057: serverapp.py:3231-3246 — start_ioloop 启动 Tornado IOLoop，Windows 上添加 5 秒 PeriodicCallback 唤醒以处理信号
- F-058: serverapp.py:3248-3257 — _post_start 异步钩子在事件循环运行后启动所有扩展的 start 任务
- F-059: serverapp.py:3259-3265 — start 方法调用 start_app()（打印信息、写服务器信息文件、写浏览器打开文件、可选启动浏览器）然后 start_ioloop()
- F-060: serverapp.py:3202-3229 — _cleanup 异步方法按序清理：删除服务器信息文件 → 删除浏览器打开文件 → 停止扩展 → 关闭所有内核 → 关闭 WebSocket 连接 → 停止 HTTP 服务器
- F-061: serverapp.py:544-561 — ServerWebApplication.last_activity() 追踪服务器最后活动时间，来源包括启动时间、内核最后活动、所有以 _last_activity 结尾的 settings 值、last_activity_times 字典
- F-062: serverapp.py:2604-2630 — shutdown_no_activity 定期检查（60秒周期），无内核运行且无活动超过 shutdown_no_activity_timeout 时自动关闭服务器
- F-063: serverapp.py:1149-1169 — cookie_secret 默认从 cookie_secret_file 读取，首次启动时生成 32 字节随机密钥并持久化
- F-064: serverapp.py:1327-1350 — allow_unauthenticated_access 默认为 True（2.0 版本），可通过 JUPYTER_SERVER_ALLOW_UNAUTHENTICATED_ACCESS 环境变量控制
- F-065: serverapp.py:1352-1400 — allow_remote_access 默认根据绑定 IP 自动判断：绑定到 loopback 时禁止远程访问，绑定到所有接口时允许
- F-066: serverapp.py:3289-3325 — list_running_servers 扫描 runtime_dir 中 jpserver-*.json 文件，验证 PID 是否存活
- F-067: serverapp.py:3331 — main = launch_new_instance = ServerApp.launch_instance，即 CLI 入口点
- F-068: serverapp.py:1530-1547 — base_url 默认为 "/"，自动补全前后斜杠
- F-069: serverapp.py:2949-2955 — write_server_info_file 将服务器信息（URL、端口、token、root_dir、pid、version 等）写入 jpserver-{pid}.json
- F-070: serverapp.py:2449-2458 — init_signal 设置 SIGINT（Ctrl-C）处理，首次按提示关闭信息，第二次强制退出；SIGTERM 优雅关闭
- F-071: serverapp.py:1238-1258 — max_body_size 和 max_buffer_size 默认均为 512MB（512 * 1024 * 1024 字节）
- F-072: serverapp.py:2214-2230 — init_event_logger 注册三个核心事件 schema：contents_service/v1、gateway_client/v1、kernel_actions/v1

## 内核服务（Kernels）

- F-073: kernelmanager.py:58 — MappingKernelManager 继承自 jupyter_client 的 MultiKernelManager，增加了文件映射、HTTP 错误处理、消息过滤功能
- F-074: kernelmanager.py:65-67 — MappingKernelManager 默认 kernel_manager_class 为 jupyter_client.ioloop.IOLoopKernelManager
- F-075: kernelmanager.py:768 — AsyncMappingKernelManager 同时继承 MappingKernelManager 和 AsyncMultiKernelManager（jupyter_client），是默认异步内核管理器
- F-076: kernelmanager.py:771-773 — AsyncMappingKernelManager 默认 kernel_manager_class 为 ServerKernelManager（自定义子类）
- F-077: kernelmanager.py:870 — ServerKernelManager 继承自 AsyncIOLoopKernelManager（jupyter_client），增加 execution_state、reason、last_activity 属性和事件发射能力
- F-078: kernelmanager.py:110-137 — 内核闲置淘汰（culling）配置：cull_idle_timeout（默认0/禁用）、cull_interval（默认300秒/5分钟）、cull_connected（默认False，不淘汰已连接内核）、cull_busy（默认False，不淘汰繁忙内核）
- F-079: kernelmanager.py:139-150 — buffer_offline_messages 默认为 True，前端断开连接时缓冲内核消息，重连时回放
- F-080: kernelmanager.py:152-164 — kernel_info_timeout 默认 60 秒，启动/重启内核时等待 kernel_info 响应的超时时间
- F-081: kernelmanager.py:71-81 — transport_encryption 支持 CurveZMQ 加密，可选值 disabled/auto/required
- F-082: kernelmanager.py:235-298 — _async_start_kernel 方法在启动内核时设置 execution_state="starting"，记录 last_activity，创建异步任务等待内核就绪，启动活动监控和死亡回调
- F-083: kernelmanager.py:360-397 — start_buffering 方法为断开连接的前端在内核 ZMQ 通道上注册 on_recv 回调，将消息缓冲到内存列表
- F-084: handlers.py:118-126 — 内核 REST API 路由：GET/POST /api/kernels（列出/创建内核）、GET/DELETE /api/kernels/{id}（查询/删除内核）、POST /api/kernels/{id}/{restart|interrupt}（重启/中断）、GET /api/kernels/{id}/channels（WebSocket 连接）
- F-085: websocket.py:16 — KernelWebsocketHandler 使用多继承：WebSocketMixin + WebSocketHandler + JupyterHandler
- F-086: websocket.py:61-66 — WebSocket GET 方法使用 @ws_authenticated 装饰器认证，pre_get 中创建 kernel_websocket_connection_class 实例
- F-087: websocket.py:86-95 — select_subprotocol 方法支持 v1.kernel.websocket.jupyter.org 子协议协商，默认回退到 legacy 协议
- F-088: connection/abc.py:5-29 — KernelWebsocketConnectionABC 定义四个抽象方法：connect()、disconnect()、handle_incoming_message()、handle_outgoing_message()
- F-089: connection/channels.py:48 — ZMQChannelsWebsocketConnection 继承自 BaseKernelWebsocketConnection，是默认的 ZMQ-WebSocket 桥接实现
- F-090: connection/channels.py:61-88 — ZMQChannelsWebsocketConnection 配置消息速率限制：iopub_msg_rate_limit 默认 1000 msg/s、iopub_data_rate_limit 默认 1000000 bytes/s、rate_limit_window 默认 3 秒
- F-091: connection/channels.py:100 — _open_sessions 类级字典跟踪所有打开的会话，session-id 作为 ZMQ identity 必须唯一
- F-092: connection/base.py:24-50 — serialize_binary_message 使用自定义二进制格式序列化消息：4字节 nbufs + 4*(nbufs+1) 字节偏移量表 + JSON 头 + buffer 列表

## 内容管理（Contents）

- F-093: manager.py:45 — ContentsManager 继承自 LoggingConfigurable，是内容管理抽象基类，定义文件/目录/notebook 的 CRUD 接口
- F-094: manager.py:82 — ContentsManager.root_dir 默认 "/"，可通过配置设置服务器根目录
- F-095: manager.py:114 — allow_hidden 默认为 False，不允许访问隐藏文件
- F-096: manager.py:122-135 — hide_globs 默认隐藏 __pycache__、*.pyc、*.pyo、.DS_Store、*~ 文件
- F-097: manager.py:153-225 — 支持 pre_save_hook 和 post_save_hook 钩子，可配置为 Python callable 或 import 字符串
- F-098: manager.py:263-282 — 同时支持旧式单一 pre_save_hook/post_save_hook 和新式 register_pre_save_hook/register_post_save_hook 多钩子注册
- F-099: manager.py:780 — AsyncContentsManager 继承 ContentsManager，checkpoints_class 为 AsyncCheckpoints
- F-100: manager.py:801-818 — AsyncContentsManager 定义异步抽象方法：dir_exists(path)、is_hidden(path)、get()、save()、delete_file()、rename_file() 等
- F-101: filemanager.py:72 — FileContentsManager 继承 FileManagerMixin + ContentsManager，实现基于本地文件系统的同步内容管理
- F-102: filemanager.py:47-69 — _get_created_timestamp 跨平台获取文件创建时间：macOS/BSD 使用 st_birthtime，Windows 使用 st_ctime，Linux 回退到 st_ctime
- F-103: largefilemanager.py:13 — LargeFileManager 继承 FileContentsManager，支持分块大文件上传
- F-104: largefilemanager.py:16-50 — save 方法处理 chunk 参数：chunk=1 为首块（覆盖写入），chunk=-1 为末块，其他为追加写入
- F-105: checkpoints.py:11-42 — Checkpoints 抽象基类定义五个抽象方法：create_checkpoint、restore_checkpoint、rename_checkpoint、delete_checkpoint、list_checkpoints
- F-106: checkpoints.py:55-75 — GenericCheckpointsMixin 提供与具体 ContentsManager 无关的通用 checkpoint 实现，只需实现 create_file_checkpoint/create_notebook_checkpoint/get_file_checkpoint/get_notebook_checkpoint
- F-107: handlers.py:48-80 — validate_model 函数验证内容模型必须包含 name/path/type/writable/created/last_modified/mimetype/content/format 等字段
- F-108: handlers.py:89 — ContentsHandler 是内容 API 核心处理器，支持 GET（获取文件/目录模型）、PUT（保存）、PATCH（分块上传）、DELETE（删除）
- F-109: manager.py:64 — ContentsManager 内置事件发射器 event_schema_id 为 JUPYTER_SERVER_EVENTS_URI + "/contents_service/v1"

## 会话管理（Sessions）

- F-110: sessionmanager.py:36-77 — KernelSessionRecord 是 @dataclass，包含 session_id 和 kernel_id 字段，定义了相等性比较和更新逻辑；同一 session_id 只能关联一个 kernel_id
- F-111: sessionmanager.py:94-159 — KernelSessionRecordList 管理 KernelSessionRecord 列表，支持通过 session_id 或 kernel_id 查找、更新（合并）、删除记录
- F-112: sessionmanager.py:161 — SessionManager 继承 LoggingConfigurable，是会话管理的核心类
- F-113: sessionmanager.py:164-172 — database_filepath 默认 ":memory:"（SQLite 内存数据库），可配置为文件路径实现持久化
- F-114: sessionmanager.py:195-200 — SessionManager 持有 kernel_manager 和 contents_manager 引用
- F-115: handlers.py:118-126 — Session API 路由模式类似 Kernels，在 /api/sessions 端点
- F-116: handlers.py:48-116 — POST /api/sessions 创建会话时关联或启动内核，支持 kernel_name/kernel_id 指定，处理 NoSuchKernel 和 DuplicateKernelError 异常

## 终端服务（Terminals）

- F-117: terminalmanager.py:9 — TerminalManager 直接从 jupyter_server_terminals.terminalmanager 导入，终端管理已完全外置到独立包
- F-118: serverapp.py:1984-2000 — terminals_enabled 默认为 True，如果 terminado 包不可用会自动禁用
- F-119: serverapp.py:1492-1496 — terminado_settings 可配置 shell_command 等 terminado 参数

## 认证与授权（Auth）

- F-120: identity.py:42-87 — User 数据类包含 username（必填）、name、display_name、initial、avatar_url、color 字段，fill_defaults 方法自动从 username 派生 name/display_name
- F-121: identity.py:89-115 — _backward_compat_user 函数提供向后兼容，支持从字符串 username 或 dict 创建 User 对象
- F-122: identity.py:118 — IdentityProvider 继承 LoggingConfigurable，是 2.0 版本新增的认证层抽象
- F-123: identity.py:122-130 — IdentityProvider 核心方法：get_user() 返回 User 对象或 None，identity_model() 将 User 转为 JSON dict
- F-124: authorizer.py:26-71 — Authorizer 抽象基类定义 is_authorized(handler, user, action, resource) 方法，返回 bool 或 Awaitable[bool]
- F-125: authorizer.py:74-89 — AllowAllAuthorizer 是默认授权器，is_authorized 始终返回 True（允许所有已认证请求）
- F-126: authorizer.py:48-50 — is_authorized 的 action 参数为 read/write/execute，resource 参数标识资源类型（contents/kernels/files 等）
- F-127: decorator.py:19-88 — @authorized 装饰器实现授权检查，自动从 HTTP 方法映射 action（GET→read、POST→write 等），从 handler.auth_resource 获取 resource
- F-128: decorator.py:91-115 — @allow_unauthenticated 装饰器标记公开端点，设置 __allow_unauthenticated=True 属性
- F-129: decorator.py:118-143 — @ws_authenticated 装饰器用于 WebSocket 端点认证，不重定向到登录页（对 WebSocket 无意义），认证失败返回 403
- F-130: login.py:18-91 — LoginFormHandler 处理 GET（显示登录表单）和 POST（处理登录提交），使用 @allow_unauthenticated 标记为公开端点
- F-131: login.py:34-82 — _redirect_safe 方法验证登录后重定向 URL 安全性，防止跨域重定向攻击
- F-132: serverapp.py:2150-2163 — 当 login_handler_class 非默认但 identity_provider_class 为默认 PasswordIdentityProvider 时，自动切换到 LegacyIdentityProvider 以兼容 2.0 之前的自定义登录处理器
- F-133: auth/utils.py 定义 HTTP_METHOD_TO_AUTH_ACTION 映射（HTTP方法→权限动作）

## 扩展系统（Extension）

- F-134: application.py:126 — ExtensionApp 继承 JupyterApp，是 Jupyter Server 扩展应用的基类
- F-135: application.py:143 — load_other_extensions 属性控制直接启动扩展时是否加载其他扩展，默认为 True
- F-136: application.py:148 — serverapp_config 字典允许扩展在直接启动时配置底层 Jupyter Server
- F-137: application.py:178 — ExtensionApp.name 是扩展名称，用于 CLI 子命令（jupyter {name}）和配置文件名
- F-138: manager.py:18-56 — ExtensionPoint 类封装单个扩展点，通过 metadata 中的 "module" 键导入模块，metadata 中 "app" 键存在时实例化 ExtensionApp
- F-139: manager.py:157-183 — ExtensionPoint 定义三阶段生命周期：link（链接到 ServerApp）、load（加载扩展）、start（事件循环启动后异步启动）
- F-140: manager.py:186 — ExtensionPackage 类管理一个 Python 包中的多个扩展点（extension_points 字典）
- F-141: manager.py:277 — ExtensionManager 是扩展管理的高级接口，负责查找、验证、链接、加载、启动所有扩展
- F-142: manager.py:304-309 — ExtensionManager.extensions 字典以包名映射 ExtensionPackage 对象
- F-143: manager.py:360-379 — add_extension 方法尝试创建 ExtensionPackage 并添加到管理器，失败时记录警告（可配置 reraise_server_extension_failures 抛异常）
- F-144: handler.py:36-99 — ExtensionHandlerMixin 为扩展 Handler 提供 initialize(name)、extensionapp、serverapp、log、config、base_url、render_template 等属性和方法
- F-145: handler.py:21-33 — ExtensionHandlerJinjaMixin 允许扩展使用自己的 Jinja2 模板环境
- F-146: serverapp.py:2544-2565 — find_server_extensions 使用 ExtensionConfigManager 扫描 jupyter_server_config.d/ 目录下的 JSON 配置文件，发现启用的扩展
- F-147: serverapp.py:2567-2578 — init_server_extensions 创建 ExtensionManager 实例，从 jpserver_extensions 配置加载扩展，调用 link_all_extensions 链接
- F-148: serverapp.py:2580-2588 — load_server_extensions 调用 extension_manager.load_all_extensions() 加载所有扩展
- F-149: serverapp.py:3254-3257 — _post_start 中调用 extension_manager.start_all_extensions() 在事件循环运行后启动扩展异步任务

## 处理器体系（Handlers）

- F-150: base/handlers.py:85 — AuthenticatedHandler 继承 web.RequestHandler，是所有需要认证的处理器的基类
- F-151: base/handlers.py:111-129 — set_default_headers 设置 X-Content-Type-Options: nosniff 和 Content-Security-Policy（默认 frame-ancestors 'self'）
- F-152: base/handlers.py:276 — JupyterHandler 继承 AuthenticatedHandler，提供对所有 Jupyter 管理器（kernel_manager、contents_manager、session_manager 等）的属性快捷访问
- F-153: base/handlers.py:232-252 — authorizer 属性延迟加载，未配置时发出警告并创建默认 AllowAllAuthorizer
- F-154: base/handlers.py:255-273 — identity_provider 属性延迟加载，未配置时发出警告并创建默认 IdentityProvider
- F-155: base/websocket.py:17-84 — WebSocketMixin 提供 WebSocket 通用功能：ping/pong 保活（默认 30 秒间隔）、CORS origin 检查
- F-156: base/websocket.py:44-84 — check_origin 方法实现 WebSocket 跨源检查：allow_origin="*" 全允许，token 认证时跳过检查，否则验证 Origin Host 匹配
- F-157: base/handlers.py:391-399 — set_cors_headers 必须在 prepare() 末尾调用（因为 current_user 在 2.0 中是异步的），设置 Access-Control-Allow-Origin 等 CORS 头

## Gateway 远程内核支持

- F-158: gateway/gateway_client.py:89 — GatewayClient 继承 SingletonConfigurable，是全局单例配置类，管理与 Kernel/Enterprise Gateway 的连接
- F-159: gateway/gateway_client.py:49-86 — GatewayTokenRenewerBase 是令牌刷新抽象基类，默认 NoOpTokenRenewer 直接返回原 token
- F-160: gateway/gateway_client.py:116-141 — GatewayClient.url 配置 Gateway 服务器地址，必须以 "http" 开头，支持 JUPYTER_GATEWAY_URL 环境变量
- F-161: gateway/gateway_client.py:143-169 — ws_url 默认从 url 推导（http→ws替换），支持 JUPYTER_GATEWAY_WS_URL 环境变量
- F-162: gateway/managers.py:40 — GatewayMappingKernelManager 继承 AsyncMappingKernelManager，代理所有内核操作到远程 Gateway
- F-163: gateway/managers.py:51-52 — GatewayMappingKernelManager 的 shared_context 默认 False，不共享 ZMQ context
- F-164: gateway/managers.py:68-94 — start_kernel 通过 GatewayClient 向远程 Gateway 发送 HTTP 请求启动内核，维护本地 _kernels 缓存
- F-165: gateway/managers.py:111-161 — list_kernels 通过 GET 请求从 Gateway 获取内核列表，检测被 Gateway 端淘汰的内核并清理本地缓存
- F-166: gateway/connections.py:24 — GatewayWebSocketConnection 继承 BaseKernelWebsocketConnection，作为 WebSocket 代理桥接前端与 Gateway 之间的 WebSocket 连接
- F-167: gateway/connections.py:40-61 — connect 方法构建 Gateway WebSocket URL，使用 tornado.websocket.websocket_connect 建立客户端连接
- F-168: gateway/connections.py:77-86 — disconnect 方法关闭 WebSocket 连接或取消挂起的连接 Future
- F-169: serverapp.py:2086 — init_configurables 中首先实例化 GatewayClient.instance(parent=self) 单例，后续管理器类选择依赖 gateway_config.gateway_enabled 标志

## 配置与 traitlets

- F-170: serverapp.py:59-75 — ServerApp 大量使用 traitlets 进行配置声明：Bool/Unicode/Integer/Float/Dict/List/Type/Instance/Bytes/Any/Union 等类型
- F-171: config_manager.py:54 — BaseJSONConfigManager 管理 JSON 格式配置文件，支持从 {section}.d/ 目录递归合并配置
- F-172: config_manager.py:20-38 — recursive_update 递归合并字典，None 值删除对应键
- F-173: serverapp.py:1278-1297 — _warn_deprecated_config 方法统一处理 2.0 版本的配置弃用警告，将旧 ServerApp 上的配置映射到对应类（如 PasswordIdentityProvider）
- F-174: serverapp.py:1190-1205 — ServerApp.token 在 2.0 中已弃用，重定向到 IdentityProvider.token
- F-175: serverapp.py:1260-1305 — password/password_required/allow_password_change 在 2.0 中已弃用，重定向到 PasswordIdentityProvider 对应属性
- F-176: serverapp.py:1927-1968 — kernel_ws_protocol/limit_rate/iopub_msg_rate_limit/iopub_data_rate_limit/rate_limit_window 已弃用，移至 ZMQChannelsWebsocketConnection
- F-177: prometheus/metrics.py:37-71 — Prometheus 指标定义：HTTP_REQUEST_DURATION_SECONDS（Histogram）、KERNEL_CURRENTLY_RUNNING_TOTAL（Gauge）、TERMINAL_CURRENTLY_RUNNING_TOTAL（Gauge）、SERVER_INFO（Info）、SERVER_EXTENSION_INFO（Info）、LAST_ACTIVITY（Gauge）、SERVER_STARTED（Gauge）、ACTIVE_DURATION（Gauge）
- F-178: prometheus/metrics.py:18-35 — 兼容 notebook v6 的指标定义：当 notebook<7 且非 shim 时直接从 notebook.prometheus.metrics 重新导出，避免重复定义冲突
- F-179: serverapp.py:1844-1871 — root_dir 默认值为当前工作目录，验证必须为存在的绝对路径目录；file_to_run 指定打开文件时 root_dir 自动设为文件父目录

## 入口点与生命周期

- F-180: __main__.py:1-6 — python -m jupyter_server 入口调用 app.launch_new_instance()
- F-181: serverapp.py:596-614 — JupyterPasswordApp 子命令用于设置密码，调用 security.set_password 写入配置文件
- F-182: serverapp.py:684-700 — JupyterServerStopApp 子命令用于停止运行中的服务器
- F-183: serverapp.py:617-681 — shutdown_server 函数先尝试 POST /api/shutdown，超时后 SIGTERM，再超时后 SIGKILL（Unix），Windows 返回 False
- F-184: serverapp.py:2461-2475 — _handle_sigint 处理首次 Ctrl-C：提示 "Shutdown this Jupyter server (y/[n])?"，确认后调用 stop()
- F-185: serverapp.py:2526-2535 — _signal_stop 处理 SIGTERM，调用 stop()
- F-186: serverapp.py:3112-3110 — launch_browser 在独立线程中调用 webbrowser.open 打开浏览器，避免阻塞主线程
- F-187: serverapp.py:3010-3040 — write_browser_open_files 写入 jpserver-{pid}-open.html 重定向文件（包含 token），浏览器通过打开本地 HTML 文件实现安全认证跳转
- F-188: serverapp.py:2336-2352 — init_resources 在非 Windows 平台调整 RLIMIT_NOFILE（文件描述符上限），默认软限制提升到 4096
- F-189: serverapp.py:1089-1119 — 支持 UNIX socket 监听（--sock 参数），sock_mode 默认 0600（仅用户可读写），Windows 不支持
- F-190: serverapp.py:1121-1139 — 支持 SSL/TLS：certfile、keyfile、client_ca 配置项
- F-191: serverapp.py:1743-1752 — trust_xheaders 配置是否信任 X-Scheme/X-Forwarded-Proto/X-Real-Ip/X-Forwarded-For 反向代理头
- F-192: base/handlers.py:297-298 — JupyterHandler.serverapp 属性通过 settings["serverapp"] 访问 ServerApp 实例
- F-193: serverapp.py:59-77 — ServerApp 从 traitlets 导入 Bool/Bytes/Dict/Float/Instance/Integer/List/TraitError/Type/Unicode/Union/default/observe/validate 等装饰器和类型
- F-194: serverapp.py:798-868 — flags 和 aliases 字典定义了 CLI 短选项映射
