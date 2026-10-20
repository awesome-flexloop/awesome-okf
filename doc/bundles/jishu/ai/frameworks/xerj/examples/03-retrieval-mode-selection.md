---
type: Example
title: 选择检索模式
description: 决策表式的实操——同一问题在词法、语义、向量、混合四种模式下各会怎样、怎么裁剪响应、以及如何用三臂方法验证哪种模式真的更好
tags: [xerj, 示例, 检索模式, 决策, 评测]
generated: { by: source-code-to-okf-wiki/E, at: 2026-10-20T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-10-20T00:00:00Z }
status: stable
stale_after: 2027-04-20
sources:
  - id: xerj-facts
    resource: /references/facts.md
    title: XERJ 事实清单
  - id: xerj-insights
    resource: /references/insights.md
    title: 架构洞察与知识地图
---

# 选择检索模式

同一个问题，XERJ 有四种检索方式。选错不会报错，只会**安静地给出更差的结果**。本示例给出一张决策表，并演示如何验证自己的选择。

## 决策表

| 问题形态 | 用什么 | 写法 |
|---|---|---|
| 已知符号名，要定义 | `match` + `prefix`，或 `xerj def` | 定义优先排序，跳过全文打分噪声 |
| 精确短语 | `match_phrase` | — |
| 词面相近的同义表达 | `match`（BM25） | 默认最稳 |
| 真正的语义/同义 | `semantic` | **先确认嵌入模式** |
| 向量近邻 | `knn` | 自带 `query_vector` |
| 两者都要 | `hybrid`（`rrf`） | 确认向量臂的索引覆盖 |
| 只要片段 | 加 `fields: ["_passage"]` | 34 倍响应缩减 |

## 一个具体问题

> 「WAL 段是怎么轮转的？」

### 方案 A：BM25（默认，最稳）

```json
{
  "fields": ["_passage"],
  "_source": ["title", "ax_path"],
  "query": { "match": { "body": "rotate WAL segment" } },
  "size": 5
}
```

只要**词面**对上就命中。上游在两个语料、12 个手标查询上的实测：BM25 的 top-3 在 rust-text 是 6/6、kv-oss 是 6/6、合并 12/12，且在任何语料上都不是最差的一臂，还快约 5 倍（F-180）。

### 方案 B：语义

```json
{
  "fields": ["_passage"],
  "_source": ["title", "ax_path"],
  "query": { "semantic": { "field": "body", "query": "how is the write ahead log rotated", "k": 10 } },
  "size": 5
}
```

> **前提**：节点必须以 `--embed-mode neural`（或 `--embed-mode proxy`）启动，且语料是在该模式下索引的。默认词法嵌入器下，这个查询等于「词/子词重叠 + BM25」——它不会失败，只是**不会**做你以为的事（F-113、F-115、F-116）。

### 方案 C：向量

```json
{
  "fields": ["_passage"],
  "_source": ["title", "ax_path"],
  "query": {
    "knn": {
      "field": "embedding",
      "query_vector": [/* 你自己算的 */],
      "k": 10,
      "num_candidates": 100
    }
  },
  "size": 5
}
```

自己带向量。未过滤且 ≥1,024 文档时走 HNSW + 精确重打分（`num_candidates` 是 beam 宽度，下限 800）；过滤形态走精确扫描（F-123、F-125）。

### 方案 D：混合

```json
{
  "query": {
    "hybrid": {
      "queries": [
        { "query": { "match": { "body": "rotate WAL segment" } }, "weight": 1.0 },
        { "query": { "semantic": { "field": "body", "query": "how is the write ahead log rotated", "k": 10 } }, "weight": 1.0 }
      ],
      "fusion": "rrf"
    }
  }
}
```

**两个前提**：

1. `fusion` 只有 `rrf`（默认）与 `linear`；`"learned"` 未实现，400（F-094）。
2. 向量臂**只对映射了 `semantic_text` 的索引有效**；在未映射的索引上发起语义查询**不降级**，而是让整个请求 400 并连带拖垮通配符下的其他索引（F-183）。

在 `xerj code` 里，混合检索的开头会给出实际跑了哪些臂：

```
[hybrid RRF(k=60) — BM25 over 9 index(es), vector over 3 of 9]
```

若向量臂跑不了，它会明说 `BM25 only — …`，而不是假装跑过。

## 混合模式的一个历史教训

上游曾把 hybrid 设为默认，**依据只在 rust-text 一个语料上**（那里它赢 top-1）。在 C 语料上，向量臂只触达 **407 个索引中的 5 个**（issue #173）——融合等于把一个好的排名与一个看不见 98.8% 材料的排名混在一起（F-181）。

因此上游的建议是：**只有当语料有广泛的 `semantic_text` 覆盖、且你确实关心 top-1 时**，才用 hybrid，并且**先测再用**。

## 裁剪：模式对了，响应仍然可能太大

无论用哪种模式，默认 `_search` 都返回完整文档。源码类语料下 5 个命中就是 416,630 字节；加 `"fields": ["_passage"]` 并投影 `_source` 后是 12,122 字节（F-087）。

`_passage` 的形状（F-088）：

```json
{ "field": "body", "ordinal": 12, "start_offset": 4810, "end_offset": 5233, "text": "…" }
```

它是**从原字段切片**的，不是摘要。

注意 `_passage` 与混合/多 kNN 融合不兼容——混合查询下请求 `_passage` 会 400 并指名修法。

## 验证：把「哪种更好」变成可测量的

上游的测量纪律可以直接照搬（F-188 上下文）：

### 第一步：构造有客观判据的任务

不要用「看起来相关」当判据。用能编译且通过**模型从未见过的隐藏测试**的任务。

### 第二步：先验证测试本身

- 注入**参考正确解** → 必须通过；
- 注入一个**貌似合理的错解**（正确但平方复杂度，或缺了那个契约）→ 必须失败。

> 一个让错代码也能通过的测试套件，什么都测不出来。

### 第三步：跑三臂

| 臂 | 检索行为 |
|---|---|
| `bare` | 仅凭记忆 |
| `native` | 智能体自己 grep 语料树 |
| `xerj` | 注入检索到的段落 |

### 第四步：看 top-3，不是 top-1

智能体读的是 k 个段落。上游的实测表里，BM25 的 top-1 是 9/12，但 top-3 是 **12/12**（F-180）。只看 top-1 会误判 BM25。

### 第五步：报中位数，不报均值

一次 flailing 试次可能是另一次的 5 倍。

### 第六步：不要在模型已记住的代码上测

它连一张 256 值的表都能凭记忆复现，检索于是显示为纯开销（F-189）。

## 一个必须守住的红线

`rerank` 是唯一在**搜索期**把文档文本发给第三方的特性（详见 [05](/concepts/05-vector-and-hybrid.md)）。除非用户明确同意，不要在必须留在本地的数据上加它。

它的失败契约值得记住：

- 提供方慢 → HTTP **200** + 引擎原序 + `_rerank.applied:false`（**必须读这个字段**）；
- 无密钥 → 503；已禁用 → 403；密钥被拒/体畸形/不可达 → 502 且**无命中**——不要重试，去掉 `rerank` 重跑；
- 与 `sort`、`search_after`、`collapse`、scroll、`size:0`、`_msearch`、搜索模板、`_async_search`、原生 `/v1`、gRPC 同时使用一律 **400 拒绝**（F-097）。

## 速查卡

```
问自己三个问题：
1. 词面能对上吗？  → match（BM25），最稳，默认选它
2. 要真语义吗？    → 先确认 --embed-mode neural 且语料已按该模式索引
3. 只需要片段吗？  → fields:["_passage"] + _source 投影（34×）
```

## 相关概念

- [05 向量、嵌入与混合检索](/concepts/05-vector-and-hybrid.md)：四种嵌入后端、ANN 判定规则、rerank 边界
- [04 检索路径与响应裁剪](/concepts/04-search-query-path.md)：`_passage`、`_xerj.hints`、严格字段
- [08 参考编码与语料库](/concepts/08-reference-coding.md)：BM25 为何是 `xerj code` 的默认模式
- [Examples 索引](index.md)：全部示例
