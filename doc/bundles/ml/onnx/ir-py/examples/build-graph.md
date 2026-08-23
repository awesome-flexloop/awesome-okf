---
type: example
title: "使用 IR 构建计算图"
description: "从零开始用 onnx-ir 构建一个完整的卷积神经网络计算图——创建输入/权重/偏置、使用 Builder 录制算子、构造 Graph 和 Model、序列化为 ONNX protobuf"
sources:
  concepts: [../concepts/00-overall-architecture.md, ../concepts/01-core-entities.md, ../concepts/06-tape-transform.md, ../concepts/03-type-system.md]
  references: [../references/core-entities.md, ../references/tape-serde.md, ../references/enums-types.md]
---

# 使用 IR 构建计算图

## 目标

从零开始使用 onnx-ir 构建一个简单的卷积神经网络计算图（Conv → BatchNorm → Relu → MaxPool → Flatten → Gemm → Softmax），演示 Value 创建、Initializer 注册、Builder 算子录制、Graph 构造和 Model 序列化的完整流程。

## 前置知识

- [IR 整体架构](../concepts/00-overall-architecture.md)：protobuf-free 分层设计
- [核心实体 Model/Graph/Node/Value](../concepts/01-core-entities.md)：实体关系模型
- [Tape 图变换](../concepts/06-tape-transform.md)：Builder 魔术方法算子调用
- [类型系统](../concepts/03-type-system.md)：DataType/Shape/SymbolicDim

## 完整代码

### 步骤 1：导入模块和创建 Builder

```python
import numpy as np
import onnx_ir as ir

# 定义 opset 导入（ai.onnx domain, version 20）
opset_imports = {"": 20}

# 创建 Builder（Tape 的子类，支持方法调用风格）
b = ir.Builder(opset_imports)
```

### 步骤 2：创建图输入

```python
# 输入张量：batch=动态, channels=3, height=224, width=224
batch = ir.SymbolicDim("N")
x = ir.val(
    name="input",
    shape=ir.Shape((batch, 3, 224, 224)),
    type=ir.TensorType(ir.DataType.FLOAT),
)
```

### 步骤 3：注册权重和偏置（Initializers）

```python
# Conv 权重：[64, 3, 7, 7]（out_channels, in_channels, kH, kW）
conv_w = ir.tensor(
    np.random.randn(64, 3, 7, 7).astype(np.float32),
    name="conv_w",
)
conv_w_val = b.initializer(conv_w)

# Conv 偏置：[64]
conv_b = ir.tensor(
    np.zeros(64, dtype=np.float32),
    name="conv_b",
)
conv_b_val = b.initializer(conv_b)

# BatchNorm 参数
bn_scale = ir.tensor(np.ones(64, dtype=np.float32), name="bn_scale")
bn_bias = ir.tensor(np.zeros(64, dtype=np.float32), name="bn_bias")
bn_mean = ir.tensor(np.zeros(64, dtype=np.float32), name="bn_mean")
bn_var = ir.tensor(np.ones(64, dtype=np.float32), name="bn_var")

bn_s = b.initializer(bn_scale)
bn_b = b.initializer(bn_bias)
bn_m = b.initializer(bn_mean)
bn_v = b.initializer(bn_var)

# 全连接层权重和偏置
fc_w = ir.tensor(
    np.random.randn(1000, 64 * 56 * 56).astype(np.float32) * 0.01,
    name="fc_w",
)
fc_b = ir.tensor(np.zeros(1000, dtype=np.float32), name="fc_b")
fc_w_val = b.initializer(fc_w)
fc_b_val = b.initializer(fc_b)
```

### 步骤 4：使用 Builder 录制算子

```python
# Conv + BN + Relu + MaxPool
conv_out = b.Conv(
    x, conv_w_val, conv_b_val,
    kernel_shape=(7, 7),
    pads=(3, 3, 3, 3),
    strides=(2, 2),
)

bn_out = b.BatchNormalization(
    conv_out, bn_s, bn_b, bn_m, bn_v,
    epsilon=1e-5,
    momentum=0.9,
)

relu_out = b.Relu(bn_out)

pool_out = b.MaxPool(
    relu_out,
    kernel_shape=(3, 3),
    pads=(1, 1, 1, 1),
    strides=(2, 2),
)

# Flatten：将 [N, 64, 56, 56] 展平为 [N, 64*56*56]
flatten_out = b.Flatten(pool_out, axis=1)

# 全连接层（Gemm）
fc_out = b.Gemm(flatten_out, fc_w_val, fc_b_val, alpha=1.0, beta=1.0)

# Softmax 输出
output = b.Softmax(fc_out, axis=1)
```

### 步骤 5：构建 Graph 和 Model

```python
# 构造计算图
graph = ir.Graph(
    b.nodes,
    inputs=[x],
    outputs=[output],
    initializers=dict(b.initializers),  # name→Value 映射
    opset_imports=b.used_opsets,
    name="SimpleCNN",
)

# 拓扑排序（确保节点按依赖顺序排列）
graph.sort()

# 构造模型
model = ir.Model(
    graph,
    ir_version=10,
    producer_name="onnx-ir-example",
    producer_version="0.1",
)
```

### 步骤 6：序列化为 ONNX 格式并保存

```python
import onnx_ir.serde as serde
import onnx

# IR → Protobuf
model_proto = serde.to_proto(model)

# 检查模型有效性
onnx.checker.check_model(model_proto)

# 保存到文件
onnx.save(model_proto, "simple_cnn.onnx")

print(f"模型已保存到 simple_cnn.onnx")
print(f"节点数量: {len(graph)}")
print(f"输入: {[v.name for v in graph.inputs]}")
print(f"输出: {[v.name for v in graph.outputs]}")
```

## 使用 Tape 而非 Builder 的等价写法

如果不使用 Builder 的魔术方法，可以直接用 `Tape.op()`：

```python
tape = ir.Tape(opset_imports)

# 显式指定 op_type 字符串
conv_out = tape.op("Conv", x, conv_w_val, conv_b_val,
                   kernel_shape=(7, 7), pads=(3, 3, 3, 3), strides=(2, 2))
relu_out = tape.op("Relu", conv_out)
# ...
```

效果完全相同，只是写法更冗长。

## 使用 _magic_handler 的运算符重载风格

通过注入 magic_handler，可以实现类似 PyTorch 的表达式风格：

```python
# 定义录制 handler
def make_handler(tape):
    def handler(op_type, self, other):
        if not isinstance(other, ir.Value):
            other = ir.tensor(np.array(other, dtype=np.float32))
            other = tape.initializer(other)
        return tape.op(op_type, self, other)
    return handler

b = ir.Builder(opset_imports)
ir.set_value_magic_handler(make_handler(b))

x = ir.val(name="x", dtype=ir.DataType.FLOAT)
w = b.initializer(ir.tensor(weight_np, name="w"))
bias = b.initializer(ir.tensor(bias_np, name="b"))

# 运算符自动录制算子！
y = (x @ w) + bias  # MatMul + Add
# 等价于：
# matmul_out = b.MatMul(x, w)
# y = b.Add(matmul_out, bias)
```

## 关键要点总结

1. **Builder 是推荐的图构建方式**：通过 `builder.OpName(...)` 方法调用自动录制节点
2. **Initializer 必须显式注册**：使用 `b.initializer(tensor)` 注册权重，Tape 不会自动识别常量
3. **Value 是连接中心**：所有算子的输入输出都是 Value 对象，它们自动维护 producer/uses 关系
4. **graph.sort() 进行拓扑排序**：构建完图后建议调用 sort() 确保节点顺序正确
5. **to_proto() 序列化**：serde 层将 IR 对象转为 ONNX ModelProto，可用 onnx.checker 验证
6. **多输出算子用 _outputs 参数**：`outputs = b.Split(x, _outputs=3)` 返回多个 Value
