---
type: api-reference
scope: deep-gemm
name: DeepGEMM Public API Reference
version: "2.6.1"
source: deep_gemm/__init__.py, csrc/apis/gemm.hpp, csrc/apis/attention.hpp, csrc/apis/einsum.hpp, csrc/apis/hyperconnection.hpp
description: DeepGEMM 公共 Python API 完整参考
---

# DeepGEMM 公共 API 参考

DeepGEMM 的 Python API 通过 `deep_gemm` 包导出，底层通过 pybind11 绑定 C++ 实现。核函数按功能分为 GEMM、Attention、Einsum、Hyperconnection、Layout、MegaMoE、Runtime 配置七大类。

---

## 一、GEMM 核函数

所有 GEMM 核函数支持四种转置组合：`nt`、`nn`、`tn`、`tt`，其中 n 表示不转置，t 表示转置。例如 `fp8_gemm_nt` 表示 A 不转置（K-major）、B 转置。

### 1.1 FP8/FP4 GEMM

```python
fp8_fp4_gemm_nt(a, b, d, c=None, recipe=None, recipe_a=None, recipe_b=None,
                compiled_dims="nk", disable_ue8m0_cast=False)
```

- **形状**：`[M, K] @ [N, K].T -> [M, N]`
- **参数**：
  - `a`: `(tensor_fp, tensor_sf)` 元组，FP8/FP4 激活张量 + 缩放因子
  - `b`: `(tensor_fp, tensor_sf)` 元组，FP8/FP4 权重张量 + 缩放因子
  - `d`: 输出张量（BF16 或 FP32）
  - `c`: 可选偏置/累加张量，与 d 同类型
  - `recipe`: `(gran_m, gran_n, gran_k)` 缩放因子粒度元组
  - `recipe_a`/`recipe_b`: 单独指定 A/B 的 recipe，与 `recipe` 互斥
  - `compiled_dims`: JIT 编译维度，"nk" 或 "mn"
  - `disable_ue8m0_cast`: 禁用 UE8M0 打包转换
- **架构分发**：SM90 → `sm90_fp8_gemm_1d1d`/`sm90_fp8_gemm_1d2d`；SM100 → `sm100_fp8_fp4_gemm_1d1d`

别名（FP8 专用）：
- `fp8_gemm_nt`, `fp8_gemm_nn`, `fp8_gemm_tn`, `fp8_gemm_tt`

### 1.2 M-Grouped GEMM（连续布局）

```python
m_grouped_fp8_fp4_gemm_nt_contiguous(a, b, d, grouped_layout, recipe=None,
    recipe_a=None, recipe_b=None, compiled_dims="nk",
    disable_ue8m0_cast=False, use_psum_layout=False,
    ensure_zero_padding=True, expected_m_for_psum_layout=None)
```

- **形状**：`[M, K] @ [G, N, K].mT -> [M, N]`
- **参数**：
  - `grouped_layout`: Int32 张量，长度为 M（非 psum 模式）或 G（psum 模式），标识每行/组的 expert ID
  - `use_psum_layout`: 是否使用 partial sum 布局（分布式场景）
  - `ensure_zero_padding`: 是否确保零填充（SM100）
  - `expected_m_for_psum_layout`: psum 布局下的预期 M 值

别名：`m_grouped_fp8_gemm_nt_contiguous`, `m_grouped_fp8_gemm_nn_contiguous`

BF16 版本：
```python
m_grouped_bf16_gemm_nt_contiguous(a, b, d, grouped_layout, compiled_dims="nk",
    use_psum_layout=False, ensure_zero_padding=True, expected_m_for_psum_layout=None)
```

### 1.3 M-Grouped GEMM（掩码布局）

```python
m_grouped_fp8_fp4_gemm_nt_masked(a, b, d, masked_m, expected_m,
    recipe=None, recipe_a=None, recipe_b=None,
    compiled_dims="nk", disable_ue8m0_cast=False)
```

- **形状**：`[G, M, K] @ [G, N, K].mT -> [G, M, N]`
- **参数**：
  - `masked_m`: Int32 张量，长度为 G，每个 expert 的实际 token 数
  - `expected_m`: 预期的 M 维度大小（含 padding）
- **架构分发**：SM90 → `sm90_m_grouped_fp8_gemm_masked_1d2d`；SM100 → `sm100_m_grouped_fp8_fp4_gemm_masked_1d1d`

BF16 版本：`m_grouped_bf16_gemm_nt_masked(a, b, d, masked_m, expected_m, compiled_dims="nk")`

历史别名：`fp8_m_grouped_gemm_nt_masked`, `bf16_m_grouped_gemm_nt_masked`

### 1.4 K-Grouped GEMM（连续布局）

```python
# TN 布局（支持 SM90 BF16, SM100 FP8/BF16）
k_grouped_fp8_gemm_tn_contiguous(a, b, d, ks_cpu, grouped_layout, c=None,
    recipe=(1, 1, 128), compiled_dims="mn", use_psum_layout=False)

# NT 布局（仅 SM90 FP8）
k_grouped_fp8_gemm_nt_contiguous(a, b, d, ks_cpu, grouped_layout, c=None,
    recipe=(1, 1, 128), compiled_dims="mn", use_psum_layout=False)
```

- **形状**：连续拼接的 K 分组 GEMM，输出 3D `[G, M, N]`
- **参数**：
  - `ks_cpu`: CPU 上的整数列表，每个 group 的 K 值
  - `grouped_layout`: Int32 张量，长度为 G
  - `c`: 必须提供的累加张量

BF16 版本：`k_grouped_bf16_gemm_tn_contiguous(a, b, d, ks_cpu, grouped_layout, c=None, compiled_dims="mn", use_psum_layout=False)`

### 1.5 BF16 GEMM

```python
bf16_gemm_nt(a, b, d, c=None, compiled_dims="nk")
```

- **形状**：`[M, K] @ [N, K].T -> [M, N]`
- **数据类型**：A/B 为 BF16，D 为 BF16 或 FP32
- **架构分发**：SM90 → `sm90_bf16_gemm`；SM100 → `sm100_bf16_gemm`

四个变体：`bf16_gemm_nt/nn/tn/tt`

### 1.6 cuBLASLt GEMM（回退路径）

```python
cublaslt_gemm_nt(a, b, d, c=None)
```

- 无条件可用，使用 cuBLASLt 库执行 GEMM
- 四个变体：`cublaslt_gemm_nt/nn/tn/tt`

---

## 二、Attention 核函数

### 2.1 FP8 GEMM with Head Split（QKV 投影）

```python
fp8_gemm_nt_skip_head_mid(a, b, d, head_splits, recipe=None,
    compiled_dims="nk", disable_ue8m0_cast=False)
```

- **形状**：`[M, K] @ [N, K].T -> [M, N']`（N' = N + N/(left+right)*mid）
- **参数**：
  - `head_splits`: `(left, mid, right)` 元组，定义 head 维度分割
  - 用于 Q/K/V 投影融合，跳过 mid 部分
- **架构分发**：SM90 → `sm90_fp8_gemm_1d2d`（自定义 epilogue）；SM100 → `sm100_fp8_fp4_gemm_1d1d`

### 2.2 MQA Logits 计算

```python
fp8_fp4_mqa_logits(q, kv, weights, cu_seq_len_k_start, cu_seq_len_k_end,
    clean_logits=True, max_seqlen_k=0, logits_dtype=torch.float32)
```

- **参数**：
  - `q`: `(q_fp, q_sf)` 元组，q_sf 可选（None 表示非 MX 格式）
  - `kv`: `(kv_fp, kv_sf)` 元组
  - `cu_seq_len_k_start`/`cu_seq_len_k_end`: 累积序列长度
  - `clean_logits`: 是否应用 causal mask 清理
  - `max_seqlen_k`: 最大 KV 序列长度（0 表示自动推断）
  - `logits_dtype`: logits 输出数据类型
- **约束**：
  - SM100：num_heads ∈ {8, 16, 32, 64}，head_dim ∈ {32, 64, 128}（FP4 时 64/128）
  - SM90：num_heads ∈ {32, 64}，head_dim == 32
- **返回**：logits 张量

旧版 API（FP8 专用，Float logits）：
```python
fp8_mqa_logits(q, kv, weights, cu_seq_len_k_start, cu_seq_len_k_end,
    clean_logits=True, max_seqlen_k=0)
```

### 2.3 Paged MQA Logits

```python
get_paged_mqa_logits_metadata(context_lens, block_kv, num_sms, indices=None)
```
- 计算 paged attention 的调度元数据，返回形状 `{num_sms + 1, 2}` 的 Int 张量

```python
fp8_fp4_paged_mqa_logits(q, fused_kv_cache, weights, context_lens, block_table,
    schedule_meta, max_context_len, clean_logits=False,
    logits_dtype=torch.float32, indices=None)
```
- **参数**：
  - `fused_kv_cache`: 融合 KV cache，形状 `(num_kv_blocks, block_kv, num_heads_kv, head_dim_with_sf)`
  - `block_table`: 页表索引
  - `schedule_meta`: `get_paged_mqa_logits_metadata` 返回值
- **约束**：SM100 支持 block_kv ∈ {32, 64, 128}；SM90 仅支持 block_kv=64

旧版：`fp8_paged_mqa_logits(...)`

---

## 三、Einsum 核函数

### 3.1 BF16 Einsum

```python
einsum(expr, a, b, d, c=None, use_cublaslt=False)
```

支持的表达式：
- `"bmk,bnk->mn"`：批量归约 GEMM，形状 `(s,m,k) @ (s,n,k) -> (m,n)`
- `"bhr,hdr->bhd"`：注意力投影，形状 `(b,h,r) @ (h,d,r).T -> (b,h,d)`
- `"bhd,hdr->bhr"`：反向投影，形状 `(b,h,d) @ (h,d,r).T -> (b,h,r)`

### 3.2 FP8 Einsum

```python
fp8_einsum(expr, a, b, d, c=None, recipe=(1, 128, 128))
```

支持的表达式：
- `"bhr,hdr->bhd"`：FP8 注意力投影（SM90/SM100）
- `"bhd,hdr->bhr"`：FP8 反向投影（仅 SM100）
- `"bhd,bhr->hdr"`：FP8 权重梯度（仅 SM100）

---

## 四、Hyperconnection 核函数

```python
tf32_hc_prenorm_gemm(a, b, d, sqr_sum, num_splits=None)
```

- **功能**：Hyperconnection 前置归一化 GEMM，使用 TF32 精度
- **数据类型**：A 为 BF16，B/D/sqr_sum 为 FP32
- **参数**：
  - `sqr_sum`: 平方和张量，用于 prenorm 计算
  - `num_splits`: 可选分割数，启用时 d 为 3D `(num_splits, m, n)`
- **架构**：SM90 → `sm90_tf32_hc_prenorm_gemm`；SM100 → `sm100_tf32_hc_prenorm_gemm`

---

## 五、Layout 工具函数

### 5.1 缩放因子布局转换

```python
transform_sf_into_required_layout(sf, mn, k, recipe, num_groups=None,
    is_sfa=None, disable_ue8m0_cast=False, psum_layout=None) -> Tensor
```

- 将缩放因子转换为核函数所需布局（TMA 对齐、MN-major、UE8M0 打包等）
- 根据架构自动选择转换策略

### 5.2 TMA 对齐工具

```python
get_tma_aligned_size(...) -> int
get_mn_major_tma_aligned_tensor(sf) -> Tensor
get_mn_major_tma_aligned_packed_ue8m0_tensor(sf, psum_layout=None) -> Tensor
get_k_grouped_mn_major_tma_aligned_packed_ue8m0_tensor(sf, ks_cpu, grouped_layout, ...) -> Tensor
```

### 5.3 MK 对齐配置

```python
set_mk_alignment_for_contiguous_layout(new_value: int) -> None
get_mk_alignment_for_contiguous_layout() -> int
get_theoretical_mk_alignment_for_contiguous_layout(expected_m=None) -> int
```

- 别名：`get_m_alignment_for_contiguous_layout`, `get_k_alignment_for_contiguous_layout`

---

## 六、MegaMoE API

参见 /deepseek/deep-gemm/references/mega-moe。

---

## 七、Runtime 配置 API

参见 /deepseek/deep-gemm/references/runtime-config。
