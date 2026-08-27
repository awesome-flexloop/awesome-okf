---
type: concept
title: "I/O 线程与多路复用"
description: "io_thread_t 主循环处理 mailbox 命令、poller 平台抽象（epoll/kqueue/select 编译时选择）、io_object_t fd 事件适配器、signaler_t 跨平台 eventfd 封装、ypipe 无锁队列与 signaler 的协作"
tags: [libzmq, zeromq, io-thread, poller, epoll, kqueue, signaler, eventfd]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [../references/command.md]
  facts: [F-053, F-054, F-055, F-056, F-057, F-084, F-085, F-086]
---

# I/O 线程与多路复用

## 核心理解

I/O 线程是 libzmq 中执行实际网络 I/O 的后台线程。每个 I/O 线程运行一个**事件循环**，通过多路复用器（poller）同时监控多个文件描述符——包括网络 socket fd 和邮箱的 signaler fd。当 fd 就绪时，poller 调用对应对象的回调函数，执行实际的 `read()`/`write()` 系统调用或命令处理。

I/O 线程与应用线程通过邮箱（mailbox）和管道（pipe）完全解耦——应用线程不直接访问 I/O 线程的对象，反之亦然。这种设计使得网络 I/O 的延迟不会阻塞应用线程的消息收发。

## io_thread_t 结构

`io_thread_t` 继承自 `object_t` 和 `i_poll_events`（F-053）：

```cpp
class io_thread_t : public object_t, public i_poll_events {
    mailbox_t _mailbox;                    // 线程邮箱
    poller_t::handle_t _mailbox_handle;    // mailbox fd 在 poller 中的句柄
    poller_t *_poller;                     // 多路复用器
};
```

构造时：
1. 创建 `poller_t` 实例（根据平台选择 epoll/kqueue/select 等）
2. 创建 `mailbox_t`
3. 获取 mailbox 的 signaler fd
4. 将该 fd 注册到 poller，关注 `POLLIN` 事件
5. 将 fd 与自身（`this`）关联，使 poller 在 fd 可读时调用 `in_event()`

### I/O 线程主循环

`in_event()` 在 mailbox fd 可读时被 poller 调用（F-054）：

```cpp
void in_event () {
    command_t cmd;
    // 批量取出所有待处理命令（非阻塞）
    while (_mailbox.recv(&cmd, 0) == 0) {
        cmd.destination->process_command(cmd);
    }
}
```

关键点：
- **批量处理**：循环 recv 直到返回 EAGAIN，一次性处理所有积压命令
- **命令分发**：每个命令有 `destination` 指针，直接调用目标对象的 `process_command()`
- **零阻塞**：timeout=0 确保不会阻塞事件循环

`out_event()` 和 `timer_event()` 被断言为 false——I/O 线程自身不关注写事件和定时器（这些由具体的 io_object 子类使用）。

I/O 线程的实际事件循环在 `poller->start()` 中，它循环调用多路复用等待（`epoll_wait`/`kevent`/`select`），当 fd 就绪时回调关联对象的事件处理方法。

## poller 平台抽象

`poller.hpp` 通过编译宏选择底层多路复用实现（F-055）：

```cpp
#if defined ZMQ_IOTHREAD_POLLER_USE_KQUEUE
#   include "kqueue.hpp"
#elif defined ZMQ_IOTHREAD_POLLER_USE_EPOLL
#   include "epoll.hpp"
#elif defined ZMQ_IOTHREAD_POLLER_USE_DEVPOLL
#   include "devpoll.hpp"
#elif defined ZMQ_IOTHREAD_POLLER_USE_POLLSET
#   include "pollset.hpp"
#elif defined ZMQ_IOTHREAD_POLLER_USE_POLL
#   include "poll.hpp"
#elif defined ZMQ_IOTHREAD_POLLER_USE_SELECT
#   include "select.hpp"
#else
#   error No polling mechanism available
#endif
```

| 实现 | 平台 | 特点 |
|------|------|------|
| epoll | Linux | O(1) 就绪通知，水平触发（LT） |
| kqueue | macOS/BSD | O(1) 就绪通知，支持过滤器 |
| devpoll | Solaris | /dev/poll |
| pollset | AIX | pollset API |
| poll | POSIX 通用 | O(n) 遍历，无 fd 数量硬限制 |
| select | 通用回退 | O(n)，FD_SETSIZE 限制（通常 1024） |

CMake 配置时按优先级自动检测：kqueue/epoll → devpoll/pollset → poll → select。同一时间只能定义一个宏，否则编译错误。

所有 poller 实现统一的 `poller_t` 接口：
- `add_fd(fd, events)`：注册 fd
- `rm_fd(handle)`：移除 fd
- `set_pollin(handle)`/`reset_pollin(handle)`：启用/禁用读事件
- `set_pollout(handle)`/`reset_pollout(handle)`：启用/禁用写事件
- `add_timer(delay, id)`/`cancel_timer(id)`：定时器管理
- `start()`/`stop()`：事件循环

## io_object_t：fd 事件适配器

`io_object_t` 是所有需要使用 poller 的对象的基类（F-056）：

```cpp
class io_object_t : public i_poll_events {
    poller_t *_poller;
protected:
    handle_t add_fd (fd_t fd);
    void rm_fd (handle_t handle);
    void set_pollin (handle_t handle);
    void reset_pollin (handle_t handle);
    void set_pollout (handle_t handle);
    void reset_pollout (handle_t handle);
    void add_timer (size_t timeout, int id);
    void cancel_timer (int id);
};
```

它持有 `_poller` 指针（构造时从 I/O 线程获取），提供 poller 的包装方法。子类覆写以下回调：

| 回调 | 触发条件 |
|------|---------|
| `in_event()` | fd 可读 |
| `out_event()` | fd 可写 |
| `timer_event(id)` | 定时器到期 |

默认实现为空——子类只覆写需要的回调。例如：
- `stream_engine_base_t` 覆写 `in_event`/`out_event`（网络读写）和 `timer_event`（握手超时、心跳）
- `tcp_connecter_t` 覆写 `out_event`（连接完成）和 `timer_event`（连接超时、重连）
- `tcp_listener_t` 覆写 `in_event`（接受新连接）

### i_poll_events 接口

所有 poller 事件回调的接口定义（F-057）：

```cpp
struct i_poll_events {
    virtual ~i_poll_events () {}
    virtual void in_event () = 0;
    virtual void out_event () = 0;
    virtual void timer_event (int id_) = 0;
};
```

三个纯虚函数分别对应可读、可写、定时器到期。注意这个接口同时被 `io_thread_t` 本身（处理 mailbox 命令）和 `io_object_t` 子类（处理网络事件）实现。

## signaler_t：跨平台事件信号

`signaler_t` 是 `signal_fd` 的跨平台等价物（F-052），用于唤醒正在 poller 中等待的 I/O 线程。

```cpp
class signaler_t {
    fd_t _r;  // 读 fd
    fd_t _w;  // 写 fd
};
```

### 关键语义

**任一时刻最多有一个未读信号**。重复发送信号是未定义行为——这不是信号量，而是"边缘触发"通知：
- `send()`：写入一个字节（或 eventfd 加 1）
- `wait(timeout)`：等待信号（poll 等待 _r 可读）
- `recv()`：读取信号（清空 _r），阻塞
- `recv_failable()`：非阻塞读取（EAGAIN 表示无信号）
- `get_fd()`：返回读 fd，用于注册到 poller

### 平台实现

| 平台 | 实现 |
|------|------|
| Linux | `eventfd(0, EFD_CLOEXEC \| EFD_NONBLOCK)` — 单个 fd，无管道开销 |
| macOS/BSD | `socketpair(AF_LOCAL, SOCK_STREAM)` — 两个 fd |
| 其他 POSIX | `pipe2(O_CLOEXEC \| O_NONBLOCK)` — 两个 fd |
| Windows | TCP loopback socket，缓冲区设为 1 |

Linux 的 eventfd 实现最优——只需要一个 fd、一次系统调用，且内核维护 64 位计数器。但 libzmq 将其当作"二进制信号"使用（最多一个未读信号），在 recv 时清空计数器。

### signaler 与 mailbox 的协作

mailbox_t 内部组合了 ypipe 和 signaler（F-050）：

```
写线程（应用线程）              读线程（I/O 线程）
     │                              │
     │ write command to cpipe       │
     │ flush() returns:             │
     │   true? → 什么都不做         │ poller 在 signaler._r 上等待
     │   false? → signaler.send()  │
     │            ──────────────►  │ signaler._r 可读
     │                              │ poller 调用 io_thread.in_event()
     │                              │ mailbox.recv() 批量取出命令
     │                              │ process_command() 分发
```

flush 返回 false 意味着 ypipe 的 `_c` 原子指针为 NULL（读端休眠），需要 signaler 唤醒。这是一个优化——如果读端正活跃处理命令（`_c != NULL`），就不需要额外的系统调用。

## ypipe + signaler 的协作机制

ypipe 的 flush 实现是无锁队列与信号机制的桥梁（F-085）：

```cpp
bool flush () {
    if (_c.cas(_w, _f)) {
        // CAS 成功：_c 之前不是 NULL，读端存活
        _w = _f;
        return true;  // 不需要唤醒
    } else {
        // CAS 失败：_c == NULL，读端休眠
        _c = _f;       // 非原子设置（写线程独占）
        _w = _f;
        return false;  // 需要 signaler 唤醒
    }
}
```

原子指针 `_c` 是读写线程唯一的争用点：
- 非 NULL：读端活跃，正在/即将处理队列
- NULL：读端休眠，需要 signal 唤醒

读端在读取完所有可用项后，将 `_c` CAS 为 NULL 然后进入 poller 等待。

## yqueue_t：批量内存分配

yqueue_t 是 ypipe 的底层存储（F-086），以 chunk 为单位分配：

```cpp
template <typename T, int N>
class yqueue_t {
    struct chunk_t {
        T values[N];
        chunk_t *prev;
        chunk_t *next;
    };
    chunk_t *_begin_chunk, *_back_chunk, *_end_chunk;
    int _begin_pos, _back_pos, _end_pos;
    static atomic_ptr_t<chunk_t> _spare_chunk;
};
```

- N 是每个 chunk 的元素数：消息管道 N=256，命令管道 N=16
- `_spare_chunk` 是线程局部静态缓存，最近释放的 chunk 不立即 free，而是缓存供下次分配使用
- 支持 `posix_memalign` 按缓存行对齐（默认 64 字节），避免多线程伪共享
- chunk 形成双向链表，队列两端可以独立推进和回退

这种设计避免了每条消息都 malloc/free——以 256 条消息为批量分配单位，在高吞吐场景下显著减少内存分配器压力。

## 多 I/O 线程扩展

通过 `zmq_ctx_set(context, ZMQ_IO_THREADS, N)` 可以配置多个 I/O 线程：

1. ctx 启动时创建 N 个 io_thread_t，每个有独立的 poller 和 mailbox
2. 创建 socket 时，`choose_io_thread(affinity)` 选择负载最低的 I/O 线程
3. 该 socket 的所有连接（session/engine/listener/connecter）都在同一个 I/O 线程上
4. 不同 socket 可能分布在不同 I/O 线程，实现网络 I/O 并行

`affinity` 参数是位掩码，允许将某些 socket 绑定到特定 I/O 线程（例如实时优先级的线程处理高优先级连接）。

## 相关概念

- [上下文与基础设施](01-context.md) — ctx 创建和管理 I/O 线程池
- [命令传递与邮箱](08-command-mailbox.md) — mailbox_t 的完整实现、mailbox_safe_t 条件变量
- [管道与流控](04-pipe.md) — ypipe 在 pipe 中的使用
- [会话与连接生命周期](05-session.md) — session 和 engine 作为 io_object 注册 fd
- [ZMTP 协议引擎](06-zmtp-engine.md) — stream_engine_base 使用 poller 进行网络读写
