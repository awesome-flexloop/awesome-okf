---
type: log
title: onnx-mlir 变更日志
description: 记录文档生成与更新历史
generated: true
verified: grep
status: stable
stale_after: 2026-12-31
---

# Bundle Update Log

## 2026-08-22

* **Creation**: 建立 ONNX-MLIR 知识包脚手架（concepts/examples/references 三目录），遵循 OKF v0.2 规范。
* **Add**: R阶段完成——深度阅读 ONNX-MLIR 源码核心模块：`src/onnx-mlir.cpp`（命令行入口main()执行流程）、`src/Compiler/CompilerUtils.cpp`/`.hpp`（输入处理/编译阶段/外部工具链调度）、`src/Compiler/CompilerOptions.hpp`（编译选项体系）、`src/Compiler/CompilerPasses.cpp`（全管线Pass编排）、`include/onnx-mlir/Compiler/OMCompilerTypes.h`（7种输出目标）、`src/Dialect/ONNX/ONNX.td`（ONNX Dialect/ONNXTensorEncodingAttr）、`src/Dialect/Krnl/Krnl.td`（Krnl Dialect声明）、`src/Conversion/ONNXToKrnl/`（Op lowering目录结构）、`src/Conversion/KrnlToLLVM/ConvertKrnlToLLVM.hpp`（KrnlToLLVM最终转换）、`src/Runtime/ExecutionSession.hpp`（动态库加载/符号解析/推理执行）、`include/OnnxMlirRuntime.h`（OMTensor/OMTensorList/run_main_graph C ABI）、`include/onnx-mlir/Runtime/OMEntryPoint.h`（入口点查询API）、`src/Accelerators/Accelerator.hpp`（加速器插件基类）、`src/Builder/FrontendDialectTransformer.hpp`（ONNX前端导入），提取 31 条源码事实（F-001~F-031），覆盖整体架构/入口与命令行/编译选项/ONNX Dialect/Krnl Dialect/Dialect转换层次/运行时/ONNX前端/加速器支持等模块。
* **Add**: I阶段完成——提炼 3 个核心架构洞察（I-01 Krnl Dialect是"编译策略层"而非语义IR的"优化即IR"反常识设计/I-02 MLIR Pass+外部LLVM工具链的松耦合分层架构/I-03 多入口点+动态符号解析的自描述共享库运行时模型），设计知识地图（架构总览1篇→Dialect体系2篇→编译管线1篇→运行时1篇→编译选项1篇，共6概念+1示例+2信源）。
* **Add**: E阶段完成——concepts/ 下 6 个概念文档（00-overall-architecture/01-onnx-dialect/02-krnl-dialect/03-lowering-pipeline/04-runtime-execution/05-compiler-options），examples/ 下 1 个实战示例（compile-model），references/ 下 2 个信源登记（compiler-entry/dialects-runtime），加上 3 个子目录 index.md 和根 index.md、log.md。
