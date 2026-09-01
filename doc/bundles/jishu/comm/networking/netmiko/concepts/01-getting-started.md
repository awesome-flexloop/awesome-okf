---
type: Concept
title: 5分钟快速上手
description: 从安装到第一个 netmiko 连接、执行命令、关闭连接的快速入门
tags: [netmiko, getting-started, quickstart]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: netmiko-source
    resource: /references/netmiko-source.md
---

# 5分钟快速上手

## 安装

```bash
pip install netmiko
```

## 第一个连接

使用 `ConnectHandler` 工厂函数连接设备并执行命令：

```python
from netmiko import ConnectHandler

connection = ConnectHandler(
    device_type="cisco_ios",
    host="192.168.1.1",
    username="admin",
    password="password",
)

output = connection.send_command("show ip interface brief")
print(output)

connection.disconnect()
```

## device_type 字典

更常见的做法是使用设备参数字典：

```python
device = {
    "device_type": "cisco_ios",
    "host": "192.168.1.1",
    "username": "admin",
    "password": "password",
    "secret": "enable_password",  # 可选，特权模式密码
}

with ConnectHandler(**device) as conn:
    print(conn.send_command("show version"))
```

使用 `with` 语句时，连接会在代码块结束时自动断开。

## 核心参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `device_type` | 设备类型（必须），如 `"cisco_ios"`, `"arista_eos"`, `"juniper_junos"`, `"linux"` | `""` |
| `host` | 设备主机名或 IP 地址 | `""` |
| `username` | SSH 用户名 | `""` |
| `password` | SSH 密码 | `None` |
| `secret` | 特权模式（enable）密码 | `""` |
| `port` | SSH 端口 | `22`（Telnet 为 `23`） |
| `conn_timeout` | TCP 连接超时（秒） | `10` |
| `fast_cli` | 快速模式（减少延迟） | `True` |
| `global_delay_factor` | 全局延迟因子 | `1.0`（fast_cli 时为 `0.1`） |
| `session_log` | 会话日志文件路径 | `None` |

## 查看支持的平台

```python
from netmiko import platforms

print(len(platforms))  # 支持的 device_type 总数
print(sorted(platforms)[:10])  # 前10个
```

`platforms` 是一个排序后的字符串列表，包含所有支持的 device_type（含 `_ssh`、`_telnet`、`_serial` 后缀变体）。

## 基本操作流程

```python
from netmiko import ConnectHandler

device = {"device_type": "cisco_ios", "host": "10.0.0.1",
          "username": "admin", "password": "pass", "secret": "enable_pass"}

conn = ConnectHandler(**device)

# 进入特权模式
conn.enable()

# 执行 show 命令
print(conn.send_command("show running-config"))

# 发送配置命令
config_commands = ["interface GigabitEthernet0/1", "description WAN Link", "no shutdown"]
output = conn.send_config_set(config_commands)
print(output)

# 保存配置
conn.save_config()

conn.disconnect()
```

## 下一步

- [ConnectHandler 工厂详解](02-connect-handler.md) — 深入理解工厂函数和设备参数
- [BaseConnection 核心](03-base-connection.md) — 连接生命周期和会话准备
- [命令执行](04-command-execution.md) — 三种命令发送模式的区别
