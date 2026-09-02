---
type: concept
title: "前端客户端工程：库选型、HTTP 协议与缓存"
description: "GraphQL 前端客户端工程实践：原生 HTTP 的局限与专用客户端库优势，Apollo Client/Relay/urql 对比，POST/GET 请求格式与请求头，GraphiQL/Playground 交互式 IDE，规范化缓存与文档缓存，@client 本地状态与乐观更新。"
sources:
  - resource: SpecWeave docs/knowledge/learning/01-agent-protocols-interfaces/graphql-wiki/05-client-basics.md
    title: GraphQL Wiki 第 5 章：客户端基础（learning 侧合并来源）
---

# 前端客户端工程：库选型、HTTP 协议与缓存

本篇覆盖 GraphQL 前端客户端开发的工程实践。规范层面的查询语言与响应格式见[查询语言基础](01-query-language-basics.md)与[响应格式](07-response-and-errors.md)；Python 侧客户端生态见 [Python 生态](10-python-ecosystem.md)。

## 为什么需要专用客户端库

使用原生 `fetch`/`axios` 可以发送 GraphQL 请求，但在实际应用开发中存在明显局限：

1. **手动模板处理**：需要手动拼接查询字符串、处理变量传递，容易出错
2. **无缓存机制**：每次请求都重新获取数据，导致重复网络请求
3. **手动状态管理**：需要手动管理加载状态、错误状态与 UI 更新逻辑
4. **无乐观更新**：Mutation 后需等待服务器响应才能更新 UI
5. **状态管理分散**：数据获取逻辑分散在各组件中
6. **无类型安全**：需手动定义 TypeScript 类型，无法与 Schema 自动同步

专用 GraphQL 客户端库提供的能力：

| 功能 | 说明 |
|---|---|
| **声明式数据获取** | 通过组件与数据的绑定关系自动管理查询的发送与更新 |
| **规范化缓存** | 自动缓存查询结果，相同数据不重复请求，更新自动通知所有使用该数据的组件 |
| **加载/错误状态管理** | 自动追踪请求的加载与错误状态 |
| **乐观 UI 更新** | Mutation 发送后立即更新界面，响应后再确认或回滚 |
| **分页支持** | 内置游标分页、偏移分页等模式 |
| **本地状态管理** | 远程数据与本地状态统一管理，无需额外引入 Redux/MobX |
| **类型安全** | 与 Schema 集成，自动生成 TypeScript 类型定义 |
| **开发工具集成** | 与浏览器 DevTools 集成，支持缓存查看、查询重放 |

## 主流客户端库对比

### Apollo Client

由 Apollo GraphQL 团队开发维护的最流行客户端：功能最全面（缓存、状态管理、分页、乐观更新、错误处理），支持 React/Vue/Angular/Svelte 等所有主流框架，规范化缓存实现成熟，支持 `@client` 指令的本地状态管理，生态丰富（Apollo DevTools、Apollo Studio、代码生成）。适合大多数项目，特别是中大型应用。

### Relay

Facebook（Meta）官方客户端，与 React 深度集成，专为高性能大规模应用设计：内置编译期优化（Relay Compiler），严格的 colocation 原则（数据需求与组件定义同文件），强大的 `@connection` 分页与数据预取，内置数据掩码（Data Masking）防止隐式数据依赖。学习曲线陡峭（Fragment、Container 等概念），仅支持 React。适合超大规模 React 应用。

### urql

Formidable 团队开发的轻量级客户端（核心约 8KB gzipped）：插件化架构（exchanges），默认文档缓存、可选规范化缓存（`@urql/exchange-graphcache`），API 简洁、学习曲线低、高度可定制。适合小型项目、对包体积敏感的应用。

### 对比总结

| 维度 | Apollo Client | Relay | urql |
|---|---|---|---|
| **包体积** | 较大（~35KB gzipped） | 中等（~25KB gzipped） | 极小（~8KB gzipped） |
| **学习曲线** | 平缓 | 陡峭 | 平缓 |
| **缓存策略** | 规范化缓存（默认） | 规范化缓存 | 文档缓存（默认）/规范化缓存（可选） |
| **框架支持** | 全框架支持 | 仅 React | 全框架支持 |
| **本地状态管理** | 内置支持 | 有限支持 | 插件支持 |
| **定制灵活性** | 中等 | 低（约定大于配置） | 高（插件化架构） |
| **推荐场景** | 大多数项目 | 大规模 React 应用 | 轻量应用、高度定制场景 |

## 原生 HTTP 请求协议约定

GraphQL 规范不绑定特定传输协议，但绝大多数服务通过 HTTP 提供，约定如下：通常使用单个端点（如 `/graphql`）处理所有请求；支持 POST（所有操作），多数实现也支持 GET（仅查询）；请求体与响应体均为 JSON。

### POST 请求格式（推荐）

POST 请求体包含三个字段：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `query` | String | ✅ 是 | GraphQL 查询或变更的字符串 |
| `variables` | Object | ❌ 否 | 变量对象 |
| `operationName` | String | ❌ 否 | 文档含多个操作时指定执行哪个 |

```json
{
  "query": "query GetHero($episode: Episode) { hero(episode: $episode) { name } }",
  "variables": { "episode": "JEDI" },
  "operationName": "GetHero"
}
```

### GET 请求仅用于幂等查询

GET 请求将 `query`/`variables`/`operationName` 作为 URL 查询参数（需 URL 编码），可利用 HTTP 缓存（浏览器、CDN）提升性能。**注意**：GET 绝对不能用于 Mutation（违反 HTTP 语义，且可能被缓存导致重复执行）；URL 有长度限制，复杂查询应使用 POST。

### 请求头

- **Content-Type**：必须设置为 `application/json`。部分实现支持 `application/graphql`（请求体直接为查询字符串，不支持变量，很少使用）
- **Authorization**：常用 Bearer Token 方式（`Authorization: Bearer <token>`）；也可用自定义头传 API Key 或 Basic Auth
- **其他**：`Accept: application/json`、`X-Request-ID`（链路追踪）等

### curl 示例

```bash
# 简单查询
curl -X POST https://example.com/graphql \
  -H "Content-Type: application/json" \
  -d '{ "query": "{ hero { name height } }" }'

# 带变量
curl -X POST https://example.com/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query GetHero($episode: Episode) { hero(episode: $episode) { name appearsIn } }",
    "variables": { "episode": "EMPIRE" }
  }'

# GET 请求（--data-urlencode 自动 URL 编码）
curl -G https://example.com/graphql \
  --data-urlencode "query={ hero { name } }"
```

### fetch 示例

```javascript
async function fetchHeroByEpisode(episode) {
  const query = `
    query GetHero($episode: Episode) {
      hero(episode: $episode) { name appearsIn friends { name } }
    }
  `;
  const response = await fetch('https://example.com/graphql', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, variables: { episode }, operationName: 'GetHero' })
  });
  const result = await response.json();
  if (result.errors) {
    throw new Error(result.errors[0].message);
  }
  return result.data;
}
```

## GraphiQL 与 GraphQL Playground

**GraphiQL**（发音 "graphical"）是 GraphQL 官方的浏览器内交互式 IDE，通常随开发环境的 `/graphql` 端点提供，核心功能：语法高亮编辑器、基于内省的自动补全、内置文档浏览器（点击即可查看类型/字段/参数描述）、查询历史、变量编辑器、请求头设置、响应格式化、错误提示。

**GraphQL Playground**（Prisma 团队）基于 GraphiQL 增强：多标签页、查询历史收藏、多端点配置、订阅的 WebSocket 调试。许多服务端框架现默认使用 Playground 或其继任者 Apollo Sandbox。

> **生产环境注意**：GraphiQL/Playground 默认只应在开发环境启用，生产环境应禁用以防止 Schema 泄露和未授权访问；如需提供给内部团队，应加身份验证保护。

## 客户端缓存

### 规范化缓存（Normalized Cache）

Apollo Client 与 Relay 使用的高级策略，将查询结果扁平化为按实体存储的记录：

1. **扁平化存储**：每个对象按 `__typename` 和 `id` 生成唯一缓存键（如 `Human:1000`），存入扁平查找表
2. **引用替换**：对象间引用替换为缓存键引用，而非完整副本
3. **自动去重**：同一对象在不同查询中只存一份
4. **自动更新**：Mutation 返回更新后的对象时，缓存实体自动更新，所有引用该实体的查询结果随之更新

例如 `human(id: "1000")` 与 `hero(episode: EMPIRE)` 若返回同一人物，缓存中只有一份 `Human:1000` 记录；后续 Mutation 更新其名字时，两个查询都会看到新值。

### 文档缓存（Document Cache）

urql 默认使用的简单策略：按查询文档整体存储结果，缓存键为查询字符串+变量的哈希。实现简单、开销小，但无法自动跨查询更新数据，适合小型应用。

### 缓存策略配置

| 策略 | 说明 |
|---|---|
| `cache-first`（默认） | 优先使用缓存，未命中则请求并缓存 |
| `network-only` | 不使用缓存，始终请求 |
| `cache-and-network` | 先返回缓存快速展示，同时请求最新数据更新 |
| `cache-only` | 只读缓存，未命中则报错 |
| `no-cache` | 既不读也不写缓存 |

## 本地状态管理与乐观更新

### @client 指令统一管理本地状态

应用状态分为**远程数据**（服务器上的数据）与**本地状态**（侧边栏展开、表单临时值、UI 主题等）。Apollo Client 与 urql 支持用 `@client` 指令标记本地字段，在一个查询中同时获取远程数据与本地状态：

```graphql
query GetUserWithSidebarState($userId: ID!) {
  user(id: $userId) {
    id
    name
    email        # 远程字段，从服务器获取
  }
  isSidebarOpen @client  # 本地字段，从客户端缓存读取
  theme @client
}
```

### 乐观更新（Optimistic UI）

Mutation 场景的重要优化：用户触发变更（如点赞、提交评论）时，UI 立即更新为预期成功状态，不等服务器响应；若服务器返回失败再回滚。乐观更新利用客户端缓存提升感知性能，让操作感觉即时响应。

### Subscription 实时推送

Subscription 通过 WebSocket 长连接实现服务器主动推送，典型场景：实时消息/聊天、通知、协作编辑、实时仪表盘。主流客户端库均有对应支持。

## 相关概念

- [GraphQL 概览与五大设计原则](00-overview.md)
- [响应格式、错误冒泡与序列化](07-response-and-errors.md)
- [内省系统](08-introspection.md) — GraphiQL 自动补全的基础
- [服务端工程：Schema 开发模式、Context 与 DataLoader](13-server-engineering.md)
