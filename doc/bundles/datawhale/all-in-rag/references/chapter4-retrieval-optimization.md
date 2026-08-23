---
type: reference
title: "第四章 检索优化"
bundle: /datawhale/all-in-rag
description: "混合检索（稠密+稀疏/RRF融合）、查询构建（元数据过滤/Text2SQL）、查询重构与分发（LLM/Embedding路由）、检索进阶重排技术（RRF/RankLLM/Cross-Encoder/ColBERT）"
source: https://github.com/datawhalechina/all-in-rag/blob/main/docs/chapter4/
path: docs/chapter4/
code:
  - code/C4/
tags: [hybrid-search, bm25, rrf, text2sql, routing, reranking, cross-encoder, colbert]
status: stable
---

# 第四章 检索优化

## 信源信息

- **章节路径**：`docs/chapter4/`
- **代码路径**：`code/C4/`
- **小节列表**：
  - 第一节 混合检索（`11_hybrid_search.md`）
  - 第二节 查询构建（`12_query_construction.md`）
  - 第三节 Text2SQL（`13_text2sql.md`）
  - 第四节 查询重构与分发（`14_query_rewriting.md`）
  - 第五节 检索进阶技术（`15_advanced_retrieval_techniques.md`）

## 内容概要

### 第一节 混合检索

- 稠密检索（Dense，向量语义匹配）与稀疏检索（Sparse，BM25 关键词匹配）
- RRF（Reciprocal Rank Fusion）倒数排名融合算法
- 混合检索优势：兼顾语义理解和精确匹配

### 第二节 查询构建

- 元数据过滤：从自然语言提取结构化条件，检索前缩小范围
- Text2SQL：自然语言转 SQL 查询，访问结构化数据库

### 第三节 Text2SQL

- 完整 Text2SQL 实现：知识库（DB描述+DDL+SQL示例）→ SQL 生成器 → Agent
- LLM 基于上下文生成正确 SQL
- 代码位于 `code/C4/text2sql/` 子模块

### 第四节 查询重构与分发

- 查询重写：LLM 优化模糊/口语化查询
- LLM-based Routing：LLM 判断查询类型选择检索策略
- Embedding-based Routing：嵌入相似度匹配路由

### 第五节 检索进阶技术（重排序）

- **RRF**：多检索器排名融合，零样本无需训练
- **RankLLM**：LLM 直接对候选文档排序评分
- **Cross-Encoder**：查询-文档联合编码，精度最高但延迟高
- **ColBERT**：独立编码+Token级后期交互（MaxSim），平衡精度与效率
- 四种重排方法对比（机制、精度、速度、适用场景）

## 代码资产

| 文件 | 职责 |
|------|------|
| `code/C4/01_hybrid_search.py` / `_v2.py` | 混合检索 |
| `code/C4/02/04_text_to_metadata_filter.py` | 元数据过滤 |
| `code/C4/03_text2sql_demo.py` / `_v2.py` | Text2SQL 演示 |
| `code/C4/05_llm_based_routing.py` | LLM 路由 |
| `code/C4/06_embedding_based_routing.py` | Embedding 路由 |
| `code/C4/07_rerank_and_refine.py` | 重排优化 |
| `code/C4/text2sql/` | Text2SQL 子模块 |

## 对应概念

- [检索进阶技术](../concepts/retrieval-advanced.md)
