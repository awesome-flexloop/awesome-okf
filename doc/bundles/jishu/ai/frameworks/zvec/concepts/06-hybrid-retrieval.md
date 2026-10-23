---
type: Concept
title: Zvec 混合检索：多路 Query 与 Reranker 融合
description: Query 规范与六种查询类型、多向量加权/RRF 融合、两阶段检索最佳实践与分组搜索
tags: [zvec, hybrid-search, multi-vector, reranker, rrf, group-by]
generated: { by: "teleagent/seven-concepts-e", at: 2026-10-22T10:30:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-10-22T10:30:00+08:00 }
status: stable
stale_after: 2027-04-22
sources:
  - id: zvec-docs
    resource: /references/website-docs.md
    title: zvec.org 官方文档站信源
---

# Zvec 混合检索：多路 Query 与 Reranker 融合

`query()` 支持向量相似度、全文检索（BM25）、条件过滤（类 SQL WHERE）及其组合，返回按相关性排序的 Doc 列表。**Query** 是描述搜索字段与查询来源的规范：`field_name` + 查询来源（显式 `vector`、复用已有 Document 的 `id`、或 `fts` 子句）+ 可选 `param`（索引特定查询参数）。单路传一个 Query，多路传列表——这是 Zvec 混合检索的基本形式。

## 六种查询类型

| 类型 | 形态 |
|---|---|
| 单向量 | `Query(field_name="dense", vector=[...])` |
| 多向量 | `[Query(dense...), Query(sparse...)]` + reranker 融合 |
| 条件过滤 | `query(filter="publish_year < 1999", topk=50)` 纯过滤 |
| 向量 + 过滤 | 向量 Query + `filter=`（hybrid） |
| 全文检索 | `Query(field_name="content", fts=Fts(match_string=...))` |
| 分组搜索 | `group_by_query(query, group_by_field_name, group_count, topk_per_group)` |

```python
# 向量 + 过滤（混合）
result = collection.query(
    queries=zvec.Query(field_name="embedding", vector=[0.3] * 768),
    topk=10,
    filter="publish_year > 1936",
)

# 多向量 + 加权融合
result = collection.query(
    topk=3,
    queries=[
        zvec.Query(field_name="dense_embedding", vector=[0.1] * 768),
        zvec.Query(field_name="sparse_embedding", vector={1: 0.1, 37: 0.43}),
    ],
    reranker=zvec.WeightedReRanker(weights=[1.2, 1.0]),
)

# 分组搜索
groups = collection.group_by_query(
    query=zvec.Query(field_name="dense_embedding", vector=[0.1] * 768),
    group_by_field_name="publish_year",
    group_count=3,
    topk_per_group=2,
)
```

## 融合重排：RrfReRanker 与 WeightedReRanker

多路结果的融合由 Reranker 完成（详见[Embedding 与 Reranker](07-embedding-reranker.md)）：

- **RrfReRanker**（倒数排名融合）：仅用排名位置、无需评分，`rank_constant=60`；稠密+稀疏混合检索的默认推荐。
- **WeightedReRanker**：按权重融合多路有评分结果；直接调用 `rerank()` 时需传 `fields`（Schema 向量定义）做评分归一化，传入 `Collection.query()` 时自动获取。

## 两阶段检索最佳实践

先快速召回、再精确重排——经典流水线：

```python
from zvec.extension import DefaultLocalDenseEmbedding, DefaultLocalReRanker
from zvec import Query

dense_emb = DefaultLocalDenseEmbedding()
query_vec = dense_emb.embed("machine learning tutorial")

candidates = collection.query(
    queries=Query(field_name="dense", vector=query_vec),
    topk=100,                                # 第一阶段：宽召回
)
reranker = DefaultLocalReRanker(
    query="machine learning tutorial",
    rerank_field="content",
)
final = reranker.rerank([candidates], topn=10)  # 第二阶段：Cross-Encoder 精排
```

多向量融合变体：稠密 + 稀疏两路 Embedding → `RrfReRanker` 融合，见[混合检索实战示例](/examples/01-hybrid-search.md)。

## 写后立即可见与迭代遍历

所有写操作（insert/upsert/update/delete）立即对查询可见，支持实时流式工作负载。`iter_docs()` 提供流式遍历整个 Collection 的迭代器（DocIterator 支持上下文管理器），无需全量载入内存；`query_internal_ids` / `resolve_internal_ids` 暴露内部 ID 通道供高级场景使用。

## 相关概念

- [全文检索与过滤](05-fts-and-filter.md)：fts 与 filter 的语法细节
- [Embedding 与 Reranker](07-embedding-reranker.md)：四种 Reranker 全景
- [混合检索实战](/examples/01-hybrid-search.md)：端到端代码
