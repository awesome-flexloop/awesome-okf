---
type: reference
title: "第二章 Transformer 架构"
bundle: /datawhale/happy-llm
description: "注意力机制原理、Self-Attention、Multi-Head Attention、位置编码、Encoder-Decoder 结构与手写实现"
source: https://github.com/datawhalechina/happy-llm/blob/main/docs/chapter2/第二章%20Transformer架构.md
path: docs/chapter2/第二章 Transformer架构.md
code: docs/chapter2/code/
tags: [transformer, attention, encoder, decoder]
status: stable
---

# 第二章 Transformer 架构

## 信源信息

- **文件路径**：`docs/chapter2/第二章 Transformer架构.md`
- **代码目录**：`docs/chapter2/code/`（含 `transformer.py`、`requirements.txt`）
- **GitHub**：https://github.com/datawhalechina/happy-llm/blob/main/docs/chapter2/第二章%20Transformer架构.md

## 内容概要

本章是全书理论基础的核心，涵盖：

- **2.1 注意力机制**：从 RNN/LSTM 的缺陷出发，介绍 Query/Key/Value 三变量，点积相似度计算，Softmax 归一化
- **2.2 深入理解注意力机制**：缩放点积注意力公式 `softmax(QK^T/√d_k)V`，多头注意力
- **2.3 Transformer 架构**：Encoder-Decoder 结构，位置编码（正弦编码），残差连接与 LayerNorm，FFN
- **2.4 手把手搭建 Transformer**：纯 PyTorch 实现完整 Transformer

## 对应概念

- [Transformer 架构](../concepts/transformer-architecture.md)
- [手写 Transformer 注意力机制示例](../examples/transformer-handwritten.md)
