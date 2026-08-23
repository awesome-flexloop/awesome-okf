---
type: Example
title: 从中文版迁移到国际版指南
description: 从trae-co-creation-demo-wall中文版迁移到trae-co-creation-demo-wall-intl国际版的完整步骤，包括代码差异、数据库迁移、环境变量变更、部署切换。
tags: [demo-wall, intl, migration, upgrade, example, deployment]
generated: { by: "reference_agent/trae-cn", at: 2026-04-22T00:00:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-04-22T00:00:00+08:00 }
status: stable
stale_after: 2026-10-22
sources:
  - id: src
    resource: /references/demo-wall-intl-source.md
    title: Demo Wall Intl 源码信源索引
---

## 迁移概述

国际版不是中文版的直接升级，而是基于同一核心架构的定向变体。迁移需要理解两版的核心差异：部署范式从 Docker 转向 Vercel、用户治理模型从封禁转向删除、审计外键从 Cascade 转向 SetNull、语言从3种扩展到5种。

## 迁移前评估

在开始迁移前，评估以下问题：

| 问题 | 如果"是" | 如果"否" |
|------|---------|---------|
| 是否需要部署到 Vercel？ | 国际版是正确选择 | 中文版 Docker 部署可能更简单 |
| 是否需要支持英语/东南亚用户？ | 国际版提供5种语言 | 中文版3种语言可能够用 |
| 是否需要 CSV 数据导出？ | 国际版内置此功能 | 可在中文版自行添加 |
| 是否需要 GDPR 合规？ | 国际版 SetNull 策略适配 | 中文版 Cascade 不满足审计要求 |
| 是否依赖用户封禁功能？ | 需要自行回加 ban.ts（参见后文） | 国际版已移除，无需迁移封禁数据 |
| 当前部署是否使用 nginx？ | 国际版移除 nginx，需调整 | 无影响 |

## 迁移步骤

### 步骤一：备份数据

**重要**：在任何迁移操作前完整备份数据库。

```bash
# PostgreSQL 备份
pg_dump $DATABASE_URL > backup_before_intl_migration.sql

# 备份 COS 文件（如需要）
# 使用腾讯云 COS 工具或控制台备份
```

### 步骤二：代码仓库切换

国际版是独立仓库（不是中文版的分支），需要克隆新仓库：

```bash
# 停止旧版服务
docker-compose down  # 如果使用 Docker

# 克隆国际版
git clone https://github.com/xinetzone/trae-co-creation-demo-wall-intl.git
cd trae-co-creation-demo-wall-intl

# 安装依赖
npm install
```

如果你在中文版基础上有自定义修改，需要手动 cherry-pick 到国际版：

```bash
# 添加中文版 remote
git remote add cn https://github.com/xinetzone/trae-co-creation-demo-wall.git
git fetch cn

# Cherry-pick 自定义提交（排除中文版专属文件：ban.ts、brand/、nginx 配置等）
git cherry-pick <commit-hash>
```

### 步骤三：数据库 Schema 迁移

国际版对 Prisma Schema 做了以下变更，需要执行迁移：

#### 1. 外键策略变更（Cascade → SetNull）

```sql
-- SysAuthLog.user: 从 Cascade 改为 SetNull
-- 注意：SetNull 要求外键字段必须是 nullable（String?），如果当前是 String 需要先改
ALTER TABLE "SysAuthLog" DROP CONSTRAINT IF EXISTS "SysAuthLog_userId_fkey";
ALTER TABLE "SysAuthLog" ALTER COLUMN "userId" DROP NOT NULL;
ALTER TABLE "SysAuthLog" ADD CONSTRAINT "SysAuthLog_userId_fkey"
  FOREIGN KEY ("userId") REFERENCES "SysUser"("id") ON DELETE SET NULL;

-- SysOperationLog.operator: 从 Cascade 改为 SetNull
ALTER TABLE "SysOperationLog" DROP CONSTRAINT IF EXISTS "SysOperationLog_operatorId_fkey";
ALTER TABLE "SysOperationLog" ALTER COLUMN "operatorId" DROP NOT NULL;
ALTER TABLE "SysOperationLog" ADD CONSTRAINT "SysOperationLog_operatorId_fkey"
  FOREIGN KEY ("operatorId") REFERENCES "SysUser"("id") ON DELETE SET NULL;
```

> 如果你从中文版开始且 SysAuthLog.userId 已经是 nullable（String?），则只需要 DROP/ADD 约束。

#### 2. DateTime 精度变更（可选）

```sql
-- DateTime 精度从 Timestamptz(6) 改为 Timestamptz
-- 这是可选变更，不影响功能，可以跳过
```

#### 3. 清理封禁相关数据

国际版移除了封禁功能，如果你的中文版有封禁数据，可以选择清理或保留（代码不会再消费）：

```sql
-- 可选：清理封禁相关字典项（如果存在且不再需要）
-- DELETE FROM "SysDictItem" WHERE "dictCode" IN ('banned_users', 'blocked_email_domains');

-- 建议保留：如果以后可能恢复封禁功能，保留这些字典数据
```

#### 4. 使用 Prisma 迁移

推荐使用 Prisma migrate 进行 schema 变更：

```bash
# 复制国际版的 prisma/schema.prisma
# 然后执行
npx prisma migrate dev --name migrate-to-intl

# 生产环境
npx prisma migrate deploy
```

> 注意：国际版 Dockerfile 和 entrypoint.sh 使用 `prisma db push` 而非 `prisma migrate deploy`。迁移期间建议先手动执行 migrate，后续部署时再根据环境选择。

### 步骤四：环境变量变更

| 变量 | 中文版 | 国际版 | 操作 |
|------|--------|--------|------|
| `DATABASE_URL` | ✅ 需要 | ✅ 需要 | 保持不变 |
| `NEXTAUTH_SECRET` | ✅ 需要 | ✅ 需要 | 保持不变 |
| `NEXTAUTH_URL` | ✅ 需要 | ✅ 需要 | 更新为新域名 |
| `COS_*` | ✅ 需要 | ✅ 需要 | 保持不变 |
| `REDIS_URL` | ✅ 需要 | ❌ 不需要 | 可移除（国际版不用 Redis） |
| `EDGE_CONFIG` | ❌ 不存在 | ✅ Vercel 自动注入 | Vercel 部署时自动配置 |
| `EDGE_CONFIG_ID` | ❌ 不存在 | ✅ 需要 | Vercel Edge Config 控制台获取 |
| `VERCEL_API_TOKEN` | ❌ 不存在 | ✅ 需要 | Vercel 账户设置中创建 |
| `ADMIN_EMAIL` | 可选 | 可选 | 保持不变 |
| `ADMIN_PASSWORD` | 可选 | 可选 | 保持不变 |

### 步骤五：翻译数据迁移

国际版新增了 id-ID 和 vi-VN 两种语言，需要：

1. **创建新翻译文件**：
```bash
# 翻译文件已在国际版源码中提供
# src/messages/id-ID.json
# src/messages/vi-VN.json
```

2. **补充字典 labelI18n**：

```typescript
// 为现有字典数据补充印尼语和越南语翻译
// 可以编写脚本批量补充（默认填充英语标签，后续由运营翻译）
import { prisma } from './src/lib/prisma';

async function migrateDictionaryTranslations() {
  const items = await prisma.sysDictItem.findMany();
  for (const item of items) {
    const labelI18n = item.labelI18n as Record<string, string> || {};
    let updated = false;
    // 为新语言填充默认英语标签
    if (!labelI18n['id-ID']) {
      labelI18n['id-ID'] = labelI18n['en-US'] || item.name;
      updated = true;
    }
    if (!labelI18n['vi-VN']) {
      labelI18n['vi-VN'] = labelI18n['en-US'] || item.name;
      updated = true;
    }
    if (updated) {
      await prisma.sysDictItem.update({
        where: { id: item.id },
        data: { labelI18n },
      });
    }
  }
}
```

### 步骤六：部署切换

#### 方案 A：切换到 Vercel（推荐）

1. 在 Vercel 导入国际版仓库
2. 配置环境变量（参见 [Vercel部署配置示例](/examples/setup-vercel-deployment.md)）
3. 配置外部 PostgreSQL 连接（Neon/Supabase 或保持原数据库）
4. 部署并测试
5. 切换 DNS 到 Vercel 域名
6. 验证所有功能正常后，关闭旧 Docker 服务

#### 方案 B：保持 Docker 部署

国际版保留了 Docker 部署能力，但需要调整：

1. **调整 docker-compose.yml**：移除 nginx 和 redis 服务（或保留 redis 做其他用途）
2. **调整反向代理**：如果需要 nginx，需要自行配置（国际版 docker-compose 不再内置 nginx）
3. **修改 Dockerfile**（可选）：将 `npm install` 改回 `npm ci` 确保确定性构建
4. **Edge Config 不可用**：Docker 部署下 getDictionaries() 始终返回 null，字典数据直接查数据库，功能正常但无边缘缓存加速
5. **CSV 导出**：5000 条上限仍然适用，但 Docker 无 Vercel 60 秒超时限制，可适当调整（不推荐超过 10000 条）

```yaml
# docker-compose.yml 调整示例
services:
  app:
    build: .
    ports:
      - "3000:3000"  # 直接暴露 3000，无 nginx
    environment:
      - DATABASE_URL=postgresql://...
      - NEXTAUTH_SECRET=...
      # EDGE_CONFIG 相关变量不设置，自动降级
    depends_on:
      - db

  db:
    image: postgres:16
    # ... 数据库配置

  # nginx 服务已移除
  # redis 服务已移除
```

### 步骤七：修复中间件正则 Bug（如需要）

国际版 middleware.ts 中 isProtectedRoute 正则存在遗漏 id-ID/vi-VN 的 Bug。如果你的部署需要印尼语/越南语用户访问受保护页面，需要修复：

```typescript
// src/middleware.ts
// 替换硬编码正则
// const isProtectedRoute = (pathname: string) => {
//   return /^\/(zh-CN|en-US)\/(submit|console|profile)/.test(pathname);
// };

// 使用动态正则
import { routing } from './lib/language/routing';
const localePattern = routing.locales.join('|');
const isProtectedRoute = (pathname: string) => {
  return new RegExp(`^/(${localePattern})/(submit|console|profile)`).test(pathname);
};
```

### 步骤八：同步 Edge Config（Vercel 部署）

如果使用 Vercel 部署，首次部署后需要触发 Edge Config 同步：

1. 登录管理员账号
2. 访问 `/api/sync-edge-config` 触发同步
3. 验证字典数据在各语言下正常显示

## 功能映射表

迁移后功能对应关系：

| 中文版功能 | 国际版对应 | 迁移说明 |
|-----------|-----------|---------|
| 用户封禁（ban.ts） | 删除用户（DELETE /api/users） | 封禁用户需改为删除用户；审计日志保留 |
| 邮箱域名屏蔽 | 无 | 注册时不再检查域名黑名单 |
| Redis 缓存 | Vercel Edge Config（字典） | 仅字典数据缓存，其他无缓存（可用 react-query 客户端缓存） |
| nginx 反向代理 | Vercel Edge CDN | Vercel 自动处理 SSL、CDN、路由 |
| `npm ci` 构建 | `npm install` 构建 | Vercel 环境自动处理缓存 |
| `prisma db push --accept-data-loss` | `prisma db push` | 更保守的迁移策略 |
| 3 种语言 | 5 种语言 | 默认语言改为 en-US |
| 品牌 logo | 无 | 需自行添加品牌资源 |
| 二维码功能 | 无 | 需自行添加 qrcode 依赖 |
| 无 CSV 导出 | CSV 导出 | 新增功能，无需迁移 |
| Cascade 删除日志 | SetNull 保留日志 | 需要数据库迁移 |

## 回滚方案

如果迁移失败，可以回滚到中文版：

1. 恢复数据库备份：`psql $DATABASE_URL < backup_before_intl_migration.sql`
2. 切换回中文版代码仓库
3. 恢复 docker-compose 服务（含 nginx/redis）
4. 验证功能正常

> 注意：SetNull 变更后回滚到 Cascade 可能有问题——如果迁移期间有用户被删除（产生 null userId 的日志），Cascade 约束要求 userId 非空且引用存在的用户。回滚前需要处理这些 null 记录（删除或关联到系统用户）。

## 验证清单

迁移完成后验证以下项：

- [ ] 用户注册/登录/登出正常
- [ ] 所有5种语言可切换，翻译正确
- [ ] 受保护路由（submit/console/profile）在所有5种语言下都需要认证
- [ ] 管理后台可正常访问
- [ ] 作品提交、编辑、审核正常
- [ ] CSV 导出正常，Excel 打开无乱码
- [ ] 文件上传到 COS 正常
- [ ] 用户删除后审计日志保留（userId 为 null）
- [ ] Edge Config 同步正常（Vercel 部署）
- [ ] 字典数据在各语言下正确显示
- [ ] Docker 部署（如使用）应用可正常启动

## 相关内容

- [与中文版完整差异对照](/concepts/06-differences-from-cn.md)
- [Vercel部署](/concepts/05-vercel-deployment.md)
- [Vercel部署配置示例](/examples/setup-vercel-deployment.md)
- [符合GDPR的用户删除操作示例](/examples/user-deletion-gdpr.md)
