---
type: Concept
title: "连接配置（UDS/SSH/TCP）"
description: "PodmanClient 支持的三种连接方式：本地 Unix Socket、SSH 远程隧道、TCP 网络连接，以及连接配置优先级与环境变量自动检测。"
tags: [podman-py, connection, uds, ssh, tcp, base_url, from_env, containers.conf]
generated: { by: "reference_agent/trae-cn", at: 2026-08-26T15:45:00+08:00 }
verified: { by: "process:grep-v", at: 2026-08-26T15:45:00+08:00 }
status: stable
stale_after: 2027-08-26
sources:
  - id: client
    resource: /references/client-source.md
    title: client.py PodmanClient 核心客户端
  - id: api
    resource: /references/api-source.md
    title: api/ HTTP 传输层实现
---

# 连接配置（UDS/SSH/TCP）

PodmanClient 支持三种连接到 Podman 服务的方式：本地 Unix Domain Socket（UDS）、SSH 远程隧道、TCP 网络连接。APIClient 通过自定义 `requests` 适配器实现对不同传输协议的支持。

## 连接配置优先级

PodmanClient 初始化时按以下优先级确定连接地址：

1. **显式 `connection` 参数**：从 `~/.config/containers/containers.conf` 读取命名连接配置
2. **显式 `base_url` 参数**：使用指定的 URL 连接
3. **active_service（Podman Machine）**：如果配置了 Podman Machine 且处于活跃状态，自动使用其连接
4. **本地默认 Socket**：回退到 `http+unix://<runtime_dir>/podman/podman.sock`

`runtime_dir` 通过 `podman.api.path_utils.get_runtime_dir()` 获取，在 Linux 上通常为 `/run/user/$UID`。

## 1. 本地 Unix Socket 连接（推荐）

这是最常用、性能最高的本地连接方式，适用于：
- Linux 本地运行 Podman
- WSL2 中运行 Podman
- rootful 或 rootless Podman

### URL 格式

```
unix:///run/podman/podman.sock          # rootful 系统 Socket
http+unix:///run/podman/podman.sock     # 显式 HTTP over UDS
unix:///run/user/$UID/podman/podman.sock # rootless 用户 Socket
```

### 示例

```python
from podman import PodmanClient

# rootless 用户连接
client = PodmanClient(base_url="unix:///run/user/1000/podman/podman.sock")

# rootful 连接（通常需要 sudo 权限）
client = PodmanClient(base_url="unix:///run/podman/podman.sock")
```

UDS 连接使用 `UDSAdapter` 适配器，通过 Unix Domain Socket 文件直接通信，无 TCP 开销。

## 2. SSH 远程连接

适用于连接远程主机上运行的 Podman 服务，通过 SSH 隧道转发 Socket 通信。

### URL 格式

```
ssh://<user>@<host>[:port]/run/podman/podman.sock[?secure=True]
http+ssh://<user>@<host>[:port]/run/podman/podman.sock
```

### 关键参数

| 参数 | 说明 |
|------|------|
| `identity` | SSH 私钥文件路径，默认使用 `~/.ssh/config` 配置 |
| `use_ssh_client` | 是否使用系统 SSH 客户端，默认为 `True` |

### 示例

```python
from podman import PodmanClient

# 使用 SSH 密钥连接远程 Podman
client = PodmanClient(
    base_url="ssh://core@192.168.1.100/run/user/1000/podman/podman.sock",
    identity="~/.ssh/id_ed25519"
)

# 使用系统 SSH 配置（~/.ssh/config 中的 Host 配置）
client = PodmanClient(
    base_url="ssh://podman-host/run/podman/podman.sock",
    use_ssh_client=True
)
```

SSH 连接使用 `SSHAdapter` 适配器，默认委托给系统 SSH 客户端处理认证和连接，支持 SSH Agent 转发、密钥认证等标准 SSH 功能。

## 3. TCP 网络连接

适用于 Podman 服务开启了 TCP 监听的场景（需要手动启用 Podman API 服务）。

### 启用 Podman TCP 服务

在远程主机上启动 Podman API 服务监听 TCP：

```bash
# 启动监听 TCP 127.0.0.1:8080（仅本地）
podman system service --time=0 tcp:127.0.0.1:8080

# 启动监听所有接口（⚠️ 生产环境请配置 TLS）
podman system service --time=0 tcp:0.0.0.0:8080
```

### URL 格式

```
tcp://<host>:<port>
http://<host>:<port>
```

### 示例

```python
from podman import PodmanClient

client = PodmanClient(base_url="tcp://192.168.1.100:8080")
```

TCP 连接使用标准 `requests.adapters.HTTPAdapter`，直接 HTTP 通信。

## 使用 from_env() 自动检测

`PodmanClient.from_env()` 类方法从环境变量自动读取连接配置，这是最便捷的连接方式，与 Docker CLI 行为一致：

```python
from podman import PodmanClient, from_env

# 方式一：类方法
client = PodmanClient.from_env()

# 方式二：便捷函数
client = from_env()
```

自动检测的环境变量：

| 环境变量 | 说明 | 示例值 |
|---------|------|--------|
| `CONTAINER_HOST` | Podman 服务 URL | `unix:///run/user/1000/podman/podman.sock` |
| `DOCKER_HOST` | Docker 风格服务 URL（兼容） | `tcp://localhost:2375` |
| `CONTAINER_TLS_VERIFY` | 是否验证 TLS | `1` 或 `0` |
| `DOCKER_TLS_VERIFY` | Docker 风格 TLS 验证（兼容） | `1` |
| `CONTAINER_CERT_PATH` | TLS 证书路径 | `~/.config/containers/certs` |
| `DOCKER_CERT_PATH` | Docker 风格证书路径（兼容） | `~/.docker/certs` |

## 使用 containers.conf 命名连接

如果在 `~/.config/containers/containers.conf` 中配置了命名连接，可以通过 `connection` 参数直接引用：

```python
from podman import PodmanClient

# 使用 containers.conf 中名为 "production" 的连接
client = PodmanClient(connection="production")
```

## 连接池配置

通过 `max_pool_size` 参数控制 HTTP 连接池大小：

```python
client = PodmanClient(
    base_url="unix:///run/user/1000/podman/podman.sock",
    max_pool_size=10
)
```

## 上下文管理器自动关闭

推荐使用 `with` 语句，退出上下文时自动调用 `client.close()` 释放连接资源：

```python
with PodmanClient.from_env() as client:
    info = client.info()
    print(info["host"]["os"])
# 此处连接已自动关闭
```

## 支持的 URL Scheme 汇总

| Scheme | 适配器 | 典型场景 |
|--------|--------|---------|
| `unix://` | UDSAdapter | Linux/WSL2 本地 rootless/rootful |
| `http+unix://` | UDSAdapter | 显式 HTTP over UDS |
| `ssh://` | SSHAdapter | 远程主机 SSH 连接 |
| `http+ssh://` | SSHAdapter | 显式 HTTP over SSH |
| `tcp://` | HTTPAdapter | 启用 TCP 监听的服务 |
| `http://` | HTTPAdapter | 普通 HTTP 连接 |

## 相关概念

- [/concepts/00-introduction.md](/concepts/00-introduction.md)
- [/concepts/02-managers.md](/concepts/02-managers.md)
- [/examples/02-container-ops.md](/examples/02-container-ops.md)
