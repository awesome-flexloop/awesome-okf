---
type: Concept
title: 构建优化与日志后端
description: conmon-rs 的极致二进制体积优化配置（LTO/opt-level=z/panic=abort/strip）、静态链接构建、三种容器日志后端（journald/CRI/JSON）、cosign 签名验证
tags: [conmon-rs, concept, build, optimization, logging, journald, cri, json, lto]
sources:
  - id: readme-source
    resource: /bundles/containers/conmon-rs/references/readme-source.md
    title: README 项目说明信源
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
---

# 构建优化与日志后端

conmon-rs 作为底层容器运行时组件，对二进制体积、部署便捷性和日志可靠性有严格要求。本文档详细解析其构建优化配置和三种内置日志后端。

## 极致的 Release 构建优化

conmon-rs 在根 `Cargo.toml` 中配置了极其激进的 release profile 优化：

```toml
[profile.release]
lto = true                  # 链接时优化（Link-Time Optimization）
opt-level = "z"             # 优化体积而非速度（"z" = 最小体积）
codegen-units = 1           # 单代码生成单元（更好的优化，但编译慢）
panic = "abort"             # panic 时直接 abort，不展开栈（减小体积）
strip = true                # 剥离符号表（减小体积）
```

### 每个优化选项详解

| 选项 | 值 | 作用 | 体积影响 | 性能影响 | 编译时间影响 |
|------|----|------|---------|---------|-------------|
| **`lto = true`** | 启用 | 跨 crate 链接时优化，可以内联、删除未使用代码、跨 crate 常量传播 | ⬇️ 显著减小 | ⬆️ 通常提升（更好的内联） | ⬆️⬆️ 大幅增加 |
| **`opt-level = "z"`** | "z" | 告诉 LLVM 优先最小化体积，而不是 "s"（平衡）或 "3"（速度） | ⬇️⬇️ 最小化体积 | ⬇️ 可能略降（但容器监控不是 CPU 密集型） | - |
| **`codegen-units = 1`** | 1 | 禁用并行代码生成，让 LLVM 看到完整的 crate 图进行优化 | ⬇️ 减小 | ⬆️ 更好的优化 | ⬆️ 增加（单线程编译） |
| **`panic = "abort"`** | abort | panic 时不生成栈展开（unwind）代码，直接 abort | ⬇️ 减小（无需 unwinder） | ⬆️ 略快（无需展开） | ⬇️ 减少 |
| **`strip = true`** | 启用 | 从二进制中剥离所有调试符号和符号表信息 | ⬇️⬇️ 显著减小（通常减少 50%+） | 无 | - |

### 为什么是 opt-level = "z"？

通常 Rust 项目 release 使用 `opt-level = 3`（速度优先）。conmon-rs 选择 "z"（体积优先）的理由：

1. **容器运行时场景**：conmonrs 是一个守护进程，启动后长时间运行，二进制加载时间和内存占用比峰值 CPU 性能更重要
2. **分发便捷性**：静态二进制越小，通过网络下载/分发越快（scripts/get 从 GCS 下载）
3. **内存占用**：更小的二进制意味着更小的页表开销和更少的内存映射
4. **性能足够**：conmon-rs 的工作主要是等待 IO（子进程退出、socket 消息），不是 CPU 密集计算，体积优化不会成为瓶颈

### 与 C 版本 conmon 的体积对比

（预期）经过这些优化后，conmonrs 静态二进制的体积应该远小于同等功能的 C 版本，同时保持内存 RSS 在 3-4 MB 以下。

## 静态链接与分发

conmon-rs 提供**静态链接**的二进制文件，这意味着：
- 不依赖系统的 glibc 或其他动态库
- 可以在任意 Linux 发行版上运行（只要内核版本够）
- 无需安装依赖，下载即可运行

### 获取静态二进制

项目提供 `scripts/get` 脚本从 Google Cloud Storage 下载最新版本：

```bash
# 下载最新版本到当前目录
curl https://raw.githubusercontent.com/containers/conmon-rs/main/scripts/get | bash

# 下载指定 git SHA 到指定路径
curl https://raw.githubusercontent.com/containers/conmon-rs/main/scripts/get | \
    bash -s -- -t $GIT_SHA -o /usr/local/bin/conmonrs
```

### cosign 签名验证

如果本地 `$PATH` 中有 [`cosign`](https://github.com/sigstore/cosign)（Sigstore 签名工具），`scripts/get` 会自动验证二进制的 sigstore 签名：
- 确保下载的二进制未被篡改
- 验证其确实由 conmon-rs 项目发布
- 供应链安全的重要保障

### Nix 支持

项目还提供 Nix 构建配置（`nix/` 目录）：
- `derivation.nix` — Nix 包定义
- `overlay.nix` — Nix overlay 便于集成到 NixOS
- `static.nix` — 静态链接构建的 Nix 配置

## 三种容器日志后端

容器日志是容器监控进程的核心职责之一。conmon-rs 原生支持三种日志后端，无需外部日志驱动，实现在 `conmon-rs/server/src/container_log/` 目录：

```
container_log/
├── mod.rs        # 日志后端 trait/统一接口
├── journald.rs   # systemd journald 后端
├── cri.rs        # Kubernetes CRI 日志格式后端
└── json.rs       # JSON 结构化日志后端
```

### 日志后端架构

```
容器进程 stdout/stderr
       │
       ▼
┌─────────────────────────────────────────┐
│         conmonrs 日志路由层              │
│  (container_log/mod.rs 统一接口)         │
└─────────┬───────────┬───────────┬───────┘
          │           │           │
          ▼           ▼           ▼
    ┌─────────┐ ┌─────────┐ ┌─────────┐
    │ journald│ │  CRI    │ │  JSON   │
    │ 后端    │ │ 格式    │ │ 格式    │
    └─────────┘ └─────────┘ └─────────┘
          │           │           │
          ▼           ▼           ▼
   systemd journal   日志文件     JSON 行
  (journalctl 查看)  (K8s 解析)  (结构化采集)
```

### 1. journald 后端

**文件**：`container_log/journald.rs`

将容器日志直接写入 systemd journal：
- 与 systemd 生态深度集成
- 使用 `journalctl` 查看日志
- 支持按容器 ID、Pod ID 等元数据过滤
- 自动处理日志轮转（journald 管理）
- 适合使用 systemd 的系统（Fedora、RHEL、Ubuntu 等主流发行版）

**journalctl 查看示例**（预期）：
```bash
# 查看特定容器的日志
journalctl CONTAINER_ID=abc123...

# 查看 conmon-rs 管理的所有容器日志
journalctl _COMM=conmonrs
```

### 2. CRI 日志格式后端

**文件**：`container_log/cri.rs`

实现 Kubernetes CRI（Container Runtime Interface）标准日志格式：
- 这是 Kubernetes 期望的日志格式
- 每行日志格式为：`timestamp stream log`
  - `timestamp`：RFC3339Nano 格式时间戳
  - `stream`：`stdout` 或 `stderr`
  - `log`：原始日志内容
- 自动处理日志轮转和大小限制
- Kubelet 可以直接采集这种格式，无需额外解析

**日志行示例**：
```
2026-08-26T15:30:00.123456789+08:00 stdout Hello from container
2026-08-26T15:30:00.123987654+08:00 stderr Error: something went wrong
```

CRI 格式日志通常写入 `/var/log/pods/<pod>/<container>/` 目录下的文件，Kubelet 会自动监听这些文件。

### 3. JSON 日志后端

**文件**：`container_log/json.rs`

输出结构化 JSON 行格式：
- 每行是一个完整的 JSON 对象
- 包含时间戳、流类型、日志消息等字段
- 便于 ELK、Loki、Datadog 等日志系统采集和索引
- 适合结构化日志处理管道

**JSON 日志行示例**：
```json
{"ts":"2026-08-26T15:30:00.123456789+08:00","stream":"stdout","log":"Hello from container"}
{"ts":"2026-08-26T15:30:00.123987654+08:00","stream":"stderr","log":"Error: something went wrong"}
```

### 日志后端选择

| 后端 | 适用场景 | 查看方式 | 日志轮转 |
|------|---------|---------|---------|
| **journald** | systemd 系统、单机容器、Podman 本地 | `journalctl` | journald 自动管理 |
| **CRI** | Kubernetes、CRI-O 运行时 | Kubelet/`kubectl logs` | conmonrs 按 CRI 标准轮转 |
| **JSON** | 结构化日志采集、ELK/Loki 等 | 日志采集器解析 | 根据配置轮转 |

## journal.rs 与 systemd 集成

除了容器日志后端，`journal.rs` 还处理 conmonrs 自身的日志与 systemd 的集成：
- 服务器自身的日志（tracing 输出）可以输出到 journald
- 使用 systemd 通知机制（`sd_notify`）报告就绪状态
- Watchdog 支持（如果配置了 systemd watchdog）

## 构建方式

### 使用 Makefile

项目提供 Makefile 简化构建：

```bash
# Debug 构建（快速，用于开发）
make build

# Release 构建（带所有优化）
make build-release

# 静态链接构建
make build-static
```

### 使用 Cargo

直接用 Cargo 构建：

```bash
# Debug 构建
cargo build

# Release 构建（应用 release profile 优化）
cargo build --release

# 输出位置：target/release/conmonrs
```

构建产物：
- Rust 服务器：`target/release/conmonrs`
- Rust CLI 客户端：`target/release/conmonrs-cli`

### Cross 编译

项目根目录有 `Cross.toml`，支持使用 [`cross`](https://github.com/cross-rs/cross) 进行交叉编译：
- 在容器中交叉编译到不同目标平台
- 支持 aarch64（ARM64）等架构
- 静态链接跨平台构建

## 可选 Feature：OpenTelemetry

服务器依赖中的 `opentelemetry` 是可选 feature：
- 默认不启用，减小二进制体积
- 需要时通过 `--features opentelemetry` 启用
- 启用后可以导出追踪数据到 Jaeger 等 OpenTelemetry 兼容后端

```bash
# 带 OpenTelemetry 构建
cargo build --release --features opentelemetry
```

这体现了 conmon-rs 的设计哲学：核心功能最小化，高级功能通过 feature flag 按需启用。

## 相关概念

- [Rust 服务器与 Cap'n Proto RPC](01-rust-server.md) —— 服务器模块结构
- [示例：架构概览](../examples/01-architecture.md) —— 完整架构图
- [示例：从 C 版本迁移](../examples/02-migration.md) —— 迁移注意事项

## 信源参考

- [README 信源](../references/readme-source.md) —— 二进制获取与签名验证
- Cargo.toml —— release profile 优化配置
- conmon-rs/server/src/container_log/ —— 三种日志后端实现
- scripts/get —— 下载脚本与 cosign 验证
