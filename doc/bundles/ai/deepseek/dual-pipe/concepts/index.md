# DualPipe 核心概念

- [双向流水线并行概述](/ai/deepseek/dual-pipe/concepts/overview) — DualPipe 核心思想、与传统 1F1B 的对比、双向调度原理
- [DualPipe 算法调度](/ai/deepseek/dual-pipe/concepts/dualpipe-algorithm) — 8 步调度算法详解、chunk 流转、phase 翻转机制
- [零气泡权重梯度优化](/ai/deepseek/dual-pipe/concepts/zero-bubble) — WeightGradStore 延迟执行机制，消除权重计算气泡
- [P2P 通信模式](/ai/deepseek/dual-pipe/concepts/communication-pattern) — 全局 tensor shape 配置、批量通信、rank 映射
- [DualPipeV 与 DualPipe 对比](/ai/deepseek/dual-pipe/concepts/dualpipev-comparison) — V 型调度 vs 对称双向调度的差异与选择
- [自定义模块集成](/ai/deepseek/dual-pipe/concepts/custom-module-integration) — 如何编写 PipelineStage、overlapped_forward_backward 接口、WeightGradStore 集成
