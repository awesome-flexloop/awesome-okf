# Concepts

pyzmq 核心概念文档，按学习路径排列。

| 编号 | 文档 | 说明 |
|------|------|------|
| 00 | [整体架构与双后端机制](00-architecture-dual-backend.md) | Cython/CFFI 双后端、sugar 层职责、public_api 契约、导入顺序、COPY_THRESHOLD |
| 01 | [Context 生命周期与资源管理](01-context-lifecycle.md) | 单例、shadow、term/destroy、WeakSet、sockopts、fork 安全 |
| 02 | [Socket 与 sugar 语法层](02-socket-sugar.md) | bind/connect 上下文管理器、send/recv、序列化、订阅、监控、装饰器 |
| 03 | [Frame 与消息](03-frame-message.md) | bytes 子类、zero-copy、MessageTracker、GC 回调、draft 属性 |
| 04 | [Poller 多路复用与 select 兼容](04-poller.md) | register/poll、POLLIN/POLLOUT、原生 fd、zmq.select |
| 05 | [异步双路径：Future 状态机与 asyncio 集成](05-async-future-asyncio.md) | _AsyncSocket 状态机、shadow socket、asyncio/tornado 双适配、Windows 兼容 |
| 06 | [认证与 ZAP](06-auth-zap.md) | ZAP 协议、Authenticator、PLAIN/CURVE、Thread/Asyncio 认证器、证书管理 |
| 07 | [生态模块：eventloop、green、devices、log 与 utils](07-ecosystem-eventloop-green-devices-log.md) | tornado 集成、gevent 适配、设备代理、PUBHandler 日志、jsonapi |

```{toctree}
:maxdepth: 7

00-architecture-dual-backend
01-context-lifecycle
02-socket-sugar
03-frame-message
04-poller
05-async-future-asyncio
06-auth-zap
07-ecosystem-eventloop-green-devices-log
```
