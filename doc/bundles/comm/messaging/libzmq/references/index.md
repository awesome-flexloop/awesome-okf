# 信源登记簿

* [zmq.h：公共 C API 完整索引](zmq-h-api.md) — include/zmq.h 中的全部公共 API、常量枚举、结构体
* [ctx_t：上下文基础设施完整索引](ctx.md) — src/ctx.hpp/cpp 的 ctx_t 类成员与启动/终止时序
* [socket_base_t：套接字基类完整索引](socket-base.md) — src/socket_base.hpp/cpp 的多继承、钩子、工厂方法
* [msg_t：消息内部结构与引用计数完整索引](msg.md) — src/msg.hpp/cpp 的 union 布局、六类型、引用计数
* [ZMTP 线协议：帧格式与握手完整索引](zmtp-wire-protocol.md) — zmtp_engine、v2_encoder/decoder、greeting 字节布局
* [command_t 与 mailbox：命令传递完整索引](command.md) — command.hpp、mailbox、signaler 的命令传递机制
* [options_t：套接字选项完整索引](options.md) — src/options.hpp 的全字段类型/默认值/选项常量

```{toctree}
:hidden:

command
ctx
msg
options
socket-base
zmq-h-api
zmtp-wire-protocol
```
