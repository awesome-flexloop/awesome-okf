---
type: Example
title: 批量配置变更
description: 使用 send_config_set 批量发送配置命令、配置回滚、多设备配置推送
tags: [netmiko, example, config, send-config-set, batch]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: netmiko-source
    resource: /references/netmiko-source.md
---

# 批量配置变更

## 基本配置变更

```python
from netmiko import ConnectHandler

device = {
    "device_type": "cisco_ios",
    "host": "10.0.0.1",
    "username": "admin",
    "password": "password",
    "secret": "enable_pass",
}

with ConnectHandler(**device) as conn:
    conn.enable()

    config_commands = [
        "interface GigabitEthernet0/1",
        "description Uplink to Core Switch",
        "ip address 10.1.1.1 255.255.255.252",
        "no shutdown",
        "exit",
        "ip route 0.0.0.0 0.0.0.0 10.1.1.2",
    ]

    output = conn.send_config_set(config_commands)
    print(output)

    conn.save_config()
```

## 从文件加载配置

配置文件 `config.txt`：

```text
interface GigabitEthernet0/2
description Server Port
switchport mode access
switchport access vlan 100
spanning-tree portfast
no shutdown
```

加载并发送：

```python
with ConnectHandler(**device) as conn:
    conn.enable()
    output = conn.send_config_from_file("config.txt")
    print(output)
    conn.save_config()
```

## 不自动进入/退出配置模式

如果已在配置模式中，或需要手动控制：

```python
with ConnectHandler(**device) as conn:
    conn.enable()
    conn.config_mode()

    output = conn.send_config_set(
        ["hostname NewRouter"],
        enter_config_mode=False,
        exit_config_mode=False,
    )

    conn.exit_config_mode()
    conn.save_config()
```

## 配置错误检测

使用 `error_pattern` 检测配置错误：

```python
with ConnectHandler(**device) as conn:
    conn.enable()

    try:
        output = conn.send_config_set(
            ["interface GigabitEthernet0/99", "no shutdown"],
            error_pattern=r"% Invalid input",
        )
    except Exception as e:
        print(f"配置错误: {e}")
```

## 多设备批量配置

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException

devices = [
    {"device_type": "cisco_ios", "host": "10.0.0.1", "username": "admin", "password": "pass", "secret": "enable"},
    {"device_type": "cisco_ios", "host": "10.0.0.2", "username": "admin", "password": "pass", "secret": "enable"},
    {"device_type": "cisco_ios", "host": "10.0.0.3", "username": "admin", "password": "pass", "secret": "enable"},
]

config_commands = [
    "ntp server 10.0.0.100",
    "ntp server 10.0.0.101",
    "clock timezone UTC 0",
    "service timestamps log datetime msec",
]

def configure_device(device, commands):
    try:
        with ConnectHandler(**device, conn_timeout=10) as conn:
            conn.enable()
            output = conn.send_config_set(commands)
            conn.save_config()
            return device["host"], True, output
    except (NetmikoTimeoutException, NetmikoAuthenticationException) as e:
        return device["host"], False, str(e)

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = {executor.submit(configure_device, d, config_commands): d for d in devices}
    for future in as_completed(futures):
        host, success, output = future.result()
        status = "成功" if success else "失败"
        print(f"{host}: {status}")
```

## Juniper 配置提交流程

Juniper 设备使用候选配置和 commit 模型：

```python
juniper_device = {
    "device_type": "juniper_junos",
    "host": "10.0.0.3",
    "username": "admin",
    "password": "password",
}

with ConnectHandler(**juniper_device) as conn:
    # 发送配置命令（自动进入和退出配置模式）
    config = [
        "set interfaces ge-0/0/0 description WAN Link",
        "set interfaces ge-0/0/0 unit 0 family inet address 203.0.113.1/30",
    ]
    output = conn.send_config_set(config)
    print(output)

    # 提交前检查语法
    check = conn.commit(check=True)
    print(f"检查结果: {check}")

    # 确认提交（2分钟内需再次确认）
    conn.commit(confirm=True, confirm_delay=2, comment="WAN link config")
    print("配置已确认提交，需在2分钟内再次确认")

    # 实际提交
    conn.commit(comment="Configured WAN interface")
```

## 配置回滚模式

备份 → 配置 → 验证 → 失败则回滚：

```python
with ConnectHandler(**device) as conn:
    conn.enable()

    # 备份当前配置
    backup = conn.send_command("show running-config")
    with open(f"backup_{conn.host}.cfg", "w") as f:
        f.write(backup)

    try:
        # 发送新配置
        config = [
            "interface GigabitEthernet0/1",
            "ip address 10.1.1.1 255.255.255.252",
            "no shutdown",
        ]
        conn.send_config_set(config, cmd_verify=True)

        # 验证配置
        verification = conn.send_command("show ip interface brief")
        if "10.1.1.1" not in verification:
            raise ValueError("配置验证失败：IP 地址未生效")

        conn.save_config()
        print("配置成功并保存")

    except Exception as e:
        print(f"配置失败，正在回滚: {e}")
        # 从备份恢复
        conn.send_config_from_file(f"backup_{conn.host}.cfg")
        conn.save_config()
        print("已回滚到备份配置")
```

## VLAN 批量配置示例

```python
with ConnectHandler(**device) as conn:
    conn.enable()

    vlans = [100, 200, 300]
    commands = []
    for vlan_id in vlans:
        commands.extend([
            f"vlan {vlan_id}",
            f"name VLAN_{vlan_id}",
            "exit",
        ])

    output = conn.send_config_set(commands)
    conn.save_config()

    # 验证
    vlan_output = conn.send_command("show vlan brief")
    print(vlan_output)
```
