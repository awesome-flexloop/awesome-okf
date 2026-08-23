---
type: Concept
title: 异步连接详解
description: SSHClientConnection 全解析——connect() 参数、认证方式、主机密钥验证、连接生命周期
tags: [asyncssh, connection, ssh-client, api]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: asyncssh-source
    resource: /references/asyncssh-source.md
---

# 异步连接详解

## SSHClientConnection 的定位

`SSHClientConnection` 是 asyncssh 客户端的核心类，定义于 `connection.py:3415`，继承 `SSHConnection`（connection.py:867）。`SSHConnection` 同时继承 `SSHPacketHandler` 和 `asyncio.Protocol`，是整个 SSH 协议栈的状态机引擎。

`SSHClientConnection` 不通过构造函数直接创建，而是通过 `asyncssh.connect()` 协程建立连接并返回。连接建立后，可通过它打开会话、创建进程、启动 SFTP、设置端口转发。

## connect() 函数

`connect()` 是模块级协程，定义于 `connection.py:9180`：

```python
asyncssh.connect(
    host='', port=(), *,
    tunnel=(), family=(), flags=0,
    local_addr=(), sock=None,
    config=(), options=None,
    **kwargs
) -> SSHClientConnection
```

`**kwargs` 中的参数传递给 `SSHClientConnectionOptions`，常用参数包括：

### 认证参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `username` | `str` | 登录用户名 |
| `password` | `str` | 密码认证 |
| `client_keys` | list | 私钥文件路径或 SSHKey 对象列表 |
| `passphrase` | `str` | 私钥加密口令 |
| `known_hosts` | str/list/None | 已知主机密钥文件，None 禁用验证 |
| `agent_path` | str | SSH Agent 路径 |
| `agent_identities` | list | 仅允许使用的 Agent 身份列表 |
| `preferred_auth` | list | 首选认证方法顺序 |
| `gss_auth` | bool | 启用 GSSAPI 认证 |
| `gss_host` | str | GSSAPI 目标主机名 |
| `gss_delegate_creds` | bool | 委托 GSSAPI 凭据 |
| `client_host_keysign` | bool | 使用 ssh-keysign 进行主机认证 |

### 连接参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `tunnel` | SSHClientConnection/str | 通过已有连接隧道连接 |
| `family` | int | 地址族（AF_INET/AF_INET6/AF_UNSPEC） |
| `local_addr` | tuple | 绑定的本地地址和端口 |
| `sock` | socket | 已连接的 socket |
| `proxy_command` | str/list | ProxyCommand |
| `connect_timeout` | float | 连接超时秒数 |
| `login_timeout` | float | 登录超时秒数 |

### 算法参数

| 参数 | 说明 |
|------|------|
| `kex_algs` | 密钥交换算法列表 |
| `encryption_algs` | 加密算法列表 |
| `mac_algs` | MAC 算法列表 |
| `compression_algs` | 压缩算法列表 |
| `server_host_key_algs` | 允许的服务器主机密钥算法 |
| `signature_algs` | 签名算法列表 |

### 其他参数

| 参数 | 说明 |
|------|------|
| `term_type` | 默认终端类型 |
| `term_size` | 默认终端大小 (width, height, pixwidth, pixheight) |
| `term_modes` | 终端模式 |
| `encoding` | 默认编码（默认 UTF-8），None 表示 bytes 模式 |
| `env` | 发送的环境变量 |
| `send_env` | 从本地环境发送的变量名模式列表 |
| `keepalive_interval` | keepalive 间隔秒数 |
| `keepalive_count_max` | 最大未应答 keepalive 数 |
| `rekey_bytes` | 重密钥字节阈值 |

## 认证方式

### 密码认证

```python
conn = await asyncssh.connect('host', username='user', password='secret')
```

### 公钥认证

```python
conn = await asyncssh.connect('host', username='user',
                              client_keys=['~/.ssh/id_ed25519'])
```

可传入多个密钥：

```python
conn = await asyncssh.connect('host', username='user',
                              client_keys=['~/.ssh/id_rsa',
                                           '~/.ssh/id_ed25519'])
```

加载加密私钥：

```python
key = asyncssh.read_private_key('~/.ssh/id_rsa', passphrase='my passphrase')
conn = await asyncssh.connect('host', username='user', client_keys=[key])
```

### 键盘交互认证

可通过 `SSHClient` 回调类实现：

```python
class MySSHClient(asyncssh.SSHClient):
    async def kbdint_auth_requested(self):
        return ''

    async def kbdint_challenge_received(self, name, instructions,
                                        lang, prompts):
        return ['secret']

conn = await asyncssh.connect('host', username='user',
                              client_factory=MySSHClient)
```

### SSH Agent

asyncssh 默认连接 `SSH_AUTH_SOCK`（UNIX）或 Pageant（Windows）：

```python
conn = await asyncssh.connect('host', username='user')
```

指定 Agent 路径：

```python
conn = await asyncssh.connect('host', username='user',
                              agent_path='/path/to/agent.sock')
```

### GSSAPI/Kerberos

```python
conn = await asyncssh.connect('host', username='user',
                              gss_auth=True, gss_host='host.example.com')
```

### 多因子认证

按顺序尝试多种认证方法，通过 `preferred_auth` 控制顺序：

```python
conn = await asyncssh.connect(
    'host', username='user', password='secret',
    client_keys=['~/.ssh/id_ed25519'],
    preferred_auth=['publickey', 'password']
)
```

## 主机密钥验证

### 默认行为

默认加载 `~/.ssh/known_hosts`，验证服务器主机密钥。验证失败抛出 `HostKeyNotVerifiable`。

### 禁用验证

```python
conn = await asyncssh.connect('host', known_hosts=None)
```

### 指定 known_hosts 文件

```python
conn = await asyncssh.connect('host', known_hosts='/path/to/known_hosts')
```

### 获取服务器主机密钥

```python
key = await asyncssh.get_server_host_key('host')
print(key.get_fingerprint())
```

连接后也可获取：

```python
key = conn.get_server_host_key()
```

### 查询服务器支持的认证方法

```python
methods = await asyncssh.get_server_auth_methods('host')
print(methods)
```

## 连接生命周期

### 建立连接

```python
conn = await asyncssh.connect('host', username='user')
```

`connect()` 在认证成功后返回 `SSHClientConnection`。如果认证失败，抛出 `PermissionDenied`；连接失败抛出 `ConnectionLost` 或 `OSError`。

### 使用连接

```python
result = await conn.run('uname -a')
proc = await conn.create_process()
sftp = await conn.start_sftp_client()
listener = await conn.forward_local_port(...)
```

### 关闭连接

```python
conn.close()
await conn.wait_closed()
```

或使用异步上下文管理器自动关闭：

```python
async with asyncssh.connect('host') as conn:
    result = await conn.run('hostname')
```

### 连接状态

- `conn.is_closing()`：连接是否正在关闭
- `conn.get_extra_info('peername')`：获取对端地址
- `conn.get_server_host_key()`：获取服务器主机密钥
- `conn.get_server_auth_methods()`：获取服务器支持的认证方法

## 跳板机与隧道

### 通过已有连接隧道

```python
async with asyncssh.connect('bastion') as bastion:
    async with asyncssh.connect('internal', tunnel=bastion) as conn:
        result = await conn.run('hostname')
```

### 字符串格式跳板机

```python
conn = await asyncssh.connect('internal',
                              tunnel='user@bastion:22')
```

多跳逗号分隔：

```python
conn = await asyncssh.connect('internal',
                              tunnel='user@hop1,user@hop2')
```

### ProxyCommand

```python
conn = await asyncssh.connect('host',
                              proxy_command='ssh -W %h:%p bastion')
```

## SSHClient 回调

通过 `client_factory` 参数传入 `SSHClient` 子类，可接收连接事件回调：

```python
class MyClient(asyncssh.SSHClient):
    def connection_made(self, conn):
        print(f'已连接到 {conn.get_extra_info("peername")}')

    def connection_lost(self, exc):
        if exc:
            print(f'连接异常断开: {exc}')

    def auth_completed(self):
        print('认证成功')

    async def password_auth_requested(self):
        return 'secret'

    async def public_key_auth_requested(self):
        return asyncssh.read_private_key('~/.ssh/id_ed25519')

conn = await asyncssh.connect('host', client_factory=MyClient)
```

## 连接配置文件

asyncssh 支持加载 OpenSSH `ssh_config` 配置文件：

```python
conn = await asyncssh.connect('host', config='~/.ssh/config')
```

默认自动加载 `~/.ssh/config`。设为 `None` 禁用配置加载。

## 相关概念

- [5分钟快速上手](/concepts/01-getting-started.md)
- [通道与流](/concepts/03-channels.md)
- [认证体系](/concepts/05-authentication.md)
- [端口转发](/concepts/09-port-forwarding.md)
- [paramiko SSHClient 详解](../../paramiko/concepts/02-ssh-client.md)（同步模型对比）

[^asyncssh-source]: asyncssh 源码信源，见 [asyncssh-source.md](/references/asyncssh-source.md)。
