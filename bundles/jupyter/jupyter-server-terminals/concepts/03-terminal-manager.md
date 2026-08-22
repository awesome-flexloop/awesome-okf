---
type: Concept
title: TerminalManager 终端管理器
description: TerminalManager 类详解——终端 CRUD 操作、REST 模型、闲置终端自动清理（Culler）、Prometheus 指标、活动追踪
tags: [jupyter, terminals, TerminalManager, culler, NamedTermManager, prometheus]
generated: { by: "reference_agent/trae-glm", at: "2026-08-22T06:47:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T07:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: jst-source
    resource: /references/jupyter-server-terminals-source.md
---

# TerminalManager 终端管理器

## 类定义与继承

`TerminalManager` 定义在 [terminalmanager.py](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_terminals/jupyter_server_terminals/terminalmanager.py) 中，是终端管理的核心类：

```python
from terminado.management import NamedTermManager, PtyWithClients
from traitlets import Integer
from traitlets.config import LoggingConfigurable

class TerminalManager(LoggingConfigurable, NamedTermManager):
    """A MultiTerminalManager for use in the notebook webserver"""
```

它使用**多继承**组合了两个父类的能力：
- `LoggingConfigurable`：提供 Traitlets 配置系统和日志能力
- `NamedTermManager`（来自 terminado）：提供底层命名终端管理（PTY 创建、进程管理等）

## 可配置项

TerminalManager 暴露两个配置 Trait：

```python
cull_inactive_timeout = Integer(
    0,
    config=True,
    help="Timeout (in seconds) in which a terminal has been inactive and ready to be culled."
)

cull_interval = Integer(
    300,  # 5 minutes default
    config=True,
    help="The interval (in seconds) on which to check for terminals exceeding the inactive timeout value."
)
```

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `cull_inactive_timeout` | 0 | 闲置超时秒数，0 或负值表示禁用自动清理 |
| `cull_interval` | 300 | 检查间隔秒数（默认 5 分钟） |

## 终端 CRUD 操作

TerminalManager 在 terminado 的 `NamedTermManager` 基础上，增加了 REST 友好的 CRUD 方法和 JSON 模型。

### create(**kwargs) → MODEL

```python
def create(self, **kwargs: t.Any) -> MODEL:
    """Create a new terminal."""
```

创建新终端：
1. 调用 `self.new_named_terminal(**kwargs)` 创建命名终端（继承自 terminado）
2. 给终端对象打上 `last_activity = utcnow()` 时间戳（monkey-patch）
3. 调用 `get_terminal_model(name)` 返回 JSON 模型
4. 增加 Prometheus 计数器 `RUNNING_TOTAL.inc()`
5. 确保 culler 已初始化（首次创建时启动）

`kwargs` 透传给 `new_named_terminal`，支持的参数包括 `cwd`（工作目录）等。

### get(name) → MODEL

```python
def get(self, name: str) -> MODEL:
    """Get terminal 'name'."""
    return self.get_terminal_model(name)
```

返回指定名称终端的 JSON 模型。

### list() → list[MODEL]

```python
def list(self) -> list[MODEL]:
    """Get a list of all running terminals."""
```

返回所有运行中终端的模型列表，同时更新 Prometheus 指标为当前终端数。

### async terminate(name, force=False) → None

```python
async def terminate(self, name: str, force: bool = False) -> None:
    """Terminate terminal 'name'."""
```

异步终止指定终端：
1. 调用 `_check_terminal(name)` 验证终端存在（不存在抛 404）
2. 调用父类 `terminate(name, force=force)` 终止进程
3. 减少 Prometheus 计数器 `RUNNING_TOTAL.dec()`

### async terminate_all() → None

```python
async def terminate_all(self) -> None:
    """Terminate all terminals."""
```

遍历所有终端，逐个调用 `terminate(name, force=True)` 强制关闭。

## REST 数据模型

### get_terminal_model(name) → MODEL

```python
def get_terminal_model(self, name: str) -> MODEL:
    """Return a JSON-safe dict representing a terminal."""
```

返回标准化的 JSON 安全字典：

```python
{
    "name": name,
    "last_activity": isoformat(term.last_activity),
}
```

- `name`：终端名称（字符串，如 `"1"`, `"2"` 等）
- `last_activity`：ISO 8601 格式的 UTC 时间戳（如 `"2026-08-22T06:00:00.000000Z"`）

这也是 REST API 返回的 Terminal 对象格式。

### _check_terminal(name) → None

```python
def _check_terminal(self, name: str) -> None:
    """Check a that terminal 'name' exists and raise 404 if not."""
    if name not in self.terminals:
        raise web.HTTPError(404, "Terminal not found: %s" % name)
```

内部检查方法，终端不存在时抛出 Tornado HTTP 404 错误。`self.terminals` 是 terminado 的 NamedTermManager 维护的终端字典（name → PtyWithClients 映射）。

## 闲置终端自动清理（Culler）

TerminalManager 内置了自动清理机制，可以在终端闲置一段时间后自动关闭，释放系统资源。

### 初始化 Culler

```python
def _initialize_culler(self) -> None:
```

该方法在首次创建终端时被调用（由 `create()` 触发）：
1. 检查 `_initialized_culler` 标志，防止重复初始化
2. 如果 `cull_inactive_timeout > 0`，创建 Tornado `PeriodicCallback`
3. 如果 `cull_interval <= 0`（无效值），重置为默认 300 秒并记录警告
4. 启动周期性回调，每 `cull_interval` 秒调用 `_cull_terminals()`
5. 设置 `_initialized_culler = True`

### 轮询检查

```python
async def _cull_terminals(self) -> None:
```

周期性检查方法：
1. 遍历终端列表的**副本**（`list(self.terminals)`，避免迭代时修改导致冲突）
2. 对每个终端调用 `_cull_inactive_terminal(name)`
3. 异常被捕获并记录日志（不影响其他终端的检查）

### 单终端清理判定

```python
async def _cull_inactive_terminal(self, name: str) -> None:
```

判定并清理单个闲置终端：
1. 尝试获取终端对象，如果已被终止（KeyError）则直接返回
2. 检查终端是否有 `last_activity` 属性
3. 计算闲置时长：`dt_inactive = utcnow() - term.last_activity`
4. 如果 `dt_inactive > timedelta(seconds=cull_inactive_timeout)`，调用 `terminate(name, force=True)` 强制关闭
5. 记录警告日志说明被 cull 的终端名称和闲置秒数

### 活动时间戳更新时机

终端的 `last_activity` 在两个时机被更新：

1. **WebSocket 消息收发时**：`TermSocket._update_activity()` 更新
2. **PTY 数据读取时**：`pre_pty_read_hook()` 钩子在每次从 PTY 读取数据前更新

```python
def pre_pty_read_hook(self, ptywclients: PtyWithClients) -> None:
    """The pre-pty read hook."""
    ptywclients.last_activity = utcnow()
```

这个双层更新机制确保无论是用户输入（WebSocket 消息）还是程序输出（PTY 读取），都会刷新活动时间。

## Prometheus 指标

```python
RUNNING_TOTAL = metrics.TERMINAL_CURRENTLY_RUNNING_TOTAL
```

TerminalManager 使用 Jupyter Server 的 Prometheus 指标系统，通过 `RUNNING_TOTAL` 暴露当前运行终端数：
- `create()`：`RUNNING_TOTAL.inc()`（+1）
- `terminate()`：`RUNNING_TOTAL.dec()`（-1）
- `list()`：`RUNNING_TOTAL.set(len(models))`（校准为实际值）

## Culler 配置示例

```python
# jupyter_server_config.py
c.TerminalManager.cull_inactive_timeout = 600   # 10分钟无活动则清理
c.TerminalManager.cull_interval = 120           # 每2分钟检查一次
```

禁用 culling（默认）：

```python
c.TerminalManager.cull_inactive_timeout = 0
```

## 终端命名

终端名称由 terminado 的 `NamedTermManager` 自动分配，采用从 `"1"` 开始的递增数字字符串。第一个终端名为 `"1"`，第二个为 `"2"`，以此类推。删除后名称不会立即复用。

## 相关概念

- [TerminalsExtensionApp 扩展应用](/concepts/02-extension-app.md)
- [REST API 处理器](/concepts/04-rest-api.md)
- [WebSocket 处理器](/concepts/05-websocket.md)
- [基础终端操作示例](/examples/basic-operations.md)
- [配置自动清理与指定工作目录示例](/examples/culler-and-cwd.md)
- [jupyter_server_terminals 源码信源登记](/references/jupyter-server-terminals-source.md)

[^jst-source]: jupyter_server_terminals 源码信源，见 [jupyter-server-terminals-source.md](/references/jupyter-server-terminals-source.md)。
