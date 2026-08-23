---
type: Concept
title: ConnectHandler 工厂
description: ConnectHandler 工厂函数、设备参数字典、ssh_dispatcher 类映射、redispatch 动态切换
tags: [netmiko, ConnectHandler, factory, dispatcher, redispatch]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: netmiko-source
    resource: /references/netmiko-source.md
---

# ConnectHandler 工厂

## 工厂函数

`ConnectHandler(*args, **kwargs)` 是 netmiko 的主入口点。它是一个工厂函数，根据 `device_type` 参数选择对应的驱动类并实例化：

```python
def ConnectHandler(*args, **kwargs):
    device_type = kwargs["device_type"]
    if device_type not in platforms:
        raise ValueError("Unsupported 'device_type' ...")
    ConnectionClass = ssh_dispatcher(device_type)
    return ConnectionClass(*args, **kwargs)
```

该函数位于 `ssh_dispatcher.py`，执行三步：
1. 从 kwargs 中提取 `device_type`
2. 校验 device_type 是否在 `platforms` 列表中
3. 调用 `ssh_dispatcher(device_type)` 获取驱动类，实例化并返回

## ssh_dispatcher 类映射

`ssh_dispatcher(device_type)` 是一个简单的字典查找函数：

```python
def ssh_dispatcher(device_type):
    return CLASS_MAPPER[device_type]
```

`CLASS_MAPPER` 字典的构建过程：
1. `CLASS_MAPPER_BASE` 定义约170个基础 device_type → 驱动类映射
2. 自动为每个 key 生成 `_ssh` 后缀别名（如 `"cisco_ios"` 和 `"cisco_ios_ssh"` 都映射到 `CiscoIosSSH`）
3. 追加约60个 `_telnet` 驱动
4. 追加2个 `_serial` 驱动
5. `"terminal_server"` 和 `"autodetect"` 映射到 `TerminalServerSSH`

```python
from netmiko.ssh_dispatcher import CLASS_MAPPER, ssh_dispatcher

# 查看某个 device_type 对应的类
print(CLASS_MAPPER["cisco_ios"])       # <class 'netmiko.cisco.cisco_ios.CiscoIosSSH'>
print(CLASS_MAPPER["arista_eos"])     # <class 'netmiko.arista.arista.AristaSSH'>
print(CLASS_MAPPER["juniper_junos"])  # <class 'netmiko.juniper.juniper.JuniperSSH'>
```

## platforms 列表

`platforms` 是 `CLASS_MAPPER` 所有 key 的排序列表：

```python
from netmiko import platforms

# platforms 包含 _ssh 后缀变体、_telnet 变体等
print(len(platforms))  # 约 400+ 个条目

# platforms_base 仅包含基础名称（无后缀）
from netmiko.ssh_dispatcher import platforms_base
print(len(platforms_base))  # 约 170 个
```

## redispatch 动态切换

`redispatch(obj, device_type, session_prep=True)` 允许在运行时动态改变连接对象的类：

```python
from netmiko import ConnectHandler, redispatch

# 先连接到终端服务器
conn = ConnectHandler(device_type="terminal_server", host="term-server",
                      username="admin", password="pass")

# 通过终端服务器连接到内部设备后，切换到 Cisco IOS 驱动
conn.write_channel("ssh admin@10.0.0.1\n")
# ... 处理登录 ...

# 动态切换驱动类
redispatch(conn, device_type="cisco_ios")

# 现在可以使用 Cisco IOS 特有的方法
conn.send_command("show version")
```

`redispatch` 的工作原理：
1. 通过 `ssh_dispatcher(device_type)` 获取新类
2. 设置 `obj.device_type = device_type`
3. 修改 `obj.__class__ = new_class`（Python 允许在运行时改变对象的类）
4. 如果 `session_prep=True`，调用 `obj._try_session_preparation()` 重新初始化会话

## 其他工厂变体

### TelnetFallback

SSH 连接失败时自动回退到 Telnet：

```python
from netmiko import TelnetFallback

conn = TelnetFallback(device_type="cisco_ios", host="10.0.0.1",
                      username="admin", password="pass")
# 如果 SSH 超时，自动尝试 cisco_ios_telnet
```

### ConnLogOnly

连接失败时返回 `None` 而非抛出异常，并将错误写入日志文件：

```python
from netmiko import ConnLogOnly

conn = ConnLogOnly(device_type="cisco_ios", host="10.0.0.1",
                   username="admin", password="pass",
                   log_file="netmiko_errors.log")
if conn is None:
    print("连接失败，查看日志")
```

### ConnUnify

将所有连接异常统一包装为 `ConnectionException`：

```python
from netmiko import ConnUnify, ConnectionException

try:
    conn = ConnUnify(device_type="cisco_ios", host="10.0.0.1",
                     username="admin", password="pass")
except ConnectionException as e:
    print(f"连接失败: {e}")
```

## FileTransfer 工厂

`FileTransfer(*args, **kwargs)` 是文件传输的工厂函数，根据 device_type 选择对应的 FileTransfer 类：

```python
from netmiko import FileTransfer

# FileTransfer 从 ssh_conn 参数获取 device_type
scp_transfer = FileTransfer(
    ssh_conn=conn,
    source_file="config.txt",
    dest_file="config.txt",
    file_system="flash:",
    direction="put",
)
```

仅18个平台在 `FILE_TRANSFER_MAP` 中有专用 FileTransfer 类，其他平台需要使用通用 SCP 或 InLineTransfer。
