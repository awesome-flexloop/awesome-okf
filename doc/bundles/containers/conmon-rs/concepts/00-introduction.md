---
type: Concept
title: Pod 级监控架构与 C 版本差异
description: conmon-rs 的核心设计——从单容器监控演进为 Pod 级监控，与 C 版本 conmon 的架构差异对比，双语言组件设计与内存优化目标
tags: [conmon-rs, concept, architecture, pod, monitor, rust]
sources:
  - id: readme-source
    resource: /bundles/containers/conmon-rs/references/readme-source.md
    title: README 项目说明信源
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
---

# Pod 级监控架构与 C 版本差异

conmon-rs（Rust 语言（Rust programming language）实现的容器监控器）最根本的架构革新是**将监控粒度从"单个容器"提升到"整个 Pod（容器组）"**。这一设计改变了容器引擎与监控进程的交互模型，带来了资源效率和可扩展性的提升。

## 从"一容器一实例"到"一 Pod 一实例"

### C 版本 conmon 的传统模型

在传统的 C 版本 conmon 中，容器引擎（如 CRI-O、Podman）遵循以下模式：

```
容器引擎
  ├─→ 创建容器 A → fork/exec conmon (实例 1) → fork/exec 容器 A 进程
  ├─→ 创建容器 B → fork/exec conmon (实例 2) → fork/exec 容器 B 进程
  └─→ 容器 A exec → fork/exec conmon (实例 3) → 处理 exec 会话
```

**问题**：
- 每个容器至少一个 conmon 进程，Pod 内 N 个容器就有 N 个 conmon 实例
- 每个 exec 操作还要额外创建 conmon 实例
- 进程数量多，内存开销累积
- 容器间协调需要通过容器引擎间接完成

### conmon-rs 的 Pod 级模型

conmon-rs 采用全新的设计：

```
容器引擎
  └─→ 创建 Pod → fork/exec conmon-rs (单个实例)
                    ├─→ 通过 RPC 请求创建容器 A
                    ├─→ 通过 RPC 请求创建容器 B
                    ├─→ 通过 RPC 请求在容器 A 中 exec
                    └─→ 统一管理所有容器的生命周期、日志、终端
```

**优势**：
- 整个 Pod 只需要一个监控实例
- exec 操作复用现有实例，无需额外 fork
- Pod 内容器共享监控进程的资源
- 内存占用目标控制在 RSS 3-4 MB 以下

## 核心架构对比

| 维度 | C 版本 conmon | Rust 版本 conmon-rs |
|------|---------------|---------------------|
| **监控粒度** | 单个容器 | 整个 Pod（容器组） |
| **进程模型** | 一容器一实例 + exec 额外实例 | 一 Pod 一实例，复用处理所有操作 |
| **编程语言** | C（使用 GLib 事件循环） | Rust（服务器）+ Go（Golang，客户端） |
| **通信方式** | 命令行参数、信号、FIFO 管道 | UNIX domain socket + Cap'n Proto RPC |
| **API 设计** | 无结构化 API，通过文件描述符和信号 | 类型安全的 RPC 接口，可扩展 |
| **内存目标** | 无明确目标（通常数 MB/实例） | RSS < 3-4 MB（整个 Pod） |
| **进程等待** | waitpid() + signalfd | pidfd（异步进程退出等待） |
| **日志后端** | 主要是文件日志 | journald + CRI 格式 + JSON 三种内置后端 |

## conmon-rs 的双组件架构

conmon-rs 不是纯 Rust 项目，而是采用**Rust 服务器 + Go 客户端**的双语言架构：

```
┌─────────────────────────────────────────────────────────────┐
│                    容器引擎 (CRI-O/Podman)                    │
│                         (Go 编写)                            │
└──────────────────────────┬──────────────────────────────────┘
                           │ 静态链接/导入
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Go 客户端库                               │
│                   (pkg/client)                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  ConmonClient 结构体                                 │   │
│  │  - 创建服务器子进程                                   │   │
│  │  - 建立 UNIX socket 连接                              │   │
│  │  - 封装 Cap'n Proto RPC 调用                          │   │
│  │  - 提供类型安全的 Go API                              │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │ fork/exec + RPC over UDS
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  Rust 服务器 (conmonrs)                      │
│                (conmon-rs/server)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ RPC 服务     │  │ 进程管理     │  │ 日志后端         │  │
│  │ (Cap'n Proto)│  │ (pidfd)      │  │ (journald/CRI/JSON)│
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ 终端/流处理  │  │ OOM 监控     │  │ 遥测 (可选)      │  │
│  │ (attach)     │  │ (cgroup)     │  │ (OpenTelemetry)  │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │ fork/exec (多个容器)
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
    ┌─────────┐       ┌─────────┐       ┌─────────┐
    │ 容器 A  │       │ 容器 B  │  ...  │ 容器 N  │
    └─────────┘       └─────────┘       └─────────┘
```

### 为什么选择双语言？

1. **Go 生态集成**：CRI-O、Podman 等容器引擎都是 Go 编写的，提供 Go 客户端库可以直接集成，无需 cgo 或进程外调用
2. **Rust 性能安全**：服务器端需要高性能、内存安全、低资源占用，Rust 是理想选择
3. **职责分离**：Go 客户端负责"控制面"（创建服务器、封装 API），Rust 服务器负责"数据面"（实际监控容器、处理 IO）

## 容器创建与通信流程

当容器引擎需要在 Pod 中创建新容器时：

```
1. 容器引擎调用 Go 客户端的 CreateContainer() 方法
2. Go 客户端构造 Cap'n Proto RPC 请求
3. 请求通过 UNIX domain socket 发送给 Rust 服务器
4. Rust 服务器接收请求，验证参数
5. 服务器 fork/exec 容器进程（通过 OCI runtime）
6. 服务器记录容器 PID，设置 pidfd 等待退出
7. 服务器配置容器标准流（stdin/stdout/stderr）
8. 服务器配置日志后端
9. RPC 响应返回给 Go 客户端
10. Go 客户端返回结果给容器引擎
```

**关键点**：整个过程中 conmon-rs 进程保持运行，不需要为新容器 fork 新的监控实例。

## exec 无需重启实例

在 C 版本 conmon 中，`exec`（在运行中容器内执行新进程）需要启动一个新的 conmon 实例来处理 exec 会话的 IO。conmon-rs 中：

- exec 请求通过同一个 RPC 通道发送
- 现有服务器进程处理 exec 进程的创建和 IO
- 无需额外监控进程
- 减少了进程创建开销和内存占用

## 内存占用目标

conmon-rs 明确设定了内存目标：**保持 RSS（Resident Set Size，常驻内存集）在 3-4 MB 以下**。

实现这一目标的手段：
- Rust 语言的内存安全和无 GC 开销
- Release 构建极致优化（详见 [构建优化与日志后端](03-build-optimization.md)）
- 单实例多容器设计减少进程开销
- 高效的数据结构（如 BoundedHashMap）

## 已实现 vs 计划中特性

### ✅ 已实现核心特性

- Pod 级单实例监控
- RSS 内存控制在 3-4 MB 以下
- exec 无需重新生成实例
- Cap'n Proto RPC API（支持 Go 客户端）
- pidfd 异步进程退出等待

### 🔲 未来规划

- 作为 PID 命名空间 init 进程
- 加入网络命名空间运行 Pod 内 hooks
- io_uring 异步 IO
- seccomp 通知插件支持
- 日志速率限制
- 统计信息接口
- IPv6 端口转发

## 相关概念

- [Rust 服务器与 Cap'n Proto RPC](01-rust-server.md) —— 深入了解 Rust 服务器实现和 RPC 机制
- [Go 客户端库集成](02-go-client.md) —— Go 客户端 API 和使用方式
- [构建优化与日志后端](03-build-optimization.md) —— 构建配置和三种日志后端

## 信源参考

- [README 信源](../references/readme-source.md) —— 项目定位与架构描述
