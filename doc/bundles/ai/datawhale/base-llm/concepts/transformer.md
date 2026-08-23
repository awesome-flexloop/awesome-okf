---
type: concept
title: "Transformer 架构"
bundle: "/datawhale/base-llm"
description: "从 Seq2Seq 信息瓶颈到注意力机制，深入自注意力（Q/K/V）、多头注意力、位置编码、Encoder-Decoder 完整架构，Transformer 是大模型的架构基石。"
sources:
  - https://github.com/datawhalechina/base-llm/blob/main/docs/chapter4/10_seq2seq.md
  - https://github.com/datawhalechina/base-llm/blob/main/docs/chapter4/11_attention.md
  - https://github.com/datawhalechina/base-llm/blob/main/docs/chapter4/12_transformer.md
related:
  - /datawhale/base-llm/concepts/word-vectors-rnn
  - /datawhale/base-llm/concepts/pretrained-models
  - /datawhale/base-llm/concepts/llm-architecture
---

# Transformer 架构

## 核心理解

2017 年 Google 论文《Attention Is All You Need》提出的 Transformer，彻底抛弃了 RNN 的顺序计算，以**自注意力机制**为核心，实现了并行计算和全局依赖建模。它不仅是 NLP 领域的划时代架构，更是后续 BERT、GPT、Llama 等几乎所有大语言模型的基础。本概念是整个教程的**架构枢纽**。

## Seq2Seq 与信息瓶颈

### Seq2Seq 架构

Seq2Seq（Sequence-to-Sequence）由 Encoder 和 Decoder 组成：
- **Encoder**：将输入序列编码为固定维度的**上下文向量 c**。
- **Decoder**：以 c 为初始状态，自回归生成输出序列。

### 信息瓶颈问题

无论输入序列多长，Encoder 最终都需将全部信息压缩到固定维度的上下文向量 c 中。当序列较长时，c 成为信息瓶颈，导致：
- 长距离信息丢失
- Decoder 在生成每个词时无法区分输入中各部分的重要性

Attention 机制正是为解决这一瓶颈而生。

## 注意力机制（Attention）

### Q/K/V 范式

注意力机制的本质是**加权求和**，通过 Query（查询）、Key（键）、Value（值）三元组实现：

1. **计算注意力分数**：$score(q, k) = q \cdot k$（点积）
2. **缩放与归一化**：$\alpha = \text{softmax}(score / \sqrt{d_k})$
3. **加权求和**：$output = \sum \alpha_i \cdot v_i$

### Bahdanau vs Luong

- **Bahdanau Attention（加性注意力）**：用前馈网络计算分数，$score = v^T \tanh(W_1 h + W_2 s)$。
- **Luong Attention（乘性注意力）**：直接用点积计算，更高效。

### 自注意力 vs 交叉注意力

| 类型 | Q 来源 | K/V 来源 | 目的 |
|------|--------|----------|------|
| **自注意力** | 同一序列 | 同一序列 | 捕捉序列内部依赖，重构每个词的表示 |
| **交叉注意力** | Decoder 状态 | Encoder 输出 | 在生成时从源序列中查找相关信息 |

## 自注意力机制

在自注意力中，Q、K、V 均来自同一输入序列 X：

$$Q = X W^Q, \quad K = X W^K, \quad V = X W^V$$

$$Attention(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

**缩放因子 $\sqrt{d_k}$** 的作用：当维度 d_k 较大时，点积方差增大，softmax 进入梯度极小区域导致梯度消失；除以 $\sqrt{d_k}$ 保持方差稳定。

### 计算过程

1. 每个词元 x_i 经线性变换生成 q_i、k_i、v_i。
2. q_i 与所有 k_j 计算点积得到注意力分数。
3. 缩放 + softmax 归一化得到权重 α_ij。
4. 用 α_ij 对所有 v_j 加权求和得到新表示 z_i。

关键特性：每个词元可直接关注序列中的任意其他词元，距离为 O(1)，彻底解决长距离依赖问题。

## 多头注意力（Multi-Head Attention）

将 Q/K/V 分别投影到 h 个子空间，并行计算 h 组注意力，再拼接结果：

$$head_i = Attention(Q W_i^Q, K W_i^K, V W_i^V)$$
$$MultiHead = Concat(head_1, ..., head_h) W^O$$

每个头可关注不同的语义子空间（如语法关系、指代关系、位置关系等），增强模型表达能力。

## 位置编码（Positional Encoding）

自注意力本身是**置换不变**的（不考虑序列顺序），需显式注入位置信息。Transformer 原论文使用**正弦/余弦位置编码**：

$$PE_{(pos, 2i)} = \sin(pos / 10000^{2i/d_{model}})$$
$$PE_{(pos, 2i+1)} = \cos(pos / 10000^{2i/d_{model}})$$

特性：
- 每个位置有唯一编码。
- 任意两个位置的编码点积仅与相对距离有关，模型可学习相对位置关系。
- 可扩展到训练时未见过的序列长度。

后续改进包括可学习位置编码、RoPE（旋转位置编码，见 [大模型架构深入](llm-architecture.md)）等。

## Transformer 完整架构

### Encoder（编码器）

每层由两个子层组成：
1. **多头自注意力**：带残差连接 + 层归一化（Pre-LN 或 Post-LN）。
2. **位置前馈网络（FFN）**：两层线性变换 + ReLU，带残差连接 + 层归一化。

Encoder 堆叠 N 层（原论文 N=6），输出每个位置的上下文表示。

### Decoder（解码器）

每层有三个子层：
1. **掩码多头自注意力**：Mask 确保预测第 t 个词时只能看到 t 之前的词（因果掩码）。
2. **交叉注意力**：Q 来自 Decoder，K/V 来自 Encoder 输出。
3. **位置前馈网络**：同 Encoder。

Decoder 同样堆叠 N 层，最终经线性层 + softmax 输出下一个词的概率。

### 关键组件

- **残差连接**：$output = LayerNorm(x + Sublayer(x))$，缓解深层网络梯度消失。
- **层归一化**：对每个样本的特征维度归一化，稳定训练。
- **FFN**：$FFN(x) = max(0, xW_1 + b_1)W_2 + b_2$，中间维度通常放大 4 倍。

## 手写实现

教程 `code/C4/transformer/` 目录提供了模块化的手写 Transformer 实现：

| 文件 | 内容 |
|------|------|
| `src/attention.py` | 多头自注意力、交叉注意力 |
| `src/pos.py` | 位置编码 |
| `src/ffn.py` | 位置前馈网络 |
| `src/norm.py` | 层归一化 |
| `src/transformer.py` | Encoder/Decoder 完整组装 |
| `main.py` | 运行入口 |

此外 `code/C4/` 还包含独立的 Seq2Seq（01）、Attention（02）、Self-Attention（03）渐进式实现。

## Transformer 的历史意义

1. **并行计算**：自注意力不依赖顺序计算，可充分利用 GPU/TPU 并行能力。
2. **长距离依赖**：任意两个位置间距离为 O(1)，不再受 RNN 梯度消失限制。
3. **架构统一**：Encoder-only（BERT）、Decoder-only（GPT）、Encoder-Decoder（T5）三条路线均源于 Transformer。
4. **规模化基础**：Transformer 的并行特性使得训练千亿参数模型成为可能。

## 延伸阅读

- 前置：[词向量与循环神经网络](word-vectors-rnn.md)——Transformer 解决的问题来源
- 后续：[预训练语言模型](pretrained-models.md)——Transformer 的三大变体
- 深入：[大模型架构深入](llm-architecture.md)——Transformer 的现代演进
- 示例代码：[C4 Transformer 代码](../examples/index.md#c4-transformer)
