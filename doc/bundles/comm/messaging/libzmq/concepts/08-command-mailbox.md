---
type: concept
title: "命令传递与邮箱"
description: "command_t 的 22 种命令类型及 union 参数、object_t 的 send/process 方法对、mailbox_t 基于 ypipe+signaler 的实现、mailbox_safe_t 条件变量机制、应用线程 process_commands 命令处理循环"
tags: [libzmq, zeromq, command, mailbox, signaler, thread-communication, condition-variable]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [../references/command.md, ../references/socket-base.md]
  facts: [F-048, F-049, F-050, F-051, F-052, F-020, F-021]
---

# 命令传递与邮箱

## 核心理解

libzmq 的线程间通信不使用共享状态加锁，而是通过**邮箱（mailbox）**传递**命令对象（command_t）**。每个生活在特定线程中的对象（socket、session、io_object）都有一个邮箱，其他线程通过向其邮箱发送命令来请求操作，命令在目标线程的主循环中被串行处理。

这是 Actor 模型的变体——对象不共享内存，而是通过异步消息通信。设计目标是彻底消除应用线程与 I/O 线程之间的数据竞争，代价是命令处理有一定延迟。

## command_t：22 种命令

`command_t` 是线程间通信的消息单元（F-048），包含：

```cpp
class command_t {
public:
    enum type_t {
        stop, plug, own, attach, bind,
        activate_read, activate_write, hiccup,
        pipe_term, pipe_term_ack, pipe_hwm,
        term_req, term, term_ack, term_endpoint,
        reap, reaped, inproc_connected, conn_failed,
        pipe_peer_stats, pipe_stats_publish, done
    };

    object_t *destination;
    type_t type;
    args_t args;  // union，携带命令特定参数
};
```

### 命令分类

**生命周期管理**：

| 命令 | 方向 | 用途 |
|------|------|------|
| `stop` | ctx → socket | 通知 socket 开始关闭 |
| `plug` | owner → child | 通知子对象已加入 I/O 线程 |
| `own` | child → owner | 注册子对象所有权 |
| `term_req` | child → parent | 子对象请求终止 |
| `term` | parent → child | 父对象批准终止（携带 linger） |
| `term_ack` | child → parent | 子对象终止完成 |
| `reap` | socket → reaper | 将 socket 交给 reaper |
| `reaped` | reaper → ctx | socket 已回收 |
| `done` | reaper → term_mailbox | 所有 socket 回收完成 |

**管道与引擎**：

| 命令 | 用途 |
|------|------|
| `attach` | 将引擎附加到会话（携带 `i_engine*`） |
| `bind` | 将 pipe 绑定到 socket（携带 `pipe_t*`） |
| `activate_read` | 通知 pipe/socket 有数据可读 |
| `activate_write` | 通知 pipe 写端恢复（携带 msgs_read） |
| `hiccup` | inproc 连接后同步配置 |
| `pipe_term` | 请求终止 pipe |
| `pipe_term_ack` | 确认 pipe 终止 |
| `pipe_hwm` | 更新 pipe 的 HWM 配置 |

**连接与端点**：

| 命令 | 用途 |
|------|------|
| `inproc_connected` | inproc 连接建立完成 |
| `conn_failed` | 连接失败 |
| `term_endpoint` | 终止指定端点（携带 endpoint 字符串） |

**统计**：

| 命令 | 用途 |
|------|------|
| `pipe_peer_stats` | pipe 对端统计更新 |
| `pipe_stats_publish` | 发布 pipe 统计 |

### union 参数

不同命令携带不同参数（F-049），通过 union 紧凑存储：

```cpp
union args_t {
    struct { own_t *object; } own;
    struct { socket_base_t *socket; } reap;
    struct { i_engine *engine; } attach;
    struct { pipe_t *pipe; } bind;
    struct { pipe_t *pipe; uint64_t msgs_read; } activate_write;
    struct { int linger; } term;
    struct { std::string *endpoint; } term_endpoint;
    // ...
};
```

`destination` 指针指定命令的处理对象——命令到达目标线程后，调用 `destination->process_command(cmd)` 分发。

## object_t：命令发送与处理

`object_t` 是所有生活在线程中的对象的基类（F-020），提供：

### send_* 方法

每个 `send_*` 方法构造对应的 command_t，通过 `ctx->send_command(target_tid, cmd)` 投递到目标邮箱。例如：

```cpp
void send_bind (own_t *destination_, pipe_t *pipe_) {
    command_t cmd(destination_, command_t::bind, pipe_);
    _ctx->send_command(destination_->get_tid(), cmd);
}
```

关键设计：发送者不需要知道目标邮箱的具体地址，只需通过 ctx 的 slot 数组按 tid 查找。

### process_* 虚函数

每个命令类型对应一个虚函数处理方法：

```cpp
virtual void process_stop ();
virtual void process_plug ();
virtual void process_own (own_t *object_);
virtual void process_attach (i_engine *engine_);
virtual void process_bind (pipe_t *pipe_);
virtual void process_activate_read ();
virtual void process_activate_write (uint64_t msgs_read_);
virtual void process_hiccup (void *pipe_);
virtual void process_pipe_term ();
virtual void process_pipe_term_ack ();
virtual void process_term_req (own_t *object_);
virtual void process_term (int linger_);
virtual void process_term_ack ();
virtual void process_reap (socket_base_t *socket_);
// ...
```

默认实现为空操作或断言 false。子类只覆写需要处理的命令。

`process_command(cmd)` 是分发入口，switch `cmd.type` 调用对应 `process_*`。

## mailbox_t：普通邮箱

`mailbox_t` 基于 ypipe + signaler 实现（F-050）：

```cpp
class mailbox_t : public i_mailbox {
    ypipe_t<command_t, 16> _cpipe;  // 命令无锁队列
    signaler_t _signaler;            // 跨线程唤醒
    mutex_t _sync;                   // 保护多写者
};
```

### cpipe 设计

`ypipe_t<command_t, 16>` 使用 N=16 粒度——每个 chunk 存储 16 个 command_t。命令通常比消息小且不频繁，16 的粒度在内存使用和批量效率之间取得平衡。

### send 流程

```cpp
void send (const command_t &cmd_) {
    _sync.lock();              // 多线程写安全
    _cpipe.write(cmd_, false); // 写入命令（false = 不是 more）
    bool ok = _cpipe.flush();
    _sync.unlock();
    if (!ok) {
        _signaler.send();     // 读端休眠，唤醒
    }
}
```

关键点：
- `_sync` 互斥锁保护写端——多个应用线程可以向同一个 I/O 线程邮箱发送命令
- flush 返回 false 时才需要 signaler 系统调用（优化：读端活跃时跳过）
- signaler 发送一个信号唤醒 poller

### recv 流程

```cpp
int recv (command_t *cmd_, int timeout_) {
    // 先尝试非阻塞读取
    if (_cpipe.read(cmd_)) {
        return 0;  // 成功
    }

    if (timeout_ == 0) {
        return EAGAIN;
    }

    // 等待 signaler
    int rc = _signaler.wait(timeout_);
    if (rc == -1 && errno == EAGAIN) {
        return EAGAIN;
    }

    // 被唤醒，批量读取所有命令
    _signaler.recv();  // 清空信号
    if (!_cpipe.read(cmd_)) {
        return EAGAIN;  // 竞态：信号和命令之间可能有间隙
    }
    return 0;
}
```

signaler 可能在命令写入之前就被触发（flush 和 send 之间有窗口），因此 recv 后必须再次检查 cpipe。

## mailbox_safe_t：线程安全邮箱

`mailbox_safe_t` 用于线程安全 socket（CLIENT/SERVER/CHANNEL/PEER），基于条件变量而非 signaler（F-051）：

```cpp
class mailbox_safe_t : public i_mailbox {
    mutex_t *_sync;                    // 外部传入，与 socket 共用
    condition_variable_t _cond_var;    // 条件变量
    std::vector<signaler_t*> _signalers;
    ypipe_t<command_t, 16> _cpipe;
};
```

### 与 mailbox_t 的区别

| 特性 | mailbox_t | mailbox_safe_t |
|------|-----------|----------------|
| 唤醒机制 | signaler（fd 事件） | 条件变量 + signaler |
| 读者 | 单个（I/O 线程） | 多个（应用线程） |
| 锁粒度 | 仅写端加锁 | 读写都加锁 |
| 适用场景 | 普通 socket | 线程安全 socket |
| recv 阻塞方式 | signaler.wait() | cond_var.wait() |
| send 通知方式 | signaler.send() | cond_var.notify() + signalers |

### 为什么需要条件变量？

mailbox_t 的设计假设只有一个读者（I/O 线程的 poller 事件循环）。对于线程安全 socket，多个应用线程可能同时调用 recv，signaler 的"最多一个未读信号"语义不够——需要条件变量让多个线程等待同一队列。

`_sync` 互斥锁由 socket_base_t 持有并传入，mailbox_safe_t 与 socket 的公共 API 共用同一把锁，避免死锁。

### _signalers 列表

线程安全 socket 可能被多个线程使用，每个线程可能需要被唤醒。`_signalers` 列表存储所有等待线程的 signaler，send 时通知所有 signaler 和条件变量。

## 应用线程的命令处理

应用线程（socket 所在线程）没有 poller 事件循环，但它在 `send()`/`recv()` 时处理自己邮箱中的命令：

```cpp
// socket_base_t::send 内部
int process_commands (int timeout_, bool throttle_) {
    // ...
    while (true) {
        command_t cmd;
        if (_mailbox->recv(&cmd, 0) == 0) {
            cmd.destination->process_command(cmd);
        } else {
            break;  // 没有更多命令
        }
    }
    // ...
}
```

这意味着：
1. I/O 线程的命令（activate_read/activate_write/pipe_term 等）在应用线程下次调用 send/recv 时才被处理
2. 如果应用线程长时间不调用 send/recv，命令会积压在邮箱中
3. `ZMQ_FD` 选项提供的 fd 可用于集成到外部事件循环，当邮箱有命令时 fd 变为可读

### 超时重试中的命令处理

`send()` 的超时重试循环中反复调用 `process_commands(timeout)`（F-030）：

```
while xsend returns EAGAIN:
    process_commands(remaining_timeout)
        → 可能收到 activate_write 命令（pipe 恢复可写）
        → xwrite_activated 更新路由算法状态
    retry xsend
```

这就是为什么 `zmq_send` 在 HWM 满时阻塞，但一旦 I/O 线程发送了一些消息（通过 activate_write 通知），send 就能恢复——命令在 process_commands 中被处理，更新了 socket 的可写状态。

## 命令流示例：连接建立

以下是一个 TCP connect 操作涉及的命令流：

```
应用线程                      I/O 线程                     对端
  │                              │                           │
  │ zmq_connect()                │                           │
  │── send_own(ctx, session) ──►│                           │
  │── send_own(ctx, connecter) ►│                           │
  │                              │ process_plug(session)     │
  │                              │ process_plug(connecter)   │
  │                              │ connecter.open()          │
  │                              │── TCP SYN ──────────────►│
  │                              │◄─ SYN-ACK ───────────────│
  │                              │ out_event(): connected    │
  │                              │ 创建 engine + session     │
  │                              │ engine.plug()             │
  │                              │── ZMTP greeting ────────►│
  │                              │◄─ ZMTP greeting ─────────│
  │                              │ 握手...                   │
  │                              │ 握手完成                   │
  │◄─ send_bind(socket, pipe) ───│                           │
  │ process_bind():              │                           │
  │   xattach_pipe(pipe)         │                           │
  │   pipe 可用于收发            │                           │
```

## 终止序列中的命令流

上下文终止涉及多个命令往返：

```
zmq_ctx_term()
  │
  ├─► send stop to all sockets
  │     │
  │     └─► socket.process_stop()
  │           ├─ terminate all sessions (send term_req)
  │           └─ close all pipes
  │
  ├─► socket 完成关闭后 send reap 到 reaper
  │     │
  │     └─► reaper.process_reap(socket)
  │           └─ 收集 socket
  │
  └─► 所有 socket reaped 后
        reaper send done 到 term_mailbox
          │
          └─► terminate() unblocks → delete this
```

`own_t` 的终止协议（F-021）也通过命令完成：`term_req` → `term` → `term_ack`，确保对象树中所有子对象都清理完毕后父对象才销毁。

## 相关概念

- [套接字基类](02-socket-base.md) — socket 的 process_commands 在 send/recv 中调用
- [上下文与基础设施](01-context.md) — ctx 通过 slots 数组路由命令到目标邮箱
- [I/O 线程与多路复用](07-io-thread-poller.md) — I/O 线程通过 poller 监听 signaler fd
- [管道与流控](04-pipe.md) — activate_read/write 命令驱动 pipe 流控
- [会话与连接生命周期](05-session.md) — plug/attach/bind 命令建立会话
