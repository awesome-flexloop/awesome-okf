---
type: reference_index
title: "onnx-mlir API 参考索引"
description: "onnx-mlir API 参考文档导航"
generated: true
verified: grep
status: stable
stale_after: 2026-12-31
---

# onnx-mlir API 参考


信源登记簿

本目录登记本知识包所有内容据以派生的 ONNX-MLIR 源码信源。所有概念文档和示例文档的 `sources` 字段均指向此目录下的信源登记条目。信源基于 ONNX-MLIR 源码（`src/` 目录）核心头文件和实现文件的深度阅读。

* [编译器入口：onnx-mlir.cpp 驱动与编译流程](compiler-entry.md) — `src/onnx-mlir.cpp`（命令行入口 main() 执行流程）、`src/Compiler/CompilerUtils.cpp`/`.hpp`（输入处理/编译阶段/外部工具链调度）、`src/Compiler/CompilerOptions.hpp`（编译选项体系）、`include/onnx-mlir/Compiler/OMCompilerTypes.h`（7种输出目标枚举）。
* [Dialect 定义与运行时：ONNX/Krnl Dialect 与 ExecutionSession](dialects-runtime.md) — `src/Dialect/ONNX/ONNX.td`（ONNX Dialect/ONNXTensorEncodingAttr）、`src/Dialect/Krnl/Krnl.td`（Krnl Dialect 声明）、`src/Compiler/CompilerPasses.cpp`（全管线 Pass 编排：ONNX预处理→ONNXToKrnl→KrnlToAffine→KrnlToLLVM/Linalg路径）、`src/Conversion/KrnlToLLVM/ConvertKrnlToLLVM.hpp`（KrnlToLLVM 最终转换）、`src/Runtime/ExecutionSession.hpp`（动态库加载/符号解析/推理执行）、`include/OnnxMlirRuntime.h`（OMTensor/OMTensorList/run_main_graph C ABI）、`include/onnx-mlir/Runtime/OMEntryPoint.h`（入口点查询 API）、`src/Accelerators/Accelerator.hpp`（加速器插件基类）。

```{toctree}
:hidden:
:maxdepth: 7

compiler-entry
dialects-runtime
```
