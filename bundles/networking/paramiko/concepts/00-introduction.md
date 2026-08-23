---
type: Concept
title: paramiko 简介
description: 纯 Python SSH2 协议库——什么是 paramiko、设计哲学、安装方法、与其他 SSH 库的对比
tags: [paramiko, introduction, ssh]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: paramiko-source
    resource: /references/paramiko-source.md
---

# paramiko 简介

## 什么是 paramiko

paramiko 是一个纯 Python 实现的 SSH2（Secure Shell version 2）协议库。它提供了客户端和服务端的完整 SSH2 协议实现，支持加密会话、身份认证、通道多路复用、SFTP 文件传输、端口转发等核心 SSH 功能。paramiko 的名字来自世界语"paranoiko"（偏执狂）的谐音，体现了 SSH 协议对安全的关注。

paramiko 由 Robey Pointer 创建，现由 Jeff Forcier 维护，是 Python 生态中最广泛使用的 SSH 库。Fabric、Ansible 等知名自动化工具均以 paramiko 作为底层 SSH 引擎。

## 设计哲学

paramiko 遵循以下设计原则：

- **纯 Python 实现**：核心协议不依赖系统 OpenSSH 客户端，通过 cryptography、bcrypt、pynacl 等库实现加密原语，跨平台一致性好
- **分层架构**：`SSHClient` 提供高层便捷 API，`Transport` 处理底层协议，`Channel` 模拟 socket，用户可按需选择抽象层级
- **协议完整性**：实现 SSH2 协议的完整状态机，包括密钥交换（KEX）、加密协商、认证、通道管理、重密钥（rekey）
- **可扩展性**：通过 `ServerInterface`、`SFTPServerInterface`、`MissingHostKeyPolicy`、`AuthStrategy` 等接口支持自定义行为
- **上下文管理器支持**：所有资源类（SSHClient/Transport/Channel/SFTPClient 等）均继承 `ClosingContextManager`，支持 `with` 语句

## 安装方法

paramiko 通过 pip 安装：

```bash
pip install paramiko
```

paramiko v5.0.0 的依赖：

- `cryptography`：加密原语（AES、RSA、ECDSA、Ed25519 等）
- `bcrypt`：OpenSSH 私钥解密
- `pynacl`：Ed25519 密钥支持

Python 版本要求 ≥ 3.7。

验证安装：

```bash
python -c "import paramiko; print(paramiko.__version__)"
```

## 与其他 SSH 库的对比

| 特性 | paramiko | Fabric | asyncssh | spur |
|------|----------|--------|----------|------|
| 定位 | SSH 协议底层库 | 远程执行高层框架 | 异步 SSH 库 | 极简远程执行 |
| 实现语言 | 纯 Python | 基于 paramiko | 纯 Python（asyncio） | 基于 paramiko/ssh |
| 异步支持 | 线程模型 | 同步 | asyncio 原生 | 同步 |
| SFTP 支持 | 完整 | 封装 | 完整 | 无 |
| 服务端支持 | 有 | 无 | 有 | 无 |
| 端口转发 | 有 | 无 | 有 | 无 |
| 学习曲线 | 中等 | 低 | 中高 | 极低 |

### 与 subprocess + ssh 命令的对比

直接调用系统 `ssh` 命令是另一种常见方式：

```python
import subprocess
result = subprocess.run(["ssh", "user@host", "ls"], capture_output=True)
```

paramiko 相比此方式的优势：

1. **无外部依赖**：不需要目标系统安装 OpenSSH 客户端
2. **编程控制**：可编程化控制认证过程、通道管理、端口转发
3. **多路复用**：单个 SSH 连接上可并行打开多个通道
4. **SFTP 集成**：内建 SFTP 客户端，无需调用 sftp/scp 命令
5. **跨平台**：Windows/macOS/Linux 行为一致
6. **异常处理**：Python 异常体系，优于解析命令输出

## 核心模块一览

paramiko 的主要模块构成：

- **客户端层**：`SSHClient`——连接、认证、执行命令、SFTP 的一站式入口
- **传输层**：`Transport`——SSH2 协议核心，管理加密会话和通道
- **通道层**：`Channel`——多路复用的逻辑通道，类 socket API
- **认证层**：`AuthHandler`/`AuthStrategy`——多机制认证
- **密钥层**：`PKey`/`RSAKey`/`Ed25519Key`/`ECDSAKey`——密钥管理
- **SFTP 层**：`SFTPClient`/`SFTPFile`/`SFTPAttributes`——文件传输
- **服务端层**：`ServerInterface`/`SFTPServer`——自定义 SSH 服务端
- **安全层**：`HostKeys`/`MissingHostKeyPolicy`——主机密钥验证

## 相关概念

- [5分钟快速上手](/concepts/01-getting-started.md)
- [SSHClient 详解](/concepts/02-ssh-client.md)
- [Transport 底层传输](/concepts/03-transport.md)
- [认证体系](/concepts/05-authentication.md)
- [paramiko 源码信源登记](/references/paramiko-source.md)

[^paramiko-source]: paramiko 源码信源，见 [paramiko-source.md](/references/paramiko-source.md)。
