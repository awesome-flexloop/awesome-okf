---
type: Concept
title: 服务端开发
description: ServerInterface、SFTPServer、SFTPServerInterface、SubsystemHandler——构建自定义 SSH 服务端
tags: [paramiko, server, sftp-server]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: paramiko-source
    resource: /references/paramiko-source.md
---

# 服务端开发

## 服务端架构

paramiko 不仅能作为 SSH 客户端，也支持构建 SSH 服务端。服务端的核心是：

- `Transport.start_server(server=...)`：启动服务端模式
- `ServerInterface`：回调接口，控制认证、通道、转发授权
- `SubsystemHandler`：子系统处理器线程（如 SFTP）
- `SFTPServer` + `SFTPServerInterface`：SFTP 服务端实现
- `SFTPHandle`：SFTP 文件句柄

## ServerInterface

`ServerInterface` 是服务端的核心回调类，定义了客户端请求各类服务时被调用的方法。默认实现拒绝所有请求。

### 最小服务端

```python
import paramiko
import socket

class SimpleSSHServer(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if username == "admin" and password == "secret":
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_auth_publickey(self, username, key):
        return paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        return "password"

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(self, channel, term, width, height,
                                   pixelwidth, pixelheight, modes):
        return True

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("0.0.0.0", 2222))
sock.listen(100)

client, addr = sock.accept()
transport = paramiko.Transport(client)
transport.add_server_key(host_key)

server = SimpleSSHServer()
transport.start_server(server=server)

channel = transport.accept(20)
if channel is None:
    raise Exception("No channel")

server.event.wait(10)
channel.send(b"Welcome to the SSH server!\r\n")
```

### 认证回调

```python
def check_auth_none(self, username):
    return paramiko.AUTH_FAILED

def check_auth_password(self, username, password):
    if verify_password(username, password):
        return paramiko.AUTH_SUCCESSFUL
    return paramiko.AUTH_FAILED

def check_auth_publickey(self, username, key):
    if verify_key(username, key):
        return paramiko.AUTH_SUCCESSFUL
    return paramiko.AUTH_FAILED

def check_auth_interactive(self, username, submethods):
    return paramiko.AUTH_FAILED

def get_allowed_auths(self, username):
    return "publickey,password"
```

认证返回值：

| 常量 | 值 | 含义 |
|------|---|------|
| `AUTH_SUCCESSFUL` | 0 | 认证成功 |
| `AUTH_PARTIALLY_SUCCESSFUL` | 1 | 部分成功，需继续认证 |
| `AUTH_FAILED` | 2 | 认证失败 |

### 通道请求回调

```python
def check_channel_request(self, kind, chanid):
    if kind == "session":
        return paramiko.OPEN_SUCCEEDED
    return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

def check_channel_pty_request(self, channel, term, width, height,
                               pixelwidth, pixelheight, modes):
    return True

def check_channel_shell_request(self, channel):
    return True

def check_channel_exec_request(self, channel, command):
    threading.Thread(target=self.run_command, args=(channel, command)).start()
    return True

def check_channel_subsystem_request(self, channel, name):
    if name == "sftp":
        return True
    return False
```

通道请求返回值：

| 常量 | 值 |
|------|---|
| `OPEN_SUCCEEDED` | 0 |
| `OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED` | 1 |
| `OPEN_FAILED_CONNECT_FAILED` | 2 |
| `OPEN_FAILED_UNKNOWN_CHANNEL_TYPE` | 3 |
| `OPEN_FAILED_RESOURCE_SHORTAGE` | 4 |

### 其他回调

```python
def check_port_forward_request(self, address, port):
    return port if port == 8080 else None

def cancel_port_forward_request(self, address, port):
    pass

def check_global_request(self, kind, msg):
    return False

def check_channel_direct_tcpip_request(self, chanid, origin, destination):
    return paramiko.OPEN_SUCCEEDED

def check_channel_x11_request(self, channel, single_connection,
                               auth_protocol, auth_cookie, screen_number):
    return False

def check_channel_forward_agent_request(self, channel):
    return False

def check_channel_env_request(self, channel, name, value):
    return True if name.startswith("LC_") else False

def get_banner(self):
    return ("Authorized access only", "en")
```

### InteractiveQuery

keyboard-interactive 认证中返回交互式查询：

```python
def check_auth_interactive(self, username, submethods):
    query = paramiko.InteractiveQuery(
        name="SSH Login",
        instructions="Please enter your credentials",
    )
    query.add_prompt("Username: ", echo=True)
    query.add_prompt("Password: ", echo=False)
    return query

def check_auth_interactive_response(self, responses):
    username, password = responses
    if self.verify(username, password):
        return paramiko.AUTH_SUCCESSFUL
    return paramiko.AUTH_FAILED
```

## 添加服务器密钥

服务端必须至少有一个主机密钥：

```python
host_key = paramiko.RSAKey.from_private_key_file("/etc/ssh/ssh_host_rsa_key")
transport.add_server_key(host_key)

host_ed25519 = paramiko.Ed25519Key.from_private_key_file(
    "/etc/ssh/ssh_host_ed25519_key"
)
transport.add_server_key(host_ed25519)
```

可添加多个不同类型的密钥，协商时选择客户端支持的。

## SFTP 服务端

### SFTPServer

`SFTPServer` 是 SFTP 子系统的处理器，继承 `BaseSFTP` 和 `SubsystemHandler`。注册到 Transport：

```python
transport.set_subsystem_handler("sftp", paramiko.SFTPServer)
```

默认 SFTPServer 使用操作系统文件系统。如需自定义后端，需提供 `SFTPServerInterface` 子类。

### SFTPServerInterface

这是 SFTP 服务端的文件系统抽象接口，默认所有方法返回 `SFTP_OP_UNSUPPORTED`。

```python
class VirtualSFTPServer(paramiko.SFTPServerInterface):
    def __init__(self, server, *args, **kwargs):
        super().__init__(server, *args, **kwargs)
        self.files = {}

    def list_folder(self, path):
        try:
            entries = os.listdir(path)
            attrs = []
            for name in entries:
                full = os.path.join(path, name)
                attr = paramiko.SFTPAttributes.from_stat(
                    os.stat(full), name
                )
                attrs.append(attr)
            return attrs
        except OSError as e:
            return paramiko.SFTP_NO_SUCH_FILE

    def stat(self, path):
        try:
            return paramiko.SFTPAttributes.from_stat(os.stat(path))
        except OSError:
            return paramiko.SFTP_NO_SUCH_FILE

    def lstat(self, path):
        try:
            return paramiko.SFTPAttributes.from_stat(os.lstat(path))
        except OSError:
            return paramiko.SFTP_NO_SUCH_FILE

    def open(self, path, flags, attr):
        try:
            fd = os.open(path, flags, 0o644)
            handle = paramiko.SFTPHandle(flags)
            f = os.fdopen(fd, "rb+")
            handle.readfile = f
            handle.writefile = f
            return handle
        except OSError:
            return paramiko.SFTP_PERMISSION_DENIED

    def remove(self, path):
        try:
            os.remove(path)
            return paramiko.SFTP_OK
        except OSError:
            return paramiko.SFTP_NO_SUCH_FILE

    def rename(self, oldpath, newpath):
        try:
            os.rename(oldpath, newpath)
            return paramiko.SFTP_OK
        except OSError:
            return paramiko.SFTP_FAILURE

    def mkdir(self, path, attr):
        try:
            os.mkdir(path, attr.st_mode or 0o755)
            return paramiko.SFTP_OK
        except OSError:
            return paramiko.SFTP_FAILURE

    def rmdir(self, path):
        try:
            os.rmdir(path)
            return paramiko.SFTP_OK
        except OSError:
            return paramiko.SFTP_NO_SUCH_FILE

    def chattr(self, path, attr):
        try:
            if attr.st_mode is not None:
                os.chmod(path, attr.st_mode)
            if attr.st_uid is not None:
                os.chown(path, attr.st_uid, attr.st_gid)
            return paramiko.SFTP_OK
        except OSError:
            return paramiko.SFTP_PERMISSION_DENIED
```

### 注册自定义 SFTP 服务端

```python
transport.set_subsystem_handler(
    "sftp",
    paramiko.SFTPServer,
    VirtualSFTPServer,
)
```

`set_subsystem_handler(name, handler, *args, **kwargs)` 的额外参数传递给 handler 的构造函数。SFTPServer 的第三个参数是 `sftp_si`，即 SFTPServerInterface 子类。

### SFTPHandle

`SFTPHandle` 是服务端文件句柄抽象：

```python
class MySFTPHandle(paramiko.SFTPHandle):
    def chattr(self, attr):
        return paramiko.SFTP_OP_UNSUPPORTED

    def stat(self):
        try:
            return paramiko.SFTPAttributes.from_stat(os.fstat(self.readfile.fileno()))
        except OSError:
            return paramiko.SFTP_FAILURE
```

默认实现检查 `self.readfile` 和 `self.writefile` 属性并调用其 close()。子类覆盖 read(offset, length) 和 write(offset, data) 实现自定义存储。

## SubsystemHandler

`SubsystemHandler` 继承 `threading.Thread`，是子系统处理器的基类：

```python
class MySubsystemHandler(paramiko.SubsystemHandler):
    def __init__(self, channel, name, server):
        super().__init__(channel, name, server)

    def start_subsystem(self, name, transport, channel):
        while True:
            data = channel.recv(4096)
            if not data:
                break
            channel.send(data)

    def finish_subsystem(self):
        pass
```

## 会话生命周期

服务端处理连接的典型流程：

1. 接受 TCP 连接
2. 创建 Transport，添加服务器密钥
3. 调用 `start_server(server=server_interface)`
4. 循环 `accept(timeout)` 接受通道
5. 根据通道请求类型处理（exec/shell/subsystem）
6. 通道关闭后继续 accept 或退出

## 服务端最佳实践

1. **线程模型**：每个连接的 Transport 运行在独立线程，每个 Channel 也在线程中处理。使用线程池或异步框架时需注意线程安全。
2. **资源限制**：重写 `check_channel_request` 限制并发通道数，防止资源耗尽。
3. **认证安全**：不要在日志中记录密码；使用常量时间比较密钥。
4. **超时设置**：为 accept 和通道操作设置超时，防止慢速攻击。
5. **Banner**：通过 `get_banner()` 返回法律声明或欢迎信息。
6. **清理**：重写 `session_ended()` 清理 SFTP 资源。

## 相关概念

- [Transport 底层传输](03-transport.md)
- [Channel 通道](04-channel.md)
- [SFTP 文件传输](07-sftp.md)
- [认证体系](05-authentication.md)
- [高级模式](10-advanced-patterns.md)

[^paramiko-source]: paramiko 源码信源，见 [paramiko-source.md](../references/paramiko-source.md)。
