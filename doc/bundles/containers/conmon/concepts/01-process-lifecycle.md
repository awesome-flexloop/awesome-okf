---
type: Concept
title: 进程生命周期管理
description: conmon的双fork守护进程化流程、setsid新会话创建、subreaper子进程收割者机制、pid_to_handler回调映射表完整解析
tags: [concept, process, lifecycle, double-fork, daemon, subreaper, setsid, atexit, pid-namespace]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
sources:
  - id: conmon-source
    resource: /bundles/containers/conmon/references/conmon-source.md
    title: conmon 主入口信源
  - id: oom-source
    resource: /bundles/containers/conmon/references/oom-source.md
    title: OOM 分数调整信源
---

# 进程生命周期管理

conmon 的进程生命周期管理是其核心设计之一，采用**双 fork（double-fork）守护进程化** + **subreaper（子进程收割者）** 组合机制，确保容器进程的可靠监控和孤儿进程回收。

## 为什么需要双 fork？

标准的 `daemon()` 调用虽然也能实现守护进程化，但 conmon 选择手动实现双 fork 流程，原因是：

1. 需要精确控制 fork 时机（在 OOM 调整之后、设置 subreaper 之前）
2. 需要在第一次 fork 后的父进程中写入 conmon pidfile
3. 需要处理 `opt_sync` 模式（同步模式不执行双 fork，用于调试）
4. 需要在两次 fork 之间完成 setsid、管道设置等操作

## 双 fork 流程详解

conmon 的进程树演变如下：

```
【阶段1：启动时】
Podman/CRI-O (父进程)
    └─ conmon (初始进程, PID=X)

【阶段2：第一次 fork (opt_sync=false时)】
Podman/CRI-O
    └─ conmon (父进程, PID=X)
    │   ├─ 写入 pidfile (子进程 PID=Y)
    │   └─ _exit(0)  ← 立即退出，让 Podman/CRI-O 可以继续
    │
    └─ conmon (中间子进程, PID=Y)  ← 继续执行后续初始化

【阶段3：第二次 fork (创建容器运行时)】
    conmon (守护进程, PID=Y)
    │   ├─ setsid() 创建新会话
    │   ├─ set_subreaper(true) 设为子收割者
    │   ├─ 设置管道/socket
    │   └─ fork()
    │       │
    │       ├─ [子进程, PID=Z] (create_pid)
    │       │   ├─ set_pdeathsig(SIGKILL)
    │       │   ├─ reset_oom_adjust() 恢复 OOM 分数
    │       │   └─ execv(runc/crun) → OCI 运行时
    │       │       └─ [容器进程 PID=C] (container_pid)
    │       │
    │       └─ [conmon 继续运行, PID=Y]
    │           └─ 进入 GMainLoop 事件循环，监控 Z 和 C
```

### 第一次 fork：脱离父进程

**源码位置**：[conmon-source.md](/bundles/containers/conmon/references/conmon-source.md) 第3节

```c
if (!opt_sync) {
    pid_t main_pid = fork();
    if (main_pid < 0) {
        pexit("Failed to fork the create command");
    } else if (main_pid != 0) {
        // 父进程（原始 conmon 进程）
        if (opt_conmon_pid_file) {
            char content[16];
            snprintf(content, sizeof(content), "%i", main_pid);
            g_file_set_contents(opt_conmon_pid_file, content, strlen(content), &err);
        }
        _exit(0);
    }
}
// 子进程（守护进程）继续执行
```

**关键点**：
- 父进程在 fork 后立即调用 `_exit(0)` 而非 `exit()`：`_exit()` 不执行 atexit 钩子、不刷新 stdio 缓冲区，适合 fork 后的子进程退出
- 父进程负责将**子进程 PID**（而非自身 PID）写入 pidfile，这是守护进程的正确做法
- `opt_sync=true` 模式下跳过双 fork，用于前台调试

### setsid()：创建新会话

第一次 fork 后，子进程调用 `setsid()`：

```c
setsid();
```

`setsid()` 的作用：
1. 创建新的会话（session），进程成为会话首进程（session leader）
2. 创建新的进程组（process group），进程成为进程组首进程
3. **脱离控制终端**：进程不再有控制终端，即使启动它的终端关闭也不会收到 SIGHUP

这是守护进程的标准操作，确保 conmon 不会被终端关闭信号意外终止。

### set_subreaper(true)：子进程收割者

```c
int ret = set_subreaper(true);
if (ret != 0) {
    pexit("Failed to set as subreaper");
}
```

这是 conmon 进程模型中**最关键的设计**。

#### 什么是 subreaper？

Linux 内核中，`prctl(PR_SET_CHILD_SUBREAPER)` 将进程标记为"子收割者"：
- 当进程的子孙进程变成孤儿（父进程退出）时，它们不会被 PID 1（init/systemd）收养，而是被最近的 subreaper 祖先收养
- subreaper 可以通过 `waitpid()` 获取这些孤儿进程的退出状态

#### 为什么需要 subreaper？

容器进程的父进程链是：conmon → runc create → runc init → 容器进程。当 runc create 完成任务退出后，如果没有 subreaper，容器进程会被 PID 1 收养，conmon 将无法通过 waitpid 获取容器退出状态。设置 subreaper 后：

1. runc create 进程（PID=Z）退出 → conmon 通过 `runtime_exit_cb` 收割
2. 容器进程（PID=C）的父进程 runc 退出 → C 被 conmon（subreaper）收养
3. 容器进程退出 → conmon 通过 `container_exit_cb` 收割并记录退出码

### atexit(reap_children)：退出时兜底收割

```c
atexit(reap_children);
```

注册退出钩子，在 conmon 自身退出时（正常或异常）循环调用 `waitpid(-1, NULL, WNOHANG)` 收割所有剩余的僵尸子进程，避免留下僵尸进程。

## 第二次 fork：启动 OCI 运行时

设置好所有环境后，conmon fork 出"中间子进程"来 exec runc/crun：

```c
create_pid = fork();
if (create_pid < 0) {
    pexit("Failed to fork the create command");
} else if (!create_pid) {
    // ===== 子进程（中间进程）=====
    set_pdeathsig(SIGKILL);  // 父进程死亡时自动收 SIGKILL
    
    // 恢复信号掩码
    // dup2 标准流到 workerfd
    // 处理 LISTEN_PID 环境变量
    
    reset_oom_adjust();  // 关键：恢复 OOM 分数，不继承免疫
    execv(g_ptr_array_index(runtime_argv, 0), (char **)runtime_argv->pdata);
    exit(127);  // exec 失败才会到这里
}
// ===== conmon 父进程继续 =====
```

### set_pdeathsig(SIGKILL)：父死子随

```c
if (set_pdeathsig(SIGKILL) < 0)
    _pexit("Failed to set PDEATHSIG");
```

`prctl(PR_SET_PDEATHSIG, SIGKILL)` 设置：如果父进程（conmon）意外死亡，内核会向这个子进程发送 SIGKILL。这是一个安全机制：
- 如果 conmon 崩溃，runc/create 子进程不会变成孤儿继续运行
- 避免容器在没有监控的情况下"悬空"运行

> **注意**：`set_pdeathsig` 只在 fork 后的子进程中设置，并且在 Linux 上，这是 per-process 属性，不会被 exec 后的进程继承？不——实际上，`PDEATHSIG` 会在 exec 后保留，因此 runc 和容器进程也会在 conmon 死亡时被杀死。

### reset_oom_adjust()：不继承 OOM 免疫

在 execv 之前调用 `reset_oom_adjust()` 将 oom_score_adj 恢复为正常值（通常是 0）：
- conmon 自身设为 -1000（完全免疫 OOM）是为了确保监控者存活
- 但容器进程**必须**可以被 OOM killer 杀死，这是内存资源管理的基本要求
- 如果不 reset，容器内所有进程都会继承 -1000，内存压力下系统会杀死其他重要进程而非容器，导致系统不稳定

## pid_to_handler：PID 到回调的映射表

conmon 使用 GLib 的 `GHashTable` 维护 PID 到退出处理回调的映射：

```c
GHashTable *pid_to_handler = g_hash_table_new(g_int_hash, g_int_equal);
```

**注册的回调**：

| PID | 回调函数 | 触发时机 |
|-----|---------|---------|
| `create_pid`（runc进程） | `runtime_exit_cb` | runc create/exec 命令完成时 |
| `container_pid`（容器进程） | `container_exit_cb` | 容器内主进程退出时 |

### 为什么需要这个映射？

因为 conmon 通过 signalfd 统一接收 SIGCHLD 信号，一个 SIGCHLD 可能对应多个子进程退出。`on_signalfd_cb` 调用 `check_child_processes()` 时：
1. 使用 `waitpid(-1, &status, WNOHANG)` 非阻塞遍历所有已退出子进程
2. 对每个退出的 PID，在 `pid_to_handler` 中查找对应的回调
3. 调用回调处理退出状态（runc 完成 vs 容器退出）

这种设计实现了**关注点分离**：信号处理只负责发现子进程退出，具体的退出处理逻辑由注册的回调决定。

## 容器退出后的清理流程

主循环退出后，conmon 执行清理：

1. **cgroup v2 OOM 最终检查**：`check_cgroup2_oom()` 解析 memory.events 确认是否有遗漏的 OOM 事件
2. **排空标准流**：`drain_stdio()` 读取并写入所有剩余的 stdout/stderr 数据
3. **同步日志**：`sync_logs()` 确保日志数据落盘
4. **超时处理**：如 `timed_out` 为真，`kill(-process_group, SIGKILL)` 杀死整个进程组
5. **写入退出文件**：将退出码写入 `opt_persist_path/exit` 和 `opt_exit_dir/<cid>`
6. **清理资源**：移除 signalfd、关闭 self-pipe、关闭其他 fd、删除 attach socket 符号链接
7. **返回退出码**：conmon 自身以容器的退出码退出

## 进程模型关键特性总结

| 机制 | 作用 | 相关事实 |
|------|------|---------|
| 双 fork | 脱离启动父进程，实现守护进程化 | F-008 |
| setsid() | 创建新会话，脱离控制终端 | F-010 |
| set_subreaper(true) | 收养孤儿孙进程，能 waitpid 容器 | F-011 |
| atexit(reap_children) | 退出时兜底收割所有僵尸进程 | F-009 |
| set_pdeathsig(SIGKILL) | conmon 死亡时自动杀死子进程 | F-016 |
| pid_to_handler 哈希表 | 将 PID 映射到对应的退出回调 | F-018, F-019 |
| attempt_oom_adjust(-1000) | conmon 自身免疫 OOM | F-005 |
| reset_oom_adjust() | 容器 exec 前恢复正常 OOM 优先级 | F-017 |

## 相关概念

- [事件循环与信号处理](02-event-loop.md) — GMainLoop如何驱动SIGCHLD处理、IO事件和超时
- [cgroup与OOM检测](03-cgroup-oom.md) — cgroup v1/v2的OOM事件检测机制
- [conmon定位与架构概览](00-introduction.md) — conmon在容器栈中的位置
