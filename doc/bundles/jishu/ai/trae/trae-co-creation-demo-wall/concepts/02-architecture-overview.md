---
type: Concept
title: 架构总览
description: Demo Wall 的 Next.js 全栈架构设计，包括垂直分表数据模型、三层数据流、认证+审核+日志治理闭环和容器化部署架构。
tags: [demo-wall, architecture, nextjs, fullstack, overview]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: "/references/demo-wall-source.md"
    title: "Demo Wall 源码信源"
---

## Next.js 全栈架构

Demo Wall 采用 Next.js 15 App Router 全栈架构，前后端同仓库，Server Component 与 Client Component 混合渲染，Route Handler 提供 RESTful API。

### 架构分层

```
┌─────────────────────────────────────────────────────────┐
│                     浏览器（Client）                      │
│  ┌──────────┐  ┌───────────┐  ┌──────────────────────┐  │
│  │ React    │  │ Tiptap    │  │ @tsparticles         │  │
│  │ Components│  │ Rich Text │  │ 粒子背景              │  │
│  └────┬─────┘  └─────┬─────┘  └──────────┬───────────┘  │
│       │              │                   │              │
│  ┌────┴──────────────┴───────────────────┴───────────┐  │
│  │ 状态管理层                                          │  │
│  │  ┌──────────┐ ┌──────────────┐ ┌───────────────┐  │  │
│  │  │ zustand  │ │ react-query  │ │ react-hook-   │  │  │
│  │  │ (命令式   │ │ (声明式服务   │ │ form + zod    │  │  │
│  │  │  缓存)    │ │  端状态同步)  │ │ (表单状态)     │  │  │
│  │  └──────────┘ └──────────────┘ └───────────────┘  │  │
│  └───────────────────────┬───────────────────────────┘  │
└──────────────────────────┼──────────────────────────────┘
                           │ HTTP (fetch)
┌──────────────────────────┼──────────────────────────────┐
│                     Next.js 服务端                        │
│  ┌───────────────────────┴───────────────────────────┐  │
│  │              中间件链 (middleware.ts)                │  │
│  │  NextAuth auth → 受保护路由检查 → next-intl i18n    │  │
│  └───────────────────────┬───────────────────────────┘  │
│                          │                              │
│  ┌───────────────────────┴───────────────────────────┐  │
│  │              Route Handlers (/api/*)               │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌────────┐  │  │
│  │  │ 作品CRUD │ │ 认证/注册 │ │ 文件上传 │ │ 管理后台│  │  │
│  │  └────┬────┘ └────┬────┘ └────┬────┘ └───┬────┘  │  │
│  │       │           │           │           │        │  │
│  │  ┌────┴───────────┴───────────┴───────────┴─────┐  │  │
│  │  │   服务端工具层                                   │  │  │
│  │  │  prisma(单例) / auth(权限) / audit-log(日志)   │  │  │
│  │  │  ban(封禁) / rich-text(sanitize) / cos(存储)   │  │  │
│  └───────────────────────┬───────────────────────────┘  │
│                          │                              │
│  ┌───────────────────────┴───────────────────────────┐  │
│  │         Server Components (RSC)                    │  │
│  │  直接 import prisma 查询，减少 API 层开销           │  │
│  └───────────────────────┬───────────────────────────┘  │
└──────────────────────────┼──────────────────────────────┘
                           │ Prisma Client
┌──────────────────────────┼──────────────────────────────┐
│                     数据层                               │
│  ┌───────────────────────┴───────────────────────────┐  │
│  │              PostgreSQL 数据库                      │  │
│  │  Work 五表(垂直分表) + SysDict 字典 + RBAC         │  │
│  │  + 审核日志 + 认证/操作日志 + NextAuth 表           │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────┐  ┌────────────────────────────┐   │
│  │ 腾讯云 COS       │  │  Redis (基础设施预留)        │   │
│  │ (图片/头像存储)   │  │  (docker-compose中配置)     │   │
│  └──────────────────┘  └────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 目录结构总览

```
trae-co-creation-demo-wall/
├── src/
│   ├── app/                    # App Router 页面与API
│   │   ├── [language]/         # 国际化动态段（所有页面路由）
│   │   │   ├── console/        # 管理后台页面
│   │   │   ├── submit/         # 作品提交流程（4步向导）
│   │   │   ├── works/          # 作品详情/编辑
│   │   │   ├── profile/        # 个人资料
│   │   │   ├── rankings/       # 排行榜
│   │   │   ├── user/[id]/      # 用户公开主页
│   │   │   └── sign-in/sign-up # 认证页面
│   │   ├── api/                # API Route Handlers
│   │   │   ├── auth/           # NextAuth + 注册
│   │   │   ├── works/          # 作品 CRUD + 点赞/浏览/统计
│   │   │   ├── submit/         # 作品提交
│   │   │   ├── file/           # COS 文件上传/删除
│   │   │   ├── avatar/         # 头像上传
│   │   │   ├── console/        # 管理后台 API
│   │   │   ├── dictionaries/   # 字典管理
│   │   │   ├── tags/           # 标签管理
│   │   │   ├── users/          # 用户管理 + 封禁
│   │   │   ├── roles/          # 角色查询
│   │   │   ├── profile/        # 个人资料 + 修改密码
│   │   │   ├── rankings/       # 排行榜数据
│   │   │   └── logs/           # 审计日志查询
│   │   └── layout.tsx          # 根布局（空壳）
│   ├── components/             # React 组件
│   │   ├── auth/               # 登录/注册表单
│   │   ├── common/             # 通用组件（QueryProvider/HeroBanner等）
│   │   ├── crud/               # CRUD 通用组件（筛选/分页/反馈）
│   │   ├── layout/             # 布局组件（SiteLayout/粒子背景）
│   │   ├── ui/                 # shadcn/ui 基础组件
│   │   └── work/               # 作品业务组件
│   ├── lib/                    # 工具模块
│   │   ├── auth*.ts            # 认证（NextAuth配置+权限工具）
│   │   ├── prisma.ts           # Prisma 单例
│   │   ├── cos.ts              # COS 客户端
│   │   ├── crud.ts             # CRUD 常量
│   │   ├── audit-log.ts        # 审计日志写入
│   │   ├── ban.ts              # 用户封禁管理
│   │   ├── rich-text.ts        # 富文本 sanitize
│   │   ├── work-form.ts        # 表单 zod schema
│   │   ├── works-store.ts      # zustand store
│   │   ├── use-works.ts        # react-query Hook
│   │   ├── use-feedback.ts     # 反馈 Hook
│   │   ├── types.ts            # 类型定义
│   │   ├── utils.ts            # 工具函数（cn）
│   │   └── language/           # next-intl 三件套
│   ├── assets/                 # 静态资源
│   │   ├── translations/       # 三语翻译 JSON
│   │   ├── brand/              # 品牌 logo
│   │   └── globals.css         # 全局样式
│   └── middleware.ts           # 中间件（认证+i18n+路由保护）
├── prisma/                     # 数据库 schema 和 seed
│   ├── schema.prisma           # 17 个 model 定义
│   ├── seed.ts                 # 种子数据
│   └── seed-data-countries.ts  # 国家城市数据
├── Dockerfile                  # 三阶段构建
├── docker-compose.yml          # 五服务编排
├── entrypoint.sh               # 容器启动脚本
└── nginx.conf                  # Nginx 反向代理
```

> 目录结构来自 F-015~F-026。

## 垂直分表数据模型

作品（Work）是系统的核心实体，采用垂直分表设计将逻辑上的一个作品拆分为五个物理表（F-033~F-037）：

```
WorkBase (核心表)
├── id, userId(FK→SysUser), title, summary, coverUrl
├── countryCode, cityCode, categoryCode, devStatusCode
├── createdAt, updatedAt
├── indexes: [userId], [countryCode], [cityCode], [categoryCode]
│
├── WorkDetail (一对一, workId=PK)
│   ├── story(富文本), highlights(JSON), scenarios(JSON)
│   ├── demoUrl, repoUrl
│
├── WorkImage (一对多, workId=FK)
│   ├── id, imageUrl, imageType, sortOrder, createdAt
│
├── WorkTeam (一对一, workId=PK, unique)
│   ├── teamIntro, members(JSON), contactPhone, contactEmail
│
└── WorkStatistic (一对一, workId=PK)
    ├── auditStatus(0/1/2), displayStatus(0/1)
    ├── viewCount, likeCount, lastAuditAt
```

所有子表对 WorkBase 设置 `on delete: Cascade` 级联删除（F-034~F-037）。详见 [数据模型设计](03-data-model.md)。

## 三层数据流

数据访问明确分为三层，各司其职（F-098, F-107, F-109, F-119）：

1. **服务端数据层（Prisma）**：在 Server Component 和 Route Handler 中直接使用 Prisma Client 查询数据库，处理事务、权限检查、多表 JOIN、i18n 标签解析、HTML sanitize，返回净化后的 DTO。

2. **客户端命令式缓存（zustand）**：`useWorksStore` 用两个 Map 缓存作品列表（listCache，key 为序列化查询参数）和作品详情（detailCache）。提供 `setListCache`、`setDetailCache`、`getDetailCache` 命令式操作，用于列表点击时预填详情缓存实现"秒开"。

3. **客户端声明式状态同步（react-query）**：`useWorks` Hook 封装 `useQuery`，queryKey 为 `['works', params]`，staleTime=2分钟，自动处理 loading/error/缓存失效/后台刷新。

表单状态由 react-hook-form + zod 独立管理，与数据缓存层解耦。

Provider 嵌套顺序：SessionProvider → QueryProvider → NextIntlClientProvider → SiteLayout（F-118）。

详见 [CRUD 数据层](07-crud-layer.md)。

## 认证 + 审核 + 日志治理闭环

系统形成完整的治理闭环：

### 认证链路
- NextAuth v5 Credentials provider（邮箱+密码）→ bcryptjs 校验 → JWT session
- `authorize()` 回调检查 `isUserBanned()`，阻止被封禁用户登录（F-060）
- `jwt` callback 在 Node.js runtime 再次检查封禁状态，清空 `token.id` 使存量会话失效（F-062）
- `signIn` event 写入 SysAuthLog 并更新 `lastSignInAt`（F-064）

### 审核链路
- 作品提交后初始 `auditStatus=0`（待审），标签命中自动审核规则则直接通过（F-079）
- 管理员审核操作写入 WorkAuditLog（prevStatus→newStatus + 审核人 + 原因 + 时间）（F-039）
- `auditStatus`（0待审/1通过/2拒绝）与 `displayStatus`（0下架/1上架）正交独立（F-037）

### 日志链路
- **SysAuthLog**：认证事件（登录/注册/登出的成功/失败、IP、UA、metadata）（F-043）
- **SysOperationLog**：操作事件（模块+动作+目标+操作者+IP+UA+payload+成功/失败）（F-044）
- **WorkAuditLog**：审核状态变更链（F-039）
- 日志写入封装在 `lib/audit-log.ts`，统一 IP/UA 提取、BigInt 安全序列化、try-catch 不抛异常（F-102）

详见 [认证系统](04-auth-system.md)、[审核与治理](10-audit-governance.md)。

## 请求处理流程

一个典型的受保护页面请求（如提交作品）流程：

1. 浏览器请求 `/zh-CN/submit`
2. `middleware.ts` 执行：
   - NextAuth `auth()` wrapper 获取 session
   - 匹配 `isProtectedRoute` 正则，未登录 → 重定向到 `/zh-CN/sign-in?callbackUrl=/zh-CN/submit`
3. 已登录则请求到达 `[language]/submit/page.tsx`（Server Component）
4. 页面渲染时，客户端组件通过 `useWorks`（react-query）请求 `/api/works` 获取数据
5. API Route 中：
   - 通过 `getAuthUser()` 获取当前用户及角色
   - 使用 zod 校验参数
   - Prisma 事务执行数据库操作
   - 调用 `writeOperationLog()` 记录操作日志
   - 返回 JSON 响应
6. 客户端 react-query 更新缓存，zustand 可命令式更新详情缓存
7. 用户提交表单时，react-hook-form + zod 校验后 POST 到 `/api/submit`
8. 服务端 sanitize HTML → 事务写入五表 → 自动审核判断 → 记录日志 → 返回结果

## Docker 部署架构

```
                    ┌─────────────┐
                    │   Nginx     │ :80
                    │ (反向代理)   │
                    └──────┬──────┘
                           │ proxy_pass
                    ┌──────┴──────┐
                    │    App      │ :3000
                    │ (Next.js)   │
                    └──┬───────┬──┘
                       │       │
          ┌────────────┘       └────────────┐
          │                                 │
   ┌──────┴──────┐                   ┌──────┴──────┐
   │ PostgreSQL  │                   │    Redis    │
   │   :5432     │                   │   :6379     │
   └─────────────┘                   └─────────────┘
```

- **三阶段构建**：base（node:20-slim + openssl）→ builder（npm ci + prisma generate + next build）→ runner（standalone 输出，极小镜像）（F-134）
- **app-init 容器**：单独执行 `prisma db push` + `seed`，`restart: no` 确保只执行一次，避免多实例迁移冲突（F-137, F-138）
- **entrypoint.sh**：支持 `RUN_DB_INIT=true` 仅初始化模式和 `START_SERVER=true` 启动模式（F-137）
- **Nginx**：反向代理到 app:3000，提供静态文件服务（F-138, F-140）

详见 [Docker 部署](15-docker-deployment.md)。

## 相关概念

- [项目简介](00-introduction.md)
- [快速开始](01-getting-started.md)
- [数据模型设计](03-data-model.md)
- [认证系统](04-auth-system.md)
- [国际化路由](05-i18n-routing.md)
- [API 路由设计](06-api-routes.md)
- [CRUD 数据层](07-crud-layer.md)
- [审核与治理](10-audit-governance.md)
- [Docker 部署](15-docker-deployment.md)
