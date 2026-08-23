---
type: Concept
title: 点赞与统计
description: Demo Wall 的 WorkLike 唯一约束点赞机制、viewCount/likeCount 计数器、toggle-like API、排行榜 rankings、乐观更新。
tags: [demo-wall, like, ranking, statistics, counter]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: "/references/demo-wall-source.md"
    title: "Demo Wall 源码信源"
---

## 点赞模型（F-042）

WorkLike 表记录用户点赞：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BigInt PK | 自增主键 |
| userId | BigInt FK→SysUser(Cascade) | 点赞用户 |
| workId | BigInt FK→WorkBase(Cascade) | 被点赞作品 |
| createdAt | DateTime? | 点赞时间 |

唯一约束：`@@unique([userId, workId])`，保证用户不能重复点赞同一作品。
索引：`[workId]`, `[userId]`。

## 切换点赞 API（F-073）

POST /api/works/[id]/like 切换点赞状态（需登录）：

1. 获取当前用户
2. 查询是否已存在 WorkLike 记录
3. **已赞**：事务内删除 WorkLike + decrement WorkStatistic.likeCount
4. **未赞**：事务内创建 WorkLike + upsert WorkStatistic increment likeCount
5. writeOperationLog() 记录操作
6. 返回 `{ liked: boolean }`

## 浏览量计数（F-074）

POST /api/works/[id]/view 记录浏览量（无需登录）：

- upsert WorkStatistic 使 viewCount+1
- writeOperationLog() 记录（未登录用户 operatorId 为空）

## 作品统计 API（F-075）

GET /api/works/[id]/stats 返回：
- viewCount、likeCount
- 当前用户是否已点赞（需登录）

## 我的点赞列表（F-076）

GET /api/works/likes 返回当前用户点赞的作品列表（分页，需登录）。

管理后台提供 GET /api/console/works/[id]/likes 查询某作品的点赞用户列表（分页），用于排查刷量（F-096）。

## 排行榜（F-091）

GET /api/rankings 返回公开排行榜数据：

| 排行类型 | 说明 |
|---------|------|
| cityRanking | Top20 城市，按作品数/浏览量/点赞数排序 |
| worksRanking | byViews、byLikes 各 Top20 作品 |
| creatorsRanking | byWorks、byViews、byLikes 各 Top20 创作者 |
| trendingWorks | 7天内按浏览量 Top20 趋势作品 |

## 计数器设计

viewCount 和 likeCount 存储在 WorkStatistic 表中（与 WorkBase 分离），原因：

1. **写入频率高**：每次浏览/点赞都更新，与低频写的作品内容分离
2. **避免锁竞争**：高频更新不会锁定包含大文本字段的行
3. **计数冗余换查询效率**：避免每次查询都 COUNT WorkLike 表

## 相关概念

- [数据模型设计](/concepts/03-data-model.md)
- [API 路由设计](/concepts/06-api-routes.md)
- [CRUD 数据层](/concepts/07-crud-layer.md)
- [审核与治理](/concepts/10-audit-governance.md)
