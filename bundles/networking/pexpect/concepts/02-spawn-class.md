---
type: Concept
title: spawn 类详解
description: spawn 构造参数、子进程生命周期管理、PTY 伪终端机制、平台限制
tags: [pexpect, spawn, pty, subprocess]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: pexpect-source
    resource: /references/pexpect-source.md
---

# spawn 类详解

## spawn 的定位

`spawn` 是 pexpect 最核心的类，定义在 `pexpect/pty_spawn.py` 中。它通过伪终端（PTY）启动子进程，允许程序像人类用户一样与子进程交互。`spawn` 继承自 `SpawnBase`，获得了 expect 匹配引擎和文件对象接口。

> **平台限制**：`spawn` 仅在 Unix/Linux/macOS 上可用，依赖 `pty` 模块和 `ptyprocess` 库。Windows 上需使用 `PopenSpawn`。

## 构造函数

完整签名：

```python
class spawn(SpawnBase):
    def __init__(self, command, args=[], timeout=30, maxread=2000,
                 searchwindowsize=None, logfile=None, cwd=None, env=None,
                 ignore_sighup=False, echo=True, preexec_fn=None,
                 encoding=None, codec_errors='strict', dimensions=None,
                 use_poll=False)
```

### 参数详解

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `command` | （必填） | 要执行的命令字符串或路径 |
| `args` | `[]` | 命令参数列表；为空时自动从 command 解析 |
| `timeout` | `30` | expect 系列方法的默认超时秒数；None 表示无限等待 |
| `maxread` | `2000` | 每次从 TTY 读取的最大字节数 |
| `searchwindowsize` | `None` | 搜索窗口大小；None 搜索整个缓冲区 |
| `logfile` | `None` | 日志文件对象，所有输入输出都会复制到此对象 |
| `cwd` | `None` | 子进程工作目录 |
| `env` | `None` | 子进程环境变量字典；None 继承当前环境 |
| `ignore_sighup` | `False` | True 时子进程忽略 SIGHUP 信号 |
| `echo` | `True` | PTY 回显模式；False 禁用输入回显 |
| `preexec_fn` | `None` | fork 后、exec 前在子进程中调用的可调用对象 |
| `encoding` | `None` | 指定编码（如 'utf-8'）启用 unicode 模式；None 为 bytes 模式 |
| `codec_errors` | `'strict'` | 编解码错误处理策略（strict/ignore/replace） |
| `dimensions` | `None` | PTY 窗口尺寸 `(rows, cols)` 元组 |
| `use_poll` | `False` | True 使用 `select.poll()`，False 使用 `select.select()`；fd 数 >1024 时用 poll |

### command 与 args 的两种形式

命令可以作为完整字符串传递（自动解析参数）：

```python
child = pexpect.spawn('ls -latr /tmp')
child = pexpect.spawn('/usr/bin/ssh user@example.com')
```

也可以将命令和参数分开传递：

```python
child = pexpect.spawn('ls', ['-latr', '/tmp'])
child = pexpect.spawn('/usr/bin/ssh', ['user@example.com'])
```

> **重要**：pexpect 不解释 shell 元字符（`>`、`|`、`*`、`&` 等）。如需管道或重定向，必须显式启动 shell：
> ```python
> child = pexpect.spawn('/bin/bash', ['-c', 'ls -l | grep LOG > logs.txt'])
> child.expect(pexpect.EOF)
> ```

## 子进程生命周期

### 启动

`_spawn()` 方法在构造时被调用，通过 `ptyprocess.PtyProcess.spawn()` 创建 PTY 子进程，设置 `self.pid` 和 `self.child_fd`。命令路径通过 `which()` 在 PATH 中查找。

### 存活检测

```python
child = pexpect.spawn('some_command')

if child.isalive():
    print("Child is running")

child.wait()       # 阻塞等待退出
print(f"Exit status: {child.exitstatus}")
print(f"Signal: {child.signalstatus}")
```

- `isalive()`：非阻塞检测，子进程终止时更新 exitstatus/signalstatus
- `wait()`：阻塞等待子进程退出，返回 exitstatus
- `exitstatus`：正常退出时的返回码（信号终止时为 None）
- `signalstatus`：被信号终止时的信号值（正常退出时为 None）
- `status`：`os.waitpid` 返回的原始状态值

### 终止子进程

```python
child.close(force=True)   # 优雅关闭，force=True 时 SIGKILL
child.terminate(force=False)  # SIGHUP→SIGCONT→SIGINT→SIGKILL
child.kill(signal.SIGTERM)    # 发送指定信号
```

`terminate(force=False)` 的信号升级序列：

1. SIGHUP → 等待 `delayafterterminate`（0.1s）
2. SIGCONT → 等待
3. SIGINT → 等待
4. 若 `force=True`：SIGKILL → 等待

## PTY 伪终端机制

### 什么是 PTY

伪终端（Pseudo-Terminal）是一对字符设备：主端（master）和从端（slave）。pexpect 持有主端，子进程的 stdin/stdout/stderr 连接到从端。子进程认为自己在与真实终端交互，因此会：

- 使用行缓冲（而非全缓冲）
- 输出颜色和 ANSI 转义序列
- 密码输入时关闭回显
- 响应终端窗口大小变化（SIGWINCH）

### 回显控制

PTY 默认回显输入（用户在键盘输入的字符会显示在屏幕上）。这在自动化中可能导致密码被回显：

```python
child = pexpect.spawn('ssh user@host', echo=False)  # 启动时禁用回显

# 或运行时动态控制
child.setecho(False)   # 关闭回显
child.waitnoecho()     # 等待回显确实关闭
child.sendline(password)
child.setecho(True)    # 重新开启
```

`waitnoecho(timeout=-1)` 轮询检测终端 ECHO 标志是否关闭，可用于检测应用何时进入密码输入模式：

```python
child = pexpect.spawn('ssh user@host')
child.waitnoecho()  # 等待远端关闭回显（表示正在等待密码输入）
child.sendline(password)
```

### 终端窗口大小

```python
rows, cols = child.getwinsize()   # 获取当前尺寸
child.setwinsize(40, 120)         # 设置为 40 行 120 列
```

`setwinsize` 会触发 SIGWINCH 信号，使 vim、top 等 TUI 程序响应窗口变化。

### interact() 交回控制

`interact()` 将 PTY 控制权交还给真实终端用户：

```python
child = pexpect.spawn('ssh user@host')
child.expect('password:')
child.sendline('mypassword')
child.expect(r'[$#] ')

# 用户直接操作远程 shell
# 按 Ctrl-]（默认转义字符）退出 interact
child.interact()

child.close()
```

完整签名：

```python
child.interact(escape_character=chr(29),  # Ctrl-]
               input_filter=None,
               output_filter=None)
```

`input_filter` 和 `output_filter` 是字节过滤函数，接收 bytes 返回 bytes，可用于记录或转换数据。设 `escape_character=None` 可禁止转义。

## 日志与调试

```python
import sys

# 记录所有交互到 stdout
child = pexpect.spawn('ssh user@host', encoding='utf-8', logfile=sys.stdout)

# 分别记录
child.logfile_read = sys.stdout        # 只看子进程输出
child.logfile_send = open('sent.log', 'w')  # 只记录发送内容
```

日志在每次读写后 flush，适合实时调试。

## 时序参数

SpawnBase 提供四个可调时序参数：

| 属性 | 默认值 | 用途 |
|------|--------|------|
| `delaybeforesend` | `0.05` | send 前等待 50ms，解决密码回显问题；设 None 禁用 |
| `delayafterclose` | `0.1` | close 后等待内核更新进程状态 |
| `delayafterterminate` | `0.1` | terminate 信号间等待 |
| `delayafterread` | `0.0001` | 每次 read_nonblocking 后 sleep |

`delaybeforesend` 解决的是一个常见问题：应用打印"Password:"提示后关闭回显，但如果密码在关闭回显前就到达，密码会被 PTY 回显出来。50ms 延迟给了应用足够时间关闭回显。

## 相关概念

- [5分钟快速上手](/concepts/01-getting-started.md)
- [expect 模式匹配](/concepts/03-expect-patterns.md)
- [发送与交互](/concepts/04-send-interact.md)
- [跨平台 spawn 变体](/concepts/06-cross-platform-spawn.md)
- [pexpect 源码信源登记](/references/pexpect-source.md)

[^pexpect-source]: pexpect 源码信源，见 [pexpect-source.md](/references/pexpect-source.md)。
