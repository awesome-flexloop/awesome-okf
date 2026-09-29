---
type: concept
title: "模型训练"
bundle: /datawhale/happy-llm
description: "LLM 三阶段训练流程（Pretrain→SFT→RLHF）与工业级训练实践：Transformers、DeepSpeed、LoRA/QLoRA"
sources:
  - https://github.com/datawhalechina/happy-llm/blob/main/docs/chapter4/第四章%20大语言模型.md
  - https://github.com/datawhalechina/happy-llm/blob/main/docs/chapter6/第六章%20大模型训练流程实践.md
related:
  - /datawhale/happy-llm/concepts/pretrained-language-model
  - /datawhale/happy-llm/concepts/llama2-implementation
  - /datawhale/happy-llm/concepts/grpo-reinforcement-learning
  - /datawhale/happy-llm/examples/llama2-pretrain-sft
tags: [pretrain, sft, rlhf, lora, deepspeed, transformers]
status: stable
---

# 模型训练

## 核心理解

LLM 的训练分为三个阶段：预训练（Pretraining）赋予模型语言能力和世界知识，有监督微调（SFT）教会模型遵循指令，强化学习（RLHF/GRPO）对齐人类偏好。第六章在第五章手写实现的基础上，引入 HuggingFace Transformers + DeepSpeed + PEFT 等工业级框架，展示高效训练实践。

## 三阶段训练流程

### 第一阶段：预训练（Pretraining）

- **任务**：因果语言建模（CLM）——根据上文预测下一个 token
- **数据**：数 T token 的海量无监督语料（网页、书籍、代码等）
- **目标**：让模型学会语言规律、事实知识和基本推理能力
- **产出**：Base 模型——会"续写"但不会"对话"
- **成本**：最高，需要多卡分布式集群训练数周至数月

### 第二阶段：有监督微调（Supervised Fine-Tuning, SFT）

- **任务**：在指令-回答对上训练，学习人类期望的回复格式
- **数据**：数万至数百万条高质量指令数据（人工标注或合成）
- **目标**：将 Base 模型转化为 Chat 模型，理解并遵循指令
- **方法**：全参数微调或高效参数微调（LoRA/QLoRA）
- **产出**：SFT 模型——能对话但可能不够安全/有用

### 第三阶段：强化学习对齐

- **传统方法**：RLHF（Reinforcement Learning from Human Feedback）
  - 训练奖励模型（RM）学习人类偏好
  - 使用 PPO 算法优化策略
- **现代方法**：GRPO（见 [GRPO 强化学习](grpo-reinforcement-learning.md)）
  - 省去 Value Model，使用组内相对优势
  - DeepSeekMath/DeepSeek-R1 等模型采用
- **目标**：对齐人类价值观，提升有用性、安全性和推理能力

## 工业级训练框架

### HuggingFace Transformers

- **AutoModel/AutoConfig**：一键加载数百种预训练模型架构
- **Trainer 类**：封装训练循环、分布式训练、日志记录、检查点保存
- **HuggingFace Hub**：共享预训练模型、数据集和评估指标
- 新模型（DeepSeek、Qwen 等）通常首发即支持 Transformers

### DeepSpeed 分布式训练

- **ZeRO（Zero Redundancy Optimizer）**：将优化器状态、梯度、参数分片到多 GPU
  - ZeRO-1：分片优化器状态
  - ZeRO-2：分片优化器状态 + 梯度（第六章使用）
  - ZeRO-3：分片所有内容（包括模型参数）
- 通过 JSON 配置文件（`ds_config_zero2.json`）控制分片策略
- 与 Transformers Trainer 无缝集成

### PEFT 高效微调

**LoRA（Low-Rank Adaptation）**：
- 在原始权重旁添加低秩分解矩阵 `ΔW = BA`（B∈R^{d×r}, A∈R^{r×k}, r≪d）
- 仅训练低秩矩阵，原始权重冻结
- 参数量减少至 0.1%-1%，显存大幅降低
- 推理时可将 LoRA 权重合并回原始权重，无额外延迟

**QLoRA**：
- LoRA + 4-bit 量化（NF4）
- 基座模型以 4-bit 量化加载，仅 LoRA 参数为 fp16
- 单卡 24GB 显存可微调 65B 模型
- 使用 bitsandbytes 库实现量化

## 手写 vs 框架

第五章手写实现让读者理解每个张量运算，第六章框架实践让读者掌握工业级训练：

| 维度 | 第五章（手写） | 第六章（框架） |
|------|--------------|--------------|
| 模型定义 | 纯 PyTorch 手写 LLaMA2 | AutoModel 加载预训练模型 |
| 分布式 | 基础 DDP | DeepSpeed ZeRO-2 |
| 微调 | 全参数 SFT | 全参数 SFT + LoRA/QLoRA |
| 兼容性 | 自定义格式 | HuggingFace 标准格式 |
| 适用场景 | 学习原理 | 生产训练 |

## 在 Happy-LLM 中的位置

第四章从理论层面讲解三阶段训练流程，第六章从工程层面使用 Transformers + DeepSpeed + PEFT 实践。第五章的手写实现是两者之间的桥梁——理解了手写代码，使用框架时才能知其所以然。

## 延伸阅读

- [LLaMA2 手写实现](llama2-implementation.md)——手写训练全流程
- [GRPO 强化学习](grpo-reinforcement-learning.md)——第三阶段训练的现代方法
- [LLaMA2 模型构建与预训练示例](../examples/llama2-pretrain-sft.md)——第五章和第六章代码实践
