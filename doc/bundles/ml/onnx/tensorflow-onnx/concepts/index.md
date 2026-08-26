---
type: concept_index
title: "tensorflow-onnx 核心概念索引"
description: "tensorflow-onnx 核心概念文档导航"
generated: true
verified: grep
status: stable
stale_after: 2026-12-31
---

# tensorflow-onnx 核心概念


概念文档

本目录包含 tf2onnx 的 7 个核心概念文档，按学习路径排列：从架构总览到具体机制逐步深入。

## 架构总览

* [tf2onnx 整体架构：三阶段图转换流水线](00-overall-architecture.md) — "目标即 IR"设计哲学、Loader→Rewriter→Mapper→Optimizer 四阶段总览、包结构与懒加载机制、支持范围。

## 流水线与注册机制

* [转换流水线：Loader→Rewriter→Mapper→Optimizer](01-conversion-pipeline.md) — 从模型加载、Protobuf 1:1 转换、预处理重写、算子映射、后处理重写到图优化的完整调用链，三种源格式（TF/TFLite/TFJS）路径差异。
* [装饰器驱动的版本化算子注册表](02-versioned-opset-registry.md) — @tf_op 装饰器工作原理、version_N 方法约定、_OPSETS 三维索引、create_mapping 版本堆叠算法、DirectOp 模式、自定义算子扩展。

## 图操作与变换

* [图重写与模式匹配：子图重写先于单算子映射](03-graph-rewriting.md) — OpTypePattern 树形模式匹配、rewriter 函数签名、20+ 预处理重写器分类、late_rewriters 的 Target 条件激活、重写器排序原则。
* [内部 Graph API 设计：make_node / set_dtype / get_shape](04-graph-internal-api.md) — Node 类对 ONNX NodeProto 的封装、Graph 三大索引体系（nodes_by_name/output_to_node_name/output_to_consumers）、形状类型传播、子图管理、ExternalTensorStorage 大模型支持。

## 优化与适配

* [ONNX 图优化器：常量折叠/布局转换/冗余消除](05-optimizers.md) — 12 个内置优化器功能分类、迭代收敛策略、错误隔离机制（catch_errors+deepcopy 回滚）、三层常量折叠对比、与重写器的本质区别。
* [NHWC/NCHW 布局转换、数据类型系统与 Target 适配](06-data-layout-types.md) — TF NHWC 与 ONNX NCHW 布局差异、inputs_as_nchw 自动转置、TF dtype→ONNX dtype 映射、动态形状处理、opset 广播语义差异、rs5/rs6/caffe2/tensorrt/nhwc 平台适配。

```{toctree}
:hidden:
:maxdepth: 7

00-overall-architecture
01-conversion-pipeline
02-versioned-opset-registry
03-graph-rewriting
04-graph-internal-api
05-optimizers
06-data-layout-types
```
