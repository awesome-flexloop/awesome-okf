---
type: Example
title: 多厂商设备连接
description: 使用 ConnectHandler 连接 Cisco IOS、Arista EOS、Juniper Junos、Linux 等不同厂商设备
tags: [netmiko, example, multi-vendor, ConnectHandler]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: netmiko-source
    resource: /references/netmiko-source.md
---

# 多厂商设备连接

## 统一连接模式

netmiko 的核心优势是使用相同的 API 连接不同厂商设备，只需更改 `device_type`：

```python
from netmiko import ConnectHandler

devices = [
    {
        "device_type": "cisco_ios",
        "host": "10.0.0.1",
        "username": "admin",
        "password": "password",
        "secret": "enable_pass",
    },
    {
        "device_type": "arista_eos",
        "host": "10.0.0.2",
        "username": "admin",
        "password": "password",
        "secret": "enable_pass",
    },
    {
        "device_type": "juniper_junos",
        "host": "10.0.0.3",
        "username": "admin",
        "password": "password",
    },
    {
        "device_type": "linux",
        "host": "10.0.0.4",
        "username": "admin",
        "password": "password",
    },
]

for device in devices:
    with ConnectHandler(**device) as conn:
        output = conn.send_command("show version")
        print(f"=== {device['host']} ({device['device_type']}) ===")
        print(output[:200])
        print()
```

## Cisco IOS

```python
cisco_device = {
    "device_type": "cisco_ios",
    "host": "router1.example.com",
    "username": "admin",
    "password": "cisco_pass",
    "secret": "enable_secret",
    "port": 22,
    "verbose": True,
}

with ConnectHandler(**cisco_device) as conn:
    conn.enable()
    print(conn.find_prompt())  # Router1#
    print(conn.send_command("show ip interface brief"))
    conn.save_config()
```

## Arista EOS

```python
arista_device = {
    "device_type": "arista_eos",
    "host": "switch1.example.com",
    "username": "admin",
    "password": "arista_pass",
    "secret": "enable_pass",
}

with ConnectHandler(**arista_device) as conn:
    conn.enable()
    # EOS 支持 JSON 输出
    output = conn.send_command("show version | json")
    print(output)
```

Arista 驱动自动启用 ANSI 转义码处理，并使用 `terminal width 511` 和 `no pagination`。

## Juniper Junos

```python
juniper_device = {
    "device_type": "juniper_junos",
    "host": "fw1.example.com",
    "username": "admin",
    "password": "juniper_pass",
}

with ConnectHandler(**juniper_device) as conn:
    # Juniper 使用 NoEnable mixin，无需 enable()
    print(conn.send_command("show version"))

    # 配置变更使用 commit 而非 save_config
    config = ["set interfaces ge-0/0/0 description WAN"]
    conn.send_config_set(config)
    conn.commit(comment="Updated WAN description")
```

注意：Juniper 不使用 enable 模式（混入了 NoEnable），配置后需要 `commit()` 提交。

## Linux SSH

```python
linux_device = {
    "device_type": "linux",
    "host": "server1.example.com",
    "username": "admin",
    "password": "linux_pass",
}

with ConnectHandler(**linux_device) as conn:
    print(conn.send_command("uname -a"))
    # Linux 的 config_mode 映射到 sudo -s
    # check_config_mode 检查是否为 root
    print(conn.send_command("df -h"))
```

## HP Comware

```python
hp_device = {
    "device_type": "hp_comware",
    "host": "10.0.0.5",
    "username": "admin",
    "password": "hp_pass",
}

with ConnectHandler(**hp_device) as conn:
    # Comware 默认禁用 global_cmd_verify
    # config_mode 发送 "system-view"
    output = conn.send_command("display version")
    print(output)
```

## 使用自动探测

当不知道设备类型时：

```python
from netmiko import SSHDetect, ConnectHandler

device = {
    "device_type": "autodetect",
    "host": "unknown.example.com",
    "username": "admin",
    "password": "password",
}

guesser = SSHDetect(**device)
device_type = guesser.autodetect()
guesser.connection.disconnect()

if device_type:
    device["device_type"] = device_type
    with ConnectHandler(**device) as conn:
        print(conn.send_command("show version"))
else:
    print("无法识别设备类型")
```

## 并发连接多厂商设备

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException

def get_version(device):
    try:
        with ConnectHandler(**device, conn_timeout=10) as conn:
            output = conn.send_command("show version")
            return device["host"], output, None
    except NetmikoAuthenticationException:
        return device["host"], None, "认证失败"
    except NetmikoTimeoutException:
        return device["host"], None, "连接超时"

devices = [
    {"device_type": "cisco_ios", "host": "10.0.0.1", "username": "admin", "password": "pass"},
    {"device_type": "arista_eos", "host": "10.0.0.2", "username": "admin", "password": "pass"},
    {"device_type": "juniper_junos", "host": "10.0.0.3", "username": "admin", "password": "pass"},
]

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(get_version, d) for d in devices]
    for future in as_completed(futures):
        host, output, error = future.result()
        if error:
            print(f"{host}: 错误 - {error}")
        else:
            print(f"{host}: 成功 ({len(output)} bytes)")
```
