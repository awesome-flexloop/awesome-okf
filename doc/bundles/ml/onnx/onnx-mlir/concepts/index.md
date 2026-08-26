---
type: concept_index
title: "onnx-mlir 核心概念索引"
description: "onnx-mlir 核心概念文档导航"
generated: true
verified: grep
status: stable
stale_after: 2026-12-31
---

# onnx-mlir 核心概念


概念文档

本目录包含 ONNX-MLIR 的 6 个核心概念文档，按学习路径排列：从架构总览到 Dialect 设计、转换管线、运行时和编译选项，逐步深入。

## 架构与核心设计

* [ONNX-MLIR 整体架构：多级 Lowering 编译器](00-overall-architecture.md) — 多级 lowering 流水线总览、Krnl/Linalg 双路径、7种输出目标、MLIR Pass+外部LLVM工具链分层协作、加速器插件架构、自描述共享库设计。

## Dialect 体系

* [ONNX Dialect：ONNX 算子的 MLIR 表示](01-onnx-dialect.md) — ONNX Dialect 命名空间与声明、TableGen Op 定义体系、ShapeInference 接口、ONNXTensorEncodingAttr 自定义布局属性、ONNX 级预处理 Passes、FrontendDialectTransformer 前端导入。
* [Krnl Dialect：编译策略层中间表示](02-krnl-dialect.md) — Krnl Dialect 的核心创新定位（洞察I-01："优化即IR"反常识设计）、循环优化操作集（define_loops/iterate/block/permute/unroll/parallel/matmul）、内存操作（load/store/memcpy/memset/tile_buffer/global）、运行时桥接操作（call/entry_point/instrument）、Krnl→Affine lowering、与 Linalg 路径的对比。

## 编译管线

* [Dialect 转换管线：ONNX→Krnl→Affine→LLVM](03-lowering-pipeline.md) — 完整 lowering 管线四阶段详解：ONNX预处理Passes、ONNX→Krnl Op lowering（Math/NN/Tensor/RNN/ControlFlow分类实现）、Krnl→Affine循环转换、Krnl→LLVM最终转换（入口点转换/运行时函数生成/C包装）、MLIR Pass与外部工具链边界、Linalg替代路径。

## 运行时与部署

* [运行时执行模型：ExecutionSession 与自描述共享库](04-runtime-execution.md) — run_main_graph统一C ABI、OMTensor/OMTensorList张量数据结构、ExecutionSession动态库加载（dlopen/LoadLibrary）、多入口点与tag符号管理、JSON签名自描述机制（洞察I-03）、信号处理与错误恢复、Python/C++/C/Java多语言绑定。

## 性能调优

* [编译选项体系与性能调优](05-compiler-options.md) — O0-O3优化级别实质差异（tiling/SIMD/并行化条件）、目标三元组/架构/CPU配置、加速器插件（NNPA）、--Xopt/--Xllc/--mllvm LLVM选项透传、调试与剖析选项（print-ir/timing/instrument/bind-check）、三源选项优先级、外部工具链依赖、常用调优场景。

```{toctree}
:hidden:
:maxdepth: 7

00-overall-architecture
01-onnx-dialect
02-krnl-dialect
03-lowering-pipeline
04-runtime-execution
05-compiler-options
```
