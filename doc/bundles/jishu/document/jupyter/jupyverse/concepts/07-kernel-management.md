---
type: Concept
title: "内核管理"
description: "Kernels 服务管理 Jupyter 内核的完整生命周期，包括内核启动/关闭/中断/重启、会话管理、内核规格查询，以及通过 WebSocket channels 实现前端与内核的 Jupyter 协议通信。"
tags: [kernels, kernel, sessions, websocket, zmq, execution, lifecycle]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T06:55:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: kernels_api
    resource: /references/kernels-api-source.md
    title: Kernels API 信源
  - id: kernel_api
    resource: /references/kernel-api-source.md
    title: Kernel 抽象信源
  - id: fps_kernels
    resource: /references/fps-kernels-source.md
    title: fps-kernels 实现信源
---

# 内核管理

Kernels 服务是 Jupyverse 中最复杂的核心服务，负责 Jupyter 内核的生命周期管理、会话（Session）管理以及前端与内核之间的消息通信。

## 核心概念

### Kernel（内核实例）

一个 Kernel 实例代表一个运行中的 Jupyter 内核进程（如 IPython），通过 ZeroMQ 通道与 Jupyverse 通信。

```python
class Kernel(BaseModel):
    id: str                    # 内核唯一 ID（UUID）
    name: str                  # 内核规格名称（如 "python3"）
    last_activity: str         # 最后活动时间
    execution_state: str       # 执行状态：starting/idle/busy
    connections: int           # 当前 WebSocket 连接数
```

### Session（会话）

Session 将一个 Notebook 文件与一个内核实例关联：

```python
class Session(BaseModel):
    id: str                    # 会话唯一 ID
    path: str                  # Notebook 文件路径
    name: str                  # 会话名称
    type: str                  # 类型（通常是 "notebook"）
    kernel: Kernel             # 关联的内核
    notebook: Notebook         # 关联的 Notebook 信息
```

### KernelSpec（内核规格）

KernelSpec 描述可用的内核类型（Python、R、Julia 等），包含内核启动命令、显示名称、语言等元数据。

## REST API 端点

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | `/api/status` | status:read | 服务器状态（内核/连接数） |
| GET | `/api/kernelspecs` | kernelspecs:read | 获取所有可用内核规格 |
| GET | `/kernelspecs/{name}/{file}` | - | 获取内核规格资源文件（logo、kernel.js等） |
| GET | `/api/kernels` | kernels:read | 获取所有运行中内核列表 |
| GET | `/api/kernels/{id}` | kernels:read | 获取指定内核信息 |
| POST | `/api/kernels` | kernels:write | 启动新内核（通过创建会话） |
| DELETE | `/api/kernels/{id}` | kernels:write | 关闭内核 |
| POST | `/api/kernels/{id}/interrupt` | kernels:write | 中断内核执行（SIGINT） |
| POST | `/api/kernels/{id}/restart` | kernels:write | 重启内核 |
| POST | `/api/kernels/{id}/execute` | kernels:write | 执行代码单元格 |
| GET | `/api/sessions` | sessions:read | 获取所有会话 |
| POST | `/api/sessions` | sessions:write | 创建新会话（启动内核+关联文件） |
| PATCH | `/api/sessions/{id}` | sessions:write | 重命名会话 |
| DELETE | `/api/sessions/{id}` | sessions:write | 删除会话（关闭关联内核） |
| WebSocket | `/api/kernels/{id}/channels` | kernels:execute | 内核通信通道 |

## WebSocket Channels

WebSocket `/api/kernels/{id}/channels` 是前端与内核通信的核心通道。Jupyter 协议定义了五个通道：

| 通道 | 方向 | 用途 |
|------|------|------|
| **shell** | 前端→内核 | 代码执行请求、补全请求、检查请求等 |
| **iopub** | 内核→前端 | 执行输出（stdout/stderr）、显示数据、执行状态广播 |
| **stdin** | 双向 | 标准输入请求（`input()` 函数） |
| **control** | 前端→内核 | 控制命令（中断、重启、关闭） |
| **heartbeat** | 双向 | 心跳检测（在 ZMQ 层面，不走 WebSocket） |

前端通过 WebSocket 发送的消息携带 `channel` 字段标识目标通道，Jupyverse 将消息转发到对应的 ZMQ 套接字。

## Kernel 抽象与工厂模式

Kernel 抽象基类使用 anyio 内存对象流（memory object stream）实现通道的内存表示：

```python
class Kernel(ABC):
    def __init__(self):
        self.key = "0"              # 消息签名密钥
        self.wait_for_ready = False
        self.started = Event()      # 内核就绪事件

        # Shell 通道（双向）
        self._shell_stream = StapledObjectStream(
            self._to_shell_send_stream, self._from_shell_receive_stream)
        # Control 通道（双向）
        self._control_stream = StapledObjectStream(...)
        # Stdin 通道（双向）
        self._stdin_stream = StapledObjectStream(...)
        # IOPub 通道（仅接收，无限缓冲）
        # max_buffer_size=float("inf")
```

### KernelFactory 与 DefaultKernelFactory

内核工厂使用注册模式：

```python
class KernelFactory:
    def __init__(self, kernel_factory: type[Kernel]):
        self._kernel_factory = kernel_factory
    def __call__(self, *args, **kwargs) -> Kernel:
        return self._kernel_factory(*args, **kwargs)
```

`fps-kernel-subprocess` 插件将子进程内核注册为默认工厂：

```python
class KernelSubprocessModule(Module):
    async def prepare(self):
        default_kernel_factory = DefaultKernelFactory(KernelSubprocess)
        self.put(default_kernel_factory)
```

也可以通过 `register_kernel_factory()` 注册其他内核类型（如 Web Worker 内核）：

```python
kernels.register_kernel_factory("web-worker", web_worker_factory)
```

## KernelsConfig

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| default_kernel | str | "python3" | 默认内核名称 |
| allow_external_kernels | bool | False | 是否允许外部内核（连接文件方式） |
| external_connection_dir | str\|None | None | 外部内核连接文件目录 |
| require_yjs | bool | False | 是否依赖 Yjs（协作时需要同步文档状态） |
| kernelenv_path | str | "" | 内核环境路径 |
| wait_for_kernelspec | bool | False | 是否等待 kernelspec 文件就绪 |

## 内核生命周期

```
创建会话 (POST /api/sessions)
    │
    ▼
启动内核进程 (KernelSubprocess.start())
    │  1. 启动内核子进程（python -m ipykernel_launcher）
    │  2. 建立 ZMQ 连接（shell/control/stdin/iopub/hb）
    │  3. 发送 kernel_info_request 获取内核信息
    │  4. 设置 started 事件
    ▼
内核就绪 (execution_state: "idle")
    │
    │ ◄── WebSocket 连接（前端连接 channels）
    │
    ▼
执行代码 (shell 通道发送 execute_request)
    │  iopub 通道广播: status(busy) → execute_input → stream/display_data/execute_result → status(idle)
    │
    ▼
中断/重启 (control 通道发送 interrupt_request 或重启进程)
    │
    ▼
关闭 (DELETE /api/kernels/{id} 或 DELETE /api/sessions/{id})
    │  发送 shutdown_request → 终止进程 → 清理资源
```

## 外部内核支持

当 `allow_external_kernels=True` 时，Kernels 服务会监视 `external_connection_dir` 目录中的连接文件（`kernel-*.json`），自动发现并连接到外部启动的内核进程。这适用于：
- 在容器外启动内核
- 连接到已有的内核进程
- 分布式内核场景

## 协作集成

当 `require_yjs=True` 时，Kernels 服务与 Yjs 协作模块集成，在内核启动和执行时同步 Notebook 文档的 CRDT 状态，确保多用户编辑时代码执行的一致性。

## 相关概念

- [Contents 文件服务](06-contents-service.md) — 会话关联的 Notebook 文件管理
- [协作编辑 Yjs](09-collaboration-yjs.md) — 内核与协作的集成
- [FPS 模块系统](03-fps-module-system.md) — KernelsModule 的依赖注入
- [插件开发指南](12-plugin-development.md) — 开发自定义内核类型
