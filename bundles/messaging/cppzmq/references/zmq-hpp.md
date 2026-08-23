---
type: reference
title: "zmq.hpp 文件参考"
description: "cppzmq 核心头文件 zmq.hpp 的行号索引、类/函数/宏清单与条件编译开关"
tags: [cppzmq, zeromq, reference, zmq.hpp]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  - path: "external/libs/remote/cppzmq/zmq.hpp"
    facts: [F-001, F-002, F-003, F-004, F-005, F-006, F-007, F-008, F-009, F-010, F-011, F-012, F-013, F-014, F-015, F-016, F-017, F-018, F-019, F-020, F-021, F-022, F-023, F-024, F-025, F-026, F-027, F-028, F-029, F-030, F-031, F-032, F-033, F-034, F-035, F-036, F-037, F-038, F-039, F-040, F-041, F-042, F-043, F-044, F-045, F-046, F-047, F-048, F-049, F-050]
---

# zmq.hpp 文件参考

cppzmq 核心头文件，header-only。包含 `<zmq.h>` 后在 `namespace zmq` 内提供全部核心封装。

## 行号索引（按出现顺序）

| 行号 | 内容 |
|---|---|
| L26-L42 | Windows `NOMINMAX` 与 min/max 宏保存恢复 |
| L44-L116 | C++ 标准检测（`CPPZMQ_LANG`/`ZMQ_CPP11/14/17`）与兼容宏（`ZMQ_NOTHROW`/`ZMQ_NODISCARD`/`ZMQ_DEPRECATED` 等） |
| L118-L158 | 标准库头文件；`<optional>`/`<string_view>` 探测（`CPPZMQ_HAS_OPTIONAL`/`CPPZMQ_HAS_STRING_VIEW`） |
| L160-L167 | 版本宏 `CPPZMQ_VERSION_MAJOR/MINOR/PATCH = 4/11/0` |
| L169-L210 | 右值引用/删除函数检测、`ZMQ_IS_TRIVIALLY_COPYABLE` |
| L212-L229 | 旧 monitor 事件布局、`zmq_msg_recv` 兼容宏 |
| L240-L286 | `namespace detail`：ranges ADL、`is_range`、`void_t`、迭代器别名 |
| L288-L300 | `free_fn`/`pollitem_t` 类型别名、平台相关 `fd_t` |
| L302-L315 | **`error_t`**：继承 `std::exception`，`num()`/`what()` |
| L317-L395 | `detail::poll` 与多组 `poll()` 自由函数重载（含废弃版本） |
| L398-L409 | `version()` 两种重载 |
| L426-L770 | **`message_t`**：构造族、移动/禁拷贝、rebuild/move/copy、data/size/more、get/gets、routing_id/group、to_string/str、swap、handle |
| L773-L814 | `enum class ctxopt` |
| L817-L934 | **`context_t`**：构造/移动/析构、set/get(ctxopt)、close/shutdown、handle、swap |
| L938-L1018 | `recv_buffer_size`、`send_result_t`/`recv_result_t`/`recv_buffer_result_t`、`trivial_optional` 兜底 |
| L1020-L1095 | `enum class send_flags`/`recv_flags` 与位运算符 |
| L1098-L1400 | **buffer 抽象**：`mutable_buffer`/`const_buffer`、`buffer()` 重载族、`str_buffer`、`literals::operator""_zbuf` |
| L1403-L1432 | `enum class socket_type` |
| L1435-L1759 | **`namespace sockopt`**：`integral_option`/`array_option` 标签与约 80 个选项宏声明 |
| L1763-L2149 | `detail::socket_base`：setsockopt/getsockopt（废弃）、set/get 模板、bind/unbind/connect/disconnect、send/recv 重载族、join/leave、handle、operator bool |
| L2151-L2160 | `from_handle_t`/`from_handle` |
| L2164-L2194 | `socket_ref`（非拥有引用）与 nullptr 比较 |
| L2196-L2240 | `socket_base` 比较运算符、`std::hash<socket_ref>` 特化 |
| L2244-L2327 | **`socket_t`**：拥有型 RAII，友元 monitor_t，移动/禁拷贝，close，隐式转 socket_ref |
| L2329-L2365 | `proxy`/`proxy_steerable` |
| L2367-L2674 | **`monitor_t`**：init/monitor/check_event/process_event、虚 `on_event_*`、内部 PAIR socket |
| L2676-L2864 | **`event_flags`**、**`poller_event<T>`**、**`poller_t<T>`**（Draft）：add/remove/modify/wait/wait_all/size、`destroy_poller_t` |
| L2866-L2869 | `operator<<(ostream&, message_t)` |
| L2871-L2948 | **`timers`** 类（ZMQ_HAVE_TIMERS） |
| L2950-L2971 | `curve_keypair`/`curve_public`（ZMQ_HAVE_CURVE） |
| L2975-L2995 | `z85_encode`/`z85_decode` |
| L2999-L3008 | Windows min/max 宏恢复 |

## 关键条件编译开关

| 宏 | 效果 |
|---|---|
| `ZMQ_CPP11/14/17` | 启用对应标准特性；自动检测 |
| `ZMQ_BUILD_DRAFT_API` | Draft 套接字类型、`poller_t`、routing_id/group、join/leave |
| `ZMQ_HAVE_POLLER` | 启用 `poller_t`（libzmq 提供 zmq_poller_*） |
| `ZMQ_HAVE_TIMERS` | 启用 `timers` 类 |
| `ZMQ_HAVE_CURVE` | 启用 curve 密钥函数 |
| `CPPZMQ_HAS_OPTIONAL` | 使用 `std::optional`，否则用 `trivial_optional` |
| `CPPZMQ_HAS_STRING_VIEW` | 启用 `std::string_view` 构造/重载 |
| `ZMQ_CPP11_PARTIAL` | 旧 GCC/libstdc++ 部分 C++11 支持的兼容路径 |
| `ZMQ_EXTENDED_CONSTEXPR` | 更严格的 constexpr 断言（buffer 非空检查） |
| `ZMQ_VERSION >= ZMQ_MAKE_VERSION(...)` | 按 libzmq 版本启用/屏蔽 API |

## 设计要点

- 所有资源类在 `zmq` 命名空间，实现在 `detail` 命名空间。
- 错误：`error_t` 异常用于真错误；`optional` 空值用于 EAGAIN。
- 选项：`sockopt` 标签 + `socket_base::set/get` 模板，编译期类型安全。
- 轮询：旧 `zmq::poll(POD)` 与新 Draft `poller_t<T>` 并存。
