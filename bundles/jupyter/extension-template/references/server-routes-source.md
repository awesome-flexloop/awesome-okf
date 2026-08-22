---
type: Reference
title: Python 服务端模板解析
description: frontend-and-server 类型扩展的 Python 后端模板，包括 __init__.py 入口点、routes.py 路由处理器和 server-config 配置的完整参考。
tags: [python, server-extension, apihandler, tornado, routes, authentication]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T12:15:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:15:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: server-templates
    resource: /references/server-routes-source.md
    title: Python 后端模板源码（__init__.py.jinja, routes.py.jinja, check_auth.py.jinja）
---

## Python 服务端模板解析

Python 后端文件仅在 `kind == 'frontend-and-server'` 时生成，包括三个核心部分：包入口点（`__init__.py`）、路由处理器（`routes.py`）、Jupyter 配置文件（`jupyter-config/server-config/`）和认证检查脚本（`.github/scripts/check_auth.py`）。

## __init__.py 包入口点

### 版本处理

```python
try:
    from ._version import __version__
except ImportError:
    import warnings
    warnings.warn("Importing '{{ python_name }}' outside a proper installation.")
    __version__ = "dev"
```

`_version.py` 由 hatch-nodejs-version 钩子自动生成。开发模式下未安装时 fallback 到 `"dev"`。

### 前端扩展路径注册

```python
def _jupyter_labextension_paths():
    return [{
        "src": "labextension",
        "dest": "{{ labextension_name }}"
    }]
```

所有扩展类型（包括纯前端）都需要此函数，告诉 JupyterLab 在哪里找到前端静态资源。

### 服务端扩展点（仅 frontend-and-server）

```python
from .routes import setup_route_handlers

def _jupyter_server_extension_points():
    return [{
        "module": "{{ python_name }}"
    }]

def _load_jupyter_server_extension(server_app):
    setup_route_handlers(server_app.web_app)
    name = "{{ python_name }}"
    server_app.log.info(f"Registered {name} server extension")
```

三个关键函数：
1. `_jupyter_server_extension_points()`：声明服务端扩展模块
2. `_load_jupyter_server_extension(server_app)`：Jupyter Server 启动时调用，注册路由
3. `setup_route_handlers(web_app)`：自定义函数，将 HTTP 处理器挂载到 Tornado web app

## routes.py 路由处理器

### 导入

```python
import json
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
import tornado
```

关键基类：
- `APIHandler`：Jupyter Server 提供的 API 处理器基类（继承自 Tornado 的 RequestHandler）
- `url_path_join`：安全的 URL 路径拼接工具

### HelloRouteHandler

```python
class HelloRouteHandler(APIHandler):
    @tornado.web.authenticated
    def get(self):
        self.finish(json.dumps({
            "data": (
                "Hello, world!"
                " This is the '/{{ python_name | replace('_', '-') }}/hello' endpoint."
                " Try visiting me in your browser!"
            ),
        }))
```

要点：
- 继承 `APIHandler`（而非直接使用 `tornado.web.RequestHandler`）
- 每个 HTTP 方法（`get`/`post`/`put`/`delete`/`patch`/`head`/`options`）必须装饰 `@tornado.web.authenticated`
- 公共端点需使用 `@allow_unauthenticated` 或 `@ws_authenticated`（来自 `jupyter_server.auth.decorator`）
- 使用 `self.finish(json.dumps({...}))` 返回 JSON 响应

### 路由注册

```python
def setup_route_handlers(web_app):
    host_pattern = ".*$"
    base_url = web_app.settings["base_url"]
    hello_route_pattern = url_path_join(base_url, "{{ python_name | replace('_', '-') }}", "hello")
    handlers = [(hello_route_pattern, HelloRouteHandler)]
    web_app.add_handlers(host_pattern, handlers)
```

要点：
- URL 命名空间使用 `{{ python_name | replace('_', '-') }}`（下划线转连字符），与前端 `requestAPI` 函数一致
- 使用 `url_path_join()` 拼接路径，避免硬编码
- `host_pattern = ".*$"` 匹配所有主机名
- 调用 `web_app.add_handlers()` 注册路由

## Jupyter Server 配置

`jupyter-config/server-config/{{python_name}}.json`：

```json
{
  "ServerApp": {
    "jpserver_extensions": {
      "{{ python_name }}": true
    }
  }
}
```

此文件通过 wheel 的 `shared-data` 安装到 `etc/jupyter/jupyter_server_config.d/`，自动启用服务端扩展。

## 认证检查脚本

`.github/scripts/check_auth.py` 在 CI 中运行，验证所有端点都有认证装饰器：

```python
from jupyter_server.serverapp import ServerApp
from jupyter_server.utils import JupyterServerAuthWarning

app = ServerApp(
    allow_unauthenticated_access=False,
    jpserver_extensions={"{{ python_name }}": True},
    reraise_server_extension_failures=True,
)

with warnings.catch_warnings(record=True) as records:
    warnings.simplefilter("always")
    app.initialize(argv=[], find_extensions=False, new_httpserver=False)

problems = [
    str(record.message)
    for record in records
    if issubclass(record.category, JupyterServerAuthWarning)
]

if problems:
    sys.exit("...Add a `@tornado.web.authenticated` decorator...")
```

工作原理：
1. 创建一个禁止未认证访问的 ServerApp 实例
2. 加载扩展并捕获 JupyterServerAuthWarning
3. 如果有警告（即缺少认证装饰器），CI 构建失败

## 测试配置（conftest.py）

```python
import pytest
pytest_plugins = ("pytest_jupyter.jupyter_server",)

@pytest.fixture
def jp_server_config(jp_server_config):
    return {
        "ServerApp": {
            "jpserver_extensions": {"{{ python_name }}": True},
            "allow_unauthenticated_access": False,
        }
    }
```

使用 pytest-jupyter 插件提供的 `jupyter_server` fixture，在测试中启用扩展并强制认证检查。

## 相关概念

- [服务端扩展开发](/concepts/07-server-extension.md)
- [前端扩展开发 — 前后端通信](/concepts/06-frontend-extension.md)
- [三层测试策略](/concepts/11-testing-strategy.md)
- [CI/CD 工作流详解](/concepts/12-ci-workflows.md)
