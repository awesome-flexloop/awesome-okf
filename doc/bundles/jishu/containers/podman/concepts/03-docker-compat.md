---
type: Concept
title: "Docker CLI/API 兼容性设计"
description: "CLI 命令对齐、环境变量双兼容、DOCKER_HOST→CONTAINER_HOST、REST API 双端点、podman-compose 与已知差异清单。"
tags: [podman, docker, compatibility, migration, cli, rest-api, docker-compose]
generated: { by: "reference_agent/trae-cn", at: 2026-09-07T09:45:00+08:00 }
verified: { by: "process:grep-v", at: 2026-09-07T09:45:00+08:00 }
status: stable
stale_after: 2027-09-07
sources:
  - id: cli-domain
    resource: /references/cli-domain-source.md
    title: CLI 层与 Domain 层架构源码
---

# Docker CLI/API 兼容性设计

Podman 的核心战略定位是"**Drop-in Docker replacement**"——即 Docker 用户在 99% 的场景下只需把 `docker` 命令替换为 `podman`，其他什么都不用改。这个目标通过三层兼容设计达成。

## 第一层：CLI 命令与别名兼容

### 别名法：一行命令，零改动

最简单的迁移方案——在 shell rc 中加一行别名：
```bash
# ~/.bashrc / ~/.zshrc
alias docker=podman
alias docker-compose=podman-compose
```

之后所有习惯的 `docker run` / `docker build` / `docker ps` 照常工作。

### CLI 命令级对齐（v6.x）

Podman CLI 复刻了 Docker CLI 的所有核心命令与绝大多数 flags。典型的"一字不差"命令：

| 场景 | Docker 命令 | Podman 等价 |
|------|------------|------------|
| 后台跑 Nginx | `docker run -d -p 8080:80 --name web nginx` | **完全相同** |
| 构建镜像 | `docker build -t myapp:latest .` | **完全相同**（也接受 Dockerfile） |
| 列容器 | `docker ps` / `docker ps -a -q` | **完全相同** |
| 看日志 | `docker logs -f --tail 100 web` | **完全相同** |
| 进容器 | `docker exec -it web bash` | **完全相同** |
| 看详情 | `docker inspect web` | **完全相同**（JSON 字段兼容） |
| 拉镜像 | `docker pull alpine:3.20` | **完全相同** |
| 推镜像 | `docker push myrepo/myapp:v1` | **完全相同** |
| 清理 | `docker system prune -a -f` | **完全相同** |

### Podman 独有的增强命令

除了兼容，Podman 还提供很多 Docker 没有的命令：

| Podman 独有命令 | 作用 | Docker 用户怎么办到 |
|----------------|------|---------------------|
| `podman pod ...` | 原生 Pod 管理 | Docker 需 k3s / minikube 或 docker compose 模拟 |
| `podman kube play` | 直接跑 K8s YAML | Docker 无解（或 Kind 集群） |
| `podman generate kube` | 容器→导出 K8s Deployment | Docker 无解 |
| `podman generate systemd` | 容器→systemd unit | Docker 需手写 service |
| `podman quadlet` | .container 单元 | Docker 无解 |
| `podman machine` | macOS/Windows 虚拟机 | Docker Desktop（商业） |
| `podman unshare` | user namespace 工具 | Docker rootless 用 nsenter |
| `podman image scp` | 跨主机直接传镜像 | Docker 必须走 registry |

## 第二层：环境变量与连接串兼容

### 双环境变量识别
Podman 同时识别 Docker 风格（DOCKER_*）和 Podman 风格（CONTAINER_*）两套环境变量，前者优先：

| 优先级 | Podman 变量 | Docker 变量 | 作用 |
|-------|------------|------------|------|
| 1（高） | `CONTAINER_HOST` | `DOCKER_HOST` | 连接串 URL |
| 1 | `CONTAINER_TLS_VERIFY` | `DOCKER_TLS_VERIFY` | TLS 开启 |
| 1 | `CONTAINER_CERT_PATH` | `DOCKER_CERT_PATH` | 证书路径 |
| 2 | `CONTAINER_CONNECTION` | — | 命名连接（Podman 独有） |

典型的 Docker 迁移脚本**零修改**运行：
```bash
# 这段 Docker 脚本直接用 Podman 跑：
export DOCKER_HOST="ssh://root@10.0.0.5/run/user/0/podman/podman.sock"
export DOCKER_TLS_VERIFY=0
docker run hello-world    # 走 alias → podman → SSH 远程
```

### Socket 路径差异需要注意

| 模式 | Docker socket | Podman socket |
|------|--------------|--------------|
| root / rootful | `/var/run/docker.sock` | `/run/podman/podman.sock` |
| rootless | `/run/user/$UID/docker.sock` | `/run/user/$UID/podman/podman.sock` |

> 应用里硬编码了 `unix:///var/run/docker.sock` 的话：① 把 Podman 开个 Docker 兼容 socket（`systemctl enable --now podman.socket` 默认兼容）；② 或做软链 `/var/run/docker.sock -> /run/podman/podman.sock`。

## 第三层：REST API 双端点兼容

Podman REST API 服务器（`podman system service`）在**同一个 HTTP 端口上同时提供两套 API**：

| URL 前缀 | 规范 | 用途 |
|----------|------|------|
| `/v1.x/...` | Docker API（兼容） | 供 docker-py、Docker SDK 客户端使用 |
| `/libpod/...` | Podman 原生 API | Podman 独有功能（Pod / kube / quadlet / machine） |

Swagger / OpenAPI 定义：
- `https://docs.podman.io/en/latest/_static/swagger.yaml`（最新 main 分支）
- `https://docs.podman.io/en/v6.0.0/_static/swagger.yaml`（指定版本）

### Docker SDK for Python → podman-py 零修改迁移
`podman-py` SDK 完全复刻 docker-py 的 API（见 [podman-py 知识包](../podman-py/index.md)）：

```python
# Docker 用户原代码
import docker
client = docker.from_env()
for c in client.containers.list():
    print(c.name)

# 迁移后 ↓ 只有 import 改了一行；其他代码 100% 相同
import podman as docker
client = docker.from_env()
for c in client.containers.list():
    print(c.name)
```

## podman-compose：Docker Compose 兼容方案

Docker Compose 是 Docker 用户的重度依赖，Podman 通过 `podman-compose` 脚本实现了对 `docker-compose.yml`（v2/v3）的 95%+ 兼容：

```bash
# 安装
pip install podman-compose   # 或 dnf install -y podman-compose

# 用法：与 docker-compose 完全同形同义
podman-compose -f compose.yaml up -d
podman-compose ps
podman-compose logs -f web
podman-compose down
```

内部机制：podman-compose 解析 compose YAML → 翻译为对应的 `podman run / podman pod create / podman network create` 命令，不需要常驻 compose 守护进程。

> 2025 年后推荐：`podman compose`（Podman 6.x 内置，不再需要单独安装），命令语义与 docker compose 完全一致。

## 已知差异清单（Migration checklist）

> ⚠️ 迁移前必须检查以下不兼容点，其余 95% 命令完全相同。

### 不支持的 Docker 特性

| Docker 特性 | Podman 行为 | 替代方案 |
|------------|------------|---------|
| **Docker Swarm**（集群编排） | 原生不支持，相关 API 抛 NotImplementedError | 用 Kubernetes / Nomad；或 Podman + Ansible 自行编排 |
| `docker link`（废弃的容器链接） | 不支持 | 使用 `--network` + 内置 DNS（Podman 100% 支持） |
| Docker Desktop UI | 无官方 UI | Cockpit + Podman 插件 / Portainer Podman 后端 |
| BuildKit (`DOCKER_BUILDKIT=1`) | 默认用 Buildah（同等能力，语法兼容） | 完全不需要迁移，Containerfile 同构 |
| `docker scan`（Snyk 镜像扫描） | 内置不包含 | 用 `podman build --sbom=true` + Trivy 或 Grype 扫描 |

### 行为不一致的细节

| 项目 | Docker | Podman | 解决 |
|------|--------|--------|------|
| **容器主机名** | 默认随机短 ID | 默认 `podman run --hostname` 为空，需要手动设 | 脚本里显式写 `--hostname=web-01` |
| `/etc/hosts` 自动追加记录 | 自动写容器名到 hosts | 默认不写（符合更严格的隔离） | 加 `--add-host name:ip` 或 `--network-alias` |
| `--name` 已被占用报错时机 | create 时 | create 时相同 | 完全一致 |
| 卷挂载**不存在的目录** | Docker 自动 mkdir（root） | Podman 会报错（安全更严格） | 提前 mkdir 或显式 `--mount type=tmpfs` |
| `docker exec -u 0`（指定 exec 用户） | 支持 | 同支持；但 rootless 下 exec 进容器 uid=0 仍是映射用户 | 预期内 |
| 默认 seccomp/selinux 配置 | 宽松一些 | Podman 更严格（更安全） | 容器若有 syscall 被拦，用 `--security-opt seccomp=unconfined` 排查 |

### 生产迁移五步法

```
①  评估：跑 podman-compose + 应用全量回归测试（1-2 周，发现卷属主/端口/SELinux 问题）
②  基础设施：所有节点配置 subuid/subgid、开 cgroup v2 delegation
③  套接字：把老的 /var/run/docker.sock 软链到 Podman socket
④  灰度：10% 流量切到 Podman 节点跑，观察 72 小时 CPU/内存/IO 指标
⑤  全量：alias docker=podman；systemctl stop docker --now; mask docker.socket
```

## 相关概念
- [/concepts/02-rootless.md](02-rootless.md) — Rootless 迁移的核心前提
- [../podman-py/index.md](../podman-py/index.md) — Python SDK 兼容性详解
- [/examples/01-rootless-production.md](../examples/01-rootless-production.md) — 生产环境部署流程
