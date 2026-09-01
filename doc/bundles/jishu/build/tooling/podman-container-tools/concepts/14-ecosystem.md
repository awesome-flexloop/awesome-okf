---
type: Concept
title: 容器工具生态全景
description: Containers组织项目全景，Podman+Buildah+Skopeo三剑客协作，共享底层库，社区治理统一在community仓库
tags: [podman, concept, ecosystem, buildah, skopeo, containers, storage, netavark, community, governance]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-26T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-26T00:00:00Z" }
status: stable
stale_after: 2027-08-26
sources: [{id:"podman-source", resource:"/references/podman-source.md", title:"Podman Container Tools 源码信源登记"}]
---

## Containers 组织项目全景

Podman 是 containers GitHub 组织下多个项目之一，这些项目共同构成了一个完整的、无守护进程的容器工具生态系统。所有项目采用开源协作模式开发，共享底层库，分工明确。

### 核心三剑客

| 项目 | 核心职责 | 定位 |
|------|---------|------|
| **Podman** | 维护和运行 OCI 镜像及容器（容器生命周期管理、Pod 管理、Kubernetes YAML 支持） | 核心运行时工具 |
| **Buildah** | 专注构建 OCI 容器镜像 | 镜像构建专家 |
| **Skopeo** | 容器镜像搬运与跨仓库检查 | 镜像运输工具 |

三剑客各自独立但功能互补，共同提供了 Docker CLI 所覆盖的全部功能，且无需依赖任何守护进程。

### 共享底层库

三剑客和其他 containers 项目共享一套底层库，这些库封装了容器运行的核心能力：

| 库 | 核心职责 | 被谁使用 |
|----|---------|---------|
| **containers/storage** | 容器镜像和容器层的存储管理（copy-on-write、层缓存） | Podman、Buildah、CRI-O |
| **containers/image** | 容器镜像的拉取、推送、格式转换、签名验证 | Podman、Buildah、Skopeo |
| **containers/common** | 共享配置、工具函数、通用类型定义（seccomp、capabilities、sysctl 等） | 全部容器工具 |
| **containers/netavark** | 容器网络栈（Rust 编写，替代 CNI，内置 DNS/IPAM/IPv6） | Podman |
| **containers/libpod** | Podman 核心库，定义 Container/Pod/Runtime 抽象 | Podman |

### Podman 核心依赖

Podman 构建在以下关键项目之上：

| 依赖 | 作用 |
|------|------|
| containers/buildah | Podman 的 `build` 命令底层直接调用 Buildah 库构建镜像 |
| containers/image | 镜像拉取、推送、签名、格式转换 |
| containers/storage | 镜像和容器层的本地存储管理 |
| containers/common | 共享配置解析、安全选项处理 |
| containers/netavark | 默认容器网络后端 |
| conmon | 容器监控进程（OCI runtime  companion） |
| crun/runc | OCI 容器运行时（实际创建和运行容器进程） |

## Podman vs Buildah：互补而非竞争

Buildah 专注于构建 OCI 镜像，Podman 专注于维护和运行容器，两者互补：

| 维度 | Buildah | Podman |
|------|---------|--------|
| **核心目标** | 细粒度控制镜像构建过程 | 用户友好的容器运行时管理 |
| **构建方式** | 支持 `buildah from/run/commit` 精细的命令式构建 | `podman build`（调用 Buildah）提供 Dockerfile 构建体验 |
| **运行能力** | 可运行构建过程中的临时容器（仅用于构建） | 完整的容器/Pod 生命周期管理 |
| **Dockerfile 支持** | `buildah bud`（build using Dockerfile） | `podman build`（等价于 buildah bud） |
| **镜像推送** | `buildah push` | `podman push`（底层调用 containers/image） |
| **目标用户** | 需要精细控制构建过程的高级用户/CI 系统 | 日常容器运行、开发、部署 |
| **守护进程** | 无守护进程 | 无守护进程 |

典型的镜像构建工作流可以混用两者：
- 简单构建：`podman build -t myimage .`（内部使用 Buildah）
- 精细构建：使用 `buildah from`/`buildah run`/`buildah copy` 等命令一步步构建，完全控制每一层
- 构建后运行：用 `podman run` 启动构建好的镜像

这种"Buildah 负责构建，Podman 负责运行"的分工让每个工具都保持简洁聚焦，避免了单一工具的功能膨胀。

## Podman 仓库子目录概览

Podman 主仓库包含 5 个主要子目录/模块，各自承担不同职责：

| 子目录 | 职责范围 | 说明 |
|--------|---------|------|
| `podman/`（主代码） | CLI 命令、libpod 库、API 服务、核心引擎 | Podman 主体代码，包含 cmd/、libpod/、pkg/ 等 |
| `automation/` | CI/CD 自动化脚本与配置 | 包含 CI 镜像构建、Mac 测试池、Renovate 依赖更新 |
| `community/` | 社区治理文档 | 共享治理、行为准则、贡献指南（为 Podman/Buildah/Skopeo/Container Libraries 共享） |
| `image_build/` | 官方容器镜像构建 | AIO/Podman/Buildah/Skopeo 官方镜像，多架构构建脚本 |
| `podman-machine-os/` | Podman Machine 虚拟机磁盘镜像构建 | 构建 macOS/Windows 上使用的 Podman Machine OS 镜像 |

### automation/：CI 自动化

`automation/` 目录（F-100~F-110）包含 Podman 项目的 CI/CD 基础设施：
- CI 自动化脚本：定义 PR、构建、发布、验证等工作流
- `container-images/`：CI 流水线使用的容器镜像构建定义
- `mac_pw_pool/`：macOS 测试的密码池管理（Mac CI 测试需要）
- `renovate/`：Renovate 依赖更新配置，自动更新 Go 依赖和容器镜像引用

### community/：社区治理

`community/` 目录（F-200~F-207）是 Podman、Buildah、Skopeo 以及 Container Libraries 项目共享的社区治理中心。这意味着这些容器工具项目遵循统一的治理模式和社区规范：
- **GOVERNANCE.md**：治理结构，描述项目如何决策、维护者如何产生
- **CODE-OF-CONDUCT.md**：行为准则，保证社区环境友好包容
- **CONTRIBUTING.md**：贡献指南，如何提交 Issue、PR、参与开发
- **MEETINGS.md**：社区会议记录，定期社区同步会议的议程和纪要
- **SECURITY.md**：安全政策，如何报告安全漏洞
- **PRIORITIES.md**：项目优先级路线图
- **LLM_POLICY.md**：LLM/AI 工具使用政策

F-207 明确指出这些治理文档是多个容器项目**共享**的，体现了 containers 组织的统一协作模式。

### image_build/：官方镜像构建

`image_build/` 目录（F-300~F-314）负责构建和发布 Podman 生态的官方容器镜像，包括：
- AIO（All-In-One）镜像：包含 Podman + Buildah + Skopeo 全家桶
- Podman 镜像：仅包含 Podman
- Buildah 镜像：仅包含 Buildah
- Skopeo 镜像：仅包含 Skopeo
- `ci/build-push.sh`：多架构构建脚本
- 支持多架构：amd64、arm64、ppc64le、s390x
- 发布到 quay.io 容器仓库
- `built.by` 审计标签，记录镜像构建来源

### podman-machine-os/：Machine OS 构建

`podman-machine-os/` 目录（F-400~F-415）负责构建 Podman Machine 使用的虚拟机磁盘镜像：
- `build.sh`：构建入口脚本
- 在 Linux 环境下以 root 权限运行构建
- 依赖 rpm-ostree 和 osbuild 构建工具
- 支持两种镜像类型：COREOS（基于 Fedora CoreOS）和 WSL（Windows Subsystem for Linux）
- `verify/` 目录包含 Go 测试，验证构建出的镜像正确性

## 三剑客协作流程

三剑客配合完成容器全生命周期管理的典型流程：

```text
镜像构建 → 镜像传输 → 容器运行 → 镜像分发
  ↓          ↓          ↓          ↓
Buildah    Skopeo     Podman     Skopeo/Podman
```

### 示例：从源码到生产部署

```bash
# 1. Buildah 精细构建镜像（或用 podman build）
buildah from --name mybuild docker.io/library/golang:1.22
buildah copy mybuild ./src /src
buildah run mybuild -- go build -o /app /src
buildah commit mybuild myapp:latest

# 2. Skopeo 检查镜像、跨仓库搬运
skopeo inspect containers-storage:localhost/myapp:latest
skopeo copy containers-storage:localhost/myapp:latest docker://registry.example.com/myapp:v1

# 3. Podman 拉取运行
podman pull registry.example.com/myapp:v1
podman run -d -p 8080:8080 --name myapp myapp:v1

# 4. Podman 管理运行中的容器
podman ps
podman logs myapp
podman generate kube myapp > myapp-pod.yaml

# 5. Skopeo 在不同仓库间同步镜像
skopeo sync --src docker --dest docker registry.example.com/myapp mirror.example.com/myapp
```bash

### 与 Docker 单工具模式对比

Docker 采用"一个守护进程 + 一个 CLI"的大而全模式：
- dockerd 同时负责镜像构建、容器运行、网络管理、镜像传输
- 所有功能耦合在一个守护进程中
- dockerd 崩溃会影响所有运行中的容器

Podman 生态采用"小工具协作"的 Unix 哲学：
- 每个工具专注做好一件事
- 通过共享库复用底层能力
- 工具之间通过标准 OCI 镜像格式和容器存储协作
- 无单点故障

## 相关生态项目

除了三剑客和共享库，containers 组织还维护其他重要项目：

| 项目 | 说明 |
|------|------|
| **CRI-O** | Kubernetes CRI（容器运行时接口）实现，用于 Kubernetes 集群的轻量级容器运行时，底层也使用 containers/storage 和 containers/image |
| **conmon** | 容器监控进程，OCI runtime 的 companion，负责日志收集、TTY 分配、容器退出监控 |
| **crun** | 快速轻量的 OCI 容器运行时（C 编写），比 runc 更快、内存更小 |
| **runc** | OCI 参考运行时（Go 编写），Docker 也使用此运行时 |
| **youki** | Rust 编写的 OCI 运行时（containers 组织合作项目） |
| **libhvee** | Podman Machine 对 Hyper-V 虚拟化的支持（Windows） |
| **vfkit** | macOS 上的虚拟化框架支持 |
| **gvisor-tap-vsock** | Podman Machine 虚拟机网络栈 |
| **qemu-user-static** | 跨架构镜像构建的 QEMU 用户态模拟器 |

## 社区治理与贡献

Containers 项目社区遵循开源最佳实践：

### 贡献渠道
- **GitHub Issues**：报告 Bug、提出功能请求
- **GitHub Pull Requests**：提交代码贡献
- **社区会议**：定期公开会议，讨论路线图和重大变更
- **Slack/Matrix**：实时交流渠道
- **邮件列表**：正式讨论和公告

### 贡献流程
1. 在 GitHub 上搜索已有 Issue，避免重复
2. 提交 Issue 描述问题或提案
3. Fork 仓库，创建特性分支
4. 编写代码，确保测试通过
5. 提交 PR，遵循 Conventional Commits 规范
6. 通过 CI 检查和代码审查
7. 维护者合并

### 共享治理的优势

Podman、Buildah、Skopeo 共享 community 仓库治理文档的优势：
- 统一的行为准则和贡献流程，降低跨项目贡献门槛
- 共享的安全政策，漏洞处理流程一致
- 统一的社区会议，三剑客用户和开发者可以共同讨论
- 避免重复的治理文档维护工作
- 强化生态整体的一致性和协同性

## 相关概念

- [Podman简介](00-introduction.md) — Podman在容器工具生态中的定位
- [官方镜像构建](15-image-build.md) — image_build目录AIO/Podman/Buildah/Skopeo镜像构建详解
- [自动化与Machine OS](16-automation-ci.md) — automation/CI自动化与podman-machine-os镜像构建系统
- [systemd集成与Quadlet](12-systemd-quadlet.md) — CRI-O作为K8s运行时与Podman的关系
