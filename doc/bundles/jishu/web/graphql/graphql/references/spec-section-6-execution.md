---
type: reference
title: "GraphQL 规范 Section 6：Execution"
description: "GraphQL 执行引擎规范，涵盖请求执行、变量强制转换、操作分派、选择集收集与执行、字段解析、值完成及错误处理。"
sources:
  - path: "external/libs/GraphQL/graphql-spec/spec/Section 6 -- Execution.md"
    facts: [F-303, F-304, F-305, F-306, F-307, F-308, F-309, F-310, F-311, F-312, F-313, F-314, F-315, F-316, F-317, F-318, F-319, F-320, F-321, F-322, F-323, F-324, F-325, F-326, F-327, F-328, F-329, F-330, F-331, F-332, F-333, F-334, F-335, F-336, F-337, F-338, F-339, F-340, F-341, F-342, F-343, F-344, F-345, F-346, F-347, F-348, F-349, F-350, F-351, F-352, F-353, F-354, F-355, F-356, F-357, F-358, F-359, F-360, F-361, F-362, F-363, F-364, F-365, F-366, F-367, F-368, F-369, F-370, F-371, F-372, F-373, F-374, F-375]
---

# GraphQL 规范 Section 6：Execution

## 信源概述

| 信源 | 类型 | 事实范围 | 职责 |
|------|------|----------|------|
| external/libs/GraphQL/graphql-spec/spec/Section 6 -- Execution.md | 规范文档 | F-303~F-375 | 定义 GraphQL 请求的执行算法、字段解析与错误处理 |

## 关键事实登记

### 请求执行（F-303~F-310）

执行请求由以下信息组成：
- **schema**：类型系统定义
- **document**：必须含 OperationDefinition，可含 FragmentDefinition
- **operationName**（可选）：指定执行哪个操作
- **variableValues**（可选）：变量值映射
- **initialValue**（可选）：初始值
- **extensions**（可选）：扩展 map，键应使用唯一前缀

关键约束：
- GraphQL 请求不要求特定序列化格式或传输机制
- 可执行文档中的 description 和 comment 在执行期间必须被忽略，对可观察的执行、验证或响应无影响
- 只有通过所有验证规则的请求才应执行；已知验证错误应在 response 的 errors 中报告且请求必须不执行
- 服务可对先前已验证通过且未变更的请求记忆化验证结果

#### ExecuteRequest 流程

```
ExecuteRequest(schema, document, operationName, variableValues, initialValue)
  → GetOperation
  → CoerceVariableValues
  → 按操作类型分派：
      query    → ExecuteQuery
      mutation → ExecuteMutation
      subscription → Subscribe
```

**GetOperation**：
- operationName 为 null 时，文档必须恰好包含一个操作并返回之，否则引发 request error 要求提供 operationName
- operationName 非 null 时按名称查找，未找到则引发 request error

### 变量值强制转换（F-311~F-315）

CoerceVariableValues 算法：
1. 变量值按变量声明类型的输入强制转换规则进行强制转换
2. 未提供值且存在默认值（包括 null）时，对默认值强制转换后使用
3. 变量类型为 Non-Nullable 且未提供值或值为 null 时，引发 request error
4. 提供 null 值时 coercedValues 中记录 null；提供非 null 值时按类型强制转换，不可转换则引发 request error
5. 输入强制转换期间遇到 request error 则操作不执行

### 操作执行（F-316~F-335）

#### Query 执行（F-317~F-319）

- query 操作结果是在 query root operation type 上执行其 root selection set 的结果
- ExecuteQuery：获取 query root type（断言为 Object 类型），以 "normal" 执行模式调用 ExecuteRootSelectionSet
- 执行 query 操作时可提供 initialValue

#### Mutation 执行（F-320~F-322）

- mutation 操作结果是在 mutation root object type 上执行其 root selection set 的结果
- ExecuteMutation：获取 mutation root type（断言为 Object 类型），以 "serial" 执行模式调用 ExecuteRootSelectionSet
- mutation 顶级选择集必须串行执行，因为顶级字段预期对底层数据系统产生副作用，串行执行可防止竞态条件

#### Subscription 执行（F-323~F-335）

subscription 操作结果是称为 **response stream** 的 event stream，source stream 中每个新事件触发一次操作执行并产生一个 execution result。

**Subscribe 算法**：
```
CreateSourceEventStream → sourceStream
MapSourceToResponseEvent → responseStream
返回 responseStream
```

关键特性：
- Subscribe 和 ExecuteSubscriptionEvent 算法可在独立服务上运行
- event stream 表示随时间发出的离散值序列；可随时完成、可发出无限序列值、遇到错误必须以该错误完成
- query 和 mutation 操作是无状态的；subscription 是有状态的，需在订阅生命周期内维护 GraphQL 文档、变量和上下文
- GraphQL subscription 不要求特定序列化格式或传输机制；规范不规定消息确认、缓冲、重传请求或任何 QoS 细节

**CreateSourceEventStream**：
1. CollectFields 收集顶级字段，collectedFieldsMap 必须恰好一个条目（否则 request error）
2. 取第一个字段的 fieldName 和 field，CoerceArgumentValues
3. ResolveFieldEventStream 返回 sourceStream

**MapSourceToResponseEvent**：
- sourceStream 发出 sourceValue 时调用 ExecuteSubscriptionEvent
- 内部错误则取消 sourceStream 并以 error 完成 responseStream
- sourceStream 正常完成则 responseStream 正常完成
- sourceStream 错误完成则 responseStream 以错误完成
- responseStream 取消时取消 sourceStream 并正常完成

**ExecuteSubscriptionEvent**：获取 subscription root type（断言为 Object），以 "normal" 模式执行 root selection set，与 ExecuteQuery 类似。

### 选择集执行（F-336~F-352）

#### 执行模型（F-336~F-342）

GraphQL 操作递归收集并执行每个选定字段：先收集顶级 root selection set 的字段，逐个执行；每个字段完成后收集其子字段再执行，直到没有更多子字段。

**ExecuteRootSelectionSet**：
```
CollectFields 收集字段 → ExecuteCollectedFields（serial 串行 / normal 可并行）→ 返回 {data, errors}
```

**字段收集**：
- 执行前，每个 selection set 通过将具有相同 response name（含引用 fragment 中）的字段收集到独立 field set，转换为 collected fields map
- collected fields map 是有序 map，每个条目是 response name 及其关联的 field set
- field set 是共享同一 response name（别名优先，否则字段名）的有序选定字段集合
- 验证确保 set 中每个字段具有相同名称和参数，但可有不同子字段

#### CollectFields 算法（F-343~F-346）

遍历 selectionSet 中每个 selection：
1. @skip 的 if 参数为 true 则跳过
2. @include 的 if 参数不为 true 则跳过
3. Field 按 responseName 加入对应 field set
4. FragmentSpread：检查 visitedFragments 防环、DoesFragmentTypeApply 判定后递归收集
5. InlineFragment：类似处理

**DoesFragmentTypeApply(objectType, fragmentType)**：
- Object 类型——相同类型返回 true
- Interface 类型——objectType 实现该接口返回 true
- Union 类型——objectType 是其可能类型返回 true

@skip 和 @include 的求值步骤满足交换律，可按任意顺序应用。

#### ExecuteCollectedFields（F-347~F-349）

1. 初始化 resultMap 为有序 map
2. 遍历 collectedFieldsMap，取每个 fields 第一个条目的 fieldName
3. 查 objectType 上该字段的 fieldType
4. 调用 ExecuteField，结果以 responseName 为键存入 resultMap
5. resultMap 按字段在操作中首次出现的顺序排序

**Non-Null 错误传播**：Non-Null 类型响应位置引发 execution error 时，错误必须传播到父响应位置；如父位置可为 null 则解析为 null，否则继续传播。尚未执行的兄弟位置可取消以避免不必要工作。

#### 执行模式（F-350~F-352）

| 模式 | 行为 | 适用场景 |
|------|------|----------|
| normal | 可按任意顺序（通常并行）执行 collected fields map 中的条目 | query 顶级、所有嵌套选择集 |
| serial | 必须按 collected fields map 中的顺序逐个处理，每个条目完成后才继续下一个 | mutation 顶级选择集 |

mutation 顶级字段串行执行，但其子选择集在 CompleteValue 期间以 normal 模式（可并行）执行。

### 字段执行（F-353~F-367）

字段执行三阶段：**强制转换参数值 → 解析字段值 → 完成值**。

```
ExecuteField(objectType, objectValue, fieldType, fields, variableValues)
  → 取 fields 第一个条目
  → CoerceArgumentValues
  → ResolveFieldValue
  → CompleteValue
```

#### 参数强制转换（F-355~F-357）

CoerceArgumentValues：
1. 遍历字段的 argumentDefinitions，未提供值且有默认值则强制转换默认值后使用
2. Non-Null 类型参数缺失或值为 null 引发 execution error
3. 变量值不再强制转换（已在 CoerceVariableValues 中转换）
4. 字面量值按类型输入强制转换规则转换
5. 因输入强制转换引发的 request error 应视为 execution error
6. 实现可优化参数默认值的强制转换，只执行一次并缓存结果

#### 值解析（F-358~F-359）

ResolveFieldValue 调用 objectType 为 fieldName 提供的内部 resolver 函数，传入 objectValue 和 argumentValues 返回解析值。

resolver 通常是异步的（依赖底层数据库或网络服务），GraphQL 执行器必须处理异步执行流。List 类型字段返回的值集合中每个值本身也可能异步获取。

#### 值完成（F-360~F-367）

CompleteValue 按返回类型分派：

| 返回类型 | 处理方式 |
|----------|----------|
| Non-Null | 取 innerType 递归 CompleteValue；若结果为 null 则引发 execution error |
| null 结果 | 返回 null |
| List | result 必须是值集合；对每个 resultItem 以 innerType 递归 CompleteValue |
| Scalar/Enum | 调用 CoerceResult(fieldType, result) 返回结果 |
| Object/Interface/Union | Object 直接使用；Interface/Union 先 ResolveAbstractType 确定 objectType；CollectSubfields 后以 normal 模式 ExecuteCollectedFields |

**CoerceResult(leafType, value)**：断言 value 非 null；调用类型系统提供的 result coercion 内部方法；该方法必须返回类型有效值且非 null，否则引发 execution error。

**ResolveAbstractType(abstractType, objectValue)**：调用类型系统内部方法，根据 abstractType 和 objectValue 确定对应的 Object 类型。

### 执行错误处理（F-368~F-375）

#### 错误分类

- **execution error**：在字段执行、值解析或强制转换期间于特定 response position 引发；通过产生部分 data 来"处理"
- **request error**：产生 request error result 且无 data

#### 错误处理规则

1. 字段解析期间引发 execution error 时，该错误发生的 response position 视为解析为 null，错误加入 execution result 的 errors 列表
2. response position 因 ResolveFieldValue 结果或 execution error 而为 null，且该位置为 Non-Null 类型时，在该位置引发 execution error 并加入 errors 列表
3. 因已加入 errors 列表的 execution error 导致 position 为 null 时，errors 列表不再受影响——每个 response position 只添加一个错误

#### Non-Null 冒泡机制

- Non-Null response position 不能为 null，execution error 传播到父 response position 处理
- 父位置可为 null 则解析为 null；父位置也是 Non-Null 则继续传播
- List 包装 Non-Null 类型时，列表元素位置解析为 null 则整个列表 position 必须解析为 null
- 从请求根到 execution error 源的每个 response position 都是 Non-Null 类型时，execution result 的 data 条目应为 null
