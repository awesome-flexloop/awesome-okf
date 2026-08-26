# EasyVecDB 概念文档索引

本目录包含向量数据库的核心概念文档，建议按顺序阅读。

## 基础理论

| 文档 | 说明 |
|------|------|
| [vector-retrieval-basics.md](vector-retrieval-basics.md) | 向量嵌入（Word2Vec/BERT）、相似度度量（L2/IP/Cosine）、维度灾难、暴力搜索 |
| [ann-algorithms.md](ann-algorithms.md) | ANN 核心思想、六大索引分类、精度-速度-内存三角权衡 |

## 算法深入

| 文档 | 说明 |
|------|------|
| [ivf-pq-quantization.md](ivf-pq-quantization.md) | IVF 倒排索引（K-Means/nprobe）、PQ 乘积量化（码本/查表）、IVF-PQ 混合索引 |
| [hnsw-lsh.md](hnsw-lsh.md) | HNSW 分层小世界图（M/efSearch）、LSH 局部敏感哈希（汉明距离/多哈希表） |

## 工具实践

| 文档 | 说明 |
|------|------|
| [annoy-practice.md](annoy-practice.md) | Spotify 轻量 ANN 库、随机投影树、mmap 内存映射、多进程共享、API 调优 |
| [faiss-milvus-engineering.md](faiss-milvus-engineering.md) | Faiss 高性能检索库（GPU/索引/调优）、Milvus 分布式数据库（架构/API/AI应用） |

```{toctree}
:maxdepth: 7

ann-algorithms
annoy-practice
faiss-milvus-engineering
hnsw-lsh
ivf-pq-quantization
vector-retrieval-basics
```
