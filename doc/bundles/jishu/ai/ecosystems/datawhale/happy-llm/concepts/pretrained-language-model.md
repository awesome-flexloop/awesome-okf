---
type: concept
title: "预训练语言模型"
bundle: /datawhale/happy-llm
description: "基于 Transformer 的预训练-微调范式，分化为 Encoder-only、Encoder-Decoder、Decoder-only 三种架构"
sources: https://github.com/datawhalechina/happy-llm/blob/main/docs/chapter3/第三章%20预训练语言模型.md
related:
  - /datawhale/happy-llm/concepts/transformer-architecture
  - /datawhale/happy-llm/concepts/llama2-implementation
  - /datawhale/happy-llm/concepts/model-training
tags: [plm, bert, gpt, pretrain, finetune]
status: stable
---

# 预训练语言模型

## 核心理解

预训练语言模型（Pre-trained Language Model，PLM）是在大规模无监督语料上通过自监督任务预训练，再针对下游任务微调的 NLP 模型范式。Transformer 问世后，PLM 沿 Encoder 和 Decoder 的不同组合分化为三条技术路线，最终 Decoder-only 路线演化为现代 LLM。

## 三种架构范式

### Encoder-only（BERT 代表）

- **架构**：仅堆叠 Transformer Encoder，双向自注意力可同时看到左右上下文
- **预训练任务**：
  - **MLM（掩码语言模型）**：随机遮蔽 15% token，根据上下文预测被遮蔽词，模拟"完形填空"
  - **NSP（下一句预测）**：判断两个句子是否连续（BERT 原始设计，后续模型多弃用）
- **分词**：WordPiece 子词切分（如 "playing" → ["play", "##ing"]）
- **激活函数**：GELU（高斯误差线性单元）
- **能力偏向**：自然语言理解（NLU）——分类、NER、问答等
- **代表模型**：BERT-base（12层/768维/110M）、BERT-large（24层/1024维/340M）、RoBERTa、MacBERT

### Encoder-Decoder（T5 代表）

- **架构**：同时保留 Encoder 和 Decoder，Encoder 双向编码输入，Decoder 单向生成输出
- **预训练任务**：Span Corruption（遮蔽连续文本段并生成）
- **能力偏向**：Seq2Seq 任务——翻译、摘要、文本生成
- **代表模型**：T5、BART

### Decoder-only（GPT 代表）

- **架构**：仅堆叠 Transformer Decoder，使用因果掩码（Causal Mask）确保每个位置只能看到左侧上下文
- **预训练任务**：CLM（因果语言模型/自回归语言模型）——根据上文预测下一个 token
- **能力偏向**：自然语言生成（NLG），Scaling Law 效应最显著
- **代表模型**：GPT 系列、LLaMA、Qwen、DeepSeek——**现代 LLM 的主流架构**

## 预训练-微调范式

PLM 的核心思想是**预训练与微调分离**：

1. **预训练阶段**：在海量无监督语料（数亿～数千亿 token）上训练，学习语言知识和世界知识，成本高但只需一次
2. **微调阶段**：在下游任务标注数据上继续训练，成本低，一个预训练模型可适配多种任务

这一范式在 BERT 发布后成为 NLP 主流，直到 LLM 时代被 Prompt Engineering 和上下文学习（ICL）部分替代。

## 从 PLM 到 LLM

PLM 是 LLM 的直接前身。LLM 在 Decoder-only PLM 基础上，通过：
- 大规模扩大参数（从亿级到千亿级）
- 扩大预训练数据（从 GB 级到 TB 级）
- 引入指令微调（SFT）和人类反馈强化学习（RLHF）

实现了涌现能力、上下文学习、指令遵循等传统 PLM 不具备的能力。

## 在 Happy-LLM 中的位置

第三章系统对比三种架构的设计选择、预训练任务和优劣势，建立"架构选择决定能力偏向"的认知。这是理解第四章"为什么 LLM 选择 Decoder-only"和第五章"LLaMA2 如何在 Decoder-only 上优化"的必要前提。

## 延伸阅读

- [Transformer 架构](transformer-architecture.md)——PLM 的基础架构
- [LLaMA2 手写实现](llama2-implementation.md)——Decoder-only 路线的现代集大成者
- [模型训练](model-training.md)——预训练与微调的工程实践
