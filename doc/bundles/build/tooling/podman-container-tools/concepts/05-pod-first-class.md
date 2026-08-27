---
type: Concept
title: Pod 一等公民
description: Pod作为独立资源模型解析、PodConfig字段详解、infra容器设计原理、命名空间共享策略与Kubernetes Pod概念对应关系
tags: [podman, concept, pod, infra-container, namespace, kubernetes, podState, restart-policy]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-26T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-26T00:00:00Z" }
status: stable
stale_after: 2027-08-26
sources:
  - id: podman-source
    resource: /references/podman-source.md
    title: Podman Container Tools 源码信源登记
---

## Pod 不是容器分组而是独立资源

在 Podman 中，Pod 是与 Container 平级的**一等公民资源**，而不是容器的简单分组或标签。这一设计直接继承自 Kubernetes 的 Pod 概念，但在无守护进程架构下有独特的实现方式。

### 一等公民的含义

Pod 作为独立资源意味着：
- Pod 有自己的 ID、名称、标签、生命周期
- Pod 有独立的配置（PodConfig）和运行时状态（podState）
- Pod 有独立的并发锁（lock.Locker）
- 对 Pod 的操作（创建/启动/停止/删除）与容器操作是分开的
- Pod 的存在不依赖于其中的业务容器，有自己的 infra 容器维持生命周期

### Pod 结构体定义

Pod 结构定义在 `libpod/pod.go:30-37`，字段设计与 Container 高度一致：

| 字段 | 类型 | 职责 |
|------|------|------|
| `config` | `*PodConfig` | Pod 静态配置，创建时确定 |
| `state` | `*podState` | Pod 运行时动态状态 |
| `valid` | `bool` | 标记 Pod 实例是否可用 |
| `runtime` | `*Runtime` | 反向引用所属 Runtime 实例 |
| `lock` | `lock.Locker` | 并发锁，防止多进程竞态操作 |

这种对称性反映了 libpod 的设计哲学：Container 和 Pod 都是 Runtime 管理的顶级资源，各自管理自己的生命周期和状态同步。

## updatePod()：Pod 状态同步

与 Container 的 `syncContainer()` 对应，Pod 操作访问状态前必须调用 `updatePod()`。源码在 `libpod/pod.go:20-28` 处有明确注释要求。

### 为什么需要 updatePod()

同样基于无守护进程架构的考虑：
- 多个 CLI 进程可以同时操作同一个 Pod
- Pod 的容器状态可能被独立操作改变（如单独停止 Pod 内某个容器）
- infra 容器可能独立退出
- Pod 状态存储在 BoltDB/SQLite 中，内存中的 state 可能过期

`updatePod()` 从底层状态存储重新读取 Pod 的最新状态，包括：
- Pod 内各容器的实际运行状态
- cgroup 路径是否仍然有效
- infra 容器是否仍在运行
- 刷新 podState 的 CgroupPath 和 InfraContainerID

## PodConfig 详解

PodConfig 结构定义在 `libpod/pod.go:40-98`，包含 Pod 的全部静态配置。

### 身份与元数据

| 字段 | 类型 | 说明 |
|------|------|------|
| `ID` | `string` | Pod 唯一标识符，由库自动生成 |
| `Name` | `string` | Pod 可读名称，用户可指定或自动生成 |
| `Namespace` | `string` | Pod 所属命名空间，用于分组隔离 |
| `Hostname` | `string` | Pod 主机名，Pod 内容器共享此主机名 |
| `Labels` | `map[string]string` | 用户自定义标签键值对 |
| `CreatedTime` | `time.Time` | Pod 创建时间 |
| `CreateCommand` | `[]string` | 创建 Pod 时的完整命令行，用于审计 |
| `LockID` | `uint32` | 锁管理器分配的锁 ID |

### Cgroup 配置

| 字段 | 类型 | 说明 |
|------|------|------|
| `CgroupParent` | `string` | cgroup 父路径，Pod 级资源限制在此 cgroup 下设置 |
| `UsePodCgroup` | `bool` | 是否使用 Pod 级 cgroup，启用后 Pod 内所有容器加入同一 cgroup |

### 命名空间共享策略

命名空间共享是 Pod 的核心功能，PodConfig 通过一系列 `UsePod*NS` 布尔字段控制哪些命名空间在 Pod 内共享：

| 字段 | 对应命名空间 | 说明 |
|------|-------------|------|
| `UsePodPIDNS` | PID Namespace | Pod 内容器共享进程 ID 空间，容器间可通过 PID 互相发送信号 |
| `UsePodIPCNS` | IPC Namespace | Pod 内容器共享进程间通信资源（信号量、消息队列、共享内存） |
| `UsePodNetNS` | Network Namespace | Pod 内容器共享网络栈（IP、端口、路由、localhost） |
| `UsePodMountNS` | Mount Namespace | Pod 内容器共享挂载点视图 |
| `UsePodUserNS` | User Namespace | Pod 内容器共享用户/组映射 |
| `UsePodUTSNS` | UTS Namespace | Pod 内容器共享主机名和 NIS 域名 |
| `UsePodCgroupNS` | Cgroup Namespace | Pod 内容器共享 cgroup 视图 |

默认情况下（创建 Pod 时不显式指定），`UsePodNetNS` 和 `UsePodUTSNS` 默认启用，其他命名空间按需配置。这与 Kubernetes 的默认行为一致：Pod 内容器总是共享网络和 UTS 命名空间。

### Infra 容器配置

| 字段 | 类型 | 说明 |
|------|------|------|
| `HasInfra` | `bool` | 是否创建 infra 容器维持共享命名空间 |
| `InfraContainerID` | `string` | infra 容器的 ID（存储在 config 中，state 中也有记录） |
| `ServiceContainerID` | `string` | 服务容器 ID（用于特殊的 service pod 场景） |

### 重启与退出策略

| 字段 | 类型 | 说明 |
|------|------|------|
| `ExitPolicy` | `string` | Pod 退出策略，控制容器退出后 Pod 的行为 |
| `RestartPolicy` | `string` | 重启策略（no/on-failure/always），与 Kubernetes 重启策略概念一致 |
| `RestartRetries` | `uint` | 已重启次数，用于重启退避计数 |

### 资源限制

| 字段 | 类型 | 说明 |
|------|------|------|
| `ResourceLimits` | `*LinuxResources` | Pod 级资源限制（CPU、内存、PID 等），使用 cgroup 实施 |

## 为什么需要 Infra 容器

Infra（基础设施）容器是 Pod 实现命名空间共享的关键机制，理解 infra 容器是理解 Pod 的核心。

### 命名空间生命周期问题

Linux 命名空间的生命周期规则：
- 命名空间由最后一个持有该命名空间引用的进程维持
- 当最后一个进程退出或离开命名空间时，命名空间被销毁
- 命名空间被销毁后，新进程无法加入该命名空间

如果 Pod 没有 infra 容器，会出现以下问题：
1. 创建 Pod 后启动第一个业务容器 A，创建并持有共享命名空间
2. 启动第二个业务容器 B，加入 A 的命名空间
3. 如果 A 因为某种原因退出（如崩溃、被停止），共享命名空间随 A 一起销毁
4. B 虽然仍在运行，但新的容器无法再加入该 Pod 的网络等共享命名空间
5. Pod 变得不一致，网络隔离被破坏

### Infra 容器的解决方案

Infra 容器是一个**极轻量**的容器，它的唯一作用是**持有 Pod 级共享命名空间的生命周期**：

```text
┌─────────────────────────────────────────────┐
│                   Pod                       │
│                                             │
│  ┌─────────────┐                            │
│  │ infra 容器  │ ◄── 永远第一个启动          │
│  │  (pause)    │ ◄── 持有所有共享命名空间     │
│  │             │ ◄── 不做任何实际工作         │
│  └──────┬──────┘                            │
│         │ 共享命名空间                       │
│    ┌────┴────┬─────────┐                    │
│    ▼         ▼         ▼                    │
│ ┌──────┐ ┌──────┐ ┌──────┐                  │
│ │ 容器A│ │ 容器B│ │ 容器C│ ◄── 业务容器      │
│ │ app1 │ │ app2 │ │ side│                  │
│ └──────┘ └──────┘ └──────┘                  │
└─────────────────────────────────────────────┘
```

### Infra 容器的特征

- **镜像极小**：通常使用 `k8s.gcr.io/pause` 或 Podman 内置的极简 pause 镜像
- **进程极简单**：只执行一个无限循环 `pause()` 系统调用，不做任何实际工作
- **资源占用极低**：占用内存可以忽略不计，不消耗 CPU
- **生命周期最长**：Pod 内第一个启动、最后一个停止
- **不可见**：默认 `podman ps` 不显示 infra 容器（使用 `--all` 可查看）
- **持有命名空间**：创建 Pod 时创建共享命名空间，infra 容器加入并持有它们
- **其他容器加入**：Pod 内的业务容器创建时加入 infra 容器持有的命名空间

这种设计确保：即使所有业务容器都退出，只要 infra 容器还在，Pod 的共享命名空间就仍然存在，新启动的容器可以正常加入。

## podState 运行时状态

podState 结构定义在 `libpod/pod.go:101-107`，字段比 ContainerState 简洁得多。

| 字段 | 类型 | 说明 |
|------|------|------|
| `CgroupPath` | `string` | Pod 级 cgroup 路径，用于 Pod 级资源监控和限制 |
| `InfraContainerID` | `string` | 当前 infra 容器 ID（可能因重建而变化） |

podState 比 ContainerState 简单的原因：
- Pod 本身不是一个运行中的进程，它只是容器的组织边界
- Pod 的实际状态由其 infra 容器和业务容器的状态聚合得出
- CgroupPath 是 Pod 级资源管理的关键路径
- InfraContainerID 用于快速定位 infra 容器

## Pod 生命周期管理

Pod 的生命周期管理围绕 infra 容器展开，命令操作覆盖完整的 Pod 生命周期。

### Pod 命令集

pods/ 子目录下有 16 个命令管理 Pod 生命周期：

| 分类 | 命令 | 说明 |
|------|------|------|
| **生命周期** | `create` | 创建 Pod（含 infra 容器） |
| | `start` | 启动 Pod 及所有容器 |
| | `stop` | 停止 Pod 及所有容器 |
| | `restart` | 重启 Pod |
| | `rm` | 删除 Pod 及所有容器 |
| | `clone` | 克隆现有 Pod |
| | `kill` | 发送信号到 Pod 内所有容器 |
| **状态查询** | `ps` | 列出 Pod |
| | `inspect` | 查看 Pod 详细配置和状态 |
| | `stats` | Pod 资源使用统计（CPU/内存/网络/IO） |
| | `top` | 查看 Pod 内所有容器进程 |
| | `logs` | 查看 Pod 内容器日志 |
| | `exists` | 检查 Pod 是否存在 |
| **状态控制** | `pause` | 暂停 Pod 内所有容器 |
| | `unpause` | 恢复 Pod 内所有容器 |
| **清理** | `prune` | 清理已停止的 Pod |

### Pod 创建流程

```text
podman pod create
       │
       ▼
┌─────────────────────────────────────┐
│ 1. 生成 Pod ID 和 Name              │
│ 2. 创建 PodConfig                   │
│ 3. 创建 infra 容器（pause 进程）    │
│ 4. infra 容器创建并持有共享命名空间 │
│ 5. 记录 CgroupPath                  │
│ 6. 持久化 Pod 配置和状态            │
└─────────────────────────────────────┘
       │
       ▼
   Pod 已创建，可以添加容器
```

### 添加容器到 Pod

使用 `podman create --pod <pod-id/name> ...` 或 `podman run --pod ...` 将容器加入 Pod：
1. 查找目标 Pod 的 infra 容器
2. 获取 infra 容器持有的共享命名空间路径
3. 新容器配置为加入这些命名空间
4. 新容器的网络等配置由 Pod 统一管理

## 与 Kubernetes Pod 概念对应

Podman Pod 与 Kubernetes Pod 共享相同的核心概念，但有实现差异。

### 概念对应关系

| 概念 | Kubernetes Pod | Podman Pod |
|------|----------------|------------|
| **共享网络** | Pod 内所有容器共享 IP 和端口空间 | `UsePodNetNS=true`，通过 infra 容器持有 netns |
| **共享主机名** | Pod 主机名对所有容器相同 | `UsePodUTSNS=true`，UTS 命名空间共享 |
| **共享 IPC** | 默认共享 IPC 命名空间 | `UsePodIPCNS=true`（可选） |
| **共享 PID** | 通过 `shareProcessNamespace: true` 启用 | `UsePodPIDNS=true`（可选） |
| **Pause 容器** | 每个 Pod 有 pause 容器 | infra 容器（HasInfra=true） |
| **重启策略** | Always/OnFailure/Never | RestartPolicy 字段，语义一致 |
| **资源限制** | Pod 级 resources.requests/limits | ResourceLimits 字段，通过 cgroup 实施 |
| **标签** | metadata.labels | Labels map |
| **生命周期** | Pending/Running/Succeeded/Failed | 通过容器状态聚合判断 |

### 关键差异

| 方面 | Kubernetes | Podman |
|------|------------|--------|
| **调度** | 由 kube-scheduler 调度到 Node | 本机直接创建，无调度 |
| **网络** | CNI 插件分配 IP，kube-proxy 处理 Service | netavark/CNI 配置网络，无 Service 概念 |
| **存储** | PV/PVC/StorageClass 抽象 | 直接使用 volumes 和 bind mount |
| **探针** | livenessProbe/readinessProbe | healthcheck（容器级） |
| **Init 容器** | initContainers 按顺序执行 | 通过普通容器 + 启动顺序模拟 |

### podman kube play

Podman 提供 `podman kube play` 命令，可以直接运行 Kubernetes YAML 定义的 Pod：
- 解析 Kubernetes Pod YAML
- 转换为 Podman Pod 配置
- 创建对应 Pod 和容器
- 支持 Pod、Deployment、PersistentVolumeClaim 等资源类型
- 这使得本地开发和测试 Kubernetes 工作负载变得简单

```bash
podman kube play pod.yaml
```bash

## 相关概念

- [容器基础](04-container-basics.md) — Container结构体、syncContainer同步机制与Linux命名空间详解
- [Runtime运行时](03-runtime.md) — Runtime结构体与容器/Pod管理入口
- [网络与存储卷](09-network-volume.md) — 网络命名空间配置、CNI/netavark网络栈与Volume管理
- [架构概览](02-architecture-overview.md) — 三层核心抽象与双引擎模式
