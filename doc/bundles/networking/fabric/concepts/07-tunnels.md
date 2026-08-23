---
type: Concept
title: 隧道与跳板机
description: forward_local/forward_remote 端口转发、Tunnel/TunnelManager 实现机制、ProxyJump/ProxyCommand 跳板机配置
tags: [fabric, tunnel, port-forwarding, gateway, bastion, proxyjump]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: fabric-source
    resource: /references/fabric-source.md
---

# 隧道与跳板机

## 概述

fabric 提供两类 SSH 隧道能力：

1. **端口转发**（`forward_local`/`forward_remote`）：通过已建立的 SSH 连接转发 TCP 流量
2. **跳板机/网关**（`gateway` 参数）：通过中间主机建立到目标主机的 SSH 连接

两者底层都使用 paramiko 的通道机制，但用途和实现不同。

## 本地端口转发（ssh -L）

`Connection.forward_local()` 将本地端口转发到远程服务器可达的地址：

```python
from fabric import Connection

c = Connection("db-server.example.com")

with c.forward_local(5432):
    import psycopg2
    db = psycopg2.connect(host="localhost", port=5432, database="mydb")
```

### 方法签名

```python
@contextmanager
@opens
def forward_local(
    local_port,
    remote_port=None,
    remote_host="localhost",
    local_host="localhost",
):
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `local_port` | 必填 | 本地监听端口 |
| `remote_port` | 同 local_port | 远程目标端口 |
| `remote_host` | `"localhost"` | 远程目标主机（从 SSH 服务器视角） |
| `local_host` | `"localhost"` | 本地监听地址 |

### 转发到远程主机的其他机器

```python
# 本地 8080 -> SSH 服务器能访问的 internal-host:80
with c.forward_local(8080, remote_port=80, remote_host="internal-host"):
    import requests
    r = requests.get("http://localhost:8080")
```

### 实现机制

`forward_local()` 内部创建 `TunnelManager` 线程：

1. 在本地创建非阻塞 TCP socket，绑定到 `(local_host, local_port)` 并 listen
2. 主循环接受入站连接（非阻塞 + 10ms 轮询）
3. 对每个入站连接，通过 `transport.open_channel("direct-tcpip", remote_address, local_addr)` 打开 SSH 通道
4. 创建 `Tunnel` 线程在 socket 和 channel 之间双向转发数据
5. 上下文退出时设置 `finished` Event，等待所有 Tunnel 关闭

## 远程端口转发（ssh -R）

`Connection.forward_remote()` 将远程服务器上的端口转发回本地可达的地址：

```python
from fabric import Connection

c = Connection("remote-server.example.com")

with c.forward_remote(8080):
    # 远程服务器上访问 127.0.0.1:8080 的流量
    # 会被转发到本地的 localhost:8080
    c.run("curl http://127.0.0.1:8080")
    input("按 Enter 关闭隧道...")
```

### 方法签名

```python
@contextmanager
@opens
def forward_remote(
    remote_port,
    local_port=None,
    remote_host="127.0.0.1",
    local_host="localhost",
):
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `remote_port` | 必填 | 远程 SSH 服务器上的监听端口 |
| `local_port` | 同 remote_port | 本地目标端口 |
| `remote_host` | `"127.0.0.1"` | 远程监听地址 |
| `local_host` | `"localhost"` | 本地目标主机 |

### 实现机制

与本地转发不同，远程转发利用 paramiko Transport 的端口转发机制：

1. 调用 `transport.request_port_forward(address=remote_host, port=remote_port, handler=callback)`
2. 当远程端口收到连接时，sshd 调用 callback，传入一个 channel
3. callback 创建到 `(local_host, local_port)` 的出站 socket 连接
4. 创建 `Tunnel` 线程在 channel 和 socket 之间双向转发
5. 上下文退出时 cancel_port_forward 并关闭所有 Tunnel

> **注意**：远程转发没有使用 TunnelManager，而是通过 Paramiko  transport 线程的回调机制直接管理 Tunnel 列表。

## Tunnel 和 TunnelManager

### Tunnel

`tunnels.Tunnel` 继承 `invoke.util.ExceptionHandlingThread`，在 SSH channel 和 TCP socket 之间双向转发数据：

```python
Tunnel(channel=channel, sock=sock, finished=Event())
```

核心逻辑（`_run()`）：
- 使用 `select.select([sock, channel], [], [], 1)` 等待双向数据
- 从可读端 recv 1024 字节，sendall 到另一端
- 任一端关闭（recv 返回空）则结束
- finally 中关闭 channel 和 socket

### TunnelManager

`tunnels.TunnelManager` 同样继承 `ExceptionHandlingThread`，管理本地转发的监听 socket：

```python
TunnelManager(
    local_host="localhost",
    local_port=5432,
    remote_host="localhost",
    remote_port=5432,
    transport=paramiko_transport,
    finished=Event(),
)
```

它负责：
- 创建监听 socket（设置 SO_REUSEADDR、非阻塞）
- 接受连接并创建 direct-tcpip 通道
- 为每个连接启动独立的 Tunnel 线程
- 退出时传播 finished 信号、等待所有 Tunnel 关闭、收集异常、关闭监听 socket

## 跳板机（Gateway）

### ProxyJump — Connection 作为网关

通过 `gateway` 参数传入另一个 `Connection` 对象，实现 SSH 跳板：

```python
from fabric import Connection

bastion = Connection("bastion.example.com", user="jumpuser")
db = Connection(
    "db.internal",
    user="dbuser",
    gateway=bastion,
)

db.run("hostname")
# 连接路径: 本地 -> bastion -> db.internal
```

`open_gateway()` 在 Connection 类型 gateway 上：
1. 调用 `gateway.open()` 确保跳板连接已建立
2. 在跳板 transport 上打开 `direct-tcpip` 通道：
   ```python
   gateway.transport.open_channel(
       kind="direct-tcpip",
       dest_addr=(self.host, int(self.port)),
       src_addr=("", 0),
   )
   ```
3. 返回的 Channel 作为 `sock` 参数传给目标连接的 `SSHClient.connect()`

### 多跳 ProxyJump

SSH config 中的 `ProxyJump hop1,hop2,hop3` 会被解析为嵌套的 Connection 链：

```python
def get_gateway(self):
    if "proxyjump" in self.ssh_config:
        hops = reversed(self.ssh_config["proxyjump"].split(","))
        prev_gw = None
        for hop in hops:
            kwargs = dict(config=self.config.clone())
            if prev_gw is not None:
                kwargs["gateway"] = prev_gw
            cxn = Connection(hop, **kwargs)
            prev_gw = cxn
        return prev_gw
```

配置 `ProxyJump hop1,hop2,target` 时，代码从最内层（target）开始反向创建 Connection：
1. 创建到 target 的 Connection（gateway=hop2 的 Connection）
2. 创建到 hop2 的 Connection（gateway=hop1 的 Connection）
3. 创建到 hop1 的 Connection（无网关）

最终连接建立顺序为：本地 → hop1 → hop2 → target。

代码中包含自代理检测：如果某个 hop 的 host 与目标 host 相同，返回 None 防止无限递归。

### ProxyCommand — 命令字符串网关

`gateway` 参数也接受字符串，作为 ProxyCommand：

```python
c = Connection(
    "target.example.com",
    gateway="ssh -W %h:%p bastion.example.com",
)
```

`open_gateway()` 对字符串 gateway：
1. 创建临时 `SSHConfig` 解析 `%h`/`%p` 等占位符
2. 返回 `paramiko.proxy.ProxyCommand` 对象
3. ProxyCommand 启动子进程，其 stdin/stdout 作为 socket

### SSH config 网关配置

除了在代码中设置，网关也可通过 SSH config 文件配置：

```ssh-config
# ~/.ssh/config
Host bastion
    HostName bastion.example.com
    User jumpuser

Host db-*
    ProxyJump bastion
    User dbuser

Host multi-hop
    ProxyJump hop1,hop2,hop3
```

Connection 初始化时自动查询这些指令，优先级：
1. 构造函数 `gateway` 参数（非 None）
2. SSH config 的 `proxyjump`（创建 Connection 链）
3. SSH config 的 `proxycommand`（返回字符串）
4. fabric Config 的 `gateway` 值
5. None（直连）

传入 `gateway=False` 可显式覆盖已配置的网关。

## 典型场景

### 场景一：通过跳板机访问数据库

```python
bastion = Connection("bastion.example.com")
db = Connection("db.internal", gateway=bastion)

with db.forward_local(5432):
    conn = psycopg2.connect(host="localhost", port=5432)
```

### 场景二：Webhook 本地调试（远程转发）

```python
c = Connection("prod-server")
with c.forward_remote(9000, local_port=3000):
    # 远程服务器的 127.0.0.1:9000 -> 本地 3000
    input("等待 webhook...")
```

### 场景三：SSH config 驱动的多环境

```python
# ~/.ssh/config 中已配置好所有主机和跳板
prod = Connection("prod-app-01")
staging = Connection("staging-app-01")
```

## 相关概念

- [Connection 详解](02-connection.md) — gateway 参数和 open_gateway 方法
- [paramiko 端口转发](../../paramiko/concepts/08-port-forwarding.md) — 底层 direct-tcpip 和 forward-tcpip 机制
