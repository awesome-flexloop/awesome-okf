---
type: Concept
title: "daemonless 架构与分层代码结构"
description: "Podman 无守护进程设计哲学、Go 代码库四层架构（cmd→pkg/domain→libpod→containers依赖）、持久化存储与命令组织。"
tags: [podman, architecture, daemonless, go-codebase, layered-design, cobra]
generated: { by: "reference_agent/trae-cn", at: 2026-09-07T09:30:00+08:00 }
verified: { by: "process:grep-v", at: 2026-09-07T09:30:00+08:00 }
status: stable
stale_after: 2027-09-07
sources:
  - id: code-structure
    resource: /references/libpod-source.md
    title: libpod 核心与外部协同库源码
  - id: readme-docs
    resource: /references/readme-source.md
    title: README 与 docs/README 文档工程
---

# daemonless 架构与分层代码结构

Podman（POD MANager）是一款**无守护进程（daemonless）**的容器与 Pod 管理引擎，全程不依赖后台常驻的 dockerd 类守护进程，所有容器操作直接由用户进程调用 OCI runtime（crun/runc）完成。这一设计从根本上消除了单点故障与守护进程提权攻击面，是 Podman 与 Docker 最核心的架构差异。

## 设计哲学：无守护进程的三重优势

### 1. 进程隔离与安全
传统 Docker 架构中，所有容器操作都要通过 Unix socket 向 dockerd 发请求，dockerd 以 root 权限运行——这意味着任何能访问 socket 的用户都有机会通过 dockerd 提权。Podman 的 daemonless 架构让每个 `podman` 命令都是独立的 fork/exec 流程，容器进程直接挂在 `podman` 父进程下，无需中间守护进程转发。

### 2. Rootless 原生支持
daemonless 架构天然适配 rootless（无根）模式：普通用户可以在自己的 user namespace 中运行容器，无需 sudo、无需把用户加入 docker 组，从内核层面隔离了不同用户的容器运行时。

### 3. systemd 深度集成
没有守护进程意味着可以直接用 systemd 管理单个容器：`podman generate systemd` 为每个容器生成独立的 `.service` 单元，由 systemd 直接拉起、监控、重启容器；结合 `podman auto-update` 可以实现 systemd 级别的镜像滚动更新。

## Go 代码库四层架构（自顶向下）

```text
┌──────────────────────────────────────────────────┐
│  cmd/podman/           CLI 入口层                 │
│  (Cobra 命令树 + 标志定义 + 参数解析)              │
├──────────────────────────────────────────────────┤
│  pkg/domain/           业务逻辑层（双实现）         │
│  ├─ entities/          ContainerEngine/ImageEngine │
│  ├─ infra/abi/         本地 → 直接调 libpod        │
│  └─ infra/tunnel/      远程 → 调 pkg/bindings     │
├──────────────────────────────────────────────────┤
│  libpod/                容器核心层（Linux/FreeBSD） │
│  (容器/Pod/Volume 状态机 + SQLite/BoltDB 持久化)   │
├──────────────────────────────────────────────────┤
│  containers/*          外部核心依赖库              │
│  storage / image / buildah / common/libnetwork    │
└──────────────────────────────────────────────────┘
```

### 第一层：cmd/podman/ —— CLI 入口层
- 使用 [spf13/cobra](https://github.com/spf13/cobra) CLI 框架
- 每个子目录对应一个命令子树：`run/`、`build/`、`container/`、`image/`、`pod/`、`network/`、`volume/`、`machine/`、`kube/`、`quadlet/` 等
- **只负责**：参数解析、标志定义、帮助文案；不做任何业务逻辑
- 典型调用：`commandRun → registry.ContainerEngine().Command(registry.GetContext(), options)`

### 第二层：pkg/domain/ —— 业务逻辑层（关键双实现）
这是 Podman 最精巧的抽象层：**同一个业务接口有两个平行实现**，让本地与远程调用对 CLI 完全透明。

| 包 | 运行模式 | 实现方式 |
|----|---------|---------|
| `pkg/domain/entities/` | 接口定义 | `ContainerEngine`、`ImageEngine` 两大接口，每个 CLI 命令对应一个方法 |
| `pkg/domain/infra/abi/` | 本地模式 | 直接调用 `ic.Libpod.*`，零网络开销 |
| `pkg/domain/infra/tunnel/` | 远程模式 | 调用 `pkg/bindings/*` → HTTP REST → 远端 Podman API |

设计要点：
- `entities.CommandOptions` 结构体承载所有 CLI 解析后的参数
- CLI 层完全不知道是本地还是远程——由启动时的 `--url` / `--connection` / 环境变量切换实现
- `podman`（默认本地）与 `podman-remote`（纯远程客户端）两个二进制共享此层

### 第三层：libpod/ —— 容器核心层（Linux 独占）
- 定义了三大核心实体：`Container`、`Pod`、`Volume` 以及对应的 `Runtime` 管理器
- **持久化**：每个实例的状态存放在磁盘数据库中，支持 SQLite（默认）和 BoltDB（旧格式）
- 不做网络 I/O，不做 CLI 解析；纯逻辑函数库
- 向四大外部依赖库借势：
  - `containers/storage`：创建和挂载容器文件系统层
  - `containers/buildah`：Containerfile/Dockerfile 镜像构建
  - `containers/common/libnetwork`：容器网络（网桥、端口映射、DNS）
  - `containers/image`：镜像拉取、推送、导入导出（5 种传输协议）

### 第四层：containers/* 外部依赖
位于主仓库的 `vendor/github.com/containers/` 下，是 containers 组织维护的独立 Go 库。Podman **禁止直接修改 vendor/**，必须向上游提交 patch 后通过 `go mod vendor` 同步。

## 配套层：API 与客户端
- `pkg/api/`：REST API 服务端，基于 gorilla/mux 路由，对应 `podman system service` 启动
- `pkg/bindings/`：稳定的 Go HTTP 客户端，**API 稳定承诺**（ABI 不兼容需走废弃流程），被 podman-remote 和第三方工具调用
- `pkg/specgen/`：`SpecGenerator` 规格生成器——把各种 CLI flags/API 参数归并成统一的容器/Pod 规格描述，再传给 libpod 或 remote

## 9 大命令域总览

| 命令域 | 核心子命令 | 对应 Go 包 |
|-------|-----------|-----------|
| **container** | run/create/start/stop/exec/logs/inspect/ls/rm/prune | cmd/podman/container → libpod.container |
| **image** | pull/push/build/tag/ls/rm/prune/save/load/search | cmd/podman/image → buildah + containers/image |
| **pod** | create/start/stop/ps/rm/inspect/prune/logs | cmd/podman/pod → libpod.pod |
| **network** | create/ls/rm/connect/disconnect/reload/prune | cmd/podman/network → containers/common/libnetwork |
| **volume** | create/ls/rm/inspect/import/export/prune | cmd/podman/volume → libpod.volume |
| **secret** | create/ls/rm/inspect/exists | cmd/podman/secret → libpod.secret |
| **system** | info/df/prune/migrate/reset/service/connection | cmd/podman/system → runtime 元数据 |
| **manifest** | create/add/annotate/inspect/push/rm | cmd/podman/manifest → OCI 多架构镜像清单 |
| **kube / quadlet** | kube play/apply/down/generate / quadlet install/list | cmd/podman/{kube,quadlet} → K8s YAML + systemd |

## 相关概念
- [/concepts/01-commands.md](01-commands.md) — 核心命令分层与资源状态机
- [/concepts/02-rootless.md](02-rootless.md) — Rootless 安全模型详解
