---
type: Concept
title: GDPR 合规审计留存
description: intl版将SysAuthLog和SysOperationLog的外键onDelete策略从Cascade改为SetNull，删除用户时保留审计日志链（userId置null），确保GDPR合规下的审计完整性。DateTime字段精度从微秒简化为默认精度。
tags: [demo-wall, intl, gdpr, audit, prisma, foreign-key, cascade, setnull, compliance]
generated: { by: "reference_agent/trae-cn", at: 2026-04-22T00:00:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-04-22T00:00:00+08:00 }
status: stable
stale_after: 2026-10-22
sources:
  - id: src
    resource: /references/demo-wall-intl-source.md
    title: Demo Wall Intl 源码信源索引
---

## 外键策略变更

国际版对 Prisma Schema 中审计日志表的外键策略做了关键调整，这是面向 GDPR 合规的重要变更：

| 表 | 关系字段 | 中文版 onDelete | 国际版 onDelete | 影响 |
|---|---------|:---:|:---:|------|
| SysAuthLog | user (→ SysUser) | Cascade | **SetNull** | 删除用户时认证日志保留，userId 置 null |
| SysOperationLog | operator (→ SysUser) | Cascade | **SetNull** | 删除用户时操作日志保留，operatorId 置 null |

### Schema 定义对比

**中文版（Cascade）**：
```prisma
model SysAuthLog {
  // ...
  user   SysUser? @relation(fields: [userId], references: [id], onDelete: Cascade)
  userId String?
  // ...
}
```

**国际版（SetNull）**：
```prisma
model SysAuthLog {
  // ...
  user   SysUser? @relation(fields: [userId], references: [id], onDelete: SetNull)
  userId String?
  // ...
}

model SysOperationLog {
  // ...
  operator   SysUser? @relation(fields: [operatorId], references: [id], onDelete: SetNull)
  operatorId String?
  // ...
}
```

## 为什么从 Cascade 改为 SetNull

### Cascade 的问题（中文版）

`onDelete: Cascade` 意味着删除用户时，数据库会自动级联删除该用户所有的认证日志和操作日志。这在国内项目中很常见（注重"数据干净"，删除用户后清理所有关联数据），但在国际合规场景下存在严重问题：

1. **GDPR 审计要求**：GDPR 要求企业能够证明其数据处理活动的合规性，审计日志是关键证据。删除用户时销毁日志 = 销毁证据
2. **被遗忘权的边界**：GDPR 第17条规定了"被遗忘权"（用户有权要求删除个人数据），但这并不意味着可以销毁审计记录。审计日志中虽然包含 userId，但属于"合规必需"的数据，在保留期内不应删除
3. **安全事件追溯**：如果用户在删除账号前进行了恶意操作，Cascade 删除日志后将无法追溯
4. **孤儿记录风险是可控的**：Cascade 的主要优点是避免孤儿记录，但 SetNull 通过将外键置 null 解决了参照完整性问题

### SetNull 的优势（国际版）

1. **审计链不断裂**：删除用户后，"谁在什么时间从哪个IP登录"、"谁执行了什么操作"的记录完整保留
2. **GDPR 合规**：满足审计数据留存要求，用户个人数据（姓名/邮箱等）被删除，但操作历史保留
3. **参照完整性**：外键字段置 null 而非悬空，数据库约束仍然有效
4. **可追溯性**：日志中显示为"已删除用户"的操作记录，可用于安全分析

## DateTime 精度简化

国际版还将 DateTime 字段精度从 `@db.Timestamptz(6)`（微秒精度）简化为 `@db.Timestamptz`（默认精度，PostgreSQL 默认毫秒级）：

| 字段 | 中文版 | 国际版 |
|------|--------|--------|
| DateTime 类型 | @db.Timestamptz(6) | @db.Timestamptz |

这个变更的影响很小：
- 日志的 created_at 排序和筛选精确到秒已足够
- 微秒精度在业务系统中几乎无用
- 降低精度可微幅减少存储和索引开销
- Prisma 在应用层以 JavaScript Date 对象（毫秒精度）处理时间，微秒精度在应用层也会丢失

## SetNull 的实现要求

使用 SetNull 策略需要注意：

### 1. 外键字段必须 nullable

```prisma
userId String?  // 注意 ? 表示 nullable
```

如果字段是非 nullable 的（`userId String`），SetNull 会导致数据库错误。

### 2. 查询日志时处理 null 用户

```typescript
// 查询审计日志时，null 用户显示为"已删除用户"
const logs = await prisma.sysAuthLog.findMany({
  include: { user: true },
  orderBy: { createdAt: 'desc' }
});

const formatted = logs.map(log => ({
  ...log,
  username: log.user?.username || '已删除用户',
  // 不要因为 user 为 null 就报错
}));
```

### 3. 删除用户的操作流程

国际版删除用户时（替代封禁）：

```typescript
async function deleteUser(userId: string, operatorId: string) {
  await prisma.$transaction([
    // 1. 记录删除操作（在删除用户前记录，因为操作日志需要operatorId）
    prisma.sysOperationLog.create({
      data: {
        action: 'user_delete',
        targetType: 'user',
        targetId: userId,
        operatorId: operatorId,
        detail: `Deleted user ${userId}`
      }
    }),
    // 2. 删除用户（SetNull 自动将日志的 userId/operatorId 置 null）
    prisma.sysUser.delete({ where: { id: userId } }),
  ]);
}
```

删除后：
- 用户的个人数据（用户名、邮箱、密码哈希、头像等）被删除
- 认证日志保留，userId 为 null
- 操作日志保留，operatorId 为 null
- 用户提交的作品处理策略需单独定义（如保留但标记为"已删除用户作品"或级联删除）

## 与移除封禁功能的协同

SetNull 外键策略与移除封禁功能形成协同：

| 处置方式 | 中文版 | 国际版 |
|---------|--------|--------|
| 轻微违规 | 封禁账号（ban） | 内容审核驳回（rejected/hidden） |
| 严重违规 | 封禁 + 删除内容 | 删除用户（SetNull 保留日志） |
| 审计追溯 | 封禁有记录，但删除用户会 Cascade 销毁日志 | 删除用户保留完整审计链 |

国际版的安全模型是：
1. **内容层面**：auditStatus/displayStatus 双状态机控制内容可见性
2. **用户层面**：不做封禁，严重违规直接删除用户
3. **审计层面**：删除用户不销毁日志，保证合规追溯

## 相关概念

- [Demo Wall Intl 简介](00-introduction.md)
- [与中文版完整差异对照](06-differences-from-cn.md)
- [符合GDPR的用户删除操作示例](../examples/user-deletion-gdpr.md)
