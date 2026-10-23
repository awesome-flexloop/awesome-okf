---
type: Example
title: 混合检索实战：稠密 + 稀疏多路融合
description: 多模态商品 Schema、稠密+稀疏双路查询、RrfReRanker/WeightedReRanker 融合与两阶段检索的端到端实战
tags: [zvec, hybrid-search, multi-vector, rrf, weighted-reranker, example]
generated: { by: "teleagent/seven-concepts-e", at: 2026-10-22T10:30:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-10-22T10:30:00+08:00 }
status: stable
stale_after: 2027-04-22
sources:
  - id: zvec-docs
    resource: /references/website-docs.md
    title: zvec.org 官方文档站信源
---

# 混合检索实战：稠密 + 稀疏多路融合

综合官方"创建 Collection 实战示例"与"混合搜索最佳实践"的端到端流程：多模态 Schema → 双路 Embedding → 多路 Query → 融合重排。

## 第一步：多模态商品 Schema

来自官方商品搜索示例——标量字段负责过滤与展示、三个向量字段（图像稠密 + 描述稠密 + 关键词稀疏）负责语义检索：

```python
import zvec

schema = zvec.CollectionSchema(
    name="product_search",
    fields=[
        zvec.FieldSchema(name="image_url", data_type=zvec.DataType.STRING, nullable=True),  # 仅展示，不建索引
        zvec.FieldSchema(name="description", data_type=zvec.DataType.STRING),               # 仅展示
        zvec.FieldSchema(name="category", data_type=zvec.DataType.ARRAY_STRING,
                         index_param=zvec.InvertIndexParam()),           # CONTAIN_ANY/ALL
        zvec.FieldSchema(name="price", data_type=zvec.DataType.INT32,
                         index_param=zvec.InvertIndexParam(enable_range_optimization=True)),  # price > 100
        zvec.FieldSchema(name="in_stock", data_type=zvec.DataType.BOOL,
                         index_param=zvec.InvertIndexParam()),
    ],
    vectors=[
        zvec.VectorSchema(name="image_vec", data_type=zvec.DataType.VECTOR_FP32, dimension=512,
                          index_param=zvec.HnswIndexParam(metric_type=zvec.MetricType.COSINE)),
        zvec.VectorSchema(name="description_vec", data_type=zvec.DataType.VECTOR_FP32, dimension=768,
                          index_param=zvec.HnswIndexParam(metric_type=zvec.MetricType.COSINE,
                                                          quantize_type=zvec.QuantizeType.INT8)),  # 量化加速
        zvec.VectorSchema(name="keywords_sparse", data_type=zvec.DataType.SPARSE_VECTOR_FP32,
                          index_param=zvec.HnswIndexParam(metric_type=zvec.MetricType.IP)),
    ],
)

collection = zvec.create_and_open(
    path="path/to/collection", schema=schema,
    option=zvec.CollectionOption(read_only=False, enable_mmap=True),
)
```

设计要点：仅用于展示的字段不建索引（省存储、免写放大）；过滤字段建倒排索引；`CONTAIN_ANY ("electronics", "headphones")` 类查询依赖 ARRAY_STRING + InvertIndexParam。

## 第二步：生成双路 Embedding

```python
from zvec.extension import DefaultLocalDenseEmbedding, DefaultLocalSparseEmbedding

dense_emb = DefaultLocalDenseEmbedding()                            # 384 维稠密
sparse_emb = DefaultLocalSparseEmbedding(encoding_type="query")    # SPLADE 稀疏

query = "What is a vector database"
dense_vec = dense_emb.embed(query)
sparse_vec = sparse_emb.embed(query)
```

## 第三步：多路 Query + RRF 融合

```python
from zvec import Query
from zvec.extension import RrfReRanker

final_results = collection.query(
    queries=[
        Query(field_name="description_vec", vector=dense_vec),
        Query(field_name="keywords_sparse", vector=sparse_vec),
    ],
    topk=3,
    reranker=RrfReRanker(rank_constant=60),
)
```

加权融合变体（需要评分归一化时 `Collection.query()` 自动获取字段 Schema）：

```python
final_results = collection.query(
    queries=[
        zvec.Query(field_name="description_vec", vector=dense_vec),
        zvec.Query(field_name="keywords_sparse", vector=sparse_vec),
    ],
    topk=3,
    reranker=zvec.WeightedReRanker(weights=[0.7, 0.3]),
)
```

## 变体：两阶段检索（宽召回 + 精排）

```python
from zvec.extension import DefaultLocalReRanker

candidates = collection.query(
    queries=Query(field_name="description_vec", vector=dense_vec),
    topk=100,                                   # 宽召回
)
reranker = DefaultLocalReRanker(
    query=query, rerank_field="description",
)
final = reranker.rerank([candidates], topn=10)  # Cross-Encoder 精排
```

## 相关概念

- [混合检索](/concepts/06-hybrid-retrieval.md)：六种查询类型与融合原理
- [Embedding 与 Reranker](/concepts/07-embedding-reranker.md)：函数体系与自定义扩展
- [快速上手](00-quickstart-python.md)
