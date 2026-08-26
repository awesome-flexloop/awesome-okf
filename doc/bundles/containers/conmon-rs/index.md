---
type: OKF
title: conmon-rs 教程
description: conmon-rs——Rust编写的Pod级OCI容器运行时监视器，下一代容器监控架构。包含双语言架构解析、Cap'n Proto RPC、Rust服务器与Go客户端集成、构建优化与日志后端。
tags: [conmon-rs, containers, oci, rust, golang, capnproto, pod, monitor, cri-o, podman, runtime]
version: "1.0.1"
source: https://github.com/containers/conmon-rs
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
---

# conmon-rs 教程

conmon-rs 是一个使用 **Rust** 语言（Rust programming language）编写的 **Pod 级别** OCI（Open Container Initiative）容器运行时监视器。它是传统 C 版本 [conmon](https://github.com/containers/conmon) 的下一代演进——从"每个容器一个监控实例"升级为"每个 Pod（容器组）一个监控实例"，通过 **Go** 语言（Golang）客户端 + Rust 服务器的双语言架构，结合 **Cap'n Proto**（卡普恩原型）零拷贝 RPC（远程过程调用）通信，实现低内存占用（目标 RSS < 3-4 MB）和高性能容器监控。

conmon-rs 的设计目标不仅是覆盖 C 版本 conmon 的全部功能（守护进程化、持有容器标准流、记录退出码），更扩展到 Pod 级管理——容器引擎在创建 Pod 时只需启动一个 conmon-rs 实例，即可通过 RPC 管理 Pod 内多个容器的创建、启动、exec（在运行中容器执行命令）、终端附加等全部生命周期操作，无需为每个容器或 exec 额外 fork 监控进程。

## 📚 快速导航

### [概念文档](concepts/index.md)

- [00-Pod级监控架构与C版本差异](concepts/00-introduction.md) — 核心设计革新：从"一容器一实例"到"一Pod一实例"、双语言架构、与C版本详细对比、内存目标与特性状态 ⭐ 入门必读
- [01-Rust服务器与Cap'n Proto RPC](concepts/01-rust-server.md) — Cargo Workspace三crate组织、Cap'n Proto代码生成、服务器核心模块（进程管理/IO/日志/OOM监控）、pidfd异步等待、subreaper子进程收割、FD传递
- [02-Go客户端库集成](concepts/02-go-client.md) — Go模块配置、ConmonClient生命周期、容器管理/exec/终端API、Cap'n Proto封装、SCM_RIGHTS文件描述符传递、CRI-O/Podman集成流程
- [03-构建优化与日志后端](concepts/03-build-optimization.md) — 极致release优化（lto/opt-level="z"/panic="abort"/strip）、静态链接分发、cosign签名验证、三种内置日志后端（journald/CRI/JSON）、Nix与Cross编译支持

### [实践示例](examples/index.md)

- [01-架构概览](examples/01-architecture.md) — 完整双语言架构图、Cargo Workspace组件图、容器创建21步调用链、exec流程对比、FD传递机制、日志后端决策树 ⭐ 入门
- [02-从C版本迁移](examples/02-migration.md) — 8步迁移流程、Go客户端集成代码、Pod生命周期管理改造、容器/exec/attach API对比、常见问题FAQ、13项迁移检查清单 ⭐⭐ 进阶

### [信源参考](references/index.md)

- [README信源](references/readme-source.md) — 项目定位、架构、目标特性、二进制获取方式（基于官方README提取）

## 🚀 快速获取

### 下载静态二进制（推荐）

conmon-rs 提供静态链接二进制，无需编译即可使用，脚本自动验证 cosign 签名：

```bash
# 下载最新版本
curl https://raw.githubusercontent.com/containers/conmon-rs/main/scripts/get | bash

# 下载到指定路径
curl https://raw.githubusercontent.com/containers/conmon-rs/main/scripts/get | \
    bash -s -- -o /usr/local/bin/conmonrs

# 验证
chmod +x /usr/local/bin/conmonrs
conmonrs --help
```

### 从源码编译

```bash
# 安装 Rust 工具链
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"

# 克隆并编译 release 版本
git clone https://github.com/containers/conmon-rs.git
cd conmon-rs
cargo build --release

# 二进制位置
ls -lh target/release/conmonrs
```

## 🎯 核心特性

| 特性 | 说明 |
|------|------|
| 📦 Pod级单实例 | 一个conmon-rs实例管理Pod内所有容器，exec无需额外进程 |
| 🦀 Rust安全性能 | Rust语言实现，内存安全、无GC、低资源占用 |
| 🐹 Go原生客户端 | 提供Go客户端库，无缝集成CRI-O/Podman等Go生态容器引擎 |
| ⚡ Cap'n Proto RPC | 零拷贝序列化RPC，UNIX domain socket传输，支持FD传递 |
| 🪶 极致体积优化 | LTO + opt-level="z" + strip，静态二进制，目标RSS < 3-4MB |
| 📝 三种日志后端 | 内置journald、CRI格式、JSON日志，无需外部日志驱动 |
| 🔍 pidfd进程等待 | 使用Linux pidfd异步等待进程退出，避免信号处理竞态 |
| 🔒 供应链安全 | 静态二进制通过cosign签名验证，scripts/get自动验证 |
| 📊 可选遥测 | feature flag启用OpenTelemetry分布式追踪 |

## 📖 推荐学习路径

1. **建立认知**：阅读 [00-Pod级监控架构](concepts/00-introduction.md)，理解conmon-rs与传统conmon的核心差异
2. **直观理解**：浏览 [01-架构概览](examples/01-architecture.md) 的架构图和调用流程
3. **深入服务器**：学习 [01-Rust服务器](concepts/01-rust-server.md)，了解Cargo Workspace和服务器模块
4. **客户端集成**：学习 [02-Go客户端](concepts/02-go-client.md)，掌握API使用方式
5. **部署构建**：学习 [03-构建优化](concepts/03-build-optimization.md)，了解构建配置和日志后端
6. **迁移实践**：如果从C版本迁移，详细阅读 [02-迁移指南](examples/02-migration.md)

## 🏗️ 架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                   容器引擎 (CRI-O / Podman)                       │
│                         (Go 编写)                                │
└───────────────────────────┬─────────────────────────────────────┘
                            │ import
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Go 客户端库 (pkg/client)                        │
│  - 自动启动/管理conmonrs进程  - Cap'n Proto RPC封装              │
│  - SCM_RIGHTS文件描述符传递    - 类型安全Go API                  │
└──────────────┬────────────────────────────┬────────────────────┘
               │ fork/exec                  │ UNIX socket + RPC
               ▼                            │
┌──────────────────────────────────────────┐ │
│         Rust 服务器 (conmonrs)           │ │
│  ┌─────────┐ ┌─────────┐ ┌────────────┐ │ │
│  │ RPC服务 │ │进程管理 │ │ 日志后端   │ │ │
│  │(capnp)  │ │(pidfd)  │ │journald/   │◄┘ │
│  └─────────┘ └─────────┘ │CRI/JSON    │   │
│  ┌─────────┐ ┌─────────┐ └────────────┘   │
│  │终端/IO  │ │OOM监控  │                  │
│  │(attach) │ │(cgroup) │                  │
│  └─────────┘ └─────────┘                  │
└──────────────────────┬────────────────────┘
                       │ fork/exec
          ┌────────────┼────────────┐
          ▼            ▼            ▼
    ┌──────────┐ ┌──────────┐ ┌──────────┐
    │ 容器 A   │ │ 容器 B   │ │ exec进程  │ ... 同一Pod共享监控
    └──────────┘ └──────────┘ └──────────┘
```

## 🔄 与 C 版本 conmon 对比

| 维度 | C 版本 conmon | Rust 版本 conmon-rs |
|------|---------------|---------------------|
| 监控粒度 | 单个容器 | 整个 Pod（容器组） |
| 实例数量 | 每容器1个 + 每exec1个 | 每Pod1个，复用处理所有操作 |
| 语言 | C（GLib事件循环） | Rust（服务器）+ Go（客户端） |
| 通信 | 命令行+信号+FIFO | UNIX socket + Cap'n Proto RPC |
| 内存 | 每实例数MB（累积） | 目标RSS < 3-4MB（整个Pod） |
| 进程等待 | waitpid + signalfd | pidfd（异步） |
| 日志 | 文件为主 | journald/CRI/JSON三种内置 |
| 静态二进制 | 需要手动构建 | 官方提供，cosign签名 |

## 🔗 外部资源

- **GitHub 仓库**：[containers/conmon-rs](https://github.com/containers/conmon-rs)
- **Rust API 文档**：[containers.github.io/conmon-rs](https://containers.github.io/conmon-rs/conmonrs/index.html)
- **Go API 文档**：[pkg.go.dev - conmon-rs/pkg/client](https://pkg.go.dev/github.com/containers/conmon-rs/pkg/client)
- **使用文档**：[usage.md](https://github.com/containers/conmon-rs/blob/main/usage.md)
- **发布指南**：[release.md](https://github.com/containers/conmon-rs/blob/main/release.md)
- **Cap'n Proto 官网**：[capnproto.org](https://capnproto.org)
- **传统 conmon（C版本）**：[containers/conmon](https://github.com/containers/conmon)

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
