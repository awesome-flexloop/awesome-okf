---
type: example
title: "序列化到 Protobuf 与反序列化"
description: "IR Model ↔ ONNX Protobuf 双向转换完整流程——from_proto 加载模型、to_proto 序列化、外部数据加载/卸载、文本格式转换、零拷贝 TensorProtoTensor 策略、mmap 大模型加载"
sources:
  concepts: [../concepts/05-serde.md, ../concepts/02-tensor-protocol.md, ../concepts/00-overall-architecture.md]
  references: [../references/tape-serde.md, ../references/io-metadata.md, ../references/core-entities.md]
---

# 序列化到 Protobuf 与反序列化

## 目标

掌握 onnx-ir 的序列化/反序列化完整流程：从 ONNX 文件加载为 IR Model、IR Model 转为 Protobuf、外部数据管理、文本格式转换、零拷贝策略、以及 mmap 加载大模型的最佳实践。

## 前置知识

- [序列化/反序列化](../concepts/05-serde.md)：from_proto/to_proto 多态分发、两阶段反序列化
- [张量体系](../concepts/02-tensor-protocol.md)：五种 Tensor 类型、TensorProtoTensor 零拷贝
- [IR 整体架构](../concepts/00-overall-architecture.md)：protobuf-free 分层设计

## 基本加载与保存

### 1. 加载 ONNX 模型

```python
import onnx_ir as ir
from onnx_ir import serde

# 方法 1：使用 io.load()（推荐，自动设置外部数据路径）
from onnx_ir._io import load, save

model = load("model.onnx")
print(f"IR version: {model.ir_version}")
print(f"Producer: {model.producer_name}")
print(f"Graph nodes: {len(model.graph)}")
print(f"Inputs: {[v.name for v in model.graph.inputs]}")
print(f"Outputs: {[v.name for v in model.graph.outputs]}")

# 方法 2：手动加载 proto 再转换
import onnx
model_proto = onnx.load("model.onnx", load_external_data=False)
model = serde.from_proto(model_proto)
# 需要手动设置外部数据路径
from onnx_ir import external_data
external_data.set_base_dir(model.graph, ".")
```

`load()` 内部做了三件事（F-054）：
1. `onnx.load(path, load_external_data=False)` 加载 proto（不让 ONNX C++ 层加载外部数据）
2. `serde.from_proto()` 反序列化为 IR Model
3. `external_data.set_base_dir()` 设置外部数据基础目录（用于 mmap 加载）

### 2. 保存 ONNX 模型

```python
from onnx_ir._io import save

# 基本保存（所有数据写入单文件）
save(model, "output.onnx")

# 保存为外部数据模式（大模型推荐）
save(model, "output_external.onnx",
     external_data="output_external.data",  # 外部数据文件路径
     size_threshold_bytes=1024,              # 超过 1KB 的 tensor 转为外部数据
     max_shard_size_bytes=1024*1024*64,     # 每个分片 64MB
     # max_workers=4,                        # 并行写入线程数
     # alignment=4096,                       # mmap 对齐
)
```

外部数据保存的关键特性（F-055）：
- `size_threshold_bytes`：超过阈值的 initializer 转为外部数据
- `max_shard_size_bytes`：外部数据分片大小上限
- `max_workers`：并行写入线程数
- `alignment`：数据对齐偏移（用于 mmap 对齐优化）
- **finally 块保证 model 不变**：序列化后恢复原始 initializer 值

### 3. IR ↔ Protobuf 直接转换

```python
import onnx
import onnx_ir.serde as serde

# IR → Protobuf
model_proto = serde.to_proto(model)
onnx.checker.check_model(model_proto)  # 验证 proto 有效性
onnx.save(model_proto, "output.onnx")

# Protobuf → IR
model_proto2 = onnx.load("model.onnx", load_external_data=False)
model2 = serde.from_proto(model_proto2)
```

`to_proto()` 和 `from_proto()` 不仅支持 Model，还支持所有 IR 实体：

```python
# 单个节点转换
node = ir.Node("Add", inputs=[x, y], outputs=[z])
node_proto = serde.to_proto(node)
node_ir = serde.from_proto(node_proto)

# 单个张量转换
tensor = ir.tensor(np.array([1.0, 2.0], dtype=np.float32))
tensor_proto = serde.to_proto(tensor)

# 单个图转换
graph_proto = serde.to_proto(model.graph)
graph_ir = serde.from_proto(graph_proto)
```

## 张量序列化策略

### TensorProtoTensor：零拷贝包装

加载模型时，普通张量（非外部数据、非字符串）被包装为 `TensorProtoTensor`（F-022），不会立即复制到 numpy 数组：

```python
# 加载模型后，检查 initializer 的类型
for name, value in model.graph.initializers.items():
    tensor = value.const_value
    print(f"{name}: {type(tensor).__name__}")
    # 输出：w1: TensorProtoTensor, w2: ExternalTensor, ...
```

`TensorProtoTensor` 的零拷贝 numpy 转换：

```python
# 当调用 .numpy() 时，如果 proto 有 raw_data：
# 1. 使用 np.frombuffer(raw_data, dtype=dtype) 直接 view proto 内存
# 2. 对 bfloat16/float8/int4/int2 通过 ml_dtypes 做 view（不复制）
# 3. 对 typed field（float_data/int64_data 等）按类型转换

tensor = model.graph.initializers["conv_w"].const_value
arr = tensor.numpy()  # 零拷贝或最小拷贝
print(arr.shape, arr.dtype)
```

### ExternalTensor：mmap 按需加载

如果模型保存为外部数据格式，加载时 initializer 是 `ExternalTensor`，通过 mmap 按需访问（F-016/F-017）：

```python
ext_tensor = model.graph.initializers["large_weight"].const_value
print(type(ext_tensor))  # ExternalTensor
print(ext_tensor.location)  # 外部数据文件中的偏移位置
print(ext_tensor.dtype, ext_tensor.shape)

# 首次访问 .numpy() 触发 mmap
arr = ext_tensor.numpy()  # mmap 整个（或部分）文件

# 生命周期管理
ext_tensor.invalidate()  # 标记数据损坏/删除，后续访问报错
ext_tensor.release()     # 关闭 mmap，释放引用
```

**安全防护**：ExternalTensor 包含三层安全检查：
1. 路径遍历防护（拒绝包含 `..` 的路径）
2. 符号链接 realpath 检查
3. 硬链接检测（`nlink > 1` 拒绝）

### StringTensor：字符串专用

字符串张量不支持 raw_data 和 DLPack，通过 `string_data()` 访问：

```python
str_tensor = model.graph.initializers["labels"].const_value
assert isinstance(str_tensor, ir.StringTensor)
strings = str_tensor.string_data()  # Sequence[bytes]
for s in strings:
    print(s.decode("utf-8"))
```

## 外部数据管理

```python
from onnx_ir import external_data

# 将模型中的大 initializer 卸载到外部数据文件
external_data.unload_from_model(
    model.graph,
    location="weights.data",
    size_threshold=1024,  # 超过 1KB 的 tensor 转为外部
)

# 将外部数据加载回内存
external_data.load_to_model(model.graph)

# 设置外部数据基础目录（加载模型后需要调用）
external_data.set_base_dir(model.graph, "./model_dir/")
```

## 文本格式转换

```python
from onnx_ir import serde

# 序列化为 ONNX 文本格式
text = serde.to_onnx_text(model, exclude_initializers=True)
print(text[:500])  # 查看前500字符

# 从文本格式加载
model_text = '''
<
  ir_version: 7,
  opset_import: [ "" : 13 ]
>
agraph (float[N, 3, 224, 224] x) => (float[N, 1000] y) {
    w = Constant<value = float[64, 3, 7, 7] { ... }>()
    conv = Conv<kernel_shape = [7, 7], pads = [3, 3, 3, 3], strides = [2, 2]>(x, w)
    y = Softmax<axis = 1>(conv)
}
'''
# 注意：实际文本格式需要完整的 tensor 数据
# model = serde.from_onnx_text(model_text)
```

## GraphView 的序列化

`GraphView` 是 Graph 的只读视图，可以直接序列化而不复制图：

```python
view = ir.GraphView(model.graph)
graph_proto = serde.to_proto(view)  # 直接序列化，不复制节点
```

这使得在不修改原图的情况下创建 Model 成为可能。

## 大模型加载最佳实践

```python
# ✅ 推荐：延迟加载策略
model = load("large_model.onnx")
# 此时 initializer 可能是 TensorProtoTensor（零拷贝proto包装）
# 或 ExternalTensor（mmap外存），不占用额外内存

# 只在需要时访问具体权重
for name, value in model.graph.initializers.items():
    tensor = value.const_value
    if isinstance(tensor, ir.TensorProtoTensor):
        # 零拷贝 numpy 视图
        arr = tensor.numpy()
    elif isinstance(tensor, ir.ExternalTensor):
        # mmap 访问，不加载整个权重到内存
        arr = tensor.numpy()
    # arr 是 numpy 数组视图

# ❌ 避免：急切加载所有权重
# for value in model.graph.initializers.values():
#     value.const_value.numpy()  # 触发所有张量加载到内存！
```

### 内存效率对比

| 加载策略 | 内存占用 | 适用场景 |
|----------|---------|---------|
| 默认加载（TensorProtoTensor） | Proto 内存 + 访问时 numpy 视图 | 大多数场景 |
| 外部数据（ExternalTensor） | 仅 mmap 元数据，数据在磁盘 | 大模型（>系统内存） |
| 急切 numpy() | 所有张量复制到内存 | 小模型、需要修改权重 |

### 使用 PackedTensor 节省空间

对于 INT4/INT2 量化模型，可以使用 PackedTensor 存储打包格式：

```python
# 创建打包张量（INT4）
import numpy as np
data_packed = np.packbits(
    np.unpackbits(np.array([1, 2, 3, 15], dtype=np.uint8).reshape(-1, 1) >> 4, axis=1),
    axis=0,
    bitorder="little",
)
packed = ir.PackedTensor(data_packed, dtype=ir.DataType.UINT4, shape=ir.Shape((4,)))
arr = packed.numpy()  # 解包为普通数组
```

## 完整序列化/反序列化 Roundtrip 示例

```python
import numpy as np
import onnx
import onnx_ir as ir
from onnx_ir._io import load, save
import onnx_ir.serde as serde

# === 构建模型 ===
b = ir.Builder({"": 20})
x = ir.val(name="x", shape=ir.Shape((1, 3, 224, 224)),
           type=ir.TensorType(ir.DataType.FLOAT))
w = b.initializer(ir.tensor(np.random.randn(64, 3, 7, 7).astype(np.float32), name="w"))
conv = b.Conv(x, w, kernel_shape=(7, 7), pads=(3, 3, 3, 3), strides=(2, 2))
relu = b.Relu(conv)
pool = b.MaxPool(relu, kernel_shape=(3, 3), pads=(1, 1, 1, 1), strides=(2, 2))

graph = ir.Graph(b.nodes, inputs=[x], outputs=[pool],
                 initializers=dict(b.initializers), opset_imports=b.used_opsets)
graph.sort()
model = ir.Model(graph, ir_version=10, producer_name="roundtrip-test")

# === 保存 ===
save(model, "roundtrip.onnx")

# === 加载 ===
loaded = load("roundtrip.onnx")

# === 验证 ===
assert len(loaded.graph) == len(graph)
assert len(loaded.graph.inputs) == len(graph.inputs)
assert len(loaded.graph.outputs) == len(graph.outputs)

# 检查节点 op_type 一致
for orig_node, loaded_node in zip(graph, loaded.graph):
    assert orig_node.op_type == loaded_node.op_type
    print(f"✓ {orig_node.op_type}")

# 检查权重一致
w_orig = graph.initializers["w"].const_value.numpy()
w_loaded = loaded.graph.initializers["w"].const_value.numpy()
np.testing.assert_allclose(w_orig, w_loaded, rtol=1e-6)
print("✓ Weights match")

# === Protobuf 验证 ===
model_proto = serde.to_proto(loaded)
onnx.checker.check_model(model_proto)
print("✓ ONNX checker passed")

print("Roundtrip successful!")
```

## 关键要点总结

1. **使用 `load()`/`save()`** 而非手动 `onnx.load`/`onnx.save`，它们自动处理外部数据路径
2. **TensorProtoTensor 是默认策略**：零拷贝包装 proto，`numpy()` 时才创建 view
3. **ExternalTensor 用于大模型**：mmap 按需加载，包含三层安全防护
4. **外部数据模式在 finally 中恢复**：`save(external_data=...)` 不会修改原 model
5. **to_proto/from_proto 支持所有实体类型**：不仅是 Model，Node/Tensor/Graph/Value/Attr 都可以单独转换
6. **文本格式用于调试**：`to_onnx_text(exclude_initializers=True)` 查看模型结构
7. **大模型避免急切 numpy()**：TensorProtoTensor/ExternalTensor 的延迟策略可以显著降低内存占用
