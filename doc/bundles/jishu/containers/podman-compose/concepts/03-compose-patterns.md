---
type: Concept
title: Compose 文件常见模式
description: podman-compose 支持的 Compose 文件常见配置模式与最佳实践
tags: [podman, compose, yaml, patterns, configuration, best-practices]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-26T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-26T00:00:00Z" }
status: stable
stale_after: "2027-08-26"
sources:
  - id: readme
    resource: /references/readme-source.md
    title: podman-compose 官方 README
---

# Compose 文件常见模式

podman-compose 遵循 Compose Spec 规范，支持标准的 `compose.yaml`/`docker-compose.yml` 配置文件。本文档介绍常见的配置模式。

## 基础结构

一个典型的 Compose 文件包含以下顶层字段：

```yaml
---
version: '3'  # 可选，Compose Spec 不再强制要求
services:     # 服务定义（必填）
  web:
    image: nginx
volumes:      # 命名卷声明
  data:
networks:     # 自定义网络声明
  frontend:
configs:      # 配置（可选）
secrets:      # 密钥（可选）
```

> **注意**：现代 Compose Spec 不强制要求 `version` 字段，但为了兼容性仍可保留。

## 服务定义模式

### 基础服务：使用镜像

最常见的模式，直接使用现有镜像：

```yaml
services:
  web:
    image: docker.io/nginx:alpine
    ports:
      - "8080:80"
    restart: unless-stopped
```

### 构建镜像：使用 Dockerfile

从本地 Dockerfile 构建镜像：

```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
```

简写形式：

```yaml
services:
  app:
    build: .  # 等价于 context: .，使用默认 Dockerfile
```

### 环境变量配置

两种方式设置环境变量：

```yaml
services:
  db:
    image: mariadb:10.6
    # 方式1：列表形式
    environment:
      - MYSQL_ROOT_PASSWORD=secret
      - MYSQL_DATABASE=app
      - MYSQL_USER=app
      - MYSQL_PASSWORD=app123
    # 方式2：键值对形式（支持变量插值）
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD:-secret}
      MYSQL_DATABASE: app
```

### 使用 .env 文件

从文件加载环境变量：

```yaml
services:
  app:
    image: myapp
    env_file:
      - .env
      - .env.local
```

项目根目录下的 `.env` 文件会被自动加载。

### 端口映射

```yaml
services:
  web:
    image: nginx
    ports:
      # 主机端口:容器端口
      - "8080:80"
      # 指定绑定 IP
      - "127.0.0.1:8443:443"
      # 范围映射
      - "9090-9091:8080-8081"
      # 只指定容器端口（主机端口随机分配）
      - "3000"
    expose:
      # 仅暴露给内部网络，不映射到主机
      - "8080"
```

## 卷与存储模式

### 命名卷（推荐）

```yaml
volumes:
  db_data:
  cache_data:

services:
  db:
    image: postgres:15
    volumes:
      - db_data:/var/lib/postgresql/data
  redis:
    image: redis:7
    volumes:
      - cache_data:/data
```

### 绑定挂载：开发模式

开发时挂载源代码实现热重载：

```yaml
services:
  app:
    build: .
    volumes:
      - ./src:/app/src:ro  # 只读挂载源代码
      - ./config:/app/config
      - app_logs:/app/logs
    ports:
      - "8000:8000"

volumes:
  app_logs:  # 日志用命名卷，避免权限问题
```

### 只读根文件系统

安全加固：

```yaml
services:
  app:
    image: myapp
    read_only: true
    tmpfs:
      - /tmp
      - /run
    volumes:
      - app_data:/app/data
```

## 网络模式

### 单网络：默认桥接

服务默认加入同一网络，可通过服务名互相访问：

```yaml
services:
  web:
    image: nginx
    ports:
      - "8080:80"
  app:
    image: myapp
  db:
    image: postgres
# 无需显式声明 networks，默认创建一个网络
```

`web` 可通过 `http://app:8000` 访问应用服务，`app` 可通过 `db:5432` 访问数据库。

### 多网络隔离

前后端网络隔离：

```yaml
networks:
  frontend:
  backend:
    internal: true  # 后端网络无外网访问

services:
  web:
    image: nginx
    networks:
      - frontend
      - backend
  app:
    image: myapp
    networks:
      - backend
  db:
    image: postgres
    networks:
      - backend
```

- `web` 同时在两个网络，可作为反向代理
- `db` 仅在 backend 网络，外部无法直接访问

### 主机网络

直接使用主机网络栈（适合高性能场景）：

```yaml
services:
  app:
    image: myapp
    network_mode: host
    # 此时 ports 映射不生效
```

## 服务依赖与启动顺序

### depends_on

声明服务依赖关系：

```yaml
services:
  web:
    image: nginx
    depends_on:
      - app
    ports:
      - "8080:80"
  app:
    image: myapp
    depends_on:
      - db
  db:
    image: postgres
```

> **注意**：`depends_on` 只保证启动顺序，不等待服务就绪。应用需要自己实现重试逻辑或使用健康检查。

### 健康检查

配合健康检查实现等待服务就绪：

```yaml
services:
  db:
    image: postgres
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
  app:
    image: myapp
    depends_on:
      db:
        condition: service_healthy
```

## 多容器扩展模式

### 副本模式

```yaml
services:
  worker:
    image: myworker
    deploy:
      replicas: 3
```

### 资源限制

```yaml
services:
  app:
    image: myapp
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

## 配置复用模式

### extends：继承配置

```yaml
# common-services.yml
services:
  base:
    build: .
    environment:
      - APP_ENV=production
    restart: unless-stopped
```

```yaml
# docker-compose.yml
services:
  web:
    extends:
      file: common-services.yml
      service: base
    ports:
      - "8080:80"
  worker:
    extends:
      file: common-services.yml
      service: base
    command: python worker.py
```

### include：组合多个 Compose 文件

```yaml
include:
  - compose.base.yaml
  - compose.dev.yaml
```

或命令行指定多个文件：

```bash
podman-compose -f compose.yaml -f compose.override.yaml up
```

## profiles：条件启动

使用 profiles 选择性启动服务：

```yaml
services:
  web:
    image: nginx
    profiles:
      - web
  debug:
    image: busybox
    profiles:
      - debug
    command: sleep infinity
```

```bash
podman-compose --profile web up        # 只启动 web
podman-compose --profile debug up      # 启动 debug 及依赖
podman-compose --profile web --profile debug up  # 启动全部
```

## 标签与元数据

```yaml
services:
  app:
    image: myapp
    labels:
      - "com.example.description=My Application"
      - "com.example.environment=production"
    container_name: my-app  # 固定容器名（不推荐多副本场景）
```

## 重启策略

```yaml
services:
  app:
    image: myapp
    restart: unless-stopped
    # 可选值：
    # - "no"：不重启（默认）
    # - always：总是重启
    # - on-failure：失败时重启
    # - unless-stopped：除非手动停止否则重启
```

## 完整示例：WordPress

这是一个典型的双服务应用配置：

```yaml
---
volumes:
  db_data:
services:
  wordpress:
    image: docker.io/library/wordpress:latest
    ports:
      - 8080:80
    environment:
      - WORDPRESS_DB_HOST=db
      - WORDPRESS_DB_USER=wordpress
      - WORDPRESS_DB_PASSWORD=password
      - WORDPRESS_DB_NAME=wordpress
  db:
    image: docker.io/library/mariadb:10.6.4-focal
    command: '--default-authentication-plugin=mysql_native_password'
    volumes:
      - db_data:/var/lib/mysql
    environment:
      - MYSQL_ROOT_PASSWORD=somewordpress
      - MYSQL_DATABASE=wordpress
      - MYSQL_USER=wordpress
      - MYSQL_PASSWORD=password
```

## 相关概念

- [快速上手与 Compose Spec 兼容](00-introduction.md)
- [daemon-less 架构](01-daemonless-arch.md)
- [rootless 模式下的网络与卷](02-rootless.md)
- [WordPress 部署示例](../examples/01-wordpress.md)
- [多容器应用编排](../examples/02-multi-container.md)
