---
type: Concept
title: Podman 简介
description: Podman是无守护进程的OCI容器与Pod管理工具，支持rootless运行与Docker兼容CLI，采用Apache 2.0许可证
tags: [podman, concept, introduction, container, oci, rootless, daemonless]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
verified: { by: "human:trae-agent", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
sources:
  - id: podman-source
    resource: /references/podman-source.md
    title: Podman 源码参考
---

## 什么是 Podman

Podman（POD MANager）是一个用于管理 OCI（Open Container Initiative）容器和 Pods 的工具。Podman 基于 libpod 库开发，该库提供了容器、Pods、容器镜像和卷的管理 API。

Podman 的核心设计理念是**无守护进程（daemonless）**——它不依赖常驻的 manager daemon 进程，这与传统的 Docker 架构形成鲜明对比。这种设计提升了系统安全性，并减少了空闲时的资源占用。

## 与 Docker 的核心区别

Podman 与 Docker 最显著的架构差异在于守护进程模型：

| 特性 | Podman | Docker |
|------|--------|--------|
| **架构模型** | 无守护进程，直接通过 CLI 与 OCI 运行时交互 | Client-Server 架构，依赖 dockerd 守护进程 |
| **进程模型** | 每个容器是 CLI 进程的子进程，无单点故障 | 所有容器由 dockerd 管理，守护进程崩溃影响全部容器 |
| **权限模型** | 原生支持 rootless，无需 setuid | rootless 支持较晚，默认需要 root 权限或 setuid |
| **CLI 兼容性** | 提供 Docker 兼容的命令行接口 | 原生 Docker CLI |

Podman 的 CLI 设计与 Docker 高度兼容，大多数 `docker` 命令可以直接替换为 `podman` 使用，降低了用户的迁移成本。

## Rootless 容器特性

Podman 原生支持无 root（rootless）运行容器，无需 setuid 二进制文件。在 rootless 模式下，Podman 使用用户命名空间（user namespace）将容器内的 root 用户映射到运行 Podman 的普通用户，容器内进程拥有的权限不超过启动 Podman 的用户权限。

这种设计带来的安全优势包括：
- 容器逃逸无法获得宿主机 root 权限
- 多个普通用户可以在同一台机器上独立运行容器而互不干扰
- 降低了容器运行时的攻击面

## 生态定位：容器工具三剑客

Podman 并不是孤立存在的工具，它与 Buildah、Skopeo 共同构成了 Podman Container Tools 生态系统：

| 工具 | 核心职责 | 与 Podman 的关系 |
|------|----------|------------------|
| **Podman** | 维护和运行 OCI 镜像及容器 | 核心运行时工具，负责容器生命周期管理 |
| **Buildah** | 构建 OCI 容器镜像 | 专注镜像构建，Podman 的 build 命令底层使用 Buildah 库 |
| **Skopeo** | 容器镜像搬运与检查 | 跨镜像仓库复制、检查镜像，无需完整拉取 |

三者分工明确、功能互补，共同提供了完整的容器管理能力，而无需依赖单一的守护进程。这些项目共享容器社区维护的底层库（containers/storage、containers/image 等），保持了生态的一致性。

## 开源许可与版本发布

Podman 采用 **Apache 2.0** 许可证开源，这是一种宽松的开源许可证，允许商业使用、修改、分发和专利授权。

项目遵循固定的版本发布节奏：**每年发布 4 次主要/次要版本**，分别在 2 月、5 月、8 月、11 月的第二周发布。这种可预测的发布周期便于用户规划升级。

当前项目使用 Go 语言开发，Go 模块路径为 `go.podman.io/podman/v6`。

## 跨平台支持

Podman 在不同平台上的运行方式有所差异：

- **Linux**：原生运行容器，直接与 Linux 内核的 cgroup、namespace 等特性交互
- **macOS**：通过 Podman 管理的轻量级虚拟机运行容器
- **Windows**：通过 Podman 管理的虚拟机（支持 WSL2）运行容器

这种架构保证了在非 Linux 平台上也能获得一致的容器体验，底层通过 `pkg/machine/` 包管理虚拟机生命周期。

## 社区治理

Podman Container Tools 是一个社区驱动的项目，在 community 仓库中提供共享治理文档，包括：
- 治理结构（GOVERNANCE.md）
- 行为准则（CODE-OF-CONDUCT.md）
- 安全政策（SECURITY.md）
- 贡献指南（CONTRIBUTING.md）
- LLM 使用政策（LLM_POLICY.md）

## 相关概念

- [快速上手](01-getting-started.md) — 各平台安装方式与第一个容器运行
- [架构概览](02-architecture-overview.md) — 无守护进程架构与核心抽象分层
- [Runtime 运行时](03-runtime.md) — libpod 核心 Runtime 结构体与初始化流程
