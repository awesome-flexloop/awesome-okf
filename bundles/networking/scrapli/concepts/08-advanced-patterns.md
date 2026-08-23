---
type: Concept
title: 高级模式
description: 回调读取、提示输入、文件批量命令、Result 结构化解析、异常处理、FFI 架构深入、会话录制
tags: [scrapli, advanced, callbacks, ffi, exceptions, parsing]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:grep-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: scrapli-source
    resource: /references/scrapli-source.md
---

# 高级模式

## 回调读取（read_with_callbacks）

`read_with_callbacks` 是 scrapli2 中最灵活的交互机制。它持续读取设备输出，当输出匹配指定条件时执行回调函数，适合处理多步交互式场景（如确认提示、分页、自动应答）。

### 基本结构

```python
from scrapli import Cli, AuthOptions, ReadCallback

def on_confirm(cli, recent, full):
    cli.write_and_return("y")

def on_complete(cli, recent, full):
    pass

callbacks = [
    ReadCallback(
        name="confirm_reload",
        contains="Proceed with reload? [confirm]",
        callback=on_confirm,
        once=True,
    ),
    ReadCallback(
        name="prompt_return",
        contains_pattern=r"[\w-]+#\s*$",
        callback=on_complete,
        completes=True,
    ),
]

with Cli(host="...", auth_options=AuthOptions(username="admin", password="admin")) as cli:
    result = cli.read_with_callbacks(
        callbacks,
        initial_input="reload",
    )
```

### 匹配条件

每个 `ReadCallback` 支持两种匹配方式：

- **`contains`**：子字符串精确匹配（优先于 contains_pattern）
- **`contains_pattern`**：PCRE2 正则匹配（contains 为空时使用）
- **`not_contains`**：排除字符串，找到时取消本次匹配

`search_depth` 控制在累积结果中向后搜索的字符数。设为 0（默认）表示仅搜索最后一次读取的内容。

### 执行控制

- **`once=True`**：回调只执行一次，之后不再触发
- **`completes=True`**：回调执行后立即结束整个 read_with_callbacks 操作，返回累积的 Result
- 未设置 completes 的回调执行后继续循环读取

### 同步与异步回调

同步版本使用 `callback`：

```python
ReadCallback(
    name="handler",
    contains="Password:",
    callback=lambda cli, recent, full: cli.write_and_return("secret"),
)
```

异步版本必须使用 `callback_async`：

```python
async def async_handler(cli, recent, full):
    await asyncio.sleep(0.1)
    cli.write_and_return("y")

ReadCallback(
    name="handler",
    contains="Confirm?",
    callback_async=async_handler,
)
```

`ReadCallback.__post_init__` 强制要求至少设置一个匹配条件和一个回调函数，否则抛出 `OperationException`。

## 提示输入（send_prompted_input）

`send_prompted_input` 处理发送命令后需要响应提示的场景：

```python
result = cli.send_prompted_input(
    input_="enable",
    prompt="Password:",
    prompt_pattern="",
    response="enable_password",
    abort_input="",
    hidden_response=True,
    requested_mode="",
)
```

典型场景是 Cisco 设备的 `enable` 命令。平台 YAML 定义中的 `send_prompted_input` 指令在模式切换时自动使用此机制。

参数说明：

| 参数 | 说明 |
|------|------|
| `input_` | 初始发送的命令 |
| `prompt` | 精确匹配的提示符文本（与 prompt_pattern 二选一） |
| `prompt_pattern` | 正则匹配的提示符模式 |
| `response` | 对提示符的响应文本 |
| `abort_input` | 出错时发送的中止输入 |
| `hidden_response` | True 时响应不回显（如密码输入） |

## 从文件批量发送命令

```python
result = cli.send_inputs_from_file("commands.txt")
```

文件中每行作为一条命令，尾部换行符被忽略。内部通过 `resolve_file()` 解析路径（支持 `~` 展开），然后调用 `send_inputs()`。

文件示例 `commands.txt`：

```
show version
show interfaces description
show ip route summary
show running-config | section interface
```

## 低级读写操作

除了高级的 send_input 系列方法，Cli 还提供底层读写：

```python
cli.write("command without newline")
cli.write_and_return("command with newline")
cli.write_return()

data = cli.read(size=4096)
```

这些方法绕过操作循环和结果等待机制，直接通过 FFI 调用 Zig 层的 session read/write。`read()` 不执行实际 IO，仅排空已由 Zig 层填充的缓冲区。

## Result 结构化解析

CLI Result 对象集成了两种结构化解析引擎：

### TextFSM 解析

```python
result = cli.send_input("show interfaces")

parsed = result.textfsm_parse()
# 返回 list[dict]，自动使用平台对应的 ntc-templates 模板

parsed = result.textfsm_parse(
    template="/path/to/custom.template",
    to_dict=True,
)
```

需要安装可选依赖：

```bash
pip install textfsm ntc-templates
```

模板查找基于 `Cli.ntc_templates_platform` 属性（从 YAML 定义的 `ntc_templates_platform` 字段获取）和输入的命令文本。

### Genie 解析

```python
result = cli.send_input("show version")
parsed = result.genie_parse()
# 返回 dict
```

需要安装 Cisco genie：

```bash
pip install genie
```

平台通过 `Cli.genie_platform` 属性确定（从 YAML 定义的 `genie_platform` 字段获取）。

### Result 合并

多个 Result 对象可以合并：

```python
result1 = cli.send_input("show version")
result2 = cli.send_input("show interfaces")
result1.extend(result2)
```

`extend()` 合并 inputs、results、splits 和 raw journals，并清除缓存的原始输出以触发重构。

## 异常处理

scrapli2 定义了完整的异常层次：

```
ScrapliException
├── LibScrapliException      # 共享库加载失败
├── OptionsException         # 选项配置错误
├── AllocationException      # Zig 对象分配失败
├── FFIException             # FFI 边界错误（包装下层异常）
├── NotOpenedException       # 未连接时调用操作
├── OperationException       # 操作返回错误
├── ParsingException         # 输出解析失败
├── NoMessagesException      # NETCONF 无通知消息
├── OutOfMememoryException   # 内存不足（同时继承 MemoryError）
├── EOFException             # 连接 EOF（同时继承 EOFError）
├── CancelledException       # 操作被取消
├── TimeoutException         # 操作超时（同时继承 TimeoutError）
├── DriverException          # 驱动层错误
├── SessionException         # 会话层错误
├── TransportException       # 传输层错误
└── InvalidArgumentException # 无效参数
```

### 典型异常处理模式

```python
from scrapli.exceptions import (
    NotOpenedException,
    OperationException,
    TimeoutException,
    CancelledException,
    FFIException,
)

try:
    with Cli(host="...", auth_options=auth) as cli:
        result = cli.send_input("show version", operation_timeout_ns=5_000_000_000)
except TimeoutException:
    print("操作超时")
except OperationException as e:
    print(f"设备返回错误: {e}")
except FFIException as e:
    print(f"FFI/连接错误: {e}")
except NotOpenedException:
    print("连接未打开")
```

`result.failed` 属性可用于检查设备返回的失败指示器（不抛异常）：

```python
result = cli.send_input("show run")
if result.failed:
    print(f"命令可能失败，输出: {result.result}")
```

## FFI 架构深入

### ZigSlice 数据交换

Python 与 Zig 之间通过 `ZigSlice` 结构体传递字节数据：

```python
class ZigSlice(Structure):
    _fields_ = [
        ("ptr", POINTER(c_uint8)),
        ("len", c_size_t),
    ]
```

所有字符串在跨 FFI 边界时编码为 UTF-8 字节，通过 `to_c_string()` 转换为 `c_char_p`。返回数据时 Zig 写入预分配的 ZigSlice 缓冲区，Python 通过 `get_contents()` / `get_decoded_contents()` 读取。

### 操作执行模型

1. Python 调用 FFI 函数（如 `ls_cli_send_input`），Zig 返回 operation_id
2. Zig 在后台执行操作，完成后向 poll fd 写入 4 字节 operation_id
3. Python 轮询 poll fd（同步用 select，异步用 asyncio.add_reader）
4. 收到匹配的 operation_id 后，Python 调用 `fetch_sizes` 获取各缓冲区大小
5. Python 分配缓冲区，调用 `fetch` 获取实际数据
6. 如有错误，抛出 `OperationException`

### 操作超时机制

`handle_operation_timeout` 装饰器在操作前通过 FFI 设置 Zig 层的 `operation_timeout_ns`，在 `finally` 块中无条件重置为 SessionOptions 的默认值。超时由 Zig 层原生检测和处理，而非 Python 侧定时器。

### Cancel 取消机制

`Cancel` 对象包装 `c_bool`，通过指针传递给 Zig。Python 侧调用 `cancel.cancel()` 将值设为 True，Zig 在操作循环中检测并中止。异步模式下，asyncio 任务取消会自动触发 Cancel。

## 会话录制

SessionOptions 支持录制完整的会话交互：

```python
from scrapli import SessionOptions

session = SessionOptions(
    recorder_path="/tmp/session.log",
)
```

或使用回调函数实时处理：

```python
def on_session_data(data: str) -> None:
    with open("session.log", "a") as f:
        f.write(data)

session = SessionOptions(recorder_callback=on_session_data)
```

录制通过 ctypes 回调函数（`RecorderCallbackC`）从 Zig 层接收数据，包含所有读取和写入的原始内容。

## 日志配置

scrapli2 使用 Python 标准 logging 模块。Logger 名称格式为 `scrapli.cli.{host}:{port}` 或 `scrapli.netconf.{host}:{port}`，可附加 `logging_uid`：

```python
import logging
logging.basicConfig(level=logging.DEBUG)

cli = Cli(
    host="192.168.1.1",
    auth_options=AuthOptions(username="admin", password="admin"),
    logging_uid="router1",
)
# logger 名称: scrapli.cli.192.168.1.1:22:router1
```

Zig 层的日志通过 `ffi_logger_callback_wrapper` 回调传递到 Python logger，支持 6 个级别（trace/debug/info/warning/critical/fatal）。

## 配置调试（JSON 选项导出）

`Cli._get_options()` 和 `Netconf._get_options()` 将所有选项序列化为 JSON 字符串，可用于调试配置：

```python
cli = Cli(host="...", auth_options=...)
options_json = cli._get_options()
print(options_json)
```

跨束参考：
- [paramiko 高级模式](../../paramiko/concepts/10-advanced-patterns.md) — paramiko 的 ProxyCommand、连接池等高级用法
- [asyncssh 高级模式](../../asyncssh/concepts/11-advanced-patterns.md) — asyncssh 的高级特性
