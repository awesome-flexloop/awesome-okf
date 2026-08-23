---
type: concept
title: "响应格式、错误冒泡与序列化"
description: "GraphQL 响应的三种形态（execution result/response stream/request error）、data/errors/extensions 结构、request error 与 execution error 的区别、错误对象格式（message/locations/path/extensions）、Non-Null 错误冒泡 path 规则、序列化原语与 JSON 映射、字段顺序保持以及 Appendix C 语法产生式汇总。"
sources:
  - /references/spec-section-7-response.md
    facts: [F-376, F-377, F-378, F-379, F-380, F-381, F-382, F-383, F-384, F-385, F-386, F-387, F-388, F-389, F-390, F-391, F-392, F-393, F-394, F-395, F-396, F-397, F-398, F-399, F-400, F-401, F-402, F-403, F-404, F-405, F-406, F-407, F-408, F-409, F-410, F-411, F-412, F-413, F-414, F-415, F-416, F-417, F-418, F-419, F-420, F-421, F-422, F-423, F-424, F-425, F-426, F-427, F-428, F-429, F-430, F-431, F-432, F-433, F-434]
---

# 响应格式、错误冒泡与序列化

响应（Response）是 GraphQL 请求处理三阶段管线的最后阶段，负责将执行结果序列化为客户端可消费的格式。GraphQL 规范定义了响应的抽象结构、错误分类与传播规则、以及序列化格式的最小要求，但不绑定特定传输协议。

## 响应的三种形态

GraphQL 服务收到请求必须返回格式良好的 response（F-376）。response 是以下三种形态之一（F-378）：

| 形态 | 触发条件 | 包含 data |
|------|---------|----------|
| **execution result** | query/mutation 执行完成，或 subscription 事件触发 | ✅ 必须 |
| **response stream** | subscription 操作的持续事件流 | 每个事件一个 execution result |
| **request error result** | 请求在执行前失败 | ❌ 不得包含 |

当 execution error 被引发并替换为 null 时，response 可同时包含部分响应和错误列表（F-377）。

### Execution Result

query 或 mutation 操作且请求包含执行时返回 execution result；subscription source stream 中每个事件也发出一个 execution result（F-379）。

execution result 必须是 map，必须包含键为 `"data"` 的条目（F-380）。执行引发错误时，必须包含键为 `"errors"` 的条目，值为非空 execution error 列表；请求无错误完成时该条目**不得出现**（F-381）。execution result 可包含键为 `"extensions"` 的条目（F-382）。

成功响应示例：

```json
{
  "data": {
    "user": {
      "id": "1",
      "name": "Alice"
    }
  }
}
```

部分错误响应示例：

```json
{
  "data": {
    "user": {
      "id": "1",
      "name": null
    }
  },
  "errors": [
    {
      "message": "Failed to resolve name",
      "locations": [{ "line": 3, "column": 5 }],
      "path": ["user", "name"]
    }
  ]
}
```

### Response Stream

subscription 操作且请求包含执行时返回 response stream；response stream 必须是 execution result 的流（F-383）。source stream 中每个事件触发一次 GraphQL 执行，产生一个独立的 execution result。

### Request Error Result

一个或多个 request error 引发（导致请求在执行前失败）时返回 request error result，不产生响应数据（F-384）。

request error 可因以下原因引发（F-385）：
- 信息缺失；
- 语法错误；
- 验证失败；
- 强制转换失败；
- 实现判定应阻止请求继续的任何原因。

request error result 必须是 map（F-386）：
- 必须包含非空 `"errors"` 列表（至少包含一个说明为何无法返回数据的 request error）；
- **不得包含 `"data"` 条目**；
- 可包含 `"extensions"`。

```json
{
  "errors": [
    {
      "message": "Cannot query field \"nam\" on type \"User\". Did you mean \"name\"?",
      "locations": [{ "line": 2, "column": 3 }]
    }
  ]
}
```

## Request Error vs Execution Error

这两类错误的区分是理解 GraphQL 响应结构的关键（F-395~F-398）：

| 维度 | Request Error | Execution Error |
|------|--------------|-----------------|
| 发生时机 | 请求执行前 | 特定字段执行期间 |
| 原因 | 语法错误、验证失败、变量强制转换失败、无法确定操作 | 字段参数强制转换失败、值解析内部错误、结果强制转换失败 |
| 响应形态 | request error result | execution result（部分 data） |
| data 条目 | 不得包含 | 包含（可能为 null） |
| 责任归属 | 通常是客户端过错 | 通常是服务端过错 |
| 影响范围 | 整个请求不执行 | 仅影响出错字段及 Non-Null 冒泡链路 |

request error 引发时 response 必须是 request error result，不得包含 `"data"`，errors 必须包含该错误，请求执行应中止（F-396）。

## Response Position 与 Path

### Response Position

response position 是执行期间产生的响应数据中可唯一标识的位置（F-387）。它可以是：
- ExecuteSelectionSet 的 resultMap 中的直接条目（字段位置）；
- （可能嵌套的）List 值中的位置（列表元素位置）。

### Response Path

response path 通过从响应根开始到关联 response position 结束的路径段列表唯一标识 response position（F-388）。

路径段规则（F-389）：
- 表示字段 **response name** 的路径段必须是**字符串**；
- 表示列表索引的路径段必须是**从 0 开始的整数**；
- 别名字段必须使用**别名**（因为 path 表示响应中的路径而非请求中的路径）。

```graphql
query {
  user {
    friends: people {
      name
    }
  }
}
```

若 `friends[0].name` 出错，path 为 `["user", "friends", 0, "name"]`（使用别名 `friends` 而非字段名 `people`）。

error result 上存在 response path 时，它标识引发错误的 response position（F-390）。

## Data 条目

execution result 中的 `"data"` 条目是请求操作执行的结果（F-391）：
- query 为 query root operation type 的对象；
- mutation 为 mutation root operation type 的对象。

响应数据是执行期间所有 response position 解析结果的累积（F-392）。

关于 data 何时为 null（F-393）：
- 执行**开始前**引发错误时，response 必须是 request error result（无 data 键）；
- 执行**期间**引发导致有效响应无法生成的错误时，`"data"` 条目应为 **null**。

## Errors 条目

execution result 或 request error result 中的 `"errors"` 条目是请求期间引发的非空错误列表，每个错误是按错误结果格式描述的 map（F-394）。

### 错误对象格式

每个错误对象可包含以下字段（F-401~F-406）：

| 字段 | 必须 | 类型 | 说明 |
|------|------|------|------|
| `message` | ✅ | String | 面向开发者的字符串错误描述 |
| `locations` | 可选 | Array | 请求文档中关联位置列表，每个位置含 `line` 和 `column`（从 1 开始） |
| `path` | 条件必须 | Array | 引发错误的 response position 的 response path；execution error 必须包含 |
| `extensions` | 可选 | Object | 实现者自定义的附加信息，值必须是 map |

**locations**（F-402）：错误若可关联到请求 GraphQL 文档中特定位置，应包含此条目。每个位置是包含 `"line"` 和 `"column"` 键的 map，两者均为从 1 开始的正数。

**path**（F-403）：错误若可关联到 GraphQL 结果中特定字段，必须包含此条目。它使客户端可识别 null 结果是真实值还是 execution error 所致。

**extensions**（F-405）：GraphQL 服务可在错误中提供此条目，值必须是 map。保留给实现者添加附加信息，对其内容无额外限制。

服务不应在错误格式中提供除 message/locations/path/extensions 以外的条目，以避免与规范未来版本可能添加的条目冲突（F-406）。非规范条目不视为违规但不鼓励。

### Execution Error 的位置与传播

execution error 必须发生在特定 response position，可发生在任意 response position；通过错误响应的 `"path"` 条目指示（F-399）。

execution error 在给定 response position 引发时（F-400）：
- 该 position 不得出现在响应 `"data"` 条目中（null 除外）；
- errors 必须包含该错误；
- **嵌套执行中止，兄弟执行继续**以产生部分结果。

## Non-Null 错误冒泡

> **洞察4：Non-Null 错误冒泡——类型驱动的错误传播**。Non-Null 类型不仅是"字段不返回 null"的承诺，更是错误传播的控制机制。当 Non-Null 字段解析失败或强制转换为 null 时，null 沿响应树向上冒泡到第一个可为 null 的父位置，若整条路径均为 Non-Null 则整个 data 为 null。

### 冒泡规则

发生错误的字段声明为 Non-Null 时，null 结果冒泡到下一个可为 null 的字段（F-404）。错误的 path 应包含到引发错误的结果字段的**完整路径**，即使该字段不在响应中（因冒泡而被抹去）。

详细冒泡机制（详见 [执行引擎](/concepts/06-execution.md)）：

1. 叶子字段 execution error → 该 position 视为 null；
2. 若该 position 类型为 Non-Null → 错误传播到父 position；
3. 父 position 可为 null → 解析为 null，错误停止；
4. 父 position 也是 Non-Null → 继续向上传播；
5. List 包装 Non-Null item → 元素 null 导致整个 List position 为 null；
6. 从根到错误源全链 Non-Null → `data` 为 null。

### 冒泡示例

```graphql
type Query {
  user: User!
}

type User {
  id: ID!
  profile: Profile!
}

type Profile {
  avatar: String!
  bio: String
}
```

查询：

```graphql
query {
  user {
    id
    profile {
      avatar
      bio
    }
  }
}
```

若 `profile.avatar` 解析失败：
- `avatar: String!` 为 Non-Null → 冒泡到 `profile`；
- `profile: Profile!` 为 Non-Null → 冒泡到 `user`；
- `user: User!` 为 Non-Null → 冒泡到根；
- 全链 Non-Null → `data` 为 null。

响应：

```json
{
  "data": null,
  "errors": [
    {
      "message": "Failed to resolve avatar",
      "locations": [{ "line": 5, "column": 7 }],
      "path": ["user", "profile", "avatar"]
    }
  ]
}
```

注意 path 仍然指向 `["user", "profile", "avatar"]`，即使这些字段因冒泡都不在 data 中。

若 `profile.bio`（nullable `String`）解析失败：
- `bio: String` 可为 null → 该位置为 null，错误停止；
- `profile` 和 `user` 正常返回。

```json
{
  "data": {
    "user": {
      "id": "1",
      "profile": {
        "avatar": "url",
        "bio": null
      }
    }
  },
  "errors": [
    {
      "message": "Failed to resolve bio",
      "path": ["user", "profile", "bio"]
    }
  ]
}
```

### schema 设计权衡

Non-Null 越强，错误爆炸半径越大。一个深层叶子字段的错误可能因为 Non-Null 类型链而抹掉整个父对象，甚至导致全部数据为 null。这是 schema 设计中需要权衡的关键决策：

- 对**绝对必需**的数据使用 Non-Null（如 `id: ID!`）；
- 对**可能缺失**或**可能解析失败**的数据保持 nullable；
- 避免在对象层级过度使用 Non-Null，防止单点错误导致大面积数据丢失。

## Extensions 条目

execution result 或 request error result 中的 `"extensions"` 条目如果设置，其值必须是 map（F-407）。保留给实现者按需扩展协议，对其内容无额外限制。

extensions 可用于传递执行时间、追踪 ID、缓存信息、分页元数据等实现特定数据。

## Additional Entries

execution result 和 request error result map 不得包含上述条目（`data`、`errors`、`extensions`）以外的任何条目；客户端必须忽略上述以外的任何条目（F-408）。

## 序列化格式

GraphQL 不要求特定序列化格式，但序列化格式必须至少支持四种原语的表示（F-409）：

| 原语 | 说明 |
|------|------|
| **Map** | 键值对集合 |
| **List** | 有序值序列 |
| **String** | UTF-8 字符串 |
| **Null** | 空值 |

序列化格式还应支持以下类型（F-410）：

| 类型 | 说明 |
|------|------|
| Boolean | 布尔值 |
| Int | 整数 |
| Float | 浮点数 |
| Enum Value | 枚举值（如不直接支持，可用字符串或更简单原语替代） |

自定义标量可按格式支持的方式表示。

### JSON 序列化映射

GraphQL 类型到 JSON 的映射（F-411）：

| GraphQL 类型 | JSON 表示 |
|-------------|----------|
| Map | Object |
| List | Array |
| Null | `null` |
| String | String |
| Boolean | `true` / `false` |
| Int | Number |
| Float | Number |
| Enum Value | String（枚举值名称） |

### 字段顺序保持

选择集求值结果是有序的，序列化 Map 应按 CollectFields 定义的字段请求顺序写入条目（F-412）。JSON 等文本有序格式应在文本上保持请求字段顺序。

```graphql
query {
  user {
    name
    id
    email
  }
}
```

响应中字段顺序应为 `name`、`id`、`email`，与查询中的选择顺序一致。这一要求影响人类可读性和缓存键计算。

## Appendix C 语法产生式汇总

Appendix C 汇总了 GraphQL 语言的全部语法产生式，分为五个部分（F-413）：

1. **Source Text**：SourceCharacter 是任意 Unicode 标量值（F-414）；
2. **Ignored Tokens**：包括 UnicodeBOM、Whitespace、LineTerminator、Comment、Comma（F-415）；
3. **Lexical Tokens**：包括 Punctuator、Name、IntValue、FloatValue、StringValue（F-416）；
   - Punctuator 为：`!` `$` `&` `(` `)` `...` `:` `=` `@` `[` `]` `{` `|` `}`（F-417）；
4. **Document Syntax**：Document 由 Definition 组成（F-418~F-428）；
5. **Schema Coordinate Syntax**：Schema Coordinate 语法（F-433、F-434）。

### Document 语法核心产生式

```
Document : Definition+
Definition : ExecutableDefinition | TypeSystemDefinitionOrExtension
ExecutableDocument : ExecutableDefinition+
ExecutableDefinition : OperationDefinition | FragmentDefinition
```

- OperationDefinition 有两种形式：完整形式（Description? OperationType Name? VariablesDefinition? Directives? SelectionSet）和简写形式（SelectionSet）（F-420）；
- OperationType 为 `query`、`mutation`、`subscription` 之一（F-421）；
- SelectionSet 为 `{ Selection+ }`；Selection 为 Field、FragmentSpread 或 InlineFragment（F-422）；
- Field 为 Alias? Name Arguments? Directives? SelectionSet?；Alias 为 `Name :`（F-423）。

### 类型与变量语法

```
Type : NamedType | ListType | NonNullType
ListType : [ Type ]
NonNullType : NamedType ! | ListType !
```

- VariableDefinition 为 `Description? Variable : Type DefaultValue? Directives[Const]?`（F-428）；
- Variable 为 `$ Name`；DefaultValue 为 `= Value[Const]`。

### 类型系统定义语法

TypeSystemDefinition 包括 SchemaDefinition、TypeDefinition、DirectiveDefinition（F-429）。TypeDefinition 包括六种类型定义（F-429）：

```
TypeDefinition :
  ScalarTypeDefinition
  | ObjectTypeDefinition
  | InterfaceTypeDefinition
  | UnionTypeDefinition
  | EnumTypeDefinition
  | InputObjectTypeDefinition
```

DirectiveDefinition 形式（F-430）：

```
Description? directive @ Name ArgumentsDefinition? Directives[Const]? repeatable? on DirectiveLocations
```

### 指令位置枚举

- **ExecutableDirectiveLocation**：8 个值——QUERY、MUTATION、SUBSCRIPTION、FIELD、FRAGMENT_DEFINITION、FRAGMENT_SPREAD、INLINE_FRAGMENT、VARIABLE_DEFINITION（F-431）；
- **TypeSystemDirectiveLocation**：12 个值——SCHEMA、SCALAR、OBJECT、FIELD_DEFINITION、ARGUMENT_DEFINITION、INTERFACE、UNION、ENUM、ENUM_VALUE、INPUT_OBJECT、INPUT_FIELD_DEFINITION、DIRECTIVE_DEFINITION（F-432）。

### Schema Coordinate 语法

Schema Coordinate 包括（F-433）：
- TypeCoordinate：`Name`；
- MemberCoordinate：`Name.Name`；
- ArgumentCoordinate：`Name.Name(Name:)`；
- DirectiveCoordinate：`@Name`；
- DirectiveArgumentCoordinate：`@Name(Name:)`。

Schema coordinate 不得包含 Ignored token（F-434）。

## 相关概念

- [执行引擎：字段解析与值完成](/concepts/06-execution.md) — 了解 execution error 的产生机制和 Non-Null 冒泡算法（洞察4）
- [指令、包装类型与输入系统](/concepts/04-directives-and-wrapping-types.md) — Non-Null 类型语义是错误冒泡的类型基础
- [验证管线与规则体系](/concepts/05-validation.md) — request error 主要来源于验证阶段
- [复合类型：对象、接口、联合与枚举](/concepts/03-composite-types.md) — 了解类型定义语法和 List item 错误处理
- [内省系统：GraphQL 的自描述机制](/concepts/08-introspection.md) — 内省查询的响应格式遵循相同规则
