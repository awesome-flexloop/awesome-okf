---
type: concept
title: "图重写与模式匹配：子图重写先于单算子映射"
description: "tf2onnx 图重写机制：OpTypePattern 树形模式匹配、rewriter 函数签名约定、预处理重写器分类、late_rewriters 的 target 条件激活，以及为什么子图重写必须先于单算子映射"
sources:
  references: [../references/graph-rewriter.md]
  facts: [F-027, F-028, F-029, F-030, F-042]
  insights: [I-002]
---

# 图重写与模式匹配：子图重写先于单算子映射

## 核心理解

图重写是 tf2onnx 转换流水线中复杂度最高的阶段，也是最容易被忽视的阶段。直觉上模型转换就是"算子 A 映射为算子 B"，但实际上 **大部分 TF 算子在 ONNX 中不是单个算子，而是多个算子的组合**（如 FusedBatchNorm、LSTMCell、Conv2D+BiasAdd+Relu 融合模式）。这些复合算子必须先用图模式匹配识别，然后替换为 ONNX 等效子图，才能进入单算子映射阶段。

**核心原则**：子图重写（Rewriter）→ 单算子映射（Mapper），顺序不可颠倒。

## 为什么重写必须在映射之前？

考虑 TF 的 `FusedBatchNormV3` 算子：
- 在 TF 中，它是一个单独的算子（执行 BatchNorm 计算 + 可能的激活融合）
- 在 ONNX 中，没有直接对应的单算子（opset 9+ 有 `BatchNormalization`，但语义不完全一致）
- 如果直接进入 Mapper 阶段，找不到对应的 ONNX 算子，转换失败

重写器的作用是在映射之前，将这类 TF 复合算子（或算子组合）替换为 ONNX 可表达的形式：
1. 识别 TF 中由多个小算子组成的复合模式（如 LSTM 展开的 20+ 个算子）
2. 将其替换为单个 ONNX 算子（如 `LSTM`）或等效子图
3. 被替换的节点标记 `skip_conversion = True`，Mapper 阶段跳过

## OpTypePattern：树形模式匹配器

图重写的核心是 `OpTypePattern` 类，它实现了**树形结构的子图模式匹配**。

### 模式定义语法

```python
from tf2onnx.graph_matcher import OpTypePattern, GraphMatcher

# 单个算子匹配
relu_pattern = OpTypePattern("Relu")

# 多算子树形模式：Conv -> BiasAdd -> Relu
conv_pattern = OpTypePattern("Conv", name="conv")
bias_pattern = OpTypePattern("BiasAdd", name="bias",
                              inputs=[conv_pattern, OpTypePattern("Const")])
relu_pattern = OpTypePattern("Relu", name="relu",
                              inputs=[bias_pattern])

# 使用 GraphMatcher 执行匹配
matcher = GraphMatcher(relu_pattern)
matches = matcher.match_ops(g.get_nodes())
for match in matches:
    conv_node = match.get_op("conv")
    bias_node = match.get_op("bias")
    relu_node = match.get_op("relu")
    # 执行替换...
```

### 模式语法详解

| 语法 | 含义 | 示例 |
|------|------|------|
| `"OpType"` | 精确匹配单个算子类型 | `OpTypePattern("Relu")` |
| `"*"` | 通配符，匹配任意算子类型 | `OpTypePattern("*")` |
| `"A\|B\|C"` | 多类型选择，匹配其中任意一个 | `OpTypePattern("Relu\|Relu6")` |
| `inputs=[...]` | 指定输入子模式（嵌套定义树结构） | `OpTypePattern("Add", inputs=[pattern_a, pattern_b])` |
| `name="xxx"` | 给模式节点命名，匹配后通过 name 提取对应节点 | `OpTypePattern("Conv", name="conv")` |
| `allow_reorder=True` | 允许输入顺序重排（用于可交换算子） | `OpTypePattern("Add", allow_reorder=True)` |

### 匹配结果：MatchResult

`GraphMatcher.match_ops()` 返回 `MatchResult` 列表，每个 MatchResult 包含：

```python
class MatchResult:
    def get_op(self, name):
        """通过 pattern 中的 name 获取匹配到的 Node"""
        ...
    def get_ops(self):
        """获取所有匹配到的 Node"""
        ...
```

## Rewriter 函数签名与执行框架

### 统一的 rewriter 函数签名

所有重写器函数遵循统一签名：

```python
def rewrite_xxx(g, ops):
    """
    Args:
        g: Graph 对象（可以创建/删除/修改节点）
        ops: 当前节点列表
    Returns:
        new_ops: 修改后的节点列表
    """
    # 1. 定义模式
    pattern = OpTypePattern(...)
    matcher = GraphMatcher(pattern)
    # 2. 匹配并替换
    for match in matcher.match_ops(ops):
        # 获取匹配节点
        target_node = match.get_op("target")
        # 创建替换节点
        new_node = g.make_node("OnnxOp", inputs=..., outputs=...)
        # 替换输入引用
        g.replace_all_inputs(target_node.output[0], new_node.output[0])
        # 删除旧节点（标记为跳过）
        target_node.skip_conversion = True
    return ops  # 返回修改后的 ops 列表
```

### run_rewriters：重写器执行框架

```python
def run_rewriters(g, ops, rewriters, name="rewriter"):
    """
    顺序执行重写器列表，对主图和子图递归应用。
    """
    for rewrite_func in rewriters:
        ops = rewrite_func(g, ops)
        # 递归处理子图（If/Loop/Scan 的 body）
        for subgraph_name, subgraph in g.contained_graphs.items():
            sub_ops = subgraph.get_nodes()
            rewrite_func(subgraph, sub_ops)
    # Debug 模式下检查图完整性
    if g.debug:
        g.check_integrity()
    return ops
```

**关键机制**：
1. **顺序执行**：重写器按列表顺序执行，前一个重写器的输出是后一个的输入
2. **子图递归**：重写器自动应用到所有 contained_graphs（控制流算子的子图）
3. **完整性检查**：debug 模式下验证图的输入输出连接一致性
4. **迭代稳定**：重写器可能改变图结构，但不影响后续重写器（因为操作的是 Graph 对象）

## 预处理重写器分类

预处理重写器（pre-rewriters）共 20+ 个，按功能可以分为以下几类：

### 1. 常量折叠类

| 重写器 | 功能 |
|--------|------|
| `rewrite_constant_fold` | 使用 numpy 折叠 Add/Mul/Cast/ConcatV2/Pack/Range 等常量表达式 |

这是三层常量折叠的第二层（TF 层面之后，ONNX 优化器之前）。

### 2. 融合算子拆分/转换类

| 重写器 | 功能 |
|--------|------|
| `rewrite_fused_ops` | 拆分 TF 融合算子为基本算子组合 |
| `rewrite_quantize_and_dequantize` | 处理 QDQ 量化模式 |
| `rewrite_gemm` | 识别 MatMul+BiasAdd 模式为 ONNX GEMM |

### 3. 卷积相关重写

| 重写器 | 功能 |
|--------|------|
| `rewrite_conv_dilations` | 处理膨胀卷积（atrous convolution） |
| `rewrite_conv2d_with_pad` | 合并 Conv2D 和 Pad 为带 padding 属性的 Conv |
| `rewrite_biasadd_with_conv2d` | 融合 Conv2D+BiasAdd 模式 |

### 4. RNN/序列模型重写

| 重写器 | 功能 |
|--------|------|
| LSTM 重写器 | 识别 TF LSTMCell 展开子图（~20个算子），替换为 ONNX LSTM 单算子 |
| GRU 重写器 | 识别 TF GRUCell 展开子图，替换为 ONNX GRU 单算子 |

这是最复杂的重写器之一——TF 的 RNN 单元在图中被展开为大量基础算子（Multiply、Add、Sigmoid、Tanh 等），重写器需要匹配这些复杂模式并替换为单个 ONNX RNN 算子。

### 5. 归一化/激活重写

| 重写器 | 功能 |
|--------|------|
| `rewrite_layer_normalization` | 识别 LayerNorm 子图 |
| `rewrite_leakyrelu` | LeakyReLU 激活转换 |
| `rewrite_thresholded_relu` | ThresholdedReLU 转换 |
| `rewrite_dropout` | Dropout 模式处理 |

### 6. 布局/形状重写

| 重写器 | 功能 |
|--------|------|
| `rewrite_transpose` | 转置优化（消除冗余 Transpose） |
| `rewrite_flatten` | Flatten 算子转换 |
| `rewrite_ragged_variant_shape` | RaggedTensor 形状处理 |

### 7. 随机数生成重写

| 重写器 | 功能 |
|--------|------|
| `rewrite_random_uniform` | RandomUniform 转换 |
| `rewrite_random_normal` | RandomNormal 转换 |

### 8. 其他

| 重写器 | 功能 |
|--------|------|
| `rewrite_eye` | Eye 矩阵生成转换 |

## 后处理重写器：Target 条件激活

与预处理重写器不同，后处理重写器（late_rewriters）根据 `--target` 参数条件性应用，用于处理特定部署目标的限制：

```python
# tfonnx.py 中 late_rewriters 的注册
late_rewriters = []
if target is not None:
    if "rs5" in target:
        late_rewriters.append(rewrite_incomplete_type_support_rs5)
    if "rs6" in target:
        late_rewriters.append(rewrite_incomplete_type_support_rs6)
    if "nhwc" in target or "channels_last" in target:
        late_rewriters.append(rewrite_channels_last)
```

| Target | 重写器 | 解决的问题 |
|--------|--------|-----------|
| `rs5` | `rewrite_incomplete_type_support_rs5` | Windows ML RS5 不支持某些数据类型，自动插入 Cast |
| `rs6` | `rewrite_incomplete_type_support_rs6` | Windows ML RS6 的类型限制适配 |
| `nhwc` | `rewrite_channels_last` | Channels Last 布局适配（不在输入输出插入 Transpose，保持 NHWC） |

## 重写器排序原则

重写器的执行顺序很重要，遵循"单向→双向"原则：

1. **常量折叠先执行**：折叠常量可以简化后续模式匹配（常量输入变为常量属性）
2. **融合算子拆分先于模式匹配**：FusedBatchNorm 拆分后，其子算子才能被后续重写器识别
3. **卷积/矩阵等大模式先匹配**：GEMM、Conv+BiasAdd 等大模式先于简单模式匹配，避免部分节点被其他重写器修改后无法匹配
4. **布局优化在映射前**：Transpose 重写确保后续算子映射时数据布局正确
5. **late_rewriters 最后执行**：Target 适配在所有映射完成后执行，此时图已经是纯 ONNX 图

## 一个具体例子：rewrite_gemm

理解重写器的最好方式是看一个具体例子。GEMM 重写器识别 MatMul + BiasAdd 模式并替换为 ONNX GEMM 算子：

```python
def rewrite_gemm(g, ops):
    # 模式：MatMul -> BiasAdd
    # BiasAdd 的输入是 MatMul 的输出和一个 Const（bias）
    matmul_pattern = OpTypePattern("MatMul", name="matmul")
    bias_pattern = OpTypePattern("BiasAdd", name="biasadd",
                                  inputs=[matmul_pattern, OpTypePattern("Const", name="bias")])
    matcher = GraphMatcher(bias_pattern)
    
    for match in matcher.match_ops(ops):
        matmul = match.get_op("matmul")
        biasadd = match.get_op("biasadd")
        bias = match.get_op("bias")
        
        # 创建 GEMM 节点替代 MatMul + BiasAdd
        # ONNX GEMM: Y = alpha * A * B + beta * C
        gemm = g.make_node("Gemm",
                           inputs=[matmul.input[0], matmul.input[1], bias.input[0]],
                           outputs=biasadd.output,
                           alpha=1.0, beta=1.0)
        
        # 将所有引用 biasadd 输出的地方改为引用 gemm 输出
        g.replace_all_inputs(biasadd.output[0], gemm.output[0])
        
        # 标记旧节点为已转换
        matmul.skip_conversion = True
        biasadd.skip_conversion = True
        bias.skip_conversion = True
    
    return ops
```

## 关联概念

- [tf2onnx 整体架构](00-overall-architecture.md) — 理解重写器在三阶段流水线中的位置
- [转换流水线详解](01-conversion-pipeline.md) — 理解 pre-rewriters 和 late_rewriters 的执行时机
- [装饰器驱动的版本化算子注册表](02-versioned-opset-registry.md) — 理解 Mapper 阶段的 skip_conversion 标记机制
- [内部 Graph API 设计](04-graph-internal-api.md) — 理解重写器中 g.make_node、replace_all_inputs 等 API
- [ONNX 图优化器](05-optimizers.md) — 对比重写器与优化器的区别（语义 vs 性能）
