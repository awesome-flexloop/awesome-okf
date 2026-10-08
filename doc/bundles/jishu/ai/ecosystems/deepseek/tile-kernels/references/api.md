---
type: api-reference
scope: tile-kernels
name: TileKernels 公共 API 参考
version: "0.1.0"
source: tile_kernels/__init__.py, tile_kernels/config.py, tile_kernels/quant/__init__.py, tile_kernels/moe/__init__.py, tile_kernels/engram/__init__.py, tile_kernels/modeling/
description: TileKernels 公共 Python API 完整参考
---

# TileKernels 公共 API 参考

TileKernels 的 Python API 通过 `tile_kernels` 包导出，按功能分为配置管理、量化核函数、MoE 核函数、MHC 建模层、Engram 建模层、转置、PyTorch 参考实现、测试工具八大类。

---

## 一、配置管理

### get_num_sms

```python
tile_kernels.get_num_sms() -> int
```

返回当前配置使用的 SM（Streaming Multiprocessor）数量。若未通过 `set_num_sms()` 显式设置，则返回当前 GPU 的物理 SM 数量（通过 `torch.cuda.get_device_properties` 查询，结果带 LRU 缓存）。

### set_num_sms

```python
tile_kernels.set_num_sms(num_sms: int) -> None
```

设置全局使用的 SM 数量。断言 `0 < num_sms <= get_device_num_sms()`。用于控制 kernel 启动的 SM 数量，配合 MPS 实现多实例公平共享，或在 partial reduce 场景中控制并行度。

### get_device_num_sms

```python
tile_kernels.get_device_num_sms() -> int
```

查询当前 CUDA 设备的物理 SM 数量，使用 `@functools.lru_cache(maxsize=None)` 缓存结果。

### get_max_smem_per_sm

```python
tile_kernels.get_max_smem_per_sm() -> int
```

查询每个 SM 的最大共享内存大小（字节），使用 `@functools.lru_cache(maxsize=None)` 缓存结果。

---

## 二、量化核函数（quant）

量化核函数统一通过 `tile_kernels.quant` 子模块访问。量化结果为 `QuantTensor = tuple[torch.Tensor, torch.Tensor]`，即 `(data, scale_factors)` 二元组。

### per_token_cast

```python
tile_kernels.quant.per_token_cast(
    x: torch.Tensor,
    fmt: str,
    num_per_channels: int,
    x_block_size: tuple[int, int] | None = None,
    use_tma_aligned_col_major_sf: bool = False,
    round_sf: bool = False,
    use_packed_ue8m0: bool = False,
) -> QuantTensor
```

逐 token 量化。每行（token）独立计算缩放因子。

- **fmt**：`'e4m3'`（FP8 E4M3）或 `'e2m1'`（FP4 E2M1，packed 为 int8）
- **num_per_channels**：每个缩放因子覆盖的 channel 数
- **x_block_size**：可选输入 block 大小，默认 `(1, num_per_channels)`
- **round_sf**：是否将缩放因子舍入到 2 的幂次
- **use_packed_ue8m0**：是否使用 UE8M0 打包缩放因子
- **返回**：`(quantized_data, scale_factors)`，data 为对应精度 tensor，sf 为 float32 或 uint8

### per_token_cast_with_sf_only

```python
tile_kernels.quant.per_token_cast_with_sf_only(...) -> torch.Tensor
```

仅计算缩放因子，不输出量化数据。参数同 `per_token_cast`。

### per_token_cast_with_precomputed_sf

```python
tile_kernels.quant.per_token_cast_with_precomputed_sf(
    x: torch.Tensor,
    fmt: str,
    num_per_channels: int,
    sf: torch.Tensor,
    ...
) -> torch.Tensor
```

使用预计算的缩放因子进行量化，仅返回量化数据。

### per_token_cast_to_e5m6

```python
tile_kernels.quant.per_token_cast_to_e5m6(
    x: torch.Tensor,
    num_per_channels: int,
    use_tma_aligned_col_major_sf: bool = False,
    round_sf: bool = False,
    use_packed_ue8m0: bool = False,
) -> QuantTensor
```

逐 token 量化到 E5M6 格式（1位符号+5位指数+6位尾数，bias=15）。

- **约束**：`num_per_channels` 必须等于 `hidden`；`hidden % 8 == 0`
- **输出**：data 为 uint8（8 个 E5M6 值打包为 3 个 uint32=96 位=12 字节），shape 为 `(num_tokens, hidden*3//2)`
- **数值范围**：max_normal=65024.0, min_normal=2^-14

### per_block_cast

```python
tile_kernels.quant.per_block_cast(
    x: torch.Tensor,
    fmt: str,
    block_size: tuple[int, int],
    use_tma_aligned_col_major_sf: bool = False,
    round_sf: bool = False,
    use_packed_ue8m0: bool = False,
) -> QuantTensor
```

逐 block 量化。每个 `block_size` 大小的块独立计算缩放因子，常用于权重量化。

- **fmt**：`'e4m3'` 或 `'e2m1'`
- **block_size**：`(block_m, block_k)` 元组

### per_block_cast_with_sf_only

```python
tile_kernels.quant.per_block_cast_with_sf_only(...) -> torch.Tensor
```

仅计算 per-block 缩放因子。

### per_block_cast_with_precomputed_sf

```python
tile_kernels.quant.per_block_cast_with_precomputed_sf(...) -> torch.Tensor
```

使用预计算 sf 进行 per-block 量化。

### per_channel_cast

```python
tile_kernels.quant.per_channel_cast(
    x: torch.Tensor,
    fmt: str,
    num_per_tokens: int,
    round_sf: bool = False,
) -> QuantTensor
```

逐 channel 量化（缩放因子沿 token 维度分组）。

- **约束**：fmt 必须为 `'e4m3'`；`num_tokens % 128 == 0`；`hidden % 64 == 0`；`num_per_tokens` 必须为 128

### per_channel_cast_fused

```python
tile_kernels.quant.per_channel_cast_fused(
    x: torch.Tensor | QuantTensor,
    fmt: str,
    num_per_tokens: int,
    round_sf: bool = False,
    num_per_channels: int | None = None,
    pos_to_token: torch.Tensor | None = None,
) -> QuantTensor
```

融合 per-channel 量化，支持 FP8 输入反量化重缩放（当 x 为 QuantTensor 时）和 pos_to_token token 扩展/gather。

- **约束**：fmt 必须为 `'e4m3'`；`num_per_tokens` 必须为 128；使用 pos_to_token 时输出 token 数需 16 对齐，否则 128 对齐

### per_channel_cast_and_transpose

```python
tile_kernels.quant.per_channel_cast_and_transpose(
    x: torch.Tensor,
    fmt: str,
    num_per_tokens: int,
    round_sf: bool = False,
) -> QuantTensor
```

逐 channel 量化 + 转置融合，输出为 `(hidden, num_tokens)` 布局。

### cast_back

```python
tile_kernels.quant.cast_back(
    x: QuantTensor,
    fmt: str,
    x_block_size: tuple[int, int],
    x_special_fmt: str | None = None,
) -> torch.Tensor
```

反量化：将低精度 QuantTensor 转回高精度。

- **fmt**：`'bf16'` 或 `'fp32'`
- **x_block_size**：量化时的 block 大小
- **x_special_fmt**：可选 `'e5m6'` 表示输入为 E5M6 格式

### per_token_cast_back

```python
tile_kernels.quant.per_token_cast_back(
    x: QuantTensor,
    fmt: str,
    num_per_channels: int,
    x_special_fmt: str | None = None,
) -> torch.Tensor
```

逐 token 反量化，等价于 `cast_back(x, fmt, (1, num_per_channels), ...)`。

### per_block_cast_lossless

```python
tile_kernels.quant.per_block_cast_lossless(
    x: QuantTensor,
    fmt: str,
    x_block_size: tuple[int, int],
    out_block_size: tuple[int, int],
    use_tma_aligned_col_major_sf: bool = False,
    round_sf: bool = False,
    use_packed_ue8m0: bool = False,
) -> QuantTensor
```

FP4 → FP8 无损重量化。输入必须为 E2M1（FP4）格式，输出为 E4M3（FP8）格式。

- **约束**：fmt 必须为 `'e4m3'`

### swiglu_forward_and_per_token_cast

```python
tile_kernels.quant.swiglu_forward_and_per_token_cast(
    x: torch.Tensor,
    fmt: str,
    num_per_channels: int,
    pos_to_token_topk: torch.Tensor | None = None,
    topk_weights: torch.Tensor | None = None,
    pos_to_expert: torch.Tensor | None = None,
    use_tma_aligned_col_major_sf: bool = False,
    round_sf: bool = False,
    use_packed_ue8m0: bool = False,
    swiglu_clamp_value: float | None = None,
    clamped_count: torch.Tensor | None = None,
    sf_clamp_min: float | None = None,
) -> QuantTensor
```

融合 SwiGLU 激活（`silu(x_left) * x_right`）+ 按路由权重缩放 + FP8 量化。MoE 场景下 expert GEMM 后的融合算子。

- **约束**：fmt 必须为 `'e4m3'`
- **x**：shape `(num_expanded_tokens, hidden*2)`，bfloat16

### swiglu_backward_and_per_token_cast

```python
tile_kernels.quant.swiglu_backward_and_per_token_cast(
    x: QuantTensor,
    grad_out: torch.Tensor,
    weight: torch.Tensor,
    pos_to_token_topk: torch.Tensor,
    token_topk_to_pos: torch.Tensor,
    num_per_channels: int,
    round_sf: bool = False,
    swiglu_clamp_value: float | None = None,
) -> tuple[torch.Tensor, QuantTensor, torch.Tensor, torch.Tensor]
```

SwiGLU 反向传播 + 梯度 FP8 量化融合。

- **返回**：`(out_bf16, (x_grad_fp8, x_grad_fp8_sf), x_grad_bf16, weight_grad)`
- **约束**：`num_per_channels` 必须为 32 或 128；输入 x 为 FP8 格式

### swiglu_forward_and_per_channel_cast_and_transpose

```python
tile_kernels.quant.swiglu_forward_and_per_channel_cast_and_transpose(
    x: torch.Tensor,
    fmt: str,
    num_per_tokens: int,
    round_sf: bool = False,
    without_transpose: bool = False,
    swiglu_clamp_value: float | None = None,
) -> QuantTensor
```

SwiGLU 前向 + per-channel 量化 + 转置融合。

- **约束**：fmt 必须为 `'e4m3'`；x 必须为 bfloat16；`num_tokens % 128 == 0`；`hidden % 128 == 0`；`num_per_tokens` 为 32 或 128
- **without_transpose=True**：输出保持 `(num_tokens, hidden)` 布局

### unpack_from_e2m1fn_x2

```python
tile_kernels.quant.unpack_from_e2m1fn_x2(
    x: torch.Tensor,
    out_dtype: torch.dtype = torch.float32,
) -> torch.Tensor
```

将 packed FP4（int8/uint8）解码为高精度张量。FP4 布局为 s(1)|e(2)|m(1)，bias=1。

---

## 三、MoE 核函数（moe）

MoE 核函数通过 `tile_kernels.moe` 子模块访问。

### topk_gate

```python
tile_kernels.moe.topk_gate(
    scores: torch.Tensor,
    num_topk: int,
) -> torch.Tensor
```

TopK 路由门控。

- **输入**：scores shape `(num_tokens, num_experts)`，float32
- **输出**：topk_idx shape `(num_tokens, num_topk)`，int64
- **特性**：稳定排序（ties 时返回较小索引），输出 contiguous

### topk_sum_and_topk_group_idx

```python
tile_kernels.moe.topk_sum_and_topk_group_idx(
    scores: torch.Tensor,
    num_topk_sum: int,
    num_topk_groups: int,
) -> torch.Tensor
```

组内 topk sum 后选择 topk groups。

- **输入**：scores shape `(num_tokens, num_groups, num_experts_per_group)`，float32
- **输出**：group indices shape `(num_tokens, num_topk_groups)`，int64
- **约束**：`num_topk_sum` 仅支持 1 和 2

### top2_sum_gate

```python
tile_kernels.moe.top2_sum_gate(
    logits: torch.Tensor,
    bias: torch.Tensor,
    num_topk: int,
    num_topk_groups: int,
    num_groups: int,
    use_shared_as_routed: bool,
    num_shared_experts: int,
    routed_scaling_factor: float,
    ep_rank: int,
    num_ep_ranks: int,
    tp_rank: int,
    num_tp_ranks: int,
    scoring_func: str,
    mask: torch.Tensor | None = None,
    fix_routing_mask: torch.Tensor | None = None,
    to_physical_map: torch.Tensor | None = None,
    logical_count: torch.Tensor | None = None,
    unmapped_topk_idx: torch.Tensor | None = None,
) -> tuple[torch.Tensor, torch.Tensor]
```

端到端 Top2-Sum 门控路由。支持完整的生产级路由逻辑。

- **输入**：logits shape `(num_tokens, num_routed_experts)`，float32
- **输出**：`(topk_idx, topk_weights)`，shape 分别为 `(num_tokens, num_physical_topk)` 的 int64 和 float32
- **scoring_func**：`'sigmoid'`、`'sqrtsoftplus'` 或 `'softmax'`
- **特性**：shared expert 追加、EP/TP masking、logical→physical expert 映射、固定路由 mask

### get_fused_mapping

```python
tile_kernels.moe.get_fused_mapping(
    topk_idx: torch.Tensor,
    num_experts: int,
    num_expanded_tokens: int,
    alignment: int,
    force_no_sync: bool = False,
) -> tuple
```

构建融合映射表，用于 dispatch/combine。

- **返回**：8元组 `(pos_to_expert, pos_to_token, pos_to_token_topk, token_topk_to_pos, expert_start, expert_end, num_tokens_per_expert, num_tokens_per_expert_list)`
- **num_expanded_tokens=0 且 force_no_sync=False**：自动估算并做 host sync 裁剪

### expand_to_fused

```python
tile_kernels.moe.expand_to_fused(
    x: torch.Tensor,
    token_topk_to_pos: torch.Tensor,
    pos_to_expert: torch.Tensor,
) -> torch.Tensor
```

将 token 数据按 expert 路由扩展排列（dispatch 本地操作）。

- **输入**：x shape `(num_tokens, hidden)`
- **输出**：shape `(num_expanded_tokens, hidden)`

### expand_to_fused_with_sf

```python
tile_kernels.moe.expand_to_fused_with_sf(
    x: QuantTensor,
    num_per_channels: int,
    token_topk_to_pos: torch.Tensor,
    pos_to_expert: torch.Tensor,
    use_tma_aligned_col_major_sf: bool = False,
) -> tuple[torch.Tensor, torch.Tensor]
```

扩展 QuantTensor（同时扩展 data 和 scale factors）。

### reduce_fused

```python
tile_kernels.moe.reduce_fused(
    x: torch.Tensor | QuantTensor,
    topk_weights: torch.Tensor | None,
    token_topk_to_pos: torch.Tensor,
    fp8_format: str = '',
    sf: torch.Tensor | None = None,
    out: torch.Tensor | None = None,
) -> torch.Tensor
```

将 expert 输出加权归约回 token（combine 本地操作）。

- **输入**：expanded tensor shape `(num_expanded_tokens, hidden)` 或 QuantTensor
- **输出**：reduced tensor shape `(num_tokens, hidden)`
- **fp8_format**：`'e4m3'` 时直接输出 FP8 格式
- **约束**：`hidden % 256 == 0`

### aux_fi

```python
tile_kernels.moe.aux_fi(
    topk_idx: torch.Tensor,
    num_experts: int,
    num_aux_topk: int,
) -> torch.Tensor
```

辅助负载均衡频率指示器。计算 `f_i[e] = count[e] * num_experts / (num_tokens * num_aux_topk)`。

- **输出**：float32 tensor shape `(num_experts,)`

### group_count

```python
tile_kernels.moe.group_count(
    group_idx: torch.Tensor,
    num_groups: int,
) -> torch.Tensor
```

统计每组 token 数。

- **输出**：int32 tensor shape `(num_groups,)`

### mask_indices_by_tp

```python
tile_kernels.moe.mask_indices_by_tp(
    indices: torch.Tensor,
    n: int,
    num_ep_ranks: int,
    tp_rank: int,
    num_tp_ranks: int,
) -> torch.Tensor
```

TP（Tensor Parallelism）掩码：非本 TP rank 的 expert 索引设为 -1，本地索引重映射。

### normalize_weight

```python
tile_kernels.moe.normalize_weight(
    topk_weights: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor]
```

归一化 topk 权重（使每个 token 的权重和为 1）。

- **输入**：float32
- **返回**：`(denominator, normalized_weights)`，shape 分别为 `(num_tokens,)` 和 `(num_tokens, num_topk)`

### inplace_unique_group_indices

```python
tile_kernels.moe.inplace_unique_group_indices(
    group_indices: torch.Tensor,
    num_groups: int,
) -> None
```

原地去重 group 索引：每行重复出现的 group 索引（非首次出现）设为 -1。

- **约束**：`num_groups <= 128`

---

## 四、MHC 建模层（modeling.mhc）

MHC 高层 API 通过 `tile_kernels.modeling.mhc` 访问。

### expand_from_embedding

```python
tile_kernels.modeling.mhc.expand_from_embedding(
    x: torch.Tensor,
    mhc_mult: int = 4,
) -> torch.Tensor
```

将 embedding 输出从 `(..., H)` 扩展为 `(..., mhc_mult, H)`，用于初始化 MHC residual。

### mhc_pre

```python
tile_kernels.modeling.mhc.mhc_pre(
    residual: torch.Tensor,
    fn: torch.Tensor,
    scale: torch.Tensor,
    base: torch.Tensor,
    *,
    norm_weight: torch.Tensor | None = None,
    norm_eps: float = 1e-6,
    mhc_mult: int = 4,
    post_mult_value: float = 1.0,
    pre_eps: float = 1e-6,
    sinkhorn_eps: float = 1e-6,
    sinkhorn_repeat: int = 10,
    n_splits: int = 16,
) -> tuple[torch.Tensor, tuple[torch.Tensor, torch.Tensor]]
```

一个子层（attention/FFN）的 MHC 预处理一站式 API。

- **训练模式**：mhc_pre_norm_fn → mhc_pre_split_mixes → sinkhorn_normalize → mhc_pre_apply_mix
- **推理模式**（`not torch.is_grad_enabled()`）：使用 `mhc_pre_big_fuse` 融合 kernel
- **参数**：
  - residual：`(..., mhc_mult, hidden_size)` bf16
  - fn：`[mhc_mult*(mhc_mult+2), mhc_mult*hidden_size]` fp32
  - scale：`[3]` fp32
  - base：`[mhc_mult*(mhc_mult+2)]` fp32
- **返回**：`(layer_input, (post_mix, comb_mix))`

### mhc_head

```python
tile_kernels.modeling.mhc.mhc_head(
    residual: torch.Tensor,
    fn: torch.Tensor,
    scale: torch.Tensor,
    base: torch.Tensor,
    *,
    norm_weight: torch.Tensor | None = None,
    norm_eps: float = 1e-6,
    mhc_mult: int = 4,
    pre_eps: float = 1e-6,
    n_splits: int = 16,
) -> torch.Tensor
```

LM Head 的 MHC 处理，组合 pre_norm_fn + head_compute_mix + pre_apply_mix。

- **fn**：shape `[mhc_mult, mhc_mult*hidden_size]`，内部 pad 到 `[mhc_mult*(mhc_mult+2), ...]`
- **返回**：layer_input shape `(..., hidden_size)`

### MHC 原子 Op

以下原子 Op 通过 `tile_kernels.modeling.mhc.ops` 访问：

| 函数 | 说明 |
|---|---|
| `expand_to_mhc(hidden, mhc_mult, out=None)` | (...,H)→(...,mhc_mult,H) 复制 |
| `mhc_head_compute_mix(input_mix, mhc_scale, mhc_base, mhc_pre_eps)` | sigmoid(input*scale+base)+eps |
| `mhc_pre_norm_fn(residual, mhc_fn, mhc_norm_weight, mhc_norm_eps, fuse_grad_acc=True, n_splits=16)` | RMSNorm+GEMM 预处理 |
| `mhc_pre_split_mixes(input_mixes, mhc_scale, mhc_base, mhc_mult, mhc_post_mult_value, mhc_pre_eps)` | mix 线性变换+分割 |
| `sinkhorn_normalize(x, repeat=10, eps=1e-6)` | Sinkhorn 双随机归一化 |
| `mhc_pre_apply_mix(x, mix, out=None)` | 加权求和归约 mhc 维度 |
| `mhc_post(x, residual, post_layer_mix, comb_res_mix, out=None)` | 后处理 residual 混合 |
| `mhc_post_fwd(...)` / `mhc_post_bwd(...)` | Post 前向/反向独立调用 |
| `mhc_pre_big_fuse(...)` | 推理融合 kernel |
| `mhc_multilayer_recompute(...)` | 多层 MHC residual 原地重计算 |

---

## 五、Engram 建模层（modeling.engram）

### engram_gate

```python
tile_kernels.modeling.engram.engram_gate(
    hidden_states: torch.Tensor,
    k: torch.Tensor,
    v: torch.Tensor,
    weight_hidden: torch.Tensor,
    weight_embed: torch.Tensor,
    clamp_value: float,
    eps: float,
) -> torch.Tensor
```

Engram 门控机制（`EngramGateFn.apply`）。

- **hidden_states/k**：`(*, hc_mult, hidden_size)` bf16
- **v**：`(*, hidden_size)` bf16
- **weight_hidden/weight_embed**：`(hc_mult, hidden_size)` bf16（RMSNorm 权重）
- **计算**：`gate = sigmoid(signed_sqrt(dot(RMSNorm(x,wh), RMSNorm(k,we)) * scalar)); output = hidden_states + gate * v`
- **梯度**：支持 main_grad 模式

---

## 六、Engram 底层核函数（engram）

### fused_weight

```python
tile_kernels.engram.fused_weight(
    weight_hidden: torch.Tensor,
    weight_embed: torch.Tensor,
) -> torch.Tensor
```

逐元素 bf16×bf16→fp32 融合权重乘法。

- **输入**：`(hc_mult, hidden_size)` bf16 × 2
- **输出**：`(hc_mult, hidden_size)` fp32

### engram_gate_fwd

```python
tile_kernels.engram.engram_gate_fwd(
    hidden_states, k, v, weight_fused, eps, clamp_value,
    save_for_backward=True,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]
```

Engram 门前向 kernel。

- **返回**：`(output, dot, gate_score, rstd_x, rstd_k)`

### engram_gate_bwd

```python
tile_kernels.engram.engram_gate_bwd(
    grad_out, hidden_states, k, v, weight_fused,
    dot, gate_score, rstd_x, rstd_k, clamp_value,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]
```

Engram 门反向 kernel。

- **返回**：`(grad_x, grad_k, grad_v, grad_w_partial)`，grad_w_partial 需进一步 reduce

### grad_w_reduce

```python
tile_kernels.engram.grad_w_reduce(
    grad_w_partial: torch.Tensor,
    weight_hidden: torch.Tensor,
    weight_embed: torch.Tensor,
    grad_weight_hidden: torch.Tensor,
    grad_weight_embed: torch.Tensor,
) -> None
```

原地归约 partial 权重梯度并融合权重乘法，累积到 grad_weight 张量。

### engram_hash

```python
tile_kernels.engram.engram_hash(
    ngram_token_ids: torch.Tensor,
    multipliers: torch.Tensor,
    vocab_sizes: torch.Tensor,
    offsets: torch.Tensor,
) -> torch.Tensor
```

N-gram XOR 哈希计算。

- **ngram_token_ids**：`(num_tokens, max_ngram_size)` int32
- **multipliers**：`(num_ngram_layers, max_ngram_size)` int64
- **vocab_sizes**：`(num_ngram_layers, max_ngram_size-1, num_embed_table_per_ngram)` int32
- **offsets**：`(num_ngram_layers, (max_ngram_size-1)*num_embed_table_per_ngram)` int32
- **输出**：`(num_ngram_layers, num_tokens, (max_ngram_size-1)*num_embed_table_per_ngram)` int32

---

## 七、转置（transpose）

### transpose

```python
tile_kernels.transpose(
    x: torch.Tensor,
) -> torch.Tensor
```

2D 张量转置。

- **输入**：`(M, N)`，M 和 N 需被 64 整除，stride(-2)%4==0, stride(-1)==1
- **输出**：`(N, M)`

### batched_transpose

```python
tile_kernels.batched_transpose(
    x: torch.Tensor,
) -> torch.Tensor
```

3D 批量转置。

- **输入**：`(B, M, N)`
- **输出**：`(B, N, M)`

---

## 八、数据类与类型

### QuantTensor

```python
QuantTensor = tuple[torch.Tensor, torch.Tensor]
```

量化张量类型别名，表示 `(data, scale_factors)` 二元组。

### BaseCastConfig

```python
@dataclass(frozen=True)
class BaseCastConfig:
    torch_dtype: torch.dtype = torch.float8_e4m3fn
    sf_block: tuple[int, int] = (1, 1)
    use_tma_aligned_col_major_sf: bool = False
    use_packed_ue8m0: bool = False
```

基础量化配置。属性：
- `dtype`：映射到 TileLang dtype（torch.int8 → T.float4_e2m1fn）
- `sf_torch_dtype`：缩放因子的 torch dtype（packed_ue8m0 时为 torch.uint8，否则 torch.float32）
- `sf_dtype`：缩放因子的 TileLang dtype

### CastInputConfig

```python
@dataclass(frozen=True)
class CastInputConfig(BaseCastConfig):
    with_sf: bool = True
```

输入量化配置，新增 `with_sf` 字段表示输入是否携带缩放因子。

### CastOutputConfig

```python
@dataclass(frozen=True)
class CastOutputConfig(BaseCastConfig):
    round_sf: bool = False
    custom_clamp_min_value: float | None = None
```

输出量化配置。属性 `clamp_min_value`：e4m3 时为 1e-4，e2m1 时为 T.max_value(dtype)*2^-126。

### ScoringFunc

```python
class ScoringFunc(IntEnum):
    SIGMOID = 0
    SQRTSOFTPLUS = 1
    SOFTMAX = 2
    IDENTITY = 3
```

MoE 评分函数枚举。支持 `from_str(label)` 类方法从字符串构造。
