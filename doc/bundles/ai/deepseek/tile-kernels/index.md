---
type: bundle
okf_version: "0.2"
scope: tile-kernels
name: TileKernels Wiki
version: "0.1.0"
source: https://github.com/deepseek-ai/TileKernels
description: TileKernels - DeepSeek 基于 TileLang DSL 的 CUDA 核函数库文档（量化、MoE、MHC、Engram、转置）
---

# TileKernels

**TileKernels** 是 DeepSeek 开源的基于 TileLang DSL 的高性能 CUDA 核函数库，为大语言模型（特别是 DeepSeek-V3/V4）的训练与推理提供 GEMM 之外的关键算子——覆盖 FP8/FP4/E5M6 低精度量化、MoE 路由与 dispatch/combine、MHC（Multi-Head Compute）多头残差计算、Engram 记忆机制以及高性能转置。

- **版本**：0.1.0（Alpha）
- **开源仓库**：[deepseek-ai/TileKernels](https://github.com/deepseek-ai/TileKernels)
- **DSL**：TileLang ≥ 0.1.9
- **最低 PyTorch 版本**：2.10
- **Python 版本**：≥ 3.10
- **许可证**：MIT

---

## 核心能力

| 能力 | 说明 | 主要算子 |
|---|---|---|
| **FP8 量化** | E4M3 精度，per-token/per-block/per-channel 粒度 | `per_token_cast`, `per_block_cast`, `per_channel_cast_fused` |
| **FP4 量化** | E2M1 精度，nibble packing（2值/byte） | `per_token_cast`(fmt='e2m1'), `per_block_cast_lossless` |
| **E5M6 量化** | 12-bit 自定义格式，8值打包为3uint32 | `per_token_cast_to_e5m6`, `cast_back_e5m6` |
| **SwiGLU 融合** | 激活+量化/转置多算子融合 | `swiglu_forward_and_per_token_cast`, `swiglu_backward_and_per_token_cast` |
| **MoE 路由** | Top-k/Top2-Sum gate，支持 group routing | `topk_gate`, `top2_sum_gate`, `topk_sum_and_topk_group_idx` |
| **MoE 映射** | Fused mapping 一次性构建全部索引 | `get_fused_mapping` |
| **MoE Dispatch/Combine** | Token 扩展排列与加权归约 | `expand_to_fused`, `reduce_fused`, `expand_to_fused_with_sf` |
| **MHC 多头计算** | DeepSeek-V4 核心结构，多head残差 | `mhc_pre`, `mhc_post`, `mhc_head`, `mhc_pre_big_fuse` |
| **MHC Sinkhorn** | 双随机矩阵归一化 | `sinkhorn_normalize` |
| **Engram 记忆门控** | 记忆增强机制 | `engram_gate`, `fused_weight`, `grad_w_reduce` |
| **Engram Hash** | N-gram XOR 哈希 | `engram_hash` |
| **转置** | 高性能 2D/3D 张量转置 | `transpose`, `batched_transpose` |

---

## 支持的数据格式

| 格式 | 位宽 | 指数/尾数 | torch dtype | 主要用途 |
|---|---|---|---|---|
| FP8 E4M3 | 8 bit | 4e/3m | `torch.float8_e4m3fn` | 训练/推理主量化精度 |
| FP4 E2M1 | 4 bit | 2e/1m | `torch.int8`（packed） | 极限压缩（权重/KV cache） |
| E5M6 | 12 bit | 5e/6m | `torch.uint8`（packed） | KV cache 高精度压缩 |
| BF16 | 16 bit | 8e/7m | `torch.bfloat16` | 主计算精度 |
| FP32 | 32 bit | 8e/23m | `torch.float32` | 累加/权重/中间结果 |
| TF32 | 19 bit | 8e/10m | float32（rounded） | Tensor Core GEMM |
| UE8M0 | 8 bit | 8e/0m | `torch.uint8`（packed） | SM100 缩放因子 |

---

## 文档导航

### 📘 核心概念 [concepts/](/ai/deepseek/tile-kernels/concepts/)

| 文档 | 内容 |
|---|---|
| [概述](/ai/deepseek/tile-kernels/concepts/overview) | 架构总览、功能模块、包结构、与 DeepGEMM/DeepEP 的协同 |
| [FP8/FP4 量化与反量化](/ai/deepseek/tile-kernels/concepts/fp8-quantization) | 低精度格式、量化粒度（per-token/block/channel）、缩放因子布局、SwiGLU 融合量化 |
| [MoE 核函数流水线](/ai/deepseek/tile-kernels/concepts/moe-kernels) | 完整 MoE 前向流水线、top2-sum gate、fused mapping、expand/reduce、warp 原语 |
| [MHC Multi-Head Compute](/ai/deepseek/tile-kernels/concepts/mhc-multi-head-compute) | DeepSeek-V4 MHC 结构、多头残差、Sinkhorn 归一化、训练/推理双路径、梯度融合 |
| [TileLang DSL 编程模式](/ai/deepseek/tile-kernels/concepts/tilelang-dsl-patterns) | @tilelang.jit、T.prim_func、T.Kernel、T.Parallel、共享内存、warp 原语、宏复用、Pass 配置 |
| [Autograd 集成模式](/ai/deepseek/tile-kernels/concepts/autograd-integration) | autograd.Function 封装、fuse_grad_acc、main_grad、partial buffer reduce |

### 📗 API 参考 [references/](/ai/deepseek/tile-kernels/references/)

| 文档 | 内容 |
|---|---|
| [公共 API](/ai/deepseek/tile-kernels/references/api) | 配置管理、量化、MoE、MHC、Engram、转置、数据类完整 API 签名 |
| [量化核函数](/ai/deepseek/tile-kernels/references/quant-kernels) | FP8/FP4/E5M6 cast、SwiGLU 融合、反量化、量化配置体系、缩放因子布局 |
| [MoE 核函数](/ai/deepseek/tile-kernels/references/moe-kernels) | topk gate、fused mapping、expand/reduce、辅助算子、与 DeepGEMM/DeepEP 协同 |
| [MHC/Engram/转置](/ai/deepseek/tile-kernels/references/mhc-kernels) | MHC 全套算子、Engram 门控/哈希/梯度、转置、配置工具函数 |

### 📙 代码示例 [examples/](/ai/deepseek/tile-kernels/examples/)

| 示例 | 内容 |
|---|---|
| [FP8 量化基础](/ai/deepseek/tile-kernels/examples/basic-quant) | Per-token/block/channel 量化、FP4/E5M6、SwiGLU 融合、精度对比 |
| [MoE 前向计算](/ai/deepseek/tile-kernels/examples/moe-forward) | 完整 MoE 流水线：gate → mapping → expand → expert compute → reduce |
| [MHC 使用](/ai/deepseek/tile-kernels/examples/mhc-usage) | MHC 初始化、mhc_pre/mhc_post 训练/推理、LM Head、多层重计算 |

---

## 快速开始

```python
import torch
import tile_kernels

# === FP8 量化 ===
x = torch.randn(4096, 4096, device='cuda', dtype=torch.bfloat16)
x_fp8, x_sf = tile_kernels.quant.per_token_cast(x, fmt='e4m3', num_per_channels=128)
x_bf16 = tile_kernels.quant.per_token_cast_back((x_fp8, x_sf), fmt='bf16', num_per_channels=128)

# === MoE 路由 ===
scores = torch.randn(4096, 64, device='cuda', dtype=torch.float32)
topk_idx = tile_kernels.moe.topk_gate(scores, num_topk=8)

# === 配置 SM 数量 ===
tile_kernels.set_num_sms(64)
print(f"SMs: {tile_kernels.get_num_sms()}")
```

---

## 包结构

```
tile_kernels/
├── config.py              # SM 管理配置
├── utils.py               # 工具函数
├── quant/                 # 量化核函数（FP8/FP4/E5M6 + SwiGLU融合）
├── moe/                   # MoE 核函数（gate/expand/reduce/辅助）
├── mhc/                   # MHC 底层核函数
├── engram/                # Engram 底层核函数
├── modeling/              # autograd.Function 高层封装
│   ├── engram/            # EngramGateFn
│   └── mhc/               # MHC 全套 autograd.Function + functional API
├── transpose/             # 转置核函数
├── torch/                 # PyTorch 参考实现（数值验证用）
└── testing/               # 测试工具（bench/numeric/generator）
```

---

## 相关项目

| 项目 | 关系 |
|---|---|
| [DeepGEMM](/ai/deepseek/deep-gemm/) | DeepSeek 高性能 C++ JIT GEMM 库，负责核心矩阵乘法；TileKernels 为其提供量化、MoE dispatch/combine 等补充算子 |
| [DeepEP](/ai/deepseek/deep-ep/) | DeepSeek 专家并行通信库，负责跨节点 all-to-all 通信；TileKernels 负责本地 dispatch/combine |
| [TileLang](https://github.com/tile-ai/tilelang) | TileKernels 使用的 Python DSL 编译器和 JIT 运行时 |

```{toctree}
:hidden:

concepts/index
examples/index
references/index
spec/facts
spec/insights
```
