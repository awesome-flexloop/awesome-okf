# FPS 源码事实清单

> R阶段产出：零推测事实，每条事实指向具体源码位置。禁止出现"用于"/"目的是"/"设计为"等推断词。

## 项目元数据

- F-001: 包名 `fps`，版本 `0.6.7`，描述 "A system for creating modular, configurable, pluggable and concurrent applications"
- F-002: 构建系统使用 hatchling，`pyproject.toml` 中 `build-backend = "hatchling.build"`
- F-003: Python 版本要求 `>= 3.10`，支持 Python 3.10-3.14
- F-004: 核心依赖：`anyio >=4.14.0,<5.0.0`、`structlog`、`exceptiongroup`（Python<3.11条件依赖）
- F-005: 可选依赖组：`click`（>=8.1.8,<9）、`fastapi`（>=0.137.2,<1.0.0）、`anycorn`（>=0.19.0,<0.21.0）
- F-006: CLI入口点：`fps = "fps.cli._cli:main"`
- F-007: entry-points组 `"fps.modules"` 注册 `fps_module = "fps:Module"`
- F-008: 源码位于 `src/fps/` 目录，测试覆盖率声明为100%
- F-009: License 为 BSD License，作者为 Jupyter Development Team
- F-010: 源码仓库地址 `https://github.com/jupyter-server/fps`

## 包入口 `__init__.py`（src/fps/__init__.py）

- F-011: `__init__.py` 导出：`Context`、`SharedValue`、`Value`、`current_context`、`put`、`get`、`get_nowait`（来自`_context`）；`Module`、`initialize`（来自`_module`）；`get_root_module`、`merge_config`（来自`_config`）；`Signal`（来自`_signal`）
- F-012: `__version__ = "0.6.7"`

## 模块系统 `_module.py`（src/fps/_module.py）

- F-013: `Module` 类定义在 `_module.py` 第29行
- F-014: `Module.__init__` 接受参数：`name: str`、`prepare_timeout: float = 1`、`start_timeout: float = 1`、`stop_timeout: float = 1`、`global_start_timeout: float | None = None`
- F-015: `Module.__init__` 初始化实例属性：`_initialized=False`、`_parent=None`、`_context=Context()`、`_prepared=Event()`、`_started=Event()`、`_stopped=Event()`、`_is_stopping=False`、`_name=name`、`_path=[]`、`_uninitialized_modules={}`、`_modules={}`、`_published_values={}`、`_acquired_values={}`、`_context_manager_exits=[]`、`_config={}`、`config=None`
- F-016: `Module` 有 property：`parent`、`name`、`path`、`prepared`、`started`、`stopped`、`exceptions`、`modules`
- F-017: `Module.path` 返回 `".".join(self._path + [self._name])`，即点分路径
- F-018: `Module.get_path(root=True)` 方法，`root=False` 时去掉根模块名前缀
- F-019: `Module.exit_app()` 调用 `self._exit.set()`
- F-020: `Module.add_module(module_type, name, **config)` 方法，接受 `type[Module] | str` 类型的 module_type，通过 `import_from_string` 导入字符串类型
- F-021: `Module.add_module` 在 `_uninitialized_modules` 中注册 `{"type": module_type, "config": config, "modules": {}}`
- F-022: `Module.add_module` 检测到同名模块已存在时抛出 `RuntimeError(f"Module name already exists: {name}")`
- F-023: `Module.freed(value)` 方法，通过 `id(value)` 查找 `_published_values` 中的 `SharedValue` 并调用其 `freed()`
- F-024: `Module.all_freed()` 遍历 `_published_values.values()` 逐个调用 `freed()`
- F-025: `Module.drop_all()` 遍历 `_acquired_values.values()` 逐个调用 `drop()`
- F-026: `Module.drop(value)` 通过 `id(value)` 查找并调用对应 `Value.drop()`
- F-027: `Module.add_teardown_callback(callback)` 委托给 `self._context.add_teardown_callback(callback)`
- F-028: `Module.put(value, types=None, max_borrowers=inf, teardown_callback=None)` 方法：通过 `self._context.put()` 发布值到当前模块context，记录到 `_published_values`；如果有parent，同时通过 `parent._context.put(shared_value=shared_value)` 发布到父context
- F-029: `Module.get(value_type, timeout=inf)` 异步方法：同时在 `self._context` 和 `self.parent._context`（如果存在）上竞争获取值，先返回的获胜，另一个任务被cancel
- F-030: `Module.get` 获取值后通过 `id(value.unwrap())` 记录到 `_acquired_values`，返回 `value.unwrap()`
- F-031: `Module.__aenter__` 异步上下文管理器入口：调用 `initialize(self)`，创建 `AsyncExitStack` 和 `create_task_group()`，执行 `_prepare` 阶段（带超时），然后执行 `_start` 阶段（带超时），异常发生时设置 `_exit`
- F-032: `Module.__aexit__` 异步上下文管理器出口：执行 `_stop` 阶段（带超时），设置 `_exit`，cancel task group，关闭 exit_stack，打印异常日志
- F-033: `Module.context_manager(value)` 和 `async_context_manager(value)` 方法用于管理同步/异步上下文管理器的enter/exit
- F-034: `Module.done()` 方法：在 `preparing` 阶段设置 `self.prepared.set()`，在 `starting` 阶段设置 `self.started.set()`，在 `stopping` 阶段启动 `_finish` 任务
- F-035: `Module._finish()` 同时等待 `_drop_and_wait_values` 和 `_exit.wait`，任一完成即cancel
- F-036: `Module._drop_and_wait_values()` 调用 `drop_all()`、`_context.aclose()`，然后设置 `self.stopped.set()`
- F-037: `Module._prepare()` 方法：为每个子模块设置 `_task_group`、`_phase`、`_exceptions`，启动子模块的 `_prepare` 任务，同时启动自身的 `_prepare_and_done` 任务
- F-038: `Module._prepare_and_done()` 调用 `await self.prepare()`，如果 `prepared` 未设置则调用 `self.done()`
- F-039: `Module.prepare()` 默认实现为空方法（`pass`）
- F-040: `Module._start()` 方法结构与 `_prepare` 类似：启动子模块 `_start` 和自身 `_start_and_done`
- F-041: `Module._start_and_done()` 调用 `await self.start()`，如果 `started` 未设置则调用 `self.done()`
- F-042: `Module.start()` 默认实现为空方法（`pass`）
- F-043: `Module._stop()` 方法结构类似：先逆序调用 `_context_manager_exits` 中的退出函数，然后启动子模块 `_stop` 和自身 `_stop_and_done`
- F-044: `Module._stop_and_done()` 调用 `await self.stop()`，如果不在 `_is_stopping` 状态则调用 `self.done()`
- F-045: `Module.stop()` 默认实现为空方法（`pass`）
- F-046: `Module._all_prepared()`、`_all_started()`、`_all_stopped()` 递归等待所有子模块和自身的Event
- F-047: `Module._get_all_prepare_timeout()`、`_get_all_start_timeout()`、`_get_all_stop_timeout()` 递归为未完成的模块添加 `TimeoutError` 到 `_exceptions`
- F-048: `Module.run(backend="asyncio")` 方法调用 `anyio.run(self._main, backend=backend)`，`_main` 在异步上下文管理器中等待 `_exit.wait()`
- F-049: `Module.run` 捕获 `KeyboardInterrupt` 静默退出（区分asyncio和trio的异常结构）
- F-050: `initialize(root_module)` 函数：递归初始化根模块及其所有子模块，返回配置字典；已初始化则返回None
- F-051: `initialize` 设置 `root_module._exit = Event()`，提取 `__init__` 的kwargs默认值，合并 `_config`，构建config结构，调用 `_initialize` 递归实例化子模块
- F-052: `_initialize(submodules, parent_module, root_module_modules, config)` 递归函数：合并配置、通过 `import_from_string` 导入模块类型、实例化子模块、设置parent关系、递归初始化孙模块
- F-053: `get_kwargs_with_default(function)` 函数：提取函数签名中有默认值的参数及其默认值，返回dict；对 `Module.__init__` 返回空dict

## 上下文系统 `_context.py`（src/fps/_context.py）

- F-054: `Value(Generic[T])` 类定义在第26行
- F-055: `Value.__init__(shared_value: SharedValue)` 保存对 `SharedValue` 的引用
- F-056: `Value` 支持同步上下文管理器协议（`__enter__`/`__exit__`），enter调用 `unwrap()`，exit调用 `drop()`
- F-057: `Value.unwrap()` 返回 `self._shared_value._value`；如果 `self` 不在 `_shared_value._borrowers` 中则抛出 `RuntimeError("Already dropped")`
- F-058: `Value.drop()` 调用 `self._shared_value._drop(self)`
- F-059: `SharedValue(Generic[T])` 类定义在第73行
- F-060: `SharedValue.__init__` 接受参数：`value: T`、`max_borrowers: float = float("inf")`、`teardown_callback`（sync或async callable或None）、`close_timeout: float | None = None`
- F-061: `SharedValue.__init__` 初始化：`_value=value`、`_max_borrowers=max_borrowers`、`_teardown_callback=teardown_callback`、`_close_timeout=close_timeout`、`_borrowers=set()`、`_dropped=Event()`、`_opened=False`、`_closing=False`
- F-062: `SharedValue._drop(borrower)` 从 `_borrowers` 中移除borrower，设置 `_dropped` Event，然后创建新的 `Event()` 实例
- F-063: `SharedValue` 支持异步上下文管理器（`__aenter__`/`__aexit__`），exit调用 `aclose`
- F-064: `SharedValue.get(timeout=inf)` 异步方法：创建新的 `Value`，在 `fail_after(timeout)` 中循环等待直到 `len(_borrowers) < _max_borrowers`，然后将value加入 `_borrowers` 并返回
- F-065: `SharedValue.get_nowait()` 同步方法：如果当前可借用则立即返回 `Value`，否则抛出 `RuntimeError("Cannot borrow shared value")`
- F-066: `SharedValue.freed(timeout=inf)` 异步方法：等待所有borrower都被drop（`_borrowers`为空集合）
- F-067: `SharedValue.aclose(timeout=None, ...)` 异步方法：设置 `_closing=True`，等待 `freed()`，然后调用 `teardown_callback`（如果存在），超时则抛出 `TimeoutError`
- F-068: `Context` 类定义在第213行
- F-069: `Context.__init__` 初始化：`_context={}`（dict[int, SharedValue]）、`_value_added=Event()`、`_closed=False`、`_teardown_callbacks=[]`、`_parent=None`、`_children=set()`
- F-070: `Context` 支持异步上下文管理器：`__aenter__` 通过 `ContextVar` 设置当前context，建立父子关系；`__aexit__` 调用 `aclose`、reset token、从父children中移除
- F-071: `_current_context: ContextVar[Context]` 模块级 ContextVar，定义在第23行
- F-072: `Context._check_closed()` 在 `_closed=True` 时抛出 `RuntimeError("Context is closed")`
- F-073: `Context.add_teardown_callback(callback)` 将callback追加到 `_teardown_callbacks` 列表
- F-074: `Context.put(value, types=None, max_borrowers=inf, teardown_callback=None, shared_value=None)` 方法：如果传入 `shared_value` 则复用，否则创建新的 `SharedValue`；通过 `_get_value_types` 确定注册类型；对每个类型以 `id(value_type)` 为key注册到 `_context` dict；同类型已存在时抛出 `RuntimeError(f'Value type "{value_type}" already exists')`
- F-075: `Context.get(value_type, timeout=inf)` 异步方法：使用 `create_task_group` 同时在自身和所有父context（沿 `_parent` 链）上启动 `get_in_context` 任务竞争获取，先到先得，cancel其余任务；处理 `ExceptionGroup`
- F-076: `Context.get_nowait(value_type)` 同步方法：沿 `_parent` 链查找，找到则返回，否则抛出 `RuntimeError("Shared value not found or cannot be borrowed")`
- F-077: `Context._get(value_type)` 内部异步方法：循环等待直到 `value_type_id` 在 `_context` 中，然后调用 `shared_value.get()`
- F-078: `Context._get_nowait(value_type)` 内部同步方法：立即检查或抛出 `RuntimeError("Shared value not found")`
- F-079: `Context.aclose(timeout=None, ...)` 异步方法：在 `fail_after(timeout)` 中并行关闭所有 `SharedValue`（task_group），然后逆序调用 `_teardown_callbacks`，设置 `_closed=True`
- F-080: `count_parameters(func)` 使用 `lru_cache(maxsize=1024)` 缓存，返回函数签名的参数数量
- F-081: `call(callback, exc_value)` 异步函数：根据callback参数数量决定是否传入 `exc_value`，调用callback，如果返回awaitable则await
- F-082: `current_context()` 返回 `_current_context.get()`，无context时抛出 `LookupError`
- F-083: 模块级 `put(value, types=None, max_borrowers=inf, teardown_callback=None)` 委托给 `current_context().put(...)`
- F-084: 模块级 `get(value_type, timeout=inf)` 异步函数，委托给 `current_context().get(...)`
- F-085: 模块级 `get_nowait(value_type)` 委托给 `current_context().get_nowait(...)`
- F-086: `_get_value_types(value, types=None)` 函数：如果types为None则使用 `[type(value)]`；如果types不可迭代（单个类型）则包装为列表

## 导入系统 `_importer.py`（src/fps/_importer.py）

- F-087: `ImportFromStringError(Exception)` 自定义异常类
- F-088: `import_from_string(import_str: Any)` 函数：非字符串直接返回；不含 `:` 的字符串在 `"fps.modules"` entry-points组中按名称查找并加载；含 `:` 的字符串按 `module:attr` 格式分割，先 `importlib.import_module(module_str)`，再按 `.` 分割逐级getattr
- F-089: `import_from_string` 中模块导入失败抛出 `ImportFromStringError`，属性查找失败也抛出 `ImportFromStringError`；entry-point未找到抛出 `RuntimeError`

## 配置系统 `_config.py`（src/fps/_config.py）

- F-090: `get_root_module(config: dict)` 函数：遍历config dict的第一项，通过 `import_from_string(module_info["type"])` 导入类型，以 `module_name` 和 `module_config` 实例化根模块，递归设置子模块的未初始化配置到 `_uninitialized_modules`
- F-091: `merge_config(config, override, root=True)` 递归深度合并字典：root=True时先deepcopy；dict值递归合并，非dict值覆盖；新key直接添加
- F-092: `dump_config(config)` 将配置字典转为 `"module.param=value"` 格式的行列表，以换行符连接
- F-093: `_dump_config(config_lines, config, path)` 递归遍历config，将每个config参数格式化为 `{path}{name}.{param}={value}`
- F-094: `get_config_description(root_module)` 递归遍历模块树，提取Pydantic model的字段信息（title、default、annotation、description），格式化为可读描述文本
- F-095: `_get_config_description(description_lines, module)` 递归函数：访问 `type(module.config).model_fields` 提取字段元数据，然后递归处理子模块

## 信号系统 `_signal.py`（src/fps/_signal.py）

- F-096: `Signal(Generic[T])` 类定义在第12行
- F-097: `Signal.__init__` 初始化：`_callbacks=set()`（回调函数集合）、`_send_streams=set()`（MemoryObjectSendStream集合）
- F-098: `Signal.iterate()` 创建 `create_memory_object_stream[T]()`，将send_stream加入 `_send_streams`，返回receive_stream
- F-099: `Signal.connect(callback)` 将callback加入 `_callbacks` 集合
- F-100: `Signal.disconnect(callback)` 从 `_callbacks` 中移除callback
- F-101: `Signal.emit(value)` 异步方法：在task_group中并行执行所有回调（协程函数用 `tg.start_soon`，普通函数直接调用），同时向所有 `_send_streams` 发送value
- F-102: `Signal._send(send_stream, value, to_remove)` 内部异步方法：尝试 `send_stream.send(value)`，遇到 `BrokenResourceError` 时将stream加入to_remove列表；emit结束后清理断开的stream

## CLI `cli/_cli.py`（src/fps/cli/_cli.py）

- F-103: CLI使用click框架，入口函数 `main()` 被装饰为 `@click.command()`
- F-104: CLI选项：`--config`（click.File类型）、`--show-config`（flag，默认False）、`--help-all`（flag，默认False）、`--set`（multiple，格式key=value）、`--backend`（默认"asyncio"，可选"trio"）、`--timeout`（float，默认None）、`--stop-timeout`（float，默认1）
- F-105: CLI位置参数 `module`（默认空字符串）
- F-106: 无 `--config` 时，通过 `import_from_string(module)` 导入模块类型，构造 `{root_module_name: {"type": module_type}}` 格式的config_dict
- F-107: 有 `--config` 时读取JSON文件，可通过 `module` 参数选择子模块作为根
- F-108: `--set` 参数解析：按 `key=value` 分割，key按 `.` 分割为路径，在config_dict中逐级创建modules子dict，最终设置config参数值
- F-109: 全局变量 `CONFIG` 和 `TEST`；`TEST=True` 时只设置CONFIG不实际运行
- F-110: `get_config()` 返回全局CONFIG变量
- F-111: 正常流程：`get_root_module(config_dict)` → 设置超时 → `initialize(root_module)` → 根据 `--help-all` 输出配置描述或根据 `--show-config` 输出实际配置 → `root_module.run(backend=backend)`

## Web模块 - FastAPI `web/fastapi.py`

- F-112: `FastAPIModule(Module)` 类定义在 `fps/web/fastapi.py` 第10行
- F-113: `FastAPIModule.__init__` 接受参数：`name: str`、`app: FastAPI | None = None`、`debug: bool | None = None`、`routes_url: str | None = None`、`openapi_url: str | None = "/openapi.json"`
- F-114: `FastAPIModule.__init__` 调用 `super().__init__(name)`，debug默认取 `__debug__` 值；app为None时创建 `FastAPI(debug=debug, openapi_url=openapi_url)`
- F-115: `FastAPIModule.prepare()` 方法调用 `self.put(self.app)` 将FastAPI实例发布到context
- F-116: `FastAPIModule.start()` 方法：如果 `routes_url` 不为None，遍历 `self.app.routes` 使用iter_route_contexts，分类记录APIWebSocketRoute、Mount、Route的path/name/methods，注册GET端点返回routes列表

## Web模块 - Server `web/server.py`

- F-117: `ServerModule(Module)` 类定义在 `fps/web/server.py` 第12行
- F-118: `ServerModule.__init__` 接受参数：`name: str`、`host: str = "127.0.0.1"`、`port: int = 8000`、`websocket_permessage_deflate: bool = True`
- F-119: `ServerModule.__init__` 初始化 `self.shutdown_event = Event()`
- F-120: `ServerModule.start()` 异步方法：通过 `await self.get(FastAPI)` 获取FastAPI实例，创建 `anycorn.Config`，设置bind、websocket_permessage_deflate、loglevel="WARN"，在task_group中启动 `serve(app, config, shutdown_trigger=self.shutdown_event.wait, mode="asgi")`
- F-121: `ServerModule.start()` 注册teardown_callback用于设置shutdown_event并等待server任务结束，最后调用 `self.done()`

## 日志与依赖

- F-122: `_module.py` 中使用 `structlog.get_logger()` 获取logger，调用 `structlog.stdlib.recreate_defaults(log_level=logging.INFO)`
- F-123: 日志事件包括："Module added"、"Module added value"、"Module getting value"、"Module got value"、"Module could not get value"（critical级别）、"Running root module"、"Application running"、"Application failed"、"Application stopped"、"Preparing module"、"Module prepared"、"Starting module"、"Module started"、"Stopping module"、"Module stopped"、"Module failed while preparing/starting/stopping"（critical级别）

## 目录结构

- F-124: 源码目录结构：
  ```
  src/fps/
  ├── __init__.py          # 包入口，导出公共API
  ├── _config.py           # 配置系统（get_root_module, merge_config等）
  ├── _context.py          # 上下文与共享值系统（Context, SharedValue, Value）
  ├── _importer.py         # 动态导入系统（import_from_string）
  ├── _module.py           # 核心模块系统（Module, initialize）
  ├── _signal.py           # 信号系统（Signal）
  ├── py.typed             # PEP 561类型标记
  ├── cli/
  │   └── _cli.py          # CLI入口（click命令）
  └── web/
      ├── fastapi.py       # FastAPIModule
      └── server.py        # ServerModule（anycorn服务器）
  ```
- F-125: 测试文件：tests/conftest.py、test_cli.py、test_config.py、test_context.py、test_exceptions.py、test_module.py、test_signal.py、test_start_stop.py、test_tasks.py、test_value.py、test_web.py
- F-126: 文档文件：docs/index.md、docs/guide.md、docs/install.md、docs/api_reference.md、mkdocs.yml
