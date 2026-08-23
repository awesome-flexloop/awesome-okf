# TileKernels 核心概念

本章节深入讲解 TileKernels 的核心概念与设计原理。

## 概念文档列表

| 文档 | 说明 |
|---|---|
| [overview](/ai/deepseek/tile-kernels/concepts/overview) | TileKernels 整体架构、功能模块、包结构、与 DeepGEMM/DeepEP 的协同关系 |
| [fp8-quantization](/ai/deepseek/tile-kernels/concepts/fp8-quantization) | FP8/FP4/E5M6 低精度格式、per-token/per-block/per-channel 量化粒度、SwiGLU 融合量化 |
| [moe-kernels](/ai/deepseek/tile-kernels/concepts/moe-kernels) | MoE 流水线、top2-sum gate、fused mapping、expand dispatch、reduce combine、warp 原语 |
| [mhc-multi-head-compute](/ai/deepseek/tile-kernels/concepts/mhc-multi-head-compute) | DeepSeek-V4 MHC 结构、多头残差、Sinkhorn 归一化、训练/推理双路径、梯度融合 |
| [tilelang-dsl-patterns](/ai/deepseek/tile-kernels/concepts/tilelang-dsl-patterns) | TileLang DSL 编程模式、@tilelang.jit、T.prim_func、T.Kernel、T.Parallel、warp 原语、宏复用 |
| [autograd-integration](/ai/deepseek/tile-kernels/concepts/autograd-integration) | autograd.Function 封装模式、fuse_grad_acc、main_grad、partial buffer reduce |
