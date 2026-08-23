---
type: reference
title: "语义内省 RFC（Semantic Introspection）"
description: "GraphQL AI 工作组语义内省 RFC 登记，涵盖动机、__search 语义搜索、__SearchResult 类型、__SchemaDefinition 联合、__definitions 坐标查找及潜在扩展。"
sources:
  - path: "external/libs/GraphQL/ai-wg/rfcs/semantic-introspection.md"
    facts: [F-587, F-588, F-589, F-590, F-591, F-592, F-593, F-594, F-595, F-596, F-597, F-598, F-599, F-600, F-601, F-602, F-603, F-604, F-605, F-606, F-607, F-608, F-609, F-610, F-611, F-612]
---

# 语义内省 RFC（Semantic Introspection）

## 信源概述

| 信源 | 类型 | 事实范围 | 职责 |
|------|------|----------|------|
| external/libs/GraphQL/ai-wg/rfcs/semantic-introspection.md | RFC | F-587~F-612 | 提议扩展 GraphQL 内省系统，支持自然语言语义搜索 API 能力 |

## 关键事实登记

### 元信息（F-587）

- **作者**：Pascal Senn 和 Michael Staib（ChilliCream）
- **状态**：草案（RFC）

### 动机与背景（F-588~F-593）

#### 摘要

RFC 提议扩展 GraphQL 内省系统，通过标准化 `__search` 端点和相关类型实现 schema 能力的语义搜索，使 AI agent 和 LLM 能用自然语言查询发现相关 API 能力。

#### MCP 与 GraphQL 的相似性（F-589~F-591）

RFC 指出 MCP 的工具抽象与 GraphQL 高度相似：

| 维度 | MCP | GraphQL |
|------|-----|---------|
| 读数据 | MCP tool（读） | Query 字段 |
| 写数据 | MCP tool（写） | Mutation 字段 |
| 输入/输出定义 | JSON Schema | 类型系统 |
| 本质 | 具有类型化输入输出的可调用操作 | 自诞生以来即提供相同能力 |

差异主要是表面的：JSON Schema vs 类型系统、扁平工具 vs 图组合字段。

RFC 提出核心问题：GraphQL 现有 schema 和内省能力能否扩展为 AI agent 的一等工具提供者，包括 prompts？

#### 当前 LLM 与 GraphQL 交互的三种方式（F-592）

1. **遍历完整 schema**：通过内省或 schema 文件，昂贵且对大 schema 不切实际
2. **依赖预训练知识**：脆弱且不可泛化到新 API
3. **接收手工工具描述**：每个 API 需人工编写，维护成本高

#### 机会（F-593）

通过语义搜索扩展内省，实现 **"学一次，到处用"（learn once, use anywhere）** 模式：
- LLM 学一次 GraphQL 规范和语义内省协议
- 从此可发现和使用任何实现此规范的 GraphQL API
- API 提供者索引 schema 一次
- 无需每 API 训练或自定义工具定义

### 提议 1：语义搜索内省（__search）（F-594~F-602）

#### __search 字段定义（F-594~F-598）

```graphql
extend type Query {
  """
  Search the schema for capabilities matching the provided query.
  """
  __search(
    query: String!
    first: Int! = 10
    after: String
    minScore: Float
  ): [__SearchResult!]!
}
```

**参数说明**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `query` | `String!` | 自然语言查询或搜索词，应被解释为描述所需能力的自然语言 |
| `first` | `Int! = 10` | 最大返回结果数 |
| `after` | `String` | 不透明前向分页游标；提供时结果必须从该游标位置之后开始；游标值必须从之前 `__SearchResult` 的 `cursor` 字段获取 |
| `minScore` | `Float` | 可选最低分数；提供时所有返回结果必须 score >= minScore |

结果应按 score 降序排列。

**分页模型**：简单快进模型——将最后结果的 cursor 作为 after 参数获取下一页；返回结果少于 first 时表示无更多页。

#### __SearchResult 类型（F-599~F-602）

```graphql
type __SearchResult {
  coordinate: String!
  definition: __SchemaDefinition!
  pathsToRoot: [[String!]!]!
  score: Float
  cursor: String!
}
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `coordinate` | `String!` | Schema 坐标标识匹配的定义，如 `"Query.user"` 或 `"Mutation.createPost(input: )"` |
| `definition` | `__SchemaDefinition!` | 匹配的 schema 定义 |
| `pathsToRoot` | `[[String!]!]!` | 从根字段到匹配定义的路径列表；每条路径是从根到匹配定义的 schema 坐标序列 |
| `score` | `Float` | 相关性分数，应在 [0.0, 1.0] 范围，1.0 表示最高相关性 |
| `cursor` | `String!` | 分页游标，传递给 `__search` 的 `after` 参数获取下一页 |

**pathsToRoot 语义**：
- 提供从根字段到匹配定义的路径列表，辅助查询构造
- 若定义可通过多条路径到达，可返回多条路径，但不保证穷尽
- 若匹配定义本身是根字段，路径只包含单个元素

**示例**：给定 schema：
```graphql
type Query { userByEmail(email: String!): User }
type User { email: String! }
```

匹配 `User.email` 的搜索结果返回：
```json
{ "pathsToRoot": [["Query.userByEmail", "User.email"]] }
```

匹配根字段 `Query.userByEmail` 返回：
```json
{ "pathsToRoot": [["Query.userByEmail"]] }
```

**编者注**（F-602）：`pathsToRoot` 字段放在 `__SearchResult` 上，但其可能更应属于 schema 定义类型本身（如 `__Field`、`__Type`），需进一步讨论。

### __SchemaDefinition 联合类型（F-603）

```graphql
union __SchemaDefinition =
  | __Type
  | __Field
  | __InputValue
  | __EnumValue
  | __Directive
```

表示可通过语义搜索发现的所有可内省 schema 定义的联合类型。

### 提议 2：坐标查找内省（__definitions）（F-604~F-606）

```graphql
extend type Query {
  """
  Resolves schema definitions by their schema coordinates.
  Returns the resolved definitions in the same order as the input coordinates.
  """
  __definitions(
    coordinates: [String!]!
  ): [__SchemaDefinition!]!
}
```

**设计目的**：
- 通过 schema 坐标直接查找定义，消除通过 `__schema`、`__type` 等遍历内省图的需要
- 可独立于 `__search` 使用，是通用内省原语
- 与 `__search` 自然配合形成"发现-解析"两步工作流

**使用示例**：
```graphql
query {
  __definitions(coordinates: ["Query.userByEmail", "User"]) {
    ... on __Type { name kind fields { name type { name kind ofType { name } } } }
    ... on __Field { name description type { name kind ofType { name } } args { name type { name kind } defaultValue } }
  }
}
```

**编者注**（F-606）：`__definitions` 与 `__search` 自然配合，但本身也是通用内省原语，任何处理 schema 坐标的工具都可受益。

### 索引要求（F-607）

遵循此规范的实现：
- **必须（MUST）** 维护活跃 schema 的索引
- **可以（MAY）** 使用任意向量化或索引策略
- **应该（SHOULD）** 至少索引：类型名、字段名和描述

索引策略有意留给实现决定。

### 完整使用示例

```graphql
query {
  __search(query: "Find a user by their email address") {
    coordinate
    score
    pathsToRoot
    definition {
      ... on __Field {
        name
        description
        args { name type { name } }
      }
    }
  }
}
```

示例响应：
```json
{
  "data": {
    "__search": [
      {
        "coordinate": "Query.userByEmail",
        "score": 0.92,
        "pathsToRoot": [["Query.userByEmail"]],
        "definition": {
          "name": "userByEmail",
          "description": "Retrieve a user by their email address",
          "args": [{ "name": "email", "type": { "name": "String" } }]
        }
      },
      {
        "coordinate": "User.email",
        "score": 0.71,
        "pathsToRoot": [
          ["Query.userByEmail", "User.email"],
          ["Query.users", "User.email"]
        ],
        "definition": {
          "name": "email",
          "description": "The user's email address",
          "args": []
        }
      }
    ]
  }
}
```

### 潜在扩展（F-608~F-611）

#### 扩展 A：使用示例（F-608~F-609）

提议 `__Example` 类型和在各内省类型上扩展 `examples` 字段：

```graphql
type __Example {
  operation: String!
  description: String
}

extend type __Type { examples: [__Example!] }
extend type __Field { examples: [__Example!] }
extend type __InputValue { examples: [__Example!] }
extend type __EnumValue { examples: [__Example!] }
extend type __Directive { examples: [__Example!] }
```

为 AI agent 和人类开发者提供使用示例。

#### 扩展 B：MCP 风格 Prompts（F-610~F-611）

提议在 Query 上扩展 `__prompts` 字段和 `__Prompt` 类型：

```graphql
extend type Query {
  __prompts: [__Prompt!]!
}

type __Prompt {
  name: String!
  description: String
  arguments: [__InputValue!]!
}
```

Schema 可暴露 prompt 模板，为 AI agent 提供预定义交互模式。

### 开放问题（F-612）

1. **有效性**：此方法对 LLM 是否实际有效？
2. **安全考虑**：语义搜索的速率限制和访问控制是否需要安全指导？
3. **命名冲突**：`capabilities` 命名可能与主仓库中已有的 Semantic Introspection RFC 冲突

### 反馈请求

RFC 征求以下反馈：
- 是否解决了真实需求？
- 是否适合作为 GraphQL 内省的扩展，还是应作为独立机制？
- 这种发现方式对 LLM 是否有效？
- 对实现复杂度有何顾虑？
