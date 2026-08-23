---
type: reference
title: "zmq_addon.hpp 文件参考"
description: "cppzmq 扩展头文件 zmq_addon.hpp 的多部分消息、active_poller_t、poller_ref_t 签名与依赖"
tags: [cppzmq, zeromq, reference, zmq_addon.hpp, multipart]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  - path: "external/libs/remote/cppzmq/zmq_addon.hpp"
    facts: [F-051, F-052, F-053, F-054, F-055, F-056]
---

# zmq_addon.hpp 文件参考

扩展头文件，首行 `#include "zmq.hpp"`。提供高层多部分消息与主动轮询抽象，不包含 `request_t`/`reply_t`/`server_t`/`client_t` 等类型。

## 行号索引

| 行号 | 内容 |
|---|---|
| L27 | `#include "zmq.hpp"` |
| L38-L92 | **`poller_ref_t`**：socket/fd 带标签可哈希联合（`RT_SOCKET`/`RT_FD`），内部 `tuple<int,socket_ref,fd_t>`；`std::hash<poller_ref_t>` 特化 |
| L98-L158 | `namespace detail`：`recv_multipart_n<CheckN>`、`is_little_endian`、网络序 uint32 读写 |
| L172-L178 | **`recv_multipart(socket_ref, OutputIt, recv_flags=none)`** → `recv_result_t` |
| L194-L201 | **`recv_multipart_n(socket_ref, OutputIt, size_t n, recv_flags=none)`**：超 n 抛 `std::runtime_error` |
| L215-L245 | **`send_multipart(socket_ref, Range&&, send_flags=none)`**：接受 message_t/buffer 的 ForwardRange，自动加 sndmore |
| L266-L313 | **`encode(const Range& parts)`** → `message_t`：CZMQ zmsg 兼容编码（RFC 50） |
| L330-L357 | **`decode(const message_t&, OutputIt)`**：解码到输出迭代器 |
| L371-L731 | **`multipart_t`**：`std::deque<message_t>` 容器，移动语义、收发、push/add/pop/peek/str/encode/decode |
| L733-L736 | `operator<<(ostream&, multipart_t)` |
| L740-L853 | **`active_poller_t`**（Draft）：`handler_type = std::function<void(event_flags)>`，add/remove/modify/wait，内部 `poller_t<handler_type>` + `unordered_map<poller_ref_t, shared_ptr<handler_type>>` |

## 自由函数签名

```c++
template<class OutputIt>
recv_result_t recv_multipart(socket_ref s, OutputIt out,
                             recv_flags flags = recv_flags::none);

template<class OutputIt>
recv_result_t recv_multipart_n(socket_ref s, OutputIt out, size_t n,
                               recv_flags flags = recv_flags::none);

template<class Range>
send_result_t send_multipart(socket_ref s, Range&& msgs,
                             send_flags flags = send_flags::none);

template<class Range>
message_t encode(const Range& parts);

template<class OutputIt>
OutputIt decode(const message_t& encoded, OutputIt out);
```

`send_multipart`/`encode` 的 `Range` 必须满足 `detail::is_range` 且元素为 `message_t`、`const_buffer` 或 `mutable_buffer`。

## multipart_t 关键方法

- 收发：`recv(socket_ref, int flags=0)` / `send(socket_ref, int flags=0)` + C++11 `send(socket_ref, send_flags)`
- 迭代器：`begin/end/cbegin/cend/rbegin/rend`
- 前插：`push/pushmem/pushstr/pushtyp<T>`；后插：`add/addmem/addstr/addtyp<T>`/`push_back`
- 弹出：`pop/popstr/poptyp<T>`（前）、`remove`（后）
- 查看：`front/back/peek/peekstr/peektyp<T>`、`operator[]/at`
- 工具：`clone()`（深拷贝）、`str()`、`equal()`、`operator==`、`prepend/append`
- 编码：`encode()`、`decode_append()`、静态 `decode()`
- 拷贝删除，移动支持

## active_poller_t 关键方法

```c++
using handler_type = std::function<void(event_flags)>;
void add(socket_ref, event_flags, handler_type);
void add(fd_t, event_flags, handler_type);
void remove(socket_ref);
void remove(fd_t);
void modify(socket_ref, event_flags);
void modify(fd_t, event_flags);
size_t wait(std::chrono::milliseconds timeout);
bool empty() const noexcept;
size_t size() const noexcept;
```

- 空 handler 抛 `std::invalid_argument`；重复注册抛 `error_t(EINVAL)`。
- `wait` 在增删后重建 handler 向量（`need_rebuild`），调 `wait_all` 并逐个回调。
- 拷贝删除，移动默认。

## 依赖条件

- 多部分自由函数需要 `ZMQ_CPP11`。
- `multipart_t` 需要 `ZMQ_HAS_RVALUE_REFS`（移动语义）。
- `active_poller_t`/`poller_ref_t` 需要 `ZMQ_BUILD_DRAFT_API` + `ZMQ_CPP11` + `ZMQ_HAVE_POLLER`。
- `encode`/`decode` 的网络序辅助在 `detail` 命名空间。
