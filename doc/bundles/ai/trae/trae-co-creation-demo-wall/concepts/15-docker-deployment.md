---
type: Concept
title: Docker 部署
description: Demo Wall 的三阶段 Dockerfile、docker-compose 五服务编排（app/postgres/redis/nginx）、entrypoint.sh 迁移等待、Nginx 反向代理、2C8G 生产配置。
tags: [demo-wall, docker, deployment, nginx, postgresql, redis]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: "/references/demo-wall-source.md"
    title: "Demo Wall 源码信源"
---

## 三阶段 Dockerfile（F-134）

### base 阶段

- 基础镜像：`node:20-slim`（使用国内镜像源 `docker.cnb.cool/.../node:20-slim_amd64`）（F-135）
- 安装 openssl、ca-certificates（Prisma 需要）
- 配置清华 Debian 镜像源加速国内构建
- 设置工作目录 /app

### builder 阶段

- 在 base 基础上安装构建依赖：python3、make、g++（部分 npm 包需要编译）
- 复制 package.json、package-lock.json
- `npm ci` 安装所有依赖（含 devDependencies）
- 复制 prisma schema 和源码
- 构建参数传入环境变量（F-136）：COS_SECRET_ID、COS_SECRET_KEY、COS_BUCKET、COS_REGION、NEXTAUTH_SECRET
- DATABASE_URL 使用占位符（构建时不需要数据库连接）
- `prisma generate` 生成 Prisma Client
- `npm run build`（prisma generate && next build）构建 Next.js

### runner 阶段

- 基础镜像：node:20-slim
- 仅安装生产必需的 openssl
- 复制 standalone 输出（Next.js output='standalone' 自动追踪依赖）
- 复制 .next/static 静态资源
- 复制 prisma 目录（schema + seed）
- 复制必要的 node_modules（Prisma 等运行时需要的）
- 复制 entrypoint.sh
- EXPOSE 3000
- CMD ["sh", "entrypoint.sh"]

Next.js 配置 `output: 'standalone'` 自动追踪用到的依赖，输出仅几十 MB，配合 `outputFileTracingExcludes` 排除 @next/swc-* 和 @swc/core-* 二进制进一步压缩镜像（F-125）。

## entrypoint.sh 启动脚本（F-137）

支持两种模式，通过环境变量切换：

### 初始化模式（RUN_DB_INIT=true）

1. 等待 db:5432 端口可用（循环检测）
2. 执行 `prisma db push --accept-data-loss` 同步数据库 schema
3. 执行 `tsx prisma/seed.ts` 导入种子数据（失败不中断）
4. 如果 START_SERVER≠true，退出（初始化容器用）

### 启动模式

执行 `node server.js` 启动 Next.js standalone 服务器。

## docker-compose 五服务编排（F-138~F-141）

| 服务 | 镜像 | 端口 | 说明 |
|------|------|------|------|
| app | 构建的镜像 | 3000 | 主应用，依赖 app-init 完成后启动 |
| app-init | 同app | — | 初始化容器，RUN_DB_INIT=true, START_SERVER=false, restart:no |
| db | postgres:16-alpine | 5432 | 数据库 trae_demo_wall，性能调优（max_connections=100, shared_buffers=256MB） |
| db-dev | postgres:16-alpine | 5433 | 开发数据库 trae_demo_wall_dev |
| redis | redis:7-alpine | 6379 | 256MB LRU 缓存（基础设施预留） |
| nginx | nginx:alpine | 80 | 反向代理到 app:3000 |

### 为什么需要 app-init？

如果部署多个 app 实例（水平扩展），多个容器同时执行 prisma migrate 会冲突。app-init 用 `restart: no` 确保只执行一次，成功后退出，app 容器通过 depends_on 等待它完成再启动。

### 数据库连接串（F-139）

```
DATABASE_URL=postgresql://postgres:postgres@db:5432/trae_demo_wall?schema=public&connection_limit=20&pool_timeout=20&connect_timeout=10
DIRECT_URL=postgresql://postgres:postgres@db:5432/trae_demo_wall
```

### Volumes 和 Network

- volumes：postgres-data、postgres-dev-data、redis-data（数据持久化）
- network：trae-network（bridge 驱动，服务间通信）

## 多环境配置（F-140）

| 文件 | 用途 |
|------|------|
| docker-compose.yml | 开发/基础配置 |
| docker-compose.2c8g.yml | 2核8G低配服务器配置 |
| docker-compose.prod.yml | 生产环境配置 |

## Nginx 配置（F-140）

- nginx.conf：反向代理到 app:3000 的标准配置
- nginx-lb.conf / nginx-lb-2.conf：负载均衡配置（多 app 实例场景）

## 环境变量

必需的环境变量（.env.example / .env.docker.example）：
- DATABASE_URL、DIRECT_URL
- NEXTAUTH_SECRET、NEXTAUTH_URL
- COS_SECRET_ID、COS_SECRET_KEY、COS_BUCKET、COS_REGION

## 测试脚本（F-012）

package.json 中定义的部署相关测试：
- test:docker-deps：Docker 依赖测试
- test:docker-runtime：运行时启动测试
- test:seed：seed 序列测试
- test:deploy-config：部署配置测试

## 相关概念

- [快速开始](/concepts/01-getting-started.md)
- [架构总览](/concepts/02-architecture-overview.md)
- [COS 对象存储](/concepts/09-cos-storage.md)
- [测试体系](/concepts/16-testing.md)
- [Docker部署示例](/examples/docker-deploy.md)
