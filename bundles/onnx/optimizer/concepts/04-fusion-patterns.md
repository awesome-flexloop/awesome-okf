---
type: concept
title: "算子融合模式"
description: "ONNX Optimizer 中核心算子融合 pass 的数学原理与变换模式：BN-Conv 融合、AddBias 融合、QKV 融合、连续 Transpose/Concat/Squeeze 融合、Pad 融合等"
sources:
  references: [../references/pass-base.md]
  facts: [F-045, F-048, F-049, F-057]
---

# 算子融合模式

## 核心理解

算子融合（Operator Fusion）是 ONNX Optimizer 中最重要的优化类别，默认集包含 17 个融合 pass。融合的核心思想是将多个相邻的算子合并为一个等价的算子（或修改现有算子的属性），从而减少内核启动开销、消除中间结果的内存读写、提升推理性能。理解融合的数学原理和模式匹配条件，有助于正确理解优化后的模型结构。

## 融合的基本原则

1. **数学等价性**：融合前后的计算结果在数值上必须等价（浮点精度允许微小差异）
2. **常量前提**：大多数融合要求权重为常量（initializer），因为需要在编译时计算融合后的权重
3. **独占使用**：被融合的中间结果不能有其他消费者（否则无法安全移除中间算子）
4. **拓扑序**：融合在拓扑遍历中执行，确保前驱算子先处理

## 一、BN-Conv 融合（fuse_bn_into_conv）

**类型**：Fuse / Complete / Compute

这是推理优化中最经典的融合，将 BatchNormalization 的线性变换参数折叠进前面的 Conv 权重和偏置。

### 数学原理

Conv 层输出：

```
Y = Conv(X, W, b) = X * W + b    （* 表示卷积）
```

BatchNormalization（推理模式，training_mode=0）：

```
Y_bn = γ * (Y - μ) / sqrt(σ² + ε) + β
```

其中 γ（scale）、β（bias）、μ（running_mean）、σ²（running_var）均为训练后固定的常量。

将 Conv 代入 BN：

```
Y_bn = γ * (X*W + b - μ) / sqrt(σ² + ε) + β
     = X * (γ * W / sqrt(σ² + ε)) + (γ * (b - μ) / sqrt(σ² + ε) + β
     = X * W' + b'
```

其中：
- `W' = W * γ / sqrt(σ² + ε)`（逐通道缩放权重）
- `b' = γ * (b - μ) / sqrt(σ² + ε) + β`（融合偏置）

### 匹配条件

1. Conv 后紧接 BatchNormalization
2. BN 的 scale/bias/mean/var 均为常量（initializer）
3. Conv 权重为常量（initializer）
4. BN 输入仅被 BN 使用（无其他分支）
5. BN 只有一个输出
6. 处于推理模式（training_mode=0，即非训练模式）

### 效果

融合后：
- 移除 BatchNormalization 节点
- 更新 Conv 的权重 W 和偏置 b
- 若 Conv 原来没有 bias，添加 bias 输入
- 运行时减少一个算子（BN），减少一次完整的张量遍历

## 二、AddBias-Conv 融合（fuse_add_bias_into_conv）

**类型**：Fuse / Complete / Compute

将 Conv 后面的 Add（偏置加法）融合进 Conv 的 bias 输入。

### 数学原理

```
Y = Conv(X, W, b)
Z = Y + C    （C 为常量偏置）
```

融合后：

```
Z = Conv(X, W, b + C) = X*W + (b + C)
```

### 效果

- 移除 Add 节点
- 将常量 C 加到 Conv 的 bias 上（若 Conv 无 bias，则用 C 创建 bias）

## 三、Mul-Conv 融合（fuse_mul_into_conv）

**类型**：Fuse / Complete / Compute

将 Conv 后面的逐通道 Mul（缩放）融合进 Conv 权重。

### 数学原理

```
Y = Conv(X, W, b)
Z = Y * S    （S 为逐通道缩放因子）
```

融合后：

```
W' = W * S（逐输出通道缩放）
b' = b * S
Z = Conv(X, W', b')
```

## 四、Pad-Conv/Pool 融合（fuse_pad_into_conv / fuse_pad_into_pool）

**类型**：Fuse / Complete / Compute

将显式 Pad 算子的 padding 参数融合进 Conv 或 Pool 的 `pads` 属性（或 `auto_pad` 属性）。

### 变换模式

```
X → Pad(pads=[p1,p2,...]) → Conv(kernel_shape, pads=[0,0,...])
```

融合后：

```
X → Conv(kernel_shape, pads=[p1,p2,...])    （去掉显式 Pad，padding 写进 Conv 属性）
```

### 效果

- 移除 Pad 节点
- 将 padding 值合并到 Conv/Pool 的 pads 属性中
- 减少一次内存读写（Pad 产生的中间张量不再需要）

## 五、QKV 融合（fuse_qkv）

**类型**：Fuse / Complete / Compute

Transformer 模型中，Q/K/V 三个投影 MatMul 共享同一输入，融合为单个 MatMul+Split。

### 变换模式

```
     X
    /|\
   / | \
  Mq Mk Mv    （三个 MatMul，权重 Wq/Wk/Wv 为常量，形状相同）
  |  |  |
  Q  K  V
```

融合后：

```
     X
     |
  Concat(Wq, Wk, Wv) → W_qkv
     |
   MatMul(W_qkv)
     |
   Split(axis=-1)
    /|\
   / | \
  Q  K  V
```

### 匹配条件

1. 三个 MatMul 共享同一个输入 X
2. 三个 MatMul 的权重 Wq/Wk/Wv 均为常量
3. 三个权重形状相同（最后一维可不同？不，需要能 concat）
4. 适用于 Transformer 自注意力的 Q/K/V 投影

### 效果

- 将三次矩阵乘法合并为一次（GPU 上大矩阵乘法效率更高）
- 减少两次内核启动
- 在批量大、hidden_dim 大时效果显著

## 六、连续算子融合

### 连续 Transpose 融合（fuse_consecutive_transposes）

**类型**：Fuse / Partial / Compute

两个相邻的 Transpose，perm 可以组合：

```
X → Transpose(perm1) → Transpose(perm2) → Y
```

融合为：

```
X → Transpose(perm = perm2[perm1]) → Y
```

其中组合 perm 的计算为 `result[i] = perm2[perm1[i]]`。如果组合后的 perm 是恒等排列（`perm[i]=i`），则完全移除 Transpose（eliminate_nop_transpose 后续处理）。

**为什么是 Partial？** 融合两个 Transpose 后，新的 Transpose 可能与前面或后面的 Transpose 再次相邻，需要定点迭代。

### 连续 Concat 融合（fuse_consecutive_concats）

**类型**：Fuse / Partial / Compute

轴相同的相邻 Concat 可以合并输入列表。

```
Concat([A,B], axis=1) → Concat([C,D], axis=1) → Y
```

融合为：

```
Concat([A,B,C,D], axis=1) → Y
```

### 连续 Squeeze/Unsqueeze 融合

| Pass | 效率 | 说明 |
|------|:----:|------|
| fuse_consecutive_squeezes | Complete | 合并连续 Squeeze 的 axes |
| fuse_consecutive_unsqueezes | Complete | 合并连续 Unsqueeze 的 axes |
| fuse_consecutive_squeeze_unsqueeze | Partial | Squeeze 后跟 Unsqueeze 可能抵消 |

### 连续 Slice 融合（fuse_consecutive_slices）

**类型**：Fuse / Partial / Compute

将连续的 Slice 操作组合为单个 Slice（计算复合偏移量和范围）。

### 连续 Reduce+Unsqueeze 融合（fuse_consecutive_reduce_unsqueeze）

**类型**：Fuse / Complete / Compute

Reduce 操作后跟 Unsqueeze 恢复维度时，直接用 keepdims=1 替代。

## 七、GEMM 相关融合

### MatMul+Add → Gemm（fuse_matmul_add_bias_into_gemm）

**类型**：Fuse / Complete / Compute

```
Y = MatMul(A, B)
Z = Y + C    （C 可以是偏置向量或矩阵）
```

融合为 Gemm 算子（alpha=1, beta=1）：

```
Z = Gemm(A, B, C, alpha=1, beta=1)
```

Gemm 算子在 BLAS 库中有高度优化的实现，比分开的 MatMul+Add 更快。

### Transpose+Gemm 融合（fuse_transpose_into_gemm）

**类型**：Fuse / Complete / Compute

将 Gemm 输入的 Transpose 操作融合进 Gemm 的 `transA`/`transB` 属性：

```
X → Transpose → Gemm(A, B, ...)
```

融合为：

```
Gemm(A_transposed, B, ..., transA=1)
```

## 八、LogSoftmax 融合（fuse_consecutive_log_softmax）

**类型**：Fuse / Complete / Compute

```
Y = Softmax(X)
Z = Log(Y)
```

融合为单个 LogSoftmax 算子：

```
Z = LogSoftmax(X)
```

LogSoftmax 直接计算 `log(softmax(x))`，使用 log-sum-exp 技巧避免数值溢出，数值稳定性更好。

## 九、Concat→Reshape 融合（fuse_concat_into_reshape）

**类型**：Fuse / Complete / Compute

特定模式的 Concat（输入在内存中连续）可以用 Reshape 替代，避免数据拷贝。

## 融合 pass 的 pass_util 工具

开发融合 pass 时，`pass_util.h` 提供了常用的模板工具函数：

| 工具函数 | 用途 |
|----------|------|
| `CheckKind<kOpType>(node)` | 检查节点是否为指定算子类型 |
| `IsConstantTensor(value)` | 判断值是否为常量节点或 initializer |
| `FetchConstantTensor(value)` | 获取常量张量的数据指针 |
| `PrevNode(node, input_index)` | 获取指定输入的前驱节点 |
| `GetValueFromAttr<T>(node, name)` | 类型安全读取属性值 |
| `isABroadcastToB(shape_a, shape_b)` | 检查广播兼容性 |
| `FetchSoleIntValueOfTensor(tensor)` | 获取标量张量的整数值 |

## 融合的局限性

1. **仅局部匹配**：PredicateBasedPass 的逐节点匹配无法发现跨多层结构的融合机会
2. **需要常量权重**：融合涉及权重计算时，要求权重必须是 initializer（常量）
3. **独占使用要求**：中间结果不能有多个消费者，否则无法安全移除
4. **不含常量折叠**：项目 Roadmap 明确指出需要"分离图重写与常量折叠"，当前优化器不做解释执行的常量折叠

对于需要常量折叠的场景，推荐组合使用 onnx-simplifier（先做常量折叠，再调用 optimizer 做图清理）。

## 关联概念

- [Pass 系统：基类继承体系与注册机制](01-pass-system.md) — 了解融合 pass 的基类 PredicateBasedPass
- [内置优化 Passes 分类详解](02-builtin-passes.md) — 查看完整的融合 pass 列表
- [PassManager 执行模型与定点收敛](03-pass-execution.md) — 了解 Partial 效率融合 pass 的定点迭代
- [自定义 Pass 开发方法](06-custom-pass.md) — 学习开发自定义融合 pass
