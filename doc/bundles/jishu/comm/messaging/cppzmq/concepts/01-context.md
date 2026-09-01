---
type: concept
title: "context_t 上下文"
description: "ZeroMQ 上下文的 RAII 封装，ctxopt 类型安全选项、shutdown/close 语义与移动语义"
tags: [cppzmq, zeromq, context, raii]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [/references/zmq-hpp.md]
  facts: [F-025, F-026, F-027, F-028, F-029]
---

# context_t 上下文

`zmq::context_t` 封装 `void*`（`zmq_ctx_new` 的返回值），管理 ZeroMQ 上下文的生命周期。一个进程通常只需一个 context。

## 构造

```c++
zmq::context_t ctx;                       // 默认：zmq_ctx_new()
zmq::context_t ctx(1);                    // io_threads=1, max_sockets=默认
zmq::context_t ctx(1, 1024);              // 指定 io_threads 与 max_sockets
```

带参构造在 `zmq_ctx_new` 后调用 `zmq_ctx_set(ZMQ_IO_THREADS)` 与 `zmq_ctx_set(ZMQ_MAX_SOCKETS)`，失败用 `ZMQ_ASSERT`（编程错误即崩溃，不走异常）。

## 类型安全选项：ctxopt

`enum class ctxopt` 强类型映射所有上下文选项（`io_threads`/`max_sockets`/`blocky`/`thread_priority`/`ipv6`/`max_msgsz` 等）：

```c++
ctx.set(zmq::ctxopt::io_threads, 2);
int n = ctx.get(zmq::ctxopt::max_sockets);
```

`set` 在 `zmq_ctx_set` 返回 -1 时抛 `error_t`；`get` 同理。旧的 `setctxopt(int,int)`/`getctxopt(int)` 已废弃。

## shutdown 与 close 的区别

- `shutdown()`：调用 `zmq_ctx_shutdown`，使所有阻塞中的 socket 操作立即以 `ETERM` 返回，并禁止后续 socket 操作。**不阻塞**，用于发起关停。
- `close()`：调用 `zmq_ctx_term`，**阻塞**直到其上所有 socket 关闭、待发消息处理完毕（或超过 linger）。内含 `EINTR` 重试循环。幂等（`ptr==nullptr` 直接返回）。
- 析构 `~context_t()` 调用 `close()`。

推荐关停顺序：`ctx.shutdown()` → join 所有工作线程（线程内 recv/poll 因 ETERM 退出）→ 让 `ctx` 析构或显式 `ctx.close()`。

## 移动语义

```c++
zmq::context_t a;
zmq::context_t b = std::move(a);   // a.ptr 置空
b = std::move(a2);                 // 先 close(b) 再 swap
```

拷贝构造/赋值被删除。`swap()` 与自由 `swap()` 可用。

## 与 C API 互操作

- `handle()` 返回 `void*`，可直接传给仍需 C 句柄的接口。
- `explicit operator void*()` / `operator bool()` 便于判空，但前者已不推荐，建议 `handle() != nullptr`。

## 相关概念

- [02 socket_t](02-socket.md)：socket 必须由 context 创建
- [04 错误处理](04-error-handling.md)：ETERM 与 error_t
- [信源：zmq.hpp](../references/zmq-hpp.md)
