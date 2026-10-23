---
type: Concept
title: Zvec 全文检索与标量过滤：FTS、倒排与 ANTLR SQL 引擎
description: BM25+WAND+Jieba 的全文索引、倒排索引的精确/范围/模式匹配过滤、ANTLR4 四段式 SQL 过滤引擎源码栈
tags: [zvec, fts, bm25, wand, jieba, inverted-index, antlr, sql-filter]
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

# Zvec 全文检索与标量过滤：FTS、倒排与 ANTLR SQL 引擎

Zvec 内置了两套互补的"非向量"检索能力：**倒排索引**（inverted index，标量字段精确过滤）与**全文索引**（FTS，文本关键词检索 + BM25 相关性排序）。二者共用 `src/db/index/column/` 下的 inverted_column 与 fts_column 列引擎，倒排列存储落在 RocksDB。

## 倒排索引：按值查找

倒排索引将 Document→值 的正向映射反转为 值→Document 列表，支持：

- 精确值过滤：`status = "active"`、`category IN ("electronics", "books")`
- 范围查询：`age > 25`（`enable_range_optimization=True` 加速）
- 文本模式匹配：前缀 `product_name LIKE "Wireless%"`、后缀 `email LIKE "%@company.com"`
- 数组成员查询：`tags CONTAIN_ANY ["sport", "music"]`、`permissions CONTAIN_ALL ["read", "write"]`

代价：额外存储 + 写放大。只为频繁过滤的字段建索引（如 `InvertIndexParam()`）。

## 全文索引：BM25 关键词检索

FTS 将文本字段分词为 Token 构建倒排映射，按 BM25 相关性排序。工作流：分词 → Token 过滤 → 构建倒排 → BM25 评分 → WAND 优化。

### 分词器与过滤器

| 配置 | 取值 | 建议 |
|---|---|---|
| `tokenizer_name` | `standard` / `whitespace` / `jieba` | standard 实现 Unicode UAX #29 词边界（类 Elasticsearch standard）；中文或中英混合用 jieba |
| `filters` | `lowercase` / `stemmer` / `ascii_folding` | 英文建议 `["lowercase", "stemmer"]`；重音文本加 `ascii_folding` |
| `extra_params` | JSON | 分词器/过滤器专用配置 |

v0.8.0 起内置 Jieba 中文词典和 HMM 模型——无需单独部署词典文件。索引与查询使用同一套分词配置，创建字段时即确定分析策略。

### BM25 与 WAND

BM25 综合词频（TF，有饱和衰减）、逆文档频率（IDF）与文档长度归一化。多词项查询启用 **WAND（Weak AND）** 优化：预计算各词项评分上界，跳过不可能进 top-k 的 Document，并以 128 个 Document 为一个块（Block-Max 策略）快速跳跃。

### 查询参数

- `match_string`：由字段分词器处理的自然语言查询（适合用户输入）
- `query_string`：结构化表达式，支持短语与布尔运算符（`+机器学习 -深度学习`）
- `default_operator`：裸词间默认布尔符（`OR` 高召回 / `AND` 全必含）

```python
from zvec.model.param.query import Fts, Query

result = collection.query(
    queries=Query(field_name="content", fts=Fts(match_string="机器学习")),
    topk=10,
)
```

## FTS 与向量：单 Query 互斥

单个 `Query` 可执行向量搜索或全文检索，**不能同时**——同一 Query 不应同时设置 `fts` 与 `vector`/`id`。关键词匹配 + 语义检索的组合走多路查询 + 重排序（见[混合检索](06-hybrid-retrieval.md)）或应用层合并。

## ANTLR4 SQL 过滤引擎（源码视角）

过滤字符串（`filter="publish_year > 1936"`）由 `src/db/sqlengine/` 的完整四段栈编译执行：

```text
SQLLexer.g4 / SQLParser.g4（ANTLR4 语法）
    → parser/（zvec_parser + zvec_cached_sql_parser 缓存解析）
    → analyzer/（query_analyzer、search_cond_binder、search_cond_validator、simple_rewriter）
    → planner/（query_planner、optimizer、ops/ 算子目录）
    → 执行（invert_recall_node / fts_recall_node / vector_recall_node 等计划节点）
```

`init()` 的 `invert_to_forward_scan_ratio`（默认 0.9）控制倒排索引转全量正向扫描的阈值、`brute_force_by_keys_ratio`（默认 0.1）与 `fts_brute_force_by_keys_ratio`（默认 0.05）控制键值暴力查找与索引路径的切换——FTS 单独阈值是因为逐候选 FTS 成本更高。

## 相关概念

- [混合检索](06-hybrid-retrieval.md)：FTS 与向量的多路融合
- [数据模型](02-data-modeling.md)：FieldSchema 的 InvertIndexParam
- [源码架构](01-architecture.md)：sqlengine 在 db 层的位置
