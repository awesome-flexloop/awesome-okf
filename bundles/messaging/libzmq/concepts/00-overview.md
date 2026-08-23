---
type: concept
title: "libzmq 整体架构总览"
description: "libzmq 的四层管线模型（socket→pipe→session→engine）、线程模型、公共 C API 全景、消息模式分类，理解 ZeroMQ 套接字不是网络套接字而是异步消息队列"
tags: [libzmq, zeromq, architecture, overview, socket, zmtp]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [../references/zmq-h-api.md, ../references/socket-base.md]
  facts: [F-001, F-002, F-003, F-006, F-007, F-008, F-009, F-010, F-011, F-023, F-024, F-025, F-026]
---

# libzmq 整体架构总览

## 核心理解

libzmq（ZeroMQ 核心 C++ 库）是一个**异步消息传递库**。它不是一个消息 broker（代理服务器），而是一个嵌入式库，直接链接到应用程序进程中，提供类似套接字的 API，但在底层自动处理 I/O 线程管理、连接重连、消息帧编解码、多模式路由等复杂性。

本知识包基于 libzmq 4.3.6 版本源码（`ZMQ_VERSION_MAJOR=4, MINOR=3, PATCH=6`，F-001）深度阅读生成，覆盖从公共 C API 到内部 C++ 对象层次的完整架构。

## 最关键的认知：套接字不是网络套接字

使用 libzmq 最反直觉的一点是：`zmq_socket()` 返回的不是操作系统的文件描述符，而是一个驻留在应用线程中的 C++ 对象（`socket_base_t`）。真正的网络 I/O 发生在独立的 I/O 线程中。

消息从应用线程到达网络，需要经过四层管线：

```
应用线程                     I/O 线程
┌───────────────┐          ┌──────────────────────────────────┐
│ socket_base_t │◄─pipe_t─►│ session_base_t ◄─► zmtp_engine_t │
│  (消息模式)    │  (无锁)  │  (连接生命周期)    (ZMTP编解码)    │
└───────────────┘          └──────────────────────────────────┘
                                 ▲
                                 │ TCP/IPC/PGM/INPROC
                                 ▼
```

### 第一层：socket_base_t（应用线程）

`socket_base_t`（F-023）运行在创建它的应用线程中，持有：
- `_pipes`：管道数组，每个 pipe 对应一个连接
- `_mailbox`：邮箱，接收来自 I/O 线程的命令
- 消息模式的路由逻辑（通过 `xsend`/`xrecv` 等虚函数钩子实现，F-024）

应用程序调用 `zmq_send()`/`zmq_msg_recv()` 时，操作的是 socket 本地的 pipe（无锁队列），而非直接操作网络 fd。这意味着 `zmq_send` 返回成功不等于消息已到达网络。

### 第二层：pipe_t（跨线程无锁队列）

`pipe_t` 是 socket 与 session 之间的双向消息通道，底层使用 `ypipe_t<msg_t>` 无锁队列（F-032, F-033）。pipe 实现了 HWM/LWM 流控，是 libzmq 背压机制的核心。

### 第三层：session_base_t（I/O 线程）

`session_base_t`（F-064）运行在 I/O 线程中，管理连接引擎的生命周期：
- 持有 `_pipe`（连接到 socket 的管道）
- 持有 `_engine`（协议引擎指针）
- 处理连接建立/断开/重连
- 在引擎就绪后通知 socket

### 第四层：zmtp_engine_t（I/O 线程）

`zmtp_engine_t`（F-058）负责实际的网络读写和 ZMTP（ZeroMQ Message Transport Protocol）协议处理：
- ZMTP greeting 交换和握手
- 安全机制协商（NULL/PLAIN/CURVE/GSSAPI）
- 消息帧编码（v2_encoder）和解码（v2_decoder）
- 心跳管理
- 底层 TCP socket fd 的读写

## 线程模型

libzmq 的线程模型遵循"不共享、只通信"原则：

| 线程 | 生活的对象 | 通信方式 |
|------|-----------|---------|
| 应用线程 | socket_base_t | 通过 pipe 写消息到 I/O 线程 |
| I/O 线程 | session_base_t, engine, listener, connecter | 通过 mailbox 命令与 socket 通信 |
| reaper 线程 | reaper_t | 收集已关闭的 socket，完成终止 |
| 其他应用线程 | 其他 socket_base_t | inproc 连接通过 pipe 直接通信 |

线程间不直接访问对方的对象字段，而是通过**邮箱（mailbox）**传递**命令（command_t）**异步通信（F-020, F-048）。每个生活在特定线程的对象都有一个邮箱，其他线程向其邮箱发送命令，命令在目标线程的主循环中被串行处理。

这带来两个重要结论：
1. **socket 不是线程安全的**（除非使用 `ZMQ_THREAD_SAFE` 选项的 Draft 类型），因为 pipe 的写端归属创建线程
2. **应用线程永远不会阻塞在实际的 `send()`/`recv()` 系统调用上**，网络 I/O 由 I/O 线程异步完成

## 公共 C API 全景

libzmq 的公共 API 定义在 `include/zmq.h` 中（详见 [zmq.h C API 参考](../references/zmq-h-api.md)），可以分为以下几类：

### 上下文管理（F-002, F-003）

```c
void *context = zmq_ctx_new ();
zmq_ctx_set (context, ZMQ_IO_THREADS, 2);
zmq_ctx_set (context, ZMQ_MAX_SOCKETS, 4096);
// ... 创建和使用 socket ...
zmq_ctx_term (context);  // 阻塞直到所有 socket 关闭
```

上下文管理 I/O 线程池和 socket 槽位。`ZMQ_IO_THREADS` 默认 1 个，`ZMQ_MAX_SOCKETS` 默认 1023（F-003）。

### 消息操作（F-004, F-005）

```c
zmq_msg_t msg;
zmq_msg_init_size (&msg, 100);
memcpy (zmq_msg_data (&msg), "hello", 5);
zmq_msg_send (&msg, socket, 0);
zmq_msg_close (&msg);
```

`zmq_msg_t` 是 64 字节的不透明结构体（F-004），内部根据消息大小采用不同存储策略（内联小消息或堆分配大消息），支持引用计数的零拷贝传递。

### 套接字类型（F-006）

libzmq 提供 12 种稳定套接字类型：

| 类型 | 模式 | 方向 | 典型用途 |
|------|------|------|---------|
| PAIR | 一对一 | 双向 | 线程间 inproc 通信 |
| PUB/SUB | 发布-订阅 | PUB只发/SUB只收 | 主题广播 |
| REQ/REP | 请求-回复 | 双向（严格状态机） | RPC |
| DEALER | 匿名轮询 | 双向 | 异步客户端 |
| ROUTER | 显式寻址 | 双向 | 异步服务端 |
| PUSH/PULL | 流水线 | PUSH只发/PULL只收 | 任务分发 |
| XPUB/XSUB | 扩展发布订阅 | 双向 | 代理/转发 |
| STREAM | 原始 TCP | 双向 | 与非 ZeroMQ 客户端通信 |

### 套接字选项（F-007）

通过 `zmq_setsockopt()`/`zmq_getsockopt()` 配置，包括：
- 流控：`ZMQ_SNDHWM`/`ZMQ_RCVHWM`（高水位，默认 1000）
- 超时：`ZMQ_SNDTIMEO`/`ZMQ_RCVTIMEO`（默认 -1 永久阻塞）
- 逗留：`ZMQ_LINGER`（关闭时等待消息发送，默认 -1）
- 安全：`ZMQ_PLAIN_USERNAME`/`ZMQ_CURVE_PUBLICKEY` 等
- 心跳：`ZMQ_HEARTBEAT_IVL`/`ZMQ_HEARTBEAT_TIMEOUT`（ZMTP/3.1）

### 安全机制（F-008）

四种安全机制：NULL（无安全）、PLAIN（明文用户名密码）、CURVE（椭圆曲线加密，推荐）、GSSAPI（Kerberos）。

### 轮询（F-009）

```c
zmq_pollitem_t items[] = {
    { socket1, 0, ZMQ_POLLIN, 0 },
    { socket2, 0, ZMQ_POLLIN, 0 }
};
zmq_poll (items, 2, -1);  // 永久等待
```

`zmq_pollitem_t` 可以同时轮询 ZMQ socket 和原生 fd。`ZMQ_FD` 选项提供边缘触发的信号 fd，可用于集成到外部事件循环。

### 监控（F-010）

通过 `zmq_socket_monitor()` 注册监控套接字，接收连接建立/断开/握手成功/失败等事件，用于调试和运维。

### 代理（F-011）

`zmq_proxy()` 在两个套接字之间转发消息，常用于构建消息代理：
- 转发 PUB→SUB（发布订阅代理）
- 转发 ROUTER→DEALER（请求回复代理）
- `capture` 参数可镜像所有流量用于审计

## 对象层次结构

libzmq 的 C++ 对象层次以 `object_t` 为线程间通信基类，`own_t` 为所有权管理基类：

```
object_t（线程间通信：send_*/process_*）
  └── own_t（所有权树：终止序列）
        ├── ctx_t（全局上下文，ZMQ_FINAL）
        ├── socket_base_t（套接字基类）
        │     ├── pair_t, pub_t, sub_t, pull_t, push_t
        │     ├── dealer_t → req_t
        │     ├── rep_t
        │     ├── routing_socket_base_t → router_t, stream_t
        │     └── xpub_t → pub_t; xsub_t → sub_t
        ├── session_base_t（会话基类）
        ├── tcp_listener_t / tcp_connecter_t
        └── reaper_t（回收线程）

io_object_t（poller 事件适配器）
  ├── session_base_t
  ├── stream_engine_base_t → zmtp_engine_t
  └── tcp_listener_t / tcp_connecter_t
```

## 消息模式的模板方法设计

`socket_base_t` 使用**模板方法模式**（F-024, F-026）实现消息模式的差异化：

1. 公共方法 `send()`/`recv()` 定义骨架算法：处理命令、超时重试、标志管理
2. 将具体路由委托给 protected 虚函数 `xsend()`/`xrecv()`/`xattach_pipe()` 等
3. 各模式子类（dealer_t、router_t、pub_t 等）覆写这些钩子实现不同语义

例如：
- `push_t` 只持有 `lb_t`（负载均衡器），覆写 `xsend` 轮询发送（F-075）
- `pull_t` 只持有 `fq_t`（公平队列），覆写 `xrecv` 轮询接收（F-075）
- `dealer_t` 同时持有 `fq_t` 和 `lb_t`，实现双向轮询（F-069）
- `router_t` 额外维护 routing_id→pipe 的映射表，实现显式寻址（F-070）

工厂方法 `socket_base_t::create()` 根据类型参数 switch 创建对应实例（F-026）。

## 关键反常识

1. **`zmq_send` 返回成功 ≠ 消息已发送**：消息先写入本地 pipe，由 I/O 线程异步发送
2. **socket 不能跨线程共享**：除非使用线程安全的 Draft 类型（CLIENT/SERVER）
3. **HWM 是 pipe 层的流控，不是 TCP buffer**：HWM 限制的是未确认消息数
4. **不要把 ZMQ socket 当 fd 传给 select/poll**：应使用 `ZMQ_FD` 获取信号 fd
5. **PUB/SUB 过滤在两端发生**：SUB 端用 trie 本地过滤，PUB 端用 mtrie 智能分发
6. **`zmq_msg_copy` 不是深拷贝**：它创建共享引用，修改副本会影响原消息

## 相关概念

- [上下文与基础设施](/concepts/01-context.md) — ctx_t 延迟启动、I/O 线程池、reaper 终止序列
- [套接字基类](/concepts/02-socket-base.md) — 模板方法模式、x-钩子体系、bind/connect 流程
- [消息与引用计数](/concepts/03-message.md) — msg_t 六类型、content_t 引用计数、零拷贝
- [管道与流控](/concepts/04-pipe.md) — pipepair、ypipe 无锁队列、HWM/LWM
- [会话与连接生命周期](/concepts/05-session.md) — session_base_t、connecter/listener、重连退避
- [ZMTP 协议引擎](/concepts/06-zmtp-engine.md) — greeting 帧结构、握手状态机、安全机制
- [消息模式实现](/concepts/11-patterns.md) — fq/lb/dist 算法、ROUTER 路由、PUB/SUB 过滤
