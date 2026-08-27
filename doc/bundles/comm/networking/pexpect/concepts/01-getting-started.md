---
type: Concept
title: 5分钟快速上手
description: 从安装到第一个 spawn+expect 示例，快速掌握 pexpect 基本用法
tags: [pexpect, getting-started, tutorial]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: pexpect-source
    resource: /references/pexpect-source.md
---

# 5分钟快速上手

## 安装

```bash
pip install pexpect
```

验证安装：

```python
import pexpect
print(pexpect.__version__)  # 4.9.0
```

## 第一个示例：FTP 交互

```python
import pexpect

child = pexpect.spawn('ftp ftp.example.com')
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

这个示例展示了 pexpect 的核心编程模式：

1. **spawn**：启动子进程
2. **expect**：等待输出中出现指定模式
3. **sendline**：发送一行输入
4. **before**：获取匹配位置之前的输出
5. **close**：关闭连接

## 使用 run() 快速执行

对于不需要复杂交互的场景，`run()` 函数更简洁：

```python
import pexpect

output = pexpect.run('ls -la')
print(output.decode())
```

带退出状态：

```python
output, exitstatus = pexpect.run('ls -la /nonexistent', withexitstatus=True)
print(f'Exit: {exitstatus}')
```

带自动密码响应：

```python
output = pexpect.run('scp file.txt user@host:/tmp/',
                     events={'(?i)password:': 'mypassword\n'})
```

## 上下文管理器

spawn 支持 `with` 语句自动关闭：

```python
import pexpect

with pexpect.spawn('ssh user@host') as child:
    child.expect('password:')
    child.sendline('mypassword')
    child.expect(r'[$#] ')
    child.sendline('whoami')
    child.expect(r'[$#] ')
    print(child.before.decode())
```

## 多模式匹配

expect 最强大的功能之一是接受模式列表，返回匹配项的索引：

```python
import pexpect
import sys

child = pexpect.spawn('ssh user@host', encoding='utf-8')

i = child.expect([
    r'password:',           # 0: 密码提示
    r'Are you sure.*\(yes/no',  # 1: 主机密钥确认
    r'Permission denied',   # 2: 认证失败
    pexpect.EOF,            # 3: 连接结束
    pexpect.TIMEOUT,        # 4: 超时
], timeout=30)

if i == 0:
    child.sendline('mypassword')
elif i == 1:
    child.sendline('yes')
elif i == 2:
    print('Authentication failed')
    sys.exit(1)
elif i == 3:
    print('Connection closed')
    sys.exit(1)
elif i == 4:
    print('Connection timed out')
    sys.exit(1)
```

## 日志记录

调试时可将所有输入输出记录到文件或 stdout：

```python
import pexpect
import sys

child = pexpect.spawn('ssh user@host', encoding='utf-8')
child.logfile = sys.stdout  # 实时显示所有交互到终端

# 分别记录读取和发送
child.logfile_read = sys.stdout   # 只看子进程输出
child.logfile_send = open('sent.log', 'w')  # 记录发送的内容
```

## Unicode 支持

默认模式是 bytes（Python 3 中返回 bytes），通过 `encoding` 参数启用 unicode 模式：

```python
import pexpect

# bytes 模式（默认）
child = pexpect.spawn('ls')
child.expect(pexpect.EOF)
print(child.before)  # b'total 0\ndrwxr-xr-x...'

# unicode 模式
child = pexpect.spawn('ls', encoding='utf-8')
child.expect(pexpect.EOF)
print(child.before)  # 'total 0\ndrwxr-xr-x...'
```

## 交回终端控制

`interact()` 将子进程的控制权交还给用户，让用户直接与子进程交互：

```python
import pexpect

child = pexpect.spawn('ssh user@host')
child.expect('password:')
child.sendline('mypassword')
child.expect(r'[$#] ')

# 现在让用户直接操作远程 shell
# 按 Ctrl-] 退出 interact 模式
child.interact()

child.close()
```

## Windows 用户

Windows 上使用 `PopenSpawn` 替代 `spawn`：

```python
from pexpect.popen_spawn import PopenSpawn

child = PopenSpawn('cmd.exe', encoding='utf-8')
child.expect(r'>')
child.sendline('dir')
child.expect(r'>')
print(child.before)
```

## 相关概念

- [pexpect 简介](00-introduction.md)
- [spawn 类详解](02-spawn-class.md)
- [expect 模式匹配](03-expect-patterns.md)
- [发送与交互](04-send-interact.md)
- [pxssh SSH 自动化](05-pxssh.md)
- [SSH 自动登录示例](../examples/ssh-login-automation.md)

[^pexpect-source]: pexpect 源码信源，见 [pexpect-source.md](../references/pexpect-source.md)。
