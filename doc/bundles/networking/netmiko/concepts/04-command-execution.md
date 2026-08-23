---
type: Concept
title: 命令执行
description: send_command、send_command_timing、send_command_expect 三种命令发送模式、read_timeout、expect_string
tags: [netmiko, send-command, command-execution, read-timeout, expect-string]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: netmiko-source
    resource: /references/netmiko-source.md
---

# 命令执行

netmiko 提供三种命令发送方法，适用于不同的输出等待场景。

## 三种命令发送模式对比

| 方法 | 等待机制 | 默认 read_timeout | 默认 cmd_verify | 适用场景 |
|------|---------|-------------------|----------------|----------|
| `send_command` | 等待提示符或 expect_string 出现 | 10秒 | True | 标准 show 命令，知道提示符会返回 |
| `send_command_timing` | 等待 last_read 秒无新数据 | 120秒 | False | 不确定输出格式、命令持续输出 |
| `send_command_expect` | `send_command` 的别名 | - | - | 向后兼容 |

## send_command

基于**模式匹配**的命令执行。发送命令后持续读取，直到检测到设备提示符（或 `expect_string`）：

```python
output = conn.send_command("show ip interface brief")
```

关键参数：

```python
output = conn.send_command(
    command_string="show version",
    expect_string=None,        # 自定义结束正则模式；None 表示使用设备提示符
    read_timeout=10.0,         # 最大等待时间（秒），超时抛出 ReadTimeout
    auto_find_prompt=True,     # 自动调用 find_prompt() 更新提示符
    strip_prompt=True,         # 移除输出末尾的提示符
    strip_command=True,        # 移除输出开头的命令回显
    normalize=True,            # 规范化命令结尾的换行符
    cmd_verify=True,           # 验证命令回显
    use_textfsm=False,         # 使用 TextFSM 解析
    textfsm_template=None,     # TextFSM 模板路径
    use_ttp=False,             # 使用 TTP 解析
    use_genie=False,           # 使用 Genie/pyATS 解析
)
```

使用 `expect_string` 处理非标准提示符：

```python
# 命令可能进入交互模式，等待特定提示
output = conn.send_command(
    "copy running-config tftp://10.0.0.2/config.cfg",
    expect_string=r"Address of remote host",
)
conn.send_command("\n", expect_string=r"Destination filename")
conn.send_command("\n", expect_string=r"#")
```

## send_command_timing

基于**延迟**的命令执行。发送命令后持续读取，直到 `last_read` 秒内没有新数据到达：

```python
output = conn.send_command_timing("show running-config")
```

关键参数：

```python
output = conn.send_command_timing(
    command_string="show running-config",
    last_read=2.0,             # 无新数据后继续等待的时间（秒）
    read_timeout=120.0,        # 绝对超时（秒），0 表示永不超时
    strip_prompt=True,
    strip_command=True,
    normalize=True,
    cmd_verify=False,          # 默认不验证命令回显
)
```

**何时使用 timing 模式：**
- 命令输出格式不确定，无法可靠匹配提示符
- 命令执行时间较长（如 `show running-config`、`debug` 输出）
- 命令可能进入分页或交互状态
- 设备响应较慢

**read_timeout=0** 表示无限等待——netmiko 会一直读取直到 last_read 时间窗口内无新数据：

```python
# 长时间运行的命令，不设绝对超时
output = conn.send_command_timing("show tech-support", read_timeout=0, last_read=5.0)
```

## send_command_expect

`send_command_expect` 是 `send_command` 的别名，保留用于向后兼容：

```python
# 这两者完全等价
output = conn.send_command("show version")
output = conn.send_command_expect("show version")
```

## 底层读取方法

三种命令方法底层依赖以下通道读取方法：

### read_channel

读取通道中当前可用的所有数据（非阻塞）：

```python
data = conn.read_channel()
```

### read_channel_timing

延迟驱动的循环读取：

```python
output = conn.read_channel_timing(last_read=2.0, read_timeout=120.0)
```

### read_until_pattern

读取直到匹配指定正则模式：

```python
output = conn.read_until_pattern(pattern=r"#\s*$", read_timeout=10.0)
```

### read_until_prompt

读取直到匹配 base_prompt：

```python
output = conn.read_until_prompt()
```

### read_until_prompt_or_pattern

读取直到匹配提示符或指定模式（先匹配到者优先）：

```python
output = conn.read_until_prompt_or_pattern(pattern=r"[Pp]assword")
```

## 输出处理

### strip_prompt

移除输出最后一行（如果包含 base_prompt）：

```python
# 默认 strip_prompt=True
output = conn.send_command("show version")
# output 不包含末尾的 "Router1#"

# 保留提示符
output = conn.send_command("show version", strip_prompt=False)
```

### strip_command

移除输出开头的命令回显行：

```python
# 默认 strip_command=True
output = conn.send_command("show version")
# output 不包含开头的 "show version" 回显

# 保留命令回显
output = conn.send_command("show version", strip_command=False)
```

### normalize_linefeeds

将 `\r\r\n`、`\r\n`、`\n\r` 统一转换为 `\n`：

```python
clean = conn.normalize_linefeeds(raw_output)
```

## 结构化输出

三种命令方法都支持通过 TextFSM、TTP 或 Genie 解析非结构化输出：

```python
# TextFSM
interfaces = conn.send_command("show ip interface brief", use_textfsm=True)
# 返回列表，每个元素是字典

# Genie/pyATS
version = conn.send_command("show version", use_genie=True)
# 返回嵌套字典
```

详见[输出解析示例](../examples/output-parsing-textfsm.md)。
