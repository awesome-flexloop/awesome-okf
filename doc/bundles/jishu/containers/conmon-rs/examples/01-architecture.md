---
type: Example
title: 架构概览
description: conmon-rs 完整架构图与组件交互详解，从容器引擎到 Rust 服务器的完整调用链
tags: [conmon-rs, example, architecture, diagram, overview]
sources:
  - id: readme-source
    resource: /bundles/containers/conmon-rs/references/readme-source.md
    title: README 项目说明信源
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
---

# 架构概览

本文通过完整的架构图和调用流程，帮助你直观理解 conmon-rs 的双语言组件架构、RPC 通信机制和 Pod 级容器管理模型。

> **前置概念**：阅读前建议先了解 [Pod级监控架构与C版本差异](../concepts/00-introduction.md) 中的核心设计。

## 整体架构图

conmon-rs 采用 **Go 客户端 + Rust 服务器** 的双语言架构，通过 UNIX domain socket 上的 Cap'n Proto RPC 通信：

```
┌─────────────────────────────────────────────────────────────────────┐
│                        容器引擎 (Container Engine)                   │
│                    (CRI-O / Podman / 其他 CRI 兼容)                   │
│                              (Go 编写)                               │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               │  import 并调用
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     Go 客户端库 (pkg/client/)                        │
│                         github.com/containers/conmon-rs/pkg/client   │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                     ConmonClient 结构体                         │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌───────────────────────┐ │  │
│  │  │ 进程管理    │  │ RPC 调用封装  │  │ 文件描述符传递        │ │  │
│  │  │ - 启动/等待  │  │ - capnp_util │  │ - SCM_RIGHTS          │ │  │
│  │  │ - 信号处理  │  │ - 序列化     │  │ - remote_fds.go       │ │  │
│  │  └─────────────┘  └──────────────┘  └───────────────────────┘ │  │
│  └───────────────────────────────────────────────────────────────┘  │
└──────────────┬─────────────────────────────┬────────────────────────┘
               │ 1. fork/exec conmonrs       │
               │    (创建子进程)              │
               ▼                             │
┌──────────────────────────────┐             │
│  Rust 服务器 (conmonrs)       │◄────────────┘
│  conmon-rs/server/src/main.rs│   2. UNIX domain socket
│  ┌────────────────────────┐  │      Cap'n Proto RPC
│  │  CLI 参数解析 (clap)    │  │
│  │  日志初始化 (tracing)   │  │
│  └───────────┬────────────┘  │
│              │               │
│  ┌───────────▼────────────┐  │
│  │  Listener (UDS 监听)   │  │
│  │  listener.rs           │  │
│  └───────────┬────────────┘  │
│              │               │
│  ┌───────────▼────────────┐  │
│  │  RPC 服务 (capnp-rpc)   │  │
│  │  rpc.rs + capnp_util.rs │  │
│  └───────────┬────────────┘  │
│              │               │
│  ┌───────────▼────────────┐  │
│  │  Server 主逻辑          │  │
│  │  server.rs             │  │
│  └───┬────────┬────────┬───┘  │
│      │        │        │      │
│  ┌───▼───┐ ┌──▼───┐ ┌──▼────┐ │
│  │ 进程  │ │ IO/  │ │ 日志   │ │
│  │ 管理  │ │终端  │ │ 后端   │ │
│  │child/ │ │streams/│container_log/│
│  │reaper/│ │attach/│ │journald│ │
│  │oom_   │ │fd_   │ │/cri/   │ │
│  │watcher│ │socket│ │json.rs │ │
│  └───┬───┘ └──┬───┘ └───┬────┘ │
│      │        │         │      │
└──────┼────────┼─────────┼──────┘
       │ fork/exec
       │ (通过 OCI runtime: runc/crun)
       │
┌──────▼────────▼─────────▼──────────────────────────────────────────┐
│                          Pod (容器组)                                │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  pause 容器 (沙箱)                                           │  │
│  │  - 持有 Pod 的命名空间（网络/PID/IPC）                        │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌─────────────────────┐  ┌─────────────────────┐                 │
│  │ 业务容器 A           │  │ 业务容器 B           │  ...            │
│  │ - stdin/stdout/stderr│  │ - stdin/stdout/stderr│                 │
│  │ - cgroup 路径        │  │ - cgroup 路径        │                 │
│  │ - OCI bundle         │  │ - OCI bundle         │                 │
│  └─────────────────────┘  └─────────────────────┘                 │
│                                                                     │
│  所有容器由同一个 conmonrs 实例管理，共享：                          │
│  ✅ 同一个监控进程 ✅ 同一个 RPC 连接 ✅ Pod 级资源统计             │
└─────────────────────────────────────────────────────────────────────┘
```

## Cargo Workspace 组件图

```
conmon-rs/ (Workspace root)
├── Cargo.toml (workspace 配置 + release profile)
├── Cargo.lock
│
├── conmon-rs/
│   ├── common/              # 共享 crate
│   │   ├── Cargo.toml       # (dep: capnp 0.27.0)
│   │   ├── build.rs         # capnpc 代码生成
│   │   ├── proto/
│   │   │   └── conmon.capnp # Cap'n Proto schema (RPC接口定义)
│   │   └── src/lib.rs
│   │
│   ├── client/              # Rust CLI 客户端 (conmonrs-cli)
│   │   ├── Cargo.toml       # (dep: tokio, capnp-rpc, futures, serde)
│   │   └── src/main.rs
│   │
│   └── server/              # 核心服务器 (conmonrs)
│       ├── Cargo.toml       # (dep: axum, clap, nix, libc, tracing...)
│       ├── build.rs
│       └── src/
│           ├── main.rs
│           ├── lib.rs
│           ├── server.rs
│           ├── rpc.rs
│           ├── child.rs
│           ├── child_reaper.rs
│           ├── container_log/
│           │   ├── journald.rs
│           │   ├── cri.rs
│           │   └── json.rs
│           └── ... (其他模块)
│
├── pkg/
│   └── client/              # Go 客户端库
│       ├── client.go        # ConmonClient
│       ├── attach.go
│       ├── capnp_util.go
│       ├── remote_fds.go
│       └── ...
│
├── internal/
│   └── proto/
│       └── conmon.capnp.go  # capnpc 生成的 Go 代码
│
├── scripts/
│   └── get                  # 下载静态二进制的脚本
│
└── nix/                     # Nix 构建配置
    ├── derivation.nix
    ├── overlay.nix
    └── static.nix
```

## 容器创建完整调用链

下面是从容器引擎发起请求到容器启动的完整调用流程：

```
容器引擎 (Go)                   Go 客户端                     Rust 服务器
     │                              │                              │
     │ 1. NewConmonClient(cfg)      │                              │
     ├─────────────────────────────►│                              │
     │                              │ 2. exec.Command(conmonrs)    │
     │                              │    fork/exec 子进程           │
     │                              ├─────────────────────────────►│
     │                              │                              │ 3. main.rs:
     │                              │                              │    - parse args
     │                              │                              │    - init tracing
     │                              │                              │    - bind UDS
     │                              │                              │    - start RPC loop
     │                              │                              │
     │                              │ 4. wait for socket ready     │
     │                              │◄─────────────────────────────┤
     │                              │    (socket 可连接)            │
     │                              │                              │
     │                              │ 5. dial UDS                  │
     │                              │    建立 capnp-rpc 连接        │
     │                              ├─────────────────────────────►│
     │                              │                              │
     │  ◄───────────────────────────┤                              │
     │    (client 创建完成)         │                              │
     │                              │                              │
     │ 6. CreateContainer(cfg)     │                              │
     ├─────────────────────────────►│                              │
     │                              │ 7. 构造 Cap'n Proto 请求     │
     │                              │    capnp_util.go             │
     │                              │                              │
     │                              │ 8. RPC Call (CreateContainer)│
     │                              ├─────────────────────────────►│
     │                              │                              │
     │                              │                              │ 9. rpc.rs: 解析请求
     │                              │                              │
     │                              │                              │ 10. server.rs:
     │                              │                              │     - 验证参数
     │                              │                              │     - 准备日志后端
     │                              │                              │     - fork/exec OCI runtime
     │                              │                              │
     │                              │                              │     [子进程: runc create]
     │                              │                              │     [子进程: 容器进程]
     │                              │                              │
     │                              │                              │ 11. 注册 pidfd
     │                              │                              │     child_reaper
     │                              │                              │
     │                              │                              │ 12. 配置 IO 流
     │                              │                              │     container_io
     │                              │                              │
     │                              │ 13. 返回 OK                  │
     │                              │◄─────────────────────────────┤
     │  ◄───────────────────────────┤                              │
     │    err == nil                 │                              │
     │                              │                              │
     │ 14. StartContainer(id)       │                              │
     ├─────────────────────────────►│                              │
     │                              │ 15. RPC Call (StartContainer)│
     │                              ├─────────────────────────────►│
     │                              │                              │ 16. runc start
     │                              │                              │ 17. 容器进程启动
     │                              │ 18. 返回 OK                  │
     │                              │◄─────────────────────────────┤
     │  ◄───────────────────────────┤                              │
     │                              │                              │
     │ 19. (容器运行中...)          │                              │ 20. oom_watcher:
     │                              │                              │     监控 cgroup OOM
     │                              │                              │ 21. 等待 pidfd 可读
     │                              │                              │     (容器退出)
```

## Exec 调用流程（无需新实例）

对比 C 版本需要为 exec 创建新 conmon 实例，conmon-rs 复用现有服务器进程：

```
C 版本 conmon:
  容器引擎
    └─→ exec 请求
        └─→ fork/exec conmon (实例 3)
            └─→ 连接到容器的 master FD
            └─→ fork/exec exec 进程
            └─→ 处理 IO
            └─→ 等待 exec 退出
            └─→ conmon 实例退出

conmon-rs:
  容器引擎
    └─→ ExecContainer() RPC
        └─→ 现有 conmonrs 实例接收请求
            └─→ fork/exec exec 进程
            └─→ 复用现有进程管理逻辑
            └─→ 复用现有 RPC 连接
            └─→ (无额外监控进程！)
```

## 文件描述符传递流程

容器的 stdin/stdout/stderr 通过 UNIX socket 的 SCM_RIGHTS 机制传递，而不是通过 RPC 消息转发：

```
Go 客户端                          Rust 服务器
    │                                  │
    │ 1. 创建 pipe() 或 openpty()     │
    │    得到 stdin_r/stdin_w 等 FD    │
    │                                  │
    │ 2. 构造 RPC 请求（不包含数据）   │
    │                                  │
    │ 3. sendmsg() 带 SCM_RIGHTS      │
    │    ┌──────────────────────────┐  │
    │    │  RPC 消息头              │  │
    │    │  控制消息: SCM_RIGHTS    │  │
    │    │    - stdin_w FD          │  │
    │    │    - stdout_r FD         │  │
    │    │    - stderr_r FD         │  │
    │    │    (如果是 tty: 一个 PTY FD)
    │    └──────────────────────────┘  │
    ├─────────────────────────────────►│
    │                                  │
    │                                  │ 4. recvmsg() 接收
    │                                  │    提取 FD 到本地进程
    │                                  │
    │                                  │ 5. 容器启动时 dup2() 到
    │                                  │    容器进程的 0/1/2
    │                                  │
    │ 6. 客户端写入 stdin_r          │
    ├─────────────────────────────────►│ → 容器的 stdin
    │                                  │
    │ 7. 容器 stdout → stdout_w      │
    │◄─────────────────────────────────┤
    │  (客户端从 stdout_r 读取)        │
```

这种方式的优点：
- **零拷贝**：数据直接在内核中从管道/PTY 传递到容器，不经过用户态 RPC
- **高效**：FD 传递是一次性操作，后续 IO 是普通的 read/write
- **标准兼容**：容器看到的是普通的 stdin/stdout/stderr 文件描述符

## 三种日志后端选择决策图

```
开始
  │
  ├─► 运行在 systemd 系统上？
  │    └─► 是 ──► 用 journald 后端 ──→ journalctl 查看日志
  │
  ├─► 运行在 Kubernetes (CRI-O) 上？
  │    └─► 是 ──► 用 CRI 格式后端 ──→ kubectl logs 直接可用
  │
  └─► 需要结构化日志采集 (ELK/Loki/Datadog)？
       └─► 是 ──► 用 JSON 后端 ──→ 日志采集器直接解析
       │
       └─► 否 ──► 默认（通常是 CRI 或 journald，取决于配置）
```

## 关键设计决策总结

| 决策 | 选择 | 理由 |
|------|------|------|
| 监控粒度 | Pod 级单实例 | 减少进程数、降低内存占用、Pod 内容器协调更高效 |
| 服务器语言 | Rust | 内存安全、无 GC、高性能、二进制体积可优化 |
| 客户端语言 | Go | 无缝集成 CRI-O/Podman 等 Go 生态容器引擎 |
| 通信协议 | Cap'n Proto | 零拷贝序列化、类型安全、RPC 原生支持 |
| 传输层 | UNIX domain socket | 本机通信高性能、支持 FD 传递、通过文件权限控制访问 |
| 进程等待 | pidfd | 比信号处理更可靠、原生支持异步 IO（epoll） |
| 日志后端 | 内置三种 | 无需外部日志驱动、覆盖主流使用场景 |
| 构建优化 | opt-level="z" + LTO | 最小化二进制体积、便于分发和部署 |

## 延伸阅读

- [示例：从 C 版本迁移](02-migration.md) —— 从传统 conmon 迁移到 conmon-rs 的指南
- [概念：Pod级监控架构](../concepts/00-introduction.md) —— 架构设计理念
- [概念：Rust服务器与Cap'n Proto RPC](../concepts/01-rust-server.md) —— 服务器内部实现
- [概念：Go客户端库集成](../concepts/02-go-client.md) —— 客户端 API 使用

## 信源参考

- [README 信源](../references/readme-source.md) —— 官方架构描述
