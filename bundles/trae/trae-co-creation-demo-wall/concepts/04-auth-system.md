---
type: Concept
title: 认证系统
description: Demo Wall 的 NextAuth v5 认证配置，包括 Credentials provider、JWT session、Prisma Adapter、授权守卫和用户封禁双重检查机制。
tags: [demo-wall, auth, nextauth, jwt, credentials, rbac]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: "/references/demo-wall-source.md"
    title: "Demo Wall 源码信源"
---

## NextAuth v5 配置概览

认证系统基于 NextAuth v5 (beta) 构建，配置位于 `src/lib/auth-nextauth.ts`，导出 `handlers`、`auth`、`signIn`、`signOut`（F-058）。核心配置：

- **Adapter**：`PrismaAdapter(prisma)`，使用 Prisma 持久化 Account/Session/VerificationToken
- **Session 策略**：JWT（不使用数据库 Session）
- **Provider**：仅 Credentials（邮箱+密码）（F-059）
- **Pages**：signIn 页面路径 `/sign-in`（经 middleware 重定向到 `/{lang}/sign-in`）（F-061）

## Credentials Provider

Credentials provider 接受 `email` 和 `password` 字段（F-059）。

### authorize 回调（F-060）

认证第一道关卡：

1. 通过 email 查找 SysUser
2. 验证 passwordHash 是否存在
3. bcrypt compare 校验密码
4. 调用 `isUserBanned()` 检查封禁状态，封禁用户记录失败日志并返回 null
5. 返回用户对象（id 转为 string）

### JWT Callback（F-062）

封禁双重检查的第二道关卡：

1. 登录时设置 `token.id = user.id`
2. Node.js runtime 下检查封禁状态，若封禁则清空 `token.id` 使存量会话失效
3. Edge Runtime 下跳过（Prisma 无法在 Edge 运行，已知安全权衡）

### Session Callback（F-063）

将 `token.id` 赋值给 `session.user.id`，供客户端和服务端使用。

### signIn Event（F-064）

成功登录后：
- 写入 SysAuthLog（authType=sign_in, authChannel=credentials, authStatus=success）
- 更新 `SysUser.lastSignInAt`

## 认证工具函数

`src/lib/auth.ts` 导出（F-065~F-067）：

### AuthUser 类型

```typescript
interface AuthUser {
  userId: bigint;
  email: string;
  username: string;
  roles: string[]; // roleCode 数组
}
```

### getAuthUser()

从 NextAuth session 获取当前用户及角色（F-066）：
1. 调用 `auth()` 获取 session
2. 查询数据库获取用户及 SysUserRole→SysRole
3. 返回 AuthUser 或 null

### isAdmin()

判断角色是否包含 `'admin'` 或 `'root'`（F-067）。

### hasAnyRole()

检查是否拥有指定角色中的任意一个。

## 用户注册

`POST /api/auth/register`（F-068）：
1. 校验 email/password/username 必填
2. 检查 `isEmailDomainBlocked()` 屏蔽域名
3. 检查邮箱唯一性
4. `bcrypt.hash(password, 10)` 哈希密码
5. 创建用户，分配 `common` 角色
6. 记录注册认证日志

默认管理员账号（seed）：trae@example.com / trae1234，root 角色（F-056）。

## NextAuth 路由

`src/app/api/auth/[...nextauth]/route.ts` 导出 `handlers.GET` 和 `handlers.POST`（F-069），处理 /api/auth/signin、/api/auth/callback/* 等标准路径。

## 密码安全

- 算法：bcryptjs，salt rounds = 10（F-056, F-068）
- 修改密码需验证旧密码，新密码不少于6字符（F-090）
- 注册时检查屏蔽域名（默认 example.com/org/net，字典动态配置）
- 禁止封禁 admin/root 角色用户（F-083）

## 相关概念

- [数据模型设计](/concepts/03-data-model.md)
- [国际化路由](/concepts/05-i18n-routing.md)
- [审核与治理](/concepts/10-audit-governance.md)
- [API 路由设计](/concepts/06-api-routes.md)
- [用户注册认证示例](/examples/user-registration-auth.md)
