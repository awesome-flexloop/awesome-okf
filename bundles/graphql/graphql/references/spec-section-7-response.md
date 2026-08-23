---
type: reference
title: "GraphQL 规范 Section 7：Response 与 Appendix C 语法汇总"
description: "GraphQL 响应格式规范，涵盖执行结果、请求错误、响应路径、错误格式、序列化映射，以及 Appendix C 语法产生式汇总。"
sources:
  - path: "external/libs/GraphQL/graphql-spec/spec/Section 7 -- Response.md"
    facts: [F-376, F-377, F-378, F-379, F-380, F-381, F-382, F-383, F-384, F-385, F-386, F-387, F-388, F-389, F-390, F-391, F-392, F-393, F-394, F-395, F-396, F-397, F-398, F-399, F-400, F-401, F-402, F-403, F-404, F-405, F-406, F-407, F-408, F-409, F-410, F-411, F-412]
  - path: "external/libs/GraphQL/graphql-spec/spec/Appendix C -- Grammar Summary.md"
    facts: [F-413, F-414, F-415, F-416, F-417, F-418, F-419, F-420, F-421, F-422, F-423, F-424, F-425, F-426, F-427, F-428, F-429, F-430, F-431, F-432, F-433, F-434]
---

# GraphQL 规范 Section 7：Response 与 Appendix C

## 信源概述

| 信源 | 类型 | 事实范围 | 职责 |
|------|------|----------|------|
| external/libs/GraphQL/graphql-spec/spec/Section 7 -- Response.md | 规范文档 | F-376~F-412 | 定义 GraphQL 响应格式、错误结构与序列化规则 |
| external/libs/GraphQL/graphql-spec/spec/Appendix C -- Grammar Summary.md | 规范文档 | F-413~F-434 | 汇总 GraphQL 全部语法产生式 |

## 关键事实登记

### 响应格式（F-376~F-386）

GraphQL 服务收到请求必须返回格式良好的 response；response 描述成功执行的结果或请求期间引发的错误。

response 是以下三种之一：
1. **Execution result**：query/mutation 操作执行结果，或 subscription source stream 中每个事件发出的结果
2. **Response stream**：subscription 操作返回的 execution result 流
3. **Request error result**：一个或多个 request error 引发时返回，不产生响应数据

#### Execution Result

execution result 必须是 map，必须包含键为 `"data"` 的条目。

- 执行引发错误时，必须包含键为 `"errors"` 的条目，值为非空 execution error 列表
- 请求无错误完成时该条目不得出现
- 可包含键为 `"extensions"` 的条目

#### Request Error Result

request error result 必须是 map：
- 必须包含非空 `"errors"` 列表（至少包含一个说明为何无法返回数据的 request error）
- **不得包含 `"data"` 条目**
- 可包含 `"extensions"`

request error 可因信息缺失、语法错误、验证失败、强制转换失败或实现判定应阻止请求继续的任何原因引发。

### 响应位置与路径（F-387~F-390）

**Response position**：执行期间产生的响应数据中可唯一标识的位置，可以是 resultMap 中的直接条目，也可以是（可能嵌套的）List 值中的位置。

**Response path**：通过从响应根开始到关联 response position 结束的路径段列表唯一标识。

- 表示字段 response name 的路径段必须是字符串
- 表示列表索引的路径段必须是从 0 开始的整数
- 别名字段必须使用别名（因为表示响应中的路径而非请求中的路径）
- error result 上存在 response path 时，它标识引发错误的 response position

### Data（F-391~F-393）

- `"data"` 条目是请求操作执行的结果：query 为 query root operation type 的对象，mutation 为 mutation root operation type 的对象
- 响应数据是执行期间所有 response position 解析结果的累积
- 执行开始前引发错误时，response 必须是 request error result（无响应数据）
- 执行期间引发导致有效响应无法生成的错误时，`"data"` 条目应为 null

### Errors（F-394~F-406）

#### 错误类型对比

| 特性 | Request Error | Execution Error |
|------|--------------|-----------------|
| 发生时机 | 请求期间，通常在执行开始前 | 特定字段执行期间 |
| 原因 | 语法/验证错误、无法确定操作、变量值无效 | 参数强制转换失败、值解析内部错误、结果强制转换失败 |
| 数据 | 无 data 条目 | 部分响应数据 |
| 责任方 | 通常是客户端过错 | 通常是服务端过错 |
| 位置 | 无特定 response position | 必须发生在特定 response position |

#### 错误对象字段

每个错误必须包含：

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `message` | String | 是 | 面向开发者的字符串错误描述 |
| `locations` | List | 否 | 请求文档中的位置列表，每个位置含 `line` 和 `column`（从 1 开始） |
| `path` | List | 否 | 引发错误的 response position 路径，使客户端可识别 null 结果是真实值还是错误所致 |
| `extensions` | Map | 否 | 实现者添加附加信息，值必须是 map |

关键规则：
- execution error 在给定 response position 引发时，该 position 不得出现在响应 data 条目中（null 除外）
- 嵌套执行中止，兄弟执行继续以产生部分结果
- 发生错误的字段声明为 Non-Null 时，null 结果冒泡到下一个可为 null 的字段
- 错误的 path 应包含到引发错误的结果字段的完整路径，即使该字段不在响应中
- 服务不应在错误格式中提供除 message/locations/path/extensions 以外的条目

### Extensions（F-407~F-408）

- `"extensions"` 条目如果设置，其值必须是 map
- 保留给实现者按需扩展协议，对其内容无额外限制
- execution result 和 request error result map 不得包含上述条目以外的任何条目
- 客户端必须忽略非规范条目

### 序列化格式（F-409~F-412）

GraphQL 不要求特定序列化格式，但序列化格式必须至少支持四种原语：Map、List、String、Null。还应支持 Boolean、Int、Float、Enum Value。

#### JSON 序列化映射

| GraphQL 类型 | JSON 表示 |
|-------------|-----------|
| Map | Object |
| List | Array |
| Null | null |
| String | String |
| Boolean | true/false |
| Int | Number |
| Float | Number |
| Enum Value | String |

- 选择集求值结果是有序的，序列化 Map 应按 CollectFields 定义的字段请求顺序写入条目
- JSON 等文本有序格式应在文本上保持请求字段顺序

### Appendix C：语法汇总（F-413~F-434）

语法汇总分为五个部分：Source Text、Ignored Tokens、Lexical Tokens、Document Syntax、Schema Coordinate Syntax。

#### 词法部分

- **SourceCharacter**：任意 Unicode 标量值
- **Ignored**：UnicodeBOM、Whitespace、LineTerminator、Comment、Comma
- **Token**：Punctuator、Name、IntValue、FloatValue、StringValue
- **Punctuator**：`!` `$` `&` `(` `)` `...` `:` `=` `@` `[` `]` `{` `|` `}`

#### 文档语法

```
Document : Definition+
Definition : ExecutableDefinition | TypeSystemDefinitionOrExtension
ExecutableDocument : ExecutableDefinition+
ExecutableDefinition : OperationDefinition | FragmentDefinition

OperationDefinition :
  Description? OperationType Name? VariablesDefinition? Directives? SelectionSet
  | SelectionSet

OperationType : query | mutation | subscription

SelectionSet : { Selection+ }
Selection : Field | FragmentSpread | InlineFragment
Field : Alias? Name Arguments? Directives? SelectionSet?
Alias : Name :

FragmentSpread : ... FragmentName Directives?
InlineFragment : ... TypeCondition? Directives? SelectionSet
FragmentDefinition : Description? fragment FragmentName TypeCondition Directives? SelectionSet
```

#### 值语法

```
Value[Const] :
  Variable (非 Const 时)
  | IntValue | FloatValue | StringValue | BooleanValue | NullValue
  | EnumValue | ListValue | ObjectValue

EnumValue : Name (但不得为 true、false、null)
FragmentName : Name (但不得为 on)
BooleanValue : true | false
NullValue : null
```

#### 类型与变量语法

```
Type : NamedType | ListType | NonNullType
NamedType : Name
ListType : [ Type ]
NonNullType : NamedType ! | ListType !

VariableDefinition : Description? Variable : Type DefaultValue? Directives[Const]?
Variable : $ Name
DefaultValue : = Value[Const]
```

#### 类型系统定义语法

```
TypeSystemDefinition : SchemaDefinition | TypeDefinition | DirectiveDefinition
TypeDefinition :
  ScalarTypeDefinition | ObjectTypeDefinition | InterfaceTypeDefinition
  | UnionTypeDefinition | EnumTypeDefinition | InputObjectTypeDefinition

DirectiveDefinition :
  Description? directive @ Name ArgumentsDefinition? Directives[Const]? repeatable?
  on DirectiveLocations
```

#### 指令位置

- **ExecutableDirectiveLocation**（8 个）：QUERY、MUTATION、SUBSCRIPTION、FIELD、FRAGMENT_DEFINITION、FRAGMENT_SPREAD、INLINE_FRAGMENT、VARIABLE_DEFINITION
- **TypeSystemDirectiveLocation**（12 个）：SCHEMA、SCALAR、OBJECT、FIELD_DEFINITION、ARGUMENT_DEFINITION、INTERFACE、UNION、ENUM、ENUM_VALUE、INPUT_OBJECT、INPUT_FIELD_DEFINITION、DIRECTIVE_DEFINITION

#### Schema Coordinate 语法

```
TypeCoordinate : Name
MemberCoordinate : Name . Name
ArgumentCoordinate : Name . Name ( Name : )
DirectiveCoordinate : @ Name
DirectiveArgumentCoordinate : @ Name ( Name : )
```

Schema coordinate 不得包含 Ignored token。
