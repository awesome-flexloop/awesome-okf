---
type: example
title: "自定义算子映射"
description: "为 tf2onnx 不原生支持的 TF 算子添加自定义转换器，包括 @tf_op 装饰器新 API 和 custom_op_handlers 旧 API 两种方式，以及命令行 --custom-ops 用法"
sources:
  concepts: [../concepts/02-versioned-opset-registry.md, ../concepts/04-graph-internal-api.md, ../concepts/03-graph-rewriting.md]
  references: [../references/opset-mapping.md, ../references/graph-rewriter.md]
---

# 自定义算子映射

## 目标

当 tf2onnx 遇到不认识的 TF 算子时（通常报错 "Unknown OP: XXX"），可以通过自定义算子映射扩展转换能力。本示例展示两种自定义方式：推荐的 `@tf_op` 装饰器新 API，以及兼容旧版的 `custom_op_handlers` 字典 API。

## 场景描述

假设你的模型使用了一个 TF 自定义算子 `MyFusedOp`，它执行 `output = relu(a * b + c)`（即 Fused Mul+Add+Relu）。tf2onnx 不认识这个算子，需要自定义转换器将其映射为 ONNX 算子组合。

## 方式一：@tf_op 装饰器（推荐）

### 步骤一：定义自定义算子处理器

```python
import numpy as np
import tensorflow as tf
import tf2onnx
from tf2onnx.handler import tf_op
from tf2onnx import helper

# 使用 @tf_op 装饰器注册自定义算子处理器
@tf_op("MyFusedOp", domain="com.example")
class MyFusedOp:
    @classmethod
    def version_1(cls, ctx, node, **kwargs):
        """
        将 MyFusedOp(a, b, c) 转换为:
            t = Mul(a, b)
            t = Add(t, c)
            output = Relu(t)
        """
        # 获取输入
        a = node.input[0]
        b = node.input[1]
        c = node.input[2]
        output = node.output[0]
        
        # 获取输入的形状和类型（用于新节点）
        dtype = ctx.get_dtype(a)
        shape = ctx.get_shape(a)
        
        # 创建中间节点名称
        mul_name = ctx.get_unique_name(node.name + "_mul")
        add_name = ctx.get_unique_name(node.name + "_add")
        
        # 创建 Mul 节点
        mul_out = mul_name + ":0"
        ctx.make_node(
            "Mul",
            inputs=[a, b],
            outputs=[mul_out],
            name=mul_name
        )
        ctx.set_dtype(mul_out, dtype)
        ctx.set_shape(mul_out, shape)
        
        # 创建 Add 节点
        add_out = add_name + ":0"
        ctx.make_node(
            "Add",
            inputs=[mul_out, c],
            outputs=[add_out],
            name=add_name
        )
        ctx.set_dtype(add_out, dtype)
        ctx.set_shape(add_out, shape)
        
        # 将输出改为连接到 Relu
        # 修改原节点为 Relu，将 Add 的输出作为输入
        node.type = "Relu"
        node.input[0] = add_out
        # 多余的输入清除
        del node.input[1:]
```

### 步骤二：使用自定义转换器

```python
# 导入自定义模块（触发 @tf_op 装饰器注册）
# （如果定义在同一文件中则不需要额外导入）

# 创建一个包含自定义算子的简单模型用于演示
# 实际场景中你的模型已经包含 MyFusedOp
class MyFusedLayer(tf.keras.layers.Layer):
    def __init__(self):
        super().__init__()
    
    @tf.function(input_signature=[
        tf.TensorSpec([None, 128], tf.float32, name="a"),
        tf.TensorSpec([None, 128], tf.float32, name="b"),
        tf.TensorSpec([128], tf.float32, name="c"),
    ])
    def call(self, a, b, c):
        # 模拟自定义算子（实际中这是你注册的自定义 TF op）
        return tf.nn.relu(a * b + c)

# 保存为 SavedModel（包含自定义算子）
layer = MyFusedLayer()
# 在实际场景中，这里是你真实的含自定义算子的模型
# 我们用标准算子模拟

# 转换时通过 extra_opset 指定自定义 domain 的 opset 版本
model_proto, _ = tf2onnx.convert.from_function(
    layer.call,
    input_signature=[
        tf.TensorSpec([None, 128], tf.float32, name="a"),
        tf.TensorSpec([None, 128], tf.float32, name="b"),
        tf.TensorSpec([128], tf.float32, name="c"),
    ],
    opset=15,
    extra_opset=[("com.example", 1)],  # 注册自定义 domain
    # 新 API 的 @tf_op 不需要传 custom_op_handlers
)

# 验证
import onnx
onnx.checker.check_model(model_proto)
print("自定义算子转换成功！")
```

## 方式二：custom_op_handlers 字典（旧 API）

如果你不想使用装饰器，可以通过 `custom_op_handlers` 字典注册：

```python
from tf2onnx.handler import tf_op

def my_fused_op_handler(ctx, node, **kwargs):
    """
    处理函数签名与 @tf_op 装饰的 version_N 方法相同：
    Args:
        ctx: Graph 对象
        node: 当前 Node 对象
        **kwargs: 额外参数
    """
    a = node.input[0]
    b = node.input[1]
    c = node.input[2]
    
    dtype = ctx.get_dtype(a)
    shape = ctx.get_shape(a)
    
    # 创建 Mul -> Add -> Relu
    mul_name = ctx.get_unique_name(node.name + "_mul")
    mul_out = mul_name + ":0"
    ctx.make_node("Mul", inputs=[a, b], outputs=[mul_out], name=mul_name)
    ctx.set_dtype(mul_out, dtype)
    ctx.set_shape(mul_out, shape)
    
    add_name = ctx.get_unique_name(node.name + "_add")
    add_out = add_name + ":0"
    ctx.make_node("Add", inputs=[mul_out, c], outputs=[add_out], name=add_name)
    ctx.set_dtype(add_out, dtype)
    ctx.set_shape(add_out, shape)
    
    node.type = "Relu"
    node.input[0] = add_out
    del node.input[1:]

# 注册处理器
custom_op_handlers = {
    "MyFusedOp": (my_fused_op_handler, {}),
}

# 转换
model_proto, _ = tf2onnx.convert.from_function(
    layer.call,
    input_signature=[...],
    opset=15,
    custom_op_handlers=custom_op_handlers,
    output_path="model_custom.onnx"
)
```

## 方式三：命令行 --custom-ops（标记未知算子）

如果你只需要让 tf2onnx 将未识别的算子标记为自定义算子（由推理引擎自行处理），而不提供转换器：

```bash
# 将 MyFusedOp 标记为 ai.onnx.converters.tensorflow domain 的自定义算子
python -m tf2onnx.convert \
  --saved-model saved_model_dir \
  --output model.onnx \
  --custom-ops MyFusedOp

# 指定自定义 domain
python -m tf2onnx.convert \
  --saved-model saved_model_dir \
  --output model.onnx \
  --custom-ops "MyFusedOp:com.example"

# 多个自定义算子
python -m tf2onnx.convert \
  --saved-model saved_model_dir \
  --output model.onnx \
  --custom-ops "OpA:com.example,OpB:com.example"
```

使用 `--custom-ops` 时，tf2onnx 不会转换这些算子，而是将它们作为指定 domain 的自定义算子保留在 ONNX 模型中。推理引擎需要支持这些自定义算子才能运行模型。

## 高级：映射到现有 ONNX 算子

很多情况下，TF 算子可以映射到单个现有的 ONNX 算子，只需要改名或设置属性。这是最简单的自定义方式：

### 例子：TF RealDiv → ONNX Div（tf2onnx 内置做法）

```python
# 这就是 tf2onnx 内部处理 RealDiv 的方式
@tf_op("RealDiv", onnx_op="Div")
class RealDiv:
    @classmethod
    def version_6(cls, ctx, node, **kwargs):
        # onnx_op="Div" 自动将 node.type 改为 "Div"
        # opset 6+ 的 Div 支持广播，不需要额外处理
        pass
```

### 例子：带属性设置的映射

```python
@tf_op("MyCustomConv")
class MyCustomConv:
    @classmethod
    def version_11(cls, ctx, node, **kwargs):
        # 映射到 ONNX Conv
        node.type = "Conv"
        # 设置卷积属性
        node.set_attr("kernel_shape", [3, 3])
        node.set_attr("strides", [1, 1])
        node.set_attr("pads", [1, 1, 1, 1])
        # 设置分组卷积
        node.set_attr("group", 1)
```

## 高级：使用 OpTypePattern 做子图重写

如果你的自定义转换涉及模式匹配（在映射前替换子图），需要编写自定义重写器：

```python
from tf2onnx.graph_matcher import OpTypePattern, GraphMatcher

def rewrite_custom_fused_pattern(g, ops):
    """自定义重写器：识别 Mul->Add->Relu 模式并替换"""
    # 定义模式
    mul_pat = OpTypePattern("Mul", name="mul")
    add_pat = OpTypePattern("Add", name="add", inputs=[mul_pat, OpTypePattern("*", name="bias")])
    relu_pat = OpTypePattern("Relu", name="relu", inputs=[add_pat])
    
    matcher = GraphMatcher(relu_pat)
    for match in matcher.match_ops(ops):
        mul = match.get_op("mul")
        add = match.get_op("add")
        relu = match.get_op("relu")
        
        # 执行替换...
        # 这里可以将三个节点替换为单个自定义算子或 ONNX 组合
    
    return ops

# 使用自定义重写器
model_proto, _ = tf2onnx.convert.from_saved_model(
    "saved_model_dir",
    opset=15,
    custom_rewriter=[rewrite_custom_fused_pattern],
)
```

## 自定义处理函数 API 参考

处理函数（无论是 `@tf_op` 的 `version_N` 方法还是 `custom_op_handlers` 中的函数）都可以使用以下 Graph/Node API：

### Graph API（ctx 参数）

| 方法 | 说明 |
|------|------|
| `ctx.make_node(op_type, inputs, outputs, name=None, **attr)` | 创建新节点 |
| `ctx.remove_node(node)` | 删除节点 |
| `ctx.get_shape(tensor_name)` | 获取张量形状 |
| `ctx.set_shape(tensor_name, shape)` | 设置张量形状 |
| `ctx.get_dtype(tensor_name)` | 获取张量数据类型 |
| `ctx.set_dtype(tensor_name, dtype)` | 设置张量数据类型 |
| `ctx.get_unique_name(prefix)` | 生成唯一节点/张量名 |
| `ctx.replace_all_inputs(old_name, new_name)` | 全局替换输入引用 |
| `ctx.copy_node(node, new_name=None)` | 复制节点 |

### Node API（node 参数）

| 属性/方法 | 说明 |
|----------|------|
| `node.type` | 获取/设置算子类型名 |
| `node.name` | 节点名称 |
| `node.input` | 输入张量名列表（可修改） |
| `node.output` | 输出张量名列表（可修改） |
| `node.set_attr(name, value)` | 设置属性 |
| `node.get_attr(name, default=None)` | 获取属性 |
| `node.replace_input(idx, new_name)` | 替换指定位置的输入 |
| `node.skip_conversion = True` | 标记该节点不需要进一步转换 |

## 要点解析

### 新 API vs 旧 API 选择

| 特性 | @tf_op 装饰器（新） | custom_op_handlers（旧） |
|------|-------------------|------------------------|
| 版本支持 | ✅ 支持 version_N 多版本 | ❌ 单版本 |
| 自动注册 | ✅ 导入即注册 | ❌ 需手动传入 |
| domain 支持 | ✅ domain 参数 | ❌ 需要额外处理 |
| onnx_op 改名 | ✅ 装饰器参数 | ❌ 手动设置 |
| 推荐程度 | ⭐ 推荐 | 兼容旧代码 |

### 自定义 domain 的 opset 声明

使用 `@tf_op(domain="com.example")` 时，必须在转换时通过 `extra_opset` 声明该 domain 使用的 opset 版本：

```python
extra_opset=[("com.example", 1)]  # 声明 com.example domain 使用 version 1
```

这会在生成的 ONNX 模型中添加对应的 opset_import 条目。

### 调试自定义转换器

1. **启用详细日志**：设置环境变量 `TF_CPP_MIN_LOG_LEVEL=0` 或在代码中添加 `logging.basicConfig(level=logging.DEBUG)`
2. **使用 large_model 模式保存中间结果**：可以分阶段保存 ONNX 模型检查
3. **onnx.checker**：转换后运行 `onnx.checker.check_model()` 验证模型结构
4. **数值验证**：对比 TF 和 ONNX 推理结果确保转换正确

### 常见错误

**错误 1：节点创建后未设置 shape/dtype**

新创建的节点必须设置输出的 shape 和 dtype，否则后续优化器可能出错：

```python
# ❌ 错误：缺少 set_shape/set_dtype
ctx.make_node("Mul", inputs=[a, b], outputs=[mul_out], name=mul_name)

# ✅ 正确
ctx.make_node("Mul", inputs=[a, b], outputs=[mul_out], name=mul_name)
ctx.set_shape(mul_out, ctx.get_shape(a))
ctx.set_dtype(mul_out, ctx.get_dtype(a))
```

**错误 2：忘记清除多余输入**

如果将原节点改为单输入算子（如 Relu），必须清除多余输入：

```python
node.type = "Relu"
node.input[0] = add_out
del node.input[1:]  # 清除原来的 b, c 输入
```

**错误 3：节点名不唯一**

使用 `ctx.get_unique_name(prefix)` 生成名称，避免与现有节点重名。

## 延伸阅读

- [装饰器驱动的版本化算子注册表](../concepts/02-versioned-opset-registry.md) — 理解 @tf_op 的工作原理
- [内部 Graph API 设计](../concepts/04-graph-internal-api.md) — 完整的 Graph/Node API 参考
- [图重写与模式匹配](../concepts/03-graph-rewriting.md) — 如何编写自定义重写器
- [信源登记簿：算子版本化注册表](../references/opset-mapping.md) — 算子注册的源码级参考
- [Keras 模型转 ONNX](keras-conversion.md) — 基础转换流程
- [SavedModel 转换](savedmodel-conversion.md) — 命令行自定义算子用法
