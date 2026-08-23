---
type: api-reference
scope: flash-mla
name: FlashMLA Python API 参考
version: "1.0.0"
source: flash_mla/__init__.py, flash_mla/flash_mla_interface.py
description: FlashMLA 公共 Python API 完整参考
---

# FlashMLA Python API 参考

FlashMLA 的 Python API 通过 `flash_mla` 包导出，底层通过 pybind11 绑定 C++ CUDA 扩展模块 `flash_mla.cuda`。公共 API 共导出 6 个符号，涵盖 MLA 解码、稀疏注意力预填充和变长注意力三大类功能。

---

## 一、MLA 解码核函数

### 1.1 `get_mla_metadata`

```python
def get_mla_metadata(*args, **kwargs) -> Tuple[FlashMLASchedMeta, None]
```

获取 FlashMLA 的 tile 调度元数据。当前版本（v1.0.0）采用延迟初始化策略：该函数返回一个空的 `FlashMLASchedMeta` 实例，实际的调度元数据在第一次调用 `flash_mla_with_kvcache` 时自动生成。

- **参数**：无需任何参数（保留 `*args, **kwargs` 仅为兼容旧接口）
- **返回值**：`(FlashMLASchedMeta(), None)` 元组，仅第一个元素有用
- **说明**：同一个 `FlashMLASchedMeta` 实例可在多次调用间复用，但前提是张量形状和 `cache_seqlens`、`topk_length`、`extra_topk_length` 的值保持不变

```python
from flash_mla import get_mla_metadata

tile_scheduler_metadata, num_splits = get_mla_metadata()
# num_splits 始终为 None，为兼容旧接口保留
```

### 1.2 `flash_mla_with_kvcache`

```python
def flash_mla_with_kvcache(
    q: torch.Tensor,
    k_cache: torch.Tensor,
    block_table: Optional[torch.Tensor],
    cache_seqlens: Optional[torch.Tensor],
    head_dim_v: int,
    tile_scheduler_metadata: FlashMLASchedMeta,
    num_splits: None = None,
    softmax_scale: Optional[float] = None,
    causal: bool = False,
    is_fp8_kvcache: bool = False,
    indices: Optional[torch.Tensor] = None,
    attn_sink: Optional[torch.Tensor] = None,
    extra_k_cache: Optional[torch.Tensor] = None,
    extra_indices_in_kvcache: Optional[torch.Tensor] = None,
    topk_length: Optional[torch.Tensor] = None,
    extra_topk_length: Optional[torch.Tensor] = None
) -> Tuple[torch.Tensor, torch.Tensor]
```

FlashMLA 的核心解码核函数，支持 dense 和 sparse 两种注意力模式，自动根据 `indices` 是否存在路由到对应 C++ 实现。

**参数说明：**

| 参数 | 类型 | 形状 | 说明 |
|---|---|---|---|
| `q` | Tensor (BF16/FP16) | `(b, s_q, h_q, d)` | 查询张量 |
| `k_cache` | Tensor | `(num_blocks, page_block_size, h_k, d)`（dense）或按字节布局（sparse FP8） | KV Cache |
| `block_table` | Tensor (int32) | `(b, max_num_blocks_per_seq)` | 页表，dense 模式必需，sparse 模式为 None |
| `cache_seqlens` | Tensor (int32) | `(b,)` | 各序列 KV 长度，dense 模式必需，sparse 模式为 None |
| `head_dim_v` | int | 标量 | V 的头维度，必须为 512 |
| `tile_scheduler_metadata` | FlashMLASchedMeta | — | `get_mla_metadata()` 返回值 |
| `num_splits` | None | — | 必须为 None（兼容旧接口） |
| `softmax_scale` | float | 标量 | QK^T 缩放因子，默认 `1/sqrt(d)` |
| `causal` | bool | — | 是否使用因果掩码，仅 dense 模式有效 |
| `is_fp8_kvcache` | bool | — | KV cache 是否为 FP8 格式 |
| `indices` | Tensor (int32) | `(b, s_q, topk)` | 稀疏注意力索引，提供时启用 sparse 模式 |
| `attn_sink` | Tensor (float32) | `(h_q,)` | 可选注意力 sink，输出乘以 `exp(lse)/(exp(lse)+exp(attn_sink))` |
| `extra_k_cache` | Tensor | — | 额外 KV cache（sparse 模式可选） |
| `extra_indices_in_kvcache` | Tensor (int32) | — | 额外 KV cache 的索引 |
| `topk_length` | Tensor (int32) | `(b,)` | 各 batch 实际有效 topk 数量 |
| `extra_topk_length` | Tensor (int32) | `(b,)` | 额外 KV cache 的 topk 长度 |

**返回值：**

| 返回值 | 类型 | 形状 | 说明 |
|---|---|---|---|
| `out` | Tensor (BF16) | `(b, s_q, h_q, head_dim_v)` | 注意力输出 |
| `softmax_lse` | Tensor (float32) | `(b, h_q, s_q)` | 注意力分数的 log-sum-exp |

**内部路由逻辑：**
- `indices is not None` → sparse decode → `flash_mla_cuda.sparse_decode_fwd()`，要求 `causal=False`、`is_fp8_kvcache=True`
- `indices is None` → dense decode → `flash_mla_cuda.dense_decode_fwd()`，要求 block_table 和 cache_seqlens 不为 None
- 首次调用时进行 sanity check 并初始化 `sched_meta.config`，后续调用验证参数一致性

### 1.3 `FlashMLASchedMeta` 数据类

```python
@dataclasses.dataclass
class FlashMLASchedMeta:
    @dataclasses.dataclass
    class Config:
        b: int
        s_q: int
        h_q: int
        page_block_size: int
        h_k: int
        causal: bool
        is_fp8_kvcache: bool
        topk: Optional[int]
        extra_page_block_size: Optional[int]
        extra_topk: Optional[int]

    have_initialized: bool = False
    config: Optional[Config] = None
    tile_scheduler_metadata: Optional[torch.Tensor] = None  # (num_sm_parts, TileSchedulerMetaDataSize), int32
    num_splits: Optional[torch.Tensor] = None               # (b+1), int32
```

存储 FlashMLA tile 调度元数据的数据类。首次调用 `flash_mla_with_kvcache` 后，`tile_scheduler_metadata` 和 `num_splits` 会被填充为实际的调度张量。

---

## 二、Sparse MLA Prefill 核函数

### 2.1 `flash_mla_sparse_fwd`

```python
def flash_mla_sparse_fwd(
    q: torch.Tensor,
    kv: torch.Tensor,
    indices: torch.Tensor,
    sm_scale: float,
    d_v: int = 512,
    attn_sink: Optional[torch.Tensor] = None,
    topk_length: Optional[torch.Tensor] = None,
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]
```

Sparse attention prefill 核函数，用于预填充阶段的 token 级稀疏注意力计算。

**参数说明：**

| 参数 | 类型 | 形状 | 说明 |
|---|---|---|---|
| `q` | Tensor (BF16) | `(s_q, h_q, d_qk)` | 查询张量（3D，无 batch 维度） |
| `kv` | Tensor (BF16) | `(s_kv, h_kv, d_qk)` | KV 张量（3D，无 batch 维度） |
| `indices` | Tensor (int32) | `(s_q, h_kv, topk)` | 稀疏注意力索引，无效索引设为 -1 或 >= s_kv |
| `sm_scale` | float | 标量 | Softmax 缩放因子 |
| `d_v` | int | 标量 | Value 维度，只能为 512 |
| `attn_sink` | Tensor (float32) | `(h_q,)` | 可选注意力 sink |
| `topk_length` | Tensor (int32) | `(s_q,)` | 各 query 实际有效 topk 数量 |

**返回值：**

| 返回值 | 类型 | 形状 | 说明 |
|---|---|---|---|
| `output` | Tensor (BF16) | `(s_q, h_q, d_v)` | 注意力输出 |
| `max_logits` | Tensor (float32) | `(s_q, h_q)` | 注意力分数最大值 |
| `lse` | Tensor (float32) | `(s_q, h_q)` | 注意力分数的 log-sum-exp（以 2 为底） |

**注意事项：**
- 该核函数不支持 batch 维度。多 batch 推理需手动 reshape 输入张量并调整 indices
- h_kv 必须为 1（MQA 模式）
- 内部调用 `flash_mla_cuda.sparse_prefill_fwd()`

---

## 三、Dense MHA Prefill 核函数（变长）

### 3.1 `flash_attn_varlen_func`

```python
def flash_attn_varlen_func(
    q: torch.Tensor,
    k: torch.Tensor,
    v: torch.Tensor,
    cu_seqlens_qo: torch.Tensor,
    cu_seqlens_kv: torch.Tensor,
    max_seqlen_qo: int,
    max_seqlen_kv: int,
    dropout_p: float = 0.0,
    softmax_scale: Optional[float] = None,
    causal: bool = False,
    deterministic: bool = False,
    is_varlen: bool = True,
) -> Tuple[torch.Tensor, torch.Tensor]
```

Dense 变长注意力前向核函数（仅 SM100），基于 CUTLASS 实现标准 MHA 模式（非 MLA 压缩）。

**参数说明：**

| 参数 | 形状 | 说明 |
|---|---|---|
| `q` | `(qo_total_len, num_qo_heads, head_dim_qk)` | 拼接后的 Q 张量 |
| `k` | `(kv_total_len, num_kv_heads, head_dim_qk)` | 拼接后的 K 张量 |
| `v` | `(kv_total_len, num_kv_heads, head_dim_vo)` | 拼接后的 V 张量 |
| `cu_seqlens_qo` | `(batch_size + 1,)` int32 | Q 序列累积长度前缀和 |
| `cu_seqlens_kv` | `(batch_size + 1,)` int32 | KV 序列累积长度前缀和 |
| `max_seqlen_qo` | int | 最大 Q 序列长度 |
| `max_seqlen_kv` | int | 最大 KV 序列长度 |
| `dropout_p` | float | 必须为 0.0（不支持 dropout） |
| `deterministic` | bool | 必须为 False |

**返回值**：`(out, lse)`，out 形状 `(qo_total_len, num_qo_heads, head_dim_vo)`，lse 形状 `(num_qo_heads, qo_total_len)`。

**注意**：反向传播不支持 GQA（`num_qo_heads != num_kv_heads` 时抛出 ValueError）。

### 3.2 `flash_attn_varlen_qkvpacked_func`

```python
def flash_attn_varlen_qkvpacked_func(
    qkv: torch.Tensor,
    cu_seqlens: torch.Tensor,
    max_seqlen: int,
    head_dim_qk: int,
    dropout_p: float = 0.0,
    softmax_scale: Optional[float] = None,
    causal: bool = False,
    deterministic: bool = False,
    is_varlen: bool = True,
) -> Tuple[torch.Tensor, torch.Tensor]
```

QKV 打包版本，`qkv` 形状为 `(total_len, num_heads, head_dim_qk * 3)`，按 `head_dim_qk` 切分为 Q/K/V 三部分。

### 3.3 `flash_attn_varlen_kvpacked_func`

```python
def flash_attn_varlen_kvpacked_func(
    q: torch.Tensor,
    kv: torch.Tensor,
    cu_seqlens_qo: torch.Tensor,
    cu_seqlens_kv: torch.Tensor,
    max_seqlen_qo: int,
    max_seqlen_kv: int,
    head_dim_qk: int,
    dropout_p: float = 0.0,
    softmax_scale: Optional[float] = None,
    causal: bool = False,
    deterministic: bool = False,
    is_varlen: bool = True,
) -> Tuple[torch.Tensor, torch.Tensor]
```

KV 打包版本，`kv` 形状为 `(kv_total_len, num_kv_heads, head_dim_qk * 2)`，切分为 K/V 两部分。

---

## 四、C++ 扩展模块（pybind11 导出）

底层 C++ 扩展 `flash_mla.cuda` 导出以下 5 个函数：

| C++ 函数 | Python 绑定 | 说明 |
|---|---|---|
| `sparse_attn_decode_interface` | `sparse_decode_fwd` | Sparse MLA 解码前向 |
| `dense_attn_decode_interface` | `dense_decode_fwd` | Dense MLA 解码前向 |
| `sparse_attn_prefill_interface` | `sparse_prefill_fwd` | Sparse MLA 预填充前向 |
| `FMHACutlassSM100FwdRun` | `dense_prefill_fwd` | Dense MHA 预填充前向（SM100 CUTLASS） |
| `FMHACutlassSM100BwdRun` | `dense_prefill_bwd` | Dense MHA 预填充反向（SM100 CUTLASS） |

---

## 五、相关链接

- [/deepseek/flash-mla/concepts/overview](/ai/deepseek/flash-mla/concepts/overview) — FlashMLA 整体架构概述
- [/deepseek/flash-mla/concepts/mla-decoding](/ai/deepseek/flash-mla/concepts/mla-decoding) — MLA 解码算法原理
- [/deepseek/flash-mla/concepts/splitkv](/ai/deepseek/flash-mla/concepts/splitkv) — SplitKV 长序列技术
- [/deepseek/flash-mla/concepts/kv-cache-quantization](/ai/deepseek/flash-mla/concepts/kv-cache-quantization) — FP8 KV cache 量化格式
- [/deepseek/flash-mla/examples/basic-decoding](/ai/deepseek/flash-mla/examples/basic-decoding) — MLA 解码使用示例
- [/deepseek/flash-mla/examples/benchmark](/ai/deepseek/flash-mla/examples/benchmark) — 性能基准测试指南
- [/deepseek/flash-mla/references/kernel-architecture](/ai/deepseek/flash-mla/references/kernel-architecture) — SM90/SM100 内核架构详解
- [/deepseek/flash-mla/references/kv-cache-layout](/ai/deepseek/flash-mla/references/kv-cache-layout) — KV cache 内存布局
