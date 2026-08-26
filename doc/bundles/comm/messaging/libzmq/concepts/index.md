# 概念文档

## 架构基础篇

* [00 整体架构总览](00-overview.md) — 四层管线模型、线程模型、公共 C API 全景
* [01 上下文与基础设施](01-context.md) — ctx_t 延迟启动、I/O 线程池、reaper 终止序列
* [02 套接字基类 socket_base_t](02-socket-base.md) — 模板方法模式、x-钩子体系、bind/connect 流程
* [03 消息 msg_t 与引用计数](03-message.md) — 六类型、content_t 引用计数、零拷贝
* [04 管道 pipe_t 与流控](04-pipe.md) — pipepair、ypipe 无锁队列、HWM/LWM 流控
* [05 会话与连接生命周期](05-session.md) — session_base_t、connecter/listener、重连退避
* [06 ZMTP 协议引擎](06-zmtp-engine.md) — greeting 帧结构、握手状态机、安全机制、心跳

## 核心机制篇

* [07 I/O 线程与多路复用](07-io-thread-poller.md) — io_thread 主循环、poller 平台抽象、signaler
* [08 命令传递与邮箱](08-command-mailbox.md) — 22 种命令、mailbox_t、条件变量
* [09 套接字选项体系](09-options.md) — options_t 全字段、HWM/linger/timeout/heartbeat/security
* [10 传输层](10-transport.md) — TCP/IPC/inproc、URI 解析、重连退避

## 高级功能篇

* [11 消息模式实现](11-patterns.md) — fq/lb/dist 算法、ROUTER 路由、PUB/SUB trie/mtrie 过滤
* [12 编解码与帧格式](12-encoder-decoder.md) — v2_encoder/decoder 状态机、零拷贝、命令帧

```{toctree}
:maxdepth: 7

00-overview
01-context
02-socket-base
03-message
04-pipe
05-session
06-zmtp-engine
07-io-thread-poller
08-command-mailbox
09-options
10-transport
11-patterns
12-encoder-decoder
```
