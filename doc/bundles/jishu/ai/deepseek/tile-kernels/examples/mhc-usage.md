---
type: example
scope: tile-kernels
name: MHC 核函数使用
version: "0.1.0"
source: tile-kernels-spec-facts
description: MHC（Multi-Head Compute）核函数的使用示例，包括初始化、mhc_pre/mhc_post 流程、推理融合、LM Head
---

# MHC 核函数使用

本示例展示如何使用 TileKernels 的 MHC（Multi-Head Compute）核函数，包括 residual 初始化、训练模式下的 mhc_pre/mhc_post 流程、推理模式下的大融合 kernel，以及 LM Head 处理。

---

## 环境准备

```python
import torch
import tile_kernels
from tile_kernels.modeling import mhc as mhc_modeling

device = 'cuda'
torch.manual_seed(42)
```

---

## MHC 参数设置

```python
# MHC 配置（典型 DeepSeek-V4 参数）
batch_size = 2
seq_len = 1024
hidden_size = 4096
mhc_mult = 4  # MHC 头数
mhc_mult3 = mhc_mult * (mhc_mult + 2)  # = 24，fn 输出维度倍数

# RMSNorm epsilon
norm_eps = 1e-6
mhc_pre_eps = 1e-6
mhc_sinkhorn_eps = 1e-6
mhc_sinkhorn_repeat = 10
post_mult_value = 1.0
```

---

## Step 1: 初始化 MHC Residual

MHC residual 的 shape 为 `(..., mhc_mult, hidden_size)`：

```python
# 模拟 embedding 输出
embedding_out = torch.randn(
    batch_size, seq_len, hidden_size,
    device=device, dtype=torch.bfloat16
)

# 方法1：使用高层 API expand_from_embedding
residual = mhc_modeling.expand_from_embedding(embedding_out, mhc_mult=mhc_mult)
print(f"Residual shape: {residual.shape}")  # (B, S, mhc_mult, H)
print(f"Residual dtype: {residual.dtype}")  # bfloat16

# 方法2：使用底层 op
from tile_kernels.modeling.mhc.ops import expand_to_mhc
residual2 = expand_to_mhc(embedding_out, mhc_mult=mhc_mult)
print(f"expand_to_mhc shape: {residual2.shape}")
```

---

## Step 2: 准备 MHC 参数

```python
# fn 权重：RMSNorm+线性变换
# fn shape: [mhc_mult*(mhc_mult+2), mhc_mult*hidden_size] fp32
# 这是一个大的线性层，将 mhc_mult*H 映射到 mhc_mult*(mhc_mult+2)*mhc_mult*H
fn = torch.randn(
    mhc_mult3, mhc_mult * hidden_size,
    device=device, dtype=torch.float32
) * 0.01

# scale 和 base 参数（控制 mix 系数的 sigmoid 变换）
# scale shape: [3]（pre/post/comb 三个 mix 共享缩放）
scale = torch.ones(3, device=device, dtype=torch.float32)
# base shape: [mhc_mult*(mhc_mult+2)]
base = torch.zeros(mhc_mult3, device=device, dtype=torch.float32)

# RMSNorm 权重（可选）
norm_weight = torch.ones(mhc_mult * hidden_size, device=device, dtype=torch.float32)
```

---

## Step 3: 训练模式——MHC Pre

训练模式下，`mhc_pre` 自动分步执行 norm_fn → split_mixes → sinkhorn → apply_mix：

```python
# 确保 requires_grad 以触发训练路径
residual.requires_grad_(True)
fn.requires_grad_(True)
scale.requires_grad_(True)
base.requires_grad_(True)

# MHC Pre（子层预处理）
layer_input, (post_mix, comb_mix) = mhc_modeling.mhc_pre(
    residual,
    fn=fn,
    scale=scale,
    base=base,
    norm_weight=norm_weight,
    norm_eps=norm_eps,
    mhc_mult=mhc_mult,
    post_mult_value=post_mult_value,
    pre_eps=mhc_pre_eps,
    sinkhorn_eps=mhc_sinkhorn_eps,
    sinkhorn_repeat=mhc_sinkhorn_repeat,
    n_splits=16,
)

print(f"Layer input shape: {layer_input.shape}")  # (B, S, H) bf16
print(f"Post mix shape: {post_mix.shape}")        # (B, S, mhc_mult, 1) fp32
print(f"Comb mix shape: {comb_mix.shape}")        # (B, S, mhc_mult, mhc_mult) fp32
```

---

## Step 4: 子层计算（Attention/FFN）

```python
# 模拟 attention 或 FFN 计算（实际中使用 DeepGEMM 或 FlashMLA）
# 这里用简单的线性层模拟
attn_weight = torch.randn(
    hidden_size, hidden_size,
    device=device, dtype=torch.bfloat16
) * 0.01
x = layer_input @ attn_weight  # (B, S, H) bf16
print(f"Sub-layer output shape: {x.shape}")
```

---

## Step 5: 训练模式——MHC Post

```python
from tile_kernels.modeling.mhc.ops import mhc_post

# MHC Post（更新 residual）
new_residual = mhc_post(
    x, residual,
    post_layer_mix=post_mix,
    comb_res_mix=comb_mix,
)
print(f"New residual shape: {new_residual.shape}")  # (B, S, mhc_mult, H)
```

---

## Step 6: 反向传播

```python
# 模拟 loss
loss = new_residual.float().sum()
loss.backward()

print(f"Residual grad shape: {residual.grad.shape}")
print(f"Fn grad shape: {fn.grad.shape if fn.grad is not None else 'None (main_grad)'}")
print(f"Scale grad: {scale.grad}")
```

---

## Step 7: 推理模式——大融合 Kernel

推理时（`torch.no_grad()`），`mhc_pre` 自动使用 `mhc_pre_big_fuse` 融合 kernel：

```python
with torch.no_grad():
    residual_infer = torch.randn(
        batch_size, seq_len, mhc_mult, hidden_size,
        device=device, dtype=torch.bfloat16
    )

    # mhc_pre 在推理模式下自动使用大融合 kernel
    layer_input_infer, (post_mix_infer, comb_mix_infer) = mhc_modeling.mhc_pre(
        residual_infer,
        fn=fn,
        scale=scale,
        base=base,
        norm_weight=norm_weight,
        norm_eps=norm_eps,
        mhc_mult=mhc_mult,
        post_mult_value=post_mult_value,
        pre_eps=mhc_pre_eps,
        sinkhorn_eps=mhc_sinkhorn_eps,
        sinkhorn_repeat=mhc_sinkhorn_repeat,
        n_splits=1,
    )

    print(f"推理 layer_input shape: {layer_input_infer.shape}")

    # 也可以直接调用融合 kernel
    from tile_kernels.modeling.mhc.ops import mhc_pre_big_fuse
    post_mix_bf, comb_mix_bf, layer_input_bf = mhc_pre_big_fuse(
        residual_infer, fn, scale, base,
        rms_eps=norm_eps,
        mhc_pre_eps=mhc_pre_eps,
        mhc_sinkhorn_eps=mhc_sinkhorn_eps,
        mhc_post_mult_value=post_mult_value,
        sinkhorn_repeat=mhc_sinkhorn_repeat,
        n_splits=1,
    )
    print(f"直接调用 big fuse layer_input shape: {layer_input_bf.shape}")
```

---

## Step 8: MHC Head（LM Head）

LM Head 层使用简化的 MHC 处理：

```python
with torch.no_grad():
    # LM Head 的 fn shape 不同：[mhc_mult, mhc_mult*hidden_size]
    fn_head = torch.randn(
        mhc_mult, mhc_mult * hidden_size,
        device=device, dtype=torch.float32
    ) * 0.01
    scale_head = torch.ones(3, device=device, dtype=torch.float32)
    base_head = torch.zeros(mhc_mult3, device=device, dtype=torch.float32)

    # mhc_head 内部 pad fn 到 [mhc_mult*(mhc_mult+2), ...]
    logits_input = mhc_modeling.mhc_head(
        residual_infer,
        fn=fn_head,
        scale=scale_head,
        base=base_head,
        norm_weight=norm_weight,
        norm_eps=norm_eps,
        mhc_mult=mhc_mult,
        pre_eps=mhc_pre_eps,
        n_splits=1,
    )
    print(f"LM Head input shape: {logits_input.shape}")  # (B, S, H)
```

---

## Step 9: 原子 Op 独立使用

可以独立使用各个原子 op：

```python
from tile_kernels.modeling.mhc.ops import (
    mhc_pre_norm_fn, mhc_pre_split_mixes,
    sinkhorn_normalize, mhc_pre_apply_mix,
)

with torch.no_grad():
    test_residual = torch.randn(
        2, 64, mhc_mult, hidden_size,
        device=device, dtype=torch.bfloat16
    )

    # Step 1: Norm + Fn
    normed = mhc_pre_norm_fn(
        test_residual, fn[:mhc_mult3, :mhc_mult*hidden_size],
        mhc_norm_weight=norm_weight,
        mhc_norm_eps=norm_eps,
        fuse_grad_acc=False,
        n_splits=1,
    )
    print(f"Norm+Fn output shape: {normed.shape}")

    # Step 2: Split mixes
    test_scale = torch.ones(3, device=device, dtype=torch.float32)
    test_base = torch.zeros(mhc_mult3, device=device, dtype=torch.float32)
    pre_mix, post_mix, comb_mix = mhc_pre_split_mixes(
        normed, test_scale, test_base,
        mhc_mult=mhc_mult,
        mhc_post_mult_value=post_mult_value,
        mhc_pre_eps=mhc_pre_eps,
    )
    print(f"Pre mix shape: {pre_mix.shape}")
    print(f"Post mix shape: {post_mix.shape}")
    print(f"Comb mix shape: {comb_mix.shape}")

    # Step 3: Sinkhorn normalize
    comb_mix_normed = sinkhorn_normalize(comb_mix, repeat=10, eps=1e-6)
    print(f"Sinkhorn comb mix shape: {comb_mix_normed.shape}")
    # 验证双随机性
    row_sums = comb_mix_normed.sum(-1)
    col_sums = comb_mix_normed.sum(-2)
    print(f"Row sums (should be ~1): {row_sums[0,0,:5]}")
    print(f"Col sums (should be ~1): {col_sums[0,0,:5]}")

    # Step 4: Apply mix
    layer_in = mhc_pre_apply_mix(normed, pre_mix)
    print(f"Apply mix output shape: {layer_in.shape}")  # (B, S, H)
```

---

## Step 10: 梯度检查点——多层重计算

```python
from tile_kernels.modeling.mhc.ops import mhc_multilayer_recompute

# 模拟多层 MHC 的重计算（用于 gradient checkpointing）
num_layers = 4
num_post = num_layers  # 或 num_layers - 1

# 构建各层的 mix 列表
pre_mix_list = []
post_mix_list = []
comb_mix_list = []
layer_output_list = []
residual_list = []
layer_input_list = []

initial_residual = torch.randn(
    2, 32, mhc_mult, hidden_size,
    device=device, dtype=torch.bfloat16
)

for i in range(num_layers):
    pre_mix_list.append(torch.randn(
        2, 32, mhc_mult*(mhc_mult+2), 1,
        device=device, dtype=torch.float32
    ))
    post_mix_list.append(torch.randn(
        2, 32, mhc_mult, 1,
        device=device, dtype=torch.float32
    ))
    comb_mix_list.append(torch.randn(
        2, 32, mhc_mult, mhc_mult,
        device=device, dtype=torch.float32
    ))
    layer_output_list.append(torch.randn(
        2, 32, hidden_size,
        device=device, dtype=torch.bfloat16
    ))
    residual_list.append(torch.zeros_like(initial_residual))
    layer_input_list.append(torch.zeros(
        2, 32, hidden_size,
        device=device, dtype=torch.bfloat16
    ))

# 原地重计算多层 residual
mhc_multilayer_recompute(
    initial_residual,
    pre_mix_list, layer_output_list,
    post_mix_list, comb_mix_list,
    layer_input_list, residual_list,
)
print(f"多层重计算完成，重计算了 {num_layers} 层 residual")
print(f"Residual list[0] 是否非零: {residual_list[0].abs().sum().item() > 0}")
```

---

## 完整 MHC Transformer Block（训练）

```python
class MHCBlock(torch.nn.Module):
    def __init__(self, hidden_size, mhc_mult=4, num_heads=32):
        super().__init__()
        self.hidden_size = hidden_size
        self.mhc_mult = mhc_mult
        mhc_mult3 = mhc_mult * (mhc_mult + 2)

        # MHC 参数
        self.mhc_fn = torch.nn.Parameter(
            torch.randn(mhc_mult3, mhc_mult * hidden_size) * 0.01
        )
        self.mhc_scale = torch.nn.Parameter(torch.ones(3))
        self.mhc_base = torch.nn.Parameter(torch.zeros(mhc_mult3))
        self.mhc_norm_weight = torch.nn.Parameter(
            torch.ones(mhc_mult * hidden_size)
        )

    def forward(self, residual):
        """
        residual: (B, S, mhc_mult, H) bf16
        returns: new_residual (B, S, mhc_mult, H) bf16
        """
        from tile_kernels.modeling.mhc import mhc_pre
        from tile_kernels.modeling.mhc.ops import mhc_post

        # MHC Pre
        layer_input, (post_mix, comb_mix) = mhc_pre(
            residual,
            fn=self.mhc_fn,
            scale=self.mhc_scale,
            base=self.mhc_base,
            norm_weight=self.mhc_norm_weight,
            mhc_mult=self.mhc_mult,
        )

        # 这里应该是 Attention + FFN
        # 实际中使用 FlashMLA + DeepGEMM
        x = layer_input  # 占位

        # MHC Post
        new_residual = mhc_post(
            x, residual,
            post_layer_mix=post_mix,
            comb_res_mix=comb_mix,
        )
        return new_residual
```

---

## 注意事项

1. **精度要求**：MHC 的 residual 使用 BF16，fn/scale/base 使用 FP32
2. **维度对齐**：hidden_size 需要满足 kernel 的对齐约束（通常 64/128/256 对齐）
3. **n_splits**：TileLang 实现中 n_splits 强制为 1，大维度 GEMM 建议使用 DeepGEMM
4. **训练/推理自动切换**：`mhc_pre()` 根据 `torch.is_grad_enabled()` 自动选择分步执行或融合 kernel
5. **梯度融合**：`fuse_grad_acc=True`（默认）通过 storage 属性传递梯度缓冲区，减少内存分配
6. **mhc_mult 约束**：当前实现 mhc_mult3 = mhc_mult*(mhc_mult+2) ≤ 32，因此 mhc_mult ≤ 4（4*6=24 ≤ 32）
