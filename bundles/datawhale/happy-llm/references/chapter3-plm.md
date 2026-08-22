---
type: reference
title: "第三章 预训练语言模型"
bundle: /datawhale/happy-llm
description: "Encoder-only（BERT）、Encoder-Decoder（T5）、Decoder-only（GPT）三种架构范式对比"
source: https://github.com/datawhalechina/happy-llm/blob/main/docs/chapter3/第三章%20预训练语言模型.md
path: docs/chapter3/第三章 预训练语言模型.md
tags: [plm, bert, gpt, t5, pretrain]
status: stable
---

# 第三章 预训练语言模型

## 信源信息

- **文件路径**：`docs/chapter3/第三章 预训练语言模型.md`
- **GitHub**：https://github.com/datawhalechina/happy-llm/blob/main/docs/chapter3/第三章%20预训练语言模型.md

## 内容概要

本章系统讲解 Transformer 时代的三种预训练模型架构：

- **3.1 Encoder-only PLM**：BERT（Bidirectional Encoder Representations from Transformers）
  - 架构：Transformer Encoder 堆叠，双向自注意力
  - 预训练任务：MLM（掩码语言模型）+ NSP（下一句预测）
  - 分词：WordPiece 子词切分
  - 激活函数：GELU
  - 规模：BERT-base（12层/768维/110M）、BERT-large（24层/1024维/340M）
  - 能力偏向：自然语言理解（NLU）

- **3.2 Encoder-Decoder PLM**：T5 等
  - 架构：同时保留 Encoder 和 Decoder
  - 预训练任务：Span Corruption
  - 能力偏向：Seq2Seq 任务（翻译、摘要）

- **3.3 Decoder-only PLM**：GPT 系列
  - 架构：Transformer Decoder 堆叠，因果掩码
  - 预训练任务：CLM（因果语言模型/自回归）
  - 能力偏向：自然语言生成（NLG），Scaling Law 效应显著
  - 现代 LLM 的主流架构选择

## 对应概念

- [预训练语言模型](../concepts/pretrained-language-model.md)
- [Transformer 架构](../concepts/transformer-architecture.md)
