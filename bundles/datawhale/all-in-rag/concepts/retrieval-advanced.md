---
type: concept
title: "检索进阶技术"
bundle: /datawhale/all-in-rag
description: "混合检索（稠密+稀疏）、查询构建（元数据过滤/Text2SQL）、查询重构与分发（LLM/Embedding路由）、重排技术（RRF/RankLLM/Cross-Encoder/ColBERT）"
sources: https://github.com/datawhalechina/all-in-rag/blob/main/docs/chapter4/
related:
  - /datawhale/all-in-rag/concepts/index-construction
  - /datawhale/all-in-rag/concepts/generation-rerank
  - /datawhale/all-in-rag/concepts/rag-overview
  - /datawhale/all-in-rag/concepts/project-practice
tags: [hybrid-search, bm25, text2sql, reranking, rrf, cross-encoder, colbert, routing, query-rewriting]
status: stable
---

# 检索进阶技术

## 核心理解

基础向量检索存在固有限制：最相关的文档不总在检索结果顶端，纯语义匹配可能遗漏关键词精确匹配，复杂查询需要结构化数据支持。第四章系统讲解从 Advanced RAG 到 Modular RAG 的检索优化技术，涵盖五大主题：**混合检索**、**查询构建**、**Text2SQL**、**查询重构与分发**、**检索进阶（重排）**。

## 混合检索

### 稠密检索 vs 稀疏检索

- **稠密检索（Dense Retrieval）**：基于嵌入模型的向量相似度搜索，擅长语义匹配，但可能遗漏精确关键词
- **稀疏检索（Sparse Retrieval）**：基于词频的 BM25 算法，擅长精确关键词匹配，但无法理解同义词语义

### 融合策略

混合检索同时使用两种检索器，通过 **RRF（Reciprocal Rank Fusion，倒数排名融合）** 合并结果：

- 不依赖原始相似度分数（不同检索器分数尺度不同）
- 仅基于文档在各结果列表中的排名计算融合分数
- 公式：`score(d) = Σ 1/(k + rank_i(d))`，k 通常取 60

RRF 是零样本方法，无需训练，简单有效。

## 查询构建

### 元数据过滤（Metadata Filtering）

将自然语言查询中的结构化条件（分类、时间、难度等）转换为数据库过滤条件，在向量检索前缩小搜索范围。

例如："推荐几个简单的素菜" → 过滤条件 `{category: "素菜", difficulty: "简单"}` + 向量检索。

第八章实战实现了基于关键词的元数据过滤，从查询中提取分类和难度条件。

### Text2SQL

将自然语言转换为 SQL 查询，适用于结构化数据（关系型数据库）场景。第四章提供了完整的 Text2SQL 实现（`code/C4/text2sql/`）：

- **knowledge_base.py**：数据库描述、DDL 示例、SQL 示例的知识库
- **sql_generator.py**：基于 LLM 的 SQL 生成器
- **text2sql_agent.py**：Text2SQL Agent，整合知识库检索和 SQL 生成

Text2SQL 让 RAG 系统不仅能检索非结构化文档，还能查询结构化数据库中的精确数据。

## 查询重构与分发

### 查询重写（Query Rewriting）

用户原始查询可能表述模糊、缺少上下文或包含口语化表达。通过 LLM 将查询重写为更适合检索的形式：

- 扩展关键词和同义词
- 消除指代歧义
- 分解复杂问题为子查询

第八章实战中，根据查询路由类型决定是否重写：列表查询保持原样，详细查询和一般查询使用 LLM 智能重写。

### 查询路由（Query Routing）

Modular RAG 的核心能力——根据查询类型自动选择最优检索策略：

- **LLM-based Routing**：让 LLM 判断查询类型并选择路由（灵活但慢）
- **Embedding-based Routing**：将查询嵌入后与路由描述嵌入比较，选择最相似路由（快但灵活性低）

第九章的 `IntelligentQueryRouter` 进一步量化查询复杂度（query_complexity）和关系密集度（relationship_intensity），在传统混合检索、图 RAG 检索、组合策略之间智能选择。

## 重排序（Re-ranking）

初筛检索（First-stage Retrieval）追求速度，召回较多候选；重排（Second-stage Reranking）追求精度，对候选重新精细排序。第四章介绍四种重排方法：

### 1. RRF（Reciprocal Rank Fusion）

- 机制：融合多个检索器的排名信息
- 优点：零样本、无需模型、简单有效
- 缺点：仅用排名，忽略原始分数

### 2. RankLLM / LLM-based Reranker

- 机制：将候选文档摘要和查询交给 LLM，要求输出排序和相关性分数
- 优点：利用 LLM 强大的语义理解能力
- 缺点：延迟高、成本高、受 Prompt 影响大

### 3. Cross-Encoder（交叉编码器）

- 机制：将查询和文档拼接输入 Transformer，输出单一相关性分数
- 优点：精度最高，能捕捉查询-文档间的深层交互
- 缺点：N 次独立推理，延迟高（不适合大规模候选集）
- 常用模型：`ms-marco-MiniLM-L-12-v2`

### 4. ColBERT（Contextualized Late Interaction over BERT）

- 机制：查询和文档独立编码（可预计算文档向量），查询时计算 Token 级 MaxSim 后期交互
- 优点：在 Cross-Encoder 精度和 Bi-Encoder 效率间取得平衡
- 缺点：需要存储所有 Token 向量，存储成本较高

### 重排方法对比

| 特性 | RRF | RankLLM | Cross-Encoder | ColBERT |
|------|-----|---------|---------------|---------|
| 核心机制 | 融合排名 | LLM 推理排序 | 联合编码评分 | 独立编码+后期交互 |
| 精度 | 中 | 高 | 最高 | 高 |
| 速度 | 快 | 慢 | 最慢 | 中 |
| 是否需模型 | 否 | LLM | 专用模型 | 专用模型 |

## 代码实践

第四章代码位于 `code/C4/`：
- `01_hybrid_search.py`——混合检索
- `02/04_text_to_metadata_filter.py`——元数据过滤
- `03_text2sql_demo.py`——Text2SQL 演示
- `05_llm_based_routing.py`——LLM 路由
- `06_embedding_based_routing.py`——Embedding 路由
- `07_rerank_and_refine.py`——重排优化

## 延伸阅读

- [索引构建](index-construction.md)——检索优化的基础
- [生成与重排](generation-rerank.md)——检索后的生成集成
- [项目实战](project-practice.md)——混合检索和智能路由的工程实现
