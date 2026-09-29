---
type: Example
title: Vercel 部署配置完整流程
description: 将 trae-co-creation-demo-wall-intl 部署到 Vercel 的完整步骤，包括项目导入、环境变量配置、数据库设置、Edge Config 集成、域名绑定和部署验证。
tags: [demo-wall, intl, vercel, deployment, serverless, edge-config]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/demo-wall-intl-source.md
    title: Demo Wall Intl 源码信源索引
---

## Vercel 部署概述

trae-co-creation-demo-wall-intl 采用 Vercel 优先的部署策略，移除了中文版的 nginx 反向代理和 Docker 多服务编排，适配 Vercel Serverless Functions 的运行时约束。部署流程包括：Vercel 项目创建 → 环境变量配置 → 数据库 provisioning → Prisma 迁移 → Edge Config 集成 → 域名绑定 → 部署验证。

## 前提条件

- 已注册 [Vercel](https://vercel.com) 账号
- GitHub/GitLab/Bitbucket 仓库已推送国际版代码
- 可访问 PostgreSQL 数据库（推荐 [Vercel Postgres](https://vercel.com/docs/storage/vercel-postgres) 或 [Neon](https://neon.tech)、[Supabase](https://supabase.com)）
- 已创建 [Vercel Edge Config](https://vercel.com/docs/storage/vercel-edge-config) 存储（用于字典缓存）
- 腾讯云 COS 账号（文件存储，如使用 S3 兼容存储可替换）

## 步骤一：导入项目

1. 登录 Vercel Dashboard，点击 **Add New → Project**
2. 选择国际版代码仓库（`trae-co-creation-demo-wall-intl`）
3. 框架预设应自动识别为 **Next.js**
4. 确认以下默认设置：
   - Build Command: `prisma generate && next build`（来自 package.json）
   - Output Directory: Next.js 默认（`.next`）
   - Install Command: `npm ci`（注意：国际版使用 `npm ci` 而非 `npm install`）
   - Node.js Version: 18.x 或更高

## 步骤二：配置环境变量

在 Vercel 项目 Settings → Environment Variables 中添加以下变量：

### 数据库

```
DATABASE_URL=postgresql://user:password@host:5432/dbname?pgbouncer=true
DIRECT_URL=postgresql://user:password@host:5432/dbname
```

> `DATABASE_URL` 用于 Prisma Client 日常查询（可经 PgBouncer），`DIRECT_URL` 用于迁移（直连）。

### NextAuth

```
NEXTAUTH_URL=https://your-domain.vercel.app
NEXTAUTH_SECRET=<openssl rand -base64 32 生成的密钥>
```

### 腾讯云 COS

```
COS_SECRET_ID=<腾讯云SecretId>
COS_SECRET_KEY=<腾讯云SecretKey>
COS_BUCKET=<bucket-name>
COS_REGION=ap-singapore（海外部署推荐新加坡节点）
```

### Edge Config

```
EDGE_CONFIG=<Vercel Edge Config Connection String>
EDGE_CONFIG_STORE_ID=<Edge Config Store ID>
```

### 可选配置

```
# Clerk 集成（如使用 Clerk OAuth）
CLERK_SECRET_KEY=
# Supabase（如使用 Supabase Auth）
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
```

## 步骤三：数据库初始化

首次部署后需要执行 Prisma 迁移和 seed 数据导入：

```bash
# 本地安装 Vercel CLI
npm i -g vercel

# 链接到 Vercel 项目
vercel link

# 拉取生产环境变量到本地 .env
vercel env pull .env.production.local

# 执行数据库迁移
npx prisma migrate deploy

# 导入初始数据（字典数据、管理员账号等）
npx prisma db seed
```

## 步骤四：Edge Config 字典同步

国际版使用 Edge Config 缓存字典数据，部署后需要手动触发初始同步：

```bash
# 调用同步 API（需要管理员权限）
curl -X POST https://your-domain.vercel.app/api/sync-edge-config \
  -H "Authorization: Bearer $NEXTAUTH_SECRET"
```

或在管理后台（Console → Dictionaries）点击"同步到 Edge Config"按钮。同步成功后，字典数据将缓存到 Vercel Edge Network，API 响应延迟显著降低。

## 步骤五：配置构建优化

在 `vercel.json` 中确认以下配置（国际版已内置）：

```json
{
  "buildCommand": "prisma generate && next build",
  "installCommand": "npm ci",
  "regions": ["sin1", "hnd1"],
  "functions": {
    "maxDuration": 30
  }
}
```

- `regions`: 选择靠近目标用户的边缘节点（东南亚推荐 sin1 新加坡）
- `maxDuration`: Serverless Function 最大执行时间，CSV 导出大数据量时可适当增加

## 步骤六：绑定自定义域名

1. Settings → Domains → 添加域名
2. 按 Vercel 指引配置 DNS 记录
3. 等待 SSL 证书自动签发（Let's Encrypt，通常几分钟）
4. 更新 `NEXTAUTH_URL` 环境变量为自定义域名
5. 重新部署以生效

## 步骤七：部署后验证

部署完成后执行以下检查：

```bash
# 1. 首页可访问
curl -sI https://your-domain.com | head -1
# 期望: HTTP/2 200

# 2. API 健康检查
curl -s https://your-domain.com/api/dictionaries | python -m json.tool | head -5
# 期望: 返回字典 JSON 数据

# 3. 登录功能（浏览器验证）
# 访问 /sign-in，测试注册和登录

# 4. Edge Config 缓存验证
# 响应头中应包含 x-edge-config-cache: HIT 或类似标识

# 5. 文件上传（COS 连通性）
# 登录后提交作品，上传图片验证 COS 直传
```

## 常见问题排查

### 构建失败：Prisma Client 生成错误

确保 `postinstall` 脚本正确执行 `prisma generate`，且 `DATABASE_URL` 在构建时可访问（或在 Vercel 中设置为预览/生产环境变量）。

### Serverless Function 超时

CSV 导出或大量数据查询可能触发超时。解决方案：
- 降低 CSV 导出上限（国际版默认 5000 条）
- 对查询添加分页
- 考虑使用 Edge Runtime 或增量导出

### Edge Config 连接失败

检查 `EDGE_CONFIG` 连接字符串是否正确，Edge Config Store 是否与 Vercel 项目在同一账号下。

### 中文显示乱码

确保 i18n 配置正确加载翻译文件，`next-intl` 的 `getRequestConfig` 中语言检测逻辑正常。

## Docker 备选部署

如需 Docker 部署（非 Vercel 环境），国际版保留了 Docker 兼容性：

```bash
# 使用 docker-compose 构建
docker compose -f docker-compose.yml up -d

# 注意：国际版 docker-compose.yml 已移除 nginx 服务
# 直接暴露 Next.js standalone 端口（3000）
# 需要外部反向代理（如 Caddy、Cloudflare Tunnel）处理 HTTPS
```

## 相关内容

- [Edge Config 缓存同步示例](edge-config-sync.md)
- [从中文版迁移指南](migrate-from-cn.md)
- [Vercel 部署概念](../concepts/05-vercel-deployment.md)
- [CSV 导出功能](../concepts/03-csv-export.md)
- [GDPR 合规审计留存](../concepts/04-gdpr-audit-retention.md)
