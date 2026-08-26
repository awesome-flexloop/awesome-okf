---
type: Concept
title: 事件循环与信号处理
description: conmon基于GLib GMainLoop的事件驱动架构、signalfd信号处理、self-pipe安全唤醒机制、超时回调完整解析
tags: [concept, event-loop, glib, gmainloop, signalfd, self-pipe, signals, sigchld, timeout]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
sources:
  - id: conmon-source
    resource: /bundles/containers/conmon/references/conmon-source.md
    title: conmon 主入口信源
---

# 事件循环与信号处理

conmon 使用 **GLib 的 GMainLoop** 作为事件驱动框架，而非手写 epoll 循环。这是一个反常识的选择——C 语言系统项目通常直接使用 epoll/select，但 conmon 选择 GLib 是因为其成熟的事件源抽象、跨平台兼容性和内存管理工具。

## GMainLoop 架构概述

GMainLoop 是 GLib 提供的事件循环实现，采用**事件源（GSource）注册 + 回调分发**模型：

```
┌─────────────────────────────────────────────────────────────┐
│                    GMainLoop 主循环                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  signalfd   │  │  self-pipe  │  │ g_timeout_add_seconds│ │
│  │  (SIGCHLD)  │  │  (安全唤醒)  │  │    (超时处理)        │ │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
│         │                │                     │            │
│         ▼                ▼                     ▼            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              g_main_loop_run(main_loop)              │   │
│  │                    (poll 等待事件)                    │   │
│  └──────────────────────────┬──────────────────────────┘   │
│                             │                               │
│         ┌───────────────────┼───────────────────┐          │
│         ▼                   ▼                   ▼          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │on_signalfd_cb│   │self_pipe_cb │   │ timeout_cb  │     │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘     │
│         │                  │                   │            │
│         ▼                  ▼                   ▼            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            check_child_processes_cb                 │   │
│  │         (waitpid + pid_to_handler 分发)             │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  stdout fd  │  │  stderr fd  │  │  console socket fd  │ │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
│         └─────────────────┼─────────────────────┘          │
│                           ▼                                │
│                    ┌─────────────┐                         │
│                    │  stdio_cb   │                         │
│                    │terminal_accept_cb│                     │
│                    └─────────────┘                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 事件源注册流程

所有事件源在进入主循环前完成注册：

```c
// 1. SIGCHLD 通过 signalfd 处理
int signal_fd = get_signal_descriptor();
g_unix_fd_add(signal_fd, G_IO_IN, on_signalfd_cb, &data);

// 2. self-pipe 安全唤醒
self_pipe_init(self_pipe_cb, &data);

// 3. 控制台 socket 连接（终端模式）
g_unix_fd_add(console_socket_fd, G_IO_IN, terminal_accept_cb, csname);

// 4. stdout/stderr IO
g_unix_fd_add(mainfd_stdout, G_IO_IN, stdio_cb, GINT_TO_POINTER(STDOUT_PIPE));
g_unix_fd_add(mainfd_stderr, G_IO_IN, stdio_cb, GINT_TO_POINTER(STDERR_PIPE));

// 5. 超时
if (opt_timeout > 0) {
    g_timeout_add_seconds(opt_timeout, timeout_cb, NULL);
}

// 6. 空闲时检查已退出的子进程（避免竞态）
g_idle_add(check_child_processes_cb, &data);

// 运行主循环
g_main_loop_run(main_loop);
```

## signalfd：信号处理的现代方式

conmon 不使用传统的 `signal()` 回调处理 SIGCHLD，而是使用 **signalfd** 将信号转换为文件描述符事件：

```c
// 信号阻塞（主循环前）
sigset_t mask, oldmask;
sigemptyset(&mask);
sigaddset(&mask, SIGTERM);
sigaddset(&mask, SIGQUIT);
sigaddset(&mask, SIGINT);
sigaddset(&mask, SIGCHLD);  // SIGCHLD 也加入阻塞掩码
sigprocmask(SIG_BLOCK, &mask, &oldmask);

// 创建 signalfd 并注册到主循环
int signal_fd = get_signal_descriptor();
g_unix_fd_add(signal_fd, G_IO_IN, on_signalfd_cb, &data);
```

### 为什么用 signalfd 而非传统信号处理器？

传统信号处理器（signal handler）有严格的限制：
- 只能调用**异步信号安全函数**（如 `write()`，不能调用 `fprintf()`、`malloc()` 等）
- 与主循环的交互复杂（需要全局标志位，可能有竞态）

signalfd 的优势：
1. **信号变成 IO 事件**：可以像普通 fd 一样在 poll/epoll 中等待
2. **回调中可以做任何事**：在 `on_signalfd_cb` 中可以安全调用 GLib 函数、分配内存、操作哈希表
3. **统一事件模型**：所有事件（信号、IO、超时）都在同一个线程、同一个循环中处理

### on_signalfd_cb 回调

signalfd 可读时触发：

```c
static gboolean on_signalfd_cb(int fd, GIOCondition condition, gpointer user_data)
{
    struct signalfd_siginfo si;
    ssize_t s = read(fd, &si, sizeof(si));
    
    if (si.ssi_signo == SIGCHLD) {
        check_child_processes(user_data);
    } else if (si.ssi_signo == SIGTERM || si.ssi_signo == SIGINT || si.ssi_signo == SIGQUIT) {
        // 处理退出信号
        g_main_loop_quit(main_loop);
    }
    return G_SOURCE_CONTINUE;
}
```

回调读取 `signalfd_siginfo` 结构体，根据信号类型分发处理：
- **SIGCHLD**：调用 `check_child_processes()` 非阻塞收割所有已退出子进程
- **SIGTERM/SIGINT/SIGQUIT**：退出主循环，进入清理流程

## self-pipe：信号安全的唤醒机制

除了 signalfd，conmon 还初始化了**自管道（self-pipe）**：

```c
self_pipe_init(self_pipe_cb, &data);
```

### 为什么需要 self-pipe？

self-pipe 解决一个经典问题：**如何从信号处理器安全唤醒主循环？**

虽然 SIGCHLD 通过 signalfd 处理，但其他场景（如其他线程或信号处理器需要唤醒主循环时）直接调用 `g_main_loop_quit()` 不是异步信号安全的。self-pipe 技巧：

1. 创建一个管道（pipe），读端注册到 GMainLoop
2. 信号处理器中只做一件事：`write(pipefd[1], "x", 1)` 向管道写一个字节
3. 主循环检测到管道可读，触发回调，在回调中安全执行实际逻辑

### self-pipe 在 conmon 中的作用

根据源码注释（[conmon.c#L314-L316](file:///d:/spaces/SpecWeave/external/dao/action/Containers/conmon/src/conmon.c#L314-L316)）：

> Create a self-pipe to safely wake up the main loop from signal handlers. This avoids calling raise() from a signal handler while ppoll() is active, which can trigger glibc's __syscall_cancel and cause SIGABRT (issue #657).

self-pipe 主要用于避免在信号处理器中调用 `raise()` 时，ppoll 系统调用正在执行导致 glibc `__syscall_cancel` 触发 SIGABRT 的 bug。

## check_child_processes：非阻塞子进程收割

SIGCHLD 信号触发后，`check_child_processes()` 使用 `waitpid(-1, &status, WNOHANG)` 循环收割所有已退出的子进程：

```c
// 来自 ctr_exit.c
static void check_child_processes(struct pid_check_data *data)
{
    int status;
    pid_t pid;
    
    while ((pid = waitpid(-1, &status, WNOHANG)) > 0) {
        // 查找对应的回调函数
        void (*cb)(GPid, int, gpointer) = g_hash_table_lookup(data->pid_to_handler, &pid);
        if (cb) {
            cb(pid, status, NULL);
        } else {
            // 未知子进程，缓存退出状态
            g_hash_table_insert(data->exit_status_cache, ...);
        }
    }
}
```

**关键设计点**：
- 使用 `WNOHANG`（非阻塞）：没有已退出子进程时立即返回，不会阻塞主循环
- 使用 `waitpid(-1, ...)` 收割**所有**已退出子进程：SIGCHLD 是边沿触发，一个信号可能对应多个子进程退出，必须循环直到无更多僵尸
- 回调分发：通过 `pid_to_handler` 哈希表查找该 PID 对应的处理函数

## exit_status_cache：竞态防护

conmon 使用 `exit_status_cache` 哈希表处理一种**竞态条件**：

1. 子进程在信号处理器注册完成**之前**就退出了
2. 这种情况下 SIGCHLD 可能丢失或未被处理
3. `g_idle_add(check_child_processes_cb, &data)` 在主循环第一次迭代时检查

如果回调还没注册子进程就退出了，退出状态会被缓存到 `exit_status_cache`，等回调注册后再回放调用：

```c
// 主循环前注册空闲检查
g_idle_add(check_child_processes_cb, &data);
g_main_loop_run(main_loop);

// ... 回调注册完成后，处理缓存的退出状态
if (data.exit_status_cache) {
    GHashTableIter iter;
    gpointer key, value;
    g_hash_table_iter_init(&iter, data.exit_status_cache);
    while (g_hash_table_iter_next(&iter, &key, &value)) {
        pid_t *k = (pid_t *)key;
        int *v = (int *)value;
        void (*cb)(GPid, int, gpointer) = g_hash_table_lookup(pid_to_handler, k);
        if (cb)
            cb(*k, *v, 0);
    }
    g_hash_table_destroy(data.exit_status_cache);
}
```

## 超时处理：timeout_cb

通过 `g_timeout_add_seconds(opt_timeout, timeout_cb, NULL)` 注册超时回调：

```c
// 来自 ctr_exit.c
static gboolean timeout_cb(gpointer user_data)
{
    timed_out = TRUE;
    ninfo("Timed out!");
    g_main_loop_quit(main_loop);
    return G_SOURCE_REMOVE;  // 超时只触发一次
}
```

超时触发时：
1. 设置全局 `timed_out = TRUE` 标志
2. 退出主循环
3. 主循环退出后的清理逻辑会杀死容器进程组

## 主循环退出条件

主循环**不是无限运行**，满足以下任一条件时退出：

```c
if (opt_api_version < 1 || !opt_exec || !opt_terminal || container_status < 0) {
    g_idle_add(check_child_processes_cb, &data);
    g_main_loop_run(main_loop);
}
```

| 条件 | 含义 |
|------|------|
| `opt_api_version < 1` | 使用旧版 API（v0），始终运行循环 |
| `!opt_exec` | create/restore 操作（非 exec），等待容器退出 |
| `!opt_terminal` | exec 但无终端，需要处理所有 IO 输出 |
| `container_status < 0` | exec 带终端，但容器状态尚未设置（快速命令可能已退出） |

退出触发点：
- `container_exit_cb` 中容器退出时调用 `g_main_loop_quit()`
- `timeout_cb` 超时时调用 `g_main_loop_quit()`
- SIGTERM/SIGINT/SIGQUIT 信号触发 `on_sig_exit` 退出

## get_exit_status：退出码计算

容器退出后，`get_exit_status(int status)` 统一计算退出码：

```c
static int get_exit_status(int status)
{
    if (WIFEXITED(status))
        return WEXITSTATUS(status);      // 正常退出：返回退出码
    if (WIFSIGNALED(status))
        return 128 + WTERMSIG(status);  // 信号终止：128 + 信号号
    return -1;
}
```

这是 shell 传统约定（如 bash 中进程被 SIGTERM(15) 杀死，退出码为 128+15=143）。

## 信号处理总结

conmon 中不同信号的处理方式：

| 信号 | 处理方式 | 时机 |
|------|---------|------|
| SIGPIPE | `signal(SIGPIPE, SIG_IGN)` 直接忽略 | main 早期 |
| SIGTERM | 早期：`handle_signal` → exit()（触发 atexit）；fork后：通过 signalfd → `on_sig_exit` → 退出主循环 | 分两个阶段 |
| SIGINT/SIGQUIT | 通过 signalfd → `on_sig_exit` → 退出主循环 | fork 后 |
| SIGCHLD | 通过 signalfd → `on_signalfd_cb` → `check_child_processes()` | fork 后 |

## 为什么用 GLib 而非手写 epoll？

1. **事件源抽象**：`g_unix_fd_add`、`g_timeout_add_seconds`、`g_idle_add` 统一了不同类型事件的注册
2. **哈希表等数据结构**：`GHashTable` 用于 pid_to_handler，无需手写
3. **内存管理**：`_cleanup_` 属性、`g_autoptr` 等 GLib 内存管理工具减少泄漏
4. **日志工具**：`ninfo`/`nwarn`/`ndebug`/`pexit` 等日志宏
5. **跨平台**：GLib 抽象了平台差异（虽然 conmon 主要运行在 Linux）
6. **成熟稳定**：GLib 是 GNOME 项目的基础库，经过数十年生产环境验证

## 相关概念

- [进程生命周期管理](01-process-lifecycle.md) — 双fork、subreaper如何与事件循环配合
- [cgroup与OOM检测](03-cgroup-oom.md) — OOM事件如何通过inotify/eventfd集成到GMainLoop
- [终端附加与日志管理](04-attach-logging.md) — console socket和stdio_cb如何处理容器IO
