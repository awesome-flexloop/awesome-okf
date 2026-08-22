---
okf_version: "0.2"
type: reference
title: "主应用源码（app.py）"
description: "jupyterlab_server/app.py 中 LabServerApp 主应用类的完整 API：继承体系、配置 traitlets、初始化流程与弃用别名处理"
tags: [app, labserverapp, extensionapp, traitlets, configuration, lifecycle]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:30:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T12:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: app-py
    resource: "../../../../../external/libs/jupyter/jupyterlab_server/jupyterlab_server/app.py"
    title: "jupyterlab_server/app.py"
---

# 主应用源码（app.py）

本信源登记 `jupyterlab_server/app.py`（约145行）的核心类、方法和配置项。app.py 定义了 jupyterlab_server 的主入口类 `LabServerApp`，它作为 Jupyter Server 的 ExtensionApp 插件运行。

## LabServerApp 类

```python
class LabServerApp(ExtensionAppJinjaMixin, LabConfig, ExtensionApp):
```

### 类属性

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `name` | str | `"jupyterlab_server"` | 应用名称，用于Jupyter Server扩展注册 |
| `extension_url` | str | `"/lab"` | 扩展挂载的URL路径 |
| `app_name` | str | `"JupyterLab Server Application"` | 人类可读的应用名称 |
| `file_url_prefix` | str | `"/lab/tree"` | 文件树的URL前缀 |
| `default_url` | Unicode | `"/lab"` | 根路径重定向的默认URL |
| `load_other_extensions` | bool | `True` | 是否加载其他服务器扩展 |
| `app_version` | Unicode | `__version__` | 应用版本号 |

### 配置 Traitlets

| Trait | 类型 | 默认值 | 说明 |
|-------|------|--------|------|
| `blacklist_uris` | Unicode | `""` | **已弃用**（v1.2），使用 `blocked_extensions_uris` |
| `blocked_extensions_uris` | Unicode | `""` | 逗号分隔的屏蔽扩展列表URI |
| `whitelist_uris` | Unicode | `""` | **已弃用**（v1.2），使用 `allowed_extensions_uris` |
| `allowed_extensions_uris` | Unicode | `""` | 逗号分隔的允许扩展列表URI |
| `listings_refresh_seconds` | Integer | `3600` | 扩展列表刷新间隔（秒） |
| `listings_request_options` | Dict | `{}` | 传递给 requests 库的HTTP请求选项 |

### 属性

#### app_namespace

```python
@property
def app_namespace(self) -> str:
    return self.name
```

返回应用命名空间，即 `self.name`（`"jupyterlab_server"`）。重写了 ExtensionApp 的同名属性。

### 方法

#### initialize_settings()

```python
def initialize_settings(self) -> None:
```

初始化应用设置：

1. 获取或创建 `static_immutable_cache` 集合
2. 将 `static_url_prefix` 添加到不可变缓存（前端静态文件名带hash，可长期缓存）
3. 遍历 `labextensions_path` 和 `extra_labextensions_path`，将所有扩展的 `**/static` 目录URL加入不可变缓存
4. 如果存在 serverapp，获取 kernel_manager 的 `untracked_message_types`，注入到 `page_config_data`

#### initialize_templates()

```python
def initialize_templates(self) -> None:
```

初始化模板路径：
- `self.static_paths = [self.static_dir]`
- `self.template_paths = [self.templates_dir]`

#### initialize_handlers()

```python
def initialize_handlers(self) -> None:
```

初始化路由处理器，直接调用 `add_handlers(self.handlers, self)`。

#### _deprecated_trait(change)

```python
@observe(*list(_deprecated_aliases))
def _deprecated_trait(self, change: Any) -> None:
```

弃用别名观察器（来自JupyterHub的模式）：
- 监听 `blacklist_uris` 和 `whitelist_uris` 的变化
- 当设置了弃用名称时，发出warning并将值转发到新名称
- 仅当新旧值不同时才warning，避免配置中同时设置两个名称导致重复警告

### 弃用别名映射

```python
_deprecated_aliases = {
    "blacklist_uris": ("blocked_extensions_uris", "1.2"),
    "whitelist_uris": ("allowed_extensions_uris", "1.2"),
}
```

### 模块级导出

```python
main = launch_new_instance = LabServerApp.launch_instance
```

提供 `main()` 和 `launch_new_instance()` 两个便捷入口，均指向 `LabServerApp.launch_instance()` 类方法。

[F-200]
