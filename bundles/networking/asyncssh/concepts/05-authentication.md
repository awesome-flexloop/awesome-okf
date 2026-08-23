---
type: Concept
title: 认证体系
description: 密码/公钥/键盘交互/GSSAPI/hostbased 认证、SSHClient 回调、authorized_keys、known_hosts
tags: [asyncssh, authentication, public-key, password, gssapi]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: asyncssh-source
    resource: /references/asyncssh-source.md
---

# 认证体系

## 认证框架

asyncssh 的认证框架定义于 `auth.py`，采用双端对称设计：

- `Auth`（auth.py:75）：认证基类，管理认证任务和包发送
- `ClientAuth`（auth.py:116）：客户端认证基类
- `ServerAuth`（auth.py:528）：服务端认证基类
- `register_auth_method()`（auth.py:948）：注册认证方法处理器

客户端和服务端各有 7 种认证方法实现：

| 方法 | 客户端类 | 服务端类 |
|------|---------|---------|
| none | `_ClientNullAuth` | `_ServerNullAuth` |
| GSSAPI-KEX | `_ClientGSSKexAuth` | `_ServerGSSKexAuth` |
| GSSAPI-MIC | `_ClientGSSMICAuth` | `_ServerGSSMICAuth` |
| hostbased | `_ClientHostBasedAuth` | `_ServerHostBasedAuth` |
| publickey | `_ClientPublicKeyAuth` | `_ServerPublicKeyAuth` |
| keyboard-interactive | `_ClientKbdIntAuth` | `_ServerKbdIntAuth` |
| password | `_ClientPasswordAuth` | `_ServerPasswordAuth` |

认证方法顺序由 `preferred_auth` 参数控制，默认使用 `get_supported_client_auth_methods()` 返回的顺序。

## 密码认证

### 客户端

最简单的方式：

```python
conn = await asyncssh.connect('host', username='user',
                              password='secret')
```

动态密码（通过 SSHClient 回调）：

```python
class MyClient(asyncssh.SSHClient):
    async def password_auth_requested(self):
        return await get_password_from_keyring()

conn = await asyncssh.connect('host', username='user',
                              client_factory=MyClient)
```

密码修改回调（服务器要求改密时触发）：

```python
class MyClient(asyncssh.SSHClient):
    async def password_change_requested(self, prompt, lang):
        return new_password

    def password_changed(self):
        print('密码已修改')

    def password_change_failed(self):
        print('密码修改失败')
```

### 服务端

```python
class MySSHServer(asyncssh.SSHServer):
    def begin_auth(self, username):
        return True  # 需要认证

    def password_auth_supported(self):
        return True

    def validate_password(self, username, password):
        return check_credentials(username, password)

await asyncssh.create_server(MySSHServer, '', 8022,
                             server_host_keys=['ssh_host_key'])
```

## 公钥认证

### 客户端

通过文件路径：

```python
conn = await asyncssh.connect('host', username='user',
                              client_keys=['~/.ssh/id_ed25519',
                                           '~/.ssh/id_rsa'])
```

通过 SSHKey 对象：

```python
key = asyncssh.read_private_key('~/.ssh/id_ed25519')
conn = await asyncssh.connect('host', username='user',
                              client_keys=[key])
```

加密私钥需提供 passphrase：

```python
key = asyncssh.read_private_key('~/.ssh/id_rsa',
                                passphrase='my passphrase')
```

动态密钥选择：

```python
class MyClient(asyncssh.SSHClient):
    async def public_key_auth_requested(self):
        keys = load_available_keys()
        return keys[0] if keys else None
```

### 服务端

使用 authorized_keys 文件：

```python
class MySSHServer(asyncssh.SSHServer):
    def begin_auth(self, username):
        return True

    def public_key_auth_supported(self):
        return True

    def validate_public_key(self, username, key):
        authorized_keys = asyncssh.read_authorized_keys(
            f'/home/{username}/.ssh/authorized_keys'
        )
        return authorized_keys.validate(key)
```

`SSHAuthorizedKeys` 类支持 OpenSSH authorized_keys 格式解析和密钥验证。

## 键盘交互认证

键盘交互（keyboard-interactive）是一种多轮问答认证方式，常用于 PAM、二次认证等场景。

### 客户端

```python
class MyClient(asyncssh.SSHClient):
    async def kbdint_auth_requested(self):
        return ''  # 返回子方法名，空字符串使用默认

    async def kbdint_challenge_received(self, name, instructions,
                                        lang, prompts):
        responses = []
        for prompt, echo in prompts:
            if echo:
                responses.append(input(prompt))
            else:
                responses.append(getpass.getpass(prompt))
        return responses
```

### 服务端

```python
class MySSHServer(asyncssh.SSHServer):
    def kbdint_auth_supported(self):
        return True

    async def get_kbdint_auth_methods(self, username):
        return ['']

    async def begin_kbdint_auth(self, username, lang, submethods):
        return [(b'Password: ', False)]

    async def perform_kbdint_auth(self, username, responses):
        return validate_password(username, responses[0])
```

## GSSAPI/Kerberos 认证

GSSAPI 认证需要安装 `python-gssapi` 包，支持两种模式：

- **GSSAPI-KEX**：在密钥交换阶段完成认证
- **GSSAPI-MIC**：在用户认证阶段使用 MIC 验证

```python
conn = await asyncssh.connect('host', username='user',
                              gss_auth=True,
                              gss_host='host.example.com',
                              gss_delegate_creds=True)
```

服务端验证：

```python
class MySSHServer(asyncssh.SSHServer):
    def validate_gss_principal(self, username, user_principal,
                               host_principal):
        return user_principal == f'{username}@EXAMPLE.COM'
```

## Hostbased 认证

Hostbased 认证允许客户端主机代表用户认证，类似 rhosts 机制：

```python
conn = await asyncssh.connect('host', username='user',
                              client_host_keysign=True,
                              client_host_pubkeys=['/etc/ssh/ssh_host_ed25519_key.pub'])
```

也可使用 `client_host_keypairs` 直接传入密钥对。

## SSH Agent

asyncssh 默认自动连接 SSH Agent：

- UNIX：`SSH_AUTH_SOCK` 环境变量指定的 socket
- Windows：Pageant（PuTTY Agent）

```python
agent = await asyncssh.connect_agent()
keys = await agent.get_keys()
for key in keys:
    print(key.get_algorithm(), key.get_comment())
agent.close()
```

指定 Agent 路径：

```python
conn = await asyncssh.connect('host', username='user',
                              agent_path='/tmp/agent.sock')
```

限制使用的 Agent 身份：

```python
conn = await asyncssh.connect('host', username='user',
                              agent_identities=['key_comment_1'])
```

Agent 转发（服务端需启用）：

```python
conn = await asyncssh.connect('host', username='user',
                              agent_forwarding=True)
```

## 已知主机密钥

### 默认行为

默认加载 `~/.ssh/known_hosts`，验证服务器主机密钥。验证失败抛出 `HostKeyNotVerifiable`。

### 禁用验证

```python
conn = await asyncssh.connect('host', known_hosts=None)
```

### 自定义 known_hosts

```python
conn = await asyncssh.connect('host',
                              known_hosts='/path/to/known_hosts')
```

### 编程式加载

```python
known_hosts = asyncssh.read_known_hosts('~/.ssh/known_hosts')
```

### 获取服务器密钥指纹

```python
key = await asyncssh.get_server_host_key('host')
print(key.get_fingerprint('sha256'))
```

### 主机密钥别名

当通过跳板机或 NAT 连接时，可使用 `host_key_alias` 指定 known_hosts 中匹配的主机名：

```python
conn = await asyncssh.connect('internal-ip',
                              host_key_alias='internal.example.com')
```

## authorized_keys

`SSHAuthorizedKeys` 解析 OpenSSH authorized_keys 文件：

```python
keys = asyncssh.read_authorized_keys('~/.ssh/authorized_keys')
```

`import_authorized_keys()` 从字符串加载：

```python
keys = asyncssh.import_authorized_keys(open('authorized_keys').read())
```

## 认证方法查询

连接前查询服务器支持的认证方法：

```python
methods = await asyncssh.get_server_auth_methods('host')
print(methods)  # ['publickey', 'password']
```

连接后也可查询：

```python
methods = conn.get_server_auth_methods()
```

## 无认证模式

服务端可对特定用户免认证：

```python
class MySSHServer(asyncssh.SSHServer):
    def begin_auth(self, username):
        return username != 'guest'  # guest 用户免认证
```

`begin_auth()` 返回 `False` 表示该用户无需认证，直接通过。

## 相关概念

- [密钥与证书](/concepts/06-keys-certificates.md) —— SSHKey 生成/读取/导出、SSHCertificate
- [异步连接详解](/concepts/02-async-connection.md) —— connect() 认证参数
- [服务端开发](/concepts/10-server.md) —— SSHServer 认证回调
- [paramiko 认证体系](../../paramiko/concepts/05-authentication.md)（同步认证对比）

[^asyncssh-source]: asyncssh 源码信源，见 [asyncssh-source.md](/references/asyncssh-source.md)。
