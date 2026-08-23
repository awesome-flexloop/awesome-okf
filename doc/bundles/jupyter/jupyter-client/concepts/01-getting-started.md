---
okf_version: "0.2"
type: concept
title: "5分钟快速上手"
description: "安装 jupyter_client、启动内核、执行代码、获取结果、关闭内核，含 Python API 最小可运行示例"
tags: ["getting-started", "quickstart", "install", "basic-usage", "python-api"]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T15:57:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:57:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: manager-source
    resource: /references/manager-source.md
    title: 内核管理器信源
  - id: client-source
    resource: /references/client-source.md
    title: 客户端核心信源
---

# 5分钟快速上手

## 安装

jupyter_client 要求 Python ≥ 3.10，可以通过 pip 安装：

```bash
pip install jupyter_client ipykernel
```

`ipykernel` 是 Python 内核实现，jupyter_client 本身不包含内核，需要至少安装一个内核才能执行代码。

安装后可使用 `jupyter kernelspec list` 查看已安装的内核。

## 最小可运行示例：阻塞式 API

以下是使用 `BlockingKernelClient` 启动内核、执行代码、获取结果的完整示例：

```python
from jupyter_client import KernelManager

# 1. 创建内核管理器并启动内核
km = KernelManager(kernel_name="python3")
km.start_kernel()

try:
    # 2. 创建客户端并启动通道
    kc = km.client()
    kc.start_channels()

    # 3. 等待内核就绪
    kc.wait_for_ready(timeout=30)

    # 4. 执行代码
    msg_id = kc.execute("print('Hello, Jupyter!')\n2 + 2")

    # 5. 收集输出
    while True:
        msg = kc.get_iopub_msg(timeout=10)
        msg_type = msg["header"]["msg_type"]

        if msg_type == "stream":
            # stdout/stderr 输出
            print(f"[OUTPUT] {msg['content']['text']}", end="")

        elif msg_type == "execute_result":
            # 执行结果（最后一个表达式的值）
            print(f"[RESULT] {msg['content']['data'].get('text/plain', '')}")

        elif msg_type == "error":
            # 错误信息
            print(f"[ERROR] {msg['content']['ename']}: {msg['content']['evalue']}")

        # 判断是否执行完毕（status: idle 表示当前请求处理完）
        if (
            msg["parent_header"].get("msg_id") == msg_id
            and msg_type == "status"
            and msg["content"]["execution_state"] == "idle"
        ):
            break

    # 6. 获取 shell 通道的 execute_reply（包含执行计数等元数据）
    reply = kc.get_shell_msg(timeout=5)
    print(f"[EXECUTION] count={reply['content'].get('execution_count')}")

finally:
    # 7. 清理资源
    kc.stop_channels()
    km.shutdown_kernel()
```

预期输出：
```
[OUTPUT] Hello, Jupyter!
[RESULT] 4
[EXECUTION] count=1
```

## 使用便捷函数 start_new_kernel

`jupyter_client.manager` 提供了 `start_new_kernel()` 便捷函数，封装了上述步骤：

```python
from jupyter_client import start_new_kernel

# 启动内核并返回 (manager, client)
km, kc = start_new_kernel(kernel_name="python3", startup_timeout=30)

try:
    # 执行代码（execute_interactive 自动处理输出和 stdin）
    reply = kc.execute_interactive(
        "x = 10\nprint(f'x = {x}')\nx * 2",
        timeout=30,
        output_hook=lambda msg: (
            print(msg["content"]["text"], end="")
            if msg["header"]["msg_type"] == "stream"
            else None
        ),
    )
    print(f"Status: {reply['content']['status']}")
finally:
    kc.stop_channels()
    km.shutdown_kernel()
```

## 异步 API 示例

使用 `AsyncKernelManager` 和 `AsyncKernelClient` 进行异步操作：

```python
import asyncio
from jupyter_client import AsyncKernelManager

async def main():
    km = AsyncKernelManager(kernel_name="python3")
    await km.start_kernel()

    try:
        kc = km.client()
        kc.start_channels()
        await kc._async_wait_for_ready(timeout=30)

        msg_id = kc.execute("import this")

        while True:
            msg = await kc._async_get_iopub_msg(timeout=10)
            if msg["header"]["msg_type"] == "stream":
                print(msg["content"]["text"], end="")
            if (
                msg["parent_header"].get("msg_id") == msg_id
                and msg["header"]["msg_type"] == "status"
                and msg["content"]["execution_state"] == "idle"
            ):
                break
    finally:
        kc.stop_channels()
        await km.shutdown_kernel()

asyncio.run(main())
```

## 连接到已运行的内核

如果内核已经在运行（例如 Notebook 启动的内核），可以通过连接文件连接：

```python
from jupyter_client import BlockingKernelClient
import glob

# 查找最近的连接文件
import os
from jupyter_core.paths import jupyter_runtime_dir
runtime_dir = jupyter_runtime_dir()
connection_files = sorted(
    glob.glob(os.path.join(runtime_dir, "kernel-*.json")),
    key=os.path.getmtime,
)

if connection_files:
    kc = BlockingKernelClient()
    kc.load_connection_file(connection_files[-1])
    kc.start_channels()
    kc.wait_for_ready(timeout=10)

    # 现在可以向正在运行的内核发送命令
    msg_id = kc.execute("print('Connected to existing kernel!')")
    # ... 收集输出 ...

    kc.stop_channels()
```

## CLI 使用

jupyter_client 提供了几个命令行工具：

```bash
# 列出已安装的内核
jupyter-kernelspec list

# 安装内核规范
jupyter-kernelspec install /path/to/kernel_spec

# 直接运行脚本
jupyter-run my_script.py

# 启动内核（通常不需要手动调用）
jupyter-kernel
```

## 常见问题

**Q: 为什么我的 execute() 不返回结果？**
A: `execute()` 只发送消息并返回 `msg_id`，不会自动等待结果。需要通过 `get_iopub_msg()` 或 `get_shell_msg()` 主动从通道拉取消息，或者使用 `execute_interactive()` 方法。

**Q: wait_for_ready() 超时怎么办？**
A: 确认 ipykernel 已正确安装，内核启动命令可以手动在终端运行 `python -m ipykernel_launcher --help` 测试。

**Q: 如何支持 stdin 输入？**
A: 启动 stdin 通道并在 `execute_interactive()` 中传入 `stdin_hook`，或在消息循环中监听 stdin 通道的 `input_request` 消息。

## 相关概念

- [jupyter_client 简介](00-introduction.md)
- [架构总览](02-architecture-overview.md)
- [客户端体系](05-client-hierarchy.md)
