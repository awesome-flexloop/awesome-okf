---
type: example
title: "错误处理与 Non-Null 冒泡"
description: "通过图书馆场景的 Schema 演示 request error 与 execution error 的响应区别、Non-Null 错误冒泡链、errors 数组的 path/locations/extensions 字段以及部分数据响应模式。"
sources:
  - resource: /references/spec-section-5-validation.md
    facts: [F-249, F-250, F-252, F-254, F-256, F-261, F-268, F-270, F-272, F-285, F-287, F-289, F-293, F-295]
  - resource: /references/spec-section-6-execution.md
    facts: [F-303, F-307, F-308, F-309, F-311, F-313, F-349, F-355, F-356, F-361, F-368, F-369, F-370, F-371, F-372, F-373, F-374, F-375]
  - resource: /references/spec-section-7-response.md
    facts: [F-376, F-377, F-378, F-380, F-381, F-384, F-385, F-386, F-387, F-388, F-389, F-390, F-393, F-394, F-395, F-396, F-397, F-398, F-399, F-400, F-401, F-402, F-403, F-404, F-405, F-406]
---

# 错误处理与 Non-Null 冒泡

GraphQL 的错误处理是其类型系统的核心组成部分。理解 request error 与 execution error 的区别、以及 Non-Null 类型如何驱动错误冒泡，是设计健壮 Schema 和正确处理客户端响应的关键。本文通过一个图书馆场景，逐层演示错误传播机制。

## 错误分类总览

GraphQL 将错误分为两大类（F-369、F-395、F-397）：

| 特性 | Request Error | Execution Error |
|------|--------------|-----------------|
| 发生时机 | 请求执行**前**（解析、验证、变量强制转换） | 字段执行**期间**（resolver 抛错、值强制转换失败） |
| 响应中 `data` | **不得包含**（F-386） | 必须包含，可能为部分数据或 `null`（F-380） |
| 触发原因 | 语法错误、验证失败、变量无效、操作未找到 | resolver 内部错误、字段返回 null 但类型为 Non-Null |
| 通常责任方 | 客户端（F-395） | 服务端（F-398） |
| `path` 字段 | 通常无 | 必须包含，标识出错位置（F-403） |

## 演示 Schema

以下 Schema 特意混合了不同的可空性配置，用于展示各种冒泡场景：

```graphql
type Query {
  book(id: ID!): Book
  library: Library!
  reader(id: ID!): Reader
}

type Library {
  name: String!
  director: Staff!
  books: [Book!]!
}

type Staff {
  id: ID!
  name: String!
  email: String!
  profile: Profile
}

type Profile {
  bio: String!
  website: String
}

type Book {
  id: ID!
  title: String!
  isbn: String
  author: Author!
  tags: [String!]!
  reviews: [Review!]
}

type Author {
  id: ID!
  name: String!
  bio: String
}

type Review {
  id: ID!
  rating: Int!
  comment: String
  reviewer: Reader!
}

type Reader {
  id: ID!
  name: String!
  favoriteBook: Book
}
```

关键的可空性链：

- **链 A（在可空位置停止）**：`Query.book` → `Book`（可空）→ `Book.author` → `Author!` → `Author.name` → `String!`
- **链 B（冒泡到根）**：`Query.library` → `Library!` → `Library.director` → `Staff!` → `Staff.email` → `String!`
- **链 C（可空叶子）**：`Book.isbn` → `String`（可空）
- **链 D（Non-Null 列表元素）**：`Book.tags` → `[String!]!`（列表和元素均 Non-Null）
- **链 E（可空列表、Non-Null 元素）**：`Book.reviews` → `[Review!]`（列表可空，元素 Non-Null）

## Request Error 示例

Request error 在执行前发生，响应不包含 `data` 条目（F-386）。

### 语法错误

查询中包含 GraphQL 无法解析的语法：

```graphql
query {
  book(id: "b_1") {
    id
    title
  }
```

响应（缺少闭合括号）：

```json
{
  "errors": [
    {
      "message": "Syntax Error: Expected Name, found <EOF>.",
      "locations": [{ "line": 5, "column": 1 }]
    }
  ]
}
```

响应中**没有 `data` 键**，因为请求未能通过解析阶段（F-384、F-386）。

### 验证错误：选择不存在的字段

查询了 Schema 中未定义的字段（F-261）：

```graphql
query {
  book(id: "b_1") {
    id
    title
    publisher
  }
}
```

响应：

```json
{
  "errors": [
    {
      "message": "Cannot query field \"publisher\" on type \"Book\". Did you mean \"title\" or \"author\"?",
      "locations": [{ "line": 4, "column": 5 }]
    }
  ]
}
```

### 验证错误：缺少必需参数

`book` 字段的 `id` 参数类型为 `ID!`（Non-Null 且无默认值），必须提供（F-272）：

```graphql
query {
  book {
    id
    title
  }
}
```

响应：

```json
{
  "errors": [
    {
      "message": "Field \"book\" argument \"id\" of type \"ID!\" is required, but it was not provided.",
      "locations": [{ "line": 2, "column": 3 }]
    }
  ]
}
```

### 变量强制转换错误

变量值与声明类型不匹配（F-311、F-313）：

```graphql
query GetBook($bookId: ID!) {
  book(id: $bookId) {
    id
    title
  }
}
```

变量值（类型错误——传了整数给期望 ID 的场景虽可接受，但传 `null` 给 Non-Null 变量会报错）：

```json
{
  "bookId": null
}
```

响应：

```json
{
  "errors": [
    {
      "message": "Variable \"$bookId\" of non-null type \"ID!\" must not be null.",
      "locations": [{ "line": 1, "column": 17 }]
    }
  ]
}
```

### 操作名未找到

当文档包含多个命名操作，但请求的 `operationName` 不存在时（F-308）：

```json
{
  "query": "query A { book(id: \"1\") { id } } query B { reader(id: \"1\") { id } }",
  "operationName": "C"
}
```

响应：

```json
{
  "errors": [
    {
      "message": "Unknown operation named \"C\"."
    }
  ]
}
```

## Execution Error 示例

Execution error 在特定字段执行期间发生，响应始终包含 `data` 条目，同时包含 `errors` 列表（F-380、F-381、F-397）。错误发生的字段位置在 `path` 中标识（F-399、F-403）。

### 场景 1：可空叶子字段错误（最小爆炸半径）

`Book.isbn` 的类型是 `String`（可空）。当它的 resolver 抛出异常时，错误仅影响该字段本身——该位置解析为 `null`，其他字段不受影响（F-370）。

```graphql
query GetBook {
  book(id: "b_1") {
    id
    title
    isbn
    author {
      name
    }
  }
}
```

假设 `isbn` 的 resolver 因数据库超时而抛出错误。响应：

```json
{
  "data": {
    "book": {
      "id": "b_1",
      "title": "GraphQL 实战",
      "isbn": null,
      "author": {
        "name": "李青"
      }
    }
  },
  "errors": [
    {
      "message": "Failed to fetch ISBN: database connection timeout",
      "locations": [{ "line": 5, "column": 5 }],
      "path": ["book", "isbn"],
      "extensions": {
        "code": "DB_TIMEOUT",
        "service": "inventory-db"
      }
    }
  ]
}
```

要点：
- `data.book` 完整存在，只有 `isbn` 为 `null`；
- `path` 精确指向 `["book", "isbn"]`（F-403）；
- `locations` 指向查询文档中的行列位置（F-402）；
- `extensions` 是实现自定义的扩展信息（F-405），此处包含错误码和服务名。

### 场景 2：Non-Null 叶子字段冒泡到可空父级

这是最典型的冒泡场景。考虑链 A：

```
Query.book (Book, 可空)
  └─ Book.author (Author!, Non-Null)
       └─ Author.name (String!, Non-Null)
```

当 `Author.name` 的 resolver 抛出错误时（F-361、F-371）：

1. `name` 是 `String!`（Non-Null）→ 不能为 null，错误**向上冒泡**到 `author`（F-373）；
2. `author` 是 `Author!`（Non-Null）→ 不能为 null，错误**继续向上冒泡**到 `book`；
3. `book` 是 `Book`（**可空**）→ **冒泡停止**，`book` 解析为 `null`（F-349、F-373）。

```graphql
query GetBookWithAuthor {
  book(id: "b_2") {
    id
    title
    author {
      id
      name
      bio
    }
  }
}
```

响应：

```json
{
  "data": {
    "book": null
  },
  "errors": [
    {
      "message": "Failed to resolve author name: upstream service unavailable",
      "locations": [{ "line": 6, "column": 7 }],
      "path": ["book", "author", "name"]
    }
  ]
}
```

关键点：
- `path` 指向的是**错误源头** `["book", "author", "name"]`，即使该字段不在最终 `data` 中（F-404）；
- `data.book` 为 `null`——尽管 `id` 和 `title` 本身可以正常解析，但由于 `author` 子树冒泡导致整个 `book` 被置空；
- `data` 本身仍然存在（不为 `null`），因为 `book` 字段是可空的，冒泡在此停止。

### 场景 3：全链 Non-Null 冒泡到根（data 为 null）

考虑链 B：

```
Query.library (Library!, Non-Null)
  └─ Library.director (Staff!, Non-Null)
       └─ Staff.email (String!, Non-Null)
```

当 `Staff.email` 的 resolver 抛出错误时：

1. `email` 是 `String!`（Non-Null）→ 冒泡到 `director`；
2. `director` 是 `Staff!`（Non-Null）→ 冒泡到 `library`；
3. `library` 是 `Library!`（Non-Null）→ 冒泡到响应根；
4. 从根到错误源**每个位置都是 Non-Null** → `data` 条目为 `null`（F-375）。

```graphql
query GetLibrary {
  library {
    name
    director {
      id
      name
      email
      profile {
        bio
      }
    }
  }
}
```

响应：

```json
{
  "data": null,
  "errors": [
    {
      "message": "Failed to resolve staff email: permission denied",
      "locations": [{ "line": 6, "column": 7 }],
      "path": ["library", "director", "email"]
    }
  ]
}
```

整个响应数据丢失！这就是为什么**不应在对象层级过度使用 Non-Null**——一个深层字段的错误可能抹掉全部数据（F-375）。对比场景 2，`book` 字段是可空的所以数据部分保留；而 `library` 是非空的，错误无处停止。

### 场景 4：列表元素错误与冒泡

列表类型的错误行为取决于元素类型是否为 Non-Null（F-194、F-374）。

#### Non-Null 元素 + Non-Null 列表：`tags: [String!]!`

当 `tags` 列表中某个元素解析失败时：

1. 元素类型是 `String!`（Non-Null）→ 元素不能为 null，**整个列表位置**解析为 null（F-374）；
2. 列表本身是 `[String!]!`（Non-Null）→ 列表不能为 null，错误**向上冒泡**到 `book`；
3. `book` 是可空的 → 冒泡停止。

```graphql
query GetBookTags {
  book(id: "b_3") {
    id
    title
    tags
  }
}
```

假设 `tags` resolver 返回了 `["fiction", "bestseller", null, "new"]`，第三个元素为 null（可能由数据异常导致）。响应：

```json
{
  "data": {
    "book": null
  },
  "errors": [
    {
      "message": "Cannot return null for non-nullable field \"Book.tags\".",
      "locations": [{ "line": 5, "column": 5 }],
      "path": ["book", "tags", 2]
    }
  ]
}
```

注意 `path` 中的 `2` 是列表索引（从 0 开始），精确标识第三个元素出错（F-389）。即使只有一个元素异常，整个 `book` 都被置空——这就是 `[String!]!` 的代价。

#### 可空列表 + Non-Null 元素：`reviews: [Review!]`

`reviews` 字段类型是 `[Review!]`——列表本身可空，但元素不可空。当一个 review 元素内部发生 Non-Null 错误时：

1. 该 review 元素的 Non-Null 字段冒泡 → 元素位置不能为 null；
2. 元素类型是 `Review!`（Non-Null）→ **整个列表**解析为 null（F-374）；
3. 列表本身是可空的（`[Review!]` 没有外层 `!`）→ **冒泡停止**，`reviews` 为 `null`，`book` 保留。

```graphql
query GetBookReviews {
  book(id: "b_4") {
    id
    title
    reviews {
      id
      rating
      comment
      reviewer {
        name
      }
    }
  }
}
```

假设第二条 review 的 `reviewer.name` resolver 失败。响应：

```json
{
  "data": {
    "book": {
      "id": "b_4",
      "title": "类型系统设计",
      "reviews": null
    }
  },
  "errors": [
    {
      "message": "Failed to resolve reviewer name",
      "locations": [{ "line": 8, "column": 9 }],
      "path": ["book", "reviews", 1, "reviewer", "name"]
    }
  ]
}
```

`path` 为 `["book", "reviews", 1, "reviewer", "name"]`，其中 `1` 是出错元素在列表中的索引（F-389）。`reviews` 整体为 `null`，但 `book` 的其他字段保留。

#### 可空元素：假设的 `notes: [String]`

如果字段类型是 `[String]`（列表和元素都可空），单个元素错误只影响该位置：

```json
{
  "data": {
    "book": {
      "id": "b_5",
      "notes": ["first note", null, "third note"]
    }
  },
  "errors": [
    {
      "message": "Failed to resolve note at index 1",
      "path": ["book", "notes", 1]
    }
  ]
}
```

其他元素正常返回，列表和父对象都不受影响。

### 场景 5：多个同时发生的错误

一次查询可以产生多个 execution error。兄弟字段的错误互不影响——每个错误独立冒泡，各自在最近的可空位置停止（F-349、F-400）。

```graphql
query GetReaderLibrary {
  reader(id: "r_1") {
    id
    name
    favoriteBook {
      id
      title
      isbn
      author {
        name
      }
    }
  }
}
```

假设 `isbn` resolver 和 `author.name` resolver 同时失败：

- `isbn` 是可空的 → 仅 `isbn` 为 null；
- `author.name` 是 Non-Null → 冒泡到 `author`（Non-Null）→ 冒泡到 `favoriteBook`（可空，`Book` 类型）→ 停止。

响应：

```json
{
  "data": {
    "reader": {
      "id": "r_1",
      "name": "王芳",
      "favoriteBook": null
    }
  },
  "errors": [
    {
      "message": "Failed to fetch ISBN: database connection timeout",
      "locations": [{ "line": 6, "column": 7 }],
      "path": ["reader", "favoriteBook", "isbn"]
    },
    {
      "message": "Failed to resolve author name: upstream service unavailable",
      "locations": [{ "line": 8, "column": 9 }],
      "path": ["reader", "favoriteBook", "author", "name"]
    }
  ]
}
```

两个错误都出现在 `errors` 数组中。`favoriteBook` 最终为 null 是因为第二个错误（author 冒泡）导致的；第一个错误（isbn）本来只影响 isbn 字段，但被第二个错误的冒泡覆盖了。嵌套执行中止，兄弟执行继续（F-400）。

## 错误对象结构

每个错误是一个 map，包含以下字段（F-394、F-401~F-406）：

| 字段 | 必需 | 说明 |
|------|------|------|
| `message` | ✅ 是 | 面向开发者的错误描述字符串（F-401） |
| `locations` | 否 | 请求文档中的位置列表，每个位置含 `line` 和 `column`（均从 1 开始）（F-402） |
| `path` | 否 | 引发错误的响应路径，字段名为字符串，列表索引为整数（F-389、F-403） |
| `extensions` | 否 | 实现者自定义的附加信息，必须是 map（F-405） |

### path 的构建规则

`path` 是从响应根到错误位置的路径段列表（F-388）：

- 字段的 response name（别名优先）作为**字符串**段（F-389）；
- 列表索引作为**整数**段，从 0 开始（F-389）；
- 如果字段使用了别名，path 中使用**别名**而非原始字段名（F-389）。

例如，以下查询中别名为 `bookInfo`：

```graphql
query {
  bookInfo: book(id: "b_1") {
    author {
      name
    }
  }
}
```

若 `name` 出错，`path` 为 `["bookInfo", "author", "name"]`，使用别名 `bookInfo` 而非 `book`。

### extensions 的常见用法

`extensions` 可用于传递标准化错误码、追踪 ID、服务名、重试建议等：

```json
{
  "errors": [
    {
      "message": "Rate limit exceeded",
      "path": ["library"],
      "extensions": {
        "code": "RATE_LIMITED",
        "retryAfter": 30,
        "requestId": "req_abc123"
      }
    }
  ]
}
```

规范鼓励使用 `extensions` 而非添加额外的顶层错误字段，以避免与未来规范版本冲突（F-406）。

## 冒泡机制总结

Non-Null 错误冒泡遵循以下算法（F-349、F-361、F-373）：

```
字段 resolver 抛出错误或返回 null
  │
  ├─ 字段类型可空（无 !）
  │    └─ 该位置解析为 null，停止冒泡
  │
  └─ 字段类型 Non-Null（有 !）
       │
       ├─ 该位置不能为 null，错误加入 errors 列表
       ├─ null 传播到父响应位置
       │
       ├─ 父位置可空
       │    └─ 父位置解析为 null，停止冒泡
       │
       └─ 父位置也是 Non-Null
            └─ 继续向上传播...
                 │
                 └─ 若到达根且根仍为 Non-Null
                      └─ data 为 null
```

### 设计建议

基于冒泡机制，Schema 设计应遵循以下原则：

1. **根查询字段保持可空**：`Query.book(id: ID!): Book` 而非 `Book!`，让单个资源查询失败不会抹掉同次查询中的其他字段；
2. **根 Query/Mutation 类型本身的字段谨慎使用 Non-Null**：特别是 `Query.library: Library!` 这种，一个内部错误会导致整个 `data` 为 null；
3. **列表元素使用 Non-Null 需谨慎**：`[T!]!` 中单个元素异常会导致整个列表甚至父对象丢失；若元素可能独立失败，考虑使用 `[T]!`（元素可空）；
4. **对可能解析失败的外部数据保持可空**：如第三方 API 返回的字段、可选的关联数据；
5. **对标识性字段和必填业务字段使用 Non-Null**：如 `id: ID!`、`status: Status!` 等保证存在的数据。

## 相关概念

- [响应格式、错误冒泡与序列化](/concepts/07-response-and-errors.md) — 错误响应格式的完整规范，包括 execution result、request error result 和序列化映射
- [指令、包装类型与输入系统](/concepts/04-directives-and-wrapping-types.md) — Non-Null 和 List 包装类型的类型语义，是错误冒泡的类型基础
- [验证管线与规则体系](/concepts/05-validation.md) — request error 的来源：字段选择、参数、变量等验证规则
- [执行引擎：字段解析与值完成](/concepts/06-execution.md) — CompleteValue 算法和 Non-Null 错误传播的执行时机制
- [Schema 设计实战](/examples/schema-design.md) — Non-Null 与 Nullable 的设计权衡及 Connection 分页模式
