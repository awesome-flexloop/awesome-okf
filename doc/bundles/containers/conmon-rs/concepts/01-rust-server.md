---
type: Concept
title: Rust 服务器与 Cap'n Proto RPC
description: conmon-rs Rust 服务器的架构设计、Cargo Workspace 组织、Cap'n Proto RPC 协议、核心模块（进程管理/IO/日志/OOM监控）与 axum Web 框架
tags: [conmon-rs, concept, rust, server, capnproto, rpc, axum]
sources:
  - id: readme-source
    resource: /bundles/containers/conmon-rs/references/readme-source.md
    title: README 项目说明信源
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
---

# Rust 服务器与 Cap'n Proto RPC

conmon-rs 的核心是 Rust 语言（Rust programming language）编写的服务器进程（二进制名 `conmonrs`），它负责实际的容器监控工作。服务器通过 Cap'n Proto（卡普恩原型）RPC（远程过程调用）协议与 Go 客户端通信，使用 UNIX domain socket 作为传输层。

## Cargo Workspace 组织

conmon-rs 使用 Rust 的 Cargo Workspace 管理多个 crate（包）：

```toml
# 根 Cargo.toml
[workspace]
members = [
    "conmon-rs/common",    # 共享：Cap'n Proto 协议、公共类型
    "conmon-rs/client",    # Rust CLI 客户端
    "conmon-rs/server",    # 核心服务器（我们主要关注的部分）
]

[workspace.package]
version = "1.0.1"
license = "Apache-2.0"
edition = "2024"
```

### 三个 Crate 的职责

| Crate | 路径 | 二进制/库 | 核心依赖 | 职责 |
|-------|------|-----------|----------|------|
| **conmon-common** | `conmon-rs/common/` | 库（rlib） | `capnp 0.27.0` | Cap'n Proto schema 定义、共享数据结构、build.rs 代码生成 |
| **conmonrs-cli** | `conmon-rs/client/` | 二进制 | `tokio`、`capnp-rpc`、`futures`、`serde` | Rust 命令行客户端（主要用于测试/调试） |
| **conmonrs** | `conmon-rs/server/` | 二进制 + 库 | `axum`、`clap`、`nix`、`libc`、`tracing`、`opentelemetry`（可选） | 核心监控服务器 |

## conmon-common：协议定义

所有 RPC 接口和数据结构都在 `conmon-rs/common/proto/conmon.capnp` 中定义。Cap'n Proto 的独特之处在于它是**"零拷贝"序列化框架**——数据不需要编码/解码步骤，可以直接从序列化格式中读取，这也是 conmon-rs 选择它的原因之一（性能 + 低延迟）。

### 代码生成流程

```
conmon.capnp (schema 定义)
     │
     ▼
capnpc 编译器 (通过 build.rs 调用)
     │
     ├─→ Rust 代码 (conmon-common/src/capnp/ 或生成位置)
     │   └─→ 由 conmonrs 服务器使用
     │
     └─→ Go 代码 (internal/proto/conmon.capnp.go)
         └─→ 由 pkg/client Go 客户端使用
```

`conmon-rs/common/build.rs` 在编译时自动调用 capnpc 生成 Rust 代码，确保 schema 修改后两端代码自动同步。

## 服务器核心依赖

`conmon-rs/server/Cargo.toml` 的关键依赖：

```toml
[dependencies]
# Web 框架（用于 HTTP 端点？或 RPC 传输？）
axum = "..."        # Rust 异步 Web 框架
# 命令行解析
clap = "..."        # 命令行参数解析器（derive 特性）
# Unix 系统编程
nix = "..."         # Rust 友好的 Unix 系统调用绑定
libc = "..."        # 原始 libc 绑定
# 异步运行时
tokio = "..."       # Rust 异步运行时（与 axum 配合）
# 日志与追踪
tracing = "..."     # 结构化日志框架
# Cap'n Proto
capnp = "0.27.0"
capnp-rpc = "..."   # Cap'n Proto RPC 实现
# 可选：遥测
opentelemetry = { version = "...", optional = true }
```

## 服务器源码模块结构

`conmon-rs/server/src/` 目录结构：

```
server/src/
├── main.rs              # 二进制入口点
├── lib.rs               # 库根（导出公共 API）
├── config.rs            # 配置解析（clap  derive 定义）
├── server.rs            # 服务器主逻辑
├── listener.rs          # UNIX socket 监听
├── rpc.rs               # Cap'n Proto RPC 服务实现
├── capnp_util.rs        # Cap'n Proto 工具函数
│
├── 进程管理
├── child.rs             # 容器子进程表示
├── child_reaper.rs      # 子进程收割者（subreaper）
├── init.rs              # 容器 init 进程处理
├── pause.rs             # pause 容器（Pod 沙箱）
├── oom_watcher.rs       # OOM 事件监控（cgroup v1/v2）
│
├── IO 与终端
├── container_io.rs      # 容器 IO 抽象
├── streams.rs           # 标准流（stdin/stdout/stderr）处理
├── terminal.rs          # 终端（PTY）处理
├── attach.rs            # 终端附加（类似 docker attach）
├── fd_socket.rs         # 文件描述符通过 socket 传递
├── fd_mapping.rs        # FD 映射
├── streaming_server.rs  # 流式数据服务
│
├── 日志
├── journal.rs           # systemd journal 集成
├── container_log/       # 容器日志后端
│   ├── mod.rs
│   ├── journald.rs      # journald 日志后端
│   ├── cri.rs           # CRI（Container Runtime Interface）日志格式
│   └── json.rs          # JSON 日志格式
│
└── 其他
    ├── macros.rs        # 过程宏/宏定义
    ├── bounded_hashmap.rs # 有界 HashMap（内存控制）
    ├── version.rs       # 版本信息
    └── telemetry.rs     # OpenTelemetry 遥测（可选 feature）
```

## RPC 通信模型

### 传输层：UNIX Domain Socket

客户端和服务器运行在同一台机器上，使用 **UNIX domain socket**（UDS）进行通信：
- 比 TCP loopback 更快（无网络栈开销）
- 支持文件描述符传递（`SCM_RIGHTS`）——这是关键特性，用于传递容器的 stdin/stdout/stderr 文件描述符
- 通过文件系统权限控制访问

### 协议：Cap'n Proto RPC

Cap'n Proto RPC 提供：
- **类型安全**：schema 定义接口，编译时检查
- **异步**：基于 futures 的异步 RPC
- **流水线**：支持 RPC 流水线调用
- **双向通信**：服务器可以回调客户端

### 典型 RPC 调用流程

```
Go 客户端                          Rust 服务器
    │                                 │
    │  1. 构造 CreateContainer 请求   │
    │  (capnp struct)                 │
    ├────────────────────────────────→│
    │                                 │ 2. 反序列化（零拷贝！）
    │                                 │ 3. 验证参数
    │                                 │ 4. 调用 server.rs 中的处理函数
    │                                 │ 5. fork/exec 容器进程
    │                                 │ 6. 设置 pidfd 等待
    │                                 │ 7. 配置日志/流
    │  9. 接收响应                    │ 8. 构造响应
    │←────────────────────────────────┤
    │                                 │
```

注意：由于使用 Cap'n Proto，步骤 2 的"反序列化"实际上**不需要复制数据**——可以直接在接收缓冲区上读取字段。

## 关键服务器特性

### 1. 子进程收割（Child Reaper）

conmon-rs 会将自己设置为 **subreaper（子进程收割者）**（通过 `prctl(PR_SET_CHILD_SUBREAPER)`）：
- 当容器进程的父进程退出后，conmon-rs 会成为其"收养父进程"
- 确保容器进程成为孤儿时仍能被正确 wait() 回收
- 避免僵尸进程（zombie processes）

这对应 C 版本中的 `set_subreaper(true)` 机制。

### 2. pidfd 异步进程等待

conmon-rs 使用 Linux 的 **pidfd**（进程文件描述符）机制等待进程退出，而不是传统的信号处理：
- pidfd 是一个文件描述符，引用特定进程
- 可以通过 epoll/kevent 等异步 IO 机制等待
- 避免信号处理的竞态条件和复杂性
- 比 `waitpid()` + `SIGCHLD` 信号处理更可靠

### 3. BoundedHashMap：内存控制

`bounded_hashmap.rs` 实现了一个有上界的 HashMap，用于限制缓存大小，确保内存使用不会无限增长——这是实现 RSS < 3-4 MB 目标的重要组件。

### 4. 多种日志后端内置

服务器内置三种日志后端（详见 [构建优化与日志后端](03-build-optimization.md)），无需外部日志驱动：
- journald：写入 systemd journal
- CRI 格式：Kubernetes CRI 标准日志格式
- JSON：结构化 JSON 日志

### 5. 文件描述符传递

通过 `fd_socket.rs` 和 `fd_mapping.rs`，服务器可以在 UNIX socket 上使用 `SCM_RIGHTS`  ancillary 消息传递文件描述符。这用于：
- 将容器的 stdout/stderr 传递给客户端
- 传递终端 PTY 的主端文件描述符
- 附加到运行中容器时传递 IO 流

### 6. OOM 监控

`oom_watcher.rs` 监控容器的 cgroup 内存事件，检测 OOM（Out of Memory，内存不足）条件：
- 支持 cgroup v1 和 v2
- v1 使用 eventfd 监听 `memory.oom_control`
- v2 使用 inotify 或轮询 `memory.events`

### 7. 可选 OpenTelemetry 遥测

通过 feature flag 启用 OpenTelemetry 支持：
- 分布式追踪
- 指标收集
- 适合生产环境监控和调试

## 二进制入口点

`conmon-rs/server/src/main.rs` 是 `conmonrs` 二进制的入口：
1. 解析命令行参数（使用 clap derive）
2. 初始化 tracing 日志
3. 初始化可选的 OpenTelemetry
4. 创建 UNIX socket 监听器
5. 启动 Cap'n Proto RPC 事件循环
6. 等待并处理请求

## 与 Rust 客户端的关系

`conmon-rs/client/` 提供了一个 Rust CLI 客户端（`conmonrs-cli`），主要用于：
- 开发和测试
- 调试 RPC 接口
- 作为如何使用 conmon-common 中 Cap'n Proto 代码的示例

生产环境中主要使用 Go 客户端（见 [Go 客户端库集成](02-go-client.md)）。

## 相关概念

- [Pod 级监控架构与 C 版本差异](00-introduction.md) —— 为什么采用这种架构
- [Go 客户端库集成](02-go-client.md) —— 客户端如何调用服务器
- [构建优化与日志后端](03-build-optimization.md) —— 构建配置与三种日志后端

## 信源参考

- [README 信源](../references/readme-source.md) —— 架构概览
- Cargo.toml（根目录 + conmon-rs/common/ + conmon-rs/server/）—— 依赖与 workspace 配置
- conmon-rs/common/proto/conmon.capnp —— RPC 协议 schema
