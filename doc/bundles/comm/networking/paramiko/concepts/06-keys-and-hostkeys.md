---
type: Concept
title: 密钥与主机密钥
description: PKey 密钥体系、RSAKey/Ed25519Key/ECDSAKey 详解、HostKeys 主机密钥管理、MissingHostKeyPolicy 策略
tags: [paramiko, keys, hostkeys, security]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: paramiko-source
    resource: /references/paramiko-source.md
---

# 密钥与主机密钥

## PKey 基类

`PKey` 是所有公钥类型的抽象基类，定义了统一的密钥加载、签名、验签和序列化接口。

### 核心属性和方法

```python
key.get_name()
key.get_bits()
key.can_sign()
key.get_fingerprint()
key.get_base64()
key.asbytes()
key.sign_ssh_data(data, algorithm=None)
key.verify_ssh_sig(data, message)
key.load_certificate(cert_path)
```

- `get_name()`：返回算法标识字符串（如 `"ssh-rsa"`、`"ssh-ed25519"`）
- `get_bits()`：返回密钥位数
- `can_sign()`：是否持有私钥可签名
- `get_fingerprint()`：返回 MD5 指纹的 bytes
- `get_base64()`：返回 base64 编码的公钥 blob

### 加载密钥

```python
key = paramiko.RSAKey.from_private_key_file("/path/to/id_rsa", password=None)

with open("/path/to/id_ed25519", "rb") as f:
    key = paramiko.Ed25519Key.from_private_key(f, password="passphrase")

key = paramiko.ECDSAKey.from_private_key_file("/path/to/id_ecdsa")
```

### 从路径加载（v3.x+）

```python
key = paramiko.PKey.from_path(
    path="/path/to/key",
    password="optional-passphrase",
)
```

`from_path` 自动检测密钥类型。

### 根据类型字符串构造

```python
key = paramiko.PKey.from_type_string(key_type, key_bytes)
```

### 写出私钥

```python
key.write_private_key_file("/path/to/output", password="optional-pass")

with open("/path/to/output", "wb") as f:
    key.write_private_key(f, password=None)
```

### PublicBlob

`PublicBlob` 表示公钥 blob，可从文件、字符串或 Message 构造：

```python
blob = paramiko.PublicBlob.from_file("/path/to/key.pub")
blob = paramiko.PublicBlob.from_string("ssh-ed25519 AAAAC3Nz...")
print(blob.type_, blob.blob, blob.comment)
```

### UnknownKeyType

当遇到不认识的密钥算法时抛出 `UnknownKeyType`，包含 `key_type` 和 `key_bytes` 属性。

## RSAKey

RSA 密钥实现，算法名 `ssh-rsa`。

```python
key = paramiko.RSAKey.generate(bits=2048)
key = paramiko.RSAKey.from_private_key_file("~/.ssh/id_rsa")
```

### RSA-SHA2 算法

paramiko 支持 RFC 8332 定义的 RSA-SHA2 签名算法：

- `rsa-sha2-256`：使用 SHA-256 哈希
- `rsa-sha2-512`：使用 SHA-512 哈希

`RSAKey.HASHES` 字典映射算法名到哈希类。虽然密钥本身的 `name` 仍是 `"ssh-rsa"`，但在密钥交换和认证时会优先协商 rsa-sha2-512/256。

## Ed25519Key

Ed25519 密钥，算法名 `ssh-ed25519`，基于 pynacl 库实现。

```python
key = paramiko.Ed25519Key.from_private_key_file("~/.ssh/id_ed25519")
```

特点：

- 固定 256 位密钥长度
- 仅支持 OpenSSH 格式私钥（不支持 PEM 格式）
- OpenSSH 6.5+ 支持
- paramiko v2.2+ 支持

## ECDSAKey

ECDSA 密钥，支持 NIST P-256/P-384/P-521 曲线：

```python
key = paramiko.ECDSAKey.from_private_key_file("~/.ssh/id_ecdsa")
```

算法标识：

- `ecdsa-sha2-nistp256`（P-256）
- `ecdsa-sha2-nistp384`（P-384）
- `ecdsa-sha2-nistp521`（P-521）

内部通过 `_ECDSACurve` 和 `_ECDSACurveSet` 管理曲线配置，根据曲线长度自动选择 SHA-256/384/512 哈希。

## 私钥加密格式

PKey 支持两种私钥格式：

| 格式 | 标识 | 支持密钥 |
|------|------|---------|
| PEM | `BEGIN RSA/EC PRIVATE KEY` | RSA、ECDSA |
| OpenSSH | `BEGIN OPENSSH PRIVATE KEY` | RSA、ECDSA、Ed25519 |

PKey._CIPHER_TABLE 支持三种私钥加密：

- `AES-128-CBC`
- `AES-256-CBC`
- `DES-EDE3-CBC`（3DES）

## HostKeys 主机密钥管理

`HostKeys` 类管理 OpenSSH 风格的 known_hosts 文件，继承 `MutableMapping`。

### 基本用法

```python
host_keys = paramiko.HostKeys()

host_keys.load("/home/user/.ssh/known_hosts")

entry = host_keys.lookup("example.com")
if entry:
    for key_type, key in entry.items():
        print(f"  {key_type}: {key.get_fingerprint().hex()}")

host_keys.add("newhost.example.com", "ssh-ed25519", new_key)
host_keys.save("/home/user/.ssh/known_hosts")
```

### 数据结构

HostKeys 内部维护 `_entries` 列表，每个元素是 `HostKeyEntry`：

- `hostnames`：主机名列表（一行可包含多个逗号分隔的主机）
- `key`：`PKey` 实例

### 查询

```python
result = host_keys.lookup("example.com")
is_valid = host_keys.check("example.com", server_key)
```

- `lookup(hostname)` 返回 keytype→PKey 的字典（SubDict），未找到返回 None
- `check(hostname, key)` 返回布尔值，验证密钥是否匹配

### 字典接口

HostKeys 可像 dict 一样使用：

```python
host_keys["example.com"] = {"ssh-ed25519": key}
keys = host_keys["example.com"]
del host_keys["old-host.com"]
for hostname in host_keys:
    print(hostname)
```

### 哈希主机名

支持 OpenSSH 的 hashed known_hosts 格式（`|1|salt|hash`）：

```python
hashed = paramiko.HostKeys.hash_host("example.com")
```

`hash_host(hostname, salt=None)` 使用 HMAC-SHA1 生成哈希主机名，salt 为 None 时随机生成。

### HostKeyEntry

```python
entry = paramiko.hostkeys.HostKeyEntry.from_line(
    "example.com ssh-ed25519 AAAAC3Nz...", lineno=1
)
line = entry.to_line()
```

## 主机密钥验证策略

### MissingHostKeyPolicy

抽象基类，定义 `missing_host_key(client, hostname, key)` 方法：

- 返回 None = 接受密钥
- 抛出异常 = 拒绝连接

### RejectPolicy（默认）

```python
client.set_missing_host_key_policy(paramiko.RejectPolicy)
```

未知主机密钥时抛出 `SSHException("Server ... not found in known_hosts")`。这是最安全的默认行为。

### AutoAddPolicy

```python
client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
```

自动将新主机密钥添加到 `_host_keys` 并立即写入磁盘文件。适用于受控环境，但存在中间人攻击风险。

### WarningPolicy

```python
client.set_missing_host_key_policy(paramiko.WarningPolicy)
```

通过 `warnings.warn()` 发出警告但接受密钥。不写入磁盘。

### 自定义策略

```python
class FingerprintVerifyPolicy(paramiko.MissingHostKeyPolicy):
    TRUSTED_FINGERPRINTS = {
        "example.com": "a1:b2:c3:d4:...",
    }

    def missing_host_key(self, client, hostname, key):
        fp = key.get_fingerprint().hex()
        if hostname in self.TRUSTED_FINGERPRINTS:
            if fp == self.TRUSTED_FINGERPRINTS[hostname]:
                return
        raise paramiko.SSHException(
            f"Unknown host key for {hostname}: {fp}"
        )
```

## 两层主机密钥

SSHClient 维护两层主机密钥：

1. **system_host_keys**（只读）：通过 `load_system_host_keys()` 加载，通常来自系统 known_hosts
2. **host_keys**（可写）：通过 `load_host_keys()` 加载，AutoAddPolicy 添加的密钥存于此

connect() 验证顺序：
1. 先查 system_host_keys
2. 再查 host_keys
3. 都未命中时调用 missing_host_key_policy

## 安全最佳实践

1. **始终验证主机密钥**：生产环境使用 RejectPolicy 或自定义指纹验证
2. **避免 AutoAddPolicy**：仅在完全受控的测试环境使用
3. **使用 Ed25519 密钥**：比 RSA 更短更快更安全
4. **保护私钥密码**：使用 passphrase 加密私钥，通过环境变量或密钥管理服务传递
5. **定期更新 known_hosts**：主机密钥轮换时及时更新

## 相关概念

- [认证体系](05-authentication.md)
- [SSHClient 详解](02-ssh-client.md)
- [服务端开发](09-server.md)
- [高级模式](10-advanced-patterns.md)
- [基础连接示例](../examples/basic-connection.md)

[^paramiko-source]: paramiko 源码信源，见 [paramiko-source.md](../references/paramiko-source.md)。
