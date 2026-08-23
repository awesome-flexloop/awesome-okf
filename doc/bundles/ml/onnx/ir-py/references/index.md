---
type: reference_index
title: "ir-py API 参考索引"
description: "ir-py API 参考文档导航"
generated: true
verified: grep
status: stable
stale_after: 2026-12-31
---

# ir-py API 参考


信源登记簿

本目录登记本知识包所有内容据以派生的 onnx-ir 源码信源。所有概念文档和示例文档的 `sources` 字段均指向此目录下的信源登记条目。信源基于 onnx-ir（`onnx_ir` 包，v1.1.0）的核心模块源码分析。

* [_core.py 核心实体：Model/Graph/Node/Value/Tensor 系列](core-entities.md) — `src/onnx_ir/_core.py`（~5300行）：TensorBase 抽象基类与五种张量、SymbolicDim/Shape 形状系统、Value/Node/Graph/Model/Function 图结构、Attr 属性、TypeProtocol 类型层次、WithArithmeticMethods 算术混入、双轨元数据、便捷构造器。
* [_enums.py 类型枚举：DataType 与 AttributeType](enums-types.md) — `src/onnx_ir/_enums.py`（~410行）：AttributeType 15种属性类型、DataType 27种数据类型（FLOAT/DOUBLE/BFLOAT16/FLOAT8/INT4/INT2等）、numpy↔ONNX dtype 映射、位宽表、分类查询方法。
* [_tape.py/serde.py/tape.py：图变换录制与 Protobuf 序列化](tape-serde.md) — `src/onnx_ir/_tape.py`（~240行）Tape/Builder 图构建录制器、`src/onnx_ir/serde.py`（~1200行）from_proto/to_proto 多态序列化、TensorProtoTensor 零拷贝包装、两阶段图反序列化、文本格式支持。
* [_io.py/_metadata.py/_linked_list.py/_name_authority.py：IO、元数据、链表与命名](io-metadata.md) — `src/onnx_ir/_io.py`（~200行）load/save 与外部数据、`_metadata.py`（~50行）MetadataStore 失效标记、`_linked_list.py`（~280行）DoublyLinkedSet 双向链表、`_name_authority.py`（~70行）NameAuthority 自动唯一命名。
