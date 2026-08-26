---
type: Index
title: Demo Wall Intl 国际版
description: trae-co-creation-demo-wall-intl是Demo Wall共创作品墙的国际版变体，面向海外Vercel部署，支持5种语言（en-US/zh-CN/ja-JP/id-ID/vi-VN），新增Edge Config缓存、CSV导出、GDPR合规审计，移除封禁系统。本bundle仅覆盖与中文版的差异点。
tags: [demo-wall, intl, vercel, i18n, nextjs, prisma, gdpr, edge-config]
generated: { by: "reference_agent/trae-cn", at: 2026-04-22T00:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-04-22T00:00:00+08:00 }
status: stable
stale_after: 2026-10-22
sources:
  - id: src
    resource: /references/demo-wall-intl-source.md
    title: Demo Wall Intl 源码信源索引
  - id: cn-bundle
    resource: ../trae-co-creation-demo-wall/index.md
    title: Demo Wall 中文版 Bundle
---

## Demo Wall Intl Bundle

本bundle提供 trae-co-creation-demo-wall-intl（国际版共创作品墙）的源码级差异文档。国际版是中文版的**Vercel优先部署变体**，共享核心架构（Next.js + Prisma + NextAuth + next-intl + Tiptap + COS），针对海外市场做了6项核心调整。

> ⚠️ **重要提示**：本bundle**仅覆盖国际版与中文版的差异部分**。核心架构（五表分表、RBAC、认证、审核、COS存储等）与中文版完全一致，请先阅读中文版bundle建立基础认知，再读本bundle的差异文档。

## 快速导航

### 差异概念（intl 独有）

| 文档 | 内容 |
|------|------|
| [国际版简介](/concepts/00-introduction.md) | 定位差异、与中文版的关系、5种语言支持、移除封禁系统概述 |
| [Vercel Edge Config缓存](/concepts/01-edge-config-cache.md) | Edge Config字典缓存层、getDictionaries()优雅降级、sync-edge-config同步端点、手动vs自动同步权衡 |
| [5语言国际化](/concepts/02-multi-language.md) | en-US/zh-CN/ja-JP/id-ID/vi-VN、默认en-US、isProtectedRoute正则遗漏Bug及修复、东南亚市场覆盖 |
| [CSV导出功能](/concepts/03-csv-export.md) | /api/console/works/export端点、5000条硬上限、UTF-8 BOM、escapeCsv防公式注入 |
| [GDPR合规审计留存](/concepts/04-gdpr-audit-retention.md) | 外键Cascade→SetNull、删除用户保留审计日志链、userId置null策略 |
| [Vercel部署](/concepts/05-vercel-deployment.md) | Vercel优先Docker兼容、npm ci调整、移除nginx、standalone输出、Edge Runtime权衡 |
| [与中文版完整差异对照](/concepts/06-differences-from-cn.md) | 系统功能/API/依赖/部署/默认配置差异速查表 |

### 实践示例

| 文档 | 内容 |
|------|------|
| [Vercel部署配置示例](/examples/setup-vercel-deployment.md) | 从GitHub导入→环境变量→外部PostgreSQL→Edge Config→部署验证 |
| [Edge Config缓存同步示例](/examples/edge-config-sync.md) | 修改字典→触发同步→验证缓存→模拟降级回退 |
| [CSV数据导出示例](/examples/csv-export-usage.md) | 选中导出/筛选导出、Excel打开验证、escapeCsv安全机制 |
| [5语言配置与翻译扩展示例](/examples/multi-language-setup.md) | next-intl配置、翻译文件结构、语言切换组件、字典labelI18n |
| [符合GDPR的用户删除操作示例](/examples/user-deletion-gdpr.md) | SetNull外键策略下删除用户、审计链验证、"已删除用户"日志查询 |
| [从中文版迁移到国际版指南](/examples/migrate-from-cn.md) | 代码切换、数据库迁移、环境变量变更、部署切换、回滚方案 |
| [添加新语言完整步骤](/examples/add-new-language.md) | 以th-TH泰语为例，routing.ts→翻译文件→字典翻译→中间件验证→测试 |

### 参考信源

| 文档 | 内容 |
|------|------|
| [源码信源索引](/references/demo-wall-intl-source.md) | intl版差异文件索引、中文版共享架构引用、部署目标对比表 |

### 中文版共享概念（前置阅读）

国际版与中文版共享的核心架构，请参阅中文版bundle：

| 主题 | 参考 |
|------|------|
| 五表垂直分表模型 | 中文版 WorkBase/WorkDetail/WorkImage/WorkTeam/WorkStatistic |
| RBAC 权限模型 | 中文版 SysUser/SysRole/SysUserRole |
| NextAuth 认证配置 | 中文版 PrismaAdapter + JWT + Credentials |
| 审核双状态机 | 中文版 auditStatus/displayStatus |
| COS 文件存储 | 中文版 cos-nodejs-sdk-v5 配置 |
| Tiptap 富文本 | 中文版编辑器 + sanitize-html |
| App Router 架构 | 中文版双层 layout + Provider 嵌套 |
| Docker 基础配置 | 中文版三阶段构建（国际版有调整） |

## 学习路径

### 推荐路径：先读中文版 → 再读差异

```
中文版核心概念（前置必读）
  ↓
00-introduction（国际版简介）
  ↓
  ┌─────────────────────────────────┐
  │                                 │
  ├→ 01-edge-config-cache ──→ 05-vercel-deployment
  │        ↓                        │
  ├→ 02-multi-language ────→ examples/add-new-language
  │        ↓                        │
  ├→ 03-csv-export                  │
  │        ↓                        │
  └→ 04-gdpr-audit-retention        │
           ↓                        │
     06-differences-from-cn ────────┘
           ↓
     examples/（动手实践）
```

### 路径1：快速了解差异

```
00-introduction → 06-differences-from-cn（差异速查表）
```

### 路径2：Vercel 部署实践

```
00-introduction → 01-edge-config-cache → 05-vercel-deployment
    → examples/setup-vercel-deployment → examples/edge-config-sync
```

### 路径3：多语言开发

```
02-multi-language → examples/multi-language-setup → examples/add-new-language
```

### 路径4：从中文版迁移

```
06-differences-from-cn → 04-gdpr-audit-retention → examples/migrate-from-cn
```

## 6个核心差异洞察摘要

### 洞察一：Vercel Edge Config 缓存层——海外冷启动性能优化
国际版引入 Vercel Edge Config 作为字典数据（country/city/category/honor）的边缘缓存层，替代中文版的 Redis。管理员手动触发同步，将字典推送到全球边缘节点（<50ms 读取延迟），getDictionaries() 失败时优雅降级到数据库查询。**为什么不缓存作品数据？** 字典是高频读取低频变更的典型缓存候选，作品数据高频变更不适合最终一致缓存。详见 [Vercel Edge Config缓存](/concepts/01-edge-config-cache.md)。

### 洞察二：用户治理简化——移除封禁功能的安全取舍
国际版彻底移除用户封禁功能（ban.ts + 封禁API + 域名屏蔽 + 双重封禁检查），改用"删除用户+内容审核"模式。海外社区依赖用户举报+人工审核而非预防性封禁；同时 ban.ts 的 60 秒内存缓存在多实例/Edge Runtime 下有一致性问题。审计日志仍然完整保留。详见 [GDPR合规审计留存](/concepts/04-gdpr-audit-retention.md)。

### 洞察三：语言扩展到5种与中间件正则遗漏缺陷
支持语言从3种扩展到5种（新增 id-ID 印尼语/vi-VN 越南语，覆盖东南亚市场），默认语言切换为 en-US。但 middleware.ts 中 isProtectedRoute 正则硬编码未包含新增语言，导致印尼语/越南语用户访问受保护路由时可能绕过认证——这是典型的DRY违反，应从 routing.locales 动态生成正则。详见 [5语言国际化](/concepts/02-multi-language.md)。

### 洞察四：CSV 导出——面向国际运营数据需求
新增管理员 CSV 导出功能，支持选中导出和筛选导出，硬上限5000条（防止OOM和Vercel超时），输出UTF-8 BOM兼容Excel，escapeCsv防公式注入（`=`/`+`/`-`/`@`开头前置单引号）。国际版运营人员可能无数据库权限，需要界面导出。详见 [CSV导出功能](/concepts/03-csv-export.md)。

### 洞察五：外键策略从Cascade改为SetNull——日志数据留存哲学
SysAuthLog.user 和 SysOperationLog.operator 的 onDelete 从 Cascade 改为 SetNull。Cascade 删除用户会销毁所有审计日志，在GDPR合规场景下不可接受；SetNull 保留审计链（"谁在什么时间做了什么"），仅将操作者标识置为null。中文版注重大陆习惯的"数据干净"，国际版选择审计优先。详见 [GDPR合规审计留存](/concepts/04-gdpr-audit-retention.md)。

### 洞察六：部署目标从Docker转向Vercel——平台化部署范式迁移
next.config.ts 注释从"减小Docker镜像"变为"避免Vercel Lambda限制"、docker-compose移除nginx、Dockerfile npm install替代npm ci、移除--accept-data-loss、新增Edge Config集成。整体定位"Vercel优先，Docker兼容"——Vercel接管CDN/SSL/伸缩，Docker保留给自托管场景。详见 [Vercel部署](/concepts/05-vercel-deployment.md)。

## 技术栈速览

| 类别 | 技术选型 | 差异说明 |
|------|---------|---------|
| 框架 | Next.js 15.3.3 (App Router) | 同中文版 |
| UI | React 18 + Tailwind + shadcn/ui | 同中文版 |
| 数据库 | PostgreSQL + Prisma 5.10.2 | 外键 Cascade→SetNull |
| 认证 | NextAuth v5 (JWT) | 移除封禁检查 |
| 国际化 | next-intl 4.8.3 | 5种语言，默认en-US |
| 缓存 | Vercel Edge Config | 替代 Redis（字典数据） |
| 存储 | 腾讯云 COS | 同中文版 |
| 部署 | Vercel（优先）+ Docker（兼容） | 从Docker转向Vercel |
| 新增功能 | CSV导出、Edge Config、印尼/越南语 | 国际版独有 |
| 移除功能 | 用户封禁、nginx、二维码、brand logo | 面向海外简化 |

## 版本信息

- **项目名称**：dem（trae-co-creation-demo-wall-intl）
- **基于**：trae-co-creation-demo-wall（中文版）核心架构
- **文档生成日期**：2026-04-22
- **支持语言**：en-US（默认）、zh-CN、ja-JP、id-ID、vi-VN
- **部署平台**：Vercel（推荐）/ Docker（兼容）

```{toctree}
:hidden:
:maxdepth: 7

concepts/00-introduction
concepts/01-edge-config-cache
concepts/02-multi-language
concepts/03-csv-export
concepts/04-gdpr-audit-retention
concepts/05-vercel-deployment
concepts/06-differences-from-cn
examples/add-new-language
examples/csv-export-usage
examples/edge-config-sync
examples/migrate-from-cn
examples/multi-language-setup
examples/setup-vercel-deployment
examples/user-deletion-gdpr
references/demo-wall-intl-source
spec/facts
spec/insights
```
