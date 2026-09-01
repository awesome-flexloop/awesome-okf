---
okf_version: '0.2'
generated: '2026-08-22'
tags:
- jupyter
- server
- terminal
- websocket
sources:
- ../../../../../external/libs/jupyter/jupyter_server_terminals/pyproject.toml
- ../../../../../external/libs/jupyter/jupyter_server_terminals/README.md
- ../../../../../external/libs/jupyter/jupyter_server_terminals/jupyter_server_terminals/__init__.py
- ../../../../../external/libs/jupyter/jupyter_server_terminals/jupyter_server_terminals/_version.py
- ../../../../../external/libs/jupyter/jupyter_server_terminals/jupyter_server_terminals/api_handlers.py
- ../../../../../external/libs/jupyter/jupyter_server_terminals/jupyter_server_terminals/app.py
- ../../../../../external/libs/jupyter/jupyter_server_terminals/jupyter_server_terminals/base.py
- ../../../../../external/libs/jupyter/jupyter_server_terminals/jupyter_server_terminals/handlers.py
- ../../../../../external/libs/jupyter/jupyter_server_terminals/jupyter_server_terminals/terminalmanager.py
type: Facts
title: jupyter-server-terminals 源码事实清单
---

# jupyter_server_terminals 事实清单（R阶段）

> 本文件记录从源码中提取的可验证事实，编号 F-001 起。所有事实均指向具体源码路径，禁止推测。

## 元数据

- F-001: `__version__ = "0.5.4"`，定义于 `_version.py` 第1-2行
- F-002: 构建系统使用 `hatchling>=1.5`，`build-backend = "hatchling.build"`，定义于 `pyproject.toml` 第2-3行
- F-003: 包名 `jupyter_server_terminals`，描述为 `"A Jupyter Server Extension Providing Terminals."`，定义于 `pyproject.toml` 第6行、第10行
- F-004: Python 版本要求 `>=3.8`，支持 3.8/3.9/3.10/3.11，定义于 `pyproject.toml` 第18-23行
- F-005: 运行时依赖：Windows 平台需 `pywinpty>=2.0.3`，全平台需 `terminado>=0.8.3`，定义于 `pyproject.toml` 第24-27行
- F-006: 测试依赖包括 `jupyter_server>=2.0.0`、`pytest-jupyter[server]>=0.5.3`、`pytest>=7.0`、`pytest-timeout`，定义于 `pyproject.toml` 第41-46行
- F-007: 许可证为 BSD License，定义于 `pyproject.toml` 第9行、第16行
- F-008: Hatch 版本源指向 `jupyter_server_terminals/_version.py`，定义于 `pyproject.toml` 第62-63行
- F-009: 构建时将 `jupyter-config/` 目录安装到 `etc/jupyter/jupyter_server_config.d`，定义于 `pyproject.toml` 第65-66行
- F-010: 包内含 `py.typed` 标记文件（PEP 561），支持类型检查，位于 `jupyter_server_terminals/py.typed`

## 目录结构

- F-011: 核心包目录 `jupyter_server_terminals/` 包含 7 个 Python 源文件：`__init__.py`、`_version.py`、`api_handlers.py`、`app.py`、`base.py`、`handlers.py`、`terminalmanager.py`
- F-012: 包含 `rest-api.yml` OpenAPI 3.0.1 规范文件，定义于 `rest-api.yml` 第1行
- F-013: `jupyter-config/jupyter_server_terminals.json` 配置 `ServerApp.jpserver_extensions` 自动启用扩展，定义于该文件第1-7行
- F-014: 测试目录 `tests/` 包含 `test_auth.py`、`test_disable_app.py`、`test_terminal.py` 三个测试文件

## 与 jupyter_server 集成

- F-015: `__init__.py` 在导入时尝试导入 `jupyter_server._version.version_info`，若 Jupyter Server 未安装则抛出 `ModuleNotFoundError`，定义于 `__init__.py` 第5-9行
- F-016: `__init__.py` 检查 Jupyter Server 主版本号 >= 2，否则抛出 `RuntimeError("Jupyter Server Terminals requires Jupyter Server 2.0+")`，定义于 `__init__.py` 第11-13行
- F-017: `_jupyter_server_extension_points()` 返回列表，包含模块路径 `"jupyter_server_terminals.app"` 和应用类 `TerminalsExtensionApp`，定义于 `__init__.py` 第18-24行
- F-018: `TerminalsExtensionApp` 继承自 `jupyter_server.extension.application.ExtensionApp`，定义于 `app.py` 第11行、第19行
- F-019: `TerminalsExtensionApp.name = "jupyter_server_terminals"`，定义于 `app.py` 第22行
- F-020: `terminal_manager_class` 是可配置的 `Type` traitlet，默认值为 `TerminalManager`，通过 `.tag(config=True)` 暴露配置，定义于 `app.py` 第24-26行
- F-021: `terminals_available` 类变量默认为 `False`，是终端功能最终可用性的标志（区别于 web settings 中的同名变量），定义于 `app.py` 第35行
- F-022: `initialize_settings()` 检查 `serverapp.terminals_enabled`，为 False 时设置 `settings["terminals_available"] = False` 并直接返回，定义于 `app.py` 第37-41行
- F-023: `initialize_settings()` 在终端启用时调用 `initialize_configurables()`，并将 `terminals_available=True` 和 `terminal_manager` 写入 settings，定义于 `app.py` 第42-45行
- F-024: `initialize_handlers()` 在终端禁用时仅同步 `terminals_available` 到 `web_app.settings` 以兼容 nbclassic，定义于 `app.py` 第81-86行
- F-025: `initialize_handlers()` 在终端启用时注册 WebSocket 路由 `/terminals/websocket/(\w+)` 并扩展 API handlers，定义于 `app.py` 第87-94行
- F-026: `initialize_handlers()` 将 `terminal_manager` 实例和 `terminals_available` 标志写入 `serverapp.web_app.settings`，定义于 `app.py` 第96-99行
- F-027: `stop_extension()` 异步调用 `cleanup_terminals()`，定义于 `app.py` 第126-128行
- F-028: `cleanup_terminals()` 记录待关闭终端数量日志，通过 `ensure_async()` 异步调用 `terminal_manager.terminate_all()`，定义于 `app.py` 第109-124行
- F-029: `current_activity()` 在有活动终端时返回 `terminal_manager.terminals` 字典，否则返回 `None`，定义于 `app.py` 第101-107行

## Shell 配置与进程环境

- F-030: 默认 shell 选择逻辑：Windows 使用 `"powershell.exe"`，非 Windows 通过 `shutil.which("sh")` 查找 sh，定义于 `app.py` 第49行
- F-031: Shell 命令确定优先级链：`terminado_settings["shell_command"]` 配置 > `SHELL` 环境变量 > 默认 shell，定义于 `app.py` 第51-56行
- F-032: `shell_command` 配置为字符串时通过 `shlex.split()` 拆分为列表，定义于 `app.py` 第52-53行
- F-033: 非 Windows 平台、无 shell override、且 stdout 非 TTY 时（如 JupyterHub spawner 启动场景），自动追加 `"-l"` 启动 login shell 以加载 `/etc/profile` 等环境配置，定义于 `app.py` 第62-63行
- F-034: 创建 `TerminalManager` 时传入 `extra_env` 字典，包含 `JUPYTER_SERVER_ROOT`（serverapp.root_dir）和 `JUPYTER_SERVER_URL`（serverapp.connection_url），定义于 `app.py` 第66-70行
- F-035: `TerminalManager` 的 `parent` 设为 `serverapp`，`log` 设为 `serverapp.log`，定义于 `app.py` 第71-73行

## TerminalManager

- F-036: `TerminalManager` 继承 `LoggingConfigurable`（traitlets）和 `NamedTermManager`（terminado.management），定义于 `terminalmanager.py` 第14行、第18行、第25行
- F-037: `cull_inactive_timeout` 是 `Integer` traitlet，默认值 0（禁用自动清理），单位秒，可配置，定义于 `terminalmanager.py` 第32-37行
- F-038: `cull_interval_default = 300`（5 分钟），`cull_interval` 是 `Integer` traitlet，默认 300 秒，定义于 `terminalmanager.py` 第39-44行
- F-039: Prometheus 指标使用 `TERMINAL_CURRENTLY_RUNNING_TOTAL`，从 `jupyter_server.prometheus.metrics` 导入，定义于 `terminalmanager.py` 第13行、第20行
- F-040: `create()` 调用 `self.new_named_terminal(**kwargs)` 创建终端，为返回的 term 对象 monkey-patch `last_activity` 属性（初始化为 `utcnow()`），递增 Prometheus 指标，初始化 culler，定义于 `terminalmanager.py` 第49-61行
- F-041: `list()` 返回所有终端模型列表，并同步 Prometheus 指标 `RUNNING_TOTAL` 为当前终端数，定义于 `terminalmanager.py` 第67-73行
- F-042: `terminate(name, force=False)` 先调用 `_check_terminal(name)`，再调用 `super().terminate(name, force=force)`，最后递减 Prometheus 指标，定义于 `terminalmanager.py` 第75-82行
- F-043: `terminate_all()` 遍历 `list(self.terminals)` 的副本逐个 force terminate，定义于 `terminalmanager.py` 第84-88行
- F-044: `get_terminal_model(name)` 返回 JSON-safe 字典 `{"name": name, "last_activity": isoformat(term.last_activity)}`，定义于 `terminalmanager.py` 第90-99行
- F-045: `_check_terminal(name)` 检查名称是否在 `self.terminals` 中，不存在抛出 `web.HTTPError(404, "Terminal not found: %s" % name)`，定义于 `terminalmanager.py` 第101-104行
- F-046: `_initialize_culler()` 在首次创建终端且 `cull_inactive_timeout > 0` 时启动 `PeriodicCallback`；`cull_interval <= 0` 时重置为默认值 300 秒并记录警告，定义于 `terminalmanager.py` 第106-130行
- F-047: Culler 的 `PeriodicCallback` 间隔为 `1000 * cull_interval` 毫秒，回调函数为 `self._cull_terminals`，定义于 `terminalmanager.py` 第120-122行
- F-048: `_cull_terminals()` 遍历 `list(self.terminals)` 副本（避免迭代中修改冲突），逐个调用 `_cull_inactive_terminal()`，捕获并记录所有异常，定义于 `terminalmanager.py` 第132-148行
- F-049: `_cull_inactive_terminal(name)` 计算 `dt_now - term.last_activity`，若超过 `cull_inactive_timeout` 秒则记录警告日志并 `force=True` 终止终端，定义于 `terminalmanager.py` 第150-168行
- F-050: `pre_pty_read_hook(ptywclients)` 在 PTY 每次读取前将 `ptywclients.last_activity` 更新为 `utcnow()`，定义于 `terminalmanager.py` 第170-172行

## WebSocket Handler

- F-051: `TermSocket` 使用四父类多继承：`TerminalsMixin`、`WebSocketMixin`、`JupyterHandler`、`BaseTermSocket`（来自 `terminado.websocket`），定义于 `handlers.py` 第13-14行、第22行
- F-052: `AUTH_RESOURCE = "terminals"`，`TermSocket.auth_resource = AUTH_RESOURCE`，定义于 `handlers.py` 第19行、第25行
- F-053: `initialize()` 方法重写签名，接收 `term_manager: NamedTermManager` 参数，依次调用 `BaseTermSocket.initialize()` 和 `TerminalsMixin.initialize()`，定义于 `handlers.py` 第27-32行
- F-054: `origin_check()` 直接返回 `True`，注释说明 Tornado 已在 `check_origin` 中处理，terminado 自带的 origin_check 是冗余的，定义于 `handlers.py` 第34-38行
- F-055: `get()` 方法（WebSocket 握手）首先检查 `self.current_user`，无用户则抛出 `HTTPError(403)`，定义于 `handlers.py` 第42-45行
- F-056: `get()` 方法通过 `self.authorizer.is_authorized(self, user, "execute", self.auth_resource)` 检查用户对 "terminals" 资源的 "execute" 权限，未授权抛出 `HTTPError(403)`；若 authorizer 为 None 则调用 `warn_disabled_authorization()` 警告，定义于 `handlers.py` 第48-54行
- F-057: `get()` 方法检查终端名是否在 `self.term_manager.terminals` 中，不存在抛出 `HTTPError(404)`，然后调用 `super().get()` 完成 WebSocket 升级，定义于 `handlers.py` 第56-60行
- F-058: `on_message()` 异步调用 `super().on_message(message)`（即 terminado 的消息处理），然后调用 `_update_activity()` 更新活动时间戳，定义于 `handlers.py` 第62-65行
- F-059: `write_message()` 调用 `super().write_message(message, binary=binary)` 发送消息后，调用 `_update_activity()` 更新活动时间戳，定义于 `handlers.py` 第67-70行
- F-060: `_update_activity()` 同时更新全局 `application.settings["terminal_last_activity"]` 和单个终端的 `last_activity` 属性（仅在终端仍存在时），定义于 `handlers.py` 第72-76行

## REST API

- F-061: `TerminalAPIHandler` 继承 `APIHandler`（jupyter_server），设置 `auth_resource = "terminals"`，作为所有 REST API handler 的基类，定义于 `api_handlers.py` 第17-20行
- F-062: `TerminalsMixin` 继承 `ExtensionHandlerMixin`，提供 `terminal_manager` property，从 `self.settings["terminal_manager"]` 获取管理器实例，定义于 `base.py` 第12-17行
- F-063: `TerminalRootHandler` 处理 `/api/terminals` 路由，继承 `TerminalsMixin` 和 `TerminalAPIHandler`，定义于 `api_handlers.py` 第23行、第89行
- F-064: `GET /api/terminals` 调用 `terminal_manager.list()` 返回终端列表 JSON，装饰有 `@web.authenticated` 和 `@authorized`，定义于 `api_handlers.py` 第26-31行
- F-065: `POST /api/terminals` 从请求体获取 JSON data（默认为空字典），支持 `cwd` 参数指定工作目录，定义于 `api_handlers.py` 第33-64行
- F-066: POST 创建终端时 cwd 路径三级解析策略：①若为绝对路径且存在则直接使用；②作为相对路径拼接 `server_root_dir` 后检查是否存在；③都不存在则删除 cwd 参数（使用默认工作目录）并记录 debug 日志，定义于 `api_handlers.py` 第42-61行
- F-067: `TerminalHandler` 处理 `/api/terminals/(\w+)` 路由，继承 `TerminalsMixin` 和 `TerminalAPIHandler`，定义于 `api_handlers.py` 第67行、第90行
- F-068: `TerminalHandler.SUPPORTED_METHODS = ("GET", "DELETE", "OPTIONS")`，不支持 PUT/PATCH 方法，定义于 `api_handlers.py` 第70行
- F-069: `GET /api/terminals/{name}` 调用 `terminal_manager.get(name)` 返回单个终端模型 JSON，装饰有 `@web.authenticated` 和 `@authorized`，定义于 `api_handlers.py` 第72-77行
- F-070: `DELETE /api/terminals/{name}` 异步调用 `terminal_manager.terminate(name, force=True)`，返回 HTTP 204 No Content，定义于 `api_handlers.py` 第79-85行
- F-071: `default_handlers` 列表注册两条路由：`/api/terminals` → `TerminalRootHandler`，`/api/terminals/(\w+)` → `TerminalHandler`，定义于 `api_handlers.py` 第88-91行

## OpenAPI 规范

- F-072: `rest-api.yml` 使用 OpenAPI 3.0.1，定义 Terminal schema 包含 `name`（required, string）和 `last_activity`（ISO 8601 UTC 时间戳，带 Z 后缀）两个属性；四个端点（GET/POST 集合、GET/DELETE 单终端）分别返回 200/204/403/404，定义于 `rest-api.yml` 第1-111行
