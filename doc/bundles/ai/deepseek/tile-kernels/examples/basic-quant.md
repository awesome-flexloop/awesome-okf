---
type: example
scope: tile-kernels
name: FP8 量化基础用法
version: "0.1.0"
source: tile-kernels-spec-facts
description: FP8/FP4 量化、反量化、SwiGLU融合量化的基础使用示例
---

# FP8 量化基础用法

本示例展示 TileKernels 量化核函数的基础用法，包括 per-token/per-block/per-channel 量化、反量化、SwiGLU 融合量化以及 E5M6 格式。

---

## 环境准备

```python
import torch
import tile_kernels

# 确认 GPU 可用
assert torch.cuda.is_available()
device = 'cuda'

# 可选：设置使用的 SM 数量（用于性能调优或 MPS 多实例）
# tile_kernels.set_num_sms(64)
print(f"使用 SM 数量: {tile_kernels.get_num_sms()}")
print(f"每 SM 最大共享内存: {tile_kernels.get_max_smem_per_sm()} bytes")
```

---

## Per-Token FP8 量化（激活量化）

Per-token 量化是最常用的激活量化方式，每个 token（行）独立计算缩放因子。

```python
# 创建 BF16 激活张量
num_tokens, hidden = 4096, 4096
x = torch.randn(num_tokens, hidden, device=device, dtype=torch.bfloat16)

# Per-token FP8 E4M3 量化
num_per_channels = 128  # 每128个channel共享一个sf
x_fp8, x_sf = tile_kernels.quant.per_token_cast(
    x, fmt='e4m3', num_per_channels=num_per_channels
)

print(f"输入 shape: {x.shape}, dtype: {x.dtype}")
print(f"FP8 data shape: {x_fp8.shape}, dtype: {x_fp8.dtype}")
print(f"Scale factor shape: {x_sf.shape}, dtype: {x_sf.dtype}")

# 反量化回 BF16 验证精度
x_bf16 = tile_kernels.quant.per_token_cast_back(
    (x_fp8, x_sf), fmt='bf16', num_per_channels=num_per_channels
)

# 计算余弦相似度
x_fp32 = x.float()
x_deq_fp32 = x_bf16.float()
cos_sim = torch.nn.functional.cosine_similarity(x_fp32.flatten(), x_deq_fp32.flatten(), dim=0)
print(f"反量化余弦相似度: {cos_sim.item():.6f}")  # 应接近 1.0
```

---

## Per-Block FP8 量化（权重量化）

Per-block 量化常用于权重量化，每个矩形 block 独立缩放。

```python
# 创建 BF16 权重张量
out_features, in_features = 4096, 4096
weight = torch.randn(out_features, in_features, device=device, dtype=torch.bfloat16)

# Per-block FP8 量化，block_size=(128, 128)
block_size = (128, 128)
w_fp8, w_sf = tile_kernels.quant.per_block_cast(
    weight, fmt='e4m3', block_size=block_size
)

print(f"权重 shape: {weight.shape}")
print(f"FP8 weight shape: {w_fp8.shape}")
print(f"SF shape: {w_sf.shape}")  # (32, 32) = (4096/128, 4096/128)

# 反量化验证
w_deq = tile_kernels.quant.cast_back(
    (w_fp8, w_sf), fmt='bf16', x_block_size=block_size
)
cos_sim = torch.nn.functional.cosine_similarity(
    weight.float().flatten(), w_deq.float().flatten(), dim=0
)
print(f"权重反量化余弦相似度: {cos_sim.item():.6f}")
```

---

## FP4 E2M1 量化

FP4（E2M1）是 4-bit 极低精度格式，两个值打包为一个 int8：

```python
# Per-token FP4 量化
x_fp4, x_fp4_sf = tile_kernels.quant.per_token_cast(
    x, fmt='e2m1', num_per_channels=num_per_channels
)

print(f"FP4 data shape: {x_fp4.shape}, dtype: {x_fp4.dtype}")
# 注意：FP4 的物理 hidden 是逻辑 hidden 的一半（2个4bit值=1byte）
print(f"逻辑 hidden: {hidden}, 物理 shape[-1]: {x_fp4.shape[-1]}")

# FP4 反量化
x_fp4_deq = tile_kernels.quant.per_token_cast_back(
    (x_fp4, x_fp4_sf), fmt='bf16', num_per_channels=num_per_channels
)
cos_sim = torch.nn.functional.cosine_similarity(
    x.float().flatten(), x_fp4_deq.float().flatten(), dim=0
)
print(f"FP4 反量化余弦相似度: {cos_sim.item():.6f}")  # 精度低于 FP8
```

---

## FP4 → FP8 无损重量化

将 FP4 量化的权重无损上转为 FP8（FP8 精度高于 FP4，无精度损失）：

```python
# FP4 权重量化
w_fp4, w_fp4_sf = tile_kernels.quant.per_block_cast(
    weight, fmt='e2m1', block_size=block_size
)

# FP4 → FP8 无损重量化（不同 block size）
out_block_size = (128, 128)
w_fp8_from_fp4, w_fp8_from_fp4_sf = tile_kernels.quant.per_block_cast_lossless(
    (w_fp4, w_fp4_sf), fmt='e4m3',
    x_block_size=block_size,
    out_block_size=out_block_size,
)

print(f"FP4→FP8 无损转换完成")
print(f"FP8 data shape: {w_fp8_from_fp4.shape}")
```

---

## Per-Channel 量化

Per-channel 量化沿 token 维度分组缩放，常用于 MoE 场景：

```python
# per-channel 要求 num_tokens % 128 == 0, hidden % 64 == 0
x_pc_fp8, x_pc_sf = tile_kernels.quant.per_channel_cast(
    x, fmt='e4m3', num_per_tokens=128
)
print(f"Per-channel FP8 data shape: {x_pc_fp8.shape}")
print(f"Per-channel SF shape: {x_pc_sf.shape}")

# Per-channel + 转置融合
x_pc_t_fp8, x_pc_t_sf = tile_kernels.quant.per_channel_cast_and_transpose(
    x, fmt='e4m3', num_per_tokens=128
)
print(f"Per-channel+转置 FP8 data shape: {x_pc_t_fp8.shape}")  # (hidden, num_tokens)
```

---

## E5M6 量化（KV Cache 压缩）

E5M6 是 DeepSeek 自定义的 12-bit 格式，8 个值打包为 3 个 uint32：

```python
# E5M6 per-token 量化
# 要求 num_per_channels == hidden, hidden % 8 == 0
hidden_e5m6 = 4096  # 必须被8整除
x_e5m6 = torch.randn(num_tokens, hidden_e5m6, device=device, dtype=torch.bfloat16)

x_e5m6_q, x_e5m6_sf = tile_kernels.quant.per_token_cast_to_e5m6(
    x_e5m6, num_per_channels=hidden_e5m6
)

print(f"E5M6 输入 shape: {x_e5m6.shape}")
print(f"E5M6 data shape: {x_e5m6_q.shape}, dtype: {x_e5m6_q.dtype}")
# shape[-1] = hidden * 3 // 2（8个12bit值=12字节=3*uint32）
print(f"E5M6 压缩比: {hidden_e5m6 * 2 / x_e5m6_q.shape[-1]:.2f}x (vs bf16)")

# E5M6 反量化
x_e5m6_deq = tile_kernels.quant.cast_back(
    (x_e5m6_q, x_e5m6_sf), fmt='bf16',
    x_block_size=(1, hidden_e5m6),
    x_special_fmt='e5m6',
)
cos_sim = torch.nn.functional.cosine_similarity(
    x_e5m6.float().flatten(), x_e5m6_deq.float().flatten(), dim=0
)
print(f"E5M6 反量化余弦相似度: {cos_sim.item():.6f}")
```

---

## SwiGLU 融合量化

MoE expert FFN 中的 SwiGLU 激活 + FP8 量化融合：

```python
# 模拟 expert GEMM 输出（gate+up 拼接）
num_expanded_tokens = 8192
ffn_hidden = 4096
gemm_out = torch.randn(
    num_expanded_tokens, ffn_hidden * 2, device=device, dtype=torch.bfloat16
)

# SwiGLU + per-token FP8 量化
swiglu_fp8, swiglu_sf = tile_kernels.quant.swiglu_forward_and_per_token_cast(
    gemm_out,
    fmt='e4m3',
    num_per_channels=128,
    swiglu_clamp_value=None,  # 可选 clamp
)

print(f"SwiGLU 输入 shape: {gemm_out.shape}")  # (tokens, 2*hidden)
print(f"SwiGLU+FP8 输出 shape: {swiglu_fp8.shape}")  # (tokens, hidden) - 已减半
print(f"SwiGLU+FP8 SF shape: {swiglu_sf.shape}")

# SwiGLU + per-channel 量化 + 转置
swiglu_pc_fp8, swiglu_pc_sf = tile_kernels.quant.swiglu_forward_and_per_channel_cast_and_transpose(
    gemm_out, fmt='e4m3', num_per_tokens=128,
)
print(f"SwiGLU+PC+转置 输出 shape: {swiglu_pc_fp8.shape}")  # (hidden, tokens) 转置
```

---

## 使用预计算 SF 量化

如果缩放因子已经预先计算好，可以跳过 amax 计算直接量化：

```python
# 先只计算 SF
sf_only = tile_kernels.quant.per_token_cast_with_sf_only(
    x, fmt='e4m3', num_per_channels=num_per_channels
)

# 使用预计算 SF 量化
x_fp8_precomputed = tile_kernels.quant.per_token_cast_with_precomputed_sf(
    x, fmt='e4m3', num_per_channels=num_per_channels, sf=sf_only
)
print(f"预计算 SF 量化完成，输出 shape: {x_fp8_precomputed.shape}")
```

---

## Round-SF（2的幂次舍入）

将缩放因子舍入到 2 的幂次，反量化时可以用位移替代乘法：

```python
x_fp8_rounded, x_sf_rounded = tile_kernels.quant.per_token_cast(
    x, fmt='e4m3', num_per_channels=num_per_channels, round_sf=True
)
```

---

## 精度对比

```python
# 不同格式的量化精度对比
def test_quant(x, fmt, cast_fn, **kwargs):
    if fmt == 'e5m6':
        x_q, x_sf = cast_fn(x, **kwargs)
        x_dq = tile_kernels.quant.cast_back(
            (x_q, x_sf), fmt='bf16',
            x_block_size=(1, x.shape[-1]),
            x_special_fmt='e5m6',
        )
    else:
        x_q, x_sf = cast_fn(x, fmt=fmt, **kwargs)
        x_dq = tile_kernels.quant.per_token_cast_back(
            (x_q, x_sf), fmt='bf16', num_per_channels=kwargs.get('num_per_channels', 128)
        )
    cos = torch.nn.functional.cosine_similarity(
        x.float().flatten(), x_dq.float().flatten(), dim=0
    )
    return cos.item()

print("=== 量化精度对比 (cosine similarity) ===")
test_x = torch.randn(4096, 4096, device=device, dtype=torch.bfloat16)
print(f"FP8 E4M3 per-token:   {test_quant(test_x, 'e4m3', tile_kernels.quant.per_token_cast, num_per_channels=128):.6f}")
print(f"FP8 E4M3 per-block:   {test_quant(test_x, 'e4m3', tile_kernels.quant.per_block_cast, block_size=(128,128)):.6f}")
print(f"FP4 E2M1 per-token:   {test_quant(test_x, 'e2m1', tile_kernels.quant.per_token_cast, num_per_channels=128):.6f}")
```
