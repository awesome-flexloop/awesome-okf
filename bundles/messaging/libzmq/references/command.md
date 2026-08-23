---
type: reference
title: "command_t 与 mailbox：命令传递完整索引"
description: "src/command.hpp 中 22 种命令类型及 union 参数、object_t 的 send/process 方法对、mailbox_t 基于 ypipe+signaler 的实现、mailbox_safe_t 条件变量机制、signaler_t 跨平台 eventfd 封装"
tags: [libzmq, reference, command, mailbox, signaler]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  - path: "external/libs/remote/libzmq/src/command.hpp"
    facts: [F-048, F-049]
  - path: "external/libs/remote/libzmq/src/mailbox.hpp"
    facts: [F-050]
  - path: "external/libs/remote/libzmq/src/mailbox_safe.hpp"
    facts: [F-051]
  - path: "external/libs/remote/libzmq/src/signaler.hpp"
    facts: [F-052]
  - path: "external/libs/remote/libzmq/src/object.hpp"
    facts: [F-020]
  - path: "external/libs/remote/libzmq/src/own.hpp"
    facts: [F-021]
---

# command_t 与 mailbox：命令传递完整索引

## 信源概述

| 信源 | 职责 |
|------|------|
| `src/command.hpp` | command_t 类定义、22 种命令类型枚举、union 参数结构 |
| `src/object.hpp/cpp` | object_t 基类、send_* 发送方法、process_* 处理虚函数 |
| `src/mailbox.hpp/cpp` | mailbox_t 普通邮箱（ypipe + signaler） |
| `src/mailbox_safe.hpp/cpp` | mailbox_safe_t 线程安全邮箱（条件变量） |
| `src/signaler.hpp/cpp` | signaler_t 跨平台事件信号封装 |

## 关键事实登记

### F-048：command_t 包含 22 种命令类型

**信源**：`src/command.hpp` L26-L50

```cpp
class command_t {
public:
    enum type_t {
        stop,
        plug,
        own,
        attach,
        bind,
        activate_read,
        activate_write,
        hiccup,
        pipe_term,
        pipe_term_ack,
        pipe_hwm,
        term_req,
        term,
        term_ack,
        term_endpoint,
        reap,
        reaped,
        inproc_connected,
        conn_failed,
        pipe_peer_stats,
        pipe_stats_publish,
        done
    };
    // ...
};
```

完整命令清单及用途：

| 命令 | 用途 |
|------|------|
| `stop` | 通知 socket 开始终止 |
| `plug` | 通知对象（session/listener/connecter）已加入 I/O 线程 |
| `own` | 将子对象所有权注册到父对象 |
| `attach` | 将引擎附加到会话（携带 `i_engine*`） |
| `bind` | 将 pipe 绑定到 socket（携带 `pipe_t*`） |
| `activate_read` | 通知 pipe 有数据可读 |
| `activate_write` | 通知 pipe 写端恢复（携带 msgs_read 计数） |
| `hiccup` | inproc 连接后同步配置 |
| `pipe_term` | 请求终止 pipe |
| `pipe_term_ack` | 确认 pipe 终止 |
| `pipe_hwm` | 更新 pipe 的 HWM 配置 |
| `term_req` | 子对象请求父对象终止 |
| `term` | 父对象命令子对象终止（携带 linger） |
| `term_ack` | 子对象确认终止完成 |
| `term_endpoint` | 终止指定端点（携带 endpoint 字符串） |
| `reap` | 将 socket 交给 reaper 等待销毁（携带 `socket_base_t*`） |
| `reaped` | reaper 通知 ctx socket 已销毁 |
| `inproc_connected` | inproc 连接建立完成 |
| `conn_failed` | 连接失败 |
| `pipe_peer_stats` | pipe 对端统计信息更新 |
| `pipe_stats_publish` | 发布 pipe 统计 |
| `done` | reaper 通知 ctx 所有 socket 已回收 |

### F-049：command_t 使用 union 携带参数

**信源**：`src/command.hpp` L52-L185

```cpp
class command_t {
public:
    object_t *destination;
    type_t type;

    union args_t {
        struct { own_t *object; } own;
        struct { socket_base_t *socket; } reap;
        struct { i_engine *engine; } attach;
        struct { pipe_t *pipe; } bind;
        struct { pipe_t *pipe; } pipe_term;
        struct { pipe_t *pipe; } pipe_term_ack;
        struct { pipe_t *pipe; uint64_t msgs_read; } activate_write;
        struct { pipe_t *pipe; } hiccup;
        struct { int linger; } term;
        struct { std::string *endpoint; } term_endpoint;
        struct { pipe_t *pipe; uint64_t queue_size; } pipe_hwm;
        struct { pipe_t *pipe; } pipe_peer_stats;
        // ...
    } args;
};
```

关键命令参数说明：

| 命令 | 参数 | 说明 |
|------|------|------|
| `own` | `own_t *object` | 要注册所有权的子对象 |
| `reap` | `socket_base_t *socket` | 要回收的 socket |
| `attach` | `i_engine *engine` | 要附加的协议引擎 |
| `bind` | `pipe_t *pipe` | 要绑定的管道 |
| `activate_write` | `pipe_t *pipe` + `uint64_t msgs_read` | 对端已读取的消息数（用于 HWM 流控恢复） |
| `term` | `int linger` | 关闭逗留时间（毫秒） |
| `term_endpoint` | `std::string *endpoint` | 要终止的端点名（堆分配字符串） |

### F-050：mailbox_t 基于 ypipe + signaler

**信源**：`src/mailbox.hpp` L18-L56, `src/mailbox.cpp` L7-L74

```cpp
class mailbox_t : public i_mailbox {
private:
    ypipe_t<command_t, 16> _cpipe;
    signaler_t _signaler;
    mutex_t _sync;
};
```

| 成员 | 类型 | 说明 |
|------|------|------|
| `_cpipe` | `ypipe_t<command_t, 16>` | 命令无锁队列，粒度 16 |
| `_signaler` | `signaler_t` | 跨线程唤醒信号 |
| `_sync` | `mutex_t` | 保护发送端的互斥锁 |

**`send(cmd)` 流程**：
1. 加锁 `_sync`（多线程写安全）
2. `_cpipe.write(cmd)` 写入命令
3. `_cpipe.flush()` 刷新写入
4. 若 flush 返回 false（读端休眠），调用 `_signaler.send()` 唤醒读端
5. 解锁

**`recv(cmd*, timeout)` 流程**：
1. 先尝试 `_cpipe.read()` 非阻塞读取
2. 若有命令，立即返回
3. 若无命令，超时=0 返回 EAGAIN
4. 若 timeout>0，等待 `_signaler.wait(timeout)`
5. 被唤醒后循环读取所有命令（批量处理）

ypipe 粒度为 16 意味着命令队列每次批量分配 16 个 command_t 大小的内存块。

### F-051：mailbox_safe_t 使用条件变量

**信源**：`src/mailbox_safe.hpp` L20-L58

```cpp
class mailbox_safe_t : public i_mailbox {
private:
    condition_variable_t _cond_var;
    mutex_t *_sync;
    std::vector<signaler_t*> _signalers;
    ypipe_t<command_t, 16> _cpipe;
};
```

与 `mailbox_t` 的区别：

| 特性 | mailbox_t | mailbox_safe_t |
|------|-----------|----------------|
| 唤醒机制 | signaler（fd 事件） | 条件变量 + signaler |
| 线程安全 | 单写者（_sync 保护） | 多写者多读者 |
| 适用场景 | 普通 socket | 线程安全 socket（CLIENT/SERVER） |
| recv 阻塞 | signaler.wait() | cond_var.wait() |
| send 通知 | signaler.send() | cond_var.notify() + 所有 signaler.send() |

`_sync` 互斥锁由外部（socket_base_t）传入并持有，mailbox_safe_t 与 socket 的公共 API 共用同一把锁。

### F-052：signaler_t 是跨平台 eventfd/pipe 封装

**信源**：`src/signaler.hpp` L15-L58

```cpp
class signaler_t {
private:
    fd_t _r;  // 读 fd
    fd_t _w;  // 写 fd
};
```

**关键语义**：任一时刻最多有一个未读信号。重复发送信号是未定义行为——这与 eventfd 的信号量模式不同，signaler 是"边缘触发"的。

公共方法：

| 方法 | 说明 |
|------|------|
| `send()` | 发送一个信号（写入 _w） |
| `wait(timeout)` | 等待信号（超时返回 -1） |
| `recv()` | 接收信号（从 _r 读取，阻塞） |
| `recv_failable()` | 非阻塞接收（EAGAIN 表示无信号） |
| `get_fd()` | 返回读 fd（用于注册到 poller） |

**平台实现**：
- Linux：使用 `eventfd()`（单个 fd，非管道）
- 其他 POSIX：使用 `socketpair(AF_LOCAL)` 或 `pipe()`
- Windows：使用 `SO_RCVBUF`/`SO_SNDBUF` 为 1 的 TCP loopback socket

signaler 的 fd 被注册到 I/O 线程的 poller，当其他线程向 mailbox 发送命令时，通过 signaler 唤醒 poller 处理命令。

### F-020：object_t 是线程间通信基类

**信源**：`src/object.hpp` L28-L140

`object_t` 是所有生活在特定线程中的对象的基类，持有：
- `ctx_t *_ctx`：所属上下文
- `uint32_t _tid`：所属线程 ID（对应 ctx 的 slot 索引）

**命令发送方法**（send_*）：

每个 `send_*` 方法构造对应的 `command_t`，通过 `ctx->send_command(recipient_tid, cmd)` 投递到目标线程的 mailbox。

**命令处理方法**（process_*）：

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
virtual void process_pipe_hwm (int inhwm_, int outhwm_);
virtual void process_term_req (own_t *object_);
virtual void process_term (int linger_);
virtual void process_term_ack ();
virtual void process_term_endpoint (std::string *endpoint_);
virtual void process_reap (socket_base_t *socket_);
virtual void process_reaped ();
virtual void process_inproc_connected ();
virtual void process_conn_failed ();
virtual void process_pipe_peer_stats (uint64_t queue_size_, ...);
virtual void process_pipe_stats_publish (uint64_t ...);
```

默认实现为空操作或断言 false（不期望收到的命令）。子类覆写需要处理的命令。

`process_command(cmd)` 是命令分发入口，switch `cmd.type` 调用对应 `process_*`。

### F-021：own_t 终止序列中的命令流

**信源**：`src/own.hpp` L21-L117

own_t 的终止涉及以下命令交换：

```
父对象                         子对象
  │                              │
  │── term_req (子→父) ─────────►│  子对象请求关闭
  │                              │
  │◄── term (父→子, linger) ─────│  父对象批准终止
  │                              │
  │   子对象清理资源...           │
  │                              │
  │◄── term_ack (子→父) ────────│  子对象终止完成
  │                              │
  │   父对象 unregister_term_ack │
  │   所有 ack 收齐 → 自销毁      │
```

`register_term_acks(n)` 注册 n 个待确认终止，每个 `process_term_ack()` 调用 `unregister_term_ack()` 递减计数，归零后对象 `delete this`。
