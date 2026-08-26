---
type: bundle
title: "ZeroMQ 核心库（libzmq）"
okf_version: "0.2"
---

# ZeroMQ 核心库（libzmq）知识库

本知识包是高性能异步消息库 [ZeroMQ](https://zeromq.org/)（MPL-2.0 许可证）核心 C++ 库 libzmq 的系统化中文源码教程，基于 libzmq 4.3.6 源码（`external/libs/remote/libzmq/` 目录）深度阅读生成，覆盖从公共 C API 到内部 C++ 对象层次、从四层管线架构到消息模式实现的完整知识体系。所有内容均溯源至 libzmq 源码核心模块，遵循 [OKF v0.2 规范](concepts/00-overview.md)。

## 架构基础篇（concepts/）

* [libzmq 整体架构总览](concepts/00-overview.md) — 四层管线模型（socket→pipe→session→engine）、线程模型（应用线程与 I/O 线程通过 mailbox 解耦）、公共 C API 全景、套接字不是网络套接字而是异步消息队列的核心认知。
* [上下文与基础设施](concepts/01-context.md) — ctx_t 延迟启动机制、slot 槽位分配、I/O 线程池管理、reaper 终止序列、inproc 端点注册表、choose_io_thread 负载选择。
* [套接字基类 socket_base_t](concepts/02-socket-base.md) — 多继承结构、模板方法模式的 x-钩子体系、send/recv 骨架算法与超时重试、bind/connect 流程、线程安全 mailbox_safe_t、routing_socket_base_t 路由表。
* [消息 msg_t 与引用计数](concepts/03-message.md) — 64 字节内存布局、六种内部类型（VSM/LMSG/CMSG/ZCLMSG/delimiter/join-leave）、content_t 原子引用计数、copy/move/close 生命周期、零拷贝发送与接收。
* [管道 pipe_t 与流控](concepts/04-pipe.md) — pipepair 双向管道、ypipe_t 单读单写无锁队列、HWM/LWM 背压流控、六种终止状态机、conflate 只保留最新消息模式、flush 唤醒机制。
* [会话 session_base_t 与连接生命周期](concepts/05-session.md) — 主动/被动会话区别、tcp_connecter 非阻塞连接、tcp_listener accept 流程、指数退避重连、engine 插拔与引擎就绪通知、ZAP 认证管道。
* [ZMTP 协议引擎](concepts/06-zmtp-engine.md) — greeting 64 字节帧结构、函数指针握手状态机（v1.0/v2.0/v3.0/v3.1）、NULL/PLAIN/CURVE/GSSAPI 安全机制创建、心跳定时器、stream_engine_base 编解码缓冲区。

## 核心机制篇（concepts/）

* [I/O 线程与多路复用](concepts/07-io-thread-poller.md) — io_thread 主循环批量处理 mailbox 命令、poller 平台抽象（epoll/kqueue/select 编译时选择）、io_object_t fd 事件适配器、signaler_t 跨平台 eventfd 封装、yqueue 批量内存块分配。
* [命令传递与邮箱](concepts/08-command-mailbox.md) — 22 种命令类型及 union 参数、object_t 的 send/process 方法对、mailbox_t 基于 ypipe+signaler、mailbox_safe_t 条件变量、应用线程 process_commands 命令处理循环。
* [套接字选项体系](concepts/09-options.md) — options_t 全字段分类、HWM/LINGER/TIMEOUT 行为语义、CURVE 密钥长度与 Z85 编码、心跳选项、选项在 bind/connect 时的值复制时机、只读选项。
* [传输层](concepts/10-transport.md) — TCP connecter/listener 非阻塞连接与 accept、inproc 进程内直连零拷贝、IPC Unix 域套接字、URI 解析、stream_connecter_base 指数退避重连、各传输协议特性对比。

## 高级功能篇（concepts/）

* [消息模式实现](concepts/11-patterns.md) — fq_t 公平队列/lb_t 负载均衡/dist_t 发布分发算法、DEALER/ROUTER 路由策略、PUB/SUB 的 trie/mtrie 双端订阅过滤、REQ/REP 严格状态机、PUSH/PULL 流水线、模板方法模式在各模式中的应用。
* [编解码与帧格式](concepts/12-encoder-decoder.md) — v2_encoder CRTP 状态机（size_ready/message_ready）、v2_decoder 零拷贝接收、ZMTP 长短帧格式、i_encoder/i_decoder 接口、编码器零拷贝优化、SUBSCRIBE/PING/PONG 命令帧类型。

## 实战示例（examples/）

* [PUSH/PULL 流水线模式](examples/push-pull-pipeline.md) — 任务分发器+多工作者+结果收集器完整 C 代码，演示 lb_t 轮询负载均衡、fq_t 公平队列、HWM 流控行为，含编译运行说明。
* [PUB/SUB 主题订阅与过滤](examples/pub-sub-filtering.md) — 天气更新发布者+多主题订阅者完整 C 代码，演示 ZMQ_SUBSCRIBE 前缀匹配、trie/mtrie 双端过滤、多部分消息主题帧、订阅取消。
* [ROUTER/DEALER 异步请求-回复](examples/router-dealer-async.md) — 异步服务端+多 worker+多客户端完整 C 代码，演示 identity 路由帧、多部分消息信封结构、ZMQ_ROUTER_MANDATORY、非阻塞异步模式。
* [inproc 线程间零拷贝通信](examples/inproc-zero-copy.md) — 多线程 inproc 完整 C 代码，演示 zmq_msg_init_data 发送端零拷贝、zmq_msg_move 所有权转移、content_t 引用计数共享、VSM/LMSG 消息类型差异。

## 信源登记簿（references/）

* [zmq.h：公共 C API 完整索引](references/zmq-h-api.md) — 版本宏、上下文生命周期函数、消息操作函数集、12 种稳定套接字类型枚举、套接字选项常量、安全机制常量、zmq_pollitem_t 结构体、监控事件、zmq_proxy 函数。
* [ctx_t：上下文基础设施完整索引](references/ctx.md) — thread_ctx_t 基类、ctx_t 关键成员表、endpoint_t 结构体、start 延迟启动时序、create_socket 槽位分配、terminate 等待 reaper 完成、choose_io_thread 负载选择。
* [socket_base_t：套接字基类完整索引](references/socket-base.md) — 多继承结构、纯虚钩子对照表、pipe 数组与 mailbox、工厂方法类型映射、bind/connect inproc 与网络协议分支、线程安全 mailbox_safe_t、routing_socket_base_t 路由表。
* [msg_t：消息内部结构与引用计数完整索引](references/msg.md) — 64 字节 union 内存布局、六种 type_t 枚举、content_t 引用计数结构、init_size/copy/move/close 实现细节、命令帧标志位、C API 与 C++ 方法对照表。
* [ZMTP 线协议：帧格式与握手完整索引](references/zmtp-wire-protocol.md) — greeting 64 字节逐字段布局、握手函数指针选择逻辑、安全机制创建对照表、心跳定时器 ID、v2_encoder/decoder 状态、stream_engine_base 成员、i_engine 接口。
* [command_t 与 mailbox：命令传递完整索引](references/command.md) — 22 种命令类型用途表、union 参数结构、mailbox_t ypipe+signaler 实现、mailbox_safe_t 条件变量、signaler_t 跨平台 eventfd/pipe 封装、own_t 终止命令流。
* [options_t：套接字选项完整索引](references/options.md) — 全字段分类表（流控/超时/安全/心跳/网络）、CURVE 密钥长度、setsockopt 选项常量值速查表、四种安全机制对比、上下文选项 vs 套接字选项。

## 信任与生命周期说明

* **status 判定依据**：全部 24 个内容文档（13 个概念 + 4 个示例 + 7 个信源登记）均 `status: stable`。内容基于对 libzmq 4.3.6 源码（`external/libs/remote/libzmq/` 目录）核心模块的逐文件阅读与事实提取（93 条源码事实 F-001~F-093），经 seven-concepts 方法论 R→I→E 三阶段流程生成。
* **stale_after 解释**：统一设置为 `2027-08-23`。libzmq 核心架构（四层管线/mailbox 命令传递/ZMTP 3.x/模板方法模式）自 4.x 以来保持稳定，新传输和 Draft API 不断添加但核心设计不变；该日期作为针对未来大版本（如 5.x 引入 breaking change）的保守重新评估节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻；`verified.at` 记录 V 阶段对抗审查核验事件，两者分离、可追溯。所有类名/函数名/结构体字段均来自 facts.md 登记的源码事实，无虚构 API。

本知识包共收录 24 个内容文档（13 个概念 + 4 个示例 + 7 个信源登记），另含 3 个子目录 index.md 与根 index.md、log.md。

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
spec/index
log
```
