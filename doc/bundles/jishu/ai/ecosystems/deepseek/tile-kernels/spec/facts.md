---
type: spec
title: "TileKernels 项目事实清单"
---

# TileKernels 项目事实清单

> R阶段（事实收集）产出。所有事实均为源码直接观察，不含推断。
> 源码根路径：`d:\spaces\SpecWeave\external\libs\ai\deepseek-ai\TileKernels`

---

## F-001: 项目元数据与依赖

**文件**: `pyproject.toml`
- 构建系统：`setuptools` + `wheel` + `setuptools-scm>=8`，build-backend为`setuptools.build_meta`
- 版本管理：`setuptools-scm`自动生成版本，写入`tile_kernels/_version.py`；`dynamic = ["version"]`
- 项目名称：`tile_kernels`
- 描述：`"Tilelang-based kernels."`
- README：`"README.md"`
- 许可证：`MIT`
- 作者：Chenhao Xu, Xiangwen Wang, Huanqi Cao, Rui Tian, Weilin Zhao, Kuai Yu, Chenggang Zhao（邮箱@deepseek.com）
- Python版本要求：`>=3.10`
- 分类器：Development Status 3 - Alpha, 支持Python 3.10/3.11/3.12, 科学/AI主题
- 核心运行时依赖：
  - `torch>=2.10`
  - `tilelang>=0.1.9`
- 可选开发依赖组（`[project.optional-dependencies]`）：
  - `dev`：`setuptools`, `wheel`, `setuptools-scm>=8`, `pytest`, `pytest-xdist`, `pytest-repeat`
- 包发现：`where=["."]`, `include=["tile_kernels*"]`
- 项目URL：`https://github.com/deepseek-ai/TileKernels`
- Ruff配置：line-length=150，启用Q000（flake8-quotes单引号）

## F-002: 包级公共API导出

**文件**: `tile_kernels/__init__.py`
- 子模块导出：`config`, `engram`, `mhc`, `modeling`, `moe`, `quant`, `transpose`, `torch`, `testing`
- 函数导出：`get_num_sms`, `get_device_num_sms`, `set_num_sms`（来自`.config`）

---

## F-003: 配置模块

**文件**: `tile_kernels/config.py`
- 模块级变量：`_num_sms: int = 0`（全局SM数量覆盖值）
- `get_device_num_sms() -> int`：使用`@functools.lru_cache(maxsize=None)`装饰，通过`torch.cuda.get_device_properties(torch.cuda.current_device()).multi_processor_count`获取当前GPU的SM数量
- `set_num_sms(num_sms: int) -> None`：设置全局SM数量，断言`0 < num_sms <= get_device_num_sms()`
- `get_num_sms() -> int`：返回`_num_sms`（若为0则返回`get_device_num_sms()`）
- `get_max_smem_per_sm() -> int`：使用`@functools.lru_cache(maxsize=None)`装饰，返回`torch.cuda.get_device_properties(...).shared_memory_per_multiprocessor`（每个SM的最大共享内存大小）

## F-004: 工具函数

**文件**: `tile_kernels/utils.py`
- `ceil_div(x: int, y: int) -> int`：返回`(x + y - 1) // y`
- `align(x: int, y: int) -> int`：返回`ceil_div(x, y) * y`
- `is_power_of_two(x: int) -> bool`：返回`x > 0 and (x & (x - 1)) == 0`

---

## F-005: 量化类型定义

**文件**: `tile_kernels/quant/types.py`
- `QuantTensor = tuple[torch.Tensor, torch.Tensor]`：量化张量类型别名，即`(data, scale_factors)`二元组

## F-006: 量化公共模块

**文件**: `tile_kernels/quant/common.py`

### 数据类
- `@dataclass(frozen=True) class BaseCastConfig`:
  - 字段：`torch_dtype: torch.dtype = torch.float8_e4m3fn`, `sf_block: tuple[int,int] = (1,1)`, `use_tma_aligned_col_major_sf: bool = False`, `use_packed_ue8m0: bool = False`
  - 属性：`dtype -> T.dtype`（torch.int8映射为T.float4_e2m1fn），`sf_torch_dtype -> torch.dtype`（packed_ue8m0时为torch.uint8，否则torch.float32），`sf_dtype -> T.dtype`
- `@dataclass(frozen=True) class CastInputConfig(BaseCastConfig)`：新增字段`with_sf: bool = True`
- `@dataclass(frozen=True) class CastOutputConfig(BaseCastConfig)`：新增字段`round_sf: bool = False`, `custom_clamp_min_value: Optional[float] = None`；属性`clamp_min_value -> float`（e4m3为1e-4，e2m1为T.max_value(dtype)*2^-126）

### 函数
- `get_best_vectorize_size(dtype: T.dtype) -> int`：根据GPU compute capability返回16或32除以dtype.bytes
- `get_cast_input_and_config(x, sf_block) -> tuple[torch.Tensor, torch.Tensor, CastInputConfig]`：解析输入（普通tensor或QuantTensor），返回(data, sf, config)
- `get_cast_output_config(fmt, sf_block, ...) -> CastOutputConfig`：fmt支持`'e5m6'/'e4m3'/'e2m1'`，映射到torch.uint32/torch.float8_e4m3fn/torch.int8
- `get_logical_hidden(hidden: int, dtype: torch.dtype) -> int`：int8(FP4)时返回hidden*2，否则返回hidden
- `get_physical_hidden(hidden: int, dtype: torch.dtype) -> int`：int8(FP4)时返回hidden//2，否则返回hidden
- `get_sf_shape(shape, config) -> tuple[int,int]`：计算缩放因子shape
- `alloc_scaling_factors(shape, out_config, device) -> torch.Tensor`：分配缩放因子张量
- `cast_epilogue(out_sf, num_tokens, hidden, config) -> torch.Tensor`：kernel启动后的sf后处理
- `unpack_from_e2m1fn_x2(x: torch.Tensor, out_dtype=torch.float32) -> torch.Tensor`：将packed FP4(int8/uint8)解码为float32；FP4布局为s(1)|e(2)|m(1)，bias=1

### TileLang宏
- `@T.macro get_sf_and_inv(amax, out_config)`：计算sf和sf_inv，支持round_sf（2的幂次舍入）
- `@T.macro load_sf(tensor, m_idx, k_idx, config)`：根据config从sf tensor加载（支持packed_ue8m0和col-major）
- `@T.macro transform_sf(sf, config) -> T.float32`：sf转换为float32
- `@T.macro store_sf(tensor, sf, m_idx, k_idx, config)`：存储sf到tensor

## F-007: 量化模块公共导出

**文件**: `tile_kernels/quant/__init__.py`
- 导出函数：
  - `swiglu_forward_and_per_channel_cast_and_transpose`
  - `per_channel_cast`
  - `per_channel_cast_fused`
  - `per_channel_cast_and_transpose`
  - `swiglu_forward_and_per_token_cast`
  - `swiglu_backward_and_per_token_cast`
  - `unpack_from_e2m1fn_x2`
  - `per_token_cast`, `per_token_cast_with_precomputed_sf`, `per_token_cast_with_sf_only`
  - `per_block_cast`, `per_block_cast_with_precomputed_sf`, `per_block_cast_with_sf_only`
  - `cast_back`, `per_token_cast_back`
  - `per_block_cast_lossless`

---

## F-008: 每Token量化Kernel

**文件**: `tile_kernels/quant/per_token_cast_kernel.py`
- JIT kernel工厂：`get_per_token_cast_kernel(...)`（@tilelang.jit装饰）
- Python wrapper：
  - `per_token_cast(x: torch.Tensor, fmt: str, num_per_channels: int, x_block_size=None, use_tma_aligned_col_major_sf=False, round_sf=False, use_packed_ue8m0=False) -> QuantTensor`
  - `per_token_cast_with_sf_only(...) -> torch.Tensor`：仅返回sf
  - `per_token_cast_with_precomputed_sf(x, fmt, num_per_channels, sf, ...) -> torch.Tensor`：使用预计算sf
  - `per_token_cast_impl(...)`：内部实现，支持`sf_only`参数
- fmt支持：`'e4m3'`(FP8 E4M3)、`'e2m1'`(FP4 E2M1)

## F-009: 每Block量化Kernel

**文件**: `tile_kernels/quant/per_block_cast_kernel.py`
- JIT kernel工厂：`get_per_block_cast_kernel(...)`
- Python wrapper：
  - `per_block_cast(x: torch.Tensor, fmt: str, block_size: tuple[int,int], use_tma_aligned_col_major_sf=False, round_sf=False, use_packed_ue8m0=False) -> QuantTensor`
  - `per_block_cast_with_sf_only(...) -> torch.Tensor`
  - `per_block_cast_with_precomputed_sf(x, fmt, block_size, sf, ...) -> torch.Tensor`
  - `per_block_cast_impl(...)`：内部实现

## F-010: 每Channel量化Kernel

**文件**: `tile_kernels/quant/per_channel_cast_kernel.py`
- `per_channel_cast(x: torch.Tensor, fmt: str, num_per_tokens: int, round_sf: bool = False) -> QuantTensor`
- 约束：fmt必须为`'e4m3'`；num_tokens%128==0；hidden%64==0；num_per_tokens必须为128
- 内部调用`per_channel_cast_fused`

## F-011: 每Channel量化融合Kernel

**文件**: `tile_kernels/quant/per_channel_cast_fused_kernel.py`
- 内部宏：`transform_token_idx(with_expand, idx, token_idx, x)`
- JIT kernel工厂：`get_per_channel_cast_fused_kernel(...)`
- Python wrapper：
  - `per_channel_cast_fused(x: Union[torch.Tensor, QuantTensor], fmt: str, num_per_tokens: int, round_sf=False, num_per_channels=None, pos_to_token=None) -> QuantTensor`
  - 支持FP8输入反量化重缩放（当x为QuantTensor时）
  - 支持pos_to_token token扩展/gather
  - 约束：fmt必须为`'e4m3'`；num_per_tokens必须为128；pos_to_token时输出token数必须16对齐，否则128对齐

## F-012: 每Channel量化+转置Kernel

**文件**: `tile_kernels/quant/per_channel_cast_and_transpose_kernel.py`
- JIT kernel工厂：`get_per_channel_cast_and_transpose_kernel(...)`
- Python wrapper：
  - `per_channel_cast_and_transpose(x: torch.Tensor, fmt: str, num_per_tokens: int, round_sf: bool = False) -> QuantTensor`

## F-013: 反量化Kernel

**文件**: `tile_kernels/quant/cast_back_kernel.py`
- JIT kernel工厂：`get_cast_back_kernel(...)`
- Python wrapper：
  - `cast_back(x: QuantTensor, fmt: str, x_block_size: tuple[int,int], x_special_fmt: Optional[str] = None) -> torch.Tensor`
    - fmt: `'bf16'`或`'fp32'`
    - x_special_fmt: 可选`'e5m6'`
  - `per_token_cast_back(x: QuantTensor, fmt: str, num_per_channels: int, x_special_fmt=None) -> torch.Tensor`
    - 等价于`cast_back(x, fmt, (1, num_per_channels), x_special_fmt=x_special_fmt)`

## F-014: E5M6格式反量化Kernel

**文件**: `tile_kernels/quant/cast_back_e5m6_kernel.py`
- 内部函数：`e5m6_to_float(...)`
- JIT kernel工厂：`get_cast_back_e5m6_kernel(...)`
- Python wrapper：
  - `cast_back_e5m6(x: QuantTensor, fmt: str, x_block_size: tuple[int,int]) -> torch.Tensor`
  - x.data为uint8（packed E5M6），shape为(num_tokens, hidden*3//2)

## F-015: 无损重量化Kernel（FP4→FP8）

**文件**: `tile_kernels/quant/per_block_cast_lossless_kernel.py`
- JIT kernel工厂：`get_per_block_cast_lossless_kernel(...)`
- Python wrapper：
  - `per_block_cast_lossless(x: QuantTensor, fmt: str, x_block_size: tuple[int,int], out_block_size: tuple[int,int], use_tma_aligned_col_major_sf=False, round_sf=False, use_packed_ue8m0=False) -> QuantTensor`
  - 约束：fmt必须为`'e4m3'`；输入必须为e2m1(FP4)格式；执行FP4→FP8无损重量化

## F-016: E5M6每Token量化Kernel

**文件**: `tile_kernels/quant/per_token_cast_to_e5m6_kernel.py`
- 内部宏/函数：`get_sf_and_inv_e5m6(amax, out_config)`, `float_to_e5m6(...)`
- JIT kernel工厂：`get_per_token_cast_to_e5m6_kernel(...)`
- Python wrapper：
  - `per_token_cast_to_e5m6(x: torch.Tensor, num_per_channels: int, use_tma_aligned_col_major_sf=False, round_sf=False, use_packed_ue8m0=False) -> QuantTensor`
  - E5M6格式：1位符号+5位指数+6位尾数（类FP16截断），bias=15；8个值打包为3个uint32（96位），输出为uint8，shape为(num_tokens, hidden*3//2)
  - 约束：num_per_channels必须等于hidden；hidden%8==0

## F-017: SwiGLU前向+每Token量化融合Kernel

**文件**: `tile_kernels/quant/swiglu_forward_and_per_token_cast_kernel.py`
- JIT kernel工厂：`get_swiglu_forward_and_per_token_cast_kernel(...)`
- Python wrapper：
  - `swiglu_forward_and_per_token_cast(x: torch.Tensor, fmt: str, num_per_channels: int, pos_to_token_topk=None, topk_weights=None, pos_to_expert=None, use_tma_aligned_col_major_sf=False, round_sf=False, use_packed_ue8m0=False, swiglu_clamp_value=None, clamped_count=None, sf_clamp_min=None) -> QuantTensor`
  - 融合SwiGLU激活（silu(x_left)*x_right）+ 按路由权重缩放 + FP8量化
  - 约束：fmt必须为`'e4m3'`

## F-018: SwiGLU反向+每Token量化融合Kernel

**文件**: `tile_kernels/quant/swiglu_backward_and_per_token_cast_kernel.py`
- JIT kernel工厂：`get_swiglu_backward_and_per_token_cast_kernel(...)`
- Python wrapper：
  - `swiglu_backward_and_per_token_cast(x: QuantTensor, grad_out: torch.Tensor, weight: torch.Tensor, pos_to_token_topk: torch.Tensor, token_topk_to_pos: torch.Tensor, num_per_channels: int, round_sf=False, swiglu_clamp_value=None) -> tuple[torch.Tensor, QuantTensor, torch.Tensor, torch.Tensor]`
  - 返回：`(out_bf16, (x_grad_fp8, x_grad_fp8_sf), x_grad_bf16, weight_grad)`
  - 约束：num_per_channels必须为32或128；输入x为FP8格式

## F-019: SwiGLU前向+每Channel量化+转置融合Kernel

**文件**: `tile_kernels/quant/swiglu_forward_and_per_channel_cast_and_transpose_kernel.py`
- JIT kernel工厂：`get_swiglu_forward_and_per_channel_cast_and_transpose_kernel(...)`
- Python wrapper：
  - `swiglu_forward_and_per_channel_cast_and_transpose(x: torch.Tensor, fmt: str, num_per_tokens: int, round_sf=False, without_transpose=False, swiglu_clamp_value=None) -> QuantTensor`
  - 约束：fmt必须为`'e4m3'`；x必须为bfloat16；num_tokens%128==0；hidden%128==0；num_per_tokens为32或128
  - `without_transpose=True`时输出保持(num_tokens, hidden)布局而非转置

---

## F-020: MoE模块公共导出

**文件**: `tile_kernels/moe/__init__.py`
- 导出函数：
  - `get_fused_mapping`, `reduce_fused`, `expand_to_fused`, `expand_to_fused_with_sf`
  - `inplace_unique_group_indices`, `aux_fi`, `group_count`, `mask_indices_by_tp`
  - `normalize_weight`, `top2_sum_gate`, `topk_gate`, `topk_sum_and_topk_group_idx`

## F-021: MoE评分函数

**文件**: `tile_kernels/moe/scoring.py`
- `class ScoringFunc(IntEnum)`：枚举值`SIGMOID=0`, `SQRTSOFTPLUS=1`, `SOFTMAX=2`, `IDENTITY=3`
  - `__str__(self)`返回小写名称
  - `from_str(cls, label: str)`类方法，从字符串构造
- `@T.macro softplus(x: T.Ref)`：TileLang宏实现softplus，threshold=20（x>threshold时直接返回x）

## F-022: MoE公共宏

**文件**: `tile_kernels/moe/common.py`
- `@T.macro get_topk_group_idx(scores_shared, topk_group_idx_shared, num_groups, num_experts_per_group, num_topk_groups, num_topk_sum, num_vectorize_for_grouped_expert)`：
  - warp内规约topk group选择
  - 使用warp shuffle进行warp级reduce
  - 支持num_topk_sum为1或2（top1或top2 sum）

## F-023: TopK Gate Kernel

**文件**: `tile_kernels/moe/topk_gate_kernel.py`
- JIT kernel工厂：`get_topk_gate_kernel(num_experts: int, num_topk: int)`
- Python wrapper：
  - `topk_gate(scores: torch.Tensor, num_topk: int) -> torch.Tensor`
  - 输入：scores shape (num_tokens, num_experts), float32
  - 输出：topk_idx shape (num_tokens, num_topk), int64
  - 特性：稳定排序（ties时返回较小索引），输出contiguous

## F-024: TopK组求和+组选择Kernel

**文件**: `tile_kernels/moe/topk_sum_and_topk_group_idx_kernel.py`
- JIT kernel工厂：`get_topk_sum_and_topk_group_idx_kernel(...)`
- Python wrapper：
  - `topk_sum_and_topk_group_idx(scores: torch.Tensor, num_topk_sum: int, num_topk_groups: int) -> torch.Tensor`
  - 输入：scores shape (num_tokens, num_groups, num_experts_per_group), float32
  - 输出：group indices shape (num_tokens, num_topk_groups), int64
  - 约束：num_topk_sum仅支持1和2

## F-025: Top2-Sum Gate完整路由Kernel

**文件**: `tile_kernels/moe/top2_sum_gate_kernel.py`
- 内部函数：`warp_reduce_sum(x: T.Ref)`：warp级求和规约
- JIT kernel工厂：`get_top2_sum_gate_kernel(...)`
- Python wrapper：
  - `top2_sum_gate(logits: torch.Tensor, bias: torch.Tensor, num_topk: int, num_topk_groups: int, num_groups: int, use_shared_as_routed: bool, num_shared_experts: int, routed_scaling_factor: float, ep_rank: int, num_ep_ranks: int, tp_rank: int, num_tp_ranks: int, scoring_func: str, mask: Optional[Tensor]=None, fix_routing_mask: Optional[Tensor]=None, to_physical_map: Optional[Tensor]=None, logical_count: Optional[Tensor]=None, unmapped_topk_idx: Optional[Tensor]=None) -> tuple[Tensor, Tensor]`
  - 输入logits shape (num_tokens, num_routed_experts), float32
  - 输出：(topk_idx, topk_weights)，shape分别为(num_tokens, num_physical_topk)的int64和float32
  - 支持三种评分函数：sigmoid/sqrtsoftplus/softmax
  - 支持shared expert追加、EP/TP masking、logical→physical expert映射、固定路由mask

## F-026: 融合映射构建Kernel

**文件**: `tile_kernels/moe/get_fused_mapping_kernel.py`
- 内部宏：`divide_task(length, num_tasks, task_id, start, end)`：任务划分
- JIT kernel工厂：`get_get_fused_mapping_kernel(...)`
- Python wrapper：
  - `get_fused_mapping(topk_idx: torch.Tensor, num_experts: int, num_expanded_tokens: int, alignment: int, force_no_sync: bool=False) -> tuple[...]`
  - 返回8元组：`(pos_to_expert, pos_to_token, pos_to_token_topk, token_topk_to_pos, expert_start, expert_end, num_tokens_per_expert, num_tokens_per_expert_list)`
  - 当num_expanded_tokens=0且force_no_sync=False时自动估算并做host sync裁剪

## F-027: Expand-to-Fused Kernel

**文件**: `tile_kernels/moe/expand_to_fused_kernel.py`
- JIT kernel工厂：`get_expand_to_fused_kernel(...)`
- Python wrapper：
  - `expand_to_fused(x: torch.Tensor, token_topk_to_pos: torch.Tensor, pos_to_expert: torch.Tensor) -> torch.Tensor`
    - 输入x: (num_tokens, hidden)，输出: (num_expanded_tokens, hidden)
  - `expand_to_fused_with_sf(x: QuantTensor, num_per_channels: int, token_topk_to_pos: torch.Tensor, pos_to_expert: torch.Tensor, use_tma_aligned_col_major_sf: bool=False) -> tuple[Tensor, Tensor]`
    - 同时扩展activation和sf因子

## F-028: Reduce-Fused Kernel

**文件**: `tile_kernels/moe/reduce_fused_kernel.py`
- JIT kernel工厂：`get_reduce_fused_kernel(...)`
- Python wrapper：
  - `reduce_fused(x: Union[torch.Tensor, QuantTensor], topk_weights: Optional[Tensor], token_topk_to_pos: Tensor, fp8_format: str='', sf: Optional[Tensor]=None, out: Optional[Tensor]=None) -> torch.Tensor`
  - 输入：expanded tensor (num_expanded_tokens, hidden) 或 QuantTensor
  - 输出：reduced tensor (num_tokens, hidden)
  - 支持FP8输出（fp8_format='e4m3'）和可选标量sf缩放
  - 约束：hidden%256==0

## F-029: 辅助频率指示器Kernel

**文件**: `tile_kernels/moe/aux_fi_kernel.py`
- JIT kernel工厂：`get_aux_fi_kernel(num_topk, num_experts, num_sms)`
- Python wrapper：
  - `aux_fi(topk_idx: torch.Tensor, num_experts: int, num_aux_topk: int) -> torch.Tensor`
  - 计算`f_i[e] = count[e] * num_experts / (num_tokens * num_aux_topk)`
  - 输出：float32 tensor (num_experts,)

## F-030: Group Count Kernel

**文件**: `tile_kernels/moe/group_count_kernel.py`
- JIT kernel工厂：`get_group_count_kernel(num_topk, num_groups, num_sms)`
- Python wrapper：
  - `group_count(group_idx: torch.Tensor, num_groups: int) -> torch.Tensor`
  - 输出：int32 tensor (num_groups,)，统计每组token数

## F-031: TP Mask Kernel

**文件**: `tile_kernels/moe/mask_indices_by_tp_kernel.py`
- JIT kernel工厂：`get_mask_indices_by_tp_kernel(num_topk, dtype)`
- Python wrapper：
  - `mask_indices_by_tp(indices: torch.Tensor, n: int, num_ep_ranks: int, tp_rank: int, num_tp_ranks: int) -> torch.Tensor`
  - 非本TP rank的expert索引设为-1，本地索引重映射

## F-032: 权重归一化Kernel

**文件**: `tile_kernels/moe/normalize_weight_kernel.py`
- JIT kernel工厂：`get_normalize_weight_kernel(num_topk)`
- Python wrapper：
  - `normalize_weight(topk_weights: torch.Tensor) -> tuple[Tensor, Tensor]`
  - 返回：(denominator, normalized_weights)，shape分别为(num_tokens,)和(num_tokens, num_topk)
  - 约束：输入为float32

## F-033: 原地去重Group索引Kernel

**文件**: `tile_kernels/moe/inplace_unique_group_indices_kernel.py`
- JIT kernel工厂：`get_inplace_unique_group_indices_kernel(num_topk, num_groups_aligned, num_sms)`
- Python wrapper：
  - `inplace_unique_group_indices(group_indices: torch.Tensor, num_groups: int) -> None`
  - 原地修改：每行重复出现的group索引（非首次）设为-1
  - 约束：num_groups<=128

---

## F-034: MHC模块（空__init__.py）

**文件**: `tile_kernels/mhc/__init__.py`
- 空文件（无内容），MHC kernel函数不通过包级__init__导出，通过modeling层封装使用

## F-035: MHC Expand Kernel

**文件**: `tile_kernels/mhc/expand_kernel.py`
- JIT kernel：
  - `expand_to_mhc_fwd_tl(hidden: int, mhc_mult: int) -> JITKernel`：前向kernel，blk_n=32, blk_h=128，将(n,h)复制为(n,mhc,h)
  - `expand_to_mhc_bwd_tl(hidden: int, mhc_mult: int) -> JITKernel`：反向kernel，对mhc维度求和归约

## F-036: MHC Head Compute Mix Kernel

**文件**: `tile_kernels/mhc/head_compute_mix_kernel.py`
- Pass配置：`TL_DISABLE_WARP_SPECIALIZED: True`
- JIT kernel：
  - `_mhc_head_compute_mix_fwd(mhc_mult: int, mhc_pre_eps: float, token_block_size: int) -> JITKernel`
    - 计算：`output = sigmoid(input * scale + base) + eps`
  - `_mhc_head_compute_mix_bwd(mhc_mult: int, token_block_size: int, num_sms: int) -> JITKernel`
    - 使用`T.alloc_reducer`做梯度partial sum归约

## F-037: MHC Norm-Fn Kernel

**文件**: `tile_kernels/mhc/norm_fn_kernel.py`
- Pass配置：`TL_DISABLE_WGMMA: True`
- JIT kernel：
  - `_mhc_fn_normw_merge_fwd(m, n, dtype=T.float32)`：逐元素`out = fn * normw`
  - `_mhc_fn_normw_merge_bwd(m, n, dtype=T.float32)`：反向，累加fn_grad和normw_grad
  - `_mhc_pre_norm_fn_fwd_mul(mhc_mult3, n_rms_group, rms_group_size, token_block=32, hidden_block=256)`：RMSNorm+GEMM前向matmul部分
  - `_mhc_pre_norm_fn_fwd_norm(...)`：RMSNorm归一化部分
  - `_mhc_pre_norm_fn_bwd_norm(...)`：归一化反向
  - `_mhc_pre_norm_fn_bwd_mul(...)`：matmul反向
- Python函数：
  - `round_to_tf32(x: torch.Tensor) -> torch.Tensor`：`(x.view(torch.int32) + 0x1000).view(torch.float32)`，将float32舍入到tf32精度
- 约束：mhc_mult3 <= 32；rms_group_size % hidden_block == 0

## F-038: MHC Post Kernel

**文件**: `tile_kernels/mhc/post_kernel.py`
- JIT kernel：
  - `_mhc_post_fwd(mhc: int, hidden: int, n_thr=128, h_blk=1024)`：后处理前向
  - `_mhc_post_bwd(mhc: int, hidden: int, n_thr=128, h_blk=256)`：后处理反向
- Python wrapper：
  - `mhc_post_fwd(x, residual, post_layer_mix, comb_res_mix, out=None) -> Tensor`
    - 输入x: (S, T, hidden) bf16; residual: (S, T, mhc, hidden) bf16; post_layer_mix: (S, T, mhc, 1) fp32; comb_res_mix: (S, T, mhc, mhc) fp32
  - `mhc_post_bwd(x, residual, post_layer_mix, comb_res_mix, d_o, fuse_grad_acc=True) -> tuple[Tensor, Tensor, Tensor, Tensor]`
    - 返回(d_x, d_residual, d_post_layer_mix, d_comb_res_mix)
    - 当fuse_grad_acc=True时，将d_residual存入`residual.untyped_storage().grad_from_mhc_post`用于梯度累加融合

## F-039: MHC Pre-Apply-Mix Kernel

**文件**: `tile_kernels/mhc/pre_apply_mix_kernel.py`
- JIT kernel：
  - `_mhc_pre_apply_mix_fwd(mhc, h)`：前向，加权求和`out = sum(x * mix, dim=-2)`
  - `_mhc_pre_apply_mix_bwd(mhc, h)`（out_idx=[4]）：反向，支持fused grad acc

## F-040: MHC Pre-Big-Fuse Kernel（推理融合）

**文件**: `tile_kernels/mhc/pre_big_fuse_kernel.py`
- JIT kernel：
  - `_mhc_pre_big_fuse(...)`：推理模式下融合norm_fn + split_mixes + sinkhorn + apply_mix的大融合kernel

## F-041: MHC Pre-Split-Mixes Kernel

**文件**: `tile_kernels/mhc/pre_split_mixes_kernel.py`
- Pass配置：`TL_DISABLE_WARP_SPECIALIZED: True`
- JIT kernel：
  - `_mhc_pre_split_mixes_fwd(mhc_mult, mhc_post_mult_value, mhc_pre_eps, token_block_size=32)`
  - `_mhc_pre_split_mixes_bwd(mhc_mult, mhc_post_mult_value, token_block_size=32, num_sms)`
- 计算：将input_mixes按scale+base线性变换后sigmoid，分割为pre_layer_mix, post_layer_mix, comb_res_mix

## F-042: MHC Sinkhorn Kernel

**文件**: `tile_kernels/mhc/sinkhorn_kernel.py`
- Pass配置：`TL_DISABLE_WARP_SPECIALIZED: True`
- JIT kernel：
  - `_mhc_sinkhorn_fwd(hidden_size, token_block, repeat, eps)`：Sinkhorn归一化前向（迭代行列归一化）
  - `_mhc_sinkhorn_bwd(hidden_size, token_block, repeat, eps)`：Sinkhorn归一化反向

## F-043: MHC多层重计算Kernel

**文件**: `tile_kernels/mhc/multilayer_recompute_kernel.py`
- Pass配置：`TL_DISABLE_WARP_SPECIALIZED: True`, `TL_PTXAS_REGISTER_USAGE_LEVEL: 10`, `TL_DISABLE_VECTORIZE_256: True`
- 辅助函数：`_make_ptr_tables_batched(tensor_lists, device) -> list[Tensor]`：构建批处理指针表（pinned memory→GPU）
- JIT kernel：`_mhc_multilayer_recompute_kernel(mhc_mult, hidden, num_layers, num_post, n_thr=64, h_blk=2048)`
- Python wrapper：
  - `mhc_multilayer_recompute(initial_residual, pre_mix_list, layer_output_list, post_mix_list, comb_mix_list, layer_input_list, residual_list) -> None`
  - 原地重计算多层MHC residual，使用指针表批处理
  - 约束：num_post == num_layers-1 或 num_post == num_layers

---

## F-044: Engram模块公共导出

**文件**: `tile_kernels/engram/__init__.py`
- 导出函数：`fused_weight`, `engram_gate_fwd`, `engram_gate_bwd`, `grad_w_reduce`, `engram_hash`

## F-045: Engram Fused Weight Kernel

**文件**: `tile_kernels/engram/engram_fused_weight_kernel.py`
- Pass配置：`TL_DISABLE_WARP_SPECIALIZED: True`
- JIT kernel：`get_engram_fused_weight_kernel(hidden_size: int, hc_mult: int)`
  - 逐元素bf16×bf16→fp32乘法：`weight_fused = weight_hidden * weight_embed`
  - threads=32, vec_size=8, blk_d=256
- Python wrapper：
  - `fused_weight(weight_hidden: Tensor, weight_embed: Tensor) -> Tensor`
  - 输入：(hc_mult, hidden_size) bf16 × 2；输出：(hc_mult, hidden_size) fp32

## F-046: Engram Gate Kernel

**文件**: `tile_kernels/engram/engram_gate_kernel.py`
- JIT kernel工厂：
  - `get_engram_gate_fwd_kernel(...)`：前向kernel
  - `get_engram_gate_bwd_kernel(...)`：反向kernel
- Python wrapper：
  - `engram_gate_fwd(hidden_states, k, v, weight_fused, eps, clamp_value, save_for_backward=True) -> tuple[output, dot, gate_score, rstd_x, rstd_k]`
    - 计算：`gate = sigmoid(signed_sqrt(dot(RMSNorm(x,wh), RMSNorm(k,we)) * scalar)); output = hidden_states + gate * v`
    - 其中`signed_sqrt(x) = sign(x)*sqrt(|x|)`, `scalar = 1/sqrt(hidden_size)`
    - hidden_states/k: (num_tokens, hc_mult, hidden_size) bf16; v: (num_tokens, hidden_size) bf16
    - weight_fused: (hc_mult, hidden_size) fp32
  - `engram_gate_bwd(grad_out, hidden_states, k, v, weight_fused, dot, gate_score, rstd_x, rstd_k, clamp_value) -> tuple[grad_x, grad_k, grad_v, grad_w_partial]`
    - grad_w_partial shape: (num_persistent_blocks, hc_mult, hidden_size)，需进一步reduce

## F-047: Engram梯度W归约Kernel

**文件**: `tile_kernels/engram/engram_grad_w_reduce_kernel.py`
- JIT kernel工厂：`get_engram_grad_w_reduce_kernel(...)`
- Python wrapper：
  - `grad_w_reduce(grad_w_partial, weight_hidden, weight_embed, grad_weight_hidden, grad_weight_embed) -> None`
  - 原地归约partial梯度并融合权重乘法，累积到grad_weight张量
  - grad_w_partial: (num_persistent_blocks, hc_mult, hidden_size) fp32
  - grad_weight_hidden/embed: (hc_mult, hidden_size) fp32，原地修改

## F-048: Engram Hash Kernel

**文件**: `tile_kernels/engram/engram_hash_kernel.py`
- JIT kernel工厂：`get_engram_hash_kernel(max_ngram_size, num_ngram_layers, num_embed_table_per_ngram)`
- Python wrapper：
  - `engram_hash(ngram_token_ids, multipliers, vocab_sizes, offsets) -> Tensor`
  - ngram_token_ids: (num_tokens, max_ngram_size) int32
  - multipliers: (num_ngram_layers, max_ngram_size) int64
  - vocab_sizes: (num_ngram_layers, max_ngram_size-1, num_embed_table_per_ngram) int32
  - offsets: (num_ngram_layers, (max_ngram_size-1)*num_embed_table_per_ngram) int32
  - 输出：(num_ngram_layers, num_tokens, (max_ngram_size-1)*num_embed_table_per_ngram) int32
  - 计算：XOR hash → mod vocab_size → + offsets

---

## F-049: Transpose模块公共导出

**文件**: `tile_kernels/transpose/__init__.py`
- 导出：`transpose`, `batched_transpose`（来自`.batched_transpose_kernel`）

## F-050: 批量转置Kernel

**文件**: `tile_kernels/transpose/batched_transpose_kernel.py`
- 辅助函数：`create_loop_layout_fn(block_x: int, num_threads: int=256)`：创建循环布局函数（用于shared memory写回优化）
- JIT kernel（`pass_configs={TL_DISABLE_WARP_SPECIALIZED: True}`）：
  - `get_batched_transpose_kernel(shape_x_mod_128: int, shape_y_mod_128: int, dtype: T.dtype)`
  - 约束：shape_x_mod_128和shape_y_mod_128均为0或64
  - block_x/block_y: 128或64（取决于mod128值）；block_k=4; num_threads=256
  - 使用shared memory padding (block_y, block_x+block_k)减少bank conflict
  - 使用swizzle布局写入shared memory
- Python wrapper：
  - `transpose(x: torch.Tensor) -> torch.Tensor`：2D tensor转置，输入(M,N)且维度可被64整除，输出(N,M)
  - `batched_transpose(x: torch.Tensor) -> torch.Tensor`：3D tensor转置，输入(B,M,N)，输出(B,N,M)
  - 约束：M%64==0, N%64==0, stride(-2)%4==0, stride(-1)==1
  - 环境变量`TK_PRINT_KERNEL_SOURCE=1`时打印kernel源码

---

## F-051: Modeling包导出

**文件**: `tile_kernels/modeling/__init__.py`
- 子模块导出：`engram`, `mhc`

## F-052: Modeling Engram模块

**文件**: `tile_kernels/modeling/engram/__init__.py`
- 导出：`engram_gate`, `EngramGateFn`

## F-053: EngramGateFn（autograd.Function）

**文件**: `tile_kernels/modeling/engram/engram_gate.py`
- `class EngramGateFn(torch.autograd.Function)`：
  - `forward(ctx, hidden_states, k, v, weight_hidden, weight_embed, clamp_value, eps)`：
    - hidden_states: (*, hc_mult, hidden_size) bf16; k: (*, hc_mult, hidden_size) bf16; v: (*, hidden_size) bf16
    - weight_hidden/weight_embed: (hc_mult, hidden_size) bf16（RMSNorm权重）
    - 内部调用fused_weight合并权重，再调用engram_gate_fwd
    - 支持main_grad属性：若权重有main_grad属性，梯度累积到main_grad（原地），返回None
  - `backward(ctx, grad_output)`：
    - 调用engram_gate_bwd计算梯度
    - 使用grad_w_reduce归约权重梯度
    - 使用`getattr(weight, 'main_grad', None)`检测fp32梯度缓冲区
- `engram_gate = EngramGateFn.apply`：函数式API

## F-054: Modeling MHC模块

**文件**: `tile_kernels/modeling/mhc/__init__.py`
- 导出：`expand_from_embedding`, `mhc_head`, `mhc_pre`（来自`.functional`）

## F-055: Modeling MHC Ops导出

**文件**: `tile_kernels/modeling/mhc/ops/__init__.py`
- 导出：`expand_to_mhc`, `mhc_head_compute_mix`, `mhc_multilayer_recompute`, `mhc_pre_norm_fn`, `mhc_post`, `mhc_post_bwd`, `mhc_post_fwd`, `mhc_pre_apply_mix`, `mhc_pre_big_fuse`, `mhc_pre_split_mixes`, `sinkhorn_normalize`

## F-056: MHC Functional高层API

**文件**: `tile_kernels/modeling/mhc/functional.py`
- `expand_from_embedding(x: Tensor, mhc_mult: int=4) -> Tensor`：将(...,H)扩展为(...,mhc_mult,H)，调用expand_to_mhc
- `mhc_pre(residual, fn, scale, base, *, norm_weight=None, norm_eps=1e-6, mhc_mult=4, post_mult_value=1.0, pre_eps=1e-6, sinkhorn_eps=1e-6, sinkhorn_repeat=10, n_splits=16) -> tuple[Tensor, tuple[Tensor,Tensor]]`：
  - 一个子层（attention/FFN）的MHC预处理
  - 推理模式（`not torch.is_grad_enabled()`）使用mhc_pre_big_fuse融合kernel
  - 训练模式：mhc_pre_norm_fn → mhc_pre_split_mixes → sinkhorn_normalize → mhc_pre_apply_mix
  - 返回(layer_input, (post_mix, comb_mix))
  - residual: (..., mhc_mult, hidden_size); fn: [mhc_mult*(mhc_mult+2), mhc_mult*hidden_size] fp32; scale: [3] fp32; base: [mhc_mult*(mhc_mult+2)] fp32
- `mhc_head(residual, fn, scale, base, *, norm_weight=None, norm_eps=1e-6, mhc_mult=4, pre_eps=1e-6, n_splits=16) -> Tensor`：
  - LM Head的MHC处理，组合pre_norm_fn + head_compute_mix + pre_apply_mix
  - fn shape为[mhc_mult, mhc_mult*hidden_size]，内部pad到[mhc_mult*(mhc_mult+2), ...]
  - 返回layer_input: (..., hidden_size)

## F-057: ExpandToMHC autograd.Function

**文件**: `tile_kernels/modeling/mhc/ops/expand.py`
- `class ExpandToMHCFn(torch.autograd.Function)`：
  - `forward(ctx, hidden, mhc_mult, out)`：hidden:(...,H)→(...,mhc_mult,H)，调用expand_to_mhc_fwd_tl
  - `backward(ctx, out_grad)`：mhc维度求和归约，调用expand_to_mhc_bwd_tl
- `expand_to_mhc(hidden, mhc_mult, out=None) -> Tensor`

## F-058: MHCHeadComputeMix autograd.Function

**文件**: `tile_kernels/modeling/mhc/ops/head_compute_mix.py`
- `class MHCHeadComputeMix(torch.autograd.Function)`：
  - `forward(ctx, input_mix, mhc_scale, mhc_base, mhc_pre_eps)`：token_block_size=32
  - `backward(ctx, output_mix_grad)`：使用num_sms做partial sum归约scale和base梯度
- `mhc_head_compute_mix(input_mix, mhc_scale, mhc_base, mhc_pre_eps) -> Tensor`

## F-059: MHC Multilayer Recompute导出

**文件**: `tile_kernels/modeling/mhc/ops/multilayer_recompute.py`
- 直接re-export：`mhc_multilayer_recompute`（来自mhc kernel层）
- `__all__ = ['mhc_multilayer_recompute']`

## F-060: MHCPreNormFn autograd.Function

**文件**: `tile_kernels/modeling/mhc/ops/norm_fn.py`
- `class _MHCFnNormwMerge(torch.autograd.Function)`：融合fn和normw的乘法（前向和反向），支持main_grad
- `class MHCPreNormFn(torch.autograd.Function)`：
  - `forward(ctx, x, fn, norm_eps, fuse_grad_acc, n_splits)`：
    - x必须为bf16，fn必须为fp32
    - TileLang实现n_splits强制为1（注释说明不支持split-K，建议用DeepGEMM）
    - 调用_mhc_pre_norm_fn_fwd_mul + _mhc_pre_norm_fn_fwd_norm
    - 对fn调用round_to_tf32
  - `backward(ctx, out_grad)`：
    - fuse_grad_acc=True时使用`x.untyped_storage().grad_from_mhc_post`做梯度融合累加
- `mhc_pre_norm_fn(residual, mhc_fn, mhc_norm_weight, mhc_norm_eps, fuse_grad_acc=True, n_splits=16) -> Tensor`：
  - 若mhc_norm_weight不为None，先通过_MHCFnNormwMerge.apply合并权重

## F-061: MHCPost autograd.Function

**文件**: `tile_kernels/modeling/mhc/ops/post.py`
- `class MHCPost(torch.autograd.Function)`：
  - `forward(ctx, x, residual, post_layer_mix, comb_res_mix, out)`：调用mhc_post_fwd
  - `backward(ctx, d_o)`：调用mhc_post_bwd
- `mhc_post(x, residual, post_layer_mix, comb_res_mix, out=None) -> Tensor`

## F-062: MHCPreApplyMix autograd.Function

**文件**: `tile_kernels/modeling/mhc/ops/pre_apply_mix.py`
- `class MHCPreApplyMix(torch.autograd.Function)`：
  - `forward(ctx, x, mix, out)`：mix最后一维必须为1
  - `backward(ctx, o_grad)`：检测`x.untyped_storage().grad_from_mhc_post`做fused grad acc
- `mhc_pre_apply_mix(x, mix, out=None) -> Tensor`

## F-063: MHC Pre-Big-Fuse推理函数

**文件**: `tile_kernels/modeling/mhc/ops/pre_big_fuse.py`
- `mhc_pre_big_fuse(residual, fn, mhc_scale, mhc_base, rms_eps, mhc_pre_eps, mhc_sinkhorn_eps, mhc_post_mult_value, sinkhorn_repeat, n_splits=16) -> tuple[Tensor, Tensor, Tensor]`
- 约束：residual为bf16，fn/scale/base为fp32；TileLang实现n_splits强制为1
- 返回(post_mix, comb_mix, layer_input)

## F-064: MHCPreSplitMixes autograd.Function

**文件**: `tile_kernels/modeling/mhc/ops/pre_split_mixes.py`
- `class MHCPreSplitMixes(torch.autograd.Function)`：
  - 支持main_grad（scale/base的fp32梯度缓冲区）
  - forward使用token_block_size=32
  - backward使用num_sms做partial sum归约
- `mhc_pre_split_mixes(input_mixes, mhc_scale, mhc_base, mhc_mult, mhc_post_mult_value, mhc_pre_eps) -> tuple[pre_layer_mix, post_layer_mix, comb_res_mix]`

## F-065: Sinkhorn Normalize autograd.Function

**文件**: `tile_kernels/modeling/mhc/ops/sinkhorn.py`
- `class _SinkhornNormalize(torch.autograd.Function)`：
  - `forward(ctx, x, repeat, eps)`：调用_mhc_sinkhorn_fwd，fwd token_block=1，bwd token_block=32
  - `backward(ctx, grad_output)`：调用_mhc_sinkhorn_bwd
- `sinkhorn_normalize(x, repeat=10, eps=1e-6) -> Tensor`：输入需contiguous，view为(-1, m, m)后reshape回原形状

---

## F-066: Torch参考实现模块导出

**文件**: `tile_kernels/torch/__init__.py`
- 量化相关：`cast`, `cast_back`, `cast_to_e5m6`, `cast_back_from_e5m6`
- MoE相关：`expand_to_fused`, `expand_to_fused_with_sf`, `reduce_fused`, `stable_topk`, `topk_sum_and_topk_group_idx`, `top2_sum_gate`, `inplace_unique_group_indices`, `aux_fi`, `group_count`, `mask_indices_by_tp`, `normalize_weight`
- MHC相关：`expand_to_mhc_ref`, `mhc_head_compute_mix_ref`, `mhc_post_ref`, `mhc_pre_apply_mix_ref`, `mhc_pre_norm_fn_ref`, `mhc_pre_split_mixes_ref`, `sinkhorn_normalize_ref`
- SwiGLU相关：`swiglu_forward`, `swiglu_backward`
- 融合cast：`per_channel_cast_fused`

## F-067: Torch量化参考实现

**文件**: `tile_kernels/torch/cast.py`
- `right_shift_unsigned(x, shift)`：CUDA torch uint32位运算的无符号右移workaround
- `get_min_clamp_val(dtype)`：int8→6.0*2^-126, float8_e4m3fn→0.0001
- `get_max_quant_val(dtype)`：int8→6.0, float8_e4m3fn→448.0
- `transform_sf(sf) -> Tensor`：int32 sf→float32转换（位操作：(uint8<<23).view(float32)）
- `cast_back(x: QuantTensor, fmt: str, block_size=(32,32)) -> Tensor`：反量化参考实现，支持bf16/fp32输出
- `cast(x, fmt, block_size=(32,32), sf=None, x_block_size=None, round_sf=False, use_tma_aligned_col_major_sf=False, use_packed_ue8m0=False) -> Union[Tensor, QuantTensor]`：
  - 量化参考实现，支持e2m1(FP4)/e4m3(FP8)
  - FP4打包：两个4位值打包为一个int8（低4位+高4位）
  - RTNE（round to nearest, ties to even）舍入
- `convert_to_e2m1_bits(quant_tensor, max_quant_val, device)`：FP4位转换参考，E8→E2指数转换，RTNE舍入

## F-068: Torch E5M6参考实现

**文件**: `tile_kernels/torch/cast_e5m6.py`
- `right_shift_unsigned(x, shift)`：无符号右移
- `transform_sf(sf) -> Tensor`：int32→float32 sf转换
- `_make_col_major(sf, tma_alignment) -> Tensor`：TMA对齐的列主序sf视图
- `_float32_to_fp16_rtz_bits(x) -> Tensor`：float32→fp16 RTZ（round toward zero）位转换
- `_cast_to_e5m6(x) -> Tensor`：float32→E5M6打包，8个E5M6值→3个uint32（w0,w1,w2位打包）
- `_cast_back_from_e5m6(x) -> Tensor`：E5M6解包→fp16→float32
- `cast_to_e5m6(x, num_per_channels, use_tma_aligned_col_major_sf=False, round_sf=False, use_packed_ue8m0=False) -> tuple[Tensor, Tensor]`：E5M6量化参考
- `cast_back_from_e5m6(x, fmt, x_block_size) -> Tensor`：E5M6反量化参考
- E5M6常量：max_normal=65024.0, min_normal=2^-14, max_subnormal=2^-14*63/64, min_subnormal=2^-20

## F-069: Torch Engram参考实现

**文件**: `tile_kernels/torch/engram.py`
- `make_offsets(vocab_sizes: Tensor) -> Tensor`：从vocab_sizes计算exclusive prefix-sum offsets
- `engram_hash_ref(ngram_token_ids, multipliers, vocab_sizes, offsets) -> Tensor`：Engram hash纯PyTorch参考，使用bitwise_xor
- `engram_gate_ref(hidden_states, k, v, weight_hidden, weight_embed, clamp_value, eps, save_for_backward=False) -> Tensor|tuple`：
  - 向量化参考实现，支持autograd
  - 计算公式同kernel层
  - scalar = hidden_size^-0.5

## F-070: Torch Expand-to-Fused参考实现

**文件**: `tile_kernels/torch/expand_to_fused.py`
- `expand_to_fused(x, token_topk_to_pos, pos_to_expert) -> Tensor`：使用indexing实现扩展
- `expand_to_fused_with_sf(x: QuantTensor, num_per_channels, token_topk_to_pos, pos_to_expert, use_tma_aligned_col_major_sf=False) -> tuple[Tensor, Tensor]`：同时扩展data和sf

## F-071: Torch MHC参考实现

**文件**: `tile_kernels/torch/mhc.py`
- `expand_to_mhc_ref(hidden, mhc_mult) -> Tensor`：`hidden.unsqueeze(-2).expand(...).contiguous()`
- `sinkhorn_normalize_ref(x, repeat=10, eps=1e-6) -> Tensor`：纯PyTorch Sinkhorn迭代
- `mhc_head_compute_mix_ref(input_mix, mhc_scale, mhc_base, mhc_pre_eps) -> Tensor`：`sigmoid(input*scale+base)+eps`
- `mhc_pre_split_mixes_ref(input_mixes, mhc_scale, mhc_base, mhc_mult, mhc_post_mult_value, mhc_pre_eps) -> tuple`：纯PyTorch分割
- `mhc_pre_apply_mix_ref(x, mix) -> Tensor`：`(x*mix).sum(-2).bfloat16()`
- `mhc_post_ref(x, residual, post_layer_mix, comb_res_mix) -> Tensor`：使用einsum计算
- `mhc_pre_norm_fn_ref(residual, mhc_fn, mhc_norm_weight, mhc_norm_eps) -> Tensor`：einsum+RMSNorm参考

## F-072: Torch MoE参考实现

**文件**: `tile_kernels/torch/moe.py`
- `aux_fi(topk_idx, num_experts, num_aux_topk) -> Tensor`：`count[e]*num_experts/(num_tokens*num_aux_topk)`
- `group_count(group_idx, num_groups) -> Tensor`：scatter_add_统计每组数量
- `mask_indices_by_tp(indices, n, num_ep_ranks, tp_rank, num_tp_ranks) -> Tensor`：非本地expert设为-1
- `normalize_weight(topk_weights) -> tuple[Tensor, Tensor]`：按token归一化weights和为1
- `inplace_unique_group_indices(group_indices, num_groups) -> None`：稳定排序后原地去重

## F-073: Torch Per-Channel Cast Fused参考实现

**文件**: `tile_kernels/torch/per_channel_cast_fused.py`
- `per_channel_cast_fused(x, num_per_tokens, num_per_channels, round_sf, pos_to_token) -> QuantTensor`：
  - 支持pos_to_token gather扩展
  - 内部调用tile_kernels.torch.cast，block_size=(num_per_tokens, 1)

## F-074: Torch Reduce-Fused参考实现

**文件**: `tile_kernels/torch/reduce_fused.py`
- `@torch.compile elementwise_fma(a, b, c) -> Tensor`：显式FMA模式`a*b+c`供torch.compile捕获
- `reduce_fused(x, topk_weights, token_topk_to_pos, fp8_format='', sf=None) -> Tensor`：循环topk slots加权求和归约

## F-075: Torch SwiGLU参考实现

**文件**: `tile_kernels/torch/swiglu.py`
- `@torch.compile elementwise_fma(a, b, c) -> Tensor`：FMA模式
- `swiglu_forward(x, pos_to_token_topk=None, topk_weights=None, swiglu_clamp_value=None, clamped_count=None) -> Tensor`：
  - 计算`silu(x_left)*x_right`，可选clamp和topk权重缩放
  - x: (num_expanded_tokens, hidden*2)，输出fp32: (num_expanded_tokens, hidden)
- `swiglu_backward(x: QuantTensor, grad_out, weight, pos_to_token_topk, token_topk_to_pos, num_per_channels, swiglu_clamp_value=None) -> tuple[Tensor, Tensor, Tensor]`：
  - FP8输入反量化→SwiGLU反向→返回(act_out, x_grad_full, weight_grad)
  - 支持clamp梯度零化

## F-076: Torch TopK参考实现

**文件**: `tile_kernels/torch/topk.py`
- `stable_topk(scores, num_topk) -> Tensor`：稳定降序排序后取前num_topk个索引
- `topk_sum_and_topk_group_idx(scores, num_group_sum_topk, num_topk_groups) -> Tensor`：组内topk sum后选topk组
- `top2_sum_gate(logits, bias, num_topk, num_topk_groups, num_groups, use_shared_as_routed, num_shared_experts, routed_scaling_factor, ep_rank, num_ep_ranks, tp_rank, num_tp_ranks, scoring_func, mask=None, fix_routing_mask=None, to_physical_map=None, logical_count=None, unmapped_topk_idx=None) -> tuple[Tensor, Tensor]`：
  - 完整top2-sum路由参考实现
  - 支持sigmoid/sqrtsoftplus/softmax三种评分函数
  - 支持shared expert、EP/TP masking、logical→physical映射、固定路由

---

## F-077: Testing模块导出

**文件**: `tile_kernels/testing/__init__.py`
- 子模块：`bench`, `numeric`, `generator`, `quant`
- 导出：`clear_unused_sf`（来自`.quant`）

## F-078: Bench工具

**文件**: `tile_kernels/testing/bench.py`
- `class empty_suppress`：空上下文管理器
- `class suppress_stdout_stderr`：抑制stdout/stderr输出的上下文管理器（使用os.dup2重定向）
- `print_average_perf(latency_list, bandwidth_list, relative_speed_list)`：打印几何平均性能（us, GB/s, speedup）
- `dtype_to_str(dtype) -> str`：dtype映射：fp32→'fp32', bf16→'bf16', float8_e4m3fn→'e4m3', int8→'e2m1'
- `make_param_key(params) -> str`：生成benchmark记录的短key
- `make_param_id(params) -> str`：生成benchmark参数ID字符串
- 短名映射：num_ep_ranks→'ep', num_experts→'experts', use_tma_aligned_col_major_sf→'col', use_packed_ue8m0→'ue8m0', round_sf→'round'

## F-079: 测试数据生成器

**文件**: `tile_kernels/testing/generator.py`
- `generate_num_tokens(alignment=1, is_benchmark=False) -> list[int]`：生成测试token数[4001, 8001]，TK_FULL_TEST时加0
- `generate_hidden_sizes(align=64) -> list[int]`：生成hidden size列表[576, 2048, 2560, 3072, 4096, 6144, 7168]
- `generate_num_sms() -> list[int]`：生成SM数列表
- `generate_moe_params(is_benchmark=False) -> Iterable[dict]`：生成MoE参数组合
- `@torch.compile generate_topk_idx(params) -> Tensor`：生成随机topk_idx
- E5M6特殊值：`_E5M6_SPECIAL_VALUES = (2^-20, 2^-14*63/64, 2^-14)`
- `generate_e5m6_inputs(num_tokens, hidden, dtype) -> Iterable[tuple[Tensor, bool]]`：生成E5M6测试输入（随机+特殊值）
- `generate_rand_float(shape) -> Tensor`：生成随机float32 tensor（随机指数范围），NaN/Inf替换并clamp

## F-080: 数值验证工具

**文件**: `tile_kernels/testing/numeric.py`
- `assert_equal(x, y, check_dtype=True, check_shape=True, check_stride=True)`：断言两个tensor完全相等（dtype/shape/stride/device/值）
- `calc_diff(x, y) -> Tensor`：计算余弦相似度差异`1 - 2*<x,y>/(|x|^2+|y|^2)`
- `check_bias(x, ref_x)`：统计偏差检验（二项分布，99.99999%置信区间）
- `count_bytes(*tensors) -> int`：递归计算tensor(s)的总字节数

## F-081: 量化测试工具

**文件**: `tile_kernels/testing/quant.py`
- `clear_unused_sf(sf, hidden, num_per_channels) -> Tensor`：将sf中超出实际channel block数的尾部条目清零

---

## F-082: 支持的数据格式汇总

根据源码直接观察，项目支持以下量化数据格式：
- **FP8 E4M3**：`torch.float8_e4m3fn`，最大量化值448.0，clamp_min=1e-4
- **FP4 E2M1**：`torch.int8`（packed，两个4位值打包为一个int8），最大量化值6.0，bias=1，RTNE舍入
- **E5M6**：`torch.uint8`（packed，8个12位值打包为3个uint32=12字节=96位），1s+5e+6m，bias=15，max_normal=65024.0
- **BF16**：`torch.bfloat16`，主要计算精度
- **FP32**：`torch.float32`，累加/权重/中间结果精度
- **FP16**：`torch.float16`，E5M6反量化中间格式
- **TF32**：通过`round_to_tf32`将float32舍入到tf32精度用于GEMM

## F-083: TileLang DSL使用模式

- Kernel工厂函数使用`@tilelang.jit`装饰，接受编译期参数（如hidden, mhc_mult等），返回JITKernel
- Pass配置常用：`TL_DISABLE_WARP_SPECIALIZED: True`, `TL_DISABLE_WGMMA: True`, `TL_PTXAS_REGISTER_USAGE_LEVEL`, `TL_DISABLE_VECTORIZE_256`
- 动态维度使用`T.dynamic('name')`声明
- Kernel主体使用`@T.prim_func`装饰，参数用`T.Tensor[(dims), dtype]`或`T.StridedTensor[(dims), (strides), dtype]`声明
- Kernel启动用`with T.Kernel(...) as (pid...)`网格定义
- 共享内存：`T.alloc_shared(shape, dtype)`；局部寄存器：`T.alloc_local/fragment(shape, dtype)`
- 并行循环：`for i, j in T.Parallel(shape...)`；展开循环：`for i in T.unroll(n)`；向量化：`for i in T.vectorized(n)`
- 线程束原语：`T.shfl_sync`, `T.sync_warp()`, `T.sync_threads()`
- Reducer：`T.alloc_reducer(size, dtype, replication='all')`
- 宏定义：`@T.macro`装饰器定义可复用TileLang代码块
- 环境变量`TK_PRINT_KERNEL_SOURCE=1`时多个kernel会打印生成的CUDA源码

## F-084: Autograd Function模式

- 所有高层op封装为`torch.autograd.Function`子类
- 统一模式：`forward`中调用TileLang JIT kernel，`backward`中调用对应的反向kernel
- 梯度累加融合（fuse_grad_acc）：通过`tensor.untyped_storage().grad_from_mhc_post`属性在不同Function之间传递fp32梯度缓冲区，避免额外内存分配
- main_grad模式：参数权重的`main_grad`属性（fp32梯度缓冲区）存在时，梯度原地累积到main_grad，backward返回None
- backward中scale/base等1D参数的梯度使用`num_sms`个partial buffer，最后sum(0)归约
