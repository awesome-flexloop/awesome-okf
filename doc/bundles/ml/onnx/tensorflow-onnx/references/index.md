---
type: reference_index
title: "tensorflow-onnx API 参考索引"
description: "tensorflow-onnx API 参考文档导航"
generated: true
verified: grep
status: stable
stale_after: 2026-12-31
---

# tensorflow-onnx API 参考


信源登记簿

本目录登记本知识包所有内容据以派生的 tf2onnx 源码信源。所有概念文档和示例文档的 `sources` 字段均指向此目录下的信源登记条目。

* [转换入口 API：from_keras / from_saved_model / from_function / 命令行](convert-entry.md) — `tf2onnx/convert.py`（Python API 五个核心转换函数、_convert_common 核心流程、命令行参数解析）、`tf2onnx/tf_loader.py`（多格式模型加载、_Lazy 代理模式）、`tf2onnx/constants.py`（PREFERRED_OPSET 常量）。
* [图表示 Graph 类与重写机制（Rewriter / GraphMatcher）](graph-rewriter.md) — `tf2onnx/graph.py`（Node/Graph/ExternalTensorStorage 类定义、三大索引体系、make_node/make_model API）、`tf2onnx/graph_matcher.py`（OpTypePattern 树形模式匹配、MatchResult）、`tf2onnx/tfonnx.py`（run_rewriters 执行框架、20+ 预处理重写器、late_rewriters Target 条件激活）。
* [算子版本化注册表：@tf_op 装饰器与 onnx_opset 目录](opset-mapping.md) — `tf2onnx/handler.py`（tf_op 装饰器类、_OPSETS 三维注册表、create_mapping 版本堆叠算法）、`tf2onnx/onnx_opset/`（13 个按类别分文件的算子处理器实现、DirectOp 模式）、`tf2onnx/tfonnx.py`（tensorflow_onnx_mapping 遍历映射、custom_op_handlers 兼容层）。

```{toctree}
:maxdepth: 7

convert-entry
graph-rewriter
opset-mapping
```
