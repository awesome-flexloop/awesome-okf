---
type: bundle
title: ONNX IR Python 参考实现
okf_version: "0.2"
---


# ONNX 纯 Python IR（onnx-ir）知识库

本知识包是 [ONNX](https://onnx.ai) 生态中纯 Python 中间表示实现 `onnx-ir`（v1.1.0，BSD-3-Clause 许可证）的系统化中文源码教程，基于 `src/onnx_ir/` 源码深度阅读生成，覆盖从 protobuf-free 分层架构到张量体系、图结构、序列化、Tape 图变换的完整知识体系。所有内容均溯源至源码核心模块（`_core.py`/`_enums.py`/`_tape.py`/`serde.py`/`_io.py`/`_linked_list.py`/`_name_authority.py`/`_metadata.py`），遵循 [OKF v0.2 规范](../../../meta/okf-spec/index.md)。

onnx-ir 是 ONNX 格式的纯 Python 中间表示，核心设计特点是 IR 层完全 protobuf-free——序列化/反序列化作为独立层次通过 Protocol 多态分发实现，五种张量实现（内存/mmap/字符串/延迟/亚字节打包）统一 TensorProtocol 协议，双向链表支持迭代中安全增删，Tape/Builder 提供声明式图构建 API。

## 架构与核心实体（concepts/）

* [IR 整体架构：protobuf-free 分层设计](concepts/00-overall-architecture.md) — 纯 Python IR 层独立于 Protobuf、六大子模块导出、21个公开实体类、关注点分离与零拷贝优先设计原则。
* [核心实体：Model/Graph/Node/Value](concepts/01-core-entities.md) — Value 作为图连接中心（producer/uses 双向引用）、Node 受控变异 API、Graph 双向链表存储与拓扑排序、Model opset 委托、Function Graph 委托模式、Attr 统一属性。
* [张量体系：五种 Tensor 与零拷贝/延迟/mmap 设计](concepts/02-tensor-protocol.md) — TensorBase 统一协议，Tensor(零拷贝内存)/ExternalTensor(mmap+三层安全防护)/StringTensor/LazyTensor(thunk)/PackedTensor(亚字节打包)/TensorProtoTensor(protobuf零拷贝)。
* [类型系统：DataType 枚举、形状 Dimension、AttributeType](concepts/03-type-system.md) — 27种 DataType（INT2~COMPLEX128/BFLOAT16/FLOAT8系列）、15种 AttributeType、SymbolicDim sympy 符号运算、Shape 冻结与维度合并、递归类型层次。

## 数据结构与机制（concepts/）

* [双向链表图结构：DoublyLinkedSet 迭代安全与 NameAuthority 命名](concepts/04-doubly-linked-graph.md) — 循环双向链表 O(1) 增删、_LinkBox erase 语义保证迭代器安全、NameAuthority 单调计数器永不释放、Graph 容器角色标记一致性。
* [序列化/反序列化：Protobuf 双向转换与多格式支持](concepts/05-serde.md) — from_proto/to_proto 11+种类型多态分发、两阶段作用域栈反序列化处理前向引用、TensorProtoTensor np.frombuffer 零拷贝、外部数据分片并行写入。
* [Tape 图变换：算子录制、Builder 魔术方法与运算符重载](concepts/06-tape-transform.md) — Tape.op() 节点录制、Builder.__getattr__ 伪方法调用、_magic_handler ClassVar 动态注入实现算术运算符重载、graph_like 绑定模式。
* [名称管理、元数据存储与废弃 API](concepts/07-name-metadata.md) — NameAuthority 命名治理、MetadataStore invalidate 失效标记、meta（临时分析）vs metadata_props（可序列化）双轨元数据、Input()→ir.val() 迁移、Attr* 工厂函数。

## 实战示例（examples/）

* [使用 IR 构建计算图](examples/build-graph.md) — 从零构建 CNN 计算图（Conv→BN→Relu→MaxPool→Flatten→Gemm→Softmax）：Builder 录制、Initializer 注册、Graph/Model 构造、magic_handler 运算符重载风格。
* [图遍历与变换](examples/graph-traversal.md) — 顺序迭代、前驱/后继查询、子图递归、安全增删、replace_all_uses_with SSA 替换、常量折叠 Pass 完整实现、收集-应用模式。
* [序列化到 Protobuf 与反序列化](examples/serialize-protobuf.md) — load/save、to_proto/from_proto 多态转换、TensorProtoTensor 零拷贝、ExternalTensor mmap、外部数据分片、文本格式、大模型内存优化、roundtrip 验证。

## 信源登记簿（references/）

* [_core.py 核心实体：Model/Graph/Node/Value/Tensor 系列](references/core-entities.md) — `src/onnx_ir/_core.py`（~5300行）源码事实登记：张量体系、形状系统、Value/Node/Graph/Model/Function、Attr、TypeProtocol、双轨元数据。
* [_enums.py 类型枚举：DataType 与 AttributeType](references/enums-types.md) — `src/onnx_ir/_enums.py`（~410行）源码事实登记：27种 DataType、15种 AttributeType、numpy 映射、位宽表、非原生类型 ml_dtypes。
* [_tape.py/serde.py/tape.py：图变换录制与 Protobuf 序列化](references/tape-serde.md) — `src/onnx_ir/_tape.py`（Tape/Builder）、`src/onnx_ir/serde.py`（多态序列化/反序列化/零拷贝/TensorProtoTensor）、`src/onnx_ir/tape.py`（公开模块）。
* [_io.py/_metadata.py/_linked_list.py/_name_authority.py：IO、元数据、链表与命名](references/io-metadata.md) — `_io.py`（load/save/外部数据）、`_metadata.py`（MetadataStore）、`_linked_list.py`（DoublyLinkedSet）、`_name_authority.py`（NameAuthority）。

## 信任与生命周期说明

* **status 判定依据**：全部 15 个内容文档（8 个概念 + 3 个示例 + 4 个信源登记）均 `status: stable`。内容基于对 onnx-ir（`onnx_ir` 包 v1.1.0，`src/onnx_ir/` 目录）核心模块的逐文件阅读与事实提取（63 条源码事实 F-001~F-063），经 seven-concepts 方法论 R→I→E 三阶段流程生成。
* **stale_after 解释**：统一设置为 `2027-12-31`。onnx-ir 核心架构（protobuf-free 分层/Tensor Protocol 层次/DoublyLinkedSet/Tape Builder/serde 多态分发）自 0.x 版本以来设计稳定，v1.1.0 已确立核心 API；该日期作为针对未来大版本（如 2.x）的保守重新评估节点。
* **核验链路**：事实来源于对源码的静态分析，洞察基于事实提炼，示例代码基于验证过的 API 编写。

本知识包共收录 15 个内容文档（8 个概念 + 3 个示例 + 4 个信源登记），另含 3 个子目录 index.md 与根 index.md、log.md。

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
