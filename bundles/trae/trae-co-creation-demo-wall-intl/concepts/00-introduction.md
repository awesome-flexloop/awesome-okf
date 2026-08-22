---
type: Concept
title: Demo Wall Intl 国际版简介
description: trae-co-creation-demo-wall-intl 是 Demo Wall 共创作品墙的国际版变体，面向海外市场，支持5种语言，Vercel优先部署，移除封禁系统，新增Edge Config缓存和CSV导出。
tags: [demo-wall, intl, introduction, vercel, i18n]
generated: { by: "reference_agent/trae-cn", at: 2026-04-22T00:00:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-04-22T00:00:00+08:00 }
status: stable
stale_after: 2026-10-22
sources:
  - id: src
    resource: /references/demo-wall-intl-source.md
    title: Demo Wall Intl 源码信源索引
  - id: cn-src
    resource: ../trae-co-creation-demo-wall/references/demo-wall-source.md
    title: Demo Wall 中文版源码信源
---

## 什么是 Demo Wall Intl

**trae-co-creation-demo-wall-intl**（项目名 `dem`）是 [trae-co-creation-demo-wall](../trae-co-creation-demo-wall/index.md)（中文版共创作品墙）的**国际版变体**。它在中文版核心架构基础上，针对海外市场和 Vercel 平台部署做了定向调整：将默认语言切换为英语、扩展到5种语言覆盖东南亚市场、引入 Vercel Edge Config 边缘缓存、新增管理员 CSV 导出、按 GDPR 要求调整审计日志外键策略、移除用户封禁系统以简化运营。

> **重要**：本 bundle 仅覆盖国际版与中文版的**差异部分**。核心架构（五表分表、RBAC、NextAuth 认证、COS 存储、Tiptap 富文本、App Router 双层 layout 等）与中文版完全一致，请先阅读中文版概念文档建立基础认知，再读本 bundle 的差异文档。

## 定位差异

| 维度 | 中文版（demo-wall） | 国际版（demo-wall-intl） |
|------|---------------------|-------------------------|
| 目标市场 | 中国国内 | 海外（英语+东南亚） |
| 首要部署平台 | Docker 自托管 | Vercel Serverless 平台 |
| 默认语言 | zh-CN（中文） | en-US（英语） |
| 支持语言 | 3种（zh-CN/en-US/ja-JP） | 5种（+id-ID印尼语/vi-VN越南语） |
| 用户治理 | 封禁系统（ban.ts + 封禁API + 域名屏蔽） | 无封禁（删除用户 + 内容审核） |
| 数据导出 | 无 | 管理员 CSV 导出（5000条上限） |
| 缓存方案 | Redis（docker-compose内置） | Vercel Edge Config（字典数据边缘缓存） |
| 审计日志策略 | 用户删除级联删除日志（Cascade） | 用户删除保留日志链（SetNull，GDPR合规） |
| 品牌资源 | 内置 brand/logo | 无品牌资源 |

## 与中文版的关系

国际版**不是 fork 后的独立项目**，而是基于同一套核心架构做的定向变体：

- **共享核心**：Next.js 15 App Router + React 18 + Prisma（PostgreSQL）+ NextAuth v5（JWT + Credentials）+ next-intl 4 + Tiptap 富文本 + 腾讯云 COS + Tailwind/shadcn/ui + zustand/react-query
- **移除功能**：用户封禁系统（`ban.ts`、`/api/users/[id]/ban`、authorize/jwt 封禁检查、注册域名屏蔽）、brand logo、二维码依赖、nginx 反向代理
- **新增功能**：Vercel Edge Config 字典缓存、管理员 CSV 导出、印尼语/越南语翻译、单元测试目录、CNB 同步 CI 工作流
- **策略调整**：外键 Cascade→SetNull、默认语言 zh-CN→en-US、npm ci→npm install、移除 `--accept-data-loss`、next.config.ts 注释指向 Vercel Lambda 限制

## 5 种语言支持

国际版面向海外市场，支持以下语言（默认英语）：

| 语言代码 | 语言 | 覆盖区域 |
|---------|------|---------|
| en-US | 英语（美国） | 全球通用（默认） |
| zh-CN | 简体中文 | 中国及华人用户 |
| ja-JP | 日语 | 日本 |
| id-ID | 印尼语 | 印度尼西亚（东南亚最大市场） |
| vi-VN | 越南语 | 越南（东南亚增长市场） |

> ⚠️ **已知 Bug**：middleware.ts 中 `isProtectedRoute` 正则硬编码为 `/^\/(zh-CN\|en-US)\/(submit\|console\|profile)/`，未包含 id-ID 和 vi-VN，导致印尼语/越南语用户访问受保护路由时可能绕过认证检查。详见 [5语言国际化](/concepts/02-multi-language.md)。

## 移除封禁系统的设计决策

国际版彻底移除了用户封禁功能，这不是安全疏忽，而是针对海外运营场景的有意决策：

1. **海外社区治理模式**：依赖用户举报+人工审核内容，而非预防性封禁账号
2. **降低运营复杂度**：缺少专职运营团队时，封禁申诉/解封流程成为负担
3. **技术债考量**：ban.ts 的 60 秒内存缓存在多实例/Edge Runtime 下存在一致性问题
4. **审计能力保留**：SysAuthLog/SysOperationLog 完整保留，管理员仍可通过删除用户处理严重违规
5. **最后一道防线**：内容审核双状态机（auditStatus/displayStatus）仍然完整

详见 [GDPR合规审计留存](/concepts/04-gdpr-audit-retention.md) 中外键策略变更。

## Vercel 优先部署范式

国际版的部署范式从"IaaS（Docker + Nginx + 自建PostgreSQL/Redis）"迁移到"PaaS/Serverless（Vercel + 外部PostgreSQL + Edge Config）"：

- Vercel 接管 CDN、SSL、边缘计算、自动伸缩
- 数据库使用外部 Neon/Supabase 等托管 PostgreSQL
- 字典数据通过 Edge Config 在全球边缘节点缓存（<50ms 读取延迟）
- Docker 配置保留作为备选方案（"Vercel优先，Docker兼容"）

详见 [Vercel部署](/concepts/05-vercel-deployment.md)。

## 学习路径

建议按以下顺序学习：

1. **先读中文版核心概念**：了解五表分表、RBAC、认证、审核、COS 存储等基础架构
2. **读本 bundle 差异概念**：
   - [Vercel Edge Config缓存](/concepts/01-edge-config-cache.md)
   - [5语言国际化](/concepts/02-multi-language.md)
   - [CSV导出功能](/concepts/03-csv-export.md)
   - [GDPR合规审计留存](/concepts/04-gdpr-audit-retention.md)
   - [Vercel部署](/concepts/05-vercel-deployment.md)
   - [与中文版完整差异对照](/concepts/06-differences-from-cn.md)
3. **动手实践**：参考 [examples/](/examples/) 目录下的示例文档

## 技术栈速览

| 类别 | 技术选型 | 与中文版差异 |
|------|---------|:---:|
| 框架 | Next.js 15.3.3 (App Router) | 同 |
| UI | React 18 + Tailwind + shadcn/ui + Radix UI | 同 |
| 数据库 | PostgreSQL + Prisma 5.10.2 | 外键策略差异 |
| 认证 | NextAuth v5 (JWT + Credentials) | 移除封禁检查 |
| 国际化 | next-intl 4.8.3 | 5种语言，默认en-US |
| 富文本 | Tiptap + sanitize-html | 同 |
| 存储 | 腾讯云 COS (cos-nodejs-sdk-v5) | 同 |
| 状态管理 | zustand + @tanstack/react-query | 同 |
| 缓存 | Vercel Edge Config（新增） | 替代 Redis 字典缓存 |
| 校验 | Zod 4.3.6 | 同 |
| 部署 | Vercel（优先）+ Docker（兼容） | 从Docker转向Vercel |

## 相关概念

- [Vercel Edge Config缓存](/concepts/01-edge-config-cache.md)
- [5语言国际化](/concepts/02-multi-language.md)
- [CSV导出功能](/concepts/03-csv-export.md)
- [GDPR合规审计留存](/concepts/04-gdpr-audit-retention.md)
- [Vercel部署](/concepts/05-vercel-deployment.md)
- [与中文版完整差异对照](/concepts/06-differences-from-cn.md)
