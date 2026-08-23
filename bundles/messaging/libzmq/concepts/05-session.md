---
type: concept
title: "会话 session_base_t 与连接生命周期"
description: "session_base_t 多继承结构、主动/被动会话区别、connecter/listener 连接建立、tcp_connecter 非阻塞连接与重连退避、engine 插拔与引擎就绪通知、ZAP 认证管道"
tags: [libzmq, zeromq, session, connecter, listener, tcp, reconnect]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [../references/socket-base.md, ../references/zmtp-wire-protocol.md]
  facts: [F-064, F-065, F-066, F-077, F-078, F-079, F-080]
---

# 会话 session_base_t 与连接生命周期

## 核心理解

`session_base_t`（会话）是 libzmq 中管理单个网络连接生命周期的对象，运行在 I/O 线程中。它是四层管线模型的第三层——上接 socket 的 pipe，下接协议引擎（如 zmtp_engine_t），负责连接建立/断开/重连、引擎插拔、pipe 绑定等。

会话有两种类型：
- **主动会话（outbound）**：由 `connect()` 创建，主动连接对端，支持自动重连
- **被动会话（inbound）**：由 listener 在接受连接时创建，瞬态存在

## 多继承结构

`session_base_t` 同时继承三个基类（F-064）：

```cpp
class session_base_t : public own_t,        // 所有权管理 + 终止序列
                       public io_object_t,  // poller 事件适配器
                       public i_pipe_events // pipe 事件回调
```

| 基类 | 提供能力 |
|------|---------|
| `own_t`（→`object_t`） | 对象树管理、终止序列、跨线程命令发送 |
| `io_object_t` | 可向 poller 注册 fd、添加定时器（用于重连） |
| `i_pipe_events` | 接收 pipe 事件（read_activated/write_activated/pipe_terminated） |

这种组合让会话既能参与对象树的终止协议（own_t），又能使用 poller 进行异步 I/O（io_object_t），还能响应 pipe 状态变化。

## 关键成员

`session_base_t` 的关键成员（F-065）：

| 成员 | 类型 | 说明 |
|------|------|------|
| `_active` | bool | true=主动连接会话，false=listener 创建的瞬态会话 |
| `_pipe` | pipe_t* | 连接到 socket 的管道 |
| `_zap_pipe` | pipe_t* | ZAP（ZeroMQ Authentication Protocol）认证管道 |
| `_engine` | i_engine* | 协议引擎指针（如 zmtp_engine_t） |
| `_socket` | socket_base_t* | 所属 socket |
| `_io_thread` | io_thread_t* | 所在 I/O 线程 |
| `_addr` | address_t | 连接地址 |
| `_pending` | bool | 终止时是否等待消息发送完毕 |

## 连接建立流程

### 主动连接（connect）

当应用调用 `zmq_connect(socket, "tcp://host:port")` 时：

```
应用线程                     I/O 线程
┌──────────┐                ┌──────────────────┐
│ socket   │── send_own ──►│ ctx 创建 session  │
│ connect  │                │ + tcp_connecter  │
└──────────┘                └────────┬─────────┘
                                     │
                              tcp_connecter::open()
                              │  创建非阻塞 TCP socket
                              │  调用 connect()（立即返回 EINPROGRESS）
                              │  注册 fd 到 poller（关注 POLLOUT）
                                     │
                              ◄── poller 通知 fd 可写 ──
                                     │
                              tcp_connecter::out_event()
                              │  getsockopt(SO_ERROR) 检查连接结果
                              │  连接成功 → tune_socket()
                              │  创建 zmtp_engine_t(fd)
                              │  创建/复用 session
                              │  engine->plug(io_thread, session)
                              │  session->bind(pipe)
                                     │
                              ◄── 引擎握手完成 ──
                                     │
                              session.engine_ready()
                              │  send_attach(socket, engine) 或
                              │  send_bind(socket, pipe)
```

### 被动接受（bind + accept）

当应用调用 `zmq_bind(socket, "tcp://*:port")` 时：

```
I/O 线程
┌──────────────────┐
│ tcp_listener     │
│  创建监听 socket │
│  bind + listen   │
│  注册到 poller   │
└────────┬─────────┘
         │
  ◄── 新连接到达（POLLIN）──
         │
  tcp_listener::in_event()
  │  accept() → 获取新 fd
  │  tune_socket(fd)
  │  创建 zmtp_engine_t(fd)
  │  创建瞬态 session（_active=false）
  │  engine->plug(io_thread, session)
  │  session->bind(pipe)
  │  send_attach(socket, engine)
```

被动会话是瞬态的——连接断开后不重连，直接销毁。

## tcp_connecter_t：非阻塞连接

`tcp_connecter_t` 以 `ZMQ_FINAL` 标记（F-077），继承 `stream_connecter_base_t`：

| 方法 | 说明 |
|------|------|
| `open()` | 创建 TCP socket，设置非阻塞，发起 `connect()` |
| `out_event()` | poller 通知 fd 可写时调用——连接完成或失败 |
| `timer_event()` | 连接超时处理 |
| `connect()` | 获取已连接 fd（调用 `accept` 风格的完成确认） |
| `tune_socket()` | 设置 TCP 参数（keepalive、buffer 大小、nodelay 等） |
| `start_connecting()` | 启动连接流程，添加到 poller |

非阻塞连接的关键：
1. 创建 socket 后调用 `fcntl(fd, F_SETFL, O_NONBLOCK)`
2. `connect()` 立即返回 -1，errno=EINPROGRESS（正常）
3. 将 fd 注册到 poller 关注 POLLOUT
4. poller 通知可写时，用 `getsockopt(fd, SOL_SOCKET, SO_ERROR)` 检查连接结果
5. 成功则创建引擎，失败则启动重连定时器

## tcp_listener_t：接受连接

`tcp_listener_t` 继承 `stream_listener_base_t`（F-078）：

| 成员/方法 | 说明 |
|----------|------|
| `_address` | tcp_address_t，解析后的监听地址 |
| `set_local_address()` | 解析地址、创建监听 socket、bind+listen |
| `in_event()` | 新连接到达时调用 `accept()`，创建 engine |

`in_event()` 执行流程：
1. `accept()` 获取新连接 fd
2. 基类 `create_engine(fd)` 创建 `zmtp_engine_t`
3. 创建瞬态 session 并将 engine 插入

## 重连退避机制

`stream_connecter_base_t` 实现指数退避重连（F-079）：

| 成员 | 说明 |
|------|------|
| `_addr` | 服务器地址 |
| `_s` | 当前 TCP socket |
| `_handle` | poller 句柄 |
| `_socket` | 所属 socket |
| `_session` | 关联的会话 |
| `_delayed_start` | 是否延迟启动（immediate 选项） |
| `_current_reconnect_ivl` | 当前重连间隔 |

重连间隔计算 `get_new_reconnect_ivl()`：

```
if reconnect_ivl_max > 0:
    _current_reconnect_ivl = min(
        _current_reconnect_ivl * 2,  // 指数增长
        reconnect_ivl_max             // 上限
    )
else:
    _current_reconnect_ivl = reconnect_ivl
```

- 初始间隔为 `ZMQ_RECONNECT_IVL`（默认 100ms）
- 每次失败间隔翻倍，直到达到 `ZMQ_RECONNECT_IVL_MAX`（默认 0=无上限，但会被随机化）
- 实际间隔加入随机抖动，避免重连风暴
- 使用 `reconnect_timer_id=1` 定时器触发重连

重连流程：
```
连接失败
  → 添加 reconnect 定时器（当前间隔）
  → 定时器到期
  → start_connecting()
  → open() 创建新 socket + connect
  → 成功 → 创建 engine，重置间隔
  → 失败 → 间隔翻倍，重新添加定时器
```

## engine 插拔

### plug：引擎插入

当 engine 创建后，调用 `engine->plug(io_thread, session)`（F-091）：

1. engine 将自己注册到 io_thread 的 poller
2. 设置 `_session = session`
3. 设置 `_socket = session->get_socket()`
4. 开始 ZMTP 握手（发送 greeting）
5. 设置 `_handshaking = true`

### engine_ready：握手完成

`i_engine` 接口声明 `has_handshake_stage()`（F-066, F-091）：
- 若返回 true（zmtp_engine 有握手阶段），引擎必须在握手完成后调用 `session.engine_ready()`
- 此时 session 才将 pipe 与 engine 正式连接，开始数据传输

```
engine 握手完成
  → session.engine_ready()
  → session 设置 _engine = engine
  → 若 _pipe 已存在:
      engine 与 pipe 对接
      read_activated / write_activated
  → 若 _pipe 不存在（罕见）:
      等待 pipe 绑定
```

### terminate：引擎终止

连接断开时：
1. engine 检测到错误（read 返回 0 或错误）
2. engine 调用 `session.terminate()`
3. session 启动终止序列（own_t 协议）
4. 若是主动会话（`_active=true`），启动重连定时器
5. 若是被动会话，直接销毁

## ZAP 认证管道

`_zap_pipe` 用于 ZAP（ZeroMQ Authentication Protocol）认证：

- 当 socket 配置了 PLAIN/CURVE/GSSAPI 机制时，引擎在握手期间通过 ZAP 管道向 ZAP handler 发送认证请求
- ZAP handler 是一个 REP socket，绑定到 `inproc://zeromq.zap.01`
- 认证请求包含：域名、地址、身份、凭据
- ZAP handler 回复：状态码（200=允许/400=拒绝）、用户 ID、元数据

ZAP 管道在 engine 和 ZAP handler socket 之间建立，使认证逻辑可以委托给外部应用程序处理。

## 地址解析

`tcp_open_socket()` 是地址解析和 socket 创建的工具函数（F-080）：

```cpp
fd_t tcp_open_socket (const char *address_,
                      const options_t &options_,
                      bool local_,
                      bool fallback_to_ipv4_,
                      tcp_address_t *out_tcp_addr_);
```

执行：
1. 解析地址（host:port），支持 IPv4/IPv6
2. 根据 options 设置 IPv6 选项
3. 创建 socket
4. 设置 SO_REUSEADDR
5. 设置 keepalive（如果 options 配置）
6. 设置发送/接收缓冲区大小（sndbuf/rcvbuf）
7. 返回 fd

## 会话与 socket/engine 的关系

```
应用线程                     I/O 线程
┌──────────────┐           ┌─────────────────────────────────┐
│ socket_base  │           │ session_base_t                  │
│              │  pipe_t   │  ┌─────────┐    ┌────────────┐ │
│  _pipes[] ◄──┼──────────►│  │ _pipe   │◄──►│ _engine    │ │
│              │  (无锁)   │  └─────────┘    │ (zmtp_eng) │ │
│  xsend/xrecv │           │                 └─────┬──────┘ │
└──────────────┘           │                       │ fd     │
                           │                       ▼        │
                           │                   TCP socket   │
                           └─────────────────────────────────┘
```

session 是 socket 和 engine 之间的桥梁：
- 对 socket 而言，session 通过 pipe 提供消息收发接口
- 对 engine 而言，session 提供 pipe 绑定、错误通知、终止协调

session 还负责在 engine 终止时决定是否重连（主动会话）或销毁（被动会话）。

## 相关概念

- [套接字基类](/concepts/02-socket-base.md) — socket 通过 send_own 创建 session 和 connecter
- [ZMTP 协议引擎](/concepts/06-zmtp-engine.md) — engine 握手完成后通知 session
- [管道与流控](/concepts/04-pipe.md) — session 持有 pipe 连接到 socket
- [I/O 线程与多路复用](/concepts/07-io-thread-poller.md) — io_object_t 的 poller 接口
- [传输层](/concepts/10-transport.md) — TCP/IPC/inproc 传输的详细对比
- [套接字选项体系](/concepts/09-options.md) — reconnect_ivl/heartbeat 等选项影响 session 行为
