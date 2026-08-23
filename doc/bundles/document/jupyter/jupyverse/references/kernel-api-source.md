---
type: Reference
title: "Kernel 抽象信源"
description: "Jupyter 内核抽象层，定义 Kernel ABC 和 KernelFactory，使用 anyio 内存对象流实现 Jupyter 协议通道。"
tags: [kernel, subprocess, channels, streams, zmq, factory]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T06:55:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: kernel_init
    resource: /external/libs/jupyter/jupyverse/api/kernel/src/jupyverse_kernel/__init__.py
    title: jupyverse_kernel/__init__.py
  - id: kernel_subprocess
    resource: /external/libs/jupyter/jupyverse/plugins/kernel_subprocess/src/fps_kernel_subprocess/main.py
    title: fps_kernel_subprocess/main.py
---

# Kernel 抽象信源

## Kernel 抽象基类

`Kernel` 类使用 anyio 的内存对象流（memory object stream）实现 Jupyter 协议的五个通道：

| 通道 | 方向 | 用途 |
|------|------|------|
| shell | 请求/响应 | 代码执行请求、完成请求等 |
| control | 请求/响应 | 控制命令（中断、重启等） |
| stdin | 请求/响应 | 标准输入请求（input()） |
| iopub | 发布 | 输出流、执行结果、状态更新等 |

### 内存流初始化

```python
def __init__(self):
    self.key = "0"
    self.wait_for_ready = False
    self.started = Event()

    # 创建五对 send/receive 流
    self._to_shell_send_stream, self._to_shell_receive_stream = create_memory_object_stream[list[bytes]]()
    self._from_shell_send_stream, self._from_shell_receive_stream = create_memory_object_stream[list[bytes]]()
    # ... control, stdin 同理
    self._from_iopub_send_stream, self._from_iopub_receive_stream = create_memory_object_stream[list[bytes]](max_buffer_size=float("inf"))

    # 打包为 StapledObjectStream（双向流）
    self._shell_stream = StapledObjectStream(self._to_shell_send_stream, self._from_shell_receive_stream)
    # ... control, stdin 同理
```

### 属性

| 属性 | 返回类型 | 说明 |
|------|---------|------|
| `shell_stream` | StapledObjectStream[list[bytes]] | Shell 通道双向流 |
| `control_stream` | StapledObjectStream[list[bytes]] | Control 通道双向流 |
| `stdin_stream` | StapledObjectStream[list[bytes]] | Stdin 通道双向流 |
| `iopub_stream` | MemoryObjectReceiveStream[list[bytes]] | IOPub 通道接收流（无限缓冲） |

### 抽象方法

| 方法 | 说明 |
|------|------|
| `start(*, task_status)` | 启动内核，设置 started 事件 |
| `stop()` | 停止内核 |
| `interrupt()` | 中断内核执行 |

## KernelFactory

```python
class KernelFactory:
    def __init__(self, kernel_factory: type[Kernel]):
        self._kernel_factory = kernel_factory

    def __call__(self, *args, **kwargs) -> Kernel:
        return self._kernel_factory(*args, **kwargs)
```

DefaultKernelFactory 继承 KernelFactory，作为默认内核工厂标记。

## fps-kernel-subprocess 插件

```python
class KernelSubprocessModule(Module):
    async def prepare(self) -> None:
        default_kernel_factory = DefaultKernelFactory(KernelSubprocess)
        self.put(default_kernel_factory)
```

该插件将 `KernelSubprocess`（子进程内核实现）注册为默认内核工厂。
