---
type: Example
title: 端口转发隧道
description: 本地/远程端口转发、SOCKS 代理、UNIX socket 转发、动态端口、访问控制
tags: [asyncssh, example, port-forwarding, tunnel, socks, proxy]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: asyncssh-source
    resource: /references/asyncssh-source.md
---

# 端口转发隧道

## 本地端口转发

将本地端口转发到远程服务器可达的目标：

```python
import asyncio
import asyncssh

async def main():
    async with asyncssh.connect('bastion.example.com',
                                username='user',
                                known_hosts=None) as conn:
        listener = await conn.forward_local_port(
            'localhost', 8080,
            'internal-db.example.com', 5432
        )
        print(f'转发: localhost:{listener.get_port()} '
              f'-> internal-db.example.com:5432')
        print('按 Ctrl+C 停止')

        await listener.wait_closed()

asyncio.run(main())
```

本地访问 `localhost:8080` 即通过堡垒机连接到内网数据库 `internal-db:5432`。

## 动态本地端口（自动分配）

```python
listener = await conn.forward_local_port(
    'localhost', 0,  # 0 = 系统自动分配
    'remote-host', 80
)
print(f'动态端口: {listener.get_port()}')
```

## 远程端口转发

将远程服务器的端口转发回客户端可达的目标：

```python
import asyncio
import asyncssh

async def main():
    async with asyncssh.connect('public-server.example.com',
                                username='user',
                                known_hosts=None) as conn:
        listener = await conn.forward_remote_port(
            '', 8080,
            'localhost', 3000
        )
        print('远程转发: public-server:8080 -> localhost:3000')
        await listener.wait_closed()

asyncio.run(main())
```

外部访问 `public-server:8080` 的流量通过 SSH 隧道转发到本地运行在 3000 端口的服务。

## SOCKS 代理

创建 SOCKS4/SOCKS5 代理，通过 SSH 服务器访问任意目标：

```python
import asyncio
import asyncssh

async def main():
    async with asyncssh.connect('proxy.example.com',
                                known_hosts=None) as conn:
        listener = await conn.forward_socks('localhost', 1080)
        print(f'SOCKS 代理监听在 localhost:{listener.get_port()}')
        await listener.wait_closed()

asyncio.run(main())
```

配置应用使用此代理：

```bash
# HTTP
curl --socks5 localhost:1080 http://internal.example.com

# 全局代理（部分应用）
export ALL_PROXY=socks5://localhost:1080
```

## 访问控制

使用 `accept_handler` 控制哪些连接允许通过隧道：

```python
import asyncio
import asyncssh

ALLOWED_CLIENTS = {'192.168.1.0/24'}

async def accept_connection(orig_host, orig_port):
    import ipaddress
    try:
        addr = ipaddress.ip_address(orig_host)
        for network in ALLOWED_CLIENTS:
            if addr in ipaddress.ip_network(network):
                return True
    except ValueError:
        pass
    print(f'拒绝连接来自 {orig_host}:{orig_port}')
    return False

async def main():
    async with asyncssh.connect('bastion', known_hosts=None) as conn:
        listener = await conn.forward_local_port(
            '0.0.0.0', 8080,
            'internal', 80,
            accept_handler=accept_connection
        )
        await listener.wait_closed()

asyncio.run(main())
```

## UNIX Socket 转发

### 本地 TCP 到远程 UNIX Socket

```python
listener = await conn.forward_local_port_to_path(
    'localhost', 5432,
    '/var/run/postgresql/.s.PGSQL.5432'
)
```

### 本地 UNIX Socket 到远程 TCP

```python
listener = await conn.forward_local_path_to_port(
    '/tmp/docker.sock',
    'remote-docker', 2375
)
```

### 远程 TCP 到本地 UNIX Socket

```python
listener = await conn.forward_remote_port_to_path(
    '', 8080,
    '/var/run/local-service.sock'
)
```

### 远程 UNIX Socket 到本地 TCP

```python
listener = await conn.forward_remote_path_to_port(
    '/tmp/remote.sock',
    'localhost', 8080
)
```

## 一次性 Direct-TCPIP 连接

不使用监听器，直接打开单次转发连接：

```python
import asyncio
import asyncssh

async def main():
    async with asyncssh.connect('bastion', known_hosts=None) as conn:
        reader, writer, chan = await conn.open_connection(
            'internal-redis.example.com', 6379
        )

        writer.write(b'PING\r\n')
        response = await reader.readline()
        print(response)

        writer.close()
        await writer.wait_closed()

asyncio.run(main())
```

## 多目标转发

一个 SSH 连接上可同时设置多个转发：

```python
import asyncio
import asyncssh

async def main():
    async with asyncssh.connect('bastion', known_hosts=None) as conn:
        l1 = await conn.forward_local_port(
            'localhost', 8080, 'web.internal', 80)
        l2 = await conn.forward_local_port(
            'localhost', 8443, 'web.internal', 443)
        l3 = await conn.forward_local_port(
            'localhost', 5432, 'db.internal', 5432)

        socks = await conn.forward_socks('localhost', 1080)

        print('转发已建立:')
        print(f'  localhost:{l1.get_port()} -> web.internal:80')
        print(f'  localhost:{l2.get_port()} -> web.internal:443')
        print(f'  localhost:{l3.get_port()} -> db.internal:5432')
        print(f'  SOCKS localhost:{socks.get_port()}')

        await asyncio.Event().wait()

asyncio.run(main())
```

## 异步上下文管理器

```python
async with conn.forward_local_port(
    'localhost', 8080, 'remote', 80
) as listener:
    # 在此期间转发生效
    await do_work()
# 退出后自动关闭转发
```

## 完整数据库隧道示例

```python
import asyncio
import asyncssh
import asyncpg

async def query_via_tunnel():
    async with asyncssh.connect(
        'bastion.example.com',
        username='dbuser',
        client_keys=['~/.ssh/id_ed25519'],
        known_hosts='~/.ssh/known_hosts'
    ) as conn:
        listener = await conn.forward_local_port(
            'localhost', 0,
            'db-master.internal', 5432
        )
        local_port = listener.get_port()
        print(f'隧道: localhost:{local_port} -> db-master:5432')

        conn_pg = await asyncpg.connect(
            host='localhost',
            port=local_port,
            user='dbuser',
            password='dbpass',
            database='production'
        )

        rows = await conn_pg.fetch('SELECT version()')
        print(rows[0]['version'])

        await conn_pg.close()
        listener.close()
        await listener.wait_closed()

asyncio.run(query_via_tunnel())
```

## 相关概念

- [端口转发](../concepts/09-port-forwarding.md) —— 转发 API 详解
- [异步连接详解](../concepts/02-async-connection.md) —— 建立连接
- [通道与流](../concepts/03-channels.md) —— direct-tcpip 通道
- [paramiko 端口转发](../../paramiko/examples/port-forwarding.md)（同步转发对比）

[^asyncssh-source]: asyncssh 源码信源，见 [asyncssh-source.md](../references/asyncssh-source.md)。
