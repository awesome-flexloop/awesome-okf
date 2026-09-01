---
type: Concept
title: Channel 通道
description: Channel 多路复用通道详解——exec/shell/subsystem、PTY、recv/send、exit_status、X11/agent 转发
tags: [paramiko, channel, multiplexing]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: paramiko-source
    resource: /references/paramiko-source.md
---

# Channel 通道

## Channel 的概念

`Channel` 是 SSH 连接上的安全隧道。SSH2 协议允许在单个加密传输上多路复用多个通道，每个通道独立进行流量控制。Channel 的 API 设计与 Python socket 几乎一致，支持 `recv`、`send`、`settimeout`、`setblocking`、`fileno` 等方法。

Channel 继承 `ClosingContextManager`，支持 `with` 语句。

## 获取 Channel

Channel 通常不直接构造，而是通过 Transport 或 SSHClient 获取：

```python
chan = transport.open_session()

chan = client.invoke_shell()

chan = transport.open_channel("direct-tcpip", dest_addr, src_addr)
```

## 通道类型

### session 通道

最常用的通道类型，支持 exec、shell、subsystem 三种请求：

```python
chan = transport.open_session()

chan.exec_command("uname -a")

chan.invoke_shell()

chan.invoke_subsystem("sftp")
```

### direct-tcpip 通道

用于本地端口转发，将 TCP 连接通过 SSH 隧道转发：

```python
chan = transport.open_channel(
    "direct-tcpip",
    ("internal-db.example.com", 3306),
    ("127.0.0.1", 12345),
)
```

### x11 通道

用于 X11 转发：

```python
chan = transport.open_x11_channel(src_addr=("localhost", 6010))
```

## 执行命令

### exec_command

```python
chan = transport.open_session()
chan.exec_command("ls -la /tmp")

output = chan.recv(4096)
exit_code = chan.recv_exit_status()
```

exec_command 在通道上执行单条命令，命令结束后通道进入 EOF 状态。

### 交互式 Shell

```python
chan = transport.open_session()
chan.get_pty(term="xterm", width=120, height=40)
chan.invoke_shell()

chan.send(b"ls -la\n")
import time; time.sleep(0.5)
print(chan.recv(4096).decode())
```

### 子系统

```python
chan = transport.open_session()
chan.invoke_subsystem("sftp")
```

## 伪终端 (PTY)

### 请求 PTY

```python
chan.get_pty(
    term="vt100",
    width=80,
    height=24,
    width_pixels=0,
    height_pixels=0,
)
```

参数：

- `term`：终端类型（如 `"vt100"`、`"xterm"`、`"ansi"`）
- `width`/`height`：字符行列数
- `width_pixels`/`height_pixels`：像素尺寸（通常为 0）

### 调整终端大小

```python
chan.resize_pty(width=120, height=50)
```

窗口大小变化时发送 SSH_MSG_CHANNEL_REQUEST window-change。

## 数据收发

### 读取数据

```python
data = chan.recv(4096)

err_data = chan.recv_stderr(4096)

ready = chan.recv_ready()
err_ready = chan.recv_stderr_ready()
```

`recv_ready()` 非阻塞检查是否有数据可读，适合配合 select 使用。

### 发送数据

```python
sent = chan.send(b"hello\n")
chan.sendall(b"large data block\n")
chan.send_stderr(b"error output\n")
```

`send` 可能部分发送，返回实际发送字节数；`sendall` 阻塞直到全部发送。

### 超时与阻塞

```python
chan.settimeout(10.0)
chan.setblocking(True)
print(chan.gettimeout())
```

与 Python socket 行为一致：超时模式下 recv/send 在超时后抛出 `socket.timeout`。

### 合并 stderr

```python
chan.set_combine_stderr(True)
```

将 stderr 数据合并到 stdout 流中读取。

## 退出状态

```python
chan.exit_status_ready()

exit_code = chan.recv_exit_status()
print(f"Exit status: {exit_code}")

print(chan.exit_status)
```

- `exit_status_ready()`：非阻塞检查远端进程是否已退出
- `recv_exit_status()`：阻塞等待并返回退出码
- `exit_status` 属性：初始为 -1，退出后为实际退出码

## 环境变量

```python
chan.set_environment_variable("LANG", "en_US.UTF-8")
chan.update_environment({"MY_VAR": "value", "DEBUG": "1"})
```

> 服务器可能通过 `AcceptEnv` 配置限制允许的环境变量，不被接受的变量会被静默忽略。

## X11 转发

```python
def x11_handler(channel, src_addr, dest_addr):
    print(f"X11 connection from {src_addr} to {dest_addr}")

chan.request_x11(
    handler=x11_handler,
    auth_cookie="abc123",
    screen_number=0,
    single_connection=False,
)
```

## Agent 转发

```python
def agent_handler(channel):
    print("Agent forwarding requested")

chan.request_forward_agent(agent_handler)
```

## 文件对象

Channel 提供三种类文件对象：

```python
stdin = chan.makefile_stdin("wb", -1)
stdout = chan.makefile("r", -1)
stderr = chan.makefile_stderr("r", -1)
```

这些返回 `ChannelStdinFile`、`ChannelFile`、`ChannelStderrFile` 实例，继承自 `BufferedFile`，支持标准 Python 文件接口（read/readline/write/close 等）。

```python
stdout = chan.makefile("r")
for line in stdout:
    print(line.rstrip())
```

## 通道信息

```python
chan.get_id()
chan.get_name()
chan.get_transport()
chan.getpeername()
chan.origin_addr
```

- `get_id()`：通道 ID
- `get_name()`：通道名（字符串形式的 ID）
- `get_transport()`：所属 Transport
- `getpeername()`：对端地址（如果是转发通道）
- `origin_addr`：转发通道的来源地址

## 关闭与关闭控制

```python
chan.close()
chan.shutdown(how)
chan.shutdown_read()
chan.shutdown_write()
```

- `close()`：完全关闭通道
- `shutdown_read()`：半关闭读取端（发送 EOF）
- `shutdown_write()`：半关闭写入端

`open_only` 装饰器保护的方法在通道关闭后调用会抛出 `SSHException("Channel is not open")`。

## 底层属性

```python
chan.closed
chan.active
chan.eof_received
chan.eof_sent
chan.in_window_size
chan.out_window_size
```

这些属性可用于检查通道状态，但通常不直接修改。

## Channel 与 socket 的对比

| 特性 | socket | Channel |
|------|--------|---------|
| recv/send | ✓ | ✓ |
| settimeout/setblocking | ✓ | ✓ |
| makefile | ✓ | ✓（三种流） |
| fileno | ✓ | ✓（可用于 select） |
| 多路复用 | 无 | 单 Transport 多 Channel |
| 独立流控 | 无 | 每通道独立窗口 |
| stderr | 无 | ✓ 独立流 |
| exit status | 无 | ✓ |
| PTY | 无 | ✓ |

## 相关概念

- [Transport 底层传输](03-transport.md)
- [SSHClient 详解](02-ssh-client.md)
- [认证体系](05-authentication.md)
- [端口转发](08-port-forwarding.md)
- [交互式 Shell 示例](../examples/interactive-shell.md)

[^paramiko-source]: paramiko 源码信源，见 [paramiko-source.md](../references/paramiko-source.md)。
