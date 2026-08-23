---
type: Example
title: 开发环境搭建完整示例
description: 从克隆仓库到 dev 服务器启动的全流程：安装依赖、.env 配置、数据库初始化、seed 导入、启动开发服务器。
tags: [demo-wall, example, setup, development, environment]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: "/references/demo-wall-source.md"
    title: "Demo Wall 源码信源"
---

## 前置条件

确保本地已安装：
- Node.js 20.x
- PostgreSQL 16（或使用 Docker 运行）
- Git

## 步骤 1：克隆仓库

```bash
git clone <repository-url>
cd trae-co-creation-demo-wall
```

## 步骤 2：安装依赖

```bash
npm install
```

postinstall 自动执行 `prisma generate`。

## 步骤 3：启动 PostgreSQL（Docker 方式）

如果不想本地安装 PostgreSQL，使用 docker-compose 启动数据库：

```bash
docker-compose up -d db
```

这会启动 PostgreSQL 在 localhost:5432，数据库名 trae_demo_wall，用户名/密码 postgres/postgres。

## 步骤 4：配置环境变量

复制模板并编辑：

```bash
cp .env.example .env
```

编辑 .env 文件（F-058, F-099）：

```env
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/trae_demo_wall?schema=public"
DIRECT_URL="postgresql://postgres:postgres@localhost:5432/trae_demo_wall"
NEXTAUTH_SECRET="dev-secret-key-change-in-production"
NEXTAUTH_URL="http://localhost:3000"
COS_SECRET_ID=""
COS_SECRET_KEY=""
COS_BUCKET=""
COS_REGION=""
```

> COS 配置留空时图片上传功能不可用，不影响其他功能开发。

## 步骤 5：初始化数据库

```bash
npx prisma db push
```

根据 schema.prisma 创建所有表。

## 步骤 6：导入种子数据

```bash
npm run seed
```

执行 prisma/seed.ts，创建（F-048~F-056）：
- 3 个系统角色（root/admin/common）
- 6 个系统字典及字典项
- 国家城市数据
- 默认管理员：trae@example.com / trae1234

## 步骤 7：启动开发服务器

```bash
npm run dev
```

访问 http://localhost:3000，自动重定向到 http://localhost:3000/zh-CN。

## 验证安装

1. 使用 trae@example.com / trae1234 登录
2. 访问 /zh-CN/console 进入管理后台
3. 访问 /zh-CN/submit 测试作品提交流程
4. 运行 lint 检查：`npm run lint`

## 常见问题

**Prisma Client 报错**：运行 `npx prisma generate` 重新生成。

**数据库连接失败**：确认 PostgreSQL 运行中，端口 5432 未被占用，DATABASE_URL 密码正确。

**端口 3000 被占用**：`npx next dev -p 3001` 使用其他端口。

## 相关内容

- [快速开始](/concepts/01-getting-started.md)
- [Docker 部署](/concepts/15-docker-deployment.md)
- [用户注册认证示例](/examples/user-registration-auth.md)
