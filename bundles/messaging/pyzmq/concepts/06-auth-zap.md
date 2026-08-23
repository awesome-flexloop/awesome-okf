---
type: concept
title: "认证与 ZAP：ZeroMQ 安全协议"
description: "pyzmq auth 模块的 ZAP 协议实现、Authenticator 基类、allow/deny 地址过滤、PLAIN/CURVE/GSSAPI 认证机制、ThreadAuthenticator 后台线程、AsyncioAuthenticator 协程版、证书加载与 curve_user_id 映射"
tags: [pyzmq, zeromq, auth, zap, curve, plain, security, authentication]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [../references/constants-enums.md, ../references/error-hierarchy.md]
  facts: [F-098, F-099, F-100, F-101, F-102, F-103, F-104, F-105]
---

# 认证与 ZAP：ZeroMQ 安全协议

## 核心理解

ZeroMQ 的认证通过 **ZAP（ZeroMQ Authentication Protocol，ZeroMQ 认证协议）** 实现——这是一个简单的请求-应答协议，运行在 `inproc://zeromq.zap.01` 端点上。当一个 socket 配置了安全机制（PLAIN/CURVE/GSSAPI）并接收到连接时，libzmq 自动向 ZAP 端点发送认证请求，由认证器（Authenticator）决定允许或拒绝。

pyzmq 在 `zmq.auth` 模块中提供了完整的 ZAP 认证器实现，支持三种运行模式：同步基类（可自定义）、后台线程版（`ThreadAuthenticator`）和 asyncio 协程版（`AsyncioAuthenticator`）。它还提供了 NULL 地址白名单/黑名单、PLAIN 用户名密码认证、CURVE 公钥认证和证书管理功能。

## ZAP 协议概述

ZAP 是一个简单的同步请求-应答协议：

```
连接请求到达
  │
  ├─ libzmq 检查 socket 的安全机制配置
  │
  ├─ 构造 ZAP 请求消息（multipart）：
  │   [0] version     = b"1.0"
  │   [1] request_id  = 唯一请求 ID
  │   [2] domain      = 安全域（socket 的 ZAP_DOMAIN 选项）
  │   [3] address     = 对端 IP 地址
  │   [4] identity    = 对端 socket identity
  │   [5] mechanism   = 安全机制名（NULL/PLAIN/CURVE）
  │   [6+] credentials = 机制相关凭证（用户名/密码/公钥等）
  │
  ├─ 发送到 inproc://zeromq.zap.01（REP 端点）
  │
  └─ 等待 ZAP 应答：
      [0] version     = b"1.0"
      [1] request_id  = 与请求对应
      [2] status_code = b"200"（允许）/ b"400"（拒绝）
      [3] status_text = 描述
      [4] user_id     = 认证后的用户标识（可选）
      [5] metadata    = 扩展元数据（可选）
```

认证器在 `inproc://zeromq.zap.01` 上绑定一个 REP socket，接收并回复所有 ZAP 请求。

## Authenticator 基类

### F-098：初始化与 ZAP 端点

```python
auth = zmq.auth.Authenticator(ctx)
auth.start()
```

`Authenticator` 基类在 `start()` 中：
- 创建 `zmq.REP` socket
- 绑定到 `inproc://zeromq.zap.01`（ZAP 标准端点）
- 设置 `linger=1`（关闭时最多等待 1 毫秒）

`zmq.auth.__init__` 仅从 `.base` 与 `.certs` 子模块导出公共 API。

### F-099：地址白名单/黑名单

```python
auth.allow("127.0.0.1")       # 允许指定地址
auth.allow("192.168.1.0/24") # 允许网段
auth.deny("10.0.0.1")        # 拒绝指定地址
```

- `allow(*addresses)`：添加允许的地址
- `deny(*addresses)`：添加拒绝的地址
- 两者互斥——同时使用抛 `ValueError`

**NULL 机制下**：未被 deny 的地址默认允许（或仅在 allow 列表中的地址允许，如果设置了 allow）。
**PLAIN/CURVE 机制下**：即使地址在 allow 列表中，仍需通过凭证认证。地址过滤只是第一层。

### F-100：PLAIN 认证

```python
auth.configure_plain(
    domain='*',                    # 安全域，'*' 表示默认
    passwords={                    # 用户名→密码字典
        "admin": "secret123",
        "user": "password456",
    }
)
```

PLAIN 机制使用明文用户名密码（适合在已加密的内部网络或配合 CURVE 使用）。密码按 domain 存入 `self.passwords` 字典。ZAP 请求中的用户名密码与字典比对。

### F-100：CURVE 认证

```python
auth.configure_curve(
    domain='*',
    location='/path/to/known_clients/',  # 公钥证书目录
    # 或 location='*' 表示 CURVE_ALLOW_ANY（允许所有客户端）
)
```

CURVE 是 ZeroMQ 的椭圆曲线加密认证机制，提供双向认证和端到端加密。公钥证书从指定目录加载 `*.key` 文件。`'*'` 表示 `CURVE_ALLOW_ANY`——允许所有持有有效 CURVE 密钥对的客户端（不验证公钥身份）。

### F-101：ZAP 请求处理

`handle_zap_message(msg)` 是核心 async 方法：

```python
async def handle_zap_message(self, msg):
    version = msg[0]
    request_id = msg[1]
    domain = msg[2]
    address = msg[3]
    identity = msg[4]
    mechanism = msg[5]
    credentials = msg[6:]

    if mechanism == b"NULL":
        # 检查 allow/deny
        if self._is_allowed(address):
            await self._send_zap_reply(request_id, b"200", b"OK")
        else:
            await self._send_zap_reply(request_id, b"400", b"Denied")

    elif mechanism == b"PLAIN":
        username = credentials[0]
        password = credentials[1]
        # 验证用户名密码
        ...

    elif mechanism == b"CURVE":
        client_public_key = credentials[0]
        # 调用 _authenticate_curve 验证公钥
        allowed = await self._authenticate_curve(domain, client_public_key)
        ...

    elif mechanism == b"GSSAPI":
        # GSSAPI/Kerberos 认证
        ...
```

认证结果通过 `_send_zap_reply` 回复：
- **200**：认证成功，可附加 user_id 和 metadata
- **400**：认证失败，连接被拒绝

### F-102：curve_user_id 自定义映射

```python
class MyAuthenticator(zmq.auth.Authenticator):
    def curve_user_id(self, client_public_key):
        # 默认返回公钥的 z85 编码
        # 可覆写为自定义映射（如查数据库返回用户名）
        return self.user_db.get(client_public_key, "anonymous")
```

默认实现返回公钥的 z85 编码（Z85 是 ZeroMQ 的 Base85 文本编码）作为 User-Id。子类可覆写此方法实现公钥到用户名/角色的自定义映射。返回的 user_id 会通过 ZAP 应答传给服务端 socket，通过 `frame['User-Id']` 访问。

## ThreadAuthenticator

### F-103：后台线程认证器

`ThreadAuthenticator` 在后台 daemon 线程中运行 ZAP 处理，适合同步应用：

```python
auth = zmq.auth.ThreadAuthenticator(ctx)
auth.start()  # 启动后台线程
auth.allow("127.0.0.1")
auth.configure_curve(domain='*', location='./keys')
# ... 主线程正常使用 ZeroMQ
auth.stop()  # 停止后台线程
```

**内部实现**：

1. `start()` 创建 PAIR pipe（`inproc://{id(self)}.inproc`）用于线程间控制
2. 启动 `AuthenticationThread`（daemon 线程）
3. 线程内新建独立的 asyncio event loop
4. 用 `zmq.asyncio.Poller` 同时监听：
   - pipe（接收停止命令）
   - zap_socket（接收 ZAP 请求）
5. 收到 ZAP 请求时调用 `handle_zap_message` 处理

使用独立 asyncio loop 的原因：ZAP 处理的 `handle_zap_message` 是 async 方法（CURVE 认证可能涉及异步证书加载），而主线程可能没有运行 asyncio loop。后台线程的独立 loop 使同步应用也能使用 async 认证逻辑。

## AsyncioAuthenticator

### F-104：协程认证器

`AsyncioAuthenticator` 在当前 asyncio event loop 中启动 ZAP 处理任务，适合 asyncio 应用：

```python
async def main():
    auth = zmq.auth.AsyncioAuthenticator(ctx)
    auth.start()  # 在当前 loop 中启动 __handle_zap 任务
    auth.allow("127.0.0.1")
    auth.configure_plain(domain='*', passwords={"user": "pass"})
    # ... asyncio 应用运行中
    auth.stop()   # 取消任务、注销 poller、关闭 socket
```

**内部实现**：
- `start()` 在当前 loop 中创建 `__handle_zap` asyncio 任务
- 用 `zmq.asyncio.Poller` 监听 zap_socket
- `stop()` 取消任务、从 poller 注销、关闭 zap_socket

与 `ThreadAuthenticator` 的区别：不创建新线程，直接在调用者的 asyncio loop 中运行，更轻量但要求调用者在 async 上下文中。

## 证书管理

### F-105：证书加载与创建

**加载证书**：

```python
from zmq.auth.certs import load_certificates

# 从目录加载所有 *.key 公钥证书
# 返回 {public_key_bytes: True} 字典
allowed_keys = load_certificates(directory='./known_clients')
```

`load_certificates(directory='.')`：
1. glob 目录下所有 `*.key` 文件
2. 调用 `load_certificate` 提取公钥
3. 返回 `{public_key_bytes: True}` 字典（用字典模拟集合）

**创建证书**：

```python
from zmq.auth.certs import create_certificates

# 生成密钥对并写入文件
create_certificates(
    key_dir='./keys',
    name='server',
    metadata=None,  # 可选的元数据字典
)
# 生成：
#   ./keys/server.key        — 公钥证书（可分发）
#   *.key_secret             — 私钥文件（保密！）
```

内部使用 `zmq.curve_keypair()` 生成 CURVE 密钥对，公钥写入 `.key` 文件，私钥写入 `.key_secret` 文件。

## 认证配置完整示例

### 服务端（CURVE）

```python
import zmq
import zmq.auth

ctx = zmq.Context.instance()

# 启动认证器
auth = zmq.auth.ThreadAuthenticator(ctx)
auth.start()
auth.configure_curve(domain='*', location='./allowed_clients')

# 创建 CURVE 服务端 socket
server = ctx.socket(zmq.PUSH)
server.curve_publickey, server.curve_secretkey = zmq.curve_keypair()
server.curve_server = True  # 启用 CURVE 服务端模式
server.bind("tcp://*:5555")
```

### 客户端（CURVE）

```python
client = ctx.socket(zmq.PULL)
client.curve_publickey, client.curve_secretkey = zmq.curve_keypair()
client.curve_serverkey = server_public_key  # 服务端公钥
client.connect("tcp://localhost:5555")
```

## 安全机制对比

| 机制 | 加密 | 认证 | 适用场景 |
|------|------|------|---------|
| NULL | 无 | 地址过滤 | 可信内网 |
| PLAIN | 无 | 用户名密码 | 已加密通道（VPN/TLS） |
| CURVE | 有（椭圆曲线） | 公钥认证 | 公网/不可信网络 |
| GSSAPI | 有（Kerberos） | Kerberos 票据 | 企业 Kerberos 环境 |

## 相关概念

- [整体架构与双后端](/concepts/00-architecture-dual-backend.md) — curve_keypair 在 public_api 中
- [异步与 asyncio](/concepts/05-async-future-asyncio.md) — AsyncioAuthenticator 与 asyncio.Poller
- [Socket sugar 语法层](/concepts/02-socket-sugar.md) — CURVE/PLAIN 套接字选项设置
- [常量枚举参考](/references/constants-enums.md) — SecurityMechanism 枚举
- [Frame 与消息](/concepts/03-frame-message.md) — frame['User-Id'] 访问认证用户
