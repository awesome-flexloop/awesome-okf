---
type: concept
title: "Python Helper API 详解"
description: "make_node/make_graph/make_model/make_tensor/make_attribute/make_tensor_value_info 的完整用法、kwargs自动转属性、raw_data压缩、亚字节打包、__repr__覆写"
sources:
  references: [../references/helper-api.md]
  facts: [F-021, F-022, F-023, F-024, F-025, F-026, F-027, F-028, F-029, F-030, F-032]
---

# Python Helper API 详解

## 核心理解

helper.py 是 Python 端构造 ONNX 模型的主要入口。它提供 `make_*` 系列函数，将 Python 原生类型（int/float/str/list/numpy array）转换为对应的 Protobuf message 对象。理解这些函数的参数、自动类型推断和存储策略，是正确编写 ONNX 模型构造代码的基础。

## 机制详解

### 构造函数全景

```
make_tensor_value_info ──→ ValueInfoProto（输入输出定义）
       │
       ↓
make_node ──→ NodeProto（计算节点）
       │    (kwargs 自动通过 make_attribute 转换)
       ↓
make_tensor ──→ TensorProto（常量数据/初始化器）
       │
       ↓
make_graph ──→ GraphProto（计算图，组合 nodes+inputs+outputs+initializers）
       │
       ↓
make_model ──→ ModelProto（模型，自动设置 ir_version/opset）
make_model_gen_version ──→ ModelProto（根据opset自动推算ir_version）
```

### make_node：创建计算节点

```python
make_node(
    op_type: str,
    inputs: Sequence[str],
    outputs: Sequence[str],
    name: Optional[str] = None,
    doc_string: Optional[str] = None,
    domain: Optional[str] = None,
    overload: Optional[str] = None,
    **kwargs: Any,           # 节点属性
) -> NodeProto
```

核心特性（F-021）：
1. **kwargs 自动转属性**：额外的关键字参数自动通过 `make_attribute()` 转换为 AttributeProto
2. **None 值跳过**：值为 None 的属性不添加
3. **input/output 是字符串列表**：通过名字连接，不是对象引用

```python
from onnx import helper

# 基本用法：MatMul(X, W) -> Y
node = helper.make_node("MatMul", ["X", "W"], ["Y"])

# 带属性：Conv(X, W) -> Y, kernel_shape=(3,3), strides=(1,1)
node = helper.make_node(
    "Conv",
    ["X", "W"],
    ["Y"],
    kernel_shape=[3, 3],     # kwargs → INTS 属性
    strides=[1, 1],          # kwargs → INTS 属性
    pads=[0, 0, 0, 0],       # kwargs → INTS 属性
    name="conv1",
)

# 值为 None 的属性被跳过
node = helper.make_node(
    "Clip",
    ["X"],
    ["Y"],
    min=None,    # 不添加（可选属性）
    max=None,    # 不添加（可选属性）
)
```

### make_graph：创建计算图

```python
make_graph(
    nodes: Sequence[NodeProto],
    name: str,
    inputs: Sequence[ValueInfoProto],
    outputs: Sequence[ValueInfoProto],
    initializer: Optional[Sequence[TensorProto]] = None,
    doc_string: Optional[str] = None,
    value_info: Optional[Sequence[ValueInfoProto]] = None,
    sparse_initializer: Optional[Sequence[SparseTensorProto]] = None,
) -> GraphProto
```

行为（F-022）：
- `initializer`、`value_info`、`sparse_initializer` 默认为空列表（不是 None）
- nodes 应按拓扑序排列（但 checker 不严格验证拓扑序，只验证名字引用）

```python
graph = helper.make_graph(
    nodes=[matmul_node, add_node],
    name="linear_regression",
    inputs=[X_info, W_info, B_info],
    outputs=[Y_info],
    initializer=[W_tensor, B_tensor],  # 常量权重
)
```

### make_model：创建模型

```python
make_model(graph: GraphProto, **kwargs) -> ModelProto
```

自动行为（F-023）：
1. 自动设置 `ir_version = onnx.IR_VERSION`（当前最新版本14）
2. 若未指定 `opset_imports`，默认导入当前 ai.onnx opset 版本
3. 其他 kwargs 直接设置到 ModelProto 字段

```python
# 简单创建（自动使用最新版本）
model = helper.make_model(graph)

# 指定 opset 版本
model = helper.make_model(
    graph,
    producer_name="my_project",
    producer_version="1.0",
    opset_imports=[helper.make_operatorsetid("", 17)],
)
```

### make_model_gen_version：智能版本选择

```python
make_model_gen_version(graph: GraphProto, **kwargs) -> ModelProto
```

与 make_model 的区别（F-024）：当未指定 ir_version 时，通过 `find_min_ir_version_for(opset_imports)` 计算所需的**最小** IR 版本，而非使用最新版本。适用于需要最大兼容性的场景。

```python
# 针对 opset 11，自动计算 ir_version=6
model = helper.make_model_gen_version(
    graph,
    opset_imports=[helper.make_operatorsetid("", 11)],
)
# model.ir_version == 6
```

### make_tensor：创建张量

```python
make_tensor(
    name: str,
    data_type: int,         # TensorProto.DataType 枚举值
    dims: Sequence[int],
    vals: Any,              # Python 列表或 numpy 数组
    raw: bool = False,
) -> TensorProto
```

存储策略（F-025）：

| 模式 | 存储方式 | 适用场景 |
|------|---------|---------|
| `raw=False`（默认） | 类型特定字段（float_data/int32_data等） | 小张量、需要可读性 |
| `raw=True` | raw_data 原始字节 | 大张量、更紧凑 |

```python
import numpy as np
from onnx import TensorProto

# 默认模式：使用类型特定字段
tensor = helper.make_tensor(
    "W", TensorProto.FLOAT, [2, 3], [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
)
# 数据存储在 tensor.float_data 中

# raw 模式：原始字节（更紧凑）
data = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], dtype=np.float32)
tensor = helper.make_tensor(
    "W", TensorProto.FLOAT, [2, 3], data.tobytes(), raw=True
)
# 数据存储在 tensor.raw_data 中

# STRING 类型不支持 raw=True
str_tensor = helper.make_tensor(
    "labels", TensorProto.STRING, [2], [b"cat", b"dog"]
)
```

**亚字节打包规则**：
- UINT4/INT4/FLOAT4E2M1：2个元素→1字节
- UINT2/INT2：4个元素→1字节

### make_attribute：自动类型推断

```python
make_attribute(
    key: str,
    value: Any,
    domain: Optional[str] = None,
    doc_string: Optional[str] = None,
) -> AttributeProto
```

Python 值到 AttributeType 的自动映射（F-026）：

| Python 值类型 | AttributeType | 属性字段 |
|--------------|---------------|---------|
| `int` | INT | `i` |
| `float` | FLOAT | `f` |
| `str` | STRING | `s`（编码为bytes） |
| `bytes` | STRING | `s` |
| `TensorProto` | TENSOR | `t` |
| `SparseTensorProto` | SPARSE_TENSOR | `sparse_tensor` |
| `GraphProto` | GRAPH | `g` |
| `TypeProto` | TYPE_PROTO | `tp` |
| `list/tuple of int` | INTS | `ints` |
| `list/tuple of float` | FLOATS | `floats` |
| `list/tuple of str` | STRINGS | `strings` |
| `list/tuple of TensorProto` | TENSORS | `tensors` |
| `list/tuple of GraphProto` | GRAPHS | `graphs` |
| `list/tuple of TypeProto` | TYPE_PROTOS | `type_protos` |

```python
# 整数属性
attr = helper.make_attribute("axis", 1)
# attr.type == INT, attr.i == 1

# 整数列表属性
attr = helper.make_attribute("strides", [1, 1])
# attr.type == INTS, attr.ints == [1, 1]

# 张量属性
t = helper.make_tensor("const", TensorProto.FLOAT, [1], [0.0])
attr = helper.make_attribute("value", t)
# attr.type == TENSOR, attr.t == t
```

### make_attribute_ref：引用属性（函数用）

```python
make_attribute_ref(
    key: str,
    type: AttributeType,
    doc_string: Optional[str] = None,
) -> AttributeProto
```

创建设置了 `ref_attr_name` 的属性（F-027），用于函数体中引用父函数的参数：

```python
# 在函数体内引用父函数的"axis"属性
ref_attr = helper.make_attribute_ref("axis", AttributeProto.INT)
# ref_attr.ref_attr_name == "axis"
# ref_attr 不携带值，在函数实例化时从父作用域获取
```

### make_tensor_value_info：创建值信息

```python
make_tensor_value_info(
    name: str,
    elem_type: int,
    shape: Optional[Sequence[Union[str, int, None]]],
    doc_string: Optional[str] = None,
    shape_denotation: Optional[List[str]] = None,
) -> ValueInfoProto
```

shape 参数的处理（F-028）：

| shape 元素 | 设置的字段 | 含义 |
|-----------|-----------|------|
| `int`（如 3, 768） | `dim_value` | 静态维度（编译时已知） |
| `str`（如 "batch"） | `dim_param` | 符号/动态维度 |
| `None` | 不设置 | 未知维度 |
| `shape=[]` | 空 dim 列表 | 标量（0维张量） |
| `shape=None` | 不设置 shape | 完全未知的形状 |

```python
# 静态形状输入：[1, 3, 224, 224]
X = helper.make_tensor_value_info(
    "X", TensorProto.FLOAT, [1, 3, 224, 224]
)

# 动态batch输入：[batch, 3, 224, 224]
X = helper.make_tensor_value_info(
    "X", TensorProto.FLOAT, ["batch", 3, 224, 224]
)

# 完全动态形状：["N", "C", "H", "W"]
X = helper.make_tensor_value_info(
    "X", TensorProto.FLOAT, ["N", "C", "H", "W"]
)

# 标量（空shape）
scalar = helper.make_tensor_value_info(
    "scalar", TensorProto.FLOAT, []
)
```

### make_function：创建函数

```python
make_function(
    domain: str,
    fname: str,
    inputs: Sequence[str],
    outputs: Sequence[str],
    nodes: Sequence[NodeProto],
    opset_imports: Optional[Sequence[OperatorSetIdProto]] = None,
    attributes: Optional[Sequence[str]] = None,
    attribute_protos: Optional[Sequence[AttributeProto]] = None,
    doc_string: Optional[str] = None,
    overload: Optional[str] = None,
    value_info: Optional[Sequence[ValueInfoProto]] = None,
) -> FunctionProto
```

- `attributes`：字符串列表，声明函数参数化属性名
- `attribute_protos`：AttributeProto 列表，提供属性默认值（F-029）

### make_operatorsetid：创建算子集标识

```python
make_operatorsetid(domain: str, version: int) -> OperatorSetIdProto
```

### tensor_dtype_to_field：类型到存储字段映射

带 `@lru_cache` 的函数，将 DataType 枚举值映射到对应的 proto 存储字段名（F-030）：

```python
from onnx.helper import tensor_dtype_to_field

tensor_dtype_to_field(TensorProto.FLOAT)   # "float_data"
tensor_dtype_to_field(TensorProto.INT64)   # "int64_data"
tensor_dtype_to_field(TensorProto.STRING)  # "string_data"
tensor_dtype_to_field(TensorProto.BOOL)    # "int32_data"（注意！）
```

## Python 构造模型完整流程

```python
import onnx
from onnx import helper, TensorProto, numpy_helper
import numpy as np

# 步骤1：定义输入输出
X = helper.make_tensor_value_info("X", TensorProto.FLOAT, [1, 3])
Y = helper.make_tensor_value_info("Y", TensorProto.FLOAT, [1, 1])

# 步骤2：创建初始器（常量权重）
W_init = np.random.randn(3, 1).astype(np.float32)
B_init = np.array([[0.0]], dtype=np.float32)
W = numpy_helper.from_array(W_init, name="W")
B = numpy_helper.from_array(B_init, name="B")

# 步骤3：创建计算节点
matmul = helper.make_node("MatMul", ["X", "W"], ["hidden"])
add = helper.make_node("Add", ["hidden", "B"], ["Y"])

# 步骤4：构建计算图
graph = helper.make_graph(
    [matmul, add],
    "linear_model",
    [X],        # inputs: X是运行时输入
    [Y],        # outputs
    [W, B],     # initializers: W和B是常量
)

# 步骤5：封装为模型
model = helper.make_model(graph)

# 步骤6：验证模型
onnx.checker.check_model(model)

# 步骤7：保存
onnx.save(model, "linear_model.onnx")
```

## 关键洞察/反常识

1. **kwargs 属性不检查存在性**：make_node 的 kwargs 会无条件转为属性，即使该算子没有这个属性。错误的属性名只有在 checker 检查时才会被发现。
2. **int32_data 是"小整数大杂烩"**：BOOL、INT8、UINT8、FLOAT16、BFLOAT16 等类型的数据都存储在 int32_data 字段中，因为这些类型在 protobuf 中没有对应的重复字段。
3. **shape=[] 和 shape=None 不同**：前者表示标量（0维张量），后者表示完全未知形状。这个区分在某些推理引擎中很重要。
4. **STRING 类型不支持 raw=True**：字符串是变长的，不能用 raw_data 紧凑存储，必须使用 string_data。
5. **make_model 默认用最新版本**：创建模型时如果需要旧版兼容性，必须显式指定 opset_imports 或使用 make_model_gen_version。

## 关联概念

- [Protobuf IR：核心 Message 结构](01-protobuf-ir.md) — make_* 函数创建的各个 message 的字段定义
- [张量类型系统](02-tensor-type-system.md) — DataType 枚举和存储字段映射
- [计算图模型](03-computation-graph.md) — initializer/input/output 的区别
- [Opset版本机制与算子域](04-opset-versioning.md) — make_model 的自动版本设置
- [从零构建线性回归模型](../examples/build-linear-regression.md) — 完整的模型构造实战
