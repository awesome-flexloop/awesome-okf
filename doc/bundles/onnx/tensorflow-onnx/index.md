---
type: bundle
title: tf2onnx TensorFlow 转换器
okf_version: "0.2"
---


# tensorflow-onnx (tf2onnx) 知识库

本知识包是 TensorFlow 到 ONNX 模型转换器 [tensorflow-onnx (tf2onnx)](https://github.com/onnx/tensorflow-onnx)（Apache-2.0 许可证）的系统化中文源码教程，基于 tf2onnx 源码深度阅读生成，覆盖从整体架构到转换流水线、算子注册、图重写、优化器、数据布局适配的完整知识体系。所有内容均溯源至 tf2onnx Python 源码核心模块（convert.py/tfonnx.py/handler.py/graph.py/graph_matcher.py/optimizer/onnx_opset/ 等），遵循 [OKF v0.2 规范](concepts/00-overall-architecture.md)。

## 架构总览篇（concepts/）

* [tf2onnx 整体架构：三阶段图转换流水线](concepts/00-overall-architecture.md) — "目标即 IR"设计哲学、Loader→Rewriter→Mapper→Optimizer 四阶段总览、包结构与懒加载机制、支持范围与版本要求。

## 核心机制篇（concepts/）

* [转换流水线：Loader→Rewriter→Mapper→Optimizer](concepts/01-conversion-pipeline.md) — 从模型加载、Protobuf 1:1 转换、预处理重写、算子映射、后处理重写到图优化的完整六阶段调用链，三阶段形状推断，TFLite/TFJS 路径差异。
* [装饰器驱动的版本化算子注册表](concepts/02-versioned-opset-registry.md) — @tf_op 装饰器工作原理、version_N 类方法约定、_OPSETS 三维索引（domain→opset→op_map）、create_mapping 版本堆叠算法、DirectOp 零成本映射、自定义算子扩展新旧 API。
* [图重写与模式匹配：子图重写先于单算子映射](concepts/03-graph-rewriting.md) — OpTypePattern 树形模式匹配、rewriter 函数签名约定、20+ 预处理重写器分类（常量折叠/融合拆分/RNN识别/卷积/布局）、late_rewriters Target 条件激活、子图递归重写。
* [内部 Graph API 设计：make_node / set_dtype / get_shape](concepts/04-graph-internal-api.md) — Node 类对 ONNX NodeProto 的封装、Graph 三大索引体系（nodes_by_name/output_to_node_name/output_to_consumers）、形状类型传播 API、子图管理（contained_graphs）、ExternalTensorStorage 大模型外部存储、Identity 输出保护。

## 功能模块篇（concepts/）

* [ONNX 图优化器：常量折叠/布局转换/冗余消除](concepts/05-optimizers.md) — 12 个内置优化器分类（Transpose/ConstFold/Identity/MergeDuplicated/Reshape/BackToBack 等）、迭代收敛策略、catch_errors 错误隔离机制（deepcopy+回滚）、三层常量折叠对比、自定义优化器。
* [NHWC/NCHW 布局转换、数据类型系统与 Target 适配](concepts/06-data-layout-types.md) — TF NHWC vs ONNX NCHW 布局差异、inputs_as_nchw 自动 Transpose 插入、TF dtype→ONNX dtype 映射、动态形状处理（shape_override/-1）、opset 广播语义差异、rs5/rs6/tensorrt/nhwc 平台适配。

## 实战示例（examples/）

* [Keras 模型转 ONNX](examples/keras-conversion.md) — Sequential 和 Functional API 模型转换、inputs_as_nchw NCHW 布局转换、opset 选择、TF vs ONNX 推理结果一致性验证。
* [SavedModel 转换](examples/savedmodel-conversion.md) — Python API 和命令行两种方式、签名选择、shape_override 固定/动态形状、大模型外部存储、--custom-ops 标记自定义算子、Target 平台优化。
* [自定义算子映射](examples/custom-op-mapping.md) — @tf_op 装饰器新 API、custom_op_handlers 旧 API、命令行标记未知算子、自定义子图重写器、Graph/Node API 速查、常见错误排查。

## 信源登记簿（references/）

* [转换入口 API：from_keras / from_saved_model / from_function / 命令行](references/convert-entry.md) — `convert.py` 五个核心转换函数、_convert_common 共用流程、_Lazy 代理模式、命令行 6 种输入格式、形状内联指定。
* [图表示 Graph 类与重写机制（Rewriter / GraphMatcher）](references/graph-rewriter.md) — `graph.py` Node/Graph/ExternalTensorStorage 类、`graph_matcher.py` OpTypePattern/MatchResult、`tfonnx.py` run_rewriters 框架与重写器列表。
* [算子版本化注册表：@tf_op 装饰器与 onnx_opset 目录](references/opset-mapping.md) — `handler.py` tf_op 装饰器与 create_mapping 算法、`onnx_opset/` 13 个分类文件、tensorflow_onnx_mapping 遍历映射。

## 信任与生命周期说明

* **status 判定依据**：全部 13 个内容文档（7 个概念 + 3 个示例 + 3 个信源登记）均 `status: stable`。内容基于对 tf2onnx 源码（`tf2onnx/` 目录）核心模块的逐文件阅读与事实提取（44 条源码事实 F-001~F-044），经 seven-concepts 方法论 R→I→E 三阶段流程生成。
* **stale_after 解释**：统一设置为 `2027-12-31`。tf2onnx 核心架构（三阶段流水线/@tf_op 装饰器注册/Graph API/优化器体系）自 1.x 以来保持稳定，新算子和 opset 版本持续添加但核心设计不变；该日期作为针对未来大版本的保守重新评估节点。
* **核验链路**：代码示例基于 tf2onnx 公开 API（from_keras/from_saved_model/from_function/@tf_op 装饰器），API 签名与源码一致。

本知识包共收录 13 个内容文档（7 个概念 + 3 个示例 + 3 个信源登记），另含 3 个子目录 index.md 与根 index.md、log.md。
