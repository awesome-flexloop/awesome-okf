---
type: reference
title: "options_t：套接字选项完整索引"
description: "src/options.hpp 中 options_t 结构体全字段、HWM/linger/timeout/heartbeat/security 选项分类、CURVE 密钥长度、setsockopt/getsockopt 分支表"
tags: [libzmq, reference, options, setsockopt]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  - path: "external/libs/remote/libzmq/src/options.hpp"
    facts: [F-067, F-068]
  - path: "external/libs/remote/libzmq/include/zmq.h"
    facts: [F-007, F-008]
---

# options_t：套接字选项完整索引

## 信源概述

| 信源 | 职责 |
|------|------|
| `src/options.hpp` | options_t 结构体定义，存储所有套接字可配置选项 |
| `src/options.cpp` | setsockopt/getsockopt 实现、选项默认值初始化 |
| `include/zmq.h` | ZMQ_* 选项常量定义、安全机制枚举 |

`options_t` 是一个纯数据结构体（plain old data），在 socket 创建时初始化，在 bind/connect 时被复制到 session 和 pipe，使各层无需同步即可访问选项。

## 关键事实登记

### F-067：options_t 存储所有套接字选项

**信源**：`src/options.hpp` L34-L301

完整字段分类如下：

#### 流控选项

| 字段 | 类型 | 默认值 | 对应 ZMQ 选项 | 说明 |
|------|------|--------|--------------|------|
| `sndhwm` | int | 1000 | `ZMQ_SNDHWM` | 发送高水位 |
| `rcvhwm` | int | 1000 | `ZMQ_RCVHWM` | 接收高水位 |
| `conflate` | bool | false | `ZMQ_CONFLATE` | 只保留最新消息（忽略 HWM） |

#### 线程与亲和性

| 字段 | 类型 | 默认值 | 对应 ZMQ 选项 | 说明 |
|------|------|--------|--------------|------|
| `affinity` | uint64_t | 0 | `ZMQ_AFFINITY` | I/O 线程亲和性掩码（0=全部） |
| `thread_safe` | bool | false | — | 是否线程安全（CLIENT/SERVER 为 true） |

#### 标识与路由

| 字段 | 类型 | 默认值 | 对应 ZMQ 选项 | 说明 |
|------|------|--------|--------------|------|
| `routing_id` | char[256] | 空 | `ZMQ_ROUTING_ID` | 套接字路由标识（最大 255 字节） |
| `type` | int8_t | — | `ZMQ_TYPE`（只读） | 套接字类型 |
| `immediate` | bool | false | `ZMQ_IMMEDIATE` | 仅在连接完成后排队消息 |

#### 多播/Pgm

| 字段 | 类型 | 默认值 | 对应 ZMQ 选项 |
|------|------|--------|--------------|
| `rate` | int | 100 | `ZMQ_RATE` |
| `recovery_ivl` | int | 10000 | `ZMQ_RECOVERY_IVL` |
| `recovery_ivl_msec` | int | — | `ZMQ_RECOVERY_IVL_MSEC` |
| `multicast_loop` | bool | true | `ZMQ_MULTICAST_LOOP` |
| `multicast_maxmsg` | int | — | `ZMQ_MULTICAST_MAXMSG` |

#### 网络缓冲区

| 字段 | 类型 | 默认值 | 对应 ZMQ 选项 |
|------|------|--------|--------------|
| `sndbuf` | int | 0（系统默认） | `ZMQ_SNDBUF` |
| `rcvbuf` | int | 0（系统默认） | `ZMQ_RCVBUF` |
| `tos` | int | 0 | `ZMQ_TOS` |
| `priority` | int | 0 | `ZMQ_PRIORITY` |
| `backlog` | int | 100 | `ZMQ_BACKLOG` |

#### 超时与逗留

| 字段 | 类型 | 默认值 | 对应 ZMQ 选项 | 说明 |
|------|------|--------|--------------|------|
| `linger` | atomic_value_t | -1 | `ZMQ_LINGER` | 关闭时逗留时间（毫秒，-1=永久） |
| `rcvtimeo` | int | -1 | `ZMQ_RCVTIMEO` | 接收超时（-1=永久阻塞） |
| `sndtimeo` | int | -1 | `ZMQ_SNDTIMEO` | 发送超时（-1=永久阻塞） |
| `reconnect_ivl` | int | 100 | `ZMQ_RECONNECT_IVL` | 重连初始间隔（毫秒） |
| `reconnect_ivl_max` | int | 0 | `ZMQ_RECONNECT_IVL_MAX` | 重连最大间隔（0=无上限） |
| `handshake_ivl` | int | 30000 | `ZMQ_HANDSHAKE_IVL` | 握手超时（毫秒，默认 30 秒） |

#### 心跳（ZMTP/3.1）

| 字段 | 类型 | 默认值 | 对应 ZMQ 选项 | 说明 |
|------|------|--------|--------------|------|
| `heartbeat_interval` | int | 0 | `ZMQ_HEARTBEAT_IVL` | 心跳间隔（毫秒，0=禁用心跳） |
| `heartbeat_timeout` | int | 0 | `ZMQ_HEARTBEAT_TIMEOUT` | 心跳超时（毫秒） |
| `heartbeat_ttl` | int | 0 | `ZMQ_HEARTBEAT_TTL` | 心跳生存时间（毫秒） |

#### 消息限制

| 字段 | 类型 | 默认值 | 对应 ZMQ 选项 |
|------|------|--------|--------------|
| `maxmsgsize` | int64_t | -1（无限制） | `ZMQ_MAXMSGSIZE` |
| `in_batch_size` | int | — | `ZMQ_IN_BATCH_SIZE` |
| `out_batch_size` | int | — | `ZMQ_OUT_BATCH_SIZE` |

#### 网络协议

| 字段 | 类型 | 默认值 | 对应 ZMQ 选项 |
|------|------|--------|--------------|
| `ipv6` | bool | false | `ZMQ_IPV6` |
| `filter` | bool | false | `ZMQ_FILTER` |

#### 安全

| 字段 | 类型 | 默认值 | 对应 ZMQ 选项 | 说明 |
|------|------|--------|--------------|------|
| `mechanism` | int | ZMQ_NULL | `ZMQ_MECHANISM`（只读） | 安全机制 |
| `as_server` | bool | false | `ZMQ_AS_SERVER` | 服务器端角色 |
| `plain_username` | std::string | 空 | `ZMQ_PLAIN_USERNAME` | PLAIN 用户名 |
| `plain_password` | std::string | 空 | `ZMQ_PLAIN_PASSWORD` | PLAIN 密码 |
| `curve_public_key` | uint8_t[32] | 全 0 | `ZMQ_CURVE_PUBLICKEY` | CURVE 公钥（原始 32 字节） |
| `curve_secret_key` | uint8_t[32] | 全 0 | `ZMQ_CURVE_SECRETKEY` | CURVE 私钥（原始 32 字节） |
| `curve_server_key` | uint8_t[32] | 全 0 | `ZMQ_CURVE_SERVERKEY` | CURVE 服务器公钥 |
| `gssapi_principal` | std::string | 空 | `ZMQ_GSSAPI_PRINCIPAL` |
| `gssapi_service_principal` | std::string | 空 | `ZMQ_GSSAPI_SERVICE_PRINCIPAL` |
| `gssapi_plaintext` | bool | false | `ZMQ_GSSAPI_PLAINTEXT` |

#### 零拷贝

| 字段 | 类型 | 默认值 | 对应 ZMQ 选项 | 说明 |
|------|------|--------|--------------|------|
| `zero_copy` | bool | true | — | 是否启用零拷贝接收（context 级别） |

#### ROUTER 特定

| 字段 | 类型 | 默认值 | 对应 ZMQ 选项 |
|------|------|--------|--------------|
| `mandatory` | bool | false | `ZMQ_ROUTER_MANDATORY` |
| `probe_router` | bool | false | `ZMQ_PROBE_ROUTER` |
| `handover` | bool | false | `ZMQ_ROUTER_HANDOVER` |

#### 其他

| 字段 | 类型 | 默认值 | 对应 ZMQ 选项 |
|------|------|--------|--------------|
| `connected` | bool | false | —（内部状态） |
| `pipe_hwm` | bool | false | `ZMQ_XPUB_VERBOSE` 等内部使用 |
| `require_fds` | bool | false | — |

### F-068：CURVE 密钥长度

**信源**：`src/options.hpp` L28-L30

```cpp
#define CURVE_KEYSIZE 32
#define CURVE_KEYSIZE_Z85 40
```

| 表示形式 | 长度 | 说明 |
|---------|------|------|
| 原始二进制密钥 | 32 字节 | 256 位椭圆曲线密钥 |
| Z85 编码密钥 | 40 字节 | ASCII 可打印编码（4/5 膨胀比） |

options 中存储的三个密钥均为原始 32 字节：
- `curve_public_key[32]`：本端公钥
- `curve_secret_key[32]`：本端私钥
- `curve_server_key[32]`：对端服务器公钥（客户端使用）

Z85 编码是 ZeroMQ 自定义的 Base85 变体，字符集为 `0-9a-zA-Z.-:+=^!/*?&<>()[]{}@%$#`。应用程序通过 `zmq_z85_encode()`/`zmq_z85_decode()` 在两种格式间转换。

### F-007：套接字选项常量（公共 API）

**信源**：`include/zmq.h` L276-L351

常用选项常量值速查：

| 常量 | 值 | 数据类型 | 读写 |
|------|----|---------|------|
| `ZMQ_AFFINITY` | 4 | uint64 | 读写 |
| `ZMQ_ROUTING_ID` | 5 | binary | 读写 |
| `ZMQ_SUBSCRIBE` | 6 | binary | 只写 |
| `ZMQ_UNSUBSCRIBE` | 7 | binary | 只写 |
| `ZMQ_SNDBUF` | 11 | int | 读写 |
| `ZMQ_RCVBUF` | 12 | int | 读写 |
| `ZMQ_RCVMORE` | 13 | int | 只读 |
| `ZMQ_FD` | 14 | fd | 只读 |
| `ZMQ_EVENTS` | 15 | int | 只读 |
| `ZMQ_TYPE` | 16 | int | 只读 |
| `ZMQ_LINGER` | 17 | int | 读写 |
| `ZMQ_SNDHWM` | 23 | int | 读写 |
| `ZMQ_RCVHWM` | 24 | int | 读写 |
| `ZMQ_RCVTIMEO` | 27 | int | 读写 |
| `ZMQ_SNDTIMEO` | 28 | int | 读写 |
| `ZMQ_RECONNECT_IVL` | 30 | int | 读写 |
| `ZMQ_BACKLOG` | 32 | int | 读写 |
| `ZMQ_ROUTER_MANDATORY` | 33 | int | 读写 |
| `ZMQ_PROBE_ROUTER` | 51 | int | 读写 |
| `ZMQ_MECHANISM` | 43 | int | 只读 |
| `ZMQ_PLAIN_USERNAME` | 46 | string | 读写 |
| `ZMQ_PLAIN_PASSWORD` | 47 | string | 读写 |
| `ZMQ_CURVE_PUBLICKEY` | 48 | binary | 读写 |
| `ZMQ_CURVE_SECRETKEY` | 49 | binary | 读写 |
| `ZMQ_CURVE_SERVERKEY` | 50 | binary | 读写 |
| `ZMQ_HEARTBEAT_IVL` | 75 | int | 读写 |
| `ZMQ_HEARTBEAT_TTL` | 76 | int | 读写 |
| `ZMQ_HEARTBEAT_TIMEOUT` | 77 | int | 读写 |
| `ZMQ_CONFLATE` | 54 | int | 读写 |
| `ZMQ_HANDSHAKE_IVL` | 66 | int | 读写 |
| `ZMQ_MAXMSGSIZE` | 22 | int64 | 读写 |
| `ZMQ_IPV6` | 42 | int | 读写 |
| `ZMQ_IMMEDIATE` | 39 | int | 读写 |

### F-008：安全机制常量

**信源**：`include/zmq.h` L362-L365

```c
#define ZMQ_NULL   0
#define ZMQ_PLAIN  1
#define ZMQ_CURVE  2
#define ZMQ_GSSAPI 3
```

| 机制 | 认证 | 加密 | 适用场景 |
|------|------|------|---------|
| NULL | 无 | 无 | 可信网络/测试 |
| PLAIN | 用户名密码（明文） | 无 | 配合 IPSec/TLS 隧道 |
| CURVE | 公钥认证 | 加密 | 公网安全通信（推荐） |
| GSSAPI | Kerberos 票据 | 可选 | 企业 Kerberos 环境 |

`ZMQ_MECHANISM` 选项（值 43）为只读，返回当前协商后的安全机制。在 ZMTP/3.x 握手完成前返回 `ZMQ_NULL`。
