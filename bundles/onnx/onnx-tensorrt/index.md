---
type: bundle
title: ONNX-TensorRT 解析器
okf_version: "0.2"
---


# ONNX-TensorRT 知识库

本知识包是 NVIDIA TensorRT 的 ONNX 解析器 [onnx-tensorrt](https://github.com/onnx/onnx-tensorrt)（Apache-2.0 许可证）的系统化中文源码教程，基于 onnx-tensorrt 源码（`external/libs/models/onnx/onnx-tensorrt/` 目录，对应 TensorRT 11.2 版本）深度阅读生成，覆盖从整体编译器架构到解析管线、算子注册、权重管理、错误诊断的完整知识体系。所有内容均溯源至 onnx-tensorrt C++ 源码核心类（IParser/ModelImporter/ImporterContext/ShapedWeights/WeightsContext 等），遵循 OKF v0.2 规范。

## 架构总览（concepts/）

* [解析器整体架构：两遍式拓扑遍历+算子注册表的编译器架构](concepts/00-overall-architecture.md) — 编译器定位（而非格式转换器）、六阶段解析管线、四层分发机制、两遍式设计（解析→子图分区）、核心数据流转、TensorOrWeights 变体设计。

## 核心机制篇（concepts/）

* [解析管线详解：importModel 六阶段、parseGraph 拓扑排序、parseNode 四层分发](concepts/01-parsing-pipeline.md) — importModel 十步流程、initializer 导入、子图外部作用域依赖补全、拓扑排序算法、静态检查与动态导入分离、parseNode 七层逻辑、output 标记与 TRT 元数据反序列化、input==output 的 Identity HACK、分步 API 执行路径。
* [算子注册与插件扩展：194个内置算子、NodeImporter 函数类型、FallbackPluginImporter、插件覆盖机制](concepts/02-op-registration-plugin.md) — DEFINE_BUILTIN_OP_IMPORTER 静态自注册模式、NodeImporter/OpStaticErrorChecker 函数签名、四层分发优先级、FallbackPluginImporter 三版本 Creator 查找、plugin_namespace/version 三级查找、kENABLE_PLUGIN_OVERRIDE 插件覆盖、LocalFunction 局部函数递归、VC 插件追踪全流程。
* [权重内存模型：ShapedWeights 非拥有语义、WeightsContext 内存管理、UINT8/DOUBLE/INT64 自动降级、BFloat16 手工位操作](concepts/03-weights-memory-model.md) — TensorOrWeights 三态变体、ShapedWeights 视图语义与生命周期陷阱、WeightsContext 所有权模型与类型转换、外部权重 mmap、BFloat16 round-to-even 舍入、临时权重分配规范、Refittable 权重与 IParserRefitter。
* [错误处理与诊断：15种ErrorCode、异常+错误列表双轨、子图分区报告](concepts/04-error-diagnostics.md) — OnnxTrtException 异常模型、ONNXTRT_TRY/CATCH 边界宏设计、Status/IParserError 丰富上下文、ValueOrStatus 返回值模式、supportsModelV2 子图分区算法、DLA 能力验证模式、15 种 ErrorCode 分类与排查路径。

## 实战示例（examples/）

* [使用解析器加载 ONNX 模型到 TensorRT 网络：构建 engine 与推理](examples/parse-onnx-model.md) — 完整推理流程：Logger→Builder→Network→Parser→parseFromFile→错误处理→BuilderConfig→动态形状 OptimizationProfile→buildSerializedNetwork→反序列化→enqueueV3 推理，含 CMakeLists.txt 和分步 API 权重注入示例。
* [自定义插件处理不支持的算子](examples/custom-plugin.md) — IPluginV3One+IPluginCreatorV3One 插件实现、REGISTER_TENSORRT_PLUGIN 自注册、GPU kernel 编写、属性传递、plugin_namespace 三级查找、VC 引擎插件序列化、Python 端创建带插件节点的 ONNX 模型。

## 信源登记簿（references/）

* [IParser 公共 API 与 ModelImporter 实现](references/parser-api.md) — `NvOnnxParser.h`（公共 API v0.2.0）、`ModelImporter.hpp/cpp`（IParser 具体实现）：IParser 纯虚接口、三种解析入口、supportsModelV2 子图查询、5 个 OnnxParserFlag、IParserRefitter 重拟合、importModel 六阶段管线、parseGraph 拓扑排序、parseNode 四层分发、子图分区算法。
* [核心工具类：ShapedWeights/OnnxAttrs/TensorOrWeights/WeightsContext/BFloat16/Status](references/core-utilities.md) — `TensorOrWeights.hpp`（变体类型）、`ShapedWeights.hpp/cpp`（非拥有视图）、`OnnxAttrs.hpp/cpp`（属性访问器）、`WeightsContext.hpp`（内存管理）、`bfloat16.hpp/cpp`（BF16 位操作）、`Status.hpp`/`errorHelpers.hpp`（错误处理）、`ImporterContext.hpp`（中央上下文）、`importerUtils.hpp`（RAII 与 helper 函数）。

## 信任与生命周期说明

* **status 判定依据**：全部 9 个内容文档（5 个概念 + 2 个示例 + 2 个信源登记）均 `status: stable`。内容基于对 onnx-tensorrt 源码（`external/libs/models/onnx/onnx-tensorrt/` 目录）核心文件的逐文件阅读与事实提取（33 条源码事实 F-001~F-033），经 seven-concepts 方法论 R→I→E→V 四阶段流程生成。
* **stale_after 解释**：统一设置为 `2027-12-31`。onnx-tensorrt 核心架构（IParser 门面/ModelImporter 六阶段管线/算子注册表模式/WeightsContext 权重管理）自 TensorRT 7.x 以来保持稳定，新算子和插件接口版本不断添加但核心设计不变；该日期作为针对 TensorRT 未来大版本（如 12.x+）的保守重新评估节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻；`verified.at` 记录 V 阶段对抗审查核验事件，两者分离、可追溯。

本知识包共收录 9 个内容文档（5 个概念 + 2 个示例 + 2 个信源登记），另含 3 个子目录 index.md 与根 index.md、log.md。
