---
type: ExampleIndex
title: conmon-rs 实践示例
description: conmon-rs 架构概览与从 C 版本迁移指南，通过图文和对比理解 conmon-rs 的使用
tags: [conmon-rs, example, index, tutorial, migration, architecture]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
---

# conmon-rs 实践示例

本目录包含 conmon-rs 的实践示例和指南，帮助你从架构层面理解 conmon-rs，并指导从传统 C 版本 conmon 的迁移。

> **配套文档**：核心概念讲解见 [概念文档](../concepts/index.md)，信源参考见 [参考文档](../references/index.md)。

---

## 前置条件

### 了解背景知识

阅读示例前，建议先具备以下基础：

| 知识点 | 要求 | 补充资源 |
|--------|------|---------|
| OCI 容器基础 | 理解容器、镜像、bundle、runc | [OCI runtime-spec](https://github.com/opencontainers/runtime-spec) |
| Pod 概念 | 知道 Pod 是容器组 | Kubernetes Pod 文档 |
| 传统 conmon | 了解 C 版本 conmon 的作用（迁移示例需要） | conmon 项目文档 |
| Go 基础 | 能读懂 Go 代码示例（客户端 API 是 Go） | Go 官方教程 |
| Rust 基础 | 不需要（概念文档已解释关键 Rust 术语） | - |

### 运行环境（如果要实际运行 conmonrs）

- Linux 内核 5.3+（推荐，获得完整 pidfd 支持）
- Rust 工具链（从源码编译需要，rustup 安装）
- 或直接下载静态二进制（无需 Rust）
- 可选：cosign（验证二进制签名）
- 可选：Go 1.26+（开发集成需要）

---

## 示例列表

| 序号 | 示例 | 难度 | 核心内容 |
|------|------|------|---------|
| 1 | [架构概览](01-architecture.md) | ⭐ 入门 | 完整双语言架构图、Cargo Workspace 组件图、容器创建调用链、exec流程对比、FD传递机制、日志后端选择决策图、关键设计决策总结 |
| 2 | [从 C 版本迁移](02-migration.md) | ⭐⭐ 进阶 | 核心认知转变、进程模型对比、8步迁移流程、Go客户端集成代码、Pod生命周期管理改造、容器/exec/日志/attach API对比、常见问题FAQ、迁移检查清单 |

---

## 示例详情

### 1. [架构概览](01-architecture.md) ⭐ 入门

**适合人群**：所有 conmon-rs 初学者，尤其是想快速了解整体架构的开发者。

通过多张架构图直观理解 conmon-rs 的设计：

- **整体架构图**：从容器引擎 → Go 客户端 → Rust 服务器 → Pod 内容器的完整层次
- **Cargo Workspace 组件图**：三个 crate（common/client/server）的职责和依赖
- **容器创建调用链**：从 `CreateContainer()` 到容器进程启动的 21 步时序
- **Exec 流程对比**：C 版本（新 conmon 实例）vs conmon-rs（复用实例）的流程图
- **文件描述符传递**：SCM_RIGHTS 机制图解
- **日志后端决策树**：如何选择 journald/CRI/JSON

你将获得：
- 对 conmon-rs 各组件如何协同工作的直观理解
- 理解为什么选择双语言架构和 Cap'n Proto
- 掌握关键设计决策的理由

---

### 2. [从 C 版本迁移](02-migration.md) ⭐⭐ 进阶

**适合人群**：需要将 CRI-O/Podman 或其他容器引擎从传统 conmon 迁移到 conmon-rs 的开发者。

这是一份面向集成开发者的迁移指南，涵盖：

- **核心认知转变**：从"一容器一conmon"到"一Pod一conmon-rs"的思维转换
- **8 步迁移流程**：获取二进制→集成客户端→Pod生命周期改造→容器操作→exec→日志→attach→测试
- **代码对比**：传统 CLI 参数方式 vs Go RPC API 方式的代码并列对比
- **关键简化**：exec 不再需要额外 fork conmon 实例
- **日志配置**：三种后端的适用场景和配置方法
- **常见问题 FAQ**：退出码获取、OOM检测、内核版本、兼容性等
- **迁移检查清单**：13 项验证项确保迁移完整

你将学会：
- 如何在 Go 项目中集成 conmon-rs 客户端库
- 如何改造 Pod/容器生命周期管理逻辑
- 如何处理 exec、attach、日志等常见操作的 API 变化

---

## 快速导航图

```
我是 conmon-rs 新手
    │
    └─→ 先读 [概念文档: 00-简介](../concepts/00-introduction.md)
         │
         └─→ 读 [示例: 01-架构概览](01-architecture.md) 看图建立认知
              │
              ├─→ 想深入 Rust 服务器？ ──→ [概念: 01-Rust服务器](../concepts/01-rust-server.md)
              ├─→ 想了解 Go 客户端 API？ ──→ [概念: 02-Go客户端](../concepts/02-go-client.md)
              └─→ 想了解构建/日志？ ──→ [概念: 03-构建优化](../concepts/03-build-optimization.md)

我要从 C 版本迁移到 conmon-rs
    │
    └─→ 先读 [示例: 02-迁移指南](02-migration.md)
         │
         └─→ 根据需要回查概念文档
```

---

## 延伸阅读

- [conmon-rs GitHub 仓库](https://github.com/containers/conmon-rs) —— 源码、Issue、Release
- [conmon-rs Rust API 文档](https://containers.github.io/conmon-rs/conmonrs/index.html) —— conmonrs 服务器的 rustdoc
- [conmon-rs Go API 文档](https://pkg.go.dev/github.com/containers/conmon-rs/pkg/client) —— ConmonClient 的 GoDoc
- [usage.md](https://github.com/containers/conmon-rs/blob/main/usage.md) —— 官方使用文档
- [Cap'n Proto 官网](https://capnproto.org) —— RPC 序列化框架介绍
- [传统 conmon](https://github.com/containers/conmon) —— C 版本源码，对比参考

```{toctree}
:hidden:
:maxdepth: 7

01-architecture
02-migration
```
