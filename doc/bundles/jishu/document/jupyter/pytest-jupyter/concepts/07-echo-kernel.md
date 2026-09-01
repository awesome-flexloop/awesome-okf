---
okf_version: "0.2"
type: concept
title: "Echo测试内核"
description: "深入理解 EchoKernel 回显内核的实现原理、类属性定义、do_execute 方法、stdin 输入处理，以及如何使用和扩展测试内核。"
tags: [echo-kernel, kernel, ipykernel, do-execute, testing-kernel, kernel-app, stdin, kernel-spec]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:45:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T14:45:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: echo-kernel-source
    resource: "/references/echo-kernel-source.md"
    title: "Echo内核源码信源"
  - id: jupyter-core-source
    resource: "/references/jupyter-core-source.md"
    title: "Core插件源码信源"
---

# Echo测试内核

EchoKernel 是 pytest-jupyter 内置的一个**极简测试内核**，它将收到的代码原样回显（echo）到stdout，不做任何实际执行。在测试中使用echo内核可以大幅加速测试运行，因为不需要启动完整的IPython内核。

## 为什么需要EchoKernel？

在测试Jupyter相关组件时，很多场景并不需要内核真正执行代码：

| 测试场景 | 是否需要真实Python执行 | EchoKernel是否足够 |
|---------|:---:|:---:|
| 内核能否启动/关闭 | ❌ | ✅ |
| 内核消息协议是否正确 | ❌ | ✅ |
| WebSocket通道是否连通 | ❌ | ✅ |
| KernelManager生命周期管理 | ❌ | ✅ |
| REST API的kernel端点 | ❌ | ✅ |
| 代码实际执行结果验证 | ✅ | ❌ |
| Python语法检查/补全 | ✅ | ❌ |
| 显示数据(display_data)渲染 | ✅ | ❌ |

对于前5类场景，启动完整的IPython内核是浪费时间——IPython内核启动需要初始化Python解释器、命名空间、completer、matplotlib后端等，耗时数秒。EchoKernel启动几乎瞬间完成。

## 类结构

```
ipykernel.kernelbase.Kernel (抽象基类)
└── EchoKernel (pytest_jupyter.echo_kernel)
    ├── 类属性（元信息）
    ├── do_execute() — 核心执行方法
    └── (其他方法继承自Kernel基类)

ipykernel.kernelapp.IPKernelApp
└── EchoKernelApp
    └── kernel_class = EchoKernel
```

## 类属性（内核元信息）

EchoKernel定义了以下类属性来声明内核的身份信息：

| 属性 | 值 | 说明 |
|------|-----|------|
| `implementation` | `"Echo"` | 内核实现名称，显示在内核信息中 |
| `implementation_version` | `"1.0"` | 内核实现版本 |
| `language` | `"echo"` | 语言标识（不是python，是自定义的echo语言） |
| `language_version` | `"0.1"` | 语言版本 |
| `banner` | `"Echo kernel - as useful as a parrot"` | 内核启动横幅文本 |
| `language_info` | `{"name": "echo", "mimetype": "text/plain", "file_extension": ".txt"}` | 语言信息字典 |

**language_info 字段说明：**
- `name`: 语言名称（`"echo"`）
- `mimetype`: 代码的MIME类型（纯文本）
- `file_extension`: 该语言文件的扩展名（`.txt`）

这些属性通过Jupyter消息协议的`kernel_info_reply`消息暴露给前端，前端据此决定语法高亮、文件保存格式等行为。

[F-040]

## do_execute 方法

`do_execute`是Kernel基类要求子类实现的核心方法，负责处理`execute_request`消息。

### 方法签名

```python
def do_execute(
    self,
    code: str,
    silent: bool,
    store_history=True,
    user_expressions=None,
    allow_stdin=False,
    *,
    cell_id=None,
) -> dict[str, typing.Any]:
```

### 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| `code` | str | 要执行的代码字符串（用户输入） |
| `silent` | bool | 是否静默执行（静默时不广播输出） |
| `store_history` | bool | 是否将执行记录存入历史（EchoKernel忽略此参数） |
| `user_expressions` | dict | 用户表达式（EchoKernel忽略） |
| `allow_stdin` | bool | 是否允许内核向前端请求输入 |
| `cell_id` | str\|None | 单元格ID（EchoKernel忽略） |

### 执行流程

```
do_execute(code, silent, ...)
│
├── silent == False?
│   ├── YES:
│   │   ├── 构造stream消息: {"name": "stdout", "text": code}
│   │   ├── self.send_response(self.iopub_socket, "stream", stream_content)
│   │   │   └── 将code原样发送到iopub通道的stdout流
│   │   └── allow_stdin == True AND code包含"input("?
│   │       └── YES: self._input_request("Echo Prompt", ...)
│   │           └── 向前端发送input_request消息
│   └── NO: 不发送任何输出
│
└── 返回执行结果字典:
    {
        "status": "ok",
        "execution_count": self.execution_count,
        "payload": [],
        "user_expressions": {},
    }
```

[F-041]

### 关键行为细节

1. **原样回显**：收到的`code`字符串直接作为stdout流内容发送，不做任何解析、编译或执行
2. **silent模式**：当`silent=True`时不发送任何输出（符合Jupyter协议规范）
3. **execution_count**：使用`self.execution_count`（基类维护的计数器），基类在每次执行后自动递增
4. **payload和user_expressions**：返回空列表/字典（EchoKernel不支持这些高级特性）
5. **stdin输入**：仅当`allow_stdin=True`且代码中包含`"input("`字符串时才触发input_request

### stdin输入处理

EchoKernel的stdin处理非常简单——它不真正读取输入，只是演示如何发送input_request消息：

```python
if allow_stdin and code and code.find("input(") != -1:
    self._input_request(
        "Echo Prompt",
        self._parent_ident["shell"],
        self.get_parent(channel="shell"),
        password=False,
    )
```

- 提示文本固定为`"Echo Prompt"`
- `password=False`表示输入不需要隐藏（不是密码输入）
- 这个检测是基于字符串匹配的（`code.find("input(")`），非常简陋但足以测试stdin通道是否工作

[F-041]

## EchoKernelApp启动类

```python
class EchoKernelApp(IPKernelApp):
    kernel_class = EchoKernel
```

`EchoKernelApp`继承自`IPKernelApp`，只覆盖了`kernel_class`属性指向`EchoKernel`。这复用了IPKernelApp的完整启动逻辑：

1. 解析命令行参数（特别是`-f {connection_file}`）
2. 读取连接文件（ZMQ端口、签名密钥等）
3. 创建ZMQ通道（shell、iopub、stdin、control、hb）
4. 启动心跳线程
5. 进入事件循环等待消息

通过复用IPKernelApp，EchoKernel无需重新实现任何通信层代码。

[F-042]

## 模块入口

```python
if __name__ == "__main__":
    logging.disable(logging.ERROR)
    EchoKernelApp.launch_instance()
```

当作为模块直接运行时（`python -m pytest_jupyter.echo_kernel`）：
1. 禁用ERROR级别以下的日志输出，减少测试噪声
2. 调用`EchoKernelApp.launch_instance()`启动内核应用

[F-043]

## kernel.json（kernelspec）

`echo_kernel_spec` fixture安装的kernelspec内容如下：

```json
{
    "argv": ["python", "-m", "pytest_jupyter.echo_kernel", "-f", "{connection_file}"],
    "display_name": "echo",
    "language": "echo"
}
```

- `argv`：启动内核的命令行，`{connection_file}`由Jupyter在启动时替换为实际连接文件路径
- `display_name`：前端显示的内核名称
- `language`：语言标识

这个kernel.json被`echo_kernel_spec` fixture写入`{jp_data_dir}/kernels/echo/kernel.json`，在隔离的测试环境中注册为可用内核。

[F-023]

## 使用示例

### 基本使用：启动echo内核

```python
async def test_echo(jp_start_kernel):
    # 启动echo内核
    km, kc = await jp_start_kernel("echo")

    # 发送执行请求
    msg = await kc.execute("hello world", reply=True)
    assert msg["content"]["status"] == "ok"

    # 在iopub上接收输出
    output_msg = await kc.get_iopub_msg()
    # output_msg["content"]["text"] == "hello world"
```

### 对比：使用默认Python内核

```python
async def test_python_kernel(jp_start_kernel):
    # 启动默认的python3内核（NATIVE_KERNEL_NAME）
    km, kc = await jp_start_kernel()  # 不传参数
    msg = await kc.execute("print(2+2)", reply=True)
    assert msg["content"]["status"] == "ok"
    # 输出将包含 "4"
```

### 直接实例化测试（不走ZMQ）

```python
from unittest.mock import Mock
from jupyter_client.session import Session
from pytest_jupyter.echo_kernel import EchoKernel

def test_echo_kernel_direct():
    kernel = EchoKernel()
    kernel.session = Mock(spec=Session)
    result = kernel.do_execute("foo", False)
    assert result["status"] == "ok"
    # 可以用mock验证send_response被调用
```

## 扩展EchoKernel

你可以基于EchoKernel创建自定义的测试内核：

```python
from pytest_jupyter.echo_kernel import EchoKernel, EchoKernelApp

class CountingKernel(EchoKernel):
    """一个计数内核，执行时返回执行次数"""
    implementation = "Counting"
    language = "counting"
    banner = "Counting kernel"

    def do_execute(self, code, silent, **kwargs):
        if not silent:
            count_text = f"Execution #{self.execution_count}: {code}"
            stream_content = {"name": "stdout", "text": count_text}
            self.send_response(self.iopub_socket, "stream", stream_content)
        return {
            "status": "ok",
            "execution_count": self.execution_count,
            "payload": [],
            "user_expressions": {},
        }

class CountingKernelApp(EchoKernelApp):
    kernel_class = CountingKernel
```

## EchoKernel的局限

1. **不执行代码**：它只是回显，无法验证代码逻辑
2. **不支持completion/inspect**：`do_complete`、`do_inspect`等方法使用基类默认实现（返回空结果）
3. **不支持display_data**：只发送stream消息，不支持富文本输出
4. **stdin检测简陋**：基于字符串匹配`"input("`，不解析AST
5. **不支持历史记录**：`store_history`参数被忽略

这些局限在测试场景中通常是可接受的——如果需要这些功能，应该使用真实的IPython内核。

---

**下一步阅读：**
- [Client插件详解](04-client-plugin.md) — 如何使用jp_start_kernel启动内核
- [Fixture工厂模式](08-fixture-factories.md) — 工厂fixtures的设计模式
- [示例：内核测试](../examples/02-kernel-testing.md) — 更多内核测试代码示例
