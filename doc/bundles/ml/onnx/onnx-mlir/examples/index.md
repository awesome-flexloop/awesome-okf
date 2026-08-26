---
type: example_index
title: "onnx-mlir 示例索引"
description: "onnx-mlir 示例文档导航"
generated: true
verified: grep
status: stable
stale_after: 2026-12-31
---

# onnx-mlir 示例


实战示例

本目录包含 ONNX-MLIR 的端到端使用示例，从模型编译到多语言推理执行。

* [编译 ONNX 模型为共享库并使用 Python 运行时推理](compile-model.md) — 从零开始的完整流程：创建/获取 ONNX 模型 → 使用 onnx-mlir 命令行编译为自描述共享库（O3优化、tag选项、IR查看）→ Python/C++/C 三种方式加载推理（PyRuntime/ExecutionSession/C API）→ 正确性验证与常见问题排查。对应概念：[ONNX-MLIR 整体架构](../concepts/00-overall-architecture.md)、[Dialect 转换管线](../concepts/03-lowering-pipeline.md)、[运行时执行模型](../concepts/04-runtime-execution.md)、[编译选项体系与性能调优](../concepts/05-compiler-options.md)。

```{toctree}
:maxdepth: 7

compile-model
```
