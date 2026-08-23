---
type: Example
title: 基础连接与命令执行
description: 从创建 SSHClient 到连接服务器、执行命令、读取输出、关闭连接的完整示例
tags: [paramiko, example, connection, exec]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: paramiko-source
    resource: /references/paramiko-source.md
---

# 基础连接与命令执行

## 最简连接

```python
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("example.com", username="myuser", password="mypassword")

stdin, stdout, stderr = client.exec_command("hostname")
print(stdout.read().decode().strip())

client.close()
```

## 使用上下文管理器

推荐使用 `with` 语句自动关闭连接：

```python
import paramiko

with paramiko.SSHClient() as client:
    client.load_system_host_keys()
    client.connect("example.com", username="myuser", key_filename="~/.ssh/id_ed25519")

    stdin, stdout, stderr = client.exec_command("uptime")
    print(stdout.read().decode().strip())
```

## 使用密钥认证

```python
import paramiko

with paramiko.SSHClient() as client:
    client.load_system_host_keys()

    key = paramiko.Ed25519Key.from_private_key_file(
        "/home/user/.ssh/id_ed25519",
        password="my-passphrase",
    )

    client.connect(
        "example.com",
        username="myuser",
        pkey=key,
        timeout=10,
    )

    stdin, stdout, stderr = client.exec_command("whoami")
    print(stdout.read().decode().strip())
```

## 执行命令并获取退出码

```python
import paramiko

with paramiko.SSHClient() as client:
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("example.com", username="user", password="pass")

    stdin, stdout, stderr = client.exec_command("ls -la /tmp")

    output = stdout.read().decode()
    errors = stderr.read().decode()
    exit_code = stdout.channel.recv_exit_status()

    print(f"Exit code: {exit_code}")
    print("Output:")
    print(output)
    if errors:
        print("Errors:")
        print(errors)
```

## 逐行读取输出

```python
import paramiko

with paramiko.SSHClient() as client:
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("example.com", username="user", password="pass")

    stdin, stdout, stderr = client.exec_command("dmesg | tail -20")

    for line in stdout:
        print(line.rstrip())
```

## 向命令传递输入

```python
import paramiko

with paramiko.SSHClient() as client:
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("example.com", username="user", password="pass")

    stdin, stdout, stderr = client.exec_command("cat > /tmp/remote_file.txt")
    stdin.write("Hello from paramiko!\n")
    stdin.write("Line 2\n")
    stdin.channel.shutdown_write()

    exit_code = stdout.channel.recv_exit_status()
    print(f"Write completed with exit code: {exit_code}")
```

## 多命令执行

```python
import paramiko

commands = [
    "uname -a",
    "df -h",
    "free -m",
    "uptime",
]

with paramiko.SSHClient() as client:
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("example.com", username="user", password="pass")

    for cmd in commands:
        stdin, stdout, stderr = client.exec_command(cmd)
        output = stdout.read().decode().strip()
        code = stdout.channel.recv_exit_status()
        print(f"$ {cmd}")
        print(f"  [{code}] {output}")
```

## 带超时的连接

```python
import paramiko
import socket

try:
    with paramiko.SSHClient() as client:
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            "example.com",
            username="user",
            password="pass",
            timeout=10,
            banner_timeout=15,
            auth_timeout=15,
        )
        stdin, stdout, stderr = client.exec_command("sleep 30", timeout=5)
        print(stdout.read().decode())
except socket.timeout:
    print("Operation timed out")
except paramiko.AuthenticationException:
    print("Authentication failed")
except paramiko.ssh_exception.NoValidConnectionsError as e:
    print(f"Could not connect: {e}")
```

## 相关概念

- [5分钟快速上手](/concepts/01-getting-started.md)
- [SSHClient 详解](/concepts/02-ssh-client.md)
- [命令执行模式](/examples/execute-commands.md)
- [交互式 Shell](/examples/interactive-shell.md)

[^paramiko-source]: paramiko 源码信源，见 [paramiko-source.md](/references/paramiko-source.md)。
