---
type: bundle
title: ONNX 核心规范
okf_version: "0.2"
---


# ONNX 核心知识库

本知识包是开放神经网络交换格式 [ONNX](https://onnx.ai/)（Apache-2.0 许可证）的系统化中文源码教程，基于 ONNX 源码（`external/libs/models/onnx/onnx/` 目录）深度阅读生成，覆盖从 Protobuf IR 定义到 C++ 内部表示、从 Python Helper API 到形状推断/检查器/序列化/版本转换的完整知识体系。所有内容均溯源至 ONNX Python/C++ 源码核心模块，遵循 [OKF v0.2 规范](concepts/00-overall-architecture.md)。

## 架构基础篇（concepts/）

* [ONNX 整体架构与生态定位](concepts/00-overall-architecture.md) — 三层架构（Protobuf标准/C++IR/Python Helper）、五个核心架构洞察（Protobuf唯一事实源/OpSchema注册表驱动/Checker C++验证/注册表序列化/表驱动版本管理）、ONNX在AI模型交换生态中的定位。
* [Protobuf IR：核心 Message 结构](concepts/01-protobuf-ir.md) — ModelProto/GraphProto/NodeProto/AttributeProto/ValueInfoProto/FunctionProto 完整字段定义、字段号、属性类型枚举（14种）、引用属性机制、IR_VERSION 演进（1→14）。
* [张量类型系统](concepts/02-tensor-type-system.md) — DataType枚举26种数据类型、TensorProto七种存储字段、TypeProto六种类型变体（tensor/sequence/map/optional/sparse/opaque）、Dimension oneof三态表示、亚字节打包规则。
* [计算图模型](concepts/03-computation-graph.md) — 字符串名字连接机制、initializer与input的区别（IR≥4分离）、value_info的作用、C++ IR双向循环链表哨兵模式、use-def链、replaceAllUsesWith图变换。
* [Opset版本机制与算子域](concepts/04-opset-versioning.md) — VERSION_TABLE表驱动映射、四个算子域（标准/ML/训练/预览）、NormalizeDomain规范化、make_model vs make_model_gen_version、find_min_ir_version_for查表。

## 核心机制篇（concepts/）

* [算子定义与注册机制 OpSchema](concepts/05-operator-schema.md) — OpSchema链式API、FormalParameterOption（Single/Optional/Variadic）、ONNX_OPERATOR_SET_SCHEMA宏静态注册、OpSchemaRegistry单例、TypeConstraint类型约束、FunctionBody函数体机制。
* [形状推断实现](concepts/06-shape-inference.md) — InferenceContext抽象接口、InferenceFunction/DataPropagationFunction注册、ShapeInferenceOptions（check_type/error_mode/data_prop）、kMaxMaterializedRank=1024安全限制、Python infer_shapes()。
* [模型检查器 Checker](concepts/07-model-checker.md) — Python→C++全委托架构、check_model基础验证规则、full_check模式（形状推断+类型检查）、CheckerContext/LexicalScopeContext、函数循环检测、外部数据路径安全验证。
* [序列化/反序列化与外部数据](concepts/08-serialization.md) — _Registry注册表架构、四种序列化器（protobuf/textproto/json/onnxtxt）、2GiB protobuf硬限制、外部数据三层安全防御、load/save API、numpy_helper.to_array。
* [Python Helper API 详解](concepts/09-python-helpers.md) — make_node kwargs自动转属性、make_tensor raw_data压缩与亚字节打包、make_attribute自动类型推断、make_tensor_value_info shape三态处理、make_function函数构造。

## 高级功能篇（concepts/）

* [图组合 Compose 与子图处理](concepts/10-graph-compose.md) — merge_models前提条件、check_overlapping_names冲突检测、add_prefix前缀策略、子图属性递归处理、rename_functions。
* [文本解析器与打印器](concepts/11-parser-printer.md) — onnxtxt文本格式、parse_model/parse_graph/parse_function/parse_node、to_text打印、TextualSerializer实验性警告。
* [C++ 核心 IR](concepts/12-cpp-core-ir.md) — Graph/Node/Value三核心结构体、双向循环链表哨兵模式、CRTP Attributes类型安全访问、Value use-def链与replaceAllUsesWith、initializer_node_ Param节点、used_names_O(1)查重。
* [版本转换与函数内联](concepts/13-version-converter-inliner.md) — convert_version adapter机制、OpSchema函数体vs模型局部函数、inline_local_functions递归内联、inline_selected_functions选择性内联、函数调用循环检测。

## 实战示例（examples/）

* [从零构建线性回归模型](examples/build-linear-regression.md) — make_tensor_value_info→make_node→make_graph→make_model→save_model完整可运行代码，含动态形状说明。
* [模型加载、检查与形状推断](examples/load-check-model.md) — load_model→check_model→infer_shapes→check_model(full_check=True)完整验证流程、模型结构统计、权重读取。
* [图遍历与变换实战](examples/graph-transformation.md) — 遍历节点/查找算子/修改属性/添加删除节点/边重连/操作initializer/深拷贝保护/形状推断后访问value_info。
* [自定义算子注册与使用示例](examples/custom-operator.md) — 自定义domain构建op节点、opset_import自定义域、checker对自定义op的行为、FunctionProto局部函数与内联。

## 信源登记簿（references/）

* [onnx.proto：Protobuf IR 核心 Message 定义](references/onnx-proto.md) — onnx.proto中全部核心message（ModelProto/GraphProto/NodeProto/AttributeProto/TensorProto/ValueInfoProto/TypeProto/FunctionProto/OperatorSetIdProto/SparseTensorProto）的字段、字段号与嵌套关系。
* [helper.py：Python Helper 核心 API](references/helper-api.md) — make_node/make_graph/make_model/make_tensor/make_attribute/make_function等API签名与行为、VERSION_TABLE版本映射表、TENSOR_TYPE_MAP、find_min_ir_version_for。
* [checker.py/checker.cc/checker.h：模型检查器实现](references/checker.md) — C++核心验证逻辑、Python委托机制、full_check形状推断集成、MAXIMUM_PROTOBUF、CheckerContext/LexicalScopeContext、路径安全verify_path_containment。
* [serialization.py/external_data_helper.py/numpy_helper.py：序列化与外部数据](references/serialization.md) — _Registry注册表、四种序列化器、2GiB限制、外部数据三层安全防御、numpy_helper张量转换、__repr__覆写。
* [defs/schema.h/cc：OpSchema算子注册机制](references/op-schema.md) — OpSchema链式API、FormalParameterOption枚举、ONNX_OPERATOR_SET_SCHEMA宏、OpSchemaRegistry单例、TypeConstraint、FunctionBody、四个算子域常量。
* [common/ir.h：C++ IR核心类](references/cpp-ir.md) — Graph/Node/Value结构体、双向循环链表哨兵、CRTP Attributes、Dimension三态、AttributeKind、Use结构体、initializer_node_、used_names_、subgraph_bearing_nodes_。
* [shape_inference.h/cc/shape_inference.py：形状推断实现](references/shape-inference.md) — InferenceContext接口、InferenceFunction/DataPropagationFunction、ShapeInferenceOptions、kMaxMaterializedRank、Python infer_shapes封装。
* [compose.py/parser.py/printer.py/version_converter.py/inliner.py：图组合/解析/打印/转换/内联](references/compose-parser-printer.md) — merge_models/add_prefix、parse_*四函数、to_text、convert_version、inline_local_functions/inline_selected_functions。

## 信任与生命周期说明

* **status 判定依据**：全部 26 个内容文档（14 个概念 + 4 个示例 + 8 个信源登记）均 `status: stable`。内容基于对 ONNX 源码（`external/libs/models/onnx/onnx/` 目录）核心模块的逐文件阅读与事实提取（83 条源码事实 F-001~F-083），经 seven-concepts 方法论 R→I→E 三阶段流程生成。
* **stale_after 解释**：统一设置为 `2027-08-22`。ONNX 核心架构（Protobuf IR三层/OpSchema注册表/Checker C++验证/注册表序列化/表驱动版本）自 1.x 以来保持稳定，新算子和工具不断添加但核心设计不变；该日期作为针对未来大版本（如 IR_VERSION 15+ 引入breaking change）的保守重新评估节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻；`verified.at` 记录 V 阶段对抗审查核验事件，两者分离、可追溯。

本知识包共收录 26 个内容文档（14 个概念 + 4 个示例 + 8 个信源登记），另含 3 个子目录 index.md 与根 index.md、log.md。
