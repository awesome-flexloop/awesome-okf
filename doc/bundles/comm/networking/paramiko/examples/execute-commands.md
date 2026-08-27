---
type: Example
title: 多种命令执行模式
description: exec_command、PTY 模式、sudo 命令、长时间命令、环境变量传递等命令执行技巧
tags: [paramiko, example, exec, pty, sudo]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: paramiko-source
    resource: /references/paramiko-source.md
---

# 多种命令执行模式

## 简单命令执行

```python
import paramiko

with paramiko.SSHClient() as client:
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("example.com", username="user", password="pass")

    stdin, stdout, stderr = client.exec_command("ls -la /home/user")
    print(stdout.read().decode())
```

## 使用 PTY 执行 sudo 命令

```python
import paramiko
import time

with paramiko.SSHClient() as client:
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("example.com", username="user", password="pass")

    stdin, stdout, stderr = client.exec_command(
        "sudo -S apt-get update",
        get_pty=True,
    )
    stdin.write("user-sudo-password\n")
    stdin.flush()

    for line in stdout:
        print(line.rstrip())
```

## 执行长时间命令并实时输出

```python
import paramiko
import select

with paramiko.SSHClient() as client:
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("example.com", username="user", password="pass")

    transport = client.get_transport()
    transport.set_keepalive(30)

    chan = transport.open_session()
    chan.exec_command("for i in $(seq 1 10); do echo $i; sleep 1; done")

    while not chan.exit_status_ready():
        while chan.recv_ready():
            data = chan.recv(4096).decode()
            print(data, end="")
        while chan.recv_stderr_ready():
            data = chan.recv_stderr(4096).decode()
            print(data, end="")
        select.select([chan], [], [], 1.0)

    while chan.recv_ready():
        print(chan.recv(4096).decode(), end="")

    print(f"\nExit status: {chan.recv_exit_status()}")
```

## 传递环境变量

```python
import paramiko

with paramiko.SSHClient() as client:
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("example.com", username="user", password="pass")

    stdin, stdout, stderr = client.exec_command(
        "echo $MY_APP_ENV && echo $MY_APP_MODE",
        environment={
            "MY_APP_ENV": "production",
            "MY_APP_MODE": "debug",
        },
    )
    print(stdout.read().decode())
```

## 使用 Channel 直接执行

```python
import paramiko

with paramiko.SSHClient() as client:
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("example.com", username="user", password="pass")

    chan = client.get_transport().open_session()
    chan.exec_command("uname -r")

    output = b""
    while True:
        data = chan.recv(4096)
        if not data:
            break
        output += data

    print(output.decode())
    print(f"Exit: {chan.recv_exit_status()}")
```

## 合并 stderr 到 stdout

```python
import paramiko

with paramiko.SSHClient() as client:
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("example.com", username="user", password="pass")

    chan = client.get_transport().open_session()
    chan.set_combine_stderr(True)
    chan.exec_command("ls /nonexistent")

    output = chan.makefile("r").read()
    print(f"Combined output:\n{output}")
    print(f"Exit: {chan.recv_exit_status()}")
```

## 执行多条命令（同一 shell 会话）

`exec_command` 每次打开新通道，命令之间无状态保持。如需在同一 shell 中执行多条命令：

```python
import paramiko
import time

with paramiko.SSHClient() as client:
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("example.com", username="user", password="pass")

    chan = client.invoke_shell()
    time.sleep(1)
    chan.recv(4096)

    commands = [
        "cd /tmp",
        "mkdir -p test_dir",
        "cd test_dir",
        "pwd",
        "echo 'hello' > test.txt",
        "cat test.txt",
        "cd ..",
        "rm -rf test_dir",
        "exit",
    ]

    for cmd in commands:
        chan.send(cmd.encode() + b"\n")
        time.sleep(0.3)

    output = b""
    while chan.recv_ready():
        output += chan.recv(4096)

    print(output.decode(errors="replace"))
```

## 使用 AuthStrategy 执行命令

```python
import getpass
import paramiko
from paramiko.auth_strategy import AuthStrategy, Password, InMemoryPrivateKey

class MyAuthStrategy(AuthStrategy):
    def get_sources(self):
        config = self.ssh_config
        username = config.get("user", "default-user")

        yield InMemoryPrivateKey(
            username=username,
            pkey=paramiko.Ed25519Key.from_private_key_file("~/.ssh/id_ed25519"),
        )
        yield Password(
            username=username,
            password_getter=lambda: getpass.getpass("Password: "),
        )

config = {"user": "myuser"}
strategy = MyAuthStrategy(ssh_config=config)

with paramiko.SSHClient() as client:
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    result = client.connect("example.com", auth_strategy=strategy)
    print("Auth result:")
    for sr in result:
        print(f"  {sr.source} -> {sr.result or 'success'}")

    stdin, stdout, stderr = client.exec_command("id")
    print(stdout.read().decode())
```

## 相关概念

- [SSHClient 详解](../concepts/02-ssh-client.md)
- [Channel 通道](../concepts/04-channel.md)
- [认证体系](../concepts/05-authentication.md)
- [交互式 Shell 示例](interactive-shell.md)

[^paramiko-source]: paramiko 源码信源，见 [paramiko-source.md](../references/paramiko-source.md)。
