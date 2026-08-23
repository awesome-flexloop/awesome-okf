# FlashMLA 核心概念

本章节深入讲解 FlashMLA 的核心概念与设计原理。

## 概念文档列表

| 文档 | 说明 |
|---|---|
| [overview](/ai/deepseek/flash-mla/concepts/overview) | FlashMLA 整体架构、功能模块、支持矩阵、包结构与快速开始 |
| [mla-decoding](/ai/deepseek/flash-mla/concepts/mla-decoding) | MLA（Multi-head Latent Attention）低秩 KV 压缩原理、解码计算流程、online softmax、MQA/GQA 支持 |
| [splitkv](/ai/deepseek/flash-mla/concepts/splitkv) | SplitKV 长序列分块并行技术、调度元数据、两阶段执行、Ring Buffer 流水线 |
| [kv-cache-quantization](/ai/deepseek/flash-mla/concepts/kv-cache-quantization) | FP8 E4M3 KV cache 量化方案、V32/MODEL1 两种模式对比、反量化流程、精度设计 |
| [hopper-blackwell-kernels](/ai/deepseek/flash-mla/concepts/hopper-blackwell-kernels) | Hopper (SM90) WGMMA+TMA+DSM 与 Blackwell (SM100) tmem+UTCMMA+UTCCP 内核设计差异 |
