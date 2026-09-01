---
type: concept_index
title: "onnx-tensorrt 核心概念索引"
description: "onnx-tensorrt 核心概念文档导航"
generated: true
verified: grep
status: stable
stale_after: 2026-12-31
---

# onnx-tensorrt 核心概念


概念文档

本目录包含 onnx-tensorrt 的 5 个核心概念文档，按学习路径排列：从整体架构到具体机制逐步深入。

## 架构总览

* [解析器整体架构：两遍式拓扑遍历+算子注册表的编译器架构](00-overall-architecture.md) — onnx-tensorrt 的编译器定位、六阶段解析管线、四层分发机制、两遍式设计（解析→子图分区）、核心数据流转。

## 核心机制篇

* [解析管线详解：importModel 六阶段、parseGraph 拓扑排序、parseNode 四层分发](01-parsing-pipeline.md) — importModel 十步流程详解、initializer 导入与外部作用域依赖补全、拓扑排序算法、静态检查与动态导入分离、output 标记与 TRT 元数据反序列化、input==output 的 Identity HACK。
* [算子注册与插件扩展：194 个内置算子、NodeImporter 函数类型、FallbackPluginImporter、插件覆盖机制](02-op-registration-plugin.md) — DEFINE_BUILTIN_OP_IMPORTER 静态自注册模式、NodeImporter/OpStaticErrorChecker 函数签名、四层分发优先级、FallbackPluginImporter 三版本 Creator 查找、plugin_namespace/version 三级查找、kENABLE_PLUGIN_OVERRIDE 插件覆盖、LocalFunction 局部函数递归、VC 插件追踪。
* [权重内存模型：ShapedWeights 非拥有语义、WeightsContext 内存管理、UINT8/DOUBLE/INT64 自动降级、BFloat16 手工位操作](03-weights-memory-model.md) — TensorOrWeights 变体三态设计、ShapedWeights 视图语义与生命周期陷阱、WeightsContext 所有权模型与类型转换、外部权重 mmap、BFloat16 round-to-even 舍入实现、临时权重分配规范。
* [错误处理与诊断：15 种 ErrorCode、异常+错误列表双轨、子图分区报告](04-error-diagnostics.md) — OnnxTrtException 异常模型、ONNXTRT_TRY/CATCH 边界宏设计、Status/IParserError 丰富上下文、ValueOrStatus 返回值模式、supportsModelV2 子图分区算法、DLA 能力验证模式、常见错误排查路径。

```{toctree}
:hidden:
:maxdepth: 7

00-overall-architecture
01-parsing-pipeline
02-op-registration-plugin
03-weights-memory-model
04-error-diagnostics
```
