---
type: example
scope: flash-mla
name: MLA 解码基础使用示例
version: "1.0.0"
source: README.md, tests/test_flash_mla_dense_decoding.py, tests/test_flash_mla_sparse_decoding.py
description: FlashMLA MLA 解码核函数的基础使用方法，包括 dense 和 sparse 两种模式
---

# MLA 解码基础使用示例

本文档展示如何使用 FlashMLA 进行 MLA 解码计算，包括 dense BF16 模式和 sparse FP8 模式的基本用法。

---

## 一、环境要求

```python
import torch
assert torch.cuda.is_available()
major, minor = torch.cuda.get_device_capability()
assert major >= 9, "FlashMLA requires Hopper (SM90) or Blackwell (SM100) GPU"
```

- CUDA ≥ 12.8（SM100 需要 12.9+）
- PyTorch ≥ 2.0
- FlashMLA 已通过 `pip install -v .` 安装

---

## 二、Dense MLA 解码（BF16）

Dense 模式是最基础的用法，适用于标准自回归解码场景。

### 2.1 完整示例

```python
import torch
from flash_mla import get_mla_metadata, flash_mla_with_kvcache

def setup_dense_kv_cache(
    batch_size: int,
    max_seq_len: int,
    num_kv_heads: int,
    head_dim: int,
    page_block_size: int = 64,
    dtype: torch.dtype = torch.bfloat16,
    device: str = "cuda",
):
    """初始化分页 KV cache 和相关张量"""
    # 计算需要的 block 数量
    max_num_blocks_per_seq = (max_seq_len + page_block_size - 1) // page_block_size
    total_blocks = batch_size * max_num_blocks_per_seq

    # 分配 KV cache（物理存储）
    k_cache = torch.randn(
        total_blocks, page_block_size, num_kv_heads, head_dim,
        dtype=dtype, device=device
    )

    # 页表：逻辑 block → 物理 block
    block_table = torch.arange(
        batch_size * max_num_blocks_per_seq,
        dtype=torch.int32, device=device
    ).view(batch_size, max_num_blocks_per_seq)

    # 各序列当前长度（随机生成长度用于测试）
    cache_seqlens = torch.randint(
        1, max_seq_len + 1, (batch_size,),
        dtype=torch.int32, device=device
    )

    return k_cache, block_table, cache_seqlens


def dense_mla_decode_example():
    """Dense MLA 解码示例（V32 模式：head_dim=576, dv=512）"""
    # 配置参数
    batch_size = 128
    s_q = 1              # decode 时每次只生成 1 个 token
    h_q = 128            # query 头数
    h_kv = 1             # KV 头数（MQA）
    head_dim = 576       # V32 模式
    head_dim_v = 512     # V 维度
    max_seq_len = 4096
    dtype = torch.bfloat16
    device = "cuda"

    # 1. 初始化 KV cache
    k_cache, block_table, cache_seqlens = setup_dense_kv_cache(
        batch_size, max_seq_len, h_kv, head_dim, dtype=dtype, device=device
    )

    # 2. 获取调度元数据（返回空的 FlashMLASchedMeta，首次调用时自动初始化）
    tile_scheduler_metadata, num_splits = get_mla_metadata()

    # 3. 准备 query（当前 step 的查询向量）
    q = torch.randn(
        batch_size, s_q, h_q, head_dim,
        dtype=dtype, device=device
    )

    # 4. 第一次调用（会触发调度元数据初始化）
    out, lse = flash_mla_with_kvcache(
        q=q,
        k_cache=k_cache,
        block_table=block_table,
        cache_seqlens=cache_seqlens,
        head_dim_v=head_dim_v,
        tile_scheduler_metadata=tile_scheduler_metadata,
        num_splits=num_splits,       # 必须为 None
        causal=True,                 # 因果掩码
        is_fp8_kvcache=False,        # BF16 模式
    )

    # 验证输出形状
    assert out.shape == (batch_size, s_q, h_q, head_dim_v)
    assert lse.shape == (batch_size, h_q, s_q)
    print(f"Dense MLA decode output shape: {out.shape}")
    print(f"LSE shape: {lse.shape}")

    # 5. 后续解码步骤（复用同一个 tile_scheduler_metadata）
    for step in range(1, 10):
        # 生成新的 query（实际场景中由模型前向计算得到）
        q_new = torch.randn(batch_size, s_q, h_q, head_dim, dtype=dtype, device=device)

        # 追加新 token 到 KV cache（实际场景中需要更新 cache_seqlens 和 block_table）
        # ...

        # 解码（注意：形状和 cache_seqlens 必须与首次一致，否则会 assertion error）
        out_new, lse_new = flash_mla_with_kvcache(
            q=q_new,
            k_cache=k_cache,
            block_table=block_table,
            cache_seqlens=cache_seqlens,  # 实际场景中长度会递增
            head_dim_v=head_dim_v,
            tile_scheduler_metadata=tile_scheduler_metadata,
            causal=True,
            is_fp8_kvcache=False,
        )

    return out, lse


# 运行示例
out, lse = dense_mla_decode_example()
```

### 2.2 FP16 Dense 解码

FlashMLA 也支持 FP16（半精度）数据类型（除非编译时设置了 `FLASH_MLA_DISABLE_FP16`）：

```python
k_cache_fp16 = k_cache.to(torch.float16)
q_fp16 = q.to(torch.float16)

out_fp16, lse_fp16 = flash_mla_with_kvcache(
    q=q_fp16,
    k_cache=k_cache_fp16,
    block_table=block_table,
    cache_seqlens=cache_seqlens,
    head_dim_v=head_dim_v,
    tile_scheduler_metadata=get_mla_metadata()[0],  # 需要新的 sched_meta
    causal=True,
    is_fp8_kvcache=False,
)
```

---

## 三、Sparse MLA 解码（FP8 KV Cache）

Sparse 模式使用 FP8 量化 KV cache 和 token 级稀疏注意力（DSA），适用于 DeepSeek-V3.2 等支持稀疏注意力的模型。

### 3.1 FP8 KV Cache 准备

```python
def create_fp8_kv_cache_v32(
    batch_size: int,
    max_seq_len: int,
    page_block_size: int = 64,
    device: str = "cuda",
):
    """
    创建 V32 模式的 FP8 KV cache
    每 token 656 字节：512B FP8 NoPE + 16B FP32 scales + 128B BF16 RoPE
    """
    d_qk = 576
    d_noPE = 512
    d_RoPE = 64
    num_heads_k = 1  # sparse decode 仅支持 MQA
    bytes_per_token = 656  # V32

    max_num_blocks_per_seq = (max_seq_len + page_block_size - 1) // page_block_size
    total_blocks = batch_size * max_num_blocks_per_seq

    # FP8 KV cache 以 uint8 张量分配
    k_cache = torch.zeros(
        total_blocks, page_block_size, num_heads_k, bytes_per_token,
        dtype=torch.uint8, device=device
    )

    # 填充示例数据
    for block_idx in range(total_blocks):
        for token_idx in range(page_block_size):
            # NoPE 部分：512 个 FP8 E4M3 值
            nope_data = torch.randn(d_noPE, dtype=torch.bfloat16, device=device)
            # 简单 per-tensor 量化（实际应使用 per-tile 量化）
            scale = nope_data.abs().max() / 448.0
            nope_fp8 = (nope_data.float() / scale).clamp(-448, 448).to(torch.float8_e4m3fn)

            # Scales：4 个 float32（per 128 FP8 values）
            scales = torch.full((4,), scale.item(), dtype=torch.float32, device=device)

            # RoPE 部分：64 个 BF16 值
            rope_data = torch.randn(d_RoPE, dtype=torch.bfloat16, device=device)

            # 写入 KV cache
            offset = 0
            k_cache[block_idx, token_idx, 0, offset:offset+d_noPE] = nope_fp8.view(torch.uint8)
            offset += d_noPE
            k_cache[block_idx, token_idx, 0, offset:offset+16] = scales.view(torch.uint8)
            offset += 16
            k_cache[block_idx, token_idx, 0, offset:offset+128] = rope_data.view(torch.uint8)

    return k_cache
```

### 3.2 Sparse Indices 准备

```python
def create_sparse_indices(
    batch_size: int,
    s_q: int,
    topk: int,
    max_seq_len: int,
    page_block_size: int = 64,
    device: str = "cuda",
):
    """
    创建 sparse attention 的 indices 张量
    indices[i][j][k] = physical_block_idx * page_block_size + offset_within_block
    """
    # 随机选择 topk 个历史 token（实际场景由稀疏注意力路由算法生成）
    indices = torch.randint(
        0, max_seq_len, (batch_size, s_q, topk),
        dtype=torch.int32, device=device
    )
    return indices
```

### 3.3 完整 Sparse 解码示例

```python
def sparse_mla_decode_example():
    """Sparse FP8 MLA 解码示例（V32 模式）"""
    # 配置参数
    batch_size = 64
    s_q = 1
    h_q = 128
    d_qk = 576       # V32
    d_v = 512
    topk = 64        # 每个 query 关注 top-64 个 KV token
    max_seq_len = 8192
    dtype = torch.bfloat16
    device = "cuda"

    # 1. 创建 FP8 KV cache
    k_cache_fp8 = create_fp8_kv_cache_v32(batch_size, max_seq_len, device=device)

    # 2. 创建 sparse indices
    indices = create_sparse_indices(batch_size, s_q, topk, max_seq_len, device=device)

    # 3. 获取调度元数据
    tile_scheduler_metadata, num_splits = get_mla_metadata()

    # 4. 准备 query（BF16）
    q = torch.randn(batch_size, s_q, h_q, d_qk, dtype=dtype, device=device)

    # 5. 调用 sparse decode（block_table 和 cache_seqlens 为 None）
    out, lse = flash_mla_with_kvcache(
        q=q,
        k_cache=k_cache_fp8,
        block_table=None,            # sparse 模式不需要
        cache_seqlens=None,          # sparse 模式不需要
        head_dim_v=d_v,
        tile_scheduler_metadata=tile_scheduler_metadata,
        num_splits=None,
        causal=False,                # sparse 模式必须为 False
        is_fp8_kvcache=True,         # FP8 KV cache
        indices=indices,             # 稀疏注意力索引
    )

    assert out.shape == (batch_size, s_q, h_q, d_v)
    print(f"Sparse MLA decode (FP8) output shape: {out.shape}")

    return out, lse
```

### 3.4 带 attn_sink 的 Sparse 解码

```python
def sparse_decode_with_attn_sink():
    """带 attention sink 的 sparse 解码"""
    # ...（初始化同上）

    # attention sink 值（每个 query 头一个）
    attn_sink = torch.zeros(h_q, dtype=torch.float32, device=device)
    # -inf 表示无 sink 影响，+inf 表示输出为 0
    # attn_sink[some_heads] = float('-inf')  # 对某些头无影响

    out, lse = flash_mla_with_kvcache(
        q=q,
        k_cache=k_cache_fp8,
        block_table=None,
        cache_seqlens=None,
        head_dim_v=d_v,
        tile_scheduler_metadata=tile_scheduler_metadata,
        causal=False,
        is_fp8_kvcache=True,
        indices=indices,
        attn_sink=attn_sink,
    )
    return out, lse
```

### 3.5 带 topk_length 的 Sparse 解码

当不同 query 的实际 topk 数量不同时，使用 `topk_length` 避免不必要的计算：

```python
def sparse_decode_with_variable_topk():
    """可变 topk 长度的 sparse 解码"""
    # topk_length 指定每个 batch 实际有效的 topk 数量
    topk_length = torch.randint(32, topk, (batch_size,), dtype=torch.int32, device=device)

    out, lse = flash_mla_with_kvcache(
        q=q,
        k_cache=k_cache_fp8,
        block_table=None,
        cache_seqlens=None,
        head_dim_v=d_v,
        tile_scheduler_metadata=tile_scheduler_metadata,
        causal=False,
        is_fp8_kvcache=True,
        indices=indices,
        topk_length=topk_length,  # 只有前 topk_length[i] 个索引被处理
    )
    return out, lse
```

---

## 四、Sparse MLA Prefill

```python
from flash_mla import flash_mla_sparse_fwd

def sparse_prefill_example():
    """Sparse MLA Prefill 示例（注意：3D 张量，无 batch 维度）"""
    s_q = 1024       # prefill 长度
    s_kv = 4096      # KV 长度
    h_q = 128
    h_kv = 1
    d_qk = 576
    d_v = 512
    topk = 64
    sm_scale = d_qk ** (-0.5)
    dtype = torch.bfloat16
    device = "cuda"

    # 注意：prefill 输入为 3D 张量，无 batch 维度
    q = torch.randn(s_q, h_q, d_qk, dtype=dtype, device=device)
    kv = torch.randn(s_kv, h_kv, d_qk, dtype=dtype, device=device)
    indices = torch.randint(0, s_kv, (s_q, h_kv, topk), dtype=torch.int32, device=device)
    # 无效索引设为 -1 或 >= s_kv
    indices[:, :, topk//2:] = -1

    out, max_logits, lse = flash_mla_sparse_fwd(
        q=q,
        kv=kv,
        indices=indices,
        sm_scale=sm_scale,
        d_v=d_v,
    )

    assert out.shape == (s_q, h_q, d_v)
    assert max_logits.shape == (s_q, h_q)
    assert lse.shape == (s_q, h_q)
    print(f"Sparse prefill output shape: {out.shape}")

    return out, max_logits, lse
```

---

## 五、常见注意事项

1. **page_block_size 固定为 64**：当前版本硬编码 page_block_size=64，不支持其他大小
2. **head_dim_v 必须为 512**：当前只支持 d_v=512
3. **sched_meta 复用约束**：同一个 `FlashMLASchedMeta` 可以复用，但张量形状和 `cache_seqlens`/`topk_length`/`extra_topk_length` 必须保持一致
4. **首次调用开销**：第一次调用 `flash_mla_with_kvcache` 会触发调度元数据生成，性能略低；后续调用正常
5. **Sparse 模式约束**：`causal` 必须为 `False`，`is_fp8_kvcache` 必须为 `True`，`h_kv` 必须为 1
6. **Dense 模式约束**：必须提供 `block_table` 和 `cache_seqlens`，sparse 相关参数必须为 None
7. **SM100 KV cache 连续性**：SM100 上 sparse 模式要求 KV cache 内存连续有效（contiguously valid），不能是不连续的内存块列表

---

## 六、相关链接

- [/deepseek/flash-mla/concepts/overview](/ai/deepseek/flash-mla/concepts/overview) — FlashMLA 概述
- [/deepseek/flash-mla/concepts/mla-decoding](/ai/deepseek/flash-mla/concepts/mla-decoding) — MLA 解码算法
- [/deepseek/flash-mla/references/api](/ai/deepseek/flash-mla/references/api) — Python API 完整参考
- [/deepseek/flash-mla/references/kv-cache-layout](/ai/deepseek/flash-mla/references/kv-cache-layout) — FP8 KV cache 布局
- [/deepseek/flash-mla/examples/benchmark](/ai/deepseek/flash-mla/examples/benchmark) — 性能基准测试指南
