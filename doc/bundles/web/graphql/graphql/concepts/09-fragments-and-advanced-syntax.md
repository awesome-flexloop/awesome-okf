---
type: concept
title: "片段、变量作用域与 Schema Coordinates"
description: "深入 GraphQL 片段（FragmentDefinition/FragmentSpread/InlineFragment）的类型条件与 spread 可能性规则，变量定义作用域与 IsVariableUsageAllowed 兼容性检查，以及 Schema Coordinates 自包含坐标语法。"
sources:
  - resource: /references/spec-section-2-language.md
    facts: [F-045, F-046, F-047, F-048, F-049, F-050, F-051, F-052, F-053, F-054, F-055, F-084, F-085, F-086, F-087, F-088, F-089, F-090, F-091, F-092, F-093]
---

# 片段、变量作用域与 Schema Coordinates

片段（Fragments）是 GraphQL 查询语言中实现复用与组合的核心机制。它允许将一组字段选择抽取为命名单元，在多个操作或选择集中重复使用。变量作用域规则决定了片段中引用的变量如何与顶层操作关联，而 Schema Coordinates 则提供了一种精确定位 schema 中任意元素的自包含语法。

## 参数与别名基础

在进入片段之前，先回顾与片段密切相关的参数（Arguments）和别名（Alias）语法。

### 参数

参数是传递给字段或指令的命名值（F-045）：

```graphql
Arguments[Const] ::= '(' Argument+ ')'
Argument        ::= Name ':' Value
```

参数可以按任意语法顺序提供，语义相同（F-046）。这意味着 `field(a: 1, b: 2)` 与 `field(b: 2, a: 1)` 完全等价。

### 别名

别名为字段的响应键指定替代名称（F-047）：

```graphql
Alias ::= Name ':'
```

别名在查询同一类型的多个字段实例时特别有用，例如：

```graphql
{
  firstUser: user(id: "1") { name }
  secondUser: user(id: "2") { name }
}
```

响应中会出现 `firstUser` 和 `secondUser` 两个键，而非两个 `user` 键冲突。

## 片段定义（FragmentDefinition）

片段定义是可复用的字段选择集合（F-049）：

```graphql
FragmentDefinition ::= Description? 'fragment' FragmentName TypeCondition Directives? SelectionSet
```

一个完整的片段定义包含五个部分：

1. **描述**（可选）：StringValue，用于文档说明；
2. **关键字** `fragment`；
3. **片段名**（FragmentName）：Name 但不能是 `on`（F-050）；
4. **类型条件**（TypeCondition）：`on` NamedType（F-052），声明片段适用的类型；
5. **指令**（可选）和**选择集**。

示例：

```graphql
fragment UserFields on User {
  id
  name
  email
}
```

### 类型条件的限制

片段不能指定在输入值（标量、枚举或输入对象）上，只能指定在对象类型（Object）、接口（Interface）和联合（Union）上（F-053）。这是因为片段的本质是对复合类型的字段选择进行复用，而标量和枚举是叶子类型，没有子选择集。

## 片段展开（FragmentSpread）

片段通过展开操作符（spread operator）`...` 消费（F-051）。命名片段展开的语法为（F-048）：

```graphql
FragmentSpread ::= '...' FragmentName Directives?
```

示例：

```graphql
query {
  user(id: "1") {
    ...UserFields
  }
}
```

片段展开后，其选择集被内联到展开位置。展开时，片段的类型条件必须与当前作用域类型兼容（详见"Spread 可能性规则"）。

### 指令在片段展开中的使用

片段展开可以携带指令，如 `@skip` 和 `@include`：

```graphql
...UserFields @include(if: $withUser)
```

`@skip` 和 `@include` 的有效位置包括 `FRAGMENT_SPREAD`，因此可以在片段展开上条件性地控制是否应用片段。

## 内联片段（InlineFragment）

内联片段是没有名称的片段，直接在选择集中定义（F-054）：

```graphql
InlineFragment ::= '...' TypeCondition? Directives? SelectionSet
```

内联片段主要用于两种场景：

### 1. 联合/接口类型的条件选择

当查询接口或联合类型时，不同实现类型可能有不同字段，需要通过内联片段按类型选择：

```graphql
query {
  search(term: "phone") {
    ... on Product {
      name
      price
    }
    ... on Category {
      name
      productCount
    }
  }
}
```

### 2. 省略类型条件

若内联片段省略 TypeCondition，则被视为与封闭上下文相同类型（F-055）。这种形式主要用于在内联片段上应用指令：

```graphql
... @skip(if: $debug) {
  internalField
}
```

### 片段定义中的指令

片段定义本身也可以携带指令。`@skip` 和 `@include` 的 `FRAGMENT_DEFINITION` 位置虽然不在它们的定义中，但自定义指令可以声明 `FRAGMENT_DEFINITION` 位置。片段展开和内联片段分别对应 `FRAGMENT_SPREAD` 和 `INLINE_FRAGMENT` 位置。

## Spread 可能性规则

片段能否在某个类型作用域中展开，取决于片段类型条件（fragmentType）与父类型（parentType）的可能类型集合是否有交集。验证规则 Fragment Spread Is Possible 要求两者的 `GetPossibleTypes` 交集不得为空（F-280）。

### GetPossibleTypes

`GetPossibleTypes(type)` 返回类型所有可能的具体对象类型集合（F-281）：

- **Object 类型**：返回包含自身的单元素集合；
- **Interface 类型**：返回实现该接口的所有 Object 类型集合；
- **Union 类型**：返回其所有成员 Object 类型集合。

### 四种组合情形

片段展开是否有效，取决于 fragmentType 和 parentType 的种类组合（F-282、F-283）：

| parentType | fragmentType | 有效条件 |
|---|---|---|
| Object | Object | 两者必须是同一类型 |
| Object | Interface/Union | Object 必须实现该接口或是该 Union 的成员 |
| Interface/Union | Object | Object 必须是该抽象类型的可能类型之一 |
| Interface/Union | Interface/Union | 两者可能类型集合的交集非空即可 |

此外，Interface 类型的片段可始终 spread 到它所实现的 Interface 作用域中（F-284）。

### 示例

```graphql
interface Node { id: ID! }
type User implements Node { id: ID!, name: String! }
type Product implements Node { id: ID!, price: Float! }
union SearchResult = User | Product

fragment NodeFields on Node { id }

query {
  user(id: "1") {
    ...NodeFields
  }
}
```

`NodeFields` 的 fragmentType 是 `Node`（Interface），parentType 是 `User`（Object）。`User` 实现了 `Node`，因此 `User` 在 `Node` 的可能类型集合中，spread 有效。

## 片段验证规则汇总

除了 spread 可能性，片段还需满足以下验证规则：

- **片段名唯一性**：文档中每个片段定义的名称必须唯一（F-274）；
- **目标类型存在**：片段和内联片段的目标类型必须在 schema 中定义（F-275）；
- **复合类型目标**：片段目标类型必须是 UNION、INTERFACE 或 OBJECT（F-276）；
- **片段必须被使用**：每个已定义片段必须至少被一个 spread 引用（F-277）；
- **展开目标已定义**：每个命名片段展开必须引用文档中已定义的片段（F-278）；
- **无环**：片段展开图不得形成环，包括自引用（F-279）。

## 变量定义与作用域

### 变量定义语法

变量（Variable）以 `$` 开头（F-080），变量定义在操作顶部（F-081、F-082）：

```graphql
Variable           ::= '$' Name
VariablesDefinition ::= '(' VariableDefinition+ ')'
VariableDefinition  ::= Description? Variable ':' Type DefaultValue? Directives[Const]?
DefaultValue        ::= '=' Value[Const]
```

示例：

```graphql
query GetUser($userId: ID!, $withEmail: Boolean = true) {
  user(id: $userId) {
    name
    email @include(if: $withEmail)
  }
}
```

### 作用域规则

变量必须在操作顶部定义，在整个操作执行期间内有效（F-084）。这意味着变量的作用域是整个操作，包括其传递性引用的所有片段。

片段中使用的变量必须在传递性消费该片段的任意顶层操作中声明（F-085）。"传递性"意味着如果操作 A 展开片段 B，B 又展开片段 C，那么 C 中使用的变量也必须在 A 中声明。

```graphql
fragment UserFields on User {
  name
  email @include(if: $withEmail)
}

query GetUser($userId: ID!, $withEmail: Boolean = true) {
  user(id: $userId) {
    ...UserFields
  }
}
```

`$withEmail` 在片段 `UserFields` 中使用，但必须在顶层 query 中声明。

### 变量验证规则

- **变量名唯一性**：每个操作中定义的变量名在该操作内唯一，不同操作可定义同名变量（F-293）；
- **输入类型**：变量类型必须是输入类型，Object/Union/Interface 不能用作变量类型（F-294）；
- **所有变量使用已定义**：操作及其传递性片段中使用的每个变量必须在操作变量列表中定义（F-295）；
- **所有变量已使用**：操作定义的每个变量必须在操作本身或其传递性片段中至少使用一次（F-296）。

## 变量使用允许规则（IsVariableUsageAllowed）

并非所有变量类型都能用于所有位置。`IsVariableUsageAllowed` 检查变量类型与位置类型的兼容性（F-297、F-298）。

### Non-Null 位置与 nullable 变量

当位置类型（locationType）为 non-null，而变量类型（variableType）为 nullable 时，变量或位置必须提供非 null 默认值，否则不允许（F-298）。

例如，参数 `id: ID!`（non-null 位置），若传入 `$id: ID`（nullable 变量），则要么变量有默认值（`$id: ID = "0"`），要么位置有默认值，否则验证失败。

### OneOf Input Object 特殊位置

当变量使用位于 OneOf Input Object 的字段中时，该位置被视为 non-null 位置（F-299），且变量本身必须是 non-nullable 类型（F-301）。

### 类型兼容性（AreTypesCompatible）

通过 non-null 检查后，使用 `AreTypesCompatible` 递归比较类型（F-300）：

1. 两者都解包 non-null 后递归比较；
2. List 的基数必须匹配，item 类型递归兼容；
3. 最终要求命名类型相同。

### 运行时行为

nullable 变量在变量或位置提供默认值时可出现在 non-null 参数位置；但运行时若仍提供 null 值，non-null 参数必须引发 execution error（F-302）。

## 类型引用

类型引用（Type References）在变量定义和字段定义中使用（F-086、F-087）：

```graphql
Type       ::= NamedType | ListType | NonNullType
NamedType  ::= Name
ListType   ::= '[' Type ']'
NonNullType ::= NamedType '!' | ListType '!'
```

类型引用支持任意嵌套，如 `[String!]!`（非空列表，每项为非空字符串）。

## 指令

指令（Directives）为 GraphQL 文档提供附加元数据和行为控制（F-088）：

```graphql
Directives[Const] ::= Directive+
Directive         ::= '@' Name Arguments[?Const]?
```

指令顺序是有意义的，不同顺序可能产生不同语义（F-089）。例如同时使用 `@skip` 和 `@include` 时，两者无优先级，仅当 `@skip(if: false)` **且** `@include(if: true)` 时字段才被查询。

## Schema Coordinates

Schema Coordinates 是一种精确定位 schema 中元素的自包含字符串语法（F-090、F-091）。它不包含在 GraphQL Document 中，而是用于工具、错误消息、IDE 等场景中引用 schema 元素。

### 五种坐标形式

| 坐标类型 | 语法 | 示例 | 引用目标 |
|---|---|---|---|
| TypeCoordinate | `Name` | `User` | 命名类型 |
| MemberCoordinate | `Name '.' Name` | `User.name` | 字段或枚举值 |
| ArgumentCoordinate | `Name '.' Name '(' Name ':' ')'` | `User.user(id:)` | 字段参数 |
| DirectiveCoordinate | `'@' Name` | `@deprecated` | 指令 |
| DirectiveArgumentCoordinate | `'@' Name '(' Name ':' ')'` | `@deprecated(reason:)` | 指令参数 |

### 语法约束

Schema Coordinate 是自包含语法，其字符序列不得包含 Whitespace 或其他 Ignored 词法元素（F-092）。例如 `User.name` 中不能有空格，`User.user(id:)` 中 `id:` 后也不能有空格。

### 可引用的 Schema 元素

schema element 可以是（F-093）：

- 命名类型（Named Type）
- 字段（Field）
- 输入字段（Input Field）
- 枚举值（Enum Value）
- 字段参数（Field Argument）
- 指令（Directive）
- 指令参数（Directive Argument）

元字段（如 `__typename`）和内省类型（如 `__Schema`）不是 schema element，不能通过 Schema Coordinate 引用。

### 使用场景

Schema Coordinates 在以下场景中广泛使用：

- **错误消息**：精确定位验证错误涉及的 schema 元素；
- **工具链**：代码生成、schema 比较、变更检测；
- **语义内省**：`__SearchResult.coordinate` 字段返回 schema 坐标字符串；
- **文档**：交叉引用 schema 中的类型和字段。

## 相关概念

- [查询语言基础：文档、操作与选择集](/concepts/01-query-language-basics.md) — 片段是选择集的复用单元，变量定义是操作的组成部分
- [复合类型：对象、接口、联合与枚举](/concepts/03-composite-types.md) — 片段的类型条件只能应用于复合类型（Object/Interface/Union）
- [指令、包装类型与输入系统](/concepts/04-directives-and-wrapping-types.md) — 指令可在片段定义、片段展开和内联片段上使用
- [验证管线与规则体系](/concepts/05-validation.md) — Fragment Spread Is Possible、IsVariableUsageAllowed 等验证规则
- [内省系统：GraphQL 的自描述机制](/concepts/08-introspection.md) — Schema Coordinates 与内省类型的关联
- [GraphQL 与 AI：MCP、语义内省与 Agent](/concepts/11-graphql-and-ai.md) — 语义内省 RFC 使用 Schema Coordinates 定位 schema 元素
