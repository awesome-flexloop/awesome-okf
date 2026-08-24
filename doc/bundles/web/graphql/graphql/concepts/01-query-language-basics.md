---
type: concept
title: "查询语言基础：文档、操作与选择集"
description: "GraphQL 查询语言的词法规则、Document 结构、OperationDefinition、SelectionSet、Field、Arguments、Value 类型体系与 VariablesDefinition。"
sources:
  - resource: /references/spec-section-2-language.md
    facts: [F-011, F-012, F-013, F-014, F-015, F-016, F-017, F-018, F-019, F-020, F-021, F-022, F-023, F-024, F-025, F-026, F-027, F-028, F-029, F-030, F-031, F-032, F-033, F-034, F-035, F-036, F-037, F-038, F-039, F-040, F-041, F-042, F-043, F-044, F-045, F-046, F-047, F-056, F-057, F-058, F-059, F-060, F-061, F-062, F-063, F-064, F-065, F-066, F-067, F-068, F-069, F-070, F-071, F-072, F-073, F-074, F-075, F-076, F-077, F-078, F-079, F-080, F-081, F-082, F-083]
---

# 查询语言基础：文档、操作与选择集

## Document 结构

GraphQL 文档（Document）可包含操作（queries、mutations、subscriptions）以及片段（fragments）（F-011）。文档的语法产生式如下（F-031、F-032）：

```
Document : Definition+
Definition : ExecutableDefinition | TypeSystemDefinitionOrExtension
ExecutableDocument : ExecutableDefinition+
ExecutableDefinition : OperationDefinition | FragmentDefinition
```

文档只有在作为**可执行文档**（ExecutableDocument）且包含至少一个 OperationDefinition 时才可被 GraphQL 服务执行（F-033）。包含类型系统定义或扩展（TypeSystemDefinitionOrExtension）的文档不得被执行（F-034）。

关于操作命名的规则（F-035~F-037）：

- 若文档仅包含一个操作，该操作可以是**匿名**的；
- 若文档包含多个操作，每个操作必须**命名**，提交时必须提供要执行的操作名称；
- 若唯一操作是无变量且无指令的 query，可使用省略 `query` 关键字和操作名的**简写形式**。

```graphql
# 简写形式（唯一、无变量、无指令的 query）
{
  field
}

# 命名操作
query GetItem {
  field
}
```

## 词法规则

### 源文本与字符集

GraphQL 文档的源文本必须是 SourceCharacter 序列，由 Token 和 Ignored 词法语法序列描述（F-013）。SourceCharacter 是任意 Unicode 标量值，范围为 U+0000 到 U+D7FF 或 U+E000 到 U+10FFFF（F-014）。文档可仅以 ASCII 范围表达；非 ASCII Unicode 标量值可出现在 StringValue 和 Comment 中（F-015）。

语法产生式用冒号 `:` 区分，词法语法产生式用双冒号 `::` 区分（F-012）。

### 空白、行终止符与注释

**Whitespace**（空白）由 Horizontal Tab（U+0009）和 Space（U+0020）组成（F-016）。

**LineTerminator**（行终止符）包含（F-017）：
- New Line（U+000A）
- 不后跟 New Line 的 Carriage Return（U+000D）
- Carriage Return 后跟 New Line

**Comment**（注释）以 `#` 开头，后跟零个或多个 CommentChar；CommentChar 是除 LineTerminator 外的任意 SourceCharacter（F-018）。注释属于 Ignored，可出现在任意 token 之后或 LineTerminator 之前，对语义无意义（F-019）。

### 逗号与忽略标记

Comma（逗号）是 `,` 字符，在语法和语义上均无关紧要（F-020）。

**Ignored**（忽略标记）包括（F-022）：
- UnicodeBOM（U+FEFF，可出现在任意词法 token 之前或之后）（F-023）
- Whitespace
- LineTerminator
- Comment
- Comma

### 词法 Token 与标点

Token 包括：Punctuator、Name、IntValue、FloatValue、StringValue（F-021）。

Punctuator（标点符）为以下之一（F-024）：

```
! $ & ( ) ... : = @ [ ] { | }
```

### Name（名称）

Name 由 NameStart 后接零个或多个 NameContinue 组成（F-025）：

```
NameStart : Letter | _
NameContinue : Letter | Digit | _
```

名称规则（F-026~F-028）：
- Name **区分大小写**，下划线是有意义的；
- 类型系统中的任意 Name 不得以两个下划线 `__` 开头，除非它属于内省系统；
- Name token 后不得紧跟 NameContinue，即 Name 始终是最长的有效序列（贪婪匹配）。

## Description（描述）

Description 是一个 StringValue，以 Markdown（CommonMark 规范）提供（F-029）。可执行文档中的描述不得影响文档的执行、验证或响应；移除所有描述和注释不改变行为或结果（F-030）。

## OperationDefinition（操作定义）

操作定义有两种形式（F-038）：

```
OperationDefinition :
  Description? OperationType Name? VariablesDefinition? Directives? SelectionSet
  | SelectionSet
```

OperationType 为 `query`、`mutation`、`subscription` 之一（F-039），三者语义不同（F-040）：

| 操作类型 | 语义 |
|----------|------|
| `query` | 只读获取 |
| `mutation` | 先写入后获取 |
| `subscription` | 随时间事件序列获取数据的长连接请求 |

query 简写不允许带 Description（F-041）。当文档包含多个操作时，每个操作必须命名，执行时通过操作名称选择要执行的操作（F-036）。

## SelectionSet（选择集）

选择集是字段查询的核心结构（F-042）：

```
SelectionSet : { Selection+ }
Selection : Field | FragmentSpread | InlineFragment
```

选择集由一对花括号包裹，包含一个或多个选择项。选择项可以是：

- **Field**（字段）：直接请求一个字段；
- **FragmentSpread**（片段展开）：通过 `...FragmentName` 引用已定义的片段；
- **InlineFragment**（内联片段）：通过 `...` 直接定义内联的类型条件选择。

所有 GraphQL 操作必须将选择指定到**叶子字段**（leaf fields），即最终选择到标量或枚举类型，不能停留在复合类型上（F-044）。

## Field（字段）

字段的完整语法为（F-043）：

```
Field : Alias? Name Arguments? Directives? SelectionSet?
```

一个字段可以包含以下可选部分：

- **Alias**（别名）：重命名响应中的字段键；
- **Arguments**（参数）：向字段传递输入值；
- **Directives**（指令）：附加元信息或改变执行行为；
- **SelectionSet**（子选择集）：若字段返回复合类型，需嵌套选择其子字段。

### Alias（别名）

别名的语法为 `Name :`（F-047），允许在响应中使用不同的键名：

```graphql
{
  firstItem: field
  secondItem: field
}
```

上例中同一字段通过别名在响应中出现两次，键名分别为 `firstItem` 和 `secondItem`。

### Arguments（参数）

参数的语法为（F-045）：

```
Arguments[Const] : ( Argument+ )
Argument : Name : Value
```

参数以键值对形式提供，用圆括号包裹。参数可以任意语法顺序提供，语义相同（F-046）。

```graphql
{
  field(limit: 10, offset: 0)
}
```

### 嵌套选择集

当字段返回复合类型（对象、接口或联合）时，必须提供子选择集来指定需要获取的子字段，直到叶子字段（F-044）：

```graphql
{
  field {
    childField
    nestedField {
      leafField
    }
  }
}
```

这种嵌套结构正是 GraphQL 分层原则的语法体现——请求的形状与响应数据的形状一致。

## Value（值）类型体系

GraphQL 的输入值包括多种类型（F-056）：

```
Value[Const] :
  Variable (when not Const)
  | IntValue | FloatValue | StringValue | BooleanValue | NullValue
  | EnumValue | ListValue | ObjectValue
```

### IntValue（整数值）

IntValue 由 IntegerPart 构成，通过 lookahead 限制确保不后跟 Digit、`.` 或 NameStart（F-057）：

```
IntegerPart : NegativeSign? 0
            | NegativeSign? NonZeroDigit Digit*
```

- NegativeSign 是 `-`（F-059）；
- NonZeroDigit 是除 `0` 外的 Digit；
- IntValue **不得有前导 `0`**（F-060）。

合法示例：`0`、`42`、`-7`；非法示例：`01`、`007`。

### FloatValue（浮点值）

FloatValue 有三种形式（F-061）：
- IntegerPart FractionalPart ExponentPart
- IntegerPart FractionalPart
- IntegerPart ExponentPart

其中 FractionalPart 是 `.` 后接一个或多个 Digit；ExponentPart 是 ExponentIndicator Sign? Digit+（F-062）。ExponentIndicator 是 `e` 或 `E`；Sign 是 `+` 或 `-`（F-063）。

合法示例：`3.14`、`1.0e2`、`-0.5E-3`。

### BooleanValue（布尔值）

BooleanValue 是 `true` 或 `false`（F-064）。

### StringValue（字符串值）

StringValue 有三种形式（F-065）：
- `""`（空串）
- `"` StringCharacter+ `"`（单行字符串）
- BlockString（块字符串）

单行字符串中，StringCharacter 可以是除 `"`、`\`、LineTerminator 外的任意 SourceCharacter，也可以是转义序列（F-066）。EscapedCharacter 包括 `"`、`\`、`/`、`b`、`f`、`n`、`r`、`t`（F-067）。EscapedUnicode 支持可变宽度（`{` HexDigit+ `}`）和固定宽度（四个 HexDigit）两种形式（F-068）。

块字符串由三个双引号 `"""` 包裹（F-069）。转义序列仅在单引号字符串中有意义；在块字符串中转义序列是字面字符（F-070）。空字符串 `""` 后不得紧跟另一个 `"`，否则会被解释为块字符串的开始（F-071）。块字符串值通过 BlockStringValue() 算法去除统一缩进和首尾空行（F-072）。

```graphql
{
  field(name: "hello")
  field(description: """
    这是一个
    多行块字符串
  """)
}
```

### NullValue（空值）

NullValue 是关键字 `null`（F-073）。GraphQL 有两种表示值缺失的方式：显式提供字面量 `null`；隐式完全不提供值（F-074）。

### EnumValue（枚举值）

EnumValue 是 Name，但不能是 `true`、`false` 或 `null`（F-075）。枚举值以**不加引号**的名称表示（如 `MOBILE_WEB`），规范建议枚举值全大写（F-076）。

```graphql
{
  field(status: ACTIVE)
}
```

### ListValue（列表值）

ListValue 是空列表或包含一个或多个值的列表（F-077）：

```
ListValue[Const] : [ ] | [ Value[?Const]+ ]
```

```graphql
{
  field(ids: [1, 2, 3])
}
```

### ObjectValue（输入对象值）

ObjectValue 是空对象或包含一个或多个字段的对象（F-078）：

```
ObjectValue[Const] : { } | { ObjectField[?Const]+ }
ObjectField : Name : Value
```

输入对象字段无序，语法顺序不影响语义（F-079）。

```graphql
{
  field(input: { name: "test", count: 5 })
}
```

## VariablesDefinition（变量定义）

变量允许操作参数化，避免在查询字符串中硬编码值。

**Variable**（变量）以 `$` 后跟 Name 表示（F-080）：

```
Variable : $ Name
```

**VariablesDefinition** 是一个或多个变量定义的列表（F-081）：

```
VariablesDefinition : ( VariableDefinition+ )
VariableDefinition : Description? Variable : Type DefaultValue? Directives[Const]?
DefaultValue : = Value[Const]
```

变量定义指定变量名、类型和可选的默认值（F-082、F-083）：

```graphql
query GetItem($id: ID!, $limit: Int = 10) {
  field(id: $id, limit: $limit)
}
```

上例中：
- `$id` 是 `ID!` 类型（非空，必须提供）；
- `$limit` 是 `Int` 类型，默认值为 `10`。

变量类型引用的语法（NamedType、ListType、NonNullType）将在 [Schema 与类型系统入门](/concepts/02-schema-and-types.md) 中详细介绍。

## 相关概念

- [GraphQL 概览与五大设计原则](/concepts/00-overview.md) — 了解 GraphQL 的设计哲学与三阶段管线
- [Schema 与类型系统入门](/concepts/02-schema-and-types.md) — 学习类型系统如何定义查询所基于的契约
