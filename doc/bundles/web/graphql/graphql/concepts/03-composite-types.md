---
type: concept
title: "复合类型：对象、接口、联合与枚举"
description: "深入 GraphQL 类型系统的复合类型：ObjectTypeDefinition 的字段/参数/接口实现、InterfaceTypeDefinition 的 implements 机制、UnionTypeDefinition 成员类型、EnumTypeDefinition 枚举值与指令、InputObjectTypeDefinition 输入对象、@oneOf 指令、类型扩展以及抽象类型的 resolveType 机制。"
sources:
  - resource: /references/spec-section-3-type-system.md
    facts: [F-138, F-139, F-140, F-141, F-142, F-143, F-144, F-145, F-146, F-147, F-148, F-149, F-150, F-151, F-152, F-153, F-154, F-155, F-156, F-157, F-158, F-159, F-160, F-161, F-162, F-163, F-164, F-165, F-166, F-167, F-168, F-169, F-170, F-171, F-172, F-173, F-174, F-175, F-176, F-177, F-178, F-179, F-180, F-181, F-182, F-183, F-184, F-185, F-186, F-187, F-188, F-189, F-190, F-191, F-192, F-193, F-194]
---

# 复合类型：对象、接口、联合与枚举

GraphQL 类型系统中，除标量（Scalar）外的命名类型统称为复合类型（Composite Types），包括对象（Object）、接口（Interface）、联合（Union）、枚举（Enum）和输入对象（Input Object）。这些类型构成了 GraphQL schema 的主体结构，定义了数据的形状、关系和约束。

## ObjectTypeDefinition（对象类型）

对象类型是 GraphQL 中最常用的复合类型，表示一个包含字段的具体数据结构。其定义有两种形式（F-138）：带字段定义的完整形式，以及不带字段的形式（lookahead 不等于 `{`）。

```
ObjectTypeDefinition :
  Description? type Name ImplementsInterfaces? Directives[Const]? FieldsDefinition?
  | Description? type Name ImplementsInterfaces? Directives[Const]?
FieldsDefinition : { FieldDefinition+ }
```

### 字段定义

字段定义（FieldDefinition）是对象类型的核心（F-141）：

```
FieldDefinition : Description? Name ArgumentsDefinition? : Type Directives[Const]?
```

每个字段包含名称、可选参数、返回类型和可选指令。关于字段的关键规则（F-142~F-148）：

- 对象类型必须定义**一个或多个**字段；
- 字段名必须唯一，且不得以 `__` 开头；
- 字段必须返回输出类型（IsOutputType 为 true），可以是 Scalar、Enum、另一个 Object、Interface、Union，或这五者之一的包装类型；
- 对象类型不能作为有效输入；
- 字段排序按执行中遇到的顺序，JSON 等无序映射格式应文本上保留该顺序。

```graphql
type User {
  id: ID!
  name: String!
  email: String!
  orders(status: OrderStatus, limit: Int = 10): [Order!]!
}
```

### 接口实现（ImplementsInterfaces）

对象类型可声明实现一个或多个接口（F-139、F-147）：

```
ImplementsInterfaces :
  ImplementsInterfaces & NamedType
  | implements &? NamedType
```

对象类型必须是其所实现所有接口的**超集**——即必须包含接口声明的所有字段（及对应参数），并可额外定义自有字段。实现的接口必须唯一。

```graphql
type Business implements Node & Timestamped {
  id: ID!
  createdAt: String!
  updatedAt: String!
  name: String!
}
```

### 字段参数与弃用

字段可接受参数，参数通过 ArgumentsDefinition 定义（F-149~F-152）。参数名在字段内必须唯一、不得以 `__` 开头，参数类型必须是输入类型。若参数类型为 Non-Null 且未定义默认值，则不得对该参数应用 `@deprecated` 指令（F-152）。

字段可通过 `@deprecated` 指令标记为已弃用（F-153），弃用字段仍可查询但会在工具中提示。

### 对象类型扩展

对象类型支持通过 `extend type` 语法扩展（F-154、F-155），有三种形式：

1. 带 FieldsDefinition（添加新字段）；
2. 仅带 Directives（添加指令）；
3. 仅带 ImplementsInterfaces（声明实现新接口）。

扩展字段名必须唯一且不得在先前 Object 类型上已定义；不可重复指令不得重复应用；提供的接口不得已被先前 Object 实现。

## InterfaceTypeDefinition（接口类型）

接口类型定义了一组字段契约，对象类型通过实现接口来承诺提供这些字段。接口定义同样有两种形式（F-156）：带字段定义和不带字段。

```
InterfaceTypeDefinition :
  Description? interface Name ImplementsInterfaces? Directives[Const]? FieldsDefinition?
  | Description? interface Name ImplementsInterfaces? Directives[Const]?
```

### 接口规则

关于接口的关键规则（F-157~F-161）：

- 接口类型必须定义一个或多个字段，字段名唯一，字段必须返回输出类型；
- **接口可以实现其他接口**——被实现接口所传递实现的接口也必须在实现类型或接口上定义；
- 接口定义不得包含循环引用，也不得实现自身；
- 接口不能作为有效输入；
- 在接口类型上选择字段时，只能查询该接口上声明的字段（具体实现者上的额外字段需通过类型精炼片段访问）。

```graphql
interface Node {
  id: ID!
}

interface Timestamped {
  createdAt: String!
  updatedAt: String!
}

type Product implements Node & Timestamped {
  id: ID!
  createdAt: String!
  updatedAt: String!
  name: String!
  price: Float!
}
```

### 接口扩展

接口类型可通过 `extend interface` 扩展（F-162、F-163），有三种形式（添加字段、添加指令、添加接口实现）。扩展字段名必须唯一且不得在先前 Interface 上定义。已实现先前 Interface 的 Object 或 Interface 必须也是扩展字段的超集。

### 抽象类型与 resolveType 机制

Interface 和 Union 统称为**抽象类型**（Abstract Types）。在执行时，当查询作用于抽象类型，GraphQL 需要确定运行时的具体 Object 类型。这一过程由 `ResolveAbstractType` 机制完成：执行引擎调用类型系统内部方法，根据抽象类型和实际对象值确定对应的 Object 类型（F-367）。

对于 Interface，可能类型是所有实现该接口的 Object 类型集合；对于 Union，可能类型是其成员类型集合。片段展开可能性验证和字段收集都依赖这一可能类型集合。

## UnionTypeDefinition（联合类型）

联合类型表示多个 Object 类型的"或"关系，不定义自己的字段。

```
UnionTypeDefinition :
  Description? union Name Directives[Const]? UnionMemberTypes?
UnionMemberTypes :
  UnionMemberTypes | NamedType
  | = |? NamedType
```

### 联合规则

关于联合类型的关键规则（F-164~F-171）：

- 联合类型必须包含一个或多个唯一成员类型；
- 成员类型必须全部是 **Object 基类型**——Scalar、Interface、Union 和包装类型不得作为 Union 成员；
- Union 不定义任何字段，除元字段 `__typename` 外，不使用类型精炼片段（inline fragment 或 named fragment）则不能查询任何字段；
- Union 不能作为有效输入。

```graphql
type Cat {
  name: String!
  meow: Boolean!
}

type Dog {
  name: String!
  bark: Boolean!
}

union Pet = Cat | Dog

type Query {
  pets: [Pet!]!
}
```

查询联合类型时必须使用片段：

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

### 联合扩展

联合类型可通过 `extend union` 扩展（F-170、F-171），有两种形式：带 UnionMemberTypes（添加成员）或仅带 Directives。扩展成员类型必须全部是 Object 基类型，必须唯一且不得已是先前 Union 的成员。

## EnumTypeDefinition（枚举类型）

枚举类型定义了一组固定的枚举值，是一种特殊的标量级别叶子类型。

```
EnumTypeDefinition :
  Description? enum Name Directives[Const]? EnumValuesDefinition?
  | Description? enum Name Directives[Const]?
EnumValuesDefinition : { EnumValueDefinition+ }
EnumValueDefinition : Description? EnumValue Directives[Const]?
```

### 枚举规则

关于枚举类型的关键规则（F-172~F-178）：

- 枚举类型必须定义一个或多个唯一枚举值；
- 枚举值可序列化为字符串（所表示值的名称）；
- GraphQL 字符串字面量**不得**作为枚举输入接受，必须引发 request error——枚举值以不加引号的名称表示（如 `PENDING`）。

```graphql
enum OrderStatus {
  "订单待处理"
  PENDING
  "订单已发货"
  SHIPPED
  "订单已送达"
  DELIVERED
  "订单已取消"
  CANCELLED
}
```

枚举值可附加指令（如 `@deprecated`）。规范建议枚举值全大写命名。枚举类型可通过 `extend enum` 扩展（F-177、F-178），支持添加新枚举值或仅添加指令，扩展值必须唯一且不得已是先前 Enum 的值。

## InputObjectTypeDefinition（输入对象类型）

输入对象类型用于定义复杂的输入结构，常用于字段参数和变量。与 Object 类型不同，Input Object 只能作为输入，不能作为字段返回类型。

```
InputObjectTypeDefinition :
  Description? input Name Directives[Const]? InputFieldsDefinition?
  | Description? input Name Directives[Const]?
InputFieldsDefinition : { InputValueDefinition+ }
```

### 输入对象规则

关于输入对象的关键规则（F-179~F-185）：

- 输入对象类型必须定义一个或多个输入字段；
- 输入字段名必须唯一且不得以 `__` 开头；
- 输入字段类型必须是输入类型；
- 输入对象类型**不能**作为 Object 或 Interface 字段的返回类型；
- 输入对象可引用其他 Input Object 作为字段类型；循环引用中至少一个字段必须是 nullable 或 List 类型，否则无效；
- 输入对象字段值可以是输入对象字面量或变量提供的无序映射；
- **不得包含未定义字段名**，否则引发 request error；
- 显式提供 `null` 与未提供值在语义上不同。

```graphql
input PlaceOrderInput {
  userId: ID!
  items: [PlaceOrderItemInput!]!
  note: String
  couponCode: String
}

input PlaceOrderItemInput {
  productId: ID!
  quantity: Int!
}

type Mutation {
  placeOrder(input: PlaceOrderInput!): OrderConfirmation!
}
```

### OneOf Input Objects（@oneOf 指令）

OneOf Input Object 是输入对象的特殊变体，用于表示"多选一"语义（F-186~F-189）：

- 由 `@oneOf` 指令标记；
- **恰好一个字段**必须被设置且非 null，所有其他字段省略；
- 所有字段必须是 **nullable**，且**不得有默认值**；
- 内省中 `__Type.isOneOf` 字段对 OneOf Input Object 返回 true，对其他 Input Object 返回 false；
- Input Object 类型扩展**不得**提供 `@oneOf` 指令（即不能将普通 Input Object 通过扩展变为 OneOf）。

```graphql
input SearchInput @oneOf {
  byEmail: String
  byUsername: String
  byId: ID
}
```

使用时必须恰好提供一个字段：

```graphql
query {
  findUser(input: { byEmail: "alice@example.com" }) {
    id
    name
  }
}
```

### 输入对象扩展

输入对象可通过 `extend input` 扩展（F-190、F-191），支持添加输入字段或仅添加指令。扩展字段名必须唯一且不得已是先前 Input Object 的字段。若原类型是 OneOf Input Object，扩展字段也必须 nullable 且无默认值。

## List 类型与错误处理

List 类型虽然在包装类型文档中详述，但与复合类型密切相关（F-192~F-194）：

- List 类型声明列表中每一项的类型（item type），列表值序列化为有序列表，允许嵌套列表（如 `[[Int]]`）；
- 若非列表且非 null 值作为列表类型输入，强制转换结果为大小为 1 的列表（可递归应用于嵌套列表）；
- **列表 item 错误处理**：List 的 item type 为 nullable 时，单个 item 的错误导致该位置为 null 并附加 execution error；item type 为 non-null 时，单个 item 错误导致整个列表 execution error。

## 类型扩展机制总览

GraphQL 的六种命名类型均支持扩展（Extend），允许在不修改原始定义的情况下增量添加内容（F-117）：

| 类型 | 扩展语法 | 可添加内容 |
|------|----------|-----------|
| Scalar | `extend scalar` | 指令 |
| Object | `extend type` | 字段、指令、接口实现 |
| Interface | `extend interface` | 字段、指令、接口实现 |
| Union | `extend union` | 成员类型、指令 |
| Enum | `extend enum` | 枚举值、指令 |
| Input Object | `extend input` | 输入字段、指令 |

所有扩展都要求被扩展的类型必须已定义，且不可重复指令不得重复应用。类型扩展是 schema 演进和模块化组合的重要机制。

## 输入类型与输出类型总结

复合类型在输入/输出维度上的划分（F-116）：

| 类型 | 可作为输入 | 可作为输出 |
|------|-----------|-----------|
| Scalar | ✅ | ✅ |
| Enum | ✅ | ✅ |
| Object | ❌ | ✅ |
| Interface | ❌ | ✅ |
| Union | ❌ | ✅ |
| Input Object | ✅ | ❌ |
| List | 取决于 item type | 取决于 item type |
| Non-Null | 取决于内部类型 | 取决于内部类型 |

这一划分决定了字段参数和变量只能使用输入类型，而字段返回类型只能使用输出类型。

## 相关概念

- [Schema 与类型系统入门](/concepts/02-schema-and-types.md) — 了解类型系统文档结构、SchemaDefinition 和标量类型基础
- [指令、包装类型与输入系统](/concepts/04-directives-and-wrapping-types.md) — 深入学习 List/Non-Null 包装类型、@deprecated/@oneOf 等指令以及输入强制转换
- [验证管线与规则体系](/concepts/05-validation.md) — 了解复合类型上的字段选择、片段展开等验证规则
- [执行引擎：字段解析与值完成](/concepts/06-execution.md) — 了解抽象类型的 ResolveAbstractType 和 CompleteValue 各分支处理
- [内省系统：GraphQL 的自描述机制](/concepts/08-introspection.md) — 了解复合类型如何通过 __Type 内省暴露
