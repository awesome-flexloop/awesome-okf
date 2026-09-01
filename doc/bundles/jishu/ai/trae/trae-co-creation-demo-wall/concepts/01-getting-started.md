---
type: Concept
title: 快速开始
description: Demo Wall 的环境要求、安装步骤、环境变量配置、数据库初始化和开发服务器启动指南。
tags: [demo-wall, getting-started, installation, setup]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: "/references/demo-wall-source.md"
    title: "Demo Wall 源码信源"
---

## 环境要求

在开始之前，请确保本地环境满足以下条件：

| 依赖 | 最低版本 | 说明 |
|------|---------|------|
| Node.js | 20.x | Dockerfile 使用 node:20-slim，建议本地使用相同大版本 |
| PostgreSQL | 16 | docker-compose 使用 postgres:16-alpine |
| npm | 随 Node.js | 项目使用 npm 作为包管理器 |
| Git | 任意 | 克隆源码 |

可选依赖（用于本地对象存储而非 COS）：
- 腾讯云 COS 账号（生产环境需要，开发环境可跳过图片上传功能）

> 以上版本信息来自 F-005（Prisma datasource provider 为 postgresql）、F-134（Dockerfile base 镜像 node:20-slim）、F-138（docker-compose db 镜像 postgres:16-alpine）。

## 安装步骤

### 1. 克隆仓库

```bash
git clone <repository-url>
cd trae-co-creation-demo-wall
```

### 2. 安装依赖

```bash
npm install
```

`postinstall` 脚本会自动执行 `prisma generate`，生成 Prisma Client（F-012）。

### 3. 配置环境变量

复制环境变量模板并填写：

```bash
cp .env.example .env
```

必需的环境变量：

```env
# 数据库连接
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/trae_demo_wall?schema=public"
DIRECT_URL="postgresql://postgres:postgres@localhost:5432/trae_demo_wall"

# NextAuth 密钥（生产环境必须修改为随机字符串）
NEXTAUTH_SECRET="your-secret-key-here"
NEXTAUTH_URL="http://localhost:3000"

# 腾讯云 COS（开发环境可留空，图片上传功能不可用）
COS_SECRET_ID="your-cos-secret-id"
COS_SECRET_KEY="your-cos-secret-key"
COS_BUCKET="your-bucket-name"
COS_REGION="ap-guangzhou"
```

> 环境变量配置参考 F-099（COS 配置使用环境变量）、F-058（NextAuth 配置使用 NEXTAUTH_SECRET）、F-136（Dockerfile 构建参数包含这些变量）。

### 4. 初始化数据库

确保本地 PostgreSQL 服务正在运行，然后执行数据库推送：

```bash
npx prisma db push
```

这会根据 `prisma/schema.prisma` 中的 model 定义创建数据库表结构（F-027~F-047）。

### 5. 导入种子数据

```bash
npm run seed
```

种子脚本 `prisma/seed.ts` 会初始化以下数据（F-048~F-056）：

- **系统角色**：root（根用户）、admin（管理员）、common（普通角色）
- **系统字典**：
  - `audit_status`（审核状态）：0=待审核、1=已通过、2=已拒绝
  - `dev_status`（开发状态）：ideation=创意构思、prototype=初步原型、completed=功能完成、released=已可体验
  - `category_code`（作品分类）：utility=实用工具、scenario=场景应用、assistant=智能助手、content=内容创作、creative=创意实验、other=其他类型
  - `honor_type`（荣誉类型）：community_choice=社区精选、city_star=城市人气、best_of_year=城市推荐
  - `banned_users`（封禁用户黑名单）
  - `blocked_email_domains`（注册屏蔽域名）：example.com、example.org、example.net
- **国家城市数据**：从 `seed-data-countries.ts` 导入
- **默认管理员账号**：
  - 邮箱：`trae@example.com`
  - 密码：`trae1234`
  - 角色：root

### 6. 启动开发服务器

```bash
npm run dev
```

开发服务器启动后，访问 `http://localhost:3000`，会自动重定向到默认语言首页 `http://localhost:3000/zh-CN`（F-110, F-115）。

## npm scripts 一览

| 命令 | 说明 |
|------|------|
| `npm run dev` | 启动开发服务器（next dev） |
| `npm run build` | 构建生产版本（prisma generate && next build） |
| `npm run start` | 启动生产服务器（next start） |
| `npm run lint` | ESLint 代码检查 |
| `npm run seed` | 执行数据库种子（tsx prisma/seed.ts） |
| `npm run test:docker-deps` | 测试 Docker 依赖 |
| `npm run test:docker-runtime` | 测试运行时启动 |
| `npm run test:seed` | 测试 seed 序列 |
| `npm run test:deploy-config` | 测试部署配置 |

> 以上脚本定义来自 F-012。

## 开发快速验证

启动后可以验证以下功能：

1. **首页浏览**：访问 `/zh-CN`，查看作品列表（seed 不创建示例作品，列表为空）
2. **注册账号**：访问 `/zh-CN/sign-up`，注册新用户（自动分配 common 角色）
3. **管理员登录**：使用 `trae@example.com` / `trae1234` 登录
4. **管理后台**：登录后访问 `/zh-CN/console` 查看概览
5. **提交作品**：登录后访问 `/zh-CN/submit` 体验四步表单提交流程
6. **排行榜**：访问 `/zh-CN/rankings` 查看排行榜页面

## 使用 Docker 快速启动（可选）

如果不想本地安装 PostgreSQL，可以直接使用 docker-compose：

```bash
docker-compose up -d db redis
```

这会启动 PostgreSQL（端口 5432）和 Redis（端口 6379），然后配置 `.env` 中 `DATABASE_URL` 指向 localhost，再执行上述步骤 4-6。

完整 Docker 部署方式参见 [Docker 部署](15-docker-deployment.md)。

## 相关概念

- [项目简介](00-introduction.md)
- [架构总览](02-architecture-overview.md)
- [数据模型设计](03-data-model.md)
- [认证系统](04-auth-system.md)
- [Docker 部署](15-docker-deployment.md)
- [开发环境搭建示例](../examples/setup-dev-environment.md)
