---
type: reference
title: "GraphQL 规范 Section 3：Type System"
description: "GraphQL 类型系统完整规范，涵盖 Schema 定义、六种命名类型、包装类型、指令系统及扩展机制。"
sources:
  - path: "external/libs/GraphQL/graphql-spec/spec/Section 3 -- Type System.md"
    facts: [F-094, F-095, F-096, F-097, F-098, F-099, F-100, F-101, F-102, F-103, F-104, F-105, F-106, F-107, F-108, F-109, F-110, F-111, F-112, F-113, F-114, F-115, F-116, F-117, F-118, F-119, F-120, F-121, F-122, F-123, F-124, F-125, F-126, F-127, F-128, F-129, F-130, F-131, F-132, F-133, F-134, F-135, F-136, F-137, F-138, F-139, F-140, F-141, F-142, F-143, F-144, F-145, F-146, F-147, F-148, F-149, F-150, F-151, F-152, F-153, F-154, F-155, F-156, F-157, F-158, F-159, F-160, F-161, F-162, F-163, F-164, F-165, F-166, F-167, F-168, F-169, F-170, F-171, F-172, F-173, F-174, F-175, F-176, F-177, F-178, F-179, F-180, F-181, F-182, F-183, F-184, F-185, F-186, F-187, F-188, F-189, F-190, F-191, F-192, F-193, F-194, F-195, F-196, F-197, F-198, F-199, F-200, F-201, F-202, F-203, F-204, F-205, F-206, F-207, F-208, F-209, F-210, F-211, F-212, F-213, F-214, F-215, F-216, F-217, F-218]
---

# GraphQL 规范 Section 3：Type System

## 信源概述

| 信源 | 类型 | 事实范围 | 职责 |
|------|------|----------|------|
| external/libs/GraphQL/graphql-spec/spec/Section 3 -- Type System.md | 规范文档 | F-094~F-218 | 定义 GraphQL 类型系统、Schema、所有类型种类与指令系统 |

## 关键事实登记

### 类型系统文档与扩展（F-094~F-097）

```
TypeSystemDocument : TypeSystemDefinition+
TypeSystemDefinition : SchemaDefinition | TypeDefinition | DirectiveDefinition
TypeSystemExtension : SchemaExtension | TypeExtension | DirectiveExtension
TypeSystemDefinitionOrExtension : TypeSystemDefinition | TypeSystemExtension
```

### Schema

#### Schema 定义（F-098~F-109）

```
SchemaDefinition :
  Description? schema Directives[Const]? { RootOperationTypeDefinition+ }
RootOperationTypeDefinition : OperationType : NamedType
```

Schema 规则：
- 所有类型必须具有唯一名称，不得与任何内建类型冲突
- 所有指令必须具有唯一名称
- 所有类型和指令名称不得以 `__` 开头
- `query` 根操作类型必须提供，且必须是 Object 类型
- `mutation` 和 `subscription` 根操作类型是可选的；若提供则必须是 Object 类型
- query、mutation、subscription 根类型若提供则必须互不相同
- 文档最多包含一个 `schema` 定义
- 默认根类型名分别为 `Query`、`Mutation`、`Subscription`
- 当每个根操作类型使用各自默认根类型名、无其他类型使用默认根类型名、且 schema 无描述时，可省略 schema 定义

#### Schema 扩展（F-110~F-111）

```
SchemaExtension :
  extend schema Directives[Const]? { RootOperationTypeDefinition+ }
  | extend schema Directives[Const]?
```

扩展要求 Schema 必须已定义；任何不可重复指令不得已应用于先前 Schema。

### 类型总览（F-112~F-117）

GraphQL 有六种命名类型定义和两种包装类型：

| 类别 | 类型 |
|------|------|
| 命名类型 | Scalar、Object、Interface、Union、Enum、InputObject |
| 包装类型 | List、Non-Null |

输入/输出类型规则：
- Scalar 和 Enum 可同时作为输入和输出类型
- Input Object 只能作为输入类型
- Object、Interface、Union 只能作为输出类型
- List 和 Non-Null 取决于被包装类型

### 标量类型（F-118~F-137）

```
ScalarTypeDefinition : Description? scalar Name Directives[Const]?
```

#### 内建标量（F-119~F-123）

内建标量类型为：**Int、Float、String、Boolean、ID**。

- 从 `__Schema` 内省返回类型集合时，必须包含所有被引用的内建标量；未被引用的不得包含
- 使用 IDL 表示 schema 时，必须省略所有内建标量
- 可定义自定义标量类型；自定义标量应通过 `@specifiedBy` 指令提供标量规范 URL
- 内建标量类型不得提供标量规范 URL

#### Int（F-124~F-126）

表示有符号 32 位数值非小数值。内部值小于 -2^31 或大于等于 2^31 时应引发 execution error。作为输入类型时，仅接受整数输入值。

#### Float（F-127~F-129）

表示 IEEE 754 规定的有符号双精度有限值。非有限浮点值（NaN 和 Infinity）不能强制转换为 Float。作为输入时接受整数和浮点输入值，整数通过添加空小数部分强制转换（`1` → `1.0`）。

#### String（F-130~F-131）

表示文本数据，即 Unicode 码位序列。作为输入类型时仅接受有效的 Unicode 字符串。

#### Boolean（F-132~F-133）

表示 `true` 或 `false`。作为输入仅接受布尔值。

#### ID（F-134~F-135）

表示唯一标识符；序列化方式与 String 相同，但必须始终序列化为 String。作为输入时接受任意字符串（如 `"4"`）或整数（如 `4`、`-4`）并强制转换；浮点值（如 `4.0`）必须引发 request error。

#### Scalar 扩展（F-136~F-137）

```
ScalarTypeExtension : extend scalar Name Directives[Const]
```

### 对象类型（F-138~F-155）

```
ObjectTypeDefinition :
  Description? type Name ImplementsInterfaces? Directives[Const]? FieldsDefinition?
FieldsDefinition : { FieldDefinition+ }
FieldDefinition : Description? Name ArgumentsDefinition? : Type Directives[Const]?
ImplementsInterfaces :
  ImplementsInterfaces & NamedType
  | implements &? NamedType
```

对象类型规则：
- 必须定义一个或多个字段
- 字段名必须唯一且不得以 `__` 开头
- 字段必须返回输出类型（IsOutputType 为 true）
- 字段可以是 Scalar、Enum、另一个 Object、Interface、Union，或其包装类型
- Object 类型不能作为有效输入
- 可声明实现一个或多个唯一接口；必须是其所实现所有接口的超集
- 字段排序按执行中遇到的顺序

#### 字段参数（F-149~F-152）

```
ArgumentsDefinition : ( InputValueDefinition+ )
InputValueDefinition : Description? Name : Type DefaultValue? Directives[Const]?
```

- 参数名称不得以 `__` 开头，在字段内必须唯一
- 参数类型必须是输入类型
- 若参数类型为 Non-Null 且未定义默认值，则不得应用 `@deprecated`

#### 字段弃用（F-153）

`@deprecated` 指令用于标记字段已弃用。

#### Object 扩展（F-154~F-155）

三种形式：带 FieldsDefinition、仅带 Directives、仅带 ImplementsInterfaces。

### 接口类型（F-156~F-163）

- 必须定义一个或多个字段，字段名唯一，返回输出类型
- Interface 可以实现其他接口；被实现接口所传递实现的接口也必须在实现类型或接口上定义
- Interface 定义不得包含循环引用，也不得实现自身
- Interface 不能作为有效输入
- 在接口类型上选择字段时，只能查询该接口上声明的字段

### 联合类型（F-164~F-171）

```
UnionTypeDefinition : Description? union Name Directives[Const]? UnionMemberTypes?
UnionMemberTypes :
  UnionMemberTypes | NamedType
  | = |? NamedType
```

- 必须包含一个或多个唯一成员类型
- 成员类型必须全部是 Object 基类型
- Union 不定义任何字段；除元字段 `__typename` 外，不使用类型精炼片段则不能查询任何字段
- Union 不能作为有效输入

### 枚举类型（F-172~F-178）

```
EnumTypeDefinition : Description? enum Name Directives[Const]? EnumValuesDefinition?
EnumValuesDefinition : { EnumValueDefinition+ }
EnumValueDefinition : Description? EnumValue Directives[Const]?
```

- 必须定义一个或多个唯一枚举值
- 枚举值可序列化为字符串（值的名称）；GraphQL 字符串字面量不得作为枚举输入接受

### 输入对象类型（F-179~F-191）

```
InputObjectTypeDefinition :
  Description? input Name Directives[Const]? InputFieldsDefinition?
InputFieldsDefinition : { InputValueDefinition+ }
```

- 必须定义一个或多个输入字段
- 输入字段名必须唯一且不得以 `__` 开头
- 输入字段类型必须是输入类型
- Input Object 不能作为 Object 或 Interface 字段的返回类型
- 循环引用中至少一个字段必须是 nullable 或 List 类型
- 显式提供 `null` 与未提供值在语义上不同

#### OneOf Input Objects（F-186~F-189）

OneOf Input Object 是 Input Object 的特殊变体：
- 恰好一个字段必须被设置且非 null，所有其他字段省略
- 由 `@oneOf` 指令标记
- 所有字段必须是 nullable，且不得有默认值
- 内省中 `__Type.isOneOf` 对其返回 true
- Input Object 类型扩展不得提供 `@oneOf` 指令

### 包装类型

#### List（F-192~F-194）

- 声明列表中每一项的类型（item type）
- 列表值序列化为有序列表
- 允许嵌套列表（如 `[[Int]]`）
- 非列表且非 null 值作为列表输入时，强制转换为大小为 1 的列表
- item type 为 nullable 时，单个 item 错误导致该位置为 null；为 non-null 时导致整个列表错误

#### Non-Null（F-195~F-199）

- 由尾随感叹号 `!` 表示
- 不得包装另一个 Non-Null 类型
- 返回 Non-Null 类型的字段被查询时永不返回 null
- Non-Null 输入类型是必需的：不接受 null 值，也不接受省略
- 若 Non-Null 类型的结果强制转换为 null，必须引发 execution error

### 指令系统（F-200~F-218）

#### 指令定义（F-200~F-203）

```
DirectiveDefinition :
  Description? directive @ Name ArgumentsDefinition? Directives[Const]? repeatable? on DirectiveLocations
DirectiveLocations : DirectiveLocation | DirectiveLocations | DirectiveLocation
```

**ExecutableDirectiveLocation**（8 个）：
QUERY、MUTATION、SUBSCRIPTION、FIELD、FRAGMENT_DEFINITION、FRAGMENT_SPREAD、INLINE_FRAGMENT、VARIABLE_DEFINITION

**TypeSystemDirectiveLocation**（12 个）：
SCHEMA、SCALAR、OBJECT、FIELD_DEFINITION、ARGUMENT_DEFINITION、INTERFACE、UNION、ENUM、ENUM_VALUE、INPUT_OBJECT、INPUT_FIELD_DEFINITION、DIRECTIVE_DEFINITION

#### 内建指令（F-204~F-212）

| 指令 | 定义 |
|------|------|
| `@skip` | `directive @skip(if: Boolean!) on FIELD \| FRAGMENT_SPREAD \| INLINE_FRAGMENT` |
| `@include` | `directive @include(if: Boolean!) on FIELD \| FRAGMENT_SPREAD \| INLINE_FRAGMENT` |
| `@deprecated` | `directive @deprecated(reason: String! = "No longer supported") on FIELD_DEFINITION \| ARGUMENT_DEFINITION \| INPUT_FIELD_DEFINITION \| ENUM_VALUE \| DIRECTIVE_DEFINITION` |
| `@specifiedBy` | `directive @specifiedBy(url: String!) on SCALAR` |
| `@oneOf` | `directive @oneOf on INPUT_OBJECT` |

`@skip` 和 `@include` 均无优先级；同时出现在同一字段或片段上时，仅当 `@skip` 条件为 false **且** `@include` 条件为 true 时才查询。

约束规则：
- `@deprecated` 不得出现在必需参数（non-null 且无默认值）或输入对象字段定义上
- `@specifiedBy` 不得出现在内建标量类型上
- 指令可通过 `repeatable` 关键字定义为可重复
- 指令定义必须包含至少一个 DirectiveLocation
- 指令不得直接或间接引用自身；名称不得以 `__` 开头
- 使用 IDL 时可省略内建指令；内省时必须返回所有指令

#### 指令扩展（F-217~F-218）

```
DirectiveExtension : extend directive @ Name Directives[Const]
```

扩展要求前序指令必须已定义；不可重复指令不得已应用；不得包含直接或间接引用前序指令的指令。
