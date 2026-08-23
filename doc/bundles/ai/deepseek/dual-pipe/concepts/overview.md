---
type: concept
scope: dual-pipe
name: 双向流水线并行概述
version: "1.0.0"
source: external/libs/ai/deepseek-ai/DualPipe/dualpipe/dualpipe.py, dualpipe/dualpipev.py
prerequisites:
  - /pydata/pytorch/distributed/basics
  - /ai-agent/llm-training/pipeline-parallelism
description: 解释双向流水线并行（DualPipe）的核心思想，对比传统 1F1B 流水线，说明为何双向调度能消除气泡
---

# 双向流水线并行概述

## 为什么需要流水线并行

当模型太大无法放入单个 GPU 显存时，流水线并行（Pipeline Parallelism, PP）将模型按层切分到多个 GPU 上。每个 GPU 只持有模型的一部分层（一个 stage），微批次数据依次流过各个 stage。

传统流水线并行（如 GPipe、1F1B）存在"流水线气泡"问题：在流水线启动和排空阶段，部分 GPU 处于空闲等待状态。

## 传统 1F1B 的气泡问题

以 4 个 stage、4 个微批次为例，1F1B 调度如下（F=前向，B=反向，W=权重更新，_=空闲）：

```
GPU0: F F F F B B B B
GPU1: _ F F F B B B _
GPU2: _ _ F F B B _ _
GPU3: _ _ _ F B _ _ _
```

气泡率 = (空闲时间) / (总时间) ≈ (pp_size - 1) / (num_chunks + pp_size - 1)

当 pp_size 很大时，气泡严重影响效率。

## DualPipe 的核心思想：双向对称调度

DualPipe 的关键创新是让每个 GPU 同时持有两个 stage，分别处理来自两个方向的微批次：

```
Phase 0: GPU0(s0) → GPU1(s1) → ... → GPU(N-1)(sN-1)
Phase 1: GPU0(sN-1) ← GPU1(sN-2) ← ... ← GPU(N-1)(s0)
```

每个 GPU 同时计算：
- 一个方向的前向传播
- 另一个方向的反向传播
- 或者同时进行两个方向的通信

这样计算和通信在时间上完全重叠，极大消除了气泡。

## 双向调度的直观理解

想象一条单向高速公路，车只能朝一个方向开，会有堵车（气泡）。DualPipe 修成双向车道，两个方向的车流同时使用路面资源（GPU 计算单元），路面利用率大幅提升。

每个 GPU 就像一个双向收费站，同时处理来和往的车辆（micro-batch），不会有单向空等的情况。

## DualPipe 与 DualPipeV

DualPipe 提供两种调度模式：

| 模式 | GPU 数量 | Stage 分配方式 | 特点 |
|------|---------|---------------|------|
| DualPipe | 2×pp_size | GPU i 持有 stage(i) 和 stage(pp_size-1-i) | 对称双向，气泡最小 |
| DualPipeV | pp_size | GPU i 持有 stage(i) 和 stage(2pp_size-1-i) | V 型连接，节省 GPU |

详见 [DualPipe 算法调度](/ai/deepseek/dual-pipe/concepts/dualpipe-algorithm) 和 [DualPipeV 与 DualPipe 对比](/ai/deepseek/dual-pipe/concepts/dualpipev-comparison)。

## 适用场景

DualPipe 适用于：
- 大规模 MoE 模型训练（DeepSeek-V3 使用双向流水线+EP并行）
- 多节点分布式训练（跨节点 PP，减少通信空闲时间）
- 需要最大化 GPU 利用率的大模型训练场景
