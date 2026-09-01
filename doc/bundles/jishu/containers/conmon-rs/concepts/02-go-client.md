---
type: Concept
title: Go 客户端库集成
description: conmon-rs Go 客户端库（pkg/client）的架构设计、ConmonClient API、Cap'n Proto 封装、与容器引擎的集成方式、文件描述符传递机制
tags: [conmon-rs, concept, go, golang, client, api, cri-o, podman]
sources:
  - id: readme-source
    resource: /bundles/containers/conmon-rs/references/readme-source.md
    title: README 项目说明信源
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
---

# Go 客户端库集成

conmon-rs 虽然核心服务器使用 Rust 语言（Rust programming language）编写，但它为容器生态系统提供了完整的 **Go 语言（Golang）客户端库**，位于 `pkg/client/` 目录。这是因为 CRI-O、Podman 等主流容器引擎都是用 Go 编写的，提供原生 Go 客户端可以无缝集成到这些项目中。

## Go 模块配置

```go
// go.mod
module github.com/containers/conmon-rs

go 1.26.3

require (
    capnproto.org/go/capnp/v3          // Cap'n Proto Go 实现
    github.com/opencontainers/runc     // OCI runc 类型绑定
    go.podman.io/common                // Podman 共享库
    // ... 其他依赖
)
```

Go 模块路径是 `github.com/containers/conmon-rs`，Go 版本要求 1.26.3。

## 为什么需要 Go 客户端？

容器引擎（CRI-O、Podman）的集成流程：

```
┌─────────────────────────────────────────────────────────────┐
│                    CRI-O / Podman (Go)                      │
│                                                             │
│  直接 import "github.com/containers/conmon-rs/pkg/client"   │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              ConmonClient (Go 结构体)                 │   │
│  │  - 类型安全的 API                                     │   │
│  │  - 自动管理 conmonrs 服务器进程生命周期                │   │
│  │  - 封装 Cap'n Proto 序列化/反序列化                   │   │
│  │  - 处理文件描述符传递                                 │   │
│  └───────────────────────┬─────────────────────────────┘   │
└──────────────────────────┼──────────────────────────────────┘
                           │
          ┌────────────────┴────────────────┐
          │ 1. fork/exec conmonrs 二进制    │
          │ 2. 连接 UNIX socket             │
          │ 3. Cap'n Proto RPC              │
          ▼                                 ▼
┌─────────────────────────────────────────────────────────────┐
│              Rust 服务器 (conmonrs 二进制)                   │
└─────────────────────────────────────────────────────────────┘
```

**关键设计决策**：Go 客户端是**主要接口**——它不仅负责发送 RPC 请求，还负责**创建和管理 Rust 服务器进程**。容器引擎不需要手动启动 conmonrs，客户端库会处理：
- 启动 conmonrs 子进程
- 等待服务器 socket 就绪
- 建立 RPC 连接
- 容器退出时清理服务器进程

## pkg/client 目录结构

```
pkg/client/
├── client.go          # ConmonClient 主结构体、连接管理、核心 API
├── client_test.go     # 客户端测试
├── attach.go          # 终端附加（attach）实现
├── capnp_util.go      # Cap'n Proto 序列化/反序列化工具
├── consts.go          # 常量定义
├── errors.go          # 错误类型定义
├── remote_fds.go      # 远程文件描述符传递（SCM_RIGHTS）
├── files_test.go      # 文件相关测试
└── suite_test.go      # 测试套件
```

## ConmonClient：核心 API 结构体

`client.go` 中定义的 `ConmonClient` 是主要入口点。它的典型生命周期：

```go
// 伪代码示意（非真实 API，仅说明概念）
package main

import (
    "github.com/containers/conmon-rs/pkg/client"
)

func main() {
    // 1. 创建客户端配置
    cfg := &client.ConmonClientConfig{
        // conmonrs 二进制路径
        ConmonrsPath: "/usr/local/bin/conmonrs",
        // UNIX socket 路径（用于和服务器通信）
        SocketPath: "/run/podman/conmon-rs/pod-123.sock",
        // 日志级别
        LogLevel: "info",
        // 日志后端：journald/cri/json
        LogDriver: "journald",
        // ... 其他配置：容器日志路径、cgroup 路径等
    }

    // 2. 创建并启动客户端（内部会启动 conmonrs 服务器进程）
    c, err := client.NewConmonClient(cfg)
    if err != nil {
        panic(err)
    }
    // 程序退出时清理
    defer c.Shutdown()

    // 3. 通过 RPC 创建容器
    containerCfg := &client.CreateContainerConfig{
        ID:     "container-abc",
        Bundle: "/var/lib/containers/storage/overlay/.../bundle",
        // ... OCI 配置、终端标志、日志路径等
    }
    err = c.CreateContainer(ctx, containerCfg)
    if err != nil {
        panic(err)
    }

    // 4. 启动容器
    err = c.StartContainer(ctx, "container-abc")
    if err != nil {
        panic(err)
    }

    // 5. 在容器中执行命令（exec）
    execCfg := &client.ExecConfig{
        ContainerID: "container-abc",
        Cmd:         []string{"/bin/sh"},
        Tty:         true,
        // ... stdin/stdout/stderr 流
    }
    err = c.ExecContainer(ctx, execCfg)
    if err != nil {
        panic(err)
    }
}
```

## 核心 API 方法

根据 conmon-rs 的定位，ConmonClient 应该提供以下核心方法（具体方法名以实际代码为准）：

| 方法类别 | 方法 | 职责 |
|---------|------|------|
| **生命周期** | `NewConmonClient()` | 创建客户端、启动 conmonrs 服务器、建立连接 |
| | `Shutdown()` / `Close()` | 关闭连接、终止服务器进程 |
| **容器管理** | `CreateContainer()` | 通过 RPC 在 Pod 中创建新容器 |
| | `StartContainer()` | 启动已创建的容器 |
| | `StopContainer()` | 停止运行中的容器 |
| | `RemoveContainer()` | 移除容器 |
| | `WaitContainerExit()` | 等待容器退出，获取退出码 |
| **Exec 操作** | `ExecContainer()` | 在运行中容器内执行进程（复用同一服务器实例） |
| | `ExecAttach()` | 附加到 exec 会话的 IO |
| **终端/IO** | `AttachContainer()` | 附加到容器的 stdin/stdout/stderr（类似 `docker attach`） |
| | `ResizeTerminal()` | 调整终端窗口大小（TIOCSWINSZ） |
| **日志** | `GetContainerLogs()` | 获取容器日志 |
| **状态** | `GetContainerStatus()` | 查询容器状态 |
| | `Ping()` | 健康检查（RPC ping） |

## Cap'n Proto 封装层

Go 客户端不直接暴露 Cap'n Proto 细节，而是通过 `capnp_util.go` 中的工具函数封装：

```
Go 原生类型/结构体
        │
        ▼
capnp_util.go 转换函数
        │
        ├─→ 构造 Cap'n Proto 消息
        ├─→ 序列化到缓冲区
        ├─→ 通过 UNIX socket 发送
        │
        ▼
Rust 服务器接收并处理
        │
        ▼
Cap'n Proto 响应返回
        │
        ├─→ 从缓冲区读取（零拷贝）
        ├─→ capnp_util.go 转换
        │
        ▼
Go 原生类型/结构体
```

这种封装的好处：
- 容器引擎代码不需要了解 Cap'n Proto
- API 是惯用的 Go 风格（结构体、context、error 返回值）
- schema 更新时只需修改 capnp_util.go，上层 API 保持稳定

## 文件描述符传递：SCM_RIGHTS

容器的 stdin/stdout/stderr 不是通过 RPC 消息体传递的（那样效率太低），而是使用 UNIX domain socket 的 **ancillary data（辅助数据）** 机制传递文件描述符：

```go
// remote_fds.go 中的概念示意
func sendFd(sock *net.UnixConn, fd int) error {
    // 使用 UnixRights 构造 SCM_RIGHTS 消息
    rights := syscall.UnixRights(fd)
    // 通过 WriteMsg 发送带辅助数据的消息
    _, _, err := sock.WriteMsgUnix(nil, rights, nil)
    return err
}

func recvFd(sock *net.UnixConn) (int, error) {
    // 接收消息，提取文件描述符
    buf := make([]byte, 0)
    oob := make([]byte, syscall.CmsgSpace(4))
    _, _, _, _, err := sock.ReadMsgUnix(buf, oob)
    // 解析 control message，获取 fd
    // ...
}
```

这是 Go 客户端的关键能力——容器引擎可以把管道/PTY 的文件描述符直接传递给 Rust 服务器，服务器直接写入这些 fd，不需要通过 RPC 转发字节流。

## 与 CRI-O/Podman 的集成

在 CRI-O 或 Podman 中，集成 conmon-rs 的大致流程：

1. **Pod 创建时**：
   - 引擎决定使用 conmon-rs 而非传统 conmon
   - 创建 ConmonClient 实例，这会自动启动 conmonrs 服务器进程
   - 为 Pod 准备 socket 路径、日志目录等

2. **创建 Pod 沙箱（pause 容器）**：
   - 调用 `CreateContainer()` 创建 pause 容器
   - 调用 `StartContainer()` 启动 pause 容器
   - pause 容器持有 Pod 的命名空间

3. **创建业务容器**：
   - 对 Pod 内每个容器，调用 `CreateContainer()`
   - 每个容器都在同一个 conmonrs 实例中管理
   - 传递 OCI bundle 路径、cgroup 路径等

4. **启动容器**：
   - 调用 `StartContainer()` 启动容器
   - conmonrs 服务器 fork/exec OCI runtime（runc/crun）

5. **运行中操作**：
   - exec：调用 `ExecContainer()`，不需要新 conmon 实例
   - attach：调用 `AttachContainer()` 附加到终端
   - logs：通过日志后端或 `GetContainerLogs()` 获取

6. **Pod 删除时**：
   - 停止并移除所有容器
   - 调用 `Shutdown()` 关闭客户端
   - conmonrs 服务器进程被终止并回收

## 错误处理

`errors.go` 定义了 conmon-rs 客户端的错误类型。Go 惯用的 `(result, error)` 返回值模式让错误处理直接集成到容器引擎现有的错误处理流程中。

## 测试

`pkg/client/` 包含测试文件：
- `client_test.go`：客户端基本功能测试
- `files_test.go`：文件/FD 传递相关测试
- `suite_test.go`：Ginkgo/Gomega 测试套件配置

测试覆盖了主要的 RPC 调用流程和 FD 传递机制。

## 与 Rust 客户端的对比

| 维度 | Go 客户端（pkg/client） | Rust 客户端（conmon-rs/client） |
|------|-------------------------|--------------------------------|
| **用途** | 生产集成（CRI-O/Podman） | 开发/测试/调试 |
| **API 风格** | 惯用 Go 风格（context + error） | Rust 风格（Result + async/await） |
| **服务器管理** | 自动启动/管理 conmonrs 进程 | 需要手动启动服务器 |
| **FD 传递** | 完整支持（SCM_RIGHTS） | 支持 |
| **主要用户** | 容器引擎开发者 | conmon-rs 开发者 |

## 相关概念

- [Pod 级监控架构与 C 版本差异](00-introduction.md) —— 双组件架构设计
- [Rust 服务器与 Cap'n Proto RPC](01-rust-server.md) —— 服务器端 RPC 实现
- [示例：架构概览](../examples/01-architecture.md) —— 完整架构图

## 信源参考

- [README 信源](../references/readme-source.md) —— Go 客户端介绍
- go.mod —— Go 模块与依赖
- pkg/client/*.go —— Go 客户端源码
