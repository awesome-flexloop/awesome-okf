---
title: 后端应用类
type: concept
bundle: jupyter-notebook
chapter: "02"
difficulty: intermediate
tags: ["backend", "app", "traitlets", "configuration"]
prerequisites: ["01-architecture-overview"]
sources: ["F-010", "F-011", "F-012", "F-013", "F-015", "F-016", "F-017", "F-018", "F-027", "F-028", "F-029"]
next: ["04-handlers", "05-shim-layer"]
---

# 02 | 后端应用类：JupyterNotebookApp

`JupyterNotebookApp` 是Notebook后端的入口类，负责服务器启动、路由注册、配置管理和模板渲染。

## 类定义与继承

```python
class JupyterNotebookApp(NotebookConfigShimMixin, LabServerApp):
    """The notebook server extension app."""
    name = "notebook"
    app_name = "Jupyter Notebook"
    description = "Jupyter Notebook - A web-based notebook environment for interactive computing"
    version = version
```

> **信源**: [app.py:L242-248](../references/00-source-registry.md#S-004)（F-010, F-011）

### MRO（方法解析顺序）

```
JupyterNotebookApp
├── NotebookConfigShimMixin (notebook_shim.shim)  ← v6配置兼容
└── LabServerApp (jupyterlab_server)               ← JupyterLab后端基座
    └── ExtensionApp (jupyter_server)              ← Jupyter Server扩展基类
        └── JupyterApp (jupyter_core)              ← Jupyter应用基类
            └── Application (traitlets.config)     ← traitlets配置应用
```

## 类属性与配置项

### 标识属性

| 属性 | 值 | 说明 |
|------|-----|------|
| `name` | `"notebook"` | 扩展名称，用于URL路径和配置节名 |
| `app_name` | `"Jupyter Notebook"` | 应用显示名称 |
| `version` | `__version__` | 版本号（v7.7.0a1） |
| `extension_url` | `"/"` | 扩展根URL（F-012） |
| `default_url` | `"/tree"` | 默认跳转URL（F-012） |
| `file_url_prefix` | `"/tree"` | 文件URL前缀（F-013） |
| `load_other_extensions` | `True` | 是否加载其他Jupyter Server扩展（F-013） |

### 可配置traitlets

```python
expose_app_in_browser = Bool(
    False,
    config=True,
    help="Whether to expose the global app instance to browser via window.jupyterapp",
)

custom_css = Bool(
    True,
    config=True,
    help="Whether custom CSS is loaded on the page.",
)
```

> **信源**: [app.py:L257-269](../references/00-source-registry.md#S-004)（F-015, F-016）

| Traitlet | 类型 | 默认值 | 说明 |
|----------|------|--------|------|
| `expose_app_in_browser` | Bool | `False` | 是否在浏览器暴露 `window.jupyterapp` |
| `custom_css` | Bool | `True` | 是否加载自定义CSS |
| `default_url` | Unicode | `"/tree"` | 默认URL |

### CLI Flags

```python
flags["expose-app-in-browser"] = (
    {"JupyterNotebookApp": {"expose_app_in_browser": True}},
    "Expose the global app instance to browser via window.jupyterapp.",
)

flags["custom-css"] = (
    {"JupyterNotebookApp": {"custom_css": True}},
    "Load custom CSS in template html files. Default is True",
)
```

> **信源**: [app.py:L271-280](../references/00-source-registry.md#S-004)（F-017）

使用方式：
```bash
jupyter notebook --expose-app-in-browser
jupyter notebook --custom-css
```

### 默认目录配置

使用 `@default` 装饰器定义默认路径：

```python
@default("static_dir")
def _default_static_dir(self) -> str:
    return str(HERE / "static")

@default("templates_dir")
def _default_templates_dir(self) -> str:
    return str(HERE / "templates")

@default("app_settings_dir")
def _default_app_settings_dir(self) -> str:
    return str(app_dir / "settings")

@default("schemas_dir")
def _default_schemas_dir(self) -> str:
    return str(app_dir / "schemas")

@default("themes_dir")
def _default_themes_dir(self) -> str:
    return str(app_dir / "themes")

@default("user_settings_dir")
def _default_user_settings_dir(self) -> str:
    return t.cast(str, get_user_settings_dir())

@default("workspaces_dir")
def _default_workspaces_dir(self) -> str:
    return t.cast(str, get_workspaces_dir())
```

> **信源**: [app.py:L282-308](../references/00-source-registry.md#S-004)（F-018）

| 目录 | 默认路径 | 说明 |
|------|---------|------|
| `static_dir` | `notebook/static/` | 静态文件（JS/CSS/fonts） |
| `templates_dir` | `notebook/templates/` | Jinja2 HTML模板 |
| `app_settings_dir` | `<jupyter_app_dir>/settings/` | 应用设置 |
| `schemas_dir` | `<jupyter_app_dir>/schemas/` | JSON Schema定义 |
| `themes_dir` | `<jupyter_app_dir>/themes/` | 主题文件 |
| `user_settings_dir` | JupyterLab用户设置目录 | 用户自定义设置 |
| `workspaces_dir` | JupyterLab工作区目录 | 工作区布局保存 |

其中 `app_dir` 通过 `get_app_dir()` 从 `jupyterlab.commands` 获取（F-018），这是Notebook复用JupyterLab配置目录的关键。

## 启动流程

### 入口点声明

在 `__init__.py` 中声明Jupyter Server扩展入口：

```python
def _jupyter_server_extension_points() -> list[dict[str, Any]]:
    from .app import JupyterNotebookApp
    return [{"module": "notebook", "app": JupyterNotebookApp}]

def _jupyter_labextension_paths() -> list[dict[str, str]]:
    return [{"src": "labextension", "dest": "@jupyter-notebook/lab-extension"}]
```

> **信源**: [__init__.py:L12-20](../references/00-source-registry.md#S-003)（F-027, F-028）

- `_jupyter_server_extension_points()`: Jupyter Server发现扩展时调用，返回应用类
- `_jupyter_labextension_paths()`: JupyterLab发现前端扩展时调用，返回静态资源路径

### 启动入口

```python
main = launch_new_instance = JupyterNotebookApp.launch_instance

if __name__ == "__main__":
    main()
```

> **信源**: [app.py:L363-366](../references/00-source-registry.md#S-004)（F-029）

`launch_instance` 是traitlets `Application` 类提供的类方法，负责：
1. 解析命令行参数
2. 加载配置文件
3. 调用 `initialize()` 初始化
4. 调用 `start()` 启动服务器
5. 进入事件循环

### initialize() 方法

```python
def initialize(self, argv: list[str] | None = None) -> None:
    """Subclass because the ExtensionApp.initialize() method does not take arguments"""
    super().initialize()
```

> **信源**: [app.py:L358-360](../references/00-source-registry.md#S-004)

这个方法重写了父类方法，因为 `ExtensionApp.initialize()` 不接受 `argv` 参数，实际初始化逻辑由父类链完成。

### 初始化Handler

`initialize_handlers()` 是路由注册的核心方法：

```python
def initialize_handlers(self) -> None:
    """Initialize handlers."""
    assert self.serverapp is not None
    page_config = self.serverapp.web_app.settings.setdefault("page_config_data", {})
    nbclassic_enabled = self.server_extension_is_enabled("nbclassic")
    page_config["nbclassic_enabled"] = nbclassic_enabled

    # JupyterHub集成...
    if "hub_prefix" in self.serverapp.tornado_settings:
        # 设置hubPrefix, hubHost, hubUser, shareUrl
        page_config["token"] = ""  # 安全：不暴露API token

    self.handlers.append(("/tree(.*)", TreeHandler))
    self.handlers.append(("/notebooks(.*)", NotebookHandler))
    self.handlers.append(("/edit(.*)", FileHandler))
    self.handlers.append(("/consoles/(.*)", ConsoleHandler))
    self.handlers.append(("/terminals/(.*)", TerminalHandler))
    self.handlers.append(("/custom/custom.css", CustomCssHandler))
    super().initialize_handlers()
```

> **信源**: [app.py:L326-356](../references/00-source-registry.md#S-004)（F-021, F-026）

主要工作：
1. 检测nbclassic扩展是否启用，写入page_config
2. 处理JupyterHub环境变量（如果在Hub下运行）
3. 注册6个页面路由Handler
4. 调用父类 `initialize_handlers()` 注册JupyterLab的路由

## 模板准备

```python
def _prepare_templates(self) -> None:
    super(LabServerApp, self)._prepare_templates()
    self.jinja2_env.globals.update(custom_css=self.custom_css)
```

> **信源**: [app.py:L310-312](../references/00-source-registry.md#S-004)

注意这里调用的是 `super(LabServerApp, self)._prepare_templates()`，**跳过了LabServerApp的模板准备**，直接使用ExtensionApp的模板环境，并注入 `custom_css` 全局变量供Jinja2模板使用。

## 扩展状态检查

```python
def server_extension_is_enabled(self, extension: str) -> bool:
    """Check if server extension is enabled."""
    if self.serverapp is None:
        return False
    try:
        extension_enabled = (
            self.serverapp.extension_manager.extensions[extension].enabled is True
        )
    except (AttributeError, KeyError, TypeError):
        extension_enabled = False
    return extension_enabled
```

> **信源**: [app.py:L314-324](../references/00-source-registry.md#S-004)

这个工具方法用于检查其他Jupyter Server扩展是否启用，当前用于检测nbclassic（Notebook Classic兼容层）是否安装。

## 配置系统

Jupyter Notebook使用traitlets配置系统，配置优先级从高到低：

1. **命令行参数**: `jupyter notebook --port=9999`
2. **用户配置**: `~/.jupyter/jupyter_notebook_config.py`
3. **环境变量**: `JUPYTER_PORT=9999`
4. **默认值**: 代码中定义的默认值

### v7中的配置迁移

在Notebook 6.x中，常用配置写在 `c.NotebookApp.*` 下：
```python
# v6 配置（v7中通过shim层兼容）
c.NotebookApp.port = 8888
c.NotebookApp.notebook_dir = "/home/user/notebooks"
c.NotebookApp.open_browser = True
```

在Notebook 7.x中，这些配置迁移到了 `c.ServerApp.*` 或 `c.LabServerApp.*`：
```python
# v7 原生配置
c.ServerApp.port = 8888
c.ServerApp.root_dir = "/home/user/notebooks"
c.LabServerApp.open_browser = True
```

`NotebookConfigShimMixin` 自动将旧配置名映射到新配置名，但新项目建议直接使用新配置名。

## 启动方式汇总

| 方式 | 命令 |
|------|------|
| 命令行启动 | `jupyter notebook` |
| 模块启动 | `python -m notebook` |
| Python API | `JupyterNotebookApp.launch_instance()` |
| Jupyter Server | `jupyter server --ServerApp.jpserver_extensions="{'notebook': True}"` |

## 下一步

- → [请求处理器体系](04-handlers.md) 理解NotebookBaseHandler和页面路由的详细实现
- → [配置兼容层](05-shim-layer.md) 理解notebook_shim如何桥接v6配置
