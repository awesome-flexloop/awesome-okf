---
type: reference_index
title: "onnx API 参考索引"
description: "onnx API 参考文档导航"
generated: true
verified: grep
status: stable
stale_after: 2026-12-31
---

# onnx API 参考


信源登记簿

本目录登记本知识包所有内容据以派生的 ONNX 源码信源。所有概念文档和示例文档的 `sources` 字段均指向此目录下的信源登记条目。信源基于 ONNX 源码（`external/libs/models/onnx/onnx/` 目录）的核心文件。

* [onnx.proto：Protobuf IR 核心 Message 定义](onnx-proto.md) — `onnx/onnx.proto`：ModelProto/GraphProto/NodeProto/AttributeProto/TensorProto/ValueInfoProto/TypeProto/FunctionProto/OperatorSetIdProto/SparseTensorProto 全部 message 字段、字段号、DataType 26种枚举、TypeProto 六种类型变体、Dimension oneof、IR_VERSION=14。
* [helper.py：Python Helper 核心 API](helper-api.md) — `onnx/helper.py`、`onnx/_mapping.py`：make_node/make_graph/make_model/make_model_gen_version/make_tensor/make_attribute/make_attribute_ref/make_tensor_value_info/make_function/make_operatorsetid、tensor_dtype_to_field 映射、VERSION_TABLE 版本映射表、TENSOR_TYPE_MAP、find_min_ir_version_for 查表。
* [checker.py/checker.cc/checker.h：模型检查器实现](checker.md) — `onnx/checker.cc`、`onnx/checker.py`、`onnx/checker.h`：check_model 验证规则、Python 全委托 C++、full_check 形状推断、MAXIMUM_PROTOBUF 2GiB 限制、CheckerContext/LexicalScopeContext、外部数据路径安全 verify_path_containment。
* [serialization.py/external_data_helper.py/numpy_helper.py：序列化与外部数据](serialization.md) — `onnx/__init__.py`、`onnx/serialization.py`、`onnx/external_data_helper.py`、`onnx/numpy_helper.py`：_Registry 注册表、四种序列化器（protobuf/textproto/json/onnxtxt）、load_model/save_model API、外部数据三层安全防御、numpy_helper.to_array 转换、__repr__ 覆写。
* [defs/schema.h/cc：OpSchema 算子注册机制](op-schema.md) — `onnx/defs/schema.h`、`onnx/defs/schema.cc`、`onnx/common/constants.h`：OpSchema 链式 API、FormalParameterOption（Single/Optional/Variadic）、ONNX_OPERATOR_SET_SCHEMA 宏、OpSchemaRegistry 单例、TypeConstraint 类型约束、FunctionBody 函数体、四个算子域（标准/ML/训练/预览）、NormalizeDomain。
* [common/ir.h：C++ IR 核心类](cpp-ir.md) — `onnx/common/ir.h`：Graph/Node/Value 三核心结构体、Node 双向循环链表（哨兵节点）、CRTP Attributes、Value replaceAllUsesWith、Dimension 三态、AttributeKind 12种、initializer_node_、used_names_ O(1) 查重、subgraph_bearing_nodes_、Use 结构体。
* [shape_inference.h/cc/shape_inference.py：形状推断实现](shape-inference.md) — `onnx/defs/shape_inference.h`、`onnx/defs/shape_inference.cc`、`onnx/shape_inference.py`：InferenceContext 抽象接口、InferenceFunction/DataPropagationFunction、ShapeInferenceOptions（check_type/error_mode/data_prop）、kMaxMaterializedRank=1024、Python infer_shapes() 封装。
* [compose.py/parser.py/printer.py/version_converter.py/inliner.py：图组合、解析打印、版本转换与内联](compose-parser-printer.md) — `onnx/compose.py`、`onnx/parser.py`/`parser.cc`、`onnx/printer.py`、`onnx/version_converter.py`、`onnx/inliner.py`：merge_models 前提条件、add_prefix 前缀策略与子图递归、parse_model/parse_graph/parse_function/parse_node、to_text 打印、convert_version 跨版本转换、inline_local_functions 递归内联、inline_selected_functions 选择性内联。

```{toctree}
:maxdepth: 7

checker
compose-parser-printer
cpp-ir
helper-api
onnx-proto
op-schema
serialization
shape-inference
```
