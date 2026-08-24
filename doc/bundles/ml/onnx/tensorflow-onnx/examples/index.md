---
type: example_index
title: "tensorflow-onnx 示例索引"
description: "tensorflow-onnx 示例文档导航"
generated: true
verified: grep
status: stable
stale_after: 2026-12-31
---

# tensorflow-onnx 示例


实战示例

本目录包含 3 个完整的 tf2onnx 使用示例，覆盖最常见的转换场景和自定义扩展。

* [Keras 模型转 ONNX](keras-conversion.md) — 从内存中的 `tf.keras.Model` 直接转换：Sequential 和 Functional API 两种建模方式、inputs_as_nchw 自动布局转换、opset 选择、TF vs ONNX 推理结果对比验证。对应概念：[tf2onnx 整体架构](../concepts/00-overall-architecture.md)、[转换流水线详解](../concepts/01-conversion-pipeline.md)、[数据布局与类型系统](../concepts/06-data-layout-types.md)。
* [SavedModel 转换](savedmodel-conversion.md) — 将已保存的 SavedModel 目录转换为 ONNX：Python API 和命令行两种方式、签名选择（signature_def）、shape_override 形状指定与动态维度（-1）、大模型外部存储、Target 平台优化、Checkpoint 转换。对应概念：[转换入口 API](../references/convert-entry.md)、[转换流水线详解](../concepts/01-conversion-pipeline.md)、[数据布局与类型系统](../concepts/06-data-layout-types.md)。
* [自定义算子映射](custom-op-mapping.md) — 为 tf2onnx 不支持的 TF 算子编写自定义转换器：@tf_op 装饰器新 API（推荐，支持多 opset 版本）、custom_op_handlers 旧 API 兼容、命令行 --custom-ops 标记未知算子、自定义子图重写器（custom_rewriter）、Graph/Node API 速查与常见错误排查。对应概念：[装饰器驱动的版本化算子注册表](../concepts/02-versioned-opset-registry.md)、[内部 Graph API 设计](../concepts/04-graph-internal-api.md)、[图重写与模式匹配](../concepts/03-graph-rewriting.md)。

```{toctree}
:hidden:

custom-op-mapping
keras-conversion
savedmodel-conversion
```
