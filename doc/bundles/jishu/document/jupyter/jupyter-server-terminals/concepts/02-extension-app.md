---
type: Concept
title: TerminalsExtensionApp 扩展应用
description: TerminalsExtensionApp 类详解——Jupyter Server 扩展生命周期、初始化流程、设置与 Handler 注册、清理逻辑
tags: [jupyter, terminals, extension-app, lifecycle, ExtensionApp]
generated: { by: "reference_agent/trae-glm", at: "2026-08-22T06:47:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T07:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: jst-source
    resource: /references/jupyter-server-terminals-source.md
---

# TerminalsExtensionApp 扩展应用

## 类定义与继承

`TerminalsExtensionApp` 是 jupyter_server_terminals 的核心入口类，定义在 app.py 中：

```python
from jupyter_server.extension.application import ExtensionApp
from traitlets import Type
from .terminalmanager import TerminalManager

class TerminalsExtensionApp(ExtensionApp):
    """A terminals extension app."""
    name = "jupyter_server_terminals"
```

它继承自 Jupyter Server 的 `ExtensionApp` 基类，遵循 Jupyter Server 扩展应用（Extension Application）的标准生命周期协议。

## 扩展点注册

包的 `__init__.py` 通过 `_jupyter_server_extension_points()` 函数向 Jupyter Server 注册此扩展：

```python
def _jupyter_server_extension_points() -> List[Dict[str, Any]]:
    return [
        {
            "module": "jupyter_server_terminals.app",
            "app": TerminalsExtensionApp,
        },
    ]
```

Jupyter Server 启动时会发现这个入口点，实例化 `TerminalsExtensionApp` 并调用其生命周期方法。同时，`jupyter-config/jupyter_server_terminals.json` 默认启用该扩展：

```json
{
  "ServerApp": {
    "jpserver_extensions": {
      "jupyter_server_terminals": true
    }
  }
}
```

## 可配置项

`TerminalsExtensionApp` 暴露一个可配置 Trait：

```python
terminal_manager_class: type[TerminalManager] = Type(
    default_value=TerminalManager,
    help="The terminal manager class to use."
).tag(config=True)
```

这允许开发者通过配置替换 `TerminalManager` 的子类，实现自定义终端管理行为。

## 生命周期方法

ExtensionApp 生命周期主要包括三个阶段：设置初始化 → Handler 注册 → 清理关闭。

### initialize_settings()

```python
def initialize_settings(self) -> None:
    """Initialize settings."""
    if not self.serverapp or not self.serverapp.terminals_enabled:
        self.settings.update({"terminals_available": False})
        return
    self.initialize_configurables()
    self.settings.update(
        {"terminals_available": True, "terminal_manager": self.terminal_manager}
    )
```

该方法执行以下逻辑：

1. **门控检查**：如果 `serverapp` 不存在或 `terminals_enabled = False`，直接标记 `terminals_available = False` 并返回
2. **初始化配置组件**：调用 `initialize_configurables()` 创建 TerminalManager
3. **注册设置**：将 `terminals_available = True` 和 `terminal_manager` 实例注册到 settings 字典

注意：`terminals_available = False` 是类属性默认值，只有在初始化成功后才设为 `True`。这个"最终指示"变量比 web settings 中的同名变量更可靠——如果 terminado 初始化失败，它保持 `False`。

### initialize_configurables()

```python
def initialize_configurables(self) -> None:
    """Initialize configurables."""
```

该方法负责创建 TerminalManager 实例，是 Shell 配置的核心逻辑：

1. **确定默认 Shell**：
   - Windows：`"powershell.exe"`
   - 非 Windows：通过 `shutil.which("sh")` 查找 sh
2. **处理 Shell 覆盖**：从 `serverapp.terminado_settings["shell_command"]` 获取自定义 Shell 命令
   - 如果是字符串，用 `shlex.split()` 分词
3. **确定最终 Shell**：有覆盖则用覆盖值，否则使用 `[$SHELL 或 default_shell]`
4. **Login Shell 处理**：非 Windows、无自定义 Shell、且 stdout 非 TTY 时（如 JupyterHub 派生环境），追加 `"-l"` 参数启用 login shell（自动 source `/etc/profile` 等）
5. **创建 TerminalManager**：传入 `shell_command`、`extra_env`（包含 `JUPYTER_SERVER_ROOT` 和 `JUPYTER_SERVER_URL`）和 `parent=serverapp`
6. **设置日志**：`self.terminal_manager.log = self.serverapp.log`

### initialize_handlers()

```python
def initialize_handlers(self) -> None:
    """Initialize handlers."""
```

该方法注册 URL 路由：

1. **提前返回条件**：`serverapp` 不存在，或 `terminals_enabled = False`（后者仍需同步 settings 到 web_app 以兼容 nbclassic）
2. **注册 WebSocket Handler**：
   ```python
   self.handlers.append((
       r"/terminals/websocket/(\w+)",
       handlers.TermSocket,
       {"term_manager": self.terminal_manager},
   ))
   ```
3. **注册 REST API Handlers**：`self.handlers.extend(api_handlers.default_handlers)`
4. **同步到 web_app settings**：设置 `terminal_manager` 和 `terminals_available`

### current_activity()

```python
def current_activity(self) -> dict[str, t.Any] | None:
```

返回当前活动终端的信息（如果有），用于 Jupyter Server 的活动追踪。如果 `terminals_available` 为 `True` 且存在终端，返回终端字典；否则返回 `None`。

### cleanup_terminals()

```python
async def cleanup_terminals(self) -> None:
```

异步关闭所有终端：
- 检查 `terminals_available`，不可用则直接返回
- 记录待关闭终端数量的日志（支持单复数国际化）
- 调用 `terminal_manager.terminate_all()` 关闭所有终端进程

### stop_extension()

```python
async def stop_extension(self) -> None:
```

扩展停止时的清理入口，委托给 `cleanup_terminals()`。

## 初始化流程总结

```
Jupyter Server 启动
    │
    ├─ 发现 _jupyter_server_extension_points()
    ├─ 实例化 TerminalsExtensionApp
    │
    ├─ initialize_settings()
    │   ├─ terminals_enabled? ──No──> terminals_available=False, return
    │   └─ Yes
    │       └─ initialize_configurables()
    │           ├─ 确定 shell_command（平台默认 / 自定义 / login shell）
    │           └─ 创建 TerminalManager 实例
    │       └─ settings: terminals_available=True, terminal_manager=...
    │
    ├─ initialize_handlers()
    │   ├─ 注册 /terminals/websocket/(\w+) → TermSocket
    │   ├─ 注册 /api/terminals → TerminalRootHandler
    │   ├─ 注册 /api/terminals/(\w+) → TerminalHandler
    │   └─ 同步 settings 到 web_app
    │
    └─ （运行中... 处理请求）
        │
        └─ stop_extension()
            └─ cleanup_terminals() → terminate_all()
```

## 环境变量传递

TerminalManager 创建时传入两个环境变量给终端进程：

| 环境变量 | 值来源 | 说明 |
|---------|--------|------|
| `JUPYTER_SERVER_ROOT` | `serverapp.root_dir` | Jupyter Server 的根目录（notebook 目录） |
| `JUPYTER_SERVER_URL` | `serverapp.connection_url` | Jupyter Server 的连接 URL（含 token） |

终端进程中可以通过这些环境变量知道 Jupyter Server 的位置和根目录。

## 相关概念

- [5分钟快速上手](01-getting-started.md)
- [TerminalManager 终端管理器](03-terminal-manager.md)
- [REST API 处理器](04-rest-api.md)
- [WebSocket 处理器](05-websocket.md)
- [Shell 配置与平台差异](06-shell-configuration.md)
- [jupyter_server_terminals 源码信源登记](../references/jupyter-server-terminals-source.md)

[^jst-source]: jupyter_server_terminals 源码信源，见 [jupyter-server-terminals-source.md](../references/jupyter-server-terminals-source.md)。
