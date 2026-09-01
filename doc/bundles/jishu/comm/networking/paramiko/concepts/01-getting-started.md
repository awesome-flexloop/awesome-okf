---
type: Concept
title: 5分钟快速上手
description: 从安装到第一个 SSH 连接、执行命令、传输文件的快速入门指南
tags: [paramiko, getting-started, quickstart]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: paramiko-source
    resource: /references/paramiko-source.md
---

# 5分钟快速上手

## 安装

```bash
pip install paramiko
```

验证安装：

```python
import paramiko
print(paramiko.__version__)
```

## 第一个 SSH 连接

以下是最简化的 SSH 连接示例，执行命令并获取输出：

```python
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("example.com", username="myuser", password="mypassword")

stdin, stdout, stderr = client.exec_command("ls -la")
print(stdout.read().decode())

client.close()
```

> **安全提示**：`AutoAddPolicy` 会自动接受未知主机密钥，存在中间人攻击风险。生产环境应使用 `load_system_host_keys()` 或 `RejectPolicy`（默认）。

## 使用上下文管理器

所有 paramiko 资源类都支持 `with` 语句，自动关闭连接：

```python
import paramiko

with paramiko.SSHClient() as client:
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("example.com", username="myuser", password="mypassword")
    stdin, stdout, stderr = client.exec_command("hostname")
    print(stdout.read().decode().strip())
```

## 使用密钥认证

推荐使用公钥认证而非密码：

```python
import paramiko

with paramiko.SSHClient() as client:
    client.load_system_host_keys()
    key = paramiko.RSAKey.from_private_key_file("/home/user/.ssh/id_rsa")
    client.connect("example.com", username="myuser", pkey=key)
    stdin, stdout, stderr = client.exec_command("whoami")
    print(stdout.read().decode().strip())
```

也可以使用带密码保护的密钥：

```python
key = paramiko.Ed25519Key.from_private_key_file(
    "/home/user/.ssh/id_ed25519", password="keypassphrase"
)
```

## 传输文件

通过 `open_sftp()` 获取 SFTP 客户端进行文件传输：

```python
import paramiko

with paramiko.SSHClient() as client:
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("example.com", username="myuser", password="mypassword")

    sftp = client.open_sftp()

    sftp.put("local_file.txt", "/remote/path/file.txt")
    sftp.get("/remote/path/file.txt", "downloaded_file.txt")

    sftp.close()
```

SFTP 客户端也支持上下文管理器：

```python
with client.open_sftp() as sftp:
    sftp.put("local.txt", "remote.txt")
```

## 交互式 Shell

需要交互式终端（如 top、vim）时使用 `invoke_shell`：

```python
import paramiko
import time

with paramiko.SSHClient() as client:
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("example.com", username="myuser", password="mypassword")

    chan = client.invoke_shell(term="xterm", width=120, height=40)
    time.sleep(1)
    output = chan.recv(4096).decode()
    print(output)

    chan.send(b"ls -la\n")
    time.sleep(1)
    print(chan.recv(4096).decode())
```

## 连接参数速查

`SSHClient.connect()` 的常用参数：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `hostname` | 必填 | 服务器地址 |
| `port` | 22 | SSH 端口 |
| `username` | 当前系统用户 | 登录用户名 |
| `password` | None | 密码（也用于密钥解密） |
| `pkey` | None | PKey 私钥对象 |
| `key_filename` | None | 私钥文件路径（可列表） |
| `timeout` | None | TCP 连接超时（秒） |
| `allow_agent` | True | 是否允许 SSH agent |
| `look_for_keys` | True | 是否搜索 ~/.ssh/ 密钥 |
| `passphrase` | None | 私钥密码短语 |
| `compress` | False | 是否启用压缩 |
| `banner_timeout` | None | SSH banner 等待超时 |
| `auth_timeout` | None | 认证超时 |
| `disabled_algorithms` | None | 禁用的算法字典 |

## 认证顺序

SSHClient 默认按以下顺序尝试认证：

1. 显式传入的 `pkey` 或 `key_filename`
2. SSH agent 中的密钥（如果 `allow_agent=True`）
3. `~/.ssh/` 下发现的 `id_rsa`、`id_ecdsa`、`id_ed25519`（如果 `look_for_keys=True`）
4. 密码认证（如果提供了 `password`）

## 下一步

- 了解 [SSHClient 详解](02-ssh-client.md) 掌握完整 API
- 深入 [Transport 底层传输](03-transport.md) 理解协议机制
- 学习 [SFTP 文件传输](07-sftp.md) 掌握文件操作
- 查看 [基础连接示例](../examples/basic-connection.md) 获取更多代码

## 相关概念

- [paramiko 简介](00-introduction.md)
- [SSHClient 详解](02-ssh-client.md)
- [认证体系](05-authentication.md)
- [SFTP 文件传输](07-sftp.md)
- [基础连接示例](../examples/basic-connection.md)

[^paramiko-source]: paramiko 源码信源，见 [paramiko-source.md](../references/paramiko-source.md)。
