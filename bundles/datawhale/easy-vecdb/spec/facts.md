---
sources:
  - https://github.com/datawhalechina/easy-vecdb/blob/main/README.md
  - https://github.com/datawhalechina/easy-vecdb/blob/main/docs/index.md
  - https://github.com/datawhalechina/easy-vecdb/blob/main/src/README.md
type: Facts
okf_version: '0.2'
title: easy-vecdb 文档事实清单
generated: '2026-08-23'
tags:
  - facts
  - vector-database
---

# easy-vecdb 文档事实清单

> R阶段产出：基于 README.md、docs/index.md、src/README.md 及 docs/ 目录结构的零推测事实记录。

## 项目元数据

- F-001: 项目名称 EasyVecDB，定位为"从零开始的向量数据库原理与实践教程"
- F-002: 项目由 Datawhale 社区维护，采用 CC BY-NC-SA 4.0 开源协议
- F-003: 源码仓库地址 https://github.com/datawhalechina/easy-vecdb
- F-004: 在线文档地址 https://datawhalechina.github.io/easy-vecdb/
- F-005: 项目覆盖三大方向：理论入门（向量数据库原理、架构与索引机制）、实战教程（Milvus/Faiss/Annoy 使用与优化）、项目案例（RAG、嵌入检索、聚类可视化）
- F-006: 文档使用 VitePress 构建，配置位于 docs/.vitepress/config.js

## docs/ 目录章节结构

### 第一部分：基础学习篇（base/）

- F-007: base/chapter1/ 包含 `项目介绍.md` 和 `学习路径推荐.md`
- F-008: base/chapter2/ `为什么需要向量数据库.md` — 检索瓶颈、相似度搜索原理、LLM 与向量数据库协同（RAG）
- F-009: base/chapter3/ `向量嵌入算法基础.md` — Word2Vec、GloVe 静态嵌入；BERT、GPT 动态嵌入；含 Python 代码实战
- F-010: base/chapter4/ `向量搜索算法基础.md` — 欧氏距离、内积、余弦相似度、归一化；暴力搜索；维度灾难
- F-011: base/chapter5/ 包含 6 个文件：
  - `ANN搜索算法.md` — 索引类型总览（空间划分/图索引/量化压缩/哈希/混合/磁盘分布式）、IVF/HNSW/PQ/LSH/混合索引详解
  - `IVF算法.md` — IVF 倒排文件索引
  - `PQ算法.md` — 乘积量化
  - `HNSW算法.md` — 分层可导航小世界图
  - `LSH算法.md` — 局部敏感哈希
  - `Annoy算法.md` — Annoy 随机投影树
- F-012: base/chapter6/ `实现你自己的向量数据库.md` — Python 手写 Mini Vector DB，含向量存储、CRUD、暴力检索、IVF 索引、持久化

### 第二部分：Annoy 教程（Annoy/）

- F-013: Annoy/chapter1/ `Annoy入门与环境搭建.md` — Spotify 开源的轻量级 ANN 库，mmap 内存映射、多进程共享
- F-014: Annoy/chapter2/ `Annoy核心API详解.md` — 索引构建、查询、参数调优
- F-015: Annoy/chapter3/ `Annoy进阶技巧与最佳实践.md` — 性能优化、工程实践

### 第三部分：Faiss 教程（Faiss/）

- F-016: Faiss/chapter1/ `FAISS入门与环境搭建.md` — Meta AI 研发的向量相似性搜索库；与 Milvus/Chroma 对比；CPU/GPU 安装
- F-017: Faiss/chapter2/ `FAISS数据结构与索引.md` — Flat、IVF、PQ、HNSW 等索引类型
- F-018: Faiss/chapter3/ `FAISS核心功能进阶.md` — 复合索引、GPU 加速、批量检索
- F-019: Faiss/chapter4/ `FAISS性能调优与评估.md` — Recall、延迟、内存调优
- F-020: Faiss/chapter5/ `FAISS工程化落地实战.md` — 工程结构、服务化、实战案例

### 第四部分：Milvus 教程（Milvus/）

- F-021: Milvus/chapter1/ `Milvus向量数据库入门.md` — 架构设计、核心组件（Proxy/Query Node/Data Node/Index Node）、Lite/Standalone/Distributed 三版本对比
- F-022: Milvus/chapter2/ `Milvus核心概念.md` — Collection、Partition、Index 数据模型与索引体系
- F-023: Milvus/chapter3/ `PyMilvus核心API实战.md` — 数据写入、查询、索引管理
- F-024: Milvus/chapter4/ `Milvus的AI应用开发.md` — 基于 BM25 的混合搜索、RAG 应用
- F-025: Milvus/chapter5/ 包含 `1_build_text_image_search_engine.ipynb` 和 `Milvus的AI应用开发.md` — 图像检索应用
- F-026: Milvus/chapter6/ 包含 5 个文件：
  - `Milvus底层架构详解.md`
  - `Milvus Reranker重排.md`
  - `Milvus Lite部署与应用.md`
  - `MinerU部署教程.md`
  - `milvus 存储优化.md`

### 第五部分：实战项目（projects/）

- F-027: projects/project1/ — 基于 Annoy 的推荐系统召回（Annoy + DSSM），含 ml-1m_sample.csv 和 project1.ipynb
- F-028: projects/project2/ — 基于 FAISS 框架 RAG 实战，含 rag/ 模块（Embeddings.py、faiss_db.py、llm.py、prompt.py、utils.py）、main.py、requirements.txt
- F-029: projects/project3/ — 基于 Milvus 框架的 Agent 项目，含 project3.ipynb
- F-030: projects/project4/ — 基于 Milvus 和 ArangoDB 的 RAG 系统，含 movie_item.ann 和 project4.ipynb
- F-031: projects/index.md — 项目导航页

### 第六部分：补充内容（more/）

- F-032: more/chapter1/ `GPU加速检索-基于FusionANNS.md` — GPU 加速检索系统架构
- F-033: more/chapter2/ `Meta-Chunking：一种新的文本切分策略.md` — 智能文本切分算法
- F-034: more/chapter3/ `Limit基于嵌入检索的理论极限.md` — 向量检索性能边界分析，含 code/ 和 result/ 子目录
- F-035: more/chapter4/ `RabitQ：用于近似最近邻搜索的带理论误差界的高维向量量化.md` — 高维向量量化方法
- F-036: more/chapter5/ `向量.md` — 向量基础概念与数学原理，含 book/ 和 code/colBert/ 子目录
- F-037: more/chapter6/ 包含 `K-mean算法详解.md` 和 `聚类算法介绍.md`
- F-038: more/ 下另有 `milvus 数据切分总结.md`

## src/ 目录结构

- F-039: src/ANN_alorithms/ 包含 5 个 Jupyter Notebook：Annoy算法、HNSW算法、IVF算法、LSH算法、PQ算法
- F-040: src/Cre_milvus/ 是 Milvus 部分的主项目，包含：
  - ColBuilder/（可视化）、IndexParamBuilder/（索引参数构建）、Search/（ES/clustering/embedding/milvusSer/redisSer/search/search_optimization）
  - System/（Retry/cluster_utils/eval/init/monitor/start）、dataBuilder/（chunking/meta_chunking + tools/csvmake/imgmake/mdmake/pdfmake/txtmake）
  - milvusBuilder/（connection_manager/fast_insert/lazy_connection/persistent_connection）
  - multimodal/（clip_encoder）、reorder/（reo_clu）、testing/（locust_manager/locust_test/performance_monitor）
  - backend_api.py、config.yaml、config_loader.py、frontend.py、simple_milvus.py、start_simple.py
- F-041: src/HDBSCAN/ — 数据聚类可视化，含 pipeline_hdbscan_umap.py
- F-042: src/Meta_chunking/ — Meta-chunking 论文代码 demo，含 app.py、chunk_rag.py、perplexity_chunking.py
- F-043: src/faissSear/ — Faiss 搜索应用，含 app.py 和 template/index.html
- F-044: src/graph_rag/ — 基于 Neo4j 的图 RAG，支持 annoy/faiss/milvus 三种向量库，含 docker-compose.yml、rag_code/
- F-045: src/README.md 记录了实践项目清单和数据集构建要求（噪声/去重/标准化/安全合规/分块策略/模型适配/索引优化）

## 核心知识点覆盖

- F-046: 向量相似性度量：欧氏距离（L2）、内积（IP）、余弦相似度（Cosine）；L2 归一化后 L2 与 IP 排序等价
- F-047: 维度灾难：高维空间中点间距离趋同，最近邻与平均距离比值逼近 1；余弦相似度因方向不变性比欧氏距离更鲁棒
- F-048: ANN 索引六大分类：空间划分类（IVF/KD-Tree/Annoy）、图索引类（HNSW/NSG）、量化压缩类（PQ/OPQ/SQ）、哈希类（LSH/SimHash）、混合索引（IVF+PQ/HNSW+PQ）、磁盘/分布式扩展（DiskANN/SPANN/ScaNN）
- F-049: IVF 通过 K-Means 聚类划分向量空间，搜索时只查 nprobe 个最近簇；核心参数 nlist（簇数）和 nprobe（探测簇数）
- F-050: PQ 将高维向量分块后分别量化为子码本编号，通过查表法估算距离，压缩率可达 1/10；常与 IVF 组合为 IVF-PQ
- F-051: HNSW 构建多层小世界图，从稀疏层向密集层逐层导航搜索；参数 M（每层最大连接数）、efConstruction（构建时搜索宽度）、efSearch（查询时搜索宽度）
- F-052: LSH 通过局部敏感哈希函数将相似向量映射到相同桶，用汉明距离快速比较；适合粗筛阶段
- F-053: Annoy 基于多棵随机投影树，支持 mmap 内存映射和多进程共享，适合静态只读数据，不支持增量更新
- F-054: Faiss 是 Meta AI 的向量检索库（非完整数据库），支持 CPU/GPU，内置 Flat/IVF/PQ/HNSW 等索引，适合作为底层检索引擎
- F-055: Milvus 是云原生分布式向量数据库，支持三种部署模式（Lite/Standalone/Distributed），微服务架构（Proxy/Query Node/Data Node/Index Node），支持亿级到百亿级向量
- F-056: 向量数据库六大核心模块：向量存储、索引、相似度计算、查询引擎、元数据管理、持久化
