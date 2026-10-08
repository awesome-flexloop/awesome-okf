---
type: concept
scope: tile-kernels
name: MHC Multi-Head Compute
version: "0.1.0"
source: tile-kernels-spec-facts
description: TileKernels MHC（Multi-Head Compute）详解——DeepSeek-V4 核心结构，多头残差计算、Sinkhorn归一化、训练/推理双路径
---

# MHC Multi-Head Compute

MHC（Multi-Head Compute）是 DeepSeek-V4 引入的核心架构创新。传统 Transformer 中 residual 是一个单一的向量，而 MHC 将 residual 扩展为 mhc_mult 个"头"，每个头独立进行线性变换和归一化，然后通过学习到的 mix 系数加权合并。这种多"头"计算机制提供了更细粒度的特征处理能力，配合 Sinkhorn 双随机归一化保证训练稳定性。

---

## 一、MHC 核心思想

### 1.1 从单头残差到多头残差

传统 Transformer 的残差连接：

```
residual (B, S, H)
→ layer_input = RMSNorm(residual)
→ x = Attention(layer_input) 或 FFN(layer_input)
→ residual = residual + x
```

MHC 将 residual 扩展为多头：

```
residual (B, S, mhc_mult, H)     # mhc_mult 个头，通常 mhc_mult=4
→ layer_input = mhc_pre(residual)  # 多头→单头
→ x = Attention(layer_input) 或 FFN(layer_input)
→ residual = mhc_post(residual, x) # 单头→多头更新
```

### 1.2 为什么需要 MHC？

- **更细粒度的特征路由**：不同的 head 可以学习处理不同类型的特征
- **动态残差混合**：mix 系数根据输入动态计算，决定每个 head 对当前子层的贡献
- **Sinkhorn 归一化保证稳定性**：mix 系数矩阵经 Sinkhorn 归一化为双随机矩阵，保证梯度流动的平衡
- **与 MoE 互补**：MoE 在 FFN 层做 expert 路由，MHC 在 residual 层面做 head 级别的特征混合

---

## 二、MHC 计算流水线

### 2.1 训练模式：分步执行

每个子层（attention 或 FFN）之前执行 `mhc_pre`，之后执行 `mhc_post`。

**mhc_pre 流水线**：

```
residual (B, S, mhc_mult, H) bf16
    │
    ├─ Step 1: mhc_pre_norm_fn
    │   · RMSNorm(residual, norm_weight)         → 归一化
    │   · fn_matmul: (B,S,mhc_mult,H) → (B,S,mhc_mult*(mhc_mult+2), mhc_mult*H)
    │   · 内部对 fn 权重做 round_to_tf32
    │
    ├─ Step 2: mhc_pre_split_mixes
    │   · output_mix = sigmoid(input * scale + base) + eps
    │   · 沿特征维分割为:
    │     - pre_layer_mix:  (B, S, mhc_mult*(mhc_mult+2), 1)
    │     - post_layer_mix: (B, S, mhc_mult, 1)
    │     - comb_res_mix:   (B, S, mhc_mult, mhc_mult)
    │
    ├─ Step 3: sinkhorn_normalize
    │   · 对 comb_res_mix 做 Sinkhorn 迭代归一化
    │   · 迭代 repeat 次（默认10次）行列归一化
    │   · 输出双随机矩阵（每行和=1，每列和=1）
    │
    └─ Step 4: mhc_pre_apply_mix
        · out = sum(normed_residual * pre_layer_mix, dim=mhc_mult)
        · 加权求和归约 mhc_mult 维度
        → layer_input (B, S, H) bf16
```

**mhc_post 流水线**（子层计算后）：

```
x = Attention/FFN(layer_input)  → (B, S, H) bf16
residual (B, S, mhc_mult, H) bf16
post_layer_mix (B, S, mhc_mult, 1) fp32
comb_res_mix (B, S, mhc_mult, mhc_mult) fp32
    │
    ▼ mhc_post:
    · new_residual = einsum(comb_res_mix, residual)  # residual 混合
    · new_residual += post_layer_mix * x.unsqueeze(-2) # 加入新计算结果
    → new_residual (B, S, mhc_mult, H) bf16
```

### 2.2 推理模式：大融合 kernel

推理时 `not torch.is_grad_enabled()`，使用 `mhc_pre_big_fuse` 将 norm_fn + split_mixes + sinkhorn + apply_mix 融合为单个 kernel：

```python
if not torch.is_grad_enabled():
    # 推理：大融合 kernel
    post_mix, comb_mix, layer_input = mhc_pre_big_fuse(
        residual, fn, scale, base, rms_eps, pre_eps,
        sinkhorn_eps, post_mult_value, sinkhorn_repeat
    )
else:
    # 训练：分步 autograd.Function
    normed = mhc_pre_norm_fn(residual, fn, norm_weight, norm_eps)
    pre_mix, post_mix, comb_mix = mhc_pre_split_mixes(normed, scale, base, ...)
    comb_mix = sinkhorn_normalize(comb_mix, ...)
    layer_input = mhc_pre_apply_mix(normed, pre_mix)
```

融合 kernel 减少了中间结果的全局内存读写，显著提升推理性能。

---

## 三、核心算子详解

### 3.1 Expand to MHC

```python
expand_to_mhc(hidden, mhc_mult=4)
# (B, S, H) → (B, S, mhc_mult, H)
# 沿 mhc_mult 维复制
```

用于从 embedding 输出初始化 MHC residual（`expand_from_embedding`）。反向是对 mhc_mult 维求和。

### 3.2 Pre-Norm-Fn

MHC 预处理的第一步：RMSNorm + 线性变换。

```python
mhc_pre_norm_fn(residual, mhc_fn, mhc_norm_weight, mhc_norm_eps=1e-6,
                fuse_grad_acc=True, n_splits=16)
```

- **RMSNorm**：对每个 head 独立做 RMSNorm
- **Fn Matmul**：线性变换将 `mhc_mult*H` 映射到 `mhc_mult*(mhc_mult+2)*mhc_mult*H`
  - 输出维度为 `mhc_mult*(mhc_mult+2)`，包含 pre_layer_mix(mhc_mult) + post_layer_mix(mhc_mult) + comb_res_mix(mhc_mult*mhc_mult) 的原始特征
- **TF32 舍入**：`round_to_tf32(fn)` 将 fp32 权重舍入到 TF32 精度
- **注意**：TileLang 实现中 n_splits 强制为 1（不支持 split-K GEMM），大维度 GEMM 建议使用 DeepGEMM

### 3.3 Pre-Split-Mixes

将 fn matmul 的输出经 sigmoid 变换后分割为三种 mix 系数：

```python
mhc_pre_split_mixes(input_mixes, mhc_scale, mhc_base, mhc_mult,
                    mhc_post_mult_value, mhc_pre_eps)
# → (pre_layer_mix, post_layer_mix, comb_res_mix)
```

计算公式：
```
output_mix = sigmoid(input_mix * mhc_scale + mhc_base) + mhc_pre_eps
```

三种 mix 的用途：
- **pre_layer_mix** (B, S, mhc_mult*(mhc_mult+2), 1)：mhc_pre 最后一步 apply_mix 的权重
- **post_layer_mix** (B, S, mhc_mult, 1)：mhc_post 中新加 x 的权重
- **comb_res_mix** (B, S, mhc_mult, mhc_mult)：mhc_post 中 residual 自混合的权重矩阵

### 3.4 Sinkhorn Normalize

将 comb_res_mix 归一化为双随机矩阵（每行和为 1，每列和为 1）。

```python
sinkhorn_normalize(x, repeat=10, eps=1e-6)
```

Sinkhorn-Knopp 算法：反复执行行归一化和列归一化，直到收敛。默认 10 次迭代足够接近双随机矩阵。

```python
for _ in range(repeat):
    x = x / x.sum(dim=-1, keepdim=True)  # 行归一化
    x = x / x.sum(dim=-2, keepdim=True)  # 列归一化
```

双随机矩阵的性质保证了：
- 每个 head 的输入权重和为 1（行归一化）
- 每个 head 的输出贡献和为 1（列归一化）
- 训练过程中梯度流动平衡，不会出现某些 head 主导或被忽略的情况

### 3.5 Pre-Apply-Mix

加权求和归约 mhc 维度，输出单头 layer_input：

```python
mhc_pre_apply_mix(x, mix)
# out = sum(x * mix, dim=-2)
# x: (B, S, mhc_mult, H), mix: (B, S, mhc_mult, 1)
# out: (B, S, H)
```

### 3.6 Post

子层计算后，更新 residual：

```python
mhc_post(x, residual, post_layer_mix, comb_res_mix)
```

计算：
1. residual 自混合：`mixed_res = einsum(comb_res_mix, residual)`，即 `mixed_res[..., i, :] = sum_j comb_res_mix[...,i,j] * residual[...,j,:]`
2. 加入新计算：`new_residual = mixed_res + post_layer_mix * x.unsqueeze(-2)`

### 3.7 Head Compute Mix

LM Head 专用的简化 mix 计算：

```python
mhc_head_compute_mix(input_mix, mhc_scale, mhc_base, mhc_pre_eps)
# output = sigmoid(input * scale + base) + eps
```

`mhc_head()` 高层 API 组合 pre_norm_fn + head_compute_mix + pre_apply_mix，用于 LM Head 层。

### 3.8 Multilayer Recompute

用于梯度检查点（gradient checkpointing）的多层 residual 重计算：

```python
mhc_multilayer_recompute(
    initial_residual,
    pre_mix_list, layer_output_list,
    post_mix_list, comb_mix_list,
    layer_input_list, residual_list
)
```

使用指针表（pointer table）批处理多个层，原地重计算 residual，避免保存所有中间结果。

---

## 四、梯度优化技术

### 4.1 Fused Grad Acc

MHC 模块广泛使用 fuse_grad_acc 技术：通过 `tensor.untyped_storage().grad_from_mhc_post` 属性在多个 autograd.Function 之间共享 fp32 梯度缓冲区。

**工作原理**：
1. mhc_post_bwd 计算 d_residual 后，不直接返回，而是将梯度存入 `residual.untyped_storage().grad_from_mhc_post`
2. mhc_pre_apply_mix_bwd 检测到 `x.untyped_storage().grad_from_mhc_post` 存在时，直接在该缓冲区上累加梯度
3. 避免为中间结果分配额外的梯度张量

这种"梯度缓冲区接力"机制在反向传播中减少了大量的内存分配和数据搬移。

### 4.2 Main Grad

对于 scale/base/fn 等参数，如果参数上存在 `.main_grad` 属性（fp32 主梯度缓冲区），梯度直接原地累积到 main_grad，backward 对该参数返回 None。这用于混合精度训练中维护 fp32 主梯度。

### 4.3 Partial Buffer Reduce

Scale/base 等 1D 参数的梯度在 backward 中使用 num_sms 个 partial buffer，每个 SM 独立累积梯度，最后 `sum(0)` 归约。这种并行规约避免了原子操作的竞争。

---

## 五、高层 Functional API

```python
# 一站式子层预处理（自动选择训练/推理路径）
layer_input, (post_mix, comb_mix) = tile_kernels.modeling.mhc.mhc_pre(
    residual,              # (B, S, mhc_mult, H) bf16
    fn,                    # [mhc_mult*(mhc_mult+2), mhc_mult*H] fp32
    scale,                 # [3] fp32
    base,                  # [mhc_mult*(mhc_mult+2)] fp32
    norm_weight=None,      # RMSNorm 权重
    norm_eps=1e-6,
    mhc_mult=4,
    post_mult_value=1.0,
    pre_eps=1e-6,
    sinkhorn_eps=1e-6,
    sinkhorn_repeat=10,
    n_splits=16,
)

# LM Head 处理
layer_input = tile_kernels.modeling.mhc.mhc_head(
    residual, fn, scale, base,
    norm_weight=None, norm_eps=1e-6,
    mhc_mult=4, pre_eps=1e-6, n_splits=16,
)

# 初始化 residual
residual = tile_kernels.modeling.mhc.expand_from_embedding(
    embedding_output, mhc_mult=4
)
```
