---
type: Reference
title: "extension/ 扩展系统源码信源"
description: "ExtensionApp 基类、ExtensionManager 加载机制、ExtensionPoint 连接点与扩展配置管理"
tags: [extensions, plugins, extension-app, extension-manager, server-extension]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:40:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: application-py
    resource: ../../../../../../external/libs/jupyter/jupyter_server/jupyter_server/extension/application.py
    title: jupyter_server/extension/application.py
  - id: manager-py
    resource: ../../../../../../external/libs/jupyter/jupyter_server/jupyter_server/extension/manager.py
    title: jupyter_server/extension/manager.py
  - id: config-py
    resource: ../../../../../../external/libs/jupyter/jupyter_server/jupyter_server/extension/config.py
    title: jupyter_server/extension/config.py
  - id: handler-py
    resource: ../../../../../../external/libs/jupyter/jupyter_server/jupyter_server/extension/handler.py
    title: jupyter_server/extension/handler.py
  - id: serverextension-py
    resource: ../../../../../../external/libs/jupyter/jupyter_server/jupyter_server/extension/serverextension.py
    title: jupyter_server/extension/serverextension.py
  - id: utils-py
    resource: ../../../../../../external/libs/jupyter/jupyter_server/jupyter_server/extension/utils.py
    title: jupyter_server/extension/utils.py
---

# extension/ 扩展系统源码信源

## 模块结构

```
extension/
├── __init__.py
├── application.py     # ExtensionApp 基类
├── config.py          # ExtensionConfigManager 扩展配置
├── handler.py         # ExtensionHandlerMixin/ExtensionHandlerJinjaMixin
├── manager.py         # ExtensionManager/ExtensionPackage/ExtensionPoint
├── serverextension.py # jupyter server extension CLI 命令
└── utils.py           # 扩展加载工具与异常类
```

## ExtensionApp (application.py L126)

服务器扩展应用基类，继承 JupyterApp。扩展可通过两种方式初始化：
1. 作为 jpserver_extension 配置项被 ServerApp 加载
2. 通过 `launch_instance()` 直接启动（此时自动创建内嵌 ServerApp）

**核心类属性/配置项**：
| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `load_other_extensions` | Bool | True | 直接启动时是否加载其他扩展 |
| `serverapp_config` | dict | {} | 内嵌 ServerApp 配置 |
| `name` | Unicode | 模块名 | 扩展名称 |
| `default_url` | Unicode | '' | 默认 URL |
| `handlers` | List | [] | 扩展 Handlers 列表 |
| `static_paths` | List | [] | 静态文件路径 |
| `template_paths` | List | [] | Jinja2 模板路径 |
| `settings` | Dict | {} | Tornado 设置 |
| `jinja2_options` | Dict | {} | Jinja2 环境选项 |

**核心方法**：
| 方法 | 说明 |
|------|------|
| `initialize_settings()` | 初始化扩展 settings |
| `initialize_handlers()` | 初始化 URL Handlers |
| `initialize_templates()` | 初始化 Jinja2 模板 |
| `_link_jupyter_server_extension(serverapp)` | 链接到 ServerApp（内部） |
| `_start_jupyter_server_extension(serverapp)` | 启动扩展（内部） |
| `load_jupyter_server_extension(serverapp)` | 经典加载入口（classmethod） |
| `launch_instance(argv)` | 直接启动扩展（自动创建 ServerApp） |
| `static_url(path)` | 静态文件 URL |

## ExtensionAppJinjaMixin (application.py L82)

为 ExtensionApp 提供 Jinja2 模板支持的 Mixin：
- `_prepare_templates()`: 创建 Jinja2 Environment，注册到 Tornado settings

## ExtensionManager (manager.py L277)

管理所有服务器扩展的加载与生命周期。

**核心配置项**：
- `enabled`: Bool，True。是否启用扩展系统

**核心方法**：
| 方法 | 说明 |
|------|------|
| `load_extensions(extension_apps)` | 批量加载扩展 |
| `link_extension(extapp)` | 链接扩展到 ServerApp |
| `start_extension(extapp)` | 启动扩展 |
| `stop_extension(extapp)` | 停止扩展 |
| `stop_extensions()` | 停止所有扩展 |
| `list_extensions()` | 列出已加载扩展 |
| `extension_points(name)` | 获取扩展的 ExtensionPoint 列表 |

## ExtensionPackage (manager.py L186)

表示一个已安装的扩展 Python 包。

- `metadata`: 从 pyproject.toml 或 `_jupyter_server_extension_points()` 获取元数据
- `name`: 包名
- `version`: 版本
- `extension_points`: ExtensionPoint 列表
- `enabled`: 是否启用

## ExtensionPoint (manager.py L18)

扩展连接点，表示一个可被 ServerApp 加载的扩展模块。

**核心属性**：
- `metadata`: Dict，包含 module 路径、app 类等
- `module_name`: str，Python 模块路径
- `module`: 已导入的模块
- `name`: str，扩展名称
- `app`: ExtensionApp 实例（如果 metadata 包含 app 字段）
- `linked`: bool，是否已链接到 ServerApp

**核心方法**：
- `validate()`: 验证 linker 和 loader 存在
- `link(serverapp)`: 链接到 ServerApp
- `start(serverapp)`: 启动扩展
- `stop(serverapp)`: 停止扩展

## ExtensionConfigManager (config.py L8)

管理扩展的启用/禁用配置，继承 ConfigManager。

配置存储在 JSON 文件中，支持：
- 启用/禁用扩展
- 列出扩展配置
- 读取 `jupyter_server_config.d/*.json` 片段配置

## ExtensionHandlerMixin (handler.py L36)

为扩展 Handler 提供便捷访问扩展属性的 Mixin：
- `name`: 扩展名称
- `extensionapp`: 扩展应用实例
- `base_url`: 扩展 base URL
- `static_url()`: 扩展静态文件 URL
- `render_template()`: 渲染扩展模板

## ExtensionHandlerJinjaMixin (handler.py L21)

扩展 Handler 的 Jinja2 模板支持 Mixin。

## ServerExtension CLI (serverextension.py)

`jupyter server extension` 子命令：
- `enable`: 启用扩展
- `disable`: 禁用扩展
- `list`: 列出扩展
- `ServerExtensionApp`: 子命令入口

## 扩展发现机制

扩展通过 Python entry points 或 `_jupyter_server_extension_points()` 函数被发现：
```python
def _jupyter_server_extension_points():
    return [{"module": "my_extension", "app": MyExtensionApp}]
```

## 异常类 (utils.py)

- `ExtensionLoadingError`: 扩展加载错误
- `ExtensionMetadataError`: 扩展元数据错误
- `ExtensionModuleNotFound`: 扩展模块未找到
- `NotAnExtensionApp`: 不是有效扩展应用
