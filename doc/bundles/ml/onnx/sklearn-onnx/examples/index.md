---
type: example_index
title: "sklearn-onnx 示例索引"
description: "sklearn-onnx 示例文档导航"
generated: true
verified: grep
status: stable
stale_after: 2026-12-31
---

# sklearn-onnx 示例


实战示例

本目录包含 3 个完整的 sklearn-onnx 使用示例，覆盖从基础分类器转换到复合 Pipeline、再到自定义转换器开发的渐进式学习路径。

* [分类器转ONNX：LogisticRegression 完整示例](classifier-conversion.md) — Iris 数据集训练 LogisticRegression，convert_sklearn 转换为 ONNX，onnxruntime 推理验证，zipmap 选项对比。对应概念：[整体架构](../concepts/00-overall-architecture.md)、[转换管线](../concepts/01-conversion-pipeline.md)、[Pipeline/FeatureUnion/ColumnTransformer处理](../concepts/05-pipeline-feature-union.md)。
* [Pipeline 完整转换：预处理+分类器串联](pipeline-conversion.md) — StandardScaler+PCA+LogisticRegression Pipeline 转换为单个 ONNX 模型（预处理内嵌），ColumnTransformer 异构特征 Pipeline（数值列+分类列），to_onnx 自动类型推断，intermediate=True 调试模式。对应概念：[转换管线](../concepts/01-conversion-pipeline.md)、[Pipeline/FeatureUnion/ColumnTransformer处理](../concepts/05-pipeline-feature-union.md)、[Topology IR](../concepts/02-topology-ir.md)。
* [自定义转换器开发：两种模式对比](custom-converter.md) — 实现 ThresholdApplier 自定义估计器的 ONNX 导出，对比传统三件套（parser+shape_calculator+converter 手写）和 OnnxOperatorMixin 代数API（一个 to_onnx_operator 方法搞定）两种模式，Pipeline 中嵌入自定义转换器，常见错误调试。对应概念：[转换器注册](../concepts/03-converter-registration.md)、[OnnxOperator代数API](../concepts/04-onnx-operator-algebra.md)、[整体架构](../concepts/00-overall-architecture.md)。

```{toctree}
:hidden:

classifier-conversion
custom-converter
pipeline-conversion
```
