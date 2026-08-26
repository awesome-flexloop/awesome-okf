---
type: Concept
title: 架构概览
description: Podman无守护进程架构解析、三层核心抽象、双引擎模式、libpod库分层与REST API设计
tags: [podman, concept, architecture, libpod, abi, tunnel, rest-api, daemonless]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
verified: { by: "human:trae-agent", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
sources:
  - id: podman-source
    resource: /references/podman-source.md
    title: Podman 源码参考
---

## 无守护进程架构

Podman 采用**无守护进程（daemonless）**架构，这是它与 Docker 最根本的架构差异。

### Docker 的 Client-Server 模型

Docker 使用经典的 Client-Server 架构：
- `docker` CLI 只是一个轻量客户端
- 所有容器操作都通过 REST API 发送给常驻的 `dockerd` 守护进程
- `dockerd` 负责镜像管理、容器生命周期、网络、存储等全部功能
- 守护进程以 root 权限运行，成为单点故障和安全攻击面

```text
┌─────────┐    REST API    ┌───────────┐   OCI calls   ┌──────────┐
│ docker  │ ─────────────→ │  dockerd   │ ────────────→ │  runc/   │
│  CLI    │                │ (daemon)   │               │  crun    │
└─────────┘                └───────────┘               └──────────┘
                               │
                               ├── 镜像管理
                               ├── 容器管理
                               ├── 网络管理
                               └── 存储管理
```

### Podman 的无守护进程模型

Podman 摒弃了中心化守护进程，采用更直接的架构：
- `podman` CLI 进程直接通过 libpod 库与底层组件交互
- 每个容器是 Podman CLI 进程的子进程（通过 conmon 监控）
- 没有常驻的 root 权限守护进程
- 进程间使用 fork/exec 和传统 Unix 机制通信

```text
┌─────────────────────────────────────────────────────────┐
│                     podman CLI 进程                     │
│  ┌──────────┐  ┌─────────┐  ┌────────┐  ┌───────────┐ │
│  │ Cobra CLI│  │  libpod │  │  ABI/  │  │ conmon/   │ │
│  │  框架    │→ │ Runtime │→ │ Tunnel │→ │ OCI runtime│ │
│  └──────────┘  └─────────┘  └────────┘  └───────────┘ │
└─────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
   ┌─────────┐          ┌─────────┐          ┌─────────┐
   │  镜像   │          │  网络   │          │  存储   │
   │ (storage)│          │(netavark)│          │(containers│
   │ Buildah  │          │ pasta   │          │ storage) │
   └─────────┘          └─────────┘          └─────────┘
```

这种架构带来的优势包括：
- **安全性**：无 root 常驻进程，rootless 模式下攻击面极小
- **资源效率**：空闲时无后台进程占用 CPU 和内存
- **可靠性**：无单点故障，一个 CLI 进程崩溃不影响其他运行容器
- **可组合性**：各组件可独立使用（Buildah 构建镜像、Skopeo 搬运镜像）

## 三层核心抽象

libpod 库定义了三层核心抽象来管理容器化资源：Runtime、Container 和 Pod。

### Runtime：运行时环境

Runtime 是 libpod 的最顶层抽象，代表一个容器运行时实例。它负责：
- 管理全局配置（config.Config）
- 持有状态存储连接（State：BoltDB 或 SQLite）
- 管理容器存储（storage.Store）
- 注册 OCI 运行时（默认 crun）
- 管理网络栈（nettypes.ContainerNetwork）
- 提供事件系统（events.Eventer）
- 管理异步 worker 池

所有容器和 Pod 的操作都通过 Runtime 实例进行。Runtime 初始化是一个复杂过程，由 `NewRuntime()` 函数完成，支持函数式选项模式配置。

### Container：单个容器

Container 代表一个独立的 OCI 容器，是资源隔离和执行的基本单元。Container 结构体包含：
- **静态配置**（ContainerConfig）：镜像、命令、环境变量、挂载点、资源限制等
- **运行时状态**（ContainerState）：运行状态、PID、挂载点、启动/结束时间、退出码等
- **锁**（lock.Locker）：用于并发操作的同步
- **反向引用**：指向所属 Runtime 的指针（*Runtime）
- **OCI 运行时引用**：实际使用的 OCI 运行时实例

所有访问 Container 状态的操作都必须以 `syncContainer()` 开头，确保从底层状态存储同步最新状态。Container 还维护一个 `valid` 字段标记是否可用。

### Pod：容器组

Pod 是 Kubernetes 启发的概念，代表一组共同调度和管理的容器。Pod 内的容器共享：
- 网络命名空间（IP 地址、端口空间）
- IPC 命名空间
- PID 命名空间（可选）
- 存储卷
- cgroup 资源限制（可选）

Pod 结构体包含：
- **静态配置**（PodConfig）：ID、名称、命名空间、标签、cgroup 配置、重启策略、资源限制等
- **运行时状态**（podState）：cgroup 路径、infra 容器 ID
- **锁和反向引用**：与 Container 类似

Pod 操作访问状态前必须调用 `updatePod()`。Pod 可以包含一个 infra 容器来持有命名空间，其他容器加入 infra 容器的命名空间。

## 双引擎模式：ABI 与 Tunnel

Podman CLI 支持两种运行引擎模式，通过 `pkg/domain/` 层统一抽象。

### 业务逻辑层：pkg/domain/

`pkg/domain/` 是 Podman 的业务逻辑抽象层，采用清晰的分层设计：

```text
┌─────────────────────────────────────────┐
│              CLI (Cobra)                │
├─────────────────────────────────────────┤
│        pkg/domain/entities/             │
│     ContainerEngine/ImageEngine 接口     │
├──────────────────┬──────────────────────┤
│   infra/abi/     │    infra/tunnel/     │
│  (本地实现)      │    (远程实现)         │
│ 直接调用 libpod  │   通过 REST API 调用  │
└──────────────────┴──────────────────────┘
```

- **entities/**：定义接口和数据结构，包括 `ContainerEngine` 和 `ImageEngine` 两个核心接口
- **infra/abi/**：ABI（Application Binary Interface）模式的本地实现，直接链接 libpod 库调用本地功能
- **infra/tunnel/**：Tunnel 模式的远程实现，通过 HTTP 绑定（`pkg/bindings/`）连接到远程 Podman 服务

命令注册时通过 `registry.Commands` 标记命令支持的模式，`parseCommands()` 根据当前 EngineMode（ABIMode/TunnelMode）过滤可用命令。

### ABI 模式（本地）

默认模式，CLI 进程直接链接 libpod：
- 所有操作在本地完成，无网络开销
- 完整功能可用（包括需要本地文件系统访问的功能）
- libpod 代码仅在非 remote 构建且 Linux/FreeBSD 平台编译（build tag: `!remote && (linux || freebsd)`）

### Tunnel 模式（远程）

用于管理远程 Podman 实例：
- CLI 通过 REST API 与远程 `podman service` 通信
- 支持 `podman system connection` 管理多个远程连接
- 部分需要本地访问的命令不可用
- 使用 `pkg/bindings/` 提供类型安全的 HTTP 客户端绑定

## libpod 库分层结构

libpod 是 Podman 的核心容器管理库，代码组织清晰分层。

### 核心文件组织

| 模块 | 核心文件 | 职责 |
|------|----------|------|
| **Runtime 层** | `runtime.go`, `options.go`, `runtime_worker.go` | 运行时初始化、全局配置、worker 池 |
| **Container 层** | `container.go`, `container_api.go`, `container_config.go`, `container_internal.go` | 容器生命周期、配置、状态同步 |
| **Pod 层** | `pod.go`, `pod_api.go`, `pod_internal.go`, `pod_status.go` | Pod 管理、容器组调度 |
| **状态层** | `state.go`, `boltdb_state.go`, `sqlite_state.go` | 状态存储接口与两种实现（BoltDB、SQLite） |
| **OCI 运行时层** | `oci.go`, `oci_conmon.go`, `oci_conmon_linux.go`, `oci_util.go` | OCI 运行时交互、conmon 进程管理 |
| **网络层** | `networking_common.go`, `networking_linux.go`, `networking_rootlessport.go` | 网络配置、rootless 端口转发 |
| **镜像层** | `runtime_img.go` | 与 libimage 库集成的镜像操作 |
| **事件层** | `events/events.go`, `events/logfile.go`, `events/journal_linux.go` | 事件发布与订阅、多种事件后端 |
| **锁层** | `lock.go`, `lock/file/`, `lock/shm/` | 并发控制、文件锁和共享内存锁 |

### 关键依赖库

libpod 构建在 containers 社区维护的一系列底层库之上：

| 库 | 用途 |
|----|------|
| `containers/storage` | 容器镜像和容器层存储 |
| `containers/image` | 镜像拉取、推送、格式转换 |
| `containers/common` | 共享配置、工具函数 |
| `containers/buildah` | 容器镜像构建（Podman build 命令底层） |
| `containers/netavark` | 容器网络配置 |
| `containers/gvisor-tap-vsock` | VM 网络（用于 Mac/Windows） |
| `github.com/opencontainers/runtime-tools` | OCI 运行时规范工具 |

## REST API 设计

Podman 提供 REST API 供远程访问，API 服务在 `pkg/api/` 目录实现，支持两种 API 集合。

### API 服务结构

```text
┌─────────────────────────────────────────┐
│         pkg/api/server/                 │
│         HTTP 服务器与路由注册            │
├────────────────────┬────────────────────┤
│  handlers/compat/  │  handlers/libpod/  │
│  Docker 兼容 API   │  Podman 原生 API    │
└────────────────────┴────────────────────┘
```

### Docker 兼容 API

为了与现有 Docker 客户端生态兼容，Podman 实现了 Docker Engine API 的大部分接口：
- 路径前缀：`/v1.xx/`（对应 Docker API 版本）
- 支持 `docker-py`、`docker-compose` 等工具
- 可以通过 `DOCKER_HOST` 环境变量将 Docker 客户端指向 Podman

### Podman 原生 API

除了兼容 API，Podman 还提供了暴露自身高级功能的改进 API：
- 路径前缀：`/libpod/`
- 提供 Pod 管理、健康检查、systemd 集成等 Podman 特有功能
- 随 Podman 版本演进而保持语义化兼容

API 使用 gorilla/mux 作为 HTTP 路由器，定义了完整的 Swagger/OpenAPI 规范。

## Buildah 与 Skopeo 分工

Podman 与 Buildah、Skopeo 虽然是独立项目，但它们协同工作、共享底层库，共同构成完整的容器工具链。

### Buildah：专注镜像构建

Buildah 的核心职责是**构建** OCI 容器镜像：
- 提供 `buildah from`、`buildah run`、`buildah copy` 等细粒度构建命令
- 支持无 Dockerfile 的交互式镜像构建
- Podman 的 `podman build` 命令底层使用 Buildah 库
- Buildah 构建的镜像存储在 containers/storage 中，Podman 可直接使用

### Skopeo：专注镜像搬运

Skopeo 的核心职责是**搬运和检查**容器镜像：
- 支持在不同镜像仓库之间复制镜像（无需完整拉取到本地）
- 检查远程镜像的标签、配置、层信息
- 镜像签名和验证
- 删除远程镜像标签
- 支持多种镜像存储和传输格式

### 三者协作

```text
Buildah（构建镜像） ──→ containers/storage ──→ Podman（运行容器）
     │                     │                      │
     └─────────────────────┼──────────────────────┘
                           ▼
                    containers/image
                           │
                           ▼
                    Skopeo（镜像搬运）
```

- 三者共享 `containers/storage` 和 `containers/image` 库，镜像可以无缝互通
- Podman 专注于运行时，不重复实现镜像构建和搬运逻辑
- 每个工具专注做好一件事，遵循 Unix 哲学
- 可以独立使用，也可以组合使用

## 入口点与命令执行流程

### CLI 入口流程

Podman CLI 的执行流程从 `cmd/podman/main.go` 开始：

1. `reexec.Init()`：处理子进程重新执行（用于某些特殊场景，如用户命名空间内重新执行）
2. 设置日志配置
3. 处理 podmansh shell 模式
4. 通过空导入注册所有子命令包（`cmd/podman/...`）
5. `parseCommands()`：从 `registry.Commands` 注册表遍历命令，根据 EngineMode 过滤
6. 执行 rootCmd（Cobra 根命令）
7. `shutdown.Stop()`：命令执行完成后关闭 Runtime，清理资源

### 命令注册机制

所有子命令通过 `registry.Commands` 注册表管理：
- 每个命令包在 init() 函数中向注册表注册自己
- 注册时标记命令支持的 EngineMode（本地/远程/两者）
- 支持命令别名和分组
- 根命令定义在 `cmd/podman/root.go`，设置了 PersistentPreRunE 和 PersistentPostRunE 钩子

## 相关概念

- [Podman 简介](00-introduction.md) — 项目定位、rootless 特性与生态概览
- [快速上手](01-getting-started.md) — 安装方法与基础命令
- [Runtime 运行时](03-runtime.md) — Runtime 结构体、函数式选项与初始化流程详解
