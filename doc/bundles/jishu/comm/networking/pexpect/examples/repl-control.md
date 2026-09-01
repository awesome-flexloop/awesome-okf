---
type: Example
title: REPL 交互控制
description: 使用 REPLWrapper 控制 Python/Bash/数据库 REPL，执行命令并获取输出
tags: [pexpect, example, repl, replwrap, python, bash]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: pexpect-source
    resource: /references/pexpect-source.md
---

# REPL 交互控制

## Python REPL 控制

```python
from pexpect.replwrap import python

p = python()

# 执行简单表达式
print(p.run_command('1 + 1'))           # '2\r\n'
print(p.run_command('2 ** 10'))         # '1024\r\n'

# 多行代码
code = '\n'.join([
    'total = 0',
    'for i in range(5):',
    '    total += i',
    'print(total)',
])
print(p.run_command(code))              # '10\r\n'

# 导入模块
p.run_command('import os')
print(p.run_command('os.getcwd()'))
```

## Bash REPL 控制

```python
from pexpect.replwrap import bash

b = bash()

print(b.run_command('uname -a'))
print(b.run_command('ls -la'))
print(b.run_command('echo $HOME'))

# 切换目录后保持状态
b.run_command('cd /tmp')
print(b.run_command('pwd'))  # '/tmp\r\n'
```

## 自定义 REPL——sqlite3

```python
import pexpect
from pexpect.replwrap import REPLWrapper

child = pexpect.spawn('sqlite3 :memory:', echo=False, encoding='utf-8')
repl = REPLWrapper(
    child,
    r'sqlite> ',
    ".prompt '{0}' '{1}'",
)

repl.run_command('CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT);')
repl.run_command("INSERT INTO users (name) VALUES ('Alice');")
repl.run_command("INSERT INTO users (name) VALUES ('Bob');")
result = repl.run_command('SELECT * FROM users;')
print(result)
```

## 自定义 REPL——Redis CLI

```python
import pexpect
from pexpect.replwrap import REPLWrapper

child = pexpect.spawn('redis-cli', echo=False, encoding='utf-8')
repl = REPLWrapper(child, r'127\.0\.0\.1:6379> ', None)

repl.run_command('SET mykey "hello"')
print(repl.run_command('GET mykey'))    # '"hello"\r\n'
repl.run_command('DEL mykey')
```

## 通过 SSH 控制远程 REPL

```python
from pexpect import pxssh
from pexpect.replwrap import REPLWrapper

s = pxssh.pxssh(encoding='utf-8')
s.login('remote-host', 'user', 'password')

# 在远程启动 Python
s.sendline('python3')
s.expect('>>> ')

# 将 pxssh 的 spawn 实例包装为 REPLWrapper
repl = REPLWrapper(
    s,
    '>>> ',
    'import sys; sys.ps1="{0}"; sys.ps2="{1}"'
)

print(repl.run_command('import platform; platform.node()'))
print(repl.run_command('import os; os.listdir(".")'))

s.logout()
```

## 多行命令与续行处理

`run_command` 自动处理多行输入和续行提示符：

```python
from pexpect.replwrap import python

p = python()

# 函数定义（多行）
func_code = '\n'.join([
    'def fib(n):',
    '    if n <= 1:',
    '        return n',
    '    return fib(n-1) + fib(n-2)',
])
p.run_command(func_code)

# 调用函数
print(p.run_command('fib(10)'))  # '55\r\n'

# 不完整命令会触发 ValueError
try:
    p.run_command('for i in range(3):')  # 缺少循环体
except ValueError as e:
    print(f"Incomplete command: {e}")
```

## 带超时的命令执行

```python
from pexpect.replwrap import bash

b = bash()

# 设置单次命令超时
try:
    result = b.run_command('sleep 10 && echo done', timeout=5)
except Exception as e:
    print(f"Command timed out: {e}")

# 无限等待（不推荐）
result = b.run_command('long_running_command', timeout=None)
```

## 异步 REPL 控制

```python
import asyncio
from pexpect.replwrap import python

async def main():
    p = python()
    result = await p.run_command('sum(range(1000000))', async_=True)
    print(result)

asyncio.run(main())
```

## 使用 spawn 手动控制 REPL

不使用 REPLWrapper，直接通过 expect/send 控制：

```python
import pexpect

child = pexpect.spawn('python3', encoding='utf-8', timeout=10)
child.expect('>>> ')

child.sendline('1 + 1')
child.expect('>>> ')
print(child.before)  # '1 + 1\r\n2\r\n'

# 多行命令
child.sendline('for i in range(3):')
child.expect('\.\.\. ')
child.sendline('    print(i)')
child.expect('\.\.\. ')
child.sendline('')
child.expect('>>> ')
print(child.before)
```

> **注意**：手动处理 `...` 续行提示符容易出错。REPLWrapper 自动处理了这些细节，推荐优先使用。

## 相关概念

- [REPLWrapper REPL 交互封装](../concepts/07-replwrap.md)
- [expect 模式匹配](../concepts/03-expect-patterns.md)
- [发送与交互](../concepts/04-send-interact.md)
- [pxssh SSH 自动化](../concepts/05-pxssh.md)
- [高级模式](../concepts/08-advanced-patterns.md)

[^pexpect-source]: pexpect 源码信源，见 [pexpect-source.md](../references/pexpect-source.md)。
