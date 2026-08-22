---
okf_version: "0.2"
type: reference
title: "Client插件源码（jupyter_client.py）"
description: "pytest_jupyter/jupyter_client.py 的完整API：ZMQ上下文fixture、内核启动工厂fixture、资源自动清理"
tags: [client-plugin, kernel, zmq, ipykernel, start-kernel, kernel-manager, kernel-client, cleanup]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:45:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T14:45:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: jupyter-client-py
    resource: "../../../../../external/libs/jupyter/pytest-jupyter/pytest_jupyter/jupyter_client.py"
    title: "pytest_jupyter/jupyter_client.py"
---

# Client插件源码（jupyter_client.py）

本信源登记 `pytest_jupyter/jupyter_client.py`（约57行）的核心fixtures。jupyter_client.py提供Jupyter内核管理相关的测试fixtures，通过`from pytest_jupyter.jupyter_core import *`继承core插件的所有fixtures。

## 模块级导入处理

### 可选依赖导入

模块顶部使用try/except处理可选依赖：

```python
try:
    import ipykernel
    from jupyter_client.kernelspec import NATIVE_KERNEL_NAME
    from jupyter_client.manager import start_new_async_kernel
except ImportError:
    warnings.warn(
        "The client plugin has not been installed. "
        "Try: `pip install 'pytest-jupyter[client]'`",
        stacklevel=2,
    )
```

**导入项：**
- `NATIVE_KERNEL_NAME`：本机默认内核名（通常为`"python3"`）
- `start_new_async_kernel`：异步启动新内核的工厂函数
- `ipykernel`：确保IPython内核已安装（导入检查）

[F-030]

## 核心Fixtures

### jp_zmq_context()

提供ZMQ asyncio上下文。

**行为：**
1. 在fixture内部懒加载`import zmq`
2. 创建`zmq.asyncio.Context()`
3. yield该context
4. 测试结束后调用`ctx.term()`终止上下文

[F-031]

### jp_start_kernel(jp_environ, jp_asyncio_loop)

内核启动工厂fixture，返回一个可调用的`inner`函数用于启动内核。

**inner函数签名：**
```python
async def inner(kernel_name=NATIVE_KERNEL_NAME, **kwargs):
```

**参数：**
- `kernel_name` (str): 内核名称，默认为`NATIVE_KERNEL_NAME`（即`"python3"`）
- `**kwargs`: 传递给`start_new_async_kernel`的额外参数

**返回：**
- `(km, kc)` 元组：`km`是KernelManager实例，`kc`是KernelClient实例

**资源清理（yield之后）：**
1. 遍历所有创建的kc（KernelClient），调用`kc.stop_channels()`停止通道
2. 遍历所有创建的km（KernelManager），在事件循环上运行`km.shutdown_kernel(now=True)`
3. 断言：`km.context.closed`必须为True，否则抛出AssertionError

**依赖fixtures：**
- `jp_environ`：提供隔离的Jupyter环境
- `jp_asyncio_loop`：提供事件循环用于运行内核关闭协程

[F-032]

## 设计要点

1. **懒导入警告**：模块顶部try/except提供友好的安装提示，而非直接抛出ImportError
2. **工厂模式**：`jp_start_kernel`返回内部函数而非直接启动内核，允许测试中灵活调用（可启动多个内核）
3. **资源追踪**：使用`kms = []`和`kcs = []`列表追踪所有创建的内核管理器和客户端，确保测试结束全部清理
4. **强制清理断言**：清理后断言`km.context.closed`为True，防止ZMQ上下文泄漏
5. **插件继承**：通过`from pytest_jupyter.jupyter_core import *`继承core插件的所有fixtures（jp_environ、jp_asyncio_loop等）
6. **默认内核可配置**：虽然默认使用NATIVE_KERNEL_NAME，但测试可以传入`"echo"`来使用echo_kernel
