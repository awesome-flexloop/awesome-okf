---
type: concept
title: "树模型转换范式：LightGBM/XGBoost/CoreML算子集与属性模板"
description: "onnxmltools 树模型转换的统一范式：TreeEnsembleClassifier/Regressor属性对模板、节点编码格式、LightGBM/XGBoost/H2O的共性与差异、zipmap输出控制、split大数精度控制、without_onnx_ml的Hummingbird后处理"
sources:
  references: [../references/registration-types.md, ../references/topology-ir.md, ../references/convert-entry.md]
  facts: [F-012, F-013, F-030, F-033, F-035, F-036]
---

# 树模型转换范式：LightGBM/XGBoost/CoreML算子集与属性模板

## 核心理解

树模型（GBDT、随机森林、决策树）是 onnxmltools **自有IR路径最核心、最成熟的支持领域**。LightGBM、XGBoost、H2O GBM 虽然接口和训练方式不同，但在转换时都映射到 ONNX-ML 的同一组算子：

- **TreeEnsembleClassifier**：树分类器（输出类别标签和概率）
- **TreeEnsembleRegressor**：树回归器（输出连续值）
- **ZipMap**：将概率张量映射为 `{类别: 概率}` 字典（可选）

所有树模型共享 `tree_ensemble.py` 提供的属性对模板，通过统一的 `add_node` 函数填充树结构，然后交由各自的 converter 生成 ONNX 节点。

## TreeEnsemble 属性对模板（F-030）

ONNX TreeEnsemble 算子使用属性字典（attributes）而非嵌套消息结构来表示树。`tree_ensemble.py` 提供两个默认模板初始化函数：

### TreeEnsembleClassifier 属性模板

```python
def get_default_tree_classifier_attribute_pairs():
    return {
        # 树结构字段（所有树共享的平行数组）
        'nodes_treeids': [],               # 每个节点所属树ID
        'nodes_nodeids': [],               # 节点在树内的ID
        'nodes_featureids': [],            # 分裂特征ID
        'nodes_modes': [],                 # 节点模式（'BRANCH_LEQ'/'LEAF'等）
        'nodes_values': [],                # 分裂阈值
        'nodes_truenodeids': [],           # 左子节点ID（条件为真时）
        'nodes_falsenodeids': [],          # 右子节点ID（条件为假时）
        'nodes_missing_value_tracks_true': [],  # 缺失值走向（True→左子树）
        'nodes_hitrates': [],              # 节点命中率（可选统计）
        
        # 叶子权重字段（分类器）
        'class_treeids': [],               # 叶子节点所属树ID
        'class_nodeids': [],               # 叶子节点ID
        'class_ids': [],                   # 类别ID
        'class_weights': [],               # 类别权重
        
        'post_transform': 'NONE',          # 后处理（'SOFTMAX'/'LOGISTIC'/'NONE'等）
        'classlabels_strings': [],         # 字符串类别标签（与classlabels_int64s二选一）
        'classlabels_int64s': [],          # 整数类别标签
        'base_values': [],                 # 基值（初始预测）
    }
```

### TreeEnsembleRegressor 属性模板

```python
def get_default_tree_regressor_attribute_pairs():
    return {
        # 树结构字段（与Classifier完全相同）
        'nodes_treeids': [], 'nodes_nodeids': [], 'nodes_featureids': [],
        'nodes_modes': [], 'nodes_values': [],
        'nodes_truenodeids': [], 'nodes_falsenodeids': [],
        'nodes_missing_value_tracks_true': [], 'nodes_hitrates': [],
        
        # 叶子权重字段（回归器）
        'target_treeids': [],              # 叶子节点所属树ID
        'target_nodeids': [],              # 叶子节点ID
        'target_ids': [],                  # 目标ID（多目标回归时使用）
        'target_weights': [],              # 目标权重
        
        'n_targets': 1,                    # 目标数量
        'post_transform': 'NONE',
        'base_values': [],
    }
```

### add_node：统一节点填充函数

```python
def add_node(attr_pairs, is_classifier, tree_id, tree_weight, node_id,
             feature_id, mode, value, true_child_id, false_child_id,
             weights, weight_id_bias=0, missing_tracks_true=False, hitrates=0.0):
```

关键行为：
- **tree_weight 归一化**：叶子节点权重乘以 `tree_weight`，确保多棵树（如boosting）的权重和正确
- **平行数组填充**：按字段名append到对应的属性列表中
- **分类器/回归器分支**：`is_classifier=True` 时填充 `class_*` 字段，否则填充 `target_*` 字段

### 节点模式（nodes_modes）

| 模式 | 含义 |
|------|------|
| `BRANCH_LEQ` | 分裂节点：value ≤ threshold → 左子树，否则→右子树 |
| `BRANCH_LT` | 分裂节点：value < threshold → 左子树 |
| `BRANCH_GTE` | 分裂节点：value ≥ threshold → 左子树 |
| `BRANCH_GT` | 分裂节点：value > threshold → 左子树 |
| `BRANCH_EQ` | 分裂节点：value == threshold → 左子树 |
| `BRANCH_NEQ` | 分裂节点：value != threshold → 左子树 |
| `LEAF` | 叶子节点（无子节点） |

## 三框架树转换共性

LightGBM、XGBoost、H2O 的树模型转换遵循相同的高层模式：

```
原始模型 → parse遍历树结构 → 填充TreeEnsemble属性对 → converter生成ONNX节点
                │
                ├─ 遍历每棵树（tree_id从0开始）
                ├─ 遍历每个节点
                │   ├─ 内部节点：提取feature_id、threshold、左右子节点、缺失值方向
                │   └─ 叶子节点：提取权重值（按tree_weight归一化）
                ├─ 设置base_values（初始预测/偏置）
                └─ 设置post_transform（SOFTMAX/NONE等）
```

### 共性处理

| 方面 | 处理方式 |
|------|----------|
| Booster自动包装 | 原生Booster对象包装为WrappedBooster（F-036） |
| 树遍历 | dump_model()获取JSON/字典表示，递归遍历 |
| 缺失值处理 | `missing_value_tracks_true` 字段标记缺失值方向 |
| 多分类 | TreeEnsembleClassifier + 多个class_weights |
| 基值 | `base_values` 填充初始预测分数 |
| 输出后处理 | `post_transform` 设为'SOFTMAX'（分类）或'NONE'（回归） |

### 差异对比

| 特性 | LightGBM | XGBoost | H2O |
|------|----------|---------|-----|
| 模型dump | `model.dump_model()` → JSON | `model.get_booster().get_dump(dump_format='json')` → JSON列表 | MOJO zip → `h2o.print_mojo(format='json')` → 临时文件 |
| 算子类型 | LgbmClassifier/LgbmRegressor/LgbmRanker/LgbmZipMap | XGBClassifier/XGBRegressor/XGBRFClassifier/XGBRFRegressor | 仅支持algo="gbm" |
| 特有参数 | zipmap, split, without_onnx_ml | 无特有参数 | 默认initial_types |
| 多分类处理 | 每棵树num_class个输出 | 每棵树num_class个输出 | 每棵树num_class个输出 |

## LightGBM 特有选项（F-033）

LightGBM 转换器有三个独有的参数控制输出形式：

### zipmap：概率输出格式

```python
convert_lightgbm(model, initial_types=..., zipmap=True)
```

- `zipmap=True`（默认）：在TreeEnsembleClassifier后追加ZipMap算子，输出 `{类别名: 概率}` 字典序列
- `zipmap=False`：不输出ZipMap，概率直接为2D张量（通过Mul×1恒等替代），更适合ONNX Runtime推理

```
zipmap=True 输出链：
  input → TreeEnsembleClassifier → (label, probabilities) → ZipMap → (label, probabilities_dict)

zipmap=False 输出链：
  input → TreeEnsembleClassifier → (label, probabilities) → Mul×1 → (label, probabilities)
```

### split：大树林精度控制

```python
convert_lightgbm(model, initial_types=..., split=None)
```

- `split=None`（默认）：所有树放入一个TreeEnsembleRegressor/Classifier
- `split=N`（整数）：将大树林拆分为多个TreeEnsembleRegressor，每个含N棵树，通过Cast(double)+Sum累加

为什么要split？当树很多时，float32精度累积可能导致预测偏差。拆分后每段用double累加，最后cast回float，降低精度损失。

```
split=100（每100棵树一组）：
  TreeEnsembleRegressor(1-100) → Cast(double) ─┐
  TreeEnsembleRegressor(101-200) → Cast(double) ┼─ Sum(double) → Cast(float) → output
  TreeEnsembleRegressor(201-300) → Cast(double) ─┘
```

### without_onnx_ml：Hummingbird纯ONNX转换

```python
convert_lightgbm(model, initial_types=..., without_onnx_ml=False)
```

- `without_onnx_ml=True`：转换后调用 Hummingbird 库将 ONNX-ML 模型（TreeEnsemble等）转为纯ONNX算子（If/Gather/MatMul等）
- 用途：某些推理引擎不支持ONNX-ML域算子，需要纯ONNX算子
- 注意：需要额外安装 Hummingbird

## CoreML 树模型与传统ML算子（F-014）

CoreML 转换器是 onnxmltools 中 IR 覆盖最全面的前端，不仅支持树模型，还支持完整的传统 ML 算子集：

| 算子类别 | CoreML算子 | ONNX-ML映射 |
|----------|-----------|-------------|
| 树模型 | TreeEnsemble | TreeEnsembleClassifier/Regressor |
| 广义线性模型 | GLMClassifier/GLMRegressor | LinearClassifier/Regressor |
| 支持向量机 | SVC/SVR | SVMClassifier/Regressor |
| 特征工程 | DictVectorizer/FeatureVectorizer/OneHotEncoder | DictVectorizer/OneHotEncoder |
| 预处理 | Scaler/Imputer/Normalizer | Scaler/Imputer/Normalizer |
| 数组操作 | ArrayFeatureExtractor | ArrayFeatureExtractor |
| 后处理 | TensorToLabel/TensorToProbabilityMap | ArgMax/ZipMap |
| 神经网络 | neural_network/子包40+层 | Conv/LSTM/BN等 |

CoreML 特有处理：
- **metadata自动提取**：从 `spec.description.metadata` 提取 `shortDescription`→doc_string、`author`→metadata_props、`license`→metadata_props（F-034）
- **2D→4D shape fix**：compile阶段将2D图像输入补全为4D（NCHW格式）（F-019中的_fix_shapes）

## H2O MOJO 转换特殊性（F-035）

H2O 转换器接收 MOJO zip 内容（bytes或文件路径），通过临时文件调用H2O的JSON导出：

```python
# H2O转换流程
1. 接收MOJO zip路径或bytes
2. 写入临时文件
3. 调用 h2o.print_mojo(path, format="json") 获取JSON
4. 解析JSON（仅支持 algo="gbm" 类型）
5. 走标准parse→compile→convert流水线
6. 默认initial_types = [("input", FloatTensorType(["None", "None"]))]
```

## 设计洞察

1. **属性平行数组是ONNX-ML树模型的编码范式**：TreeEnsemble不使用嵌套消息，而是用多个平行数组（nodes_treeids[i]与nodes_nodeids[i]等共同描述第i个节点），这种设计便于protobuf序列化但需要仔细保持数组同步。
2. **共享模板是多框架统一的关键**：LightGBM/XGBoost/H2O都使用同一个`get_default_tree_*_attribute_pairs()`和`add_node`函数，这保证了树模型转换的一致性。
3. **zipmap/split/without_onnx_ml是实用主义的后处理**：这些选项不是ONNX标准的一部分，而是为了应对实际部署需求（字典输出、精度控制、引擎兼容）。
4. **CoreML是最完整的IR前端**：15+40个算子的覆盖使CoreML转换器成为扩展IR表达能力时的最佳参考。

## 关联概念

- [Topology IR：三层核心类、C风格唯一名称、raw_name隐藏](01-topology-ir.md) — 了解树模型如何被表示为IR
- [转换器注册与分发：双注册池、导入副作用、委托路径](03-converter-registration.md) — 了解树模型算子的注册
- [XGBoost模型转ONNX实战](../examples/xgboost-conversion.md) — 完整代码示例
- [LightGBM Pipeline转换实战](../examples/lightgbm-pipeline.md) — 带zipmap/split选项的示例
