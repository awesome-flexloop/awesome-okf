---
type: bundle
okf_version: "0.2"
scope: deep-gemm
name: DeepGEMM Wiki
version: "2.6.1"
source: https://github.com/deepseek-ai/DeepGEMM
description: DeepGEMM - DeepSeek 高性能 JIT GEMM 核函数库文档
---

# DeepGEMM

**DeepGEMM** 是 DeepSeek 开源的高性能矩阵乘法（GEMM）核函数库，专为 NVIDIA Hopper（SM90）和 Blackwell（SM100）GPU 架构设计，采用运行时 JIT 编译技术动态生成最优 CUDA 核函数，为大语言模型（LLM）训练与推理——特别是 MoE（Mixture of Experts）场景——提供极致的矩阵计算性能。

- **版本**：2.6.1
- **开源仓库**：[deepseek-ai/DeepGEMM](https://github.com/deepseek-ai/DeepGEMM)
- **支持架构**：Hopper (H100/H200)、Blackwell (B100/B200)
- **最低 CUDA 版本**：12.1（TMA 支持）
- **最低 PyTorch 版本**：2.1（FP8 支持）

---

## 核心能力

| 能力 | 说明 | SM90 | SM100 |
|---|---|---|---|
| **FP8 GEMM** | E4M3 精度矩阵乘，per-block 缩放因子 | ✅ 1D1D/1D2D | ✅ 1D1D |
| **FP4 GEMM** | E2M1 精度矩阵乘（nibble packing） | ❌ | ✅ 1D1D |
| **BF16 GEMM** | BF16 精度矩阵乘 | ✅ | ✅ |
| **M-Grouped GEMM** | MoE 前向分组 GEMM（连续/掩码布局） | ✅ | ✅ |
| **K-Grouped GEMM** | MoE 反向分组 GEMM | ✅ | ✅ |
| **MegaMoE** | 对称缓冲区融合 MoE（零拷贝通信） | ❌ | ✅ |
| **MQA Logits** | 多查询注意力 logits 计算 | ✅ | ✅ |
| **Paged MQA** | 分页 KV cache 注意力 | ✅ | ✅ |
| **Einsum** | 批量 GEMM / 注意力投影 | ✅ | ✅ |
| **Hyperconnection** | TF32 超连接 prenorm GEMM | ✅ | ✅ |
| **JIT 编译** | 运行时 NVCC/NVRTC 编译+缓存 | ✅ | ✅ |
| **cuBLASLt 回退** | 所有架构可用的兜底路径 | ✅ | ✅ |

---

## 文档导航

### 📘 核心概念 [concepts/](/ai/deepseek/deep-gemm/concepts/)

| 文档 | 内容 |
|---|---|
| [概述](/ai/deepseek/deep-gemm/concepts/overview) | 架构总览、功能模块、支持矩阵、包结构 |
| [FP8/FP4 GEMM](/ai/deepseek/deep-gemm/concepts/fp8-gemm) | 低精度方案、per-block 缩放因子、UE8M0 编码、量化工具 |
| [分组 GEMM 与 MoE 并行](/ai/deepseek/deep-gemm/concepts/grouped-gemm) | M/K-grouped GEMM、连续/掩码布局、PSUM 布局 |
| [JIT 内核编译系统](/ai/deepseek/deep-gemm/concepts/jit-kernel-compilation) | NVCC/NVRTC 编译、两级缓存、CRTP 启动、内核加载 |
| [MegaMoE 融合运算](/ai/deepseek/deep-gemm/concepts/moe-operations) | 对称环形缓冲区、零拷贝通信、权重交错、双精度方案 |
| [性能优化技术](/ai/deepseek/deep-gemm/concepts/performance-optimization) | TMA、WGMMA/TCGen05、PDL、Cluster、SM 控制、Swizzle |

### 📗 API 参考 [references/](/ai/deepseek/deep-gemm/references/)

| 文档 | 内容 |
|---|---|
| [公共 API](/ai/deepseek/deep-gemm/references/api) | GEMM、Attention、Einsum、Hyperconnection、Layout 核函数完整签名 |
| [JIT 编译系统](/ai/deepseek/deep-gemm/references/jit-system) | 编译器、设备运行时、内核运行时、Include 解析、句柄管理 |
| [MegaMoE API](/ai/deepseek/deep-gemm/references/mega-moe) | SymmBuffer、权重变换、fp8_fp4_mega_moe、bf16_mega_moe |
| [运行时配置](/ai/deepseek/deep-gemm/references/runtime-config) | SM/TC/PDL 配置、编译维度、Block 对齐、环境变量 |

### 📙 代码示例 [examples/](/ai/deepseek/deep-gemm/examples/)

| 示例 | 内容 |
|---|---|
| [基础 GEMM](/ai/deepseek/deep-gemm/examples/basic-gemm) | FP8/BF16 GEMM 调用、量化、性能基准测试 |
| [MoE 前向](/ai/deepseek/deep-gemm/examples/moe-forward) | M-grouped GEMM MoE、MegaMoE 单/多 rank 用法 |
| [性能调优](/ai/deepseek/deep-gemm/examples/tuning) | SM/TC 配置、JIT 预热、benchmark、问题排查 |

---

## 快速开始

```python
import torch
import deep_gemm

# 要求 Hopper (SM90) 或 Blackwell (SM100)
assert torch.cuda.get_device_capability()[0] >= 9

# BF16 GEMM
M, N, K = 4096, 4096, 8192
a = torch.randn(M, K, device='cuda', dtype=torch.bfloat16)
b = torch.randn(N, K, device='cuda', dtype=torch.bfloat16)
d = torch.empty(M, N, device='cuda', dtype=torch.bfloat16)
deep_gemm.bf16_gemm_nt(a, b, d)  # D = A @ B^T

# FP8 GEMM
from deep_gemm import per_block_cast_to_fp8
a_fp8, a_sf = per_block_cast_to_fp8(a.float())
b_fp8, b_sf = per_block_cast_to_fp8(b.float())
deep_gemm.fp8_gemm_nt((a_fp8, a_sf), (b_fp8, b_sf), d)
```

---

## 相关项目

| 项目 | 关系 |
|---|---|
| [DeepEP](/ai/deepseek/deep-ep/) | DeepSeek 专家并行（EP）通信库，提供 all-to-all 等通信原语，与 DeepGEMM 分组 GEMM/MegaMoE 协同使用 |
| [TileLang Kernels](/ai/deepseek/tile-kernels/) | TileLang 编写的核函数库（如 SwiGLU+weight 到 FP8 的融合算子），作为 DeepGEMM 的补充 |

```{toctree}
:hidden:

concepts/index
examples/index
references/index
spec/facts
spec/insights
```
