---
type: Concept
title: 服务端开发
description: SSHServer 回调、create_server/listen 启动服务端、自定义认证、会话处理器、SFTPServer VFS、进程工厂
tags: [asyncssh, server, sshserver, sftpserver, vfs]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: asyncssh-source
    resource: /references/asyncssh-source.md
---

# 服务端开发

## 创建 SSH 服务端

使用 `asyncssh.create_server()`（connection.py:9691）或 `listen()`（connection.py:9400）启动 SSH 服务端：

```python
import asyncio
import asyncssh

class MySSHServer(asyncssh.SSHServer):
    def connection_made(self, conn):
        self.conn = conn

    def connection_lost(self, exc):
        if exc:
            print(f'连接异常: {exc}')

async def start_server():
    await asyncssh.create_server(
        MySSHServer, '', 8022,
        server_host_keys=['/etc/ssh/ssh_host_ed25519_key']
    )

asyncio.run(start_server())
```

`create_server()` 是 `listen()` 的包装，签名为：

```python
async def create_server(server_factory, host='', port=(), **kwargs) -> SSHAcceptor
```

`SSHAcceptor`（connection.py:759）包装 `asyncio.AbstractServer`，支持 `close()`、`wait_closed()`、`get_port()`、`update()` 和异步上下文管理器。

## SSHServer 回调

`SSHServer`（server.py:66）定义了一系列可重写的回调方法：

### 连接生命周期

| 方法 | 说明 |
|------|------|
| `connection_made(conn)` | 新连接建立 |
| `connection_lost(exc)` | 连接断开 |
| `debug_msg_received(msg, lang, always_display)` | 收到调试消息 |

### 认证

| 方法 | 返回值 | 说明 |
|------|--------|------|
| `begin_auth(username)` | `bool` | 返回 False 表示免认证 |
| `auth_completed()` | None | 认证成功 |
| `password_auth_supported()` | `bool` | 是否支持密码认证 |
| `validate_password(username, password)` | `bool` | 验证密码 |
| `public_key_auth_supported()` | `bool` | 是否支持公钥认证 |
| `validate_public_key(username, key)` | `bool` | 验证公钥 |
| `kbdint_auth_supported()` | `bool` | 是否支持键盘交互 |
| `get_kbdint_auth_methods(username, lang)` | list | 返回键盘交互子方法 |
| `begin_kbdint_auth(username, lang, submethods)` | list | 返回提示列表 |
| `perform_kbdint_auth(username, responses)` | `bool` | 验证键盘交互响应 |
| `validate_gss_principal(username, user_principal, host_principal)` | `bool` | 验证 GSSAPI 主体 |
| `host_based_auth_supported()` | `bool` | 是否支持 hostbased |
| `validate_host_based_request(username, key, hostname, host_username, client_addr)` | `bool` | 验证 hostbased |

### 通道与转发

| 方法 | 说明 |
|------|------|
| `session_requested()` | 客户端请求会话通道，返回 session 处理器或 True |
| `connection_requested(dest_host, dest_port, orig_host, orig_port)` | 客户端请求 direct-tcpip |
| `server_requested(listen_host, listen_port)` | 客户端请求 tcpip-forward（远程转发） |
| `unix_connection_requested(path)` | 客户端请求 direct-streamlocal |
| `unix_server_requested(path)` | 客户端请求 streamlocal-forward |

所有认证回调均可定义为协程（`async def`）。

## 会话处理器

客户端请求 exec/shell/subsystem 时，通过 `session_requested()` 返回会话处理器。asyncssh 提供多层会话抽象：

### SSHServerSession

直接使用 `SSHServerSession`（stream.py:694）：

```python
class MySession(asyncssh.SSHServerSession):
    def connection_made(self, chan):
        self.chan = chan

    def data_received(self, data, datatype):
        self.chan.write(data)  # Echo

    def eof_received(self):
        self.chan.write_eof()

class MyServer(asyncssh.SSHServer):
    def session_requested(self):
        return MySession()
```

### SSHServerProcess（推荐）

使用进程工厂创建 `SSHServerProcess`，自动管理 stdin/stdout/stderr 流：

```python
async def handle_client(process: asyncssh.SSHServerProcess):
    command = process.command
    if command:
        process.stdout.write(f'执行: {command}\n')
        result = await run_command(command)
        process.stdout.write(result.stdout)
        process.exit(result.returncode)
    else:
        process.stdout.write('Welcome\n')
        async for line in process.stdin:
            process.stdout.write(line)
        process.exit(0)

class MyServer(asyncssh.SSHServer):
    def session_requested(self):
        return handle_client
```

`SSHServerProcess` 提供：

| 属性/方法 | 说明 |
|-----------|------|
| `process.command` | 客户端请求的命令（None 表示 shell） |
| `process.subsystem` | 请求的子系统（如 'sftp'） |
| `process.env` | 环境变量映射 |
| `process.stdin` | `SSHReader` |
| `process.stdout` | `SSHWriter` |
| `process.stderr` | `SSHWriter` |
| `process.term_type` | 终端类型（None 表示无 PTY） |
| `process.term_size` | 终端尺寸 `(width, height, pixw, pixh)` |
| `process.exit(status)` | 设置退出码 |
| `process.exit_with_signal(signal, ...)` | 信号退出 |
| `process.redirect(...)` | IO 重定向 |
| `process.wait()` | 等待进程结束 |

### 终端尺寸变化

```python
async def handle_client(process):
    async for event in process:
        if isinstance(event, asyncssh.TerminalSizeChanged):
            w, h, pw, ph = event.size
            process.stdout.write(f'窗口: {w}x{h}\n')
```

或重写 `terminal_size_changed()` 回调。

## 内置 SFTP 服务端

asyncssh 内置完整的 SFTP 服务端实现：

```python
await asyncssh.create_server(
    MySSHServer, '', 22,
    server_host_keys=['host_key'],
    sftp_factory=asyncssh.SFTPServer
)
```

默认以服务进程的文件系统权限访问本地文件系统。

### 自定义 VFS

子类化 `SFTPServerFS`（sftp.py:8153）实现虚拟文件系统：

```python
class MyFS(asyncssh.SFTPServerFS):
    def __init__(self, conn):
        super().__init__(conn)
        self.files = {}

    async def stat(self, path):
        if path in self.files:
            return asyncssh.SFTPAttrs(size=len(self.files[path]))
        raise SFTPNoSuchFile

    async def open(self, path, mode, attrs):
        return MyFile(self, path, mode)

    async def scandir(self, path):
        for name in self.files:
            yield asyncssh.SFTPName(name, asyncssh.SFTPAttrs())

class MySFTPServer(asyncssh.SFTPServer):
    def __init__(self, chan):
        root = '/var/sftp-root'
        super().__init__(chan, [MyFS(chan, root)])

await asyncssh.create_server(
    MyServer, '', 22,
    sftp_factory=MySFTPServer
)
```

## SCP 服务端

设置 `allow_scp=True` 并提供 `sftp_factory`，asyncssh 自动处理 SCP 协议：

```python
await asyncssh.create_server(
    MyServer, '', 22,
    server_host_keys=['host_key'],
    sftp_factory=asyncssh.SFTPServer,
    allow_scp=True
)
```

`run_scp_server()`（scp.py:1129）由 `SSHServerStreamSession`（stream.py:766）在检测到 `scp ` 命令时内部调用，基于 SFTPServer VFS 实现。

## 服务端连接选项

`SSHServerConnectionOptions`（connection.py:8478）管理服务端配置，常用参数：

| 参数 | 说明 |
|------|------|
| `server_host_keys` | 主机密钥列表 |
| `server_host_key_algs` | 允许的主机密钥算法 |
| `kex_algs` | 密钥交换算法 |
| `encryption_algs` | 加密算法 |
| `mac_algs` | MAC 算法 |
| `compression_algs` | 压缩算法 |
| `login_timeout` | 认证超时 |
| `keepalive_interval` | keepalive 间隔 |
| `keepalive_count_max` | 最大未应答 keepalive 数 |
| `rekey_bytes` | 重密钥字节阈值 |
| `rekey_seconds` | 重密钥时间阈值 |
| `preferred_auth` | 首选认证方法顺序 |
| `x11_forwarding` | 是否允许 X11 转发 |
| `agent_forwarding` | 是否允许 Agent 转发 |
| `sftp_factory` | SFTP 子系统工厂 |
| `allow_scp` | 是否允许 SCP |

## 生成服务端主机密钥

```python
key = asyncssh.generate_private_key('ssh-ed25519')
key.write_private_key('ssh_host_ed25519_key')
key.write_public_key('ssh_host_ed25519_key.pub')
```

## 服务端认证完整示例

```python
import asyncssh

authorized_keys = asyncssh.read_authorized_keys(
    '~/.ssh/authorized_keys'
)

class MySSHServer(asyncssh.SSHServer):
    def connection_made(self, conn):
        self.conn = conn

    def begin_auth(self, username):
        return username != 'anonymous'

    def public_key_auth_supported(self):
        return True

    def validate_public_key(self, username, key):
        return authorized_keys.validate(key)

    def password_auth_supported(self):
        return True

    def validate_password(self, username, password):
        return verify_user(username, password)

async def handle_process(process):
    if process.command:
        proc = await asyncio.create_subprocess_shell(
            process.command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        process.stdout.write(stdout)
        process.stderr.write(stderr)
        process.exit(proc.returncode)
    else:
        process.stdout.write('No shell available\n')
        process.exit(1)

await asyncssh.create_server(
    MySSHServer, '', 22,
    server_host_keys=['ssh_host_ed25519_key'],
    process_factory=handle_process,
    sftp_factory=asyncssh.SFTPServer
)
```

## 相关概念

- [认证体系](05-authentication.md) —— 服务端认证回调详解
- [密钥与证书](06-keys-certificates.md) —— 主机密钥生成与证书
- [SFTP 文件传输](07-sftp.md) —— SFTPServer VFS
- [端口转发](09-port-forwarding.md) —— 转发权限控制
- [paramiko 服务端开发](../../paramiko/concepts/09-server.md)（同步服务端对比）

[^asyncssh-source]: asyncssh 源码信源，见 [asyncssh-source.md](../references/asyncssh-source.md)。
