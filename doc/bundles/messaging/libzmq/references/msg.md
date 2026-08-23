---
type: reference
title: "msg_t：消息内部结构与引用计数完整索引"
description: "src/msg.hpp 和 src/msg.cpp 中 msg_t 的 64 字节内存布局、六种内部类型、union 变体、content_t 引用计数、init/copy/move/close 实现、命令帧标志位"
tags: [libzmq, reference, message, msg]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  - path: "external/libs/remote/libzmq/src/msg.hpp"
    facts: [F-039, F-040, F-041, F-042, F-047]
  - path: "external/libs/remote/libzmq/src/msg.cpp"
    facts: [F-043, F-044, F-045, F-046]
  - path: "external/libs/remote/libzmq/include/zmq.h"
    facts: [F-004, F-005]
---

# msg_t：消息内部结构与引用计数完整索引

## 信源概述

| 信源 | 类型 | 职责 |
|------|------|------|
| `src/msg.hpp` | C++ 头文件 | msg_t 类声明、type_t 枚举、content_t 结构体、union 布局、标志位 |
| `src/msg.cpp` | C++ 实现 | init_size/copy/move/close 等生命周期方法实现 |
| `include/zmq.h` | C 公共头文件 | zmq_msg_t 不透明结构体定义、消息操作 C API |

## 关键事实登记

### F-004：zmq_msg_t 为 64 字节不透明结构体

**信源**：`include/zmq.h` L218-L232

```c
typedef struct zmq_msg_t {
    unsigned char _ [64];
} zmq_msg_t;
```

公共 C API 中的 `zmq_msg_t` 是内部 `msg_t` 的不透明包装。两者大小相同（64 字节），内存布局一致。

### F-039：msg_t 总大小为 64 字节

**信源**：`src/msg.hpp` L148-L156

```cpp
enum { msg_t_size = 64 };
enum { max_vsm_size =
    msg_t_size - (sizeof(metadata_t*) + 3 + 16 + sizeof(uint32_t))
};
```

- `msg_t_size = 64`：msg_t 固定 64 字节
- `max_vsm_size`：小消息（VSM, Very Small Message）可内联存储的最大数据大小
  - 在 64 位平台上：64 - (8 + 3 + 16 + 4) = 33 字节（实际受对齐影响约为 30 字节）
  - 小消息数据直接存储在 msg_t 内部，无需额外堆分配

### F-040：msg_t 六种内部类型

**信源**：`src/msg.hpp` L168-L190

```cpp
enum type_t {
    type_vsm       = 101,  // 微小消息：数据内联在 msg_t 中
    type_lmsg      = 102,  // 长消息：堆分配 content_t
    type_delimiter = 103,  // 分隔符：用于管道终止标记
    type_cmsg      = 104,  // 常量消息：指向外部常量数据，无 free 函数
    type_zclmsg    = 105,  // 零拷贝长消息：v2_decoder 使用共享内存池
    type_join      = 106,  // RADIO-DISH 组播加入
    type_leave     = 107   // RADIO-DISH 组播离开
};
```

| 类型 | 存储方式 | 释放 | 典型场景 |
|------|---------|------|---------|
| VSM | 内联在 64 字节 msg_t 中 | 无需释放 | ≤30 字节小消息 |
| LMSG | 堆分配 `content_t` | 引用计数归零后 `free()` | 普通大消息 |
| delimiter | 无数据 | 无需释放 | pipe 终止协议 |
| CMSG | 指向外部常量 | 不释放 | 常量字符串/静态数据 |
| ZCLMSG | 共享内存池 | 通过 `ffn` 回调归还池 | 零拷贝接收 |
| join/leave | 组名 | — | RADIO/DISH Draft 模式 |

类型值从 101 开始而非 0，是为了让未初始化的 type=0 能被检测为无效。

### F-041：msg_t 使用 union 紧凑存储

**信源**：`src/msg.hpp` L223-L297

`msg_t` 内部是一个匿名 union，所有变体共享前 64 字节内存：

```cpp
struct msg_t {
    union {
        struct {
            metadata_t *metadata;
            unsigned char type;
            unsigned char flags;
            unsigned char group[16];
            uint32_t routing_id;
        } base;

        struct {
            metadata_t *metadata;
            unsigned char type;
            unsigned char flags;
            unsigned char group[16];
            uint32_t routing_id;
            unsigned char data[max_vsm_size];
            unsigned char size;
        } vsm;

        struct {
            metadata_t *metadata;
            unsigned char type;
            unsigned char flags;
            unsigned char group[16];
            uint32_t routing_id;
            content_t *content;
        } lmsg;

        struct {
            metadata_t *metadata;
            unsigned char type;
            unsigned char flags;
            unsigned char group[16];
            uint32_t routing_id;
            content_t *content;
        } zclmsg;

        struct {
            metadata_t *metadata;
            unsigned char type;
            unsigned char flags;
            unsigned char group[16];
            uint32_t routing_id;
            void *data;
            size_t size;
        } cmsg;

        struct {
            metadata_t *metadata;
            unsigned char type;
            unsigned char flags;
            unsigned char group[16];
            uint32_t routing_id;
        } delimiter;
    } _u;
};
```

**公共字段**（所有变体共享）：
- `metadata`：消息元数据指针（属性键值对）
- `type`：消息类型（type_t 枚举）
- `flags`：标志位（more/command/subscribe 等）
- `group[16]`：RADIO/DISH 组名（最多 15 字符 + null）
- `routing_id`：路由 ID（用于 SERVER/CLIENT Draft 模式）

### F-042：content_t 引用计数结构

**信源**：`src/msg.hpp` L43-L50

```cpp
struct content_t {
    void *data;
    size_t size;
    msg_free_fn *ffn;
    void *hint;
    zmq::atomic_counter_t refcnt;
};
```

| 字段 | 说明 |
|------|------|
| `data` | 指向消息数据的指针（紧跟 content_t 之后） |
| `size` | 数据大小（字节） |
| `ffn` | 释放函数指针（NULL 时使用 `free()`） |
| `hint` | 传递给 ffn 的用户数据指针 |
| `refcnt` | 原子引用计数器 |

内存布局：`[content_t 头部][data 数据区]`，通过 placement new 在数据块头部构造 refcnt。`content->data` 指向 content 之后的内存地址。

### F-043：init_size 按大小选择 VSM 或 LMSG

**信源**：`src/msg.cpp` L62-L95

```cpp
int init_size (size_t size_);
```

执行逻辑：

1. **若 `size_ <= max_vsm_size`**：
   - 设置 `type = type_vsm`
   - 数据直接写入 `_u.vsm.data`
   - `_u.vsm.size = size_`
   - 无堆分配
2. **若 `size_ > max_vsm_size`**：
   - 设置 `type = type_lmsg`
   - 分配 `sizeof(content_t) + size_` 字节
   - `content->data` 指向 content 之后的内存
   - `content->size = size_`
   - `content->ffn = NULL`（默认使用 free）
   - `content->hint = NULL`
   - 使用 placement new 在 `&content->refcnt` 构造 `atomic_counter_t`，初始值为 1
   - `_u.lmsg.content = content`

### F-044：copy 实现共享引用计数

**信源**：`src/msg.cpp` L326-L362

```cpp
int copy (msg_t &src_);
```

执行逻辑：

1. 先调用 `close()` 关闭目标消息当前持有的资源
2. **若源为 lmsg/zclmsg**：
   - 若源已 `shared`：`refcnt.add(1)` 增加引用
   - 若源未 shared：设置 `shared` 标志，并将 `refcnt` 设为 2（源和副本各持一个）
3. **metadata 引用计数**：若有 metadata，增加其引用计数
4. **long group 引用计数**：若 group 超过 16 字节（使用堆分配），增加其引用
5. **按位复制**：`memcpy(this, &src_, 64)` 复制整个 msg_t

copy 之后，源和目标共享同一份数据 content。修改副本的数据内容会影响原消息（对于 lmsg 类型）。

### F-045：close 递减引用计数并条件释放

**信源**：`src/msg.cpp` L242-L303

```cpp
int close ();
```

执行逻辑：

1. **lmsg 类型**：
   - 若未 shared：直接释放
   - 若 shared：`refcnt.sub(1)`，若返回 0（引用归零）：
     - 显式析构 refcnt（`~atomic_counter_t()`）
     - 若有 `ffn`：调用 `ffn(data, hint)`（自定义释放）
     - 若无 `ffn`：`free(content)`
2. **zclmsg 类型**：
   - 类似 lmsg，但**必须**有 ffn（零拷贝消息必须通过回调释放回内存池）
3. **metadata**：按引用计数释放
4. **long group**：按引用计数释放
5. 将 `type` 置 0 使消息失效

### F-046：move 是零拷贝所有权转移

**信源**：`src/msg.cpp` L305-L324

```cpp
int move (msg_t &src_);
```

执行逻辑：

1. 先调用 `close()` 关闭目标当前资源
2. **按位复制**：`memcpy(this, &src_, 64)` 复制整个 msg_t
3. **重置源**：调用 `src_.init()` 将源重置为空消息（type=0）

move 不涉及引用计数修改——它是纯粹的 64 字节内存拷贝 + 源重置。这是最高效的消息传递方式，所有权从源转移到目标。

### F-047：msg_t 命令帧标志

**信源**：`src/msg.hpp` L53-L67

```cpp
enum {
    more       = 1,    // 多部分消息后续帧
    command    = 2,    // ZMTP 命令帧
    ping       = 4,    // PING 心跳
    pong       = 8,    // PONG 心跳响应
    subscribe  = 12,   // SUBSCRIBE 订阅命令
    cancel     = 16,   // CANCEL 取消订阅
    close_cmd  = 20,   // CLOSE 关闭连接
    credential = 32,   // 凭证消息
    routing_id = 64,   // 路由 ID 帧
    shared     = 128   // 消息内容已共享（引用计数 >1）
};
```

**命令类型编码**：命令类型使用 bits 2-5（掩码 `0x1c`），用等值比较而非位运算：
- `ping = 4`（0b00100）
- `pong = 8`（0b01000）
- `subscribe = 12`（0b01100）
- `cancel = 16`（0b10000）
- `close_cmd = 20`（0b10100）

这些标志与 `command` 标志（bit1=2）组合使用，表示 ZMTP 连接上的内部控制消息，而非用户数据。

### F-005：消息操作函数集

**信源**：`include/zmq.h` L236-L251

C API 函数与 C++ 方法的对应关系：

| C API | C++ msg_t 方法 | 说明 |
|-------|---------------|------|
| `zmq_msg_init` | `init()` | 初始化为空消息 |
| `zmq_msg_init_size` | `init_size(size)` | 初始化指定大小 |
| `zmq_msg_init_data` | `init_data(data, size, ffn, hint)` | 使用外部缓冲区 |
| `zmq_msg_close` | `close()` | 释放资源 |
| `zmq_msg_move` | `move(src)` | 所有权转移 |
| `zmq_msg_copy` | `copy(src)` | 共享引用复制 |
| `zmq_msg_data` | `data()` | 获取数据指针 |
| `zmq_msg_size` | `size()` | 获取数据大小 |
| `zmq_msg_more` | `flags() & more` | 是否有后续帧 |
| `zmq_msg_get/set` | `get/set property` | 消息属性 |
| `zmq_msg_gets` | `gets(property)` | 字符串属性（如 "Socket-Type"） |
