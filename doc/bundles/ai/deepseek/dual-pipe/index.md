---
type: bundle
scope: dual-pipe
name: DualPipe
version: "1.0.0"
okf_version: "0.2"
source: external/libs/ai/deepseek-ai/DualPipe/
description: DualPipe 双向流水线并行库，DeepSeek-V3 提出的计算-通信完全重叠的流水线并行算法
tags:
  - pipeline-parallelism
  - distributed-training
  - zero-bubble
  - deepseek
  - dualpipe
prerequisites:
  - /pydata/pytorch/distributed/basics
  - /ai-agent/llm-training/pipeline-parallelism
---

# DualPipe

DualPipe 是 DeepSeek-V3 提出的双向流水线并行（Bidirectional Pipeline Parallelism）算法实现。它通过让每个 GPU 同时持有两个对称 pipeline stage，实现前向/反向计算与通信的完全重叠，大幅减少甚至消除传统流水线并行中的气泡问题。

## 核心特性

- **双向对称调度**：两个方向的 micro-batch 在同一组 GPU 上双向流动，计算与通信完全重叠
- **零气泡优化**：WeightGradStore 延迟权重梯度计算到通信阶段，消除权重更新气泡
- **两种调度模式**：DualPipe（对称双向）和 DualPipeV（V 型调度，节省 GPU）
- **自定义前后向重叠**：通过 `overlapped_forward_backward` 类方法自定义计算重叠策略
- **拓扑感知 rank 映射**：支持自定义 rank_mapping，适配 NVLink/NVSwitch 拓扑
- **纯 PyTorch 实现**：无需自定义 CUDA kernel，基于 `torch.distributed` P2P 通信

## 快速导航

### [核心概念](/ai/deepseek/dual-pipe/concepts)

| 概念 | 说明 |
|------|------|
| [双向流水线并行概述](/ai/deepseek/dual-pipe/concepts/overview) | 核心思想、与 1F1B 对比、为什么双向能消除气泡 |
| [算法调度详解](/ai/deepseek/dual-pipe/concepts/dualpipe-algorithm) | 8 步调度流程、chunk 流转、phase 翻转机制 |
| [零气泡优化](/ai/deepseek/dual-pipe/concepts/zero-bubble) | WeightGradStore 延迟 dW 计算机制 |
| [P2P 通信模式](/ai/deepseek/dual-pipe/concepts/communication-pattern) | 批量通信、peer rank 计算、内存管理 |
| [DualPipe vs DualPipeV](/ai/deepseek/dual-pipe/concepts/dualpipev-comparison) | 两种调度的差异与选择 |
| [自定义模块集成](/ai/deepseek/dual-pipe/concepts/custom-module-integration) | PipelineStage 编写、overlapped_forward_backward 接口 |

### [API 参考](/ai/deepseek/dual-pipe/references)

- [公开 API](/ai/deepseek/dual-pipe/references/api) — DualPipe、DualPipeV、WeightGradStore、通信配置函数
- [内部模块](/ai/deepseek/dual-pipe/references/internal-modules) — 内部方法签名与通信工具

### [示例](/ai/deepseek/dual-pipe/examples)

- [基础训练](/ai/deepseek/dual-pipe/examples/basic-training) — 完整训练脚本
- [推理示例](/ai/deepseek/dual-pipe/examples/inference) — DualPipeV 推理

## 安装

```bash
cd external/libs/ai/deepseek-ai/DualPipe
pip install -e .
```

## 最小使用示例

```python
import torch.distributed as dist
from dualpipe import DualPipe, set_p2p_tensor_shapes, set_p2p_tensor_dtype

# 初始化分布式
dist.init_process_group("nccl")

# 创建模型（每个 rank 两个 stage）
model = DualPipe((stage0, stage1))

# 配置 P2P 通信
set_p2p_tensor_shapes([(micro_bsz, hidden_size)])
set_p2p_tensor_dtype(torch.bfloat16)

# 训练步
loss, _ = model.step(
    inputs, num_chunks=8, criterion=criterion, labels=labels
)
```

## 与其他 DeepSeek 组件的关系

- [DeepEP](/ai/deepseek/deep-ep)：MoE 专家并行通信库，与 DualPipe 配合实现 EP+PP 混合并行
- [LPLB](/ai/deepseek/lplb)：专家负载均衡器，决定 EP 路由策略
- [DeepGEMM](/ai/deepseek/deep-gemm)：MoE 分组 GEMM 内核，为 DualPipe stage 内的计算提供高性能 GEMM

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
spec/facts
spec/insights
```
