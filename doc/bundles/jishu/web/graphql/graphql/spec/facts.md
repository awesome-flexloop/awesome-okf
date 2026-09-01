---
type: spec
title: "R 阶段：事实清单"
---

# R 阶段：事实清单

> 来源：GraphQL Specification（Section 1–4）
> 采集规则：只记录规范原文所述事实，不含推断。

## Section 1 — Overview

F-001: [Overview] GraphQL 是一种查询语言，通过提供直观且灵活的语法与系统来描述客户端的数据需求与交互，以构建客户端应用。
F-002: [Overview] GraphQL 不是能够进行任意计算的编程语言。
F-003: [Overview] GraphQL 不强制要求实现它的应用服务使用特定的编程语言或存储系统。
F-004: [Overview] GraphQL 有五个设计原则：Product-centric（产品中心）、Hierarchical（分层）、Strong-typing（强类型）、Client-specified response（客户端指定响应）、Self-describing（自描述）。
F-005: [Overview-Product-centric] GraphQL 由视图和编写视图的前端工程师的需求驱动，从他们的思维方式和需求出发构建语言和运行时。
F-006: [Overview-Hierarchical] GraphQL 请求本身是分层结构的，请求的形状与其响应中的数据形状一致。
F-007: [Overview-Strong-typing] 每个 GraphQL 服务定义一个应用特定的类型系统；请求在该类型系统的上下文中执行；工具可以在执行前（开发时）确保操作在语法上正确且在该类型系统中有效。
F-008: [Overview-Client-specified response] GraphQL 服务通过类型系统发布客户端允许消费的能力，由客户端负责指定如何消费这些能力；请求以字段级粒度指定；响应恰好包含客户端所请求的内容，不多不少。
F-009: [Overview-Self-describing] GraphQL 服务的类型系统可通过 GraphQL 语言本身查询，其中包含可读的文档。
F-010: [Overview] 本规范描述语言及其语法、类型系统、用于查询类型系统的内省系统，以及执行和验证引擎及其算法。

## Section 2 — Language

### 文档与语法

F-011: [Language] 文档可包含操作（queries、mutations、subscriptions）以及 fragments（片段）。
F-012: [Language] 语法语法产生式用冒号 `:` 区分，词法语法产生式用双冒号 `::` 区分。
F-013: [Language] GraphQL 文档的源文本必须是 SourceCharacter 序列，由 Token 和 Ignored 词法语法序列描述；省略 Ignored 后的词法 token 序列必须由单个 Document 语法语法描述。
F-014: [Language-Source Text] SourceCharacter 是任意 Unicode 标量值，范围为 U+0000 到 U+D7FF 或 U+E000 到 U+10FFFF。
F-015: [Language-Source Text] GraphQL 文档可仅以 ASCII 范围表达；非 ASCII Unicode 标量值可出现在 StringValue 和 Comment 中。

### 词法分析

F-016: [Language-White Space] Whitespace 由 Horizontal Tab（U+0009）和 Space（U+0020）组成。
F-017: [Language-Line Terminators] LineTerminator 包含：New Line（U+000A）、不后跟 New Line 的 Carriage Return（U+000D）、Carriage Return 后跟 New Line。
F-018: [Language-Comments] Comment 以 `#` 开头，后跟零个或多个 CommentChar；CommentChar 是除 LineTerminator 外的任意 SourceCharacter。
F-019: [Language-Comments] Comment 属于 Ignored，可出现在任意 token 之后或 LineTerminator 之前，对语义无意义。
F-020: [Language-Insignificant Commas] Comma 是 `,` 字符，在语法和语义上均无关紧要。
F-021: [Language-Lexical Tokens] Token 包括：Punctuator、Name、IntValue、FloatValue、StringValue。
F-022: [Language-Ignored Tokens] Ignored 包括：UnicodeBOM、Whitespace、LineTerminator、Comment、Comma。
F-023: [Language-Ignored Tokens] UnicodeBOM 是 Byte Order Mark（U+FEFF），可出现在任意词法 token 之前或之后，属于 Ignored。
F-024: [Language-Punctuators] Punctuator 为以下之一：`!` `$` `&` `(` `)` `...` `:` `=` `@` `[` `]` `{` `|` `}`。
F-025: [Language-Names] Name 由 NameStart 后接零个或多个 NameContinue 组成；NameStart 是 Letter 或 `_`；NameContinue 是 Letter、Digit 或 `_`。
F-026: [Language-Names] GraphQL 中的 Name 区分大小写；下划线是有意义的。
F-027: [Language-Names] GraphQL 类型系统中的任意 Name 不得以两个下划线 `__` 开头，除非它属于内省系统。
F-028: [Language-Names] Name token 后不得紧跟 NameContinue，即 Name 始终是最长的有效序列。

### 描述

F-029: [Language-Descriptions] Description 是一个 StringValue；描述以 Markdown（CommonMark 规范）提供。
F-030: [Language-Descriptions] 可执行文档中的描述不得影响文档的执行、验证或响应；移除所有描述和注释不改变行为或结果。

### Document

F-031: [Language-Document] Document 是一个或多个 Definition；Definition 是 ExecutableDefinition 或 TypeSystemDefinitionOrExtension。
F-032: [Language-Document] ExecutableDocument 是一个或多个 ExecutableDefinition；ExecutableDefinition 是 OperationDefinition 或 FragmentDefinition。
F-033: [Language-Document] 文档只有在作为 ExecutableDocument 且包含至少一个 OperationDefinition 时才可被 GraphQL 服务执行。
F-034: [Language-Document] 包含 TypeSystemDefinitionOrExtension 的 Document 不得被执行。
F-035: [Language-Document] 若 Document 仅包含一个操作，该操作可以是匿名的。
F-036: [Language-Document] 若 Document 包含多个操作，每个操作必须命名；提交时必须提供要执行的操作名称。
F-037: [Language-Document] 若唯一操作是无变量且无指令的 query，可使用省略 `query` 关键字和操作名的简写形式。

### Operations

F-038: [Language-Operations] OperationDefinition 有两种形式：Description? OperationType Name? VariablesDefinition? Directives? SelectionSet；或 SelectionSet（简写）。
F-039: [Language-Operations] OperationType 为 `query`、`mutation`、`subscription` 之一。
F-040: [Language-Operations] query 是只读获取；mutation 是先写入后获取；subscription 是随时间事件序列获取数据的长连接请求。
F-041: [Language-Operations] query 简写不允许带 Description。

### Selection Sets

F-042: [Language-Selection Sets] SelectionSet 是 `{` 一个或多个 Selection `}`；Selection 是 Field、FragmentSpread 或 InlineFragment。

### Fields

F-043: [Language-Fields] Field 是：Alias? Name Arguments? Directives? SelectionSet?。
F-044: [Language-Fields] 所有 GraphQL 操作必须将选择指定到叶子字段（leaf fields）。

### Arguments

F-045: [Language-Arguments] Arguments[Const] 是 `(` 一个或多个 Argument `)`；Argument 是 Name `:` Value。
F-046: [Language-Arguments] 参数可以任意语法顺序提供，语义相同。

### Field Alias

F-047: [Language-Field Alias] Alias 是 Name `:`。

### Fragments

F-048: [Language-Fragments] FragmentSpread 是 `...` FragmentName Directives?。
F-049: [Language-Fragments] FragmentDefinition 是：Description? `fragment` FragmentName TypeCondition Directives? SelectionSet。
F-050: [Language-Fragments] FragmentName 是 Name 但不能是 `on`。
F-051: [Language-Fragments] Fragment 使用展开操作符（`...`）消费。
F-052: [Language-Fragments] TypeCondition 是 `on` NamedType。
F-053: [Language-Fragments] Fragment 不能指定在输入值（标量、枚举或输入对象）上；可指定在对象类型、接口和联合上。

### Inline Fragments

F-054: [Language-Inline Fragments] InlineFragment 是 `...` TypeCondition? Directives? SelectionSet。
F-055: [Language-Inline Fragments] 若省略 TypeCondition，内联片段被视为与封闭上下文相同类型。

### Input Values

F-056: [Language-Input Values] Value[Const] 包括：Variable（非常量时）、IntValue、FloatValue、StringValue、BooleanValue、NullValue、EnumValue、ListValue、ObjectValue。

#### Int Value

F-057: [Language-Int Value] IntValue 是 IntegerPart，lookahead 限制为不后跟 Digit、`.` 或 NameStart。
F-058: [Language-Int Value] IntegerPart 是：NegativeSign? `0`；或 NegativeSign? NonZeroDigit Digit*。
F-059: [Language-Int Value] NegativeSign 是 `-`；NonZeroDigit 是除 `0` 外的 Digit。
F-060: [Language-Int Value] IntValue 不得有前导 `0`。

#### Float Value

F-061: [Language-Float Value] FloatValue 有三种形式：IntegerPart FractionalPart ExponentPart；IntegerPart FractionalPart；IntegerPart ExponentPart；均带 lookahead 限制。
F-062: [Language-Float Value] FractionalPart 是 `.` 后接一个或多个 Digit；ExponentPart 是 ExponentIndicator Sign? Digit+。
F-063: [Language-Float Value] ExponentIndicator 是 `e` 或 `E`；Sign 是 `+` 或 `-`。

#### Boolean Value

F-064: [Language-Boolean Value] BooleanValue 是 `true` 或 `false`。

#### String Value

F-065: [Language-String Value] StringValue 有三种形式：`""`（空串）、`"` StringCharacter+ `"`、BlockString。
F-066: [Language-String Value] StringCharacter 是：除 `"`、`\`、LineTerminator 外的 SourceCharacter；`\u` EscapedUnicode；`\` EscapedCharacter。
F-067: [Language-String Value] EscapedCharacter 为以下之一：`"` `\` `/` `b` `f` `n` `r` `t`。
F-068: [Language-String Value] EscapedUnicode 有两种形式：`{` HexDigit+ `}`（可变宽度）；或四个 HexDigit（固定宽度）。
F-069: [Language-String Value] BlockString 是 `"""` 零个或多个 BlockStringCharacter `"""`。
F-070: [Language-String Value] 转义序列仅在单引号字符串中有意义；在块字符串中转义序列是字面字符。
F-071: [Language-String Value] 空字符串 `""` 后不得紧跟另一个 `"`，否则会被解释为块字符串的开始。
F-072: [Language-String Value] 块字符串值通过 BlockStringValue() 算法去除统一缩进和首尾空行。

#### Null Value

F-073: [Language-Null Value] NullValue 是关键字 `null`。
F-074: [Language-Null Value] GraphQL 有两种表示值缺失的方式：显式提供字面量 `null`；隐式完全不提供值。

#### Enum Value

F-075: [Language-Enum Value] EnumValue 是 Name，但不能是 `true`、`false` 或 `null`。
F-076: [Language-Enum Value] 枚举值以不加引号的名称表示（如 `MOBILE_WEB`）；规范建议枚举值全大写。

#### List Value

F-077: [Language-List Value] ListValue[Const] 是 `[ ]` 或 `[` Value[?Const]+ `]`。

#### Input Object Values

F-078: [Language-Input Object Values] ObjectValue[Const] 是 `{ }` 或 `{` ObjectField[?Const]+ `}`；ObjectField 是 Name `:` Value。
F-079: [Language-Input Object Values] 输入对象字段无序，语法顺序不影响语义。

### Variables

F-080: [Language-Variables] Variable 是 `$` Name。
F-081: [Language-Variables] VariablesDefinition 是 `(` VariableDefinition+ `)`。
F-082: [Language-Variables] VariableDefinition 是：Description? Variable `:` Type DefaultValue? Directives[Const]?。
F-083: [Language-Variables] DefaultValue 是 `=` Value[Const]。
F-084: [Language-Variables] 变量必须在操作顶部定义，在整个操作执行期间内有效。
F-085: [Language-Variables] 片段中使用的变量必须在传递性消费该片段的任意顶层操作中声明。

### Type References

F-086: [Language-Type References] Type 是 NamedType、ListType 或 NonNullType。
F-087: [Language-Type References] NamedType 是 Name；ListType 是 `[` Type `]`；NonNullType 是 NamedType `!` 或 ListType `!`。

### Directives

F-088: [Language-Directives] Directives[Const] 是一个或多个 Directive；Directive 是 `@` Name Arguments[?Const]?。
F-089: [Language-Directives] 指令顺序是有意义的，不同顺序可能产生不同语义。

### Schema Coordinates

F-090: [Language-Schema Coordinates] SchemaCoordinate 包括：TypeCoordinate、MemberCoordinate、ArgumentCoordinate、DirectiveCoordinate、DirectiveArgumentCoordinate。
F-091: [Language-Schema Coordinates] TypeCoordinate 是 Name；MemberCoordinate 是 Name `.` Name；ArgumentCoordinate 是 Name `.` Name `(` Name `:` `)`；DirectiveCoordinate 是 `@` Name；DirectiveArgumentCoordinate 是 `@` Name `(` Name `:` `)`。
F-092: [Language-Schema Coordinates] SchemaCoordinate 是自包含语法，不包含在 Document 中；其字符序列不得包含 Whitespace 或其他 Ignored 语法。
F-093: [Language-Schema Coordinates] schema element 可以是命名类型、字段、输入字段、枚举值、字段参数、指令或指令参数；元字段和内省类型不是 schema element。

## Section 3 — Type System

### 类型系统文档与扩展

F-094: [Type System] TypeSystemDocument 是一个或多个 TypeSystemDefinition。
F-095: [Type System] TypeSystemDefinition 是 SchemaDefinition、TypeDefinition 或 DirectiveDefinition。
F-096: [Type System] TypeSystemExtension 是 SchemaExtension、TypeExtension 或 DirectiveExtension。
F-097: [Type System] TypeSystemDefinitionOrExtension 是 TypeSystemDefinition 或 TypeSystemExtension。

### Schema

F-098: [Type System-Schema] SchemaDefinition 是：Description? `schema` Directives[Const]? `{` RootOperationTypeDefinition+ `}`。
F-099: [Type System-Schema] RootOperationTypeDefinition 是 OperationType `:` NamedType。
F-100: [Type System-Schema] schema 中所有类型必须具有唯一名称，不得与任何内建类型（包括标量和内省类型）冲突。
F-101: [Type System-Schema] schema 中所有指令必须具有唯一名称。
F-102: [Type System-Schema] schema 中定义的所有类型和指令名称不得以 `__` 开头。
F-103: [Type System-Schema] `query` 根操作类型必须提供，且必须是 Object 类型。
F-104: [Type System-Schema] `mutation` 根操作类型是可选的；若提供则必须是 Object 类型；未提供则服务不支持 mutation。
F-105: [Type System-Schema] `subscription` 根操作类型是可选的；若提供则必须是 Object 类型；未提供则服务不支持 subscription。
F-106: [Type System-Schema] query、mutation、subscription 根类型若提供则必须互不相同。
F-107: [Type System-Schema] 类型系统定义语言中文档最多包含一个 `schema` 定义。
F-108: [Type System-Schema] 默认根类型名分别为 `Query`、`Mutation`、`Subscription`。
F-109: [Type System-Schema] 当每个根操作类型使用各自默认根类型名、无其他类型使用默认根类型名、且 schema 无描述时，可省略 schema 定义。

### Schema Extension

F-110: [Type System-Schema Extension] SchemaExtension 有两种形式：`extend schema` Directives[Const]? `{` RootOperationTypeDefinition+ `}`；`extend schema` Directives[Const]?（无大括号，lookahead != `{`）。
F-111: [Type System-Schema Extension] Schema 扩展要求 Schema 必须已定义；任何不可重复指令不得已应用于先前 Schema。

### Types

F-112: [Type System-Types] TypeDefinition 包括：ScalarTypeDefinition、ObjectTypeDefinition、InterfaceTypeDefinition、UnionTypeDefinition、EnumTypeDefinition、InputObjectTypeDefinition。
F-113: [Type System-Types] GraphQL 有六种命名类型定义和两种包装类型（List 和 Non-Null）。
F-114: [Type System-Wrapping Types] List 包装另一个类型，表示另一个类型的列表。
F-115: [Type System-Wrapping Types] Non-Null 包装另一个类型，表示结果值永不为 null。
F-116: [Type System-Input and Output Types] Scalar 和 Enum 可同时作为输入和输出类型；Input Object 只能作为输入类型；Object、Interface、Union 只能作为输出类型；List 和 Non-Null 取决于被包装类型。
F-117: [Type System-Type Extensions] TypeExtension 包括：ScalarTypeExtension、ObjectTypeExtension、InterfaceTypeExtension、UnionTypeExtension、EnumTypeExtension、InputObjectTypeExtension。

### Scalars

F-118: [Type System-Scalars] ScalarTypeDefinition 是：Description? `scalar` Name Directives[Const]?。
F-119: [Type System-Scalars] 内建标量类型为：Int、Float、String、Boolean、ID。
F-120: [Type System-Scalars] 从 `__Schema` 内省类型返回类型集合时，必须包含所有被引用的内建标量；未被引用的内建标量不得包含。
F-121: [Type System-Scalars] 使用类型系统定义语言表示 schema 时，必须省略所有内建标量。
F-122: [Type System-Scalars] 可定义自定义标量类型；自定义标量应通过 `@specifiedBy` 指令或 `specifiedByURL` 内省字段提供标量规范 URL。
F-123: [Type System-Scalars] 内建标量类型不得提供标量规范 URL。

#### Int

F-124: [Type System-Int] Int 标量类型表示有符号 32 位数值非小数值。
F-125: [Type System-Int] Int 内部值小于 -2^31 或大于等于 2^31 时应引发 execution error。
F-126: [Type System-Int] 作为输入类型时，仅接受整数输入值；所有其他输入值（包括含数字内容的字符串）必须引发 request error；值小于 -2^31 或大于等于 2^31 时引发 request error。

#### Float

F-127: [Type System-Float] Float 标量类型表示 IEEE 754 规定的有符号双精度有限值。
F-128: [Type System-Float] 非有限浮点值（NaN 和 Infinity）不能强制转换为 Float，必须引发 execution error。
F-129: [Type System-Float] 作为输入类型时，接受整数和浮点输入值；整数值通过添加空小数部分强制转换为 Float（如 `1` → `1.0`）；其他值引发 request error。

#### String

F-130: [Type System-String] String 标量类型表示文本数据，即 Unicode 码位序列。
F-131: [Type System-String] 作为输入类型时，仅接受有效的 Unicode 字符串输入值；其他值引发 request error。

#### Boolean

F-132: [Type System-Boolean] Boolean 标量类型表示 `true` 或 `false`。
F-133: [Type System-Boolean] 作为输入类型时，仅接受布尔输入值；其他值引发 request error。

#### ID

F-134: [Type System-ID] ID 标量类型表示唯一标识符；其序列化方式与 String 相同，但必须始终序列化为 String。
F-135: [Type System-ID] 作为输入类型时，接受任意字符串（如 `"4"`）或整数（如 `4`、`-4`）输入值并强制转换为 ID；浮点输入值（如 `4.0`）必须引发 request error。

#### Scalar Extensions

F-136: [Type System-Scalar Extensions] ScalarTypeExtension 是 `extend scalar` Name Directives[Const]。
F-137: [Type System-Scalar Extensions] 扩展要求命名类型必须已定义且为 Scalar 类型；不可重复指令不得已应用。

### Objects

F-138: [Type System-Objects] ObjectTypeDefinition 有两种形式：带 FieldsDefinition 的形式；不带字段的形式（lookahead != `{`）。
F-139: [Type System-Objects] ImplementsInterfaces 是：ImplementsInterfaces `&` NamedType；或 `implements` `&`? NamedType。
F-140: [Type System-Objects] FieldsDefinition 是 `{` FieldDefinition+ `}`。
F-141: [Type System-Objects] FieldDefinition 是：Description? Name ArgumentsDefinition? `:` Type Directives[Const]?。
F-142: [Type System-Objects] Object 类型中所有字段名称不得以 `__` 开头。
F-143: [Type System-Objects] Object 类型必须定义一个或多个字段。
F-144: [Type System-Objects] Object 类型中字段名必须唯一；字段必须返回 IsOutputType 为 true 的类型。
F-145: [Type System-Objects] Object 字段可以是 Scalar、Enum、另一个 Object、Interface、Union，或这五者之一的包装类型。
F-146: [Type System-Objects] Object 类型不能作为有效输入。
F-147: [Type System-Objects] Object 类型可声明实现一个或多个唯一接口；必须是其所实现所有接口的超集。
F-148: [Type System-Objects] 字段排序按执行中遇到的顺序；JSON 等无序映射格式应文本上保留该顺序。

### Field Arguments

F-149: [Type System-Field Arguments] ArgumentsDefinition 是 `(` InputValueDefinition+ `)`。
F-150: [Type System-Field Arguments] InputValueDefinition 是：Description? Name `:` Type DefaultValue? Directives[Const]?。
F-151: [Type System-Field Arguments] 字段中所有参数名称不得以 `__` 开头；参数名在字段内必须唯一；参数类型必须是输入类型。
F-152: [Type System-Field Arguments] 若参数类型为 Non-Null 且未定义默认值，则不得对该参数应用 `@deprecated` 指令。

### Field Deprecation

F-153: [Type System-Field Deprecation] `@deprecated` 指令用于标记字段已弃用。

### Object Extensions

F-154: [Type System-Object Extensions] ObjectTypeExtension 有三种形式：带 FieldsDefinition；仅带 Directives（无大括号）；仅带 ImplementsInterfaces（无大括号）。
F-155: [Type System-Object Extensions] 扩展字段名必须唯一且不得已在先前 Object 类型上定义；不可重复指令不得已应用；提供的接口不得已被先前 Object 实现。

### Interfaces

F-156: [Type System-Interfaces] InterfaceTypeDefinition 有两种形式：带 FieldsDefinition；不带字段（lookahead != `{`）。
F-157: [Type System-Interfaces] Interface 类型必须定义一个或多个字段；字段名必须唯一；字段必须返回输出类型。
F-158: [Type System-Interfaces] Interface 可以实现其他接口；被实现接口所传递实现的接口也必须在实现类型或接口上定义。
F-159: [Type System-Interfaces] Interface 定义不得包含循环引用，也不得实现自身。
F-160: [Type System-Interfaces] Interface 不能作为有效输入。
F-161: [Type System-Interfaces] 在接口类型上选择字段时，只能查询该接口上声明的字段。

### Interface Extensions

F-162: [Type System-Interface Extensions] InterfaceTypeExtension 有三种形式。
F-163: [Type System-Interface Extensions] 扩展字段名必须唯一且不得已在先前 Interface 上定义；已实现先前 Interface 的 Object 或 Interface 必须也是扩展字段的超集。

### Unions

F-164: [Type System-Unions] UnionTypeDefinition 是：Description? `union` Name Directives[Const]? UnionMemberTypes?。
F-165: [Type System-Unions] UnionMemberTypes 是：UnionMemberTypes `|` NamedType；或 `=` `|`? NamedType。
F-166: [Type System-Unions] Union 类型必须包含一个或多个唯一成员类型。
F-167: [Type System-Unions] Union 成员类型必须全部是 Object 基类型；Scalar、Interface、Union 和包装类型不得作为 Union 成员。
F-168: [Type System-Unions] Union 不定义任何字段；除元字段 `__typename` 外，不使用类型精炼片段或内联片段则不能查询任何字段。
F-169: [Type System-Unions] Union 不能作为有效输入。

### Union Extensions

F-170: [Type System-Union Extensions] UnionTypeExtension 有两种形式：带 UnionMemberTypes；仅带 Directives。
F-171: [Type System-Union Extensions] 扩展成员类型必须全部是 Object 基类型；必须唯一且不得已是先前 Union 的成员。

### Enums

F-172: [Type System-Enums] EnumTypeDefinition 有两种形式：带 EnumValuesDefinition；不带（lookahead != `{`）。
F-173: [Type System-Enums] EnumValuesDefinition 是 `{` EnumValueDefinition+ `}`。
F-174: [Type System-Enums] EnumValueDefinition 是：Description? EnumValue Directives[Const]?。
F-175: [Type System-Enums] Enum 类型必须定义一个或多个唯一枚举值。
F-176: [Type System-Enums] 枚举值可序列化为字符串（所表示值的名称）；GraphQL 字符串字面量不得作为枚举输入接受，必须引发 request error。

### Enum Extensions

F-177: [Type System-Enum Extensions] EnumTypeExtension 有两种形式：带 EnumValuesDefinition；仅带 Directives。
F-178: [Type System-Enum Extensions] 扩展值必须唯一且不得已是先前 Enum 的值。

### Input Objects

F-179: [Type System-Input Objects] InputObjectTypeDefinition 有两种形式：带 InputFieldsDefinition；不带（lookahead != `{`）。
F-180: [Type System-Input Objects] InputFieldsDefinition 是 `{` InputValueDefinition+ `}`。
F-181: [Type System-Input Objects] Input Object 类型必须定义一个或多个输入字段；输入字段名必须唯一且不得以 `__` 开头；输入字段类型必须是输入类型。
F-182: [Type System-Input Objects] Input Object 类型不能作为 Object 或 Interface 字段的返回类型。
F-183: [Type System-Input Objects] Input Object 可引用其他 Input Object 作为字段类型；循环引用中至少一个字段必须是 nullable 或 List 类型，否则无效。
F-184: [Type System-Input Objects] 输入对象字段值可以是输入对象字面量或变量提供的无序映射；不得包含未定义字段名，否则 request error。
F-185: [Type System-Input Objects] 显式提供 `null` 与未提供值在语义上不同。

### OneOf Input Objects

F-186: [Type System-OneOf Input Objects] OneOf Input Object 是 Input Object 的特殊变体，恰好一个字段必须被设置且非 null，所有其他字段省略；由 `@oneOf` 指令标记。
F-187: [Type System-OneOf Input Objects] OneOf Input Object 的所有字段必须是 nullable，且不得有默认值。
F-188: [Type System-OneOf Input Objects] 内省中 `__Type.isOneOf` 字段对 OneOf Input Object 返回 true，对其他 Input Object 返回 false。
F-189: [Type System-OneOf Input Objects] Input Object 类型扩展不得提供 `@oneOf` 指令。

### Input Object Extensions

F-190: [Type System-Input Object Extensions] InputObjectTypeExtension 有两种形式：带 InputFieldsDefinition；仅带 Directives。
F-191: [Type System-Input Object Extensions] 扩展字段名必须唯一且不得已是先前 Input Object 的字段；若原类型是 OneOf Input Object，扩展字段必须 nullable 且无默认值。

### List

F-192: [Type System-List] List 类型声明列表中每一项的类型（item type）；列表值序列化为有序列表；允许嵌套列表（如 `[[Int]]`）。
F-193: [Type System-List] 若非列表且非 null 值作为列表类型输入，强制转换结果为大小为 1 的列表（可递归应用于嵌套列表）。
F-194: [Type System-List] List 的 item type 为 nullable 时，单个 item 的错误导致该位置为 null 并附加 execution error；item type 为 non-null 时，单个 item 错误导致整个列表 execution error。

### Non-Null

F-195: [Type System-Non-Null] Non-Null 类型由尾随感叹号 `!` 表示。
F-196: [Type System-Non-Null] Non-Null 类型不得包装另一个 Non-Null 类型。
F-197: [Type System-Non-Null] 字段在选择集中始终可选，但返回 Non-Null 类型的字段被查询时永不返回 null。
F-198: [Type System-Non-Null] Non-Null 输入类型是必需的：不接受 null 值，也不接受省略。
F-199: [Type System-Non-Null] 若 Non-Null 类型的结果强制转换为 null，必须引发 execution error。

### Directives

F-200: [Type System-Directives] DirectiveDefinition 是：Description? `directive` `@` Name ArgumentsDefinition? Directives[Const]? `repeatable`? `on` DirectiveLocations。
F-201: [Type System-Directives] DirectiveLocations 是由 `|` 分隔的一个或多个 DirectiveLocation。
F-202: [Type System-Directives] ExecutableDirectiveLocation 值：QUERY、MUTATION、SUBSCRIPTION、FIELD、FRAGMENT_DEFINITION、FRAGMENT_SPREAD、INLINE_FRAGMENT、VARIABLE_DEFINITION。
F-203: [Type System-Directives] TypeSystemDirectiveLocation 值：SCHEMA、SCALAR、OBJECT、FIELD_DEFINITION、ARGUMENT_DEFINITION、INTERFACE、UNION、ENUM、ENUM_VALUE、INPUT_OBJECT、INPUT_FIELD_DEFINITION、DIRECTIVE_DEFINITION。
F-204: [Type System-Directives] 内建指令包括：`@skip`、`@include`、`@deprecated`、`@specifiedBy`、`@oneOf`。
F-205: [Type System-Directives] `@skip` 定义：`directive @skip(if: Boolean!) on FIELD | FRAGMENT_SPREAD | INLINE_FRAGMENT`。
F-206: [Type System-Directives] `@include` 定义：`directive @include(if: Boolean!) on FIELD | FRAGMENT_SPREAD | INLINE_FRAGMENT`。
F-207: [Type System-Directives] `@deprecated` 定义：`directive @deprecated(reason: String! = "No longer supported") on FIELD_DEFINITION | ARGUMENT_DEFINITION | INPUT_FIELD_DEFINITION | ENUM_VALUE | DIRECTIVE_DEFINITION`。
F-208: [Type System-Directives] `@specifiedBy` 定义：`directive @specifiedBy(url: String!) on SCALAR`。
F-209: [Type System-Directives] `@oneOf` 定义：`directive @oneOf on INPUT_OBJECT`。
F-210: [Type System-Directives] `@skip` 和 `@include` 均无优先级；同时出现在同一字段或片段上时，仅当 `@skip` 条件为 false **且** `@include` 条件为 true 时才查询。
F-211: [Type System-Directives] `@deprecated` 不得出现在必需参数（non-null 且无默认值）或输入对象字段定义上。
F-212: [Type System-Directives] `@specifiedBy` 不得出现在内建标量类型上。
F-213: [Type System-Directives] 指令可通过 `repeatable` 关键字定义为可重复。
F-214: [Type System-Directives] 指令定义必须包含至少一个 DirectiveLocation。
F-215: [Type System-Directives] 指令不得直接或间接引用自身；指令名称不得以 `__` 开头；参数名不得以 `__` 开头且必须唯一。
F-216: [Type System-Directives] 使用 IDL 表示 schema 时可省略内建指令；内省时必须返回所有指令（包括内建指令）。

### Directive Extensions

F-217: [Type System-Directive Extensions] DirectiveExtension 是 `extend directive @` Name Directives[Const]。
F-218: [Type System-Directive Extensions] 扩展要求前序指令必须已定义；不可重复指令不得已应用；不得包含直接或间接引用前序指令的指令。

## Section 4 — Introspection

### 保留名称与元字段

F-219: [Introspection] 内省系统所需的类型和字段以 `__`（两个下划线）为前缀，以避免与用户定义类型命名冲突。
F-220: [Introspection] 类型名称内省元字段 `__typename: String!` 可在任意 Object、Interface 或 Union 的选择集中使用，返回执行时具体 Object 类型的名称。
F-221: [Introspection] `__typename` 不得作为 subscription 操作的根字段包含。
F-222: [Introspection] `__typename` 是隐式的，不出现在任何已定义类型的字段列表中。
F-223: [Introspection] Schema 内省元字段可从 query 操作根类型访问：`__schema: __Schema!` 和 `__type(name: String!): __Type`。
F-224: [Introspection] `__schema` 和 `__type` 是隐式的，不出现在 query 操作根类型的字段列表中。

### 通用约定

F-225: [Introspection] 内省系统中所有类型提供 `description: String` 字段；可使用 Markdown 语法。
F-226: [Introspection] 字段、参数、输入字段和枚举值可指示是否弃用（`isDeprecated: Boolean!`）及弃用原因（`deprecationReason: String`）。
F-227: [Introspection] 内省应按源码顺序返回：object fields、input object fields、arguments、enum values、directives、union member types、implemented interfaces。

### __Schema

F-228: [Introspection-__Schema] `__Schema` 类型字段：
  - `description: String`
  - `types: [__Type!]!`
  - `queryType: __Type!`
  - `mutationType: __Type`
  - `subscriptionType: __Type`
  - `directives(includeDeprecated: Boolean! = false): [__Directive!]!`
F-229: [Introspection-__Schema] `types` 必须返回 schema 中包含的所有命名类型集合；可通过任意内省类型字段到达的命名类型必须包含。
F-230: [Introspection-__Schema] `directives` 必须返回 schema 中所有可用指令集合（包括所有内建指令）；`includeDeprecated` 参数默认为 false，为 true 时也返回已弃用指令。
F-231: [Introspection-__Schema] `mutationType` 在不支持 mutation 时返回 null；`subscriptionType` 在不支持 subscription 时返回 null。

### __Type

F-232: [Introspection-__Type] `__Type` 类型字段：
  - `kind: __TypeKind!`
  - `name: String`
  - `description: String`
  - `specifiedByURL: String`（自定义 SCALAR 可能非 null，否则 null）
  - `fields(includeDeprecated: Boolean! = false): [__Field!]`（OBJECT 和 INTERFACE 必须非 null，否则 null）
  - `interfaces: [__Type!]`（OBJECT 和 INTERFACE 必须非 null，否则 null）
  - `possibleTypes: [__Type!]`（INTERFACE 和 UNION 必须非 null，否则 null）
  - `enumValues(includeDeprecated: Boolean! = false): [__EnumValue!]`（ENUM 必须非 null，否则 null）
  - `inputFields(includeDeprecated: Boolean! = false): [__InputValue!]`（INPUT_OBJECT 必须非 null，否则 null）
  - `ofType: __Type`（NON_NULL 和 LIST 必须非 null，否则 null）
  - `isOneOf: Boolean`（INPUT_OBJECT 必须非 null，否则 null）
F-233: [Introspection-__Type] `__TypeKind` 枚举值：SCALAR、OBJECT、INTERFACE、UNION、ENUM、INPUT_OBJECT、LIST、NON_NULL。
F-234: [Introspection-__Type] SCALAR kind：`kind` 返回 `__TypeKind.SCALAR`；`name` 返回 String；`specifiedByURL` 对自定义标量可返回 URL 字符串，否则必须 null；其他字段返回 null。
F-235: [Introspection-__Type] OBJECT kind：`kind` 返回 `__TypeKind.OBJECT`；`name` 返回 String；`fields` 返回可选字段集合；`interfaces` 返回实现的接口集合（无则返回空集）；其他字段返回 null。
F-236: [Introspection-__Type] INTERFACE kind：`kind` 返回 `__TypeKind.INTERFACE`；`fields` 返回所需字段集合；`interfaces` 返回所实现接口集合；`possibleTypes` 返回实现该接口的类型列表（必须为 object 类型）；其他字段返回 null。
F-237: [Introspection-__Type] UNION kind：`kind` 返回 `__TypeKind.UNION`；`possibleTypes` 返回可在该联合中表示的类型列表（必须为 object 类型）；其他字段返回 null。
F-238: [Introspection-__Type] ENUM kind：`kind` 返回 `__TypeKind.ENUM`；`enumValues` 返回 `__EnumValue` 列表（至少一个，名称唯一）；其他字段返回 null。
F-239: [Introspection-__Type] INPUT_OBJECT kind：`kind` 返回 `__TypeKind.INPUT_OBJECT`；`inputFields` 返回 `__InputValue` 列表；`isOneOf` 对 OneOf Input Object 返回 true，否则 false；其他字段返回 null。
F-240: [Introspection-__Type] LIST kind：`kind` 返回 `__TypeKind.LIST`；`ofType` 返回任意类型；其他字段返回 null。
F-241: [Introspection-__Type] NON_NULL kind：`kind` 返回 `__TypeKind.NON_NULL`；`ofType` 返回除 Non-Null 外的任意类型；其他字段返回 null。

### __Field

F-242: [Introspection-__Field] `__Field` 类型字段：
  - `name: String!`
  - `description: String`
  - `args(includeDeprecated: Boolean! = false): [__InputValue!]!`
  - `type: __Type!`
  - `isDeprecated: Boolean!`
  - `deprecationReason: String`

### __InputValue

F-243: [Introspection-__InputValue] `__InputValue` 类型字段：
  - `name: String!`
  - `description: String`
  - `type: __Type!`
  - `defaultValue: String`（使用 GraphQL 语言编码的默认值，无默认值时返回 null）
  - `isDeprecated: Boolean!`
  - `deprecationReason: String`

### __EnumValue

F-244: [Introspection-__EnumValue] `__EnumValue` 类型字段：
  - `name: String!`
  - `description: String`
  - `isDeprecated: Boolean!`
  - `deprecationReason: String`

### __Directive

F-245: [Introspection-__Directive] `__Directive` 类型字段：
  - `name: String!`
  - `description: String`
  - `isRepeatable: Boolean!`
  - `locations: [__DirectiveLocation!]!`
  - `args(includeDeprecated: Boolean! = false): [__InputValue!]!`
  - `isDeprecated: Boolean!`
  - `deprecationReason: String`
F-246: [Introspection-__Directive] `__Directive` 表示服务支持的指令，包括内建指令和自定义指令。
F-247: [Introspection-__Directive] `isRepeatable` 返回 Boolean，指示指令是否可在单个位置重复使用。

### __DirectiveLocation

F-248: [Introspection-__DirectiveLocation] `__DirectiveLocation` 枚举值：QUERY、MUTATION、SUBSCRIPTION、FIELD、FRAGMENT_DEFINITION、FRAGMENT_SPREAD、INLINE_FRAGMENT、VARIABLE_DEFINITION、SCHEMA、SCALAR、OBJECT、FIELD_DEFINITION、ARGUMENT_DEFINITION、INTERFACE、UNION、ENUM、ENUM_VALUE、INPUT_OBJECT、INPUT_FIELD_DEFINITION、DIRECTIVE_DEFINITION。

---

## 事实总数统计

| 章节 | 事实数 | 编号范围 |
|---|---|---|
| Section 1 — Overview | 10 | F-001 ~ F-010 |
| Section 2 — Language | 83 | F-011 ~ F-093 |
| Section 3 — Type System | 125 | F-094 ~ F-218 |
| Section 4 — Introspection | 30 | F-219 ~ F-248 |
| **合计** | **248** | **F-001 ~ F-248** |

---

## Section 5 — Validation

F-249: [Validation] GraphQL 服务不仅验证请求语法正确，还确保其在给定 schema 上下文中无歧义且无错误。
F-250: [Validation] 无效请求在技术上仍可执行，且按 Execution 章节算法产生稳定结果，但该结果可能有歧义或出乎意料，因此执行应仅针对有效请求发生。
F-251: [Validation] 类型系统随时间演进添加新类型和字段时，先前有效的请求可能变为无效；导致此情况的变更称为 breaking change。

### Documents

F-252: [Validation-Documents] Executable Definitions：文档中每个 definition 必须是 ExecutableDefinition，不得是 TypeSystemDefinitionOrExtension。
F-253: [Validation-Documents] 包含 TypeSystemDefinitionOrExtension 的文档对执行无效。

### Operations

F-254: [Validation-Operations] 每个 schema 必须支持 query 操作；mutation 和 subscription 操作的支持是可选的。
F-255: [Validation-Operations] Operation Type Existence：对文档中每个操作定义，schema 中必须存在对应操作类型的 root operation type。
F-256: [Validation-Operations] Operation Name Uniqueness：文档中每个命名操作定义的名称在文档内必须唯一，即使操作类型不同也不允许同名。
F-257: [Validation-Operations] Lone Anonymous Operation：当文档包含多个操作时，不得存在匿名操作。
F-258: [Validation-Operations] Subscription Single Root Field：subscription 操作的顶级选择集经 CollectSubscriptionFields 收集后必须恰好有一个条目，且该条目不得是内省字段。
F-259: [Validation-Operations] CollectSubscriptionFields 在收集时禁止选择项提供 @skip 或 @include 指令（因为验证时无法访问运行时变量）。
F-260: [Validation-Operations] 单个文档可包含任意数量的 subscription 操作，每个可包含不同根字段；执行含多个 subscription 的文档时必须提供 operation name。

### Fields

F-261: [Validation-Fields] Field Selections：字段选择的目标字段必须在作用域类型上定义；别名名称无限制。
F-262: [Validation-Fields] 对 Interface 类型，只能直接选择 Interface 上定义的字段，具体实现者上的字段与该 interface 类型选择集的有效性无关。
F-263: [Validation-Fields] Union 类型不定义字段（__typename 元字段除外），不得直接从 union 类型选择集选择字段，必须通过片段间接查询。
F-264: [Validation-Fields] Field Selection Merging：任意选择集中 FieldsInSetCanMerge(set) 必须为 true。
F-265: [Validation-Fields] FieldsInSetCanMerge：同 response name 的每对不同字段必须 SameResponseShape 为 true；当父类型相同或任一非 Object 类型时，必须具有相同字段名和相同参数集合，且合并后的子选择集也必须可合并。
F-266: [Validation-Fields] SameResponseShape：Non-Null 与 nullable 不匹配返回 false；List 基数不匹配返回 false；Scalar/Enum 必须同类型；复合类型递归检查子字段响应形状。
F-267: [Validation-Fields] 不同 Object 类型下（通过 fragment 区分）的同 response name 字段可具有不同字段名或参数，因为它们不会在同一对象上同时遇到。
F-268: [Validation-Fields] Leaf Field Selections：解包结果类型为 scalar 或 enum 时，该选择的子选择集必须为空。
F-269: [Validation-Fields] 解包结果类型为 interface、union 或 object 时，该选择的子选择集不得为空。

### Arguments

F-270: [Validation-Arguments] Argument Names：提供给字段或指令的每个参数必须在该字段或指令的可能参数集合中定义。
F-271: [Validation-Arguments] Argument Uniqueness：同一参数集合中不得出现多个同名参数。
F-272: [Validation-Arguments] Required Arguments：类型为 Non-Null 且无默认值的参数必须提供，且值不得为 null 字面量；否则参数为可选。
F-273: [Validation-Arguments] 参数顺序不影响验证结果。

### Fragments

F-274: [Validation-Fragments] Fragment Name Uniqueness：文档中每个 fragment 定义的名称必须唯一；inline fragment 不受此规则影响。
F-275: [Validation-Fragments] Fragment Spread Type Existence：命名片段和内联片段的目标类型必须在 schema 中定义。
F-276: [Validation-Fragments] Fragments on Composite Types：fragment 的目标类型必须是 UNION、INTERFACE 或 OBJECT 类型，不得声明在 scalar 上。
F-277: [Validation-Fragments] Fragments Must Be Used：每个已定义的 fragment 必须至少被文档中的一个 spread 引用。
F-278: [Validation-Fragments] Fragment Spread Target Defined：每个命名 fragment spread 必须引用文档中已定义的 fragment。
F-279: [Validation-Fragments] Fragment Spreads Must Not Form Cycles：fragment spread 图不得形成任何环（包括自引用），否则会导致无限展开或无限执行。
F-280: [Validation-Fragments] Fragment Spread Is Possible：对每个 spread，其 fragmentType 与 parentType 的 GetPossibleTypes 交集不得为空。
F-281: [Validation-Fragments] GetPossibleTypes：Object 类型返回包含自身的集合；Interface 返回实现该接口的类型集合；Union 返回其可能类型集合。
F-282: [Validation-Fragments] Object 作用域中 Object spread 仅在同类型时有效；Abstract（interface/union）spread 在 object 实现该接口或是 union 成员时有效。
F-283: [Validation-Fragments] Abstract 作用域中 Object spread 在 object 是该 abstract 类型可能类型之一时有效；Abstract spread 在 abstract scope 中只要存在至少一个同时属于两者可能类型交集的 object 类型即有效。
F-284: [Validation-Fragments] Interface 类型 fragment 可始终 spread 到它所实现的 Interface 作用域中。

### Values

F-285: [Validation-Values] Values of Correct Type：文档中每个字面量 Input Value 必须可强制转换到其位置所期望的类型（假设嵌套的 variableUsage 在运行时具有有效值）。
F-286: [Validation-Values] 期望类型位置包括：参数值位置、输入对象字段值位置、变量定义默认值位置。
F-287: [Validation-Values] Input Object Field Names：输入对象值中的每个字段必须在该输入对象期望类型的可能字段集合中定义。
F-288: [Validation-Values] Input Object Field Uniqueness：输入对象值中不得包含多个同名字段。
F-289: [Validation-Values] Input Object Required Fields：Non-Null 且无默认值的输入对象字段必须提供且值不得为 null 字面量；否则为可选字段。

### Directives

F-290: [Validation-Directives] Directives Are Defined：文档中每个指令使用必须对应服务中已定义的指令。
F-291: [Validation-Directives] Directives Are in Valid Locations：每个指令使用必须出现在该指令定义声明的有效位置之一。
F-292: [Validation-Directives] Directives Are Unique per Location：非 repeatable 指令在同一位置只能出现一次；repeatable 指令可在同一位置多次使用。

### Variables

F-293: [Validation-Variables] Variable Uniqueness：每个操作中定义的变量名在该操作内必须唯一；不同操作可定义同名变量。
F-294: [Validation-Variables] Variables Are Input Types：每个变量的类型必须是输入类型（IsInputType 为 true）；Object、Union、Interface 不能用作变量类型。
F-295: [Validation-Variables] All Variable Uses Defined：操作作用域及其传递性引用的所有 fragment 中使用的每个变量必须在该操作的变量列表中定义。
F-296: [Validation-Variables] All Variables Used：操作定义的每个变量必须在该操作本身或其传递性引用的 fragment 中至少使用一次，未使用变量导致验证错误。
F-297: [Validation-Variables] All Variable Usages Are Allowed：每个变量使用必须通过 IsVariableUsageAllowed 检查。
F-298: [Validation-Variables] IsVariableUsageAllowed：当 locationType 为 non-null 位置且 variableType 为 nullable 时，变量或位置必须提供非 null 默认值，否则返回 false；然后通过 AreTypesCompatible 判定类型兼容性。
F-299: [Validation-Variables] IsNonNullPosition：locationType 本身是 non-null 返回 true；当 variableUsage 位于 OneOf Input Object 的 ObjectField 中时返回 true；否则返回 false。
F-300: [Validation-Variables] AreTypesCompatible：non-null 对 non-null 解包后递归比较；List 基数必须匹配且 item 类型递归兼容；最终要求命名类型相同。
F-301: [Validation-Variables] OneOf Input Object 字段位置上的变量必须是 non-nullable 类型。
F-302: [Validation-Variables] nullable 变量在变量或位置提供默认值时可出现在 non-null 参数位置；运行时仍提供 null 时 non-null 参数必须引发 execution error。

## Section 6 — Execution

### Executing Requests

F-303: [Execution] 执行请求由以下信息组成：schema、document（必须含 OperationDefinition，可含 FragmentDefinition）、operationName（可选）、variableValues（可选）、initialValue（可选）、extensions（可选）。
F-304: [Execution] extensions 如果存在必须是 map，键应使用唯一前缀以避免与未来规范版本冲突；实现不应向 request 添加额外属性。
F-305: [Execution] GraphQL 请求不要求特定序列化格式或传输机制。
F-306: [Execution] 可执行文档（操作定义、片段定义、变量定义）中的 description 和 comment 在执行期间必须被忽略，对可观察的执行、验证或响应无影响。
F-307: [Execution-ExecuteRequest] ExecuteRequest(schema, document, operationName, variableValues, initialValue) 流程：GetOperation → CoerceVariableValues → 按操作类型分派到 ExecuteQuery（query）、ExecuteMutation（mutation）或 Subscribe（subscription）。
F-308: [Execution-GetOperation] operationName 为 null 时，文档必须恰好包含一个操作并返回之，否则引发 request error 要求提供 operationName；operationName 非 null 时按名称查找，未找到则引发 request error。
F-309: [Execution] 只有通过所有验证规则的请求才应执行；已知验证错误应在 response 的 errors 中报告且请求必须不执行。
F-310: [Execution] 服务可对先前已验证通过且未变更的请求记忆化验证结果，避免重复验证。

### Coercing Variable Values

F-311: [Execution-CoerceVariableValues] 变量值按变量声明类型的输入强制转换规则进行强制转换；输入强制转换期间遇到 request error 则操作不执行。
F-312: [Execution-CoerceVariableValues] 未提供值且存在默认值（包括 null）时，对默认值按变量类型输入强制转换规则强制转换后使用。
F-313: [Execution-CoerceVariableValues] 变量类型为 Non-Nullable 且未提供值或值为 null 时，引发 request error。
F-314: [Execution-CoerceVariableValues] 提供 null 值时 coercedValues 中记录 null；提供非 null 值时按类型强制转换，不可转换则引发 request error。
F-315: [Execution-CoerceVariableValues] CoerceVariableValues 算法与 CoerceArgumentValues 非常相似。

### Executing Operations

F-316: [Execution-Operations] 类型系统必须提供 query root operation type；支持 mutation/subscription 时必须分别提供 mutation/subscription root operation type。

#### Query

F-317: [Execution-Query] query 操作结果是在 query root operation type 上执行其 root selection set 的结果。
F-318: [Execution-Query] ExecuteQuery：获取 query root type（断言为 Object 类型），以 "normal" 执行模式调用 ExecuteRootSelectionSet。
F-319: [Execution-Query] 执行 query 操作时可提供 initialValue。

#### Mutation

F-320: [Execution-Mutation] mutation 操作结果是在 mutation root object type 上执行其 root selection set 的结果。
F-321: [Execution-Mutation] ExecuteMutation：获取 mutation root type（断言为 Object 类型），以 "serial" 执行模式调用 ExecuteRootSelectionSet。
F-322: [Execution-Mutation] mutation 顶级选择集必须串行执行，因为顶级字段预期对底层数据系统产生副作用，串行执行可防止竞态条件。

#### Subscription

F-323: [Execution-Subscription] subscription 操作结果是称为 response stream 的 event stream，source stream 中每个新事件触发一次操作执行并产生一个 execution result。
F-324: [Execution-Subscription] 执行 subscription 操作在服务上创建持久函数，将底层 source stream 映射到返回的 response stream。
F-325: [Execution-Subscription] Subscribe 算法：CreateSourceEventStream 产生 sourceStream → MapSourceToResponseEvent 产生 responseStream → 返回 responseStream。
F-326: [Execution-Subscription] Subscribe 和 ExecuteSubscriptionEvent 算法可在独立服务上运行，以维持大规模订阅系统的可预测扩展特性。
F-327: [Execution-Subscription] event stream 表示随时间发出的离散值序列；可随时完成、可发出无限序列值、遇到错误必须以该错误完成；被观察者取消时必须完成。
F-328: [Execution-Subscription] query 和 mutation 操作是无状态的，可通过克隆服务实例扩展；subscription 是有状态的，需在订阅生命周期内维护 GraphQL 文档、变量和其他上下文。
F-329: [Execution-Subscription] GraphQL subscription 不要求特定序列化格式或传输机制；规范不规定消息确认、缓冲、重传请求或任何 QoS 细节。
F-330: [Execution-Subscription] source stream 是表示根值序列的 event stream，每个根值触发一次 GraphQL 执行；创建 source stream 的逻辑是应用特定的。
F-331: [Execution-Subscription] CreateSourceEventStream：CollectFields 收集顶级字段，collectedFieldsMap 必须恰好一个条目（否则 request error）；取第一个字段的 fieldName 和 field，CoerceArgumentValues，ResolveFieldEventStream 返回 sourceStream。
F-332: [Execution-Subscription] ResolveFieldEventStream 调用 subscriptionType 为指定 fieldName 提供的内部函数，传入 rootValue 和 argumentValues 返回 event stream。
F-333: [Execution-Subscription] MapSourceToResponseEvent：sourceStream 发出 sourceValue 时调用 ExecuteSubscriptionEvent；内部错误则取消 sourceStream 并以 error 完成 responseStream；正常发出结果；sourceStream 正常完成则 responseStream 正常完成；sourceStream 错误完成则 responseStream 以错误完成；responseStream 取消时取消 sourceStream 并正常完成。
F-334: [Execution-Subscription] ExecuteSubscriptionEvent：获取 subscription root type（断言为 Object），以 "normal" 模式执行 root selection set，与 ExecuteQuery 类似。
F-335: [Execution-Subscription] Unsubscribe 取消 responseStream，进而取消 sourceStream。

### Executing Selection Sets

F-336: [Execution-SelectionSets] GraphQL 操作递归收集并执行每个选定字段：先收集顶级 root selection set 的字段，逐个执行；每个字段完成后收集其子字段再执行，直到没有更多子字段。
F-337: [Execution-SelectionSets] root selection set 是 GraphQL 操作提供的顶级 selection set，始终从 root operation type 选择。
F-338: [Execution-SelectionSets] ExecuteRootSelectionSet(variableValues, initialValue, objectType, selectionSet, executionMode)：CollectFields 收集字段 → ExecuteCollectedFields（serial 模式串行，否则 normal 可并行）→ 返回包含 data 和 errors 的无序 map。
F-339: [Execution-FieldCollection] 执行前，每个 selection set 通过将具有相同 response name（含引用 fragment 中）的字段收集到独立 field set，转换为 collected fields map，确保同 response name 的字段只执行一次。
F-340: [Execution-FieldCollection] collected fields map 是有序 map，每个条目是 response name 及其关联的 field set；可由 CollectFields 从 selection set 产生，或由 CollectSubfields 从 field set 的选择集产生。
F-341: [Execution-FieldCollection] field set 是共享同一 response name（别名优先，否则字段名）的有序选定字段集合；验证确保 set 中每个字段具有相同名称和参数，但可有不同子字段。
F-342: [Execution-FieldCollection] collected fields map 和 field set 中字段选择的顺序是有意义的，规范以有序 map 和有序 set 建模。
F-343: [Execution-CollectFields] CollectFields 遍历 selectionSet 中每个 selection：@skip 的 if 参数为 true（或变量值为 true）则跳过；@include 的 if 参数不为 true（且变量值不为 true）则跳过；Field 按 responseName 加入对应 field set；FragmentSpread 检查 visitedFragments 防环、DoesFragmentTypeApply 判定后递归收集；InlineFragment 类似处理。
F-344: [Execution-CollectFields] DoesFragmentTypeApply(objectType, fragmentType)：Object 类型——相同类型返回 true；Interface 类型——objectType 实现该接口返回 true；Union 类型——objectType 是其可能类型返回 true。
F-345: [Execution-CollectFields] @skip 和 @include 的求值步骤可按任意顺序应用，因为它们满足交换律。
F-346: [Execution-SelectionSets] CollectSubfields 将 field set 中所有字段的选择集合并为单个 collected fields map。
F-347: [Execution-SelectionSets] ExecuteCollectedFields：初始化 resultMap 为有序 map；遍历 collectedFieldsMap，取每个 fields 第一个条目的 fieldName，查 objectType 上该字段的 fieldType，调用 ExecuteField，结果以 responseName 为键存入 resultMap。
F-348: [Execution-SelectionSets] resultMap 按字段在操作中首次出现的顺序排序。
F-349: [Execution-SelectionSets] Non-Null 类型响应位置引发 execution error 时，错误必须传播到父响应位置；如父位置可为 null 则解析为 null，否则继续传播；尚未执行的兄弟位置可取消以避免不必要工作。

#### Normal and Serial Execution

F-350: [Execution-ExecutionMode] normal 模式下，执行器可按任意顺序（通常并行）执行 collected fields map 中的条目；非顶级 mutation 字段的解析必须无副作用且幂等，执行顺序不影响结果。
F-351: [Execution-ExecutionMode] serial 模式下（mutation 顶级选择集），执行器必须按 collected fields map 中的顺序逐个处理每个条目，每个条目在 resultMap 中对应值完成后才继续下一个。
F-352: [Execution-ExecutionMode] mutation 顶级字段串行执行，但其子选择集在 CompleteValue 期间以 normal 模式（可并行）执行。

### Executing Fields

F-353: [Execution-Fields] 字段执行先强制转换参数值，然后解析字段值，最后通过递归执行另一个选择集或强制转换标量值来完成该值。
F-354: [Execution-Fields] ExecuteField(objectType, objectValue, fieldType, fields, variableValues)：取 fields 第一个条目 → CoerceArgumentValues → ResolveFieldValue → CompleteValue。

#### Coercing Field Arguments

F-355: [Execution-CoerceArgumentValues] CoerceArgumentValues：遍历字段的 argumentDefinitions，未提供值且有默认值（包括 null）则强制转换默认值后使用；Non-Null 类型参数缺失或值为 null 引发 execution error；变量值不再强制转换（已在 CoerceVariableValues 中转换）；字面量值按类型输入强制转换规则转换。
F-356: [Execution-CoerceArgumentValues] CoerceArgumentValues 期间因输入强制转换引发的 request error 应视为 execution error。
F-357: [Execution-CoerceArgumentValues] 实现可优化参数默认值的强制转换，只执行一次并缓存结果。

#### Value Resolution

F-358: [Execution-ResolveFieldValue] ResolveFieldValue 调用 objectType 为 fieldName 提供的内部 resolver 函数，传入 objectValue 和 argumentValues 返回解析值。
F-359: [Execution-ResolveFieldValue] resolver 通常是异步的（依赖底层数据库或网络服务），GraphQL 执行器必须处理异步执行流；List 类型字段返回的值集合中每个值本身也可能异步获取。

#### Value Completion

F-360: [Execution-CompleteValue] 字段值解析后，通过确保其符合预期返回类型来完成；返回类型为另一个 Object 类型时，字段执行递归收集并执行子字段。
F-361: [Execution-CompleteValue] Non-Null 类型：取 innerType，递归调用 CompleteValue；若 completedResult 为 null 则引发 execution error；否则返回 completedResult。
F-362: [Execution-CompleteValue] result 为 null（或类似 null 的内部值如 undefined）时返回 null。
F-363: [Execution-CompleteValue] List 类型：result 必须是值的集合，否则引发 execution error；对 result 中每个 resultItem 以 innerType 递归调用 CompleteValue，返回结果列表。
F-364: [Execution-CompleteValue] Scalar 或 Enum 类型：调用 CoerceResult(fieldType, result) 返回结果。
F-365: [Execution-CompleteValue] Object/Interface/Union 类型：Object 直接使用 fieldType；Interface/Union 先 ResolveAbstractType 确定 objectType；CollectSubfields 后以 normal 模式 ExecuteCollectedFields。
F-366: [Execution-CoerceResult] CoerceResult(leafType, value)：断言 value 非 null；调用类型系统提供的 result coercion 内部方法；该方法必须返回类型有效值且非 null，否则引发 execution error。
F-367: [Execution-ResolveAbstractType] ResolveAbstractType(abstractType, objectValue) 调用类型系统内部方法，根据 abstractType 和 objectValue 确定对应的 Object 类型。

### Handling Execution Errors

F-368: [Execution-Errors] execution error 在字段执行、值解析或强制转换期间于特定 response position 引发；这些错误必须在响应中报告，但通过产生部分 data 来"处理"。
F-369: [Execution-Errors] execution error 与 request error 不同，后者产生 request error result 且无 data。
F-370: [Execution-Errors] 字段解析期间（直接或嵌套在列表中）引发 execution error 时，该错误发生的 response position 视为解析为 null，错误必须加入 execution result 的 errors 列表。
F-371: [Execution-Errors] response position 因 ResolveFieldValue 结果或 execution error 而为 null，且该位置为 Non-Null 类型时，在该位置引发 execution error 并加入 errors 列表。
F-372: [Execution-Errors] 因已加入 errors 列表的 execution error 导致 position 为 null 时，errors 列表不再受影响——每个 response position 只添加一个错误。
F-373: [Execution-Errors] Non-Null response position 不能为 null，execution error 传播到父 response position 处理；父位置可为 null 则解析为 null；父位置也是 Non-Null 则继续传播。
F-374: [Execution-Errors] List 包装 Non-Null 类型时，列表元素位置解析为 null 则整个列表 position 必须解析为 null；若 List 也被 Non-Null 包装则 execution error 继续向上传播。
F-375: [Execution-Errors] 从请求根到 execution error 源的每个 response position 都是 Non-Null 类型时，execution result 的 data 条目应为 null。

## Section 7 — Response

### Response Format

F-376: [Response] GraphQL 服务收到请求必须返回格式良好的 response；response 描述成功执行的结果或请求期间引发的错误。
F-377: [Response] 当 execution error 被引发并替换为 null 时，response 可同时包含部分响应和错误列表。
F-378: [Response-Format] response 是 execution result、response stream 或 request error result 之一。
F-379: [Response-ExecutionResult] query 或 mutation 操作且请求包含执行时返回 execution result；subscription source stream 中每个事件也发出一个 execution result。
F-380: [Response-ExecutionResult] execution result 必须是 map，必须包含键为 "data" 的条目。
F-381: [Response-ExecutionResult] 执行引发错误时，execution result 必须包含键为 "errors" 的条目，值为执行期间引发的非空 execution error 列表；请求无错误完成时该条目不得出现。
F-382: [Response-ExecutionResult] execution result 可包含键为 "extensions" 的条目。
F-383: [Response-ResponseStream] subscription 操作且请求包含执行时返回 response stream；response stream 必须是 execution result 的流。
F-384: [Response-RequestErrorResult] 一个或多个 request error 引发（导致请求在执行前失败）时返回 request error result，不产生响应数据。
F-385: [Response-RequestErrorResult] request error 可因信息缺失、语法错误、验证失败、强制转换失败或实现判定应阻止请求继续的任何原因引发。
F-386: [Response-RequestErrorResult] request error result 必须是 map，必须包含非空 "errors" 列表（至少包含一个说明为何无法返回数据的 request error），不得包含 "data" 条目，可包含 "extensions"。

### Response Position

F-387: [Response-Position] response position 是执行期间产生的响应数据中可唯一标识的位置，可以是 ExecuteSelectionSet 的 resultMap 中的直接条目，也可以是（可能嵌套的）List 值中的位置。
F-388: [Response-Path] response path 通过从响应根开始到关联 response position 结束的路径段列表唯一标识 response position。
F-389: [Response-Path] response path 必须是路径段列表：表示字段 response name 的路径段必须是字符串，表示列表索引的路径段必须是从 0 开始的整数；别名字段必须使用别名（因为表示响应中的路径而非请求中的路径）。
F-390: [Response-Path] error result 上存在 response path 时，它标识引发错误的 response position。

### Data

F-391: [Response-Data] execution result 中的 "data" 条目是请求操作执行的结果：query 为 query root operation type 的对象，mutation 为 mutation root operation type 的对象。
F-392: [Response-Data] 响应数据是执行期间所有 response position 解析结果的累积。
F-393: [Response-Data] 执行开始前引发错误时，response 必须是 request error result（无响应数据）；执行期间引发导致有效响应无法生成的错误时，"data" 条目应为 null。

### Errors

F-394: [Response-Errors] execution result 或 request error result 中的 "errors" 条目是请求期间引发的非空错误列表，每个错误是按错误结果格式描述的 map。
F-395: [Response-Errors] request error 在请求期间引发，导致无响应数据；通常在执行开始前引发，包括 Document 解析语法或验证错误、无法确定执行哪个操作、变量输入值无效；通常是请求客户端的过错。
F-396: [Response-Errors] request error 引发时 response 必须是 request error result，不得包含 "data"，errors 必须包含该错误，请求执行应中止。
F-397: [Response-Errors] execution error 在特定字段执行期间引发，导致部分响应数据；可因字段参数强制转换失败、值解析期间内部错误或结果强制转换失败引发。
F-398: [Response-Errors] execution error 通常是 GraphQL 服务的过错。
F-399: [Response-Errors] execution error 必须发生在特定 response position，可发生在任意 response position；通过错误响应的 "path" 条目指示。
F-400: [Response-Errors] execution error 在给定 response position 引发时，该 position 不得出现在响应 "data" 条目中（null 除外），errors 必须包含该错误；嵌套执行中止，兄弟执行继续以产生部分结果。
F-401: [Response-Errors] 每个错误必须包含键为 "message" 的条目，值为面向开发者的字符串错误描述。
F-402: [Response-Errors] 错误若可关联到请求 GraphQL 文档中特定位置，应包含键为 "locations" 的条目，值为位置列表；每个位置是包含 "line" 和 "column" 键的 map，两者均为从 1 开始的正数。
F-403: [Response-Errors] 错误若可关联到 GraphQL 结果中特定字段，必须包含键为 "path" 的条目，值为描述引发错误的 response position 的 response path，使客户端可识别 null 结果是真实值还是 execution error 所致。
F-404: [Response-Errors] 发生错误的字段声明为 Non-Null 时，null 结果冒泡到下一个可为 null 的字段；错误的 path 应包含到引发错误的结果字段的完整路径，即使该字段不在响应中。
F-405: [Response-Errors] GraphQL 服务可在错误中提供键为 "extensions" 的条目，设置时其值必须是 map；该条目保留给实现者添加附加信息，对其内容无额外限制。
F-406: [Response-Errors] 服务不应在错误格式中提供除 message/locations/path/extensions 以外的条目，以避免与规范未来版本可能添加的条目冲突；非规范条目不视为违规但不鼓励。

### Extensions

F-407: [Response-Extensions] execution result 或 request error result 中的 "extensions" 条目如果设置，其值必须是 map；保留给实现者按需扩展协议，对其内容无额外限制。

### Additional Entries

F-408: [Response-AdditionalEntries] execution result 和 request error result map 不得包含上述条目以外的任何条目；客户端必须忽略上述以外的任何条目。

### Serialization Format

F-409: [Response-Serialization] GraphQL 不要求特定序列化格式，但序列化格式必须至少支持四种原语的表示：Map、List、String、Null。
F-410: [Response-Serialization] 序列化格式还应支持 Boolean、Int、Float、Enum Value（如不直接支持，可用字符串或更简单原语替代）；自定义标量可按格式支持的方式表示。
F-411: [Response-Serialization] JSON 序列化映射：Map→Object、List→Array、Null→null、String→String、Boolean→true/false、Int→Number、Float→Number、Enum Value→String。
F-412: [Response-Serialization] 选择集求值结果是有序的，序列化 Map 应按 CollectFields 定义的字段请求顺序写入条目；JSON 等文本有序格式应在文本上保持请求字段顺序。

## Appendix C — Grammar Summary

F-413: [Appendix C] 语法汇总分为五个部分：Source Text、Ignored Tokens、Lexical Tokens、Document Syntax、Schema Coordinate Syntax。
F-414: [Appendix C] SourceCharacter 是任意 Unicode 标量值。
F-415: [Appendix C] Ignored 包括 UnicodeBOM、Whitespace、LineTerminator、Comment、Comma。
F-416: [Appendix C] Token 包括 Punctuator、Name、IntValue、FloatValue、StringValue。
F-417: [Appendix C] Punctuator 为以下之一：`!` `$` `&` `(` `)` `...` `:` `=` `@` `[` `]` `{` `|` `}`。
F-418: [Appendix C] Document 由一个或多个 Definition 组成；Definition 为 ExecutableDefinition 或 TypeSystemDefinitionOrExtension。
F-419: [Appendix C] ExecutableDocument 仅包含 ExecutableDefinition；ExecutableDefinition 为 OperationDefinition 或 FragmentDefinition。
F-420: [Appendix C] OperationDefinition 有两种形式：Description? OperationType Name? VariablesDefinition? Directives? SelectionSet；或简写 SelectionSet。
F-421: [Appendix C] OperationType 为 `query`、`mutation`、`subscription` 之一。
F-422: [Appendix C] SelectionSet 为 `{ Selection+ }`；Selection 为 Field、FragmentSpread 或 InlineFragment。
F-423: [Appendix C] Field 为 Alias? Name Arguments? Directives? SelectionSet?；Alias 为 `Name :`。
F-424: [Appendix C] FragmentSpread 为 `... FragmentName Directives?`；InlineFragment 为 `... TypeCondition? Directives? SelectionSet`；FragmentDefinition 为 `Description? fragment FragmentName TypeCondition Directives? SelectionSet`。
F-425: [Appendix C] Value[Const] 包括：Variable（非 Const 时）、IntValue、FloatValue、StringValue、BooleanValue（`true`/`false`）、NullValue（`null`）、EnumValue、ListValue、ObjectValue。
F-426: [Appendix C] EnumValue 是 Name 但不得为 `true`、`false` 或 `null`；FragmentName 是 Name 但不得为 `on`。
F-427: [Appendix C] Type 为 NamedType、ListType（`[ Type ]`）或 NonNullType（NamedType `!` 或 ListType `!`）。
F-428: [Appendix C] VariableDefinition 为 `Description? Variable : Type DefaultValue? Directives[Const]?`；Variable 为 `$ Name`；DefaultValue 为 `= Value[Const]`。
F-429: [Appendix C] TypeSystemDefinition 包括 SchemaDefinition、TypeDefinition、DirectiveDefinition；TypeDefinition 包括 Scalar/Object/Interface/Union/Enum/InputObject 六种类型定义。
F-430: [Appendix C] DirectiveDefinition 形式：Description? `directive @` Name ArgumentsDefinition? Directives[Const]? `repeatable`? `on` DirectiveLocations。
F-431: [Appendix C] ExecutableDirectiveLocation 有 8 个值：QUERY、MUTATION、SUBSCRIPTION、FIELD、FRAGMENT_DEFINITION、FRAGMENT_SPREAD、INLINE_FRAGMENT、VARIABLE_DEFINITION。
F-432: [Appendix C] TypeSystemDirectiveLocation 有 12 个值：SCHEMA、SCALAR、OBJECT、FIELD_DEFINITION、ARGUMENT_DEFINITION、INTERFACE、UNION、ENUM、ENUM_VALUE、INPUT_OBJECT、INPUT_FIELD_DEFINITION、DIRECTIVE_DEFINITION。
F-433: [Appendix C] Schema Coordinate 语法包括：TypeCoordinate（Name）、MemberCoordinate（Name.Name）、ArgumentCoordinate（Name.Name(Name:)）、DirectiveCoordinate（@Name）、DirectiveArgumentCoordinate（@Name(Name:)）。
F-434: [Appendix C] Schema coordinate 不得包含 Ignored token。

<!-- 总计：669 条事实（Section 1-7：434 条；AI WG MCP 服务器源码+README：152 条 F-435~F-586；语义内省 RFC：26 条 F-587~F-612；官网生态信息：57 条 F-613~F-669） -->

## AI WG — MCP 服务器源码

### server.py — 模块与依赖

F-435: [server.py] 模块 docstring 说明该 MCP 服务器暴露 `list_types` 和 `run_query` 工具，支持 schema 文件或实时 endpoint 两种模式。（来源：server.py）
F-436: [server.py] import 依赖包括：标准库 os、json、threading、pathlib.Path、typing.Literal、urllib.error.HTTPError、urllib.request.Request/urlopen。（来源：server.py:24-30）
F-437: [server.py] 从 graphql-core 导入 build_client_schema、build_schema、get_introspection_query、graphql_sync、print_schema。（来源：server.py:32-38）
F-438: [server.py] 从 mcp.server.fastmcp 导入 FastMCP。（来源：server.py:39）
F-439: [server.py] 从 schema_indexer 导入 DEFAULT_DATA_DIR、DEFAULT_EMBED_MODEL、DEFAULT_SCHEMA_PATH、EmbeddingStore、OpenAIEmbedder、ensure_index、ensure_index_text。（来源：server.py:41-49）

### server.py — 全局常量与配置

F-440: [server.py] APP_NAME = "graphql-mcp"。（来源：server.py:51）
F-441: [server.py] DEFAULT_TRANSPORT 依次从环境变量 MCP_TRANSPORT、FASTMCP_TRANSPORT 读取，默认值为 "sse"。（来源：server.py:52）
F-442: [server.py] DEFAULT_INSTRUCTIONS 指示 LLM 将此 MCP 服务器视为 GraphQL 抽象层，先调用 list_types 再调用 run_query，避免不必要的工具调用。（来源：server.py:53-57）
F-443: [server.py] MCP_INSTRUCTIONS 可通过环境变量 MCP_INSTRUCTIONS 覆盖。（来源：server.py:58）
F-444: [server.py] SCHEMA_PATH 从环境变量 GRAPHQL_SCHEMA_PATH 读取，默认 DEFAULT_SCHEMA_PATH。（来源：server.py:60）
F-445: [server.py] ENDPOINT_URL 从环境变量 GRAPHQL_ENDPOINT_URL 读取。（来源：server.py:61）
F-446: [server.py] DATA_DIR 从环境变量 GRAPHQL_EMBEDDER_DATA_DIR 读取，默认 DEFAULT_DATA_DIR。（来源：server.py:62）
F-447: [server.py] EMBED_MODEL 从环境变量 GRAPHQL_EMBED_MODEL 读取，默认 DEFAULT_EMBED_MODEL。（来源：server.py:63）
F-448: [server.py] 全局实例化 embedder = OpenAIEmbedder(model=EMBED_MODEL) 和 store = EmbeddingStore(data_dir=DATA_DIR, embedding_model=embedder.model)。（来源：server.py:65-66）
F-449: [server.py] SCHEMA_SOURCE 初始化为 {"kind": "file", "path": str(SCHEMA_PATH)}。（来源：server.py:67）
F-450: [server.py] SCHEMA_TEXT 初始化为 None（str | None 类型）。（来源：server.py:68）
F-451: [server.py] _REMOTE_HEADERS 为 dict[str, str]，初始为空字典；_REMOTE_TIMEOUT_S 为 float，默认 30.0。（来源：server.py:69-70）
F-452: [server.py] _INDEX_LOCK = threading.Lock() 用于索引构建的线程同步。（来源：server.py:71）
F-453: [server.py] _SCALAR_TYPES = {"String", "Int", "Float", "Boolean", "ID"}。（来源：server.py:72）
F-454: [server.py] _AGGREGATE_KEYWORDS = {"count", "total", "sum", "avg", "average", "how many", "number of"}。（来源：server.py:73）
F-455: [server.py] _AGGREGATE_FIELD_PATTERNS = {"count", "total", "sum", "avg", "aggregate"}。（来源：server.py:74）
F-456: [server.py] mcp = FastMCP(APP_NAME, instructions=MCP_INSTRUCTIONS)；mcp.dependencies = ["graphql-core", "openai", "numpy"]。（来源：server.py:76-77）

### server.py — 传输与运行时配置函数

F-457: [server.py] 函数 _run_with_default_transport(self, transport: Literal["stdio","sse","streamable-http"] | None = None, mount_path: str | None = None) 通过 monkey-patch 覆盖 mcp.run，使默认传输使用 DEFAULT_TRANSPORT。（来源：server.py:80-89）
F-458: [server.py] 函数 configure_runtime(*, schema_path: Path, data_dir: Path, embed_model: str) -> None 重新设置文件模式的全局变量：SCHEMA_PATH、ENDPOINT_URL=None、DATA_DIR、EMBED_MODEL、embedder、store、SCHEMA_SOURCE={"kind":"file"}、SCHEMA_TEXT=None。（来源：server.py:92-101）
F-459: [server.py] 函数 configure_runtime_endpoint(*, endpoint_url: str, data_dir: Path, embed_model: str, schema_text: str, schema_source: dict) -> None 重新设置 endpoint 模式的全局变量，SCHEMA_PATH 设为 Path("<endpoint>")。（来源：server.py:104-120）

### server.py — HTTP 与内省辅助函数

F-460: [server.py] 函数 _parse_headers(raw_headers: list[str] | None) -> dict[str, str] 将 "Name: Value" 格式的字符串列表解析为字典，无效格式抛出 ValueError。（来源：server.py:123-134）
F-461: [server.py] 函数 _post_json(url: str, payload: dict, headers: dict[str,str] | None = None, timeout_s: float = 30.0) -> dict 发送 POST JSON 请求，设置 Content-Type 和 Accept 头，HTTPError 时尝试解析错误响应体。（来源：server.py:137-156）
F-462: [server.py] 函数 _introspect_schema_sdl(endpoint_url: str, headers: dict[str,str], timeout_s: float) -> str 使用 get_introspection_query(descriptions=True) 发送内省查询，通过 build_client_schema 和 print_schema 将结果转为 SDL 字符串。（来源：server.py:159-172）

### server.py — 签名解析与字段工具函数

F-463: [server.py] 函数 _parse_signature(signature: str) -> tuple[str, str, list[tuple[str,str]], str] 解析 "Type.field(arg: Type) -> ReturnType" 格式签名，返回 (type_name, field_name, args, return_type)。（来源：server.py:175-189）
F-464: [server.py] 函数 _base_type(type_str: str) -> str 递归去除 NonNull（!）和 List（[]）包装，返回基础类型名。（来源：server.py:192-199）
F-465: [server.py] 函数 _tokenize(text: str) -> list[str] 将文本转为小写字母数字 token 列表。（来源：server.py:202-218）
F-466: [server.py] 函数 _token_score(tokens: list[str], *values: str) -> int 统计 token 在 values 拼接文本中的出现次数。（来源：server.py:221-227）
F-467: [server.py] 函数 _is_aggregate_query(query: str) -> bool 检查查询是否包含 _AGGREGATE_KEYWORDS 中的关键词。（来源：server.py:230-233）
F-468: [server.py] 函数 _is_aggregate_field(field_name: str) -> bool 检查字段名是否包含 _AGGREGATE_FIELD_PATTERNS 中的模式。（来源：server.py:236-239）
F-469: [server.py] 函数 _is_connection_field(field_name: str) -> bool 检查字段名是否以 "connection" 结尾（不区分大小写）。（来源：server.py:242-244）
F-470: [server.py] 函数 _parse_field_info(meta: dict) -> dict[str, list[dict]] 从索引元数据的 items 中解析每个 summary 的签名部分，按 type_name 分组返回字段信息列表。（来源：server.py:247-263）
F-471: [server.py] 函数 _format_args(args: list[tuple[str,str]]) -> str 将参数列表格式化为 "(name: <type>, ...)" 字符串。（来源：server.py:266-270）
F-472: [server.py] 函数 _render_selection_set(type_name, fields_by_type, tokens, depth=1, max_fields=6) -> str | None 递归为对象类型生成 GraphQL selection set，优先选择标量字段和 token 匹配字段，id/name 字段加分。（来源：server.py:273-318）

### server.py — 索引确保函数

F-473: [server.py] 函数 ensure_schema_indexed(*, force: bool = False) -> dict 使用 _INDEX_LOCK 同步；endpoint 模式调用 ensure_index_text，文件模式调用 ensure_index；异常时包装为 RuntimeError。（来源：server.py:321-345）

### server.py — MCP 工具：list_types

F-474: [server.py] @mcp.tool() 装饰的函数 list_types(query: str, limit: int = 20) -> list，对 schema 进行模糊搜索，自动构建/更新持久化嵌入索引。（来源：server.py:348-450）
F-475: [server.py] list_types 中 capped_limit = max(1, min(limit, 20))，限制返回数量在 1-20 之间。（来源：server.py:359）
F-476: [server.py] list_types 使用 embedder.embed_one(query) 生成查询向量，store.search(query_vec, limit=capped_limit) 检索结果。（来源：server.py:360-361）
F-477: [server.py] list_types 的 sort_key 对结果排序：聚合查询时优先级为 Query 类型 > 聚合字段 > Connection 字段 > 相似度分数；非聚合查询时优先级为 Query 类型 > 相似度分数。（来源：server.py:363-391）
F-478: [server.py] list_types 对每个结果构造 entry，包含 type、field、summary 字段；Query 类型字段额外生成 query_template。（来源：server.py:393-403）
F-479: [server.py] list_types 对 Connection 字段（以 connection 结尾）生成深度 2、最多 8 字段的 selection set，添加 usage_hint 提示使用游标分页。（来源：server.py:410-420）
F-480: [server.py] list_types 对聚合字段生成无 selection set 的 query_template，添加 usage_hint 标注为 O(1) count 操作。（来源：server.py:421-424）
F-481: [server.py] list_types 对非 Query 类型的非标量返回字段，生成 selection_hint（深度 1，最多 5 字段）。（来源：server.py:437-446）

### server.py — MCP 工具：run_query

F-482: [server.py] @mcp.tool() 装饰的函数 run_query(query: str) -> dict，验证并执行 GraphQL 查询。（来源：server.py:453-483）
F-483: [server.py] run_query 在 endpoint 模式下将查询代理到 ENDPOINT_URL，返回包含 valid、errors、data、extensions 的字典。（来源：server.py:461-474）
F-484: [server.py] run_query 在本地模式下使用 build_schema(SCHEMA_PATH.read_text()) 和 graphql_sync(schema, query) 执行；无 resolver 时字段解析为 null，主要用于验证和形状检查。（来源：server.py:476-483）

### server.py — CLI 入口

F-485: [server.py] __main__ 块使用 argparse，支持 --transport（stdio/sse/streamable-http，默认 sse）、--schema、--endpoint（互斥）、--data-dir、--model、--header（可重复）、--timeout（默认 30.0）、--host、--port、--log-level、--mount-path 参数。（来源：server.py:486-553）
F-486: [server.py] CLI 中 --endpoint 模式先调用 _introspect_schema_sdl 获取 SDL，再调用 configure_runtime_endpoint；否则调用 configure_runtime。（来源：server.py:559-569）
F-487: [server.py] 启动时在 daemon 线程 "graphql-mcp-indexer" 中后台调用 ensure_schema_indexed(force=False)。（来源：server.py:582-586）
F-488: [server.py] 最后调用 mcp.run(transport=args.transport, mount_path=args.mount_path) 启动服务器。（来源：server.py:587）

### schema_indexer.py — 模块与常量

F-489: [schema_indexer.py] 导入 argparse、hashlib、json、dataclasses（asdict, dataclass）、pathlib.Path、typing（Iterable, List, Sequence）、numpy as np、graphql（GraphQLList, GraphQLNonNull, GraphQLObjectType, build_schema）、openai.OpenAI、dotenv.load_dotenv。（来源：schema_indexer.py:1-14）
F-490: [schema_indexer.py] DEFAULT_DATA_DIR = Path(__file__).parent / "data"。（来源：schema_indexer.py:15）
F-491: [schema_indexer.py] DEFAULT_SCHEMA_PATH = Path(__file__).parent / "schema.graphql"。（来源：schema_indexer.py:16）
F-492: [schema_indexer.py] DEFAULT_EMBED_MODEL = "text-embedding-3-small"。（来源：schema_indexer.py:17）

### schema_indexer.py — 数据结构

F-493: [schema_indexer.py] @dataclass class TypeField 包含三个字段：type_name: str、field_name: str、summary: str。（来源：schema_indexer.py:20-24）

### schema_indexer.py — Schema 展平函数

F-494: [schema_indexer.py] 函数 describe_type(graphql_type) -> str 递归将 GraphQL 类型转为字符串表示：GraphQLNonNull 添加 "!"，GraphQLList 包装为 "[]"。（来源：schema_indexer.py:27-32）
F-495: [schema_indexer.py] 函数 flatten_schema(schema_text: str) -> List[TypeField] 使用 build_schema 解析 SDL，遍历 schema.type_map，跳过 "__" 开头的内省类型和非 GraphQLObjectType，为每个字段生成 "Type.field(args) -> ReturnType" 签名，附加 description 作为 summary。（来源：schema_indexer.py:35-70）

### schema_indexer.py — OpenAIEmbedder 类

F-496: [schema_indexer.py] class OpenAIEmbedder：__init__(self, model=DEFAULT_EMBED_MODEL) 创建 OpenAI() 客户端并保存 model。（来源：schema_indexer.py:73-76）
F-497: [schema_indexer.py] OpenAIEmbedder.embed_many(self, texts: Sequence[str]) -> np.ndarray 调用 OpenAI embeddings API，返回 L2 归一化后的 float32 向量数组；空输入返回 zeros((0,0))。（来源：schema_indexer.py:78-84）
F-498: [schema_indexer.py] OpenAIEmbedder.embed_one(self, text: str) -> np.ndarray 调用 embed_many 并返回第一个向量。（来源：schema_indexer.py:86-87）
F-499: [schema_indexer.py] OpenAIEmbedder._normalize(vectors) 为静态方法，按行计算 L2 范数并归一化，零范数替换为 1.0 防止除零。（来源：schema_indexer.py:89-93）

### schema_indexer.py — EmbeddingStore 类

F-500: [schema_indexer.py] class EmbeddingStore：__init__(self, data_dir: Path, embedding_model: str) 设置 meta_path = data_dir/"metadata.json"、vectors_path = data_dir/"vectors.npz"，延迟加载 _vectors、_items、_meta。（来源：schema_indexer.py:96-105）
F-501: [schema_indexer.py] EmbeddingStore.is_ready(self) -> bool 检查 metadata.json 和 vectors.npz 是否存在。（来源：schema_indexer.py:107-108）
F-502: [schema_indexer.py] EmbeddingStore.load(self) -> dict 加载元数据和向量；若 embedding_model 不匹配则抛出 ValueError。（来源：schema_indexer.py:110-128）
F-503: [schema_indexer.py] EmbeddingStore.save(self, vectors, items, schema_sha, schema_source=None) -> dict 创建 data_dir，保存向量为 npz 压缩文件、元数据为 JSON（含 embedding_model、schema_sha、items、可选 schema_source）。（来源：schema_indexer.py:130-153）
F-504: [schema_indexer.py] EmbeddingStore.search(self, query_vector, limit=5) -> list[dict] 通过矩阵乘法计算余弦相似度（向量已归一化），返回 top-N 结果，每项含 type、field、summary、score。（来源：schema_indexer.py:155-173）

### schema_indexer.py — 索引构建函数

F-505: [schema_indexer.py] 函数 compute_schema_sha(schema_text: str) -> str 返回 schema_text 的 SHA-256 十六进制摘要。（来源：schema_indexer.py:175-176）
F-506: [schema_indexer.py] 函数 index_schema_text(schema_text, *, data_dir, embed_model, embedder, store, schema_source) -> dict 调用 flatten_schema、embed_many、compute_schema_sha、store.save，返回含 count 的元数据。（来源：schema_indexer.py:178-201）
F-507: [schema_indexer.py] 函数 index_schema(schema_path, *, data_dir, embed_model, embedder, store, schema_source) -> dict 读取 schema_path 文件内容，自动构造 {"kind":"file","path":...} 源信息，委托给 index_schema_text。（来源：schema_indexer.py:204-225）
F-508: [schema_indexer.py] 函数 ensure_index_text(schema_text, *, schema_source, data_dir, embed_model, embedder, store, force=False) -> dict 检查索引是否存在且 schema_sha/schema_source 未变，未变则直接返回，否则重建。（来源：schema_indexer.py:228-272）
F-509: [schema_indexer.py] 函数 ensure_index(schema_path, *, data_dir, embed_model, embedder, store, force=False) -> dict 文件模式版本，读取 schema_path 计算 sha，委托给 index_schema。（来源：schema_indexer.py:275-322）
F-510: [schema_indexer.py] 函数 search_index(query, data_dir, embed_model, embedder, limit=5) -> list[dict] 加载 store、嵌入查询、搜索，并为每个结果附加 schema_sha。（来源：schema_indexer.py:325-340）

### schema_indexer.py — CLI

F-511: [schema_indexer.py] 函数 cli(argv=None) -> int 提供两个子命令：index（索引 schema）和 search（自然语言搜索，--limit 默认 5，上限 20）。（来源：schema_indexer.py:343-396）
F-512: [schema_indexer.py] cli 的 search 子命令先调用 ensure_index 再调用 search_index，以 JSON 格式输出结果；无子命令时默认执行 index_schema 并打印索引统计。（来源：schema_indexer.py:367-396）

### schema.graphql — Query 类型

F-513: [schema.graphql] type Query 定义字段：user(id: ID!): User。（来源：schema.graphql:4）
F-514: [schema.graphql] type Query 定义字段：users(limit: Int = 10, offset: Int = 0): [User!]!。（来源：schema.graphql:5）
F-515: [schema.graphql] type Query 定义字段：usersConnection(first: Int = 10, after: ID): UserConnection!。（来源：schema.graphql:6）
F-516: [schema.graphql] type Query 定义字段：usersCount: Int!。（来源：schema.graphql:7）
F-517: [schema.graphql] type Query 定义字段：order(id: ID!): Order。（来源：schema.graphql:8）
F-518: [schema.graphql] type Query 定义字段：orders(status: OrderStatus, limit: Int = 10): [Order!]!。（来源：schema.graphql:9）
F-519: [schema.graphql] type Query 定义字段：ordersConnection(first: Int = 10, after: ID, status: OrderStatus): OrderConnection!。（来源：schema.graphql:10）
F-520: [schema.graphql] type Query 定义字段：ordersCount(status: OrderStatus): Int!。（来源：schema.graphql:11）
F-521: [schema.graphql] type Query 定义字段：product(id: ID!): Product。（来源：schema.graphql:12）
F-522: [schema.graphql] type Query 定义字段：products(limit: Int = 10, offset: Int = 0): [Product!]!。（来源：schema.graphql:13）
F-523: [schema.graphql] type Query 定义字段：productsConnection(first: Int = 10, after: ID): ProductConnection!。（来源：schema.graphql:14）
F-524: [schema.graphql] type Query 定义字段：productsCount: Int!。（来源：schema.graphql:15）
F-525: [schema.graphql] type Query 定义字段：searchProducts(term: String!, limit: Int = 10): [Product!]!。（来源：schema.graphql:16）
F-526: [schema.graphql] type Query 定义字段：category(id: ID!): Category。（来源：schema.graphql:17）
F-527: [schema.graphql] type Query 定义字段：categories: [Category!]!。（来源：schema.graphql:18）
F-528: [schema.graphql] type Query 定义字段：categoriesCount: Int!。（来源：schema.graphql:19）
F-529: [schema.graphql] type Query 定义字段：reviewsCount: Int!。（来源：schema.graphql:20）

### schema.graphql — Connection 分页类型

F-530: [schema.graphql] type PageInfo（描述"Pagination metadata for cursor-based navigation"）包含字段：hasNextPage: Boolean!、hasPreviousPage: Boolean!、startCursor: ID、endCursor: ID。（来源：schema.graphql:23-29）
F-531: [schema.graphql] type UserConnection 包含：totalCount: Int!、pageInfo: PageInfo!、edges: [UserEdge!]!。（来源：schema.graphql:31-36）
F-532: [schema.graphql] type UserEdge 包含：cursor: ID!（描述为游标）、node: User!。（来源：schema.graphql:38-44）
F-533: [schema.graphql] type ProductConnection 包含：totalCount: Int!、pageInfo: PageInfo!、edges: [ProductEdge!]!。（来源：schema.graphql:46-54）
F-534: [schema.graphql] type ProductEdge 包含：cursor: ID!、node: Product!。（来源：schema.graphql:56-62）
F-535: [schema.graphql] type OrderConnection 包含：totalCount: Int!、pageInfo: PageInfo!、edges: [OrderEdge!]!。（来源：schema.graphql:64-72）
F-536: [schema.graphql] type OrderEdge 包含：cursor: ID!、node: Order!。（来源：schema.graphql:74-80）

### schema.graphql — Mutation 类型

F-537: [schema.graphql] type Mutation 定义字段：placeOrder(input: PlaceOrderInput!): OrderConfirmation!。（来源：schema.graphql:82-84）

### schema.graphql — 业务对象类型

F-538: [schema.graphql] type User 包含字段：id: ID!、name: String!、email: String!、profile: UserProfile、address: Address、company: Company、orders: [Order!]!、wishlist: [Product!]!、reviews: [Review!]!。（来源：schema.graphql:86-96）
F-539: [schema.graphql] type UserProfile 包含：bio: String、joinedAt: String!、preferences: Preferences。（来源：schema.graphql:98-102）
F-540: [schema.graphql] type Preferences 包含：newsletter: Boolean!、favoriteCategories: [Category!]!。（来源：schema.graphql:104-107）
F-541: [schema.graphql] type Company 包含：id: ID!、name: String!、address: Address。（来源：schema.graphql:109-113）
F-542: [schema.graphql] type Address 包含：id: ID!、line1: String!、line2: String、city: String!、region: String、postalCode: String!、country: String!。（来源：schema.graphql:115-123）
F-543: [schema.graphql] type Product 包含：id: ID!、name: String!、description: String、price: Float!、inStock: Boolean!、tags: [String!]!、category: Category、reviews: [Review!]!、related: [Product!]!、inventory: [InventoryLocation!]!。（来源：schema.graphql:125-136）
F-544: [schema.graphql] type Review 包含：id: ID!、rating: Int!、title: String、body: String、author: User!、product: Product!、createdAt: String!。（来源：schema.graphql:138-146）
F-545: [schema.graphql] type Category 包含：id: ID!、name: String!、parent: Category、children: [Category!]!、products: [Product!]!。（来源：schema.graphql:148-154）
F-546: [schema.graphql] type Order 包含：id: ID!、status: OrderStatus!、items: [OrderItem!]!、total: Float!、placedAt: String!、shipment: Shipment、payment: Payment、discounts: [Discount!]!、notes: [String!]!。（来源：schema.graphql:156-166）
F-547: [schema.graphql] type OrderItem 包含：product: Product!、quantity: Int!、subtotal: Float!、appliedDiscounts: [Discount!]!。（来源：schema.graphql:168-173）
F-548: [schema.graphql] type Shipment 包含：carrier: Carrier!、trackingNumber: String!、address: Address!、trackingEvents: [TrackingEvent!]!。（来源：schema.graphql:175-180）
F-549: [schema.graphql] type Carrier 包含：id: ID!、name: String!、phone: String。（来源：schema.graphql:182-186）
F-550: [schema.graphql] type TrackingEvent 包含：status: String!、timestamp: String!、location: String。（来源：schema.graphql:188-192）
F-551: [schema.graphql] type Payment 包含：id: ID!、method: PaymentMethod!、status: PaymentStatus!、amount: Float!、processedAt: String、billingAddress: Address。（来源：schema.graphql:194-201）
F-552: [schema.graphql] type Discount 包含：code: String!、amount: Float!、description: String。（来源：schema.graphql:203-207）
F-553: [schema.graphql] type InventoryLocation 包含：id: ID!、name: String!、status: InventoryStatus!、quantity: Int!、address: Address。（来源：schema.graphql:209-215）

### schema.graphql — Input 类型与返回类型

F-554: [schema.graphql] input PlaceOrderInput 包含：userId: ID!、items: [PlaceOrderItemInput!]!、note: String、couponCode: String。（来源：schema.graphql:217-222）
F-555: [schema.graphql] input PlaceOrderItemInput 包含：productId: ID!、quantity: Int!。（来源：schema.graphql:224-227）
F-556: [schema.graphql] type OrderConfirmation 包含：id: ID!、estimatedDelivery: String!、message: String、order: Order。（来源：schema.graphql:229-234）

### schema.graphql — Enum 类型

F-557: [schema.graphql] enum OrderStatus 值：PENDING、SHIPPED、DELIVERED、CANCELLED。（来源：schema.graphql:236-241）
F-558: [schema.graphql] enum PaymentStatus 值：AUTHORIZED、CAPTURED、FAILED、REFUNDED。（来源：schema.graphql:243-248）
F-559: [schema.graphql] enum PaymentMethod 值：CARD、PAYPAL、BANK_TRANSFER。（来源：schema.graphql:250-254）
F-560: [schema.graphql] enum InventoryStatus 值：IN_STOCK、LOW_STOCK、OUT_OF_STOCK。（来源：schema.graphql:256-260）

### test_graphql_server/server.py — 测试服务器

F-561: [test_server.py] 导入 argparse、json、http.server（BaseHTTPRequestHandler, HTTPServer）、pathlib.Path、typing.Any、graphql（build_schema, graphql_sync）。（来源：test_graphql_server/server.py:1-7）
F-562: [test_server.py] 函数 _json_response(handler, status, payload) 发送 JSON HTTP 响应，设置 CORS 头（Access-Control-Allow-Origin: *）。（来源：test_graphql_server/server.py:10-19）
F-563: [test_server.py] 函数 _read_json(handler) 从请求体读取 JSON。（来源：test_graphql_server/server.py:22-27）
F-564: [test_server.py] class Root 在 __init__ 中构造内存数据：addresses（4条）、companies（2条）、categories（5条，含层级关系）、products（5条，含 related/inventory）、discounts（2条）、carriers（2条）、shipments（2条）、payments（2条）、orders（2条）、user_store（3条）、reviews（4条），并建立双向关联。（来源：test_graphql_server/server.py:30-421）
F-565: [test_server.py] Root._normalize_id(value, prefix) 静态方法，若 value 不以 prefix 开头则添加前缀。（来源：test_graphql_server/server.py:423-427）
F-566: [test_server.py] Root 定义 Query resolver 方法：user(info, id)、users(info, limit=10, offset=0)、order(info, id)、orders(info, status=None, limit=10)、product(info, id)、products(info, limit=10, offset=0)、searchProducts(info, term, limit=10)、category(info, id)、categories(info)。（来源：test_graphql_server/server.py:429-474）
F-567: [test_server.py] Root 定义 count 方法：usersCount、productsCount、ordersCount(status=None)、categoriesCount、reviewsCount，均返回 int。（来源：test_graphql_server/server.py:478-498）
F-568: [test_server.py] Root._build_connection(items, first=10, after=None) 构建 Connection 响应，游标为 item ID，first 上限 100，返回 totalCount/pageInfo/edges。（来源：test_graphql_server/server.py:502-545）
F-569: [test_server.py] Root 定义 Connection resolver：usersConnection(first=10, after=None)、productsConnection(first=10, after=None)、ordersConnection(first=10, after=None, status=None)。（来源：test_graphql_server/server.py:547-562）
F-570: [test_server.py] Root.placeOrder(info, input) 实现下单逻辑：验证用户和商品、计算小计、应用优惠券折扣、返回 OrderConfirmation。（来源：test_graphql_server/server.py:564-617）
F-571: [test_server.py] 函数 _format_result(result) 将 graphql_sync 结果格式化为 {"data":..., "errors":...} 字典。（来源：test_graphql_server/server.py:620-632）
F-572: [test_server.py] 函数 make_handler(schema_sdl) 创建闭包 Handler 类（继承 BaseHTTPRequestHandler），处理 OPTIONS（CORS 预检）、GET /healthz、POST /graphql（执行 graphql_sync）。（来源：test_graphql_server/server.py:635-681）
F-573: [test_server.py] 函数 main() 解析 --host（默认 127.0.0.1）、--port（默认 4000）、--schema（默认 ../schema.graphql），启动 HTTPServer。（来源：test_graphql_server/server.py:684-701）

## AI WG — MCP README

F-574: [mcp/README.md] 该 MCP 服务器是 Docker 化的 Python 服务，为 LLM 索引 GraphQL schema，按 type->field 存储 OpenAI embeddings，支持快速查找和 run_query 执行。（来源：mcp/README.md:1-3）
F-575: [mcp/README.md] 架构组件：schema.graphql（电商示例）、schema_indexer.py（展平为 type.field 签名并嵌入）、server.py（暴露 list_types 和 run_query 工具）、data/ 目录持久化（metadata.json + vectors.npz，已 gitignore）。（来源：mcp/README.md:5-10）
F-576: [mcp/README.md] Setup 需要创建 .env 文件设置 OPENAI_API_KEY，使用 venv 安装 requirements.txt。（来源：mcp/README.md:13-21）
F-577: [mcp/README.md] Docker 方式通过 docker compose up --build 启动，MCP 服务器在 http://127.0.0.1:8000/sse；可通过 GRAPHQL_ENDPOINT_URL 环境变量连接测试 endpoint。（来源：mcp/README.md:23-40）
F-578: [mcp/README.md] CLI 索引命令：python3 schema_indexer.py（默认使用 schema.graphql 和 data/）；搜索命令：python3 schema_indexer.py search "query" [--limit N]。（来源：mcp/README.md:42-53）
F-579: [mcp/README.md] MCP 服务器运行支持 --transport（sse/streamable-http）、--schema、--endpoint、--header（可重复）、--host、--port、--log-level、--mount-path 参数。（来源：mcp/README.md:55-67）
F-580: [mcp/README.md] list_types(query, limit=5) 工具对 type.field 签名进行模糊搜索，Query 字段优先，包含 query_template 和 selection_hint。（来源：mcp/README.md:69）
F-581: [mcp/README.md] run_query(query) 工具在 --endpoint 模式下代理查询，否则在本地 schema 上验证/运行（无 resolver，数据为 null）。（来源：mcp/README.md:70）
F-582: [mcp/README.md] 索引和查询均使用 text-embedding-3-small 模型（默认）。（来源：mcp/README.md:71）
F-583: [mcp/README.md] 支持 FASTMCP_ 前缀环境变量（FASTMCP_HOST、FASTMCP_PORT、FASTMCP_LOG_LEVEL）覆盖默认值；MCP_INSTRUCTIONS 环境变量可覆盖服务器指令。（来源：mcp/README.md:97-100）
F-584: [mcp/README.md] 可通过 npx @modelcontextprotocol/inspector 连接 SSE 服务器进行测试。（来源：mcp/README.md:102-113）
F-585: [mcp/README.md] 测试服务器位于 test_graphql_server/，默认端口 4000，run_query 返回真实数据，list_types 仍需 OPENAI_API_KEY。（来源：mcp/README.md:115-128）
F-586: [mcp/README.md] 可配置到 Claude Desktop/CLI，使用 claude mcp add --transport sse 命令或 JSON 配置文件。（来源：mcp/README.md:130-154）

## AI WG — 语义内省 RFC

### 元信息与动机

F-587: [semantic-introspection.md] RFC 作者为 Pascal Senn 和 Michael Staib（ChilliCream）。（来源：semantic-introspection.md:7-8）
F-588: [semantic-introspection.md] 摘要提议扩展 GraphQL 内省系统，通过标准化 `__search` 端点和相关类型实现 schema 能力的语义搜索，使 AI agent 和 LLM 能用自然语言查询发现相关 API 能力。（来源：semantic-introspection.md:14-21）
F-589: [semantic-introspection.md] RFC 指出 MCP 的工具抽象与 GraphQL 高度相似：读数据的 MCP 工具等价于 Query 字段，写数据的工具等价于 Mutation 字段；MCP 用 JSON Schema 定义输入输出，GraphQL 用类型系统。（来源：semantic-introspection.md:32-39）
F-590: [semantic-introspection.md] RFC 指出 MCP 工具本质上是具有类型化输入输出的可调用操作，与 GraphQL 自诞生以来提供的能力一致；差异主要是表面的（JSON Schema vs 类型系统、扁平 vs 图组合）。（来源：semantic-introspection.md:38-43）
F-591: [semantic-introspection.md] RFC 提出问题：GraphQL 现有 schema 和内省能力能否扩展为 AI agent 的一等工具提供者，包括 prompts。（来源：semantic-introspection.md:45-52）
F-592: [semantic-introspection.md] 当前 LLM 与 GraphQL API 交互的三种方式：遍历完整 schema（昂贵）、依赖预训练知识（脆弱不可泛化）、接收手工工具描述（每 API 需人工）。（来源：semantic-introspection.md:56-63）
F-593: [semantic-introspection.md] 机会：通过语义搜索扩展内省，实现"学一次，到处用"模式——LLM 学一次规范，API 提供者索引一次 schema，无需每 API 训练或自定义工具定义。（来源：semantic-introspection.md:68-79）

### 提议 1：语义搜索内省（__search）

F-594: [semantic-introspection.md] 提议在 Query 类型上扩展 `__search` 字段，参数包括：query: String!（自然语言查询）、first: Int! = 10（最大结果数）、after: String（前向分页游标）、minScore: Float（可选最低分数），返回 [__SearchResult!]!。（来源：semantic-introspection.md:95-133）
F-595: [semantic-introspection.md] __search 的 query 参数应被解释为描述所需能力的自然语言；结果应按 score 降序排列。（来源：semantic-introspection.md:98-104）
F-596: [semantic-introspection.md] __search 的 after 参数为不透明游标，提供时结果必须从该游标指示位置之后开始；游标值必须从之前 __SearchResult 的 cursor 字段获取。（来源：semantic-introspection.md:117-124）
F-597: [semantic-introspection.md] __search 的 minScore 参数提供时，所有返回结果必须 score >= minScore。（来源：semantic-introspection.md:126-131）
F-598: [semantic-introspection.md] 分页采用简单快进模型：将最后结果的 cursor 作为 after 参数获取下一页；返回结果少于 first 时表示无更多页。（来源：semantic-introspection.md:136-138）

### __SearchResult 类型

F-599: [semantic-introspection.md] 定义 type __SearchResult，包含字段 coordinate: String!（schema 坐标，如 "Query.user"）、definition: __SchemaDefinition!（匹配的定义）、pathsToRoot: [[String!]!]!（从根字段到匹配定义的路径列表）、score: Float（相关性分数，应在 [0.0, 1.0] 范围）、cursor: String!（分页游标）。（来源：semantic-introspection.md:142-183）
F-600: [semantic-introspection.md] pathsToRoot 字段提供从根字段到匹配定义的路径列表，每条路径是从根到匹配定义的 schema 坐标序列；若定义可通过多条路径到达，可返回多条路径，但不保证穷尽。（来源：semantic-introspection.md:190-219）
F-601: [semantic-introspection.md] 若匹配定义本身是根字段，pathsToRoot 路径只包含单个元素。（来源：semantic-introspection.md:221-227）
F-602: [semantic-introspection.md] 编者注指出 pathsToRoot 字段放在 __SearchResult 上，但其可能更应属于 schema 定义类型本身（如 __Field、__Type），需进一步讨论。（来源：semantic-introspection.md:186-188）

### __SchemaDefinition 联合类型

F-603: [semantic-introspection.md] 定义 union __SchemaDefinition = __Type | __Field | __InputValue | __EnumValue | __Directive，表示可通过语义搜索发现的所有可内省 schema 定义的联合。（来源：semantic-introspection.md:231-242）

### 提议 2：坐标查找内省（__definitions）

F-604: [semantic-introspection.md] 提议在 Query 类型上扩展 `__definitions` 字段，参数 coordinates: [String!]!（schema 坐标列表），返回 [__SchemaDefinition!]!，按输入坐标顺序返回解析结果。（来源：semantic-introspection.md:254-268）
F-605: [semantic-introspection.md] __definitions 通过 schema 坐标直接查找定义，消除通过 __schema、__type 等遍历内省图的需要；可独立于 __search 使用。（来源：semantic-introspection.md:244-253）
F-606: [semantic-introspection.md] 编者注指出 __definitions 与 __search 自然配合形成"发现-解析"两步工作流，但其本身也是通用内省原语，任何处理 schema 坐标的工具都可受益。（来源：semantic-introspection.md:368-371）

### 索引要求

F-607: [semantic-introspection.md] 遵循此规范的实现必须维护活跃 schema 的索引；可使用任意向量化或索引策略；应至少索引类型名、字段名和描述。（来源：semantic-introspection.md:373-381）

### 潜在扩展 A：使用示例

F-608: [semantic-introspection.md] 潜在扩展提议 type __Example，包含 operation: String!（示例 GraphQL 操作）和 description: String（可读描述）。（来源：semantic-introspection.md:453-467）
F-609: [semantic-introspection.md] 潜在扩展提议在 __Type、__Field、__InputValue、__EnumValue、__Directive 上扩展 examples: [__Example!] 字段，提供使用示例。（来源：semantic-introspection.md:469-502）

### 潜在扩展 B：MCP 风格 Prompts

F-610: [semantic-introspection.md] 潜在扩展提议在 Query 上扩展 `__prompts: [__Prompt!]!` 字段，检索 schema 中定义的所有 prompt 模板。（来源：semantic-introspection.md:510-517）
F-611: [semantic-introspection.md] 定义 type __Prompt，包含 name: String!（唯一标识）、description: String（可读描述）、arguments: [__InputValue!]!（可自定义参数）。（来源：semantic-introspection.md:519-537）

### 开放问题

F-612: [semantic-introspection.md] 开放问题包括：此方法对 LLM 是否实际有效；语义搜索的速率限制和访问控制安全指导；`capabilities` 命名可能与主仓库中已有的 Semantic Introspection RFC 冲突。（来源：semantic-introspection.md:542-548）

---

## 官网生态信息

### 首页与入门

F-613: [官网首页] GraphQL 是一种用于 API 的开源查询语言和服务端运行时，提供强类型 schema 定义数据之间的关系，使 API 更灵活和可预测；不绑定特定数据库或存储引擎，可与现有代码和数据协同工作。（来源：https://graphql.org/）
F-614: [官网首页] Facebook 移动应用自 2012 年起使用 GraphQL；GraphQL 规范于 2015 年开源；现由 GraphQL 基金会支持，该基金会自 2018 年起由非营利组织 Linux 基金会托管。（来源：https://graphql.org/）
F-615: [官网首页] GraphQL 五大设计支柱：Product-centric（产品中心）、Hierarchical（分层）、Strong-typing（强类型）、Client-specified response（客户端指定响应）、Self-describing（自描述）。（来源：https://graphql.org/）
F-616: [官网首页] GraphQL 六大优势：Precision（精确获取所需数据，无过度获取或获取不足）、Optimization（单次请求获取多个资源，跟随数据间关系）、Productivity（社区构建的强大工具提升效率，如 GraphiQL）、Consistency（围绕类型和字段而非 endpoint 构建，确保数据一致性和自文档化）、Versionless（无版本演进 API，通过弃用字段保持 API 清洁）、Integration（存储无关，可集成数据库、REST API 和第三方服务到统一数据层）。（来源：https://graphql.org/）
F-617: [官网首页] GraphQL fragments 支持数据共置（Data Colocation）：可在组件附近定义每个组件的数据需求，并通过单个查询满足。（来源：https://graphql.org/）
F-618: [官网首页] GraphiQL 是 GraphQL 社区构建的开源交互式查询编辑器，支持 Ctrl+Space 打开自动补全菜单、Ctrl+Enter 运行查询。（来源：https://graphql.org/）
F-619: [入门介绍] GraphQL 是 API 查询语言和服务端运行时，使用自定义类型系统执行查询；规范于 2015 年开源，已在多种编程语言中实现；不绑定特定数据库或存储引擎，由现有代码和数据支撑。（来源：https://graphql.org/learn/introduction/）
F-620: [入门介绍] GraphQL 服务通过定义类型及其字段、然后为每个字段编写提供所需数据的函数来创建。（来源：https://graphql.org/learn/introduction/）
F-621: [入门介绍] GraphQL 服务接收查询后首先检查查询，确保它仅引用 API 已定义的类型和字段，然后运行提供的函数生成结果。（来源：https://graphql.org/learn/introduction/）
F-622: [入门介绍] 客户端可构造镜像所需数据结构的 GraphQL 查询，单次请求获取预期形状的数据，无需关心底层数据源。（来源：https://graphql.org/learn/introduction/）
F-623: [入门介绍] GraphQL 允许 API 无版本演进：添加新字段和类型不影响现有查询；通过 `@deprecated` 弃用过时字段，确定不再使用后移除。（来源：https://graphql.org/learn/introduction/）
F-624: [入门介绍] 学习指南中的查询编辑器是交互式的；下一步学习路径为 Schemas and Types（类型系统），也可参加官方培训课程深入学习。（来源：https://graphql.org/learn/introduction/）

### Python 客户端库

F-625: [Python 客户端库] **Ariadne Codegen** — 从任意 schema 和查询生成完全类型化的 Python GraphQL 客户端；通过 `pip install ariadne-codegen` 安装；在 pyproject.toml 中配置 queries_path 和 remote_schema_url 后运行 ariadne-codegen 生成异步客户端代码；URL: https://github.com/mirumee/ariadne-codegen（来源：https://graphql.org/community/tools-and-libraries/?tags=python&tags=client）
F-626: [Python 客户端库] **GQL** — Python 中的 GraphQL 客户端；URL: https://github.com/graphql-python/gql（来源：https://graphql.org/community/tools-and-libraries/?tags=python&tags=client）
F-627: [Python 客户端库] **graphql-query** — 完整的 Python GraphQL 查询字符串生成库；通过 `pip install graphql_query` 安装；提供 Operation、Query、Field、Argument、Variable、Directive 等构建块渲染 GraphQL 查询字符串；文档位于 https://denisart.github.io/graphql-query；URL: https://denisart.github.io/graphql-query/（来源：https://graphql.org/community/tools-and-libraries/?tags=python&tags=client）
F-628: [Python 客户端库] **python-graphql-client** — 面向 Python 2.7+ 的简单 GraphQL 客户端；URL: https://github.com/prisma/python-graphql-client（来源：https://graphql.org/community/tools-and-libraries/?tags=python&tags=client）
F-629: [Python 客户端库] **ql** — 基于 pydantic 的非侵入式 Python GraphQL 客户端，通过 pydantic 类进行类型验证，提供安全简单的 GraphQL API 查询方式；支持 Python 对象转有效 GraphQL 字符串、标量查询响应和类型安全；通过 `pip3 install pydantic-graphql` 安装；URL: https://dsal3389.github.io/ql/（来源：https://graphql.org/community/tools-and-libraries/?tags=python&tags=client）
F-630: [Python 客户端库] **Qlient** — 快速现代的 GraphQL 客户端，以简洁为设计理念；通过 `pip install qlient` 安装；提供 HTTPClient 和 GraphQLResponse，支持链式字段查询和 _fields 参数指定返回字段；URL: https://github.com/qlient-org/python-qlient（来源：https://graphql.org/community/tools-and-libraries/?tags=python&tags=client）
F-631: [Python 客户端库] **sgqlc** — 简单的 Python GraphQL 客户端，支持根据 GraphQL schema 中定义的类型生成代码；URL: https://github.com/profusion/sgqlc（来源：https://graphql.org/community/tools-and-libraries/?tags=python&tags=client）

### Python 服务端库

F-632: [Python 服务端库] **Ariadne** — 使用 schema-first 方式实现 GraphQL 服务器的 Python 库；支持同步和异步查询执行；内置查询成本验证、性能追踪等常见 GraphQL 服务器问题解决方案；API 简单易扩展或替换；通过 `pip install ariadne` 安装，可使用 uvicorn 运行 ASGI 应用；URL: https://ariadnegraphql.org/（来源：https://graphql.org/community/tools-and-libraries/?tags=server&tags=python）
F-633: [Python 服务端库] **Django Graphbox** — 用于轻松构建 Django 模型基本 CRUD 操作 GraphQL API 的包；通过 `pip install django-graphbox` 安装；使用 SchemaBuilder 添加 Django 模型，自动生成 schema query 和 mutation 类；支持认证、过滤器、验证等高级功能；URL: https://90horasporsemana.com/graphbox/（来源：https://graphql.org/community/tools-and-libraries/?tags=server&tags=python）
F-634: [Python 服务端库] **Graphene Django CRUDDALS** — 将 Django 模型转换为包含所有 CRUD 操作的完整 GraphQL API；通过 `pip install graphene-django-cruddals` 安装；定义继承 DjangoModelCruddals 的类即可自动生成 Schema、Query 和 Mutation；URL: https://graphene-django-cruddals.readthedocs.io/en/latest/（来源：https://graphql.org/community/tools-and-libraries/?tags=server&tags=python）
F-635: [Python 服务端库] **Graphene** — 用于构建 GraphQL API 的 Python 库；通过 `pip install graphene` 安装；提供 Relay、Django、SQLAlchemy 和 Google App Engine 的绑定；URL: http://graphene-python.org/（来源：https://graphql.org/community/tools-and-libraries/?tags=server&tags=python）
F-636: [Python 服务端库] **Strawberry** — 使用现代 Python 特性（如类型注解）实现 code-first GraphQL 服务器的 Python 库；通过 `pip install strawberry-graphql` 安装；使用 @strawberry.type 和 @strawberry.field 装饰器定义 schema；提供 ASGI、Flask 和 Django 视图，以及 dataloaders 和 tracing 工具；运行 `strawberry server app` 启动服务器；URL: https://strawberry.rocks/（来源：https://graphql.org/community/tools-and-libraries/?tags=server&tags=python）
F-637: [Python 服务端库] **Tartiflette** — 面向 Python 3.6+ 的 asyncio GraphQL API 构建库；通过 `pip install tartiflette` 安装；使用 @Resolver 装饰器定义异步解析器；提供 tartiflette-aiohttp HTTP 包装器；URL: https://tartiflette.io/（来源：https://graphql.org/community/tools-and-libraries/?tags=server&tags=python）

### 后端与前端资源

F-638: [后端资源] PHP 生态后端工具包括：API Platform、Gato GraphQL、GraPHPinator、graphql-attribute-schema、graphql-php、graphql-relay-php、GraphQLBundle、GraphQLite、Lighthouse、Railt、serge、Siler、WPGraphQL。（来源：https://graphql.org/resources/backend/）
F-639: [后端资源] Go 生态后端工具包括：99designs/gqlgen、appointy/jaal、EGGQL、graph-gophers/graphql-go、graphql-go、graphql-go-tools、graphql-relay-go、samsarahq/thunder。（来源：https://graphql.org/resources/backend/）
F-640: [后端资源] C#/.NET 生态后端工具包括：Entity GraphQL、graphql-dotnet、graphql-net、Hot Chocolate、NGraphQL。（来源：https://graphql.org/resources/backend/）
F-641: [后端资源] Java/Kotlin 生态后端工具包括：Domain Graph Service (DGS) Framework、GraphQL Spring Boot、graphql-calculator、graphql-java、graphql-kotlin、Jimmer、KGraphQL、MicroProfile GraphQL、Spring for GraphQL、Viaduct。（来源：https://graphql.org/resources/backend/）
F-642: [后端资源] JavaScript 生态后端工具包括：Apollo Server、GraphQL-SSE、GraphQL-WS、graphql-yoga、GraphQL.js、GraphQLBox server、Grats、Mercurius、Pylon。（来源：https://graphql.org/resources/backend/）
F-643: [后端资源] 其他语言后端工具：Ruby（Agoo、graphql-ruby、Rails GraphQL）、Rust（Async-graphql、graphql-rust/juniper）、Scala（Caliban、Sangria）、Elixir（absinthe、graphql-elixir）、Haskell（Morpheus GraphQL、Mu-Haskell with Mu-GraphQL）、Swift/Objective-C（Graphiti、GraphZahl）、C/C++（cppgraphqlgen-schemagen）、Clojure（alumbra、graphql-clj、lacinia）、OCaml（ocaml-graphql-server）、Erlang（graphql-erlang）、R（ghql）、Perl（graphql-perl）、Groovy（gorm-graphql）、D（graphqld）、Ballerina（ballerina-graphql）。（来源：https://graphql.org/resources/backend/）
F-644: [前端资源] JavaScript 生态前端客户端工具包括：Apollo Client、AWS Amplify、gq-loader、GQty、Grafoo、GraphQL Request、graphql-hooks、graphql-ts-client、GraphQLBox client、graphqurl、Lokka、nanographql、Relay、urql、zodql。（来源：https://graphql.org/resources/frontend/#documentation）
F-645: [前端资源] Swift/Objective-C 生态前端工具包括：Apollo iOS、Graphaello、GraphQL iOS、SwiftGraphQL。（来源：https://graphql.org/resources/frontend/#documentation）
F-646: [前端资源] Go 生态前端客户端工具包括：genqlient、go-graphql-client、graphql（shurcooL）、machinebox/graphql。（来源：https://graphql.org/resources/frontend/#documentation）
F-647: [前端资源] C#/.NET 生态前端客户端工具包括：graphql-net-client、GraphQL.Client、Linq2GraphQL、SAHB.GraphQLClient、Strawberry Shake、ZeroQL。（来源：https://graphql.org/resources/frontend/#documentation）
F-648: [前端资源] 其他前端工具：Flutter（Ferry）、Rust（cynic、gql_client）、Java/Kotlin（Apollo Kotlin、Nodes）、Elm（dillonkearns/elm-graphql）、PowerShell（PSGraphQL）、Julia（Diana.jl、GraphQLClient.jl）、Elixir（common_graphql_client、Neuron）、Clojure（regraph）、Haskell（morpheus-graphql-client）、C/C++（cppgraphqlgen-clientgen）、Ballerina（ballerina-graphql）。（来源：https://graphql.org/resources/frontend/#documentation）
F-649: [前端资源] 前端资源页面列出的 Python 客户端库与社区工具库页面一致：Ariadne Codegen、GQL、graphql-query、python-graphql-client、ql、Qlient、sgqlc，共 7 个。（来源：https://graphql.org/resources/frontend/#documentation）
F-650: [后端资源] 后端资源页面列出的 Python 服务端库与社区工具库页面一致：Ariadne、Django Graphbox、Graphene、Graphene Django CRUDDALS、Strawberry、Tartiflette，共 6 个。（来源：https://graphql.org/resources/backend/）
F-651: [后端资源] 后端资源页面还包含特色视频（如"A GraphQL Framework for Non-JS Servers"、"Build a Full GraphQL Backend in Under 5 Minutes"、"GraphQL Servers"等）和 GraphQL 博客文章（如"GraphQL: A data query language"）。（来源：https://graphql.org/resources/backend/）
F-652: [前端资源] 前端资源页面还包含特色视频（如"Apollo Client: Put GraphQL Data in Your UI"、"Building Native Mobile Apps with GraphQL"等）和 GraphQL 博客文章（如"Subscriptions in GraphQL and Relay"、"Mocking your server is easy with GraphQL"、"Improving Latency with @defer and @stream Directives"）。（来源：https://graphql.org/resources/frontend/#documentation）

### GraphQL + AI

F-653: [GraphQL+AI] GraphQL AI 页面标语为"The API language for humans and agents"（面向人类和智能体的 API 语言）；能访问 GraphQL endpoint 的 agent 可读取类型、字段参数和文档，然后精确请求所需字段，无需额外发布和保持同步的内容。（来源：https://graphql.org/ai/）
F-654: [GraphQL+AI] GraphQL 用于 AI 的三大核心特性：Self-describing schemas（自描述 schema 让 agent 发现 API）、Invalid queries fail validation before they execute（无效查询在执行前验证失败）、Field selection keeps responses to what the query asked for（字段选择使响应仅包含查询请求的内容）。（来源：https://graphql.org/ai/）
F-655: [GraphQL+AI] GraphQL 从第一天起就为机器可读而设计；其内省系统、类型安全和可组合性为工具和客户端而构建，恰好满足 agent 理解 API 能力并请求部分数据的需求。（来源：https://graphql.org/ai/）
F-656: [GraphQL+AI] Self-describing 特性：每个 GraphQL API 内置类型系统；AI agent 查询 `__schema` 即可立即了解可用数据、字段接受的参数及类型关系，无需手写工具描述；支持自动生成 LLM 工具定义、agent 运行时发现能力、从 schema 生成 MCP 服务器。（来源：https://graphql.org/ai/）
F-657: [GraphQL+AI] Strongly typed 特性：每个字段有已知的验证类型；LLM 可自信地推理输入和输出；错误猜测返回命名的验证错误供 agent 修正，而非返回 200 但携带错误数据；类型系统减少 LLM 产生幻觉的 API 交互。（来源：https://graphql.org/ai/）
F-658: [GraphQL+AI] Composable 特性：AI agent 可动态组合精确查询——请求嵌套数据、使用别名、应用过滤器；单个 endpoint 服务于 schema 允许的任何数据访问模式，无需客户端拼接；响应大小跟随查询而非 endpoint。（来源：https://graphql.org/ai/）
F-659: [GraphQL+AI] GraphQL 与 REST+OpenAPI 对比——Discovery：GraphQL 内省来自 endpoint 本身（在 agent 已调用的同一 endpoint 上响应，无需定位或保持同步的第二个制品），REST 的 OpenAPI 文档发布在旁边（需定位和保持同步的第二个制品）。（来源：https://graphql.org/ai/）
F-660: [GraphQL+AI] GraphQL 与 REST+OpenAPI 对比——Response shape：GraphQL 响应包含查询请求的字段（调用者决定），REST endpoint 返回其固定载荷（缩小响应需稀疏字段集约定或另一个 endpoint）；agent 为上下文窗口中的差异付出代价。（来源：https://graphql.org/ai/）
F-661: [GraphQL+AI] GraphQL 与 REST+OpenAPI 对比——Traversal：GraphQL 一次查询遍历多类型关系（agent 无需在上下文中同时持有整个类型图），REST 每个资源一个 endpoint（关系存在于 agent 脑中，需自行组合结果）。（来源：https://graphql.org/ai/）
F-662: [GraphQL+AI] GraphQL 与 REST+OpenAPI 对比——Documentation：GraphQL 描述附着在类型、每个字段和每个参数上，通过同一内省调用返回（无单独文档文件需指向），REST 文档在规范文档和指令文件中。（来源：https://graphql.org/ai/）
F-663: [GraphQL+AI] Apollo 报告称当 MCP 服务器暴露精选操作集而非整个 schema 时，schema 上下文减少约 40%，工具调用减少 40-75%；这是 Apollo 对自己服务器的测量而非独立基准，描述的是工具选择而非 GraphQL 对 REST 的对比；GraphQL AI 工作组欢迎可复现的 agent 对 GraphQL API 的测量数据。（来源：https://graphql.org/ai/）
F-664: [GraphQL+AI] 文档存在于 schema 中：使用 `"""` 编写的描述存储在类型和每个字段上；agent 通过内置 `__type` 内省查询读回，无需单独的文档文件或 AGENTS.md 指向。（来源：https://graphql.org/ai/）
F-665: [GraphQL+AI] AI 页面提供交互式演示：基于 Star Wars schema，展示 agent 如何组合查询回答业务问题；例如使用 search 联合类型和三个内联片段（inline fragments），每个结果成员匹配片段并仅返回片段中命名字段。（来源：https://graphql.org/ai/）
F-666: [GraphQL+AI] 用例一 MCP Servers：构建由 GraphQL 驱动的 Model Context Protocol 服务器；每个 query、mutation 和 subscription 成为自动可发现的工具；schema 即契约，工具定义从 schema 生成而非旁边维护；类型安全的输入和结构化输出；一个 MCP 服务器暴露整个 API 表面。（来源：https://graphql.org/ai/）
F-667: [GraphQL+AI] 用例二 RAG Applications：用 GraphQL 驱动检索增强生成；单次请求精确获取文档、嵌入和交叉引用，无需 REST 分页加客户端合并；跨集合和来源 join 数据；字段选择最小化上下文窗口浪费。（来源：https://graphql.org/ai/）
F-668: [GraphQL+AI] 用例三 AI Agents & Tool Calling：为 AI agent 提供结构化、类型安全的数据层访问；GraphQL 查询组合让 LLM 在单次往返中构建复杂多步数据获取——调用多个服务、过滤和聚合；支持实时订阅用于流式 agent；单个 endpoint 处理所有数据操作。（来源：https://graphql.org/ai/）
F-669: [GraphQL+AI] GraphQL AI 工作组（AI Working Group）对所有人开放，在 GitHub 上协作（https://github.com/graphql/ai-wg）；相关博客文章包括 2025-07-03 "GraphQL: Supercharging AI" 和 2025-10-14 "Announcing the GraphQL AI Working Group"；社区通过 Discord（https://discord.graphql.org/）和 GitHub 协作定义 GraphQL 如何驱动下一代智能系统。（来源：https://graphql.org/ai/）
