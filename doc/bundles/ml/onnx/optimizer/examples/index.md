---
type: example_index
title: "optimizer 示例索引"
description: "optimizer 示例文档导航"
generated: true
verified: grep
status: stable
stale_after: 2026-12-31
---

# optimizer 示例


实战示例

本目录包含 2 个 ONNX Optimizer 实战示例，覆盖从基础使用到自定义扩展的渐进式学习路径。

* [使用预打包优化 Passes 优化 ONNX 模型](optimize-model.md) — Python API/CLI/C++ 三种方式使用 onnxoptimizer 优化模型：默认优化、自定义 pass 列表、定点迭代、与 onnx-simplifier 组合使用、大模型自动处理、优化前后校验完整流程。对应概念：[整体架构](../concepts/00-overall-architecture.md)、[内置优化 Passes](../concepts/02-builtin-passes.md)、[PassManager 执行模型](../concepts/03-pass-execution.md)、[Python/CLI/C API](../concepts/05-python-cli-api.md)。
* [开发自定义优化 Pass](custom-pass-dev.md) — 从零开发自定义 pass 的完整教程：PredicateBasedPass（消除双重 Relu、消除加零）和 FullGraphBasedPass（算子统计）的实现、模式匹配谓词编写、安全替换与节点销毁、子图递归、注册编译、测试验证。对应概念：[Pass 系统](../concepts/01-pass-system.md)、[PassManager 执行模型](../concepts/03-pass-execution.md)、[自定义 Pass 开发方法](../concepts/06-custom-pass.md)。

```{toctree}
:hidden:
:maxdepth: 7

custom-pass-dev
optimize-model
```
