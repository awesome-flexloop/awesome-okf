---
type: reference
title: "双注册池、数据类型系统与apply快捷函数"
description: "onnxmltools 的 _registration.py 双注册池（converter/shape_calculator）设计、导入副作用注册模式、data_types.py 四层DataType体系、三向类型猜测函数族、_apply_operation.py 74个ONNX节点构造快捷函数的源码信源登记"
sources:
  - path: "external/libs/models/onnx/onnxmltools/onnxmltools/convert/common/_registration.py"
    facts: [F-010, F-011, F-012, F-013, F-014]
  - path: "external/libs/models/onnx/onnxmltools/onnxmltools/convert/common/data_types.py"
    facts: [F-026, F-027, F-028]
  - path: "external/libs/models/onnx/onnxmltools/onnxmltools/convert/common/_apply_operation.py"
    facts: [F-029]
  - path: "external/libs/models/onnx/onnxmltools/onnxmltools/convert/common/tree_ensemble.py"
    facts: [F-030]
  - path: "external/libs/models/onnx/onnxmltools/onnxmltools/convert/common/shape_calculator.py"
    facts: [F-038]
---

# 双注册池、数据类型系统与apply快捷函数

## 信源概述

| 信源 | 类型 | 职责 |
|------|------|------|
| `common/_registration.py` | 注册机制 | 双注册池（converter/shape_calculator）、register/get 函数 |
| `common/data_types.py` | 类型系统 | DataType 类层次、TensorType 子类、类型猜测函数族 |
| `common/_apply_operation.py` | 算子快捷构造 | 74个 `apply_xxx` 快捷函数，处理opset版本差异 |
| `common/tree_ensemble.py` | 树模型模板 | TreeEnsemble 属性对默认模板、add_node 函数 |
| `common/shape_calculator.py` | 形状校验工具 | check_input_and_output_numbers/types、线性回归默认形状计算器 |

## 双注册池设计（F-010）

**信源**：`common/_registration.py` L6-L67

`_registration.py` 维护两个模块级字典：

```python
_converter_pool = {}        # key: operator类型字符串 → value: 转换函数
_shape_calculator_pool = {} # key: operator类型字符串 → value: 形状计算函数
```

提供四对操作函数：

```python
def register_converter(operator_type, converter_function, overwrite=False):
    if operator_type in _converter_pool and not overwrite:
        raise ValueError(f"Converter for '{operator_type}' already registered.")
    _converter_pool[operator_type] = converter_function

def get_converter(operator_type):
    if operator_type not in _converter_pool:
        raise ValueError(f"Unsupported conversion for operator '{operator_type}'.")
    return _converter_pool[operator_type]

def register_shape_calculator(operator_type, shape_calculator_function, overwrite=False):
    if operator_type in _shape_calculator_pool and not overwrite:
        raise ValueError(f"Shape calculator for '{operator_type}' already registered.")
    _shape_calculator_pool[operator_type] = shape_calculator_function

def get_shape_calculator(operator_type):
    if operator_type not in _shape_calculator_pool:
        raise ValueError(f"Unsupported shape calculator for operator '{operator_type}'.")
    return _shape_calculator_pool[operator_type]
```

默认不允许覆盖（`overwrite=False` 时抛 ValueError），防止意外覆盖。

## 导入副作用注册模式（F-011）

**信源**：各框架子目录 `convert.py` 顶部

各框架的 `convert.py` 在模块顶部通过 import 语句触发注册：

```python
# lightgbm/convert.py L12
from . import operator_converters, shape_calculators
```

而 `operator_converters/__init__.py` 导入各算子模块，每个算子模块在文件底部直接调用 `register_converter(...)`：

```python
# lightgbm/operator_converters/LightGbm.py L1041-L1044
register_converter('LgbmClassifier', convert_lightgbm)
register_converter('LgbmRegressor', convert_lightgbm)
register_converter('LgbmRanker', convert_lightgbm)
register_converter('LgbmZipMap', convert_lgbm_zipmap)
```

这是"导入即注册"模式：import 语句本身就是注册的触发器，没有显式的注册函数调用步骤。

## 各框架注册统计（F-012, F-013, F-014）

### LightGBM（F-012）
注册4个operator类型：`LgbmClassifier`、`LgbmRegressor`、`LgbmRanker` → 同一 `convert_lightgbm` 函数（内部 isinstance 分发），`LgbmZipMap` → `convert_lgbm_zipmap`。

### XGBoost（F-013）
注册4个operator类型：`XGBClassifier`、`XGBRFClassifier`、`XGBRegressor`、`XGBRFRegressor` → 同一 `convert_xgboost` 函数，内部根据 isinstance 分发到 `XGBClassifierConverter` 或 `XGBRegressorConverter`。

### CoreML（F-014）
- 顶层注册15个转换器：`ArrayFeatureExtractor`、`DictVectorizer`、`FeatureVectorizer`、`GLMClassifier`、`GLMRegressor`、`Identity`、`Imputer`、`Normalizer`、`OneHotEncoder`、`Scaler`、`SVC`、`SVR`、`TensorToLabel`、`TensorToProbabilityMap`、`TreeEnsemble`
- `neural_network/` 子包额外注册40+神经网络层算子

CoreML 是 IR 覆盖最全面的前端。

## 数据类型系统（F-026）

**信源**：`common/data_types.py` L8-L280

DataType 四层类层次：

```
DataType（基类：持有 shape, doc_string）
├── FloatType          # 标量，固定 shape=[1,1]
├── Int64Type          # 标量
├── StringType         # 标量
├── DoubleType         # 标量
├── UInt8Type          # 标量
├── Int8Type           # 标量
├── TensorType（抽象类：_get_element_onnx_type 子类实现）
│   ├── FloatTensorType
│   ├── DoubleTensorType
│   ├── Int8TensorType
│   ├── Int16TensorType
│   ├── Int32TensorType
│   ├── Int64TensorType
│   ├── UInt8TensorType
│   ├── UInt16TensorType
│   ├── UInt32TensorType
│   ├── UInt64TensorType
│   ├── Float16TensorType
│   ├── StringTensorType
│   ├── BooleanTensorType
│   ├── Complex64TensorType
│   └── Complex128TensorType    # 共15种张量类型
├── SequenceType(element_type)  # ONNX-ML 序列类型
└── DictionaryType(key_type, value_type)  # ONNX-ML 字典类型
```

标量类型固定 `shape=[1,1]`，TensorType 子类通过 `_get_element_onnx_type()` 返回对应的 ONNX TensorProto 枚举值。

## TensorType.to_onnx_type 维度规格（F-027）

**信源**：`common/data_types.py` L76-L105

维度值支持三种规格：

```python
def to_onnx_type(self):
    tensor_type = TensorProto.DataType.Value(self._get_element_onnx_type())
    dims = []
    for d in self.shape:
        dim = TensorShapeProto.Dimension()
        if isinstance(d, (int, np.integer)):
            dim.dim_value = int(d)           # 固定维度
        elif isinstance(d, str):
            dim.dim_param = d                # 符号维度（如 "None"、"N"）
        elif d is None:
            pass                             # 未知维度（不设置）
        dims.append(dim)
    # 同时支持 denotation 和 channel_denotations 语义标注
```

示例：`FloatTensorType([None, 4])` → 第一维为符号维度（batch），第二维固定为4。

## 三向类型猜测函数族（F-028）

**信源**：`common/data_types.py` L291-L544

提供三个底层方向检测函数和四个高层封装：

### 底层三向函数

| 函数 | 输入源 | 示例 |
|------|--------|------|
| `_guess_type_proto` | onnx.TensorProto 枚举值 | `TensorProto.FLOAT` → FloatTensorType |
| `_guess_type_proto_str` | ONNX类型字符串 | `"tensor(float)"` → FloatTensorType |
| `_guess_numpy_type` | numpy dtype | `np.float32` → FloatTensorType |

### 高层封装

| 函数 | 功能 |
|------|------|
| `guess_data_type` | 通用类型猜测，自动识别 DataFrame/Series/ndarray |
| `guess_numpy_type` | numpy dtype → TensorType，支持 shape 推断 |
| `guess_proto_type` | onnx TypeProto → DataType |
| `guess_tensor_type` | TensorProto 枚举 → TensorType 子类 |

`guess_data_type` 自动识别逻辑：
- `np.ndarray` → 根据 dtype 和 shape 生成 TensorType
- `pd.DataFrame` → 每列一个输入变量
- `pd.Series` → 单变量
- list/dict → 递归处理

## _apply_operation 快捷函数（F-029）

**信源**：`common/_apply_operation.py` L40-L1871

提供74个 `apply_xxx` 快捷函数，统一处理 opset 版本差异：

| 类别 | 示例函数 |
|------|----------|
| 算术运算 | `apply_add`, `apply_sub`, `apply_mul`, `apply_div`, `apply_matmul` |
| 激活函数 | `apply_relu`, `apply_sigmoid`, `apply_softmax`, `apply_tanh` |
| 张量操作 | `apply_reshape`, `apply_concat`, `apply_transpose`, `apply_split`, `apply_gather` |
| 神经网络 | `apply_conv`, `apply_batch_normalization`, `apply_max_pool`, `apply_lstm`, `apply_gru` |
| 线性代数 | `apply_gemm`, `apply_matmul` |
| 逻辑比较 | `apply_less`, `apply_greater`, `apply_and`, `apply_or`, `apply_not` |
| 归约操作 | `apply_reduce_sum`, `apply_reduce_mean`, `apply_reduce_max` |

opset 版本差异处理：
- **opset < 6**：`consumed_inputs` 属性（原地操作标记）
- **opset < 7**：Caffe2 风格的 `axis`/`broadcast` 属性
- **opset ≥ 7**：使用 numpy 式广播语义，不设 broadcast/axis

所有 `apply_xxx` 函数签名统一为 `apply_xxx(scope, container, *inputs, **attrs)`，返回输出变量名列表。

## 树模型属性对模板（F-030）

**信源**：`common/tree_ensemble.py` L6-L79

提供两个默认属性字典初始化函数：

```python
def get_default_tree_classifier_attribute_pairs():
    """TreeEnsembleClassifier 默认属性"""
    return {
        'nodes_treeids': [], 'nodes_nodeids': [], 'nodes_featureids': [],
        'nodes_modes': [], 'nodes_values': [],
        'nodes_truenodeids': [], 'nodes_falsenodeids': [],
        'nodes_missing_value_tracks_true': [], 'nodes_hitrates': [],
        'class_treeids': [], 'class_nodeids': [], 'class_ids': [],
        'class_weights': [],  # 叶子节点类别权重
        'post_transform': 'NONE',
    }

def get_default_tree_regressor_attribute_pairs():
    """TreeEnsembleRegressor 默认属性"""
    return {
        'nodes_treeids': [], 'nodes_nodeids': [], 'nodes_featureids': [],
        'nodes_modes': [], 'nodes_values': [],
        'nodes_truenodeids': [], 'nodes_falsenodeids': [],
        'nodes_missing_value_tracks_true': [], 'nodes_hitrates': [],
        'target_treeids': [], 'target_nodeids': [], 'target_ids': [],
        'target_weights': [],  # 叶子节点回归目标权重
        'n_targets': 1,
        'post_transform': 'NONE',
    }

def add_node(attr_pairs, is_classifier, tree_id, tree_weight, node_id,
             feature_id, mode, value, true_child_id, false_child_id,
             weights, weight_id_bias=0, missing_tracks_true=False, hitrates=0.0):
    """统一填充节点属性，按 tree_weight 归一化叶子权重"""
```

`add_node` 函数在填充叶子节点权重时按 `tree_weight` 归一化，确保多棵树的权重和正确。

## 形状计算器校验工具（F-038）

**信源**：`common/shape_calculator.py` L6-L141

提供两个通用校验函数和一个默认形状计算器：

```python
def check_input_and_output_numbers(operator, input_count_range=None, output_count_range=None):
    """校验输入/输出个数范围，支持 (min,max) 元组或精确数字"""
    # 例：check_input_and_output_numbers(op, input_count_range=1, output_count_range=(1,2))

def check_input_and_output_types(operator, good_input_types=None, good_output_types=None):
    """校验输入/输出类型白名单"""
    # 例：check_input_and_output_types(op, good_input_types=[FloatTensorType, DoubleTensorType])

def calculate_linear_regressor_output_shapes(operator):
    """默认线性回归形状计算器：[N,C] → [N,nout]"""
```
