---
type: concept
title: "消息 msg_t 与引用计数"
description: "msg_t 的 64 字节内存布局、六种内部类型（VSM/LMSG/CMSG/ZCLMSG/delimiter/join-leave）、content_t 原子引用计数、copy/move/close 生命周期、零拷贝发送与接收"
tags: [libzmq, zeromq, message, msg, reference-counting, zero-copy]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [../references/msg.md, ../references/zmq-h-api.md]
  facts: [F-004, F-005, F-039, F-040, F-041, F-042, F-043, F-044, F-045, F-046, F-047]
---

# 消息 msg_t 与引用计数

## 核心理解

`msg_t` 是 libzmq 中消息的内部表示，对应公共 API 的 `zmq_msg_t`。它是一个**固定 64 字节的值类型**（F-004, F-039），但消息数据根据大小采用不同的存储策略——小消息内联在 msg_t 内部，大消息通过引用计数的堆块共享。

msg_t 的设计哲学是：消息本身轻量（64 字节可值拷贝传递），数据内容通过引用计数避免不必要的复制。`move()` 是零开销的所有权转移，`copy()` 是共享引用（非深拷贝）。

## 64 字节内存布局

msg_t 总大小固定为 64 字节（F-039），内部使用匿名 union 实现紧凑存储（F-041）。所有变体共享相同的公共头部：

```
偏移   大小    字段
0      8       metadata_t *metadata（消息元数据/属性）
8      1       unsigned char type（消息类型 type_t）
9      1       unsigned char flags（标志位）
10     16      unsigned char group[16]（RADIO/DISH 组名）
26     4       uint32_t routing_id（SERVER/CLIENT 路由 ID）
30     34      类型特定数据（union 变体）
─── 总计 64 字节 ───
```

小消息（VSM）的数据直接存储在偏移 30 开始的区域，最大约 30 字节（具体取决于平台对齐）。大消息在偏移 30 处存储一个 `content_t*` 指针（8 字节）。

## 六种消息类型

msg_t 定义了六种内部类型（F-040），类型值从 101 开始：

### type_vsm = 101：微小消息（Very Small Message）

数据内联在 msg_t 的 64 字节内部，无需任何堆分配。

```
[metadata|type|flags|group|routing_id|data[~30]|size]
```

适用于不超过 `max_vsm_size`（约 30 字节）的消息。这是最高效的消息类型——拷贝就是 64 字节 memcpy，无原子操作，无 malloc/free。

### type_lmsg = 102：长消息（Long Message）

数据存储在堆分配的 `content_t` 块中：

```
msg_t (64 bytes)              content_t (heap)
├── ...                        ├── data (void*)     ──→ [实际数据]
└── content_t *content ──────► ├── size (size_t)
                               ├── ffn (free_fn*)
                               ├── hint (void*)
                               └── refcnt (atomic)
```

内存布局为 `[content_t 头部][数据区]`，`content->data` 指向头部之后的内存。这是最常见的大消息类型。

### type_cmsg = 104：常量消息（Constant Message）

指向外部常量数据，不拥有数据，不释放：

```cpp
struct {
    void *data;      // 指向常量/静态数据
    size_t size;
};
```

适用于发送静态字符串或常量缓冲区，ZeroMQ 不会尝试释放数据。

### type_zclmsg = 105：零拷贝长消息（Zero-Copy Long Message）

由 v2_decoder 在零拷贝接收模式下创建。content_t 的 `ffn` 回调将数据缓冲区归还到 decoder 的共享内存池，而非 `free()`。

### type_delimiter = 103：分隔符

无数据的特殊消息，用于 pipe 终止协议。当 pipe 关闭时，写入一个 delimiter 标记"之后没有更多消息"，读端遇到 delimiter 后知道写端已关闭。

### type_join = 106 / type_leave = 107：组播加入/离开

RADIO/DISH Draft 模式使用，携带组名信息。

类型值从 101 开始而非 0，使得未初始化的 type=0 能被检测为无效消息，帮助调试。

## content_t：引用计数数据块

长消息的数据块头部是 `content_t`（F-042）：

```cpp
struct content_t {
    void *data;               // 数据指针（指向 content 之后）
    size_t size;              // 数据大小
    msg_free_fn *ffn;         // 自定义释放函数（NULL = free()）
    void *hint;               // 传递给 ffn 的用户数据
    zmq::atomic_counter_t refcnt;  // 原子引用计数器
};
```

关键点：
- 数据紧跟在 content_t 之后分配（`malloc(sizeof(content_t) + size)`）
- `ffn` 允许应用程序提供自定义释放逻辑（如释放共享内存、归还缓冲区池）
- `refcnt` 使用原子操作，支持多线程安全的引用计数

## init_size：按大小选择存储策略

`init_size(size_)` 是最常用的消息初始化方法（F-043）：

```
if size_ <= max_vsm_size (~30 bytes):
    type = type_vsm
    数据写入 _u.vsm.data
    _u.vsm.size = size_
    // 无堆分配
else:
    type = type_lmsg
    分配 sizeof(content_t) + size_ 字节
    content->data 指向 content 之后
    content->ffn = NULL
    placement new 构造 refcnt，初始值 = 1
```

这意味着：
- 小消息（如短命令、心跳、ACK）完全避免 malloc/free 开销
- 大消息只分配一次内存（content 头 + 数据连续）

`zmq_msg_init_data()` 创建 type_cmsg，让 ZeroMQ 直接引用应用程序缓冲区，实现发送端零拷贝。必须提供 `ffn` 释放函数。

## copy：共享引用而非深拷贝

`copy(&src_)` 创建源消息的"副本"（F-044），但这不是深拷贝：

```
1. close() 目标当前持有的资源
2. 若源为 lmsg/zclmsg:
   - 若已 shared: refcnt.add(1)
   - 若未 shared: 设置 shared 标志，refcnt = 2
3. metadata 和 long group 也增加引用
4. memcpy(this, &src_, 64)  // 复制整个 msg_t
```

copy 后，源和目标指向**同一个 content_t**。这意味着：
- 修改副本的数据内容会影响原消息（对于 lmsg）
- 两者独立调用 `close()`，引用计数归零后数据才释放
- 对于 VSM，copy 就是简单的 64 字节 memcpy（数据内联，无引用计数）

**重要反常识**：`zmq_msg_copy()` 不是深拷贝。如果需要独占数据，应自行深拷贝或使用 `zmq_msg_init_data()` 配合独立的缓冲区。

## close：递减引用计数

`close()` 释放消息持有的资源（F-045）：

```
lmsg:
  if not shared → 直接释放
  if shared:
    refcnt.sub(1)
    if 结果 == 0:  // 最后一个引用
      析构 refcnt
      if ffn: ffn(data, hint)  // 自定义释放
      else: free(content)       // 默认释放

zclmsg:
  类似 lmsg，但必须有 ffn（归还内存池）

metadata/long group:
  各自按引用计数释放

type = 0  // 使消息失效
```

close 后 msg_t 变为空消息（type=0），不能再使用。应用程序必须为每个初始化的消息调用 close，否则资源泄漏。

## move：零开销所有权转移

`move(&src_)` 将消息所有权从源转移到目标（F-046）：

```
1. close() 目标当前资源
2. memcpy(this, &src_, 64)   // 按位复制
3. src_.init()                // 重置源为空消息
```

move **不修改引用计数**——它只是复制 64 字节指针并重置源。这是最高效的消息传递方式：
- 发送消息时，`zmq_msg_send()` 内部使用 move 将消息所有权转移给 pipe
- inproc 通信时，消息通过 move 在 pipe 之间传递
- 大消息的 content 数据自始至终只有一份拷贝

move 后源消息变为空消息（size=0, data=NULL），不能再读取。

## 标志位

msg_t 的 flags 字段定义了 ZMTP 帧级别的标志（F-047）：

| 标志 | 值 | 说明 |
|------|----|------|
| `more` | 1 | 多部分消息的后续帧 |
| `command` | 2 | ZMTP 命令帧（非用户数据） |
| `ping` | 4 | PING 心跳 |
| `pong` | 8 | PONG 心跳响应 |
| `subscribe` | 12 | SUBSCRIBE 订阅命令 |
| `cancel` | 16 | CANCEL 取消订阅 |
| `close_cmd` | 20 | CLOSE 连接关闭 |
| `credential` | 32 | 认证凭证 |
| `routing_id` | 64 | 路由 ID 帧 |
| `shared` | 128 | 内容已共享（引用计数 >1） |

命令类型使用 bits 2-5（掩码 0x1c），用等值比较而非位运算。例如 `subscribe=12`（0b01100）同时设置了 bit2 和 bit3，不是独立的 ping + 其他。

## 零拷贝机制

### 发送端零拷贝

使用 `zmq_msg_init_data()`：

```c
void my_free(void *data, void *hint) {
    free(data);  // 应用程序负责释放
}

void *buf = malloc(1024);
zmq_msg_t msg;
zmq_msg_init_data(&msg, buf, 1024, my_free, NULL);
zmq_msg_send(&msg, socket, 0);
```

ZeroMQ 直接引用应用程序缓冲区，不复制数据。发送完成后通过 `ffn` 回调通知应用程序释放。注意：在 ZeroMQ 调用 ffn 之前，应用程序不能重用或释放缓冲区。

### 接收端零拷贝（zclmsg）

当 context 启用零拷贝接收（默认 `_zero_copy=true`，F-015）时：
1. decoder 使用 `shared_message_memory_allocator` 从内存池分配数据缓冲区
2. 直接从 socket fd 读取数据到池缓冲区
3. 创建 `type_zclmsg` 消息，content 的 ffn 将缓冲区归还到池
4. 消息通过 move 在 pipe 间传递，无数据拷贝
5. 最后一个引用 close 时，缓冲区归还到池而非 free

编码器也有零拷贝优化（F-081）：当待编码数据量 ≥ 输出缓冲区大小时，直接返回消息内容指针，避免从消息到缓冲区的 memcpy。

## 多部分消息

多部分消息通过 `more` 标志实现：

```c
zmq_msg_send(&part1, socket, ZMQ_SNDMORE);  // more=1
zmq_msg_send(&part2, socket, ZMQ_SNDMORE);  // more=1
zmq_msg_send(&part3, socket, 0);            // more=0, 最后一帧
```

- 接收方通过 `zmq_msg_more()` 检查是否有后续帧
- 多部分消息是原子的：所有帧要么一起传递，要么不传递
- PUB/SUB 中订阅匹配只检查第一帧（主题帧）
- ROUTER 接收的消息第一帧是 routing_id，第二帧起是用户数据

## inproc 零拷贝

同一进程内的 inproc 连接不经过网络栈和编解码：
1. `pipepair()` 在两个 socket 之间创建双向无锁队列
2. 发送方将 msg_t 写入 ypipe（64 字节值拷贝）
3. 接收方从 ypipe 读出 msg_t
4. 大消息的 content_t 引用计数确保数据只在最后一个引用关闭时释放

这使得 inproc 成为最高效的线程间通信方式之一——小消息只有 64 字节内存拷贝，大消息只有指针拷贝。

## 相关概念

- [整体架构总览](00-overview.md) — 消息在四层管线中的流动
- [管道与流控](04-pipe.md) — msg_t 在 pipe 的 ypipe 中传递
- [编解码与帧格式](12-encoder-decoder.md) — v2_encoder/decoder 处理 msg_t 的线格式
- [ZMTP 协议引擎](06-zmtp-engine.md) — 命令帧标志在 ZMTP 握手和心跳中的使用
- [命令传递与邮箱](08-command-mailbox.md) — command_t 也使用 ypipe 但类型不同
