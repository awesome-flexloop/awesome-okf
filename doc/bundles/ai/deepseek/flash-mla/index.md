---
type: bundle
okf_version: "0.2"
scope: flash-mla
name: FlashMLA Wiki
version: "1.0.0"
source: https://github.com/deepseek-ai/FlashMLA
description: FlashMLA - DeepSeek 高效 MLA 注意力解码核函数库文档，支持 Hopper/Blackwell GPU
---

# FlashMLA

**FlashMLA** 是 DeepSeek 开源的高效 MLA（Multi-head Latent Attention）注意力核函数库，专为 NVIDIA Hopper（SM90）和 Blackwell（SM100）GPU 深度优化，为 [DeepSeek-V3](https://github.com/deepseek-ai/DeepSeek-V3)、DeepSeek-V3.2、DeepSeek-R1 等模型的推理提供高性能 MLA 解码（decoding）与预填充（prefill）计算。

- **版本**：1.0.0
- **开源仓库**：[deepseek-ai/FlashMLA](https://github.com/deepseek-ai/FlashMLA)
- **支持架构**：Hopper (H100/H200/H800)、Blackwell (B100/B200)
- **最低 CUDA 版本**：12.8（SM100 需要 12.9+）
- **最低 PyTorch 版本**：2.0

---

## 核心能力

| 能力 | 说明 | SM90 | SM100 |
|---|---|---|---|
| **Dense MLA Decoding** | BF16/FP16 分页注意力解码 | ✅ | ❌ |
| **Sparse MLA Decoding (FP8)** | FP8 KV cache + Token 级稀疏注意力 | ✅ | ✅ |
| **Dense MHA Prefill** | 标准 MHA 前向/反向变长注意力 | ❌ | ✅ (CUTLASS) |
| **Sparse MLA Prefill** | Token 级稀疏注意力预填充 | ✅ | ✅ |
| **SplitKV 长序列** | KV 序列分块并行，支持 32K+ 上下文 | ✅ | ✅ |
| **FP8 KV Cache** | NoPE FP8 量化 + RoPE BF16，V32: 656B/token | ✅ | ✅ |
| **GQA/MQA** | 分组查询注意力（h_q % h_k == 0） | ✅ | ✅ |

---

## 性能数据

| 内核 | GPU | 性能 |
|---|---|---|
| Dense MLA Decoding（内存受限） | H800 SXM5 | 3000 GB/s |
| Dense MLA Decoding（计算受限） | H800 SXM5 | 660 TFLOPS |
| Sparse MLA Decoding (FP8) | H800 SXM5 | 410 TFLOPS |
| Sparse MLA Decoding (FP8) | B200 | 350 TFLOPS（未充分优化） |
| Sparse MLA Prefill | H800 SXM5 | 640 TFLOPS |
| Sparse MLA Prefill | B200 | 1450 TFLOPS |
| Dense MHA Prefill FWD | B200 | 1460 TFLOPS |
| Dense MHA Prefill BWD | B200 | 1000 TFLOPS |

---

## 文档导航

### 📘 核心概念 [concepts/](/ai/deepseek/flash-mla/concepts/)

| 文档 | 内容 |
|---|---|
| [概述](/ai/deepseek/flash-mla/concepts/overview) | 架构总览、功能模块、支持矩阵、包结构、快速开始 |
| [MLA 解码算法](/ai/deepseek/flash-mla/concepts/mla-decoding) | 低秩 KV 压缩原理、解码计算流程、online softmax、MQA/GQA 支持 |
| [SplitKV 长序列技术](/ai/deepseek/flash-mla/concepts/splitkv) | KV 分块并行、调度元数据、两阶段执行、Ring Buffer 流水线 |
| [FP8 KV Cache 量化](/ai/deepseek/flash-mla/concepts/kv-cache-quantization) | FP8 E4M3 量化方案、V32/MODEL1 对比、反量化流程、精度设计 |
| [Hopper/Blackwell 内核](/ai/deepseek/flash-mla/concepts/hopper-blackwell-kernels) | WGMMA+TMA+DSM vs tmem+UTCMMA+UTCCP 架构差异与优化 |

### 📗 API 参考 [references/](/ai/deepseek/flash-mla/references/)

| 文档 | 内容 |
|---|---|
| [Python API](/ai/deepseek/flash-mla/references/api) | `flash_mla_with_kvcache`、`get_mla_metadata`、`flash_mla_sparse_fwd`、`flash_attn_varlen_func` 完整签名 |
| [内核架构](/ai/deepseek/flash-mla/references/kernel-architecture) | SM90/SM100 内核配置、MMA 指令、Shared Memory 布局、编译配置 |
| [KV Cache 布局](/ai/deepseek/flash-mla/references/kv-cache-layout) | V32 (656B) / MODEL1 (576B) FP8 KV cache 内存布局、分页结构、索引格式 |

### 📙 代码示例 [examples/](/ai/deepseek/flash-mla/examples/)

| 示例 | 内容 |
|---|---|
| [基础解码](/ai/deepseek/flash-mla/examples/basic-decoding) | BF16 dense 和 FP8 sparse MLA 解码的完整使用示例 |
| [性能基准测试](/ai/deepseek/flash-mla/examples/benchmark) | Benchmark 脚本用法、自定义性能测试、正确性验证 |

---

## 快速开始

### 安装

```bash
git clone https://github.com/deepseek-ai/FlashMLA.git flash-mla
cd flash-mla
git submodule update --init --recursive
pip install -v .
```

### 基本用法

```python
from flash_mla import get_mla_metadata, flash_mla_with_kvcache
import torch

# 1. 获取调度元数据
tile_scheduler_metadata, num_splits = get_mla_metadata()

# 2. 准备输入（BF16 dense 模式）
q = torch.randn(batch_size, 1, h_q, 576, dtype=torch.bfloat16, device="cuda")
# k_cache: (num_blocks, 64, h_kv, 576) BF16 paged KV cache
# block_table: (batch_size, max_blocks) int32 页表
# cache_seqlens: (batch_size,) int32 序列长度

# 3. MLA 解码
out, lse = flash_mla_with_kvcache(
    q, k_cache, block_table, cache_seqlens,
    head_dim_v=512,
    tile_scheduler_metadata=tile_scheduler_metadata,
    causal=True,
)
# out: (batch_size, 1, h_q, 512) BF16
# lse: (batch_size, h_q, 1) float32
```

---

## 支持矩阵

| 内核 | GPU | MLA 模式 | KV Cache 格式 | Q 数据类型 |
|---|---|---|---|---|
| Dense Decoding | SM90 | MQA | Paged BF16/FP16 | BF16/FP16 |
| Sparse Decoding | SM90 & SM100 | MQA | FP8（V32/MODEL1） | BF16 |
| Dense Prefill (MHA) | SM100 | MHA | —（输入 K/V） | BF16 |
| Sparse Prefill | SM90 & SM100 | MQA | —（输入 K/V） | BF16 |

> **注意**：SM100 的 Dense MHA Prefill 支持前向和反向传播（基于 CUTLASS），但反向传播当前不支持 GQA。

---

## 相关项目

| 项目 | 关系 |
|---|---|
| [DeepGEMM](/ai/deepseek/deep-gemm/) | DeepSeek 高性能 JIT GEMM 核函数库，为 LLM 训练/推理提供矩阵乘法能力，与 FlashMLA 在推理 pipeline 中协同使用——FlashMLA 负责注意力计算，DeepGEMM 负责 MLP/MoE 线性层 |
| [TileLang Kernels](/ai/deepseek/tile-kernels/) | TileLang 编写的核函数库，提供更高抽象层级的算子开发方式，作为 FlashMLA CUDA C++ 手写核函数的补充 |
| [DeepEP](/ai/deepseek/deep-ep/) | DeepSeek 专家并行通信库，提供 all-to-all 通信原语，用于 MoE 模型的分布式推理与训练 |
| [FlashAttention](https://github.com/Dao-AILab/flash-attention) | FlashMLA 灵感来源，FlashAttention 2&3 提供 IO-aware 精确注意力的 tiling 与 online softmax 基础思想 |
| [CUTLASS](https://github.com/NVIDIA/cutlass) | NVIDIA CUTLASS 库，FlashMLA SM100 Dense Prefill/Backward 基于 CUTLASS 实现 |

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
spec/facts
spec/insights
```
