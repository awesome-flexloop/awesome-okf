---
title: 手写 Mini Vector DB
type: example
bundle: /datawhale/easy-vecdb
description: 使用 numpy + scikit-learn + pickle 从零实现一个简化版向量数据库，包含向量 CRUD、余弦相似度暴力检索、IVF 近似检索和持久化
related:
  - /datawhale/easy-vecdb/concepts/vector-retrieval-basics
  - /datawhale/easy-vecdb/concepts/ivf-pq-quantization
  - /datawhale/easy-vecdb/concepts/faiss-milvus-engineering
sources:
  - https://github.com/datawhalechina/easy-vecdb/blob/main/docs/base/chapter6/实现你自己的向量数据库.md
tags:
  - tutorial
  - numpy
  - ivf
  - from-scratch
---

# 手写 Mini Vector DB

本示例用约 200 行 Python 实现一个简化版向量数据库，帮助理解向量数据库"存储-索引-检索"的核心流程。实现基于 numpy、scikit-learn 和 pickle，包含向量 CRUD、暴力检索、IVF 近似检索和持久化功能。

## 依赖安装

```bash
pip install numpy scikit-learn sentence-transformers modelscope
```

## 完整实现

```python
import numpy as np
import pickle
import uuid
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity


class SimpleVectorDB:
    def __init__(self, vector_dim, db_path="vector_db.pkl"):
        self.vector_dim = vector_dim
        self.db_path = db_path
        self.vectors = np.array([])
        self.vector_ids = []
        self.id_to_index = dict()
        self.metadata = dict()
        self.ivf_index = None
        self.ivf_kmeans = None

    def _check_vector_dim(self, vector):
        if len(vector) != self.vector_dim:
            raise ValueError(f"向量维度错误，需为{self.vector_dim}维，当前为{len(vector)}维")

    def insert(self, vector, metadata=None):
        vector = np.array(vector, dtype=np.float32).flatten()
        self._check_vector_dim(vector)
        vector_id = str(uuid.uuid4())
        if len(self.vectors) == 0:
            self.vectors = np.expand_dims(vector, axis=0)
        else:
            self.vectors = np.vstack([self.vectors, vector])
        self.vector_ids.append(vector_id)
        self.id_to_index[vector_id] = len(self.vector_ids) - 1
        if metadata:
            self.metadata[vector_id] = metadata
        return vector_id

    def get_by_id(self, vector_id):
        if vector_id not in self.id_to_index:
            raise KeyError(f"未找到ID为{vector_id}的向量")
        index = self.id_to_index[vector_id]
        return {
            "vector_id": vector_id,
            "vector": self.vectors[index].tolist(),
            "metadata": self.metadata.get(vector_id, {})
        }

    def update(self, vector_id, new_vector=None, new_metadata=None):
        if vector_id not in self.id_to_index:
            raise KeyError(f"未找到ID为{vector_id}的向量")
        index = self.id_to_index[vector_id]
        if new_vector is not None:
            new_vector = np.array(new_vector, dtype=np.float32).flatten()
            self._check_vector_dim(new_vector)
            self.vectors[index] = new_vector
        if new_metadata is not None:
            self.metadata[vector_id] = new_metadata

    def delete(self, vector_id):
        if vector_id not in self.id_to_index:
            raise KeyError(f"未找到ID为{vector_id}的向量")
        index = self.id_to_index[vector_id]
        self.vectors = np.delete(self.vectors, index, axis=0)
        self.vector_ids.pop(index)
        del self.id_to_index[vector_id]
        if vector_id in self.metadata:
            del self.metadata[vector_id]
        self.id_to_index = {vid: idx for idx, vid in enumerate(self.vector_ids)}

    def brute_force_search(self, query_vector, top_k=5):
        if len(self.vectors) == 0:
            return []
        query_vector = np.array(query_vector, dtype=np.float32).flatten()
        self._check_vector_dim(query_vector)
        similarities = cosine_similarity([query_vector], self.vectors)[0]
        top_indices = np.argsort(similarities)[::-1][:top_k]
        results = []
        for idx in top_indices:
            vector_id = self.vector_ids[idx]
            results.append({
                "vector_id": vector_id,
                "similarity": float(similarities[idx]),
                "metadata": self.metadata.get(vector_id, {})
            })
        return results

    def build_ivf_index(self, n_clusters=8):
        if len(self.vectors) == 0:
            raise ValueError("数据库中无向量数据，无法构建索引")
        vectors_for_kmeans = self.vectors.astype(np.float64)
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(vectors_for_kmeans)
        self.ivf_index = {i: [] for i in range(n_clusters)}
        for idx, label in enumerate(cluster_labels):
            self.ivf_index[label].append(idx)
        self.ivf_kmeans = kmeans

    def ivf_search(self, query_vector, top_k=5):
        if self.ivf_index is None:
            raise ValueError("请先调用build_ivf_index()构建IVF索引")
        if len(self.vectors) == 0:
            return []
        query_vector = np.array(query_vector, dtype=np.float64).flatten()
        self._check_vector_dim(query_vector)
        cluster_id = self.ivf_kmeans.predict([query_vector])[0]
        cluster_indices = self.ivf_index[cluster_id]
        if not cluster_indices:
            return []
        cluster_vectors = self.vectors[cluster_indices]
        similarities = cosine_similarity([query_vector], cluster_vectors)[0]
        top_cluster_indices = np.argsort(similarities)[::-1][:top_k]
        results = []
        for idx in top_cluster_indices:
            original_idx = cluster_indices[idx]
            vector_id = self.vector_ids[original_idx]
            results.append({
                "vector_id": vector_id,
                "similarity": float(similarities[idx]),
                "metadata": self.metadata.get(vector_id, {}),
                "cluster_id": int(cluster_id)
            })
        return results

    def save(self):
        data = {
            "vector_dim": self.vector_dim,
            "vectors": self.vectors,
            "vector_ids": self.vector_ids,
            "id_to_index": self.id_to_index,
            "metadata": self.metadata,
            "ivf_index": self.ivf_index,
            "ivf_kmeans": self.ivf_kmeans
        }
        with open(self.db_path, "wb") as f:
            pickle.dump(data, f)

    @classmethod
    def load(cls, db_path="vector_db.pkl"):
        with open(db_path, "rb") as f:
            data = pickle.load(f)
        db = cls(vector_dim=data["vector_dim"], db_path=db_path)
        db.vectors = data["vectors"]
        db.vector_ids = data["vector_ids"]
        db.id_to_index = data["id_to_index"]
        db.metadata = data["metadata"]
        db.ivf_index = data["ivf_index"]
        db.ivf_kmeans = data.get("ivf_kmeans")
        return db
```

## 使用示例：文本向量检索

使用 GTE 中文文本向量模型将文本转为向量并检索。

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("./model/iic/nlp_gte_sentence-embedding_chinese-base")

db = SimpleVectorDB(vector_dim=768)

sentences = [
    "向量数据库是AI时代的核心基础设施",
    "HNSW是一种高性能的近似最近邻搜索算法",
    "RAG通过检索增强生成提升大模型回答准确性",
    "Faiss支持GPU加速大规模向量检索",
    "Milvus是云原生分布式向量数据库",
]

embeddings = model.encode(sentences)
for sentence, embedding in zip(sentences, embeddings):
    db.insert(embedding, metadata={"text": sentence})

db.build_ivf_index(n_clusters=2)

query = "什么算法搜索向量最快？"
query_vec = model.encode(query)

print("=== 暴力检索 ===")
for res in db.brute_force_search(query_vec, top_k=3):
    print(f"相似度: {res['similarity']:.4f} | {res['metadata']['text']}")

print("\n=== IVF 检索 ===")
for res in db.ivf_search(query_vec, top_k=3):
    print(f"相似度: {res['similarity']:.4f} | 簇{res['cluster_id']} | {res['metadata']['text']}")

db.save()
loaded_db = SimpleVectorDB.load()
```

## 核心设计要点

### 数据存储结构

- `vectors`：NumPy 数组，形状 [N, dim]，存储所有向量
- `vector_ids`：UUID 列表，与 vectors 行下标一一对应
- `id_to_index`：字典，ID → 下标映射，O(1) 查找
- `metadata`：字典，ID → 元数据字典

### 暴力检索 vs IVF 检索

| 维度 | 暴力检索 | IVF 检索 |
|------|---------|---------|
| 精度 | 100% | 近似（可能漏检其他簇的近邻） |
| 速度 | O(N) | O(N/n_clusters) |
| 预处理 | 无 | 需 K-Means 聚类训练 |
| 适合规模 | 万级以下 | 万级到百万级 |

### 与工业级向量数据库的差距

这个 Mini Vector DB 仅实现核心逻辑，工业级系统（Milvus、Faiss）还具备：

- 分布式存储与并行计算（亿级以上向量）
- 更多索引算法（HNSW、PQ 的优化实现）
- 向量与结构化数据的混合查询
- 高可用与容错（副本、备份、故障恢复）
- RESTful API / 多语言 SDK
- 并发控制和事务支持

## 延伸阅读

- [向量检索基础](/datawhale/easy-vecdb/concepts/vector-retrieval-basics.md) — 相似度度量和维度灾难
- [IVF 与 PQ 量化](/datawhale/easy-vecdb/concepts/ivf-pq-quantization.md) — IVF 算法原理详解
- [Faiss 与 Milvus 工程实践](/datawhale/easy-vecdb/concepts/faiss-milvus-engineering.md) — 工业级实现
