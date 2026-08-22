---
type: Concept
title: Vercel Edge Config 缓存
description: intl版引入Vercel Edge Config作为字典数据的边缘缓存层，通过手动同步API将country/city/category/honor字典推送到全球边缘节点，getDictionaries()读取失败时优雅降级到数据库查询。
tags: [demo-wall, intl, edge-config, vercel, cache, performance]
generated: { by: "reference_agent/trae-cn", at: 2026-04-22T00:00:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-04-22T00:00:00+08:00 }
status: stable
stale_after: 2026-10-22
sources:
  - id: src
    resource: /references/demo-wall-intl-source.md
    title: Demo Wall Intl 源码信源索引
---

## 为什么需要 Edge Config

海外 Vercel 部署场景下，冷启动时的数据库查询延迟是一个显著问题。字典数据（国家/城市/分类/荣誉）是**高频读取、低频变更**的典型数据——每个列表页、筛选器、详情页都需要字典数据做标签解析，但字典变更仅在运营操作时发生（可能数周才变一次）。

中文版使用 Redis 做缓存，但海外 Vercel 部署场景下：
- Redis 需要额外配置 Upstash 或自建实例，增加成本和延迟
- Edge Config 是 Vercel 原生全球边缘网络，读取延迟 <50ms 全球一致
- Edge Config 与 Vercel 部署深度集成，零运维

## 架构概览

Edge Config 缓存层的架构分为三部分：

```
管理员操作
    │
    ▼
POST /api/sync-edge-config ──→ PATCH Vercel Management API ──→ Edge Config 存储
    │（序列化字典数据，BigInt→string）                          （全球边缘节点复制）
    │
    ▼
前端/API 请求
    │
    ▼
getDictionaries() ──→ @vercel/edge-config SDK ──→ Edge Config（边缘节点，<50ms）
    │                                    │
    │         失败/未配置                 ▼
    └──────────────────────────────→ 返回 null ──→ 回退到数据库查询
```

## getDictionaries() 实现

`src/lib/edge-config.ts` 导出 `getDictionaries()` 函数，是缓存读取的唯一入口：

```typescript
import { createClient } from '@vercel/edge-config';

let edgeConfig: ReturnType<typeof createClient> | null = null;

function getEdgeConfig() {
  if (!process.env.EDGE_CONFIG) return null;
  if (!edgeConfig) {
    edgeConfig = createClient(process.env.EDGE_CONFIG);
  }
  return edgeConfig;
}

export async function getDictionaries() {
  const client = getEdgeConfig();
  if (!client) return null;
  try {
    const dictionaries = await client.get('dictionaries');
    return dictionaries || null;
  } catch {
    return null;  // 优雅降级：Edge Config 不可用时回退到数据库
  }
}
```

### 关键设计点

1. **懒初始化**：Edge Config client 仅在首次调用时创建，避免不使用 Edge Config 时的初始化开销
2. **环境变量检查**：未设置 `EDGE_CONFIG` 环境变量时直接返回 null（本地开发场景）
3. **优雅降级**：任何异常（网络故障、权限错误、数据不存在）都返回 null 而非抛出错误，调用方回退到数据库查询
4. **单例模式**：client 实例缓存复用，避免重复创建连接

## /api/sync-edge-config 同步端点

管理员手动触发同步，将四类字典数据推送到 Edge Config：

```
POST /api/sync-edge-config
```

### 同步流程

1. **鉴权**：验证调用者为 admin 角色
2. **查询数据库**：获取 country、city、category、honor 四类字典的完整数据
3. **序列化处理**：Prisma 返回的 BigInt 类型（id 字段）需要转为 string，因为 Edge Config 只接受 JSON 兼容类型
4. **PATCH 到 Edge Config**：调用 Vercel Management API，使用 `EDGE_CONFIG_ID` 和 `VERCEL_API_TOKEN` 环境变量
5. **返回结果**：同步成功/失败状态

### 为什么是手动同步而非自动同步

字典变更频率极低（数周一次），手动同步比自动同步（webhook/定时任务）更简单可靠：

| 方案 | 优点 | 缺点 |
|------|------|------|
| **手动触发**（当前方案） | 简单可靠、无竞态条件、运营可控 | 字典变更后需手动操作 |
| 自动 webhook | 实时同步 | 需要额外开发、字典管理操作需触发webhook、失败重试复杂 |
| 定时任务 | 无需运营介入 | 同步延迟（最坏情况=定时间隔）、不必要的API调用 |

手动同步的"缺点"在低频变更场景下可接受——运营修改字典后顺手点一次同步即可。

## 缓存数据结构

Edge Config 中 `dictionaries` key 的数据结构：

```typescript
{
  countries: Array<{ id: string; code: string; name: string; labelI18n: Record<string, string> }>;
  cities: Array<{ id: string; countryId: string; name: string; labelI18n: Record<string, string> }>;
  categories: Array<{ id: string; name: string; labelI18n: Record<string, string>; sortOrder: number }>;
  honors: Array<{ id: string; name: string; labelI18n: Record<string, string>; sortOrder: number }>;
}
```

注意：
- `id` 字段在数据库中是 BigInt，序列化时转为 string（Edge Config 不支持 BigInt）
- `labelI18n` 是多语言标签映射，key 为语言代码（en-US/zh-CN/ja-JP/id-ID/vi-VN）

## Edge Config 限制与注意事项

1. **大小限制**：Edge Config 通常限制在 1MB 以下，不要缓存大数据集（如作品列表）
2. **最终一致性**：PATCH 更新后全球边缘节点同步需要几秒时间，不适合高频变更数据
3. **只读无写入**：Edge Config 是只读缓存，不能在运行时写入；写入必须通过 Vercel Management API
4. **必须处理降级**：调用 getDictionaries() 时必须处理 null 返回值，不能假设缓存永远命中
5. **环境变量**：生产环境必须配置 `EDGE_CONFIG`（Edge Config 连接字符串）和 `EDGE_CONFIG_ID`、`VERCEL_API_TOKEN`（同步API用）

## 使用模式

```typescript
// 在 API 路由或服务端组件中
async function getDicts(lang: string) {
  // 优先从 Edge Config 读取
  const cached = await getDictionaries();
  if (cached) {
    return pickI18nForDicts(cached, lang);  // 从缓存中提取对应语言标签
  }
  // 降级到数据库查询
  const [countries, cities, categories, honors] = await Promise.all([
    prisma.sysDictItem.findMany({ where: { dictCode: 'country' } }),
    prisma.sysDictItem.findMany({ where: { dictCode: 'city' } }),
    prisma.sysDictItem.findMany({ where: { dictCode: 'category' } }),
    prisma.sysDictItem.findMany({ where: { dictCode: 'honor' } }),
  ]);
  return { countries, cities, categories, honors };
}
```

## 扩展方向

如需缓存其他低频变更数据（如系统配置、排行榜周榜），可：
1. 在 sync-edge-config API 中追加新的 key 到 PATCH payload
2. 在 edge-config.ts 中添加对应的 getter 函数（同 getDictionaries() 模式）
3. 确保总大小不超过 Edge Config 限制
4. 评估变更频率——高频变更数据不适合 Edge Config

## 相关概念

- [Demo Wall Intl 简介](/concepts/00-introduction.md)
- [Vercel部署](/concepts/05-vercel-deployment.md)
- [Edge Config缓存同步示例](/examples/edge-config-sync.md)
- [Vercel部署配置示例](/examples/setup-vercel-deployment.md)
