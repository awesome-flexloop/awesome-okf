---
type: Reference
title: conmon 主入口信源
description: src/conmon.c 主程序源码信源——main函数、双fork守护进程化、GMainLoop事件循环、信号处理、进程管理完整API
tags: [reference, main, conmon.c, event-loop, process, signals, glib]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
sources:
  - id: conmon-main
    title: src/conmon.c
    path: external/dao/action/Containers/conmon/src/conmon.c
---

# conmon 主入口信源

> 信源文件：conmon.c

本文档记录 conmon 主入口 `main()` 函数的完整流程、关键函数调用和数据结构。

---

## 关键宏定义

```c
#define DEFAULT_UMASK 0022
```

默认 umask 值，在 main 函数开头设置。

---

## main() 函数执行流程

### 1. 初始化阶段

```c
int main(int argc, char *argv[])
{
    setlocale(LC_ALL, "");
    umask(DEFAULT_UMASK);
    // ...
    int initialize_ec = initialize_cli(argc, argv);
    if (initialize_ec >= 0) {
        exit(initialize_ec);
    }
    process_cli();
    attempt_oom_adjust(-1000);
    signal(SIGPIPE, SIG_IGN);
    signal(SIGTERM, handle_signal);
```

- `setlocale(LC_ALL, "")`：设置本地化
- `umask(DEFAULT_UMASK)`：设置默认文件权限掩码为 0022
- `initialize_cli()`：解析命令行参数，返回值≥0时直接退出（处理--help/--version等）
- `process_cli()`：处理CLI选项，创建 GMainLoop
- `attempt_oom_adjust(-1000)`：将自身 oom_score_adj 设为 -1000（免疫OOM killer）
- `signal(SIGPIPE, SIG_IGN)`：忽略 SIGPIPE 信号防止意外终止
- `signal(SIGTERM, handle_signal)`：捕获 SIGTERM 信号

### 2. 启动管道处理

```c
    int start_pipe_fd = get_pipe_fd_from_env("_OCI_STARTPIPE");
    if (start_pipe_fd > 0) {
        num_read = read(start_pipe_fd, buf, BUF_SIZE);
        // ...
    }
```

从环境变量 `_OCI_STARTPIPE` 获取启动管道文件描述符，阻塞等待父进程写入，确保父进程可以将 conmon 放入正确的 cgroup。

### 3. 双 fork 守护进程化

```c
    if (!opt_sync) {
        pid_t main_pid = fork();
        if (main_pid < 0) {
            pexit("Failed to fork the create command");
        } else if (main_pid != 0) {
            if (opt_conmon_pid_file) {
                // 写入 pidfile
            }
            _exit(0);
        }
    }
```

非同步模式下执行第一次 fork：父进程写入 conmon pidfile 后立即退出，子进程继续运行。这是双 fork 的第一阶段。

### 4. 子收割者与会话设置

```c
    atexit(reap_children);
    setsid();
    int ret = set_subreaper(true);
```

- `atexit(reap_children)`：注册退出时收割子进程的钩子
- `setsid()`：创建新的会话组，脱离控制终端
- `set_subreaper(true)`：将自身设置为子进程收割者（subreaper），确保孤儿进程能被回收

### 5. 标准流管道设置

```c
    if (opt_terminal) {
        csname = setup_console_socket();
    } else {
        // 创建 stdin/stdout 管道
        if (opt_stdin) {
            pipe2(fds, O_CLOEXEC);
            mainfd_stdin = fds[1];
            workerfd_stdin = fds[0];
        }
        pipe2(fds, O_CLOEXEC);
        mainfd_stdout = fds[0];
        workerfd_stdout = fds[1];
    }
    // stderr 管道始终创建
    pipe2(fds, O_CLOEXEC);
    mainfd_stderr = fds[0];
    workerfd_stderr = fds[1];
```

- 终端模式（`opt_terminal`）：调用 `setup_console_socket()` 创建控制台 socket
- 非终端模式：创建 stdin/stdout 管道对
- stderr 管道始终创建，用于在 tty 创建前捕获 runc 的错误消息

### 6. 运行时参数配置与容器进程 fork

```c
    GPtrArray *runtime_argv = configure_runtime_args(csname);
    // 设置 attach socket 和控制 FIFO
    // ...
    create_pid = fork();
    if (create_pid < 0) {
        pexit("Failed to fork the create command");
    } else if (!create_pid) {
        // 子进程（中间进程）
        set_pdeathsig(SIGKILL);
        // 恢复信号掩码
        // dup2 标准流到 workerfd
        reset_oom_adjust();
        execv(g_ptr_array_index(runtime_argv, 0), (char **)runtime_argv->pdata);
        exit(127);
    }
```

这是第二次 fork：
- 中间子进程设置 `PDEATHSIG`（父进程死亡时收 SIGKILL）
- 调用 `reset_oom_adjust()` 恢复 OOM 分数（不希望 runc 不可杀死）
- `execv` 执行 OCI 运行时（runc/crun）

### 7. 事件循环初始化

```c
    GHashTable *pid_to_handler = g_hash_table_new(g_int_hash, g_int_equal);
    g_hash_table_insert(pid_to_handler, (pid_t *)&create_pid, runtime_exit_cb);

    int signal_fd = get_signal_descriptor();
    g_unix_fd_add(signal_fd, G_IO_IN, on_signalfd_cb, &data);

    self_pipe_init(self_pipe_cb, &data);
```

- `pid_to_handler`：GHashTable 映射 pid 到退出回调函数
- `signalfd`：通过 signalfd 处理 SIGCHLD 信号，使用 `g_unix_fd_add` 注册到 GLib 主循环
- `self_pipe`：自管道机制，安全地从信号处理唤醒主循环（避免 glibc __syscall_cancel 导致的 SIGABRT）

### 8. 等待运行时进程退出（无终端场景）

```c
    } else {
        do
            ret = waitpid(create_pid, &runtime_status, 0);
        while (ret < 0 && errno == EINTR);
        // ...
    }
```

无控制台 socket 场景下，同步等待 create 进程（runc create）退出。

### 9. 容器 PID 获取与 OOM 监控设置

```c
    container_pid = atoi(contents);
    g_hash_table_insert(pid_to_handler, (pid_t *)&container_pid, container_exit_cb);

#ifdef __linux__
    setup_oom_handling(container_pid);
#endif
```

- 从 `opt_container_pid_file` 读取容器 PID
- 将 container_pid 映射到 `container_exit_cb` 回调
- Linux 下调用 `setup_oom_handling()` 设置 OOM 检测

### 10. 标准流 IO 监听与超时

```c
    if (mainfd_stdout >= 0) {
        g_unix_fd_add(mainfd_stdout, G_IO_IN, stdio_cb, GINT_TO_POINTER(STDOUT_PIPE));
    }
    if (mainfd_stderr >= 0) {
        g_unix_fd_add(mainfd_stderr, G_IO_IN, stdio_cb, GINT_TO_POINTER(STDERR_PIPE));
    }
    if (opt_timeout > 0) {
        g_timeout_add_seconds(opt_timeout, timeout_cb, NULL);
    }
```

- 将 stdout/stderr fd 注册到主循环，`stdio_cb` 处理日志写入
- `opt_timeout > 0` 时通过 `g_timeout_add_seconds` 设置超时回调

### 11. 主循环运行

```c
    if (opt_api_version < 1 || !opt_exec || !opt_terminal || container_status < 0) {
        g_idle_add(check_child_processes_cb, &data);
        g_main_loop_run(main_loop);
    }
```

主循环运行条件：
1. 使用旧版 API（api_version < 1）
2. 非 exec 操作（create/restore）
3. exec 但无终端
4. exec 带终端但 container_status 尚未设置

### 12. 主循环退出后处理

```c
#ifdef __linux__
    check_cgroup2_oom();
#endif
    if (!timed_out)
        drain_stdio();
    if (!opt_no_sync_log)
        sync_logs();
```

- `check_cgroup2_oom()`：cgroup v2 下检查是否发生 OOM
- `drain_stdio()`：排空剩余的 stdout/stderr 数据
- `sync_logs()`：同步日志文件

### 13. 超时处理与进程杀死

```c
    if (timed_out && container_pid > 0) {
        pid_t process_group = getpgid(container_pid);
        if (process_group > 1)
            kill(-process_group, SIGKILL);
        else
            kill(container_pid, SIGKILL);
        exit_message = TIMED_OUT_MESSAGE;
    } else {
        exit_status = get_exit_status(container_status);
    }
```

- 超时发生时：杀死整个进程组（`-process_group`）或单个容器进程
- 正常退出：通过 `get_exit_status()` 计算退出码

### 14. 退出状态写入

```c
    if (opt_persist_path) {
        char *ctr_exit_file_path = g_build_filename(opt_persist_path, "exit", NULL);
        g_file_set_contents(ctr_exit_file_path, status_str, -1, &err);
    }
    if (opt_exit_dir) {
        char *exit_file_path = g_build_filename(opt_exit_dir, opt_cid, NULL);
        g_file_set_contents(exit_file_path, status_str, -1, &err);
    }
```

将退出状态码写入两个位置：
1. `opt_persist_path/exit`：容器持久化目录
2. `opt_exit_dir/opt_cid`：退出目录（方便 inotify 监控所有容器退出）

---

## 关键全局变量

| 变量 | 类型 | 说明 |
|------|------|------|
| `runtime_status` | int | create 进程（runc create）的退出状态 |
| `container_status` | int | 容器进程的退出状态 |
| `mainfd_stdin/mainfd_stdout/mainfd_stderr` | int | 主进程侧标准流 fd |
| `container_pid` | volatile sig_atomic_t | 容器进程 PID |
| `create_pid` | volatile sig_atomic_t | create 进程 PID |
| `timed_out` | gboolean | 是否发生超时 |
| `main_loop` | GMainLoop* | GLib 主循环实例 |
| `self_pipe_w` | int | 自管道写端 |

---

## 关键回调函数

| 回调 | 触发时机 | 功能 |
|------|---------|------|
| `runtime_exit_cb` | create_pid 退出时 | 处理 runc create 完成 |
| `container_exit_cb` | container_pid 退出时 | 处理容器退出，设置 container_status 并退出主循环 |
| `on_signalfd_cb` | signalfd 可读时 | 处理 SIGCHLD 信号，调用 check_child_processes |
| `self_pipe_cb` | 自管道可读时 | 安全唤醒主循环 |
| `stdio_cb` | stdout/stderr fd 可读时 | 读取容器输出并写入日志 |
| `timeout_cb` | 超时到期时 | 设置 timed_out=TRUE 并退出主循环 |
| `terminal_accept_cb` | console socket 有连接时 | 接受终端连接，处理控制台附加 |
