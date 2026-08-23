---
type: example
title: "Keras 模型转 ONNX"
description: "将 tf.keras.Model 转换为 ONNX 格式的完整示例，包括 Sequential 和 Functional API 模型、inputs_as_nchw 布局转换、opset 选择、模型验证"
sources:
  concepts: [../concepts/00-overall-architecture.md, ../concepts/01-conversion-pipeline.md, ../concepts/06-data-layout-types.md]
  references: [../references/convert-entry.md]
---

# Keras 模型转 ONNX

## 目标

将 TensorFlow Keras 模型（`tf.keras.Model`）转换为 ONNX 格式，支持 Sequential 和 Functional API 两种建模方式，并正确处理数据布局转换。

## 前置条件

```bash
pip install tensorflow tf2onnx onnx onnxruntime
```

- TensorFlow ≥ 2.13
- Python 3.10-3.12
- 推荐 opset 15（默认）或更高

## 示例一：Sequential 模型转换

### 训练一个简单模型

```python
import tensorflow as tf
import tf2onnx
import onnx
import onnxruntime as ort
import numpy as np

# 1. 构建 Sequential 模型
model = tf.keras.Sequential([
    tf.keras.layers.InputLayer(input_shape=(28, 28, 1), name="input"),
    tf.keras.layers.Conv2D(32, 3, activation="relu"),
    tf.keras.layers.MaxPooling2D(),
    tf.keras.layers.Conv2D(64, 3, activation="relu"),
    tf.keras.layers.MaxPooling2D(),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(10, activation="softmax", name="output"),
])

model.compile(optimizer="adam",
              loss="sparse_categorical_crossentropy",
              metrics=["accuracy"])

# （可选）训练模型
# (x_train, y_train), _ = tf.keras.datasets.mnist.load_data()
# x_train = x_train.reshape(-1, 28, 28, 1).astype("float32") / 255.0
# model.fit(x_train, y_train, epochs=1)
```

### 转换为 ONNX

```python
# 2. 转换为 ONNX（最简单的方式）
model_proto, external_tensor_storage = tf2onnx.convert.from_keras(
    model,
    opset=15,                    # ONNX opset 版本，默认 15
    output_path="mnist_cnn.onnx" # 直接保存到文件
)

# 验证模型
onnx_model = onnx.load("mnist_cnn.onnx")
onnx.checker.check_model(onnx_model)
print("ONNX 模型验证通过")
print(f"IR 版本: {onnx_model.ir_version}")
print(f"Opset 导入:")
for opset in onnx_model.opset_import:
    print(f"  domain='{opset.domain}' version={opset.version}")
```

### 对比推理结果

```python
# 3. 对比 TF 和 ONNX 推理结果
test_input = np.random.randn(1, 28, 28, 1).astype("float32")

# TF 推理
tf_output = model.predict(test_input, verbose=0)

# ONNX Runtime 推理
sess = ort.InferenceSession("mnist_cnn.onnx")
input_name = sess.get_inputs()[0].name
onnx_output = sess.run(None, {input_name: test_input})[0]

# 检查一致性
np.testing.assert_allclose(tf_output, onnx_output, rtol=1e-5, atol=1e-5)
print("TF 和 ONNX 推理结果一致！")
print(f"TF 输出:  {tf_output[0][:5]}")
print(f"ONNX 输出: {onnx_output[0][:5]}")
```

## 示例二：Functional API 模型 + NCHW 布局

图像模型通常需要在 ONNX 中使用 NCHW 布局（ONNX Runtime 的 CPU/CUDA EP 在 NCHW 下性能更好）。使用 `inputs_as_nchw` 参数自动插入布局转换。

```python
# 1. 构建 Functional API 模型（注意：输入仍然是 NHWC）
inputs = tf.keras.Input(shape=(224, 224, 3), name="input_rgb")
x = tf.keras.layers.Conv2D(64, 7, strides=2, padding="same", activation="relu")(inputs)
x = tf.keras.layers.MaxPooling2D(3, strides=2, padding="same")(x)
x = tf.keras.layers.Conv2D(128, 3, padding="same", activation="relu")(x)
x = tf.keras.layers.GlobalAveragePooling2D()(x)
outputs = tf.keras.layers.Dense(1000, activation="softmax", name="predictions")(x)

model = tf.keras.Model(inputs=inputs, outputs=outputs)

# 2. 转换为 ONNX，自动处理 NHWC→NCHW 布局转换
# 使用 inputs_as_nchw 指定哪些输入需要转为 NCHW
# 使用 outputs_as_nchw 指定哪些输出保持 NCHW（不回转 NHWC）
model_proto, _ = tf2onnx.convert.from_keras(
    model,
    opset=15,
    inputs_as_nchw=["input_rgb:0"],     # 输入转为 NCHW
    outputs_as_nchw=["predictions:0"],  # 输出保持 NCHW（分类输出不受布局影响）
    output_path="simple_resnet.onnx"
)

# 验证
onnx_model = onnx.load("simple_resnet.onnx")
onnx.checker.check_model(onnx_model)

# 3. ONNX Runtime 推理时使用 NCHW 输入
sess = ort.InferenceSession("simple_resnet.onnx")
# 注意：ONNX 模型输入是 NCHW 格式！
input_name = sess.get_inputs()[0].name
input_shape = sess.get_inputs()[0].shape
print(f"ONNX 输入形状: {input_shape}")  # 应为 [None, 3, 224, 224] (NCHW)

# NCHW 输入（注意 permute）
nhwc_input = np.random.randn(1, 224, 224, 3).astype("float32")
nchw_input = nhwc_input.transpose(0, 3, 1, 2)  # NHWC → NCHW
onnx_output = sess.run(None, {input_name: nchw_input})[0]
print(f"ONNX 输出形状: {onnx_output.shape}")  # [1, 1000]
```

## 示例三：不保存文件，直接获取 ModelProto

```python
# 转换但不保存到文件，在内存中操作
model_proto, external_storage = tf2onnx.convert.from_keras(
    model,
    opset=18,          # 使用更高 opset
    # 不指定 output_path 则不保存文件
)

# model_proto 是 onnx.ModelProto 对象
print(f"模型输入: {[i.name for i in model_proto.graph.input]}")
print(f"模型输出: {[o.name for o in model_proto.graph.output]}")
print(f"节点数量: {len(model_proto.graph.node)}")

# 之后可以手动保存
onnx.save(model_proto, "model_v18.onnx")
```

## 要点解析

### from_keras 的参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `model` | tf.keras.Model | 必填 | 要转换的 Keras 模型 |
| `opset` | int | PREFERRED_OPSET (15) | 目标 ONNX opset 版本 |
| `input_signature` | list | None | 输入签名（legacy keras 可能需要） |
| `inputs_as_nchw` | list[str] | None | 需要转为 NCHW 的输入名列表 |
| `outputs_as_nchw` | list[str] | None | 保持 NCHW 的输出名列表 |
| `target` | list[str] | None | 目标平台（rs5/rs6/caffe2/tensorrt/nhwc） |
| `custom_ops` | dict | None | 自定义算子映射 |
| `custom_op_handlers` | dict | None | 旧 API 自定义算子处理器 |
| `custom_rewriter` | list | None | 自定义重写器列表 |
| `shape_override` | dict | None | 输入形状覆盖 |
| `large_model` | bool | False | 启用大模型外部张量存储 |
| `output_path` | str | None | 输出文件路径，不指定则不保存 |
| `extra_opset` | list[tuple] | None | 自定义 domain 的 opset 列表，如 `[("com.example", 1)]` |

### TF 版本兼容

from_keras 内部处理 TF 版本差异：
- **TF < 2.16**：使用 `trace_model_call` 追踪模型前向传播
- **TF ≥ 2.16**：回退到 `tf.function` 方式获取 concrete function
- **Legacy keras**：支持独立 `keras` 包（非 `tf.keras`）

### 为什么需要 inputs_as_nchw？

TensorFlow 模型默认使用 NHWC 数据布局，但大多数 ONNX 推理引擎（ONNX Runtime CPU/CUDA、TensorRT 等）在 NCHW 布局下性能更优。`inputs_as_nchw` 做的事情：

1. 在模型输入端插入 `Transpose(perm=[0,3,1,2])` 节点，将 NHWC 输入转为 NCHW
2. 模型内部所有算子以 NCHW 计算
3. 除非指定 `outputs_as_nchw`，否则在输出端再插入 `Transpose(perm=[0,2,3,1])` 转回 NHWC
4. TransposeOptimizer 会尝试优化这些 Transpose 节点

### 模型验证必做步骤

转换后务必验证：

```python
# 1. 结构验证
onnx.checker.check_model(model_proto)

# 2. 数值验证（对比 TF 和 ONNX 输出）
for _ in range(5):  # 多次随机输入
    x = np.random.randn(1, *model.input_shape[1:]).astype("float32")
    tf_out = model.predict(x, verbose=0)
    ort_out = sess.run(None, {input_name: x})[0]
    np.testing.assert_allclose(tf_out, ort_out, rtol=1e-4, atol=1e-4)
```

## 常见问题

### Q: 转换报错 "Unknown OP: XXX"

说明某个 TF 算子没有内置转换器。解决方案：
1. 检查是否有拼写错误或使用了非常见算子
2. 尝试升级 tf2onnx 到最新版本
3. 使用 `--custom-ops` 或自定义 `@tf_op` 注册自定义转换器（见[自定义算子映射示例](custom-op-mapping.md)）

### Q: 转换成功但推理结果不一致

1. 检查数据布局：如果使用了 `inputs_as_nchw`，ONNX 输入必须是 NCHW 格式
2. 检查数据类型：确保输入 dtype 与模型期望一致
3. 放宽容差：`rtol=1e-3` 对于 float16 或量化模型是可以接受的

### Q: 模型输入名带 ":0" 后缀

TF 张量名格式为 `name:index`，如 `input:0`。tf2onnx 通常会自动处理，但在指定 `inputs_as_nchw` 或 `shape_override` 时需要使用完整的张量名（含 `:0`）。

## 延伸阅读

- [SavedModel 转换](savedmodel-conversion.md) — 转换已保存的 SavedModel 目录
- [自定义算子映射](custom-op-mapping.md) — 为不支持的 TF 算子添加自定义转换器
- [转换流水线详解](../concepts/01-conversion-pipeline.md) — 理解 from_keras 内部的六阶段流程
- [NHWC/NCHW 布局转换](../concepts/06-data-layout-types.md) — 深入理解数据布局处理
