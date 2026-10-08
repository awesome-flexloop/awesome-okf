---
type: example
title: "手写 Transformer 注意力机制"
bundle: /datawhale/happy-llm
description: "第二章代码实践：使用纯 PyTorch 从零实现 Multi-Head Attention 和完整 Transformer Encoder-Decoder"
sources: https://github.com/datawhalechina/happy-llm/tree/main/docs/chapter2/code
related:
  - /datawhale/happy-llm/concepts/transformer-architecture
tags: [transformer, attention, pytorch, hands-on]
status: stable
---

# 手写 Transformer 注意力机制

## 概述

本示例对应 Happy-LLM 第二章，代码位于 `docs/chapter2/code/transformer.py`。通过纯 PyTorch 手写实现 Transformer 的核心组件，建立对注意力机制和 Encoder-Decoder 结构的直觉理解。

## 环境准备

```bash
pip install -r docs/chapter2/code/requirements.txt
```

CPU 或单卡 GPU 即可运行，是全书最轻量的代码实践。

## 核心实现

### Scaled Dot-Product Attention

```python
class Attention(nn.Module):
    def __init__(self, dropout=0.1):
        super().__init__()
        self.dropout = nn.Dropout(dropout)

    def forward(self, q, k, v, mask=None, dropout=None):
        # QK^T / sqrt(d_k)
        scores = torch.matmul(q, k.transpose(-2, -1)) / torch.sqrt(
            torch.tensor(k.size(-1), dtype=torch.float32)
        )
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
        p_attn = F.softmax(scores, dim=-1)
        if dropout is not None:
            p_attn = dropout(p_attn)
        return torch.matmul(p_attn, v), p_attn
```

关键点：缩放因子 `√d_k` 防止点积过大导致 Softmax 梯度消失；Decoder 中的 mask 确保位置只能注意已生成 token。

### Multi-Head Attention

```python
class MultiHeadedAttention(nn.Module):
    def __init__(self, h, d_model, dropout=0.1):
        super().__init__()
        assert d_model % h == 0
        self.d_k = d_model // h
        self.h = h
        self.linears = clones(nn.Linear(d_model, d_model), 4)
        self.attn = None
        self.dropout = nn.Dropout(p=dropout)

    def forward(self, query, key, value, mask=None):
        if mask is not None:
            mask = mask.unsqueeze(1)
        nbatches = query.size(0)
        # 线性投影 Q/K/V，分头
        q, k, v = [
            l(x).view(nbatches, -1, self.h, self.d_k).transpose(1, 2)
            for l, x in zip(self.linears, (query, key, value))
        ]
        # 注意力计算
        x, self.attn = attention(q, k, v, mask=mask, dropout=self.dropout)
        # 拼接多头
        x = x.transpose(1, 2).contiguous().view(nbatches, -1, self.h * self.d_k)
        return self.linears[-1](x)
```

### Encoder-Decoder 完整结构

实现还包括：
- PositionwiseFeedForward（FFN 层）
- PositionalEncoding（正弦位置编码）
- Embeddings（词嵌入 + √d_model 缩放）
- Generator（输出层 + Softmax）
- Encoder/Decoder 堆叠结构
- 完整的 `make_model()` 工厂函数

## 学习要点

1. **注意力计算的三步**：QK^T 相似度 → Softmax 归一化 → 加权 V
2. **多头的意义**：不同头关注不同子空间的语义关系
3. **Mask 的作用**：Encoder 用 padding mask，Decoder 额外用 causal mask
4. **残差连接 + LayerNorm**：每个子层的标准模式
5. **位置编码**：无位置信息的注意力是词袋模型，位置编码注入序列顺序

## 延伸阅读

- [Transformer 架构](../concepts/transformer-architecture.md)——完整概念解析
- [LLaMA2 手写实现](llama2-pretrain-sft.md)——从基础 Transformer 到现代 LLM 架构
