---
type: example
title: "Embedding 文本向量化流程"
description: "基于 BCEmbedding 封装类与 sentence-transformers 两条路径完成文本向量化：模型加载、encode 调用、余弦相似度计算，以及指令前缀的正确使用（应为空）。"
tags: [bcembedding, embedding, example, sentence-transformers, similarity]
generated: { by: "reference_agent/trae-cn", at: 2026-09-09T10:00:00+08:00 }
verified: { by: "process:facts-md", at: 2026-09-09T10:00:00+08:00 }
status: stable
stale_after: 2027-09-09
sources:
  - id: facts
    resource: /references/facts.md
    title: BCEmbedding 源码事实清单（F-bc 系列）
  - id: concepts
    resource: /concepts/01-embedding-model.md
    title: EmbeddingModel：向量化接口全解
---

# Embedding 文本向量化流程

本演练演示两条向量化路径：官方 `BCEmbedding` 封装类（推荐）与 `sentence-transformers` 生态路径。接口签名均忠实于源码与 README Quick Start（F-bc-005、F-bc-009、F-bc-029）。

## 前置条件

```bash
pip install BCEmbedding==0.1.5
```

依赖约束：`torch>=1.6.0`、`transformers>=4.35.0,<4.37.0`、`datasets`、`sentence-transformers`（F-bc-002）。模型权重首次运行时会从 HuggingFace `maidalun1020` 组织下载（F-bc-027）。

## 路径一：`BCEmbedding` 封装类

```python
from BCEmbedding import EmbeddingModel

# list of sentences
sentences = ['句子零', '句子一']

# init embedding model（默认加载 bce-embedding-base_v1，cls pooler）
model = EmbeddingModel(model_name_or_path="maidalun1020/bce-embedding-base_v1")

# extract embeddings：默认 return_numpy=True，返回 numpy ndarray
embeddings = model.encode(sentences)
print(embeddings.shape)   # (2, 768)
```

关键默认行为（F-bc-005、F-bc-009、F-bc-011）：

- `pooler='cls'`：取 `outputs.last_hidden_state[:, 0]`；
- `normalize_to_unit=True`：按行 L2 范数归一化，因此**点积即余弦相似度**；
- `max_length=512`：token 级截断；
- `query_instruction=""`：**BCE 自家模型不需要指令**（F-bc-028），保持默认空串即可。

计算相似度：

```python
import numpy as np

q_emb = model.encode("什么是检索增强生成？")
p_embs = model.encode([
    "检索增强生成（RAG）通过检索外部知识增强大模型回答。",
    "今天天气晴朗，适合外出。",
])

sims = (p_embs @ q_emb)        # 行归一化后点积 = 余弦相似度
best = int(np.argmax(sims))    # 语义最相关的篇章下标
```

`encode` 也接受单条字符串（自动包装为单元素列表，F-bc-010），返回形状 `(1, hidden_dim)` 的 ndarray。

## 路径二：`sentence-transformers`

适合已在使用 `SentenceTransformer` 生态的项目（F-bc-029）：

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("maidalun1020/bce-embedding-base_v1")
embeddings = model.encode(sentences, normalize_embeddings=True)
```

注意 `normalize_embeddings=True` 对应封装类默认的 `normalize_to_unit=True`（F-bc-011）；若漏掉，向量未归一化，后续相似度计算需显式除以模长。

## 常见错误

| 现象 | 原因 | 对策 |
|---|---|---|
| 检索效果明显差于官方 demo | 换用了 BGE/e5 底模却未加指令前缀 | 查 `query_instruction_for_retrieval_dict` 补指令（见 [/concepts/03-query-instruction.md](../concepts/03-query-instruction.md)） |
| 同一权重两次结果维度一致但数值不同 | 一次用 `pooler='cls'`、一次用 `'mean'` | pooler 是语义的一部分，建库后不可更换 |
| transformers 版本冲突 | 环境内 transformers ≥ 4.37 | 按 `>=4.35.0,<4.37.0` 约束安装（F-bc-002） |

## 相关概念

- [/concepts/00-quickstart.md](../concepts/00-quickstart.md) — 安装与三种调用路径
- [/concepts/01-embedding-model.md](../concepts/01-embedding-model.md) — encode 数据流详解
- [/concepts/03-query-instruction.md](../concepts/03-query-instruction.md) — 指令字典与跨家模型适配
