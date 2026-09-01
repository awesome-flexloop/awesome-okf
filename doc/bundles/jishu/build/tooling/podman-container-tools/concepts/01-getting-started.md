---
type: Concept
title: 快速上手
description: Podman各平台安装指南、安装验证方法、运行第一个容器及基础命令速览
tags: [podman, concept, getting-started, installation, hello-world, cli]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
verified: { by: "human:trae-agent", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
sources:
  - id: podman-source
    resource: /references/podman-source.md
    title: Podman 源码参考
---

## 平台安装方式

Podman 支持 Linux、macOS 和 Windows 三大平台，不同平台的安装方式有所差异。

### Linux 原生安装

Linux 是 Podman 的原生支持平台，无需额外的虚拟机层。Podman 可以直接利用 Linux 内核的 cgroup 和 namespace 特性运行容器。

在主流 Linux 发行版上，Podman 通常可以通过系统包管理器直接安装：

```bash
# Fedora/RHEL/CentOS
sudo dnf install -y podman

# Ubuntu/Debian
sudo apt-get update && sudo apt-get install -y podman

# Arch Linux
sudo pacman -S podman
```

Linux 平台支持 rootful 和 rootless 两种运行模式。rootless 模式是推荐的默认方式，使用用户命名空间提供更强的安全隔离。

### macOS 安装

macOS 上 Podman 通过管理的轻量级虚拟机运行容器。Podman 提供了 `podman machine` 子命令来管理虚拟机生命周期。

推荐使用 Homebrew 安装：

```bash
brew install podman
```

安装完成后需要初始化并启动虚拟机：

```bash
podman machine init
podman machine start
```

### Windows 安装

Windows 上 Podman 通过 Podman 管理的虚拟机运行，支持 WSL2 后端。可以通过以下方式安装：

- 使用官方 Windows 安装包
- 通过 Chocolatey 或 Scoop 等包管理器
- 在 WSL2 发行版内直接安装 Linux 版本

安装后同样需要使用 `podman machine` 初始化并启动虚拟机环境。`pkg/machine/` 目录包含了各平台虚拟机管理的实现代码，支持 QEMU、Apple HV、WSL2 等多种虚拟化后端。

## 验证安装

安装完成后，通过以下命令验证 Podman 是否正确安装并可用。

### 查看版本信息

使用 `podman --version` 或 `podman version` 查看版本信息：

```bash
podman --version
```

该命令输出版本号，对应源码中 `version.Version.String()` 绑定到 rootCmd 的 Version 字段。

### 查看系统信息

使用 `podman info` 查看系统和 Podman 的详细配置信息：

```bash
podman info
```

该命令返回的信息包括：
- 主机信息（操作系统、内核版本、CPU、内存）
- 存储配置（存储驱动、存储路径）
- OCI 运行时配置（默认运行时路径）
- 网络配置
- 注册的容器镜像仓库

`podman info` 是排查安装问题时的首要命令，它会触发 Runtime 初始化流程并输出完整的配置状态。

## 运行第一个容器

使用官方 `hello-world` 镜像验证容器运行功能：

```bash
podman run hello-world
```

该命令的执行流程包括：
1. CLI 通过 Cobra 框架解析 `run` 子命令
2. 检查本地是否存在 `hello-world` 镜像，不存在则从默认仓库拉取
3. 创建容器配置（通过 `pkg/specgen/` 生成 OCI 规范）
4. 调用 OCI 运行时（默认为 crun）启动容器
5. 容器输出欢迎信息后退出

首次运行时，Podman 会自动拉取镜像，这是正常现象。成功输出欢迎信息说明容器运行时工作正常。

### 运行交互式容器

可以运行一个交互式的 Alpine Linux 容器进行体验：

```bash
podman run -it alpine sh
```

其中：
- `-i`：保持标准输入打开（interactive）
- `-t`：分配一个伪终端（tty）
- `alpine`：使用轻量级 Alpine Linux 镜像
- `sh`：容器启动后执行的命令

在容器内可以执行 `ls`、`cat /etc/os-release` 等命令验证环境，输入 `exit` 退出容器。

## 基础命令速览

Podman 的 CLI 结构与 Docker 高度兼容，大多数 Docker 命令可以直接替换为 `podman`。命令通过 `cmd/podman/` 目录下的子命令包注册，使用 Cobra 框架管理。

### 容器生命周期命令

| 命令 | 功能 |
|------|------|
| `podman run <image>` | 创建并启动一个新容器 |
| `podman start <container>` | 启动已停止的容器 |
| `podman stop <container>` | 停止运行中的容器 |
| `podman restart <container>` | 重启容器 |
| `podman rm <container>` | 删除容器 |
| `podman ps` | 列出运行中的容器（`-a` 显示所有容器） |
| `podman exec -it <container> <cmd>` | 在运行中的容器内执行命令 |
| `podman logs <container>` | 查看容器日志 |
| `podman inspect <container>` | 查看容器详细配置信息 |

容器相关命令的实现在 `cmd/podman/containers/` 目录下。

### 镜像管理命令

| 命令 | 功能 |
|------|------|
| `podman pull <image>` | 拉取镜像到本地 |
| `podman push <image>` | 推送镜像到仓库 |
| `podman images` | 列出本地镜像 |
| `podman rmi <image>` | 删除本地镜像 |
| `podman build <dir>` | 使用 Containerfile/Dockerfile 构建镜像 |
| `podman tag <image> <new-tag>` | 为镜像添加标签 |

镜像相关命令的实现在 `cmd/podman/images/` 目录下，底层使用 containers/image 和 Buildah 库。

### Pod 管理命令

Pod 是 Podman 的特色概念，允许将多个容器作为一组管理：

| 命令 | 功能 |
|------|------|
| `podman pod create` | 创建新的 Pod |
| `podman pod start <pod>` | 启动 Pod 中的所有容器 |
| `podman pod stop <pod>` | 停止 Pod 中的所有容器 |
| `podman pod rm <pod>` | 删除 Pod |
| `podman pod ps` | 列出所有 Pod |

Pod 相关命令的实现在 `cmd/podman/pods/` 目录下。

### 系统与帮助命令

| 命令 | 功能 |
|------|------|
| `podman info` | 查看系统信息 |
| `podman version` | 查看版本信息 |
| `podman help <command>` | 查看命令帮助 |
| `podman system prune` | 清理未使用的资源（容器、镜像、网络、卷） |

## Rootless 模式说明

Podman 默认以 rootless 模式运行，这是区别于 Docker 的重要安全特性。rootless 模式下：

- 无需 sudo 即可运行容器命令
- 容器内 root 用户映射到宿主机普通用户
- 容器数据默认存储在用户目录下（遵循 XDG 目录规范）
- 使用用户命名空间实现隔离

首次运行 rootless Podman 时，`SetXdgDirs()` 函数会确保正确设置 `XDG_RUNTIME_DIR` 和 `XDG_CONFIG_HOME` 环境变量，供容器存储和配置使用。

## 双引擎模式注意

Podman CLI 支持两种运行模式，这会影响某些命令的可用性：

- **ABI 模式（本地）**：直接在本地调用 libpod 库，完整功能可用
- **Tunnel 模式（远程）**：通过 REST API 连接到远程 Podman 服务，部分本地专用命令不可用

命令注册时会根据 EngineMode 过滤，`registry.Commands` 注册表中的命令带有模式标记。使用 `podman system connection` 管理远程连接。

## 相关概念

- [Podman 简介](00-introduction.md) — 项目定位、核心特性与生态概览
- [架构概览](02-architecture-overview.md) — 无守护进程架构与核心抽象分层
- [Runtime 运行时](03-runtime.md) — libpod 核心 Runtime 结构体与初始化流程
