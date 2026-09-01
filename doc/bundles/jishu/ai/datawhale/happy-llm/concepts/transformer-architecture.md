---
type: concept
title: "Transformer 架构"
bundle: /datawhale/happy-llm
description: "基于自注意力机制的 Encoder-Decoder 神经网络架构，LLM 的核心基础"
sources: https://github.com/datawhalechina/happy-llm/blob/main/docs/chapter2/第二章%20Transformer架构.md
related:
  - /datawhale/happy-llm/concepts/pretrained-language-model
  - /datawhale/happy-llm/concepts/llama2-implementation
  - /datawhale/happy-llm/examples/transformer-handwritten
tags: [architecture, attention, transformer, nlp]
status: stable
---

# Transformer 架构

## 核心理解

Transformer 是 Vaswani 等人在 2017 年论文《Attention is All You Need》中提出的神经网络架构，完全基于注意力机制构建，摒弃了 RNN/LSTM 的序列依赖结构，是现代大语言模型（LLM）的架构基石。

Transformer 解决了 RNN/LSTM 的两个根本缺陷：

1. **无法并行计算**：RNN 必须按序列依次处理每个 token，限制了 GPU 并行能力
2. **长距离依赖捕捉困难**：序列中距离越远的 token 之间关系越难捕捉，LSTM 门机制仅部分缓解

## 注意力机制

注意力机制的三个核心变量：

- **Query（查询值 Q）**：当前位置的查询向量，表示"我在找什么"
- **Key（键值 K）**：所有位置的键向量，表示"我能提供什么"
- **Value（真值 V）**：所有位置的值向量，表示"我实际包含的信息"

注意力计算通过 Query 与 Key 的点积衡量相关性，经 Softmax 归一化后对 Value 加权求和：

```
Attention(Q, K, V) = softmax(QK^T / √d_k) · V
```

缩放因子 `√d_k` 防止点积过大导致 Softmax 梯度消失。

## Multi-Head Attention

多头注意力将 Q/K/V 投影到多个子空间并行计算注意力，再拼接结果：

```
MultiHead(Q, K, V) = Concat(head_1, ..., head_h) · W_O
where head_i = Attention(QW_Q^i, KW_K^i, VW_V^i)
```

多头机制允许模型同时关注不同位置的不同表示子空间的信息。

## Encoder-Decoder 结构

Transformer 由 Encoder（编码器）和 Decoder（解码器）两部分组成：

**Encoder**（每层包含）：
- Multi-Head Self-Attention（自注意力，所有位置可互相注意）
- Feed-Forward Network（FFN，两层线性变换 + ReLU）
- 残差连接 + LayerNorm

**Decoder**（每层包含）：
- Masked Multi-Head Self-Attention（带掩码，只能注意已生成位置）
- Encoder-Decoder Attention（Q 来自 Decoder，K/V 来自 Encoder 输出）
- Feed-Forward Network
- 残差连接 + LayerNorm

## 位置编码

由于注意力机制本身不包含序列顺序信息，Transformer 使用正弦位置编码注入位置信息：

```
PE(pos, 2i)   = sin(pos / 10000^(2i/d_model))
PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
```

后续 BERT 使用可学习的相对位置编码，LLaMA 等现代 LLM 使用 RoPE 旋转位置编码。

## 在 Happy-LLM 中的位置

第二章从注意力机制的直觉解释出发，逐步推导 Self-Attention、Multi-Head Attention、位置编码、Encoder-Decoder 的完整结构，并提供 `code/transformer.py` 的纯 PyTorch 手写实现。这是后续理解 BERT、GPT、LLaMA2 等所有模型的基础。

## 延伸阅读

- [预训练语言模型](pretrained-language-model.md)——Transformer 如何分化为 Encoder-only/Encoder-Decoder/Decoder-only 三种范式
- [LLaMA2 手写实现](llama2-implementation.md)——现代 LLM 如何在 Transformer Decoder 基础上优化
- [手写 Transformer 示例](../examples/transformer-handwritten.md)——第二章代码实践
