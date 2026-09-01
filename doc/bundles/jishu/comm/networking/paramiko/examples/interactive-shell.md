---
type: Example
title: 交互式 Shell 与 invoke_shell
description: 使用 invoke_shell 创建交互式终端会话、实时收发数据、模拟终端操作的完整示例
tags: [paramiko, example, shell, interactive, pty]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: paramiko-source
    resource: /references/paramiko-source.md
---

# 交互式 Shell 与 invoke_shell

## 基本交互式 Shell

```python
import paramiko
import time

with paramiko.SSHClient() as client:
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("example.com", username="user", password="pass")

    chan = client.invoke_shell(term="xterm", width=120, height=40)
    time.sleep(1)

    output = chan.recv(4096).decode(errors="replace")
    print(output, end="")

    chan.send(b"ls -la\n")
    time.sleep(1)
    print(chan.recv(4096).decode(errors="replace"), end="")

    chan.send(b"whoami\n")
    time.sleep(0.5)
    print(chan.recv(4096).decode(errors="replace"), end="")

    chan.close()
```

## 使用 select 实时交互

```python
import paramiko
import select
import sys

with paramiko.SSHClient() as client:
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("example.com", username="user", password="pass")

    chan = client.invoke_shell(term="xterm-256color", width=120, height=40)

    while True:
        r, w, x = select.select([chan, sys.stdin], [], [])
        if chan in r:
            data = chan.recv(4096)
            if not data:
                print("\nConnection closed")
                break
            sys.stdout.write(data.decode(errors="replace"))
            sys.stdout.flush()
        if sys.stdin in r:
            line = sys.stdin.readline()
            if not line:
                break
            chan.send(line.encode())
```

## 执行全屏程序

```python
import paramiko
import time

with paramiko.SSHClient() as client:
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("example.com", username="user", password="pass")

    chan = client.invoke_shell(term="xterm", width=120, height=40)
    time.sleep(1)
    chan.recv(4096)

    chan.send(b"top -bn1\n")
    time.sleep(2)
    output = chan.recv(65536).decode(errors="replace")
    print(output)

    chan.send(b"clear\n")
    time.sleep(0.5)
    chan.recv(4096)

    chan.send(b"df -h\n")
    time.sleep(1)
    print(chan.recv(4096).decode(errors="replace"))
```

## 调整终端大小

```python
import paramiko
import time

with paramiko.SSHClient() as client:
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("example.com", username="user", password="pass")

    chan = client.invoke_shell(term="xterm", width=80, height=24)
    time.sleep(1)
    chan.recv(4096)

    chan.resize_pty(width=160, height=50, width_pixels=0, height_pixels=0)
    time.sleep(0.5)
    chan.recv(4096)

    chan.send(b"stty size\n")
    time.sleep(0.5)
    print(chan.recv(4096).decode(errors="replace"))
```

## 使用 Channel 直接创建 Shell

```python
import paramiko
import time

with paramiko.SSHClient() as client:
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("example.com", username="user", password="pass")

    transport = client.get_transport()
    chan = transport.open_session()
    chan.get_pty(term="vt100", width=80, height=24)
    chan.invoke_shell()

    time.sleep(1)
    print(chan.recv(4096).decode(errors="replace"))

    chan.send(b"echo Hello from shell\n")
    time.sleep(0.5)
    print(chan.recv(4096).decode(errors="replace"))
```

## 带环境变量的 Shell

```python
import paramiko
import time

with paramiko.SSHClient() as client:
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("example.com", username="user", password="pass")

    chan = client.invoke_shell(
        term="xterm",
        width=80,
        height=24,
        environment={"MY_VAR": "hello", "DEBUG": "1"},
    )
    time.sleep(1)
    chan.recv(4096)

    chan.send(b"echo $MY_VAR\n")
    time.sleep(0.5)
    print(chan.recv(4096).decode(errors="replace"))
```

## 非阻塞读取

```python
import paramiko
import socket
import time

with paramiko.SSHClient() as client:
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("example.com", username="user", password="pass")

    chan = client.invoke_shell()
    chan.settimeout(0.0)
    time.sleep(1)

    chan.send(b"for i in $(seq 1 5); do echo line-$i; sleep 0.5; done\n")

    output = b""
    deadline = time.time() + 5
    while time.time() < deadline:
        try:
            data = chan.recv(4096)
            if not data:
                break
            output += data
        except socket.timeout:
            pass
        time.sleep(0.1)

    print(output.decode(errors="replace"))
```

## 登录后自动执行命令序列

```python
import paramiko
import time

def wait_for_prompt(chan, prompt="$", timeout=10):
    buf = b""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if chan.recv_ready():
            buf += chan.recv(4096)
            if buf.rstrip().endswith(prompt.encode()):
                return buf.decode(errors="replace")
        time.sleep(0.1)
    return buf.decode(errors="replace")

with paramiko.SSHClient() as client:
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("example.com", username="user", password="pass")

    chan = client.invoke_shell(term="xterm")

    print(wait_for_prompt(chan), end="")

    commands = [
        "cd /tmp",
        "mkdir -p mywork",
        "cd mywork",
        "echo 'done' > status.txt",
        "cat status.txt",
    ]

    for cmd in commands:
        chan.send(cmd.encode() + b"\n")
        output = wait_for_prompt(chan)
        print(output, end="")

    chan.send(b"exit\n")
    chan.close()
```

## invoke_shell 与 exec_command 的选择

| 场景 | 使用 |
|------|------|
| 执行单条命令获取输出 | `exec_command` |
| 需要屏幕控制（vim/top/htop） | `invoke_shell` |
| 多条命令共享 shell 状态 | `invoke_shell` |
| 需要 sudo 密码交互 | `exec_command(get_pty=True)` 或 `invoke_shell` |
| 自动化脚本解析输出 | `exec_command`（更干净） |
| 模拟真实终端用户行为 | `invoke_shell` |

## 相关概念

- [SSHClient 详解](../concepts/02-ssh-client.md)
- [Channel 通道](../concepts/04-channel.md)
- [基础连接示例](basic-connection.md)
- [命令执行模式](execute-commands.md)

[^paramiko-source]: paramiko 源码信源，见 [paramiko-source.md](../references/paramiko-source.md)。
