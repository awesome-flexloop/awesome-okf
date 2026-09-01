---
type: Concept
title: Connection 详解
description: Connection 类全解析——构造参数、open/close 生命周期、SSH config 集成、gateway 跳板机、命令与文件操作
tags: [fabric, connection, api, ssh]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: fabric-source
    resource: /references/fabric-source.md
---

# Connection 详解

## 定位与架构

`Connection` 是 fabric 的核心类。它同时使用了继承和组合：

- **继承** `invoke.Context`：获得配置系统、`_run()`/`_sudo()` 模板方法、Watcher 支持等能力
- **组合** `paramiko.SSHClient`：内部持有 SSH 客户端实例处理协议细节

Connection 将父类的 `run()` 重绑定为 `local()`（本地执行），新增的 `run()` 用于远程 SSH 执行。

```python
from fabric import Connection

c = Connection("web.example.com", user="deploy")
```

## 构造函数

```python
Connection(
    host,
    user=None,
    port=None,
    config=None,
    gateway=None,
    forward_agent=None,
    connect_timeout=None,
    connect_kwargs=None,
    inline_ssh_env=None,
    remainder=None,
)
```

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `host` | str | 必填 | 目标主机名或 IP，支持 `user@host:port` 简写 |
| `user` | str | config.user | SSH 登录用户名 |
| `port` | int | config.port (22) | SSH 端口 |
| `config` | Config | 匿名 Config | 配置对象 |
| `gateway` | Connection/str/None | None | 跳板机：Connection 对象（ProxyJump）或命令字符串（ProxyCommand） |
| `forward_agent` | bool | config.forward_agent | 是否启用 SSH agent 转发 |
| `connect_timeout` | int | config.timeouts.connect | 连接超时（秒） |
| `connect_kwargs` | dict | config.connect_kwargs | 传递给 `paramiko.SSHClient.connect()` 的关键字参数 |
| `inline_ssh_env` | bool | config.inline_ssh_env (True) | 是否以 `export K=V &&` 前缀方式传递环境变量 |
| `remainder` | str | None | CLI 残余文本，透传给任务 |

### connect_kwargs

`connect_kwargs` 是透传给 paramiko 的通道，常用的键包括：

- `key_filename`：私钥文件路径（字符串或列表）
- `password`：SSH 密码
- `passphrase`：私钥密码短语
- `pkey`：已加载的 PKey 对象
- `allow_agent`：是否允许使用 SSH agent（默认 True）
- `look_for_keys`：是否在 `~/.ssh/` 中查找密钥（默认 True）
- `timeout`：连接超时（与 connect_timeout 不能同时设置）

```python
c = Connection(
    "db.example.com",
    user="admin",
    connect_kwargs={
        "key_filename": "/home/user/.ssh/id_ed25519",
        "password": "key-passphrase",
    },
    connect_timeout=10,
)
```

### 简写解析

`host` 参数支持三种简写形式：

```
user@host:port
user@host
host:port
```

解析规则：
- 按最后一个 `@` 分割 user 和 host:port
- IPv4 地址按最后一个 `:` 分割 port
- IPv6 地址（含多个 `:`）不解析 port，需显式使用 `port=` 参数
- 同时通过简写和关键字参数给出 user/port 会抛出 `ValueError`

模块级函数 `derive_shorthand(host_string)` 实现了解析逻辑，也可通过 `Connection.derive_shorthand()` 实例方法调用。

## SSH config 集成

Connection 在初始化时自动查询 `Config.base_ssh_config`（一个 `paramiko.config.SSHConfig` 对象）：

```python
self.ssh_config = self.config.base_ssh_config.lookup(host)
```

SSH config 指令影响以下属性：

| SSH config 指令 | 影响 |
|-----------------|------|
| `Hostname` | 覆盖 `self.host`，原始值保存在 `self.original_host` |
| `User` | 作为 user 的默认值（低于显式参数） |
| `Port` | 作为 port 的默认值 |
| `ProxyJump` | 构建网关 Connection 链 |
| `ProxyCommand` | 设置网关为命令字符串 |
| `ForwardAgent` | 覆盖 forward_agent（yes/no） |
| `ConnectTimeout` | 覆盖 connect_timeout |
| `IdentityFile` | 合并到 connect_kwargs.key_filename |

配置优先级（从低到高）：
1. SSH config 文件值
2. fabric Config 值
3. Connection 构造函数显式参数

## 生命周期

### 懒连接

Connection 构造函数**不发起网络连接**，仅记录参数并创建 `SSHClient` 对象。实际连接在首次调用 `open()` 时建立。

`@opens` 装饰器修饰的方法（`run`、`sudo`、`shell`、`create_session`、`sftp`、`forward_local`、`forward_remote`）会在执行前自动调用 `open()`。

### 显式打开与关闭

```python
c = Connection("web.example.com")
c.open()
c.run("hostname")
c.close()
```

### 上下文管理器

```python
with Connection("web.example.com") as c:
    c.run("hostname")
```

`__exit__` 自动调用 `close()`，关闭 SFTP 会话和 SSH 连接。

### is_connected 属性

```python
if c.is_connected:
    print("连接已建立")
```

返回 `self.transport.active if self.transport else False`。

### open() 细节

`open()` 方法执行以下步骤：
1. 若 `is_connected` 为 True，短路返回
2. 检查参数冲突：`hostname`/`port`/`username` 不能出现在 connect_kwargs 中；`timeout` 不能与 connect_timeout 同时设置
3. 合并参数：username、hostname、port 从 Connection 属性取
4. 若配置了 gateway，调用 `open_gateway()` 获取 socket
5. 若配置了认证策略类，创建 auth_strategy 并移除冲突的 connect_kwargs
6. 调用 `self.client.connect(**kwargs)`
7. 保存 `self.transport = self.client.get_transport()`

### open_gateway()

返回 socket-like 对象：

- **gateway 为字符串**：创建 `paramiko.proxy.ProxyCommand`（支持 `%h`/`%p` 等占位符）
- **gateway 为 Connection**：调用网关连接的 `transport.open_channel(kind="direct-tcpip", dest_addr=(host, port), src_addr=("", 0))`

### close() 细节

- 若 SFTP 会话已打开，关闭并置为 None
- 若连接活跃，调用 `client.close()`
- 若启用了 agent 转发且 `_agent_handler` 存在，关闭它

## 命令执行

### run() — 远程执行

```python
result = c.run("uname -a")
result = c.run("ls -la", hide=True)
result = c.run("false", warn=True)
```

`run()` 被 `@opens` 装饰，自动确保连接已打开。它创建 `Remote` runner 并调用继承自 invoke.Context 的 `_run()` 方法。

### sudo() — 提权执行

```python
c.sudo("systemctl restart nginx")
c.sudo("apt-get update", password="custom-password")
```

与 `run()` 类似，但通过 sudo 执行。支持 per-host sudo 密码配置。

### local() — 本地执行

```python
c.local("ls -la")
```

直接调用 `super().run()`（即 `invoke.Context.run()`），在本地系统执行命令。不经过 SSH。

### shell() — 交互式 Shell

```python
result = c.shell()
```

使用 `RemoteShell` runner 调用 `invoke_shell()`，分配 PTY。仅接受 `encoding`、`env`、`in_stream`、`replace_env`、`watchers` 五个 kwargs。适用于网络设备等非 POSIX 环境。

## 文件传输

### get() — 下载

```python
c.get("/var/log/syslog", "/tmp/syslog")
c.get("/var/log/syslog")
```

委托给 `Transfer(self).get()`。

### put() — 上传

```python
c.put("app.tar.gz", "/tmp/app.tar.gz")
c.put("app.tar.gz")
```

委托给 `Transfer(self).put()`。

详见 [文件传输](06-file-transfer.md)。

## 端口转发

### forward_local() — 本地转发（ssh -L）

```python
with c.forward_local(5432):
    import psycopg2
    db = psycopg2.connect(host="localhost", port=5432)
```

### forward_remote() — 远程转发（ssh -R）

```python
with c.forward_remote(8080):
    c.run("my-daemon --port 8080")
```

详见 [隧道与跳板机](07-tunnels.md)。

## SFTP 客户端

直接获取底层 `paramiko.SFTPClient`：

```python
sftp = c.sftp()
sftp.mkdir("/tmp/newdir")
files = sftp.listdir("/tmp")
```

`sftp()` 方法 memoize 结果，同一 Connection 实例只创建一个 SFTP 客户端。

## 其他特性

### 相等性与哈希

Connection 的相等性基于 `(host, user, port)` 三元组，不考虑 gateway/密钥等：

```python
c1 = Connection("host", user="u", port=22)
c2 = Connection("host", user="u", port=22)
assert c1 == c2
```

### __repr__

```python
repr(c)
# "<Connection host='web.example.com' user=deploy gw=proxyjump>"
```

仅显示 host，以及与默认值不同的 user/port/gateway。

### from_v1() 迁移构造器

```python
c = Connection.from_v1(env)
```

从 Fabric 1.x 的 `env` 字典构造 Connection，映射 host_string、user、port、key_filename 等。

## 相关概念

- [配置体系](03-configuration.md)
- [命令执行](04-command-execution.md)
- [隧道与跳板机](07-tunnels.md)
- [paramiko SSHClient](../../paramiko/concepts/02-ssh-client.md)
- [pyinvoke Context 对象](../../../../build/tooling/pyinvoke/index.md)
