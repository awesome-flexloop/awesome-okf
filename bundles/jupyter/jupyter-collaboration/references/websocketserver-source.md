---
type: Reference
title: WebSocket服务器源码分析
description: JupyterWebsocketServer 的实现：房间管理、消息广播、监控任务
tags: [backend, websocket, server]
sources:
  - id: websocketserver-py
    title: jupyter_server_ydoc/websocketserver.py
    resource: file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter-collaboration/projects/jupyter-server-ydoc/jupyter_server_ydoc/websocketserver.py
  - id: utils-py
    title: jupyter_server_ydoc/utils.py
    resource: file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter-collaboration/projects/jupyter-server-ydoc/jupyter_server_ydoc/utils.py
generated: { by: source-code-to-okf-wiki/agent, at: "2026-04-21T00:00:00Z" }
status: stable
---

# WebSocket 服务器与工具函数源码分析

## JupyterWebsocketServer

**文件**：`websocketserver.py`
**继承**：`pycrdt.websocket.WebsocketServer`

JupyterWebsocketServer 是 pycrdt WebsocketServer 的 Jupyter 定制版本，管理所有文档房间和客户端连接。

### 构造参数

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `ystore_class` | type[BaseYStore] | 必填 | Y存储类 |
| `rooms_ready` | bool | `True` | 房间是否立即可用 |
| `auto_clean_rooms` | bool | `True` | 是否自动清理空房间 |
| `exception_handler` | Callable | None | 异常处理函数 |
| `log` | Logger | None | 日志器 |

在 `YDocExtension` 中创建时使用 `rooms_ready=False, auto_clean_rooms=False`，因为房间的ready状态和清理由Jupyter侧手动管理。

### 核心属性

| 属性 | 说明 |
|---|---|
| `ypatch_nb` | 一分钟内处理的Y补丁计数（监控用） |
| `connected_users` | dict[int, str]，客户端ID→用户名映射 |
| `rooms` | dict[str, YRoom]，所有活跃房间 |
| `monitor_task` | 异步监控任务 |

### 核心方法

#### room_exists(path) → bool

检查指定room_id的房间是否存在。

#### add_room(path, room)

将房间添加到服务器管理中。

#### async get_room(path) → YRoom

获取房间，如果不存在则抛出 `RoomNotFound`。获取时自动调用 `start_room(room)` 确保房间已启动。

#### async serve(websocket)

重写父类方法，在首次调用时启动监控任务：

```python
async def serve(self, websocket):
    if self.monitor_task is None:
        self.monitor_task = asyncio.create_task(self._monitor())
    await super().serve(websocket)
```

#### async clean()

清理所有资源：停止服务器、取消监控任务。

#### async _monitor()

每60秒执行一次的监控循环：

1. 统计所有房间的客户端总数
2. 如果有补丁处理，记录"Processed N Y patches in one minute"
3. 如果客户端数变化，记录"Connected Y users: N"
4. 重置 `ypatch_nb = 0`

### RoomNotFound 异常

当请求不存在的房间时抛出，继承自 `LookupError`。

### exception_logger

模块级别的默认异常处理器，记录错误日志并返回 `True`（表示异常已处理，不终止serve循环）：

```python
def exception_logger(exception: Exception, log: Logger) -> bool:
    log.error("Jupyter Websocket Server: ", exc_info=exception)
    return True
```

---

## 工具函数（utils.py）

### 常量

| 常量 | 值 | 说明 |
|---|---|---|
| `JUPYTER_COLLABORATION_EVENTS_URI` | `https://schema.jupyter.org/jupyter_collaboration/session/v1` | 会话事件Schema URI |
| `JUPYTER_COLLABORATION_AWARENESS_EVENTS_URI` | `https://schema.jupyter.org/jupyter_collaboration/awareness/v1` | Awareness事件Schema URI |
| `JUPYTER_COLLABORATION_FORK_EVENTS_URI` | `https://schema.jupyter.org/jupyter_collaboration/fork/v1` | Fork事件Schema URI |
| `SERVER_SESSION` | `str(uuid.uuid4())` | 服务器启动时生成的唯一会话ID |
| `YDOC_SERVER_VERSION` | `__version__` | 协作包版本号 |

### 枚举类型

**MessageType(IntEnum)**：WebSocket消息类型

| 值 | 名称 | 说明 |
|---|---|---|
| 0 | SYNC | Yjs同步消息 |
| 1 | AWARENESS | Awareness状态更新 |
| 2 | RAW | 自定义JSON消息（save/conflict等） |
| 125 | CHAT | 聊天消息 |

**LogLevel(Enum)**：日志级别
- INFO, DEBUG, WARNING, ERROR, CRITICAL

### 异常类

| 异常 | 说明 |
|---|---|
| `OutOfBandChanges` | 文件被外部修改 |
| `ReadError` | 读取错误 |
| `WriteError` | 写入错误 |

### 路径编解码

```python
def encode_file_path(format: str, file_type: str, file_id: str) -> str:
    return f"{format}:{file_type}:{file_id}"

def decode_file_path(path: str) -> tuple[str, str, str]:
    format, file_type, file_id = path.split(":", 2)
    return (format, file_type, file_id)

def room_id_from_encoded_path(encoded_path: str) -> str:
    return encoded_path.split("/")[-1]
```

### 会话兼容性管理

#### save_current_session()

将当前会话信息持久化到 JSON 文件：

- 路径：`<root_dir>/.jupyter/collaboration_sessions.json`（或自定义 `session_store_path`）
- 内容：`{sessionId: {version, created_at, document_version}}`
- 只保留最近10个会话记录
- 写入失败时静默处理（回退到 `/dev/null`）

#### check_session_compatibility()

检查客户端携带的旧sessionId是否可以重连：

| 条件 | 结果 |
|---|---|
| sessionId == SERVER_SESSION | ✅ 兼容（当前会话） |
| sessionId不在记录中 | ❌ 不兼容（unknown_session） |
| 版本号不匹配 | ❌ 不兼容（version_mismatch） |
| document_version不匹配 | ❌ 不兼容（version_mismatch） |
| 全部匹配 | ✅ 兼容 |

## 关键设计洞察

1. **房间管理委托**：JupyterWebsocketServer 禁用了自动房间管理（auto_clean_rooms=False），清理逻辑由YDocWebSocketHandler的延迟清理机制接管
2. **永不崩溃**：exception_handler确保WebSocket服务不会因单条消息处理失败而终止
3. **会话版本控制**：通过SERVER_SESSION（启动时UUID）和版本号检测不兼容的重连，防止脏数据合并
4. **监控轻量**：_monitor任务仅做日志统计，不影响核心同步路径性能
5. **优雅降级**：会话存储写入失败时回退到os.devnull，不影响核心功能

## 相关概念

- [WebSocket通信协议](../concepts/05-websocket-protocol.md)
- [整体架构概览](../concepts/01-architecture-overview.md)
- [文档房间管理](../concepts/03-document-room.md)
