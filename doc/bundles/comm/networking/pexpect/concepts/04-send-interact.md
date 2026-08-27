---
type: Concept
title: 发送与交互
description: send/sendline/write/sendcontrol/sendeof、interact 交回终端控制、logfile 日志记录
tags: [pexpect, send, interact, logging]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: pexpect-source
    resource: /references/pexpect-source.md
---

# 发送与交互

## 发送数据到子进程

### send(s)

`send()` 向子进程发送字符串，返回写入的字节数。

```python
import pexpect

child = pexpect.spawn('cat', encoding='utf-8')
n = child.send('Hello\n')
print(f"Wrote {n} bytes")
child.expect('Hello')
```

发送前如果 `delaybeforesend` 非 None（默认 0.05 秒），会先 sleep 一小段时间。这是为了解决密码回显问题：应用打印密码提示后需要一点时间关闭终端回显。

### sendline(s='')

`sendline()` 在 `send()` 基础上自动追加行分隔符：

```python
child.sendline('ls -la')      # 发送 "ls -la\n"
child.sendline()              # 仅发送换行符（回车）
```

在 bytes 模式下行分隔符为 `os.linesep.encode('ascii')`，unicode 模式下为 `os.linesep`。

### write(s) 和 writelines(sequence)

`write()` 调用 `send()` 但无返回值；`writelines()` 对序列中每个元素调用 `write()`：

```python
child.write('line1\n')
child.writelines(['line2\n', 'line3\n'])
```

这两个方法提供与 Python 文件对象一致的接口。

### 行缓冲限制

PTY 默认使用规范输入模式（canonical mode），每行有最大长度限制：

- Linux：4096 字节（N_TTY_BUF_SIZE）
- macOS：1024 字节（PC_MAX_CANON）
- FreeBSD：1920 字节
- OpenSolaris：256 字节

超长行会被截断，超限部分丢弃并响铃（BEL）。如需发送超长数据，可先禁用规范模式：

```python
bash = pexpect.spawn('/bin/bash', echo=False)
bash.sendline('stty -icanon')
bash.sendline('base64')
bash.sendline('x' * 5000)
```

## 控制字符与信号

### sendcontrol(char)

发送控制字符。参数为字母字符串，如 `'c'` 表示 Ctrl-C，`'d'` 表示 Ctrl-D：

```python
child.sendcontrol('c')   # Ctrl-C (SIGINT)
child.sendcontrol('d')   # Ctrl-D (EOF)
child.sendcontrol('g')   # Ctrl-G (BEL)
child.sendcontrol('z')   # Ctrl-Z (suspend)
```

### sendeof()

发送 EOF 字符（通常是 Ctrl-D）。注意：必须在行首发送才会被解释为 EOF：

```python
child.sendline('some input')
child.sendeof()  # 在新行开始处发送 EOF
```

对于 `PopenSpawn`，`sendeof()` 通过关闭 stdin 管道实现。

### sendintr()

发送 SIGINT 信号（Ctrl-C），中断子进程当前操作：

```python
child.sendline('long-running-command')
# ... 需要中断时
child.sendintr()
child.expect(r'[$#] ')
```

## interact()——交回终端控制权

`interact()` 将子进程的控制权交还给用户的真实键盘。用户的按键直接发送给子进程，子进程输出直接显示在用户终端上。

### 基本用法

```python
import pexpect

child = pexpect.spawn('ssh user@remote-host')
child.expect('password:')
child.sendline('mypassword')
child.expect(r'[$#] ')

# 自动化登录完成后，交回给用户手动操作
child.interact()

# 用户按 Ctrl-] 退出 interact 后继续
child.close()
```

### 方法签名

```python
spawn.interact(self, escape_character=chr(29),
               input_filter=None, output_filter=None)
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `escape_character` | `chr(29)` (Ctrl-]) | 退出 interact 的转义字符；设为 None 禁止退出 |
| `input_filter` | `None` | 输入过滤函数，接收 bytes 返回 bytes |
| `output_filter` | `None` | 输出过滤函数，接收 bytes 返回 bytes |

> **注意**：即使设置了 `encoding='utf-8'`，`input_filter` 和 `output_filter` 接收和返回的始终是 **bytes**，需要自行 decode/encode。

### 窗口大小传递

interact 模式下，父终端窗口大小变化不会自动传递给子进程。如需此功能，需手动注册 SIGWINCH 处理器：

```python
import pexpect, struct, fcntl, termios, signal, sys

def sigwinch_passthrough(sig, data):
    if not p.closed:
        s = struct.pack("HHHH", 0, 0, 0, 0)
        a = struct.unpack('hhhh', fcntl.ioctl(
            sys.stdout.fileno(), termios.TIOCGWINSZ, s))
        p.setwinsize(a[0], a[1])

p = pexpect.spawn('/bin/bash')
signal.signal(signal.SIGWINCH, sigwinch_passthrough)
p.interact()
```

## 日志记录

### logfile——记录全部交互

```python
import sys

# 实时输出到终端
child = pexpect.spawn('ssh user@host', encoding='utf-8', logfile=sys.stdout)

# 写入文件
with open('session.log', 'w') as f:
    child = pexpect.spawn('ssh user@host', encoding='utf-8', logfile=f)
    child.expect('password:')
    child.sendline('mypassword')
    child.expect(r'[$#] ')
```

`logfile` 同时记录读取和发送的数据，每次 write 后 flush。

### logfile_read / logfile_send——分别记录

```python
child.logfile_read = sys.stdout        # 只看子进程返回的内容
child.logfile_send = open('sent.log', 'w')  # 只记录发送的内容
```

典型场景：自动化测试时记录所有子进程输出用于调试，但不记录发送的密码。

### 编码模式下的日志

- bytes 模式（`encoding=None`）：logfile 应接收 bytes（如以 `'wb'` 打开的文件或 `sys.stdout.buffer`）。
- unicode 模式（`encoding='utf-8'`）：logfile 应接收 str（如 `sys.stdout`）。

```python
# bytes 模式记录到文件
child = pexpect.spawn('command')
fout = open('mylog.txt', 'wb')
child.logfile = fout

# unicode 模式输出到终端
child = pexpect.spawn('command', encoding='utf-8')
child.logfile = sys.stdout
```

## 发送前延迟（delaybeforesend）

`delaybeforesend` 是 pexpect 为解决密码回显问题设计的机制：

1. 应用打印 "Password:" 提示
2. 应用关闭终端 ECHO 标志
3. 用户输入密码（不回显）

但在自动化中，`sendline()` 可能在应用关闭 ECHO 之前就发送了密码，导致密码被 PTY 回显出来。默认的 50ms 延迟（`0.05` 秒）给了应用足够时间关闭 ECHO。

```python
child = pexpect.spawn('ssh user@host')
child.delaybeforesend = 0.05   # 默认值，50ms
child.delaybeforesend = None   # 禁用延迟（恢复旧行为）
child.delaybeforesend = 0.1    # 增加到 100ms
```

也可使用 `waitnoecho()` 精确等待回显关闭：

```python
child = pexpect.spawn('ssh user@host')
child.waitnoecho()       # 阻塞直到 ECHO 关闭
child.sendline(password)
```

## 相关概念

- [spawn 类详解](02-spawn-class.md)
- [expect 模式匹配](03-expect-patterns.md)
- [pxssh SSH 自动化](05-pxssh.md)
- [SSH 自动登录示例](../examples/ssh-login-automation.md)
- [密码提示处理示例](../examples/password-prompts.md)

[^pexpect-source]: pexpect 源码信源，见 [pexpect-source.md](../references/pexpect-source.md)。
