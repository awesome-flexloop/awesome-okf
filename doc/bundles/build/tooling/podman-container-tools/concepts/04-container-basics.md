---
type: Concept
title: 容器基础
description: Container结构体解析、syncContainer同步机制、ContainerState状态字段、7种Linux命名空间隔离与容器生命周期管理
tags: [podman, concept, container, libpod, linux-namespace, oci, lifecycle, syncContainer]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-26T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-26T00:00:00Z" }
status: stable
stale_after: 2027-08-26
sources:
  - id: podman-source
    resource: /references/podman-source.md
    title: Podman Container Tools 源码信源登记
---

## Container 结构体解析

Container 是 libpod 库中表示单个 OCI 容器的核心结构体，定义在 `libpod/container.go`。它聚合了容器的静态配置、运行时状态、并发控制锁以及对所属 Runtime 的反向引用。

Container 结构体定义位置：`libpod/container.go:96-128`，核心字段按职责分类如下：

| 字段 | 类型 | 职责 |
|------|------|------|
| `config` | `*ContainerConfig` | 容器静态配置，包含镜像、命令、环境变量、挂载点、资源限制等创建时确定的信息 |
| `state` | `*ContainerState` | 容器运行时状态，包含当前状态、PID、挂载点、启动/结束时间、退出码等动态信息 |
| `lock` | `lock.Locker` | 并发锁，支持文件锁和共享内存锁两种实现，防止多进程并发操作同一容器导致竞态 |
| `runtime` | `*Runtime` | 反向引用所属的 Runtime 实例，所有底层操作（存储、网络、OCI运行时）都通过 Runtime 进行 |
| `ociRuntime` | `OCIRuntime` | 当前容器使用的 OCI 运行时实例（默认 crun） |
| `batched` | `bool` | 标记是否处于批量操作模式，减少状态同步次数 |
| `valid` | `bool` | 标记 Container 实例是否可用，防止在已删除/无效的容器上操作 |

### config 与 state 的分离设计

Container 采用配置与状态分离的设计：
- **config（ContainerConfig）**：容器创建时确定，生命周期内通常不可变，存储在 BoltDB/SQLite 中
- **state（ContainerState）**：容器运行时动态变化，每次操作前需从底层存储同步最新值

这种分离使得配置和状态可以独立管理，也便于状态的快速刷新和持久化。

## syncContainer()：状态同步机制

源码在 `libpod/container.go:87-95` 处有明确注释：所有访问状态的 Container 操作必须以 `syncContainer()` 开头。

### 为什么必须先调用 syncContainer()

Podman 采用无守护进程架构，这意味着：
- 没有常驻的 dockerd 持有内存中的容器状态
- 多个 Podman CLI 进程可以同时操作同一容器（如一个进程执行 `podman run`，另一个执行 `podman stop`）
- 容器状态存储在 BoltDB/SQLite 数据库中，不在进程内存里
- conmon 进程独立于 CLI 存在，容器进程可能在 CLI 不知情的情况下退出

如果直接使用内存中的 `container.state`，可能读取到过期数据，导致操作失败或状态不一致。

### syncContainer() 的作用

`syncContainer()` 方法从底层状态存储（BoltDB/SQLite）重新读取容器的最新状态，更新内存中的 `container.state` 字段。它还会：
- 检查容器的 `valid` 标记
- 验证容器锁是否正确持有
- 刷新与 OCI 运行时相关的状态信息
- 处理批量操作优化（`batched` 模式下可延迟同步）

典型用法模式：

```go
func (c *Container) Start(ctx context.Context) error {
    c.lock.Lock()
    defer c.lock.Unlock()

    if err := c.syncContainer(); err != nil {
        return err
    }

    // 基于最新状态执行操作
    if c.state.State == define.ContainerStateRunning {
        return define.ErrCtrStateInvalid
    }

    // ... 执行启动逻辑
}
```bash

## ContainerState 字段详解

ContainerState 结构定义在 `libpod/container.go:132-150`，记录容器当前运行时的完整动态信息。

| 字段 | 类型 | 说明 |
|------|------|------|
| `State` | `define.ContainerStatus` | 容器当前状态枚举值 |
| `ConfigPath` | `string` | 容器配置文件路径（OCI bundle 配置） |
| `RunDir` | `string` | 运行时临时目录路径（存放 PID 文件、socket 等） |
| `Mounted` | `bool` | 容器根文件系统是否已挂载 |
| `Mountpoint` | `string` | 容器根文件系统挂载点路径 |
| `StartedTime` | `time.Time` | 容器启动时间 |
| `FinishedTime` | `time.Time` | 容器结束时间 |
| `ExitCode` | `int32` | 容器退出码（仅在已停止状态有效） |
| `PID` | `int` | 容器主进程 PID（仅在运行状态有效） |
| `ConmonPID` | `int` | conmon 监控进程 PID |
| `BindMounts` | `[]string` | 绑定挂载列表 |
| `Mountpoint` | `string` | 根文件系统挂载点 |

### ContainerStatus 状态枚举

容器状态定义在 `libpod/define/containerstate.go`，主要状态包括：

| 状态 | 说明 |
|------|------|
| `ContainerStateConfigured` | 已创建但尚未初始化 |
| `ContainerStateCreated` | 已创建，OCI 规范已生成，可启动 |
| `ContainerStateRunning` | 正在运行 |
| `ContainerStateStopped` | 已停止（可重启） |
| `ContainerStateExited` | 已退出（退出码可用） |
| `ContainerStatePaused` | 已暂停（通过 cgroup freezer） |
| `ContainerStateRemoving` | 正在删除中 |

## Linux 命名空间隔离

Linux 命名空间是容器隔离的核心技术基础。Podman 支持 7 种 Linux 命名空间，通过 `LinuxNS` 类型枚举表示，定义在 `libpod/container.go:46-65`。

### 七种命名空间

| 枚举值 | 命名空间 | 隔离内容 |
|--------|----------|----------|
| `IPCNS` | IPC Namespace | 进程间通信资源（信号量、消息队列、共享内存） |
| `MountNS` | Mount Namespace | 文件系统挂载点视图 |
| `NetNS` | Network Namespace | 网络设备、IP地址、端口、路由表、防火墙 |
| `PIDNS` | PID Namespace | 进程 ID 编号空间，容器内 PID 1 独立于宿主机 |
| `UserNS` | User Namespace | 用户和组 ID 映射，rootless 容器的核心机制 |
| `UTSNS` | UTS Namespace | 主机名和 NIS 域名 |
| `CgroupNS` | Cgroup Namespace | 控制组视图，容器看到的 cgroup 根是自己的 cgroup 路径 |

### 命名空间与 Pod 的关系

Pod 内的容器可以共享命名空间：
- Pod 级别可以设置 `UsePodPIDNS`、`UsePodIPCNS`、`UsePodNetNS` 等标志
- 启用共享时，Pod 内的容器加入同一个命名空间
- infra 容器的作用就是持有这些共享命名空间的生命周期

## 容器生命周期

容器从创建到删除经历一系列明确的状态转换，每个状态转换对应特定的 CLI 命令。

### 生命周期状态机

```text
           podman create
                │
                ▼
        ┌────────────────┐
        │    Created     │ ◄─── podman init（可选：提前初始化）
        └───────┬────────┘
                │ podman start
                ▼
        ┌────────────────┐
   ┌──► │    Running     │ ◄─── podman restart（停止后启动）
   │    └───┬────────┬───┘
   │        │        │
   │  podman pause   │ podman stop / 进程退出
   │        │        │
   │        ▼        ▼
   │  ┌─────────┐ ┌──────────────┐
   │  │ Paused  │ │   Stopped    │
   │  └────┬────┘ └──────┬───────┘
   │       │ podman      │ podman restart
   │       │ unpause     │
   └───────┘             │
                         ▼
                  ┌──────────────┐
                  │    Exited    │
                  └──────┬───────┘
                         │ podman rm
                         ▼
                  ┌──────────────┐
                  │   Removed    │
                  └──────────────┘
```bash

### 关键阶段说明

1. **创建（Created）**：`podman create` 创建容器，分配资源，生成 OCI 规范，但不启动进程
2. **初始化（Initialized）**：`podman init`（可选）提前完成挂载、网络配置等初始化工作
3. **运行（Running）**：`podman start` 启动容器主进程，conmon 开始监控
4. **暂停（Paused）**：`podman pause` 通过 cgroup freezer 冻结容器所有进程，不释放资源
5. **停止（Stopped）**：`podman stop` 发送信号终止容器进程，容器可被重启
6. **退出（Exited）**：容器进程已终止，退出码可用，资源尚未完全清理
7. **删除（Removed）**：`podman rm` 删除容器，清理存储层、网络配置、状态记录

### podman run = create + start

`podman run` 命令是 `podman create` + `podman start` 的便捷组合，还支持前台交互模式（`-it`）。

## 容器与 OCI 运行时关系

Container 结构体本身不直接执行容器进程，而是通过 OCI 运行时接口（OCIRuntime）与底层 OCI 运行时交互。

### 交互层次

```text
┌─────────────────────────────────────────┐
│            Container 结构体             │
│  config / state / lock / runtime        │
└──────────────┬──────────────────────────┘
               │ 调用
               ▼
┌─────────────────────────────────────────┐
│         OCI Runtime 接口                │
│  createContainer / startContainer /...  │
└──────────────┬──────────────────────────┘
               │ fork/exec
               ▼
┌─────────────────────────────────────────┐
│            conmon 进程                  │
│  监控容器IO、日志、退出码                │
└──────────────┬──────────────────────────┘
               │ fork/exec
               ▼
┌─────────────────────────────────────────┐
│       OCI Runtime (crun/runc)           │
│  创建命名空间、挂载、启动容器进程        │
└──────────────┬──────────────────────────┘
               │ clone
               ▼
┌─────────────────────────────────────────┐
│          容器进程 (PID 1)               │
│  用户指定的 entrypoint/cmd              │
└─────────────────────────────────────────┘
```bash

### 关键交互流程

1. Container.Start() 调用 ociRuntime.CreateContainer() 生成 OCI bundle
2. OCI 运行时（crun）创建容器进程，设置命名空间和 cgroup
3. conmon 进程成为容器进程的父进程，负责监控
4. Container 状态更新为 Running，记录 PID 和启动时间
5. 容器退出时，conmon 捕获退出码并写入状态文件
6. syncContainer() 可以感知到容器已退出，更新 ContainerState

## 相关概念

- [Pod一等公民](/concepts/05-pod-first-class.md) — Pod独立资源模型、infra容器与命名空间共享机制
- [Runtime运行时](/concepts/03-runtime.md) — Runtime结构体、函数式选项模式与NewRuntime创建流程
- [架构概览](/concepts/02-architecture-overview.md) — 无守护进程架构与三层核心抽象
- [CLI命令结构](/concepts/06-cli-structure.md) — Cobra框架、命令注册表与EngineMode过滤
- [容器操作命令](/concepts/07-container-commands.md) — 36个容器命令的分类用法详解
