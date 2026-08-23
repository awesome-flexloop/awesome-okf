---
type: Concept
title: 流与进程
description: SSHReader/SSHWriter 异步流 API、create_process、SSHClientProcess、SSHCompletedProcess、stdin/stdout/stderr 重定向
tags: [asyncssh, stream, process, reader, writer]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: asyncssh-source
    resource: /references/asyncssh-source.md
---

# 流与进程

## SSHReader

`SSHReader` 定义于 `stream.py:72`，是泛型类（`Generic[AnyStr]`），提供从 SSH 通道异步读取数据的接口，API 风格与 `asyncio.StreamReader` 一致。

### 读取方法

```python
async def read(n=-1) -> AnyStr
async def readline() -> AnyStr
async def readuntil(separator) -> AnyStr
async def readexactly(n) -> AnyStr
```

- `read(n=-1)`：读取最多 n 字节，n=-1 时读取直到 EOF
- `readline()`：读取直到换行符 `\n`
- `readuntil(separator)`：读取直到遇到分隔符
- `readexactly(n)`：精确读取 n 字节，不足时抛出异常

### 状态查询

```python
reader.at_eof() -> bool
reader.channel
reader.get_extra_info(name, default=None)
```

### 异步迭代

`SSHReader` 支持异步迭代协议，逐行读取：

```python
async for line in proc.stdout:
    print(line, end='')
```

## SSHWriter

`SSHWriter` 定义于 `stream.py:257`，提供向 SSH 通道异步写入数据的接口，API 风格与 `asyncio.StreamWriter` 一致。

### 写入方法

```python
writer.write(data)
writer.writelines(data_list)
writer.write_eof()
await writer.drain()
```

- `write(data)`：写入数据（立即返回，数据缓冲）
- `writelines(data_list)`：批量写入
- `write_eof()`：写入 EOF，半关闭写入方向
- `drain()`：协程，等待缓冲区刷新到网络（背压控制）

### 关闭

```python
writer.close()
writer.is_closing() -> bool
await writer.wait_closed()
writer.can_write_eof() -> bool
```

## SSHClientProcess

`SSHClientProcess` 定义于 `process.py:1240`，继承 `SSHProcess`（process.py:819）和 `SSHClientStreamSession`，是执行远程命令的高级抽象。

### 创建进程

通过 `SSHClientConnection.create_process()` 创建：

```python
proc = await conn.create_process(command='ls -la')
```

不指定 `command` 时启动交互式 shell：

```python
proc = await conn.create_process(term_type='xterm',
                                 term_size=(80, 24))
```

### stdin/stdout/stderr

`SSHClientProcess` 暴露三个流属性：

| 属性 | 类型 | 说明 |
|------|------|------|
| `proc.stdin` | `SSHWriter` | 标准输入 |
| `proc.stdout` | `SSHReader` | 标准输出 |
| `proc.stderr` | `SSHReader` | 标准错误 |

```python
proc = await conn.create_process('cat')
proc.stdin.write('hello\n')
await proc.stdin.drain()
response = await proc.stdout.readline()
```

### 等待与输出收集

```python
async def wait(check=False, timeout=None) -> SSHCompletedProcess
async def communicate(input=None) -> Tuple[AnyStr, AnyStr]
collect_output() -> Tuple[AnyStr, AnyStr]
```

`wait()` 等待进程结束，返回 `SSHCompletedProcess`：

```python
result = await proc.wait()
print(result.stdout)
```

`check=True` 时非零退出码抛出 `ProcessError`。`timeout` 超时抛出 `TimeoutError`。

`communicate()` 发送输入并等待所有输出：

```python
stdout, stderr = await proc.communicate(input='data\n')
```

### 进程控制

```python
proc.change_terminal_size(width, height, pixwidth=0, pixheight=0)
proc.send_break(msec)
proc.send_signal(signal)
proc.terminate()  # SIGTERM
proc.kill()       # SIGKILL
```

### 状态属性

```python
proc.exit_status    # Optional[int]
proc.exit_signal    # Optional[Tuple[str, bool, str, str]]
proc.returncode     # Optional[int]
proc.command        # Optional[str]
proc.subsystem      # Optional[str]
proc.env            # Mapping[str, str]
```

### 重定向

`create_process()` 支持 `stdin`/`stdout`/`stderr` 重定向参数：

```python
proc = await conn.create_process(
    'cmd',
    stdin=open('input.txt', 'rb'),
    stdout=open('output.txt', 'wb'),
    stderr=asyncssh.DEVNULL
)
```

重定向目标可以是：

| 值 | 含义 |
|----|------|
| `PIPE`（默认） | 创建可读写的流对象 |
| `DEVNULL` | 丢弃输出 / 无输入 |
| `STDOUT` | 仅用于 stderr，重定向到 stdout |
| 文件路径 `str` | 打开文件读写 |
| 文件对象 | 直接使用 |
| 文件描述符 `int` | `os.fdopen` 包装 |
| `SSHReader`/`SSHWriter` | 进程间管道 |
| `asyncio.StreamReader`/`StreamWriter` | 与 asyncio 子进程桥接 |

`input` 参数可直接传入数据（优先于 `stdin`）：

```python
proc = await conn.create_process('cat', input='hello\n')
```

### 异步上下文管理器

```python
async with conn.create_process('cat') as proc:
    proc.stdin.write('data\n')
    await proc.stdin.drain()
```

退出上下文时自动调用 `close()` 和 `wait_closed()`。

## SSHCompletedProcess

`SSHCompletedProcess` 定义于 `process.py:774`，是 `Record` 数据类，包含以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `env` | `Optional[Mapping[str, str]]` | 客户端设置的环境变量 |
| `command` | `Optional[str]` | 请求执行的命令 |
| `subsystem` | `Optional[str]` | 请求打开的子系统 |
| `exit_status` | `Optional[int]` | 退出状态码，信号退出时为 -1 |
| `exit_signal` | `Optional[Tuple]` | 退出信号 `(name, core_dumped, message, lang)` |
| `returncode` | `Optional[int]` | 退出码，信号退出时为信号编号的负值 |
| `stdout` | `Optional[BytesOrStr]` | 标准输出（未重定向时） |
| `stderr` | `Optional[BytesOrStr]` | 标准错误（未重定向时） |

## conn.run() 便捷方法

`SSHClientConnection.run()` 是 `create_process()` + `wait()` 的便捷包装：

```python
async def run(*args, check=False, timeout=None, **kwargs) -> SSHCompletedProcess
```

一行执行命令并收集输出：

```python
result = await conn.run('uname -a', check=True)
print(result.stdout)
```

所有 `create_process()` 的参数（command/term_type/term_size/env/encoding 等）均可传入。

## create_subprocess()

`create_subprocess()` 提供与 `asyncio.create_subprocess_exec()` 类似的 API，返回 `(SSHSubprocessTransport, SSHSubprocessProtocol)`：

```python
transport, protocol = await conn.create_subprocess(
    MyProtocol, 'ls', '-la'
)
```

## 编码模式

### 字符串模式（默认）

默认 `encoding='utf-8'`，`read()` 返回 `str`，`write()` 接受 `str`：

```python
result = await conn.run('echo hello')
print(type(result.stdout))  # <class 'str'>
```

### Bytes 模式

设置 `encoding=None`，所有数据以 `bytes` 处理：

```python
result = await conn.run('echo hello', encoding=None)
print(type(result.stdout))  # <class 'bytes'>
```

### 错误处理

`errors` 参数控制 Unicode 解码错误策略（默认 `'strict'`）：

```python
result = await conn.run('cmd', encoding='utf-8', errors='replace')
```

## SSHServerProcess

`SSHServerProcess` 定义于 `process.py:1607`，继承 `SSHProcess` 和 `SSHServerStreamSession`，在服务端使用。它额外提供：

```python
proc.term_type   # Optional[str] 终端类型
proc.term_size   # Tuple[int, int, int, int] 终端大小
```

服务端进程的 stdin 是 `SSHReader`（接收客户端数据），stdout/stderr 是 `SSHWriter`（向客户端发送数据）。

## 异常

- `ProcessError`（process.py:694）：非零退出码（check=True 时抛出），包含 exit_status/stdout/stderr 等字段
- `TimeoutError`（process.py:758）：等待超时，继承 `ProcessError` 和 `asyncio.TimeoutError`

## 相关概念

- [通道与流](/concepts/03-channels.md) —— SSHChannel 底层通道
- [异步连接详解](/concepts/02-async-connection.md) —— create_process 的连接前提
- [服务端开发](/concepts/10-server.md) —— SSHServerProcess 的服务端用法
- [paramiko Channel 通道](../../paramiko/concepts/04-channel.md)（同步通道对比）

[^asyncssh-source]: asyncssh 源码信源，见 [asyncssh-source.md](/references/asyncssh-source.md)。
