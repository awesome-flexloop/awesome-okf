---
type: concept
title: "最佳实践与反模式"
description: "GraphQL 生产环境工程最佳实践：Schema 命名约定与字段设计、Connections 游标分页、@deprecated 无版本演进、输入类型与 Payload 模式、N+1 与查询限制、持久化查询、认证授权与恶意查询防护、Union 业务错误模式，以及五大常见反模式。"
sources:
  - resource: SpecWeave docs/knowledge/learning/01-agent-protocols-interfaces/graphql-wiki/08-best-practices.md
    title: GraphQL Wiki 第 8 章：最佳实践（learning 侧合并来源）
---

# 最佳实践与反模式

本篇系统梳理 GraphQL 生产环境工程最佳实践。规范层面的类型系统与指令定义见 [Schema 与类型系统](02-schema-and-types.md)与[指令系统](04-directives-and-wrapping-types.md)；服务端工程基础见[服务端工程](13-server-engineering.md)。

## Schema 设计最佳实践

### 命名约定

| 元素 | 命名风格 | 示例 |
|------|----------|------|
| 字段名 | camelCase | `userName`, `createdAt`, `isActive` |
| 类型名 | PascalCase | `User`, `Post`, `UserConnection` |
| 参数名 | camelCase | `first`, `after`, `userId` |
| 枚举值 | ALL_CAPS | `ACTIVE`, `PENDING`, `DELETED` |
| 输入类型名 | PascalCase + Input 后缀 | `CreateUserInput`, `UpdatePostInput` |
| 接口名 | PascalCase（通常为形容词或名词） | `Node`, `Error`, `Timestamped` |

### 字段设计原则

- **避免过于通用的字段名**：`data`、`info`、`value` 等通用名降低自文档化能力，应使用 `fullName`、`email`、`bio` 等描述性名称
- **使用具体而非抽象的类型**：避免 `updateEntity(id: ID!, data: JSON!)` 这类丢失类型信息的设计，应按业务领域定义具体的输入/输出类型
- **合理使用 Non-Null（!）**：过度使用会限制演进能力——一旦标记 Non-Null，就不能在不破坏客户端的情况下让它返回 null。主键/业务上保证存在的字段标 Non-Null；可能因数据缺失或权限无法返回的用 Nullable；列表本身可 Non-Null，元素是否 Non-Null 需谨慎

### 分页设计：Connections/Relay 风格

一次性返回列表会导致性能与传输瓶颈。Relay 风格游标分页是社区推荐模式：

```graphql
type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}

type UserEdge {
  node: User!
  cursor: String!
}

type UserConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
  totalCount: Int
}

type Query {
  users(first: Int, after: String, last: Int, before: String): UserConnection!
}
```

核心概念：**Connection**（分页结果包装）、**Edge**（节点+游标）、**Cursor**（不透明位置标记，客户端不应解析）、**PageInfo**（分页元信息）。

简单场景可用 offset/limit 分页，但数据变动时会重复或跳过数据，大 offset 性能差，灵活性与性能不如游标分页。

### 无版本演进

废弃旧字段用 `@deprecated(reason: "...")` 标记并说明迁移路径，监控使用情况、通知客户端迁移、过渡期后再移除。

**破坏性变更（应避免）**：删除字段或类型、Non-Null 改 Nullable、更改字段参数或类型、删除枚举值、改变字段语义。

**安全的变更**：添加新字段/类型/参数、Nullable 改 Non-Null（前提是所有现有数据都有值）、添加新枚举值、标记 `@deprecated`。

### 输入类型与 Payload 模式

Mutation 推荐用输入类型而非多个独立参数——未来添加字段不改变 Mutation 签名，避免破坏性变更：

```graphql
input CreateUserInput {
  fullName: String!
  email: String!
  password: String!
}

type CreateUserPayload {
  user: User
  errors: [Error!]
  clientMutationId: String
}

type Mutation {
  createUser(input: CreateUserInput!): CreateUserPayload!
}
```

Payload 模式包装返回值便于未来扩展。

## 性能最佳实践

### N+1 与 DataLoader

N+1 问题与 DataLoader 批处理模式的完整说明见[服务端工程](13-server-engineering.md#n1-问题与-dataloader)。关键要点：DataLoader 必须请求级创建、批处理结果顺序与 keys 一致、请求内缓存。

### 查询深度限制与复杂度限制

- **深度限制**：限制最大嵌套层数，阻止过深嵌套的 DoS 查询
- **复杂度限制**：为字段分配成本（标量字段 1 点；分页连接字段按 `first`/`limit` 乘子字段复杂度；数据库密集字段更高权重），计算总复杂度并设上限（如 1000-5000）。示例：`users(first: 10) { id fullName posts(first: 5) { id title } }` 总复杂度 = 10 × (1 + 1 + 5 × (1 + 1)) = 120

### 持久化查询（Persisted Queries）

构建时客户端将查询发送到服务器生成哈希 ID，运行时只发哈希和变量。优势：减少网络传输、服务器可只允许白名单查询（防任意查询执行）、GET+哈希可被 CDN 缓存、服务器可预解析验证。

### 多层缓存策略

1. **HTTP 层缓存**：GET 请求（配合持久化查询）利用 CDN 和浏览器缓存
2. **服务端响应缓存**：基于查询哈希和变量缓存整个响应
3. **Resolver 级缓存**：DataLoader 请求级缓存或 Redis 分布式缓存
4. **客户端缓存**：Apollo Client/Relay 规范化缓存（见[前端客户端工程](12-client-engineering.md)）

## 安全最佳实践

- **认证与授权分离**：认证（你是谁）在 HTTP 中间件处理，解析出的用户信息通过 Context 传递；授权（你能做什么）在 Resolver 层或 Schema Directive 层执行，不做全局粗粒度授权
- **字段级权限控制**：在 Resolver 中检查权限，或用自定义 `@auth(requires: Role)` 指令声明式标记
- **三层防护恶意查询**：深度限制 + 复杂度限制 + 速率限制。推荐基于**复杂度**而非请求数限流——一个复杂查询的成本可能是简单查询的千倍
- **内省的生产策略**：开发环境启用；公开 API 保留内省（便于开发者）并配合其他安全措施；内部/敏感 API 可禁用（如 graphql-core 的 `NoSchemaIntrospectionCustomRule`）。禁用内省不是深度防御，仍须实施深度/复杂度限制与权限控制
- **HTTPS 传输**：生产环境必须，防止 Token 窃取与查询窃听篡改
- **输入验证**：类型系统提供基础验证，业务层仍需字符串长度、格式、数值范围验证；Resolver 中使用参数化查询或 ORM 防 SQL 注入

## 错误处理最佳实践

### 错误分类

| 错误类型 | 说明 | 处理方式 |
|----------|------|----------|
| **用户错误（User Error）** | 用户操作导致的预期内错误（邮箱已存在、密码错误、权限不足） | 推荐 Union/Interface 显式返回 |
| **系统错误（System Error）** | 意外的服务端错误（数据库失败、代码 bug） | `errors` 数组，隐藏内部细节 |

### extensions.code 机器可读错误码

推荐用 `extensions.code` 传递错误码而非让客户端解析 `message` 字符串。常见错误码：`UNAUTHENTICATED`、`FORBIDDEN`、`NOT_FOUND`、`BAD_USER_INPUT`、`INTERNAL_SERVER_ERROR`、`TOO_MANY_REQUESTS`。

### Union/Interface 业务错误模式

业务错误推荐用 Union 类型将成功与错误类型都作为返回类型的一部分，让错误成为 Schema 的显式部分：

```graphql
union CreateUserResult = CreateUserSuccess | UserAlreadyExistsError | ValidationError

interface Error {
  message: String!
}

type UserAlreadyExistsError implements Error {
  message: String!
  email: String!
}
```

客户端通过 `__typename` 显式处理每种结果。优势：错误是 Schema 显式部分、每个错误类型可含特定字段、客户端不必解析 `errors` 数组字符串。

## 工具与开发体验

- **Schema 校验与 Lint**：构建时校验 SDL 语法与类型引用；`graphql-eslint` 强制命名约定；CI 中 Schema 差异检查（Schema Diffing）检测破坏性变更
- **测试策略**：①Resolver 单元测试（Mock 数据库/外部服务）；②集成测试（真实或测试数据库，直接调用 `graphql()` 或经 HTTP，测试权限、DataLoader、错误处理）；③端到端测试（认证、网络、缓存完整链路）
- **文档化**：用字符串字面量为类型、字段、参数添加描述（GraphiQL/Playground 自动显示在文档面板），提供示例查询、废弃字段迁移指南、认证说明

## 常见反模式

### 反模式 1：过于细粒度的 Resolver 导致 N+1

为每个字段写独立数据库查询的 Resolver，嵌套查询产生 1 + N + N×M 次查询。正确做法：DataLoader 批量加载或 ORM eager loading。

### 反模式 2：将 GraphQL 当作数据库查询语言直接暴露

直接把数据库模型映射为 GraphQL 类型（如 `table(name: String!): [JSON!]!`），绕过业务逻辑与权限校验、暴露内部结构、难以演进。正确做法：GraphQL 层作为应用层，围绕业务用例设计 Query/Mutation，在 Resolver 中封装业务逻辑。

### 反模式 3：忽略缓存策略

所有请求穿透到数据库，高并发下数据库成为瓶颈。正确做法：DataLoader 请求级缓存 + Redis 热点数据缓存 + 客户端规范化缓存 + HTTP/CDN 缓存。

### 反模式 4：过度抽象导致 Schema 难以理解

为「DRY」过度使用接口/联合/泛型（如所有实体变成 `GenericEntity + attributes: JSON!`），Schema 失去自文档化能力与类型安全。正确做法：为每个业务对象定义明确类型；接口用于真正的多态场景（`Node`、`Error`）；优先具体而非通用——Schema 是给客户端开发者用的。

### 反模式 5：错误处理一刀切

即使请求完全失败也返回 200 并把所有错误塞进 `errors` 数组，迫使客户端解析 errors 判断成败。更实用的做法：HTTP 状态码表示请求级错误（解析失败 400、认证失败 401），Union/errors 数组表示业务/字段级错误，系统错误隐藏内部细节并记录日志。

## 相关概念

- [指令、包装类型与输入系统](04-directives-and-wrapping-types.md)
- [响应格式、错误冒泡与序列化](07-response-and-errors.md)
- [服务端工程：Schema 开发模式、Context 与 DataLoader](13-server-engineering.md)
- [前端客户端工程](12-client-engineering.md)
