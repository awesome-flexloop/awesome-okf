# cppzmq 示例文档

* [Hello World（REQ-REP）](hello-world.md) — 最小 REQ/REP 回显示例，展示 context_t/socket_t/message_t/buffer 两种发送方式与 optional 错误处理。
* [多部分消息与 poller](multipart-poller.md) — send_multipart/recv_multipart、multipart_t 拼装拆解、active_poller_t 回调事件循环、poller_t<T> 强类型用户数据、RFC 50 编码。

```{toctree}
:hidden:
:maxdepth: 7

hello-world
multipart-poller
```
