---
type: concept
title: "上下文与基础设施"
description: "ctx_t 延迟启动机制、slot 槽位分配、I/O 线程池管理、reaper 终止序列、inproc 端点注册表、choose_io_thread 负载选择"
tags: [libzmq, zeromq, context, ctx, io-thread, reaper]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [../references/ctx.md, ../references/command.md]
  facts: [F-012, F-013, F-014, F-015, F-016, F-017, F-018, F-019, F-053, F-054, F-055]
---

# 上下文与基础设施

## 核心理解

`ctx_t`（上下文）是 libzmq 的全局容器，管理着 I/O 线程池、socket 槽位、inproc 端点注册表和整个库的生命周期。一个进程通常只需要一个上下文——所有 socket 都从同一个上下文创建，共享 I/O 线程池。

上下文的核心设计特点是**延迟启动**：`zmq_ctx_new()` 只做最小初始化，不创建任何线程；直到第一个 socket 被创建时才启动 I/O 线程和 reaper 线程。这使得仅创建上下文但不使用时零开销。

## ctx_t 的继承结构

`ctx_t` 继承自 `thread_ctx_t`（F-012），后者管理线程调度参数：

```cpp
class thread_ctx_t {
    int _thread_priority;           // 线程优先级
    int _thread_sched_policy;       // 调度策略（SCHED_RR/SCHED_FIFO 等）
    std::set<int> _thread_affinity_cpus;  // CPU 亲和性
    std::string _thread_name_prefix;      // 线程名前缀
    mutex_t _opt_sync;              // 保护上述参数
};

class ctx_t ZMQ_FINAL : public thread_ctx_t { ... };
```

`ctx_t` 使用 `ZMQ_FINAL` 标记（F-012），不可再被继承。这些线程参数在 I/O 线程创建时应用，使 libzmq 可以在实时系统中配置线程优先级和 CPU 绑定。

## 关键成员

`ctx_t` 包含以下关键成员（F-013）：

| 成员 | 类型 | 职责 |
|------|------|------|
| `_tag` | uint32_t | 魔数 0xabadcafe，调试时检测野指针 |
| `_sockets` | array_t<socket_base_t> | 所有已创建的 socket |
| `_empty_slots` | vector<uint32_t> | 空闲槽位列表 |
| `_starting` | bool | 延迟启动标志（true=尚未启动基础设施） |
| `_terminating` | bool | 终止中标志 |
| `_slot_sync` | mutex_t | 保护槽位分配 |
| `_reaper` | reaper_t* | reaper 线程 |
| `_io_threads` | vector<io_thread_t*> | I/O 线程池 |
| `_slots` | vector<i_mailbox*> | 按 tid 索引的邮箱数组 |
| `_term_mailbox` | mailbox_t | 终止线程邮箱（槽位 0） |
| `_endpoints` | map<string, endpoint_t> | inproc 端点注册表 |
| `_pending_connections` | multimap<string, pipe_t*> | 等待 bind 的 inproc 连接 |
| `_max_sockets` | int | 最大 socket 数（默认 1023） |
| `_io_thread_count` | int | I/O 线程数（默认 1） |
| `_zero_copy` | bool | 零拷贝接收（默认 true） |

## 延迟启动：start() 函数

`start()` 在首次调用 `create_socket()` 时触发（F-016），执行以下步骤：

### 1. 计算槽位总数

```
slot_count = max_sockets + io_thread_count + 2
```

额外 2 个槽位预留给：
- 槽位 0：term mailbox（`term_tid = 0`）
- 槽位 1：reaper mailbox（`reaper_tid = 1`）

例如默认配置（1023 socket + 1 I/O 线程）需要 1026 个槽位。

### 2. 固定槽位分配

槽位布局：
```
[0] term_mailbox
[1] reaper mailbox
[2] io_thread[0] mailbox
[3] io_thread[1] mailbox（如果有）
...
[N] socket[0] mailbox
[N+1] socket[1] mailbox
...
```

每个生活在特定线程的对象都有一个 `_tid`（线程 ID），就是其在 `_slots` 数组中的索引。其他线程通过 `_slots[target_tid]` 找到目标邮箱并发送命令。

### 3. 创建并启动 reaper 线程

reaper 是一个特殊线程，负责在 socket 关闭时回收资源。它有自己的邮箱（槽位 1），接收 `reap` 命令。

### 4. 创建并启动 I/O 线程

创建 `io_thread_count` 个 `io_thread_t`，每个 I/O 线程：
- 创建自己的 `poller_t`（epoll/kqueue/select 等，F-055）
- 创建自己的 `mailbox_t`
- 将 mailbox 的 signaler fd 注册到 poller（F-053）
- 启动线程，进入 poller 主循环

### 5. 剩余槽位加入空闲列表

未分配的槽位加入 `_empty_slots`，供后续 socket 创建使用。

**为什么延迟启动？** 许多应用程序可能在初始化时创建上下文，但在某些运行路径上不创建任何 socket。延迟启动确保这些场景不会产生不必要的线程和系统资源。

## create_socket：槽位分配与工厂委托

`create_socket(type_)` 是创建新 socket 的入口（F-017）：

```
1. 加锁 _slot_sync
2. 检查 _terminating → 返回 ETERM
3. 若 _starting → 调用 start() 启动基础设施
4. 从 _empty_slots 取一个槽位
5. 生成唯一 sid（max_socket_id 原子递增）
6. 调用 socket_base_t::create(type_, this, slot, sid) 创建实例
7. 将 socket mailbox 注册到 _slots[slot]
8. 将 socket 加入 _sockets 数组
9. 返回 socket 指针
```

`socket_base_t::create()` 是静态工厂方法（F-026），根据 `type_` 参数 switch 创建具体类型：
- `ZMQ_PUB` → `pub_t`
- `ZMQ_SUB` → `sub_t`
- `ZMQ_DEALER` → `dealer_t`
- `ZMQ_ROUTER` → `router_t`
- 等等

每个 socket 绑定到一个固定的 I/O 线程（通过 `choose_io_thread` 选择，F-019）。该 I/O 线程负责该 socket 所有连接的实际网络 I/O。

## inproc 端点注册表

`_endpoints` 是一个 `map<string, endpoint_t>`（F-014），存储 inproc 端点：

```cpp
struct endpoint_t {
    socket_base_t *socket;
    options_t options;
};
```

当 socket 调用 `bind("inproc://name")` 时（F-028）：
1. 构造 `endpoint_t{this, options}`
2. 注册到 `ctx._endpoints["name"]`
3. 检查 `_pending_connections` 中是否有等待该端点的连接
4. 若有，为每个等待连接创建 pipepair

当另一个 socket 调用 `connect("inproc://name")` 时（F-029）：
1. 在 `_endpoints` 中查找
2. 若已注册：直接创建 pipepair，双向附加
3. 若未注册：将连接放入 `_pending_connections` 等待 bind

选项副本的存在使得 connect 方无需同步即可访问 bind 方的 HWM、conflate 等配置，因为 `options_t` 是值类型。

## I/O 线程选择

`choose_io_thread(affinity_)` 返回当前最空闲的 I/O 线程（F-019）：

- `affinity` 是位掩码，第 i 位为 1 表示允许使用第 i 个 I/O 线程
- affinity=0 表示所有 I/O 线程都合格
- 选择当前负载最低的线程（基于待处理事件数）

这意味着同一 socket 的所有连接都在同一个 I/O 线程上处理，但不同 socket 可能分布在不同 I/O 线程上，实现 I/O 并行。

## 终止序列：terminate()

`zmq_ctx_term()` 调用 `terminate()`，这是一个复杂的多阶段过程（F-018）：

### 阶段 1：连接 pending inproc

遍历 `_pending_connections`，为每个等待中的连接创建临时 PAIR socket 并绑定。这确保了那些 connect 在 bind 之前的 inproc 连接不会永久阻塞——它们会收到一个连接到临时 socket 的 pipe，然后随临时 socket 一起关闭。

### 阶段 2：通知所有 socket 停止

向每个 socket 发送 `stop` 命令。socket 收到后开始关闭流程：
- 关闭所有 pipe
- 终止所有 session
- 停止所有 listener/connecter

### 阶段 3：socket 自我回收

每个 socket 完成关闭后，通过 `send_reap` 命令将自己交给 reaper 线程。reaper 收集所有已关闭的 socket。

### 阶段 4：等待 reaper 完成

`terminate()` 阻塞在 `_term_mailbox.recv(&cmd, -1)` 上，等待 reaper 发送 `done` 命令。当 reaper 确认所有 socket 都已回收后，发送 `done` 到 term mailbox。

### 阶段 5：清理和自销毁

收到 `done` 后：
- 停止所有 I/O 线程
- 停止 reaper 线程
- 释放槽位数组
- `delete this` 自销毁

完整的终止信号传播链：

```
zmq_ctx_term()
  │
  ├─► send stop to all sockets
  │     │
  │     └─► each socket closes pipes/sessions
  │           │
  │           └─► send reap to reaper
  │                 │
  │                 └─► reaper collects all sockets
  │                       │
  │                       └─► send done to term_mailbox
  │                             │
  └─────────────────────────────┘
        terminate() unblocks
        → stop I/O threads
        → delete this
```

**为什么需要 reaper？** socket 的关闭涉及与 I/O 线程的命令往返。如果在应用线程中直接删除 socket，可能 I/O 线程还在访问该 socket 的 pipe。reaper 线程确保 socket 在所有 I/O 线程都确认断开后才被安全销毁。

## zmq_ctx_shutdown vs zmq_ctx_term

两者有重要区别：
- `zmq_ctx_shutdown()`：立即关闭上下文中的所有 socket，不阻塞。已在队列中的消息可能丢失
- `zmq_ctx_term()`：阻塞等待所有 socket 正常关闭（遵守 LINGER），确保消息发送完成

典型用法：
```c
// 优雅关闭
zmq_ctx_shutdown (context);  // 通知所有 socket 停止
zmq_ctx_term (context);      // 等待清理完成
```

## I/O 线程主循环

每个 I/O 线程运行一个 poller 主循环（F-053, F-054）：

1. poller 等待注册的 fd 就绪（包括 mailbox 的 signaler fd 和所有网络 socket fd）
2. 当 mailbox fd 可读时（其他线程发送了命令）：
   - 循环 `_mailbox.recv(&cmd, 0)` 取出所有命令
   - 对每个命令调用 `cmd.destination->process_command(cmd)`
3. 当网络 fd 可读/可写时：
   - 调用对应 engine 的 `in_event()`/`out_event()`
   - engine 执行实际的 read()/write() 系统调用

这种设计确保 I/O 线程永远不会因为处理一个慢连接而阻塞其他连接——poller 的水平触发（或边缘触发）特性保证了公平性。

## poller 平台抽象

`poller.hpp` 通过编译宏选择底层多路复用机制（F-055）：

| 宏 | 平台 | 实现 |
|---|---|---|
| `ZMQ_IOTHREAD_POLLER_USE_EPOLL` | Linux | epoll |
| `ZMQ_IOTHREAD_POLLER_USE_KQUEUE` | macOS/BSD | kqueue |
| `ZMQ_IOTHREAD_POLLER_USE_DEVPOLL` | Solaris | /dev/poll |
| `ZMQ_IOTHREAD_POLLER_USE_POLLSET` | AIX | pollset |
| `ZMQ_IOTHREAD_POLLER_USE_POLL` | POSIX 通用 | poll() |
| `ZMQ_IOTHREAD_POLLER_USE_SELECT` | 通用回退 | select() |

同一时间只能定义一个宏，否则编译错误。CMake 配置时自动检测最佳实现。

## 相关概念

- [套接字基类](/concepts/02-socket-base.md) — socket_base_t 的模板方法模式和 x-钩子
- [命令传递与邮箱](/concepts/08-command-mailbox.md) — mailbox_t、signaler_t、22 种命令类型
- [I/O 线程与多路复用](/concepts/07-io-thread-poller.md) — io_thread 主循环、poller 抽象、io_object
- [管道与流控](/concepts/04-pipe.md) — pipepair、HWM/LWM 流控机制
- [传输层](/concepts/10-transport.md) — TCP connecter/listener、inproc 直连
