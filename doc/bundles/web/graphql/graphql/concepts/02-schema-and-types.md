---
type: concept
title: "Schema 与类型系统入门"
description: "GraphQL SchemaDefinition 的根操作类型配置、六种命名类型与两种包装类型概览、内建标量类型规范、Enum/FieldDefinition/InputValueDefinition 基础语法，以及类型引用与 Description 机制。"
sources:
  - resource: /references/spec-section-3-type-system.md
    facts: [F-029, F-030, F-086, F-087, F-094, F-095, F-096, F-097, F-098, F-099, F-100, F-101, F-102, F-103, F-104, F-105, F-106, F-107, F-108, F-109, F-110, F-111, F-112, F-113, F-114, F-115, F-116, F-117, F-118, F-119, F-120, F-121, F-122, F-123, F-124, F-125, F-126, F-127, F-128, F-129, F-130, F-131, F-132, F-133, F-134, F-135, F-136, F-137, F-141, F-149, F-150, F-172, F-173, F-174, F-175, F-176]
---

# Schema 与类型系统入门

## 类型系统文档

类型系统文档（TypeSystemDocument）由一个或多个类型系统定义组成（F-094）。类型系统定义包括 SchemaDefinition、TypeDefinition 和 DirectiveDefinition 三类（F-095），另有对应的扩展机制（F-096、F-097）：

```
TypeSystemDocument : TypeSystemDefinition+
TypeSystemDefinition : SchemaDefinition | TypeDefinition | DirectiveDefinition
TypeSystemExtension : SchemaExtension | TypeExtension | DirectiveExtension
```

类型系统文档使用类型系统定义语言（IDL）编写，与可执行文档（包含查询操作）不同——包含类型系统定义的文档不得被 GraphQL 服务执行。

## SchemaDefinition（Schema 定义）

Schema 定义是整个 GraphQL 服务的入口，声明了三种根操作类型（F-098、F-099）：

```
SchemaDefinition :
  Description? schema Directives[Const]? { RootOperationTypeDefinition+ }
RootOperationTypeDefinition : OperationType : NamedType
```

一个典型的 schema 定义如下：

```graphql
schema {
  query: Query
  mutation: Mutation
  subscription: Subscription
}
```

### 根操作类型规则

关于三种根操作类型的规则（F-103~F-108）：

| 操作类型 | 是否必须 | 类型要求 | 默认根类型名 |
|----------|----------|----------|-------------|
| `query` | **必须提供** | Object 类型 | `Query` |
| `mutation` | 可选 | Object 类型；未提供则服务不支持 mutation | `Mutation` |
| `subscription` | 可选 | Object 类型；未提供则服务不支持 subscription | `Subscription` |

其他规则（F-100~F-107）：
- schema 中所有类型必须具有唯一名称，不得与任何内建类型（包括标量和内省类型）冲突；
- 所有指令必须具有唯一名称；
- 所有类型和指令名称不得以 `__` 开头；
- query、mutation、subscription 根类型若提供则必须互不相同；
- 文档最多包含一个 `schema` 定义。

### Schema 定义的省略

当每个根操作类型使用各自默认根类型名（`Query`、`Mutation`、`Subscription`）、无其他类型使用默认根类型名、且 schema 无描述时，可省略 schema 定义（F-109）。此时 GraphQL 实现自动推断根类型映射。

### Schema 扩展

Schema 可通过 `extend schema` 语法扩展（F-110），支持添加根操作类型定义或仅添加指令。扩展要求 Schema 必须已定义；任何不可重复指令不得已应用于先前 Schema（F-111）。

## TypeDefinition 分类概述

GraphQL 有六种命名类型定义和两种包装类型（F-112、F-113）：

| 类别 | 类型 | 说明 |
|------|------|------|
| 命名类型 | Scalar（标量） | 基本叶子值类型 |
| 命名类型 | Object（对象） | 包含字段的复合类型 |
| 命名类型 | Interface（接口） | 字段契约，可被 Object 实现 |
| 命名类型 | Union（联合） | 多个 Object 类型的联合 |
| 命名类型 | Enum（枚举） | 固定枚举值集合 |
| 命名类型 | InputObject（输入对象） | 用于参数和变量的复杂输入类型 |
| 包装类型 | List（列表） | 包装另一个类型，表示列表 |
| 包装类型 | Non-Null（非空） | 包装另一个类型，表示值永不为 null |

输入类型与输出类型的划分（F-116）：

- **可同时作为输入和输出**：Scalar 和 Enum；
- **只能作为输入类型**：Input Object；
- **只能作为输出类型**：Object、Interface、Union；
- **取决于被包装类型**：List 和 Non-Null。

## Description（描述）

类型系统中的描述使用 Description 语法编写（F-029）。Description 是一个 StringValue，以 Markdown（CommonMark 规范）提供。描述可附加在类型、字段、参数、枚举值等定义上，提供可读的文档。

在可执行文档中，描述不得影响文档的执行、验证或响应（F-030）。但在类型系统文档中，描述是自文档化能力的核心——内省系统可返回这些描述，支撑 GraphiQL 等工具的文档展示。

```graphql
"""
一个用户对象，包含系统中的用户信息。
"""
type User {
  """
  用户的唯一标识符
  """
  id: ID!
}
```

## 类型引用语法

在字段定义、变量定义等位置引用类型时，使用以下语法（F-086、F-087）：

```
Type : NamedType | ListType | NonNullType
NamedType : Name
ListType : [ Type ]
NonNullType : NamedType ! | ListType !
```

- **NamedType**（命名类型引用）：直接使用类型名，如 `String`、`User`；
- **ListType**（列表类型）：用方括号包裹另一个类型，如 `[Int]`、`[User]`；
- **NonNullType**（非空类型）：在命名类型或列表类型后加 `!`，如 `String!`、`[Int]!`、`[Int!]!`。

List 包装另一个类型，表示另一个类型的列表（F-114）。Non-Null 包装另一个类型，表示结果值永不为 null（F-115）。Non-Null 不得包装另一个 Non-Null 类型。

```graphql
type Example {
  nullableField: String
  nonNullField: String!
  listField: [Int]
  nonNullListField: [Int!]!
}
```

上例中：
- `nullableField`：可为 null 的字符串；
- `nonNullField`：非空字符串；
- `listField`：可为 null 的整数列表，列表元素也可为 null；
- `nonNullListField`：非空列表，且每个元素都是非空整数。

## FieldDefinition（字段定义）

字段定义是 Object 和 Interface 类型的核心组成部分（F-141）：

```
FieldDefinition : Description? Name ArgumentsDefinition? : Type Directives[Const]?
```

字段定义包含：
- 可选的 Description；
- 字段名（Name）；
- 可选的参数定义（ArgumentsDefinition）；
- 返回类型（Type）；
- 可选的指令。

字段必须返回输出类型（IsOutputType 为 true），可以是 Scalar、Enum、Object、Interface、Union 或它们的包装类型。

### InputValueDefinition（参数定义）

字段的参数通过 ArgumentsDefinition 定义，由一个或多个 InputValueDefinition 组成（F-149、F-150）：

```
ArgumentsDefinition : ( InputValueDefinition+ )
InputValueDefinition : Description? Name : Type DefaultValue? Directives[Const]?
```

每个参数包含名称、类型、可选的默认值和可选指令。参数类型必须是输入类型（F-151）。

```graphql
type Query {
  """
  按 ID 查找用户
  """
  user(id: ID!): User
}
```

上例中 `user` 字段接受一个非空 `ID` 类型参数 `id`，返回 `User` 类型。InputValueDefinition 也用于输入对象的字段定义和指令参数定义。

## 内建标量类型

标量类型（ScalarTypeDefinition）表示基本叶子值（F-118）：

```
ScalarTypeDefinition : Description? scalar Name Directives[Const]?
```

GraphQL 内建五种标量类型（F-119）：**Int、Float、String、Boolean、ID**。

使用类型系统定义语言（IDL）表示 schema 时，必须省略所有内建标量的显式定义（F-121）。从 `__Schema` 内省类型返回类型集合时，必须包含所有被引用的内建标量；未被引用的不得包含（F-120）。

### Int

Int 标量类型表示有符号 32 位数值非小数值（F-124）。

- 内部值小于 -2³¹ 或大于等于 2³¹ 时应引发 execution error（F-125）；
- 作为输入类型时，仅接受整数输入值；所有其他输入值（包括含数字内容的字符串）必须引发 request error；值超出范围时引发 request error（F-126）。

### Float

Float 标量类型表示 IEEE 754 规定的有符号双精度有限值（F-127）。

- 非有限浮点值（NaN 和 Infinity）不能强制转换为 Float，必须引发 execution error（F-128）；
- 作为输入类型时，接受整数和浮点输入值；整数值通过添加空小数部分强制转换为 Float（如 `1` → `1.0`）；其他值引发 request error（F-129）。

### String

String 标量类型表示文本数据，即 Unicode 码位序列（F-130）。作为输入类型时，仅接受有效的 Unicode 字符串输入值；其他值引发 request error（F-131）。

### Boolean

Boolean 标量类型表示 `true` 或 `false`（F-132）。作为输入类型时，仅接受布尔输入值；其他值引发 request error（F-133）。

### ID

ID 标量类型表示唯一标识符（F-134）：

- 其序列化方式与 String 相同，但**必须始终序列化为 String**；
- 作为输入类型时，接受任意字符串（如 `"4"`）或整数（如 `4`、`-4`）输入值并强制转换为 ID；浮点输入值（如 `4.0`）必须引发 request error（F-135）。

### 自定义标量

除内建标量外，可定义自定义标量类型（F-122）。自定义标量应通过 `@specifiedBy` 指令或 `specifiedByURL` 内省字段提供标量规范 URL，说明该标量的序列化和强制转换规则。内建标量类型不得提供标量规范 URL（F-123）。

### 标量扩展

标量类型可通过 `extend scalar` 语法扩展（F-136），用于向已定义的标量添加指令。扩展要求命名类型必须已定义且为 Scalar 类型；不可重复指令不得已应用（F-137）。

## EnumTypeDefinition（枚举类型）

枚举类型是六种命名类型之一，表示一组固定的枚举值。其定义语法为（F-172~F-174）：

```
EnumTypeDefinition :
  Description? enum Name Directives[Const]? EnumValuesDefinition?
EnumValuesDefinition : { EnumValueDefinition+ }
EnumValueDefinition : Description? EnumValue Directives[Const]?
```

枚举类型必须定义一个或多个唯一枚举值（F-175）。枚举值可序列化为字符串（所表示值的名称）；GraphQL 字符串字面量**不得**作为枚举输入接受，必须引发 request error（F-176）。

```graphql
enum OrderStatus {
  "订单已创建，等待支付"
  PENDING
  "订单已支付"
  PAID
  "订单已发货"
  SHIPPED
  "订单已完成"
  COMPLETED
}
```

枚举值以不加引号的名称表示（如 `PENDING`），在查询中使用时同样不加引号。枚举值规范建议全大写命名。

> 枚举类型的扩展机制和更详细的用法将在后续复合类型文档中深入介绍。

## 相关概念

- [GraphQL 概览与五大设计原则](/concepts/00-overview.md) — 了解类型系统如何体现强类型与自描述原则
- [查询语言基础：文档、操作与选择集](/concepts/01-query-language-basics.md) — 学习在类型系统上下文中编写查询
