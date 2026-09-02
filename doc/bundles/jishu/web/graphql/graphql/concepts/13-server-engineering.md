---
type: concept
title: "服务端工程：Schema 开发模式、Context 与 DataLoader"
description: "GraphQL 服务端工程实践：三大核心组成（Schema/Resolver/Context）与请求执行流程，Schema First vs Code First 开发模式，Context 请求级创建原则，Resolver 四参数签名与职责单一，N+1 问题与 DataLoader 批处理模式，错误处理策略，中间件/插件机制，HTTP/WebSocket 集成与部署安全。"
sources:
  - resource: SpecWeave docs/knowledge/learning/01-agent-protocols-interfaces/graphql-wiki/06-server-concepts.md
    title: GraphQL Wiki 第 6 章：服务端核心概念（learning 侧合并来源）
---

# 服务端工程：Schema 开发模式、Context 与 DataLoader

本篇覆盖 GraphQL 服务端开发的工程实践。规范层面的执行算法见[执行引擎](06-execution.md)，响应与错误规范见[响应格式](07-response-and-errors.md)；Python 服务端框架对比见 [Python 生态](10-python-ecosystem.md)。

## 服务端三大核心组成

一个典型的 GraphQL 服务由三个核心部分构成：

- **Schema（模式）**：用 SDL 定义的类型系统，描述 API 提供的所有类型、字段、参数、查询和变更操作，是客户端与服务端之间的契约
- **Resolver（解析器）**：为 Schema 中每个字段提供数据的函数，是服务端最核心的业务逻辑载体
- **Context（上下文）**：单次请求生命周期内跨所有 Resolver 共享的对象，传递数据库连接、认证用户、数据源实例等共享资源

请求执行流程：解析（Parse，查询字符串→AST）→ 验证（Validate，按 Schema 校验语法与语义）→ 上下文构建 → 执行（Execute，从根操作递归调用 Resolver）→ 结果组装 → 返回含 `data`/`errors` 的 JSON 响应。

## 两种 Schema 开发模式

### Schema First（模式优先）

先用 `.graphql` 文件编写完整 SDL 定义，再为每个字段编写 Resolver 实现，最后组合成可执行 Schema。

```graphql
# schema.graphql
type User {
  id: ID!
  name: String!
  posts: [Post!]!
}

type Query {
  user(id: ID!): User
}
```

```javascript
const resolvers = {
  Query: {
    user: (parent, args, context) => context.db.users.findById(args.id)
  },
  User: {
    posts: (parent, args, context) => context.db.posts.findByAuthorId(parent.id)
  }
};
const schema = makeExecutableSchema({ typeDefs, resolvers });
```

**优点**：Schema 即文档、前后端可围绕 Schema 并行开发、适合 API 设计先行、工具生态完善（代码生成/文档生成/Mock）。**缺点**：Schema 与 Resolver 分离两处维护、类型可能重复定义、重构需同步修改。代表：Apollo Server、graphql-tools、gqlgen（Go）。

### Code First（代码优先）

通过编程语言的类、类型注解、装饰器定义 Schema，运行时自动从代码生成 SDL，无需单独编写 SDL 文件。

```typescript
@ObjectType()
class User {
  @Field(type => ID) id: string;
  @Field() name: string;
  @Field(type => [Post])
  async posts(@Ctx() context: Context) {
    return context.db.posts.findByAuthorId(this.id);
  }
}
```

**优点**：单一数据源、编译时类型安全、重构友好（IDE 自动重命名/跳转）、无重复定义。**缺点**：Schema 隐藏在代码中需运行才可见、装饰器有学习成本、不适合纯 API 设计先行流程。代表：TypeGraphQL、Nexus、Strawberry（Python）、Sangria（Scala）。

### 如何选择

| 维度 | Schema First | Code First |
|---|---|---|
| **Schema 可见性** | 高，SDL 直接可读 | 低，需运行生成 |
| **类型安全** | 需额外工具生成类型 | 原生利用语言类型系统 |
| **重构体验** | 一般，需同步两处 | 好，IDE 支持完善 |
| **API 设计先行** | 非常适合 | 不太适合 |

小团队、快速原型、需明确 Schema 契约选 Schema First；TypeScript/强类型项目、重构频繁选 Code First。

## Context 的作用与设计原则

Context 在单次请求开始时创建、在该请求所有 Resolver 之间共享。常见内容：请求/响应对象、认证用户、数据库连接（ORM 实例）、DataLoader 实例、服务客户端、配置、日志记录器、请求 ID。

**Context 必须每个请求单独创建**，不能是全局单例，原因：①不同请求的认证用户不同，全局会导致用户信息串号；②每个请求有自己的请求头/Cookie；③DataLoader 缓存是请求级的，跨请求缓存会导致数据不一致。

```javascript
const context = async ({ req }) => {
  const token = req.headers.authorization?.replace('Bearer ', '');
  let currentUser = null;
  if (token) {
    try { currentUser = await verifyTokenAndGetUser(token); } catch (e) { /* 未登录 */ }
  }
  return {
    req, currentUser, db: prisma,
    dataLoaders: { userLoader: createUserLoader(prisma) }
  };
};
```

**使用原则**：只放确实需要跨 Resolver 访问的共享资源；避免循环引用；单个 Resolver 独用的资源不放 Context。

## Resolver 设计

### 函数签名

每个 Resolver 接收四个位置参数 `(parent, args, context, info)`：

| 参数 | 说明 |
|---|---|
| `parent` | 上一级（父）字段解析返回的结果；根字段上通常为 `undefined`/`null` |
| `args` | 该字段接收的参数对象 |
| `context` | 请求上下文，所有 Resolver 共享 |
| `info` | 执行信息（字段 Schema 定义、查询 AST、路径等），用于中间件/性能追踪等高级场景 |

Resolver 可直接返回值，也可返回 Promise，执行引擎自动处理异步。

### 职责单一原则

每个 Resolver 只负责解析自己对应的字段，不要在父 Resolver 中预先获取子字段数据（过度获取）。客户端不查询的字段，对应 Resolver 永远不会执行——这正是 GraphQL 按需获取的核心优势。

## N+1 问题与 DataLoader

### N+1 问题

查询「所有帖子及其作者」时：`Query.posts` 执行 1 次查询获取 N 篇帖子，随后每篇帖子的 `Post.author` Resolver 各执行 1 次查询，总计 **1 + N 次**数据库查询。100 篇帖子即 101 次查询，多层嵌套时更严重。

### DataLoader 模式

DataLoader（Facebook 开发的通用工具）通过**批处理（Batching）+ 缓存（Caching）**解决 N+1：

1. **批处理**：同一事件循环 tick 内，所有对同一 DataLoader 的 `.load()` 调用被收集合并为一次批量请求
2. **缓存**：同一请求内对同一 key 的重复 `.load()` 直接返回缓存结果

使用后：100 篇帖子的作者查询被收集去重（如仅 5 个不同作者），合并为 1 次 `SELECT * FROM users WHERE id IN (1,2,3,4,5)`——总共 2 次查询而非 101 次。

```javascript
// 批处理函数：返回结果必须与传入 keys 顺序一一对应
const batchGetUsers = async (userIds) => {
  const users = await db.users.findAll({ where: { id: { in: userIds } } });
  return userIds.map(id => users.find(u => u.id === id) || null);
};

// Context 中每个请求创建新实例
const context = async () => ({
  db,
  dataLoaders: { userLoader: new DataLoader(batchGetUsers) }
});

// Resolver 中使用
const resolvers = {
  Post: {
    author: (parent, args, context) =>
      context.dataLoaders.userLoader.load(parent.authorId)
  }
};
```

**关键注意事项**：

1. **必须请求级创建实例**：不能全局单例，否则跨请求数据泄漏与内存泄漏
2. **批处理结果顺序必须与 keys 顺序一致**：SQL IN 查询返回顺序不一定与传入 ids 相同，必须手动排序映射，缺失的 key 返回 `null`
3. **缓存是请求级的**：跨请求缓存需另用 Redis、HTTP 缓存等
4. **不限于数据库**：可用于任何 IO 操作（HTTP API、微服务 RPC）

## 错误处理策略

GraphQL 服务通常始终返回 **HTTP 200 OK**，错误放在响应体 `errors` 数组中（规范层面的错误格式与冒泡规则见[响应格式](07-response-and-errors.md)）。

### 抛出错误 vs 返回错误

- **抛出错误**（推荐用于真正的错误）：认证失败、系统错误、参数格式错误等，直接抛出 Error 对象，执行引擎将其放入 `errors` 数组并把对应字段设为 `null`。常用标准错误类型：`AuthenticationError`（401 语义）、`ForbiddenError`（403）、`UserInputError`（400）
- **返回错误**（用于可预期的业务结果）：登录失败、库存不足等业务分支，用 Union 类型返回结构化结果，客户端用内联片段分别处理

```graphql
union LoginResult = LoginSuccess | LoginFailed

mutation Login($email: String!, $password: String!) {
  login(email: $email, password: $password) {
    ... on LoginSuccess { token user { id name } }
    ... on LoginFailed { message remainingAttempts }
  }
}
```

| 场景 | 抛出错误 | 返回错误（Union） |
|---|---|---|
| 认证/授权失败、系统错误、参数错误 | ✅ | ❌ |
| 业务可预期失败（登录失败、库存不足） | ❌ | ✅ |

### 错误码

通过 `extensions.code` 传递程序化错误码（如 `NOT_FOUND`、`INSUFFICIENT_BALANCE`），让客户端按 `code` 而非 `message` 字符串做分支处理。**生产环境应禁用堆栈跟踪输出**，避免泄露代码结构。

## 中间件与插件

中间件（某些框架称 Plugin/Directive）拦截执行流程，在 Resolver 执行前后插入通用逻辑，处理**横切关注点**：认证/授权、操作日志、性能监控、错误上报、字段级缓存、输入验证、数据脱敏、请求限流。

常见实现方式：

1. **Resolver 级包装**：高阶函数包装 Resolver，前后执行逻辑（如计时日志）
2. **全局插件**：框架提供的请求生命周期钩子（如 Apollo Server 的 `requestDidStart`/`willSendResponse`）
3. **Schema Directive**：在 Schema 中声明式标记（如 `me: User @auth`、`users: [User!]! @rateLimit(limit: 100)`），意图清晰、无样板代码

## GraphQL 与 HTTP

- **单一端点**：通常只暴露一个端点（`/graphql`、`/api/graphql`），所有查询/变更通过请求体 `query` 字段指定
- **POST**：标准方式，请求体含 `query`/`variables`/`operationName`/`extensions`
- **GET**：仅用于幂等查询，可利用 HTTP 缓存；绝对不能用于 Mutation
- **状态码**：社区主流做法是默认始终返回 200，GraphQL 层错误通过 `errors` 数组与 `extensions.code` 表达；HTTP 层错误（401/403/413/429/500）按需使用
- **Subscription over WebSocket**：客户端握手建立连接 → 发送 `subscribe` 消息 → 服务端维持订阅并在事件触发时发送 `next` 推送 → `complete` 取消订阅 → 连接关闭自动清理。生产环境需反向代理支持连接超时与粘性会话

## 部署安全考虑

| 措施 | 说明 |
|---|---|
| **CORS 严格配置** | 生产环境限制来源白名单；需跨域 Cookie 时 `credentials: true` 且 `Access-Control-Allow-Origin` 不能为 `*` |
| **请求大小限制** | 配置 body 大小上限（如 2mb），超大请求返回 413 |
| **查询深度限制** | 限制最大嵌套层数（通常 5-15 层），防止恶意深嵌套 DoS（如 `graphql-depth-limit`） |
| **查询复杂度限制** | 为字段分配复杂度成本、计算总复杂度并设上限，防止「宽」查询过载 |
| **禁用生产环境 GraphiQL** | 交互式 IDE 暴露完整 Schema，生产应关闭或加认证 |
| **持久化查询（Persisted Queries）** | 客户端只发查询哈希 ID 和变量，服务端查表执行，防任意查询执行 |
| **速率限制与超时** | 基于 IP/用户限流；设置查询执行超时（5-30 秒） |
| **内省限制** | 内省暴露完整 Schema，公开 API 建议开放，内部 API 可关闭 |

## 相关概念

- [执行引擎：字段解析与值完成](06-execution.md)
- [响应格式、错误冒泡与序列化](07-response-and-errors.md)
- [Python 生态：客户端与服务端实践](10-python-ecosystem.md)
- [前端客户端工程](12-client-engineering.md)
- [最佳实践与反模式](14-best-practices.md)
