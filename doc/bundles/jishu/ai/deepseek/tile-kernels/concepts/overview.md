---
type: concept
scope: tile-kernels
name: TileKernels 概述
version: "0.1.0"
source: tile-kernels-spec-facts
description: TileKernels 架构总览、TileLang DSL、功能模块、包结构、与 DeepGEMM/DeepEP 的协同
---

# TileKernels 概述

**TileKernels** 是 DeepSeek 开源的基于 TileLang DSL 的高性能 CUDA 核函数库，为大语言模型（特别是 DeepSeek-V3/V4）的训练与推理提供 GEMM 之外的关键算子实现，涵盖低精度量化、MoE 路由与 dispatch/combine、MHC（Multi-Head Compute）、Engram 记忆机制和转置。

---

## 一、核心定位

TileKernels 的设计目标是作为 DeepSeek 推理/训练栈中 GEMM 核函数的补充，覆盖那些不适合用纯 C++ CUDA 编写、但需要极高性能的"非 GEMM"算子：

| 能力 | 说明 | 与 DeepGEMM 关系 |
|---|---|---|
| **FP8/FP4/E5M6 量化** | 各种粒度的 cast/cast_back 核函数 | 为 DeepGEMM 提供输入量化 |
| **SwiGLU 融合量化** | 激活+量化/转置多算子融合 | DeepGEMM GEMM 前后的融合算子 |
| **MoE 路由** | topk gate、group routing、fused mapping | DeepGEMM grouped GEMM 的前置/后置 |
| **MoE dispatch/combine** | expand_to_fused / reduce_fused | DeepGEMM 前后的数据布局转换 |
| **MHC** | Multi-Head Compute 全套算子 | DeepSeek-V4 核心结构专用 |
| **Engram** | 记忆门控、hash、权重融合 | 记忆增强机制 |
| **转置** | 高性能 2D/3D 张量转置 | 数据布局转换 |

与 DeepSeek 推理栈的关系：

```
DeepEP（通信） ←→ TileKernels（路由/dispatch/combine/量化） ←→ DeepGEMM（矩阵乘）
```

- **[DeepGEMM](../../deep-gemm/index.md)**：C++ JIT GEMM 核函数库，负责核心矩阵乘法
- **[DeepEP](../../deep-ep/index.md)**：专家并行通信库，负责跨节点 all-to-all
- **TileKernels**：TileLang DSL 编写的非 GEMM 算子，负责量化、路由、本地 dispatch/combine、MHC 等

---

## 二、技术栈

### 2.1 TileLang DSL

TileKernels 使用 [TileLang](https://github.com/tile-ai/tilelang) 作为核函数编写 DSL。TileLang 是一种类 TVMScript 的 Python DSL，允许开发者以高抽象级别编写 CUDA kernel，同时保留对线程映射、共享内存、warp 原语等底层细节的控制。

核心优势：
- **Python 原生**：kernel 代码就是 Python，支持函数、宏、dataclass 等抽象
- **JIT 编译**：`@tilelang.jit` 装饰器在运行时编译为 CUDA kernel，无需预编译
- **多面体调度**：自动处理循环变换、内存层次映射
- **Warp/Thread Block 原语**：直接访问 warp shuffle、shared memory、TMA 等硬件特性

### 2.2 依赖

| 依赖 | 版本要求 | 用途 |
|---|---|---|
| Python | >= 3.10 | 运行时 |
| PyTorch | >= 2.10 | 张量管理、autograd、CUDA 运行时 |
| TileLang | >= 0.1.9 | DSL 编译器和 JIT 运行时 |
| setuptools-scm | >= 8 | 版本自动生成 |

---

## 三、功能模块

### 3.1 量化模块（tile_kernels.quant）

量化是 TileKernels 最核心的模块，提供多种粒度和格式的量化算子：

| 类别 | 算子 | 格式 |
|---|---|---|
| Per-token 量化 | `per_token_cast`, `per_token_cast_with_precomputed_sf` | FP8 E4M3, FP4 E2M1 |
| Per-token E5M6 | `per_token_cast_to_e5m6` | E5M6 (12-bit) |
| Per-block 量化 | `per_block_cast`, `per_block_cast_with_precomputed_sf` | FP8 E4M3, FP4 E2M1 |
| Per-channel 量化 | `per_channel_cast`, `per_channel_cast_fused` | FP8 E4M3 |
| Per-channel+转置 | `per_channel_cast_and_transpose` | FP8 E4M3 |
| 反量化 | `cast_back`, `per_token_cast_back`, `cast_back_e5m6` | BF16/FP32 输出 |
| 无损重量化 | `per_block_cast_lossless` | FP4→FP8 |
| SwiGLU+per-token 量化 | `swiglu_forward_and_per_token_cast` | FP8 E4M3 |
| SwiGLU+per-channel+转置 | `swiglu_forward_and_per_channel_cast_and_transpose` | FP8 E4M3 |
| SwiGLU 反向+量化 | `swiglu_backward_and_per_token_cast` | FP8 E4M3 |

**统一类型**：量化结果统一用 `QuantTensor = tuple[torch.Tensor, torch.Tensor]` 表示，即 `(data, scale_factors)`。

**统一配置**：`BaseCastConfig`/`CastInputConfig`/`CastOutputConfig` 三个 frozen dataclass 管理量化参数。

### 3.2 MoE 模块（tile_kernels.moe）

| 阶段 | 算子 |
|---|---|
| 路由 | `topk_gate`, `topk_sum_and_topk_group_idx`, `top2_sum_gate` |
| 映射 | `get_fused_mapping` |
| Dispatch | `expand_to_fused`, `expand_to_fused_with_sf` |
| Combine | `reduce_fused` |
| 辅助 | `aux_fi`, `group_count`, `normalize_weight`, `inplace_unique_group_indices`, `mask_indices_by_tp` |

支持三种评分函数：sigmoid、sqrtsoftplus、softmax；支持 EP/TP masking、shared expert、logical→physical 映射。

### 3.3 MHC 模块（tile_kernels.mhc + tile_kernels.modeling.mhc）

MHC（Multi-Head Compute）是 DeepSeek-V4 的核心结构，在传统 residual 上引入多"头"计算：

| 算子 | 功能 |
|---|---|
| `expand_to_mhc` | 复制扩展到多头 |
| `mhc_pre_norm_fn` | RMSNorm + 线性变换 |
| `mhc_pre_split_mixes` | Mix 系数计算与分割 |
| `sinkhorn_normalize` | Sinkhorn 双随机归一化 |
| `mhc_pre_apply_mix` | 多头加权合并 |
| `mhc_post` | 后处理 residual 更新 |
| `mhc_pre_big_fuse` | 推理模式大融合 kernel |
| `mhc_multilayer_recompute` | 多层重计算（梯度检查点） |
| `mhc_head_compute_mix` | LM Head mix 计算 |

高层 API：`mhc_pre()`（子层预处理一站式）、`mhc_head()`（LM Head）。

### 3.4 Engram 模块（tile_kernels.engram + tile_kernels.modeling.engram）

| 算子 | 功能 |
|---|---|
| `fused_weight` | 权重逐元素融合乘法 |
| `engram_gate_fwd/bwd` | 记忆门控前向/反向 |
| `grad_w_reduce` | 权重梯度归约 |
| `engram_hash` | N-gram XOR 哈希 |

### 3.5 转置模块（tile_kernels.transpose）

- `transpose(x)`：2D 张量转置（M%64==0, N%64==0）
- `batched_transpose(x)`：3D 批量转置

### 3.6 PyTorch 参考实现（tile_kernels.torch）

每个 kernel 都有纯 PyTorch 参考实现，用于数值正确性验证。包括量化、反量化、MoE、MHC、SwiGLU、Engram hash 等。

### 3.7 测试工具（tile_kernels.testing）

- `bench`：CUDA Event 计时、性能统计
- `numeric`：余弦差异、偏差统计检验、完全相等断言
- `generator`：测试数据生成（随机+特殊值）
- `quant`：量化辅助工具

---

## 四、包结构

```
tile_kernels/
├── __init__.py              # 包入口，导出 config/quant/moe/engram/modeling/transpose/torch/testing
├── config.py                # SM 管理、共享内存查询
├── utils.py                 # ceil_div/align/is_power_of_two
├── quant/                   # 量化核函数
│   ├── __init__.py          # 导出所有量化函数
│   ├── types.py             # QuantTensor 类型定义
│   ├── common.py            # CastConfig dataclass、TileLang宏、辅助函数
│   ├── per_token_cast_kernel.py
│   ├── per_token_cast_to_e5m6_kernel.py
│   ├── per_block_cast_kernel.py
│   ├── per_block_cast_lossless_kernel.py
│   ├── per_channel_cast_kernel.py
│   ├── per_channel_cast_fused_kernel.py
│   ├── per_channel_cast_and_transpose_kernel.py
│   ├── cast_back_kernel.py
│   ├── cast_back_e5m6_kernel.py
│   ├── swiglu_forward_and_per_token_cast_kernel.py
│   ├── swiglu_backward_and_per_token_cast_kernel.py
│   └── swiglu_forward_and_per_channel_cast_and_transpose_kernel.py
├── moe/                     # MoE 核函数
│   ├── __init__.py
│   ├── scoring.py           # ScoringFunc 枚举、softplus 宏
│   ├── common.py            # get_topk_group_idx 宏
│   ├── topk_gate_kernel.py
│   ├── topk_sum_and_topk_group_idx_kernel.py
│   ├── top2_sum_gate_kernel.py
│   ├── get_fused_mapping_kernel.py
│   ├── expand_to_fused_kernel.py
│   ├── reduce_fused_kernel.py
│   ├── aux_fi_kernel.py
│   ├── group_count_kernel.py
│   ├── normalize_weight_kernel.py
│   ├── inplace_unique_group_indices_kernel.py
│   └── mask_indices_by_tp_kernel.py
├── mhc/                     # MHC 底层核函数
│   ├── __init__.py          # 空文件，不导出
│   ├── expand_kernel.py
│   ├── head_compute_mix_kernel.py
│   ├── norm_fn_kernel.py
│   ├── pre_split_mixes_kernel.py
│   ├── sinkhorn_kernel.py
│   ├── pre_apply_mix_kernel.py
│   ├── post_kernel.py
│   ├── pre_big_fuse_kernel.py
│   └── multilayer_recompute_kernel.py
├── engram/                  # Engram 底层核函数
│   ├── __init__.py
│   ├── engram_fused_weight_kernel.py
│   ├── engram_gate_kernel.py
│   ├── engram_grad_w_reduce_kernel.py
│   └── engram_hash_kernel.py
├── modeling/                # autograd.Function 高层封装
│   ├── __init__.py
│   ├── engram/
│   │   ├── __init__.py
│   │   └── engram_gate.py   # EngramGateFn
│   └── mhc/
│       ├── __init__.py
│       ├── functional.py    # mhc_pre/mhc_head/expand_from_embedding
│       └── ops/
│           ├── __init__.py
│           ├── expand.py
│           ├── head_compute_mix.py
│           ├── norm_fn.py
│           ├── pre_split_mixes.py
│           ├── sinkhorn.py
│           ├── pre_apply_mix.py
│           ├── post.py
│           ├── pre_big_fuse.py
│           └── multilayer_recompute.py
├── transpose/               # 转置核函数
│   ├── __init__.py
│   └── batched_transpose_kernel.py
├── torch/                   # PyTorch 参考实现
│   ├── __init__.py
│   ├── cast.py
│   ├── cast_e5m6.py
│   ├── moe.py
│   ├── mhc.py
│   ├── engram.py
│   ├── expand_to_fused.py
│   ├── reduce_fused.py
│   ├── swiglu.py
│   ├── per_channel_cast_fused.py
│   └── topk.py
└── testing/                 # 测试工具
    ├── __init__.py
    ├── bench.py
    ├── numeric.py
    ├── generator.py
    └── quant.py
```

---

## 五、设计哲学

1. **分层架构**：底层 TileLang JIT kernel → Python wrapper → autograd.Function 封装 → functional 高层 API
2. **宏复用**：量化模块通过 `@T.macro` 复用 sf 加载/存储/计算宏，避免代码重复
3. **融合优先**：尽可能将多个算子融合为单个 kernel（SwiGLU+cast、norm_fn+split+sinkhorn+apply 等）
4. **训练/推理双路径**：训练走可微 autograd.Function 链，推理用更大粒度的融合 kernel
5. **梯度优化**：fuse_grad_acc 和 main_grad 两种机制减少反向传播中的内存分配
6. **参考实现**：每个 kernel 都有纯 PyTorch 参考，确保数值正确性可验证
7. **配置驱动**：量化参数通过 frozen dataclass 管理，支持多种精度和缩放因子布局

---

## 六、相关项目

| 项目 | 关系 |
|---|---|
| [DeepGEMM](../../deep-gemm/index.md) | DeepSeek 高性能 C++ JIT GEMM 库，TileKernels 为其提供量化、MoE dispatch/combine 等补充算子 |
| [DeepEP](../../deep-ep/index.md) | DeepSeek 专家并行通信库，处理跨节点 all-to-all，TileKernels 处理本地 dispatch/combine |
| TileLang | TileKernels 使用的 DSL 编译器和 JIT 运行时 |
