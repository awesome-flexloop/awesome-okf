---
type: reference
title: "_tape.py/serde.py/tape.py：图变换录制与 Protobuf 序列化"
description: "onnx_ir._tape 模块 Tape/Builder 图构建录制器、onnx_ir.serde 模块 IR↔Protobuf 双向序列化、onnx_ir.tape 公开模块信源登记"
sources:
  - path: "src/onnx_ir/_tape.py"
    facts: [F-056, F-057]
  - path: "src/onnx_ir/serde.py"
    facts: [F-022, F-048, F-049, F-050, F-051, F-052, F-053]
  - path: "src/onnx_ir/tape.py"
    facts: [F-058]
---

# _tape.py/serde.py/tape.py：图变换录制与 Protobuf 序列化

## 信源概述

| 信源 | 类型 | 行数 | 职责 |
|------|------|------|------|
| `src/onnx_ir/_tape.py` | Python 实现 | ~240行 | `Tape` 图构建录制器、`Builder` 魔术方法算子调用 |
| `src/onnx_ir/serde.py` | Python 实现 | ~1200行 | `from_proto()`/`to_proto()` 多态序列化入口、两阶段图反序列化、TensorProtoTensor 零拷贝包装、文本格式支持 |
| `src/onnx_ir/tape.py` | Python 实现 | ~15行 | 公开模块：仅导出 Tape，重设 `__module__` 路径 |

## 关键事实登记

### F-056：Tape 图构建录制器

**信源**：`src/onnx_ir/_tape.py` L20-L205

`Tape` 是图构建录制器，收集 `op()` 创建的节点和 `initializer()` 创建的初始化值到内部列表：

```python
class Tape:
    def __init__(self, opset_imports: dict[str, int] | None = None,
                 graph_like: Graph | Function | None = None):
        self._nodes: list[Node] = []
        self._initializers: list[TensorProtocol] = []
        self._used_opsets: dict[str, int] = {}
        self._graph_like = graph_like
```

关键 API：
- `op(op_type, /, *inputs, outputs=None, _domain="", _version=None, **attributes)`：创建单输出节点并录制，返回单输出 Value
- `op_multi_out(op_type, /, *inputs, outputs=1, _domain="", _version=None, **attributes)`：创建多输出节点，返回输出 Value 序列
- `initializer(value: TensorProtocol, name: str | None = None)`：注册初始化值
- `nodes` 属性：返回已录制节点列表
- `initializers` 属性：返回已录制初始化值列表
- `used_opsets`：记录所有用到的 `(domain, version)` 集合
- 当 `graph_like` 绑定到 Graph/Function 时，节点自动添加到图中

### F-057：Builder 魔术方法算子调用

**信源**：`src/onnx_ir/_tape.py` L208-L242

`Builder` 继承 `Tape`，通过 `__getattr__` 魔术方法实现算子调用 API：

```python
class Builder(Tape):
    def __getattr__(self, op_type: str):
        # 将 builder.Add(...) 转为 self.op("Add", ...)
        # 将 builder.MatMul(...) 转为 self.op("MatMul", ...)
        def op_caller(*args, _domain="", _version=None, _outputs=None, **kwargs):
            if _outputs is not None:
                return self.op_multi_out(op_type, *args, outputs=_outputs,
                                         _domain=_domain, _version=_version, **kwargs)
            return self.op(op_type, *args, _domain=_domain, _version=_version, **kwargs)
        return op_caller
```

支持的 kwargs：
- `_domain`：算子域（默认空串即 ai.onnx）
- `_version`：算子版本
- `_outputs`：int 时创建对应数量输出，Sequence 时设置输出名称

### F-058：tape.py 公开模块

**信源**：`src/onnx_ir/tape.py` L9-L15

```python
from onnx_ir._tape import Tape
Tape.__module__ = __name__  # 重设模块路径使 isinstance 等检查通过
__all__ = ["Tape"]
```

公开模块仅导出 `Tape` 类（Builder 是内部扩展类，不公开导出）。

### F-048：from_proto() 多态反序列化入口

**信源**：`src/onnx_ir/serde.py` L126-L190

`from_proto()` 是重载的多态入口，根据 proto 类型分发到对应反序列化函数，支持类型：
- `ModelProto` → deserialize model
- `GraphProto` → deserialize graph
- `NodeProto` → deserialize node
- `TensorProto` → deserialize tensor
- `AttributeProto` → deserialize attribute
- `ValueInfoProto` → deserialize value
- `TypeProto` → deserialize type
- `FunctionProto` → deserialize function
- `TensorShapeProto` / `Dimension` → deserialize shape
- `OperatorSetIdProto` 序列 → deserialize opset imports
- `StringStringEntryProto` 序列 → deserialize metadata props

### F-049：to_proto() 多态序列化入口

**信源**：`src/onnx_ir/serde.py` L258-L308

`to_proto()` 通过 Protocol 类型判断分发，支持：
- `ModelProtocol` → serialize_model
- `GraphProtocol` → serialize_graph
- `NodeProtocol` → serialize_node
- `TensorProtocol` → serialize_tensor
- `ValueProtocol` → serialize_value
- `AttributeProtocol`（非 ref）→ serialize_attribute
- `ReferenceAttributeProtocol` → serialize_reference_attribute
- `TypeProtocol` → serialize_type_into
- `FunctionProtocol` → serialize_function
- `GraphViewProtocol` → serialize_graph

### F-022：TensorProtoTensor 零拷贝包装

**信源**：`src/onnx_ir/serde.py` L311-L556

`TensorProtoTensor` 直接包装 `onnx.TensorProto`，改进了 `onnx.numpy_helper.to_array`：
- 优先使用 `raw_data` 字段配合 `np.frombuffer` 零拷贝
- 按不同 data field（int32_data/int64_data/float_data/double_data/uint64_data/string_data）分别处理
- 自动处理 bfloat16/float8/int4/int2 等类型的 view 转换

### F-050：两阶段图反序列化与作用域栈

**信源**：`src/onnx_ir/serde.py` L763-L886

`_deserialize_graph()` 使用作用域栈 `scoped_values: list[dict[str, Value]]` 处理嵌套子图的值引用：
1. **第一阶段**：声明所有 node output 名称（处理前向引用和子图跨作用域引用）
2. **第二阶段**：反序列化节点体，连接输入输出引用

### F-051/F-052：张量反序列化分支

**信源**：`src/onnx_ir/serde.py` L1150-L1179

反序列化张量时按 data_location 和 dtype 分支：
- `EXTERNAL` data_location → `ExternalTensor`
- STRING 类型 → `StringTensor`
- 其余 → `TensorProtoTensor`（零拷贝包装 proto）

`deserialize_tensor()` 接受 `base_path` 参数用于 ExternalTensor 的 base_dir 设置。

### F-053：文本格式支持

**信源**：`src/onnx_ir/serde.py` L193-L255

- `from_onnx_text()`：通过 `onnx.parser.parse_model()` 解析文本格式，可选接受 initializers 参数
- `to_onnx_text()`：通过 `onnx.printer.to_text()` 序列化，支持 `exclude_initializers` 选项
