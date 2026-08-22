---
type: concept
title: "词向量与循环神经网络"
bundle: "/datawhale/base-llm"
description: "从分词技术到词向量表示（Word2Vec CBOW/Skip-gram），再到 RNN/LSTM/GRU 序列建模，构建文本表示与序列处理的基础知识。"
sources:
  - https://github.com/datawhalechina/base-llm/blob/main/docs/chapter2/03_tokenization.md
  - https://github.com/datawhalechina/base-llm/blob/main/docs/chapter2/04_word_vector.md
  - https://github.com/datawhalechina/base-llm/blob/main/docs/chapter2/05_Word2Vec.md
  - https://github.com/datawhalechina/base-llm/blob/main/docs/chapter2/06_gensim.md
  - https://github.com/datawhalechina/base-llm/blob/main/docs/chapter3/08_RNN.md
  - https://github.com/datawhalechina/base-llm/blob/main/docs/chapter3/09_LSTM&GRU.md
related:
  - /datawhale/base-llm/concepts/nlp-basics
  - /datawhale/base-llm/concepts/transformer
---

# 词向量与循环神经网络

## 核心理解

本章是 NLP 深度学习的两块基石：**词向量**解决"词语如何表示为计算机可处理的稠密向量"，**循环神经网络**解决"序列信息如何按顺序传递和建模"。两者共同构成了从离散文本到连续表示、从独立词到上下文序列的桥梁。

## 分词技术

分词（Tokenization）是 NLP 流水线的第一步，将连续文本切分为有意义的词元（Token）。

- **中文分词挑战**：中文没有空格分隔，"南京市长江大桥"可切分为"南京市/长江大桥"或"南京/市长/江大桥"。
- **jieba 分词**：支持精确模式、全模式、搜索引擎模式，可加载用户自定义词典和词性标注。
- **代码示例**：`code/C2/01_jieba.py` 演示 jieba 基础用法，`user_dict.txt`/`user_pos_dict.txt` 为自定义词典。

## 词向量表示

### One-hot 表示的局限

传统 One-hot 编码将每个词表示为高维稀疏向量，存在维度灾难和**语义鸿沟**问题——任意两个词的向量正交，无法表达语义相似度。

### 分布式表示

核心思想：**词语的语义由其上下文决定**（You shall know a word by the company it keeps）。将词映射到低维稠密向量空间，语义相近的词在空间中距离相近。经典示例：

$$vector(\text{国王}) - vector(\text{男人}) + vector(\text{女人}) \approx vector(\text{女王})$$

### Word2Vec

Google 2013 年提出，包含两种训练模式：

- **CBOW（Continuous Bag-of-Words）**：用上下文词预测中心词，训练快，适合小数据集。
- **Skip-gram**：用中心词预测上下文词，对低频词表现更好。

优化技术：
- **Hierarchical Softmax**：利用哈夫曼树将 softmax 复杂度从 O(V) 降到 O(log V)。
- **Negative Sampling**：采样少量负例替代全量负例计算。

### Gensim 实战

Gensim 是主流的词向量训练库，`code/C2/04_gensim.ipynb` 演示语料预处理、模型训练、相似度计算和词向量可视化。

## 循环神经网络（RNN）

### 基本结构

RNN 通过**隐藏状态 h_t** 在时间步间传递信息：

$$h_t = \tanh(W_{hh} h_{t-1} + W_{xh} x_t + b_h)$$
$$y_t = W_{hy} h_t + b_y$$

每个时间步共享同一组权重（W_hh, W_xh, W_hy），实现参数共享和变长序列处理。

### 梯度问题

标准 RNN 在长序列上存在：
- **梯度消失**：反向传播中梯度连乘导致长距离梯度趋于零，无法学习长距离依赖。
- **梯度爆炸**：梯度连乘导致数值过大，通过梯度裁剪（Gradient Clipping）缓解。

## LSTM（Long Short-Term Memory）

LSTM 通过**细胞状态 C_t** 和三个门控机制解决长距离依赖问题：

| 门 | 作用 | 公式 |
|----|------|------|
| **遗忘门 f_t** | 决定丢弃哪些旧信息 | $\sigma(W_f \cdot [h_{t-1}, x_t] + b_f)$ |
| **输入门 i_t** | 决定存储哪些新信息 | $\sigma(W_i \cdot [h_{t-1}, x_t] + b_i)$ |
| **输出门 o_t** | 决定输出什么信息 | $\sigma(W_o \cdot [h_{t-1}, x_t] + b_o)$ |

细胞状态更新：
$$C_t = f_t \odot C_{t-1} + i_t \odot \tilde{C}_t$$
$$h_t = o_t \odot \tanh(C_t)$$

细胞状态 C_t 类似一条"传送带"，信息可在其上几乎不变地流动，门控通过加法（而非乘法）更新，有效缓解梯度消失。

## GRU（Gated Recurrent Unit）

GRU 是 LSTM 的简化版本，将遗忘门和输入门合并为**更新门 z_t**，细胞状态与隐藏状态合并：

- **更新门 z_t**：决定保留多少旧信息。
- **重置门 r_t**：决定新信息与旧信息的结合方式。

GRU 参数量更少（少一个门的权重），训练更快，在许多任务上效果与 LSTM 相当。

## RNN/LSTM 的历史局限

尽管 LSTM/GRU 缓解了长距离依赖问题，但它们仍受限于：
1. **顺序计算**：必须按时间步串行处理，无法并行加速。
2. **信息瓶颈**：无论序列多长，最终都需压缩到固定维度的隐藏状态。

这些局限直接催生了 Attention 机制和 Transformer 架构的诞生。

## 延伸阅读

- 前置：[NLP 基础与发展历程](nlp-basics.md)
- 后续：[Transformer 架构](transformer.md)——RNN 的替代者
- 示例代码：[C3 RNN/LSTM 代码](../examples/index.md#c3-循环神经网络)
