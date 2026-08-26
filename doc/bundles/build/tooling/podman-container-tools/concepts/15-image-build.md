---
type: Concept
title: 官方镜像构建
description: image_build monorepo构建官方容器镜像，ci/build-push.sh支持多架构构建，通过quay.io发布
tags: [podman, concept, image-build, container-image, multi-arch, quay.io, aio, buildah-image, skopeo-image, qemu-user-static]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-26T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-26T00:00:00Z" }
status: stable
stale_after: 2027-08-26
sources: [{id:"podman-source", resource:"/references/podman-source.md", title:"Podman Container Tools 源码信源登记"}]
---

## image_build Monorepo 结构

`image_build/` 目录是一个独立的 monorepo，专门负责构建、测试和发布 Podman 生态系统的官方容器镜像（F-300~F-314）。这些镜像将 Podman、Buildah、Skopeo 等工具本身容器化，使用户可以在容器内运行容器（Docker-in-Docker 的 Podman 等价物）。

### 镜像类型

image_build 构建 4 类官方镜像：

| 镜像 | 包含工具 | 用途 |
|------|---------|------|
| **AIO 镜像（All-In-One）** | Podman + Buildah + Skopeo + 辅助工具 | 全家桶镜像，需要完整容器管理能力的 CI/CD 场景 |
| **Podman 镜像** | 仅 Podman | 只需运行容器的场景 |
| **Buildah 镜像** | 仅 Buildah | 只需构建镜像的 CI 场景 |
| **Skopeo 镜像** | 仅 Skopeo | 只需镜像搬运/检查的场景 |

### 目录结构

image_build 采用按镜像分目录的组织方式，每个镜像有独立的 Containerfile 和配置：

```text
image_build/
├── buildah/                # Buildah 镜像定义
├── podman/                 # Podman 镜像定义
├── skopeo/                 # Skopeo 镜像定义
├── aio/                    # AIO 全家桶镜像定义
├── ci/
│   └── build-push.sh       # 多架构构建与推送主脚本
└── ...
```

每个镜像目录包含：
- **Containerfile**：镜像构建定义
- **containers.conf**：Podman/Buildah 容器内配置文件
- **挂载配置**：存储卷、运行时所需的目录挂载配置

## AIO 镜像：全家桶方案

AIO（All-In-One）镜像包含 Podman、Buildah、Skopeo 三个工具的完整安装，是功能最全的官方镜像：

**使用场景**：
- CI/CD 流水线中需要同时构建、运行、搬运镜像
- 容器化的开发环境
- 需要完整容器工具链的一次性任务

**在容器内运行 Podman**：

```bash
# 运行 AIO 镜像（需要特权访问或正确的安全配置）
podman run --privileged -v /var/lib/containers:/var/lib/containers \
  quay.io/containers/podman:stable podman run --rm alpine echo "Hello from container"

# 或使用 rootless + 用户命名空间
podman run --userns=keep-id --security-opt label=disable \
  -v $HOME/.local/share/containers:/var/lib/containers \
  quay.io/containers/podman:stable podman info
```bash

## 各镜像特点

### Podman 镜像

Podman 镜像仅包含 Podman 运行时及其最小依赖：
- 镜像体积更小
- 适合只需运行容器的场景
- 包含 conmon、crun/runc、netavark 等运行时依赖
- 配置好容器内存储路径

### Buildah 镜像

Buildah 镜像专注镜像构建：
- 包含 Buildah 及其构建依赖
- 不包含网络和运行时组件（构建不需要完整运行时）
- 适合 CI 流水线中作为镜像构建步骤
- 支持 Dockerfile 构建（`buildah bud`）和命令式构建

```bash
# 在 CI 中使用 Buildah 镜像构建镜像
podman run --rm -v $PWD:/build:z -w /build \
  quay.io/buildah/stable buildah bud -t myapp:latest .
```bash

### Skopeo 镜像

Skopeo 镜像提供镜像搬运和检查功能：
- 最小化镜像，仅包含 Skopeo
- 适合跨仓库镜像同步、镜像检查、镜像复制
- 无需存储驱动，不依赖 containers/storage
- 可在无守护进程、无特权的环境中运行

```bash
# 使用 Skopeo 镜像跨仓库复制镜像
podman run --rm quay.io/skopeo/stable copy \
  docker://docker.io/library/alpine:latest \
  docker://registry.example.com/mirror/alpine:latest
```bash

## ci/build-push.sh：多架构构建脚本

`ci/build-push.sh` 是官方镜像的多架构构建和推送入口脚本，支持 4 种 CPU 架构（F-308）：

| 架构 | 说明 |
|------|------|
| **amd64** | x86_64，主流服务器/桌面架构 |
| **arm64** | AArch64，ARM 服务器、Apple Silicon、树莓派 4+ |
| **ppc64le** | IBM PowerPC 64-bit Little Endian，Power 服务器 |
| **s390x** | IBM Z/LinuxONE 大型机架构 |

### 多架构构建机制

多架构镜像构建使用 **qemu-user-static** 实现跨架构模拟：

1. **QEMU 用户态模拟**：通过 binfmt_misc 注册 QEMU 用户态模拟器，使构建主机可以透明运行非本机架构的二进制
2. **单架构构建**：每个架构在隔离环境中分别构建
3. **Manifest List**：构建完成后，将各架构镜像合并为 Docker Manifest List（多架构镜像索引）
4. **自动解析**：容器引擎拉取镜像时自动选择与当前架构匹配的镜像

### 构建流程

`build-push.sh` 的主要执行步骤：

```bash
#!/bin/bash
# ci/build-push.sh 核心流程（概念示意）

# 1. 注册 QEMU binfmt（跨架构构建需要）
# 2. 确定要构建的镜像类型（podman/buildah/skopeo/aio）
# 3. 对每个目标架构：
#    - 设置构建变量（ARCH, REPO, TAG 等）
#    - 调用 buildah bud/podman build 构建单架构镜像
#    - 标记镜像（tag）
# 4. 创建并推送 manifest list
# 5. 附加镜像标签（审计标签等）
```bash

构建脚本支持的参数包括：
- 指定镜像类型（podman/buildah/skopeo/aio）
- 指定构建版本标签
- 是否推送到 registry（CI 中推送，本地构建不推送）
- 目标架构列表

## quay.io 发布仓库

官方镜像发布到 **quay.io** 容器仓库，这是 Red Hat 运营的企业级容器镜像 registry：

| 镜像 | 仓库地址 |
|------|---------|
| Podman | `quay.io/containers/podman` |
| Buildah | `quay.io/buildah/stable`（或 `quay.io/containers/buildah`） |
| Skopeo | `quay.io/skopeo/stable`（或 `quay.io/containers/skopeo`） |
| AIO | `quay.io/containers/podman`（AIO 标记为特定标签） |

### 标签策略

官方镜像使用多标签策略，满足不同使用场景：

| 标签类型 | 示例 | 说明 |
|---------|------|------|
| **stable** | `:stable` | 最新稳定版本，生产环境推荐 |
| **immutable** | `:v5.0.0` | 不可变版本标签，永远指向特定版本 |
| **latest** | `:latest` | 最新版本（可能包括测试版），不推荐生产使用 |
| **testing** | `:testing` | 测试版/预发布版本，用于测试 |
| **upstream** | `:upstream` | 基于上游 main 分支的开发构建 |
| **架构标签** | `:stable-amd64` | 特定架构的镜像（不使用 manifest list） |

**版本标签示例**：
```bash
# 使用稳定版（推荐生产）
podman pull quay.io/containers/podman:stable

# 固定版本（可复现构建）
podman pull quay.io/containers/podman:v5.0.0

# 测试最新功能
podman pull quay.io/containers/podman:testing
```bash

## built.by 审计标签

所有官方镜像包含 `built.by` 审计标签（F-313），用于追踪镜像的构建来源：

| 标签 | 说明 |
|------|------|
| `built.by` | 构建者标识，记录 CI 系统信息 |
| `build.date` | 镜像构建时间戳 |
| `vcs-ref` | Git commit SHA，可追溯到精确源码版本 |
| `vcs-url` | 源码仓库 URL |
| `vendor` | 镜像维护者（containers organization） |
| `licenses` | 许可证信息（Apache-2.0） |

通过 `podman inspect` 可查看这些审计标签：

```bash
podman inspect quay.io/containers/podman:stable \
  --format '{{.Labels}}' | jq
```bash

审计标签的作用：
- **合规性**：满足供应链安全要求，可追溯到源码
- **问题排查**：知道镜像是何时、从哪个 commit 构建的
- **版本验证**：确认使用的镜像是官方构建而非篡改版本

## Containerfile 与 containers.conf 配置

### Containerfile 要点

每个镜像的 Containerfile 遵循以下最佳实践：

```dockerfile
# 示例 Containerfile 结构（概念示意）
FROM quay.io/fedora/fedora:latest

# 安装容器工具
RUN dnf install -y podman buildah skopeo crun netavark && \
    dnf clean all

# 配置容器存储
RUN mkdir -p /var/lib/containers /run/containers
VOLUME ["/var/lib/containers"]

# 配置 containers-storage
COPY containers.conf /etc/containers/containers.conf
COPY storage.conf /etc/containers/storage.conf

# 入口点
ENTRYPOINT ["/usr/bin/podman"]
CMD ["--help"]
```bash

### containers.conf 配置

容器内的 `containers.conf` 配置容器工具的运行参数：

```toml
# 容器内的 containers.conf 关键配置
[containers]
# 默认使用 vfs 存储驱动（容器内运行容器兼容性最好）
# 或 overlay（如果宿主机内核支持）
storage_driver = "vfs"

[engine]
# 容器内使用 crun 运行时（轻量快速）
runtime = "crun"

# 配置 cgroup 管理器
cgroup_manager = "cgroupfs"
```bash

存储驱动选择：
- **vfs**：最兼容，无需内核支持，适合容器内嵌套容器，但无写时复制（空间占用大）
- **overlay**：需要宿主机内核支持 overlayfs in userns，性能好，空间利用率高
- **fuse-overlayfs**：用户态 overlayfs，rootless 兼容方案

### 容器内运行容器的特权要求

在容器内运行 Podman（Podman-in-Podman）有两种模式：

1. **特权模式**（简单但权限大）：
   ```bash
   podman run --privileged quay.io/containers/podman:stable podman run alpine echo hi
   ```

2. **无特权 rootless 模式**（更安全）：
   ```bash
   podman run \
     --security-opt label=disable \
     --security-opt seccomp=unconfined \
     --userns=keep-id \
     -v /dev/fuse:/dev/fuse \
     quay.io/containers/podman:stable podman run alpine echo hi
   ```

## 相关概念

- [容器工具生态全景](/concepts/14-ecosystem.md) — Podman/Buildah/Skopeo三剑客与共享底层库
- [自动化与Machine OS](/concepts/16-automation-ci.md) — automation/CI镜像构建与image_build的关系
- [无Root容器](/concepts/10-rootless.md) — rootless模式嵌套容器配置
- [Runtime运行时](/concepts/03-runtime.md) — conmon/crun/storage驱动等运行时组件
