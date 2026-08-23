---
type: Concept
title: Cli 驱动详解
description: Cli 类的完整方法参考——连接生命周期、命令发送、模式管理、提示符获取、回调读取、定义替换
tags: [scrapli, cli, driver, send-input, modes, lifecycle]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:grep-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: scrapli-source
    resource: /references/scrapli-source.md
---

# Cli 驱动详解

`Cli` 类是 scrapli2 面向网络设备命令行的核心驱动。它封装了连接管理、命令发送、模式切换和结果获取。

## 连接生命周期

### open / close

```python
cli = Cli(host="192.168.1.1", auth_options=AuthOptions(username="admin", password="admin"))
cli.open()
result = cli.send_input("show version")
cli.close()
```

两个方法都返回 `Result` 对象，接受可选的 `operation_timeout_ns` 和 `cancel` 参数：

```python
from scrapli.ffi_types import Cancel

cancel = Cancel()
result = cli.open(operation_timeout_ns=30_000_000_000, cancel=cancel)
```

`close()` 额外接受 `force: bool = False` 参数，设为 True 时跳过 on_exit 指令直接关闭：

```python
cli.close(force=True)
```

### 上下文管理器

```python
with Cli(host="...", auth_options=...) as cli:
    cli.send_input("show version")
```

异步版本：

```python
async with Cli(host="...", auth_options=...) as cli:
    await cli.send_input_async("show version")
```

### 内部状态

`Cli` 实例维护以下关键内部状态：

| 属性 | 类型 | 说明 |
|------|------|------|
| `ptr` | `DriverPointer \| None` | Zig 层 Cli 对象的指针（`c_void_p`） |
| `poll_fd` | `int` | 用于轮询操作完成的文件描述符 |
| `host` | `str` | 主机地址 |
| `port` | `int` | 端口 |
| `logger` | `Logger` | Python logger 实例 |

未打开连接时调用操作方法会抛出 `NotOpenedException`。

## 命令发送

### send_input

发送单条命令：

```python
result = cli.send_input(
    "show version",
    requested_mode="",
    input_handling=InputHandling.FUZZY,
    retain_input=False,
    retain_trailing_prompt=False,
)
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `input_` | `str` | 必填 | 要发送的命令 |
| `requested_mode` | `str` | `""` | 在指定模式下发送 |
| `input_handling` | `InputHandling` | `FUZZY` | 输入匹配模式 |
| `retain_input` | `bool` | `False` | 结果中保留输入命令 |
| `retain_trailing_prompt` | `bool` | `False` | 结果中保留尾部提示符 |

### send_inputs

批量发送多条命令：

```python
result = cli.send_inputs(
    ["show version", "show interfaces", "show ip route"],
    stop_on_indicated_failure=True,
)
```

与 `send_input` 共享相同参数，额外支持：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `inputs` | `list[str]` | 必填 | 命令列表 |
| `stop_on_indicated_failure` | `bool` | `True` | 检测到失败指示器时停止后续命令 |

`send_inputs` 的 `operation_timeout_ns` 是整个批量操作的总超时，而非每条命令单独超时。

### send_inputs_from_file

从文件读取命令（每行一条）：

```python
result = cli.send_inputs_from_file("commands.txt")
```

文件路径通过 `resolve_file()` 解析，支持 `~` 用户目录展开。尾部换行符自动忽略。内部调用 `send_inputs()`。

### send_prompted_input

发送需要交互式响应的命令（如 enable 密码提示）：

```python
result = cli.send_prompted_input(
    input_="enable",
    prompt="Password:",
    prompt_pattern="",
    response="enable_password",
    abort_input="",
    hidden_response=True,
)
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `input_` | `str` | 要发送的初始命令 |
| `prompt` | `str` | 精确匹配的提示符文本 |
| `prompt_pattern` | `str` | 正则匹配的提示符模式 |
| `response` | `str` | 对提示符的响应 |
| `abort_input` | `str` | 出错时发送的中止输入 |
| `hidden_response` | `bool` | 响应是否隐藏（如密码输入） |
| `retain_trailing_prompt` | `bool` | 保留尾部提示符 |

`prompt` 和 `prompt_pattern` 必须设置其中一个。

## 低级读写

### read

直接从会话缓冲区读取字节，绕过操作循环：

```python
data = cli.read(size=1024)
```

此方法不执行 IO（仅排空已填充的缓冲区），因此无异步版本。返回 `bytes`，无数据时返回空字节。

### write / write_and_return / write_return

```python
cli.write("some input")           # 写入文本，不发送回车
cli.write_and_return("command")   # 写入文本并发送回车
cli.write_return()                # 仅发送回车字符
```

这些是低级写入方法，不返回 Result，也不等待操作完成。

## 模式管理

### enter_mode

切换到 YAML 定义中声明的模式：

```python
result = cli.enter_mode("privileged_exec")
result = cli.enter_mode("configuration")
```

平台定义 YAML 中声明了模式名称、提示符正则和模式间切换指令。`enter_mode` 触发 Zig 层自动执行模式切换指令序列。

### get_prompt

获取设备当前提示符：

```python
result = cli.get_prompt()
print(result.result)
```

### replace_definition

运行时替换平台定义：

```python
cli.replace_definition("cisco_iosxr")
```

这会重新加载 YAML 定义并更新 Zig 层的提示符模式和模式配置，适用于设备在连接后切换操作系统模式的场景。

## read_with_callbacks

`read_with_callbacks` 提供基于回调的交互式读取能力，适合处理多步交互场景：

```python
from scrapli import ReadCallback

def handle_confirmation(cli, recent_output, full_output):
    cli.write_and_return("y")

callbacks = [
    ReadCallback(
        name="confirm",
        contains="Confirm?",
        callback=handle_confirmation,
        once=True,
        completes=False,
    ),
    ReadCallback(
        name="done",
        contains_pattern=r"#\s*$",
        callback=lambda c, r, f: None,
        completes=True,
    ),
]

result = cli.read_with_callbacks(
    callbacks,
    initial_input="reload",
)
```

### ReadCallback 字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `name` | `str` | 必填 | 回调友好名称 |
| `contains` | `str` | `""` | 触发回调的包含字符串 |
| `contains_pattern` | `str` | `""` | 触发回调的 PCRE2 正则 |
| `not_contains` | `str` | `""` | 取消触发的排除字符串 |
| `search_depth` | `int` | `0` | 在历史结果中向后搜索的深度（0=仅最后一次读取） |
| `once` | `bool` | `False` | 是否只执行一次 |
| `completes` | `bool` | `False` | 执行后是否结束整个读取操作 |
| `callback` | `Callable` | `None` | 同步回调函数 `(Cli, str, str) -> None` |
| `callback_async` | `Callable` | `None` | 异步回调函数 `(Cli, str, str) -> Awaitable[None]` |

约束：
- `contains` 和 `contains_pattern` 必须至少设置一个
- `callback` 和 `callback_async` 必须至少设置一个
- 异步版本（`read_with_callbacks_async`）必须使用 `callback_async`

回调函数接收三个参数：Cli 实例、匹配位置开始的输出片段、完整输出。

## Result 对象使用

`send_input` 等方法返回的 `Result` 对象提供：

```python
result = cli.send_input("show version")

result.result              # 清理后的输出文本
result.results             # list[str]，各命令结果
result.failed              # bool，是否失败
result.elapsed_time_seconds  # float，耗时
result.results_raw         # list[bytes]，原始字节（延迟重构）
result.inputs              # list[str]，发送的命令
result.host                # str，主机
result.port                # int，端口

result.textfsm_parse()    # TextFSM 结构化解析
result.genie_parse()       # Genie 结构化解析
```

### TextFSM 解析

```python
parsed = result.textfsm_parse()
# 返回 list[dict]，使用平台对应的 ntc-templates 模板

parsed = result.textfsm_parse(template="/path/to/template.textfsm")
# 指定自定义模板
```

需要安装 `textfsm` 和 `ntc_templates` 包。模板自动根据 `Cli.ntc_templates_platform` 属性和输入命令匹配。

### Genie 解析

```python
parsed = result.genie_parse()
# 返回 dict 或 list，使用 Cisco genie parser
```

需要安装 `genie` 包。平台通过 `Cli.genie_platform` 属性确定。

## 取消操作

`Cancel` 对象支持在操作进行中取消：

```python
from scrapli.ffi_types import Cancel

cancel = Cancel()
result = cli.send_input("long running command", cancel=cancel)

# 在另一个线程中：
cancel.cancel()
```

取消后 Zig 层中止操作，Python 侧抛出 `CancelledException`。
