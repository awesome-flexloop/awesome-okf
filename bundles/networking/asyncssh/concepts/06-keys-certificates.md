---
type: Concept
title: 密钥与证书
description: SSHKey 生成/读取/导出、SSHCertificate 证书认证、SSH Agent、FIDO2 安全密钥、X.509
tags: [asyncssh, keys, certificates, ssh-key, ed25519, rsa]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: asyncssh-source
    resource: /references/asyncssh-source.md
---

# 密钥与证书

## SSHKey 类

`SSHKey` 定义于 `public_key.py:247`，是所有密钥类型的基类。asyncssh 支持的密钥算法包括：

| 算法名 | 密钥类型 | 说明 |
|--------|---------|------|
| `ssh-rsa` | RSA | 默认 2048 位，可配置 key_size/exponent |
| `ssh-dss` | DSA | 固定 1024 位（SHA1） |
| `ecdsa-sha2-nistp256` | ECDSA P-256 | 256 位 |
| `ecdsa-sha2-nistp384` | ECDSA P-384 | 384 位 |
| `ecdsa-sha2-nistp521` | ECDSA P-521 | 521 位 |
| `ssh-ed25519` | Ed25519 | 256 位，推荐 |
| `ssh-ed448` | Ed448 | 448 位 |
| `sk-ecdsa-sha2-nistp256@openssh.com` | FIDO2 ECDSA | 安全密钥 |
| `sk-ssh-ed25519@openssh.com` | FIDO2 Ed25519 | 安全密钥 |

## 生成密钥

使用模块级函数 `generate_private_key()`（public_key.py:3065）：

```python
import asyncssh

key = asyncssh.generate_private_key('ssh-ed25519', comment='my key')
```

RSA 密钥可指定参数：

```python
key = asyncssh.generate_private_key('ssh-rsa', key_size=4096,
                                    exponent=65537)
```

FIDO2 安全密钥参数：

```python
key = asyncssh.generate_private_key(
    'sk-ssh-ed25519@openssh.com',
    application='ssh:',
    user='AsyncSSH',
    resident=True,
    touch_required=True
)
```

## 读取密钥

### 从文件读取

```python
key = asyncssh.read_private_key('~/.ssh/id_ed25519')
key = asyncssh.read_private_key('~/.ssh/id_rsa', passphrase='secret')
pubkey = asyncssh.read_public_key('~/.ssh/id_ed25519.pub')
cert = asyncssh.read_certificate('~/.ssh/id_ed25519-cert.pub')
```

读取多密钥文件：

```python
keys = asyncssh.read_private_key_list('keys.pem')
pubkeys = asyncssh.read_public_key_list('authorized_keys')
certs = asyncssh.read_certificate_list('certs.pub')
```

### 从内存导入

```python
key = asyncssh.import_private_key(pem_data)
pubkey = asyncssh.import_public_key(openssh_pub_line)
cert = asyncssh.import_certificate(cert_data)
```

### 批量加载

```python
keypairs = asyncssh.load_keypairs(['~/.ssh/id_ed25519', '~/.ssh/id_rsa'])
public_keys = asyncssh.load_public_keys(['~/.ssh/authorized_keys'])
certificates = asyncssh.load_certificates(['ca-cert.pub'])
```

### 从 FIDO2 安全密钥加载 resident key

```python
keys = await asyncssh.load_resident_keys(pin='1234',
                                         application='ssh:')
```

### 从 PKCS#11 硬件加载

```python
keys = asyncssh.load_pkcs11_keys('/usr/lib/opensc-pkcs11.so',
                                 pin='1234')
```

## 导出密钥

### SSHKey 实例方法

```python
priv_openssh = key.export_private_key()
priv_pem = key.export_private_key('pkcs8-pem')
pub_openssh = key.export_public_key()
pub_rfc4716 = key.export_public_key('rfc4716')
```

`export_private_key(format_name='openssh', passphrase=None, cipher_name=None)` 支持的格式：
- `'openssh'`（默认）：OpenSSH 私钥格式
- `'pkcs8-pem'`：PKCS#8 PEM
- `'pkcs8-der'`：PKCS#8 DER

带口令加密：

```python
encrypted = key.export_private_key(passphrase='secret',
                                   cipher_name='aes256-ctr')
```

### 写入文件

```python
key.write_private_key('id_ed25519')
key.write_public_key('id_ed25519.pub')
key.append_private_key('all_keys', passphrase='secret')
key.append_public_key('authorized_keys')
```

## 密钥信息

```python
algorithm = key.get_algorithm()       # 'ssh-ed25519'
fingerprint = key.get_fingerprint('sha256')  # SHA256:...
comment = key.get_comment()
has_comment = key.has_comment()
pubkey = key.convert_to_public()       # 返回只含公钥的 SSHKey
```

## 签名与验证

```python
signature = key.sign(data, sig_algorithm)
signature = key.sign_ssh(data, b'ssh-ed25519')
key.verify_ssh(data, b'ssh-ed25519', signature)
is_valid = key.verify(data, signature)
```

## SSHCertificate

`SSHCertificate` 定义于 `public_key.py:1351`，支持 OpenSSH 证书和 X.509 证书两种体系。

### 生成 OpenSSH 用户证书

```python
ca_key = asyncssh.read_private_key('ca_key')
user_key = asyncssh.read_public_key('id_ed25519.pub')

cert = user_key.generate_user_certificate(
    ca_key,
    key_id='user@example.com',
    principals=['user'],
    valid_after=0,
    valid_before=0xFFFFFFFF,
    force_command=None,
    source_address=None,
    permit_x11_forwarding=True,
    permit_agent_forwarding=True,
    permit_port_forwarding=True,
    permit_pty=True,
    permit_user_rc=True
)

cert.write_certificate('id_ed25519-cert.pub')
```

### 生成主机证书

```python
host_cert = host_key.generate_host_certificate(
    ca_key,
    key_id='host.example.com',
    principals=['host.example.com', 'host']
)
```

### 证书链验证

```python
cert.validate(cert_type=asyncssh.OPENSSH_CERT_USER,
              principal='username')
```

### X.509 证书

```python
x509_cert = key.generate_x509_user_certificate(
    ca_key, 'CN=user',
    principals=['user@example.com'],
    valid_after=0, valid_before=...
)

chain = key.generate_x509_ca_certificate(ca_key, 'CN=My CA')
```

## 密钥在连接中的使用

### 客户端密钥

```python
conn = await asyncssh.connect('host', username='user',
                              client_keys=[key])
```

### 证书认证

```python
key = asyncssh.read_private_key('id_ed25519')
cert = asyncssh.read_certificate('id_ed25519-cert.pub')
key.append_certificate(cert)

conn = await asyncssh.connect('host', username='user',
                              client_keys=[key])
```

### 服务端主机密钥

```python
await asyncssh.create_server(
    MySSHServer, '', 22,
    server_host_keys=['ssh_host_ed25519_key']
)
```

多主机密钥：

```python
await asyncssh.create_server(
    MySSHServer, '', 22,
    server_host_keys=['ssh_host_ed25519_key',
                      'ssh_host_rsa_key']
)
```

## SSH Agent 编程

```python
agent = await asyncssh.connect_agent()

keys = await agent.get_keys()
for key in keys:
    print(f'{key.get_algorithm()} {key.get_comment()}')

await agent.close()
```

`SSHAgentKeyPair`（agent.py:108）是 SSHKeyPair 的子类，将签名操作委托给 Agent。

## 相关概念

- [认证体系](/concepts/05-authentication.md) —— 公钥认证流程
- [异步连接详解](/concepts/02-async-connection.md) —— client_keys 参数
- [服务端开发](/concepts/10-server.md) —— server_host_keys 配置
- [paramiko 密钥与主机密钥](../../paramiko/concepts/06-keys-and-hostkeys.md)（同步密钥 API 对比）

[^asyncssh-source]: asyncssh 源码信源，见 [asyncssh-source.md](/references/asyncssh-source.md)。
