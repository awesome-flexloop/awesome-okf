---
type: Concept
title: ExtensionApp 开发
description: 掌握 ExtensionApp 基类、扩展类的核心属性和方法、traitlets 配置系统、settings 传递机制和生命周期钩子。
tags: [extension-app, extensionapp, traitlets, configuration, lifecycle]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T13:10:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:10:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: extension-py
    resource: /references/extension-app-source.md
    title: ExtensionApp 类源码解析
---

## ExtensionApp 基类

`ExtensionApp`（位于 `jupyter_server.extension.application`）是所有 Jupyter Server 扩展的应用基类。它继承自 `JupyterApp` → `Application`（traitlets.config.Application），提供了扩展与 Jupyter Server 集成的完整框架。

你的扩展类继承 `ExtensionApp` 并实现必要的属性和方法：

```python
from jupyter_server.extension.application import ExtensionApp

class MyExtension(ExtensionApp):
    name = "my_extension"
    handlers = [...]
    # ...
```

## 必须实现的属性

### name

```python
name = "my_extension"
```

扩展的**唯一标识符**，必须是有效的 Python 标识符（不含连字符）。此名称用于：

- 在 Jupyter Server 配置中引用扩展（`c.ServerApp.jpserver_extensions`）
- 日志输出中标识扩展
- 扩展 URL 前缀
- 配置系统中的配置类名（`c.MyExtension.xxx`）

命名约定：使用下划线分隔的小写名称，与 Python 包名一致。如果包名包含连字符（pip 允许），在 Python 模块和 name 属性中必须转为下划线。

### handlers

```python
handlers = [
    ("my-extension/ping", PingHandler),
    (r"my-extension/items/(\w+)", ItemHandler),
]
```

URL 路由表，是一个 `(url_pattern, handler_class)` 元组列表。URL 模式支持：

- **精确匹配**：`"my-extension/ping"` 匹配精确路径
- **正则表达式**：`r"my-extension/items/(\w+)"` 捕获路径参数，捕获的值作为参数传给 Handler 方法
- **路径前缀**：Jupyter Server 会自动为扩展的 handlers 添加前缀，通常是 `/<extension-name>/` 或 `/api/extensions/<extension-name>/`

## 可选属性和方法

### 可配置 Traitlets

`traitlets` 是 Jupyter 生态的配置系统，允许用户通过配置文件或命令行参数自定义扩展行为。

```python
from traitlets import Unicode, Integer, Bool, List

class MyExtension(ExtensionApp):
    # 字符串配置项
    api_base_url = Unicode(
        default_value="https://api.example.com",
        help="Base URL for the external API."
    ).tag(config=True)

    # 整数配置项
    max_items = Integer(default_value=100).tag(config=True)

    # 布尔配置项
    enable_cache = Bool(default_value=True).tag(config=True)

    # 列表配置项
    allowed_origins = List(
        trait=Unicode(),
        default_value=["http://localhost:3000"]
    ).tag(config=True)
```

`.tag(config=True)` 是关键——它标记此 trait 可以通过配置系统修改。用户可以在 `jupyter_server_config.py` 中设置：

```python
c.MyExtension.api_base_url = "https://custom-api.example.com"
c.MyExtension.max_items = 50
c.MyExtension.enable_cache = False
```

或通过命令行：

```bash
jupyter server --MyExtension.api_base_url=https://custom-api.example.com
```

### initialize_settings()

```python
def initialize_settings(self):
    self.settings.update({
        "ping_response": self.ping_response,
        "api_base_url": self.api_base_url,
        "max_items": self.max_items,
    })
```

这是最常用的生命周期钩子，在扩展初始化时调用。**模板中的模式**是将所有需要在 Handler 中访问的配置值注入 `self.settings` 字典。

`self.settings` 是 Tornado Application 的 settings 字典，在所有 Handler 中通过 `self.settings` 属性访问。这是配置从 ExtensionApp 传递到 Handler 的标准方式。

### 其他生命周期方法

| 方法 | 调用时机 | 用途 |
|------|---------|------|
| `initialize_settings()` | 设置阶段 | 注入 settings、初始化资源 |
| `initialize_templates()` | 模板阶段 | 配置 Jinja2 模板环境（如需要 HTML 渲染） |
| `initialize_handlers()` | Handler 加载阶段 | 动态注册 handlers（可替代类级别 handlers） |
| `start()` | 扩展启动 | 启动后台任务（如定时任务、WebSocket 服务） |
| `stop()` | 扩展停止 | 清理资源（关闭连接、停止线程等） |

大多数简单扩展只需要实现 `initialize_settings()`。

## 扩展发现与注册

Jupyter Server 通过 `_jupyter_server_extension_points()` 函数发现扩展。这个函数定义在包的 `__init__.py` 中：

```python
from .extension import MyExtension

def _jupyter_server_extension_points():
    return [{
        "module": "my_extension",  # Python 模块路径
        "app": MyExtension         # ExtensionApp 子类
    }]
```

Jupyter Server 启动时：
1. 扫描 `{sys.prefix}/etc/jupyter/jupyter_server_config.d/*.json`
2. 加载配置，找到启用的扩展
3. 导入模块，调用 `_jupyter_server_extension_points()` 获取 ExtensionApp 类
4. 实例化 ExtensionApp，调用其生命周期方法
5. 将 ExtensionApp.handlers 注册到 Tornado 路由表

## static 文件和 templates 目录

ExtensionApp 还支持静态文件和 HTML 模板服务：

```python
class MyExtension(ExtensionApp):
    name = "my_extension"

    # 静态文件目录
    static_paths = [...]
    # 模板目录
    template_paths = [...]
```

但对于纯 API 扩展（如本模板生成的），不需要 static 和 templates。

## 多扩展点

一个 Python 包可以注册多个扩展点：

```python
def _jupyter_server_extension_points():
    return [
        {"module": "my_extension", "app": MyExtension},
        {"module": "my_extension.admin", "app": AdminExtension},
    ]
```

但这是高级用法，大多数扩展只注册一个。

## 完整扩展示例

```python
from traitlets import Unicode, Integer
from jupyter_server.extension.application import ExtensionApp
from .handlers import PingHandler, DataHandler, StatusHandler


class MyExtension(ExtensionApp):
    name = "my_extension"

    handlers = [
        ("my-extension/ping", PingHandler),
        ("my-extension/data", DataHandler),
        ("my-extension/status", StatusHandler),
    ]

    # 可配置项
    ping_response = Unicode(default_value="pong").tag(config=True)
    data_dir = Unicode(default_value="/tmp/my_extension").tag(config=True)
    max_retries = Integer(default_value=3).tag(config=True)

    def initialize_settings(self):
        self.settings.update({
            "ping_response": self.ping_response,
            "data_dir": self.data_dir,
            "max_retries": self.max_retries,
        })
```

## 相关概念

- [API Handler 开发](/concepts/05-api-handlers.md)
- [配置发现机制](/concepts/06-config-discovery.md)
- [测试策略](/concepts/07-testing.md)
- [ExtensionApp 源码解析](/references/extension-app-source.md)
