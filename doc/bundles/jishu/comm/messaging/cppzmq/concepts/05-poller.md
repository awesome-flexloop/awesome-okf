---
type: concept
title: "poller_t 与事件多路复用"
description: "基于 zmq_poller_* 的类型安全轮询，poller_event<T> 布局兼容，以及 active_poller_t 回调分发"
tags: [cppzmq, zeromq, poller, event-loop, draft-api]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [/references/zmq-hpp.md, /references/zmq-addon-hpp.md]
  facts: [F-007, F-046, F-047, F-051, F-056]
---

# poller_t 与事件多路复用

> 依赖 `ZMQ_BUILD_DRAFT_API` + `ZMQ_CPP11` + `ZMQ_HAVE_POLLER`（libzmq 的 Draft poller API）。

## event_flags

```c++
enum class event_flags : short {
    none = 0,
    pollin = ZMQ_POLLIN,
    pollout = ZMQ_POLLOUT,
    pollerr = ZMQ_POLLERR,
    pollpri = ZMQ_POLLPRI
};
```

支持 `| & ^ ~` 位运算（通过 `detail::enum_bit_*`）。

## poller_event<T>：布局兼容

```c++
template<class T = no_user_data>
struct poller_event {
    socket_ref socket;
    zmq::fd_t  fd;
    T*         user_data;
    event_flags events;
};
```

与 C 的 `zmq_poller_event_t` **二进制布局兼容**（测试用 `static_assert(sizeof/alignof)` 验证），因此可直接 `reinterpret_cast` 传给 `zmq_poller_wait_all`，零拷贝取回事件，且 `user_data` 以强类型 `T*` 返回。

## poller_t<T>

```c++
zmq::poller_t<> poller;                       // 无 user_data
poller.add(sock, zmq::event_flags::pollin);

zmq::poller_t<MyData> poller2;
MyData data;
poller2.add(sock, zmq::event_flags::pollin|zmq::event_flags::pollout, &data);
poller2.add(fd, zmq::event_flags::pollin, &data);   // 也支持原生 fd

poller.modify(sock, zmq::event_flags::pollout);
poller.remove(sock);

auto ev = poller.wait(std::chrono::milliseconds{100});  // optional<event_type>
if (ev) { /* ev->socket / ev->user_data / ev->events */ }

std::vector<zmq::poller_event<MyData>> events(16);
size_t n = poller.wait_all(events, timeout);   // 返回就绪数
```

- `poller_t<>`（默认 `no_user_data`）通过 SFINAE **禁止**三参 `add`——不需要用户数据时 API 面不暴露该参数。
- 内部用 `std::unique_ptr<void, destroy_poller_t>` 管理 `zmq_poller_new/destroy`，自动释放；因此不可拷贝、可移动、可 swap。
- `wait_all(Sequence&)` 静态断言 `Sequence::value_type == event_type`。
- `size()`（libzmq 4.3.3+）返回已注册项数。

## 旧式 poll() 自由函数

在 Draft poller 之外，仍提供 `zmq::poll(zmq_pollitem_t*, size_t, timeout)` 系列重载（接受 `std::vector`/`std::array` + `std::chrono::milliseconds`），包装 `zmq_poll`。新代码优先用 `poller_t`。

## active_poller_t：回调式分发

`zmq_addon.hpp` 在 `poller_t<std::function<...>>` 之上封装了注册-回调模型：

```c++
zmq::active_poller_t ap;
ap.add(sock, zmq::event_flags::pollin, [](zmq::event_flags ev){
    if (ev & zmq::event_flags::pollin) { /* 可读 */ }
});
ap.add(fd, zmq::event_flags::pollin, handler);

while (true) {
    ap.wait(std::chrono::milliseconds{-1});  // 内部 wait_all 并自动调用 handler
}
```

关键实现：
- `handler_type = std::function<void(event_flags)>`，以 `shared_ptr<handler_type>` 存入 `unordered_map<poller_ref_t, shared_ptr<handler>>`，并把 `shared_ptr.get()` 作为 `poller_t` 的 user_data。
- `poller_ref_t` 是 `(RT_SOCKET/RT_FD 标签, socket_ref, fd_t)` 的可哈希 tuple，使 socket 与 fd 可在同一 map 中共存不冲突。
- `add` 空 handler 抛 `std::invalid_argument`；重复注册抛 `error_t(EINVAL)`；底层 `poller.add` 失败时回滚 map 插入（异常安全）。
- `wait` 在 `need_rebuild` 时重建事件/handler 向量（任何 add/remove 后标记），再 `wait_all` 并逐个执行 `(*event.user_data)(event.events)`。
- 不可拷贝、可移动；提供 `empty()`/`size()`。

## 选型建议

| 需求 | 选择 |
|---|---|
| 自行管理事件循环、需携带自定义上下文 | `poller_t<MyData>` |
| 偏好回调注册、事件处理分散到各 handler | `active_poller_t` |
| 兼容旧代码 / 简单 POD 数组轮询 | `zmq::poll(...)` |

## 相关概念

- [02 socket_t](02-socket.md)：socket_ref
- [06 multipart](06-multipart.md)：多部分消息常与 poller 配合
- [信源：zmq.hpp](../references/zmq-hpp.md) · [信源：zmq_addon.hpp](../references/zmq-addon-hpp.md)
