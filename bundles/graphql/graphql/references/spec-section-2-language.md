---
type: reference
title: "GraphQL 规范 Section 2：Language"
description: "GraphQL 查询语言的语法与词法规范，涵盖文档结构、操作、选择集、片段、变量、值类型、指令与 Schema Coordinates。"
sources:
  - path: "external/libs/GraphQL/graphql-spec/spec/Section 2 -- Language.md"
    facts: [F-011, F-012, F-013, F-014, F-015, F-016, F-017, F-018, F-019, F-020, F-021, F-022, F-023, F-024, F-025, F-026, F-027, F-028, F-029, F-030, F-031, F-032, F-033, F-034, F-035, F-036, F-037, F-038, F-039, F-040, F-041, F-042, F-043, F-044, F-045, F-046, F-047, F-048, F-049, F-050, F-051, F-052, F-053, F-054, F-055, F-056, F-057, F-058, F-059, F-060, F-061, F-062, F-063, F-064, F-065, F-066, F-067, F-068, F-069, F-070, F-071, F-072, F-073, F-074, F-075, F-076, F-077, F-078, F-079, F-080, F-081, F-082, F-083, F-084, F-085, F-086, F-087, F-088, F-089, F-090, F-091, F-092, F-093]
---

# GraphQL 规范 Section 2：Language

## 信源概述

| 信源 | 类型 | 事实范围 | 职责 |
|------|------|----------|------|
| external/libs/GraphQL/graphql-spec/spec/Section 2 -- Language.md | 规范文档 | F-011~F-093 | 定义 GraphQL 文档的词法、语法与所有语言构造 |

## 关键事实登记

### 文档与源文本

**信源**：Section 2 -- Language.md

#### 文档组成（F-011, F-031~F-037）

GraphQL 文档可包含操作（queries、mutations、subscriptions）以及 fragments（片段）。

语法产生式用冒号 `:` 区分，词法语法产生式用双冒号 `::` 区分。

```
Document : Definition+
Definition : ExecutableDefinition | TypeSystemDefinitionOrExtension
ExecutableDocument : ExecutableDefinition+
ExecutableDefinition : OperationDefinition | FragmentDefinition
```

文档可执行性规则：
- 只有作为 ExecutableDocument 且包含至少一个 OperationDefinition 时才可被 GraphQL 服务执行
- 包含 TypeSystemDefinitionOrExtension 的 Document 不得被执行
- 仅包含一个操作时，该操作可以是匿名的
- 包含多个操作时，每个操作必须命名，提交时必须提供要执行的操作名称
- 若唯一操作是无变量且无指令的 query，可使用省略 `query` 关键字和操作名的简写形式

#### Source Text（F-013~F-015）

GraphQL 文档的源文本必须是 SourceCharacter 序列，由 Token 和 Ignored 词法语法序列描述。

- SourceCharacter 是任意 Unicode 标量值，范围为 U+0000 到 U+D7FF 或 U+E000 到 U+10FFFF
- GraphQL 文档可仅以 ASCII 范围表达；非 ASCII Unicode 标量值可出现在 StringValue 和 Comment 中

### 词法分析

#### 空白与行终止符（F-016~F-017）

- **Whitespace**：Horizontal Tab（U+0009）和 Space（U+0020）
- **LineTerminator**：New Line（U+000A）、不后跟 New Line 的 Carriage Return（U+000D）、Carriage Return 后跟 New Line

#### 注释（F-018~F-019）

Comment 以 `#` 开头，后跟零个或多个 CommentChar（除 LineTerminator 外的任意 SourceCharacter）。Comment 属于 Ignored，可出现在任意 token 之后或 LineTerminator 之前，对语义无意义。

#### 逗号与忽略标记（F-020~F-023）

- Comma（`,`）在语法和语义上均无关紧要
- **Ignored** 包括：UnicodeBOM、Whitespace、LineTerminator、Comment、Comma
- UnicodeBOM（U+FEFF）可出现在任意词法 token 之前或之后

#### 词法 Token（F-021~F-024）

Token 包括：Punctuator、Name、IntValue、FloatValue、StringValue。

Punctuator 为以下之一：

```
! $ & ( ) ... : = @ [ ] { | }
```

#### Names（F-025~F-028）

```
Name : NameStart NameContinue*
NameStart : Letter | _
NameContinue : Letter | Digit | _
```

- Name 区分大小写；下划线是有意义的
- 类型系统中的任意 Name 不得以两个下划线 `__` 开头，除非它属于内省系统
- Name token 后不得紧跟 NameContinue，即 Name 始终是最长的有效序列

### 描述（F-029~F-030）

Description 是一个 StringValue，以 Markdown（CommonMark 规范）提供。可执行文档中的描述不得影响文档的执行、验证或响应；移除所有描述和注释不改变行为或结果。

### 操作（F-038~F-041）

```
OperationDefinition :
  Description? OperationType Name? VariablesDefinition? Directives? SelectionSet
  | SelectionSet

OperationType : query | mutation | subscription
```

三种操作类型：
- **query**：只读获取
- **mutation**：先写入后获取
- **subscription**：随时间事件序列获取数据的长连接请求

query 简写不允许带 Description。

### 选择集与字段（F-042~F-047）

```
SelectionSet : { Selection+ }
Selection : Field | FragmentSpread | InlineFragment
Field : Alias? Name Arguments? Directives? SelectionSet?
Alias : Name :
```

- 所有 GraphQL 操作必须将选择指定到叶子字段（leaf fields）
- Alias 允许在响应中重命名字段

### 参数（F-045~F-046）

```
Arguments[Const] : ( Argument+ )
Argument : Name : Value
```

参数可以任意语法顺序提供，语义相同。

### 片段（F-048~F-055）

```
FragmentSpread : ... FragmentName Directives?
FragmentDefinition : Description? fragment FragmentName TypeCondition Directives? SelectionSet
FragmentName : Name (but not "on")
TypeCondition : on NamedType
InlineFragment : ... TypeCondition? Directives? SelectionSet
```

- Fragment 使用展开操作符（`...`）消费
- Fragment 不能指定在输入值（标量、枚举或输入对象）上；可指定在对象类型、接口和联合上
- 若内联片段省略 TypeCondition，被视为与封闭上下文相同类型

### 输入值

#### 值类型总览（F-056）

```
Value[Const] :
  Variable (when not Const)
  | IntValue | FloatValue | StringValue | BooleanValue | NullValue
  | EnumValue | ListValue | ObjectValue
```

#### Int Value（F-057~F-060）

```
IntValue : IntegerPart (lookahead prevents Digit, ., NameStart)
IntegerPart : NegativeSign? 0 | NegativeSign? NonZeroDigit Digit*
NegativeSign : -
```

- 不得有前导 `0`

#### Float Value（F-061~F-063）

FloatValue 有三种形式：
- IntegerPart FractionalPart ExponentPart
- IntegerPart FractionalPart
- IntegerPart ExponentPart

```
FractionalPart : . Digit+
ExponentPart : ExponentIndicator Sign? Digit+
ExponentIndicator : e | E
Sign : + | -
```

#### String Value（F-065~F-072）

```
StringValue : "" | " StringCharacter+ " | BlockString
BlockString : """ BlockStringCharacter* """
```

- EscapedCharacter：`"` `\` `/` `b` `f` `n` `r` `t`
- EscapedUnicode：`{` HexDigit+ `}`（可变宽度）或四个 HexDigit（固定宽度）
- 转义序列仅在单引号字符串中有意义；在块字符串中转义序列是字面字符
- 空字符串 `""` 后不得紧跟另一个 `"`
- 块字符串值通过 BlockStringValue() 算法去除统一缩进和首尾空行

#### 其他值类型（F-064, F-073~F-079）

- **BooleanValue**：`true` 或 `false`
- **NullValue**：关键字 `null`；GraphQL 有两种表示值缺失的方式：显式 `null` 和隐式不提供值
- **EnumValue**：Name 但不能是 `true`、`false` 或 `null`；以不加引号的名称表示
- **ListValue**：`[ ]` 或 `[` Value+ `]`
- **ObjectValue**：`{ }` 或 `{` ObjectField+ `}`；ObjectField 为 Name `:` Value；字段无序

### 变量（F-080~F-085）

```
Variable : $ Name
VariablesDefinition : ( VariableDefinition+ )
VariableDefinition : Description? Variable : Type DefaultValue? Directives[Const]?
DefaultValue : = Value[Const]
```

- 变量必须在操作顶部定义，在整个操作执行期间内有效
- 片段中使用的变量必须在传递性消费该片段的任意顶层操作中声明

### 类型引用（F-086~F-087）

```
Type : NamedType | ListType | NonNullType
NamedType : Name
ListType : [ Type ]
NonNullType : NamedType ! | ListType !
```

### 指令（F-088~F-089）

```
Directives[Const] : Directive+
Directive : @ Name Arguments[?Const]?
```

指令顺序是有意义的，不同顺序可能产生不同语义。

### Schema Coordinates（F-090~F-093）

SchemaCoordinate 是自包含语法，不包含在 Document 中；其字符序列不得包含 Whitespace 或其他 Ignored 语法。

```
TypeCoordinate : Name
MemberCoordinate : Name . Name
ArgumentCoordinate : Name . Name ( Name : )
DirectiveCoordinate : @ Name
DirectiveArgumentCoordinate : @ Name ( Name : )
```

schema element 可以是命名类型、字段、输入字段、枚举值、字段参数、指令或指令参数；元字段和内省类型不是 schema element。
