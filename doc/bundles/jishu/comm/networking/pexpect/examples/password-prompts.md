---
type: Example
title: 密码提示自动响应
description: 自动响应各类密码提示、sudo 密码、SSH 密码短语、多阶段认证
tags: [pexpect, example, password, sudo, authentication]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: pexpect-source
    resource: /references/pexpect-source.md
---

# 密码提示自动响应

## SSH 密码自动登录

```python
import pexpect

child = pexpect.spawn('ssh user@host', encoding='utf-8', timeout=30)

i = child.expect([
    r'(?i)password:',           # 0: 密码提示
    r'(?i)are you sure.*\(yes/no', # 1: 主机密钥确认
    r'[$#] ',                   # 2: 已到提示符（密钥认证）
    pexpect.EOF,                # 3: 连接断开
    pexpect.TIMEOUT,            # 4: 超时
])

if i == 0:
    child.sendline('mypassword')
    child.expect(r'[$#] ')
elif i == 1:
    child.sendline('yes')
    child.expect(r'(?i)password:')
    child.sendline('mypassword')
    child.expect(r'[$#] ')
elif i == 2:
    pass
elif i == 3:
    print(f'Connection closed: {child.before}')
elif i == 4:
    print(f'Timeout: {child.before}')

child.sendline('whoami')
child.expect(r'[$#] ')
print(child.before)
child.close()
```

## sudo 密码

```python
import pexpect

child = pexpect.spawn('sudo apt update', encoding='utf-8', timeout=120)

i = child.expect([
    r'(?i)\[sudo\] password for .*:',  # 0: sudo 密码提示
    pexpect.EOF,                        # 1: 无需密码或完成
    pexpect.TIMEOUT,                    # 2: 超时
])

if i == 0:
    child.sendline('sudopassword')
    child.expect(pexpect.EOF)
    print(child.before)
elif i == 1:
    print(child.before)
elif i == 2:
    print('Command timed out')
```

## 使用 run() 处理密码

对于一次性命令，`run()` 配合 events 更简洁：

```python
import pexpect

# SCP 文件传输
output = pexpect.run(
    'scp file.txt user@host:/tmp/',
    events={'(?i)password:': 'mypassword\n'},
    timeout=60,
    withexitstatus=True
)
print(f'Exit status: {output[1]}')

# sudo 命令
output = pexpect.run(
    'sudo ls /root',
    events={r'(?i)\[sudo\] password': 'mypassword\n'},
    withexitstatus=True
)
```

## 多阶段密码认证

有些系统需要多次密码输入（如 su 切换用户、数据库连接）：

```python
import pexpect

child = pexpect.spawn('su - postgres', encoding='utf-8', timeout=30)
child.expect('Password:')
child.sendline('root_password')
child.expect(r'[$#] ')

child.sendline('psql -d mydb')
child.expect(r'=# ')
child.sendline("SELECT count(*) FROM users;")
child.expect(r'=# ')
print(child.before)
child.sendline('\\q')
child.expect(r'[$#] ')
child.sendline('exit')
child.close()
```

## SSH 密钥密码短语

```python
import pexpect

child = pexpect.spawn(
    'ssh -i ~/.ssh/encrypted_key user@host',
    encoding='utf-8',
    timeout=30
)

i = child.expect([
    r'Enter passphrase for key .*:',  # 0: 密钥密码短语
    r'(?i)password:',                  # 1: 登录密码
    r'[$#] ',                          # 2: 直接到提示符
])

if i == 0:
    child.sendline('key_passphrase')
    child.expect(r'[$#] ')
elif i == 1:
    child.sendline('login_password')
    child.expect(r'[$#] ')

child.sendline('hostname')
child.expect(r'[$#] ')
print(child.before)
child.close()
```

## 使用 waitnoecho() 精确检测密码提示

密码输入时终端会关闭回显。`waitnoecho()` 可以检测这一状态，比匹配提示文字更可靠：

```python
import pexpect

child = pexpect.spawn('ssh user@host', encoding='utf-8', timeout=30)

# 等待终端关闭回显（表示远端正在等待密码输入）
if child.waitnoecho(timeout=10):
    child.sendline('mypassword')
    child.expect(r'[$#] ')
    print('Login successful')
else:
    # 可能是密钥认证直接登录，检查提示符
    i = child.expect([r'[$#] ', pexpect.TIMEOUT])
    if i == 0:
        print('Key-based login')
    else:
        print('Login failed')
```

## 避免密码回显

PTY 默认回显输入，如果在应用关闭回显前发送密码，密码会出现在输出中：

```python
import pexpect

# 方法 1: 使用 delaybeforesend（默认已启用，50ms 延迟）
child = pexpect.spawn('ssh user@host', encoding='utf-8')
child.expect('password:')
child.sendline('mypassword')  # 默认有 50ms 延迟

# 方法 2: 启动时禁用回显
child = pexpect.spawn('ssh user@host', echo=False, encoding='utf-8')

# 方法 3: 运行时关闭回显
child = pexpect.spawn('ssh user@host', encoding='utf-8')
child.setecho(False)
child.waitnoecho()
child.expect('password:')
child.sendline('mypassword')

# 方法 4: 调整延迟时间
child.delaybeforesend = 0.1  # 增加到 100ms
```

## 密码不记录到日志

自动化中需避免密码被 logfile 记录：

```python
import pexpect
import sys

child = pexpect.spawn('ssh user@host', encoding='utf-8',
                      logfile_read=sys.stdout)  # 只记录读取，不记录发送

child.expect('password:')
child.sendline('secret123')  # 不会出现在日志中

# 登录后可以记录所有内容
child.expect(r'[$#] ')
child.logfile_send = sys.stdout  # 之后的发送也记录（无敏感信息）
```

## pxssh 的 force_password

当 ssh-agent 运行时，SSH 可能优先尝试密钥认证。强制密码认证：

```python
from pexpect import pxssh

s = pxssh.pxssh()
s.force_password = True  # 添加 -o PubkeyAuthentication=no
s.login('host', 'user', 'password')
s.sendline('uptime')
s.prompt()
print(s.before.decode())
s.logout()
```

## 安全注意事项

1. **不要在代码中硬编码密码**：从环境变量、密钥管理服务或配置文件（权限 600）读取。
2. **使用 `logfile_read` 而非 `logfile`**：避免发送的密码被记录。
3. **优先使用密钥认证**：配置 SSH 密钥后无需处理密码提示。
4. **使用 ssh_config**：将主机配置和密钥路径放在 `~/.ssh/config` 中，pxssh 通过 `ssh_config` 参数读取。

```python
import os
from pexpect import pxssh

password = os.environ.get('SSH_PASSWORD')
if not password:
    raise RuntimeError("SSH_PASSWORD environment variable not set")

s = pxssh.pxssh()
s.login('host', 'user', password)
```

## 相关概念

- [发送与交互](../concepts/04-send-interact.md)
- [pxssh SSH 自动化](../concepts/05-pxssh.md)
- [SSH 自动登录](ssh-login-automation.md)
- [spawn 类详解](../concepts/02-spawn-class.md)

[^pexpect-source]: pexpect 源码信源，见 [pexpect-source.md](../references/pexpect-source.md)。
