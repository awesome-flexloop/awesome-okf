---
type: concept
title: "RAG 检索增强生成"
bundle: /datawhale/happy-llm
description: "Retrieval-Augmented Generation——先检索外部文档再生成回答，缓解 LLM 幻觉与知识过时，提升答案准确性和时效性"
sources: https://github.com/datawhalechina/happy-llm/blob/main/docs/chapter7/第七章%20大模型应用.md
related:
  - /datawhale/happy-llm/concepts/agent-intelligent-agent
  - /datawhale/happy-llm/concepts/model-training
tags: [rag, retrieval, vector-database, embedding, hallucination]
status: stable
---

# RAG 检索增强生成

## 核心理解

RAG（Retrieval-Augmented Generation，检索增强生成）是在 LLM 生成回答之前，先从外部文档库中检索相关信息，并将这些信息注入 Prompt 指导生成的技术。它解决了 LLM 的三个固有问题：**幻觉**（杜撰虚假信息）、**知识过时**（训练数据有截止日期）和**领域知识不足**（专业领域理解有限）。

第七章通过 TinyRAG 的完整实现，展示了 RAG 的核心链路和代码实践。

## 为什么需要 RAG

LLM 虽然具备强大的语言理解和生成能力，但面临：

1. **幻觉问题**：LLM 根据概率生成文本，可能"一本正经地胡说八道"，生成看似合理但完全错误的信息，在医学、金融等领域后果严重
2. **知识时效性**：模型训练数据有截止日期，无法回答训练后的新事件、新数据
3. **领域专业性**：对特定企业内部知识、专业领域文档的理解有限
4. **可验证性差**：用户难以判断答案是否准确，缺乏信息来源追溯

RAG 通过"先检索、后生成"的方式，让模型基于可信外部文档回答，答案可溯源到具体文档片段。

## RAG 核心流程

```
用户提问
  ↓
① 查询处理 → 将问题转换为向量（Embedding）
  ↓
② 向量检索 → 在向量数据库中查找最相似的文档片段（Top-K）
  ↓
③ 上下文组装 → 将检索结果 + 用户问题组装为 Prompt
  ↓
④ LLM 生成 → 模型基于检索内容生成回答（附带来源引用）
  ↓
返回答案
```

### ① 文档索引（离线阶段）

1. **文档加载与分块（Chunking）**：将长文档按固定长度或语义边界切分为片段（通常 200-1000 token），平衡检索精度和上下文长度
2. **Embedding**：使用嵌入模型（如 BGE、M3E、OpenAI text-embedding）将文本块转换为高维向量
3. **向量存储**：将向量和原始文本存入向量数据库（如 Chroma、FAISS、Milvus）

### ② 检索（在线阶段）

1. 将用户问题同样通过 Embedding 转换为向量
2. 在向量数据库中计算相似度（余弦相似度、点积等），检索 Top-K 最相关文档片段
3. 可选：重排序（Reranker）对初筛结果进行更精细的语义排序

### ③ Prompt 组装

将检索到的文档片段作为上下文注入 Prompt：

```
请根据以下参考资料回答问题。如果参考资料中没有相关信息，请说明无法回答。

参考资料：
{retrieved_documents}

问题：{user_question}
回答：
```

### ④ 生成

LLM 基于提供的上下文生成回答，由于答案直接来源于检索文档，显著降低幻觉风险。

## TinyRAG 实现

第七章提供的 TinyRAG 是一个最小可用 RAG 系统，代码位于 `docs/chapter7/RAG/`：

| 文件 | 职责 |
|------|------|
| `Embeddings.py` | 嵌入模型封装，将文本转换为向量 |
| `VectorBase.py` | 向量数据库，实现文档存储和相似度检索 |
| `LLM.py` | 大模型调用接口，生成最终回答 |
| `utils.py` | 文档加载、分块等工具函数 |
| `demo.py` | 命令行演示，串联完整 RAG 流程 |

TinyRAG 体现了 RAG 的核心设计：模块化（嵌入、检索、生成解耦）、可替换（每个组件可升级为更强大的实现）、可溯源（回答基于检索到的具体文档）。

## RAG 与微调的对比

| 维度 | RAG | 微调（SFT/LoRA） |
|------|-----|-----------------|
| 知识更新 | 实时更新文档库即可 | 需要重新训练 |
| 可解释性 | 答案可溯源到文档 | 黑盒，难以解释 |
| 成本 | 检索成本低，无需训练 | 训练成本较高 |
| 适用场景 | 动态知识、事实问答 | 风格对齐、能力习得 |
| 幻觉控制 | 显著降低 | 无法根本解决 |

实际应用中 RAG 和微调常结合使用：微调让模型学会特定领域的表达方式和工具使用，RAG 提供实时准确的知识来源。

## 在 Happy-LLM 中的位置

第七章 7.2 节讲解 RAG，位于评测（7.1）之后、Agent（7.3）之前。评测帮助理解模型能力边界，RAG 通过外部知识弥补能力不足，Agent 则进一步让模型能调用工具执行行动——三者构成"评估→增强→行动"的应用层递进。

## 延伸阅读

- [Agent 智能体](agent-intelligent-agent.md)——从知识检索到工具调用的进阶
- [模型训练](model-training.md)——RAG 与微调的互补关系
- [TinyRAG 检索增强生成示例](../examples/rag-tinyrag.md)——第七章 RAG 代码实践
