---
type: reference
title: "socket_base_t：套接字基类完整索引"
description: "src/socket_base.hpp 和 src/socket_base.cpp 中 socket_base_t 的多继承结构、纯虚钩子、pipe 数组、mailbox、工厂方法、bind/connect 流程、线程安全机制、routing_socket_base_t 路由表"
tags: [libzmq, reference, socket, socket-base]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  - path: "external/libs/remote/libzmq/src/socket_base.hpp"
    facts: [F-023, F-024, F-025, F-031]
  - path: "external/libs/remote/libzmq/src/socket_base.cpp"
    facts: [F-026, F-027, F-028, F-029, F-030]
  - path: "external/libs/remote/libzmq/src/object.hpp"
    facts: [F-020]
  - path: "external/libs/remote/libzmq/src/own.hpp"
    facts: [F-021, F-022]
---

# socket_base_t：套接字基类完整索引

## 信源概述

| 信源 | 类型 | 职责 |
|------|------|------|
| `src/socket_base.hpp` | C++ 头文件 | socket_base_t 类声明、routing_socket_base_t 子类 |
| `src/socket_base.cpp` | C++ 实现 | 工厂方法、bind/connect、send/recv 骨架、线程安全 |
| `src/object.hpp` | C++ 头文件 | object_t 线程间通信基类（send_*/process_* 方法） |
| `src/own.hpp` | C++ 头文件 | own_t 所有权层次与终止序列基类 |

## 关键事实登记

### F-023：socket_base_t 多继承结构

**信源**：`src/socket_base.hpp` L31-L35

```cpp
class socket_base_t : public own_t,
                     public array_item_t<>,
                     public i_poll_events,
                     public i_pipe_events
```

| 基类 | 提供能力 |
|------|---------|
| `own_t`（继承 `object_t`） | 所有权树管理、终止序列、线程间命令发送 |
| `array_item_t<>` | 可被 `array_t<socket_base_t>` 管理（intrusive 数组） |
| `i_poll_events` | poller 事件回调接口（`in_event`/`out_event`/`timer_event`） |
| `i_pipe_events` | pipe 事件回调接口（`read_activated`/`write_activated`/`hiccuped`/`pipe_terminated`） |

`routing_socket_base_t` 进一步继承 `socket_base_t`，增加按 routing_id 索引出站 pipe 的能力。ROUTER 和 STREAM 继承此类。

### F-024：socket_base_t 关键纯虚钩子

**信源**：`src/socket_base.hpp` L155-L182

**纯虚函数**（子类必须实现）：

```cpp
virtual void xattach_pipe (pipe_t *pipe_, bool subscribe_to_all_, bool locally_initiated_) = 0;
virtual void xpipe_terminated (pipe_t *pipe_) = 0;
```

**虚函数**（默认实现，子类按需覆写）：

| 方法 | 默认行为 | 覆写典型场景 |
|------|---------|-------------|
| `xsetsockopt(int, const void*, size_t)` | 无特殊选项 | 处理模式特定选项（如 SUB 的 ZMQ_SUBSCRIBE） |
| `xgetsockopt(int, const void**, size_t*)` | 无特殊选项 | 返回模式特定属性 |
| `xhas_out()` | false（不支持发送） | PUSH/PUB/DEALER/ROUTER 覆写为 true |
| `xsend(msg_t*)` | 返回 ENOTSUP | 发送模式实现消息入队 |
| `xhas_in()` | false（不支持接收） | PULL/SUB/DEALER/ROUTER 覆写为 true |
| `xrecv(msg_t*)` | 返回 ENOTSUP | 接收模式实现消息出队 |
| `xread_activated(pipe_t*)` | 空实现 | 标记 pipe 为可读（fq/lb 激活） |
| `xwrite_activated(pipe_t*)` | 空实现 | 标记 pipe 为可写（HWM 恢复） |
| `xhiccuped(pipe_t*)` | 空实现 | 处理 pipe  hiccup（inproc 连接后配置同步） |

这是**模板方法模式**：`send()`/`recv()` 公共方法定义骨架算法，将具体路由委托给 `xsend()`/`xrecv()` 等 protected 虚函数。

### F-025：socket_base_t 持有 pipe 数组和 mailbox

**信源**：`src/socket_base.hpp` L293-L297

```cpp
i_mailbox *_mailbox;
typedef array_t<pipe_t, 3> pipes_t;
pipes_t _pipes;
```

- `_mailbox`：指向 socket 的邮箱（`mailbox_t` 或 `mailbox_safe_t`），接收来自其他线程的命令
- `_pipes`：存储所有附加到该 socket 的 pipe
- 模板参数 `3` 表示 pipe 可同时存在于三个数组中：
  - 数组 1：入站 pipe（有数据待读）
  - 数组 2：出站 pipe（可写入）
  - 数组 3：待释放 pipe（已终止等待销毁）

### F-026：socket_base_t::create 工厂方法

**信源**：`src/socket_base.cpp` L141-L225

```cpp
static socket_base_t *create (int type_, ctx_t *parent_,
                              uint32_t tid_, uint32_t sid_);
```

根据 `type_` 参数 switch 创建具体类型实例：

| type_ | 创建的类 | 头文件 |
|-------|---------|--------|
| `ZMQ_PAIR` | `pair_t` | pair.hpp |
| `ZMQ_PUB` | `pub_t` | pub.hpp |
| `ZMQ_SUB` | `sub_t` | sub.hpp |
| `ZMQ_REQ` | `req_t` | req.hpp |
| `ZMQ_REP` | `rep_t` | rep.hpp |
| `ZMQ_DEALER` | `dealer_t` | dealer.hpp |
| `ZMQ_ROUTER` | `router_t` | router.hpp |
| `ZMQ_PULL` | `pull_t` | pull.hpp |
| `ZMQ_PUSH` | `push_t` | push.hpp |
| `ZMQ_XPUB` | `xpub_t` | xpub.hpp |
| `ZMQ_XSUB` | `xsub_t` | xsub.hpp |
| `ZMQ_STREAM` | `stream_t` | stream.hpp |

Draft 类型（需 `ZMQ_BUILD_DRAFT_API`）：`server_t`、`client_t`、`radio_t`、`dish_t`、`gather_t`、`scatter_t`、`dgram_t`、`peer_t`、`channel_t`。

若 type_ 不匹配任何已知类型，返回 NULL 并设置 errno=EINVAL。

### F-027：线程安全 socket 使用 mailbox_safe_t

**信源**：`src/socket_base.cpp` L253-L266

构造函数中根据 `_thread_safe` 标志选择邮箱实现：

```cpp
if (options.thread_safe) {
    _mailbox = new mailbox_safe_t (&_sync);
} else {
    _mailbox = new mailbox_t ();
}
```

- **普通 socket**：使用 `mailbox_t`（基于 signaler），只能在创建线程中使用
- **线程安全 socket**：使用 `mailbox_safe_t`（基于条件变量），公共 API 调用通过 `scoped_optional_lock_t` 加锁 `_sync` 互斥量
- 线程安全 socket 类型：CLIENT、SERVER、CHANNEL、PEER（Draft API）

### F-028：bind 区分 inproc 和网络协议

**信源**：`src/socket_base.cpp` L536-L568

`bind(uri_)` 执行流程：

1. 解析 URI（`protocol://address`）
2. **若协议为 `inproc`**：
   - 构造 `endpoint_t{this, options}` 注册到 ctx 的 `_endpoints` map
   - 调用 `connect_pending(addr)` 连接已等待的 pending 连接
3. **其他协议**（tcp/ipc 等）：
   - 创建对应的 listener 对象（如 `tcp_listener_t`）
   - listener 在绑定的 I/O 线程中运行，接受新连接
   - 每接受一个连接，创建 session + engine + pipe 并附加到 socket

### F-029：connect_internal 为 inproc 直接创建 pipepair

**信源**：`src/socket_base.cpp` L823-L911

`connect_internal(uri_)` 中 inproc 分支执行流程：

1. 从 ctx 的 `_endpoints` map 查找已注册的 endpoint
2. **若对端已存在**（bind 方已绑定）：
   - 调用 `pipepair()` 创建双向管道
   - HWM 为两端 HWM 之和（`options.sndhwm + peer_options.rcvhwm`）
   - 通过 `send_bind` 命令将远端 pipe 附加到对端 socket
   - 本地端调用 `attach_pipe()` 附加本地 pipe
3. **若对端不存在**（bind 尚未调用）：
   - 将连接放入 `_pending_connections` multimap 等待
   - 后续 bind 时通过 `connect_pending()` 完成连接

非 inproc 协议（tcp/ipc）走 connecter 创建流程，在 I/O 线程中异步建立连接。

### F-030：send 调用 xsend 并支持超时重试

**信源**：`src/socket_base.cpp` L1263-L1349

`send(msg_, flags_)` 公共方法执行流程：

1. 调用 `process_commands(0)` 处理待处理命令
2. 重置消息 flags（清除 more/command 等标志）
3. 根据 `ZMQ_SNDMORE` 标志设置 `more` 标志
4. 调用虚函数 `xsend(msg_)` 执行实际发送
5. **若返回 EAGAIN 且非 DONTWAIT**：
   - 计算超时截止时间
   - 循环调用 `process_commands(timeout)` 处理命令
   - 重试 `xsend(msg_)`
   - 直到成功或超时（返回 EAGAIN）
6. 成功后若 `more` 为 false，增加 `_stat_sent_msgs` 计数

`recv()` 方法采用类似模式：调用 `xrecv()`，EAGAIN 时循环处理命令并重试。

### F-031：routing_socket_base_t 按 routing_id 索引出站 pipe

**信源**：`src/socket_base.hpp` L339-L386

```cpp
class routing_socket_base_t : public socket_base_t {
protected:
    struct out_pipe_t {
        pipe_t *pipe;
        bool active;
    };
    std::map<blob_t, out_pipe_t> _out_pipes;

    void add_out_pipe (const blob_t &routing_id_, pipe_t *pipe_);
    out_pipe_t *lookup_out_pipe (const blob_t &routing_id_);
    bool erase_out_pipe (pipe_t *pipe_);
    bool has_out_pipe (const blob_t &routing_id_) const;
};
```

- `_out_pipes`：以 routing_id（二进制 blob）为键，映射到目标 pipe
- `add_out_pipe`：pipe 附加时注册其 routing_id
- `lookup_out_pipe`：发送时根据消息第一帧（routing_id 帧）查找目标 pipe
- `erase_out_pipe`：pipe 终止时移除映射
- ROUTER 接收消息时自动前置 peer 的 routing_id 帧；发送时第一帧必须是 routing_id
- STREAM 继承此类但 routing_id 为连接的文件描述符

### F-020：object_t 是线程间通信基类

**信源**：`src/object.hpp` L28-L140

```cpp
class object_t {
    ctx_t *_ctx;
    uint32_t _tid;  // 所属线程 ID
};
```

`object_t` 提供两类方法：

**send_* 方法**（向其他线程的对象发送命令）：
- `send_stop`、`send_plug`、`send_own`、`send_attach`、`send_bind`
- `send_activate_read`、`send_activate_write`、`send_hiccup`
- `send_pipe_term`、`send_pipe_term_ack`、`send_pipe_hwm`、`send_pipe_peer_stats`
- `send_term_req`、`send_term`、`send_term_ack`、`send_term_endpoint`
- `send_reap`、`send_reaped`、`send_inproc_connected`
- `send_conn_failed`、`send_done`

**process_* 虚函数**（在所属线程中处理对应命令）：
- 默认实现为空或断言 false
- 子类按需覆写感兴趣的命令处理
- `process_command(cmd)` 是命令分发入口，根据 `cmd.type` switch 调用对应 `process_*`

### F-021：own_t 实现所有权层次和终止序列

**信源**：`src/own.hpp` L21-L117

```cpp
class own_t : public object_t {
    own_t *_owner;
    std::set<own_t*> _owned;
    bool _terminating;
    atomic_counter_t _sent_seqnum;
    std::set<uint32_t> _processed_seqnum;
    uint32_t _term_acks;
};
```

关键方法：

| 方法 | 说明 |
|------|------|
| `launch_child(own_t*)` | 启动子对象（发送 plug 命令） |
| `term_child(own_t*)` | 请求终止子对象 |
| `terminate()` | 启动自身终止序列 |
| `register_term_acks(n)` | 注册 n 个待确认终止 |
| `unregister_term_ack()` | 收到一个 term ack，计数减 1 |

终止序列：当对象调用 `terminate()` 后，向所有子对象发送 `term_req`；每个子对象完成清理后回复 `term_ack`；当所有 term acks 收齐（`_term_acks == 0`），对象自销毁。

### F-022：own_t 有两种构造方式

**信源**：`src/own.hpp` L29-L32

1. **`own_t(ctx_t *parent_, uint32_t tid_)`**：用于不在 I/O 线程内的对象（如 `socket_base_t`），直接传入上下文和线程 ID
2. **`own_t(io_thread_t *io_thread_, const options_t &options_)`**：用于生活在 I/O 线程内的对象（如 `session_base_t`、`tcp_listener_t`、`tcp_connecter_t`），从 io_thread 获取 ctx 和 tid，并将 options 复制到成员 `options`
