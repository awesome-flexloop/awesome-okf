---
type: Concept
title: API 路由设计
description: Demo Wall 的 RESTful API 路由组织方式，服务端 Prisma CRUD 模式、Zod 校验、文件上传代理、审核操作端点。
tags: [demo-wall, api, routes, restful, prisma, zod]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: "/references/demo-wall-source.md"
    title: "Demo Wall 源码信源"
---

## API 路由总览

API 路由全部位于 `src/app/api/` 下，使用 Next.js App Router 的 Route Handler 模式（`route.ts` 文件导出 GET/POST/PUT/DELETE 函数）（F-020）。

### 路由分类

| 分类 | 前缀 | 认证要求 | 说明 |
|------|------|---------|------|
| 认证 | /api/auth/* | 公开 | NextAuth handlers + 注册 |
| 作品 | /api/works* | 混合 | 列表/详情公开，提交/更新/点赞需登录 |
| 提交 | /api/submit | 需登录 | 新作品提交 |
| 文件 | /api/file, /api/avatar | 需登录 | COS 图片上传/删除 |
| 用户 | /api/users* | 管理员 | 用户 CRUD + 封禁 |
| 角色 | /api/roles | 管理员 | 仅查询（角色固定） |
| 字典 | /api/dictionaries | 管理员 | 字典/字典项 CRUD |
| 标签 | /api/tags* | 混合 | 查询公开，修改需登录 |
| 个人资料 | /api/profile* | 混合 | 自己的资料需登录，公开主页无需 |
| 排行榜 | /api/rankings | 公开 | 城市/作品/创作者/趋势排行 |
| 日志 | /api/logs/* | 管理员 | 认证日志/操作日志查询 |
| 管理后台 | /api/console/* | 管理员 | 概览统计/作品管理/城市统计 |

## 标准 CRUD 模式

API 路由遵循一致的服务端处理模式：

1. **认证获取**：调用 `getAuthUser()` 获取当前用户，返回 null 表示未登录
2. **权限检查**：根据操作类型检查角色（isAdmin()/作者所有权验证）
3. **参数校验**：使用 zod schema 校验请求参数/body
4. **数据库操作**：使用 Prisma Client 执行查询/事务
5. **内容净化**：富文本内容调用 `sanitizeRichText()` 净化
6. **日志记录**：关键操作调用 `writeOperationLog()` 记录
7. **i18n 解析**：返回数据时根据 lang 参数解析 labelI18n 多语言标签

### 列表查询标准参数（F-070）

作品列表 API（GET /api/works）支持的参数体现了标准模式：

| 参数 | 说明 |
|------|------|
| page, pageSize | 分页 |
| search | 关键词搜索（标题/简介） |
| city, country, category | 字典编码筛选 |
| tags | 标签ID逗号分隔 |
| lang | 语言（默认zh-CN），用于i18n标签解析 |
| sort | newest/likes/views（默认newest） |
| date | YYYY-MM-DD 日期筛选 |
| honor | 荣誉类型筛选 |

公开列表只返回 `auditStatus=1 且 displayStatus=1` 的作品（F-070）。

## 事务写入模式

作品提交（POST /api/submit）和更新（PUT /api/works）使用 Prisma 事务保证五表写入的原子性（F-079, F-071）：

- 提交：在一个 `prisma.$transaction()` 中创建 WorkBase → WorkTagRelation → WorkDetail → WorkImage(screenshot) → WorkTeam → WorkStatistic
- 更新：事务内更新 WorkBase → 删除后重建 WorkTagRelation → upsert WorkDetail → 删除screenshot类型后重建 WorkImage → upsert WorkTeam
- 标签关联采用"删后重建"而非增量更新，逻辑简单且标签数量有限（1-5个）性能可接受

## 自动审核逻辑（F-079）

提交作品时检查标签的自动审核规则：
- 如果作品关联的标签中存在 `isAutoAudit=true` 的标签
- 且当前时间在该标签的 `auditStartTime` ~ `auditEndTime` 范围内
- 则自动设置 `auditStatus=1, displayStatus=1` 并写入 WorkAuditLog
- 否则 `auditStatus=0, displayStatus=0` 进入待审核队列

## 文件上传代理

文件上传不使用前端直传，而是通过服务端 API 代理到 COS（F-086~F-087）：

- POST /api/file：接受 FormData（field name="file"），限制 5MB，类型白名单 image/jpeg/png/webp/gif，路径 `uploads/{date}/{uuid}.{ext}`
- DELETE /api/file：接受 `{path, url}` 参数，调用 cos.deleteObject 删除
- POST /api/avatar：头像专用，限制 2MB，类型 jpg/png/webp/svg，路径 `avatars/{userId}-{timestamp}.{ext}`，上传后自动更新 avatarUrl

## 审核操作端点（F-095）

PUT /api/console/works 支持审核操作：

- 批量审核：ids[] 数组 + auditStatus + auditReason
- 单个审核：id + auditStatus + auditReason
- 仅管理员可执行批量审核
- 审核时写入 WorkAuditLog 记录 prevStatus→newStatus 变更
- 支持标签更新（tagIds）、荣誉授予（honorIds）、团队信息更新

## 相关概念

- [CRUD 数据层](/concepts/07-crud-layer.md)
- [认证系统](/concepts/04-auth-system.md)
- [作品提交流程](/concepts/13-form-submission.md)
- [COS 对象存储](/concepts/09-cos-storage.md)
- [审核与治理](/concepts/10-audit-governance.md)
- [自定义CRUD API示例](/examples/custom-crud-api.md)
