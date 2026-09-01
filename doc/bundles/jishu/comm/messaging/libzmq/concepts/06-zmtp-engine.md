---
type: concept
title: "ZMTP 协议引擎"
description: "zmtp_engine_t 的 greeting 64 字节帧结构、函数指针握手状态机（v1.0/v2.0/v3.0/v3.1）、安全机制创建与协商、心跳定时器、stream_engine_base 编解码缓冲区管理"
tags: [libzmq, zeromq, zmtp, engine, handshake, greeting, security]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [../references/zmtp-wire-protocol.md, ../references/msg.md]
  facts: [F-058, F-059, F-060, F-061, F-062, F-063, F-090, F-091, F-047]
---

# ZMTP 协议引擎

## 核心理解

ZMTP（ZeroMQ Message Transport Protocol）是 libzmq 的线协议，定义了连接建立、安全认证、消息帧传输的标准格式。`zmtp_engine_t` 是 ZMTP 协议的 C++ 实现，运行在 I/O 线程中，负责 greeting 交换、安全握手、帧编解码、心跳管理和实际的 socket 读写。

理解 zmtp_engine 的关键是：它使用**函数指针状态机**处理握手阶段，握手完成后切换为正常的消息收发状态。安全机制（NULL/PLAIN/CURVE/GSSAPI）作为可插拔组件，在握手期间创建并协商。

## 继承结构

```cpp
class zmtp_engine_t ZMQ_FINAL : public stream_engine_base_t { ... };
```

`zmtp_engine_t` 以 `ZMQ_FINAL` 标记不可继承（F-058），继承链为：

```
io_object_t（poller 事件适配器）
  └── stream_engine_base_t（流引擎基类：fd管理、编解码缓冲区、心跳）
        └── zmtp_engine_t（ZMTP 协议：greeting、握手、安全机制）
```

`stream_engine_base_t` 同时实现 `i_engine` 接口（F-090, F-091），后者定义了引擎的生命周期契约。

## Greeting 帧结构

ZMTP/3.x greeting 共 64 字节（F-060），是连接建立后双方交换的第一帧：

```
偏移   长度   字段              说明
0      1      signature[0]      0xFF（签名首字节，固定）
1-9    9      signature[1..9]   签名填充；字节9的最低位=1 表示版本化协议
10     1      revision          协议版本：3 = ZMTP/3.x
11     1      minor version     次版本：0 = 3.0, 1 = 3.1
12-31  20     mechanism         安全机制名（"NULL"/"PLAIN"/"CURVE"/"GSSAPI"），null 填充
32     1      as-server         服务器端标志（CURVE 等机制使用）
33-63  31     filler            填充字节（必须为 0）
```

### 签名段（10 字节）

签名首字节 0xFF 是 ZMTP 的魔数，用于快速识别非 ZMTP 连接（如 HTTP 请求）。第 10 字节（偏移 9）的最低位为 1 表示这是版本化协议，而非无版本的 ZMTP/1.0。

### 版本字段

- revision=3, minor=0 → ZMTP/3.0
- revision=3, minor=1 → ZMTP/3.1（支持心跳）

### 机制名称

20 字节的安全机制名，以 null 填充：
- "NULL"（4 字符 + 16 null）
- "PLAIN"（5 字符 + 15 null）
- "CURVE"（5 字符 + 15 null）
- "GSSAPI"（6 字符 + 14 null）

引擎启动时先发送 10 字节签名，然后根据对端版本发送 greeting 的剩余部分。

## ZMTP 版本枚举

```cpp
enum {
    ZMTP_1_0 = 0,
    ZMTP_2_0 = 1,
    ZMTP_3_x = 3
};
```

注意没有 ZMTP_3_0 和 ZMTP_3_1 的独立枚举——3.x 的 minor version 由 greeting 中的 minor 字节区分，在握手函数选择时处理（F-059）。

## 握手状态机

握手通过函数指针分发（F-061），`select_handshake_fun()` 根据对端版本返回成员函数指针：

```cpp
typedef bool (zmtp_engine_t::*handshake_fun_t) ();

handshake_fun_t select_handshake_fun (bool unversioned,
                                       unsigned char revision,
                                       unsigned char minor);
```

选择逻辑：

| 条件 | 握手函数 | 特点 |
|------|---------|------|
| unversioned（无签名） | `handshake_v1_0_unversioned` | 兼容最旧版，无 greeting |
| revision=0 | `handshake_v1_0` | ZMTP/1.0，有 routing_id 帧 |
| revision=1 | `handshake_v2_0` | ZMTP/2.0，12 字节 greeting |
| revision=3, minor=0 | `handshake_v3_0` | ZMTP/3.0，downgrade_sub=true |
| revision=3, minor≥1 | `handshake_v3_1` | ZMTP/3.1，支持心跳 |

### 握手时序

```
客户端                                    服务端
  │                                         │
  │──── 10字节签名 (0xFF...) ──────────────►│
  │◄─── 10字节签名 ─────────────────────────│
  │                                         │
  │──── 剩余 greeting (revision/mechanism) ►│
  │◄─── 剩余 greeting ─────────────────────│
  │                                         │
  │  select_handshake_fun() 确定版本        │
  │                                         │
  │==== 安全机制握手（如果是 ZMTP/3.x）====│
  │                                         │
  │──── READY 命令 (元数据) ───────────────►│
  │◄─── READY 命令 ────────────────────────│
  │                                         │
  │  mechanism.status() == ready            │
  │  → session.engine_ready()               │
  │                                         │
  │==== 正常消息传输 =======================│
```

### v3.0 与 v3.1 的区别

- **v3.0**：设置 `downgrade_sub=true`，订阅处理降级（兼容旧版行为）
- **v3.1**：支持心跳（PING/PONG），订阅处理更高效

## 安全机制创建

ZMTP/3.x 握手检查对端 greeting 中的机制名是否与本地配置匹配（F-062）：

| 对端机制 | as-server | 创建的对象 |
|---------|-----------|-----------|
| "NULL" | — | `null_mechanism_t` |
| "PLAIN" | true | `plain_server_t` |
| "PLAIN" | false | `plain_client_t` |
| "CURVE" | true | `curve_server_t` |
| "CURVE" | false | `curve_client_t` |
| "GSSAPI" | — | `gssapi_server_t`/`gssapi_client_t` |

若机制不匹配，触发协议错误 `ZMQ_PROTOCOL_ERROR_ZMTP_MECHANISM_MISMATCH`，连接终止。

### NULL 机制

最简单的机制，无认证、无加密。但仍交换 READY 命令携带元数据（socket 类型、routing_id 等）。适用于可信网络。

### PLAIN 机制

明文用户名密码认证。客户端发送 HELLO 命令（username + password），服务端验证后回复 WELCOME/ERROR。不加密数据，应配合 IPSec/TLS 隧道使用。

### CURVE 机制

基于椭圆曲线 Curve25519 的安全机制，提供：
- 服务器公钥认证（防止中间人）
- 客户端公钥认证（基于 ZAP 或配置的密钥）
- 端到端加密（消息内容加密）
- 完美前向保密（每次连接生成临时密钥对）

CURVE 密钥：
- 原始 32 字节二进制（F-068）
- Z85 编码为 40 字节 ASCII
- 三个密钥：public_key、secret_key、server_key

### GSSAPI 机制

基于 Kerberos/GSSAPI 的企业级认证，支持加密和数据完整性保护。适用于已有 Kerberos 基础设施的环境。

### 机制函数指针

握手期间，stream_engine_base 的函数指针被设置为：

```cpp
_next_msg = &zmtp_engine_t::next_handshake_command;
_process_msg = &zmtp_engine_t::process_handshake_command;
```

- `next_handshake_command()`：从 mechanism 获取下一条握手消息（HELLO/WELCOME/READY/INITIATE 等）发送给对端
- `process_handshake_command()`：处理从对端收到的握手消息，委托给 mechanism

当 `mechanism.status() == ready` 时：
1. 函数指针切换为正常消息处理
2. 调用 `session.engine_ready()` 通知会话
3. 开始用户数据传输

## stream_engine_base_t

`stream_engine_base_t` 是所有流协议引擎的基类（F-090），提供：

### 核心成员

| 成员 | 类型 | 说明 |
|------|------|------|
| `_s` | fd_t | 底层 TCP socket fd |
| `_handle` | poller_t::handle_t | poller 注册句柄 |
| `_decoder` | i_decoder* | 帧解码器 |
| `_encoder` | i_encoder* | 帧编码器 |
| `_mechanism` | mechanism_t* | 安全机制 |
| `_session` | session_base_t* | 关联会话 |
| `_socket` | socket_base_t* | 关联 socket |
| `_handshaking` | bool | 握手中标志 |
| `_next_msg` | 函数指针 | 下一消息生成函数 |
| `_process_msg` | 函数指针 | 消息处理函数 |

### 编解码缓冲区

| 成员 | 说明 |
|------|------|
| `_inpos` | 输入缓冲区当前读位置 |
| `_insize` | 输入缓冲区剩余字节数 |
| `_outpos` | 输出缓冲区当前写位置 |
| `_outsize` | 输出缓冲区剩余字节数 |

I/O 循环：
1. 读：从 fd 读取数据到 decoder 缓冲区 → decoder 解析帧 → 组装 msg_t → 通过 pipe 发给 session
2. 写：从 pipe 取 msg_t → encoder 编码到缓冲区 → 写入 fd

### 流控

| 标志 | 说明 |
|------|------|
| `_input_stopped` | 输入已停止（pipe HWM 满） |
| `_output_stopped` | 输出已停止（TCP 发送缓冲区满） |

- 当 pipe 满（HWM）时，停止从 fd 读取（`_input_stopped=true`，从 poller 注销 POLLIN）
- pipe 恢复时通过 `restart_input()` 重新注册
- TCP 发送缓冲区满时停止编码（`_output_stopped=true`），poller 通知可写时恢复

## 心跳机制

ZMTP/3.1 支持应用层心跳（F-063），在 zmtp_engine 中声明：

```cpp
bool produce_ping_message (msg_t *msg_);
bool process_heartbeat_message (msg_t *msg_);
bool produce_pong_message (msg_t *msg_);
```

stream_engine_base 管理三个心跳定时器：

| 定时器 ID | 值 | 说明 |
|----------|----|------|
| `heartbeat_ivl_timer_id` | 0x80 | 定时发送 PING |
| `heartbeat_timeout_timer_id` | 0x81 | 等待 PONG 超时 |
| `heartbeat_ttl_timer_id` | 0x82 | 心跳 TTL（过期丢弃连接） |

心跳流程：
```
每 heartbeat_ivl 毫秒:
  → 发送 PING 命令帧
  → 启动 timeout 定时器

收到 PING:
  → 回复 PONG

收到 PONG:
  → 取消 timeout 定时器

timeout 到期:
  → 连接无响应，终止连接
```

心跳是 ZMTP/3.1 层的机制，不是 TCP keepalive。相关选项：
- `ZMQ_HEARTBEAT_IVL`：PING 发送间隔
- `ZMQ_HEARTBEAT_TIMEOUT`：PONG 超时
- `ZMQ_HEARTBEAT_TTL`：心跳生存时间（用于代理场景）

## i_engine 接口

`i_engine` 定义引擎的生命周期契约（F-091）：

```cpp
struct i_engine {
    enum error_reason_t {
        protocol_error,     // 协议错误（greeting 无效、机制不匹配）
        connection_error,   // 连接错误（RST、超时）
        timeout_error       // 超时（握手超时、心跳超时）
    };

    virtual bool has_handshake_stage () = 0;
    virtual void plug (io_thread_t *io_thread_,
                       session_base_t *session_) = 0;
    virtual void terminate () = 0;
    virtual bool restart_input () = 0;
    virtual void restart_output () = 0;
    virtual void zap_msg_available () = 0;
    virtual const endpoint_uri_pair_t &get_endpoint () const = 0;
};
```

- `plug()`：引擎插入 I/O 线程，注册 fd，开始握手
- `has_handshake_stage()`：返回 true 表示有握手阶段，握手完成后必须调用 `session.engine_ready()`
- `terminate()`：终止引擎，关闭 fd，清理资源
- `restart_input()`：pipe 流控恢复后重新启动读取
- `restart_output()`：TCP 可写后重新启动发送
- `zap_msg_available()`：ZAP 认证管道有响应

## 消息帧格式

ZMTP 帧由 v2_encoder/v2_decoder 处理：

- **短帧**（长度 < 256）：`[flags:1][size:1][body]`
- **长帧**（长度 ≥ 256）：`[flags:1][0xFF:1][size:8 little-endian][body]`

flags 位：
- bit 0（MORE）：多部分消息后续帧
- bit 1（COMMAND）：命令帧
- bit 2（LONG）：长帧标志（0xFF 标记）

命令帧（flag bit1=1）承载 ZMTP 内部控制消息，其 body 格式为：
- 命令名长度（1 字节）
- 命令名（"SUBSCRIBE"/"CANCEL"/"PING"/"PONG"/"READY" 等）
- 命令数据

## 相关概念

- [会话与连接生命周期](05-session.md) — engine 通过 plug 插入 session，握手完成后 engine_ready
- [编解码与帧格式](12-encoder-decoder.md) — v2_encoder/decoder 状态机和零拷贝
- [消息与引用计数](03-message.md) — msg_t 命令帧标志位
- [套接字选项体系](09-options.md) — heartbeat/mechanism/curve 密钥等选项
- [传输层](10-transport.md) — TCP fd 如何传递给 engine
