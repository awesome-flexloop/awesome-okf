---
type: Reference
title: "services/kernels/ 内核管理源码信源"
description: "MappingKernelManager、Kernel WebSocket 连接、ZMQ 通道桥接与内核生命周期管理"
tags: [kernels, kernel-manager, websocket, zmq, ipython, lifecycle]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:40:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: kernelmanager-py
    resource: ../../../../../../external/libs/jupyter/jupyter_server/jupyter_server/services/kernels/kernelmanager.py
    title: jupyter_server/services/kernels/kernelmanager.py
  - id: handlers-py
    resource: ../../../../../../external/libs/jupyter/jupyter_server/jupyter_server/services/kernels/handlers.py
    title: jupyter_server/services/kernels/handlers.py
  - id: websocket-py
    resource: ../../../../../../external/libs/jupyter/jupyter_server/jupyter_server/services/kernels/websocket.py
    title: jupyter_server/services/kernels/websocket.py
  - id: connection-base-py
    resource: ../../../../../../external/libs/jupyter/jupyter_server/jupyter_server/services/kernels/connection/base.py
    title: jupyter_server/services/kernels/connection/base.py
  - id: channels-py
    resource: ../../../../../../external/libs/jupyter/jupyter_server/jupyter_server/services/kernels/connection/channels.py
    title: jupyter_server/services/kernels/connection/channels.py
---

# services/kernels/ 内核管理源码信源

## 模块结构

```
services/kernels/
├── __init__.py
├── handlers.py           # 内核 REST API Handlers
├── kernelmanager.py      # MappingKernelManager/AsyncMappingKernelManager
├── websocket.py          # KernelWebSocketHandler
└── connection/
    ├── __init__.py
    ├── abc.py            # 内核 WebSocket 连接抽象接口
    ├── base.py           # BaseKernelWebsocketConnection 基类
    └── channels.py       # ZMQChannelsWebsocketConnection ZMQ 桥接
```

## MappingKernelManager (kernelmanager.py L58)

管理多个 Jupyter 内核实例，继承自 `jupyter_client.MultiKernelManager`。

**核心配置项**：
| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `root_dir` | Unicode | cwd | 内核工作根目录 |
| `kernel_manager_class` | Type/Instance | AsyncIOLoopKernelManager | 单个内核管理器类 |
| `default_kernel_name` | Unicode | 'python3' | 默认内核名称 |
| `cull_idle_timeout` | Integer | 0 | 空闲内核回收超时（秒），0 禁用 |
| `cull_interval` | Integer | 300 | 空闲检查间隔（秒） |
| `cull_connected` | Bool | False | 是否回收有连接的空闲内核 |
| `cull_busy` | Bool | False | 是否回收忙碌内核 |
| `kernel_argv` | List(Unicode) | [] | 内核启动额外参数 |
| `transport_encryption` | Enum | 'disabled' | 传输加密策略 |

**核心方法**：
| 方法 | 说明 |
|------|------|
| `start_kernel(kernel_name, path, **kwargs)` | 启动新内核，返回 kernel_id |
| `shutdown_kernel(kernel_id, now)` | 关闭内核 |
| `restart_kernel(kernel_id)` | 重启内核 |
| `interrupt_kernel(kernel_id)` | 中断内核 |
| `get_kernel(kernel_id)` | 获取内核管理器 |
| `list_kernels()` | 列出所有运行中的内核 |
| `kernel_model(kernel_id)` | 获取内核 JSON 模型 |
| `cull_kernels()` | 回收空闲内核 |
| `start_w_activity_callback(callback)` | 注册内核活动回调 |

**内核模型格式**：
```python
{
    "id": "kernel-uuid",
    "name": "python3",
    "last_activity": "2024-01-01T00:00:00Z",
    "execution_state": "idle",  # idle/busy/starting
    "connections": 1,
}
```

### AsyncMappingKernelManager

MappingKernelManager 的异步版本，使用 async/await。

## Kernel WebSocket 连接体系

### BaseKernelWebsocketConnection (connection/base.py)

WebSocket 内核连接的基类，定义了桥接 Tornado WebSocket 与 ZMQ 通道的接口。

**核心方法**：
- `connect()`: 建立连接
- `disconnect()`: 断开连接
- `handle_incoming_message(msg)`: 处理来自前端的消息
- `handle_outgoing_message(msg)`: 处理来自内核的消息

### ZMQChannelsWebsocketConnection (connection/channels.py)

核心 ZMQ 通道桥接实现，管理五个 ZMQ 通道：

| 通道 | 用途 |
|------|------|
| Shell | 请求/执行代码 |
| IOPub | 广播输出/状态更新 |
| Stdin | 标准输入请求 |
| Control | 控制命令（中断/重启） |
| HB (Heartbeat) | 心跳检测 |

**核心功能**：
- 消息序列化/反序列化（使用 jupyter_client.session.Session）
- 通道消息路由
- 内核连接文件解析
- 消息签名验证
- WebSocket ↔ ZMQ 双向桥接

## WebSocket Handler (websocket.py)

`KernelWebSocketHandler` 处理 `/api/kernels/<kernel_id>/channels` WebSocket 连接：

- 认证检查
- 协商子协议（'v1.kernel.websocket.jupyter.org'）
- 创建 ZMQChannelsWebsocketConnection
- 消息转发
- 连接断开清理

## REST API Handlers (handlers.py)

| Handler | 路由 | 方法 |
|---------|------|------|
| MainKernelHandler | /api/kernels | GET(列表) / POST(启动) |
| KernelHandler | /api/kernels/(.*) | GET(模型) / DELETE(关闭) |
| KernelActionHandler | /api/kernels/(.*)/(.*) | POST(restart/interrupt) |
