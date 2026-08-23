---
type: Example
title: 用户注册认证示例
description: 用户注册 API 调用、NextAuth 登录流程、Session 获取、受保护路由访问的完整示例。
tags: [demo-wall, example, auth, registration, login, session]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: "/references/demo-wall-source.md"
    title: "Demo Wall 源码信源"
---

## 注册新用户

### API 调用

```bash
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "developer@example.com",
    "password": "mypassword123",
    "username": "developer"
  }'
```

服务端处理逻辑（F-068）：
1. 校验 email/password/username 必填
2. 检查邮箱域名是否在屏蔽列表（blocked_email_domains 字典，默认屏蔽 example.com/org/net）
3. 检查邮箱是否已注册
4. `bcrypt.hash(password, 10)` 哈希密码
5. 创建 SysUser，分配 common 角色
6. 记录注册认证日志（SysAuthLog）

> 注意：example.com 域名在屏蔽列表中，测试时使用其他域名。

### 前端表单

注册表单组件位于 `src/components/auth/sign-up-form.tsx`，使用 react-hook-form 管理状态。

## 登录

### NextAuth Credentials 登录

```bash
curl -X POST http://localhost:3000/api/auth/callback/credentials \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=developer@example.com&password=mypassword123&callbackUrl=http://localhost:3000/zh-CN"
```

authorize 回调逻辑（F-060）：
1. 通过 email 查找用户
2. 验证 passwordHash 存在
3. bcrypt compare 校验密码
4. 检查 isUserBanned()
5. 返回用户对象（JWT token 签发）

signIn event 自动记录日志并更新 lastSignInAt（F-064）。

### 受保护路由访问

登录后访问受保护路由（如 /zh-CN/submit）：

1. middleware.ts 检测 session 存在，放行请求
2. 未登录时重定向到 `/zh-CN/sign-in?callbackUrl=/zh-CN/submit`（F-115）

## 获取当前用户 Session

### 服务端（Server Component/Route Handler）

```typescript
import { getAuthUser } from '@/lib/auth';

const user = await getAuthUser();
if (!user) {
  // 未登录
  return Response.json({ error: 'Unauthorized' }, { status: 401 });
}
// user.userId (bigint), user.email, user.username, user.roles (string[])
```

getAuthUser() 流程（F-066）：
1. 调用 NextAuth auth() 获取 session
2. session.user.id 存在时查询数据库（含角色）
3. 返回 AuthUser 对象或 null

### 客户端（Client Component）

```tsx
'use client';
import { useSession } from 'next-auth/react';

function MyComponent() {
  const { data: session } = useSession();
  if (!session) return <div>请登录</div>;
  return <div>欢迎, {session.user?.email}</div>;
}
```

## 权限检查

```typescript
import { isAdmin, hasAnyRole } from '@/lib/auth';

// 检查是否管理员
if (await isAdmin()) {
  // 允许管理操作
}

// 检查是否有指定角色
if (await hasAnyRole(['admin', 'root'])) {
  // 允许操作
}
```

isAdmin() 判断 roles 是否包含 'admin' 或 'root'（F-067）。

## 修改密码

```bash
curl -X POST http://localhost:3000/api/profile/change-password \
  -H "Content-Type: application/json" \
  -H "Cookie: next-auth.session-token=<session-cookie>" \
  -d '{
    "oldPassword": "mypassword123",
    "newPassword": "newpassword456",
    "confirmPassword": "newpassword456"
  }'
```

验证规则（F-090）：旧密码正确、新密码不少于6字符、两次新密码一致。

## 退出登录

访问 `/api/auth/signout` 或使用 signOut() 函数。

## 相关内容

- [认证系统](/concepts/04-auth-system.md)
- [国际化路由](/concepts/05-i18n-routing.md)
- [开发环境搭建示例](/examples/setup-dev-environment.md)
