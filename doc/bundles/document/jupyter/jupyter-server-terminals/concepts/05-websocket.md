---
type: Concept
title: WebSocket 处理器
description: TermSocket 详解——终端 WebSocket 通信、认证授权流程、消息协议格式、活动时间戳追踪、origin 检查绕过
tags: [jupyter, terminals, websocket, TermSocket, terminado, realtime]
generated: { by: "reference_agent/trae-glm", at: "2026-08-22T06:47:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T07:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: jst-source
    resource: /references/jupyter-server-terminals-source.md
---

# WebSocket 处理器

## TermSocket 类

终端的实时 I/O 通信通过 WebSocket 实现，处理器 `TermSocket` 定义在 handlers.py 中：

```python
from terminado.websocket import TermSocket as BaseTermSocket

class TermSocket(TerminalsMixin, WebSocketMixin, JupyterHandler, BaseTermSocket):
    """A terminal websocket."""
    auth_resource = "terminals"
```

TermSocket 使用**多继承**组合了四个父类：

| 父类 | 来源 | 作用 |
|------|------|------|
| `TerminalsMixin` | jupyter_server_terminals.base | 提供 `terminal_manager` 属性访问 |
| `WebSocketMixin` | jupyter_server.base.websocket | Jupyter Server 的 WebSocket 支持 |
| `JupyterHandler` | jupyter_server.base.handlers | Jupyter Server 基础 Handler（认证、设置等） |
| `BaseTermSocket` | terminado.websocket | terminado 的终端 WebSocket 核心实现 |

## WebSocket 路由

```python
# app.py initialize_handlers()
self.handlers.append((
    r"/terminals/websocket/(\w+)",
    handlers.TermSocket,
    {"term_manager": self.terminal_manager},
))
```

WebSocket 端点为 `/terminals/websocket/{name}`，其中 `{name}` 是通过 REST API 创建终端后获得的终端名称（如 `"1"`）。

**重要**：WebSocket 端点本身不创建终端——必须先通过 `POST /api/terminals` 创建终端获得 name，然后才能用该 name 连接 WebSocket。如果 name 对应的终端不存在，WebSocket 连接会返回 404。

## 初始化方法

```python
def initialize(self, name: str, term_manager: NamedTermManager, **kwargs: t.Any) -> None:
    """Initialize the socket."""
    BaseTermSocket.initialize(self, term_manager, **kwargs)
    TerminalsMixin.initialize(self, name)
```

初始化时接收路由传入的 `term_manager`（即 TerminalManager 实例），分别调用 terminado 基类和 Mixin 的初始化。注意这里参数类型标注为 `NamedTermManager`（terminado 的类型），但实际传入的是其子类 `TerminalManager`。

## Origin 检查处理

```python
def origin_check(self, origin: t.Any = None) -> bool:
    """Terminado adds redundant origin_check.
    Tornado already calls check_origin, so don't do anything here.
    """
    return True
```

terminado 的 `BaseTermSocket` 自带 `origin_check` 方法，但 Tornado 框架本身已经通过 `check_origin` 进行跨域检查。为避免重复/冲突检查，此方法直接返回 `True`，将安全检查委托给 Jupyter Server/Tornado 的标准机制。

## GET 方法（WebSocket 握手）

```python
async def get(self, *args: t.Any, **kwargs: t.Any) -> None:
    """Get the terminal socket."""
```

WebSocket 连接在 HTTP GET 请求中升级，get 方法执行完整的安全检查：

1. **用户认证**：
   ```python
   user = self.current_user
   if not user:
       raise web.HTTPError(403)
   ```

2. **授权检查**：
   ```python
   if self.authorizer is None:
       warn_disabled_authorization()
   elif not await ensure_async(
       self.authorizer.is_authorized(self, user, "execute", self.auth_resource)
   ):
       raise web.HTTPError(403)
   ```
   WebSocket 连接需要 `"execute"` 权限（而非 REST 的 read/write）。如果 authorizer 未配置，记录警告但不拒绝连接。

3. **终端存在性检查**：
   ```python
   if args[0] not in self.term_manager.terminals:
       raise web.HTTPError(404)
   ```

4. **调用父类**：所有检查通过后，调用 `BaseTermSocket.get()` 完成 WebSocket 升级和 PTY 绑定。

## 消息收发与活动追踪

### on_message

```python
async def on_message(self, message: t.Any) -> None:
    """Handle a socket message."""
    await ensure_async(super().on_message(message))
    self._update_activity()
```

收到 WebSocket 消息（用户输入）时，先委托给 terminado 基类处理（写入 PTY），然后更新活动时间戳。

### write_message

```python
def write_message(self, message: t.Any, binary: bool = False) -> None:
    """Write a message to the socket."""
    super().write_message(message, binary=binary)
    self._update_activity()
```

向 WebSocket 发送消息（终端输出）时，先委托给父类发送，然后更新活动时间戳。

### _update_activity

```python
def _update_activity(self) -> None:
    self.application.settings["terminal_last_activity"] = utcnow()
    if self.term_name in self.terminal_manager.terminals:
        self.terminal_manager.terminals[self.term_name].last_activity = utcnow()
```

私有方法更新两个层级的活动时间戳：
1. **全局级**：`application.settings["terminal_last_activity"]`，记录整个服务器最后一次终端活动时间
2. **终端级**：具体终端对象的 `last_activity` 属性，用于 culler 判断闲置

注意：更新终端级时间戳前检查终端是否仍存在（可能在消息处理过程中被删除/cull），避免 KeyError。

## WebSocket 消息协议

WebSocket 使用 JSON 数组格式的消息协议（由 terminado 定义）：

### 客户端→服务端消息（stdin）

```json
["stdin", "ls -la\r\n"]
```

- 第一个元素：消息类型 `"stdin"`
- 第二个元素：发送到终端的输入数据字符串

### 服务端→客户端消息（stdout）

```json
["stdout", "file1.txt  file2.txt\r\n$ "]
```

- 第一个元素：消息类型 `"stdout"`
- 第二个元素：终端输出的字符串数据

### 其他消息类型

terminado 还支持其他消息类型（如 `"set_size"` 设置终端大小），由 BaseTermSocket 处理。

### 命令换行

发送命令时需要追加 `\r\n`（回车换行）来模拟按下 Enter 键执行命令：

```javascript
ws.send(JSON.stringify(['stdin', 'echo hello\r\n']));
```

## 认证资源与动作

WebSocket 连接的授权上下文：

| 属性 | 值 |
|------|-----|
| `auth_resource` | `"terminals"` |
| 所需动作 | `"execute"` |
| 装饰器 | 手动检查（非装饰器方式，因为 WebSocket GET 是异步升级） |

## 连接流程

```
客户端                              服务端
  │                                   │
  │  POST /api/terminals              │── 创建终端，返回 {"name":"1"}
  │◄──────────────────────────────────│
  │                                   │
  │  WS /terminals/websocket/1        │── 升级握手
  │  (HTTP 101 Switching Protocols)   │
  │◄──────────────────────────────────│
  │                                   │
  │  ["stdin","pwd\r\n"]              │── 写入 PTY，执行命令
  │──────────────────────────────────►│
  │                                   │── PTY 输出
  │  ["stdout","/home/user\r\n$ "]    │
  │◄──────────────────────────────────│
  │                                   │
  │  ... (持续交互) ...               │
  │                                   │
  │  WS Close / DELETE /api/terminals/1│── 关闭终端
  │──────────────────────────────────►│
```

## 连接失败排查

| 错误码 | 可能原因 | 解决方案 |
|--------|---------|---------|
| 403 | 未登录或无 execute 权限 | 检查认证 token/cookie，确认用户有 terminals 资源的 execute 权限 |
| 404 | 终端名称不存在 | 先 POST 创建终端，确认 name 正确，等待终端就绪 |
| 连接立即断开 | terminado 初始化失败或 Shell 不存在 | 检查 shell_command 配置，验证 Shell 路径正确 |

测试代码中常见的重试模式（等待终端就绪）：

```python
while True:
    try:
        ws = await jp_ws_fetch("terminals", "websocket", term_name)
        break
    except HTTPClientError as e:
        if e.code != 404:
            raise
        await asyncio.sleep(1)  # 等待终端进程启动
```

## 相关概念

- [REST API 处理器](04-rest-api.md)
- [TerminalManager 终端管理器](03-terminal-manager.md)
- [TerminalsExtensionApp 扩展应用](02-extension-app.md)
- [WebSocket 实时通信示例](../examples/websocket-interaction.md)
- [jupyter_server_terminals 源码信源登记](../references/jupyter-server-terminals-source.md)

[^jst-source]: jupyter_server_terminals 源码信源，见 [jupyter-server-terminals-source.md](../references/jupyter-server-terminals-source.md)。
