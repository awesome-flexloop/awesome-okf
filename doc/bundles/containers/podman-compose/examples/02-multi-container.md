---
type: Example
title: 多容器应用编排
description: 使用 podman-compose 编排包含 Web + Redis 集群的多服务应用，展示依赖管理、网络隔离与扩展模式
tags: [podman, compose, example, multi-container, redis, cluster, scaling]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-26T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-26T00:00:00Z" }
status: stable
stale_after: "2027-08-26"
sources:
  - id: readme
    resource: /references/readme-source.md
    title: podman-compose 官方 README
---

# 多容器应用编排

本示例展示如何使用 podman-compose 编排一个包含 Web 应用和 Redis 集群的多容器应用，演示服务依赖、网络配置、卷管理、环境变量等高级编排模式。

## 示例概述

我们将部署一个架构如下的应用：

```
┌─────────────────────────────────────────────────┐
│ 前端网络 (frontend)                             │
│  ┌──────┐                                       │
│  │ web  │ :8080 → 浏览器访问                     │
│  └──┬───┘                                       │
└─────┼───────────────────────────────────────────┘
      │
┌─────┼───────────────────────────────────────────┐
│ 后端网络 (backend)                              │
│  ┌──┴───┐  ┌─────────┬─────────┬─────────┐     │
│  │ web  │  │redis-   │redis-   │redis-   │ ... │
│  │      │→ │node1    │node2    │node3    │     │
│  └──────┘  └─────────┴─────────┴─────────┘     │
│                       ↕                         │
│                   ┌──────────┐                  │
│                   │redis-    │ (集群初始化)     │
│                   │cluster   │                  │
│                   └──────────┘                  │
└─────────────────────────────────────────────────┘
```

组件：
- **web**：Hello App Web 服务，对外暴露 8080 端口
- **redis-node1~5**：Redis 集群节点
- **redis-cluster**：Redis 集群初始化节点，负责创建集群
- **两个网络**：frontend（对外）、backend（内部）
- **多个卷**：每个 Redis 节点一个数据卷

## 项目结构

```
hello-redis/
└── compose.yaml
```

## 步骤 1：创建 Compose 文件

创建 `compose.yaml`：

```yaml
---
version: '3'
volumes:
  redis-node1-data:
  redis-node2-data:
  redis-node3-data:
  redis-node4-data:
  redis-node5-data:
  redis-data:

networks:
  frontend:
  backend:
    internal: true

services:
  web:
    image: gcr.io/google-samples/hello-app-redis:1.0
    depends_on:
      - redis-cluster
    ports:
      - "${HOST_PORT:-8080}:8080"
    networks:
      - frontend
      - backend
    environment:
      - REDIS_HOST=redis-cluster
      - REDIS_PORT=6379

  redis-node1:
    image: docker.io/bitnami/redis-cluster:6.2
    volumes:
      - redis-node1-data:/bitnami/redis/data
    networks:
      - backend
    environment:
      - ALLOW_EMPTY_PASSWORD=yes
      - REDIS_NODES=redis-node1 redis-node2 redis-node3 redis-node4 redis-node5 redis-cluster

  redis-node2:
    image: docker.io/bitnami/redis-cluster:6.2
    volumes:
      - redis-node2-data:/bitnami/redis/data
    networks:
      - backend
    environment:
      - ALLOW_EMPTY_PASSWORD=yes
      - REDIS_NODES=redis-node1 redis-node2 redis-node3 redis-node4 redis-node5 redis-cluster

  redis-node3:
    image: docker.io/bitnami/redis-cluster:6.2
    volumes:
      - redis-node3-data:/bitnami/redis/data
    networks:
      - backend
    environment:
      - ALLOW_EMPTY_PASSWORD=yes
      - REDIS_NODES=redis-node1 redis-node2 redis-node3 redis-node4 redis-node5 redis-cluster

  redis-node4:
    image: docker.io/bitnami/redis-cluster:6.2
    volumes:
      - redis-node4-data:/bitnami/redis/data
    networks:
      - backend
    environment:
      - ALLOW_EMPTY_PASSWORD=yes
      - REDIS_NODES=redis-node1 redis-node2 redis-node3 redis-node4 redis-node5 redis-cluster

  redis-node5:
    image: docker.io/bitnami/redis-cluster:6.2
    volumes:
      - redis-node5-data:/bitnami/redis/data
    networks:
      - backend
    environment:
      - ALLOW_EMPTY_PASSWORD=yes
      - REDIS_NODES=redis-node1 redis-node2 redis-node3 redis-node4 redis-node5 redis-cluster

  redis-cluster:
    image: docker.io/bitnami/redis-cluster:6.2
    volumes:
      - redis-data:/bitnami/redis/data
    depends_on:
      - redis-node1
      - redis-node2
      - redis-node3
      - redis-node4
      - redis-node5
    networks:
      - backend
    environment:
      - ALLOW_EMPTY_PASSWORD=yes
      - REDIS_NODES=redis-node1 redis-node2 redis-node3 redis-node4 redis-node5 redis-cluster
      - REDIS_CLUSTER_CREATOR=yes
```

## 配置详解

### 网络隔离

```yaml
networks:
  frontend:
  backend:
    internal: true
```

- `frontend`：前端网络，web 服务在此网络暴露端口
- `backend`：`internal: true` 标记为内部网络，连接此网络的容器无法访问外网，增加安全性

Web 服务同时加入两个网络，作为反向代理/应用网关：

```yaml
web:
  networks:
    - frontend
    - backend
```

Redis 节点只加入 backend 网络，外部无法直接访问数据库。

### 服务依赖链

```yaml
web:
  depends_on:
    - redis-cluster

redis-cluster:
  depends_on:
    - redis-node1
    - redis-node2
    - redis-node3
    - redis-node4
    - redis-node5
```

启动顺序：redis-node1~5 → redis-cluster → web

`redis-cluster` 通过 `REDIS_CLUSTER_CREATOR=yes` 环境变量标记为集群初始化节点，等待所有节点启动后创建 Redis 集群。

### 数据持久化

每个 Redis 节点使用独立的命名卷：

```yaml
volumes:
  redis-node1-data:
  # ... 每个节点一个卷
```

```yaml
redis-node1:
  volumes:
    - redis-node1-data:/bitnami/redis/data
```

避免不同节点的数据冲突，容器重建时数据不丢失。

### 环境变量与参数化

```yaml
ports:
  - "${HOST_PORT:-8080}:8080"
```

使用 `${VAR:-default}` 语法支持通过环境变量覆盖端口：

```bash
# 使用默认端口 8080
podman-compose up -d

# 自定义端口
HOST_PORT=9090 podman-compose up -d
```

也可以在 `.env` 文件中设置：

```bash
echo "HOST_PORT=9090" > .env
podman-compose up -d
```

### 服务发现

容器间通过服务名直接通信：

```yaml
environment:
  - REDIS_NODES=redis-node1 redis-node2 redis-node3 redis-node4 redis-node5 redis-cluster
```

无需硬编码 IP 地址，podman 内置 DNS 自动解析服务名到容器 IP。

## 步骤 2：启动应用

```bash
podman-compose up -d
```

podman-compose 将按依赖顺序启动：
1. 创建两个网络（frontend、backend）
2. 创建 6 个数据卷
3. 启动 redis-node1~5
4. 启动 redis-cluster（等待节点就绪后初始化集群）
5. 启动 web 服务

## 步骤 3：验证部署

### 查看服务状态

```bash
podman-compose ps
```

应该看到 7 个容器都处于运行状态。

### 查看日志

```bash
# 查看集群初始化日志
podman-compose logs redis-cluster

# 查看 web 服务日志
podman-compose logs web
```

### 访问 Web 服务

```bash
curl http://localhost:8080
```

## 常用编排操作

### 查看日志

```bash
# 查看所有服务日志
podman-compose logs

# 跟踪日志输出
podman-compose logs -f

# 查看特定服务日志并限制行数
podman-compose logs --tail=50 web
```

### 扩展服务

使用 `--scale` 扩展无状态服务：

```bash
# 扩展 web 服务到 3 个实例
podman-compose up -d --scale web=3
```

> **注意**：扩展多个实例时，`ports` 映射会有冲突，建议对于需要扩展的服务不直接映射端口，而是通过前端代理。

### 重启特定服务

```bash
podman-compose restart web
```

### 在运行中的容器执行命令

```bash
# 连接到 redis-cli 查看集群状态
podman-compose exec redis-cluster redis-cli cluster nodes

# 在 web 容器中执行 shell
podman-compose exec web bash
```

### 暂停与恢复

```bash
# 暂停所有服务
podman-compose pause

# 恢复服务
podman-compose unpause
```

### 停止与清理

```bash
# 停止服务（保留容器和数据）
podman-compose stop

# 停止并删除容器、网络（保留卷）
podman-compose down

# 完全清理，包括数据卷（警告：数据丢失！）
podman-compose down -v
```

## 多 Compose 文件叠加

开发/生产环境分离是常见模式。创建基础配置和环境覆盖配置：

`compose.yaml`（基础配置）：
```yaml
services:
  web:
    image: myapp:latest
    ports:
      - "8080:8080"
  db:
    image: postgres:15
```

`compose.dev.yaml`（开发环境覆盖）：
```yaml
services:
  web:
    build: .
    volumes:
      - ./src:/app/src
    environment:
      - DEBUG=true
  db:
    ports:
      - "5432:5432"
```

`compose.prod.yaml`（生产环境覆盖）：
```yaml
services:
  web:
    restart: always
    environment:
      - DEBUG=false
  db:
    restart: always
```

使用多个文件启动：

```bash
# 开发环境
podman-compose -f compose.yaml -f compose.dev.yaml up -d

# 生产环境
podman-compose -f compose.yaml -f compose.prod.yaml up -d
```

## 使用 profiles 选择性启动

如果添加了调试工具但不想默认启动：

```yaml
services:
  web:
    image: myapp
  debug:
    image: busybox
    command: sleep infinity
    profiles:
      - debug
    network_mode: service:web
```

```bash
# 正常启动，不启动 debug 容器
podman-compose up -d

# 需要调试时，带 profile 启动
podman-compose --profile debug up -d
```

## rootless 模式多容器注意事项

1. **DNS 解析**：确保 dnsname 插件已安装（CNI）或使用 netavark 后端
2. **端口冲突**：多个服务不能映射同一主机端口，rootless 模式建议用 >1024 端口
3. **文件权限**：多容器共享绑定挂载目录时，注意 UID/GID 映射
4. **网络性能**：rootless 网络使用 slirp4netns/pasta，性能略低于 root 模式，高并发场景可考虑 `network_mode: host`

## 健康检查与依赖等待

对于更可靠的启动顺序，添加健康检查：

```yaml
services:
  redis-node1:
    image: docker.io/bitnami/redis-cluster:6.2
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 2s
      timeout: 3s
      retries: 40

  redis-cluster:
    depends_on:
      redis-node1:
        condition: service_healthy
      redis-node2:
        condition: service_healthy
```

这样 `redis-cluster` 会等待所有 Redis 节点真正就绪（而非仅启动）后才开始初始化集群。

## 相关概念

- [快速上手与 Compose Spec 兼容](/concepts/00-introduction.md)
- [daemon-less 架构](/concepts/01-daemonless-arch.md)
- [rootless 模式下的网络与卷](/concepts/02-rootless.md)
- [Compose 文件常见模式](/concepts/03-compose-patterns.md)
- [WordPress 部署示例](/examples/01-wordpress.md)
