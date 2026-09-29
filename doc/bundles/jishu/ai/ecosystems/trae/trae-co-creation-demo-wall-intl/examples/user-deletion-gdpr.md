---
type: Example
title: 符合GDPR的用户删除操作示例
description: 演示SetNull外键策略下删除用户的正确流程：记录操作日志→删除用户（日志自动保留）→验证审计链完整性→查询"已删除用户"的历史记录。
tags: [demo-wall, intl, gdpr, user-deletion, audit, setnull, example, compliance]
generated: { by: "reference_agent/trae-cn", at: 2026-04-22T00:00:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-04-22T00:00:00+08:00 }
status: stable
stale_after: 2026-10-22
sources:
  - id: src
    resource: /references/demo-wall-intl-source.md
    title: Demo Wall Intl 源码信源索引
---

## GDPR 背景

GDPR（通用数据保护条例）第17条规定了"被遗忘权"（Right to Erasure）：用户有权要求控制者删除其个人数据。但同时，GDPR也要求企业保留审计日志以证明合规性。这两个要求看似矛盾——需要删除用户个人数据，但不能删除操作记录。

国际版通过 SetNull 外键策略解决了这个矛盾：
- **删除**用户的个人数据（用户名、邮箱、密码哈希等）
- **保留**审计日志，但将日志中的用户引用置为 null（"已删除用户"）

## Schema 回顾

```prisma
model SysUser {
  id            String            @id @default(cuid())
  username      String            @unique
  email         String            @unique
  passwordHash  String
  role          SysUserRole[]
  authLogs      SysAuthLog[]
  operationLogs SysOperationLog[]
  createdAt     DateTime          @default(now()) @db.Timestamptz
  updatedAt     DateTime          @updatedAt @db.Timestamptz
}

model SysAuthLog {
  id         String     @id @default(cuid())
  user       SysUser?   @relation(fields: [userId], references: [id], onDelete: SetNull)
  userId     String?
  ip         String?
  userAgent  String?
  action     String     // "login" | "logout" | "register" | "login_failed"
  success    Boolean
  createdAt  DateTime   @default(now()) @db.Timestamptz
}

model SysOperationLog {
  id         String     @id @default(cuid())
  operator   SysUser?   @relation(fields: [operatorId], references: [id], onDelete: SetNull)
  operatorId String?
  action     String
  targetType String
  targetId   String?
  detail     String?
  ip         String?
  createdAt  DateTime   @default(now()) @db.Timestamptz
}
```

关键点：
- `user`/`operator` 关系是 optional（`SysUser?`），外键字段是 nullable（`String?`）
- `onDelete: SetNull` 确保删除用户时外键自动置 null 而非级联删除日志

## 删除用户 API 实现

### 管理员删除用户

```typescript
// src/app/api/users/[id]/route.ts (DELETE)
import { NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';
import { auth, hasAnyRole } from '@/lib/auth-nextauth';
import { createAuditLog } from '@/lib/audit-log';

export async function DELETE(
  req: Request,
  { params }: { params: { id: string } }
) {
  const session = await auth();

  // 1. 鉴权：仅 admin/root 可删除用户
  if (!session?.user || !hasAnyRole(session.user, ['admin', 'root'])) {
    return NextResponse.json({ error: 'Forbidden' }, { status: 403 });
  }

  // 2. 不允许删除自己
  if (session.user.id === params.id) {
    return NextResponse.json(
      { error: 'Cannot delete yourself' },
      { status: 400 }
    );
  }

  // 3. 检查目标用户是否存在
  const targetUser = await prisma.sysUser.findUnique({
    where: { id: params.id },
    include: { role: true },
  });

  if (!targetUser) {
    return NextResponse.json({ error: 'User not found' }, { status: 404 });
  }

  // 4. 不允许删除其他 root 用户（防止权限丢失）
  if (targetUser.role.some(r => r.roleId === 'root') &&
      !hasAnyRole(session.user, ['root'])) {
    return NextResponse.json(
      { error: 'Only root can delete root users' },
      { status: 403 }
    );
  }

  // 5. 记录删除操作日志（在删除用户之前记录，因为需要 operatorId）
  await createAuditLog({
    action: 'user_delete',
    targetType: 'user',
    targetId: params.id,
    operatorId: session.user.id,
    detail: `Deleted user: ${targetUser.username} (${targetUser.email})`,
    ip: req.headers.get('x-forwarded-for') || undefined,
  });

  // 6. 删除用户（SetNull 自动将 authLogs 和 operationLogs 的外键置 null）
  await prisma.sysUser.delete({
    where: { id: params.id },
  });

  return NextResponse.json({ success: true });
}
```

### 用户自己注销账号（被遗忘权请求）

```typescript
// src/app/api/profile/delete-account/route.ts
export async function POST(req: Request) {
  const session = await auth();
  if (!session?.user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const { password } = await req.json();

  // 验证密码（防止误操作/CSRF）
  const user = await prisma.sysUser.findUnique({
    where: { id: session.user.id },
  });
  if (!user || !await bcrypt.compare(password, user.passwordHash)) {
    return NextResponse.json({ error: 'Invalid password' }, { status: 400 });
  }

  // 记录注销操作
  await createAuditLog({
    action: 'account_deletion',
    targetType: 'user',
    targetId: user.id,
    operatorId: user.id,  // 用户自己操作
    detail: 'User requested account deletion (GDPR right to erasure)',
    ip: req.headers.get('x-forwarded-for') || undefined,
  });

  // 删除用户账号
  await prisma.sysUser.delete({
    where: { id: user.id },
  });

  return NextResponse.json({ success: true });
}
```

## 作品数据处理策略

删除用户时，其提交的作品如何处理有几种策略：

### 策略一：级联删除作品

```prisma
model WorkBase {
  // ...
  author SysUser @relation(fields: [authorId], references: [id], onDelete: Cascade)
  authorId String
  // ...
}
```

用户删除时其所有作品一并删除。简单但可能丢失有价值的内容。

### 策略二：保留作品，标记为"已删除用户"（推荐）

```prisma
model WorkBase {
  // ...
  author   SysUser? @relation(fields: [authorId], references: [id], onDelete: SetNull)
  authorId String?
  // ...
}
```

将 authorId 置 null，作品保留但显示作者为"已删除用户"。这保留了社区内容，符合 GDPR 最小化原则（删除用户个人数据但保留匿名化的内容）。

## 验证审计链完整性

### 删除用户前的数据状态

```
用户: john_doe (id: "user_123")
├── 认证日志:
│   ├── 2026-04-01 10:00 - login (IP: 1.2.3.4) → userId: "user_123"
│   ├── 2026-04-02 14:30 - login (IP: 5.6.7.8) → userId: "user_123"
│   └── 2026-04-22 09:00 - login (IP: 9.10.11.12) → userId: "user_123"
└── 操作日志:
    ├── 2026-04-10 - work_submit (work_456) → operatorId: "user_123"
    └── 2026-04-22 - user_delete (user_123) → operatorId: "admin_789"
```

### 删除用户后的数据状态

```
用户: john_doe → 已删除（个人数据清除）

认证日志（保留，外键置 null）:
├── 2026-04-01 10:00 - login (IP: 1.2.3.4) → userId: null（已删除用户）
├── 2026-04-02 14:30 - login (IP: 5.6.7.8) → userId: null（已删除用户）
└── 2026-04-22 09:00 - login (IP: 9.10.11.12) → userId: null（已删除用户）

操作日志（保留，外键置 null）:
├── 2026-04-10 - work_submit (work_456) → operatorId: null（已删除用户）
└── 2026-04-22 - user_delete (user_123) → operatorId: "admin_789"（管理员操作，保留）
```

审计链完整：
- ✅ 知道谁（可能是已删除用户）在什么时间从哪个IP登录
- ✅ 知道什么时间谁（管理员）删除了哪个用户
- ✅ 知道已删除用户提交了哪些作品
- ❌ 无法关联到已删除用户的真实身份（个人数据已删除）

## 查询审计日志（处理 null 用户）

```typescript
// 查询认证日志列表
async function getAuthLogs(page: number = 1, pageSize: number = 20) {
  const logs = await prisma.sysAuthLog.findMany({
    include: { user: true },
    orderBy: { createdAt: 'desc' },
    skip: (page - 1) * pageSize,
    take: pageSize,
  });

  return logs.map(log => ({
    id: log.id,
    action: log.action,
    success: log.success,
    ip: log.ip,
    createdAt: log.createdAt,
    // 处理 null 用户：显示"已删除用户"而非报错
    username: log.user?.username || 'Deleted User',
    userEmail: log.user?.email || null,
    isDeletedUser: log.user === null,
  }));
}
```

### 日志列表 UI 显示

```tsx
function LogRow({ log }: { log: AuthLogView }) {
  return (
    <tr>
      <td>{formatDate(log.createdAt)}</td>
      <td>
        {log.isDeletedUser ? (
          <span className="text-muted-foreground italic">
            (Deleted User)
          </span>
        ) : (
          <span>{log.username}</span>
        )}
      </td>
      <td>{log.action}</td>
      <td>{log.ip}</td>
      <td>
        <Badge variant={log.success ? 'success' : 'destructive'}>
          {log.success ? 'Success' : 'Failed'}
        </Badge>
      </td>
    </tr>
  );
}
```

## 与中文版 Cascade 策略的对比

| 维度 | 中文版 Cascade | 国际版 SetNull |
|------|:-------------:|:--------------:|
| 删除用户后日志 | 级联删除 | 保留（外键置null） |
| 审计完整性 | ❌ 日志被销毁 | ✅ 审计链完整 |
| GDPR 合规 | ❌ 可能违规 | ✅ 满足留存要求 |
| 数据库清洁度 | ✅ 无孤儿记录 | ⚠️ null 外键（但数据库约束有效） |
| 查询复杂度 | 简单（user 一定存在） | 需处理 null（显示"已删除用户"） |
| 安全追溯 | 删除用户后无法追溯 | 可追溯"已删除用户"的历史行为 |

## 注意事项

1. **作品处理策略需明确**：SetNull 仅应用于日志表，作品表（WorkBase）的 author 关系需单独决定（推荐 SetNull 保留内容）
2. **null 检查贯穿全链路**：所有查询日志的代码都必须处理 `user === null` 的情况
3. **日志保留期**：GDPR 不要求永久保留审计日志，建议设定合理的保留期（如1-3年），到期后物理删除
4. **管理员操作不可 SetNull**：管理员执行的删除操作日志中 operatorId 是管理员，不会被置 null（管理员自己没被删除）

## 相关内容

- [GDPR合规审计留存](../concepts/04-gdpr-audit-retention.md)
- [与中文版完整差异对照](../concepts/06-differences-from-cn.md)
