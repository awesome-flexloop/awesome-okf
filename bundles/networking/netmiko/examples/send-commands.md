---
type: Example
title: 命令执行模式对比
description: send_command、send_command_timing、send_command_expect 的使用场景和参数对比
tags: [netmiko, example, send-command, timing, expect]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: netmiko-source
    resource: /references/netmiko-source.md
---

# 命令执行模式对比

## 基本命令执行

### send_command（模式匹配，默认）

适用于标准 show 命令，等待提示符返回：

```python
from netmiko import ConnectHandler

with ConnectHandler(device_type="cisco_ios", host="10.0.0.1",
                    username="admin", password="pass") as conn:
    # 基本用法
    output = conn.send_command("show ip interface brief")
    print(output)
```

### send_command_timing（延迟驱动）

适用于长时间运行或输出格式不确定的命令：

```python
    # show tech-support 输出量大、耗时长
    output = conn.send_command_timing(
        "show tech-support",
        last_read=5.0,       # 5秒无新数据认为命令完成
        read_timeout=300,    # 最多等待5分钟
    )
```

### send_command_expect（别名）

```python
    # send_command_expect 是 send_command 的别名
    output = conn.send_command_expect("show version")
    # 等价于 conn.send_command("show version")
```

## 自定义 expect_string

当命令不会返回标准提示符时：

```python
with ConnectHandler(**device) as conn:
    # 文件复制需要多轮交互
    conn.send_command(
        "copy running-config tftp://10.0.0.2/config.cfg",
        expect_string=r"Address or name of remote host",
        strip_prompt=False,
        strip_command=False,
    )
    conn.send_command(
        "\n",
        expect_string=r"Destination filename",
        strip_prompt=False,
        strip_command=False,
    )
    output = conn.send_command(
        "\n",
        expect_string=r"#",
        strip_prompt=False,
        strip_command=False,
    )
    print(output)
```

## 输出清洗控制

```python
with ConnectHandler(**device) as conn:
    # 默认：strip_prompt=True, strip_command=True
    clean = conn.send_command("show clock")
    # "14:30:00 UTC Tue Aug 23 2026"

    # 保留提示符和命令回显（用于调试）
    raw = conn.send_command(
        "show clock",
        strip_prompt=False,
        strip_command=False,
    )
    # "show clock\r\n14:30:00 UTC Tue Aug 23 2026\r\nRouter1#"
```

## 超时处理

```python
from netmiko import ConnectHandler, ReadTimeout

with ConnectHandler(**device) as conn:
    try:
        output = conn.send_command(
            "show logging",
            read_timeout=15.0,  # 15秒超时
        )
    except ReadTimeout:
        print("命令执行超时，清空缓冲区")
        conn.clear_buffer()
        # 可以尝试使用 timing 模式
        output = conn.send_command_timing("show logging", last_read=3.0)
```

## 结构化输出

### TextFSM

```python
    # 返回列表的字典（需安装 textfsm 和 ntc-templates）
    interfaces = conn.send_command("show ip interface brief", use_textfsm=True)
    for intf in interfaces:
        print(f"{intf['intf']:20s} {intf['ipaddr']:16s} {intf['status']}")
```

### Genie/pyATS

```python
    # 返回嵌套字典（Cisco 平台，需安装 genie/pyats）
    version = conn.send_command("show version", use_genie=True)
    print(f"Hostname: {version['version']['hostname']}")
    print(f"Version: {version['version']['version']}")
```

## 批量发送命令

### 简单循环

```python
commands = ["show version", "show ip interface brief", "show vlan", "show running-config"]

with ConnectHandler(**device) as conn:
    for cmd in commands:
        print(f"=== {cmd} ===")
        output = conn.send_command(cmd)
        print(output)
        print()
```

### 使用 send_multiline 处理交互

```python
    # 多轮交互命令
    result = conn.send_multiline(
        [
            ("debug ip routing", r"#"),
            ("show debug", r"#"),
            ("undebug all", r"#"),
        ]
    )
```

## 底层读写方法

```python
with ConnectHandler(**device) as conn:
    # 直接写入通道
    conn.write_channel("show version\n")

    # 非阻塞读取可用数据
    import time
    time.sleep(1)
    data = conn.read_channel()
    print(data)

    # 读取直到匹配模式
    output = conn.read_until_pattern(pattern=r"Router1#", read_timeout=10)

    # 读取直到提示符
    output = conn.read_until_prompt()

    # 延迟读取
    output = conn.read_channel_timing(last_read=2.0, read_timeout=30)
```

## 模式选择决策表

| 场景 | 推荐方法 | 原因 |
|------|---------|------|
| `show version` 等标准命令 | `send_command` | 快速、可靠、自动验证提示符 |
| `show running-config` 大输出 | `send_command_timing` | 输出量大，提示符可能在配置文本中出现 |
| `show tech-support` | `send_command_timing(read_timeout=0)` | 耗时长，不设绝对超时 |
| 交互式命令（copy/delete） | `send_command(expect_string=...)` | 需要等待特定提示 |
| 不确定设备响应 | `send_command_timing` | 不依赖提示符匹配 |
| 需要回显验证 | `send_command(cmd_verify=True)` | 确保命令被正确接收 |
| 向后兼容旧代码 | `send_command_expect` | 与旧版 API 兼容 |
