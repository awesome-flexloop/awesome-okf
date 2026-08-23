---
type: Concept
title: BaseConnection 核心
description: BaseConnection 连接生命周期、session_preparation、disable_paging、终端设置
tags: [netmiko, BaseConnection, connection, lifecycle, session-preparation]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: netmiko-source
    resource: /references/netmiko-source.md
---

# BaseConnection 核心

`BaseConnection` 是所有 netmiko 驱动的基类，定义了厂商无关的连接管理、命令执行、配置管理等核心方法。它位于 `base_connection.py`，是 netmiko 中最大的模块。

## 连接生命周期

### 自动连接

默认情况下，`ConnectHandler()` 在对象创建时自动建立连接（`auto_connect=True`）：

```
__init__()
  → _open()
      → _modify_connection_params()    # 子类可修改连接前参数
      → establish_connection()         # 建立底层连接
      → _try_session_preparation()     # 会话初始化
          → session_preparation()      # 终端设置
```

### 手动连接

设置 `auto_connect=False` 可以延迟连接：

```python
from netmiko import ConnectHandler

conn = ConnectHandler(device_type="cisco_ios", host="10.0.0.1",
                      username="admin", password="pass",
                      auto_connect=False)
# 此时连接尚未建立，手动调用 _open() 建立连接
conn._open()
```

### establish_connection

`establish_connection(width=511, height=1000)` 根据协议类型建立连接：

- **SSH**：创建 paramiko SSHClient → 调用 `connect()` → `invoke_shell(term="vt100", width=511, height=1000)` → 迁移到 SSHChannel
- **Telnet**：创建 telnetlib Telnet → 迁移到 TelnetChannel → 调用 `telnet_login()`
- **Serial**：创建 serial.Serial → 迁移到 SerialChannel → 调用 `serial_login()`

### 断开连接

```python
conn.disconnect()
```

`disconnect()` 执行：
1. 调用 `cleanup()`（发送 "exit" 等清理命令，由子类重写）
2. 调用 `paramiko_cleanup()`（关闭 remote_conn 和 remote_conn_pre）
3. 关闭 session_log
4. 移除 SecretsFilter

### 上下文管理器

```python
with ConnectHandler(**device) as conn:
    output = conn.send_command("show version")
# 退出 with 块时自动 disconnect()
```

## session_preparation

`session_preparation()` 是连接建立后的终端初始化方法，基类默认实现：

```python
def session_preparation(self):
    self._test_channel_read()
    self.set_base_prompt()
    self.set_terminal_width()
    self.disable_paging()
```

各厂商驱动重写此方法以适应设备差异：

| 平台 | session_preparation 步骤 |
|------|------------------------|
| Cisco IOS | `terminal width 511` → `terminal length 0` → set_base_prompt |
| Arista EOS | ANSI on → `terminal width 511` → `terminal length 0` → set_base_prompt |
| Juniper Junos | enter CLI → `set cli screen-width 511` → `set cli complete-on-space off` → `set cli screen-length 0` → set_base_prompt |
| Linux | test channel → set_base_prompt（无分页/宽度设置） |
| HP Comware | 处理横幅 → set_base_prompt → `screen-length disable` |

`_try_session_preparation()` 包装了 session_preparation，如果初始化失败会自动调用 disconnect() 清理资源。

## 终端设置方法

### set_base_prompt

识别设备提示符并存储（去除末尾的 `#` 或 `>`）：

```python
conn.set_base_prompt(pri_prompt_terminator="#", alt_prompt_terminator=">")
print(conn.base_prompt)  # 例如 "Router1"
```

Cisco IOS 会将 base_prompt 截断为16字符（IOS 在配置模式下缩写提示符为20字符）。

### disable_paging

禁用输出分页，防止 `show` 命令输出被 `--More--` 中断：

```python
# 默认发送 "terminal length 0"（Cisco 风格）
conn.disable_paging()

# 自定义命令
conn.disable_paging(command="screen-length disable")
```

### set_terminal_width

设置终端宽度防止输出自动换行变形：

```python
conn.set_terminal_width(command="terminal width 511")
```

### find_prompt

发送回车并读取当前提示符（最后一行）：

```python
prompt = conn.find_prompt()
print(prompt)  # "Router1#" 或 "Router1(config)#"
```

### clear_buffer

读取并丢弃通道中的所有待读数据：

```python
conn.clear_buffer()
```

使用指数退避策略，检测到数据时将睡眠时间翻倍（最大3秒），最多读取10次。

## 关键属性

| 属性 | 说明 |
|------|------|
| `host` | 设备主机名或 IP |
| `username` | SSH 用户名 |
| `password` | SSH 密码 |
| `secret` | enable 密码 |
| `port` | 端口号（SSH=22, Telnet=23） |
| `device_type` | 设备类型字符串 |
| `protocol` | `"ssh"`, `"telnet"`, 或 `"serial"` |
| `base_prompt` | 设备主机名提示符（不含 `#`/`>`） |
| `global_delay_factor` | 全局延迟因子 |
| `fast_cli` | 快速 CLI 模式 |
| `session_log` | 会话日志对象 |
| `encoding` | 字符编码（默认 utf-8） |
| `remote_conn` | 底层连接（paramiko.Channel / Telnet / Serial） |
| `remote_conn_pre` | paramiko SSHClient（仅 SSH） |

## 超时控制

netmiko 有多层超时设置：

| 参数 | 默认值 | 用途 |
|------|--------|------|
| `conn_timeout` | 10秒 | TCP 连接超时 |
| `banner_timeout` | 15秒 | 等待 SSH banner |
| `auth_timeout` | None | 等待认证响应 |
| `blocking_timeout` | 20秒 | 通道读取阻塞超时 |
| `session_timeout` | 60秒 | 会话锁等待超时 |

TCP 连接失败会抛出 `NetmikoTimeoutException`，认证失败抛出 `NetmikoAuthenticationException`。
