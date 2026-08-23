---
type: log
title: onnx 变更日志
description: 记录文档生成与更新历史
generated: true
verified: grep
status: stable
stale_after: 2026-12-31
---

# Bundle Update Log

## 2026-08-22

* **Creation**: 建立 ONNX 核心项目知识包脚手架（concepts/examples/references 三目录），遵循 OKF v0.2 规范。
* **Add**: R阶段完成——深度阅读 ONNX 源码（`external/libs/models/onnx/onnx/`）核心模块：`onnx.proto`（Protobuf IR定义，ModelProto/GraphProto/NodeProto/AttributeProto/TensorProto/TypeProto/FunctionProto等10个核心message，26种DataType，6种类型变体）、`onnx/helper.py`（make_node/make_graph/make_model/make_tensor/make_attribute等构造API，VERSION_TABLE版本映射）、`onnx/checker.py`/`checker.cc`/`checker.h`（C++模型检查器，Python全委托，full_check形状推断，路径安全）、`onnx/__init__.py`/`serialization.py`/`external_data_helper.py`/`numpy_helper.py`（_Registry注册表，四种序列化器，外部数据三层安全，numpy转换）、`onnx/defs/schema.h`/`schema.cc`（OpSchema链式API，ONNX_OPERATOR_SET_SCHEMA宏，OpSchemaRegistry单例，四个算子域，TypeConstraint，FunctionBody）、`onnx/common/ir.h`（C++ IR三核心类Graph/Node/Value，双向循环链表哨兵，CRTP Attributes，use-def链，used_names_）、`onnx/defs/shape_inference.h`/`shape_inference.cc`/`shape_inference.py`（InferenceContext接口，InferenceFunction/DataPropagationFunction，ShapeInferenceOptions）、`onnx/compose.py`/`parser.py`/`printer.py`/`version_converter.py`/`inliner.py`（merge_models/add_prefix图组合，parser/printer文本格式，版本转换，函数内联），提取83条源码事实（F-001~F-083），覆盖Protobuf IR/Python Helper/Checker/序列化/OpSchema/C++ IR/形状推断/Compose/Parser/Printer/版本转换/内联/常量/外部数据等全栈模块。
* **Add**: I阶段完成——提炼5个核心架构洞察（I-01 Protobuf唯一事实源三层架构/I-02 OpSchema注册表驱动算子生态/I-03 Checker C++多层验证体系/I-04 注册表架构序列化与2GiB限制/I-05 表驱动版本管理VERSION_TABLE），设计知识地图（references 8篇信源→concepts 14篇分三批架构基础5篇+核心机制5篇+高级功能4篇→examples 4篇实战）。
* **Add**: E阶段完成——references/下8个信源登记（onnx-proto/helper-api/checker/serialization/op-schema/cpp-ir/shape-inference/compose-parser-printer），concepts/下14个概念文档（00-overall-architecture/01-protobuf-ir/02-tensor-type-system/03-computation-graph/04-opset-versioning/05-operator-schema/06-shape-inference/07-model-checker/08-serialization/09-python-helpers/10-graph-compose/11-parser-printer/12-cpp-core-ir/13-version-converter-inliner），examples/下4个实战示例（build-linear-regression/load-check-model/graph-transformation/custom-operator），加上3个子目录index.md和根index.md、log.md。
