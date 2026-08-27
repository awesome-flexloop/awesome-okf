---
type: concept
title: "socket_t 与套接字层"
description: "socket_t 的 RAII 封装、socket_type 枚举、bind/connect、send/recv 结果类型、sockopt 标签机制与 socket_ref"
tags: [cppzmq, zeromq, socket, sockopt, raii]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [/references/zmq-hpp.md]
  facts: [F-035, F-036, F-037, F-038, F-039, F-040, F-041, F-042, F-043, F-044]
---

# socket_t 与套接字层

## socket_type 强类型枚举

`enum class zmq::socket_type : int` 映射全部套接字类型：`req/rep/dealer/router/pub/sub/xpub/xsub/push/pull/stream/pair`，以及 Draft 的 `server/client/radio/dish/gather/scatter/dgram/peer/channel`。

```c++
zmq::socket_t sock(ctx, zmq::socket_type::router);
zmq::socket_t sock2(ctx, ZMQ_ROUTER);   // 仍接受旧式 int
```

## RAII 与移动

- 构造调用 `zmq_socket(ctx.handle(), type)`，失败抛 `error_t`。
- 析构调用 `zmq_close`；`close()` 可显式提前关闭（幂等）。
- 保存 `_handle` 与 `ctxptr`；支持移动，禁用拷贝。
- `socket_t` 是 `socket_ref` 的友元转换来源：`zmq::socket_ref ref = sock;` 产生**非拥有**引用。

## 拓扑操作

```c++
sock.bind("tcp://*:5555");
sock.connect("tcp://localhost:5555");
sock.unbind("tcp://*:5555");
sock.disconnect("tcp://localhost:5555");
```

每个方法同时接受 `const std::string&` 和 `const char*`。

## send / recv 与 optional 结果

现代 API 用 `optional` 表达 EAGAIN（非阻塞且现在不可用）：

```c++
auto r = sock.send(zmq::buffer(data), zmq::send_flags::dontwait);
if (!r) { /* EAGAIN，稍后重试 */ }

zmq::message_t msg;
auto rr = sock.recv(msg, zmq::recv_flags::none);
```

- `send(const_buffer, send_flags)` → `send_result_t`（`optional<size_t>`）。
- `send(message_t&, send_flags)` 同理；`send(message_t&&)` 转发左值版。
- `send_static` 走 `zmq_send_const`，用于不会被修改的常量缓冲。
- `recv(mutable_buffer, recv_flags)` → `recv_buffer_result_t`，返回 `{size, untruncated_size}`，可查 `truncated()`。
- 旧的 `send(const void*, size_t, int)`/`recv(void*, size_t, int)` 已废弃。

## 类型安全选项：sockopt 标签

`sockopt` 命名空间为每个选项定义空标签类型：

```c++
sock.set(zmq::sockopt::linger, 0);
sock.set(zmq::sockopt::immediate, false);
sock.set(zmq::sockopt::routing_id, "my-id");
sock.set(zmq::sockopt::subscribe, zmq::buffer(topic));

int ev = sock.get(zmq::sockopt::events);
std::string id = sock.get(zmq::sockopt::routing_id);
```

标签分两类：
- `integral_option<Opt, T, BoolUnit>`：整型/布尔值；`BoolUnit=true` 允许传 `bool`。
- `array_option<Opt, NullTerm>`：字符串/二进制；`NullTerm` 0=二进制、1=空终止字符串、2=二进制或 Z85。

底层由 `detail::socket_base` 的 `set`/`get` 模板重载实现，编译期绑定类型与长度。

## socket_ref：非拥有引用

`zmq::socket_ref` 继承 `socket_base` 但不持有句柄，可拷贝、可为空、可比较、可哈希（`std::hash` 特化）。用于把 socket 传给不关心所有权的函数（如 `send_multipart(socket_ref, ...)`、`poller_t::add`）。通过 `zmq::from_handle` 或从 `socket_t` 隐式转换构造。

## proxy

```c++
zmq::proxy(frontend, backend);                  // 可选 capture socket
zmq::proxy_steerable(frontend, backend, capture, control);
```

接受 `socket_ref`，包装 `zmq_proxy`/`zmq_proxy_steerable`。

## 相关概念

- [01 context_t](01-context.md)
- [03 message 与 buffer](03-message-and-buffer.md)
- [04 错误处理](04-error-handling.md)
- [信源：zmq.hpp](../references/zmq-hpp.md)
