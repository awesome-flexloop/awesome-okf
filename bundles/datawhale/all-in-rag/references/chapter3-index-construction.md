---
type: reference
title: "第三章 索引构建"
bundle: /datawhale/all-in-rag
description: "向量嵌入（BGE）、多模态嵌入（Visual-BGE）、向量数据库（FAISS/Milvus）、Milvus实践及索引优化（句子窗口/递归检索）"
source: https://github.com/datawhalechina/all-in-rag/blob/main/docs/chapter3/
path: docs/chapter3/
code:
  - code/C3/
tags: [embedding, bge, multimodal, faiss, milvus, sentence-window, recursive-retrieval]
status: stable
---

# 第三章 索引构建

## 信源信息

- **章节路径**：`docs/chapter3/`
- **代码路径**：`code/C3/`
- **小节列表**：
  - 第一节 向量嵌入（`06_vector_embedding.md`）
  - 第二节 多模态嵌入（`07_multimodal_embedding.md`）
  - 第三节 向量数据库（`08_vector_db.md`）
  - 第四节 Milvus实践（`09_milvus.md`）
  - 第五节 索引优化（`10_index_optimization.md`）

## 内容概要

### 第一节 向量嵌入

- BGE（BAAI General Embedding）系列模型原理
- 文本向量化、余弦相似度计算
- 嵌入模型选型（BGE-large-zh、BGE-M3 等）

### 第二节 多模态嵌入

- Visual-BGE 图文跨模态嵌入
- EVA-CLIP backbone 架构
- 以文搜图、以图搜文、图文混合检索

### 第三节 向量数据库

- FAISS（本地轻量级向量检索库）
- Milvus（生产级分布式向量数据库）
- Chroma、Qdrant、Weaviate 等选型对比

### 第四节 Milvus实践

- Docker 部署 Milvus
- 集合（Collection）创建与管理
- 多模态集合设计（文本向量+图像向量）
- 数据插入、向量检索、元数据过滤

### 第五节 索引优化

- 句子窗口检索（Sentence Window Retrieval）：句子粒度索引，窗口上下文返回
- 递归检索（Recursive Retrieval）：层次化索引，粗检→细检

## 代码资产

| 文件 | 职责 |
|------|------|
| `code/C3/01_bge_visualized.py` | BGE 嵌入可视化 |
| `code/C3/02_langchain_faiss.py` | LangChain + FAISS |
| `code/C3/03_llamaindex_vector.py` | LlamaIndex 向量检索 |
| `code/C3/04_multi_milvus.py` | Milvus 多模态检索 |
| `code/C3/05_sentence_window_retrieval.py` | 句子窗口检索 |
| `code/C3/06_recursive_retrieval.py` | 递归检索 v1 |
| `code/C3/07_recursive_retrieval_v2.py` | 递归检索 v2 |
| `code/C3/visual_bge/` | Visual-BGE 模型子模块 |

## 对应概念

- [索引构建](../concepts/index-construction.md)
