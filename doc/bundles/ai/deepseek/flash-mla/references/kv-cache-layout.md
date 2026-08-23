---
type: reference
scope: flash-mla
name: FlashMLA KV Cache 布局
version: "1.0.0"
source: flash_mla/flash_mla_interface.py, csrc/sm90/decode/sparse_fp8/config.h, csrc/sm100/decode/head64/config.h, csrc/params.h
description: FlashMLA FP8 KV Cache 内存布局、分页结构与量化格式详解
---

# KV Cache 布局与量化格式

FlashMLA 支持两种 KV cache 模式：BF16 dense paged KV cache（dense decoding）和 FP8 量化 KV cache（sparse decoding）。两种模式在内存布局、索引方式和数据格式上有显著差异。

---

## 一、分页 KV Cache 结构（Dense 模式）

### 1.1 Paged Attention 基本概念

FlashMLA 的 dense decode 使用分页注意力（Paged Attention）机制管理 KV cache，灵感来自操作系统的虚拟内存分页：

- **物理存储**：KV cache 被划分为固定大小的物理页块（page block），每个页块包含 `page_block_size=64` 个 token
- **逻辑映射**：`block_table` 作为页表，将每个序列的逻辑 block 映射到物理 block
- **变长支持**：`cache_seqlens` 记录每个序列的实际长度，未使用的页块位置不参与计算

### 1.2 张量形状

| 张量 | 形状 | dtype | 说明 |
|---|---|---|---|
| `k_cache` | `(num_blocks, page_block_size, num_heads_k, head_dim)` | BF16/FP16 | 物理 KV cache 存储 |
| `block_table` | `(batch_size, max_num_blocks_per_seq)` | int32 | 逻辑→物理 block 映射表 |
| `cache_seqlens` | `(batch_size,)` | int32 | 每个序列的实际 KV 长度 |

**参数约束：**
- `page_block_size` 必须为 64（硬编码，当前不支持其他值）
- `head_dim_v` 必须为 512
- `head_dim_k` 支持 576（V32 模式）或 512（MODEL1 模式）
- `num_heads_q % num_heads_k == 0`（GQA/MQA 要求）

### 1.3 索引计算

对于 batch 中第 `i` 个序列的第 `token_pos` 个 KV token：

```
逻辑 block 索引：block_idx = token_pos // page_block_size
block 内偏移：offset_in_block = token_pos % page_block_size
物理 block 索引：physical_block = block_table[i][block_idx]
KV 数据位置：k_cache[physical_block][offset_in_block][:][:]
```

---

## 二、FP8 KV Cache 布局（Sparse 模式）

### 2.1 V32 模式（DeepSeek-V3/V3.1/V3.2）

V32 模式对应 `head_dim_k=576, head_dim_v=512`，每个 token 的 KV cache 占用 **656 字节**，内存布局如下：

```
偏移量 (字节)    大小 (字节)    内容              数据类型        说明
─────────────────────────────────────────────────────────────────────────
0                512            NoPE 部分（量化）  float8_e4m3    512 个 FP8 值（d_noPE=512）
512              16             缩放因子           float32        4 个 scale，每个对应 128 个 FP8 值
528              128            RoPE 部分（未量化） bfloat16       64 个 BF16 值（d_RoPE=64）
─────────────────────────────────────────────────────────────────────────
总计：656 字节/token
```

**量化细节：**
- NoPE（不参与旋转位置编码的部分）使用 FP8 E4M3 量化，每 128 个 FP8 值共享一个 float32 缩放因子
- 缩放因子数量：`NUM_SCALES = d_noPE / QUANT_TILE_SIZE = 512 / 128 = 4`
- RoPE 部分（64 维）不做量化，保持 BF16 精度，因为位置编码对精度更敏感
- V 向量完全包含在 NoPE 的 512 维中（V_HAVE_ROPE = false）

**张量形状：**

| 张量 | 形状 | 说明 |
|---|---|---|
| `k_cache` | `(num_blocks, page_block_size, num_heads_k, head_dim)` | 注意 `head_dim=576` 以元素数量表示，但实际 stride 为 656 字节 |
| 约束 | `num_heads_k == 1` | Sparse decode 仅支持 MQA（h_kv=1） |
| `kv.stride(1) == 656` | | 每个 token 在 block 内的 stride 必须等于 bytes_per_token |

> **重要**：在 FP8 sparse 模式下，`k_cache` 的最后一维 `head_dim=576` 是按 BF16 元素数量计算的（576×2=1152 字节≠656），但实际内存中每个 token 只占 656 字节。TMA 使用 `TMA_K_STRIDE=656` 字节进行加载。张量的 stride 设置反映了这种紧凑布局。

### 2.2 MODEL1 模式

MODEL1 模式对应 `head_dim_k=512, head_dim_v=512`，是 DeepSeek 新配置模型使用的量化格式，每个 token 的 KV cache 占用 **576 字节**。

与 V32 模式的关键区别：
- `d_noPE = 448`（比 V32 少 64 维）
- `QUANT_TILE_SIZE = 64`（比 V32 的 128 更小，更细粒度的量化）
- `V_HAVE_ROPE = true`（V 的计算需要 RoPE 部分参与，而 V32 模式 V 完全在 NoPE 部分中）
- `NUM_SCALES_EACH_TOKEN = 8`（7 个有效 scale + 1 padding，对应 448/64=7 个量化 tile）
- `TMA_K_STRIDE = 576` 字节

MODEL1 模式同样由 FP8 量化的 NoPE 部分、缩放因子和 BF16 RoPE 部分组成，TMA 加载步长为 576 字节/token。具体字节级布局由 SM100 内核定义，主要用于 B200 等 Blackwell GPU 上的推理部署。

### 2.3 两种模式对比

| 属性 | V32 模式 | MODEL1 模式 |
|---|---|---|
| 适用模型 | DeepSeek-V3/V3.1/V3.2/R1 | 新配置模型 |
| head_dim (d_qk) | 576 | 512 |
| head_dim_v (d_v) | 512 | 512 |
| d_noPE（FP8 量化） | 512 维 (512 B) | 448 维 (448 B) |
| d_RoPE（BF16 不量化） | 64 维 (128 B) | 64 维 (128 B) |
| QUANT_TILE_SIZE | 128 | 64 |
| 缩放因子数量 | 4 (float32, 16 B) | 8 (含 padding, 32 B) |
| bytes_per_token | 656 | 576 |
| V 是否含 RoPE | 否（V_HAVE_ROPE=false） | 是（V_HAVE_ROPE=true） |
| SM90 支持 | ✅ | ✅ |
| SM100 支持 | ✅ | ✅ |

---

## 三、Sparse Attention 索引格式

### 3.1 indices 张量编码

Sparse 模式下不使用 `block_table`，而是通过 `indices` 张量直接指定要注意力的 KV token 位置：

```
indices[i][j][k] = physical_block_idx * page_block_size + offset_within_block
```

其中：
- `i`：batch 索引
- `j`：query 序列位置索引（decode 时通常为 0）
- `k`：top-k 索引

**无效索引标记**：无效位置设为 `-1`（或任何 ≥ s_kv 的值）。

### 3.2 Sparse 模式的 KV cache 连续性要求

SM100 上 sparse attention 要求 KV cache 内存必须**连续有效**（contiguously valid），即从 KV cache 的起始字节到最后一字节之间的每个地址都必须是可访问的有效内存（不会触发 IMA）。KV cache 可以是更大数组的切片，但不能是不连续的内存块列表。

---

## 四、Dense 模式 BF16 KV Cache 布局

Dense decode 模式下，KV cache 使用标准 BF16（或 FP16）格式，无量化：

| 张量 | 形状 | dtype |
|---|---|---|
| `k_cache` | `(num_blocks, page_block_size, num_heads_k, head_dim)` | BF16 或 FP16 |

- `head_dim = 576`（V32）或 512（MODEL1）
- `num_heads_k` 可以是 1（MQA）或更多（GQA），需满足 `h_q % h_k == 0`
- 支持 BF16 和 FP16 两种数据类型（FP16 可通过 `FLASH_MLA_DISABLE_FP16` 宏禁用）
- 内存布局：物理 block 连续存储，通过 block_table 进行逻辑到物理的映射

---

## 五、Q 张量 Reshape（Dense Decode）

在 dense decode 的 C++ 入口（`dense_attn_decode_interface`）中，Q 张量会被 reshape 以适配 GQA 模式：

```python
# 原始形状: (b, s_q, h_q, head_dim)
# Reshape 为: (b, q_seq_per_hk, h_k, head_dim)
# 其中 q_seq_per_hk = s_q * (h_q / h_k)
q_reshaped = q.view({b, s_q, h_k, num_q_heads_per_hk, head_size_k})
            .transpose(2, 3)
            .reshape({b, q_seq_per_hk, h_k, head_size_k})
```

这将 query 头按 KV 头分组，使每个 KV 头对应 `h_q/h_k` 个 query 头，便于 GQA 模式下的并行计算。

---

## 六、FP8 反量化

### 6.1 反量化公式

对于 NoPE 部分的反量化：

```
bf16_value = fp8_value * scale[fp8_idx // QUANT_TILE_SIZE]
```

其中：
- V32 模式：`QUANT_TILE_SIZE = 128`，每 128 个 FP8 值共享一个 scale
- MODEL1 模式：`QUANT_TILE_SIZE = 64`，每 64 个 FP8 值共享一个 scale

### 6.2 反量化实现

SM90 上的反量化通过 `cvt_fp8x8_bf16x8` 函数实现：

```cpp
// 将 8 个 FP8 E4M3 值转为 8 个 BF16 值并乘以 scale
__device__ __forceinline__ bf16x8 cvt_fp8x8_bf16x8(
    const fp8x8 &inputs, const __nv_bfloat162 &scale_bf162
);
```

内存加载使用 PTX `ld.global.nc` 指令，并带 L1/L2 缓存提示优化带宽利用：
- L1 缓存策略：`NO_ALLOCATE`、`EVICT_FIRST`、`EVICT_NORMAL`、`EVICT_LAST`
- L2 预取提示：`B64`、`B128`、`B256`

---

## 七、量化参考代码

参见项目中的 `tests/quant.py` 文件，提供了 FP8 量化和反量化的 Python 参考实现。基本流程：

```python
import torch

def quantize_fp8_kv(nope_bf16, rope_bf16, quant_tile_size=128):
    """将 BF16 KV cache 量化为 FP8 格式"""
    # nope_bf16: (..., 512) bfloat16
    # rope_bf16: (..., 64) bfloat16

    # 计算 per-tile 缩放因子
    num_tiles = nope_bf16.shape[-1] // quant_tile_size
    nope_tiles = nope_bf16.view(*nope_bf16.shape[:-1], num_tiles, quant_tile_size)
    scales = nope_tiles.abs().amax(dim=-1) / 448.0  # FP8 E4M3 max ≈ 448
    scales = scales.to(torch.float32)

    # 量化
    nope_fp8 = (nope_tiles / scales.unsqueeze(-1)).to(torch.float8_e4m3fn)
    nope_fp8 = nope_fp8.view(*nope_bf16.shape[:-1], 512)

    # 拼接: FP8 NoPE (512B) + scales (16B) + RoPE BF16 (128B) = 656B/token
    # 实际存储需要按 656 字节 stride 排列
    return nope_fp8, scales, rope_bf16
```

---

## 八、相关链接

- [/deepseek/flash-mla/references/api](/ai/deepseek/flash-mla/references/api) — Python API 参考
- [/deepseek/flash-mla/references/kernel-architecture](/ai/deepseek/flash-mla/references/kernel-architecture) — SM90/SM100 内核架构
- [/deepseek/flash-mla/concepts/kv-cache-quantization](/ai/deepseek/flash-mla/concepts/kv-cache-quantization) — FP8 量化原理与 V32/MODEL1 对比
- [/deepseek/flash-mla/concepts/overview](/ai/deepseek/flash-mla/concepts/overview) — FlashMLA 整体概述
