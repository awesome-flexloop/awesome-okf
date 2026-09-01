---
type: Concept
title: 终端附加与日志管理
description: conmon的console socket终端附加机制、FIFO控制协议（窗口大小调整/日志重开）、stdio_cb日志写入、日志后端完整解析
tags: [concept, attach, terminal, console, logging, fifo, winsz, ioctl, journald]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
sources:
  - id: conmon-source
    resource: /bundles/containers/conmon/references/conmon-source.md
    title: conmon 主入口信源
---

# 终端附加与日志管理

终端附加（attach）和日志管理是 conmon 除进程监控外最重要的功能。conmon 保持容器标准流打开，提供 socket 端点供运行时附加，同时将容器输出持久化到日志文件。

## 终端模式 vs 非终端模式

conmon 支持两种 IO 模式，由 `--terminal/-t` 参数控制：

| 特性 | 终端模式（-t） | 非终端模式 |
|------|----------------|-----------|
| stdio 机制 | console socket（PTY） | 管道（pipe） |
| stdin | 通过控制台 socket 转发 | 通过 stdin 管道转发 |
| stdout/stderr | PTY 合并输出 | 独立管道 |
| 窗口大小调整 | 支持（TIOCSWINSZ ioctl） | 不支持 |
| 使用场景 | 交互式 shell（bash/sh） | 非交互式服务进程 |

### 终端模式：console socket

```c
if (opt_terminal) {
    csname = setup_console_socket();
}
```

`setup_console_socket()` 创建一个 Unix socket，容器运行时（runc）通过 `SCM_RIGHTS` 消息将 PTY 主端 fd 发送给 conmon。

### 非终端模式：管道对

```c
} else {
    if (opt_stdin) {
        pipe2(fds, O_CLOEXEC);
        mainfd_stdin = fds[1];   // conmon 写端
        workerfd_stdin = fds[0]; // 容器读端
    }
    pipe2(fds, O_CLOEXEC);
    mainfd_stdout = fds[0];  // conmon 读端
    workerfd_stdout = fds[1]; // 容器写端
}
// stderr 始终创建管道
pipe2(fds, O_CLOEXEC);
mainfd_stderr = fds[0];
workerfd_stderr = fds[1];
```

> **关键设计**：stderr 管道**始终创建**，即使在终端模式下也是如此。这是为了在 PTY 创建之前捕获 runc 的错误消息——如果 runc 在设置 PTY 之前失败，错误信息通过 stderr 管道传递。

## console socket：终端接受流程

控制台 socket 有新连接时，触发 `terminal_accept_cb` 回调：

```c
static gboolean terminal_accept_cb(int fd, GIOCondition condition, gpointer user_data)
{
    // 1. 接受连接
    int connfd = accept4(fd, NULL, NULL, SOCK_CLOEXEC);
    
    // 2. 通过 SCM_RIGHTS 接收 PTY 文件描述符
    console.fd = recvfd(connfd);
    
    // 3. 设置终端属性
    tset.c_oflag |= ONLCR;  // 输出时将 NL 转换为 CRNL
    tcsetattr(console.fd, TCSAFLUSH, &tset);
    
    // 4. 设置 mainfd_stdout 为 console.fd 的 dup
    mainfd_stdin = console.fd;
    mainfd_stdout = dup(console.fd);
    
    // ...
}
```

**关键点**：
- 使用 `accept4`（带 `SOCK_CLOEXEC`）而非 `accept`，避免 fd 泄漏到子进程
- 通过 `recvfd` 辅助函数接收 SCM_RIGHTS 消息传递的 PTY fd
- 设置 `ONLCR` 终端标志确保换行正确处理
- stdin 和 stdout 共享同一个 PTY fd（stdout 是 dup 出来的）

## FIFO 控制协议

除了 console socket，conmon 还创建两个 **FIFO（命名管道）** 用于运行时控制：

```c
dummyfd = setup_terminal_control_fifo();  // "ctl" FIFO
setup_console_fifo();                      // "winsz" FIFO
```

| FIFO 名称 | 用途 |
|----------|------|
| `ctl` | 控制消息（窗口大小调整、日志重开） |
| `winsz` | 窗口大小信息传递 |

### setup_fifo 通用创建函数

```c
static int setup_fifo(const char *path, mode_t mode)
{
    unlink(path);  // 已存在则先删除
    return mkfifo(path, 0660);
}
```

### 控制消息格式

`process_terminal_ctrl_line()` 解析 ctl FIFO 中的控制消息：

```c
static void process_terminal_ctrl_line(char *line)
{
    int height, width, ret;
    // 格式: "%d %d %d\n"
    ret = sscanf(line, "%d %d %d\n", &command, &height, &width);
    
    switch (command) {
    case WIN_RESIZE_EVENT:  // 1
        resize_winsz(height, width);
        break;
    case REOPEN_LOGS_EVENT: // 2
        // 重新打开日志文件（日志轮转后使用）
        break;
    }
}
```

**协议格式**（简单文本行）：
```
<command> <param1> <param2>\n
```

**消息类型**（定义在 config.h）：

```c
#define WIN_RESIZE_EVENT    1
#define REOPEN_LOGS_EVENT   2
```

### 窗口大小调整：resize_winsz()

当用户调整终端窗口大小时，上层（Podman/CRI-O）通过 ctl FIFO 发送 `WIN_RESIZE_EVENT` 消息，conmon 调用 `resize_winsz()`：

```c
static void resize_winsz(unsigned short height, unsigned short width)
{
    struct winsize ws;
    ws.ws_row = height;
    ws.ws_col = width;
    ws.ws_xpixel = 0;
    ws.ws_ypixel = 0;
    
    ioctl(mainfd_stdout, TIOCSWINSZ, &ws);
}
```

- 使用 `ioctl TIOCSWINSZ` 设置 PTY 的窗口大小
- 内核会向前台进程组发送 `SIGWINCH` 信号，应用（如 vim、top）读取新窗口大小重绘界面

## attach socket：运行时附加

除了初始的 console socket，conmon 还创建一个 **attach socket** 用于运行时 `podman attach`：

```c
if (opt_bundle_path != NULL && !logging_is_passthrough()) {
    attach_symlink_dir_path = setup_attach_socket();
    // ...
}
```

attach socket 允许在容器启动后，用户执行 `podman attach <container>` 时连接到容器的 stdin/stdout/stderr。这个 socket 的路径通常在 bundle 目录下，并创建符号链接到固定位置方便查找。

## stdio_cb：容器输出处理

容器的 stdout 和 stderr fd 通过 `g_unix_fd_add` 注册到主循环，有数据可读时触发 `stdio_cb`：

```c
if (mainfd_stdout >= 0) {
    g_unix_fd_add(mainfd_stdout, G_IO_IN, stdio_cb, GINT_TO_POINTER(STDOUT_PIPE));
}
if (mainfd_stderr >= 0) {
    g_unix_fd_add(mainfd_stderr, G_IO_IN, stdio_cb, GINT_TO_POINTER(STDERR_PIPE));
}
```

`stdio_cb` 的职责：
1. 从 fd 读取可用数据（使用 `BUF_SIZE` 缓冲区）
2. 如果是终端模式：通过 attach socket 转发给已连接的客户端
3. 写入日志文件（或 journald）
4. 如果是 stderr：可能也转发到特定位置
5. 返回 `G_SOURCE_CONTINUE` 继续监听，或在 fd 关闭时返回 `G_SOURCE_REMOVE`

## 日志管理

conmon 支持多种日志后端，将容器的 stdout/stderr 流持久化存储：

### 日志后端类型

| 后端 | 说明 |
|------|------|
| **文件日志**（默认） | 写入指定路径的日志文件，支持轮转 |
| **journald** | 写入 systemd journal，使用 `sd_journal_sendv` |
| **passthrough** | 直接透传给 conmon 的 stdout/stderr（用于前台调试） |

### 日志大小限制与轮转

通过 CLI 参数控制日志行为：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--log-size-max` | -1（无限制） | 单个日志文件最大大小（字节） |
| `--log-max-files` | 1 | 日志轮转保留的最大文件数 |

当当前日志文件大小超过 `--log-size-max` 时：
1. 关闭当前日志文件
2. 重命名（轮转）旧日志文件（如 `log.1`、`log.2`）
3. 删除超过 `--log-max-files` 的旧日志
4. 创建新的日志文件继续写入
5. 通过 ctl FIFO 发送 `REOPEN_LOGS_EVENT` 通知相关方

日志轮转后需要重新打开日志文件，这是 `REOPEN_LOGS_EVENT` 的用途。

### 日志格式

conmon 支持两种日志格式：

1. **Kubernetes CRI 日志格式**（默认）：每行带有时间戳和流类型标签
   ```
   2024-01-01T00:00:00.000000000Z stdout P <partial-line>
   2024-01-01T00:00:00.000000000Z stdout F <full-line>
   2024-01-01T00:00:00.000000000Z stderr F <error-line>
   ```
   - `P` = partial（行未结束，后续还有）
   - `F` = full（完整行）

2. **原始格式**：直接写入原始字节流，不添加额外元数据

### passthrough 模式

`--log-driver=passthrough` 模式下：
- conmon 不创建日志文件
- 不 disconnect 标准流（跳过 `disconnect_std_streams`）
- 容器输出直接到 conmon 的 stdout/stderr
- 主要用于 `podman run --attach` 前台运行场景

## 同步管道与启动同步

conmon 使用多个管道与父进程（Podman/CRI-O）同步：

| 环境变量 | 管道用途 |
|---------|---------|
| `_OCI_STARTPIPE` | 启动同步管道：conmon 在 fork 子进程前阻塞读取，等待父进程将其放入正确 cgroup 后写入 |
| `_OCI_SYNCPIPE` | 同步管道：conmon 将容器 PID 和退出码写回给父进程 |
| `_OCI_ATTACHPIPE` | attach 同步管道：exec with attach 时使用，等待 attach 完成再 exec |

### 启动同步流程

```
Podman/CRI-O                              conmon
    │                                       │
    ├─ 设置 _OCI_STARTPIPE 环境变量         │
    ├─ fork/exec conmon ──────────────────→ │
    │                                       ├─ 读取 _OCI_STARTPIPE fd
    │                                       ├─ [双fork、setsid、subreaper等]
    │                                       ├─ read(start_pipe) ← 阻塞等待
    │                                       │
    ├─ 将 conmon 放入正确 cgroup            │
    ├─ write(start_pipe, "x", 1) ─────────→ │
    │                                       ├─ read 返回，继续执行
    │                                       ├─ fork 容器进程
    │                                       ├─ ...
```

这确保 conmon 自身在被放入正确 cgroup 后才启动容器，避免容器进程在错误 cgroup 中创建。

## 退出后的 IO 处理

主循环退出后，conmon 处理剩余 IO：

```c
// 1. cgroup v2 最终 OOM 检查
check_cgroup2_oom();

// 2. 如果不是超时，排空剩余 stdio
if (!timed_out)
    drain_stdio();

// 3. 同步日志到磁盘
if (!opt_no_sync_log)
    sync_logs();
```

- `drain_stdio()`：继续读取 stdout/stderr 直到 EAGAIN，确保所有容器输出都被写入日志
- `sync_logs()`：调用 `fsync` 确保日志数据落盘，防止数据丢失

## 标准流与终端相关的关键全局变量

| 变量 | 类型 | 说明 |
|------|------|------|
| `mainfd_stdin` | int | conmon 侧 stdin（写端，向容器输入） |
| `mainfd_stdout` | int | conmon 侧 stdout（读端，读容器输出） |
| `mainfd_stderr` | int | conmon 侧 stderr（读端） |
| `console_socket_fd` | int | 控制台 socket fd（接收 PTY） |
| `attach_socket_fd` | int | 运行时 attach socket fd |
| `terminal_ctrl_fd` | int | ctl FIFO fd（控制消息） |
| `winsz_fd_r/winsz_fd_w` | int | winsz FIFO 读写端 |
| `attach_pipe_fd` | int | attach 同步管道 |

## 相关概念

- [进程生命周期管理](01-process-lifecycle.md) — 双fork后标准流如何dup到容器进程
- [事件循环与信号处理](02-event-loop.md) — stdio_cb和terminal_accept_cb如何集成到GMainLoop
- [conmon定位与架构概览](00-introduction.md) — 终端附加和日志是conmon的两大核心职责
