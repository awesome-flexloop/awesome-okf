---
type: example
title: "SavedModel 转换"
description: "将 TensorFlow SavedModel 目录转换为 ONNX 格式的完整示例，包括 Python API 和命令行两种方式、签名选择、形状指定、动态维度处理"
sources:
  concepts: [../concepts/00-overall-architecture.md, ../concepts/01-conversion-pipeline.md, ../concepts/06-data-layout-types.md]
  references: [../references/convert-entry.md]
---

# SavedModel 转换

## 目标

将 TensorFlow SavedModel 格式（TF2 标准模型保存格式）转换为 ONNX 格式。SavedModel 是 TF2 推荐的模型持久化格式，包含计算图和变量检查点。

## 前置条件

```bash
pip install tensorflow tf2onnx onnx onnxruntime
```

## 方式一：Python API 转换

### 步骤一：准备或获取 SavedModel

```python
import tensorflow as tf
import numpy as np
import tf2onnx
import onnx
import onnxruntime as ort

# 构建并保存一个简单模型（如果你已有 SavedModel 可跳过此步）
def create_and_save_model(save_dir="saved_model_dir"):
    model = tf.keras.Sequential([
        tf.keras.layers.InputLayer(input_shape=(224, 224, 3), name="input"),
        tf.keras.layers.Conv2D(32, 3, activation="relu"),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Conv2D(64, 3, activation="relu"),
        tf.keras.layers.GlobalAveragePooling2D(),
        tf.keras.layers.Dense(10, activation="softmax", name="output"),
    ])
    
    # 使用 tf.function 保存为 SavedModel
    @tf.function(input_signature=[
        tf.TensorSpec([None, 224, 224, 3], tf.float32, name="input")
    ])
    def serve(x):
        return {"predictions": model(x)}
    
    tf.saved_model.save(
        model,
        save_dir,
        signatures={"serving_default": serve}
    )
    print(f"模型已保存到 {save_dir}")
    return model

# 创建并保存
model = create_and_save_model("saved_model_dir")
```

### 步骤二：使用 from_saved_model 转换

```python
# 最简单的转换方式
model_proto, external_storage = tf2onnx.convert.from_saved_model(
    "saved_model_dir",
    opset=15,
    output_path="saved_model.onnx"
)

# 验证
onnx.checker.check_model(model_proto)
print("模型验证通过")
```

### 步骤三：指定签名（多签名模型）

SavedModel 可能包含多个签名（如 serving_default、predict、train 等），使用 `signature` 参数选择：

```python
model_proto, _ = tf2onnx.convert.from_saved_model(
    "saved_model_dir",
    signature="serving_default",  # 选择签名，默认 serving_default
    opset=15,
    output_path="saved_model.onnx"
)

# 查看可用签名
import tensorflow as tf
loaded = tf.saved_model.load("saved_model_dir")
print(f"可用签名: {list(loaded.signatures.keys())}")
```

### 步骤四：处理动态形状

```python
# 指定输入形状（固定 batch 大小）
model_proto, _ = tf2onnx.convert.from_saved_model(
    "saved_model_dir",
    opset=15,
    shape_override={
        "input:0": [1, 224, 224, 3]  # 固定 batch=1
    },
    inputs_as_nchw=["input:0"],      # 图像输入转为 NCHW
    output_path="saved_model_fixed.onnx"
)

# 动态 batch（使用 -1 或 None 表示动态维度）
model_proto, _ = tf2onnx.convert.from_saved_model(
    "saved_model_dir",
    opset=15,
    shape_override={
        "input:0": [-1, 224, 224, 3]  # 动态 batch，固定图像大小
    },
    inputs_as_nchw=["input:0"],
    output_path="saved_model_dynamic.onnx"
)

# 验证动态形状
onnx_model = onnx.load("saved_model_dynamic.onnx")
input_shape = [d.dim_param if d.dim_param else d.dim_value 
               for d in onnx_model.graph.input[0].type.tensor_type.shape.dim]
print(f"输入形状: {input_shape}")  # ['batch', 3, 224, 224] 或 [-1, 3, 224, 224]
```

### 步骤五：对比推理结果

```python
# TF 推理
imported = tf.saved_model.load("saved_model_dir")
predict_fn = imported.signatures["serving_default"]

test_input = np.random.randn(1, 224, 224, 3).astype("float32")
tf_result = predict_fn(tf.constant(test_input))
tf_output = tf_result["predictions"].numpy()

# ONNX Runtime 推理（注意：如果用了 inputs_as_nchw，输入需要是 NCHW）
sess = ort.InferenceSession("saved_model_fixed.onnx")
input_name = sess.get_inputs()[0].name
onnx_input = test_input.transpose(0, 3, 1, 2)  # NHWC → NCHW
onnx_output = sess.run(None, {input_name: onnx_input})[0]

# 对比
np.testing.assert_allclose(tf_output, onnx_output, rtol=1e-4, atol=1e-4)
print("TF 和 ONNX 推理结果一致！")
```

## 方式二：命令行转换

命令行是最快捷的转换方式，不需要写 Python 脚本。

### 基本转换

```bash
# 基本转换
python -m tf2onnx.convert \
  --saved-model saved_model_dir \
  --output model.onnx

# 指定 opset
python -m tf2onnx.convert \
  --saved-model saved_model_dir \
  --output model.onnx \
  --opset 18

# NCHW 布局转换
python -m tf2onnx.convert \
  --saved-model saved_model_dir \
  --output model_nchw.onnx \
  --inputs-as-nchw "input:0" \
  --outputs-as-nchw "predictions:0"
```

### 指定输入形状

```bash
# 固定输入形状（内联形状指定）
python -m tf2onnx.convert \
  --saved-model saved_model_dir \
  --output model.onnx \
  --inputs "input:0[1,224,224,3]"

# 动态 batch
python -m tf2onnx.convert \
  --saved-model saved_model_dir \
  --output model.onnx \
  --inputs "input:0[-1,224,224,3]"

# 重命名输入/输出
python -m tf2onnx.convert \
  --saved-model saved_model_dir \
  --output model.onnx \
  --rename-inputs "image" \
  --rename-outputs "logits"
```

### 大模型转换

```bash
# 大模型（超过 2GB）需要启用外部数据存储
python -m tf2onnx.convert \
  --saved-model large_model_dir \
  --output large_model.onnx \
  --large-model
```

这会生成 `large_model.onnx` 和一个 `.bin` 外部数据文件，部署时需要两个文件放在同一目录。

### Target 平台优化

```bash
# 针对 TensorRT 优化
python -m tf2onnx.convert \
  --saved-model saved_model_dir \
  --output model_trt.onnx \
  --target tensorrt

# 保持 NHWC 布局（某些引擎更适合）
python -m tf2onnx.convert \
  --saved-model saved_model_dir \
  --output model_nhwc.onnx \
  --target nhwc
```

### 其他命令行参数

| 参数 | 说明 |
|------|------|
| `--saved-model PATH` | SavedModel 目录路径 |
| `--output PATH` | 输出 ONNX 文件路径 |
| `--opset N` | 目标 opset 版本 |
| `--inputs NAMES[SHAPES]` | 指定输入名和形状（GraphDef/Checkpoint 格式必须） |
| `--outputs NAMES` | 指定输出名（GraphDef/Checkpoint 格式必须） |
| `--inputs-as-nchw NAMES` | NHWC→NCHW 转置的输入 |
| `--outputs-as-nchw NAMES` | 保持 NCHW 的输出 |
| `--target TARGETS` | 目标平台（逗号分隔） |
| `--custom-ops OPS` | 自定义算子（OpName:domain 格式） |
| `--rename-inputs NAMES` | 重命名输入 |
| `--rename-outputs NAMES` | 重命名输出 |
| `--large-model` | 启用大模型外部存储 |
| `--verbose` | 输出详细日志 |

## 方式三：Checkpoint 转换（TF1 风格）

如果是 TF1 checkpoint（.meta + .data 文件），也可以转换：

```python
# Python API
model_proto, _ = tf2onnx.convert.from_checkpoint(
    "model.ckpt.meta",      # meta 文件路径
    input_names=["input:0"],
    output_names=["output:0"],
    opset=15,
    output_path="from_checkpoint.onnx"
)
```

```bash
# 命令行（必须指定 --inputs 和 --outputs）
python -m tf2onnx.convert \
  --checkpoint model.ckpt.meta \
  --inputs "input:0" \
  --outputs "output:0" \
  --output model.onnx
```

## 要点解析

### from_saved_model 的关键参数

| 参数 | 说明 |
|------|------|
| `model_path` | SavedModel 目录路径 |
| `opset` | 目标 opset 版本（默认 15） |
| `signature` | 签名名（默认 serving_default） |
| `inputs_as_nchw` / `outputs_as_nchw` | 布局转换 |
| `shape_override` | 形状覆盖字典 |
| `target` | 目标平台列表 |
| `large_model` | 大模型外部存储 |
| `custom_ops` / `custom_op_handlers` | 自定义算子 |
| `output_path` | 输出文件路径 |

### SavedModel vs from_keras 区别

| 特性 | from_keras | from_saved_model |
|------|-----------|-----------------|
| 输入 | `tf.keras.Model` 对象 | SavedModel 目录路径 |
| 签名 | 自动处理 | 需指定 signature |
| 具体函数获取 | `_get_concrete_function` 内部处理 | tf_loader 加载 |
| 适用场景 | 训练过程中转换 | 训练完成后的模型转换 |

### 形状推断与指定

不指定形状时，tf2onnx 会自动推断：
1. 从 SavedModel 的 ConcreteFunction 获取输入签名
2. 运行 TF 形状推断
3. 对未确定的维度使用自定义推断

但自动推断可能得到动态维度（None/-1），这对推理部署可能不理想。明确指定 `shape_override` 可以固定形状，使优化器更有效（常量折叠需要静态形状）。

### 常见错误排查

**错误 1："Signature 'serving_default' not found"**

SavedModel 没有默认签名。先检查可用签名：
```python
loaded = tf.saved_model.load("saved_model_dir")
print(list(loaded.signatures.keys()))
```
然后通过 `signature` 参数指定正确的签名名。

**错误 2："Cannot infer shape for tensor XXX"**

形状推断失败。通过 `shape_override` 手动指定输入形状。

**错误 3："Unknown OP: XXX"**

存在不支持的算子。见[自定义算子映射示例](custom-op-mapping.md)。

**错误 4：输出结果不匹配**

1. 检查输入预处理是否一致（归一化、均值等）
2. 检查数据布局（NCHW vs NHWC）
3. 放宽容差（某些算子如 BatchNorm 在不同框架间可能有微小差异）

## 延伸阅读

- [Keras 模型转 ONNX](keras-conversion.md) — 从内存中的 Keras 模型直接转换
- [自定义算子映射](custom-op-mapping.md) — 处理不支持的算子
- [转换流水线详解](../concepts/01-conversion-pipeline.md) — 理解 from_saved_model 内部流程
- [NHWC/NCHW 布局转换](../concepts/06-data-layout-types.md) — 布局转换的原理
- [ONNX 图优化器](../concepts/05-optimizers.md) — 理解形状如何影响优化效果
