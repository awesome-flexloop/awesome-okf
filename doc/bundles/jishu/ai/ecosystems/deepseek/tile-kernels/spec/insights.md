---
type: spec-insights
scope: tile-kernels
source: tile-kernels-spec-facts
---

# TileKernels 核心洞察

## 一、架构定位

TileKernels 是 DeepSeek 开源的基于 TileLang DSL 的 CUDA 核函数库，定位为 DeepGEMM（C++ JIT GEMM）的补充算子集，覆盖大语言模型训练与推理中 GEMM 之外的关键高性能算子：量化（FP8/FP4/E5M6 cast）、MoE 路由与 dispatch/combine、MHC（Multi-Head Compute，DeepSeek-V4 核心结构）、Engram（记忆机制）以及转置。所有核函数通过 `@tilelang.jit` 装饰器在运行时编译为 CUDA kernel，无需预编译二进制。

- **DSL 选择**：使用 TileLang（类 TVMScript 的 Python DSL）编写 kernel，而非原生 CUDA C++ 或 Triton
- **精度体系**：BF16 计算主精度 + FP8/FP4/E5M6 低精度存储/通信 + FP32 累加/权重
- **与 DeepGEMM 协同**：TileKernels 负责 GEMM 前后的融合算子（SwiGLU+cast、MoE expand/reduce 等），DeepGEMM 负责核心矩阵乘
- **与 DeepEP 协同**：MoE 层通信走 DeepEP（all-to-all），本地 dispatch/combine 走 TileKernels

## 二、模块分类体系

### 2.1 量化（quant/）—— 最核心模块

| 量化粒度 | 函数 | 支持格式 | 说明 |
|---|---|---|---|
| per_token | `per_token_cast` | FP8 E4M3, FP4 E2M1 | 逐 token 缩放，激活量化 |
| per_token (E5M6) | `per_token_cast_to_e5m6` | E5M6 | 12-bit 自定义格式，8个值打包为3个uint32 |
| per_block | `per_block_cast` | FP8 E4M3, FP4 E2M1 | 逐 block 缩放，权重量化 |
| per_channel | `per_channel_cast` | FP8 E4M3 | 逐 channel 缩放（num_per_tokens=128） |
| per_channel_fused | `per_channel_cast_fused` | FP8 E4M3 | 融合反量化+重缩放+gather扩展 |
| per_channel+transpose | `per_channel_cast_and_transpose` | FP8 E4M3 | 量化+转置融合 |
| SwiGLU融合 | `swiglu_forward_and_per_token_cast` | FP8 E4M3 | SwiGLU激活+路由缩放+FP8量化 |
| SwiGLU融合 | `swiglu_forward_and_per_channel_cast_and_transpose` | FP8 E4M3 | SwiGLU+per_channel量化+转置 |
| SwiGLU反向 | `swiglu_backward_and_per_token_cast` | FP8 E4M3 | SwiGLU反向+梯度FP8量化 |
| 反量化 | `cast_back`, `per_token_cast_back` | BF16/FP32 | 低精度→高精度反量化 |
| 无损重量化 | `per_block_cast_lossless` | FP4→FP8 | FP4无损上转FP8 |

关键设计：
- **QuantTensor 类型**：所有量化结果统一为 `(data, scale_factors)` 二元组
- **三种配置 dataclass**：`BaseCastConfig`（基础）、`CastInputConfig`（含 with_sf）、`CastOutputConfig`（含 round_sf/clamp）
- **TileLang 宏复用**：`get_sf_and_inv`、`load_sf`、`transform_sf`、`store_sf` 四个 `@T.macro` 在各量化 kernel 间复用
- **E5M6 格式**：1s+5e+6m（bias=15），类 FP16 截断精度，max_normal=65024，用于 KV cache 等场景

### 2.2 MoE（moe/）—— 专家并行路由

| 阶段 | 函数 | 说明 |
|---|---|---|
| 评分+路由 | `topk_gate` | 稳定 topk 选择（warp shuffle 规约） |
| 组路由 | `topk_sum_and_topk_group_idx` | 组内 topk sum → 选 topk groups |
| 完整路由 | `top2_sum_gate` | 端到端 top2-sum gate（sigmoid/sqrtsoftplus/softmax + EP/TP mask + shared expert） |
| 映射构建 | `get_fused_mapping` | 构建 pos→token/expert 映射表（8元组输出） |
| Dispatch | `expand_to_fused` / `expand_to_fused_with_sf` | token 按 expert 扩展排列（支持 QuantTensor） |
| Combine | `reduce_fused` | expert 输出加权归约回 token（支持 FP8 输出） |
| 辅助 | `aux_fi`, `group_count`, `normalize_weight`, `inplace_unique_group_indices`, `mask_indices_by_tp` | 负载均衡、TP 掩码、权重归一化 |

关键设计：
- **评分函数枚举**：`ScoringFunc` 支持 SIGMOID(0)/SQRTSOFTPLUS(1)/SOFTMAX(2)/IDENTITY(3)
- **融合映射**：`get_fused_mapping` 一次性产出全部索引映射，支持自动估算 expanded tokens 数和 host sync 裁剪
- **FP8 combine**：reduce_fused 支持 fp8_format='e4m3' 直接输出 FP8 结果

### 2.3 MHC（mhc/ + modeling/mhc/）—— Multi-Head Compute

MHC 是 DeepSeek-V4 的核心创新结构，通过多"头"计算实现更细粒度的特征处理。

| 子模块 | Kernel 函数 | Modeling 封装 | 说明 |
|---|---|---|---|
| 扩展 | `expand_to_mhc_fwd_tl/bwd_tl` | `ExpandToMHCFn` / `expand_to_mhc` | (n,h)→(n,mhc_mult,h) 复制+反向求和 |
| Mix计算 | `_mhc_head_compute_mix_fwd/bwd` | `MHCHeadComputeMix` / `mhc_head_compute_mix` | sigmoid(input*scale+base)+eps |
| Norm+Fn | `_mhc_pre_norm_fn_fwd_mul/norm/bwd_*` | `MHCPreNormFn` / `mhc_pre_norm_fn` | RMSNorm+GEMM（TileLang强制n_splits=1，大GEMM建议DeepGEMM） |
| SplitMixes | `_mhc_pre_split_mixes_fwd/bwd` | `MHCPreSplitMixes` / `mhc_pre_split_mixes` | mix线性变换→分割为pre/post/comb |
| Sinkhorn | `_mhc_sinkhorn_fwd/bwd` | `_SinkhornNormalize` / `sinkhorn_normalize` | 迭代行列归一化（双随机矩阵） |
| ApplyMix | `_mhc_pre_apply_mix_fwd/bwd` | `MHCPreApplyMix` / `mhc_pre_apply_mix` | 加权求和归约mhc维度 |
| Post | `mhc_post_fwd/bwd` | `MHCPost` / `mhc_post` | 后处理：residual混合 |
| 大融合(推理) | `_mhc_pre_big_fuse` | `mhc_pre_big_fuse` | 推理时融合norm_fn+split_mixes+sinkhorn+apply_mix |
| 多层重计算 | `mhc_multilayer_recompute` | 同左 | 指针表批处理原地重计算多层residual |
| 高层API | — | `mhc_pre`, `mhc_head`, `expand_from_embedding` | functional 风格的一站式接口 |

关键设计：
- **训练/推理双路径**：训练走分步骤 autograd.Function 链；推理使用 `mhc_pre_big_fuse` 大融合 kernel
- **梯度累加融合**：通过 `tensor.untyped_storage().grad_from_mhc_post` 属性在 Function 间传递 fp32 梯度缓冲区，避免额外分配
- **Fn+Normw 融合**：`_MHCFnNormwMerge` 融合 fn 权重和 norm 权重的乘法
- **TF32 舍入**：`round_to_tf32` 将 float32 权重舍入到 TF32 精度供 Tensor Core 使用

### 2.4 Engram（engram/ + modeling/engram/）—— 记忆机制

| 函数 | Modeling 封装 | 说明 |
|---|---|---|
| `fused_weight` | EngramGateFn 内部调用 | bf16×bf16→fp32 逐元素融合权重乘法 |
| `engram_gate_fwd/bwd` | `EngramGateFn` / `engram_gate` | 门控计算：sigmoid(signed_sqrt(dot(RMSNorm(x,wh),RMSNorm(k,we))*scalar)); output=x+gate*v |
| `grad_w_reduce` | EngramGateFn.backward 内部 | partial 梯度归约+权重乘法融合 |
| `engram_hash` | — | n-gram XOR hash：XOR→mod→+offsets |

### 2.5 Transpose（transpose/）

- `transpose(x)`：2D 张量转置，(M,N)→(N,M)，M/N 需 64 对齐
- `batched_transpose(x)`：3D 批量转置，(B,M,N)→(B,N,M)
- 使用 shared memory padding 减少 bank conflict，swizzle 布局优化

### 2.6 工具与配置（config.py, utils.py, testing/）

- **SM 管理**：`get_num_sms()`/`set_num_sms(n)`/`get_device_num_sms()` 控制使用的 SM 数量
- **共享内存查询**：`get_max_smem_per_sm()` 获取每个 SM 的最大共享内存
- **工具函数**：`ceil_div`, `align`, `is_power_of_two`
- **测试框架**：`testing/` 提供 bench 计时、数值验证（余弦差异+偏差统计检验）、测试数据生成器

## 三、TileLang DSL 使用模式

1. **JIT 编译**：`@tilelang.jit` 装饰 kernel 工厂函数，编译期参数（hidden, mhc_mult 等）作为工厂参数，运行期维度用 `T.dynamic('name')` 声明
2. **Kernel 结构**：`@T.prim_func` 定义函数签名 → `with T.Kernel(grid, blocks) as (pid...)` 启动网格 → 内部循环/拷贝/计算
3. **内存层级**：全局内存（T.Tensor/T.StridedTensor）→ 共享内存（T.alloc_shared）→ 寄存器/片段（T.alloc_local/T.alloc_fragment）
4. **并行模式**：`T.Parallel` 自动并行化循环、`T.vectorized` 向量化加载、`T.unroll` 循环展开
5. **Warp 级原语**：`T.shfl_sync`、`T.sync_warp()` 用于 warp 内规约（topk、reduce）
6. **Reducer**：`T.alloc_reducer(size, dtype, replication='all')` 用于 block 级归约
7. **Pass 配置**：常用 `TL_DISABLE_WARP_SPECIALIZED: True`（禁用 warp specialization）、`TL_DISABLE_WGMMA: True`（禁用 WGMMA）、`TL_PTXAS_REGISTER_USAGE_LEVEL`（寄存器使用控制）
8. **宏复用**：`@T.macro` 定义可复用代码片段，如 SF 加载/存储/转换

## 四、Autograd 集成模式

所有高层算子统一封装为 `torch.autograd.Function` 子类：
- **标准模式**：`forward` 调用前向 TileLang JIT kernel，`backward` 调用对应反向 kernel
- **main_grad 模式**：权重参数若有 `.main_grad` 属性（fp32 梯度缓冲区），梯度原地累积到 main_grad，backward 对该参数返回 None
- **fuse_grad_acc 模式**：通过 `untyped_storage().grad_from_mhc_post` 属性在多个 Function 间共享梯度缓冲区，避免反复分配/释放
- **partial buffer 归约**：scale/base 等 1D 参数的梯度使用 num_sms 个 partial buffer，最后 `sum(0)` 归约
- **save_for_backward**：标准 PyTorch 反向保存中间结果机制

## 五、PyTorch 参考实现

`tile_kernels/torch/` 目录为每个 kernel 提供纯 PyTorch 参考实现：
- 用于数值正确性验证（kernel 输出 vs 参考输出的余弦差异+偏差检验）
- 包含完整的 FP4 打包/解包、E5M6 编解码、SwiGLU 前后向、MoE 路由、MHC 全流程
- `@torch.compile` 标注的 elementwise_fma 用于确保 FMA 精度匹配

## 六、数据格式体系

| 格式 | torch dtype | 位宽 | 指数/尾数 | 特点 |
|---|---|---|---|---|
| FP8 E4M3 | torch.float8_e4m3fn | 8bit | 4e/3m, bias=7 | 标准训练精度，max=448 |
| FP4 E2M1 | torch.int8 (packed) | 4bit | 2e/1m, bias=1 | 极低精度，2值/byte，max=6，RTNE舍入 |
| E5M6 | torch.uint8 (packed) | 12bit | 5e/6m, bias=15 | 类FP16截断，8值/3uint32(96bit)，max=65024 |
| BF16 | torch.bfloat16 | 16bit | 8e/7m | 主计算精度 |
| FP32 | torch.float32 | 32bit | 8e/23m | 累加/权重/中间结果 |
| FP16 | torch.float16 | 16bit | 5e/10m | E5M6反量化中间格式 |
| TF32 | float32 (rounded) | 19bit | 8e/10m | Tensor Core GEMM输入 |
| UE8M0 | torch.uint8 (packed) | 8bit | 8e/0m | SM100 缩放因子格式 |
