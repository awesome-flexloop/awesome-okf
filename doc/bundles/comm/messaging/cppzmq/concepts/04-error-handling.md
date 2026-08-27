---
type: concept
title: "错误处理"
description: "error_t 异常类、EAGAIN 与 optional 返回值的分工、断言与异常的边界"
tags: [cppzmq, zeromq, error, exception]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [/references/zmq-hpp.md]
  facts: [F-004, F-007, F-030]
---

# 错误处理

## error_t：ZeroMQ 异常

```c++
class error_t : public std::exception {
  public:
    error_t() noexcept : errnum(zmq_errno()) {}
    explicit error_t(int err) noexcept : errnum(err) {}
    const char* what() const noexcept override { return zmq_strerror(errnum); }
    int num() const noexcept { return errnum; }
  private:
    int errnum;
};
```

- 继承自 **`std::exception`**（非 `std::system_error`）。
- 默认构造自动捕获 `zmq_errno()`；也可用显式错误码构造（如 `error_t(EINVAL)`）。
- `what()` 返回 `zmq_strerror`；`num()` 返回数字错误码，可与 `EAGAIN`/`ETERM`/`EINTR` 等比较。

## 两种失败模式：异常 vs optional

cppzmq 刻意区分两类失败：

1. **真正的错误**（参数非法、连接失败、上下文已终止等）→ 抛 `error_t`。
   例：`bind`/`connect` 失败、`zmq_msg_init_size` 返回 -1、`sockopt` set/get 返回 -1。

2. **"现在不可用"**（非阻塞操作遇到 EAGAIN）→ 返回 `optional`，用空值表达，**不抛异常**。
   - `send_result_t = optional<size_t>`：`nullopt` 表示 EAGAIN。
   - `recv_result_t = optional<size_t>`：同上。
   - `recv_buffer_result_t = optional<recv_buffer_size>`：同上。

```c++
auto r = sock.send(buf, zmq::send_flags::dontwait);
if (!r) {
    // EAGAIN：发送队列满，稍后重试
} else {
    // *r 为发送字节数
}
```

无 C++17 `<optional>` 时，cppzmq 提供 `detail::trivial_optional<T>`（要求 `T` trivial）兜底，接口一致（`operator->`/`operator*`/`has_value`/`operator bool`）。

## 断言（ZMQ_ASSERT）的边界

对于"编程契约违反"而非运行时错误的情况，cppzmq 使用 `ZMQ_ASSERT(expression)`：
- Debug 构建下是 `assert`；
- Release 构建下退化为 `(void)(expression)`，不产生检查。

典型场景：`zmq_msg_init`（无内存分配，理论上不失败）、`zmq_ctx_set` 在构造期对已知合法选项、`zmq_close`/`zmq_msg_close` 析构期。这些不应在正确程序中失败，故不抛异常。

## EINTR 重试

`context_t::close()` 对 `zmq_ctx_term` 的 `EINTR` 做了循环重试（信号中断不视为失败）：

```c++
do { rc = zmq_ctx_term(ptr); } while (rc == -1 && errno == EINTR);
```

但 `poll`/`send`/`recv` 等操作**不**自动重试 EINTR——若信号中断，会作为错误抛出或返回，由调用方决定是否重试。

## ETERM 与关停

当 context 被 `shutdown()`/`close()` 后，其上所有阻塞操作以 `ETERM` 返回。在 `monitor_t::process_event` 等内部循环中，`ETERM` 被当作正常退出信号（return false）而非异常。应用层工作线程通常也应捕获 `error_t` 并检查 `num() == ETERM` 来优雅退出。

## 常见错误码

| 错误码 | 含义 | 典型场景 |
|---|---|---|
| `EAGAIN` | 非阻塞操作暂不可用 | `dontwait` send/recv/poll 超时 |
| `ETERM` | context 已终止 | shutdown 后的 socket 操作 |
| `EINTR` | 被信号中断 | 阻塞操作（term 内部已重试） |
| `EINVAL` | 参数非法 | 重复 add poller、无效选项值 |
| `EFSM` | 状态机错误 | 在错误状态发送（如 REP 未 recv 先 send） |

## 相关概念

- [01 context_t](01-context.md)：shutdown/ETERM
- [02 socket_t](02-socket.md)：send/recv optional
- [信源：zmq.hpp](../references/zmq-hpp.md)
