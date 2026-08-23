---
type: concept
title: "cppzmq 整体架构与设计目标"
description: "cppzmq 4.11.0 的 header-only 形态、分层结构、命名空间布局与核心设计哲学"
tags: [cppzmq, zeromq, architecture, overview]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [/references/zmq-hpp.md, /references/zmq-addon-hpp.md]
  facts: [F-001, F-002, F-003, F-035, F-046, F-051, F-055, F-056]
---

# cppzmq 整体架构与设计目标

cppzmq 是 ZeroMQ（libzmq）的 C++ header-only 绑定，版本 4.11.0。它不重新实现消息逻辑，而是在 libzmq C API 之上提供轻量、类型安全、RAII 化的 C++ 封装。

## 1. 物理结构

| 文件 | 行数 | 职责 |
|---|---|---|
| `zmq.hpp` | ~3010 | 核心：`error_t`/`context_t`/`message_t`/`socket_t`/`poller_t`/`monitor_t`/`timers`、buffer 抽象、sockopt 标签 |
| `zmq_addon.hpp` | ~859 | 扩展：`multipart_t`、`recv_multipart`/`send_multipart`/`encode`/`decode`、`active_poller_t`、`poller_ref_t` |

`zmq_addon.hpp` 首行 `#include "zmq.hpp"`，使用扩展功能只需包含 addon。

## 2. 命名空间布局

- 全部公开 API 位于 `namespace zmq`。
- `zmq::detail`：实现细节（`socket_base`、`poll`、`trivial_optional`、`enum_bit_*`、range 推导工具），不对外保证稳定。
- `zmq::sockopt`：套接字选项标签类型（`integral_option`/`array_option`）。
- `zmq::literals`：`_zbuf` 用户定义字面量。
- `std`：仅对 `zmq::socket_ref`、`zmq::poller_ref_t` 做 `std::hash` 特化。

## 3. 核心设计目标

1. **零成本 RAII**：`context_t`/`socket_t`/`message_t` 析构自动释放资源，禁用拷贝、支持移动；无额外分配、无虚函数开销（`monitor_t` 除外，它为事件回调而虚）。
2. **类型安全**：用 `enum class`（`socket_type`/`send_flags`/`recv_flags`/`event_flags`/`ctxopt`）替代裸整型；用 `sockopt` 标签类型把选项名/值类型/长度编码进编译期。
3. **统一内存抽象**：`const_buffer`/`mutable_buffer` + `buffer()` 重载族让 send/recv 接受任意连续 POD 容器。
4. **现代 C++ 兼容**：通过 `ZMQ_CPP11/14/17` 宏与 `CPPZMQ_HAS_OPTIONAL`/`CPPZMQ_HAS_STRING_VIEW` 自适应，同时用 `trivial_optional` 等兜底 C++11。
5. **错误显式化**：C API 的 `-1`/`nullptr` 返回被翻译为 `error_t` 异常或 `optional`（EAGAIN 用 `nullopt` 表达"现在不可用"而非异常）。

## 4. 条件编译开关

- `ZMQ_BUILD_DRAFT_API`：启用 Draft API（`poller_t`/`active_poller_t`、Draft 套接字类型 `server`/`client`/`radio`/`dish` 等）。
- `ZMQ_HAVE_POLLER`：libzmq 提供 `zmq_poller_*` 时启用 `poller_t`。
- `ZMQ_HAVE_TIMERS`：启用 `timers` 类。
- `ZMQ_HAVE_CURVE`：启用 `curve_keypair`/`curve_public`。
- `CPPZMQ_HAS_OPTIONAL`/`CPPZMQ_HAS_STRING_VIEW`：C++17 设施探测。

## 5. 与 libzmq 的分层关系

```
应用代码
  ↓
cppzmq（zmq.hpp / zmq_addon.hpp）：RAII、类型安全、buffer、多部分
  ↓
libzmq（<zmq.h>）：zmq_ctx_*、zmq_socket、zmq_msg_*、zmq_poller_*、zmq_send/recv
  ↓
操作系统网络栈
```

cppzmq 不引入额外线程或缓冲，绝大多数调用直接 inline 转发到 libzmq。

## 相关概念

- [01 context_t](/concepts/01-context.md) · [02 socket_t](/concepts/02-socket.md) · [03 message 与 buffer](/concepts/03-message-and-buffer.md)
- [04 错误处理](/concepts/04-error-handling.md) · [05 poller](/concepts/05-poller.md) · [06 multipart](/concepts/06-multipart.md)
- [信源：zmq.hpp](/references/zmq-hpp.md)
