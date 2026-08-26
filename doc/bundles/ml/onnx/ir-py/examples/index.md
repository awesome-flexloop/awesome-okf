---
type: example_index
title: "ir-py 示例索引"
description: "ir-py 示例文档导航"
generated: true
verified: grep
status: stable
stale_after: 2026-12-31
---

# ir-py 示例


实战示例

本目录包含 3 个完整的 onnx-ir 使用示例，覆盖从图构建到遍历变换再到序列化的完整工作流。

* [使用 IR 构建计算图](build-graph.md) — 从零开始构建卷积神经网络计算图（Conv→BN→Relu→MaxPool→Flatten→Gemm→Softmax）：Builder 录制算子、Initializer 权重注册、Graph/Model 构造、to_proto 序列化、magic_handler 运算符重载风格。对应概念：[IR 整体架构](../concepts/00-overall-architecture.md)、[核心实体 Model/Graph/Node/Value](../concepts/01-core-entities.md)、[Tape 图变换](../concepts/06-tape-transform.md)、[类型系统](../concepts/03-type-system.md)。
* [图遍历与变换](graph-traversal.md) — 顺序迭代、前驱/后继查询、子图递归遍历、安全增删节点、replace_all_uses_with 值替换、常量折叠 Pass 完整实现、收集-应用模式最佳实践。对应概念：[核心实体 Model/Graph/Node/Value](../concepts/01-core-entities.md)、[双向链表图结构](../concepts/04-doubly-linked-graph.md)、[张量体系](../concepts/02-tensor-protocol.md)。
* [序列化到 Protobuf 与反序列化](serialize-protobuf.md) — load/save 完整流程、to_proto/from_proto 多态转换、TensorProtoTensor 零拷贝策略、ExternalTensor mmap 按需加载、外部数据分片保存、文本格式转换、大模型内存优化、完整 roundtrip 验证。对应概念：[序列化/反序列化](../concepts/05-serde.md)、[张量体系](../concepts/02-tensor-protocol.md)、[IR 整体架构](../concepts/00-overall-architecture.md)。

```{toctree}
:hidden:
:maxdepth: 7

build-graph
graph-traversal
serialize-protobuf
```
