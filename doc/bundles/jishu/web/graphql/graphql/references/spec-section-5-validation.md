---
type: reference
title: "GraphQL 规范 Section 5：Validation"
description: "GraphQL 验证规则体系，涵盖文档、操作、字段、参数、片段、值、指令与变量的验证规则及兼容性判定。"
sources:
  - path: "external/libs/GraphQL/graphql-spec/spec/Section 5 -- Validation.md"
    facts: [F-249, F-250, F-251, F-252, F-253, F-254, F-255, F-256, F-257, F-258, F-259, F-260, F-261, F-262, F-263, F-264, F-265, F-266, F-267, F-268, F-269, F-270, F-271, F-272, F-273, F-274, F-275, F-276, F-277, F-278, F-279, F-280, F-281, F-282, F-283, F-284, F-285, F-286, F-287, F-288, F-289, F-290, F-291, F-292, F-293, F-294, F-295, F-296, F-297, F-298, F-299, F-300, F-301, F-302]
---

# GraphQL 规范 Section 5：Validation

## 信源概述

| 信源 | 类型 | 事实范围 | 职责 |
|------|------|----------|------|
| external/libs/GraphQL/graphql-spec/spec/Section 5 -- Validation.md | 规范文档 | F-249~F-302 | 定义 GraphQL 请求的验证规则与类型兼容性判定 |

## 关键事实登记

### 验证概述（F-249~F-251）

GraphQL 服务不仅验证请求语法正确，还确保其在给定 schema 上下文中无歧义且无错误。

- 无效请求在技术上仍可执行，且按 Execution 章节算法产生稳定结果，但该结果可能有歧义或出乎意料，因此执行应仅针对有效请求发生
- 类型系统随时间演进添加新类型和字段时，先前有效的请求可能变为无效；导致此情况的变更称为 **breaking change**

### 文档验证（F-252~F-253）

- **Executable Definitions**：文档中每个 definition 必须是 ExecutableDefinition，不得是 TypeSystemDefinitionOrExtension
- 包含 TypeSystemDefinitionOrExtension 的文档对执行无效

### 操作验证（F-254~F-260）

- 每个 schema 必须支持 query 操作；mutation 和 subscription 操作的支持是可选的
- **Operation Type Existence**：对文档中每个操作定义，schema 中必须存在对应操作类型的 root operation type
- **Operation Name Uniqueness**：文档中每个命名操作定义的名称在文档内必须唯一，即使操作类型不同也不允许同名
- **Lone Anonymous Operation**：当文档包含多个操作时，不得存在匿名操作
- **Subscription Single Root Field**：subscription 操作的顶级选择集经 CollectSubscriptionFields 收集后必须恰好有一个条目，且该条目不得是内省字段
- CollectSubscriptionFields 在收集时禁止选择项提供 @skip 或 @include 指令（因为验证时无法访问运行时变量）
- 单个文档可包含任意数量的 subscription 操作，每个可包含不同根字段；执行含多个 subscription 的文档时必须提供 operation name

### 字段验证（F-261~F-269）

#### 字段选择规则

- **Field Selections**：字段选择的目标字段必须在作用域类型上定义；别名名称无限制
- 对 Interface 类型，只能直接选择 Interface 上定义的字段，具体实现者上的字段与该 interface 类型选择集的有效性无关
- Union 类型不定义字段（`__typename` 元字段除外），不得直接从 union 类型选择集选择字段，必须通过片段间接查询

#### 字段合并规则

- **Field Selection Merging**：任意选择集中 FieldsInSetCanMerge(set) 必须为 true
- 同 response name 的每对不同字段必须 SameResponseShape 为 true
- 当父类型相同或任一非 Object 类型时，必须具有相同字段名和相同参数集合，且合并后的子选择集也必须可合并
- 不同 Object 类型下（通过 fragment 区分）的同 response name 字段可具有不同字段名或参数，因为它们不会在同一对象上同时遇到

#### SameResponseShape 判定

- Non-Null 与 nullable 不匹配返回 false
- List 基数不匹配返回 false
- Scalar/Enum 必须同类型
- 复合类型递归检查子字段响应形状

#### 叶子字段规则

- 解包结果类型为 scalar 或 enum 时，该选择的子选择集必须为空
- 解包结果类型为 interface、union 或 object 时，该选择的子选择集不得为空

### 参数验证（F-270~F-273）

- **Argument Names**：提供给字段或指令的每个参数必须在该字段或指令的可能参数集合中定义
- **Argument Uniqueness**：同一参数集合中不得出现多个同名参数
- **Required Arguments**：类型为 Non-Null 且无默认值的参数必须提供，且值不得为 null 字面量；否则参数为可选
- 参数顺序不影响验证结果

### 片段验证（F-274~F-284）

#### 基本规则

- **Fragment Name Uniqueness**：文档中每个 fragment 定义的名称必须唯一；inline fragment 不受此规则影响
- **Fragment Spread Type Existence**：命名片段和内联片段的目标类型必须在 schema 中定义
- **Fragments on Composite Types**：fragment 的目标类型必须是 UNION、INTERFACE 或 OBJECT 类型，不得声明在 scalar 上
- **Fragments Must Be Used**：每个已定义的 fragment 必须至少被文档中的一个 spread 引用
- **Fragment Spread Target Defined**：每个命名 fragment spread 必须引用文档中已定义的 fragment
- **Fragment Spreads Must Not Form Cycles**：fragment spread 图不得形成任何环（包括自引用），否则会导致无限展开或无限执行

#### 片段展开可能性

- **Fragment Spread Is Possible**：对每个 spread，其 fragmentType 与 parentType 的 GetPossibleTypes 交集不得为空

**GetPossibleTypes**：
- Object 类型返回包含自身的集合
- Interface 返回实现该接口的类型集合
- Union 返回其可能类型集合

**作用域判定**：
- Object 作用域中 Object spread 仅在同类型时有效
- Abstract（interface/union）spread 在 object 实现该接口或是 union 成员时有效
- Abstract 作用域中 Object spread 在 object 是该 abstract 类型可能类型之一时有效
- Abstract spread 在 abstract scope 中只要存在至少一个同时属于两者可能类型交集的 object 类型即有效
- Interface 类型 fragment 可始终 spread 到它所实现的 Interface 作用域中

### 值验证（F-285~F-289）

- **Values of Correct Type**：文档中每个字面量 Input Value 必须可强制转换到其位置所期望的类型（假设嵌套的 variableUsage 在运行时具有有效值）
- 期望类型位置包括：参数值位置、输入对象字段值位置、变量定义默认值位置
- **Input Object Field Names**：输入对象值中的每个字段必须在该输入对象期望类型的可能字段集合中定义
- **Input Object Field Uniqueness**：输入对象值中不得包含多个同名字段
- **Input Object Required Fields**：Non-Null 且无默认值的输入对象字段必须提供且值不得为 null 字面量

### 指令验证（F-290~F-292）

- **Directives Are Defined**：文档中每个指令使用必须对应服务中已定义的指令
- **Directives Are in Valid Locations**：每个指令使用必须出现在该指令定义声明的有效位置之一
- **Directives Are Unique per Location**：非 repeatable 指令在同一位置只能出现一次；repeatable 指令可在同一位置多次使用

### 变量验证（F-293~F-302）

#### 基本规则

- **Variable Uniqueness**：每个操作中定义的变量名在该操作内必须唯一；不同操作可定义同名变量
- **Variables Are Input Types**：每个变量的类型必须是输入类型（IsInputType 为 true）；Object、Union、Interface 不能用作变量类型
- **All Variable Uses Defined**：操作作用域及其传递性引用的所有 fragment 中使用的每个变量必须在该操作的变量列表中定义
- **All Variables Used**：操作定义的每个变量必须在该操作本身或其传递性引用的 fragment 中至少使用一次，未使用变量导致验证错误
- **All Variable Usages Are Allowed**：每个变量使用必须通过 IsVariableUsageAllowed 检查

#### 类型兼容性判定

**IsVariableUsageAllowed**：
1. 当 locationType 为 non-null 位置且 variableType 为 nullable 时，变量或位置必须提供非 null 默认值，否则返回 false
2. 通过 AreTypesCompatible 判定类型兼容性

**IsNonNullPosition**：
- locationType 本身是 non-null 返回 true
- 当 variableUsage 位于 OneOf Input Object 的 ObjectField 中时返回 true
- 否则返回 false

**AreTypesCompatible**：
- non-null 对 non-null 解包后递归比较
- List 基数必须匹配且 item 类型递归兼容
- 最终要求命名类型相同

#### OneOf 与默认值规则

- OneOf Input Object 字段位置上的变量必须是 non-nullable 类型
- nullable 变量在变量或位置提供默认值时可出现在 non-null 参数位置；运行时仍提供 null 时 non-null 参数必须引发 execution error
