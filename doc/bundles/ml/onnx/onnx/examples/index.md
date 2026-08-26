---
type: example_index
title: "onnx 示例索引"
description: "onnx 示例文档导航"
generated: true
verified: grep
status: stable
stale_after: 2026-12-31
---

# onnx 示例


实战示例

本目录包含 4 个完整的 ONNX 操作示例，每个示例对应核心概念，提供从基础构造到高级操作的渐进式学习路径。

* [从零构建线性回归模型](build-linear-regression.md) — make_tensor_value_info 定义输入输出→make_node 创建节点→make_graph 构建图→make_model 封装→save_model 保存，完整可运行代码。对应概念：[Python Helper API 详解](../concepts/09-python-helpers.md)、[计算图模型](../concepts/03-computation-graph.md)、[张量类型系统](../concepts/02-tensor-type-system.md)。
* [模型加载、检查与形状推断](load-check-model.md) — load_model 加载→check_model 基础检查→infer_shapes 形状推断→check_model(full_check=True) 完整检查→numpy_helper.to_array 读取张量，含模型结构统计和权重读取。对应概念：[模型检查器 Checker](../concepts/07-model-checker.md)、[形状推断实现](../concepts/06-shape-inference.md)、[序列化/反序列化与外部数据](../concepts/08-serialization.md)。
* [图遍历与变换实战](graph-transformation.md) — 遍历 GraphProto.node、修改节点属性、添加/删除节点（边重连）、操作 initializer 权重、形状推断后访问 value_info、深拷贝保护原模型。对应概念：[计算图模型](../concepts/03-computation-graph.md)、[Protobuf IR：核心 Message 结构](../concepts/01-protobuf-ir.md)、[C++ 核心IR](../concepts/12-cpp-core-ir.md)。
* [自定义算子注册与使用示例](custom-operator.md) — 使用自定义 domain 构建自定义 op 节点、opset_import 包含自定义域、checker 对自定义 op 的行为（默认跳过/full_check失败）、手动 value_info 绕过方法、FunctionProto 局部函数与内联。对应概念：[算子定义与注册机制 OpSchema](../concepts/05-operator-schema.md)、[版本转换与函数内联](../concepts/13-version-converter-inliner.md)、[Opset版本机制与算子域](../concepts/04-opset-versioning.md)。

```{toctree}
:maxdepth: 7

build-linear-regression
custom-operator
graph-transformation
load-check-model
```
