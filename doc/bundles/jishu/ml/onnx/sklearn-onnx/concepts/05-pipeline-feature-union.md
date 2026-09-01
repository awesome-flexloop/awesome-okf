---
type: concept
title: "Pipeline/FeatureUnion/ColumnTransformer 处理、类型推断 initial_types"
description: "sklearn-onnx 对复合模型（Pipeline、FeatureUnion、ColumnTransformer）的递归解析机制、ZipMap 注入时机、initial_types 类型声明与自动推断、final_types 输出覆盖"
sources:
  references: [../references/convert-api.md, ../references/topology-ir.md]
  facts: [F-017, F-018, F-019, F-020, F-021, F-030, F-031, F-032]
---

# Pipeline/FeatureUnion/ColumnTransformer 处理、类型推断 initial_types

## 核心理解

sklearn 的真正威力来自复合模型：Pipeline 串联多个步骤，FeatureUnion 并行拼接特征，ColumnTransformer 按列选择不同转换器。sklearn-onnx 通过**递归解析**处理这些复合结构——parser 函数递归调用 `_parse_sklearn()` 处理子估计器，在 IR 层面构建出与 sklearn 对象树同构的粗粒度 Operator 图。initial_types 是整个转换的起点，声明了模型输入的名称和类型。

## initial_types：转换的起点

### 什么是 initial_types？

`initial_types` 是 `convert_sklearn()` 的必填参数（除非 model 实现了 `infer_initial_types()`），它告诉 sklearn-onnx 模型的输入长什么样：

```python
initial_types = [
    ('input', FloatTensorType([None, 4])),  # 变量名"input"，float32张量，shape=[batch, 4]
]
```

格式为 `List[Tuple[str, DataType]]`，每个元素是 `(变量名字符串, 类型对象)`。

### shape 语义

| shape 值 | 含义 | 示例 |
|----------|------|------|
| `None` | 动态维度（通常是 batch size） | `[None, 4]` = batch×4 特征 |
| 整数 | 静态维度 | `[None, 10]` = batch×10 特征 |
| 字符串 | dim_param（符号化维度名） | `[None, 'n_features']` |
| `[]` | 标量 | FloatType() 的 shape 为 [1,1] |

### DataType 类型体系

```
DataType
  ├── 标量类型（shape 固定为 [1,1]）
  │     ├── FloatType
  │     ├── DoubleType
  │     ├── Int64Type
  │     ├── Int32Type
  │     ├── StringType
  │     └── UInt8Type, Int8Type, ...
  │
  ├── 张量类型（TensorType 子类）
  │     ├── FloatTensorType(shape)
  │     ├── DoubleTensorType(shape)
  │     ├── Int64TensorType(shape)
  │     ├── Int32TensorType(shape)
  │     ├── StringTensorType(shape)
  │     ├── BooleanTensorType(shape)
  │     └── Int8/16/32/64, UInt8/16/32/64, Float16, Complex64/128
  │
  └── 容器类型
        ├── SequenceType(element_type)
        └── DictionaryType(key_type, value_type)
```

### 常用 initial_types 示例

```python
from skl2onnx.common.data_types import (
    FloatTensorType, DoubleTensorType, Int64TensorType, StringTensorType
)

# 经典：4维float特征输入（如 Iris 数据集）
initial_types = [('input', FloatTensorType([None, 4]))]

# 多输入：一个数值特征 + 一个字符串特征
initial_types = [
    ('num_input', FloatTensorType([None, 10])),
    ('str_input', StringTensorType([None, 1])),
]

# 字符串输入（如 TF-IDF 的原始文本）
initial_types = [('input', StringTensorType([None, 1]))]

# double 精度
initial_types = [('input', DoubleTensorType([None, 784]))]
```

## 自动类型推断：guess_initial_types / to_onnx

`to_onnx()` 函数可以从训练数据自动推断 `initial_types`，无需手动声明：

```python
# 从 numpy 数组自动推断
X_train = np.random.randn(100, 4).astype(np.float32)
model_onnx = to_onnx(model, X_train)  # 自动推断为 FloatTensorType([None, 4])

# 从 pandas DataFrame 自动推断（每列一个输入）
import pandas as pd
df = pd.DataFrame({'age': [25.0, 30.0], 'name': ['Alice', 'Bob']})
model_onnx = to_onnx(model, df)  # age→FloatTensorType, name→StringTensorType
```

推断规则：

| 输入类型 | 推断结果 |
|---------|---------|
| `np.ndarray` | 取第一行 `X[:1]`，dtype 通过 `_guess_numpy_type` 映射为 TensorType 子类，shape[0] 设为 None |
| pandas DataFrame | 每列一个输入，列名为变量名，shape=[None,1]，列 dtype 决定 TensorType |
| list | 直接作为 initial_types 使用 |

`_guess_numpy_type` 处理 numpy dtype 到 TensorType 的映射，包括 pandas StringDtype 支持。

## 简单模型的解析输出

`_parse_sklearn_simple_model()` 根据 model 的 Mixin 类型声明不同数量和类型的输出变量：

### 分类器（ClassifierMixin）

输出两个变量：
1. **label**：`Int64TensorType([None, 1])`——预测类别标签
2. **probabilities**：`guess_tensor_type(inputs[0].type)`——各类别概率（float/double，与输入精度匹配）

### 回归器（RegressorMixin / TransformerMixin）

输出一个变量：
- **variable**：`guess_tensor_type(inputs[0].type)`——回归值或变换后的特征

### 聚类器（ClusterMixin）

输出两个变量：
1. **label**：`Int64TensorType([None, 1])`——簇标签
2. **scores**：`guess_tensor_type(inputs[0].type)`——到各簇中心的距离/得分

### 离群点检测（OutlierMixin）

输出两个变量：
1. **label**：`Int64TensorType([None, 1])`——是否离群（±1）
2. **scores`：`FloatTensorType(...)`——异常分数

### K近邻（NearestNeighbors）

输出两个变量：
1. **index**：`Int64TensorType(...)`——最近邻索引
2. **distance**：`FloatTensorType(...)`——最近邻距离

## ZipMap 注入：分类器输出后处理

分类器在解析后会根据 `zipmap` 选项注入 ZipMap 算子，将原始概率张量转换为更友好的输出格式：

### zipmap 选项的三种值

| 选项值 | 输出格式 | 适用场景 |
|--------|---------|---------|
| `True`（默认） | `output_label` + `output_probability`（序列字典：`[{class0: p0, class1: p1}, ...]`） | 与 ONNX ML 工具链兼容，便于按类名查概率 |
| `"columns"` | `output_label` + 每个类别一个概率列（如 `output_probability_0`, `output_probability_1`, ...） | 某些推理引擎不支持序列字典时 |
| `False` | `label` + `probabilities`（原始张量） | Pipeline 中间步骤、需要张量输入的后续算子 |

### 注入位置

ZipMap 在 parser 阶段（而非 converter 阶段）注入。`_parse_sklearn_classifier()` 在 `_parse_sklearn_simple_model()` 之后：
1. 如果 `options.zipmap` 不为 False
2. 在分类器输出后追加 `SklearnZipMap` 或 `SklearnZipMapColumns` 算子
3. 将最终输出变量标记为 leaf

### Pipeline 中间步骤自动关闭 zipmap

`_parse_sklearn_pipeline()` 在遍历 steps 时，对中间（非最后一步）classifier 自动注入 `zipmap: False` 选项，因为中间步骤输出字典序列会破坏后续步骤的张量计算。只有最终分类器步骤才保留 ZipMap。

## Pipeline 解析：顺序串联

Pipeline 是最常用的复合模型，将多个估计器串联成链：

```python
pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('pca', PCA(n_components=2)),
    ('clf', LogisticRegression())
])
```

### 解析流程

`_parse_sklearn_pipeline(scope, model, inputs, custom_parsers)`：

```
输入: initial_types 声明的根变量
  │
  ▼
┌─────────────────────────────────────┐
│ Step 0: scaler (StandardScaler)     │
│ inputs: [input]                     │
│ outputs: [variable0]                │
└───────────────┬─────────────────────┘
                │ variable0
                ▼
┌─────────────────────────────────────┐
│ Step 1: pca (PCA)                   │
│ inputs: [variable0]                 │
│ outputs: [variable1]                │
└───────────────┬─────────────────────┘
                │ variable1
                ▼
┌─────────────────────────────────────┐
│ Step 2: clf (LogisticRegression)    │
│ inputs: [variable1]                 │
│ options: zipmap=True (最终步)        │
│ outputs: [label, probabilities]     │
│   → ZipMap 注入 →                    │
│   [output_label, output_probability]│
└─────────────────────────────────────┘
```

关键逻辑：
1. 遍历 `model.steps`，前一步的 outputs 作为下一步的 inputs
2. 对中间 classifier 步骤自动注入 `zipmap: False`
3. 最后一步的输出作为 Pipeline 的输出

### Converter 阶段

Pipeline 的 converter（`convert_pipeline`）在拓扑转换阶段再次遍历 steps：
1. 通过 `_parse_sklearn` 逐个转换子估计器
2. 最后用 Identity 或 Cast 节点连接到 Pipeline 的 outputs（处理类型/名称不匹配）

## FeatureUnion 解析：并行+加权+拼接

FeatureUnion 将多个转换器的输出**并排拼接**（水平拼接，增加特征维度）：

```python
union = FeatureUnion([
    ('tfidf', TfidfVectorizer()),
    ('svd', TruncatedSVD(n_components=10)),
], transformer_weights={'tfidf': 0.5, 'svd': 1.0})
```

### 解析流程

`_parse_sklearn_feature_union(scope, model, inputs, custom_parsers)`：

```
                    inputs
                   /      \
                  /        \
    ┌──────────────┐  ┌──────────────┐
    │  tfidf       │  │  svd         │
    │  _parse()    │  │  _parse()    │
    └──────┬───────┘  └──────┬───────┘
           │                 │
           ▼                 ▼
    ┌──────────────┐  ┌──────────────┐
    │ Multiply(0.5)│  │ Multiply(1.0)│  ← transformer_weights 加权
    └──────┬───────┘  └──────┬───────┘
           │                 │
           └────────┬────────┘
                    ▼
            ┌──────────────┐
            │   Concat     │  ← SklearnConcat 水平拼接
            └──────────────┘
```

1. 对 `model.transformer_list` 中每个 transformer 并行（顺序）调用 `_parse_sklearn()`
2. 若有 `transformer_weights`，在每个分支后插入 `SklearnMultiply` 算子加权
3. 所有分支输出通过 `SklearnConcat` 水平拼接为最终输出

## ColumnTransformer 解析：按列选择+逐转换器+拼接

ColumnTransformer 是最复杂的复合模型，对不同列应用不同转换器：

```python
ct = ColumnTransformer([
    ('num', StandardScaler(), [0, 1, 2]),       # 数值列标准化
    ('cat', OneHotEncoder(), [3, 4]),           # 分类列独热编码
    ('text', TfidfVectorizer(), 'text_col'),    # 文本列TF-IDF
])
```

### 解析流程

`_parse_sklearn_column_transformer()` 是最复杂的 parser：

```
                          inputs
           ┌──────────┬──────────┬──────────┐
           │          │          │          │
    ┌──────▼───┐ ┌────▼────┐ ┌───▼──────┐
    │ArrayFeat │ │ArrayFeat│ │ArrayFeat │  ← SklearnArrayFeatureExtractor 列提取
    │Ext([0,1,2])│ │Ext([3,4])│ │Ext('text_col')│
    └──────┬───┘ └────┬────┘ └───┬──────┘
           │          │          │
           ▼          ▼          ▼
    ┌──────────┐ ┌─────────┐ ┌──────────┐
    │Standard- │ │OneHot-  │ │Tfidf-    │
    │Scaler    │ │Encoder  │ │Vectorizer│  ← 逐列递归 _parse_sklearn()
    └──────┬───┘ └────┬────┘ └───┬──────┘
           │          │          │
           └──────────┼──────────┘
                      ▼
             ┌─────────────────┐
             │     Concat      │  ← SklearnConcat 拼接
             └─────────────────┘
```

### 详细步骤

1. **解析列索引**：`get_column_indices(column_indices, inputs, multiple=True)` 支持：
   - `int`：单列索引
   - `str`：列名（DataFrame 输入时）
   - `slice`：列切片
   - `list`：多列索引列表
   - `"drop"`：跳过该 transformer
   - `"passthrough"`：直接透传输入列

2. **列提取**：对每列输入插入 `SklearnArrayFeatureExtractor` 算子提取列

3. **条件合并**：若多列输入且目标算子**不是** OneHotEncoder/OrdinalEncoder/ColumnTransformer，先通过 `SklearnConcat` 合并多列为一个张量再送入子转换器（OneHotEncoder 等需要看到原始多列，不需要预合并）

4. **递归转换**：调用 `_parse_sklearn()` 转换子 transformer

5. **最终拼接**：所有子输出通过 `SklearnConcat` 水平拼接

## final_types：输出类型/名称覆盖

`parse_sklearn()` 支持 `final_types` 参数，允许用户预先声明输出变量的名称和类型：

```python
final_types = [
    ('my_label', Int64TensorType([None, 1])),
    ('my_proba', FloatTensorType([None, 3])),
]
model_onnx = convert_sklearn(clf, initial_types=..., final_types=final_types)
```

### 工作机制

1. 正常解析得到 `hidden_outputs`（parser 自然产生的输出变量）
2. 比较数量：若 hidden 和 declared 数量不匹配，抛 RuntimeError
3. 对每对 (hidden, declared)：
   - 若 `declared.type is None` → 插入 `SklearnIdentity` 节点（仅改名）
   - 若 `declared.type` 不为 None → 插入 `SklearnCast` 节点（改名+类型转换）
4. hidden 标记 `is_leaf=False`，declared 标记 `is_leaf=True`

这使得用户可以控制输出变量的名称和类型，而不必接受 parser 自动生成的默认名称和类型。

## 复合模型的设计模式总结

| 复合模型 | 连接方式 | 关键 parser 逻辑 | 特殊处理 |
|---------|---------|-----------------|---------|
| Pipeline | 顺序串联 | 前步 outputs → 后步 inputs | 中间 classifier 自动 zipmap=False |
| FeatureUnion | 并行拼接 | 各分支独立 parse → Concat | transformer_weights 加权 |
| ColumnTransformer | 按列分支 | ArrayFeatureExtractor 列切片 → 逐转换器 parse → Concat | OneHotEncoder 等不预合并多列 |

三者都通过递归调用 `_parse_sklearn()` 处理子估计器，形成与 sklearn 对象树同构的 IR 图结构。递归解析是 sklearn-onnx 处理任意嵌套复合模型的核心机制。

## 关联概念

- [转换管线：解析sklearn→拓扑IR→数据流调度→ONNX组装](01-conversion-pipeline.md) — parser 在四阶段管线中的位置
- [Topology IR：Scope/Variable/Operator/Component/ModelComponentContainer](02-topology-ir.md) — Variable/Operator 如何构建复合模型的 IR 图
- [Pipeline 完整转换](../examples/pipeline-conversion.md) — Pipeline 转换的完整代码示例
