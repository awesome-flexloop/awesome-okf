---
type: concept
title: "数据类型系统：四层DataType、TensorType维度规格、三向类型猜测"
description: "onnxmltools 的数据类型体系：DataType基类与四层派生（标量/张量/序列/字典）、15种TensorType子类、TensorType.to_onnx_type三类维度规格（int固定/str符号/None未知）、三向类型猜测函数族（proto/proto_str/numpy）、denotation语义标注"
sources:
  references: [../references/registration-types.md]
  facts: [F-026, F-027, F-028]
---

# 数据类型系统：四层DataType、TensorType维度规格、三向类型猜测

## 核心理解

onnxmltools 的类型系统由 `data_types.py` 实现，是连接"原始框架类型"和"ONNX类型"的桥梁。类型系统分为四层：标量类型（固定shape）、张量类型（15种元素类型+可变shape）、序列类型、字典类型。同时提供三向类型猜测函数族，能从 ONNX 枚举值、ONNX 类型字符串、numpy dtype 自动推断出对应的 DataType 对象。

```
DataType（抽象基类）
├── 标量类型（shape固定为[1,1]）
│   ├── FloatType / DoubleType
│   ├── Int8Type / Int16Type / Int32Type / Int64Type
│   ├── UInt8Type / UInt16Type / UInt32Type / UInt64Type
│   ├── StringType / BooleanType
│   └── Float16Type / Complex64Type / Complex128Type
├── 张量类型（TensorType抽象类 + 15种具体子类）
│   ├── FloatTensorType / DoubleTensorType / ...
│   └── shape支持三种维度：int固定、str符号、None未知
├── SequenceType(element_type)     # ONNX-ML 序列
└── DictionaryType(key_type, value_type)  # ONNX-ML 字典
```

## DataType 基类

所有类型继承自 `DataType` 基类：

```python
class DataType:
    def __init__(self, shape=None, doc_string=""):
        self.shape = shape          # 维度规格
        self.doc_string = doc_string
    
    def to_onnx_type(self):
        """子类实现：转换为 onnx.TypeProto"""
        raise NotImplementedError
```

## 第一层：标量类型

标量类型代表单个值，**固定 `shape=[1,1]`**（ONNX 中没有真正的标量，最小单位是1×1张量）：

```python
class FloatType(DataType):
    def __init__(self, doc_string=""):
        super().__init__(shape=[1, 1], doc_string=doc_string)

class Int64Type(DataType):
    def __init__(self, doc_string=""):
        super().__init__(shape=[1, 1], doc_string=doc_string)
# ... DoubleType, StringType, UInt8Type, Int8Type 等同理
```

标量类型主要用于：
- 分类标签输出（Int64Type 表示类别ID，StringType 表示类别名）
- 字典类型的key/value组件
- 序列类型的元素类型

## 第二层：张量类型（TensorType）

TensorType 是最常用的类型，是一个抽象类，15个子类分别对应 ONNX 的 TensorProto.DataType 枚举值：

| TensorType子类 | ONNX枚举值 | numpy dtype | 说明 |
|----------------|-----------|-------------|------|
| `FloatTensorType` | FLOAT (1) | np.float32 | 最常用，模型权重/输入默认类型 |
| `DoubleTensorType` | DOUBLE (11) | np.float64 | 双精度 |
| `Int8TensorType` | INT8 (3) | np.int8 | 量化 |
| `Int16TensorType` | INT16 (5) | np.int16 | |
| `Int32TensorType` | INT32 (6) | np.int32 | 索引/类别 |
| `Int64TensorType` | INT64 (7) | np.int64 | 类别ID/索引 |
| `UInt8TensorType` | UINT8 (2) | np.uint8 | 图像像素 |
| `UInt16TensorType` | UINT16 (4) | np.uint16 | |
| `UInt32TensorType` | UINT32 (12) | np.uint32 | |
| `UInt64TensorType` | UINT64 (13) | np.uint64 | |
| `Float16TensorType` | FLOAT16 (10) | np.float16 | 半精度 |
| `StringTensorType` | STRING (8) | np.object_ | 文本/类别名 |
| `BooleanTensorType` | BOOL (9) | np.bool_ | 布尔掩码 |
| `Complex64TensorType` | COMPLEX64 (14) | np.complex64 | 复数 |
| `Complex128TensorType` | COMPLEX128 (15) | np.complex128 | 双精度复数 |

每个子类实现 `_get_element_onnx_type()` 返回对应的 TensorProto 枚举值：

```python
class FloatTensorType(TensorType):
    def _get_element_onnx_type(self):
        return TensorProto.FLOAT  # 值为1
```

## TensorType 的三类维度规格（F-027）

`TensorType.to_onnx_type()` 将 shape 转换为 ONNX `TensorShapeProto`，每个维度支持三种规格：

| 维度值类型 | ONNX表示 | 含义 | 示例 |
|-----------|----------|------|------|
| `int` / `np.integer` | `dim_value` | 固定维度大小 | `4` → dim_value=4 |
| `str` | `dim_param` | 符号维度（参数化） | `"None"` → dim_param="None" |
| `None` | 不设置 | 未知维度（不写入） | `None` → 跳过 |

```python
def to_onnx_type(self):
    tensor_type_proto = onnx.helper.make_tensor_type_proto(
        elem_type=self._get_element_onnx_type(),
        shape=self.shape
    )
    # 手动处理维度规格：
    for i, d in enumerate(self.shape):
        dim = tensor_type_proto.tensor_type.shape.dim[i]
        if isinstance(d, (int, np.integer)):
            dim.dim_value = int(d)
        elif isinstance(d, str):
            dim.dim_param = d
        elif d is None:
            pass  # 未知维度不设置
    return tensor_type_proto
```

### 常见维度组合

```python
# 批处理特征向量（batch大小可变，特征数固定为4）
FloatTensorType(["None", 4])
# → shape: dim_param="None", dim_value=4

# 固定batch=1的单样本
FloatTensorType([1, 784])
# → shape: dim_value=1, dim_value=784

# 图像数据（NCHW格式，batch和空间维度可变）
FloatTensorType(["None", 3, "None", "None"])
# → shape: dim_param="None", dim_value=3, dim_param="None", dim_param="None"

# 完全未知形状
FloatTensorType(None)
# → 不设置shape信息
```

### 语义标注：denotation

TensorType 支持 `denotation` 和 `channel_denotations` 语义标注：

```python
FloatTensorType(["None", 3, 224, 224],
                denotation="DATA_BATCH",
                channel_denotations={0: "DATA_BATCH", 1: "CHANNEL"})
```

denotation 遵循 ONNX ML 的语义标注标准，用于标识数据的语义角色（如"BATCH"、"FEATURE"、"LABEL"等）。

## 第三层：序列类型（SequenceType）

```python
class SequenceType(DataType):
    def __init__(self, element_type, **kwargs):
        super().__init__(**kwargs)
        self.element_type = element_type  # DataType实例
```

对应 ONNX-ML 的序列类型（`sequence_type`），用于表示可变长度序列，如文本token序列、时间步列表。

## 第四层：字典类型（DictionaryType）

```python
class DictionaryType(DataType):
    def __init__(self, key_type, value_type, **kwargs):
        super().__init__(**kwargs)
        self.key_type = key_type      # 通常是Int64Type或StringType
        self.value_type = value_type  # TensorType等
```

对应 ONNX-ML 的映射类型（`map_type`），常用于 ZipMap 算子的输出（类别→概率映射）。

## 三向类型猜测函数族（F-028）

类型猜测函数族是类型系统的"反射"能力，能从多种源格式自动推断 DataType。

### 底层三向函数

| 函数 | 输入源 | 方向 |
|------|--------|------|
| `_guess_type_proto(onnx_type_enum)` | ONNX TensorProto枚举值（如`TensorProto.FLOAT`） | ONNX内部→DataType |
| `_guess_type_proto_str(type_str)` | ONNX类型字符串（如`"tensor(float)"`） | ONNX字符串→DataType |
| `_guess_numpy_type(dtype, shape=None)` | numpy dtype（如`np.float32`） | numpy→DataType |

### 高层封装函数

| 函数 | 功能 | 支持输入 |
|------|------|----------|
| `guess_data_type(value, ...)` | 通用类型猜测 | np.ndarray / pd.DataFrame / pd.Series / dict / list |
| `guess_numpy_type(dtype, shape)` | numpy类型→TensorType | dtype + shape |
| `guess_proto_type(type_proto)` | ONNX TypeProto→DataType | onnx.TypeProto |
| `guess_tensor_type(enum)` | TensorProto枚举→TensorType子类 | int枚举值 |

### guess_data_type 自动识别逻辑

`guess_data_type` 是最智能的高层函数：

```python
def guess_data_type(value, name="", dtype=None, shape=None):
    if isinstance(value, np.ndarray):
        # numpy数组：根据dtype和shape推断
        return guess_numpy_type(value.dtype, value.shape)
    elif isinstance(value, pd.DataFrame):
        # DataFrame：每列一个输入变量，列名为变量名
        types = []
        for col in value.columns:
            col_type = guess_numpy_type(value[col].dtype, [None, 1])
            types.append((col, col_type))
        return types
    elif isinstance(value, pd.Series):
        # Series：单变量
        return guess_numpy_type(value.dtype, [None, 1])
    elif isinstance(value, dict):
        # 字典：递归处理value
        return {k: guess_data_type(v) for k, v in value.items()}
    elif isinstance(value, list):
        # 列表：直接作为initial_types使用
        return value
```

这在 `to_onnx` 风格的简化API中非常有用——用户只需传入训练数据，系统自动推断 `initial_types`。

## initial_types 类型声明

`initial_types` 是转换器的核心参数，声明模型输入的名称和类型：

```python
# 单输入：名为"input"的float32张量，batch可变，特征数4
initial_types = [("input", FloatTensorType(["None", 4]))]

# 多输入
initial_types = [
    ("numeric_features", FloatTensorType(["None", 10])),
    ("categorical_features", StringTensorType(["None", 3])),
]
```

- LightGBM/XGBoost/LibSVM：**必填**，不传则抛 ValueError
- H2O：有默认值 `[("input", FloatTensorType(["None", "None"]))]`
- CoreML/SparkML：可选但推荐传入

## 设计洞察

1. **类型系统是ONNX互操作性的核心**：DataType 在框架类型和ONNX类型之间建立了明确的映射关系，是转换正确性的基础。
2. **三类维度规格表达力完备**：int（固定）、str（符号）、None（未知）覆盖了静态形状、动态batch、未知维度三种场景。
3. **三向猜测函数降低使用门槛**：用户不需要手动构造DataType，可从numpy/DataFrame/ONNX类型自动推断。
4. **标量类型的shape=[1,1]是ONNX的约束**：ONNX没有零维张量标量，最小是1×1张量，标量类型自动处理这个映射。

## 关联概念

- [转换器注册与分发：双注册池、导入副作用、委托路径](03-converter-registration.md) — 形状计算器操作DataType
- [编译流水线五阶段：createTopology→compile→convert_topology→make_model](02-conversion-pipeline.md) — 类型推断阶段如何使用DataType
- [XGBoost模型转ONNX实战](../examples/xgboost-conversion.md) — initial_types使用示例
