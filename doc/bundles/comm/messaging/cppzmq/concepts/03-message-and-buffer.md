---
type: concept
title: "message_t 与 buffer 抽象"
description: "ZeroMQ 消息封装的构造函数族、移动/拷贝语义、零拷贝，以及 const_buffer/mutable_buffer 统一内存抽象"
tags: [cppzmq, zeromq, message, buffer, zero-copy]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [/references/zmq-hpp.md]
  facts: [F-009, F-010, F-013, F-015, F-016, F-019, F-030, F-032, F-033, F-034]
---

# message_t 与 buffer 抽象

## message_t 构造函数族

| 构造 | 用途 | 语义 |
|---|---|---|
| `message_t()` | 空消息 | `zmq_msg_init`，size=0 |
| `message_t(size_t size)` | 指定字节数 | `zmq_msg_init_size`，分配未初始化内存 |
| `message_t(const void* data, size_t size)` | 从内存拷贝 | `init_size` + `memcpy`（size=0 时跳过 memcpy） |
| `message_t(void* data, size_t, free_fn*, void* hint)` | 零拷贝 | `zmq_msg_init_data`，消息释放时回调 `free_fn` |
| `message_t(Iter first, Iter last)` | 迭代器区间 | 按 `distance*sizeof(value_t)` 拷贝 |
| `message_t(const Range& rng)` | 连续容器 | 要求元素 trivially copyable |
| `message_t(const std::string&)` / `(std::string_view)` | 字符串 | 拷贝，不含终止符 |

## 所有权与移动/拷贝

- **拷贝被删除**：`message_t(const message_t&)` = delete，防止用户无意识触发 libzmq 的引用计数共享。
- **移动**：移动构造复制底层 `zmq_msg_t` 后 `zmq_msg_init` 源对象（源变空）；移动赋值 `swap`。
- **显式共享**：`msg.copy(other)` 调 `zmq_msg_copy`（引用计数零拷贝共享）；`msg.move(other)` 调 `zmq_msg_move`。
- **析构**：`zmq_msg_close`。

## 访问数据

```c++
void* p = msg.data();                 // 或模板 msg.data<T>()
size_t n = msg.size();
bool empty = msg.empty();
bool has_more = msg.more();           // 多部分消息是否还有后续帧
std::string s = msg.to_string();
```

`operator==` 逐字节比较（先比 size）。`str(max_size)` 生成可读调试串（ASCII 原样、其余十六进制）。

## rebuild / 生命周期

`rebuild()` 系列重载先 `zmq_msg_close` 再重新 init，等价于析构后重建：空、size、(data,size)、string、零拷贝。

## buffer 抽象

受 Networking TS 启发，`mutable_buffer`/`const_buffer` 是 `(指针, 长度)` 值类型：

```c++
zmq::const_buffer cb{ptr, len};
zmq::mutable_buffer mb{buf, bufsize};
mb += 10;                 // 指针前移 min(10, size)
```

- `const_buffer` 可从 `mutable_buffer` 隐式构造（只读视角），反向不可。
- 自由函数 `buffer(...)` 重载覆盖：裸 `(void*,size)`、C 数组、`std::array`、`std::vector`、`std::basic_string`、`std::string_view`，以及 buffer 本身。
- 元素必须满足 `is_pod_like`（trivially copyable **且** standard layout），否则 `static_assert` 失败。

## str_buffer 与字符串字面量

```c++
auto cb = zmq::str_buffer("hello");     // 长度 5，不含 '\0'
sock.send(cb);
sock.send("hello"_zbuf);                // 等价（zmq::literals）
```

`str_buffer` 返回指向字面量静态存储的视图，不复制、不拥有；适用于 `send_static`。

## 与 send/recv 的配合

- `send(const_buffer, flags)`：发送任意只读连续内存。
- `recv(mutable_buffer, flags)`：接收到定长缓冲，返回 `recv_buffer_size{written, untruncated}`，可查 `truncated()`。
- `send(message_t&, flags)` / `recv(message_t&, flags)`：发送/接收整帧消息。

## 相关概念

- [02 socket_t](02-socket.md) · [06 multipart](06-multipart.md)
- [04 错误处理](04-error-handling.md)
- [信源：zmq.hpp](../references/zmq-hpp.md)
