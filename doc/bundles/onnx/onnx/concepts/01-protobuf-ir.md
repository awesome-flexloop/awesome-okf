---
type: concept
title: "Protobuf IR：核心 Message 结构"
description: "ModelProto/GraphProto/NodeProto/AttributeProto 等核心 Protobuf message 的字段定义、字段号、必选/可选字段与嵌套关系"
sources:
  references: [../references/onnx-proto.md]
  facts: [F-001, F-002, F-003, F-004, F-005, F-006, F-007, F-008, F-016, F-017, F-018, F-020]
---

# Protobuf IR：核心 Message 结构

## 核心理解

ONNX 的全部语义都编码在一组 Protobuf message 中。这些 message 在 [onnx.proto](../references/onnx-proto.md) 中定义，是跨语言模型交换的**唯一事实源**。理解这些 message 的结构和关系，是理解 ONNX 的基础。

核心 message 的包含关系：

```
ModelProto (模型顶级容器)
│
├── ir_version (int32, 字段1) ─── 必须存在
├── opset_import[] ─────────────→ OperatorSetIdProto[] (字段8, IR>=3必须)
│   ├── domain (string, 字段1)
│   └── version (int64, 字段2) ── 必须存在
│
├── producer_name / producer_version / domain / model_version / doc_string
├── metadata_props[] (StringStringEntryProto)
│
├── graph (字段7?) ─────────────→ GraphProto
│   ├── node[] (字段1) ────────→ NodeProto[]
│   ├── name (字段2)
│   ├── initializer[] (字段5) ─→ TensorProto[]
│   ├── sparse_initializer[] (字段15) → SparseTensorProto[]
│   ├── input[] (字段11) ──────→ ValueInfoProto[]
│   ├── output[] (字段12) ─────→ ValueInfoProto[]
│   ├── value_info[] (字段13) ──→ ValueInfoProto[]
│   └── doc_string (字段10)
│
└── functions[] (字段25, IR>=8) → FunctionProto[]
    ├── name / domain / overload
    ├── input[] / output[] (string names)
    ├── attribute[] (string names — 形参)
    ├── attribute_proto[] (AttributeProto — 默认值)
    ├── node[] (NodeProto — 函数体)
    └── opset_import[] (OperatorSetIdProto)
```

## 机制详解

### ModelProto：模型顶级容器

ModelProto 是模型序列化时的根 message。关键字段：

| 字段名 | 字段号 | 类型 | 必选 | 说明 |
|--------|--------|------|------|------|
| ir_version | 1 | int64 | ✅ | IR 规范版本（当前14），决定可用字段和语义 |
| opset_import | 8 | OperatorSetIdProto[] | IR≥3 ✅ | 使用的算子域及版本 |
| producer_name | 2 | string | ❌ | 生产者名称 |
| producer_version | 3 | string | ❌ | 生产者版本 |
| domain | 4 | string | ❌ | 模型域名 |
| model_version | 5 | int64 | ❌ | 模型版本号 |
| doc_string | 6 | string | ❌ | 文档描述 |
| graph | 7 | GraphProto | ✅ | 主计算图 |
| metadata_props | 14 | StringStringEntryProto[] | ❌ | 元数据键值对 |
| functions | 25 | FunctionProto[] | IR≥8 | 模型局部函数定义 |

**注意字段号不连续**：字段号 9-24 中部分被预留（training_info 在其他位置等）。

### GraphProto：计算图

GraphProto 表示一个计算图，可以是主图（model.graph）或子图（节点的 GRAPH 属性）。

| 字段名 | 字段号 | 类型 | 说明 |
|--------|--------|------|------|
| node | 1 | NodeProto[] | 计算节点列表（拓扑序） |
| name | 2 | string | 图名称 |
| initializer | 5 | TensorProto[] | 初始化器（常量权重） |
| sparse_initializer | 15 | SparseTensorProto[] | 稀疏初始化器 |
| doc_string | 10 | string | 文档描述 |
| input | 11 | ValueInfoProto[] | 图输入 |
| output | 12 | ValueInfoProto[] | 图输出 |
| value_info | 13 | ValueInfoProto[] | 中间值类型信息（形状推断结果） |
| metadata_props | 16 | StringStringEntryProto[] | 元数据 |

**注意**：`initializer` 在字段号 5，不是 3 或 4（这些字段号被历史废弃）。

### NodeProto：计算节点

NodeProto 表示计算图中的一个算子调用。节点通过 input/output 字符串名字相互连接。

| 字段名 | 字段号 | 类型 | 说明 |
|--------|--------|------|------|
| input | 1 | string[] | 输入值名列表（字符串引用） |
| output | 2 | string[] | 输出值名列表（定义新名字） |
| name | 3 | string | 节点名称（可选） |
| op_type | 4 | string | 算子类型名（如"Conv"、"Add"） |
| attribute | 5 | AttributeProto[] | 节点属性 |
| doc_string | 6 | string | 文档 |
| domain | 7 | string | 算子域（空=标准域） |
| overload | 8 | string | 函数重载名（IR≥8） |
| metadata_props | 9 | StringStringEntryProto[] | 元数据 |

**核心机制**：节点之间不直接引用对方，而是通过字符串名字连接。一个节点的 output 中定义的名字，可以被后续节点的 input 引用。这构成了计算图的边。

```python
# 示例：两个节点通过字符串名字 "Y" 连接
node1 = make_node("MatMul", ["X", "W"], ["Y"])      # 输出 "Y"
node2 = make_node("Add", ["Y", "B"], ["Z"])          # 输入引用 "Y"
```

### AttributeProto：节点属性

AttributeProto 是节点的参数。每个属性有一个类型鉴别器和对应的值字段。

| 字段名 | 字段号 | 类型 | 说明 |
|--------|--------|------|------|
| name | 1 | string | 属性名 |
| ref_attr_name | 21 | string | 引用属性名（函数内用） |
| doc_string | 13 | string | 文档 |
| type | 20 | AttributeType | 类型鉴别器（IR≥2必须设置） |

值字段（根据 type 选择使用哪个字段）：

| type 值 | 使用字段 | Python 类型 |
|---------|---------|-------------|
| FLOAT (1) | f (字段2) | float |
| INT (2) | i (字段3) | int |
| STRING (3) | s (字段4) | bytes |
| TENSOR (4) | t (字段5) | TensorProto |
| GRAPH (5) | g (字段6) | GraphProto（子图！） |
| FLOATS (6) | floats (字段7) | float[] |
| INTS (7) | ints (字段8) | int[] |
| STRINGS (8) | strings (字段9) | bytes[] |
| TENSORS (9) | tensors (字段10) | TensorProto[] |
| GRAPHS (10) | graphs (字段11) | GraphProto[] |
| SPARSE_TENSOR (11) | sparse_tensor (字段22) | SparseTensorProto |
| TYPE_PROTO (13) | tp (字段23) | TypeProto |
| SPARSE_TENSORS (12) | sparse_tensors (字段24) | SparseTensorProto[] |
| TYPE_PROTOS (14) | type_protos (字段25) | TypeProto[] |

**引用属性（F-002）**：当属性设置了 `ref_attr_name` 而非具体值时，它在子图（函数体）中作为形参引用父作用域的属性值。这是函数参数化的核心机制。

### ValueInfoProto：值的元信息

ValueInfoProto 描述一个值（图输入/输出/中间值）的名字和类型：

| 字段名 | 字段号 | 类型 |
|--------|--------|------|
| name | 1 | string |
| type | 2 | TypeProto |
| doc_string | 3 | string |
| metadata_props | 4 | StringStringEntryProto[] |

### FunctionProto：函数定义（IR≥8）

FunctionProto 定义可复用的函数体，允许模型中定义自定义算子组合。

| 字段名 | 字段号 | 类型 | 说明 |
|--------|--------|------|------|
| name | 1 | string | 函数名 |
| input | 4 | string[] | 输入值名 |
| output | 5 | string[] | 输出值名 |
| attribute | 6 | string[] | 属性参数名列表 |
| node | 7 | NodeProto[] | 函数体节点 |
| opset_import | 9 | OperatorSetIdProto[] | 使用的算子集 |
| domain | 10 | string | 域名 |
| attribute_proto | 11 | AttributeProto[] | 属性默认值 |
| value_info | 12 | ValueInfoProto[] | 值信息 |
| overload | 13 | string | 重载名 |

> **废弃字段**：since_version（字段2）和 status（字段3）在 IR 8 中废弃，使用 `reserved` 保留。

### OperatorSetIdProto：算子集标识

| 字段名 | 字段号 | 类型 | 说明 |
|--------|--------|------|------|
| domain | 1 | string | 算子域（空=""=标准域，等价于"ai.onnx"） |
| version | 2 | int64 | 算子集版本号（必须存在） |

## IR_VERSION 演进

IR_VERSION 从 1 演进到 14（F-020），主要里程碑：

| IR_VERSION | 标识 | 引入的关键特性 |
|------------|------|---------------|
| 1 | IR_VERSION_2017_10_10 | 初始版本 |
| 2 | IR_VERSION_2017_10_30 | AttributeProto.type 必须设置 |
| 3 | IR_VERSION_2017_11_3 | opset_import 成为必须 |
| 4 | IR_VERSION_2017_11_13 | initializer 不再要求在 input 中声明 |
| 5 | - | 类型系统扩展 |
| 6 | IR_VERSION_2019_1_22 | seq/map/opt 类型 |
| 7 | IR_VERSION_2020_5_8 | 稀疏张量等 |
| 8 | IR_VERSION_2021_7_30 | functions 局部函数、overload |
| 9 | - | 类型注解等 |
| 10 | - | 扩展属性类型 |
| 14 | IR_VERSION (当前) | 最新版本 |

## 关键反常识

1. **字段号不是连续的**：GraphProto 中 initializer 在字段 5 而非 3，中间的 3、4 被废弃保留。这是 protobuf 演进的正常现象——字段号一旦分配就不能复用。
2. **节点通过字符串连接，不是指针**：NodeProto 之间没有引用，input/output 是字符串名字。这使得序列化/反序列化非常简单，但名字冲突检测需要额外机制。
3. **子图是属性，不是独立引用**：控制流算子（If、Loop、Scan）的子图通过 GRAPH 类型的属性嵌入，而不是独立的顶级结构。
4. **attribute 字段号分散**：属性的值字段号从 2 到 25 不等，不是连续块，需要根据 type 字段选择正确的值字段。

## 关联概念

- [ONNX 整体架构与生态定位](00-overall-architecture.md) — 理解 Protobuf 层在三层架构中的地位
- [张量类型系统](02-tensor-type-system.md) — TensorProto 和 TypeProto 的详细类型表示
- [计算图模型](03-computation-graph.md) — 理解 NodeProto 字符串连接构成的图拓扑
- [Python Helper API 详解](09-python-helpers.md) — 如何使用 make_* 函数构造这些 message
