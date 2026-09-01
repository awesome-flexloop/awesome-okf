---
type: Example
title: 单条与批量命令发送
description: send_input、send_inputs、send_inputs_from_file 的用法，失败处理、模式切换、提示输入
tags: [scrapli, example, send-input, batch, commands]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:grep-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: scrapli-source
    resource: /references/scrapli-source.md
---

# 单条与批量命令发送

本例演示 `Cli` 的各种命令发送方式。

## 单条命令

```python
from scrapli import Cli, AuthOptions

with Cli(
    host="192.168.1.1",
    definition_file_or_name="cisco_iosxe",
    auth_options=AuthOptions(username="admin", password="admin"),
) as cli:
    result = cli.send_input("show version")
    print(result.result)
```

### 保留输入和提示符

```python
result = cli.send_input(
    "show version",
    retain_input=True,
    retain_trailing_prompt=True,
)
print(result.result)
```

### 指定模式发送

```python
result = cli.send_input(
    "show running-config",
    requested_mode="privileged_exec",
)
```

### 操作级超时

```python
result = cli.send_input(
    "ping 192.168.1.100 repeat 1000",
    operation_timeout_ns=120_000_000_000,
)
```

## 批量命令

```python
commands = [
    "show version",
    "show interfaces description",
    "show ip route summary",
    "show running-config | section interface",
]

result = cli.send_inputs(commands)

for i, output in enumerate(result.results):
    print(f"=== {commands[i]} ===")
    print(output)
    print()
```

### 失败时停止

`send_inputs` 默认 `stop_on_indicated_failure=True`。当某条命令的输出匹配平台定义中的 `failure_indicators` 时，停止发送后续命令：

```python
result = cli.send_inputs(
    ["valid command", "invalid command", "this won't be sent"],
    stop_on_indicated_failure=True,
)
```

Cisco IOS-XE 的失败指示器包括：
- `% Ambiguous command`
- `% Incomplete command`
- `% Invalid input detected`
- `% Unknown command`
- `Command authorization failed`

设为 False 可继续执行所有命令：

```python
result = cli.send_inputs(commands, stop_on_indicated_failure=False)
```

## 从文件发送命令

`commands.txt`：

```text
show version
show interfaces description
show ip arp
show mac address-table
show running-config
```

```python
result = cli.send_inputs_from_file("commands.txt")
print(result.result)
```

文件路径支持 `~` 用户目录展开。每行作为一条命令，尾部换行符自动忽略。

## 检查结果

```python
result = cli.send_input("show version")

if result.failed:
    print("命令执行失败！")
    print(result.result)
else:
    print("命令执行成功")
    print(f"耗时: {result.elapsed_time_seconds:.2f}s")
    print(f"原始字节数: {len(result.result_raw)}")
```

## 配置模式命令

```python
with Cli(host="...", definition_file_or_name="cisco_iosxe", auth_options=auth) as cli:
    config_commands = [
        "interface GigabitEthernet0/1",
        "description Uplink to Core",
        "no shutdown",
        "exit",
    ]

    result = cli.send_inputs(
        config_commands,
        requested_mode="configuration",
    )

    if result.failed:
        print("配置失败!")
    else:
        cli.send_input("write memory")
        print("配置完成")
```

## 带提示的输入（enable 密码）

```python
result = cli.send_prompted_input(
    input_="enable",
    prompt="Password:",
    prompt_pattern="",
    response="enable_secret",
    hidden_response=True,
)
```

> 注意：使用平台定义（如 cisco_iosxe）时，`enter_mode("privileged_exec")` 和 `on_open_instructions` 会自动处理 enable 密码，通常无需手动调用 `send_prompted_input`。

## TextFSM 结构化输出

```python
result = cli.send_input("show interfaces")

parsed = result.textfsm_parse()
for entry in parsed:
    print(f"接口: {entry.get('interface')}, 状态: {entry.get('link_status')}")
```

需要安装 `textfsm` 和 `ntc-templates`。

## Genie 结构化输出

```python
result = cli.send_input("show version")
parsed = result.genie_parse()
print(f"版本: {parsed.get('version', {}).get('version')}")
```

需要安装 Cisco `genie` 包。

## 完整示例

```python
from scrapli import Cli, AuthOptions, SessionOptions

commands = [
    "show version",
    "show interfaces description",
    "show ip route",
]

with Cli(
    host="192.168.1.1",
    definition_file_or_name="cisco_iosxe",
    auth_options=AuthOptions(
        username="admin",
        password="admin",
    ),
    session_options=SessionOptions(
        operation_timeout_s=30,
    ),
) as cli:
    result = cli.send_inputs(commands)

    print(f"执行了 {len(result.inputs)} 条命令")
    print(f"总耗时: {result.elapsed_time_seconds:.2f}s")
    print(f"失败: {result.failed}")

    for cmd, output in zip(result.inputs, result.results):
        print(f"\n{'='*60}")
        print(f"命令: {cmd}")
        print(f"{'='*60}")
        print(output)
```

相关文档：
- [Cli 驱动详解](../concepts/04-cli-driver.md)
- [平台定义系统](../concepts/06-platform-definitions.md)
