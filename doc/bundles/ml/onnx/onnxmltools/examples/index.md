---
type: example_index
title: "onnxmltools 示例索引"
description: "onnxmltools 示例文档导航"
generated: true
verified: grep
status: stable
stale_after: 2026-12-31
---

# onnxmltools 示例


实战示例

本目录包含 3 个完整的 onnxmltools 转换示例，覆盖最常用的树模型（XGBoost/LightGBM）和CoreML模型，从基础转换到高级选项逐步深入。

* [XGBoost模型转ONNX：从训练到推理验证](xgboost-conversion.md) — XGBoost分类器/回归器转换、Booster原生对象转换、initial_types类型声明、onnxruntime推理验证、预测一致性对比。对应概念：[整体架构](../concepts/00-overall-architecture.md)、[编译流水线](../concepts/02-conversion-pipeline.md)、[数据类型系统](../concepts/04-type-system.md)、[树模型转换范式](../concepts/05-tree-models.md)。
* [LightGBM Pipeline转换实战：zipmap/split/without_onnx_ml选项](lightgbm-pipeline.md) — LightGBM分类/回归/排序模型转换、zipmap选项对比（字典vs张量输出）、split大数精度控制（double累加）、without_onnx_ml纯ONNX转换（Hummingbird）、Booster自动包装。对应概念：[编译流水线](../concepts/02-conversion-pipeline.md)、[树模型转换范式](../concepts/05-tree-models.md)。
* [CoreML模型转换：从CoreML spec到ONNX](coreml-conversion.md) — CoreML GLM/TreeEnsemble/神经网络模型转换、metadata自动提取（author/license/description）、从.mlmodel文件加载转换、CoreML支持的15+40个算子一览。对应概念：[整体架构](../concepts/00-overall-architecture.md)、[树模型转换范式](../concepts/05-tree-models.md)、[Pipeline/元数据](../concepts/06-pipeline-metadata.md)。

```{toctree}
:maxdepth: 7

coreml-conversion
lightgbm-pipeline
xgboost-conversion
```
