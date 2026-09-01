---
type: concept
title: "IR 整体架构：protobuf-free 分层设计"
description: "onnx-ir 的核心设计理念——纯 Python IR 层完全独立于 Protobuf，序列化/反序列化作为独立层次通过 Protocol 多态分发实现双向转换"
sources:
  references: [../references/core-entities.md, ../references/tape-serde.md, ../references/io-metadata.md]
  facts: [F-001, F-002, F-004, F-048, F-049]
---

# IR 整体架构：protobuf-free 分层设计

## 核心理解

onnx-ir（`onnx_ir` 包，v1.1.0）是 ONNX 格式的纯 Python 中间表示实现。它与 ONNX 官方 Python API 的根本区别在于：**IR 核心层完全不依赖 Protobuf**。`_core.py` 中定义的实体类（Model/Graph/Node/Value/Tensor 等）不包含任何 `to_onnx`/`from_protobuf` 方法，序列化/反序列化作为独立层次（`serde.py`）通过 Protocol 多态分发实现双向转换。

这种设计使 IR 层既可用作 ONNX 的原生 Python 表示，也可独立用于图构建、优化 Pass、教学演示等非 Protobuf 场景。

## 分层架构

```
┌─────────────────────────────────────────────────────────────┐
│                     便捷 API 层（convenience）                │
│   tensor() / node() / val() 顶层便捷构造器                    │
│   Input() 废弃函数（v0.1.9 起 → ir.val()）                   │
├─────────────────────────────────────────────────────────────┤
│                     图构建层（Tape/Builder）                  │
│   Tape.op() 录制节点  │  Builder.__getattr__ 魔术方法调用     │
│   WithArithmeticMethods._magic_handler 运算符重载注入        │
├─────────────────────────────────────────────────────────────┤
│                     IR 核心层（_core.py）★ protobuf-free     │
│  ┌────────────┐  ┌────────┐  ┌───────┐  ┌────────────────┐ │
│  │ Model      │  │ Graph  │  │ Node  │  │ Value          │ │
│  │ (opset/    │  │ (双向  │  │ (域/  │  │ (producer/    │ │
│  │  functions)│  │  链表) │  │  属性)│  │  uses/元数据)  │ │
│  └────────────┘  └────────┘  └───────┘  └────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Tensor 体系（TensorBase 抽象基类）                       │ │
│  │  Tensor(内存) │ ExternalTensor(mmap) │ StringTensor     │ │
│  │  LazyTensor(thunk) │ PackedTensor(亚字节打包)           │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────┐  ┌────────┐  ┌───────┐  ┌────────────────┐ │
│  │ Type系统   │  │ Shape/ │  │ Attr  │  │ Function       │ │
│  │ (Tensor/   │  │ Symbol-│  │(属性/ │  │ (Graph委托+    │ │
│  │  Sequence/ │  │ icDim) │  │ RefAttr)│  RefAttr参数)   │ │
│  │  Optional) │  │        │  │       │  │                │ │
│  └────────────┘  └────────┘  └───────┘  └────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                  数据结构层（独立模块）                       │
│   DoublyLinkedSet（双向链表O(1)增删）                         │
│   NameAuthority（自动唯一命名）                               │
│   MetadataStore（临时分析元数据+失效标记）                     │
├─────────────────────────────────────────────────────────────┤
│                  序列化层（serde.py）★ 唯一依赖 onnx          │
│   from_proto() 多态反序列化（11+种类型分发）                  │
│   to_proto()   多态序列化（Protocol 匹配分发）                │
│   TensorProtoTensor（零拷贝 proto 包装）                      │
│   两阶段图反序列化（作用域栈处理前向引用）                     │
│   from_onnx_text()/to_onnx_text()（文本格式）                │
├─────────────────────────────────────────────────────────────┤
│                  IO 层（_io.py / external_data）             │
│   load()/save()（mmap 外部数据、分片、并行写入）              │
└─────────────────────────────────────────────────────────────┘
```

## 模块导出

`onnx_ir` 包公开导出六大子模块（F-001/F-004）：

| 子模块 | 职责 |
|--------|------|
| `serde` | 序列化/反序列化（唯一依赖 onnx/protobuf 的模块） |
| `traversal` | 图遍历工具 |
| `convenience` | 便捷构造器（`tensor()`/`node()`/`val()`） |
| `external_data` | 外部数据管理（加载/卸载/set_base_dir） |
| `tape` | Tape 图构建录制器 |
| `schemas` | ONNX schema 查询 |

公开导出的 IR 实体类（21个）：
- 张量：`Tensor`, `ExternalTensor`, `StringTensor`, `LazyTensor`, `PackedTensor`
- 形状/类型：`SymbolicDim`, `Shape`, `TensorType`, `OptionalType`, `SequenceType`, `SparseTensorType`, `TypeAndShape`
- 图实体：`Value`, `Attr`, `RefAttr`, `Node`, `Function`, `Graph`, `GraphView`, `Model`

## 关注点分离的设计决策

### 为什么 protobuf-free？

一般 ONNX 工具库（如 onnx 官方 Python API）中 `TensorProto`/`GraphProto` 既是存储格式也是操作对象，IR 和 Protobuf 耦合在一起。这导致：

1. **版本耦合**：IR 逻辑必须随 protobuf schema 升级而变更
2. **性能开销**：所有操作都需要经过 protobuf 对象的序列化/反序列化
3. **扩展性差**：难以添加非标准的张量类型（如延迟求值张量、mmap 张量）

onnx-ir 的反直觉设计：反序列化时不立即将 TensorProto 转为内存 numpy 数组，而是用 `TensorProtoTensor` 延迟包装——通过 `raw_data` + `np.frombuffer` 实现零拷贝 numpy 化。这虽然增加了一层间接，但实现了：

- **零拷贝加载**：`np.frombuffer` 直接 view proto 内存
- **Protobuf 版本无关性**：IR 层不感知 proto 版本变化
- **多存储策略统一**：内存/mmap/延迟/打包/proto 包装五种张量实现同一 Protocol

### 为什么禁止 pathlib？

`_core.py` L11 开发者注释明确禁止导入 `pathlib`：

```python
# NOTE: Do not import pathlib here—it's slow. Use os.path methods.
```

这是一个微观性能决策，在大规模图操作中避免不必要的模块开销。

## 关键设计原则总结

| 原则 | 实现方式 | 信源 |
|------|----------|------|
| protobuf-free | 核心层无 `to_onnx`/`from_protobuf`，serde 独立 | F-002 |
| Protocol 多态 | `from_proto`/`to_proto` 按 Protocol 类型分发 | F-048/F-049 |
| 零拷贝优先 | Tensor 构造零拷贝、TensorProtoTensor frombuffer | F-013/F-022 |
| 迭代安全 | DoublyLinkedSet 双向链表支持遍历中增删 | F-044-F-046 |
| 受控变异 | Node inputs/outputs 不可直接赋值，Graph remove(safe=True) | F-031/F-037 |
| 双轨元数据 | meta（临时）vs metadata_props（序列化） | F-059/F-060 |
