---
type: Concept
title: SSH 自动探测
description: SSHDetect 自动探测设备类型、SSH_MAPPER_DICT 指纹库、三种探测方法
tags: [netmiko, SSHDetect, autodetect, device-type, fingerprint]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: netmiko-source
    resource: /references/netmiko-source.md
---

# SSH 自动探测

## SSHDetect 类

`SSHDetect` 类在不知道设备类型时自动猜测 `device_type`。它通过建立一个 generic SSH 连接，发送一系列探测命令并匹配输出来识别设备厂商和操作系统。

```python
from netmiko import SSHDetect, ConnectHandler

device = {
    "device_type": "autodetect",  # 必须是 "autodetect"
    "host": "10.0.0.1",
    "username": "admin",
    "password": "password",
}

guesser = SSHDetect(**device)
best_match = guesser.autodetect()
print(best_match)  # 例如 "cisco_ios"
print(guesser.potential_matches)  # 所有匹配的 {device_type: confidence}

# 使用探测结果连接
device["device_type"] = best_match
connection = ConnectHandler(**device)
```

## 工作原理

### 初始化

1. 校验 `device_type == "autodetect"`，否则抛出 `ValueError`
2. 强制设置 `global_cmd_verify = False`（自动探测不需要命令回显验证）
3. 使用 `ConnectHandler` 建立连接（底层使用 `TerminalServerSSH` generic 驱动）
4. 等待3秒让登录完成
5. 调用 `_test_channel_read()` 清理初始数据到 `initial_buffer`
6. 初始化 `potential_matches = {}` 和 `_results_cache = {}`

### 探测循环

`autodetect()` 遍历 `SSH_MAPPER_BASE`（按命令频率排序的设备指纹列表）：

1. 对每个设备类型，获取其 `dispatch` 方法名和参数
2. 动态调用 dispatch 方法（如 `_autodetect_std`）
3. 如果返回非零 accuracy，记录到 `potential_matches`
4. 如果 accuracy >= 99，立即返回最佳匹配（高置信度短路）
5. 遍历完所有指纹后，返回 accuracy 最高的 device_type；无匹配返回 `None`

### SSH_MAPPER_DICT 指纹库

每条指纹定义4个字段：

```python
"cisco_ios": {
    "cmd": "show version",                          # 发送的命令
    "search_patterns": [                             # 匹配输出的正则列表
        "Cisco IOS Software",
        "Cisco Internetwork Operating System Software",
    ],
    "priority": 95,                                  # 置信度 0-99
    "dispatch": "_autodetect_std",                   # 探测方法
}
```

`SSH_MAPPER_BASE` 是排序后的列表（非字典），按命令使用频率降序排列——最常见的 `"show version"` 排在前面，以减少需要发送的命令数量。

## 三种探测方法

### _autodetect_std

标准探测方法：发送命令，匹配输出中的正则模式。

流程：
1. 通过 `_send_command_wrapper(cmd)` 发送命令（带缓存）
2. 检查输出中是否包含无效响应模式（如 `"% Invalid input"`, `"command not found"`）
3. 对每个 `search_pattern` 执行 `re.search()`
4. 匹配成功返回 `priority`，否则返回 0

无效响应检测列表包括：
- `% Invalid input detected`
- `syntax error, expecting`
- `Error: Unrecognized command`
- `%Error`
- `command not found`
- `Syntax Error: unexpected argument`

### _autodetect_remote_version

通过 SSH 协议层的远程版本字符串识别设备，不发送任何 CLI 命令：

```python
"cisco_wlc": {
    "cmd": "",
    "dispatch": "_autodetect_remote_version",
    "search_patterns": [r"CISCO_WLC"],
    "priority": 99,
}
```

从 `paramiko.Channel.transport.remote_version` 获取 SSH banner 字符串并匹配。适用于无法通过 CLI 命令识别的设备（如 Cisco WLC）。

### _autodetect_login_banner

通过登录前的横幅文本识别设备：

```python
"hirschmann_hios": {
    "cmd": "",
    "dispatch": "_autodetect_login_banner",
    "search_patterns": [r"Release HiOS-"],
    "priority": 99,
}
```

在 `initial_buffer`（登录后接收到的初始数据）中匹配模式。

## 命令缓存

`_send_command_wrapper(cmd)` 实现了命令结果缓存：

```python
def _send_command_wrapper(self, cmd):
    cached_results = self._results_cache.get(cmd)
    if not cached_results:
        response = self._send_command(cmd)
        self._results_cache[cmd] = response
        return response
    else:
        return cached_results
```

因为多个设备指纹可能使用相同的命令（如 "show version"），缓存避免重复发送相同命令。

## 特殊处理

- **Cisco WLC**：有两个指纹（`cisco_wlc` 使用 remote_version，`cisco_wlc_85` 使用 `"show inventory"` 命令）。如果 `cisco_wlc_85` 高优先级匹配，结果映射为 `cisco_wlc`。
- **Cisco IOS XR**：有两个指纹（`cisco_xr` 和 `cisco_xr_2` 使用 `"show version brief"`）。如果 `cisco_xr_2` 匹配，结果映射为 `cisco_xr`。

## 支持的探测设备

SSH_MAPPER_DICT 包含约50种设备类型的指纹，覆盖：

- Cisco: IOS, IOS XE, NX-OS, IOS XR, ASA, Firepower, WLC, AP, Viptela
- Arista EOS, Aruba AOS-CX, Juniper Junos
- HP/H3C Comware, HP Procurve, Huawei
- Dell OS9/OS10/Force10/PowerConnect
- F5 BIG-IP, Palo Alto, Fortinet
- Extreme EXOS/NetIron/SLX/VSP
- Linux, Cumulus Linux
- 以及 Alcatel, Allied Telesis, Brocade, Check Point, Ericsson, MikroTik（通过 remote_version）, Yamaha 等

## 使用建议

```python
from netmiko import SSHDetect, ConnectHandler

device = {
    "device_type": "autodetect",
    "host": "unknown-device.example.com",
    "username": "admin",
    "password": "password",
    "conn_timeout": 15,
}

try:
    guesser = SSHDetect(**device)
    best_match = guesser.autodetect()

    if best_match is None:
        print("无法自动识别设备类型")
        print(f"已尝试匹配: {guesser.potential_matches}")
    else:
        print(f"识别为: {best_match} (置信度: {guesser.potential_matches[best_match]})")
        device["device_type"] = best_match
        conn = ConnectHandler(**device)
        print(conn.send_command("show version"))
        conn.disconnect()
finally:
    guesser.connection.disconnect()
```

## 局限性

- 自动探测需要设备返回可识别的 CLI 输出，某些设备可能不在指纹库中
- 探测过程会向设备发送多条命令（虽然有缓存），可能在审计日志中留下记录
- 置信度低于99时不会短路，会遍历所有指纹
- 仅支持 SSH 连接的自动探测（不支持 Telnet/Serial）
- 探测完成后应使用 `best_match` 重新建立正式连接（SSHDetect 的连接是 generic 驱动，不具备厂商特定功能）
