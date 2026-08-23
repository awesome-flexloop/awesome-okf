---
type: Concept
title: 高级模式
description: session_log 日志、global_delay_factor、fast_cli、TextFSM 解析、异常处理、并发连接
tags: [netmiko, advanced, session-log, textfsm, fast-cli, exception, threading]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: netmiko-source
    resource: /references/netmiko-source.md
---

# 高级模式

## 会话日志（session_log）

记录完整的设备交互会话到文件，用于调试和审计：

```python
conn = ConnectHandler(
    device_type="cisco_ios",
    host="10.0.0.1",
    username="admin",
    password="pass",
    session_log="session.log",              # 文件路径
    session_log_file_mode="write",          # "write"（覆盖）或 "append"（追加）
    session_log_record_writes=False,        # 是否同时记录发送的命令
)
```

session_log 支持三种类型：
- **字符串**：文件路径，netmiko 自动打开和关闭
- **文件对象/BufferedIOBase**：已打开的文件句柄或内存缓冲区
- **SessionLog 对象**：自定义 SessionLog 实例

密码和 secret 会自动通过 `SecretsFilter` 替换为 `********`，不会写入日志。

```python
import io

# 输出到内存缓冲区
buffer = io.StringIO()
conn = ConnectHandler(..., session_log=buffer)
conn.send_command("show version")
print(buffer.getvalue())  # 获取完整会话内容
```

## 延迟与超时控制

### global_delay_factor

全局延迟因子影响 netmiko 内部所有 sleep 操作：

```python
# 慢速设备：增大延迟（更可靠但更慢）
conn = ConnectHandler(..., global_delay_factor=2.0)

# 快速设备：减小延迟（更快但可能不稳定）
conn = ConnectHandler(..., global_delay_factor=0.1)
```

### fast_cli

`fast_cli=True`（默认）会：
- 将 `global_delay_factor` 默认设为 0.1
- `select_delay_factor()` 取 delay_factor 和 global_delay_factor 的**较小值**
- 适用于响应快速的现代设备

`fast_cli=False` 时：
- `global_delay_factor` 默认 1.0
- `select_delay_factor()` 取**较大值**
- 适用于慢速或不稳定的设备

```python
# 保守模式，适合慢速设备
conn = ConnectHandler(..., fast_cli=False, global_delay_factor=1.0)
```

### delay_factor_compat

设置 `delay_factor_compat=True` 恢复 Netmiko 3.x 的延迟行为（在 5.x 中将被移除）。

### read_timeout_override

覆盖 send_command 和 send_command_timing 的默认 read_timeout：

```python
conn = ConnectHandler(..., read_timeout_override=30.0)
# 所有命令默认使用30秒读取超时
```

## TextFSM 输出解析

TextFSM 将非结构化 CLI 输出解析为结构化数据（列表的字典）：

```bash
pip install textfsm
```

```python
# 基本用法
interfaces = conn.send_command("show ip interface brief", use_textfsm=True)
for intf in interfaces:
    print(f"{intf['intf']}: {intf['ipaddr']} ({intf['status']})")

# 指定自定义模板
output = conn.send_command(
    "show version",
    use_textfsm=True,
    textfsm_template="/path/to/template.textfsm",
)
```

TextFSM 模板查找顺序：
1. `textfsm_template` 参数指定的路径
2. 当前目录下的模板文件
3. ntc-templates 包（如果已安装）

### ntc-templates

安装网络设备 TextFSM 模板集合：

```bash
pip install ntc-templates
```

安装后，netmiko 自动从 ntc-templates 查找模板，无需指定路径。

## TTP 解析

TTP（Template Text Parser）是另一个模板解析引擎：

```bash
pip install ttp
```

```python
output = conn.send_command(
    "show interfaces description",
    use_ttp=True,
    ttp_template="path/to/template.txt",
)
```

也可以使用 `run_ttp()` 方法直接运行 TTP 模板：

```python
result = conn.run_ttp(
    template="path/to/template.txt",
    commands=["show version", "show interfaces"],
)
```

## Genie/pyATS 解析

Cisco 的 Genie 解析器提供丰富的结构化输出：

```bash
pip install genie pyats
```

```python
version = conn.send_command("show version", use_genie=True)
print(version["version"]["hostname"])
```

Genie 主要支持 Cisco 平台（IOS、IOS XE、NX-OS、IOS XR）。

## 异常处理

```python
from netmiko import (
    ConnectHandler,
    NetmikoTimeoutException,
    NetmikoAuthenticationException,
    ReadException,
    ReadTimeout,
    ConfigInvalidException,
)

try:
    conn = ConnectHandler(
        device_type="cisco_ios",
        host="10.0.0.1",
        username="admin",
        password="wrong_password",
        conn_timeout=10,
    )
except NetmikoAuthenticationException:
    print("认证失败：用户名或密码错误")
except NetmikoTimeoutException as e:
    print(f"连接超时: {e}")
except ReadTimeout:
    print("命令执行超时")
    conn.disconnect()
```

### 异常层次

```
Exception
├── paramiko.ssh_exception.SSHException
│   └── NetmikoTimeoutException
├── paramiko.ssh_exception.AuthenticationException
│   └── NetmikoAuthenticationException
└── NetmikoBaseException
    ├── ConnectionException
    ├── ConfigInvalidException
    ├── WriteException
    └── ReadException
        ├── ReadTimeout
        └── NetmikoParsingException
```

## 并发连接

netmiko 的 `BaseConnection` 内置线程锁（`@lock_channel` 装饰器），但每个连接对象不应被多线程共享。正确做法是为每个设备创建独立连接，使用线程池并发：

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from netmiko import ConnectHandler

devices = [
    {"device_type": "cisco_ios", "host": "10.0.0.1", "username": "admin", "password": "pass"},
    {"device_type": "cisco_ios", "host": "10.0.0.2", "username": "admin", "password": "pass"},
    {"device_type": "arista_eos", "host": "10.0.0.3", "username": "admin", "password": "pass"},
]

def backup_config(device):
    with ConnectHandler(**device) as conn:
        hostname = conn.send_command("show version | include uptime", strip_prompt=False)
        config = conn.send_command("show running-config")
        return device["host"], config

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = {executor.submit(backup_config, dev): dev for dev in devices}
    for future in as_completed(futures):
        host, config = future.result()
        with open(f"backup_{host}.cfg", "w") as f:
            f.write(config)
```

`session_timeout` 参数控制线程等待锁的超时时间（默认60秒）。

## SSH 密钥认证

```python
conn = ConnectHandler(
    device_type="cisco_ios",
    host="10.0.0.1",
    username="admin",
    use_keys=True,
    key_file="/home/user/.ssh/id_rsa",
    passphrase="key_passphrase",  # 可选
    # pkey=paramiko.RSAKey.from_private_key_file(...),  # 或直接传 PKey 对象
    allow_agent=True,              # 使用 SSH agent
)
```

## SSH 配置文件支持

利用 OpenSSH 配置文件（`~/.ssh/config`）：

```python
conn = ConnectHandler(
    device_type="cisco_ios",
    host="router1",
    username="admin",
    ssh_config_file="~/.ssh/config",
)
```

支持 `ProxyCommand` 和单跳 `ProxyJump`。

## 禁用算法

```python
conn = ConnectHandler(
    device_type="cisco_ios",
    host="10.0.0.1",
    username="admin",
    password="pass",
    disabled_algorithms={"pubkeys": ["rsa-sha2-256", "rsa-sha2-512"]},
    disable_sha2_fix=True,  # 修复 paramiko issue #1961
)
```

## 多行命令交互

`send_multiline()` 处理需要多轮交互的命令：

```python
result = conn.send_multiline(
    [
        ["copy running-config tftp:", r"Address of remote host"],
        ["10.0.0.2", r"Destination filename"],
        ["\n", r"#"],
    ]
)
```

每个元素是 `[command, expected_pattern]` 对，按顺序发送命令并等待模式。

## 保持连接

```python
conn = ConnectHandler(..., keepalive=30)  # 每30秒发送 SSH keepalive
```

设置 `keepalive` 参数（秒）后，netmiko 调用 paramiko `transport.set_keepalive()` 发送保活包，防止连接被中间设备超时断开。
