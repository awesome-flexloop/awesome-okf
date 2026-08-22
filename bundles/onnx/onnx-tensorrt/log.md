---
type: log
title: onnx-tensorrt 变更日志
description: 记录文档生成与更新历史
generated: true
verified: grep
status: stable
stale_after: 2026-12-31
---

# Bundle Update Log

## 2026-08-22

* **Creation**: 建立 ONNX-TensorRT 知识包脚手架（concepts/examples/references 三目录），遵循 OKF v0.2 规范。
* **Add**: R阶段完成——深度阅读 onnx-tensorrt 源码（`external/libs/models/onnx/onnx-tensorrt/`）核心模块：`NvOnnxParser.h`（公共 API v0.2.0、IParser/IParserRefitter 接口、ErrorCode/OnnxParserFlag 枚举）、`ModelImporter.hpp/cpp`（IParser 具体实现类 ModelImporter、importModel 六阶段解析管线、parseGraph 拓扑排序、parseNode 四层分发、子图分区报告）、`TensorOrWeights.hpp`（ITensor*/ShapedWeights 变体类型）、`ShapedWeights.hpp/cpp`（非拥有权重视图）、`OnnxAttrs.hpp/cpp`（节点属性访问器、模板特化 get<T>()）、`WeightsContext.hpp`（权重内存所有权管理、类型自动转换、mmap 外部权重）、`bfloat16.hpp/cpp`（BF16 手工位操作与 round-to-even 舍入）、`Status.hpp`/`errorHelpers.hpp`（15种ErrorCode、异常+错误列表双轨机制）、`ImporterContext.hpp`（中央解析上下文）、`onnxOpImporters.cpp`（194个内置算子通过 DEFINE_BUILTIN_OP_IMPORTER 自注册、FallbackPluginImporter、LocalFunctionImporter）、`importerUtils.hpp/cpp`（NameScope RAII、通用 helper 函数），提取 33 条源码事实，覆盖公共API/ModelImporter/算子注册/核心数据结构/权重管理/错误处理/Python绑定/构建产物/辅助组件等全栈模块。
* **Add**: I阶段完成——提炼 3 个核心架构洞察（I-01 两遍式拓扑遍历+算子注册表编译器架构/I-02 权重所有权与类型适配独立子系统/I-03 插件可扩展性出口与兼容性陷阱），设计知识地图（架构总览1篇→核心机制4篇，共5概念+2示例+2信源）。
* **Add**: E阶段完成——concepts/ 下 5 个概念文档（00-overall-architecture/01-parsing-pipeline/02-op-registration-plugin/03-weights-memory-model/04-error-diagnostics），examples/ 下 2 个实战示例（parse-onnx-model/custom-plugin），references/ 下 2 个信源登记（parser-api/core-utilities），加上 3 个子目录 index.md 和根 index.md、log.md。
