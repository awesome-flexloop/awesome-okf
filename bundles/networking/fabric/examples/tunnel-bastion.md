---
type: Example
title: 跳板机隧道
description: 通过 gateway 跳板机连接内网主机、本地/远程端口转发、SSH config 驱动的多跳代理
tags: [fabric, example, tunnel, gateway, bastion, proxyjump, port-forwarding]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: fabric-source
    resource: /references/fabric-source.md
---

# 跳板机隧道

## 场景

通过 SSH 跳板机（堡垒机）访问内网服务器，以及通过 SSH 隧道访问受限端口的服务（数据库、内部 API 等）。

## 方式一：Connection 作为网关（ProxyJump）

直接在代码中创建跳板机 Connection 作为网关：

```python
from fabric import Connection

bastion = Connection(
    "bastion.example.com",
    user="jumpuser",
    connect_kwargs={"key_filename": "/home/user/.ssh/bastion_key"},
)

db = Connection(
    "10.0.1.100",
    user="dbuser",
    gateway=bastion,
    connect_kwargs={"key_filename": "/home/user/.ssh/internal_key"},
)

with db:
    result = db.run("hostname")
    print(result.stdout.strip())
```

连接路径：`本地 → bastion.example.com → 10.0.1.100`

fabric 在 `db.open()` 时：
1. 先调用 `bastion.open()` 建立跳板连接
2. 在跳板 transport 上打开 `direct-tcpip` 通道到目标 `(10.0.1.100, 22)`
3. 将该通道作为 socket 建立到目标的 SSH 连接

## 方式二：ProxyCommand 字符串

使用命令字符串作为网关（类似 OpenSSH 的 ProxyCommand）：

```python
c = Connection(
    "internal-host",
    user="deploy",
    gateway="ssh -W %h:%p bastion.example.com",
)
c.run("hostname")
```

fabric 会创建 `paramiko.proxy.ProxyCommand` 对象，启动子进程并将其 stdin/stdout 作为网络 socket。

`%h` 和 `%p` 分别被替换为目标主机和端口。

## 方式三：SSH config 驱动

在 `~/.ssh/config` 中配置跳板：

```ssh-config
Host bastion
    HostName bastion.example.com
    User jumpuser
    IdentityFile ~/.ssh/bastion_key

Host 10.0.1.*
    User deploy
    IdentityFile ~/.ssh/internal_key
    ProxyJump bastion

Host db-*
    User dbuser
    ProxyJump bastion
```

然后代码中直接使用别名：

```python
from fabric import Connection

c = Connection("10.0.1.100")
c.run("hostname")

# 或使用别名
db = Connection("db-primary")
db.run("hostname")
```

fabric 自动读取 SSH config 中的 `ProxyJump` 指令，创建跳板 Connection 链。

## 多跳跳板

SSH config 支持多跳 ProxyJump：

```ssh-config
Host hop1
    HostName hop1.example.com

Host hop2
    HostName hop2.internal
    ProxyJump hop1

Host target
    HostName 10.0.0.50
    ProxyJump hop2
```

或单行：

```ssh-config
Host target
    ProxyJump hop1,hop2
```

fabric 解析逗号分隔的跳点列表时，从最内层开始反向创建 Connection 链。连接路径：`本地 → hop1 → hop2 → target`。

代码中也可以手动构建多跳链：

```python
hop1 = Connection("hop1.example.com", user="user1")
hop2 = Connection("hop2.internal", user="user2", gateway=hop1)
target = Connection("10.0.0.50", user="admin", gateway=hop2)

target.run("hostname")
```

## 本地端口转发（ssh -L）

通过已建立的 SSH 连接，将本地端口映射到远程可达的服务：

```python
from fabric import Connection

c = Connection("db-server.example.com", user="deploy")

with c.forward_local(5432):
    import psycopg2
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="production",
        user="dbuser",
    )
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    print(cursor.fetchone())
    conn.close()
```

### 转发到远程网络的其他主机

```python
from fabric import Connection

c = Connection("bastion.example.com")

# 本地 8080 -> bastion 可访问的 internal-web:80
with c.forward_local(8080, remote_port=80, remote_host="internal-web"):
    import requests
    r = requests.get("http://localhost:8080/api/health")
    print(r.json())
```

### 数据库隧道完整示例

```python
from fabric import Connection
import pymysql

def query_via_tunnel(host, db_query):
    c = Connection(host, user="deploy")

    with c.forward_local(3306, remote_host="db.internal"):
        conn = pymysql.connect(
            host="127.0.0.1",
            port=3306,
            user="readonly",
            password="dbpass",
            database="analytics",
        )
        cursor = conn.cursor()
        cursor.execute(db_query)
        rows = cursor.fetchall()
        conn.close()
        return rows

results = query_via_tunnel(
    "web.example.com",
    "SELECT id, name FROM users LIMIT 10",
)
for row in results:
    print(row)
```

## 远程端口转发（ssh -R）

将远程服务器上的端口映射回本地：

```python
from fabric import Connection

c = Connection("remote-server.example.com")

with c.forward_remote(9000, local_port=3000):
    print("隧道已建立：remote-server:9000 -> localhost:3000")
    input("按 Enter 关闭...")
```

适用于 Webhook 本地调试：远程服务的回调被转发到本地开发服务器。

### 持续运行远程转发

```python
from fabric import Connection
import time

c = Connection("prod.example.com")

with c.forward_remote(8080, local_port=8000, remote_host="0.0.0.0"):
    print("远程 0.0.0.0:8080 -> 本地 8000")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("关闭隧道")
```

`remote_host="0.0.0.0"` 使远程端口对所有网络接口可见（默认 `127.0.0.1` 仅本机）。

## 跳板机 + 端口转发组合

通过跳板机连接到内网数据库并建立本地隧道：

```python
from fabric import Connection

bastion = Connection("bastion.example.com", user="jumpuser")
db_server = Connection(
    "db.internal",
    user="dbuser",
    gateway=bastion,
)

with db_server.forward_local(5432):
    import psycopg2
    conn = psycopg2.connect(host="localhost", port=5432, dbname="mydb")
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM users;")
    print(f"用户数: {cursor.fetchone()[0]}")
    conn.close()
```

流量路径：`localhost:5432 → SSH(db.server) → bastion → db.internal:5432`

## 禁用已配置的网关

如果 SSH config 或 Config 中配置了网关，但需要直连，传入 `gateway=False`：

```python
# SSH config 中配置了 ProxyJump，但这里需要直连
c = Connection("host-with-gateway-config", gateway=False)
c.run("hostname")
```

## 典型企业网络场景

```python
from fabric import Connection, Config

config = Config(overrides={
    "connect_kwargs": {
        "key_filename": "/home/user/.ssh/company_key",
    },
})

bastion = Connection(
    "bastion.company.com",
    user="employee",
    config=config,
)

app_servers = [
    Connection("10.0.10.1", gateway=bastion, config=config),
    Connection("10.0.10.2", gateway=bastion, config=config),
    Connection("10.0.10.3", gateway=bastion, config=config),
]

for server in app_servers:
    with server:
        result = server.run("uptime", hide=True)
        print(f"{server.host}: {result.stdout.strip()}")
```

## 关键 API 说明

| API | 说明 |
|-----|------|
| `Connection(..., gateway=other_cxn)` | ProxyJump 模式 |
| `Connection(..., gateway="ssh -W %h:%p ...")` | ProxyCommand 模式 |
| `Connection(..., gateway=False)` | 禁用已配置的网关 |
| `c.forward_local(local_port, ...)` | 本地端口转发上下文管理器 |
| `c.forward_remote(remote_port, ...)` | 远程端口转发上下文管理器 |
| `c.open_gateway()` | 获取底层 socket/channel（内部方法） |

## 相关概念

- [Connection 详解](../concepts/02-connection.md) — gateway 参数详解
- [隧道与跳板机](../concepts/07-tunnels.md) — Tunnel/TunnelManager 实现机制
- [paramiko 端口转发](../../paramiko/concepts/08-port-forwarding.md) — 底层通道机制
