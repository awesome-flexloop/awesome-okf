---
type: concept
title: "套接字选项体系"
description: "options_t 结构体全字段分类（流控/超时/安全/心跳/网络）、HWM/LINGER/TIMEOUT 的行为语义、CURVE 密钥与安全机制协商、选项在 bind/connect 时的值复制时机"
tags: [libzmq, zeromq, options, setsockopt, hwm, linger, curve, heartbeat, security]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [../references/options.md, ../references/zmq-h-api.md]
  facts: [F-007, F-008, F-067, F-068]
---

# 套接字选项体系

## 核心理解

`options_t` 是一个纯数据结构体，存储套接字的所有可配置选项。它在 socket 创建时初始化，在 bind/connect 时被**值复制**到 session 和 pipe——这意味着对端无需同步即可访问选项，因为每个连接持有独立的副本。

理解选项的关键是：
1. 选项在**连接建立时快照**，后续修改不影响已建立的连接
2. inproc 连接时，两端选项需要协调（HWM 取两端之和）
3. 部分选项是只读的（`ZMQ_TYPE`、`ZMQ_RCVMORE`、`ZMQ_MECHANISM`、`ZMQ_FD`、`ZMQ_EVENTS`）
4. 部分选项必须在 bind/connect **之前**设置（安全密钥、routing_id 等）

## options_t 结构体

`options_t` 定义在 `src/options.hpp`（F-067），包含数十个字段。以下按功能分类说明。

## 流控选项

### 高水位（HWM）

```cpp
int sndhwm = 1000;  // ZMQ_SNDHWM
int rcvhwm = 1000;  // ZMQ_RCVHWM
```

HWM 限制管道中未确认的消息数：
- `sndhwm`：发送高水位——出站管道最多缓存多少条消息
- `rcvhwm`：接收高水位——入站管道最多缓存多少条消息
- 默认值均为 1000
- 设为 0 表示无限制

**重要**：HWM 是**消息数**限制，不是字节数。对于 inproc 连接，管道 HWM 为两端 sndhwm + rcvhwm 之和。

HWM 触发时：
- 阻塞发送：`zmq_send` 阻塞直到有空间（或超时）
- 非阻塞发送：返回 EAGAIN
- PUB/SUB：HWM 满时**静默丢弃**消息（PUB 不阻塞）

### conflate 模式

```cpp
bool conflate = false;  // ZMQ_CONFLATE
```

启用后 pipe 使用 `ypipe_conflate_t`，只保留最新消息，忽略 HWM。仅支持 DEALER/PUSH/PULL/PUB/SUB。适用于"只关心最新值"的场景（如行情、传感器）。

## 超时与逗留

### LINGER

```cpp
atomic_value_t linger = -1;  // ZMQ_LINGER
```

socket 关闭时等待未发送消息发送完成的时间（毫秒）：
- `-1`（默认）：永久等待，直到所有消息发送或 ctx_term
- `0`：立即丢弃未发送消息
- `>0`：等待指定毫秒后丢弃

LINGER 使用 `atomic_value_t` 而非普通 int，因为它可能被 I/O 线程读取（终止时）。

### 发送/接收超时

```cpp
int rcvtimeo = -1;  // ZMQ_RCVTIMEO
int sndtimeo = -1;  // ZMQ_SNDTIMEO
```

- `-1`（默认）：永久阻塞
- `0`：非阻塞
- `>0`：等待指定毫秒后返回 EAGAIN

超时期间 socket 仍会处理 mailbox 命令（如 activate_write），因此超时不是简单的 sleep。

### 重连间隔

```cpp
int reconnect_ivl = 100;      // ZMQ_RECONNECT_IVL（毫秒）
int reconnect_ivl_max = 0;    // ZMQ_RECONNECT_IVL_MAX（0=无上限）
```

主动连接（connect）断开后自动重连：
- 初始间隔 100ms
- 每次失败间隔翻倍（指数退避），直到达到 reconnect_ivl_max
- 间隔加入随机抖动避免重连风暴
- 成功连接后重置间隔

## 心跳选项（ZMTP/3.1）

```cpp
int heartbeat_interval = 0;   // ZMQ_HEARTBEAT_IVL（毫秒，0=禁用）
int heartbeat_timeout = 0;    // ZMQ_HEARTBEAT_TIMEOUT
int heartbeat_ttl = 0;        // ZMQ_HEARTBEAT_TTL
```

| 选项 | 说明 |
|------|------|
| `ZMQ_HEARTBEAT_IVL` | PING 发送间隔。0 禁用心跳 |
| `ZMQ_HEARTBEAT_TIMEOUT` | 未收到 PONG 的超时时间，超时后断开 |
| `ZMQ_HEARTBEAT_TTL` | 心跳的生存时间，用于代理场景（经代理后过期） |

心跳是 ZMTP/3.1 应用层机制，不是 TCP keepalive。当对端不支持 3.1 时心跳无效。

建议配置：
```c
zmq_setsockopt(socket, ZMQ_HEARTBEAT_IVL, &(int){5000}, sizeof(int));
zmq_setsockopt(socket, ZMQ_HEARTBEAT_TIMEOUT, &(int){10000}, sizeof(int));
```

## 握手超时

```cpp
int handshake_ivl = 30000;  // ZMQ_HANDSHAKE_IVL（默认 30 秒）
```

TCP 连接建立后 ZMTP 握手必须在此时间内完成，否则断开连接。适用于对端接受了 TCP 连接但不发送 ZMTP greeting 的场景（如负载均衡器健康检查、HTTP 客户端误连）。

## 安全选项

### 安全机制

```cpp
int mechanism = ZMQ_NULL;  // ZMQ_MECHANISM（只读）
bool as_server = false;    // ZMQ_AS_SERVER
```

`ZMQ_MECHANISM` 是只读选项，返回当前协商的安全机制（NULL/PLAIN/CURVE/GSSAPI），在握手完成前返回 NULL。

### PLAIN 认证

```cpp
std::string plain_username;  // ZMQ_PLAIN_USERNAME
std::string plain_password;  // ZMQ_PLAIN_PASSWORD
```

明文用户名/密码认证，不加密。必须配合 ZAP handler 或 CURVE 安全层使用，不应在公网单独使用。

### CURVE 加密

```cpp
uint8_t curve_public_key[32];  // ZMQ_CURVE_PUBLICKEY
uint8_t curve_secret_key[32];  // ZMQ_CURVE_SECRETKEY
uint8_t curve_server_key[32];  // ZMQ_CURVE_SERVERKEY
```

CURVE 是 libzmq 推荐的公网安全机制（F-068）：

| 密钥 | 长度 | 说明 |
|------|------|------|
| 原始二进制 | 32 字节 | Curve25519 密钥 |
| Z85 编码 | 40 字节 | ASCII 可打印编码 |

- 客户端设置：public_key + secret_key + server_key（服务器公钥）
- 服务器设置：secret_key + as_server=true（不设置 server_key）
- Z85 是 ZeroMQ 自定义 Base85 编码，字符集：`0-9a-zA-Z.-:+=^!/*?&<>()[]{}@%$#`
- 使用 `zmq_z85_encode()`/`zmq_z85_decode()` 转换

CURVE 提供：
- 服务器身份认证（通过 server_key 防止中间人）
- 客户端身份认证（通过 ZAP handler 验证公钥）
- 端到端加密（所有消息内容加密）
- 完美前向保密（每次连接生成临时密钥对）

### GSSAPI

```cpp
std::string gssapi_principal;
std::string gssapi_service_principal;
bool gssapi_plaintext = false;
```

Kerberos/GSSAPI 企业级认证，适用于已有 Kerberos 基础设施的环境。

## 网络选项

### IPv6

```cpp
bool ipv6 = false;  // ZMQ_IPV6
```

启用后 socket 同时支持 IPv4 和 IPv6 连接。默认仅 IPv4。

### 缓冲区

```cpp
int sndbuf = 0;  // ZMQ_SNDBUF（0=系统默认）
int rcvbuf = 0;  // ZMQ_RCVBUF（0=系统默认）
```

设置内核 TCP 发送/接收缓冲区大小（SO_SNDBUF/SO_RCVBUF）。0 表示使用操作系统默认值。

### 其他

| 选项 | 字段 | 默认 | 说明 |
|------|------|------|------|
| `ZMQ_TOS` | tos | 0 | 服务类型（DSCP） |
| `ZMQ_PRIORITY` | priority | 0 | SO_PRIORITY |
| `ZMQ_BACKLOG` | backlog | 100 | listen() backlog |
| `ZMQ_RECONNECT_STOP` | — | — | 停止重连的条件 |

## 标识与路由

### ROUTING_ID

```cpp
char routing_id[256] = {};  // ZMQ_ROUTING_ID（最大 255 字节）
```

socket 的路由标识，用于 ROUTER 寻址：
- 必须在 connect/bind 前设置
- 未设置时由引擎自动生成 UUID
- ROUTER 接收消息时前置对端的 routing_id 帧

### IMMEDIATE

```cpp
bool immediate = false;  // ZMQ_IMMEDIATE
```

启用后，只有在连接完成（握手成功）后才将消息排队到该连接。默认 false 允许消息在连接建立前排队（在 pipe 中缓存），适用于断线重连场景；设为 true 可避免向不可达连接发送消息。

### ROUTER 特定

```cpp
bool mandatory = false;    // ZMQ_ROUTER_MANDATORY
bool probe_router = false; // ZMQ_PROBE_ROUTER
bool handover = false;     // ZMQ_ROUTER_HANDOVER
```

- `mandatory`：发送到未知 routing_id 时返回 EHOSTUNREACH 而非静默丢弃
- `probe_router`：新连接时自动发送空分隔帧通知 ROUTER
- `handover`：routing_id 冲突时新连接接管旧连接

## 消息限制

```cpp
int64_t maxmsgsize = -1;  // ZMQ_MAXMSGSIZE（-1=无限制）
int in_batch_size;        // ZMQ_IN_BATCH_SIZE
int out_batch_size;       // ZMQ_OUT_BATCH_SIZE
```

- `maxmsgsize`：限制入站消息大小，超限则断开连接
- batch size：控制网络读写批量大小，影响延迟和吞吐

## 零拷贝

```cpp
bool zero_copy = true;  // context 级别，非 socket 选项
```

零拷贝接收在 context 级别设置（`ZMQ_ZERO_COPY_RECV`），默认启用。启用后 decoder 使用共享内存池，数据直接从 fd 读到池缓冲区，避免内核到用户空间的额外拷贝。

## 选项的复制时机

选项值在连接建立时被复制到多个层：

```
socket.options
  │
  ├─ bind("tcp://...")
  │   └─ listener 持有 options 副本
  │       └─ 每个 accept 的 session/engine/pipe 持有副本
  │
  ├─ connect("tcp://...")
  │   └─ connecter 持有 options 副本
  │       └─ session/engine/pipe 持有副本
  │
  └─ connect("inproc://...")
      └─ endpoint_t 注册 {socket, options} 到 ctx
          └─ pipepair 使用两端 options 协调 HWM
```

**关键影响**：
1. bind/connect 后修改选项不影响已建立的连接
2. 必须在 bind/connect **之前**设置安全密钥、routing_id、HWM 等
3. inproc 连接时 bind 方的 options 被复制到 endpoint_t，connect 方读取它来协调 pipe 参数
4. `linger` 使用 atomic_value_t，因为它可能在连接建立后被 socket 公共 API 修改，I/O 线程终止时需要读取最新值

## 只读选项

部分选项只能通过 `zmq_getsockopt()` 读取，不能设置：

| 选项 | 说明 |
|------|------|
| `ZMQ_TYPE` | socket 类型（ZMQ_PUB/ZSUB 等） |
| `ZMQ_RCVMORE` | 当前接收的消息是否有后续帧 |
| `ZMQ_FD` | 边缘触发信号 fd（用于外部 poll） |
| `ZMQ_EVENTS` | 当前就绪事件（ZMQ_POLLIN/POLLOUT） |
| `ZMQ_MECHANISM` | 当前安全机制 |
| `ZMQ_LAST_ENDPOINT` | 最后绑定的端点 |

`ZMQ_FD` 是一个特殊的信号 fd：当 socket 状态变化（从不可读变为可读等）时 fd 变为可读。它是**边缘触发**的，必须在 fd 可读后用 `ZMQ_EVENTS` 查询实际状态，且必须读取所有可用消息后才会再次触发。

## 上下文选项 vs 套接字选项

部分选项在上下文级别设置：

| 上下文选项 | 值 | 默认 | 说明 |
|-----------|----|------|------|
| `ZMQ_IO_THREADS` | 1 | 1 | I/O 线程数 |
| `ZMQ_MAX_SOCKETS` | 2 | 1023 | 最大 socket 数 |
| `ZMQ_THREAD_PRIORITY` | 3 | — | I/O 线程优先级 |
| `ZMQ_THREAD_SCHED_POLICY` | 4 | — | 调度策略 |
| `ZMQ_MAX_MSGSZ` | 5 | INT_MAX | 最大消息大小 |
| `ZMQ_MSG_T_SIZE` | 6 | 64 | zmq_msg_t 大小 |
| `ZMQ_ZERO_COPY_RECV` | — | true | 零拷贝接收 |
| `ZMQ_IPV6` | — | false | IPv6（context 级别） |

上下文选项必须在创建任何 socket 之前设置。

## 相关概念

- [套接字基类](/concepts/02-socket-base.md) — socket 构造时接收 options，xsetsockopt 处理模式特定选项
- [上下文与基础设施](/concepts/01-context.md) — 上下文级别选项
- [管道与流控](/concepts/04-pipe.md) — HWM 选项在 pipe 层实现
- [ZMTP 协议引擎](/concepts/06-zmtp-engine.md) — 心跳和安全机制选项
- [消息模式实现](/concepts/11-patterns.md) — CONFLATE/MANDATORY 等模式特定选项
- [传输层](/concepts/10-transport.md) — reconnect/buffer 等网络选项
