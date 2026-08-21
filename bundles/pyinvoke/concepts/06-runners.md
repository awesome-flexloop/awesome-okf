---
type: Concept
title: Runner 系统
description: Local runner、命令执行流程、Result 对象、pty 模式、echo/warn/hide 选项、异步执行与 Promise
tags: [pyinvoke, runner, Local, Result, Promise, pty, subprocess, asynchronous, IO-threads]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: pyinvoke-source
    resource: /references/pyinvoke-source.md
---

# Runner 系统

Runner（运行器）是 Invoke 中负责实际执行 shell 命令的抽象层。`Runner` 是一个半抽象基类，定义了命令执行的标准流程和扩展接口；`Local` 是其内置实现，通过 `subprocess.Popen` 和 `pty.fork()` 在本地执行命令。Runner 系统还提供了 `Result` 结果对象和 `Promise` 异步承诺对象，以及丰富的执行控制选项。

## Runner 抽象基类

`Runner` 类定义了命令执行的核心 API，子类必须实现以下抽象方法才能工作：

| 方法 | 说明 |
|------|------|
| `start(command, shell, env)` | 启动命令执行（创建子进程或连接远程） |
| `wait()` | 阻塞等待命令执行完成 |
| `returncode()` | 返回命令的退出码 |
| `process_is_finished` (property) | 非阻塞检查进程是否已结束 |
| `read_proc_stdout(num_bytes)` | 从 stdout 读取最多 num_bytes 字节 |
| `read_proc_stderr(num_bytes)` | 从 stderr 读取最多 num_bytes 字节 |
| `_write_proc_stdin(data)` | 向子进程 stdin 写入已编码字节 |
| `close_proc_stdin()` | 关闭子进程 stdin |
| `kill()` | 强制终止子进程 |

`Runner.__init__(context)` 接收一个 Context 对象，从中获取配置默认值。Runner 的所有 `run()` 关键字参数默认值都来自 `context.config.run` 子树。

### 类级属性

| 属性 | 默认值 | 说明 |
|------|--------|------|
| `read_chunk_size` | `1000` | 每次流读取的最大字节数 |
| `input_sleep` | `0.01` | stdin 读取循环的休眠秒数 |

## run() 方法参数详解

`Runner.run(command, **kwargs)` 是命令执行的入口，支持以下参数（默认值来自 Context 配置）：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `command` | `str` | 必填 | 要执行的 shell 命令 |
| `asynchronous` | `bool` | `False` | 异步执行，返回 Promise |
| `disown` | `bool` | `False` | 完全分离子进程 |
| `dry` | `bool` | `False` | 试运行模式（仅打印命令不执行） |
| `echo` | `bool` | `False` | 执行前打印命令字符串 |
| `echo_stdin` | `bool` | 自动判断 | 是否回显 stdin 输入到终端 |
| `encoding` | `str` | 自动检测 | stdout/stderr 编码 |
| `env` | `dict` | `{}` | 更新子进程环境变量 |
| `fallback` | `bool` | `True` | pty 不可用时是否回退到非 pty |
| `hide` | `bool/str` | `None` | 隐藏输出级别 |
| `in_stream` | file-like | `sys.stdin` | 子进程 stdin 来源 |
| `out_stream` | file-like | `sys.stdout` | 子进程 stdout 目标 |
| `err_stream` | file-like | `sys.stderr` | 子进程 stderr 目标 |
| `pty` | `bool` | `False` | 使用伪终端执行 |
| `replace_env` | `bool` | `False` | 用 env 替换整个环境 |
| `shell` | `str` | `bash`/`cmd.exe` | 指定 shell 程序 |
| `timeout` | `float` | `None` | 超时秒数 |
| `warn` | `bool` | `False` | 非零退出时仅警告 |
| `watchers` | `list` | `[]` | StreamWatcher 实例列表 |

### hide 选项

`hide` 参数控制输出可见性，归一化为流名元组：

| 值 | 效果 |
|----|------|
| `None` / `False` | 显示所有输出（默认） |
| `'out'` / `'stdout'` | 仅隐藏 stdout |
| `'err'` / `'stderr'` | 仅隐藏 stderr |
| `'both'` / `True` | 隐藏 stdout 和 stderr |

无论 `hide` 设置如何，stdout/stderr 始终会被捕获并存储在 Result 对象中。`hide=True` 会自动将 `echo` 置为 `False`。

### echo 选项

`echo=True` 时，在执行命令前以粗体 ANSI 格式打印命令字符串。可通过 `echo_format` 参数自定义格式（目前仅支持 `{command}` 占位符）。注意 `hide=True` 会覆盖 `echo=True`。

## 命令执行流程

`run()` 方法内部通过 `_run_body()` 执行以下流程：

```
_setup() → start() → IO线程启动 → wait() → _finish() → Result
```

详细步骤：

1. **`_setup(command, kwargs)`**：统一 kwargs 与配置默认值，设置环境变量，确定编码，echo 命令（如果启用），准备 result 参数
2. **dry-run 检查**：如果 `dry=True`，直接返回退出码为 0 的空 Result
3. **`start(command, shell, env)`**：调用子类实现的 start 方法启动子进程
4. **`disown` 检查**：如果 `disown=True`，返回空 Result 并停止
5. **启动 IO 线程和定时器**：创建 stdout/stderr/stdin 处理线程，启动 timeout 定时器
6. **异步/同步分支**：
   - `asynchronous=True`：返回 `Promise` 对象
   - 同步模式：调用 `_finish()` 等待完成
7. **`_finish()`**：wait 等待进程结束，join IO 线程，汇总结果，检查异常

### 三个 IO 线程

Runner 为每个命令创建最多 3 个后台工作线程：

| 线程目标 | 条件 | 职责 |
|----------|------|------|
| `handle_stdout` | 始终创建 | 读取子进程 stdout，写入 out_stream，追加到 stdout 缓冲区，触发 watcher 响应 |
| `handle_stderr` | 非 pty 模式 | 读取子进程 stderr，写入 err_stream，追加到 stderr 缓冲区 |
| `handle_stdin` | in_stream 非 False | 从 in_stream 读取用户输入，写入子进程 stdin，可选回显 |

每个线程都是 `ExceptionHandlingThread`（封装异常捕获的 Thread 子类）。线程结束后，主线程通过 `thread.exception()` 检查是否有未捕获异常。如果 IO 线程中出现 `WatcherError`，会被收集到 `watcher_errors` 列表中，最终包装为 `Failure` 异常抛出；其他异常则包装为 `ThreadException`。

### 超时机制

当指定 `timeout` 参数时，Runner 创建一个 `threading.Timer`，在超时后调用 `kill()` 方法强制终止子进程。超时后抛出 `CommandTimedOut` 异常（Failure 的子类）。

## Local：本地运行器

`Local` 是 `Runner` 的内置子类，在本地机器上执行命令。它有两种执行模式：

### 非 PTY 模式（默认）

使用 `subprocess.Popen` 创建子进程，通过管道（PIPE）连接 stdin/stdout/stderr：

```python
self.process = Popen(
    command,
    shell=True,
    executable=shell,
    env=env,
    stdout=PIPE,
    stderr=PIPE,
    stdin=PIPE,
)
```

此模式下 stdout 和 stderr 是独立的管道，可以分别读取和捕获。

### PTY 模式

当 `pty=True` 时，Local 使用 `pty.fork()` 创建伪终端：

```python
self.pid, self.parent_fd = pty.fork()
if self.pid == 0:
    # 子进程：设置窗口大小，通过 execvpe 执行 shell 命令
    winsize = struct.pack("HHHH", rows, cols, 0, 0)
    fcntl.ioctl(sys.stdout.fileno(), termios.TIOCSWINSZ, winsize)
    os.execvpe(shell, [shell, "-c", command], env)
```

PTY 模式下 stdout 和 stderr 合并为一个流（从 `parent_fd` 读取），因此无法区分两者——`result.stderr` 始终为空字符串。这是伪终端的本质限制。

### PTY 回退

当 `pty=True` 但 stdin 没有有效的 `fileno()`（例如在管道或测试环境中）时，如果 `fallback=True`（默认），Local 会自动回退到非 PTY 模式，并向 stderr 打印警告信息。设置 `fallback=False` 可禁用此行为。Windows 平台不支持 `pty` 模块，`pty=True` 会直接退出并报错。

### PTY 窗口大小

Local 使用 `pty_size()` 获取控制终端的尺寸（cols, rows），并通过 `TIOCSWINSZ` ioctl 设置到 PTY 子进程中。

## Result：执行结果对象

`Result` 类封装了命令执行的所有结果信息。其构造参数全部暴露为同名属性：

| 属性 | 类型 | 说明 |
|------|------|------|
| `command` | `str` | 执行的命令字符串 |
| `stdout` | `str` | 标准输出（pty 模式下包含 stdout+stderr） |
| `stderr` | `str` | 标准错误（pty 模式下为空） |
| `exited` | `int` | 退出码（watcher 错误/超时时可能为 None） |
| `return_code` | `int` | `exited` 的别名 |
| `ok` | `bool` | `exited == 0` 的便捷属性 |
| `failed` | `bool` | `not ok` 的便捷属性 |
| `shell` | `str` | 使用的 shell 程序 |
| `env` | `dict` | 执行时的环境变量 |
| `pty` | `bool` | 是否使用了 PTY |
| `hide` | `tuple` | 被隐藏的流名元组 |
| `encoding` | `str` | 输出编码 |
| `pid` | `int` | 子进程 PID |
| `disowned` | `bool` | 是否已分离 |

### 布尔求值

Result 对象的布尔值等于 `ok` 属性，因此可以直接在条件中使用：

```python
result = c.run("some command", warn=True)
if result:
    print("命令成功")
else:
    print(f"命令失败，退出码: {result.exited}")
```

### tail() 方法

`result.tail(stream, count=10)` 返回指定流（`"stdout"` 或 `"stderr"`）的最后 `count` 行，用于错误信息展示：

```python
try:
    c.run("failing-command", hide=True)
except UnexpectedExit as e:
    print("stdout 最后10行:", e.result.tail("stdout"))
    print("stderr 最后10行:", e.result.tail("stderr"))
```

Windows 平台下会自动将 `\r\n` 和 `\r` 转换为 `\n`。

### 字符串表示

`str(result)` 返回包含命令描述、退出码和 stdout/stderr 摘要的格式化字符串；`repr(result)` 返回简洁的 `<Result cmd='...' exited=N>` 格式。

## Promise：异步执行承诺

当 `asynchronous=True` 时，`run()` 返回一个 `Promise` 对象而非 Result。Promise 继承自 `Result` 和 `AbstractContextManager`，支持以下操作：

### join() 方法

`promise.join()` 阻塞等待子进程完成，返回最终的 `Result` 对象，或在失败时抛出相应异常（与同步模式一致）：

```python
promise = c.run("long-command", asynchronous=True)
# 做其他事情...
result = promise.join()  # 阻塞等待完成
print(result.stdout)
```

### 上下文管理器

Promise 可以作为上下文管理器使用，退出 `with` 块时自动调用 `join()`：

```python
with c.run("long-command", asynchronous=True) as promise:
    # 做其他事情...
    pass  # 退出 with 块时自动 join()
```

### 异步模式的注意事项

- 异步模式下自动设置 `hide=True`，不转发终端输入/输出
- `asynchronous` 和 `disown` 不能同时为 True
- 必须调用 `join()`（或使用上下文管理器）以确保正确清理，防止解释器关闭时出现问题
- Promise 复制了所有 `run()` 的 kwargs 属性（如 `command`、`shell`、`pty`），但执行结果属性（`stdout`、`exited`）在 `join()` 之前不可用

## disown：完全分离

`disown=True` 使子进程完全脱离 Invoke 的控制：

- 不创建 IO 线程，不捕获 stdout/stderr
- 不检查退出码，`result.exited` 为 `None`
- 子进程可以在 Python 退出后继续运行（通常需要配合 `nohup` 或 shell `&`/`disown`）
- 返回一个功能受限的 Result 对象（`pid` 属性通常有效）

```python
c.run("nohup long-running-daemon &", disown=True)
```

## 异常体系

Runner 执行过程中可能抛出的异常：

| 异常 | 触发条件 |
|------|----------|
| `UnexpectedExit` | 命令非零退出且 `warn=False`（Failure 子类） |
| `CommandTimedOut` | 命令执行超过 `timeout` 秒（Failure 子类） |
| `AuthFailure` | sudo 密码被拒绝（Failure 子类） |
| `Failure` | WatcherError 等非退出码失败 |
| `ThreadException` | IO 线程中出现非 WatcherError 异常 |
| `SubprocessPipeError` | 管道操作失败（如关闭已关闭的 stdin） |

`Failure` 及其子类都携带一个 `result` 属性（Result 对象），用于检查命令执行的上下文信息。`warn=True` 时 `UnexpectedExit` 不会抛出，而是正常返回 Result 对象（`result.failed == True`）。

## 相关概念

- [Context 对象](/concepts/03-context-object.md)
- [配置系统](/concepts/05-configuration.md)
- [StreamWatcher 自动响应](/concepts/09-watchers.md)
- [终端与 IO](/concepts/10-terminals-io.md)
- [PyInvoke 源码信源登记](/references/pyinvoke-source.md)

[^pyinvoke-source]: PyInvoke 源码信源，见 [pyinvoke-source.md](/references/pyinvoke-source.md)；Runner/Local/Result/Promise 定义于 `invoke/runners.py`。
