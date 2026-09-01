---
type: concept_index
title: "onnxmltools 核心概念索引"
description: "onnxmltools 核心概念文档导航"
generated: true
verified: grep
status: stable
stale_after: 2026-12-31
---

# onnxmltools 核心概念


概念文档

本目录包含 onnxmltools 的 7 个核心概念文档，按学习路径排列：从架构总览到核心机制，再到具体范式和工具。

## 架构总览

* [onnxmltools 整体架构：9入口6自有IR+3委托的非对称转换工具](00-overall-architecture.md) — 非对称架构总览：9个convert入口中6个走自有Topology IR、3个委托外部转换器，ONNX-ML传统ML算子集是IR实际能力边界，RawModelContainer多态封装。

## 核心机制

* [Topology IR：三层核心类、C风格唯一名称、raw_name隐藏](01-topology-ir.md) — IR核心数据结构：Topology/Scope/Operator/Variable四核心类，C风格唯一名称生成算法，raw_name→onnx_name多对一隐藏机制模拟SSA，is_fed数据驱动拓扑遍历。
* [编译流水线五阶段：createTopology→compile→convert_topology→make_model](02-conversion-pipeline.md) — 完整转换流程：parse创建IR→compile五阶段优化（剪枝→identity消重→形状补全→类型推断→结构校验）→convert_topology拓扑遍历调度→make_model_ex opset合并与IR版本映射。
* [转换器注册与分发：双注册池、导入副作用、委托路径](03-converter-registration.md) — 算子注册机制：双注册池（converter/shape_calculator）设计、导入副作用注册模式、字符串key弱类型风险、custom参数不对称风险、converter与shape_calculator配对约束。
* [数据类型系统：四层DataType、TensorType维度规格、三向类型猜测](04-type-system.md) — 类型体系：DataType四层层次（标量/张量/序列/字典）、15种TensorType子类、三类维度规格（int固定/str符号/None未知）、三向类型猜测函数族（proto/proto_str/numpy）、denotation语义标注。

## 范式与工具

* [树模型转换范式：LightGBM/XGBoost/CoreML算子集与属性模板](05-tree-models.md) — 树模型统一范式：TreeEnsembleClassifier/Regressor属性对模板、平行数组节点编码、add_node函数、三框架共性与差异、zipmap/split/without_onnx_ml后处理选项。
* [Pipeline转换、元数据传播与校验工具](06-pipeline-metadata.md) — 复合模型处理：SparkML/CoreML Pipeline转换、CoreML元数据自动提取（author/license/description）、模型I/O工具、命名合规校验、形状计算器校验工具。

```{toctree}
:hidden:
:maxdepth: 7

00-overall-architecture
01-topology-ir
02-conversion-pipeline
03-converter-registration
04-type-system
05-tree-models
06-pipeline-metadata
```
