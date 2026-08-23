---
type: reference
title: "ZMTP 线协议：帧格式与握手完整索引"
description: "src/zmtp_engine.hpp/cpp、v2_encoder/decoder 中 ZMTP greeting 字节布局、握手状态机函数指针分发、安全机制选择、v2 编解码状态机、帧格式、心跳定时器"
tags: [libzmq, reference, zmtp, wire-protocol, codec]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  - path: "external/libs/remote/libzmq/src/zmtp_engine.hpp"
    facts: [F-058, F-059, F-061, F-063]
  - path: "external/libs/remote/libzmq/src/zmtp_engine.cpp"
    facts: [F-060, F-062]
  - path: "external/libs/remote/libzmq/src/v2_encoder.hpp"
    facts: [F-081]
  - path: "external/libs/remote/libzmq/src/v2_decoder.hpp"
    facts: [F-082]
  - path: "external/libs/remote/libzmq/src/i_encoder.hpp"
    facts: [F-083]
  - path: "external/libs/remote/libzmq/src/stream_engine_base.hpp"
    facts: [F-090, F-063]
  - path: "external/libs/remote/libzmq/src/i_engine.hpp"
    facts: [F-091]
  - path: "external/libs/remote/libzmq/src/msg.hpp"
    facts: [F-047]
---

# ZMTP 线协议：帧格式与握手完整索引

## 信源概述

| 信源 | 职责 |
|------|------|
| `src/zmtp_engine.hpp/cpp` | ZMTP 协议引擎、greeting 交换、握手状态机、安全机制创建 |
| `src/v2_encoder.hpp` | ZMTP/2.0 和 3.0 帧编码器（CRTP 状态机） |
| `src/v2_decoder.hpp` | ZMTP/2.0 和 3.0 帧解码器（支持零拷贝） |
| `src/encoder.hpp` | 编码器基类（CRTP）、零拷贝优化 |
| `src/stream_engine_base.hpp` | 流引擎基类、心跳定时器、编解码缓冲区管理 |
| `src/i_engine.hpp` | 引擎接口定义 |
| `src/i_encoder.hpp` / `i_decoder.hpp` | 编解码接口 |
| `src/msg.hpp` | 命令帧标志位定义 |

## 关键事实登记

### F-058：zmtp_engine_t 继承 stream_engine_base_t

**信源**：`src/zmtp_engine.hpp` L36-L106

```cpp
class zmtp_engine_t ZMQ_FINAL : public stream_engine_base_t {
    // ...
};
```

Greeting 大小常量：

| 常量 | 值 | 说明 |
|------|----|------|
| `signature_size` | 10 | 签名长度（0xFF + 8字节长度 + flags） |
| `v2_greeting_size` | 12 | ZMTP/2.0 greeting 大小 |
| `v3_greeting_size` | 64 | ZMTP/3.x greeting 大小 |

`stream_engine_base_t` 继承 `io_object_t` 和 `i_engine`，持有底层 fd、编解码器、安全机制、会话指针等。

### F-059：ZMTP 版本枚举

**信源**：`src/zmtp_engine.hpp` L22-L27

```cpp
enum {
    ZMTP_1_0 = 0,
    ZMTP_2_0 = 1,
    ZMTP_3_x = 3
};
```

注意没有 ZMTP_3_0 和 ZMTP_3_1 的独立枚举值——3.x 的 minor version 由 greeting 中的 minor 字节区分。

### F-060：Greeting 帧结构

**信源**：`src/zmtp_engine.cpp` L73-L90, L157-L198

**ZMTP/3.x Greeting（64 字节）**：

| 偏移 | 长度 | 字段 | 说明 |
|------|------|------|------|
| 0 | 1 | signature[0] | 0xFF（签名首字节） |
| 1-9 | 9 | signature[1..9] | 签名填充；第 10 字节（偏移9）的最低位为 1 表示版本化协议 |
| 10 | 1 | revision | 3 = ZMTP/3.x |
| 11 | 1 | minor version | 0 = ZMTP/3.0, 1 = ZMTP/3.1 |
| 12-31 | 20 | mechanism | 安全机制名称（"NULL"/"PLAIN"/"CURVE"/"GSSAPI"），null 填充 |
| 32 | 1 | as-server | 服务器端标志（CURVE 等使用） |
| 33-63 | 31 | filler | 填充字节（必须为 0） |

引擎启动时先发送 10 字节签名，随后根据对端版本发送 greeting 剩余部分。

**ZMTP/2.0 Greeting（12 字节）**：
- 字节 0-8：签名（0xFF + 8字节长度高位）
- 字节 9：flags（0x7f = 版本化）
- 字节 10：revision（1 = ZMTP/2.0）
- 字节 11：minor version

### F-061：握手通过函数指针状态机分发

**信源**：`src/zmtp_engine.hpp` L60-L70, `src/zmtp_engine.cpp` L200-L222

```cpp
typedef bool (zmtp_engine_t::*handshake_fun_t) ();
handshake_fun_t select_handshake_fun (bool unversioned,
                                       unsigned char revision,
                                       unsigned char minor);
```

选择逻辑：

| 条件 | 握手函数 | 说明 |
|------|---------|------|
| unversioned | `handshake_v1_0_unversioned` | 无版本协议（兼容旧版） |
| revision=0 | `handshake_v1_0` | ZMTP/1.0 |
| revision=1 | `handshake_v2_0` | ZMTP/2.0 |
| revision=3, minor=0 | `handshake_v3_0` | ZMTP/3.0（downgrade_sub=true） |
| revision=3, minor≥1 | `handshake_v3_1` | ZMTP/3.1（支持心跳） |

函数指针存储在 `_next_msg` 和 `_process_msg` 成员中，由 `stream_engine_base_t` 的 I/O 循环调用。

### F-062：ZMTP/3.x 握手创建安全机制

**信源**：`src/zmtp_engine.cpp` L317-L380

`handshake_v3_x()` 检查 `greeting_recv[12..31]` 中的机制名称是否与本地 `_options.mechanism` 匹配：

| 对端机制 | 本地角色 | 创建的机制对象 |
|---------|---------|---------------|
| "NULL" | — | `null_mechanism_t` |
| "PLAIN" | as-server=true | `plain_server_t` |
| "PLAIN" | as-server=false | `plain_client_t` |
| "CURVE" | as-server=true | `curve_server_t` |
| "CURVE" | as-server=false | `curve_client_t` |
| "GSSAPI" | — | `gssapi_*_t` |

若机制不匹配，触发协议错误 `ZMQ_PROTOCOL_ERROR_ZMTP_MECHANISM_MISMATCH`。

握手期间函数指针设置：
- `_next_msg` → `next_handshake_command`（机制生成握手消息）
- `_process_msg` → `process_handshake_command`（处理对端握手消息）

当 `mechanism.status() == ready` 时，调用 `session.engine_ready()` 进入正常消息传输阶段。

### F-063：心跳机制

**信源**：`src/zmtp_engine.hpp` L51-L53, L103, `src/stream_engine_base.hpp` L141-L149

`zmtp_engine_t` 声明：
```cpp
bool produce_ping_message (msg_t *msg_);
bool process_heartbeat_message (msg_t *msg_);
bool produce_pong_message (msg_t *msg_);
```

`stream_engine_base_t` 心跳定时器 ID：

| 常量 | 值 | 说明 |
|------|----|------|
| `heartbeat_ivl_timer_id` | 0x80 | 定时发送 PING |
| `heartbeat_timeout_timer_id` | 0x81 | 等待 PONG 超时 |
| `heartbeat_ttl_timer_id` | 0x82 | 心跳 TTL（过期丢弃连接） |

心跳在 ZMTP/3.1 层实现，不是 TCP keepalive。PING/PONG 使用命令帧（flag bit2=ping, bit3=pong）。

### F-081：v2_encoder_t 状态机

**信源**：`src/v2_encoder.hpp` L12-L26, `src/encoder.hpp` L27-L148

```cpp
class v2_encoder_t : public encoder_base_t<v2_encoder_t> {
    // ...
};
```

两个状态：

| 状态 | 说明 | 输出 |
|------|------|------|
| `size_ready` | 写入帧头 | flags(1) + size(1 或 9 字节) |
| `message_ready` | 写入消息体 | 消息数据 |

**帧头格式**：
- 短帧（size < 256）：`[flags][size(1 byte)]`
- 长帧（size ≥ 256）：`[flags][0xFF][size(8 bytes little-endian)]`

`_tmp_buf[10]` 暂存帧头（1 flags + 1 marker + 8 size = 10 字节）。

基类 `encoder_base_t<>` 使用 CRTP 实现：
- `encode()` 主循环根据当前状态调用子类的 `size_ready()`/`message_ready()`
- **零拷贝优化**：当待编码数据量 ≥ 缓冲区大小时，直接返回消息内容指针（`msg.data()`），避免从消息到缓冲区的 memcpy

### F-082：v2_decoder_t 状态机

**信源**：`src/v2_decoder.hpp` L14-L40

```cpp
class v2_decoder_t :
    public decoder_base_t<v2_decoder_t, shared_message_memory_allocator> {
    // ...
};
```

状态：

| 状态 | 说明 |
|------|------|
| `flags_ready` | 读取 1 字节 flags |
| `one_byte_size_ready` | 读取 1 字节短帧长度 |
| `eight_byte_size_ready` | 读取 8 字节长帧长度 |
| `message_ready` | 读取消息体 |

关键成员：
- `_in_progress`：当前正在组装的消息（`msg_t`）
- `_msg_flags`：从帧头读取的标志位
- `_zero_copy`：是否启用零拷贝模式（使用 `shared_message_memory_allocator` 共享内存池）

零拷贝接收时，decoder 从共享内存池分配数据缓冲区，直接从 socket fd 读取数据到该缓冲区，构造 zclmsg 消息。数据生命周期通过 content_t 的 ffn 回调归还到内存池。

### F-083：i_encoder / i_decoder 接口

**信源**：`src/i_encoder.hpp` L16-L28, `src/i_decoder.hpp` L15-L31

**i_encoder 接口**：
```cpp
struct i_encoder {
    virtual ~i_encoder () {}
    virtual void load_msg (msg_t *msg_) = 0;
    virtual size_t encode (unsigned char **data_, size_t size_) = 0;
};
```

**i_decoder 接口**：
```cpp
struct i_decoder {
    virtual ~i_decoder () {}
    virtual void get_buffer (unsigned char **data_, size_t size_) = 0;
    virtual void resize_buffer (size_t size_) = 0;
    virtual int decode (const unsigned char *data_, size_t size_,
                        size_t &processed_) = 0;
    virtual msg_t *msg () = 0;
};
```

`decode()` 返回值：
- `1`：消息完成
- `0`：需要更多数据
- `-1`：错误

### F-090：stream_engine_base_t 是流协议引擎基类

**信源**：`src/stream_engine_base.hpp` L28-L191

```cpp
class stream_engine_base_t : public io_object_t, public i_engine {
    // ...
};
```

关键成员：

| 成员 | 类型 | 说明 |
|------|------|------|
| `_s` | fd_t | 底层 socket fd |
| `_handle` | poller_t::handle_t | poller 句柄 |
| `_decoder` | i_decoder* | 帧解码器 |
| `_encoder` | i_encoder* | 帧编码器 |
| `_mechanism` | mechanism_t* | 安全机制 |
| `_session` | session_base_t* | 关联的会话 |
| `_socket` | socket_base_t* | 关联的 socket |
| `_handshaking` | bool | 握手中标志 |
| `_next_msg` | 函数指针 | 下一消息生成函数 |
| `_process_msg` | 函数指针 | 消息处理函数 |
| `_inpos`/`_insize` | 指针/大小 | 输入缓冲区位置和剩余 |
| `_outpos`/`_outsize` | 指针/大小 | 输出缓冲区位置和剩余 |
| `_input_stopped`/`_output_stopped` | bool | 输入/输出停止标志 |

### F-091：i_engine 接口

**信源**：`src/i_engine.hpp` L15-L52

```cpp
struct i_engine {
    enum error_reason_t {
        protocol_error,
        connection_error,
        timeout_error
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

- `plug()`：将引擎插入 I/O 线程，注册 fd 到 poller
- `has_handshake_stage()`：若返回 true，引擎在握手完成后必须调用 `session.engine_ready()`
- `restart_input/output()`：流控恢复时重新启动读/写
- `zap_msg_available()`：ZAP 认证管道有响应

### F-047：命令帧标志位

**信源**：`src/msg.hpp` L53-L67

ZMTP 命令帧使用 msg_t flags 标识：

| 标志 | 值 | 说明 |
|------|----|------|
| `more` | 1 | 多部分消息后续帧 |
| `command` | 2 | 命令帧（非用户数据） |
| `ping` | 4 | PING 心跳命令 |
| `pong` | 8 | PONG 心跳响应 |
| `subscribe` | 12 | SUBSCRIBE 订阅命令 |
| `cancel` | 16 | CANCEL 取消订阅 |
| `close_cmd` | 20 | CLOSE 连接关闭 |
| `credential` | 32 | 认证凭证消息 |

命令类型使用 bits 2-5（掩码 `0x1c`），等值比较而非位运算。SUBSCRIBE/CANCEL 命令在 XPUB/XSUB 之间的内置连接上传送订阅前缀。
