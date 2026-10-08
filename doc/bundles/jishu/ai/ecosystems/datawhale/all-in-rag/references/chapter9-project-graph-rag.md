---
type: reference
title: "第九章 项目实战一优化（选修篇）"
bundle: /datawhale/all-in-rag
description: "图RAG架构优化——Neo4j知识图谱+Milvus向量库双引擎、图数据建模、智能查询路由与检索策略、多跳推理与子图提取"
source: https://github.com/datawhalechina/all-in-rag/blob/main/docs/chapter9/
path: docs/chapter9/
code:
  - code/C9/
tags: [graph-rag, neo4j, milvus, knowledge-graph, query-routing, multi-hop, intelligent-router]
status: stable
---

# 第九章 项目实战一优化（选修篇）

## 信源信息

- **章节路径**：`docs/chapter9/`
- **代码路径**：`code/C9/`
- **小节列表**：
  - 图RAG架构设计（`01_graph_rag_architecture.md`）
  - 图数据建模与准备（`02_graph_data_modeling.md`）
  - Milvus索引构建（`03_index_construction.md`）
  - 智能查询路由与检索策略（`04_intelligent_query_routing.md`）

## 内容概要

### 第一节 图RAG架构设计

- 基础 RAG 的局限：无法捕捉实体关系、难以多跳推理
- Graph RAG 双引擎架构：Neo4j 图数据库 + Milvus 向量数据库
- 智能路由：根据查询特征自动选择传统检索、图检索或组合策略

### 第二节 图数据建模与准备

- 菜谱知识图谱建模：菜品、食材、步骤、分类实体及关系
- Neo4j 图数据加载与构建
- 从图结构数据构建可检索文档

### 第三节 Milvus索引构建

- Milvus 集合创建与管理
- 向量索引构建（替代第八章的 FAISS）
- 元数据字段设计

### 第四节 智能查询路由与检索策略

- 查询复杂度分析（query_complexity）
- 关系密集度评估（relationship_intensity）
- 三种路由策略：hybrid_traditional、graph_rag、combined
- 图 RAG 检索：多跳遍历、子图提取、关系推理
- 混合检索：向量+稀疏双路召回
- 结果融合与排序

## 代码资产

| 文件 | 职责 |
|------|------|
| `code/C9/main.py` | AdvancedGraphRAGSystem 主类 |
| `code/C9/config.py` | GraphRAGConfig 配置 |
| `code/C9/rag_modules/graph_data_preparation.py` | 图数据准备 |
| `code/C9/rag_modules/graph_indexing.py` | 图索引构建 |
| `code/C9/rag_modules/graph_rag_retrieval.py` | 图RAG检索（多跳/子图） |
| `code/C9/rag_modules/hybrid_retrieval.py` | 传统混合检索 |
| `code/C9/rag_modules/intelligent_query_router.py` | 智能查询路由器 |
| `code/C9/rag_modules/milvus_index_construction.py` | Milvus向量索引 |
| `code/C9/rag_modules/generation_integration.py` | 自适应生成 |
| `code/C9/agent(代码系ai生成)/` | AI生成的菜谱Agent扩展 |

## 对应概念与示例

- [项目实战](../concepts/project-practice.md)
- [Graph RAG食谱问答系统](../examples/c9-graph-rag.md)
