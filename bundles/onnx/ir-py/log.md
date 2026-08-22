---
type: log
title: ir-py 变更日志
description: 记录文档生成与更新历史
generated: true
verified: grep
status: stable
stale_after: 2026-12-31
---

# Bundle Update Log

## 2026-08-22

* **Creation**: 建立 onnx-ir（ir-py）知识包脚手架（concepts/examples/references 三目录），遵循 OKF v0.2 规范。
* **Add**: R阶段完成——深度阅读 onnx-ir（`onnx_ir` 包 v1.1.0，`src/onnx_ir/` 目录）核心模块：`_core.py`（~5300行，Tensor/Value/Node/Graph/Model/Function/Shape/Attr/Type 全部核心实体）、`_enums.py`（~410行，DataType/AttributeType 枚举）、`_tape.py`（~240行，Tape/Builder 图构建录制器）、`serde.py`（~1200行，protobuf 序列化/反序列化、TensorProtoTensor 零拷贝）、`_io.py`（~200行，模型 load/save 与外部数据）、`_linked_list.py`（~280行，DoublyLinkedSet 双向链表）、`_name_authority.py`（~70行，NameAuthority 自动命名）、`_metadata.py`（~50行，MetadataStore 元数据存储），提取 63 条源码事实（F-001~F-063），覆盖项目概览/类型枚举/张量体系/形状符号/核心实体/双向链表/序列化/IO/元数据/废弃API 等全栈模块。
* **Add**: I阶段完成——提炼 4 个核心架构洞察（I-01 Protocol分层+protobuf-free关注点分离/I-02 Tensor Protocol层次五张量统一协议/I-03 双向链表+NameAuthority迭代安全与命名治理/I-04 Tape算子录制+Operator Overloading构建器模式），设计知识地图（架构1篇+核心实体3篇+数据结构机制2篇+构建与元数据2篇，共8概念+3示例+4信源）。
* **Add**: E阶段完成——concepts/ 下 8 个概念文档（00-overall-architecture/01-core-entities/02-tensor-protocol/03-type-system/04-doubly-linked-graph/05-serde/06-tape-transform/07-name-metadata），examples/ 下 3 个实战示例（build-graph/graph-traversal/serialize-protobuf），references/ 下 4 个信源登记（core-entities/enums-types/tape-serde/io-metadata），加上 3 个子目录 index.md（无frontmatter）和根 index.md（含okf_version: "0.2" frontmatter）、log.md。
