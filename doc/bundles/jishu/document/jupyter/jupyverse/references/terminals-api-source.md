---
type: Reference
title: "Terminals API 信源"
description: "终端服务抽象层，定义 Terminals ABC 和 Terminal/TerminalServer 模型，提供终端管理 REST API 和 WebSocket 通信。"
tags: [terminals, websocket, terminal-server, pty]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T06:55:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: terminals_init
    resource: /external/libs/jupyter/jupyverse/api/terminals/src/jupyverse_terminals/__init__.py
    title: jupyverse_terminals/__init__.py
  - id: terminals_models
    resource: /external/libs/jupyter/jupyverse/api/terminals/src/jupyverse_terminals/models.py
    title: jupyverse_terminals/models.py
---

# Terminals API 信源

## Terminals 抽象基类

Terminals 继承 Router 和 ABC，提供终端管理端点。

### REST API 端点

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | `/api/terminals` | terminals:read | 获取终端列表 |
| POST | `/api/terminals` | terminals:write | 创建新终端 |
| DELETE | `/api/terminals/{name}` | terminals:write | 删除终端 |
| WebSocket | `/terminals/websocket/{name}` | terminals:read,execute | 终端 WebSocket 通信 |

### 抽象方法

```python
@abstractmethod
async def get_terminals(self, user: User) -> list[Terminal]: ...

@abstractmethod
async def create_terminal(self, user: User): ...

@abstractmethod
async def delete_terminal(self, name: str, user: User): ...

@abstractmethod
async def terminal_websocket(self, name, websocket_permissions): ...
```

## TerminalServer 抽象

```python
class TerminalServer(ABC):
    @abstractmethod
    async def serve(self, websocket, permissions): ...

    @abstractmethod
    def quit(self, websocket): ...
```

TerminalServer 负责底层 PTY 进程管理和 WebSocket 数据转发。fps-terminals 插件提供具体实现（Windows 使用 win_server.py，其他平台使用 server.py）。

## Terminal 模型

```python
class Terminal(BaseModel):
    name: str
```
