---
type: concept
title: "内省系统：GraphQL 的自描述机制"
description: "GraphQL 内省系统通过 __ 前缀保留名称、元字段（__typename/__type/__schema）和一组内省类型（__Schema/__Type/__Field/__InputValue/__EnumValue/__Directive/__TypeKind/__DirectiveLocation）使类型系统自身可被 GraphQL 语言查询，支撑工具生态并成为 AI agent 自动发现 API 能力的基础设施。"
sources:
  - resource: /references/spec-section-4-introspection.md
    facts: [F-219, F-220, F-221, F-222, F-223, F-224, F-225, F-226, F-227, F-228, F-229, F-230, F-231, F-232, F-233, F-234, F-235, F-236, F-237, F-238, F-239, F-240, F-241, F-242, F-243, F-244, F-245, F-246, F-247, F-248]
---

# 内省系统：GraphQL 的自描述机制

> **洞察5：自描述内省——从工具生态到 AI 原生基础设施**。GraphQL 通过 `__schema`/`__type` 内省系统使类型系统自身可被 GraphQL 语言查询，这不仅支撑了 GraphiQL、代码生成等开发工具，更成为 AI agent 自动发现 API 能力的基础设施。自描述不是附加特性，而是 GraphQL 设计哲学的核心体现（F-009）。

内省（Introspection）是 GraphQL 的自描述机制，允许客户端通过 GraphQL 查询语言本身查询服务的类型系统。这意味着 GraphQL 服务的 schema 不仅是服务端内部的类型定义，更是可通过标准查询发现的"活文档"。

## 保留名称与命名空间

内省系统所需的类型和字段以 `__`（两个下划线）为前缀，以避免与用户定义类型命名冲突（F-219）。

GraphQL 类型系统中的任意 Name 不得以两个下划线 `__` 开头，除非它属于内省系统（F-027）。schema 中定义的所有类型和指令名称也不得以 `__` 开头（F-102）。这一保留命名空间确保内省系统不会与用户 schema 冲突。

## 元字段（Meta Fields）

元字段是可在查询中使用的特殊字段，用于访问内省信息。

### __typename

类型名称内省元字段 `__typename: String!` 可在任意 Object、Interface 或 Union 的选择集中使用，返回执行时具体 Object 类型的名称（F-220）。

```graphql
query {
  pets {
    __typename
    ... on Cat {
      name
      meow
    }
    ... on Dog {
      name
      bark
    }
  }
}
```

响应示例：

```json
{
  "data": {
    "pets": [
      { "__typename": "Cat", "name": "Whiskers", "meow": true },
      { "__typename": "Dog", "name": "Rex", "bark": true }
    ]
  }
}
```

关键规则（F-221、F-222）：
- `__typename` 不得作为 subscription 操作的根字段包含；
- `__typename` 是隐式的，不出现在任何已定义类型的字段列表中。

### __schema 和 __type

Schema 内省元字段可从 query 操作根类型访问（F-223）：

```graphql
__schema: __Schema!
__type(name: String!): __Type
```

- `__schema` 返回服务的完整 schema 信息；
- `__type(name:)` 按名称查询单个类型。

这两个字段是隐式的，不出现在 query 操作根类型的字段列表中（F-224）。

## 通用约定

内省系统遵循以下通用约定（F-225~F-227）：

- **描述**：内省系统中所有类型提供 `description: String` 字段，可使用 Markdown 语法（F-225）；
- **弃用信息**：字段、参数、输入字段和枚举值可指示是否弃用（`isDeprecated: Boolean!`）及弃用原因（`deprecationReason: String`）（F-226）；
- **源码顺序**：内省应按源码顺序返回——object fields、input object fields、arguments、enum values、directives、union member types、implemented interfaces（F-227）。

## __Schema 类型

`__Schema` 类型是内省系统的根类型，表示整个 GraphQL schema（F-228）：

```graphql
type __Schema {
  description: String
  types: [__Type!]!
  queryType: __Type!
  mutationType: __Type
  subscriptionType: __Type
  directives(includeDeprecated: Boolean! = false): [__Directive!]!
}
```

| 字段 | 说明 |
|------|------|
| `description` | schema 的描述文本 |
| `types` | schema 中包含的所有命名类型集合 |
| `queryType` | query 根操作类型（必须存在） |
| `mutationType` | mutation 根操作类型（不支持时为 null） |
| `subscriptionType` | subscription 根操作类型（不支持时为 null） |
| `directives` | 所有可用指令集合（含内建指令） |

### types 字段规则

`types` 必须返回 schema 中包含的所有命名类型集合；可通过任意内省类型字段到达的命名类型必须包含（F-229）。从 `__Schema` 返回类型集合时，必须包含所有被引用的内建标量；未被引用的内建标量不得包含（F-120）。

### directives 字段规则

`directives` 必须返回 schema 中所有可用指令集合，包括所有内建指令（F-230）。`includeDeprecated` 参数默认为 false，为 true 时也返回已弃用指令。

### 根类型可空性

`mutationType` 在不支持 mutation 时返回 null；`subscriptionType` 在不支持 subscription 时返回 null（F-231）。`queryType` 始终非 null，因为每个 schema 必须支持 query。

## __Type 类型

`__Type` 是内省系统的核心类型，用于描述 GraphQL 中的任意类型（F-232）：

```graphql
type __Type {
  kind: __TypeKind!
  name: String
  description: String
  specifiedByURL: String
  fields(includeDeprecated: Boolean! = false): [__Field!]
  interfaces: [__Type!]
  possibleTypes: [__Type!]
  enumValues(includeDeprecated: Boolean! = false): [__EnumValue!]
  inputFields(includeDeprecated: Boolean! = false): [__InputValue!]
  ofType: __Type
  isOneOf: Boolean
}
```

### __TypeKind 枚举

`__TypeKind` 枚举表示类型的种类（F-233）：

```graphql
enum __TypeKind {
  SCALAR
  OBJECT
  INTERFACE
  UNION
  ENUM
  INPUT_OBJECT
  LIST
  NON_NULL
}
```

七种 kind 对应六种命名类型加两种包装类型（LIST 和 NON_NULL）。

### 各 kind 的字段返回规则

不同 kind 的类型在 `__Type` 各字段上返回不同值（F-234~F-241）：

#### SCALAR

- `kind`：`SCALAR`；
- `name`：类型名（String）；
- `specifiedByURL`：自定义标量可返回 URL 字符串，内建标量必须 null；
- 其他字段：null。

#### OBJECT

- `kind`：`OBJECT`；
- `name`：类型名；
- `fields`：可选字段集合（无字段时返回空集）；
- `interfaces`：实现的接口集合（无则返回空集）；
- 其他字段：null。

#### INTERFACE

- `kind`：`INTERFACE`；
- `fields`：所需字段集合；
- `interfaces`：所实现接口集合；
- `possibleTypes`：实现该接口的类型列表（必须为 object 类型）；
- 其他字段：null。

#### UNION

- `kind`：`UNION`；
- `possibleTypes`：可在该联合中表示的类型列表（必须为 object 类型）；
- 其他字段：null。

#### ENUM

- `kind`：`ENUM`；
- `enumValues`：`__EnumValue` 列表（至少一个，名称唯一）；
- 其他字段：null。

#### INPUT_OBJECT

- `kind`：`INPUT_OBJECT`；
- `inputFields`：`__InputValue` 列表；
- `isOneOf`：OneOf Input Object 返回 true，否则 false；
- 其他字段：null。

#### LIST

- `kind`：`LIST`；
- `ofType`：任意类型（列表元素类型）；
- 其他字段：null。

#### NON_NULL

- `kind`：`NON_NULL`；
- `ofType`：除 Non-Null 外的任意类型；
- 其他字段：null。

### 包装类型的递归表示

List 和 Non-Null 通过 `ofType` 字段递归表示。例如 `[String!]!` 的内省表示：

```json
{
  "kind": "NON_NULL",
  "ofType": {
    "kind": "LIST",
    "ofType": {
      "kind": "NON_NULL",
      "ofType": {
        "kind": "SCALAR",
        "name": "String"
      }
    }
  }
}
```

## __Field 类型

`__Field` 描述对象类型或接口类型的字段（F-242）：

```graphql
type __Field {
  name: String!
  description: String
  args(includeDeprecated: Boolean! = false): [__InputValue!]!
  type: __Type!
  isDeprecated: Boolean!
  deprecationReason: String
}
```

| 字段 | 说明 |
|------|------|
| `name` | 字段名（非空） |
| `description` | 字段描述 |
| `args` | 字段参数列表（`__InputValue` 集合） |
| `type` | 字段返回类型（非空） |
| `isDeprecated` | 是否已弃用 |
| `deprecationReason` | 弃用原因（未弃用时为 null） |

`args` 接受 `includeDeprecated` 参数，控制是否返回已弃用参数。

## __InputValue 类型

`__InputValue` 描述字段参数、输入对象字段或指令参数（F-243）：

```graphql
type __InputValue {
  name: String!
  description: String
  type: __Type!
  defaultValue: String
  isDeprecated: Boolean!
  deprecationReason: String
}
```

| 字段 | 说明 |
|------|------|
| `name` | 参数/输入字段名（非空） |
| `description` | 描述 |
| `type` | 类型（非空） |
| `defaultValue` | 默认值（使用 GraphQL 语言编码的字符串，无默认值时返回 null） |
| `isDeprecated` | 是否已弃用 |
| `deprecationReason` | 弃用原因 |

`defaultValue` 使用 GraphQL 语言语法编码，例如 `"10"`、`"PENDING"`、`"\"hello\""`（字符串需转义）。

## __EnumValue 类型

`__EnumValue` 描述枚举类型的枚举值（F-244）：

```graphql
type __EnumValue {
  name: String!
  description: String
  isDeprecated: Boolean!
  deprecationReason: String
}
```

## __Directive 类型

`__Directive` 描述服务支持的指令，包括内建指令和自定义指令（F-245、F-246）：

```graphql
type __Directive {
  name: String!
  description: String
  isRepeatable: Boolean!
  locations: [__DirectiveLocation!]!
  args(includeDeprecated: Boolean! = false): [__InputValue!]!
  isDeprecated: Boolean!
  deprecationReason: String
}
```

| 字段 | 说明 |
|------|------|
| `name` | 指令名（非空） |
| `description` | 描述 |
| `isRepeatable` | 是否可在单个位置重复使用（F-247） |
| `locations` | 有效指令位置列表（非空） |
| `args` | 指令参数列表 |
| `isDeprecated` | 指令是否已弃用 |
| `deprecationReason` | 弃用原因 |

`isRepeatable` 返回 Boolean，指示指令是否可在单个位置重复使用（F-247）。使用 IDL 表示 schema 时可省略内建指令定义，但内省时必须返回所有指令（包括内建指令）（F-216）。

## __DirectiveLocation 枚举

`__DirectiveLocation` 枚举列出所有有效的指令位置（F-248）：

```graphql
enum __DirectiveLocation {
  QUERY
  MUTATION
  SUBSCRIPTION
  FIELD
  FRAGMENT_DEFINITION
  FRAGMENT_SPREAD
  INLINE_FRAGMENT
  VARIABLE_DEFINITION
  SCHEMA
  SCALAR
  OBJECT
  FIELD_DEFINITION
  ARGUMENT_DEFINITION
  INTERFACE
  UNION
  ENUM
  ENUM_VALUE
  INPUT_OBJECT
  INPUT_FIELD_DEFINITION
  DIRECTIVE_DEFINITION
}
```

前 8 个是可执行指令位置（ExecutableDirectiveLocation），后 12 个是类型系统指令位置（TypeSystemDirectiveLocation）。

## 内省查询示例

### 查询所有类型名

```graphql
query {
  __schema {
    types {
      name
      kind
    }
  }
}
```

### 查询特定类型详情

```graphql
query {
  __type(name: "User") {
    name
    kind
    description
    fields {
      name
      type {
        name
        kind
        ofType {
          name
          kind
        }
      }
      args {
        name
        type {
          name
          kind
          ofType {
            name
            kind
          }
        }
        defaultValue
      }
    }
    interfaces {
      name
    }
  }
}
```

### 查询所有指令

```graphql
query {
  __schema {
    directives {
      name
      description
      isRepeatable
      locations
      args {
        name
        type {
          name
          kind
          ofType {
            name
            kind
          }
        }
        defaultValue
      }
    }
  }
}
```

### 标准内省查询

GraphQL 工具生态中广泛使用标准内省查询获取完整 schema。该查询递归查询所有类型的字段、参数、枚举值等信息，结果可用于构建客户端 schema、生成代码、驱动 IDE 自动补全等。

## 内省与工具生态

内省系统是 GraphQL 工具链的基石：

- **GraphiQL**：通过内省查询提供文档浏览器和自动补全；
- **代码生成**：根据内省结果生成类型安全的客户端代码；
- **Schema 校验**：工具可通过内省比较 schema 版本、检测 breaking change；
- **API 文档**：description 字段通过 Markdown 提供自文档化能力。

## 内省与 AI 集成

内省系统正在从"结构查询"向"语义发现"演进。AI agent 查询 `__schema` 即可了解服务端可用的所有数据类型、字段和指令，无需手写工具描述。MCP（Model Context Protocol）服务器利用 GraphQL 内省自动生成工具定义，使 LLM 能够发现和调用 GraphQL API。

语义内省 RFC 进一步提议扩展 `__search` 端点，实现自然语言能力发现，让 AI agent 可以用自然语言查询 schema 中相关的类型和字段。这一演进将内省从开发工具升级为 AI 原生基础设施。

## 相关概念

- [GraphQL 概览与五大设计原则](00-overview.md) — 自描述（Self-describing）是 GraphQL 五大设计原则之一
- [Schema 与类型系统入门](02-schema-and-types.md) — 内省系统反映的类型系统基础结构
- [指令、包装类型与输入系统](04-directives-and-wrapping-types.md) — __Directive 内省类型与指令系统对应
- [复合类型：对象、接口、联合与枚举](03-composite-types.md) — __Type 的各 kind 对应六种命名类型
- [响应格式、错误冒泡与序列化](07-response-and-errors.md) — 内省查询的响应格式遵循标准响应规范
- [GraphQL 与 AI：MCP、语义内省与 Agent](11-graphql-and-ai.md) — 内省系统在 AI agent 和 MCP 集成中的应用（洞察5）
