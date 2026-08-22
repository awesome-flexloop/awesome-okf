---
type: Facts
okf_version: "0.2"
title: "pytest-jupyter 源码事实清单"
generated: "2026-08-22"
tags: [jupyter, pytest, testing, plugin, fixtures]
sources:
  - ../../../../../external/libs/jupyter/pytest-jupyter/pyproject.toml
  - ../../../../../external/libs/jupyter/pytest-jupyter/pytest_jupyter/_version.py
  - ../../../../../external/libs/jupyter/pytest-jupyter/pytest_jupyter/__init__.py
  - ../../../../../external/libs/jupyter/pytest-jupyter/pytest_jupyter/jupyter_core.py
  - ../../../../../external/libs/jupyter/pytest-jupyter/pytest_jupyter/echo_kernel.py
  - ../../../../../external/libs/jupyter/pytest-jupyter/pytest_jupyter/jupyter_client.py
  - ../../../../../external/libs/jupyter/pytest-jupyter/pytest_jupyter/jupyter_server.py
  - ../../../../../external/libs/jupyter/pytest-jupyter/pytest_jupyter/pytest_tornasync.py
  - ../../../../../external/libs/jupyter/pytest-jupyter/tests/conftest.py
---
# pytest-jupyter 源码事实清单

## 项目元数据与构建配置

- F-001: `pyproject.toml:5-12` — 构建后端为 `hatchling.build`（requires `hatchling>=1.10.0`）；项目名 `pytest-jupyter`，description 为 "A pytest plugin for testing Jupyter libraries and extensions."，version 通过 `dynamic = ["version"]` 动态获取
- F-002: `pyproject.toml:29-33` — 基础依赖仅 `pytest>=7.0` 与 `jupyter_core>=5.7`，requires-python 为 `>=3.10`
- F-003: `pyproject.toml:43-53` — optional-dependencies 定义三组：`client`（jupyter_client>=7.4.0、nbformat>=5.3、ipykernel>=6.14）、`server`（在 client 之上追加 jupyter_server>=1.21）、`docs`
- F-004: `pyproject.toml:64-66` — `[tool.hatch.version]` 的 path 指向 `pytest_jupyter/_version.py` 作为版本来源
- F-005: `pyproject.toml:110-129` — `[tool.pytest.ini_options]` 配置 `testpaths=["tests"]`、`timeout=10`、`timeout_method="thread"`、`xfail_strict=true`，filterwarnings 默认按 "error" 处理
- F-006: `_version.py:5` — `__version__ = "0.12.0.dev0"`

## 包入口

- F-007: `pytest_jupyter/__init__.py:6-7` — 从 `._version` 导入 `__version__`，并以 `from .jupyter_core import *` 重导出 jupyter_core 模块的 fixture

## 基础层：jupyter_core fixtures 与 pytest hook

- F-008: `jupyter_core.py:40-51` — `jp_asyncio_loop` fixture 标记 `autouse=True`，通过 `jupyter_core.utils.ensure_event_loop(prefer_selector_loop=True)` 获取 asyncio loop，teardown 时 `loop.close()`，并屏蔽 WindowsSelectorEventLoopPolicy 的 DeprecationWarning
- F-009: `jupyter_core.py:54-59` — `pytest_pycollect_makeitem` hook 标记 `@pytest.hookimpl(tryfirst=True)`：当测试项为协程函数（`iscoroutinefunction(obj)`）时调用 `collector._genfunctions` 收集，否则返回 None
- F-010: `jupyter_core.py:62-80` — `pytest_pyfunc_call` hook 标记 `tryfirst=True`：协程测试函数用 `ensure_event_loop(prefer_selector_loop=True)` 的 loop 执行 `run_until_complete(pyfuncitem.obj(**testargs))`，普通函数直接调用，两者均返回 True
- F-011: `jupyter_core.py:83-128` — `jp_home_dir`/`jp_data_dir`/`jp_config_dir`/`jp_runtime_dir`/`jp_system_jupyter_path`/`jp_env_jupyter_path`/`jp_system_config_path`/`jp_env_config_path` 八个路径 fixture 均依赖 `tmp_path`，各自创建 `home`/`data`/`config`/`runtime`/`share/jupyter`/`env/share/jupyter`/`etc/jupyter`/`env/etc/jupyter` 子目录
- F-012: `jupyter_core.py:131-134` — `jp_kernel_dir` fixture 依赖 `jp_data_dir`，在其下创建 `kernels` 子目录
- F-013: `jupyter_core.py:137-152` — `echo_kernel_spec` fixture 在 `jp_kernel_dir/echo` 下写入 `kernel.json`，argv 为 `[sys.executable, "-m", "pytest_jupyter.echo_kernel", "-f", "{connection_file}"]`，display_name 为 "echo"
- F-014: `jupyter_core.py:155-179` — `jp_environ` fixture 聚合全部路径 fixture 与 `monkeypatch`、`tmp_path`，设置 `HOME`/`PYTHONPATH`/`JUPYTER_CONFIG_DIR`/`JUPYTER_DATA_DIR`/`JUPYTER_RUNTIME_DIR` 五个环境变量，并替换 `jupyter_core.paths` 的 `SYSTEM_JUPYTER_PATH`/`ENV_JUPYTER_PATH`/`SYSTEM_CONFIG_PATH`/`ENV_CONFIG_PATH` 四个列表
- F-015: `jupyter_core.py:27-37` — 模块导入时（`resource` 在 Windows 为 None）将 `RLIMIT_NOFILE` 的软限制调整为 4096

## 测试内核：echo_kernel

- F-016: `echo_kernel.py:15-27` — `class EchoKernel(Kernel)` 继承 `ipykernel.kernelbase.Kernel`，类属性 `implementation="Echo"`、`implementation_version="1.0"`、`language="echo"`、`language_info`（mimetype text/plain、file_extension .txt）、`banner="Echo kernel - as useful as a parrot"`
- F-017: `echo_kernel.py:29-59` — `do_execute` 在非 silent 时把收到的 code 以 stream 消息经 `self.iopub_socket` 发回 stdout；当 `allow_stdin` 且 code 含 `"input("` 时调用 `_input_request("Echo Prompt", ...)`；返回 `{"status": "ok", "execution_count": self.execution_count, "payload": [], "user_expressions": {}}`
- F-018: `echo_kernel.py:62-70` — `class EchoKernelApp(IPKernelApp)` 设置 `kernel_class = EchoKernel`；`__main__` 分支先 `logging.disable(logging.ERROR)` 再 `EchoKernelApp.launch_instance()`

## 客户端层：jupyter_client fixtures

- F-019: `jupyter_client.py:7-20` — 模块顶层 try 导入 `ipykernel` 与 `jupyter_client.manager.start_new_async_kernel`、`NATIVE_KERNEL_NAME`，ImportError 时 `warnings.warn` 提示执行 `pip install 'pytest-jupyter[client]'`
- F-020: `jupyter_client.py:26-33` — `jp_zmq_context` fixture 创建 `zmq.asyncio.Context()` 并 yield，teardown 调用 `ctx.term()`
- F-021: `jupyter_client.py:36-57` — `jp_start_kernel` fixture 依赖 `jp_environ` 与 `jp_asyncio_loop`，返回 `inner(kernel_name=NATIVE_KERNEL_NAME, **kwargs)` 函数，inner 调用 `start_new_async_kernel` 并记录 km/kc 列表；teardown 依次执行 `kc.stop_channels()` 与 `km.shutdown_kernel(now=True)`

## 服务端层：jupyter_server fixtures

- F-022: `jupyter_server.py:23-49` — 模块顶层 try 导入 jupyter_server 全套依赖（ServerApp、Authorizer、WebSocketHandler、Config、nbformat、tornado 等），并计算 `is_v2 = version_info[0] == 2`；ImportError 时 `Authorizer` 降级为 `object` 且 `warnings.warn` 提示 `pip install 'pytest-jupyter[server]'`
- F-023: `jupyter_server.py:58-69` — `jp_server_config` fixture 在 `is_v2` 时返回含 `ServerApp.jpserver_extensions={"jupyter_server_terminals": True}` 的 `Config`，否则返回空 Config
- F-024: `jupyter_server.py:72-87` — `jp_root_dir`/`jp_template_dir`/`jp_argv` 三个 fixture：前两者在 tmp_path 下创建 `root_dir`/`templates` 子目录，`jp_argv` 返回空列表 `[]`
- F-025: `jupyter_server.py:90-94` — `jp_http_port` fixture 依赖 `http_server_port`，返回 `http_server_port[-1]`，teardown 关闭 `http_server_port[0]`
- F-026: `jupyter_server.py:97-100` — `jp_extension_environ` fixture 将 `serverextension.ENV_CONFIG_PATH` monkeypatch 为 `[str(jp_env_config_path)]`
- F-027: `jupyter_server.py:103-120` — `jp_nbconvert_templates` 在 monkeypatch 前查找已安装的 `jupyter_core.paths.jupyter_path("nbconvert", "templates")`，若存在则 `shutil.copytree` 复制到 `jp_data_dir/nbconvert/templates`
- F-028: `jupyter_server.py:123-136` — `jp_logging_stream` fixture 返回 `io.StringIO()` 供 ServerApp 日志使用，teardown 时将已收集输出 `print` 出来
- F-029: `jupyter_server.py:139-231` — `jp_configurable_serverapp` 工厂 fixture：先 `ServerApp.clear_instance()`，内部工厂函数设置 `NotebookNotary.db_file=":memory:"`、生成随机 token（v2 写入 `c.IdentityProvider.token`）、以 `log_level="DEBUG"`、`port_retries=0`、`open_browser=False`、`allow_root=True` 创建 `ServerApp.instance()`，`app.init_signal=lambda: None`，把日志 StreamHandler 重定向到 `jp_logging_stream` 后 `app.start_app()`
- F-030: `jupyter_server.py:234-259` — `jp_serverapp` fixture 以 `jp_server_config`/`jp_argv` 调用 `jp_configurable_serverapp`，并屏蔽四条 Windows event loop 相关 DeprecationWarning
- F-031: `jupyter_server.py:262-279` — `jp_web_app` 返回 `jp_serverapp.web_app`；`jp_base_url` 返回 `"/a%40b/"`
- F-032: `jupyter_server.py:268-273` — `jp_auth_header` 按版本返回 `{"Authorization": "token <token>"}`（v2 使用 `jp_serverapp.identity_provider.token`）
- F-033: `jupyter_server.py:282-335` — `jp_fetch` 工厂：对 `url_path_join(*parts)` 做 `url_escape` 后拼接到 `jp_base_url`，注入 `jp_auth_header`，默认 `request_timeout=20`，底层调用 `http_server_client.fetch`
- F-034: `jupyter_server.py:338-380` — `jp_ws_fetch` 工厂：基于 `ws://localhost:{jp_http_port}` 构造 URL，过滤 `tornado.websocket.websocket_connect` 签名外的 kwargs 后建立 WebSocket 连接
- F-035: `jupyter_server.py:383-402` — `jp_create_notebook` 工厂：校验后缀必须为 `.ipynb`，用 `nbformat.v4.new_notebook()` 生成并写入文件，返回 nb 对象
- F-036: `jupyter_server.py:405-416` — `jp_server_cleanup` fixture 标记 `autouse=True`，teardown 时 `run_until_complete(app._cleanup())`、`kernel_manager.context.destroy()` 并 `ServerApp.clear_instance()`
- F-037: `jupyter_server.py:419-438` — `send_request` 工厂按 URL 是否以 `channels` 结尾或含 `/websocket/` 自动选择 `jp_ws_fetch` 或 `jp_fetch`，捕获 `HTTPClientError` 返回响应码
- F-038: `jupyter_server.py:441-543` — 认证相关：`jp_server_auth_core_resources` 遍历 `JUPYTER_SERVICE_HANDLERS` 构建 `url_regex → AUTH_RESOURCE` 映射；`class _Authorizer(Authorizer)` 定义 `HTTP_METHOD_TO_AUTH_ACTION`（GET/HEAD/OPTIONS→read、POST/PUT/PATCH/DELETE→write、WEBSOCKET→execute）与 `match_url_to_resource`/`normalize_url`/`is_authorized` 方法；`jp_server_authorizer` 将映射赋给 `_Authorizer._default_regex_mapping` 后返回该类

## vendored tornado 支持：pytest_tornasync

- F-039: `pytest_tornasync.py:1-3` — 文件头部注释声明该文件是 `pytest_tornasync`（eukaryote/pytest-tornasync 的 plugin.py）的 vendored fork
- F-040: `pytest_tornasync.py:22-56` — `io_loop`/`http_server_port`/`http_server` 三个 fixture：`io_loop` 返回 `tornado.ioloop.IOLoop.current()`，`http_server_port` 调用 `tornado.testing.bind_unused_port()`，`http_server` 用 `tornado.httpserver.HTTPServer(jp_web_app)` 绑定端口并 yield
- F-041: `pytest_tornasync.py:59-104` — `http_server_client` fixture 创建 `AsyncHTTPServerClient(http_server=...)`；`class AsyncHTTPServerClient(SimpleAsyncHTTPClient)` 重写 `fetch`（接受相对路径）、`get_protocol`（返回 "http"）、`get_http_port`、`get_url`（拼接 `127.0.0.1:{port}`）

## 插件注册与测试组织

- F-042: `tests/conftest.py:3` — 顶部设置 `os.environ["JUPYTER_PLATFORM_DIRS"] = "1"`
- F-043: `tests/conftest.py:4-8` — 通过 `pytest_plugins = ["pytest_jupyter", "pytest_jupyter.jupyter_server", "pytest_jupyter.jupyter_client"]` 显式加载三个插件模块
- F-044: `pyproject.toml:1-212` — 全文未声明 `[project.entry-points]` 段，即未通过 `pytest11` entry point 注册插件（Grep 全仓库无 `pytest11` 匹配）
