# DeepSpec 核心概念

本章节深入讲解 DeepSpec 的核心概念与设计原理。

## 概念文档列表

| 文档 | 说明 |
|---|---|
| [overview](/ai/deepseek/deep-spec/concepts/overview) | DeepSpec 整体架构、三种草稿模型对比、训练与评估管线概览、包结构、快速开始 |
| [speculative-decoding-training](/ai/deepseek/deep-spec/concepts/speculative-decoding-training) | 投机解码基本原理、拒绝采样验证机制、草稿模型训练范式、置信度校准、通用生成框架 |
| [dspark-model](/ai/deepseek/deep-spec/concepts/dspark-model) | DSpark 块级锚点采样、噪声嵌入构造、Markov 头三种变体（vanilla/gated/rnn）、多任务损失设计、DFlash 变体 |
| [eagle3-model](/ai/deepseek/deep-spec/concepts/eagle3-model) | Eagle3 5层目标隐状态拼接、双维度注意力输入、TTT自回归训练、FusedLogSoftmaxLoss Triton 融合损失、KV cache 复用 |
| [training-pipeline](/ai/deepseek/deep-spec/concepts/training-pipeline) | FSDP 分片策略、BF16Optimizer 混合精度、CUDAPrefetcher、目标隐状态缓存格式、StatelessResumableDistributedSampler、原子 Checkpoint 管理 |

```{toctree}
:hidden:

dspark-model
eagle3-model
overview
speculative-decoding-training
training-pipeline
```
