---
type: Example
title: SSH 自动登录
description: 使用 pxssh 自动化 SSH 登录、执行命令、处理密码提示和主机密钥确认
tags: [pexpect, example, ssh, pxssh, login]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: pexpect-source
    resource: /references/pexpect-source.md
---

# SSH 自动登录

## 最简 SSH 登录

```python
from pexpect import pxssh

s = pxssh.pxssh()
s.login('remote-host', 'username', 'password')
s.sendline('uptime')
s.prompt()
print(s.before.decode())
s.logout()
```

## 完整的 SSH 登录函数

```python
from pexpect import pxssh
import sys

def ssh_execute(host, username, password, commands, port=22, timeout=30):
    """
    登录远程主机并执行多条命令，返回输出列表。
    """
    results = []
    try:
        s = pxssh.pxssh(timeout=timeout, port=port)
        s.login(host, username, password)

        for cmd in commands:
            s.sendline(cmd)
            if s.prompt(timeout=timeout):
                results.append(s.before.decode())
            else:
                results.append(f"[TIMEOUT] Command: {cmd}")

        s.logout()
        return results

    except pxssh.ExceptionPxssh as e:
        print(f"SSH error: {e}", file=sys.stderr)
        raise
```

使用：

```python
outputs = ssh_execute(
    'example.com',
    'myuser',
    'mypassword',
    ['hostname', 'uname -a', 'df -h', 'free -m']
)
for cmd_out in outputs:
    print(cmd_out)
```

## 使用密钥认证

```python
from pexpect import pxssh

s = pxssh.pxssh()
s.login('example.com', 'myuser', ssh_key='/home/user/.ssh/id_ed25519')
s.prompt()
s.sendline('whoami')
s.prompt()
print(s.before.decode())
s.logout()
```

## 首次连接自动接受主机密钥

pxssh 的 `login()` 自动处理首次连接的主机密钥确认：

```python
from pexpect import pxssh

s = pxssh.pxssh()
# 首次连接时自动发送 "yes" 接受主机密钥
s.login('new-host.example.com', 'user', 'password',
        auto_prompt_reset=True)
s.sendline('hostname')
s.prompt()
print(s.before.decode())
s.logout()
```

底层机制：login() 的模式列表包含 `"(?i)are you sure you want to continue connecting"`，匹配时自动发送 `yes`。

## 禁用主机密钥检查

```python
from pexpect import pxssh

s = pxssh.pxssh(options={
    "StrictHostKeyChecking": "no",
    "UserKnownHostsFile": "/dev/null",
    "LogLevel": "ERROR",
})
s.login('host', 'user', 'password')
```

> **安全警告**：禁用主机密钥检查使连接易受中间人攻击（MITM），仅用于测试环境。

## 强制密码认证

当 ssh-agent 运行时，pxssh 可能尝试密钥认证。强制密码认证：

```python
from pexpect import pxssh

s = pxssh.pxssh()
s.force_password = True
s.login('host', 'user', 'password')
```

## 上下文管理器

```python
from pexpect import pxssh

with pxssh.pxssh(encoding='utf-8') as s:
    s.login('host', 'user', 'password')
    s.sendline('ls -la')
    s.prompt()
    print(s.before)
```

## 记录会话日志

```python
import sys
from pexpect import pxssh

s = pxssh.pxssh(encoding='utf-8', logfile=sys.stdout)
s.login('host', 'user', 'password')
s.sendline('dmesg | tail -5')
s.prompt()
s.logout()
```

## 使用 spawn 手动控制 SSH

如果 pxssh 的自动化逻辑不满足需求，可以直接使用 spawn：

```python
import pexpect
import sys

child = pexpect.spawn('ssh user@host', encoding='utf-8', timeout=30)

i = child.expect([
    r'(?i)password:',
    r'(?i)are you sure you want to continue connecting',
    r'[$#] ',
    pexpect.EOF,
    pexpect.TIMEOUT,
])

if i == 0:
    child.sendline('mypassword')
    child.expect(r'[$#] ')
elif i == 1:
    child.sendline('yes')
    child.expect(r'(?i)password:')
    child.sendline('mypassword')
    child.expect(r'[$#] ')
elif i == 3:
    print(f"Connection closed: {child.before}")
    sys.exit(1)
elif i == 4:
    print(f"Timeout: {child.before}")
    sys.exit(1)

child.sendline('uptime')
child.expect(r'[$#] ')
print(child.before)
child.sendline('exit')
child.close()
```

## 相关概念

- [pxssh SSH 自动化](/concepts/05-pxssh.md)
- [密码提示处理](/examples/password-prompts.md)
- [spawn 类详解](/concepts/02-spawn-class.md)
- [expect 模式匹配](/concepts/03-expect-patterns.md)

[^pexpect-source]: pexpect 源码信源，见 [pexpect-source.md](/references/pexpect-source.md)。
