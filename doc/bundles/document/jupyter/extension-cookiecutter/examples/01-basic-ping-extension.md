---
type: Example
title: 基础 Ping 扩展示例
description: 从零理解模板生成的 Ping 扩展的完整代码，包括 Extension 类、PingHandler、测试和配置的逐行解析。
tags: [example, hello-world, ping, basic, walkthrough]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T13:20:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:20:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: extension-py
    resource: /references/extension-app-source.md
    title: ExtensionApp 类源码解析
  - id: handler-py
    resource: /references/handler-source.md
    title: PingHandler 请求处理器源码解析
  - id: test-py
    resource: /references/test-source.md
    title: 测试源码解析
---

## 概述

模板生成的项目已经包含一个可运行的 Ping 扩展示例。本示例逐文件解析这个示例的全部代码，帮助你理解每个文件的作用。

## 完整文件清单

生成项目后（包名 `my_extension`），核心文件如下：

```
my_extension/
├── my_extension/
│   ├── __init__.py      # 包入口：版本号 + 扩展点注册
│   ├── extension.py     # ExtensionApp：扩展核心类
│   └── handlers.py      # PingHandler：HTTP 请求处理器
├── jupyter-config/
│   └── jupyter_server_config.d/
│       └── my_extension.json  # 自动启用配置
├── conftest.py          # pytest 配置
└── my_extension/tests/
    └── test_handlers.py # 测试用例
```

## 文件 1：__init__.py

```python
"""A Jupyter Server extension."""
from .extension import Extension
__version__ = "0.1.0"


def _jupyter_server_extension_points():
    return [{
        "module": "my_extension",
        "app": Extension
    }]
```

逐行解析：

1. **docstring**：项目描述（来自 `project_short_description` 参数）
2. **导入 Extension**：从同包的 extension 模块导入 Extension 类
3. **版本号**：`__version__ = "0.1.0"`，hatchling 从此处读取包版本
4. **扩展点函数**：`_jupyter_server_extension_points()` 是 Jupyter Server 发现扩展的入口
   - 返回一个列表（支持多扩展点）
   - 每个元素是包含 `module`（模块路径）和 `app`（ExtensionApp 子类）的字典

## 文件 2：extension.py

```python
from traitlets import Unicode

from jupyter_server.extension.application import ExtensionApp
from .handlers import PingHandler


class Extension(ExtensionApp):

    name = "my_extension"
    handlers = [
        ("my-extension/ping", PingHandler)
    ]

    ping_response = Unicode(default_value="pong").tag(config=True)

    def initialize_settings(self):
        self.settings.update({
            "ping_response": self.ping_response
        })
```

逐行解析：

1. **导入**：
   - `Unicode`：traitlets 的字符串类型，用于定义可配置属性
   - `ExtensionApp`：Jupyter Server 扩展应用基类
   - `PingHandler`：我们定义的请求处理器

2. **Extension 类**：
   - `name = "my_extension"`：扩展唯一标识（注意：Python 模块名下划线）
   - `handlers`：URL 路由表。将 `my-extension/ping`（注意：URL 用连字符）映射到 PingHandler
   - `ping_response`：可配置的 Unicode trait，默认值 `"pong"`，`.tag(config=True)` 允许用户通过配置修改
   - `initialize_settings()`：初始化时将 ping_response 值注入 settings 字典，供 Handler 访问

## 文件 3：handlers.py

```python
import json

from jupyter_server.extension.handler import ExtensionHandlerMixin
from jupyter_server.base.handlers import APIHandler
import tornado


class PingHandler(ExtensionHandlerMixin, APIHandler):
    @property
    def ping_response(self):
        return self.settings["ping_response"]

    @tornado.web.authenticated
    def get(self):
        self.finish(json.dumps({
            "ping_response": self.ping_response
        }))
```

逐行解析：

1. **导入**：
   - `json`：序列化响应
   - `ExtensionHandlerMixin`：扩展上下文 mixin
   - `APIHandler`：Jupyter API 端点基类
   - `tornado`：使用 `@tornado.web.authenticated` 装饰器

2. **PingHandler 类**：
   - 继承 `ExtensionHandlerMixin` 和 `APIHandler`（顺序重要：Mixin 在前）
   - `ping_response` property：从 `self.settings` 读取配置值（在 Extension.initialize_settings 中注入）
   - `get()` 方法：处理 GET 请求
     - `@tornado.web.authenticated`：要求认证
     - `self.finish(json.dumps({...}))`：返回 JSON 响应

## 文件 4：my_extension.json（配置发现）

```json
{
  "ServerApp": {
    "jpserver_extensions": {
      "my_extension": true
    }
  }
}
```

这个文件通过 pip install 时被安装到 `{sys.prefix}/etc/jupyter/jupyter_server_config.d/`，告诉 Jupyter Server 自动启用 `my_extension` 扩展。

## 文件 5：conftest.py

```python
import pytest

pytest_plugins = ["jupyter_server.pytest_plugin"]

@pytest.fixture
def jp_server_config(jp_server_config):
     return {"ServerApp": {"jpserver_extensions": {"my_extension": True}}}
```

- 注册 pytest-jupyter 插件（提供 `jp_fetch` 等 fixture）
- 覆盖 `jp_server_config`，确保测试时启用扩展

## 文件 6：test_handlers.py

```python
import json


async def test_get(jp_fetch):
    response = await jp_fetch("my-extension/ping")

    assert response.code == 200
    payload = json.loads(response.body)
    assert payload == {
        "ping_response": "pong"
    }
```

- 异步测试函数，使用 `jp_fetch` fixture
- 发送 GET 请求到 `my-extension/ping`
- 验证状态码 200 和响应内容

## 运行并测试

```bash
# 生成项目
cookiecutter https://github.com/jupyter-server/extension-cookiecutter
# 按提示输入，package_name 用 my_extension

# 安装
cd my_extension
pip install -e ".[test]"

# 运行测试
pytest
# 预期：1 passed

# 启动 Jupyter Server
jupyter server --autoreload

# 在另一个终端测试（替换 token）
curl http://localhost:8888/my-extension/ping?token=<your-token>
# 预期：{"ping_response": "pong"}
```

## 自定义 ping_response

通过配置文件修改 ping_response 的默认值：

```python
# jupyter_server_config.py
c.Extension.ping_response = "hello from config"
```

重启 Jupyter Server 后，`/ping` 端点返回 `{"ping_response": "hello from config"}`。

## 这就是全部

这就是模板生成的完整示例——一个可以工作的 Jupyter Server 扩展，只用了约 30 行核心代码。模板提供了所有基础设施（构建、测试、CI、配置发现），你只需要在此基础上添加自己的 Handler 和业务逻辑。

## 相关概念

- [ExtensionApp 开发](/concepts/04-extension-app.md)
- [API Handler 开发](/concepts/05-api-handlers.md)
- [测试策略](/concepts/07-testing.md)
- [添加自定义 API 端点示例](/examples/02-custom-endpoint.md)
