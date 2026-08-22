---
type: concept
title: "转换管线：解析sklearn→拓扑IR→数据流调度→ONNX组装"
description: "convert_sklearn 主流程详解：从 sklearn 对象到 ONNX ModelProto 经历的解析、形状推断、转换、组装四个阶段的具体执行逻辑"
sources:
  references: [../references/convert-api.md, ../references/topology-ir.md]
  facts: [F-003, F-004, F-016, F-017, F-018, F-023, F-011, F-032]
---

# 转换管线：解析sklearn→拓扑IR→数据流调度→ONNX组装

## 核心理解

`convert_sklearn()` 是 sklearn-onnx 的主入口，它编排了一条完整的类编译器管线。理解这条管线的关键是区分四个阶段的职责边界，以及每个阶段的输入输出是什么。

## 阶段总览

```
输入: sklearn model + initial_types + options
  │
  ▼
┌─────────────────────────────────────────┐
│ 阶段1: Parse（解析）                      │
│ parse_sklearn_model() → Topology         │
│ 输入: sklearn对象树                       │
│ 输出: 粗粒度计算图 (Scope/Operator/Variable)│
└────────────────┬────────────────────────┘
                 ▼
┌─────────────────────────────────────────┐
│ 阶段2+3: Shape Infer + Convert（调度转换）│
│ topology.convert_operators(container)    │
│ 输入: Topology IR                        │
│ 输出: ModelComponentContainer（细粒度节点）│
└────────────────┬────────────────────────┘
                 ▼
┌─────────────────────────────────────────┐
│ 阶段4: Assemble（组装）                   │
│ convert_topology() → ModelProto          │
│ 输入: ModelComponentContainer            │
│ 输出: onnx.ModelProto                    │
└─────────────────────────────────────────┘
```

## 阶段1：Parse——构建粗粒度 IR

### 入口函数

```python
parse_sklearn_model(model, initial_types, target_opset,
                    custom_conversion_functions, custom_shape_calculators,
                    custom_parsers, options)
```

该函数创建 `Topology` 实例，声明唯一的 `Scope`，将 `initial_types` 声明为图的根输入变量，然后调用 `_parse_sklearn()` 递归解析模型。

### _parse_sklearn 分发器

`_parse_sklearn(scope, model, inputs, custom_parsers, alias)` 是解析阶段的核心分发器，查找顺序为：

1. 若指定了 alias → 直接调用 `_parse_sklearn_simple_model`
2. `custom_parsers[type(model)]` → 用户自定义 parser
3. `sklearn_parsers_map[type(model)]` → 内置专用 parser
4. 若 `isinstance(model, Pipeline)` → `_parse_sklearn_pipeline`
5. 默认 → `_parse_sklearn_simple_model`

### 简单模型解析

`_parse_sklearn_simple_model()` 根据 model 的 Mixin 类型声明不同数量的输出变量：

| 模型类型 | 输出变量 | 类型 |
|---------|---------|------|
| ClassifierMixin / classifier_list | `label` + `probabilities` | Int64TensorType + guess_tensor_type |
| ClusterMixin / cluster_list | `label` + `scores` | Int64TensorType + guess_tensor_type |
| OutlierMixin / outlier_list | `label` + `scores` | Int64TensorType + FloatTensorType |
| NearestNeighbors | `index` + `distance` | Int64TensorType + FloatTensorType |
| GaussianMixture | `label` + `probabilities` (+ score_samples) | Int64TensorType + guess_tensor_type |
| Transformer/Regressor（其他） | `variable`（单个输出） | guess_tensor_type |

若 model 定义了 `onnx_parser()` 方法，则优先使用该方法返回的输出名列表。

### Classifier 后处理——ZipMap 注入

`_parse_sklearn_classifier()` 在 simple_model 解析后，根据 options.zipmap 决定是否注入 ZipMap 算子：

| zipmap 选项 | 输出格式 |
|------------|---------|
| `True`（默认） | `output_label` + `output_probability`（SequenceType(DictionaryType)，字典序列） |
| `"columns"` | `output_label` + 每个类别一个概率列（多输出张量） |
| `False` | `label` + `probabilities`（原始张量，无字典包装） |

Pipeline 中间步骤的 classifier 自动注入 `zipmap: False`，避免中间步骤产生字典输出。

### Pipeline 解析

`_parse_sklearn_pipeline()` 遍历 `model.steps`：
1. 将前一步的 outputs 作为下一步的 inputs
2. 依次递归调用 `_parse_sklearn()`
3. 对中间 classifier 步骤自动注入 `zipmap: False` 选项

### FeatureUnion 解析

`_parse_sklearn_feature_union()`：
1. 对每个 transformer 并行（顺序）调用 `_parse_sklearn()`
2. 若有 `transformer_weights` 则插入 `SklearnMultiply` 算子加权
3. 最后所有子输出通过 `SklearnConcat` 拼接

### ColumnTransformer 解析

`_parse_sklearn_column_transformer()`：
1. 遍历 `model.transformers_`
2. 通过 `get_column_indices()` 解析列索引（支持 int/str/slice/list）
3. 对每列输入插入 `SklearnArrayFeatureExtractor` 提取列
4. 若多列输入且目标算子不是 OneHotEncoder/OrdinalEncoder/ColumnTransformer，先通过 `SklearnConcat` 合并
5. 递归调用 `_parse_sklearn()` 转换子 transformer
6. `"drop"` 字符串跳过，`"passthrough"` 直接透传输入
7. 最终所有子输出通过 `SklearnConcat` 拼接

### final_types——输出类型覆盖

`parse_sklearn()` 支持 `final_types` 参数，用于预先声明输出变量：
- 正常解析得到 `hidden_outputs`
- 若数量不匹配抛 RuntimeError
- 对每对 (hidden, declared)：若 declared.type 为 None 插入 SklearnIdentity，否则插入 SklearnCast
- hidden 标记 `is_leaf=False`，declared 标记 `is_leaf=True`

## 阶段2+3：数据流调度——convert_operators

### 状态机模型

每个 Variable 有三个布尔状态：

| 状态 | 含义 |
|------|------|
| `is_fed` | 该变量是否已有生产者（输入是否就绪） |
| `is_root` | 是否为图的根输入（由 initial_types 声明） |
| `is_leaf` | 是否为图的最终输出 |

每个 Operator 有一个状态：

| 状态 | 含义 |
|------|------|
| `is_evaluated` | 该算子是否已完成转换 |

### 固定点迭代算法

```
初始化:
  - 所有 is_root=True 的 Variable → is_fed=True
  - 所有 Operator → is_evaluated=False

循环（直到 changes == 0）:
  changes = 0
  for each operator in topology:
    if operator.is_evaluated:
      continue
    if all(input.is_fed for input in operator.inputs):
      // 阶段2: Shape Inference
      operator.infer_types()  // 调用 shape_calculator
      
      // 阶段3: Convert
      topology.call_converter(operator, container)
      
      // 更新状态
      operator.is_evaluated = True
      for output in operator.outputs:
        output.is_fed = True
      changes += 1
  
  // 沿 ONNX nodes 传播 fed 状态
  _propagate_status(container)
  
  // 处理多算子共享输出的"取消 fed"逻辑

验证:
  assert all(operator.is_evaluated for operator in topology)
```

### shape_calculator 的作用

shape_calculator 在 converter 之前调用，负责推断输出变量的类型和形状。它接收一个参数 `operator`，通过 `operator.inputs` 和 `operator.outputs` 访问变量，设置输出变量的 `type` 属性。

例如，线性分类器的 shape_calculator 会设置：
- `operator.outputs[0].type = Int64TensorType([None, 1])`（label 输出）
- `operator.outputs[1].type = FloatTensorType([None, n_classes])`（probability 输出）

### converter 的作用

converter 接收三个参数 `(scope, operator, container)`，负责向 container 中追加细粒度 ONNX 节点：

```python
def convert_sklearn_linear_classifier(scope, operator, container):
    # 1. 从 operator.raw_operator 获取 sklearn 模型参数
    coef = operator.raw_operator.coef_
    intercept = operator.raw_operator.intercept_
    
    # 2. 获取输入输出的 ONNX 名称
    input_name = operator.inputs[0].onnx_name
    label_name = operator.outputs[0].onnx_name
    prob_name = operator.outputs[1].onnx_name
    
    # 3. 向 container 添加 ONNX 节点
    container.add_node(
        'LinearClassifier', input_name, [label_name, prob_name],
        op_domain='ai.onnx.ml', op_version=1,
        coefficients=coef.flatten().tolist(),
        intercepts=intercept.tolist(),
        multi_class=1 if n_classes > 2 else 0,
        post_transform='LOGISTIC',
        ...
    )
```

## 阶段4：Assemble——组装 ModelProto

`convert_topology()` 完成最后的组装：

1. **opset 解析**：支持 int（统一版本）或 dict（按 domain 指定版本），校验不超过 onnx 包支持版本和 latest tested 版本
2. **创建 Container**：实例化 `ModelComponentContainer`，持有 nodes/initializers/inputs/outputs
3. **执行调度**：调用 `topology.convert_operators(container)`（阶段2+3）
4. **拓扑排序**：`container.ensure_topological_order()` 对 nodes 执行拓扑排序，检测环和断图
5. **构建 GraphProto**：`make_model_from_container()` 使用 `onnx.helper.make_graph()` 构建计算图
6. **构建 ModelProto**：`onnx.helper.make_model()` 设置：
   - `ir_version`（根据 OPSET_TO_IR_VERSION 映射表）
   - `producer_name = "skl2onnx"`
   - `producer_version = __version__`
   - `opset_import`（主域 + 用到的其他域）
   - `doc_string`
7. **Identity 消除**：若 `remove_identity=True`，调用 `onnx_remove_node_identity()` 删除冗余 Identity 节点
8. **子函数处理**：递归处理 `container.local_functions` 中的 FunctionProto

## to_onnx 的简化路径

`to_onnx()` 是 `convert_sklearn()` 的简化封装，增加了两个便利：

1. **Mixin 快捷路径**：若 model 是 `OnnxOperatorMixin` 实例，直接调用 `model.to_onnx()`（内部仍走 convert_sklearn）
2. **自动类型推断**：从训练数据 X 自动推断 `initial_types`
   - numpy 数组 → 取第一行，dtype 映射，shape[0] 设为 None（batch）
   - DataFrame → 每列一个输入
   - list → 直接使用

## 关联概念

- [sklearn-onnx 整体架构：四阶段类编译器管线](00-overall-architecture.md) — 架构全局视图
- [Topology IR：Scope/Variable/Operator/Component/ModelComponentContainer](02-topology-ir.md) — IR 核心类详解
- [Pipeline/FeatureUnion/ColumnTransformer处理、类型推断initial_types](05-pipeline-feature-union.md) — 复合模型解析细节
