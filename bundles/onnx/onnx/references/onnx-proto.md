---
type: reference
title: "onnx.proto：Protobuf IR 核心 Message 定义"
description: "onnx.proto 中 ModelProto/GraphProto/NodeProto/AttributeProto/TensorProto/ValueInfoProto/TypeProto/FunctionProto/OperatorSetIdProto/SparseTensorProto 的字段定义、字段号与关系"
sources:
  - path: "external/libs/models/onnx/onnx/onnx/onnx.proto"
    facts: [F-001, F-002, F-003, F-004, F-005, F-006, F-007, F-008, F-009, F-010, F-011, F-012, F-013, F-014, F-015, F-016, F-017, F-018, F-019, F-020]
---

# onnx.proto：Protobuf IR 核心 Message 定义

## 信源概述

| 信源 | 类型 | 行数 | 职责 |
|------|------|------|------|
| `onnx/onnx.proto` | Protobuf 定义 | ~1050行 | ONNX 标准 IR 的唯一权威定义，所有跨语言交换的事实源 |

## 关键事实登记

### F-001：AttributeProto 包含 14 种属性类型枚举值

**信源**：`onnx/onnx.proto` L144-L161

```protobuf
enum AttributeType {
  UNDEFINED = 0;
  FLOAT = 1;
  INT = 2;
  STRING = 3;
  TENSOR = 4;
  GRAPH = 5;
  SPARSE_TENSOR = 11;
  TYPE_PROTO = 13;
  FLOATS = 6;
  INTS = 7;
  STRINGS = 8;
  TENSORS = 9;
  GRAPHS = 10;
  SPARSE_TENSORS = 12;
  TYPE_PROTOS = 14;
}
```

单值类型（1-5, 11, 13）与复数列表类型（6-10, 12, 14）对应：float/FLOATS、int/INTS、string/STRINGS、tensor/TENSORS、graph/GRAPHS、sparse_tensor/SPARSE_TENSORS、type_proto/TYPE_PROTOS。

### F-002：AttributeProto 包含 ref_attr_name 字段用于属性引用

**信源**：`onnx/onnx.proto` L166-L170

`ref_attr_name`（字段号21）为字符串类型，仅在子图（函数）中有效。当属性设置了 `ref_attr_name` 时，该属性不携带值，而是在实例化时从父函数作用域中引用同名属性的值。这是函数参数化的核心机制。

### F-003：AttributeProto 的 type 字段是类型鉴别器

**信源**：`onnx/onnx.proto` L175-L181

`type` 字段（字段号20）为 AttributeType 枚举值。从 IR_VERSION >= 2（IR_VERSION_2017_10_30）起，type 字段必须设置，并且必须与实际填充的值字段相匹配（例如 type=FLOAT 时只能设置 f 字段，不能设置 i 字段）。

### F-004：ValueInfoProto 包含四个字段

**信源**：`onnx/onnx.proto` L205-L215

```protobuf
message ValueInfoProto {
  optional string name = 1;
  optional TypeProto type = 2;
  optional string doc_string = 3;
  repeated StringStringEntryProto metadata_props = 4;
}
```

ValueInfoProto 是值的元信息描述：名字、类型、文档、元数据。它描述图中每个值（输入/输出/中间值）的类型信息。

### F-005：NodeProto 完整字段定义

**信源**：`onnx/onnx.proto` L224-L250

```protobuf
message NodeProto {
  repeated string input = 1;
  repeated string output = 2;
  optional string name = 3;
  optional string op_type = 4;
  repeated AttributeProto attribute = 5;
  optional string doc_string = 6;
  optional string domain = 7;
  optional string overload = 8;
  repeated StringStringEntryProto metadata_props = 9;
  repeated DeviceTypeProto device_configurations = 10;
}
```

- `input`/`output`：字符串列表，通过名字引用值，构成图的连接边
- `op_type`：算子类型名（如 "Conv"、"Relu"）
- `domain`：算子域（空字符串表示标准域）
- `overload`：函数重载名（IR >= 8）
- `attribute`：节点属性列表

### F-006：ModelProto 的 ir_version 和 opset_import 字段

**信源**：`onnx/onnx.proto` L449-L462

ModelProto 中 `ir_version`（字段1）必须存在，表示模型遵循的 IR 规范版本。`opset_import`（字段8）为重复的 OperatorSetIdProto，声明模型使用的算子集版本。

### F-007：ModelProto 支持 functions 字段存储模型局部函数

**信源**：`onnx/onnx.proto` L505-L521；L99-L104

从 IR_VERSION >= 8（IR_VERSION_2021_7_30）起，ModelProto 包含 `functions` 字段（字段25），为重复的 FunctionProto。模型局部函数由 (domain, name, overload) 三元组唯一标识。

### F-008：GraphProto 完整字段定义

**信源**：`onnx/onnx.proto` L564-L602

```protobuf
message GraphProto {
  repeated NodeProto node = 1;
  optional string name = 2;
  repeated TensorProto initializer = 5;
  repeated SparseTensorProto sparse_initializer = 15;
  optional string doc_string = 10;
  repeated ValueInfoProto input = 11;
  repeated ValueInfoProto output = 12;
  repeated ValueInfoProto value_info = 13;
  repeated QuantizationAnnotationProto quantization_annotation = 14;
  repeated StringStringEntryProto metadata_props = 16;
}
```

注意字段号不连续（3、4被保留/废弃），`initializer` 在字段5而非3。`value_info` 存储形状推断产生的中间值类型信息。

### F-009：TensorProto.DataType 枚举定义 26 种数据类型

**信源**：`onnx/onnx.proto` L608-L663

| 值 | 名称 | 说明 |
|----|------|------|
| 0 | UNDEFINED | 未定义 |
| 1 | FLOAT | 32位浮点数 |
| 2 | UINT8 | 8位无符号整数 |
| 3 | INT8 | 8位有符号整数 |
| 4 | UINT16 | 16位无符号整数 |
| 5 | INT16 | 16位有符号整数 |
| 6 | INT32 | 32位有符号整数 |
| 7 | INT64 | 64位有符号整数 |
| 8 | STRING | 字符串 |
| 9 | BOOL | 布尔值 |
| 10 | FLOAT16 | 16位浮点数 |
| 11 | DOUBLE | 64位浮点数 |
| 12 | UINT32 | 32位无符号整数 |
| 13 | UINT64 | 64位无符号整数 |
| 14 | COMPLEX64 | 64位复数 |
| 15 | COMPLEX128 | 128位复数 |
| 16 | BFLOAT16 | BFloat16 |
| 17 | FLOAT8E4M3FN | 8位浮点 E4M3 |
| 18 | FLOAT8E4M3FNUZ | 8位浮点 E4M3 无零 |
| 19 | FLOAT8E5M2 | 8位浮点 E5M2 |
| 20 | FLOAT8E5M2FNUZ | 8位浮点 E5M2 无零 |
| 21 | UINT4 | 4位无符号整数 |
| 22 | INT4 | 4位有符号整数 |
| 23 | FLOAT4E2M1 | 4位浮点 |
| 24 | FLOAT8E8M0 | 8位浮点 E8M0 |
| 25 | UINT2 | 2位无符号整数 |
| 26 | INT2 | 2位有符号整数 |

### F-010：TensorProto 的七种数据存储字段

**信源**：`onnx/onnx.proto` L686-L785

| 字段名 | 字段号 | 类型 | 适用 DataType |
|--------|--------|------|---------------|
| float_data | 4 | repeated float | FLOAT |
| int32_data | 5 | repeated int32 | INT8, INT16, INT32, UINT8, UINT16, BOOL, FLOAT16, BFLOAT16, FLOAT8系列, UINT4, INT4, FLOAT4E2M1, UINT2, INT2 |
| string_data | 6 | repeated bytes | STRING |
| int64_data | 7 | repeated int64 | INT64 |
| raw_data | 9 | bytes | 所有数值类型（原始字节） |
| double_data | 10 | repeated double | DOUBLE |
| uint64_data | 11 | repeated uint64 | UINT64, UINT32 |

数据可以通过类型特定的重复字段存储，也可以通过 raw_data 以原始字节方式存储（小端序）。

### F-011：TensorProto 包含 external_data 字段

**信源**：`onnx/onnx.proto` L751-L760

`external_data`（字段13）为重复的 StringStringEntryProto 键值对，描述外部数据存储位置。识别键：
- `"location"`（必需）：外部数据文件路径
- `"offset"`（可选）：数据在文件中的字节偏移
- `"length"`（可选）：数据字节长度
- `"checksum"`（可选）：校验和

### F-012：TensorProto 的 data_location 字段

**信源**：`onnx/onnx.proto` L762-L771

`data_location`（字段14）为 DataLocation 枚举：
- `DEFAULT = 0`：数据存储在 protobuf 消息内部（默认）
- `EXTERNAL = 1`：数据存储在外部文件中，由 external_data 字段描述

### F-013：TensorShapeProto.Dimension 使用 oneof 表示维度

**信源**：`onnx/onnx.proto` L819-L833

```protobuf
message Dimension {
  oneof value {
    int64 dim_value = 1;
    string dim_param = 2;
  };
  optional string denotation = 3;
}
```

维度可以是具体整数值（静态形状）或符号参数字符串（动态形状，如 "batch_size"）。`denotation` 提供语义标注（如 "DATA_BATCH"）。

### F-014：TypeProto 使用 oneof value 表示六种类型变体

**信源**：`onnx/onnx.proto` L838-L916

| 变体 | 字段号 | 说明 |
|------|--------|------|
| tensor_type | 1 | 张量类型 |
| sequence_type | 4 | 序列类型 |
| map_type | 5 | 映射类型 |
| optional_type | 9 | 可选类型 |
| sparse_tensor_type | 8 | 稀疏张量类型 |
| opaque_type | 7 | 不透明类型 |

注意字段号不连续（2、3、6被保留）。

### F-015：TypeProto 各变体的结构

**信源**：`onnx/onnx.proto` L840-L890

- `TypeProto.Tensor`：`elem_type`（int32，字段1）+ `shape`（TensorShapeProto，字段2）
- `TypeProto.SparseTensor`：结构同 Tensor
- `TypeProto.Sequence`：`elem_type`（TypeProto，字段1）
- `TypeProto.Optional`：`elem_type`（TypeProto，字段1）
- `TypeProto.Map`：`key_type`（int32，字段1）+ `value_type`（TypeProto，字段2）
- `TypeProto.Opaque`：`domain`（string，字段1）+ `name`（string，字段2）

### F-016：FunctionProto 完整字段定义

**信源**：`onnx/onnx.proto` L946-L1011

```protobuf
message FunctionProto {
  optional string name = 1;
  repeated string input = 4;
  repeated string output = 5;
  repeated string attribute = 6;
  repeated NodeProto node = 7;
  repeated OperatorSetIdProto opset_import = 9;
  optional string domain = 10;
  repeated AttributeProto attribute_proto = 11;
  repeated ValueInfoProto value_info = 12;
  optional string overload = 13;
  repeated StringStringEntryProto metadata_props = 14;
}
```

FunctionProto 定义一个函数体：输入输出名字、属性参数名、节点列表、opset导入、属性默认值。

### F-017：FunctionProto 的 since_version 和 status 已废弃

**信源**：`onnx/onnx.proto` L951-L959

`since_version`（字段2）和 `status`（字段3）在 IR_VERSION 8 中废弃，使用 `reserved` 关键字保留字段号，不再使用。

### F-018：OperatorSetIdProto 定义算子集标识

**信源**：`onnx/onnx.proto` L928-L938

```protobuf
message OperatorSetIdProto {
  optional string domain = 1;
  optional int64 version = 2;
}
```

`domain` 为空字符串或缺失时表示 ONNX 标准域（""），与 "ai.onnx" 等价。`version` 必须存在。

### F-019：SparseTensorProto 稀疏张量结构

**信源**：`onnx/onnx.proto` L792-L814

```protobuf
message SparseTensorProto {
  optional TensorProto values = 1;   // 形状 [NNZ]
  optional TensorProto indices = 2;  // 形状 [NNZ, rank] 或 [NNZ]（COO格式）
  repeated int64 dims = 3;           // 稀疏张量的完整维度
}
```

### F-020：IR_VERSION 枚举当前值为 14

**信源**：`onnx/onnx.proto` L50-L130

IR_VERSION 从 IR_VERSION_2017_10_10=1 演进到当前 IR_VERSION=0x0000000E=14。共定义了 14 个版本里程碑，每个版本引入新的 proto 字段或语义约束。

```protobuf
const int32 IR_VERSION = 0x0000000E;  // 14
```

## Message 关系图

```
ModelProto
├── ir_version (int32)
├── opset_import[] → OperatorSetIdProto (domain, version)
├── producer_name / producer_version / domain / model_version / doc_string
├── metadata_props[]
├── training_info[]
├── functions[] → FunctionProto
│   ├── name / domain / overload
│   ├── input[] / output[] (string names)
│   ├── attribute[] (string names)
│   ├── attribute_proto[] → AttributeProto (defaults)
│   ├── node[] → NodeProto
│   └── opset_import[] → OperatorSetIdProto
└── graph → GraphProto
    ├── node[] → NodeProto
    │   ├── input[] / output[] (string names → edge connections)
    │   ├── op_type / domain / overload / name / doc_string
    │   └── attribute[] → AttributeProto
    │       ├── type (AttributeType enum)
    │       ├── ref_attr_name (optional, for function attribute reference)
    │       └── value fields: f/i/s/t/g/fs/is/ss/ts/gs/sparse_tensors/type_protos
    ├── input[] / output[] / value_info[] → ValueInfoProto
    │   ├── name / doc_string
    │   └── type → TypeProto
    │       ├── oneof: tensor_type / sparse_tensor_type / sequence_type / map_type / optional_type / opaque_type
    │       └── (tensor_type has shape → TensorShapeProto → Dimension[])
    ├── initializer[] → TensorProto
    │   ├── dims[] / data_type / doc_string
    │   ├── data storage: float_data/int32_data/string_data/int64_data/raw_data/double_data/uint64_data
    │   ├── external_data[] (key-value for external storage)
    │   └── data_location (DEFAULT/EXTERNAL)
    └── sparse_initializer[] → SparseTensorProto
        ├── values → TensorProto [NNZ]
        ├── indices → TensorProto [NNZ, rank]
        └── dims[] (full shape dimensions)
```
