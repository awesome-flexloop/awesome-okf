---
type: Example
title: Docker 部署示例
description: 使用 docker-compose 部署 Demo Wall 的完整流程：环境变量配置、数据库迁移、Nginx 反向代理、生产配置。
tags: [demo-wall, example, docker, deploy, nginx, production]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: "/references/demo-wall-source.md"
    title: "Demo Wall 源码信源"
---

## 部署架构

使用 docker-compose 编排 5 个服务（F-138）：

```
用户 → Nginx(:80) → App(:3000) → PostgreSQL(:5432)
                              ↘ Redis(:6379)
```

App 启动前由 app-init 容器执行数据库迁移和 seed（F-137）。

## 步骤 1：准备环境

安装 Docker 和 docker-compose：

```bash
docker --version
docker-compose --version
```

## 步骤 2：配置环境变量

创建 `.env` 文件（参考 .env.docker.example）：

```env
# 数据库
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=trae_demo_wall

# 应用
DATABASE_URL=postgresql://postgres:your-secure-password@db:5432/trae_demo_wall?schema=public&connection_limit=20&pool_timeout=20&connect_timeout=10
DIRECT_URL=postgresql://postgres:your-secure-password@db:5432/trae_demo_wall
NEXTAUTH_SECRET=your-production-secret-key-change-this
NEXTAUTH_URL=https://your-domain.com

# 腾讯云 COS
COS_SECRET_ID=your-cos-secret-id
COS_SECRET_KEY=your-cos-secret-key
COS_BUCKET=your-bucket-name
COS_REGION=ap-guangzhou
```

> **重要**：生产环境必须修改 NEXTAUTH_SECRET 为强随机字符串，数据库密码不要使用默认值。

## 步骤 3：构建并启动

### 开发/测试环境

```bash
docker-compose up -d --build
```

这会：
1. 构建三阶段 Docker 镜像
2. 启动 db（PostgreSQL）、redis、app-init（执行迁移和seed）
3. app-init 完成后自动退出（restart: no）
4. 启动 app（Next.js 服务）
5. 启动 nginx（反向代理）

### 生产环境

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

### 2核8G 低配服务器

```bash
docker-compose -f docker-compose.yml -f docker-compose.2c8g.yml up -d --build
```

## 步骤 4：验证部署

```bash
# 检查容器状态
docker-compose ps

# 检查应用日志
docker-compose logs -f app

# 检查初始化日志
docker-compose logs app-init
```

验证访问：

```bash
curl http://localhost/zh-CN
# 应返回 HTML 页面
```

默认管理员账号：trae@example.com / trae1234（F-056）。

## Dockerfile 三阶段构建说明（F-134）

### base 阶段

```dockerfile
FROM node:20-slim AS base
# 安装 openssl（Prisma 需要）
# 配置国内镜像源加速
WORKDIR /app
```

### builder 阶段

```dockerfile
FROM base AS builder
# 安装构建依赖（python3/make/g++）
# npm ci（使用 lock 文件确保依赖版本一致）
# 构建参数传入 COS/NEXTAUTH 环境变量
# prisma generate && next build
```

注意 DATABASE_URL 使用占位符，构建时不需要真实数据库连接。

### runner 阶段

```dockerfile
FROM base AS runner
# 仅复制 standalone 输出（自动追踪依赖，极小镜像）
# 复制 .next/static（静态资源）
# 复制 prisma 目录（schema + seed）
# 复制必要的 node_modules
EXPOSE 3000
CMD ["sh", "entrypoint.sh"]
```

Next.js `output: 'standalone'` 配合 `outputFileTracingExcludes` 排除 SWC 二进制，大幅减小镜像体积（F-125）。

## entrypoint.sh 启动逻辑（F-137）

```bash
#!/bin/sh
if [ "$RUN_DB_INIT" = "true" ]; then
  # 等待数据库可用
  wait-for-it db:5432 -t 60

  # 推送 schema
  npx prisma db push --accept-data-loss

  # 导入种子数据（失败不中断）
  npx tsx prisma/seed.ts || echo "Seed failed, continuing..."
fi

if [ "$START_SERVER" != "true" ]; then
  exit 0  # 仅初始化模式
fi

# 启动应用
node server.js
```

app-init 容器：RUN_DB_INIT=true, START_SERVER=false
app 容器：RUN_DB_INIT=false（或不设）, START_SERVER=true（默认）

## Nginx 配置

nginx.conf 配置反向代理（F-140）：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 静态资源缓存
    location /_next/static/ {
        proxy_pass http://app:3000;
        expires 30d;
    }

    # API 和页面请求代理到 app
    location / {
        proxy_pass http://app:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

负载均衡场景使用 nginx-lb.conf 或 nginx-lb-2.conf。

## 常用运维命令

```bash
# 查看日志
docker-compose logs -f app

# 重启应用
docker-compose restart app

# 重新执行 seed（谨慎）
docker-compose run --rm -e RUN_DB_INIT=true -e START_SERVER=false app sh entrypoint.sh

# 备份数据库
docker-compose exec db pg_dump -U postgres trae_demo_wall > backup.sql

# 恢复数据库
cat backup.sql | docker-compose exec -T db psql -U postgres trae_demo_wall

# 停止所有服务
docker-compose down

# 停止并删除数据卷（彻底清除）
docker-compose down -v
```

## 生产环境建议

1. **HTTPS**：在 Nginx 前加 SSL 终止（Let's Encrypt + certbot），或使用云负载均衡
2. **数据库持久化**：确保 postgres-data volume 挂载到可靠存储
3. **资源限制**：2C8G 配置下合理设置 PostgreSQL shared_buffers 和 Redis maxmemory
4. **日志收集**：配置 Docker 日志驱动或挂载日志目录
5. **备份策略**：定期备份 PostgreSQL 数据卷
6. **安全组**：只暴露 80/443 端口，数据库端口不对外
7. **NEXTAUTH_SECRET**：使用 `openssl rand -base64 32` 生成强密钥

## 相关内容

- [Docker 部署](../concepts/15-docker-deployment.md)
- [快速开始](../concepts/01-getting-started.md)
- [测试体系](../concepts/16-testing.md)
- [开发环境搭建示例](setup-dev-environment.md)
