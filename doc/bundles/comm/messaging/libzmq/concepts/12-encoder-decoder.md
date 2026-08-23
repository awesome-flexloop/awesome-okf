---
type: concept
title: "编解码与帧格式"
description: "v2_encoder_t CRTP 状态机（size_ready/message_ready）、v2_decoder_t 零拷贝接收、ZMTP 长短帧格式、i_encoder/i_decoder 接口、编码器零拷贝优化、命令帧类型（subscribe/ping/pong）"
tags: [libzmq, zeromq, encoder, decoder, zmtp, frame, crtp, zero-copy, codec]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [../references/zmtp-wire-protocol.md, ../references/msg.md]
  facts: [F-081, F-082, F-083, F-047, F-090]
---

# 编解码与帧格式

## 核心理解

编解码器（encoder/decoder）负责在内存中的 `msg_t` 对象与 ZMTP 线格式字节流之间转换。`v2_encoder_t` 和 `v2_decoder_t` 服务于 ZMTP/2.0 和 3.0 协议，使用**CRTP（奇异递归模板模式）状态机**高效处理帧的序列化和反序列化。

理解编解码的关键是：
1. 帧格式简单：flags 字节 + 长度（1 或 8 字节）+ body
2. 编码器有零拷贝优化——大数据块直接返回消息指针而非拷贝
3. 解码器支持零拷贝接收——数据从 fd 直接读到共享内存池
4. 命令帧（SUBSCRIBE/PING/PONG 等）与用户数据帧复用相同的帧格式，通过 flags 区分

## ZMTP 帧格式

### 帧结构

每个 ZMTP 消息帧由帧头和帧体组成：

```
短帧（body 长度 < 256 字节）:
┌───────┬──────┬───────────┐
│ flags │ size │   body    │
│ 1 byte│1 byte│ 0-255 字节│
└───────┴──────┴───────────┘

长帧（body 长度 ≥ 256 字节）:
┌───────┬──────┬───────────┬───────────┐
│ flags │ 0xFF │   size    │   body    │
│ 1 byte│1 byte│  8 bytes  │ N 字节    │
└───────┴──────┴───────────┴───────────┘
```

- 短帧的 size 字段为 1 字节，最大值 255
- 长帧的 size 字段为 8 字节小端序 uint64，第一字节为 0xFF 标记
- body 可以是用户数据或命令数据

### flags 字节

```
bit 0: MORE      — 多部分消息后续帧
bit 1: COMMAND   — 命令帧（非用户数据）
bit 2: LONG      — 长帧标志（实际由 0xFF 标记位判断）
bit 3-7: 保留
```

注意：在 v2 编解码器中，长帧标志不在 flags 字节中，而是通过 size 字段第一字节是否为 0xFF 判断。flags 字节只有 bit0（MORE）和 bit1（COMMAND）有意义。

### 多部分消息

多部分消息通过 MORE 标志链接：

```
┌─────────┬─────────┬─────────┐
│ frame 1 │ frame 2 │ frame 3 │
│ MORE=1  │ MORE=1  │ MORE=0  │
└─────────┴─────────┴─────────┘
```

- MORE=1 表示后面还有帧
- MORE=0 表示这是最后一帧
- 多部分消息是原子的——对等方要么收到所有帧，要么一帧都收不到

## i_encoder / i_decoder 接口

### i_encoder（F-083）

```cpp
struct i_encoder {
    virtual ~i_encoder () {}
    virtual void load_msg (msg_t *msg_) = 0;
    virtual size_t encode (unsigned char **data_, size_t size_) = 0;
};
```

- `load_msg(msg)`：加载要编码的消息
- `encode(&data, size)`：获取下一块要发送的数据
  - `data` 输出：指向数据缓冲区的指针
  - `size` 输入：可用缓冲区大小
  - 返回值：数据块大小
  - 引擎将返回的数据写入 TCP fd

### i_decoder（F-083）

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

- `get_buffer(&data, size)`：获取解码器的数据接收缓冲区
  - 引擎将从 fd 读到的数据直接写入此缓冲区
- `resize_buffer(size)`：调整缓冲区大小
- `decode(data, size, &processed)`：解析接收到的数据
  - 返回 `1`：消息完成
  - 返回 `0`：需要更多数据
  - 返回 `-1`：错误
- `msg()`：获取解码完成的消息

## v2_encoder_t：编码状态机

`v2_encoder_t` 使用 CRTP 继承 `encoder_base_t<v2_encoder_t>`（F-081）：

```cpp
class v2_encoder_t : public encoder_base_t<v2_encoder_t> {
    enum { size_ready, message_ready } _state;
    unsigned char _tmp_buf[10];  // 帧头暂存（1+1+8=10）
};
```

### 两个状态

| 状态 | 说明 | 输出 |
|------|------|------|
| `size_ready` | 准备写入帧头 | flags + size（2 或 10 字节） |
| `message_ready` | 准备写入消息体 | msg 数据 |

### 编码流程

```
load_msg(msg)
  → _state = size_ready
  → 根据 msg.size() 准备帧头:
      size < 256: _tmp_buf = [flags, size]
      size ≥ 256: _tmp_buf = [flags, 0xFF, size(8字节LE)]

encode(&data, bufsize):
  while true:
    if _state == size_ready:
      data = &_tmp_buf[offset]
      if 帧头已全部输出:
        _state = message_ready
      return 帧头剩余字节数

    if _state == message_ready:
      // 零拷贝优化（见下文）
      if 消息剩余 ≥ bufsize:
        data = msg.data() + offset  // 直接返回消息内存
        return bufsize
      else:
        data = msg.data() + offset
        size = 消息剩余字节数
        _state = size_ready  // 消息写完，准备下一帧头
        load next msg (if any)
        return size
```

### 零拷贝优化

`encoder_base_t` 的零拷贝优化是性能关键（F-081）：

当待编码数据量 **≥ 输出缓冲区大小**时，编码器不将消息数据拷贝到临时缓冲区，而是直接返回消息内容的指针（`msg.data() + offset`）。引擎通过 `writev()` 或直接 `send()` 将此指针的数据写入 fd，避免了一次 memcpy。

这对大消息（如文件传输、视频帧）显著减少内存带宽使用。小消息仍然走拷贝路径（因为缓冲区足以容纳整个消息）。

### CRTP 设计

CRTP（`encoder_base_t<v2_encoder_t>`）使得基类可以直接调用子类的 `size_ready()`/`message_ready()` 方法而无需虚函数开销。编译器可以内联这些调用，实现零开销抽象。不同版本的编码器（v2、v3_1）只需实现不同的状态处理方法。

## v2_decoder_t：解码状态机

`v2_decoder_t` 继承 `decoder_base_t<v2_decoder_t, shared_message_memory_allocator>`（F-082）：

```cpp
class v2_decoder_t : public decoder_base_t<...> {
    enum {
        flags_ready,
        one_byte_size_ready,
        eight_byte_size_ready,
        message_ready
    } _state;

    unsigned char _tmpbuf[10];   // 帧头暂存
    msg_t _in_progress;          // 当前组装的消息
    unsigned char _msg_flags;    // 从帧头解析的 flags
    bool _zero_copy;             // 零拷贝模式
};
```

### 四个状态

| 状态 | 说明 | 读取字节 |
|------|------|---------|
| `flags_ready` | 读取 flags 字节 | 1 |
| `one_byte_size_ready` | 读取短帧长度 | 1 |
| `eight_byte_size_ready` | 读取长帧长度 | 8 |
| `message_ready` | 读取消息体 | N 字节 |

### 解码流程

```
收到数据 → decode():
  while 有数据:
    switch _state:
      case flags_ready:
        _msg_flags = data[0]
        if data[0] & 0x02:  // COMMAND flag
          标记为命令帧
        _state = one_byte_size_ready
        消费 1 字节

      case one_byte_size_ready:
        if data[0] == 0xFF:
          _state = eight_byte_size_ready  // 长帧
        else:
          _msg_size = data[0]
          准备消息缓冲区
          _state = message_ready
        消费 1 字节

      case eight_byte_size_ready:
        读取 8 字节小端 uint64 → _msg_size
        准备消息缓冲区
        _state = message_ready
        消费 8 字节

      case message_ready:
        将数据拷贝/移动到 _in_progress
        if 消息体读取完成:
          _in_progress.set_flags(_msg_flags)
          return 1  // 消息完成！
```

### 零拷贝接收

`shared_message_memory_allocator` 支持零拷贝接收：

1. `get_buffer()` 返回共享内存池中的缓冲区
2. 引擎直接从 fd `read()` 数据到此缓冲区（无中间拷贝）
3. 消息完成后，创建 `type_zclmsg` 消息
4. content_t 的 `ffn` 回调在引用归零时将缓冲区归还到池
5. 消息通过 move 在 pipe 间传递，无数据拷贝

零拷贝接收需要 context 启用 `_zero_copy`（默认 true）。它在大消息高吞吐场景下显著减少内存分配和拷贝。

### 零拷贝的内存布局

```
共享内存池 chunk:
┌──────────────┬──────────────────────────────────┐
│ content_t    │  数据缓冲区（直接从 fd 读入）    │
│ (refcnt, ffn)│                                  │
└──────────────┴──────────────────────────────────┘
       ▲
       │ content->data 指向这里
```

content_t 头部嵌入在数据缓冲区前面，`ffn` 是将 chunk 归还池的回调函数。当所有引用关闭时，`ffn(data, hint)` 被调用，chunk 回到池中供下次接收使用。

## 命令帧

命令帧通过 flags 字节的 bit1（COMMAND）标识，body 格式为：

```
┌────────────┬─────────────┬──────────────┐
│ cmd_len(1) │  command    │  cmd data    │
│            │  name       │  (optional)  │
└────────────┴─────────────┴──────────────┘
```

### 命令类型

msg_t 的 flags 定义了命令类型（F-047）：

| 标志 | 值 | 命令名 | 说明 |
|------|----|--------|------|
| `ping` | 4 | PING | 心跳探测 |
| `pong` | 8 | PONG | 心跳响应 |
| `subscribe` | 12 | SUBSCRIBE | 订阅前缀 |
| `cancel` | 16 | CANCEL | 取消订阅 |
| `close_cmd` | 20 | CLOSE | 优雅关闭连接 |
| `credential` | 32 | — | 认证凭证 |

命令类型使用 bits 2-5（掩码 0x1c），等值比较而非位运算。注意 `subscribe=12` 是 0b01100，不是独立的两个位。

### SUBSCRIBE/CANCEL

订阅命令在 XPUB/XSUB 之间的内置连接上传送：
- SUB 调用 `zmq_setsockopt(ZMQ_SUBSCRIBE, prefix)` 时，xsub_t 创建一个 subscribe 命令帧发送给上游
- 帧 body：命令名 "SUBSCRIBE" + 订阅前缀
- XPUB 收到后，在 mtrie 中为该 pipe 添加前缀映射
- CANCEL 同理，移除前缀映射

### PING/PONG（ZMTP/3.1）

心跳命令：
- PING 帧 body 可选包含上下文数据（ttl 等）
- 收到 PING 后回复 PONG
- PING/PONG 不传递给应用层，由引擎内部处理
- 心跳超时（未收到 PONG）导致连接终止

### CLOSE

ZMTP/3.1 的优雅关闭命令：
- 一方发送 CLOSE 命令后停止接收新消息
- 对端收到 CLOSE 后关闭连接
- 比直接 TCP RST 更优雅，允许在途消息交付

## v3_1_encoder

ZMTP/3.1 使用独立的 `v3_1_encoder_t`（而非 v2_encoder），区别：
- 支持心跳命令帧的生成
- 支持 CLOSE 命令
- 帧格式与 v2 相同（flags + size + body）

v3_1_decoder 继承 v2_decoder 并增加命令帧处理逻辑。

## 编解码在引擎中的位置

```
stream_engine_base_t I/O 循环:

出站（发送）:
  pipe → read msg_t
    → encoder.load_msg(msg)
    → 循环:
        encoder.encode(&data, bufsize)
        ::write(fd, data, size)
      直到编码器返回 0（消息完全写入）
    → msg.move() 或 msg.close()

入站（接收）:
  decoder.get_buffer(&buf, size)
    → ::read(fd, buf, size)
    → decoder.decode(buf, bytes_read, processed)
      → 返回 1（消息完成）:
          msg = decoder.msg()
          pipe->write(msg)
          pipe->flush()
      → 返回 0: 继续读
      → 返回 -1: 协议错误，终止连接
```

## 相关概念

- [ZMTP 协议引擎](/concepts/06-zmtp-engine.md) — 握手状态机和安全机制
- [消息与引用计数](/concepts/03-message.md) — msg_t 标志位和 zclmsg 零拷贝类型
- [消息模式实现](/concepts/11-patterns.md) — SUBSCRIBE/CANCEL 命令在 PUB/SUB 中的传播
- [套接字选项体系](/concepts/09-options.md) — 心跳和最大消息大小选项
- [I/O 线程与多路复用](/concepts/07-io-thread-poller.md) — 引擎在 I/O 线程中执行实际 read/write
