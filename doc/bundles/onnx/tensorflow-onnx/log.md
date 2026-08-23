---
type: log
title: tensorflow-onnx 变更日志
description: 记录文档生成与更新历史
generated: true
verified: grep
status: stable
stale_after: 2026-12-31
---

# Bundle Update Log

## 2026-08-22

* **Creation**: 建立 tensorflow-onnx (tf2onnx) 知识包脚手架（concepts/examples/references 三目录），遵循 OKF v0.2 规范。
* **Add**: R阶段完成——深度阅读 tf2onnx 源码核心模块：`tf2onnx/convert.py`（转换入口与命令行）、`tf2onnx/tfonnx.py`（核心转换流程、重写器框架、算子映射）、`tf2onnx/handler.py`（@tf_op 装饰器与版本注册表）、`tf2onnx/graph.py`（Node/Graph/ExternalTensorStorage 图表示）、`tf2onnx/graph_matcher.py`（OpTypePattern 模式匹配）、`tf2onnx/optimizer/__init__.py`（12 个图优化器）、`tf2onnx/tf_loader.py`（多格式模型加载与 _Lazy 代理）、`tf2onnx/onnx_opset/`（13 个分类算子处理器）、`tf2onnx/shape_inference.py`（形状推断）、`tf2onnx/constants.py`（常量定义）、`tf2onnx/tf_utils.py`（Protobuf 1:1 转换）、`tf2onnx/__init__.py`（PEP 562 懒加载），提取 44 条源码事实，覆盖项目概述/包结构/转换入口/核心流程/算子映射/图表示/图重写/图优化/Protobuf转换/模型加载/形状推断/数据格式/命令行/常量折叠/自定义算子/Target适配等模块。
* **Add**: I阶段完成——提炼 3 个核心架构洞察（I-01 装饰器驱动的版本化算子注册表实现无分支多版本兼容/I-02 三阶段图转换流水线Rewriter→Mapper→Optimizer实现关注点分离/I-03 以ONNX Protobuf作为内部IR的"目标即IR"哲学），设计知识地图（7个概念文档+3个示例+3个信源登记）。
* **Add**: E阶段完成——references/ 下 3 个信源登记（convert-entry/graph-rewriter/opset-mapping），concepts/ 下 7 个概念文档（00-overall-architecture/01-conversion-pipeline/02-versioned-opset-registry/03-graph-rewriting/04-graph-internal-api/05-optimizers/06-data-layout-types），examples/ 下 3 个实战示例（keras-conversion/savedmodel-conversion/custom-op-mapping），加上 3 个子目录 index.md 和根 index.md、log.md。
