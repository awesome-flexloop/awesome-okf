---
type: example_index
title: "onnx-tensorrt 示例索引"
description: "onnx-tensorrt 示例文档导航"
generated: true
verified: grep
status: stable
stale_after: 2026-12-31
---

# onnx-tensorrt 示例


实战示例

本目录包含 onnx-tensorrt 的实战示例，从基础模型解析到自定义插件扩展，覆盖常见使用场景。

* [使用解析器加载 ONNX 模型到 TensorRT 网络：构建 engine 与推理](parse-onnx-model.md) — 完整的 ONNX 模型加载流程：创建 Logger→Builder→Network→Parser→解析模型→配置 Builder→构建 Engine→反序列化→执行推理，含错误处理和动态形状配置。对应概念：[解析管线详解](../concepts/01-parsing-pipeline.md)、[错误处理与诊断](../concepts/04-error-diagnostics.md)、[解析器整体架构](../concepts/00-overall-architecture.md)。
* [自定义插件处理不支持的算子](custom-plugin.md) — 为不支持的 ONNX 算子编写 TensorRT 自定义插件、注册 IPluginCreator、通过 FallbackPluginImporter 自动导入、构建版本兼容引擎。对应概念：[算子注册与插件扩展](../concepts/02-op-registration-plugin.md)、[错误处理与诊断](../concepts/04-error-diagnostics.md)、[权重内存模型](../concepts/03-weights-memory-model.md)。

```{toctree}
:hidden:

custom-plugin
parse-onnx-model
```
