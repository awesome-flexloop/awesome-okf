---
type: Example
title: 管理员审核示例
description: 管理后台登录、作品审核通过/拒绝、荣誉授予、用户管理、日志查看的操作示例。
tags: [demo-wall, example, admin, review, audit, console]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: "/references/demo-wall-source.md"
    title: "Demo Wall 源码信源"
---

## 管理员登录

使用 seed 创建的默认管理员账号登录（F-056）：
- 邮箱：trae@example.com
- 密码：trae1234
- 角色：root

登录后访问 `/zh-CN/console` 进入管理后台概览页。

## 查看待审核作品

访问 `/zh-CN/console/works` 或调用 API（F-095）：

```bash
curl "http://localhost:3000/api/console/works?page=1&pageSize=20&auditStatus=0" \
  -H "Cookie: next-auth.session-token=<admin-session>"
```

管理员可看全部作品，普通用户只能看自己的作品。

## 审核通过作品

```bash
curl -X PUT http://localhost:3000/api/console/works \
  -H "Content-Type: application/json" \
  -H "Cookie: next-auth.session-token=<admin-session>" \
  -d '{
    "id": "123",
    "auditStatus": 1,
    "auditReason": "内容质量优秀，审核通过"
  }'
```

服务端处理：
1. 验证操作者为管理员
2. 查询作品当前状态
3. 事务更新 WorkStatistic（auditStatus=1, displayStatus=1, lastAuditAt=now）
4. 创建 WorkAuditLog 记录（prevStatus=0, newStatus=1, auditorId, reason）（F-039）
5. writeOperationLog() 记录

## 批量审核

```bash
curl -X PUT http://localhost:3000/api/console/works \
  -H "Content-Type: application/json" \
  -H "Cookie: next-auth.session-token=<admin-session>" \
  -d '{
    "ids": ["123", "124", "125"],
    "auditStatus": 1,
    "auditReason": "批量审核通过"
  }'
```

批量审核仅管理员可用（F-095）。

## 审核拒绝作品

```bash
curl -X PUT http://localhost:3000/api/console/works \
  -H "Content-Type: application/json" \
  -H "Cookie: next-auth.session-token=<admin-session>" \
  -d '{
    "id": "126",
    "auditStatus": 2,
    "auditReason": "内容不符合规范，请补充截图和详细描述后重新提交"
  }'
```

拒绝后作品 auditStatus=2，作者可查看拒绝原因并编辑重新提交。

## 授予荣誉

```bash
curl -X PUT http://localhost:3000/api/console/works \
  -H "Content-Type: application/json" \
  -H "Cookie: next-auth.session-token=<admin-session>" \
  -d '{
    "id": "123",
    "honorIds": [1, 2]
  }'
```

honorIds 对应 honor_type 字典项（community_choice/city_star/best_of_year）（F-053），创建 WorkHonor 记录关联授予者（grantedBy=当前管理员ID）（F-038）。

## 下架作品

已上架作品可以下架（displayStatus=0），不改变 auditStatus：

```bash
# 通过更新 API 设置 displayStatus=0
curl -X PUT http://localhost:3000/api/console/works \
  -H "Content-Type: application/json" \
  -H "Cookie: next-auth.session-token=<admin-session>" \
  -d '{
    "id": "123",
    "displayStatus": 0
  }'
```

## 用户管理

### 查看用户列表

```bash
curl "http://localhost:3000/api/users?page=1&pageSize=20" \
  -H "Cookie: next-auth.session-token=<admin-session>"
```

返回用户列表，包含 banned 封禁状态字段（F-082）。

### 封禁用户

```bash
curl -X POST http://localhost:3000/api/users/456/ban \
  -H "Content-Type: application/json" \
  -H "Cookie: next-auth.session-token=<admin-session>" \
  -d '{"banned": true}'
```

- 禁止封禁 admin/root 角色用户（F-083）
- 封禁后：authorize 回调阻止新登录，jwt callback 清空存量 session（F-060, F-062）
- 封禁信息存储在 banned_users 字典中（F-103）

### 解封用户

```bash
curl -X POST http://localhost:3000/api/users/456/ban \
  -H "Content-Type: application/json" \
  -H "Cookie: next-auth.session-token=<admin-session>" \
  -d '{"banned": false}'
```

## 查看日志

### 认证日志

```bash
curl "http://localhost:3000/api/logs/auth?page=1&pageSize=20&filter=sign_in&startDate=2026-04-01&endDate=2026-04-22" \
  -H "Cookie: next-auth.session-token=<admin-session>"
```

### 操作日志

```bash
curl "http://localhost:3000/api/logs/operations?page=1&pageSize=20&filter=failed&module=works" \
  -H "Cookie: next-auth.session-token=<admin-session>"
```

## 管理后台概览

```bash
curl "http://localhost:3000/api/console/overview?window=7" \
  -H "Cookie: next-auth.session-token=<admin-session>"
```

返回 stats（总量/环比）、trend（每日时序）、distribution（操作分布）、latestActivities（最近活动）（F-094）。

## 相关内容

- [审核与治理](/concepts/10-audit-governance.md)
- [认证系统](/concepts/04-auth-system.md)
- [字典系统](/concepts/11-dictionary-system.md)
- [作品提交示例](/examples/submit-work.md)
