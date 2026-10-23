---
type: Example
title: Python 快速上手：从 Schema 到向量检索
description: 依据官方快速开始流程的完整 Python 上手示例——建 Collection、插 Document、optimize、过滤检索与删除
tags: [zvec, python, quickstart, example]
generated: { by: "teleagent/seven-concepts-e", at: 2026-10-22T10:30:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-10-22T10:30:00+08:00 }
status: stable
stale_after: 2027-04-22
sources:
  - id: zvec-docs
    resource: /references/website-docs.md
    title: zvec.org 官方文档站信源
---

# Python 快速上手：从 Schema 到向量检索

依据 zvec.org 官方快速开始流程的最小可运行路径：安装 → 定义 Schema → 创建 Collection → 插入 Document → 优化 → 检索。前置条件：64 位 Python 3.10–3.14。

## 安装

```bash
pip install zvec
```

## 定义 Schema 并创建 Collection

Schema 由 `fields`（标量）与 `vectors`（向量）两部分构成；插入与查询必须严格使用此处定义的字段名。

```python
import zvec

collection_schema = zvec.CollectionSchema(
    name="my_collection",
    fields=[
        zvec.FieldSchema(
            name="publish_year",
            data_type=zvec.DataType.INT32,
            index_param=zvec.InvertIndexParam(enable_range_optimization=True),
        ),
    ],
    vectors=[
        zvec.VectorSchema(
            name="embedding",
            data_type=zvec.DataType.VECTOR_FP32,
            dimension=768,
            index_param=zvec.HnswIndexParam(metric_type=zvec.MetricType.COSINE),
        ),
    ],
)

collection = zvec.create_and_open(
    path="./my_collection_data",
    schema=collection_schema,
)
```

## 插入与获取 Document

```python
collection.insert(
    zvec.Doc(
        id="book_1",
        vectors={"embedding": [0.1] * 768},   # 替换为真实向量
        fields={"publish_year": 1936},
    )
)

result = collection.fetch(ids="book_1")
print(result)
```

## 优化 Collection

新插入向量暂存 Flat 缓冲区；调用 `optimize()` 后台构建向量索引加速检索（不阻塞读写）：

```python
collection.optimize()
```

## 向量检索（含条件过滤）

```python
# 相似度检索
result = collection.query(
    queries=zvec.Query(
        field_name="embedding",
        vector=[0.3] * 768,
    ),
    topk=10,
)

# 带条件过滤的相似度检索
result = collection.query(
    queries=zvec.Query(
        field_name="embedding",
        vector=[0.3] * 768,
    ),
    topk=10,
    filter="publish_year > 1936",
)
```

## 查看 Schema 与统计、删除 Document

```python
print(collection.schema)   # schema
print(collection.stats)    # 索引状态统计

collection.delete(ids="book_1")                              # 按 ID 删除
collection.delete_by_filter(filter="publish_year < 1900")    # 按条件删除
```

## 相关概念

- [数据模型](/concepts/02-data-modeling.md)：Schema 与 DataType 全集
- [存储与配置](/concepts/08-storage-and-config.md)：optimize 的后台合并机制
- [混合检索实战](01-hybrid-search.md)
