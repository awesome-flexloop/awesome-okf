---
type: Concept
title: asyncssh 简介
description: 基于 asyncio 的异步 SSH2 协议库——什么是 asyncssh、异步模型、安装方法、与 paramiko 对比
tags: [asyncssh, introduction, ssh, async]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: asyncssh-source
    resource: /references/asyncssh-source.md
---

# asyncssh 简介

## 什么是 asyncssh

asyncssh 是一个基于 Python `asyncio` 的异步 SSHv2 协议客户端和服务端库，由 Ron Frederick 开发。它提供了完整的 SSH2 协议实现，支持加密会话、身份认证、通道多路复用、SFTP/SCP 文件传输、端口转发、SSH Agent 等核心 SSH 功能。

asyncssh v2.24.0 基于 Python 3.10+，依赖 `cryptography` 库提供加密原语。整个库采用纯 Python 实现，通过 asyncio 事件循环实现高并发，无需线程即可同时处理数百个 SSH 连接。

## 异步模型

asyncssh 与同步 SSH 库（如 paramiko）的根本区别在于 IO 模型：

- **所有 IO 操作都是协程**：`connect()`、`run()`、`create_process()`、`start_sftp_client()`、`get()`、`put()` 等均为 `async def`，必须通过 `await` 调用
- **单线程并发**：基于 asyncio 事件循环，单个线程内可并行处理多个 SSH 连接和通道
- **asyncio.Protocol 状态机**：`SSHConnection` 继承 `asyncio.Protocol`，通过 `connection_made()`/`data_received()`/`connection_lost()` 回调驱动协议
- **异步上下文管理器**：`SSHClientConnection`、`SFTPClient`、`SSHProcess`、`SSHListener` 均支持 `async with` 语法
- **asyncio 流风格 API**：`SSHReader` 提供 `read()`/`readline()`/`readuntil()`，`SSHWriter` 提供 `write()`/`drain()`，与 `asyncio.StreamReader`/`StreamWriter` 接口一致

## 安装方法

```bash
pip install asyncssh
```

asyncssh v2.24.0 的核心依赖：

- `cryptography`：加密原语（AES、RSA、ECDSA、Ed25519、X25519 等）
- `typing_extensions`：类型扩展支持

Python 版本要求 ≥ 3.10。

验证安装：

```bash
python -c "import asyncssh; print(asyncssh.__version__)"
```

可选依赖：

- `python-gssapi`：GSSAPI/Kerberos 认证
- `pkcs11`：PKCS#11 硬件安全模块
- `libnacl`：额外加密算法支持

## 与 paramiko 的对比

| 特性 | asyncssh | paramiko |
|------|----------|----------|
| IO 模型 | asyncio 原生异步 | 线程模型（Transport 继承 Thread） |
| Python 版本 | ≥ 3.10 | ≥ 3.7 |
| 连接入口 | `await asyncssh.connect()` 协程 | `SSHClient().connect()` 同步方法 |
| 执行命令 | `await conn.run('cmd')` 返回 `SSHCompletedProcess` | `client.exec_command('cmd')` 返回 stdin/stdout/stderr |
| SFTP | `await conn.start_sftp_client()` | `client.open_sftp()` |
| 流 API | `SSHReader`/`SSHWriter`（async 原生） | `Channel`（类 socket，recv/send） |
| 进程模型 | `SSHClientProcess` 带 stdin/stdout/stderr 流 | `Channel` + `ChannelFile` |
| 端口转发 | `forward_local_port()`/`forward_remote_port()` 协程 | `request_port_forward()` 同步 |
| 密钥生成 | `generate_private_key('ssh-ed25519')` 函数 | `RSAKey.generate()` 类方法 |
| 服务端 | `create_server()` 协程，`SSHServer` 回调 | `Transport` + `ServerInterface` |
| SFTP 版本 | v3-v6 | v3 |
| 后量子 KEX | 支持 ML-KEM、SNTRUP | 不支持 |
| X.509 证书 | 支持 | 不支持 |
| 许可证 | EPL-2.0 OR GPL-2.0-or-later | LGPL |

### 核心 API 映射

| 用途 | paramiko | asyncssh |
|------|----------|----------|
| 连接 | `SSHClient().connect(host, username=, password=)` | `await asyncssh.connect(host, username=, password=)` |
| 执行命令 | `stdin, stdout, stderr = client.exec_command(cmd)` | `result = await conn.run(cmd)` |
| 交互式 Shell | `chan = client.invoke_shell()` | `proc = await conn.create_process(term_type='xterm')` |
| SFTP | `sftp = client.open_sftp()` | `sftp = await conn.start_sftp_client()` |
| 上传 | `sftp.put(local, remote)` | `await sftp.put(local, remote)` |
| 下载 | `sftp.get(remote, local)` | `await sftp.get(remote, local)` |
| 本地转发 | `client.request_port_forward(...)` | `listener = await conn.forward_local_port(...)` |

参考：[paramiko SSHClient 详解](../../paramiko/concepts/02-ssh-client.md)（同步模型对比）。

## 核心模块一览

asyncssh 的主要模块构成：

- **连接层**：`connect()` / `listen()` / `create_server()` —— 客户端与服务端入口
- **协议层**：`SSHConnection` / `SSHClientConnection` / `SSHServerConnection` —— asyncio.Protocol 状态机
- **通道层**：`SSHChannel` / `SSHClientChannel` / `SSHServerChannel` —— 多路复用逻辑通道
- **流层**：`SSHReader` / `SSHWriter` —— asyncio 流风格读写
- **进程层**：`SSHClientProcess` / `SSHServerProcess` / `SSHCompletedProcess` —— 命令执行与 IO 重定向
- **SFTP 层**：`SFTPClient` / `SFTPClientFile` / `SFTPServer` / `SFTPAttrs` —— 文件传输
- **密钥层**：`SSHKey` / `SSHCertificate` / `generate_private_key()` —— 密钥与证书管理
- **认证层**：`SSHClient` / `SSHServer` 回调、password/publickey/keyboard-interactive/GSSAPI
- **转发层**：`SSHForwarder` / `SSHListener` —— 端口转发与 SOCKS
- **加密层**：`crypto/` 子包 —— 算法插件注册体系

## 相关概念

- [5分钟快速上手](01-getting-started.md)
- [异步连接详解](02-async-connection.md)
- [通道与流](03-channels.md)
- [asyncssh 源码信源登记](../references/asyncssh-source.md)

[^asyncssh-source]: asyncssh 源码信源，见 [asyncssh-source.md](../references/asyncssh-source.md)。
