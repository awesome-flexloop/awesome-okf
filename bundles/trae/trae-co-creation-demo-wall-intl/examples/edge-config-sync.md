---
type: Example
title: Edge Config 字典缓存同步示例
description: 演示字典同步流程：修改字典数据→调用sync-edge-config API→验证边缘缓存生效→模拟降级回退到数据库。
tags: [demo-wall, intl, edge-config, cache, sync, example, vercel]
generated: { by: "reference_agent/trae-cn", at: 2026-04-22T00:00:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-04-22T00:00:00+08:00 }
status: stable
stale_after: 2026-10-22
sources:
  - id: src
    resource: /references/demo-wall-intl-source.md
    title: Demo Wall Intl 源码信源索引
---

## Edge Config 工作流程概述

```
1. 管理员修改字典数据（数据库）
2. 管理员调用 POST /api/sync-edge-config
3. API 查询数据库字典 → 序列化（BigInt→string）→ PATCH 到 Vercel Edge Config
4. 全球边缘节点在几秒内同步新数据
5. 前端/API 通过 getDictionaries() 从边缘节点读取
6. 如果 Edge Config 不可用，自动降级到数据库查询
```

## 前置条件

- 已在 Vercel 部署并配置 Edge Config（参见 [Vercel部署配置示例](/examples/setup-vercel-deployment.md)）
- 管理员账号
- 配置了 `EDGE_CONFIG_ID` 和 `VERCEL_API_TOKEN` 环境变量

## 步骤一：修改字典数据

首先在管理后台修改字典数据。例如，新增一个作品分类：

1. 登录管理员账号
2. 进入管理后台 → 字典管理
3. 找到分类字典（category），新增一项：
   - code: `ai-agent`
   - labelI18n:
     - en-US: `AI Agent`
     - zh-CN: `AI 智能体`
     - ja-JP: `AIエージェント`
     - id-ID: `Agen AI`
     - vi-VN: `Đại lý AI`
   - sortOrder: 50
4. 保存到数据库

此时新分类已写入数据库，但 Edge Config 中仍然是旧数据，前端页面不会立即显示新分类。

## 步骤二：触发 Edge Config 同步

### 方式一：通过浏览器（最简单）

管理员登录后，直接在浏览器中访问：

```
https://your-domain.vercel.app/api/sync-edge-config
```

或者通过管理后台的"同步缓存"按钮触发。

### 方式二：通过 curl（适合自动化）

```bash
# 获取管理员 session token（从浏览器 cookie 中复制 next-auth.session-token）
curl -X POST https://your-domain.vercel.app/api/sync-edge-config \
  -H "Content-Type: application/json" \
  -H "Cookie: next-auth.session-token=your-admin-session-token" \
  -d "{}"
```

### 方式三：通过 Vercel API 直接更新（高级）

```bash
curl -X PATCH "https://api.vercel.com/v1/edge-config/${EDGE_CONFIG_ID}/items" \
  -H "Authorization: Bearer ${VERCEL_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "operation": "upsert",
        "key": "dictionaries",
        "value": {
          "countries": [...],
          "cities": [...],
          "categories": [...],
          "honors": [...]
        }
      }
    ]
  }'
```

## 步骤三：验证同步成功

同步成功后，API 返回类似：

```json
{
  "success": true,
  "syncedAt": "2026-04-22T08:30:00.000Z",
  "counts": {
    "countries": 247,
    "cities": 3400,
    "categories": 8,
    "honors": 5
  }
}
```

### 验证前端生效

1. 打开作品提交页 `/en-US/submit`
2. 查看分类下拉框，新添加的 "AI Agent" 分类应已出现
3. 切换语言（如中文），下拉框应显示 "AI 智能体"

### 验证边缘缓存命中

通过响应头或 Vercel 日志判断是否从 Edge Config 读取：

```typescript
// 在 API 中添加调试信息（仅开发环境）
const cached = await getDictionaries();
console.log(cached ? 'Edge Config hit' : 'DB fallback');
```

## 步骤四：模拟降级回退

测试当 Edge Config 不可用时系统是否正常降级：

### 本地开发环境

本地开发时默认不配置 `EDGE_CONFIG` 环境变量，getDictionaries() 返回 null，系统自动从数据库查询字典：

```bash
# 本地启动（无 Edge Config）
npm run dev
```

访问提交页，字典下拉正常加载——数据来自数据库而非 Edge Config。

### 生产环境模拟

临时移除 `EDGE_CONFIG` 环境变量（不推荐在生产环境做此测试）：

1. 在 Vercel 项目设置中删除 `EDGE_CONFIG` 环境变量
2. 重新部署
3. 验证字典下拉仍能正常加载（从数据库）
4. 恢复 `EDGE_CONFIG` 环境变量并重新部署

### 模拟 Edge Config 故障

在代码中临时模拟 getDictionaries() 抛出异常：

```typescript
// edge-config.ts —— 仅用于测试
export async function getDictionaries() {
  // ...
  try {
    throw new Error('Simulated Edge Config failure');
    // ...
  } catch {
    return null;  // 降级到数据库
  }
}
```

验证：即使 Edge Config 不可用，系统仍然正常工作，字典数据从数据库读取。

## 同步 API 实现解析

```typescript
// src/app/api/sync-edge-config/route.ts
import { NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';
import { createClient } from '@vercel/edge-config';

// BigInt 序列化：Prisma 返回的 id 是 BigInt，Edge Config 不支持
function serializeBigInt(obj: unknown): unknown {
  if (typeof obj === 'bigint') {
    return obj.toString();
  }
  if (Array.isArray(obj)) {
    return obj.map(serializeBigInt);
  }
  if (obj && typeof obj === 'object') {
    return Object.fromEntries(
      Object.entries(obj).map(([k, v]) => [k, serializeBigInt(v)])
    );
  }
  return obj;
}

export async function POST() {
  // 1. 鉴权（仅管理员）
  const session = await auth();
  if (!session?.user || !hasAnyRole(session.user, ['admin', 'root'])) {
    return NextResponse.json({ error: 'Forbidden' }, { status: 403 });
  }

  // 2. 查询所有字典数据
  const [countries, cities, categories, honors] = await Promise.all([
    prisma.sysDictItem.findMany({ where: { dictCode: 'country' } }),
    prisma.sysDictItem.findMany({ where: { dictCode: 'city' } }),
    prisma.sysDictItem.findMany({ where: { dictCode: 'category' } }),
    prisma.sysDictItem.findMany({ where: { dictCode: 'honor' } }),
  ]);

  // 3. 序列化（BigInt → string）
  const dictionaries = serializeBigInt({ countries, cities, categories, honors });

  // 4. PATCH 到 Edge Config
  const edgeConfig = createClient(process.env.EDGE_CONFIG!);
  await edgeConfig.set('dictionaries', dictionaries);

  return NextResponse.json({
    success: true,
    syncedAt: new Date().toISOString(),
    counts: {
      countries: countries.length,
      cities: cities.length,
      categories: categories.length,
      honors: honors.length,
    }
  });
}
```

## getDictionaries() 使用示例

```typescript
// src/app/[language]/submit/page.tsx
import { getDictionaries } from '@/lib/edge-config';
import { pickI18nLabel } from '@/lib/utils';

async function getSubmitFormData(lang: string) {
  // 优先从 Edge Config 读取
  const cached = await getDictionaries();

  let categories;
  if (cached) {
    // Edge Config 命中，从缓存中提取当前语言标签
    categories = cached.categories.map(cat => ({
      value: cat.code,
      label: pickI18nLabel(cat, lang),
    }));
  } else {
    // 降级到数据库查询
    categories = await prisma.sysDictItem.findMany({
      where: { dictCode: 'category', enabled: true },
      orderBy: { sortOrder: 'asc' },
    }).then(items => items.map(item => ({
      value: item.code,
      label: pickI18nLabel(item, lang),
    })));
  }

  return { categories };
}
```

## 最佳实践

1. **字典变更后及时同步**：在管理后台的字典管理页面添加"同步到 Edge Config"按钮，修改后一键同步
2. **部署后自动同步**：可在 CI/CD 中自动调用 sync-edge-config，确保部署后缓存是最新的
3. **监控降级**：添加日志记录 getDictionaries() 返回 null 的频率，如果频繁降级说明 Edge Config 配置有问题
4. **不要缓存大数据**：Edge Config 总大小限制在 1MB 以下，只缓存字典等低频小数据
5. **本地开发不依赖 Edge Config**：本地开发无 Vercel 环境，确保降级路径正常工作

## 相关内容

- [Vercel Edge Config缓存](/concepts/01-edge-config-cache.md)
- [Vercel部署](/concepts/05-vercel-deployment.md)
- [Vercel部署配置示例](/examples/setup-vercel-deployment.md)
