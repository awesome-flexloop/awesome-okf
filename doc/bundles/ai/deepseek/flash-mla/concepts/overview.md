---
type: concept
scope: flash-mla
name: FlashMLA 概述
version: "1.0.0"
source: README.md, flash_mla/__init__.py, csrc/api/
description: FlashMLA 高效 MLA 注意力核函数库整体架构、功能模块与支持矩阵
---

# FlashMLA 概述

FlashMLA 是 DeepSeek 开源的高效 MLA（Multi-head Latent Attention）注意力核函数库，专为 NVIDIA Hopper（SM90）和 Blackwell（SM100）GPU 深度优化，为 [DeepSeek-V3](https://github.com/deepseek-ai/DeepSeek-V3)、DeepSeek-V3.2、DeepSeek-R1 等模型的推理提供高性能注意力计算。

---

## 一、核心定位

FlashMLA 的设计目标是解决大语言模型推理中的注意力计算瓶颈，特别是 MLA 架构下的解码（decoding）阶段性能问题。其核心特性包括：

1. **MLA 低秩 KV 压缩**：原生支持 MLA（Multi-head Latent Attention）的低秩 KV cache 格式，d_noPE=512/448 FP8 + d_RoPE=64 BF16
2. **SplitKV 长序列并行**：通过 SplitKV 技术将长序列 KV 沿序列维度切分，多 SM 并行处理后合并，支持 32K+ 长上下文
3. **分页 KV Cache**：Paged Attention 机制，page_block_size=64，灵活管理变长序列的 KV 内存
4. **FP8 量化 KV Cache**：NoPE 部分使用 FP8 E4M3 量化，RoPE 部分保持 BF16 精度，V32 模式每 token 仅 656 字节
5. **稀疏注意力（DSA）**：Token 级稀疏注意力支持，仅计算 top-k 相关 token，配合 FP8 KV cache 大幅提升计算效率
6. **Hopper/Blackwell 双架构优化**：SM90 使用 WGMMA+TMA+DSM，SM100 使用 Tensor Memory+UTCMMA+UTCCP

---

## 二、支持矩阵

| 内核类型 | GPU 架构 | MLA 模式 | KV Cache 格式 | 数据类型 |
|---|---|---|---|---|
| Dense Decoding | SM90 (Hopper) | MQA | Paged BF16/FP16 | BF16/FP16 |
| Sparse Decoding | SM90 & SM100 | MQA | FP8 量化 | BF16 计算/FP8 存储 |
| Dense Prefill (MHA) | SM100 (Blackwell) | MHA | 输入 K/V | BF16 |
| Sparse Prefill | SM90 & SM100 | MQA | 输入 K/V | BF16 |

**性能数据**（CUDA 12.8/12.9）：

| 内核 | GPU | 性能指标 |
|---|---|---|
| Dense MLA Decoding | H800 SXM5 | 3000 GB/s（内存受限）/ 660 TFLOPS（计算受限） |
| Sparse MLA Decoding (FP8) | H800 SXM5 | 410 TFLOPS |
| Sparse MLA Decoding (FP8) | B200 | 350 TFLOPS |
| Sparse MLA Prefill | H800 SXM5 | 640 TFLOPS |
| Sparse MLA Prefill | B200 | 1450 TFLOPS |
| Dense MHA Prefill FWD | B200 | 1460 TFLOPS |
| Dense MHA Prefill BWD | B200 | 1000 TFLOPS |

---

## 三、功能模块

FlashMLA 的功能按以下模块组织：

### 3.1 MLA Decoding（核心）

| 功能 | Python API | C++ 实现 | 说明 |
|---|---|---|---|
| Dense MLA Decode | `flash_mla_with_kvcache` | `dense_decode_fwd` | BF16 分页注意力解码 |
| Sparse MLA Decode | `flash_mla_with_kvcache` + `indices` | `sparse_decode_fwd` | FP8 KV cache 稀疏解码 |
| SplitKV 调度 | `get_mla_metadata` | `get_decoding_sched_meta` | 长序列分块调度元数据 |
| SplitKV 合并 | 内核内部自动 | `combine` | 多 split 结果合并 |

### 3.2 MLA Prefill

| 功能 | Python API | C++ 实现 | 说明 |
|---|---|---|---|
| Sparse MLA Prefill | `flash_mla_sparse_fwd` | `sparse_prefill_fwd` | Token 级稀疏预填充 |
| Dense MHA Prefill | `flash_attn_varlen_func` | `FMHACutlassSM100FwdRun` | SM100 CUTLASS 标准 MHA |
| Dense MHA Backward | autograd 自动 | `FMHACutlassSM100BwdRun` | SM100 反向传播 |

### 3.3 QKV 打包变体

| API | 说明 |
|---|---|
| `flash_attn_varlen_func` | 独立 Q/K/V 输入 |
| `flash_attn_varlen_qkvpacked_func` | QKV 打包沿最后一维 |
| `flash_attn_varlen_kvpacked_func` | KV 打包沿最后一维 |

---

## 四、Python 包结构

```
flash_mla/
├── __init__.py                    # 包入口，导出 6 个公共 API
├── flash_mla_interface.py         # Python 层接口实现
│   ├── FlashMLASchedMeta          # 调度元数据类
│   ├── get_mla_metadata()         # 获取调度元数据（延迟初始化）
│   ├── flash_mla_with_kvcache()   # 核心解码函数（dense/sparse 路由）
│   ├── flash_mla_sparse_fwd()     # 稀疏预填充函数
│   ├── _flash_attn_varlen_forward()  # Dense prefill 前向
│   ├── _flash_attn_varlen_backward() # Dense prefill 反向
│   ├── FlashAttnVarlenFunc        # autograd Function
│   ├── flash_attn_varlen_func()   # 变长注意力
│   ├── flash_attn_varlen_qkvpacked_func()  # QKV 打包版本
│   └── flash_attn_varlen_kvpacked_func()   # KV 打包版本
└── cuda*.so                       # C++ CUDA 扩展（pybind11）
```

---

## 五、C++ 源码结构

```
csrc/
├── api/                           # C++ API 层
│   ├── api.cpp                    # pybind11 模块入口
│   ├── common.h                   # Arch 检测、DISPATCH 宏、ImplBase
│   ├── dense_decode.h             # Dense decode 入口（SM90）
│   ├── sparse_decode.h            # Sparse decode 入口（SM90/SM100）
│   ├── sparse_fwd.h               # Sparse prefill 入口
│   └── dense_fwd.h                # Dense prefill 入口（SM100 CUTLASS）
├── params.h                       # 参数结构体定义
├── defines.h                      # 类型别名与基础结构体
├── utils.h                        # 工具宏与 RingBufferState
├── sm90/                          # Hopper 内核
│   ├── helpers.h                  # TMA/WGMMA/DSM helper
│   ├── decode/
│   │   ├── dense/                 # BF16 dense decode
│   │   └── sparse_fp8/            # FP8 sparse decode
│   └── prefill/
│       └── sparse/                # Sparse prefill
├── sm100/                         # Blackwell 内核
│   ├── helpers.h                  # SM100 helper
│   ├── decode/
│   │   ├── head64/                # 64 头 decode
│   │   └── head128/               # 128 头 decode（small_topk）
│   └── prefill/
│       ├── sparse/                # Sparse prefill（head64/head128）
│       ├── sparse/fwd_for_small_topk/  # 小 topk 优化
│       └── dense/                 # CUTLASS dense MHA
└── smxx/                          # 架构无关通用组件
    └── decode/
        ├── get_decoding_sched_meta/   # SplitKV 调度元数据生成
        └── combine/                   # SplitKV combine 内核
```

---

## 六、环境要求

| 要求 | 最低版本 | 说明 |
|---|---|---|
| GPU 架构 | SM90 (Hopper) 或 SM100 (Blackwell) | H100/H200/B100/B200 |
| CUDA | 12.8+ | SM100 编译需要 CUDA 12.9+ |
| PyTorch | 2.0+ | FP8 支持 |
| C++ 标准 | C++20 | — |

**编译环境变量：**
- `FLASH_MLA_DISABLE_SM90=1`：禁用 SM90 内核编译
- `FLASH_MLA_DISABLE_SM100=1`：禁用 SM100 内核编译
- `FLASH_MLA_DISABLE_FP16`：禁用 FP16 dense decode

---

## 七、快速开始

```python
from flash_mla import get_mla_metadata, flash_mla_with_kvcache
import torch

# 1. 获取调度元数据
tile_scheduler_metadata, num_splits = get_mla_metadata()

# 2. 在解码循环中调用
for step in range(max_gen_len):
    # q: (batch, 1, h_q, 576) BF16
    # k_cache: (num_blocks, 64, 1, 576) 或 FP8 紧凑布局
    # block_table: (batch, max_blocks) int32
    # cache_seqlens: (batch,) int32
    out, lse = flash_mla_with_kvcache(
        q, k_cache, block_table, cache_seqlens,
        head_dim_v=512,
        tile_scheduler_metadata=tile_scheduler_metadata,
        causal=True,
    )
```

---

## 八、相关链接

### 核心概念
- [/deepseek/flash-mla/concepts/mla-decoding](/ai/deepseek/flash-mla/concepts/mla-decoding) — MLA 解码算法原理
- [/deepseek/flash-mla/concepts/splitkv](/ai/deepseek/flash-mla/concepts/splitkv) — SplitKV 长序列技术
- [/deepseek/flash-mla/concepts/kv-cache-quantization](/ai/deepseek/flash-mla/concepts/kv-cache-quantization) — FP8 KV cache 量化
- [/deepseek/flash-mla/concepts/hopper-blackwell-kernels](/ai/deepseek/flash-mla/concepts/hopper-blackwell-kernels) — Hopper/Blackwell 内核设计

### API 参考
- [/deepseek/flash-mla/references/api](/ai/deepseek/flash-mla/references/api) — Python API 完整参考
- [/deepseek/flash-mla/references/kernel-architecture](/ai/deepseek/flash-mla/references/kernel-architecture) — 内核架构详解
- [/deepseek/flash-mla/references/kv-cache-layout](/ai/deepseek/flash-mla/references/kv-cache-layout) — KV cache 内存布局

### 相关项目
- [/deepseek/deep-gemm/](/ai/deepseek/deep-gemm/) — DeepSeek 高性能 GEMM 核函数库（JIT 编译），负责 MLP/MoE 线性层计算
- [/deepseek/tile-kernels/](/ai/deepseek/tile-kernels/) — TileLang 核函数库，作为 CUDA C++ 核函数的补充
