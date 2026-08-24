---
type: bundle
title: ONNX Optimizer 图优化器
okf_version: "0.2"
---


# ONNX Optimizer 知识库

本知识包是 ONNX 图优化库 [ONNX Optimizer](https://github.com/onnx/optimizer) v0.4.2（Apache-2.0 许可证）的系统化中文源码教程，基于对 ONNX Optimizer C++ 源码（`external/libs/models/onnx/optimizer/onnxoptimizer/` 目录）的深度阅读生成，覆盖从三层架构到 Pass 系统、从内置优化 passes 到自定义扩展的完整知识体系。所有内容均溯源至 C++ 源码核心类和函数，遵循 OKF v0.2 规范。

## 架构与核心机制（concepts/）

* [ONNX Optimizer 整体架构](concepts/00-overall-architecture.md) — 三层架构（C++核心/Python薄绑定/C API）、IR v3→v4 自动升级、设计哲学与实验性声明。
* [Pass 系统：基类继承体系与注册机制](concepts/01-pass-system.md) — Pass/PredicateBasedPass/FullGraphBasedPass/ImmutablePass 类层次、三个元数据注解（类型/效率/优化目标）、PostPassAnalysis 定点收敛机制、GlobalPassRegistry 单例注册中心、子图递归处理、安全替换工具函数。
* [PassManager 执行模型与定点收敛](concepts/03-pass-execution.md) — GeneralPassManager 线性执行、FixedPointPassManager 双层定点迭代算法、全局 vs 局部 pass 执行差异、pass 排序策略、Optimizer 入口完整优化流程。

## 优化 Passes 与融合模式（concepts/）

* [内置优化 Passes 分类与功能](concepts/02-builtin-passes.md) — 50 个内置 pass 完整分类详解：算子融合类 17 个、无用操作消除类 21 个、算子替换类 4 个、图分离类 3 个、结构/元数据类 5 个，各 pass 功能、适用条件和限制。
* [算子融合模式](concepts/04-fusion-patterns.md) — BN-Conv 融合、AddBias 融合、QKV 融合、连续 Transpose/Concat/Squeeze 融合、Pad 融合、GEMM 相关融合、LogSoftmax 融合的数学原理、匹配条件和效果。

## API 使用与扩展开发（concepts/）

* [Python API、CLI 与 C API 使用指南](concepts/05-python-cli-api.md) — Python `optimize()` 函数用法、`get_available_passes()`/`get_fuse_and_elimination_passes()` 辅助函数、命令行参数与流程、C++ 自由函数 API、纯 C API 注意事项（含已知拼写错误）、大模型自动回退处理、与 onnx-simplifier 组合的典型优化管道。
* [自定义 Pass 开发方法](concepts/06-custom-pass.md) — PredicateBasedPass vs FullGraphBasedPass 选择决策树、patternMatchPredicate 编写模式、runTransform 节点操作规范、tryReplacingAllUsesWith 保护机制、pass_util.h 工具函数库使用、子图递归处理、opset 版本兼容、注册新 pass 完整流程。

## 实战示例（examples/）

* [使用预打包优化 Passes 优化 ONNX 模型](examples/optimize-model.md) — Python API/CLI/C++ 三种方式使用 onnxoptimizer：默认优化、自定义 pass 列表、定点迭代模式对比、与 onnx-simplifier 组合、大模型自动处理、C++ 直接调用、优化前后模型校验。
* [开发自定义优化 Pass](examples/custom-pass-dev.md) — 从零开发自定义 pass：PredicateBasedPass（消除双重 Relu、消除加零）和 FullGraphBasedPass（算子统计）的完整实现、模式匹配谓词编写、安全替换与节点销毁、子图递归、注册编译流程、单元测试模板、常见陷阱。

## 信源登记簿（references/）

* [Pass 基类与注册机制](references/pass-base.md) — `pass.h`/`pass.cc`（Pass 抽象基类、枚举类型、PredicateBasedPass 遍历算法、FullGraphBasedPass/ImmutablePass、PostPassAnalysis、安全替换函数）、`pass_registry.h`/`pass_registry.cc`（GlobalPassRegistry、registerPass 模板、GetFuseAndEliminationPass）：F-016~F-036。
* [PassManager 执行引擎与 Optimizer 入口类](references/pass-manager.md) — `pass_manager.h`/`pass_manager.cc`（PassManager/GeneralPassManager/FixedPointPassManager 算法实现）、`optimize.h`/`optimize.cc`（Optimizer 类、IR 版本升级、proto↔Graph 转换、Optimize/OptimizeFixed 自由函数）：F-037~F-044。
* [Python API、命令行 API 与 C API](references/python-c-api.md) — `__init__.py`（optimize 函数、大模型回退）、`cpp2py_export.cc`（nanobind 绑定）、`onnxoptimizer_main.py`（CLI 参数与流程）、`model_util.h/cc`（loadModel/saveModel、外部数据处理）、`c_api/onnxoptimizer_c_api.h`（纯 C API）、`pass_util.h`（工具函数库）、`data_type.h`（FP16/BF16/复数类型）、C++ 示例：F-006~F-015、F-054~F-060。

## 信任与生命周期说明

* **status 判定依据**：全部 12 个内容文档（7 个概念 + 2 个示例 + 3 个信源登记）均 `status: stable`。内容基于对 ONNX Optimizer v0.4.2 源码（`external/libs/models/onnx/optimizer/onnxoptimizer/` 目录）核心模块的逐文件阅读与事实提取（60 条源码事实 F-001~F-060），经 R→I→E 阶段流程生成。
* **stale_after 解释**：统一设置为 `2027-08-22`。ONNX Optimizer 核心架构（Pass 基类体系、PassManager 执行引擎、GlobalPassRegistry 注册机制）自 0.x 以来稳定；新 pass 不断添加但核心设计不变；该日期作为一年后重新评估的保守节点。
* **已知限制**：所有源码文件标注 "highly EXPERIMENTAL"，API 可能变化；C API 存在 `C_API_OtimizeFromFile` 拼写错误（ABI 兼容性导致无法修复）；项目不做常量折叠（需配合 onnx-simplifier 使用）。

本知识包共收录 12 个内容文档（7 个概念 + 2 个示例 + 3 个信源登记），另含 3 个子目录 index.md 与根 index.md、log.md。

```{toctree}
:hidden:

concepts/index
examples/index
references/index
log
```
