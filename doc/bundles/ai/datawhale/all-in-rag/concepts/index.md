# 核心概念

本目录包含 All-in-RAG 教程的 7 个核心概念，按 RAG 技术链路排列：从架构概述到数据准备、索引构建、检索优化、生成集成、评估体系，最终通过项目实战串联全链路。

## 基础理论

* [RAG 概述与架构](rag-overview.md) — RAG 核心定义、双阶段架构、Naive/Advanced/Modular 三阶段演进、RAG vs 微调选型。对应第一章。
* [数据准备与处理](data-preparation.md) — Unstructured 多格式文档加载、Character/Recursive/Semantic 三种分块策略、父子文档分块。对应第二章。

## 索引与检索

* [索引构建](index-construction.md) — BGE 向量嵌入、Visual-BGE 多模态嵌入、FAISS/Milvus 向量数据库、句子窗口与递归检索优化。对应第三章。
* [检索进阶技术](retrieval-advanced.md) — 混合检索（稠密+稀疏）、元数据过滤、Text2SQL、查询重写与路由、RRF/RankLLM/Cross-Encoder/ColBERT 四种重排。对应第四章。

## 生成与评估

* [生成与重排](generation-rerank.md) — Pydantic 结构化输出、Function Calling、查询路由驱动的差异化生成、重排与生成的协同。对应第五章。
* [评估体系](evaluation-system.md) — RAG 三元组（上下文相关性/忠实度/答案相关性）、Precision@k/Recall@k/F1/MRR/MAP 指标、RAGAS/TruLens/LlamaIndex 评估工具。对应第六章。

## 综合实战

* [项目实战](project-practice.md) — 第八章"尝尝咸淡"基础 RAG（FAISS+混合检索+查询路由）到第九章 Graph RAG（Neo4j+Milvus 双引擎+智能路由+多跳推理）的完整实战。对应第八、九章。

```{toctree}
:maxdepth: 7

data-preparation
evaluation-system
generation-rerank
index-construction
project-practice
rag-overview
retrieval-advanced
```
