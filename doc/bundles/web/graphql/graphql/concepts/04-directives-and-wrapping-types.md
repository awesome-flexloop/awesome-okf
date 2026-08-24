---
type: concept
title: "指令、包装类型与输入系统"
description: "GraphQL ListType 与 NonNullType 包装语法、指令系统（@skip/@include/@deprecated/@specifiedBy/@oneOf）、自定义指令 DirectiveDefinition、指令位置分类、输入强制转换规则以及变量定义与类型兼容性。"
sources:
  - resource: /references/spec-section-3-type-system.md
    facts: [F-195, F-196, F-197, F-198, F-199, F-200, F-201, F-202, F-203, F-204, F-205, F-206, F-207, F-208, F-209, F-210, F-211, F-212, F-213, F-214, F-215, F-216, F-217, F-218]
---

# 指令、包装类型与输入系统

GraphQL 类型系统除了六种命名类型外，还提供两种包装类型（Wrapping Types）——List 和 Non-Null，用于修饰其他类型的基数和可空性。指令系统（Directives）则为类型定义和查询执行提供了可扩展的元信息标注机制。本文还将覆盖输入强制转换（Input Coercion）和变量定义规则。

## Non-Null 类型（!）

Non-Null 类型由尾随感叹号 `!` 表示（F-195），用于声明一个值永不为 null。

```
NonNullType : NamedType ! | ListType !
```

### Non-Null 规则

关于 Non-Null 类型的关键规则（F-196~F-199）：

- **Non-Null 不得包装另一个 Non-Null 类型**——即不允许 `String!!` 这样的写法；
- 字段在选择集中始终可选，但返回 Non-Null 类型的字段被查询时**永不返回 null**；
- Non-Null 输入类型是**必需的**：不接受 null 值，也不接受省略；
- 若 Non-Null 类型的结果强制转换为 null，必须引发 execution error。

```graphql
type Example {
  nullableField: String
  nonNullField: String!
  nonNullList: [String!]!
}
```

上例中：
- `nullableField: String`：可为 null；
- `nonNullField: String!`：非空字符串，若解析结果为 null 则引发错误；
- `nonNullList: [String!]!`：非空列表，每个元素也是非空字符串。

> **重要**：Non-Null 不仅是类型约束，更是错误传播控制机制。当 Non-Null 字段解析失败时，null 会沿响应树向上冒泡。详见 [响应格式、错误冒泡与序列化](/concepts/07-response-and-errors.md)。

## List 类型（[]）

List 类型用方括号 `[]` 包裹另一个类型，表示该类型的有序集合（F-114）。

```
ListType : [ Type ]
```

List 可包装任意类型（包括另一个 List 或 Non-Null），也可被 Non-Null 包装：

```graphql
type Example {
  listOfStrings: [String]
  nonNullList: [String!]!
  listOfNonNull: [String!]
  nestedList: [[Int]]
}
```

各组合的语义：

| 类型语法 | 列表本身 | 列表元素 |
|---------|---------|---------|
| `[String]` | 可为 null | 可为 null |
| `[String!]` | 可为 null | 不可为 null |
| `[String]!` | 不可为 null | 可为 null |
| `[String!]!` | 不可为 null | 不可为 null |

List 类型声明列表中每一项的类型（item type），列表值序列化为有序列表，允许嵌套列表如 `[[Int]]`（F-192）。

### List 输入强制转换

非列表且非 null 值作为列表类型输入时，强制转换结果为大小为 1 的列表（F-193）。此规则可递归应用于嵌套列表。

### List 错误处理

List 的 item type 为 nullable 时，单个 item 的错误导致该位置为 null 并附加 execution error；item type 为 non-null 时，单个 item 错误导致整个列表 execution error（F-194）。这一规则与 Non-Null 错误冒泡机制紧密相关。

## 指令系统概述

指令（Directive）为 GraphQL 文档和类型系统提供了可扩展的标注机制。指令以 `@` 符号开头，后接名称和可选参数（F-088）。

```
Directive : @ Name Arguments?
Directives : Directive+
```

指令顺序是有意义的，不同顺序可能产生不同语义（F-089）。

### 内建指令

GraphQL 规范定义了五个内建指令（F-204）：

| 指令 | 用途 | 位置 |
|------|------|------|
| `@skip` | 条件跳过字段/片段 | FIELD, FRAGMENT_SPREAD, INLINE_FRAGMENT |
| `@include` | 条件包含字段/片段 | FIELD, FRAGMENT_SPREAD, INLINE_FRAGMENT |
| `@deprecated` | 标记弃用 | FIELD_DEFINITION, ARGUMENT_DEFINITION, INPUT_FIELD_DEFINITION, ENUM_VALUE, DIRECTIVE_DEFINITION |
| `@specifiedBy` | 标量规范 URL | SCALAR |
| `@oneOf` | 标记 OneOf 输入对象 | INPUT_OBJECT |

#### @skip 和 @include

`@skip` 和 `@include` 是执行时指令，用于条件性地包含或跳过选择（F-205、F-206）：

```graphql
directive @skip(if: Boolean!) on FIELD | FRAGMENT_SPREAD | INLINE_FRAGMENT
directive @include(if: Boolean!) on FIELD | FRAGMENT_SPREAD | INLINE_FRAGMENT
```

两者均无优先级；同时出现在同一字段或片段上时，仅当 `@skip` 条件为 **false** 且 `@include` 条件为 **true** 时才查询该字段（F-210）。

```graphql
query GetUser($withEmail: Boolean!) {
  user(id: "1") {
    name
    email @include(if: $withEmail)
    pending @skip(if: $withEmail)
  }
}
```

#### @deprecated

`@deprecated` 用于标记 schema 元素已弃用（F-207）：

```graphql
directive @deprecated(
  reason: String! = "No longer supported"
) on FIELD_DEFINITION | ARGUMENT_DEFINITION | INPUT_FIELD_DEFINITION | ENUM_VALUE | DIRECTIVE_DEFINITION
```

`@deprecated` 不得出现在必需参数（non-null 且无默认值）或输入对象字段定义上（F-211）。弃用原因通过 `reason` 参数提供，默认为 `"No longer supported"`。

```graphql
type User {
  id: ID!
  name: String!
  oldField: String @deprecated(reason: "Use `newField` instead.")
  newField: String!
}
```

#### @specifiedBy

`@specifiedBy` 为自定义标量类型提供规范文档 URL（F-208）：

```graphql
directive @specifiedBy(url: String!) on SCALAR
```

该指令不得出现在内建标量类型上（F-212）。

```graphql
scalar DateTime @specifiedBy(url: "https://scalars.graphql.org/andimarek/date-time")
```

#### @oneOf

`@oneOf` 标记输入对象为 OneOf 变体（F-209），详见 [复合类型](/concepts/03-composite-types.md) 中的 OneOf Input Objects 章节。

```graphql
directive @oneOf on INPUT_OBJECT
```

## 自定义指令（DirectiveDefinition）

除内建指令外，可通过 DirectiveDefinition 定义自定义指令（F-200）：

```
DirectiveDefinition :
  Description? directive @ Name ArgumentsDefinition? Directives[Const]? repeatable? on DirectiveLocations
DirectiveLocations : DirectiveLocation | DirectiveLocations | DirectiveLocation
```

### 指令定义规则

关于自定义指令的关键规则（F-213~F-216）：

- 指令可通过 `repeatable` 关键字定义为**可重复**——可在同一位置多次使用；
- 指令定义必须包含**至少一个** DirectiveLocation；
- 指令不得直接或间接引用自身；
- 指令名称不得以 `__` 开头；
- 参数名不得以 `__` 开头且必须唯一。

```graphql
"""
标记字段需要认证
"""
directive @auth(requires: Role = USER) repeatable on FIELD_DEFINITION

enum Role {
  ADMIN
  USER
  GUEST
}

type Query {
  adminData: String! @auth(requires: ADMIN)
  publicData: String!
}
```

使用 IDL 表示 schema 时可省略内建指令的定义；但内省时必须返回所有指令（包括内建指令）（F-216）。

### 指令位置（DirectiveLocation）

指令位置分为两类（F-202、F-203）：

**可执行指令位置（ExecutableDirectiveLocation）**——8 个，用于查询文档中：

| 位置 | 说明 |
|------|------|
| `QUERY` | 查询操作 |
| `MUTATION` | 变更操作 |
| `SUBSCRIPTION` | 订阅操作 |
| `FIELD` | 字段选择 |
| `FRAGMENT_DEFINITION` | 片段定义 |
| `FRAGMENT_SPREAD` | 片段展开 |
| `INLINE_FRAGMENT` | 内联片段 |
| `VARIABLE_DEFINITION` | 变量定义 |

**类型系统指令位置（TypeSystemDirectiveLocation）**——12 个，用于 schema 定义中：

| 位置 | 说明 |
|------|------|
| `SCHEMA` | schema 定义 |
| `SCALAR` | 标量类型 |
| `OBJECT` | 对象类型 |
| `FIELD_DEFINITION` | 字段定义 |
| `ARGUMENT_DEFINITION` | 参数定义 |
| `INTERFACE` | 接口类型 |
| `UNION` | 联合类型 |
| `ENUM` | 枚举类型 |
| `ENUM_VALUE` | 枚举值 |
| `INPUT_OBJECT` | 输入对象类型 |
| `INPUT_FIELD_DEFINITION` | 输入字段定义 |
| `DIRECTIVE_DEFINITION` | 指令定义 |

### 指令扩展

指令可通过 `extend directive` 语法扩展（F-217、F-218），用于向已定义的指令添加指令（元指令）。扩展要求前序指令必须已定义；不可重复指令不得重复应用；不得包含直接或间接引用前序指令的指令。

## 输入强制转换（Input Coercion）

输入强制转换是将外部输入值（来自查询字面量或变量）转换为类型系统内部值的过程。不同类型有不同的强制转换规则。

### 标量类型输入强制转换

各内建标量的输入规则：

- **Int**：仅接受整数输入值；含数字内容的字符串、浮点值等必须引发 request error；值超出 32 位有符号整数范围时引发 request error（F-126）；
- **Float**：接受整数和浮点输入值；整数通过添加空小数部分转换为 Float（如 `1` → `1.0`）；其他值引发 request error（F-129）；
- **String**：仅接受有效的 Unicode 字符串输入值（F-131）；
- **Boolean**：仅接受布尔输入值（F-133）；
- **ID**：接受任意字符串（如 `"4"`）或整数（如 `4`、`-4`）并强制转换为 ID；浮点输入值（如 `4.0`）必须引发 request error（F-135）。

### Enum 输入强制转换

枚举值以不加引号的名称表示。GraphQL 字符串字面量**不得**作为枚举输入接受，必须引发 request error（F-176）。

### List 输入强制转换

- 列表值按 item type 逐个强制转换；
- 非列表且非 null 值强制转换为大小为 1 的列表（F-193）；
- item type 为 nullable 时，单个 item 错误导致该位置为 null；item type 为 non-null 时，单个 item 错误导致整个列表错误（F-194）。

### Input Object 输入强制转换

- 字段值按字段类型逐个强制转换；
- 不得包含未定义字段名，否则 request error（F-184）；
- **显式提供 `null` 与未提供值语义不同**（F-185）：
  - 未提供值且有默认值时使用默认值；
  - 未提供值且无默认值时，nullable 字段为 null，non-null 字段引发错误；
  - 显式提供 `null` 时，即使有默认值也使用 null（non-null 字段引发错误）。
- 输入对象字段无序，语法顺序不影响语义（F-079）。

### Non-Null 输入强制转换

- Non-Null 输入类型不接受 null 值，也不接受省略（F-198）；
- 未提供值且有默认值时使用默认值；
- 值为 null 或无法强制转换时引发 request error。

### Null 值与缺失值

GraphQL 有两种表示值缺失的方式（F-074）：
1. **显式提供字面量 `null`**；
2. **隐式完全不提供值**。

这两种方式在 Input Object 中语义不同（F-185），在参数和变量处理中也有不同行为。

## 变量定义与类型

变量（Variable）以 `$` 符号开头，在操作顶部定义（F-080~F-084）：

```
Variable : $ Name
VariableDefinition : Description? Variable : Type DefaultValue? Directives[Const]?
DefaultValue : = Value[Const]
```

变量必须在操作顶部定义，在整个操作执行期间有效。片段中使用的变量必须在传递性消费该片段的任意顶层操作中声明（F-085）。

```graphql
query GetUser($userId: ID!, $withEmail: Boolean = false) {
  user(id: $userId) {
    name
    email @include(if: $withEmail)
  }
}
```

### 变量默认值

变量可通过 `=` 语法提供默认值（F-083），默认值必须是常量值（Value[Const]），不能引用其他变量。未提供变量值且存在默认值时，使用默认值（包括 null 默认值）。

### 变量类型兼容性

变量使用时必须通过 `IsVariableUsageAllowed` 检查（F-297~F-302），这是验证阶段的重要规则：

1. **Non-Null 位置检查**：当 locationType 为 non-null 位置且 variableType 为 nullable 时，变量或位置必须提供非 null 默认值，否则不兼容；
2. **OneOf Input Object 特殊规则**：位于 OneOf Input Object 字段位置上的变量必须是 non-nullable 类型（F-301）；
3. **类型兼容性递归检查**（AreTypesCompatible）：
   - non-null 对 non-null 解包后递归比较；
   - List 基数必须匹配且 item 类型递归兼容；
   - 最终要求命名类型相同。

nullable 变量在变量或位置提供默认值时可出现在 non-null 参数位置；但运行时仍提供 null 时，non-null 参数必须引发 execution error（F-302）。

### 变量强制转换

在执行阶段，`CoerceVariableValues` 算法按变量声明类型对传入的变量值进行输入强制转换（F-311~F-314）：

- 未提供值且有默认值时，对默认值按变量类型强制转换后使用；
- Non-Nullable 变量未提供值或值为 null 时引发 request error；
- 提供 null 值时记录 null；
- 提供非 null 值时按类型强制转换，不可转换则引发 request error。

变量值在 `CoerceVariableValues` 阶段完成强制转换后，字段参数中引用的变量值不再重复强制转换（F-355）。

## 相关概念

- [复合类型：对象、接口、联合与枚举](/concepts/03-composite-types.md) — 了解 Input Object 类型和 @oneOf 指令的使用
- [验证管线与规则体系](/concepts/05-validation.md) — 了解指令位置验证、变量类型兼容性验证
- [执行引擎：字段解析与值完成](/concepts/06-execution.md) — 了解 @skip/@include 在 CollectFields 中的求值、CoerceVariableValues 算法
- [响应格式、错误冒泡与序列化](/concepts/07-response-and-errors.md) — 深入理解 Non-Null 类型的错误冒泡机制（洞察4）
- [内省系统：GraphQL 的自描述机制](/concepts/08-introspection.md) — 了解指令如何通过 __Directive 内省暴露
