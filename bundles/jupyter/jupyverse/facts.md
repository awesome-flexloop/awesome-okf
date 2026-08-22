---
type: Facts
okf_version: '0.2'
title: jupyverse 源码事实清单
tags:
- jupyter
- jupyverse
- fastapi
- fps
- server
generated: '2026-08-22'
sources:
- ../../../../../external/libs/jupyter/jupyverse/pyproject.toml
- ../../../../../external/libs/jupyter/jupyverse/src/jupyverse/__init__.py
- ../../../../../external/libs/jupyter/jupyverse/api/api/pyproject.toml
- ../../../../../external/libs/jupyter/jupyverse/api/api/src/jupyverse_api/__init__.py
- ../../../../../external/libs/jupyter/jupyverse/api/api/src/jupyverse_api/app/__init__.py
- ../../../../../external/libs/jupyter/jupyverse/api/api/src/jupyverse_api/exceptions.py
- ../../../../../external/libs/jupyter/jupyverse/api/api/src/jupyverse_api/cli.py
- ../../../../../external/libs/jupyter/jupyverse/api/api/src/jupyverse_api/main/__init__.py
- ../../../../../external/libs/jupyter/jupyverse/api/auth/src/jupyverse_auth/__init__.py
- ../../../../../external/libs/jupyter/jupyverse/api/contents/src/jupyverse_contents/__init__.py
- ../../../../../external/libs/jupyter/jupyverse/api/kernels/src/jupyverse_kernels/__init__.py
- ../../../../../external/libs/jupyter/jupyverse/api/frontend/src/jupyverse_frontend/__init__.py
- ../../../../../external/libs/jupyter/jupyverse/api/lab/src/jupyverse_lab/lab.py
- ../../../../../external/libs/jupyter/jupyverse/plugins/contents/pyproject.toml
- ../../../../../external/libs/jupyter/jupyverse/plugins/lab/pyproject.toml
- ../../../../../external/libs/jupyter/jupyverse/plugins/kernels/pyproject.toml
- ../../../../../external/libs/jupyter/jupyverse/plugins/contents/src/fps_contents/main.py
- ../../../../../external/libs/jupyter/jupyverse/plugins/lab/src/fps_lab/main.py
- ../../../../../external/libs/jupyter/jupyverse/plugins/kernels/src/fps_kernels/main.py
- ../../../../../external/libs/jupyter/jupyverse/plugins/frontend/src/fps_frontend/main.py
- ../../../../../external/libs/jupyter/jupyverse/plugins/kernel_subprocess/src/fps_kernel_subprocess/main.py
- ../../../../../external/libs/jupyter/jupyverse/plugins/file_watcher/src/fps_file_watcher/main.py
- ../../../../../external/libs/jupyter/jupyverse/plugins/nbconvert/src/fps_nbconvert/main.py
- ../../../../../external/libs/jupyter/jupyverse/plugins/terminals/src/fps_terminals/main.py
- ../../../../../external/libs/jupyter/jupyverse/plugins/auth/src/fps_auth/main.py
- ../../../../../external/libs/jupyter/jupyverse/plugins/contents/src/fps_contents/routes.py
- ../../../../../external/libs/jupyter/jupyverse/plugins/kernels/src/fps_kernels/routes.py
- ../../../../../external/libs/jupyter/jupyverse/plugins/noauth/src/fps_noauth/backends.py
- ../../../../../external/libs/jupyter/jupyverse/plugins/jupyter_server/src/fps_jupyter_server/jupyter_server.py
- ../../../../../external/libs/jupyter/jupyverse/plugins/yrooms/src/fps_yrooms/yrooms.py
- ../../../../../external/libs/jupyter/jupyverse/plugins/yrooms/src/fps_yrooms/config.py
- ../../../../../external/libs/jupyter/jupyverse/plugins/file_id/src/fps_file_id/file_id.py
- ../../../../../external/libs/jupyter/jupyverse/plugins/lab/src/fps_lab/routes.py
- ../../../../../external/libs/jupyter/jupyverse/plugins/noauth/src/fps_noauth/main.py
- ../../../../../external/libs/jupyter/jupyverse/plugins/yjs/src/fps_yjs/main.py
- ../../../../../external/libs/jupyter/jupyverse/plugins/jupyter_server/src/fps_jupyter_server/main.py
---

# 项目元数据

- F-001: pyproject.toml:6 — 包名为 `jupyverse`
- F-002: pyproject.toml:7 — 当前版本为 `0.14.15`
- F-003: pyproject.toml:8 — 项目描述为 "A set of FPS plugins implementing a Jupyter server"，明确 jupyverse 是一组 FPS 插件的集合
- F-004: pyproject.toml:9 — 关键词为 `["jupyter", "server", "fastapi", "plugins"]`
- F-005: pyproject.toml:10 — 要求 Python >= 3.10
- F-006: pyproject.toml:12 — 开发状态标记为 "Production/Stable"（5 - Production/Stable）
- F-007: pyproject.toml:14-19 — 支持 Python 3.10 至 3.14，同时支持 CPython 和 PyPy
- F-008: pyproject.toml:24 — 核心依赖 `fps[click,fastapi,anycorn] >=0.6.3,<0.7.0`，使用 FPS 框架
- F-009: pyproject.toml:25-32 — 默认依赖 fps-contents、fps-file-watcher、fps-kernel-subprocess、fps-kernels、fps-terminals、fps-nbconvert、fps-lab、fps-frontend 共 8 个核心插件
- F-010: pyproject.toml:33 — 额外依赖 `rich-click >=1.6.1,<2` 用于 CLI 美化
- F-011: pyproject.toml:35 — 许可证为 BSD-3-Clause
- F-012: pyproject.toml:39 — 作者为 "Jupyter Development Team"
- F-013: pyproject.toml:50-69 — 定义了多个 optional-dependencies 功能组：jupyterlab、notebook、collaboration、auth、auth-fief、auth-jupyterhub、noauth、file-watcher-poll、kernel-web-worker、resource-usage、webdav、jupyterlab-git、jupyterlab-lsp
- F-014: pyproject.toml:52-58 — collaboration 功能组依赖 jupyter-collaboration-ui、jupyter-docprovider 前端包，以及 fps-file-id、fps-yjs、fps-ystore-sqlite、fps-yrooms 四个后端插件
- F-015: pyproject.toml:111-112 — 使用 uv workspace 管理 monorepo，成员为 `api/*` 和 `plugins/*`
- F-016: pyproject.toml:2 — 构建系统使用 `uv_build >=0.11.32,<0.12`
- F-017: src/jupyverse/__init__.py:1-3 — 根包 `jupyverse` 仅 3 行代码，通过 `importlib.metadata.version` 获取版本号，无任何业务逻辑

# 目录结构

- F-018: api/ — 包含抽象 API 层（接口定义 + Pydantic 模型），共 17 个子包：api、auth、contents、file_id、file_watcher、frontend、jupyterlab、kernel、kernels、lab、login、nbconvert、notebook、resource_usage、terminals、yjs、yrooms、ystore
- F-019: plugins/ — 包含具体插件实现（FPS Module 子类），共 25 个子包：auth、auth_fief、auth_jupyterhub、contents、file_id、file_watcher、file_watcher_poll、frontend、jupyter_server、jupyterlab、jupyterlab_git、jupyterlab_lsp、kernel_subprocess、kernel_web_worker、kernels、lab、login、nbconvert、noauth、notebook、resource_usage、terminals、webdav、yjs、yrooms、ystore_sqlite
- F-020: src/jupyverse/ — 根包仅含 `__init__.py` 和 `py.typed`，是一个极薄的元包
- F-021: tests/ — 顶层集成测试目录，包含 test_app.py、test_auth.py、test_contents.py、test_execute.py、test_kernels.py、test_server.py、test_settings.py
- F-022: docs/ — MkDocs 文档目录，使用 mkdocs-material 主题

# jupyverse-api 核心层

- F-023: api/api/pyproject.toml:6 — API 核心包名为 `jupyverse-api`，版本 `0.15.3`
- F-024: api/api/pyproject.toml:42 — CLI 入口点 `jupyverse = "jupyverse_api.cli:main"`，CLI 定义在 jupyverse-api 包中
- F-025: api/api/pyproject.toml:44-46 — 通过 `fps.modules` entry point 注册两个模块：`app` → `AppModule`，`jupyverse` → `JupyverseModule`
- F-026: api/api/pyproject.toml:48-49 — 通过 `jupyverse.modules` entry point 仅注册 `app` → `AppModule`（JupyverseModule 由 CLI 动态配置）
- F-027: api/api/pyproject.toml:29 — jupyverse-api 依赖 fastapi `>=0.95.0,<1,!=0.137.0,!=0.137.1`，排除了两个有问题的版本
- F-028: api/api/src/jupyverse_api/__init__.py:10-16 — 定义了 `Singleton` 元类，用于确保类只有一个实例
- F-029: api/api/src/jupyverse_api/__init__.py:19-20 — 定义了 `Config` 基类，继承 Pydantic BaseModel，设置 `extra = "forbid"` 禁止未知配置字段
- F-030: api/api/src/jupyverse_api/__init__.py:23-43 — 定义了 `Router` 类，持有 `_app: App` 引用，提供 `include_router`、`mount`、`add_middleware` 方法，委托给 App 对象
- F-031: api/api/src/jupyverse_api/__init__.py:33-34 — Router 使用 `_type` 属性（类名）标识路由来源，用于冲突检测

# App 包装器

- F-032: api/api/src/jupyverse_api/app/__init__.py:18 — `App` 类是 FastAPI 的包装器，用于检测端点路径冲突
- F-033: api/api/src/jupyverse_api/app/__init__.py:24-30 — App 构造函数支持 `mount_path` 参数，若提供则创建子 FastAPI 应用并挂载
- F-034: api/api/src/jupyverse_api/app/__init__.py:31 — App 注册 `RedirectException` 的全局异常处理器
- F-035: api/api/src/jupyverse_api/app/__init__.py:33-34 — App 记录 `_started_time`（UTC 启动时间）和 `_last_activity`（最后 HTTP 请求时间）
- F-036: api/api/src/jupyverse_api/app/__init__.py:36-39 — App 添加 HTTP 中间件，每次请求更新 `_last_activity` 时间戳
- F-037: api/api/src/jupyverse_api/app/__init__.py:53-70 — `_include_router` 方法在注册路由前检查路径冲突，若同一已被其他 Router 注册则抛出 RuntimeError
- F-038: api/api/src/jupyverse_api/app/__init__.py:12-13 — 检测 fastapi 版本，>= 0.137.2 时使用 `iter_route_contexts` 迭代路由
- F-039: api/api/src/jupyverse_api/app/__init__.py:72-80 — `_mount` 方法同样检测挂载路径冲突
- F-040: api/api/src/jupyverse_api/exceptions.py:7-14 — 定义 `RedirectException` 异常和 `_redirect_exception_handler` 处理器，返回 RedirectResponse

# CLI 入口

- F-041: api/api/src/jupyverse_api/cli.py:7 — CLI 基于 rich-click，从 `fps.cli._cli` 导入 `main as fps_main`
- F-042: api/api/src/jupyverse_api/cli.py:10-98 — 定义 CLI 选项：--debug、--show-config、--help-all、--backend(asyncio/trio)、--open-browser、--host(默认127.0.0.1)、--port(默认8000)、--websocket-permessage-deflate、--query-param、--allow-origin、--set、--disable、--timeout、--stop-timeout
- F-043: api/api/src/jupyverse_api/cli.py:129-139 — CLI 将所有选项序列化为 JSON 配置，通过 `fps_main.callback()` 传递给 FPS 框架
- F-044: api/api/src/jupyverse_api/cli.py:142-151 — `get_pluggin_config` 函数通过 `entry_points(group="jupyverse.modules")` 发现所有已注册插件，排除 `--disable` 指定的插件，构建 FPS 配置字典，顶层模块类型为 `jupyverse_api.main:JupyverseModule`

# JupyverseModule 主模块

- F-045: api/api/src/jupyverse_api/main/__init__.py:19-32 — `AppModule`（FPS Module 子类）在 prepare 阶段从 FPS 容器获取 FastAPI 实例，包装为 App 对象并注册到容器
- F-046: api/api/src/jupyverse_api/main/__init__.py:35 — `JupyverseModule` 继承自 `FastAPIModule`（FPS 提供的 FastAPI 模块基类）
- F-047: api/api/src/jupyverse_api/main/__init__.py:37-45 — JupyverseModule 构造函数接收配置并传递给 FastAPIModule，设置 debug、openapi_url、routes_url 参数
- F-048: api/api/src/jupyverse_api/main/__init__.py:47-54 — 当 `start_server=True` 时，JupyverseModule 添加 `fps.web.server:ServerModule` 作为子模块，传入 host、port、websocket_permessage_deflate 参数
- F-049: api/api/src/jupyverse_api/main/__init__.py:56-66 — prepare 阶段配置 CORS 中间件（当 allow_origins 非空时）
- F-050: api/api/src/jupyverse_api/main/__init__.py:67-75 — prepare 阶段将 QueryParams、Host URL、Lifespan 对象放入 FPS 容器供其他插件使用
- F-051: api/api/src/jupyverse_api/main/__init__.py:77-92 — start 阶段等待服务器启动后打印 URL，若 open_browser=True 则自动打开浏览器
- F-052: api/api/src/jupyverse_api/main/__init__.py:94-96 — stop 阶段设置 `lifespan.shutdown_request` 事件通知所有插件停止
- F-053: api/api/src/jupyverse_api/main/__init__.py:111-121 — JupyverseConfig 默认值：start_server=True、host=127.0.0.1、port=8000、websocket_permessage_deflate=False、allow_origins=[]、open_browser=False、debug=False、openapi_url=/openapi.json

# API 抽象层（接口契约）

- F-054: api/auth/src/jupyverse_auth/__init__.py:13-25 — `Auth` 是 ABC 抽象基类，定义三个抽象方法：`current_user(permissions)` 返回 FastAPI 依赖、`update_user()` 返回用户更新依赖、`websocket_auth(permissions)` 返回 WebSocket 认证依赖
- F-055: api/auth/src/jupyverse_auth/__init__.py:27-28 — `AuthConfig` 继承 Config，是一个空的配置基类（pass），供具体认证插件扩展
- F-056: api/contents/src/jupyverse_contents/__init__.py:15 — `Contents` 同时继承 `Router` 和 `ABC`，是内容 API 的抽象基类
- F-057: api/contents/src/jupyverse_contents/__init__.py:16 — Contents 使用 `ResourceLock`（anyioutils）作为 `file_lock` 进行文件并发控制
- F-058: api/contents/src/jupyverse_contents/__init__.py:23-91 — Contents 构造函数中直接定义所有 REST API 路由（/api/contents 系列端点），路由路径和权限在抽象层固定
- F-059: api/contents/src/jupyverse_contents/__init__.py:28 — 写操作端点（create_checkpoint、create_content、save_content、delete_content、rename_content）要求 `permissions={"contents": ["write"]}`
- F-060: api/contents/src/jupyverse_contents/__init__.py:93-165 — Contents 定义了 8 个抽象方法：read_content、write_content、create_checkpoint、create_content、get_root_content、get_checkpoint、get_content、save_content、delete_content、rename_content
- F-061: api/kernels/src/jupyverse_kernels/__init__.py:16 — `Kernels` 同时继承 `Router` 和 `ABC`，是内核管理 API 的抽象基类
- F-062: api/kernels/src/jupyverse_kernels/__init__.py:22-125 — Kernels 构造函数中定义所有内核相关路由：/api/status、/api/kernelspecs、/kernelspecs/、/api/kernels、/api/sessions、WebSocket /api/kernels/{id}/channels
- F-063: api/kernels/src/jupyverse_kernels/__init__.py:235-259 — `KernelsConfig` 默认 default_kernel="python3"、allow_external_kernels=False、require_yjs=False、wait_for_kernelspec=False
- F-064: api/kernels/src/jupyverse_kernels/__init__.py:227-232 — Kernels 提供 `register_kernel_factory` 方法的默认空实现，供内核插件注册自定义工厂
- F-065: api/frontend/src/jupyverse_frontend/__init__.py:8-9 — `FrontendConfig` 仅含 base_url（默认"/"）和 collaborative（默认 False）两个字段
- F-066: api/lab/src/jupyverse_lab/lab.py:17 — `Lab` 同时继承 `Router` 和 `ABC`，是 JupyterLab 前端 API 的抽象基类
- F-067: api/lab/src/jupyverse_lab/lab.py:33 — Lab 使用 `sys.prefix` 作为 prefix_dir 查找 JupyterLab 静态文件
- F-068: api/lab/src/jupyverse_lab/lab.py:40-46 — Lab 支持 dev_mode，开发模式下从 jupyterlab 包的 dev_mode 目录加载，否则从 sys.prefix/share/jupyter/lab 加载
- F-069: api/lab/src/jupyverse_lab/lab.py:50-60 — Lab 自动为每个 federated extension 挂载静态文件目录到 `/lab/extensions/{name}/static`，并挂载主题目录到 `/lab/api/themes`

# 插件体系（Entry Points）

- F-070: plugins/contents/pyproject.toml:48-49 — fps-contents 插件同时注册到 `fps.modules` 和 `jupyverse.modules` 两个 entry point 组
- F-071: plugins/lab/pyproject.toml:51-52 — fps-lab 插件同样注册到两个 entry point 组
- F-072: plugins/kernels/pyproject.toml:61-62 — fps-kernels 插件同样注册到两个 entry point 组
- F-073: plugins/contents/src/fps_contents/main.py:9 — 每个插件定义一个继承 `fps.Module` 的类（如 `ContentsModule`）
- F-074: plugins/contents/src/fps_contents/main.py:10-14 — 插件在 `prepare()` 异步方法中：从 FPS 容器 `get()` 依赖对象、创建实现类实例、通过 `self.put()` 注册到容器
- F-075: plugins/contents/src/fps_contents/main.py:12 — 插件通过 `await self.get(Auth)` 获取认证抽象，注释标记 `# type: ignore[type-abstract]`，说明运行时注入具体实现
- F-076: plugins/lab/src/fps_lab/main.py:12-28 — LabModule 在 prepare 中使用 `create_task_group()` 启动后台任务，调用 `self.done()` 标记准备完成，通过 Event 等待关闭信号
- F-077: plugins/kernels/src/fps_kernels/main.py:24 — KernelsModule 先 `self.put(self.config, KernelsConfig)` 将配置放入容器，再获取其他依赖
- F-078: plugins/kernels/src/fps_kernels/main.py:48 — KernelsModule 通过 `teardown_callback=self.kernels.stop` 注册清理回调
- F-079: plugins/kernels/src/fps_kernels/main.py:30-34 — Yjs 依赖是可选的：当 `config.require_yjs` 为 True 时才获取 Yjs 实例，否则为 None
- F-080: plugins/frontend/src/fps_frontend/main.py:5-11 — FrontendModule 是最简单的插件之一：创建 FrontendConfig 并通过 `self.put()` 注册
- F-081: plugins/kernel_subprocess/src/fps_kernel_subprocess/main.py:7-9 — KernelSubprocessModule 创建 `DefaultKernelFactory(KernelSubprocess)` 并注册，替换默认内核工厂
- F-082: plugins/file_watcher/src/fps_file_watcher/main.py:7-10 — FileWatcherModule 创建 `_FileWatcher()` 实例并注册为 FileWatcher 抽象的实现
- F-083: plugins/nbconvert/src/fps_nbconvert/main.py:9-14 — NbconvertModule 遵循相同模式：get App 和 Auth → 创建实现类 → put 到容器
- F-084: plugins/terminals/src/fps_terminals/main.py:12-15 — TerminalsModule 根据平台（sys.platform == "win32"）选择终端服务器实现：Windows 用 win_server，其他用 server
- F-085: plugins/auth/src/fps_auth/main.py:15-59 — AuthModule 在 prepare 阶段创建数据库表、创建测试用户（test 模式）、创建全局 token 用户、在 token 模式下将 token 添加到 query params

# 具体实现细节

- F-086: plugins/contents/src/fps_contents/routes.py:26 — `_Contents` 类继承抽象基类 `Contents`，前缀下划线表示这是内部实现类
- F-087: plugins/contents/src/fps_contents/routes.py:32-36 — 检查点（checkpoint）保存在 `.ipynb_checkpoints/` 目录，文件名格式为 `{stem}-checkpoint{suffix}`
- F-088: plugins/contents/src/fps_contents/routes.py:36 — 文件操作使用 `anyio.to_thread.run_sync` 将同步 IO（shutil.copyfile）放到线程池执行
- F-089: plugins/contents/src/fps_contents/routes.py:227-228 — 文件写入使用 `CancelScope(shield=True)` 确保写入操作不可取消，防止文件损坏
- F-090: plugins/contents/src/fps_contents/routes.py:149 — 文件读取使用 `self.file_lock(str(path))` 异步文件锁进行并发控制
- F-091: plugins/contents/src/fps_contents/routes.py:156 — 目录列表过滤掉以 `.` 开头的隐藏文件
- F-092: plugins/contents/src/fps_contents/routes.py:177-178 — `.ipynb` 文件被识别为 type="notebook"，读取时标记所有 cell 为 untrusted（trusted: False）
- F-093: plugins/kernels/src/fps_kernels/routes.py:43 — `_Kernels` 类继承抽象基类 `Kernels`
- F-094: plugins/kernels/src/fps_kernels/routes.py:65-69 — 内核状态使用模块级字典 `kernels` 存储，包含 server 和 driver 引用
- F-095: plugins/kernels/src/fps_kernels/routes.py:74-80 — 支持外部内核：通过监控 `external_connection_dir` 目录中的连接文件发现外部内核
- F-096: plugins/kernels/src/fps_kernels/routes.py:304 — 新启动的内核使用 `uuid.uuid4()` 生成 kernel_id
- F-097: plugins/kernels/src/fps_kernels/routes.py:455-460 — WebSocket 内核通道支持 `v1.kernel.websocket.jupyter.org` 子协议
- F-098: plugins/noauth/src/fps_noauth/backends.py:6 — NoAuth 实现创建一个空的全局 `User()` 对象，所有请求共享同一用户
- F-099: plugins/noauth/src/fps_noauth/backends.py:9-14 — NoAuth 的 `current_user()` 直接返回全局 USER 对象，不做任何认证检查
- F-100: plugins/noauth/src/fps_noauth/backends.py:24-31 — NoAuth 的 `update_user()` 直接修改全局 USER 对象的属性
- F-101: plugins/jupyter_server/src/fps_jupyter_server/jupyter_server.py:35-36 — `JupyterServer` 类是一个代理/桥接器，启动真正的 `jupyter server` 子进程并通过 httpx2 代理 HTTP/WebSocket 请求
- F-102: plugins/jupyter_server/src/fps_jupyter_server/jupyter_server.py:52-61 — JupyterServer 通过 `anyio.open_process` 启动 `jupyter server --IdentityProvider.token={token} --port {port}` 子进程
- F-103: plugins/yrooms/src/fps_yrooms/yrooms.py:28-223 — YRoom 实现协作文档房间管理，支持从文件加载文档、通过 pycrdt 同步 CRDT 更新、延迟保存到磁盘
- F-104: plugins/yrooms/src/fps_yrooms/yrooms.py:78-79 — YRoom 使用 YStore（如 SQLite）持久化 CRDT 更新，文件名为 `.{file_type}:{file_id}.y`
- F-105: plugins/yrooms/src/fps_yrooms/yrooms.py:130-156 — 文件写入采用防抖策略：最后一次变更后等待 `document_save_delay`（默认1秒）再写入磁盘
- F-106: plugins/yrooms/src/fps_yrooms/yrooms.py:214-222 — 房间清理：最后一个客户端断开后等待 `document_cleanup_delay`（默认60秒）再关闭房间
- F-107: plugins/yrooms/src/fps_yrooms/config.py:5-17 — YRoomsConfig 配置 document_cleanup_delay（默认60秒）和 document_save_delay（默认1秒）
- F-108: plugins/file_id/src/fps_file_id/file_id.py:38 — `_FileId` 使用 SQLite 数据库（通过 sqlite_anyio）维护文件路径到 ID 的映射，支持文件重命名检测
- F-109: plugins/file_id/src/fps_file_id/file_id.py:98-121 — 初始化时递归索引当前工作目录下所有文件，为每个文件生成 UUID 并记录 mtime
- F-110: plugins/file_id/src/fps_file_id/file_id.py:214-235 — 通过比较 mtime 检测文件重命名：同时添加和删除的文件若 mtime 相同则视为重命名
- F-111: plugins/lab/src/fps_lab/routes.py:88-94 — 通过 entry_points(group="jupyterlab.languagepack") 发现已安装的语言包
- F-112: plugins/lab/src/fps_lab/routes.py:249-265 — `get_federated_extensions` 扫描 extensions 目录下的 package.json，自动发现 federated JupyterLab 扩展
- F-113: api/api/src/jupyverse_api/main/__init__.py:106-108 — `Lifespan` 类包含一个 `shutdown_request: Event`，用于协调所有插件的优雅关闭

# 技术栈

- F-114: api/api/pyproject.toml:28-33 — jupyverse-api 依赖：anyio、fastapi、fps、structlog、packaging、pydantic v2
- F-115: plugins/contents/pyproject.toml:23-32 — fps-contents 额外依赖 anyioutils（ResourceLock）、starlette
- F-116: plugins/kernels/pyproject.toml:23-39 — fps-kernels 额外依赖 pycrdt（CRDT）、python-dateutil、packaging
- F-117: plugins/yrooms/src/fps_yrooms/yrooms.py:9-10 — fps-yrooms 使用 jupyter_ydoc（YDOCS）和 pycrdt 实现 CRDT 协作编辑
- F-118: plugins/kernels/src/fps_kernels/routes.py:21 — 使用 httpx2（非 httpx）作为 HTTP 客户端
- F-119: plugins/auth/src/fps_auth/main.py:2 — fps-auth 使用 fastapi-users 库进行用户管理
- F-120: plugins/lab/src/fps_lab/routes.py:172 — Lab 设置使用 json5 解析用户设置（支持注释等 JSON5 特性）
- F-121: api/api/src/jupyverse_api/cli.py:36 — 事件循环后端支持 asyncio 和 trio 两种选择
