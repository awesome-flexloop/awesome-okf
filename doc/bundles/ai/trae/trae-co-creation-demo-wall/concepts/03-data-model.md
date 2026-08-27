---
type: Concept
title: 数据模型设计
description: Demo Wall 的 Prisma Schema 详解，包括 Work 五表垂直分表设计、SysDict 字典系统、RBAC 角色权限模型以及各实体间的关系。
tags: [demo-wall, data-model, prisma, schema, vertical-partitioning]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: "/references/demo-wall-source.md"
    title: "Demo Wall 源码信源"
---

## Prisma Schema 总览

Prisma schema 定义在 `prisma/schema.prisma`，数据源 provider 为 `postgresql`，共定义 20 个 model（F-005, F-027），按功能分为五大类：

| 分类 | Model | 数量 |
|------|-------|------|
| 字典系统 | SysDict, SysDictItem | 2 |
| 用户与权限 | SysUser, SysRole, SysUserRole | 3 |
| 作品核心 | WorkBase, WorkDetail, WorkImage, WorkTeam, WorkStatistic | 5 |
| 作品扩展 | WorkHonor, WorkAuditLog, WorkTag, WorkTagRelation, WorkLike | 5 |
| 系统日志 | SysAuthLog, SysOperationLog | 2 |
| NextAuth | Account, Session, VerificationToken | 3 |

所有表名通过 `@@map()` 映射为下划线命名（如 `work_base`），主键使用 BigInt 自增，时间字段使用 `@db.Timestamptz(6)`。

## Work 五表垂直分表

作品数据采用垂直分表设计，将一个逻辑实体拆分为五个物理表（F-033~F-037），所有子表对 WorkBase 设置 `onDelete: Cascade` 级联删除。

### WorkBase — 核心标识表

`@@map("work_base")`（F-033），列表查询的主要表：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BigInt PK | 自增主键 |
| userId | BigInt FK→SysUser | 作者ID |
| title | String(255) | 作品标题 |
| summary | String?(255) | 作品简介 |
| coverUrl | String?(255) | 封面图片URL |
| countryCode/cityCode | String?(100) | 国家/城市编码（字典） |
| categoryCode | String?(100) | 分类编码（字典） |
| devStatusCode | String?(100) | 开发状态编码（字典） |
| createdAt/updatedAt | DateTime? | 时间戳 |

索引：`[userId]`、`[countryCode]`、`[cityCode]`、`[categoryCode]`。

### WorkDetail — 富文本内容表

`@@map("work_detail")`，以 workId 为主键，一对一关联 WorkBase（F-034）。存储低频访问的大文本：story（富文本）、highlights（JSON亮点）、scenarios（JSON场景）、demoUrl、repoUrl。

### WorkImage — 截图集合表

`@@map("work_image")`，一对多关联 WorkBase（F-035）。字段：id、workId(FK)、imageUrl、imageType（如screenshot）、sortOrder、createdAt。索引 `[workId]`。

### WorkTeam — 团队信息表

`@@map("work_team")`，workId 设为 unique，一对一关联 WorkBase（F-036）。字段：id、workId(FK unique)、teamIntro、members(JSON)、contactPhone、contactEmail。

### WorkStatistic — 状态与计数表

`@@map("work_statistic")`，以 workId 为主键，一对一关联 WorkBase（F-037）。存储高频更新的状态和计数：

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| auditStatus | Int? | 0 | 0=待审, 1=通过, 2=拒绝 |
| displayStatus | Int? | 0 | 0=下架, 1=上架 |
| viewCount | BigInt? | 0 | 浏览量 |
| likeCount | BigInt? | 0 | 点赞数 |
| lastAuditAt | DateTime? | — | 最后审核时间 |

### 垂直分表的设计理由

1. **访问频率差异**：列表页只需要 WorkBase 字段，不加载 WorkDetail 的大文本或 WorkImage 的多条记录；
2. **写入模式分离**：WorkStatistic 的 viewCount/likeCount 是高频写，与低频写的内容字段分离避免锁竞争；
3. **关系天然独立**：截图是一对多集合，无法用单表字段承载；团队成员用 JSON 存储避免复杂子表。

## 字典系统：SysDict / SysDictItem

### SysDict（`@@map("sys_dict")`）（F-028）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BigInt PK | 自增主键 |
| dictCode | String(50) unique | 字典编码 |
| dictName | String(50) | 字典名称 |
| description | String?(255) | 描述 |
| isSystem | Boolean? default(false) | 是否系统内置 |

### SysDictItem（`@@map("sys_dict_item")`）（F-029）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BigInt PK | 自增主键 |
| dictCode | String(50) | 所属字典编码 |
| itemLabel | String(100) | 默认标签 |
| labelI18n | Json? | 多语言标签 `{"zh-CN": "中国", "en-US": "China"}` |
| itemValue | String(100) | 字典项值 |
| parentValue | String?(100) | 父级值（层级关系） |
| sortOrder | Int? default(0) | 排序序号 |
| status | Boolean? default(true) | 是否启用 |

唯一约束：`@@unique([dictCode, itemValue])`。

### 预置系统字典

seed.ts 初始化（F-049~F-055）：

| dictCode | 用途 | 预置项 |
|----------|------|--------|
| audit_status | 审核状态 | 0=待审核、1=已通过、2=已拒绝 |
| dev_status | 开发状态 | ideation、prototype、completed、released |
| category_code | 作品分类 | utility、scenario、assistant、content、creative、other |
| honor_type | 荣誉类型 | community_choice、city_star、best_of_year |
| banned_users | 封禁用户黑名单 | 动态添加 |
| blocked_email_domains | 屏蔽邮箱域名 | example.com、example.org、example.net |
| country/city | 国家城市 | 从 seed-data-countries.ts 导入 |

字典系统复用于封禁用户和屏蔽域名，无需额外黑名单表（F-103）。

## RBAC 权限模型

### SysRole（`@@map("sys_role")`）（F-031）

固定三个角色（F-048），不允许通过 API 增删改（POST/PUT/DELETE 返回 403）（F-084）：

| roleCode | 权限范围 |
|----------|---------|
| root | 最高权限，不可被封禁 |
| admin | 管理后台、审核、用户管理 |
| common | 提交作品、编辑自己的作品、点赞 |

### SysUserRole（`@@map("sys_user_role")`）（F-032）

用户-角色多对多关联表，字段：id、userId(FK Cascade)、roleId(FK Cascade)，唯一约束 `[userId, roleId]`。

角色硬编码而非字典化，因为角色与代码权限检查强耦合（`isAdmin()` 直接判断字符串），动态化会导致安全漏洞。

### SysUser（`@@map("sys_user")`）（F-030）

主要字段：id、username、email(unique)、phone、clerk_id(unique)、passwordHash、avatarUrl、bio、lastSignInAt、identities(JSON)、createdAt、updatedAt。

关系：accounts/sessions（NextAuth）、authLogs/operationLogs（日志）、roles、auditedLogs（审核记录）、works、grantedHonors、likes。

## 作品扩展 Model

- **WorkHonor**（F-038）：作品荣誉，关联 SysDictItem（honor_type）和授予者 SysUser（GrantedBy）
- **WorkAuditLog**（F-039）：审核状态变更链，记录 prevStatus→newStatus、reason、auditorId
- **WorkTag**（F-040）：标签定义，含 isAutoAudit 自动审核标记和 auditStartTime/auditEndTime 时间窗口
- **WorkTagRelation**（F-041）：作品-标签多对多，复合主键 `[workId, tagId]`
- **WorkLike**（F-042）：点赞记录，唯一约束 `[userId, workId]`，索引 `[workId]`、`[userId]`

## 系统日志 Model

- **SysAuthLog**（F-043）：认证日志，字段含 authType、authChannel、authStatus、ipAddress、userAgent、metadata、clerkId，索引 `[userId]`、`[clerkId]`、`[authType]`、`[createdAt]`
- **SysOperationLog**（F-044）：操作日志，字段含 module、action、targetType、targetId、success、errorMessage、requestMethod、requestPath、ipAddress、userAgent、payload，索引 `[operatorId]`、`[module, action]`、`[createdAt]`

## NextAuth 标准表

- **Account**（F-045）：OAuth 账号关联，字段含 userId、type、provider、providerAccountId、token 相关字段
- **Session**（F-046）：用户会话，字段含 sessionToken(unique)、userId、expires
- **VerificationToken**（F-047）：验证令牌，字段含 identifier、token(unique)、expires

## 相关概念

- [架构总览](02-architecture-overview.md)
- [认证系统](04-auth-system.md)
- [字典系统](11-dictionary-system.md)
- [审核与治理](10-audit-governance.md)
- [API 路由设计](06-api-routes.md)
- [CRUD 数据层](07-crud-layer.md)
