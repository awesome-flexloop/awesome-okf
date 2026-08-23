# FlashMLA 源码事实清单（R-Phase）

> 源码路径：`d:\spaces\SpecWeave\external\libs\ai\deepseek-ai\FlashMLA`
> 收集日期：2026-08-22
> 版本：`__version__ = "1.0.0"`（来自 [flash_mla/__init__.py](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/flash_mla/__init__.py#L1)）

---

## F-001：Python 包版本与公开 API 导出

- 文件：[flash_mla/__init__.py](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/flash_mla/__init__.py#L1-L19)
- 版本号：`__version__ = "1.0.0"`
- 从 `flash_mla.flash_mla_interface` 导入并通过 `__all__` 导出以下 6 个公开符号：
  1. `get_mla_metadata`
  2. `flash_mla_with_kvcache`
  3. `flash_attn_varlen_func`
  4. `flash_attn_varlen_qkvpacked_func`
  5. `flash_attn_varlen_kvpacked_func`
  6. `flash_mla_sparse_fwd`

---

## F-002：`FlashMLASchedMeta` 数据类

- 文件：[flash_mla/flash_mla_interface.py](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/flash_mla/flash_mla_interface.py#L8-L35)
- `FlashMLASchedMeta` 是一个 `@dataclasses.dataclass` 类，存储 FlashMLA 的 tile 调度元数据。
- 内嵌 `Config` 数据类，字段包括：
  - `b: int`（batch size）
  - `s_q: int`（query 序列长度）
  - `h_q: int`（query 头数）
  - `page_block_size: int`（页块大小）
  - `h_k: int`（KV 头数）
  - `causal: bool`
  - `is_fp8_kvcache: bool`
  - `topk: Optional[int]`
  - `extra_page_block_size: Optional[int]`
  - `extra_topk: Optional[int]`
- `FlashMLASchedMeta` 自身字段：
  - `have_initialized: bool = False`
  - `config: Optional[Config] = None`
  - `tile_scheduler_metadata: Optional[torch.Tensor] = None`，形状注释为 `(num_sm_parts, TileSchedulerMetaDataSize)`，dtype `torch.int32`
  - `num_splits: Optional[torch.Tensor] = None`，形状注释为 `(1)`，dtype `torch.int32`

---

## F-003：`get_mla_metadata` 函数签名

- 文件：[flash_mla/flash_mla_interface.py](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/flash_mla/flash_mla_interface.py#L37-L50)
- 签名：`def get_mla_metadata(*args, **kwargs) -> Tuple[FlashMLASchedMeta, None]`
- 该函数不使用任何参数（保留 `*args, **kwargs` 仅为兼容旧接口）。
- 返回值：返回一个空的 `FlashMLASchedMeta()` 实例和 `None` 组成的元组 `(FlashMLASchedMeta(), None)`。
- docstring 说明：实际调度元数据在第一次调用 `flash_mla_with_kvcache` 时延迟生成。

---

## F-004：`flash_mla_with_kvcache` 函数签名与参数

- 文件：[flash_mla/flash_mla_interface.py](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/flash_mla/flash_mla_interface.py#L53-L173)
- 签名：
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
- 参数说明（来自 docstring）：
  - `q`: 形状 `(batch_size, seq_len_q, num_heads_q, head_dim)`
  - `k_cache`: 形状 `(num_blocks, page_block_size, num_heads_k, head_dim)`（非 FP8 模式）；FP8+sparse 模式下每个 token 656 字节
  - `block_table`: 形状 `(batch_size, max_num_blocks_per_seq)`，dtype `torch.int32`，sparse attention 时可为 None
  - `cache_seqlens`: 形状 `(batch_size)`，dtype `torch.int32`，sparse attention 时可为 None
  - `head_dim_v`: V 的头维度，必须为 512
  - `tile_scheduler_metadata`: `FlashMLASchedMeta` 类型
  - `num_splits`: 必须为 `None`（兼容旧接口）
  - `softmax_scale`: float，默认 `1 / sqrt(head_dim_k)`
  - `causal`: bool，仅对 dense attention 有效
  - `is_fp8_kvcache`: bool
  - `indices`: 形状 `(batch_size, seq_len_q, topk)`，sparse attention 的 KV 索引
  - `attn_sink`: 形状 `(num_heads_q,)`，dtype `torch.float32`，可选
  - `extra_k_cache` / `extra_indices_in_kvcache`: 额外 KV cache 和对应索引
  - `topk_length` / `extra_topk_length`: 形状 `(batch_size,)`，dtype `torch.int32`，可选
- 返回值：
  - `out`: 形状 `(batch_size, seq_len_q, num_heads_q, head_dim_v)`
  - `softmax_lse`: 形状 `(batch_size, num_heads_q, seq_len_q)`，dtype `torch.float32`

---

## F-005：`flash_mla_with_kvcache` 内部路由逻辑

- 文件：[flash_mla/flash_mla_interface.py](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/flash_mla/flash_mla_interface.py#L104-L173)
- 首次调用时（`sched_meta.have_initialized == False`），执行 sanity check 并初始化 `sched_meta.config`，记录 `b, s_q, h_q, page_block_size, h_k, causal, is_fp8_kvcache, topk, extra_k_page_block_size, extra_topk`。
- 后续调用时检查输入参数与 `sched_meta.config` 一致性。
- 若 `topk is not None`（即 sparse attention），调用 `flash_mla_cuda.sparse_decode_fwd(...)`；断言 `causal == False`、`is_fp8_kvcache == True`。
- 若 `topk is None`（即 dense attention），调用 `flash_mla_cuda.dense_decode_fwd(...)`；断言 `indices_in_kvcache, attn_sink, extra_k_cache, extra_indices_in_kvcache, topk_length, extra_topk_length` 均为 None，且 `block_table` 和 `cache_seqlens` 不为 None。
- 调用后更新 `sched_meta.tile_scheduler_metadata` 和 `sched_meta.num_splits`。

---

## F-006：DeepSeek V3/V3.1/V3.2 FP8+sparse KV cache 布局

- 文件：[flash_mla/flash_mla_interface.py](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/flash_mla/flash_mla_interface.py#L92-L99)
- DeepSeek V3/V3.1/V3.2 配置：`head_dim = 576`，`head_dim_v = 512`。
- FP8+sparse 模式每个 token 的 KV cache 为 656 字节，结构：
  - `k_cache` 形状 `(num_blocks, page_block_size, num_heads_k, head_dim)`，`num_heads_k` 必须为 1。
  - 前 512 字节：量化后的 "NoPE" 部分，含 512 个 `float8_e4m3` 值。
  - 接下来 16 字节：缩放因子，含 4 个 `float32` 值，每个 float32 对应 128 个 `float8_e4m3` 值的缩放。
  - 最后 128 字节："RoPE" 部分，含 64 个 `bfloat16` 值，不做量化。

---

## F-007：`flash_mla_sparse_fwd` 函数签名

- 文件：[flash_mla/flash_mla_interface.py](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/flash_mla/flash_mla_interface.py#L176-L211)
- 签名：
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
- 用途：Sparse attention prefill kernel。
- 参数形状：
  - `q`: `[s_q, h_q, d_qk]`，bfloat16
  - `kv`: `[s_kv, h_kv, d_qk]`，bfloat16
  - `indices`: `[s_q, h_kv, topk]`，int32，无效索引设为 -1 或 >= s_kv
  - `sm_scale`: float
  - `d_v`: value 维度，只能为 512
  - `attn_sink`: 可选 `[h_q]`，float32
  - `topk_length`: 可选 `[s_q]`，int32
- 返回值：`(output, max_logits, lse)`
  - `output`: `[s_q, h_q, d_v]`，bfloat16
  - `max_logits`: `[s_q, h_q]`，float
  - `lse`: `[s_q, h_q]`，float（attention scores 的 log-sum-exp）
- 内部调用 `flash_mla_cuda.sparse_prefill_fwd(q, kv, indices, sm_scale, d_v, attn_sink, topk_length)`。

---

## F-008：`_flash_attn_varlen_forward` 函数签名

- 文件：[flash_mla/flash_mla_interface.py](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/flash_mla/flash_mla_interface.py#L214-L258)
- 签名：
  ```python
  def _flash_attn_varlen_forward(
      q: torch.Tensor, k: torch.Tensor, v: torch.Tensor,
      cu_seqlens_qo: torch.Tensor, cu_seqlens_kv: torch.Tensor,
      max_seqlen_qo: int, max_seqlen_kv: int,
      out: Optional[torch.Tensor] = None, lse: Optional[torch.Tensor] = None,
      causal: bool = False, softmax_scale: Optional[float] = None,
      is_varlen: bool = True,
  ) -> Tuple[torch.Tensor, torch.Tensor]
  ```
- `q` 形状：`(qo_total_len, num_qo_heads, head_dim_qk)`；`v` 形状：`(kv_total_len, num_kv_heads, head_dim_vo)`。
- 分配 32MB workspace buffer（`torch.empty(32 * 1024 * 1024, dtype=torch.uint8)`）。
- 调用 `flash_mla_cuda.dense_prefill_fwd(...)`。
- 默认 `softmax_scale = head_dim_qk ** (-0.5)`。

---

## F-009：`_flash_attn_varlen_backward` 函数签名

- 文件：[flash_mla/flash_mla_interface.py](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/flash_mla/flash_mla_interface.py#L261-L325)
- 签名：
  ```python
  def _flash_attn_varlen_backward(
      do, q, k, v, out, lse,
      cu_seqlens_qo, cu_seqlens_kv,
      max_seqlen_qo, max_seqlen_kv,
      dq=None, dk=None, dv=None,
      causal=False, softmax_scale=None, is_varlen=True,
  ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]
  ```
- 当 `num_qo_heads != num_kv_heads` 时抛出 `ValueError`："SM100 bwd doesn't support GQA now"。
- 动态计算 workspace 大小，包含 `dQ_acc`、`sum_OdO and scaled_lse`、`dKV_acc`（GQA 场景）。
- 调用 `flash_mla_cuda.dense_prefill_bwd(...)`。

---

## F-010：`FlashAttnVarlenFunc` 自定义 autograd Function

- 文件：[flash_mla/flash_mla_interface.py](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/flash_mla/flash_mla_interface.py#L328-L369)
- 继承 `torch.autograd.Function`。
- `forward` 方法调用 `_flash_attn_varlen_forward`，保存 `q, k, v, out, lse, cu_seqlens_qo, cu_seqlens_kv` 及序列长度、causal、scale 等参数到 `ctx`。
- `backward` 方法丢弃 `dlse`（注释："LSE doesn't support backward currently"），调用 `_flash_attn_varlen_backward`。

---

## F-011：`flash_attn_varlen_func` / `flash_attn_varlen_qkvpacked_func` / `flash_attn_varlen_kvpacked_func`

- 文件：[flash_mla/flash_mla_interface.py](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/flash_mla/flash_mla_interface.py#L372-L435)
- `flash_attn_varlen_func(q, k, v, cu_seqlens_qo, cu_seqlens_kv, max_seqlen_qo, max_seqlen_kv, dropout_p=0.0, softmax_scale=None, causal=False, deterministic=False, is_varlen=True)`：
  - 断言 `dropout_p == 0.0`、`not deterministic`。
  - 调用 `FlashAttnVarlenFunc.apply(...)`。
- `flash_attn_varlen_qkvpacked_func(qkv, cu_seqlens, max_seqlen, head_dim_qk, ...)`：
  - 将 `qkv` 按 `head_dim_qk` 切分为 q/k/v 三部分。
- `flash_attn_varlen_kvpacked_func(q, kv, cu_seqlens_qo, cu_seqlens_kv, max_seqlen_qo, max_seqlen_kv, head_dim_qk, ...)`：
  - 将 `kv` 按 `head_dim_qk` 切分为 k/v 两部分。

---

## F-012：pybind11 模块导出的 C++ 函数

- 文件：[csrc/api/api.cpp](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/csrc/api/api.cpp#L1-L15)
- 模块名：`TORCH_EXTENSION_NAME`（即 `flash_mla.cuda`）。
- 导出 5 个函数：
  1. `sparse_decode_fwd` → `sparse_attn_decode_interface`
  2. `dense_decode_fwd` → `dense_attn_decode_interface`
  3. `sparse_prefill_fwd` → `sparse_attn_prefill_interface`
  4. `dense_prefill_fwd` → `FMHACutlassSM100FwdRun`
  5. `dense_prefill_bwd` → `FMHACutlassSM100BwdRun`

---

## F-013：类型别名与基础结构体（defines.h）

- 文件：[csrc/defines.h](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/csrc/defines.h#L1-L26)
- 类型别名：
  - `bf16 = cutlass::bfloat16_t`
  - `fp8 = cutlass::float_e4m3_t`
  - `transac_bar_t = cutlass::arch::ClusterTransactionBarrier`
- 导入：`fence_view_async`、`fence_barrier_init`、`NamedBarrier`。
- 自定义结构体：
  - `int32x8_t`：包含 `int a0~a7`
  - `float8`：包含 `float2 a01, a23, a45, a67`
  - `bf16x8`：包含 `__nv_bfloat162 a01, a23, a45, a67`

---

## F-014：ModelType 枚举与 DecodingSchedMeta 结构体

- 文件：[csrc/params.h](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/csrc/params.h#L5-L17)
- `enum class ModelType { V32, MODEL1 }`。
- `DecodingSchedMeta` 结构体（对齐 `4*8` 字节）：
  - `int begin_req_idx, end_req_idx`（均为 inclusive）
  - `int begin_block_idx, end_block_idx`（inclusive, exclusive）
  - `int begin_split_idx`
  - `int is_first_req_splitted, is_last_req_splitted`
  - `int _pad[1]`
- `static constexpr int DecodingSchedMetaSize = sizeof(DecodingSchedMeta)`。

---

## F-015：DenseAttnDecodeParams 结构体

- 文件：[csrc/params.h](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/csrc/params.h#L19-L61)
- 成员变量：
  - 维度参数：`b, s_q, q_seq_per_hk, d, d_v, h_q, h_k, num_blocks, q_head_per_hk`
  - `bool is_causal`
  - `float scale_softmax, scale_softmax_log2`
  - 指针：`q_ptr, k_ptr, o_ptr, softmax_lse_ptr`
  - 步长：`q_batch_stride, k_batch_stride, o_batch_stride, q_row_stride, k_row_stride, o_row_stride, q_head_stride, k_head_stride, o_head_stride`（类型 `index_t = int64_t`）
  - Paged KV cache：`block_table`（int32），`block_table_batch_stride`，`page_block_size`，`seqlens_k_ptr`
  - SplitKV：`tile_scheduler_metadata_ptr`（`DecodingSchedMeta*`），`num_sm_parts`，`num_splits_ptr`，`total_num_splits`，`softmax_lseaccum_ptr`，`oaccum_ptr`
  - `cudaStream_t stream`

---

## F-016：SparseAttnDecodeParams 结构体

- 文件：[csrc/params.h](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/csrc/params.h#L63-L103)
- 成员变量：
  - 维度：`b, s_q, h_q, h_kv, d_qk, d_v`
  - `float sm_scale, sm_scale_div_log2`
  - `int num_blocks, page_block_size, topk`
  - `ModelType model_type`
  - 输入指针：`q`（bf16，`[b, s_q, h_q, d_qk]`）、`kv`（bf16，`[num_blocks, page_block_size, d_qk]`）、`indices`（int32，`[b, s_q, topk]`）、`topk_length`（int32，`[b]`，可为 nullptr）、`attn_sink`（float32，`[h_q]`，可为 nullptr）
  - 输出：`lse`（float32，`[b, s_q, h_q]`）、`out`（bf16，`[b, s_q, h_q, d_v]`）
  - Extra KV：`extra_num_blocks, extra_page_block_size, extra_topk`，对应指针 `extra_kv, extra_indices, extra_topk_length`
  - 步长：`stride_q_b, stride_q_s_q, stride_q_h_q` 等
  - SplitKV：`lse_accum, o_accum, tile_scheduler_metadata_ptr, num_splits_ptr, num_sm_parts`
  - `cudaStream_t stream`

---

## F-017：CombineParams 与 GetDecodeSchedMetaParams

- 文件：[csrc/params.h](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/csrc/params.h#L105-L143)
- `CombineParams`：SplitKV 后 combine 阶段参数，包含 `b, s_q, h_q, d_v`，lse/out 指针及步长，lse_accum/o_accum 指针及步长，`tile_scheduler_metadata_ptr`，`num_splits_ptr`，`num_sm_parts`，`attn_sink`，`stream`。
- `GetDecodeSchedMetaParams`：调度元数据生成参数，包含 `b, s_q, block_size_n, fixed_overhead_num_blocks, topk, extra_topk`（-1 表示禁用 sparse/extra），`topk_length, extra_topk_length`，`seqlens_k_ptr`（仅 dense attention 需要），`tile_scheduler_metadata_ptr, num_splits_ptr, num_sm_parts, stream`。

---

## F-018：SparseAttnFwdParams 与 SparseAttnFwdMode

- 文件：[csrc/params.h](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/csrc/params.h#L145-L180)
- `SparseAttnFwdParams`：
  - 维度：`s_q, s_kv, h_q, h_kv, d_qk, d_v, topk`
  - `float sm_scale, sm_scale_div_log2`
  - 输入：`q`（`[s_q, h_q, d_qk]`，bf16）、`kv`（`[s_kv, h_kv, d_qk]`，bf16）、`indices`（`[s_q, h_kv, topk]`，int32）、`attn_sink`（`[h_q]`，float32）、`topk_length`（`[s_q]`，int32）
  - 步长、输出：`out`（`[s_q, h_q, d_v]`，bf16）、`max_logits`（`[s_q, h_q]`，float32）、`lse`（`[s_q, h_q]`，float32）
  - `int num_sm; cudaStream_t stream`
- `enum class SparseAttnFwdMode { Prefill, DecodeWithSplitKV }`
- 模板工具：`is_decode_v<FWD_MODE>` 判断是否 decode 模式；`SparseFwdArgT<FWD_MODE>` 根据模式选择参数类型。

---

## F-019：Arch 结构体与 GPU 架构检测

- 文件：[csrc/api/common.h](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/csrc/api/common.h#L20-L41)
- `Arch` 结构体在构造时通过 `at::cuda::getCurrentDeviceProperties()` 获取当前 GPU 的 `major, minor, num_sms, device_prop`。
- 方法：
  - `bool is_sm90a() const`：返回 `major == 9 && minor == 0`
  - `bool is_sm100f() const`：返回 `major == 10`
- 常量：`static constexpr float LOG_2_E = 1.44269504f`。

---

## F-020：Dispatch 宏定义

- 文件：[csrc/api/common.h](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/csrc/api/common.h#L51-L99)
- `DISPATCH_NUM_HEADS(NUM_HEADS, CONSTEXPR_NAME, ...)`：支持 `NUM_HEADS == 64` 和 `NUM_HEADS == 128`。
- `DISPATCH_HEAD_DIM(HEAD_DIM, CONSTEXPR_NAME, ...)`：支持 `HEAD_DIM == 576` 和 `HEAD_DIM == 512`。
- `DISPATCH_BOOLEAN_FLAG(FLAG, CONSTEXPR_NAME, ...)`：将 bool 转为 constexpr bool。
- `DISPATCH_MODEL_TYPE(MODEL_TYPE, CONSTEXPR_NAME, ...)`：支持 `ModelType::V32` 和 `ModelType::MODEL1`。

---

## F-021：ImplBase 模板类（特性分发基类）

- 文件：[csrc/api/common.h](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/csrc/api/common.h#L160-L230)
- `ImplBase<RunArgT_, FeatureT_>` 是所有 kernel 实现的基类。
- 纯虚函数：
  - `virtual void run_(const RunArgT &params, const std::vector<FeatureT> &required_features) = 0`
  - `constexpr virtual std::span<const FeatureT> get_supported_features() const = 0`
- `DECLARE_SUPPORTED_FEATURES(...)` 宏用于声明支持的特性。
- `run()` 方法先调用 `check_if_all_features_are_supported_and_abort()` 验证特性，再调用 `run_()`。

---

## F-022：dense_attn_decode_interface 函数（Dense Decode C++ 入口）

- 文件：[csrc/api/dense_decode.h](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/csrc/api/dense_decode.h#L13-L225)
- 返回类型：`std::tuple<at::Tensor, at::Tensor, std::optional<at::Tensor>, std::optional<at::Tensor>>`
- 架构检查：仅支持 SM90a（`arch.is_sm90a()`），否则报错。
- 数据类型：`q` 支持 `kBFloat16` 或 `kHalf`；`kcache` 必须与 q 同 dtype；`seqlens_k` 和 `block_table` 必须为 `kInt32`。
- 维度约束：
  - `head_size_k == 576 || head_size_k == 512`
  - `head_size_v == 512`
  - `page_block_size == 64`（注释："Currently page_block_size must be 64"）
  - `num_heads_q % num_heads_k == 0`
  - 当 `seqlen_q_ori == 1` 时强制 `is_causal = false`
- Q 张量 reshape：`q.view({b, s_q, h_k, num_q_heads_per_hk, head_size_k}).transpose(2,3).reshape({b, q_seq_per_hk, h_k, head_size_k})`。
- `num_sm_parts = std::max(arch.num_sms / num_heads_k / ceil_div(s_q * h_q / h_k, 64), 1)`。
- 首次调用时分配 `tile_scheduler_metadata`（形状 `{num_sm_parts, sizeof(DecodingSchedMeta)/4}`，int32）和 `num_splits`（形状 `{b+1}`，int32），调用 `smxx::decode::run_get_decoding_sched_meta_kernel()`。
- Dense kernel 调用：BF16 调用 `sm90::run_flash_splitkv_mla_kernel<cutlass::bfloat16_t>(params)`；FP16 调用 `sm90::run_flash_splitkv_mla_kernel<cutlass::half_t>(params)`（受 `FLASH_MLA_DISABLE_FP16` 宏控制）。
- Combine 阶段调用 `smxx::decode::run_flash_mla_combine_kernel<T>(combine_params)`。
- 固定开销块数：`fixed_overhead_num_blocks = 5`，`block_size_n = 64`。
- 输出张量最终 reshape 回 `{b, s_q, h_q, head_size_v}` 和 `{b, h_q, s_q}`。

---

## F-023：sparse_attn_decode_interface 函数（Sparse Decode C++ 入口）

- 文件：[csrc/api/sparse_decode.h](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/csrc/api/sparse_decode.h#L183-L495)
- 返回类型同 dense decode。
- 架构支持：SM90a 和 SM100f。
- 维度约束：
  - `h_kv == 1`（"Currently only MQA (i.e. h_kv == 1) is supported for sparse decoding"）
  - `d_qk == 576 || d_qk == 512`
  - `d_v == 512`
- KV cache dtype：`kFloat8_e4m3fn || kInt8 || kUInt8`；q dtype：`kBFloat16`；indices dtype：`kInt32`。
- bytes_per_token 计算：
  - V3.2 模式（d_qk=576, d_v=512）：`512 + 64*2 + (512/128)*4 = 656` 字节/token
  - MODEL1 模式（d_qk=512, d_v=512）：`448 + 64*2 + (448/64)*1 + 1 = 576` 字节/token
- `kv.stride(1) == bytes_per_token`（整块连续）。
- ModelType 判定：`d_qk == 576 → ModelType::V32`，`d_qk == 512 → ModelType::MODEL1`。
- 实现分发：
  - SM100f + h_q=64 → `Decode_Sm100_Head64_Impl`
  - SM100f + h_q=128 + d_qk=576 → `Decode_Sm100_Head64x2_Impl`（调用 head64 kernel 两次）
  - SM100f + h_q=128 + d_qk=512 → `Decode_Sm100_Head128_Impl`
  - SM90a → `Decode_Sm90_Impl`
- `DecodeImplMeta` 字段：`num_sm_parts, fixed_overhead_num_blocks, block_size_topk`。
- SM90 实现：`num_sm_parts = max(arch.num_sms / s_q / (h_q/64), 1)`，`fixed_overhead_num_blocks=5`，`block_size_topk=64`。
- SM100 Head64：`num_sm_parts = max(arch.num_sms / s_q, 1)`，`fixed_overhead_num_blocks=5`，`block_size_topk=64`。
- SM100 Head64x2：`num_sm_parts = max(arch.num_sms / s_q, 1)`，循环两次每次处理 64 头。
- SM100 Head128：`num_sm_parts = max(arch.num_sms / s_q / 2, 1)`，`fixed_overhead_num_blocks=3`，`block_size_topk=64`；调用 `sm100::fwd_for_small_topk::head128::run_fwd_for_small_topk_phase1_kernel<DecodeWithSplitKV, 512>`。
- Combine 阶段：`smxx::decode::run_flash_mla_combine_kernel<bf16>(combine_params)`。
- 返回 lse 时做了 transpose：`lse.transpose(1, 2)`（从 `[b, s_q, h_q]` 到 `[b, h_q, s_q]`）。

---

## F-024：sparse_attn_prefill_interface 函数（Sparse Prefill C++ 入口）

- 文件：[csrc/api/sparse_fwd.h](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/csrc/api/sparse_fwd.h#L101-L243)
- 返回类型：`std::vector<at::Tensor>`（out, max_logits, lse）。
- 架构支持：SM90a 和 SM100f。
- 输入维度：3D 张量（q: `[s_q, h_q, d_qk]`，kv: `[s_kv, h_kv, d_qk]`，indices: `[s_q, h_kv, topk]`）。
- 数据类型：q 和 kv 为 `kBFloat16`，indices 为 `kInt32`，attn_sink 为 `kFloat32`，topk_length 为 `kInt32`。
- 维度约束：`d_qk == 576 || d_qk == 512`，`d_v == 512`，h_q 支持 64/128。
- 实现分发：
  - SM90a → `Fwd_Sm90_Impl`（支持 HEAD_64/128, HEAD_DIM_512/576, ATTN_SINK, SINK_LSE, TOPK_LENGTH）
  - SM100f + h_q=64 → `Fwd_Sm100_Head64_Impl`
  - SM100f + h_q=128：当 `topk <= 1280` 且 small_topk_impl 支持所需特性时，使用 `Fwd_Sm100_Head128_Small_TopK_Impl`；否则使用 `Fwd_Sm100_Head128_Impl`。
- 返回 3 个张量：out `[s_q, h_q, d_v]`，max_logits `[s_q, h_q]`，lse `[s_q, h_q]`。

---

## F-025：dense_fwd.h（SM100 Dense Prefill 接口）

- 文件：[csrc/api/dense_fwd.h](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/csrc/api/dense_fwd.h#L1-L5)
- 仅 `#include "sm100/prefill/dense/interface.h"`。
- SM100 dense prefill 接口声明在 [csrc/sm100/prefill/dense/interface.h](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/csrc/sm100/prefill/dense/interface.h#L1-L12)：
  - `void FMHACutlassSM100FwdRun(workspace_buffer, q, k, v, cumulative_seqlen_q, cumulative_seqlen_kv, o, lse, mask_mode_code, softmax_scale, max_seqlen_q, max_seqlen_kv, is_varlen)`
  - `void FMHACutlassSM100BwdRun(workspace_buffer, d_o, q, k, v, o, lse, cumulative_seqlen_q, cumulative_seqlen_kv, dq, dk, dv, mask_mode_code, softmax_scale, max_seqlen_q, max_seqlen_kv, is_varlen)`

---

## F-026：SM90 Dense Decode 配置与 Traits

- 文件：[csrc/sm90/decode/dense/config.h](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/csrc/sm90/decode/dense/config.h#L1-L10)
- 命名空间 `Config`：
  - `BLOCK_SIZE_M = 64`
  - `PAGE_BLOCK_SIZE = 64`
  - `HEAD_DIM_K = 576`
  - `HEAD_DIM_V = 512`

- 文件：[csrc/sm90/decode/dense/traits.h](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/csrc/sm90/decode/dense/traits.h#L1-L107)
- 模板 `Traits<InputT_>`（InputT 为 `cutlass::bfloat16_t` 或 `cutlass::half_t`）：
  - `NUM_THREADS = 256`
  - WGMMA 配置：
    - `TiledMMA_QK_sQ`：MMA 形状 `64x64x16`，SS 模式，K-major 布局
    - `TiledMMA_QK_rQ`：RS 模式
    - `TiledMMA_PV_LocalP`：MMA 形状 `64x256x16`，RS 模式，MN-major
    - `TiledMMA_PV_RemoteP`：SS 模式
  - SharedMemoryPlan 包含：`smem_sQ, smem_sK0, smem_sK1`（双缓冲 K），`smem_sP0`，`smem_sM`，`sL_reduction_wksp`，`smem_sScale0, smem_sScale1`，barriers。
- `TmaParams` 模板包含 Q/K/O 的 shape 和 TMA descriptor。
- NamedBarriers 枚举：`sScale0Ready, sScale1Ready, sP0Ready, rO1sP0sV0RIssued, sMInitialized`。

---

## F-027：SM90 Dense Decode 内核入口声明

- 文件：[csrc/sm90/decode/dense/splitkv_mla.h](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/csrc/sm90/decode/dense/splitkv_mla.h#L1-L10)
- 命名空间 `sm90`：
  - `template<typename InputT> void run_flash_splitkv_mla_kernel(DenseAttnDecodeParams &params);`

---

## F-028：SM90 Sparse FP8 Decode 配置

- 文件：[csrc/sm90/decode/sparse_fp8/config.h](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/csrc/sm90/decode/sparse_fp8/config.h#L1-L20)
- 命名空间 `sm90::decode::sparse_fp8`：
  - `HEAD_DIM_K = 576`
  - `HEAD_DIM_V = 512`
  - `HEAD_DIM_NOPE = HEAD_DIM_V`（512）
  - `HEAD_DIM_ROPE = HEAD_DIM_K - HEAD_DIM_V`（64）
  - `QUANT_TILE_SIZE = 128`
  - `NUM_SCALES = HEAD_DIM_NOPE / QUANT_TILE_SIZE`（4）
  - `NUM_BYTES_PER_TOKEN = HEAD_DIM_NOPE + NUM_SCALES*sizeof(float) + HEAD_DIM_ROPE*sizeof(bf16)`（= 512 + 16 + 128 = 656）
  - `PAGE_BLOCK_SIZE = 64`

---

## F-029：SM90 Sparse FP8 Decode 内核模板参数

- 文件：[csrc/sm90/decode/sparse_fp8/splitkv_mla.cuh](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/csrc/sm90/decode/sparse_fp8/splitkv_mla.cuh#L15-L277)（通过 config.h 引用的 KernelTemplate）
- 模板：`template<ModelType MODEL_TYPE, int NUM_HEADS> class KernelTemplate`
- 编译期常量：
  - `NUM_HEADS == 64 || NUM_HEADS == 128`（static_assert）
  - `NUM_M_BLOCKS = NUM_HEADS / 64`
  - `CLUSTER_SIZE = NUM_M_BLOCKS`
  - `HEAD_DIM_K = MODEL_TYPE == V32 ? 576 : 512`
  - `HEAD_DIM_V = 512`
  - `HEAD_DIM_ROPE = 64`
  - `HEAD_DIM_NOPE = HEAD_DIM_K - HEAD_DIM_ROPE`
  - `QUANT_TILE_SIZE = MODEL_TYPE == V32 ? 128 : 64`
  - `NUM_SCALES = MODEL_TYPE == V32 ? 4 : 8`（MODEL1: 7 fp8 + 1 padding）
  - `NUM_THREADS = 128*3 = 384`
  - `BLOCK_M = 64`
  - `TOPK_BLOCK_SIZE = 64`
  - `NUM_K_BUFS = 2`（双缓冲）
- MMA 指令：
  - `TiledMMA_QK`: `GMMA::MMA_64x64x16_F32BF16BF16_SS`
  - `TiledMMA_QK_rQ`: `GMMA::MMA_64x64x16_F32BF16BF16_RS`
  - `TiledMMA_PV_LocalP`: `GMMA::MMA_64x256x16_F32BF16BF16_RS`（MN major）
  - `TiledMMA_PV_RemoteP`: `GMMA::MMA_64x256x16_F32BF16BF16_SS`（MN major）
- NamedBarriers：`sScale_and_sS_ready, sScale_and_sS_free, oBuf_free_and_sL_ready, epilogue_r2s_ready, batch_loop_sync, warpgroup0_sync`。
- 使用 Cluster（CLUSTER_SIZE = NUM_M_BLOCKS）进行 MQA/GQA 多头协作。
- SharedMemoryPlan 包含：Q smem、K/O 共用 union（双缓冲 K）、S smem（attention scores）、有效性掩码 `is_kv_valid`、online softmax 状态（`sM, sL, sScale, sOScale`）、transaction barriers。

---

## F-030：SM90 Sparse FP8 Decode 反量化组件

- 文件：[csrc/sm90/decode/sparse_fp8/components/dequant.h](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/csrc/sm90/decode/sparse_fp8/components/dequant.h#L1-L127)
- 定义 `fp8x8` 和 `fp8x16` 结构体（基于 `__nv_fp8x4_e4m3`）。
- `cvt_fp8x8_bf16x8(const fp8x8 &inputs, const __nv_bfloat162 &scale_bf162)`：将 8 个 FP8 E4M3 值转为 8 个 BF16 值并乘以 scale。
- L1 缓存提示枚举：`L1CacheHint { NO_ALLOCATE, EVICT_FIRST, EVICT_NORMAL, EVICT_LAST }`。
- L2 预取提示枚举：`L2PrefetchHint { B64, B128, B256 }`。
- `load_128b_from_gmem<T, l1_cache_hint, l2_prefetch_hint>(const void* addr)` 和 `load_64b_from_gmem<...>(...)`：使用 PTX `ld.global.nc.L1::...L2::...` 指令的带缓存提示全局内存加载。

---

## F-031：SM90 Sparse Prefill 内核配置

- 文件：[csrc/sm90/prefill/sparse/config.h](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/csrc/sm90/prefill/sparse/config.h)（引用的 KernelTemplate）
- 文件：[csrc/sm90/prefill/sparse/fwd.h](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/csrc/sm90/prefill/sparse/fwd.h#L1-L9)
- 命名空间 `sm90`：`void run_fwd_kernel(const SparseAttnFwdParams& params);`
- KernelTemplate（在 `fwd.cu`/`phase1.cuh` 中定义，通过 sparse_fwd.h 中的引用可知）：
  - 模板参数：`int D_QK, bool HAVE_TOPK_LENGTH`
  - `D_V = 512, B_H = 64, B_TOPK = 64, NUM_THREADS = 384`
  - V3.2（D_QK=576）时 S 缓冲区与 K 的 RoPE 部分重叠以节省 shared memory；MODEL1（D_QK=512）时分配两个 S 缓冲区。
  - MMA 配置：`MMA_64x64x16_F32BF16BF16_SS`（QK），`MMA_64x256x16_F32BF16BF16_RS/SS`（PV）。
  - NamedBarriers：`wg0_bunch_0_ready, wg1_bunch_0_ready, wg0_s0_ready, wg1_s1_ready, sL_ready, warpgroup0_sync, warpgroup1_sync, epilogue_sync`。

---

## F-032：SM100 Sparse Decode Head64 配置

- 文件：[csrc/sm100/decode/head64/config.h](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/csrc/sm100/decode/head64/config.h#L30-L210)
- 模板：`template<ModelType MODEL_TYPE> struct KernelTemplate`
- 编译期常量：
  - `D_Q = MODEL_TYPE == V32 ? 576 : 512`
  - `D_K = D_Q`
  - `D_V = 512`
  - `D_NOPE = V32 ? 512 : 448`
  - `D_ROPE = 64`
  - `QUANT_TILE_SIZE = V32 ? 128 : 64`
  - `V_HAVE_ROPE = V32 ? false : true`（V32 模式 V 不含 RoPE，MODEL1 模式 V 含 RoPE）
  - `NUM_SCALES_EACH_TOKEN = V32 ? 4 : 8`（含 padding）
  - `TMA_K_STRIDE = V32 ? 656 : 576`
  - `B_H = 64, B_TOPK = 64, NUM_BUFS = 2, NUM_INDEX_BUFS = 4`
  - `NUM_THREADS = 128*3 = 384`
  - `MAX_INIT_VAL = -1e30f`（避免 -inf - -inf = NaN）
  - `D_Q_SW128 = 512, D_Q_SW64 = V32 ? 64 : 0`
  - `K_ROPE_SW = V32 ? 64 : 128`（字节，V32 RoPE 用 SW64，MODEL1 用 SW128）
- Tensor Memory 列布局：
  - 列 0~255：输出 O
  - 列 256~：Q
  - 列 400~464：P（attention scores）
- MMA 指令：
  - `TiledMMA_P`: `SM100_MMA_F16BF16_WS_TS_NOELECT<bf16, bf16, float, 64, 128, K, K>`（B_TOPK*2 用于 dual gemm）
  - `TiledMMA_O`: `SM100_MMA_F16BF16_WS_SS_NOELECT<bf16, bf16, float, 64, 256, K, MN>`
- SM100 使用 Tensor Memory（tmem）存储 Q、P、O；使用 UTCCP（Tensor Memory copy）和 UTCMMA。
- SharedMemoryPlan 使用 union 重叠 Q/O 和 KV dequant 缓冲区，节省 shared memory。
- 包含多种 transaction barriers 用于 TMA async copy 同步。

---

## F-033：SM100 Decode Head128 支持说明

- 文件：[csrc/sm100/decode/head128/README.md](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/csrc/sm100/decode/head128/README.md#L1)
- 内容："Head128 decoding kernels are located at `csrc/sm100/prefill/sparse/fwd_for_small_topk/head128/instantiations/phase1_decode_k512.cu` (for k_dim = 512) or simulated using 2x head64 kernel"。
- 即：SM100 上 h_q=128 的 decode 有两种路径：
  1. d_qk=512（MODEL1）时使用 `fwd_for_small_topk/head128` 的 decode 模式专门内核。
  2. d_qk=576（V32）时通过调用两次 head64 内核模拟（`Decode_Sm100_Head64x2_Impl`）。

---

## F-034：SMxx 通用内核（调度元数据 + Combine）

- 文件：[csrc/smxx/decode/get_decoding_sched_meta/get_decoding_sched_meta.h](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/csrc/smxx/decode/get_decoding_sched_meta/get_decoding_sched_meta.h#L1-L8)
- 命名空间 `smxx::decode`：`void run_get_decoding_sched_meta_kernel(GetDecodeSchedMetaParams &params);`

- 文件：[csrc/smxx/decode/combine/combine.h](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/csrc/smxx/decode/combine/combine.h#L1-L10)
- 命名空间 `smxx::decode`：`template<typename ElementT> void run_flash_mla_combine_kernel(CombineParams &params);`
- 这两个内核是架构无关的通用组件，被 SM90 和 SM100 的 dense/sparse decode 路径共同使用。

---

## F-035：SM100 Sparse Prefill/Decode 公共子程序

- 文件：[csrc/sm100/prefill/sparse/common_subroutine.h](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/csrc/sm100/prefill/sparse/common_subroutine.h#L1-L208)
- `load_indices_and_generate_mask(lane_idx, gIndices, s_kv, abs_pos_start, topk_length)`：从全局内存加载 K/V 索引，每线程加载 8 个，生成有效性掩码（char 类型 bitmask）。
- `retrieve_mask_and_reduce_p<NUM_ELEMS_PER_THREAD, TMEM_COL_START, ...>(k_validness_base, local_warp_idx, lane_idx, slot_bar_P_empty_arrival, p_exchange_buf, p)`：从 Tensor Memory 获取 P，在 shared memory 中做 warp 间 reduce，执行 masking。Dual GEMM 产生两块 P（行 0-63 和 64-127），经 reduce 合并为一块。
- `rescale_O<D_V, CHUNK_SIZE, TMEM_COL_START>(scale_factor)`：对 Tensor Memory 中的 O 按 chunk 重新缩放。
- `get_max(p[])`：求线程本地 P 的最大值。
- `get_s_from_p(s[], p[], scale, new_max)`：计算 `s := exp2f(p*scale - new_max)` 并求和。

---

## F-036：setup.py 编译配置

- 文件：[setup.py](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/setup.py#L1-L151)
- 包名：`flash_mla`，版本 `1.0.0+<git_rev>`。
- CUDA 扩展模块名：`flash_mla.cuda`。
- 编译环境：C++20，`-O3`/`-DNDEBUG`，`--use_fast_math`。
- 架构 flags：SM90a（`arch=compute_90a,code=sm_90a`）和 SM100f（`arch=compute_100f,code=sm_100f`），可通过环境变量 `FLASH_MLA_DISABLE_SM90=1` / `FLASH_MLA_DISABLE_SM100=1` 禁用。
- NVCC 版本要求：SM100 编译需要 NVCC 12.9+。
- 源文件列表：
  - API：`csrc/api/api.cpp`
  - smxx 通用：`get_decoding_sched_meta.cu`、`combine.cu`
  - SM90 dense decode：`fp16.cu`、`bf16.cu`
  - SM90 sparse decode：`model1_persistent_h64.cu`、`model1_persistent_h128.cu`、`v32_persistent_h64.cu`、`v32_persistent_h128.cu`
  - SM90 sparse prefill：`fwd.cu`、4 个 phase1 instantiations（k512/k576 × with/without topklen）
  - SM100 dense prefill/backward：`fmha_cutlass_fwd_sm100.cu`、`fmha_cutlass_bwd_sm100.cu`
  - SM100 sparse prefill：head64（k512/k576）、head128（k512/k576）、fwd_for_small_topk/head128（phase1_prefill_k512.cu）
  - SM100 sparse decode：head64（v32.cu、model1.cu）、fwd_for_small_topk/head128（phase1_decode_k512.cu）
- 可选编译宏：`FLASH_MLA_DISABLE_FP16`（禁用 FP16 dense decode）。
- 依赖：CUTLASS（git submodule at `csrc/cutlass`）、kerutils（`csrc/kerutils/include`）。

---

## F-037：benchmark 脚本配置与用法

- 文件：[benchmark/bench_flash_mla.py](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/benchmark/bench_flash_mla.py#L1-L520)
- 导入：`flash_mla_with_kvcache, get_mla_metadata`（来自 flash_mla），`flashinfer`，`triton`。
- 4 个 benchmark 目标（`FUNC_TABLE`）：
  1. `torch`：PyTorch 参考实现（`scaled_dot_product_attention` + `repeat_interleave` 处理 GQA）
  2. `flash_mla`：FlashMLA CUDA 内核（调用 `flash_mla_with_kvcache`）
  3. `flash_infer`：FlashInfer 的 `BatchMLAPagedAttentionWrapper`（backend="fa3"）
  4. `flash_mla_triton`：Triton 实现的 MLA decode kernel（split-KV 后 reduce）
- 默认 shape_configs：
  - batch=128, s_q=1（decode 场景）, h_q=128, h_kv=1, d=576(=512+64), dv=512, causal=True, dtype=bfloat16
  - 序列长度：1024, 2048, 4096, 8192, 16384, 32768
- block_size = 64（硬编码）。
- 命令行参数：
  - `--baseline`（默认 "torch"）
  - `--target`（默认 "flash_mla"）
  - `--all`：运行所有目标
  - `--one`：运行单个目标
  - `--compare`：对比 baseline 和 target
- Triton 参考 kernel 参数：
  - `BLOCK_H = 16, BLOCK_N = 64, NUM_KV_SPLITS = 32`
  - Triton kernel 分为 `_mla_attn_kernel`（分块 QK + PV）和 `_mla_softmax_reducev_kernel`（split-KV reduce）。
- 性能指标计算：
  - FLOPS = `s_q * total_seqlens * h_q * (d + dv) * 2`
  - Bytes = `(total_seqlens * h_kv * d + b * s_q * h_q * d + b * s_q * h_q * dv) * (finfo(dtype).bits // 8)`
  - 输出 TFLOPS 和 GB/s。
- `run_flash_mla` 中调用 `get_mla_metadata(cache_seqlens, s_q * h_q // h_kv, h_kv)`（传参兼容旧接口），然后调用 `flash_mla_with_kvcache(q, blocked_k, block_table, cache_seqlens, dv, tile_scheduler_metadata, num_splits, causal=causal)`。

---

## F-038：utils.h 工具宏与 RingBufferState

- 文件：[csrc/utils.h](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/csrc/utils.h#L1-L82)
- 宏定义：
  - `CHECK_CUDA(call)`：CUDA 错误检查，失败时 fprintf + exit(1)。
  - `CHECK_CUDA_KERNEL_LAUNCH()`：检查 kernel launch 错误。
  - `FLASH_ASSERT(cond)`：Host 端断言。
  - `FLASH_DEVICE_ASSERT(cond)`：Device 端断言（printf + trap）。
  - `TRAP_ONLY_DEVICE_ASSERT(cond)`：Device 端仅 trap 不打印。
- `template<typename T> __host__ __device__ T ceil_div(const T &a, const T &b)`：返回 `(a + b - 1) / b`。
- `struct RingBufferState`：多阶段流水线环形缓冲区状态管理。
  - `cur_block_idx: uint32_t`
  - `update()`：`cur_block_idx += 1`
  - `get<NUM_STAGES>() const`：返回 `{stage_idx, phase}` 对（`stage_idx = cur_block_idx % NUM_STAGES`，`phase = (cur_block_idx / NUM_STAGES) & 1`）。
  - `offset_by(offset) const`：返回偏移后的新 RingBufferState。

---

## F-039：SM90/SM100 helpers 差异

- 文件：[csrc/sm90/helpers.h](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/csrc/sm90/helpers.h#L1-L170)
- SM90 Hopper 特定辅助函数：
  - `cp_async_cacheglobal_l2_prefetch_256B`：使用 `cp.async.cg.shared.global.L2::256B` PTX 指令进行 L2 预取。
  - `createpolicy_evict_last()` / `createpolicy_evict_first()`：创建 L2 cache 策略（`createpolicy.fractional.L2::evict_last/evict_first.b64`）。
  - `get_AorC_row_idx/get_AorC_col_idx`：WGMMA 片段布局行列索引映射。
  - `gemm/gemm_ss/gemm_rs`：封装 warpgroup arrive/wait/fence 的 WGMMA 执行辅助函数。
  - `get_sm_id()`：通过 `mov.u32 %0, %%smid` 获取当前 SM ID。
  - `get_peer_addr(p)`：DSM 跨 cluster 地址计算（`p ^ PEER_ADDR_MASK(16777216)`）。
  - `launch_tma_copy(...)`：封装 TMA async copy 与 ClusterTransactionBarrier。

- 文件：[csrc/sm100/helpers.h](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/csrc/sm100/helpers.h#L1-L34)
- SM100 Blackwell 特定辅助函数：
  - `int4_max/int4_min`：int4 向量的 max/min。
  - `fp8x2_to_bf16x2_with_scale(data, scale)`：将 2 个 FP8 E4M3 转为 2 个 BF16 并乘以 scale（TODO: 待 CUDA>=13.1 使用原生转换）。

---

## F-040：SM100 Dense Prefill/Backward CUTLASS 内核

- 文件：[csrc/sm100/prefill/dense/](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/csrc/sm100/prefill/dense/)
- SM100 dense prefill 基于 CUTLASS 实现，包含：
  - 编译单元：`fmha_cutlass_fwd_sm100.cu`、`fmha_cutlass_bwd_sm100.cu`
  - 主循环/Epilogue/Load TMA warpspecialized 内核
  - MLA 专用 mainloop 和 load TMA 实现：`sm100_fmha_mla_fwd_mainloop_tma_warpspecialized.hpp`、`sm100_fmha_mla_load_tma_warpspecialized.hpp`
  - 公共组件：`fmha_common.hpp`、`pipeline_mla.hpp`、`mask.cuh`、`gather_tensor.hpp`
  - Device 层：`fmha.hpp`（fwd device）、`fmha_device_bwd.hpp`（bwd device）
  - Kernel 层：tile scheduler、causal tile scheduler、bwd convert/sum_OdO kernels、fwd/bwd tma warpspecialized kernels
- 这部分对应 `flash_attn_varlen_func`（及其 qkvpacked/kvpacked 变体）的底层实现。
