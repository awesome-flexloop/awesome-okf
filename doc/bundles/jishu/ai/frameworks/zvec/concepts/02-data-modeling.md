---
type: Concept
title: Zvec 数据模型：Collection、Document 与 Schema
description: 强类型 Schema 系统、23 种 DataType 枚举（源码口径）、动态 Schema 演进 DDL 与 Collection 24 个公共 API 成员
tags: [zvec, data-model, schema, ddl, datatype]
generated: { by: "teleagent/seven-concepts-e", at: 2026-10-22T10:30:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-10-22T10:30:00+08:00 }
status: stable
stale_after: 2027-04-22
sources:
  - id: zvec-source
    resource: /references/source-code.md
    title: alibaba/zvec 源码信源
  - id: zvec-docs
    resource: /references/website-docs.md
    title: zvec.org 官方文档站信源
---

# Zvec 数据模型：Collection、Document 与 Schema

Zvec 用 **Collection**（具名容器，类比关系库的表）与 **Document**（基本存储单元，类比一行记录）组织数据。每个 Collection 由 Schema 定义标量字段与向量字段，写入时执行强类型检查。Schema 是动态的——可在运行期添加/删除标量字段、创建/删除索引，无需停机或重导数据；但不支持跨 Collection 查询（无 Join/Union）。

每个 Collection 独立持久化于磁盘专属目录且完全自包含——迁移 Collection 只需移动目录后按新路径打开。

## Document 结构

Document 由三部分组成：

- `id`：唯一字符串标识（v0.8.0 起 UTF-8、上限 1024 字节），写入后不可修改
- `vectors`：一组具名向量（稠密或稀疏）
- `fields`：一组具名标量字段（含数组）

字段名在插入/查询时必须与 Schema 定义完全一致；768 维向量字段不接受 512 维数据。文档插入后可用 `upsert()` 整体替换或 `update()` 局部更新，仍受 Schema 约束。

## DataType：23 个枚举成员（源码口径）

源码 `python/zvec/typing/__init__.pyi` 声明 23 个成员：

| 类别 | 成员 |
|---|---|
| 基础标量（8） | STRING、BOOL、INT32、INT64、UINT32、UINT64、FLOAT、DOUBLE |
| 稠密向量（5） | VECTOR_FP16、VECTOR_FP32、VECTOR_FP64、VECTOR_INT8、VECTOR_UINT8 |
| 稀疏向量（2） | SPARSE_VECTOR_FP32、SPARSE_VECTOR_FP16 |
| 数组（8） | ARRAY_STRING、ARRAY_INT32、ARRAY_INT64、ARRAY_FLOAT、ARRAY_DOUBLE、ARRAY_BOOL、ARRAY_UINT32、ARRAY_UINT64 |

> 官方文档"数据结构"页列 21 个（稠密向量仅 FP16/FP32/INT8）；源码多出 VECTOR_FP64 与 VECTOR_UINT8。冲突以源码为准。数组不支持混合类型或嵌套。

## Schema 定义与索引规则

```python
import zvec

schema = zvec.CollectionSchema(
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
collection = zvec.create_and_open(path="./my_collection_data", schema=schema)
```

两条索引规则：**每个向量字段必须建向量索引**（相似度检索的前提，且向量字段索引不可删除）；**标量字段索引可选**——计划用于过滤的字段应建倒排索引。`enable_range_optimization=True` 可加速范围查询。

## Schema 演进（DDL）

| 操作 | API | 说明 |
|---|---|---|
| 添加列 | `add_column(field_schema=..., expression="5")` | 数值型标量；expression 为已有 Document 填充默认值（字面量或算术表达式如 `"publish_year + 1"`） |
| 删除列 | `drop_column(field_name=...)` | 永久删除该字段及全部数据，不可逆 |
| 修改列 | `alter_column(old_name=..., new_name=...)` 或 `alter_column(field_schema=...)` | 重命名或安全类型变更（如 INT32→INT64） |
| 创建索引 | `create_index(field_name=..., index_param=...)` | 向量/标量字段均可；可替换既有索引类型 |
| 删除索引 | `drop_index(field_name=...)` | 仅标量字段；向量字段必须始终有且仅有一个索引 |

添加/删除向量字段暂不支持（官方标记"即将支持"）。

## Collection 公共 API 面（24 个成员）

`python/zvec/model/collection.py` 中 Collection 类导出 24 个公共成员——4 个属性（`path`、`option`、`schema`、`stats`）与 20 个方法：生命周期（`close`/`destroy`/`flush`）、DDL（`add_column`/`drop_column`/`alter_column`/`create_index`/`drop_index`）、写（`insert`/`upsert`/`update`/`delete`/`delete_by_filter`）、读（`fetch`/`iter_docs`/`query`/`group_by_query`）、内部 ID 通道（`query_internal_ids`/`resolve_internal_ids`）、维护（`optimize`）。所有写操作立即对查询可见（实时流式工作负载）。

## 相关概念

- [索引类型](03-index-types.md)：向量索引六类选型
- [全文检索与过滤](05-fts-and-filter.md)：倒排索引与 FTS 的分工
- [快速上手示例](/examples/00-quickstart-python.md)
