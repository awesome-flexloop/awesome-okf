---
type: concept_index
title: "onnx 核心概念索引"
description: "onnx 核心概念文档导航"
generated: true
verified: grep
status: stable
stale_after: 2026-12-31
---

# onnx 核心概念


概念文档

本目录包含 ONNX 核心项目的 14 个核心概念文档，按学习路径排列：从架构总览到具体机制逐步深入。

## 架构基础篇

* [ONNX 整体架构与生态定位](00-overall-architecture.md) — 三层架构（Protobuf标准/C++IR/Python Helper）、五个核心架构洞察（Protobuf唯一事实源/OpSchema注册表驱动/Checker C++验证/注册表序列化/表驱动版本管理）、ONNX在AI模型交换生态中的定位。
* [Protobuf IR：核心 Message 结构](01-protobuf-ir.md) — ModelProto/GraphProto/NodeProto/AttributeProto/ValueInfoProto/FunctionProto/OperatorSetIdProto 的完整字段定义、字段号、必选/可选字段、属性类型枚举、引用属性机制、IR_VERSION演进历程。
* [张量类型系统](02-tensor-type-system.md) — DataType枚举26种数据类型、TensorProto七种存储字段、TypeProto六种类型变体（tensor/sequence/map/optional/sparse/opaque）、TensorShapeProto.Dimension的oneof三态表示、亚字节打包规则、SparseTensorProto结构、外部数据字段。
* [计算图模型](03-computation-graph.md) — 字符串名字连接机制、initializer与input的区别、value_info的作用、C++ IR双向循环链表哨兵模式、Dimension三态、used_names_O(1)查重、Value replaceAllUsesWith图变换、Use结构体。
* [Opset版本机制与算子域](04-opset-versioning.md) — IR_VERSION演进(1-14)、VERSION_TABLE表驱动映射、四个算子域（标准/ML/训练/预览）、NormalizeDomain规范化、make_model vs make_model_gen_version版本策略、find_min_ir_version_for查表、OperatorStatus。

## 核心机制篇

* [算子定义与注册机制 OpSchema](05-operator-schema.md) — OpSchema链式API、FormalParameterOption（Single/Optional/Variadic）、ONNX_OPERATOR_SET_SCHEMA宏、OpSchemaRegistry单例注册表、TypeConstraint类型约束、FunctionBody/ContextDependentFunctionBodyBuilder函数体机制。
* [形状推断实现](06-shape-inference.md) — InferenceContext抽象接口、InferenceFunction/DataPropagationFunction注册、ShapeInferenceOptions（check_type/error_mode/data_prop）、kMaxMaterializedRank=1024安全限制、Python infer_shapes()用法、子图递归推断。
* [模型检查器 Checker](07-model-checker.md) — Python→C++全委托架构、check_model基础验证规则、full_check形状推断+类型检查、CheckerContext/LexicalScopeContext、局部函数检查与循环检测、外部数据路径安全（verify_path_containment+禁止..遍历）、MAXIMUM_PROTOBUF 2GiB限制。
* [序列化/反序列化与外部数据](08-serialization.md) — _Registry注册表架构、四种序列化器（protobuf/textproto/json/onnxtxt）、2GiB protobuf硬限制、外部数据机制（external_data/data_location）、三层安全防御（白名单/类型验证/文件大小检查）、load_model/save_model API、numpy_helper.to_array张量转换。
* [Python Helper API 详解](09-python-helpers.md) — make_node kwargs自动转属性、make_graph/make_model默认版本设置、make_tensor raw_data压缩与亚字节打包、make_attribute自动类型推断、make_attribute_ref引用属性、make_tensor_value_info的shape三态处理、make_function函数构造、tensor_dtype_to_field映射。

## 高级功能篇

* [图组合 Compose 与子图处理](10-graph-compose.md) — merge_models前提条件（ir_version/opset/metadata/functions兼容）、check_overlapping_names冲突检测、add_prefix_graph前缀策略（可选择范围+空名跳过+rename_edges处理）、子图属性递归处理、add_prefix rename_functions支持。
* [文本解析器与打印器](11-parser-printer.md) — onnxtxt文本格式、parse_model/parse_graph/parse_function/parse_node四个解析函数、to_text打印、TextualSerializer实验性警告、ParseError错误处理。
* [C++ 核心 IR](12-cpp-core-ir.md) — Graph/Node/Value三核心结构体所有权模型、Node双向循环链表哨兵模式、CRTP Attributes类型安全访问、Value use-def链与replaceAllUsesWith、Use双向链表、Dimension三态、AttributeKind 12种、initializer_node_ Param节点、used_names_哈希表、subgraph_bearing_nodes_索引。
* [版本转换与函数内联](13-version-converter-inliner.md) — convert_version跨版本adapter机制、OpSchema函数体vs模型局部函数、inline_local_functions递归内联、inline_selected_functions选择性内联（白名单/黑名单模式）、inline_schema_functions控制、函数调用循环检测。

```{toctree}
:hidden:
:maxdepth: 7

00-overall-architecture
01-protobuf-ir
02-tensor-type-system
03-computation-graph
04-opset-versioning
05-operator-schema
06-shape-inference
07-model-checker
08-serialization
09-python-helpers
10-graph-compose
11-parser-printer
12-cpp-core-ir
13-version-converter-inliner
```
