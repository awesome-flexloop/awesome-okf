---
type: Concept
title: 与中文版完整差异对照
description: trae-co-creation-demo-wall-intl与中文版trae-co-creation-demo-wall的系统性差异对照表，涵盖系统功能、API、依赖、部署、默认配置等维度。
tags: [demo-wall, intl, diff, comparison, reference]
generated: { by: "reference_agent/trae-cn", at: 2026-04-22T00:00:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-04-22T00:00:00+08:00 }
status: stable
stale_after: 2026-10-22
sources:
  - id: src
    resource: /references/demo-wall-intl-source.md
    title: Demo Wall Intl 源码信源索引
---

本文档系统性地列出国际版（trae-co-creation-demo-wall-intl）与中文版（trae-co-creation-demo-wall）的所有差异点，作为差异查询的速查表。

## 系统功能差异

| 功能 | 中文版 | 国际版 | 差异说明 |
|------|--------|--------|---------|
| 用户封禁 | ✅ ban.ts + 封禁API + 内存缓存 | ❌ 完全移除 | 面向海外社区治理模式，减少运营复杂度 |
| 邮箱域名屏蔽 | ✅ isEmailDomainBlocked 检查 | ❌ 移除 | 随封禁系统一并移除 |
| 封禁状态检查 | ✅ authorize/jwt 回调检查 isUserBanned | ❌ 移除 | 无 ban.ts 模块，无封禁状态 |
| CSV 导出 | ❌ 无 | ✅ GET /api/console/works/export | 面向国际运营离线数据分析需求 |
| Edge Config 缓存 | ❌ 无 | ✅ 字典数据边缘缓存 | Vercel 部署性能优化，替代 Redis |
| Edge Config 同步 | ❌ 无 | ✅ POST /api/sync-edge-config | 管理员手动触发字典缓存同步 |
| 品牌资源 | ✅ assets/brand/logo.png/svg | ❌ 无 | 国际版不内置品牌 logo |
| 二维码功能 | ✅ qrcode/qrcode-generator 依赖 | ❌ 移除 | 无二维码分享功能 |
| 单元测试 | ❌ 无 test/ 目录 | ✅ test/filter-options-sort.test.ts | 新增测试覆盖 |
| CI 工作流 | ❌ 无 sync-cnb | ✅ .github/workflows/sync-cnb.yml | CNB 云原生构建同步 |

## API 差异

| API 端点 | 中文版 | 国际版 | 差异说明 |
|---------|--------|--------|---------|
| POST /api/users/[id]/ban | ✅ 封禁/解封用户 | ❌ 不存在 | 封禁功能移除 |
| POST /api/sync-edge-config | ❌ 不存在 | ✅ 同步字典到 Edge Config | intl 新增 |
| GET /api/console/works/export | ❌ 不存在 | ✅ 导出作品 CSV | intl 新增 |
| POST /api/auth/register | 检查 isEmailDomainBlocked | 不检查域名屏蔽 | 移除封禁系统连带影响 |
| NextAuth authorize 回调 | 检查 isUserBanned | 不检查封禁 | 移除封禁系统连带影响 |
| NextAuth jwt callback | 封禁后清空 token.id | 不处理封禁 | 移除封禁系统连带影响 |

共享 API（两版相同）：
- /api/works（GET列表/PUT更新）、/api/works/[id]（GET详情）
- /api/works/[id]/like、/api/works/[id]/view、/api/works/[id]/stats
- /api/works/likes、/api/works/filter-options、/api/submit
- /api/console/overview、/api/console/works、/api/console/works/[id]/likes
- /api/console/cities/stats、/api/dictionaries、/api/tags
- /api/users、/api/roles、/api/logs/auth、/api/logs/operations
- /api/file（COS上传/删除）、/api/avatar
- /api/profile、/api/profile/[id]、/api/profile/change-password
- /api/rankings

## 依赖差异

### 新增依赖

| 包名 | 版本 | 用途 |
|------|------|------|
| @vercel/edge-config | ^1.4.3 | Vercel Edge Config SDK，读取字典边缘缓存 |

### 移除依赖

| 包名 | 原用途 |
|------|--------|
| qrcode | 二维码生成 |
| qrcode-generator | 二维码生成（备用库） |

### 共享依赖（两版相同）

| 类别 | 包名 |
|------|------|
| 框架 | next@^15.3.3、react@^18.3.1、react-dom@^18.3.1 |
| 认证 | next-auth@^5.0.0-beta.30、@auth/prisma-adapter@^2.11.1、bcryptjs@^3.0.3 |
| 国际化 | next-intl@^4.8.3 |
| 数据库 | prisma@5.10.2、@prisma/client@5.10.2 |
| UI | Radix UI 全家桶、lucide-react、class-variance-authority、tailwind-merge、clsx、sonner |
| 编辑器 | Tiptap 全家桶、sanitize-html |
| 状态 | zustand、@tanstack/react-query、react-hook-form、@hookform/resolvers |
| 存储 | cos-nodejs-sdk-v5 |
| 校验 | zod@^4.3.6 |

## 数据模型差异

| 项目 | 中文版 | 国际版 |
|------|--------|--------|
| SysAuthLog.user onDelete | Cascade | **SetNull** |
| SysOperationLog.operator onDelete | Cascade | **SetNull** |
| DateTime 精度 | @db.Timestamptz(6)（微秒） | @db.Timestamptz（默认/毫秒） |

共享模型（两版相同）：
- WorkBase、WorkDetail、WorkImage、WorkTeam、WorkStatistic（五表分表）
- SysUser、SysRole、SysUserRole（RBAC 三角色）
- SysDict、SysDictItem（字典驱动，含 labelI18n）
- WorkAuditLog（作品审核日志）
- seed 数据（系统字典、角色、默认管理员、国家城市）

## 部署差异

| 项目 | 中文版 | 国际版 |
|------|--------|--------|
| 首要部署目标 | Docker 自托管 | Vercel 平台 |
| docker-compose 服务数 | 5（app/app-init/db/redis/nginx） | 4（app/app-init/db，无 redis/nginx） |
| 反向代理 | nginx 容器 | Vercel Edge CDN |
| 缓存层 | Redis（docker 容器） | Vercel Edge Config |
| Dockerfile 构建命令 | `npm ci` | `npm install` |
| entrypoint.sh | `prisma db push --accept-data-loss` | `prisma db push` |
| next.config.ts 注释 | "减小 Docker 镜像体积" | "避免 Vercel Lambda 100MB 限制" |
| 应用端口 | 通过 nginx 暴露 80 | 直接暴露 3000 |
| 品牌资源 | 打包在镜像中 | 无 |

## 国际化差异

| 项目 | 中文版 | 国际版 |
|------|--------|--------|
| 支持语言 | 3种 | 5种 |
| 语言列表 | zh-CN、en-US、ja-JP | en-US、zh-CN、ja-JP、id-ID、vi-VN |
| 默认语言 | zh-CN | en-US |
| 翻译文件数 | 3个 | 5个 |
| isProtectedRoute 正则 | `/^\/(zh-CN\|en-US)\/(submit\|console\|profile)/` | 相同（**Bug：未含 id-ID/vi-VN，也未含 ja-JP**） |

## 中间件差异

| 项目 | 中文版 | 国际版 |
|------|--------|--------|
| isProtectedRoute | 硬编码 zh-CN\|en-US | 硬编码 zh-CN\|en-US（同样遗漏 ja-JP、新增的 id-ID/vi-VN） |
| /api/auth 放行 | ✅ 相同 | ✅ 相同 |
| 受保护路由重定向 | ✅ 相同 | ✅ 相同 |
| /api 跳过 i18n | ✅ 相同 | ✅ 相同 |
| next-intl middleware | ✅ 相同 | ✅ 相同 |

## 目录结构差异

| 路径 | 中文版 | 国际版 | 差异 |
|------|--------|--------|------|
| src/lib/edge-config.ts | ❌ | ✅ | intl 新增 |
| src/lib/ban.ts | ✅ | ❌ | 封禁模块移除 |
| src/app/api/sync-edge-config/ | ❌ | ✅ | intl 新增 |
| src/app/api/console/works/export/ | ❌ | ✅ | intl 新增 |
| src/app/api/users/[id]/ban/ | ✅ | ❌ | 封禁 API 移除 |
| src/assets/brand/ | ✅ | ❌ | 品牌资源移除 |
| src/messages/id-ID.json | ❌ | ✅ | 印尼语翻译 |
| src/messages/vi-VN.json | ❌ | ✅ | 越南语翻译 |
| test/ | ❌ | ✅ | 单元测试目录 |
| .github/workflows/sync-cnb.yml | ❌ | ✅ | CI 工作流 |

## 前端架构差异

前端架构（App Router 双层 layout、Provider 嵌套顺序、UI 框架、状态管理三层分离）两版完全一致。唯一差异源于移除品牌 logo 和封禁相关 UI。

## 默认配置差异

| 配置项 | 中文版默认 | 国际版默认 |
|--------|-----------|-----------|
| 默认语言 | zh-CN | en-US |
| 用户注册邮箱域名检查 | 启用（屏蔽域名单） | 禁用 |
| 登录后封禁检查 | 启用 | 禁用 |
| 数据导出 | 不支持 | CSV 导出 |
| 字典数据读取 | 直接查数据库 | Edge Config 优先，数据库降级 |

## 共享架构清单

以下架构组件两版完全一致，本 bundle 不重复文档化，请参阅中文版对应文档：

- 五表垂直分表模型（WorkBase/WorkDetail/WorkImage/WorkTeam/WorkStatistic）
- RBAC 权限模型（SysUser/SysRole/SysUserRole，三角色 root/admin/common）
- NextAuth 认证配置（PrismaAdapter + JWT session + Credentials provider）
- session callback、signIn event 逻辑
- COS 文件存储（环境变量配置、上传路径、类型/大小限制、删除 API）
- Tiptap 富文本编辑器 + sanitize-html 清洗
- App Router 双层 layout 架构
- Provider 嵌套顺序（SessionProvider → QueryProvider → NextIntlClientProvider → SiteLayout + Toaster）
- Tailwind CSS + shadcn/ui + Radix UI 组件体系
- zustand 客户端缓存 + react-query 服务端数据（staleTime=2分钟）三层状态分离
- 字典驱动模型（SysDict/SysDictItem + labelI18n）
- 审核双状态机（auditStatus/displayStatus）
- Docker 三阶段构建（base → builder → runner）
- entrypoint.sh 可选 DB 初始化 + seed + 启动 server 逻辑

## 相关概念

- [Demo Wall Intl 简介](/concepts/00-introduction.md)
- [Vercel Edge Config缓存](/concepts/01-edge-config-cache.md)
- [5语言国际化](/concepts/02-multi-language.md)
- [CSV导出功能](/concepts/03-csv-export.md)
- [GDPR合规审计留存](/concepts/04-gdpr-audit-retention.md)
- [Vercel部署](/concepts/05-vercel-deployment.md)
- [从中文版迁移到国际版指南](/examples/migrate-from-cn.md)
