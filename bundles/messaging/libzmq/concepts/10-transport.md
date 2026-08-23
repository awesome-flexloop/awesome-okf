---
type: concept
title: "传输层"
description: "TCP connecter/listener 的非阻塞连接与 accept 流程、inproc 进程内直连零拷贝、IPC  Unix 域套接字、URI 解析、stream_connecter_base 指数退避重连、各传输协议特性对比"
tags: [libzmq, zeromq, transport, tcp, inproc, ipc, connecter, listener, reconnect]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [../references/socket-base.md, ../references/ctx.md]
  facts: [F-077, F-078, F-079, F-080, F-028, F-029]
---

# 传输层

## 核心理解

libzmq 支持多种传输协议，每种协议有独立的 connecter/listener 实现，但都遵循相同的会话-引擎模型。传输层负责建立和管理底层连接（TCP/IPC/inproc），上层 ZMTP 引擎在连接建立后接管协议握手和消息收发。

理解传输层的关键是：
1. bind/connect 是异步的——立即返回，连接在 I/O 线程中建立
2. TCP 连接支持自动重连（指数退避）
3. inproc 不经过网络栈，直接在两个 socket 之间创建 pipepair
4. 传输选项（HWM、安全、心跳）在连接建立时快照到 session/engine

## 支持的传输协议

| 协议 | URI 格式 | 跨进程 | 跨主机 | 特点 |
|------|---------|--------|--------|------|
| tcp | `tcp://host:port` | ✅ | ✅ | 标准 TCP，自动重连 |
| ipc | `ipc:///path/to/socket` | ✅ | ❌ | Unix 域套接字 |
| inproc | `inproc://name` | ❌ | ❌ | 进程内，零拷贝 |
| pgm | `pgm://...` | ✅ | ✅ | 可靠多播（需编译启用） |
| epgm | `epgm://...` | ✅ | ✅ | PGM over UDP（需编译启用） |
| vmci | `vmci://...` | ✅ | 虚拟机间 | VMware VMCI |

本知识包聚焦最常用的 tcp、inproc、ipc 三种。

## TCP 传输

### tcp_connecter_t：主动连接

`tcp_connecter_t` 以 `ZMQ_FINAL` 标记（F-077），继承 `stream_connecter_base_t`：

```cpp
class tcp_connecter_t ZMQ_FINAL : public stream_connecter_base_t {
    bool _connect_timer_started;
    // ...
};
```

关键方法：

| 方法 | 说明 |
|------|------|
| `start_connecting()` | 创建非阻塞 TCP socket 并发起连接 |
| `open()` | 解析地址、创建 socket、设置非阻塞、调用 connect() |
| `out_event()` | poller 通知 fd 可写（连接完成） |
| `connect()` | 确认连接结果，获取已连接 fd |
| `tune_socket()` | 设置 TCP 参数（keepalive、buffer、nodelay） |
| `timer_event()` | 连接超时或重连定时器到期 |

#### 非阻塞连接流程

```
1. start_connecting()
   ├─ open()
   │   ├─ tcp_open_socket() 创建 socket
   │   ├─ fcntl(O_NONBLOCK) 设为非阻塞
   │   └─ ::connect() → 返回 -1, errno=EINPROGRESS（正常）
   ├─ add_fd() 注册 fd 到 poller
   └─ set_pollout() 关注可写事件

2. poller 通知 out_event()（fd 可写）
   ├─ getsockopt(SO_ERROR) 检查连接结果
   ├─ 成功:
   │   ├─ tune_socket() 设置 TCP 参数
   │   ├─ 创建 zmtp_engine_t(fd)
   │   ├─ 创建/复用 session
   │   └─ engine->plug(io_thread, session)
   └─ 失败:
       └─ 添加重连定时器
```

为什么非阻塞 connect 关注 POLLOUT？当 TCP 三次握手完成后，socket 变为可写状态（即使应用没有数据要发），这是 POSIX 的标准连接完成通知机制。

#### 连接参数调优

`tune_socket()` 根据 options 设置：
- `TCP_NODELAY`：禁用 Nagle 算法（默认启用，降低延迟）
- `SO_KEEPALIVE`：TCP keepalive（如果配置）
- `SO_SNDBUF`/`SO_RCVBUF`：内核缓冲区大小
- `TCP_KEEPIDLE`/`TCP_KEEPINTVL`/`TCP_KEEPCNT`：keepalive 参数（Linux）

### tcp_listener_t：被动接受

`tcp_listener_t` 继承 `stream_listener_base_t`（F-078）：

```cpp
class tcp_listener_t ZMQ_FINAL : public stream_listener_base_t {
    tcp_address_t _address;
};
```

| 方法 | 说明 |
|------|------|
| `set_local_address()` | 解析地址、创建监听 socket、bind+listen |
| `in_event()` | 新连接到达，accept 获取 fd，创建 engine |

#### 接受连接流程

```
1. set_local_address(addr)
   ├─ 解析地址（支持 IPv4/IPv6、通配符 *）
   ├─ 创建 socket
   ├─ setsockopt(SO_REUSEADDR)
   ├─ bind()
   ├─ listen(backlog)
   └─ add_fd() 注册 fd，关注 POLLIN

2. poller 通知 in_event()（新连接到达）
   ├─ accept() → 获取新 fd 和对端地址
   ├─ tune_socket() 设置参数
   ├─ create_engine(fd) 创建 zmtp_engine_t
   ├─ 创建瞬态 session（_active=false）
   └─ engine->plug(io_thread, session)
```

被动会话（`_active=false`）连接断开后不重连，直接销毁。

### tcp_open_socket：地址解析与 socket 创建

`tcp_open_socket()` 是工具函数（F-080）：

```cpp
fd_t tcp_open_socket (const char *address_,
                      const options_t &options_,
                      bool local_,
                      bool fallback_to_ipv4_,
                      tcp_address_t *out_tcp_addr_);
```

执行：
1. 解析 `host:port` 地址（支持主机名、IPv4、IPv6）
2. 根据 `options.ipv6` 选择地址族
3. 创建 TCP socket
4. 设置 `SO_REUSEADDR`
5. 如果是监听 socket（local_=true），设置绑定选项
6. 根据 options 设置 keepalive、buffer 大小
7. 返回 fd 和解析后的地址

地址格式支持：
- `tcp://*:5555`：监听所有接口
- `tcp://eth0:5555`：指定网卡
- `tcp://127.0.0.1:5555`：IPv4
- `tcp://[::1]:5555`：IPv6
- `tcp://host.example.com:5555`：主机名（DNS 解析）

### 重连退避

`stream_connecter_base_t` 实现指数退避重连（F-079）：

```cpp
uint32_t get_new_reconnect_ivl () {
    if (options.reconnect_ivl_max > 0) {
        uint32_t candidate_ivl = _current_reconnect_ivl * 2;
        candidate_ivl = std::min(candidate_ivl,
                                  options.reconnect_ivl_max);
        // 加入随机抖动
        candidate_ivl += generate_random() %
                         (options.reconnect_ivl + 1);
        _current_reconnect_ivl = candidate_ivl;
    } else {
        _current_reconnect_ivl = options.reconnect_ivl;
    }
    return _current_reconnect_ivl;
}
```

重连定时器 ID 为 1（`reconnect_timer_id=1`），通过 poller 的定时器机制实现：

```
连接失败
  → rm_fd() 关闭失败的 socket
  → get_new_reconnect_ivl() 计算间隔
  → add_timer(interval, reconnect_timer_id)
  → timer_event() 到期
  → start_connecting() 创建新 socket 重试
  → 成功: 重置 _current_reconnect_ivl
  → 失败: 间隔翻倍，重新添加定时器
```

关键行为：
- 重连只发生在 `connect()` 方（主动会话），`bind()` 方不重连
- 重连间隔默认 100ms，最大无上限（除非设置 `ZMQ_RECONNECT_IVL_MAX`）
- 随机抖动防止多个客户端同时重连导致"惊群"
- 成功连接后重置间隔为初始值

## inproc 传输

inproc（进程内）传输不经过网络栈，直接在同一进程的两个 socket 之间创建 pipepair（F-028, F-029）。

### bind 流程

```
socket A: bind("inproc://service")
  │
  ├─ 构造 endpoint_t{socket_A, options_A}
  ├─ 注册到 ctx._endpoints["service"]
  └─ connect_pending("service")
       └─ 对 _pending_connections 中每个等待的连接:
           └─ pipepair() + 双向 attach
```

### connect 流程

```
socket B: connect("inproc://service")
  │
  ├─ 在 ctx._endpoints 查找 "service"
  │
  ├─ 找到（A 已 bind）:
  │   ├─ pipepair(parents=[A,B], pipes=[pA,pB], hwms, conflates)
  │   ├─ HWM = A.sndhwm + B.rcvhwm（双向）
  │   ├─ send_bind(A, pA)  // 命令将 pA 附加到 A
  │   └─ B.attach_pipe(pB)
  │
  └─ 未找到（A 未 bind）:
      └─ 将 B 的 pipe 放入 _pending_connections["service"]
          等待 A bind 时完成连接
```

### inproc 的关键特性

1. **零网络开销**：无 socket()、connect()、read()、write() 系统调用
2. **msg_t 值传递**：消息通过 64 字节 memcpy 在 ypipe 中传递
3. **大消息引用计数**：lmsg 的 content_t 引用计数确保数据只在最后一个引用关闭时释放
4. **connect-before-bind**：支持先 connect 后 bind（pending connections）
5. **HWM 协调**：两端 HWM 之和作为管道 HWM
6. **选项快照**：bind 方的 options 被复制到 endpoint_t，connect 时读取

inproc 是最高效的线程间通信方式，特别适合：
- 多线程应用中的工作线程与主线程通信
- 代理（proxy）的前端和后端在同一进程
- 替代互斥锁+条件变量的消息传递模式

## IPC 传输

IPC（Unix 域套接字）传输使用 `AF_UNIX` socket：

- URI 格式：`ipc:///tmp/feedservice`
- 仅在同一台机器上的进程间通信
- 不经过网络协议栈，比 TCP loopback 延迟更低
- 支持文件权限控制（socket 文件的权限）
- 不支持 Windows（Windows 10+ 有 AF_UNIX 支持但 libzmq 可能未适配）

IPC 的 connecter/listener 实现与 TCP 类似，只是地址族改为 `AF_UNIX`，地址是文件路径而非 host:port。连接断开后同样支持自动重连。

## URI 解析

bind/connect 的 URI 格式：`protocol://address`

socket_base 的 `bind()` 和 `connect_internal()` 首先解析协议前缀（F-028, F-029）：

```cpp
// 伪代码
std::string protocol = uri.substr(0, uri.find("://"));
std::string address = uri.substr(uri.find("://") + 3);

if (protocol == "inproc") {
    // 直接在 ctx endpoints 中操作
} else if (protocol == "tcp") {
    // 创建 tcp_listener_t 或 tcp_connecter_t
} else if (protocol == "ipc") {
    // 创建 ipc_listener_t 或 ipc_connecter_t
} else if (protocol == "pgm" || protocol == "epgm") {
    // 创建 pgm_sender/receiver
}
```

## 传输层与会话/引擎的关系

```
bind()
  └─ 创建 listener (io_object)
       └─ in_event() [新连接到达]
            └─ accept() → fd
            └─ 创建 engine(fd) + session
            └─ engine->plug(io_thread, session)

connect()
  └─ 创建 connecter (io_object)
       └─ start_connecting() [非阻塞]
       └─ out_event() [连接完成]
            └─ 创建 engine(fd) + session
            └─ engine->plug(io_thread, session)

engine->plug()
  ├─ 注册 fd 到 poller
  ├─ 开始 ZMTP 握手
  └─ 握手完成 → session.engine_ready()
       └─ pipe 在 session 和 socket 之间建立
```

每个网络连接对应一组对象：
- **listener/connecter**：临时对象，连接建立后销毁（listener 持续存在接受更多连接）
- **engine**：协议处理，持有 fd
- **session**：连接生命周期管理
- **pipe**：连接 socket 和 session 的消息队列

## 相关概念

- [套接字基类](/concepts/02-socket-base.md) — bind/connect 的入口和协议分发
- [上下文与基础设施](/concepts/01-context.md) — inproc 端点注册表在 ctx 中
- [会话与连接生命周期](/concepts/05-session.md) — session 管理 engine 插拔和重连
- [ZMTP 协议引擎](/concepts/06-zmtp-engine.md) — 连接建立后的协议握手
- [I/O 线程与多路复用](/concepts/07-io-thread-poller.md) — connecter/listener 作为 io_object
- [套接字选项体系](/concepts/09-options.md) — reconnect/buffer 等传输选项
