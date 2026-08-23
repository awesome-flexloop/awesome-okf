---
type: Concept
title: Demo Wall 项目简介
description: trae-co-creation-demo-wall 是一个基于 Next.js 15 全栈框架构建的 AI 共创作品展示平台，支持作品提交、审核、展示、点赞排行等完整功能。
tags: [demo-wall, introduction, nextjs, fullstack]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: "/references/demo-wall-source.md"
    title: "Demo Wall 源码信源"
---

## 什么是 Demo Wall

**trae-co-creation-demo-wall**（简称 Demo Wall）是一个面向 AI 共创社区的作品展示与分享平台。它为创作者提供作品提交、富文本编辑、图片上传、团队协作信息录入等完整的提交流程，为管理员提供审核治理、用户管理、字典配置、日志审计等后台能力，为普通用户提供作品浏览、筛选搜索、点赞收藏、排行榜等展示功能。

项目采用 Next.js 15 App Router 全栈架构，前后端同仓库，Prisma ORM 操作 PostgreSQL 数据库，NextAuth v5 处理认证，next-intl 实现三语国际化，Tiptap 提供富文本编辑，腾讯云 COS 存储图片资源，Docker 三阶段构建支持容器化部署。

## 技术栈总览

| 层面 | 技术选型 | 版本 |
|------|---------|------|
| 核心框架 | Next.js (App Router) | ^15.3.3 |
| UI 库 | React | ^18.3.1 |
| 数据库 ORM | Prisma | 5.10.2 |
| 数据库 | PostgreSQL | — |
| 认证 | NextAuth (Auth.js v5 beta) | ^5.0.0-beta.30 |
| 国际化 | next-intl | ^4.8.3 |
| 富文本编辑 | Tiptap | ^3.20.4 |
| 富文本安全 | sanitize-html | ^2.17.2 |
| 状态管理 | zustand | ^5.0.3 |
| 服务端状态 | @tanstack/react-query | ^5.95.2 |
| 表单处理 | react-hook-form | ^7.71.2 |
| 校验 | zod | ^4.3.6 |
| UI 组件 | Radix UI + shadcn/ui | 多个包 |
| 样式 | Tailwind CSS | — |
| 对象存储 | 腾讯云 COS (cos-nodejs-sdk-v5) | ^2.15.4 |
| 粒子动效 | @tsparticles/react + @tsparticles/slim | ^3.0.0 / ^3.9.1 |
| 密码加密 | bcryptjs | ^3.0.3 |
| 容器化 | Docker + docker-compose | — |
| 反向代理 | Nginx | — |

> 以上依赖版本来自 F-002~F-011。

## 核心特性

1. **垂直分表的作品数据模型**：作品数据拆分为 WorkBase/WorkDetail/WorkImage/WorkTeam/WorkStatistic 五表，按读写频率和数据关系精准切分，支持高效列表查询和高频计数更新（F-033~F-037）。

2. **RBAC + 动态字典双层架构**：root/admin/common 三角色硬编码保障安全，SysDict/SysDictItem 字典表驱动分类配置（审核状态/开发状态/作品分类/荣誉类型/国家城市/封禁名单/屏蔽域名），运营可动态增删改无需发版（F-028~F-032, F-048~F-055）。

3. **[language] 动态段国际化**：URL 前缀方案（/zh-CN/...、/en-US/...、/ja-JP/...），三层中间件链处理认证→受保护路由→i18n 语言检测，双层 layout 设计支持 per-locale `lang` 属性（F-110~F-118, F-126~F-129）。

4. **三层数据访问分离**：服务端 Prisma 直接查询+事务处理 → zustand 命令式缓存（预填详情避免闪烁） → react-query 声明式数据获取（staleTime=2分钟），各司其职（F-098, F-107, F-109）。

5. **富文本 + COS 直传内容管线**：Tiptap 编辑器 → 服务端 sanitize-html 白名单净化 → COS 服务端代理上传（5MB/类型限制） → 事务五表原子写入 + 标签自动审核（F-007, F-086~F-087, F-104, F-079）。

6. **双状态审核 + 三类审计日志治理闭环**：auditStatus（0待审/1通过/2拒绝）+ displayStatus（0下架/1上架）双状态正交独立；WorkAuditLog 审核链 + SysAuthLog 认证日志 + SysOperationLog 操作日志全覆盖；用户封禁双重检查（authorize + jwt callback）+ 60秒缓存（F-037, F-039, F-043~F-044, F-060, F-062, F-102~F-103）。

7. **Docker 三阶段构建 + 五服务编排**：base→builder→runner 极小镜像，app-init 初始化容器防迁移冲突，docker-compose 编排 app/db/db-dev/redis/nginx，entrypoint.sh 支持初始化/启动双模式（F-134~F-141）。

## 能力边界

**Demo Wall 是一个面向特定社区场景的作品展示平台，不是通用 CMS 或博客系统。** 它的设计取舍包括：

- **认证方式**：仅配置 Credentials provider（邮箱+密码登录），不包含 OAuth 社交登录（代码中有 Account/Session 等 NextAuth 标准表，预留了扩展能力但未配置 OAuth providers）（F-059）。
- **部署目标**：以 Docker 自托管为主，standalone 输出适配容器化，非 Vercel Serverless 优先（F-125, F-134）。
- **国际化覆盖**：支持中/英/日三语，未包含右向语言（RTL）支持；中间件受保护路由正则硬编码语言前缀（F-114, F-126）。
- **富文本能力**：白名单严格（p/br/strong/em/u/s/h2/h3/ul/ol/li/a/blockquote/code），不支持图片嵌入、表格、视频等复杂格式（F-104）。
- **文件存储**：固定使用腾讯云 COS，未抽象存储层接口（F-099）。
- **Redis 使用**：docker-compose 中包含 redis 服务，但应用代码中未见 Redis 作为缓存/会话存储的使用，为基础设施预留（F-138）。
- **intl 版本差异**：存在 intl 分支版本，支持 5 种语言（增加 id-ID/vi-VN）、Vercel Edge Config 缓存字典、CSV 导出功能，但缺少用户封禁/域名屏蔽功能（F-142~F-163）。

## 支持的语言

- **zh-CN**（简体中文，默认语言）
- **en-US**（英文）
- **ja-JP**（日文）

(F-126)

## 版本与许可

- **项目版本**：0.0.0（初始开发版本）
- **可见性**：私有仓库（private: true）
- **许可证**：详见项目根目录 LICENSE 文件（F-001, F-026）

## 相关概念

- [快速开始](/concepts/01-getting-started.md)
- [架构总览](/concepts/02-architecture-overview.md)
- [数据模型设计](/concepts/03-data-model.md)
- [认证系统](/concepts/04-auth-system.md)
- [国际化路由](/concepts/05-i18n-routing.md)
