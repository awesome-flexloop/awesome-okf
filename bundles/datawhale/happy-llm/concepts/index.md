# 核心概念

本目录包含 Happy-LLM 教程的 7 个核心概念，按学习路径排列：从架构基础到训练方法，再到应用与前沿强化学习。

## 架构基础

* [Transformer 架构](transformer-architecture.md) — 注意力机制（Q/K/V）、Self-Attention、Multi-Head Attention、位置编码、Encoder-Decoder 结构。对应第二章。
* [预训练语言模型](pretrained-language-model.md) — Encoder-only（BERT/MLM）、Encoder-Decoder（T5）、Decoder-only（GPT/CLM）三种范式。对应第三章。

## 模型实现与训练

* [LLaMA2 手写实现](llama2-implementation.md) — RMSNorm、RoPE、GQA、SwiGLU、Transformer Block、KV Cache 的 PyTorch 手写实现。对应第五章。
* [模型训练](model-training.md) — Pretrain→SFT→RLHF 三阶段、DeepSpeed 分布式、LoRA/QLoRA 高效微调。对应第四、六章。

## 前沿技术

* [GRPO 强化学习](grpo-reinforcement-learning.md) — 组内相对优势估计、RLVR 可验证奖励、PPO 到 GRPO 的演进。对应第八章。
* [RAG 检索增强生成](rag-retrieval-augmented-generation.md) — 文档分块、Embedding、向量检索、Prompt 组装，缓解幻觉。对应第七章。
* [Agent 智能体](agent-intelligent-agent.md) — ReAct 范式、工具调用、多轮交互、自主规划。对应第七章。
