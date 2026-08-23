---
type: Concept
title: SSHClient 详解
description: SSHClient 高层接口全解析——connect、exec_command、invoke_shell、open_sftp、主机密钥策略
tags: [paramiko, ssh-client, api]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: paramiko-source
    resource: /references/paramiko-source.md
---

# SSHClient 详解

## SSHClient 的定位

`SSHClient` 是 paramiko 最高层的 API，封装了创建 `Transport`、密钥交换、认证、打开通道的完整流程。它内部组合了 `Transport`、`Channel`、`SFTPClient` 和 `HostKeys`，是大多数应用的入口点。

`SSHClient` 继承 `ClosingContextManager`，可作为上下文管理器使用。

## 创建客户端

```python
import paramiko

client = paramiko.SSHClient()
```

构造函数不接受参数，初始化以下内部状态：

- `_system_host_keys`：系统级只读主机密钥（`HostKeys` 实例）
- `_host_keys`：应用级可写主机密钥（`HostKeys` 实例）
- `_policy`：未知主机密钥策略，默认 `RejectPolicy()`
- `_transport`：底层 Transport 实例，初始为 None
- `_agent`：SSH Agent 连接，初始为 None

## 主机密钥管理

### 加载已知主机密钥

```python
client.load_system_host_keys()
client.load_system_host_keys("/path/to/known_hosts")

client.load_host_keys("/path/to/custom_known_hosts")
```

- `load_system_host_keys(filename=None)`：加载只读密钥。filename 为 None 时尝试读取 `~/.ssh/known_hosts`，文件不存在不报错。这些密钥不会被 `save_host_keys` 写回。
- `load_host_keys(filename)`：加载可写密钥文件。AutoAddPolicy 添加的新密钥会保存到此文件。

### 保存主机密钥

```python
client.save_host_keys("/path/to/known_hosts")
```

仅保存通过 `load_host_keys` 加载或运行时添加的密钥，不包含系统密钥。

### 设置未知主机密钥策略

```python
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
```

三种内置策略：

| 策略 | 行为 | 安全性 |
|------|------|--------|
| `RejectPolicy`（默认） | 抛出 `SSHException`，拒绝连接 | 最高 |
| `AutoAddPolicy` | 自动添加并保存到本地 known_hosts | 低（易受 MITM） |
| `WarningPolicy` | 发出 Python warning 但接受连接 | 中 |

参数可以是类或实例，内部通过 `inspect.isclass()` 判断后自动实例化。

### 自定义策略

继承 `MissingHostKeyPolicy` 并实现 `missing_host_key(client, hostname, key)` 方法：

```python
class AskUserPolicy(paramiko.MissingHostKeyPolicy):
    def missing_host_key(self, client, hostname, key):
        fingerprint = key.get_fingerprint().hex()
        response = input(f"Accept key {fingerprint} for {hostname}? [y/N] ")
        if response.lower() != "y":
            raise paramiko.SSHException(f"Key rejected for {hostname}")
        client._host_keys.add(hostname, key.get_name(), key)
```

## 连接服务器

`connect()` 是核心方法，完整签名：

```python
client.connect(
    hostname,
    port=22,
    username=None,
    password=None,
    pkey=None,
    key_filename=None,
    timeout=None,
    allow_agent=True,
    look_for_keys=True,
    compress=False,
    sock=None,
    banner_timeout=None,
    auth_timeout=None,
    channel_timeout=None,
    passphrase=None,
    disabled_algorithms=None,
    transport_factory=None,
    auth_strategy=None,
)
```

### 连接流程

1. **地址解析**：通过 `socket.getaddrinfo()` 获取 IPv4/IPv6 地址列表
2. **TCP 连接**：逐个地址尝试，全部失败抛 `NoValidConnectionsError`
3. **Transport 创建**：使用 `transport_factory`（默认 `Transport`）
4. **密钥交换**：调用 `start_client()` 执行 SSH 握手
5. **主机密钥验证**：检查 system_host_keys → host_keys → policy
6. **认证**：按优先级尝试多种认证方式
7. 返回 `None`（旧认证模式）或 `AuthResult`（使用 auth_strategy 时）

### 多协议支持

connect() 自动处理 IPv4/IPv6 双栈：

```python
try:
    client.connect("example.com", username="user", password="pass")
except paramiko.ssh_exception.NoValidConnectionsError as e:
    print(f"All addresses failed: {e.errors}")
```

### 使用现有 socket

通过 `sock` 参数传入已连接的 socket：

```python
import socket
sock = socket.create_connection(("example.com", 22))
client.connect("example.com", sock=sock, username="user", password="pass")
```

### 禁用算法

```python
client.connect(
    "example.com",
    username="user",
    password="pass",
    disabled_algorithms={
        "kex": ["diffie-hellman-group16-sha512"],
        "ciphers": ["3des-cbc"],
    },
)
```

可禁用的算法类型键名：`"ciphers"`、`"macs"`（digests）、`"keys"`（key_types）、`"kex"`、`"compression"`。

## 执行命令

### exec_command

```python
stdin, stdout, stderr = client.exec_command("ls -la")
print(stdout.read().decode())
error = stderr.read().decode()
exit_status = stdout.channel.recv_exit_status()
```

完整签名：

```python
client.exec_command(
    command,
    bufsize=-1,
    timeout=None,
    get_pty=False,
    environment=None,
)
```

返回三元组 `(stdin, stdout, stderr)`，分别是 `ChannelStdinFile`、`ChannelFile`、`ChannelStderrFile`。

参数说明：

- `command`：要执行的命令字符串
- `bufsize`：同 Python 内建 `open()` 的缓冲参数
- `timeout`：通道超时秒数
- `get_pty`：是否请求伪终端（对 sudo 等需要 tty 的命令有用）
- `environment`：dict 类型的环境变量（服务器可能静默拒绝）

### 使用 PTY

```python
stdin, stdout, stderr = client.exec_command("sudo apt update", get_pty=True)
stdin.write("password\n")
stdin.flush()
print(stdout.read().decode())
```

### 传递环境变量

```python
stdin, stdout, stderr = client.exec_command(
    "echo $MY_VAR",
    environment={"MY_VAR": "hello"}
)
```

> 注意：SSH 服务器可能配置为拒绝某些或所有环境变量（sshd_config 的 `AcceptEnv`）。

## 交互式 Shell

```python
chan = client.invoke_shell(
    term="vt100",
    width=80,
    height=24,
    width_pixels=0,
    height_pixels=0,
    environment=None,
)
```

返回 `Channel` 对象，已请求 PTY 并启动 shell。适用于需要全屏交互的程序（top、vim、tmux）。

与 `exec_command` 的区别：

| 特性 | exec_command | invoke_shell |
|------|-------------|--------------|
| 用途 | 单条命令 | 交互式会话 |
| PTY | 可选 | 自动请求 |
| 返回 | (stdin, stdout, stderr) | Channel |
| Shell 状态 | 每次新会话 | 持续保持 |
| 适合 | 脚本自动化 | 终端模拟 |

## SFTP 会话

```python
sftp = client.open_sftp()
```

委托给 `Transport.open_sftp_client()`，返回 `SFTPClient` 实例。

## 获取底层 Transport

```python
transport = client.get_transport()
if transport.is_authenticated():
    print("Connected as", transport.get_username())
```

通过 Transport 可以执行更底层的操作：直接打开通道、端口转发、自定义认证等。

## 关闭连接

```python
client.close()
```

关闭底层 Transport 和 Agent 连接。也推荐使用 `with` 语句自动关闭。

> **重要**：paramiko 注册了垃圾回收钩子尝试自动关闭，但不可靠。源码文档明确警告：不显式关闭可能导致进程退出时挂起。

## 日志配置

```python
client.set_log_channel("myapp.ssh")
```

设置 paramiko transport 的日志 channel 名，默认为 `"paramiko.transport"`。

## 相关概念

- [5分钟快速上手](/concepts/01-getting-started.md)
- [Transport 底层传输](/concepts/03-transport.md)
- [Channel 通道](/concepts/04-channel.md)
- [认证体系](/concepts/05-authentication.md)
- [SFTP 文件传输](/concepts/07-sftp.md)
- [基础连接示例](/examples/basic-connection.md)

[^paramiko-source]: paramiko 源码信源，见 [paramiko-source.md](/references/paramiko-source.md)。
