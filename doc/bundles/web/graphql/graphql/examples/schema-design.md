---
type: example
title: "Schema 设计实战"
description: "通过内容平台场景演示 Interface 与 Union、枚举、输入对象、自定义指令、Non-Null 权衡以及 Connection/Edge/PageInfo 游标分页模式的 Schema 设计。"
sources:
  - resource: /references/spec-section-3-type-system.md
    facts: [F-112, F-113, F-114, F-115, F-116, F-117, F-138, F-141, F-143, F-144, F-147, F-149, F-150, F-156, F-157, F-158, F-159, F-161, F-164, F-165, F-166, F-167, F-168, F-172, F-173, F-174, F-175, F-176, F-179, F-180, F-181, F-182, F-183, F-184, F-185, F-192, F-193, F-195, F-196, F-197, F-198, F-199, F-200, F-201, F-202, F-203, F-204, F-213]
---

# Schema 设计实战

本文以一个内容平台（文章、视频、评论、点赞）为场景，演示 GraphQL Schema 设计中的高级类型构造：接口（Interface）、联合（Union）、枚举（Enum）、输入对象（InputObject）、自定义指令（Directive），以及游标分页的 Connection 模式。每个类型构造都配有 Schema 定义和查询示例。

## 场景概述

我们要建模的平台包含两类内容：文章（Article）和视频（Video）。它们共享一些字段（id、标题、作者、创建时间），但也有各自特有字段。内容可以被评论（Comment）和点赞（Like），这两类行为也需要被建模为统一的"时间线事件"。这自然引出 Interface 和 Union 的使用场景。

## 接口（Interface）

接口定义一组字段契约，对象类型通过 `implements` 声明实现该接口，必须包含接口的所有字段（F-147、F-156）。接口可以实现其他接口（F-158），但不能循环引用或自实现（F-159）。

### 定义接口

```graphql
interface Node {
  id: ID!
}

interface Content {
  id: ID!
  title: String!
  author: User!
  createdAt: DateTime!
  updatedAt: DateTime
}

interface Timed {
  duration: Int!
}
```

`Node` 是最基础的接口，只要求 `id` 字段。`Content` 要求内容类实体具备标题、作者和时间戳。`Timed` 为有时长的内容（如视频、音频）定义契约。

### 实现接口

对象类型可以实现一个或多个接口，使用 `&` 分隔（F-139）：

```graphql
type User implements Node {
  id: ID!
  name: String!
  email: String!
  articles: [Article!]!
  videos: [Video!]!
}

type Article implements Node & Content {
  id: ID!
  title: String!
  author: User!
  createdAt: DateTime!
  updatedAt: DateTime
  body: String!
  wordCount: Int!
  comments: [Comment!]!
}

type Video implements Node & Content & Timed {
  id: ID!
  title: String!
  author: User!
  createdAt: DateTime!
  updatedAt: DateTime
  duration: Int!
  thumbnailUrl: String!
  views: Int!
  comments: [Comment!]!
}
```

注意 `Video` 同时实现了 `Content` 和 `Timed` 两个接口，因此必须包含两者的全部字段。`Article` 不需要 `duration`，所以不实现 `Timed`。

### 查询接口字段

在接口类型上只能直接选择接口上声明的字段（F-161、F-262）。要访问实现类型的特有字段，需要使用内联片段（F-054）：

```graphql
query GetContent($id: ID!) {
  content(id: $id) {
    id
    title
    createdAt
    ... on Article {
      wordCount
      body
    }
    ... on Video {
      duration
      thumbnailUrl
      views
    }
  }
}
```

当 `content` 返回 Article 时，响应包含 `wordCount` 和 `body`；返回 Video 时包含 `duration`、`thumbnailUrl` 和 `views`。这就是多态查询。

## 联合（Union）

联合类型表示"多个对象类型之一"，但与接口不同——联合不定义共享字段（F-164、F-168）。联合成员必须全部是 Object 基类型，不能是 Scalar、Interface 或其他 Union（F-167）。

### 定义联合

```graphql
union TimelineEvent = Comment | Like | ContentPublished

type Comment {
  id: ID!
  author: User!
  text: String!
  createdAt: DateTime!
}

type Like {
  id: ID!
  user: User!
  target: Content!
  createdAt: DateTime!
}

type ContentPublished {
  id: ID!
  content: Content!
  publishedAt: DateTime!
}
```

### 查询联合成员

Union 不定义任何字段（除元字段 `__typename` 外），必须通过片段查询成员字段（F-168、F-263）：

```graphql
query GetTimeline($userId: ID!) {
  timeline(userId: $userId, limit: 10) {
    __typename
    ... on Comment {
      id
      text
      createdAt
      author { name }
    }
    ... on Like {
      id
      createdAt
      user { name }
      target { title }
    }
    ... on ContentPublished {
      id
      publishedAt
      content {
        title
        ... on Video { duration }
      }
    }
  }
}
```

`__typename` 元字段返回具体对象类型的名称（F-220），客户端可据此区分不同成员。

### Interface 与 Union 的选择

| 特性 | Interface | Union |
|------|-----------|-------|
| 共享字段 | 是，强制实现 | 否，不定义字段 |
| 成员关系 | 显式 `implements` | 显式列在联合中 |
| 适用场景 | 多态对象有共同字段契约 | 多态对象无共同字段，仅归为一类 |
| 可嵌套接口 | 接口可实现其他接口 | 联合不能包含接口 |

## 枚举（Enum）

枚举类型定义一组具名的离散值（F-172、F-175）。枚举值在查询中以不加引号的名称表示，序列化为字符串（F-176、F-411）。

```graphql
enum ContentStatus {
  DRAFT
  IN_REVIEW
  PUBLISHED
  ARCHIVED
}

enum MediaFormat {
  MP4
  WEBM
  MOV
}

enum SortOrder {
  ASC
  DESC
}
```

枚举可作为字段类型、参数类型使用：

```graphql
type Query {
  articles(status: ContentStatus, order: SortOrder = DESC): [Article!]!
  videos(format: MediaFormat): [Video!]!
}
```

查询示例：

```graphql
query GetPublishedArticles {
  articles(status: PUBLISHED, order: DESC) {
    id
    title
    createdAt
  }
}
```

枚举值建议使用全大写命名（F-076）。字符串字面量 `"PUBLISHED"` 不能作为枚举输入，必须使用裸名称 `PUBLISHED`，否则引发 request error（F-176）。

## 输入对象（InputObject）

输入对象用于向 mutation 或 query 传递复杂结构化参数（F-179）。输入对象只能作为输入类型，不能作为字段返回类型（F-182）。

### 定义输入对象

```graphql
input CreateArticleInput {
  title: String!
  body: String!
  tagIds: [ID!]
  status: ContentStatus = DRAFT
}

input UpdateArticleInput {
  title: String
  body: String
  status: ContentStatus
}

input CreateVideoInput {
  title: String!
  duration: Int!
  thumbnailUrl: String!
  format: MediaFormat! = MP4
  tagIds: [ID!]
}
```

输入对象字段可以有默认值（F-150）。显式提供 `null` 与不提供值在语义上不同（F-185）：前者表示"将字段设为 null"，后者表示"使用默认值或保持不变"。

### 用于 Mutation

```graphql
type Mutation {
  createArticle(input: CreateArticleInput!): Article!
  updateArticle(id: ID!, input: UpdateArticleInput!): Article!
  createVideo(input: CreateVideoInput!): Video!
}
```

使用示例：

```graphql
mutation CreateDraft {
  createArticle(input: {
    title: "GraphQL Schema 设计指南"
    body: "本文介绍..."
    tagIds: ["tag_1", "tag_3"]
  }) {
    id
    title
    status
    createdAt
  }
}
```

### OneOf 输入对象

OneOf Input Object 是输入对象的特殊变体，恰好一个字段必须被设置且非 null，由 `@oneOf` 指令标记（F-186）。其所有字段必须 nullable 且无默认值（F-187）。

```graphql
input ContentFilter @oneOf {
  authorId: ID
  tagId: ID
  keyword: String
}
```

使用时必须恰好提供一个字段：

```graphql
query SearchContent($filter: ContentFilter!) {
  searchContent(filter: $filter, limit: 10) {
    __typename
    ... on Article { title wordCount }
    ... on Video { title duration }
  }
}
```

变量值（正确——只提供一个字段）：

```json
{ "filter": { "keyword": "GraphQL" } }
```

## 自定义指令（Directive）

指令是 GraphQL 的扩展机制，以 `@Name` 表示，可附加在操作、字段、片段、类型定义等多种位置（F-088、F-200、F-202、F-203）。指令可定义为 `repeatable`（可在同一位置重复使用）（F-213）。

### 定义自定义指令

```graphql
directive @auth(requires: Role!) on FIELD_DEFINITION | OBJECT

directive @cacheControl(maxAge: Int!, scope: CacheScope = PUBLIC) on FIELD_DEFINITION

directive @tag(name: String!) repeatable on FIELD_DEFINITION | OBJECT | INTERFACE

# 注意：@deprecated 是内建指令，无需在 SDL 中重新定义。
# 以下仅展示自定义指令；@deprecated 可直接在字段或枚举值上使用。

enum Role {
  ADMIN
  EDITOR
  AUTHOR
  READER
}

enum CacheScope {
  PUBLIC
  PRIVATE
}
```

指令定义包含：
- `@` 后接指令名；
- 可选的参数定义（ArgumentsDefinition）；
- 可选的 `repeatable` 关键字；
- `on` 后接一个或多个指令位置（F-200、F-201）。

### 使用自定义指令

在类型定义上使用：

```graphql
type AdminStats @auth(requires: ADMIN) {
  totalUsers: Int!
  totalRevenue: Float!
}

type Article implements Node & Content {
  id: ID!
  title: String!
  body: String!
  viewCount: Int! @cacheControl(maxAge: 60, scope: PUBLIC)
  secretNotes: String @auth(requires: EDITOR)
  oldSlug: String @deprecated(reason: "Use 'slug' instead")
  slug: String!
}
```

`repeatable` 指令可在同一位置重复出现：

```graphql
type Video implements Node & Content & Timed {
  id: ID!
  title: String!
  duration: Int!
  thumbnailUrl: String!
  views: Int!
}
```

内建指令包括 `@skip`、`@include`、`@deprecated`、`@specifiedBy`、`@oneOf`（F-204）。`@skip(if: Boolean!)` 和 `@include(if: Boolean!)` 用于在执行时条件性地包含或跳过字段（F-205、F-206、F-210）：

```graphql
query GetArticle($id: ID!, $includeBody: Boolean!) {
  article(id: $id) {
    id
    title
    body @include(if: $includeBody)
    draftNote @skip(if: $includeBody)
  }
}
```

## Non-Null 与 Nullable 的设计权衡

Non-Null 类型由尾随 `!` 表示（F-195），表示该字段永不为 null（F-197）。这看似简单，但它深刻影响错误处理语义和 Schema 演进能力。

### 设计原则

```graphql
type User implements Node {
  id: ID!                    # 始终存在——Non-Null
  name: String!              # 注册时必填——Non-Null
  email: String!             # 注册时必填——Non-Null
  avatarUrl: String          # 可能未设置头像——Nullable
  bio: String                # 可能未填写简介——Nullable
  lastLoginAt: DateTime      # 从未登录过为 null——Nullable
}
```

| 使用 Non-Null | 使用 Nullable |
|--------------|---------------|
| 数据创建时必填且永不缺失 | 数据可能缺失或尚未生成 |
| 主键、外键、时间戳 | 可选的用户配置字段 |
| 枚举状态字段 | 可能解析失败的外部数据 |
| 列表本身（`[T]!`） | 列表中的元素（视情况） |

### Non-Null 与错误爆炸半径

Non-Null 不仅是类型约束，更是错误传播的控制机制。当 Non-Null 字段解析失败时，null 会沿类型链向上冒泡到第一个可 null 的父位置（F-199、F-349、F-373）。这意味着：

- 字段 `bio: String`（nullable）解析失败 → 仅 `bio` 为 null；
- 字段 `email: String!`（Non-Null）解析失败 → 整个 `User` 对象可能为 null（若 User 在可 null 位置）；
- 若从根到错误源全链 Non-Null → 整个 `data` 为 null。

因此，设计建议：

- 对**绝对必需**的数据使用 Non-Null（如 `id: ID!`）；
- 对**可能解析失败**或**未来可能变为可选**的字段保持 nullable；
- 避免在对象层级过度使用 Non-Null，防止单点错误导致大面积数据丢失；
- Non-Null 一旦发布就难以回退——将 Non-Null 改为 Nullable 是非破坏性变更，但反过来是破坏性变更。

### List 的 Non-Null 变体

List 类型有四种组合（F-192）：

```graphql
type Example {
  a: [String]    # 列表可为 null，元素可为 null
  b: [String]!   # 列表本身不为 null，元素可为 null
  c: [String!]   # 列表可为 null，元素不为 null
  d: [String!]!  # 列表和元素都不为 null
}
```

- `c: [String!]`：列表可能为 null（如字段未加载），但一旦返回列表，其中每个元素都不为 null；
- `d: [String!]!`：最严格，列表和元素都保证非 null。

当 List 包装 Non-Null 元素类型时，单个元素解析为 null 会导致整个列表为 null（F-194、F-374）。

## Connection/Edge/PageInfo 游标分页模式

对于可能返回大量数据的列表字段，GraphQL 社区形成了 Relay 风格的 Connection 分页模式。它使用不透明游标（cursor）而非偏移量（offset），在数据频繁变化时更稳定。

### 核心类型

```graphql
"分页元数据，用于游标导航"
type PageInfo {
  "是否有下一页"
  hasNextPage: Boolean!
  "是否有上一页"
  hasPreviousPage: Boolean!
  "当前页第一条边的游标"
  startCursor: String
  "当前页最后一条边的游标"
  endCursor: String
}

"Article 与游标组成的边"
type ArticleEdge {
  "用于分页的不透明游标"
  cursor: String!
  "边的实际数据节点"
  node: Article!
}

"Article 的分页连接"
type ArticleConnection {
  "符合条件的总数"
  totalCount: Int!
  "分页元数据"
  pageInfo: PageInfo!
  "当前页的边列表"
  edges: [ArticleEdge!]!
}
```

### 在 Query 中使用

```graphql
type Query {
  articlesConnection(
    first: Int = 10
    after: String
    status: ContentStatus
  ): ArticleConnection!
}
```

参数说明：
- `first`：取多少条（向前分页）；
- `after`：游标，从该游标之后开始取；
- `status`：业务过滤参数。

### 查询第一页

```graphql
query GetFirstPage {
  articlesConnection(first: 5, status: PUBLISHED) {
    totalCount
    pageInfo {
      hasNextPage
      endCursor
    }
    edges {
      cursor
      node {
        id
        title
        createdAt
      }
    }
  }
}
```

响应：

```json
{
  "data": {
    "articlesConnection": {
      "totalCount": 42,
      "pageInfo": {
        "hasNextPage": true,
        "endCursor": "YXJyXzU="
      },
      "edges": [
        { "cursor": "YXJyXzE=", "node": { "id": "a_1", "title": "第一篇", "createdAt": "2026-01-10T08:00:00Z" } },
        { "cursor": "YXJyXzI=", "node": { "id": "a_2", "title": "第二篇", "createdAt": "2026-01-12T09:30:00Z" } },
        { "cursor": "YXJyXzM=", "node": { "id": "a_3", "title": "第三篇", "createdAt": "2026-01-15T11:00:00Z" } },
        { "cursor": "YXJyXzQ=", "node": { "id": "a_4", "title": "第四篇", "createdAt": "2026-01-18T14:20:00Z" } },
        { "cursor": "YXJyXzU=", "node": { "id": "a_5", "title": "第五篇", "createdAt": "2026-01-20T16:45:00Z" } }
      ]
    }
  }
}
```

### 查询下一页

将上一页的 `endCursor` 作为 `after` 参数传入：

```graphql
query GetNextPage($after: String!) {
  articlesConnection(first: 5, after: $after, status: PUBLISHED) {
    totalCount
    pageInfo {
      hasNextPage
      endCursor
    }
    edges {
      cursor
      node {
        id
        title
        createdAt
      }
    }
  }
}
```

变量：

```json
{ "after": "YXJyXzU=" }
```

### Connection 模式的优势

| 特性 | 偏移分页 (`limit/offset`) | 游标分页 (`first/after`) |
|------|--------------------------|-------------------------|
| 数据插入时的稳定性 | 可能重复或跳过条目 | 稳定，游标锚定具体位置 |
| 元数据 | 需额外查询总数 | `totalCount` 和 `pageInfo` 内置 |
| 双向分页 | 需自行处理 | `first/after` + `last/before` |
| 适用场景 | 静态数据、小数据集 | 实时数据、无限滚动、大数据集 |

## 完整 Schema 汇总

以下是整合上述所有类型构造的完整 Schema：

```graphql
scalar DateTime

interface Node {
  id: ID!
}

interface Content {
  id: ID!
  title: String!
  author: User!
  createdAt: DateTime!
  updatedAt: DateTime
}

interface Timed {
  duration: Int!
}

union TimelineEvent = Comment | Like | ContentPublished

type User implements Node {
  id: ID!
  name: String!
  email: String!
  avatarUrl: String
  bio: String
  articles: [Article!]!
  videos: [Video!]!
}

type Article implements Node & Content {
  id: ID!
  title: String!
  author: User!
  createdAt: DateTime!
  updatedAt: DateTime
  body: String!
  wordCount: Int!
  status: ContentStatus!
  comments: [Comment!]!
}

type Video implements Node & Content & Timed {
  id: ID!
  title: String!
  author: User!
  createdAt: DateTime!
  updatedAt: DateTime
  duration: Int!
  thumbnailUrl: String!
  format: MediaFormat!
  views: Int!
  status: ContentStatus!
  comments: [Comment!]!
}

type Comment {
  id: ID!
  author: User!
  text: String!
  createdAt: DateTime!
}

type Like {
  id: ID!
  user: User!
  target: Content!
  createdAt: DateTime!
}

type ContentPublished {
  id: ID!
  content: Content!
  publishedAt: DateTime!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}

type ArticleEdge {
  cursor: String!
  node: Article!
}

type ArticleConnection {
  totalCount: Int!
  pageInfo: PageInfo!
  edges: [ArticleEdge!]!
}

enum ContentStatus {
  DRAFT
  IN_REVIEW
  PUBLISHED
  ARCHIVED
}

enum MediaFormat {
  MP4
  WEBM
  MOV
}

enum SortOrder {
  ASC
  DESC
}

input CreateArticleInput {
  title: String!
  body: String!
  status: ContentStatus = DRAFT
  tagIds: [ID!]
}

input CreateVideoInput {
  title: String!
  duration: Int!
  thumbnailUrl: String!
  format: MediaFormat! = MP4
  tagIds: [ID!]
}

input ContentFilter @oneOf {
  authorId: ID
  tagId: ID
  keyword: String
}

directive @auth(requires: Role!) on FIELD_DEFINITION | OBJECT
directive @cacheControl(maxAge: Int!, scope: CacheScope = PUBLIC) on FIELD_DEFINITION
directive @tag(name: String!) repeatable on FIELD_DEFINITION | OBJECT

enum Role { ADMIN EDITOR AUTHOR READER }
enum CacheScope { PUBLIC PRIVATE }

type Query {
  user(id: ID!): User
  content(id: ID!): Content
  articles(status: ContentStatus, order: SortOrder = DESC): [Article!]!
  articlesConnection(first: Int = 10, after: String, status: ContentStatus): ArticleConnection!
  timeline(userId: ID!, limit: Int = 10): [TimelineEvent!]!
  searchContent(filter: ContentFilter!, limit: Int = 10): [Content!]!
}

type Mutation {
  createArticle(input: CreateArticleInput!): Article!
  createVideo(input: CreateVideoInput!): Video!
}
```

## 相关概念

- [Schema 与类型系统入门](../concepts/02-schema-and-types.md) — Schema 定义、标量类型、六种命名类型的基础概念
- [复合类型：对象、接口、联合与枚举](../concepts/03-composite-types.md) — Interface、Union、Enum、Object 的详细规范
- [指令、包装类型与输入系统](../concepts/04-directives-and-wrapping-types.md) — Non-Null/List 包装、InputObject、OneOf、自定义指令的完整语义
- [响应格式、错误冒泡与序列化](../concepts/07-response-and-errors.md) — Non-Null 设计如何影响错误传播和部分数据响应
- [基础查询与变更示例](basic-query.md) — 基础 query/mutation 语法
