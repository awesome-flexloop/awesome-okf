---
type: example
title: "TinyRAG 检索增强生成"
bundle: /datawhale/happy-llm
description: "第七章 RAG 实践：实现 Embeddings、VectorBase、LLM 调用的完整检索增强生成链路"
sources: https://github.com/datawhalechina/happy-llm/tree/main/docs/chapter7/RAG
related:
  - /datawhale/happy-llm/concepts/rag-retrieval-augmented-generation
tags: [rag, embedding, vector-search, retrieval]
status: stable
---

# TinyRAG 检索增强生成

## 概述

本示例对应 Happy-LLM 第七章 7.2 节，代码位于 `docs/chapter7/RAG/`。TinyRAG 是一个最小可用的检索增强生成系统，展示了从文档加载、向量化、存储检索到 LLM 生成的完整 RAG 链路。

## 环境准备

```bash
pip install -r docs/chapter7/RAG/requirements.txt
cp .env_example .env  # 配置 LLM API Key
```

CPU 即可体验，向量检索建议预留充足内存。

## 代码结构

| 文件 | 职责 |
|------|------|
| `Embeddings.py` | 嵌入模型封装，将文本转换为向量 |
| `VectorBase.py` | 向量数据库，文档存储与相似度检索 |
| `LLM.py` | 大模型调用接口，生成回答 |
| `utils.py` | 文档加载、分块等工具函数 |
| `demo.py` | 命令行演示，串联完整 RAG 流程 |
| `.env_example` | 环境变量模板（API Key 配置） |

## RAG 流程实现

### 1. 文档处理与索引（离线）

```python
# utils.py: 文档加载与分块
docs = load_documents("./data")          # 加载文档
chunks = split_documents(docs, chunk_size=500, overlap=50)  # 分块

# Embeddings.py: 文本向量化
embedding_model = Embeddings()
vectors = embedding_model.encode(chunks)  # 批量编码

# VectorBase.py: 存储
vector_db = VectorBase()
vector_db.add(chunks, vectors)            # 存入向量库
```

### 2. 检索与生成（在线）

```python
# demo.py: 完整 RAG 流程
query = "什么是 RAG？"

# 步骤1：查询向量化
query_vec = embedding_model.encode(query)

# 步骤2：向量检索 Top-K
results = vector_db.search(query_vec, top_k=3)
context = "\n".join([r.text for r in results])

# 步骤3：组装 Prompt
prompt = f"""请根据以下参考资料回答问题。

参考资料：
{context}

问题：{query}
回答："""

# 步骤4：LLM 生成
llm = LLM()
answer = llm.chat(prompt)
print(answer)
```

### 3. 向量检索核心

`VectorBase.py` 实现基于余弦相似度的向量检索：

```python
import numpy as np

class VectorBase:
    def search(self, query_vec, top_k=3):
        # 余弦相似度
        scores = np.dot(self.vectors, query_vec) / (
            np.linalg.norm(self.vectors, axis=1) * np.linalg.norm(query_vec)
        )
        top_indices = np.argsort(scores)[-top_k:][::-1]
        return [self.documents[i] for i in top_indices]
```

## 学习要点

1. **模块化设计**：Embeddings、VectorBase、LLM 三个组件解耦，每个可独立替换升级
2. **分块策略**：chunk_size 和 overlap 影响检索精度——太大会引入噪声，太小会丢失上下文
3. **相似度计算**：余弦相似度衡量向量方向相似性，适合文本语义匹配
4. **Prompt 工程**：明确指示模型"基于参考资料回答"，降低幻觉
5. **可溯源**：回答基于检索到的具体文档片段，可追溯信息来源

## 从 TinyRAG 到生产级 RAG

TinyRAG 展示核心原理，生产环境可升级：
- 嵌入模型：使用更强的 BGE、M3E、Cohere Embed
- 向量数据库：使用 FAISS、Milvus、Chroma 替代 numpy
- 检索策略：加入混合检索（BM25 + 向量）、重排序（Reranker）
- 文档处理：支持 PDF、Word、网页等多格式，语义分块
- 评估框架：加入 RAGAS 等评估指标

## 延伸阅读

- [RAG 检索增强生成](../concepts/rag-retrieval-augmented-generation.md)——完整概念解析
- [TinyAgent 智能体工具调用](agent-tinyagent.md)——从知识检索到工具调用
