---
okf_version: "0.2"
type: bundles-index
title: "DeepSeek-AI 基础设施"
description: "DeepSeek-AI 开源大模型基础设施项目源码中文教程——MoE通信、GPU kernel优化、注意力机制、投机解码、流水线并行、负载均衡"
total_bundles: 12
---

# DeepSeek-AI 基础设施（DeepSeek-AI Infrastructure）

本分组提供 DeepSeek-AI 组织开源的大模型基础设施项目的源码级中文学习文档。这些项目是 DeepSeek-V3/R1 等模型高性能训练与推理的核心技术支撑，涵盖 MoE 专家并行通信、GPU Tensor Core 优化、MLA 注意力解码、投机解码、双向流水线并行、基于线性规划的负载均衡等关键系统层技术。

## 生态关系概览

```
┌──────────────────────────────────────────────────────────────┐
│                  🧠 DeepSeek-AI 基础设施生态                   │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                  训练与推理系统层                        │  │
│  │  DeepSpec(投机解码)  DualPipe(双向流水线)  LPLB(负载均衡)│  │
│  └───────────────────────┬────────────────────────────────┘  │
│                          │ 调用                              │
│  ┌───────────────────────▼────────────────────────────────┐  │
│  │                  通信原语层                              │  │
│  │              DeepEP (MoE专家并行通信)                    │  │
│  │     高吞吐all-to-all · 低延迟dispatch/combine · Engram  │  │
│  └───────────────────────┬────────────────────────────────┘  │
│                          │ 数据传输                          │
│  ┌───────────────────────▼────────────────────────────────┐  │
│  │                  GPU Kernel层                           │  │
│  │  DeepGEMM(GEMM/MoE)  FlashMLA(注意力)  TileKernels(DSL)│  │
│  │   FP8/FP4 GEMM · MLA解码 · MoE路由/量化/超连接          │  │
│  └───────────────────────┬────────────────────────────────┘  │
│                          │                                   │
│  ┌───────────────────────▼────────────────────────────────┐  │
│  │                  应用与论文层                            │  │
│  │  DeepSeek-OCR · awesome-deepseek-agent · Math-V2 · Engram│
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

## 知识包导航

### GPU Kernel 与计算原语

| 知识包 | 简介 |
|--------|------|
| [deep-gemm](deep-gemm/index.md) | 高性能 JIT GEMM 核函数库——FP8/FP4 量化、grouped GEMM（MoE）、MegaMoE 对称缓冲区、WGMMA/TMA/TCGen05 |
| [flash-mla](flash-mla/index.md) | MLA 注意力解码内核——低秩 KV 压缩、paged KV cache、SplitKV 长序列、Hopper/Blackwell 双架构 |
| [tile-kernels](tile-kernels/index.md) | TileLang DSL 核函数库——FP8/FP4/E5M6 量化、MoE 全管线、MHC 多头计算、Engram 条件记忆核 |

### 分布式训练与通信

| 知识包 | 简介 |
|--------|------|
| [deep-ep](deep-ep/index.md) | MoE 专家并行通信库——ElasticBuffer V2、NVSHMEM 后端、dispatch/combine、低延迟推理、JIT 内核 |
| [dual-pipe](dual-pipe/index.md) | 双向流水线并行——8 步调度算法、DualPipeV V 型调度、WeightGradStore 零气泡、P2P 批量通信 |
| [lplb](lplb/index.md) | 专家负载均衡器——LP 线性规划求解、cuSolverDx GPU 求解器、拓扑感知路由、EPLB 层次化重平衡 |

### 模型训练与推理系统

| 知识包 | 简介 |
|--------|------|
| [deep-spec](deep-spec/index.md) | 投机解码训练框架——DSpark（块级锚点+Markov 头）、Eagle3（TTT+融合损失）、FSDP+BF16 训练管线 |

### 应用模型与资源

| 知识包 | 简介 |
|--------|------|
| [deepseek-ocr](deepseek-ocr/index.md) | 文档 OCR 模型——vLLM/HF 双部署、图像/PDF 批量处理、ngram 重复抑制、deepencoder 视觉编码器 |
| [deepseek-ocr2](deepseek-ocr2/index.md) | 文档 OCR 模型 V2——deepencoderv2 增强编码器、Qwen2 D2E 模块、GPU 加速图像处理 |
| [deepseek-math-v2](deepseek-math-v2/index.md) | 数学推理模型——IMO/Putnam/CMO 竞赛数学、自验证推理管线、数学模板 prompt |
| [engram](engram/index.md) | 条件记忆机制——n-gram 哈希门控、记忆读写融合、稀疏记忆路由、长上下文扩展 |
| [awesome-deepseek-agent](awesome-deepseek-agent/index.md) | Agent 生态资源列表——28+ Agent 工具/平台集成指南（Cline/Claude Code/Cherry Studio 等） |

## 推荐学习路径

### 路径1：理解 DeepSeek-V3 核心基础设施

```
deep-gemm (GEMM/MoE计算原语)
    → flash-mla (MLA注意力解码)
    → deep-ep (MoE专家并行通信)
    → dual-pipe (双向流水线并行调度)
    → lplb (专家负载均衡)
```

### 路径2：GPU Kernel 优化学习

```
deep-gemm (JIT编译kernel架构)
    → tile-kernels (TileLang DSL kernel集合)
    → flash-mla (分代架构SM90/SM100 kernel设计)
```

### 路径3：推理加速技术

```
deep-spec (投机解码草稿模型训练评估)
    → dual-pipe (流水线并行减少气泡)
    → flash-mla (高效注意力解码)
```

## 版本信息

- **文档生成日期**：2026-08-23
- **源码来源**：https://github.com/deepseek-ai
- **许可证**：各项目采用 MIT 或其他开源许可（详见各 bundle）

```{toctree}
:hidden:
:maxdepth: 7

deep-gemm/index
flash-mla/index
tile-kernels/index
deep-ep/index
dual-pipe/index
lplb/index
deep-spec/index
deepseek-ocr/index
deepseek-ocr2/index
deepseek-math-v2/index
engram/index
awesome-deepseek-agent/index
```
