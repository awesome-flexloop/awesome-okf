---
title: 基于 Faiss 的 RAG 实战
type: example
bundle: /datawhale/easy-vecdb
description: 使用 FAISS 构建检索增强生成（RAG）系统的完整流程，包含文档分块、向量嵌入、FAISS 索引构建、相似度检索和 LLM 生成
related:
  - /datawhale/easy-vecdb/concepts/faiss-milvus-engineering
  - /datawhale/easy-vecdb/concepts/vector-retrieval-basics
  - /datawhale/easy-vecdb/concepts/ivf-pq-quantization
sources:
  - https://github.com/datawhalechina/easy-vecdb/blob/main/docs/projects/project2/README.md
  - https://github.com/datawhalechina/easy-vecdb/tree/main/src/faissSear
tags:
  - rag
  - faiss
  - llm
  - retrieval-augmented-generation
---

# 基于 Faiss 的 RAG 实战

本示例展示如何使用 FAISS 构建一个完整的检索增强生成（RAG）系统。RAG 通过从向量数据库中检索相关文档片段，将其作为上下文传递给大语言模型，从而生成准确、有依据的回答。

## RAG 架构

```
文档 → 分块(Chunking) → 嵌入(Embedding) → FAISS索引
                                                  ↓
用户问题 → 嵌入 → FAISS检索 → Top-K相关片段 → 拼接Prompt → LLM → 回答
```

## 环境依赖

```bash
pip install faiss-cpu numpy sentence-transformers
```

如需 LLM 生成部分，可根据使用的模型安装对应 SDK（如 openai、transformers 等）。

## 完整实现

### 1. 文档处理与分块

```python
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer


class Document:
    def __init__(self, content, metadata=None):
        self.content = content
        self.metadata = metadata or {}


class TextChunker:
    def __init__(self, chunk_size=200, overlap=50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def split(self, text):
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - self.overlap
        return chunks

    def split_documents(self, documents):
        all_chunks = []
        for doc in documents:
            chunks = self.split(doc.content)
            for i, chunk in enumerate(chunks):
                all_chunks.append(Document(
                    content=chunk,
                    metadata={**doc.metadata, "chunk_id": i}
                ))
        return all_chunks
```

### 2. FAISS 向量检索引擎

```python
class FaissVectorStore:
    def __init__(self, dimension, index_type="flat", nlist=100):
        self.dimension = dimension
        self.documents = []

        if index_type == "flat":
            self.index = faiss.IndexFlatIP(dimension)
        elif index_type == "ivf":
            quantizer = faiss.IndexFlatIP(dimension)
            self.index = faiss.IndexIVFFlat(quantizer, dimension, nlist)
        else:
            raise ValueError(f"不支持的索引类型: {index_type}")

        self.index_type = index_type
        self._trained = False

    def add_documents(self, documents, embeddings):
        vectors = np.array(embeddings).astype('float32')
        faiss.normalize_L2(vectors)

        if self.index_type == "ivf" and not self._trained:
            self.index.train(vectors)
            self._trained = True

        self.index.add(vectors)
        self.documents.extend(documents)

    def search(self, query_embedding, top_k=5):
        query = np.array([query_embedding]).astype('float32')
        faiss.normalize_L2(query)

        if self.index_type == "ivf":
            self.index.nprobe = min(10, self.index.nlist)

        scores, indices = self.index.search(query, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1 and idx < len(self.documents):
                results.append({
                    "document": self.documents[idx],
                    "score": float(score)
                })
        return results

    def save(self, path):
        faiss.write_index(self.index, path)

    def load(self, path):
        self.index = faiss.read_index(path)
        self._trained = True
```

### 3. 嵌入模型封装

```python
class EmbeddingModel:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def encode(self, texts):
        return self.model.encode(texts, show_progress_bar=False)

    def encode_query(self, text):
        return self.model.encode(text)
```

### 4. RAG 系统整合

```python
class RAGSystem:
    def __init__(self, embedding_model, vector_store, llm_func=None):
        self.embedding_model = embedding_model
        self.vector_store = vector_store
        self.llm_func = llm_func
        self.chunker = TextChunker(chunk_size=200, overlap=50)

    def ingest(self, documents):
        chunks = self.chunker.split_documents(documents)
        texts = [chunk.content for chunk in chunks]
        embeddings = self.embedding_model.encode(texts)
        self.vector_store.add_documents(chunks, embeddings)
        return len(chunks)

    def retrieve(self, query, top_k=5):
        query_embedding = self.embedding_model.encode_query(query)
        return self.vector_store.search(query_embedding, top_k)

    def _build_prompt(self, query, contexts):
        context_str = "\n\n".join([
            f"[片段{i+1}] {r['document'].content}"
            for i, r in enumerate(contexts)
        ])
        return f"""根据以下参考资料回答问题。如果参考资料中没有相关信息，请说明无法回答。

参考资料：
{context_str}

问题：{query}

回答："""

    def answer(self, query, top_k=5):
        contexts = self.retrieve(query, top_k)

        if not contexts:
            return "未找到相关文档。", []

        prompt = self._build_prompt(query, contexts)

        if self.llm_func:
            answer = self.llm_func(prompt)
        else:
            answer = "（未配置 LLM，以下为检索到的相关片段）\n\n"
            for i, r in enumerate(contexts):
                answer += f"[{i+1}] (相似度: {r['score']:.4f}) {r['document'].content}\n\n"

        return answer, contexts
```

### 5. 使用示例

```python
documents = [
    Document("向量数据库是专门用于存储和检索高维向量的数据库系统。它通过索引技术实现毫秒级相似性搜索。",
             metadata={"source": "vector_db_intro.txt"}),
    Document("FAISS是Meta开发的向量相似性搜索库，支持IVF、PQ、HNSW等多种索引，支持GPU加速。",
             metadata={"source": "faiss_guide.txt"}),
    Document("HNSW是一种基于图的近似最近邻算法，通过分层小世界图实现高精度低延迟的向量检索。",
             metadata={"source": "hnsw_paper.txt"}),
    Document("RAG即检索增强生成，通过从知识库检索相关文档来增强大语言模型的回答准确性。",
             metadata={"source": "rag_overview.txt"}),
]

embedding_model = EmbeddingModel("all-MiniLM-L6-v2")
store = FaissVectorStore(dimension=384, index_type="flat")
rag = RAGSystem(embedding_model, store)

chunk_count = rag.ingest(documents)
print(f"已摄入 {chunk_count} 个文本块")

query = "什么是HNSW算法？"
answer, contexts = rag.answer(query, top_k=3)
print(f"\n问题: {query}")
print(f"\n回答:\n{answer}")
```

## 关键设计说明

### 索引选择

| 数据规模 | 推荐索引 | 原因 |
|---------|---------|------|
| < 10 万 | Flat | 暴力搜索精度 100%，构建快 |
| 10 万~100 万 | IVFFlat | 聚类加速，精度可控 |
| 100 万~千万 | IVFPQ | 量化压缩，内存友好 |
| 高召回低延迟 | HNSW | 图索引性能最优 |

### 分块策略

- **固定长度分块**：简单直接，但可能切断语义
- **重叠分块**：相邻块保留重叠（如 50 字），避免关键信息丢失
- **语义分块**：按句子/段落边界切分，保留语义完整性（教程中介绍了 Meta-Chunking 等高级策略）
- **块大小选择**：技术文档适合较长块（300~500 字），对话数据适合短块（100~200 字）

### 检索优化

1. **混合搜索**：结合 BM25 关键词检索和向量检索，用 RRF 融合排序
2. **重排（Rerank）**：初检索返回较多候选（如 Top-50），用 Cross-Encoder 重排取 Top-5
3. **元数据过滤**：检索前按来源、时间等字段过滤，减少搜索范围
4. **查询改写**：用 LLM 将用户问题改写为更适合检索的查询

## 延伸阅读

- [Faiss 与 Milvus 工程实践](/datawhale/easy-vecdb/concepts/faiss-milvus-engineering.md) — FAISS 索引类型详解
- [向量检索基础](/datawhale/easy-vecdb/concepts/vector-retrieval-basics.md) — 嵌入模型和相似度度量
- [Milvus 快速入门](/datawhale/easy-vecdb/examples/milvus-getting-started.md) — 使用分布式向量数据库构建 RAG
