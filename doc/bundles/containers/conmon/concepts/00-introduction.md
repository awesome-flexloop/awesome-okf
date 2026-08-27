---
type: Concept
title: conmon 定位与架构概览
description: conmon 作为 OCI 容器运行时监控器的定位、核心职责、在容器栈中的位置，以及整体架构设计概览
tags: [concept, introduction, overview, conmon, oci, architecture, container-runtime]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
sources:
  - id: readme-source
    resource: /bundles/containers/conmon/references/readme-source.md
    title: README 项目说明信源
  - id: conmon-source
    resource: /bundles/containers/conmon/references/conmon-source.md
    title: conmon 主入口信源
---

# conmon 定位与架构概览

## conmon 是什么

conmon（container monitor）是一个 **OCI（Open Container Initiative）容器运行时监控器**，使用 C 语言编写，设计目标是极低内存占用。它在容器管理生态中扮演"容器守护进程"的角色，每个运行的容器都对应一个 conmon 实例。

conmon 的官方定位是容器管理器（如 Podman、CRI-O）与底层 OCI 运行时（如 runc、crun）之间的**监控程序和通信工具**。

```
┌─────────────────────────────────────────────────────────────┐
│                     容器管理栈分层                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐                                           │
│  │  Podman/CRI-O│  ← 容器管理器（前端/编排层）               │
│  └──────┬───────┘                                           │
│         │ fork/exec + 管道通信                              │
│         ▼                                                   │
│  ┌──────────────┐                                           │
│  │    conmon    │  ← 容器监控器（本项目）                    │
│  └──────┬───────┘                                           │
│         │ fork/exec runc/crun                               │
│         ▼                                                   │
│  ┌──────────────┐     ┌──────────────┐                      │
│  │runc/crun(OCI)│────→│ 容器进程(PID) │  ← 实际用户容器      │
│  └──────────────┘     └──────────────┘                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 在容器生态中的位置

conmon 是 Podman/CRI-O 等容器管理器的**核心依赖组件**，解决了一个关键问题：容器管理器（如 Podman CLI）是短生命周期的前台进程，而容器可能长时间运行——conmon 作为长生命周期守护进程，在容器管理器退出后继续监控容器。

### 为什么需要 conmon？

直接调用 runc 启动容器存在以下问题：

1. **进程脱离问题**：runc create/start 后，runc 进程退出，容器进程变成孤儿，没有直接父进程监控
2. **日志持久化问题**：容器 stdout/stderr 输出需要被记录到文件，不能随父进程退出而丢失
3. **终端附加问题**：需要一个稳定的套接字端点，支持后续 `podman attach` 附加到运行中容器
4. **退出状态回收**：容器退出后的退出码需要被可靠地记录和传递
5. **OOM 检测**：需要检测容器是否因内存不足（OOM）被内核杀死

conmon 就是为解决这些问题而存在的"最小守护进程"——它不做容器创建、不做镜像管理、不做网络配置，只专注于**单个容器的生命周期监控**。

## 核心职责

根据 [README 信源](../references/readme-source.md) 和源码实现，conmon 在容器运行期间承担以下职责：

### 1. 守护进程化与进程隔离

启动时执行双 fork（double-fork）脱离父进程和控制终端，调用 `setsid()` 创建新会话，将自身设置为子进程收割者（subreaper），确保容器进程成为孤儿时仍能被正确回收。

详见 [进程生命周期管理](01-process-lifecycle.md)。

### 2. OOM 自我保护

启动后立即将自身 `oom_score_adj` 设置为 -1000（OOM killer 完全免疫），确保 conmon 比容器进程更晚被杀死；在 exec 容器进程前恢复为正常值，不影响容器内进程的 OOM 优先级。

详见 [cgroup 与 OOM 检测](03-cgroup-oom.md)。

### 3. 事件驱动主循环

使用 GLib 的 GMainLoop 作为事件循环，通过 signalfd 处理 SIGCHLD、self-pipe 安全唤醒机制、inotify/eventfd 监听 OOM 事件、g_timeout_add 处理超时、GHashTable 映射 pid 到退出回调。

详见 [事件循环与信号处理](02-event-loop.md)。

### 4. 终端附加（Attach）

提供 Unix socket 端点，保持容器标准流（stdin/stdout/stderr）打开，支持运行时通过 socket 附加到容器终端，实现交互式 shell 等功能。

### 5. 日志记录

将容器 stdout/stderr 流写入日志文件（或 systemd journal），支持日志轮转和大小限制，确保容器输出在容器终止后仍可被读取。

详见 [终端附加与日志管理](04-attach-logging.md)。

### 6. cgroup OOM 检测

支持 cgroup v1 和 v2 双版本的 OOM 检测：v1 使用 eventfd 监听 `memory.oom_control`，v2 使用 inotify 监控 `memory.events` 文件并解析计数器变化。

详见 [cgroup 与 OOM 检测](03-cgroup-oom.md)。

### 7. 退出状态记录

容器退出后，将退出状态码写入持久化目录的 `exit` 文件和退出目录的容器 ID 文件，供上层管理程序读取。若检测到 OOM，创建 `oom` 标记文件。

## 架构概览

conmon 是单进程事件驱动架构，代码按功能模块划分为多个 C 文件：

```
conmon 单进程
├── 主入口 (conmon.c)
│   ├── CLI 解析
│   ├── 双 fork 守护进程化
│   ├── setsid + subreaper 设置
│   ├── 标准流管道/控制台 socket 设置
│   ├── fork 容器进程
│   └── GMainLoop 事件循环运行
├── 命令行解析 (cli.c/cli.h)
│   └── GOptionEntry 选项定义
├── 进程退出处理 (ctr_exit.c/ctr_exit.h)
│   ├── pid_to_handler 哈希表
│   ├── SIGCHLD 信号处理
│   ├── waitpid 非阻塞收割
│   └── 超时回调
├── cgroup 与 OOM 检测 (cgroup.c/cgroup.h)
│   ├── cgroup v1: eventfd + cgroup.event_control
│   ├── cgroup v2: inotify + memory.events 解析
│   └── oom 标记文件创建
├── OOM 分数调整 (oom.c/oom.h)
│   ├── attempt_oom_adjust(-1000): 自我保护
│   └── reset_oom_adjust(): 容器 exec 前恢复
├── 终端控制 (ctrl.c/ctrl.h)
│   ├── console socket 接受连接
│   ├── FIFO 控制协议（ctl/winsz）
│   ├── WIN_RESIZE_EVENT 窗口大小调整
│   └── REOPEN_LOGS_EVENT 日志重开
├── 标准流处理 (ctr_stdio.c/ctr_stdio.h)
│   └── stdio_cb: 读取容器输出写入日志
├── 日志管理 (ctr_logging.c/ctr_logging.h)
│   ├── 文件日志后端
│   ├── journald 后端
│   └── 日志轮转
├── 附加 socket (conn_sock.c/conn_sock.h)
│   └── attach socket 设置
├── 自管道 (self_pipe.c/self_pipe.h)
│   └── 信号安全的主循环唤醒
└── 工具函数 (utils.c/utils.h, globals.c/globals.h, ...)
```

## 设计哲学

conmon 的设计体现了典型的 Unix 哲学：

1. **做一件事并做好**：只做容器监控，不做镜像管理、网络、存储
2. **低内存占用**：C 语言编写，事件驱动而非多线程，每个容器一个实例内存开销极小
3. **机制而非策略**：提供稳定的监控和 I/O 转发机制，策略交给上层 Podman/CRI-O
4. **可靠性优先**：OOM 自我保护、subreaper 孤儿回收、信号安全处理，确保监控进程不丢失
5. **无状态设计**：状态通过文件系统传递（pidfile、exit 文件、oom 文件、日志文件），崩溃后可通过文件恢复信息

## 与 conmon-rs 的关系

conmon-rs 是 conmon 的 Rust 重写版本，由 same 团队开发，定位演进为 **Pod 级监控器**——一个 conmon-rs 实例可以管理 Pod 内的多个容器，而非 conmon 那样"一容器一实例"。conmon-rs 还采用 Rust 服务器 + Golang 客户端的双语言架构，提供 Cap'n Proto RPC 接口。本教程专注于 C 版本的 conmon。

## 相关概念

- [进程生命周期管理](01-process-lifecycle.md) — 双fork守护进程化、subreaper机制、pid_to_handler回调映射
- [事件循环与信号处理](02-event-loop.md) — GMainLoop架构、signalfd、self-pipe、超时处理
- [cgroup与OOM检测](03-cgroup-oom.md) — cgroup v1/v2双版本OOM检测实现对比
- [终端附加与日志管理](04-attach-logging.md) — console socket、FIFO控制协议、日志写入
