---
type: Concept
title: "快速入门与 Docker SDK 兼容性"
description: "podman-py 安装、第一个程序、与 docker-py 的 API 兼容性设计、Python 版本要求与核心依赖。"
tags: [podman-py, introduction, quickstart, docker-compatibility, installation]
generated: { by: "reference_agent/trae-cn", at: 2026-08-26T15:45:00+08:00 }
verified: { by: "process:grep-v", at: 2026-08-26T15:45:00+08:00 }
status: stable
stale_after: 2027-08-26
sources:
  - id: readme
    resource: /references/readme-source.md
    title: README.md 项目概览与快速入门
  - id: client
    resource: /references/client-source.md
    title: client.py PodmanClient 核心客户端
---

# 快速入门与 Docker SDK 兼容性

podman-py 是 [Podman](https://github.com/containers/podman) 容器引擎的官方 Python RESTful API 绑定库，提供与 Docker SDK for Python（docker-py）高度兼容的编程接口，使现有 Docker Python 应用可以低成本迁移到 Podman 运行时。

## Python 版本要求

podman-py 5.8.0 要求 Python 版本 ≥ 3.9。

## 安装

使用 pip 从 PyPI 安装：

```bash
pip install podman
```

如需镜像拉取进度条支持，安装带 `progress_bar` 可选依赖的版本：

```bash
pip install "podman[progress_bar]"
```

## 第一个 Podman 程序

使用 `with` 上下文管理器自动管理连接资源：

```python
from podman import PodmanClient

with PodmanClient(base_url="unix:///run/user/1000/podman/podman.sock") as client:
    print("Podman 版本:", client.version()["Version"])
    print("运行中容器:", len(client.containers.list()))
    print("本地镜像:", len(client.images.list()))
```

## Docker SDK 兼容性设计

podman-py 在 API 层面做了大量兼容 docker-py 的设计，核心兼容机制包括：

### 1. 类型别名

```python
from podman import PodmanClient
# 或使用 Docker 风格别名直接替换导入
from podman import DockerClient  # DockerClient = PodmanClient
```

代码中 `import docker` 替换为 `import podman as docker` 通常即可完成大部分迁移。

### 2. 环境变量兼容

`PodmanClient.from_env()` 同时识别以下两组环境变量：

| Podman 变量              | Docker 变量           | 用途       |
| ---------------------- | ------------------- | -------- |
| `CONTAINER_HOST`       | `DOCKER_HOST`       | 服务连接 URL |
| `CONTAINER_TLS_VERIFY` | `DOCKER_TLS_VERIFY` | TLS 证书验证 |
| `CONTAINER_CERT_PATH`  | `DOCKER_CERT_PATH`  | TLS 证书路径 |

### 3. Manager API 对齐

`client.containers`、`client.images`、`client.networks`、`client.volumes` 等管理器的方法签名与 docker-py 保持一致，包括：

- `containers.list()` / `containers.get()` / `containers.run()` / `containers.create()`
- `images.list()` / `images.get()` / `images.pull()` / `images.push()` / `images.build()`
- `networks.list()` / `networks.get()` / `networks.create()`
- `volumes.list()` / `volumes.get()` / `volumes.create()`

### 4. 兼容模式参数

部分 API 支持 `compatible=True` 参数以切换到 Docker 兼容端点行为：

```python
# Docker 兼容模式下列出容器（默认 sparse=False，返回完整属性）
containers = client.containers.list(compatible=True)
```

### 不支持的功能

Podman 是无守护进程（daemonless）容器引擎，原生不支持 Docker Swarm 模式，以下属性会抛出 `NotImplementedError`：

- `client.swarm`
- `client.services`
- `client.configs`
- `client.nodes`

## 核心依赖

| 依赖         | 版本要求    | 用途                                        |
| ---------- | ------- | ----------------------------------------- |
| `requests` | ≥ 2.24  | HTTP 客户端，APIClient 继承自 `requests.Session` |
| `tomli`    | ≥ 1.2.3 | TOML 配置解析（Python < 3.11）                  |
| `urllib3`  | -       | HTTP 底层传输                                 |

## 相关概念

- [/concepts/01-connection.md](/concepts/01-connection.md)
- [/concepts/02-managers.md](/concepts/02-managers.md)
- [/examples/01-migration.md](/examples/01-migration.md)

