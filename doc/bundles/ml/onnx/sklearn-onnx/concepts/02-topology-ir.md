---
type: concept
title: "Topology IR：Scope/Variable/Operator/Component/ModelComponentContainer"
description: "sklearn-onnx 内部拓扑中间表示（IR）的核心数据结构：Variable（数据流边）、Operator（粗粒度计算节点）、Scope（命名空间）、Topology（IR容器）和 ModelComponentContainer（ONNX图构建器）"
sources:
  references: [../references/topology-ir.md, ../references/convert-api.md]
  facts: [F-006, F-007, F-008, F-009, F-010, F-011, F-012, F-020, F-022, F-032, F-033, F-034]
---

# Topology IR：Scope/Variable/Operator/Component/ModelComponentContainer

## 核心理解

sklearn-onnx 的中间表示（IR）是一个**粗粒度有向图**：Operator 是顶点（对应 sklearn 估计器），Variable 是边（对应估计器间的数据流）。Scope 管理命名空间，Topology 是整个图的容器，ModelComponentContainer 则是细粒度 ONNX 节点的收集器。理解这些类的职责和交互是调试转换问题的基础。

## 核心类层次

```
Topology（整个计算图的容器）
  └── Scope（命名空间，当前只允许一个）
        ├── Variable（数据流节点/边）
        │     ├── _is_fed / _is_root / _is_leaf（状态标志）
        │     ├── operators_inputs_（引用该变量作为输入的算子列表）
        │     └── operators_outputs_（引用该变量作为输出的算子列表，最多一个）
        └── Operator（粗粒度计算节点）
              ├── type（算子别名，如 "SklearnLinearClassifier"）
              ├── raw_operator（原始 sklearn 估计器对象）
              ├── inputs（OperatorList[Variable]，输入变量列表）
              └── outputs（OperatorList[Variable]，输出变量列表）

ModelComponentContainer（细粒度 ONNX 节点收集器，独立于 Topology）
  ├── inputs/outputs（ValueInfoProto 列表）
  ├── nodes（NodeProto 列表）
  ├── initializers（TensorProto 列表）
  └── value_info（中间变量类型信息）
```

## Variable——数据流节点

Variable 是 IR 图中的"边"，代表一个在估计器间流动的数据张量（或序列/字典）。

### 核心属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `_raw_name` | str | sklearn 侧的原始名称，如 `"input"`、`"probability"` |
| `_onnx_name` | str | ONNX 图中的唯一名称，由 Scope 生成 |
| `_scope` | str | 所属 Scope 名称 |
| `_type` | DataType | 变量类型，如 `FloatTensorType([None, 4])` |

### 状态标志

三个布尔状态控制数据流调度算法：

| 标志 | 含义 | 设置时机 |
|------|------|---------|
| `_is_root` | 是否为图的根输入 | Parse 阶段，由 initial_types 声明的变量 |
| `_is_leaf` | 是否为图的最终输出 | Parse 阶段，模型输出或 final_types 声明 |
| `_is_fed` | 是否已有生产者（输入就绪） | 初始化时 is_root=True 的变量 fed=True；Operator 执行后其输出 fed=True |

状态标志只能通过 `init_status()` 方法修改，确保状态转换的一致性。

### 双向链接

Variable 维护两个列表，记录引用它的算子：
- `operators_inputs_`：以该变量为输入的算子列表
- `operators_outputs_`：以该变量为输出的算子列表（最多一个，`set_parent()` 强制执行）

这使得从任何 Variable 都可以快速找到上游生产者和下游消费者。

### 元组解包

Variable 支持元组解包语法：

```python
onnx_name, var_type = variable
# 等价于：variable.onnx_name, variable.type
```

这在 converter 函数中非常方便：

```python
def convert_my_model(scope, operator, container):
    # 解包获取输入名和类型
    input_name, input_type = operator.inputs[0]
    output_name, output_type = operator.outputs[0]
    # ...
```

## Operator——粗粒度计算节点

Operator 是 IR 图中的"顶点"，代表一个 sklearn 估计器在计算图中的位置。注意 Operator **不是 ONNX 算子**——它是粗粒度的、对应 sklearn 估计器的节点，在 Convert 阶段才会被展开为多个细粒度 ONNX NodeProto。

### 核心属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `onnx_name` | str | ONNX 图中唯一算子名 |
| `scope` | str | 所属 Scope 名 |
| `type` | str | 算子别名字符串，如 `"SklearnLinearClassifier"` |
| `raw_operator` | sklearn estimator | 原始 sklearn 估计器对象（含拟合后的参数） |
| `target_opset` | int | 目标 opset 版本 |
| `inputs` | OperatorList | 输入 Variable 列表 |
| `outputs` | OperatorList | 输出 Variable 列表 |

### OperatorList 双向链接机制

`OperatorList` 继承自 Python `list`，重写了 `append()` 和 `extend()` 方法，在添加 Variable 时自动建立双向链接：

```python
class OperatorList(list):
    def append(self, var):
        super().append(var)
        var.set_parent(self.operator)  # 设置父算子（一个变量最多一个生产者）
        var.add_operator(self.operator, as_input=...)  # 反向引用
```

这保证了 Variable 和 Operator 之间的链接始终一致，避免手动维护导致的悬挂引用。

### 类型推断

`Operator.infer_types()` 方法查找并调用 shape_calculator：

```python
def infer_types(self):
    shape_calc = _registration.get_shape_calculator(self.type)
    shape_calc(self)  # 设置 self.outputs 的 type 属性
```

## Scope——命名空间管理

Scope 负责生成唯一名称、管理变量和算子的声明。

### 唯一命名算法

`get_unique_variable_name(seed)` 和 `get_unique_operator_name(seed)` 实现了 C 风格标识符生成：

1. 特殊字符（`.`、`-`、空格等）替换为下划线 `_`
2. 若首字符为数字，前缀加 `_`
3. 在 `onnx_variable_names`/`onnx_operator_names` 集合中去重
4. 重名时追加数字后缀（`name` → `name1` → `name2` ...）

### 变量声明

```python
def declare_local_variable(self, raw_name, type=None):
    # 1. 生成唯一 onnx_name
    # 2. 创建 Variable 实例
    # 3. 注册到 variable_mappings
    # 4. 返回 Variable
```

同一 `raw_name` 多次声明会形成 name mapping 列表（后声明的隐藏前声明），支持变量"重定义"语义。

### Options 两级查找

`get_options(model, default_values, fail)` 实现两级 options 查找：
1. 先按 `type(model)`（类级别）查找
2. 再按 `id(model)`（实例级别）查找，优先级更高

这使得同一类的不同实例可以有不同配置（如 Pipeline 中两个 TfidfVectorizer 使用不同 separators）。

## Topology——IR 图容器

Topology 是整个计算图的顶层容器。

### 当前限制：单 Scope

当前版本（1.21.0）的 sklearn-onnx 只允许创建一个 Scope。`declare_scope()` 方法显式检查：

```python
if len(self.scopes) != 0:
    raise RuntimeError("Only one scope can be created.")
```

声明 Scope 时自动将 `initial_types` 中的变量声明为 local_input，并标记 `is_root=True`。

### 转换器四级查找链

`call_converter()` 和 `call_shape_calculator()` 使用相同的四级优先级：

| 优先级 | 来源 | 适用场景 |
|--------|------|---------|
| 1（最高） | `custom_conversion_functions[type(raw_operator)]` | 用户按 sklearn 类注册的自定义函数 |
| 2 | `custom_conversion_functions[operator.type]` | 用户按算子别名注册的自定义函数 |
| 3 | `raw_operator.onnx_converter()` | 模型对象自带的方法（OnnxOperatorMixin） |
| 4（最低） | `_registration.get_converter(operator.type)` | 全局注册池（内置转换器） |

这个查找链是 sklearn-onnx 扩展性的核心：用户可以通过多种方式定制转换行为。

## ModelComponentContainer——细粒度节点收集器

ModelComponentContainer 独立于 Topology IR，负责收集 Convert 阶段产生的细粒度 ONNX 构建材料。

### 核心收集器

| 收集器 | 类型 | 内容 |
|--------|------|------|
| `inputs` | list[ValueInfoProto] | 图输入声明 |
| `outputs` | list[ValueInfoProto] | 图输出声明 |
| `nodes` | list[NodeProto] | ONNX 算子节点 |
| `initializers` | list[TensorProto] | 模型权重/常量 |
| `value_info` | list[ValueInfoProto] | 中间变量类型信息 |

### add_node 方法

`add_node(op_type, inputs, outputs, op_domain, op_version, name, **attrs)` 是 converter 中最常用的方法，它：

1. 校验 inputs 和 outputs 没有交集
2. 检查白/黑名单（`_check_operator()`）
3. 校验 opset 版本兼容性
4. 创建 NodeProto 并追加到 nodes
5. 记录 (domain, version) 到 `node_domain_version_pair_sets`

### add_initializer 方法

`add_initializer(name, onnx_type, shape, content)` 创建 TensorProto，包含**内容去重**优化：相同序列化内容的 initializer 只存一份，重复引用通过 Identity 节点连接。

### 白/黑名单机制

`_WhiteBlackContainer` 提供算子过滤：
- 白名单模式：只有白名单中的算子类型允许使用
- 黑名单模式：黑名单中的算子类型禁止使用

这可用于限制 Pipeline 转换中允许使用的 ONNX 算子类型（如只允许核心域算子、禁止 ML 域算子）。

### 拓扑排序

`ensure_topological_order()` 在组装阶段执行：
1. 基于 nodes 间的数据依赖构建 DAG
2. 执行 Kahn 算法进行拓扑排序
3. 检测环（环检测到抛 RuntimeError）
4. 检测断图（不可达节点警告）

## DataType 类型体系

Variable 的 `_type` 属性是 `DataType` 实例：

### 类型层次

```
DataType（基类）
  ├── FloatType / Int64Type / DoubleType / StringType / ...（标量类型，shape=[1,1]）
  ├── TensorType（张量类型抽象基类）
  │     ├── FloatTensorType
  │     ├── DoubleTensorType
  │     ├── Int64TensorType
  │     ├── Int32TensorType
  │     ├── StringTensorType
  │     ├── BooleanTensorType
  │     └── ...（共15种具体张量类型）
  ├── SequenceType(element_type)（序列类型）
  └── DictionaryType(key_type, value_type)（字典类型）
```

### TensorType 的 shape 语义

```python
FloatTensorType([None, 4])  # batch维度动态(None)，特征维度4(静态)
Int64TensorType([None, 1])   # 二分类label输出
FloatTensorType([None, 3])   # 3分类概率输出
FloatTensorType([])          # 标量（shape为空）
```

- `None` 表示动态维度（如 batch size）
- 整数表示静态维度
- 字符串表示 dim_param（符号化维度名）

所有 TensorType 通过 `to_onnx_type()` 生成 ONNX TypeProto。

## 关联概念

- [转换管线：解析sklearn→拓扑IR→数据流调度→ONNX组装](01-conversion-pipeline.md) — 了解这些类在四阶段管线中的作用
- [转换器注册：别名→实现三级映射、shape_calculator配对](03-converter-registration.md) — converter/shape_calculator 如何注册到系统
- [OnnxOperator代数API：嵌入式DSL、类工厂、延迟求值、三件套自动生成](04-onnx-operator-algebra.md) — 代数API如何绕过手写 converter
