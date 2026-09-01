---
type: concept
title: "序列化/反序列化：Protobuf 双向转换与多格式支持"
description: "from_proto()/to_proto() 多态分发实现 IR↔Protobuf 双向转换，两阶段图反序列化处理前向引用，TensorProtoTensor 零拷贝包装，支持外部数据和文本格式"
sources:
  references: [../references/tape-serde.md, ../references/io-metadata.md, ../references/core-entities.md]
  facts: [F-048, F-049, F-050, F-051, F-052, F-053, F-054, F-055, F-022]
---

# 序列化/反序列化：Protobuf 双向转换与多格式支持

## 核心理解

onnx-ir 的序列化层（`serde.py`）是唯一依赖 `onnx`（Protobuf）包的模块。它通过 `from_proto()` 和 `to_proto()` 两个多态入口函数，实现 IR 实体与 ONNX Protobuf 对象之间的双向转换。核心设计特点是：(1) 多态分发——根据输入/输出对象的 Protocol 类型自动选择正确的转换函数；(2) 零拷贝优先——TensorProtoTensor 直接包装 proto 内存避免数据复制；(3) 两阶段反序列化——先声明所有节点输出名称再连接引用，处理前向引用和嵌套子图。

## 架构概览

```
┌─────────────────────────────────────────────────────────┐
│                    IR 实体层（_core.py）                  │
│   Model / Graph / Node / Value / Tensor / Attr / ...    │
│              ▲                         │                │
│              │ to_proto()              │ from_proto()   │
│              │ （序列化）               │ （反序列化）    │
├──────────────┼─────────────────────────┼────────────────┤
│              │    serde.py 序列化层     │                │
│  ┌───────────┴───────────┐ ┌───────────┴───────────┐   │
│  │    to_proto() 多态分发 │ │  from_proto() 多态分发 │   │
│  │  (Protocol类型匹配)    │ │  (proto类型判断)       │   │
│  └───────────┬───────────┘ └───────────┬───────────┘   │
│              │                         │                │
│  ┌───────────┴─────────────────────────┴───────────┐   │
│  │           具体序列化/反序列化函数                   │   │
│  │  serialize_model / deserialize_graph / ...       │   │
│  │  TensorProtoTensor（零拷贝包装）                   │   │
│  │  两阶段作用域栈反序列化                           │   │
│  └──────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────┤
│                 ONNX Protobuf 层                        │
│   ModelProto / GraphProto / NodeProto / TensorProto    │
│   AttributeProto / ValueInfoProto / FunctionProto      │
└─────────────────────────────────────────────────────────┘
```

## from_proto()：多态反序列化入口

`from_proto()` 接受一个 ONNX proto 对象，根据其类型分发到对应的反序列化函数（F-048）：

| proto 类型 | 反序列化目标 |
|------------|-------------|
| `ModelProto` | `Model` |
| `GraphProto` | `Graph` |
| `NodeProto` | `Node` |
| `TensorProto` | `TensorProtocol`（Tensor/ExternalTensor/StringTensor/TensorProtoTensor） |
| `AttributeProto` | `Attr` |
| `ValueInfoProto` | `Value` |
| `TypeProto` | `TypeProtocol` |
| `FunctionProto` | `Function` |
| `TensorShapeProto` | `Shape` |
| `TensorShapeProto.Dimension` | `int | SymbolicDim` |
| `list[OperatorSetIdProto]` | `dict[str, int]`（opset_imports） |
| `list[StringStringEntryProto]` | `dict[str, str]`（metadata_props） |

分发基于 Python 的 `isinstance()` 检查，支持传入 proto 对象自动选择正确路径。

## to_proto()：多态序列化入口

`to_proto()` 接受一个 IR 实体（通过 Protocol 接口约束），根据其实现的 Protocol 类型分发（F-049）：

| IR Protocol | 序列化目标 |
|-------------|-----------|
| `ModelProtocol` | `ModelProto` |
| `GraphProtocol` | `GraphProto` |
| `NodeProtocol` | `NodeProto` |
| `TensorProtocol` | `TensorProto` |
| `ValueProtocol` | `ValueInfoProto` |
| `AttributeProtocol`（非ref） | `AttributeProto` |
| `ReferenceAttributeProtocol` | `AttributeProto`（ref_attr） |
| `TypeProtocol` | `TypeProto` |
| `FunctionProtocol` | `FunctionProto` |
| `GraphViewProtocol` | `GraphProto` |

注意 `GraphView` 也可以直接序列化为 `GraphProto`——这使得在不复制 Graph 的情况下创建 Model 成为可能。

## 两阶段图反序列化（F-050）

反序列化 `GraphProto` 是最复杂的操作，因为需要处理：
- **前向引用**：节点的输入可能引用后面才定义的节点输出
- **嵌套子图**：If/Loop 等算子包含子图，子图中的值可以引用外层作用域
- **Initializer 和 Input 的同名冲突**

解决方案是**两阶段反序列化**配合**作用域栈**：

```
_deserialize_graph(graph_proto, scoped_values):

  第一阶段：声明所有节点输出名称
  ┌─────────────────────────────────────────────┐
  │ scoped_values.append({})                    │
  │ for node_proto in graph_proto.node:         │
  │     for i, output_name in enumerate(outputs):│
  │         value = Value(name=output_name)      │
  │         scoped_values[-1][output_name] = value│
  │ # 此时所有名称都已注册，可以处理前向引用      │
  └─────────────────────────────────────────────┘

  第二阶段：反序列化节点体并连接引用
  ┌─────────────────────────────────────────────┐
  │ for node_proto in graph_proto.node:         │
  │     inputs = [lookup_value(name, scoped_values)│
  │               for name in node_proto.input]  │
  │     # lookup 从栈顶向下查找，支持跨作用域引用 │
  │     node = Node(op_type, inputs=inputs, ...) │
  │     # outputs 已在第一阶段创建，设置 producer  │
  └─────────────────────────────────────────────┘
```

`scoped_values` 是一个 `list[dict[str, Value]]`，每进入一层子图就 push 一个新 dict，退出时 pop。值查找从栈顶（当前作用域）向下搜索到栈底（外层作用域），这天然支持子图引用外层图的值。

## 张量反序列化分支（F-051/F-052）

反序列化 `TensorProto` 时按数据位置和类型分支：

```
TensorProto
├── data_location == EXTERNAL
│   └── ExternalTensor(location, base_path, ...)
│       （mmap 按需加载，不立即读入内存）
├── dtype == STRING
│   └── StringTensor(string_data=...)
│       （专门处理字符串，无 raw_data）
└── 其他（默认路径）
    └── TensorProtoTensor(tensor_proto)
        （零拷贝包装 proto，不立即转为 numpy）
```

`TensorProtoTensor` 的零拷贝策略（F-022）：
1. 如果 proto 有 `raw_data` 字段，用 `np.frombuffer(raw_data, dtype=...)` **零拷贝**创建 numpy 视图
2. 如果数据在 typed fields（float_data/int32_data/int64_data 等），按类型分别处理
3. bfloat16/float8/int4/int2 等非标准类型通过 `ml_dtypes` 做 view（不复制数据）

## 文本格式支持（F-053）

除了二进制 Protobuf 格式，还支持 ONNX 文本格式：

```python
# 从文本格式加载
model = ir.from_onnx_text(
    text_string,
    initializers={"W": ir.tensor(np_array, name="W")}  # 可选：附加initializer
)

# 序列化为文本格式
text = ir.to_onnx_text(model, exclude_initializers=True)
```

- `from_onnx_text()`：通过 `onnx.parser.parse_model()` 解析文本，可选接受 initializers 参数将张量附加到对应 Value
- `to_onnx_text()`：通过 `onnx.printer.to_text()` 序列化，`exclude_initializers=True` 可排除初始化器减小输出体积

## IO 层：模型加载与保存（F-054/F-055）

### load()

```python
def load(path: str | os.PathLike) -> Model:
    model_proto = onnx.load(path, load_external_data=False)
    model = from_proto(model_proto)
    external_data.set_base_dir(model.graph, os.path.dirname(path))
    return model
```

关键点：`load_external_data=False` 不让 ONNX C++ 层加载外部数据，而是由 IR 层的 ExternalTensor 通过 mmap 按需加载。

### save()

`save()` 支持外部数据模式：

```python
def save(model: Model, path: str | os.PathLike,
         external_data: str | None = None,
         size_threshold_bytes: int = 0,
         max_shard_size_bytes: int = 0,
         max_workers: int | None = None,
         max_in_flight_bytes: int = 0,
         alignment: int | None = None):
    if external_data is not None:
        # 将大 initializer 转为外部数据文件
        external_data.unload_from_model(
            model.graph,
            location=external_data,
            size_threshold=size_threshold_bytes,
            max_shard_size=max_shard_size_bytes,
            max_workers=max_workers,
            max_in_flight_bytes=max_in_flight_bytes,
            alignment=alignment,
        )
    try:
        model_proto = to_proto(model)
        onnx.save(model_proto, path)
    finally:
        # 恢复原始 initializer 值，保证 model 对象不变
        if external_data is not None:
            external_data.load_to_model(model.graph)
```

外部数据参数说明：

| 参数 | 作用 |
|------|------|
| `size_threshold_bytes` | 超过此大小的 initializer 转为外部数据 |
| `max_shard_size_bytes` | 外部数据分片大小上限（0=不分片） |
| `max_workers` | 并行写入线程数 |
| `max_in_flight_bytes` | 内存中 in-flight 字节上限（流控） |
| `alignment` | 数据对齐偏移（用于 mmap 对齐优化） |

finally 块确保即使序列化失败，model 对象也不会被修改（事务性语义）。
