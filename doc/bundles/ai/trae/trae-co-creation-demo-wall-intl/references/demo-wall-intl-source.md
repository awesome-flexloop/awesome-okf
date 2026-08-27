---
type: Reference
title: Demo Wall Intl 源码信源索引
description: trae-co-creation-demo-wall-intl 国际版变体的源码文件索引，标注与中文版的差异文件和共享架构引用
tags: [demo-wall, intl, source, reference, vercel, i18n]
generated: { by: "reference_agent/trae-cn", at: 2026-04-22T00:00:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-04-22T00:00:00+08:00 }
status: stable
stale_after: 2026-10-22
sources:
  - id: intl-repo
    resource: https://github.com/xinetzone/trae-co-creation-demo-wall-intl
    title: Demo Wall Intl GitHub Repository
  - id: cn-bundle
    resource: ../trae-co-creation-demo-wall/index.md
    title: Demo Wall 中文版 Bundle
---

## 项目定位

**trae-co-creation-demo-wall-intl** 是 [trae-co-creation-demo-wall](../../trae-co-creation-demo-wall/index.md)（中文版）的**国际版变体**，核心架构与中文版相同（Next.js App Router + Prisma + NextAuth + next-intl + Tiptap + 腾讯云 COS），针对海外 Vercel 部署场景做了定向调整。共享架构部分请参阅中文版信源索引，本文档仅列出 intl 版的差异文件。

### 中文版共享源码引用

以下模块与中文版完全相同，直接引用中文版对应文档：

| 模块 | 中文版文档 | 说明 |
|------|-----------|------|
| 五表垂直分表模型 | 与中文版共享 | WorkBase/WorkDetail/WorkImage/WorkTeam/WorkStatistic |
| RBAC 权限模型 | 与中文版共享 | SysUser/SysRole/SysUserRole，三角色 root/admin/common |
| 字典驱动模型 | 与中文版共享 | SysDict/SysDictItem，支持 labelI18n |
| 审核日志模型 | 与中文版共享 | WorkAuditLog/SysAuthLog/SysOperationLog（外键策略有差异，见下） |
| NextAuth 认证 | 与中文版共享 | PrismaAdapter + JWT + Credentials（封禁检查有差异） |
| 核心 CRUD API | 与中文版共享 | /api/works、/api/submit、/api/file 等 |
| COS 文件存储 | 与中文版共享 | cos-nodejs-sdk-v5、上传/删除 API |
| 富文本编辑器 | 与中文版共享 | Tiptap 全家桶 + sanitize-html |
| 前端架构 | 与中文版共享 | App Router 双层 layout、Provider 嵌套、Tailwind + shadcn/ui |
| 状态管理 | 与中文版共享 | zustand + @tanstack/react-query + react-hook-form |

---

## Intl 版差异文件索引

### 项目配置差异

| 文件 | 路径（相对仓库根） | 差异说明 |
|------|-------------------|----------|
| 包定义 | `package.json` | 项目名 `dem`、新增 `@vercel/edge-config@^1.4.3` 依赖、移除 qrcode 相关依赖 |
| Next.js 配置 | `next.config.ts` | outputFileTracingExcludes 注释指向 Vercel Lambda 100MB 限制 |
| Dockerfile | `Dockerfile` | 构建阶段使用 `npm install`（中文版为 `npm ci`） |
| Docker Compose | `docker-compose.yml` | 移除 nginx 服务，直接暴露 3000 端口 |
| 启动脚本 | `entrypoint.sh` | `prisma db push` 不带 `--accept-data-loss` 参数 |

### 新增模块

| 文件 | 路径 | 职责 |
|------|------|------|
| Edge Config 工具 | `src/lib/edge-config.ts` | 导出 `getDictionaries()` 函数，从 Vercel Edge Config 读取字典缓存，失败返回 null 优雅降级 |
| Edge Config 同步 API | `src/app/api/sync-edge-config/route.ts` | POST 端点，管理员触发将 country/city/category/honor 字典序列化后 PATCH 到 Edge Config |
| CSV 导出 API | `src/app/api/console/works/export/route.ts` | GET 端点，管理员导出作品 CSV，支持 ids/筛选条件，5000 条上限，UTF-8 BOM，escapeCsv 防注入 |

### 移除模块

| 文件（中文版存在） | 说明 |
|-------------------|------|
| `src/lib/ban.ts` | 用户封禁模块，提供 clearBanCache/getBannedUserIds/isUserBanned/banUser/unbanUser/isEmailDomainBlocked 及 60 秒内存缓存 |
| `src/app/api/users/[id]/ban/` | 用户封禁 API 路由 |
| `src/assets/brand/` | 品牌 logo 目录（logo.png、logo.svg） |

### 修改模块

| 文件 | 路径 | 修改内容 |
|------|------|----------|
| 语言路由配置 | `src/lib/language/routing.ts` | locales 扩展为 `['en-US', 'zh-CN', 'ja-JP', 'id-ID', 'vi-VN']`，defaultLocale 改为 `'en-US'` |
| 中间件 | `src/middleware.ts` | isProtectedRoute 正则仍为 `/^\/(zh-CN\|en-US)\/(submit\|console\|profile)/`，**遗漏 id-ID 和 vi-VN**（已知 Bug） |
| 认证配置 | `src/lib/auth-nextauth.ts` | authorize 回调不检查 isUserBanned；jwt callback 不做封禁检查和 token.id 清空 |
| 注册 API | `src/app/api/auth/register/route.ts` | 不检查 isEmailDomainBlocked（因无 ban.ts 模块） |
| Prisma Schema | `prisma/schema.prisma` | SysAuthLog.user onDelete 改为 SetNull；SysOperationLog.operator onDelete 改为 SetNull；DateTime 精度去掉 (6) |

### 国际化文件

| 文件 | 路径 | 说明 |
|------|------|------|
| 英文翻译 | `src/messages/en-US.json` | 默认语言翻译 |
| 中文翻译 | `src/messages/zh-CN.json` | 中文翻译 |
| 日文翻译 | `src/messages/ja-JP.json` | 日文翻译 |
| 印尼语翻译 | `src/messages/id-ID.json` | **intl 新增**，印尼语翻译 |
| 越南语翻译 | `src/messages/vi-VN.json` | **intl 新增**，越南语翻译 |

### CI/CD 与测试

| 文件 | 路径 | 说明 |
|------|------|------|
| CI 工作流 | `.github/workflows/sync-cnb.yml` | intl 新增，CNB 同步工作流 |
| 单元测试 | `test/filter-options-sort.test.ts` | intl 新增，筛选选项排序测试 |

### 必需环境变量（intl 新增）

| 变量名 | 用途 | 中文版是否需要 |
|--------|------|:---:|
| `EDGE_CONFIG_ID` | Vercel Edge Config 实例 ID，字典缓存同步必需 | ❌ |
| `VERCEL_API_TOKEN` | Vercel Management API Token，调用 PATCH Edge Config 必需 | ❌ |

---

## 部署目标对比

| 维度 | 中文版 | 国际版（intl） |
|------|--------|---------------|
| 首要部署目标 | Docker 自托管 | Vercel 平台 |
| 反向代理 | nginx（docker-compose 内置） | Vercel Edge CDN |
| 数据库 | Docker PostgreSQL | 外部 PostgreSQL（Neon/Supabase 等） |
| 缓存层 | Redis（docker-compose 内置） | Vercel Edge Config（字典数据） |
| 构建命令 | `npm ci` | `npm install`（更容错） |
| 默认语言 | zh-CN | en-US |
| 支持语言数 | 3（zh-CN/en-US/ja-JP） | 5（+id-ID/vi-VN） |
| 用户治理 | 封禁系统（ban.ts + API） | 无封禁（删除用户+内容审核） |
| 数据导出 | 无 | CSV 导出（管理员） |
| 审计日志外键 | Cascade（删除用户级联删日志） | SetNull（删除用户保留日志链） |
| 品牌资源 | 有 brand/logo | 无 |
