---
type: reference
title: "_enums.py 类型枚举：DataType 与 AttributeType"
description: "onnx_ir._enums 模块数据类型枚举与属性类型枚举信源登记——27种DataType、15种AttributeType、numpy↔ONNX映射、位宽表、非原生类型ml_dtypes支持"
sources:
  - path: "src/onnx_ir/_enums.py"
    facts: [F-005, F-006, F-007, F-008, F-010]
  - path: "src/onnx_ir/_core.py"
    facts: [F-009]
---

# _enums.py 类型枚举：DataType 与 AttributeType

## 信源概述

| 信源 | 类型 | 行数 | 职责 |
|------|------|------|------|
| `src/onnx_ir/_enums.py` | Python 实现 | ~410行 | `AttributeType` 枚举（15种属性类型）、`DataType` 枚举（27种数据类型）、位宽映射、numpy 互操作 |
| `src/onnx_ir/_core.py` | Python 实现 | ~5300行 | `_NON_NUMPY_NATIVE_TYPES` 非原生类型集合、ml_dtypes 支持 |

## 关键事实登记

### F-005：AttributeType 属性类型枚举

**信源**：`src/onnx_ir/_enums.py` L14-L31

`AttributeType` 是 `IntEnum`，定义 15 种属性类型：

```python
class AttributeType(IntEnum):
    UNDEFINED = 0
    FLOAT = 1
    INT = 2
    STRING = 3
    TENSOR = 4
    GRAPH = 5
    FLOATS = 6
    INTS = 7
    STRINGS = 8
    TENSORS = 9
    GRAPHS = 10
    SPARSE_TENSOR = 11
    SPARSE_TENSORS = 12
    TYPE_PROTO = 13
    TYPE_PROTOS = 14
```

标量类型（FLOAT/INT/STRING/TENSOR/GRAPH/SPARSE_TENSOR/TYPE_PROTO）与列表类型（FLOATS/INTS/STRINGS/TENSORS/GRAPHS/SPARSE_TENSORS/TYPE_PROTOS）一一对应。

### F-006：DataType 数据类型枚举

**信源**：`src/onnx_ir/_enums.py` L40-L71

`DataType` 是 `IntEnum`，定义 27 种数据类型，从 UNDEFINED=0 到 INT2=26：

| 值 | 名称 | 说明 |
|----|------|------|
| 0 | UNDEFINED | 未定义 |
| 1 | FLOAT | float32 |
| 2 | UINT8 | uint8 |
| 3 | INT8 | int8 |
| 4 | UINT16 | uint16 |
| 5 | INT16 | int16 |
| 6 | INT32 | int32 |
| 7 | INT64 | int64 |
| 8 | STRING | 字符串 |
| 9 | BOOL | 布尔 |
| 10 | FLOAT16 | float16 |
| 11 | DOUBLE | float64 |
| 12 | UINT32 | uint32 |
| 13 | UINT64 | uint64 |
| 14 | COMPLEX64 | 复数64位（两个float32） |
| 15 | COMPLEX128 | 复数128位（两个float64） |
| 16 | BFLOAT16 | bfloat16 |
| 17-21 | FLOAT8系列 | FLOAT8E4M3FN/FLOAT8E4M3FNUZ/FLOAT8E5M2/FLOAT8E5M2FNUZ/FLOAT8E8M0 |
| 22 | UINT4 | 4位无符号整数 |
| 23 | INT4 | 4位有符号整数 |
| 24 | FLOAT4E2M1 | 4位浮点数 |
| 25 | UINT2 | 2位无符号整数 |
| 26 | INT2 | 2位有符号整数 |

### F-007：from_numpy() 类型映射

**信源**：`src/onnx_ir/_enums.py` L73-L110

`DataType.from_numpy()` 类方法将 numpy dtype 映射到 DataType：
- 标准 numpy 类型直接查表映射
- 通过 `dtype.names` 元组字段识别 ONNX 自定义 dtype（如 `("bfloat16",)`, `("e4m3fn",)` 等）
- ml_dtypes 提供的非标准类型通过 name 字段识别

### F-008：DataType 分类属性与方法

**信源**：`src/onnx_ir/_enums.py` L123-L380

| 属性/方法 | 返回值 | 说明 |
|-----------|--------|------|
| `itemsize` | int | 字节大小（4位/2位类型返回1） |
| `bitwidth` | int | 位宽（见F-010） |
| `numpy()` | np.dtype | 映射到 numpy dtype（非原生类型通过 ml_dtypes） |
| `short_name()` | str | 短名称（f32/i64/bf16 等） |
| `is_floating_point()` | bool | 是否浮点类型 |
| `is_integer()` | bool | 是否整数类型 |
| `is_signed()` | bool | 是否有符号 |
| `is_string()` | bool | 是否字符串类型 |

### F-009：非 numpy 原生类型集合

**信源**：`src/onnx_ir/_core.py` L87-L101

```python
_NON_NUMPY_NATIVE_TYPES = frozenset({
    DataType.BFLOAT16,
    DataType.FLOAT8E4M3FN,
    DataType.FLOAT8E4M3FNUZ,
    DataType.FLOAT8E5M2,
    DataType.FLOAT8E5M2FNUZ,
    DataType.FLOAT8E8M0,
    DataType.INT4,
    DataType.UINT4,
    DataType.FLOAT4E2M1,
    DataType.INT2,
    DataType.UINT2,
})
```

这些类型通过 `ml_dtypes` 包提供 numpy 支持。

### F-010：_BITWIDTH_MAP 位宽映射

**信源**：`src/onnx_ir/_enums.py` L382-L408

位宽映射明确记录每种 DataType 的精确位宽：

| 类型 | 位宽 | 备注 |
|------|------|------|
| COMPLEX64 | 64位 | 两个float32 |
| COMPLEX128 | 128位 | 两个float64 |
| INT4/UINT4/FLOAT4E2M1 | 4位 | 亚字节类型 |
| INT2/UINT2 | 2位 | 亚字节类型 |
| FLOAT/INT32/UINT32 | 32位 | 标准字长 |
| DOUBLE/INT64/UINT64 | 64位 | 双字长 |
