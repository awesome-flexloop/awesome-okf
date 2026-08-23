---
type: Concept
title: 认证体系
description: paramiko 认证全解——password/publickey/keyboard-interactive、AuthStrategy 可插拔框架、Agent 集成
tags: [paramiko, authentication, auth-strategy, agent]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: paramiko-source
    resource: /references/paramiko-source.md
---

# 认证体系

## 认证机制概览

paramiko 支持 SSH2 协议定义的多种认证方式：

| 方式 | 方法 | 说明 |
|------|------|------|
| 密码 | `auth_password` | 用户名+密码 |
| 公钥 | `auth_publickey` | 私钥签名验证 |
| 键盘交互 | `auth_interactive` | 服务器发起问答挑战 |
| None | `auth_none` | 查询服务器允许的认证方式 |
| GSSAPI | （需扩展） | Kerberos 等 |

paramiko v3.2+ 引入了新版 `AuthStrategy` 可插拔认证框架，与旧版 `SSHClient._auth()` 硬编码逻辑并存。

## SSHClient 的旧版认证流程

`SSHClient.connect()` 默认使用旧版认证路径 `_auth()`，按固定优先级尝试：

1. **显式密钥**：传入的 `pkey` 参数
2. **密钥文件**：`key_filename` 指定的文件（按 RSAKey、ECDSAKey、Ed25519Key 顺序尝试）
3. **SSH Agent**：通过 `Agent()` 连接本地 agent，遍历 `get_keys()`
4. **自动发现密钥**：搜索 `~/.ssh/id_rsa`、`~/.ssh/id_ecdsa`、`~/.ssh/id_ed25519`（含 `-cert.pub` 证书）
5. **密码认证**：使用 `password` 参数

```python
client.connect(
    "example.com",
    username="myuser",
    password="mypassword",
    key_filename=["~/.ssh/id_rsa", "~/.ssh/id_ed25519"],
    allow_agent=True,
    look_for_keys=True,
)
```

### 双因素认证

旧版流程支持部分认证（partial authentication）。公钥认证成功但服务器要求第二因素时，返回允许的后续认证类型（如 `["password"]`），流程继续尝试密码或 keyboard-interactive：

```python
try:
    client.connect("example.com", username="user", pkey=key, password="otp")
except paramiko.AuthenticationException as e:
    print(f"Auth failed: {e}")
```

## Transport 认证方法

直接使用 Transport 时需手动调用认证方法：

### 密码认证

```python
transport.auth_password(username="user", password="pass")
```

`fallback=True`（默认）时，若密码认证失败且服务器允许 keyboard-interactive，自动降级尝试。

### 公钥认证

```python
key = paramiko.RSAKey.from_private_key_file("/path/to/key")
transport.auth_publickey(username="user", key=key)
```

### 键盘交互认证

```python
def auth_handler(title, instructions, prompt_list):
    responses = []
    for prompt, echo in prompt_list:
        if "password" in prompt.lower():
            responses.append("mypassword")
        elif "verification" in prompt.lower():
            responses.append("123456")
        else:
            responses.append(input(prompt))
    return responses

transport.auth_interactive("user", auth_handler)
```

`prompt_list` 是 `(prompt_text, echo)` 元组列表，`echo` 为 False 表示密码类输入不应回显。

### 简化交互认证

```python
transport.auth_interactive_dumb("user")
```

无回调函数，适用于不需要响应用户输入的场景。

### 查询可用认证方式

```python
allowed = transport.auth_none("user")
print(f"Allowed auth methods: {allowed}")
```

## AuthStrategy 新版认证框架

v3.2 引入的 `AuthStrategy` 是面向未来的可插拔认证框架。通过 `connect(auth_strategy=...)` 参数启用，与旧认证参数互斥。

### 核心类

- `AuthStrategy`：基类，子类实现 `get_sources()` 生成器
- `AuthSource`：认证源基类
- `NoneAuth`：none 认证
- `Password`：密码认证（接受 `password_getter` 惰性调用）
- `PrivateKey`：私钥认证 mixin
- `InMemoryPrivateKey`：内存中的已解密密钥
- `OnDiskPrivateKey`：磁盘上的密钥文件
- `AuthResult`：认证结果，list 子类
- `AuthFailure`：整体认证失败异常

### 认证源

```python
from paramiko.auth_strategy import (
    AuthStrategy, NoneAuth, Password, InMemoryPrivateKey, OnDiskPrivateKey
)

class MyAuthStrategy(AuthStrategy):
    def get_sources(self):
        config = self.ssh_config
        username = config["user"]

        yield NoneAuth(username=username)

        key_path = config.get("identityfile", ["~/.ssh/id_ed25519"])[0]
        yield OnDiskPrivateKey(
            username=username,
            source="ssh-config",
            path=key_path,
            pkey=paramiko.Ed25519Key.from_private_key_file(key_path),
        )

        yield Password(
            username=username,
            password_getter=lambda: getpass.getpass("Password: "),
        )
```

### 执行认证

```python
from paramiko import SSHConfig

config = SSHConfig.from_path("~/.ssh/config")
host_config = config.lookup("example.com")

strategy = MyAuthStrategy(ssh_config=host_config)
result = client.connect("example.com", auth_strategy=strategy)

for source_result in result:
    print(f"{source_result.source} -> {source_result.result or 'success'}")
```

### AuthResult 语义

`AuthResult` 是 `SourceResult` namedtuple 的列表：

- `source`：尝试的 `AuthSource` 对象
- `result`：Transport 认证方法的返回值（允许的后续认证方式列表），或异常对象

认证成功时，对应 result 为空列表 `[]`，`__str__` 显示为 "success"。所有 source 均失败时抛出 `AuthFailure`，其 `result` 属性包含完整的 AuthResult。

### Password 的惰性获取

`Password` 接受 `password_getter` 可调用对象而非直接的密码字符串，仅在实际认证时调用：

```python
import functools, getpass

Password(
    username="user",
    password_getter=functools.partial(getpass.getpass, "Password: "),
)
```

## SSH Agent 集成

paramiko 支持连接本地 SSH agent 获取密钥：

```python
agent = paramiko.Agent()
keys = agent.get_keys()
print(f"Agent has {len(keys)} keys")

for key in keys:
    print(f"  {key.get_name()} {key.get_bits()} bits: {key.get_base64()[:40]}...")
```

### AgentKey

`AgentKey` 继承 `PKey`，密钥材料存储在 agent 进程中，签名操作通过 agent 协议完成：

```python
for key in agent.get_keys():
    try:
        transport.auth_publickey("user", key)
        break
    except paramiko.AuthenticationException:
        continue
```

### Agent 转发

服务端模式下可通过 `request_forward_agent` 转发客户端的 agent 连接，`AgentRequestHandler` 处理转发请求。

### 平台支持

- **Linux/macOS**：通过 `$SSH_AUTH_SOCK` Unix socket 连接
- **Windows**：支持 OpenSSH agent 和 Pageant（`win_pageant.py`、`win_openssh.py`）

## 密钥文件格式

paramiko 支持的私钥格式：

| 格式 | 支持的密钥类型 |
|------|---------------|
| PEM (TraditionalOpenSSL) | RSA、ECDSA |
| OpenSSH (openssh-key-v1) | RSA、ECDSA、Ed25519 |

加载带密码的密钥：

```python
key = paramiko.RSAKey.from_private_key_file("id_rsa", password="keypass")

with open("id_ed25519", "rb") as f:
    key = paramiko.Ed25519Key.from_private_key(f, password="keypass")
```

## 证书认证

paramiko 支持 OpenSSH 证书认证：

```python
key = paramiko.RSAKey.from_private_key_file("id_rsa")
key.load_certificate("id_rsa-cert.pub")
transport.auth_publickey("user", key)
```

SSHClient 的 `key_filename` 参数可直接传入 `-cert.pub` 路径，自动匹配加载对应私钥。

## 认证异常体系

```
SSHException
└── AuthenticationException
    ├── PasswordRequiredException
    ├── BadAuthenticationType (含 allowed_types)
    ├── PartialAuthentication (内部使用)
    ├── UnableToAuthenticate
    └── AuthFailure (AuthStrategy 整体失败)
```

### BadAuthenticationType

```python
try:
    transport.auth_password("user", "pass")
except paramiko.BadAuthenticationType as e:
    print(f"Password not allowed. Try: {e.allowed_types}")
```

### PasswordRequiredException

密钥文件已加密但未提供密码时抛出。

## 相关概念

- [SSHClient 详解](/concepts/02-ssh-client.md)
- [Transport 底层传输](/concepts/03-transport.md)
- [密钥与主机密钥](/concepts/06-keys-and-hostkeys.md)
- [高级模式](/concepts/10-advanced-patterns.md)
- [命令执行示例](/examples/execute-commands.md)

[^paramiko-source]: paramiko 源码信源，见 [paramiko-source.md](/references/paramiko-source.md)。
