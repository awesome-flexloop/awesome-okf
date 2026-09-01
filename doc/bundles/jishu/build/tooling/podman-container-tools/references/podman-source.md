---
type: Reference
title: Podman Container Tools 源码信源登记
description: Podman容器工具集源码路径、版本、核心模块清单与项目结构说明
tags: [podman, containers, OCI, source, reference]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-26T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-26T00:00:00Z" }
status: stable
stale_after: 2027-08-26
sources: []
---

## 源码位置

- **本地路径**：`external/dao/action/podman-container-tools/`
- **上游项目**：Podman 容器工具集（Containers 组织）
- **核心仓库**：Podman v6（Go 模块：`go.podman.io/podman/v6`）
- **许可证**：Apache 2.0

## 子项目清单

podman-container-tools 是一个容器工具生态 monorepo，包含以下子项目：

| 子目录 | 用途 | 主要语言 |
|--------|------|---------|
| `podman/` | Podman 核心引擎——无守护进程OCI容器管理工具 | Go |
| `automation/` | CI自动化脚本集合 | Shell/Python |
| `community/` | 社区治理、贡献指南、会议记录 | Markdown |
| `image_build/` | 官方容器镜像构建（Podman/Buildah/Skopeo/AIO） | Containerfile/Shell |
| `podman-machine-os/` | Podman Machine 虚拟机磁盘镜像构建 | Shell/Go |

## Podman 核心模块清单（podman/）

### cmd/podman/ - CLI入口与命令

| 路径 | 说明 |
|------|------|
| `cmd/podman/main.go` | CLI主入口，reexec初始化、命令解析、执行 |
| `cmd/podman/root.go` | rootCmd定义、初始化钩子、Engine关闭 |
| `cmd/podman/containers/` | 容器操作命令（run/start/stop/exec/ps等36个命令） |
| `cmd/podman/images/` | 镜像操作命令（pull/push/build/rmi等27个命令） |
| `cmd/podman/pods/` | Pod操作命令（create/start/stop/ps等16个命令） |
| `cmd/podman/networks/` | 网络操作命令（create/connect/ls等11个命令） |
| `cmd/podman/volumes/` | 卷操作命令（create/ls/mount等13个命令） |
| `cmd/podman/system/` | 系统命令（info/events/df/service/connection等） |
| `cmd/podman/machine/` | 虚拟机管理命令（init/start/ssh/os等） |
| `cmd/podman/kube/` | Kubernetes集成（play/generate/apply/down） |
| `cmd/podman/manifest/` | 清单列表操作（add/push/remove等） |
| `cmd/podman/secrets/` | 密钥管理（create/ls/rm等） |
| `cmd/podman/quadlet/` | Quadlet systemd单元生成 |

### libpod/ - 核心容器库（本地模式）

| 路径 | 说明 |
|------|------|
| `libpod/runtime.go` | Runtime核心结构定义与NewRuntime创建 |
| `libpod/container.go` | Container结构定义 |
| `libpod/pod.go` | Pod结构定义 |
| `libpod/volume.go` | Volume结构定义 |
| `libpod/state.go` | State接口（BoltDB/SQLite双实现） |
| `libpod/boltdb_state.go` | BoltDB状态存储实现 |
| `libpod/sqlite_state.go` | SQLite状态存储实现 |
| `libpod/oci.go` | OCI运行时交互（conmon监控） |
| `libpod/events/` | 事件系统 |
| `libpod/lock/` | 锁机制（file/shm） |
| `libpod/define/` | 常量与类型定义 |

### pkg/ - 可复用包

| 路径 | 说明 |
|------|------|
| `pkg/api/` | REST API服务（Docker兼容API+libpod原生API） |
| `pkg/bindings/` | HTTP客户端绑定 |
| `pkg/domain/` | 业务逻辑层（entities接口+abi本地实现+tunnel远程实现） |
| `pkg/specgen/` | OCI规范生成器 |
| `pkg/machine/` | 虚拟机管理（QEMU/WSL/Apple HV） |
| `pkg/systemd/` | systemd集成与Quadlet |
| `pkg/rootless/` | 无root运行支持 |
| `pkg/auth/` | 认证功能 |
| `pkg/util/` | 通用工具函数 |

## 核心数据结构公开API

### Runtime相关（libpod/runtime.go）

- `type RuntimeOption func(*Runtime) error`
- `func NewRuntime(ctx context.Context, options ...RuntimeOption) (*Runtime, error)`
- Runtime字段：config, state, store, imageContext, defaultOCIRuntime, network, lockManager, eventer, secretsManager

### Container相关（libpod/container.go）

- Container操作前必须调用`syncContainer()`同步状态
- ContainerState字段：State, ConfigPath, RunDir, Mounted, Mountpoint, StartedTime, FinishedTime, ExitCode

### Pod相关（libpod/pod.go）

- Pod操作前必须调用`updatePod()`同步状态
- PodConfig字段：ID, Name, Namespace, Hostname, Labels, UsePod*NS, HasInfra, RestartPolicy, ResourceLimits
- podState字段：CgroupPath, InfraContainerID

## 核心依赖

| 依赖 | 用途 |
|------|------|
| containers/buildah | OCI镜像构建 |
| containers/image | 容器镜像管理 |
| containers/storage | 容器存储 |
| containers/common | 共享工具库 |
| containers/netavark | 容器网络 |
| github.com/spf13/cobra | CLI框架 |
| github.com/sirupsen/logrus | 日志 |
| go.etcd.io/bbolt | BoltDB状态存储 |
| github.com/mattn/go-sqlite3 | SQLite状态存储 |

## 相关概念

- [Podman简介](../concepts/00-introduction.md)
- [架构概览](../concepts/02-architecture-overview.md)
- [Runtime运行时](../concepts/03-runtime.md)
