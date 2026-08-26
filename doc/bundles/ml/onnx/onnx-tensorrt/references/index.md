---
type: reference_index
title: "onnx-tensorrt API 参考索引"
description: "onnx-tensorrt API 参考文档导航"
generated: true
verified: grep
status: stable
stale_after: 2026-12-31
---

# onnx-tensorrt API 参考


信源登记簿

本目录登记本知识包所有内容据以派生的 onnx-tensorrt 源码信源。所有概念文档和示例文档的 `sources` 字段均指向此目录下的信源登记条目。信源基于 onnx-tensorrt 源码（`external/libs/models/onnx/onnx-tensorrt/` 目录）的核心头文件和实现文件。

* [IParser 公共 API 与 ModelImporter 实现](parser-api.md) — `NvOnnxParser.h`（公共 API 版本 0.2.0）、`NvOnnxParser.cpp`（工厂函数实现）、`ModelImporter.hpp`/`ModelImporter.cpp`（IParser 具体实现类与 importModel 六阶段解析流程）：IParser 纯虚接口、parse/parseFromFile/分步 API、supportsModelV2 子图查询、OnnxParserFlag 5 个标志、IParserRefitter 权重重拟合、importModel 六阶段管线、parseGraph 拓扑排序、parseNode 四层分发。
* [核心工具类：ShapedWeights/OnnxAttrs/TensorOrWeights/WeightsContext/BFloat16/Status](core-utilities.md) — `ShapedWeights.hpp/cpp`（非拥有权重视图）、`OnnxAttrs.hpp/cpp`（节点属性访问）、`TensorOrWeights.hpp`（ITensor*/ShapedWeights 变体）、`WeightsContext.hpp`（权重内存所有权管理）、`bfloat16.hpp/cpp`（BF16 手工位操作）、`Status.hpp`（错误状态）、`errorHelpers.hpp`（异常宏）、`ImporterContext.hpp`（中央解析上下文）：TensorOrWeights 三态变体、OnnxAttrs 模板特化 get<T>()、WeightsContext mmap 外部权重、BFloat16 round-to-even 舍入、Status 15 种 ErrorCode。

```{toctree}
:hidden:
:maxdepth: 7

core-utilities
parser-api
```
