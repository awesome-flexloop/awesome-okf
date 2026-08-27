---
type: Concept
title: Transport 底层传输
description: Transport 核心协议引擎详解——start_client、密钥交换、加密协商、认证、通道管理
tags: [paramiko, transport, protocol, core]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: paramiko-source
    resource: /references/paramiko-source.md
---

# Transport 底层传输

## Transport 的角色

`Transport` 是 paramiko 的核心协议引擎，继承自 `threading.Thread` 和 `ClosingContextManager`。它附着在一个 socket（或类 socket 对象）上，负责：

- SSH 版本协商和 banner 交换
- 密钥交换（KEX）
- 加密、MAC、压缩算法协商
- 用户认证
- 通道多路复用
- 全局请求处理（端口转发等）
- 重密钥（rekey）

一个 Transport 对应一个 SSH 连接，多个 Channel 可在其上多路复用。

## 创建 Transport

```python
import paramiko
import socket

sock = socket.create_connection(("example.com", 22))
transport = paramiko.Transport(sock)
transport.connect(username="myuser", password="mypassword")
```

Transport 构造函数签名：

```python
Transport(
    sock,
    default_window_size=2097152,
    default_max_packet_size=32768,
    disabled_algorithms=None,
    server_sig_algs=True,
    strict_kex=True,
    packetizer_class=None,
)
```

`sock` 可以是：
- 已连接的 `socket.socket` 对象
- 实现了 send/recv/close/settimeout 的类 socket 对象（如 `ProxyCommand`、`Channel`）
- `"host:port"` 字符串（自动创建 socket 连接）
- `(host, port)` 元组（自动创建 socket 连接）

## 启动会话

### 客户端模式

```python
transport.start_client(timeout=30)
```

执行 SSH 握手：发送/接收 banner、KEXINIT、密钥交换、NEWKEYS。完成后传输层已加密，但尚未认证。

### 服务端模式

```python
transport.start_server(server=my_server_interface)
```

`server` 是 `ServerInterface` 子类实例，用于处理认证和通道请求回调。

## 密钥交换与算法协商

Transport 定义了按优先级排列的算法元组：

- **加密算法** (`_preferred_ciphers`)：aes128-ctr、aes192-ctr、aes256-ctr、aes128-cbc、aes192-cbc、aes256-cbc、3des-cbc、aes128-gcm@openssh.com、aes256-gcm@openssh.com
- **MAC 算法** (`_preferred_macs`)：hmac-sha2-256、hmac-sha2-512、etm 变体、hmac-sha1、hmac-md5 等
- **主机密钥算法** (`_preferred_keys`)：ssh-ed25519、ecdsa-sha2-nistp256/384/521、rsa-sha2-512/256、ssh-rsa
- **密钥交换** (`_preferred_kex`)：curve25519-sha256、ecdh-sha2-nistp256/384/521、diffie-hellman-group-exchange-sha256、group14/16
- **压缩算法** (`_preferred_compression`)：none、zlib、zlib@openssh.com

### SecurityOptions

通过 `get_security_options()` 获取 `SecurityOptions` 对象，可在启动前修改算法优先级：

```python
sec_opts = transport.get_security_options()

print(sec_opts.ciphers)
print(sec_opts.digests)
print(sec_opts.key_types)
print(sec_opts.kex)
print(sec_opts.compression)

sec_opts.ciphers = ("aes256-ctr", "aes128-ctr")
sec_opts.kex = ("curve25519-sha256",)
```

赋值时必须是 tuple 或 list，且所有算法名必须在支持列表中，否则抛出 `ValueError` 或 `TypeError`。

### 禁用算法

```python
transport = paramiko.Transport(
    sock,
    disabled_algorithms={"kex": ["diffie-hellman-group16-sha512"]}
)
```

## 认证

Transport 提供五种认证方法：

### auth_none

```python
allowed = transport.auth_none("username")
```

发送 "none" 认证请求，服务器返回允许的认证方式列表。

### auth_password

```python
transport.auth_password("username", "password")
```

密码认证。`fallback=True` 时自动尝试 keyboard-interactive。

### auth_publickey

```python
key = paramiko.RSAKey.from_private_key_file("/path/to/key")
transport.auth_publickey("username", key)
```

公钥认证。成功返回空列表，部分成功返回允许的后续认证方式。

### auth_interactive

```python
def handler(title, instructions, prompt_list):
    responses = []
    for prompt, echo in prompt_list:
        responses.append(input(prompt))
    return responses

transport.auth_interactive("username", handler)
```

键盘交互式认证，通过回调函数响应服务器的挑战。

### auth_interactive_dumb

```python
transport.auth_interactive_dumb("username")
```

简化的交互式认证，无回调，适用于无需用户输入的场景。

### 获取认证状态

```python
transport.is_authenticated()
transport.get_username()
transport.get_banner()
```

## 通道管理

### 打开会话通道

```python
chan = transport.open_session(timeout=30)
```

打开 "session" 类型通道，用于 exec、shell、subsystem。

### 打开通用通道

```python
chan = transport.open_channel(
    kind="direct-tcpip",
    dest_addr=("internal-host", 80),
    src_addr=("localhost", 12345),
    timeout=30,
)
```

支持的通道类型：
- `"session"`：交互式会话
- `"direct-tcpip"`：直接 TCP/IP 转发（本地端口转发）
- `"x11"`：X11 转发
- `"forwarded-tcpip"`：转发的 TCP/IP 连接（远程端口转发）

### 服务端接受通道

```python
chan = transport.accept(timeout=30)
```

在服务端模式下等待入站通道请求。

### 其他通道方法

```python
transport.open_x11_channel(src_addr=None)
transport.open_forward_agent_channel()
transport.open_forwarded_tcpip_channel(src_addr, dest_addr)
```

## 端口转发

### 请求远程端口转发

```python
port = transport.request_port_forward("", 8080)
```

请求服务器在指定地址和端口监听，连接通过 `accept()` 接收为通道。

### 取消端口转发

```python
transport.cancel_port_forward("", 8080)
```

### 设置子系统处理器

```python
transport.set_subsystem_handler("sftp", paramiko.SFTPServer)
```

注册子系统处理器，服务端收到 subsystem 请求时自动实例化。

## SFTP 客户端

```python
sftp = transport.open_sftp_client()
```

内部执行 `open_session()` + `invoke_subsystem("sftp")`，返回 `SFTPClient`。

## 服务器密钥管理

```python
transport.add_server_key(host_key)

remote_key = transport.get_remote_server_key()
print(remote_key.get_name(), remote_key.get_fingerprint().hex())
```

### 加载 DH moduli

```python
Transport.load_server_moduli("/etc/ssh/moduli")
```

静态方法，加载 DH-GEX 密钥交换所需的素数集合。

## 连接管理

```python
transport.is_active()
transport.close()
transport.get_exception()
```

### 保活

```python
transport.set_keepalive(30)
```

每 30 秒发送 SSH ignore 消息作为保活。

### 压缩

```python
transport.use_compression(compress=True)
```

### 日志

```python
transport.set_log_channel("myapp.transport")
transport.get_log_channel()
transport.set_hexdump(True)
```

## ServiceRequestingTransport

v3.2 新增的 `ServiceRequestingTransport` 继承 Transport，增加了对 `SSH_MSG_SERVICE_ACCEPT` 的处理，支持 ssh-userauth 服务请求流程。这是面向未来的现代化传输实现：

```python
transport = paramiko.ServiceRequestingTransport(sock)
```

## 直接使用 Transport vs SSHClient

| 方面 | SSHClient | Transport |
|------|-----------|-----------|
| 抽象层级 | 高 | 低 |
| 认证 | 自动尝试多种方式 | 手动调用 auth_* |
| 主机密钥 | 策略模式自动处理 | 手动验证 |
| 通道打开 | 封装好的便捷方法 | 直接调用 open_channel |
| 适用场景 | 90% 常规使用 | 自定义协议/高级控制 |
| 线程模型 | 内部创建 Transport 线程 | 自身就是 Thread |

## 相关概念

- [SSHClient 详解](02-ssh-client.md)
- [Channel 通道](04-channel.md)
- [认证体系](05-authentication.md)
- [密钥与主机密钥](06-keys-and-hostkeys.md)
- [端口转发](08-port-forwarding.md)
- [服务端开发](09-server.md)

[^paramiko-source]: paramiko 源码信源，见 [paramiko-source.md](../references/paramiko-source.md)。
