---
type: Example
title: 基础连接与命令发送
description: 使用 Cli 连接网络设备、发送 show 命令、处理 Result 对象的完整示例
tags: [scrapli, example, cli, connect, basic]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:grep-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: scrapli-source
    resource: /references/scrapli-source.md
---

# 基础连接与命令发送

本例演示使用 scrapli2 的 `Cli` 类连接 Cisco IOS-XE 设备并执行命令。

## 同步连接

```python
from scrapli import Cli, AuthOptions, TransportBinOptions

with Cli(
    host="192.168.1.1",
    definition_file_or_name="cisco_iosxe",
    auth_options=AuthOptions(
        username="admin",
        password="admin",
        lookups=[
            LookupKeyValue(key="enable", value="enable_password"),
        ],
    ),
    transport_options=TransportBinOptions(
        ssh_config_path="~/.ssh/config",
    ),
) as cli:
    result = cli.send_input("show version")

    print(f"主机: {result.host}:{result.port}")
    print(f"耗时: {result.elapsed_time_seconds:.2f}s")
    print(f"失败: {result.failed}")
    print("---")
    print(result.result)
```

## 逐行说明

1. **创建 Cli 对象**：`host` 是唯一必填参数，通过关键字参数传入平台名、认证和传输配置
2. **`definition_file_or_name="cisco_iosxe"`**：加载内置的 Cisco IOS-XE 平台定义，自动处理 enable 模式切换、term width/len 设置
3. **`AuthOptions`**：配置用户名和密码，`lookups` 中的 enable 密码供平台定义的 `__lookup::enable` 模板引用
4. **`TransportBinOptions`**：使用系统 SSH 客户端，复用 `~/.ssh/config` 中的配置
5. **`with` 语句**：自动调用 `open()` 和 `close()`，连接打开时平台定义的 `on_open_instructions` 自动执行（进入特权模式、设置 term width 512、term len 0）
6. **`send_input("show version")`**：发送命令，Zig 层自动匹配提示符并返回清理后的输出
7. **Result 对象**：包含主机、端口、耗时、失败状态和输出文本

## 使用 SSH2 传输（libssh2）

```python
from scrapli import Cli, AuthOptions, TransportSsh2Options

with Cli(
    host="192.168.1.1",
    definition_file_or_name="cisco_iosxe",
    auth_options=AuthOptions(
        username="admin",
        private_key_path="~/.ssh/id_rsa",
        private_key_passphrase="key_passphrase",
    ),
    transport_options=TransportSsh2Options(
        known_hosts_path="~/.ssh/known_hosts",
        libssh2_trace=False,
    ),
) as cli:
    result = cli.send_input("show ip interface brief")
    print(result.result)
```

## 使用 Telnet

```python
from scrapli import Cli, AuthOptions, TransportTelnetOptions

with Cli(
    host="192.168.1.1",
    port=23,
    auth_options=AuthOptions(
        username="admin",
        password="admin",
        force_in_session_auth=True,
    ),
    transport_options=TransportTelnetOptions(),
) as cli:
    result = cli.send_input("show version")
    print(result.result)
```

Telnet 模式下端口自动推断为 23。

## 手动管理连接（不使用 with）

```python
cli = Cli(
    host="192.168.1.1",
    definition_file_or_name="cisco_iosxe",
    auth_options=AuthOptions(username="admin", password="admin"),
)

try:
    open_result = cli.open()
    result = cli.send_input("show version")
    print(result.result)
finally:
    cli.close()
```

## 预期输出

```
主机: 192.168.1.1:22
耗时: 1.23s
失败: False
---
Cisco IOS XE Software, Version 17.9.3
Cisco IOS Software [Cupertino], Catalyst L3 Switch Software (CAT9K_IOSXE), Version 17.9.3...
ROM: IOS-XE ROMMON
...
```

相关文档：
- [Cli 驱动详解](../concepts/04-cli-driver.md)
- [认证与会话配置](../concepts/03-auth-session.md)
- [传输层](../concepts/02-transport-layer.md)
