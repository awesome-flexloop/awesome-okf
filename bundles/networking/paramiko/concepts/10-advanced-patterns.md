---
type: Concept
title: 高级模式
description: ProxyCommand 跳板机、连接池、并发通道、日志调试、异常处理、压缩与保活最佳实践
tags: [paramiko, advanced, proxy, logging, exceptions]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: paramiko-source
    resource: /references/paramiko-source.md
---

# 高级模式

## ProxyCommand 跳板机

`ProxyCommand` 通过 subprocess 包装外部代理命令，实现与 `ssh -o ProxyCommand` 相同的效果。它实现了 send/recv/close/settimeout 的 socket-like 接口，可直接传给 Transport。

### 基本用法

```python
import paramiko

proxy = paramiko.ProxyCommand("ssh -W %h:%p bastion.example.com")
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(
    "internal.example.com",
    username="myuser",
    password="mypassword",
    sock=proxy,
)
```

### 通过 nc 跳板

```python
proxy_cmd = "ssh bastion.example.com nc internal-host 22"
sock = paramiko.ProxyCommand(proxy_cmd)

transport = paramiko.Transport(sock)
transport.connect(username="user", password="pass")
```

### ProxyCommand 的工作原理

```python
class ProxyCommand(ClosingContextManager):
    def __init__(self, command_line):
        self.cmd = shlex.split(command_line)
        self.process = subprocess.Popen(
            self.cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
        )
```

- `send(data)`：写入子进程 stdin
- `recv(size)`：从子进程 stdout 读取，使用 select 支持超时
- `close()`：发送 SIGTERM 终止子进程
- `settimeout(timeout)`：设置 recv 超时

子进程异常退出时抛出 `ProxyCommandFailure`，包含 command 和 error 属性。

### 链式跳板

通过嵌套 ProxyCommand 实现多级跳板：

```python
import subprocess, shlex

def jump_chain(jumps, target_host, target_port=22):
    cmd = f"ssh -W {target_host}:{target_port} {jumps[-1]}"
    for jump in reversed(jumps[:-1]):
        cmd = f"ssh -W %h:%p {jump} {cmd}"
    return paramiko.ProxyCommand(cmd)
```

## 连接管理

### 连接池

paramiko 不内建连接池，但可以简单实现：

```python
import queue
import paramiko

class SSHConnectionPool:
    def __init__(self, max_size=5, **connect_kwargs):
        self._pool = queue.Queue(maxsize=max_size)
        self._connect_kwargs = connect_kwargs
        self._max_size = max_size

    def get(self):
        try:
            client = self._pool.get_nowait()
            if client.get_transport() and client.get_transport().is_active():
                return client
            client.close()
        except queue.Empty:
            pass
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(**self._connect_kwargs)
        return client

    def put(self, client):
        try:
            self._pool.put_nowait(client)
        except queue.Full:
            client.close()

    def close_all(self):
        while not self._pool.empty():
            try:
                client = self._pool.get_nowait()
                client.close()
            except queue.Empty:
                break
```

### 连接健康检查

```python
def ensure_alive(client):
    transport = client.get_transport()
    if transport is None or not transport.is_active():
        raise ConnectionError("SSH connection is not active")
    if not transport.is_authenticated():
        raise ConnectionError("SSH connection is not authenticated")
    return True
```

## 并发通道

单个 Transport 支持多路复用多个 Channel，可并行执行多个操作：

```python
import concurrent.futures

def run_command(transport, command):
    chan = transport.open_session()
    chan.exec_command(command)
    output = chan.makefile("r").read()
    exit_code = chan.recv_exit_status()
    chan.close()
    return command, output, exit_code

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    futures = [
        executor.submit(run_command, transport, f"sleep {i}; echo done{i}")
        for i in range(4)
    ]
    for future in concurrent.futures.as_completed(futures):
        cmd, output, code = future.result()
        print(f"{cmd}: exit={code}, output={output.strip()}")
```

### 并发 SFTP 传输

```python
def parallel_download(sftp, remote_files, local_dir, max_workers=4):
    import os
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {}
        for remote in remote_files:
            local = os.path.join(local_dir, os.path.basename(remote))
            f = pool.submit(sftp.get, remote, local)
            futures[f] = remote
        for future in concurrent.futures.as_completed(futures):
            remote = futures[future]
            try:
                future.result()
                print(f"Downloaded: {remote}")
            except Exception as e:
                print(f"Failed {remote}: {e}")
```

> 注意：SFTPClient 内部有请求编号锁，多线程共享单个 SFTPClient 是安全的，但高并发场景可能需要为每个线程创建独立 SFTP 会话。

## 日志调试

### 配置日志

```python
import logging
import paramiko

logging.basicConfig(level=logging.DEBUG)
paramiko.util.log_to_file("/tmp/paramiko.log", level=logging.DEBUG)
```

`paramiko.util.log_to_file(filename, level=DEBUG)` 便捷函数配置文件日志。

### 自定义日志通道

```python
client.set_log_channel("myapp.ssh")
transport.set_log_channel("myapp.transport")
```

### Hexdump 调试

```python
transport.set_hexdump(True)
```

启用原始数据包十六进制转储，用于调试协议问题。生产环境应关闭。

### 日志器命名

paramiko 使用以下日志器：

- `paramiko.transport`：传输层日志
- `paramiko.transport.sftp`：SFTP 日志（通道名附加 `.sftp`）
- `paramiko.hostkeys`：主机密钥日志

## 异常处理

### 异常层次

```
SSHException
├── AuthenticationException
│   ├── PasswordRequiredException
│   ├── BadAuthenticationType
│   ├── PartialAuthentication
│   ├── UnableToAuthenticate
│   └── AuthFailure
├── ChannelException
├── BadHostKeyException
├── IncompatiblePeer
├── ProxyCommandFailure
├── CouldNotCanonicalize
├── ConfigParseError
└── MessageOrderError

socket.error
└── NoValidConnectionsError
```

### 完整异常处理模板

```python
import paramiko
from paramiko.ssh_exception import (
    AuthenticationException,
    BadHostKeyException,
    NoValidConnectionsError,
    SSHException,
)

try:
    with paramiko.SSHClient() as client:
        client.load_system_host_keys()
        client.connect(
            "example.com",
            username="user",
            password="pass",
            timeout=10,
            banner_timeout=15,
            auth_timeout=15,
        )
        stdin, stdout, stderr = client.exec_command("ls", timeout=30)
        output = stdout.read().decode()
        exit_code = stdout.channel.recv_exit_status()

except BadHostKeyException as e:
    print(f"Host key mismatch: expected {e.expected_key.get_base64()[:20]}")
    print(f"Got: {e.key.get_base64()[:20]}")

except AuthenticationException as e:
    print(f"Authentication failed: {e}")

except NoValidConnectionsError as e:
    print(f"Could not connect to any address:")
    for addr, error in e.errors.items():
        print(f"  {addr}: {error}")

except SSHException as e:
    print(f"SSH error: {e}")

except socket.timeout:
    print("Connection timed out")

except OSError as e:
    print(f"Network error: {e}")
```

### BadAuthenticationType

```python
try:
    transport.auth_password("user", "pass")
except paramiko.BadAuthenticationType as e:
    print(f"Password auth not allowed. Allowed: {e.allowed_types}")
    if "publickey" in e.allowed_types:
        transport.auth_publickey("user", key)
```

### ChannelException

```python
try:
    chan = transport.open_session(timeout=5)
except paramiko.ChannelException as e:
    print(f"Channel open failed: code={e.code}, text={e.text}")
```

## 压缩

```python
client.connect("example.com", compress=True)
```

或在 Transport 层：

```python
transport.use_compression(compress=True)
```

压缩在认证完成后生效，对慢速网络有帮助，对快速内网可能增加 CPU 开销。支持 zlib 和 zlib@openssh.com。

## 保活

```python
transport.set_keepalive(30)
```

每 30 秒发送 SSH ignore 消息，防止 NAT/防火墙断开空闲连接。

### 手动保活

```python
transport.send_ignore(byte_count=1)
```

手动发送 ignore 消息。

### 重密钥

```python
transport.renegotiate_keys()
```

手动触发密钥重协商。通常 paramiko 根据传输字节数自动触发。

## SSH Config 集成

```python
from paramiko import SSHConfig, SSHClient

config = SSHConfig.from_path("/home/user/.ssh/config")
host_config = config.lookup("myhost")

client.connect(
    hostname=host_config.get("hostname", "myhost"),
    port=int(host_config.get("port", 22)),
    username=host_config.get("user"),
    key_filename=host_config.get("identityfile"),
    timeout=float(host_config.get("connecttimeout", 10)),
)
```

`SSHConfig` 解析 OpenSSH ssh_config 格式，支持 `Host`、`Match`、`%h`/`%p`/`%r` 等 token 展开。

## 全局请求

```python
result = transport.global_request("tcpip-forward", data=None, wait=True)
```

发送 SSH_MSG_GLOBAL_REQUEST，可用于自定义扩展协议。

## 安全建议

1. **使用 Ed25519 密钥**：比 RSA 更短更快，安全性相当
2. **禁用弱算法**：通过 `disabled_algorithms` 关闭 3des-cbc、hmac-md5 等
3. **验证主机密钥**：生产环境绝不使用 AutoAddPolicy
4. **使用 AuthStrategy**：替代硬编码的旧认证流程，更灵活可审计
5. **设置超时**：始终设置 connect/auth/banner/channel 超时
6. **显式关闭**：使用 with 语句或 try/finally 确保连接关闭
7. **日志不含敏感信息**：paramiko 不记录密码，但自定义日志中需注意

## 相关概念

- [SSHClient 详解](/concepts/02-ssh-client.md)
- [Transport 底层传输](/concepts/03-transport.md)
- [认证体系](/concepts/05-authentication.md)
- [密钥与主机密钥](/concepts/06-keys-and-hostkeys.md)
- [端口转发](/concepts/08-port-forwarding.md)
- [服务端开发](/concepts/09-server.md)

[^paramiko-source]: paramiko 源码信源，见 [paramiko-source.md](/references/paramiko-source.md)。
