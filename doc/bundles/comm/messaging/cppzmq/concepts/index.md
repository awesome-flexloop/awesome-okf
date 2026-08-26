# cppzmq 概念文档

* [00 整体架构与设计目标](00-overview.md) — header-only 形态、与 libzmq 的分层、命名空间布局、C++11/14/17 兼容垫片、五大设计目标。
* [01 context_t 上下文](01-context.md) — ctxopt 强类型选项、io_threads/max_sockets、shutdown vs close、EINTR 重试循环、移动语义。
* [02 socket_t 与套接字层](02-socket.md) — socket_type 枚举、bind/connect、send/recv optional 结果、sockopt 标签机制、socket_ref 非拥有引用、proxy。
* [03 message_t 与 buffer 抽象](03-message-and-buffer.md) — 消息构造函数族、移动/禁拷贝语义、零拷贝 free_fn、const_buffer/mutable_buffer、buffer() 重载族、str_buffer/_zbuf。
* [04 错误处理](04-error-handling.md) — error_t（继承 std::exception）、EAGAIN 与 optional 返回值、ZMQ_ASSERT 边界、EINTR 重试、ETERM 关停、常见错误码。
* [05 poller_t 与事件多路复用](05-poller.md) — event_flags、poller_event<T> 布局兼容、add/remove/modify/wait_all、active_poller_t 回调分发、poller_ref_t。
* [06 multipart 高层抽象](06-multipart.md) — recv_multipart/send_multipart 迭代器接口、multipart_t 容器、encode/decode（RFC 50）、选型建议。

```{toctree}
:maxdepth: 7

00-overview
01-context
02-socket
03-message-and-buffer
04-error-handling
05-poller
06-multipart
```
