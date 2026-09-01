---
type: Concept
title: "扩展系统"
description: "ExtensionApp 扩展应用、ExtensionManager 扩展发现加载机制、entry points 注册、静态资源与自定义 API"
tags: [extensions, extension-app, plugin, entry-points, extension-manager, lab-server]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:55:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: extension
    resource: /references/extension-source.md
    title: extension/ 扩展系统源码信源
---

# 扩展系统

扩展系统允许第三方包以标准方式向 Jupyter Server 添加功能：注册自定义 URL Handler、提供静态资源、添加配置选项、注入前端插件。ExtensionApp 是扩展的核心基类。

## 扩展类型

| 类型 | 说明 | 示例 |
|------|------|------|
| Server Extension | 服务端扩展（Handler、API） | jupyterlab、nbclassic |
| Lab Extension | JupyterLab 前端插件 | jupyterlab-git |
| 混合扩展 | 前后端结合 | 大多数实用扩展 |

## ExtensionApp 基类

每个服务端扩展继承 `ExtensionApp`（基于 `JupyterApp`/`traitlets.Configurable`）：

```python
from jupyter_server.extension.application import ExtensionApp
from traitlets import Unicode, Bool

class MyExtension(ExtensionApp):
    # 扩展元数据
    name = "my_extension"                     # 扩展名称（必填）
    extension_url = "/myext"                  # 默认入口 URL
    load_other_extensions = True              # 是否加载其他扩展

    # 配置项（traitlets）
    my_config = Unicode("default_value").tag(config=True)
    feature_enabled = Bool(True).tag(config=True)

    # 静态资源路径
    static_paths = ["static"]                 # 静态文件目录列表
    template_paths = ["templates"]            # Jinja2 模板目录列表
    settings = {"mykey": "myvalue"}           # 附加到 application.settings

    def initialize_settings(self):
        """初始化扩展特定设置（可选）"""
        self.settings.update({
            "my_service": MyService(),
        })

    def initialize_templates(self):
        """初始化 Jinja2 模板环境（可选）"""
        pass

    def initialize_handlers(self):
        """注册 URL Handlers（核心方法）"""
        self.handlers.extend([
            ("/myext/api/data", MyDataHandler),
            ("/myext/static/(.*)", FileFindHandler,
             {"path": self.static_paths[0]}),
        ])
```

## ExtensionApp 生命周期

```
ServerApp 启动
  │
  ▼
ExtensionManager.discover_extensions()
  │ 查找 jupyter_server_extensions entry points
  │ 或包中的 _jupyter_server_extension_points()
  │
  ▼
对每个 ExtensionApp：
  1. 实例化 ExtensionApp
  2. 调用 initialize_settings()
  3. 调用 initialize_templates()
  4. 调用 initialize_handlers() → 注册 URL 路由
  5. 将 static_paths 注册到静态文件服务
  6. 扩展挂载到 serverapp
```

## 扩展发现机制

### 方式 1：Entry Points（推荐）

在 `pyproject.toml` 或 `setup.cfg` 中注册 entry point：

```toml
# pyproject.toml
[project.entry-points."jupyter_server.extensions"]
my_extension = "my_extension:MyExtension"
```

```ini
# setup.cfg
[options.entry_points]
jupyter_server.extensions =
    my_extension = my_extension:MyExtension
```

### 方式 2：`_jupyter_server_extension_points()` 函数

在包的 `__init__.py` 中定义：

```python
def _jupyter_server_extension_points():
    return [{"module": "my_extension", "app": MyExtension}]
```

### 方式 3：旧版 `_jupyter_server_extension_paths()`

兼容 v1.x 旧格式，仅支持简单扩展：

```python
def _jupyter_server_extension_paths():
    return [{"module": "my_extension"}]

def load_jupyter_server_extension(nbapp):
    """旧版扩展加载函数"""
    nbapp.log.info("My extension loaded!")
    webapp = nbapp.web_app
    webapp.add_handlers(".*$", [("/myext/api/old", OldHandler)])
```

## 扩展管理 API

`ExtensionManager` 提供 REST API 管理扩展：

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/extensions` | 列出所有已发现的扩展 |
| GET | `/api/extensions/<name>` | 获取扩展详情 |
| POST | `/api/extensions/<name>` | 启用/禁用扩展 |

### 扩展详情模型

```json
{
  "name": "jupyterlab",
  "version": "4.0.0",
  "enabled": true,
  "status": "enabled",
  "extensions": [
    {
      "module": "jupyterlab",
      "app": "LabApp",
      "loaded": true
    }
  ]
}
```

## 扩展 URL 命名空间

扩展的 Handler 应使用统一的 URL 前缀（通常是 `/<extension_name>/...`），避免与核心 API 冲突：

```
核心 API:    /api/contents, /api/kernels, /api/sessions
扩展 API:    /myext/api/..., /lab/api/..., /nbclassic/...
静态资源:    /static/<extension_name>/...
```

Jupyter Server 自动为扩展静态资源注册路由：`/static/<ext_name>/<file>` 映射到 `static_paths` 中的文件。

## 配置扩展

扩展可以通过 traitlets 提供配置项，用户在 `jupyter_server_config.py` 中配置：

```python
# jupyter_server_config.py
c.MyExtension.my_config = "custom_value"
c.MyExtension.feature_enabled = False
```

扩展也可以通过 `_load_` 前缀的 traitlets 控制加载行为：

| traitlet | 说明 |
|----------|------|
| `_load_jupyter_server_extension` | 是否自动加载 |

## JupyterLab 作为 Extension 的范例

JupyterLab 是最大的 ExtensionApp 实例：

```python
# jupyterlab/labapp.py
class LabApp(ExtensionApp):
    name = "jupyterlab"
    extension_url = "/lab"
    static_paths = ["static"]  # 编译后的前端文件
    app_url = "/lab"

    def initialize_handlers(self):
        self.handlers.extend([
            (r"/lab", LabHandler),
            (r"/lab/api/(.*)", LabApiHandler),
            (r"/lab/workspaces/(.+)", WorkspacesHandler),
            (r"/lab/api/workspaces", WorkspacesHandler),
            # ... 更多路由
        ])
```

JupyterLab 前端作为静态资源由 Jupyter Server 提供服务，前后端通过 `/lab/api/*` 通信。

## 禁用扩展

### 方法 1：配置文件

```python
c.ServerApp.jpserver_extensions = {
    "my_extension": False,  # 禁用特定扩展
}
```

### 方法 2：命令行

```bash
jupyter server --ServerApp.jpserver_extensions="{'my_extension': False}"
```

### 方法 3：配置文件禁用

在 `jupyter_server_config.d/` 目录中创建 JSON 配置：

```json
{
  "ServerApp": {
    "jpserver_extensions": {
      "my_extension": false
    }
  }
}
```

## 链接扩展

ExtensionApp 可以相互依赖，通过 `_link_jupyter_server_extension(serverapp)` 方法在加载时获取对 ServerApp 的引用：

```python
class MyExtension(ExtensionApp):
    def initialize_settings(self):
        # self.serverapp 引用主 ServerApp
        self.serverapp.log.info(f"Running on port {self.serverapp.port}")
        # 访问其他扩展
        lab = self.serverapp.extension_manager.extensions.get("jupyterlab")
```

## 前端扩展点（Lab Extensions）

服务端扩展可以提供前端扩展包：

1. 编译前端扩展为 npm 包
2. 将编译产物放到 `static/` 目录
3. 通过 `page_config` 注册前端入口点

```python
def initialize_settings(self):
    self.settings["page_config_data"]["frontend_extensions"] = {
        "my-frontend-extension": {"import": "/static/myext/static/index.js"}
    }
```

## 编写扩展的最佳实践

1. **使用命名空间前缀**：所有 Handler 路径以 `/<ext_name>/` 开头
2. **提供静态资源**：前端编译产物放在 `static/` 目录
3. **定义配置项**：可配置的行为使用 traitlets
4. **异步 Handler**：使用 `async def` 定义 Handler 方法
5. **使用 baseHandler**：自定义 Handler 继承 `APIHandler` 或 `JupyterHandler`
6. **文档化 API**：扩展 API 提供 OpenAPI 文档
7. **错误处理**：使用 `web.HTTPError` 返回标准错误
8. **日志**：使用 `self.log` 记录日志

## 相关概念

- [快速上手](01-getting-started.md) — 安装和启动扩展
- [Handler 继承体系](04-handler-hierarchy.md) — 编写自定义 Handler
- [配置管理](06-config-management.md) — 扩展配置方式
