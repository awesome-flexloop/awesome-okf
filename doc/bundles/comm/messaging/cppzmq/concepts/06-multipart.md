---
type: concept
title: "multipart 高层抽象"
description: "多部分消息的自由函数 send_multipart/recv_multipart、multipart_t 容器、以及 encode/decode 单帧编码"
tags: [cppzmq, zeromq, multipart, zmsg, high-level]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [/references/zmq-addon-hpp.md]
  facts: [F-052, F-053, F-054, F-055]
---

# multipart 高层抽象

ZeroMQ 的多部分消息（multipart message）由若干帧组成，除最后一帧外均带 `SNDMORE`/`more` 标志。`zmq_addon.hpp` 提供三种抽象层级。

## 1. 自由函数：recv_multipart / send_multipart

### 接收到输出迭代器

```c++
std::vector<zmq::message_t> parts;
auto r = zmq::recv_multipart(sock, std::back_inserter(parts));
if (!r) { /* EAGAIN */ }
// *r = 帧数
```

`recv_multipart(socket_ref, OutputIt, recv_flags=none)` 循环 `recv(message_t)`，每帧 `*out++ = std::move(msg)`，直到 `msg.more()==false`。返回 `recv_result_t`（帧数或 nullopt）。

带上限版本：

```c++
zmq::recv_multipart_n(sock, std::back_inserter(parts), 5);  // 超过 5 帧抛 std::runtime_error
```

### 从范围发送

```c++
std::vector<zmq::message_t> msgs = ...;
auto s = zmq::send_multipart(sock, msgs);   // 自动对非末帧加 sndmore
```

`send_multipart(socket_ref, Range&&, send_flags=none)` 接受 `message_t`/`const_buffer`/`mutable_buffer` 的 ForwardRange；对除最后一帧外的每帧加 `send_flags::sndmore`，返回发送帧数或 nullopt（EAGAIN）。

## 2. multipart_t：类似 CZMQ zmsg 的容器

内部是 `std::deque<zmq::message_t>`，禁用拷贝、使用移动语义。

### 构造与收发

```c++
zmq::multipart_t mp;
mp.recv(sock);                  // 从 socket 接收整组多部分
mp.send(sock);                  // 发送后 clear()

zmq::multipart_t mp2(sock);     // 构造即接收
zmq::multipart_t mp3("hello");  // 从字符串构造单帧
zmq::multipart_t mp4(std::move(msg));
```

### 部件操作（前/后）

| 操作 | 前（front） | 后（back） |
|---|---|---|
| 推入 message_t | `push(message_t&&)` | `add(message_t&&)` / `push_back` |
| 推入内存 | `pushmem(ptr,size)` | `addmem(ptr,size)` |
| 推入字符串 | `pushstr(str)` | `addstr(str)` |
| 推入定长类型 | `pushtyp<T>(v)` | `addtyp<T>(v)` |
| 弹出 | `pop()` → message_t | `remove()` → message_t |
| 弹字符串 | `popstr()` | — |
| 弹定长类型 | `poptyp<T>()`（size 不匹配抛 runtime_error） | — |
| 查看 | `front()` / `peek(i)` / `peekstr(i)` / `peektyp<T>(i)` | `back()` |

### 其他

- `size()`/`empty()`/`clear()`；完整迭代器（`begin/end/rbegin/rend`）与 `operator[]`/`at`。
- `clone()` 深拷贝所有帧（逐帧 `addmem`）。
- `prepend(multipart_t&&)` / `append(multipart_t&&)` 合并两组。
- `str()` 生成可读调试输出；`operator==` 逐帧比较；`operator<<` 输出到流。
- C++11 下 `encode()`/`decode_append()`/静态 `decode()`。

## 3. encode / decode：单帧序列化（RFC 50）

把多部分消息编解码为**单个** `message_t`，兼容 CZMQ `zmsg_encode()`（[ZeroMQ RFC 50](https://rfc.zeromq.org/spec/50/)）：

```c++
zmq::message_t packed = zmq::encode(parts);    // parts 是 message_t/buffer 的范围
zmq::multipart_t restored = zmq::multipart_t::decode(packed);
```

编码格式：每部分 = 长度 + 数据。
- 长度 < 255：1 字节长度。
- 长度 ≥ 255：`0xFF` + 4 字节**网络序** uint32 长度。

- `encode` 对超过 uint32 上限的部分抛 `std::range_error`。
- `decode` 遇到越界抛 `std::out_of_range`。

## 选型建议

| 场景 | 推荐 |
|---|---|
| 接收到已有容器、最小依赖 | `recv_multipart` + `back_inserter` |
| 需要在内存中拼装/拆解多帧、类 zmsg 操作 | `multipart_t` |
| 需要把多帧打包成单帧传输/存储 | `encode`/`decode` |

## 相关概念

- [03 message 与 buffer](03-message-and-buffer.md)
- [05 poller](05-poller.md)
- [示例：multipart-poller](../examples/multipart-poller.md)
- [信源：zmq_addon.hpp](../references/zmq-addon-hpp.md)
