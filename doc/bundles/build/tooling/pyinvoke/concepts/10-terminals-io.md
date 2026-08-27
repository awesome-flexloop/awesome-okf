---
type: Concept
title: 终端与 IO
description: 伪终端 PTY、输出控制、字符缓冲模式、平台兼容性
tags: [pyinvoke, terminal, pty, PTY, IO, character-buffered, cbreak, windows, platform, FIONREAD]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: pyinvoke-source
    resource: /references/pyinvoke-source.md
---

# 终端与 IO

终端与 IO 处理是命令执行中最容易被忽视但又极其关键的环节。Invoke 在 `terminals.py` 模块中封装了跨平台的终端操作，包括伪终端尺寸检测、字符缓冲模式切换、非阻塞 IO 检测等底层功能。这些功能直接支撑了 Runner 系统的 PTY 模式、交互式输入转发和实时输出。

## 终端的基本概念

### TTY 与 PTY

- **TTY（Teletypewriter）**：指物理终端或虚拟终端设备。在 Unix 系统中，每个终端窗口、SSH 会话、串口连接都是一个 TTY。
- **PTY（Pseudo-Terminal，伪终端）**：是一对虚拟终端设备，包含主端（master）和从端（slave）。从端表现得像一个真实 TTY，主端用于读写数据。`pty.fork()` 创建 PTY 对并 fork 子进程，子进程的 stdin/stdout/stderr 连接到 PTY 从端。

许多程序（如 sudo、ssh、vim、top、交互式 shell）会检测自己是否运行在 TTY 中，并据此改变行为：

- 在 TTY 中：使用行缓冲、显示颜色、输出进度条、发出密码提示
- 不在 TTY 中（管道/重定向）：使用块缓冲、不输出颜色、不进行交互

### 为什么需要 PTY

当 Invoke 通过 `subprocess.Popen` 创建子进程时，子进程的 stdin/stdout/stderr 连接的是管道（pipe），不是 TTY。这会导致：

1. 程序检测到 stdout 不是 TTY，启用块缓冲（输出不实时刷新）
2. sudo 等程序不输出密码提示
3. 彩色输出被禁用
4. 交互式程序无法正常工作

设置 `pty=True` 时，子进程连接到 PTY 从端，认为自己运行在真实终端中，从而正常工作。

## pty_size()：获取终端尺寸

`pty_size()` 返回当前终端的列数和行数：

```python
from invoke import pty_size

cols, rows = pty_size()  # 例如 (120, 40)
```

### 实现原理

**Unix 平台**：

通过 `TIOCGWINSZ` ioctl 系统调用查询 stdout 的窗口大小：

```python
import fcntl, struct, termios, sys
buf = struct.pack("HHHH", 0, 0, 0, 0)
result = fcntl.ioctl(sys.stdout, termios.TIOCGWINSZ, buf)
rows, cols, *_ = struct.unpack("HHHH", result)
return (cols, rows)
```

当 ioctl 失败时（例如 stdout 被重定向、不是 TTY、测试环境等），返回 `(None, None)`，最终回退到默认值。

**Windows 平台**：

通过 Windows API `GetConsoleScreenBufferInfo` 获取控制台窗口尺寸：

```python
from ctypes import windll, byref, POINTER, Structure, c_ushort
from ctypes.wintypes import HANDLE, _COORD, _SMALL_RECT

class CONSOLE_SCREEN_BUFFER_INFO(Structure):
    _fields_ = [
        ("dwSize", _COORD),
        ("dwCursorPosition", _COORD),
        ("wAttributes", c_ushort),
        ("srWindow", _SMALL_RECT),
        ("dwMaximumWindowSize", _COORD),
    ]

hstd = windll.kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
csbi = CONSOLE_SCREEN_BUFFER_INFO()
windll.kernel32.GetConsoleScreenBufferInfo(hstd, byref(csbi))
sizex = csbi.srWindow.Right - csbi.srWindow.Left + 1
sizey = csbi.srWindow.Bottom - csbi.srWindow.Top + 1
```

### 默认值

当无法动态获取终端尺寸时（管道、重定向、测试等），`pty_size()` 返回默认值 `(80, 24)`——这是传统终端的标准尺寸。Local runner 在 PTY 模式下使用此值设置子进程终端窗口大小。

## character_buffered()：字符缓冲上下文管理器

`character_buffered(stream)` 是一个上下文管理器，将 Unix TTY 切换到**字符模式**（cbreak mode），使得每次按键都立即可读，而不需要等待换行符。

### 问题背景

Unix TTY 默认处于**规范模式**（canonical mode / cooked mode）：输入按行缓冲，用户输入一行文字并按 Enter 后，程序才能读到数据。这对于需要实时逐字符读取输入的场景（如转发用户按键到 PTY 子进程）来说是不可接受的。

cbreak 模式（也称为 rare mode）的特性：
- 关闭行缓冲：字符立即可读
- 关闭回显（由 Invoke 自己控制是否回显）
- 保留信号处理（Ctrl+C 仍会产生 SIGINT）

### 实现

```python
@contextmanager
def character_buffered(stream):
    if WINDOWS or not isatty(stream) or not stdin_is_foregrounded_tty(stream) or cbreak_already_set(stream):
        yield
    else:
        old_settings = termios.tcgetattr(stream)
        tty.setcbreak(stream)
        try:
            yield
        finally:
            termios.tcsetattr(stream, termios.TCSADRAIN, old_settings)
```

### 前置条件检查

在设置 cbreak 模式前，会进行多项安全检查：

1. **WINDOWS**：Windows 上此操作为 no-op（Windows 控制台 IO 模型不同）
2. **isatty(stream)**：流不是 TTY 时不操作（如管道、文件、StringIO）
3. **stdin_is_foregrounded_tty(stream)**：进程不在前台进程组时不操作（后台进程修改终端设置会导致 shell 暂停）
4. **cbreak_already_set(stream)**：已处于 cbreak 模式时不重复设置（幂等性）

`stdin_is_foregrounded_tty()` 通过比较进程组 ID 与终端前台进程组 ID 来判断：

```python
def stdin_is_foregrounded_tty(stream):
    if not has_fileno(stream):
        return False
    return os.getpgrp() == os.tcgetpgrp(stream.fileno())
```

退出上下文管理器时，通过 `termios.tcsetattr()` 恢复原始终端设置，确保终端不会停留在 cbreak 模式。

### 在 Runner 中的使用

`handle_stdin` IO 线程在启动时包裹在 `character_buffered(input_)` 中：

```python
def handle_stdin(self, input_, output, echo=False):
    closed_stdin = False
    with character_buffered(input_):
        while True:
            data = self.read_our_stdin(input_)
            if data:
                self.write_proc_stdin(data)
                if echo:
                    self.write_our_output(stream=output, string=data)
            elif data is not None:
                if not self.using_pty and not closed_stdin:
                    self.close_proc_stdin()
                    closed_stdin = True
            if self.program_finished.is_set() and not data:
                break
            time.sleep(self.input_sleep)
```

这确保了用户按键能够实时转发到子进程，实现流畅的交互式体验。

## WINDOWS 常量

`WINDOWS = sys.platform == "win32"` 是一个模块级常量，用于在整个 Invoke 代码库中进行平台分支判断。注意 Cygwin 环境虽然运行在 Windows 上，但因其足够接近真实 Unix，不会被检测为 WINDOWS。

WINDOWS 常量影响的行为：

| 功能 | Unix | Windows |
|------|------|---------|
| 默认 shell | `bash` | `COMSPEC` 环境变量或 `cmd.exe` |
| 系统配置路径 | `/etc/` | 无系统级配置 |
| PTY 支持 | `pty.fork()` | 不支持（需要 fallback） |
| 字符缓冲 | `tty.setcbreak()` | no-op |
| 非阻塞 IO | `select.select()` | `msvcrt.kbhit()` |
| 字节可读检测 | `FIONREAD` ioctl | 回退到读 1 字节 |
| 换行符 | `\n` | `\r\n`/`\r` 转换为 `\n` |

## ready_for_reading()：非阻塞 IO 检测

`ready_for_reading(input_)` 检测输入流是否有数据可读，用于非阻塞 IO 轮询：

```python
def ready_for_reading(input_):
    if not has_fileno(input_):
        return True  # 非文件描述符流，假设可读（如 StringIO）
    if sys.platform == "win32":
        return msvcrt.kbhit()  # Windows：检查键盘输入
    else:
        reads, _, _ = select.select([input_], [], [], 0.0)
        return bool(reads and reads[0] is input_)
```

在 `read_our_stdin()` 中使用此函数进行轮询，避免在 stdin 上阻塞导致无法响应子进程退出信号：

```python
def read_our_stdin(self, input_):
    bytes_ = None
    if ready_for_reading(input_):
        try:
            bytes_ = input_.read(bytes_to_read(input_))
        except OSError as e:
            if e.errno != errno.EBADF:  # 忽略 nohup 等场景下的坏 FD
                raise
        if bytes_ and isinstance(bytes_, bytes):
            bytes_ = self.decode(bytes_)
    return bytes_
```

轮询间隔由 `Runner.input_sleep`（默认 0.01 秒）控制。

## bytes_to_read()：可读字节数检测

`bytes_to_read(input_)` 查询流中有多少字节立即可读：

```python
def bytes_to_read(input_):
    if not WINDOWS and isatty(input_) and has_fileno(input_):
        fionread = fcntl.ioctl(input_, termios.FIONREAD, b"  ")
        return int(struct.unpack("h", fionread)[0])
    return 1  # 回退：每次读 1 字节
```

Unix TTY 上使用 `FIONREAD` ioctl 获取输入缓冲区中的可读字节数，避免逐字节读取的效率问题。非 TTY 流或 Windows 平台回退到每次读 1 字节。

读取 1 字节虽然效率较低，但对于交互式输入已经足够，且能保证多字节字符（如 UTF-8 中文）最终被正确拼合（在 decode 阶段处理）。

## PTY 模式的限制与注意事项

### stdout/stderr 合并

PTY 只有一个输出通道，stderr 被合并到 stdout 中：

- `result.stderr` 始终为空字符串
- 无法区分正常输出和错误输出
- `hide='stderr'` 无效
- Runner 不会创建 stderr 处理线程

### stdin 关闭限制

`pty=True` 时无法关闭子进程的 stdin（调用 `close_proc_stdin()` 会抛出 `SubprocessPipeError`），因为 PTY 主端不支持半关闭语义。

### 平台限制

- **Windows**：Python 的 `pty` 模块在 Windows 上不可用（ImportError）。Local runner 在 pty=True 时会直接 `sys.exit()` 报错
- **无 fileno 的 stdin**：当 `sys.stdin` 没有有效 `fileno()`（如管道环境、测试 harness）时，Local 会自动 fallback 到非 pty 模式并打印警告（`fallback=True`，默认启用）

### 输出缓冲问题

即使使用 PTY，某些程序可能仍会检测 stdout 是否为 TTY 但在 Invoke 的读取模型下表现出缓冲行为。`read_chunk_size`（默认 1000 字节）控制每次读取的最大数据量。

## 换行符处理

Windows 平台下，Runner 会将 `\r\n` 和 `\r` 统一转换为 `\n`：

```python
if WINDOWS:
    stdout = stdout.replace("\r\n", "\n").replace("\r", "\n")
    stderr = stderr.replace("\r\n", "\n").replace("\r", "\n")
```

这确保跨平台输出的一致性。Unix 平台使用 `\n` 作为换行符，不需要转换。

## 编码处理

Runner 使用 `default_encoding()` 获取系统默认编码：

```python
def default_encoding():
    return locale.getpreferredencoding(False)
```

用户可以通过 `encoding` 参数覆盖自动检测。解码时使用 `"replace"` 错误处理策略，遇到无效字节不会抛出异常，而是替换为 Unicode 替换字符（U+FFFD）：

```python
def decode(self, data):
    return data.decode(self.encoding, "replace")
```

## 相关概念

- [Runner 系统](06-runners.md)
- [StreamWatcher 自动响应](09-watchers.md)
- [配置系统](05-configuration.md)
- [PyInvoke 源码信源登记](../references/pyinvoke-source.md)

[^pyinvoke-source]: PyInvoke 源码信源，见 [pyinvoke-source.md](../references/pyinvoke-source.md)；终端工具函数定义于 `invoke/terminals.py`，Runner 的 IO 线程处理定义于 `invoke/runners.py`。
