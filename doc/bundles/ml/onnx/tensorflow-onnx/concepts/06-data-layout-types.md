---
type: concept
title: "NHWC/NCHW 布局转换、数据类型系统与 Target 适配"
description: "TF 默认 NHWC 与 ONNX 默认 NCHW 的数据布局转换策略、TF dtype 到 ONNX dtype 映射、动态形状处理、广播语义差异，以及 Target 平台类型限制适配"
sources:
  references: [../references/convert-entry.md, ../references/graph-rewriter.md]
  facts: [F-036, F-037, F-038, F-040, F-044]
---

# NHWC/NCHW 布局转换、数据类型系统与 Target 适配

## 核心理解

TensorFlow 和 ONNX 在数据布局、类型系统和算子语义上存在系统性差异。tf2onnx 必须在转换过程中处理这些差异，才能生成正确的 ONNX 模型。最显著的差异是**数据布局**（NHWC vs NCHW），其次是**类型映射**和**广播语义**，最后是**Target 平台适配**（为特定推理引擎插入必要的类型转换）。

## 数据布局：NHWC vs NCHW

### 两种布局的区别

| 维度顺序 | 框架 | 含义 | 内存排列（以 224×224 RGB 图为例） |
|----------|------|------|------|
| **NHWC** | TensorFlow 默认 | Batch-Height-Width-Channel | 逐像素排列：[R1,G1,B1, R2,G2,B2, ...] |
| **NCHW** | ONNX 默认 | Batch-Channel-Height-Width | 逐通道排列：[R1,R2,...,R50176, G1,G2,...,B50176] |

对于 4D 张量（如图像特征图）：
- NHWC：shape = `[N, H, W, C]`
- NCHW：shape = `[N, C, H, W]`

### 布局转换策略

tf2onnx 提供两种布局处理策略：

#### 策略一：输入端插入 Transpose（默认）

默认情况下，tf2onnx 在输入端插入 Transpose 节点将 NHWC 转为 NCHW，在所有算子以 NCHW 布局计算后，输出端再插入 Transpose 转回 NHWC（如果用户指定了 `outputs_as_nchw` 则不转回）。

```
用户输入 (NHWC)
    │
    ▼
Transpose(perm=[0,3,1,2])  ← NHWC → NCHW
    │
    ▼
ONNX 算子 (全部 NCHW)
    │
    ▼
Transpose(perm=[0,2,3,1])  ← NCHW → NHWC（可选）
    │
    ▼
用户输出 (NHWC)
```

**相关参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `inputs_as_nchw` | list[str] | 需要在输入端从 NHWC 转为 NCHW 的输入张量名列表 |
| `outputs_as_nchw` | list[str] | 输出保持 NCHW（不插入回转 Transpose）的张量名列表 |

```python
# Python API
model_proto, _ = tf2onnx.convert.from_keras(
    model,
    inputs_as_nchw=["input:0"],     # 输入转为 NCHW
    outputs_as_nchw=["output:0"],   # 输出保持 NCHW
    opset=15
)
```

```bash
# 命令行
python -m tf2onnx.convert --saved-model model_dir \
  --output model.onnx \
  --inputs-as-nchw "input:0" \
  --outputs-as-nchw "output:0"
```

transpose_inputs/transpose_outputs 函数（F-038）要求张量形状为 rank 4，使用固定的 perm 参数：
- NHWC → NCHW：`perm = [0, 3, 1, 2]`
- NCHW → NHWC：`perm = [0, 2, 3, 1]`

#### 策略二：Channels Last（NHWC 直通）

当 `target` 包含 `nhwc` 或 `channels_last` 时，tf2onnx 不插入布局转换，保持 NHWC 布局。适用于支持 NHWC 的推理引擎（如某些版本的 TensorRT、Android NNAPI）。

此时 `late_rewriters` 中的 `rewrite_channels_last` 会激活，调整算子属性以适配 NHWC 布局。

### TransposeOptimizer 的布局优化

输入端插入的 Transpose 节点会被 TransposeOptimizer 尝试向后传播或消除：

1. **Conv 算子融合**：如果 Transpose 后面是 Conv，优化器可能将 Transpose 吸收到 Conv 的 kernel 重排中
2. **冗余消除**：如果后续算子不关心布局（如 Element-wise 算子在两侧都有 Transpose 时），可以消除
3. **连续 Transpose 合并**：两个连续 Transpose 的 perm 矩阵相乘，恒等则消除

经过优化后，最终模型中的 Transpose 数量远少于输入端插入的数量。

## 数据类型系统

### TF dtype → ONNX dtype 映射

TensorFlow 和 ONNX 都基于 protobuf 枚举表示数据类型，但枚举值不同，需要映射：

| TF dtype | ONNX dtype (TensorProto) | 说明 |
|----------|-------------------------|------|
| `tf.float32` | `FLOAT` (1) | 32位浮点 |
| `tf.float64` | `DOUBLE` (11) | 64位浮点 |
| `tf.float16` | `FLOAT16` (10) | 16位浮点 |
| `tf.bfloat16` | `BFLOAT16` (16) | Brain 16位浮点（opset 18+） |
| `tf.int32` | `INT32` (6) | 32位有符号整数 |
| `tf.int64` | `INT64` (7) | 64位有符号整数 |
| `tf.int8` | `INT8` (3) | 8位有符号整数 |
| `tf.uint8` | `UINT8` (2) | 8位无符号整数 |
| `tf.int16` | `INT16` (5) | 16位有符号整数 |
| `tf.uint16` | `UINT16` (4) | 16位无符号整数 |
| `tf.bool` | `BOOL` (9) | 布尔值 |
| `tf.complex64` | `COMPLEX64` (14) | 64位复数 |
| `tf.complex128` | `COMPLEX128` (15) | 128位复数 |
| `tf.string` | `STRING` (8) | 字符串 |

### 类型不兼容处理

并非所有 TF 类型都能直接映射到 ONNX：
- `tf.resource`、`tf.variant`：TF 特有类型，在转换时被过滤掉（如 HashTable 资源句柄）
- `tf.bfloat16`：需要 opset 18+ 或通过 `--custom-ops` 处理
- `tf.qint8`/`tf.quint8`：量化类型，通过 QDQ 重写器处理

Target 平台可能不支持某些类型（如 Windows ML 不支持 float16 计算），late_rewriters 会在必要时自动插入 Cast 节点转换类型。

## 动态形状处理

### 形状指定

ONNX 模型可以包含动态形状（未知维度），tf2onnx 通过多种方式处理：

**方式一：shape_override 参数**

```python
model_proto, _ = tf2onnx.convert.from_saved_model(
    "saved_model_dir",
    shape_override={"input:0": [1, 224, 224, 3]}  # 完全固定形状
)
```

**方式二：命令行 --inputs 内联形状**

```bash
python -m tf2onnx.convert --saved-model model_dir \
  --output model.onnx \
  --inputs "input:0[-1,224,224,3]"  # -1 表示 batch 维度动态
```

`-1` 表示该维度未知/动态，ONNX 模型中该维度为 `dim_param`（符号维度）而非固定值。

**方式三：自动形状推断**

不指定形状时，tf2onnx 通过三阶段形状推断确定张量形状：

### 三阶段形状推断

形状推断在 `graphs_from_tf` 阶段执行（F-036, F-037）：

```
1. shape_override 应用 → 用户指定的形状优先
2. infer_shape_for_graph → TF 原生形状推断
   ├─ 利用 TF 运行时推断
   ├─ 基于关键假设迭代：
   │   ├─ Merge 输出与输入同形状（至少同 rank）
   │   ├─ tf.cond 两个分支输出同 rank
   │   └─ tf.while_loop 循环变量不改变 rank
   └─ 直到没有形状更新为止
3. infer_shape_for_graph_legacy → 自定义推断规则
   └─ 对仍有 None 形状的节点使用启发式规则推断
```

动态维度（None/-1）会保留到 ONNX 模型中，推理时由推理引擎确定实际大小。

## 广播语义差异

TensorFlow 和 ONNX 在不同 opset 版本中的广播（broadcasting）语义不同：

| 版本 | 广播方式 | 说明 |
|------|----------|------|
| TF | NumPy-style broadcasting | 始终支持 multi-directional broadcast |
| ONNX opset 1-5 | 显式 broadcast 属性 | Add/Sub/Mul 等算子有 `broadcast` 属性和 `axis` 属性 |
| ONNX opset 6+ | Multi-directional broadcast | 原生支持 NumPy-style 广播，无 broadcast 属性 |

这意味着：
- 目标 opset < 6 时，BroadcastOp 的 version_1 处理器需要设置 `broadcast=1` 并可能插入广播节点
- 目标 opset ≥ 6 时，version_6 处理器为空（DirectOp），ONNX 原生支持广播

```python
# BroadcastOp 的多版本处理器
@tf_op("Add", "Sub", "Mul")
class BroadcastOp:
    @classmethod
    def version_1(cls, ctx, node, **kwargs):
        """opset 1-5：需要设置 broadcast 属性"""
        bcast = cls._should_broadcast(ctx, node)
        if bcast:
            node.set_attr("broadcast", 1)
            # 可能需要显式插入 Broadcast 节点
    
    @classmethod
    def version_6(cls, ctx, node, **kwargs):
        """opset 6+：原生支持 multi-directional broadcast"""
        pass  # 无需特殊处理
```

## Target 平台适配

tf2onnx 通过 `--target` 参数支持多个部署目标，每个 target 激活特定的 late_rewriter 来处理平台限制：

| Target | 适用平台 | 适配内容 |
|--------|----------|----------|
| （空/默认） | 通用 ONNX Runtime | 无特殊适配 |
| `rs4` | Windows ML RS4 | 兼容旧版 Windows ML 的类型/算子限制 |
| `rs5` | Windows ML RS5 | `rewrite_incomplete_type_support_rs5` 自动插入 Cast |
| `rs6` | Windows ML RS6 | `rewrite_incomplete_type_support_rs6` 自动插入 Cast |
| `caffe2` | Caffe2 | Caffe2 特定的算子/属性调整 |
| `tensorrt` | TensorRT | TensorRT 友好的图优化（如融合模式） |
| `nhwc`/`channels_last` | NHWC 推理引擎 | `rewrite_channels_last` 保持 NHWC 布局 |

### Target 类型支持适配（rs5/rs6）

Windows ML 的不同版本不支持某些 ONNX 数据类型（如 float16 计算、int64 输入）。`rewrite_incomplete_type_support` 系列重写器会：

1. 遍历图中所有节点
2. 检查算子的输入类型是否在目标平台支持列表中
3. 如果不支持，在输入前插入 Cast 节点转为支持的类型
4. 在输出后插入 Cast 节点转回原类型

例如，Windows ML 不支持 int64 作为 Gather 的索引输入，重写器自动插入 `Cast(to=INT32)` 和 `Cast(to=INT64)`。

### POSSIBLE_TARGETS 常量

```python
# constants.py
POSSIBLE_TARGETS = ["rs4", "rs5", "rs6", "caffe2", "tensorrt", "nhwc"]
DEFAULT_TARGET = []  # 默认无 target
```

## 形状与类型传播

在转换过程中，Graph 对象通过 `shapes` 和 `_dtypes` 字典维护每个张量的形状和类型信息：

```python
# 新创建节点时必须设置输出的形状和类型
new_node = g.make_node("Transpose", inputs=[input_name], outputs=[output_name], perm=[0,3,1,2])
g.set_shape(output_name, new_shape)      # NHWC [N,H,W,C] → NCHW [N,C,H,W]
g.set_dtype(output_name, input_dtype)   # Transpose 不改变数据类型
```

形状信息在 TransposeOptimizer、ConstFoldOptimizer 等优化器中至关重要——没有正确的形状信息，优化器无法判断 Transpose 是否可以消除、常量是否可以折叠。

## 关联概念

- [tf2onnx 整体架构](00-overall-architecture.md) — 理解布局转换在流水线中的位置
- [转换流水线详解](01-conversion-pipeline.md) — 理解 transpose_inputs/transpose_outputs 的执行时机
- [图重写与模式匹配](03-graph-rewriting.md) — 理解 late_rewriters 如何进行 Target 适配
- [内部 Graph API 设计](04-graph-internal-api.md) — 理解 set_shape/set_dtype API
- [ONNX 图优化器](05-optimizers.md) — 理解 TransposeOptimizer 如何优化布局转换
- [Keras 模型转 ONNX 示例](../examples/keras-conversion.md) — 实战 inputs_as_nchw 使用
- [SavedModel 转换示例](../examples/savedmodel-conversion.md) — 实战 shape_override 使用
