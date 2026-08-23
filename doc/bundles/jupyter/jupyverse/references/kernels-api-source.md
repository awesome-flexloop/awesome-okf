---
type: Reference
title: "Kernels API 信源"
description: "内核管理服务抽象层，定义 Kernels ABC、Session/Kernel 模型和 KernelsConfig，提供内核与会话的 REST API 和 WebSocket 通道。"
tags: [kernels, sessions, websocket, execution, kernel-management]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T06:55:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: kernels_init
    resource: /external/libs/jupyter/jupyverse/api/kernels/src/jupyverse_kernels/__init__.py
    title: jupyverse_kernels/__init__.py
  - id: kernels_models
    resource: /external/libs/jupyter/jupyverse/api/kernels/src/jupyverse_kernels/models.py
    title: jupyverse_kernels/models.py
---

# Kernels API 信源

## Kernels 抽象基类

`Kernels` 继承 `Router` 和 `ABC`，注册内核管理和会话管理的 REST/WebSocket 端点。

### REST API 端点

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | `/api/status` | status:read | 服务器状态 |
| GET | `/api/kernelspecs` | kernelspecs:read | 获取可用内核规格 |
| GET | `/kernelspecs/{kernel_name}/{file_name}` | - | 获取内核规格资源文件 |
| GET | `/api/kernels` | kernels:read | 获取运行中的内核列表 |
| GET | `/api/kernels/{kernel_id}` | kernels:read | 获取指定内核信息 |
| POST | `/api/kernels/{kernel_id}/interrupt` | kernels:write | 中断内核 |
| POST | `/api/kernels/{kernel_id}/restart` | kernels:write | 重启内核 |
| POST | `/api/kernels/{kernel_id}/execute` | kernels:write | 执行代码单元格 |
| DELETE | `/api/kernels/{kernel_id}` | kernels:write | 关闭内核 |
| GET | `/api/sessions` | sessions:read | 获取会话列表 |
| POST | `/api/sessions` | sessions:write | 创建新会话 |
| PATCH | `/api/sessions/{session_id}` | sessions:write | 重命名会话 |
| DELETE | `/api/sessions/{session_id}` | sessions:write | 删除会话 |
| WebSocket | `/api/kernels/{kernel_id}/channels` | kernels:execute | 内核通信通道 |

### 抽象方法

| 方法 | 说明 |
|------|------|
| `watch_connection_files(path)` | 监视外部内核连接文件 |
| `get_status(user)` | 获取服务器状态 |
| `get_kernelspecs(user)` | 获取内核规格 |
| `get_kernelspec(kernel_name, file_name, user)` | 获取内核规格文件 |
| `get_kernels(user)` | 获取内核列表 |
| `get_kernel(kernel_id, user)` | 获取指定内核 |
| `interrupt_kernel(kernel_id, user)` | 中断内核 |
| `restart_kernel(kernel_id, user)` | 重启内核 |
| `execute_cell(request, kernel_id, user)` | 执行单元格 |
| `shutdown_kernel(kernel_id, user)` | 关闭内核 |
| `get_sessions(user)` | 获取会话列表 |
| `create_session(request, user)` | 创建会话 |
| `rename_session(request, user)` | 重命名会话 |
| `delete_session(session_id, user)` | 删除会话 |
| `kernel_channels(kernel_id, session_id, websocket_permissions)` | WebSocket 通信 |
| `register_kernel_factory(kernel_name, kernel_factory)` | 注册内核工厂 |

### KernelsConfig

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| default_kernel | str | "python3" | 默认内核名称 |
| allow_external_kernels | bool | False | 是否允许外部内核 |
| external_connection_dir | str\|None | None | 外部内核连接文件目录 |
| require_yjs | bool | False | 是否依赖 Yjs 协作 |
| kernelenv_path | str | "" | 内核环境路径 |
| wait_for_kernelspec | bool | False | 是否等待 kernelspec 文件 |

## 数据模型

### Kernel

```python
class Kernel(BaseModel):
    id: str
    name: str
    last_activity: str
    execution_state: str  # "starting" | "idle" | "busy"
    connections: int
```

### Session

```python
class Session(BaseModel):
    id: str
    path: str
    name: str
    type: str
    kernel: Kernel
    notebook: Notebook
```

### Notebook

```python
class Notebook(BaseModel):
    path: str
    name: str
```

### CreateSession

```python
class CreateSession(BaseModel):
    kernel: KernelInfo
    name: str
    path: str
    type: str
```
