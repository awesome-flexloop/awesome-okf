---
title: Milvus 快速入门
type: example
bundle: /datawhale/easy-vecdb
description: 使用 PyMilvus 完成向量数据库的核心操作：连接 Milvus、创建 Collection、插入数据、构建索引、向量搜索与元数据过滤
related:
  - /datawhale/easy-vecdb/concepts/faiss-milvus-engineering
  - /datawhale/easy-vecdb/concepts/ivf-pq-quantization
  - /datawhale/easy-vecdb/examples/rag-with-faiss
sources:
  - https://github.com/datawhalechina/easy-vecdb/blob/main/docs/Milvus/chapter3/PyMilvus核心API实战.md
  - https://github.com/datawhalechina/easy-vecdb/blob/main/docs/Milvus/chapter2/Milvus核心概念.md
tags:
  - milvus
  - pymilvus
  - tutorial
  - crud
---

# Milvus 快速入门

本示例演示如何使用 PyMilvus 完成向量数据库的核心操作，包括连接服务、创建 Collection、定义 Schema、插入数据、构建索引和执行向量搜索。

## 环境准备

### 启动 Milvus Standalone

使用 Docker 启动单机版 Milvus：

```bash
wget https://github.com/milvus-io/milvus/releases/download/v2.4.0/milvus-standalone-docker-compose.yml -O docker-compose.yml
docker compose up -d
```

Milvus 默认服务端口为 19530。

### 安装 PyMilvus

```bash
pip install pymilvus
```

## 完整示例

### 1. 连接 Milvus

```python
from pymilvus import (
    connections,
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
    utility
)

connections.connect(
    alias="default",
    host="localhost",
    port="19530"
)

print(utility.get_server_version())
```

### 2. 创建 Collection 与 Schema

```python
collection_name = "document_vectors"

if utility.has_collection(collection_name):
    utility.drop_collection(collection_name)

fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=128),
    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=1024),
    FieldSchema(name="category", dtype=DataType.VARCHAR, max_length=64),
]

schema = CollectionSchema(
    fields=fields,
    description="文档向量集合",
    enable_dynamic_field=True
)

collection = Collection(
    name=collection_name,
    schema=schema,
    using="default"
)

print(f"Collection '{collection_name}' 创建成功")
```

### 3. 插入数据

```python
import numpy as np

np.random.seed(42)
num_entities = 1000
dim = 128

vectors = np.random.randn(num_entities, dim).astype(np.float32)
texts = [f"这是第{i}个文档的内容片段" for i in range(num_entities)]
categories = [f"cat_{i % 5}" for i in range(num_entities)]

entities = [
    vectors.tolist(),
    texts,
    categories,
]

insert_result = collection.insert(entities)
print(f"插入 {insert_result.insert_count} 条数据")

collection.flush()
```

### 4. 构建索引

```python
index_params = {
    "index_type": "IVF_PQ",
    "params": {
        "nlist": 128,
        "m": 16,
        "nbits": 8
    },
    "metric_type": "L2"
}

collection.create_index(
    field_name="vector",
    index_params=index_params
)

print("索引构建完成")
```

常用索引类型选择：

| 索引类型 | 参数 | 适用场景 |
|---------|------|---------|
| `FLAT` | 无 | 小数据量、100% 精度 |
| `IVF_FLAT` | nlist | 中等规模、精度优先 |
| `IVF_PQ` | nlist, m, nbits | 大规模、内存受限 |
| `HNSW` | M, efConstruction | 高召回、低延迟 |
| `DISKANN` | 无 | 超大规模、磁盘存储 |

### 5. 加载 Collection 并搜索

```python
collection.load()

query_vector = np.random.randn(1, dim).astype(np.float32).tolist()

search_params = {
    "params": {"nprobe": 16},
    "metric_type": "L2"
}

results = collection.search(
    data=query_vector,
    anns_field="vector",
    param=search_params,
    limit=10,
    output_fields=["text", "category"]
)

for hits in results:
    for hit in hits:
        print(f"ID: {hit.id}, 距离: {hit.distance:.4f}, "
              f"分类: {hit.entity.get('category')}, "
              f"文本: {hit.entity.get('text')[:30]}")
```

### 6. 带元数据过滤的搜索

```python
filtered_results = collection.search(
    data=query_vector,
    anns_field="vector",
    param=search_params,
    limit=10,
    expr='category == "cat_1"',
    output_fields=["text", "category"]
)

print(f"过滤后结果数: {len(filtered_results[0])}")
for hit in filtered_results[0]:
    print(f"ID: {hit.id}, 分类: {hit.entity.get('category')}")
```

支持的过滤表达式语法：

```python
# 比较运算
expr = 'category == "cat_1"'
expr = 'id > 100'

# 逻辑运算
expr = 'category == "cat_1" and id > 500'
expr = 'category in ["cat_1", "cat_2"]'

# 范围查询
expr = 'id >= 100 and id <= 200'
```

### 7. 标量查询

```python
query_results = collection.query(
    expr='category == "cat_1"',
    output_fields=["id", "text", "category"],
    limit=5
)

for result in query_results:
    print(f"ID: {result['id']}, 分类: {result['category']}, "
          f"文本: {result['text'][:30]}")
```

### 8. 删除数据

```python
collection.delete(expr='id in [0, 1, 2]')
collection.flush()
```

### 9. 分区管理

```python
collection.create_partition("partition_cat_1")
collection.create_partition("partition_cat_2")

collection.insert(
    [vectors[:500].tolist(), texts[:500], categories[:500]],
    partition_name="partition_cat_1"
)

results = collection.search(
    data=query_vector,
    anns_field="vector",
    param=search_params,
    limit=10,
    partition_names=["partition_cat_1"],
    output_fields=["text"]
)
```

### 10. 资源清理

```python
collection.release()
utility.drop_collection(collection_name)
connections.disconnect("default")
```

## Milvus Lite 快速原型（无需 Docker）

对于快速原型开发，可使用 Milvus Lite（Python 库形式）：

```bash
pip install pymilvus[milvus_lite]
```

```python
from pymilvus import MilvusClient

client = MilvusClient("./milvus_demo.db")

client.create_collection(
    collection_name="demo",
    dimension=128
)

client.insert(
    collection_name="demo",
    data=[{"id": i, "vector": vec.tolist()} for i, vec in enumerate(vectors[:100])]
)

results = client.search(
    collection_name="demo",
    data=[query_vector[0]],
    limit=5
)
```

注意：Milvus Lite 不支持 Windows 系统，Windows 用户请使用 Docker 或 WSL。

## 性能调优要点

### 索引参数调优

| 参数 | 增大影响 | 建议起始值 |
|------|---------|-----------|
| nlist（IVF） | 簇更细、精度↑、构建慢 | sqrt(N) ~ 4*sqrt(N) |
| nprobe（IVF） | 查询更准、延迟↑ | 16~64 |
| M（HNSW） | 图更密、召回↑、内存↑ | 16~48 |
| efConstruction | 构建质量↑、构建慢 | 100~500 |
| efSearch | 查询召回↑、延迟↑ | 64~256 |
| m（PQ） | 精度↑、压缩率↓ | 8~64（维度的因数） |

### 批量操作

- 批量插入比单条插入高效得多，建议每批 1000~10000 条
- 构建索引前完成所有数据插入，避免增量构建的性能损耗
- 查询时合并多个查询向量为 batch，提升吞吐量

## 延伸阅读

- [Faiss 与 Milvus 工程实践](/ai/datawhale/easy-vecdb/concepts/faiss-milvus-engineering.md) — Milvus 架构与核心概念详解
- [IVF 与 PQ 量化](/ai/datawhale/easy-vecdb/concepts/ivf-pq-quantization.md) — IVF_PQ 索引原理
- [基于 Faiss 的 RAG 实战](/ai/datawhale/easy-vecdb/examples/rag-with-faiss.md) — 使用 Milvus 构建 RAG 系统
