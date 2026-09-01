---
type: Concept
title: 跨平台 spawn 变体
description: PopenSpawn（跨平台无 PTY）、fdspawn（文件描述符）、SocketSpawn（socket）、Unix vs Windows 差异
tags: [pexpect, cross-platform, popenspawn, fdspawn, socketspawn]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: pexpect-source
    resource: /references/pexpect-source.md
---

# 跨平台 spawn 变体

## 概述

pexpect 通过 `SpawnBase` 抽象基类定义统一接口，针对不同 I/O 机制提供四个具体实现：

| 类 | 模块 | I/O 机制 | 平台 | PTY |
|----|------|---------|------|-----|
| `spawn` | `pty_spawn` | 伪终端（ptyprocess） | 仅 Unix | ✅ |
| `PopenSpawn` | `popen_spawn` | subprocess.Popen 管道 | 跨平台 | ❌ |
| `fdspawn` | `fdpexpect` | 任意文件描述符 | Unix | ❌ |
| `SocketSpawn` | `socket_pexpect` | TCP socket | 跨平台 | ❌ |

## PopenSpawn

### 定位

`PopenSpawn` 基于 `subprocess.Popen`，在 Windows 和 Unix 上均可使用。它不提供 PTY，因此子进程不会认为自己连接到终端。

### 构造函数

```python
from pexpect.popen_spawn import PopenSpawn

PopenSpawn(cmd, timeout=30, maxread=2000, searchwindowsize=None,
           logfile=None, cwd=None, env=None, encoding=None,
           codec_errors='strict', preexec_fn=None)
```

与 `spawn` 相比，PopenSpawn **不支持**以下参数：
- `args`（命令和参数合并为 cmd）
- `echo`、`ignore_sighup`、`dimensions`、`use_poll`（PTY 专属）

### 基本用法

```python
from pexpect.popen_spawn import PopenSpawn

child = PopenSpawn('ftp ftp.example.com', encoding='utf-8')
child.expect('Name .*: ')
child.sendline('anonymous')
child.expect('Password:')
child.sendline('user@example.com')
child.expect('ftp> ')
print(child.before)
child.close()
```

命令可以是字符串（Unix 上用 shlex.split 解析）或列表：

```python
child = PopenSpawn(['ssh', 'user@host'])  # 列表形式
child = PopenSpawn('ssh user@host')        # 字符串形式（Unix）
```

### 与 spawn 的关键差异

| 特性 | spawn（PTY） | PopenSpawn（管道） |
|------|-------------|-------------------|
| 子进程感知终端 | ✅ 认为是 tty | ❌ 认为是管道 |
| 输出缓冲 | 行缓冲 | 可能全缓冲 |
| 换行符 | `\r\n` (CR/LF) | `os.linesep` |
| 密码回显 | 可控制 echo | 无终端回显概念 |
| interact() | ✅ 支持 | ❌ 不支持 |
| 信号控制 | ✅ kill/terminate/sendintr | ⚠️ 有限（Windows 映射） |
| setwinsize/getwinsize | ✅ | ❌ |
| waitnoecho/setecho/getecho | ✅ | ❌ |
| stderr | 连接到 PTY | 合并到 stdout |
| 跨平台 | ❌ 仅 Unix | ✅ Windows/Unix |

### 管道模式的注意事项

由于子进程检测到非 tty 时通常切换为全缓冲，输出可能不会立即出现：

```python
# 在 PTY 模式下工作正常，但 PopenSpawn 可能因全缓冲而超时
child = PopenSpawn('python script.py', encoding='utf-8')
child.expect('Ready', timeout=10)  # 可能超时
```

解决方案：
- 在命令中使用 `stdbuf` 或 `unbuffer` 禁用缓冲
- 设置环境变量 `PYTHONUNBUFFERED=1`（对 Python 程序）
- 在程序中主动 flush

### Windows 特殊处理

PopenSpawn 在 Windows 上：

1. 设置 `STARTUPINFO` 隐藏控制台窗口（`STARTF_USESHOWWINDOW`）
2. 使用 `CREATE_NEW_PROCESS_GROUP` 创建新进程组
3. 信号映射：
   - `SIGINT` 或 `CTRL_C_EVENT` → `CTRL_C_EVENT`
   - `SIGBREAK` 或 `CTRL_BREAK_EVENT` → `CTRL_BREAK_EVENT`
   - 其他信号 → `SIGTERM`

```python
import signal
child.kill(signal.SIGINT)       # 发送 Ctrl-C
child.kill(signal.CTRL_BREAK_EVENT)  # 发送 Ctrl-Break
```

### sendeof() 差异

PopenSpawn 的 `sendeof()` 通过关闭 stdin 管道实现（而非发送 Ctrl-D）：

```python
def sendeof(self):
    self.proc.stdin.close()
```

### 内部架构

PopenSpawn 使用独立守护线程从管道读取数据到 Queue：

```
子进程 stdout → _read_incoming 线程 → Queue → read_nonblocking()
```

`read_nonblocking(size, timeout)` 从 Queue 获取数据，在 timeout 内循环读取直到达到 size 或超时。`_read_reached_eof` 标志标记 EOF 状态。

## fdspawn

### 定位

`fdspawn`（`pexpect.fdpexpect.fdspawn`）接受一个已打开的文件描述符，适用于串口、命名管道（FIFO）、设备文件等。

### 基本用法

```python
import os
from pexpect.fdpexpect import fdspawn

# 打开串口
fd = os.open('/dev/ttyUSB0', os.O_RDWR | os.O_NOCTTY)
child = fdspawn(fd, encoding='utf-8')
child.expect('login:')
child.sendline('user')
child.close()  # 关闭 fd

# 也接受具有 fileno() 方法的对象
import serial
ser = serial.Serial('/dev/ttyUSB0', 9600)
child = fdspawn(ser, encoding='utf-8')
```

### 注意事项

- 调用者负责打开和关闭文件描述符（fdspawn.close() 会关闭 fd）
- `terminate(force=False)` 直接抛出异常——文件描述符没有"终止进程"的概念
- `sendcontrol`、`sendeof`、`sendintr` 等终端控制方法不可用（基类无 PTY）
- Windows 上 `socket.fileno()` 不能用于 select，应改用 SocketSpawn
- POSIX 系统上 `read_nonblocking` 使用 `select.select()` 或 `select.poll()` 实现超时

## SocketSpawn

### 定位

`SocketSpawn`（`pexpect.socket_pexpect.SocketSpawn`）接受一个已连接的 socket，提供跨平台的网络交互能力。

### 基本用法

```python
import socket
from pexpect.socket_pexpect import SocketSpawn

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('example.com', 23))  # Telnet

child = SocketSpawn(sock, encoding='utf-8')
child.expect('login:')
child.sendline('user')
child.expect('Password:')
child.sendline('pass')
child.expect(r'[$#] ')
child.sendline('ls')
child.expect(r'[$#] ')
print(child.before)
child.close()
```

### 与 fdspawn 的区别

| 特性 | fdspawn | SocketSpawn |
|------|---------|-------------|
| 输入 | 文件描述符（int） | socket.socket 对象 |
| 平台 | 主要 Unix | 跨平台 |
| 超时机制 | select.select/poll | socket.settimeout |
| Windows socket | ❌ 不可用 | ✅ 支持 |
| close() | os.close(fd) | socket.shutdown + close |

SocketSpawn 的 `read_nonblocking` 使用 `socket.recv()` 配合 contextmanager 临时设置 socket 超时：

```python
@contextmanager
def _timeout(self, timeout):
    saved_timeout = self.socket.gettimeout()
    try:
        self.socket.settimeout(timeout)
        yield
    finally:
        self.socket.settimeout(saved_timeout)
```

收到空字节（`b''`）抛出 EOF，`socket.timeout` 转为 `TIMEOUT`。

## 平台选择指南

```
需要自动化交互式 CLI？
├── Unix/Linux/macOS
│   └── 使用 pexpect.spawn（PTY，完整功能）
├── Windows
│   ├── 子进程交互 → PopenSpawn
│   └── 网络服务交互 → SocketSpawn
└── 串口/设备文件
    └── fdspawn（Unix）或 SocketSpawn（网络设备）
```

### 跨平台代码模式

```python
import sys

if sys.platform == 'win32':
    from pexpect.popen_spawn import PopenSpawn as SpawnClass
else:
    from pexpect import spawn as SpawnClass

child = SpawnClass('some-command', encoding='utf-8')
child.expect('pattern')
child.sendline('response')
```

### 各变体能力矩阵

| 能力 | spawn | PopenSpawn | fdspawn | SocketSpawn |
|------|-------|------------|---------|-------------|
| expect/expect_exact | ✅ | ✅ | ✅ | ✅ |
| send/sendline | ✅ | ✅ | ✅ | ✅ |
| write/writelines | ✅ | ✅ | ✅ | ✅ |
| read/readline | ✅ | ✅ | ✅ | ✅ |
| read_nonblocking | ✅ | ✅ | ✅ | ✅ |
| close | ✅ | ✅ | ✅ | ✅ |
| isalive | ✅ | ✅ | ✅ | ✅ |
| kill(sig) | ✅ | ✅ | ❌ | ❌ |
| terminate | ✅ | ❌ | ❌（抛异常） | ❌ |
| wait | ✅ | ✅ | ❌ | ❌ |
| interact | ✅ | ❌ | ❌ | ❌ |
| sendcontrol/sendeof/sendintr | ✅ | sendeof 仅关 stdin | ❌ | ❌ |
| setwinsize/getwinsize | ✅ | ❌ | ❌ | ❌ |
| setecho/getecho/waitnoecho | ✅ | ❌ | ❌ | ❌ |
| 上下文管理器 | ✅ | ✅ | ✅ | ✅ |
| 日志（logfile） | ✅ | ✅ | ✅ | ✅ |

## 相关概念

- [pexpect 简介](00-introduction.md)
- [spawn 类详解](02-spawn-class.md)
- [expect 模式匹配](03-expect-patterns.md)
- [REPLWrapper](07-replwrap.md)
- [pexpect 源码信源登记](../references/pexpect-source.md)

[^pexpect-source]: pexpect 源码信源，见 [pexpect-source.md](../references/pexpect-source.md)。
