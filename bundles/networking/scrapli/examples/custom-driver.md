---
type: Example
title: 自定义平台定义与高级用法
description: 创建自定义 YAML 平台定义、LoadedDefinition、平台钩子、会话录制、回调读取、replace_definition
tags: [scrapli, example, custom, yaml, definition, callback]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:grep-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: scrapli-source
    resource: /references/scrapli-source.md
---

# 自定义平台定义与高级用法

本例演示自定义 YAML 平台定义、`LoadedDefinition`、回调读取和会话录制等高级功能。

## 从 YAML 文件加载自定义定义

创建 `my_device.yaml`：

```yaml
---
prompt_pattern: '^.*[>#$]\s?+$'
default_mode: 'cli'
modes:
  - name: 'cli'
    prompt_pattern: '^.*[>#$]\s?+$'
    accessible_modes:
      - name: 'config'
        instructions:
          - send_input:
              input: 'configure'
  - name: 'config'
    prompt_pattern: '^.*\(config\)#\s?+$'
    accessible_modes:
      - name: 'cli'
        instructions:
          - send_input:
              input: 'exit'
failure_indicators:
  - 'Error:'
  - 'Invalid input'
  - 'Unknown command'
on_open_instructions:
  - send_input:
      input: 'set cli screen-length 0'
  - send_input:
      input: 'set cli screen-width 512'
on_close_instructions:
  - write:
      input: 'exit'
ntc_templates_platform: 'my_device'
genie_platform: ''
```

使用自定义定义：

```python
from scrapli import Cli, AuthOptions

with Cli(
    host="192.168.1.1",
    definition_file_or_name="/path/to/my_device.yaml",
    auth_options=AuthOptions(username="admin", password="admin"),
) as cli:
    result = cli.send_input("show system info")
    print(result.result)
```

## 使用 LoadedDefinition（内联定义）

```python
from scrapli import Cli, AuthOptions, LoadedDefinition

custom_yaml = """
---
prompt_pattern: '^.*[>#$]\\s?+$'
default_mode: 'cli'
modes:
  - name: 'cli'
    prompt_pattern: '^.*[>#$]\\s?+$'
on_close_instructions:
  - write:
      input: 'exit'
"""

definition = LoadedDefinition(
    platform_name="my_inline_device",
    definition=custom_yaml,
)

with Cli(
    host="192.168.1.1",
    definition_file_or_name=definition,
    auth_options=AuthOptions(username="admin", password="admin"),
) as cli:
    result = cli.send_input("show version")
    print(result.result)
```

## 使用 LookupKeyValue 模板变量

平台定义中使用 `__lookup::key` 引用敏感值：

```yaml
on_open_instructions:
  - send_prompted_input:
      input: 'enable'
      prompt_exact: 'Password:'
      response: '__lookup::enable_password'
```

Python 代码传入查找值：

```python
from scrapli import Cli, AuthOptions, LookupKeyValue

auth = AuthOptions(
    username="admin",
    password="login_pass",
    lookups=[
        LookupKeyValue(key="enable_password", value="secret_enable_pass"),
        LookupKeyValue(key="snmp_community", value="public"),
    ],
)

with Cli(
    host="192.168.1.1",
    definition_file_or_name="my_device.yaml",
    auth_options=auth,
) as cli:
    result = cli.send_input("show running-config")
```

## 运行时替换定义

`replace_definition()` 在连接建立后切换平台定义：

```python
with Cli(
    host="192.168.1.1",
    definition_file_or_name="cisco_iosxe",
    auth_options=AuthOptions(username="admin", password="admin"),
) as cli:
    result = cli.send_input("show version")
    print("IOS-XE:", result.result[:100])

    cli.replace_definition("cisco_iosxr")
    result = cli.send_input("show version")
    print("IOS-XR:", result.result[:100])
```

## 回调读取（交互式命令）

处理需要确认的命令（如 reload）：

```python
from scrapli import Cli, AuthOptions, ReadCallback

def handle_reload_confirm(cli, recent_output, full_output):
    cli.write_and_return("y")

callbacks = [
    ReadCallback(
        name="confirm",
        contains="Proceed with reload? [confirm]",
        callback=handle_reload_confirm,
        once=True,
        completes=True,
    ),
]

with Cli(
    host="192.168.1.1",
    definition_file_or_name="cisco_iosxe",
    auth_options=AuthOptions(username="admin", password="admin"),
) as cli:
    result = cli.read_with_callbacks(
        callbacks,
        initial_input="reload",
        operation_timeout_ns=60_000_000_000,
    )
    print(result.result)
```

### 多回调链式处理

```python
callbacks = [
    ReadCallback(
        name="more_prompt",
        contains="--More--",
        callback=lambda c, r, f: c.write(" "),
        once=False,
        completes=False,
    ),
    ReadCallback(
        name="command_complete",
        contains_pattern=r"[\w-]+#\s*$",
        callback=lambda c, r, f: None,
        completes=True,
    ),
]

result = cli.read_with_callbacks(
    callbacks,
    initial_input="show running-config",
)
```

## 会话录制

录制完整的会话交互到文件：

```python
from scrapli import Cli, AuthOptions, SessionOptions

with Cli(
    host="192.168.1.1",
    auth_options=AuthOptions(username="admin", password="admin"),
    session_options=SessionOptions(
        recorder_path="/tmp/router_session.log",
    ),
) as cli:
    cli.send_input("show version")
    cli.send_input("show interfaces")
```

或使用回调实时处理：

```python
def record(data: str) -> None:
    with open("session.log", "a") as f:
        f.write(data)
    print(f"[SESSION] {len(data)} bytes")

with Cli(
    host="192.168.1.1",
    auth_options=AuthOptions(username="admin", password="admin"),
    session_options=SessionOptions(recorder_callback=record),
) as cli:
    cli.send_input("show version")
```

## 环境变量覆盖

### 自定义平台定义目录

```bash
export SCRAPLI_DEFINITIONS_PATH=/opt/scrapli/definitions
```

```python
cli = Cli(
    host="192.168.1.1",
    definition_file_or_name="my_custom_platform",
    auth_options=AuthOptions(username="admin", password="admin"),
)
```

### 自定义 libscrapli 路径

```bash
export LIBSCRAPLI_PATH=/opt/scrapli/libscrapli-x86_64-linux-gnu.so.0.0.1-rc.35
```

## 配置选项导出（调试）

```python
cli = Cli(
    host="192.168.1.1",
    definition_file_or_name="cisco_iosxe",
    auth_options=AuthOptions(username="admin", password="admin"),
)

import json
options = json.loads(cli._get_options())
print(json.dumps(options, indent=2))
```

## 跳过平台特定钩子

某些平台有 Python 后初始化钩子（如 MikroTik 自动修改用户名），可通过 `skip_static_options=True` 跳过：

```python
cli = Cli(
    host="192.168.1.1",
    definition_file_or_name="mikrotik_routeros",
    auth_options=AuthOptions(username="admin", password="admin"),
    skip_static_options=True,
)
```

## Cli 对象复制

使用 `copy.copy()` 安全复制 Cli 配置（用于并行任务）：

```python
import copy

template = Cli(
    host="192.168.1.1",
    auth_options=AuthOptions(username="admin", password="admin"),
)

cli1 = copy.copy(template)
cli2 = copy.copy(template)
```

相关文档：
- [平台定义系统](../concepts/06-platform-definitions.md)
- [高级模式](../concepts/08-advanced-patterns.md)
- [Cli 驱动详解](../concepts/04-cli-driver.md)
