---
type: Concept
title: 远程连接与REST API
description: Podman双引擎ABI/Tunnel，ContainerEngine/ImageEngine抽象，Docker兼容与libpod双套REST API
tags: [podman, concept, rest-api, remote, abi, tunnel, gorilla-mux, bindings, docker-compat, system-service]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-26T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-26T00:00:00Z" }
status: stable
stale_after: 2027-08-26
sources: [{id:"podman-source", resource:"/references/podman-source.md", title:"Podman Container Tools 源码信源登记"}]
---

## 双引擎架构

Podman 采用**双引擎架构**设计，通过统一的引擎接口抽象同时支持本地直接调用和远程网络调用。CLI 命令通过 `parseCommands` 函数根据当前的 `EngineMode` 自动过滤可用命令：

- **ABIMode（本地模式）**：直接在本地调用 libpod 库，通过 ABI（Application Binary Interface）层与运行时交互，无网络开销
- **TunnelMode（隧道模式）**：通过 HTTP 连接到远程 Podman 服务，所有命令通过 REST API 转发执行

`cmd/podman/` 下的命令注册时会声明自己支持的引擎模式，`parseCommands` 在启动时根据当前模式过滤出可用命令，确保本地命令不会在远程连接时暴露，反之亦然。

## ContainerEngine 与 ImageEngine 接口抽象

Podman 的核心能力通过两个引擎接口抽象，定义在 `pkg/domain/entities/engine.go`：

| 接口 | 职责 | 核心方法分类 |
|------|------|-------------|
| **ContainerEngine** | 容器/Pod/网络/卷/系统等完整生命周期管理 | ContainerCreate/Start/Stop/Inspect、PodCreate/Start、NetworkCreate/、VolumeCreate、Events、Info 等 |
| **ImageEngine** | 镜像生命周期管理 | ImagePull/Push/Build/Tag/Remove/Inspect/List 等 |

### 分层架构实现

`pkg/domain/` 目录采用清晰的三层分层设计：

```text
pkg/domain/
├── entities/       # 接口定义 + 数据传输对象(DTO)
└── infra/
    ├── abi/        # 本地实现：直接调用 libpod 库
    └── tunnel/     # 远程实现：HTTP 客户端调用 REST API
```

- **entities/**：定义 ContainerEngine、ImageEngine 接口，以及所有请求/响应结构体
- **infra/abi/**：本地引擎实现，将接口方法直接转发到 libpod Runtime，性能最优
- **infra/tunnel/**：远程引擎实现，将接口方法序列化为 HTTP 请求发送到服务端

这种分层设计保证了 CLI 代码无需关心本地/远程差异，同一套命令代码在两种模式下都能工作。

## 远程连接管理

`system/` 子目录包含远程连接管理相关命令：connection、context、service。

### podman system service：启动 API 服务

`podman system service` 命令启动 Podman REST API 服务，监听 Unix socket 或 TCP 端口：

```bash
podman system service --time=0 unix:///run/podman/podman.sock
podman system service tcp://localhost:8080
```bash

默认情况下，Podman 服务以 systemd socket 激活方式运行，仅在有客户端连接时才启动实际服务进程，空闲时自动退出以节省资源。`--time=0` 表示不超时。

### podman system connection：管理远程连接

`podman system connection` 命令管理多个远程 Podman 服务端点的连接配置：

```bash
podman system connection add myserver ssh://user@host/run/user/1000/podman/podman.sock
podman system connection list
podman system connection default myserver
podman system connection remove myserver
```bash

支持的连接协议：
- **unix://**：本地 Unix socket
- **ssh://**：通过 SSH 隧道连接远程 Podman socket（推荐）
- **tcp://**：直接 TCP 连接（需额外配置 TLS）

### podman system context：管理多上下文

`podman system context` 类似 Kubernetes 的 kubeconfig 上下文，允许在多个连接配置间快速切换：

```bash
podman system context create prod --identity ~/.ssh/prod_key ssh://root@prod-host
podman system context use prod
podman system context list
```bash

## REST API 双接口设计

Podman 提供 REST API，包含两套 API 端点，分别满足不同需求：

| API 路径前缀 | 名称 | 设计目标 |
|-------------|------|---------|
| `/v1.xx/libpod/` | **Docker 兼容 API** | 与 Docker Engine API 兼容，现有 Docker 客户端和工具可直接使用 |
| `/libpod/` | **Podman 原生 API** | 暴露 Podman 全部高级功能（Pods、Quadlet、kube play 等） |

### API 服务实现架构

`pkg/api/` 目录包含 REST API 服务的完整实现：

```text
pkg/api/
├── handlers/
│   ├── compat/    # Docker 兼容 API 处理器
│   └── libpod/    # Podman 原生 API 处理器
└── server/        # HTTP 服务器实现
```bash

- **handlers/compat/**：实现 Docker 兼容接口，将 Docker API 请求转换为 ContainerEngine/ImageEngine 调用
- **handlers/libpod/**：实现 Podman 特有功能的 API 端点
- **server/**：HTTP 服务器核心，处理路由注册、中间件、请求/响应编解码

### HTTP 路由与编解码

API 服务使用以下第三方库：
- **gorilla/mux**：HTTP 路由，用于注册和匹配 API 端点路径
- **gorilla/schema**：Schema 解码，将 URL 查询参数解码为 Go 结构体

这两个库都是 Go 生态中成熟稳定的选择，保证了 API 服务的性能和可靠性。

## pkg/bindings：Go 客户端绑定

`pkg/bindings/` 目录提供了类型安全的 Go HTTP 客户端绑定，供 `pkg/domain/infra/tunnel/` 远程引擎实现使用，也可供第三方 Go 程序直接集成 Podman API。

绑定层的特点：
- 与服务端共享 `pkg/domain/entities/` 中定义的数据结构
- 自动处理连接管理、认证、错误处理
- 支持 Unix socket 和 SSH 隧道连接
- 提供完整的容器、镜像、Pod、网络、卷等操作方法

Go 程序使用示例：

```go
import (
    "context"
    "github.com/containers/podman/v5/pkg/bindings"
    "github.com/containers/podman/v5/pkg/bindings/containers"
)

func main() {
    ctx, _ := bindings.NewConnection(context.Background(), "unix:///run/podman/podman.sock")
    list, _ := containers.List(ctx, nil, nil)
    for _, c := range list {
        fmt.Println(c.ID, c.Names)
    }
}
```bash

## podman-remote 客户端

`podman-remote` 是专门编译的远程客户端二进制文件，默认工作在 TunnelMode：

- 与本地 `podman` 命令行接口完全一致
- 默认读取远程连接配置，无需显式指定目标
- 适合安装在客户端机器（如 macOS/Windows 开发者机器）连接到 Linux 服务器上的 Podman 服务
- 也是 Podman Desktop 等 GUI 工具与 Podman 交互的基础

在 macOS 和 Windows 上安装的 Podman 客户端实际上就是 `podman-remote`，因为这些平台通过 Podman Machine 虚拟机运行容器，CLI 自动通过 SSH 连接到虚拟机内的 Podman 服务。

## 典型 API 使用示例

### 使用 curl 调用 Docker 兼容 API

```bash
# 列出容器（Docker 兼容）
curl -s --unix-socket /run/podman/podman.sock http://v1.41/containers/json | python3 -m json.tool

# 拉取镜像
curl -s --unix-socket /run/podman/podman.sock \
  -X POST http://v1.41/images/create?fromImage=docker.io/library/alpine:latest
```bash

### 使用 curl 调用 Podman 原生 API

```bash
# 列出 Pods（Podman 特有功能）
curl -s --unix-socket /run/podman/podman.sock http://d/v5.0.0/libpod/pods/json

# 生成 systemd 单元
curl -s --unix-socket /run/podman/podman.sock \
  -X POST "http://d/v5.0.0/libpod/generate/systemd?names=mycontainer"
```bash

### 通过 SSH 远程调用

```bash
# 通过 SSH 隧道调用远程 Podman
podman -c ssh://user@remote-host run --rm alpine echo "Hello from remote"

# 或先设为默认连接
podman system connection add prod ssh://user@remote-host
podman system connection default prod
podman info
```bash

## 相关概念

- [CLI结构](/concepts/06-cli-structure.md) — parseCommands命令过滤机制与命令树结构
- [架构概览](/concepts/02-architecture-overview.md) — Podman整体分层架构与组件交互
- [Runtime运行时](/concepts/03-runtime.md) — ABI模式下libpod Runtime直接调用路径
- [systemd集成与Quadlet](/concepts/12-systemd-quadlet.md) — systemd socket激活API服务
