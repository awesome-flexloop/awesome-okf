---
type: concept
title: "类型系统：DataType 枚举、形状 Dimension、AttributeType"
description: "27种DataType覆盖从INT2到DOUBLE/COMPLEX128、bfloat16/float8系列到亚字节类型，SymbolicDim支持sympy符号运算，AttributeType定义15种属性类型，类型类层次支持Tensor/Sequence/Optional/Sparse递归组合"
sources:
  references: [../references/enums-types.md, ../references/core-entities.md]
  facts: [F-005, F-006, F-007, F-008, F-009, F-010, F-023, F-024, F-042, F-043]
---

# 类型系统：DataType 枚举、形状 Dimension、AttributeType

## 核心理解

onnx-ir 的类型系统由三部分组成：(1) `DataType` 枚举定义张量元素类型（27种，覆盖到位宽2位），(2) `SymbolicDim`/`Shape` 描述张量形状（支持符号维度和动态形状），(3) `AttributeType` 枚举定义算子属性类型（15种），外加递归类型类层次（TensorType/SequenceType/OptionalType/SparseTensorType）支持复杂类型组合。

## DataType：数据类型枚举

DataType 是 IntEnum，定义 27 种数据类型，从 UNDEFINED=0 到 INT2=26（F-006）。

### 类型分类

```
标准数值类型（numpy 原生支持）：
├── 浮点：FLOAT(1)/FLOAT16(10)/DOUBLE(11)
├── 整数：INT8(3)/INT16(5)/INT32(6)/INT64(7)
│        UINT8(2)/UINT16(4)/UINT32(12)/UINT64(13)
├── 复数：COMPLEX64(14)/COMPLEX128(15)
└── 布尔/字符串：BOOL(9)/STRING(8)

非标准类型（ml_dtypes 支持）：
├── BFLOAT16(16)
├── FLOAT8 系列：FLOAT8E4M3FN(17)/FLOAT8E4M3FNUZ(18)
│              FLOAT8E5M2(19)/FLOAT8E5M2FNUZ(20)/FLOAT8E8M0(21)
└── 亚字节类型：UINT4(22)/INT4(23)/FLOAT4E2M1(24)
              UINT2(25)/INT2(26)
```

### 分类查询方法（F-008）

| 方法 | 返回值 | 说明 |
|------|--------|------|
| `is_floating_point()` | bool | 是否浮点类型（含bfloat16/float8/float4） |
| `is_integer()` | bool | 是否整数类型（含int4/int2） |
| `is_signed()` | bool | 是否有符号整数 |
| `is_string()` | bool | 是否字符串类型 |

### numpy 互操作（F-007）

`DataType.from_numpy(dtype)` 类方法将 numpy dtype 映射到 DataType：
- 标准 numpy 类型直接查表
- 非标准类型通过 `dtype.names` 元组识别（如 `("bfloat16",)`, `("e4m3fn",)`）

`DataType.numpy()` 返回对应的 numpy dtype，非原生类型通过 `ml_dtypes` 包提供。

### 位宽与字节大小（F-008/F-010）

| 类型类别 | 位宽 | itemsize | 说明 |
|----------|------|----------|------|
| DOUBLE/INT64/UINT64/COMPLEX128 | 64 | 8 | COMPLEX128 = 2×float64 |
| FLOAT/INT32/UINT32/COMPLEX64 | 32 | 4 | COMPLEX64 = 2×float32 |
| FLOAT16/INT16/UINT16/BFLOAT16 | 16 | 2 | |
| FLOAT8系列/UINT8/INT8 | 8 | 1 | float8 占1字节存储 |
| UINT4/INT4/FLOAT4E2M1 | 4 | 1 | 4位值打包存储，itemsize=1 |
| UINT2/INT2 | 2 | 1 | 2位值打包存储，itemsize=1 |

`nbytes` 对亚字节类型使用 `math.ceil(dtype.itemsize * size)` 而非简单乘法（F-012）。

### 短名称（F-008）

`short_name()` 返回紧凑名称：
- 标准类型：`f32`, `i64`, `u8`, `bf16` 等
- float8：`e4m3fn`, `e5m2` 等
- 亚字节：`u4`, `i4`, `u2`, `i2`, `f4e2m1`

## AttributeType：属性类型枚举

AttributeType 是 IntEnum，定义 15 种属性类型（F-005）：

| 值 | 名称 | Python 类型 | 说明 |
|----|------|-------------|------|
| 0 | UNDEFINED | — | 未定义 |
| 1 | FLOAT | float | 标量浮点数 |
| 2 | INT | int | 标量整数 |
| 3 | STRING | str | 标量字符串 |
| 4 | TENSOR | TensorProtocol | 单个张量 |
| 5 | GRAPH | GraphProtocol | 单个子图 |
| 6 | FLOATS | tuple[float,...] | 浮点数列表 |
| 7 | INTS | tuple[int,...] | 整数列表 |
| 8 | STRINGS | tuple[str,...] | 字符串列表 |
| 9 | TENSORS | tuple[TensorProtocol,...] | 张量列表 |
| 10 | GRAPHS | tuple[GraphProtocol,...] | 子图列表 |
| 11 | SPARSE_TENSOR | SparseTensor | 稀疏张量 |
| 12 | SPARSE_TENSORS | tuple[SparseTensor,...] | 稀疏张量列表 |
| 13 | TYPE_PROTO | TypeAndShape | 类型引用 |
| 14 | TYPE_PROTOS | tuple[TypeAndShape,...] | 类型引用列表 |

Attr 构造时强制类型转换：INT/FLOAT 转为 Python 原生 int/float（而非 numpy 类型），列表类型强制转为 tuple（F-041）。

## SymbolicDim：符号维度

`SymbolicDim` 是不可变符号维度，内部存储 `_value`（str/None）和懒初始化的 `_expr_cache`（sympy.Expr）（F-023）。

### 支持的运算

```python
import onnx_ir as ir

d = ir.SymbolicDim("N")

# 算术运算
d + 1       # N + 1
d * 2       # 2 * N
d // 2      # floor(N / 2)
-d          # -N
d.ceil()    # ceil(N)
d.floor()   # floor(N)
d.trunc()   # trunc(N)

# 符号求值
d.evaluate({"N": 32})  # → 32
d.free_symbols()       # → {"N"}
```

## Shape：形状

`Shape` 描述张量的维度信息，支持静态、动态和未知维度（F-024）。

### 维度查询

```python
shape = ir.Shape((ir.SymbolicDim("N"), 3, 4))

shape.rank()              # → 3
shape.is_static(0)        # → False（N 是符号维度）
shape.is_static(1)        # → True（3 是静态维度）
shape.is_dynamic(0)       # → True
shape.has_unknown_dim()   # → False（没有 None 维度）
shape.numpy()             # 错误！存在动态维度，无法转为纯整数tuple

static_shape = ir.Shape((1, 3, 224, 224))
static_shape.numpy()      # → (1, 3, 224, 224)
```

### 冻结机制

```python
shape = ir.Shape((1, 3, 224))
shape.freeze()           # 冻结后不可修改
shape[0] = 2             # 错误！冻结后不可变
```

### 维度合并规则

当两个 Shape 需要合并时（如形状推断），优先级规则：
1. **int 优先于 SymbolicDim**：静态值比符号值更具体
2. **有名字的 SymbolicDim 优先于 None**：命名符号比未知维度信息更丰富
3. **同名字保留当前值**：同名符号维度以当前值为准

### Denotation 语义标注

```python
shape.set_denotation(0, "DATA_BATCH")
shape.get_denotation(0)  # → "DATA_BATCH"
```

## 类型类层次（F-042/F-043）

```
TypeProtocol
├── TensorType(dtype: DataType, shape: Shape | None)
│   └── SparseTensorType(elem_type: TensorType)
└── _RecursiveTypeBase(elem_type: TypeProtocol)
    ├── SequenceType(elem_type)
    └── OptionalType(elem_type)
```

- `TensorType`：最常用的稠密张量类型，指定元素类型和形状
- `SparseTensorType`：稀疏张量，包裹一个 TensorType 作为元素类型
- `SequenceType`：序列类型，元素可以是任意 TypeProtocol（递归）
- `OptionalType`：可选类型，元素可以是任意 TypeProtocol（递归）

递归类型通过递归 `__eq__` 比较元素类型，支持任意嵌套（如 `Sequence<Optional<Tensor<float>>>`）。

### TypeAndShape 组合

`TypeAndShape` 是 dataclass：

```python
@dataclass
class TypeAndShape:
    type: TypeProtocol | None
    shape: Shape | None
```

用于构造 TypeProto 属性值（`AttrType.TYPE_PROTO`），将类型和形状组合在一起。
