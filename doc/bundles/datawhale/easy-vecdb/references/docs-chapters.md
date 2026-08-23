---
title: 教程章节登记
type: reference
bundle: /datawhale/easy-vecdb
description: easy-vecdb 项目 docs/ 目录全部章节的路径、标题与内容摘要登记
sources:
  - https://github.com/datawhalechina/easy-vecdb/tree/main/docs
tags:
  - reference
  - docs
---

# 教程章节登记

本文件登记 easy-vecdb 项目 `docs/` 目录下的全部章节，供概念文档溯源引用。

## 第一部分：基础学习篇（base/）

| 章节路径 | 标题 | 内容摘要 |
|---------|------|---------|
| `base/chapter1/项目介绍.md` | 项目介绍 | 项目目标、整体学习路径推荐 |
| `base/chapter1/学习路径推荐.md` | 学习路径推荐 | 分阶段学习建议 |
| `base/chapter2/为什么需要向量数据库.md` | 为什么需要向量数据库 | LLM 高维处理缺陷、传统数据库瓶颈、向量数据库原理、RAG 协同效应、应用场景 |
| `base/chapter3/向量嵌入算法基础.md` | 向量嵌入算法基础 | Word2Vec/GloVe 静态嵌入、BERT/GPT 动态嵌入、Python 代码验证多义词语境差异 |
| `base/chapter4/向量搜索算法基础.md` | 向量搜索算法基础 | 欧氏距离/内积/余弦相似度、归一化、暴力搜索、维度灾难及代码模拟 |
| `base/chapter5/ANN搜索算法.md` | ANN 搜索算法 | 六大索引分类（空间划分/图/量化/哈希/混合/分布式）、IVF/HNSW/PQ/LSH/混合索引详解、ANN-Benchmarks |
| `base/chapter5/IVF算法.md` | IVF 算法 | IVF 倒排文件索引的原理与代码实战 |
| `base/chapter5/PQ算法.md` | PQ 算法 | 乘积量化的原理与代码实战 |
| `base/chapter5/HNSW算法.md` | HNSW 算法 | 分层可导航小世界图的原理与代码实战 |
| `base/chapter5/LSH算法.md` | LSH 算法 | 局部敏感哈希的原理与代码实战 |
| `base/chapter5/Annoy算法.md` | Annoy 算法 | Annoy 随机投影树的原理与代码实战 |
| `base/chapter6/实现你自己的向量数据库.md` | 实现你自己的向量数据库 | Python 手写 Mini Vector DB：CRUD、暴力检索、IVF 索引、持久化 |

## 第二部分：Annoy 教程（Annoy/）

| 章节路径 | 标题 | 内容摘要 |
|---------|------|---------|
| `Annoy/chapter1/Annoy入门与环境搭建.md` | Annoy 入门与环境搭建 | Annoy 简介（Spotify 开源、mmap、多进程共享）、pip/conda 安装、验证、常见问题 |
| `Annoy/chapter2/Annoy核心API详解.md` | Annoy 核心 API 详解 | AnnoyIndex 创建、add_item、build、save/load、get_nns_by_vector/item、参数说明 |
| `Annoy/chapter3/Annoy进阶技巧与最佳实践.md` | Annoy 进阶技巧与最佳实践 | n_trees/search_k 调优、内存映射、多进程部署、工程实践 |

## 第三部分：Faiss 教程（Faiss/）

| 章节路径 | 标题 | 内容摘要 |
|---------|------|---------|
| `Faiss/chapter1/FAISS入门与环境搭建.md` | FAISS 入门与环境搭建 | Faiss 定位（Meta AI 检索库）、与 Milvus/Chroma 对比、适用场景、CPU/GPU 安装 |
| `Faiss/chapter2/FAISS数据结构与索引.md` | FAISS 数据结构与索引 | IndexFlat、IVF、PQ、HNSW 等索引类型详解与代码示例 |
| `Faiss/chapter3/FAISS核心功能进阶.md` | FAISS 核心功能进阶 | 复合索引、GPU 加速、批量检索、高级功能 |
| `Faiss/chapter4/FAISS性能调优与评估.md` | FAISS 性能调优与评估 | Recall、QPS、延迟、内存调优方法与评估指标 |
| `Faiss/chapter5/FAISS工程化落地实战.md` | FAISS 工程化落地实战 | 工程结构、服务化封装、实战案例 |

## 第四部分：Milvus 教程（Milvus/）

| 章节路径 | 标题 | 内容摘要 |
|---------|------|---------|
| `Milvus/chapter1/Milvus向量数据库入门.md` | Milvus 向量数据库入门 | 向量数据库认知、Milvus 定位与优势、Lite/Standalone/Distributed 三版本、核心架构（Proxy/Query/Data/Index Node） |
| `Milvus/chapter2/Milvus核心概念.md` | Milvus 核心概念 | Collection、Partition、Index 数据模型与索引体系 |
| `Milvus/chapter3/PyMilvus核心API实战.md` | PyMilvus 核心 API 实战 | 连接、Collection 创建、数据写入、查询、索引管理 |
| `Milvus/chapter4/Milvus的AI应用开发.md` | Milvus 的 AI 应用开发 | 基于 BM25 的混合搜索、RAG 应用开发 |
| `Milvus/chapter5/Milvus的AI应用开发.md` | Milvus 的 AI 应用开发（图像检索） | 文搜图应用实战、CLIP 多模态嵌入 |
| `Milvus/chapter5/1_build_text_image_search_engine.ipynb` | 文本图像搜索引擎 Notebook | 图文检索完整代码 |
| `Milvus/chapter6/Milvus底层架构详解.md` | Milvus 底层架构详解 | 微服务组件、数据流、存储架构深入 |
| `Milvus/chapter6/Milvus Reranker重排.md` | Milvus Reranker 重排 | 检索结果重排技术 |
| `Milvus/chapter6/Milvus Lite部署与应用.md` | Milvus Lite 部署与应用 | 轻量级版本使用指南 |
| `Milvus/chapter6/MinerU部署教程.md` | MinerU 部署教程 | 文档解析工具部署 |
| `Milvus/chapter6/milvus 存储优化.md` | Milvus 存储优化 | 存储层性能优化策略 |

## 第五部分：实战项目（projects/）

| 章节路径 | 标题 | 内容摘要 |
|---------|------|---------|
| `projects/index.md` | 项目导航 | 实战项目总览 |
| `projects/project1/` | 基于 Annoy 的推荐系统召回 | Annoy + DSSM 推荐召回，含 MovieLens 数据 |
| `projects/project2/` | 基于 FAISS 框架 RAG 实战 | RAG 系统：Embeddings/faiss_db/llm/prompt/utils 模块 |
| `projects/project3/` | 基于 Milvus 框架的 Agent 项目 | Agent + Milvus 智能应用 |
| `projects/project4/` | 基于 Milvus 和 ArangoDB 的 RAG 系统 | 图 RAG：Milvus 向量 + ArangoDB 图数据库 |

## 第六部分：补充内容（more/）

| 章节路径 | 标题 | 内容摘要 |
|---------|------|---------|
| `more/chapter1/GPU加速检索-基于FusionANNS.md` | GPU 加速检索 - 基于 FusionANNS | GPU 加速检索系统架构设计 |
| `more/chapter2/Meta-Chunking：一种新的文本切分策略.md` | Meta-Chunking 文本切分策略 | PPL/MSP 智能文本切分算法 |
| `more/chapter3/Limit基于嵌入检索的理论极限.md` | Limit 基于嵌入检索的理论极限 | 向量检索性能边界分析 |
| `more/chapter4/RabitQ：用于近似最近邻搜索的带理论误差界的高维向量量化.md` | RabitQ 高维向量量化 | 带理论误差界的量化方法 |
| `more/chapter5/向量.md` | 向量基础知识 | 向量基础概念与数学原理 |
| `more/chapter6/聚类算法介绍.md` | 聚类算法介绍 | 聚类算法概述 |
| `more/chapter6/K-mean算法详解.md` | K-means 算法详解 | K-Means 聚类算法深入 |
| `more/milvus 数据切分总结.md` | Milvus 数据切分总结 | 数据分片实践经验 |

## 文档首页

| 文件 | 说明 |
|------|------|
| `docs/index.md` | VitePress 首页：项目介绍、四大特性（快速入门/实战驱动/开箱即用/持续更新）、学习收获 |
