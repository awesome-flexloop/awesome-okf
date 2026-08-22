---
type: reference
title: "Topology IR 核心类：Scope / Variable / Operator / Topology"
description: "sklearn-onnx 内部拓扑中间表示（IR）的核心类 Variable、Operator、Scope、Topology 及 ModelComponentContainer 的 API 与源码信源登记"
sources:
  - path: "external/libs/models/onnx/sklearn-onnx/skl2onnx/common/_topology.py"
    facts: [F-006, F-007, F-008, F-009, F-010, F-011, F-012, F-023, F-024]
  - path: "external/libs/models/onnx/sklearn-onnx/skl2onnx/common/_container.py"
    facts: [F-022, F-033]
  - path: "external/libs/models/onnx/sklearn-onnx/skl2onnx/common/data_types.py"
    facts: [F-020]
---

# Topology IR 核心类：Scope / Variable / Operator / Topology

## 信源概述

| 信源 | 类型 | 行数 | 职责 |
|------|------|------|------|
| `skl2onnx/common/_topology.py` | 核心模块 | ~1700行 | Topology/Scope/Variable/Operator 类定义、数据流调度算法、convert_topology 组装流程 |
| `skl2onnx/common/_container.py` | 图构建器 | ~1100行 | ModelComponentContainer 收集 ONNX 节点/初始值/输入输出，拓扑排序 |
| `skl2onnx/common/data_types.py` | 类型系统 | ~550行 | DataType 基类及 TensorType/SequenceType/DictionaryType 派生类 |

## Variable 类——拓扑中的变量节点（F-006）

**信源**：`common/_topology.py` L102-L412

### 构造函数

```python
Variable(raw_name, onnx_name, scope, type=None)
```

| 属性 | 类型 | 说明 |
|------|------|------|
| `_raw_name` | str | 原始名称（sklearn 侧名称，如 "input"、"probability"） |
| `_onnx_name` | str | ONNX 图中唯一名称（由 Scope 生成，如 "input"、"variable0"） |
| `_scope` | str | 所属 Scope 名称 |
| `_type` | DataType | DataType 实例（如 FloatTensorType([None, 4])） |
| `_is_fed` | bool | 该变量是否已有生产者（状态标志，只能通过 init_status 修改） |
| `_is_root` | bool | 是否为图的根输入（由 initial_types 声明） |
| `_is_leaf` | bool | 是否为图的最终输出 |
| `operators_inputs_` | list | 以该变量为输入的 Operator 列表 |
| `operators_outputs_` | list | 以该变量为输出的 Operator 列表（最多一个） |

### 关键方法

| 方法 | 说明 |
|------|------|
| `init_status(is_root=False, is_leaf=False, is_fed=False)` | 设置三个布尔状态标志 |
| `set_parent(operator)` | 强制一个变量只能是一个算子的输出，否则抛 RuntimeError |
| `add_operator(operator, as_input)` | 双向链接：记录引用该变量的算子 |
| `from_pb(obj)` | 静态方法，从 ONNX ValueInfoProto 反序列化 |
| `__iter__()` | 支持元组解包 `a, b = variable` → `(onnx_name, type)` |

## Operator 类——拓扑中的算子节点（F-007）

**信源**：`common/_topology.py` L436-L663

### 构造函数

```python
Operator(onnx_name, scope, type, raw_operator, target_opset, scope_inst)
```

| 属性 | 类型 | 说明 |
|------|------|------|
| `onnx_name` | str | ONNX 图中唯一算子名 |
| `scope` | str | 所属 Scope 名 |
| `type` | str | 算子别名字符串（如 `"SklearnLinearClassifier"`） |
| `raw_operator` | sklearn estimator | 原始 sklearn 估计器对象 |
| `target_opset` | int | 目标 opset 版本 |
| `inputs` | OperatorList | 输入变量列表（继承 list，append 时自动建立双向链接） |
| `outputs` | OperatorList | 输出变量列表 |

### 关键方法

| 方法 | 说明 |
|------|------|
| `infer_types()` | 通过 `_registration.get_shape_calculator(self.type)` 查找并调用 shape calculator |
| `has_attribute(attr)` | 检查 raw_operator 是否有指定属性 |

### OperatorList 双向链接

`OperatorList` 继承自 `list`，重写了 `append()` 方法，在添加变量时自动调用：
- `v.set_parent(self)` —— 设置变量的父算子
- `v.add_operator(self, as_input=True/False)` —— 建立反向引用

这确保 Variable 和 Operator 之间始终保持双向链接一致性。

## Scope 类——命名空间与容器（F-008）

**信源**：`common/_topology.py` L665-L958

### 构造函数

```python
Scope(name, target_opset, custom_conversion_functions=None,
      custom_shape_calculators=None, options=None)
```

### 核心属性

| 属性 | 说明 |
|------|------|
| `onnx_variable_names` | set，已分配的 ONNX 变量名集合（去重用） |
| `onnx_operator_names` | set，已分配的 ONNX 算子名集合 |
| `target_opset` | 目标 opset 版本 |
| `options` | 转换器选项字典 |

### 关键方法

| 方法 | 说明 |
|------|------|
| `get_unique_variable_name(seed)` | 基于 seed 生成 C 风格合法标识符（特殊字符→下划线，首字符数字则加 `_` 前缀，重名追加数字后缀） |
| `get_unique_operator_name(seed)` | 同理，生成唯一算子名 |
| `declare_local_variable(raw_name, type=None)` | 创建 Variable 并注册；同一 raw_name 多次声明形成 name mapping 列表（后声明的隐藏前声明） |
| `declare_local_operator(type, raw_model)` | 创建 Operator 实例 |
| `get_options(model, default_values, fail)` | 按 `type(model)` 和 `id(model)` 两级查找 options |

### 唯一命名规则示例

```
seed: "LogisticRegression" → "LogisticRegression"
seed: "input" → "input"
seed: "123abc" → "_123abc"（首字符为数字，前加下划线）
seed: "a.b" → "a_b"（点替换为下划线）
重名: "variable" → "variable" → "variable1" → "variable2"
```

## Topology 类——计算图中间表示（F-009）

**信源**：`common/_topology.py` L960-L1033

### 构造函数

```python
Topology(model, default_batch_size=1, initial_types=None,
         target_opset=None, custom_conversion_functions=None,
         custom_shape_calculators=None, registered_models=None)
```

### 核心属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `scopes` | list | Scope 列表（当前实现只允许一个 Scope） |
| `raw_model` | RawModelContainerNode | 包装原始 sklearn 模型 |
| `model_aliases` | dict | 自定义类型→别名映射，格式 `"{ClassName}_{id(self)}"` |
| `custom_conversion_functions` | dict | 用户自定义 converter 覆盖 |
| `custom_shape_calculators` | dict | 用户自定义 shape_calculator 覆盖 |
| `target_opset` | int | 目标 opset 版本 |

### 单 Scope 约束（F-010）

`declare_scope()` 方法显式检查：

```python
def declare_scope(self, name=""):
    if len(self.scopes) != 0:
        raise RuntimeError("Only one scope can be created.")
    # ...
```

声明 Scope 时自动将 `initial_types` 中的变量声明为 local_input。

### 转换器查找优先级链（F-012）

`Topology.call_converter(operator, container)` 的四级查找顺序：

1. `custom_conversion_functions[type(operator.raw_operator)]` —— 用户按类型注册的 custom 函数
2. `custom_conversion_functions[operator.type]` —— 用户按别名注册的 custom 函数
3. `operator.raw_operator.onnx_converter()` —— 模型对象自带的 `onnx_converter()` 方法（OnnxOperatorMixin）
4. `_registration.get_converter(operator.type)` —— 全局注册池

shape calculator 有完全相同的四级优先级链（`call_shape_calculator`）。

### 数据流调度算法——convert_operators（F-011）

**信源**：`common/_topology.py` L1239-L1436

采用"输入已就绪则调度"的固定点迭代算法：

```
1. 初始化：
   - input 变量标记 is_fed=True
   - 所有算子标记 is_evaluated=False

2. 迭代循环：
   - changes = 0
   - 遍历所有未评估算子：
     - 若所有 inputs 都 is_fed=True 且自身 is_evaluated=False：
       a. 调用 operator.infer_types()（shape calculator 推断输出形状）
       b. 调用 call_converter(operator, container)（生成 ONNX 节点）
       c. 标记 operator.is_evaluated=True
       d. 将其 outputs 标记为 is_fed=True
       e. changes += 1
   - _propagate_status()：沿 ONNX nodes 传播 fed 状态
   - 处理多算子共享输出的"取消 fed"逻辑
   - 直到 changes == 0（不动点）

3. 验证：所有算子必须 is_evaluated=True，否则报错
```

关键特性：converter 执行过程中可以**追加新的 Operator 到拓扑**，这些新算子会在下一轮迭代中被调度，直到不动点。

## ModelComponentContainer——ONNX 图构建器（F-022）

**信源**：`common/_container.py` L216-L1072

收集构建 ONNX GraphProto 所需的全部材料：

| 属性 | 类型 | 说明 |
|------|------|------|
| `inputs` | list | ValueInfoProto 列表（图输入） |
| `outputs` | list | ValueInfoProto 列表（图输出） |
| `initializers` | list | TensorProto 列表（模型权重/常量） |
| `nodes` | list | NodeProto 列表（ONNX 算子节点） |
| `value_info` | list | 中间变量类型信息 |
| `node_domain_version_pair_sets` | set | 使用到的 (domain, version) 集合 |
| `target_opset_all` | dict | 按 domain 指定不同 opset 版本 |

### 关键方法

| 方法 | 说明 |
|------|------|
| `add_node(op_type, inputs, outputs, op_domain, op_version, name, **attrs)` | 创建 NodeProto 并追加到 nodes；自动校验白/黑名单、opset 版本兼容性、inputs/outputs 交集为空 |
| `add_initializer(name, onnx_type, shape, content)` | 创建 TensorProto；含内容去重（相同序列化内容复用 initializer，通过 Identity 节点引用） |
| `ensure_topological_order()` | 执行拓扑排序，检测环和断图 |
| `add_input(name, onnx_type, shape, doc_string)` | 添加图输入 |
| `add_output(name, onnx_type, shape, doc_string)` | 添加图输出 |

### 白/黑名单过滤（F-033）

`_WhiteBlackContainer` 类提供 `check_white_black_list(node_type)` 方法：
- 若设置了 `_white_op` 且 node_type 不在其中 → 抛 RuntimeError
- 若设置了 `_black_op` 且 node_type 在其中 → 抛 RuntimeError

## convert_topology——从 IR 到 ModelProto（F-023）

**信源**：`common/_topology.py` L1484-L1694

流程：

```
convert_topology(topology, model_name, doc_string, target_opset, options, ...)
  │
  ├─ 1. 解析 target_opset（支持 int 或 dict）
  │     校验不超过 onnx 包支持版本和 latest tested 版本
  ├─ 2. 创建 ModelComponentContainer
  ├─ 3. topology.convert_operators(container)  → 数据流调度（F-011）
  ├─ 4. make_model_from_container() → 构建 GraphProto → ModelProto
  ├─ 5. 设置 ir_version（OPSET_TO_IR_VERSION 映射）
  │     producer_name="skl2onnx", producer_version=__version__
  ├─ 6. 若 remove_identity=True → onnx_remove_node_identity() 删除冗余 Identity
  └─ 7. 递归处理 container.local_functions 中的子函数（FunctionProto）
```

## OPSET 到 IR_VERSION 映射（F-024）

**信源**：`common/_topology.py` L41-L78

| opset 范围 | IR_VERSION |
|-----------|------------|
| 1-7 | 3 |
| 8-9 | 4 |
| 10 | 5 |
| 11 | 6 |
| 12-14 | 7 |
| 15-18 | 8 |
| 19-20 | 9 |
| 21-25 | 10 |

ML 域映射：`OPSET_ML_TO_OPSET = {1: 11, 2: 15, 3: 18}`。
