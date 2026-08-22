---
type: bundle
title: ONNX-MLIR 编译器
okf_version: "0.2"
---


# ONNX-MLIR 编译器知识库

本知识包是 [ONNX-MLIR](https://github.com/onnx/onnx-mlir)（Apache-2.0 许可证）——基于 LLVM/MLIR 技术栈的 ONNX 模型编译器——的系统化中文源码教程，基于 ONNX-MLIR 源码（`src/` 目录下核心模块）深度阅读生成，覆盖从多级 lowering 流水线架构、ONNX/Krnl 双 Dialect 设计、完整转换管线、自描述共享库运行时模型到编译选项调优的完整知识体系。所有内容均溯源至源码核心模块（`onnx-mlir.cpp`/`CompilerUtils.cpp`/`CompilerPasses.cpp`/`ONNX.td`/`Krnl.td`/`ExecutionSession.hpp`/`OnnxMlirRuntime.h` 等），遵循 [OKF v0.2 规范](../../meta/okf-spec/index.md)。

ONNX-MLIR 将 ONNX 计算图编译为最小运行时支持的原生共享库，核心创新是插入 Krnl Dialect 作为"编译策略层"——将循环 tiling、SIMD、并行等优化决策编码进 IR 本身，结合 MLIR Pass+外部 LLVM 工具链的分层架构，输出自描述的 .so/.dll 部署单元（内嵌模型签名和元数据查询函数）。

## 架构与 Dialect 设计（concepts/）

* [ONNX-MLIR 整体架构：多级 Lowering 编译器](concepts/00-overall-architecture.md) — 多级 lowering 流水线总览、Krnl/Linalg 双 lowering 路径、7种输出目标、MLIR Pass+外部LLVM工具链分层协作模型、加速器插件架构、自描述共享库设计。
* [ONNX Dialect：ONNX 算子的 MLIR 表示](concepts/01-onnx-dialect.md) — onnx命名空间、TableGen Op 定义体系、ShapeInferenceOpInterface 形状推断、ONNXTensorEncodingAttr 自定义布局编码、ONNX级预处理Passes（形状推断/常量折叠/算子融合）、FrontendDialectTransformer 前端导入。
* [Krnl Dialect：编译策略层中间表示](concepts/02-krnl-dialect.md) — Krnl 作为"优化即IR"的设计哲学（I-01反常识洞察）、循环优化操作集（define_loops/iterate/block/permute/unroll/parallel/matmul）、内存操作（load/store/memcpy/tile_buffer/global）、运行时桥接（call/entry_point/instrument）、Krnl→Affine lowering、与Linalg路径的对比。

## 编译管线与运行时（concepts/）

* [Dialect 转换管线：ONNX→Krnl→Affine→LLVM](concepts/03-lowering-pipeline.md) — 四阶段 lowering 管线详解：ONNX预处理Passes、ONNX→Krnl Op lowering（Math/NN/Tensor/RNN/ControlFlow）、Krnl→Affine循环转换、Krnl→LLVM最终转换（入口点转换/运行时函数生成/C包装/常量处理）、MLIR Pass与外部opt/llc/cxx/jar工具链边界、Linalg替代路径。
* [运行时执行模型：ExecutionSession 与自描述共享库](concepts/04-runtime-execution.md) — run_main_graph统一C ABI、OMTensor/OMTensorList张量数据结构、ExecutionSession动态加载(dlopen/LoadLibrary+dlsym)、多入口点与tag符号管理、JSON签名自描述机制（I-03洞察）、信号处理与错误恢复、Python/C++/C/Java多语言绑定。
* [编译选项体系与性能调优](concepts/05-compiler-options.md) — O0-O3优化级别实质差异（tiling/SIMD/并行化条件）、目标三元组/架构/CPU配置、加速器插件（NNPA）、--Xopt/--Xllc/--mllvm LLVM选项透传、调试与剖析选项、三源选项优先级、外部工具链依赖、常用调优场景。

## 实战示例（examples/）

* [编译 ONNX 模型为共享库并使用 Python 运行时推理](examples/compile-model.md) — 端到端流程：创建ONNX模型→onnx-mlir命令行编译（O3优化/tag/IR查看选项）→Python/C++/C三种方式加载推理（PyRuntime/ExecutionSession/C API）→正确性验证（numpy对比）→常见问题排查（opt未找到/符号冲突/形状不匹配）。

## 信源登记簿（references/）

* [编译器入口：onnx-mlir.cpp 驱动与编译流程](references/compiler-entry.md) — `src/onnx-mlir.cpp`（main()执行流程/配置文件/选项优先级）、`src/Compiler/CompilerUtils.cpp`/`.hpp`（输入文件处理/7种输出目标/编译阶段打印/外部工具链调度opt/llc/cxx/jar）、`src/Compiler/CompilerOptions.hpp`（O0-O3/--mtriple/--march/--maccel/调试选项）、`include/onnx-mlir/Compiler/OMCompilerTypes.h`（EmissionTargetType枚举）。
* [Dialect 定义与运行时：ONNX/Krnl Dialect 与 ExecutionSession](references/dialects-runtime.md) — `src/Dialect/ONNX/ONNX.td`（ONNX Dialect声明/ONNXTensorEncodingAttr）、`src/Dialect/Krnl/Krnl.td`（Krnl Dialect声明与8个依赖Dialect）、`src/Compiler/CompilerPasses.cpp`（全管线Pass编排：ONNX预处理/ONNXToKrnl/KrnlToAffine/KrnlToLLVM/Linalg路径）、`src/Conversion/KrnlToLLVM/ConvertKrnlToLLVM.hpp`（KrnlToLLVM最终转换/运行时函数生成）、`src/Runtime/ExecutionSession.hpp`（动态库加载/符号解析/多入口点/信号处理）、`include/OnnxMlirRuntime.h`（OMTensor/OMTensorList/run_main_graph C ABI）、`include/onnx-mlir/Runtime/OMEntryPoint.h`（入口点查询API）、`src/Accelerators/Accelerator.hpp`（加速器插件基类）。

## 信任与生命周期说明

* **status 判定依据**：全部 9 个内容文档（6 个概念 + 1 个示例 + 2 个信源登记）均 `status: stable`。内容基于对 ONNX-MLIR 源码核心模块的逐文件阅读与事实提取（31 条源码事实 F-001~F-031），经 seven-concepts 方法论 R→I→E 三阶段流程生成，提炼 3 个核心架构洞察（I-01 Krnl编译策略层/I-02 MLIR+外部LLVM工具链分层/I-03 自描述共享库）。
* **stale_after 解释**：统一设置为 `2027-12-31`。ONNX-MLIR 核心架构（多级lowering/Krnl策略层/ExecutionSession自描述运行时/外部工具链调度）自项目早期以来设计稳定，Krnl Dialect和7种输出目标已确立核心范式；Linalg路径仍在演进但Krnl路径是默认且成熟的实现；该日期作为针对未来大版本重构的保守重新评估节点。
* **核验链路**：事实来源于对源码的静态分析（31条事实F-001~F-031，每条附源码路径和行号证据），洞察基于事实提炼（3个洞察I-01~I-03，各含证据链、反常识点和行动建议），示例代码基于验证过的API编写（run_main_graph C ABI、OMTensor/OMTensorList、ExecutionSession动态加载、PyRuntime Python绑定）。

本知识包共收录 9 个内容文档（6 个概念 + 1 个示例 + 2 个信源登记），另含 3 个子目录 index.md 与根 index.md、log.md。
