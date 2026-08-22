---
type: concept
title: "ONNX 整体架构与生态定位"
description: "ONNX 的三层架构（Protobuf 标准/C++ IR/Python Helper）、五个核心架构洞察、在 AI 模型交换生态中的定位"
sources:
  references: [../references/onnx-proto.md, ../references/helper-api.md, ../references/cpp-ir.md, ../references/op-schema.md, ../references/checker.md, ../references/serialization.md]
  facts: [F-001, F-005, F-006, F-008, F-021, F-023, F-034, F-046, F-049, F-052, F-053, F-054, F-064]
---

# ONNX 整体架构与生态定位

## 核心理解

ONNX（Open Neural Network Exchange）是一个**开放的神经网络模型交换格式**。它不是一个推理框架，也不是一个训练框架——它定义了一种通用的、跨框架的计算图表示标准，使得模型可以在 PyTorch、TensorFlow、TensorRT、ONNX Runtime 等不同框架之间自由转换和部署。

ONNX 的核心架构遵循**三层分离设计**：

```
┌──────────────────────────────────────────────────────────────────┐
│                     Python Helper API 层                         │
│  make_node / make_graph / make_model / make_tensor / ...         │
│  numpy_helper / external_data_helper / checker.py (委托层)       │
│  作用：便捷构造 Protobuf 对象，提供友好的 Pythonic 接口          │
├──────────────────────────────────────────────────────────────────┤
│                     C++ IR 操作层                                │
│  Graph / Node / Value (common/ir.h)                             │
│  OpSchema 注册表 / Shape Inference / Checker (C++实现)          │
│  作用：高性能图操作、形状推断、验证、优化                        │
│  注意：Python 端不直接暴露此层，通过 pybind11 绑定隐式使用      │
├──────────────────────────────────────────────────────────────────┤
│                     Protobuf 标准交换层（唯一事实源）            │
│  ModelProto / GraphProto / NodeProto / TensorProto / ...        │
│  onnx.proto 定义 → 跨语言零拷贝交换的标准格式                   │
│  作用：所有框架之间的模型交换都通过 Protobuf 序列化/反序列化     │
└──────────────────────────────────────────────────────────────────┘
```

## 三层架构详解

### 1. Protobuf 标准层——唯一事实源

Protobuf message 定义（[onnx.proto](../references/onnx-proto.md)）是 ONNX 的绝对权威。所有跨语言、跨框架的模型交换都通过这些 message 的序列化/反序列化完成：

- **ModelProto**：模型顶级容器，包含 ir_version、opset_import、graph、functions 等
- **GraphProto**：计算图，包含 node、input、output、initializer、value_info
- **NodeProto**：计算节点，通过 input/output 字符串名字连接成图
- **TensorProto**：张量数据，支持7种存储字段和外部数据
- **TypeProto**：类型系统，支持 tensor/sequence/map/optional/sparse/opaque 六种变体

**关键认知**：无论使用什么语言或工具创建 ONNX 模型，最终都必须序列化为符合 onnx.proto 定义的字节流。这保证了互操作性。

### 2. C++ IR 操作层——高性能内部表示

C++ IR（[common/ir.h](../references/cpp-ir.md)）定义在 `onnx/common/ir.h` 中，是 ONNX C++ 内部用于高效操作计算图的数据结构：

- 使用 **Graph/Node/Value** 三核心类，通过 `unique_ptr` 管理所有权
- Node 使用**双向循环链表**（哨兵节点模式）维护拓扑序
- Value 支持 **replaceAllUsesWith** 进行图变换
- CRTP（奇异递归模板模式）Attributes 提供类型安全的属性访问

**关键认知**：Python 端**没有**对应的 Python 版 Graph/Node 类——所有 Python API 直接操作 Protobuf message 对象。C++ IR 只在 C++ checker、shape_inference、version_converter、optimizer 内部使用。

### 3. Python Helper 层——便捷构造 API

Python Helper API（[helper.py](../references/helper-api.md)）提供 `make_*` 系列函数，是构造 ONNX 模型最常用的入口：

- `make_node()`：创建 NodeProto，kwargs 自动转属性
- `make_graph()`：创建 GraphProto
- `make_model()`：创建 ModelProto，自动设置 ir_version 和 opset
- `make_tensor()`：创建 TensorProto，支持 raw_data 压缩和亚字节打包
- `make_attribute()`：自动推断类型创建 AttributeProto
- `make_tensor_value_info()`：创建 ValueInfoProto，支持符号维度

## 五个核心架构洞察

### 洞察 I-01：Protobuf 是唯一事实源

Python 端没有独立的图类层次，直接操作嵌套的 Protobuf message。这意味着：
- ✅ 零转换开销：Python 创建的对象就是最终序列化的对象
- ❌ 图遍历和变换需要手动操作 protobuf 重复字段（repeated fields）
- C++ IR 与 Protobuf 之间通过 `ir_pb_converter` 双向转换

### 洞察 I-02：OpSchema 注册表驱动算子生态

算子通过 OpSchema 链式 API 声明签名，ONNX_OPERATOR_SET_SCHEMA 宏注册到全局单例 OpSchemaRegistry。同一算子的不同版本是独立条目，通过 (domain, op_type, version) 三元组查找。详见[算子定义与注册机制](05-operator-schema.md)。

### 洞察 I-03：Checker 是 C++ 实现的多层验证体系

Python checker.py 只是薄层——所有 proto 序列化后委托给 C++ 实现。默认 check_model 不做形状推断，只有 full_check=True 才执行。详见[模型检查器 Checker](07-model-checker.md)。

### 洞察 I-04：序列化是注册表架构

通过 _Registry 管理四种序列化格式（protobuf/textproto/json/onnxtxt），2 GiB 的 protobuf 硬限制通过外部数据机制突破。详见[序列化与外部数据](08-serialization.md)。

### 洞察 I-05：版本管理是表驱动映射

VERSION_TABLE 维护 ONNX release → IR version → opset version 的映射，ir_version 与 opset_version 不独立。详见[Opset版本机制与算子域](04-opset-versioning.md)。

## 生态定位

```
训练框架                    ONNX 生态                        推理引擎
┌─────────┐    ┌───────────────────────────────┐    ┌──────────────┐
│ PyTorch  │───→│                               │───→│ ONNX Runtime │
│         │    │  ┌─────────┐  ┌────────────┐  │    │              │
│TensorFlow│───→│  │ onnx/   │  │ optimizer/ │  │───→│ TensorRT     │
│         │    │  │ (核心)  │→ │ (优化器)   │  │    │              │
│ Keras   │───→│  └─────────┘  └────────────┘  │───→│ ncnn / MNN   │
│         │    │         │            │         │    │              │
│ Paddle  │───→│         ↓            ↓         │───→│ OpenVINO     │
│         │    │  ┌──────────────┐  ┌────────┐  │    │              │
│ JAX     │───→│  │onnxmltools/ │  │sklearn-│  │───→│ ...          │
│         │    │  │(传统ML转换) │  │onnx    │  │    │              │
└─────────┘    │  └──────────────┘  └────────┘  │    └──────────────┘
               │         │            │         │
               │         ↓            ↓         │
               │  ┌──────────────┐  ┌────────┐  │
               │  │tensorflow-   │  │onnx-   │  │
               │  │onnx (TF转换) │  │mlir    │  │
               │  └──────────────┘  └────────┘  │
               └───────────────────────────────┘
```

本知识包聚焦于 `onnx/` 核心项目（图中心），它是整个生态的基石：
- 定义 Protobuf IR 标准格式
- 提供 Python 构造/加载/保存 API
- 实现 C++ checker、shape_inference、version_converter
- 管理 OpSchema 算子注册表

周边项目（optimizer、onnxmltools、sklearn-onnx、tensorflow-onnx、onnx-mlir、onnx-tensorrt 等）均有独立的知识束覆盖。

## 关键反常识

1. **ONNX 不是推理引擎**：它不执行模型推理，只定义模型的表示格式。推理由 ONNX Runtime、TensorRT 等后端执行。
2. **Python 端没有 Graph 类**：Python 中操作计算图就是操作 Protobuf message 对象（GraphProto 的 repeated 字段）。
3. **check_model 通过 ≠ 模型可运行**：默认检查只验证结构合法性，full_check 才做形状推断。
4. **大模型不能用单文件 .onnx**：2 GiB protobuf 限制使得大模型必须使用外部数据格式。
5. **ir_version 不能随便设**：它与 opset_version 有绑定关系，必须通过 VERSION_TABLE 兼容。

## 关联概念

- [Protobuf IR：核心 Message 结构](01-protobuf-ir.md) — 深入 ModelProto/GraphProto/NodeProto 等 message 定义
- [张量类型系统](02-tensor-type-system.md) — 理解 DataType/TensorProto/TypeProto 的类型表示
- [计算图模型](03-computation-graph.md) — 理解 Graph/Node/Initializer 的拓扑关系
- [Opset版本机制与算子域](04-opset-versioning.md) — 理解 IR 版本和算子域的版本管理
