---
type: Example
title: FTP 交互自动化
description: 使用 pexpect 自动化 FTP 登录、文件上传下载、目录操作
tags: [pexpect, example, ftp, automation]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: pexpect-source
    resource: /references/pexpect-source.md
---

# FTP 交互自动化

## 基础 FTP 登录与列目录

```python
import pexpect

child = pexpect.spawn('ftp ftp.example.com', encoding='utf-8', timeout=30)

child.expect('Name .*: ')
child.sendline('anonymous')
child.expect('Password:')
child.sendline('user@example.com')
child.expect('ftp> ')

child.sendline('ls')
child.expect('ftp> ')
print(child.before)

child.sendline('bye')
child.close()
```

## 完整 FTP 操作类

```python
import pexpect

class FTPClient:
    def __init__(self, host, username='anonymous', password='user@example.com',
                 timeout=30):
        self.child = pexpect.spawn(f'ftp {host}', encoding='utf-8',
                                   timeout=timeout)
        self.child.expect('Name .*: ')
        self.child.sendline(username)
        self.child.expect('Password:')
        self.child.sendline(password)
        idx = self.child.expect(['ftp> ', 'Login failed', pexpect.EOF,
                                 pexpect.TIMEOUT])
        if idx != 0:
            raise ConnectionError(f'FTP login failed: {self.child.before}')

    def ls(self, path=''):
        self.child.sendline(f'ls {path}')
        self.child.expect('ftp> ')
        return self.child.before

    def cd(self, path):
        self.child.sendline(f'cd {path}')
        idx = self.child.expect(['ftp> ', 'failed'])
        return idx == 0

    def pwd(self):
        self.child.sendline('pwd')
        self.child.expect('ftp> ')
        return self.child.before.strip()

    def get(self, remote, local=None):
        cmd = f'get {remote}' + (f' {local}' if local else '')
        self.child.sendline(cmd)
        idx = self.child.expect(['ftp> ', 'cannot open', pexpect.TIMEOUT])
        return idx == 0

    def put(self, local, remote=None):
        cmd = f'put {local}' + (f' {remote}' if remote else '')
        self.child.sendline(cmd)
        idx = self.child.expect(['ftp> ', 'cannot open', pexpect.TIMEOUT])
        return idx == 0

    def binary(self):
        self.child.sendline('binary')
        self.child.expect('ftp> ')

    def quit(self):
        self.child.sendline('bye')
        self.child.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        try:
            self.quit()
        except Exception:
            self.child.close()


with FTPClient('ftp.example.com', 'user', 'pass') as ftp:
    print(ftp.pwd())
    print(ftp.ls())
    ftp.cd('/pub/files')
    ftp.binary()
    ftp.get('data.tar.gz', '/tmp/data.tar.gz')
```

## 使用 run() 简化 FTP

对于简单场景，`run()` 配合 events 更简洁：

```python
import pexpect

output = pexpect.run(
    'ftp ftp.example.com',
    events={
        'Name .*: ': 'anonymous\n',
        'Password:': 'user@example.com\n',
        'ftp> ': 'ls\nbye\n',
    },
    timeout=30,
    withexitstatus=True
)
print(output[0].decode())
```

## 处理 FTP 的各种提示

```python
import pexpect
import sys

child = pexpect.spawn('ftp ftp.example.com', encoding='utf-8', timeout=30)

while True:
    i = child.expect([
        'Name .*: ',           # 0: 用户名提示
        'Password:',           # 1: 密码提示
        'ftp> ',               # 2: 命令提示符
        r'Login failed',       # 3: 登录失败
        r'Connection refused', # 4: 连接拒绝
        pexpect.EOF,           # 5: 连接结束
        pexpect.TIMEOUT,       # 6: 超时
    ])

    if i == 0:
        child.sendline('anonymous')
    elif i == 1:
        child.sendline('user@example.com')
    elif i == 2:
        break
    elif i in (3, 4, 5, 6):
        print(f'Error: {child.before}', file=sys.stderr)
        sys.exit(1)

child.sendline('ls -la')
child.expect('ftp> ')
print(child.before)
child.sendline('quit')
child.close()
```

## 被动模式与二进制传输

```python
import pexpect

child = pexpect.spawn('ftp ftp.example.com', encoding='utf-8')
child.expect('Name .*: ')
child.sendline('user')
child.expect('Password:')
child.sendline('pass')
child.expect('ftp> ')

child.sendline('passive')        # 启用被动模式
child.expect('ftp> ')
child.sendline('binary')         # 二进制传输模式
child.expect('ftp> ')

child.sendline('put /local/file.dat /remote/file.dat')
idx = child.expect(['ftp> ', 'cannot open', pexpect.TIMEOUT])
if idx == 0:
    print('Upload successful')
else:
    print(f'Upload failed: {child.before}')

child.sendline('quit')
child.close()
```

## Windows 上使用 PopenSpawn

Windows 没有原生 ftp 客户端的 PTY 支持，使用 PopenSpawn：

```python
from pexpect.popen_spawn import PopenSpawn

child = PopenSpawn('ftp ftp.example.com', encoding='utf-8', timeout=30)
child.expect('Name .*: ')
child.sendline('anonymous')
child.expect('Password:')
child.sendline('user@example.com')
child.expect('ftp> ')
child.sendline('ls')
child.expect('ftp> ')
print(child.before)
child.sendline('quit')
```

## 相关概念

- [5分钟快速上手](../concepts/01-getting-started.md)
- [spawn 类详解](../concepts/02-spawn-class.md)
- [expect 模式匹配](../concepts/03-expect-patterns.md)
- [跨平台 spawn 变体](../concepts/06-cross-platform-spawn.md)
- [密码提示处理](password-prompts.md)

[^pexpect-source]: pexpect 源码信源，见 [pexpect-source.md](../references/pexpect-source.md)。
