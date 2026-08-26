---
type: Example
title: 从 C 版本迁移
description: 从传统 C 版本 conmon 迁移到 conmon-rs 的指南，包括架构差异、API 变化、配置变更和注意事项
tags: [conmon-rs, example, migration, conmon, c-version, upgrade]
sources:
  - id: readme-source
    resource: /bundles/containers/conmon-rs/references/readme-source.md
    title: README 项目说明信源
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
---

# 从 C 版本迁移

本文档面向容器引擎开发者（CRI-O、Podman 或其他使用 conmon 的项目），讲解如何从传统的 C 版本 conmon 迁移到 conmon-rs，包括架构差异、API 变化和迁移步骤。

> **前置阅读**：建议先阅读 [Pod级监控架构与C版本差异](../concepts/00-introduction.md) 理解核心设计差异，再阅读本文。

## 核心认知转变

在开始迁移之前，必须理解几个根本性的思维转变：

| 传统 conmon (C) | conmon-rs (Rust) | 思维转变 |
|-----------------|------------------|---------|
| "一容器一 conmon" | "一 Pod 一 conmon-rs" | 从"管理单个容器"到"管理整个 Pod" |
| 每个 exec 创建新 conmon 实例 | exec 复用现有实例 | 不需要为 exec 额外 fork 监控进程 |
| 通过命令行参数 + 信号 + FIFO 通信 | 通过 Go 客户端 API + Cap'n Proto RPC | 从"进程+信号"模型到"RPC 客户端"模型 |
| 自己管理 conmon 进程生命周期 | Go 客户端库自动管理 | 不需要手动 fork/wait conmonrs |
| 日志主要写文件 | 三种内置日志后端可选 | 根据场景选择 journald/CRI/JSON |

## 架构对比：进程模型变化

### 传统 conmon 的进程树

```
容器引擎 (CRI-O/Podman)
├── conmon (容器 A) ──→ 容器 A 进程
├── conmon (容器 B) ──→ 容器 B 进程
├── conmon (容器 A exec) ──→ exec 进程 1
└── conmon (容器 A exec) ──→ exec 进程 2

4 个容器/exec = 4 个 conmon 进程
```

### conmon-rs 的进程树

```
容器引擎 (CRI-O/Podman)
└── conmonrs (整个 Pod 的监控)
    ├── 容器 A 进程
    ├── 容器 B 进程
    ├── exec 进程 1 (容器 A)
    └── exec 进程 2 (容器 B)

N 个容器/exec = 1 个 conmonrs 进程
```

## 迁移步骤概览

```
步骤 1: 获取 conmonrs 二进制
    │
    ▼
步骤 2: 集成 Go 客户端库
    │
    ▼
步骤 3: 改造 Pod 生命周期管理
    │
    ▼
步骤 4: 改造容器创建/启动流程 (从 conmon CLI → RPC API)
    │
    ▼
步骤 5: 改造 exec 流程 (去掉额外 conmon fork)
    │
    ▼
步骤 6: 改造日志配置 (选择日志后端)
    │
    ▼
步骤 7: 改造终端附加 (attach)
    │
    ▼
步骤 8: 测试与验证
```

---

## 步骤 1：获取 conmonrs 二进制

conmon-rs 提供静态链接二进制，无需从源码编译即可使用。

### 方式 A：使用 get 脚本（推荐用于测试）

```bash
# 下载最新版本到当前目录
curl https://raw.githubusercontent.com/containers/conmon-rs/main/scripts/get | bash

# 下载到系统路径
curl https://raw.githubusercontent.com/containers/conmon-rs/main/scripts/get | \
    bash -s -- -o /usr/local/bin/conmonrs

# 验证（如果有 cosign 会自动验证签名）
chmod +x /usr/local/bin/conmonrs
conmonrs --help
```

### 方式 B：从源码编译

```bash
# 安装 Rust 工具链
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 克隆源码
git clone https://github.com/containers/conmon-rs.git
cd conmon-rs

# Release 构建（带全部优化）
cargo build --release

# 二进制位置：target/release/conmonrs
sudo cp target/release/conmonrs /usr/local/bin/
```

### 方式 C：包管理器

Fedora/RHEL COPR：
```bash
dnf copr enable rhcontainerbot/podman-next
dnf install conmon-rs
```

---

## 步骤 2：集成 Go 客户端库

在你的 Go 项目中添加 conmon-rs 依赖：

```bash
go get github.com/containers/conmon-rs@latest
```

### 传统方式：手动 fork/exec conmon

```go
// 传统 conmon 方式：手动构造命令行参数
cmd := exec.Command(
    "/usr/bin/conmon",
    "--cid", containerID,
    "--cups", "/usr/bin/runc",
    "-b", bundlePath,
    "-c", cgroupPath,
    "-l", logPath,
    "--socket-fd-attach", strconv.Itoa(attachSocketFd),
    // ... 数十个命令行参数
)
cmd.ExtraFiles = []*os.File{attachSocket, ...}
err := cmd.Start()
if err != nil {
    return err
}
// 手动保存 conmon PID，手动 wait，手动处理信号...
conmonPid := cmd.Process.Pid
```

### conmon-rs 方式：使用 ConmonClient

```go
import (
    "github.com/containers/conmon-rs/pkg/client"
)

// 创建客户端配置
cfg := &client.ConmonClientConfig{
    ConmonrsPath: "/usr/local/bin/conmonrs",
    SocketPath:   filepath.Join(runDir, "conmon-rs.sock"),
    LogLevel:     "info",
    LogDriver:    "cri", // 或 "journald", "json"
    // ... 其他配置
}

// 创建客户端 - 内部自动启动 conmonrs 进程、建立连接
c, err := client.NewConmonClient(ctx, cfg)
if err != nil {
    return fmt.Errorf("failed to create conmon client: %w", err)
}
// 客户端会在垃圾回收或显式 Shutdown 时清理服务器进程
defer c.Shutdown()
```

**关键变化**：
- 不需要手动构造数十个命令行参数
- 不需要手动管理 conmon 进程的 PID 和生命周期
- 客户端库自动处理连接、重试、清理

---

## 步骤 3：改造 Pod 生命周期管理

这是迁移中最重要的架构变化——**conmon-rs 实例的生命周期绑定到 Pod，而不是单个容器**。

### 传统 conmon：每个容器创建时启动 conmon

```go
// 伪代码：传统方式
func createContainer(containerID string) error {
    // 每个容器都创建一个 conmon 实例
    cmd := exec.Command("conmon", ...)
    return cmd.Start()
}

func stopPod(podID string) {
    // 需要逐个找到并杀死所有容器的 conmon 进程
    for _, container := range pod.Containers {
        killConmon(container.ConmonPid)
    }
}
```

### conmon-rs：Pod 创建时启动单个客户端

```go
// 伪代码：conmon-rs 方式
func createPodSandbox(podConfig *PodConfig) (*PodSandbox, error) {
    // 为整个 Pod 创建一个 ConmonClient 实例
    cfg := &client.ConmonClientConfig{
        SocketPath: podSocketPath(podConfig.ID),
        // Pod 级别配置
    }
    c, err := client.NewConmonClient(ctx, cfg)
    if err != nil {
        return nil, err
    }

    // 1. 先创建 pause 容器（沙箱容器）
    pauseCfg := &client.CreateContainerConfig{
        ID:     podConfig.PauseContainerID,
        Bundle: pauseBundlePath,
        // ... pause 容器配置
    }
    if err := c.CreateContainer(ctx, pauseCfg); err != nil {
        c.Shutdown()
        return nil, err
    }
    if err := c.StartContainer(ctx, pauseCfg.ID); err != nil {
        c.Shutdown()
        return nil, err
    }

    return &PodSandbox{
        ID:           podConfig.ID,
        ConmonClient: c,  // 保存客户端实例供后续容器使用
        // ...
    }, nil
}

func createContainerInPod(pod *PodSandbox, containerCfg *ContainerConfig) error {
    // 使用同一个 Pod 的 ConmonClient 创建业务容器
    // 不需要启动新的 conmonrs 进程！
    return pod.ConmonClient.CreateContainer(ctx, &client.CreateContainerConfig{
        ID:     containerCfg.ID,
        Bundle: containerCfg.BundlePath,
        // ...
    })
}

func stopPod(pod *PodSandbox) {
    // 停止所有容器
    for _, ctr := range pod.Containers {
        pod.ConmonClient.StopContainer(ctx, ctr.ID)
    }
    // 关闭客户端 - 自动终止 conmonrs 服务器进程
    pod.ConmonClient.Shutdown()
}
```

---

## 步骤 4：容器创建/启动流程对比

### 传统 conmon：CLI 参数驱动

传统 conmon 通过大量命令行参数配置容器：

| 操作 | 传统 conmon 方式 |
|------|-----------------|
| 创建容器 | 启动 conmon 时传 `-b bundle`、`-c cgroup`、`--cid-file` 等数十个参数 |
| 启动容器 | conmon 启动后自动 runc start，或通过 ctl FIFO 发送命令 |
| 停止容器 | 向 conmon 发送信号，或通过 FIFO 发送停止命令 |
| 等待退出 | wait conmon 进程（conmon 退出码 = 容器退出码） |

### conmon-rs：RPC API 驱动

conmon-rs 通过结构化 RPC 调用完成操作：

```go
// 1. 创建容器（CreateContainer RPC）
err = pod.ConmonClient.CreateContainer(ctx, &client.CreateContainerConfig{
    ID:           containerID,
    BundlePath:   bundlePath,
    CgroupPath:   cgroupPath,
    LogPath:      logPath,
    Terminal:     hasTerminal,
    Stdin:        stdinEnabled,
    Stdout:       stdoutFD,     // 通过 SCM_RIGHTS 传递
    Stderr:       stderrFD,
    // ... 更多结构化字段
})

// 2. 启动容器（StartContainer RPC）
err = pod.ConmonClient.StartContainer(ctx, containerID)

// 3. 等待容器退出（WaitContainerExit RPC）
exitCode, err := pod.ConmonClient.WaitContainerExit(ctx, containerID)
```

**优势**：
- API 是类型安全的 Go 结构体，不会拼错参数名
- 不需要解析命令行输出或依赖文件系统上的 cid 文件
- 错误通过 Go error 返回，不是通过退出码
- 可以在 Pod 生命周期内多次调用创建/启动/停止

---

## 步骤 5：Exec 流程变化

这是迁移后最简化的部分——不需要再为 exec 创建新的 conmon 实例！

### 传统 conmon exec：额外 conmon 进程

```go
// 传统方式：exec 也需要一个 conmon 实例
func execInContainer(containerID string, cmd []string) error {
    // 创建 exec 专用的 conmon 实例
    execConmonCmd := exec.Command(
        "conmon",
        "--exec",
        "--cid", containerID,
        "-e", execID,
        "-t", strconv.FormatBool(tty),
        // ... exec 专用参数
    )
    // 这会创建一个额外的 conmon 进程来处理 exec IO
    return execConmonCmd.Start()
}
```

### conmon-rs exec：复用现有实例

```go
// conmon-rs 方式：同一个客户端，同一个服务器进程
func execInPod(pod *PodSandbox, containerID string, execCfg *ExecConfig) error {
    // 通过现有连接发送 ExecContainer RPC
    // 不需要启动新进程！
    execSession, err := pod.ConmonClient.ExecContainer(ctx, &client.ExecConfig{
        ContainerID: containerID,
        Command:     execCfg.Cmd,
        Tty:         execCfg.Tty,
        Stdin:       execCfg.StdinFD,
        Stdout:      execCfg.StdoutFD,
        Stderr:      execCfg.StderrFD,
        // ...
    })
    if err != nil {
        return err
    }

    // 等待 exec 会话结束
    exitCode, err := execSession.Wait(ctx)
    return err
}
```

**变化**：
- ✅ 去掉了一个 fork/exec conmon 的步骤
- ✅ 减少了进程数量
- ✅ exec 启动延迟更低
- ✅ 不需要清理 exec conmon 进程

---

## 步骤 6：日志配置

传统 conmon 主要通过 `-l/--log-path` 写日志文件。conmon-rs 提供三种日志后端，根据部署场景选择：

### 日志后端选择

| 如果你的场景是... | 选择 | 配置 |
|-----------------|------|------|
| 本地 systemd 系统（Podman 单机） | **journald** | `LogDriver: "journald"` |
| Kubernetes + CRI-O | **CRI 格式** | `LogDriver: "cri"` + `LogPath: "/var/log/pods/..."` |
| 需要结构化日志采集（ELK/Loki） | **JSON** | `LogDriver: "json"` + `LogPath: "..."` |

### 配置示例

```go
cfg := &client.ConmonClientConfig{
    // CRI 日志格式（Kubernetes 场景）
    LogDriver: "cri",
    LogPath:   filepath.Join(podLogDir, containerID+".log"),
    // 可选：日志大小限制、轮转
    LogSizeMax: 10 * 1024 * 1024, // 10MB
}

// 或 journald
cfg.LogDriver = "journald"

// 或 JSON
cfg.LogDriver = "json"
cfg.LogPath = jsonLogPath
```

### 查看日志

```bash
# journald 后端
journalctl CONTAINER_ID=abc123...

# CRI/JSON 文件后端
tail -f /var/log/pods/.../abc123.log
```

---

## 步骤 7：终端附加（Attach）

### 传统 conmon：通过 ctl FIFO

传统 conmon 使用 FIFO（命名管道）发送控制命令（如 resize），通过 socket 传递 IO。

### conmon-rs：通过 Attach API

```go
// 附加到运行中容器
attachSession, err := pod.ConmonClient.AttachContainer(ctx, &client.AttachConfig{
    ContainerID: containerID,
    Stdin:       userStdin,
    Stdout:      userStdout,
    Stderr:      userStderr,
    // 可以选择附加哪些流
    AttachStdin:  true,
    AttachStdout: true,
    AttachStderr: true,
})
if err != nil {
    return err
}

// 调整终端窗口大小（类似传统的 WIN_RESIZE_EVENT）
err = pod.ConmonClient.ResizeTerminal(ctx, containerID, &client.ResizeConfig{
    Width:  cols,
    Height: rows,
})

// 等待 attach 会话结束（用户断开等）
err = attachSession.Wait(ctx)
```

---

## 步骤 8：常见迁移问题与解决方案

### Q1: 如何处理需要 per-container conmon 实例的旧代码？

**方案**：conmon-rs 设计上一个实例管理多个容器，但你仍然可以为每个容器创建一个 conmonrs 实例——只是这样无法获得 Pod 级优化的好处，但可以作为过渡方案：

```go
// 过渡方案：每容器一个实例（不推荐，但兼容旧代码结构）
func createContainer(...) {
    // 为每个容器创建独立的 ConmonClient
    c, _ := client.NewConmonClient(ctx, cfg)
    c.CreateContainer(ctx, ...)
    c.StartContainer(ctx, ...)
}
```

### Q2: 怎么获取容器退出码？

传统 conmon 通过自身退出码传递容器退出码。conmon-rs 中：

```go
// RPC 方式等待退出并获取退出码
exitCode, err := pod.ConmonClient.WaitContainerExit(ctx, containerID)
if err != nil {
    // 错误处理
}
fmt.Printf("Container exited with code: %d\n", exitCode)
```

### Q3: OOM 检测怎么工作？

和 C 版本一样，conmon-rs 监控 cgroup 的 OOM 事件，但通过 API 暴露：

```go
// 伪代码：监听 OOM 事件（具体 API 以实际 client 为准）
eventChan := pod.ConmonClient.Events(ctx)
for event := range eventChan {
    switch event.Type {
    case client.EventOOM:
        log.Printf("Container %s OOM killed", event.ContainerID)
    case client.EventExit:
        log.Printf("Container %s exited with %d", event.ContainerID, event.ExitCode)
    }
}
```

### Q4: conmon-rs 会替代 C 版本吗？

conmon-rs 是下一代实现，目标是覆盖 C 版本的所有功能并扩展到 Pod 级管理。但 C 版本仍然稳定维护，两者会并存一段时间。建议：
- 新部署/新项目优先考虑 conmon-rs
- 需要稳定生产的系统可以继续使用 C 版本，待 conmon-rs 成熟后迁移

### Q5: 二进制兼容性？

conmonrs 是静态链接的，不依赖系统库版本，可以在任意 Linux 发行版运行（内核 3.x+，推荐 4.x+ 以获得完整 pidfd 支持）。

### Q6: pidfd 需要什么内核版本？

pidfd 是 Linux 5.3+ 的特性。conmon-rs 在旧内核上应该有回退机制（具体以项目文档为准），但推荐 5.3+ 内核获得最佳体验。

---

## 迁移检查清单

迁移完成后，验证以下检查项：

- [ ] conmonrs 二进制可以在目标系统运行
- [ ] Pod 创建时自动创建 ConmonClient
- [ ] pause 容器通过 RPC 创建并启动
- [ ] 业务容器在同一个 Pod 客户端中创建
- [ ] 容器可以正常启动、停止、删除
- [ ] exec 不需要额外监控进程
- [ ] 日志正确写入选择的后端
- [ ] attach 可以附加到容器终端
- [ ] resize 终端窗口大小正常工作
- [ ] OOM 事件可以正确检测到
- [ ] 容器退出码正确获取
- [ ] Pod 删除时 ConmonClient 正确关闭（conmonrs 进程被回收）
- [ ] 没有遗留僵尸进程

## 相关资源

- [示例：架构概览](01-architecture.md) —— 完整架构图
- [概念：Pod级监控架构](../concepts/00-introduction.md) —— 设计差异详解
- [概念：Go客户端库集成](../concepts/02-go-client.md) —— 客户端 API
- [概念：构建优化与日志后端](../concepts/03-build-optimization.md) —— 日志后端配置
- conmon-rs GitHub: https://github.com/containers/conmon-rs
- usage.md: 项目中的使用文档

## 信源参考

- [README 信源](../references/readme-source.md)
- facts-conmon-rs.md（事实清单）
