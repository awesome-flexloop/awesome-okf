---
type: Concept
title: 配置管理
description: send_config_set、send_config_from_file、config_mode、enable 模式、save_config
tags: [netmiko, config, send-config-set, enable, config-mode, save-config]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: netmiko-source
    resource: /references/netmiko-source.md
---

# 配置管理

## 特权模式（Enable Mode）

许多网络设备需要进入特权模式才能执行配置变更：

```python
conn.enable()  # 进入特权模式，使用 secret 参数作为密码
```

`enable()` 方法：
1. 检查是否已在特权模式（`check_enable_mode()`）
2. 发送 enable 命令（Cisco 默认为 `"enable"`）
3. 检测密码提示（pattern `"ssword"`）并发送 secret
4. 验证已进入特权模式

```python
conn.exit_enable_mode()  # 退出特权模式（Cisco 发送 "disable"）
```

`check_enable_mode()` 检查当前提示符是否包含特权模式标识：

```python
if conn.check_enable_mode():
    print("已在特权模式")
```

## 配置模式（Config Mode）

### 进入和退出

```python
conn.config_mode()  # 进入配置模式（Cisco 发送 "configure terminal"）
# 执行配置命令...
conn.exit_config_mode()  # 退出配置模式（Cisco 发送 "end"）
```

### 检查状态

```python
if conn.check_config_mode():
    print("在配置模式中")
```

不同设备的配置模式标识不同：

| 平台 | config_mode 命令 | 配置模式提示符标识 |
|------|-----------------|------------------|
| Cisco IOS | `configure terminal` | `)#` |
| Arista EOS | `configure terminal` | `)#` |
| Juniper Junos | `configure` | `]` |
| HP Comware | `system-view` | `]` |
| Linux | `sudo -s` | `#`（root 提示符） |

## send_config_set

`send_config_set()` 是批量发送配置命令的核心方法。它自动进入配置模式、逐条发送命令、然后退出配置模式：

```python
config_commands = [
    "interface GigabitEthernet0/1",
    "description WAN Link to ISP",
    "ip address 203.0.113.1 255.255.255.252",
    "no shutdown",
]
output = conn.send_config_set(config_commands)
print(output)
```

关键参数：

```python
output = conn.send_config_set(
    config_commands,          # 字符串、字符串列表或文件对象
    exit_config_mode=True,    # 完成后自动退出配置模式
    read_timeout=None,        # 读取超时
    strip_prompt=False,       # 移除提示符（配置输出默认保留）
    strip_command=False,      # 移除命令回显（配置输出默认保留）
    cmd_verify=True,          # 验证每条命令回显
    enter_config_mode=True,   # 自动进入配置模式
    error_pattern="",         # 错误模式正则，匹配则停止
    terminator=r"#",          # 配置模式终止符
    bypass_commands=None,     # 绕过配置模式的命令正则
)
```

### 从文件加载配置

```python
output = conn.send_config_from_file("config.txt")
```

`send_config_from_file()` 逐行读取文件并调用 `send_config_set()`。文件每行是一条配置命令。

### 错误检测

使用 `error_pattern` 在配置过程中检测错误：

```python
try:
    output = conn.send_config_set(
        ["interface GigabitEthernet0/99", "no shutdown"],
        error_pattern=r"% Invalid input",
    )
except Exception as e:
    print(f"配置错误: {e}")
```

### 不自动进入配置模式

如果已经在配置模式中，可以禁用自动进入/退出：

```python
conn.config_mode()
output = conn.send_config_set(
    ["hostname NewRouter"],
    enter_config_mode=False,
    exit_config_mode=False,
)
conn.exit_config_mode()
```

## save_config

保存运行配置到启动配置：

```python
conn.save_config()
```

不同平台的默认保存命令：

| 平台 | 命令 |
|------|------|
| Cisco IOS | `write mem` |
| Cisco Base | `copy running-config startup-config` |
| 其他 | 需在驱动中重写，基类抛出 NotImplementedError |

支持确认交互：

```python
# 需要确认的保存命令
output = conn.save_config(
    cmd="copy running-config startup-config",
    confirm=True,
    confirm_response="",  # 发送回车确认
)
```

## commit（Juniper 等）

支持候选配置模型的设备（如 Juniper Junos）提供 `commit()` 方法：

```python
if conn.device_type.startswith("juniper"):
    # Juniper 提交配置
    output = conn.commit()

    # 提交确认（2分钟内需再次确认，否则回滚）
    output = conn.commit(confirm=True, confirm_delay=2)

    # 提交前检查语法
    output = conn.commit(check=True)

    # 带注释提交
    output = conn.commit(comment="Changed interface description")
```

`commit()` 参数：

| 参数 | 说明 |
|------|------|
| `confirm` | 确认提交（需在 confirm_delay 内再次确认） |
| `confirm_delay` | 确认超时（分钟） |
| `check` | 仅检查语法，不实际提交 |
| `comment` | 提交注释 |
| `and_quit` | 提交后退出配置模式 |

基类 `BaseConnection.commit()` 抛出 `AttributeError`，不支持 commit 的设备不应调用此方法。

## NoEnable 和 NoConfig Mixin

某些设备没有特权模式或配置模式的概念，netmiko 通过 mixin 类处理：

- **NoEnable**：`check_enable_mode()` 始终返回 True，`enable()` 和 `exit_enable_mode()` 为空操作。Juniper Junos 使用此 mixin。
- **NoConfig**：`check_config_mode()` 始终返回 True，`config_mode()` 和 `exit_config_mode()` 为空操作。适用于配置命令可直接执行的设备。

## 完整配置工作流示例

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
    # 进入特权模式
    conn.enable()

    # 备份当前配置
    backup = conn.send_command("show running-config")

    # 发送配置变更
    config = [
        "interface GigabitEthernet0/1",
        "description Updated WAN Link",
        "ip address 203.0.113.1 255.255.255.252",
        "no shutdown",
    ]
    output = conn.send_config_set(config)
    print(output)

    # 保存配置
    conn.save_config()

    # 验证
    verification = conn.send_command("show ip interface brief")
    print(verification)
```
