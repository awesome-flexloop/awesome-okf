---
type: Concept
title: 审核与治理
description: Demo Wall 的双状态审核机制、WorkAuditLog 审核链、SysAuthLog/SysOperationLog 审计日志、管理员后台 console、用户封禁治理闭环。
tags: [demo-wall, audit, governance, logging, ban]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: "/references/demo-wall-source.md"
    title: "Demo Wall 源码信源"
---

## 双状态审核机机（F-037）

WorkStatistic 表使用两个正交独立的状态字段：

| 字段 | 值 | 含义 |
|------|-----|------|
| auditStatus | 0 | 待审核 |
| auditStatus | 1 | 审核通过 |
| auditStatus | 2 | 审核拒绝 |
| displayStatus | 0 | 下架（不可见） |
| displayStatus | 1 | 上架（可见） |

**为什么需要两个状态？** 运营中存在"审核通过但需临时下架"（投诉/修改）和"审核拒绝但允许作者查看编辑重新提交"的场景，单状态无法表达这些组合。

公开列表只展示 `auditStatus=1 AND displayStatus=1` 的作品（F-070）。作品详情权限检查：非作者/非管理员只能查看审核通过且上架的作品（F-072）。

## WorkAuditLog 审核链（F-039）

每次审核状态变更都记录到 WorkAuditLog：

| 字段 | 说明 |
|------|------|
| workId | 作品ID |
| auditorId | 审核人ID（关联SysUser） |
| prevStatus | 变更前 auditStatus |
| newStatus | 变更后 auditStatus |
| reason | 审核原因/备注 |
| createdAt | 审核时间 |

形成完整的审核状态变更链，支持审核追溯。

## SysAuthLog 认证日志（F-043）

记录认证相关事件：

| 字段 | 说明 |
|------|------|
| userId/clerkId | 用户标识 |
| authType | 认证类型（sign_in/register等） |
| authChannel | 认证渠道（credentials等） |
| authStatus | 成功/失败 |
| ipAddress | 客户端IP |
| userAgent | 浏览器UA |
| metadata | 附加元数据（JSON） |

索引：`[userId]`, `[clerkId]`, `[authType]`, `[createdAt]`

查询 API：GET /api/logs/auth 支持分页/搜索/筛选/日期范围（F-092）。

## SysOperationLog 操作日志（F-044）

记录关键业务操作：

| 字段 | 说明 |
|------|------|
| operatorId | 操作者ID |
| module | 模块名（如 works, users, file） |
| action | 动作名（如 create, update, delete, like, view） |
| targetType/targetId | 操作目标 |
| success | 是否成功 |
| errorMessage | 错误信息（失败时） |
| requestMethod/path | 请求方法/路径 |
| ipAddress/userAgent | 客户端信息 |
| payload | 请求参数（JSON） |

索引：`[operatorId]`, `[module, action]`, `[createdAt]`

查询 API：GET /api/logs/operations 支持分页/搜索/筛选/模块/日期范围，返回 modules 列表（F-093）。

## 审计日志工具（F-102）

`src/lib/audit-log.ts` 封装日志写入：

- `writeAuthLog(params)`：写入 sys_auth_log
- `writeOperationLog(params)`：写入 sys_operation_log

内部辅助函数：
- `normalizeId()`：BigInt/number/string/null 统一转 BigInt 或 null
- `getHeaderValue()`：安全获取 header 值
- `getClientIp()`：从 x-forwarded-for/x-real-ip/cf-connecting-ip/x-client-ip 获取真实 IP
- `toSafeJson()`：BigInt 安全序列化
- `getRequestMeta()`：从 Request 对象提取 IP/UA/Method/Path

**关键设计**：所有日志写入用 try-catch 包裹，不抛异常——日志失败不能阻断主业务流程。

## 用户封禁机制（F-103）

`src/lib/ban.ts` 导出封禁相关函数：

- `BANNED_USERS_DICT = 'banned_users'`：封禁用户存储在字典表
- `BLOCKED_DOMAINS_DICT = 'blocked_email_domains'`：屏蔽域名也在字典表
- `CACHE_TTL_MS = 60000`：60秒内存缓存，避免每次请求查库

**核心函数**：
- `isUserBanned(userId)`：检查用户是否被封禁（带缓存）
- `banUser(userId)`：封禁用户（自动 ensureDict，upsert 字典项）
- `unbanUser(userId)`：解封用户（删除字典项）
- `getBannedUserIds()`：获取所有封禁用户ID列表（带缓存）
- `clearBanCache()`：清除缓存
- `isEmailDomainBlocked(email)`：检查邮箱域名是否被屏蔽（合并默认域名和数据库配置）

### 封禁双重检查

1. **authorize 回调**（F-060）：阻止被封禁用户新登录
2. **jwt callback**（F-062）：清空已登录封禁用户的 token.id，使存量会话失效

Edge Runtime 下跳过封禁检查（Prisma 无法在 Edge 运行，已知权衡）。

禁止封禁 admin/root 角色用户（F-083）。

## 管理后台 Console（F-018, F-094~F-097）

管理后台页面位于 `src/app/[language]/console/`：

| 页面 | 功能 |
|------|------|
| /console（概览） | 统计数据、趋势图、分布、最近活动（7/30天窗口） |
| /console/works | 作品管理/审核 |
| /console/users | 用户管理/封禁 |
| /console/roles | 角色查看（不可编辑） |
| /console/dictionaries | 字典管理 |
| /console/tags | 标签管理 |
| /console/cities | 城市统计 |
| /console/auth-logs | 认证日志 |
| /console/operation-logs | 操作日志 |

概览 API（GET /api/console/overview）使用原生 SQL 查询日聚合和去重活跃用户（F-094）。

## 相关概念

- [认证系统](/concepts/04-auth-system.md)
- [数据模型设计](/concepts/03-data-model.md)
- [字典系统](/concepts/11-dictionary-system.md)
- [API 路由设计](/concepts/06-api-routes.md)
- [点赞与统计](/concepts/14-like-system.md)
