---
okf_version: "0.2"
type: example
title: "内核测试"
description: "使用Client插件的jp_start_kernel fixture启动和测试Jupyter内核，包括echo内核和Python原生内核。"
tags: [kernel, client, jp-start-kernel, echo-kernel, zmq, kernel-messages, ipykernel]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:45:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T14:45:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: test-client
    resource: "../../../../../external/libs/jupyter/pytest-jupyter/tests/test_jupyter_client.py"
    title: "tests/test_jupyter_client.py"
  - id: jupyter-client-source
    resource: "/references/jupyter-client-source.md"
    title: "Client插件源码信源"
  - id: echo-kernel-source
    resource: "/references/echo-kernel-source.md"
    title: "Echo内核源码信源"
---

# 内核测试

本文档演示如何使用pytest-jupyter的Client插件（`pytest_jupyter.jupyter_client`）测试Jupyter内核的启动、消息通信和生命周期管理。

## 前置条件

```bash
pip install "pytest-jupyter[client]"
```

```python
# conftest.py
pytest_plugins = ["pytest_jupyter.jupyter_client"]
```

## 示例1：启动并测试Echo内核

```python
async def test_echo_kernel_startup(jp_start_kernel):
    """测试echo内核启动和消息回显"""
    # 启动echo内核
    km, kc = await jp_start_kernel("echo")

    # 验证内核名称
    assert km.kernel_name == "echo"
    assert km.is_alive()

    # 发送执行请求，等待reply
    msg = await kc.execute("hello world", reply=True)
    assert msg["content"]["status"] == "ok"
    assert msg["parent_header"]["msg_type"] == "execute_request"

    # 等待iopub上的输出消息
    output_msg = await kc.get_iopub_msg(timeout=5)
    # echo内核将输入原样输出到stdout
    if output_msg["header"]["msg_type"] == "stream":
        assert output_msg["content"]["text"] == "hello world"
```

## 示例2：启动Python原生内核

```python
async def test_python_kernel_execution(jp_start_kernel):
    """测试Python3内核实际执行代码"""
    # 不传参数默认启动NATIVE_KERNEL_NAME（python3）
    km, kc = await jp_start_kernel()
    assert km.kernel_name == "python3"

    # 执行简单Python代码
    msg = await kc.execute("x = 2 + 2\nprint(x)", reply=True)
    assert msg["content"]["status"] == "ok"

    # 收集iopub消息直到收到idle状态
    outputs = []
    while True:
        msg = await kc.get_iopub_msg(timeout=10)
        msg_type = msg["header"]["msg_type"]
        if msg_type == "stream":
            outputs.append(msg["content"]["text"])
        elif msg_type == "status" and msg["content"]["execution_state"] == "idle":
            break

    # 验证输出包含"4"
    assert any("4" in out for out in outputs)
```

## 示例3：在一个测试中启动多个内核

`jp_start_kernel`是工厂fixture，可以多次调用启动多个内核。

```python
async def test_multiple_kernels(jp_start_kernel):
    """测试同时运行多个内核"""
    # 启动echo内核
    km_echo, kc_echo = await jp_start_kernel("echo")

    # 启动Python内核
    km_py, kc_py = await jp_start_kernel()

    # 两个内核都存活
    assert km_echo.is_alive()
    assert km_py.is_alive()
    assert km_echo.kernel_name == "echo"
    assert km_py.kernel_name == "python3"

    # 分别发送消息
    msg_echo = await kc_echo.execute("test", reply=True)
    msg_py = await kc_py.execute("1+1", reply=True)
    assert msg_echo["content"]["status"] == "ok"
    assert msg_py["content"]["status"] == "ok"

    # 测试结束后所有内核自动被清理
```

## 示例4：ZMQ上下文fixture

```python
def test_zmq_context(jp_zmq_context):
    """测试ZMQ上下文fixture"""
    import zmq
    # jp_zmq_context提供zmq.asyncio.Context
    assert isinstance(jp_zmq_context, zmq.asyncio.Context)
    # 底层socket未关闭
    assert not jp_zmq_context.closed
```

## 示例5：直接实例化EchoKernel（不走ZMQ）

对于单元测试EchoKernel的逻辑，不需要启动ZMQ通信：

```python
from unittest.mock import Mock, ANY
from jupyter_client.session import Session
from pytest_jupyter.echo_kernel import EchoKernel

def test_echo_kernel_do_execute_silent():
    """测试silent模式下不产生输出"""
    kernel = EchoKernel()
    kernel.session = Mock(spec=Session)
    kernel.iopub_socket = Mock()

    result = kernel.do_execute("test code", silent=True)
    assert result["status"] == "ok"
    assert result["execution_count"] == kernel.execution_count

    # silent=True时不应该发送stream消息
    kernel.send_response = Mock()
    kernel.do_execute("test", silent=True)
    kernel.send_response.assert_not_called()

def test_echo_kernel_do_execute_stdout():
    """测试非silent模式发送stdout"""
    kernel = EchoKernel()
    kernel.session = Mock(spec=Session)
    kernel.iopub_socket = Mock()
    kernel.send_response = Mock()

    result = kernel.do_execute("hello", silent=False)
    assert result["status"] == "ok"

    # 验证send_response被调用发送stream消息
    kernel.send_response.assert_called_with(
        kernel.iopub_socket,
        "stream",
        {"name": "stdout", "text": "hello"}
    )

def test_echo_kernel_do_execute_with_input():
    """测试包含input()时发送input_request"""
    kernel = EchoKernel()
    kernel.session = Mock(spec=Session)
    kernel.iopub_socket = Mock()
    kernel._input_request = Mock()
    kernel.send_response = Mock()
    kernel._parent_ident = {"shell": b"ident"}
    kernel.get_parent = Mock(return_value={})

    kernel.do_execute("x = input('?')", silent=False, allow_stdin=True)

    # 应该发送input_request
    kernel._input_request.assert_called_once()
```

## 示例6：自定义内核启动参数

```python
async def test_kernel_with_custom_kwargs(jp_start_kernel):
    """测试传递额外参数给start_new_async_kernel"""
    # 传递额外的内核启动参数
    km, kc = await jp_start_kernel(
        "echo",
        startup_timeout=30,  # 启动超时
        # 其他参数传递给jupyter_client.manager.start_new_async_kernel
    )
    assert km.is_alive()
```

## 内核消息协议基础

使用KernelClient（kc）与内核通信的基本模式：

```python
async def test_kernel_message_pattern(jp_start_kernel):
    km, kc = await jp_start_kernel("echo")

    # 1. 发送execute_request
    msg_id = kc.execute("test code")

    # 2. 在shell通道等待execute_reply
    reply = await kc.get_shell_msg(timeout=10)
    assert reply["parent_header"]["msg_id"] == msg_id
    assert reply["content"]["status"] == "ok"

    # 3. 在iopub通道接收输出和状态消息
    while True:
        msg = await kc.get_iopub_msg(timeout=5)
        msg_type = msg["header"]["msg_type"]
        if msg_type == "stream":
            # stdout/stderr输出
            text = msg["content"]["text"]
        elif msg_type == "status":
            if msg["content"]["execution_state"] == "idle":
                break  # 执行完成

    # 4. 使用reply=True简化（等待shell reply）
    reply = await kc.execute("more code", reply=True, timeout=10)
    assert reply["content"]["status"] == "ok"
```

## 运行测试

```bash
pytest tests/test_kernel.py -v
```

## 注意事项

1. **echo内核 vs Python内核**：echo内核启动极快但不执行代码；Python内核启动慢但能真正执行Python。根据测试需求选择。
2. **超时设置**：内核操作可能需要较长时间，始终给`get_iopub_msg`和`get_shell_msg`设置合理的timeout。
3. **资源清理**：jp_start_kernel在测试结束后自动清理内核资源，不需要手动调用shutdown。
4. **iopub消息消费**：执行代码后必须消费iopub消息直到idle状态，否则消息会堆积影响后续测试。

## 相关概念

- [Client插件详解](../concepts/04-client-plugin.md) — Client插件fixtures完整API
- [Echo测试内核](../concepts/07-echo-kernel.md) — EchoKernel实现细节
- [Server API测试](03-server-api-test.md) — 结合Server插件测试REST API
