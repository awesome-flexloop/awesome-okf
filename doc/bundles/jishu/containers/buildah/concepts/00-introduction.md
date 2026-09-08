---
type: Concept
title: "buildah 概述与 working container 概念"
description: "buildah 无守护进程镜像构建工具的核心定位、working container 生命周期、与 Podman container 的本质区别。"
tags: [buildah, working-container, oci-build, daemonless, podman-relationship]
generated: { by: "reference_agent/trae-cn", at: 2026-09-08T12:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-09-08T12:00:00+08:00 }
status: stable
stale_after: 2027-09-08
sources:
  - id: buildah-readme
    resource: /references/source.md
    title: buildah 源码与文档信源登记
---

# buildah 概述与 working container 概念

Buildah 是 [Podman Container Tools](https://github.com/containers/buildah)（CNCF Sandbox 项目）的核心组件之一，定位为**专注于构建 OCI 镜像的低层 coreutils 接口**。与 Podman 管理容器全生命周期不同，Buildah 只做一件事：从 Dockerfile/Containerfile 或手工操作构建 OCI 兼容镜像，然后将结果推送到注册表或本地存储。

## 与 Podman 的定位差异

```
┌─────────────────────────────────────────────────────────────────┐
│                    Podman Container Tools                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │  Buildah    │  │   Podman    │  │       Skopeo            │ │
│  │  构建镜像   │  │  运行管理   │  │    远程仓库操作          │ │
│  │             │  │             │  │                         │ │
│  │ from+run    │  │ run/start   │  │ copy/delete/inspect     │ │
│  │ commit      │  │ stop/kill   │  │ sync/list-tags          │ │
│  │ build       │  │ exec        │  │ standalone-sign         │ │
│  │ push        │  │ logs        │  │                         │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
│                                                                     │
│  共同基础：containers/storage（层存储）+ containers/image（传输）   │
└─────────────────────────────────────────────────────────────────┘
```

**核心区别**：
- Buildah container（working container）是**临时构建环境**，用完即弃，不可 `buildah start` 长期运行
- Podman container 是**长期运行的容器实例**，支持 `podman start/stop/exec/logs`
- 两者的存储命名空间隔离，互不可见

## working container 生命周期

Buildah 的核心抽象是 **working container（工作容器）**——一种特殊的容器，专为镜像构建而设计：

```
from → config → run → commit → push
  ↓       ↓      ↓        ↓        ↓
创建    配置修改 执行命令  保存为镜像 推送到注册表
working  环境   修改 FS   builder.   buildah
container            Save()  commit  push()
```

### 生命周期各阶段

| 阶段 | 命令 | 作用 |
|------|------|------|
| **创建** | `buildah from` | 基于基础镜像创建 working container |
| **配置** | `buildah config` | 设置 CMD/ENV/USER/WORKINGDIR 等镜像配置 |
| **操作** | `buildah run` | 在 working container 内执行命令（修改文件系统） |
| **挂载** | `buildah mount` | 手动挂载 working container 根文件系统 |
| **提交** | `buildah commit` | 将 working container 的状态写入镜像 |
| **推送** | `buildah push` | 将镜像推送到注册表 |
| **删除** | `buildah rm` | 清理 working container |

### working container 的存储隔离

```bash
# buildah 创建的 working container 在 buildah 存储命名空间
buildah containers
# 输出：CONTAINER  ID  BUILDER  IMAGE  NAME

# Podman 的容器在 podman 存储命名空间
podman ps
# 输出：CONTAINER ID  IMAGE  COMMAND  STATUS  PORTS

# 两者互不可见——这是 deliberate 的设计决策
```

## 22 个命令分 4 组

Buildah 的命令通过 Cobra 框架按 GroupID 分组组织（见 `cmd/buildah/main.go`）：

| GroupID | 常量值 | 命令数量 | 命令列表 |
|---------|--------|---------|---------|
| `groupImages` | "images" | 8 | images、pull、push、tag、rmi、manifest、info、prune |
| `groupContainers` | "containers" | 8 | containers、from、run、commit、config、build、mount、umount |
| `groupRegistries` | "registries" | 3 | login、logout、source |
| `groupSystem` | "system" | 3 | version、rpc、sftp |

## Go API 可被 vendored

Buildah 不仅是一个 CLI 工具，其核心 Go API（`github.com/containers/buildah`）可被其他工具 vendored 集成：

```go
import "github.com/containers/buildah"

// 以编程方式创建 working container
store, _ := buildah.GetStore(buildah.StoreOptions{})
builder, _ := buildah.NewBuilder(ctx, store, buildah.BuilderOptions{
    FromImage: "docker.io/library/alpine:latest",
    Container: "my-builder",
})

// 在 working container 内执行命令
builder.Run([]string{"apk", "add", "curl"})

// 提交为镜像
imageID, _ := builder.Commit(ctx, "myimage:latest", buildah.CommitOptions{})
```

这使得 Buildah 成为 CI/CD 流水线中镜像构建的**基础设施层**，而非仅限于命令行用户。

## 相关概念
- [/concepts/01-build-flow.md](01-build-flow.md) — build/commit/run 核心流水线详解
- [/examples/00-dockerfile-build.md](../examples/00-dockerfile-build.md) — Containerfile 构建完整示例
