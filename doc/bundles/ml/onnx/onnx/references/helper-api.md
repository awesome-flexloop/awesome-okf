---
type: reference
title: "helper.py：Python Helper 核心 API"
description: "helper.py 中 make_node/make_graph/make_model/make_tensor/make_attribute/make_function 等构造函数 API 的签名、行为与 VERSION_TABLE 版本映射"
sources:
  - path: "external/libs/models/onnx/onnx/onnx/helper.py"
    facts: [F-021, F-022, F-023, F-024, F-025, F-026, F-027, F-028, F-029, F-030, F-031, F-032, F-072]
---

# helper.py：Python Helper 核心 API

## 信源概述

| 信源 | 类型 | 行数 | 职责 |
|------|------|------|------|
| `onnx/helper.py` | Python 模块 | ~1400行 | 提供 Python 端构造 ONNX Protobuf 对象的便捷 API（make_* 系列函数） |
| `onnx/_mapping.py` | Python 模块 | ~120行 | TENSOR_TYPE_MAP：DataType → numpy dtype / 存储类型映射 |

## 关键事实登记

### F-021：make_node 函数签名与 kwargs 自动转属性

**信源**：`onnx/helper.py` L136-L182

```python
def make_node(
    op_type: str,
    inputs: Sequence[str],
    outputs: Sequence[str],
    name: str | None = None,
    doc_string: str | None = None,
    domain: str | None = None,
    overload: str | None = None,
    **kwargs: Any,
) -> NodeProto:
```

- `inputs`/`outputs`：字符串列表，为节点的输入输出值名
- `kwargs` 中的额外关键字参数自动通过 `make_attribute` 转换为 AttributeProto
- 值为 `None` 的属性被跳过（不添加）
- 返回构造好的 NodeProto 对象

### F-022：make_graph 函数签名

**信源**：`onnx/helper.py` L203-L243

```python
def make_graph(
    nodes: Sequence[NodeProto],
    name: str,
    inputs: Sequence[ValueInfoProto],
    outputs: Sequence[ValueInfoProto],
    initializer: Sequence[TensorProto] | None = None,
    doc_string: str | None = None,
    value_info: Sequence[ValueInfoProto] | None = None,
    sparse_initializer: Sequence[SparseTensorProto] | None = None,
) -> GraphProto:
```

- `nodes`：NodeProto 列表，图中的计算节点
- `inputs`/`outputs`：ValueInfoProto 列表，图的输入输出
- `initializer`：默认为空列表，TensorProto 列表，图的初始化器（常量权重）
- `value_info`：默认为空列表，中间值类型信息
- `sparse_initializer`：默认为空列表，稀疏初始化器

### F-023：make_model 自动设置 ir_version 和 opset_import

**信源**：`onnx/helper.py` L297-L329

```python
def make_model(
    graph: GraphProto,
    **kwargs: Any,
) -> ModelProto:
```

行为：
1. 创建 ModelProto，设置传入的 graph
2. 自动设置 `ir_version` 为当前 `onnx.IR_VERSION`（最新版本）
3. 若未指定 `opset_imports`，默认导入当前 ai.onnx opset 版本（通过 `defs.onnx_opset_version()` 获取）
4. 其他 kwargs 直接设置到 ModelProto 字段

### F-024：make_model_gen_version 根据 opset 自动计算 IR 版本

**信源**：`onnx/helper.py` L334-L340

```python
def make_model_gen_version(
    graph: GraphProto,
    **kwargs: Any,
) -> ModelProto:
```

与 `make_model` 的区别：当未指定 `ir_version` 时，通过 `find_min_ir_version_for(opset_imports)` 根据 opset 导入列表计算所需的最小 IR 版本，而非使用最新 IR_VERSION。

### F-025：make_tensor 数据存储策略

**信源**：`onnx/helper.py` L365-L485

```python
def make_tensor(
    name: str,
    data_type: int,
    dims: Sequence[int],
    vals: Any,
    raw: bool = False,
) -> TensorProto:
```

存储策略：
- `raw=False`（默认）：根据 `data_type` 选择对应 proto 存储字段（float_data/int32_data/int64_data 等）
- `raw=True`：使用 `raw_data` 字段以原始字节存储，数值按小端序打包
- STRING 类型不支持 `raw=True`
- 4-bit 类型（UINT4/INT4/FLOAT4E2M1）：每2个元素打包到1字节
- 2-bit 类型（UINT2/INT2）：每4个元素打包到1字节

### F-026：make_attribute 自动类型推断

**信源**：`onnx/helper.py` L608-L699

```python
def make_attribute(
    key: str,
    value: Any,
    domain: str | None = None,
    doc_string: str | None = None,
) -> AttributeProto:
```

Python 值类型到 AttributeProto 类型的自动映射：

| Python 类型 | AttributeType |
|-------------|---------------|
| int | INT |
| float | FLOAT |
| str / bytes | STRING |
| TensorProto | TENSOR |
| SparseTensorProto | SPARSE_TENSOR |
| GraphProto | GRAPH |
| TypeProto | TYPE_PROTO |
| (int, float, ...) 可迭代 | INTS, FLOATS, ... |
| [TensorProto, ...] | TENSORS |
| [GraphProto, ...] | GRAPHS |
| [TypeProto, ...] | TYPE_PROTOS |

### F-027：make_attribute_ref 创建引用属性

**信源**：`onnx/helper.py` L702-L733

```python
def make_attribute_ref(
    key: str,
    type: AttributeType,
    doc_string: str | None = None,
) -> AttributeProto:
```

创建设置了 `ref_attr_name` 的属性，该属性不携带值，在函数实例化时从父函数作用域获取同名属性的值。仅在函数子图（FunctionProto 内的 NodeProto）中有效。

### F-028：make_tensor_value_info 构造 ValueInfoProto

**信源**：`onnx/helper.py` L787-L847

```python
def make_tensor_value_info(
    name: str,
    elem_type: int,
    shape: Sequence[str | int | None] | None,
    doc_string: str | None = None,
    shape_denotation: list[str] | None = None,
) -> ValueInfoProto:
```

shape 参数处理：
- `int` 值 → 设置 `dim_value`（静态维度）
- `str` 值 → 设置 `dim_param`（符号维度/动态维度）
- `None` 值 → 不设置维度值（未知维度）
- 显式传入空列表 `[]` → 产生空 dim 列表（标量，与 None 不同）

### F-029：make_function 构造 FunctionProto

**信源**：`onnx/helper.py` L261-L294

```python
def make_function(
    domain: str,
    fname: str,
    inputs: Sequence[str],
    outputs: Sequence[str],
    nodes: Sequence[NodeProto],
    opset_imports: Sequence[OperatorSetIdProto] | None = None,
    attributes: Sequence[str] | None = None,
    attribute_protos: Sequence[AttributeProto] | None = None,
    doc_string: str | None = None,
    overload: str | None = None,
    value_info: Sequence[ValueInfoProto] | None = None,
) -> FunctionProto:
```

- `attributes`：字符串列表，声明函数的参数化属性名
- `attribute_protos`：AttributeProto 列表，提供属性默认值
- `opset_imports`：函数体内使用的算子集版本

### F-030：tensor_dtype_to_field 类型到存储字段映射

**信源**：`onnx/helper.py` L1309-L1330

```python
@lru_cache()
def tensor_dtype_to_field(tensor_type: int) -> str:
```

映射关系：
| DataType | 存储字段 |
|----------|---------|
| FLOAT (1) | float_data |
| INT32 (6) | int32_data |
| INT64 (7) | int64_data |
| DOUBLE (11) | double_data |
| UINT32 (12), UINT64 (13) | uint64_data |
| STRING (8) | string_data |

其他类型（FLOAT16、INT8、UINT8、BOOL、BFLOAT16等）的存储字段为 int32_data。

### F-031：VERSION_TABLE 版本映射表

**信源**：`onnx/helper.py` L45-L81

VERSION_TABLE 是一个列表，每个元素为元组 `(Release-version, IR version, ai.onnx version, ai.onnx.ml version, ai.onnx.training version)`。映射从 ONNX 1.0 到 1.23.0 的历史版本。部分关键版本：

| Release | IR | ai.onnx | ai.onnx.ml | ai.onnx.training |
|---------|-----|---------|------------|-----------------|
| 1.0 | 3 | 1 | 1 | - |
| 1.3 | 3 | 8 | 1 | - |
| 1.6 | 6 | 11 | 2 | - |
| 1.8 | 7 | 13 | 2 | - |
| 1.10 | 8 | 15 | 2 | 1 |
| 1.12 | 8 | 17 | 3 | 1 |
| 1.14 | 9 | 19 | 4 | 1 |
| 1.16 | 10 | 21 | 4 | 1 |
| 1.20 | 12 | 23 | 5 | 1 |
| 1.23.0 | 14 | 25 | 5 | 1 |

### F-032：TENSOR_TYPE_MAP 数据类型映射

**信源**：`onnx/_mapping.py` L24-L119

`TENSOR_TYPE_MAP` 字典将 TensorProto 数据类型整数值映射到 `(np_dtype, storage_dtype, name)` 三元组。关键映射：
- UINT8/INT8/BOOL/FLOAT16/BFLOAT16/FLOAT8系列/UINT4/INT4/FLOAT4E2M1/UINT2/INT2 的存储类型均为 INT32（np.int32）
- UINT32 的存储类型为 UINT64（np.uint64）
- FLOAT→np.float32，DOUBLE→np.float64，INT32→np.int32，INT64→np.int64

### F-072：find_min_ir_version_for 查表计算最小 IR 版本

**信源**：`onnx/helper.py` L108-L133

```python
def find_min_ir_version_for(
    opset_imports: list[OperatorSetIdProto],
) -> int:
```

通过 OP_SET_ID_VERSION_MAP 映射表（从 VERSION_TABLE 派生），查找每个域的 opset 版本所需的 IR 版本，取各域所需 IR 版本的最大值返回。
