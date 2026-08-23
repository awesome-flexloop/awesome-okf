---
type: Concept
title: 通道与流
description: SSHChannel 通道抽象、会话/执行/direct-tcpip 通道类型、PTY 伪终端、窗口调整
tags: [asyncssh, channel, stream, pty, ssh]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: asyncssh-source
    resource: /references/asyncssh-source.md
---

# 通道与流

## SSHChannel 的定位

`SSHChannel` 是 asyncssh 中所有 SSH 通道的泛型基类，定义于 `channel.py:86`，继承 `SSHPacketHandler`，类型参数为 `AnyStr`（`str` 或 `bytes`）。通道是 SSH 连接上多路复用的逻辑数据流，类似 TCP socket 但运行在加密的 SSH 会话之上。

通常不直接使用 `SSHChannel`，而是通过其具体子类：

- `SSHClientChannel`（channel.py:1119）：客户端通道，支持 exec/shell/subsystem
- `SSHServerChannel`（channel.py:1497）：服务端通道，处理客户端请求
- `SSHTCPChannel`：direct-tcpip / forwarded-tcpip 通道
- `SSHUNIXChannel`：UNIX domain socket 转发通道
- `SSHTunTapChannel`：TUN/TAP 设备通道
- `SSHForwardChannel`：端口转发通道基类
- `SSHLineEditorChannel`：带行编辑功能的通道（editor.py）

## 通道默认参数

| 参数 | 默认值 | 位置 |
|------|--------|------|
| 接收窗口 | 2 MiB（2097152 字节） | connection.py:277 |
| 最大包大小 | 32 KiB（32768 字节） | connection.py:278 |

## SSHChannel 核心方法

### 写入数据

```python
channel.write(data)
channel.writelines([data1, data2])
channel.write_eof()
```

- `write(data, datatype=None)`：写入数据，`datatype` 可指定扩展数据类型（如 `EXTENDED_DATA_STDERR` 发送 stderr）
- `writelines(list_of_data, datatype=None)`：批量写入
- `write_eof()`：半关闭写入端（发送 EOF）

服务端通道有专门的 stderr 写入方法：

```python
server_channel.write_stderr(data)
server_channel.writelines_stderr(data_list)
```

### 读取数据

通道本身不直接提供 `read()` 方法——读取通过 `SSHReader` 流对象完成。底层通过 `data_received(data, datatype)` 回调接收数据。

### 流控制

```python
channel.pause_reading()
channel.resume_reading()
channel.get_write_buffer_size()
channel.set_write_buffer_limits(high=None, low=None)
```

### 关闭

```python
channel.close()
channel.abort()
await channel.wait_closed()
channel.is_closing()
```

- `close()`：优雅关闭，发送 EOF 后等待对端关闭
- `abort()`：立即强制关闭
- `wait_closed()`：协程，等待通道完全关闭
- `is_closing()`：返回是否正在关闭

### 扩展信息

```python
channel.get_extra_info('peername')
channel.set_extra_info(custom_key='value')
channel.get_connection()
channel.get_loop()
channel.get_encoding()
channel.set_encoding('utf-8', errors='strict')
channel.get_recv_window()
```

## SSHClientChannel 方法

### 退出状态

```python
status = channel.get_exit_status()
signal = channel.get_exit_signal()
returncode = channel.get_returncode()
```

- `get_exit_status()`：返回退出码 `Optional[int]`，进程未结束时返回 None
- `get_exit_signal()`：返回退出信号元组 `(signal_name, core_dumped, message, lang)`
- `get_returncode()`：返回退出码，或信号编号的负值（类比 `subprocess.Popen.returncode`）

### 终端控制

```python
channel.change_terminal_size(width, height, pixwidth=0, pixheight=0)
channel.send_break(msec)
channel.send_signal(signal)
channel.terminate()
channel.kill()
```

- `change_terminal_size()`：改变 PTY 窗口大小
- `send_break(msec)`：发送 break 信号
- `send_signal(signal)`：发送信号（字符串如 `'TERM'`/`'KILL'`，或信号编号）
- `terminate()`：发送 SIGTERM
- `kill()`：发送 SIGKILL

### 会话信息

```python
channel.get_environment()
channel.get_environment_bytes()
channel.get_command()
channel.get_subsystem()
```

## SSHServerChannel 方法

### 终端信息

```python
term_type = channel.get_terminal_type()
width, height, pixwidth, pixheight = channel.get_terminal_size()
mode = channel.get_terminal_mode(opcode)
modes = channel.get_terminal_modes()
```

### 退出

```python
channel.exit(status)
channel.exit_with_signal(signal, core_dumped=False, message='', lang='')
```

### X11 和 Agent 转发

```python
display = channel.get_x11_display()
agent_path = channel.get_agent_path()
```

### 流控制

```python
channel.set_xon_xoff(client_can_do)
```

## 通道类型

### 会话通道（session）

通过 `create_session()` / `open_session()` / `create_process()` 创建，用于执行命令、启动 shell 或打开子系统：

```python
writer, reader, chan = await conn.open_session(command='ls -la')
writer, reader, chan = await conn.open_session(term_type='xterm',
                                               term_size=(80, 24))
writer, reader, chan = await conn.open_session(subsystem='sftp')
```

### Direct TCP/IP 通道

通过 `create_connection()` / `open_connection()` 创建，请求服务器向目标发起 TCP 连接：

```python
chan, session = await conn.create_connection(
    SSHTCPSession, 'remote-db.example.com', 5432,
    orig_host='localhost', orig_port=12345
)
```

### 转发 TCP/IP 通道

当服务器请求客户端接受转发连接时创建，由 `start_server()` / `create_server()` 的回调处理。

### UNIX Socket 通道

通过 `create_unix_connection()` / `create_unix_server()` 创建，用于 UNIX domain socket 转发。

## PTY 伪终端

请求 PTY 后，通道连接到远程伪终端设备，可用于全屏交互式程序：

```python
proc = await conn.create_process(term_type='xterm',
                                 term_size=(80, 24, 0, 0),
                                 term_modes={os_tty_operations})
```

`term_type` 设置 `$TERM` 环境变量，`term_size` 是 `(columns, rows, pixels_width, pixels_height)`。

终端大小改变时调用：

```python
proc.change_terminal_size(120, 40)
```

服务端可通过 `TerminalSizeChanged` 异常或 `SSHServerProcess.term_size` 属性获取新尺寸。

## 通道与流的关系

通道层提供底层字节流，流层在其上提供 asyncio 风格 API：

```
SSHChannel（字节流）
    └── SSHStreamSession（缓冲与背压）
            ├── SSHReader.read()/readline()/readuntil()
            └── SSHWriter.write()/drain()
```

`open_session()` 返回 `(SSHWriter, SSHReader, SSHClientChannel)` 三元组：

```python
writer, reader, chan = await conn.open_session(command='cat')
writer.write('hello\n')
await writer.drain()
response = await reader.readline()
```

`create_process()` 在流层之上进一步封装为进程模型，提供 `stdin`/`stdout`/`stderr` 三个独立流。

## 相关概念

- [流与进程](/concepts/04-streams-processes.md) —— SSHReader/SSHWriter、create_process、SSHCompletedProcess
- [异步连接详解](/concepts/02-async-connection.md) —— 如何创建连接
- [端口转发](/concepts/09-port-forwarding.md) —— TCP/UNIX 通道的转发应用
- [paramiko Channel 通道](../../paramiko/concepts/04-channel.md)（同步 Channel 对比）

[^asyncssh-source]: asyncssh 源码信源，见 [asyncssh-source.md](/references/asyncssh-source.md)。
