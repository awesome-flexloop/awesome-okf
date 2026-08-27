---
type: concept
title: "验证管线与规则体系"
description: "GraphQL 验证在执行前进行，覆盖文档验证（操作命名/匿名操作/单根字段订阅）、字段验证（叶子字段/字段合并/参数名）、参数验证、片段验证（spread 可能性/目标类型/环检测/未使用片段）、值验证、指令验证以及变量验证的 IsVariableUsageAllowed 类型兼容性算法。"
sources:
  - resource: /references/spec-section-5-validation.md
    facts: [F-249, F-250, F-251, F-252, F-253, F-254, F-255, F-256, F-257, F-258, F-259, F-260, F-261, F-262, F-263, F-264, F-265, F-266, F-267, F-268, F-269, F-270, F-271, F-272, F-273, F-274, F-275, F-276, F-277, F-278, F-279, F-280, F-281, F-282, F-283, F-284, F-285, F-286, F-287, F-288, F-289, F-290, F-291, F-292, F-293, F-294, F-295, F-296, F-297, F-298, F-299, F-300, F-301, F-302]
---

# 验证管线与规则体系

验证（Validation）是 GraphQL 请求处理三阶段管线的第一阶段，在执行（Execution）之前进行。GraphQL 服务不仅验证请求语法正确，还确保其在给定 schema 上下文中无歧义且无错误（F-249）。无效请求在技术上仍可执行且按执行算法产生稳定结果，但该结果可能有歧义或出乎意料，因此执行应仅针对有效请求发生（F-250）。

## 验证的定位与意义

验证在请求处理管线中处于静态检查阶段，其输入是已解析的 GraphQL 文档和 schema，输出是验证通过或错误列表。验证规则可分为以下几大类：

1. **文档验证**：确保文档结构合法；
2. **操作验证**：操作类型存在、命名唯一、订阅单根字段；
3. **字段验证**：字段存在、叶子字段选择正确、字段可合并；
4. **参数验证**：参数名存在、唯一、必需参数已提供；
5. **片段验证**：片段名称唯一、目标类型存在、spread 可能、无环、已使用；
6. **值验证**：字面量类型正确、输入对象字段合法；
7. **指令验证**：指令已定义、位置合法、唯一性；
8. **变量验证**：变量唯一、输入类型、已定义、已使用、类型兼容。

类型系统随时间演进添加新类型和字段时，先前有效的请求可能变为无效——导致此情况的变更称为 **breaking change**（破坏性变更）（F-251）。

## 文档验证

### Executable Definitions

文档中每个 definition 必须是 ExecutableDefinition（OperationDefinition 或 FragmentDefinition），不得是 TypeSystemDefinitionOrExtension（F-252）。包含 TypeSystemDefinitionOrExtension 的文档对执行无效（F-253）。

这意味着提交给 GraphQL 服务执行的文档只能包含查询操作和片段定义，不能包含 `type`、`schema`、`directive` 等类型系统定义。

## 操作验证

### 操作类型存在性

每个 schema 必须支持 query 操作；mutation 和 subscription 操作的支持是可选的（F-254）。对文档中每个操作定义，schema 中必须存在对应操作类型的 root operation type（F-255）。若 schema 未定义 mutation 根类型而文档包含 mutation 操作，验证失败。

### 操作名称唯一性

文档中每个命名操作定义的名称在文档内必须唯一，即使操作类型不同也不允许同名（F-256）。以下文档无效：

```graphql
query GetUser { ... }
mutation GetUser { ... }
```

### 匿名操作规则

当文档包含多个操作时，不得存在匿名操作（F-257）。若文档仅包含一个操作，该操作可以是匿名的。

### 订阅单根字段

subscription 操作的顶级选择集经 `CollectSubscriptionFields` 收集后必须恰好有一个条目，且该条目不得是内省字段（F-258）。`CollectSubscriptionFields` 在收集时禁止选择项提供 `@skip` 或 `@include` 指令，因为验证时无法访问运行时变量（F-259）。

```graphql
subscription OnNewOrder {
  newOrder { id total }
}

subscription Invalid {
  newOrder { id }
  newUser { id }
}
```

上例中第二个订阅无效，因为包含两个顶级根字段。

单个文档可包含任意数量的 subscription 操作，每个可包含不同根字段；执行含多个 subscription 的文档时必须提供 operation name（F-260）。

## 字段验证

### 字段选择存在性

字段选择的目标字段必须在作用域类型上定义（F-261）。别名名称无限制，但实际字段名必须在对应类型上存在。

对 Interface 类型，只能直接选择 Interface 上定义的字段，具体实现者上的字段与该 interface 类型选择集的有效性无关（F-262）。若需查询实现者特有字段，必须使用类型精炼片段。

Union 类型不定义字段（`__typename` 元字段除外），不得直接从 union 类型选择集选择字段，必须通过片段间接查询（F-263）。

### 字段选择合并（Field Selection Merging）

任意选择集中 `FieldsInSetCanMerge(set)` 必须为 true（F-264）。这一规则确保同一 response name 的多个字段选择能够安全合并为一次执行。

**FieldsInSetCanMerge 规则**（F-265）：
- 同 response name 的每对不同字段必须 `SameResponseShape` 为 true；
- 当父类型相同或任一非 Object 类型时，必须具有相同字段名和相同参数集合；
- 合并后的子选择集也必须可合并。

**SameResponseShape 规则**（F-266）：
- Non-Null 与 nullable 不匹配返回 false；
- List 基数不匹配返回 false；
- Scalar/Enum 必须同类型；
- 复合类型递归检查子字段响应形状。

不同 Object 类型下（通过 fragment 区分）的同 response name 字段可具有不同字段名或参数，因为它们不会在同一对象上同时遇到（F-267）。

### 叶子字段选择（Leaf Field Selections）

解包结果类型为 scalar 或 enum 时，该选择的子选择集必须为空（F-268）——叶子字段不能有子选择。

解包结果类型为 interface、union 或 object 时，该选择的子选择集**不得为空**（F-269）——复合类型字段必须选择子字段直到叶子。

```graphql
type Query {
  user: User!
  username: String!
}

query Valid {
  user { name }
  username
}

query Invalid {
  user { name { ... } }
  username { ... }
}
```

## 参数验证

### 参数名存在性

提供给字段或指令的每个参数必须在该字段或指令的可能参数集合中定义（F-270）。传递未定义的参数名导致验证错误。

### 参数唯一性

同一参数集合中不得出现多个同名参数（F-271）。

### 必需参数

类型为 Non-Null 且无默认值的参数必须提供，且值不得为 `null` 字面量；否则参数为可选（F-272）。

参数顺序不影响验证结果（F-273）。

## 片段验证

### 片段名称唯一性

文档中每个 fragment 定义的名称必须唯一（F-274）。inline fragment 不受此规则影响，因为它们没有名称。

### 片段目标类型存在性

命名片段和内联片段的目标类型必须在 schema 中定义（F-275）。

### 片段目标类型必须是复合类型

fragment 的目标类型必须是 UNION、INTERFACE 或 OBJECT 类型，不得声明在 scalar 上（F-276）。片段不能指定在输入值（标量、枚举或输入对象）上。

### 片段必须被使用

每个已定义的 fragment 必须至少被文档中的一个 spread 引用（F-277）。定义但未使用的片段导致验证错误。

### 片段展开目标已定义

每个命名 fragment spread 必须引用文档中已定义的 fragment（F-278）。引用不存在的片段导致错误。

### 片段展开不得形成环

fragment spread 图不得形成任何环（包括自引用），否则会导致无限展开或无限执行（F-279）。

### 片段展开可能性（Fragment Spread Is Possible）

对每个 spread，其 fragmentType 与 parentType 的 `GetPossibleTypes` 交集不得为空（F-280）。这一规则确保片段在当前作用域类型中至少有一种可能的具体类型匹配。

**GetPossibleTypes**（F-281）：
- Object 类型返回包含自身的集合；
- Interface 返回实现该接口的类型集合；
- Union 返回其可能类型集合。

具体的可能性判定规则（F-282~F-284）：

- **Object 作用域中 Object spread**：仅在同类型时有效；
- **Object 作用域中 Abstract（interface/union）spread**：在 object 实现该接口或是 union 成员时有效；
- **Abstract 作用域中 Object spread**：在 object 是该 abstract 类型可能类型之一时有效；
- **Abstract 作用域中 Abstract spread**：只要存在至少一个同时属于两者可能类型交集的 object 类型即有效；
- **Interface 类型 fragment**：可始终 spread 到它所实现的 Interface 作用域中。

```graphql
type Cat { name: String! }
type Dog { name: String! }
union Pet = Cat | Dog

query {
  pets {
    ... on Cat { name }
    ... on Dog { name }
    ... on String { length }
  }
}
```

上例中 `... on String` 无效，因为 `Pet` 的可能类型与 `String` 无交集。

## 值验证

### 值类型正确性

文档中每个字面量 Input Value 必须可强制转换到其位置所期望的类型（F-285）。假设嵌套的 variableUsage 在运行时具有有效值，字面量部分在验证时检查。

期望类型位置包括（F-286）：
- 参数值位置；
- 输入对象字段值位置；
- 变量定义默认值位置。

### 输入对象字段名

输入对象值中的每个字段必须在该输入对象期望类型的可能字段集合中定义（F-287）。包含未定义字段名导致验证错误。

### 输入对象字段唯一性

输入对象值中不得包含多个同名字段（F-288）。

### 输入对象必需字段

Non-Null 且无默认值的输入对象字段必须提供且值不得为 `null` 字面量；否则为可选字段（F-289）。

## 指令验证

### 指令已定义

文档中每个指令使用必须对应服务中已定义的指令（F-290）。使用未定义指令导致错误。

### 指令位置合法

每个指令使用必须出现在该指令定义声明的有效位置之一（F-291）。例如，`@skip` 只能出现在 FIELD、FRAGMENT_SPREAD、INLINE_FRAGMENT 位置，不能出现在 FIELD_DEFINITION 等类型系统位置。

### 指令位置唯一性

非 repeatable 指令在同一位置只能出现一次；repeatable 指令可在同一位置多次使用（F-292）。

## 变量验证

变量验证是最复杂的验证规则集之一，涉及变量定义、使用和类型兼容性。

### 变量名称唯一性

每个操作中定义的变量名在该操作内必须唯一（F-293）。不同操作可定义同名变量。

### 变量必须是输入类型

每个变量的类型必须是输入类型（IsInputType 为 true）（F-294）。Object、Union、Interface 不能用作变量类型——因为它们是输出类型。可作为变量类型的包括 Scalar、Enum、Input Object 及其包装类型。

### 变量使用必须已定义

操作作用域及其传递性引用的所有 fragment 中使用的每个变量必须在该操作的变量列表中定义（F-295）。片段中使用的变量必须由消费该片段的操作声明。

### 变量必须被使用

操作定义的每个变量必须在该操作本身或其传递性引用的 fragment 中至少使用一次（F-296）。未使用变量导致验证错误。

### 变量使用类型兼容性

每个变量使用必须通过 `IsVariableUsageAllowed` 检查（F-297）。这是变量验证的核心算法。

**IsVariableUsageAllowed(variableType, locationType, variableDefaultValue, locationDefaultValue)**（F-298）：

1. **Non-Null 位置检查**：如果 locationType 是 non-null 位置且 variableType 是 nullable，则变量或位置必须提供非 null 默认值，否则返回 false；
2. 然后通过 `AreTypesCompatible` 判定类型兼容性。

**IsNonNullPosition(locationType, variableUsage)**（F-299）：
- locationType 本身是 non-null 返回 true；
- 当 variableUsage 位于 OneOf Input Object 的 ObjectField 中时返回 true；
- 否则返回 false。

这意味着 OneOf Input Object 的字段位置始终视为 non-null 位置，即使字段类型本身是 nullable。

**AreTypesCompatible(variableType, locationType)**（F-300）：
- non-null 对 non-null：解包后递归比较；
- non-null 对 nullable：解包 variableType 的 non-null 后递归比较（locationType 可接受更严格的变量类型）；
- nullable 对 non-null：不兼容（除非通过默认值检查）；
- List：基数必须匹配且 item 类型递归兼容；
- 最终要求命名类型相同。

### OneOf Input Object 变量规则

OneOf Input Object 字段位置上的变量必须是 non-nullable 类型（F-301）。这与 OneOf 语义一致——字段值必须恰好提供一个且非 null。

### Nullable 变量在 Non-Null 位置

nullable 变量在变量或位置提供默认值时可出现在 non-null 参数位置（F-302）。但运行时仍提供 null 时，non-null 参数必须引发 execution error——验证通过不保证运行时值有效。

```graphql
type Query {
  user(id: ID!): User
}

query GetUser($userId: ID) {
  user(id: $userId) { name }
}
```

上例中，`$userId: ID` 是 nullable，但 `id: ID!` 是 non-null 位置。若变量无默认值则验证失败；若 `$userId` 有默认值（如 `$userId: ID = "1"`）则验证通过，但运行时传入 null 仍会 execution error。

## 验证与执行的关系

验证阶段的错误属于 request error，导致请求不执行（F-309）。已知验证错误应在 response 的 errors 中报告，且请求必须不执行。服务可对先前已验证通过且未变更的请求记忆化验证结果，避免重复验证（F-310）。

验证规则确保：
- 查询在 schema 上下文中语义合法；
- 所有字段和参数引用存在且类型正确；
- 片段展开不会产生类型不匹配或无限循环；
- 变量使用类型兼容且作用域正确；
- 指令使用符合定义约束。

通过验证的请求才能进入执行阶段，由执行引擎进行字段解析和值完成。

## 相关概念

- [复合类型：对象、接口、联合与枚举](03-composite-types.md) — 了解 Object/Interface/Union 等类型上的字段选择规则
- [指令、包装类型与输入系统](04-directives-and-wrapping-types.md) — 了解指令位置定义、变量类型与输入强制转换
- [执行引擎：字段解析与值完成](06-execution.md) — 验证通过后进入执行阶段
- [响应格式、错误冒泡与序列化](07-response-and-errors.md) — 验证错误作为 request error 返回
- [查询语言基础：文档、操作与选择集](01-query-language-basics.md) — 了解文档、操作、片段等语法基础
