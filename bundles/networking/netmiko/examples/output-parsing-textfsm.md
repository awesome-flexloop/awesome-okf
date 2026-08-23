---
type: Example
title: TextFSM 输出解析
description: 使用 TextFSM 和 ntc-templates 将 CLI 输出解析为结构化数据
tags: [netmiko, example, textfsm, ntc-templates, structured-data, parsing]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: netmiko-source
    resource: /references/netmiko-source.md
---

# TextFSM 输出解析

## 安装

```bash
pip install netmiko textfsm ntc-templates
```

`ntc-templates` 是社区维护的网络设备 TextFSM 模板集合，安装后 netmiko 自动使用。

## 基本用法

在 `send_command()` 中设置 `use_textfsm=True`：

```python
from netmiko import ConnectHandler

device = {
    "device_type": "cisco_ios",
    "host": "10.0.0.1",
    "username": "admin",
    "password": "password",
}

with ConnectHandler(**device) as conn:
    # 返回 list of dict
    interfaces = conn.send_command("show ip interface brief", use_textfsm=True)
    print(interfaces)
```

输出示例：

```python
[
    {"intf": "GigabitEthernet0/0", "ipaddr": "10.0.0.1", "status": "up", "proto": "up"},
    {"intf": "GigabitEthernet0/1", "ipaddr": "10.1.1.1", "status": "up", "proto": "up"},
    {"intf": "Loopback0", "ipaddr": "192.168.1.1", "status": "up", "proto": "up"},
]
```

## 遍历结构化数据

```python
with ConnectHandler(**device) as conn:
    interfaces = conn.send_command("show ip interface brief", use_textfsm=True)

    # 查找状态为 down 的接口
    down_interfaces = [
        intf for intf in interfaces
        if intf["status"].lower() == "administratively down"
    ]

    for intf in down_interfaces:
        print(f"接口 {intf['intf']} ({intf['ipaddr']}) 处于管理关闭状态")

    # 统计接口数量
    print(f"共 {len(interfaces)} 个接口，{len(down_interfaces)} 个关闭")
```

## 常用 TextFSM 解析命令

### show version

```python
with ConnectHandler(**device) as conn:
    version = conn.send_command("show version", use_textfsm=True)
    print(version)
```

输出示例：

```python
[{
    "hostname": "Router1",
    "version": "15.7(3)M",
    "serial": ["FTX1234ABCD"],
    "uptime": "10 weeks, 3 days",
    "running_image": "flash:c2900-universalk9-mz.SPA.157-3.M.bin",
    "hardware": ["Cisco 2911"],
}]
```

### show mac address-table

```python
with ConnectHandler(**device) as conn:
    mac_table = conn.send_command("show mac address-table", use_textfsm=True)
    for entry in mac_table:
        print(f"VLAN {entry['vlan']}: {entry['destination_address']} -> {entry['destination_port']}")
```

### show vlan brief

```python
with ConnectHandler(**device) as conn:
    vlans = conn.send_command("show vlan brief", use_textfsm=True)
    for vlan in vlans:
        print(f"VLAN {vlan['vlan_id']}: {vlan['vlan_name']}")
```

## 使用自定义 TextFSM 模板

指定模板文件路径：

```python
with ConnectHandler(**device) as conn:
    output = conn.send_command(
        "show custom command",
        use_textfsm=True,
        textfsm_template="/path/to/custom_template.textfsm",
    )
```

### 编写 TextFSM 模板

模板文件 `template.textfsm`：

```text
Value Required INTERFACE (\S+)
Value IPADDR (\d+\.\d+\.\d+\.\d+)
Value STATUS (\S+)
Value PROTO (\S+)

Start
  ^${INTERFACE}\s+${IPADDR}\s+\w+\s+\w+\s+${STATUS}\s+${PROTO} -> Record
```

## TTP 解析

TTP 是另一个模板解析引擎，模板语法更简洁：

```bash
pip install ttp
```

```python
with ConnectHandler(**device) as conn:
    ttp_template = """
<group>
interface {{ interface }}
 description {{ description }}
 ip address {{ ip }} {{ mask }}
</group>
"""
    result = conn.send_command(
        "show running-config",
        use_ttp=True,
        ttp_template=ttp_template,
    )
    print(result)
```

也可以使用 `run_ttp()` 方法：

```python
with ConnectHandler(**device) as conn:
    result = conn.run_ttp(
        template="path/to/template.txt",
        commands=["show interfaces description", "show ip route"],
    )
```

## Genie/pyATS 解析（Cisco 平台）

```bash
pip install genie pyats
```

```python
with ConnectHandler(device_type="cisco_ios", **device) as conn:
    # Genie 返回嵌套字典，结构丰富
    version = conn.send_command("show version", use_genie=True)
    print(version["version"]["hostname"])
    print(version["version"]["version"])

    interfaces = conn.send_command("show ip interface brief", use_genie=True)
    for name, intf in interfaces["interface"].items():
        print(f"{name}: {intf.get('ip_address', 'unassigned')}")
```

## 解析错误处理

```python
from netmiko import ConnectHandler, NetmikoParsingException

with ConnectHandler(**device) as conn:
    try:
        output = conn.send_command(
            "show version",
            use_textfsm=True,
            raise_parsing_error=True,  # 解析失败时抛出异常
        )
    except NetmikoParsingException as e:
        print(f"TextFSM 解析失败: {e}")
        # 回退到原始文本
        output = conn.send_command("show version", use_textfsm=False)
```

`raise_parsing_error=False`（默认）时，解析失败会静默返回原始字符串。设置为 `True` 可在解析失败时获得明确的异常通知。

## 多平台结构化输出

```python
devices = [
    {"device_type": "cisco_ios", "host": "10.0.0.1", ...},
    {"device_type": "arista_eos", "host": "10.0.0.2", ...},
]

with ConnectHandler(**devices[0]) as conn:
    # ntc-templates 自动根据 device_type 选择模板
    output = conn.send_command("show interfaces status", use_textfsm=True)
```

netmiko 会将 `device_type` 传递给 TextFSM 解析器，自动在 ntc-templates 中查找对应平台的模板。

## 检查 ntc-templates 模板目录

```python
from netmiko.utilities import get_template_dir

template_dir = get_template_dir()
print(f"TextFSM 模板目录: {template_dir}")

import os
templates = [f for f in os.listdir(template_dir) if f.endswith(".textfsm")]
print(f"可用模板数: {len(templates)}")
print(sorted(templates)[:10])
```
