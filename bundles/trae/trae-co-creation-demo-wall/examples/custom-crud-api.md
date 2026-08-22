---
type: Example
title: 自定义 CRUD API 示例
description: 新增 API 路由的完整模式：创建路由文件、定义 Zod schema、Prisma 查询、权限检查、日志记录、i18n 处理。
tags: [demo-wall, example, api, crud, custom, zod, prisma]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: "/references/demo-wall-source.md"
    title: "Demo Wall 源码信源"
---

## API 开发标准模式

新增 API 路由遵循一致的模式，参考现有 API（如 /api/works、/api/dictionaries）的实现。

## 示例：新增「作品评论」API

假设需要新增作品评论功能，步骤如下：

### 步骤 1：扩展 Prisma Schema

在 prisma/schema.prisma 添加 WorkComment model：

```prisma
model WorkComment {
  id        BigInt   @id @default(autoincrement())
  workId    BigInt   @map("work_id")
  userId    BigInt   @map("user_id")
  content   String   @db.VarChar(500)
  createdAt DateTime? @default(now()) @map("created_at") @db.Timestamptz(6)
  work      WorkBase @relation(fields: [workId], references: [id], onDelete: Cascade)
  user      SysUser  @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@index([workId])
  @@index([userId])
  @@map("work_comment")
}
```

在 WorkBase 和 SysUser 中添加 comments 关系字段。

运行数据库推送：

```bash
npx prisma db push
```

### 步骤 2：创建 API 路由文件

创建 `src/app/api/works/[id]/comments/route.ts`：

```typescript
import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';
import { getAuthUser } from '@/lib/auth';
import { writeOperationLog } from '@/lib/audit-log';
import { z } from 'zod';

// 评论创建 schema
const createCommentSchema = z.object({
  content: z.string().min(1, '评论内容不能为空').max(500, '评论不能超过500字符')
});

// 评论查询 schema
const querySchema = z.object({
  page: z.coerce.number().min(1).default(1),
  pageSize: z.coerce.number().min(1).max(50).default(20)
});

/**
 * GET /api/works/[id]/comments
 * 获取作品评论列表（公开，仅返回已审核通过作品的评论）
 */
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const workId = BigInt(id);
    const { searchParams } = new URL(request.url);
    const { page, pageSize } = querySchema.parse({
      page: searchParams.get('page'),
      pageSize: searchParams.get('pageSize')
    });

    // 检查作品是否存在且公开可见
    const work = await prisma.workStatistic.findUnique({
      where: { workId },
      select: { auditStatus: true, displayStatus: true }
    });

    if (!work || work.auditStatus !== 1 || work.displayStatus !== 1) {
      return NextResponse.json({ error: '作品不存在或不可见' }, { status: 404 });
    }

    // 查询评论（分页）
    const [items, total] = await Promise.all([
      prisma.workComment.findMany({
        where: { workId },
        include: {
          user: {
            select: { id: true, username: true, avatarUrl: true }
          }
        },
        orderBy: { createdAt: 'desc' },
        skip: (page - 1) * pageSize,
        take: pageSize
      }),
      prisma.workComment.count({ where: { workId } })
    ]);

    // BigInt 序列化
    const serialized = items.map(c => ({
      ...c,
      id: String(c.id),
      workId: String(c.workId),
      userId: String(c.userId),
      user: { ...c.user, id: String(c.user.id) }
    }));

    return NextResponse.json({
      items: serialized,
      total,
      page,
      pageSize,
      totalPages: Math.ceil(total / pageSize)
    });
  } catch (error) {
    console.error('Get comments error:', error);
    return NextResponse.json({ error: '获取评论失败' }, { status: 500 });
  }
}

/**
 * POST /api/works/[id]/comments
 * 创建评论（需登录）
 */
export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    // 1. 认证检查
    const authUser = await getAuthUser();
    if (!authUser) {
      return NextResponse.json({ error: '请先登录' }, { status: 401 });
    }

    const { id } = await params;
    const workId = BigInt(id);
    const body = await request.json();

    // 2. 参数校验
    const { content } = createCommentSchema.parse(body);

    // 3. 检查作品是否存在
    const work = await prisma.workBase.findUnique({
      where: { id: workId }
    });
    if (!work) {
      return NextResponse.json({ error: '作品不存在' }, { status: 404 });
    }

    // 4. 创建评论
    const comment = await prisma.workComment.create({
      data: {
        workId,
        userId: authUser.userId,
        content
      },
      include: {
        user: {
          select: { id: true, username: true, avatarUrl: true }
        }
      }
    });

    // 5. 记录操作日志
    await writeOperationLog({
      operatorId: authUser.userId,
      module: 'comments',
      action: 'create',
      targetType: 'work',
      targetId: String(workId),
      success: true,
      request
    });

    // 6. BigInt 序列化并返回
    return NextResponse.json({
      ...comment,
      id: String(comment.id),
      workId: String(comment.workId),
      userId: String(comment.userId),
      user: { ...comment.user, id: String(comment.user.id) }
    });
  } catch (error) {
    // Zod 校验错误
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: '参数错误', details: error.errors },
        { status: 400 }
      );
    }

    // 记录失败日志
    console.error('Create comment error:', error);
    return NextResponse.json({ error: '评论失败' }, { status: 500 });
  }
}
```

### 步骤 3：权限检查模式总结

API 中的标准权限检查模式：

```typescript
// 公开接口：无需登录，但需检查数据可见性
// （如作品列表只返回 auditStatus=1 且 displayStatus=1）

// 需登录接口：
const authUser = await getAuthUser();
if (!authUser) return 401;

// 作者权限：验证资源所有权
const resource = await prisma.xxx.findUnique({ where: { id } });
if (resource.userId !== authUser.userId) return 403;

// 管理员权限：
const admin = await isAdmin();
if (!admin) return 403;
```

### 步骤 4：添加 react-query Hook（可选）

如果客户端需要使用，在 src/lib/ 下创建 Hook：

```typescript
// src/lib/use-comments.ts
'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export function useComments(workId: string, page = 1, pageSize = 20) {
  return useQuery({
    queryKey: ['comments', workId, page, pageSize],
    queryFn: async () => {
      const res = await fetch(`/api/works/${workId}/comments?page=${page}&pageSize=${pageSize}`);
      if (!res.ok) throw new Error('获取评论失败');
      return res.json();
    },
    staleTime: 60000 // 1分钟
  });
}
```

### 步骤 5：注意 BigInt 序列化

Prisma 使用 BigInt 作为主键类型，JSON.stringify 不能直接序列化 BigInt。解决方案：

1. 查询后手动转换：`String(bigintValue)`
2. 使用 audit-log.ts 中的 toSafeJson() 辅助函数
3. 在 Prisma 查询中使用 select 只返回需要的字段

## API 开发检查清单

- [ ] 是否添加了 getAuthUser() 认证检查？
- [ ] 是否做了 zod 参数校验？
- [ ] 是否检查了资源权限（所有权/角色）？
- [ ] 是否做了 BigInt 安全序列化？
- [ ] 是否调用 writeOperationLog() 记录关键操作？
- [ ] 富文本内容是否调用 sanitizeRichText()？
- [ ] 公开接口是否过滤了不可见数据（auditStatus/displayStatus）？
- [ ] 是否处理了 ZodError 等异常情况？

## 相关内容

- [API 路由设计](/concepts/06-api-routes.md)
- [CRUD 数据层](/concepts/07-crud-layer.md)
- [认证系统](/concepts/04-auth-system.md)
- [审核与治理](/concepts/10-audit-governance.md)
