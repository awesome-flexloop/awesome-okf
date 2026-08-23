---
type: Example
title: 端口转发隧道
description: 本地端口转发、远程端口转发、SOCKS 代理的完整可运行示例
tags: [paramiko, example, port-forwarding, tunnel, socks]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: paramiko-source
    resource: /references/paramiko-source.md
---

# 端口转发隧道

## 本地端口转发

将本地端口通过 SSH 服务器转发到远程目标：

```python
import socket
import select
import threading
import paramiko

def handler(chan, target_host, target_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((target_host, target_port))
    except Exception as e:
        print(f"Forwarding to {target_host}:{target_port} failed: {e}")
        chan.close()
        return

    while True:
        r, w, x = select.select([sock, chan], [], [])
        if sock in r:
            data = sock.recv(4096)
            if len(data) == 0:
                break
            chan.send(data)
        if chan in r:
            data = chan.recv(4096)
            if len(data) == 0:
                break
            sock.send(data)

    chan.close()
    sock.close()

def local_forward(local_port, remote_host, remote_port, transport):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("127.0.0.1", local_port))
    server.listen(5)
    print(f"Local forwarding: 127.0.0.1:{local_port} -> {remote_host}:{remote_port}")

    while True:
        client_sock, addr = server.accept()
        chan = transport.open_channel(
            "direct-tcpip",
            (remote_host, remote_port),
            ("127.0.0.1", local_port),
        )
        if chan is None:
            print("Channel open rejected")
            client_sock.close()
            continue
        t = threading.Thread(
            target=handler,
            args=(chan, client_sock),
        )
        t.daemon = True
        t.start()

def reverse_handler(chan, local_host, local_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((local_host, local_port))
    while True:
        r, w, x = select.select([sock, chan], [], [])
        if sock in r:
            data = sock.recv(4096)
            if not data:
                break
            chan.send(data)
        if chan in r:
            data = chan.recv(4096)
            if not data:
                break
            sock.send(data)
    chan.close()
    sock.close()

with paramiko.SSHClient() as client:
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("bastion.example.com", username="user", password="pass")

    transport = client.get_transport()

    local_forward(
        local_port=8080,
        remote_host="internal-web.example.com",
        remote_port=80,
        transport=transport,
    )
```

## 远程端口转发

在 SSH 服务器上监听端口，转发回本地服务：

```python
import socket
import select
import threading
import paramiko

def forward_handler(channel, origin_addr, dest_addr):
    print(f"Remote forward from {origin_addr} to {dest_addr}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(("127.0.0.1", dest_addr[1]))
    except Exception as e:
        print(f"Connect local failed: {e}")
        channel.close()
        return

    while True:
        r, _, _ = select.select([sock, channel], [], [])
        if sock in r:
            data = sock.recv(4096)
            if not data:
                break
            channel.send(data)
        if channel in r:
            data = channel.recv(4096)
            if not data:
                break
            sock.send(data)

    channel.close()
    sock.close()

with paramiko.SSHClient() as client:
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("public-server.example.com", username="user", password="pass")

    transport = client.get_transport()

    port = transport.request_port_forward(
        address="",
        port=9000,
        handler=forward_handler,
    )
    print(f"Remote forwarding on server port {port}")

    try:
        while True:
            chan = transport.accept(timeout=60)
            if chan is not None:
                print(f"Accepted channel: {chan.get_id()}")
    except KeyboardInterrupt:
        transport.cancel_port_forward("", port)
```

## 双向数据管道

通用的双向数据复制工具函数：

```python
import select

def pipe_between(sock_a, sock_b, chunk_size=4096, timeout=None):
    sockets = [sock_a, sock_b]
    try:
        while True:
            r, _, _ = select.select(sockets, [], [], timeout)
            if not r:
                break
            for sock in r:
                data = sock.recv(chunk_size)
                if not data:
                    return
                other = sock_b if sock is sock_a else sock_a
                other.sendall(data)
    except (OSError, paramiko.SSHException):
        pass
    finally:
        for s in sockets:
            try:
                s.close()
            except:
                pass
```

## SOCKS5 动态代理

简单的 SOCKS5 代理实现：

```python
import socket
import struct
import threading
import select
import paramiko

def handle_socks5_client(client_sock, transport):
    try:
        ver = client_sock.recv(2)
        if ver[0] != 5:
            client_sock.close()
            return
        nmethods = ver[1]
        client_sock.recv(nmethods)
        client_sock.sendall(b"\x05\x00")

        header = client_sock.recv(4)
        if len(header) < 4 or header[1] != 1:
            client_sock.sendall(b"\x05\x07\x00\x01" + b"\x00" * 6)
            client_sock.close()
            return

        addr_type = header[3]
        if addr_type == 1:
            addr_bytes = client_sock.recv(4)
            dest_host = socket.inet_ntoa(addr_bytes)
        elif addr_type == 3:
            length = client_sock.recv(1)[0]
            dest_host = client_sock.recv(length).decode()
        elif addr_type == 4:
            client_sock.recv(16)
            dest_host = "ipv6-unsupported"
        else:
            client_sock.sendall(b"\x05\x08\x00\x01" + b"\x00" * 6)
            client_sock.close()
            return

        port_bytes = client_sock.recv(2)
        dest_port = struct.unpack("!H", port_bytes)[0]

        try:
            chan = transport.open_channel(
                "direct-tcpip",
                (dest_host, dest_port),
                ("127.0.0.1", 0),
            )
        except Exception:
            client_sock.sendall(b"\x05\x05\x00\x01" + b"\x00" * 6)
            client_sock.close()
            return

        client_sock.sendall(b"\x05\x00\x00\x01" + b"\x00" * 6)

        while True:
            r, _, _ = select.select([client_sock, chan], [], [])
            if client_sock in r:
                data = client_sock.recv(4096)
                if not data:
                    break
                chan.send(data)
            if chan in r:
                data = chan.recv(4096)
                if not data:
                    break
                client_sock.send(data)

    except Exception:
        pass
    finally:
        try:
            client_sock.close()
        except:
            pass

def start_socks5_proxy(local_port, transport):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("127.0.0.1", local_port))
    server.listen(5)
    print(f"SOCKS5 proxy listening on 127.0.0.1:{local_port}")

    while True:
        client_sock, _ = server.accept()
        t = threading.Thread(
            target=handle_socks5_client,
            args=(client_sock, transport),
        )
        t.daemon = True
        t.start()

with paramiko.SSHClient() as client:
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("bastion.example.com", username="user", password="pass")
    start_socks5_proxy(1080, client.get_transport())
```

启动后配置浏览器或工具使用 SOCKS5 代理 `127.0.0.1:1080`。

## 数据库连接隧道示例

通过 SSH 隧道连接远程数据库：

```python
import pymysql
import paramiko

with paramiko.SSHClient() as client:
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("bastion.example.com", username="user", password="pass")

    transport = client.get_transport()

    chan = transport.open_channel(
        "direct-tcpip",
        ("db.internal.example.com", 3306),
        ("127.0.0.1", 0),
    )

    sock = chan
    conn = pymysql.connect(
        host="db.internal.example.com",
        user="dbuser",
        password="dbpass",
        database="mydb",
        sock=sock,
    )

    with conn.cursor() as cursor:
        cursor.execute("SELECT VERSION()")
        print(cursor.fetchone())

    conn.close()
```

## 相关概念

- [端口转发](/concepts/08-port-forwarding.md)
- [Transport 底层传输](/concepts/03-transport.md)
- [Channel 通道](/concepts/04-channel.md)
- [高级模式](/concepts/10-advanced-patterns.md)

[^paramiko-source]: paramiko 源码信源，见 [paramiko-source.md](/references/paramiko-source.md)。
