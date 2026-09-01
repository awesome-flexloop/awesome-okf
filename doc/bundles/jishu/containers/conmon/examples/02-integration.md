---
type: Example
title: 与 Podman/CRI-O 集成
description: conmon在Podman和CRI-O中的调用方式、参数传递、同步管道通信、attach流程、OOM检测集成的完整说明
tags: [example, integration, podman, crio, cri-o, container-manager, attach, runtime-integration]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
sources:
  - id: conmon-source
    resource: /bundles/containers/conmon/references/conmon-source.md
    title: conmon 主入口信源
  - id: cgroup-source
    resource: /bundles/containers/conmon/references/cgroup-source.md
    title: cgroup 与 OOM 检测信源
---

# 与 Podman/CRI-O 集成

conmon 设计为被容器管理器调用，而非直接由最终用户使用。本示例说明 conmon 如何被 Podman 和 CRI-O 集成，包括调用流程、参数传递、管道通信和状态回传。

## conmon 在容器启动流程中的位置

典型的 `podman run` 执行流程：

```
用户执行: podman run -d alpine sleep 100
    │
    ▼
Podman CLI 进程
    │
    ├─ 拉取镜像（如需要）
    ├─ 创建 OCI bundle（config.json + rootfs）
    ├─ 创建持久化目录、日志路径、PID文件路径
    ├─ 设置 _OCI_STARTPIPE/_OCI_SYNCPIPE 环境变量（管道）
    │
    └─ fork/exec conmon ────────────────────────┐
                                                 │
    ├─ 阻塞读取 _OCI_STARTPIPE                   │
    ├─ [将 conmon 放入正确 cgroup]                │
    ├─ write(_OCI_STARTPIPE) 通知 conmon 继续    │
                                                 ▼
                                            conmon 守护进程（双fork后）
                                                 │
                                                 ├─ setsid + subreaper
                                                 ├─ 创建管道/socket
                                                 ├─ fork/exec runc create
                                                 │
    ├─ 从 _OCI_SYNCPIPE 读取容器 PID ◄───────────┤
    │                                            │
    ├─ Podman CLI 可以退出了                     ├─ runc create 完成后退出
    │  (conmon 在后台监控)                       │
                                                 ├─ 读取 container.pid 获取容器PID
                                                 ├─ 设置 cgroup OOM 监控
                                                 ├─ 注册 stdio/terminal 回调
                                                 └─ 进入 GMainLoop 事件循环
                                                      │
                                                      ▼
                                                 runc start（或直接start）
                                                      │
                                                      ▼
                                                 容器进程运行中
                                                      │
                                         ┌────────────┼────────────┐
                                         │            │            │
                                    用户attach   容器输出→日志   OOM事件→oom文件
                                         │            │            │
                                         ▼            ▼            ▼
                                    attach socket   log文件    persist/oom
```

## Podman 如何调用 conmon

Podman 使用 `pkg/conmon` 包封装对 conmon 的调用。典型的参数构建：

```go
// Podman 中 conmon 命令参数构建（简化伪代码）
args := []string{
    "--api-version", "1",
    "-c", container.ID,
    "-u", container.ID,
    "-b", bundlePath,
    "-p", filepath.Join(persistDir, "container.pid"),
    "-P", filepath.Join(runtimeDir, "conmon.pid"),
    "--exit-dir", exitDir,
    "--persist-dir", persistDir,
    "--log-path", logPath,
    "--runtime", runtimePath,
    "--runtime-arg", "--root",
    "--runtime-arg", runtimeRoot,
    "--log-level", logLevel,
    "-l", container.LogLevel,
}

// 终端模式
if container.Terminal {
    args = append(args, "-t")
}

// 超时设置
if container.Timeout > 0 {
    args = append(args, "-T", strconv.Itoa(container.Timeout))
}

// 设置 socket 路径
args = append(args, "--socket-dir-path", socketDir)

// exec 会话
if isExec {
    args = append(args, "-e")
    args = append(args, "--exec-process-spec", execSpecPath)
}
```

## 管道同步机制

Podman/CRI-O 与 conmon 之间通过三个管道（环境变量传递 fd）进行同步：

| 环境变量 | 方向 | 用途 |
|---------|------|------|
| `_OCI_STARTPIPE` | Podman → conmon | 启动同步：Podman 将 conmon 放入正确 cgroup 后写入，conmon 阻塞等待 |
| `_OCI_SYNCPIPE` | conmon → Podman | 同步回传：conmon 先写容器 PID，退出时写退出码 |
| `_OCI_ATTACHPIPE` | Podman → conmon | Attach 同步：exec with attach 时使用，等待 attach 完成 |

### 启动同步流程

```
Podman                                    conmon
   │                                         │
   ├─ pipe(start_pipe)                       │
   ├─ _OCI_STARTPIPE=<fd> 设置环境变量       │
   ├─ fork/exec conmon ────────────────────→ │
   │                                         ├─ attempt_oom_adjust(-1000)
   │                                         ├─ 双fork守护进程化
   │                                         ├─ get_pipe_fd_from_env("_OCI_STARTPIPE")
   │                                         ├─ read(start_pipe) ← 阻塞等待
   │                                         │
   ├─ 将 conmon 进程放入容器 cgroup           │
   ├─ write(start_pipe, "x", 1) ───────────→ │
   │                                         ├─ read 返回，继续执行
   │                                         ├─ setsid, set_subreaper
   │                                         ├─ fork/exec runc create
```

**为什么需要这个同步点？**

如果 conmon 在 fork 出 runc 之前没有被放入正确的 cgroup，runc 和容器进程可能会在错误的 cgroup 中创建（cgroup v2 中子进程继承父进程 cgroup）。这个同步点确保 Podman 有机会在 conmon 启动容器进程之前将其移入正确的 cgroup。

### 同步管道回传协议

conmon 通过 `_OCI_SYNCPIPE` 向 Podman 回传信息：

```c
// 1. 读取到 container_pid 后，先发送容器 PID
write_or_close_sync_fd(&sync_pipe_fd, container_pid, NULL);

// 2. 容器退出时，发送退出码
if (opt_exec && sync_pipe_fd >= 0)
    write_or_close_sync_fd(&sync_pipe_fd, exit_status, exit_message);
```

`write_or_close_sync_fd` 写入一个整数（PID 或退出码），Podman 端：
1. 先读取容器 PID（整数）
2. 阻塞在读取，直到 conmon 发送退出码
3. 收到退出码后容器生命周期结束

**对于 create 操作**（非 exec）：
- 第一个值：容器 PID（成功时），或 -1（失败时）
- 第二个值：退出码（仅 exec 会话，create 不发送第二个值，Podman 通过 exit 文件获取退出码）

## Exit 文件与 OOM 检测

conmon 退出时将退出状态写入两个位置：

```c
// 持久化目录
g_build_filename(opt_persist_path, "exit", NULL);

// 退出目录（以容器ID命名）
g_build_filename(opt_exit_dir, opt_cid, NULL);
```

### Podman 监控容器退出

Podman 使用 **inotify** 监控 exit 目录：
1. 监控 `opt_exit_dir` 目录的 `IN_CREATE` 事件
2. 当 conmon 创建 `<cid>` 文件时，Podman 知道容器退出
3. 读取文件内容获取退出码
4. 同时检查 persist 目录下是否存在 `oom` 文件判断是否因 OOM 退出

```go
// Podman 中检查 OOM 的逻辑（简化）
func checkOOM(persistDir string) bool {
    oomPath := filepath.Join(persistDir, "oom")
    _, err := os.Stat(oomPath)
    return err == nil
}
```

## Attach 流程：连接到运行中容器

用户执行 `podman attach <container>` 时的流程：

```
podman attach 命令
    │
    ├─ 连接到 conmon 的 attach socket
    │  （路径通常在 /run/conmon/<cid>/attach 或 bundle 目录）
    │
    ├─ 如果是 exec -it，通过 _OCI_ATTACHPIPE 同步
    │  - Podman 准备好终端后写入 attach pipe
    │  - conmon 收到后才允许 exec 继续，避免输出丢失
    │
    ├─ 转发 stdin 到 socket
    ├─ 从 socket 读取输出到本地终端
    └─ 处理 WINCH 信号：通过 ctl FIFO 发送 WIN_RESIZE_EVENT
```

### 窗口大小调整同步

用户调整终端窗口时：
1. Podman 收到 `SIGWINCH` 信号
2. 获取新的终端窗口大小（`TIOCGWINSZ`）
3. 通过 ctl FIFO 发送消息：`1 <height> <width>\n`（WIN_RESIZE_EVENT=1）
4. conmon 的 `process_terminal_ctrl_line()` 解析消息
5. 调用 `resize_winsz(height, width)` → `ioctl(TIOCSWINSZ)` 设置 PTY 窗口大小
6. 内核发送 `SIGWINCH` 到容器内前台进程组

### 日志重开（日志轮转）

外部日志轮转工具重命名日志文件后，需要通知 conmon 重新打开：
1. 通过 ctl FIFO 发送：`2 0 0\n`（REOPEN_LOGS_EVENT=2）
2. conmon 关闭当前日志 fd，重新打开日志路径

## CRI-O 集成要点

CRI-O 作为 Kubernetes 的 CRI 运行时，对 conmon 的使用与 Podman 类似，但有一些差异：

### 日志格式

CRI-O 要求 conmon 使用 Kubernetes CRI 日志格式：
- 每行带时间戳
- 标记流类型（stdout/stderr）
- 标记部分行/完整行（P/F）

conmon 通过 `--log-format-json` 或相关参数配置。

### journald 日志后端

CRI-O 可能配置 conmon 使用 systemd-journald 作为日志后端而非文件：

```bash
conmon --log-driver journald ...
```

日志条目带有容器 ID 等元数据，通过 `journalctl _CONTAINER_ID=<cid>` 查询。

### conmon PID 文件位置

CRI-O 将 conmon pidfile 放在其运行时目录下：
- `/var/run/crio/conmon/<cid>-pid`

### 与 CRI-O 的退出同步

CRI-O 使用 exit 文件（与 Podman 相同），exit 目录通常为：
- `/var/run/crio/exits/`

## 错误处理

conmon 通过以下方式向管理器报告错误：

| 错误场景 | 处理方式 |
|---------|---------|
| CLI 参数错误（如缺少 --cid） | conmon 直接退出，退出码非零 |
| runc create 失败 | stderr 管道读取错误消息，通过 sync_pipe 发送 -1 和错误信息 |
| runtime pidfile 读取失败 | 读取 stderr 错误消息，通过 sync_pipe 发送 -1 |
| 容器超时 | 杀死进程组，exit_message = "command timed out" |
| cgroup OOM | 创建 oom 标记文件，退出码通常为 137（128+9=SIGKILL） |

### runc create 失败场景

```
conmon fork runc create
    │
    └─ runc create 失败（非0退出码）
        │
        ├─ runtime_exit_cb 被触发
        ├─ 读取 mainfd_stderr 上的错误消息
        ├─ 通过 sync_pipe_fd 写入 to_report = -1 和 error_msg
        └─ nexitf("Failed to create container: exit status %d", ...)
```

Podman 收到 -1 后，读取错误消息并显示给用户。

## 实际观察：运行中容器的 conmon

在一个运行 Podman 的系统上，可以观察到 conmon 进程：

```bash
# 列出所有运行中的 conmon 进程
ps aux | grep conmon

# 示例输出：
# root      12345  0.0  0.1 123456  7890 ? Ss  10:00  0:00 conmon -c abc123...

# 查看 conmon 的子进程
pstree -p 12345
# conmon(12345)───sleep(12346)
# (runc 已经退出，容器的 init 进程被 conmon subreaper 收养)

# 查看 conmon 打开的 fd
ls -la /proc/12345/fd/
# 0 → /dev/null
# 1 → /dev/null
# 2 → /dev/null
# 3 → socket:[...]（signalfd）
# 4 → pipe:[...]（self-pipe）
# 5 → /var/lib/containers/.../config/container.pid
# 6 → /var/lib/containers/.../container.log
# ...
```

## 相关概念

- [基本命令行使用](01-basic-usage.md) — 手动调用 conmon 的参数示例
- [进程生命周期管理](../concepts/01-process-lifecycle.md) — 理解双fork和subreaper如何让conmon脱离Podman继续运行
- [cgroup与OOM检测](../concepts/03-cgroup-oom.md) — 理解Podman如何通过oom文件判断OOM
- [终端附加与日志管理](../concepts/04-attach-logging.md) — 理解attach socket和FIFO控制协议
