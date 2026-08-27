---
type: Concept
title: Vercel 部署
description: intl版部署目标从Docker自托管转向Vercel平台（"Vercel优先，Docker兼容"），适配包括outputFileTracingExcludes、Edge Config集成、移除nginx、npm install替代npm ci、移除--accept-data-loss等。
tags: [demo-wall, intl, vercel, deployment, docker, serverless, edge-config]
generated: { by: "reference_agent/trae-cn", at: 2026-04-22T00:00:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-04-22T00:00:00+08:00 }
status: stable
stale_after: 2026-10-22
sources:
  - id: src
    resource: /references/demo-wall-intl-source.md
    title: Demo Wall Intl 源码信源索引
---

## 部署范式迁移

国际版的部署定位是**"Vercel 优先，Docker 兼容"**：

| 维度 | 中文版（Docker 优先） | 国际版（Vercel 优先） |
|------|---------------------|---------------------|
| 首要部署平台 | Docker 自托管 | Vercel Serverless 平台 |
| Web 服务器 | nginx 反向代理 | Vercel Edge CDN（自动 SSL、全球 CDN） |
| 数据库 | Docker PostgreSQL | 外部托管 PostgreSQL（Neon/Supabase 等） |
| 缓存 | Docker Redis | Vercel Edge Config（字典数据） |
| 构建命令 | `npm ci`（确定性构建） | `npm install`（更容错） |
| 数据库迁移 | `prisma db push --accept-data-loss` | `prisma db push`（保守模式） |
| 反向代理 | nginx 容器 | 不需要（Vercel 接管） |
| 端口映射 | nginx:80 → app:3000 | 直接暴露 3000（Vercel 路由） |

### 为什么保留 Docker 配置

Vercel 虽方便但有局限，保留 Docker 配置给用户选择余地：
- **Vercel 快速体验**：导入 GitHub 仓库即可部署，适合演示和轻量使用
- **Docker 生产部署**：自有服务器、需完全控制环境、数据库内网访问等场景
- **本地开发**：Docker Compose 仍是最方便的本地一键启动方式

## Vercel 适配改动详解

### 1. next.config.ts：Lambda 体积优化

```typescript
// next.config.ts
// 排除不需要的文件以避免 Vercel Lambda 100MB 限制
// （中文版注释为"减小 Docker 镜像体积"）
outputFileTracingExcludes: {
  '*': [
    'node_modules/@swc/core-linux-x64-gnu',
    'node_modules/@swc/core-linux-x64-musl',
  ]
}
```

Vercel Serverless Function 有 250MB（解压后）的包大小限制，outputFileTracingExcludes 用于排除构建时不需要的原生二进制文件，减小 Lambda 体积。

### 2. Dockerfile：npm install 替代 npm ci

```dockerfile
# 中文版：npm ci（要求 lockfile 完全一致）
# 国际版：npm install（更宽松，容忍依赖解析差异）
RUN npm install
```

| 命令 | 特点 | 适用场景 |
|------|------|---------|
| `npm ci` | 严格按照 package-lock.json 安装，lockfile 与 package.json 不一致时报错 | CI/CD 确定性构建 |
| `npm install` | 根据 package.json 安装，可能更新 lockfile，更容错 | Vercel 构建环境 |

Vercel 构建环境有时会有依赖解析差异（Node.js 版本、平台架构等），`npm install` 更容错。Docker 部署场景下用户可自行改回 `npm ci`。

### 3. entrypoint.sh：移除 --accept-data-loss

```bash
# 中文版：自动接受数据丢失风险
# npx prisma db push --accept-data-loss

# 国际版：保守模式，需要手动确认
npx prisma db push
```

`--accept-data-loss` 会在 schema 变更可能导致数据丢失时（如删除列、更改字段类型）自动确认，适合开发环境但生产环境有风险。移除后，Prisma 会在检测到潜在数据丢失时提示手动确认，更安全但初始化流程更保守。

### 4. docker-compose.yml：移除 nginx 和 Redis

**中文版五服务编排**：
```yaml
services:
  app:         # Next.js 应用
  app-init:    # 初始化（DB push + seed）
  db:          # PostgreSQL
  redis:       # Redis 缓存
  nginx:       # Nginx 反向代理（端口 80 → 3000）
```

**国际版精简编排**：
```yaml
services:
  app:         # Next.js 应用（直接暴露 3000）
  app-init:    # 初始化
  db:          # PostgreSQL
  # redis:     # 移除（字典缓存改用 Edge Config）
  # nginx:     # 移除（Vercel 提供 CDN/SSL）
```

移除 nginx 的原因：Vercel 部署自带全球 CDN、自动 SSL 证书、边缘缓存；Docker 部署场景下用户可自行配置反向代理。

### 5. Edge Config 集成

Vercel 原生服务集成，详见 [Vercel Edge Config缓存](01-edge-config-cache.md)。

## Vercel 部署必需环境变量

| 变量名 | 必需 | 说明 |
|--------|:----:|------|
| `DATABASE_URL` | ✅ | PostgreSQL 连接字符串（Neon/Supabase/自建） |
| `NEXTAUTH_SECRET` | ✅ | NextAuth JWT 加密密钥 |
| `COS_SECRET_ID` | ✅ | 腾讯云 COS SecretId |
| `COS_SECRET_KEY` | ✅ | 腾讯云 COS SecretKey |
| `COS_BUCKET` | ✅ | COS 存储桶名称 |
| `COS_REGION` | ✅ | COS 地域 |
| `EDGE_CONFIG` | 推荐 | Vercel Edge Config 连接字符串（自动注入） |
| `EDGE_CONFIG_ID` | ✅* | Edge Config 实例 ID（sync-edge-config API 需要） |
| `VERCEL_API_TOKEN` | ✅* | Vercel Management API Token（sync-edge-config API 需要） |
| `ADMIN_EMAIL` | 推荐 | 默认管理员邮箱（seed 使用） |
| `ADMIN_PASSWORD` | 推荐 | 默认管理员密码（seed 使用） |

*标注项仅在使用 Edge Config 字典缓存同步功能时必需。

## Vercel 部署限制与注意事项

### Serverless Function 限制

| 限制项 | Hobby（免费） | Pro（付费） |
|--------|:------------:|:-----------:|
| 执行超时 | 10秒 | 60秒 |
| 函数内存 | 1024MB | 1024MB |
| 包大小（解压） | 250MB | 250MB |

影响：
- CSV 导出 5000 条上限要考虑 60 秒执行时间限制
- Prisma 在 Serverless 环境下需要注意连接池管理（建议使用 PgBouncer 或 Prisma Data Proxy）

### Edge Runtime 权衡

部分 API 路由可以考虑使用 Edge Runtime 获得更低延迟，但存在限制：
- Edge Runtime 不支持 Node.js 原生 API（如 fs、child_process）
- Prisma 目前不完全兼容 Edge Runtime（需要 Data Proxy/Accelerate）
- ban.ts 的内存缓存机制在 Edge Runtime 下不工作（国际版已移除 ban.ts 消除了此问题）

### 文件系统只读

Vercel 部署的文件系统是只读的，文件上传必须走外部存储（腾讯云 COS），不能写本地磁盘。国际版已使用 COS 存储，无需改动。

### 冷启动优化

Serverless Function 冷启动时间受代码体积影响：
- outputFileTracingExcludes 减小包体积，降低冷启动时间
- Edge Config 缓存字典数据减少冷启动时的数据库查询
- 避免在模块顶层执行重计算或大模块导入

## Docker 兼容部署

国际版保留了 Docker 部署能力，主要用于：
- **本地开发**：`docker-compose up -d` 一键启动
- **自托管生产环境**：在自有服务器上部署
- **无 Vercel 账户场景**：Docker 是唯一选择

Docker 部署注意事项：
- 需要自行配置反向代理（nginx/Caddy/云LB）处理 SSL 和域名
- 外部 PostgreSQL（可使用 docker-compose 中的 db 服务或外部数据库）
- Edge Config 功能不可用（无 Vercel 环境），字典数据直接查数据库
- 建议将 Dockerfile 中的 `npm install` 改为 `npm ci` 确保确定性构建
- 建议生产环境使用 `prisma migrate deploy` 而非 `prisma db push`

## CI/CD

国际版新增 `.github/workflows/sync-cnb.yml` CI 工作流（CNB 云原生构建平台同步）。Vercel 部署通常配合 GitHub 集成，推送代码自动触发部署。项目包含 `test/` 目录，建议在 CI 中运行单元测试。

## 相关概念

- [Demo Wall Intl 简介](00-introduction.md)
- [Vercel Edge Config缓存](01-edge-config-cache.md)
- [与中文版完整差异对照](06-differences-from-cn.md)
- [Vercel部署配置示例](../examples/setup-vercel-deployment.md)
- [从中文版迁移到国际版指南](../examples/migrate-from-cn.md)
