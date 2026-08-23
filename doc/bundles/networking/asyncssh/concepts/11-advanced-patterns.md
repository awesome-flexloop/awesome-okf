---
type: Concept
title: 高级模式
description: 并发连接、asyncio.gather 并行、加密算法配置、后量子密钥交换、调试日志、异常处理、连接池、X11/Agent 转发
tags: [asyncssh, advanced, concurrency, post-quantum, logging, debugging]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: asyncssh-source
    resource: /references/asyncssh-source.md
---

# 高级模式

## 并发连接

asyncssh 基于 asyncio，单线程内可并行管理大量 SSH 连接。使用 `asyncio.gather()` 同时操作多台主机：

```python
import asyncio
import asyncssh

async def run_command(host, command):
    async with asyncssh.connect(host, known_hosts=None) as conn:
        result = await conn.run(command, check=True)
        return host, result.stdout

async def main():
    hosts = ['host1', 'host2', 'host3', 'host4']
    tasks = [run_command(h, 'uname -r') for h in hosts]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for host, result in zip(hosts, results):
        if isinstance(result, Exception):
            print(f'{host}: 错误 - {result}')
        else:
            print(f'{host}: {result.strip()}')

asyncio.run(main())
```

### 信号量限流

大量并发时使用 `asyncio.Semaphore` 控制并发数：

```python
sem = asyncio.Semaphore(10)

async def limited_connect(host):
    async with sem:
        async with asyncssh.connect(host) as conn:
            return await conn.run('hostname')
```

### 连接池模式

简单的连接池：

```python
class SSHConnectionPool:
    def __init__(self, host, pool_size=5, **kwargs):
        self.host = host
        self.kwargs = kwargs
        self.pool = []
        self.sem = asyncio.Semaphore(pool_size)

    async def acquire(self):
        await self.sem.acquire()
        if self.pool:
            return self.pool.pop()
        return await asyncssh.connect(self.host, **self.kwargs)

    def release(self, conn):
        if not conn.is_closing():
            self.pool.append(conn)
        self.sem.release()

    async def run(self, command):
        conn = await self.acquire()
        try:
            return await conn.run(command)
        finally:
            self.release(conn)

    async def close(self):
        for conn in self.pool:
            conn.close()
        await asyncio.gather(*[c.wait_closed() for c in self.pool])
```

## 加密算法配置

### 指定算法列表

`connect()` 和 `create_server()` 接受算法参数：

```python
conn = await asyncssh.connect(
    'host',
    kex_algs=['curve25519-sha256', 'ecdh-sha2-nistp256'],
    encryption_algs=['chacha20-poly1305@openssh.com',
                     'aes256-gcm@openssh.com'],
    mac_algs=['hmac-sha2-256-etm@openssh.com'],
    compression_algs=['none', 'zlib@openssh.com'],
    server_host_key_algs=['ssh-ed25519', 'rsa-sha2-512']
)
```

### 禁用弱算法

```python
conn = await asyncssh.connect(
    'host',
    kex_algs=['-diffie-hellman-group1-sha1',
              '-diffie-hellman-group14-sha1'],
    encryption_algs=['-3des-cbc', '-aes128-cbc']
)
```

前缀 `-` 表示从默认列表中排除。

## 后量子密钥交换

asyncssh 支持 ML-KEM（Kyber）和 SNTRUP 后量子密钥交换算法（需要 cryptography 库支持）：

```python
conn = await asyncssh.connect(
    'host',
    kex_algs=['mlkem768nistp256-sha256',
              'sntrup761x25519-sha512',
              'curve25519-sha256']
)
```

检测可用性：

```python
from asyncssh.crypto import mlkem_available, sntrup_available

if mlkem_available:
    print('ML-KEM 可用')
if sntrup_available:
    print('SNTRUP 可用')
```

## 调试日志

asyncssh 使用 Python logging 模块。

### 设置日志级别

```python
asyncssh.set_log_level('DEBUG')
```

### SFTP 专用日志

```python
asyncssh.set_sftp_log_level('DEBUG')
```

### 调试级别（更详细）

```python
asyncssh.set_debug_level(2)  # 0-3，越高越详细
```

### 包级别日志

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('asyncssh').setLevel(logging.DEBUG1)
```

asyncssh 定义了自定义日志级别 `DEBUG1`（比 DEBUG 更详细）、`DEBUG2`、`DEBUG3`。

## 异常处理

asyncssh 异常层次定义于 `misc.py`，基类为 `Error`：

```python
try:
    async with asyncssh.connect('host') as conn:
        result = await conn.run('cmd', check=True, timeout=10)
except asyncssh.HostKeyNotVerifiable as e:
    print(f'主机密钥验证失败: {e}')
except asyncssh.PermissionDenied as e:
    print(f'认证失败: {e}')
except asyncssh.ChannelOpenError as e:
    print(f'通道打开失败: {e}')
except asyncssh.ConnectionLost as e:
    print(f'连接断开: {e}')
except asyncssh.ProcessError as e:
    print(f'命令失败 (exit {e.returncode}): {e.stderr}')
except asyncssh.TimeoutError as e:
    print(f'命令超时: {e.stdout}, {e.stderr}')
except asyncssh.DisconnectError as e:
    print(f'服务器断开: code={e.code}, reason={e.reason}')
```

### 异常分类

| 异常 | 场景 |
|------|------|
| `DisconnectError` | SSH 连接被断开 |
| `ConnectionLost` | 网络连接丢失 |
| `HostKeyNotVerifiable` | 主机密钥验证失败 |
| `KeyExchangeFailed` | 密钥交换失败 |
| `PermissionDenied` | 认证失败 |
| `ChannelOpenError` | 通道打开被拒 |
| `ChannelListenError` | 端口监听失败 |
| `ProtocolError` | 协议错误 |
| `ProtocolNotSupported` | 不支持的协议版本 |
| `ServiceNotAvailable` | 请求的服务不可用 |
| `CompressionError` | 压缩失败 |
| `MACError` | MAC 验证失败 |
| `PasswordChangeRequired` | 需要修改密码 |
| `ProcessError` | 进程非零退出（check=True） |
| `TimeoutError` | 命令执行超时 |
| `BreakReceived` | 收到 break 信号 |
| `SignalReceived` | 收到信号 |
| `TerminalSizeChanged` | 终端窗口大小变化 |
| `KeyGenerationError` | 密钥生成失败 |
| `KeyImportError` | 密钥导入失败 |
| `KeyExportError` | 密钥导出失败 |
| `SFTPError` | SFTP 操作失败（30+ 子类） |

## 多通道并行

单个 SSH 连接上可并行打开多个通道：

```python
async with asyncssh.connect('host') as conn:
    results = await asyncio.gather(
        conn.run('command1'),
        conn.run('command2'),
        conn.run('command3')
    )
    for r in results:
        print(r.stdout)
```

## 长连接与 Keepalive

```python
conn = await asyncssh.connect(
    'host',
    keepalive_interval=30,      # 每 30 秒发送 keepalive
    keepalive_count_max=5       # 5 次未应答后断开
)
```

## 重密钥（Rekey）

```python
conn = await asyncssh.connect(
    'host',
    rekey_bytes=1024*1024*1024,  # 每传输 1 GiB 后重密钥
    rekey_seconds=3600           # 或每小时重密钥
)
```

## X11 转发

```python
proc = await conn.create_process(
    'xeyes',
    x11_forwarding=True,
    x11_display='localhost:0'
)
```

服务端通过 `get_x11_display()` 获取 X11 显示信息。

## Agent 转发

```python
conn = await asyncssh.connect(
    'host',
    agent_forwarding=True
)
```

服务端通过 `get_agent_path()` 获取转发的 Agent socket 路径。

## TUN/TAP 隧道

```python
listener = await conn.forward_tun(local_unit=0)
```

需要 root 权限和系统 TUN/TAP 设备支持。

## SSHSubprocess 桥接

`subprocess.py` 提供与 `asyncio.create_subprocess_exec()` 兼容的 API：

```python
transport, protocol = await conn.create_subprocess(
    MyProtocol, 'ls', '-la'
)
```

`SSHSubprocessProtocol` 实现 `asyncio.SubprocessProtocol` 接口，可直接替换本地子进程。

## 行编辑器

`SSHLineEditorChannel`（editor.py）提供终端行编辑功能（readline 风格）：

```python
async def handle_session(process):
    line_editor = asyncssh.SSHLineEditorChannel(process)
    async for line in line_editor:
        process.stdout.write(f'执行: {line}\n')
```

## 配置文件

asyncssh 支持 OpenSSH `ssh_config` 配置文件：

```python
conn = await asyncssh.connect('alias-in-config',
                              config='~/.ssh/config')
```

支持的配置项包括 HostName、User、Port、IdentityFile、ProxyCommand、LocalForward、RemoteForward 等。

## 相关概念

- [异步连接详解](/concepts/02-async-connection.md) —— connect() 参数全览
- [端口转发](/concepts/09-port-forwarding.md) —— 转发详解
- [服务端开发](/concepts/10-server.md) —— 服务端配置
- [实战示例：并行连接](/examples/parallel-connections.md)
- [paramiko 高级模式](../../paramiko/concepts/10-advanced-patterns.md)（同步模式对比）

[^asyncssh-source]: asyncssh 源码信源，见 [asyncssh-source.md](/references/asyncssh-source.md)。
