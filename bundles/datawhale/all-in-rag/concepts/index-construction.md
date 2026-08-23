---
type: concept
title: "索引构建"
bundle: /datawhale/all-in-rag
description: "向量嵌入（BGE）、多模态嵌入（Visual-BGE）、向量数据库（FAISS/Milvus）及索引优化技术（句子窗口、递归检索），构建高效检索的基础"
sources: https://github.com/datawhalechina/all-in-rag/blob/main/docs/chapter3/
related:
  - /datawhale/all-in-rag/concepts/data-preparation
  - /datawhale/all-in-rag/concepts/retrieval-advanced
  - /datawhale/all-in-rag/concepts/rag-overview
tags: [embedding, bge, multimodal, vector-database, faiss, milvus, index-optimization]
status: stable
---

# 索引构建

## 核心理解

索引构建是将非结构化文本（及多模态数据）转化为可高效检索的向量索引的过程，是 RAG 离线阶段的核心工作。第三章覆盖五个主题：**向量嵌入**（文本→向量）、**多模态嵌入**（图文→统一向量空间）、**向量数据库**（存储与检索引擎）、**Milvus 实践**（生产级部署）、**索引优化**（高级索引策略）。

## 向量嵌入

### 嵌入模型原理

嵌入模型将文本映射为高维稠密向量（如 768 维、1024 维），语义相近的文本在向量空间中距离更近。项目主要使用 **BGE**（BAAI General Embedding）系列模型，这是北京智源人工智能研究院开源的中英文嵌入模型。

### 关键概念

- **相似度计算**：余弦相似度（Cosine Similarity）最常用，衡量向量方向相似性
- **维度选择**：维度越高表达能力越强，但存储和计算成本也越高
- **模型选型**：BGE-large-zh 适合中文，BGE-M3 支持多语言和多功能（稠密+稀疏+多向量）

## 多模态嵌入

### Visual-BGE

传统 RAG 仅处理文本，多模态嵌入将图像和文本映射到同一向量空间，实现"以文搜图"和"以图搜文"。

项目中的 Visual-BGE 基于 EVA-CLIP 架构，支持：
- 文本查询 → 检索相关图片
- 图片查询 → 检索相关文本
- 图文混合检索

代码位于 `code/C3/visual_bge/`，包含完整的模型定义（`modeling.py`）和 EVA-CLIP  backbone 实现。

### 多模态检索实战

第三章通过 Dragon（龙）数据集演示多模态检索：
- 文本描述龙的特征 → 检索龙的图片
- 龙的图片 → 检索相关文本描述

## 向量数据库

### FAISS

Facebook AI Similarity Search，轻量级向量检索库：
- 优点：无需部署服务，本地库即可使用，适合开发和小规模场景
- 缺点：不支持持久化服务、分布式扩展、元数据过滤较弱
- 第八章实战使用 FAISS 作为向量索引

### Milvus

生产级向量数据库，通过 Docker 部署：
- 优点：支持海量向量、分布式架构、丰富索引类型、元数据过滤、多模态集合
- 缺点：需要 Docker 部署，运维成本较高
- 第九章 Graph RAG 实战使用 Milvus 作为向量引擎

### 选型建议

| 场景 | 推荐 |
|------|------|
| 本地开发/原型验证 | FAISS（Chroma 也可） |
| 生产环境/大规模数据 | Milvus（或 Qdrant、Weaviate） |
| 多模态检索 | Milvus（支持多向量字段） |

## Milvus 实践

项目提供 `code/docker-compose.yml` 一键部署 Milvus 服务。关键操作包括：

1. **集合（Collection）管理**：创建、加载、释放、删除
2. **数据插入**：向量 + 元数据批量写入
3. **向量检索**：相似度搜索 Top-K
4. **多模态集合**：同时存储文本向量和图像向量
5. **元数据过滤**：检索时结合标量字段过滤（如分类、难度）

## 索引优化

### 句子窗口检索（Sentence Window Retrieval）

- 索引时：按句子粒度嵌入（小块，检索精准）
- 检索时：命中句子后，返回其周围的上下文窗口（大块，生成质量高）
- 兼顾检索精度和上下文完整性

### 递归检索（Recursive Retrieval）

- 构建层次化索引：文档→章节→段落→句子
- 先粗检索定位大范围，再细检索定位具体片段
- 适合长文档和结构化文档

代码位于 `code/C3/05_sentence_window_retrieval.py` 和 `06_recursive_retrieval.py`。

## 代码实践

第三章代码位于 `code/C3/`：
- `01_bge_visualized.py`——BGE 嵌入可视化
- `02_langchain_faiss.py`——LangChain + FAISS
- `03_llamaindex_vector.py`——LlamaIndex 向量检索
- `04_multi_milvus.py`——Milvus 多模态
- `05_sentence_window_retrieval.py`——句子窗口检索
- `06/07_recursive_retrieval.py`——递归检索

## 延伸阅读

- [数据准备与处理](data-preparation.md)——索引构建的上游
- [检索进阶技术](retrieval-advanced.md)——索引构建后的检索优化
- [项目实战](project-practice.md)——FAISS 与 Milvus 的工程应用
