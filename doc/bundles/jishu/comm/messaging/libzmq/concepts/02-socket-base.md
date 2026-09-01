---
type: concept
title: "套接字基类 socket_base_t"
description: "socket_base_t 的多继承结构、模板方法模式的 x-钩子体系、send/recv 骨架算法、bind/connect 流程、线程安全机制、routing_socket_base_t 路由表"
tags: [libzmq, zeromq, socket, socket-base, template-method, routing]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [../references/socket-base.md, ../references/ctx.md, ../references/command.md]
  facts: [F-020, F-021, F-022, F-023, F-024, F-025, F-026, F-027, F-028, F-029, F-030, F-031]
---

# 套接字基类 socket_base_t

## 核心理解

`socket_base_t` 是所有 ZeroMQ 套接字类型的 C++ 基类。它实现了套接字的公共骨架——命令处理、超时重试、标志管理、pipe 生命周期——将具体的消息路由策略通过 protected 虚函数（`xsend`/`xrecv`/`xattach_pipe` 等）委托给子类。这是经典的**模板方法模式**应用。

理解 socket_base_t 的关键是：它运行在应用线程中，不直接进行网络 I/O。它持有的 pipe 是连接到 I/O 线程中 session 的无锁队列。

## 多继承结构

`socket_base_t` 同时继承四个基类（F-023）：

```cpp
class socket_base_t : public own_t,           // 所有权管理 + 终止序列
                     public array_item_t<>,   // 可被 intrusive array 管理
                     public i_poll_events,    // poller 事件接口
                     public i_pipe_events     // pipe 事件接口
```

| 基类 | 提供的能力 |
|------|-----------|
| `own_t`（→`object_t`） | 所有权树、终止序列、跨线程命令发送 |
| `array_item_t<>` | intrusive 数组项，可被 `array_t<socket_base_t>` 管理 |
| `i_poll_events` | `in_event()`/`out_event()`/`timer_event()` 回调（reaper 中使用） |
| `i_pipe_events` | `read_activated()`/`write_activated()`/`hiccuped()`/`pipe_terminated()` 回调 |

`routing_socket_base_t` 进一步继承 `socket_base_t`，增加按 routing_id 索引出站 pipe 的能力。ROUTER 和 STREAM 继承此类（F-031）。

## object_t：线程间通信基类

`object_t`（F-020）是所有生活在特定线程中的对象的基类，持有：
- `ctx_t *_ctx`：所属上下文
- `uint32_t _tid`：所属线程 ID（邮箱槽位索引）

它提供两类方法：

**send_* 方法**：向其他线程的对象发送命令。每个方法构造对应的 `command_t`，通过 `ctx->send_command(target_tid, cmd)` 投递到目标邮箱。例如：
- `send_bind(pipe)`：通知对端 socket 绑定 pipe
- `send_activate_read()`：通知 pipe 读端有数据
- `send_term_req()`：请求终止
- `send_reap(socket)`：将 socket 交给 reaper

**process_* 虚函数**：在所属线程中处理收到的命令。默认实现为空或断言 false，子类按需覆写。例如 socket_base_t 覆写了 `process_bind`、`process_activate_read`、`process_pipe_term` 等。

## own_t：所有权与终止序列

`own_t`（F-021）在 object_t 之上增加了对象树管理：

```cpp
class own_t : public object_t {
    own_t *_owner;                // 所有者
    std::set<own_t*> _owned;      // 子对象集合
    bool _terminating;            // 终止中标志
    atomic_counter_t _sent_seqnum;    // 已发送序列号
    std::set<uint32_t> _processed_seqnum; // 已处理序列号
    uint32_t _term_acks;          // 待确认终止数
};
```

对象树用于管理生命周期：当父对象终止时，所有子对象也必须终止。终止通过命令往返完成：

```
父对象                           子对象
  │── term_req ──────────────────►│  (子对象请求关闭)
  │◄──────── term (linger) ───────│  (父对象批准)
  │   子对象清理...               │
  │◄──────── term_ack ───────────│  (子对象完成)
  │                               │
  └─ _term_acks-- → 0 → delete this
```

`register_term_acks(n)` 注册 n 个待确认，`process_term_ack()` 递减计数，归零后对象自销毁。

`own_t` 有两种构造方式（F-022）：
1. `own_t(ctx*, tid)`：用于不在 I/O 线程内的对象（socket_base_t）
2. `own_t(io_thread*, options)`：用于生活在 I/O 线程内的对象（session、listener、connecter），后者会复制 options

## x-钩子体系：模板方法模式

socket_base_t 定义了一组 protected 虚函数钩子（F-024），子类覆写这些钩子实现不同的消息模式语义：

### 必须覆写的纯虚函数

```cpp
virtual void xattach_pipe (pipe_t *pipe_, bool subscribe_to_all_,
                           bool locally_initiated_) = 0;
virtual void xpipe_terminated (pipe_t *pipe_) = 0;
```

- `xattach_pipe`：新 pipe 附加到 socket 时调用，子类将 pipe 注册到其路由算法（fq/lb/dist/mtrie）
- `xpipe_terminated`：pipe 终止时调用，子类从路由算法中移除

### 可选覆写的虚函数

| 方法 | 默认行为 | 覆写场景 |
|------|---------|---------|
| `xhas_out()` | false（不支持发送） | 发送模式覆写为 true |
| `xsend(msg*)` | 返回 ENOTSUP | 实现消息入队逻辑 |
| `xhas_in()` | false（不支持接收） | 接收模式覆写为 true |
| `xrecv(msg*)` | 返回 ENOTSUP | 实现消息出队逻辑 |
| `xsetsockopt(...)` | 无特殊选项 | SUB 处理 SUBSCRIBE，ROUTER 处理 MANDATORY 等 |
| `xgetsockopt(...)` | 无特殊选项 | 返回模式特定属性 |
| `xread_activated(pipe*)` | 空 | 标记 pipe 为可读 |
| `xwrite_activated(pipe*)` | 空 | 标记 pipe 为可写（HWM 恢复） |
| `xhiccuped(pipe*)` | 空 | 处理 inproc 配置同步 |

### 公共方法的骨架算法

`send(msg_, flags_)` 公共方法（F-030）展示了模板方法的工作方式：

```
1. process_commands(0)     // 处理待处理命令
2. 重置消息 flags
3. 根据 ZMQ_SNDMORE 设置 more 标志
4. 调用 xsend(msg_)       // ← 委托给子类
5. 若 EAGAIN 且非 DONTWAIT:
     循环:
       process_commands(timeout)  // 处理命令（可能触发 write_activated）
       重试 xsend(msg_)
       直到成功或超时
```

关键点：
- 超时重试逻辑由基类统一处理，子类的 `xsend` 只需返回 EAGAIN 表示当前无法发送
- `process_commands` 在等待期间处理 mailbox 中的命令，这可能包括来自 I/O 线程的 `activate_write`（通知 pipe 恢复可写）
- `recv()` 方法采用相同模式

## pipe 数组管理

socket_base_t 持有 pipe 数组（F-025）：

```cpp
typedef array_t<pipe_t, 3> pipes_t;
pipes_t _pipes;
i_mailbox *_mailbox;
```

模板参数 `3` 表示 pipe 可同时存在于三个数组索引中：
- 索引 0：入站活跃（有数据可读）
- 索引 1：出站活跃（可写入）
- 索引 2：待终止（等待销毁）

这种 intrusive array 设计允许 O(1) 添加/删除 pipe，且每个 pipe 可以同时在多个数组中（例如一个双向活跃的 pipe 同时在入站和出站数组中）。

当 pipe 有数据到达时，I/O 线程通过 `send_activate_read` 命令通知 socket，socket 在 `process_commands` 中调用 `xread_activated`，子类将 pipe 标记为可读。

## 工厂方法

`socket_base_t::create(type_, ctx, tid, sid)` 是静态工厂方法（F-026），根据类型创建具体实例：

| 类型 | 创建的类 | 路由算法 |
|------|---------|---------|
| ZMQ_PAIR | pair_t | 单 pipe 直连 |
| ZMQ_PUB | pub_t (→xpub_t) | dist + mtrie |
| ZMQ_SUB | sub_t (→xsub_t) | fq + trie |
| ZMQ_REQ | req_t (→dealer_t) | fq + lb + 状态机 |
| ZMQ_REP | rep_t | fq + lb + 状态机 |
| ZMQ_DEALER | dealer_t | fq + lb |
| ZMQ_ROUTER | router_t | fq + routing_id 表 |
| ZMQ_PULL | pull_t | fq only |
| ZMQ_PUSH | push_t | lb only |
| ZMQ_XPUB | xpub_t | dist + mtrie |
| ZMQ_XSUB | xsub_t | fq + trie + dist |
| ZMQ_STREAM | stream_t | routing_id 表 + raw |

工厂方法确保类型与实现的映射集中在一处，新增类型只需在此 switch 中添加分支。

## bind 流程

`bind(uri_)` 区分 inproc 和网络协议（F-028）：

### inproc 绑定

```
1. 解析 URI → "inproc://name"
2. 构造 endpoint_t{this, options}
3. 注册到 ctx._endpoints["name"]
4. 调用 connect_pending("name")
   └─ 对 _pending_connections 中每个等待的连接:
      └─ 创建 pipepair，双向附加
```

### 网络协议绑定（tcp/ipc）

```
1. 解析 URI → protocol + address
2. 创建对应 listener（如 tcp_listener_t）
3. listener 启动，在 I/O 线程中监听
4. 新连接到达时:
   └─ accept() 获取 fd
   └─ create_engine(fd) 创建 zmtp_engine_t
   └─ 创建 session_base_t
   └─ engine-plug(session)，session 创建 pipe 连接到 socket
```

## connect 流程

`connect_internal(uri_)` 同样区分协议（F-029）：

### inproc 连接

```
1. 在 ctx._endpoints 查找 "name"
2. 若找到（对端已 bind）:
   └─ pipepair(parents, pipes, hwms, conflates)
   └─ HWM = 两端 sndhwm + rcvhwm 之和
   └─ send_bind 将远端 pipe 附加到对端 socket
   └─ 本地 attach_pipe
3. 若未找到（对端未 bind）:
   └─ 放入 _pending_connections 等待
```

inproc 连接不经过网络栈，pipepair 直接在两个 socket 之间创建双向无锁队列。消息通过 64 字节 `msg_t` 值拷贝传递，大消息的 content 引用计数确保数据只在最后一个引用关闭时释放。

### 网络协议连接

```
1. 创建 connecter（如 tcp_connecter_t）
2. connecter 在 I/O 线程中异步连接
3. 连接成功后创建 engine + session
4. 连接失败时按指数退避重连
```

## 线程安全

普通 socket 不是线程安全的——只能在创建线程中使用。构造函数根据 `_thread_safe` 选项选择邮箱实现（F-027）：

```cpp
if (options.thread_safe) {
    _mailbox = new mailbox_safe_t (&_sync);  // 条件变量
} else {
    _mailbox = new mailbox_t ();             // signaler
}
```

- **普通 socket**：使用 `mailbox_t`（基于 signaler fd），公共 API 不加锁
- **线程安全 socket**：使用 `mailbox_safe_t`（基于条件变量），公共 API 通过 `scoped_optional_lock_t` 加锁 `_sync`

线程安全 socket 类型包括 Draft API 中的 CLIENT、SERVER、CHANNEL、PEER。它们允许多个线程同时调用 send/recv，但有锁竞争的性能代价。

## routing_socket_base_t：显式寻址

`routing_socket_base_t`（F-031）为 ROUTER 和 STREAM 提供按 routing_id 路由的能力：

```cpp
class routing_socket_base_t : public socket_base_t {
    struct out_pipe_t {
        pipe_t *pipe;
        bool active;
    };
    std::map<blob_t, out_pipe_t> _out_pipes;
};
```

| 方法 | 说明 |
|------|------|
| `add_out_pipe(routing_id, pipe)` | pipe 附加时注册其 routing_id |
| `lookup_out_pipe(routing_id)` | 根据 ID 查找目标 pipe |
| `erase_out_pipe(pipe)` | pipe 终止时移除映射 |
| `has_out_pipe(routing_id)` | 检查 ID 是否存在 |

ROUTER 接收消息时，自动在消息前前置 peer 的 routing_id 帧；发送时第一帧必须是 routing_id，用于查找目标 pipe。若启用了 `ZMQ_ROUTER_MANDATORY`，发送到未知 routing_id 时返回 EHOSTUNREACH 而非静默丢弃。

## 相关概念

- [整体架构总览](00-overview.md) — 四层管线模型和线程模型
- [上下文与基础设施](01-context.md) — ctx_t 管理 socket 槽位和 I/O 线程
- [消息与引用计数](03-message.md) — msg_t 在 pipe 中的传递方式
- [管道与流控](04-pipe.md) — pipe_t 的双向无锁队列和 HWM 流控
- [消息模式实现](11-patterns.md) — dealer/router/pub/sub 等子类的 x-钩子覆写
- [套接字选项体系](09-options.md) — options_t 如何影响 socket 行为
- [命令传递与邮箱](08-command-mailbox.md) — mailbox_t vs mailbox_safe_t
