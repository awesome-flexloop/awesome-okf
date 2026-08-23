---
type: reference
title: "GraphQL 规范 Section 4：Introspection"
description: "GraphQL 内省系统规范，涵盖保留名称、元字段 __typename/__schema/__type，以及 __Schema、__Type、__Field 等内省类型。"
sources:
  - path: "external/libs/GraphQL/graphql-spec/spec/Section 4 -- Introspection.md"
    facts: [F-219, F-220, F-221, F-222, F-223, F-224, F-225, F-226, F-227, F-228, F-229, F-230, F-231, F-232, F-233, F-234, F-235, F-236, F-237, F-238, F-239, F-240, F-241, F-242, F-243, F-244, F-245, F-246, F-247, F-248]
---

# GraphQL 规范 Section 4：Introspection

## 信源概述

| 信源 | 类型 | 事实范围 | 职责 |
|------|------|----------|------|
| external/libs/GraphQL/graphql-spec/spec/Section 4 -- Introspection.md | 规范文档 | F-219~F-248 | 定义 GraphQL 内省系统的类型与元字段 |

## 关键事实登记

### 保留名称与元字段（F-219~F-224）

内省系统所需的类型和字段以 `__`（两个下划线）为前缀，以避免与用户定义类型命名冲突。

#### __typename 元字段

```graphql
__typename: String!
```

- 可在任意 Object、Interface 或 Union 的选择集中使用
- 返回执行时具体 Object 类型的名称
- 不得作为 subscription 操作的根字段包含
- 是隐式的，不出现在任何已定义类型的字段列表中

#### Schema 内省元字段

可从 query 操作根类型访问：

```graphql
__schema: __Schema!
__type(name: String!): __Type
```

两者都是隐式的，不出现在 query 操作根类型的字段列表中。

### 通用约定（F-225~F-227）

- 内省系统中所有类型提供 `description: String` 字段，可使用 Markdown 语法
- 字段、参数、输入字段和枚举值可指示是否弃用（`isDeprecated: Boolean!`）及弃用原因（`deprecationReason: String`）
- 内省应按源码顺序返回：object fields、input object fields、arguments、enum values、directives、union member types、implemented interfaces

### __Schema 类型（F-228~F-231）

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

- `types` 必须返回 schema 中包含的所有命名类型集合；可通过任意内省类型字段到达的命名类型必须包含
- `directives` 必须返回 schema 中所有可用指令集合（包括所有内建指令）；`includeDeprecated` 为 true 时也返回已弃用指令
- `mutationType` 在不支持 mutation 时返回 null；`subscriptionType` 在不支持 subscription 时返回 null

### __Type 类型（F-232~F-241）

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

#### __TypeKind 枚举

```
SCALAR | OBJECT | INTERFACE | UNION | ENUM | INPUT_OBJECT | LIST | NON_NULL
```

#### 各 kind 的字段返回规则

| Kind | 非 null 字段 | 说明 |
|------|-------------|------|
| SCALAR | `kind`, `name` | `specifiedByURL` 对自定义标量可返回 URL，否则 null |
| OBJECT | `kind`, `name`, `fields`, `interfaces` | `interfaces` 无则返回空集 |
| INTERFACE | `kind`, `name`, `fields`, `interfaces`, `possibleTypes` | `possibleTypes` 必须为 object 类型列表 |
| UNION | `kind`, `name`, `possibleTypes` | `possibleTypes` 必须为 object 类型列表 |
| ENUM | `kind`, `name`, `enumValues` | 至少一个枚举值，名称唯一 |
| INPUT_OBJECT | `kind`, `name`, `inputFields`, `isOneOf` | `isOneOf` 对 OneOf Input Object 返回 true |
| LIST | `kind`, `ofType` | `ofType` 返回任意类型 |
| NON_NULL | `kind`, `ofType` | `ofType` 返回除 Non-Null 外的任意类型 |

### __Field 类型（F-242）

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

### __InputValue 类型（F-243）

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

`defaultValue` 使用 GraphQL 语言编码的默认值，无默认值时返回 null。

### __EnumValue 类型（F-244）

```graphql
type __EnumValue {
  name: String!
  description: String
  isDeprecated: Boolean!
  deprecationReason: String
}
```

### __Directive 类型（F-245~F-247）

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

`__Directive` 表示服务支持的指令，包括内建指令和自定义指令。`isRepeatable` 返回 Boolean，指示指令是否可在单个位置重复使用。

### __DirectiveLocation 枚举（F-248）

```
QUERY | MUTATION | SUBSCRIPTION | FIELD
| FRAGMENT_DEFINITION | FRAGMENT_SPREAD | INLINE_FRAGMENT
| VARIABLE_DEFINITION
| SCHEMA | SCALAR | OBJECT | FIELD_DEFINITION | ARGUMENT_DEFINITION
| INTERFACE | UNION | ENUM | ENUM_VALUE
| INPUT_OBJECT | INPUT_FIELD_DEFINITION | DIRECTIVE_DEFINITION
```

前 8 个为可执行指令位置，后 12 个为类型系统指令位置。
