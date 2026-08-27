---
type: Concept
title: 端口转发
description: forward_local_port/forward_remote_port、SSHForwarder、SOCKS 代理、UNIX socket 转发、TCP/Path 混合转发
tags: [asyncssh, port-forwarding, tunnel, socks, proxy]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: asyncssh-source
    resource: /references/asyncssh-source.md
---

# 端口转发

## 转发模型

asyncssh 支持完整的 SSH 端口转发体系，通过 `SSHForwarder`（forward.py:41）和 `SSHListener`（listener.py:52）实现。转发分为两大方向：

- **本地转发（Local Forwarding）**：客户端监听本地端口，通过 SSH 隧道转发到远程目标
- **远程转发（Remote Forwarding）**：服务端监听端口，通过 SSH 隧道转发回客户端可达的目标

## 本地端口转发

`forward_local_port()` 定义于 connection.py:3252：

```python
async def forward_local_port(
    listen_host, listen_port,
    dest_host, dest_port,
    accept_handler=None
) -> SSHListener
```

```python
listener = await conn.forward_local_port(
    'localhost', 8080,
    'internal-db.example.com', 5432
)
print(f'监听在 localhost:{listener.get_port()}')
await listener.wait_closed()
```

本地访问 `localhost:8080` 的流量通过 SSH 隧道转发到服务器可达的 `internal-db.example.com:5432`。

### 动态端口（端口 0）

```python
listener = await conn.forward_local_port(
    'localhost', 0,  # 0 表示系统分配端口
    'remote-host', 80
)
print(f'动态分配端口: {listener.get_port()}')
```

### 访问控制

`accept_handler` 参数可控制是否允许转发：

```python
async def accept(orig_host, orig_port):
    return orig_host in allowed_clients

listener = await conn.forward_local_port(
    '0.0.0.0', 8080, 'remote', 80,
    accept_handler=accept
)
```

### 异步上下文管理器

```python
async with conn.forward_local_port('localhost', 8080,
                                    'remote', 80) as listener:
    await listener.wait_closed()
```

### 关闭转发

```python
listener.close()
await listener.wait_closed()
```

## 远程端口转发

`forward_remote_port()` 定义于 connection.py:5476：

```python
async def forward_remote_port(
    listen_host, listen_port,
    dest_host, dest_port,
    accept_handler=None
) -> SSHListener
```

```python
listener = await conn.forward_remote_port(
    '', 8080,
    'localhost', 3000
)
```

服务器监听 8080 端口，访问该端口的流量通过隧道转发到客户端的 `localhost:3000`。常用于将内网服务暴露到公网服务器。

## UNIX Socket 转发

### 本地 Path 到远程 Path

```python
listener = await conn.forward_local_path(
    '/tmp/local.sock',
    '/var/run/docker.sock'
)
```

### 本地 TCP 到远程 UNIX Socket

`forward_local_port_to_path()`（connection.py:5349）：

```python
listener = await conn.forward_local_port_to_path(
    'localhost', 5432,
    '/var/run/postgresql/.s.PGSQL.5432'
)
```

### 本地 UNIX Socket 到远程 TCP

`forward_local_path_to_port()`（connection.py:5425）：

```python
listener = await conn.forward_local_path_to_port(
    '/tmp/local.sock',
    'remote-host', 80
)
```

### 远程 TCP 到本地 UNIX Socket

`forward_remote_port_to_path()`（connection.py:5557）

### 远程 UNIX Socket 到本地 TCP

`forward_remote_path_to_port()`（connection.py:5599）

## SOCKS 代理

`forward_socks()` 定义于 connection.py:5639，创建 SOCKS4/SOCKS5 代理监听器：

```python
listener = await conn.forward_socks('localhost', 1080)
print(f'SOCKS 代理监听在端口 {listener.get_port()}')
await listener.wait_closed()
```

通过该代理的连接由 SSH 服务器代为建立目标 TCP 连接。可配置浏览器或命令行工具使用此 SOCKS 代理：

```bash
curl --socks5 localhost:1080 http://internal.example.com
```

## TUN/TAP 转发

### 三层隧道（TUN）

`forward_tun()`（connection.py:5695）：

```python
listener = await conn.forward_tun(local_unit=0)
```

### 二层隧道（TAP）

`forward_tap()`（connection.py:5730）：

```python
listener = await conn.forward_tap(local_unit=0)
```

TUN/TAP 需要 root 权限和系统支持。

## SSHForwarder

`SSHForwarder`（forward.py:41）继承 `asyncio.BaseProtocol`，是转发连接的协议处理器：

- `write(data)` / `write_eof()`：写入数据
- `pause_reading()` / `resume_reading()`：流控制
- `close()`：关闭转发
- `get_extra_info(name)`：获取连接信息
- `connection_made(transport)` / `connection_lost(exc)`：生命周期回调
- `data_received(data, datatype)` / `eof_received()`：数据回调

子类：
- `SSHLocalForwarder`（forward.py:192）：本地转发基类
- `SSHLocalPortForwarder`（forward.py:229）：TCP 本地转发
- `SSHLocalPathForwarder`（forward.py:245）：UNIX socket 本地转发
- `SSHSOCKSForwarder`（socks.py）：SOCKS 代理

## SSHListener

`SSHListener`（listener.py:52）是转发监听器基类：

| 方法 | 说明 |
|------|------|
| `close()` | 停止接受新连接（已有连接继续） |
| `await wait_closed()` | 等待监听器和所有连接关闭 |
| `get_port()` | 获取监听端口（TCP） |
| `get_addresses()` | 获取监听地址列表 |
| `set_tunnel(conn)` | 设置关联的隧道连接 |

支持异步上下文管理器（`async with`）。

监听器子类：
- `SSHForwardListener`（listener.py:234）：本地转发监听器
- `SSHTCPClientListener`（listener.py:150）：远程 TCP 转发监听器
- `SSHUNIXClientListener`（listener.py:199）：远程 UNIX 转发监听器

## Direct TCP/IP 连接（一次性转发）

除了监听器模式，还可通过 `create_connection()` 打开单次转发连接：

```python
chan, session = await conn.create_connection(
    SSHTCPSession,
    'remote-db.example.com', 5432
)
```

`open_connection()` 返回流风格接口：

```python
reader, writer, chan = await conn.open_connection(
    'remote-db.example.com', 5432
)
writer.write(b'query\n')
response = await reader.readline()
writer.close()
```

## 服务端转发控制

`SSHServer` 回调控制是否允许转发：

```python
class MyServer(asyncssh.SSHServer):
    def connection_requested(self, dest_host, dest_port, orig_host, orig_port):
        # direct-tcpip 请求
        return dest_port in allowed_ports

    def server_requested(self, listen_host, listen_port):
        # tcpip-forward 请求（远程转发）
        return listen_port >= 1024
```

## 转发配置参数

连接时可配置转发相关选项：

```python
conn = await asyncssh.connect(
    host,
    permit_remote_port_forwards=True,
    permit_open_direct_tcpip=True,
    permit_tun_device=False
)
```

## 相关概念

- [异步连接详解](02-async-connection.md) —— 建立转发所需的连接
- [通道与流](03-channels.md) —— direct-tcpip 通道
- [实战示例：端口转发隧道](../examples/port-forward-tunnel.md)
- [paramiko 端口转发](../../paramiko/concepts/08-port-forwarding.md)（同步转发对比）

[^asyncssh-source]: asyncssh 源码信源，见 [asyncssh-source.md](../references/asyncssh-source.md)。
