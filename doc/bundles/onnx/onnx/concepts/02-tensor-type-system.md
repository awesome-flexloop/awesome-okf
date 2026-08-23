---
type: concept
title: "张量类型系统"
description: "DataType 枚举26种数据类型、TensorProto 七种存储字段、TypeProto 六种类型变体、TensorShapeProto.Dimension 的 oneof 维度表示"
sources:
  references: [../references/onnx-proto.md, ../references/helper-api.md]
  facts: [F-009, F-010, F-011, F-012, F-013, F-014, F-015, F-019, F-030, F-032]
---

# 张量类型系统

## 核心理解

ONNX 的类型系统围绕 **TensorProto**（实际数据）和 **TypeProto**（类型描述）构建。TensorProto 存储张量的实际数值，TypeProto 描述值的类型（不限于张量，还包括序列、映射等复合类型）。理解数据类型枚举、存储字段映射和类型变体是正确构造和操作 ONNX 模型的基础。

## 机制详解

### DataType 枚举：26 种数据类型

TensorProto.DataType 枚举定义了 ONNX 支持的所有元素类型（F-009）：

```
整数类型：
├── 8位：  INT8(3), UINT8(2)
├── 16位： INT16(5), UINT16(4)
├── 32位： INT32(6), UINT32(12)
├── 64位： INT64(7), UINT64(13)
├── 4位：  INT4(22), UINT4(21)      ← 亚字节类型
└── 2位：  INT2(26), UINT2(25)      ← 亚字节类型

浮点类型：
├── IEEE 半精度： FLOAT16(10)
├── IEEE 单精度： FLOAT(1)
├── IEEE 双精度： DOUBLE(11)
├── BF16：       BFLOAT16(16)
├── 8位浮点：    FLOAT8E4M3FN(17), FLOAT8E4M3FNUZ(18),
│              FLOAT8E5M2(19), FLOAT8E5M2FNUZ(20)
├── 4位浮点：    FLOAT4E2M1(23)
└── 8位特殊：    FLOAT8E8M0(24)

其他类型：
├── BOOL(9) — 布尔值
├── STRING(8) — 字符串
├── COMPLEX64(14), COMPLEX128(15) — 复数
└── UNDEFINED(0) — 未定义（无效值）
```

### TensorProto 七种存储字段

张量数据可以通过七种不同的 proto 字段存储（F-010），helper.py 中的 `tensor_dtype_to_field()`（F-030）提供类型到字段的映射：

| 存储字段 | 字段号 | Proto 类型 | 对应 DataType | numpy 存储类型 (F-032) |
|----------|--------|-----------|---------------|----------------------|
| float_data | 4 | repeated float | FLOAT(1) | np.float32 |
| int32_data | 5 | repeated int32 | INT8, INT16, INT32, UINT8, UINT16, BOOL, FLOAT16, BFLOAT16, FLOAT8*, UINT4, INT4, FLOAT4E2M1, UINT2, INT2 | np.int32 |
| string_data | 6 | repeated bytes | STRING(8) | np.object_ |
| int64_data | 7 | repeated int64 | INT64(7) | np.int64 |
| raw_data | 9 | bytes | 所有数值类型 | 原始字节（小端序） |
| double_data | 10 | repeated double | DOUBLE(11) | np.float64 |
| uint64_data | 11 | repeated uint64 | UINT64(13), UINT32(12) | np.uint64 |

**存储策略选择**（F-025）：
- 默认（`raw=False`）：按类型选择对应重复字段存储
- `raw=True`：使用 raw_data 以原始字节存储，更紧凑
- STRING 类型不能使用 raw_data

**亚字节打包规则**：
- 4-bit 类型（UINT4/INT4/FLOAT4E2M1）：2 个元素打包到 1 字节
- 2-bit 类型（UINT2/INT2）：4 个元素打包到 1 字节

### TypeProto：六种类型变体

TypeProto 使用 `oneof value` 表示六种类型变体（F-014），字段号不连续：

```
TypeProto (oneof value):
│
├── (1) tensor_type → TypeProto.Tensor
│   ├── elem_type: int32 (DataType enum value)
│   └── shape: TensorShapeProto
│       └── dim[] → Dimension (oneof value)
│           ├── dim_value: int64    ← 静态维度
│           └── dim_param: string   ← 符号/动态维度
│           └── denotation: string  ← 语义标注（可选）
│
├── (4) sequence_type → TypeProto.Sequence
│   └── elem_type: TypeProto  ← 序列元素类型
│
├── (5) map_type → TypeProto.Map
│   ├── key_type: int32       ← 键类型（必须是整数或字符串基本类型）
│   └── value_type: TypeProto ← 值类型
│
├── (7) opaque_type → TypeProto.Opaque
│   ├── domain: string
│   └── name: string
│
├── (8) sparse_tensor_type → TypeProto.SparseTensor
│   ├── elem_type: int32
│   └── shape: TensorShapeProto  ← 结构同 Tensor
│
└── (9) optional_type → TypeProto.Optional
    └── elem_type: TypeProto  ← 包装的类型
```

**字段号缺口说明**：字段 2、3、6 不存在（预留/废弃），从 1 跳到 4、5，再到 7、8、9。这是 protobuf 演进的正常现象。

### TensorShapeProto.Dimension：维度的 oneof 表示

每个维度有三种状态（F-013），通过 protobuf oneof 实现：

```python
# 状态1：静态维度（具体整数）
dim.dim_value = 768     # 例如 hidden_size=768

# 状态2：符号维度（动态参数）
dim.dim_param = "batch_size"  # 例如动态batch

# 状态3：未知维度
# 既不设置 dim_value 也不设置 dim_param
```

`make_tensor_value_info()`（F-028）中 shape 参数的 None 处理：
- `int` 值 → 设置 `dim_value`
- `str` 值 → 设置 `dim_param`
- `None` 值 → 不设置（未知维度）
- 空列表 `[]` → 产生空 dim 列表（标量，与 None 不同）

### SparseTensorProto：稀疏张量

稀疏张量使用三个字段表示（F-019）：

| 字段 | 类型 | 说明 |
|------|------|------|
| values | TensorProto | 非零值，形状 [NNZ]（非零元素数） |
| indices | TensorProto | 索引，形状 [NNZ, rank]（COO格式）或 [NNZ] |
| dims | int64[] | 稀疏张量的完整维度 |

### 外部数据：突破内存限制

TensorProto 支持数据存储在 protobuf 消息外部（F-011, F-012）：

- `data_location`（字段14）：DataLocation 枚举
  - DEFAULT(0)：数据在 proto 内部（默认）
  - EXTERNAL(1)：数据在外部文件
- `external_data`（字段13）：StringStringEntryProto 键值对
  - `"location"`（必需）：外部文件路径
  - `"offset"`（可选）：字节偏移
  - `"length"`（可选）：数据字节长度
  - `"checksum"`（可选）：校验和

## 类型关系图

```
                        TypeProto
                       ╱    │    ╲
                      ╱     │     ╲
          tensor_type  sequence  map_type
              │          │        │
         elem_type    elem_type  key_type
         shape:      (TypeProto) value_type
         TensorShape    ↑        (TypeProto)
           │            │
         dim[] ──→ Dimension (oneof: dim_value | dim_param)
              ↑
    TensorProto.data_type (DataType enum) 必须与 tensor_type.elem_type 匹配
    TensorProto.dims[] 必须与 shape.dim[] 一致
```

## 关键洞察/反常识

1. **int32_data 是"万能"小整数存储**：INT8/UINT8/BOOL/FLOAT16/BFLOAT16/FLOAT8/UINT4/INT4 等都存储在 int32_data 中（F-032），读取时需要按实际 elem_type 重新解释字节。
2. **raw_data 小端序**：使用 raw_data 时数据按小端序存储，大端系统上 numpy_helper.to_array() 会自动 byteswap（F-075）。
3. **空shape ≠ 未设置shape**：make_tensor_value_info 中传入 `shape=[]` 产生空 dim 列表（标量形状），传入 `shape=None` 不设置 shape（完全未知）。
4. **TypeProto 不只有张量**：很多人以为 ONNX 只有张量类型，实际上还支持 sequence、map、optional、sparse_tensor、opaque 五种复合类型。
5. **维度可以同时表示静态/动态/未知**：通过 oneof 的 dim_value/dim_param 三态，同一个类型系统中支持形状推断从完全未知到完全静态的渐进精化。

## 关联概念

- [Protobuf IR：核心 Message 结构](01-protobuf-ir.md) — 理解 TensorProto/TypeProto 在整体 message 结构中的位置
- [计算图模型](03-computation-graph.md) — initializer（TensorProto）与图输入（ValueInfoProto）的区别
- [序列化与外部数据](08-serialization.md) — 外部数据机制的安全防御和加载
- [Python Helper API 详解](09-python-helpers.md) — make_tensor/make_tensor_value_info 的具体用法
