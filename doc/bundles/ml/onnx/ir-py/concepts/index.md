---
type: concept_index
title: "ir-py 核心概念索引"
description: "ir-py 核心概念文档导航"
generated: true
verified: grep
status: stable
stale_after: 2026-12-31
---

# ir-py 核心概念


概念文档

本目录包含 onnx-ir 的 8 个核心概念文档，按学习路径排列：从架构总览到具体机制逐步深入。

## 架构总览

* [IR 整体架构：protobuf-free 分层设计](00-overall-architecture.md) — 纯 Python IR 层完全独立于 Protobuf，序列化层通过 Protocol 多态分发，六大子模块导出、21个公开实体类、关注点分离设计决策。

## 核心实体

* [核心实体：Model/Graph/Node/Value](01-core-entities.md) — Value 作为图连接中心的一等公民设计、producer/uses 双向引用、Node 受控变异 API、Graph 双向链表存储与拓扑排序、Model 的 opset 委托、Function 的 Graph 委托模式、Attr 统一属性表示。
* [张量体系：五种 Tensor 与零拷贝/延迟/mmap 设计](02-tensor-protocol.md) — TensorBase 统一协议，Tensor(零拷贝内存)/ExternalTensor(mmap+三层安全)/StringTensor/LazyTensor(thunk延迟)/PackedTensor(亚字节打包) 五种实现，TensorProtoTensor(protobuf零拷贝)，numpy/DLPack 互操作。
* [类型系统：DataType 枚举、形状 Dimension、AttributeType](03-type-system.md) — 27种 DataType（覆盖到INT2级位宽）、15种 AttributeType、SymbolicDim sympy 符号运算、Shape 冻结/维度合并规则、TensorType/SequenceType/OptionalType/SparseTensorType 递归类型层次。

## 数据结构与机制

* [双向链表图结构：DoublyLinkedSet 迭代安全与 NameAuthority 命名](04-doubly-linked-graph.md) — 循环双向链表+id索引实现 O(1) 增删、_LinkBox erase 不破坏指针的迭代器安全保证、NameAuthority 单调计数器永不释放的命名策略、Graph 容器包装与角色标记一致性。
* [序列化/反序列化：Protobuf 双向转换与多格式支持](05-serde.md) — from_proto()/to_proto() 多态分发（11+种类型）、两阶段作用域栈反序列化处理前向引用、TensorProtoTensor 零拷贝策略、外部数据分片并行写入、文本格式支持。

## 构建与元数据

* [Tape 图变换：算子录制、Builder 魔术方法与运算符重载](06-tape-transform.md) — Tape.op() 录制节点与 initializer、Builder.__getattr__ 伪方法调用、_magic_handler ClassVar 动态注入实现算术运算符重载、三种图构建方式对比。
* [名称管理、元数据存储与废弃 API](07-name-metadata.md) — NameAuthority 命名治理与永不释放设计、MetadataStore 失效标记（invalidate/valid）、meta（临时分析）vs metadata_props（可序列化）双轨元数据、Input()→ir.val() 废弃迁移、Attr* 工厂函数。

```{toctree}
:hidden:

00-overall-architecture
01-core-entities
02-tensor-protocol
03-type-system
04-doubly-linked-graph
05-serde
06-tape-transform
07-name-metadata
```
