---
title: EasyVecDB — 向量数据库原理与实践教程
type: index
bundle: easy-vecdb
description: 从零开始的向量数据库系统性学习教程，覆盖向量检索基础、ANN 算法（IVF/PQ/HNSW/LSH）、Annoy/Faiss/Milvus 工程实践及 RAG 项目案例
concepts:
  - concepts/vector-retrieval-basics.md
  - concepts/ann-algorithms.md
  - concepts/ivf-pq-quantization.md
  - concepts/hnsw-lsh.md
  - concepts/annoy-practice.md
  - concepts/faiss-milvus-engineering.md
references:
  - references/docs-chapters.md
  - references/source-code-map.md
examples:
  - examples/mini-vector-db.md
  - examples/rag-with-faiss.md
  - examples/milvus-getting-started.md
sources:
  - https://github.com/datawhalechina/easy-vecdb
tags:
  - vector-database
  - ann
  - faiss
  - milvus
  - annoy
  - rag
okf_version: '0.2'
generated: '2026-08-23'
---

# EasyVecDB — 向量数据库原理与实践教程

[EasyVecDB](https://github.com/datawhalechina/easy-vecdb) 是 Datawhale 社区出品的向量数据库系统性学习教程，覆盖从基础概念、算法原理到生产级应用部署的全流程。本知识束基于教程文档提炼，帮助开发者快速掌握向量检索核心技术。

## 概念文档（concepts/）

| 概念 | 说明 |
|------|------|
| [向量检索基础](concepts/vector-retrieval-basics.md) | 向量嵌入（Word2Vec/BERT）、相似度度量（L2/IP/Cosine）、维度灾难、暴力搜索 |
| [ANN 近似最近邻算法](concepts/ann-algorithms.md) | ANN 核心思想、六大索引分类（空间划分/图/量化/哈希/混合/分布式）、精度-速度-内存权衡 |
| [IVF 与 PQ 量化](concepts/ivf-pq-quantization.md) | IVF 倒排文件索引（K-Means 聚类/nprobe）、PQ 乘积量化（分块/码本/查表）、IVF-PQ 混合索引 |
| [HNSW 与 LSH](concepts/hnsw-lsh.md) | HNSW 分层小世界图（M/efConstruction/efSearch）、LSH 局部敏感哈希（汉明距离/桶查找） |
| [Annoy 实践](concepts/annoy-practice.md) | Spotify 开源的轻量级 ANN 库、随机投影树、mmap 内存映射、多进程共享、API 与调优 |
| [Faiss 与 Milvus 工程实践](concepts/faiss-milvus-engineering.md) | Faiss 高性能检索库（GPU/索引类型/性能调优）、Milvus 分布式向量数据库（架构/三版本/API） |

## 实践示例（examples/）

| 示例 | 说明 |
|------|------|
| [手写 Mini Vector DB](examples/mini-vector-db.md) | 用 numpy + sklearn 实现向量数据库，含 CRUD、暴力检索、IVF 索引、持久化 |
| [基于 Faiss 的 RAG 实战](examples/rag-with-faiss.md) | 使用 FAISS 构建检索增强生成系统，含嵌入、索引、检索、LLM 生成全流程 |
| [Milvus 快速入门](examples/milvus-getting-started.md) | PyMilvus 核心 API 实战：Collection 创建、数据插入、索引构建、向量搜索 |

## 信源参考（references/）

| 信源 | 说明 |
|------|------|
| [教程章节登记](references/docs-chapters.md) | docs/ 目录全部章节路径与内容摘要 |
| [源码结构映射](references/source-code-map.md) | src/ 目录代码项目结构与核心模块说明 |

## 推荐学习路径

1. **基础入门**：[向量检索基础](concepts/vector-retrieval-basics.md) → [ANN 近似最近邻算法](concepts/ann-algorithms.md)
2. **算法深入**：[IVF 与 PQ 量化](concepts/ivf-pq-quantization.md) → [HNSW 与 LSH](concepts/hnsw-lsh.md)
3. **工具实践**：[Annoy 实践](concepts/annoy-practice.md) → [Faiss 与 Milvus 工程实践](concepts/faiss-milvus-engineering.md)
4. **动手项目**：[手写 Mini Vector DB](examples/mini-vector-db.md) → [RAG 实战](examples/rag-with-faiss.md)

## 核心洞察

- **精度-速度-内存三角权衡**：所有 ANN 算法都在三者间取舍，不存在同时最优的方案
- **从算法到工程的递进**：相似度度量 → 索引算法 → 检索库 → 分布式系统，需逐级深入
- **嵌入质量决定上限**：索引只决定能否接近上限，嵌入模型和分块策略才是效果天花板
- **选型三维定位**：Annoy（轻量只读）、Faiss（高性能引擎）、Milvus（分布式数据库）各有适用场景
- **RAG 是杀手级应用**：向量数据库因 LLM 崛起成为 AI 基础设施，RAG 串联全链路

```{toctree}
:hidden:

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
