---
type: api-reference
scope: tile-kernels
name: TileKernels MHC 与 Engram 核函数参考
version: "0.1.0"
source: tile_kernels/mhc/, tile_kernels/engram/, tile_kernels/transpose/, tile_kernels/modeling/
description: TileKernels MHC（Multi-Head Compute）、Engram 和转置核函数详细参考
---

# TileKernels MHC 与 Engram 核函数参考

本章节详细描述 TileKernels 的 MHC（Multi-Head Compute）核函数、Engram 记忆机制核函数，以及转置核函数。

---

## 一、MHC（Multi-Head Compute）

MHC 是 DeepSeek-V4 的核心创新结构，通过引入多个"计算头"实现更细粒度的残差特征处理。每个 token 的 hidden states 在 mhc_mult 个头上独立计算后加权合并，配合 Sinkhorn 归一化保证稳定训练。

### 1.1 MHC 计算流水线

**训练模式**（分步 autograd.Function 链）：

```
residual (B, S, mhc_mult, H)
→ mhc_pre_norm_fn:      RMSNorm(residual) → fn_matmul → 输出 (B, S, mhc_mult*(mhc_mult+2), mhc_mult*H)
→ mhc_pre_split_mixes:  sigmoid(input*scale+base)+eps → 分割为 pre/post/comb mix
→ sinkhorn_normalize:   comb_mix 迭代行列归一化为双随机矩阵
→ mhc_pre_apply_mix:    加权求和归约 mhc 维度 → layer_input (B, S, H)
→ [attention/FFN 计算]  → 输出 x (B, S, H)
→ mhc_post:             x + residual 的混合更新 → 新 residual
```

**推理模式**：
- `mhc_pre_big_fuse` 将 norm_fn + split_mixes + sinkhorn + apply_mix 融合为单个 kernel

### 1.2 Expand

将 (..., H) 复制扩展为 (..., mhc_mult, H)，用于初始化 residual。

**底层 JIT kernel**：
- `expand_to_mhc_fwd_tl(hidden: int, mhc_mult: int) -> JITKernel`：前向，blk_n=32, blk_h=128
- `expand_to_mhc_bwd_tl(hidden: int, mhc_mult: int) -> JITKernel`：反向，对 mhc 维度求和归约

**Modeling 封装**：

```python
# 底层 op
tile_kernels.modeling.mhc.ops.expand_to_mhc(hidden, mhc_mult=4, out=None) -> Tensor

# 高层 API
tile_kernels.modeling.mhc.expand_from_embedding(x, mhc_mult=4) -> Tensor
# 将 embedding 输出 (..., H) 扩展为 (..., mhc_mult, H)
```

### 1.3 Head Compute Mix

计算 mix 系数：`output = sigmoid(input * scale + base) + eps`。

**底层 JIT kernel**：
- `_mhc_head_compute_mix_fwd(mhc_mult, mhc_pre_eps, token_block_size=32) -> JITKernel`
- `_mhc_head_compute_mix_bwd(mhc_mult, token_block_size=32, num_sms) -> JITKernel`
  - 使用 `T.alloc_reducer` 做梯度 partial sum 归约
- Pass 配置：`TL_DISABLE_WARP_SPECIALIZED: True`

**Modeling 封装**：

```python
tile_kernels.modeling.mhc.ops.mhc_head_compute_mix(
    input_mix: Tensor,      # 输入 mix 系数
    mhc_scale: Tensor,      # 缩放参数
    mhc_base: Tensor,       # 偏置参数
    mhc_pre_eps: float,     # epsilon
) -> Tensor
```

### 1.4 Pre-Norm-Fn（RMSNorm + GEMM）

MHC 预处理的第一步：RMSNorm + 线性变换。

**底层 JIT kernel**：

| Kernel | 说明 |
|---|---|
| `_mhc_pre_norm_fn_fwd_mul(mhc_mult3, n_rms_group, rms_group_size, token_block=32, hidden_block=256)` | GEMM 前向（矩阵乘） |
| `_mhc_pre_norm_fn_fwd_norm(...)` | RMSNorm 归一化前向 |
| `_mhc_pre_norm_fn_bwd_norm(...)` | RMSNorm 反向 |
| `_mhc_pre_norm_fn_bwd_mul(...)` | GEMM 反向 |

Pass 配置：`TL_DISABLE_WGMMA: True`。

**辅助函数**：

```python
def round_to_tf32(x: torch.Tensor) -> torch.Tensor:
    """将 float32 舍入到 TF32 精度：(x.view(int32) + 0x1000).view(float32)"""
```

**约束**：
- `mhc_mult3 <= 32`
- `rms_group_size % hidden_block == 0`
- TileLang 实现中 `n_splits` 强制为 1（不支持 split-K，大 GEMM 建议使用 DeepGEMM）
- x 必须为 bf16，fn 必须为 fp32

**Modeling 封装**：

```python
tile_kernels.modeling.mhc.ops.mhc_pre_norm_fn(
    residual: Tensor,
    mhc_fn: Tensor,
    mhc_norm_weight: Tensor | None,
    mhc_norm_eps: float = 1e-6,
    fuse_grad_acc: bool = True,
    n_splits: int = 16,
) -> Tensor
```

若 `mhc_norm_weight` 不为 None，先通过 `_MHCFnNormwMerge.apply` 融合 fn 和 normw 权重。

### 1.5 Pre-Split-Mixes

将 input_mixes 经线性变换+sigmoid 后分割为 pre_layer_mix、post_layer_mix、comb_res_mix。

**底层 JIT kernel**：
- `_mhc_pre_split_mixes_fwd(mhc_mult, mhc_post_mult_value, mhc_pre_eps, token_block_size=32)`
- `_mhc_pre_split_mixes_bwd(mhc_mult, mhc_post_mult_value, token_block_size=32, num_sms)`
- Pass 配置：`TL_DISABLE_WARP_SPECIALIZED: True`

**Modeling 封装**：

```python
tile_kernels.modeling.mhc.ops.mhc_pre_split_mixes(
    input_mixes: Tensor,
    mhc_scale: Tensor,
    mhc_base: Tensor,
    mhc_mult: int,
    mhc_post_mult_value: float,
    mhc_pre_eps: float,
) -> tuple[Tensor, Tensor, Tensor]
# 返回 (pre_layer_mix, post_layer_mix, comb_res_mix)
```

支持 main_grad 模式（scale/base 的 fp32 梯度缓冲区）。backward 使用 num_sms 个 partial buffer 做梯度归约。

### 1.6 Sinkhorn Normalize

Sinkhorn 迭代归一化，将 comb_res_mix 转换为双随机矩阵（行和=1，列和=1）。

**底层 JIT kernel**：
- `_mhc_sinkhorn_fwd(hidden_size, token_block=1, repeat=10, eps=1e-6)`
- `_mhc_sinkhorn_bwd(hidden_size, token_block=32, repeat=10, eps=1e-6)`
- Pass 配置：`TL_DISABLE_WARP_SPECIALIZED: True`

**Modeling 封装**：

```python
tile_kernels.modeling.mhc.ops.sinkhorn_normalize(
    x: Tensor,          # 输入需 contiguous
    repeat: int = 10,   # 迭代次数
    eps: float = 1e-6,
) -> Tensor
```

内部先 view 为 (-1, m, m) 后逐 batch 归一化，再 reshape 回原形状。

### 1.7 Pre-Apply-Mix

加权求和归约 mhc 维度：`out = sum(x * mix, dim=-2)`。

**底层 JIT kernel**：
- `_mhc_pre_apply_mix_fwd(mhc, h)`
- `_mhc_pre_apply_mix_bwd(mhc, h)`（out_idx=[4]）
- 支持 fused grad acc

**Modeling 封装**：

```python
tile_kernels.modeling.mhc.ops.mhc_pre_apply_mix(
    x: Tensor,
    mix: Tensor,        # mix 最后一维必须为 1
    out: Tensor | None = None,
) -> Tensor
```

backward 检测 `x.untyped_storage().grad_from_mhc_post` 做 fused grad acc。

### 1.8 Post

MHC 后处理：residual 混合更新。

**底层 JIT kernel**：
- `_mhc_post_fwd(mhc, hidden, n_thr=128, h_blk=1024)`
- `_mhc_post_bwd(mhc, hidden, n_thr=128, h_blk=256)`

**Python wrapper**：

```python
def mhc_post_fwd(x, residual, post_layer_mix, comb_res_mix, out=None) -> Tensor:
    """
    x:               (S, T, hidden) bf16
    residual:        (S, T, mhc, hidden) bf16
    post_layer_mix:  (S, T, mhc, 1) fp32
    comb_res_mix:    (S, T, mhc, mhc) fp32
    """

def mhc_post_bwd(x, residual, post_layer_mix, comb_res_mix, d_o, fuse_grad_acc=True) -> tuple:
    """返回 (d_x, d_residual, d_post_layer_mix, d_comb_res_mix)"""
    # fuse_grad_acc=True 时，d_residual 存入 residual.untyped_storage().grad_from_mhc_post
```

**Modeling 封装**：

```python
tile_kernels.modeling.mhc.ops.mhc_post(
    x, residual, post_layer_mix, comb_res_mix, out=None
) -> Tensor
```

### 1.9 Fn-Normw Merge

融合 fn 权重和 norm 权重的乘法。

**Modeling 封装**（`_MHCFnNormwMerge` autograd.Function）：

- forward: `out = fn * normw`（逐元素乘）
- backward: 累加 fn_grad 和 normw_grad
- 支持 main_grad

### 1.10 Pre-Big-Fuse（推理融合）

推理模式下将 norm_fn + split_mixes + sinkhorn + apply_mix 融合为单个 kernel。

**底层 JIT kernel**：`_mhc_pre_big_fuse(...)`。

**Python 函数**：

```python
def mhc_pre_big_fuse(
    residual, fn, mhc_scale, mhc_base,
    rms_eps, mhc_pre_eps, mhc_sinkhorn_eps,
    mhc_post_mult_value, sinkhorn_repeat,
    n_splits=16,
) -> tuple[Tensor, Tensor, Tensor]:
    """返回 (post_mix, comb_mix, layer_input)"""
```

**约束**：
- residual 为 bf16，fn/scale/base 为 fp32
- TileLang 实现 n_splits 强制为 1

### 1.11 Multilayer Recompute

多层 MHC residual 原地重计算，使用指针表批处理。

**底层 JIT kernel**：`_mhc_multilayer_recompute_kernel(mhc_mult, hidden, num_layers, num_post, n_thr=64, h_blk=2048)`。

Pass 配置：`TL_DISABLE_WARP_SPECIALIZED: True`, `TL_PTXAS_REGISTER_USAGE_LEVEL: 10`, `TL_DISABLE_VECTORIZE_256: True`。

**辅助函数**：

```python
def _make_ptr_tables_batched(tensor_lists, device) -> list[Tensor]:
    """构建批处理指针表（pinned memory → GPU）"""
```

**Python wrapper**：

```python
def mhc_multilayer_recompute(
    initial_residual: Tensor,
    pre_mix_list: list[Tensor],
    layer_output_list: list[Tensor],
    post_mix_list: list[Tensor],
    comb_mix_list: list[Tensor],
    layer_input_list: list[Tensor],
    residual_list: list[Tensor],
) -> None:
    """原地重计算多层 MHC residual"""
```

**约束**：`num_post == num_layers - 1` 或 `num_post == num_layers`。

### 1.12 高层 Functional API

```python
# 子层预处理（attention/FFN 前）
tile_kernels.modeling.mhc.mhc_pre(
    residual, fn, scale, base,
    norm_weight=None, norm_eps=1e-6,
    mhc_mult=4, post_mult_value=1.0, pre_eps=1e-6,
    sinkhorn_eps=1e-6, sinkhorn_repeat=10, n_splits=16,
) -> tuple[Tensor, tuple[Tensor, Tensor]]
# 返回 (layer_input, (post_mix, comb_mix))
# 训练：分步执行；推理：使用 mhc_pre_big_fuse 融合

# LM Head 处理
tile_kernels.modeling.mhc.mhc_head(
    residual, fn, scale, base,
    norm_weight=None, norm_eps=1e-6,
    mhc_mult=4, pre_eps=1e-6, n_splits=16,
) -> Tensor
# 返回 layer_input (..., hidden_size)
```

---

## 二、Engram 记忆机制

Engram 是 DeepSeek 的记忆增强机制，通过门控融合 KV cache 和 hidden states。

### 2.1 Fused Weight

```python
tile_kernels.engram.fused_weight(
    weight_hidden: Tensor,    # (hc_mult, hidden_size) bf16
    weight_embed: Tensor,     # (hc_mult, hidden_size) bf16
) -> Tensor:                   # (hc_mult, hidden_size) fp32
```

逐元素 bf16×bf16→fp32 融合权重乘法，用于 RMSNorm 权重的预计算。

- JIT kernel：`get_engram_fused_weight_kernel(hidden_size, hc_mult)`
- Pass 配置：`TL_DISABLE_WARP_SPECIALIZED: True`
- threads=32, vec_size=8, blk_d=256

### 2.2 Engram Gate

前向计算公式：

```
x_norm = RMSNorm(hidden_states, weight_hidden)   # (T, hc_mult, H)
k_norm = RMSNorm(k, weight_embed)                # (T, hc_mult, H)
dot = sum(x_norm * k_norm, dim=-1)               # (T, hc_mult)
scalar = 1 / sqrt(hidden_size)
gate_score = sigmoid(signed_sqrt(dot * scalar))  # signed_sqrt(x) = sign(x)*sqrt(|x|)
gate = gate_score.unsqueeze(-1) * v              # (T, hc_mult, H)
output = hidden_states + gate                    # (T, hc_mult, H)
```

**Python API**：

```python
# 底层 kernel
tile_kernels.engram.engram_gate_fwd(
    hidden_states, k, v,       # (T, hc_mult, H) bf16 / (T, H) bf16
    weight_fused,              # (hc_mult, H) fp32（fused_weight 输出）
    eps, clamp_value,
    save_for_backward=True,
) -> tuple[output, dot, gate_score, rstd_x, rstd_k]

tile_kernels.engram.engram_gate_bwd(
    grad_out, hidden_states, k, v, weight_fused,
    dot, gate_score, rstd_x, rstd_k, clamp_value,
) -> tuple[grad_x, grad_k, grad_v, grad_w_partial]
# grad_w_partial: (num_persistent_blocks, hc_mult, H) fp32，需 reduce
```

**Modeling 封装**：

```python
tile_kernels.modeling.engram.engram_gate(
    hidden_states: Tensor,     # (*, hc_mult, hidden_size) bf16
    k: Tensor,                 # (*, hc_mult, hidden_size) bf16
    v: Tensor,                 # (*, hidden_size) bf16
    weight_hidden: Tensor,     # (hc_mult, hidden_size) bf16
    weight_embed: Tensor,      # (hc_mult, hidden_size) bf16
    clamp_value: float,
    eps: float,
) -> Tensor
```

`EngramGateFn` autograd.Function 特性：
- 内部先调用 `fused_weight` 合并权重
- 支持 main_grad：权重若有 `.main_grad` 属性，梯度原地累积到 main_grad
- backward 使用 `grad_w_reduce` 归约权重梯度

### 2.3 Grad W Reduce

```python
tile_kernels.engram.grad_w_reduce(
    grad_w_partial: Tensor,          # (num_persistent_blocks, hc_mult, H) fp32
    weight_hidden: Tensor,           # (hc_mult, H) bf16
    weight_embed: Tensor,            # (hc_mult, H) bf16
    grad_weight_hidden: Tensor,      # (hc_mult, H) fp32，原地修改
    grad_weight_embed: Tensor,       # (hc_mult, H) fp32，原地修改
) -> None
```

原地归约 partial 梯度并融合权重乘法，累积到 grad_weight 张量。

- JIT kernel：`get_engram_grad_w_reduce_kernel(...)`

### 2.4 Engram Hash

N-gram XOR 哈希，用于 Engram 的嵌入表索引。

```python
tile_kernels.engram.engram_hash(
    ngram_token_ids: Tensor,    # (num_tokens, max_ngram_size) int32
    multipliers: Tensor,        # (num_ngram_layers, max_ngram_size) int64
    vocab_sizes: Tensor,        # (num_ngram_layers, max_ngram_size-1, num_embed_table_per_ngram) int32
    offsets: Tensor,            # (num_ngram_layers, (max_ngram_size-1)*num_embed_table_per_ngram) int32
) -> Tensor:                    # (num_ngram_layers, num_tokens, (max_ngram_size-1)*num_embed_table_per_ngram) int32
```

计算流程：XOR hash → mod vocab_size → + offsets。

- JIT kernel：`get_engram_hash_kernel(max_ngram_size, num_ngram_layers, num_embed_table_per_ngram)`

---

## 三、转置

### transpose

2D 张量转置。

**JIT kernel**：`get_batched_transpose_kernel(shape_x_mod_128, shape_y_mod_128, dtype)`。

- Pass 配置：`TL_DISABLE_WARP_SPECIALIZED: True`
- block_x/block_y：128 或 64（取决于 mod128 值）
- block_k=4, num_threads=256
- shared memory padding：(block_y, block_x+block_k) 减少 bank conflict
- swizzle 布局写入 shared memory

```python
tile_kernels.transpose(
    x: torch.Tensor,     # (M, N)，M%64==0, N%64==0, stride(-2)%4==0, stride(-1)==1
) -> torch.Tensor:       # (N, M)
```

### batched_transpose

3D 批量转置。

```python
tile_kernels.batched_transpose(
    x: torch.Tensor,     # (B, M, N)
) -> torch.Tensor:       # (B, N, M)
```

**约束**：M%64==0, N%64==0, stride(-2)%4==0, stride(-1)==1。

**环境变量**：`TK_PRINT_KERNEL_SOURCE=1` 时打印 kernel 生成的 CUDA 源码。

---

## 四、配置与工具函数

### 配置模块（config.py）

```python
tile_kernels.get_num_sms() -> int              # 获取当前使用的 SM 数
tile_kernels.set_num_sms(num_sms: int) -> None  # 设置使用的 SM 数
tile_kernels.get_device_num_sms() -> int        # 查询物理 SM 数（LRU 缓存）
tile_kernels.get_max_smem_per_sm() -> int       # 查询每 SM 最大共享内存（LRU 缓存）
```

### 工具函数（utils.py）

```python
from tile_kernels.utils import ceil_div, align, is_power_of_two

ceil_div(x: int, y: int) -> int      # (x + y - 1) // y
align(x: int, y: int) -> int         # ceil_div(x, y) * y
is_power_of_two(x: int) -> bool      # x > 0 and (x & (x - 1)) == 0
```
