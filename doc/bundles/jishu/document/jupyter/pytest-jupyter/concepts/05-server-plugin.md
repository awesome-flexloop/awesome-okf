---
okf_version: "0.2"
type: concept
title: "Server插件详解"
description: "深入理解 jupyter_server 插件：ServerApp生命周期管理、jp_configurable_serverapp工厂、jp_fetch/jp_ws_fetch HTTP测试客户端、认证授权测试、自动清理机制。"
tags: [server-plugin, jupyter-server, serverapp, lifecycle, http-fetch, websocket, authentication, authorization, cleanup, factory-pattern]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:45:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T14:45:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: jupyter-server-source
    resource: "/references/jupyter-server-source.md"
    title: "Server插件源码信源"
  - id: pytest-tornasync-source
    resource: "/references/pytest-tornasync-source.md"
    title: "Tornado异步测试源码信源"
---

# Server插件详解

Server插件（`pytest_jupyter.jupyter_server`）是pytest-jupyter的最高层插件，提供Jupyter Server完整生命周期管理、HTTP/WebSocket测试客户端、Notebook创建工具、认证授权测试基础设施。加载此插件自动获得core、client和tornasync的所有fixtures。

## 激活与依赖

```bash
pip install "pytest-jupyter[server]"
```

依赖包括：`jupyter_server>=1.21`、`tornado`、`nbformat`、`jupyter_client`、`ipykernel`。

```python
# conftest.py
pytest_plugins = ["pytest_jupyter.jupyter_server"]
```

[F-070]

## 插件继承链

```
jupyter_server.py
├── from .jupyter_core import *      # core fixtures
├── from .pytest_tornasync import *  # tornado HTTP fixtures
└── from .utils import mkdir         # 工具函数

# 注意：jupyter_client的fixtures通过core→client的间接路径不可用，
# 但jupyter_server.py本身依赖ipykernel/jupyter_client，且jp_start_kernel
# 需要单独加载jupyter_client插件才能使用。
```

## ServerApp生命周期管理

### 配置Fixtures

| Fixture | 默认值 | 用途 |
|---------|-------|------|
| `jp_server_config` | `Config({"ServerApp": {"jpserver_extensions": {"jupyter_server_terminals": True}}})` (v2) | 默认ServerApp配置，可被覆盖 |
| `jp_argv` | `[]` | 命令行参数列表 |
| `jp_base_url` | `"/a%40b/"` | 基础URL（含URL编码测试） |
| `jp_root_dir` | `{tmp_path}/root_dir` | Notebook根目录 |
| `jp_template_dir` | `{tmp_path}/templates` | 模板目录 |
| `jp_http_port` | 自动分配空闲端口 | HTTP端口 |

[F-071]~[F-076]

### 核心工厂：jp_configurable_serverapp

`jp_configurable_serverapp`是Server插件最核心的fixture，返回一个工厂函数，允许在测试中灵活创建配置化的ServerApp实例。

**fixture依赖顺序（关键）：**
```
jp_nbconvert_templates  ← 必须在jp_environ之前（在monkeypatch前复制模板）
    ↓
jp_environ              ← 环境隔离
    ↓
jp_server_config, jp_argv, jp_http_port, jp_base_url, tmp_path, jp_root_dir, jp_logging_stream, jp_asyncio_loop
    ↓
jp_configurable_serverapp (返回_configurable_serverapp函数)
```

**_configurable_serverapp函数参数：**
```python
def _configurable_serverapp(
    config=jp_server_config,    # 配置对象
    base_url=jp_base_url,        # 基础URL
    argv=jp_argv,                # 命令行参数
    environ=jp_environ,          # 环境（fixture依赖触发）
    http_port=jp_http_port,      # 端口
    tmp_path=tmp_path,           # 临时路径
    root_dir=jp_root_dir,        # 根目录
    **kwargs                     # 传递给ServerApp.instance()的额外参数
):
```

**创建流程：**
1. `ServerApp.clear_instance()` — 清除已有单例
2. v2版本注入`jupyter_server_terminals`扩展
3. 设置`c.NotebookNotary.db_file = ":memory:"` — 内存SQLite，无磁盘IO
4. 生成随机8字符hex token
5. 配置token位置（v1用`kwargs["token"]`，v2用`c.IdentityProvider.token`）
6. 设置root_dir（如果不为None）
7. 创建ServerApp实例：
   ```python
   app = ServerApp.instance(
       log_level="DEBUG",
       port=http_port,
       port_retries=0,        # 端口不重试
       open_browser=False,    # 不打开浏览器
       base_url=base_url,
       config=c,
       allow_root=True,       # 允许root运行（Docker/CI）
       **kwargs,
   )
   ```
8. `app.init_signal = lambda: None` — 禁用信号处理
9. 初始化app（处理事件循环是否在运行）
10. 重定向日志到`jp_logging_stream`
11. `app.start_app()` — 启动应用

[F-080]

### 便捷fixture：jp_serverapp

```python
@pytest.fixture
def jp_serverapp(jp_server_config, jp_argv, jp_configurable_serverapp):
    return jp_configurable_serverapp(config=jp_server_config, argv=jp_argv)
```

当你不需要自定义ServerApp配置时，直接使用`jp_serverapp`即可获得一个预配置好的ServerApp实例。

[F-081]

### 自动清理：jp_server_cleanup（autouse）

```python
@pytest.fixture(autouse=True)
def jp_server_cleanup(jp_asyncio_loop):
    yield
    app = ServerApp.instance()
    try:
        jp_asyncio_loop.run_until_complete(app._cleanup())
    except (RuntimeError, SystemExit) as e:
        print("ignoring cleanup error", e)
    if hasattr(app, "kernel_manager"):
        app.kernel_manager.context.destroy()
    ServerApp.clear_instance()
```

每个测试结束后自动执行：
1. 运行`app._cleanup()`清理Server资源
2. 销毁kernel_manager的ZMQ上下文
3. 清除ServerApp单例

清理错误被捕获并忽略（避免清理失败影响测试结果判定）。

[F-084]

## HTTP测试客户端

### jp_fetch：HTTP请求工厂

`jp_fetch`是最常用的fixture，返回一个发送HTTP请求的工厂函数：

```python
async def test_api(jp_fetch):
    # GET请求
    response = await jp_fetch("api", "spec.yaml")
    assert response.code == 200

    # 带查询参数
    response = await jp_fetch("api", "kernels", params={"state": "idle"})

    # POST请求带body
    import json
    response = await jp_fetch(
        "api", "kernels",
        method="POST",
        body=json.dumps({"name": "python3"})
    )
```

**client_fetch函数自动处理：**
- URL路径拼接（`url_path_join`）和编码（`url_escape`）
- base URL前缀添加
- 查询参数URL编码
- 认证头注入（`jp_auth_header`中的token）
- 默认超时20秒（可通过`request_timeout`覆盖）

[F-085]

### jp_ws_fetch：WebSocket连接工厂

```python
async def test_kernel_channels(jp_fetch, jp_ws_fetch):
    # 创建kernel
    r = await jp_fetch("api", "kernels", method="POST", body="{}")
    kid = json.loads(r.body.decode())["id"]

    # 建立WebSocket连接
    ws = await jp_ws_fetch("api", "kernels", kid, "channels")
    # ... 使用ws发送/接收消息
    ws.close()
```

**特殊处理：**
- 使用`ws://localhost:{port}`协议
- connect_timeout设为120秒（WebSocket连接可能较慢）
- **kwargs过滤**：通过`inspect.signature`检查，只传递`tornado.websocket_connect`接受的参数，跨版本兼容

[F-086]

### jp_auth_header：认证头

```python
@pytest.fixture
def jp_auth_header(jp_serverapp):
    if not is_v2:
        return {"Authorization": f"token {jp_serverapp.token}"}
    return {"Authorization": f"token {jp_serverapp.identity_provider.token}"}
```

根据Server版本（v1/v2）自动从正确位置获取token，构造`Authorization: token <token>`头。

[F-083]

### send_request：简化请求fixture

```python
async def test_with_send_request(send_request):
    code = await send_request("api/spec.yaml", method="GET")
    assert code == 200  # 直接返回状态码
```

`send_request`是一个更简单的请求工具：
- 自动选择HTTP或WebSocket（URL含`channels`或`/websocket/`时用ws）
- 返回状态码而非response对象
- 自动设置`allow_nonstandard_methods=True`
- 捕获HTTPClientError并返回错误码

[F-087]

### 日志捕获：jp_logging_stream

```python
@pytest.fixture
def jp_logging_stream():
    logging_stream = io.StringIO()
    yield logging_stream
    output = logging_stream.getvalue()
    if output:
        print(output)
    return output
```

ServerApp的日志被重定向到此StringIO流，避免与pytest的stdout捕获冲突。测试结束后如果有日志内容则print输出方便调试。

[F-079]

## Notebook与模板

### jp_create_notebook：Notebook工厂

```python
def test_create_nb(jp_create_notebook):
    nb = jp_create_notebook("test.ipynb")
    assert "nbformat" in nb
```

**行为：**
- 检查文件扩展名必须为`.ipynb`
- 创建父目录
- 使用`nbformat.v4.new_notebook()`创建空notebook
- 序列化为v4格式JSON写入文件
- 返回notebook对象（NBNode）

[F-088]

### jp_nbconvert_templates：模板复制

此fixture在`jp_environ`（monkeypatch）生效**之前**执行，从真实Jupyter路径查找nbconvert模板目录，并复制到临时数据目录中。确保测试环境中有nbconvert模板可用。

[F-078]

## 认证授权测试

### _Authorizer测试类

```python
class _Authorizer(Authorizer):
    permissions: dict[str, str] = {}
    HTTP_METHOD_TO_AUTH_ACTION = {
        "GET": "read", "HEAD": "read", "OPTIONS": "read",
        "POST": "write", "PUT": "write", "PATCH": "write", "DELETE": "write",
        "WEBSOCKET": "execute",
    }
```

`_Authorizer`是一个专门用于测试的授权器：
- `match_url_to_resource(url)`: 将URL匹配到资源名（如`/api/kernels`→`"kernels"`）
- `normalize_url(path)`: 去除base_url前缀，确保路径以`/`开头
- `is_authorized(handler, user, action, resource)`: 断言传入的action/resource与HTTP方法/URL映射一致，然后检查permissions字典决定授权结果

**关键特性**：`is_authorized`中使用`raise AssertionError`来验证Jupyter Server的授权层是否传递了正确的action和resource参数。

[F-091]~[F-094]

### jp_server_authorizer fixture

```python
@pytest.fixture
def jp_server_authorizer(jp_server_auth_resources):
    auth_klass = _Authorizer
    auth_klass._default_regex_mapping = jp_server_auth_resources
    return auth_klass
```

返回配置好URL正则→资源映射的`_Authorizer`类（注意：返回类而非实例）。

[F-095]

### 认证资源映射

- `jp_server_auth_core_resources`: 遍历`JUPYTER_SERVICE_HANDLERS`动态构建URL regex→resource映射
- `jp_server_auth_resources`: 别名fixture，返回上面的结果

[F-089][F-090]

## 自定义ServerApp配置

### 覆盖默认配置

```python
import pytest
from traitlets.config import Config

@pytest.fixture
def jp_server_config():
    """覆盖默认配置，使用echo内核作为默认内核"""
    c = Config()
    c.MultiKernelManager.default_kernel_name = "echo"
    c.ServerApp.jpserver_extensions = {
        "my_extension": True
    }
    return c
```

### 使用jp_configurable_serverapp创建自定义实例

```python
async def test_custom_server(jp_configurable_serverapp):
    app = jp_configurable_serverapp(
        root_dir="/custom/path",
        base_url="/custom-base/",
    )
    # ... 测试自定义app
```

### 覆盖base_url

```python
@pytest.fixture
def jp_base_url():
    return "/"  # 使用根路径而非默认的/a%40b/
```

## Tornado HTTP层Fixtures（来自pytest_tornasync）

| Fixture | 用途 |
|---------|------|
| `io_loop` | 当前Tornado IOLoop实例 |
| `http_server_port` | (socket, port)元组，绑定空闲端口 |
| `http_server` | Tornado HTTPServer实例 |
| `http_server_client` | AsyncHTTPServerClient测试客户端 |
| `jp_web_app` | ServerApp的web_app（tornado Application） |

注意：`jp_web_app`返回`jp_serverapp.web_app`，是连接pytest-jupyter和tornasync的桥梁——tornasync的`http_server`fixture依赖`jp_web_app`来创建服务器。

[F-082]

## 常见测试模式

### 模式1：测试REST API端点

```python
async def test_my_endpoint(jp_fetch):
    response = await jp_fetch("my_extension", "endpoint", method="GET")
    assert response.code == 200
    data = json.loads(response.body)
```

### 模式2：测试内核生命周期

```python
async def test_kernel_lifecycle(jp_fetch, jp_ws_fetch):
    # 创建kernel
    r = await jp_fetch("api", "kernels", method="POST", body="{}")
    kid = json.loads(r.body.decode())["id"]

    # 连接WebSocket
    ws = await jp_ws_fetch("api", "kernels", kid, "channels")
    # ... 通信
    ws.close()

    # 删除kernel
    r = await jp_fetch("api", "kernels", kid, method="DELETE")
    assert r.code == 204
```

### 模式3：测试自定义授权器

```python
async def test_auth(jp_serverapp, jp_server_authorizer, jp_fetch):
    # 配置权限
    jp_server_authorizer.permissions = {
        "actions": ["read"],
        "resources": ["spec"]
    }
    jp_serverapp.authorizer_class = jp_server_authorizer

    response = await jp_fetch("api", "spec.yaml")
    assert response.code == 200
```

## Server插件使用建议

1. **优先使用jp_fetch/jp_ws_fetch**：不要手动创建tornado HTTP客户端，这些fixtures已处理认证、URL拼接、超时等细节
2. **测试间隔离自动完成**：jp_server_cleanup是autouse，每个测试后ServerApp被完全清理，不需要手动teardown
3. **覆盖fixture来自定义配置**：通过覆盖`jp_server_config`、`jp_base_url`等fixture自定义行为
4. **使用jp_configurable_serverapp创建多个app实例**：需要对比不同配置的行为时，在测试内多次调用工厂函数
5. **日志调试**：测试失败时检查jp_logging_stream的输出（print到控制台），DEBUG级别日志能帮助定位问题
6. **注意v1/v2差异**：如果你的扩展需要兼容两个版本，使用`is_v2`标志或分别测试token获取方式

---

**下一步阅读：**
- [Tornado异步支持](06-tornasync-plugin.md) — HTTP服务器/客户端底层实现
- [Echo内核深入](07-echo-kernel.md) — 测试内核实现与扩展
- [Fixture工厂模式](08-fixture-factories.md) — 可配置fixtures的设计模式
