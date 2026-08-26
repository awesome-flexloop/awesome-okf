---
type: ConceptIndex
title: conmon-rs 概念文档索引
description: conmon-rs Pod级OCI容器监控器概念文档导航，涵盖架构、Rust服务器、Go客户端、构建优化与日志
tags: [conmon-rs, concept, index, containers, oci, monitor]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
---

# conmon-rs 概念文档索引

本目录包含 conmon-rs 的核心概念文档，建议按编号顺序阅读以建立完整理解。

## 学习路径

```
架构入门 → Rust 服务器深入 → Go 客户端集成 → 构建与部署
```

**00（架构入门）**建立对 conmon-rs 的核心认知——它是什么、与 C 版本的根本差异、双语言架构；**01**深入 Rust 服务器内部；**02**讲解 Go 客户端如何与服务器交互；**03**涵盖构建优化、日志后端和部署。

---

## 概念文档列表

| 编号 | 文档 | 描述 |
|------|------|------|
| 00 | [Pod级监控架构与C版本差异](00-introduction.md) | conmon-rs 最根本的架构革新：从"一容器一实例"到"一Pod一实例"；与 C 版本 conmon 的详细对比；Rust 服务器 + Go 客户端双语言架构；内存目标 RSS < 3-4MB；已实现/计划中特性 |
| 01 | [Rust服务器与Cap'n Proto RPC](01-rust-server.md) | Cargo Workspace 三crate组织；conmon-common 协议定义与代码生成；conmonrs 服务器核心依赖（axum/tokio/nix/capnp）；服务器源码模块结构（进程管理/IO/日志/OOM监控）；Cap'n Proto 零拷贝RPC；pidfd异步进程等待；subreaper子进程收割；文件描述符传递 |
| 02 | [Go客户端库集成](02-go-client.md) | Go 模块配置（go 1.26.3）；为什么 Go 客户端是主要接口；ConmonClient 核心结构体与生命周期；容器管理/Exec/终端/日志 API；Cap'n Proto 封装层设计；SCM_RIGHTS 文件描述符传递；与 CRI-O/Podman 的集成流程 |
| 03 | [构建优化与日志后端](03-build-optimization.md) | 极致release优化配置详解（lto/opt-level="z"/codegen-units=1/panic="abort"/strip）；静态链接二进制分发；scripts/get下载脚本与cosign签名验证；三种内置日志后端：journald/CRI格式/JSON格式；日志后端选择指南；Nix构建支持；Cross交叉编译；OpenTelemetry可选feature |

---

## 前置知识

阅读这些概念文档不需要深入的 Rust 或 Go 语言知识，但了解以下概念会有帮助：

| 概念 | 说明 |
|------|------|
| OCI 容器运行时 | 了解 runc/crun、容器生命周期、bundle 格式等基本概念 |
| Pod | Kubernetes Pod（容器组）概念——多个容器共享网络/命名空间 |
| Unix 域套接字（UDS） | 知道 UNIX domain socket 是什么，以及它与 TCP 的区别 |
| RPC | 远程过程调用的基本概念 |
| C 版本 conmon | 如果了解传统 conmon 的工作方式，对比理解会更深刻 |

---

## 相关资源

| 资源 | 路径 | 说明 |
|------|------|------|
| 实践示例 | [examples/](../examples/index.md) | 架构概览图、从 C 版本迁移指南 |
| 信源参考 | [references/](../references/index.md) | README信源、源码模块索引 |
| 项目主页 | https://github.com/containers/conmon-rs | GitHub 仓库 |
| Rust API 文档 | https://containers.github.io/conmon-rs/conmonrs/index.html | conmonrs 服务器文档 |
| Go API 文档 | https://pkg.go.dev/github.com/containers/conmon-rs/pkg/client | ConmonClient 文档 |

## 概念关系图

```
00-introduction (架构入门)
    ├── 为什么是 Pod 级？ ──→ 01-rust-server (如何管理多个容器)
    ├── 双语言架构 ────────→ 01-rust-server (Rust 端)
    │                       └─→ 02-go-client (Go 端)
    └── 部署目标 ──────────→ 03-build-optimization (优化与日志)

01-rust-server (Rust 服务器)
    ├── Cargo Workspace ──→ 03-build-optimization (构建配置)
    ├── 日志模块 ─────────→ 03-build-optimization (日志后端详解)
    └── RPC 协议 ─────────→ 02-go-client (客户端如何调用)

02-go-client (Go 客户端)
    └── FD 传递 ──────────→ 01-rust-server (服务器端 fd_socket)
```

```{toctree}
:hidden:
:maxdepth: 7

00-introduction
01-rust-server
02-go-client
03-build-optimization
```
