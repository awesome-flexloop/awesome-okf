---
type: Concept
title: 端口转发
description: SSH 端口转发详解——本地转发、远程转发、direct-tcpip 通道、动态 SOCKS 代理
tags: [paramiko, port-forwarding, tunneling, socks]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: paramiko-source
    resource: /references/paramiko-source.md
---

# 端口转发

## 端口转发概念

SSH 端口转发（tunneling）通过加密的 SSH 连接隧道传输其他 TCP 流量。paramiko 通过 Channel 的 `direct-tcpip` 和 `forwarded-tcpip` 通道类型实现端口转发。

三种常见模式：

| 模式 | 方向 | SSH 命令等价 | 用途 |
|------|------|-------------|------|
| 本地转发 | 本地端口 → SSH 服务器 → 远程目标 | `ssh -L` | 访问内网服务 |
| 远程转发 | SSH 服务器端口 → 本地 → 本地目标 | `ssh -R` | 暴露本地服务 |
| 动态转发 | SOCKS 代理 | `ssh -D` | 通用代理 |

## 本地端口转发

本地转发将本地端口的流量通过 SSH 服务器转发到远程目标。

### 基本实现

```python
import socket
import select
import paramiko
import threading

def handle_channel(chan, target_host, target_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((target_host, target_port))
    while True:
        r, w, x = select.select([sock, chan], [], [])
        if sock in r:
            data = sock.recv(1024)
            if len(data) == 0:
                break
            chan.send(data)
        if chan in r:
            data = chan.recv(1024)
            if len(data) == 0:
                break
            sock.send(data)
    chan.close()
    sock.close()

def forward_local_port(local_port, remote_host, remote_port, transport):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("127.0.0.1", local_port))
    server.listen(5)

    while True:
        client_sock, addr = server.accept()
        chan = transport.open_channel(
            "direct-tcpip",
            (remote_host, remote_port),
            ("127.0.0.1", local_port),
        )
        if chan is None:
            client_sock.close()
            continue
        t = threading.Thread(
            target=handle_channel,
            args=(chan, client_sock),
        )
        t.daemon = True
        t.start()
```

### direct-tcpip 通道

`open_channel("direct-tcpip", dest_addr, src_addr)` 参数：

- `dest_addr`：目标地址元组 `(host, port)`，从 SSH 服务器角度可达的地址
- `src_addr`：来源地址元组 `(host, port)`，发起连接的地址

```python
chan = transport.open_channel(
    "direct-tcpip",
    ("internal-db.example.com", 3306),
    ("localhost", 12345),
)
```

通道建立后，通过 `chan.send()`/`chan.recv()` 与目标服务通信，数据由 SSH 服务器转发到 `dest_addr`。

## 远程端口转发

远程转发在 SSH 服务器上监听端口，将连接通过 SSH 隧道转回本地可达的目标。

### 请求远程转发

```python
def forward_handler(channel, src_addr, dest_addr):
    print(f"Forwarded connection from {src_addr} to {dest_addr}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(("localhost", dest_addr[1]))
    except Exception:
        channel.close()
        return
    while True:
        r, w, x = select.select([sock, channel], [], [])
        if sock in r:
            data = sock.recv(1024)
            if len(data) == 0:
                break
            channel.send(data)
        if channel in r:
            data = channel.recv(1024)
            if len(data) == 0:
                break
            sock.send(data)
    channel.close()
    sock.close()

port = transport.request_port_forward("", 8080, handler=forward_handler)
print(f"Remote forwarding on port {port}")

transport.accept()
```

### request_port_forward

`request_port_forward(address, port, handler=None)`：

- `address`：服务器绑定地址，`""` 表示所有接口
- `port`：服务器监听端口，0 表示由服务器分配
- `handler`：连接到达时的回调函数，接收 `(channel, origin_addr, dest_addr)`

返回实际绑定的端口号。

### 取消转发

```python
transport.cancel_port_forward("", 8080)
```

### 服务端配合

服务端需通过 `ServerInterface.check_port_forward_request()` 授权：

```python
class MyServer(paramiko.ServerInterface):
    def check_port_forward_request(self, address, port):
        if port == 8080:
            return port
        return None

    def cancel_port_forward_request(self, address, port):
        pass
```

## 双向转发处理

无论是本地还是远程转发，核心都是在 Channel 和本地 socket 之间双向复制数据：

```python
def pipe_sockets(sock1, sock2, timeout=60):
    while True:
        r, _, _ = select.select([sock1, sock2], [], [], timeout)
        if not r:
            break
        for sock in r:
            data = sock.recv(4096)
            if not data:
                return
            other = sock2 if sock is sock1 else sock1
            other.sendall(data)
```

可使用 `chan.makefile()` 获取文件对象简化处理。

## 动态 SOCKS 代理

paramiko 本身不内建 SOCKS 服务器，但可以通过 `direct-tcpip` 通道实现：

```python
import struct
import select

def handle_socks5(transport, client_sock):
    data = client_sock.recv(2)
    if len(data) < 2 or data[0] != 0x05:
        client_sock.close()
        return
    nmethods = data[1]
    methods = client_sock.recv(nmethods)
    client_sock.sendall(b"\x05\x00")

    header = client_sock.recv(4)
    if len(header) < 4 or header[1] != 0x01:
        client_sock.close()
        return

    addr_type = header[3]
    if addr_type == 0x01:
        addr_bytes = client_sock.recv(4)
        dest_host = socket.inet_ntoa(addr_bytes)
    elif addr_type == 0x03:
        length = client_sock.recv(1)[0]
        dest_host = client_sock.recv(length).decode()
    port_bytes = client_sock.recv(2)
    dest_port = struct.unpack("!H", port_bytes)[0]

    try:
        chan = transport.open_channel(
            "direct-tcpip",
            (dest_host, dest_port),
            ("127.0.0.1", 0),
        )
    except Exception:
        client_sock.sendall(b"\x05\x01\x00\x01" + b"\x00" * 6)
        client_sock.close()
        return

    client_sock.sendall(b"\x05\x00\x00\x01" + b"\x00" * 6)
    pipe_sockets(client_sock, chan)
```

然后在本地监听并处理每个 SOCKS5 连接，配合浏览器或其他支持 SOCKS5 的工具使用。

## X11 转发

```python
def x11_handler(channel, src_addr, dest_addr):
    x11_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    x11_sock.connect(os.environ["DISPLAY"])
    pipe_sockets(channel, x11_sock)

chan = transport.open_session()
chan.request_x11(
    handler=x11_handler,
    auth_cookie="random-cookie",
    screen_number=0,
    single_connection=True,
)
chan.exec_command("xterm")
```

## 转发中的注意事项

### 通道窗口大小

转发大量数据时可调整窗口大小和包大小提升性能：

```python
chan = transport.open_channel(
    "direct-tcpip",
    dest_addr,
    src_addr,
    window_size=4194304,
    max_packet_size=65536,
)
```

### 超时与错误处理

```python
try:
    chan = transport.open_channel(
        "direct-tcpip", dest, src, timeout=10
    )
except paramiko.ChannelException as e:
    print(f"Channel open failed: code={e.code}, text={e.text}")
except socket.timeout:
    print("Channel open timed out")
```

### 线程模型

每个转发连接通常需要一个独立线程处理双向 IO。使用 `select` 可在单线程中处理多个连接，但 Channel 的 `recv_ready()` 也可用于非阻塞检查：

```python
if chan.recv_ready():
    data = chan.recv(4096)
if chan.exit_status_ready():
    break
```

### 关闭顺序

转发结束时正确的关闭顺序：

1. 停止接受新连接
2. 关闭本地监听 socket
3. 等待处理线程结束
4. 取消远程端口转发（如适用）
5. 关闭 Channel 和 Transport

## 相关概念

- [Transport 底层传输](03-transport.md)
- [Channel 通道](04-channel.md)
- [服务端开发](09-server.md)
- [高级模式](10-advanced-patterns.md)
- [端口转发示例](../examples/port-forwarding.md)

[^paramiko-source]: paramiko 源码信源，见 [paramiko-source.md](../references/paramiko-source.md)。
