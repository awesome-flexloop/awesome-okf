# DeepGEMM 源码事实清单 (Facts)

> 收集时间: 2026-08-22
> 源码路径: `d:\spaces\SpecWeave\external\libs\ai\deepseek-ai\DeepGEMM`

---

## 一、项目入口与版本

**F-001** 文件: `deep_gemm/__init__.py`
- 顶层包 `deep_gemm`，导入 `os`, `subprocess`, `torch`
- 尝试从 `.envs` 模块导入 `persistent_envs`（字典类型），遍历其 key/value 设置到 `os.environ`（仅当 key 不存在时）
- 从 `._C`（C++ 扩展模块）导入配置函数：`set_num_sms`, `get_num_sms`, `set_tc_util`, `get_tc_util`, `set_ignore_compile_dims`, `set_block_size_multiple_of`, `set_pdl`, `get_pdl`
- 从 `._C` 导入 cuBLASLt 核函数：`cublaslt_gemm_nt`, `cublaslt_gemm_nn`, `cublaslt_gemm_tn`, `cublaslt_gemm_tt`
- 在 try 块中从 `._C` 导入 DeepGEMM 核函数（FP8/FP4 GEMM、BF16 GEMM、einsum、attention、hyperconnection、layout、MegaMoE）；ImportError 时静默跳过（兼容 CUDA < 12.1）
- 定义别名：`fp8_m_grouped_gemm_nt_masked = m_grouped_fp8_gemm_nt_masked`，`bf16_m_grouped_gemm_nt_masked = m_grouped_bf16_gemm_nt_masked`
- 从 `.mega` 导入：`SymmBuffer`, `get_symm_buffer_for_mega_moe`, `transform_weights_for_mega_moe`, `fp8_fp4_mega_moe`, `bf16_mega_moe`
- 导入 `.testing` 和 `.utils` 子模块，并执行 `from .utils import *`
- 在 try 块中导入 `.legacy` 子模块（A100 Triton 核函数），异常时打印警告
- 定义函数 `_find_cuda_home() -> str`：依次检查 `CUDA_HOME`/`CUDA_PATH` 环境变量、`which nvcc` 命令路径，默认 `/usr/local/cuda`；断言 `cuda_home is not None`，返回路径字符串
- 调用 `_C.init()`，参数为 `os.path.dirname(os.path.abspath(__file__))`（库根目录路径）和 `_find_cuda_home()` 返回值（CUDA home 路径）
- `__version__ = '2.6.1'`

---

## 二、公共 Python API（C++ 绑定导出）

### 2.1 GEMM 运算 (csrc/apis/gemm.hpp, namespace `deep_gemm::gemm`)

**F-002** 文件: `csrc/apis/gemm.hpp`
- 命名空间 `deep_gemm::gemm`
- 条件编译 `#if DG_FP8_COMPATIBLE and DG_TENSORMAP_COMPATIBLE` 下包含头文件：`sm90_fp8_gemm_1d1d.hpp`, `sm90_fp8_gemm_1d2d.hpp`, `sm90_bf16_gemm.hpp`, `sm100_fp8_fp4_gemm_1d1d.hpp`, `sm100_bf16_gemm.hpp`
- 无条件包含 `smxx_cublaslt.hpp` 和 `layout.hpp`

**F-003** 静态函数 `early_return(const int& m, const int& n, const int& k, const torch::Tensor& d, const std::optional<torch::Tensor>& c) -> bool`
- 当 `m == 0 or n == 0` 时返回 `true`
- 检查 C/D 张量数据指针是否相同（`is_cd_same`），相同则断言 shapes 和 strides 一致
- 断言 `d.scalar_type() == torch::kBFloat16 or d.scalar_type() == torch::kFloat`
- 若 `c.has_value()`，调用 `check_major_type_cd(c.value())` 并断言 d 与 c 类型一致
- 当 `k == 0`：若 C/D 不同且 c 有值则 `d.copy_(c.value())`，否则 `d.zero_()`；返回 `true`
- 若 `c.has_value() and not is_cd_same`，执行 `d.copy_(c.value())`
- 返回 `false`

**F-004** 静态函数 `check_k_grouped_args(const std::optional<std::vector<int>>& ks_cpu, const torch::Tensor& grouped_layout, const int& num_groups, const bool& use_psum_layout, const int& k_alignment, const int& sum_k_if_ks_cpu_missing = 0) -> int`
- 断言 `grouped_layout.is_contiguous()`，`grouped_layout.scalar_type() == torch::kInt`，`grouped_layout.numel() == num_groups`
- 若 `ks_cpu` 有值且非空：断言 size == num_groups，每个 k 满足 `k % k_alignment == 0`，返回 sum_k
- 否则断言 `use_psum_layout` 为 true，返回 `sum_k_if_ks_cpu_missing`

**F-005** 静态函数 `fp8_fp4_gemm_nt(...)` -> void
- 参数：`a: pair<Tensor,Tensor>`, `b: pair<Tensor,Tensor>`, `d: Tensor`, `c: optional<Tensor>`, `recipe: optional<tuple<int,int,int>>`, `recipe_a: optional<tuple<int,int>>`, `recipe_b: optional<tuple<int,int>>`, `compiled_dims: string = "nk"`, `disable_ue8m0_cast: bool = false`
- 形状约束：`[M, K] @ [N, K].T`
- 获取 major_a, major_b；SM90 下断言 both K-major
- 调用 `check_major_type_cd(d)`
- 通过 `check_ab_fp8_fp4` 获取 (m,k), (n,k_)；断言 m==m_, n==n_, k==k_
- 调用 `layout::transform_sf_pair_into_required_layout(...)` 转换缩放因子
- 架构分发：arch_major==9 且 sfa 为 Float 类型：gran_n==1 调用 `sm90_fp8_gemm_1d1d`，否则调用 `sm90_fp8_gemm_1d2d`；arch_major==10 且 sfa 为 Int 类型调用 `sm100_fp8_fp4_gemm_1d1d`

**F-006** 静态函数 `fp8_fp4_gemm_nn(...)` -> void：通过转置 b 调用 `fp8_fp4_gemm_nt(a, {b.first.T, b.second.T}, ...)`
**F-007** 静态函数 `fp8_fp4_gemm_tn(...)` -> void：转置 a 和 b 调用 `fp8_fp4_gemm_nt`
**F-008** 静态函数 `fp8_fp4_gemm_tt(...)` -> void：转置 a 调用 `fp8_fp4_gemm_nt`

**F-009** 静态函数 `m_grouped_fp8_fp4_gemm_nt_contiguous(...)` -> void
- 参数：a, b, d, grouped_layout, recipe, recipe_a, recipe_b, compiled_dims="nk", disable_ue8m0_cast=false, use_psum_layout=false, ensure_zero_padding=true, expected_m_for_psum_layout=nullopt
- 形状：`[M, K] @ [G, N, K].mT`
- 断言 major_a == K-major；fp8_requires_k_major() 时 major_b == K-major
- 架构分发：SM90 -> `sm90_m_grouped_fp8_gemm_contiguous_1d2d`；SM100 -> `sm100_m_grouped_fp8_fp4_gemm_contiguous_1d1d`

**F-010** 静态函数 `m_grouped_fp8_fp4_gemm_nn_contiguous(...)` -> void：转置 b 的最后两维调用 nt_contiguous
**F-011** 静态函数 `m_grouped_fp8_fp4_gemm_nt_masked(...)` -> void
- 参数额外包含 `masked_m: Tensor`, `expected_m: int`
- 形状：`[G, M, K] @ [G, N, K].mT`
- 架构分发：SM90 -> `sm90_m_grouped_fp8_gemm_masked_1d2d`；SM100 -> `sm100_m_grouped_fp8_fp4_gemm_masked_1d1d`

**F-012** 静态函数 `k_grouped_fp8_gemm_tn_contiguous(...)` -> void
- 参数：a, b, d, ks_cpu, grouped_layout, c, recipe=(1,1,128), compiled_dims="mn", use_psum_layout=false
- 断言 recipe 为 (1,1,?)，gran_k 为 32 或 128
- SM100 分发：`sm100_k_grouped_fp8_gemm_1d1d`

**F-013** 静态函数 `k_grouped_fp8_gemm_nt_contiguous(...)` -> void
- 参数：同上，recipe 默认 (1,1,128)
- 断言 recipe == (1,1,128)，断言 not use_psum_layout 且 ks_cpu 非空
- 分配 tensormap buffer：大小 `num_sms * 4 * sizeof(CUtensorMap)` 字节
- SM90 分发：`sm90_k_grouped_fp8_gemm_1d1d`

**F-014** 静态函数 `bf16_gemm_nt(...)` -> void
- 参数：a: Tensor, b: Tensor, d: Tensor, c: optional<Tensor>, compiled_dims: string = "nk"
- 形状：`[M, K] @ [N, K].T`
- 断言 a/b 为 kBFloat16，d 为 kBFloat16 或 kFloat
- 架构分发：SM90 -> `sm90_bf16_gemm`；SM100 -> `sm100_bf16_gemm`

**F-015** `bf16_gemm_nn`, `bf16_gemm_tn`, `bf16_gemm_tt` 均通过转置调用 `bf16_gemm_nt`

**F-016** `m_grouped_bf16_gemm_nt_contiguous(...)` -> void
- 参数：a, b, d, grouped_layout, compiled_dims="nk", use_psum_layout=false, ensure_zero_padding=true, expected_m_for_psum_layout=nullopt
- SM90 -> `sm90_m_grouped_bf16_gemm_contiguous`；SM100 -> `sm100_m_grouped_bf16_gemm_contiguous`

**F-017** `m_grouped_bf16_gemm_nn_contiguous` 通过转置 b 调用 nt_contiguous

**F-018** `m_grouped_bf16_gemm_nt_masked(...)` -> void
- 参数额外：masked_m: Tensor, expected_m: int
- SM90 -> `sm90_bf16_m_grouped_gemm_masked`；SM100 -> `sm100_m_grouped_bf16_gemm_masked`

**F-019** `k_grouped_bf16_gemm_tn_contiguous(...)` -> void
- 参数：a, b, d, ks_cpu, grouped_layout, c, compiled_dims="mn", use_psum_layout=false
- SM90 -> `sm90_bf16_k_grouped_gemm`（断言 not use_psum_layout）；SM100 -> `sm100_bf16_k_grouped_gemm`

**F-020** 静态函数 `cublaslt_gemm_nt(...)` -> void
- 参数：a: Tensor, b: Tensor, d: Tensor, c: optional<Tensor>
- 调用 `cublaslt_gemm(a, b, d, m, n, k, major_a, major_b, c.has_value())`
- `cublaslt_gemm_nn/tn/tt` 通过转置调用 nt 版本

**F-021** `register_apis(pybind11::module_& m)` 函数中注册的 Python 绑定：
- FP8/FP4 GEMM（条件编译）：`fp8_fp4_gemm_nt/nn/tn/tt`, `m_grouped_fp8_fp4_gemm_nt/nn_contiguous`, `m_grouped_fp8_fp4_gemm_nt_masked`, `k_grouped_fp8_gemm_tn/nt_contiguous`
- FP8 GEMM 别名（attr 赋值）：`fp8_gemm_nt = fp8_fp4_gemm_nt`, `fp8_gemm_nn = fp8_fp4_gemm_nn`, `fp8_gemm_tn = fp8_fp4_gemm_tn`, `fp8_gemm_tt = fp8_fp4_gemm_tt`, `m_grouped_fp8_gemm_nt/nn_contiguous`, `m_grouped_fp8_gemm_nt_masked`
- BF16 GEMM（条件编译）：`bf16_gemm_nt/nn/tn/tt`, `m_grouped_bf16_gemm_nt/nn_contiguous`, `m_grouped_bf16_gemm_nt_masked`, `k_grouped_bf16_gemm_tn_contiguous`
- cuBLASLt GEMM（无条件）：`cublaslt_gemm_nt/nn/tn/tt`

### 2.2 Attention 运算 (csrc/apis/attention.hpp, namespace `deep_gemm::attention`)

**F-022** 文件: `csrc/apis/attention.hpp`，命名空间 `deep_gemm::attention`
- 条件编译下包含：`sm90_fp8_gemm_1d1d.hpp`, `sm90_fp8_gemm_1d2d.hpp`, `sm100_fp8_fp4_gemm_1d1d.hpp`, `sm100_mqa_logits.hpp`, `sm90_fp8_mqa_logits.hpp`, `smxx_clean_logits.hpp`

**F-023** 静态函数 `fp8_gemm_nt_skip_head_mid(...)` -> void
- 参数：a: pair<Tensor,Tensor>, b: pair<Tensor,Tensor>, d: Tensor, head_splits: tuple<int,int,int>, recipe: optional<tuple<int,int,int>>, compiled_dims="nk", disable_ue8m0_cast=false
- 形状 `[M,K] @ [N,K].T`，head_splits=(left,mid,right)，断言 `n % (left+right) == 0`，`n_ == n + n/(left+right)*mid`
- 生成 epilogue 类型字符串 `"epilogue::transform::EpilogueHeadSplits<{}, {}, {}>"`
- SM90 -> `sm90_fp8_gemm_1d2d`（含自定义 epilogue）；SM100 -> `sm100_fp8_fp4_gemm_1d1d`（含自定义 epilogue，gran_k=128）

**F-024** 静态函数 `fp8_fp4_mqa_logits(...)` -> torch::Tensor
- 参数：q: tuple<Tensor, optional<Tensor>>, kv: tuple<Tensor,Tensor>, weights: Tensor, cu_seq_len_k_start: Tensor, cu_seq_len_k_end: Tensor, clean_logits: bool=true, max_seqlen_k: int=0, logits_dtype: ScalarType=kFloat32
- q 解构为 (q_fp, q_sf)，kv 解构为 (kv_fp, kv_sf)
- `is_fp4 = (qk_dtype == kPackedFP4)`，`is_mx_sf = q_sf.has_value()`
- 从 q_fp 获取逻辑形状 (seq_len, num_heads, head_dim)，head_dim 约束：非FP4时==32，或64或128
- SM100 约束：num_heads ∈ {8,16,32,64}；SM90 约束：num_heads ∈ {32,64}，非mx_sf
- 常量 block_qh=128, block_kv=256，block_q = block_qh / num_heads
- logits 行步长 1024 字节对齐
- SM100 调用 `sm100_mqa_logits`；SM90 调用 `sm90_fp8_mqa_logits`
- 若 clean_logits 为 true，调用 `smxx_clean_logits`
- 返回 logits Tensor

**F-025** 静态函数 `get_paged_mqa_logits_metadata(...)` -> torch::Tensor
- 参数：context_lens: Tensor, block_kv: int, num_sms: int, indices: optional<Tensor>=nullopt
- 断言 context_lens.dim() == 2，scalar_type == kInt，is_contiguous
- 返回 schedule_metadata Tensor，形状 `{num_sms + 1, 2}`
- SM100 支持 block_kv ∈ {32,64,128}；SM90 仅 block_kv==64
- varlen 模式（indices 有值）仅 SM100 支持，断言 next_n==1

**F-026** 静态函数 `fp8_fp4_paged_mqa_logits(...)` -> torch::Tensor
- 参数：q: tuple<Tensor, optional<Tensor>>, fused_kv_cache: Tensor, weights: Tensor, context_lens: Tensor, block_table: Tensor, schedule_meta: Tensor, max_context_len: int, clean_logits: bool=false, logits_dtype: ScalarType=kFloat32, indices: optional<Tensor>=nullopt
- fused_kv_cache 形状 (num_kv_blocks, block_kv, num_heads_kv, head_dim_with_sf)
- 从 fused_kv_cache 派生 kv_cache（dtype=kPackedFP4 或 kFloat8_e4m3fn）和 kv_cache_sf（dtype=kInt32 或 kFloat32），通过 `torch::from_blob` 创建视图
- split_kv=256，logits 步长 1024 字节对齐
- SM100 调用 `sm100_paged_mqa_logits`；SM90 调用 `sm90_fp8_paged_mqa_logits`
- clean_logits 为 true 时调用 `smxx_clean_logits`（断言非 2D context_lens）
- 返回 logits Tensor

**F-027** 旧版 API 包装：
- `fp8_mqa_logits(q, kv, weights, cu_seq_len_k_start, cu_seq_len_k_end, clean_logits, max_seqlen_k) -> Tensor`：调用 `fp8_fp4_mqa_logits` 且 q_sf=nullopt, logits_dtype=kFloat
- `fp8_paged_mqa_logits(q, kv_cache, weights, context_lens, block_table, schedule_meta, max_context_len, clean_logits, indices) -> Tensor`：调用 `fp8_fp4_paged_mqa_logits` 且 q_sf=nullopt, logits_dtype=kFloat

**F-028** `register_apis(m)` 注册：`fp8_gemm_nt_skip_head_mid`, `fp8_fp4_mqa_logits`, `get_paged_mqa_logits_metadata`, `fp8_fp4_paged_mqa_logits`，旧版 `fp8_mqa_logits`, `fp8_paged_mqa_logits`

### 2.3 Einsum 运算 (csrc/apis/einsum.hpp, namespace `deep_gemm::einsum`)

**F-029** 文件: `csrc/apis/einsum.hpp`，命名空间 `deep_gemm::einsum`
- 条件编译下包含：`sm90_bmk_bnk_mn.hpp`, `sm100_bmk_bnk_mn.hpp`, `sm90_bf16_gemm.hpp`, `sm100_bf16_gemm.hpp`, `smxx_cublaslt.hpp`

**F-030** 静态函数 `bmk_bnk_mn(a: Tensor, b: Tensor, d: Tensor, c: optional<Tensor>) -> void`
- d 为 kFloat 时：断言 c 与 d 同指针/形状/步长；d 为 kBFloat16 时：分配 FP32 workspace，递归调用自身后 copy_(workspace)
- 断言 a/b/d contiguous；形状检查 (s,m,k) @ (s,n,k) -> (m,n)
- SM90 -> `sm90_bmn_bnk_mn_gemm`；SM100 -> `sm100_bmn_bnk_mn_gemm`

**F-031** 静态函数 `bhr_hdr_bhd(A: Tensor, B: Tensor, D: Tensor, use_cublaslt: bool) -> void`
- 形状 (b,h,r) @ (h,d,r).T -> (b,h,d)；A/B/D 均为 kBFloat16，stride(2)==1
- use_cublaslt -> `cublaslt_bhr_hdr_bhd`；SM90 -> `sm90_bf16_bhr_hdr_bhd`；SM100 -> `sm100_bf16_bhr_hdr_bhd`

**F-032** 静态函数 `bhd_hdr_bhr(A: Tensor, B: Tensor, D: Tensor, use_cublaslt: bool) -> void`
- 形状 (b,h,d) @ (h,d,r).T -> (b,h,r)
- use_cublaslt -> `cublaslt_bhd_hdr_bhr`；SM90 -> `sm90_bf16_bhd_hdr_bhr`；SM100 -> `sm100_bf16_bhd_hdr_bhr`

**F-033** 静态函数 `einsum(expr: string, a: Tensor, b: Tensor, d: Tensor, c: optional<Tensor>, use_cublaslt: bool=false) -> void`
- 断言 a/b 为 kBFloat16，d 为 kBFloat16 或 kFloat
- 支持的 expr：
  - `"bmk,bnk->mn"`：调用 `bmk_bnk_mn`（断言 not use_cublaslt）
  - `"bhr,hdr->bhd"`：调用 `bhr_hdr_bhd`（断言 not c.has_value()）
  - `"bhd,hdr->bhr"`：调用 `bhd_hdr_bhr`（断言 not c.has_value()）
- 其他表达式触发 DG_HOST_UNREACHABLE

**F-034** 静态函数 `fp8_bmm(a: Tensor, sfa: Tensor, b: Tensor, sfb: Tensor, d: Tensor, c: optional<Tensor>, recipe: optional<tuple<int,int,int>>, compiled_dims: string) -> void`
- 形状 `[B,M,K] @ [B,N,K].T`，通过 stride 判断 major（stride(-1)==1 为 K-major，stride(-2)==1 为 MN-major）
- a/b 为 kFloat8_e4m3fn，d 为 kBFloat16 或 kFloat
- SM100 -> `sm100_fp8_bmm`；否则 -> `sm90_fp8_bmm`

**F-035** 静态函数 `fp8_einsum(expr: string, a: pair<Tensor,Tensor>, b: pair<Tensor,Tensor>, d: Tensor, c: optional<Tensor>, recipe: tuple<int,int,int>=(1,128,128)) -> void`
- 支持的 expr：
  - `"bhr,hdr->bhd"`：permute 为 (h,b,d/r) 后调用 fp8_bmm（compiled_dims="nk"）
  - `"bhd,hdr->bhr"`（仅 SM100）：permute 后调用 fp8_bmm
  - `"bhd,bhr->hdr"`（仅 SM100）：permute 为 (h,d/r,b) 后调用 fp8_bmm（compiled_dims="mn"）

**F-036** `register_apis(m)` 注册：`einsum`, `fp8_einsum`

### 2.4 Hyperconnection 运算 (csrc/apis/hyperconnection.hpp)

**F-037** 文件: `csrc/apis/hyperconnection.hpp`，命名空间 `deep_gemm::hyperconnection`
- 条件编译下包含 `sm90_tf32_hc_prenorm_gemm.hpp`, `sm100_tf32_hc_prenorm_gemm.hpp`

**F-038** 静态函数 `tf32_hc_prenorm_gemm(a: Tensor, b: Tensor, d: Tensor, sqr_sum: Tensor, num_splits: optional<int>=nullopt) -> void`
- 断言 a/b 为 K-major，d 为 N-major，sqr_sum contiguous
- a 为 kBFloat16，b 为 kFloat，d 和 sqr_sum 为 kFloat
- num_splits 有值时 d 为 3D (num_splits, m, n)，sqr_sum 为 2D (num_splits, m)；无值时 d 为 2D，sqr_sum 为 1D
- SM90 -> `sm90_tf32_hc_prenorm_gemm`；SM100 -> `sm100_tf32_hc_prenorm_gemm`

**F-039** `register_apis(m)` 注册：`tf32_hc_prenorm_gemm`

### 2.5 Layout 工具 (csrc/apis/layout.hpp)

**F-040** 文件: `csrc/apis/layout.hpp`，命名空间 `deep_gemm::layout`
- 包含 `jit_kernels/heuristics/runtime.hpp`, `utils/layout.hpp`, `utils/compatibility.hpp`
- 条件编译下包含 `smxx_layout.hpp`

**F-041** 静态函数 `transform_sf_into_required_layout(sf: Tensor, mn: int, k: int, recipe: variant<tuple<int,int,int>, tuple<int,int>>, num_groups: optional<int>, is_sfa: optional<bool>, disable_ue8m0_cast: bool, psum_layout: optional<Tensor>=nullopt) -> Tensor`
- 从 recipe 解析 gran_mn, gran_k：tuple<int,int,int> 版本需 is_sfa，(is_sfa?0:1) 取 gran_mn，2 取 gran_k；tuple<int,int> 版本直接解构
- 先调用 `check_sf_layout(sf, mn, k, gran_mn, gran_k, num_groups)` 验证
- 转换规则：
  - (kFloat, gran_mn=1, gran_k=128) on SM90 或 disable_ue8m0_cast -> `get_mn_major_tma_aligned_tensor(sf)`
  - (kFloat, gran_mn=128, gran_k=128) on SM90 或 disable_ue8m0_cast -> `check_sf_layout(sf,..., sm90_sfb_check=true, type_check=kFloat)` 返回 sf
  - (kFloat, gran_k∈{32,128}) on SM100 -> 广播后调用 `get_mn_major_tma_aligned_packed_ue8m0_tensor(broadcasted, psum_layout)`
  - (kInt, gran_mn=1, gran_k∈{32,128}) on SM100 -> `check_sf_layout(sf,..., tma_stride_check=true, type_check=kInt)` 返回 sf

**F-042** 静态函数 `transform_sf_pair_into_required_layout(sfa, sfb, m, n, k, recipe, recipe_a, recipe_b, num_groups_a, num_groups_b, disable_ue8m0_cast=false, psum_layout=nullopt) -> tuple<Tensor, Tensor, int, int>`
- 若 recipe_a 和 recipe 均未提供，调用 `get_default_recipe(sfa_dtype, sfb_dtype)` 设置默认 recipe
- 断言 recipe_a 和 recipe_b 同时有值或同时无值，且与 recipe 互斥
- 分别转换 sfa（含 psum_layout）和 sfb
- 返回 (transformed_sfa, transformed_sfb, gran_k_a, gran_k_b)

**F-043** 静态函数 `transform_k_grouped_sf_into_required_layout(sf, ks_cpu, grouped_layout, recipe, k_alignment, use_psum_layout) -> Tensor`
- 断言 sf.dim()==2，recipe 为 (1,1,?)，gran_k∈{32,128}
- (kFloat, SM90) -> `get_mn_major_tma_aligned_tensor(sf)`
- (kFloat, SM100) -> `get_k_grouped_mn_major_tma_aligned_packed_ue8m0_tensor(...)`
- (kInt, SM100) -> `check_k_grouped_packed_ue8m0_tensor(...)`

**F-044** `register_apis(m)` 注册：
- 条件编译：`transform_sf_into_required_layout`, `get_tma_aligned_size`, `get_mn_major_tma_aligned_tensor`, `get_mn_major_tma_aligned_packed_ue8m0_tensor`, `get_k_grouped_mn_major_tma_aligned_packed_ue8m0_tensor`
- 无条件（通过 lambda 包装 heuristics_runtime）：
  - `set_mk_alignment_for_contiguous_layout(new_value: int)` -> void
  - `get_mk_alignment_for_contiguous_layout() -> int`
  - `get_theoretical_mk_alignment_for_contiguous_layout(expected_m: optional<int>=nullopt) -> int`

### 2.6 MegaMoE 运算 (csrc/apis/mega.hpp)

**F-045** 文件: `csrc/apis/mega.hpp`，命名空间 `deep_gemm::mega`
- 包含 `<deep_gemm/common/types.cuh>`, `<deep_gemm/scheduler/mega_moe.cuh>`
- 包含 `jit/compiler.hpp`, `jit/device_runtime.hpp`, `sm100_bf16_mega_moe.hpp`, `sm100_fp8_fp4_mega_moe.hpp`

**F-046** 静态函数 `get_token_alignment_for_mega_moe() -> int`：返回 `layout::kLCMCandidateBlockM`（值为 384）

**F-047** 静态函数 `get_block_m_for_mega_moe(num_ranks: int, num_experts: int, num_max_tokens_per_rank: int, num_tokens: int, num_topk: int, mma_type: string) -> int`
- 断言 num_tokens >= 0
- 调用 `parse_mma_kind(mma_type)` 解析 MMA 类型
- 调用 `get_block_config_for_mega_moe(...)` 返回元组，取其中 block_m 返回

**F-048** 静态函数 `get_symm_buffer_size_for_mega_moe(num_ranks, num_experts, num_max_tokens_per_rank, num_topk, hidden, intermediate_hidden, mma_type, activation, num_shared_experts=0) -> tuple<int64_t, function>`
- 断言 num_experts % num_ranks == 0，activation == "swiglu"，num_shared_experts >= 0
- 计算 num_ring_tokens（遍历 kCandidateBlockM 取最大 live pool blocks * block_m），对齐到 kLCMCandidateBlockM
- with_sf 时计算 num_sf_ring_tokens
- 构造 `layout::MegaMoEBuffer` 对象
- 返回 (num_bytes, slice_input_buffers)，其中 slice_input_buffers 是一个 lambda，接收 buffer Tensor 并返回 12 个 Tensor 视图的元组：(x, x_sf, topk_idx, topk_weights, shared_l1_acts, shared_l1_acts_sf, shared_l2_acts, shared_l2_acts_sf, l1_acts, l1_acts_sf, l2_acts, l2_acts_sf)
  - x 形状 (num_max_tokens_per_rank, hidden)，dtype 由 with_sf 决定（kFloat8_e4m3fn 或 kBFloat16）
  - x_sf 形状 (num_max_tokens_per_rank, hidden/128)，dtype kInt（仅 with_sf）
  - topk_idx 形状 (num_max_tokens_per_rank, num_topk)，dtype kInt64
  - topk_weights 形状 (num_max_tokens_per_rank, num_topk)，dtype kFloat32
  - l1_acts 形状 (num_ring_tokens, hidden)，l2_acts 形状 (num_ring_tokens, intermediate_hidden)
  - l1_acts_sf/l2_acts_sf 为 M-major（stride(0)=1）

**F-049** 静态函数 `fp8_fp4_mega_moe(y, l1_weights_tuple, l2_weights_tuple, shared_l1_weights_tuple_opt, shared_l2_weights_tuple_opt, cumulative_local_expert_recv_stats, sym_buffer, sym_buffer_ptrs, rank_idx, num_max_tokens_per_rank, num_experts, num_topk, recipe=(1,1,32), activation, activation_clamp_opt, fast_math=true) -> void`
- l1_weights_tuple 解构为 (l1_weights, l1_weights_sf)，l2_weights_tuple 解构为 (l2_weights, l2_weights_sf)
- 断言 recipe == (1,1,32)，activation == "swiglu"
- l1_weights/l2_weights scalar_type == kPackedFP4（即 torch::kInt8），K-major，contiguous
- l1 形状 (num_experts_per_rank, intermediate_hidden*2, hidden)（FP4 时 k*=2），l2 形状 (num_experts_per_rank, hidden, intermediate_hidden)
- weight SF 布局检查：gran_mn=1, gran_k=32, MN-major, TMA-aligned, dtype kInt
- shared experts 存在时检查 shared_l1/l2_weights（kFloat8_e4m3fn，2D，K-major）
- cumulative_local_expert_recv_stats 有值时：dtype kInt，numel == num_experts_per_rank，contiguous
- 验证 sym_buffer.nbytes() >= num_required_bytes
- 仅支持 SM100，调用 `sm100_fp8_fp4_mega_moe(...)`
- DG_COMM_KERNEL_DEBUG 环境变量非零时对 sym_buffer 执行 zero_()

**F-050** 静态函数 `bf16_mega_moe(y, l1_weights, l2_weights, shared_l1_weights_opt, shared_l2_weights_opt, cumulative_local_expert_recv_stats, sym_buffer, sym_buffer_ptrs, rank_idx, num_max_tokens_per_rank, num_experts, num_topk, activation, activation_clamp_opt, fast_math=true) -> void`
- 结构类似 fp8_fp4 版本，但 l1_weights/l2_weights 为 kBFloat16，无 SF 参数
- mma_type 传 "bf16xbf16"
- 仅支持 SM100，调用 `sm100_bf16_mega_moe(...)`

**F-051** `register_apis(m)` 注册：`get_token_alignment_for_mega_moe`, `get_block_m_for_mega_moe`, `get_symm_buffer_size_for_mega_moe`, `fp8_fp4_mega_moe`, `bf16_mega_moe`

### 2.7 Runtime 配置 (csrc/apis/runtime.hpp)

**F-052** 文件: `csrc/apis/runtime.hpp`，命名空间 `deep_gemm::runtime`
- 包含 `jit/compiler.hpp`, `jit/device_runtime.hpp`, `jit_kernels/heuristics/runtime.hpp`

**F-053** `register_apis(m)` 注册（均为 lambda 包装）：
- `set_num_sms(new_num_sms: int)` -> void：调用 `device_runtime->set_num_sms()`
- `get_num_sms() -> int`：调用 `device_runtime->get_num_sms()`
- `set_tc_util(new_tc_util: int)` -> void：调用 `device_runtime->set_tc_util()`
- `get_tc_util() -> int`：调用 `device_runtime->get_tc_util()`
- `set_pdl(new_enable_pdl: bool)` -> void：调用 `device_runtime->set_pdl()`
- `get_pdl() -> bool`：调用 `device_runtime->get_pdl()`
- `set_ignore_compile_dims(new_value: bool)` -> void：调用 `heuristics_runtime->set_ignore_compile_dims()`
- `set_block_size_multiple_of(new_value: variant<int, tuple<int,int>>)` -> void：int 版本设置 m/n 相同值，tuple 版本分别设置
- `init(library_root_path: string, cuda_home_path_by_python: string)` -> void：调用 `Compiler::prepare_init()`, `KernelRuntime::prepare_init()`, `IncludeParser::prepare_init()`

---

## 三、C++ 模块入口 (csrc/python_api.cpp)

**F-054** 文件: `csrc/python_api.cpp`
- 包含 pybind11 和 torch 头文件
- 包含各 API 头：`apis/attention.hpp`, `apis/einsum.hpp`, `apis/hyperconnection.hpp`, `apis/gemm.hpp`, `apis/layout.hpp`, `apis/mega.hpp`, `apis/runtime.hpp`
- 宏 `TORCH_EXTENSION_NAME` 默认定义为 `_C`
- `PYBIND11_MODULE(TORCH_EXTENSION_NAME, m)` 设置模块文档为 "DeepGEMM C++ library"
- 依次调用各命名空间的 `register_apis(m)`：attention, einsum, hyperconnection, gemm, layout, mega, runtime

---

## 四、JIT 编译系统

### 4.1 DeviceRuntime (csrc/jit/device_runtime.hpp)

**F-055** 文件: `csrc/jit/device_runtime.hpp`，类 `DeviceRuntime`
- 成员变量：`num_sms: int = 0`, `tc_util: int = 0`, `enable_pdl: bool = false`, `cached_prop: shared_ptr<cudaDeviceProp>`
- 静态常量 `kCublasLtWorkspaceSize = 32 * 1024 * 1024`（32MB）
- 公共成员：`cublaslt_handle: cublasLtHandle_t`, `cublaslt_workspace: torch::Tensor`, `use_pytorch_managed_cublaslt_handle: bool`, `use_temp_cublaslt_workspace: bool`

**F-056** DeviceRuntime 构造函数：
- `use_pytorch_managed_cublaslt_handle` 由环境变量 `DG_USE_PYTORCH_CUBLASLT_HANDLE` 控制（默认 0）
- `use_temp_cublaslt_workspace` 由环境变量 `DG_USE_TEMP_CUBLASLT_WORKSPACE` 控制（默认 0）
- 非 PyTorch 管理模式下调用 `cublasLtCreate(&cublaslt_handle)`
- 非临时 workspace 模式下分配 32MB Byte Tensor 在 CUDA 上

**F-057** DeviceRuntime 析构函数：非 PyTorch 管理模式下调用 `cublasLtDestroy(cublaslt_handle)`

**F-058** DeviceRuntime 公共方法：
- `get_cublaslt_handle() -> cublasLtHandle_t`：返回 PyTorch 管理的或自管理的 handle
- `get_cublaslt_workspace() -> Tensor`：返回临时分配的或持有的 workspace
- `get_prop() -> shared_ptr<cudaDeviceProp>`：懒加载并缓存 cudaDeviceProp
- `get_arch_pair() -> pair<int,int>`：返回 (major, minor)
- `get_arch(number_only=false, support_arch_family=false) -> string`：
  - SM100 且 minor!=1：number_only 返回 "100"，support_arch_family 返回 "100f"，否则 "100a"
  - 其他：返回 `to_string(major*10+minor) + "a"`（number_only 时不加 "a"）
- `get_arch_major() -> int`：返回 prop->major
- `set_num_sms(new_num_sms: int)`：断言 0 <= new_num_sms <= multiProcessorCount
- `get_num_sms() -> int`：num_sms==0 时返回 multiProcessorCount
- `get_l2_cache_size() -> int`：返回 prop->l2CacheSize
- `set_tc_util(new_tc_util: int)`：断言 0 <= new_tc_util <= 100
- `get_tc_util() -> int`：tc_util==0 时返回 100
- `set_pdl(new_enable_pdl: bool)`, `get_pdl() -> bool`

**F-059** 全局静态变量 `device_runtime = LazyInit<DeviceRuntime>(...)`

### 4.2 Handle (csrc/jit/handle.hpp)

**F-060** 文件: `csrc/jit/handle.hpp`
- 函数 `get_driver_handle() -> void*`：懒加载 `libcuda.so.1`（通过 dlopen），静态缓存
- 宏 `DECL_LAZY_CUDA_DRIVER_FUNCTION(name)`：生成模板函数 `lazy_name(args...)`，通过 dlsym 懒加载 CUDA driver API 函数指针
- 懒加载的 CUDA Driver API：cuGetErrorName, cuGetErrorString, cuFuncSetAttribute, cuModuleLoad, cuModuleUnload, cuModuleGetFunction, cuLibraryLoadFromFile, cuLibraryUnload, cuKernelGetFunction, cuLaunchKernelEx, cuTensorMapEncodeTiled

**F-061** CUDA Runtime API 路径（CUDART_VERSION >= 12080 且定义 DG_JIT_USE_RUNTIME_API）：
- 类型别名：LibraryHandle = cudaLibrary_t, KernelHandle = cudaKernel_t, LaunchConfigHandle = cudaLaunchConfig_t, LaunchAttrHandle = cudaLaunchAttribute
- `load_kernel(cubin_path, func_name, library_opt=nullptr) -> KernelHandle`：调用 cudaLibraryLoadFromFile + cudaLibraryGetKernel
- `unload_library(library)`：调用 cudaLibraryUnload
- `construct_launch_config(kernel, stream, smem_size, grid_dim, block_dim, cluster_dim, enable_pdl) -> LaunchConfigHandle`：设置 cluster dimension 和 PDL 属性
- `launch_kernel(kernel, config, args...)`：调用 cudaLaunchKernelExC

**F-062** CUDA Driver API 路径（else 分支）：
- 类型别名：KernelHandle = CUfunction, LaunchConfigHandle = CUlaunchConfig, LaunchAttrHandle = CUlaunchAttribute
- CUDA_VERSION >= 12040 时使用 cuLibrary API（LibraryHandle = CUlibrary），否则使用 cuModule API（LibraryHandle = CUmodule）
- `load_kernel(...)`：通过 cuLibraryLoadFromFile + cuLibraryEnumerateKernels（12.4+）或 cuModuleLoad + cuModuleGetFunction 加载
- 断言 cubin 中仅包含 1 个 kernel 函数（过滤 vprintf/__instantiate_kernel/__internal/__assertfail）
- `construct_launch_config(...)` 和 `launch_kernel(...)` 使用 Driver API 等价物

### 4.3 IncludeParser (csrc/jit/include_parser.hpp)

**F-063** 文件: `csrc/jit/include_parser.hpp`，类 `IncludeParser`
- 成员：`cache: unordered_map<string, optional<string>>`
- 静态方法 `get_includes(code, file_path="") -> vector<string>`：使用正则 `#\s*include\s*[<"][^>"]+[>"]` 提取 include；仅解析 `<deep_gemm/*>` 形式的尖括号 include；非标准 include 触发 DG_HOST_UNREACHABLE
- 静态成员 `library_include_path: filesystem::path`
- 静态方法 `prepare_init(library_root_path: string)`：设置 library_include_path 为 `library_root_path / "include"`
- 方法 `get_hash_value(code: string, exclude_code: bool=true) -> string`：遍历所有 include 递归计算 hash，可选包含 code 本身 hash；最终返回 hex digest
- 方法 `get_hash_value_by_path(path) -> string`：读取文件内容，递归计算 include 依赖 hash；检测循环 include（cache 中 nullopt 表示正在处理）

**F-064** 全局静态变量 `include_parser = make_shared<IncludeParser>()`

### 4.4 Compiler (csrc/jit/compiler.hpp)

**F-065** 文件: `csrc/jit/compiler.hpp`，类 `Compiler`（抽象基类）
- 静态成员：`library_root_path`, `library_include_path`, `cuda_home`, `cuobjdump_path`（均为 filesystem::path）
- 静态方法 `prepare_init(library_root_path, cuda_home_path_by_python)`：设置上述路径，library_include_path = library_root_path / "include"，cuobjdump_path = cuda_home / "bin" / "cuobjdump"
- 成员：`signature: string`, `flags: string`, `cache_dir_path: filesystem::path`

**F-066** Compiler 构造函数：
- 断言静态路径已初始化
- cache_dir_path 默认 `$HOME/.deep_gemm`，可由环境变量 `DG_JIT_CACHE_DIR` 覆盖
- signature 默认 "unknown-compiler"
- flags 基础部分：`-std=c++{DG_JIT_CPP_STANDARD默认20} --diag-suppress=39,161,174,177,186,940 --ptxas-options=--register-usage-level=10`
- DG_JIT_DEBUG/DG_JIT_PTXAS_VERBOSE/DG_JIT_PTXAS_CHECK 时追加 `--ptxas-options=--verbose,--warn-on-local-memory-usage`
- DG_JIT_WITH_LINEINFO 时追加 `-Xcompiler -rdynamic -lineinfo`

**F-067** Compiler 方法：
- `make_tmp_dir() -> path`：返回 cache_dir_path / "tmp" 目录（通过 make_dirs 创建）
- 静态 `fsync_path(path)`：open+fsync+close
- 静态 `fsync_dir(dir_path)`：递归 fsync 所有子目录和文件，最后 fsync 目录自身
- 静态 `put(path, data)`：写入二进制文件并 fsync
- `build(name: string, code: string) -> shared_ptr<KernelRuntime>`：
  - kernel_signature = `"{name}$${signature}$${flags}$${code}"`
  - dir_path = cache_dir_path / "cache" / `"kernel.{name}.{hex_digest(signature)}"`
  - 先查 runtime cache（kernel_runtime_cache->get）
  - 未命中则编译到临时目录 tmp_dir_path（含 kernel.cubin 和可选 kernel.ptx/kernel.sass），fsync 后原子 rename 到 dir_path
  - rename 失败时（其他进程已创建）清理临时目录
  - 返回 kernel_runtime_cache->get(dir_path)
- 静态 `disassemble(cubin_path, sass_path)`：调用 cuobjdump --dump-sass
- 纯虚函数 `compile(code, dir_path, cubin_path, ptx_path=nullopt)` -> void

**F-068** 类 `NVCCCompiler final : public Compiler`
- 成员：`nvcc_path: filesystem::path`
- 私有方法 `get_nvcc_version() -> pair<int,int>`：执行 `nvcc --version`，正则提取版本号；断言 >= 12.3，< 12.9 时打印性能警告
- 构造函数：
  - nvcc_path 默认 cuda_home/"bin"/"nvcc"，可由 DG_JIT_NVCC_COMPILER 环境变量覆盖
  - signature = `"NVCC{major}.{minor}"`
  - flags 追加：`-I{include_path} --gpu-architecture=sm_{arch} --compiler-options=-fPIC,-O3,-fconcepts,-Wno-deprecated-declarations,-Wno-abi -O3 --expt-relaxed-constexpr --expt-extended-lambda`
  - arch 通过 device_runtime->get_arch(false, nvcc>=12.9) 获取
- `compile(...)` 重写：写入 kernel.cu，调用 nvcc -cubin 编译；ptx_path 有值时额外编译 PTX；DG_JIT_PTXAS_CHECK 时断言无 "Local memory used"

**F-069** 类 `NVRTCCompiler final : public Compiler`
- 构造函数：
  - 调用 nvrtcVersion 获取版本，signature = `"NVRTC{major}.{minor}"`，断言 >= 12.3
  - include_dirs 包含 library_include_path 和 cuda_home/"include"
  - NVRTC >= 12.8 时添加 `--pch` 标志（DG_JIT_DEBUG 时加 --pch-verbose=true）
  - flags 追加：include_dirs + `--gpu-architecture=sm_{arch} -default-device {pch_flags} --device-int128`
- `compile(...)` 重写：写入 kernel.cu，解析 flags 为字符串数组，调用 nvrtcCreateProgram + nvrtcCompileProgram；编译失败时打印 NVRTC log；获取 PTX/CUBIN 数据并写入文件；最后 nvrtcDestroyProgram

**F-070** 全局静态变量 `compiler = LazyInit<Compiler>(...)`：DG_JIT_USE_NVRTC 环境变量非零时使用 NVRTCCompiler，否则使用 NVCCCompiler

### 4.5 KernelRuntime (csrc/jit/kernel_runtime.hpp)

**F-071** 文件: `csrc/jit/kernel_runtime.hpp`，结构体 `LaunchArgs`
- 成员：`grid_dim: pair<int,int>`, `num_threads: int`, `smem_size: int`, `cluster_dim: int`, `enable_pdl: bool`
- 构造函数 1：`(grid_dim_x: int, num_threads: int, smem_size=0, cluster_dim=1, enable_pdl=true)` -> grid_dim={grid_dim_x, 1}
- 构造函数 2：`(grid_dim: pair<int,int>, num_threads: int, smem_size=0, cluster_dim=1, enable_pdl=true)`

**F-072** 类 `KernelRuntime final`
- 静态成员 `cuda_home: filesystem::path`
- 公共成员：`library: LibraryHandle`, `kernel: KernelHandle`
- 构造函数 `KernelRuntime(dir_path: path)`：
  - 断言 cuda_home 非空
  - cubin_path = dir_path / "kernel.cubin"
  - DG_JIT_USE_LIBRARY_ENUM_KERNELS 路径：直接 load_kernel（不需函数名）
  - 否则：调用 cuobjdump -symbols 获取符号列表，过滤非法名称（vprintf, __instantiate_kernel, __internal, __assertfail），断言仅 1 个入口函数，调用 load_kernel(cubin_path, symbol_names[0], &library)
  - DG_JIT_DEBUG/DG_JIT_PRINT_LOAD_TIME 时打印加载耗时
- 静态方法 `prepare_init(cuda_home_path_by_python)`：设置 cuda_home
- 静态方法 `check_validity(dir_path) -> bool`：检查目录存在，且 kernel.cu 和 kernel.cubin 均存在；损坏时打印错误并断言
- 析构函数：调用 unload_library(library)

**F-073** 模板类 `LaunchRuntime<Derived>`（CRTP 模式）
- 静态方法 `generate(args: const Args&) -> string`：
  - 调用 `Derived::generate_impl(args)` 生成 CUDA C++ 代码
  - 首次调用时通过 include_parser 计算 include hash 并静态缓存
  - 在代码前添加注释 `"// Includes' hash value: {include_hash}\n"`
- 静态方法 `launch(kernel_runtime: shared_ptr<KernelRuntime>, args: const Args&)`：
  - 获取当前 CUDA stream
  - 从 args.launch_args 获取 LaunchArgs，enable_pdl 被 device_runtime->get_pdl() 运行时覆盖
  - 构造 dim3 grid/block，调用 construct_launch_config
  - 调用 `Derived::launch_impl(kernel, config, args)`

### 4.6 KernelRuntimeCache (csrc/jit/cache.hpp)

**F-074** 文件: `csrc/jit/cache.hpp`，类 `KernelRuntimeCache`
- 成员：`cache: unordered_map<string, shared_ptr<KernelRuntime>>`
- 方法 `get(dir_path: path) -> shared_ptr<KernelRuntime>`：
  - 命中 cache 直接返回
  - 未命中时调用 KernelRuntime::check_validity(dir_path)，有效则创建 KernelRuntime 并存入 cache
  - 无效返回 nullptr
- 全局静态变量 `kernel_runtime_cache = make_shared<KernelRuntimeCache>()`

---

## 五、兼容性宏 (csrc/utils/compatibility.hpp)

**F-075** 文件: `csrc/utils/compatibility.hpp`
- `DG_FP8_COMPATIBLE`：PyTorch >= 2.1（TORCH_VERSION_MAJOR > 2 或 MAJOR==2 且 MINOR >= 1）
- `DG_TENSORMAP_COMPATIBLE`：CUDA Driver API >= 12.1（CUDA_VERSION >= 12010）
- `DG_CUBLAS_GET_ERROR_STRING_COMPATIBLE`：CUDA Runtime >= 11.4.2
- `DG_CUBLASLT_ADVANCED_FEATURES_COMPATIBLE`：CUDA Runtime >= 11.8

---

## 六、工具函数 (csrc/utils/layout.hpp)

**F-076** 文件: `csrc/utils/layout.hpp`
- 命名空间 `deep_gemm`
- 函数 `major_check(t: Tensor)`：断言 dim 为 2 或 3；3D 时 stride(0) == size(-2)*size(-1)；stride(-2)==1 或 stride(-1)==1
- 函数 `get_major_type_ab(t: Tensor) -> cute::UMMA::Major`：stride(-1)==1 返回 K，否则返回 MN
- 函数 `check_major_type_cd(t: Tensor)`：调用 major_check，断言 stride(-1)==1（行优先）
- 函数 `fp8_requires_k_major() -> bool`：arch_major == 9 时返回 true
- 模板函数 `get_shape<N>(t: Tensor) -> tuple<int,...>`：断言 t.is_cuda() 且 dim==N，返回 N 个 int 组成的 tuple
- 模板函数 `get_logical_shape<N>(t: Tensor)`：调用 get_shape，若 dtype == kPackedFP4 则最后一维 *= 2
- 函数 `check_ab_fp8_fp4(ab, major, arch_major) -> tuple<int,int>`：获取 (mn,k)，非 kFloat8_e4m3fn 时（即 kPackedFP4 且 arch_major==10）根据 major 调整 k*=2 或 mn*=2
- 函数 `check_grouped_ab_fp8_fp4(ab, major, arch_major) -> tuple<int,int,int>`：3D 版本，返回 (num_groups, mn, k)
- 函数 `get_default_recipe(sfa_dtype, sfb_dtype) -> tuple<int,int,int>`：
  - SM90：返回 (1, 128, 128)
  - SM100：sfb 为 kFloat 时返回 (1,128,128)（旧格式），为 kInt 时返回 (1,1,128)（1D1D 核函数）
- 函数 `check_sf_layout(sf, mn, k, gran_mn, gran_k, num_groups, tma_stride_check=false, sm90_sfb_check=false, type_check=nullopt) -> Tensor`：
  - 验证 sf dtype（kFloat 或 kInt）、维度（2 或 3）、形状（ceil_div(mn,gran_mn), ceil_div(k,gran_k/(Float?1:4))）
  - tma_stride_check 时验证 TMA 对齐和 MN-major
  - sm90_sfb_check 时验证 contiguous 或 transpose 后 contiguous

---

## 七、工具函数 (csrc/utils/math.hpp)

**F-077** 文件: `csrc/utils/math.hpp`
- 定义常量 `constexpr auto kPackedFP4 = torch::kInt8`

---

## 八、类型定义 (deep_gemm/include/deep_gemm/common/types.cuh)

**F-078** 文件: `deep_gemm/include/deep_gemm/common/types.cuh`
- 命名空间 `deep_gemm`
- `enum class MmaKind { BF16 = 0, MXFP8FP4 = 1 }`
- `constexpr int get_element_size(MmaKind)`：BF16 返回 2，MXFP8FP4 返回 1
- `enum class GemmType { Normal=0, MGroupedContiguous=1, MGroupedMasked=2, KGroupedContiguous=3, Batched=4, MGroupedContiguousWithPsumLayout=5, KGroupedContiguousWithPsumLayout=6 }`
- `constexpr bool is_m_grouped_contiguous(GemmType)`：MGroupedContiguous 和 MGroupedContiguousWithPsumLayout 返回 true
- `constexpr bool is_k_grouped_contiguous(GemmType)`：KGroupedContiguous 和 KGroupedContiguousWithPsumLayout 返回 true
- `enum class KernelType { Kernel1D1D=0, Kernel1D2D=1, KernelNoSF=2 }`

---

## 九、启发式运行时 (csrc/jit_kernels/heuristics/runtime.hpp)

**F-079** 文件: `csrc/jit_kernels/heuristics/runtime.hpp`，类 `HeuristicsRuntime`
- 静态常量 `kLegacyMKAlignmentForContiguousLayout = 128`
- 成员：`ignore_compile_dims: bool = false`, `block_m_multiple_of: int = 1`, `block_n_multiple_of: int = 1`, `mk_alignment_for_contiguous_layout: int = 128`
- 方法：
  - `set/get_ignore_compile_dims()`
  - `set/get_block_size_multiple_of(m, n)` / `get_block_m/n_multiple_of()`
  - `set_mk_alignment_for_contiguous_layout(new_value)`, `get_mk_alignment_for_contiguous_layout() -> int`
  - 静态 `get_theoretical_mk_alignment_for_contiguous_layout(expected_m: optional<int>) -> int`：
    - SM100 以外返回 128
    - SM100：block_m 从 224 开始以 32 为步长递减，确保 block_m - 32 >= expected_m，最小 32
- 全局静态 `heuristics_runtime = LazyInit<HeuristicsRuntime>(...)`

---

## 十、MegaMoE 布局常量 (deep_gemm/include/deep_gemm/layout/mega_moe.cuh)

**F-080** 文件: `deep_gemm/include/deep_gemm/layout/mega_moe.cuh`
- `static constexpr int kNumCandidateBlockMs = 7`
- `static constexpr int kCandidateBlockM[7] = {8, 16, 32, 64, 96, 128, 192}`
- `static constexpr int kLCMCandidateBlockM = 384`
- `constexpr T get_num_sf_ring_tokens(T num_ring_tokens, T block_m)`（模板函数）
- `constexpr T get_num_max_shared_sf_tokens(const T& num_max_tokens_per_rank)`（模板函数）

---

## 十一、MegaMoE 启发式配置 (csrc/jit_kernels/heuristics/mega_moe.hpp)

**F-081** 文件: `csrc/jit_kernels/heuristics/mega_moe.hpp`
- 结构体 `MegaMoEConfig`：包含 block_m/n/k, load_block_m/n, store_block_m, sf_block_m/n, num_ring_tokens, num_sf_ring_tokens, swizzle_acts_mode, swizzle_weights_mode, num_stages, smem_size, num_dispatch/non_epilogue/epilogue_threads, num_bytes_per_pull
- 函数 `parse_mma_kind(mma_type_str: string) -> MmaKind`："bf16xbf16" 返回 BF16，"fp8xfp4" 返回 MXFP8FP4
- 函数 `get_num_mma_elem_bytes(mma_kind) -> int`：BF16=2, MXFP8FP4=1
- 函数 `is_mma_with_sf(mma_kind) -> bool`：MXFP8FP4 返回 true
- 函数 `get_block_config_for_mega_moe(num_ranks, num_experts, num_max_tokens_per_rank, num_topk, num_tokens, mma_kind) -> tuple<int,int,int,int,int>`：返回 (cluster_size, block_m, store_block_m, block_k, num_epilogue_warpgroups)；基于 num_expected_tokens_per_expert 分档选择 block_m（16/32/64/96/128/192），block_k 为 128 或 256，cluster_size=2

---

## 十二、Python 包结构（deep_gemm/ 目录）

### 12.1 mega 子模块 (deep_gemm/mega/__init__.py)

**F-082** 文件: `deep_gemm/mega/__init__.py`
- 导入 `torch`, `types`, `warnings`, `Tuple/Optional/Union` from typing, `align` from ..utils.math
- 尝试导入 `torch.distributed._symmetric_memory as symm_mem` 和 `torch.distributed as dist`，失败时打印警告

**F-083** 类 `SymmBuffer`
- `__init__(self, group: dist.ProcessGroup, num_experts: int, num_max_tokens_per_rank: int, num_topk: int, hidden: int, intermediate_hidden: int, num_shared_experts: int = 0, mma_type: str = 'fp8xfp4', activation: str = 'swiglu')`：
  - 断言 activation == 'swiglu'
  - 存储所有参数为实例属性
  - 调用 `_C.get_symm_buffer_size_for_mega_moe(...)` 获取 (num_bytes, slice_input_buffers)
  - 单 rank 用 `torch.empty`，多 rank 用 `symm_mem.empty` 分配 int8 缓冲区
  - 单 rank handle 为 SimpleNamespace(buffer_ptrs=[self.buffer.data_ptr()])，多 rank 通过 `symm_mem.rendezvous` 获取
  - buffer.zero_()，group.barrier()，torch.cuda.synchronize()
  - 调用 slice_input_buffers(self.buffer) 创建 12 个 tensor 视图：(x, x_sf, topk_idx, topk_weights, shared_l1_acts, shared_l1_acts_sf, shared_l2_acts, shared_l2_acts_sf, l1_acts, l1_acts_sf, l2_acts, l2_acts_sf)
- `destroy(self)`：将 handle, buffer, group, x, x_sf 置为 None

**F-084** 函数 `get_symm_buffer_for_mega_moe(group, num_experts, num_max_tokens_per_rank, num_topk, hidden, intermediate_hidden, num_shared_experts=0, use_fp8_dispatch: Union[bool,None]=None, mma_type='fp8xfp4', activation='swiglu') -> SymmBuffer`
- 使用 `align()` 将 num_max_tokens_per_rank 对齐到 `_C.get_token_alignment_for_mega_moe()` 返回值
- use_fp8_dispatch 非 None 时做向后兼容检查，发出 DeprecationWarning
- 返回 SymmBuffer 实例

**F-085** 函数 `_interleave_weights(t: torch.Tensor, gran: int = 8) -> torch.Tensor`
- 将权重沿 n 维度按 gran 分组，交错排列 gate 和 up 部分（[gate:0..7, up:0..7, gate:8..15, up:8..15,...]）
- 支持 2D 和 3D 张量，2D 时先 unsqueeze(0) 后 squeeze

**F-086** 函数 `_transpose_sf_for_utccp(sf: torch.Tensor) -> torch.Tensor`
- 断言 sf.dtype == torch.int 且 dim 为 2 或 3，mn % 128 == 0
- 执行 reshape(-1, 4, 32, packed_sf_k).transpose(2,3).reshape(num_groups, mn, packed_sf_k) 变换

**F-087** 函数 `transform_weights_for_mega_moe(l1_weights, l2_weights, activation='swiglu') -> Tuple`
- FP8 模式（tuple 输入）：l1 权重 interleaved，l1 SF 先 interleaved 再 _transpose_sf_for_utccp；l2 权重不变，l2 SF 仅 _transpose_sf_for_utccp
- BF16 模式（tensor 输入）：l1 interleaved，l2 不变
- 返回 (l1_transformed, l2_transformed)

**F-088** 函数 `fp8_fp4_mega_moe(y, l1_weights, l2_weights, sym_buffer, shared_l1_weights=None, shared_l2_weights=None, cumulative_local_expert_recv_stats=None, recipe=(1,1,32), activation='swiglu', activation_clamp=None, fast_math=True)`
- 调用 `_C.fp8_fp4_mega_moe(...)`，传入 sym_buffer.buffer, sym_buffer.handle.buffer_ptrs, sym_buffer.group.rank() 等参数

**F-089** 函数 `bf16_mega_moe(y, l1_weights, l2_weights, sym_buffer, shared_l1_weights=None, shared_l2_weights=None, cumulative_local_expert_recv_stats=None, activation='swiglu', activation_clamp=None, fast_math=True)`
- 调用 `_C.bf16_mega_moe(...)`，传入类似参数但无 SF 和 recipe

### 12.2 testing 子模块

**F-090** 文件: `deep_gemm/testing/__init__.py`
- 导入 bench, numeric, utils 子模块，并通过 `from .bench import *`, `from .numeric import *`, `from .utils import *` 导出所有公共符号

**F-091** 文件: `deep_gemm/testing/bench.py`
- 函数 `bench(fn, num_warmups: int = 5, num_tests: int = 10, high_precision: bool = False) -> float`：
  - 使用 256MB int 张量 flush L2 cache
  - warmup 执行 num_warmups 次 fn()
  - high_precision 时先执行一次 8192x8192 FP32 matmul 消除 CPU launch overhead
  - 使用 CUDA Event 计时，执行 num_tests 次，返回平均耗时（秒）
- 类 `empty_suppress`：空上下文管理器（__enter__/__exit__ 无操作）
- 类 `suppress_stdout_stderr`：上下文管理器，重定向 stdout/stderr 到 /dev/null，退出时恢复
- 函数 `bench_kineto(fn, kernel_names, num_tests: int = 30, suppress_kineto_output: bool = False, trace_path: str = None, flush_l2: bool = True, with_multiple_kernels: bool = False, barrier: Optional[Callable] = None)`：
  - kernel_names 为 str 或 tuple
  - 环境变量 DG_USE_NVIDIA_TOOLS 非零时跳过 profile，返回 (1,)*len 或 1
  - 使用 torch.profiler 进行 CUDA activity profiling（schedule: wait=0, warmup=1, active=1, repeat=1）
  - 可选 flush L2（8GB memset）和 barrier（torch.cuda._sleep + barrier()）
  - 解析 profiler key_averages 表格提取 kernel 时间（支持 ms/us 单位）
  - trace_path 非 None 时导出 chrome trace
  - 返回单个 kernel 时间或 tuple

**F-092** 文件: `deep_gemm/testing/numeric.py`
- 函数 `calc_diff(x: torch.Tensor, y: torch.Tensor) -> float`：计算 `1 - 2*<x,y>/(||x||^2+||y||^2)`（余弦距离），double 精度；全零返回 0.0
- 函数 `count_bytes(*tensors) -> int`：递归计算所有 tensor（含 tuple/list 嵌套）的总字节数
- 函数 `assert_bitwise_equal(x: torch.Tensor, y: torch.Tensor, label: str = '')`：逐字节比较；不匹配时提供详细错误信息（num_mismatch、第一个不匹配位置、坐标、值）

**F-093** 文件: `deep_gemm/testing/utils.py`
- 函数 `get_arch_major() -> int`：返回 torch.cuda.get_device_capability()[0]
- 装饰器 `test_filter(condition: Callable)`：condition() 返回 True 时执行 func，否则打印跳过信息
- 装饰器 `ignore_env(name: str, condition: Callable)`：condition() 返回 True 时临时移除环境变量 name 后执行 func，执行后恢复

### 12.3 utils 子模块

**F-094** 文件: `deep_gemm/utils/__init__.py`
- 导入 math 和 layout 子模块
- 通过 `from .layout import *` 和 `from .math import *` 导出
- 从 `.dist` 导入 `init_dist`, `uneven_all_gather`

**F-095** 文件: `deep_gemm/utils/dist.py`
- 模块级变量 `_local_rank = None`
- 函数 `init_dist(local_rank: int, num_local_ranks: int) -> Tuple[int, int, dist.ProcessGroup]`：
  - 从环境变量获取 MASTER_ADDR（默认127.0.0.1）、MASTER_PORT（默认8361）、WORLD_SIZE（默认1）、RANK（默认0）
  - 设置全局 _local_rank
  - 调用 dist.init_process_group（backend='nccl'，tcp init_method），若支持 device_id 参数则传入
  - 设置 default device 为 cuda，set_device(local_rank)
  - 返回 (rank, world_size, new_group)
- 函数 `uneven_all_gather(tensor: torch.Tensor, dim: int = 0, group: dist.ProcessGroup = None) -> torch.Tensor`：
  - 交换各 rank 的 dim 大小，pad 到 max_dim_size，all_gather 后裁剪 padding，cat 返回
- 函数 `dist_print(s: str = '', once_in_node: bool = False) -> None`：
  - 断言 _local_rank 已设置；once_in_node 时仅 local_rank==0 打印；之后 dist.barrier()

**F-096** 文件: `deep_gemm/utils/layout.py`
- try 块中从 `.._C` 导入：`get_tma_aligned_size`, `get_mn_major_tma_aligned_tensor`, `get_mn_major_tma_aligned_packed_ue8m0_tensor`, `get_k_grouped_mn_major_tma_aligned_packed_ue8m0_tensor`（ImportError 时跳过，兼容旧 CUDA）
- 无条件从 `.._C` 导入：`set_mk_alignment_for_contiguous_layout`, `get_mk_alignment_for_contiguous_layout`, `get_theoretical_mk_alignment_for_contiguous_layout`
- 别名：`get_m_alignment_for_contiguous_layout = get_mk_alignment_for_contiguous_layout`, `get_k_alignment_for_contiguous_layout = get_mk_alignment_for_contiguous_layout`

**F-097** 文件: `deep_gemm/utils/math.py`
- 函数 `ceil_div(x: int, y: int) -> int`：返回 `(x + y - 1) // y`
- 函数 `align(x: int, y: int) -> int`：返回 `ceil_div(x, y) * y`
- 函数 `ceil_to_ue8m0(x: torch.Tensor) -> torch::Tensor`：通过 bit 操作计算 UE8M0 指数
- 函数 `pack_ue8m0_to_int(x: torch.Tensor) -> torch.Tensor`：将 4 个 UE8M0 byte 打包为一个 int32
- 函数 `per_token_cast_to_fp8(x, use_ue8m0, gran_k=128, use_packed_ue8m0=False) -> Tuple[Tensor, Tensor]`：per-token 按 gran_k 分组计算 abs max 作为 scale，量化到 FP8；可选 packed UE8M0 scale
- 函数 `per_channel_cast_to_fp8(x, use_ue8m0, gran_k=128) -> Tuple[Tensor, Tensor]`：per-channel（沿 M 维度分块）量化
- 函数 `per_block_cast_to_fp8(x, use_ue8m0, gran_k=128) -> Tuple[Tensor, Tensor]`：per-block（M 和 K 均按 gran_k 分块）量化
- 函数 `per_custom_dims_cast_to_fp8(x, dims: Tuple, use_ue8m0) -> Tuple[Tensor, Tensor]`：自定义维度量化
- 函数 `_quantize_to_fp4_e2m1(x) -> Tensor`：E2M1 FP4 量化（码点 {0,0.5,1,1.5,2,3,4,6}，含符号位）
- 函数 `per_token_cast_to_fp4(x, use_ue8m0, gran_k=128, use_packed_ue8m0=False) -> Tuple[Tensor, Tensor]`：per-token FP4 量化，每 2 个 E2M1 码打包为 1 byte（nibble packing）
- 函数 `transpose_packed_fp4(a: Tensor) -> Tensor`：对 packed FP4 矩阵（int8）执行转置
- 函数 `_dequantize_from_fp4_e2m1(x) -> Tensor`：FP4 E2M1 反量化
- 函数 `unpack_ue8m0_from_int(packed_sf) -> Tensor`：将打包的 int32 scale 解包为 float
- 函数 `cast_back_from_fp4(packed, sf, gran_k=128, use_packed_ue8m0=False) -> Tensor`：FP4 反量化回 float
- 函数 `cast_back_from_fp8(x_fp8, sf, gran_k=128, use_packed_ue8m0=False) -> Tensor`：FP8 反量化回 float

### 12.4 legacy 子模块（A100 Triton 核函数）

**F-098** 文件: `deep_gemm/legacy/__init__.py`
- 从 `.m_grouped_gemm`, `.a_fused_m_grouped_gemm`, `.a_fused_k_grouped_gemm`, `.b_fused_k_grouped_gemm` 导入所有公共符号（通配符导入）

**F-099** 文件: `deep_gemm/legacy/tune_options.py`
- 从 triton 导入 Config，从 `.._C` 导入 `get_mk_alignment_for_contiguous_layout`
- 函数 `get_config_smem_size(config: Config, elem_bytes: int = 2) -> int`：计算 shared memory 大小 `(BLOCK_M + BLOCK_N) * BLOCK_K * elem_bytes * num_stages`
- `_gemm_configs` 列表：9 个 Triton Config，BLOCK_M ∈ {32,64,128}, BLOCK_N ∈ {64,128,256}, BLOCK_K ∈ {64,128}, GROUP_SIZE_M=8, num_stages ∈ {2,3,4}, num_warps ∈ {4,8}
- 过滤 _gemm_configs：smem <= 166912（A100 shared memory 限制），BLOCK_M 和 BLOCK_K <= get_mk_alignment_for_contiguous_layout()
- `get_m_grouped_gemm_configs`：lambda，返回按 BLOCK_M <= alignment 过滤的配置列表
- `get_k_grouped_gemm_configs`：lambda，返回按 BLOCK_K <= alignment 过滤的配置列表

**F-100** 文件: `deep_gemm/legacy/m_grouped_gemm.py`
- 导入 torch, triton, triton.language as tl, Tuple from typing
- Triton JIT 核函数 `m_grouped_bf16_gemm_contiguous_tl_impl`（装饰器 `@triton.autotune(configs=get_m_grouped_gemm_configs(), key=[])` + `@triton.jit`）：
  - 参数：a_ptr, b_ptr, d_ptr, m_indices_ptr, M, N(tl.constexpr), K(tl.constexpr), BLOCK_SIZE_M/N/K(tl.constexpr), GROUP_SIZE_M(tl.constexpr), IS_B_K_MAJOR(tl.constexpr)
  - 使用 grouped GEMM 的 program ID 计算（GROUP_SIZE_M 分组 swizzle）
  - 通过 m_indices_ptr[pid_m * BLOCK_SIZE_M] 获取 batch_id，负值表示空 token（写入零）
  - IS_B_K_MAJOR 控制 B 的步长计算（K-major 或 N-major）
  - 内积循环累加，结果转换为 d 的 dtype 后写回
- 函数 `m_grouped_bf16_gemm_nt_contiguous_tl(a: Tensor, b: Tensor, d: Tensor, m_indices: Tensor) -> None`：
  - 断言 a/b/d contiguous，a/b/d dtype=bfloat16，m_indices dtype=int32
  - 形状：a(M,K), b(B,N,K) 或 (B,K,N)（B K-major 或 N-major），d(M,N)
  - m_indices.numel() == M，M % alignment == 0
  - grid = lambda META: (cdiv(M, BLOCK_M) * cdiv(N, BLOCK_N),)
  - 调用 triton kernel，IS_B_K_MAJOR = b.is_contiguous()
- 函数 `m_grouped_bf16_gemm_nn_contiguous_tl(a, b, d, m_indices) -> None`：调用 nt 版本但传入 `b.mT`
