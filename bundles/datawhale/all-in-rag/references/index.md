# 信源登记

本目录登记 All-in-RAG 教程的全部章节信源，共 10 章（第十章规划中）。每章对应 `docs/chapterN/` 目录和 `code/CN/` 代码目录。

## 第一部分：RAG基础入门

* [第一章 解锁RAG](chapter1-rag-intro.md) — RAG 核心概念、双阶段架构、三阶段演进（Naive/Advanced/Modular）、LangChain/LlamaIndex 快速上手。
* [第二章 数据准备](chapter2-data-preparation.md) — Unstructured 多格式文档加载、Character/Recursive/Semantic 三种分块策略。

## 第二部分：索引构建与优化

* [第三章 索引构建](chapter3-index-construction.md) — BGE 向量嵌入、Visual-BGE 多模态嵌入、FAISS/Milvus 向量数据库、句子窗口与递归检索优化。

## 第三部分：检索技术进阶

* [第四章 检索优化](chapter4-retrieval-optimization.md) — 混合检索（稠密+稀疏/RRF）、元数据过滤、Text2SQL、查询重写与路由、四种重排方法（RRF/RankLLM/Cross-Encoder/ColBERT）。

## 第四部分：生成与评估

* [第五章 生成集成](chapter5-generation.md) — Pydantic 结构化输出、Function Calling 函数调用。
* [第六章 RAG系统评估](chapter6-evaluation.md) — RAG 三元组（上下文相关性/忠实度/答案相关性）、Precision@k/Recall@k/F1/MRR/MAP 指标、RAGAS/TruLens/LlamaIndex 评估工具。

## 第五部分：高级应用与实战

* [第七章 高级RAG架构（拓展选修篇）](chapter7-advanced-rag.md) — 基于知识图谱的 RAG（KG-RAG）理论。
* [第八章 项目实战一（基础篇）](chapter8-project-basic.md) — "尝尝咸淡"食谱 RAG 系统（FAISS+混合检索+查询路由+流式生成）。
* [第九章 项目实战一优化（选修篇）](chapter9-project-graph-rag.md) — Graph RAG 优化（Neo4j+Milvus 双引擎+智能路由+多跳推理）。
* [第十章 项目实战二（选修篇）](chapter10-project-two.md) — 规划中。
