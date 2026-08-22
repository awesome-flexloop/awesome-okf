---
okf_version: "0.2"
type: concept
title: "Client插件详解"
description: "深入理解 jupyter_client 插件：ZMQ上下文管理、内核启动工厂fixture、资源自动清理机制、echo_kernel与原生内核的选择。"
tags: [client-plugin, kernel, zmq, jupyter-client, kernel-manager, kernel-client, echo-kernel, ipykernel, resource-cleanup]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:45:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T14:45:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: jupyter-client-source
    resource: "/references/jupyter-client-source.md"
    title: "Client插件源码信源"
  - id: echo-kernel-source
    resource: "/references/echo-kernel-source.md"
    title: "Echo内核源码信源"
---

# Client插件详解

Client插件（`pytest_jupyter.jupyter_client`）在Core插件基础上提供Jupyter内核（Kernel）生命周期管理能力。它让测试中启动、通信、关闭Jupyter内核变得简单，并自动处理ZMQ资源清理。

## 插件激活条件

Client插件需要额外的可选依赖：

```bash
pip install "pytest-jupyter[client]"
```

依赖包括：`jupyter_client>=7.4.0`、`nbformat>=5.3`、`ipykernel>=6.14`。

如果未安装这些依赖就尝试加载client插件，模块顶部的`try/except ImportError`会发出友好警告：
> "The client plugin has not been installed. Try: `pip install 'pytest-jupyter[client]'`"

[F-030]

## Fixture依赖关系

```
pytest内置
├── tmp_path ── jp_*_dir (core) ── jp_environ ──┐
│                                                │
jp_asyncio_loop (core, autouse) ────────────────┤
│                                                │
└────────────────────────────────────────────────┴── jp_start_kernel
                                                      │
                                                 返回inner函数
                                                      │
                                            ┌─────────┴─────────┐
                                            │  测试中调用inner()  │
                                            │  km, kc = await    │
                                            │  jp_start_kernel() │
                                            └───────────────────┘
```

Client插件通过`from pytest_jupyter.jupyter_core import *`继承所有core fixtures。

[F-030]

## ZMQ上下文管理：jp_zmq_context

```python
@pytest.fixture
def jp_zmq_context():
    import zmq
    ctx = zmq.asyncio.Context()
    yield ctx
    ctx.term()
```

**行为：**
- 懒加载`import zmq`（在fixture内部导入，而非模块顶部，避免zmq未安装时模块加载失败）
- 创建`zmq.asyncio.Context()`——异步ZMQ上下文
- yield给测试使用
- 测试结束后调用`ctx.term()`终止上下文，释放ZMQ资源

ZMQ上下文是所有ZMQ socket的容器，必须正确关闭以避免资源泄漏。

[F-031]

## 内核启动工厂：jp_start_kernel

`jp_start_kernel`是Client插件的核心fixture，采用**工厂模式**——返回一个内部函数而非直接启动内核，允许测试中灵活启动一个或多个内核。

### 基本用法

```python
async def test_kernel(jp_start_kernel):
    # 启动默认内核（python3，即NATIVE_KERNEL_NAME）
    km, kc = await jp_start_kernel()
    assert km.kernel_name == "python3"

    # 启动echo内核（快速测试用）
    km_echo, kc_echo = await jp_start_kernel("echo")
    assert km_echo.kernel_name == "echo"
```

### inner函数签名

```python
async def inner(kernel_name=NATIVE_KERNEL_NAME, **kwargs):
```

**参数：**
- `kernel_name` (str): 内核名称，默认为`NATIVE_KERNEL_NAME`（通常是`"python3"`）
- `**kwargs`: 传递给`jupyter_client.manager.start_new_async_kernel()`的额外参数

**返回值：**
- `km` (KernelManager): 内核管理器实例，可用于控制内核生命周期
- `kc` (KernelClient): 内核客户端实例，用于发送/接收内核消息

[F-032]

### 资源追踪与清理

`jp_start_kernel`使用两个列表追踪所有创建的资源：

```python
kms = []  # KernelManager列表
kcs = []  # KernelClient列表
```

每次调用`inner()`启动内核时，`km`和`kc`会被追加到对应列表。测试结束后（yield之后）：

```python
# 1. 停止所有KernelClient的通道
for kc in kcs:
    kc.stop_channels()

# 2. 关闭所有KernelManager（立即shutdown）
for km in kms:
    jp_asyncio_loop.run_until_complete(km.shutdown_kernel(now=True))
    # 防御性断言
    if not km.context.closed:
        raise AssertionError
```

**关键安全措施：**
- `now=True`：立即关闭内核，不等待内核完成当前执行
- **防御性断言**：如果`km.context.closed`不为True，抛出AssertionError，强制暴露ZMQ上下文泄漏
- 按顺序清理：先停止客户端通道，再关闭内核管理器

[F-032]

## Echo测试内核

pytest-jupyter内置了一个极简的**回显内核（EchoKernel）**，专门用于加速测试。

### 为什么需要EchoKernel？

完整的IPython内核（ipykernel）启动较慢（需要初始化Python解释器、命名空间、completer等），对于只需要测试"内核能否启动""消息能否收发"的场景，启动完整内核是浪费时间。EchoKernel：

1. 启动极快（不初始化Python执行环境）
2. 将收到的代码原样回显到stdout
3. 支持基本的`input()`请求处理
4. 完全兼容Jupyter消息协议

### EchoKernel实现要点

```python
class EchoKernel(Kernel):
    implementation = "Echo"
    language = "echo"
    language_info = {"name": "echo", "mimetype": "text/plain", "file_extension": ".txt"}
    banner = "Echo kernel - as useful as a parrot"

    def do_execute(self, code, silent, ...):
        if not silent:
            stream_content = {"name": "stdout", "text": code}
            self.send_response(self.iopub_socket, "stream", stream_content)
            if allow_stdin and code and "input(" in code:
                self._input_request("Echo Prompt", ...)
        return {"status": "ok", "execution_count": self.execution_count, ...}
```

- `do_execute`方法只做一件事：将`code`字符串原样作为stdout流消息发回
- 当code中包含`"input("`且`allow_stdin=True`时，发送input_request消息
- 返回`"status": "ok"`表示执行成功

### EchoKernelApp启动入口

```python
class EchoKernelApp(IPKernelApp):
    kernel_class = EchoKernel

if __name__ == "__main__":
    logging.disable(logging.ERROR)
    EchoKernelApp.launch_instance()
```

通过设置`kernel_class = EchoKernel`复用IPKernelApp的完整启动逻辑（连接文件解析、ZMQ通道建立、心跳等），只替换内核类本身。

[F-040]~[F-043]

### 使用EchoKernel的测试示例

```python
async def test_echo_kernel(jp_start_kernel):
    km, kc = await jp_start_kernel("echo")

    # 发送消息并等待回复
    msg = await kc.execute("hello world", reply=True)
    assert msg["content"]["status"] == "ok"

    # 在iopub通道上收集输出
    msg = await kc.get_iopub_msg()
    assert msg["content"]["text"] == "hello world"

async def test_native_kernel(jp_start_kernel):
    # 使用默认的python3内核（真实执行Python代码）
    km, kc = await jp_start_kernel()
    msg = await kc.execute("print('hi')", reply=True)
    assert msg["content"]["status"] == "ok"
```

[F-032]

## 内核消息通信基础

使用`kc`（KernelClient）与内核通信的基本模式：

```python
async def test_kernel_communication(jp_start_kernel):
    km, kc = await jp_start_kernel("echo")

    # 发送执行请求
    msg_id = kc.execute("test code")

    # 等待shell通道的reply消息
    reply = await kc.get_shell_msg(timeout=10)
    assert reply["content"]["status"] == "ok"

    # 或者使用reply=True（等待回复并返回）
    reply = await kc.execute("test code", reply=True)
```

**KernelClient通道：**
- `shell`：请求/回复通道（执行、补全、inspect等）
- `iopub`：广播通道（stdout/stderr输出、执行状态、display_data等）
- `stdin`：输入请求通道（内核请求用户输入）
- `hb`（心跳）：心跳通道（由KernelManager管理）
- `control`：控制通道（shutdown、debug等）

## Client插件使用建议

1. **优先使用echo内核做协议测试**：测试内核消息协议、WebSocket通道、API层逻辑时，用`"echo"`内核加速；只有需要真实执行Python代码时才用默认内核
2. **总是使用jp_start_kernel而非手动创建KernelManager**：手动创建的KernelManager不会被自动清理，容易导致ZMQ资源泄漏
3. **可以启动多个内核**：`jp_start_kernel`返回的工厂函数支持在一个测试中启动多个内核，所有内核都会被追踪并在测试结束后清理
4. **注意kc.execute是异步的**：发送消息后需要await get_shell_msg()或使用`reply=True`等待回复
5. **Client插件不包含HTTP测试能力**：需要测试Server REST API时，请加载`pytest_jupyter.jupyter_server`（它包含client的所有功能）

---

**下一步阅读：**
- [Echo内核深入](/concepts/07-echo-kernel.md) — EchoKernel的完整实现细节和扩展方式
- [Tornado异步支持](/concepts/06-tornasync-plugin.md) — HTTP测试基础设施
- [Server插件详解](/concepts/05-server-plugin.md) — 完整Server测试栈（含client能力）
