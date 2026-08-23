---
type: concept
title: "执行引擎：字段解析与值完成"
description: "GraphQL 执行引擎核心算法：ExecuteRequest 入口、CoerceVariableValues、ExecuteOperation（query 并行/mutation 串行/subscription 事件流）、CollectFields/DoesFragmentTypeApply/MergeSelectionSets、ExecuteField/CoerceArgumentValues/ResolveFieldValue、CompleteValue 各分支（Scalar/Enum/Object/Interface/Union/List/NonNull）以及 Non-Null 错误传播与 ResolveAbstractType。"
sources:
  - /references/spec-section-6-execution.md
    facts: [F-303, F-304, F-305, F-306, F-307, F-308, F-309, F-310, F-311, F-312, F-313, F-314, F-315, F-316, F-317, F-318, F-319, F-320, F-321, F-322, F-323, F-324, F-325, F-326, F-327, F-328, F-329, F-330, F-331, F-332, F-333, F-334, F-335, F-336, F-337, F-338, F-339, F-340, F-341, F-342, F-343, F-344, F-345, F-346, F-347, F-348, F-349, F-350, F-351, F-352, F-353, F-354, F-355, F-356, F-357, F-358, F-359, F-360, F-361, F-362, F-363, F-364, F-365, F-366, F-367, F-368, F-369, F-370, F-371, F-372, F-373, F-374, F-375]
---

# 执行引擎：字段解析与值完成

执行（Execution）是 GraphQL 请求处理三阶段管线的第二阶段，在验证通过后进行。执行引擎负责将 GraphQL 操作转换为实际的数据获取和处理过程：从根操作类型开始，递归收集字段、解析字段值、完成值类型，最终构建与查询形状同构的响应数据。

## ExecuteRequest 入口

执行请求由以下信息组成（F-303）：

- **schema**：GraphQL schema；
- **document**：已解析的文档，必须含 OperationDefinition，可含 FragmentDefinition；
- **operationName**（可选）：要执行的操作名称；
- **variableValues**（可选）：变量值；
- **initialValue**（可选）：初始根值；
- **extensions**（可选）：扩展信息。

extensions 如果存在必须是 map，键应使用唯一前缀以避免与未来规范版本冲突；实现不应向 request 添加额外属性（F-304）。GraphQL 请求不要求特定序列化格式或传输机制（F-305）。

### 执行流程

`ExecuteRequest(schema, document, operationName, variableValues, initialValue)` 的流程（F-307）：

```
1. GetOperation(document, operationName) → operation
2. CoerceVariableValues(schema, operation, variableValues) → coercedVariableValues
3. 根据 operation 类型分派：
   - query → ExecuteQuery(...)
   - mutation → ExecuteMutation(...)
   - subscription → Subscribe(...)
```

可执行文档中的 description 和 comment 在执行期间必须被忽略，对可观察的执行、验证或响应无影响（F-306）。

只有通过所有验证规则的请求才应执行；已知验证错误应在 response 的 errors 中报告且请求必须不执行（F-309）。服务可对先前已验证通过且未变更的请求记忆化验证结果（F-310）。

### GetOperation

`GetOperation(document, operationName)` 确定要执行的操作（F-308）：

- operationName 为 `null` 时，文档必须恰好包含一个操作并返回之，否则引发 request error 要求提供 operationName；
- operationName 非 `null` 时按名称查找，未找到则引发 request error。

## CoerceVariableValues（变量值强制转换）

在执行操作前，必须对传入的变量值按变量声明类型进行输入强制转换（F-311~F-315）：

1. 未提供值且存在默认值（包括 null）时，对默认值按变量类型输入强制转换规则强制转换后使用；
2. 变量类型为 Non-Nullable 且未提供值或值为 null 时，引发 request error；
3. 提供 null 值时 coercedValues 中记录 null；
4. 提供非 null 值时按类型强制转换，不可转换则引发 request error。

输入强制转换期间遇到 request error 则操作不执行（F-311）。`CoerceVariableValues` 算法与 `CoerceArgumentValues` 非常相似（F-315），但变量值在变量阶段完成强制转换后，字段参数中引用的变量值不再重复转换。

## ExecuteOperation（执行操作）

类型系统必须提供 query root operation type；支持 mutation/subscription 时必须分别提供对应的 root operation type（F-316）。三种操作类型有不同的执行模式。

### Query 执行（并行）

query 操作结果是在 query root operation type 上执行其 root selection set 的结果（F-317）。

`ExecuteQuery`（F-318、F-319）：
1. 获取 query root type（断言为 Object 类型）；
2. 以 **"normal"** 执行模式调用 `ExecuteRootSelectionSet`；
3. 执行 query 操作时可提供 initialValue。

normal 模式下，字段可并行执行。

### Mutation 执行（串行）

mutation 操作结果是在 mutation root object type 上执行其 root selection set 的结果（F-320）。

`ExecuteMutation`（F-321、F-322）：
1. 获取 mutation root type（断言为 Object 类型）；
2. 以 **"serial"** 执行模式调用 `ExecuteRootSelectionSet`。

mutation 顶级选择集必须**串行执行**，因为顶级字段预期对底层数据系统产生副作用，串行执行可防止竞态条件（F-322）。但 mutation 顶级字段的子选择集在 CompleteValue 期间以 normal 模式（可并行）执行（F-352）。

### Subscription 执行（事件流）

subscription 操作结果是称为 **response stream** 的 event stream（F-323）。source stream 中每个新事件触发一次操作执行并产生一个 execution result。

执行 subscription 操作在服务上创建持久函数，将底层 source stream 映射到返回的 response stream（F-324）。

**Subscribe 算法**（F-325）：

```
1. CreateSourceEventStream(...) → sourceStream
2. MapSourceToResponseEvent(sourceStream, ...) → responseStream
3. 返回 responseStream
```

Subscribe 和 ExecuteSubscriptionEvent 算法可在独立服务上运行，以维持大规模订阅系统的可预测扩展特性（F-326）。

#### Event Stream 语义

event stream 表示随时间发出的离散值序列（F-327）：
- 可随时完成；
- 可发出无限序列值；
- 遇到错误必须以该错误完成；
- 被观察者取消时必须完成。

query 和 mutation 操作是无状态的，可通过克隆服务实例扩展；subscription 是有状态的，需在订阅生命周期内维护 GraphQL 文档、变量和其他上下文（F-328）。GraphQL subscription 不要求特定序列化格式或传输机制；规范不规定消息确认、缓冲、重传请求或任何 QoS 细节（F-329）。

source stream 是表示根值序列的 event stream，每个根值触发一次 GraphQL 执行；创建 source stream 的逻辑是应用特定的（F-330）。

#### CreateSourceEventStream

1. `CollectFields` 收集顶级字段；
2. collectedFieldsMap 必须恰好一个条目（否则 request error）；
3. 取第一个字段的 fieldName 和 field；
4. `CoerceArgumentValues`；
5. `ResolveFieldEventStream` 返回 sourceStream（F-331、F-332）。

#### MapSourceToResponseEvent

sourceStream 发出 sourceValue 时调用 `ExecuteSubscriptionEvent`（F-333）：
- 内部错误则取消 sourceStream 并以 error 完成 responseStream；
- 正常发出结果；
- sourceStream 正常完成则 responseStream 正常完成；
- sourceStream 错误完成则 responseStream 以错误完成；
- responseStream 取消时取消 sourceStream 并正常完成。

#### ExecuteSubscriptionEvent

获取 subscription root type（断言为 Object），以 **"normal"** 模式执行 root selection set，与 ExecuteQuery 类似（F-334）。Unsubscribe 取消 responseStream，进而取消 sourceStream（F-335）。

## 执行选择集

GraphQL 操作递归收集并执行每个选定字段：先收集顶级 root selection set 的字段，逐个执行；每个字段完成后收集其子字段再执行，直到没有更多子字段（F-336）。

root selection set 是 GraphQL 操作提供的顶级 selection set，始终从 root operation type 选择（F-337）。

### ExecuteRootSelectionSet

`ExecuteRootSelectionSet(variableValues, initialValue, objectType, selectionSet, executionMode)`（F-338）：

1. `CollectFields(objectType, selectionSet, variableTypeMap)` → collectedFieldsMap；
2. `ExecuteCollectedFields(objectType, initialValue, collectedFieldsMap, variableValues, executionMode)`；
3. 返回包含 data 和 errors 的无序 map。

### 字段收集（Field Collection）

执行前，每个 selection set 通过将具有相同 response name（含引用 fragment 中）的字段收集到独立 field set，转换为 collected fields map，确保同 response name 的字段只执行一次（F-339）。

**collected fields map** 是有序 map，每个条目是 response name 及其关联的 field set（F-340）。**field set** 是共享同一 response name（别名优先，否则字段名）的有序选定字段集合（F-341）。验证确保 set 中每个字段具有相同名称和参数，但可有不同子字段。collected fields map 和 field set 中字段选择的顺序是有意义的（F-342）。

### CollectFields 算法

`CollectFields(objectType, selectionSet, variableValues, visitedFragments)` 遍历 selectionSet 中每个 selection（F-343）：

1. **@skip 检查**：if 参数为 true（或变量值为 true）则跳过；
2. **@include 检查**：if 参数不为 true（且变量值不为 true）则跳过；
3. **Field**：按 responseName 加入对应 field set；
4. **FragmentSpread**：
   - 检查 visitedFragments 防环；
   - `DoesFragmentTypeApply(objectType, fragmentType)` 判定后递归收集；
5. **InlineFragment**：类似 FragmentSpread 处理。

@skip 和 @include 的求值步骤可按任意顺序应用，因为它们满足交换律（F-345）。

### DoesFragmentTypeApply

`DoesFragmentTypeApply(objectType, fragmentType)` 判定片段类型是否适用于当前对象类型（F-344）：

- **Object 类型**：相同类型返回 true；
- **Interface 类型**：objectType 实现该接口返回 true；
- **Union 类型**：objectType 是其可能类型返回 true。

### CollectSubfields

`CollectSubfields(objectType, fields, variableValues)` 将 field set 中所有字段的选择集合并为单个 collected fields map（F-346）。这在 CompleteValue 处理复合类型字段时使用，将多个同 response name 字段的子选择集合并。

### ExecuteCollectedFields

1. 初始化 resultMap 为有序 map；
2. 遍历 collectedFieldsMap，对每个条目：
   - 取 fields 第一个条目的 fieldName；
   - 查 objectType 上该字段的 fieldType；
   - 调用 `ExecuteField`；
   - 结果以 responseName 为键存入 resultMap；
3. resultMap 按字段在操作中首次出现的顺序排序（F-347、F-348）。

## Normal 与 Serial 执行模式

- **normal 模式**：执行器可按任意顺序（通常并行）执行 collected fields map 中的条目。非顶级 mutation 字段的解析必须无副作用且幂等，执行顺序不影响结果（F-350）。
- **serial 模式**：执行器必须按 collected fields map 中的顺序逐个处理每个条目，每个条目在 resultMap 中对应值完成后才继续下一个（F-351）。此模式用于 mutation 顶级选择集。

mutation 顶级字段串行执行，但其子选择集在 CompleteValue 期间以 normal 模式执行（F-352）。

## 执行字段

字段执行分三步：强制转换参数值 → 解析字段值 → 完成值（F-353）。

`ExecuteField(objectType, objectValue, fieldType, fields, variableValues)`（F-354）：

```
1. 取 fields 第一个条目
2. CoerceArgumentValues(objectType, field, variableValues) → argumentValues
3. ResolveFieldValue(objectType, objectValue, fieldName, argumentValues) → result
4. CompleteValue(fieldType, fields, result, ...) → completedResult
```

### CoerceArgumentValues（字段参数强制转换）

`CoerceArgumentValues` 遍历字段的 argumentDefinitions（F-355、F-356）：

1. 未提供值且有默认值（包括 null）则强制转换默认值后使用；
2. Non-Null 类型参数缺失或值为 null 引发 execution error；
3. 变量值**不再强制转换**（已在 CoerceVariableValues 中转换）；
4. 字面量值按类型输入强制转换规则转换；
5. 因输入强制转换引发的 request error 应视为 execution error。

实现可优化参数默认值的强制转换，只执行一次并缓存结果（F-357）。

### ResolveFieldValue（字段值解析）

`ResolveFieldValue` 调用 objectType 为 fieldName 提供的内部 resolver 函数，传入 objectValue 和 argumentValues 返回解析值（F-358）。

resolver 通常是异步的（依赖底层数据库或网络服务），GraphQL 执行器必须处理异步执行流。List 类型字段返回的值集合中每个值本身也可能异步获取（F-359）。

## CompleteValue（值完成）

CompleteValue 是执行引擎的核心算法，负责确保解析值符合预期返回类型。字段值解析后，通过确保其符合预期返回类型来完成；返回类型为另一个 Object 类型时，字段执行递归收集并执行子字段（F-360）。

CompleteValue 根据返回类型的不同种类有不同的处理分支：

### Non-Null 分支

```
CompleteValue(NonNullType, ...):
  innerType = NonNullType.ofType
  completedResult = CompleteValue(innerType, ...)
  if completedResult is null:
    throw execution error
  return completedResult
```

取 innerType，递归调用 CompleteValue；若 completedResult 为 null 则引发 execution error；否则返回 completedResult（F-361）。

### Null 值处理

result 为 null（或类似 null 的内部值如 undefined）时返回 null（F-362）。这是所有可空类型的 null 快速路径。

### List 分支

```
CompleteValue(ListType, ...):
  if result is not a collection:
    throw execution error
  for each resultItem in result:
    completedItem = CompleteValue(innerType, resultItem, ...)
    append completedItem to results
  return results
```

result 必须是值的集合，否则引发 execution error；对 result 中每个 resultItem 以 innerType 递归调用 CompleteValue，返回结果列表（F-363）。

### Scalar/Enum 分支

调用 `CoerceResult(fieldType, result)` 返回结果（F-364）。

`CoerceResult(leafType, value)`（F-366）：
- 断言 value 非 null；
- 调用类型系统提供的 result coercion 内部方法；
- 该方法必须返回类型有效值且非 null，否则引发 execution error。

### Object/Interface/Union 分支

对于复合输出类型（F-365）：

```
CompleteValue(ObjectType | InterfaceType | UnionType, ...):
  if fieldType is Object:
    objectType = fieldType
  else (Interface or Union):
    objectType = ResolveAbstractType(fieldType, result)

  subFields = CollectSubfields(objectType, fields, variableValues)
  return ExecuteCollectedFields(objectType, result, subFields, variableValues, "normal")
```

- **Object**：直接使用 fieldType 作为 objectType；
- **Interface/Union**：先调用 `ResolveAbstractType` 确定运行时 objectType；
- 然后 `CollectSubfields` 合并子选择集；
- 以 **normal 模式**（可并行）执行子字段。

### ResolveAbstractType

`ResolveAbstractType(abstractType, objectValue)` 调用类型系统内部方法，根据 abstractType 和 objectValue 确定对应的 Object 类型（F-367）。这是抽象类型（Interface/Union）多态解析的关键机制——schema 实现需提供类型解析器（如 `__resolveType`）。

## Non-Null 错误传播

Non-Null 类型不仅是类型约束，更是错误传播的控制机制。执行错误在特定 response position 引发时，按以下规则传播：

### 基本规则

- execution error 在字段执行、值解析或强制转换期间于特定 response position 引发；这些错误必须在响应中报告，但通过产生部分 data 来"处理"（F-368）；
- 字段解析期间引发 execution error 时，该错误发生的 response position 视为解析为 null，错误必须加入 errors 列表（F-370）；
- response position 因 ResolveFieldValue 结果或 execution error 而为 null，且该位置为 Non-Null 类型时，在该位置引发 execution error 并加入 errors 列表（F-371）。

### 冒泡机制

Non-Null response position 不能为 null，execution error **传播到父 response position** 处理（F-349、F-373）：

```
if fieldType is Non-Null and result is null/error:
  if parentPosition is nullable:
    parentPosition resolves to null
    error stops here
  else (parent is also Non-Null):
    propagate error to parent's parent
    continue bubbling
```

- 父位置**可为 null** 则解析为 null，错误停止冒泡；
- 父位置**也是 Non-Null** 则继续向上传播；
- 尚未执行的兄弟位置可取消以避免不必要工作（F-349）。

### List 中的 Non-Null

List 包装 Non-Null 类型时，列表元素位置解析为 null 则整个列表 position 必须解析为 null（F-374）。若 List 也被 Non-Null 包装（即 `[T!]!`），则 execution error 继续向上传播。

### 全链 Non-Null → data 为 null

从请求根到 execution error 源的每个 response position 都是 Non-Null 类型时，execution result 的 data 条目应为 null（F-375）。

### 错误去重

因已加入 errors 列表的 execution error 导致 position 为 null 时，errors 列表不再受影响——每个 response position 只添加一个错误（F-372）。这避免了冒泡链路上重复添加同一错误。

### 冒泡示例

```graphql
type Query {
  user: User!
}

type User {
  id: ID!
  profile: Profile!
}

type Profile {
  avatar: String!
  bio: String
}
```

若 `profile.avatar` 解析失败（返回 null 或抛错）：
1. `avatar: String!` 为 Non-Null，错误冒泡到 `profile`；
2. `profile: Profile!` 为 Non-Null，错误继续冒泡到 `user`；
3. `user: User!` 为 Non-Null，错误继续冒泡到根；
4. 根 `data` 为 null。

若 `profile.bio`（nullable）解析失败：
1. `bio: String` 可为 null，该位置为 null；
2. 错误不传播，其他字段正常返回。

## execution error 与 request error 的区别

- **execution error**：在特定字段执行期间引发，导致部分响应数据（F-368、F-397）。通常是 GraphQL 服务的过错（F-398）。
- **request error**：产生 request error result 且无 data（F-369）。在执行开始前引发，包括语法错误、验证错误、变量强制转换失败等。

## 执行流程全景

```
ExecuteRequest
├── GetOperation
├── CoerceVariableValues
└── ExecuteOperation
    ├── ExecuteQuery (normal)
    ├── ExecuteMutation (serial top-level, normal sub-fields)
    └── Subscribe → responseStream
        └── ExecuteSubscriptionEvent (per event, normal)

ExecuteRootSelectionSet
├── CollectFields
│   ├── @skip/@include evaluation
│   ├── Field → field set
│   ├── FragmentSpread → DoesFragmentTypeApply → recursive
│   └── InlineFragment → recursive
├── ExecuteCollectedFields (normal=parallel / serial=sequential)
│   └── ExecuteField (per field)
│       ├── CoerceArgumentValues
│       ├── ResolveFieldValue (resolver)
│       └── CompleteValue
│           ├── Non-Null → recurse innerType, null→error
│           ├── null → return null
│           ├── List → recurse each item
│           ├── Scalar/Enum → CoerceResult
│           └── Object/Interface/Union
│               ├── ResolveAbstractType (for Interface/Union)
│               ├── CollectSubfields
│               └── ExecuteCollectedFields (normal) → recursive
└── Non-Null error bubbling
```

## 相关概念

- [验证管线与规则体系](/concepts/05-validation.md) — 执行前必须通过验证，验证失败产生 request error
- [响应格式、错误冒泡与序列化](/concepts/07-response-and-errors.md) — 执行结果的响应格式、error 对象结构和 Non-Null 冒泡的 path 规则
- [指令、包装类型与输入系统](/concepts/04-directives-and-wrapping-types.md) — Non-Null/List 类型语义、@skip/@include 指令、变量与参数强制转换
- [复合类型：对象、接口、联合与枚举](/concepts/03-composite-types.md) — 抽象类型 ResolveAbstractType 机制、Object/Interface/Union 类型
- [内省系统：GraphQL 的自描述机制](/concepts/08-introspection.md) — 内省字段 __typename/__schema/__type 的执行
