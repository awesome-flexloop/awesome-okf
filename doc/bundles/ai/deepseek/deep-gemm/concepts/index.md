# DeepGEMM 核心概念

本章节深入讲解 DeepGEMM 的核心概念与设计原理。

## 概念文档列表

| 文档 | 说明 |
|---|---|
| [overview](/ai/deepseek/deep-gemm/concepts/overview) | DeepGEMM 整体架构、功能模块、支持矩阵、包结构 |
| [fp8-gemm](/ai/deepseek/deep-gemm/concepts/fp8-gemm) | FP8/FP4 低精度方案、per-block 缩放因子、UE8M0 编码、量化工具 |
| [grouped-gemm](/ai/deepseek/deep-gemm/concepts/grouped-gemm) | M-grouped/K-grouped 分组 GEMM、MoE 前向/反向、PSUM 布局 |
| [jit-kernel-compilation](/ai/deepseek/deep-gemm/concepts/jit-kernel-compilation) | JIT 编译系统、NVCC/NVRTC、两级缓存、内核加载、CRTP 启动模式 |
| [moe-operations](/ai/deepseek/deep-gemm/concepts/moe-operations) | MegaMoE 对称缓冲区融合核、环形通信、权重交错、双精度方案 |
| [performance-optimization](/ai/deepseek/deep-gemm/concepts/performance-optimization) | TMA、WGMMA/TCGen05、PDL、Thread Block Cluster、SM 控制、Swizzle、Pipeline |

```{toctree}
:maxdepth: 7

fp8-gemm
grouped-gemm
jit-kernel-compilation
moe-operations
overview
performance-optimization
```
