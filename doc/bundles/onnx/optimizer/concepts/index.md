---
type: concept_index
title: "optimizer 核心概念索引"
description: "optimizer 核心概念文档导航"
generated: true
verified: grep
status: stable
stale_after: 2026-12-31
---

# optimizer 核心概念


概念文档

本目录包含 ONNX Optimizer 的 7 个核心概念文档，按从架构到使用、从核心到扩展的学习路径排列。

## 架构与核心机制

* [ONNX Optimizer 整体架构](00-overall-architecture.md) — 三层架构（C++核心/Python绑定/C API）、IR版本自动升级、设计哲学与实验性声明。
* [Pass 系统：基类继承体系与注册机制](01-pass-system.md) — Pass/PredicateBasedPass/FullGraphBasedPass/ImmutablePass 类层次、三个元数据注解（类型/效率/优化目标）、PostPassAnalysis 定点收敛机制、GlobalPassRegistry 单例注册、子图递归处理。
* [PassManager 执行模型与定点收敛](03-pass-execution.md) — GeneralPassManager 线性执行、FixedPointPassManager 双层定点迭代算法、全局vs局部pass执行差异、pass排序策略、Optimizer入口完整流程。

## 优化 Passes 与融合模式

* [内置优化 Passes 分类与功能](02-builtin-passes.md) — 50个内置pass完整分类：Fuse融合类17个、Nop消除类21个、Replace替换类4个、Separate分离类3个、Other/Immutable结构类5个，各pass功能与适用条件。
* [算子融合模式](04-fusion-patterns.md) — BN-Conv融合、AddBias融合、QKV融合、连续Transpose/Concat/Squeeze融合、Pad融合、GEMM相关融合的数学原理与匹配条件。

## API 与扩展开发

* [Python API、CLI 与 C API 使用指南](05-python-cli-api.md) — optimize()函数用法、get_available_passes()/get_fuse_and_elimination_passes()辅助函数、CLI参数与流程、C++自由函数API、纯C API注意事项、大模型自动处理、典型优化管道。
* [自定义 Pass 开发方法](06-custom-pass.md) — PredicateBasedPass vs FullGraphBasedPass选择决策树、patternMatchPredicate编写模式、runTransform节点操作规范、tryReplacingAllUsesWith保护机制、pass_util工具函数库、子图递归处理、opset版本兼容、注册新pass方法。
