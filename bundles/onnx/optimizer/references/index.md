---
type: reference_index
title: "optimizer API 参考索引"
description: "optimizer API 参考文档导航"
generated: true
verified: grep
status: stable
stale_after: 2026-12-31
---

# optimizer API 参考


信源登记簿

本目录登记 ONNX Optimizer 知识包所有内容据以派生的 C++ 源码信源。所有概念文档和示例文档的 `sources` 字段均指向此目录下的信源登记条目。信源基于 ONNX Optimizer v0.4.2 源码（`external/libs/models/onnx/optimizer/onnxoptimizer/` 目录）的核心头文件和实现文件。

* [Pass 基类与注册机制](pass-base.md) — `pass.h` / `pass.cc`（Pass 抽象基类、PredicateBasedPass/FullGraphBasedPass/ImmutablePass 继承体系、PostPassAnalysis、子图递归工具、安全替换函数）、`pass_registry.h` / `pass_registry.cc`（GlobalPassRegistry 单例、registerPass 模板、GetFuseAndEliminationPass 默认集合筛选）：覆盖 F-016~F-036。
* [PassManager 执行引擎与 Optimizer 入口类](pass-manager.md) — `pass_manager.h` / `pass_manager.cc`（PassManager 抽象基类、GeneralPassManager 线性执行、FixedPointPassManager 定点迭代算法）、`optimize.h` / `optimize.cc`（Optimizer 入口类、IR v3→v4 自动升级、proto↔Graph 转换、Optimize/OptimizeFixed 自由函数）：覆盖 F-037~F-044。
* [Python API、命令行 API 与 C API](python-c-api.md) — `__init__.py`（optimize 函数签名、大模型回退路径）、`cpp2py_export.cc`（nanobind 绑定）、`onnxoptimizer_main.py`（CLI 参数与流程）、`model_util.h/cc`（loadModel/saveModel、外部数据处理）、`c_api/onnxoptimizer_c_api.h`（纯 C API 及已知拼写错误）、`pass_util.h`（pass 开发工具函数）、`data_type.h`（FP16/BF16/复数类型）、`examples/onnx_optimizer_exec.cpp`（C++ 示例）：覆盖 F-006~F-015、F-054~F-060。
