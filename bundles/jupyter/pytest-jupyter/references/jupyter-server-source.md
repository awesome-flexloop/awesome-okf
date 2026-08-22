---
okf_version: "0.2"
type: reference
title: "Server插件源码（jupyter_server.py）"
description: "pytest_jupyter/jupyter_server.py 的完整API：ServerApp配置fixtures、HTTP/WebSocket请求工厂、Notebook创建、认证授权测试工具、自动清理"
tags: [server-plugin, jupyter-server, serverapp, http-fetch, websocket, authorizer, notebook, cleanup, fixture-factory]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:45:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T14:45:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: jupyter-server-py
    resource: "../../../../../external/libs/jupyter/pytest-jupyter/pytest_jupyter/jupyter_server.py"
    title: "pytest_jupyter/jupyter_server.py"
---

# Server插件源码（jupyter_server.py）

本信源登记 `pytest_jupyter/jupyter_server.py`（约543行）的核心fixtures和类。jupyter_server.py是pytest-jupyter的最高层插件，提供Jupyter Server完整生命周期管理、HTTP/WebSocket测试客户端、认证授权测试工具等。它通过`import *`继承core插件和pytest_tornasync的所有fixtures。

## 模块级导入处理

```python
try:
    import nbformat, tornado, tornado.testing
    from jupyter_server._version import version_info
    from jupyter_server.auth import Authorizer
    from jupyter_server.extension import serverextension
    from jupyter_server.serverapp import JUPYTER_SERVICE_HANDLERS, ServerApp
    from jupyter_server.utils import url_path_join
    from tornado.escape import url_escape
    from tornado.httpclient import HTTPClientError
    from tornado.websocket import WebSocketHandler
    from traitlets.config import Config
    is_v2 = version_info[0] == 2
except ImportError:
    Authorizer = object
    warnings.warn("The server plugin has not been installed. Try: `pip install 'pytest-jupyter[server]'`", stacklevel=2)
```

- `is_v2`：布尔值，标记是否为Jupyter Server 2.x版本（影响默认配置和token位置）
- 导入失败时提供友好安装提示

[F-070]

## 配置Fixtures

### jp_server_config() -> Config

返回默认的ServerApp配置（traitlets Config对象）。

**行为：**
- 若is_v2为True：返回`Config({"ServerApp": {"jpserver_extensions": {"jupyter_server_terminals": True}}})`
- 若is_v2为False：返回空`Config({})`

[F-071]

### jp_root_dir(tmp_path) -> Path

返回临时根目录：`mkdir(tmp_path, "root_dir")`

[F-072]

### jp_template_dir(tmp_path) -> Path

返回临时模板目录：`mkdir(tmp_path, "templates")`

[F-073]

### jp_argv() -> list

返回空argv列表（`[]`），供测试覆盖传入自定义命令行参数。

[F-074]

### jp_base_url() -> str

返回测试用base URL，默认值为`"/a%40b/"`（包含URL编码的`@`字符，测试URL编码场景）。

[F-075]

### jp_http_port(http_server_port) -> int

从`http_server_port`元组中提取端口号。

**行为：**
1. yield `http_server_port[-1]`（端口号）给测试使用
2. 测试结束后调用`http_server_port[0].close()`关闭socket

[F-076]

### jp_extension_environ(jp_env_config_path, monkeypatch)

monkeypatch Jupyter Extension的配置路径。

**行为：**
- `monkeypatch.setattr(serverextension, "ENV_CONFIG_PATH", [str(jp_env_config_path)])`

[F-077]

### jp_nbconvert_templates(jp_data_dir)

在monkeypatch生效**之前**复制nbconvert模板到临时目录。

**行为：**
1. 调用`jupyter_core.paths.jupyter_path("nbconvert", "templates")`查找nbconvert模板路径
2. 遍历找到第一个存在的路径
3. 复制模板目录到`{jp_data_dir}/nbconvert/templates/`
4. **关键顺序**：此fixture必须在`jp_environ`之前执行（fixture依赖顺序保证），否则路径会被monkeypatch改变

[F-078]

### jp_logging_stream() -> StringIO

提供StringIO流用于捕获ServerApp日志输出。

**行为：**
1. 创建`io.StringIO()`实例
2. yield该流给测试使用
3. 测试结束后：
   - 获取输出内容`logging_stream.getvalue()`
   - 若有内容则print输出（方便调试）
   - 返回输出内容

[F-079]

## ServerApp生命周期Fixtures

### jp_configurable_serverapp(...) -> callable

可配置的ServerApp工厂fixture（核心fixture），返回内部函数`_configurable_serverapp`用于创建ServerApp实例。

**依赖fixtures（按顺序）：**
`jp_nbconvert_templates` → `jp_environ` → `jp_server_config` → `jp_argv` → `jp_http_port` → `jp_base_url` → `tmp_path` → `jp_root_dir` → `jp_logging_stream` → `jp_asyncio_loop`

**_configurable_serverapp参数：**
```python
def _configurable_serverapp(
    config=jp_server_config,
    base_url=jp_base_url,
    argv=jp_argv,
    environ=jp_environ,
    http_port=jp_http_port,
    tmp_path=tmp_path,
    root_dir=jp_root_dir,
    **kwargs,
):
```

**创建ServerApp的流程：**
1. 调用`ServerApp.clear_instance()`清除已有实例
2. 在config中注入`jupyter_server_terminals`扩展（v2且未显式配置时）
3. 复制config为新Config对象`c`，设置`c.NotebookNotary.db_file = ":memory:"`（内存SQLite，避免磁盘IO）
4. 生成随机token：`hexlify(os.urandom(4)).decode("ascii")`（8字符十六进制）
5. 设置token：v1用`kwargs["token"]`，v2用`c.IdentityProvider.token`
6. 若root_dir不为None，设置`kwargs["root_dir"] = str(root_dir)`
7. 创建ServerApp实例：
   ```python
   app = ServerApp.instance(
       log_level="DEBUG",
       port=http_port,
       port_retries=0,
       open_browser=False,
       base_url=base_url,
       config=c,
       allow_root=True,
       **kwargs,
   )
   ```
8. 禁用信号处理：`app.init_signal = lambda: None`
9. 初始化app（处理事件循环是否运行的情况）：
   - 若loop正在运行：直接调用`app.initialize(argv=argv, new_httpserver=False)`
   - 否则：在loop上`run_until_complete`运行初始化协程
10. 重定向日志StreamHandler到`jp_logging_stream`（避免与pytest stdout冲突）
11. 调用`app.start_app()`启动应用
12. 返回app实例

[F-080]

### jp_serverapp(jp_server_config, jp_argv, jp_configurable_serverapp) -> ServerApp

创建预配置的ServerApp实例。

**行为：**
1. 忽略多个Windows事件循环相关的DeprecationWarning
2. 调用`jp_configurable_serverapp(config=jp_server_config, argv=jp_argv)`创建并返回app

[F-081]

### jp_web_app(jp_serverapp) -> Application

返回ServerApp的web_app（供pytest_tornasync的http_server fixture使用）。

- 返回`jp_serverapp.web_app`

[F-082]

### jp_auth_header(jp_serverapp) -> dict

构造认证头字典。

**行为：**
- v1：返回`{"Authorization": f"token {jp_serverapp.token}"}`
- v2：返回`{"Authorization": f"token {jp_serverapp.identity_provider.token}"}`

[F-083]

### jp_server_cleanup(jp_asyncio_loop) (autouse=True)

自动清理ServerApp资源（autouse fixture）。

**行为：**
1. yield（测试执行）
2. 获取当前ServerApp实例：`app = ServerApp.instance()`
3. 在事件循环上运行`app._cleanup()`（捕获RuntimeError和SystemExit）
4. 若app有kernel_manager，销毁其ZMQ context：`app.kernel_manager.context.destroy()`
5. 调用`ServerApp.clear_instance()`清除单例

[F-084]

## HTTP/WebSocket请求Fixtures

### jp_fetch(jp_serverapp, http_server_client, jp_auth_header, jp_base_url) -> callable

HTTP请求工厂fixture，返回`client_fetch`函数。

**client_fetch签名：**
```python
def client_fetch(*parts, headers=None, params=None, **kwargs):
```

**参数：**
- `*parts`: URL路径段（如`"api", "spec.yaml"`），将被url_path_join拼接
- `headers` (dict|None): 请求头，默认空dict
- `params` (dict|None): 查询参数，默认空dict
- `**kwargs`: 传递给tornado HTTPClient.fetch的额外参数
- `request_timeout` (int): 请求超时，默认20秒

**行为：**
1. 使用`url_path_join(*parts)`拼接路径，`url_escape`编码
2. 拼接base URL和编码后的路径
3. 用`urllib.parse.urlencode`编码查询参数
4. 合并认证头（不覆盖用户传入的同名header）
5. 设置默认超时20秒
6. 调用`http_server_client.fetch(url, headers=headers, request_timeout=request_timeout, **kwargs)`发送请求

[F-085]

### jp_ws_fetch(jp_serverapp, http_server_client, jp_auth_header, jp_http_port, jp_base_url) -> callable

WebSocket请求工厂fixture，返回`client_fetch`函数。

**client_fetch签名：**
```python
def client_fetch(*parts, headers=None, params=None, **kwargs):
```

**行为：**
1. 类似jp_fetch拼接URL路径
2. 构造`ws://localhost:{port}`URL（使用urllib.parse）
3. 合并认证头
4. 创建`tornado.httpclient.HTTPRequest`，设置connect_timeout=120
5. 过滤kwargs：只保留`tornado.websocket.websocket_connect`签名中存在的参数
6. 调用`tornado.websocket.websocket_connect(req, **kwargs)`建立WebSocket连接

[F-086]

### send_request(jp_fetch, jp_ws_fetch) -> callable

通用请求发送fixture，自动选择HTTP或WebSocket。

**_函数签名：**
```python
async def _(url, **fetch_kwargs):
```

**行为：**
1. 若URL以`"channels"`结尾或包含`"/websocket/"`，使用`jp_ws_fetch`
2. 否则使用`jp_fetch`
3. 设置`allow_nonstandard_methods=True`允许非标准HTTP方法
4. 尝试发送请求，成功返回`r.code`
5. 捕获HTTPClientError，返回错误码`err.code`
6. WebSocket请求后关闭连接

[F-087]

## Notebook与扩展Fixtures

### jp_create_notebook(jp_root_dir) -> callable

创建notebook文件的工厂fixture。

**inner签名：**
```python
def inner(nbpath):
```

**参数：**
- `nbpath` (Path|str): notebook路径（相对于jp_root_dir）

**行为：**
1. 拼接路径：`nbpath = jp_root_dir.joinpath(nbpath)`
2. 检查后缀必须为`.ipynb`，否则抛出Exception
3. 创建父目录（`parents=True, exist_ok=True`）
4. 使用`nbformat.v4.new_notebook()`创建空notebook
5. 使用`nbformat.writes(nb, version=4)`序列化为JSON字符串
6. 写入文件
7. 返回notebook对象（NBNode）

[F-088]

### jp_server_auth_core_resources() -> dict

构建核心认证资源映射。

**行为：**
1. 遍历`JUPYTER_SERVICE_HANDLERS.values()`收集所有handler模块名
2. 动态import每个模块
3. 获取模块的`AUTH_RESOURCE`属性
4. 遍历模块的`default_handlers`，建立`url_regex → auth_resource`映射
5. 返回`resource_map`字典

[F-089]

### jp_server_auth_resources(jp_server_auth_core_resources) -> dict

直接返回`jp_server_auth_core_resources`（别名fixture，可被子项目覆盖）。

[F-090]

## 测试授权器类

### class _Authorizer(Authorizer)

继承自`jupyter_server.auth.Authorizer`（导入失败时为`object`）的测试用授权器。

**类属性：**
- `permissions: dict[str, str] = {}`：权限字典（测试中动态设置）
- `_default_regex_mapping: dict[str, str] = {}`：默认URL正则→资源映射
- `HTTP_METHOD_TO_AUTH_ACTION`：HTTP方法→认证动作映射：
  ```python
  {
      "GET": "read", "HEAD": "read", "OPTIONS": "read",
      "POST": "write", "PUT": "write", "PATCH": "write", "DELETE": "write",
      "WEBSOCKET": "execute",
  }
  ```

[F-091]

#### match_url_to_resource(url, regex_mapping=None) -> str | None

将URL匹配到认证资源名。

**行为：**
- 使用正则表达式遍历映射表
- 返回第一个fullmatch成功的资源名
- 无匹配返回None

[F-092]

#### normalize_url(path) -> str

规范化URL路径。

**行为：**
1. 若`self.parent`不存在，抛出ValueError
2. 获取base_url，若path以base_url开头则移除前缀
3. 确保path以`/`开头
4. 返回规范化后的路径

[F-093]

#### is_authorized(handler, user, action, resource) -> bool

判断请求是否被授权。

**行为：**
1. 判断方法类型：WebSocketHandler为"WEBSOCKET"，否则取`handler.request.method`
2. 规范化URL路径
3. 映射到期望的action和resource
4. 断言：若传入的action/resource与期望不匹配，抛出AssertionError
5. 检查权限：action在permissions["actions"]中 AND resource在permissions["resources"]中
6. 返回布尔值

[F-094]

### jp_server_authorizer(jp_server_auth_resources) -> type[_Authorizer]

返回配置好默认regex映射的_Authorizer类。

**行为：**
1. 设置`auth_klass._default_regex_mapping = jp_server_auth_resources`
2. 返回`_Authorizer`类（而非实例）

[F-095]

## 设计要点

1. **三层插件继承**：jupyter_server → jupyter_client + pytest_tornasync → jupyter_core，形成完整测试栈
2. **工厂fixture模式**：核心fixtures（jp_configurable_serverapp、jp_fetch、jp_ws_fetch、jp_create_notebook、jp_start_kernel）都返回内部函数，允许测试中灵活调用
3. **fixture执行顺序控制**：jp_nbconvert_templates显式依赖jp_data_dir且注释标明必须在jp_environ之前执行，利用pytest fixture依赖DAG控制顺序
4. **v1/v2双版本兼容**：通过`is_v2`标志处理Jupyter Server 1.x和2.x的配置差异（token位置、默认扩展）
5. **日志流重定向**：jp_logging_stream将ServerApp日志从stdout重定向到StringIO，避免与pytest输出冲突
6. **内存数据库**：NotebookNotary.db_file设为":memory:"，避免测试产生磁盘文件
7. **随机token**：每次测试生成随机8字符hex token，防止测试间token冲突
8. **autouse清理**：jp_server_cleanup是autouse fixture，确保每个测试后ServerApp资源被正确清理
9. **URL编码测试**：jp_base_url默认值包含`%40`（@的URL编码），测试框架是否正确处理编码URL
10. **kwargs过滤**：jp_ws_fetch使用inspect.signature过滤websocket_connect不接受的参数，增强跨版本兼容
