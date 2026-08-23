---
title: Faiss 与 Milvus 工程实践
type: concept
bundle: /datawhale/easy-vecdb
description: Faiss 高性能向量检索库（索引类型、GPU 加速、性能调优）与 Milvus 分布式向量数据库（架构、三版本部署、Collection/Partition/Index、PyMilvus API）的工程实践
related:
  - /datawhale/easy-vecdb/concepts/ann-algorithms
  - /datawhale/easy-vecdb/concepts/ivf-pq-quantization
  - /datawhale/easy-vecdb/concepts/hnsw-lsh
  - /datawhale/easy-vecdb/concepts/annoy-practice
  - /datawhale/easy-vecdb/examples/milvus-getting-started
sources:
  - https://github.com/datawhalechina/easy-vecdb/blob/main/docs/Faiss/chapter1/FAISS入门与环境搭建.md
  - https://github.com/datawhalechina/easy-vecdb/blob/main/docs/Faiss/chapter2/FAISS数据结构与索引.md
  - https://github.com/datawhalechina/easy-vecdb/blob/main/docs/Faiss/chapter4/FAISS性能调优与评估.md
  - https://github.com/datawhalechina/easy-vecdb/blob/main/docs/Milvus/chapter1/Milvus向量数据库入门.md
  - https://github.com/datawhalechina/easy-vecdb/blob/main/docs/Milvus/chapter2/Milvus核心概念.md
  - https://github.com/datawhalechina/easy-vecdb/blob/main/docs/Milvus/chapter3/PyMilvus核心API实战.md
tags:
  - faiss
  - milvus
  - engineering
  - distributed
  - gpu
---

# Faiss 与 Milvus 工程实践

Faiss 和 Milvus 是向量检索工程化的两大核心工具。Faiss 是 Meta AI 开源的高性能向量检索库，擅长算法实现和 GPU 加速；Milvus 是云原生分布式向量数据库，提供完整的数据库服务能力。二者定位互补，共同构成企业级向量检索的技术底座。

## Faiss：高性能向量检索库

### 核心定位

Faiss（Facebook AI Similarity Search）是 Meta AI 团队研发的开源向量相似性搜索库，专为大规模高维向量的快速检索设计。它是**检索库**而非完整数据库——不提供持久化、事务、权限管理、分布式等数据库特性，需自行封装。

### 核心优势

- **高效性**：百万到十亿级向量毫秒级响应
- **算法丰富**：内置精确检索与多种近似检索算法
- **硬件适配**：支持 CPU 与 GPU 加速，GPU 版本大幅提升批量处理能力
- **易用性**：简洁的 Python/C++ API
- **可扩展性**：部分索引支持动态增删

### Faiss 索引类型

| 索引 | 类型 | 说明 | 适用场景 |
|------|------|------|---------|
| **IndexFlatL2/IP** | 精确 | 暴力搜索，精度 100% | 小规模基线、验证 |
| **IndexIVFFlat** | IVF | 聚类划分，簇内精确搜索 | 中等规模，精度优先 |
| **IndexIVFPQ** | IVF+PQ | 聚类+乘积量化压缩 | 大规模，内存受限 |
| **IndexHNSWFlat** | HNSW | 分层小世界图 | 高召回低延迟 |
| **IndexHNSWPQ** | HNSW+PQ | 图索引+量化压缩 | 高精度且内存受限 |
| **IndexLSH** | LSH | 局部敏感哈希 | 超大规模粗筛 |
| **IndexScalarQuantizer** | SQ | 标量量化（fp32→uint8） | 简单压缩 |
| **GPU 版本** | GPU | 上述索引的 GPU 实现 | 大批量高吞吐 |

### 索引用法模式

Faiss 索引通常遵循三步模式：

```python
import faiss
import numpy as np

# 1. 创建索引
d = 128  # 向量维度
quantizer = faiss.IndexFlatL2(d)
index = faiss.IndexIVFPQ(quantizer, d, nlist=1024, m=8, nbits=8)

# 2. 训练 + 添加
index.train(train_vectors)   # 聚类和码本训练需要代表性数据
index.add(database_vectors)  # 添加向量

# 3. 查询
index.nprobe = 16  # 设置查询参数
distances, indices = index.search(query_vectors, k=10)
```

### GPU 加速

```python
# 单 GPU
res = faiss.StandardGpuResources()
gpu_index = faiss.index_cpu_to_gpu(res, 0, cpu_index)

# 多 GPU 分片
gpu_index = faiss.index_cpu_to_all_gpus(cpu_index)
```

GPU 版本适合大批量查询场景。单条查询时 GPU 可能因数据传输开销不一定比 CPU 快，但在批量数千条查询时吞吐量可提升数倍到数十倍。

### 性能调优

| 调优方向 | 方法 |
|---------|------|
| **召回率** | 增大 nprobe（IVF）、efSearch（HNSW）、n_trees |
| **查询速度** | 使用 PQ 压缩、GPU 加速、减小 nprobe/efSearch |
| **内存** | 使用 PQ/SQ 压缩、mmap 加载、分片存储 |
| **构建速度** | GPU 训练、减少 nlist/M、多线程 |
| **批量查询** | 合并多条查询为 batch、GPU 并行 |

### Faiss 与其他向量库对比

| 维度 | Faiss | Milvus | Chroma |
|------|-------|--------|--------|
| 本质 | 检索库 | 企业级数据库 | 轻量数据库 |
| 优势 | 算法强、GPU 优 | 分布式、高可用 | 简单、LangChain 集成 |
| 部署 | 库级调用 | 单机/分布式集群 | 单机开箱即用 |
| 场景 | 大规模检索、算法研究 | 企业级高并发 | 原型开发、个人项目 |
| 生态 | 需自行集成 | Spark/Flink/LangChain | 深度适配 LangChain |

## Milvus：分布式向量数据库

### 核心定位

Milvus 是开源的云原生向量数据库，专注于海量高维向量的高效相似性检索与管理。由 Zilliz 主导开发，支持亿级到百亿级向量，提供完整的数据库服务能力。

### 三种部署版本

| 版本 | 架构 | 数据规模 | 部署方式 | 适用场景 |
|------|------|---------|---------|---------|
| **Milvus Lite** | Python 库 | 百万级 | `pip install` | 原型开发、Jupyter、边缘设备 |
| **Standalone** | 单机容器 | 亿级 | Docker | 中小规模生产、测试环境 |
| **Distributed** | K8s 微服务 | 百亿级 | Kubernetes 集群 | 大规模生产、高并发 |

三种版本使用统一 API（PyMilvus），代码可无缝迁移。注意 Milvus Lite 不支持 Windows 系统。

### 核心架构（Milvus 2.x）

Milvus 采用微服务架构，分为三层：

**数据处理层**：
- **Proxy**：接入层，接收客户端请求、校验、路由分发
- **Query Node**：加载索引并执行相似性检索
- **Data Node**：处理异步数据写入，将数据转为结构化格式写入存储
- **Index Node**：异步构建索引

**元数据管理层**：
- 管理 Collection、Partition、Index 等元信息
- 使用 etcd 存储元数据

**存储层**：
- 采用计算与存储分离设计
- 持久化存储使用 MinIO/S3 等对象存储
- 支持数据备份与恢复

### 核心概念

#### Collection（集合）

Collection 是 Milvus 中数据组织的基本单元，类似关系型数据库中的表。每个 Collection 包含：

- 一组向量字段（Vector Field）
- 可选的标量字段（Scalar Field，用于元数据过滤）
- 主键字段（Primary Key）

```python
from pymilvus import CollectionSchema, FieldSchema, DataType

fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True),
    FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=128),
    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=512),
    FieldSchema(name="category", dtype=DataType.VARCHAR, max_length=64)
]
schema = CollectionSchema(fields, description="文档向量集合")
```

#### Partition（分区）

Partition 是 Collection 内部的数据分区，用于将数据物理分组以提升查询性能。常见用法：

- 按时间分区（如每月一个分区）
- 按类别分区
- 查询时可指定只搜索特定分区（Partition Key 过滤）

#### Index（索引）

Milvus 支持多种索引类型：

| 索引类型 | 说明 | 适用场景 |
|---------|------|---------|
| **FLAT** | 暴力搜索 | 小规模、100% 精度 |
| **IVF_FLAT** | IVF + 精确距离 | 中等规模 |
| **IVF_PQ** | IVF + 乘积量化 | 大规模、内存受限 |
| **IVF_SQ8** | IVF + 标量量化 | 平衡精度与压缩 |
| **HNSW** | 分层小世界图 | 高召回低延迟 |
| **DISKANN** | 磁盘索引 | 超大规模、内存不足 |

```python
index_params = {
    "index_type": "IVF_PQ",
    "params": {"nlist": 1024, "m": 8, "nbits": 8},
    "metric_type": "L2"
}
collection.create_index("vector", index_params)
```

### PyMilvus 核心 API

#### 连接与 Collection 管理

```python
from pymilvus import connections, Collection, utility

# 连接
connections.connect(host="localhost", port="19530")

# 创建 Collection
collection = Collection("docs", schema)

# 删除 Collection
utility.drop_collection("docs")
```

#### 数据插入

```python
# 批量插入
entities = [
    [1, 2, 3],  # id
    [vec1, vec2, vec3],  # vector
    ["文本1", "文本2", "文本3"],  # text
    ["cat1", "cat2", "cat1"]  # category
]
collection.insert(entities)
collection.flush()  # 持久化
```

#### 构建索引与加载

```python
collection.create_index("vector", index_params)
collection.load()  # 加载到内存以供查询
```

#### 向量搜索

```python
search_params = {"params": {"nprobe": 16}}
results = collection.search(
    data=[query_vector],
    anns_field="vector",
    param=search_params,
    limit=10,
    expr='category == "cat1"',  # 元数据过滤
    output_fields=["text", "category"]
)

for hits in results:
    for hit in hits:
        print(f"ID: {hit.id}, 距离: {hit.distance}, 文本: {hit.entity.get('text')}")
```

#### 查询与删除

```python
# 标量查询
results = collection.query(
    expr='category == "cat1"',
    output_fields=["id", "text"],
    limit=10
)

# 删除
collection.delete(expr='id in [1, 2, 3]')
```

### Milvus 的 AI 应用

#### 混合搜索（Hybrid Search）

Milvus 支持 BM25 关键词检索 + 向量检索的混合搜索：

- 向量检索擅长语义匹配
- BM25 擅长精确关键词匹配
- 通过 RRF（Reciprocal Rank Fusion）等融合算法合并结果
- 混合搜索通常比纯向量检索效果更好

#### Reranker 重排

Milvus 内置 Reranker 支持，在初步检索后用更精确的模型对候选结果重排，提升最终精度。

#### RAG 应用

Milvus 在 RAG 架构中扮演知识检索引擎角色：

1. 文档分块 → 嵌入模型生成向量 → 存入 Milvus
2. 用户提问 → 嵌入 → Milvus 向量检索 → 返回相关片段
3. 相关片段 + 问题 → LLM → 生成答案

### 性能评估指标

| 指标 | 说明 |
|------|------|
| **Recall@K** | 检索结果中真实近邻的比例，核心精度指标 |
| **QPS** | 每秒查询数，吞吐量指标 |
| **Latency** | 单次查询延迟（P50/P95/P99） |
| **内存占用** | 索引和数据占用的内存 |
| **构建时间** | 索引构建耗时 |

## Faiss vs Milvus：如何选择

| 决策因素 | 选择 Faiss | 选择 Milvus |
|---------|-----------|-------------|
| 团队规模 | 算法团队，能自行封装 | 需要开箱即用的数据库服务 |
| 数据规模 | 百万到亿级 | 亿级到百亿级 |
| 部署复杂度 | 可接受库级集成 | 需要单机/分布式部署 |
| 功能需求 | 只需检索，不需要数据库特性 | 需要持久化、CRUD、元数据过滤 |
| GPU 需求 | 需要 GPU 加速检索 | 需要分布式 GPU 集群 |
| 高可用 | 自行实现 | 内置副本、故障恢复 |
| 多语言 | C++/Python | Python/Java/Go/REST API |

实际项目中，Milvus 底层也使用 Faiss 作为部分索引的计算引擎，二者并非互斥。

## 延伸阅读

- [IVF 与 PQ 量化](/ai/datawhale/easy-vecdb/concepts/ivf-pq-quantization.md) — Faiss/Milvus 核心索引的算法原理
- [HNSW 与 LSH](/ai/datawhale/easy-vecdb/concepts/hnsw-lsh.md) — 图索引与哈希索引
- [Annoy 实践](/ai/datawhale/easy-vecdb/concepts/annoy-practice.md) — 轻量级替代方案
- [Milvus 快速入门](/ai/datawhale/easy-vecdb/examples/milvus-getting-started.md) — 动手实践
